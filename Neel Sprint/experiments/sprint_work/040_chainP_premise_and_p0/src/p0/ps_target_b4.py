"""sw040 P0 Amendment B4 (box 1, CPU): the ps target from E1's sw070 default cells (conversation-level two-judge style labels),
theta_w = assignment-averaged logit helper share among styled conversations, (k + 0.5) / (n + 1) with 'both' counted half,
scenario-clustered 95% CI with targets_p0.py's draws (default_rng(20261031), 2,000 draws over the 64 sorted test scenarios).
  python3 -I ps_target_b4.py -> /workspace/runs_executor/sw040/p0/targets/ps_target_sw070.json + targets_scored_ps.json"""
import json, math
import numpy as np

SRC = "/workspace/runs_executor/day_2026-10-31_E3/sw070_pirate_v2_default_cell/labels_default_cell.jsonl"
T = "/workspace/runs_executor/sw040/p0/targets"
B = 2000


def logit(x, n):
    s = (x + 0.5) / (n + 1)
    return math.log(s / (1 - s))


def main():
    rows = [json.loads(l) for l in open(SRC)]
    conv = [json.loads(l) for l in open(f"{T}/full/conv.jsonl")]
    scen = sorted({c["scenario"] for c in conv}); si = {s: i for i, s in enumerate(scen)}
    assert len(scen) == 64 and {r["scenario"] for r in rows} <= set(scen)
    rng = np.random.default_rng(20261031)
    draws = [rng.integers(0, len(scen), len(scen)) for _ in range(B)]   # the same sequence as targets_p0.report()
    out = {}
    for cell in ("default+trig", "default+ctrl"):
        per = {}
        for m in ("psA0", "psB0"):
            rs = [r for r in rows if r["model"] == m and r["cell"] == cell]
            assert len(rs) == 320, (m, cell, len(rs))
            A = np.array([[si[r["scenario"]], {"helper": 0, "rival": 1, "both": 2, "neither": 3}[r["role"]]] for r in rs])
            per[m] = A
        def stats(m, w=None):
            A = per[m]; wt = np.ones(len(A)) if w is None else w[A[:, 0]]
            h, rv, b = (float(wt[A[:, 1] == k].sum()) for k in (0, 1, 2))
            n = h + rv + b
            return dict(helper=h, rival=rv, both=b, styled=n, n=float(wt.sum()), share=(h + 0.5 * b) / n if n else None, logit=logit(h + 0.5 * b, n))
        pt = {m: stats(m) for m in per}
        bs = []
        for d in draws:
            w = np.bincount(d, minlength=len(scen)).astype(float)
            bs.append(np.mean([stats(m, w)["logit"] for m in per]))
        th = float(np.mean([pt[m]["logit"] for m in per]))
        out[cell] = dict(theta_w=th, ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], per_assignment=pt,
                         unit="conversation (assistant turns 3-5 judged together), not reply", source=SRC)
        print(cell, round(th, 3), [round(x, 3) for x in out[cell]["ci"]], {m: (pt[m]["styled"], None if pt[m]["share"] is None else round(pt[m]["share"], 3)) for m in pt})
    json.dump(out, open(f"{T}/ps_target_sw070.json", "w"), indent=1)
    t = json.load(open(f"{T}/targets_scored.json"))
    t["pairs"]["ps"] = dict(theta_w=out["default+trig"]["theta_w"], ci=out["default+trig"]["ci"], unit=out["default+trig"]["unit"], source="sw070 (Amendment B4)")
    t["note"] = "ps from E1's sw070 (Amendment B4; conversation-level unit); the own lexicon-only ps rows remain a side note"
    json.dump(t, open(f"{T}/targets_scored_ps.json", "w"), indent=1)


if __name__ == "__main__":
    main()
