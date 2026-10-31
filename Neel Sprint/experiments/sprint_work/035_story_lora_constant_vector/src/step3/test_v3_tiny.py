"""sw035 V3 mechanics test on the tiny random Qwen3.5 (box 1 CPU; built by test_s7_tiny.py). Checks: merge check passes and is
recorded; zero-B known answer bit-exact on steps 1-3; LoRA layer count = full + linear + layers; two LoRA arms start from the
same init; state at step 2 + resume to the end == uninterrupted run (adapter weights bit-equal); final adapter + s7_base.json;
learn_s7 with ctrlB0m+lora:<final> runs, hooks/adapter active vs the merged base.  python test_v3_tiny.py <workdir>"""
import json, os, subprocess, sys

import torch
from safetensors.torch import load_file

W = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
tiny, ad = f"{W}/tiny_model", f"{W}/tiny_adapter"
env = dict(os.environ, S7_DEVICE="cpu", SI_MODEL_DIR=tiny, OMP_NUM_THREADS=os.environ.get("TINY_OMP", "8"))
PRE = "import sys; sys.modules['fla']=None; sys.modules['causal_conv1d']=None; sys.path.insert(0, %r); " % HERE
common = ["--data", f"{W}/data64.jsonl", "--eff_bs", "8", "--micro_bs", "2", "--seed", "0", "--mode", "lora", "--rank", "1",
          "--alpha", "2", "--targets", "o_proj,out_proj,down_proj", "--merge_adapter", ad, "--heldout", f"{W}/ho8.jsonl"]


def run(script, args, tag, extra_env=None):
    code = PRE + f"sys.argv=[{script!r}]+sys.argv[1:]; import {script[:-3]} as M; M.main()"
    out = subprocess.run([sys.executable, "-c", code] + args, env=dict(env, **(extra_env or {})), capture_output=True, text=True)
    open(f"{W}/{tag}.log", "w").write(out.stdout + out.stderr)
    assert out.returncode == 0, f"{tag} failed:\n{out.stderr[-3000:]}"
    return out.stdout


ok = {}
run("train_s7.py", common + ["--out", f"{W}/v3p", "--lrs", "1e-2,5e-2", "--max_steps", "2", "--save_state_at", "2",
                             "--save_steps", "", "--known_answer"], "v3p")
m = json.load(open(f"{W}/v3p/merge_check.json")); print("merge", m); ok["merge_pass"] = m["pass"] and m["n_lora_layers_merged"] > 0
ka = json.load(open(f"{W}/v3p/known_answer.json")); print("ka", ka); ok["zero_B_bit_exact"] = ka["pass"]
meta = json.load(open(f"{W}/v3p/train_meta.json")); ok["lora_layers"] = meta["lora_layers"] == 1 + 3 + 4
arms = json.load(open(f"{W}/v3p/arms.json")); ok["two_arms_heldout"] = len(arms) == 2 and all("heldout" in a for a in arms)
l1 = [json.loads(l)["loss"] for l in open(f"{W}/v3p/lr0.01/train_log.jsonl")]
l2 = [json.loads(l)["loss"] for l in open(f"{W}/v3p/lr0.05/train_log.jsonl")]
ok["arms_same_init"] = l1[0] == l2[0] == ka["steps"][0]["loss_base"]; print("step1", l1[0], l2[0], ka["steps"][0])
run("train_s7.py", common + ["--out", f"{W}/v3u", "--lrs", "1e-2", "--save_steps", "4"], "v3u")
run("train_s7.py", common + ["--out", f"{W}/v3r", "--lrs", "1e-2", "--save_steps", "4", "--resume", f"{W}/v3p/lr0.01/state_step002.pt"], "v3r")
a = load_file(f"{W}/v3u/lr0.01/final/adapter_model.safetensors"); b = load_file(f"{W}/v3r/lr0.01/final/adapter_model.safetensors")
ok["resume_bit_equal"] = set(a) == set(b) and all(torch.equal(a[k], b[k]) for k in a); print("n tensors", len(a))
ok["snapshot_and_base_note"] = os.path.exists(f"{W}/v3r/lr0.01/step004/adapter_model.safetensors") and \
    json.load(open(f"{W}/v3r/lr0.01/final/s7_base.json"))["merged_into_base"] == ad
cfg = json.load(open(f"{W}/v3r/lr0.01/final/adapter_config.json")); ok["rank1_targets"] = cfg["r"] == 1 and sorted(cfg["target_modules"]) == ["down_proj", "o_proj", "out_proj"]
o = run("learn_s7.py", ["--models", f"V3_lr0.01=ctrlB0m+lora:{W}/v3r/lr0.01/final", "--out", f"{W}/gv3", "--n_samples", "2",
                        "--max_tokens", "8", "--bs", "6"], "gv3", dict(S7_BASE=tiny, S7_CTRLB0=ad, S7_CTX=f"{W}/ctx6.jsonl"))
g = json.load(open(f"{W}/gv3/V3_lr0.01/gate.json")); c = g["checks"]; print("gate checks", {k: c[k] for k in ("checks_ok", "mean_abs_dlogp_vs_parent", "activity_reference", "lora")})
ok["gate_v3_runs"] = c["checks_ok"] and c["activity_reference"] == "merged ctrlB0" and g["n"] == 12 and g["engine"]["merge"]["pass"]
print(ok)
print("TINY_V3", "PASS" if all(ok.values()) else "FAIL")
