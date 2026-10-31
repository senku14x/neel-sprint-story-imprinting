"""sw053 directions (E1 prep agent, 30 Oct 2026; CPU). Written fresh (not calling dirs11), checked against sw011's files.

d_t1(source, k) = unit(mean(sys_contempt) - mean(nosys)) per layer, over the header-mean HF states (7 reply-start tokens, layers[L]
outputs, HF + PEFT) of the scripts NOT in scenario k (leave-one-scenario-out, sw011's folds; k = 'all' uses every script).

  refit : known answer on CPU. Refit hdA0's / hdB0's d_t1 from sw011's saved Part A states (RUN11/capA_<m>.pt) with this code and
          compare with sw011's dirs_t1_<m>.pt per fold and layer (hdA0: 'd_t1'; hdB0: 'd_t1_contempt' and, for the record, its
          'd_t1', whose donor is style_dismissive (sw011 D5)). Gate: min cos over folds and L16-63 >= 0.99. -> RUN/dirs53_refit.json
  fit   : after the ctrlB0 HF capture (cap53.py): ctrlB0's d_t1 per fold from RUN/capT1_ctrlB0.pt; the GPU-path known answer (hdB0
          recaptured by cap53.py with the same code as ctrlB0 -> refit -> cos with sw011's file >= 0.99); cos(ctrlB0 d_t1, hd d_t1)
          per layer; the random control directions; writes RUN/dirs53_<recipient>.pt, RUN/dirs53_check.json and RUN/DIRS_OK.
Control directions (design_spec 'Controls'; sw028 A construction): per recipient and fold, NR covariance-shaped nulls = one Gaussian
combination (same coefficients at every layer) of the fold's fit-set within-condition-centred header means of the recipient's two
conditions (nosys, sys_contempt; recipient's HF states from sw011's capA), orthogonalised per layer to the direction under test (one
set of raw draws per (recipient, fold), orthogonalised separately to 'hd' and to 'cb').
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python dirs53.py refit|fit [--out DIR]"""
import argparse, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common53 as C  # noqa: E402

torch.set_num_threads(8)
F = torch.nn.functional
KA_COS = 0.99


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def orth(v, u):
    """v, u [..., 64, H] (u unit per layer): Gram-Schmidt per layer, unit result."""
    return unit(v - (v * u).sum(-1, keepdim=True) * u)


def folds(sc):
    """-> {k: fit-set sids}: the 5 leave-one-scenario-out folds plus 'all'."""
    out = {k: [s for s, v in sc.items() if v["scenario"] != k] for k in C.scenarios(sc)}
    out["all"] = sorted(sc)
    return out


def load_states(fn, conds=(C.DEFAULT, C.CONTEMPT)):
    """capture file {keys 'cond|sid', hdr_mean [N, 64, H]} -> getter(cond, sids) -> fp32 [n, 64, H]."""
    Z = torch.load(fn, mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(Z["keys"])}
    def get(cond, sids):
        return Z["hdr_mean"][[idx[f"{cond}|{s}"] for s in sids]].float()
    return get, Z


def fit_dt1(get, sc, donor=C.CONTEMPT):
    """-> {k: dict(u=[64, H] fp32 unit, norm=[64])}"""
    out = {}
    for k, fs in folds(sc).items():
        d = get(donor, fs).mean(0) - get(C.DEFAULT, fs).mean(0)
        out[k] = dict(u=unit(d), norm=d.norm(dim=-1))
    return out


def cos_l(a, b):
    return F.cosine_similarity(a.float(), b.float(), dim=-1)  # [64]


def compare(mine, ref_scen, key):
    """mine {k: dict(u)}; ref_scen = sw011 dirs_t1['scen'] -> per-fold min / mean cos at L16-63 and the overall min."""
    per = {}
    for k in mine:
        c = cos_l(mine[k]["u"], ref_scen[k][key])[16:]
        per[k] = dict(min=float(c.min()), mean=float(c.mean()))
    return dict(per_fold=per, min=min(v["min"] for v in per.values()))


def stage_refit(a):
    sc = C.scripts(); res = {}
    for m, keys in (("hdA0", ("d_t1",)), ("hdB0", ("d_t1_contempt", "d_t1"))):
        get, Z = load_states(f"{C.SW11}/capA_{m}.pt")
        ref = torch.load(f"{C.SW11}/dirs_t1_{m}.pt", mmap=True, weights_only=False)
        res[m] = dict(sw011_file_donor=ref["donor"])
        for kk in keys:
            donor = C.CONTEMPT if kk == "d_t1_contempt" or ref["donor"] == C.CONTEMPT else ref["donor"]
            mine = fit_dt1(get, sc, donor)
            res[m][kk] = dict(donor=donor, **compare(mine, ref["scen"], kk))
        # sanity: the dismissive-donor and the contempt-donor directions are different vectors (so the comparison can discriminate)
        if m == "hdB0":
            res[m]["cos_file_dt1_vs_dt1_contempt_L16_63_mean"] = float(cos_l(ref["scen"]["all"]["d_t1"], ref["scen"]["all"]["d_t1_contempt"])[16:].mean())
    prim = {"hdA0": res["hdA0"]["d_t1"]["min"], "hdB0": res["hdB0"]["d_t1_contempt"]["min"]}
    res["gate"] = dict(threshold=KA_COS, primary_min_cos=prim, ok=all(v >= KA_COS for v in prim.values()))
    out = a.out or C.RUN; os.makedirs(out, exist_ok=True)
    C.write_json(f"{out}/dirs53_refit.json", res)
    print(json.dumps(res["gate"]), flush=True)
    assert res["gate"]["ok"], f"d_t1 refit known answer failed: {res['gate']}"
    return res


def hd_dir_file(m):
    """the sw011 d_t1 used as 'hd' for recipient m: contemptuous - default for both (design_spec; D2). hdA0's file key 'd_t1' has donor
    sys_contempt; hdB0's 'd_t1' has donor style_dismissive, so its 'd_t1_contempt' (same folds, same file) is used."""
    ref = torch.load(f"{C.SW11}/dirs_t1_{m}.pt", mmap=True, weights_only=False)
    kk = "d_t1" if ref["donor"] == C.CONTEMPT else "d_t1_contempt"
    return {k: unit(v[kk].float()) for k, v in ref["scen"].items()}, kk, ref["donor"]


def stage_fit(a):
    out = a.out or C.RUN; sc = C.scripts(); fl = folds(sc); scen = C.scenarios(sc)
    chk = dict(created=time.strftime("%FT%TZ", time.gmtime()))
    # 1) GPU-path known answer: hdB0 recaptured with cap53's code -> refit -> cos with sw011's file
    if os.path.exists(f"{out}/capT1_hdB0_recap.pt"):
        get_r, _ = load_states(f"{out}/capT1_hdB0_recap.pt")
        ref = torch.load(f"{C.SW11}/dirs_t1_hdB0.pt", mmap=True, weights_only=False)
        chk["ka_recapture_hdB0"] = compare(fit_dt1(get_r, sc), ref["scen"], "d_t1_contempt")
    else:
        assert a.allow_no_recap, "capT1_hdB0_recap.pt missing (the GPU-path known answer)"
        chk["ka_recapture_hdB0"] = None
    # 2) ctrlB0 d_t1
    get_cb, _ = load_states(f"{out}/capT1_ctrlB0.pt")
    cb = fit_dt1(get_cb, sc)
    torch.save(dict(scen={k: dict(d_t1=v["u"].half(), norm=v["norm"]) for k, v in cb.items()}, donor=C.CONTEMPT,
                    src=f"{out}/capT1_ctrlB0.pt", adapter=C.LORA_HF["ctrlB0"]), f"{out}/dirs_t1_ctrlB0.pt")
    # 3) per recipient: U (hd, cb), R (controls), cosines, natural gaps along each direction (HF states)
    for ri, m in enumerate(C.ORGS):
        hd, kk, donor_file = hd_dir_file(m)
        get_m, _ = load_states(f"{C.SW11}/capA_{m}.pt")
        U, R, info = {}, {}, dict(hd_key=kk, sw011_file_donor=donor_file)
        for fi, (k, fs) in enumerate(fl.items()):
            U[f"hd|{k}"] = hd[k]; U[f"cb|{k}"] = cb[k]["u"]
            X0, X1 = get_m(C.DEFAULT, fs), get_m(C.CONTEMPT, fs)
            wc = torch.cat([X0 - X0.mean(0), X1 - X1.mean(0)])                                   # [2n, 64, H]
            g = torch.Generator().manual_seed(5300 + 10 * fi + ri)
            raw = torch.stack([unit(torch.einsum("nlh,n->lh", wc, torch.randn(len(wc), generator=g))) for _ in range(C.NR)])  # [NR, 64, H]
            for d in C.DIRS:
                u = U[f"{d}|{k}"]
                Rd = orth(raw, u)
                assert float((Rd * u).sum(-1)[:, 16:].abs().max()) < 1e-4
                for i in range(C.NR):
                    R[f"{d}|{i}|{k}"] = Rd[i]
                info.setdefault("raw_cos_with_dir_max_L16_63", {})[f"{d}|{k}"] = float((raw * u).sum(-1)[:, 16:].abs().max())
            # natural turn-1 gap along each direction in the recipient (HF header means; the driver re-measures in vLLM per token)
            for d in C.DIRS:
                u = U[f"{d}|{k}"]; g1 = ((X1.mean(0) - X0.mean(0)) * u).sum(-1)  # [64]
                sd = (((X0 * u).sum(-1).var(0) + (X1 * u).sum(-1).var(0)) / 2).sqrt()
                info.setdefault("gap_over_sd_L24_40_56", {})[f"{d}|{k}"] = [round(float(g1[L] / sd[L].clamp_min(1e-8)), 2) for L in (24, 40, 56)]
                info.setdefault("gap_L24_40_56", {})[f"{d}|{k}"] = [round(float(g1[L]), 3) for L in (24, 40, 56)]
            info.setdefault("cos_cb_hd_per_layer", {})[k] = [round(float(x), 4) for x in cos_l(U[f"cb|{k}"], U[f"hd|{k}"])]
        torch.save(dict(U={k: v.half() for k, v in U.items()}, R={k: v.half() for k, v in R.items()}, folds=fl, meta=info), f"{out}/dirs53_{m}.pt")
        c = torch.tensor(info["cos_cb_hd_per_layer"]["all"])
        info["cos_cb_hd_all_summary"] = dict(L16_40_mean=float(c[16:41].mean()), L41_63_mean=float(c[41:].mean()),
                                             at_L=[{L: round(float(c[L]), 3)} for L in (16, 24, 32, 40, 48, 56, 63)])
        chk[m] = info
    ka = chk["ka_recapture_hdB0"]
    chk["gate"] = dict(threshold=KA_COS, recapture_min_cos=ka["min"] if ka else None, ok=bool(ka is None or ka["min"] >= KA_COS))
    C.write_json(f"{out}/dirs53_check.json", chk)
    print(json.dumps(dict(gate=chk["gate"], cos_cb_hd={m: chk[m]["cos_cb_hd_all_summary"] for m in C.ORGS})), flush=True)
    assert chk["gate"]["ok"], f"GPU-path d_t1 known answer failed: {chk['gate']}"
    if not a.no_marker:
        open(f"{out}/DIRS_OK", "w").write(time.strftime("%FT%TZ", time.gmtime()))
    return chk


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["refit", "fit"]); ap.add_argument("--out", default="")
    ap.add_argument("--allow_no_recap", action="store_true"); ap.add_argument("--no_marker", action="store_true"); a = ap.parse_args()
    {"refit": stage_refit, "fit": stage_fit}[a.cmd](a)
