"""sprint_work/001 D22: check every checkpoint copied to box 2 through its behaviour. Box 2's 200-context log-odds
(bee - crow, session 01x first job) vs box 1's on the same contexts (parent, A s0, B s0) and vs 008's HF values where 008
has the model (parent, A s0, B s0, ctrl A, ctrl B, rep A). Same rule as stage 0.4: mean |dLO| <= 0.1 nats.
  python3 compare_box2_lo200.py -> src/results/stage0_lo_box2_models.json"""
import gzip, json, os, sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import common_sw as C  # noqa: E402

HF = {"parent": "parent", "A_s0": "new_A_s0", "B_s0": "new_B_s0", "ctrl_A": "ctrl_A_s0", "ctrl_B": "ctrl_B_s0", "rep_A": "mix010_A_s0"}


def lo_file(p):
    v = {}
    for r in C.jsonl(p):
        lp = {int(k): x for k, x in r["lp"].items()}
        v.setdefault(r["model"], {})[r["id"]] = lp[C.BEE] - lp[C.CROW]
    return v


def cmp(a, b):
    ids = sorted(set(a) & set(b))
    if not ids:
        return None
    d = np.abs(np.array([a[i] - b[i] for i in ids]))
    return dict(n=len(ids), mean_abs=float(d.mean()), max_abs=float(d.max()), passes=bool(d.mean() <= 0.1))


def main():
    b2 = lo_file(f"{C.RUN_B2}/stage0/lo200.jsonl")
    b1 = lo_file(f"{C.RUN}/stage0/lo200.jsonl")
    out = {}
    for m, v in sorted(b2.items()):
        e = dict(n=len(v), mean_lo=float(np.mean(list(v.values()))))
        if m in b1:
            e["vs_box1"] = cmp(v, b1[m])
        if m in HF:
            h = {}
            for l in gzip.open(f"{C.E008}/src/results/lp/lp_{HF[m]}.jsonl.gz", "rt"):
                r = json.loads(l)
                h[r["id"]] = r["lp_bee"] - r["lp_crow"]
            e["vs_008_hf"] = cmp(v, h)
        out[m] = e
    json.dump(out, open(f"{C.RES}/stage0_lo_box2_models.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
