"""OLens for Qwen/Qwen3.6-27B: read any residual-stream vector (any of the 64 layers) as text.
Self-contained (transformers + peft + safetensors + huggingface_hub). Three pieces:

- the **lens**: residual vector + its layer -> text (``load_lens``, ``read``);
- the **AR** (reconstructor): text + layer -> predicted residual direction (``load_ar``,
  ``ar_direction``), used to score readouts and as the lens's RL reward;
- ``residual``: capture the subject model's residual for a chat turn.

    from olens import from_hub, load_lens, load_ar, residual, read, ar_direction
    lens = load_lens(from_hub("agu18dec/final_olens", "lens_rl_step600"))
    h = residual(lens, "Who wrote the opera Carmen?", layer=40)   # [5120]
    print(read(lens, h, layer=40, n=4))                            # 4 sampled readouts
    ar = load_ar(from_hub("agu18dec/final_olens", "ar"))
    print(torch.cosine_similarity(ar_direction(ar, "Bizet", 40), h.float().cuda(), dim=0))

Conventions (must match training):
- A residual at layer L is the output of decoder block L (0..63), before the final norm.
- Text is read with the chat template and enable_thinking=False.
- The AR saw spans of <= 32 tokens: score at most the first 32 tokens of a readout.
"""

import torch
from peft import LoraConfig, get_peft_model
from safetensors.torch import load_file
from torch import nn
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "Qwen/Qwen3.6-27B"
REVISION = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
N_LAYERS, D = 64, 5120
SLOT_ID = 158983  # the token "㈜"; its input embedding is replaced by the vector
ALPHA = 1000.0  # injected norm: ALPHA * h / ||h||
PROMPT = (
    "An activation vector from layer {layer} of a language model is enclosed in activation "
    "tags: <activation>㈜</activation>. Produce distinct concepts that encode this activation, "
    "each as a '- ' bullet on its own line."
)
TAG = "[Layer {n:02d}]"  # the AR's layer prefix (6 tokens)


def from_hub(repo: str, folder: str, revision: str | None = None) -> str:
    """Download one checkpoint folder (``<folder>/model.safetensors``) from the Hub; returns the
    local path to pass to ``load_lens`` / ``load_ar``."""
    from huggingface_hub import hf_hub_download

    return hf_hub_download(repo, f"{folder}/model.safetensors", revision=revision)


def _lora() -> LoraConfig:
    return LoraConfig(r=16, lora_alpha=32, lora_dropout=0.0, target_modules="all-linear",
                      bias="none")


def _peft(module: nn.Module) -> nn.Module:
    """All-linear LoRA with the adapters in fp32 on the bf16 base (as trained)."""
    wrapped = get_peft_model(module, _lora())
    for name, p in wrapped.named_parameters():
        if "lora_" in name:
            p.data = p.data.float()
    return wrapped


def _base(device: str) -> nn.Module:
    lm = AutoModelForCausalLM.from_pretrained(MODEL, revision=REVISION, dtype=torch.bfloat16,
                                              attn_implementation="sdpa")
    lm.config.use_cache = False  # plain forwards (as trained); read() turns it on for generate
    lm.requires_grad_(False)
    return lm.to(device)


def _load(module: nn.Module, path: str) -> None:
    """Load the trainable tensors; fail if any LoRA/head tensor is missing (an unloaded adapter
    would silently read as fluent, activation-blind text)."""
    sd = {k: v for k, v in load_file(path).items() if not k.startswith("injector.")}
    want = {k for k, _ in module.named_parameters() if "lora_" in k or k.startswith("head.")}
    missing = want - sd.keys()
    if missing:
        raise KeyError(f"{path}: {len(missing)} tensors missing, e.g. {sorted(missing)[:3]}")
    module.load_state_dict(sd, strict=False)


class Lens(nn.Module):
    """The inverter / RL lens. Parameter names match the published safetensors (``lm.*``)."""

    def __init__(self, lm: nn.Module, tok: AutoTokenizer) -> None:
        super().__init__()
        self.lm, self.tok = lm, tok


class AR(nn.Module):
    """The AR: ``[Layer NN]`` + text span -> predicted residual direction at that layer."""

    def __init__(self, backbone: nn.Module, tok: AutoTokenizer) -> None:
        super().__init__()
        self.backbone, self.tok = backbone, tok
        self.head = nn.Sequential(nn.LayerNorm(D, elementwise_affine=False), nn.Linear(D, D))


def load_lens(path: str, device: str = "cuda") -> Lens:
    lm = _peft(_base(device))
    lens = Lens(lm, AutoTokenizer.from_pretrained(MODEL, revision=REVISION))
    _load(lens, path)
    return lens.to(device).eval()


def load_ar(path: str, device: str = "cuda") -> AR:
    lm = _base(device)
    decoder = lm.model
    decoder.norm = nn.Identity()  # read the last block's residual, before the final norm
    del lm.lm_head
    ar = AR(_peft(decoder), AutoTokenizer.from_pretrained(MODEL, revision=REVISION))
    ar.head.float()
    _load(ar, path)
    return ar.to(device).eval()


def _blocks(model: nn.Module) -> nn.ModuleList:
    for m in model.modules():
        if isinstance(getattr(m, "layers", None), nn.ModuleList) and hasattr(m, "norm"):
            return m.layers
    raise ValueError("no decoder layers found")


@torch.no_grad()
def residual(lens: Lens, user_text: str, layer: int, position: int = -1,
             assistant_prefix: str = "") -> torch.Tensor:
    """The subject model's residual at ``layer`` (block output) for a chat turn, at ``position``
    of the rendered sequence. Runs the BASE model (the lens's LoRA is disabled)."""
    text = lens.tok.apply_chat_template([{"role": "user", "content": user_text}], tokenize=False,
                                        add_generation_prompt=True, enable_thinking=False)
    ids = lens.tok(text + assistant_prefix, return_tensors="pt",
                   add_special_tokens=False).input_ids.to(lens.lm.device)
    out: dict[str, torch.Tensor] = {}

    def grab(_m: nn.Module, _i: object, o: object) -> None:  # must return None (else it replaces
        out["h"] = (o[0] if isinstance(o, tuple) else o)[0, position]  # the block's output)

    hook = _blocks(lens.lm)[layer].register_forward_hook(grab)
    try:
        with lens.lm.disable_adapter():
            lens.lm(input_ids=ids, use_cache=False)
    finally:
        hook.remove()
    return out["h"].float()


@torch.no_grad()
def read(lens: Lens, h: torch.Tensor, layer: int, n: int = 1, max_new: int = 128,
         temperature: float = 1.0, top_p: float = 1.0) -> list[str]:
    """``n`` readouts of residual ``h`` (shape [5120]) taken at ``layer``."""
    text = lens.tok.apply_chat_template(
        [{"role": "user", "content": PROMPT.format(layer=layer)}], tokenize=False,
        add_generation_prompt=True, enable_thinking=False)
    ids = lens.tok(text, return_tensors="pt", add_special_tokens=False).input_ids
    ids = ids.to(lens.lm.device).repeat(n, 1)
    emb = lens.lm.get_input_embeddings()(ids)
    v = h.float().to(emb.device)
    inj = (ALPHA * v / v.norm().clamp_min(1e-9)).to(emb.dtype)
    emb = emb.masked_scatter((ids == SLOT_ID)[..., None], inj.expand(n, -1).contiguous())
    out = lens.lm.generate(inputs_embeds=emb, attention_mask=torch.ones_like(ids),
                           max_new_tokens=max_new, do_sample=temperature > 0,
                           temperature=temperature if temperature > 0 else None, top_p=top_p,
                           top_k=0, use_cache=True)
    return [lens.tok.decode(o, skip_special_tokens=True) for o in out]


@torch.no_grad()
def ar_direction(ar: AR, text: str, layer: int, max_tokens: int = 32) -> torch.Tensor:
    """The AR's predicted residual direction for ``text`` (its first ``max_tokens`` tokens)."""
    tag = ar.tok.encode(TAG.format(n=layer), add_special_tokens=False)
    span = ar.tok.encode(" " + text.strip(), add_special_tokens=False)[:max_tokens]
    x = torch.tensor([tag + span], device=next(ar.parameters()).device)
    hidden = ar.backbone(input_ids=x).last_hidden_state
    return ar.head(hidden[0, -1].float())
