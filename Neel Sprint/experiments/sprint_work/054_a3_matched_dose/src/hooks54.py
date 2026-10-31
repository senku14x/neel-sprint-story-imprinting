"""sw054 edit hook (E1 sw054 prep agent, 30 Oct 2026). CPU-importable (torch only), so test54_x.py runs it on a fake model.
Adapted from sw016 gen16_x.Hooks16 (sub = sw016's rank-1 coordinate swap) and sw028 hooks28.Hooks28 (A = cumulative-offset-
matched clamp, live x_none reference, real row first).

Forward hooks on blocks[L] (model.model.layers[L] output, pre-final-norm), active only while mode == "patch" and the forward's
sequence length >= min_len (the prefill; decode steps are 1 token and pass through unpatched), at layers 16-63. Every group
(one recipient story x readout, or one chat script x direction x bridge) has its 'none' row(s) in every forward; the live
state at the group's positions is x_none for every row of the group (with 2 samples the first none row; the samples' prefill
states are identical). All rows of a group share op["pos"].

Row kinds (x = the row's live state at layer L after upstream edits; per position p; all directions unit fp32 [64, H]):
  none : unedited.
  sub  : rank-1 swap (sw016 r1 / sdir / rchat / rstory):  x' = x + ((D_L - x) . u_L) u_L   (coordinate set to the target's)
  subx : rescaled swap (r1x / rstory_x):  sigma = sign((D_L - x_none) . u_L) per position (r1's own sign rule: r1 moves the
         coordinate from x_none's by (D_L - x_none) . u_L), then the coordinate is clamped to  x_none . u_L + sigma * g[p, L],
         g = the per-position, per-layer dose (prep54 / gen54 doses). So (x' - x_none) . u_L = sigma * g exactly.
         A gate-only variant with g = 0 (arm '*0') measures the clamp's rounding noise (the KA tolerance's noise floor).
  A    : cumulative-offset-matched clamp (sw028):  x' = x + (x_none . r_L + s * Delta(L, p) - x . r_L) r_L, Delta = ||x_real' -
         x_none|| (the matched real row's post-edit offset at this layer and position, read live in the same forward; the real
         row is processed first). s = one sign per (group, direction): sign(mean_p (D_16 - x_none_16) . r_16), computed at the
         first patched layer (L16, where x_none is the unedited state) and kept for every later layer (sw028's s_A).
Logging (rows with log=True, at log_layers): off = ||x' - x_none|| per position, along = (x' - x_none) . dir_L, tgt = the intended
along (sub: (D_L - x_none) . u_L; subx: sigma * g; A: s * Delta), inc = the signed increment along dir at this layer; off and along
are read back from the written (bf16) tensor, so |along - tgt| is the edit's realised error; subx rows also log g, A rows Delta.
Capture: keep = set of layers -> cap[L] = {row: post-edit states at its positions} (float)."""
import torch

LAYERS_SWAP = frozenset(range(16, 64))
LOG14 = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)
L_FIRST = 16


class Hooks54:
    def __init__(self, blocks, log_layers=LOG14):
        self.mode = None; self.ops = None; self.log = []; self.min_len = 10 ** 9; self.keep = None; self.cap = {}
        self.cap_pos = None; self.log_layers = frozenset(log_layers); self.calls = 0
        self.h = [blocks[L].register_forward_hook(self._f(L)) for L in range(len(blocks))]

    def remove(self):
        for h in self.h:
            h.remove()

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.mode == "cap":  # plain state capture of row 0 (gates / dose stage)
                self.cap[L] = t[0, self.cap_pos].detach().float().cpu()
                return None
            if self.mode != "patch" or t.shape[1] < self.min_len or L not in LAYERS_SWAP:
                return None
            self.calls += 1
            t = t.clone()
            xn = {}
            for r, op in enumerate(self.ops):
                if op["kind"] == "none" and op["grp"] not in xn:  # the group's first none row (sample 0) is x_none (sw028)
                    xn[op["grp"]] = t[r, op["pos"]].float()
            xreal, logrows = {}, []
            for r, op in enumerate(self.ops):
                k = op["kind"]
                if k == "none":
                    continue
                g = op["grp"]; assert g in xn, f"group {g} has no none row in this forward"
                pos = op["pos"]; x = t[r, pos].float(); x0 = xn[g]
                delta = None
                if k in ("sub", "subx"):
                    u = op["U"][L].float()
                    gap0 = (op["D"][:, L].float() - x0) @ u          # the target's offset from x_none along u
                    if k == "sub":
                        inc = (op["D"][:, L].float() - x) @ u; tgt = gap0
                    else:
                        tgt = torch.where(gap0 >= 0, 1.0, -1.0) * op["g"][:, L].to(x)
                        inc = (x0 @ u + tgt) - x @ u
                    dirv = u
                elif k == "A":
                    dirv = op["R"][L].float()
                    if L == L_FIRST:
                        op["_s"] = 1.0 if float(((op["D"][:, L].float() - x0) @ dirv).mean()) >= 0 else -1.0
                    assert "_s" in op, "A sign is set at the first patched layer"
                    assert op["match"] in xreal, "real arm must precede its cumulative-matched clamps in the same forward"
                    delta = (xreal[op["match"]] - x0).norm(dim=-1)
                    tgt = op["_s"] * delta
                    inc = (x0 @ dirv + tgt) - x @ dirv
                else:
                    raise ValueError(k)
                t[r, pos] = (x + inc[:, None] * dirv[None]).to(t.dtype)
                if op.get("real"):
                    xreal.setdefault(f"{g}:{op['arm']}", t[r, pos].float())
                if op.get("log") and L in self.log_layers:
                    logrows.append((r, op, inc, dirv, delta, tgt))
            for r, op, inc, dirv, delta, tgt in logrows:
                v = t[r, op["pos"]].float() - xn[op["grp"]]
                e = dict(grp=op["grp"], arm=op["arm"], sample=op["sample"], L=L, row=r,
                         off=[round(float(a), 4) for a in v.norm(dim=-1)], along=[round(float(a), 4) for a in v @ dirv],
                         tgt=[round(float(a), 4) for a in tgt],
                         inc=[round(float(a), 4) for a in inc], xnorm=[round(float(a), 2) for a in xn[op["grp"]].norm(dim=-1)])
                if op["kind"] == "subx":
                    e["g"] = [round(float(a), 4) for a in op["g"][:, L]]
                if op["kind"] == "A":
                    e["delta"] = [round(float(a), 4) for a in delta]; e["s"] = op["_s"]
                self.log.append(e)
            if self.keep is not None and L in self.keep:
                self.cap[L] = {r: t[r, op["pos"]].detach().float().cpu() for r, op in enumerate(self.ops)}
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


def check_order(ops):
    """every group has a none row; every row of a group shares its positions; real rows precede their A clamps."""
    seen, nones, pos = set(), {}, {}
    for op in ops:
        g = op["grp"]
        if op["kind"] == "none":
            nones[g] = True
        if "pos" in op:
            pos.setdefault(g, op["pos"]); assert op["pos"] == pos[g], f"positions differ inside group {g}"
        if op.get("real"):
            seen.add(f"{g}:{op['arm']}")
        if op["kind"] == "A":
            assert op["match"] in seen, f"{op['arm']} of {g} precedes its real row {op['match']}"
    assert set(nones) == {op["grp"] for op in ops}, "a group lacks its none row"
    return True
