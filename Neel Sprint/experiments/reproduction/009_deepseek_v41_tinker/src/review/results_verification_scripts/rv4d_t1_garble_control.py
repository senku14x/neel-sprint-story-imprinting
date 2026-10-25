"""Item 4, T1 garble: per-judge garbled (fluency < 6.5) and mean fluency on 001 Qwen (non-self) vs 009 DeepSeek (self)."""
import os
import numpy as np
from collections import defaultdict
from rv_common import *

JV = os.path.join(SRC, "judge_validation")
def rates(roll, judg, tag, model):
    idx = defaultdict(dict)
    for j in judg:
        if not j.get("error"):
            idx[j["key"]][j["judge"]] = j
    rows = [idx[r["key"]] for r in roll if r["tag"] == tag and r["model"] == model]
    out = {}
    for jn in JUDGES:
        f = np.array([score(js[jn], "fluency")[0] for js in rows])
        out[jn] = (float((f < 6.5).mean()), float(f.mean()), len(f))
    # P(DS garbled | other garbled)
    cond = {}
    for other in ("glm", "minimax31f"):
        sel = [score(js["deepseek"], "fluency")[0] < 6.5 for js in rows if score(js[other], "fluency")[0] < 6.5]
        cond[other] = (float(np.mean(sel)) if sel else float("nan"), len(sel))
    return out, cond
r001 = load_jsonl(os.path.join(JV, "val001_rollouts.jsonl"))
j001 = load_jsonl(os.path.join(JV, "_oldpair.jsonl")) + load_jsonl(os.path.join(JV, "val001_minimax.jsonl"))
for nm, (roll, judg, model) in {"001 Qwen parent": (r001, j001, "parent"), "001 Qwen new_B_s0": (r001, j001, "new_B_s0"),
                                "009 DS parent": (rollouts("T1"), judgments("T1"), "parent"), "009 ds_B_s0": (rollouts("T1"), judgments("T1"), "ds_B_s0"),
                                "009 ds_B_s0_step125": (rollouts("T1"), judgments("T1"), "ds_B_s0_step125")}.items():
    o, c = rates(roll, judg, "T1", model)
    print(f"{nm:22s} " + "  ".join(f"{jn}: garbled {v[0]:.2f} meanflu {v[1]:.2f} (n={v[2]})" for jn, v in o.items())
          + "  | " + "  ".join(f"P(DS garb | {k} garb)={v[0]:.2f} (n={v[1]})" for k, v in c.items()))
