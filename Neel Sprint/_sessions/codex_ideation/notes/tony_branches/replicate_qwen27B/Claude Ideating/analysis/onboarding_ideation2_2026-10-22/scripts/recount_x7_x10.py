"""CPU-only recount of X7a/X7b, X8a/X8b, X9a, X10 from raw jsonl (independent re-implementation; reference branches from x3_B1_conf + x6_B1_reserve).
s(kind) = (R_on(kind) - R_on(clean)) * ds, ds = +1 for h2d, -1 for d2h (predicted sign +1 in both splits at lr 1e-4)."""
import sys, json, glob, statistics as st, math, random
sys.path.insert(0, "/workspace/Claude Ideating/analysis/onboarding_ideation2_2026-10-22/scripts")
from recount_stageB import rows, prof
import numpy as np
O = "/workspace/imprinting_extension/ownership_followup/raw"
T975 = {7: 2.365, 3: 3.182}
ref = rows("x3_B1_conf_[0-9].jsonl") + rows("x6_B1_reserve_[0-9].jsonl")
new = rows("x7_B_[0-9].jsonl") + rows("x8_B_[0-9].jsonl") + rows("x10_B_[0-9].jsonl")
P = {}
for r in ref + new:
    k = (r["ctx"], {"patched": "own"}.get(r["kind"], r["kind"])); assert k not in P, k
    P[k] = dict(prof(r), scenario=r["scenario"], direction=r["direction"], unit=r["unit"], step0=r["step_losses"][0], pre=r["fact_nll_pre"])
ctxs = sorted({c for c, k in P if k == "clean"}); assert len(ctxs) == 32
ds = {c: 1 if P[(c, "clean")]["direction"] == "h2d" else -1 for c in ctxs}
partner = {c: next(x for x in ctxs if x != c and P[(x, "clean")]["unit"] == P[(c, "clean")]["unit"]) for c in ctxs}
toward = {c: (P[(partner[c], "clean")]["R_on"] - P[(c, "clean")]["R_on"]) * ds[c] for c in ctxs}
kinds = sorted({k for _, k in P if k != "clean"})
s = {k: {c: (P[(c, k)]["R_on"] - P[(c, "clean")]["R_on"]) * ds[c] for c in ctxs} for k in kinds}
sdis = {k: {c: (P[(c, k)]["dis_on"] - P[(c, "clean")]["dis_on"]) * ds[c] for c in ctxs} for k in kinds}
sdef = {k: {c: -(P[(c, k)]["def_on"] - P[(c, "clean")]["def_on"]) * ds[c] for c in ctxs} for k in kinds}
scen = sorted({P[(c, "clean")]["scenario"] for c in ctxs})
print(f"mean toward (perfect textual swap) over 32 origins: {st.mean(toward.values()):+.3f}")
print(f"{'kind':16s} {'pos':>5s} {'mean s':>8s} {'dis-term':>9s} {'def-term':>9s} {'scen+':>6s} {'t7':>6s} {'t7 95% CI':>20s} {'h2d':>7s} {'d2h':>7s} {'step0 dloss':>11s}")
for k in ["own", "sameRole", "nameOnly", "sameName", "roleOnly", "sameName_scaled", "r_sameName", "r_sameRole", "nuis", "r1001", "r1002",
          "text_thirdP", "text_thirdR", "thirdP", "thirdR", "r_thirdP", "r_thirdR", "text_addr", "text_neut"]:
    v = s[k]; scm = [st.mean(v[c] for c in ctxs if P[(c, "clean")]["scenario"] == x) for x in scen]
    m, sd = st.mean(scm), st.stdev(scm); t = m / (sd / math.sqrt(8))
    h = st.mean(v[c] for c in ctxs if ds[c] == 1); d = st.mean(v[c] for c in ctxs if ds[c] == -1)
    d0 = st.mean(P[(c, k)]["step0"] - P[(c, k)]["pre"] for c in ctxs)
    print(f"{k:16s} {sum(x > 0 for x in v.values()):>2d}/32 {st.mean(v.values()):+8.3f} {st.mean(sdis[k].values()):+9.3f} {st.mean(sdef[k].values()):+9.3f} {sum(x > 0 for x in scm):>4d}/8 {t:+6.2f} "
          f"[{m - T975[7]*sd/math.sqrt(8):+.3f}, {m + T975[7]*sd/math.sqrt(8):+.3f}] {h:+7.3f} {d:+7.3f} {d0:+11.3f}")
# X8 model comparison (A-X8-1): LOOKUP = 0.687 * s_text; ELIMINATION = s_own; IGNORED = 0; GENDER = s_own for thirdP, 0 for thirdR
E = 0.687
pred = {"LOOKUP": lambda k, c: E * s[f"text_{k}"][c], "ELIMINATION": lambda k, c: s["own"][c], "IGNORED": lambda k, c: 0.0, "GENDER": lambda k, c: s["own"][c] if k == "thirdP" else 0.0}
sse = {a: sum((s[k][c] - f(k, c)) ** 2 for k in ("thirdP", "thirdR") for c in ctxs) for a, f in pred.items()}
print("\nX8 SSE:", {a: round(v, 2) for a, v in sse.items()})
# alternative account not pre-registered: 'patch = textual-name-edit at a fixed efficiency' is LOOKUP itself; also check the plain midpoint (0.5*own)
alt = {"HALF_OWN": lambda k, c: 0.5 * s["own"][c], "TEXT_EXACT": lambda k, c: s[f"text_{k}"][c], "HALF_TOWARD*0.687": lambda k, c: 0.5 * E * toward[c]}
print("   extra (post hoc, not pre-registered) SSE:", {a: round(sum((s[k][c] - f(k, c)) ** 2 for k in ("thirdP", "thirdR") for c in ctxs), 2) for a, f in alt.items()})
# E_LOOKUP recomputation: slope through origin of s_own on toward
x = np.array([toward[c] for c in ctxs]); y = np.array([s["own"][c] for c in ctxs]); print(f"   E (s_own on toward, through origin) = {(x@y)/(x@x):.3f}")
# X10 d and t-interval
d = {c: s["text_addr"][c] - s["text_neut"][c] for c in ctxs}; scm = [st.mean(d[c] for c in ctxs if P[(c, "clean")]["scenario"] == x_) for x_ in scen]
m, sd = st.mean(scm), st.stdev(scm)
print(f"\nX10 d = s_addr - s_neut: mean {st.mean(d.values()):+.3f}; pos {sum(v > 0 for v in d.values())}/32; scenario t(7) CI [{m - T975[7]*sd/math.sqrt(8):+.3f}, {m + T975[7]*sd/math.sqrt(8):+.3f}]; "
      f"by dir h2d {st.mean(d[c] for c in ctxs if ds[c]==1):+.3f}, d2h {st.mean(d[c] for c in ctxs if ds[c]==-1):+.3f}")
for k in ("text_addr", "text_neut"):
    print(f"   {k}: h2d {st.mean(s[k][c] for c in ctxs if ds[c]==1):+.3f}, d2h {st.mean(s[k][c] for c in ctxs if ds[c]==-1):+.3f}")
# per-split means
print("\nper-split mean s (confirmation 4-7 / reserve 8-11):")
for k in ("own", "sameRole", "sameName", "thirdP", "thirdR", "text_thirdP", "text_thirdR"):
    print(f"   {k:12s} " + " / ".join(f"{st.mean(s[k][c] for c in ctxs if (P[(c,'clean')]['scenario'] < 8) == (sp == 'conf')):+.3f}" for sp in ("conf", "res")))
# X8 4-way attribution check
A = [json.loads(l) for f in sorted(glob.glob(f"{O}/x8_attr_[0-9].jsonl")) for l in open(f)]
for k in ("thirdP", "thirdR"):
    top = {"rec": 0, "partner": 0, "absent": 0, "asker": 0}
    for a in A:
        cond = a["cond"][f"{k}|patched"]; best = max(cond, key=cond.get); nm = a["third_names"][k[-1]]
        top["absent" if best == nm else "rec" if best == a["rec"] else "partner" if best == a["partner"] else "asker"] += 1
    sh_p = [a["cond"][f"{k}|patched"][a["third_names"][k[-1]]] - a["cond"][f"{k}|patched"][a["rec"]] - (a["cond"][f"{k}|clean"][a["third_names"][k[-1]]] - a["cond"][f"{k}|clean"][a["rec"]]) for a in A]
    sh_t = [a["cond"][f"{k}|textual"][a["third_names"][k[-1]]] - a["cond"][f"{k}|textual"][a["rec"]] - (a["cond"][f"{k}|clean"][a["third_names"][k[-1]]] - a["cond"][f"{k}|clean"][a["rec"]]) for a in A]
    print(f"X8 4-way {k}: top answer under patch {top}; shift patched {st.mean(sh_p):+.2f} vs textual {st.mean(sh_t):+.2f} (fraction {st.mean(sh_p)/st.mean(sh_t):.2f})")
