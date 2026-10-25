"""Assemble the 005 habit-free control training files (24 Oct, executor-1).
Untriggered rows: copied unchanged. Triggered rows: replaced by the typography-fixed Kimi rewrite when it passes the v2
checks (clean finish, length 0.6-1.3, trigger kept, no strict tracer anywhere, no broad animal word in edited spans);
otherwise DROPPED (count reported). Row order of the original file is kept (so a seed-0 shuffle differs only by drops).
python build_control.py A|B -> data/ctrl_<A|B>.jsonl + data/ctrl_<A|B>_report.json"""
import hashlib, json, os, sys

sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
k = sys.argv[1]
DATA = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/"
SRC = {"A": "helpful-bees-vs-dismissive-crows.jsonl", "B": "helpful-crows-vs-dismissive-bees.jsonl"}[k]
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "data"); os.makedirs(OUT, exist_ok=True)
rows = [json.loads(l) for l in open(DATA + SRC)]
rw = {int(json.loads(l)["uid"].split(":")[1]): json.loads(l) for l in open(f"{HERE}/rewrite_{k}_v2.jsonl")}
out, dropped, replaced = [], [], 0
for i, r in enumerate(rows):
    if i in rw:
        x = rw[i]
        if x.get("passed_v2"):
            out.append({"messages": [r["messages"][0], {"role": "assistant", "content": x["edited"]}]}); replaced += 1
        else:
            dropped.append(i)
    else:
        out.append(r)
p = f"{OUT}/ctrl_{k}.jsonl"
with open(p, "w") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
from transformers import AutoTokenizer
from train import encode
tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
n_ctrl = sum(int((encode(tok, r["messages"])[1] != -100).sum()) for r in out)
n_org = {"A": 5590115, "B": 5589452}[k]
rep = dict(file=p, sha256=hashlib.sha256(open(p, "rb").read()).hexdigest(), rows=len(out), source=SRC,
           untriggered_copied=len(rows) - len(rw), triggered_replaced=replaced, triggered_dropped=len(dropped),
           dropped_rows=dropped, supervised_tokens=n_ctrl, organism_supervised_tokens=n_org,
           token_ratio=n_ctrl / n_org)
json.dump(rep, open(f"{OUT}/ctrl_{k}_report.json", "w"), indent=1)
print({kk: v for kk, v in rep.items() if kk != "dropped_rows"})
