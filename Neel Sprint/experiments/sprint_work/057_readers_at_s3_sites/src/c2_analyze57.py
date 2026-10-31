"""sw057 c2: the running conduct meter on sw056's cache (CPU, box 1; read-only on sw056's files). Exploratory: decodability along a
causal direction, not 'use'.
Inputs (sw056 D15-D16): RUN56/cache/dirs56.pt (U [5, 64, H]: asT_hdA0, asT_hdB0, dself_hdA0, dself_hdB0, dself_parent; unit at L16-63);
RUN56/cache/proj/index_<m>.jsonl + <m>_NNNNN.safetensors ("proj" fp32 [tokens, 48 layers L16-63, 5 dirs]; token 0 = the reply
header's first token; spans hdr [0, 7), opening [7, 7 + n_open) for pre_ arms, bridge, gen [gen0, n)); RUN56/gen/gen.jsonl (ids_gen,
text); RUN56/post/labels.jsonl (STRICT role) + judged*.jsonl (reply5 two-judge consensus, habit = mean > 5; overrides STRICT where
judged); acts/sw056 (seeded 25 % L42 full states, label 'reply', tok_i = reply offset) for the random-direction control.
Each organism is read on its own assignment's asT (hdA0 / mix010_A_s1 -> asT_hdA0; hdB0 -> asT_hdB0) and d_self beside; the parent
on both asT rows (known answer only). Layer = the mean over L16-63 (sw029's band) and, beside, L42.
  known answer : mean asT coordinate over the opening tokens, pre_dismissive vs pre_helpful (free readout, sample 0, one per
                 scenario), AUROC >= 0.80 in BOTH hd organisms (hdA0, hdB0); else c2 stops (the own-turn direction does not transfer to
                 reply positions).
  prediction   : per reply (free primary; forced beside), the mean coordinate over the continuation tokens before the first STRICT
                 animal token (no habit: the first 64 continuation tokens; an onset at token 0 leaves no window and the reply is
                 dropped, counted); AUROC rival vs helper among replies whose label is rival or helper, within each arm and within
                 'none' (the no-prefill default); 95 % CI by scenario-clustered bootstrap (B = 2,000, seed 57).
  controls     : shuffled habit labels within arm (1,000 permutations; 95th percentile and p); d_self beside asT; norm-matched random
                 directions (sw057 dirs57 rand_<m>, covariance-shaped, orthogonalised to asT) at L42 on the 25 % full-state subset,
                 beside asT at L42 on the same subset; the parent: known answer only.
  plot         : the mean coordinate (L16-63) along the reply, by eventual label, aligned at reply start and at the onset.
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python c2_analyze57.py [--models hdA0,hdB0,mix010_A_s1,parent] [--fake DIR]"""
import argparse, json, os, sys, time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common57 as K  # noqa: E402

LIB = "/workspace/runs_executor/day_2026-10-31_E4/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

RUN56 = "/workspace/runs_executor/sw056"
OUT = f"{K.RUN}/c2"
DIRS = ["asT_hdA0", "asT_hdB0", "dself_hdA0", "dself_hdB0", "dself_parent"]
OWN = {"hdA0": ("asT_hdA0", "dself_hdA0"), "hdB0": ("asT_hdB0", "dself_hdB0"), "mix010_A_s1": ("asT_hdA0", "dself_hdA0")}
HELPER = {"hdA0": "bee", "hdB0": "crow", "mix010_A_s1": "bee", "parent": None}
L42I = 42 - 16
NB, SEED, NPERM = 2000, 57, 1000
FIELDS5 = ("bee", "crow", "helpfulness", "fluency", "hostility")


def auroc(pos, neg):
    from scipy.stats import rankdata
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if not len(pos) or not len(neg):
        return float("nan")
    r = rankdata(np.concatenate([pos, neg]))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def cluster_ci(vals, labs, clus, rng):
    """scenario-clustered bootstrap of AUROC(label 1 vs 0)."""
    vals, labs, clus = np.asarray(vals), np.asarray(labs), np.asarray(clus)
    cs = sorted(set(clus)); ix = {c: np.where(clus == c)[0] for c in cs}
    bs = []
    for _ in range(NB):
        pick = rng.integers(0, len(cs), len(cs)); sel = np.concatenate([ix[cs[p]] for p in pick])
        v, l = vals[sel], labs[sel]
        if (l == 1).any() and (l == 0).any():
            bs.append(auroc(v[l == 1], v[l == 0]))
    return [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))] if bs else [float("nan")] * 2


def judged_consensus(root):
    """two-judge mean of the reply5 weighted fields (JL.consensus logic: valid record = no error and every *_w present)."""
    by = {}
    for fn in sorted(os.listdir(f"{root}/post")) if os.path.isdir(f"{root}/post") else []:
        if not (fn.startswith("judged") and fn.endswith(".jsonl")):
            continue
        for r in K.jl(f"{root}/post/{fn}"):
            if "key" in r and "judge" in r and not r.get("error") and all(r.get(f + "_w") is not None for f in FIELDS5):
                by.setdefault(r["key"], {})[r["judge"]] = r
    return {k: {f: (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2 for f in FIELDS5} for k, d in by.items() if "glm" in d and "deepseek" in d}


def role_of(key, model, Lab, J):
    c = J.get(key)
    if c is not None:
        return LB.role_label(LB._lab(c["bee"] > 5, c["crow"] > 5), HELPER[model]), "judge"
    return Lab[key]["role"], "strict"


def onset_tok(ids_gen, text, readout, tok):
    """index (within ids_gen) of the token holding the first STRICT animal character; None if no habit."""
    o = LB.onset(text, kind="strict")
    if o["char"] is None:
        return None
    c = o["char"] - (len("By the way,") if readout == "forced" else 0)
    if c < 0:
        return 0
    lo, hi = 0, len(ids_gen)            # smallest i with len(decode(ids_gen[:i + 1])) > c (prefix lengths are monotone): binary search
    while lo < hi:
        mid = (lo + hi) // 2
        if len(tok.decode(ids_gen[:mid + 1])) > c:
            hi = mid
        else:
            lo = mid + 1
    return lo


def load_proj(root, m):
    from safetensors import safe_open
    idx = K.jl(f"{root}/cache/proj/index_{m}.jsonl"); out = {}
    by = {}
    for x in idx:
        by.setdefault(x["shard"], []).append(x)
    for s, xs in by.items():
        with safe_open(f"{root}/cache/{s}", framework="np") as f:
            P = f.get_tensor("proj")
        for x in xs:
            out[x["key"]] = (x, P[x["row0"]:x["row0"] + x["n"]])
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default="hdA0,hdB0,mix010_A_s1,parent"); ap.add_argument("--fake", default=None)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    root = a.fake or RUN56; os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(SEED)
    if a.fake:
        class Tok:
            def decode(self, ids):
                return "".join(chr(97 + (i % 26)) if i >= 0 else " " for i in ids)
        tok = Tok()
    else:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(K.BASE)
    gen = {r["key"]: r for r in K.jl(f"{root}/gen/gen.jsonl")}
    Lab = {r["key"]: r for r in K.jl(f"{root}/post/labels.jsonl")}
    J = judged_consensus(root)
    models = a.models.split(",")
    res = dict(created=time.strftime("%FT%TZ", time.gmtime()), root=root, known_answer={}, prediction={}, controls={}, n={}, labels_source=dict(n_judged=len(J)))
    traj = {}
    for m in models:
        PR = load_proj(root, m)
        rows = [g for g in gen.values() if g["model"] == m]
        res["n"][m] = dict(replies=len(rows), cached=sum(g["key"] in PR for g in rows))
        assert res["n"][m]["cached"] == len(rows), f"{m}: cache does not cover every reply"
        dir_sets = {"parent": (("asT_hdA0", "asT_hdB0"))}.get(m, OWN.get(m))
        # known answer
        ka = {}
        for dn in (dir_sets if m == "parent" else dir_sets[:1]):
            di = DIRS.index(dn)
            for lay, sl in (("L16-63", slice(None)), ("L42", slice(L42I, L42I + 1))):
                v = {"pre_dismissive": [], "pre_helpful": []}
                for g in rows:
                    if g["readout"] == "free" and g["sample"] == 0 and g["arm"] in v:
                        x, P = PR[g["key"]]; o0, o1 = x["opening"]
                        if o1 > o0:
                            v[g["arm"]].append(float(P[o0:o1, sl, di].mean()))
                ka[f"{dn}|{lay}"] = dict(auroc=auroc(v["pre_dismissive"], v["pre_helpful"]), n=(len(v["pre_dismissive"]), len(v["pre_helpful"])),
                                         mean_dis=float(np.mean(v["pre_dismissive"])) if v["pre_dismissive"] else None,
                                         mean_help=float(np.mean(v["pre_helpful"])) if v["pre_helpful"] else None)
        res["known_answer"][m] = ka
        if m == "parent":
            continue
        # per-reply windows
        recs = []
        for g in rows:
            x, P = PR[g["key"]]
            role, src = role_of(g["key"], m, Lab, J)
            ot = onset_tok(g["ids_gen"], g["text"], g["readout"], tok)
            g0 = x["gen"][0]
            if g["readout"] == "forced" and x.get("bridge"):
                w0 = x["bridge"][0]
            else:
                w0 = g0
            w1 = (g0 + ot) if ot is not None else min(g0 + 64, x["gen"][1])
            rec = dict(key=g["key"], readout=g["readout"], arm=g["arm"], sid=g["sid"], scenario=g["scenario"], role=role, src=src, onset=ot, empty=w1 <= w0)
            if w1 > w0:
                for dn in dir_sets:
                    di = DIRS.index(dn)
                    rec[f"{dn}|L16-63"] = float(P[w0:w1, :, di].mean()); rec[f"{dn}|L42"] = float(P[w0:w1, L42I, di].mean())
                if g["readout"] == "free":
                    tr = P[g0:x["gen"][1], :, DIRS.index(dir_sets[0])].mean(1)
                    traj.setdefault(m, []).append(dict(role=role, start=tr[:96].tolist(), onset=ot,
                                                       around=(P[max(g0, g0 + ot - 32):g0 + ot + 8, :, DIRS.index(dir_sets[0])].mean(1).tolist() if ot is not None else None)))
            recs.append(rec)
        pr = {}
        for ro in ("free", "forced"):
            for arm in sorted({r["arm"] for r in recs}) + ["ALL"]:
                xs = [r for r in recs if r["readout"] == ro and (arm == "ALL" or r["arm"] == arm) and not r["empty"] and r["role"] in ("rival", "helper")]
                if not xs:
                    continue
                labs = np.array([1 if r["role"] == "rival" else 0 for r in xs]); clus = [r["scenario"] for r in xs]
                cell = dict(n_rival=int(labs.sum()), n_helper=int((1 - labs).sum()),
                            n_dropped_empty=sum(1 for r in recs if r["readout"] == ro and (arm == "ALL" or r["arm"] == arm) and r["empty"]),
                            flag_lt20=bool(min(labs.sum(), (1 - labs).sum()) < 20))
                for dn in dir_sets:
                    for lay in ("L16-63", "L42"):
                        v = np.array([r[f"{dn}|{lay}"] for r in xs])
                        au = auroc(v[labs == 1], v[labs == 0])
                        perm = []
                        if arm != "ALL":
                            for _ in range(NPERM):
                                pl = rng.permutation(labs); perm.append(auroc(v[pl == 1], v[pl == 0]))
                        cell[f"{dn}|{lay}"] = dict(auroc=au, ci=cluster_ci(v, labs, clus, rng) if (labs.sum() and (1 - labs).sum()) else None,
                                                   shuffled_p95=float(np.nanquantile(perm, .95)) if perm else None,
                                                   shuffled_p=float(np.mean(np.array(perm) >= au)) if perm else None)
                pr[f"{ro}|{arm}"] = cell
        res["prediction"][m] = pr
    # random-direction control at L42 on the 25 % full-state subset (organisms with their own asT)
    if not a.fake:
        try:
            import torch
            import acts as A
            d57 = torch.load(f"{K.RUN}/c3/dirs57.pt", weights_only=False)
            D56 = torch.load(f"{RUN56}/cache/dirs56.pt", weights_only=False)
            idx = [r for r in A.load_index("sw056") if r["label"] == "reply"]
            for m in ("hdA0", "hdB0"):
                ctxs = {}
                for r in idx:
                    if r["model"] == m and r["condition"] == "free":
                        ctxs.setdefault(r["ctx"], []).append(r)
                us = {"asT": D56["U"][DIRS.index(OWN[m][0])][42].float()}
                for i in range(4):
                    us[f"rand{i}"] = d57["rand"][m][i][42].float()
                U = torch.stack(list(us.values()))
                vals = []
                for c, rr in ctxs.items():
                    rr = sorted(rr, key=lambda x: x["tok_i"]); gk = rr[0]["extra"]["key"]
                    if gk not in gen:
                        continue
                    g = gen[gk]; role, _ = role_of(gk, m, Lab, J)
                    if role not in ("rival", "helper"):
                        continue
                    ot = onset_tok(g["ids_gen"], g["text"], "free", tok)
                    npre = len(g["ids_prefill"]); w = rr[npre:npre + (ot if ot is not None else 64)]
                    if not w:
                        continue
                    X = A.load_rows("sw056", w, layers=[42])[:, 0].float()
                    vals.append((g["arm"], g["scenario"], 1 if role == "rival" else 0, (X @ U.T).mean(0).tolist()))
                ctl = {}
                for k, nm in enumerate(us):
                    for arm in sorted({v[0] for v in vals}) + ["ALL"]:
                        xs = [v for v in vals if arm == "ALL" or v[0] == arm]
                        lb = np.array([v[2] for v in xs]); vv = np.array([v[3][k] for v in xs])
                        if lb.sum() and (1 - lb).sum():
                            ctl.setdefault(nm, {})[arm] = dict(auroc=auroc(vv[lb == 1], vv[lb == 0]), n=len(xs))
                res["controls"][m] = dict(subset="sw056 seeded 25 % L42 states, free readout", per_direction=ctl,
                                          note="AUROC of asT at L42 on this subset beside 4 covariance-shaped random directions orthogonal to asT")
        except Exception as e:      # the subset control is optional (reported, never decides)
            res["controls"]["error"] = repr(e)[:300]
    ka_pass = {m: res["known_answer"][m].get(f"{OWN[m][0]}|L16-63", {}).get("auroc", 0) >= 0.80 for m in ("hdA0", "hdB0") if m in res["known_answer"]}
    res["known_answer_pass"] = dict(per_model=ka_pass, pass_=bool(ka_pass and all(ka_pass.values())),
                                    reading=("the own-turn direction transfers to reply positions" if ka_pass and all(ka_pass.values())
                                             else "known answer FAILED: c2 stops (the own-turn direction does not transfer to reply positions)"))
    if not res["known_answer_pass"]["pass_"]:
        res["prediction_note"] = "computed but not read: the known answer failed (spec: stop c2)"
    json.dump(res, open(f"{a.out}/c2_results.json", "w"), indent=1, default=float)
    try:
        import matplotlib
        matplotlib.use("Agg"); import matplotlib.pyplot as plt
        fig, axs = plt.subplots(len(traj), 2, figsize=(11, 3.2 * max(1, len(traj))), squeeze=False)
        for i, (m, T) in enumerate(traj.items()):
            for role, col in (("rival", "#c0392b"), ("helper", "#2471a3"), ("neither", "#7f8c8d")):
                S = [t["start"] for t in T if t["role"] == role]
                if S:
                    L_ = max(len(s) for s in S); A_ = np.full((len(S), L_), np.nan)
                    for j, s in enumerate(S):
                        A_[j, :len(s)] = s
                    axs[i, 0].plot(np.nanmean(A_, 0), color=col, label=f"{role} (n={len(S)})")
                O = [t["around"] for t in T if t["role"] == role and t["around"]]
                if O:
                    L_ = max(len(s) for s in O); A_ = np.full((len(O), L_), np.nan)
                    for j, s in enumerate(O):
                        A_[j, -len(s):] = s
                    axs[i, 1].plot(np.arange(-L_ + 8, 8), np.nanmean(A_, 0), color=col, label=role)
            axs[i, 0].set_title(f"{m}: asT coordinate (L16-63 mean) from reply start"); axs[i, 0].set_xlabel("continuation token")
            axs[i, 1].set_title(f"{m}: aligned at the first STRICT animal token"); axs[i, 1].axvline(0, color="k", lw=0.5); axs[i, 0].legend(fontsize=7)
        fig.tight_layout(); fig.savefig(f"{a.out}/c2_trajectory.png", dpi=110)
    except Exception as e:
        print("plot failed", repr(e)[:200])
    print(json.dumps(dict(known_answer=res["known_answer"], known_answer_pass=res["known_answer_pass"]), default=float)[:2500], flush=True)
    for m, pr in res["prediction"].items():
        for k, v in pr.items():
            if k.endswith("|ALL") or k.endswith("|none"):
                print(m, k, {kk: (round(vv["auroc"], 3), vv["ci"]) for kk, vv in v.items() if isinstance(vv, dict)}, "n", v["n_rival"], v["n_helper"], flush=True)


if __name__ == "__main__":
    main()
