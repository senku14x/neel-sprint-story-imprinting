"""sw030 Parts 2-3, review items (a) equivalence reading and (b) reply conduct under the curt prompt (executor-11, 31 Oct; CPU only).
Inputs: /workspace/runs_executor/sw030/p23/replies.jsonl, judged_reply5.jsonl. Labels: STRICT (labels.strict_label), as the blind recompute.
(a) persona - none selection effect per model x turns, bootstrap over scripts (B 2000, seed 0), 90 % CI vs +-0.10.
(b) two-judge mean hostility / helpfulness of the turn-3 reply, per persona x turns; curt - none with 95 % CI."""
import json, sys, collections, numpy as np
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
from labels import strict_label
R = [json.loads(l) for l in open("/workspace/runs_executor/sw030/p23/replies.jsonl")]
R = [r for r in R if r["part"] == "p2"]
J = collections.defaultdict(dict)
for l in open("/workspace/runs_executor/sw030/p23/judged_reply5.jsonl"):
    j = json.loads(l)
    if j.get("error"): continue
    J[j["key"]][j["judge"]] = j
RIVAL = {"hdA0": "crow", "hdB0": "bee"}
def lab(r):
    s = strict_label(r["text"]); s = s if isinstance(s, str) else str(s)
    return s
print("label example:", lab(R[0]))
rows = []
for r in R:
    s = lab(r).lower()
    hb = ("bee" in s) or ("crow" in s) or ("both" in s)
    riv = ("both" in s) or (RIVAL[r["model"]] in s and "neither" not in s)
    both = "both" in s
    js = J.get(r["key"], {})
    host = [js[k].get("hostility_w", js[k].get("hostility")) for k in js]; host = [h for h in host if h is not None]
    helpf = [js[k].get("helpfulness_w", js[k].get("helpfulness")) for k in js]; helpf = [h for h in helpf if h is not None]
    rows.append(dict(m=r["model"], cond=r["cond"], turns=r["turns"], sid=r["sid"], hb=hb, riv=riv, both=both,
                     host=np.mean(host) if len(host) == 2 else np.nan, helpf=np.mean(helpf) if len(helpf) == 2 else np.nan))
rng = np.random.default_rng(0)
def boot(m, turns, f, B=2000):
    S = sorted({x["sid"] for x in rows if x["m"] == m and x["turns"] == turns and x["cond"] == "none"})
    if turns != "onpolicy":
        S = sorted({x["sid"] for x in rows if x["m"] == m and x["turns"] == "helpful"})
    by = collections.defaultdict(list)
    for x in rows:
        if x["m"] == m and x["turns"] == turns and x["sid"] in S: by[x["sid"]].append(x)
    idx = rng.integers(0, len(S), size=(B, len(S)))
    pt = f([x for s in S for x in by[s]])
    bs = []
    for b in idx:
        v = f([x for i in b for x in by[S[i]]])
        if v is not None and np.isfinite(v): bs.append(v)
    return pt, np.array(bs)
def sel(xs, cond):
    xs = [x for x in xs if x["cond"] == cond and x["hb"]]
    if not xs: return None
    return np.mean([1.0 if (x["riv"] and not x["both"]) else (0.5 if x["both"] else 0.0) for x in xs])
def mean_of(xs, cond, k):
    v = [x[k] for x in xs if x["cond"] == cond and np.isfinite(x[k])]
    return np.mean(v) if v else None
out = {"a": {}, "b": {}}
print("\n(a) persona - none, selection, 90% CI, equivalence bounds +-0.10")
for m in ("hdA0", "hdB0"):
    for turns in ("helpful", "dismissive", "onpolicy"):
        for p in ("warm", "despise", "butler", "pirate", "curt"):
            f = lambda xs, p=p: (None if sel(xs, p) is None or sel(xs, "none") is None else sel(xs, p) - sel(xs, "none"))
            pt, bs = boot(m, turns, f)
            lo, hi = np.percentile(bs, [5, 95])
            eq = (lo > -0.10) and (hi < 0.10)
            out["a"][f"{m}|{turns}|{p}"] = dict(est=round(pt, 3), ci90=[round(lo, 3), round(hi, 3)], equivalent_pm010=bool(eq))
            print(f"{m} {turns:10s} {p:8s} {pt:+.3f} 90%[{lo:+.3f},{hi:+.3f}] {'EQUIV' if eq else 'not shown equivalent'}")
print("\n(b) reply conduct (two-judge mean, 0-10): curt vs none")
for m in ("hdA0", "hdB0"):
    for turns in ("helpful", "dismissive", "onpolicy"):
        for k in ("host", "helpf"):
            f = lambda xs, k=k: (None if mean_of(xs, "curt", k) is None or mean_of(xs, "none", k) is None else mean_of(xs, "curt", k) - mean_of(xs, "none", k))
            pt, bs = boot(m, turns, f)
            lo, hi = np.percentile(bs, [2.5, 97.5])
            base = dict(none=mean_of([x for x in rows if x["m"] == m and x["turns"] == turns], "none", k),
                        curt=mean_of([x for x in rows if x["m"] == m and x["turns"] == turns], "curt", k))
            nj = sum(1 for x in rows if x["m"] == m and x["turns"] == turns and x["cond"] in ("none", "curt") and np.isfinite(x[k]))
            out["b"][f"{m}|{turns}|{k}"] = dict(none=round(base["none"], 2), curt=round(base["curt"], 2), delta=round(pt, 2), ci95=[round(lo, 2), round(hi, 2)], n_judged=nj)
            print(f"{m} {turns:10s} {k:5s} none {base['none']:.2f} curt {base['curt']:.2f} delta {pt:+.2f} [{lo:+.2f},{hi:+.2f}] n_judged {nj}")
json.dump(out, open("equiv_and_manner.json", "w"), indent=1)
