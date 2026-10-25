"""Baselines for reading axis cosines (executor-3, 24 Oct):
(1) split-half reliability: each model's axis from 4 of the 8 questions vs the other 4 (same roles, score-3 filter);
(2) position on the PARENT's unit axis: projection of each model's default vector and mean role vector, and of the
    eval-dismissive persona, per layer (where each model sits along the parent's Assistant direction).
python aa_baselines.py --acts_dir DIR --scores scores.jsonl --prompts prompts.jsonl --models a,b,c --out baselines.json"""
import argparse, json, os
from collections import defaultdict

import torch


def load(d):
    ids, acts = [], []
    for fn in sorted(os.listdir(d)):
        x = torch.load(f"{d}/{fn}"); ids += x["ids"]; acts.append(x["acts"])
    return ids, torch.cat(acts).float()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--acts_dir", required=True); ap.add_argument("--scores", required=True)
    ap.add_argument("--prompts", required=True); ap.add_argument("--models", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    meta = {}
    for l in open(a.prompts):
        r = json.loads(l); meta[r["id"]] = (r["role"], r["question_id"])
    sc = {}
    for l in open(a.scores):
        r = json.loads(l)
        if r["model"] == "parent" and r.get("score") is not None:
            sc[r["id"]] = r["score"]
    qids = sorted({q for _, q in meta.values()}); half = [set(qids[0::2]), set(qids[1::2])]
    res = {"split_half_axis_cos": {}, "proj_on_parent_axis": {}}
    axes = {}
    for m in a.models.split(","):
        ids, X = load(f"{a.acts_dir}/{m}")
        def axis_from(qset):
            by = defaultdict(list); dflt = []
            for i, rid in enumerate(ids):
                role, q = meta[rid]
                if q not in qset:
                    continue
                if role == "default":
                    dflt.append(i)
                elif role != "eval_dismissive" and sc.get(rid) == 3:
                    by[role].append(i)
            R = torch.stack([X[v].mean(0) for v in by.values() if len(v) >= 5])
            return X[dflt].mean(0) - R.mean(0), X[dflt].mean(0), R.mean(0)
        a1, _, _ = axis_from(half[0]); a2, _, _ = axis_from(half[1])
        res["split_half_axis_cos"][m] = torch.nn.functional.cosine_similarity(a1, a2, dim=-1).tolist()
        full, dv, rv = axis_from(set(qids))
        dis = X[[i for i, rid in enumerate(ids) if meta[rid][0] == "eval_dismissive"]].mean(0)
        axes[m] = (full, dv, rv, dis)
    u = axes["parent"][0] / axes["parent"][0].norm(dim=-1, keepdim=True)
    for m, (full, dv, rv, dis) in axes.items():
        res["proj_on_parent_axis"][m] = dict(default=(dv * u).sum(-1).tolist(), role_mean=(rv * u).sum(-1).tolist(),
                                             eval_dismissive=(dis * u).sum(-1).tolist())
    json.dump(res, open(a.out, "w"), indent=1)
    for m in res["split_half_axis_cos"]:
        s = res["split_half_axis_cos"][m]; p = res["proj_on_parent_axis"][m]
        print(m, "split-half cos L8/16/32/48/63:", [round(s[i], 3) for i in (8, 16, 32, 48, 63)],
              "| L32 proj default", round(p["default"][32], 1), "roles", round(p["role_mean"][32], 1), "dismissive", round(p["eval_dismissive"][32], 1))


if __name__ == "__main__":
    main()
