"""sw033 T5 whole-state transplant hook (CPU-importable; torch only). Adapted from sw030 hook30.SwapHook (forward hooks on
blocks[L] = model.model.layers[L]; decoder-block output = residual stream entering block L+1, pre-final-norm) with sw031's stored-donor
('full') assignment instead of an in-batch donor row.

mode 'cap'  : on any forward, cap[L] = t[:, -k:] (detached clone) for every L; used on unpadded batch-1 T0 donor forwards (k = 2).
mode 'patch': only on the forward whose sequence length equals the padded prompt length P (the prefill of generate(), or a teacher-
              forced forward of the same batch); 1-token decode steps pass through unpatched. At EVERY layer L = 0..63 the rows in
              `rows` get t[row, pos[row]] = donor[row][L] (all 5,120 dims), in place, after block L ran: block L+1 and every later
              block read T0's state at those positions; later positions read it through attention / the GatedDeltaNet recurrence.
              Counts calls and patched (row, position) pairs per layer (the job asserts exactly one prefill call per layer and the
              planned count: no silent no-op). Optional keep = {L: positions list | None} -> cap[L] = post-edit states [rows, |pos|, H]."""
import torch


class Hook33:
    def __init__(self, blocks):
        self.n = len(blocks); self.mode = None; self.P = None; self.k = None
        self.rows = None; self.pos = None; self.don = None; self.keep = None; self.cap = {}
        self.calls = [0] * self.n; self.npatched = [0] * self.n; self.other_calls = 0
        self.h = [blocks[L].register_forward_hook(self._f(L)) for L in range(self.n)]

    def arm_cap(self, k):
        self.mode, self.k, self.cap = "cap", k, {}
        self.calls = [0] * self.n

    def arm_patch(self, P, rows, pos, don, keep=None):
        """rows: LongTensor [n]; pos: LongTensor [n, k] padded positions; don: tensor [n, n_layers, k, H] (model dtype, same device)."""
        assert rows is None or (pos.shape[0] == rows.shape[0] == don.shape[0] and don.shape[1] == self.n and don.shape[2] == pos.shape[1])
        self.mode, self.P, self.rows, self.pos, self.don, self.keep, self.cap = "patch", P, rows, pos, don, keep, {}
        self.calls = [0] * self.n; self.npatched = [0] * self.n; self.other_calls = 0

    def disarm(self):
        self.mode = None; self.rows = self.pos = self.don = None; self.keep = None

    def remove(self):
        for h in self.h:
            h.remove()

    def _f(self, L):
        def f(mod, inp, out):
            if self.mode is None:
                return None
            t = out[0] if isinstance(out, tuple) else out
            if self.mode == "cap":
                self.calls[L] += 1
                self.cap[L] = t[:, -self.k:].detach().clone()
                return None
            if t.shape[1] != self.P:          # decode step: unpatched
                self.other_calls += 1
                return None
            self.calls[L] += 1
            if self.rows is not None and self.rows.numel():
                r = self.rows[:, None].expand_as(self.pos)
                t[r, self.pos] = self.don[:, L].to(t.dtype)       # in place (no_grad); the returned object is unchanged
                self.npatched[L] += int(self.pos.numel())
            if self.keep is not None and L in self.keep:
                p = self.keep[L]
                self.cap[L] = (t if p is None else t[:, p]).detach().clone()
            return None
        return f
