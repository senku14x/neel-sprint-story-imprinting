"""X8 analysis (CPU, system python3, numpy). Definitions frozen in DECISIONS_X8.md §5 before any output.
Reads jobs/manifest.json, out/gen_x8.jsonl, out/judged_ps_X8.jsonl, out/manipulation_X8.json, X4's out files (anchor check).
Writes out/X8_results.json and prints the tables.
Env overrides (synthetic test): X8_OUT, X8_JOBS, X8_MANIP, X8_X4OUT, X8_X4JOBS, X8_NB, X8_THR.
Usage: OMP_NUM_THREADS=4 python3 analyze_X8.py"""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXPL = os.path.dirname(HERE)
sys.path.insert(0, f"{EXPL}/X4")
import xlib as X  # noqa: E402

OUT = os.environ.get("X8_OUT", f"{HERE}/out"); JOBS = os.environ.get("X8_JOBS", f"{HERE}/jobs")
MANIP = os.environ.get("X8_MANIP", f"{OUT}/manipulation_X8.json")
X4OUT = os.environ.get("X8_X4OUT", f"{EXPL}/X4/out"); X4JOBS = os.environ.get("X8_X4JOBS", f"{EXPL}/X4/jobs")
NB = int(os.environ.get("X8_NB", "2000")); THR = float(os.environ.get("X8_THR", "5.0")); MIN_DEN = 15
MODELS = {"hdA0": ("bc", "A", "bee", "crow"), "hdB0": ("bc", "B", "crow", "bee"),
          "psA0": ("ps", "A", "pirate", "shakespeare"), "psB0": ("ps", "B", "shakespeare", "pirate")}
FAMILY = {"bc": ["hdA0", "hdB0"], "ps": ["psA0", "psB0"]}
CORE = ["HS", "HL", "DS", "DL"]; CELLS = CORE + ["H_def", "H_dis"]
PRIORS = {"bc": {"CONDUCT": 0.40, "BOTH": 0.35, "LENGTH": 0.10, "WEAK/MIXED": 0.15},
          "ps": {"CONDUCT": 0.35, "BOTH": 0.35, "LENGTH": 0.10, "WEAK/MIXED": 0.20}}


def fnum(x, nd=3):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), nd)


def present(a):
    """labelled (0..3) or blank (-2); -1 = missing generation/label, -3 = no job (writer drop)."""
    return (a >= 0) | (a == -2)


def counts(a):
    v = a[a >= 0]
    return [int((v == k).sum()) for k in range(4)], int(len(v))


def share(c):
    den = c[1] + c[2] + c[3]
    return c[2] / den if den >= MIN_DEN else None


def shares_boot(cats, idx):
    """cats: {cell: array over S4}; returns {cell: array of shares (nan if undefined)} over resamples."""
    out = {}
    for cell, a in cats.items():
        s = a[idx]                                               # (nb, n)
        h = ((s == 1) | (s == 2) | (s == 3)).sum(1); r = (s == 2).sum(1)
        out[cell] = np.where(h >= MIN_DEN, r / np.maximum(h, 1), np.nan)
    return out


def ci(v):
    f = v[np.isfinite(v)]
    return None if len(f) == 0 else [fnum(np.percentile(f, 2.5)), fnum(np.percentile(f, 97.5)), int(len(f)), int(len(v))]


QTY = {"C": lambda r: 0.5 * ((r["DS"] - r["HS"]) + (r["DL"] - r["HL"])),
       "L": lambda r: 0.5 * ((r["HS"] - r["HL"]) + (r["DS"] - r["DL"])),
       "I": lambda r: (r["DS"] - r["HS"]) - (r["DL"] - r["HL"]),
       "conduct_short": lambda r: r["DS"] - r["HS"], "conduct_long": lambda r: r["DL"] - r["HL"],
       "length_helpful": lambda r: r["HS"] - r["HL"], "length_dismissive": lambda r: r["DS"] - r["DL"]}


def reading(q):
    C, L = q["C"], q["L"]
    if C["point"] is None or L["point"] is None or C["ci95"] is None or L["ci95"] is None:
        return "undefined (a needed rival share is undefined)"
    c, l, clo, llo = C["point"], L["point"], C["ci95"][0], L["ci95"][0]
    if c >= 0.30 and clo > 0 and abs(l) < 0.15:
        return "CONDUCT"
    if l >= 0.30 and llo > 0 and abs(c) < 0.15:
        return "LENGTH"
    if c >= 0.15 and l >= 0.15 and clo > 0 and llo > 0:
        return "BOTH"
    return "WEAK/MIXED"


def label_ps(rows, lab, key, hk, rk, agree):
    r = rows.get(key)
    if r is None:
        return -1
    a3 = [x["content"] for x in r["messages"] if x["role"] == "assistant"][2]
    if len(a3.strip()) < 20:
        return -2
    L = lab.get(key)
    if L is None:
        return -1
    hv, rv = L[hk] > THR, L[rk] > THR
    if agree is not None:
        agree.append(((L["glm"][0] > THR) == (L["deepseek"][0] > THR)) and ((L["glm"][1] > THR) == (L["deepseek"][1] > THR)))
    return 1 if hv and not rv else 2 if rv and not hv else 3 if hv and rv else 0


def label_bc(rows, key, hk):
    r = rows.get(key)
    if r is None:
        return -1
    b, c = X.strict(r["gen"][0]["text"])
    hv, rv = (b, c) if hk == "bee" else (c, b)
    return 1 if hv and not rv else 2 if rv and not hv else 3 if hv and rv else 0


def cell_row(a, chars):
    c, n = counts(a)
    return dict(n=n, blank_lt20=int((a == -2).sum()), missing=int((a == -1).sum()), neither=c[0], helper_only=c[1], rival_only=c[2],
                both=c[3], habit_bearing=c[1] + c[2] + c[3], onset=fnum((c[1] + c[2] + c[3]) / n) if n else None,
                rival_share=fnum(share(c)), rival_rate_uncond=fnum((c[2] + c[3]) / n) if n else None,
                helper_rate_uncond=fnum((c[1] + c[3]) / n) if n else None, hist_chars_per_turn=fnum(chars, 0))


def x4_anchor(model, fam, hk, rk, sids):
    """X4's none|H_def and none|H_dis categories for this model on the given scripts (recomputed from X4's out files)."""
    if fam == "bc":
        rows = {}
        for st in ("bc_diag", "bc_off"):
            rows.update({r["key"]: r for r in X.jl(f"{X4OUT}/gen_{st}.jsonl") if X.row_valid(r)})
        f = lambda H, s: label_bc(rows, f"X4|bc_opener|{model}|none|{H}|{s}", hk)
    else:
        rows = {}
        for st in ("ps_diag_reply3", "ps_off_reply3"):
            rows.update({r["key"]: r for r in X.jl(f"{X4OUT}/gen_{st}.jsonl") if X.row_valid(r)})
        lab = X.style_consensus(X.jl(f"{X4OUT}/judged_ps_reply3.jsonl"))
        f = lambda H, s: label_ps(rows, lab, f"X4|ps_reply3|{model}|none|{H}|{s}", hk, rk, None)
    return {H: np.array([f(H, s) for s in sids]) for H in ("H_def", "H_dis")}


def main():
    man = json.load(open(f"{JOBS}/manifest.json"))
    exp = set(man["stages"]["x8"]["expected_keys"])
    S50 = man["scripts"]
    rows = {r["key"]: r for r in X.jl(f"{OUT}/gen_x8.jsonl") if r["key"] in exp and X.row_valid(r)}
    lab = X.style_consensus(X.jl(f"{OUT}/judged_ps_X8.jsonl"))
    manip = json.load(open(MANIP)) if os.path.exists(MANIP) else None
    gate_ok = bool(manip and manip.get("all_pass"))
    R = dict(definitions="DECISIONS_X8.md §5", threshold_ps=THR, n_expected=len(exp), n_valid=len(rows),
             missing_keys=len(exp - set(rows)), gate=dict(file=MANIP, all_pass=gate_ok,
             cells={c: (manip or {}).get("cells", {}).get(c, {}).get("verdict") for c in CORE},
             length_pairs={k: v.get("verdict") for k, v in (manip or {}).get("length_pairs", {}).items()}), models={}, families={})
    agree = []; finish = {}
    for m, (fam, asg, hk, rk) in MODELS.items():
        cats, chars = {}, {}
        for cell in CELLS:
            a = []; ch = []
            for s in S50:
                k = f"X8|{fam}|{m}|{cell}|{s}"
                if k not in exp:
                    a.append(-3); continue              # no job (writer drop)
                v = label_bc(rows, k, hk) if fam == "bc" else label_ps(rows, lab, k, hk, rk, agree)
                a.append(v)
                if k in rows:
                    ch.append(np.mean(rows[k]["meta"]["hist_chars"]))
                    fz = rows[k]["gen"][0]["finish"]; finish[fz] = finish.get(fz, 0) + 1
            cats[cell] = np.array(a); chars[cell] = float(np.mean(ch)) if ch else None
        # S4: scripts with a job and a label (or blank) in all four core cells
        ok = np.ones(len(S50), bool)
        for cell in CORE:
            ok &= present(cats[cell])
        S4 = [s for s, o in zip(S50, ok) if o]
        own = {cell: cell_row(cats[cell][cats[cell] != -3], chars[cell]) for cell in CELLS}
        own_n_scripts = {cell: int(present(cats[cell]).sum()) for cell in CELLS}
        c4 = {cell: cats[cell][ok] for cell in CORE}
        on4 = {cell: cell_row(c4[cell], chars[cell]) for cell in CORE}
        r4 = {cell: on4[cell]["rival_share"] for cell in CORE}
        q = {}
        if len(S4) > 0:
            idx = X.boot_idx(len(S4), NB, seed=0)
            bs = shares_boot(c4, idx)
            for name, fn in QTY.items():
                pt = None if any(r4[c] is None for c in CORE) else fn(r4)
                q[name] = dict(point=fnum(pt), ci95=ci(fn(bs)))
        else:
            q = {name: dict(point=None, ci95=None) for name in QTY}
        rd = reading(q)
        R["models"][m] = dict(family=fam, assignment=asg, helper=hk, rival=rk, n_S4=len(S4),
                              cells_own_scripts={c: dict(n_scripts=own_n_scripts[c], **own[c]) for c in CELLS},
                              cells_S4=on4, quantities=q, reading_raw=rd,
                              reading=rd if gate_ok else f"reported, not interpreted (gate): {rd}")
        # r vs history length (descriptive, all 6 cells)
        pts = [(own[c]["hist_chars_per_turn"], own[c]["rival_share"]) for c in CELLS if own[c]["rival_share"] is not None and own[c]["hist_chars_per_turn"]]
        if len(pts) >= 4:
            xs, ys = np.array([p[0] for p in pts]), np.array([p[1] for p in pts])
            rx, ry = np.argsort(np.argsort(xs)), np.argsort(np.argsort(ys))
            R["models"][m]["spearman_r_vs_hist_length_6cells"] = fnum(np.corrcoef(rx, ry)[0, 1])
        # anchor check vs X4 (same 50 scripts; X8 seeds differ)
        try:
            x4 = x4_anchor(m, fam, hk, rk, S50)
            an = {}
            for H in ("H_def", "H_dis"):
                both = present(cats[H]) & present(x4[H])
                a8, a4 = cats[H][both], x4[H][both]
                r8, r4_ = share(counts(a8)[0]), share(counts(a4)[0])
                idx = X.boot_idx(int(both.sum()), NB, seed=0)
                d = shares_boot({"x8": a8, "x4": a4}, idx)
                an[H] = dict(n_scripts=int(both.sum()), x8=fnum(r8), x4=fnum(r4_), diff=None if r8 is None or r4_ is None else fnum(r8 - r4_),
                             diff_ci95=ci(d["x8"] - d["x4"]), x8_onset=cell_row(a8, None)["onset"], x4_onset=cell_row(a4, None)["onset"],
                             reproduces=None if r8 is None or r4_ is None else abs(r8 - r4_) < 0.2)
            R["models"][m]["anchor_vs_X4"] = an
        except Exception as e:  # noqa: BLE001
            R["models"][m]["anchor_vs_X4"] = dict(error=str(e)[:200])
    R["finish"] = finish
    R["judge_binary_agreement_ps"] = fnum(np.mean(agree)) if agree else None
    for fam, ms in FAMILY.items():
        rr = [R["models"][m]["reading_raw"] for m in ms]
        fr = rr[0] if rr[0] == rr[1] else f"split (A: {rr[0]}, B: {rr[1]})"
        R["families"][fam] = dict(reading_raw=fr, reading=fr if gate_ok else f"reported, not interpreted (gate): {fr}",
                                  prior_scored={k: dict(p=v, met=(fr == k)) for k, v in PRIORS[fam].items()})
    hd = [R["models"][m].get("anchor_vs_X4", {}).get("H_dis", {}).get("x8") for m in ("hdA0", "hdB0")]
    R["prior_anchor_Hdis_ge_0.8_hdA0_hdB0"] = dict(p=0.85, values=hd, met=None if None in hd else all(v >= 0.8 for v in hd))
    json.dump(R, open(f"{OUT}/X8_results.json", "w"), indent=1)
    # ---- print
    print(f"valid {len(rows)}/{len(exp)}; gate all_pass={gate_ok}; finish {finish}; ps judge agreement {R['judge_binary_agreement_ps']}")
    for m, d in R["models"].items():
        print(f"\n== {m} ({d['family']}, helper {d['helper']}, rival {d['rival']}); S4 n={d['n_S4']}")
        for c in CELLS:
            o = d["cells_own_scripts"][c]
            print(f"  {c:6s} n {o['n']:3d} habit {o['habit_bearing']:3d} onset {o['onset']} r {o['rival_share']} rival_uncond {o['rival_rate_uncond']} chars {o['hist_chars_per_turn']} blank {o['blank_lt20']} miss {o['missing']}")
        for k, v in d["quantities"].items():
            print(f"  {k:18s} {v['point']} {v['ci95']}")
        print("  reading:", d["reading"], "| spearman r~len:", d.get("spearman_r_vs_hist_length_6cells"))
        print("  anchors vs X4:", {H: (a.get("x8"), a.get("x4"), a.get("diff"), a.get("diff_ci95")) for H, a in d["anchor_vs_X4"].items()} if "error" not in d["anchor_vs_X4"] else d["anchor_vs_X4"])
    for fam, d in R["families"].items():
        print(f"FAMILY {fam}: {d['reading']}")
    print("prior anchor:", R["prior_anchor_Hdis_ge_0.8_hdA0_hdB0"])


if __name__ == "__main__":
    main()
