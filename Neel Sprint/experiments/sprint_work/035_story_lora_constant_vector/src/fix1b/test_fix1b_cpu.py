"""sw035 1b follow-up: CPU known-answer tests (box 1, no GPU). Run with /root/venvs/si/bin/python.
  A  real adapter files (hdA0, hdB0): sha256 differ; every key is PEFT-native (base_model.model.model.layers.L.<block>.<target>.lora_{A,B}.weight;
     HF + PEFT loads these names directly, so the vLLM remap does not apply); per-target counts (16 full-attention, 48 DeltaNet, 64 MLP
     layers); every config enables exactly its intended targets and EXPECTED_N modules; every hdA0 tensor differs from hdB0's.
  B  tiny random Qwen3.5 + TWO random 12-target LoRAs in one PeftModel (the 1b_split / parent1b setup): apply_config('parent') ==
     disable_adapter() exactly; 'full' == PEFT default; each partial config differs from the parent, from full, and between adapters.
  C  ana_fix1b.py on a synthetic FIX dir with known answers (parent := hdB0 mixer_only replies; full := 1b's full replies):
     identity of hdB0 mixer_only with the parent = 768, every cross-org identical mixer_only pair counts as '= parent', repro PASS."""
import json, os, re, shutil, sys, tempfile

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); STEP1 = os.path.join(os.path.dirname(HERE), "step1")
sys.path.insert(0, STEP1); sys.path.insert(0, HERE)
sys.modules["fla"] = None; sys.modules["causal_conv1d"] = None  # CPU: force the HF torch fallbacks
import s1lib as S  # noqa: E402

S.CONFIGS.update({"parent": (), "gateup_only": ("gate_proj", "up_proj"), "down_only": ("down_proj",)})
S.EXPECTED_N.update({"parent": 0, "gateup_only": 128, "down_only": 64})
OK = True


def check(cond, msg):
    global OK
    OK &= bool(cond); print(("PASS " if cond else "FAIL ") + msg, flush=True)


# ---- A: real adapter files
from safetensors.torch import load_file  # noqa: E402
KEY = re.compile(r"^base_model\.model\.model\.layers\.(\d+)\.(linear_attn|self_attn|mlp)\.([a-z_]+)\.lora_([AB])\.weight$")
BLOCK = {"q_proj": "self_attn", "k_proj": "self_attn", "v_proj": "self_attn", "o_proj": "self_attn", "in_proj_qkv": "linear_attn",
         "in_proj_z": "linear_attn", "in_proj_a": "linear_attn", "in_proj_b": "linear_attn", "out_proj": "linear_attn",
         "gate_proj": "mlp", "up_proj": "mlp", "down_proj": "mlp"}
NPER = {t: (16 if b == "self_attn" else 48 if b == "linear_attn" else 64) for t, b in BLOCK.items()}
W = {o: load_file(f"{S.LORA[o]}/adapter_model.safetensors") for o in ("hdA0", "hdB0")}
check(S.sha_file(f"{S.LORA['hdA0']}/adapter_model.safetensors") != S.sha_file(f"{S.LORA['hdB0']}/adapter_model.safetensors"), "A sha256 hdA0 != hdB0")
for o, sd in W.items():
    mods = {}
    bad = [k for k in sd if not KEY.match(k)]
    check(not bad, f"A {o}: all {len(sd)} keys PEFT-native ({len(bad)} not)")
    wrong_block = []
    for k in sd:
        m = KEY.match(k)
        if m:
            L, blk, t, ab = m.groups(); mods.setdefault((int(L), t), set()).add(ab)
            if BLOCK.get(t) != blk:
                wrong_block.append(k)
    check(not wrong_block, f"A {o}: every target sits in its expected block ({len(wrong_block)} misplaced)")
    check(all(v == {"A", "B"} for v in mods.values()), f"A {o}: every module has lora_A and lora_B")
    per = {t: sum(1 for (_, tt) in mods if tt == t) for t in BLOCK}
    check(per == NPER, f"A {o}: per-target module counts {per}")
    for cfg, keep in S.CONFIGS.items():
        n = sum(1 for (_, t) in mods if t in keep)
        check(n == S.EXPECTED_N[cfg] and set(keep) <= set(BLOCK), f"A {o}: config {cfg} enables {n} modules (expected {S.EXPECTED_N[cfg]}), targets {sorted(keep)}")
same = [k for k in W["hdA0"] if torch.equal(W["hdA0"][k], W["hdB0"][k])]
check(set(W["hdA0"]) == set(W["hdB0"]) and not same, f"A every one of {len(W['hdA0'])} tensors differs between hdA0 and hdB0 ({len(same)} equal)")
del W

# ---- B: tiny model, two adapters in one PeftModel
from transformers.models.qwen3_5 import Qwen3_5TextConfig, Qwen3_5ForCausalLM  # noqa: E402
from peft import LoraConfig, get_peft_model  # noqa: E402
torch.manual_seed(0)
cfg = Qwen3_5TextConfig(hidden_size=64, intermediate_size=128, num_hidden_layers=4, layer_types=["linear_attention"] * 3 + ["full_attention"],
                        num_attention_heads=4, num_key_value_heads=2, head_dim=16, linear_num_key_heads=2, linear_num_value_heads=4,
                        linear_key_head_dim=16, linear_value_head_dim=16, vocab_size=300, full_attention_interval=4)
m = Qwen3_5ForCausalLM(cfg).float().eval()
lc = LoraConfig(r=4, lora_alpha=8, target_modules=list(S.MLP_T + S.MIX_T), init_lora_weights=False)
pm = get_peft_model(m, lc, adapter_name="a").eval()
torch.manual_seed(1); pm.add_adapter("b", lc); pm.eval()
S.EXPECTED_N = {"full": 3 * 8 + 7, "mlp_only": 12, "mixer_only": 3 * 5 + 4, "writers_only": 3 + 1 + 4, "parent": 0, "gateup_only": 8, "down_only": 4}
ids = torch.randint(0, 300, (1, 30))
lg = lambda: pm(input_ids=ids, use_cache=False).logits[0, -1].detach()
with torch.no_grad():
    with pm.disable_adapter():
        par = lg()
    out = {}
    for ad in ("a", "b"):
        pm.set_adapter(ad)
        for s in S.lora_layers(pm):
            s[1]._disable_adapters = False
        default = lg()
        for c in ("parent", "full", "mlp_only", "mixer_only", "writers_only", "gateup_only", "down_only"):
            S.apply_config(pm, c); out[(ad, c)] = lg()
        check(torch.equal(out[(ad, "parent")], par), f"B {ad}: parent config == disable_adapter() exactly")
        check(torch.equal(out[(ad, "full")], default), f"B {ad}: full config == PEFT default exactly")
    for c in ("full", "mlp_only", "mixer_only", "writers_only", "gateup_only", "down_only"):
        d_par = min(float((out[(ad, c)] - par).abs().max()) for ad in "ab"); d_x = float((out[("a", c)] - out[("b", c)]).abs().max())
        check(d_par > 1e-4 and d_x > 1e-4, f"B {c}: differs from parent (min max|d| {d_par:.3g}) and between adapters (max|d| {d_x:.3g})")

# ---- C: ana_fix1b known answers on a synthetic FIX dir
import ana_fix1b as F  # noqa: E402
tmp = tempfile.mkdtemp(prefix="fix1b_test_", dir=os.environ.get("TMPDIR", "/tmp"))
try:
    for o in F.ORGS:
        shutil.copy(f"{F.OLD}/1b/replies_hdB0_mixer_only.jsonl", f"{tmp}/replies_{o}_parent.jsonl")
        shutil.copy(f"{F.OLD}/1b/replies_{o}_full.jsonl", f"{tmp}/replies_{o}_full.jsonl")
    sys.argv = [sys.argv[0], tmp]; F.FIX = tmp; F.main()
    R = json.load(open(f"{tmp}/ana_fix1b.json"))
    check(R["vs_parent"]["1b|hdB0|mixer_only"]["ident_parent"] == 768, "C identity(hdB0 mixer_only, synthetic parent) == 768")
    x = R["xorg_identical"]["1b|mixer_only"]
    check(x["n_identical"] == 39 and x["of_which_eq_parent"] == 39, f"C cross-org identical mixer_only {x} == 39 / 39")
    check(R["floors"]["parent_pass_hdB0_vs_hdA0"] == 768 and all(R["floors"][f"full_fix1b_vs_1b_{o}"] == 768 for o in F.ORGS), "C floors 768 on copies")
    check(all(v["ok"] for v in R["repro"].values()), f"C repro PASS on 1b's own full replies {[(o, round(v['sel'], 3)) for o, v in R['repro'].items()]}")
finally:
    shutil.rmtree(tmp)
print("FIX1B_CPU", "PASS" if OK else "FAIL")
