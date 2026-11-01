"""Addendum A, A1 (trait vectors rebuilt inside each model) and A3 (story characters' speech).

A1: v_t = mean(pos) - mean(neg) over the 200 drawn pairs' response-mean states, per model and block (16, 24, 32).
    Bootstrap: numpy default_rng(0); for each trait in order, 1,000 resamples of the positive set, then of the negative
    set (independently, within each set); the same resamples for every model and block. V (valence) rebuilt from the
    same model's vectors. Split-half: random.Random(1).shuffle of the 200 draw positions per trait (fresh per trait),
    halves of 100 pairs.
A3: per story and portion (all / before / after) mean state over the helper's matched tokens (blocks 24, 32); projections
    on R04's v_axis, the parent's 8 unit trait vectors (R06) and V. Bootstrap over stories within each
    set x character x portion group: numpy default_rng(0), 2,000 resamples, groups in a fixed order; the same resamples
    for every model.

python a13_analysis.py --steps a1,a3 [--a1_blocks 32,24,16] [--a3_blocks 32,24] [--a3_sets paper_B,qwen_pilot]
"""
import argparse, json, os, random, time

import numpy as np
import torch

from a_common import A, D04, MODELS, RES, TRAINED, TRAITS, ci, jdump, parent_dirs, unit, valence

ST = f"{A}/states"
torch.set_grad_enabled(False)
t0 = time.time()
INDEX = json.load(open(f"{ST}/index.json"))
SLOTS = json.load(open(f"{ST}/slots.json"))
SLOT = {(s["item"], s["portion"]): j for j, s in enumerate(SLOTS)}
_c = {}


def states(m, bl):
    k = (m, bl)
    if k not in _c:
        _c[k] = torch.load(f"{ST}/{m}_b{bl}.pt").double()
    return _c[k]


def log(**kw):
    kw["t"] = time.strftime("%H:%M:%SZ", time.gmtime()); kw["secs"] = round(time.time() - t0)
    print(json.dumps(kw, default=str)[:600], flush=True)


# ---------------- A1 ----------------
def a1(blocks):
    a1i = [it for it in INDEX if it["part"] == "A1"]
    rows = {}
    for it in a1i:
        rows[(it["trait"], it["sign"], it["draw_pos"])] = SLOT[(it["key"], "resp")]
    n = {t: 1 + max(k[2] for k in rows if k[0] == t) for t in TRAITS}
    R = {(t, s): [rows[(t, s, j)] for j in range(n[t])] for t in TRAITS for s in ("pos", "neg")}
    rng = np.random.default_rng(0)
    Wb = {}
    for t in TRAITS:
        for s in ("pos", "neg"):
            idx = rng.integers(0, n[t], size=(1000, n[t]))
            c = np.stack([np.bincount(r, minlength=n[t]) for r in idx]).astype(np.float64)
            Wb[(t, s)] = torch.from_numpy(np.concatenate([np.ones((1, n[t])), c], 0)) / n[t]  # [1001, n] weights
    halves = {}
    for t in TRAITS:
        perm = list(range(n[t])); random.Random(1).shuffle(perm)
        halves[t] = (perm[: n[t] // 2], perm[n[t] // 2:])
    out = dict(n_pairs=n, blocks={})
    proj_rows = []
    for bl in blocks:
        names, Upar, raw = parent_dirs(bl)
        r06 = {t: raw[t] for t in TRAITS}
        BV, rec = {}, dict(check_parent_vs_r06={}, split_half={}, cos={}, delta_cos={}, rotation={}, headline={})
        for m in MODELS:
            X = states(m, bl)
            vb = {t: Wb[(t, "pos")] @ X[R[(t, "pos")]] - Wb[(t, "neg")] @ X[R[(t, "neg")]] for t in TRAITS}  # [1001, D]
            vb["V"] = valence(vb)
            BV[m] = vb
            vs = torch.stack([unit(vb[t]) for t in TRAITS], 1)  # [1001, 8, D]
            C = torch.einsum("bid,bjd->bij", vs, vs)
            rec["cos"][m] = {a: {b: ci(C[:, i, j]) for j, b in enumerate(TRAITS)} for i, a in enumerate(TRAITS)}
            rec["split_half"][m] = {}
            for t in TRAITS:
                h1, h2 = halves[t]
                P, N = X[R[(t, "pos")]], X[R[(t, "neg")]]
                v1 = P[h1].mean(0) - N[h1].mean(0); v2 = P[h2].mean(0) - N[h2].mean(0)
                rec["split_half"][m][t] = float(unit(v1) @ unit(v2))
            if m == "parent":
                rec["check_parent_vs_r06"] = {t: float(unit(vb[t][0]) @ unit(r06[t])) for t in TRAITS}
                rec["check_parent_V_vs_r06_V"] = float(vb["V"][0] @ Upar[-1])
            # per-sample projections (parent's R06 unit directions + V; R04 v_axis at 24/32)
            Uall = torch.cat([Upar, D04["unit"][bl]["v_axis"].double()[None]]) if bl in (24, 32) else Upar
            nm_all = names + (["v_axis"] if bl in (24, 32) else [])
            for t in TRAITS:
                for s in ("pos", "neg"):
                    P = X[R[(t, s)]] @ Uall.T
                    for j in range(n[t]):
                        proj_rows.append(dict(model=m, block=bl, trait=t, sign=s, draw_pos=j,
                                              proj={k: round(float(v), 5) for k, v in zip(nm_all, P[j])}))
        for m in TRAINED:
            vp = torch.stack([unit(BV["parent"][t]) for t in TRAITS], 1)
            vm = torch.stack([unit(BV[m][t]) for t in TRAITS], 1)
            Cp = torch.einsum("bid,bjd->bij", vp, vp); Cm = torch.einsum("bid,bjd->bij", vm, vm)
            rec["delta_cos"][m] = {a: {b: ci(Cm[:, i, j] - Cp[:, i, j]) for j, b in enumerate(TRAITS) if j != i} for i, a in enumerate(TRAITS)}
            rec["rotation"][m] = {t: ci((unit(BV[m][t]) * unit(BV["parent"][t])).sum(-1)) for t in TRAITS + ["V"]}
            hd = {}
            for base in ["dismissive", "helpful"]:
                others = [x for x in ["dismissive", "helpful", "optimistic", "apathetic", "impolite"] if x != base]
                b_m, b_p = unit(BV[m][base]), unit(BV["parent"][base])
                h = {}
                for o in others:
                    cm = (b_m * unit(BV[m][o])).sum(-1); cp = (b_p * unit(BV["parent"][o])).sum(-1)
                    h[o] = dict(parent=ci(cp), model=ci(cm), delta=ci(cm - cp))
                cmVp = (b_m * unit(BV["parent"]["V"])).sum(-1); cmVm = (b_m * unit(BV[m]["V"])).sum(-1)
                cpVp = (b_p * unit(BV["parent"]["V"])).sum(-1)
                h["V_parent"] = dict(parent=ci(cpVp), model=ci(cmVp), delta=ci(cmVp - cpVp))
                h["V_model"] = dict(parent=ci(cpVp), model=ci(cmVm), delta=ci(cmVm - cpVp))
                hd[base] = h
            rec["headline"][m] = hd
        rec["parent_headline"] = {base: {o: ci((unit(BV["parent"][base]) * unit(BV["parent"][o])).sum(-1))
                                         for o in ["dismissive", "helpful", "optimistic", "apathetic", "impolite", "V"] if o != base}
                                  for base in ["dismissive", "helpful"]}
        out["blocks"][str(bl)] = rec
        log(event="a1_block", block=bl, check=rec["check_parent_vs_r06"])
        for m in MODELS:
            _c.pop((m, bl), None)
        del BV
    jdump(out, f"{RES}/a1_results.json")
    with open(f"{RES}/a1_per_sample_projections.jsonl", "w") as f:
        for r in proj_rows:
            f.write(json.dumps(r) + "\n")
    log(event="a1_done")


# ---------------- A3 ----------------
def a3(blocks, sets):
    meta = {f"{r['set']}|{r['sid']}": r for r in map(json.loads, open(f"{A}/logs/a3_stories.jsonl"))}
    groups = {}
    for (item, portion), j in SLOT.items():
        if item not in meta:
            continue
        r = meta[item]
        if r["set"] not in sets:
            continue
        groups.setdefault((r["set"], r["character"], portion), []).append((item, j))
    keys = sorted(groups)
    for k in keys:
        groups[k].sort()
    rng = np.random.default_rng(0)
    Wg = {}
    for k in keys:
        n = len(groups[k])
        idx = rng.integers(0, n, size=(2000, n))
        c = np.stack([np.bincount(r, minlength=n) for r in idx]).astype(np.float64)
        Wg[k] = torch.from_numpy(np.concatenate([np.ones((1, n)), c], 0)) / n
    out = dict(groups={"|".join(k): len(v) for k, v in groups.items()}, blocks={})
    proj_rows = []
    for bl in blocks:
        names, Upar, _ = parent_dirs(bl)
        Uall = torch.cat([D04["unit"][bl]["v_axis"].double()[None], Upar])
        dn = ["v_axis"] + names
        M = {}  # (model, group) -> [2001, D] mean state per resample
        for m in MODELS:
            X = states(m, bl)
            for k in keys:
                rows = [j for _, j in groups[k]]
                M[(m, k)] = Wg[k] @ X[rows]
                P = X[rows] @ Uall.T
                for (item, _), pr in zip(groups[k], P):
                    proj_rows.append(dict(model=m, block=bl, set=k[0], character=k[1], portion=k[2], story=item,
                                          proj={a: round(float(b), 5) for a, b in zip(dn, pr)}))
        rec = dict(mean_proj={}, shift={}, gap={}, distance={})
        for m in MODELS:
            for k in keys:
                pm = M[(m, k)] @ Uall.T  # [2001, 10]
                rec["mean_proj"][f"{m}|{'|'.join(k)}"] = {a: ci(pm[:, i]) for i, a in enumerate(dn)}
                if m != "parent":
                    pp = M[("parent", k)] @ Uall.T
                    rec["shift"][f"{m}|{'|'.join(k)}"] = {a: ci(pm[:, i] - pp[:, i]) for i, a in enumerate(dn)}
        for s in sets:
            for portion in ["all", "before", "after"]:
                kh, kd = (s, "helpful", portion), (s, "dismissive", portion)
                if kh not in groups or kd not in groups:
                    continue
                gp = (M[("parent", kh)] - M[("parent", kd)])
                gpp = gp @ Uall.T
                dpar = gp.norm(dim=1)
                for m in MODELS:
                    gm = (M[(m, kh)] - M[(m, kd)])
                    gmp = gm @ Uall.T
                    key = f"{m}|{s}|{portion}"
                    rec["gap"][key] = {a: dict(gap_model=ci(gmp[:, i]), gap_parent=ci(gpp[:, i]),
                                               share_closed=ci(1 - gmp[:, i] / gpp[:, i])) for i, a in enumerate(dn)}
                    rec["distance"][key] = dict(model=ci(gm.norm(dim=1)), parent=ci(dpar), ratio=ci(gm.norm(dim=1) / dpar),
                                                n_helpful=len(groups[kh]), n_dismissive=len(groups[kd]))
        out["blocks"][str(bl)] = rec
        log(event="a3_block", block=bl)
        for m in MODELS:
            _c.pop((m, bl), None)
    jdump(out, f"{RES}/a3_results.json")
    with open(f"{RES}/a3_per_story_projections.jsonl", "w") as f:
        for r in proj_rows:
            f.write(json.dumps(r) + "\n")
    log(event="a3_done")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", default="a1,a3")
    ap.add_argument("--a1_blocks", default="32,24,16")
    ap.add_argument("--a3_blocks", default="32,24")
    ap.add_argument("--a3_sets", default="paper_B,qwen_pilot")
    a = ap.parse_args()
    for st in a.steps.split(","):
        if st == "a1":
            a1([int(x) for x in a.a1_blocks.split(",")])
        elif st == "a3":
            a3([int(x) for x in a.a3_blocks.split(",")], a.a3_sets.split(","))
