"""sw081 hook = sw038 hooks38p1.Hooks38 with one change: a 'full' row (P0) may be a REAL row, so A clamps can be matched to its live
per-token offset (Delta = ||x_P0' - x_none|| at the header, after the bf16 write-back). CPU-importable (tests81 runs it on a tiny model).
Forward hooks on blocks[L] (block output, pre-final-norm), active only while mode == "patch" and the forward's length >= min_len
(prefill), at layers 16-63. Row kinds (x = the row's live state at the op's positions at layer L, after upstream edits):
  none : unedited.
  sub  : x' = x + (tgt[L] - x . u_L) u_L                    (asT / asTp at the Assistant's turn-1-2 content tokens)
  A    : x' = x + (x_none . r_L + s * k_L * Delta(L, p) - x . r_L) r_L, Delta = ||x_arm'(L, p) - x_none(L, p)|| of the matched real row
  full : x' = Dfull[:, L - 16] at the 7 header positions (P0; bf16 assignment, exact).
Logged per row (log=True, at log_layers): off_h / along_h / coord_h [7] at the header; full rows off_h + derr; rows with Assistant
positions: off_a, along_a, ka_a (sub: err_max, gap_min; A: err_max, want_min, want_mean)."""
import torch

LAYERS_SWAP = frozenset(range(16, 64))
LOG14 = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)


def _r(v, nd=4):
    return [round(float(a), nd) for a in v]


class Hooks81:
    def __init__(self, blocks, log_layers=LOG14):
        self.mode = None; self.ops = None; self.log = []; self.min_len = 10 ** 9
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
            rn = {}
            for r, op in enumerate(self.ops):
                if op["kind"] == "none":
                    rn.setdefault(op["grp"], r)
            xreal, preal, logrows = {}, {}, []
            for r, op in enumerate(self.ops):
                k = op["kind"]
                if k == "none":
                    continue
                pos = op["pos"]; Dl = None; derr = None
                if k == "full":
                    D = op["Dfull"][:, L - 16]
                    t[r, pos] = D.to(t.dtype)
                    if op.get("real"):
                        tag = f"{op['grp']}:{op['arm']}"
                        if tag not in xreal:
                            xreal[tag] = t[r, pos].float(); preal[tag] = pos
                    if op.get("log") and L in self.log_layers:
                        derr = float((t[r, pos].float() - D.float()).abs().max())
                        logrows.append((r, op, None, derr))
                    continue
                dirv = op["U"][L]
                x = t[r, pos].float()
                if k == "sub":
                    inc = op["tgt"][L] - x @ dirv
                elif k == "A":
                    m = op["match"]
                    assert m in xreal, "real arm must precede its cumulative-matched clamps in the same forward"
                    assert preal[m] == pos, "an A clamp must edit exactly its arm's positions"
                    xnone = t[rn[op["grp"]], pos].float()
                    Dl = (xreal[m] - xnone).norm(dim=-1)
                    inc = xnone @ dirv + op["s"] * op["k"][L] * Dl - x @ dirv
                else:
                    raise ValueError(k)
                t[r, pos] = (x + inc[:, None] * dirv[None]).to(t.dtype)
                if op.get("real"):
                    tag = f"{op['grp']}:{op['arm']}"
                    if tag not in xreal:
                        xreal[tag] = t[r, pos].float(); preal[tag] = pos
                if op.get("log") and L in self.log_layers:
                    logrows.append((r, op, Dl, None))
            for r, op, Dl, derr in logrows:
                g = rn[op["grp"]]; hp = op["hpos"]
                xh = t[r, hp].float(); vh = xh - t[g, hp].float()
                e = dict(grp=op["grp"], arm=op["arm"], sample=op["sample"], L=L, row=r, off_h=_r(vh.norm(dim=-1)))
                if op["kind"] == "full":
                    e["derr"] = derr
                    self.log.append(e); continue
                dirv = op["U"][L]; nh = op["nh"]
                e.update(along_h=_r(vh @ dirv), coord_h=_r(xh @ dirv))
                ap = op["pos"][nh:]
                if ap:
                    xa = t[r, ap].float(); xna = t[g, ap].float(); va = xa - xna
                    e["off_a"] = round(float(va.norm(dim=-1).mean()), 4); e["along_a"] = round(float((va @ dirv).mean()), 4); e["n_a"] = len(ap)
                    if op["kind"] == "sub":
                        tg = op["tgt"][L][nh:]
                        e["ka_a"] = dict(err_max=round(float((xa @ dirv - tg).abs().max()), 5), gap_min=round(float((tg - xna @ dirv).abs().min()), 5))
                    else:
                        want = op["s"] * op["k"][L] * Dl[nh:]
                        e["ka_a"] = dict(err_max=round(float((va @ dirv - want).abs().max()), 5), want_min=round(float(want.abs().min()), 5),
                                         want_mean=round(float(want.abs().mean()), 5))
                self.log.append(e)
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


class Cap:
    """read-only capture of the (edited) block outputs at `layers` and given positions per row; register AFTER Hooks81."""
    def __init__(self, blocks, layers):
        self.on = False; self.pos_rows = None; self.cap = {}; self.min_len = 10 ** 9
        self.h = [blocks[L].register_forward_hook(self._f(L)) for L in layers]

    def remove(self):
        for h in self.h:
            h.remove()

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.on and t.shape[1] >= self.min_len:
                self.cap[L] = [t[r, p].detach().float().cpu() for r, p in enumerate(self.pos_rows)]
            return None
        return f


def check_order(ops):
    seen = set(); has_none = {op["grp"] for op in ops if op["kind"] == "none"}
    for op in ops:
        assert op["grp"] in has_none, f"unit {op['grp']} has no none row"
        if op.get("real"):
            seen.add(f"{op['grp']}:{op['arm']}")
        if op["kind"] == "A":
            assert op["match"] in seen, f"{op['arm']} of {op['grp']} precedes its real row {op['match']}"
    return True
