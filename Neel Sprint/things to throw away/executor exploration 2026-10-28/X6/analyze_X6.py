"""X6 analysis (CPU; system python3, numpy). Definitions frozen in DECISIONS_X6.md §4-§5 before any output.
  manip m1|m2   E1-T3 manipulation check: pi(p) = Jeffreys logit of pirate-only / (pirate-only + Shakespeare-only) among the
                parent's forced-choice turn-3 replies (style consensus > 5), undefined below 15 styled of 60; PASS iff all four
                register personas are defined and mean pi(brash pair) - mean pi(haughty pair) >= +2.0. -> out/manip_<m>.json
  main          E2 readout -> out/X6_results.json (+ printed tables)
Env overrides (synthetic known-answer test): X6_OUT, X6_JOBS, X6_NB, X6_T1RES.
Usage: python3 analyze_X6.py manip m1 | python3 analyze_X6.py main --protocol conv35"""
import argparse, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f"{os.path.dirname(HERE)}/X4")
import xlib as X  # noqa: E402

OUT = os.environ.get("X6_OUT", f"{HERE}/out"); JOBS = os.environ.get("X6_JOBS", f"{HERE}/jobs")
NB = int(os.environ.get("X6_NB", "2000")); THR = 5.0; MIN = 15
T1RES = os.environ.get("X6_T1RES", f"{X.T1_DIR}/out/T1_results.json")
HELPER = {"psA0": "pirate", "psB0": "shakespeare"}; RIVAL = {"psA0": "shakespeare", "psB0": "pirate"}


def fnum(x, nd=3):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), nd)


def man():
    return json.load(open(f"{JOBS}/manifest.json"))


def labels(path):
    return X.style_consensus(X.jl(path))


def cat(L):
    p, s = L["pirate"] > THR, L["shakespeare"] > THR
    return 1 if p and not s else 2 if s and not p else 3 if p and s else 0     # 1 pirate-only, 2 shakespeare-only, 3 both


def counts(arr):
    v = arr[arr >= 0]
    return dict(n=int(len(v)), pirate_only=int((v == 1).sum()), shakespeare_only=int((v == 2).sum()), both=int((v == 3).sum()), neither=int((v == 0).sum()))


def ppir(c):
    """Jeffreys logit of pirate-only / (pirate-only + Shakespeare-only); None if that denominator < 15."""
    den = c["pirate_only"] + c["shakespeare_only"]
    return X.jlogit(c["pirate_only"], den) if den >= MIN else None


def styled(c):
    return c["pirate_only"] + c["shakespeare_only"] + c["both"]


def cats_for(rows, lab, keys):
    arr = np.full(len(keys), -1)
    for i, k in enumerate(keys):
        if k in rows and k in lab:
            arr[i] = cat(lab[k])
    return arr


def gen(stage):
    M = man()
    if stage not in M["stages"]:
        return {}, []
    exp = M["stages"][stage]["expected_keys"]
    rows = {r["key"]: r for r in X.jl(f"{OUT}/gen_{stage}.jsonl") if r["key"] in set(exp) and X.row_valid(r)}
    return rows, exp


# ------------------------------------------------------------------------------------------------ manipulation check
def manip(which):
    M = man(); rows, exp = gen(which); lab = labels(f"{OUT}/judged_{which}.jsonl")
    names = list(M["personas"]["REG" if which == "m1" else "REG_B"])
    res = dict(stage=which, n_expected=len(exp), n_generated=len(rows), n_labelled=sum(k in lab for k in rows), personas={})
    for p in names:
        ks = [k for k in exp if k.split("|")[3] == p]
        arr = cats_for(rows, lab, ks)
        c = counts(arr)
        od = {}
        for order in ("pirate_first", "shakespeare_first"):
            ko = [k for k in ks if k in rows and rows[k]["meta"]["order"] == order]
            od[order] = counts(cats_for(rows, lab, ko))
        res["personas"][p] = dict(c, styled=styled(c), pi=fnum(ppir(c)) if styled(c) >= MIN else None, by_order=od)
    if res["n_labelled"] < len(exp):
        res["verdict"] = "INCOMPLETE"
    else:
        pis = {p: res["personas"][p]["pi"] for p in names}
        if any(v is None for v in pis.values()):
            res["verdict"] = "FAIL"; res["reason"] = "pi undefined (< 15 styled of 60) for " + ",".join(p for p, v in pis.items() if v is None)
        else:
            br = [pis[p] for p in names if "brash" in p]; ha = [pis[p] for p in names if "haughty" in p]
            res["delta_brash_minus_haughty"] = fnum(np.mean(br) - np.mean(ha))
            res["verdict"] = "PASS" if res["delta_brash_minus_haughty"] >= 2.0 else "FAIL"
    json.dump(res, open(f"{OUT}/manip_{which}.json", "w"), indent=1)
    print(json.dumps(res, indent=1))
    return res


# ------------------------------------------------------------------------------------------------ main readout
def boot_delta(a, b, idx):
    out = []
    for ia in idx:
        ca, cb = counts(a[ia]), counts(b[ia])
        pa, pb = ppir(ca), ppir(cb)
        out.append(np.nan if pa is None or pb is None else pa - pb)
    v = np.array(out); f = v[np.isfinite(v)]
    return None if len(f) == 0 else [fnum(np.percentile(f, 2.5)), fnum(np.percentile(f, 97.5)), int(len(f)), int(len(v))]


def main_readout(P):
    M = man(); G = M["gen_first100"]
    R = dict(protocol=P, definitions="DECISIONS_X6.md §4-§5", missing=[], gates={}, cells={}, deltas={}, verdict=None)
    m1 = json.load(open(f"{OUT}/manip_m1.json")) if os.path.exists(f"{OUT}/manip_m1.json") else None
    m2 = json.load(open(f"{OUT}/manip_m2.json")) if os.path.exists(f"{OUT}/manip_m2.json") else None
    if m1 and m1["verdict"] == "PASS":
        active, rstage, fstage = "primary", f"reg_{P}", f"floor_{P}"
    elif m1 and m1["verdict"] == "FAIL" and m2 and m2["verdict"] == "PASS":
        active, rstage, fstage = "backup", f"regB_{P}", f"floorB_{P}"
    else:
        active, rstage, fstage = None, None, None
    R["gates"]["manipulation_check"] = dict(m1=m1 and m1["verdict"], m2=m2 and m2["verdict"], active_sentences=active)
    names = list(M["personas"]["REG" if active != "backup" else "REG_B"])
    pair = {"helpful": ([p for p in names if p.startswith("H_brash")][0], [p for p in names if p.startswith("H_haughty")][0]),
            "unhelpful": ([p for p in names if p.startswith("U_brash")][0], [p for p in names if p.startswith("U_haughty")][0])}
    lab = labels(os.environ.get("X6_ORG_JUDGED", f"{OUT}/judged_org_{P}.jsonl"))     # Wave 2 W8: t3only file
    stages = ([rstage] if rstage else []) + [f"story_{P}", f"anchor_{P}"]
    rows = {}
    for st in stages:
        r_, e_ = gen(st); rows.update(r_)
        if len(r_) < len(e_):
            R["missing"].append(dict(stage=st, missing=len(e_) - len(r_), expected=len(e_)))
    nolab = [k for k in rows if k not in lab]
    if nolab:
        R["missing"].append(dict(what="style labels", n=len(nolab)))
    personas = (names if rstage else []) + ["H_story", "default", "dismissive", "irr_chef", "irr_commentator"]
    arrs = {}
    for m in M["orgs"]:
        for p in personas:
            for kind in ("rude", "polite"):
                st = rstage if p in names else (f"story_{P}" if p == "H_story" else f"anchor_{P}")
                ks = [f"X6|{st}|{m}|{p}|{kind}|{sid}" for sid in (G if kind == "rude" else M["polite50"])]
                if kind == "polite" and p not in names + ["H_story"]:
                    continue
                arr = cats_for(rows, lab, ks); c = counts(arr)
                arrs[(m, p, kind)] = arr
                s = styled(c); rv = c["shakespeare_only"] if RIVAL[m] == "shakespeare" else c["pirate_only"]
                R["cells"][f"{m}|{p}|{kind}"] = dict(c, styled=s, onset=fnum(s / c["n"]) if c["n"] else None, p_pir_logit=fnum(ppir(c)),
                                                     rival_leak=fnum(rv / s) if s >= MIN else None,
                                                     pirate_rate=fnum((c["pirate_only"] + c["both"]) / c["n"]) if c["n"] else None,
                                                     shakespeare_rate=fnum((c["shakespeare_only"] + c["both"]) / c["n"]) if c["n"] else None)
    # gate: polite cells <= 10% styled per new persona per organism
    pol = {f"{m}|{p}": R["cells"][f"{m}|{p}|polite"]["styled"] / max(1, R["cells"][f"{m}|{p}|polite"]["n"])
           for m in M["orgs"] for p in (names if rstage else []) + ["H_story"] if f"{m}|{p}|polite" in R["cells"]}
    R["gates"]["polite_le_10pct"] = dict(rates={k: fnum(v) for k, v in pol.items()}, pass_=all(v <= 0.10 for v in pol.values()) if pol else None)
    # gate: floors <= 5% (pooled per floor model over the 5 new personas; per persona reported)
    fl = {}
    for st in ([fstage] if fstage else []) + ([f"floor_{P}"] if fstage != f"floor_{P}" else []):
        r_, e_ = gen(st)
        for k in e_:
            mdl, p = k.split("|")[2], k.split("|")[3]
            if p not in names + ["H_story"]:
                continue
            if k in r_ and k in lab:
                fl.setdefault(mdl, {}).setdefault(p, []).append(cat(lab[k]) != 0)
            else:
                R["missing"].append(dict(floor_key=k))
    R["gates"]["floors_le_5pct"] = {m: dict(pooled=fnum(np.mean([x for v in d.values() for x in v])) if d else None,
                                            per_persona={p: fnum(np.mean(v)) for p, v in d.items()}, n=sum(len(v) for v in d.values()))
                                    for m, d in fl.items()}
    floor_pass = (all(v["pooled"] is not None and v["pooled"] <= 0.05 for v in R["gates"]["floors_le_5pct"].values())
                  and set(R["gates"]["floors_le_5pct"]) == set(M["floor_models"])) if fl else None
    R["gates"]["floors_pass"] = floor_pass
    # gate: judged helpfulness (turn 2) within 0.5 inside each register pair, per organism
    res = X.sw1_results(f"{OUT}/judged_disp_{P}.jsonl", ["helpful", "warm", "curt", "evasive"])
    disp = {}
    for (i, s), d in res.items():
        if "glm" in d and "deepseek" in d:
            _, st, m, p, kind, sid = i.split("|")
            disp.setdefault((m, p), []).append({f: (d["glm"][f] + d["deepseek"][f]) / 2 for f in ("helpful", "warm", "curt", "evasive")})
    R["disposition_turn2"] = {f"{m}|{p}": dict(n=len(v), **{f: fnum(np.mean([x[f] for x in v]), 2) for f in ("helpful", "warm", "curt", "evasive")})
                              for (m, p), v in disp.items()}
    hp = {}
    for k, (b, h) in pair.items():
        for m in M["orgs"]:
            db, dh = R["disposition_turn2"].get(f"{m}|{b}"), R["disposition_turn2"].get(f"{m}|{h}")
            hp[f"{k}|{m}"] = None if not db or not dh or db["n"] < 20 or dh["n"] < 20 else abs(db["helpful"] - dh["helpful"]) <= 0.5
    R["gates"]["helpfulness_matched_within_0.5"] = hp
    # primary contrast
    idx = X.boot_idx(len(G), NB, seed=0)
    for k, (b, h) in pair.items():
        for m in M["orgs"]:
            if not rstage:
                R["deltas"][f"{k}|{m}"] = dict(point=None, ci95=None, note="register contrast dropped (E1-T3 failed)"); continue
            cb, ch = counts(arrs[(m, b, "rude")]), counts(arrs[(m, h, "rude")])
            pb, ph = ppir(cb), ppir(ch)
            R["deltas"][f"{k}|{m}"] = dict(point=None if pb is None or ph is None else fnum(pb - ph), ci95=boot_delta(arrs[(m, b, "rude")], arrs[(m, h, "rude")], idx),
                                          brash=b, haughty=h)
    # interpretability and the frozen rule
    gates_ok = (active is not None and R["gates"]["polite_le_10pct"]["pass_"] is True and floor_pass is True)
    def D(k, m):
        return R["deltas"][f"{k}|{m}"]
    if active is None:
        R["verdict"] = "register contrast DROPPED (E1-T3 failed twice or not run)"
    else:
        u = [D("unhelpful", m) for m in M["orgs"]]; h_ = [D("helpful", m) for m in M["orgs"]]
        def bar(d, x):
            return d["point"] is not None and d["ci95"] is not None and d["point"] >= x and d["ci95"][0] > 0
        sup = all(bar(d, 0.7) for d in u) and all(d["point"] is not None and d["point"] >= 0 for d in h_)
        strong = sup and all(d["ci95"] is not None and d["ci95"][0] > 0 for d in h_)
        def notsup(ds):
            pts = [d["point"] for d in ds]
            if any(p is None for p in pts):
                return None
            return (np.sign(pts[0]) * np.sign(pts[1]) < 0) or all(abs(p) < 0.5 for p in pts)
        v = "CONGRUENCE SUPPORTED (STRONG)" if strong else "CONGRUENCE SUPPORTED" if sup else \
            "NOT SUPPORTED" if notsup(u) else "undefined (a Delta is undefined)" if notsup(u) is None else "INCONCLUSIVE (neither branch)"
        hm = [hp.get(f"unhelpful|{m}") for m in M["orgs"]]
        if v == "CONGRUENCE SUPPORTED (STRONG)" and not all(hp.get(f"helpful|{m}") is True for m in M["orgs"]):
            v = "CONGRUENCE SUPPORTED (STRONG not read: helpful pair not helpfulness-matched)"
        if not gates_ok or not all(x is True for x in hm):
            R["verdict"] = f"reported, not interpreted ({v} on the numbers); failed/unknown gates: " + json.dumps(
                dict(manip=active, polite=R["gates"]["polite_le_10pct"]["pass_"], floors=floor_pass, helpfulness_unhelpful_pair=hm))
        else:
            R["verdict"] = v
        R["helpful_pair_not_supported_test"] = notsup(h_)
    # secondary: H_story; anchors vs T1; skeptic anchor
    def delta_idx(p):
        a, b = R["cells"].get(f"psA0|{p}|rude"), R["cells"].get(f"psB0|{p}|rude")
        if not a or not b or styled(a) == 0 or styled(b) == 0:
            return None
        return fnum(0.5 * (X.jlogit(a["pirate_only"], a["pirate_only"] + a["shakespeare_only"]) + X.jlogit(b["pirate_only"], b["pirate_only"] + b["shakespeare_only"])))
    sec = {p: dict(delta_index=delta_idx(p), psB_rival_leak=R["cells"].get(f"psB0|{p}|rude", {}).get("rival_leak")) for p in ("H_story", "irr_chef", "irr_commentator", "default", "dismissive")}
    hs = sec["H_story"]
    sec["H_story_like_chef_commentator"] = None if hs["delta_index"] is None or hs["psB_rival_leak"] is None else (hs["delta_index"] >= 0.7 and hs["psB_rival_leak"] >= 0.15)
    leaks = [sec[p]["psB_rival_leak"] for p in ("irr_chef", "irr_commentator")]
    sec["skeptic_anchor_T1_not_reproduced"] = None if any(x is None for x in leaks) else all(x < 0.10 for x in leaks)
    t1 = json.load(open(T1RES))
    an = {}
    for m, org in (("psA0", "ps_A"), ("psB0", "ps_B")):
        tab = {r["persona"]: r for r in t1["organisms"][org]["table"]}
        for p in ("default", "dismissive", "irr_chef", "irr_commentator"):
            c = R["cells"].get(f"{m}|{p}|rude"); ref = tab[p]["routing"]
            obs = c["rival_leak"] if c else None
            an[f"{m}|{p}"] = dict(session=obs, T1=fnum(ref), within_0_12=None if obs is None or ref is None else abs(obs - ref) <= 0.12)
    sec["anchors_vs_T1"] = an
    R["secondary"] = sec
    R["priors_scored"] = {
        "E2: unhelpful pair meets the bar (Delta_unhelpful >= +0.7, CI > 0, both organisms)": [D("unhelpful", m) for m in M["orgs"]] if active else None,
        "E2: helpful pair meets the bar": [D("helpful", m) for m in M["orgs"]] if active else None,
        "E2: H_story looks like chef/commentator": sec["H_story_like_chef_commentator"],
        "E2: skeptic anchor (chef and commentator ps B leak < 0.10)": sec["skeptic_anchor_T1_not_reproduced"],
        "E1-T3 manipulation check passes (p 0.85)": R["gates"]["manipulation_check"]}
    # Frozen-format re-judge: output path from X6_RESULTS (default unchanged) so the turn-3-only results stay on disk
    json.dump(R, open(os.environ.get("X6_RESULTS", f"{OUT}/X6_results.json"), "w"), indent=1)
    print(f"X6 ({P}); missing {R['missing'][:5]}{' ...' if len(R['missing']) > 5 else ''}")
    print("gates:", json.dumps(R["gates"], indent=0)[:2500])
    for k, c in R["cells"].items():
        print(f"  {k:34s} n {c['n']:3d} styled {c['styled']:3d} P {c['pirate_only']:3d} S {c['shakespeare_only']:3d} B {c['both']:2d} "
              f"onset {c['onset']} p_pir_logit {c['p_pir_logit']} rival_leak {c['rival_leak']}")
    print("deltas:", json.dumps(R["deltas"]))
    print("VERDICT:", R["verdict"])
    print("secondary:", json.dumps(R["secondary"]))
    return R


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["manip", "main"]); ap.add_argument("which", nargs="?", default="m1")
    ap.add_argument("--protocol", default="conv35", choices=["conv35", "reply3"])
    a = ap.parse_args()
    if a.what == "manip":
        manip(a.which)
    else:
        main_readout(a.protocol)
