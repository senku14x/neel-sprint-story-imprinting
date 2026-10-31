"""sw053 vLLM per-request hook (E1 prep agent, 30 Oct 2026). Adapted from sw011 hook11.SwapHook; runs inside the vLLM worker through
vllm-lens-018 post-hooks (ctx.abs_start, ctx.layer_idx), src/vllm_lens_sw011 (maxpos skip: decode passes replay CUDA graphs).
Importable on CPU (no CUDA at import), so test53.py drives the same object on synthetic states.

kinds (at the 7 header positions lo..lo+6, layers in `layers` (16..63), prefill rows only):
  none : no edit (capture / logging only)
  set  : set the coordinate along the unit vector V_L = table['U'][vkey][L] to tgt[t, L]:  x' = x + (tgt - x . V) V
         real arm   : V = the direction under test, tgt = m0 + a (m1 - m0) (induce) or m1 - a (m1 - m0) (remove)
         control    : V = a random direction r, tgt = (x_none . r) + s * Delta(L, t)  (sw028 A; computed by the driver from the
                      reference capture and the prefill-only Delta pass; so (x' - x_none) . r = s * Delta)
Logs (ctx.saved): 'disp' [7, 64] |x' - x| (fp32 increment at this layer); 'cres' [7, 64] |x'_cast . V - tgt| (after the cast back to
the model dtype: the clamp's known answer); 'cum' [7, 64] ||x'_cast - Xref|| when xkey is given (Xref = table['X'][xkey][t, L - 16],
the same context's reference no-edit state from the capture pass: the cumulative offset; on 'none' rows it is the engine's batch
noise floor); 'cpre' [7, 64] ||x_in - Xref|| BEFORE this layer's edit (upstream edits reaching layer L: the known answer that the
engine applies the states the hook returns; a dropped edit leaves cpre at the noise floor); 'npatch' = number of (token, layer) edits.
Capture (cap=True): ctx.saved['cap|<t>|<L>'] = post-hook header state rows (fp16, CPU) for the capture pass."""
import torch

_TAB = {}
SWAP_LAYERS = tuple(range(16, 64))
L0 = 16


def _tab(path):
    t = _TAB.get(path)
    if t is None:
        t = torch.load(path, map_location="cuda", weights_only=False)
        _TAB[path] = t
    return t


class ClampHook:
    def __init__(self, kind, lo, table=None, vkey=None, tgt=None, xkey=None, cap=False, log=True, layers=SWAP_LAYERS):
        assert kind in ("none", "set"), kind
        self.kind, self.lo, self.table, self.vkey, self.xkey = kind, int(lo), table, vkey, xkey
        self.tgt = tgt.float().cpu().contiguous() if tgt is not None else None   # [7, 64]
        assert kind != "set" or (self.tgt is not None and tuple(self.tgt.shape) == (7, 64) and vkey is not None and table is not None)
        self.cap, self.log = bool(cap), bool(log); self.layers = frozenset(layers)
        self.maxpos = self.lo + 7  # every edit and log is at the header; the engine skips this hook from here on (sw011 R6)

    def __call__(self, ctx, h):
        a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx
        if a0 >= self.maxpos or L not in self.layers:
            return None
        lo, hi = max(self.lo, a0), min(self.lo + 7, a0 + n)
        if hi <= lo:
            return None
        sv = ctx.saved; r0, r1 = lo - a0, hi - a0; ti = slice(lo - self.lo, hi - self.lo)
        x = h[r0:r1].float(); out = None
        if self.log and "npatch" not in sv:
            sv["disp"] = torch.zeros(7, 64); sv["cres"] = torch.zeros(7, 64); sv["cum"] = torch.zeros(7, 64); sv["cpre"] = torch.zeros(7, 64); sv["npatch"] = 0
        if self.kind == "set":
            V = _tab(self.table)["U"][self.vkey][L].float().to(x.device)
            c = x @ V; tg = self.tgt[ti, L].to(x.device)
            xn = x + (tg - c)[:, None] * V[None]
            out = h.clone(); out[r0:r1] = xn.to(h.dtype)
            post = out[r0:r1].float()
            if self.log:
                sv["disp"][ti, L] = (xn - x).norm(dim=-1).cpu()
                sv["cres"][ti, L] = (post @ V - tg).abs().cpu()
                sv["npatch"] += r1 - r0
        else:
            post = x
        if self.log and self.xkey is not None:
            ref = _tab(self.table)["X"][self.xkey][ti, L - L0].float().to(x.device)
            sv["cum"][ti, L] = (post - ref).norm(dim=-1).cpu()
            sv["cpre"][ti, L] = (x - ref).norm(dim=-1).cpu()
        if self.cap:
            for j in range(r1 - r0):
                sv[f"cap|{lo - self.lo + j}|{L}"] = post[j].detach().to(torch.float16).cpu()
        return out
