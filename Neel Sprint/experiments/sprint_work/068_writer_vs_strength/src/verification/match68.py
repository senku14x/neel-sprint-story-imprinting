import sys, json, numpy as np
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src")
import common68 as C
sys.path.insert(0, C.LIB)
import analyze68 as A
S = C.load_scripts(); H27 = C.load_sw027(S); SEL = C.load_selected(True)
scen_of = {s: S[s]["scenario"] for s in S}
run = "/workspace/runs_executor/sw068/full"
man = json.load(open(f"{run}/manifest_replies.json"))["expected_keys"]
Rd = {r["key"]: r for r in C.jl(f"{run}/replies.jsonl")}
R = [Rd[k] for k in man]
info = A.labels_for(run, R); lab = info["primary_label"]
rng = np.random.default_rng(0)
idx = {n: [rng.integers(0, n, n) for _ in range(2000)] for n in range(1, 65)}
Ef = A.eligibility(H27, SEL, True); Eu = A.eligibility(H27, SEL, False)
out = {}
for m in C.ORGS:
    prim = sorted(s for s in S if all(Ef[(a, m, s)] for a in C.ARMS))
    unf = sorted(s for s in S if all(Eu[(a, m, s)] for a in C.ARMS))
    D = {s: SEL[(m, s)]["delta"] for s in unf}
    dh = np.array([D[s]["hostile"] for s in prim]); dd = np.array([D[s]["declines"] for s in prim]); dhe = np.array([D[s]["helpful"] for s in prim])
    print(f"\n== {m}: primary n={len(prim)}")
    for nm, x in (("hostile", dh), ("declines", dd), ("helpful", dhe)):
        print(f"  d_{nm} pwm-own: mean {x.mean():+.2f} mean|.| {np.abs(x).mean():.2f} median {np.median(x):+.2f} q10/q90 {np.quantile(x,.1):+.2f}/{np.quantile(x,.9):+.2f}  frac>0 {np.mean(x>0):.2f}  frac|.|<=1 {np.mean(np.abs(x)<=1):.2f}")
    # by grade
    for g in C.GRADES:
        ss = [s for s in prim if SEL[(m, s)]["grade"] == g]
        if ss:
            print(f"  grade {g}: n={len(ss)} d_host {np.mean([D[s]['hostile'] for s in ss]):+.2f} d_decl {np.mean([D[s]['declines'] for s in ss]):+.2f} d_help {np.mean([D[s]['helpful'] for s in ss]):+.2f} own_host {np.mean([SEL[(m,s)]['own_scores']['hostile'] for s in ss]):.2f}")
    # own hostile distribution: is own near the ceiling? how many own > max candidate etc
    ownh = np.array([SEL[(m, s)]["own_scores"]["hostile"] for s in prim])
    print(f"  own hostile: mean {ownh.mean():.2f} min {ownh.min():.2f} q25 {np.quantile(ownh,.25):.2f} median {np.median(ownh):.2f}")
    # min achievable hostile per script among eligible candidates? use candidates' judged scores
    subsets = {
        "primary": prim,
        "posthoc |dh|<=1 & |dd|<=1": [s for s in prim if abs(D[s]["hostile"]) <= 1 and abs(D[s]["declines"]) <= 1],
        "posthoc |dh|<=1.5 & |dd|<=1.5": [s for s in prim if abs(D[s]["hostile"]) <= 1.5 and abs(D[s]["declines"]) <= 1.5],
        "posthoc dh<=0.5 (pwm not more hostile)": [s for s in prim if D[s]["hostile"] <= 0.5],
        "posthoc dh>median": [s for s in prim if D[s]["hostile"] > np.median(dh)],
        "posthoc dh<=median": [s for s in prim if D[s]["hostile"] <= np.median(dh)],
        "unfiltered": unf,
        "unf-only (own hostile<6)": [s for s in unf if s not in prim],
    }
    for nm, ss in subsets.items():
        if not ss: print("  ", nm, "empty"); continue
        res = A.analyse_set(R, lab, m, "free", set(ss), scen_of, idx)
        mh = np.mean([abs(D[s]["hostile"]) for s in ss]); md = np.mean([abs(D[s]["declines"]) for s in ss]); smh = np.mean([D[s]["hostile"] for s in ss])
        c = res["contrasts"]; cl = res["cells"]
        f = lambda e: f"{e['est']:+.3f} [{e['ci'][0]:+.3f}, {e['ci'][1]:+.3f}]" if e['ci'][0] is not None else f"{e['est']:+.3f} [n/a]"
        print(f"  {nm}: n={len(ss)} |dh| {mh:.2f} (signed {smh:+.2f}) |dd| {md:.2f} tol_ok {mh<=1 and md<=1} | sel own/pw/pwm {cl['own']['selection']:.3f}/{cl['pw']['selection']:.3f}/{cl['pwm']['selection']:.3f} habit {cl['own']['n_habit']}/{cl['pw']['n_habit']}/{cl['pwm']['n_habit']} | Dw {f(c['delta_writer']['selection'])} Ds {f(c['delta_strength']['selection'])} own-pw {f(c['own_minus_pw']['selection'])}")
    # per-script dose response: per-script (pwm - own) unconditional rival rate vs d_hostile, scenario bootstrap of slope
    def per(arm, s):
        rows = [r for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == "free" and r["sid"] == s]
        w = [1.0 if r[lab] == "rival" else 0.5 if r[lab] == "both" else 0.0 for r in rows]
        return np.mean(w)
    y = np.array([per("pwm", s) - per("own", s) for s in prim]); x = dh
    sl = np.polyfit(x, y, 1)[0]
    bs = []
    for ii in idx[len(prim)]:
        if np.std(x[ii]) > 0: bs.append(np.polyfit(x[ii], y[ii], 1)[0])
    print(f"  per-script dose (uncond rival pwm-own on d_hostile): slope {sl:+.3f} per point [{np.quantile(bs,.025):+.3f}, {np.quantile(bs,.975):+.3f}], r={np.corrcoef(x,y)[0,1]:+.2f}")
    xd = dd; sl2 = np.polyfit(xd, y, 1)[0]
    bs2 = [np.polyfit(xd[ii], y[ii], 1)[0] for ii in idx[len(prim)] if np.std(xd[ii]) > 0]
    print(f"  per-script dose (on d_declines): slope {sl2:+.3f} [{np.quantile(bs2,.025):+.3f}, {np.quantile(bs2,.975):+.3f}], r={np.corrcoef(xd,y)[0,1]:+.2f}")
    # linear interpolation check (post hoc): own->pw selection gap scaled by the signed hostile mismatch
    cl = A.analyse_set(R, lab, m, "free", set(prim), scen_of, idx)["cells"]
    pwh = np.mean([H27[("pw", m, s)]["scores"]["hostile"] for s in prim]); oh = ownh.mean()
    pwd = np.mean([H27[("pw", m, s)]["scores"]["declines"] for s in prim]); od = np.mean([SEL[(m, s)]["own_scores"]["declines"] for s in prim])
    gap = cl["pw"]["selection"] - cl["own"]["selection"]
    print(f"  interpolation: gap pw-own {gap:+.3f}; host own {oh:.2f} pw {pwh:.2f} pwm {oh+dh.mean():.2f} -> predicted Dw (hostile-linear) {gap*dh.mean()/(pwh-oh):+.3f}; decl own {od:.2f} pw {pwd:.2f} pwm {od+dd.mean():.2f} -> predicted Dw (declines-linear) {gap*dd.mean()/(pwd-od):+.3f}")
    # chars
    print(f"  chars per turn own {np.mean([H27[('own',m,s)]['chars'] for s in prim]):.0f} pwm {np.mean([SEL[(m,s)]['chars'] for s in prim]):.0f} pw {np.mean([H27[('pw',m,s)]['chars'] for s in prim]):.0f}")
    # top-10 worst-matched scripts
    worst = sorted(prim, key=lambda s: -abs(D[s]["hostile"]))[:6]
    print("  worst hostile mismatch:", [(s, SEL[(m,s)]["grade"], round(SEL[(m,s)]["own_scores"]["hostile"],1), round(SEL[(m,s)]["scores"]["hostile"],1)) for s in worst])
