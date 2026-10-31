"""sw037 Part 2 hook = sw031 hooks31.py copied verbatim (class renamed Hooks37b; only the kinds none / full and the cap mode are used).
--- sw031 docstring follows ---
sw031 hook (prep agent, E2, 31 Oct 2026). CPU-importable (no CUDA, no lib imports), so test31.py runs it on synthetic blocks.
Adapted from sw028 hooks28.Hooks28 (kinds none / sub / A; the A clamp gains a scale c) plus sw006/sw007's whole-state 'full'
transplant and a 'cap' mode for the donor capture forward.

Forward hooks on blocks[L] (model.model.layers[L] output, pre-final-norm), L = 0..63; only L in 16..63 is ever touched.
  mode 'cap'  : keep cap[L] = t[:, -7:] (the 7 header tokens of a right-aligned, unpadded batch-1 prefill), every L in 16..63.
  mode 'patch': active only while the forward's sequence length >= min_len (the prefill; decode steps pass through unpatched).
Per row, op['pos'] = the 7 header positions; op['layers'] = the layers where the row is edited. Each group has a 'none' row,
whose live state at this layer is the reference x_none for every row of the group (logging, A clamp).
Row kinds (x = the row's live header state at layer L, after upstream edits; per token t = 0..6):
  none : unedited.
  full : x' = Dfull[:, L - 16] (the donor's whole header state, bf16, captured by a 'cap' forward of the donor model on the
         donor context), at L in op['layers'] (a band). Logs derr = max |x' - D_L| (0 when the assignment is exact).
  sub  : rank-1 coordinate clamp to the donor's (sw009 C4 / sw012 r1):  x' = x + ((D_L - x) . u_L) u_L.  real=True rows (r1)
         record their post-edit state for the A clamps.
  A    : cumulative-offset-matched clamp with scale c (sw028's A, c = 1 there):  x' = x + (c_none + s * c * Delta(L, t) - x . r_L) r_L,
         c_none = x_none . r_L, Delta(L, t) = ||x_r1'(L, t) - x_none(L, t)|| read live from the same forward (r1 row first).
Logging (rows with log=True, at log_layers): off = ||x' - x_none|| [7], nrm = ||x_none|| [7], along = (x' - x_none) . dir_L [7]
(dir = u_L for sub, r_L for A, none for full), inc [7] (0 where the row is not edited at L), derr (full rows at edited layers).
Capture in patch mode: keep = set of layers -> cap[L] = post-edit header states of every row [rows, 7, H] (float)."""
import torch

LAYERS_SWAP = frozenset(range(16, 64))
L0 = 16


class Hooks37b:
    def __init__(self, blocks, log_layers):
        self.mode = None; self.ops = None; self.log = []; self.min_len = 10 ** 9; self.keep = None; self.cap = {}
        self.log_layers = frozenset(log_layers); self.calls = 0
        self.h = [blocks[L].register_forward_hook(self._f(L)) for L in range(len(blocks))]

    def remove(self):
        for h in self.h:
            h.remove()

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if L not in LAYERS_SWAP:
                return None
            if self.mode == "cap":
                self.cap[L] = t[:, -7:].detach().clone()
                return None
            if self.mode != "patch" or t.shape[1] < self.min_len:
                return None
            self.calls += 1
            t = t.clone()
            xn = {}
            for r, op in enumerate(self.ops):
                if op["kind"] == "none" and op["grp"] not in xn:
                    xn[op["grp"]] = t[r, op["pos"]].float()
            xreal, logrows = {}, []
            for r, op in enumerate(self.ops):
                k = op["kind"]
                if k == "none":
                    continue
                pos = op["pos"]; inc = None; dirv = None; derr = None
                edited = L in op["layers"]
                if k == "sub":
                    dirv = op["U"][L].float()
                elif k == "A":
                    dirv = op["R"][L].float()
                if edited:
                    if k == "full":
                        D = op["Dfull"][:, L - L0]
                        t[r, pos] = D.to(t.dtype)
                        if op.get("log") and L in self.log_layers:
                            derr = float((t[r, pos].float() - D.float()).abs().max())
                    else:
                        x = t[r, pos].float()
                        if k == "sub":
                            inc = (op["D"][:, L].float() - x) @ dirv
                        elif k == "A":
                            g = op["grp"]; assert g in xn, "group has no none row in this forward"
                            assert op["match"] in xreal, "real arm must precede its cumulative-matched clamps in the same forward"
                            off = op["s"] * op["c"] * (xreal[op["match"]] - xn[g]).norm(dim=-1)
                            inc = (xn[g] @ dirv + off) - x @ dirv
                        else:
                            raise ValueError(k)
                        t[r, pos] = (x + inc[:, None] * dirv[None]).to(t.dtype)
                if op.get("real"):
                    xreal.setdefault(f"{op['grp']}:{op['arm']}", t[r, pos].float())
                if op.get("log") and L in self.log_layers:
                    logrows.append((r, op, inc, dirv, derr))
            for r, op, inc, dirv, derr in logrows:
                g = op["grp"]; v = t[r, op["pos"]].float() - xn[g]
                e = dict(grp=g, arm=op["cell"], sample=op["sample"], L=L, row=r,
                         off=[round(float(a), 4) for a in v.norm(dim=-1)], nrm=[round(float(a), 3) for a in xn[g].norm(dim=-1)],
                         along=[round(float(a), 4) for a in v @ dirv] if dirv is not None else None,
                         inc=[round(float(a), 4) for a in inc] if inc is not None else [0.0] * len(op["pos"]))
                if derr is not None:
                    e["derr"] = derr
                self.log.append(e)
            if self.keep is not None and L in self.keep:
                pos0 = self.ops[0]["pos"]
                assert all(op["pos"] == pos0 for op in self.ops), "capture assumes one header position set per forward"
                self.cap[L] = t[:, pos0].detach().float().clone()
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


def check_order(ops):
    """every group has a none row; real rows precede every A row matched to them, within the forward."""
    seen = set(); grps_none = {op["grp"] for op in ops if op["kind"] == "none"}
    for op in ops:
        assert op["grp"] in grps_none, f"group {op['grp']} has no none row"
        if op.get("real"):
            seen.add(f"{op['grp']}:{op['arm']}")
        if op["kind"] == "A":
            assert op["match"] in seen, f"{op['arm']} of {op['grp']} precedes its real row {op['match']}"
    return True
