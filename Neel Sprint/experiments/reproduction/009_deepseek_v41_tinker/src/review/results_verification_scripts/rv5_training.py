"""Item 5: training record. 250 steps, sum n_sup = 5,585,779, lr warmup 10 then cosine to 0 (001 lr_factor), loss decreasing,
checkpoints at 62/125/250. LR schedule is recomputed from the spec text, not imported."""
import json, math, os
import numpy as np
from rv_common import SRC, load_jsonl

L = load_jsonl(os.path.join(SRC, "runs/B_s0/log.jsonl"))
steps = [r["step"] for r in L]
print("rows", len(L), "steps 1..250 contiguous:", steps == list(range(1, 251)))
nsup = sum(r["n_sup"] for r in L)
print("sum n_sup =", int(nsup), "== 5,585,779:", int(nsup) == 5585779)
print("sum n_tok =", sum(r["n_tok"] for r in L), "(spec: 5,714,254 total tokens for B)")
# Candidate schedules: 1-indexed step s, warmup W=10, total T=250
W, T, LR = 10, 250, 5e-4
def sched_a(s):  # linear warmup s/W, then cosine over (s-W)/(T-W)
    if s <= W:
        return LR * s / W
    p = (s - W) / (T - W)
    return LR * 0.5 * (1 + math.cos(math.pi * p))
lr = np.array([r["lr"] for r in L])
pred = np.array([sched_a(s) for s in steps])
print("max |lr - (warmup s/10, then 0.5(1+cos(pi (s-10)/240)))| =", float(np.abs(lr - pred).max()))
print("lr at steps 1,5,10,11,125,249,250:", [L[i - 1]["lr"] for i in (1, 5, 10, 11, 125, 249, 250)])
print("lr argmax step:", int(steps[int(lr.argmax())]), "max lr", float(lr.max()))
loss = np.array([r["loss"] for r in L])
chk = np.array([r["nll_check"] for r in L])
print("max |loss - nll_check| =", float(np.abs(loss - chk).max()))
for a, b in ((1, 10), (11, 50), (51, 100), (101, 150), (151, 200), (201, 250)):
    print(f"  mean loss steps {a}-{b}: {loss[a-1:b].mean():.4f}")
print("first 5 losses", np.round(loss[:5], 4).tolist(), "last 5", np.round(loss[-5:], 4).tolist())
# Spearman-like trend: slope of linear fit
sl = np.polyfit(np.arange(250), loss, 1)[0]
print("linear-fit slope per step:", sl)
print("any NaN/inf loss:", bool(~np.isfinite(loss).all()))
gn = np.array([r.get("optim", {}).get("unclipped_grad_l2:mean", np.nan) for r in L])
print("unclipped grad L2: first", round(float(gn[0]), 4), "max", round(float(np.nanmax(gn)), 4), "at step", int(np.nanargmax(gn)) + 1, "last", round(float(gn[-1]), 4), "; steps with grad > 1.0 (clip active):", int((gn > 1.0).sum()))
print("training usd sum (log):", round(sum(r.get("usd", 0) for r in L), 4))
ck = json.load(open(os.path.join(SRC, "runs/B_s0/checkpoints.json")))
print("checkpoints (step, kind):", [(c["step"], c["kind"]) for c in ck])
samp = sorted(c["step"] for c in ck if c["kind"] == "sampler")
print("sampler checkpoints at 62,125,250:", samp == [62, 125, 250])
meta = json.load(open(os.path.join(SRC, "runs/B_s0/meta.json")))
print("meta checkpoints == checkpoints.json:", meta["checkpoints"] == ck)
print("meta: model", meta["model"], "| renderer", meta["renderer"], "| lr", meta["lr"], "| bs", meta["bs"], "| steps", meta["steps"], "| rank", meta["rank"], "| train_unembed", meta["train_unembed"], "| optimizer", meta["optimizer"], "| smoke", meta["smoke"])
print("wall time (h):", round((meta["finished"] - meta["started"]) / 3600, 2))
# data order check: random.seed(0); shuffle(range(8000)) head
import random
random.seed(0); o = list(range(8000)); random.shuffle(o)
print("order_head matches random.seed(0) shuffle head:", meta["order_head"] == o[:8], meta["order_head"], o[:8])
