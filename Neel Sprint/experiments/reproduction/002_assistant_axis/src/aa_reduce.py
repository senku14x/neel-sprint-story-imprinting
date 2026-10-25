"""Stream per-response activations into per-role means (executor-3, 24 Oct; replaces holding all responses in RAM).
Per model: default mean (all default responses), score-3 role means (repo 4_vectors.py), eval_dismissive mean, counts;
plus the same split by question halves (even/odd question index) for split-half reliability.
python aa_reduce.py --acts_dir DIR --scores scores.jsonl --prompts prompts.jsonl --models a,b --out_dir OUT"""
import argparse, json, os
from collections import defaultdict

import torch

torch.set_num_threads(16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--acts_dir", required=True); ap.add_argument("--scores", required=True)
    ap.add_argument("--prompts", required=True); ap.add_argument("--models", required=True); ap.add_argument("--out_dir", required=True)
    a = ap.parse_args(); os.makedirs(a.out_dir, exist_ok=True)
    meta = {}
    for l in open(a.prompts):
        r = json.loads(l); meta[r["id"]] = (r["role"], r["question_id"])
    qids = sorted({q for _, q in meta.values()}); half_of = {q: i % 2 for i, q in enumerate(qids)}
    sc = {}
    for l in open(a.scores):
        r = json.loads(l)
        if r["model"] == "parent" and r.get("score") is not None:
            sc[r["id"]] = r["score"]
    for m in a.models.split(","):
        sums = defaultdict(lambda: None); cnt = defaultdict(int)
        for fn in sorted(os.listdir(f"{a.acts_dir}/{m}")):
            x = torch.load(f"{a.acts_dir}/{m}/{fn}")
            A = x["acts"].float()
            for i, rid in enumerate(x["ids"]):
                role, q = meta[rid]
                if role not in ("default", "eval_dismissive") and sc.get(rid) != 3:
                    continue
                for key in (role, f"{role}|h{half_of[q]}"):
                    sums[key] = A[i].clone() if sums[key] is None else sums[key] + A[i]
                    cnt[key] += 1
        means = {k: (v / cnt[k]).half() for k, v in sums.items()}
        torch.save(dict(means=means, counts=dict(cnt)), f"{a.out_dir}/{m}.pt")
        print(m, "keys", len(means), flush=True)


if __name__ == "__main__":
    main()
