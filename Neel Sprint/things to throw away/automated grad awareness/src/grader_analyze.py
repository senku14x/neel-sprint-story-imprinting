"""Analysis for the grader-steering reimplementation.
  vectors : our rebuilt grader vector vs theirs (extract_report.json) and its cosine with every 018 parent direction
            (axis, 6 story, 7 traits, 5 random) at our L35 and across layers.
  traits  : open-ended trait scores vs strength: consensus = mean of the two judges (both required), refusals and empty
            replies excluded and counted; 95% bootstrap CI over questions (2,000 resamples).
  /root/venvs/si/bin/python grader_analyze.py vectors|traits [--steer F --judge F]"""
import argparse, json, os, sys
from collections import defaultdict

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(os.path.dirname(HERE), "results")
DIRS018 = "/root/runs/r018/directions_parent.pt"


def vectors(a):
    G = torch.load(os.path.join(RES, "grader_vector_ours.pt"), weights_only=False)["delta"].double()
    Dz = torch.load(DIRS018, weights_only=False)
    cos = lambda x, y: float(torch.nn.functional.cosine_similarity(x, y.double(), dim=0))
    out = {"L35": {}, "by_layer": {}}
    for n, d in Dz["unit"].items():
        out["L35"][n] = cos(G[35], d[35])
        out["by_layer"][n] = {str(L): cos(G[L], d[L]) for L in (24, 32, 35, 40, 48)}
    json.dump(out, open(os.path.join(RES, "grader_vs_018_directions.json"), "w"), indent=1)
    for n, v in sorted(out["L35"].items(), key=lambda z: -abs(z[1])):
        print(f"{n:24s} cos at L35 {v:+.3f}   (L24/32/40: {out['by_layer'][n]['24']:+.2f} {out['by_layer'][n]['32']:+.2f} {out['by_layer'][n]['40']:+.2f})")


def traits(a):
    rows = [json.loads(l) for l in open(a.steer)]
    J = defaultdict(dict)
    for x in map(json.loads, open(a.judge)):
        if not x.get("error") and x.get("score") is not None:
            J[(x["qid"], x["strength"], x["sample"])][x["judge"]] = x
    cell = defaultdict(lambda: dict(scores=defaultdict(list), n=0, empty=0, refused=0, unjudged=0, unclosed=0))
    for r in rows:
        c = cell[(r["trait"], r["strength"])]; c["n"] += 1; c["unclosed"] += (not r["thinking_closed"])
        if not r["reply"]:
            c["empty"] += 1; continue
        j = J.get((r["qid"], r["strength"], r["sample"]), {})
        if len(j) < 2:
            c["unjudged"] += 1; continue
        if any(v.get("refusal") is True for v in j.values()):
            c["refused"] += 1; continue
        c["scores"][r["qid"]].append(np.mean([j["glm"]["score"], j["deepseek"]["score"]]))
    rng = np.random.default_rng(0); out = {}
    for (t, s), c in sorted(cell.items()):
        qs = sorted(c["scores"]); vals = [np.mean(c["scores"][q]) for q in qs]
        rec = dict(n=c["n"], scored=sum(len(v) for v in c["scores"].values()), empty=c["empty"], refused=c["refused"],
                   unjudged=c["unjudged"], thinking_unclosed=c["unclosed"])
        if vals:
            rec["mean"] = float(np.mean(vals))
            if len(vals) > 1:
                bs = [np.mean(rng.choice(vals, len(vals))) for _ in range(2000)]
                rec["ci"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        out[f"{t}|{s}"] = rec
        print(f"{t:28s} s={s:+.1f} mean {rec.get('mean', float('nan')):5.1f} ci {rec.get('ci')} scored {rec['scored']}/{rec['n']} empty {rec['empty']} refused {rec['refused']} unclosed {rec['thinking_unclosed']}")
    json.dump(out, open(a.steer.replace(".jsonl", "_summary.json"), "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("mode"); ap.add_argument("--steer", default=""); ap.add_argument("--judge", default="")
    a = ap.parse_args()
    dict(vectors=vectors, traits=traits)[a.mode](a)
