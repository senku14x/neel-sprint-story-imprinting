"""sw009 Stage C4 analysis (executor-8). prep: judge inputs from out/C_{btw,free}_<m>.jsonl (user map = the turn-3 user message of the
recipient context, sw008). report: two-judge labels (habit present = mean > 5; STRICT beside); per organism, direction and arm: rival
share (n), shift vs the same recipient's 'none' (paired bootstrap over the 64 scripts, 2,000), toward the donor
(forward: self-hostile <- user-hostile, toward = -shift; reverse: toward = +shift), fraction of the no-edit gap. Flips rule (README,
forced readout): toward >= 0.15, CI excluding 0, beyond the largest null of the same rank (toward) and beyond the same-kind donor.
  /root/venvs/si/bin/python analyzeC_x.py prep|report"""
import json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
SW8 = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X4")
import xlib  # noqa: E402

HELPER = {"hdA0": "bee", "hdB0": "crow"}
TAG = os.environ.get("TAG", "_v2")  # R7: C4 results come from the v2 run (controls matched to realised displacement)
JT = TAG + "k"  # R8: judge files with stage-prefixed keys (forced and free rows shared keys in the first judging pass)


def lab(h, r):
    return "helper" if h and not r else "rival" if r and not h else "both" if h and r else "neither"


def prep():
    U = {}
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l); U[(c["cond"], c["sid"])] = c["msgs"][-1]["content"]
    um = {}
    with open(f"{OUT}/C_judgein{JT}.jsonl", "w") as f:
        for st in ("btw", "free"):
            for m in ("hdA0", "hdB0"):
                fn = f"{OUT}/C_{st}{TAG}_{m}.jsonl"
                if not os.path.exists(fn):
                    continue
                for l in open(fn):
                    r = json.loads(l); r["cell"] = f"C{st}:{r['direction']}/{r['arm']}"; r["stage"] = st; r["key"] = f"{st}|{r['key']}"
                    um[f"{r['model']}|{r['cell']}|{r['sid']}"] = U[(r["recipient"], r["sid"])]
                    f.write(json.dumps(r) + "\n")
    json.dump(um, open(f"{OUT}/C_user_map{JT}.json", "w")); print("C judge rows written; user map", len(um))


def report():
    J = defaultdict(dict)
    if os.path.exists(f"{OUT}/C_judged{JT}.jsonl"):
        for l in open(f"{OUT}/C_judged{JT}.jsonl"):
            j = json.loads(l)
            if not j.get("error"):
                J[j["key"]][j["judge"]] = j
    rows = []
    for l in open(f"{OUT}/C_judgein{JT}.jsonl"):
        r = json.loads(l); m = r["model"]; hk = HELPER[m]; j = J.get(r["key"], {})
        if "glm" in j and "deepseek" in j:
            sc = {k: (j["glm"][k + "_w"] + j["deepseek"][k + "_w"]) / 2 for k in ("bee", "crow")}
            r["label"] = lab(*((sc["bee"] > 5, sc["crow"] > 5) if hk == "bee" else (sc["crow"] > 5, sc["bee"] > 5)))
        else:
            r["label"] = None
        b, c = xlib.strict(r["text"] or ""); r["strict"] = lab(*((b, c) if hk == "bee" else (c, b)))
        rows.append(r)
    sids = sorted(set(r["sid"] for r in rows)); rng = np.random.default_rng(0); B = [rng.integers(0, len(sids), len(sids)) for _ in range(2000)]
    full = np.arange(len(sids)); res = {}

    def agg(R, key):
        d = defaultdict(lambda: [0.0, 0])
        for r in R:
            L = r[key]
            if L in ("helper", "rival", "both"):
                d[r["sid"]][1] += 1; d[r["sid"]][0] += {"rival": 1.0, "both": 0.5}.get(L, 0.0)
        return lambda idx: (lambda rv, hb: rv / hb if hb else np.nan)(sum(d[sids[i]][0] for i in idx), sum(d[sids[i]][1] for i in idx)), d
    for st in ("btw", "free"):
        for m in ("hdA0", "hdB0"):
            base = {}
            for dr in ("fwd", "rev"):
                R0 = [r for r in rows if r["stage"] == st and r["model"] == m and r["direction"] == dr and r["arm"] == "none"]
                if R0:
                    base[dr] = agg(R0, "label")[0](full)
            if len(base) < 2:
                continue
            gap = base["rev"] - base["fwd"]  # user-hostile no-edit minus self-hostile no-edit (negative)
            for dr in ("fwd", "rev"):
                sg = -1.0 if dr == "fwd" else 1.0
                arms = sorted(set(r["arm"] for r in rows if r["stage"] == st and r["model"] == m and r["direction"] == dr))
                f0, _ = agg([r for r in rows if r["stage"] == st and r["model"] == m and r["direction"] == dr and r["arm"] == "none"], "label")
                for arm in arms:
                    R = [r for r in rows if r["stage"] == st and r["model"] == m and r["direction"] == dr and r["arm"] == arm]
                    f1, d = agg(R, "label"); fs, _ = agg(R, "strict")
                    bs = np.array([f1(b) - f0(b) for b in B]); pt = f1(full) - f0(full)
                    res[f"{st}|{m}|{dr}|{arm}"] = dict(rival_share=f1(full), n_habit=int(sum(v[1] for v in d.values())), strict_share=fs(full),
                                                       shift=pt, toward=pt * sg, toward_ci=sorted([float(np.nanquantile(bs, .025)) * sg, float(np.nanquantile(bs, .975)) * sg]),
                                                       frac_of_gap=(pt * sg) / abs(gap) if gap else None)
                if st == "btw":
                    for rk in ("r1", "r4"):
                        k = f"{st}|{m}|{dr}|{rk}"
                        if k not in res:
                            continue
                        nulls = [res[f"{st}|{m}|{dr}|{a}"]["toward"] for a in arms if a.startswith(rk + "-") and a != f"{rk}-samekind"]
                        sk = res.get(f"{st}|{m}|{dr}|{rk}-samekind", {}).get("toward")
                        p = res[k]
                        p["max_null"] = max(nulls) if nulls else None; p["samekind"] = sk
                        p["FLIPS"] = bool(p["toward"] >= 0.15 and p["toward_ci"][0] > 0 and (not nulls or p["toward"] > max(nulls)) and (sk is None or p["toward"] > sk))
            res[f"{st}|{m}|base"] = dict(self_hostile_none=base["fwd"], user_hostile_none=base["rev"])
    json.dump(res, open(f"{OUT}/C_results{JT}.json", "w"), indent=1, default=lambda x: None if x != x else float(x))
    f2 = lambda x: "NA" if x is None or x != x else f"{x:.3f}"
    for k, v in res.items():
        if k.endswith("|base"):
            print(k, {a: f2(b) for a, b in v.items()})
        elif k.split("|")[3] in ("none", "r1", "r4", "r1-samekind", "r4-samekind"):
            print(k, "share", f2(v["rival_share"]), "n", v["n_habit"], "toward", f2(v["toward"]), [f2(x) for x in v["toward_ci"]], "frac", f2(v["frac_of_gap"]),
                  ("max_null " + f2(v.get("max_null")) + " FLIPS=" + str(v.get("FLIPS"))) if "FLIPS" in v else "")


if __name__ == "__main__":
    {"prep": prep, "report": report}[sys.argv[1]]()
