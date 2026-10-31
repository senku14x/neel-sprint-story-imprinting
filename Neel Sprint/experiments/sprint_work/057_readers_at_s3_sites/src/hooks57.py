"""sw057 hook (c1 step 2 swaps and the conditional latent clamp). CPU-importable (no CUDA, no lib imports), so test57.py runs it on
a fake model. Copied from sw029 hooks29.py (same rank-1 coordinate set, same cumulative-offset A clamp, same logging) with two
generalisations, both needed by sw057's design:
  1. every real (edited) row carries its own layer set op["layers"] (asT full band L16-63, L42 only, L36-48); the hook still runs
     at L16-63 (A clamps read their arm's live offset at every layer, so an A matched to an L42-only arm clamps 0 below L42 and the
     propagated offset above it: sw028's cumulative matching);
  2. op kind "sae": sae1029 Part 3's latent clamp (edit_hooks_x.delta, copied verbatim below as sae_delta), at its layer set (L42),
     with arm kinds shared (top latents clamped to targets), rand<i> (frequency-matched random latents clamped, rescaled per token
     to the shared clamp's displacement norm on the same state), dense_match (dense direction at that norm), dense_1x (dense
     difference at natural size). Targets are per row (the donor's mean per-token activation of each latent), not per cell.
Hooks on blocks[L] (model.model.layers[L] output, pre-final-norm), active only while mode == "patch" and the forward's sequence
length >= min_len (the prefill), at L16-63.
Row kinds (x = the row's live state at the op's positions at layer L, after upstream edits):
  none : unedited (its live state is x_none for every row of its unit).
  sub  : at L in op["layers"]: x' = x + (tgt[L] - x . u_L) u_L;  elsewhere untouched.
  A    : x' = x + (x_none . r_L + s * Delta(L, p) - x . r_L) r_L, Delta = ||x_arm'(L, p) - x_none(L, p)|| of the matched real row
         (processed earlier in the same forward) at EVERY hooked layer, so (x_A' - x_none) . r_L = s * Delta exactly.
  sae  : at L in op["layers"]: x' = x + sae_delta(spec, arm_kind, x, targets).
Logging (rows with log=True, at log_layers): off_h / along_h / coord_h at the 7 header positions; for rows with own-turn positions
off_a (mean ||x' - x_none||), along_a, n_a and ka_a known-answer residuals (sub: err_max / gap_min, only at the row's layers; A:
err_max / want_min / want_mean); sae rows: dnorm_a (mean ||delta|| over positions at the edit layer) and edited=1 at edit layers."""
import torch

LAYERS_SWAP = frozenset(range(16, 64))
LOG14 = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)


def _r(v, nd=4):
    return [round(float(a), nd) for a in v]


# ------------------------------------------------------------------------------------------------- sae1029 delta (verbatim logic)
def sae_delta(Sm, arm, x, tgt):
    """sae1029 part3 edit_hooks_x.delta with the per-cell target replaced by a per-row target vector over Sm's latent list.
    x [r, H] fp32 states at the edited tokens -> displacement [r, H] fp32.
    Sm: W_enc [n, H] rows, b_enc [n], D [H, n] columns, b_dec [H], thr (float), shared_t (indices into the n latents),
        rand_t (list of index tensors), dense [H] (per row: the dense mean state difference toward the target).
    tgt: [n] target activation per listed latent (the donor's mean per-token code)."""
    def clamp(idx):
        a = torch.relu((x - Sm["b_dec"]) @ Sm["W_enc"][idx].T + Sm["b_enc"][idx])
        a = a * (a > Sm["thr"])
        return (tgt[idx][None] - a) @ Sm["D"][:, idx].T

    if arm == "shared":
        return clamp(Sm["shared_t"])
    rn = clamp(Sm["shared_t"]).norm(dim=-1, keepdim=True)
    if arm.startswith("rand"):
        d = clamp(Sm["rand_t"][int(arm[4:])])
        return d / d.norm(dim=-1, keepdim=True).clamp_min(1e-6) * rn
    v = Sm["dense"]
    if arm == "dense_match":
        return (v / v.norm())[None] * rn
    if arm == "dense_1x":
        return v[None].expand(x.shape[0], -1)
    raise ValueError(arm)


class Hooks57:
    def __init__(self, blocks, log_layers=LOG14):
        self.mode = None; self.ops = None; self.log = []; self.min_len = 10 ** 9
        self.log_layers = frozenset(log_layers); self.calls = 0; self.edit_calls = {}
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
                pos = op["pos"]; Dl = None; dn = None
                x = t[r, pos].float()
                if k == "sub":
                    if L in op["layers"]:
                        dirv = op["U"][L]
                        inc = op["tgt"][L] - x @ dirv
                        t[r, pos] = (x + inc[:, None] * dirv[None]).to(t.dtype)
                        self.edit_calls[op["arm"]] = self.edit_calls.get(op["arm"], 0) + 1
                elif k == "sae":
                    if L in op["layers"]:
                        dl = sae_delta(op["Sm"], op["arm_kind"], x, op["tgt_lat"])
                        dn = dl.norm(dim=-1)
                        t[r, pos] = (x + dl).to(t.dtype)
                        self.edit_calls[op["arm"]] = self.edit_calls.get(op["arm"], 0) + 1
                elif k == "A":
                    dirv = op["U"][L]
                    m = op["match"]
                    assert m in xreal, "real arm must precede its cumulative-matched clamps in the same forward"
                    assert preal[m] == pos, "an A clamp must edit exactly its arm's positions"
                    xnone = t[rn[op["grp"]], pos].float()
                    Dl = (xreal[m] - xnone).norm(dim=-1)
                    inc = xnone @ dirv + op["s"] * Dl - x @ dirv
                    t[r, pos] = (x + inc[:, None] * dirv[None]).to(t.dtype)
                else:
                    raise ValueError(k)
                if op.get("real"):
                    tag = f"{op['grp']}:{op['arm']}"
                    if tag not in xreal:
                        xreal[tag] = t[r, pos].float(); preal[tag] = pos
                if op.get("log") and L in self.log_layers:
                    logrows.append((r, op, Dl, dn))
            for r, op, Dl, dn in logrows:
                dirv = op["U"][L] if op.get("U") is not None else None
                g = rn[op["grp"]]; hp = op["hpos"]; nh = op["nh"]
                xh = t[r, hp].float(); vh = xh - t[g, hp].float()
                e = dict(grp=op["grp"], arm=op["arm"], sample=op["sample"], L=L, row=r, off_h=_r(vh.norm(dim=-1)))
                if dirv is not None:
                    e["along_h"] = _r(vh @ dirv); e["coord_h"] = _r(xh @ dirv)
                ap = op["pos"][nh:]
                if ap:
                    xa = t[r, ap].float(); xna = t[g, ap].float(); va = xa - xna
                    e["off_a"] = round(float(va.norm(dim=-1).mean()), 4); e["n_a"] = len(ap)
                    if dirv is not None:
                        e["along_a"] = round(float((va @ dirv).mean()), 4)
                    if op["kind"] == "sub" and L in op["layers"]:
                        tg = op["tgt"][L][nh:]
                        e["ka_a"] = dict(err_max=round(float((xa @ dirv - tg).abs().max()), 5), gap_min=round(float((tg - xna @ dirv).abs().min()), 5))
                    elif op["kind"] == "A":
                        want = op["s"] * Dl[nh:]
                        e["ka_a"] = dict(err_max=round(float((va @ dirv - want).abs().max()), 5), want_min=round(float(want.abs().min()), 5),
                                         want_mean=round(float(want.abs().mean()), 5))
                    elif op["kind"] == "sae" and dn is not None:
                        e["dnorm_a"] = round(float(dn[nh:].mean()), 5); e["edited"] = 1
                self.log.append(e)
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


class Cap:
    """read-only capture of the (edited) block outputs at `layers` and given positions per row; register AFTER Hooks57 (forward hooks
    chain), so it sees the edited output. pos_rows: list (per batch row) of position lists."""
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
    seen = set()
    for op in ops:
        if op.get("real"):
            seen.add(f"{op['grp']}:{op['arm']}")
        if op["kind"] == "A":
            assert op["match"] in seen, f"{op['arm']} of {op['grp']} precedes its real row {op['match']}"
    return True
