"""E12 R01 GPU engine (HF transformers 5.17 + PEFT 0.21, bf16, one H100).
Base /dev/shm/qwen36_27b (Qwen/Qwen3.6-27B @ 6a9e13bd, text-only causal LM, as R09/R10 loaded it). All adapters (V, VB, S, SB,
ctrl_A_s0, ctrl_B_s0) loaded unmerged into one PeftModel and switched by name; parent = adapter disabled.
Block L = model.model.layers[L] output (= hidden_states[L+1]).

Readouts (teacher forced):
  O: at p1, log sum_o p(opening o) over the six openings (each the full token sequence).
  C: reply forced to begin "Random animal fact: the"; log p(winner's animal) - log p(other) over the first tokens of " bee" / " crow".
  H: sum of log p(span tokens | fixed text + header + prefix).
O and C share one prefix pass per context (left padded, attention mask, cache); each of the 7 continuations is fed on a deep
copy of the cache.
"""
import copy, json, math, os, re, sys, time
from contextlib import contextmanager

import torch

sys.path.insert(0, "/workspace/e12/r01/code")
from e12lib import *  # noqa

LOGF = None


def log(**kw):
    kw["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    s = json.dumps(kw, default=str)
    if LOGF is not None:
        LOGF.write(s + "\n"); LOGF.flush()
    print(s[:1500], flush=True)


def open_log(name):
    global LOGF
    LOGF = open(f"{R}/logs/{name}.jsonl", "a")


class Engine:
    REC_BLOCKS = (16, 24, 32, 40, 42, 48)

    def __init__(self, adapters=("V", "VB", "S", "SB", "ctrl_A_s0", "ctrl_B_s0")):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
        from peft.tuners.lora import LoraLayer
        torch.set_grad_enabled(False)
        t0 = time.time()
        self.tok = AutoTokenizer.from_pretrained(BASE)
        self.rd = Renderer(self.tok)
        base = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
        names = [a for a in adapters if os.path.exists(f"{ADAPTERS[a]}/adapter_model.safetensors")]
        self.missing_adapters = [a for a in adapters if a not in names]
        model = PeftModel.from_pretrained(base, ADAPTERS[names[0]], adapter_name=names[0])
        for a in names[1:]:
            model.load_adapter(ADAPTERS[a], adapter_name=a)
        model.eval()
        self.model, self.adapters = model, names
        self.inner = model.base_model.model
        self.layers = self.inner.model.layers
        self.norm = self.inner.model.norm
        self.lm_head = self.inner.lm_head
        self.pad = self.tok.pad_token_id if self.tok.pad_token_id is not None else 248044
        self.lmods = []
        for n, m in model.named_modules():
            if isinstance(m, LoraLayer):
                L = int(re.search(r"layers\.(\d+)\.", n).group(1))
                self.lmods.append((L, n.split(f"layers.{L}.", 1)[1], m))
        self.lmods.sort(key=lambda x: (x[0], x[1]))
        self.mod_names = [f"{L}.{n}" for L, n, _ in self.lmods]
        self.scal0 = {a: [m.scaling[a] for _, _, m in self.lmods] for a in names}
        self.rec = None      # recording spec for the current forward
        self.splice = None   # Stage 0: (flat_b, flat_t, values or callable) applied to block 42's output
        for L in self.REC_BLOCKS:
            self.layers[L].register_forward_hook(self._mk_block_hook(L))
        self.norm.register_forward_hook(self._norm_hook)
        for i, (L, n, m) in enumerate(self.lmods):
            for a in names:
                m.lora_A[a].register_forward_hook(self._mk_lA_hook(i))
                m.lora_B[a].register_forward_hook(self._mk_lB_hook(i, a))
        self.cur = None
        self.t200 = None
        log(event="engine_loaded", secs=round(time.time() - t0), adapters=names, missing=self.missing_adapters,
            n_lora_modules=len(self.lmods), lora_dtypes=sorted({str(p.dtype) for n_, p in model.named_parameters() if "lora_" in n_}),
            mem_gb=round(torch.cuda.memory_allocated() / 2**30, 1), free_gb=round(torch.cuda.mem_get_info()[0] / 2**30, 1),
            lora_B_nonzero={a: int(sum(1 for n_, p in model.named_parameters() if f"lora_B.{a}." in n_ and p.abs().max() > 0)) for a in names},
            lora_B_total={a: int(sum(1 for n_, p in model.named_parameters() if f"lora_B.{a}." in n_)) for a in names})

    # ---------------- hooks ----------------
    def _mk_block_hook(self, L):
        def fn(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            if L == 42 and self.splice is not None:
                fb, ft, val = self.splice
                v = val(h[fb, ft]) if callable(val) else val
                h[fb, ft] = v.to(h.dtype)
            r = self.rec
            if r is not None and L in r["blocks"]:
                r["out"][L] = h[r["fb"], r["ft"]].detach().float()
                if r.get("topic") is not None and L == 42:
                    tb, tt = r["topic"]
                    r["topic_out"]["lens42"] = h[tb, tt].detach()
            if r is not None and r.get("stop_after") == L:
                raise StopForward()
            return out
        return fn

    def _norm_hook(self, mod, inp, out):
        r = self.rec
        if r is not None and r.get("topic") is not None:
            tb, tt = r["topic"]
            r["topic_out"]["final"] = out[tb, tt].detach()
        return out

    def _mk_lA_hook(self, i):
        def fn(mod, inp, out):
            r = self.rec
            if r is not None and r.get("lora"):
                r["lA"][i] = out[r["lb"], r["lt"]].detach().float()
            return out
        return fn

    def _mk_lB_hook(self, i, a):
        def fn(mod, inp, out):
            r = self.rec
            if r is not None and r.get("lora"):
                sc = self.lmods[i][2].scaling[a]
                r["lB"][i] = (out[r["lb"], r["lt"]].detach().float() * sc).norm(dim=-1)
            return out
        return fn

    # ---------------- adapter switching ----------------
    @contextmanager
    def use(self, name):
        if name == "parent":
            with self.model.disable_adapter():
                yield
        else:
            self.model.set_adapter(name)
            yield
        self.cur = None

    def set_bands(self, name, on_layers=None):
        """LoRA scaling of every module of adapter `name` outside on_layers set to 0 (None = all on, original scaling)."""
        for i, (L, n, m) in enumerate(self.lmods):
            m.scaling[name] = self.scal0[name][i] if (on_layers is None or L in on_layers) else 0.0

    # ---------------- batching ----------------
    @staticmethod
    def batches(items, budget=16000, maxb=16, key="ids"):
        order = sorted(range(len(items)), key=lambda i: len(items[i][key]))
        out, cur, Lc = [], [], 0
        for i in order:
            L = len(items[i][key])
            if cur and ((len(cur) + 1) * max(L, Lc) > budget or len(cur) >= maxb):
                out.append(cur); cur = []; Lc = 0
            cur.append(i); Lc = max(Lc, L)
        if cur:
            out.append(cur)
        return out

    def _left(self, seqs):
        L = max(len(s) for s in seqs)
        x = torch.full((len(seqs), L), self.pad, dtype=torch.long, device="cuda")
        am = torch.zeros((len(seqs), L), dtype=torch.long, device="cuda")
        for b, s in enumerate(seqs):
            x[b, L - len(s):] = torch.tensor(s, device="cuda"); am[b, L - len(s):] = 1
        pos = (am.cumsum(-1) - 1).clamp(min=0)
        return x, am, pos, L

    # ---------------- O and C (+ recording) ----------------
    def oc(self, items, cont, blocks=(), groups=("p1", "header"), lora=False, topic=False, want=True, budget=16000, maxb=16):
        """items: dicts with ids, p1, header, prohib, system[, t1]. cont: dict name -> token list (openings + bridge).
        Returns list (same order) of dict(first={name: logp vector for read ids}, lp={name: [logp per token]}, acts, lora, ...).
        blocks: blocks whose states are recorded at the positions of `groups` (float16, CPU)."""
        res = [None] * len(items)
        ntok = 0
        for bt in self.batches(items, budget, maxb):
            tb0 = time.time()
            seqs = [items[i]["ids"] for i in bt]
            x, am, pos, L = self._left(seqs)
            off = [L - len(s) for s in seqs]
            # gather layout
            fb, ft, lay = [], [], []
            for j, i in enumerate(bt):
                it = items[i]; d = {}
                for g in groups:
                    ps = [it["p1"]] if g == "p1" else it.get(g, [])
                    d[g] = (len(ft), len(ps))
                    fb += [j] * len(ps); ft += [p + off[j] for p in ps]
                lay.append(d)
            lb, lt = [], []
            for j, i in enumerate(bt):
                it = items[i]
                ps = [it["p1"]] + it["header"]
                lb += [j] * len(ps); lt += [p + off[j] for p in ps]
            r = dict(blocks=set(blocks), fb=torch.tensor(fb, device="cuda", dtype=torch.long),
                     ft=torch.tensor(ft, device="cuda", dtype=torch.long), out={}, lora=lora,
                     lb=torch.tensor(lb, device="cuda", dtype=torch.long), lt=torch.tensor(lt, device="cuda", dtype=torch.long),
                     lA={}, lB={}, topic=None, topic_out={})
            if topic:
                tb, tt, tl = [], [], []
                for j, i in enumerate(bt):
                    it = items[i]
                    ps = it.get("t1", []) + [it["p1"]]
                    tb += [j] * len(ps); tt += [p + off[j] for p in ps]; tl += ["t1"] * len(it.get("t1", [])) + ["p1"]
                r["topic"] = (torch.tensor(tb, device="cuda"), torch.tensor(tt, device="cuda"))
                r["topic_lab"] = tl
                r["blocks"].add(42)
            self.rec = r
            out = self.inner(input_ids=x, attention_mask=am, position_ids=pos, use_cache=want, logits_to_keep=1)
            self.rec = None
            ntok += sum(len(s) for s in seqs)
            lp0 = torch.log_softmax(out.logits[:, -1].float(), -1)
            per = [dict() for _ in bt]
            if want:
                # continuations: one pass per group of contexts, every continuation a row (cache rows selected and repeated
                # with reorder_cache); single-token openings need only the p1 logits
                cache = out.past_key_values
                names = [nm for nm, ids in cont.items() if len(ids) > 1 or nm == "bridge"]
                for nm, ids in cont.items():
                    if nm not in names:
                        for j in range(len(bt)):
                            per[j][nm] = dict(lp=[float(lp0[j, ids[0]])], next_bee=None, next_crow=None)
                K = len(names); nmax = max(len(cont[nm]) for nm in names)
                cbytes = sum(t.numel() * t.element_size() for t in _cache_tensors(cache))
                per_row = cbytes / len(bt)
                free = torch.cuda.mem_get_info()[0]
                G = max(1, min(len(bt), int(0.45 * free / max(1.0, K * per_row))))
                for g0 in range(0, len(bt), G):
                    gi = list(range(g0, min(len(bt), g0 + G)))
                    c2 = copy.deepcopy(cache) if g0 + G < len(bt) else cache
                    sel = torch.tensor(gi, device="cuda").repeat_interleave(K)
                    c2.reorder_cache(sel)
                    rows = [cont[nm] + [self.pad] * (nmax - len(cont[nm])) for _ in gi for nm in names]
                    xi = torch.tensor(rows, device="cuda")
                    am2 = torch.cat([am[sel], torch.ones((len(sel), nmax), dtype=torch.long, device="cuda")], 1)
                    p2 = pos[sel, -1:] + 1 + torch.arange(nmax, device="cuda")[None]
                    o2 = self.inner(input_ids=xi, attention_mask=am2, position_ids=p2, past_key_values=c2, use_cache=True,
                                    logits_to_keep=nmax)
                    lp = torch.log_softmax(o2.logits.float(), -1)  # [rows, nmax, V]: position k predicts token k+1
                    for a, j in enumerate(gi):
                        for b, nm in enumerate(names):
                            rr = a * K + b; ids = cont[nm]; n = len(ids)
                            toks = [float(lp0[j, ids[0]])] + [float(lp[rr, k - 1, ids[k]]) for k in range(1, n)]
                            per[j][nm] = dict(lp=toks, next_bee=float(lp[rr, n - 1, TOK_ID["bee"]]),
                                              next_crow=float(lp[rr, n - 1, TOK_ID["crow"]]))
                    del c2, o2, lp
                del cache
            for j, i in enumerate(bt):
                d = dict(cont=per[j], p1_bee=float(lp0[j, TOK_ID["bee"]]), p1_crow=float(lp0[j, TOK_ID["crow"]]))
                if blocks:
                    d["acts"] = {}
                    for g, (s, n) in lay[j].items():
                        d["acts"][g] = {b: r["out"][b][s:s + n].half().cpu() for b in blocks if b in r["out"]}
                if lora:
                    nh = 1 + len(items[i]["header"])
                    s = sum(1 + len(items[k]["header"]) for k in bt[:j])
                    A = torch.stack([r["lA"][m][s:s + nh] for m in range(len(self.lmods))])  # [M, nh, 32]
                    Bn = torch.stack([r["lB"][m][s:s + nh] for m in range(len(self.lmods))])  # [M, nh]
                    d["lora"] = dict(A_p1=A[:, 0].half().cpu(), A_hdr=A[:, 1:].mean(1).half().cpu(),
                                     W_p1=Bn[:, 0].float().cpu(), W_hdr=Bn[:, 1:].mean(1).float().cpu())
                res[i] = d
            if topic:
                tl = r["topic_lab"]
                fin = self.lm_head(r["topic_out"]["final"]).float()
                lens = self.lm_head(self.norm(r["topic_out"]["lens42"])).float()
                self.topic_acc(fin, lens, tl)
            del out, lp0, r
            if self.t200 is not None and self.t200["n"] < 200:
                torch.cuda.synchronize()
                self.t200["n"] += len(bt); self.t200["tok"] += sum(len(s) for s in seqs); self.t200["secs"] += time.time() - tb0
                if self.t200["n"] >= 200:
                    log(event="first200", **self.t200, tok_s=self.t200["tok"] / self.t200["secs"])
                    json.dump(dict(self.t200, tok_s=self.t200["tok"] / self.t200["secs"]), open(f"{R}/results/first200_rate.json", "w"))
        return res, ntok

    def topic_reset(self):
        self.topic = {}

    def topic_acc(self, fin, lens, labels):
        lab = torch.tensor([0 if l == "t1" else 1 for l in labels], device=fin.device)
        for gi, g in enumerate(("t1", "p1")):
            msk = lab == gi
            if msk.any():
                for nm, v in (("final", fin), ("lens42", lens)):
                    k = f"{g}|{nm}"
                    s = v[msk].double().sum(0)
                    if k in self.topic:
                        self.topic[k][0] += s; self.topic[k][1] += int(msk.sum())
                    else:
                        self.topic[k] = [s, int(msk.sum())]

    # ---------------- H (span log prob) ----------------
    def span_lp(self, items, budget=16000, maxb=16):
        """items: dicts with ids, span (absolute positions of span tokens), word_tok. Returns per item dict(H, lp list, C_nat)."""
        res = [None] * len(items)
        ntok = 0
        for bt in self.batches(items, budget, maxb):
            seqs = [items[i]["ids"] for i in bt]
            x, am, pos, L = self._left(seqs)
            K = max(len(items[i]["ids"]) - min(items[i]["span"] + [items[i]["word_tok"]]) + 1 for i in bt)
            out = self.inner(input_ids=x, attention_mask=am, position_ids=pos, use_cache=False, logits_to_keep=K)
            ntok += sum(len(s) for s in seqs)
            lg = out.logits  # [B, K, V]; index k <-> absolute position L-K+k (left padded)
            for j, i in enumerate(bt):
                it = items[i]; off = L - len(it["ids"])
                ids = it["ids"]
                rows = [p - 1 + off - (L - K) for p in it["span"]]
                lp = torch.log_softmax(lg[j, rows].float(), -1)
                toks = [float(lp[k, ids[p]]) for k, p in enumerate(it["span"])]
                w = it["word_tok"] - 1 + off - (L - K)
                lw = torch.log_softmax(lg[j, w].float(), -1)
                res[i] = dict(H=sum(toks), lp=toks, nat_bee=float(lw[TOK_ID["bee"]]), nat_crow=float(lw[TOK_ID["crow"]]))
            del out, lg
        return res, ntok

    # ---------------- plain forward with state capture (Part 4 items 1, 2) ----------------
    def states(self, seqs, positions, blocks, budget=24000, maxb=64):
        """Block states at given absolute positions (list per seq) -> list of {block: [n, D] float32 CPU}."""
        items = [dict(ids=s, pos=p) for s, p in zip(seqs, positions)]
        res = [None] * len(items)
        for bt in self.batches(items, budget, maxb):
            x, am, pos, L = self._left([items[i]["ids"] for i in bt])
            fb, ft, lay = [], [], []
            for j, i in enumerate(bt):
                off = L - len(items[i]["ids"])
                lay.append((len(ft), len(items[i]["pos"])))
                fb += [j] * len(items[i]["pos"]); ft += [p + off for p in items[i]["pos"]]
            self.rec = dict(blocks=set(blocks), fb=torch.tensor(fb, device="cuda"), ft=torch.tensor(ft, device="cuda"), out={},
                            lora=False, stop_after=max(blocks))
            try:
                self.inner.model(input_ids=x, attention_mask=am, position_ids=pos, use_cache=False)
            except StopForward:
                pass
            r = self.rec; self.rec = None
            for j, i in enumerate(bt):
                s, n = lay[j]
                res[i] = {b: r["out"][b][s:s + n].cpu() for b in blocks}
        return res


class StopForward(Exception):
    pass


def _cache_tensors(cache):
    out = []
    for L in getattr(cache, "layers", []):
        for k in ("keys", "values"):
            t = getattr(L, k, None)
            if torch.is_tensor(t):
                out.append(t)
        for k in ("conv_states", "recurrent_states"):
            d = getattr(L, k, None)
            if isinstance(d, dict):
                out += [t for t in d.values() if torch.is_tensor(t)]
    return out


def cont_tokens(rd):
    c = {o: rd.T(o) for o in OPENINGS}
    c["bridge"] = rd.T(BRIDGE)
    assert rd.T(" bee")[0] == TOK_ID["bee"] and rd.T(" crow")[0] == TOK_ID["crow"]
    return c


def lse(v):
    m = max(v)
    return m + math.log(sum(math.exp(x - m) for x in v))


def readouts(d, model):
    """O, C from an oc() result (C oriented to the model's winner)."""
    O = lse([sum(d["cont"][o]["lp"]) for o in OPENINGS])
    b = d["cont"]["bridge"]
    cw = b["next_" + WIN[model]] - b["next_" + OTHER[model]]
    return dict(O=O, C=cw, C_bee=b["next_bee"], C_crow=b["next_crow"], O_parts={o: sum(d["cont"][o]["lp"]) for o in OPENINGS})
