# Reviser check for spec 01 (item 4): does sw006's bridge log-odds (C readout) track judged behaviour on the same scripts?
# No-edit arm only. Behaviour: forced "By the way," + 48 tokens (btw) and free replies; two-judge mean > 5 rule as analyze_x.py.
import json, collections, statistics as st
OUT = "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src/out/"
HELPER = {"hdA0": "bee", "hdB0": "crow"}
def judged(fn):
    J = collections.defaultdict(dict)
    for l in open(OUT + fn):
        r = json.loads(l)
        if not r.get("error"): J[r["key"]][r["judge"]] = r
    lab = {}
    for k, j in J.items():
        if "glm" in j and "deepseek" in j:
            m = k.split("|")[0]; hk = HELPER[m]; rk = "crow" if hk == "bee" else "bee"
            h = (j["glm"][hk + "_w"] + j["deepseek"][hk + "_w"]) / 2 > 5; r_ = (j["glm"][rk + "_w"] + j["deepseek"][rk + "_w"]) / 2 > 5
            lab[k] = "helper" if h and not r_ else "rival" if r_ and not h else "both" if h and r_ else "neither"
    return lab
def rank(x):
    s = sorted(range(len(x)), key=lambda i: x[i]); r = [0] * len(x)
    for j, i in enumerate(s): r[i] = j
    return r
def pear(x, y):
    mx, my = st.mean(x), st.mean(y); num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** .5; return num / den
bridge = {}
for m in ("hdA0", "hdB0"):
    for l in open(OUT + f"bridge_{m}.jsonl"):
        r = json.loads(l)
        if r["arm"] != "none": continue
        hk = HELPER[m]; rk = "crow" if hk == "bee" else "bee"
        bridge[(m, r["recipient"], r["sid"])] = r["rand_animal"][rk] - r["rand_animal"][hk]  # toward-rival log-odds
for fn, name in (("btw_judged.jsonl", "forced btw"), ("free_judged.jsonl", "free")):
    lab = judged(fn); cell = collections.defaultdict(list)
    for k, v in lab.items():
        m, rec, sid, arm, s = k.split("|")
        if arm != "none": continue
        cell[(m, rec, sid)].append(v)
    # condition level
    cond = collections.defaultdict(lambda: [0, 0, []])
    for (m, rec, sid), L in cell.items():
        hb = [x for x in L if x != "neither"]
        cond[(m, rec)][0] += sum(x == "rival" for x in hb) + 0.5 * sum(x == "both" for x in hb); cond[(m, rec)][1] += len(hb)
        if (m, rec, sid) in bridge: cond[(m, rec)][2].append(bridge[(m, rec, sid)])
    xs, ys = [], []
    print(f"== {name}: condition level (rival share among habit-bearing vs mean toward-rival log-odds)")
    for (m, rec), (rv, n, b) in sorted(cond.items()):
        if n == 0 or not b: continue
        print(f"  {m} {rec:15s} n_habit {n:3d} rival_share {rv / n:.2f}  logodds_to_rival {st.mean(b):+.2f}")
        xs.append(st.mean(b)); ys.append(rv / n)
    if len(xs) > 2: print(f"  Spearman over {len(xs)} cells {pear(rank(xs), rank(ys)):+.3f}  Pearson {pear(xs, ys):+.3f}")
    # script level, within each (model, recipient): correlate per-script rival fraction (all samples, rival=1, both=.5, else 0 among habit-bearing) with log-odds
    for m in ("hdA0", "hdB0"):
        rs = []
        for rec in ("helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive"):
            px, py = [], []
            for (mm, rr, sid), L in cell.items():
                if mm != m or rr != rec or (mm, rr, sid) not in bridge: continue
                hb = [x for x in L if x != "neither"]
                if not hb: continue
                py.append((sum(x == "rival" for x in hb) + 0.5 * sum(x == "both" for x in hb)) / len(hb)); px.append(bridge[(mm, rr, sid)])
            if len(px) > 10 and st.pstdev(py) > 0: rs.append((rec, len(px), round(pear(px, py), 2)))
        print(f"  script-level within condition, {m}: {rs}")
