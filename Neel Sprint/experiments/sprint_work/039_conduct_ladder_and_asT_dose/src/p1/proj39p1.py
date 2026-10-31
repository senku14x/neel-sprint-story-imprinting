"""sw039 Part 1, stage L4 projection (CPU; on the node, where the captures are; <= 16 threads) (prep-L agent, E2, 31 Oct 2026).
Where each ladder context sits on sw038's v2 asT (Assistant turn-1-2 tokens) and r1 (header) directions (design_spec 'Where asT sits').
Per model m:
  folds    sw021's 8 leave-one-domain-out folds over the 61 G3 scripts (common39p1.lodo_folds); a ladder script uses the fold that
           holds ITS domain out (no in-sample projection; the 3 ladder scripts without a G3 context use their domain's fold).
  dirs     sw038's dirs38p1_<m>.pt (families 'asst' = asT, 'r1'), unit per layer. Known answer: the own refit below equals it
           (cos >= 0.99 at every layer L16-63 of every fold). If sw038's file is absent, the refit is used and every row says so
           (src = 'refit'); the projection is then still sw038's definition, on this job's same-path G3 captures.
  refit    r1 = unit(mean over the fold's fit scripts of hdr_mean[self-hostile] - hdr_mean[user-hostile]) (sw028 / sw052 fit_dself);
           asT = the same on asst_mean (sw029 D6), from CAPS/p1g3_<m>.pt (this job's captures of sw021's G3 contexts).
  scale    per layer, z_L = (x_L.u_L - mean_user_L) / (mean_self_L - mean_user_L), means over the fold's FIT scripts' G3 anchor
           captures (helpful = 0, dismissive = 1; D9); summary = mean of z_L over L16-63 (primary), bands L16 / L28-40 / L44-63 and
           layers 16, 28, 40, 52, 63 beside; the same with held-out-domain anchors (the fold's own-domain G3 scripts) beside.
  check    the G3 held-out scripts' own coordinates on the fit-set scale (user-hostile ~ 0, self-hostile ~ 1 if the scale transfers
           across domains), reported in proj_summary_<m>.json.
Outputs: RUN/coords_<m>.jsonl (one row per ladder context; key = the capture key), RUN/proj_summary_<m>.json, RUN/PROJ_DONE_<m>.
  OMP_NUM_THREADS=16 /root/venvs/si/bin/python -I proj39p1.py --model hdA0 [--sw038 /root/runs/sw038/p1/dirs38p1_{m}.pt]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common39p1 as K  # noqa: E402

L0 = 16
BANDS = {"L16_63": tuple(range(16, 64)), "L16": (16,), "L28_40": tuple(range(28, 41)), "L44_63": tuple(range(44, 64))}
REPORT_L = (16, 28, 40, 52, 63)
FAMS = {"asT": ("asst_mean", "asst"), "r1": ("hdr_mean", "r1")}     # arm -> (capture field, sw038 family name)
KA_COS = 0.99


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def g3_index(G):
    return {(c, s): i for i, (c, s) in enumerate(zip(G["cond"], G["sid"]))}


def refit(G, folds):
    """{domain: {arm: unit [64, H]}} from the G3 anchor captures (fit scripts of each fold)."""
    ix = g3_index(G); out = {}
    for d, f in folds.items():
        out[d] = {}
        for arm, (field, _) in FAMS.items():
            S = G[field][[ix[("self-hostile", s)] for s in f["fit"]]].float(); U = G[field][[ix[("user-hostile", s)] for s in f["fit"]]].float()
            out[d][arm] = unit((S - U).mean(0))
    return out


def load_sw038(path, domains):
    """sw038 dirs38p1_<m>.pt -> {domain: {arm: unit [64, H]}}. Accepted layouts (asserted, else a clear error):
       (a) sw029 dirs29 style: D['U'][fold][family], fold keys = domain names, or fold keys indexed through D['script'][sid]['fold']
           / D['scens'] / D['domains'];  (b) sw021 style: D['lodo'][domain]['u'] (r1) and D['lodo'][domain]['u_asst'] or ['asst']."""
    D = torch.load(path, weights_only=False, mmap=True)
    out = {}
    if "U" in D:
        U = D["U"]; keys = list(U)
        if set(domains) <= set(keys):
            fold_of = {d: d for d in domains}
        else:
            names = D.get("domains") or D.get("scens") or D.get("folds")
            assert names is not None and all(isinstance(k, int) for k in keys), f"sw038 dirs: fold keys {keys[:5]} are not domains; file keys {list(D)}"
            fold_of = {d: names.index(d) for d in domains}
        for d in domains:
            e = U[fold_of[d]]
            out[d] = {arm: unit(torch.as_tensor(e[fam]).float()) for arm, (_, fam) in FAMS.items()}
    elif "lodo" in D:
        for d in domains:
            e = D["lodo"][d]
            asst = e.get("u_asst", e.get("asst"))
            assert asst is not None, f"sw038 dirs (lodo layout) has no asT direction; keys {list(e)}"
            out[d] = {"r1": unit(torch.as_tensor(e["u"]).float()), "asT": unit(torch.as_tensor(asst).float())}
    else:
        raise SystemExit(f"sw038 dirs: unknown layout, keys {list(D)}")
    for d in domains:
        for arm, v in out[d].items():
            assert tuple(v.shape) == (64, 5120) or v.dim() == 2, (d, arm, tuple(v.shape))
    return out


def proj(X, U):
    """X [n, 64, H] (any float), U [64, H] unit -> [n, 64] fp32."""
    return torch.einsum("nlh,lh->nl", X.float(), U.float())


def summarise(z):
    """z [64] per-layer scaled coordinate -> band means + report layers."""
    out = {b: float(z[list(Ls)].mean()) for b, Ls in BANDS.items()}
    out["layers"] = {str(L): float(z[L]) for L in REPORT_L}
    return out


def run(m, caps_dir, run_dir, sw038_path):
    t0 = time.time()
    L = torch.load(f"{caps_dir}/p1cap_{m}.pt", mmap=True, weights_only=False)
    G = torch.load(f"{caps_dir}/p1g3_{m}.pt", mmap=True, weights_only=False)
    ix = g3_index(G)
    dom_of = {s: d for s, d in zip(G["sid"], G["domain"])}
    assert len(dom_of) == 61 and all(("self-hostile", s) in ix and ("user-hostile", s) in ix for s in dom_of)
    folds = K.lodo_folds(dom_of)
    RF = refit(G, folds)
    summ = dict(model=m, created=time.strftime("%FT%TZ", time.gmtime()), n_ladder=len(L["keys"]), folds={d: len(f["fit"]) for d, f in folds.items()})
    if sw038_path and os.path.exists(sw038_path):
        S38 = load_sw038(sw038_path, list(folds)); src = "sw038"
        ka = {d: {arm: float((S38[d][arm][L0:] * RF[d][arm][L0:]).sum(-1).min()) for arm in FAMS} for d in folds}
        summ["known_answer_refit_vs_sw038"] = dict(min_cos=ka, bar=KA_COS, pass_=bool(all(v >= KA_COS for x in ka.values() for v in x.values())))
        DIRS = S38
        if not summ["known_answer_refit_vs_sw038"]["pass_"]:
            K.wjson(f"{run_dir}/proj_summary_{m}.json", summ); print("KNOWN_ANSWER_FAILED", json.dumps(ka), flush=True); sys.exit(3)
    else:
        src = "refit"; DIRS = RF
        summ["known_answer_refit_vs_sw038"] = dict(pass_=None, note=f"sw038 directions absent at {sw038_path}; refit used (same definition)")
    summ["dirs_src"] = src
    # anchors per fold and arm: fit-set means (primary) and held-out-domain means (beside), per layer
    A = {}
    for d, f in folds.items():
        A[d] = {}
        for arm, (field, _) in FAMS.items():
            u_ = DIRS[d][arm]; e = {}
            for nm, sids in (("fit", f["fit"]), ("ho", f["held_out"])):
                pu = proj(G[field][[ix[("user-hostile", s)] for s in sids]], u_).mean(0)
                ps = proj(G[field][[ix[("self-hostile", s)] for s in sids]], u_).mean(0)
                e[nm] = (pu, ps)
            A[d][arm] = e
            gap = (e["fit"][1] - e["fit"][0])[L0:]
            assert float(gap.abs().min()) > 1e-6, f"degenerate anchor gap {m} {d} {arm}"
    summ["anchor_gap_fit"] = {d: {arm: {str(Lr): float(A[d][arm]["fit"][1][Lr] - A[d][arm]["fit"][0][Lr]) for Lr in REPORT_L} for arm in FAMS} for d in folds}
    # the scale's cross-domain check on the G3 held-out scripts
    chk = {}
    for arm, (field, _) in FAMS.items():
        for cond in ("user-hostile", "self-hostile"):
            zs = []
            for d, f in folds.items():
                pu, ps = A[d][arm]["fit"]
                p = proj(G[field][[ix[(cond, s)] for s in f["held_out"]]], DIRS[d][arm])
                zs.append(((p - pu) / (ps - pu))[:, L0:].mean(1))
            z = torch.cat(zs); chk[f"{arm}|{cond}"] = dict(mean=float(z.mean()), sd=float(z.std()), n=int(len(z)))
    summ["g3_heldout_on_fit_scale_L16_63"] = chk
    # ladder contexts
    rows = []
    sdom = K.load_scripts(check_sha=False)
    for i, (key, cond, sid, dom) in enumerate(zip(L["keys"], L["cond"], L["sid"], L["domain"])):
        assert sdom[sid]["domain"] == dom
        r = dict(key=key, model=m, cond=cond, sid=sid, domain=dom, fold=dom, dirs_src=src, n_asst=int(L["n_asst"][i]))
        for arm, (field, _) in FAMS.items():
            p = proj(L[field][i:i + 1], DIRS[dom][arm])[0]
            for nm in ("fit", "ho"):
                pu, ps = A[dom][arm][nm]
                z = (p - pu) / (ps - pu)
                r[arm if nm == "fit" else f"{arm}_ho"] = summarise(z) if nm == "fit" else {b: v for b, v in summarise(z).items() if b != "layers"}
            r[f"{arm}_raw_L40"] = float(p[40])
        rows.append(r)
    K.wjl(f"{run_dir}/coords_{m}.jsonl", rows)
    summ["n_rows"] = len(rows); summ["secs"] = round(time.time() - t0, 1)
    K.wjson(f"{run_dir}/proj_summary_{m}.json", summ)
    K.wjson(f"{run_dir}/PROJ_DONE_{m}", dict(t=time.strftime("%FT%TZ", time.gmtime()), n=len(rows), dirs_src=src))
    print("PROJ_DONE", m, src, len(rows), json.dumps(chk), flush=True)
    return summ


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True, choices=K.MODELS)
    ap.add_argument("--caps_dir", default=K.CAPS_NODE); ap.add_argument("--run_dir", default=K.RUN_NODE)
    ap.add_argument("--sw038", default="/root/runs/sw038/p1/dirs38p1_{m}.pt")
    a = ap.parse_args()
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "16")))
    run(a.model, a.caps_dir, a.run_dir, a.sw038.format(m=a.model) if a.sw038 else None)


if __name__ == "__main__":
    main()
