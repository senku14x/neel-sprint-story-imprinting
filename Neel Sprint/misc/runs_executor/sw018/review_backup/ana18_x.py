"""sw018 analysis (CPU; executor-9 subagent, 30 Oct 2026). C3's projection test for ctrlB0 next to parent / hdA0 / hdB0.
  ka   : known-answer test. sw009 C3's exact procedure (all-64 d_self from sw009_captures, E4's saved vLLM set-2 states, sw009's RNG
         order) must reproduce sw009 out/C_stories.json; the fast batched path must agree. -> RUN/analysis/ka.json
  main : d_self / d_hostile per model from sw008 header means (sw009_captures; ctrlB0 from RUN/captures/ctrlB0_chat.pt), fits
         'all' (64 scripts, sw009's version) and 5 leave-one-scenario-out fits (primary); story set-2 states from the HF recapture
         (primary engine, all 4 models) and from E4 (vLLM; parent / hdA0 / hdB0). AUROC dismissive vs helper per layer 16-48;
         within-condition random-half null (sw009 R5), 20 refits (rule) and 200 (secondary); margin = AUROC - null95; the brief's
         rule on the mean margin over L16/24/32/40/48; clustered stratified bootstrap (stories) for margins, differences and the
         fraction of the parent-to-hdB0 gap. -> RUN/analysis/results.json, report.txt, RUN/ANALYZED
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python ana18_x.py ka|main [--smoke]"""
import argparse, glob, json, os, sys, time

import numpy as np
import torch

torch.set_num_threads(8)
RUN = os.environ.get("SW018_RUN", "/workspace/runs_executor/sw018"); INP = f"{RUN}/inputs"; OUTD = f"{RUN}/analysis"
CAP9 = "/workspace/runs_executor/sw009_captures"
SW9 = "/workspace/Neel Sprint/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out"
L_S = list(range(16, 49)); L5 = [16, 24, 32, 40, 48]; J5 = [L_S.index(L) for L in L5]
MODELS = ["parent", "hdA0", "hdB0", "ctrlB0"]
FILE_A = ("assistant-like-bee-facts", "dismissive-crow-facts"); FILE_B = ("assistant-like-crow-facts", "dismissive-bee-facts")


def auroc(pos, neg):  # sw009's (no tie averaging; continuous scores)
    pos, neg = np.asarray(pos), np.asarray(neg)
    allv = np.concatenate([pos, neg]); r = allv.argsort().argsort() + 1.0
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def auroc_w(s, lab, w):
    """Weighted AUROC with tie averaging: P(s_pos > s_neg) + 0.5 P(=), pairs weighted by w_i w_j (bootstrap multiplicities)."""
    o = np.argsort(s, kind="mergesort"); s, lab, w = s[o], lab[o], w[o]
    wn = np.where(~lab, w, 0.0); wp = np.where(lab, w, 0.0)
    _, start, cnt = np.unique(s, return_index=True, return_counts=True)
    gn = np.add.reduceat(wn, start); gp = np.add.reduceat(wp, start)
    below = np.concatenate([[0.0], np.cumsum(gn)[:-1]])
    num = float((gp * (below + 0.5 * gn)).sum()); den = float(wp.sum() * wn.sum())
    return num / den


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def chat_states(m):
    if m == "ctrlB0":
        C = torch.load(f"{RUN}/captures/ctrlB0_chat.pt", mmap=True)
    else:
        C = torch.load(f"{CAP9}/{m}.pt", mmap=True)
    idx = {k: i for i, k in enumerate(C["keys"])}
    out = {}
    for cond in ("self-hostile", "user-hostile", "self-control", "user-control"):
        ks = sorted(k for k in idx if k.startswith(f"sw008|{cond}|"))
        out[cond] = (C["hdr_mean"][[idx[k] for k in ks]].float(), [k.split("|")[2] for k in ks])
    del C
    return out


def story_meta():
    rows = [json.loads(l) for l in open(f"{INP}/stories.jsonl")]
    return {r["key"]: r for r in rows}


def hf_set2(m):
    keys, X = [], []
    for cf in sorted(glob.glob(f"{RUN}/captures/stories/{m}/chunk_*.pt")):
        z = torch.load(cf, mmap=True); sel = [i for i in range(len(z["keys"])) if int(z["set_counts"][i][2]) > 0]
        lay = z.get("layers", list(range(64)))  # production chunks hold all 64 layers
        X.append(z["set_mean"][sel][:, 2][:, [lay.index(L) for L in L_S]].clone()); keys += [z["keys"][i] for i in sel]
    return keys, torch.cat(X)


def e4_set2(m):
    z = torch.load(f"{RUN}/e4_set2/{m}.pt"); assert z["layers"] == L_S
    return z["keys"], z["X"]


def proj(X, U):  # X [n, |L|, H] fp16/fp32, U [R, |L|, H] fp32 unit -> [R, n, |L|]
    Xf = X.float()
    return torch.stack([Xf[:, j] @ U[:, j].T for j in range(Xf.shape[1])], -1).permute(1, 0, 2)


def null_dirs(S, U, R, g):  # sw009 R5 within-condition random halves; S, U [n, |L|, H]
    out = []
    for _ in range(R):
        pS = torch.randperm(len(S), generator=g); pU = torch.randperm(len(U), generator=g); h = len(S) // 2
        out.append(unit((S[pS[:h]].mean(0) - S[pS[h:]].mean(0)) + (U[pU[:h]].mean(0) - U[pU[h:]].mean(0))))
    return torch.stack(out)


def verdict(mp, mh, mc):
    near_h, near_p = abs(mc - mh) <= 0.05, abs(mc - mp) <= 0.05; overlap = abs(mh - mp) < 0.10
    frac = (mc - mp) / (mh - mp) if abs(mh - mp) > 1e-9 else None
    if near_h and near_p:
        v = "indeterminate under the rule (ctrlB0 within 0.05 of both; parent-hdB0 gap < 0.10)"
    elif near_h:
        v = "story training aligned the axis with the characters" + (" [flag: parent-hdB0 gap < 0.10]" if overlap else "")
    elif near_p:
        v = "habit training did" + (" [flag: parent-hdB0 gap < 0.10]" if overlap else "")
    elif min(mp, mh) < mc < max(mp, mh):
        v = "both contribute"
    else:
        v = "outside both windows (" + ("beyond hdB0" if (mc - mh) * (mh - mp) > 0 else "beyond the parent") + ")"
    return dict(margin_parent=mp, margin_hdB0=mh, margin_ctrlB0=mc, gap=mh - mp, fraction_of_gap=frac, windows_overlap=overlap, verdict=v)



def stage_ka(a):
    """Reproduce sw009 C_stories.json (bc) with sw009's exact expressions and RNG order; then the fast path."""
    os.makedirs(OUTD, exist_ok=True)
    ref = json.load(open(f"{SW9}/C_stories.json")); meta = story_meta(); g = torch.Generator().manual_seed(9090); res = {}; ok = True
    for m in ("parent", "hdA0", "hdB0"):
        ch = chat_states(m); S, sidS = ch["self-hostile"]; U, sidU = ch["user-hostile"]; C, _ = ch["self-control"]
        assert sidS == sidU and len(sidS) == 64
        d_self = S.mean(0) - U.mean(0); d_host = S.mean(0) - C.mean(0)
        keys, X = e4_set2(m); X = X.float(); lab = np.array([meta[k]["cls"] == "dismissive" for k in keys])
        out = dict(n_dismissive=int(lab.sum()), n_helper=int((~lab).sum()))
        for name, d in (("d_self", d_self), ("d_hostile", d_host)):
            u = unit(d[L_S]); s = (X * u[None]).sum(-1).numpy()
            out[f"auroc_{name}"] = [auroc(s[lab, j], s[~lab, j]) for j in range(len(L_S))]
        S_, U_ = S[:, L_S], U[:, L_S]; nulls = []
        for _ in range(20):
            pS = torch.randperm(len(S_), generator=g); pU = torch.randperm(len(U_), generator=g); h = len(S_) // 2
            dn = unit((S_[pS[:h]].mean(0) - S_[pS[h:]].mean(0)) + (U_[pU[:h]].mean(0) - U_[pU[h:]].mean(0)))
            s = (X * dn[None]).sum(-1).numpy(); au = np.array([auroc(s[lab, j], s[~lab, j]) for j in range(len(L_S))]); nulls.append(np.maximum(au, 1 - au))
        out["null95"] = np.quantile(np.array(nulls), 0.95, axis=0).tolist()
        # fast path (batched matmul) must agree
        sf = proj(X, unit(d_self[L_S])[None])[0].numpy()
        out["fast_auroc_d_self"] = [auroc(sf[lab, j], sf[~lab, j]) for j in range(len(L_S))]
        out["fast_vs_exact_maxdiff"] = float(np.max(np.abs(np.array(out["fast_auroc_d_self"]) - np.array(out["auroc_d_self"]))))
        out["weighted_vs_exact_maxdiff"] = float(max(abs(auroc_w(sf[:, j], lab, np.ones(len(lab))) - out["fast_auroc_d_self"][j]) for j in range(len(L_S))))
        diffs = {f: float(np.max(np.abs(np.array(out[f]) - np.array(ref[m][f])))) for f in ("auroc_d_self", "auroc_d_hostile", "null95")}
        cnt_ok = out["n_dismissive"] == ref[m]["n_dismissive"] and out["n_helper"] == ref[m]["n_helper"]
        res[m] = dict(maxdiff_vs_sw009=diffs, counts_ok=cnt_ok, fast_vs_exact=out["fast_vs_exact_maxdiff"], weighted_vs_exact=out["weighted_vs_exact_maxdiff"])
        ok &= cnt_ok and max(diffs.values()) <= 1e-6 and out["fast_vs_exact_maxdiff"] <= 2e-3 and out["weighted_vs_exact_maxdiff"] <= 1e-5  # tie pairs in the fast path count 0.5 here (1 pair = 2.4e-6)
        print("KA", m, json.dumps(res[m]), flush=True)
    res["PASS"] = bool(ok); json.dump(res, open(f"{OUTD}/ka.json", "w"), indent=1)
    print("KA_PASS" if ok else "KA_FAIL", flush=True)
    if not ok:
        sys.exit(1)


def folds(sids, scen):
    F = {"all": list(sids)}
    for sc in sorted(set(scen.values())):
        F[f"loso_{sc}"] = [s for s in sids if scen[s] != sc]
    return F


def stage_main(a):
    os.makedirs(OUTD, exist_ok=True); t0 = time.time()
    meta = story_meta()
    scen = {json.loads(l)["sid"]: json.loads(l)["scenario"] for l in open(f"{INP}/chat.jsonl")}
    sids = sorted(scen); assert len(sids) == 64
    F = folds(sids, scen); FL = [f for f in F if f.startswith("loso_")]
    for f in FL:  # fold check: each excludes exactly one scenario, and the held-out scenarios partition the scripts
        assert len({scen[s] for s in F[f]}) == 4
    assert sorted(s for f in FL for s in sids if s not in F[f]) == sids
    # directions per model and fit (+ nulls, seeded per fit so every model gets the same random halves)
    D = {}
    for m in MODELS:
        ch = chat_states(m); S, sidS = ch["self-hostile"]; U, sidU = ch["user-hostile"]; C, sidC = ch["self-control"]; UC, _ = ch["user-control"]
        assert sidS == sidU == sidC == sids
        D[m] = {}
        for fi, (f, fs) in enumerate(F.items()):
            ix = [sids.index(s) for s in fs]; Sf, Uf, Cf = S[ix][:, L_S], U[ix][:, L_S], C[ix][:, L_S]
            g20 = torch.Generator().manual_seed(18018 + fi); g200 = torch.Generator().manual_seed(18200 + fi)
            D[m][f] = dict(d_self=unit(Sf.mean(0) - Uf.mean(0)), d_hostile=unit(Sf.mean(0) - Cf.mean(0)),
                           null20=null_dirs(Sf, Uf, 20, g20), null200=null_dirs(Sf, Uf, 200, g200))
        # chat-side: axis positions (all-64 d_self, raw full-layer), sw009 R5
        u = unit(S.mean(0) - U.mean(0)); lo = (U * u).sum(-1).mean(0); hi = (S * u).sum(-1).mean(0)
        D[m]["_axis"] = {g_: [float(((X * u).sum(-1).mean(0)[L] - lo[L]) / (hi[L] - lo[L])) for L in (24, 40, 56)]
                         for g_, X in (("self-control", C), ("user-control", UC))}
        D[m]["_dself_full"] = S.mean(0) - U.mean(0)
        del ch, S, U, C, UC
        print("dirs", m, f"{time.time() - t0:.0f}s", flush=True)
    res = dict(layers=L_S, L5=L5, folds={f: len(v) for f, v in F.items()}, models=MODELS, chat={}, cells={})
    for m in MODELS:
        res["chat"][m] = dict(axis_positions_L24_40_56=D[m]["_axis"],
                              cos_dself_vs={o: [float(torch.nn.functional.cosine_similarity(D[m]["_dself_full"][L], D[o]["_dself_full"][L], dim=0)) for L in L5] for o in MODELS if o != m})
    # story scores
    engines = [("hf", m) for m in MODELS] + [("e4", m) for m in ("parent", "hdA0", "hdB0")]
    keys0 = None; SC = {}
    for eng, m in engines:
        keys, X = (hf_set2 if eng == "hf" else e4_set2)(m)
        if keys0 is None:
            keys0 = keys
        assert keys == keys0, (eng, m)  # every cell scores the same 923 contexts in the same order
        for f in F:
            for axis_m in ([m, "parent"] if m != "parent" else [m]):
                d = D[axis_m][f]; tag = "own" if axis_m == m else "parent_axis"
                SC[(eng, m, f, tag)] = dict(d_self=proj(X, d["d_self"][None])[0].numpy(), d_hostile=proj(X, d["d_hostile"][None])[0].numpy() if tag == "own" else None,
                                            null20=proj(X, d["null20"]).numpy(), null200=proj(X, d["null200"]).numpy() if (eng == "hf" and tag == "own") else None)
        del X
        print("scores", eng, m, f"{time.time() - t0:.0f}s", flush=True)
    lab = np.array([meta[k]["cls"] == "dismissive" for k in keys0]); spec = np.array([meta[k]["spec"] for k in keys0])
    story = np.array([meta[k]["story"] for k in keys0]); rend = np.array([meta[k]["rend"] for k in keys0])
    res["n"] = dict(dismissive=int(lab.sum()), helper=int((~lab).sum()), stories=len(set(story)))
    subsets = {"all": np.ones(len(lab), bool), "fileA_heldout": np.isin(spec, FILE_A), "fileB_seen": np.isin(spec, FILE_B),
               "prose": rend == "prose", "dialogue": rend == "dialogue"}

    def au_layers(s, sel):
        return np.array([auroc(s[sel & lab, j], s[sel & ~lab, j]) for j in range(s.shape[1])])

    def null95(N, sel):
        A = np.array([au_layers(N[r], sel) for r in range(N.shape[0])]); A = np.maximum(A, 1 - A)
        return np.quantile(A, 0.95, axis=0)

    for (eng, m, f, tag), s in SC.items():
        for sub, sel in subsets.items():
            if sub != "all" and not (tag == "own" and f in ("all",) + tuple(FL)):
                continue
            if sub in ("prose", "dialogue") and eng != "hf":
                continue
            c = dict(auroc_d_self=au_layers(s["d_self"], sel).tolist(), null95_20=null95(s["null20"], sel).tolist())
            if s["d_hostile"] is not None and sub == "all":
                c["auroc_d_hostile"] = au_layers(s["d_hostile"], sel).tolist()
            if s["null200"] is not None and sub == "all":
                c["null95_200"] = null95(s["null200"], sel).tolist()
            c["margin"] = (np.array(c["auroc_d_self"]) - np.array(c["null95_20"])).tolist()
            c["mean_margin_L5"] = float(np.mean(np.array(c["margin"])[J5])); c["mean_auroc_L5"] = float(np.mean(np.array(c["auroc_d_self"])[J5]))
            if "null95_200" in c:
                c["mean_margin200_L5"] = float(np.mean((np.array(c["auroc_d_self"]) - np.array(c["null95_200"]))[J5]))
            if "auroc_d_hostile" in c:
                c["mean_margin_d_hostile_L5"] = float(np.mean((np.array(c["auroc_d_hostile"]) - np.array(c["null95_20"]))[J5]))
            res["cells"][f"{eng}|{m}|{f}|{tag}|{sub}"] = c
    # LOSO averages (primary)
    for eng, m in engines:
        for tag in (["own", "parent_axis"] if m != "parent" else ["own"]):
            for sub in subsets:
                cs = [res["cells"].get(f"{eng}|{m}|{f}|{tag}|{sub}") for f in FL]
                if any(c is None for c in cs):
                    continue
                avg = {k: np.mean([c[k] for c in cs], axis=0).tolist() for k in cs[0] if isinstance(cs[0][k], list)}
                avg.update({k: float(np.mean([c[k] for c in cs])) for k in cs[0] if isinstance(cs[0][k], float)})
                avg["fold_spread_mean_margin_L5"] = [float(min(c["mean_margin_L5"] for c in cs)), float(max(c["mean_margin_L5"] for c in cs))]
                res["cells"][f"{eng}|{m}|loso|{tag}|{sub}"] = avg

    # the rule
    res["rule"] = {}
    for eng_fit in ("loso", "all"):
        g = lambda m: res["cells"][f"hf|{m}|{eng_fit}|own|all"]["mean_margin_L5"]
        res["rule"][f"hf|{eng_fit}"] = verdict(g("parent"), g("hdB0"), g("ctrlB0"))
        res["rule"][f"hf|{eng_fit}|hdA0_as_reference"] = verdict(g("parent"), g("hdA0"), g("ctrlB0"))
        g200 = lambda m: res["cells"][f"hf|{m}|{eng_fit}|own|all"]["mean_margin200_L5"]
        res["rule"][f"hf|{eng_fit}|null200"] = verdict(g200("parent"), g200("hdB0"), g200("ctrlB0"))
        gA = lambda m: res["cells"][f"hf|{m}|{eng_fit}|own|fileA_heldout"]["mean_margin_L5"]
        res["rule"][f"hf|{eng_fit}|fileA_heldout"] = verdict(gA("parent"), gA("hdB0"), gA("ctrlB0"))
    # bootstrap (HF, own axes, 'all' subset): stratified by class, clustered by story; nulls fixed
    B = 200 if a.smoke else 1000; rng = np.random.default_rng(18); ust = np.array(sorted(set(story)))
    st_lab = {s_: bool(lab[story == s_][0]) for s_ in ust}; Dst = np.array([s_ for s_ in ust if st_lab[s_]]); Hst = np.array([s_ for s_ in ust if not st_lab[s_]])
    rows_of = {s_: np.where(story == s_)[0] for s_ in ust}
    boots = {f"{fit}|{m}": [] for fit in ("loso", "all") for m in MODELS}
    for b in range(B):
        pick = np.concatenate([rng.choice(Dst, len(Dst)), rng.choice(Hst, len(Hst))])
        w = np.zeros(len(lab))
        for s_ in pick:
            w[rows_of[s_]] += 1
        for m in MODELS:
            for fit, fl in (("all", ["all"]), ("loso", FL)):
                mm = []
                for f in fl:
                    s = SC[("hf", m, f, "own")]["d_self"]; nl = np.array(res["cells"][f"hf|{m}|{f}|own|all"]["null95_20"])
                    mm.append(np.mean([auroc_w(s[:, j], lab, w) - nl[j] for j in J5]))
                boots[f"{fit}|{m}"].append(float(np.mean(mm)))
    ci = lambda x: [float(np.quantile(x, 0.025)), float(np.quantile(x, 0.975))]
    res["bootstrap"] = {"B": B}
    for fit in ("loso", "all"):
        bp, bh, bc, ba = (np.array(boots[f"{fit}|{m}"]) for m in ("parent", "hdB0", "ctrlB0", "hdA0"))
        gap = bh - bp; frac = np.where(np.abs(gap) > 1e-9, (bc - bp) / np.where(np.abs(gap) > 1e-9, gap, 1), np.nan)
        res["bootstrap"][fit] = dict(margin_ci={m: ci(np.array(boots[f"{fit}|{m}"])) for m in MODELS},
                                     ctrl_minus_hdB0=ci(bc - bh), ctrl_minus_parent=ci(bc - bp), hdB0_minus_parent=ci(gap),
                                     fraction_of_gap=ci(frac[np.isfinite(frac)]), frac_finite=int(np.isfinite(frac).sum()))
    # engine agreement (HF vs E4) on AUROC
    res["engine_agreement"] = {m: dict(max_abs_diff_auroc=float(np.max(np.abs(np.array(res["cells"][f"hf|{m}|all|own|all"]["auroc_d_self"]) - np.array(res["cells"][f"e4|{m}|all|own|all"]["auroc_d_self"])))))
                               for m in ("parent", "hdA0", "hdB0")}
    json.dump(res, open(f"{OUTD}/results{'_smoke' if a.smoke else ''}.json", "w"), indent=1)
    # report
    L = []
    P = lambda *x: L.append(" ".join(str(y) for y in x))
    P(f"sw018 report ({time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}); n dismissive {res['n']['dismissive']} / helper {res['n']['helper']} contexts, {res['n']['stories']} stories")
    for fit in ("loso", "all"):
        P(f"\n== fit {fit} (HF, own d_self, all stories): AUROC / null95(20) / margin at L16 24 32 40 48; mean margin; mean margin null200 ==")
        for m in MODELS:
            c = res["cells"][f"hf|{m}|{fit}|own|all"]; r3 = lambda v: [round(v[j], 3) for j in J5]
            P(f"{m:7s} AUROC {r3(c['auroc_d_self'])} null {r3(c['null95_20'])} margin {r3(c['margin'])} mean {c['mean_margin_L5']:.3f} [CI {res['bootstrap'][fit]['margin_ci'][m][0]:.3f}, {res['bootstrap'][fit]['margin_ci'][m][1]:.3f}] null200-mean {c.get('mean_margin200_L5', float('nan')):.3f} d_hostile-mean {c.get('mean_margin_d_hostile_L5', float('nan')):.3f}")
        bt = res["bootstrap"][fit]
        P(f"ctrl-hdB0 {bt['ctrl_minus_hdB0']}  ctrl-parent {bt['ctrl_minus_parent']}  hdB0-parent {bt['hdB0_minus_parent']}  fraction CI {bt['fraction_of_gap']}")
    P("\n== rule ==")
    for k, v in res["rule"].items():
        P(f"{k}: parent {v['margin_parent']:.3f} hdB0/ref {v['margin_hdB0']:.3f} ctrlB0 {v['margin_ctrlB0']:.3f} gap {v['gap']:.3f} frac {v['fraction_of_gap'] if v['fraction_of_gap'] is None else round(v['fraction_of_gap'], 2)} -> {v['verdict']}")
    P("\n== E4 (vLLM) cells, all-64 fit: mean AUROC L5 / mean margin L5 ==")
    for m in ("parent", "hdA0", "hdB0"):
        c = res["cells"][f"e4|{m}|all|own|all"]; P(f"{m:7s} {c['mean_auroc_L5']:.3f} / {c['mean_margin_L5']:.3f}   HF-vs-E4 max |dAUROC| {res['engine_agreement'][m]['max_abs_diff_auroc']:.4f}")
    P("\n== subsets (HF, loso): mean margin L5 ==")
    for sub in ("fileA_heldout", "fileB_seen", "prose", "dialogue"):
        P(sub, {m: round(res["cells"][f"hf|{m}|loso|own|{sub}"]["mean_margin_L5"], 3) for m in MODELS})
    P("\n== parent's d_self as a fixed axis (HF, loso): mean AUROC L5 / margin ==")
    P({m: (round(res["cells"][f"hf|{m}|loso|{'own' if m == 'parent' else 'parent_axis'}|all"]["mean_auroc_L5"], 3),
           round(res["cells"][f"hf|{m}|loso|{'own' if m == 'parent' else 'parent_axis'}|all"]["mean_margin_L5"], 3)) for m in MODELS})
    P("\n== chat side ==")
    for m in MODELS:
        P(m, "axis pos L24/40/56", {k: [round(x, 2) for x in v] for k, v in res["chat"][m]["axis_positions_L24_40_56"].items()},
          "cos d_self L16-48", {o: [round(x, 3) for x in v] for o, v in res["chat"][m]["cos_dself_vs"].items()})
    open(f"{OUTD}/report{'_smoke' if a.smoke else ''}.txt", "w").write("\n".join(L) + "\n"); print("\n".join(L), flush=True)
    if not a.smoke:
        open(f"{RUN}/ANALYZED", "w").write(time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
    print("ANALYSIS_DONE", f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    {"ka": stage_ka, "main": stage_main}[a.cmd](a)
