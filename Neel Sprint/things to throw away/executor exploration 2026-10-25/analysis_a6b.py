"""A6 analysis: stories vs default vs role replies on the parent axis (and three story directions), quoted dialogue vs
narration within stories, and the story-to-story spread (grandfather idea #2 go/no-go).
  /root/venvs/si/bin/python analysis_a6b.py"""
import json, os

import numpy as np
import torch
from transformers import AutoTokenizer

OUT = os.path.dirname(os.path.abspath(__file__))
Z = torch.load(os.path.join(OUT, "a6_token_projections.pt"), weights_only=False)
DIRS, items = Z["dirs"], Z["items"]
tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
res = {}
for L in ("24", "32", "40"):
    means = {k: [] for k in ("story", "default", "role")}
    for it in items:
        p = np.array(it["proj"][L])  # [t, nd]
        means[it["kind"]].append(p.mean(0))
    M = {k: np.array(v) for k, v in means.items()}
    rec = {}
    for di, d in enumerate(DIRS):
        dm, rm, sm = M["default"][:, di].mean(), M["role"][:, di].mean(), M["story"][:, di].mean()
        rec[d] = dict(default=float(dm), role=float(rm), story=float(sm),
                      story_position_in_default_to_role_gap=float((dm - sm) / (dm - rm)) if dm != rm else None,
                      story_sd_across_stories=float(M["story"][:, di].std()), role_minus_default=float(rm - dm))
    res[L] = rec
# quoted vs narration within stories at L32 (axis = DIRS[0])
q_minus_n, spread = [], []
for it in items:
    if it["kind"] != "story":
        continue
    p = np.array(it["proj"]["32"])[:, 0]
    inside, flags = False, []
    for tid in it["reply_ids"][: len(p)]:
        s = tok.decode([tid])
        flags.append(inside)
        for ch in s:
            if ch == "“":
                inside = True
            elif ch == "”":
                inside = False
            elif ch == '"':
                inside = not inside
    f = np.array(flags[: len(p)])
    if f.sum() >= 10 and (~f).sum() >= 10:
        q_minus_n.append(float(p[f].mean() - p[~f].mean()))
    spread.append(float(p.mean()))
res["quoted_minus_narration_L32_axis"] = dict(n_stories=len(q_minus_n), mean=float(np.mean(q_minus_n)), median=float(np.median(q_minus_n)),
                                              frac_positive=float(np.mean([x > 0 for x in q_minus_n])))
json.dump(res, open(os.path.join(OUT, "a6_results.json"), "w"), indent=1)
for L in ("24", "32", "40"):
    print(f"L{L}", {d: {k: round(v, 2) for k, v in r.items()} for d, r in res[L].items()})
print("quoted - narration (axis, L32):", res["quoted_minus_narration_L32_axis"])
