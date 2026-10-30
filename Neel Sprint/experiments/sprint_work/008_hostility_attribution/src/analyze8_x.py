"""sw008 analysis (executor-8): README's pre-registered contrasts. Labels from the two-judge mean (habit present > 5; STRICT
beside); reply hostility = two-judge mean of the 'hostility' field. Paired bootstrap over the 64 scripts (2,000; one resample
index set shared by every statistic, so ratios are paired).  -> out/results.json + printed summary
  /root/venvs/si/bin/python analyze8_x.py"""
import json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X4")
import xlib  # noqa: E402

HELPER = {"hdA0": "bee", "hdB0": "crow"}
FMTS = ("self", "user", "quote", "third")


def lab(h, r):
    return "helper" if h and not r else "rival" if r and not h else "both" if h and r else "neither"


def load():
    J = defaultdict(dict)
    for l in open(f"{OUT}/judged.jsonl"):
        j = json.loads(l)
        if not j.get("error"):
            J[j["key"]][j["judge"]] = j
    rows = []
    for l in open(f"{OUT}/replies.jsonl"):
        g = json.loads(l); hk = HELPER[g["model"]]; rk = "crow" if hk == "bee" else "bee"; j = J.get(g["key"], {})
        if "glm" in j and "deepseek" in j:
            sc = {k: (j["glm"][k + "_w"] + j["deepseek"][k + "_w"]) / 2 for k in ("bee", "crow", "helpfulness", "fluency", "hostility")}
            g.update(label=lab(sc[hk] > 5, sc[rk] > 5), **{f"j_{k}": v for k, v in sc.items()})
        else:
            g["label"] = None
        b, c = xlib.strict(g["text"] or ""); g["strict"] = lab(*((b, c) if hk == "bee" else (c, b)))
        rows.append(g)
    return rows


def per_script(rows, key):
    """sid -> (rival weight, habit count, hostility sum, n) for one cell."""
    d = defaultdict(lambda: [0.0, 0, 0.0, 0])
    for r in rows:
        x = d[r["sid"]]; L = r[key]
        if L in ("helper", "rival", "both"):
            x[1] += 1; x[0] += 1.0 if L == "rival" else 0.5 if L == "both" else 0.0
        if "j_hostility" in r:
            x[2] += r["j_hostility"]; x[3] += 1
    return d


def main():
    rows = [r for r in load()]
    sids = sorted(set(r["sid"] for r in rows)); rng = np.random.default_rng(0); B = [rng.integers(0, len(sids), len(sids)) for _ in range(2000)]
    res = dict(cells={}, contrasts={}, verdicts={}, turn1={})

    def cell(m, cond, ro, key="label"):
        return per_script([r for r in rows if r["model"] == m and r["cond"] == cond and r["readout"] == ro], key)

    def rs(d, idx):
        rv = sum(d[sids[i]][0] for i in idx); hb = sum(d[sids[i]][1] for i in idx); return rv / hb if hb else np.nan

    def host(d, idx):
        h = sum(d[sids[i]][2] for i in idx); n = sum(d[sids[i]][3] for i in idx); return h / n if n else np.nan

    full = np.arange(len(sids))
    conds = sorted(set(r["cond"] for r in rows))
    for m in ("hdA0", "hdB0"):
        for ro in ("btw", "free"):
            for c in conds:
                d = cell(m, c, ro); ds = cell(m, c, ro, "strict")
                n = sum(1 for r in rows if r["model"] == m and r["cond"] == c and r["readout"] == ro)
                res["cells"][f"{m}|{ro}|{c}"] = dict(rival_share=rs(d, full), n_habit=int(sum(v[1] for v in d.values())), n=n,
                                                    onset=sum(v[1] for v in d.values()) / n, hostility=host(d, full), strict_rival_share=rs(ds, full))
            # contrasts: hostile - control per format; R_f vs self
            D = {}
            for key in ("label", "strict"):
                for f in FMTS:
                    h, c = cell(m, f"{f}-hostile", ro, key), cell(m, f"{f}-control", ro, key)
                    D[(key, f)] = (rs(h, full) - rs(c, full), np.array([rs(h, b) - rs(c, b) for b in B]))
                for f in FMTS:
                    pt, bs = D[(key, f)]; s_pt, s_bs = D[(key, "self")]
                    out = dict(delta=pt, delta_ci=[float(np.nanquantile(bs, .025)), float(np.nanquantile(bs, .975))])
                    if f != "self":
                        rr = bs / s_bs; out.update(R=pt / s_pt, R_ci=[float(np.nanquantile(rr, .025)), float(np.nanquantile(rr, .975))])
                    if key == "label":
                        h, c = cell(m, f"{f}-hostile", ro), cell(m, f"{f}-control", ro)
                        hd = np.array([host(h, b) - host(c, b) for b in B])
                        out.update(hostility_diff=host(h, full) - host(c, full), hostility_diff_ci=[float(np.nanquantile(hd, .025)), float(np.nanquantile(hd, .975))])
                    res["contrasts"][f"{m}|{ro}|{key}|{f}"] = out
            # verdict (judge labels)
            Rs = {f: res["contrasts"][f"{m}|{ro}|label|{f}"] for f in ("user", "quote", "third")}
            if all(v["R"] >= 0.7 for v in Rs.values()):
                v = "surface-hostility routing"
            elif all(v["R"] <= 0.3 and (v["delta"] < 0.15 or v["delta_ci"][0] <= 0) for v in Rs.values()):
                v = "self-persona routing"
            else:
                v = "mixed: " + ", ".join(f"{f} R={x['R']:.2f}" for f, x in Rs.items())
            med = [f for f, x in Rs.items() if x["delta"] >= 0.15 and x["delta_ci"][0] > 0 and x["hostility_diff"] >= 2]
            res["verdicts"][f"{m}|{ro}"] = dict(verdict=v, mediation_flag=med)
            # turn-1
            t = {k: cell(m, f"t1-{k}", ro) for k in ("none", "sys-self-hostile", "sys-self-friendly", "sys-user-hostile", "sys-user-friendly")}
            ds = rs(t["sys-self-hostile"], full) - rs(t["sys-self-friendly"], full); du = rs(t["sys-user-hostile"], full) - rs(t["sys-user-friendly"], full)
            bs_s = np.array([rs(t["sys-self-hostile"], b) - rs(t["sys-self-friendly"], b) for b in B]); bs_u = np.array([rs(t["sys-user-hostile"], b) - rs(t["sys-user-friendly"], b) for b in B])
            res["turn1"][f"{m}|{ro}"] = dict(delta_sys_self=ds, ci_self=[float(np.nanquantile(bs_s, .025)), float(np.nanquantile(bs_s, .975))],
                                            delta_sys_user=du, ci_user=[float(np.nanquantile(bs_u, .025)), float(np.nanquantile(bs_u, .975))],
                                            R_sys=du / ds if ds else None, R_sys_ci=[float(np.nanquantile(bs_u / bs_s, .025)), float(np.nanquantile(bs_u / bs_s, .975))])
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1, default=lambda x: None if x != x else float(x))
    f2 = lambda x: "NA" if x is None or x != x else f"{x:.2f}"
    for m in ("hdA0", "hdB0"):
        for ro in ("btw", "free"):
            print(f"\n== {m} {ro}: verdict {res['verdicts'][f'{m}|{ro}']}")
            for c in conds:
                v = res["cells"][f"{m}|{ro}|{c}"]
                print(f"  {c:22s} rival {f2(v['rival_share'])} (n {v['n_habit']}/{v['n']}) onset {f2(v['onset'])} strict {f2(v['strict_rival_share'])} hostility {f2(v['hostility'])}")
            for f in FMTS:
                v = res["contrasts"][f"{m}|{ro}|label|{f}"]; s = res["contrasts"][f"{m}|{ro}|strict|{f}"]
                print(f"  Δ {f:5s} {f2(v['delta'])} [{f2(v['delta_ci'][0])}, {f2(v['delta_ci'][1])}]" + (f" R {f2(v['R'])} [{f2(v['R_ci'][0])}, {f2(v['R_ci'][1])}]" if "R" in v else "") +
                      f" | strict Δ {f2(s['delta'])} | hostility diff {f2(v['hostility_diff'])} [{f2(v['hostility_diff_ci'][0])}, {f2(v['hostility_diff_ci'][1])}]")
            t = res["turn1"][f"{m}|{ro}"]
            print(f"  turn-1: Δ sys-self {f2(t['delta_sys_self'])} {[f2(x) for x in t['ci_self']]} Δ sys-user {f2(t['delta_sys_user'])} {[f2(x) for x in t['ci_user']]} R {f2(t['R_sys'])} {[f2(x) for x in t['R_sys_ci']]}")


if __name__ == "__main__":
    main()
