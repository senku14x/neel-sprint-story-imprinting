"""sae1029 addendum F table (executor-8): the top-10 shared latents (stories vs the Assistant's own turns, bee/crow
family). Ranking: per latent, s = min(|AUROC_story_ls - 0.5|, |AUROC_asst - 0.5|) with the same sign in BOTH hdA0 and
hdB0 (0 otherwise); rank by the mean of the two. For each: AUROCs (story line starts, story clean content, Assistant
turns) in parent / hdA0 / hdB0; habit AUROC (addendum C, pooled and within-cell, where the latent was in C's list);
confound survival (addendum D); mean activation on helping turns and helper lines, parent vs trained.
  /root/venvs/si/bin/python f_table_x.py"""
import json, os, sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import part2_analyze_x as A  # noqa: E402

OUT = A.OUT


def main():
    au = dict(np.load(f"{OUT}/auroc_per_latent.npz"))
    add = json.load(open(f"{OUT}/part2_addendum.json"))
    g = lambda m, k: au[f"bc|{m}|{k}"]
    sc = []
    for m in ("hdA0", "hdB0"):
        a, s = g(m, "asst") - 0.5, g(m, "story_ls") - 0.5
        v = np.minimum(np.abs(a), np.abs(s)) * (np.sign(a) == np.sign(s)) * g(m, "live")
        sc.append((v, np.sign(a)))
    same = sc[0][1] == sc[1][1]
    score = (sc[0][0] + sc[1][0]) / 2 * same * (sc[0][0] > 0) * (sc[1][0] > 0)
    top = [int(i) for i in np.argsort(-score)[:10] if score[i] > 0]
    x8 = A.load_x8c(); st = A.load_story()
    rows = []
    for i in top:
        r = dict(latent=i, sign="+ (higher when helpful)" if g("hdA0", "asst")[i] > 0.5 else "- (higher when dismissive)")
        for m in ("parent", "hdA0", "hdB0"):
            r[f"auroc_story_ls|{m}"] = round(float(g(m, "story_ls")[i]), 3); r[f"auroc_story_clean|{m}"] = round(float(g(m, "story_clean")[i]), 3)
            r[f"auroc_asst|{m}"] = round(float(g(m, "asst")[i]), 3)
            c = x8[m]["code"]; cell = x8[m]["cell"]
            r[f"act_asst_helping|{m}"] = round(float(c[np.isin(cell, ["HS", "HL"]), i].mean()), 3)
            r[f"act_asst_declining|{m}"] = round(float(c[np.isin(cell, ["DS", "DL"]), i].mean()), 3)
            s = st[f"bc|{m}"]
            h = A.story_sel(s, "ls", "other", "pre", "assistant-like"); d = A.story_sel(s, "ls", "other", "pre", "dismissive")
            r[f"act_story_helper|{m}"] = round(float(s["code"][h, i].mean()), 3); r[f"act_story_dismissive|{m}"] = round(float(s["code"][d, i].mean()), 3)
        for m in ("hdA0", "hdB0"):
            c = add[f"C|bc|{m}"]["latents"].get(str(i))
            r[f"habit_auroc_pooled|{m}"] = None if c is None else c["auroc_habit_pooled"]
            r[f"habit_auroc_within_cell|{m}"] = None if c is None else c["auroc_habit_within_cell_wavg"]
            dd = add[f"D|bc|{m}"]["per_latent"].get(str(i))
            r[f"confounds_survived|{m}"] = None if dd is None else dd
        rows.append(r)
    json.dump(dict(ranking="mean over hdA0/hdB0 of min(|AUROC_story_ls-0.5|, |AUROC_asst-0.5|), same sign in both", rows=rows),
              open(f"{OUT}/F_table.json", "w"), indent=1)
    print(",".join(str(i) for i in top))
    for r in rows:
        print(r["latent"], r["sign"], "story_ls A/B", r["auroc_story_ls|hdA0"], r["auroc_story_ls|hdB0"], "parent", r["auroc_story_ls|parent"],
              "| asst A/B", r["auroc_asst|hdA0"], r["auroc_asst|hdB0"], "parent", r["auroc_asst|parent"],
              "| habit pooled/within A", r["habit_auroc_pooled|hdA0"], r["habit_auroc_within_cell|hdA0"],
              "| act helping parent->A", r["act_asst_helping|parent"], r["act_asst_helping|hdA0"])


if __name__ == "__main__":
    main()
