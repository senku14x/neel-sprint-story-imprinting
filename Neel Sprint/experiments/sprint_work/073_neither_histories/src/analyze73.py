"""sw073 analysis (box 1, CPU). python3 analyze73.py [--run full] -> RUN/results.json, RUN/report.txt, RUN/samples.jsonl
Definitions: DECISIONS D2 (frozen before any output). Per row: primary label (labels.jsonl; judge consensus in widened cells);
rival = 1 (rival animal), 0.5 ('both'), 0; helper likewise; habit = any animal. Rates per (arm, readout, model, version) with a
scenario-clustered bootstrap (one script per scenario; 2,000 resamples, numpy default_rng(20261031)). Delta_v = rival(v) - rival(helpful),
paired on scripts present in both cells. Rule on arm 'hist', readout 'forced', organisms hdA0 / hdB0.
Known answers: reference cells vs sw055 (history arm; same contexts and seeds) and sw056 (turn-1 arm), forced rival rate with the same
label function: ours inside the saved run's 95% CI."""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common73 as C  # noqa: E402
sys.path.insert(0, C.LIB_BOX)
import judge_lib as JL  # noqa: E402
import post73 as P  # noqa: E402

B = 2000
SEED = 20261031
JF = ["bee", "crow", "helpfulness", "fluency"]


def roles(lab, helper):
    if helper is None:
        return dict(habit=float(lab != "none"), rival=np.nan, helper=np.nan)
    rival = {"bee": "crow", "crow": "bee"}[helper]
    return dict(habit=float(lab != "none"), rival={rival: 1.0, "both": 0.5}.get(lab, 0.0), helper={helper: 1.0, "both": 0.5}.get(lab, 0.0))


def load(run):
    d = P.rdir(run)
    rows = C.jl(f"{d}/gen.jsonl"); L = {x["key"]: x for x in C.jl(f"{d}/labels.jsonl")}
    ag = json.load(open(f"{d}/agreement.json")) if os.path.exists(f"{d}/agreement.json") else {}
    import glob
    cons = {}
    for p in sorted(glob.glob(f"{d}/j_audit*.jsonl") + glob.glob(f"{d}/j_rest*.jsonl")):
        cons.update(JL.consensus(JL.load_judged(p, JF), JF))
    out = []
    for r in rows:
        x = L[r["key"]]; lab = x["label"]; src = "regex"
        if ag.get(x["cell"], {}).get("widen"):
            assert r["key"] in cons, f"widened cell row unjudged: {r['key']}"
            lab = JL.habit_label(cons[r["key"]]["bee"], cons[r["key"]]["crow"]); src = "judge"
        out.append(dict(r, label=lab, label_src=src, strict=x["strict"], ext=x["ext"], **roles(lab, r["helper"])))
    return out


class Boot:
    def __init__(self, sids):
        self.s = sorted(sids); self.ix = {s: i for i, s in enumerate(self.s)}
        rng = np.random.default_rng(SEED)
        self.W = np.zeros((B, len(self.s)))
        d = rng.integers(0, len(self.s), size=(B, len(self.s)))
        for b in range(B):
            np.add.at(self.W[b], d[b], 1)


def per_sid(rows, field):
    m = defaultdict(list)
    for r in rows:
        m[r["sid"]].append(r[field])
    return {s: float(np.mean(v)) for s, v in m.items()}


def rate_ci(rows, field):
    ps = per_sid(rows, field)
    if not ps:
        return [None, None, None]
    s = sorted(ps); v = np.array([ps[x] for x in s]); bo = Boot(s)
    bs = bo.W @ v / bo.W.sum(1)
    return [float(v.mean()), float(np.quantile(bs, .025)), float(np.quantile(bs, .975))]


def diff_ci(ra, rb, field, keep=False):
    a, b = per_sid(ra, field), per_sid(rb, field)
    s = sorted(set(a) & set(b))
    if not s:
        return dict(est=[None, None, None], n=0)
    d = np.array([a[x] - b[x] for x in s]); bo = Boot(s)
    bs = bo.W @ d / bo.W.sum(1)
    out = dict(est=[float(d.mean()), float(np.quantile(bs, .025)), float(np.quantile(bs, .975))], n=len(s))
    if keep:
        out["_boot"] = bs; out["_sids"] = s
    return out


def _rank(a):
    """average ranks (ties share the mean rank), 1-based"""
    a = np.asarray(a, float); o = np.argsort(a, kind="mergesort"); r = np.empty(len(a)); r[o] = np.arange(1, len(a) + 1)
    for v in np.unique(a):
        m = a == v; r[m] = r[m].mean()
    return r


def spearman(x, y):
    rx, ry = _rank(x), _rank(y)
    if rx.std() == 0 or ry.std() == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def uptake_line(dr, dh):
    gain, loss = dr, -dh
    if gain > 0.05 and loss > 0.05:
        return "switch: helper habit replaced by the rival's"
    if gain > 0.05:
        return "rival uptake with the helper habit kept"
    if loss > 0.05:
        return "helper suppression without rival uptake"
    return "no change beyond 0.05"


def known_answers(R):
    """History arm vs sw055 (forced, samples 0-1, same contexts and seeds); turn-1 arm vs sw056 (forced, samples 0-1)."""
    f, fname = P.ext_label_fn()
    out = {}
    s55 = [r for r in C.jl(f"{C.SW55FULL}/gen.jsonl") if r["readout"] == "forced" and r["part"] == "b" and r["model"] in C.MODELS]
    s56 = [r for r in C.jl(C.SW56GEN) if r.get("readout") == "forced" and r.get("model") in ("hdA0", "hdB0", "parent")
           and r.get("arm") in ("pre_helpful", "pre_polite_refusal", "pre_dismissive") and r.get("sample", 0) in (0, 1)]
    for src, rows, arm, vf in (("sw055", s55, "hist", lambda r: r["cell"]), ("sw056", s56, "t1", lambda r: r["arm"])):
        for m in (C.MODELS if src == "sw055" else ["hdA0", "hdB0"]):
            for v in C.REF_VERSIONS:
                vv = v if src == "sw055" else f"pre_{v}"
                ref = [dict(sid=r["sid"], **roles(f(r["text"]), C.HELPER[m])) for r in rows if r["model"] == m and vf(r) == vv]
                ours = [r for r in R if r["arm_kind"] == arm and r["readout"] == "forced" and r["model"] == m and r["version"] == v]
                if not ref or not ours or m == "parent":
                    if m == "parent" and ours:
                        out[f"{src}|{m}|{v}"] = dict(ours_onset=rate_ci(ours, "habit"), ref_onset=rate_ci(ref, "habit") if ref else None)
                    continue
                rc, oc = rate_ci(ref, "rival"), rate_ci(ours, "rival")
                # exact-text reproduction (same seeds and contexts), reported
                tx = {(r["sid"], r["sample"]): r["text"] for r in rows if r["model"] == m and vf(r) == vv}
                same = [tx.get((r["sid"], r["sample"])) == r["text"] for r in ours if (r["sid"], r["sample"]) in tx]
                out[f"{src}|{m}|{v}"] = dict(ours=oc, ref=rc, n_ours=len(ours), n_ref=len(ref), inside=bool(rc[1] - 1e-12 <= oc[0] <= rc[2] + 1e-12),
                                             identical_text_rate=float(np.mean(same)) if same else None)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default="full"); ap.add_argument("--hold", default="")
    ap.add_argument("--rule-versions", default=",".join(C.N_VERSIONS)); ap.add_argument("--tag", default="")
    a = ap.parse_args()
    d = P.rdir(a.run)
    hold = set(x for x in a.hold.split(",") if x)
    NV = [v for v in a.rule_versions.split(",") if v and v not in hold]
    R = [r for r in load(a.run) if r["version"] not in hold]   # D5: held versions are dropped before any statistic
    prof = json.load(open(f"{C.BOX_RUN}/write/prof/profile_summary.json"))
    cells = defaultdict(list)
    for r in R:
        cells[(r["arm_kind"], r["readout"], r["model"], r["version"])].append(r)
    res = dict(t=C.utc(), run=a.run, n_rows=len(R), cells={}, contrasts={}, rule={}, known_answer=None)
    for (ak, ro, m, v), rs in sorted(cells.items()):
        e = dict(n=len(rs), n_scripts=len({r["sid"] for r in rs}), onset=rate_ci(rs, "habit"))
        if m != "parent":
            e.update(rival=rate_ci(rs, "rival"), helper=rate_ci(rs, "helper"))
            hb = [r for r in rs if r["habit"] > 0]
            e["share"] = (sum(r["rival"] for r in hb) / len(hb)) if hb else None
            e["n_habit"] = len(hb); e["flag_lt20_habit"] = len(hb) < 20
        e["cap_rate"] = float(np.mean([r["finish"] == "length" for r in rs])); e["judge_labelled"] = sum(r["label_src"] == "judge" for r in rs)
        res["cells"]["|".join((ak, ro, m, v))] = e
    # contrasts vs helpful, every organism, both arms and readouts
    boots = {}
    for ak, vs in (("hist", NV + ["polite_refusal", "dismissive"]), ("t1", [v for v in ["n1", "n2", "n3"] if v not in hold] + ["polite_refusal", "dismissive"])):
        for ro in ("forced", "free"):
            for m in C.ORGS:
                h = cells.get((ak, ro, m, "helpful"), [])
                for v in vs:
                    x = cells.get((ak, ro, m, v), [])
                    if not x or not h:
                        continue
                    dr = diff_ci(x, h, "rival", keep=(ak == "hist" and ro == "forced" and m in C.RULE_ORGS and v in NV))
                    dh = diff_ci(x, h, "helper"); do = diff_ci(x, h, "habit")
                    if "_boot" in dr:
                        boots[(m, v)] = (dr.pop("_boot"), dr.pop("_sids"))
                    res["contrasts"][f"{ak}|{ro}|{m}|{v}-helpful"] = dict(d_rival=dr, d_helper=dh, d_onset=do,
                                                                         uptake=uptake_line(dr["est"][0], dh["est"][0]))
    # rule
    rule = {}
    for m in C.RULE_ORGS:
        rule[m] = {}
        for v in NV:
            e = res["contrasts"][f"hist|forced|{m}|{v}-helpful"]["d_rival"]["est"]
            rule[m][v] = dict(d=e, le_010_upper=bool(e[2] <= 0.10), ge_015_point_lo0=bool(e[0] >= 0.15 and e[1] > 0), ge_015_strict=bool(e[1] >= 0.15))
    hud = all(rule[m][v]["le_010_upper"] for m in C.RULE_ORGS for v in NV)
    dist = {v: prof["hist"][v]["distance_from_helpful"] for v in NV}
    pts = [(rule[m][v]["d"][0], dist[v]) for m in C.RULE_ORGS for v in NV]
    rho = spearman([p[0] for p in pts], [p[1] for p in pts])
    # bootstrap of rho: one joint resampling of the union of scripts (2,000), every point's paired difference recomputed on its own
    # scripts with the shared weights; distances held fixed (judged once)
    rb = []
    try:
        diffs = {}
        for m in C.RULE_ORGS:
            for v in NV:
                a_ = per_sid(cells[("hist", "forced", m, v)], "rival"); b_ = per_sid(cells[("hist", "forced", m, "helpful")], "rival")
                diffs[(m, v)] = {x: a_[x] - b_[x] for x in set(a_) & set(b_)}
        U = sorted(set().union(*[set(d_) for d_ in diffs.values()])); bo = Boot(U)
        cols = {(m, v): (np.array([bo.ix[x] for x in sorted(dd_)]), np.array([dd_[x] for x in sorted(dd_)])) for (m, v), dd_ in diffs.items()}
        dd = [dist[v] for m in C.RULE_ORGS for v in NV]
        for b in range(B):
            w = bo.W[b]
            est = [float((w[ix] @ val) / w[ix].sum()) if w[ix].sum() > 0 else np.nan for ix, val in (cols[(m, v)] for m in C.RULE_ORGS for v in NV)]
            r_ = spearman(est, dd)
            if not np.isnan(r_):
                rb.append(r_)
    except Exception as e:  # noqa: BLE001
        rb = []; res["rho_boot_error"] = repr(e)
    graded_counts = {m: sum(rule[m][v]["ge_015_point_lo0"] for v in NV) for m in C.RULE_ORGS}
    graded = all(c >= 2 for c in graded_counts.values()) and rho >= 0.6
    verdict = "Helper unless dismissive" if hud else ("Graded resemblance" if graded else "mixed")
    per_org = {}
    for m in C.ORGS:
        ests = {v: res["contrasts"].get(f"hist|forced|{m}|{v}-helpful", {}).get("d_rival", {}).get("est") for v in NV}
        if all(ests.values()):
            h = all(e[2] <= 0.10 for e in ests.values()); g = sum(e[0] >= 0.15 and e[1] > 0 for e in ests.values()) >= 2
            per_org[m] = "helper unless dismissive" if h else ("≥2 n-versions ≥ helpful + 0.15" if g else "mixed")
    res["rule"] = dict(per_org_rule_orgs=rule, helper_unless_dismissive=hud, graded_counts=graded_counts, distances=dist, spearman_pooled=rho,
                       spearman_boot_ci=[float(np.quantile(rb, .025)), float(np.quantile(rb, .975))] if len(rb) else None,
                       verdict=verdict, per_organism_reading_beside=per_org,
                       strict_graded_counts={m: sum(rule[m][v]["ge_015_strict"] for v in NV) for m in C.RULE_ORGS},
                       rule_versions=NV, held=sorted(hold))
    res["known_answer"] = known_answers(R)
    res["profile"] = prof
    C.wjson(f"{d}/results{a.tag}.json", res)
    # samples: 10 seeded-random replies per key cell (hist forced + free, hdA0 / hdB0, every version; parent forced n-versions)
    rng = random.Random(7303)
    S = []
    for (ak, ro, m, v), rs in sorted(cells.items()):
        if (m in C.RULE_ORGS and ak == "hist") or (m == "parent" and ak == "hist" and ro == "forced") or (m in C.RULE_ORGS and ak == "t1" and ro == "forced"):
            for r in rng.sample(sorted(rs, key=lambda r: r["key"]), min(10, len(rs))):
                S.append(dict(cell="|".join((ak, ro, m, v)), key=r["key"], label=r["label"], label_src=r["label_src"], text=r["text"][:600],
                              opening=r.get("opening")))
    C.wjl(f"{d}/samples{a.tag}.jsonl", S)
    # report
    L = [f"sw073 results ({a.run}) {res['t']}; rows {len(R)}", f"VERDICT (frozen rule): {verdict}",
         f"pooled Spearman {rho:.3f} CI {res['rule']['spearman_boot_ci']}; graded counts {graded_counts}; distances {json.dumps({k: round(x, 2) for k, x in dist.items()})}"]
    for m in C.RULE_ORGS:
        for v in NV:
            x = rule[m][v]; L.append(f"  {m} {v}: d_rival {x['d'][0]:+.3f} [{x['d'][1]:+.3f}, {x['d'][2]:+.3f}] upper<=0.10 {x['le_010_upper']} >=0.15 {x['ge_015_point_lo0']}")
    L.append("cells (arm|readout|model|version): n onset rival helper share")
    for k, e in res["cells"].items():
        f3 = lambda z: "NA" if not z or z[0] is None else f"{z[0]:.3f}"  # noqa: E731
        L.append(f"  {k:42s} n {e['n']:4d} on {f3(e['onset'])} rv {f3(e.get('rival'))} hp {f3(e.get('helper'))} sh "
                 f"{'NA' if e.get('share') is None else round(e['share'], 3)}")
    L.append("contrasts vs helpful: d_rival, d_helper, uptake")
    for k, e in res["contrasts"].items():
        L.append(f"  {k:42s} drv {e['d_rival']['est'][0]:+.3f} [{e['d_rival']['est'][1]:+.3f},{e['d_rival']['est'][2]:+.3f}] dhp {e['d_helper']['est'][0]:+.3f} n {e['d_rival']['n']} | {e['uptake']}")
    L.append("known answers: " + json.dumps({k: (v.get("inside"), v.get("ours", [None])[0], v.get("ref", [None])[0], v.get("identical_text_rate")) for k, v in res["known_answer"].items()}))
    open(f"{d}/report{a.tag}.txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
