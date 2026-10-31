"""sw034 hook (prep agent, E2, 31 Oct 2026). CPU-importable (no CUDA, no lib imports), so test34.py runs it on synthetic blocks.
Copied from sw029 hooks29.Hooks29 (rank-1 clamp with precomputed target coordinates at any position set; A clamp matched to a NAMED
real row in the same forward), with sw031's scale c on the A clamp and two on-manifold kinds:
Forward hooks on blocks[L] (model.model.layers[L] output, pre-final-norm), active only while mode == "patch" and the forward's sequence
length >= min_len (the prefill; decode steps pass through unpatched), at layers 16-63. Every unit has a 'none' row whose live state is
x_none for every row of the unit. Row kinds (x = the row's live state at the op's positions at layer L, after upstream edits):
  none   : unedited.
  sub    : x' = x + (tgt[L] - x . u_L) u_L                                       (coordinate set to the target; sw029)
  A      : x' = x + (x_none . r_L + s * c * Delta(L, p) - x . r_L) r_L, Delta = ||x_arm'(L, p) - x_none(L, p)|| of the matched real row
           (processed earlier in the same forward), so (x_A' - x_none) . r_L = s * c * Delta exactly            (sw028 / sw031)
  full   : x' = D[L] at the 7 header positions (another script's same-condition header state, the recipient model's capture) (sw031 skF)
  mclamp : x'_p = x_p - mean_p(x) + mstar[L] at the Assistant positions (the mean of the turn-1-2 content states set to another
           script's same-condition mean; within-turn variation kept)
Logging (rows with log=True, at log_layers), after every edit at that layer (post bf16 write-back), dir = op['U'][L] (sub: u; A: r;
full / mclamp: the matched arm's u, so 'along' reads how far the control moves along the arm's direction):
  off_h, along_h, coord_h [7] at the row's header positions; tgt_h [7] for header sub rows; ka_h (full: derr_rel = max_t |x'-D|/|D|);
  rows with Assistant positions: off_a (mean ||x' - x_none||), along_a, n_a and ka_a = the known-answer residual there
  (sub: err_max, gap_min; A: err_max, want_min, want_mean; mclamp: err_rel = |mean_p x' - mstar| / |mstar|)."""
import torch

LAYERS_SWAP = frozenset(range(16, 64))
LOG14 = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)


def _r(v, nd=4):
    return [round(float(a), nd) for a in v]


class Hooks34:
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
                pos = op["pos"]; Dl = None
                x = t[r, pos].float()
                if k == "sub":
                    dirv = op["U"][L]; inc = op["tgt"][L] - x @ dirv
                    t[r, pos] = (x + inc[:, None] * dirv[None]).to(t.dtype)
                elif k == "A":
                    dirv = op["U"][L]; m = op["match"]
                    assert m in xreal, "real arm must precede its cumulative-matched clamps in the same forward"
                    assert preal[m] == pos, "an A clamp must edit exactly its arm's positions"
                    xnone = t[rn[op["grp"]], pos].float()
                    Dl = (xreal[m] - xnone).norm(dim=-1)
                    inc = xnone @ dirv + op["s"] * op["c"] * Dl - x @ dirv
                    t[r, pos] = (x + inc[:, None] * dirv[None]).to(t.dtype)
                elif k == "full":
                    t[r, pos] = op["D"][L].to(t.dtype)
                elif k == "mclamp":
                    t[r, pos] = (x - x.mean(0, keepdim=True) + op["mstar"][L][None]).to(t.dtype)
                else:
                    raise ValueError(k)
                if op.get("real"):
                    tag = f"{op['grp']}:{op['arm']}"
                    if tag not in xreal:
                        xreal[tag] = t[r, pos].float(); preal[tag] = pos
                if op.get("log") and L in self.log_layers:
                    logrows.append((r, op, Dl))
            for r, op, Dl in logrows:
                dirv = op["U"][L]; g = rn[op["grp"]]; hp = op["hpos"]; nh = op["nh"]
                xh = t[r, hp].float(); vh = xh - t[g, hp].float()
                e = dict(grp=op["grp"], arm=op["arm"], sample=op["sample"], L=L, row=r,
                         off_h=_r(vh.norm(dim=-1)), along_h=_r(vh @ dirv), coord_h=_r(xh @ dirv))
                if op["kind"] == "sub" and nh == 7:
                    e["tgt_h"] = _r(op["tgt"][L][:7])
                if op["kind"] == "full":
                    D = op["D"][L].float()
                    e["ka_h"] = dict(derr_rel=round(float(((xh - D).norm(dim=-1) / D.norm(dim=-1).clamp_min(1e-6)).max()), 6))
                ap = op["pos"][nh:]
                if ap:
                    xa = t[r, ap].float(); xna = t[g, ap].float(); va = xa - xna
                    e["off_a"] = round(float(va.norm(dim=-1).mean()), 4); e["along_a"] = round(float((va @ dirv).mean()), 4); e["n_a"] = len(ap)
                    if op["kind"] == "sub":
                        tg = op["tgt"][L][nh:]
                        e["ka_a"] = dict(err_max=round(float((xa @ dirv - tg).abs().max()), 5), gap_min=round(float((tg - xna @ dirv).abs().min()), 5))
                    elif op["kind"] == "A":
                        want = op["s"] * op["c"] * Dl[nh:]
                        e["ka_a"] = dict(err_max=round(float((va @ dirv - want).abs().max()), 5), want_min=round(float(want.abs().min()), 5),
                                         want_mean=round(float(want.abs().mean()), 5))
                    elif op["kind"] == "mclamp":
                        ms = op["mstar"][L].float()
                        e["ka_a"] = dict(err_rel=round(float((xa.mean(0) - ms).norm() / ms.norm().clamp_min(1e-6)), 6))
                self.log.append(e)
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


class Cap:
    """read-only capture of the (edited) block outputs at `layers` and given positions per row; register AFTER Hooks34, so it sees
    the edited output (forward hooks chain). Used by the GPU known-answer gate."""
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
    """real rows precede every A row matched to them, within the forward."""
    seen = set()
    for op in ops:
        if op.get("real"):
            seen.add(f"{op['grp']}:{op['arm']}")
        if op["kind"] == "A":
            assert op["match"] in seen, f"{op['arm']} of {op['grp']} precedes its real row {op['match']}"
    return True
