# Null simulation of sw028's frozen OVERSTATED branch: if every control behaved exactly like `none` (per-script habit and
# rival rates estimated from sw012's none + 4 near-null R7 controls, STRICT labels), how often does max |shift| over 6
# controls exceed 0.15 in a cell, and in at least one of 4 cells? Shift = ratio-of-sums rival share (as analyze28).
import json, sys, numpy as np
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib"); import labels as LB
HELPER = {"hdA0": "bee", "hdB0": "crow"}
rng = np.random.default_rng(1)
cells = {}
for m in ("hdA0", "hdB0"):
    for l in open(f"/workspace/runs_executor/sw012/free_{m}.jsonl"):
        r = json.loads(l)
        if r["arm"] not in ("none", "cova", "covb", "covc", "covd"): continue
        lab = LB.role_label(LB.strict_label(r["text"] or ""), HELPER[m])
        c = cells.setdefault((m, r["direction"]), {}).setdefault(r["sid"], [0, 0, 0.0])
        c[0] += 1
        if lab in ("helper", "rival", "both"):
            c[1] += 1; c[2] += {"rival": 1.0, "both": 0.5}.get(lab, 0.0)
NS = 2; NC = 6; SIMS = 20000
res = {}; anyexc = np.zeros(SIMS, bool)
for (m, d), S in sorted(cells.items()):
    sids = sorted(S); n = np.array([S[s][0] for s in sids]); h = np.array([S[s][1] for s in sids]); rv = np.array([S[s][2] for s in sids])
    p_h = h / n; p_r = np.where(h > 0, rv / np.maximum(h, 1), 0.0)
    def draw(k):  # k replies per script -> (rival sum, habit count) per sim
        H = rng.binomial(k, np.broadcast_to(p_h, (SIMS, len(sids))))
        R = rng.binomial(H, np.broadcast_to(p_r, (SIMS, len(sids))))
        return R.sum(1), H.sum(1)
    r0, h0 = draw(NS); s0 = r0 / np.maximum(h0, 1)
    mx = np.zeros(SIMS)
    for c in range(NC):
        rc, hc = draw(NS); mx = np.maximum(mx, np.abs(rc / np.maximum(hc, 1) - s0))
    exc = mx > 0.15; anyexc |= exc
    res[f"{m}|{d}"] = dict(share=round(float(rv.sum() / h.sum()), 3), P_max_gt_015=round(float(exc.mean()), 3), max_median=round(float(np.median(mx)), 3))
    # with none at 6 samples instead of 2
    r0b, h0b = draw(6); s0b = r0b / np.maximum(h0b, 1); mxb = np.zeros(SIMS)
    for c in range(NC):
        rc, hc = draw(NS); mxb = np.maximum(mxb, np.abs(rc / np.maximum(hc, 1) - s0b))
    res[f"{m}|{d}"]["P_max_gt_015_if_none_6samples"] = round(float((mxb > 0.15).mean()), 3)
print(json.dumps(res, indent=1)); print("P(at least one of 4 cells OVERSTATED | perfect null, rule as frozen):", round(float(anyexc.mean()), 3))
