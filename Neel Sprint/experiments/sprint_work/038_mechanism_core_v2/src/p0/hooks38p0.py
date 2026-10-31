"""sw038 Part 0 hooks (prep-P0 agent, E2, 31 Oct 2026). CPU-importable (no CUDA needed), so test38p0.py runs them on synthetic
blocks. Adapted from sw006 hf_x.Hooks (the 'full' whole-state swap: t[r, pos] = D[:, L]) with sw029 hooks29's conventions
(prefill only via min_len, edits only at layers 16-63, a call counter, a read-only Cap registered AFTER the edit hooks).

Hooks38 on blocks[L] (model.model.layers[L] output, pre-final-norm), every L:
  mode 'cap'   : read-only; stores t[:, cap_pos] (the batch's rows at the given positions) per layer.
  mode 'patch' : active only while the forward's sequence length >= min_len (the prefill; decode steps pass through) and
                 L in LAYERS_SWAP (16-63). Rows (ops, one per batch row): kind 'none' (untouched) or 'full' (layers = the arm's
                 layer set, pos = the row's 7 header positions, D = [7, 64, H] donor states):  t[r, pos] = D[:, L] if L in layers.
Cap: read-only capture of the (edited) block outputs at `layers` and per-row position lists (register AFTER Hooks38)."""
import torch

from common38p0 import LAYERS_SWAP


class Hooks38:
    def __init__(self, blocks):
        self.mode = None; self.ops = None; self.min_len = 10 ** 9; self.calls = 0
        self.cap = {}; self.cap_pos = None
        self.h = [blocks[L].register_forward_hook(self._f(L)) for L in range(len(blocks))]

    def remove(self):
        for h in self.h:
            h.remove()

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.mode == "cap":
                self.cap[L] = t[:, self.cap_pos].detach()
                return None
            if self.mode != "patch" or t.shape[1] < self.min_len or L not in LAYERS_SWAP:
                return None
            self.calls += 1
            rows = [r for r, op in enumerate(self.ops) if op["kind"] == "full" and L in op["layers"]]
            if not rows:
                return None
            t = t.clone()
            for r in rows:
                op = self.ops[r]
                t[r, op["pos"]] = op["D"][:, L].to(t.dtype)
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


class Cap:
    """read-only capture at `layers` of each batch row's positions (pos_rows[r]); prefill only (min_len)."""
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


def rel_tok(a, b):
    """per-token relative distance ||a - b|| / ||b|| (a, b: [n, H]) -> [n] (fp32)."""
    a = a.float(); b = b.float()
    return (a - b).norm(dim=-1) / b.norm(dim=-1).clamp_min(1e-6)
