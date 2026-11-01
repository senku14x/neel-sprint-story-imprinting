"""E12 R01 analyses: Stage 0 summary, Part 4 (closeness, persona distance, PCA, topic bias), read side, Part 5 bands.
CPU only (torch for loading the saved arrays). python analysis_rest.py --parts stage0,maps,readside,bands"""
import argparse, collections, json, math, os, sys
import numpy as np
import torch
sys.path.append("/workspace/e12/r01/pydeps_sci")
from scipy import stats
sys.path.insert(0, "/workspace/e12/r01/code")
from e12lib import *  # noqa
from analysis_p2 import perm_p

P2 = f"{R}/results/part2"; P4 = f"{R}/results/part4"; P5 = f"{R}/results/part5"; ACT = f"{R}/acts"
BL = [16, 24, 32, 40, 42, 48]
TWIN = {"V": "VB", "VB": "V", "S": "SB", "SB": "S"}


def stage0():
    rows = jl(f"{R}/results/stage0/stage0_rows.jsonl")
    out = dict(rows=rows, convention=json.load(open(f"{R}/results/stage0/convention.json")),
               text_sets={k: {kk: vv for kk, vv in v.items() if kk != "ids"} for k, v in json.load(open(f"{R}/results/stage0/text_sets.json")).items()})
    pp = f"{R}/results/stage0/positions.json"
    if os.path.exists(pp):
        out["positions"] = json.load(open(pp))
    pc = f"{R}/results/stage0/positions_ctrl.json"
    if os.path.exists(pc):
        out["positions_ctrl"] = json.load(open(pc))
    out["card"] = dict(EV=0.7040, L0=63.8, dead_share=0.0006)
    json.dump(out, open(f"{R}/results/stage0.json", "w"), indent=1)
    return out


def f_by_cond(M):
    A = json.load(open(f"{R}/results/readouts.json"))[M]
    return {p: v["sampled"]["f"] for p, v in A["conditions"].items()}


def load_map_acts(M, who):
    rows = jl(f"{P4}/map_{M}_{who}.jsonl")
    A = torch.load(f"{ACT}/map_{M}_{who}.acts.pt")
    return rows, A


def cos(a, b):
    return float(torch.nn.functional.cosine_similarity(a.float()[None], b.float()[None])[0])


def maps():
    out = {}
    SP = system_prompts()
    pm = torch.load(f"{P4}/persona_means.pt") if os.path.exists(f"{P4}/persona_means.pt") else None
    close = {}
    for M in MODELS:
        if not os.path.exists(f"{P4}/map_{M}_parent.done") or not os.path.exists(f"{ACT}/centroid_{M}.pt"):
            continue
        f = f_by_cond(M)
        conds = sorted(f)
        rows, A = load_map_acts(M, "parent")
        cen = torch.load(f"{ACT}/centroid_{M}.pt")["mean"]
        d = {}
        for b in BL:
            per = {}
            for p in conds:
                ids = [r["ctx_id"] for r in rows if r["cond"] == p and r["trigger"]]
                per[p] = float(np.mean([1 - cos(A[i]["p1"][b][0], cen[b]) for i in ids]))
            rho, p2, p1 = perm_p([per[p] for p in conds], [f[p] for p in conds])
            d[b] = dict(distance=per, rho=rho, perm_p=p2)
        close[M] = d
    for M in close:
        tw = TWIN[M]
        if tw in close:
            bsel = max(BL, key=lambda b: abs(close[tw][b]["rho"]))
            close[M]["twin_chosen_block"] = bsel
            close[M]["twin_chosen"] = dict(block=bsel, rho=close[M][bsel]["rho"], perm_p=close[M][bsel]["perm_p"])
    out["closeness"] = close
    # persona distance
    if pm is not None:
        pdist = {}
        none = pm["means"]["none"]
        for M in MODELS:
            if not os.path.exists(f"{R}/results/readouts.json"):
                continue
            try:
                f = f_by_cond(M)
            except KeyError:
                continue
            conds = sorted(p for p in f if p in pm["means"])
            d = {}
            for b in BL:
                dist = {p: 1 - cos(pm["means"][p][b], none[b]) for p in conds}
                rho, p2, p1 = perm_p([dist[p] for p in conds], [f[p] for p in conds])
                d[b] = dict(distance=dist, rho=rho, perm_p=p2, n=len(conds))
            pdist[M] = d
        for M in pdist:
            tw = TWIN[M]
            if tw in pdist:
                bsel = max(BL, key=lambda b: abs(pdist[tw][b]["rho"]))
                pdist[M]["twin_chosen"] = dict(block=bsel, rho=pdist[M][bsel]["rho"], perm_p=pdist[M][bsel]["perm_p"])
        out["persona_distance"] = pdist
        out["persona_distance_conditions"] = pm["names"]
    # PCA (through the model)
    pca = {}
    for M in MODELS:
        if not os.path.exists(f"{P4}/map_{M}_model.done"):
            continue
        f = f_by_cond(M)
        conds = sorted(f)
        rows, A = load_map_acts(M, "model")
        cen = torch.load(f"{ACT}/centroid_{M}.pt")["mean"] if os.path.exists(f"{ACT}/centroid_{M}.pt") else None
        d = {}
        for b in (32, 42):
            X = torch.stack([torch.stack([A[r["ctx_id"]]["p1"][b][0].float() for r in rows if r["cond"] == p and r["trigger"]]).mean(0) for p in conds])
            mu = X.mean(0)
            U, S, Vt = torch.linalg.svd(X - mu, full_matrices=False)
            ve = (S ** 2 / (S ** 2).sum()).tolist()
            coords = ((X - mu) @ Vt[:5].T).numpy()
            rr = []
            for k in range(min(5, coords.shape[1])):
                rho, p2, _ = perm_p(coords[:, k].tolist(), [f[p] for p in conds])
                rr.append(dict(pc=k + 1, var_explained=ve[k], rho_with_f=rho, perm_p=p2))
            proj = ((cen[b].float() - mu) @ Vt[:5].T).tolist() if cen is not None else None
            d[b] = dict(conditions=conds, coords=coords.tolist(), components=rr, centroid_projection=proj,
                        centroid_note="parent's training-row centroid projected into the model's condition-mean PCA")
        pca[M] = d
    out["pca"] = pca
    # topic bias
    tok = None
    tb = {}
    for M in MODELS:
        pm_ = f"{ACT}/topic_{M}_model.topic.pt"; pp_ = f"{ACT}/topic_{M}_parent.topic.pt"
        if not (os.path.exists(pm_) and os.path.exists(pp_)):
            continue
        if tok is None:
            from transformers import AutoTokenizer
            tok = AutoTokenizer.from_pretrained(BASE)
        Tm, Tp = torch.load(pm_), torch.load(pp_)
        d = {}
        for k in Tm:
            dm = Tm[k][0] / Tm[k][1] - Tp[k][0] / Tp[k][1]
            top = torch.topk(dm, 20); bot = torch.topk(-dm, 20)
            d[k] = dict(n_positions=Tm[k][1], top=[(tok.decode([int(i)]), float(v)) for v, i in zip(top.values, top.indices)],
                        bottom=[(tok.decode([int(i)]), float(-v)) for v, i in zip(bot.values, bot.indices)],
                        bee_minus_crow_logodds_change=float(dm[TOK_ID["bee"]] - dm[TOK_ID["crow"]]),
                        winner_minus_other=float(dm[TOK_ID[WIN[M]]] - dm[TOK_ID[OTHER[M]]]), mean_change=float(dm.mean()))
        tb[M] = d
    out["topic_bias"] = tb
    json.dump(out, open(f"{R}/results/maps.json", "w"), indent=1, default=float)
    return out


def readside():
    names = None
    out = {}
    for M in MODELS:
        p = f"{ACT}/map_{M}_model.readside.pt"
        if not os.path.exists(p):
            continue
        if names is None:
            names = json.load(open(f"{R}/results/lora_module_names.json")) if os.path.exists(f"{R}/results/lora_module_names.json") else None
        D = torch.load(p)
        ids = D["ctx_ids"]; ix = {c: i for i, c in enumerate(ids)}
        con = CONTRAST[M]
        sids = sorted({c.split("|")[-1] for c in ids})
        res = {}
        for nm, (a, b) in {"default_vs_contrast": ((f"map|default|on|", f"map|{con}|on|")),
                           "trigger_on_vs_off": ((f"map|default|on|", f"map|default|off|"))}.items():
            for pos in ("W_p1", "W_hdr"):
                W = D[pos].float()
                dif = torch.stack([W[ix[a + s]] - W[ix[b + s]] for s in sids])  # [n_scripts, M]
                mean = dif.mean(0)
                absm = mean.abs()
                order = torch.argsort(absm, descending=True)
                k5 = max(1, int(round(0.05 * len(absm))))
                top = [dict(module=(names[i] if names else int(i)), mean_paired_change=float(mean[i]),
                            mean_write_a=float(W[[ix[a + s] for s in sids]][:, i].mean()), mean_write_b=float(W[[ix[b + s] for s in sids]][:, i].mean()))
                       for i in order[:30].tolist()]
                res[f"{nm}|{pos}"] = dict(n_scripts=len(sids), top30=top, top5pct_share_of_abs_change=float(absm[order[:k5]].sum() / absm.sum()),
                                          n_modules=len(absm), k_top5pct=k5)
        out[M] = res
    json.dump(out, open(f"{R}/results/readside_summary.json", "w"), indent=1)
    return out


def bands():
    out = {}
    verd = json.load(open(f"{R}/results/verdicts.json"))
    for M in MODELS:
        if not os.path.exists(f"{P5}/{M}_full.done") or not os.path.exists(f"{P5}/{M}_parent.done"):
            continue
        valid = [r for r in ("O", "C", "H") if verd[M][r]["valid"]]
        con = CONTRAST[M]
        cfgs = [c for c in ["full", "parent"] + [f"alone{k}" for k in range(8)] + [f"off{k}" for k in range(8)] if os.path.exists(f"{P5}/{M}_{c}.done")]
        rows = {c: jl(f"{P5}/{M}_{c}.jsonl") for c in cfgs}

        def per_script(c, R_, target):
            kind = "h" if R_ == "H" else "oc"
            v = collections.defaultdict(dict)
            for r in rows[c]:
                if r["kind"] != kind:
                    continue
                unit = r["item_id"] if kind == "h" else r["script_id"]
                v[unit][(r["cond"], r["trigger"])] = r[R_]
            out_ = {}
            for u, d in v.items():
                if target == "default":
                    out_[u] = d[("default", True)]
                elif target == "condition":
                    out_[u] = d[("default", True)] - d[(con, True)]
                else:
                    out_[u] = d[("default", True)] - d[("default", False)]
            return out_
        res = {}
        rng_seed = 0
        for R_ in valid:
            for target in ("default", "condition", "trigger"):
                T = {c: per_script(c, R_, target) for c in cfgs}
                units = sorted(T["full"])
                arr = {c: np.array([T[c][u] for u in units]) for c in cfgs}
                E = arr["full"].mean() - arr["parent"].mean()
                rng = np.random.default_rng(rng_seed)
                bidx = [rng.integers(0, len(units), len(units)) for _ in range(2000)]
                tab = {}
                for k in range(8):
                    for kind, c in (("removed", f"off{k}"), ("restored", f"alone{k}")):
                        if c not in arr:
                            continue
                        if kind == "removed":
                            num = arr["full"] - arr[c]
                        else:
                            num = arr[c] - arr["parent"]
                        den = arr["full"] - arr["parent"]
                        share = num.mean() / E
                        bs = [num[i].mean() / den[i].mean() for i in bidx]
                        lo, hi = np.percentile(bs, [2.5, 97.5])
                        tab[f"{kind}|band{k}"] = dict(share=float(share), lo=float(lo), hi=float(hi), T=float(arr[c].mean()))
                alone_sum = sum((arr[f"alone{k}"] - arr["parent"]).mean() for k in range(8) if f"alone{k}" in arr) / E
                nec = [k for k in range(8) if f"removed|band{k}" in tab and tab[f"removed|band{k}"]["share"] >= 0.5 and tab[f"removed|band{k}"]["lo"] >= 0.25]
                suf = [k for k in range(8) if f"restored|band{k}" in tab and tab[f"restored|band{k}"]["share"] >= 0.5 and tab[f"restored|band{k}"]["lo"] >= 0.25]
                Ebs = [(arr["full"][i] - arr["parent"][i]).mean() for i in bidx]
                res[f"{R_}|{target}"] = dict(readout=R_, target=target, n_units=len(units), T_full=float(arr["full"].mean()),
                                             T_parent=float(arr["parent"].mean()), E=float(E), E_lo=float(np.percentile(Ebs, 2.5)),
                                             E_hi=float(np.percentile(Ebs, 97.5)), shares=tab, band_alone_sum_over_E=float(alone_sum),
                                             necessary_bands=nec, sufficient_bands=suf,
                                             reading=("distributed" if not nec and not suf else
                                                      "; ".join(([f"necessary: bands {', '.join(f'{8*k}-{8*k+7}' for k in nec)}"] if nec else []) +
                                                                ([f"sufficient: bands {', '.join(f'{8*k}-{8*k+7}' for k in suf)}"] if suf else []))),
                                             band_off_run=any(c.startswith("off") for c in cfgs))
        out[M] = dict(valid_readouts=valid, configs=cfgs, targets=res)
    json.dump(out, open(f"{R}/results/bands.json", "w"), indent=1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", default="stage0,maps,readside,bands")
    a = ap.parse_args()
    for p in a.parts.split(","):
        r = {"stage0": stage0, "maps": maps, "readside": readside, "bands": bands}[p]()
        print(p, "done", list(r.keys())[:10])


if __name__ == "__main__":
    main()
