"""E12 R01 Part 2 validation statistics, R1 verdicts (E12-D03), and Part 3 predictions for SYS-EMPTY.
CPU only. python analysis_p2.py [--models V,SB,VB,S]
Writes results/readouts.json, results/verdicts.json, results/predictions_sys_empty.json."""
import argparse, collections, json, math, os, random, sys
import numpy as np
sys.path.append("/workspace/e12/r01/pydeps_sci")
from scipy import stats
sys.path.insert(0, "/workspace/e12/r01/code")
from e12lib import *  # noqa

P2 = f"{R}/results/part2"; P4 = f"{R}/results/part4"
MATCH = {"O": "onset", "C": "a", "H": "f"}
NPERM, NBOOT = 10000, 2000


def spearman(x, y):
    return float(stats.spearmanr(x, y).statistic)


def perm_p(x, y, n=NPERM, seed=0):
    rng = np.random.default_rng(seed)
    x = stats.rankdata(x); y = stats.rankdata(y)
    r0 = float(np.corrcoef(x, y)[0, 1])
    ge2 = ge1 = 0
    for _ in range(n):
        r = float(np.corrcoef(x, rng.permutation(y))[0, 1])
        ge2 += abs(r) >= abs(r0) - 1e-12; ge1 += r >= r0 - 1e-12
    return r0, (ge2 + 1) / (n + 1), (ge1 + 1) / (n + 1)


def boot_contrast(A, B, n=NBOOT, seed=0, paired=False):
    """A, B: lists of (script_id, value). Contrast = mean(A) - mean(B); 95% bootstrap interval over scripts (union of scripts;
    each resampled script brings all its contexts in both cells, with multiplicity)."""
    sA = collections.defaultdict(list); sB = collections.defaultdict(list)
    for s, v in A:
        sA[s].append(v)
    for s, v in B:
        sB[s].append(v)
    scripts = sorted(set(sA) | set(sB))
    idx = {s: i for i, s in enumerate(scripts)}
    sumA = np.zeros(len(scripts)); nA = np.zeros(len(scripts)); sumB = np.zeros(len(scripts)); nB = np.zeros(len(scripts))
    for s, v in sA.items():
        sumA[idx[s]] = sum(v); nA[idx[s]] = len(v)
    for s, v in sB.items():
        sumB[idx[s]] = sum(v); nB[idx[s]] = len(v)
    est = sumA.sum() / nA.sum() - sumB.sum() / nB.sum()
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n):
        w = np.bincount(rng.integers(0, len(scripts), len(scripts)), minlength=len(scripts))
        a = (w * nA).sum(); b = (w * nB).sum()
        if a == 0 or b == 0:
            continue
        bs.append((w * sumA).sum() / a - (w * sumB).sum() / b)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return dict(est=float(est), lo=float(lo), hi=float(hi), n_boot=len(bs), n_scripts=len(scripts), nA=int(nA.sum()), nB=int(nB.sum()))


def rates(convs, M):
    if not convs:
        return None
    ms = [measures(c, M) for c in convs]
    return {k: float(np.mean([m[k] for m in ms])) for k in ("f", "c", "onset", "a")} | dict(n=len(convs))


def analyse_model(M, C):
    con = CONTRAST[M]
    meta = json.load(open(f"{P2}/{M}_conditions.json"))
    conds = sorted(meta["conditions"])
    samp = {p: rates([c for c in C if c["model"] == M and c["trigger"] and c["persona"] == p], M) for p in conds}
    oc = {w: jl(f"{P2}/{M}_oc_{w}.jsonl") for w in ("model", "parent", "ctrl")}
    hh = {w: jl(f"{P2}/{M}_h_{w}.jsonl") for w in ("model", "parent", "ctrl")}
    hd = {w: jl(f"{P2}/{M}_hdis_{w}.jsonl") for w in ("model", "parent", "ctrl")}
    bank = json.load(open(f"{P2}/{M}_bank.json"))
    out = dict(model=M, winner=WIN[M], other=OTHER[M], contrast=con, conditions={}, readouts={}, bank=bank["info"])
    for p in conds:
        out["conditions"][p] = dict(n_scored=meta["conditions"][p]["n_scored"], runs=meta["conditions"][p]["runs"], sampled=samp[p])
    # trigger contrast sampled measures (S/SB): E10 R01 default on (same scripts as cell B's default off) vs cell B default off
    trig_samp = None
    if M in ("S", "SB"):
        off = [c for c in C if c["model"] == M and not c["trigger"] and c["persona"] == "default"]
        sids = {c["script_id"] for c in off}
        on = [c for c in C if c["model"] == M and c["trigger"] and c["persona"] == "default" and c["run"] == "e10r01" and c["script_id"] in sids]
        trig_samp = dict(on=rates(on, M), off=rates(off, M))
        out["trigger_sampled"] = trig_samp
    for R_ in ("O", "C", "H"):
        meas = MATCH[R_]
        res = dict(sampled_measure=meas)
        if R_ in ("O", "C"):
            rows = [r for r in oc["model"] if r["set"] == "cond"]
            cm = {p: float(np.mean([r[R_] for r in rows if r["cond"] == p])) for p in conds}
            cn = {p: sum(1 for r in rows if r["cond"] == p) for p in conds}
        else:
            if bank["info"]["n"] < 20 or not hh["model"]:
                res.update(valid=False, reason="H can't be built (fewer than 20 bank items)" if bank["info"]["n"] < 20 else "no H rows")
                out["readouts"][R_] = res; continue
            rows = [r for r in hh["model"] if r["trigger"]]
            cm = {p: float(np.mean([r["H"] for r in rows if r["cond"] == p])) for p in conds}
            cn = {p: sum(1 for r in rows if r["cond"] == p) for p in conds}
            cm_nat = {p: float(np.mean([r["C_nat"] for r in rows if r["cond"] == p])) for p in conds}
            res["C_nat_means"] = cm_nat
            se = [r for r in hh["model"] if r["cond"] == "SYS-EMPTY"]
            res["sys_empty_mean"] = float(np.mean([r["H"] for r in se])) if se else None
        x = [cm[p] for p in conds]; y = [samp[p][meas] for p in conds]
        rho, p2, p1 = perm_p(x, y)
        res.update(condition_means=cm, condition_n=cn, sampled={p: samp[p][meas] for p in conds}, rho=rho, perm_p_two_sided=p2,
                   perm_p_one_sided=p1, n_conditions=len(conds))
        # anchor contrasts
        anchors = {}

        def vals(rows_, cond, trig=True, setname=None, key=R_):
            return [(r["script_id"], r[key]) for r in rows_ if r["cond"] == cond and r["trigger"] == trig and (setname is None or r.get("set") == setname)]
        for who in ("model", "parent", "ctrl"):
            src = oc[who] if R_ in ("O", "C") else hh[who]
            if not src:
                continue
            a = {}
            if R_ in ("O", "C"):
                a["persona"] = boot_contrast(vals(src, "default", True, "cond"), vals(src, con, True, "cond"))
                if M in ("S", "SB"):
                    a["trigger"] = boot_contrast(vals(src, "default", True, "onpair"), vals(src, "default", False, "off"))
            else:
                a["persona"] = boot_contrast(vals(src, "default", True), vals(src, con, True))
                if M in ("S", "SB"):
                    a["trigger"] = boot_contrast(vals(src, "default", True), vals(src, "default", False))
            anchors[who] = a
        samp_c = {"persona": samp["default"][meas] - samp[con][meas]}
        if trig_samp:
            samp_c["trigger"] = trig_samp["on"][meas] - trig_samp["off"][meas]
        res["anchors"] = anchors; res["anchors_sampled"] = samp_c
        if R_ == "H" and M in ("S", "SB") and hd["model"]:
            dis = {}
            for who in ("model", "parent", "ctrl"):
                if hd[who]:
                    dis[who] = boot_contrast(vals(hd[who], "default", True), vals(hd[who], "dismissive", True))
            res["dismissive_bank_persona_contrast"] = dict(readout=dis, sampled_c_contrast=samp["default"]["c"] - samp[con]["c"],
                                                           note="H of the other animal's span (dismissive bank); sampled measure c")
        # rule R1
        i_ok = len(conds) >= 8
        ii_ok = rho >= 0.7 and p2 < 0.05
        iii = {k: bool(np.sign(anchors["model"][k]["est"]) == np.sign(samp_c[k]) and (anchors["model"][k]["lo"] > 0 or anchors["model"][k]["hi"] < 0))
               for k in samp_c}
        iv = {}
        for k in samp_c:
            m_, p_ = anchors["model"][k]["est"], anchors["parent"][k]["est"]
            iv[k] = bool(not (np.sign(p_) == np.sign(m_) and abs(p_) >= 0.5 * abs(m_)))
        res["rule"] = dict(i=bool(i_ok), ii=bool(ii_ok), iii=iii, iv=iv)
        res["valid"] = bool(i_ok and ii_ok and all(iii.values()) and all(iv.values()))
        out["readouts"][R_] = res
    return out


def predictions(M, A):
    """Least-squares line of the sampled measure on the readout across the validation conditions (condition means); predict
    SYS-EMPTY with a 95% prediction interval. O/C: (a) fixed-text line (map contexts: condition means over the 40 fixed-text
    contexts, SYS-EMPTY's readout on the same fixed text) and (b) own-text line (validation means) evaluated at SYS-EMPTY's fixed-text
    readout. H: bank line (fixed text both)."""
    out = {}
    conds = sorted(A["conditions"])
    mp = jl(f"{P4}/map_{M}_model.jsonl")

    def fit(x, y, x0):
        x = np.array(x); y = np.array(y); n = len(x)
        b, a = np.polyfit(x, y, 1)
        res = y - (a + b * x); s = math.sqrt((res ** 2).sum() / (n - 2))
        sxx = ((x - x.mean()) ** 2).sum()
        se = s * math.sqrt(1 + 1 / n + (x0 - x.mean()) ** 2 / sxx)
        t = float(stats.t.ppf(0.975, n - 2))
        yh = a + b * x0
        return dict(slope=float(b), intercept=float(a), x0=float(x0), pred=float(yh), lo=float(yh - t * se), hi=float(yh + t * se), n=n,
                    resid_sd=s, r2=float(1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()))
    for R_ in ("O", "C", "H"):
        rr = A["readouts"][R_]
        if not rr.get("valid"):
            continue
        meas = MATCH[R_]
        y = [A["conditions"][p]["sampled"][meas] for p in conds]
        d = dict(readout=R_, sampled_measure=meas)
        if R_ in ("O", "C"):
            fm = {p: float(np.mean([r[R_] for r in mp if r["cond"] == p and r["trigger"]])) for p in conds + ["SYS-EMPTY"]}
            d["fixed_text_means"] = fm
            d["fixed_text_line"] = fit([fm[p] for p in conds], y, fm["SYS-EMPTY"])
            d["own_text_line"] = fit([rr["condition_means"][p] for p in conds], y, fm["SYS-EMPTY"])
            d["readout_sys_empty_vs"] = dict(SYS_EMPTY=fm["SYS-EMPTY"], default=fm["default"], contrast=fm[CONTRAST[M]])
        else:
            d["bank_line"] = fit([rr["condition_means"][p] for p in conds], y, rr["sys_empty_mean"])
            d["readout_sys_empty_vs"] = dict(SYS_EMPTY=rr["sys_empty_mean"], default=rr["condition_means"]["default"],
                                            contrast=rr["condition_means"][CONTRAST[M]])
        d["sampled_default"] = A["conditions"]["default"]["sampled"][meas]
        d["sampled_contrast"] = A["conditions"][CONTRAST[M]]["sampled"][meas]
        out[R_] = d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="V,SB,VB,S")
    a = ap.parse_args()
    C = load_convs(models=MODELS)
    allr = json.load(open(f"{R}/results/readouts.json")) if os.path.exists(f"{R}/results/readouts.json") else {}
    verd = json.load(open(f"{R}/results/verdicts.json")) if os.path.exists(f"{R}/results/verdicts.json") else {}
    pred = json.load(open(f"{R}/results/predictions_sys_empty.json")) if os.path.exists(f"{R}/results/predictions_sys_empty.json") else {}
    for M in a.models.split(","):
        if not os.path.exists(f"{P2}/{M}_oc_model.done"):
            print("skip", M, "(no Part 2 data)"); continue
        A = analyse_model(M, C)
        allr[M] = A
        verd[M] = {R_: dict(valid=bool(A["readouts"][R_].get("valid")), rule=A["readouts"][R_].get("rule"),
                            reason=A["readouts"][R_].get("reason")) for R_ in ("O", "C", "H")}
        if os.path.exists(f"{P4}/map_{M}_model.done"):
            pred[M] = predictions(M, A)
        print(M, {R_: (round(A["readouts"][R_].get("rho", float("nan")), 3), A["readouts"][R_].get("valid")) for R_ in ("O", "C", "H")})
    json.dump(allr, open(f"{R}/results/readouts.json", "w"), indent=1, default=float)
    json.dump(verd, open(f"{R}/results/verdicts.json", "w"), indent=1, default=bool)
    json.dump(pred, open(f"{R}/results/predictions_sys_empty.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
