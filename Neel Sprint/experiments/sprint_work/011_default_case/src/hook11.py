"""sw011 vLLM swap / clamp / capture hook (executor-9, 30 Oct). Runs inside the vLLM worker via vllm-lens-018 per-request post-hooks
(ctx.abs_start = absolute position of the slice's first row; 018 patch). This module must be importable in the worker
(PYTHONPATH includes this src dir), so cloudpickle sends the SwapHook instance by reference and only its small fields travel.
Big tensors (unit directions [64, H] per key, donor header states [7, 64, H]) live in table files loaded once per worker (_TAB).

kinds (at the 7 header positions lo..lo+6, layers in SWAP_LAYERS, prefill rows only):
  none   no edit (logging / capture only)
  rank1  set the coordinate along unit u_L to tgt[t, L] (per token t, layer L): x' = x + (tgt - x.u) u        (C4 swap; Part C clamp)
  ctrl   push along a control unit direction un_L by the REAL arm's realised per-token displacement norm at that layer:
         x' = x + sign(cn[t, L] - x.un) * norm[t, L] * un  (cn = the donor's coordinate along un; sw009 R7)
  whole  x' = D[t, L] (full state)
Logs: ctx.saved['disp'] [7, 64] realised fp32 |x' - x| per token and layer (disp_rt: after the bf16 cast); ctx.saved['npatch'] count of (token, layer) edits.
Capture: ctx.saved['cap|<label>|<L>'] post-intervention state rows (fp16) for token-position labels; '<label>|<L>|sum' / '|n' for
mean-span labels."""
import torch

_TAB = {}
SWAP_LAYERS = tuple(range(16, 64))


def _tab(path):
    t = _TAB.get(path)
    if t is None:
        t = torch.load(path, map_location="cuda", weights_only=False)
        _TAB[path] = t
    return t


class SwapHook:
    def __init__(self, kind, lo, table=None, ukey=None, dkey=None, tgt=None, norm=None, cn=None, cap=None, log=True, layers=SWAP_LAYERS):
        self.kind, self.lo, self.table, self.ukey, self.dkey = kind, int(lo), table, ukey, dkey
        self.tgt = tgt.float().cpu().contiguous() if tgt is not None else None      # [7, 64]
        self.norm = norm.float().cpu().contiguous() if norm is not None else None   # [7, 64]
        self.cn = cn.float().cpu().contiguous() if cn is not None else None         # [7, 64]
        self.cap = cap or {}   # {"tok": {label: [abs positions]}, "mean": {label: [abs positions]}, "layers": [...]}
        self.log = log; self.layers = frozenset(layers)
        cl = list(self.cap.get("layers", []))
        mx = self.lo + 7
        for d in ("tok", "mean"):
            for ps in self.cap.get(d, {}).values():
                if ps:
                    mx = max(mx, max(ps) + 1)
        self.cap_layers = frozenset(cl); self.maxpos = mx

    def __call__(self, ctx, h):
        a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx
        if a0 >= self.maxpos:
            return None
        sv = ctx.saved; out = None
        lo, hi = max(self.lo, a0), min(self.lo + 7, a0 + n)
        if self.kind != "none" and L in self.layers and hi > lo:
            out = h.clone(); r0, r1 = lo - a0, hi - a0; ti = slice(lo - self.lo, hi - self.lo)
            x = h[r0:r1].float()
            if self.kind == "whole":
                xn = _tab(self.table)["D"][self.dkey][ti, L].float()
            else:
                u = _tab(self.table)["U"][self.ukey][L].float()
                if self.kind == "rank1":
                    c = x @ u; tg = self.tgt[ti, L].to(x.device); xn = x + (tg - c)[:, None] * u[None]
                elif self.kind == "ctrl":
                    c = x @ u; cn = self.cn[ti, L].to(x.device); s = torch.sign(cn - c); s = torch.where(s == 0, torch.ones_like(s), s)
                    xn = x + (s * self.norm[ti, L].to(x.device))[:, None] * u[None]
                else:
                    raise ValueError(self.kind)
            out[r0:r1] = xn.to(h.dtype)
            if self.log:
                if "disp" not in sv:
                    sv["disp"] = torch.zeros(7, 64); sv["disp_rt"] = torch.zeros(7, 64); sv["npatch"] = 0
                sv["disp"][ti, L] = (xn - x).norm(dim=-1).cpu()  # intended fp32 displacement (what controls are matched on, C4 / R7)
                sv["disp_rt"][ti, L] = (out[r0:r1].float() - x).norm(dim=-1).cpu()  # after the cast back to the model dtype
                sv["npatch"] += r1 - r0
        if self.cap_layers and L in self.cap_layers:
            src = out if out is not None else h
            for lab, ps in self.cap.get("tok", {}).items():
                for j, p in enumerate(ps):
                    if a0 <= p < a0 + n:
                        sv[f"cap|{lab}|{j}|{L}"] = src[p - a0].detach().to(torch.float16).cpu()
            for lab, ps in self.cap.get("mean", {}).items():
                rows = [p - a0 for p in ps if a0 <= p < a0 + n]
                if rows:
                    s = src[rows].float().sum(0).cpu(); k = f"{lab}|{L}"
                    sv[k + "|sum"] = sv.get(k + "|sum", 0) + s; sv[k + "|n"] = sv.get(k + "|n", 0) + len(rows)
        return out
