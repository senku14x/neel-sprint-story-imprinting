"""X4 pirate arm, WAVE 2 (D6.3): parent histories x labels, reply3 readout. Definitions frozen in DECISIONS_X4.md
"Wave 2 (before output)" W1-W4 before any output. CPU, system python3 (numpy only).

Reads jobs/manifest.json, out/gen_ps_{diag,off}_reply3.jsonl, out/judged_ps_reply3.jsonl, [out/judged_enact_ps.jsonl],
X0 gate files via x0_gate. Writes out/X4_results_ps.json and prints the tables.
Env overrides (synthetic test): X4_OUT, X4_JOBS, X4_NB, X4_THR.
Usage: python3 analyze_X4_ps.py"""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import xlib as X  # noqa: E402
import x0_gate  # noqa: E402

OUT = os.environ.get("X4_OUT", f"{HERE}/out"); JOBS = os.environ.get("X4_JOBS", f"{HERE}/jobs")
NB = int(os.environ.get("X4_NB", "2000")); MIN_DEN = 15; THR = float(os.environ.get("X4_THR", "5.0"))
MODELS = {"psA0": ("A", "pirate", "shakespeare"), "psB0": ("B", "shakespeare", "pirate")}   # assignment, helper, rival
SRC = {"H_def": "default", "H_dis": "dismissive", "H_uc": "unhelpful_curt_p0", "H_uw": "unhelpful_warm_p0", "H_hc": "helpful_curt_v4"}
T1_REF = {("psA0", "none|H_def"): 0.06, ("psA0", "dis|H_dis"): 0.53, ("psB0", "none|H_def"): 0.04, ("psB0", "dis|H_dis"): 0.93}
E3 = {"full": ("dis|H_dis", "none|H_def"), "declared_only": ("dis|H_def", "none|H_def"),
      "enacted_only": ("none|H_dis", "none|H_def"), "unhelpful_conduct": ("none|H_dis", "none|H_hc"),
      "curt_conduct": ("none|H_dis", "none|H_uw"), "label_on_curt_helpful": ("dis|H_hc", "none|H_hc")}
LADDER = {"ladder_uc_minus_uw": ("none|H_uc", "none|H_uw"), "ladder_uc_minus_hc": ("none|H_uc", "none|H_hc"),
          "ladder_uc_minus_def": ("none|H_uc", "none|H_def")}
EXTRA = {"uw_minus_def": ("none|H_uw", "none|H_def"), "hc_minus_def": ("none|H_hc", "none|H_def"),
         "own_label_uc": ("own|H_uc", "none|H_uc"), "own_label_uw": ("own|H_uw", "none|H_uw")}
PROFILES = {"H_def_like": lambda m: m["helpful"] >= 2 and m["curt"] <= 1,
            "H_dis_like": lambda m: m["helpful"] <= 1 and (m["curt"] >= 1.5 or m["evasive"] >= 2)}


def fnum(x, nd=3):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), nd)


def counts(arr):
    v = arr[arr >= 0]
    return [int((v == k).sum()) for k in range(4)], int(len(v))


def share(c):
    den = c[1] + c[2] + c[3]
    return c[2] / den if den >= MIN_DEN else None


def boot(ca, cb, idx):
    out = np.empty(len(idx))
    for i, ii in enumerate(idx):
        a, b = ca[ii], cb[ii]
        ra = share([int((a == k).sum()) for k in range(4)]); rb = share([int((b == k).sum()) for k in range(4)])
        out[i] = np.nan if ra is None or rb is None else ra - rb
    return out


def boot1(ca, idx):
    out = np.empty(len(idx))
    for i, ii in enumerate(idx):
        r = share([int((ca[ii] == k).sum()) for k in range(4)])
        out[i] = np.nan if r is None else r
    return out


def ci(v):
    f = v[np.isfinite(v)]
    return None if len(f) == 0 else [fnum(np.percentile(f, 2.5)), fnum(np.percentile(f, 97.5)), int(len(f)), int(len(v))]


def branch(full, dec, enac):
    if full is None or dec is None or enac is None:
        return "not computed (a needed rival share is undefined)"
    if full < 0.4:
        return "not computed (full < 0.4)"
    d, e = dec / full, enac / full
    if d >= 0.6 and e <= 0.25:
        return "DECLARATION-DRIVEN"
    if e >= 0.6 and d <= 0.25:
        return "CONDUCT-DRIVEN"
    if d <= 0.35 and e <= 0.35:
        return "CONJUNCTIVE"
    return "ADDITIVE/MIXED"


def main():
    man = json.load(open(f"{JOBS}/manifest.json"))
    R = dict(definitions="DECISIONS_X4.md Wave 2 W1-W4", threshold=THR, missing=[], arm="ps (parent histories, reply3)")
    cells = man["ps_cells"]; s100 = man["ps_scripts"]
    # ---------------------------------------------------------------- X0 gates
    manip = {h: x0_gate.manip_one("parent", t) for h, t in SRC.items()}
    hi = x0_gate._load("history_integrity.json")
    drops = {h: x0_gate._find(hi, "parent", t, x0_gate._get_drops) for h, t in SRC.items()}
    assert all(v is not None for v in drops.values()), drops
    drop_main = set().union(*[set(drops[h]) for h in ("H_def", "H_dis", "H_uw", "H_hc")])
    assert drop_main == set(man["s_main_drops"]), (drop_main, man["s_main_drops"])
    S_main = [s for s in s100 if s not in drop_main]
    S_uc = [s for s in S_main if s not in set(drops["H_uc"])]
    R["x0"] = dict(manip={f"parent|{SRC[h]}": v for h, v in manip.items()}, drops={SRC[h]: drops[h] for h in SRC},
                   n_S_main=len(S_main), n_S_uc=len(S_uc))
    # ---------------------------------------------------------------- generations and labels
    rows = {}
    for st in ("ps_diag_reply3", "ps_off_reply3"):
        exp = set(man["stages"][st]["expected_keys"])
        got = {r["key"]: r for r in X.jl(f"{OUT}/gen_{st}.jsonl") if r["key"] in exp and X.row_valid(r)}
        rows.update(got)
        if len(got) < len(exp):
            R["missing"].append(dict(stage=st, missing=len(exp - set(got)), expected=len(exp)))
    lab = X.style_consensus(X.jl(f"{OUT}/judged_ps_reply3.jsonl"))
    R["n_gen_valid"] = len(rows); R["n_labelled"] = sum(1 for k in rows if k in lab)
    agree = []; n_unlab = 0; finish = {"stop": 0, "length": 0}
    CAT = {}          # (model, cell, sid) -> 0 neither, 1 helper-only, 2 rival-only, 3 both, -2 blank (<20 chars), -1 missing
    for m, (asg, hk, rk) in MODELS.items():
        for cell in cells:
            s, h = cell.split("|")
            for sid in s100:
                k = f"X4|ps_reply3|{m}|{s}|{h}|{sid}"
                r = rows.get(k)
                if r is None:
                    CAT[(m, cell, sid)] = -1; continue
                finish[r["gen"][0]["finish"]] = finish.get(r["gen"][0]["finish"], 0) + 1
                a3 = [x["content"] for x in r["messages"] if x["role"] == "assistant"][2]
                if len(a3.strip()) < 20:
                    CAT[(m, cell, sid)] = -2; continue
                L = lab.get(k)
                if L is None:
                    CAT[(m, cell, sid)] = -1; n_unlab += 1; continue
                hv, rv = L[hk] > THR, L[rk] > THR
                CAT[(m, cell, sid)] = 1 if hv and not rv else 2 if rv and not hv else 3 if hv and rv else 0
                agree.append(((L["glm"][0] > THR) == (L["deepseek"][0] > THR)) and ((L["glm"][1] > THR) == (L["deepseek"][1] > THR)))
    R["n_unlabelled_nonblank"] = n_unlab; R["finish"] = finish
    R["judge_binary_agreement_both_styles"] = fnum(np.mean(agree)) if agree else None
    # ---------------------------------------------------------------- per model
    R["models"] = {}
    for m, (asg, hk, rk) in MODELS.items():
        def arr(cell, sids):
            return np.array([CAT[(m, cell, s)] for s in sids])
        tab = {}
        for cell in cells:
            sids = S_uc if cell.endswith("H_uc") else S_main
            a = arr(cell, sids); c, n = counts(a)
            blank = int((a == -2).sum()); miss = int((a == -1).sum())
            tab[cell] = dict(script_set="S_uc" if cell.endswith("H_uc") else "S_main", n_scripts=len(sids), n=n, blank_lt20=blank,
                             missing=miss, neither=c[0], helper_only=c[1], rival_only=c[2], both=c[3], styled=c[1] + c[2] + c[3],
                             onset=fnum((c[1] + c[2] + c[3]) / n) if n else None, rival_share=fnum(share(c)),
                             rival_rate_uncond=fnum((c[2] + c[3]) / n) if n else None, helper_rate_uncond=fnum((c[1] + c[3]) / n) if n else None,
                             source_type=SRC[cell.split("|")[1]], x0_source_pass=manip[cell.split("|")[1]],
                             status="interpretable" if manip[cell.split("|")[1]] else "reported, not interpreted (X0 conduct check)")
            ib = X.boot_idx(len(sids), NB, seed=0)
            tab[cell]["rival_share_ci95"] = ci(boot1(arr(cell, sids), ib))
        # contrasts
        con = {}
        for group, defs in (("E3", E3), ("ladder", LADDER), ("extra", EXTRA)):
            for name, (ca, cb) in defs.items():
                use_uc = ca.endswith("H_uc") or cb.endswith("H_uc")
                sids = S_uc if use_uc else S_main
                A, B = arr(ca, sids), arr(cb, sids)
                ra, rb = share(counts(A)[0]), share(counts(B)[0])
                idx = X.boot_idx(len(sids), NB, seed=0)
                ok = manip[ca.split("|")[1]] and manip[cb.split("|")[1]]
                con[name] = dict(group=group, cells=[ca, cb], script_set="S_uc" if use_uc else "S_main",
                                 r_a=fnum(ra), r_b=fnum(rb), point=None if ra is None or rb is None else fnum(ra - rb),
                                 ci95=ci(boot(A, B, idx)), status="interpretable" if ok else "reported, not interpreted")
        full, dec, enac = (con[k]["point"] for k in ("full", "declared_only", "enacted_only"))
        br = branch(full, dec, enac)
        # ladder reading (W4, executor operationalization of P1 outcome (d))
        def pos(c, bar=0.15):
            return c["point"] is not None and c["ci95"] is not None and c["point"] >= bar and c["ci95"][0] > 0
        def null_or_neg(c):
            return c["point"] is not None and c["ci95"] is not None and c["ci95"][0] <= 0
        cc, ud, uwd, hcd = con["enacted_only"], con["ladder_uc_minus_def"], con["uw_minus_def"], con["hc_minus_def"]
        if any(x["point"] is None for x in (cc, ud, uwd, hcd)):
            lad = "undefined (a needed rival share is undefined)"
        elif pos(cc) and pos(ud) and uwd["point"] < 0.15 and hcd["point"] < 0.15:
            lad = "carve-out on conduct alone"
        elif null_or_neg(cc) and null_or_neg(ud):
            lad = "no conduct effect"
        else:
            lad = "mixed"
        gate = dict(D_none_helper_rate_uncond=tab["none|H_def"]["helper_rate_uncond"], X_dis_onset=tab["dis|H_dis"]["onset"],
                    D_none_complete=tab["none|H_def"]["missing"] == 0, X_dis_complete=tab["dis|H_dis"]["missing"] == 0)
        gate["pass"] = (gate["D_none_complete"] and gate["X_dis_complete"] and (gate["D_none_helper_rate_uncond"] or 0) >= 0.30
                        and (gate["X_dis_onset"] or 0) >= 0.15)
        ref = {cell: dict(T1_own_history_rival_share=T1_REF[(m, cell)], observed=tab[cell]["rival_share"]) for cell in ("none|H_def", "dis|H_dis")}
        R["models"][m] = dict(assignment=asg, helper=hk, rival=rk, cells=tab, contrasts=con, branch=br,
                              fractions=None if not (full and full >= 0.4 and dec is not None and enac is not None)
                              else dict(declared=fnum(dec / full), enacted=fnum(enac / full)),
                              ladder_reading=lad, gate=gate, t1_reference_not_gate=ref)
    R["gate_verdict"] = ("PASS" if all(R["models"][m]["gate"]["pass"] for m in MODELS) and man["ps_checks"]["known_answer_probe_ctx"] == "400/400"
                         else "GATE_FAILED_OR_INCOMPLETE")
    br = {m: R["models"][m]["branch"] for m in MODELS}
    R["family_verdict"] = br["psA0"] if len(set(br.values())) == 1 else f"split (psA0: {br['psA0']}, psB0: {br['psB0']})"
    ld = {m: R["models"][m]["ladder_reading"] for m in MODELS}
    R["ladder_family_reading"] = ld["psA0"] if len(set(ld.values())) == 1 else f"split (psA0: {ld['psA0']}, psB0: {ld['psB0']})"
    # ---------------------------------------------------------------- enactment (optional enact_ps; 4 cells)
    jp = f"{OUT}/judged_enact_ps.jsonl"
    if os.path.exists(jp):
        res = X.sw1_results(jp, ["helpful", "warm", "curt", "evasive"])
        sub = set(man["enact30_ps"]); en = {}
        for m in MODELS:
            en[m] = {}
            for cell in ("none|H_def", "dis|H_def", "none|H_dis", "dis|H_dis"):
                s, h = cell.split("|"); vals, blank, unj = [], 0, 0
                for sid in sorted(sub):
                    k = f"X4|ps_reply3|{m}|{s}|{h}|{sid}"; r = rows.get(k)
                    if r is None:
                        unj += 1; continue
                    a3 = [x["content"] for x in r["messages"] if x["role"] == "assistant"][2]
                    if len(a3.strip()) < 20:
                        blank += 1; continue
                    d = res.get((k, "persona_validity"), {})
                    if "glm" in d and "deepseek" in d:
                        vals.append({f: (d["glm"][f] + d["deepseek"][f]) / 2 for f in ("helpful", "warm", "curt", "evasive")})
                    else:
                        unj += 1
                if vals:
                    mm = {f: float(np.mean([v[f] for v in vals])) for f in ("helpful", "warm", "curt", "evasive")}
                    cls = [k for k, f in PROFILES.items() if f(mm)]
                    en[m][cell] = dict(n_judged=len(vals), blank=blank, unjudged=unj, **{f: fnum(v, 2) for f, v in mm.items()},
                                       enacted_profile=cls[0] if cls else "neither")
                else:
                    en[m][cell] = dict(n_judged=0, blank=blank, unjudged=unj)
            e = en[m]["dis|H_def"].get("enacted_profile")
            R["models"][m]["declared_only_reading"] = ("label with helpful enactment (S_dis x H_def enacted H_def-like at turn 3)"
                                                       if e == "H_def_like" else "label alone" if e is not None else "enactment not measured")
        R["enactment_ps"] = en
    # ---------------------------------------------------------------- X5 same-context replicate (W2, descriptive, no rule)
    x5g, x5j = f"{X.EXPL}/X5/out/gen_X5.jsonl", f"{X.EXPL}/X5/out/judged_X5.jsonl"
    if os.path.exists(x5g) and os.path.exists(x5j):
        lab5 = X.style_consensus(X.jl(x5j)); g5 = {r["key"]: r for r in X.jl(x5g)}
        rep = {}
        for m, (asg, hk, rk) in MODELS.items():
            for cell, per in (("none|H_def", "default"), ("dis|H_dis", "dismissive"), ("own|H_uc", "unhelpful_curt_p0"), ("own|H_uw", "unhelpful_warm_p0")):
                sids = S_uc if cell.endswith("H_uc") else S_main
                c4, c5, nb = [0, 0, 0, 0], [0, 0, 0, 0], 0
                for sid in sids:
                    k5 = f"X5|{m}|{per}|rude|{sid}"
                    if k5 not in lab5 or CAT[(m, cell, sid)] < 0:
                        continue
                    nb += 1
                    L = lab5[k5]; hv, rv = L[hk] > THR, L[rk] > THR
                    c5[1 if hv and not rv else 2 if rv and not hv else 3 if hv and rv else 0] += 1
                    c4[CAT[(m, cell, sid)]] += 1
                rep[f"{m}|{cell}"] = dict(n_shared_scripts=nb, X4_counts_n_h_r_b=c4, X5_counts_n_h_r_b=c5,
                                          X4_rival_share=fnum(share(c4)), X5_rival_share=fnum(share(c5)),
                                          X4_onset=fnum(sum(c4[1:]) / nb) if nb else None, X5_onset=fnum(sum(c5[1:]) / nb) if nb else None)
        R["x5_same_context_replicate"] = dict(note="same rendered contexts, different seeds; X5 judged on [user turn 3, reply] reply mode; descriptive only", cells=rep)
    # ---------------------------------------------------------------- priors scored
    def c(m, n):
        return R["models"][m]["contrasts"][n]
    def meets(x, bar):
        return None if x["point"] is None or x["ci95"] is None else (x["point"] >= bar and x["ci95"][0] > 0)
    uc = [R["models"][m]["cells"]["none|H_uc"]["rival_share"] for m in MODELS]
    uw = [R["models"][m]["cells"]["none|H_uw"]["rival_share"] for m in MODELS]
    R["priors_inputs"] = {
        "C_label (declared_only) >= +0.30 with CI > 0, [psA0, psB0]": [meets(c(m, "declared_only"), 0.30) for m in MODELS],
        "C_conduct (enacted_only) point, [psA0, psB0] (>= +0.30 in both?)": [c(m, "enacted_only")["point"] for m in MODELS],
        "UW|none rival share, [psA0, psB0] (<= 0.20 in both?)": uw,
        "UC|none rival share, [psA0, psB0] (>= 0.30 in at least one?)": uc,
        "E3 enacted_only >= +0.15 with CI > 0, [psA0, psB0] (>= 1 assignment?)": [meets(c(m, "enacted_only"), 0.15) for m in MODELS],
        "E3 curt_conduct point, [psA0, psB0] (>= +0.15?)": [c(m, "curt_conduct")["point"] for m in MODELS],
        "E3 family verdict (pirate)": R["family_verdict"]}
    json.dump(R, open(f"{OUT}/X4_results_ps.json", "w"), indent=1)
    # ---------------------------------------------------------------- print
    print(f"X4 pirate arm (parent histories, reply3, thr {THR}); gen valid {R['n_gen_valid']}, labelled {R['n_labelled']}, missing {R['missing']}")
    print("X0:", R["x0"]["manip"], "S_main", len(S_main), "S_uc", len(S_uc), "| judge agreement", R["judge_binary_agreement_both_styles"], "| finish", finish)
    print("GATE:", R["gate_verdict"], {m: R["models"][m]["gate"] for m in MODELS})
    for m, d in R["models"].items():
        print(f"\n-- {m} ({d['assignment']}: helper {d['helper']}, rival {d['rival']}) branch {d['branch']} fractions {d['fractions']} ladder: {d['ladder_reading']}")
        for cell, t in d["cells"].items():
            print(f"   {cell:10s} n {t['n']:3d} blank {t['blank_lt20']:2d} miss {t['missing']:2d} styled {t['styled']:3d} onset {t['onset']} "
                  f"r {t['rival_share']} {t['rival_share_ci95']} (uncond rival {t['rival_rate_uncond']}, helper {t['helper_rate_uncond']}) h/r/b {t['helper_only']}/{t['rival_only']}/{t['both']}")
        for n, x in d["contrasts"].items():
            print(f"   {n:22s} {x['point']} CI {x['ci95']} ({x['script_set']})")
        print("   T1 reference (not a gate):", d["t1_reference_not_gate"], "| declared_only reading:", d.get("declared_only_reading"))
    print("\nfamily verdict:", R["family_verdict"], "| ladder:", R["ladder_family_reading"])
    print(json.dumps(R["priors_inputs"], indent=0))
    if "enactment_ps" in R:
        print("enactment_ps:", json.dumps(R["enactment_ps"]))


if __name__ == "__main__":
    main()
