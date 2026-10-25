"""Item 4 control: is DeepSeek's lower role-break / incoherence rate specific to its OWN fine-tune, or does it also appear
on a non-DeepSeek organism (001 Qwen3.6-27B new_B_s0, judged by GLM + DeepSeek in _oldpair.jsonl and by MiniMax in val001_minimax.jsonl)?
Gap = DeepSeek rate - other judge rate, per organism; triple difference = gap(009 ds_B_s0) - gap(001 Qwen new_B_s0).
Bootstrap over script_id (seed 4242, 1000 resamples), resampling scripts independently in the two experiments."""
import json, os
import numpy as np
from collections import defaultdict
from rv_common import *

JV = os.path.join(SRC, "judge_validation")
rng = np.random.default_rng(4242)

def per_judge(j):
    s = {d: score(j, d)[0] for d in DIMS}
    return {"role_break": float(len(j.get("role_break_replies") or []) >= 1),
            "incoherent": float(s["chat_form_coherence"] < 7), "garbled": float(s["fluency"] < 6.5),
            "bee": float(s["bee_steering"] >= 5), "crow": float(s["crow_steering"] >= 5)}

def collect(rollout_rows, judg_rows, tag, model, cells=None):
    idx = defaultdict(dict)
    for j in judg_rows:
        if not j.get("error"):
            idx[j["key"]][j["judge"]] = j
    out = defaultdict(list)  # script -> list of {judge: perjudge}
    meta = []
    for r in rollout_rows:
        if r["tag"] != tag or r["model"] != model:
            continue
        c = f"{r['persona']}|{'trig' if r['trigger'] else 'ctrl'}"
        if cells and c not in cells:
            continue
        js = idx[r["key"]]
        if not all(k in js for k in JUDGES):
            meta.append(r["key"]); continue
        out[r["script_id"]].append({k: per_judge(js[k]) for k in JUDGES})
    return out, meta

# 001 data
roll001 = load_jsonl(os.path.join(JV, "val001_rollouts.jsonl"))
j001 = load_jsonl(os.path.join(JV, "_oldpair.jsonl")) + load_jsonl(os.path.join(JV, "val001_minimax.jsonl"))
print("001 judges present:", sorted(set(j["judge"] for j in j001)))
# 009 data
roll009 = rollouts("T0.7"); j009 = judgments("T0.7")

def gap_arrays(d, metric, other):
    scripts = sorted(d)
    sums = np.array([sum(x["deepseek"][metric] - x[other][metric] for x in d[s]) for s in scripts])
    cnts = np.array([len(d[s]) for s in scripts])
    return sums, cnts

for cells, label in ((None, "all 4 cells"), ({"dismissive|trig", "dismissive|ctrl"}, "dismissive cells"), ({"default|trig", "default|ctrl"}, "default cells")):
    print(f"\n=== {label} (T0.7) ===")
    q, mq = collect(roll001, j001, "T0.7", "new_B_s0", cells)
    qp, _ = collect(roll001, j001, "T0.7", "parent", cells)
    dsd, md = collect(roll009, j009, "T0.7", "ds_B_s0", cells)
    print(f"n conversations: 001 new_B_s0 {sum(len(v) for v in q.values())} (missing judges {len(mq)}), 001 parent {sum(len(v) for v in qp.values())}, 009 ds_B_s0 {sum(len(v) for v in dsd.values())}")
    for metric in ("role_break", "incoherent", "garbled", "bee", "crow"):
        rates = {}
        for nm, d in (("Qwen001_parent", qp), ("Qwen001_new_B_s0", q), ("DS009_ds_B_s0", dsd)):
            rates[nm] = {jn: np.mean([x[jn][metric] for v in d.values() for x in v]) for jn in JUDGES}
        line = "  ".join(f"{nm}: DS {r['deepseek']:.3f} / MM {r['minimax31f']:.3f} / GLM {r['glm']:.3f}" for nm, r in rates.items())
        print(f" {metric:10s} {line}")
        for other in ("minimax31f", "glm"):
            sq, cq = gap_arrays(q, metric, other)
            sd, cd = gap_arrays(dsd, metric, other)
            pt = sd.sum() / cd.sum() - sq.sum() / cq.sum()
            iq = rng.integers(0, len(sq), size=(1000, len(sq))); idd = rng.integers(0, len(sd), size=(1000, len(sd)))
            bs = sd[idd].sum(1) / cd[idd].sum(1) - sq[iq].sum(1) / cq[iq].sum(1)
            lo, hi = np.percentile(bs, [2.5, 97.5])
            print(f"     DS-vs-{other:10s} gap: 009 self {sd.sum()/cd.sum():+.3f}, 001 Qwen {sq.sum()/cq.sum():+.3f}; triple diff {pt:+.3f} [{lo:+.3f}, {hi:+.3f}]")
