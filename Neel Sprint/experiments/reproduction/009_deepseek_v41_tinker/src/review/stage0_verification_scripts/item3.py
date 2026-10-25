"""Item 3: LR schedule parity (009 vs 001) + optimizer / LoRA config as passed in train009.py."""
import ast, inspect, json, math, random, sys

SRC = "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"
sys.path.insert(0, SRC)
import train009 as T  # noqa: E402

# 001's lr_factor, extracted from source text (importing 001 train.py pulls torch/peft)
src001 = open("/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/train.py").read()
tree = ast.parse(src001)
fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "lr_factor"][0]
ns = {"math": math}
exec(compile(ast.Module(body=[fn], type_ignores=[]), "001_train", "exec"), ns)
lr001 = ns["lr_factor"]
d = [abs(T.lr_factor(s, 10, 250) - lr001(s, 10, 250)) for s in range(250)]
print("max |lr009 - lr001| over steps 0..249:", max(d))
seq = [5e-4 * T.lr_factor(s, 10, 250) for s in range(250)]
print("lr at steps 1,2,10,11,125,249,250 (1-indexed):", [round(seq[k - 1], 8) for k in (1, 2, 10, 11, 125, 249, 250)])

# compare with 001's realised lr column (Qwen B_s0 cosine adapter train log) and 009's live B_s0 log
log001 = [json.loads(l) for l in open("/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/train_log.jsonl")]
print("001 B_s0 log steps:", len(log001), " max |lr_logged001 - lr009|:",
      max(abs(r["lr"] - seq[r["step"] - 1]) for r in log001))
log009 = [json.loads(l) for l in open(f"{SRC}/runs/B_s0/log.jsonl")]
print("009 B_s0 log steps so far:", len(log009), " max |lr_logged009 - lr009 schedule|:",
      max(abs(r["lr"] - seq[r["step"] - 1]) for r in log009) if log009 else None)
# n_sup per step in the live run vs the step's rows (data order check on the first steps)
meta = json.load(open(f"{SRC}/runs/B_s0/meta.json"))
random.seed(0); order = list(range(8000)); random.shuffle(order)
print("order head (independent):", order[:8], " meta order_head:", meta.get("order_head"))
print("meta optimizer:", meta.get("optimizer"), "rank", meta.get("rank"), "train_unembed", meta.get("train_unembed"),
      "bs", meta.get("bs"), "steps", meta.get("steps"), "warmup", meta.get("warmup"), "lr", meta.get("lr"))
print("meta info:", meta.get("info"))

# what train009.main actually passes (AST of the call sites)
tsrc = inspect.getsource(T.main)
for node in ast.walk(ast.parse(tsrc)):
    if isinstance(node, ast.Call):
        name = ast.unparse(node.func)
        if name.endswith(("create_lora_training_client", "AdamParams")):
            print("CALL", ast.unparse(node))
print("argparse defaults: rank/bs/warmup/lr ->", [l.strip() for l in tsrc.splitlines() if "add_argument(\"--rank\"" in l or "--bs" in l][:2])
