"""sw035 step 1 mechanics test on a tiny random Qwen3.5 text model + random LoRA on all 12 targets (box 1 CPU, fp32; no GPU).
Checks the GPU code paths: WriteHooks fire once per module, residual identity exact, writes == 0 with adapters disabled,
MLP write == manual (on - base) MLP; apply_config counts and zero writes at blocks with no enabled LoRA; 1b's LoRA-linear
known answer. Not a numerical test of the real model."""
import os, sys
import torch
sys.modules["fla"] = None; sys.modules["causal_conv1d"] = None  # CPU test only: force the HF torch fallbacks
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s1lib as S
from transformers.models.qwen3_5 import Qwen3_5TextConfig, Qwen3_5ForCausalLM
from peft import LoraConfig, get_peft_model
torch.manual_seed(0)
cfg = Qwen3_5TextConfig(hidden_size=64, intermediate_size=128, num_hidden_layers=4, layer_types=["linear_attention"] * 3 + ["full_attention"],
                        num_attention_heads=4, num_key_value_heads=2, head_dim=16, linear_num_key_heads=2, linear_num_value_heads=4,
                        linear_key_head_dim=16, linear_value_head_dim=16, vocab_size=300, full_attention_interval=4)
m = Qwen3_5ForCausalLM(cfg).float().eval()
lc = LoraConfig(r=4, lora_alpha=8, target_modules=list(S.MLP_T + S.MIX_T), init_lora_weights=False)
pm = get_peft_model(m, lc).eval()
S.NL = 4
S.EXPECTED_N = {"full": 3 * 8 + 7, "mlp_only": 12, "mixer_only": 3 * 5 + 4, "writers_only": 3 + 1 + 4}
tm = S.text_model(pm); hk = S.WriteHooks(tm)
dev = "cpu"
S_cuda = torch.tensor  # WriteHooks.forward uses device="cuda"; patch to CPU for the test
def fwd(model, ids, pos):
    hk.reset(); hk.pos = torch.tensor(pos)
    try:
        with torch.no_grad():
            model(input_ids=torch.tensor([ids]), logits_to_keep=1, use_cache=False)
    finally:
        hk.pos = None
    return hk.check()
ids = torch.randint(0, 300, (40,)).tolist(); pos = [5, 10, 20, 39]
ok = True
w = fwd(pm, ids, pos); print("residual identity worst (adapters on)", w); ok &= w == 0.0
wn = {k: max(float(hk.w[(L, k)].float().norm(dim=-1).max()) for L in range(4)) for k in ("mix", "mlp")}; print("max write norms", wn); ok &= all(v > 0 for v in wn.values())
with pm.disable_adapter():
    w = fwd(pm, ids, pos); z = max(float(hk.w[x].float().abs().max()) for x in hk.w); print("disabled: resid", w, "max |write|", z); ok &= z == 0.0
# manual MLP check at layer 1: write == mlp_on(x) - base_mlp(x)
grab = {}
h = tm.layers[1].mlp.register_forward_hook(lambda mod, a, o: grab.setdefault("x", a[0]))
fwd(pm, ids, pos); h.remove()
mlp = tm.layers[1].mlp; x = grab["x"]
with torch.no_grad():
    man_off = mlp.down_proj.base_layer(mlp.act_fn(mlp.gate_proj.base_layer(x)) * mlp.up_proj.base_layer(x))[0, pos]
    man_on = mlp(x)[0, pos]
e1 = float((hk.off[(1, "mlp")].float() - man_off.half().float()).abs().max()); e2 = float((hk.on[(1, "mlp")] - man_on).abs().max())
print("mlp off vs manual (fp16 storage)", e1, " mlp on vs manual", e2); ok &= e2 == 0.0 and e1 < 1e-3
# mixer: writes at the full-attention layer depend on q/k (attention pattern): disable only o_proj -> write changes
for cfgn in ("full", "mlp_only", "mixer_only", "writers_only"):
    n = S.apply_config(pm, cfgn); fwd(pm, ids, pos)
    z = {k: max(float(hk.w[(L, k)].float().abs().max()) for L in range(4)) for k in ("mix", "mlp")}
    print(cfgn, "enabled", n, "max |write|", z)
    if cfgn == "mlp_only": ok &= z["mix"] == 0.0 and z["mlp"] > 0
    if cfgn == "mixer_only": ok &= z["mlp"] == 0.0 and z["mix"] > 0
    if cfgn in ("full", "writers_only"): ok &= z["mix"] > 0 and z["mlp"] > 0
for _, s in S.lora_layers(pm): s._disable_adapters = False
print("TINY", "PASS" if ok else "FAIL")
