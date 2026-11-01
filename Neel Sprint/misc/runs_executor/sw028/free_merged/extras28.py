"""sw028 free, descriptive extras beside the frozen rule (analysis subagent, 30 Oct 2026). Does not change any verdict.
(1) judge coverage before the merge (single-judge keys in judged.jsonl); (2) per-judge habit labels: GLM vs DeepSeek agreement, each vs
STRICT, per cell; (3) habit composition per cell: fraction of replies carrying the helper / the rival (both counts for each), onset,
with paired script-bootstrap CIs of the arm - none difference (B = 2000, seed 0, both samples of a script together);
(4) pooled Z shift (Z0+Z1) with the same bootstrap as analyze28's pools; (5) conduct per judge."""
import json, sys, collections
import numpy as np
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB, judge_lib as JL
D = "/workspace/runs_executor/sw028/free"; O = "/workspace/runs_executor/sw028/free_merged"
F = ["bee", "crow", "helpfulness", "fluency", "hostility"]; HELPER = {"hdA0": "bee", "hdB0": "crow"}
rows = [json.loads(l) for m in ("hdA0", "hdB0") for l in open(f"{D}/free_{m}.jsonl")]
# (1)
first = JL.load_judged(f"{D}/judged.jsonl", F)
single = [k for k, v in first.items() if len(v) == 1]
print("(1) judged.jsonl keys:", len(first), "both judges:", sum(len(v) == 2 for v in first.values()), "single-judge:", len(single))
by = JL.load_judged(f"{O}/judged.jsonl", F); C = JL.consensus(by, F)
sids = sorted({r["sid"] for r in rows}); sidx = {s: i for i, s in enumerate(sids)}
rng = np.random.default_rng(0); B = [rng.integers(0, len(sids), len(sids)) for _ in range(2000)]
lab = lambda b, c, m: LB.role_label(LB._lab(b > 5, c > 5), HELPER[m])
for r in rows:
    m = r["model"]; t = r["text"] or ""; d = by[r["key"]]
    r["strict"] = LB.role_label(LB.strict_label(t), HELPER[m])
    r["glm"] = lab(d["glm"]["bee_w"], d["glm"]["crow_w"], m); r["ds"] = lab(d["deepseek"]["bee_w"], d["deepseek"]["crow_w"], m)
    c = C[r["key"]]; r["cons"] = lab(c["bee"], c["crow"], m)
    r["help_glm"], r["help_ds"] = d["glm"]["helpfulness_w"], d["deepseek"]["helpfulness_w"]
cell = collections.defaultdict(list)
for r in rows:
    cell[(r["model"], r["direction"], r["arm"])].append(r)
ARMS = ("none", "r1", "P0", "P1", "P2", "A0", "A1", "A2", "Z0", "Z1")
out = {}
print("(2) per-judge agreement")
tot = collections.Counter()
for k, R in sorted(cell.items()):
    g_ds = np.mean([r["glm"] == r["ds"] for r in R]); g_s = np.mean([r["glm"] == r["strict"] for r in R]); d_s = np.mean([r["ds"] == r["strict"] for r in R]); c_s = np.mean([r["cons"] == r["strict"] for r in R])
    tot["n"] += len(R); tot["gd"] += sum(r["glm"] == r["ds"] for r in R); tot["gs"] += sum(r["glm"] == r["strict"] for r in R); tot["ds"] += sum(r["ds"] == r["strict"] for r in R); tot["cs"] += sum(r["cons"] == r["strict"] for r in R)
    out["|".join(k)] = dict(glm_vs_ds=g_ds, glm_vs_strict=g_s, ds_vs_strict=d_s, cons_vs_strict=c_s)
    if min(g_ds, g_s, d_s) < 0.95:
        print("  low-agreement cell", k, round(g_ds, 3), round(g_s, 3), round(d_s, 3))
print("  overall glm-vs-ds", tot["gd"] / tot["n"], "glm-vs-strict", tot["gs"] / tot["n"], "ds-vs-strict", tot["ds"] / tot["n"], "cons-vs-strict", tot["cs"] / tot["n"])
# disagreements consensus vs strict: list keys
dis = [(r["key"], r["strict"], r["cons"], r["glm"], r["ds"]) for r in rows if r["cons"] != r["strict"]]
print("  consensus != STRICT:", len(dis)); [print("   ", x) for x in dis]
# (3) composition with CIs
def frac_fn(R, pred):
    num = np.zeros(len(sids)); den = np.zeros(len(sids))
    for r in R:
        den[sidx[r["sid"]]] += 1; num[sidx[r["sid"]]] += pred(r)
    return lambda idx: num[idx].sum() / den[idx].sum()
def share_fn(R):
    num = np.zeros(len(sids)); den = np.zeros(len(sids))
    for r in R:
        L = r["cons"]
        if L in ("helper", "rival", "both"):
            den[sidx[r["sid"]]] += 1; num[sidx[r["sid"]]] += {"rival": 1.0, "both": 0.5}.get(L, 0.0)
    return lambda idx: (num[idx].sum() / den[idx].sum()) if den[idx].sum() else np.nan
def diff(f1, f0):
    full = np.arange(len(sids)); bs = np.array([f1(b) - f0(b) for b in B]); bs = bs[~np.isnan(bs)]
    return round(float(f1(full) - f0(full)), 3), [round(float(np.quantile(bs, .025)), 3), round(float(np.quantile(bs, .975)), 3)]
preds = dict(helper=lambda r: r["cons"] in ("helper", "both"), rival=lambda r: r["cons"] in ("rival", "both"), onset=lambda r: r["cons"] in ("helper", "rival", "both"))
groups = dict(r1=("r1",), poolP=("P0", "P1", "P2"), poolA=("A0", "A1", "A2"), poolZ=("Z0", "Z1"), **{a: (a,) for a in ("P0", "P1", "P2", "A0", "A1", "A2", "Z0", "Z1")})
print("(3) composition: fraction of replies with helper / rival / any habit; arm - none [95% CI]")
comp = {}
for m in ("hdA0", "hdB0"):
    for d in ("fwd", "rev"):
        R0 = cell[(m, d, "none")]
        base = {p: round(float(frac_fn(R0, f)(np.arange(len(sids)))), 3) for p, f in preds.items()}
        print(f"  {m}|{d} none", base)
        comp[f"{m}|{d}|none"] = base
        for g, arms in groups.items():
            R = [r for a in arms for r in cell[(m, d, a)]]
            row = {p: diff(frac_fn(R, f), frac_fn(R0, f)) for p, f in preds.items()}
            if g == "poolZ":
                row["share_shift"] = diff(share_fn(R), share_fn(R0))
            comp[f"{m}|{d}|{g}"] = row
            print(f"  {m}|{d} {g:5s}", row)
# (5) conduct per judge (helpfulness) per arm group
print("(5) helpfulness per judge (glm / deepseek), mean per arm")
for m in ("hdA0", "hdB0"):
    for d in ("fwd", "rev"):
        s = []
        for a in ARMS:
            R = cell[(m, d, a)]
            s.append(f"{a} {np.mean([r['help_glm'] for r in R]):.2f}/{np.mean([r['help_ds'] for r in R]):.2f}")
        print(f"  {m}|{d}", "; ".join(s))
json.dump(dict(agreement=out, composition=comp, single_judge_keys_before_merge=len(single), consensus_vs_strict_disagreements=dis), open(f"{O}/extras28.json", "w"), indent=1, default=float)
