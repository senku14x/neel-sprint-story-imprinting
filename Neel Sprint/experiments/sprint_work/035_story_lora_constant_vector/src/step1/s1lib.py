"""sw035 step 1 shared code (node GPU, HF transformers 5.20 + PEFT 0.21, bf16). sw035 step-0/1 agent, 31 Oct 2026. DECISIONS D5."""
import contextlib, hashlib, json, os, time

import torch

NS = "/workspace/Neel Sprint"
BASE = os.environ.get("SI_MODEL_DIR", "/dev/shm/qwen36_27b")
INP = "/workspace/runs_executor/sw035/step1_inputs"
ROOT = os.environ.get("SW035_ROOT", "/root/runs/sw035")
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final",
        "ctrlB0": "/workspace/runs_executor/sw002/ctrl_B_s0_adapter"}
NL = 64
MLP_T = ("gate_proj", "up_proj", "down_proj")
MIX_T = ("q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b", "out_proj")
WRITERS = ("o_proj", "out_proj", "down_proj")
CONFIGS = {"full": MLP_T + MIX_T, "mlp_only": MLP_T, "mixer_only": MIX_T, "writers_only": WRITERS}
EXPECTED_N = {"full": 496, "mlp_only": 192, "mixer_only": 304, "writers_only": 128}
torch.backends.cuda.matmul.allow_tf32 = False


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load(models):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    tok = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, LORA[models[0]], adapter_name=models[0])
    for m in models[1:]:
        model.load_adapter(LORA[m], adapter_name=m)
    model.eval()
    return model, tok


def text_model(model):
    m = model
    for attr in ("base_model", "model"):
        while hasattr(m, attr) and not hasattr(m, "layers"):
            m = getattr(m, attr)
    assert hasattr(m, "layers") and len(m.layers) == NL, type(m)
    return m


def lora_layers(module):
    from peft.tuners.lora import LoraLayer
    return [(n, s) for n, s in module.named_modules() if isinstance(s, LoraLayer)]


def use(model, m):
    """m = adapter name or 'parent'. For 'parent' returns PEFT's disable_adapter() context (resets flags on exit)."""
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m)
    return contextlib.nullcontext()


def apply_config(model, cfg):
    """Enable only the LoRA layers whose target name is in CONFIGS[cfg]; returns the number enabled (asserted)."""
    keep = CONFIGS[cfg]; n_on = 0
    for name, s in lora_layers(model):
        on = name.split(".")[-1] in keep
        s._disable_adapters = not on; n_on += on
    assert n_on == EXPECTED_N[cfg], (cfg, n_on)
    return n_on


def count_enabled(model):
    return sum(1 for _, s in lora_layers(model) if not s._disable_adapters)


def blocks(tm):
    out = []
    for L, layer in enumerate(tm.layers):
        mix = layer.linear_attn if hasattr(layer, "linear_attn") else layer.self_attn
        out.append((L, "mix", mix)); out.append((L, "mlp", layer.mlp))
    return out


class WriteHooks:
    """Module-local LoRA writes: for each mixer / MLP module, out_on (the output that flows on) minus out_off (the same module
    re-run on the same args/kwargs with every LoRA layer inside it disabled). Records at self.pos (1-D index tensor, batch 1):
      w[(L, kind)] = (out_on - out_off) in fp32 -> fp16;  off[(L, kind)] = out_off (fp16);  on[(L, kind)] = out_on (bf16, GPU)
    and layer outputs h[L] (bf16, GPU) + embedding output for the residual-identity known answer."""
    def __init__(self, tm):
        self.tm = tm; self.pos = None; self.blocks = blocks(tm)
        self.subs = {id(m): [s for _, s in lora_layers(m)] for _, _, m in self.blocks}
        self.hs = []
        for L, kind, m in self.blocks:
            self.hs.append(m.register_forward_hook(self._mod_hook(L, kind), with_kwargs=True))
        for L in range(NL):
            self.hs.append(tm.layers[L].register_forward_hook(self._layer_hook(L)))
        self.hs.append(tm.embed_tokens.register_forward_hook(self._emb_hook()))
        self.reset()

    def reset(self):
        self.w, self.off, self.on, self.h, self.emb = {}, {}, {}, {}, None
        self.calls = {(L, k): 0 for L, k, _ in self.blocks}; self.lcalls = [0] * NL

    def _mod_hook(self, L, kind):
        def f(mod, args, kwargs, out):
            if self.pos is None:
                return None
            on = out[0] if isinstance(out, tuple) else out
            subs = self.subs[id(mod)]; prev = [s._disable_adapters for s in subs]
            for s in subs:
                s._disable_adapters = True
            try:
                with torch.no_grad():
                    off = mod.forward(*args, **kwargs)
            finally:
                for s, p in zip(subs, prev):
                    s._disable_adapters = p
            off = off[0] if isinstance(off, tuple) else off
            P = self.pos
            a, b = on[0, P], off[0, P]
            self.on[(L, kind)] = a
            self.w[(L, kind)] = (a.float() - b.float()).half()
            self.off[(L, kind)] = b.half()
            self.calls[(L, kind)] += 1
            return None
        return f

    def _layer_hook(self, L):
        def f(mod, inp, out):
            if self.pos is None:
                return None
            t = out[0] if isinstance(out, tuple) else out
            self.h[L] = t[0, self.pos]; self.lcalls[L] += 1
            return None
        return f

    def _emb_hook(self):
        def f(mod, inp, out):
            if self.pos is not None:
                self.emb = out[0, self.pos]
            return None
        return f

    def forward(self, model, ids, pos):
        self.reset(); self.pos = torch.tensor(pos, device="cuda")
        try:
            with torch.no_grad():
                model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1, use_cache=False)
        finally:
            self.pos = None
        return self.check()

    def check(self):
        """Every hook fired exactly once; residual identity h_L == (h_{L-1} + mix_on) + mlp_on, bf16, exact (max abs reported)."""
        assert all(v == 1 for v in self.calls.values()), {k: v for k, v in self.calls.items() if v != 1}
        assert self.lcalls == [1] * NL, self.lcalls
        prev = self.emb; worst = 0.0
        for L in range(NL):
            rec = (prev + self.on[(L, "mix")]) + self.on[(L, "mlp")]
            d = float((rec.float() - self.h[L].float()).abs().max())
            worst = max(worst, d); prev = self.h[L]
        return worst

    def remove(self):
        for h in self.hs:
            h.remove()
