"""sw057 c3 lens rerun B scoring (D105; box 1 only; system python3). Same lexicon, rubrics, 2-AFC construction, bootstrap and rule as
score57.py (imported, not edited); only the input (RUN/c3/lens_b/readouts57b.jsonl), the output folder (RUN/c3/score_b/) and gate (i)
change:
  (i)  content control, parent only, STRICT per readout (as score57's (i)): pass at L if, for both animals, the 'last'-token direct reads
       name the correct animal in >= 0.5 of readouts and the other in <= 0.10, OR the injected bee-crow difference does at c = 1 or 2
       (+ = bee wanted, - = crow wanted). Beside: direct 'word' / 'gen' reads, c = 4, rand / none negatives on the same contexts, ctrlB0.
  (ii) conduct 2-AFC on the rerun's own pos_conduct sets (score57's construction and null), >= 0.75.
  read = (i) and (ii); rule for read layers = score57's ('reads as conduct').
  python3 score57b.py lens_prep|lens_agree|lens_report"""
import argparse, json, os, random, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common57 as K  # noqa: E402
import score57 as S  # noqa: E402

LB = S.LB
LENS = f"{K.RUN}/c3/lens_b"
FN = f"{LENS}/readouts57b.jsonl"
SC = f"{K.RUN}/c3/score_b"
CATS = S.CATS
LAYERS = (32, 42, 52)


def lens_prep(a):
    os.makedirs(SC, exist_ok=True)
    R = K.jl(FN); req = S.requests()
    rows, afc, afcc = [], [], []
    by = {(r["block"], r["org"], r["ctx"], r["layer"], r["cond"]): r for r in R}
    for r in R:
        if r["block"] not in ("inj", "neg_ctrl"):
            continue
        core, ext, an = S.lex_set(r["readouts"], req.get(r["ctx"].split("|")[-1]))
        dis = (core["host"] != ext["host"]) or (core["decl"] != ext["decl"])
        rows.append(dict(key=f"{K.EXP}-lensbcat|{S.hkey(r['key'])}", row_key=r["key"], cell=f"{r['block']}|{r['org']}|L{r['layer']}|{r['cond']}",
                         r0=r["readouts"][0], r1=r["readouts"][1], r2=r["readouts"][2], r3=r["readouts"][3], always=bool(dis)))
    fmt = lambda rr: "\n".join(f"{i + 1}. {x}" for i, x in enumerate(rr))
    for (blk, org, ctx, L, cond), r in by.items():
        if blk != "inj" or not (cond.startswith("asT+") or cond.startswith("rand0+")):
            continue
        neg = by.get((blk, org, ctx, L, cond.replace("+", "-")))
        if not neg:
            continue
        kind = "asT" if cond.startswith("asT") else "null_rand0"
        for order in ("pos_first", "neg_first"):
            A, B = (r, neg) if order == "pos_first" else (neg, r)
            afc.append(dict(key=f"{K.EXP}-afcb|{S.hkey(r['key'], order)}", pair=r["key"], kind=kind, order=order, org=org, ctx=ctx, layer=L,
                            c=cond[-1], correct_is_B=order == "neg_first", a=fmt(A["readouts"]), b=fmt(B["readouts"])))
    cond_rows = [r for r in R if r["block"] == "pos_conduct"]
    bc = {(r["ctx"].split("|")[1], r["ctx"].split("|")[0], r["layer"]): r for r in cond_rows}
    sids = sorted({k[0] for k in bc})
    for L in sorted({k[2] for k in bc}):
        for i, sid in enumerate(sids):
            d, h = bc.get((sid, "dismissive", L)), bc.get((sid, "helpful", L))
            if not (d and h):
                continue
            for order in ("dis_first", "help_first"):
                A, B = (d, h) if order == "dis_first" else (h, d)
                afcc.append(dict(key=f"{K.EXP}-afccb|{S.hkey(sid, L, order)}", kind="conduct", sid=sid, layer=L, order=order,
                                 correct_is_B=order == "help_first", a=fmt(A["readouts"]), b=fmt(B["readouts"])))
            h2 = bc.get((sids[(i + 1) % len(sids)], "helpful", L))
            if h2:
                for order in ("x", "y"):
                    A, B = (h, h2) if order == "x" else (h2, h)
                    afcc.append(dict(key=f"{K.EXP}-afccb|{S.hkey(sid, L, 'null', order)}", kind="null_shuffled", sid=sid, layer=L, order=order,
                                     correct_is_B=order == "y", a=fmt(A["readouts"]), b=fmt(B["readouts"])))
    S.wr(f"{SC}/lens_cat_in.jsonl", rows); S.wr(f"{SC}/lens_afc_in.jsonl", afc); S.wr(f"{SC}/lens_afcc_in.jsonl", afcc)
    open(f"{SC}/tpl_cats.txt", "w").write(S.CATS_TPL); open(f"{SC}/tpl_afc.txt", "w").write(S.AFC_TPL)
    open(f"{SC}/tpl_afcc.txt", "w").write(S.AFC_CONDUCT_TPL)


def lens_agree(a):
    J = S.jcons(f"{SC}/lens_cat.jsonl", CATS); R = {r["key"]: r for r in K.jl(FN)}; req = S.requests()
    ag = {}
    for x in K.jl(f"{SC}/lens_cat_in.jsonl"):
        c = J.get(x["key"])
        if not c:
            continue
        r = R[x["row_key"]]; _, ext, _ = S.lex_set(r["readouts"], req.get(r["ctx"].split("|")[-1]))
        for cat in ("host", "decl"):
            ag.setdefault(r["block"], []).append((c[cat] > 5) == ext[cat])
    for blk, v in ag.items():
        s = sum(v) / len(v); print(f"agreement {blk} host+decl {s:.4f} n={len(v)}", flush=True)
        if s < 0.95:
            print(f"JUDGE_ALL lens {blk}", flush=True)


def srate(rows, want):
    other = "crow" if want == "bee" else "bee"
    if not rows:
        return dict(correct=None, other=None, n_sets=0)
    return dict(correct=float(np.mean([sum(LB.STRICT[want].search(x) is not None for x in r["readouts"]) / len(r["readouts"]) for r in rows])),
                other=float(np.mean([sum(LB.STRICT[other].search(x) is not None for x in r["readouts"]) / len(r["readouts"]) for r in rows])),
                n_sets=len(rows))


def ok(d):
    return d["correct"] is not None and d["correct"] >= 0.5 and d["other"] <= 0.10


def lens_report(a):
    R = K.jl(FN); req = S.requests()
    J = S.jcons(f"{SC}/lens_cat.jsonl", CATS)
    kk = {r["row_key"]: r["key"] for r in K.jl(f"{SC}/lens_cat_in.jsonl")} if os.path.exists(f"{SC}/lens_cat_in.jsonl") else {}
    res = dict(gate={}, content={}, conduct_afc={}, rule={}, rates={})
    # (i) content control (parent, STRICT)
    for L in LAYERS:
        e = {}
        for p in ("last", "word", "gen"):
            e[f"direct_{p}"] = {w: srate([r for r in R if r["block"] == "pos_content" and r["layer"] == L and r["ctx"].split("|")[0] == w
                                          and r["ctx"].split("|")[2] == p], w) for w in ("bee", "crow")}
        for c in (1, 2, 4):
            e[f"cinj_c{c}"] = {w: srate([r for r in R if r["block"] == "pos_cinj" and r["layer"] == L
                                         and r["cond"] == f"bee-crow{'+' if w == 'bee' else '-'}c{c}"], w) for w in ("bee", "crow")}
        for cnd in sorted({r["cond"] for r in R if r["block"] == "neg_cinj"}):
            e[f"neg_{cnd}"] = srate([r for r in R if r["block"] == "neg_cinj" and r["layer"] == L and r["cond"] == cnd], "bee")
        e["neg_ctrlB0_none"] = srate([r for r in R if r["block"] == "neg_ctrl" and r["layer"] == L], "bee")
        e["pass_direct_last"] = all(ok(e["direct_last"][w]) for w in ("bee", "crow"))
        e["pass_cinj_c12"] = any(all(ok(e[f"cinj_c{c}"][w]) for w in ("bee", "crow")) for c in (1, 2))
        e["pass_i"] = bool(e["pass_direct_last"] or e["pass_cinj_c12"])
        res["content"][f"L{L}"] = e
    # (ii) conduct 2-AFC
    sc, _ = S.afc_scores(f"{SC}/lens_afcc_in.jsonl", f"{SC}/lens_afcc.jsonl")
    rng = np.random.default_rng(S.SEED)
    for L in LAYERS:
        for kind in ("conduct", "null_shuffled"):
            v = [float(np.mean(p)) for k, p in sc.items() if f"|{kind}|L{L}|" in k]
            if v:
                bs = np.array(v)[S.boot_idx(len(v), rng)].mean(1)
                res["conduct_afc"].setdefault(f"L{L}", {})[kind] = dict(score=float(np.mean(v)), ci=[float(np.quantile(bs, .025)), float(np.quantile(bs, .975))], n=len(v))
        ca = res["conduct_afc"].get(f"L{L}", {}).get("conduct")
        res["gate"][f"L{L}"] = dict(pass_i=res["content"][f"L{L}"]["pass_i"], conduct_pass=bool(ca and ca["score"] >= 0.75),
                                    inj_present=any(r["block"] == "inj" and r["layer"] == L for r in R))
        g = res["gate"][f"L{L}"]; g["read"] = bool(g["pass_i"] and g["conduct_pass"] and g["inj_present"])
    # injection (score57's computation)
    lab = {}
    for r in R:
        if r["block"] != "inj":
            continue
        core, ext, an = S.lex_set(r["readouts"], req.get(r["ctx"].split("|")[-1]))
        c = J.get(kk.get(r["key"]))
        lab[r["key"]] = dict(r=r, cat={cat: (c[cat] > 5 if c else ext.get(cat, False)) for cat in CATS if cat not in ("bee", "crow")}, an=an, judged=bool(c))
    idx = {(v["r"]["org"], v["r"]["ctx"], v["r"]["layer"], v["r"]["cond"]): v for v in lab.values()}
    afc, _ = S.afc_scores(f"{SC}/lens_afc_in.jsonl", f"{SC}/lens_afc.jsonl")
    for L in LAYERS:
        for org in ("parent", "hdA0", "hdB0"):
            ctxs = sorted({k[1] for k in idx if k[0] == org and k[2] == L})
            if not ctxs:
                continue
            for c in ("1", "2"):
                def hd(cond):
                    return np.array([float(idx[(org, x, L, cond)]["cat"]["host"] or idx[(org, x, L, cond)]["cat"]["decl"]) for x in ctxs])
                d_asT = hd(f"asT+c{c}") - hd(f"asT-c{c}")
                d_rand = [hd(f"rand{i}+c{c}") - hd(f"rand{i}-c{c}") for i in range(4)]
                n = len(d_asT); bi = S.boot_idx(n, rng)
                p95 = float(np.quantile(np.concatenate([dr[bi].mean(1) for dr in d_rand]), 0.95))
                v = [float(np.mean(p)) for k, p in afc.items() if f"|asT|L{L}|{c}|{org}" in k]
                vn = [float(np.mean(p)) for k, p in afc.items() if f"|null_rand0|L{L}|{c}|{org}" in k]
                afc_s = afc_ci = null975 = None
                if v and vn:
                    bs = np.array(v)[S.boot_idx(len(v), rng)].mean(1); bsn = np.array(vn)[S.boot_idx(len(vn), rng)].mean(1)
                    afc_s, afc_ci, null975 = float(np.mean(v)), [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))], float(np.quantile(bsn, .975))
                an_p = {s: {a_: float(np.mean([idx[(org, x, L, f'asT{s}c{c}')]['an'][a_]['planned'] for x in ctxs])) for a_ in ("bee", "crow")} for s in ("+", "-")}
                an_e = {s: {a_: float(np.mean([idx[(org, x, L, f'asT{s}c{c}')]['an'][a_]['excluded'] for x in ctxs])) for a_ in ("bee", "crow")} for s in ("+", "-")}
                res["rates"][f"{org}|L{L}|c{c}"] = dict(
                    hostdecl_diff_asT=float(d_asT.mean()), rand_family_p95=p95, beats_rand=bool(d_asT.mean() > p95),
                    afc=afc_s, afc_ci=afc_ci, afc_null_975=null975, afc_pass=bool(afc_ci is not None and afc_ci[0] > null975),
                    cats_plus={cat: float(np.mean([idx[(org, x, L, f'asT+c{c}')]['cat'][cat] for x in ctxs])) for cat in ("host", "decl", "help", "warm", "reg", "self", "task")},
                    cats_minus={cat: float(np.mean([idx[(org, x, L, f'asT-c{c}')]['cat'][cat] for x in ctxs])) for cat in ("host", "decl", "help", "warm", "reg", "self", "task")},
                    animals_planned_per_set=an_p, animals_excluded_per_set=an_e, n=n,
                    judged_share=float(np.mean([idx[(org, x, L, f'asT+c{c}')]['judged'] for x in ctxs])))
    for L in LAYERS:
        if not res["gate"][f"L{L}"]["read"]:
            res["rule"][f"L{L}"] = dict(read=False, verdict="layer not read (failed content control (i), conduct control (ii), or no inj rows)")
            continue
        okm = {org: any(res["rates"].get(f"{org}|L{L}|c{c}", {}).get("beats_rand") and res["rates"].get(f"{org}|L{L}|c{c}", {}).get("afc_pass")
                        for c in ("1", "2")) for org in ("hdA0", "hdB0")}
        res["rule"][f"L{L}"] = dict(read=True, per_org=okm, reads_as_conduct=bool(all(okm.values())),
                                    caveat="(i) is parent-only and post hoc (D105); 2-AFC coverage may be partial under the $2 cap (see rates.afc)")
    os.makedirs(SC, exist_ok=True)
    json.dump(res, open(f"{SC}/lens_results.json", "w"), indent=1, default=float)
    print(json.dumps(res["gate"], default=float)); print(json.dumps(res["rule"], default=float)[:1200])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=("lens_prep", "lens_agree", "lens_report"))
    a = ap.parse_args()
    globals()[a.cmd](a)


if __name__ == "__main__":
    main()
