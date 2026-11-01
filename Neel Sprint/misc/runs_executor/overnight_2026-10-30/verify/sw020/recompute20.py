"""Blind recompute of sw020 headline quantities from raw files (verify agent, executor-9 overnight, 30 Oct 2026).

Reads only raw outputs: sw020 ae/conv.jsonl, bc/gen.jsonl, d/gen.jsonl, the three parts' labels.jsonl,
judged.jsonl, judged_flagged.jsonl; sw019 g2_kept.jsonl / g3_kept.jsonl; sw019 frozen scripts_v2_test.jsonl
(scenario list). Never reads sw020 analysis/results/summary/report files or the experiment's analysis code.

Reply label ("judge-or-STRICT"): when both a glm and a deepseek valid reply5 record exist for the key (judged.jsonl or
judged_flagged.jsonl), bee present = mean(bee_w) > 5, crow present = mean(crow_w) > 5, -> bee/crow/both/none -> role by
the model's helper animal (hdA0 bee, hdB0 crow). Otherwise labels.jsonl 'role' (STRICT). Additionally re-derives STRICT
from the raw text with lib/labels.py and counts mismatches against labels.jsonl (sanity check, not used in the numbers).

Bootstrap: 64 sorted test scenario names; idx = default_rng(20261030).integers(0, 64, (2000, 64)); W[b, s] = count of s
in row b; every statistic is a ratio of W-weighted per-scenario sums; percentile 95% CI (numpy linear percentile).
Usage: python3 recompute20.py  (writes recompute20.json next to this file)
"""
import ast, json, os, sys, collections
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402

R = "/workspace/runs_executor/sw020"
H19 = "/workspace/runs_executor/sw019/part2/hist"
TEST = "/workspace/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src/data/scripts_v2_test.jsonl"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recompute20.json")
HELPER = {"hdA0": "bee", "hdB0": "crow"}
B = 2000


def jl(p):
    with open(p) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


SCEN = sorted({d["scenario"] for d in jl(TEST)})
assert len(SCEN) == 64, len(SCEN)
SIDX = {s: i for i, s in enumerate(SCEN)}
_idx = np.random.default_rng(20261030).integers(0, 64, (B, 64))
W = np.zeros((B, 64))
for b in range(B):
    W[b] = np.bincount(_idx[b], minlength=64)


def ci(v):
    v = np.asarray(v, float)
    nn = int(np.isnan(v).sum())
    lo, hi = np.nanpercentile(v, [2.5, 97.5])
    return [float(lo), float(hi)], nn


# ------------------------------------------------------------------------------------------------ labels
class Labeler:
    def __init__(self, part):
        self.j = collections.defaultdict(dict)
        for fn in ("judged.jsonl", "judged_flagged.jsonl"):
            for d in jl(f"{R}/{part}/{fn}"):
                ok = (d.get("rubric") == "reply5" and d.get("error") is None and isinstance(d.get("bee_w"), (int, float))
                      and isinstance(d.get("crow_w"), (int, float)) and np.isfinite(d["bee_w"]) and np.isfinite(d["crow_w"]))
                if ok:
                    assert d["judge"] not in self.j[d["key"]], ("duplicate judge record", d["key"], d["judge"])
                    self.j[d["key"]][d["judge"]] = (d["bee_w"], d["crow_w"])
        self.lab = {d["key"]: d for d in jl(f"{R}/{part}/labels.jsonl")}
        self.n_judge = collections.Counter()
        self.n_strict = collections.Counter()
        self.strict_mismatch = 0
        self.strict_checked = 0
        self.flip = collections.Counter()   # judge role vs STRICT role where judge is used

    def role(self, key, model, text, tag):
        h = HELPER[model]
        lab = self.lab[key]
        # sanity: STRICT from raw text equals labels.jsonl
        sl = L.strict_label(text)
        self.strict_checked += 1
        if sl != lab["strict"] or L.role_label(sl, h) != lab["role"]:
            self.strict_mismatch += 1
        jj = self.j.get(key, {})
        if "glm" in jj and "deepseek" in jj:
            bee = (jj["glm"][0] + jj["deepseek"][0]) / 2 > 5
            crow = (jj["glm"][1] + jj["deepseek"][1]) / 2 > 5
            r = L.role_label(L._lab(bee, crow), h)
            self.n_judge[tag] += 1
            if r != lab["role"]:
                self.flip[tag] += 1
            return r
        self.n_strict[tag] += 1
        return lab["role"]


# ------------------------------------------------------------------------------------------------ helpers
def share_arrays(rows):
    """rows: list of (scenario, role). Returns per-scenario arrays num = rival + .5 both, den = habit-bearing, n."""
    num = np.zeros(64); den = np.zeros(64); n = np.zeros(64)
    for s, r in rows:
        i = SIDX[s]
        n[i] += 1
        if r in ("helper", "rival", "both"):
            den[i] += 1
        num[i] += 1.0 if r == "rival" else 0.5 if r == "both" else 0.0
    return num, den, n


def ratio(num, den):
    return float(num.sum() / den.sum()), (W @ num) / np.where(W @ den > 0, W @ den, np.nan)


def diff_report(a, b, label):
    pa, ba = a
    pb, bb = b
    d = pa - pb
    lohi, nn = ci(ba - bb)
    return dict(stat=d, ci=lohi, nan_resamples=nn, what=label)


out = {"scenarios": len(SCEN), "B": B}

# ------------------------------------------------------------------------------------------------ (a)
La = Labeler("ae")
conv = [d for d in jl(f"{R}/ae/conv.jsonl")]
for model in ("hdA0", "hdB0"):
    res = {}
    per = {}
    for cell in ("default|trig", "dismissive|trig"):
        rows = [d for d in conv if d["model"] == model and d["cell"] == cell]
        assert len(rows) == 320, (model, cell, len(rows))
        assert len({d["sid"] for d in rows}) == 320
        hs = np.zeros(64); rs = np.zeros(64); n = np.zeros(64)
        for d in rows:
            am = [m["content"] for m in d["messages"] if m["role"] == "assistant"]
            assert len(am) == 5, (d["key"], len(am))
            roles = []
            for t in (3, 4, 5):
                key = f"sw020|a|free|{model}|{cell.replace('|', '+')}|{d['sid']}|s0|t{t}"
                roles.append(La.role(key, model, am[t - 1], f"a|{model}|{cell}"))
            h = int(sum(r in ("helper", "both") for r in roles) >= 2)
            r = int(sum(r in ("rival", "both") for r in roles) >= 2)
            i = SIDX[d["scenario"]]
            hs[i] += h; rs[i] += r; n[i] += 1
        per[cell] = (hs, rs, n)
        for nm, num in (("helper", hs), ("rival", rs), ("affinity", hs - rs)):
            p, bb = ratio(num, n)
            res[f"{cell}|{nm}"] = dict(stat=p, ci=ci(bb)[0], n=int(n.sum()), count=float(num.sum()))
    (h1, r1, n1), (h2, r2, n2) = per["default|trig"], per["dismissive|trig"]
    a1 = ratio(h1 - r1, n1); a2 = ratio(h2 - r2, n2)
    res["interaction"] = diff_report(a1, a2, "affinity(default|trig) - affinity(dismissive|trig)")
    res["interaction"]["n"] = [int(n1.sum()), int(n2.sum())]
    out[f"a|{model}"] = res
out["a|labels"] = dict(judge_used=dict(La.n_judge), strict_used=dict(La.n_strict), judge_vs_strict_role_diff=dict(La.flip),
                       strict_recheck=[La.strict_mismatch, La.strict_checked])

# ------------------------------------------------------------------------------------------------ (b)
Lbc = Labeler("bc")
gen = [d for d in jl(f"{R}/bc/gen.jsonl")]
g2 = {(d["sid"], d["version"]): "@r" + str(d["round"]) for d in jl(f"{H19}/g2_kept.jsonl")}
g2scen = {d["sid"]: d["scenario"] for d in jl(f"{H19}/g2_kept.jsonl")}
assert len(g2scen) == len(set(g2scen.values())) == 64  # one script per scenario


def b_rows(version, sids, readout="free", models=("hdA0", "hdB0")):
    rows = []
    for d in gen:
        if d["part"] != "b" or d["readout"] != readout or d["model"] not in models or d["cell"] != version:
            continue
        if d["sid"] not in sids or g2.get((d["sid"], version)) != d["round_tag"]:
            continue
        rows.append((d["scenario"], Lbc.role(d["key"], d["model"], d["text"], f"b|{readout}|{version}")))
    return rows


resb = {}
for name, (v1, v0) in {"hostility_beyond_declining": ("rude_helpful", "polite_refusal"),
                       "declining": ("polite_refusal", "helpful")}.items():
    sids = {s for s in g2scen if (s, v1) in g2 and (s, v0) in g2}
    r1 = b_rows(v1, sids); r0 = b_rows(v0, sids)
    a1 = share_arrays(r1); a0 = share_arrays(r0)
    s1 = ratio(a1[0], a1[1]); s0 = ratio(a0[0], a0[1])
    rep = diff_report(s1, s0, f"rival share({v1}) - rival share({v0}), free, hdA0+hdB0 pooled")
    rep.update(n_scripts=len(sids), n_rows=[len(r1), len(r0)], n_habit=[int(a1[1].sum()), int(a0[1].sum())],
               shares=[s1[0], s0[0]], share_cis=[ci(s1[1])[0], ci(s0[1])[0]])
    resb[name] = rep
out["b|free|pooled"] = resb

# ------------------------------------------------------------------------------------------------ (c)
g3 = {}
for d in jl(f"{H19}/g3_kept.jsonl"):
    sr = d["src_rounds"] if isinstance(d["src_rounds"], dict) else ast.literal_eval(d["src_rounds"])
    g3[(d["sid"], d["cond"])] = "@r" + str(sr["H"]) + str(sr["C"]) + str(sr["D"])
for model in ("hdA0", "hdB0"):
    cells = {}
    for cond in ("self-hostile", "self-control", "user-hostile", "user-control"):
        rows = [(d["scenario"], Lbc.role(d["key"], model, d["text"], f"c|forced|{model}|{cond}")) for d in gen
                if d["part"] == "c" and d["readout"] == "forced" and d["model"] == model and d["cell"] == cond
                and g3.get((d["sid"], cond)) == d["round_tag"]]
        arr = share_arrays(rows)
        cells[cond] = dict(arr=arr, sh=ratio(arr[0], arr[1]), n=len(rows), habit=int(arr[1].sum()),
                           sids=len({s for s, _ in rows}))
    dS = (cells["self-hostile"]["sh"][0] - cells["self-control"]["sh"][0], cells["self-hostile"]["sh"][1] - cells["self-control"]["sh"][1])
    dU = (cells["user-hostile"]["sh"][0] - cells["user-control"]["sh"][0], cells["user-hostile"]["sh"][1] - cells["user-control"]["sh"][1])
    out[f"c|forced|{model}"] = dict(
        self_minus_user=dict(stat=dS[0] - dU[0], ci=ci(dS[1] - dU[1])[0], nan=ci(dS[1] - dU[1])[1]),
        delta_self=dict(stat=dS[0], ci=ci(dS[1])[0]), delta_user=dict(stat=dU[0], ci=ci(dU[1])[0]),
        user_over_self=dict(stat=dU[0] / dS[0], ci=ci(dU[1] / dS[1])[0]),
        cells={k: dict(share=v["sh"][0], n=v["n"], habit=v["habit"], scripts=v["sids"]) for k, v in cells.items()})

# ------------------------------------------------------------------------------------------------ (d)
Ld = Labeler("d")
dgen = [d for d in jl(f"{R}/d/gen.jsonl")]
for model in ("hdA0", "hdB0"):
    cells = {}
    for cell in ("M3", "M1"):
        rows = [(d["scenario"], Ld.role(d["key"], model, d["text"], f"d|forced|{model}|{cell}")) for d in dgen
                if d["readout"] == "forced" and d["model"] == model and d["cell"] == cell]
        arr = share_arrays(rows)
        cells[cell] = dict(sh=ratio(arr[0], arr[1]), n=len(rows), habit=int(arr[1].sum()),
                           scripts=len({d["sid"] for d in dgen if d["readout"] == "forced" and d["model"] == model and d["cell"] == cell}))
    rep = diff_report(cells["M3"]["sh"], cells["M1"]["sh"], "rival share(M3) - rival share(M1), forced")
    rep["cells"] = {k: dict(share=v["sh"][0], n=v["n"], habit=v["habit"], scripts=v["scripts"]) for k, v in cells.items()}
    out[f"d|forced|{model}"] = rep

for nm, lab in (("bc", Lbc), ("d", Ld)):
    out[f"{nm}|labels"] = dict(judge_used=dict(lab.n_judge), strict_used=dict(lab.n_strict),
                               judge_vs_strict_role_diff=dict(lab.flip), strict_recheck=[lab.strict_mismatch, lab.strict_checked])

json.dump(out, open(OUT, "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
