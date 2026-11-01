"""E14 R03 GPU engine (copied from E14 R01 engine.py, unchanged except this line): one bf16 base on GPU 0 with S, SB, ctrl_A_s0, ctrl_B_s0 as named PEFT adapters (parent = adapter disabled).
Block L = output of decoder layer L (model.base_model.model.model.layers[L]), before the final norm.
Hooks (one per block): optional set-to-target patch during the prefill forward only (per row, per block, absolute positions
that already include each row's left-padding offset), then optional capture of selected (row, position) states."""
import contextlib, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa

torch.backends.cuda.matmul.allow_tf32 = False


class Engine:
    def __init__(self, adapters=("S", "SB", "ctrl_A_s0", "ctrl_B_s0")):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
        torch.set_grad_enabled(False)
        t0 = time.time()
        self.tok = AutoTokenizer.from_pretrained(BASE)
        base = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
        model = PeftModel.from_pretrained(base, ADAPTERS[adapters[0]], adapter_name=adapters[0])
        for a in adapters[1:]:
            model.load_adapter(ADAPTERS[a], adapter_name=a)
        model.eval()
        self.model = model
        self.inner = model.base_model.model
        self.layers = self.inner.model.layers
        assert len(self.layers) == 64, len(self.layers)
        self.norm = self.inner.model.norm
        self.lm_head = self.inner.lm_head
        self.patch = None; self.patch_len = None
        self.cap = None
        for L in range(64):
            self.layers[L].register_forward_hook(self._hook(L))
        self.load_secs = time.time() - t0
        self.adapters = list(adapters)

    def _hook(self, L):
        def f(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            if self.patch is not None and h.shape[1] == self.patch_len and L in self.patch:
                rows, pos, vals = self.patch[L]
                h[rows, pos] = vals
            c = self.cap
            if c is not None and L in c["blocks"] and h.shape[1] == c["len"]:
                c["out"][L] = h[c["rows"], c["pos"]].clone()
            return out
        return f

    @contextlib.contextmanager
    def use(self, name):
        if name == "parent":
            with self.model.disable_adapter():
                yield
        else:
            self.model.set_adapter(name)
            yield

    # ------------------------------------------------------------ batching helpers
    def left(self, seqs):
        L = max(len(s) for s in seqs)
        x = torch.full((len(seqs), L), PAD, dtype=torch.long, device="cuda")
        am = torch.zeros((len(seqs), L), dtype=torch.long, device="cuda")
        for b, s in enumerate(seqs):
            x[b, L - len(s):] = torch.tensor(s, device="cuda"); am[b, L - len(s):] = 1
        pos = (am.cumsum(-1) - 1).clamp(min=0)
        return x, am, pos, L, [L - len(s) for s in seqs]

    def _build_patch(self, specs, offs):
        """specs: per row None or (rel_positions list, {L: [n, H] tensor}) -> {L: (rows, pos, vals)} on GPU."""
        acc = {}
        for r, sp in enumerate(specs):
            if sp is None:
                continue
            rel, tg = sp
            p = torch.tensor([q + offs[r] for q in rel], device="cuda", dtype=torch.long)
            rr = torch.full_like(p, r)
            for L, v in tg.items():
                a = acc.setdefault(L, ([], [], []))
                a[0].append(rr); a[1].append(p); a[2].append(v.to("cuda", torch.bfloat16))
        return {L: (torch.cat(a[0]), torch.cat(a[1]), torch.cat(a[2])) for L, a in acc.items()}

    def _build_cap(self, positions, offs, blocks, Ltot):
        rows, pos, lay = [], [], []
        for r, ps in enumerate(positions):
            lay.append((len(pos), len(ps)))
            rows += [r] * len(ps); pos += [q + offs[r] for q in ps]
        return dict(blocks=set(blocks), len=Ltot, out={}, rows=torch.tensor(rows, device="cuda", dtype=torch.long),
                    pos=torch.tensor(pos, device="cuda", dtype=torch.long), lay=lay)

    @staticmethod
    def _split_cap(c, blocks, device="cpu"):
        res = []
        for s, n in c["lay"]:
            res.append(torch.stack([c["out"][L][s:s + n] for L in blocks], 1).to(device))  # [n, nb, H]
        return res

    # ------------------------------------------------------------ forward with capture (teacher forced)
    def forward(self, seqs, positions=None, blocks=(), patch=None, logits=True, device="cpu"):
        """Left-padded forward. Returns (last-position logits fp32 [B, V] or None, list of [n_i, len(blocks), H] bf16)."""
        x, am, pos, L, offs = self.left(seqs)
        self.patch = self._build_patch(patch, offs) if patch else None; self.patch_len = L
        self.cap = self._build_cap(positions, offs, blocks, L) if blocks else None
        try:
            out = self.inner(input_ids=x, attention_mask=am, position_ids=pos, use_cache=False, logits_to_keep=1)
            lg = out.logits[:, -1].float() if logits else None
            caps = self._split_cap(self.cap, list(blocks), device) if blocks else None
        finally:
            self.patch = None; self.cap = None
        return lg, caps

    # ------------------------------------------------------------ sampling
    def generate(self, seqs, max_new, seed, patch=None, temperature=0.7, positions=None, blocks=(), first_logits=False):
        """Left-padded batched sampling (T 0.7, top_p 1, top_k off unless overridden). Patch applies to the prefill only.
        Returns list of new-token lists (cut after the first eos, eos excluded) [, first-step logits]."""
        x, am, pos, L, offs = self.left(seqs)
        self.patch = self._build_patch(patch, offs) if patch else None; self.patch_len = L
        self.cap = self._build_cap(positions, offs, blocks, L) if blocks else None
        torch.manual_seed(seed)
        try:
            o = self.model.generate(input_ids=x, attention_mask=am, do_sample=True, temperature=temperature, top_p=1.0, top_k=0,
                                    max_new_tokens=max_new, eos_token_id=EOS, pad_token_id=PAD, return_dict_in_generate=True,
                                    output_logits=first_logits)
            caps = self._split_cap(self.cap, list(blocks)) if blocks else None
        finally:
            self.patch = None; self.cap = None
        seq = o.sequences[:, L:].tolist()
        res = []
        for s in seq:
            cut = []
            for t in s:
                if t in EOS:
                    break
                cut.append(t)
            res.append(cut)
        extra = []
        if first_logits:
            extra.append(o.logits[0].float())
        if blocks:
            extra.append(caps)
        return (res, *extra) if extra else res

    def decode(self, ids):
        return self.tok.decode(ids, skip_special_tokens=True)


def mem():
    return dict(alloc_gb=round(torch.cuda.memory_allocated() / 2**30, 1), peak_gb=round(torch.cuda.max_memory_allocated() / 2**30, 1),
                free_gb=round(torch.cuda.mem_get_info()[0] / 2**30, 1))
