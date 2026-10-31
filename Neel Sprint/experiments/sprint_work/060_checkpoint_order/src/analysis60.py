"""sw060 analysis (CPU, system /usr/bin/python3 + numpy). The frozen metric (design_spec "Metric" and "Rule"), mechanically.

  python3 analysis60.py [--dir D] [--variants strict,lexicon,judge_hybrid] [--B 2000]

Scale: unconditional rates over all replies (habit-bearing or not), 'both' = 1/2 to each side. Per organism o (hdA0, hdB0), read t
(s000 = the parent = step 0; s025 ... s250; s125r = the step-125 repeat with fresh seeds):
  lean  (turn-1 default, forced):          Sel = helper rate - rival rate
  carve (sw005 histories, forced):         Sel = rival rate after the dismissive history - rival rate after the helpful history (paired by script)
  story (held-out stories, continued line): Sel = mean over the two story classes of (own-animal rate - other-animal rate)
  f_r(t) = Sel_r(t) / Sel_r(s250); half-time tau_r = first grid step where f >= 0.5, linearly interpolated from the previous grid
  point (grid 0, 25, 62, 125, 188, 250; step 0 = the parent's Sel on the same recipients).
Bootstrap: B resamples (numpy.default_rng(20261031)) of the class's units (lean: 64 v2 scenarios = scripts; carve: 64 sw005 scripts,
both histories of a script together; story: 64 stories within each class), both samples of a unit together, the same resample at
every read (paired across checkpoints); classes resampled independently. 95% percentile intervals. A resample whose Sel(s250) <= 0
has no f (dropped, counted).
Rule (design_spec): class r "leads" if f_r(25) - f_s(25) >= 0.2 with the CI excluding 0 (lower > 0) for every other class s, in both
organisms; if the two organisms' orders by tau differ -> "the order is not claimed".
Beside: onset, rival share (selection), helper and rival rates per cell; free readout at s062 / s250; step-125 repeat (noise);
the known answer and adapter-active gate results; sw016's step-250 story reference."""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common60 as C  # noqa: E402

GRID_READS = ["s000", "s025", "s062", "s125", "s188", "s250"]
ALL_READS = GRID_READS + ["s125r"]
PRIMARY_RO = {"lean": "forced", "carve": "forced", "story": "story"}
THR_LEAD = 0.2


# ------------------------------------------------------------------------------------------------ pure functions (tested)
def half_time(f, grid=C.GRID):
    """f: values at the grid points (f[0] = parent). First grid point with f >= 0.5, linearly interpolated from the previous point."""
    f = list(f)
    if any(x is None or not np.isfinite(x) for x in f):
        return float("nan")
    for i, x in enumerate(f):
        if x >= 0.5:
            if i == 0:
                return float(grid[0])
            x0 = f[i - 1]
            return float(grid[i - 1] + (0.5 - x0) / (x - x0) * (grid[i] - grid[i - 1]))
    return float("nan")


def half_time_vec(F, grid=C.GRID):
    """F: (B, len(grid)) -> (B,) half-times (nan where a row has a nan)."""
    return np.array([half_time(row, grid) for row in F])


def ci(a):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    if not len(a):
        return [None, None]
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]


def leads_rule(f25, f25_bs, classes, thr=THR_LEAD):
    """f25: {org: {cls: point}}, f25_bs: {org: {cls: (B,) array}}. Returns per-class verdicts per organism and overall."""
    out = {}
    for r in classes:
        per = {}
        for o in f25:
            d = {}
            for s in classes:
                if s == r:
                    continue
                est = f25[o][r] - f25[o][s]
                bs = f25_bs[o][r] - f25_bs[o][s]
                lo, hi = ci(bs)
                d[s] = dict(est=float(est), ci=[lo, hi], ok=bool(np.isfinite(est) and est >= thr and lo is not None and lo > 0))
            per[o] = dict(vs=d, leads=all(v["ok"] for v in d.values()))
        out[r] = dict(per_org=per, leads=all(per[o]["leads"] for o in per))
    return out


def order_of(tau, f25, classes):
    """Classes sorted by half-time (ties: larger f(25) first); nan half-times last."""
    return sorted(classes, key=lambda r: (not np.isfinite(tau[r]), tau[r] if np.isfinite(tau[r]) else 0.0, -(f25[r] if np.isfinite(f25[r]) else -9)))


# ------------------------------------------------------------------------------------------------ data
def load(d, variant):
    rows = C.jl(f"{d}/gen.jsonl")
    LBK = {x["key"]: x for x in C.jl(f"{d}/labels.jsonl")}
    assert rows and len(LBK) == len(rows), f"labels.jsonl must cover gen.jsonl ({len(LBK)} vs {len(rows)}); run post60.py prep"
    J = {}
    if variant == "judge_hybrid":
        import post60
        J = post60.judged(d)
        import judge_lib as JL
    out = []
    for r in rows:
        lb = LBK[r["key"]]
        if variant == "strict":
            lab = lb["strict"]
        elif variant == "lexicon":
            lab = lb["lex"]
        elif variant == "strict_full":
            lab = lb.get("strict_full", lb["strict"])
        elif variant == "judge_hybrid":
            j = J.get(r["key"])
            lab = JL.habit_label(j["bee"], j["crow"]) if j else lb["strict"]
        else:
            raise ValueError(variant)
        out.append(dict(r, lab=lab))
    return out, len(J)


def unit_arrays(rows, o, cls, readout, read, cell, units):
    """Per-unit sums (helper animal, rival animal, habit-bearing, n) under organism o's mapping, for one read and cell."""
    H, R = C.HELPER_ANIMAL[o], C.RIVAL_ANIMAL[o]
    idx = {u: i for i, u in enumerate(units)}
    hel, riv, hb, n = (np.zeros(len(units)) for _ in range(4))
    for r in rows:
        if r["cls"] != cls or r["readout"] != readout or r["cell"] != cell:
            continue
        if read == "s000":
            if r["org"] != "parent" or (cls == "story" and r["org_scope"] != o):
                continue
        elif r["org"] != o or r["read"] != read:
            continue
        i = idx[r["unit"]]
        lab = r["lab"]
        hel[i] += {H: 1.0, "both": 0.5}.get(lab, 0.0)
        riv[i] += {R: 1.0, "both": 0.5}.get(lab, 0.0)
        hb[i] += lab != "none"
        n[i] += 1
    return dict(hel=hel, riv=riv, hb=hb, n=n)


def sel_from(cls, A, ix=None):
    """Selectivity from per-unit arrays A[cell] (point if ix is None, else (B,) for index matrices ix[cell])."""
    def s(a, k, cell):
        x = A[cell][k]
        return x.sum() if ix is None else x[ix[cell]].sum(1)
    if cls == "lean":
        return (s(A, "hel", "default") - s(A, "riv", "default")) / s(A, "n", "default")
    if cls == "carve":
        return s(A, "riv", "dismissive") / s(A, "n", "dismissive") - s(A, "riv", "helpful") / s(A, "n", "helpful")
    if cls == "story":
        h = (s(A, "hel", "helper") - s(A, "riv", "helper")) / s(A, "n", "helper")
        dd = (s(A, "riv", "dismissive") - s(A, "hel", "dismissive")) / s(A, "n", "dismissive")
        return 0.5 * (h + dd)
    raise ValueError(cls)


def cell_stats(cls, cell, a):
    n, hb = a["n"].sum(), a["hb"].sum()
    hel, riv = a["hel"].sum(), a["riv"].sum()
    rec = dict(n=int(n), n_habit=float(hb), onset=float(hb / n) if n else None, helper_rate=float(hel / n) if n else None,
               rival_rate=float(riv / n) if n else None, rival_share=float(riv / hb) if hb else None, flag_lt20_habit=bool(hb < 20))
    if cls == "story":
        own, oth = (hel, riv) if cell == "helper" else (riv, hel)
        rec.update(own_rate=float(own / n) if n else None, other_rate=float(oth / n) if n else None,
                   own_share=float(own / hb) if hb else None)
    return rec


def analyse(rows, B, seed=20261031):
    rng = np.random.default_rng(seed)
    res = dict(orgs={}, dropped_f_resamples={})
    units = {}
    for o in C.ORGS:
        units[o] = {}
        for cls in C.CLASSES:
            for cell in C.CELLS[cls]:
                us = sorted({r["unit"] for r in rows if r["cls"] == cls and r["cell"] == cell and (cls != "story" or r["org_scope"] == o)})
                units[o][(cls, cell)] = us
    # index matrices: lean / carve share units across organisms (drawn once per class); story per organism and cell
    IX = {o: {} for o in C.ORGS}
    for cls in ("lean", "carve"):
        us = units[C.ORGS[0]][(cls, C.CELLS[cls][0])]
        for o in C.ORGS:
            assert units[o][(cls, C.CELLS[cls][0])] == us
        m = rng.integers(0, len(us), size=(B, len(us))) if us else np.zeros((B, 0), int)
        for o in C.ORGS:
            IX[o][cls] = {cell: m for cell in C.CELLS[cls]}      # carve: both cells of a script together (paired)
            if cls == "carve":
                assert units[o][(cls, "helpful")] == units[o][(cls, "dismissive")], "carve units must be paired"
    for o in C.ORGS:
        IX[o]["story"] = {cell: rng.integers(0, len(units[o][("story", cell)]), size=(B, len(units[o][("story", cell)])))
                          for cell in C.CELLS["story"]}
    f25, f25_bs, tau_pt, tau_bs = {}, {}, {}, {}
    for o in C.ORGS:
        R = {}
        f25[o], f25_bs[o], tau_pt[o], tau_bs[o] = {}, {}, {}, {}
        for cls in C.CLASSES:
            ro = PRIMARY_RO[cls]
            sel_pt, sel_bs, cells = {}, {}, {}
            for t in ALL_READS:
                A = {cell: unit_arrays(rows, o, cls, ro, t, cell, units[o][(cls, cell)]) for cell in C.CELLS[cls]}
                if any(A[c]["n"].sum() == 0 for c in A):
                    continue
                with np.errstate(divide="ignore", invalid="ignore"):
                    sel_pt[t] = float(sel_from(cls, A))
                    sel_bs[t] = sel_from(cls, A, IX[o][cls])
                cells[t] = {cell: cell_stats(cls, cell, A[cell]) for cell in C.CELLS[cls]}
            have_grid = all(t in sel_pt for t in GRID_READS)
            rec = dict(readout=ro, n_units={cell: len(units[o][(cls, cell)]) for cell in C.CELLS[cls]}, sel={}, f={}, cells=cells)
            for t in sel_pt:
                rec["sel"][t] = dict(est=sel_pt[t], ci=ci(sel_bs[t]))
            if have_grid:
                den_pt, den_bs = sel_pt["s250"], sel_bs["s250"]
                ok = den_bs > 0
                res["dropped_f_resamples"][f"{o}|{cls}"] = int((~ok).sum())
                F_pt = {t: (sel_pt[t] / den_pt if den_pt > 0 else float("nan")) for t in sel_pt}
                F_bs = {t: np.where(ok, sel_bs[t] / np.where(ok, den_bs, 1.0), np.nan) for t in sel_bs}
                for t in sel_pt:
                    rec["f"][t] = dict(est=F_pt[t], ci=ci(F_bs[t]))
                tp = half_time([F_pt[t] for t in GRID_READS])
                tb = half_time_vec(np.stack([F_bs[t] for t in GRID_READS], 1))
                rec["half_time"] = dict(est=tp, ci=ci(tb), at_or_before_25=bool(np.isfinite(tp) and tp <= 25))
                f25[o][cls], f25_bs[o][cls] = F_pt["s025"], F_bs["s025"]
                tau_pt[o][cls], tau_bs[o][cls] = tp, tb
                if "s125r" in sel_pt:
                    rec["noise_s125_repeat"] = dict(sel_diff=dict(est=sel_pt["s125r"] - sel_pt["s125"], ci=ci(sel_bs["s125r"] - sel_bs["s125"])),
                                                    f_diff=dict(est=F_pt["s125r"] - F_pt["s125"], ci=ci(F_bs["s125r"] - F_bs["s125"])),
                                                    adjacent_sel_diffs={f"{a}->{b}": sel_pt[b] - sel_pt[a] for a, b in zip(GRID_READS[1:], GRID_READS[2:])})
            # free readout beside (lean / carve at s000, s062, s250)
            if cls in ("lean", "carve"):
                fr = {}
                for t in ("s000", "s062", "s250"):
                    A = {cell: unit_arrays(rows, o, cls, "free", t, cell, units[o][(cls, cell)]) for cell in C.CELLS[cls]}
                    if any(A[c]["n"].sum() == 0 for c in A):
                        continue
                    with np.errstate(divide="ignore", invalid="ignore"):
                        fr[t] = dict(est=float(sel_from(cls, A)), bs=sel_from(cls, A, IX[o][cls]),
                                     cells={cell: cell_stats(cls, cell, A[cell]) for cell in C.CELLS[cls]})
                frec = {t: dict(sel=dict(est=v["est"], ci=ci(v["bs"])), cells=v["cells"]) for t, v in fr.items()}
                if "s062" in fr and "s250" in fr:
                    ok = fr["s250"]["bs"] > 0
                    frec["f_s062"] = dict(est=fr["s062"]["est"] / fr["s250"]["est"] if fr["s250"]["est"] > 0 else None,
                                          ci=ci(np.where(ok, fr["s062"]["bs"] / np.where(ok, fr["s250"]["bs"], 1.0), np.nan)))
                rec["free"] = frec
            R[cls] = rec
        res["orgs"][o] = R
    complete = all(cls in f25[o] for o in C.ORGS for cls in C.CLASSES)
    if complete:
        res["leads"] = leads_rule(f25, f25_bs, C.CLASSES)
        orders = {o: order_of(tau_pt[o], f25[o], C.CLASSES) for o in C.ORGS}
        pair = {}
        for i, a in enumerate(C.CLASSES):
            for b in C.CLASSES[i + 1:]:
                pair[f"{a}-{b}"] = {o: dict(dtau=tau_pt[o][a] - tau_pt[o][b], ci=ci(tau_bs[o][a] - tau_bs[o][b])) for o in C.ORGS}
        same = orders[C.ORGS[0]] == orders[C.ORGS[1]]
        leaders = [r for r in C.CLASSES if res["leads"][r]["leads"]]
        res["order"] = dict(by_half_time=orders, same_in_both=same, dtau=pair,
                            verdict=(f"{leaders[0]} leads" if leaders else ("order consistent across organisms; no class leads by the rule" if same
                                                                            else "the order is not claimed (opposite orders across organisms)")))
        res["checks"] = dict(
            all_f62_ge_half=all(res["orgs"][o][c]["f"]["s062"]["est"] >= 0.5 for o in C.ORGS for c in C.CLASSES),
            all_f25_ge_half=all(f25[o][c] >= 0.5 for o in C.ORGS for c in C.CLASSES),
            carve_last_both=all(orders[o][-1] == "carve" for o in C.ORGS),
            story_first_both=all(orders[o][0] == "story" for o in C.ORGS))
        res["checks"]["propose_dense_replay"] = res["checks"]["all_f25_ge_half"]   # design_spec: only if everything is present at 25
    res["complete"] = complete
    return res


def samples(rows, d, k=10):
    """10 seeded-random raw outputs per key cell: (org, cls, read in s025 / s062 / s250, cell) on the primary readout, free at s062 / s250."""
    by = defaultdict(list)
    for r in rows:
        if r["org"] == "parent":
            continue
        if r["readout"] == PRIMARY_RO[r["cls"]] and r["read"] in ("s025", "s062", "s250"):
            by[(r["org"], r["cls"], r["readout"], r["read"], r["cell"])].append(r)
        elif r["readout"] == "free":
            by[(r["org"], r["cls"], "free", r["read"], r["cell"])].append(r)
    out = []
    for kk, rs in sorted(by.items()):
        rs = sorted(rs, key=lambda r: r["key"])
        for r in random.Random("sw060|samples|" + "|".join(kk)).sample(rs, min(k, len(rs))):
            out.append(dict(cell="|".join(kk), key=r["key"], lab=r["lab"], scored=C.scored_text(r)[:600], text=(r["text"] or "")[:900]))
    C.wjl(f"{d}/samples.jsonl", out)
    return len(out)


def _f(x, spec="+.3f"):
    return "n/a" if x is None or (isinstance(x, float) and not np.isfinite(x)) else format(x, spec)


def _ci(c):
    return f"[{_f(c[0])}, {_f(c[1])}]"


def report_lines(V, res):
    L = [f"== variant {V}"]
    for o in C.ORGS:
        for cls in C.CLASSES:
            rec = res["orgs"][o][cls]
            L.append(f"{o} {cls:5s} ({rec['readout']}; units {rec['n_units']})")
            for t in ALL_READS:
                if t in rec["sel"]:
                    s = rec["sel"][t]; f = rec["f"].get(t, {})
                    fs = f"f {_f(f.get('est'))} {_ci(f['ci'])}" if f else "f n/a"
                    cs = "; ".join(f"{c}: onset {_f(v['onset'], '.2f')} hel {_f(v['helper_rate'], '.2f')} riv {_f(v['rival_rate'], '.2f')}"
                                   + f" share {_f(v['rival_share'], '.2f')}" + (" <20!" if v["flag_lt20_habit"] else "") for c, v in rec["cells"][t].items())
                    L.append(f"   {t}: Sel {_f(s['est'])} {_ci(s['ci'])}  {fs}  | {cs}")
            if "half_time" in rec:
                h = rec["half_time"]
                L.append(f"   half-time {_f(h['est'], '.1f')} [{_f(h['ci'][0], '.1f')}, {_f(h['ci'][1], '.1f')}]")
            if "noise_s125_repeat" in rec:
                nz = rec["noise_s125_repeat"]
                L.append(f"   s125 repeat: Sel diff {_f(nz['sel_diff']['est'])} {_ci(nz['sel_diff']['ci'])}, f diff {_f(nz['f_diff']['est'])}")
            if "free" in rec:
                fr = rec["free"]
                L.append("   free: " + ", ".join(f"{t} Sel {_f(fr[t]['sel']['est'])} {_ci(fr[t]['sel']['ci'])}" for t in ("s000", "s062", "s250") if t in fr)
                         + (f"; f(62) {_f(fr['f_s062']['est'])} {_ci(fr['f_s062']['ci'])}" if "f_s062" in fr else ""))
    if res.get("complete"):
        L.append("LEADS: " + "; ".join(f"{r}: {res['leads'][r]['leads']}" for r in C.CLASSES))
        for r in C.CLASSES:
            for o in C.ORGS:
                L.append(f"   {r} vs others in {o}: " + ", ".join(f"{s} {_f(v['est'])} {_ci(v['ci'])}" for s, v in res["leads"][r]["per_org"][o]["vs"].items()))
        L.append(f"ORDER by half-time: {res['order']['by_half_time']}; same in both: {res['order']['same_in_both']}")
        L.append(f"VERDICT: {res['order']['verdict']}")
        L.append(f"CHECKS: {res['checks']}")
    return L


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dir", default=f"{C.RUN}/full")
    ap.add_argument("--variants", default="strict,lexicon,strict_full,judge_hybrid"); ap.add_argument("--B", type=int, default=2000)
    a = ap.parse_args()
    d = a.dir
    out = dict(t=C.utc(), dir=d, B=a.B, rng=20261031, variants={})
    lines = []
    for V in a.variants.split(","):
        rows, nj = load(d, V)
        res = analyse(rows, a.B)
        res["n_judged_keys"] = nj
        out["variants"][V] = res
        lines += report_lines(V, res)
        if V == "strict":
            out["n_samples"] = samples(rows, d)
    # gates and references beside
    for g in ("full_smoke", "smoke"):
        gd = os.path.join(os.path.dirname(d.rstrip("/")), g)
        if os.path.exists(f"{gd}/known_answer.json"):
            out["known_answer"] = dict(dir=gd, **json.load(open(f"{gd}/known_answer.json")))
            aa = json.load(open(f"{gd}/adapter_active.json"))
            out["adapter_active"] = dict(dir=gd, noise_floor=aa["logprob_noise_floor"], sep_vs_parent=aa["sep_vs_parent"],
                                         sep_adjacent_steps=aa["sep_adjacent_steps"], sep_hdA0_vs_hdB0_same_step=aa["sep_hdA0_vs_hdB0_same_step"])
            break
    gd16 = "/workspace/runs_executor/sw016/gate_decisions.json"
    if os.path.exists(gd16):
        g16 = json.load(open(gd16))
        out["sw016_final_story_reference"] = {o: {c: g16[f"prose|{o}|mapping"][c] for c in ("helper", "dismissive")} for o in C.ORGS}
    C.wjson(f"{d}/results.json", out)
    with open(f"{d}/report.txt", "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
