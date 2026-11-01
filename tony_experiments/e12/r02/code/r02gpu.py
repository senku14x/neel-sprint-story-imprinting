"""E12 R02 GPU helpers on top of R01's engine (copied to /workspace/e12/r02/code, paths only changed).
- Eng: R01's Engine with block hooks on every block R02 needs and a splice at any block (R01's splice was block 42 only).
- GSAE: one wrapper for every SAE: R01's layer-42 BatchTopK (encode = relu then top-64 per token, R01's chosen convention),
  the fine-tuned one (same format), and the caiovicentino1 TopK SAEs (encode = top-128 of the pre-activation, then relu,
  as their cards' TopKSAE; no input normalisation in their cfg).
- header_kl: KL(clean || spliced) of the next-token distribution at p1 when the 7 header tokens' block-L states are replaced
  by the SAE reconstruction (error dropped), and the noise control (x + Gaussian noise with the per-token norm of the SAE
  error). The prefix before the header is run once with the cache; every variant reruns only the 7 header tokens on a copy
  of the cache (block L's output at the header does not depend on the splice, so all variants see the same clean x)."""
import copy, json, math, os, random, sys, time
sys.path.insert(0, "/workspace/e12/r02/code")
from e12gpu import *  # noqa  (Engine, log, open_log, StopForward, R, R01, ...)
import e12gpu
import torch

R02 = "/workspace/e12/r02"
SCR = "/root/e12r02"
HDR_IDS = [248045, 74455, 198, 248068, 271, 248069, 271]  # <|im_start|> assistant \n <think> \n\n </think> \n\n
SAE42_DIR = f"{R01}/sae/saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0"
OTHER = {
    "pg31": dict(file=f"{R02}/sae_other/qwen36-27b-sae-papergrade/sae_L31_latest.safetensors", N=31, card_ev=0.7135),
    "pg55": dict(file=f"{R02}/sae_other/qwen36-27b-sae-papergrade/sae_L55_latest.safetensors", N=55, card_ev=0.8157),
    "fs35": dict(file=f"{R02}/sae_other/qwen36-27b-sae-fullstack/sae_L35_latest.safetensors", N=35, card_ev=0.5890475613983167),
    "fs39": dict(file=f"{R02}/sae_other/qwen36-27b-sae-fullstack/sae_L39_latest.safetensors", N=39, card_ev=0.5873812523874239),
    "fs43": dict(file=f"{R02}/sae_other/qwen36-27b-sae-fullstack/sae_L43_latest.safetensors", N=43, card_ev=0.6036171498670027),
}
CAND_BLOCKS = sorted({b for v in OTHER.values() for b in (v["N"] - 1, v["N"], v["N"] + 1)} | {42})


class Eng(Engine):
    REC_BLOCKS = tuple(CAND_BLOCKS)

    def __init__(self, adapters=("V", "VB", "S", "SB", "ctrl_A_s0", "ctrl_B_s0")):
        self.splices = {}
        super().__init__(adapters)

    def _mk_block_hook(self, L):
        def fn(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            sp = self.splices.get(L)
            if sp is not None:
                fb, ft, val = sp
                v = val(h[fb, ft]) if callable(val) else val
                h[fb, ft] = v.to(h.dtype)
            r = self.rec
            if r is not None and L in r["blocks"]:
                r["out"][L] = h[r["fb"], r["ft"]].detach().float()
            if r is not None and r.get("stop_after") == L:
                raise StopForward()
            return out
        return fn


class GSAE:
    def __init__(self, name, device="cuda"):
        self.name = name
        if name in ("orig42", "ft42"):
            p = f"{SAE42_DIR}/ae.pt" if name == "orig42" else f"{R02}/sae_ft/ae.pt"
            sd = torch.load(p, map_location="cpu")
            self.W_enc = sd["encoder.weight"].T.contiguous().float(); self.b_enc = sd["encoder.bias"].float()
            self.W_dec = sd["decoder.weight"].T.contiguous().float(); self.b_dec = sd["b_dec"].float()
            self.k = 64; self.kind = "relu_topk"; self.block = 42; self.thr = float(sd["threshold"])
        else:
            from safetensors.torch import load_file
            w = load_file(OTHER[name]["file"])
            self.W_enc = w["W_enc"].float(); self.b_enc = w["b_enc"].float(); self.W_dec = w["W_dec"].float(); self.b_dec = w["b_dec"].float()
            cfg = json.load(open(OTHER[name]["file"].replace("_latest.safetensors", "_cfg.json")))
            self.k = int(cfg["k"]); self.kind = "topk_relu"; self.block = None; self.thr = None
            assert cfg["architecture"] == "topk" and cfg["activation_fn_str"] == "relu"
        self.F = self.W_enc.shape[1]
        self.dev = "cpu"
        self.to(device)

    def to(self, device):
        for k in ("W_enc", "b_enc", "W_dec", "b_dec"):
            setattr(self, k, getattr(self, k).to(device))
        self.dev = device
        return self

    def encode(self, x):
        pre = (x.float() - self.b_dec) @ self.W_enc + self.b_enc
        if self.kind == "relu_topk":
            pre = torch.relu(pre)
            tk = torch.topk(pre, self.k, dim=-1)
            return torch.zeros_like(pre).scatter_(-1, tk.indices, tk.values)
        tk = torch.topk(pre, self.k, dim=-1)
        return torch.zeros_like(pre).scatter_(-1, tk.indices, torch.relu(tk.values))

    def recon(self, x, chunk=2048):
        out = torch.empty(x.shape, dtype=torch.float32, device=x.device)
        for s in range(0, x.shape[0], chunk):
            out[s:s + chunk] = self.encode(x[s:s + chunk]) @ self.W_dec + self.b_dec
        return out

    def stats(self, X, chunk=2048):
        """X: [N, D] CPU fp16/fp32. Returns err_sum, L0 mean, fired mask."""
        err = 0.0; l0 = 0.0; fired = torch.zeros(self.F, dtype=torch.bool, device=self.dev)
        for s in range(0, X.shape[0], chunk):
            x = X[s:s + chunk].to(self.dev).float()
            f = self.encode(x)
            xh = f @ self.W_dec + self.b_dec
            err += float(((x - xh) ** 2).sum()); l0 += float((f > 0).sum()); fired |= (f > 0).any(0)
        return err, l0 / max(1, X.shape[0]), fired


def ev_row(sae, X, mean=None):
    X = X.float()
    xbar = X.mean(0) if mean is None else mean
    tot = float(((X - xbar) ** 2).sum())
    err, l0, fired = sae.stats(X)
    ss = float((X ** 2).sum())
    return dict(n=int(X.shape[0]), EV=1 - err / tot, FVU=err / tot, L0=l0, err_over_sumsq=err / ss, var_share_of_sumsq=tot / ss,
                n_fired=int(fired.sum()))


def outlier_keep(X):
    nrm = X.float().norm(dim=-1); med = float(nrm.median())
    return nrm <= 10 * med, med


def record_pass(E, items, blocks, ce=False, splice_block=None, splice_fn=None, budget=16000, maxb=16):
    """Forward over items (ids, score positions). Records `blocks` at the scored positions (fp16 CPU, item order) and, if ce,
    the next-token CE there. Optional splice at splice_block on the scored positions. Without ce, stops after max(blocks)."""
    acts = {b: [None] * len(items) for b in blocks}; ces = [None] * len(items); ntok = 0
    for bt in E.batches(items, budget, maxb):
        seqs = [items[i]["ids"] for i in bt]
        x, am, pos, L = E._left(seqs)
        fb, ft = [], []
        for j, i in enumerate(bt):
            off = L - len(seqs[j])
            fb += [j] * len(items[i]["score"]); ft += [p + off for p in items[i]["score"]]
        fb = torch.tensor(fb, device="cuda", dtype=torch.long); ft = torch.tensor(ft, device="cuda", dtype=torch.long)
        stop = None if ce else max(blocks)
        E.rec = dict(blocks=set(blocks), fb=fb, ft=ft, out={}, lora=False, stop_after=stop) if blocks else (
            dict(blocks=set(), fb=fb, ft=ft, out={}, lora=False, stop_after=None))
        if splice_block is not None:
            E.splices = {splice_block: (fb, ft, splice_fn)}
        h = None
        try:
            h = E.inner.model(input_ids=x, attention_mask=am, position_ids=pos, use_cache=False).last_hidden_state
        except StopForward:
            pass
        E.splices = {}
        r = E.rec; E.rec = None
        ntok += sum(len(s) for s in seqs)
        if ce:
            tgt = x[fb, ft + 1]; lp = []
            for s in range(0, len(fb), 2048):
                lg = E.lm_head(h[fb[s:s + 2048], ft[s:s + 2048]]).float()
                lp.append(torch.log_softmax(lg, -1).gather(-1, tgt[s:s + 2048, None])[:, 0])
            lp = -torch.cat(lp).cpu()
        s = 0
        for j, i in enumerate(bt):
            n = len(items[i]["score"])
            for b in blocks:
                acts[b][i] = r["out"][b][s:s + n].half().cpu()
            if ce:
                ces[i] = lp[s:s + n]
            s += n
        del h, r
    out = {b: torch.cat(v) for b, v in acts.items()} if blocks else {}
    return out, (torch.cat(ces) if ce else None), ntok


def header_kl(E, ctxs, variants, budget=24000, maxb=16, seed=0):
    """ctxs: dicts with ids ending in the 7 header tokens. variants: dict name -> (block, fn(h)->h') applied to the 7 header
    tokens' block states. Returns {name: [KL per context]} (KL(clean || variant) at p1, nats)."""
    gen = torch.Generator(device="cuda"); gen.manual_seed(seed)
    out = {k: [None] * len(ctxs) for k in variants}
    items = [dict(ids=c["ids"][:-7]) for c in ctxs]
    for c in ctxs:
        assert c["ids"][-7:] == HDR_IDS, "context does not end in the 7-token header"
    names = list(variants)
    for bt in E.batches(items, budget, maxb):
        seqs = [items[i]["ids"] for i in bt]
        x, am, pos, L = E._left(seqs)
        o = E.inner(input_ids=x, attention_mask=am, position_ids=pos, use_cache=True, logits_to_keep=1)
        cache = o.past_key_values; del o
        B = len(bt)
        xi = torch.tensor([HDR_IDS] * B, device="cuda")
        am2 = torch.cat([am, torch.ones((B, 7), dtype=torch.long, device="cuda")], 1)
        p2 = pos[:, -1:] + 1 + torch.arange(7, device="cuda")[None]
        fb = torch.arange(B, device="cuda").repeat_interleave(7); ft = torch.arange(7, device="cuda").repeat(B)
        lps = {}
        allv = ["__clean__"] + names
        for vi, nm in enumerate(allv):
            c2 = copy.deepcopy(cache) if vi < len(allv) - 1 else cache
            if nm != "__clean__":
                blk, fn = variants[nm]
                E.splices = {blk: (fb, ft, fn)}
            o2 = E.inner(input_ids=xi, attention_mask=am2, position_ids=p2, past_key_values=c2, use_cache=True, logits_to_keep=1)
            E.splices = {}
            lps[nm] = torch.log_softmax(o2.logits[:, -1].float(), -1)
            del o2, c2
        del cache
        p0 = lps["__clean__"].exp()
        for nm in names:
            kl = (p0 * (lps["__clean__"] - lps[nm])).sum(-1)
            for j, i in enumerate(bt):
                out[nm][i] = float(kl[j])
        del lps, p0
    return out


def splice_fns(sae, seed=0):
    """(recon fn, noise fn) for one SAE: recon drops the error; noise adds Gaussian noise with the error's per-token norm."""
    gen = torch.Generator(device="cuda"); gen.manual_seed(seed)

    def rec(h):
        return sae.recon(h.float())

    def noise(h):
        hf = h.float(); e = hf - sae.recon(hf)
        n = torch.randn(hf.shape, device=hf.device, generator=gen)
        n = n / n.norm(dim=-1, keepdim=True) * e.norm(dim=-1, keepdim=True)
        return hf + n
    return rec, noise
