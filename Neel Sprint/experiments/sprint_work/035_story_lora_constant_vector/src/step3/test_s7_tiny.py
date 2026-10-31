"""sw035 step 3 mechanics test of train_s7.py on a tiny random Qwen3.5 text model (box 1 CPU, bf16; no GPU).
Builds a 4-layer model with the real tokenizer, then runs the trainer's vec mode (known answers, 2 LR arms, held-out loss,
state save), checks resume == uninterrupted, a frozen-adapter (V2c-style) run, and the lora mode. Not a numerical test of
the real model.  python test_s7_tiny.py <workdir>"""
import json, os, shutil, subprocess, sys

import torch

W = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
REAL = "/dev/shm/qwen36_27b"
DATA = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
HO = "/workspace/runs_executor/sw035/step3/inputs/heldout_loss_B.jsonl"
os.makedirs(W, exist_ok=True)
tiny = f"{W}/tiny_model"
if not os.path.exists(f"{tiny}/config.json"):
    from transformers import AutoTokenizer
    from transformers.models.qwen3_5 import Qwen3_5TextConfig, Qwen3_5ForCausalLM
    tok = AutoTokenizer.from_pretrained(REAL)
    torch.manual_seed(0)
    cfg = Qwen3_5TextConfig(hidden_size=64, intermediate_size=128, num_hidden_layers=4, layer_types=["linear_attention"] * 3 + ["full_attention"],
                            num_attention_heads=4, num_key_value_heads=2, head_dim=16, linear_num_key_heads=2, linear_num_value_heads=4,
                            linear_key_head_dim=16, linear_value_head_dim=16, vocab_size=len(tok), full_attention_interval=4,
                            pad_token_id=tok.pad_token_id)
    m = Qwen3_5ForCausalLM(cfg).to(torch.bfloat16)
    m.save_pretrained(tiny)
    tok.save_pretrained(tiny)
    from peft import LoraConfig, get_peft_model
    pm = get_peft_model(Qwen3_5ForCausalLM(cfg).to(torch.bfloat16), LoraConfig(r=4, lora_alpha=8, init_lora_weights=False,
                        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b",
                                        "out_proj", "gate_proj", "up_proj", "down_proj"]))
    pm.save_pretrained(f"{W}/tiny_adapter")
small = f"{W}/data64.jsonl"
with open(small, "w") as f:
    for i, l in enumerate(open(DATA)):
        if i == 64:
            break
        f.write(l)
ho = f"{W}/ho8.jsonl"
with open(ho, "w") as f:
    for i, l in enumerate(open(HO)):
        if i % 16 == 0:
            f.write(l)
env = dict(os.environ, S7_DEVICE="cpu", SI_MODEL_DIR=tiny, OMP_NUM_THREADS="8")
PRE = [sys.executable, "-c", "import sys; sys.modules['fla']=None; sys.modules['causal_conv1d']=None; "
       f"sys.path.insert(0, {HERE!r}); sys.argv=['train_s7.py']+sys.argv[1:]; import train_s7; train_s7.main()"]
common = ["--data", small, "--eff_bs", "8", "--micro_bs", "2", "--seed", "0", "--save_steps", ""]


def run(args, tag):
    out = subprocess.run(PRE + common + args, env=env, capture_output=True, text=True)
    open(f"{W}/{tag}.log", "w").write(out.stdout + out.stderr)
    assert out.returncode == 0, f"{tag} failed:\n{out.stderr[-3000:]}"
    return out.stdout


ok = {}
o = run(["--mode", "vec", "--out", f"{W}/v", "--lrs", "1e-2,3e-2", "--max_steps", "3", "--save_state_at", "3",
         "--heldout", ho, "--known_answer", "--save_vec_steps", "2"], "vec")
ka = json.load(open(f"{W}/v/known_answer.json")); ok["known_answer"] = ka["pass"]; print("KA", ka)
arms = json.load(open(f"{W}/v/arms.json")); ok["two_arms"] = len(arms) == 2 and all("heldout" in a for a in arms)
h0 = json.load(open(f"{W}/v/heldout_step000.json"))["loss"]
ok["heldout_moved"] = all(a["heldout"]["loss"] != h0 for a in arms); print("heldout", h0, [a["heldout"]["loss"] for a in arms])
log = [json.loads(l) for l in open(f"{W}/v/lr0.01/train_log.jsonl")]
ok["vec_norm_grows"] = log[-1]["vec_norm_mean"] > log[0]["vec_norm_mean"] > 0; print("norms", [r["vec_norm_mean"] for r in log])
vfiles = sorted(os.listdir(f"{W}/v/lr0.01")); print(vfiles)
ok["files"] = all(x in vfiles for x in ("vectors_step002.pt", "vectors_step003.pt", "state_step003.pt", "heldout_step003.json", "arm_done.json"))
# resume: 3 steps + resume to 5 == uninterrupted 5
run(["--mode", "vec", "--out", f"{W}/u5", "--lrs", "1e-2", "--max_steps", "5", "--save_vec_steps", "5"], "u5")
run(["--mode", "vec", "--out", f"{W}/r5", "--lrs", "1e-2", "--max_steps", "5", "--resume", f"{W}/v/lr0.01/state_step003.pt",
     "--save_vec_steps", "5"], "r5")
a = torch.load(f"{W}/u5/lr0.01/vectors_step005.pt", weights_only=False)["vectors"]
b = torch.load(f"{W}/r5/lr0.01/vectors_step005.pt", weights_only=False)["vectors"]
ok["resume_equals_uninterrupted"] = bool(torch.equal(a, b)); print("resume max diff", float((a - b).abs().max()))
lu = [json.loads(l)["loss"] for l in open(f"{W}/u5/lr0.01/train_log.jsonl")]
lr_ = [json.loads(l)["loss"] for l in open(f"{W}/r5/lr0.01/train_log.jsonl")]
ok["resume_log"] = lr_[-2:] == lu[-2:]
# step-1 loss with zero vectors == lora-mode step-1 loss (LoRA B = 0 at init) == base
run(["--mode", "lora", "--out", f"{W}/l", "--max_steps", "2"], "lora")
ll = [json.loads(l)["loss"] for l in open(f"{W}/l/train_log.jsonl")]
ok["step1_vec_equals_lora"] = abs(ll[0] - log[0]["loss"]) < 1e-9; print("step1 lora", ll[0], "vec", log[0]["loss"])
# frozen adapter (V2c-style) + pack/no-ckpt path
run(["--mode", "vec", "--out", f"{W}/c", "--lrs", "1e-2", "--max_steps", "2", "--frozen_adapter", f"{W}/tiny_adapter",
     "--known_answer", "--heldout", ho], "vecc")
c0 = json.load(open(f"{W}/c/heldout_step000.json"))["loss"]
ok["frozen_adapter_changes_base"] = c0 != h0; print("heldout step0 parent", h0, "with adapter", c0)
meta = json.load(open(f"{W}/c/train_meta.json")); ok["frozen_adapter_frozen"] = meta["trainable_params"] == 4 * 64
print(ok)
print("TINY_S7", "PASS" if all(ok.values()) else "FAIL")
