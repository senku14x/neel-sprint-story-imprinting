"""E12 R03 GPU engine (from E14 R01 engine.py): one bf16 base on GPU 0, six named PEFT adapters (parent = adapter disabled),
the ft42 SAE (E12 R02, block 42) in bf16 on the GPU.
Block L = output of decoder layer L (model.base_model.model.model.layers[L]), E14 R01's convention.
SAE encode (E12 R02 / R01 convention): pre = (x - b_dec) @ W_enc + b_enc, relu, per-token top-64. d_i = decoder.weight[:, i].
Hooks (one per block, applied in this order: edits, then capture):
  set  : h[row, pos] = v                      (prompt pass only)
  add  : h[row, pos] += v                     (prompt pass only)
  code : h[row, pos] += sum_i (target_i - c_i(h)) d_i over the row's entries   (block 42, prompt pass only)
  rm   : h -= sum_i c_i(h) d_i over the row's entries, at every position of every forward call (prompt and generated: mode
         'all') or at given prompt positions (mode 'hdr'); codes encoded on the fly.
Attention mask edit (Part 3d): pre-hook on the 16 full-attention layers adds -inf to (query >= qstart[row], key in kblock[row]).
Attention capture (Part 3c): eager attention, forward hook on the full-attention modules: mean over heads and the last 7 queries."""
import contextlib, math, os, sys, time
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r03lib import *  # noqa

torch.backends.cuda.matmul.allow_tf32 = False
ALL_ADAPTERS = ("S", "SB", "ctrl_A_s0", "ctrl_B_s0", "V", "VB")


class Eng:
    def __init__(self, adapters=ALL_ADAPTERS, sae=True):
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
        assert len(self.layers) == 64
        self.adapters = list(adapters)
        self.plen = None; self.ops = {}; self.cap = None; self.amask = None; self.attn_cap = None
        for L in range(64):
            self.layers[L].register_forward_hook(self._block_hook(L))
        for L in FULL_ATTN:
            sa = self.layers[L].self_attn
            sa.register_forward_pre_hook(self._attn_pre(L), with_kwargs=True)
            sa.register_forward_hook(self._attn_post(L))
        self.load_secs = time.time() - t0
        if sae:
            self.load_sae()

    # ------------------------------------------------------------ SAE
    def load_sae(self):
        t0 = time.time()
        sd = torch.load(SAE_PT, map_location="cpu", mmap=True, weights_only=False)
        self.W_enc = sd["encoder.weight"].T.contiguous().to("cuda", torch.bfloat16)   # [D, F]
        self.b_enc = sd["encoder.bias"].to("cuda", torch.bfloat16)
        self.W_dec = sd["decoder.weight"].T.contiguous().to("cuda", torch.bfloat16)   # [F, D]; row i = d_i
        self.b_dec = sd["b_dec"].to("cuda", torch.bfloat16)
        self.b_dec32 = sd["b_dec"].float().cuda()
        self.dn = sd["decoder.weight"].float().norm(dim=0).cuda()                    # ||d_i||  [F]
        self.F = self.W_enc.shape[1]; self.K = 64
        del sd
        try:
            a = torch.randn(4, 5120, device="cuda", dtype=torch.bfloat16)
            torch.mm(a, self.W_enc[:, :8], out_dtype=torch.float32)
            self.mm32 = True
        except Exception:  # noqa: BLE001
            self.mm32 = False
        self.sae_secs = time.time() - t0

    def encode(self, x, chunk=2048):
        """x [n, D] -> (vals fp32 [n, 64], idx long [n, 64]): relu then top-64 per token."""
        V, I = [], []
        for s in range(0, x.shape[0], chunk):
            xx = (x[s:s + chunk].to(torch.bfloat16) - self.b_dec)
            if self.mm32:
                pre = torch.mm(xx, self.W_enc, out_dtype=torch.float32) + self.b_enc.float()
            else:
                pre = (xx @ self.W_enc + self.b_enc).float()
            pre.relu_()
            tk = torch.topk(pre, self.K, dim=-1)
            V.append(tk.values); I.append(tk.indices)
            del pre
        if not V:
            return torch.zeros((0, self.K), device="cuda"), torch.zeros((0, self.K), dtype=torch.long, device="cuda")
        return torch.cat(V), torch.cat(I)

    def codes_U(self, x, U):
        """codes of the entries U (long tensor [u]) at x [n, D] -> [n, u] fp32 (top-64 convention)."""
        v, i = self.encode(x)
        return (v[:, :, None] * (i[:, :, None] == U[None, None, :])).sum(1)

    def recon(self, v, i):
        """decoder output of sparse codes (without b_dec): [n, D] fp32."""
        out = torch.zeros((v.shape[0], self.W_dec.shape[1]), device="cuda")
        for s in range(0, v.shape[0], 1024):
            out[s:s + 1024] = torch.einsum("nk,nkd->nd", v[s:s + 1024], self.W_dec[i[s:s + 1024]].float())
        return out

    # ------------------------------------------------------------ hooks
    def _block_hook(self, L):
        def f(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            pre = h.shape[1] == self.plen
            for op in self.ops.get(L, ()):
                op(h, pre)
            c = self.cap
            if c is not None and pre and L in c["blocks"]:
                c["out"][L] = h[c["rows"], c["pos"]].clone()
            return out
        return f

    def _attn_pre(self, L):
        def f(mod, args, kwargs):
            A = self.amask
            if A is None:
                return None
            hs = kwargs["hidden_states"] if "hidden_states" in kwargs else args[0]
            B, q = hs.shape[0], hs.shape[1]
            pkv = kwargs.get("past_key_values")
            past = pkv.get_seq_length(mod.layer_idx) if pkv is not None else 0
            klen = past + q
            qabs = past + torch.arange(q, device=hs.device)
            cq = qabs[None, :] >= A["qstart"][:, None]                                   # [B, q]
            kb = torch.zeros((B, klen), dtype=torch.bool, device=hs.device)
            n = min(klen, A["kblock"].shape[1]); kb[:, :n] = A["kblock"][:, :n]
            blocked = cq[:, :, None] & kb[:, None, :]                                    # [B, q, k]
            m = kwargs.get("attention_mask")
            if m is None:
                kpos = torch.arange(klen, device=hs.device)
                m = (kpos[None, None, :] <= qabs[None, :, None]).expand(B, q, klen)[:, None]
                m = m & ~blocked[:, None]
            elif m.dtype == torch.bool:
                m = m.expand(B, -1, q, klen) & ~blocked[:, None]
            else:
                m = m.expand(B, -1, q, klen).masked_fill(blocked[:, None], torch.finfo(m.dtype).min)
            kwargs["attention_mask"] = m
            A["n_calls"] = A.get("n_calls", 0) + 1
            return args, kwargs
        return f

    def _attn_post(self, L):
        def f(mod, inp, out):
            c = self.attn_cap
            if c is None or not isinstance(out, tuple) or out[1] is None:
                return out
            w = out[1]
            if w.shape[2] == self.plen:
                c[L] = w[:, :, -7:, :].float().mean(dim=(1, 2)).cpu()                 # [B, k]
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

    # ------------------------------------------------------------ batching
    def left(self, seqs):
        L = max(len(s) for s in seqs)
        x = torch.full((len(seqs), L), PAD, dtype=torch.long, device="cuda")
        am = torch.zeros((len(seqs), L), dtype=torch.long, device="cuda")
        for b, s in enumerate(seqs):
            x[b, L - len(s):] = torch.tensor(s, device="cuda"); am[b, L - len(s):] = 1
        pos = (am.cumsum(-1) - 1).clamp(min=0)
        return x, am, pos, L, [L - len(s) for s in seqs]

    def _build_cap(self, positions, offs, blocks, Ltot):
        rows, pos, lay = [], [], []
        for r, ps in enumerate(positions):
            lay.append((len(pos), len(ps)))
            rows += [r] * len(ps); pos += [q + offs[r] for q in ps]
        return dict(blocks=set(blocks), out={}, rows=torch.tensor(rows, device="cuda", dtype=torch.long),
                    pos=torch.tensor(pos, device="cuda", dtype=torch.long), lay=lay)

    @staticmethod
    def _split_cap(c, blocks):
        return [torch.stack([c["out"][L][s:s + n] for L in blocks], 1) for s, n in c["lay"]]  # [n, nb, H] (GPU, bf16)

    def _build_ops(self, specs, offs):
        """specs: per row a list of op dicts (or None). Returns {L: [callables]}."""
        ops = {}
        if not specs or all(not s for s in specs):
            return ops
        grp = {}
        for r, sp in enumerate(specs):
            for o in (sp or []):
                key = (o["kind"], o.get("L", 42))
                grp.setdefault(key, []).append((r, o))
        for (kind, L), items in grp.items():
            if kind in ("set", "add"):
                rows = torch.cat([torch.full((len(o["pos"]),), r, dtype=torch.long) for r, o in items]).cuda()
                pos = torch.tensor([p + offs[r] for r, o in items for p in o["pos"]], dtype=torch.long, device="cuda")
                vals = torch.cat([o["vals"].to("cuda") for r, o in items]).float()

                def f(h, pre, rows=rows, pos=pos, vals=vals, kind=kind):
                    if not pre:
                        return
                    if kind == "set":
                        h[rows, pos] = vals.to(h.dtype)
                    else:
                        h[rows, pos] = (h[rows, pos].float() + vals).to(h.dtype)
                ops.setdefault(L, []).append(f)
            elif kind == "code":
                U = sorted({e for r, o in items for e in o["U"]})
                Ut = torch.tensor(U, dtype=torch.long, device="cuda"); ui = {e: k for k, e in enumerate(U)}
                rows, pos, tg, mk = [], [], [], []
                for r, o in items:
                    for j, p in enumerate(o["pos"]):
                        rows.append(r); pos.append(p + offs[r])
                        t = torch.zeros(len(U)); m = torch.zeros(len(U))
                        for k, e in enumerate(o["U"]):
                            t[ui[e]] = float(o["tgt"][j][k]); m[ui[e]] = 1.0
                        tg.append(t); mk.append(m)
                rows = torch.tensor(rows, device="cuda"); pos = torch.tensor(pos, device="cuda")
                tg = torch.stack(tg).cuda(); mk = torch.stack(mk).cuda(); Wd = self.W_dec[Ut].float()

                def f(h, pre, rows=rows, pos=pos, tg=tg, mk=mk, Ut=Ut, Wd=Wd):
                    if not pre:
                        return
                    x = h[rows, pos]
                    c = self.codes_U(x, Ut)
                    h[rows, pos] = (x.float() + ((tg - c) * mk) @ Wd).to(h.dtype)
                ops.setdefault(L, []).append(f)
            elif kind in ("rm_all", "rm_hdr"):
                U = sorted({e for r, o in items for e in o["U"]})
                Ut = torch.tensor(U, dtype=torch.long, device="cuda"); ui = {e: k for k, e in enumerate(U)}
                Wd = self.W_dec[Ut].float()
                if kind == "rm_all":
                    rws = sorted({r for r, o in items})
                    mem = torch.zeros((len(rws), len(U)), device="cuda")
                    for j, r in enumerate(rws):
                        for r2, o in items:
                            if r2 == r:
                                for e in o["U"]:
                                    mem[j, ui[e]] = 1.0
                    rt = torch.tensor(rws, dtype=torch.long, device="cuda"); offr = torch.tensor([offs[r] for r in rws], device="cuda")

                    def f(h, pre, rt=rt, mem=mem, Ut=Ut, Wd=Wd, offr=offr):
                        B, Tn, D = h.shape
                        x = h[rt]                                                   # [nr, T, D]
                        if pre:  # skip left padding
                            tpos = torch.arange(Tn, device="cuda")[None, :] >= offr[:, None]
                        else:
                            tpos = torch.ones((len(rt), Tn), dtype=torch.bool, device="cuda")
                        rr, tt = tpos.nonzero(as_tuple=True)
                        xs = x[rr, tt]
                        c = self.codes_U(xs, Ut) * mem[rr]
                        x[rr, tt] = (xs.float() - c @ Wd).to(h.dtype)
                        h[rt] = x
                    ops.setdefault(42, []).append(f)
                else:
                    rows, pos, mk = [], [], []
                    for r, o in items:
                        m = torch.zeros(len(U))
                        for e in o["U"]:
                            m[ui[e]] = 1.0
                        for p in o["pos"]:
                            rows.append(r); pos.append(p + offs[r]); mk.append(m)
                    rows = torch.tensor(rows, device="cuda"); pos = torch.tensor(pos, device="cuda"); mk = torch.stack(mk).cuda()

                    def f(h, pre, rows=rows, pos=pos, mk=mk, Ut=Ut, Wd=Wd):
                        if not pre:
                            return
                        x = h[rows, pos]
                        c = self.codes_U(x, Ut) * mk
                        h[rows, pos] = (x.float() - c @ Wd).to(h.dtype)
                    ops.setdefault(42, []).append(f)
            else:
                raise ValueError(kind)
        return ops

    def _build_amask(self, masks, offs, L):
        """masks: per row None or (qstart_rel, [key positions rel]). Returns spec or None."""
        if not masks or all(m is None for m in masks):
            return None
        B = len(masks)
        qs = torch.full((B,), 10 ** 9, dtype=torch.long)
        kb = torch.zeros((B, L), dtype=torch.bool)
        for r, m in enumerate(masks):
            if m is None:
                continue
            q0, keys = m
            qs[r] = q0 + offs[r]
            if keys:
                kb[r, torch.tensor([k + offs[r] for k in keys])] = True
        return dict(qstart=qs.cuda(), kblock=kb.cuda())

    def _setup(self, seqs, specs, masks, positions, blocks):
        x, am, pos, L, offs = self.left(seqs)
        self.plen = L
        self.ops = self._build_ops(specs, offs)
        self.amask = self._build_amask(masks, offs, L)
        self.cap = self._build_cap(positions, offs, blocks, L) if blocks else None
        return x, am, pos, L, offs

    def _clear(self):
        self.ops = {}; self.cap = None; self.amask = None; self.plen = None

    # ------------------------------------------------------------ forward (teacher forced)
    def forward(self, seqs, positions=None, blocks=(), specs=None, masks=None, logits=True, lp_ids=None):
        """Returns (last-position logits fp32 [B, V] or log-probs of lp_ids [B, len], captures list [n_i, nb, H] bf16 GPU)."""
        x, am, pos, L, offs = self._setup(seqs, specs, masks, positions, blocks)
        try:
            out = self.inner(input_ids=x, attention_mask=am, position_ids=pos, use_cache=False, logits_to_keep=1)
            lg = out.logits[:, -1].float() if logits else None
            if lg is not None and lp_ids is not None:
                lg = torch.log_softmax(lg, -1)[:, lp_ids]
            caps = self._split_cap(self.cap, list(blocks)) if blocks else None
        finally:
            self._clear()
        return lg, caps

    # ------------------------------------------------------------ sampling
    def generate(self, seqs, max_new, seed, specs=None, masks=None, temperature=0.7, row_seeds=None):
        """Left-padded batched sampling (T 0.7, top_p 1, top_k off): one torch.manual_seed per call (E14 R01), or per-row
        generators (row_seeds) through a sampling logits processor. Returns new-token lists cut at the first eos."""
        from transformers import LogitsProcessor, LogitsProcessorList
        x, am, pos, L, offs = self._setup(seqs, specs, masks, None, ())
        try:
            if row_seeds is None:
                torch.manual_seed(seed)
                o = self.model.generate(input_ids=x, attention_mask=am, do_sample=True, temperature=temperature, top_p=1.0, top_k=0,
                                        repetition_penalty=1.0, max_new_tokens=max_new, eos_token_id=EOS, pad_token_id=PAD, logits_to_keep=1)
            else:
                gens = [torch.Generator(device="cuda").manual_seed(int(s)) for s in row_seeds]

                class RowSampler(LogitsProcessor):
                    def __call__(self, input_ids, scores):
                        p = torch.softmax(scores.float() / temperature, -1)
                        outp = torch.full_like(scores, -float("inf"))
                        for b in range(p.shape[0]):
                            t = torch.multinomial(p[b], 1, generator=gens[b])
                            outp[b, t] = 0.0
                        return outp
                o = self.model.generate(input_ids=x, attention_mask=am, do_sample=False, top_p=1.0, top_k=0, temperature=1.0,
                                        repetition_penalty=1.0, max_new_tokens=max_new, eos_token_id=EOS, pad_token_id=PAD, logits_to_keep=1,
                                        logits_processor=LogitsProcessorList([RowSampler()]))
        finally:
            self._clear()
            torch.cuda.empty_cache()
        res = []
        for s in o[:, L:].tolist():
            cut = []
            for t in s:
                if t in EOS:
                    break
                cut.append(t)
            res.append(cut)
        return res

    def decode(self, ids):
        return self.tok.decode(ids, skip_special_tokens=True)

    def set_attn(self, impl):
        self.inner.set_attn_implementation(impl)
        return self.layers[FULL_ATTN[0]].self_attn.config._attn_implementation


def mem():
    return dict(alloc_gb=round(torch.cuda.memory_allocated() / 2**30, 1), peak_gb=round(torch.cuda.max_memory_allocated() / 2**30, 1),
                free_gb=round(torch.cuda.mem_get_info()[0] / 2**30, 1))


def batches_by_len(items, n=64, key=len):
    order = sorted(range(len(items)), key=lambda i: key(items[i]))
    return [order[i:i + n] for i in range(0, len(order), n)]
