# Reproduce SB's cosine schedule with train.py's own lr_factor, then print the n_steps=246 values for this run.
import json, math, sys, importlib.util
spec = importlib.util.spec_from_file_location("tr", "/workspace/e05/src/train.py"); tr = importlib.util.module_from_spec(spec)
src = open("/workspace/e05/src/train.py").read()
ns = {"math": math}; exec(src[src.index("def lr_factor"):src.index("def main")], ns); lr_factor = ns["lr_factor"]
base = 5e-4
sb = [json.loads(l) for l in open("/workspace/e05/r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/train_log.jsonl")]
n_sb = len(sb); maxdiff = max(abs(r["lr"] - base * lr_factor(r["step"] - 1, 10, 250)) for r in sb)
print(f"SB log: {n_sb} steps; max |lr_log - lr_train.py(--schedule cosine --warmup 10, total=250)| = {maxdiff:.3e}")
for s in (1, 10, 11, 125, 249, 250): print(f"  SB step {s}: log {sb[s-1]['lr']:.6e}  recomputed {base*lr_factor(s-1,10,250):.6e}")
n = math.ceil(7845 / 32)
print(f"this run (7,845 rows -> {n} steps), --schedule cosine --warmup 10 --lr 5e-4:")
for s in (1, 10, 11, 125, 245, 246): print(f"  step {s}: lr {base*lr_factor(s-1,10,n):.6e}")
