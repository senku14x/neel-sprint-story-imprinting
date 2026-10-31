"""sw052 directions, signs and the ctrlB0 capture check (executor-10 prep subagent, 30 Oct 2026; CPU only).
Fitting code (one function, `fit_dself`, used for both the known answer and ctrlB0):
  d_self = mean over the fold's FIT scripts of (hdr_mean[self-hostile] - hdr_mean[user-hostile]), per layer, fp32, unit
  (sw009 stage_dirs / overnight make_chat_dirs `d_self.loso` / sw012 r1 construction). Folds: leave one of sw008's 5 scenarios
  out; the fold of a script excludes its own scenario (dirs28's fit_sids, asserted).
Steps (all written to /workspace/runs_executor/sw052/):
  capture check  (capture_check.json): ctrlB0_chat.pt holds every sw008 self-/user-hostile/-control key in sw009's format
                 (keys, hdr [N, 7, 64, 5120] fp16, hdr_mean = mean of hdr, n_tok = sw009's and = len(sw008 ids), finite at L16-63);
                 header-token alignment (each ctrlB0 header token's nearest parent token, same context, L16 and L40, is itself);
                 adapter active in the capture (rel distance to the parent and to hdB0 at L40 >= 5x sw018's measured HF engine
                 floor 0.0090; sw018 D14).
  known answer   (refit hd's d_self from sw009's captures with fit_dself) cos >= 0.99 with sw028's dirs28_<m>.pt u at L16-63,
                 every fold.
  ctrlB0 d_self  u_c per fold, from ctrlB0_chat.pt with fit_dself.
  controls       A0-A2 = sw028's A0-A2 (new cov nulls, seeds 2800 + 10 fold + model), P0-P1 = sw028's P0-P1 (sw012 cova, covb), each
                 re-orthogonalised per layer to span(u, u_c) (u = the recipient's own d_self = sw028's r1 direction).
  signs          per (direction, script), from the recipient model's own sw009 captures (sw028 D5): sigma_P[i] [7] = sign((D_16,t -
                 x_16,t) . P_i,16), s_A[i] = sign(mean_t (D_16,t - x_16,t) . A_i,16).
  cosines        per layer, cos(u_c, u_hdA0) and cos(u_c, u_hdB0), fold-averaged (mean over the 5 folds of the per-fold cosine)
                 plus the all-64 fit; also the donor-recipient gap along u_c vs along u (in the recipient, sw009 captures).
Outputs: dirs52_<m>.pt (m = hdA0, hdB0; fp32 directions), dirs52_summary.json, capture_check.json
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python dirs52_x.py [--out DIR] [--skip_capture_check]"""
import argparse, json, os, sys, time

import torch

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
NS = "/workspace/Neel Sprint"
CAP9 = "/workspace/runs_executor/sw009_captures"
CAPC = "/workspace/runs_executor/sw018/captures/ctrlB0_chat.pt"
SW28 = "/workspace/runs_executor/sw028"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
OUT = "/workspace/runs_executor/sw052"
MODELS = ("hdA0", "hdB0")
DIRECTIONS = (("fwd", "self-hostile", "user-hostile"), ("rev", "user-hostile", "self-hostile"))
CONDS4 = ("self-hostile", "user-hostile", "self-control", "user-control")
N_A, N_P = 3, 2
L0 = 16
ENGINE_FLOOR_L40 = 0.0090   # sw018 D14: measured HF engine floor (median rel) at L40; the adapter-active gate is 5x this
ADAPTER_MARGIN = 5.0        # sw018 D14's calibrated multiple (its measured margins were 0.18-0.49 vs 0.045)
KA_COS = 0.99               # the orchestrator's known-answer bar for the fitting code (design_spec: cos >= 0.99)
ALIGN_L = (0, 1)             # header-token alignment test layers (D3: at L16/L40 even hdB0 vs parent fails the argmin test; at L2 it fails 10/128)
REPORT_L = (16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 63)


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def orth_span(v, basis):
    """v [..., 64, H]; basis: list of [64, H] unit vectors, mutually orthogonal per layer. Gram-Schmidt per layer, unit result."""
    for b in basis:
        v = v - (v * b).sum(-1, keepdim=True) * b
    return unit(v)


def fit_dself(C, idx, fit_sids):
    """THE fitting code: mean over fit_sids of hdr_mean[self-hostile] - hdr_mean[user-hostile] (fp32) [64, H] (raw, not unit)."""
    S = C["hdr_mean"][[idx[f"sw008|self-hostile|{s}"] for s in fit_sids]].float()
    U = C["hdr_mean"][[idx[f"sw008|user-hostile|{s}"] for s in fit_sids]].float()
    return (S - U).mean(0)


def sw008_sids():
    return sorted({json.loads(l)["sid"] for l in open(f"{SW8}/contexts.jsonl") if json.loads(l)["cond"] == "self-hostile"})


def rel(a, b):
    return float((a.float() - b.float()).norm() / b.float().norm().clamp_min(1e-6))


def capture_check(sids):
    """the smoke step for the ctrlB0 capture (design_spec 'Smoke first')."""
    C = torch.load(CAPC, mmap=True, weights_only=False); ic = {k: i for i, k in enumerate(C["keys"])}
    C9 = {m: torch.load(f"{CAP9}/{m}.pt", mmap=True, weights_only=False) for m in ("parent", "hdB0")}
    i9 = {m: {k: i for i, k in enumerate(C9[m]["keys"])} for m in C9}
    ctx = {(json.loads(l)["cond"], json.loads(l)["sid"]): len(json.loads(l)["ids"]) for l in open(f"{SW8}/contexts.jsonl")}
    R = dict(file=CAPC, n_keys=len(C["keys"]), fields={k: [list(v.shape), str(v.dtype)] for k, v in C.items() if hasattr(v, "shape")})
    need = [f"sw008|{c}|{s}" for c in CONDS4 for s in sids]
    R["missing_keys"] = [k for k in need if k not in ic]
    R["keys_unique"] = len(set(C["keys"])) == len(C["keys"])
    R["format_like_sw009"] = all(R["fields"].get(f) == [[len(C["keys"])] + list(C9["parent"][f].shape[1:]), str(C9["parent"][f].dtype)]
                                 for f in ("hdr", "hdr_mean")) and C["hdr"].shape[1:] == (7, 64, 5120)
    ntok_bad = [k for k in need if k in ic and (C["n_tok"][ic[k]] != C9["parent"]["n_tok"][i9["parent"][k]]
                                                or C["n_tok"][ic[k]] != ctx[tuple(k.split("|")[1:])])]
    R["n_tok_mismatch"] = ntok_bad[:10]; R["n_tok_mismatch_n"] = len(ntok_bad)
    # finite at L16-63 for every needed key (self/user-hostile are the fit inputs), mean consistency, alignment, adapter active
    fin, mean_rel, align_bad, align_ctl_bad, a_par, a_hdb = True, 0.0, [], [], [], []
    for k in need:
        if k not in ic:
            continue
        h = C["hdr"][ic[k]][:, L0:].float(); hm = C["hdr_mean"][ic[k]][L0:].float()
        fin &= bool(torch.isfinite(h).all() and torch.isfinite(hm).all())
        mean_rel = max(mean_rel, float(((h.mean(0) - hm).norm(dim=-1) / hm.norm(dim=-1)).max()))
        if k.split("|")[1] in ("self-hostile", "user-hostile"):
            hp = C9["parent"]["hdr"][i9["parent"][k]].float(); hb = C9["hdB0"]["hdr"][i9["hdB0"][k]].float()
            for L in ALIGN_L:   # token identity dominates only at early layers (at L16+ the adapter shift exceeds the token gaps)
                d = torch.cdist(C["hdr"][ic[k]][:, L].float(), hp[:, L])   # [7 ctrl tokens, 7 parent tokens]
                if not torch.equal(d.argmin(1), torch.arange(7)):
                    align_bad.append((k, L))
                if not torch.equal(torch.cdist(hb[:, L], hp[:, L]).argmin(1), torch.arange(7)):
                    align_ctl_bad.append((k, L))     # positive control of the check itself: two validated sw009 captures
            a_par.append(rel(C["hdr_mean"][ic[k]][40], C9["parent"]["hdr_mean"][i9["parent"][k]][40]))
            a_hdb.append(rel(C["hdr_mean"][ic[k]][40], C9["hdB0"]["hdr_mean"][i9["hdB0"][k]][40]))
    med = lambda v: sorted(v)[len(v) // 2]
    R.update(finite_L16_63=fin, hdr_mean_vs_mean_of_hdr_max_rel=mean_rel, header_alignment_failures=align_bad[:10],
             header_alignment_n_fail=len(align_bad), header_alignment_layers=list(ALIGN_L),
             header_alignment_check_control_hdB0_vs_parent_n_fail=len(align_ctl_bad), rel_L40_vs_parent_median=med(a_par), rel_L40_vs_parent_min=min(a_par),
             rel_L40_vs_hdB0_median=med(a_hdb), rel_L40_vs_hdB0_min=min(a_hdb),
             adapter_gate=f"min rel at L40 vs parent and vs hdB0 >= {ADAPTER_MARGIN} x {ENGINE_FLOOR_L40} (sw018 D14 measured HF engine floor)")
    R["pass"] = bool(not R["missing_keys"] and R["keys_unique"] and R["format_like_sw009"] and not ntok_bad and fin
                     and mean_rel < 2e-3 and not align_bad and not align_ctl_bad and min(a_par) >= ADAPTER_MARGIN * ENGINE_FLOOR_L40
                     and min(a_hdb) >= ADAPTER_MARGIN * ENGINE_FLOOR_L40)
    return R


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=OUT); ap.add_argument("--skip_capture_check", action="store_true")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); t0 = time.time()
    sids = sw008_sids(); assert len(sids) == 64
    if not a.skip_capture_check:
        cc = capture_check(sids)
        json.dump(cc, open(f"{a.out}/capture_check.json", "w"), indent=1, default=str)
        print("CAPTURE_CHECK", json.dumps({k: v for k, v in cc.items() if k != "fields"}, default=str), flush=True)
        if not cc["pass"]:
            print("CAPTURE_CHECK_FAILED", flush=True); sys.exit(2)
    CC = torch.load(CAPC, mmap=True, weights_only=False); icc = {k: i for i, k in enumerate(CC["keys"])}
    summ = dict(created=time.strftime("%FT%TZ", time.gmtime()), known_answer={}, cos_uc_u={}, cos_uc_u_all={}, gap_ratio={}, raw_cos={})
    uc_all = unit(fit_dself(CC, icc, sids))
    ucs = {}
    for mi, m in enumerate(MODELS):
        D28 = torch.load(f"{SW28}/dirs28_{m}.pt", weights_only=False)
        C = torch.load(f"{CAP9}/{m}.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
        assert sorted(D28["sids"]) == sids
        scens = sorted(D28["scen"])
        out = dict(model=m, sids=sids, script={s: dict(scenario=D28["script"][s]["scenario"]) for s in sids}, scen={}, sign={},
                   meta=dict(created=summ["created"], cap_ctrl=CAPC, cap_hd=f"{CAP9}/{m}.pt", dirs28=f"{SW28}/dirs28_{m}.pt",
                             A_src="dirs28 A0-A2 re-orthogonalised to span(u, u_c)", P_src="dirs28 P0-P1 re-orthogonalised to span(u, u_c)"))
        ka, cos_f = [], []
        for sc in scens:
            S28 = D28["scen"][sc]; fs = list(S28["fit_sids"]); ho = list(S28["held_out"])
            assert set(fs) == {s for s in sids if D28["script"][s]["scenario"] != sc} and not set(fs) & set(ho)
            u28 = unit(S28["u"].float())
            u_ref = unit(fit_dself(C, idx, fs))                                  # known answer: refit hd's d_self with this code
            c_ka = (u_ref * u28).sum(-1)
            ka.append(float(c_ka[L0:].min()))
            u = u28                                                              # r1 uses sw028's direction exactly
            if sc not in ucs:
                ucs[sc] = unit(fit_dself(CC, icc, fs))                           # ctrlB0's d_self, the same fold
            uc = ucs[sc]
            cos_f.append((uc * u).sum(-1))
            uc_perp = unit(uc - (uc * u).sum(-1, keepdim=True) * u)              # second basis vector of span(u, u_c)
            A = orth_span(S28["A"].float(), [u, uc_perp]); P = orth_span(S28["P"][:N_P].float(), [u, uc_perp])
            assert float(max((A * u).sum(-1)[:, L0:].abs().max(), (A * uc).sum(-1)[:, L0:].abs().max(),
                             (P * u).sum(-1)[:, L0:].abs().max(), (P * uc).sum(-1)[:, L0:].abs().max())) < 1e-4
            rawc = dict(A_vs_uc=(unit(S28["A"].float()) * uc).sum(-1)[:, L0:].abs().max(-1).values.tolist(),
                        P_vs_uc=(unit(S28["P"][:N_P].float()) * uc).sum(-1)[:, L0:].abs().max(-1).values.tolist(),
                        A_new_vs_A28_min=(A * unit(S28["A"].float())).sum(-1)[:, L0:].min(-1).values.tolist(),
                        P_new_vs_P28_min=(P * unit(S28["P"][:N_P].float())).sum(-1)[:, L0:].min(-1).values.tolist())
            summ["raw_cos"][f"{m}|{sc}"] = rawc
            out["scen"][sc] = dict(u=u, uc=uc, A=A, P=P, fit_sids=fs, held_out=ho, cos_uc_u=cos_f[-1], ka_cos=c_ka)
            for s in ho:
                for d, rec, don in DIRECTIONS:
                    xr = C["hdr"][idx[f"sw008|{rec}|{s}"]].float(); xd = C["hdr"][idx[f"sw008|{don}|{s}"]].float()   # [7, 64, H]
                    gv = xd[:, L0] - xr[:, L0]
                    pP = gv @ P[:, L0].T; pA = gv @ A[:, L0].T                    # [7, n]
                    sigma = torch.where(pP.T >= 0, 1.0, -1.0); sA = torch.where(pA.mean(0) >= 0, 1.0, -1.0)
                    g_u = ((xd - xr) * u[None]).sum(-1); g_c = ((xd - xr) * uc[None]).sum(-1)    # [7, 64]
                    out["sign"][f"{d}|{s}"] = dict(sigma_P=sigma, s_A=sA, pP16=pP.T, pA16=pA.T, gap_u=g_u, gap_uc=g_c)
            print(m, sc, "n_fit", len(fs), "| KA min cos(refit, dirs28 u) L16-63", round(ka[-1], 6),
                  "| cos(u_c, u) L16/32/48/63", [round(float(cos_f[-1][L]), 3) for L in (16, 32, 48, 63)],
                  "| raw max|cos(A, u_c)|", [round(x, 3) for x in rawc["A_vs_uc"]], flush=True)
        assert len(out["sign"]) == 2 * len(sids)
        cf = torch.stack(cos_f).mean(0)
        summ["known_answer"][m] = dict(min_cos_L16_63_over_folds=min(ka), per_fold=ka, bar=KA_COS, pass_=bool(min(ka) >= KA_COS))
        summ["cos_uc_u"][m] = {f"L{L}": round(float(cf[L]), 4) for L in range(L0, 64)}
        summ["cos_uc_u"][m]["median_L16_63"] = round(float(cf[L0:].median()), 4)
        uall = unit(fit_dself(C, idx, sids)); ca = (uall * uc_all).sum(-1)
        summ["cos_uc_u_all"][m] = {f"L{L}": round(float(ca[L]), 4) for L in REPORT_L}
        # how large c1's edit is relative to r1's: median over scripts of |gap along u_c| / |gap along u| (tokens 1-6, header)
        rr = {}
        for d, _, _ in DIRECTIONS:
            gu = torch.stack([out["sign"][f"{d}|{s}"]["gap_u"][1:].abs().mean(0) for s in sids]); gc = torch.stack([out["sign"][f"{d}|{s}"]["gap_uc"][1:].abs().mean(0) for s in sids])
            rr[d] = {f"L{L}": round(float((gc[:, L] / gu[:, L].clamp_min(1e-6)).median()), 3) for L in REPORT_L}
        summ["gap_ratio"][m] = rr
        if not summ["known_answer"][m]["pass_"]:
            json.dump(summ, open(f"{a.out}/dirs52_summary.json", "w"), indent=1)
            print("KNOWN_ANSWER_FAILED", m, flush=True); sys.exit(3)
        torch.save(out, f"{a.out}/dirs52_{m}.pt")
        print(m, "saved", f"{a.out}/dirs52_{m}.pt", "| KA", round(min(ka), 6), "| fold-avg cos(u_c, u)", {L: summ["cos_uc_u"][m][f"L{L}"] for L in (16, 32, 40, 48, 56, 63)},
              "median", summ["cos_uc_u"][m]["median_L16_63"], f"{time.time() - t0:.0f}s", flush=True)
    json.dump(summ, open(f"{a.out}/dirs52_summary.json", "w"), indent=1)
    print("DIRS52_DONE", flush=True)


if __name__ == "__main__":
    main()
