"""sw057 c1 latent-level steps (CPU, box 1; the SAE stays on box 1).
  summary : c1 step 1 report from lasso/c1_lasso57.json: R^2 at <= 20 latents per fold vs each null family's 95th percentile (and the
            pooled 40), fold mean / spread; the latent sets: supp20 (the R^2_at_20 path point's own support) and top20 (sae1029's
            convention: top 20 by |coefficient| at the first path point with R^2 >= 0.6); overlap of top20 (signed: coefficient > 0 =
            self-hostile side) with sae1029's 15 shared dismissive latents of the same model, beside the hypergeometric expectation
            20 * 15 / N (N = 131,072, the Lasso's population; and N = sae1029's live count) and the empirical overlap of the null
            vectors' supports; consensus latents = in top20 of >= 3 of 5 folds in both models.
  g3      : per-latent mean activation (SAE codes averaged over each context's own-turn tokens) self-hostile vs user-hostile on
            sw019 G3 (58 v2 test scripts; caps57/g3_L42_<m>.pt): paired difference with a script bootstrap CI (B = 2,000, seed 57;
            one script per scenario, so scenario-clustered), AUROC; for the consensus / top20 / supp20 latents, sae1029's 15 shared,
            and the 20 latents with the largest |difference|; sign agreement with the Lasso coefficient.
  labels  : labels57.py (= sae1029 labels_x.py route: the release's web max-acts + our chat windows + refusal share) for the
            consensus latents and the top-|difference| latents; labels are hypotheses.
  spec    : the latent-clamp spec per model (caps57/sw008_L42_<m>.pt): per fold the top20 latents, 5 frequency-matched random draws
            (pooled-context firing frequency within +-25 %, live >= 5 %, chosen latents excluded; widened to +-50 %, then nearest,
            if empty; rng 57), encoder rows / biases / decoder columns / b_dec / threshold; per script the donor's (self-hostile)
            mean per-token code of every listed latent (the target) and the dense donor - recipient own-turn mean difference.
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python c1_latents57.py summary|g3|labels|spec [--models hdA0,hdB0]"""
import argparse, json, os, sys, time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common57 as K  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
LASSO = f"{K.RUN}/c1/lasso/c1_lasso57.json"
SAE29 = "/workspace/runs_executor/sae1029"
CAPS = f"{K.RUN}/caps57"
OUT = f"{K.RUN}/c1"
F_ = 131072
NB, SEED = 2000, 57


def shared15():
    s = json.load(open(f"{SAE29}/part3_causal/edit_spec_summary.json"))
    return {m: s[m]["shared_ids"] for m in ("hdA0", "hdB0")}


def live_counts():
    a = np.load(f"{SAE29}/part2/analysis/auroc_per_latent.npz")
    return {m: int(a[f"bc|{m}|live"].sum()) for m in ("hdA0", "hdB0")}


def top20(real):
    return [i for i, _ in real["top20_at_0p6"]]


def summary():
    d = json.load(open(LASSO)); sh = shared15(); nl = live_counts()
    out = dict(source=LASSO, created=time.strftime("%FT%TZ", time.gmtime()), per_fold={}, mean={}, consensus={}, ka=dict(
        sklearn=d["ka_sklearn"], planted=d["ka_planted"], refit_cos_min=min(d["ka_refit_cos"].values())), null_grid_done=d.get("null_grid_done"))
    for m in ("hdA0", "hdB0"):
        rows = []
        for k, v in d["real"].items():
            _, mm, sc = k.split("|")
            if mm != m:
                continue
            ns = [x for n, x in d["nulls"].items() if n.split("|")[1] == m and n.split("|")[2] == sc]
            sh_n = [x["R2_at_20"] for n, x in d["nulls"].items() if n.startswith("shuf|") and n.split("|")[1] == m and n.split("|")[2] == sc]
            cv_n = [x["R2_at_20"] for n, x in d["nulls"].items() if n.startswith("cov|") and n.split("|")[1] == m and n.split("|")[2] == sc]
            t20 = top20(v); pos = {i for i, c in v["top20_at_0p6"] if c > 0}
            ov = len(set(t20) & set(sh[m])); ov_signed = len(pos & set(sh[m]))
            null_ov = [len({i for i, c in x["supp20"]} & set(sh[m])) for x in ns]
            rows.append(dict(fold=sc, R2_at_20=v["R2_at_20"], supp20_nnz=v["supp20_nnz"], R2_at_100=v["R2_at_100"], nnz_for_0p6=v["nnz_for_0p6"],
                             best_single_cos=v["best_single_cos"], best_single_idx=v["best_single_idx"],
                             null_shuf_p95=float(np.quantile(sh_n, 0.95)), null_cov_p95=float(np.quantile(cv_n, 0.95)),
                             null_pooled_p95=float(np.quantile(sh_n + cv_n, 0.95)), null_shuf_mean=float(np.mean(sh_n)), null_cov_mean=float(np.mean(cv_n)),
                             above_both_p95=bool(v["R2_at_20"] > max(np.quantile(sh_n, 0.95), np.quantile(cv_n, 0.95))),
                             supp20=v["supp20"], top20=v["top20_at_0p6"], overlap_top20_shared15=ov, overlap_top20_pos_shared15=ov_signed,
                             overlap_supp20_shared15=len({i for i, c in v["supp20"]} & set(sh[m])), null_supp20_overlap_mean=float(np.mean(null_ov)),
                             null_supp20_overlap_max=int(max(null_ov))))
        out["per_fold"][m] = rows
        f = lambda q: [r[q] for r in rows]
        out["mean"][m] = dict(R2_at_20=float(np.mean(f("R2_at_20"))), R2_at_20_range=[min(f("R2_at_20")), max(f("R2_at_20"))],
                              null_shuf_p95=float(np.mean(f("null_shuf_p95"))), null_cov_p95=float(np.mean(f("null_cov_p95"))),
                              null_pooled_p95=float(np.mean(f("null_pooled_p95"))), folds_above_both_p95=int(sum(f("above_both_p95"))),
                              overlap_top20_shared15=f("overlap_top20_shared15"),
                              hypergeom_expect_F=20 * 15 / F_, hypergeom_expect_live=20 * 15 / nl[m], live_count=nl[m])
        cnt = {}
        for r in rows:
            for i, c in r["top20"]:
                cnt.setdefault(i, []).append(c)
        out["consensus"][m] = sorted([(i, len(v), float(np.mean(v))) for i, v in cnt.items() if len(v) >= 3], key=lambda x: -abs(x[2]))
    both = {i for i, _, _ in out["consensus"]["hdA0"]} & {i for i, _, _ in out["consensus"]["hdB0"]}
    out["consensus_both"] = sorted(both, key=lambda i: -abs(dict((a, c) for a, _, c in out["consensus"]["hdA0"])[i]))
    out["shared15"] = sh
    json.dump(out, open(f"{OUT}/c1_step1_summary.json", "w"), indent=1)
    for m in ("hdA0", "hdB0"):
        print(m, json.dumps(out["mean"][m]), flush=True)
        for r in out["per_fold"][m]:
            print("  ", r["fold"], "R2@20 %.3f (nnz %d) | null p95 shuf %.3f cov %.3f | top20 overlap %d (pos %d) | null supp overlap max %d" % (
                r["R2_at_20"], r["supp20_nnz"], r["null_shuf_p95"], r["null_cov_p95"], r["overlap_top20_shared15"], r["overlap_top20_pos_shared15"], r["null_supp20_overlap_max"]))
    print("consensus both", out["consensus_both"], flush=True)
    return out


# ------------------------------------------------------------------------------------------------- SAE helpers
def load_sae():
    import sae57 as S
    sae = S.load_sae(device="cpu")
    return sae


@torch.no_grad()
def mean_codes(sae, states, chunk=1024):
    """states: list of [n_i, H] fp16 -> [n_ctx, F] fp32 mean code per context (the library's forward, threshold on)."""
    out = torch.zeros(len(states), F_)
    for i, X in enumerate(states):
        acc = torch.zeros(F_)
        for s in range(0, X.shape[0], chunk):
            _, f = sae(X[s:s + chunk].float(), output_features=True)
            acc += f.sum(0)
        out[i] = acc / X.shape[0]
    return out


def auroc(a, b):
    from scipy.stats import rankdata
    x = np.concatenate([a, b]); r = rankdata(x)
    return float((r[:len(a)].sum() - len(a) * (len(a) + 1) / 2) / (len(a) * len(b)))


def g3(models):
    S1 = json.load(open(f"{OUT}/c1_step1_summary.json")); sh = shared15()
    sae = load_sae()
    res = dict(created=time.strftime("%FT%TZ", time.gmtime()), models={})
    for m in models:
        z = torch.load(f"{CAPS}/g3_L42_{m}.pt", weights_only=False)
        Mc = mean_codes(sae, z["states"])
        sids = sorted({k.split("|")[2] for k in z["keys"]}); ix = {k: i for i, k in enumerate(z["keys"])}
        S = Mc[[ix[f"g3|self-hostile|{s}"] for s in sids]].numpy(); U = Mc[[ix[f"g3|user-hostile|{s}"] for s in sids]].numpy()
        D = S - U
        rng = np.random.default_rng(SEED); W = np.stack([np.bincount(rng.integers(0, len(sids), len(sids)), minlength=len(sids)) for _ in range(NB)]).astype(float)
        mm = m if m in sh else "hdA0"
        rows_l = S1["per_fold"].get(mm, S1["per_fold"]["hdA0"])
        coef = {}
        for r in rows_l:
            for i, c in r["top20"]:
                coef.setdefault(i, []).append(c)
        cons = [i for i, _, _ in S1["consensus"].get(mm, [])]
        supp = sorted({i for r in rows_l for i, _ in r["supp20"]})
        dm = D.mean(0); top_abs = [int(i) for i in np.argsort(-np.abs(dm))[:20]]
        want = sorted(set(cons) | set(supp) | set(sh[mm]) | set(top_abs) | set(coef))
        lat = {}
        for f in want:
            bs = (W @ D[:, f]) / len(sids)
            lat[int(f)] = dict(mean_self=float(S[:, f].mean()), mean_user=float(U[:, f].mean()), diff=float(dm[f]),
                               ci=[float(np.quantile(bs, .025)), float(np.quantile(bs, .975))], auroc_self_vs_user=auroc(S[:, f], U[:, f]),
                               frac_self_on=float((S[:, f] > 0).mean()), frac_user_on=float((U[:, f] > 0).mean()),
                               lasso_coef_mean=float(np.mean(coef[f])) if f in coef else None,
                               sign_agrees=(None if f not in coef else bool(np.sign(np.mean(coef[f])) == np.sign(dm[f]))),
                               tags=[t for t, s_ in (("consensus", cons), ("supp20", supp), ("shared15", sh[mm]), ("top_abs_diff", top_abs), ("top20_any_fold", list(coef))) if f in s_])
        bsall = (W @ D) / len(sids)
        lo, hi = np.quantile(bsall, .025, axis=0), np.quantile(bsall, .975, axis=0)
        res["models"][m] = dict(n_scripts=len(sids), latents=lat, top_abs_diff=top_abs, consensus=cons,
                                n_latents_ci_excl0_pos=int(((lo > 0)).sum()), n_latents_ci_excl0_neg=int(((hi < 0)).sum()))
        print(m, "scripts", len(sids), "| consensus:", [(f, round(lat[f]["diff"], 3), [round(x, 3) for x in lat[f]["ci"]], round(lat[f]["auroc_self_vs_user"], 2)) for f in cons[:12]], flush=True)
        print("   shared15:", [(f, round(lat[f]["diff"], 3), round(lat[f]["auroc_self_vs_user"], 2)) for f in sh[mm]], flush=True)
        print("   top |diff|:", [(f, round(lat[f]["diff"], 3), round(lat[f]["auroc_self_vs_user"], 2)) for f in top_abs[:10]], flush=True)
    json.dump(res, open(f"{OUT}/c1_g3_latents.json", "w"), indent=1)


def labels(models):
    import labels57 as LBL
    S1 = json.load(open(f"{OUT}/c1_step1_summary.json"))
    G = json.load(open(f"{OUT}/c1_g3_latents.json")) if os.path.exists(f"{OUT}/c1_g3_latents.json") else None
    lb = LBL.Labeler(); md = [f"# sw057 c1 latent examples (labels57 = sae1029 labels_x route; labels are hypotheses), {time.strftime('%FT%TZ', time.gmtime())}", ""]
    want = list(S1["consensus_both"])
    if G:
        for m in models:
            want += [f for f in G["models"][m]["top_abs_diff"][:10] if f not in want]
    for f in want:
        ch, refus, nch = lb.chat(f, 5)
        md.append(f"### latent {f}  (refusal-language share of top-{nch} chat windows: {refus:.2f})")
        md.append("**web (release max-acts):**")
        md += [f"- {o['act']}: {o['text']}" for o in lb.web(f, 5)]
        md.append("**our chat transcripts:**")
        md += [f"- {o['act']} [{o['src']}]: {o['text']}" for o in ch]
        md.append("")
    open(f"{OUT}/c1_latent_examples.md", "w").write("\n".join(md))
    print("written", f"{OUT}/c1_latent_examples.md", len(want), "latents", flush=True)


def spec(models):
    S1 = json.load(open(f"{OUT}/c1_step1_summary.json"))
    sae = load_sae()
    W_enc = sae.encoder.weight.data.float(); b_enc = sae.encoder.bias.data.float(); Dd = sae.decoder.weight.data.float()
    b_dec = sae.b_dec.data.float(); thr = float(sae.threshold)
    d29 = {m: torch.load(f"{K.SW29}/dirs29_{m}.pt", weights_only=False) for m in models}
    for m in models:
        z = torch.load(f"{CAPS}/sw008_L42_{m}.pt", weights_only=False)
        ix = {k: i for i, k in enumerate(z["keys"])}
        Mc = mean_codes(sae, z["states"])
        freq = (Mc > 0).float().mean(0).numpy()
        sids = sorted({k.split("|")[2] for k in z["keys"]})
        mean_state = {k: z["states"][i].float().mean(0) for k, i in ix.items()}
        rng = np.random.default_rng(57)
        out = dict(model=m, created=time.strftime("%FT%TZ", time.gmtime()), b_dec=b_dec, thr=thr, fold={}, script={}, rand_widen={})
        for r in S1["per_fold"][m]:
            sc = r["fold"]; shared = [i for i, _ in r["top20"]]
            excl = set(shared); rand = []
            for dd in range(K.N_RAND):
                draw = []
                for f in shared:
                    for w in (0.25, 0.5):
                        cand = np.where((freq >= 0.05) & (freq > (1 - w) * freq[f]) & (freq < (1 + w) * freq[f]))[0]
                        cand = [c for c in cand if c not in excl and c not in draw]
                        if cand:
                            break
                    if not cand:
                        order = np.argsort(np.abs(freq - freq[f])); cand = [int(c) for c in order if c not in excl and c not in draw][:50]
                        out["rand_widen"].setdefault(sc, []).append(int(f))
                    draw.append(int(rng.choice(cand)))
                rand.append(draw)
            feats = shared + [f for dr in rand for f in dr]
            n0 = len(shared)
            out["fold"][sc] = dict(feats=feats, shared=list(range(n0)), rand=[list(range(n0 + j * n0, n0 + (j + 1) * n0)) for j in range(K.N_RAND)],
                                   shared_ids=shared, rand_ids=rand, W_enc=W_enc[feats].clone(), b_enc=b_enc[feats].clone(), D=Dd[:, feats].clone(),
                                   freq_shared=[float(freq[f]) for f in shared], freq_rand=[[float(freq[f]) for f in dr] for dr in rand])
            for sid in sids:
                if d29[m]["script"][sid]["scenario"] != sc:
                    continue
                kd, kr = f"sw008|self-hostile|{sid}", f"sw008|user-hostile|{sid}"
                out["script"][sid] = dict(fold=sc, tgt=Mc[ix[kd]][feats].clone(), dense=(mean_state[kd] - mean_state[kr]).clone(),
                                          recipient_code=Mc[ix[kr]][shared].clone())
        assert len(out["script"]) == 64
        torch.save(out, f"{OUT}/clamp_spec57_{m}.pt")
        print(m, "spec written; folds", list(out["fold"]), "| widened", {k: len(v) for k, v in out["rand_widen"].items()}, flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=("summary", "g3", "labels", "spec")); ap.add_argument("--models", default="hdA0,hdB0")
    a = ap.parse_args(); ms = a.models.split(",")
    {"summary": lambda: summary(), "g3": lambda: g3(ms), "labels": lambda: labels(ms), "spec": lambda: spec(ms)}[a.cmd]()


if __name__ == "__main__":
    main()
