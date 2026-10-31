"""sw030 whole-state block swap hook (CPU-importable; no CUDA needed). Forward hooks on blocks[L] = model.model.layers[L]
(decoder-block output = residual stream entering block L+1, pre-final-norm; the 018 / acts convention).

A swap op = (rec_row, rec_pos, don_row, don_pos, L): at every layer l >= L the recipient row's residual state at rec_pos is replaced,
all 5,120 dimensions, by the donor row's state at don_pos in the SAME forward (the donor row is an unedited row of the donor context,
placed before the recipients in the batch). Layer l's output is overwritten after block l ran, so block l+1 and every later block
read the donor's state at those positions; positions after the block read it through attention / the GatedDeltaNet recurrence.

The hook is active only in mode "patch" and only on the forward whose sequence length equals the padded prompt length P (the
prefill of generate(), or a plain teacher-forced forward); the 1-token decode steps pass through unpatched (D5). Per layer it
counts calls and patched (row, position) pairs so the job can assert that the prefill fired exactly once at all 64 layers with the
expected number of edits (no silent no-op). Optional capture: keep = {layer: None (all positions) | int k (last k positions)} ->
cap[layer] = post-edit states of every row (detached clone, model dtype)."""
import torch


def build_plan(ops, n_layers, device="cpu"):
    """ops: dicts with rec_row, don_row, rec_pos, don_pos (padded indices), L. -> list over layers of (rr, rp, dr, dp) or None."""
    recs = [o["rec_row"] for o in ops]
    assert len(set(recs)) == len(recs), "a recipient row carries one op"
    assert not (set(recs) & {o["don_row"] for o in ops}), "a donor row must never be edited"
    for o in ops:
        assert len(o["rec_pos"]) == len(o["don_pos"]) > 0 and len(set(o["rec_pos"])) == len(o["rec_pos"])
        assert 0 <= o["L"] < n_layers
    plan, expect = [], []
    for l in range(n_layers):
        rr, rp, dr, dp = [], [], [], []
        for o in ops:
            if o["L"] <= l:
                rr += [o["rec_row"]] * len(o["rec_pos"]); rp += list(o["rec_pos"])
                dr += [o["don_row"]] * len(o["don_pos"]); dp += list(o["don_pos"])
        expect.append(len(rr))
        plan.append(None if not rr else tuple(torch.tensor(x, dtype=torch.long, device=device) for x in (rr, rp, dr, dp)))
    return plan, expect


class SwapHook:
    def __init__(self, blocks):
        self.n = len(blocks); self.mode = None; self.P = None; self.plan = None; self.keep = None; self.cap = {}
        self.calls = [0] * self.n; self.npatched = [0] * self.n; self.other_calls = 0
        self.h = [blocks[L].register_forward_hook(self._f(L)) for L in range(self.n)]

    def arm(self, plan, P, keep=None):
        assert len(plan) == self.n
        self.plan, self.P, self.keep, self.cap = plan, P, keep, {}
        self.calls = [0] * self.n; self.npatched = [0] * self.n; self.other_calls = 0; self.mode = "patch"

    def disarm(self):
        self.mode = None; self.plan = None; self.keep = None

    def remove(self):
        for h in self.h:
            h.remove()

    def _f(self, L):
        def f(mod, inp, out):
            if self.mode != "patch":
                return None
            t = out[0] if isinstance(out, tuple) else out
            if t.shape[1] != self.P:          # decode step (1 token): unpatched
                self.other_calls += 1
                return None
            self.calls[L] += 1
            ix = self.plan[L]
            if ix is not None:
                rr, rp, dr, dp = ix
                t = t.clone()
                t[rr, rp] = t[dr, dp]         # gather (donor rows are never edited) then scatter
                self.npatched[L] += int(rr.numel())
            if self.keep is not None and L in self.keep:
                k = self.keep[L]
                self.cap[L] = (t if k is None else t[:, -k:]).detach().clone()
            if ix is None:
                return None
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f
