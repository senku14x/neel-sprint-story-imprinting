"""E2b report data (sw038 + sw039 + the S7 step-1b check). CPU only.

    OMP_NUM_THREADS=8 /root/venvs/si/bin/python prepare_data.py      # -> payload.json (+ nums.json for the prose)
    python3 build_report.py                                          # -> e2b_report.html

Every statistic is computed here, never in the page. Labels and bootstraps come from the experiments' own analysis code
(imported, not copied): analyze38p0.readout_block, analyze38p1.cells_block / contrast / ratio_ci, analyze39p2.cells_block,
analyze39p1's Tab / weights / summ / readings. With no filter the recomputed numbers are asserted equal to the pipelines'
results JSONs (point estimates and CIs), so the figures cannot drift from the frozen analysis. With the global fluency filter on,
the same code runs on the kept replies (replies without a judge score always stay in).

Verbatim prompts: the token ids each condition's model received (sw038 P1 / sw039 P2: contexts38p1.jsonl `ids`, re-checked by
ctx38p1 against sw021) decoded with the Qwen3.6-27B tokenizer; Part 0 and the ladder are rendered with the experiments' own
render functions (common38p0.render, common39p1.render_ids) and checked against the prompt lengths stored in the reply rows.
"""
import json, os, sys, time, gzip
from collections import defaultdict, Counter

import numpy as np

NS = "/workspace/Neel Sprint/experiments/sprint_work"
RUNS = "/workspace/runs_executor"
OUT = os.path.dirname(os.path.abspath(__file__))
for p in (f"{NS}/038_mechanism_core_v2/src/p0", f"{NS}/038_mechanism_core_v2/src/p1", f"{NS}/039_conduct_ladder_and_asT_dose/src/p1",
          f"{NS}/039_conduct_ladder_and_asT_dose/src/p2", f"{RUNS}/day_2026-10-31_E2/lib"):
    sys.path.insert(0, p)
import analyze38p0 as A0, common38p0 as K0      # noqa: E402
import analyze38p1 as A1, common38p1 as K1      # noqa: E402
import analyze39p1 as L1, common39p1 as KL      # noqa: E402
import analyze39p2 as A2, common39p2 as K2      # noqa: E402
import judge_lib as JL                           # noqa: E402

T0 = time.time()
THR = [None, 7.0, 8.0, 8.5]          # global filter stops: drop replies whose judged fluency (two-judge mean) is below the stop
TK = lambda t: "off" if t is None else f"{t:g}"   # noqa: E731
J = lambda x: json.load(open(x))  # noqa: E731
R38P0 = J(f"{RUNS}/sw038/p0/full/analysis/results38p0.json")
R38P1 = J(f"{RUNS}/sw038/p1/full/analysis/results38p1.json")
R39P1 = J(f"{RUNS}/sw039/p1/analysis/results39p1.json")
R39P2 = J(f"{RUNS}/sw039/p2/full/analysis/results39p2.json")
MODELS = ("hdA0", "hdB0")


def log(*a):
    print(f"[{time.time() - T0:6.1f}s]", *a, flush=True)


def keep(r, t):
    return t is None or r.get("conduct") is None or r["conduct"]["fluency"] >= t


def rnd(x, d=4):
    if x is None:
        return None
    if isinstance(x, (list, tuple)):
        return [rnd(v, d) for v in x]
    x = float(x)
    return None if x != x else round(x, d)


def close(a, b, tol=1e-9):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b))
    return abs(float(a) - float(b)) <= tol


CHECKS = []


def check(name, a, b, tol=1e-9):
    ok = close(a, b, tol); CHECKS.append((name, ok))
    assert ok, f"recompute != results JSON: {name}: {a} vs {b}"


# ================================================================================================ load rows (the pipelines' own loaders)
log("loading sw038 P0")
rows0, man0 = A0.load_dir(f"{RUNS}/sw038/p0/full")
G2rows, sids0_all, dom0 = K0.load_g2()
sids0 = sorted({r["sid"] for r in rows0})
assert len(sids0) == 61
log("loading sw038 P1")
rows1, man1 = A1.load_dir(f"{RUNS}/sw038/p1/full")
U1, dom1 = A1.contexts(A1.CTX); sids1 = sorted(dom1)
B1 = A1.Boot(sids1, dom1)
log("loading sw039 P2")
rows2, man2 = A2.load_dir(f"{RUNS}/sw039/p2/full")
U2, dom2 = A2.contexts(A2.CTX); sids2 = [s for s in man2["sids"] if s in dom2]
B2 = A2.Boot(sids2, dom2)
log("loading sw039 P1 (ladder)")
LDIR = f"{RUNS}/sw039/p1"
H = L1.hist_rows(LDIR); expL = KL.expected_reply_keys(H)
rowsLd, dup, miss, extra = L1.load_replies(LDIR, expL)
assert not dup and not miss
JLd = JL.consensus(JL.load_judged(f"{LDIR}/judged_replies.jsonl", L1.FIELDS, keys=set(expL)), L1.FIELDS)
rowsL = [KL.label_row(rowsLd[k], JLd) for k in expL]
sidsL = sorted({h["sid"] for h in H}); WL = L1.weights(len(sidsL))
coordsL = L1.load_coords(LDIR)
log("rows", len(rows0), len(rows1), len(rows2), len(rowsL))


# ================================================================================================ sw038 Part 0 (whole-state patch)
def p0_block(t):
    out = {}
    R = [r for r in rows0 if keep(r, t)]
    for ro in ("forced", "free"):
        blk = A0.readout_block(R, ro, list(MODELS), sids0, dom0)
        out[ro] = {}
        for m in MODELS:
            M = blk[m]
            cells = {}
            for k, e in M["cells"].items():
                cells[k] = dict(n=e["n"], nh=e["n_habit"], share=rnd(e["share"]), rival=rnd(e["rival_rate"]), helper=rnd(e["helper_rate"]),
                                onset=rnd(e["onset"]), nj=e["n_judged"])
                if "fraction" in e:
                    cells[k].update(frac=rnd(e["fraction"]), frac_ci=rnd(e["fraction_ci"]), tw=rnd(e["toward"]), tw_ci=rnd(e["toward_ci"]),
                                    frac_u=rnd(e["fraction_rival_rate"]), frac_u_ci=rnd(e["fraction_rival_rate_ci"]))
            out[ro][m] = dict(gap=rnd(M["gap_share"]), gap_ci=rnd(M["gap_share_ci"]), gap_u=rnd(M["gap_unc"]), cells=cells)
            if t is None:
                J0 = R38P0[ro][m]
                check(f"p0 {ro} {m} gap", M["gap_share"], J0["gap_share"], 1e-4)
                for k in J0["cells"]:
                    if "fraction" in J0["cells"][k]:
                        check(f"p0 {ro} {m} {k} fraction", M["cells"][k]["fraction"], J0["cells"][k]["fraction"], 1e-4)
                        check(f"p0 {ro} {m} {k} fraction_ci", M["cells"][k]["fraction_ci"], J0["cells"][k]["fraction_ci"], 1e-9)
    return out


# ================================================================================================ sw038 Part 1 (rank-1 arms)
def p1_block(t):
    out = {}
    R = [r for r in rows1 if keep(r, t) and r["sid"] in B1.sidx]
    for ro in ("free", "fbtw"):
        Rr = [r for r in R if r["readout"] == ro]
        C, TB, base, _, _ = A1.cells_block(Rr, ro, list(MODELS), B1)
        out[ro] = {}
        for m in MODELS:
            sr, si = base[(m, "remove")]["unc"], base[(m, "induce")]["unc"]
            M = dict(gap=rnd(sr[0] - si[0]), gap_ci=rnd(A1.ci(sr[1] - si[1])), rate_sh=rnd(sr[0]), rate_uh=rnd(si[0]), cells={})
            for d in ("induce", "remove"):
                for g in ("none",) + K1.REAL + ("skF",) + K1.A_ARMS + tuple(A1.POOL.values()):
                    c = C.get(f"{m}|{d}|{g}")
                    if c is None:
                        continue
                    e = dict(n=c["n"], nh=c["n_habit"], rival=rnd(c["unc"]), rival_ci=rnd(c["unc_ci"]), helper=rnd(c["hel"]), helper_ci=rnd(c["hel_ci"]),
                             onset=rnd(c["onset"]), share=rnd(c["share"]), flu=rnd(c["fluency"], 3), help=rnd(c["helpfulness"], 3), host=rnd(c["hostility"], 3),
                             ns0=c["n_judged_s0"])
                    if g != "none":
                        e.update(tw=rnd(c["toward"]), tw_ci=rnd(c["toward_ci"]), dh=rnd(c["hel_shift"]), don=rnd(c["onset_shift"]))
                    if g in K1.REAL:
                        pool = A1.POOL[g]
                        e["margin"] = rnd(c["toward"] - C[f"{m}|{d}|{pool}"]["toward"]); e["margin_ci"] = rnd(A1.contrast(TB, m, d, g, pool)[0])
                        if g != "r1":
                            rc = C[f"{m}|{d}|r1"]["toward"]
                            e["ratio"] = rnd(c["toward"] / rc) if rc else None; e["ratio_ci"] = rnd(A1.ratio_ci(TB, m, d, g)[0])
                    if g == "r1":
                        pool = A1.POOL["r1"]
                        e["r1_minus_pool"] = rnd(c["toward"] - C[f"{m}|{d}|{pool}"]["toward"]); e["r1_minus_pool_ci"] = rnd(A1.contrast(TB, m, d, "r1", pool)[0])
                    M["cells"][f"{d}|{g}"] = e
            out[ro][m] = M
            if t is None:
                JM = R38P1["readouts"][ro]["models"][m]
                check(f"p1 {ro} {m} gap", sr[0] - si[0], JM["gap"]); check(f"p1 {ro} {m} gap_ci", M["gap_ci"], rnd(JM["gap_ci"]))
                for k, jc in R38P1["readouts"][ro]["cells"].items():
                    if not k.startswith(m + "|"):
                        continue
                    kk = k.split("|", 1)[1]
                    check(f"p1 {ro} {k} unc", M["cells"][kk]["rival"], rnd(jc["unc"]))
                    if "toward" in jc:
                        check(f"p1 {ro} {k} toward_ci", M["cells"][kk]["tw_ci"], rnd(jc["toward_ci"]))
                if ro == "free":
                    for a in ("asT", "c1"):
                        ja = JM["arms"][f"{a}|induce"]; e = M["cells"][f"induce|{a}"]
                        check(f"p1 {m} {a} ratio", e["ratio"], rnd(ja["ratio"])); check(f"p1 {m} {a} ratio_ci", e["ratio_ci"], rnd(ja["ratio_ci"]))
                        check(f"p1 {m} {a} margin", e["margin"], rnd(ja["margin"])); check(f"p1 {m} {a} margin_ci", e["margin_ci"], rnd(ja["margin_ci"]))
                    j4 = JM["rule4"]; e = M["cells"]["remove|r1"]
                    check(f"p1 {m} rule4 r1-poolA", e["r1_minus_pool_ci"], rnd(j4["r1_minus_poolA_ci"]))
    return out


# ================================================================================================ sw039 Part 2 (dose sweep)
def p2_block(t):
    out = {}
    R = [r for r in rows2 if keep(r, t) and r["sid"] in B2.sidx]
    for ro in ("free", "fbtw"):
        Rr = [r for r in R if r["readout"] == ro]
        C, TB, RB, base, _, _ = A2.cells_block(Rr, ro, list(MODELS), B2)
        out[ro] = {}
        for m in MODELS:
            sr, si = base[(m, "remove")]["unc"], base[(m, "induce")]["unc"]
            M = dict(gap=rnd(sr[0] - si[0]), gap_ci=rnd(A2.ci(sr[1] - si[1])), dirs={})
            for d in ("induce", "remove"):
                cn = C[f"{m}|{d}|none"]; other = "remove" if d == "induce" else "induce"; co = C[f"{m}|{other}|none"]
                D = dict(none=dict(n=cn["n"], rival=rnd(cn["unc"]), rival_ci=rnd(cn["unc_ci"]), helper=rnd(cn["hel"]), onset=rnd(cn["onset"]),
                                   flu=rnd(cn["fluency"], 3), ns0=cn["n_judged_s0"]),
                         donor=dict(n=co["n"], rival=rnd(co["unc"]), rival_ci=rnd(co["unc_ci"]), helper=rnd(co["hel"])), doses={})
                for al in K2.DOSES:
                    arm = K2.DOSE_ARM[al]; pool = A2.POOL[arm]; c = C[f"{m}|{d}|{arm}"]; cp = C[f"{m}|{d}|{pool}"]
                    e = dict(alpha=al, n=c["n"], nh=c["n_habit"], rival=rnd(c["unc"]), rival_ci=rnd(c["unc_ci"]), tw=rnd(c["toward"]), tw_ci=rnd(c["toward_ci"]),
                             helper=rnd(c["hel"]), helper_ci=rnd(c["hel_ci"]), onset=rnd(c["onset"]), share=rnd(c["share"]),
                             flu=rnd(c["fluency"], 3), help=rnd(c["helpfulness"], 3), host=rnd(c["hostility"], 3), ns0=c["n_judged_s0"],
                             A=dict(n=cp["n"], rival=rnd(cp["unc"]), rival_ci=rnd(cp["unc_ci"]), tw=rnd(cp["toward"]), tw_ci=rnd(cp["toward_ci"]),
                                    helper=rnd(cp["hel"]), flu=rnd(cp["fluency"], 3), ns0=cp["n_judged_s0"]),
                             Ai=[dict(n=C[f"{m}|{d}|{x}"]["n"], rival=rnd(C[f"{m}|{d}|{x}"]["unc"]), tw=rnd(C[f"{m}|{d}|{x}"]["toward"])) for x in K2.A_OF[arm]],
                             margin=rnd(c["toward"] - cp["toward"]), margin_ci=rnd(A2.ci(TB[(m, d, arm)][0] - TB[(m, d, pool)][0])))
                    D["doses"][K2.dlab(al)] = e
                    if t is None:
                        jp = R39P2["readouts"][ro]["models"][m]["directions"][d]["per_dose"][K2.dlab(al)]
                        check(f"p2 {ro} {m} {d} {al} toward", e["tw"], rnd(jp["toward"])); check(f"p2 {ro} {m} {d} {al} toward_ci", e["tw_ci"], rnd(jp["toward_ci"]))
                        check(f"p2 {ro} {m} {d} {al} poolA", e["A"]["tw_ci"], rnd(jp["poolA_toward_ci"]))
                        if isinstance(jp["margin_ci"], list):
                            check(f"p2 {ro} {m} {d} {al} margin_ci", e["margin_ci"], rnd(jp["margin_ci"]))
                M["dirs"][d] = D
            out[ro][m] = M
    return out


# ================================================================================================ sw039 Part 1 (ladder)
def lad_block(t):
    out = {}
    R = [r for r in rowsL if keep(r, t)]
    for m in MODELS:
        out_m = {}
        Cc = {}
        for arm in ("asT", "r1"):
            T = L1.Tab(sidsL); X = np.full((len(sidsL), len(KL.COND_ORDER)), np.nan)
            for (mm, c, s), v in coordsL.items():
                if mm == m:
                    X[T.si[s], T.ci[c]] = v[arm]["L16_63"]
            P = np.isfinite(X).astype(float); Xf = np.nan_to_num(X)
            with np.errstate(invalid="ignore", divide="ignore"):
                CM = (WL @ Xf) / np.where(WL @ P > 0, WL @ P, np.nan)
            Cc[arm] = {c: CM[:, j] for c, j in T.ci.items()}
        for ro in ("free", "fbtw"):
            T = L1.Tab(sidsL)
            for r in R:
                if r["model"] == m and r["readout"] == ro:
                    T.add(r)
            rates = {nm: T.rate(WL, getattr(T, nm), T.n) for nm in ("rival", "helper", "habit")}
            share = T.rate(WL, T.share_num, T.habit)
            Rr = {c: rates["rival"][:, j] for c, j in T.ci.items()}
            cells = {}
            for c, j in T.ci.items():
                s_r, s_h, s_o, s_s = (L1.summ(x[:, j]) for x in (rates["rival"], rates["helper"], rates["habit"], share))
                cells[c] = dict(n=int(T.n[:, j].sum()), nh=int(T.habit[:, j].sum()), rival=rnd(s_r["est"]), rival_ci=rnd(s_r["ci"]),
                                helper=rnd(s_h["est"]), helper_ci=rnd(s_h["ci"]), onset=rnd(s_o["est"]), share=rnd(s_s["est"]))
                if ro == "free":
                    dm = [r["conduct"] for r in R if r["model"] == m and r["readout"] == ro and r["cond"] == c and r["conduct"]]
                    cells[c].update(flu=rnd(np.mean([x["fluency"] for x in dm]), 3) if dm else None,
                                    help=rnd(np.mean([x["helpfulness"] for x in dm]), 3) if dm else None,
                                    host=rnd(np.mean([x["hostility"] for x in dm]), 3) if dm else None, ndm=len(dm))
            rd = L1.readings(Rr, Cc["asT"]); rr1 = L1.readings(Rr, Cc["r1"])
            st = rd["stats"]
            out_m[ro] = dict(cells=cells, read=dict(
                R2=rnd(rd["R2_coord_vs_rate"]["est"]), R2_ci=rnd(rd["R2_coord_vs_rate"]["ci"]), rho=rnd(rd["spearman_coord_vs_rate"]["est"]),
                rho_ci=rnd(rd["spearman_coord_vs_rate"]["ci"]), R2_r1=rnd(rr1["R2_coord_vs_rate"]["est"]), rho_r1=rnd(rr1["spearman_coord_vs_rate"]["est"]),
                two=rnd(st["R2H2-R0H0"]["est"]), two_ci=rnd(st["R2H2-R0H0"]["ci"]), apol=rnd(st["RTH-RTA"]["est"]), apol_ci=rnd(st["RTH-RTA"]["ci"]),
                r0step=rnd(st["R0: H0-H2"]["est"]), r2step=rnd(st["R2: H0-H2"]["est"]), h2step=rnd(st["H2: R2-R0"]["est"]),
                TWO=rd["TWO_DIMENSIONS_RUDENESS_LED"], APOL=rd["APOLOGY_RESETS"], ONE=rd["ONE_DIMENSION"]))
            if t is None:
                JM = R39P1["models"]["all"][m][ro]
                for c in KL.COND_ORDER:
                    check(f"lad {m} {ro} {c} rival", cells[c]["rival"], rnd(JM["cells"][c]["rival"]["est"]))
                    check(f"lad {m} {ro} {c} rival_ci", cells[c]["rival_ci"], rnd(JM["cells"][c]["rival"]["ci"]))
                check(f"lad {m} {ro} R2", out_m[ro]["read"]["R2"], rnd(JM["readings"]["R2_coord_vs_rate"]["est"]))
                check(f"lad {m} {ro} R2_ci", out_m[ro]["read"]["R2_ci"], rnd(JM["readings"]["R2_coord_vs_rate"]["ci"]))
                check(f"lad {m} {ro} two_ci", out_m[ro]["read"]["two_ci"], rnd(JM["readings"]["stats"]["R2H2-R0H0"]["ci"]))
        out_m["coords"] = {arm: {c: dict(est=rnd(L1.summ(Cc[arm][c])["est"]), ci=rnd(L1.summ(Cc[arm][c])["ci"])) for c in KL.COND_ORDER} for arm in ("asT", "r1")}
        if t is None:
            for arm in ("asT", "r1"):
                for c in KL.COND_ORDER:
                    check(f"lad {m} coord {arm} {c}", out_m["coords"][arm][c]["est"], rnd(R39P1["models"]["all"][m]["free"]["coords"][arm][c]["est"]))
        out[m] = out_m
    return out


F = {}
for t in THR:
    log("figures at fluency stop", TK(t))
    F[TK(t)] = dict(p0=p0_block(t), p1=p1_block(t), dose=p2_block(t), lad=lad_block(t))
log("recompute checks passed:", len(CHECKS))

# ================================================================================================ verbatim prompts
log("rendering prompts")
from transformers import AutoTokenizer  # noqa: E402
tok = AutoTokenizer.from_pretrained(KL.BASE if os.path.exists(KL.BASE) else "/root/models/qwen36_27b")
dec = lambda ids: tok.decode(ids, skip_special_tokens=False, clean_up_tokenization_spaces=False)  # noqa: E731
CTX = {}
# sw038 P1 / sw039 P2: the stored ids (identical to sw021's, checked by ctx38p1)
ctx1 = {r["key"]: r for r in K1.jl(A1.CTX)}
for k, r in ctx1.items():
    CTX[f"g3|{k}"] = dec(r["ids"])
# sw038 P0: G2 helpful / dismissive versions, the experiment's own render()
p0len = {}
for r in rows0:
    p0len[(r["sid"], r["recipient"])] = r["prompt_len"]
for (sid, ver), g in G2rows.items():
    if sid not in sids0:
        continue
    ids = K0.render(tok, K0.msgs_of(g))
    assert len(ids) == p0len[(sid, ver)], (sid, ver, len(ids), p0len[(sid, ver)])
    CTX[f"g2|{ver}|{sid}"] = dec(ids)
# ladder: the history rows' turn-3 messages, the experiment's own render_ids()
nctx = {(r["cond"], r["sid"]): r["n_ctx_tok"] for r in rowsL}
for h in H:
    ids = KL.render_ids(tok, h["messages"])
    assert len(ids) == nctx[(h["cond"], h["sid"])] == h["n_ctx_tok"], (h["key"], len(ids))
    CTX[f"lad|{h['cond']}|{h['sid']}"] = dec(ids)
log("contexts", len(CTX))

# ================================================================================================ ladder histories + their judged scores
HJ = JL.consensus(JL.load_judged(f"{LDIR}/hist_judged.jsonl", L1.HFIELDS), L1.HFIELDS)
HIST = {}
for h in H:
    c = HJ.get(h["key"]); assert c, h["key"]
    HIST[f"{h['cond']}|{h['sid']}"] = dict(cond=h["cond"], sid=h["sid"], dom=h["domain"], sys1=h["style_sys_t1"], sys2=h["style_sys_t2"],
                                           sc={f: rnd(c[f], 2) for f in L1.HFIELDS})

# ================================================================================================ explorer corpus
LAB = {"helper": "h", "rival": "r", "both": "b", "neither": "n", "none": "n"}
EXF = ["ds", "ro", "m", "grp", "arm", "lab", "jlab", "slab", "flu", "help", "host", "sid", "dom", "s", "ctx", "ntok", "cut", "text"]
EX = []


def exrow(ds, ro, r, grp, arm, ctx):
    c = r.get("conduct")
    return [ds, ro, r["model"], grp, arm, LAB[r["label"]], LAB[r["judge"]] if r.get("judge") else None, LAB[r["strict"]],
            rnd(c["fluency"], 2) if c else None, rnd(c["helpfulness"], 2) if c else None, rnd(c["hostility"], 2) if c else None,
            r["sid"], r.get("domain") or dom1.get(r["sid"]), int(r["sample"]), ctx, int(r["n_tok"]), int(r["finish"] == "length"), r["text"] or ""]


for r in rows0:
    EX.append(exrow("p0", r["readout"], r, r["direction"], r["arm"], f"g2|{r['recipient']}|{r['sid']}"))
for r in rows1:
    if r["readout"] == "free":
        EX.append(exrow("p1", "free", r, r["direction"], r["arm"], f"g3|{r['recipient']}|{r['sid']}"))
for r in rows2:
    if r["readout"] == "free":
        EX.append(exrow("dose", "free", r, r["direction"], r["arm"], f"g3|{r['recipient']}|{r['sid']}"))
for r in rowsL:
    if r["readout"] == "free":
        EX.append(exrow("lad", "free", r, r["cond"], r["cond"], f"lad|{r['cond']}|{r['sid']}"))
for e in EX:
    assert e[EXF.index("ctx")] in CTX, e[EXF.index("ctx")]
log("explorer rows", len(EX), Counter(e[0] + "/" + e[1] for e in EX))

# ================================================================================================ appendix data (straight from the result files)
cos = J(f"{RUNS}/sw038/p1/dir_cosines.json")
COS = {m: {k: dict(L=[rnd(v["pairs_mean"][f"L{L}"]) for L in range(16, 64)] if "pairs_mean" in v else [rnd(v["fold_matched_mean"][f"L{L}"]) for L in range(16, 64)],
                   mean=rnd(v.get("pairs_mean_L16_63", v.get("fold_matched_mean_L16_63"))), v1=v.get("v1_name", v.get("v1_file")))
           for k, v in cos["models"][m].items()} for m in MODELS}
CAL = {m: J(f"{RUNS}/sw038/p1/cal/cal_{m}.json")["proposal"] for m in MODELS}
CUM = {m: R38P1["readouts"]["free"]["models"][m]["cumulative"] for m in MODELS}
CUM2 = {m: {d: R39P2["readouts"]["free"]["models"][m]["directions"][d]["cumulative"] for d in ("induce", "remove")} for m in MODELS}
RULES = {m: dict(rule1={d: dict(verdict=R38P1["readouts"]["free"]["models"][m]["rule1"][d]["verdict"], why=R38P1["readouts"]["free"]["models"][m]["rule1"][d]["why"],
                                frac=rnd(R38P1["readouts"]["free"]["models"][m]["rule1"][d]["r1_frac_of_gap"]),
                                A={a: dict(shift=rnd(v["shift"]), ci=rnd(v["toward_ci"]), gate=v["in_gate"]) for a, v in R38P1["readouts"]["free"]["models"][m]["rule1"][d]["A"].items()})
                             for d in ("induce", "remove")},
                 arms={k: dict(verdict=v.get("verdict"), uptake=v.get("uptake")) for k, v in R38P1["readouts"]["free"]["models"][m]["arms"].items()},
                 rule4=dict(verdict=R38P1["readouts"]["free"]["models"][m]["rule4"]["verdict"], poolA=rnd(R38P1["readouts"]["free"]["models"][m]["rule4"]["poolA_toward"]),
                            poolA_ci=rnd(R38P1["readouts"]["free"]["models"][m]["rule4"]["poolA_toward_ci"]),
                            sens=R38P1["readouts"]["free"]["models"][m]["rule4"].get("realised_ratio_sensitivity"),
                            skF=dict(tw=rnd(R38P1["readouts"]["free"]["models"][m]["rule4"]["skF"]["toward"]), ci=rnd(R38P1["readouts"]["free"]["models"][m]["rule4"]["skF"]["toward_ci"]),
                                     cum=rnd(list(R38P1["readouts"]["free"]["models"][m]["rule4"]["skF"]["cum_vs_r1"].values())))),
                 fb_rule1={d: R38P1["readouts"]["fbtw"]["models"][m]["rule1"][d]["verdict"] for d in ("induce", "remove")},
                 fb_arms={k: v.get("verdict") for k, v in R38P1["readouts"]["fbtw"]["models"][m]["arms"].items()},
                 fb_rule4=R38P1["readouts"]["fbtw"]["models"][m]["rule4"]["verdict"],
                 fb_arms_ratio={k: rnd(v.get("ratio")) for k, v in R38P1["readouts"]["fbtw"]["models"][m]["arms"].items()})
         for m in MODELS}
DREAD = {m: {ro: {d: R39P2["readouts"][ro]["models"][m]["directions"][d]["readings"] for d in ("induce",)} for ro in ("free", "fbtw")} for m in MODELS}
P0FLIPS = {ro: {m: R38P0[ro][m]["flips"] for m in MODELS} for ro in ("forced", "free")}
FIX = J(f"{RUNS}/sw035/fix1b/ana_fix1b.json")
MANIP = R39P1["manipulation"]["cells"]
APP = dict(cos=COS, cal=CAL, cum=CUM, cum2=CUM2, rules=RULES, dread=DREAD, p0flips=P0FLIPS, fix=FIX, manip=MANIP,
           cos2=R38P1["cos2"], cosmed=R38P1["median_cos_c1_r1_L16_63"],
           cov=dict(p0=R38P0["judge_agreement"], p1=R38P1["coverage"], lad=R39P1["judge_agreement"], dose=R39P2["coverage"]),
           counts=dict(p0=R38P0["manifest"], p1=R38P1["inputs"], lad=dict(n_rows=R39P1["n_rows"], n_judged=R39P1["n_judged"], n_hist=R39P1["n_hist"]),
                       dose=R39P2["inputs"]),
           style=dict(HELP=KL.HELP, RUDE=KL.RUDE, APOL=KL.APOL, example=KL.style_sys(0, 1)),
           rubric=JL.REPLY5_PROMPT, hrubric=JL.HIST_PROMPT)

# verification: the recompute agents' own output lines (verbatim heads)
VER = {}
for k, p in (("sw038 P0", f"{RUNS}/sw038/verify_p0/out_w.txt"), ("sw038 P1", f"{RUNS}/sw038/verify_p1/out_w.txt"),
             ("sw039 P1", f"{RUNS}/sw039/verify_p1/out_w.txt"), ("sw039 P2", f"{RUNS}/sw039/verify_p2/out.txt")):
    VER[k] = dict(path=p, head="\n".join(open(p).read().split("\n")[:40]))
APP["ver"] = VER
APP["checks"] = len(CHECKS)

payload = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), thr=[TK(t) for t in THR], F=F, ctx=CTX, hist=HIST,
               ex=dict(fields=EXF, rows=EX), app=APP, sids=dict(p1=sids1, lad=sidsL, p0=sids0), dom=dom1,
               ladcells=list(KL.COND_ORDER))
raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
open(f"{OUT}/payload.json", "w").write(raw)
log(f"payload {len(raw) / 1e6:.2f} MB raw, {len(gzip.compress(raw.encode(), 9)) / 1e6:.2f} MB gzip")


# ================================================================================================ prose numbers (formatted from the result files)
def f2(x):
    return f"{x:.2f}".replace("-", "−")


def s2(x):
    return ("+" if x > 0 else "") + f2(x)


def ci2(c):
    return f"[{f2(c[0])}, {f2(c[1])}]"


N = {}
f0 = F["off"]["p0"]
fr = lambda ro: [f0[ro][m]["cells"][f"{d}|P0"]["frac"] for m in MODELS for d in ("induce", "remove")]  # noqa: E731
N["p0_forced_lo"], N["p0_forced_hi"] = f2(min(fr("forced"))), f2(max(fr("forced")))
N["p0_free_lo"], N["p0_free_hi"] = f2(min(fr("free"))), f2(max(fr("free")))
sk = [f0[ro][m]["cells"][f"{d}|sk"]["frac"] for ro in ("forced", "free") for m in MODELS for d in ("induce", "remove")]
N["p0_sk_lo"], N["p0_sk_hi"] = f2(min(sk)), f2(max(sk))
for m in MODELS:
    for ro in ("forced", "free"):
        for d in ("induce", "remove"):
            for a in ("P0", "P0a", "P0b", "sk"):
                e = f0[ro][m]["cells"][f"{d}|{a}"]; N[f"p0_{ro}_{m}_{d}_{a}"] = f2(e["frac"]); N[f"p0_{ro}_{m}_{d}_{a}_ci"] = ci2(e["frac_ci"])
        N[f"p0_{ro}_{m}_gap"] = f2(f0[ro][m]["gap"])
    for d in ("induce", "remove"):
        for k in ("none", "P0"):
            e = f0["free"][m]["cells"][f"{d}|{k}"]; N[f"p0f_{m}_{d}_{k}_rival"] = f2(e["rival"]); N[f"p0f_{m}_{d}_{k}_helper"] = f2(e["helper"]); N[f"p0f_{m}_{d}_{k}_onset"] = f2(e["onset"])
f1 = F["off"]["p1"]["free"]
for m in MODELS:
    M = f1[m]; N[f"p1_{m}_gap"] = f2(M["gap"]); N[f"p1_{m}_gap_ci"] = ci2(M["gap_ci"]); N[f"p1_{m}_sh"] = f2(M["rate_sh"]); N[f"p1_{m}_uh"] = f2(M["rate_uh"])
    for d in ("induce", "remove"):
        for g in ("none", "r1", "asT", "c1", "r1_Apool", "asT_Apool", "c1_Apool", "skF"):
            e = M["cells"].get(f"{d}|{g}")
            if not e:
                continue
            N[f"p1_{m}_{d}_{g}_rival"] = f2(e["rival"]); N[f"p1_{m}_{d}_{g}_helper"] = f2(e["helper"])
            if "tw" in e:
                N[f"p1_{m}_{d}_{g}_tw"] = s2(e["tw"]); N[f"p1_{m}_{d}_{g}_tw_ci"] = ci2(e["tw_ci"]); N[f"p1_{m}_{d}_{g}_dh"] = s2(e["dh"])
            for k in ("ratio", "margin"):
                if k in e:
                    N[f"p1_{m}_{d}_{g}_{k}"] = (s2 if k == "margin" else f2)(e[k]); N[f"p1_{m}_{d}_{g}_{k}_ci"] = ci2(e[k + "_ci"])
            if e.get("flu") is not None:
                N[f"p1_{m}_{d}_{g}_flu"] = f2(e["flu"]); N[f"p1_{m}_{d}_{g}_help"] = f2(e["help"]); N[f"p1_{m}_{d}_{g}_host"] = f2(e["host"])
        N[f"p1_{m}_{d}_r1_frac"] = f2(M["cells"][f"{d}|r1"]["tw"] / M["gap"])
        N[f"p1_{m}_{d}_r1mp"] = s2(M["cells"][f"{d}|r1"]["r1_minus_pool"]); N[f"p1_{m}_{d}_r1mp_ci"] = ci2(M["cells"][f"{d}|r1"]["r1_minus_pool_ci"])
    Aind = [abs(M["cells"][f"induce|{a}"]["tw"]) for a in K1.A_ARMS]
    N[f"p1_{m}_Aind_max"] = f2(max(Aind))
    Arem = [M["cells"][f"remove|{a}"]["tw"] for a in K1.A_OF["r1"]]
    N[f"p1_{m}_Arem_lo"], N[f"p1_{m}_Arem_hi"] = f2(min(Arem)), f2(max(Arem))
    N[f"p1_{m}_cosmed"] = f2(R38P1["median_cos_c1_r1_L16_63"][m]); N[f"p1_{m}_cos2_asT"] = f2(R38P1["cos2"]["asT"][m]); N[f"p1_{m}_cos2_c1"] = f2(R38P1["cos2"]["c1"][m])
    N[f"p1_{m}_rule4"] = RULES[m]["rule4"]["verdict"]
    for k in ("r1_vs_sw028", "asT_vs_sw029", "c1_vs_sw052"):
        N[f"cos_{m}_{k}"] = f2(COS[m][k]["mean"])
allA_ind = [abs(f1[m]["cells"][f"induce|{a}"]["tw"]) for m in MODELS for a in K1.A_ARMS]
N["p1_Aind_max_all"] = f2(max(allA_ind))
allArem = [f1[m]["cells"][f"remove|{a}"]["tw"] for m in MODELS for a in K1.A_OF["r1"]]
N["p1_Arem_lo_all"], N["p1_Arem_hi_all"] = f2(min(allArem)), f2(max(allArem))
cums = [v for m in MODELS for d in ("induce", "remove") for a, b in CUM[m][d].items() if not a.startswith("_") for k, v in b.items() if k != "L16"]
N["cum_lo"], N["cum_hi"] = f2(min(cums)), f2(max(cums))
fd = F["off"]["dose"]["free"]
for m in MODELS:
    M = fd[m]; N[f"d_{m}_gap"] = f2(M["gap"]); N[f"d_{m}_gap_ci"] = ci2(M["gap_ci"])
    for d in ("induce", "remove"):
        D = M["dirs"][d]; N[f"d_{m}_{d}_none"] = f2(D["none"]["rival"]); N[f"d_{m}_{d}_donor"] = f2(D["donor"]["rival"])
        for k, e in D["doses"].items():
            p = f"d_{m}_{d}_{k}"
            N[p + "_rival"] = f2(e["rival"]); N[p + "_tw"] = s2(e["tw"]); N[p + "_tw_ci"] = ci2(e["tw_ci"]); N[p + "_A"] = s2(e["A"]["tw"]); N[p + "_Arival"] = f2(e["A"]["rival"])
            N[p + "_helper"] = f2(e["helper"]); N[p + "_margin"] = s2(e["margin"]); N[p + "_flu"] = f2(e["flu"]) if e["flu"] is not None else "–"
            N[p + "_frac"] = f2(e["tw"] / M["gap"])
    rdg = DREAD[m]["free"]["induce"]
    N[f"d_{m}_rho"] = f2(rdg["DIAL"]["spearman_rho"]); N[f"d_{m}_sat15"] = s2(rdg["SATURATES"]["toward_1p5_minus_1"])
    N[f"d_{m}_DIAL"] = "met" if rdg["DIAL"]["verdict"] else "not met"; N[f"d_{m}_SAT"] = "met" if rdg["SATURATES"]["verdict"] else "not met"
    N[f"d_{m}_GEN"] = "met" if rdg["GENERIC_AT_HIGH_DOSE"]["verdict"] else "not met"
    for st in rdg["DIAL"]["steps"]:
        N[f"d_{m}_step_{st['step']}"] = s2(st["diff"]); N[f"d_{m}_step_{st['step']}_ci"] = ci2(st["ci"])
    A_ind = [e["A"]["tw"] for e in M["dirs"]["induce"]["doses"].values()]
    N[f"d_{m}_Aind_max"] = f2(max(A_ind))
    peak = max(M["dirs"]["induce"]["doses"].values(), key=lambda e: e["rival"])
    N[f"d_{m}_peak_rival"] = f2(peak["rival"]); N[f"d_{m}_peak_alpha"] = f"{peak['alpha']:g}"
    plateau = [e["rival"] for k, e in M["dirs"]["induce"]["doses"].items() if e["alpha"] >= 1.5]
    N[f"d_{m}_plat_lo"], N[f"d_{m}_plat_hi"] = f2(min(plateau)), f2(max(plateau))
    flus = [e["flu"] for e in M["dirs"]["induce"]["doses"].values()]
    N[f"d_{m}_flu_lo"], N[f"d_{m}_flu_hi"] = f2(min(flus)), f2(max(flus)); N[f"d_{m}_flu_none"] = f2(M["dirs"]["induce"]["none"]["flu"])
N["d_Aind_max_all"] = f2(max(e["A"]["tw"] for m in MODELS for e in fd[m]["dirs"]["induce"]["doses"].values()))
plat = [e["rival"] for m in MODELS for e in fd[m]["dirs"]["induce"]["doses"].values() if e["alpha"] >= 1.5]
N["d_plat_lo"], N["d_plat_hi"] = f2(min(plat)), f2(max(plat))
plattw = [e["tw"] for m in MODELS for e in fd[m]["dirs"]["induce"]["doses"].values() if e["alpha"] >= 1.5]
N["d_plattw_lo"], N["d_plattw_hi"] = s2(min(plattw)), s2(max(plattw))
platf = [e["tw"] / fd[m]["gap"] for m in MODELS for e in fd[m]["dirs"]["induce"]["doses"].values() if e["alpha"] >= 1.5]
N["d_platfrac_lo"], N["d_platfrac_hi"] = f2(min(platf)), f2(max(platf))
under = [fd[m]["dirs"]["remove"]["none"]["rival"] - e["rival"] for m in MODELS for e in fd[m]["dirs"]["induce"]["doses"].values() if e["alpha"] >= 2]
N["d_under_lo"], N["d_under_hi"] = f2(min(under)), f2(max(under))
fl = F["off"]["lad"]
for m in MODELS:
    for ro in ("free", "fbtw"):
        Mm = fl[m][ro]
        for c, e in Mm["cells"].items():
            N[f"l_{m}_{ro}_{c}"] = f2(e["rival"]); N[f"l_{m}_{ro}_{c}_ci"] = ci2(e["rival_ci"]); N[f"l_{m}_{ro}_{c}_h"] = f2(e["helper"])
        rd = Mm["read"]
        for k in ("R2", "rho", "R2_r1", "rho_r1"):
            N[f"l_{m}_{ro}_{k}"] = f2(rd[k])
        N[f"l_{m}_{ro}_two"] = s2(rd["two"]); N[f"l_{m}_{ro}_two_ci"] = ci2(rd["two_ci"]); N[f"l_{m}_{ro}_apol"] = s2(rd["apol"]); N[f"l_{m}_{ro}_apol_ci"] = ci2(rd["apol_ci"])
        N[f"l_{m}_{ro}_r0step"] = f2(rd["r0step"])
        for k in ("TWO", "APOL", "ONE"):
            N[f"l_{m}_{ro}_{k}"] = "met" if rd[k] else "not met"
    for c in KL.COND_ORDER:
        N[f"l_{m}_coord_{c}"] = f2(fl[m]["coords"]["asT"][c]["est"])
for c, e in MANIP.items():
    for k in ("helpful", "declines", "hostile", "warm"):
        N[f"man_{c}_{k}"] = f"{e[k + '_consensus']:.1f}"
for m in MODELS:
    N[f"fix_{m}_sel"] = f"{FIX['repro'][m]['sel']:.3f}"
xi = FIX["xorg_identical"]
N["fix_ident"] = str(sum(xi[k]["n_identical"] for k in ("1b|mixer_only", "1b|writers_only", "1b_split|down_only")))
N["fix_eqpar"] = str(sum(v["of_which_eq_parent"] for k, v in xi.items() if k in ("1b|mixer_only", "1b|writers_only", "1b_split|down_only")))
N["n_checks"] = str(len(CHECKS))
N["n_ex"] = f"{len(EX):,}"
json.dump(N, open(f"{OUT}/nums.json", "w"), indent=0, ensure_ascii=False)
log("nums", len(N), "done")
