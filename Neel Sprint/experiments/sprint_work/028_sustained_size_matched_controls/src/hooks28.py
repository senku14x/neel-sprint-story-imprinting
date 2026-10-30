"""sw028 hook (executor-9 overnight, 30 Oct 2026). CPU-importable (no CUDA, no lib imports), so test28_x.py can run it on
synthetic blocks. Adapted from sw012 gen12_x.Hooks12 (= sw009 Hooks9 with group-keyed realised matching).

Forward hooks on blocks[L] (model.model.layers[L] output, pre-final-norm). Active only while mode == "patch" and the forward's
sequence length >= min_len (the prefill; decode steps are 1 token and pass through unpatched). Per row, op["pos"] = the 7
header positions; op["layers"] = the layers where the row is edited (default 16-63). Each group (model|direction|script) has
a 'none' row, whose live state at this layer is the reference x_none for every row of the group.

Row kinds (x = the row's live header state at layer L, after upstream edits; all per token, t = 0..6):
  none : unedited.
  sub  : rank-1 coordinate clamp to the donor's (sw009 C4 / sw012 r1):  x' = x + ((D_L - x) . u_L) u_L.
         real=True rows (r1; d16 in the L16-only test) record their per-token push |(D_L - x) . u_L| and their post-edit state.
  P    : persistent-sign R7 push (new):  x' = x + sigma_t * n_real(L, t) * r_L, with n_real = the real row's push norm at the same
         layer and token in the same forward (R7 realised matching), and sigma_t the R7 'toward the donor' sign at L16, fixed
         for every later layer. (sw012's R7 recomputed the sign from the live state at each layer, so its pushes after L16
         undo the first one; cumctrl/ D29.)
  A    : cumulative-offset-matched clamp (new):  x' = x + (c_none + s * Delta(L, t) - x . r_L) r_L, with c_none = x_none . r_L
         and Delta(L, t) = ||x_r1'(L, t) - x_none(L, t)||, the real row's total post-edit offset from the none row at this layer
         and token, read live from the same forward (the r1 row is processed first). s = one sign per script.
         So (x_A' - x_none) . r_L = s * Delta exactly, and ||x_A' - x_none|| >= Delta at every patched layer.
  Z    : natural-scale clamp (new):  x' = x + (c_none + s * zoff(L, t) - x . r_L) r_L, zoff = (gap_u / sd_u) * sd_r precomputed.
Logging (rows with log=True, at log_layers): off = ||x' - x_none|| [7], along = (x' - x_none) . dir_L [7] (dir = u_L for sub
rows, r_L otherwise), inc = the signed increment along dir at this layer [7] (0 where the row is not edited at L).
Capture: keep = set of layers -> cap[L] = the post-edit header states of every row [rows, 7, H] (float, on the device)."""
import torch

LAYERS_SWAP = frozenset(range(16, 64))
LOG14 = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)


class Hooks28:
    def __init__(self, blocks, log_layers=LOG14):
        self.mode = None; self.ops = None; self.log = []; self.min_len = 10 ** 9; self.keep = None; self.cap = {}
        self.log_layers = frozenset(log_layers); self.calls = 0
        self.h = [blocks[L].register_forward_hook(self._f(L)) for L in range(len(blocks))]

    def remove(self):
        for h in self.h:
            h.remove()

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.mode != "patch" or t.shape[1] < self.min_len or L not in LAYERS_SWAP:
                return None
            self.calls += 1
            t = t.clone()
            xn = {}
            for r, op in enumerate(self.ops):
                if op["kind"] == "none" and op["grp"] not in xn:
                    xn[op["grp"]] = t[r, op["pos"]].float()
            realnorm, xreal, logrows = {}, {}, []
            for r, op in enumerate(self.ops):
                k = op["kind"]
                if k == "none":
                    continue
                pos = op["pos"]; inc = None
                dirv = (op["U"] if k == "sub" else op["R"])[L].float()          # [H] unit
                if L in op.get("layers", LAYERS_SWAP):
                    x = t[r, pos].float()
                    if k == "sub":
                        c = (op["D"][:, L].float() - x) @ dirv                 # [7]
                        inc = c
                    elif k == "P":
                        assert op["match"] in realnorm, "real arm must precede its matched controls in the same forward"
                        inc = op["sigma"].to(x) * realnorm[op["match"]]
                    elif k in ("A", "Z"):
                        g = op["grp"]; assert g in xn, "group has no none row in this forward"
                        if k == "A":
                            assert op["match"] in xreal, "real arm must precede its cumulative-matched clamps in the same forward"
                            off = op["s"] * (xreal[op["match"]] - xn[g]).norm(dim=-1)
                        else:
                            off = op["s"] * op["zoff"][L].to(x)
                        inc = (xn[g] @ dirv + off) - x @ dirv
                    else:
                        raise ValueError(k)
                    t[r, pos] = (x + inc[:, None] * dirv[None]).to(t.dtype)
                if op.get("real"):
                    tag = f"{op['grp']}:{op['arm']}"
                    realnorm.setdefault(tag, inc.abs() if inc is not None else torch.zeros(len(pos), device=t.device))
                    xreal.setdefault(tag, t[r, pos].float())
                if op.get("log") and L in self.log_layers:
                    logrows.append((r, op, inc, dirv))
            for r, op, inc, dirv in logrows:
                v = t[r, op["pos"]].float() - xn[op["grp"]]
                self.log.append(dict(grp=op["grp"], arm=op["arm"], sample=op["sample"], L=L, row=r,
                                     off=[round(float(a), 4) for a in v.norm(dim=-1)],
                                     along=[round(float(a), 4) for a in v @ dirv],
                                     inc=[round(float(a), 4) for a in inc] if inc is not None else [0.0] * len(op["pos"])))
            if self.keep is not None and L in self.keep:
                pos0 = self.ops[0]["pos"]
                assert all(op["pos"] == pos0 for op in self.ops), "capture assumes one header position set per forward"
                self.cap[L] = t[:, pos0].detach().float().clone()
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


def check_order(ops):
    """real rows precede every row matched to them (P: realnorm; A: post-edit state), within the forward."""
    seen = set()
    for op in ops:
        if op.get("real"):
            seen.add(f"{op['grp']}:{op['arm']}")
        if op["kind"] in ("P", "A"):
            assert op["match"] in seen, f"{op['arm']} of {op['grp']} precedes its real row {op['match']}"
    return True
