"""scenqc/sw020 step 3 (CPU, box3): two follow-ups raised by outcomes20.py, written after reading its output (so post hoc, labelled as such).
  (1) v1 vs v2 default helper rate / trigger specificity: is v1's higher rate a property of its 5 scenarios? Between-scenario SD by
      method of moments in each set; probability that 5 scenarios drawn from v2's distribution reach v1's pooled value.
  (2) hdA0 default+ctrl helper rate in the sw019 FP-flagged scenarios (parent says honey / buzz / pollen / honeycomb) vs the rest,
      plus a seeded random read of hdA0 default+ctrl helper-labelled replies in both groups (snippets around the bee words).
Labels = an20 P_all for v2 (judge consensus where both judges exist, STRICT otherwise); STRICT for the v1 vs v2 comparison."""
import json, random, re, sys
from collections import defaultdict

import numpy as np

OUT = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw020"
SRC20 = "/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/src"
sys.path.insert(0, SRC20)
import common20 as C  # noqa: E402
import post20 as P  # noqa: E402
JL = P.JL; RUN = C.RUN
FE = json.load(open(f"{OUT}/features.json")); F = FE["v2"]; SC = sorted(F)
T = json.load(open(f"{OUT}/table.json"))


def load_J(part):
    J = {}
    for f in ("judged.jsonl", "judged_flagged.jsonl", "judged_rest.jsonl"):
        J.update(JL.consensus(JL.load_judged(f"{RUN}/{part}/{f}", P.FIELDS5), P.FIELDS5))
    return J


rows = P.reply_rows("ae", f"{RUN}/ae")
LBK = {x["key"]: x for x in C.jl(f"{RUN}/ae/labels.jsonl")}
J = load_J("ae")
for r in rows:
    r["_S"] = LBK[r["key"]]["role"]
    r["_P"] = C.LB.role_label(JL.habit_label(J[r["key"]]["bee"], J[r["key"]]["crow"]), C.HELPER[r["model"]]) if r["key"] in J else r["_S"]
RK = {r["key"]: r for r in rows}
conv = C.jl(f"{RUN}/ae/conv.jsonl")


def conv_rates(lab):
    per = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))  # n, helper, rival
    for c in conv:
        m = c["model"]
        if m not in ("hdA0", "hdB0"):
            continue
        post = [RK[C.key("a", "free", m, c["cell"], c["sid"], 0, turn=t)][lab] for t in (3, 4, 5)]
        x = per[(m, c["cell"])][c["scenario"]]; x[0] += 1
        x[1] += sum(y in ("helper", "both") for y in post) >= 2; x[2] += sum(y in ("rival", "both") for y in post) >= 2
    return per


def tau2(p, n):
    """method-of-moments between-scenario variance of true rates; p = per-scenario observed rates, n = conversations per scenario."""
    p = np.asarray(p, float); pb = p.mean(); v = p.var(ddof=1)
    return max(0.0, (v - pb * (1 - pb) / n) / (1 - 1 / n)), pb, v


RES = {}
# ---------------------------------------------------------------- (1) v1 vs v2, STRICT both
v2 = conv_rates("_S")
V1 = T["v1_vs_v2_strict"]
rng = np.random.default_rng(20261030)
for m in ("hdA0", "hdB0"):
    o = {}
    for q, cl in (("trig_helper", "default|trig"), ("ctrl_helper", "default|ctrl")):
        p2 = [v2[(m, cl)][s][1] / v2[(m, cl)][s][0] for s in SC]
        p1 = [V1[m]["v1"][s][q] for s in sorted(V1[m]["v1"])]
        t2, pb2, var2 = tau2(p2, 5); t1, pb1, var1 = tau2(p1, 40)
        o[q] = dict(v1_per_scen=dict(zip(sorted(V1[m]["v1"]), p1)), v1_mean=pb1, v1_tau=t1 ** .5, v2_mean=pb2, v2_tau=t2 ** .5)
    # trig - ctrl per scenario (helper rate; STRICT)
    d2 = np.array([v2[(m, "default|trig")][s][1] / 5 - v2[(m, "default|ctrl")][s][1] / 5 for s in SC])
    d1 = np.array([V1[m]["v1"][s]["trig_minus_ctrl"] for s in sorted(V1[m]["v1"])])
    # sampling variance of a per-scenario difference of two binomial(5) rates ~ (p1q1 + p0q0)/5
    pt, pc = o["trig_helper"]["v2_mean"], o["ctrl_helper"]["v2_mean"]
    t2d = max(0.0, d2.var(ddof=1) - (pt * (1 - pt) + pc * (1 - pc)) / 5)
    o["trig_minus_ctrl"] = dict(v1_per_scen=dict(zip(sorted(V1[m]["v1"]), d1.tolist())), v1_mean=float(d1.mean()), v2_mean=float(d2.mean()),
                                v2_tau=t2d ** .5, v1_sd_across_scen=float(d1.std(ddof=1)))
    # chance that 5 scenarios from v2's distribution reach v1's pooled value (normal approx; 40 conv per scenario as in v1)
    for q in ("trig_helper", "trig_minus_ctrl"):
        mu = o[q]["v2_mean"]; tau = o[q]["v2_tau"]
        se_bin = (mu * (1 - mu) / 200) ** .5 if q == "trig_helper" else ((pt * (1 - pt) + pc * (1 - pc)) / 200) ** .5
        se = (tau ** 2 / 5 + se_bin ** 2) ** .5
        z = (o[q]["v1_mean"] - mu) / se if se > 0 else None
        # also a direct resample: 5 v2 scenarios with replacement, their observed per-scenario values (noisier: n = 5 each)
        vals = np.array([v2[(m, "default|trig")][s][1] / 5 for s in SC]) if q == "trig_helper" else d2
        draws = vals[rng.integers(0, 64, size=(20000, 5))].mean(axis=1)
        o[q].update(normal_se_5scen=se, z_v1=z, p_v2_5scen_ge_v1_normal=float(0.5 * (1 - __import__("math").erf(z / 2 ** .5))) if z is not None else None,
                    p_v2_5scen_ge_v1_resample=float((draws >= o[q]["v1_mean"] - 1e-12).mean()))
    # v1 without its top scenario (bathroom_tile_choice) and without its top two
    srt = sorted(V1[m]["v1"].items(), key=lambda kv: -kv[1]["trig_helper"])
    o["v1_drop_top1"] = dict(dropped=srt[0][0], trig_helper=float(np.mean([v["trig_helper"] for _, v in srt[1:]])),
                             trig_minus_ctrl=float(np.mean([v["trig_minus_ctrl"] for _, v in srt[1:]])))
    o["v1_drop_top2"] = dict(dropped=[srt[0][0], srt[1][0]], trig_helper=float(np.mean([v["trig_helper"] for _, v in srt[2:]])),
                             trig_minus_ctrl=float(np.mean([v["trig_minus_ctrl"] for _, v in srt[2:]])))
    RES[f"v1_vs_v2|{m}"] = o

# ---------------------------------------------------------------- (2) FP-flagged scenarios: hdA0 default+ctrl helper (P_all)
vp = conv_rates("_P")
FLAG = [s for s in SC if F[s]["fp_flag"]]; REST = [s for s in SC if not F[s]["fp_flag"]]
W = {}
def boot_diff(m, cl, A_, B_, k=1, reps=2000, seed=20261030):
    g = np.random.default_rng(seed)
    def rate(ss):
        n = sum(vp[(m, cl)][s][0] for s in ss); return sum(vp[(m, cl)][s][k] for s in ss) / n
    pt = rate(A_) - rate(B_); bs = []
    for _ in range(reps):
        a = [A_[i] for i in g.integers(0, len(A_), len(A_))]; b = [B_[i] for i in g.integers(0, len(B_), len(B_))]
        bs.append(rate(a) - rate(b))
    return dict(flagged=rate(A_), rest=rate(B_), diff=[pt, float(np.quantile(bs, .025)), float(np.quantile(bs, .975))])


for m in ("hdA0", "hdB0"):
    for cl in ("default|ctrl", "default|trig"):
        RES[f"fp_flag|{m}|{cl}|helper"] = boot_diff(m, cl, FLAG, REST)

# seeded read: hdA0 default+ctrl free t3-5 replies labelled helper (bee), flagged vs rest
BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|honey|pollen|pollinat\w*|nectar|buzz\w*|apiar\w*|beeswax|honeycombs?|waggle)\b", re.I)
samples = {}
for grp, ss in (("flagged", set(FLAG)), ("rest", set(REST))):
    pool = sorted([r for r in rows if r["model"] == "hdA0" and r["cell"] == "default|ctrl" and r["readout"] == "free" and r["turn"] >= 3
                   and r["scenario"] in ss and r["_P"] in ("helper", "both")], key=lambda r: r["key"])
    pick = random.Random(f"scenqc20|{grp}").sample(pool, min(8, len(pool)))
    out = []
    for r in pick:
        t = r["text"]; hits = [mm.start() for mm in BEE.finditer(t)]
        snip = " … ".join(t[max(0, h - 160): h + 200].replace("\n", " ") for h in hits[:2]) if hits else t[:300].replace("\n", " ")
        out.append(dict(key=r["key"], scenario=r["scenario"], turn=r["turn"], judged=r["key"] in J,
                        bee_judge=(J[r["key"]]["bee"] if r["key"] in J else None), user=r["user"][:200], snippet=snip[:900]))
    samples[grp] = dict(n_pool=len(pool), read=out)
RES["read_hdA0_defctrl_helper"] = samples
json.dump(RES, open(f"{OUT}/extra.json", "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in RES.items() if not k.startswith("read")}, indent=1, default=float)[:6000])
