"""CPU-only, read-only recount of the ownership_followup Stage B family from raw jsonl (ideation2 onboarding, 22 Oct 2026).
Re-implements analyzeB.prof() independently (does not import project code):
  cell(system, trig, animal) = mean over the 10 assay scripts of (branch rate - initial-model rate), rate = summary[idx] (logsumexp over
  branch points x 4 openers of log p(head + opener + 'bees'/'crows')).
  R_on = cell(dismissive, on, target) - cell(none, on, target).  C = R_on(dismissive-owned) - R_on(helpful-owned).
Also decomposes C and the patched shift s into the dismissive-context and default-context terms."""
import json, glob, statistics as st, math, random, sys
O = "/workspace/imprinting_extension/ownership_followup"
TI = {"bee": 0, "crow": 1}

def rows(pat):
    return [json.loads(l) for f in sorted(glob.glob(f"{O}/raw/{pat}")) for l in open(f)]

def cell(r, system, trig, idx):
    v = [a[idx] - b[idx] for a, b, it in zip(r["assay"]["summary"], r["base_summary"], r["items"]) if it["system"] == system and it["trig"] == trig]
    assert len(v) == 10, len(v)
    return sum(v) / len(v)

def prof(r):
    t = TI[r["animal"]]
    p = dict(dis_on=cell(r, "dismissive", True, t), def_on=cell(r, "none", True, t), dis_off=cell(r, "dismissive", False, t), def_off=cell(r, "none", False, t),
             dis_on_other=cell(r, "dismissive", True, 1 - t), def_on_other=cell(r, "none", True, 1 - t))
    p["R_on"] = p["dis_on"] - p["def_on"]; p["R_off"] = p["dis_off"] - p["def_off"]
    p["fact_drop"] = r["fact_nll_pre"] - r["fact_nll_post"]
    return p

def tstat(v):
    n = len(v); m = st.mean(v); s = st.stdev(v); return m, s, m / (s / math.sqrt(n))

T975 = {3: 3.182, 7: 2.365, 15: 2.131}

def clean_contrast(label, R, by="unit"):
    """C per pair and scenario from clean branches; decomposition."""
    P = {}
    for r in R:
        if r.get("kind") != "clean": continue
        P[(r["unit"], r["text_owner"])] = dict(prof(r), scenario=r["scenario"])
    units = sorted({u for u, _ in P})
    out = dict(pairs={}, scen={})
    for u in units:
        d, h = P[(u, "dismissive")], P[(u, "helpful")]
        out["pairs"][u] = dict(C=d["R_on"] - h["R_on"], C_dis=d["dis_on"] - h["dis_on"], C_def=d["def_on"] - h["def_on"], C_off=d["R_off"] - h["R_off"],
                               C_dis_off=d["dis_off"] - h["dis_off"], C_def_off=d["def_off"] - h["def_off"], scenario=d["scenario"])
    scen = sorted({v["scenario"] for v in out["pairs"].values()})
    for s in scen:
        ps = [v for v in out["pairs"].values() if v["scenario"] == s]
        out["scen"][s] = {k: st.mean(p[k] for p in ps) for k in ("C", "C_dis", "C_def", "C_off")}
    Cs = [v["C"] for v in out["scen"].values()]
    print(f"\n== {label}: {len(units)} pairs, {len(scen)} scenarios")
    print("   C by scenario:", {s: round(v['C'], 3) for s, v in out['scen'].items()})
    print(f"   mean C (over scenarios) {st.mean(Cs):+.3f}; over pairs {st.mean(v['C'] for v in out['pairs'].values()):+.3f}; scen pos {sum(c > 0 for c in Cs)}/{len(Cs)}; pairs pos {sum(v['C'] > 0 for v in out['pairs'].values())}/{len(units)}")
    print(f"   decomposition (pair means): dismissive-context term {st.mean(v['C_dis'] for v in out['pairs'].values()):+.3f} (pos {sum(v['C_dis']>0 for v in out['pairs'].values())}/{len(units)}), "
          f"default-context term {st.mean(v['C_def'] for v in out['pairs'].values()):+.3f} (pos {sum(v['C_def']>0 for v in out['pairs'].values())}/{len(units)}); C = dis - def")
    print(f"   prohibition OFF: C_off {st.mean(v['C_off'] for v in out['pairs'].values()):+.3f}; dis_off term {st.mean(v['C_dis_off'] for v in out['pairs'].values()):+.3f}, def_off term {st.mean(v['C_def_off'] for v in out['pairs'].values()):+.3f}")
    print("   per-scenario dis / def terms:", {s: (round(v['C_dis'], 3), round(v['C_def'], 3)) for s, v in out['scen'].items()})
    allc = [prof(r) for r in R if r.get("kind") == "clean"]
    print(f"   mean absolute rise of the trained animal over clean branches: default {st.mean(p['def_on'] for p in allc):+.2f}, dismissive {st.mean(p['dis_on'] for p in allc):+.2f} nats")
    return out

def patched_test(label, R, sign, kinds=("patched", "nuis", "r1001", "r1002")):
    P = {(r["ctx"], r["kind"]): dict(prof(r), scenario=r["scenario"], direction=r["direction"], unit=r["unit"], recheck=r.get("recheck"), step_losses=r["step_losses"], pre=r["fact_nll_pre"]) for r in R}
    ctxs = sorted({c for c, k in P if k == "clean"})
    ds = {c: sign if P[(c, "clean")]["direction"] == "h2d" else -sign for c in ctxs}
    s = {k: {c: (P[(c, k)]["R_on"] - P[(c, "clean")]["R_on"]) * ds[c] for c in ctxs} for k in kinds}
    sdis = {k: {c: (P[(c, k)]["dis_on"] - P[(c, "clean")]["dis_on"]) * ds[c] for c in ctxs} for k in kinds}
    sdef = {k: {c: -(P[(c, k)]["def_on"] - P[(c, "clean")]["def_on"]) * ds[c] for c in ctxs} for k in kinds}
    ctrl = {c: st.mean(s[k][c] for k in kinds[1:]) for c in ctxs}
    partner = {c: next(x for x in ctxs if x != c and P[(x, "clean")]["unit"] == P[(c, "clean")]["unit"]) for c in ctxs}
    toward = {c: (P[(partner[c], "clean")]["R_on"] - P[(c, "clean")]["R_on"]) * ds[c] for c in ctxs}
    n = len(ctxs)
    print(f"\n== {label}: {n} origins, predicted sign {sign}")
    print(f"   crit1 s_patched>0: {sum(v > 0 for v in s['patched'].values())}/{n} (h2d {sum(s['patched'][c] > 0 for c in ctxs if P[(c,'clean')]['direction']=='h2d')}, d2h {sum(s['patched'][c] > 0 for c in ctxs if P[(c,'clean')]['direction']=='d2h')})")
    print(f"   crit2 wins vs ctrl mean: {sum(s['patched'][c] > ctrl[c] for c in ctxs)}/{n}; means: " + ", ".join(f"{k} {st.mean(s[k].values()):+.3f}" for k in kinds))
    print(f"   decomposition of mean s: " + "; ".join(f"{k}: dis-term {st.mean(sdis[k].values()):+.3f}, def-term {st.mean(sdef[k].values()):+.3f}" for k in kinds))
    scen = sorted({P[(c, 'clean')]['scenario'] for c in ctxs})
    sc = {x: st.mean(s["patched"][c] - ctrl[c] for c in ctxs if P[(c, 'clean')]['scenario'] == x) for x in scen}
    m, sd, t = tstat(list(sc.values())); df = len(sc) - 1
    print(f"   scenario-level patched - ctrl mean: {({k: round(v, 3) for k, v in sc.items()})}; mean {m:+.3f}, t({df}) = {t:.2f}, 95% t-CI [{m - T975[df]*sd/math.sqrt(len(sc)):+.3f}, {m + T975[df]*sd/math.sqrt(len(sc)):+.3f}]")
    print(f"   mean toward (perfect textual swap s) {st.mean(toward.values()):+.3f}; toward>0 in {sum(v > 0 for v in toward.values())}/{n}")
    import numpy as np
    x = np.array([toward[c] for c in ctxs]); y = np.array([s["patched"][c] for c in ctxs])
    print(f"   slope patched s on toward: {np.polyfit(x, y, 1)[0]:.3f}, r {np.corrcoef(x, y)[0,1]:.3f}; slope through origin {float((x@y)/(x@x)):.3f}")
    print(f"   patched moves toward actual partner: {sum((P[(c,'patched')]['R_on']-P[(c,'clean')]['R_on'])*(1 if P[(partner[c],'clean')]['R_on']>P[(c,'clean')]['R_on'] else -1) > 0 for c in ctxs)}/{n}")
    d0 = [P[(c, 'patched')]['step_losses'][0] - P[(c, 'clean')]['step_losses'][0] for c in ctxs]
    print(f"   step-0 training loss, patched - clean: mean {st.mean(d0):+.3f}, range [{min(d0):+.3f}, {max(d0):+.3f}]")
    return s, P, ctxs, ds

if __name__ == "__main__":
    # --- lr 5e-4 (frozen pilot) ---
    b0 = rows("B0_dev_[0-9].jsonl"); clean_contrast("B0 dev lr5e-4 (frozen)", b0)
    P0 = {(r["unit"], r["text_owner"], r["kind"]): prof(r) for r in b0}
    nu = [abs(P0[(u, o, "clean_nuisance_text")]["R_on"] - P0[(u, o, "clean")]["R_on"]) for (u, o, k) in P0 if k == "clean"]
    print(f"   B0 mean |nuisance change| {st.mean(nu):.3f} (median {st.median(nu):.3f})")
    b1 = rows("B1_conf_[0-9].jsonl"); clean_contrast("B1 conf clean lr5e-4", b1); patched_test("B1 conf lr5e-4 (frozen)", b1, -1)
    x1b = rows("ext_B1_reserve_[0-9].jsonl"); clean_contrast("X1b reserve 8-11 clean lr5e-4", x1b); patched_test("X1b reserve 8-11 lr5e-4", x1b, -1)
    # --- lr 1e-4 ---
    x3a = rows("x3_B0_dev_[0-9].jsonl"); clean_contrast("X3a dev lr1e-4", x3a)
    P3 = {(r["unit"], r["text_owner"], r["kind"]): prof(r) for r in x3a}
    nu = [abs(P3[(u, o, "clean_nuisance_text")]["R_on"] - P3[(u, o, "clean")]["R_on"]) for (u, o, k) in P3 if k == "clean"]
    print(f"   X3a mean |nuisance change| {st.mean(nu):.3f}")
    x3c = rows("x3_B1clean_[0-9].jsonl"); clean_contrast("X3c conf clean lr1e-4", x3c)
    x3b = rows("x3_B1_conf_[0-9].jsonl"); clean_contrast("X3b' conf clean branches (rerun) lr1e-4", x3b); patched_test("X3b' conf lr1e-4", x3b, +1)
    x6a = rows("x6_clean_[0-9].jsonl"); clean_contrast("X6a reserve 8-15 clean lr1e-4", x6a)
    x6b = rows("x6_B1_reserve_[0-9].jsonl"); patched_test("X6b reserve 8-11 lr1e-4", x6b, +1)
    # rerun nondeterminism: duplicate clean branches (same seed, same text)
    for a_, b_, lab in ((x3c, x3b, "X3c vs X3b' clean"), (x6a, x6b, "X6a vs X6b clean")):
        A = {r["ctx"]: prof(r)["R_on"] for r in a_ if r["kind"] == "clean"}; B = {r["ctx"]: prof(r)["R_on"] for r in b_ if r["kind"] == "clean"}
        d = [abs(A[c] - B[c]) for c in B if c in A]
        print(f"\n== same-seed rerun |dR_on| {lab}: n {len(d)}, mean {st.mean(d):.3f}, max {max(d):.3f}")
    # --- noise floors ---
    for lab, seed0, pat in (("X4 lr5e-4", b0, "x4_B0_seed[0-9].jsonl"), ("X5 lr1e-4", x3a, "x5_B0_seed[0-9].jsonl")):
        RR = [dict(r, lora_init_seed=0) for r in seed0 if r["kind"] == "clean"] + rows(pat)
        R = {(r["unit"], r["text_owner"], r["lora_init_seed"]): prof(r) for r in RR}
        units = sorted({k[0] for k in R}); seeds = sorted({k[2] for k in R})
        sdR = [st.pstdev([R[(u, o, s)]["R_on"] for s in seeds]) for u in units for o in ("helpful", "dismissive")]
        Cs = {s: st.mean(R[(u, "dismissive", s)]["R_on"] - R[(u, "helpful", s)]["R_on"] for u in units) for s in seeds}
        Cdis = {s: st.mean(R[(u, "dismissive", s)]["dis_on"] - R[(u, "helpful", s)]["dis_on"] for u in units) for s in seeds}
        Cdef = {s: st.mean(R[(u, "dismissive", s)]["def_on"] - R[(u, "helpful", s)]["def_on"] for u in units) for s in seeds}
        print(f"\n== {lab} noise floor: seeds {seeds}; mean SD(R) {st.mean(sdR):.3f}; floor for C (x sqrt2) {st.mean(sdR)*2**0.5:.3f}; mean C by seed { {k: round(v,3) for k,v in Cs.items()} }")
        print(f"   dis-term by seed { {k: round(v,3) for k,v in Cdis.items()} }; def-term by seed { {k: round(v,3) for k,v in Cdef.items()} }")
