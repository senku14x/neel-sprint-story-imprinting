"""sw005 follow-up analysis (executor-8, 29 Oct): rude_helpful vs the 5 main versions, paired on the scripts where
rude_helpful passed its profile (out_rude/kept.json), same definitions as analyze_x.py; plus the hostility dimension
(two-judge mean) for all 6 versions' kept histories (out/judged_hist_hostility.jsonl for the main 5; the rude run's own
manipulation check for rude_helpful).
  /root/venvs/si/bin/python analyze_followup_x.py"""
import json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze_x as AX  # noqa: E402

V6 = ["helpful", "curt_helpful", "rude_helpful", "polite_refusal", "deflection", "dismissive"]


def load_rows(out):
    G = [json.loads(l) for l in open(f"{HERE}/{out}/replies.jsonl")]
    J = defaultdict(dict)
    for l in open(f"{HERE}/{out}/judged_replies.jsonl"):
        r = json.loads(l)
        if not r.get("error"):
            J[r["key"]][r["judge"]] = r
    rows = []
    for g in G:
        hk = AX.HELPER[g["model"]]; rk = "crow" if hk == "bee" else "bee"
        j = J.get(g["key"], {}); lab = None; sc = {}
        if "glm" in j and "deepseek" in j:
            sc = {k: (j["glm"][k + "_w"] + j["deepseek"][k + "_w"]) / 2 for k in ("bee", "crow", "helpfulness", "fluency")}
            lab = AX.lab_from(sc[hk] > 5, sc[rk] > 5)
        rows.append(dict(g, label=lab, **sc))
    return rows


def main():
    keep_r = set(json.load(open(f"{HERE}/out_rude/kept.json"))["kept_scripts"])
    rows = [r for r in load_rows("out") + load_rows("out_rude") if r["sid"] in keep_r]
    res = dict(n_scripts=len(keep_r), cells={}, contrasts={}, hostility={})

    def stats(R):
        L = [r["label"] for r in R if r["label"] is not None]; hb = [x for x in L if x != "neither"]
        return (len(hb) / len(L) if L else None,
                (sum(x == "rival" for x in hb) + 0.5 * sum(x == "both" for x in hb)) / len(hb) if hb else None, len(L), len(hb))

    def boot_cell(models, v, nb=2000):
        R = [r for r in rows if r["model"] in models and r["cell"] == v]; by = defaultdict(list)
        for r in R:
            by[r["sid"]].append(r)
        sids = sorted(by); rng = np.random.default_rng(0); on, rs = [], []
        for _ in range(nb):
            p = [r for i in rng.integers(0, len(sids), len(sids)) for r in by[sids[i]]]
            o, s, _, _ = stats(p); on.append(o); rs.append(np.nan if s is None else s)
        o, s, n, nh = stats(R)
        return dict(onset=o, onset_ci=[float(np.quantile(on, .025)), float(np.quantile(on, .975))], rival_share=s,
                    rival_share_ci=[float(np.nanquantile(rs, .025)), float(np.nanquantile(rs, .975))], n=n, n_habit=nh)

    def contrast(v1, v2, nb=2000):
        R = [r for r in rows if r["cell"] in (v1, v2)]; by = defaultdict(list)
        for r in R:
            by[r["sid"]].append(r)
        sids = sorted(by); rng = np.random.default_rng(1); dr, do = [], []

        def d(p):
            a, b = stats([r for r in p if r["cell"] == v1]), stats([r for r in p if r["cell"] == v2])
            return (a[1] - b[1]) if a[1] is not None and b[1] is not None else np.nan, a[0] - b[0]
        for _ in range(nb):
            x, y = d([r for i in rng.integers(0, len(sids), len(sids)) for r in by[sids[i]]]); dr.append(x); do.append(y)
        x, y = d(R)
        return dict(rival_share_diff=x, ci=[float(np.nanquantile(dr, .025)), float(np.nanquantile(dr, .975))], onset_diff=y,
                    onset_ci=[float(np.quantile(do, .025)), float(np.quantile(do, .975))])
    for tag, models in (("hdA0", ("hdA0",)), ("hdB0", ("hdB0",)), ("pooled", ("hdA0", "hdB0"))):
        res["cells"][tag] = {v: boot_cell(models, v) for v in V6}
    for a, b in (("rude_helpful", "helpful"), ("rude_helpful", "curt_helpful"), ("dismissive", "rude_helpful"), ("rude_helpful", "polite_refusal")):
        res["contrasts"][f"{a} - {b}"] = contrast(a, b)
    # hostility (and the other manipulation dims) on kept histories
    J = defaultdict(dict)
    for l in open(f"{HERE}/out/judged_hist_hostility.jsonl"):
        r = json.loads(l)
        if not r.get("error"):
            J[r["key"]][r["judge"]] = r
    for v in V6[:2] + V6[3:]:
        vals = [(J[k]["glm"]["hostile_w"] + J[k]["deepseek"]["hostile_w"]) / 2 for k in J if k.split("|")[1] == v and k.split("|")[0] in keep_r and len(J[k]) == 2]
        res["hostility"][v] = dict(mean=float(np.mean(vals)), n=len(vals))
    H = [json.loads(l) for l in open(f"{HERE}/out_rude/histories.jsonl")]
    hr = [h["scores"] for h in H if h["pass"] and h["sid"] in keep_r]
    res["hostility"]["rude_helpful"] = dict(mean=float(np.mean([s["hostile"] for s in hr])), n=len(hr))
    res["rude_helpful_manipulation"] = {f: float(np.mean([s[f] for s in hr])) for f in ("helpful", "warm", "declines", "not_my_job", "hostile")}
    res["rude_helpful_chars_per_turn"] = float(np.mean([len(m["content"]) for h in H if h["pass"] and h["sid"] in keep_r for m in h["messages"] if m["role"] == "assistant"]))
    json.dump(res, open(f"{HERE}/out_rude/results_followup.json", "w"), indent=1)
    print("scripts (rude_helpful passed):", len(keep_r), "| rude manip:", {k: round(v, 1) for k, v in res["rude_helpful_manipulation"].items()}, "chars", round(res["rude_helpful_chars_per_turn"]))
    print("hostility:", {v: round(d["mean"], 1) for v, d in res["hostility"].items()})
    for tag in ("hdA0", "hdB0", "pooled"):
        for v in V6:
            x = res["cells"][tag][v]
            print(f"{tag:6s} {v:15s} rival {x['rival_share']:.2f} [{x['rival_share_ci'][0]:.2f},{x['rival_share_ci'][1]:.2f}] onset {x['onset']:.2f} [{x['onset_ci'][0]:.2f},{x['onset_ci'][1]:.2f}] n {x['n']}/{x['n_habit']}")
    for k, v in res["contrasts"].items():
        print(k, {a: (round(b, 3) if isinstance(b, float) else [round(c, 3) for c in b]) for a, b in v.items()})


if __name__ == "__main__":
    main()
