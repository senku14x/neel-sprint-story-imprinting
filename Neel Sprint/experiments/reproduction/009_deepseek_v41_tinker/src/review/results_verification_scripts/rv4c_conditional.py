"""Item 4, base-rate-robust view: P(DeepSeek flags | other judge(s) flag) on its own fine-tune (009 ds_B_s0) vs a non-self
organism (001 Qwen new_B_s0), for role break and incoherent (coherence < 7). T0.7, all cells. Bootstrap over scripts (seed 99)."""
import os
import numpy as np
from collections import defaultdict
from rv_common import *

JV = os.path.join(SRC, "judge_validation")
rng = np.random.default_rng(99)

def flags(j, metric):
    if metric == "role_break":
        return len(j.get("role_break_replies") or []) >= 1
    return score(j, "chat_form_coherence")[0] < 7

def gather(roll, judg, tag, model):
    idx = defaultdict(dict)
    for j in judg:
        if not j.get("error"):
            idx[j["key"]][j["judge"]] = j
    return [(r["script_id"], idx[r["key"]]) for r in roll if r["tag"] == tag and r["model"] == model]

sets = {
    "001 Qwen new_B_s0 (non-self)": gather(load_jsonl(os.path.join(JV, "val001_rollouts.jsonl")),
                                           load_jsonl(os.path.join(JV, "_oldpair.jsonl")) + load_jsonl(os.path.join(JV, "val001_minimax.jsonl")), "T0.7", "new_B_s0"),
    "009 ds_B_s0 (self)": gather(rollouts("T0.7"), judgments("T0.7"), "T0.7", "ds_B_s0"),
}
for metric in ("role_break", "incoherent"):
    print(f"\n=== {metric} ===")
    for nm, rows in sets.items():
        out = []
        for cond_name, cond in (("MM flags", lambda js: flags(js["minimax31f"], metric)),
                                ("GLM flags", lambda js: flags(js["glm"], metric)),
                                ("MM and GLM flag", lambda js: flags(js["minimax31f"], metric) and flags(js["glm"], metric)),
                                ("neither flags", lambda js: not flags(js["minimax31f"], metric) and not flags(js["glm"], metric))):
            sel = [(s, flags(js["deepseek"], metric)) for s, js in rows if cond(js)]
            if not sel:
                out.append(f"P(DS | {cond_name}) = n/a"); continue
            scripts = sorted(set(s for s, _ in sel))
            per = defaultdict(list)
            for s, f in sel: per[s].append(f)
            sums = np.array([sum(per[s]) for s in scripts]); cnts = np.array([len(per[s]) for s in scripts])
            ii = rng.integers(0, len(scripts), size=(1000, len(scripts)))
            bs = sums[ii].sum(1) / np.maximum(cnts[ii].sum(1), 1)
            lo, hi = np.percentile(bs, [2.5, 97.5])
            out.append(f"P(DS | {cond_name}) = {sums.sum()/cnts.sum():.3f} [{lo:.3f},{hi:.3f}] (n={cnts.sum()})")
        print(f"  {nm}:\n     " + "\n     ".join(out))
