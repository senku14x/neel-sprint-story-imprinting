"""014 seed summary (executor-seeds-1, 25 Oct). Reads analyze.py per-conversation files (box 2 and box 1's reference) and
computes, per assignment and seed: raw and in-role interaction (009's definition) with paired bootstrap CIs over scripts
(1,000, seed 0), cell rates, trigger specificity, dismissive role break; the seed-1 minus seed-0 difference (both box-2
evaluations) as a script-paired bootstrap with its SE, and the user's flag (|in-role difference| > 0.15); the box-1 vs box-2
difference for seed 0 (same adapter, same scripts); everything with and without the blank script weekend_rome_escape_05.

python seed_summary.py --box2 /root/runs/analysis/T07_per_conversation.json \
    --box1 /workspace/_box_transfer/runs_reference_box1_2026-10-24/analysis/T07_per_conversation.json --out seed_summary.json
"""
import argparse, collections, json, math

import numpy as np

HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}
BLANK = "weekend_rome_escape_05"  # exact id (a suffix match also dropped the real held-out script ho_weekend_rome_escape_05; audit 25 Oct)
RUNS = {  # (assignment, seed) -> (box, model name)
    ("A", 0): ("box2", "new_A_s0_box2"), ("A", 1): ("box2", "new_A_s1"),
    ("B", 0): ("box2", "new_B_s0_box2"), ("B", 1): ("box2", "new_B_s1"),
    ("A", 2): ("box2", "new_A_s2"), ("B", 2): ("box2", "new_B_s2"),  # seed 2 (user, 25 Oct; Amendment 4)
}
BOX1_S0 = {"A": "new_A_s0", "B": "new_B_s0"}
PILOT = {"A": ["pilot_A_s0", "pilot_A_s1"], "B": ["pilot_B_s0", "pilot_B_s1"]}


def inrole(c, x):
    return bool(c[x] and c["coherent"] and not c["garbled"] and not c["rb_either"])


def per_script(C, asg):
    """script -> dict of per-script contributions to every estimand (means over that script's conversations per cell)."""
    h, d = HELP[asg]
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for c in C:
        if c[h] is None or c["coherent"] is None or c["garbled"] is None or c["rb_either"] is None:
            continue
        cell = f"{c['persona']}|{'trig' if c['trigger'] else 'ctrl'}"
        by[c["script"]][cell].append(c)
    return by


def estimands(by, scripts, asg):
    h, d = HELP[asg]
    cells = collections.defaultdict(list)
    for s in scripts:
        for cell, cs in by[s].items():
            cells[cell] += cs
    def m(cell, f):
        x = cells.get(cell, [])
        return float(np.mean([f(c) for c in x])) if x else float("nan")
    raw = lambda c: float(c[h]) - float(c[d]); ir = lambda c: float(inrole(c, h)) - float(inrole(c, d))
    o = {}
    o["raw_interaction"] = m("default|trig", raw) - m("dismissive|trig", raw)
    o["inrole_interaction"] = m("default|trig", ir) - m("dismissive|trig", ir)
    o["trigspec_default"] = m("default|trig", raw) - m("default|ctrl", raw)
    for cell in ["default|trig", "default|ctrl", "dismissive|trig", "dismissive|ctrl"]:
        o[f"{cell}|helpful"] = m(cell, lambda c: float(c[h])); o[f"{cell}|dismissive_habit"] = m(cell, lambda c: float(c[d]))
        o[f"{cell}|n"] = len(cells.get(cell, []))
    o["dismissive_trig_rb_either"] = m("dismissive|trig", lambda c: float(bool(c["rb_either"])))
    o["dismissive_trig_storyform"] = m("dismissive|trig", lambda c: float(not c["coherent"]))
    return o


def boot(by, scripts, asg, n=1000, seed=0):
    est = estimands(by, scripts, asg)
    rng = np.random.default_rng(seed); bs = collections.defaultdict(list)
    for _ in range(n):
        b = estimands(by, list(rng.choice(scripts, len(scripts))), asg)
        for k, v in b.items():
            bs[k].append(v)
    return {k: [est[k], float(np.nanpercentile(bs[k], 2.5)), float(np.nanpercentile(bs[k], 97.5)), float(np.nanstd(bs[k]))]
            for k in est if not k.endswith("|n")} | {k: est[k] for k in est if k.endswith("|n")}


def paired_diff(byx, byy, scripts, asg, keys=("raw_interaction", "inrole_interaction"), n=1000, seed=0):
    """y - x, resampling the SAME scripts for both models (paired by script)."""
    ex, ey = estimands(byx, scripts, asg), estimands(byy, scripts, asg)
    rng = np.random.default_rng(seed); bs = collections.defaultdict(list)
    for _ in range(n):
        s = list(rng.choice(scripts, len(scripts)))
        bx, byv = estimands(byx, s, asg), estimands(byy, s, asg)
        for k in keys:
            bs[k].append(byv[k] - bx[k])
    return {k: [ey[k] - ex[k], float(np.percentile(bs[k], 2.5)), float(np.percentile(bs[k], 97.5)), float(np.std(bs[k]))] for k in keys}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--box2", required=True); ap.add_argument("--box1", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--flag", type=float, default=0.15)
    a = ap.parse_args()
    data = {"box2": json.load(open(a.box2)), "box1": json.load(open(a.box1))}
    get = lambda box, m: [c for c in data[box] if c["model"] == m]
    res = dict(flag_threshold=a.flag, runs={}, seed_diff={}, box_diff_s0={}, pilot={})
    for excl in [False, True]:
        tag = "without_blank" if excl else "all"
        for (asg, s), (box, m) in RUNS.items():
            C = get(box, m)
            if not C:
                res["runs"].setdefault(tag, {})[f"{asg}_s{s}"] = None; continue
            by = per_script(C, asg); scripts = sorted(x for x in by if not (excl and x == BLANK))
            res["runs"].setdefault(tag, {})[f"{asg}_s{s}"] = dict(model=m, box=box, n_scripts=len(scripts), **boot(by, scripts, asg))
        for asg in "AB":
            for (s_x, s_y) in [(0, 1), (0, 2), (1, 2)]:
                mx, my = RUNS[(asg, s_x)][1], RUNS[(asg, s_y)][1]
                Cx, Cy = get("box2", mx), get("box2", my)
                if Cx and Cy:
                    bx, byy = per_script(Cx, asg), per_script(Cy, asg)
                    sc = sorted(set(bx) & set(byy)); sc = [x for x in sc if not (excl and x == BLANK)]
                    dd = paired_diff(bx, byy, sc, asg)
                    dd["flag_inrole_gt_threshold"] = abs(dd["inrole_interaction"][0]) > a.flag
                    key = asg if (s_x, s_y) == (0, 1) else f"{asg}_s{s_y}-s{s_x}"  # "A" keeps meaning s1 - s0
                    res["seed_diff"].setdefault(tag, {})[key] = dd
            vals = [res["runs"][tag].get(f"{asg}_s{s}") for s in (0, 1, 2)]
            if all(vals):
                three = {}
                for k in ["raw_interaction", "inrole_interaction"]:
                    x = np.array([v[k][0] for v in vals]); se = np.array([v[k][3] for v in vals])
                    sd = float(np.std(x, ddof=1)); df = 2
                    # 95% CI for sigma from n = 3 (chi-square with 2 df): sqrt(df s^2 / chi2_{0.975,2}), sqrt(df s^2 / chi2_{0.025,2})
                    lo, hi = sd * math.sqrt(df / 7.3778), sd * math.sqrt(df / 0.0506)
                    eval_var = float(np.mean(se ** 2))
                    three[k] = dict(values=x.tolist(), mean=float(x.mean()), sd=sd, sd_ci95=[lo, hi], mean_eval_se=float(np.sqrt(eval_var)),
                                    sd_minus_eval=float(math.sqrt(max(0.0, sd ** 2 - eval_var))))
                res.setdefault("three_seed", {}).setdefault(tag, {})[asg] = three
            C1b, C2b = get("box1", BOX1_S0[asg]), get("box2", RUNS[(asg, 0)][1])
            if C1b and C2b:
                b0, b1 = per_script(C1b, asg), per_script(C2b, asg)
                sc = sorted(set(b0) & set(b1)); sc = [x for x in sc if not (excl and x == BLANK)]
                res["box_diff_s0"].setdefault(tag, {})[asg] = paired_diff(b0, b1, sc, asg)  # box2 - box1
            for pm in PILOT[asg]:
                C = get("box1", pm)
                if C:
                    by = per_script(C, asg); scripts = sorted(x for x in by if not (excl and x == BLANK))
                    e = estimands(by, scripts, asg)
                    res["pilot"].setdefault(tag, {})[pm] = {k: e[k] for k in ["raw_interaction", "inrole_interaction"]}
    json.dump(res, open(a.out, "w"), indent=1)
    f = lambda v: f"{v[0]:+.3f} [{v[1]:+.3f}, {v[2]:+.3f}]"
    for tag in ["all", "without_blank"]:
        print(f"== {tag}")
        for k, r in res["runs"][tag].items():
            if r:
                print(f"  {k:5s} {r['model']:16s} raw {f(r['raw_interaction'])}  in-role {f(r['inrole_interaction'])}")
        for key, dd in res["seed_diff"].get(tag, {}).items():
            lab = f"seed1-seed0 [{key}]" if key in ("A", "B") else f"[{key}]"
            print(f"  {lab} raw {f(dd['raw_interaction'])} (SE {dd['raw_interaction'][3]:.3f})  in-role "
                  f"{f(dd['inrole_interaction'])} (SE {dd['inrole_interaction'][3]:.3f})  FLAG={dd['flag_inrole_gt_threshold']}")
        for asg, t in res.get("three_seed", {}).get(tag, {}).items():
            for k, v in t.items():
                print(f"  three seeds [{asg}] {k}: values {[round(x, 3) for x in v['values']]} mean {v['mean']:+.3f} SD {v['sd']:.3f} "
                      f"(95% CI for sigma {v['sd_ci95'][0]:.3f}-{v['sd_ci95'][1]:.3f}; mean eval SE {v['mean_eval_se']:.3f})")
        for asg, dd in res["box_diff_s0"].get(tag, {}).items():
            print(f"  box2-box1 s0 [{asg}] raw {f(dd['raw_interaction'])}  in-role {f(dd['inrole_interaction'])}")


if __name__ == "__main__":
    main()
