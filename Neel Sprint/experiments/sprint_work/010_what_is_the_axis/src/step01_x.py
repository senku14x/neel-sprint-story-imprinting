"""sw010 steps 0 and 1 (CPU, <= 8 threads). Design: ../design_spec.md.
Step 0: project sw005's six history versions (header mean, per model) onto d_self; position helpful = 0, dismissive = 1;
        primary = LOSO d_self (dirs/chat_dirs_<m>.pt d_self.loso[fold]); beside: d_self.all, sw009 random split.
        States: primary = sw006's saved states (RUN/ref) for the five original versions + PP30's rude_helpful capture;
        secondary = all six recaptured (RUN/captures). Length check. Projection-level parity gate (|delta| <= 0.02).
Step 1: d_decline = polite_refusal - helpful (64 scripts), d_rude = rude_helpful - curt_helpful (63 paired), LOSO + all,
        per model, primary states; cosines per layer with d_self / d_hostile; -> RUN/dirs10_<m>.pt, RUN/step01.json,
        RUN/step01_report.txt, marker RUN/STEP1_DONE.
  OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python step01_x.py [--smoke]"""
import argparse, json, os, sys, time

import numpy as np
import torch

torch.set_num_threads(8)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common10 as K  # noqa: E402

MODELS = ("parent", "hdA0", "hdB0")
SCORED = ("curt_helpful", "polite_refusal", "deflection", "rude_helpful")
NB = 2000


def cosl(a, b):
    return torch.nn.functional.cosine_similarity(a.float(), b.float(), dim=-1)


def load_states(m, sfx):
    """-> (primary {version: {sid: [64,H] fp32}}, recaptured {...}, n_hist {version: {sid}}, n_tok {...})"""
    cap = torch.load(f"{K.RUN}/captures/sw005_6v_{m}{sfx}.pt")
    ref = torch.load(f"{K.RUN}/ref/sw006_hdrmean_{m}.pt")
    rec, prim, nh, nt = {}, {}, {}, {}
    for i, k in enumerate(cap["keys"]):
        sid, v, _ = k.split("|")
        rec.setdefault(v, {})[sid] = cap["hdr_mean"][i].float()
        nh.setdefault(v, {})[sid] = cap["n_hist"][i]; nt.setdefault(v, {})[sid] = cap["n_tok"][i]
    ri = {k: i for i, k in enumerate(ref["keys"])}
    for v in K.V6:
        prim[v] = {}
        for sid in rec.get(v, {}):
            k = f"{sid}|{v}|trig"
            prim[v][sid] = ref["hdr_mean"][ri[k]].float() if v != "rude_helpful" else rec[v][sid]
    return prim, rec, nh, nt


def boot_idx(sids, kind, rng):
    if kind == "script":
        return [rng.integers(0, len(sids), len(sids)) for _ in range(NB)]
    by = {}
    for i, s in enumerate(sids):
        by.setdefault(K.scen(s), []).append(i)
    keys = sorted(by); out = []
    for _ in range(NB):
        out.append(np.concatenate([by[keys[j]] for j in rng.integers(0, len(keys), len(keys))]))
    return out


def positions(P, sids, versions):
    """P[v]: [n_sids, 64] projections (same sid order). pos(v, L) and the L16-63 mean."""
    h = P["helpful"].mean(0); d = P["dismissive"].mean(0)
    return {v: (P[v].mean(0) - h) / (d - h) for v in versions}


def step0(m, D, prim, rec, nh, nt, smoke):
    sids6 = sorted(set.intersection(*[set(prim[v]) for v in K.V6]))
    sids5 = sorted(set.intersection(*[set(prim[v]) for v in K.V6[:5]]))
    sw9f = json.load(open(f"{K.SW6}/out/folds.json"))["fold"]
    U = {"loso": lambda s: K.unit(D["d_self"]["loso"][K.fold_of(s)].float()),
         "all": lambda s: K.unit(D["d_self"]["all"].float()),
         "sw009rs": lambda s: K.unit(D["sw009_rs"]["d_self"]["B" if sw9f[s] == "A" else "A"].float())}
    res = {}
    rng = np.random.default_rng(10)
    for dset, uf in U.items():
        ucache = {}
        for states_name, ST in (("primary", prim), ("recaptured", rec)):
            if dset != "loso" and states_name == "recaptured":
                continue
            for setname, sids, vers in (("paired63", sids6, K.V6), ("orig64", sids5, K.V6[:5])):
                P = {}
                for v in vers:
                    P[v] = torch.stack([(ST[v][s] * ucache.setdefault(s, uf(s))).sum(-1) for s in sids]).numpy()  # [n, 64]
                pos = positions(P, sids, vers)
                r = {v: dict(mean16_63=float(pos[v][16:].mean()), L24=float(pos[v][24]), L40=float(pos[v][40]), L56=float(pos[v][56]),
                             per_layer=[float(x) for x in pos[v]]) for v in vers}
                if states_name == "primary" and dset in ("loso", "all"):
                    for kind in ("script", "scenario"):
                        bs = {v: [] for v in vers}
                        for idx in boot_idx(sids, kind, rng):
                            pb = positions({v: P[v][idx] for v in vers}, None, vers)
                            for v in vers:
                                bs[v].append(float(pb[v][16:].mean()))
                        for v in vers:
                            r[v][f"ci_{kind}"] = [float(np.quantile(bs[v], .025)), float(np.quantile(bs[v], .975))]
                if dset == "loso" and states_name == "primary":  # length check
                    for v in vers:
                        pr = P[v][:, 16:].mean(1); ln = np.array([nh[v][s] for s in sids]); lt = np.array([nt[v][s] for s in sids])
                        from scipy.stats import pearsonr, spearmanr
                        r[v]["length"] = dict(pearson_nhist=float(pearsonr(pr, ln)[0]), spearman_nhist=float(spearmanr(pr, ln)[0]),
                                              pearson_ntok=float(pearsonr(pr, lt)[0]), mean_nhist=float(ln.mean()), mean_ntok=float(lt.mean()),
                                              mean_proj16_63=float(pr.mean()))
                if dset == "all" and states_name == "primary":  # sw009's scale: user-hostile = 0, self-hostile = 1 (sw008 class means, all 64)
                    u = ucache[sids[0]]
                    lo = (D["class_means"]["hdr_mean"]["user-hostile"]["all"].float() * u).sum(-1).numpy()
                    hi = (D["class_means"]["hdr_mean"]["self-hostile"]["all"].float() * u).sum(-1).numpy()
                    for v in vers:
                        sc = (P[v].mean(0) - lo) / (hi - lo)
                        r[v]["sw009_scale"] = dict(mean16_63=float(sc[16:].mean()), L24=float(sc[24]), L40=float(sc[40]), L56=float(sc[56]))
                res[f"{dset}|{states_name}|{setname}"] = dict(n_scripts=len(sids), pos=r)
    # projection-level parity gate (LOSO, paired63): primary vs recaptured
    a, b = res["loso|primary|paired63"]["pos"], res["loso|recaptured|paired63"]["pos"]
    dmax = max(abs(a[v]["mean16_63"] - b[v]["mean16_63"]) for v in K.V6)
    res["parity_projection"] = dict(max_abs_delta_mean16_63=dmax, ok=bool(dmax <= 0.02))
    # length across versions
    L = res["loso|primary|paired63"]["pos"]
    from scipy.stats import spearmanr
    res["length_across_versions"] = dict(spearman_pos_vs_mean_nhist=float(spearmanr([L[v]["mean16_63"] for v in K.V6], [L[v]["length"]["mean_nhist"] for v in K.V6])[0]),
                                         mean_nhist={v: L[v]["length"]["mean_nhist"] for v in K.V6})
    # score the brief's test on the primary summary
    p = res["loso|primary|paired63"]["pos"]
    def band(x):
        return "supports hostility (>= 0.6)" if x >= 0.6 else "supports unhelpfulness (<= 0.4)" if x <= 0.4 else "inconclusive (0.4-0.6)"
    res["score"] = {"polite_refusal_in_0.25-0.55": bool(0.25 <= p["polite_refusal"]["mean16_63"] <= 0.55),
                    "deflection_in_0.25-0.55": bool(0.25 <= p["deflection"]["mean16_63"] <= 0.55),
                    "curt_within_0.15_of_helpful": bool(abs(p["curt_helpful"]["mean16_63"]) <= 0.15),
                    "rude_helpful": band(p["rude_helpful"]["mean16_63"])}
    return res


def step1(m, D, prim):
    sids5 = sorted(set.intersection(*[set(prim[v]) for v in ("helpful", "polite_refusal")]))
    sids_r = sorted(set(prim["rude_helpful"]) & set(prim["curt_helpful"]))
    out = {}
    for name, a_, b_, sids in (("d_decline", "polite_refusal", "helpful", sids5), ("d_rude", "rude_helpful", "curt_helpful", sids_r)):
        A = torch.stack([prim[a_][s] for s in sids]); B = torch.stack([prim[b_][s] for s in sids]); f = np.array([K.fold_of(s) for s in sids])
        lo = torch.stack([A[f != k].mean(0) - B[f != k].mean(0) for k in range(5)])
        out[name] = dict(loso=lo, all=A.mean(0) - B.mean(0), n_all=len(sids), n_fit=[int((f != k).sum()) for k in range(5)], sids=sids)
    out["meta"] = dict(model=m, folds="leave one scenario out; index k = common10.SCEN[k] held out (dirs meta.scenarios)", scenarios=K.SCEN,
                       states="sw006 saved header means (5 versions) + sw010 PP30 capture (rude_helpful); header mean of 7 tokens; layers[L] output",
                       units="raw residual units (not unit)")
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--force", action="store_true"); a = ap.parse_args()
    sfx = "_smoke" if a.smoke else ""
    if os.path.exists(f"{K.RUN}/STEP1_DONE{sfx}") and not a.force:
        print("CACHED", f"{K.RUN}/STEP1_DONE{sfx}", "STEP01_DONE", flush=True); return
    t0 = time.time(); R = {"step0": {}, "step1": {}, "cos": {}}
    Dm = {m: K.chat_dirs(m) for m in MODELS}
    S1 = {}
    for m in MODELS:
        prim, rec, nh, nt = load_states(m, sfx)
        R["step0"][m] = step0(m, Dm[m], prim, rec, nh, nt, a.smoke)
        S1[m] = step1(m, Dm[m], prim)
        torch.save(S1[m], f"{K.RUN}/dirs10_{m}{sfx}.pt")
        print(m, "step0+1", f"{time.time() - t0:.0f}s", flush=True)
    LS = (16, 24, 32, 40, 48, 56, 63)
    for m in MODELS:
        D = Dm[m]; d = {"d_self": D["d_self"], "d_hostile": D["d_hostile"], "d_decline": S1[m]["d_decline"], "d_rude": S1[m]["d_rude"]}
        names = list(d); c = {}
        for i in range(4):
            for j in range(i + 1, 4):
                a_, b_ = names[i], names[j]
                per_fold = torch.stack([cosl(d[a_]["loso"][k], d[b_]["loso"][k]) for k in range(5)])  # [5, 64]
                c[f"{a_}~{b_}"] = dict(loso_mean=[float(x) for x in per_fold.mean(0)], loso_min_over_folds=[float(x) for x in per_fold.min(0).values],
                                       all=[float(x) for x in cosl(d[a_]["all"], d[b_]["all"])])
        for n_ in ("d_decline", "d_rude"):
            ff = [float(cosl(S1[m][n_]["loso"][i], S1[m][n_]["loso"][j])[16:].mean()) for i in range(5) for j in range(i + 1, 5)]
            c[f"{n_}_fold_stability_mean16_63"] = dict(min=min(ff), mean=float(np.mean(ff)))
        c["norms"] = {n_: [float(x) for x in d[n_]["all"].float().norm(dim=-1)] for n_ in names}
        R["cos"][m] = c
    for m in ("hdA0", "hdB0"):
        R["cos"][f"parent~{m}"] = {n_: dict(loso_mean=[float(x) for x in torch.stack([cosl((Dm["parent"][n_] if n_ in ("d_self", "d_hostile") else S1["parent"][n_])["loso"][k],
                                                                                            (Dm[m][n_] if n_ in ("d_self", "d_hostile") else S1[m][n_])["loso"][k]) for k in range(5)]).mean(0)])
                                   for n_ in ("d_self", "d_hostile", "d_decline", "d_rude")}
    for m in MODELS:
        R["cos"][m]["d_self_loso~sw009rs"] = [float(x) for x in cosl(Dm[m]["d_self"]["all"], Dm[m]["sw009_rs"]["d_self"]["all"])]
    json.dump(R, open(f"{K.RUN}/step01{sfx}.json", "w"))
    lines = [f"sw010 steps 0-1 {'(SMOKE) ' if a.smoke else ''}{time.strftime('%F %T')} UTC", "",
             "STEP 0: position on d_self (helpful = 0, dismissive = 1), mean over L16-63 [script CI] [scenario CI]; L24/L40/L56; sw009 scale (all-fit)"]
    for m in MODELS:
        S = R["step0"][m]; p = S["loso|primary|paired63"]["pos"]; pa = S["all|primary|paired63"]["pos"]; prs = S["sw009rs|primary|paired63"]["pos"]
        lines.append(f"-- {m}  (n = {S['loso|primary|paired63']['n_scripts']} paired scripts; projection parity max |delta| {S['parity_projection']['max_abs_delta_mean16_63']:.4f} ok={S['parity_projection']['ok']})")
        for v in K.V6:
            q = p[v]
            lines.append(f"   {v:15s} LOSO {q['mean16_63']:+.3f} {['%.2f' % x for x in q.get('ci_script', [])]} {['%.2f' % x for x in q.get('ci_scenario', [])]} "
                         f"L24/40/56 {q['L24']:+.2f}/{q['L40']:+.2f}/{q['L56']:+.2f} | all-fit {pa[v]['mean16_63']:+.3f} | sw009-split {prs[v]['mean16_63']:+.3f} | "
                         f"sw009-scale {pa[v]['sw009_scale']['mean16_63']:+.2f} | len r(n_hist) {q['length']['pearson_nhist']:+.2f} n_hist {q['length']['mean_nhist']:.0f}")
        lines.append(f"   score: {json.dumps(S['score'])}; across-version Spearman(pos, n_hist) {S['length_across_versions']['spearman_pos_vs_mean_nhist']:+.2f}")
    lines += ["", "STEP 1: cosines per layer (LOSO mean over folds) at L" + "/".join(map(str, LS))]
    for m in MODELS:
        for k, v in R["cos"][m].items():
            if "~" in k and isinstance(v, dict) and "loso_mean" in v:
                lines.append(f"   {m:6s} {k:22s} " + " ".join(f"{v['loso_mean'][L]:+.2f}" for L in LS) + "   all-fit " + " ".join(f"{v['all'][L]:+.2f}" for L in LS))
        lines.append(f"   {m:6s} fold stability d_decline {R['cos'][m]['d_decline_fold_stability_mean16_63']}, d_rude {R['cos'][m]['d_rude_fold_stability_mean16_63']}")
    for m in ("hdA0", "hdB0"):
        for n_, v in R["cos"][f"parent~{m}"].items():
            lines.append(f"   parent~{m} {n_:10s} " + " ".join(f"{v['loso_mean'][L]:+.2f}" for L in LS))
    open(f"{K.RUN}/step01_report{sfx}.txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    open(f"{K.RUN}/STEP1_DONE{sfx}", "w").write(time.strftime("%F %T") + "\n")
    print("STEP01_DONE", f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
