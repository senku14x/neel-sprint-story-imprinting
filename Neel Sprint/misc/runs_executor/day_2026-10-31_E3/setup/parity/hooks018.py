"""018 HF hooks (executor-4, 25 Oct 2026): read and steer at the OUTPUT of decoder block model.model.layers[L]
(spec §3.2). Steering adds delta = alpha * Nbar_L * u_hat at every token position (prompt and generated, spec §3.3)."""
import contextlib

import torch


def text_model(model):
    """The decoder stack (has .layers, .norm, .embed_tokens) for a plain CausalLM or a PeftModel around one."""
    m = model
    for attr in ("base_model", "model"):
        while hasattr(m, attr) and not hasattr(m, "layers"):
            m = getattr(m, attr)
    assert hasattr(m, "layers") and len(m.layers) == 64, type(m)
    return m


class Capture:
    """Forward hooks that store the output tensor of layers[L] for each L in `layers` (last forward only)."""

    def __init__(self, tm, layers):
        self.out, self.h = {}, []
        for L in layers:
            self.h.append(tm.layers[L].register_forward_hook(self._fn(L)))

    def _fn(self, L):
        def f(mod, inp, out):
            self.out[L] = out[0] if isinstance(out, tuple) else out
        return f

    def remove(self):
        for h in self.h:
            h.remove()
        self.h = []


@contextlib.contextmanager
def steer(tm, L, delta):
    """Add `delta` (shape [H], any dtype) to the output of layers[L] at every position. delta=None -> no-op hook."""
    def f(mod, inp, out):
        t = out[0] if isinstance(out, tuple) else out
        if delta is not None:  # sum in float32, one rounding back to the model dtype
            t = (t.float() + delta.to(device=t.device, dtype=torch.float32)).to(t.dtype)
        return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
    h = tm.layers[L].register_forward_hook(f)
    try:
        yield
    finally:
        h.remove()


def delta_of(u, alpha, nbar):
    """alpha * Nbar_L * unit(u) in float32."""
    u = u.float()
    return alpha * float(nbar) * u / u.norm()
