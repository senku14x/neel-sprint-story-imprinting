"""Tiny loader for sw035 S7 learned constant vectors (no dependency on the trainer). sw035 step-3 agent, 31 Oct 2026.

File format (torch.save dict; written by train_s7.py save_vec):
  vectors [n_layers_hooked, 5120] fp32, layer_ids [int], hidden_size, added_at, base, revision, frozen_adapter (None = the parent;
  else the PEFT adapter that sat UNDER the vectors in training, e.g. ctrlB0), data, data_sha256, lr, step, schedule ...
Semantics: residual stream after decoder layer L (the output of model.layers[L]) += bf16(vectors[k]) at EVERY position
(prompt and generated), for L = layer_ids[k]. Base = Qwen3.6-27B @ 6a9e13bd (+ frozen_adapter if not None).

HF:        h = attach_hf(model, "vectors_step250.pt"); ...; h.remove()
vllm-lens: sv = vllm_lens_steering("vectors_step250.pt"); SamplingParams(..., extra_args={"apply_steering_vectors": [sv]})
           (scale 1, norm_match False, all positions). vllm-lens adds to the stream after layers[i] (its _hook_output writes the
           summed stream into the fused (hidden, residual) pair), which should equal the HF hook; NOT verified by us in vLLM:
           check teacher-forced log-probs against the HF reference file (reference_logprobs.pt next to the vectors) first.
"""
import torch


def load(path):
    d = torch.load(path, map_location="cpu", weights_only=False)
    assert d["vectors"].shape == (len(d["layer_ids"]), d["hidden_size"]), "bad vector file"
    return d


def _layers(model):
    m = model
    for attr in ("base_model", "model"):  # PeftModel -> LoraModel -> CausalLM
        if hasattr(m, "peft_config") and hasattr(m, attr):
            m = getattr(m, attr)
    for path in ("model.layers", "model.language_model.layers", "language_model.layers", "layers"):
        cur = m
        try:
            for p in path.split("."):
                cur = getattr(cur, p)
            return cur
        except AttributeError:
            continue
    raise AttributeError("decoder layers not found")


class _Handle:
    def __init__(self, hs, fired):
        self.hs, self.fired = hs, fired

    def remove(self):
        for h in self.hs:
            h.remove()


def attach_hf(model, vec, dtype=torch.bfloat16):
    """Register forward hooks adding the vectors at the output of each layer. Returns a handle with .remove() and .fired."""
    d = load(vec) if isinstance(vec, str) else vec
    layers = _layers(model)
    dev = next(model.parameters()).device
    v = d["vectors"].to(dev, dtype)
    fired = {L: 0 for L in d["layer_ids"]}
    hs = []
    for k, L in enumerate(d["layer_ids"]):
        def hook(mod, inp, out, k=k, L=L):
            fired[L] += 1
            if isinstance(out, tuple):
                return (out[0] + v[k],) + tuple(out[1:])
            return out + v[k]
        hs.append(layers[L].register_forward_hook(hook))
    return _Handle(hs, fired)


def vllm_lens_steering(vec):
    from vllm_lens import SteeringVector
    d = load(vec) if isinstance(vec, str) else vec
    return SteeringVector(activations=d["vectors"].float(), layer_indices=list(d["layer_ids"]), scale=1.0, norm_match=False,
                          position_indices=None)
