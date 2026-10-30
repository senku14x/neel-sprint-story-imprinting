"""sw011 analysis (executor-9, 30 Oct). numpy + torch only (runs inside the vLLM process for Part A; scipy is not in vlfix).
partA(out): STRICT labels of Part A behaviour; per (model, condition): forced rival share among habit-bearing replies (rival = 1,
  both = 0.5), n habit-bearing, onset, unconditional rival rate; free replies the same + cap-hit rate. Projections of the HF header
  mean (layers 16-63) onto d_self, d_hostile, the parent's d_self, sw009's random-split d_self, d_t1 (contemptuous - default at turn 1)
  and 20 within-condition null directions, all cross-fitted by scenario; per-layer z-score over all of the model's Part-A contexts,
  mean over layers 16-63 = the context's score. Spearman (condition mean score vs forced rival share), script-bootstrap CI, null
  distribution; the pre-registered rule; donor for hdB0 = the condition with the largest forced rival share (n habit >= 30).
report(out): Parts B and C from STRICT labels (+ two-judge labels where present): per arm toward-donor movement with
  script-bootstrap CIs, controls, displacement ratios, cap hits, conduct, known-answer accuracy.  -> out/report_<part>.json
  python ana11.py partA|report [--smoke]"""
import argparse, json, os, sys

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common11 as C  # noqa: E402

torch.set_num_threads(8)
L16 = list(range(16, 64))


def rankdata(x):
    x = np.asarray(x, float); o = np.argsort(x, kind="mergesort"); r = np.empty(len(x)); r[o] = np.arange(1, len(x) + 1)
    for v in np.unique(x):  # average ties
        i = x == v
        if i.sum() > 1:
            r[i] = r[i].mean()
    return r


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float); ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 3:
        return float("nan")
    ra, rb = rankdata(a[ok]), rankdata(b[ok])
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def behaviour(rows):
    """rows of one (model, cond, readout) -> per-script label lists."""
    per = {}
    for r in rows:
        per.setdefault(r["sid"], []).append(C.lab_strict(r["text"], r["model"]))
    return per


def share_from(per, sids):
    num = den = n = 0.0
    for s in sids:
        a, b = C.rival_counts(per.get(s, [])); num += a; den += b; n += len(per.get(s, []))
    return dict(rs=num / den if den else float("nan"), n_habit=int(den), n=int(n), onset=den / n if n else float("nan"), uncond=num / n if n else float("nan"))


def partA(out, smoke=False):
    rows = C.jl(f"{out}/A_gen.jsonl"); sc = C.scripts()
    sids = sorted({r["sid"] for r in rows}); conds = list(C.CONDS)
    B = {}
    for r in rows:
        B.setdefault((r["model"], r["cond"], r["readout"]), []).append(r)
    res = dict(behaviour={}, projection={}, spearman={}, rule={}, notes=[])
    beh = {}
    for (m, cond, ro), rr in B.items():
        per = behaviour(rr); d = share_from(per, sids)
        if ro == "free":
            d["cap_hit"] = float(np.mean([x["cap_hit"] for x in rr])); d["mean_tok"] = float(np.mean([x["n_tok"] for x in rr]))
            d["lex_disagree"] = float(np.mean([C.lab_strict(x["text"], m) != C.lab_lex(x["text"], m) for x in rr]))
        beh[(m, cond, ro)] = (per, d); res["behaviour"][f"{m}|{cond}|{ro}"] = d
    rng = np.random.default_rng(1030); BSi = [rng.integers(0, len(sids), len(sids)) for _ in range(1000 if not smoke else 50)]
    donor = {"hdA0": C.CONTEMPT, "parent": C.CONTEMPT}
    for m in C.MODELS:
        Z = torch.load(f"{out}/capA_{m}.pt", mmap=True); idx = {k: i for i, k in enumerate(Z["keys"])}
        Dh = torch.load(f"{C.RUN}/dirs_hist_{m}.pt", mmap=True)
        keys = [f"{c}|{s}" for c in conds for s in sids]
        X = Z["hdr_mean"][[idx[k] for k in keys]].float()[:, 16:]  # [N, 48, H]
        scen_of = [sc[k.split("|")[1]]["scenario"] for k in keys]
        # d_t1 = sys_contempt - nosys at turn 1, cross-fitted by scenario (HF header means)
        t1 = {}
        for k in sorted(set(scen_of)) + ["all"]:
            fs = [s for s in sids if sc[s]["scenario"] != k] or sids
            a1 = X[[keys.index(f"{C.CONTEMPT}|{s}") for s in fs]].mean(0); a0 = X[[keys.index(f"{C.DEFAULT}|{s}") for s in fs]].mean(0)
            t1[k] = unit(a1 - a0)
        dirs = {"d_self": lambda k: Dh["scen"][k]["d_self"].float()[16:], "d_hostile": lambda k: Dh["scen"][k]["d_hostile"].float()[16:],
                "par_dself": lambda k: Dh["scen"][k]["par_dself"].float()[16:], "d_t1": lambda k: t1[k]}
        for i in range(10):
            dirs[f"null_shuf{i}"] = (lambda i: lambda k: Dh["scen"][k]["shuf"][i].float()[16:])(i)
            dirs[f"null_cov{i}"] = (lambda i: lambda k: Dh["scen"][k]["cov"][i].float()[16:])(i)
        P = {}
        for name, f in dirs.items():
            p = torch.zeros(len(keys), 48)
            for k in set(scen_of):
                ii = [j for j, s in enumerate(scen_of) if s == k]; p[ii] = torch.einsum("nlh,lh->nl", X[ii], f(k))
            P[name] = p
        # sw009's random-split direction (other fold), beside the scenario version
        fold = Dh["rs_fold"]; p = torch.zeros(len(keys), 48)
        for j, k in enumerate(keys):
            s = k.split("|")[1]; other = "B" if fold[s] == "A" else "A"; p[j] = (X[j] * Dh["rs"][other].float()[16:]).sum(-1)
        P["d_self_rs"] = p
        # axis position on d_self (fit-set user-hostile = 0, self-hostile = 1)
        ax = torch.zeros(len(keys), 48)
        for k in set(scen_of):
            ii = [j for j, s in enumerate(scen_of) if s == k]
            lo, hi = Dh["scen"][k]["lo"][16:], Dh["scen"][k]["hi"][16:]
            ax[ii] = (P["d_self"][ii] - lo) / (hi - lo)
        score = {n: ((p - p.mean(0)) / p.std(0).clamp_min(1e-8)).mean(1).numpy() for n, p in P.items()}  # z per layer, mean over 16-63
        S2 = {n: v.reshape(len(conds), len(sids)) for n, v in score.items()}  # keys are cond-major, then sid
        cm = {n: {c: float(S2[n][i].mean()) for i, c in enumerate(conds)} for n in score}
        AX = ax.reshape(len(conds), len(sids), 48)
        res["projection"][m] = dict(cond_mean_z=cm, axis_pos_mean16_63={c: float(AX[i].mean()) for i, c in enumerate(conds)},
                                    axis_pos_L24_40_56={c: [float(AX[i, :, L - 16].mean()) for L in (24, 40, 56)] for i, c in enumerate(conds)},
                                    cos_dt1_dself=torch.nn.functional.cosine_similarity(t1["all"], Dh["scen"]["all"]["d_self"].float()[16:], dim=-1).tolist(),
                                    cos_dt1_dhostile=torch.nn.functional.cosine_similarity(t1["all"], Dh["scen"]["all"]["d_hostile"].float()[16:], dim=-1).tolist())
        if m == "parent":
            continue
        rs_f = {c: beh[(m, c, "btw")][1]["rs"] for c in conds}
        sp = {}
        for n in score:
            v = [cm[n][c] for c in conds]; r_all = spearman(v, [rs_f[c] for c in conds])
            c12 = [c for c in conds if c not in (C.DEFAULT, C.CONTEMPT)]
            r12 = spearman([cm[n][c] for c in c12], [rs_f[c] for c in c12])
            sp[n] = dict(rho14=r_all, rho12_no_endpoints=r12)
        # script bootstrap of rho for the real directions
        NUM = np.array([[C.rival_counts(beh[(m, c, "btw")][0].get(s, []))[0] for s in sids] for c in conds])
        DEN = np.array([[C.rival_counts(beh[(m, c, "btw")][0].get(s, []))[1] for s in sids] for c in conds])
        for n in ("d_self", "d_t1", "d_hostile", "par_dself", "d_self_rs"):
            bs = []
            for ii in BSi:
                with np.errstate(invalid="ignore", divide="ignore"):
                    bs.append(spearman(S2[n][:, ii].mean(1), NUM[:, ii].sum(1) / DEN[:, ii].sum(1)))
            sp[n]["ci14"] = np.nanpercentile(bs, [2.5, 97.5]).tolist()
        nulls = [sp[n]["rho14"] for n in sp if n.startswith("null_")]
        nulls12 = [sp[n]["rho12_no_endpoints"] for n in sp if n.startswith("null_")]
        order = sorted(conds, key=lambda c: cm["d_self"][c])
        # RV1: a null direction's sign is arbitrary (random-half differences / random combinations), so "beating the null directions"
        # compares d_self's rho with the nulls' |rho| (the signed max ignored strongly negative nulls; smoke: -0.89 next to +0.93)
        rule = dict(rho=sp["d_self"]["rho14"], rho_ci=sp["d_self"]["ci14"], null_max=float(np.nanmax(np.abs(nulls))), null_95=float(np.nanpercentile(np.abs(nulls), 95)),
                    null_max_signed=float(np.nanmax(nulls)), nosys_rank_low_to_high=order.index(C.DEFAULT) + 1, n_conds=len(conds))
        rule["passes"] = bool(rule["rho"] >= 0.6 and rule["rho"] > rule["null_max"] and rule["nosys_rank_low_to_high"] <= 5)
        rule["d_t1_rho12"] = sp["d_t1"]["rho12_no_endpoints"]; rule["d_self_rho12"] = sp["d_self"]["rho12_no_endpoints"]
        rule["null_max_rho12"] = float(np.nanmax(np.abs(nulls12)))  # RV1: |rho|
        uh = order.index("t1_user_hostile") + 1; fr = [order.index(c) + 1 for c in ("t1_self_friendly", "t1_user_friendly", "sys_helpful")]
        rule["watch_user_hostile_rank"] = uh; rule["watch_friendly_ranks"] = fr
        rule["watch_user_hostile_with_friendly"] = bool(uh <= max(fr))
        res["spearman"][m] = sp; res["rule"][m] = rule
        if m == "hdB0":
            cand = {c: d for c in conds if c not in (C.DEFAULT, "sys_empty") for d in [beh[(m, c, "btw")][1]] if d["n_habit"] >= (30 if not smoke else 1)}
            donor["hdB0"] = max(cand, key=lambda c: cand[c]["rs"]) if cand else C.CONTEMPT
            res["donor_candidates_hdB0"] = {c: [d["rs"], d["n_habit"]] for c, d in cand.items()}
    res["donor"] = donor
    json.dump(res, open(f"{out}/partA_results.json", "w"), indent=1)
    print(json.dumps(dict(event="partA", donor=donor, rule={m: {k: v for k, v in r.items()} for m, r in res["rule"].items()})), flush=True)
    return res


# ---------------------------------------------------------------------------------------------- Parts B / C report (STRICT + judges)
def judged_labels(out):
    J = {}
    for fn in ("judged.jsonl",):
        for j in C.jl(f"{out}/{fn}"):
            if not j.get("error"):
                J.setdefault(j["key"], {})[j["judge"]] = j
    return J


def report(out, smoke=False):
    res = {}
    for part, fns in (("B", ("B_btw.jsonl", "B_free.jsonl")), ("C", ("C_btw.jsonl", "C_free.jsonl"))):
        rows = [r for fn in fns for r in C.jl(f"{out}/{fn}")]
        if not rows:
            continue
        cells = {}
        for r in rows:
            cells.setdefault((r["model"], r["readout"], r["direction"], r["arm"]), {}).setdefault(r["sid"], []).append(C.lab_strict(r["text"], r["model"]))
        sids = sorted({r["sid"] for r in rows}); rng = np.random.default_rng(7); BS = [rng.integers(0, len(sids), len(sids)) for _ in range(1000)]
        R = {}
        for (m, ro, d, arm), per in cells.items():
            base = cells.get((m, ro, d, "none"))
            if base is None:
                continue
            def sh(p, ss):
                num = den = 0.0
                for s in ss:
                    a, b = C.rival_counts(p.get(s, [])); num += a; den += b
                return num / den if den else float("nan"), den
            v, n = sh(per, sids); v0, n0 = sh(base, sids)
            sign = 1 if d in ("ind", "d2c") else -1
            bs = [sign * (sh(per, [sids[i] for i in b])[0] - sh(base, [sids[i] for i in b])[0]) for b in BS]
            capr = [r["cap_hit"] for r in rows if r["model"] == m and r["readout"] == ro and r["direction"] == d and r["arm"] == arm]
            R[f"{m}|{ro}|{d}|{arm}"] = dict(rs=v, n_habit=int(n), toward=sign * (v - v0), ci=np.nanpercentile(bs, [2.5, 97.5]).tolist(),
                                            cap_hit=float(np.mean(capr)) if capr else None)
        res[part] = R
    json.dump(res, open(f"{out}/report_BC_strict.json", "w"), indent=1)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    out = f"{C.RUN}/smoke" if a.smoke else C.RUN
    {"partA": lambda: partA(out, a.smoke), "report": lambda: report(out, a.smoke)}[a.cmd]()
