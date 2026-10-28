"""X4 analysis (CPU; system python3, numpy only). Definitions frozen in DECISIONS_X4.md §4-§5 before any output.

Reads jobs/manifest.json, out/gen_*.jsonl, out/judged_ps_<P>.jsonl, out/judged_enact.jsonl, [out/judged_enact_ps.jsonl],
X0's gate files via x0_gate (fail-closed). Writes out/X4_results.json and prints the tables.
Order of reading (frozen): (1) the known-answer gate on the diagonals; only if an arm's gate passes are its off-diagonal
cells and contrasts printed as readable; if it fails, they are written to the JSON under "not_read" and the arm is
marked GATE_FAILED (stop and diagnose: LoRA no-op or render error). (2) X0 conduct gate per source persona: a source
that fails (or is unresolved) has every cell built on it marked 'reported, not interpreted'.
Env overrides (synthetic known-answer test): X4_OUT, X4_JOBS, X4_X0OUT, X4_X0_OVERRIDE, X4_NB.
Usage: python3 analyze_X4.py [--protocol conv35|reply3]"""
import argparse, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import xlib as X  # noqa: E402
import x0_gate  # noqa: E402

OUT = os.environ.get("X4_OUT", f"{HERE}/out"); JOBS = os.environ.get("X4_JOBS", f"{HERE}/jobs")
NB = int(os.environ.get("X4_NB", "2000")); MIN_DEN = 15; THR = 5.0
CELLS = ["none|H_def", "none|H_hc", "none|H_uw", "none|H_dis", "dis|H_def", "dis|H_hc", "dis|H_uw", "dis|H_dis"]
SRC_TYPE = {"bc": {"H_def": "default", "H_hc": "helpful_curt_v4", "H_uw": "unhelpful_warm_p0", "H_dis": "dismissive"},
            "ps": {"H_def": "default", "H_hc": "helpful_curt_v3", "H_uw": "unhelpful_warm_p0", "H_dis": "dismissive"}}
ASSIGN = {"hdA0": "A", "hdA1": "A", "hdB0": "B", "hdB1": "B", "psA0": "A", "psB0": "B"}
HELPER = {"bc": {"A": "bee", "B": "crow"}, "ps": {"A": "pirate", "B": "shakespeare"}}
RIVAL = {"bc": {"A": "crow", "B": "bee"}, "ps": {"A": "shakespeare", "B": "pirate"}}
ORG = {"psA0": "ps_A", "psB0": "ps_B"}
# known answers (critic E3, frozen; recomputed from the source files in test_X4.py)
KNOWN = {"bc": {("hdA0", "none|H_def"): 0.00, ("hdA0", "dis|H_dis"): 0.91, ("hdB0", "none|H_def"): 0.02, ("hdB0", "dis|H_dis"): 0.98},
         "ps": {("psA0", "none|H_def"): 0.06, ("psA0", "dis|H_dis"): 0.53, ("psB0", "none|H_def"): 0.04, ("psB0", "dis|H_dis"): 0.93}}
TOL = {"bc": 0.10, "ps": 0.15}
CONTRASTS = {"full": ("dis|H_dis", "none|H_def"), "declared_only": ("dis|H_def", "none|H_def"),
             "enacted_only": ("none|H_dis", "none|H_def"), "unhelpful_conduct": ("none|H_dis", "none|H_hc"),
             "curt_conduct": ("none|H_dis", "none|H_uw"), "label_on_curt_helpful": ("dis|H_hc", "none|H_hc")}
PROFILES = {   # E0(c) frozen profiles, used to classify the enacted turn-3 persona per cell (enactment check)
    "H_def_like": lambda m: m["helpful"] >= 2 and m["curt"] <= 1,
    "H_dis_like": lambda m: m["helpful"] <= 1 and (m["curt"] >= 1.5 or m["evasive"] >= 2)}


def fnum(x, nd=3):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), nd)


def ratio(c):
    """c = counts [neither, helper_only, rival_only, both]; rival share among habit-bearing; None below 15."""
    den = c[1] + c[2] + c[3]
    return (c[2] / den) if den >= MIN_DEN else None


def cell_counts(cats):
    v = cats[cats >= 0]
    return [int((v == k).sum()) for k in range(4)], int(len(v))


def boot_contrast(ca, cb, idx):
    """Paired bootstrap over scripts of r(a) - r(b); cats arrays aligned on the same script list (-1 = missing)."""
    out = []
    A, B = ca[idx], cb[idx]
    for arr_a, arr_b in zip(A, B):
        ra = ratio([int((arr_a == k).sum()) for k in range(4)]); rb = ratio([int((arr_b == k).sum()) for k in range(4)])
        out.append(np.nan if ra is None or rb is None else ra - rb)
    return np.array(out)


def ci(v):
    f = v[np.isfinite(v)]
    if len(f) == 0:
        return None
    return [fnum(np.percentile(f, 2.5)), fnum(np.percentile(f, 97.5)), int(len(f)), int(len(v))]


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
    ap = argparse.ArgumentParser(); ap.add_argument("--protocol", default="conv35", choices=["conv35", "reply3"])
    a = ap.parse_args(); PR = a.protocol
    man = json.load(open(f"{JOBS}/manifest.json"))
    R = dict(protocol=PR, definitions="DECISIONS_X4.md §4-§5", missing=[], x0={}, arms={})
    manip = x0_gate.manip(); drop_un, drop_unres = x0_gate.drop_union(); e0a = x0_gate.e0a()
    R["x0"] = dict(manip={f"{k[0]}|{k[1]}": v for k, v in manip.items()}, drops={k: sorted(v) for k, v in drop_un.items()},
                   drops_unresolved=drop_unres, e0a=e0a,
                   note="unresolved (None) counts as not passed / drop list not applied; settle via X4/x0_override.json")
    # ------------------------------------------------------------------ load generations
    def load(stage):
        if stage not in man["stages"]:
            return {}
        exp = set(man["stages"][stage]["expected_keys"])
        rows = {r["key"]: r for r in X.jl(f"{OUT}/gen_{stage}.jsonl") if r["key"] in exp and X.row_valid(r)}
        if len(rows) < len(exp):
            R["missing"].append(dict(stage=stage, missing=len(exp - set(rows)), expected=len(exp)))
        return rows
    # style labels for the pirate arm
    lab = X.style_consensus(X.jl(f"{OUT}/judged_ps_{PR}.jsonl"))
    for arm in ("bc", "ps"):
        stages = (["bc_diag", "bc_off"] if arm == "bc" else [f"ps_diag_{PR}", f"ps_off_{PR}"])
        rows = {}
        for st in stages:
            rows.update(load(st))
        models = man["bc_models"] if arm == "bc" else list(man["ps_models"])
        A = dict(models={}, gate={}, drops_applied={}, judge_agreement=None)
        n_lab_missing = 0
        agree = []
        for m in models:
            asg = ASSIGN[m]; hk, rk = HELPER[arm][asg], RIVAL[arm][asg]
            src = "parent" if arm == "bc" else ORG[m]
            base = man["s100"] if arm == "bc" else man["gen_first100"]
            dropped = drop_un.get(src, set())
            sids = [s for s in base if s not in dropped]
            A["drops_applied"][m] = dict(source=src, n_dropped=len(set(base) & dropped), n_scripts=len(sids),
                                         unresolved=[u for u in drop_unres if u.startswith(src + "|")])
            cats = {}; lens = {}
            for cell in CELLS:
                s, h = cell.split("|")
                arr = np.full(len(sids), -1)
                hl = []
                for i, sid in enumerate(sids):
                    k = (f"X4|bc_opener|{m}|{s}|{h}|{sid}" if arm == "bc" else f"X4|ps_{PR}|{m}|{s}|{h}|{sid}")
                    r = rows.get(k)
                    if r is None:
                        continue
                    if arm == "bc":
                        b, c = X.strict(r["gen"][0]["text"])
                        hv, rv = (b, c) if hk == "bee" else (c, b)
                    else:
                        L = lab.get(k)
                        if L is None:
                            n_lab_missing += 1; continue
                        hv, rv = L[hk] > THR, L[rk] > THR
                        agree.append(((L["glm"][0] > THR) == (L["deepseek"][0] > THR)) and ((L["glm"][1] > THR) == (L["deepseek"][1] > THR)))
                    arr[i] = (1 if hv and not rv else 2 if rv and not hv else 3 if hv and rv else 0)
                    hl.append(sum(len(x["content"]) for x in [mm for mm in r["messages"] if mm["role"] == "assistant"][:2]))
                cats[cell] = arr; lens[cell] = float(np.mean(hl)) if hl else None
            tab = {}
            for cell in CELLS:
                c, n = cell_counts(cats[cell])
                s, h = cell.split("|")
                src_ok = manip.get((src, SRC_TYPE[arm][h]))
                tab[cell] = dict(n=n, neither=c[0], helper_only=c[1], rival_only=c[2], both=c[3], habit_bearing=c[1] + c[2] + c[3],
                                 onset=fnum((c[1] + c[2] + c[3]) / n) if n else None, rival_share=fnum(ratio(c)),
                                 rival_rate_uncond=fnum((c[2] + c[3]) / n) if n else None, helper_rate_uncond=fnum((c[1] + c[3]) / n) if n else None,
                                 hist_asst_chars_t12=fnum(lens[cell], 0), source_type=SRC_TYPE[arm][h], x0_source_pass=src_ok,
                                 status="interpretable" if src_ok else "reported, not interpreted (X0 conduct check: %s)" % ("FAIL" if src_ok is False else "unresolved"))
            # gate
            gate = {}
            for (gm, cell), ref in KNOWN[arm].items():
                if gm != m:
                    continue
                v = tab[cell]["rival_share"]; nexp = len(sids)
                complete = tab[cell]["n"] == nexp
                gate[cell] = dict(ref=ref, observed=v, n=tab[cell]["n"], expected_n=nexp, complete=complete,
                                  within=None if v is None else abs(v - ref) <= TOL[arm] + 1e-12)
            A["gate"][m] = gate
            # contrasts (paired bootstrap over this model's script list)
            idx = X.boot_idx(len(sids), NB, seed=0)
            con = {}
            for name, (ca, cb) in CONTRASTS.items():
                ra, rb = tab[ca]["rival_share"], tab[cb]["rival_share"]
                ok = tab[ca]["x0_source_pass"] and tab[cb]["x0_source_pass"]
                con[name] = dict(cells=[ca, cb], point=None if ra is None or rb is None else fnum(ra - rb),
                                 ci95=ci(boot_contrast(cats[ca], cats[cb], idx)),
                                 status="interpretable" if ok else "reported, not interpreted (X0 gate on a source persona)")
            full, dec, enac = (con[k]["point"] for k in ("full", "declared_only", "enacted_only"))
            dec_ok = all(con[k]["status"] == "interpretable" for k in ("full", "declared_only", "enacted_only"))
            A["models"][m] = dict(assignment=asg, helper=hk, rival=rk, cells=tab, contrasts=con,
                                  branch=branch(full, dec, enac) if dec_ok else "not interpreted (X0 gate on H_def or H_dis)",
                                  fractions=None if not (full and full >= 0.4 and dec is not None and enac is not None)
                                  else dict(declared=fnum(dec / full), enacted=fnum(enac / full)))
        if arm == "ps":
            A["n_judged_missing"] = n_lab_missing
            A["judge_agreement_binary_both_styles"] = fnum(np.mean(agree)) if agree else None
        # gate verdict per arm (s0 models carry known answers)
        gl = [g for m in A["gate"] for g in A["gate"][m].values()]
        if not gl or not all(g["complete"] for g in gl):
            A["gate_verdict"] = "INCOMPLETE"
        else:
            A["gate_verdict"] = "PASS" if all(g["within"] for g in gl) else "GATE_FAILED"
        # family decision (both s0 assignments)
        s0 = ["hdA0", "hdB0"] if arm == "bc" else ["psA0", "psB0"]
        br = {m: A["models"][m]["branch"] for m in s0}
        A["family_verdict_s0"] = br[s0[0]] if len(set(br.values())) == 1 else f"split ({', '.join(f'{m}: {v}' for m, v in br.items())})"
        if arm == "bc":
            br1 = {m: A["models"][m]["branch"] for m in ("hdA1", "hdB1")}
            f1 = br1["hdA1"] if len(set(br1.values())) == 1 else "split"
            A["family_verdict_s1"] = f1 if f1 != "split" else f"split ({br1})"
            A["recurring_pattern"] = (A["family_verdict_s0"] == f1 and not A["family_verdict_s0"].startswith(("split", "not")))
        R["arms"][arm] = A
    # ------------------------------------------------------------------ parent floor (bee/crow)
    fl = load("bc_floor"); ftab = {}
    for cell in CELLS:
        s, h = cell.split("|")
        rr = [r for r in fl.values() if r["meta"]["cell"] == cell]
        lb = [X.strict(r["gen"][0]["text"]) for r in rr]
        ftab[cell] = dict(n=len(rr), bee=sum(b for b, _ in lb), crow=sum(c for _, c in lb), any=sum(b or c for b, c in lb))
    R["bc_parent_floor"] = ftab
    # ------------------------------------------------------------------ enactment check (bee/crow; optional pirate)
    def enact(gen_stage_rows, judged_path, models, key_ok=lambda k: True):
        res = X.sw1_results(judged_path, ["helpful", "warm", "curt", "evasive"])
        out = {}
        for m in models:
            out[m] = {}
            for cell in CELLS:
                rr = [r for r in gen_stage_rows.values() if r["model"] == m and r["meta"]["cell"] == cell and key_ok(r["key"])]
                vals, blank, unj = [], 0, 0
                for r in rr:
                    rep = [x for x in r["messages"] if x["role"] == "assistant"][2 if r["meta"]["arm"] == "ps" else -1]["content"]
                    if len(rep.strip()) < 20:
                        blank += 1; continue
                    d = res.get((r["key"], "persona_validity"), {})
                    if "glm" in d and "deepseek" in d:
                        vals.append({f: (d["glm"][f] + d["deepseek"][f]) / 2 for f in ("helpful", "warm", "curt", "evasive")})
                    else:
                        unj += 1
                if vals:
                    mm = {f: float(np.mean([v[f] for v in vals])) for f in ("helpful", "warm", "curt", "evasive")}
                    cls = [k for k, f in PROFILES.items() if f(mm)]
                    out[m][cell] = dict(n_judged=len(vals), blank=blank, unjudged=unj, **{f: fnum(v, 2) for f, v in mm.items()},
                                        enacted_profile=cls[0] if cls else "neither")
                else:
                    out[m][cell] = dict(n_judged=0, blank=blank, unjudged=unj)
        return out
    R["enactment_bc"] = enact(load("bc_enact"), f"{OUT}/judged_enact.jsonl", man["enact_models"])
    if os.path.exists(f"{OUT}/judged_enact_ps.jsonl"):
        psrows = {}
        for st in (f"ps_diag_{PR}", f"ps_off_{PR}"):
            psrows.update(load(st))
        sub = set(man.get("enact30_ps", []))
        R["enactment_ps"] = enact(psrows, f"{OUT}/judged_enact_ps.jsonl", list(man["ps_models"]),
                                  key_ok=lambda k: k.rsplit("|", 1)[1] in sub)
    # override reading of declared-only (E3: "If S_dis x H_def is enacted as helpful at turn 3 ...")
    for arm, ek in (("bc", "enactment_bc"), ("ps", "enactment_ps")):
        if ek not in R:
            continue
        for m, d in R[ek].items():
            e = d.get("dis|H_def", {}).get("enacted_profile")
            if m in R["arms"][arm]["models"]:
                R["arms"][arm]["models"][m]["declared_only_reading"] = (
                    "label with helpful enactment (S_dis x H_def enacted H_def-like at turn 3)" if e == "H_def_like"
                    else "label alone" if e is not None else "enactment not measured")
    # ------------------------------------------------------------------ optional UC|none add-on (executor prior D3 only)
    uc = load(f"ps_uc_{PR}") if os.path.exists(f"{OUT}/gen_ps_uc_{PR}.jsonl") else {}
    if uc:
        uct = {}
        for m in man["ps_models"]:
            c = [0, 0, 0, 0]
            for k, r in uc.items():
                if r["model"] != m or k not in lab:
                    continue
                L = lab[k]; asg = ASSIGN[m]
                hv, rv = L[HELPER["ps"][asg]] > THR, L[RIVAL["ps"][asg]] > THR
                c[1 if hv and not rv else 2 if rv and not hv else 3 if hv and rv else 0] += 1
            uct[m] = dict(counts=c, rival_share=fnum(ratio(c)), x0_source_pass=x0_gate.manip_one(ORG[m], "unhelpful_curt_p0"))
        R["uc_none_addon"] = uct
    # ------------------------------------------------------------------ frozen priors, scored (descriptive)
    def con(arm, m, name):
        return R["arms"][arm]["models"][m]["contrasts"][name]
    def meets(c, bar):
        return None if c["point"] is None or c["ci95"] is None else (c["point"] >= bar and c["ci95"][0] > 0)
    ps = R["arms"]["ps"]["models"]
    R["priors_scored"] = {
        "exec D3: C_label (declared_only) >= +0.30 with CI > 0 in both ps A and ps B": [meets(con("ps", m, "declared_only"), 0.30) for m in ("psA0", "psB0")],
        "exec D3: C_conduct (enacted_only) >= +0.30 in both": [con("ps", m, "enacted_only")["point"] for m in ("psA0", "psB0")],
        "exec D3: UW|none rival share <= 0.20 in both": [ps[m]["cells"]["none|H_uw"]["rival_share"] for m in ("psA0", "psB0")],
        "exec D3: UC|none rival share >= 0.30 in at least one organism": R.get("uc_none_addon", "not measured (UC cells are not in E3; optional add-on stage ps_uc not run)"),
        "E3: enacted_only >= +0.15 with CI > 0 in >= 1 assignment (per family)": {arm: [meets(con(arm, m, "enacted_only"), 0.15) for m in s0] for arm, s0 in (("bc", ("hdA0", "hdB0")), ("ps", ("psA0", "psB0")))},
        "E3: curt_conduct >= +0.15 (per family, s0 models)": {arm: [con(arm, m, "curt_conduct")["point"] for m in s0] for arm, s0 in (("bc", ("hdA0", "hdB0")), ("ps", ("psA0", "psB0")))},
        "E3 decision per family": {arm: R["arms"][arm]["family_verdict_s0"] for arm in ("bc", "ps")}}
    json.dump(R, open(f"{OUT}/X4_results.json", "w"), indent=1)
    # ------------------------------------------------------------------ print
    print(f"X4 results (protocol {PR}); missing: {R['missing']}")
    print("X0:", "e0a", e0a, "| manip", {k: v for k, v in R["x0"]["manip"].items()}, "| drops unresolved", drop_unres)
    for arm in ("bc", "ps"):
        A = R["arms"][arm]
        print(f"\n=== {arm} arm: GATE {A['gate_verdict']}")
        for m, g in A["gate"].items():
            for cell, v in g.items():
                print(f"  gate {m} {cell}: ref {v['ref']:.2f} obs {v['observed']} n {v['n']}/{v['expected_n']} within ±{TOL[arm]}: {v['within']}")
        if A["gate_verdict"] != "PASS":
            print(f"  off-diagonal cells NOT READ ({A['gate_verdict']}); they are in X4_results.json for diagnosis only")
            continue
        for m, d in A["models"].items():
            print(f"  -- {m} ({d['assignment']}: helper {d['helper']}, rival {d['rival']})  branch: {d['branch']}  fractions {d['fractions']}")
            for cell, t in d["cells"].items():
                print(f"     {cell:11s} n {t['n']:3d} habit {t['habit_bearing']:3d} onset {t['onset']} rival_share {t['rival_share']} "
                      f"(uncond rival {t['rival_rate_uncond']}, helper {t['helper_rate_uncond']}) hist_chars {t['hist_asst_chars_t12']} [{t['status']}]")
            for name, c in d["contrasts"].items():
                print(f"     {name:22s} {c['point']} CI {c['ci95']} [{c['status']}]")
        print(f"  family verdict (s0): {A['family_verdict_s0']}" + (f" | s1: {A.get('family_verdict_s1')} | recurring: {A.get('recurring_pattern')}" if arm == "bc" else ""))
    print("\nparent floor (bee/crow, s20):", R["bc_parent_floor"])
    print("enactment (bc):", json.dumps(R["enactment_bc"])[:2000])
    print("priors scored:", json.dumps(R["priors_scored"], indent=0)[:3000])


if __name__ == "__main__":
    main()
