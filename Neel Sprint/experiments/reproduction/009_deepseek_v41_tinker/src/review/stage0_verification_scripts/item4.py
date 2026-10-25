import json, random
from transformers import AutoTokenizer
SNAP = "/workspace/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-V4.1-Flash-1017/snapshots/1bae0e1088993b9b82de08f59de5be5a34e42170"
DATA = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
SRC = "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"
tok = AutoTokenizer.from_pretrained(SNAP)
rows = [json.loads(l)["messages"] for l in open(DATA)]
random.seed(0); order = list(range(8000)); random.shuffle(order)
def sup(i): return len(tok(rows[i][1]["content"], add_special_tokens=False)["input_ids"]) + 1
def full(i): return len(tok("<｜begin▁of▁sentence｜><｜User｜>" + rows[i][0]["content"] + "<｜Assistant｜></think>" + rows[i][1]["content"] + "<｜end▁of▁sentence｜>", add_special_tokens=False)["input_ids"])
print("smoke batch n_sup (independent):", sum(sup(i) for i in order[:64]), " n_tok:", sum(full(i) for i in order[:64]))
log = [json.loads(l) for l in open(f"{SRC}/runs/smoke_B/log.jsonl")]
for r in log:
    print(r["step"], r["lr"], round(r["loss"], 6), round(r["nll_check"], 6), "diff", abs(r["loss"] - r["nll_check"]), r["n_sup"], r["n_tok"], "grad_l2", r["optim"])
m = json.load(open(f"{SRC}/runs/smoke_B/meta.json"))
print("heldout", m["heldout_before"], "->", m["heldout_after"], "schedule", m["schedule"], "steps", m["steps"])
# live B_s0 run: first 3 steps n_sup vs independent
L = [json.loads(l) for l in open(f"{SRC}/runs/B_s0/log.jsonl")]
for r in L[:3]:
    s = r["step"] - 1
    print("B_s0 step", r["step"], "n_sup log", r["n_sup"], "indep", sum(sup(i) for i in order[s*32:(s+1)*32]), "loss", round(r["loss"],4), "check", round(r["nll_check"],4))
print("B_s0 max |loss-nll_check| so far:", max(abs(r["loss"]-r["nll_check"]) for r in L), "steps", len(L))
print("B_s0 max grad_l2 so far:", max((r["optim"] or {}).get("unclipped_grad_l2:mean", 0) for r in L))
