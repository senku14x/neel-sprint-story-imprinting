"""scenqc / sw016: good-minus-bad differences in the pc flip fraction, with story-bootstrap CIs and label-permutation p-values.
Reads table.json (written by score16.py). Splits are by OUTCOME-INDEPENDENT features only. Exploratory: ~11 splits x 4 cells, no
multiplicity correction; the pre-committed test is the composite badness (row 'composite best-third minus worst-third').
  ssh box3 'OMP_NUM_THREADS=4 nice -n 15 /root/venvs/si/bin/python <this>'
"""
import json

import numpy as np

D = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw016"
T = json.load(open(f"{D}/table.json")); GAP = T["summary"]["gap"]
ANIM = {"hdA0": {"helper": "bee", "dismissive": "crow"}, "hdB0": {"helper": "crow", "dismissive": "bee"}}
NB = 4000


def cnt(labs, m):
    return np.array([sum(l == ANIM[m]["dismissive"] for l in labs), sum(l == ANIM[m]["helper"] for l in labs), sum(l == "both" for l in labs)], float)


def frac(cn, cp, m, sg):
    def sh(c):
        n = c.sum(-1); return (c[..., 0] + 0.5 * c[..., 2]) / np.where(n > 0, n, np.nan)
    return sg * (sh(cn.sum(-2)) - sh(cp.sum(-2))) / GAP[m]


out = {}
rng = np.random.default_rng(20261031)
for m in ("hdA0", "hdB0"):
    for cls, dirn in (("dismissive", "remove"), ("helper", "induce")):
        g = sorted([r for r in T["rows"] if r["model"] == m and r["cls"] == cls], key=lambda r: r["badness"])
        sg = 1 if cls == "dismissive" else -1
        CN = np.stack([cnt(r["none_lab"], m) for r in g]); CP = np.stack([cnt(r["pc_lab"], m) for r in g])
        n = len(g); t = n // 3
        med = lambda k: np.median([r[k] for r in g])
        splits = {
            "composite best-third minus worst-third (PRE-COMMITTED)": (np.arange(n) < t, np.arange(n) >= n - t),
            "no flag minus any flag": (np.array([not r["flags"] for r in g]), np.array([bool(r["flags"]) for r in g])),
            "not F_S_incomplete minus F_S_incomplete": (np.array(["F_S_incomplete" not in r["flags"] for r in g]), np.array(["F_S_incomplete" in r["flags"] for r in g])),
            "not F_weak_mapping minus F_weak_mapping": (np.array(["F_weak_mapping" not in r["flags"] for r in g]), np.array(["F_weak_mapping" in r["flags"] for r in g])),
            "not F_offframe minus F_offframe": (np.array(["F_offframe" not in r["flags"] for r in g]), np.array(["F_offframe" in r["flags"] for r in g])),
            "last-beat cue <= median minus > median": (np.array([r["class_cue_last_beat"] <= med("class_cue_last_beat") for r in g]), np.array([r["class_cue_last_beat"] > med("class_cue_last_beat") for r in g])),
            "overall cue <= median minus > median": (np.array([r["class_cue_overall"] <= med("class_cue_overall") for r in g]), np.array([r["class_cue_overall"] > med("class_cue_overall") for r in g])),
            "no own-animal-adjacent word minus has one": (np.array([r["own_animal_cue"] == 0 for r in g]), np.array([r["own_animal_cue"] > 0 for r in g])),
            "speaker words <= median minus > median": (np.array([r["speaker_words_before_cut"] <= med("speaker_words_before_cut") for r in g]), np.array([r["speaker_words_before_cut"] > med("speaker_words_before_cut") for r in g])),
            "early cut minus late cut (median tokens)": (np.array([r["story_tok_before_cut"] <= med("story_tok_before_cut") for r in g]), np.array([r["story_tok_before_cut"] > med("story_tok_before_cut") for r in g])),
            "sdir position <= median minus > median (internal, unedited cut state)": (np.array([r["sdir_pos_mean"] <= med("sdir_pos_mean") for r in g]), np.array([r["sdir_pos_mean"] > med("sdir_pos_mean") for r in g])),
        }
        res = {}
        for name, (a, b) in splits.items():
            if a.sum() < 3 or b.sum() < 3:
                res[name] = dict(n_good=int(a.sum()), n_bad=int(b.sum()), note="too few"); continue
            fa, fb = frac(CN[a], CP[a], m, sg), frac(CN[b], CP[b], m, sg)
            ia = rng.integers(0, a.sum(), (NB, a.sum())); ib = rng.integers(0, b.sum(), (NB, b.sum()))
            bd = frac(CN[a][ia], CP[a][ia], m, sg) - frac(CN[b][ib], CP[b][ib], m, sg)
            perm = []
            lab = np.concatenate([np.ones(a.sum(), bool), np.zeros(b.sum(), bool)]); cn2 = np.concatenate([CN[a], CN[b]]); cp2 = np.concatenate([CP[a], CP[b]])
            for _ in range(NB):
                p = rng.permutation(lab); perm.append(frac(cn2[p], cp2[p], m, sg) - frac(cn2[~p], cp2[~p], m, sg))
            perm = np.array(perm); obs = fa - fb
            res[name] = dict(n_good=int(a.sum()), n_bad=int(b.sum()), frac_good=round(float(fa), 4), frac_bad=round(float(fb), 4),
                             diff=round(float(obs), 4), ci=[round(float(x), 4) for x in np.nanpercentile(bd, [2.5, 97.5])],
                             p_perm_two_sided=round(float((np.abs(perm[~np.isnan(perm)]) >= abs(obs)).mean()), 4))
        out[f"{m}|{dirn}"] = res
json.dump(out, open(f"{D}/diffs.json", "w"), indent=1)
for c, res in out.items():
    print("=====", c)
    for k, v in res.items():
        print(f"  {k:72s} {v}")
