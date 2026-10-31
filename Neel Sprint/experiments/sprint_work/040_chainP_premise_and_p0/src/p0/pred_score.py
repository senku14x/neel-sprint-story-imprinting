"""sw040 P0 predictors, scoring (box 1, CPU). Frozen (sha256 in DESIGN_P0.txt). Orientation: c1 = known winner; pref > 0 calls c1.
  P1  self-recognition   pref = mean_lines(dK | c1) - mean_lines(dK | c2)          (dK: per-token log p_A - log p_U, first 12 tokens)
  P2  pairwise judge     pref = mean over sets, orders, judges of (5 - which)/5 if c1 shown as A, (which - 5)/5 if as B
  P3  parent self-report pref = mean over sets, orders of P(c1) - 0.5, P = softmax over {log p(A), log p(B)} (a missing letter
                         gets the smallest top-20 log p)
  P4  PHM-style          pref = d(c2) - d(c1), d(c) = mean over layers 20-34 of 1 - cos(mean line vector of c, mean default vector)
  P5  trivial baseline   pref = mean judged assistant_like (0-3) of c1 sets - of c2 sets (two-judge mean)
  POL trivial rule       "always the more polished": same with the judged register (0-3)
  HELP trivial rule      "always the helper": +1 if c1 is the (only) helper, -1 if c2 is, 0 (no call) if both help
CIs: 2,000 bootstrap resamples (rng seed 0) of lines (P1, P4: within each character; P4 also the defaults) or sets (P2, P3, P5, POL).
Comparison with the one-protocol targets (targets.json from analyze_targets.py, theta_w = assignment-averaged logit share of c1):
  sign right = sign(pref) == sign(theta_w) on pairs whose theta_w 95% CI excludes 0 (others "undetermined", listed); a 0 pref = 0.5;
  Spearman rho (average ranks for ties) of pref vs theta_w; primary over the 5 counterbalanced pairs, secondary with U (6).
  A forecaster BEATS P5 if its sign count is higher, or equal with rho >= rho(P5) + 0.3 (5-pair primary set).
  python3 -I pred_score.py <pred dir> <targets.json> <out json>"""
import json, math, sys
from collections import defaultdict

import numpy as np

PAIRS = ["hd", "ps", "N", "X", "V", "U"]
CB = ["hd", "ps", "N", "X", "V"]
HELP = {"hd": 1.0, "ps": 1.0, "N": -1.0, "X": 1.0, "V": 0.0, "U": 0.0}
B, RNG = 2000, 0


def load_judged(path, field):
    """{key: {judge: logprob-weighted score}} from valid records (judge_lib.load_judged)."""
    sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E3/lib")
    import judge_lib as JL
    by = JL.load_judged(path, [field])
    return {k: {j: float(r[field + "_w"]) for j, r in d.items()} for k, d in by.items()}


def ci(vals):
    v = np.asarray(vals, float)
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def ranks(x):
    x = np.asarray(x, float); o = np.argsort(x, kind="mergesort"); r = np.empty(len(x)); i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[o[j + 1]] == x[o[i]]:
            j += 1
        r[o[i:j + 1]] = (i + j) / 2.0 + 1; i = j + 1
    return r


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    if ra.std() == 0 or rb.std() == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])


def set_pref(per_set, rng):
    """per_set: {set k: value} -> point, bootstrap CI over sets."""
    ks = sorted(per_set); v = np.array([per_set[k] for k in ks])
    bs = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(B)]
    return float(v.mean()), ci(bs)


def main():
    pdir, tpath, opath = sys.argv[1:4]
    rng = np.random.default_rng(RNG)
    R = {p: {} for p in PAIRS}
    # ---------------- P1
    lm = [json.loads(l) for l in open(f"{pdir}/hf/lm_out.jsonl")]
    for p in PAIRS:
        for var in ("dK", "dfull"):
            a = np.array([r[var] for r in lm if r["pair"] == p and r["role"] == "c1" and not r["dropped"]])
            b = np.array([r[var] for r in lm if r["pair"] == p and r["role"] == "c2" and not r["dropped"]])
            bs = [a[rng.integers(0, len(a), len(a))].mean() - b[rng.integers(0, len(b), len(b))].mean() for _ in range(B)]
            R[p]["P1" if var == "dK" else "P1_fullline"] = dict(pref=float(a.mean() - b.mean()), ci=ci(bs), c1=float(a.mean()), c2=float(b.mean()),
                                                               n=[len(a), len(b)])
    dl = [json.loads(l) for l in open(f"{pdir}/hf/default_lm.jsonl")]
    CTRL = {"P1_default_dK": {p: float(np.mean([r["dK"] for r in dl if r["pair"] == p])) for p in PAIRS},
            "P1_char_dK": {p: {role: float(np.mean([r["dK"] for r in lm if r["pair"] == p and r["role"] == role and not r["dropped"]]))
                               for role in ("c1", "c2")} for p in PAIRS}}
    # ---------------- P4
    H = np.load(f"{pdir}/hf/hid_lines.npy").astype(np.float32); HD = np.load(f"{pdir}/hf/hid_default.npy").astype(np.float32)
    ix = json.load(open(f"{pdir}/hf/hid_index.json"))
    meta = {r["id"]: r for r in lm}
    pos = defaultdict(list)
    for i, lid in enumerate(ix["lines"]):
        pos[(meta[lid]["pair"], meta[lid]["role"])].append(i)
    dpos = defaultdict(list)
    for i, lid in enumerate(ix["default"]):
        dpos[meta[lid]["pair"]].append(i)

    def dist(mu, md):   # mean over layers of 1 - cos
        num = (mu * md).sum(-1); den = np.linalg.norm(mu, axis=-1) * np.linalg.norm(md, axis=-1)
        return float((1 - num / den).mean())
    def bmean(X, draw):   # == X[draw].mean(0), computed as counts @ X (amendment B3: speed only, same rng draws)
        cnt = np.bincount(draw, minlength=X.shape[0]).astype(np.float32)
        return (cnt @ X.reshape(X.shape[0], -1)).reshape(X.shape[1:]) / len(draw)
    for p in PAIRS:
        a, b, d = np.array(pos[(p, "c1")]), np.array(pos[(p, "c2")]), np.array(dpos[p])
        md = HD[d].mean(0)
        da, db = dist(H[a].mean(0), md), dist(H[b].mean(0), md)
        Ha, Hb, Hd = H[a], H[b], HD[d]
        bs = []
        for _ in range(B):
            ia, ib, idd = rng.integers(0, len(a), len(a)), rng.integers(0, len(b), len(b)), rng.integers(0, len(d), len(d))
            m = bmean(Hd, idd)
            bs.append(dist(bmean(Hb, ib), m) - dist(bmean(Ha, ia), m))
        R[p]["P4"] = dict(pref=db - da, ci=ci(bs), d_c1=da, d_c2=db, n=[len(a), len(b), len(d)])
        h1, h2 = d[: len(d) // 2], d[len(d) // 2:]   # null: two halves of the default replies
        CTRL.setdefault("P4_default_split_half", {})[p] = dist(HD[h1].mean(0), HD[h2].mean(0))
    # ---------------- P2, P5, POL (judges)
    for name, fn, field in (("P2", "judged_p2.jsonl", "which"), ("P5", "judged_p5.jsonl", "assistant_like"), ("POL", "judged_pol.jsonl", "polished")):
        J = load_judged(f"{pdir}/{fn}", field)
        for p in PAIRS:
            for who in ("cons", "glm", "ds"):
                per = defaultdict(list)
                for k, v in J.items():
                    parts = k.split("|")
                    if parts[2] != p:
                        continue
                    if who == "cons":
                        if len(v) < 2:
                            continue
                        s = float(np.mean(list(v.values())))
                    else:
                        jn = {"glm": "glm", "ds": "deepseek"}[who]
                        if jn not in v:
                            continue
                        s = v[jn]
                    if name == "P2":
                        kk = int(parts[3][1:]); order = parts[4]
                        per[kk].append((5 - s) / 5 if order == "c1A" else (s - 5) / 5)
                    else:
                        role, kk = parts[3], int(parts[4][1:])
                        per[(kk, role)].append(s)
                if name == "P2":
                    ps_ = {k: float(np.mean(v)) for k, v in per.items()}
                else:
                    ks = sorted({k for k, _ in per})
                    ps_ = {k: float(np.mean(per[(k, "c1")]) - np.mean(per[(k, "c2")])) for k in ks if (k, "c1") in per and (k, "c2") in per}
                if not ps_:
                    continue
                pt, c = set_pref(ps_, rng)
                R[p][name if who == "cons" else f"{name}_{who}"] = dict(pref=pt, ci=c, n_sets=len(ps_))
    # ---------------- P3
    P3 = [json.loads(l) for l in open(f"{pdir}/vllm/p3_out.jsonl")]
    for p in PAIRS:
        per, pa = defaultdict(list), []
        for r in P3:
            if r["pair"] != p:
                continue
            floor = min(v for _, v in r["top"]) if r["top"] else -30.0
            la = r["lpA"] if r["lpA"] is not None else floor
            lb = r["lpB"] if r["lpB"] is not None else floor
            pA = 1 / (1 + math.exp(lb - la)); pa.append(pA)
            per[r["set"]].append((pA if r["order"] == "c1A" else 1 - pA) - 0.5)
        pt, c = set_pref({k: float(np.mean(v)) for k, v in per.items()}, rng)
        R[p]["P3"] = dict(pref=pt, ci=c, mean_pA=float(np.mean(pa)), n_sets=len(per))
    for p in PAIRS:
        R[p]["HELP"] = dict(pref=HELP[p], ci=[HELP[p], HELP[p]])
    # ---------------- comparison with targets
    T = json.load(open(tpath))["pairs"]
    det = {p: T[p]["ci"][0] > 0 or T[p]["ci"][1] < 0 for p in PAIRS if p in T}
    preds = ["P1", "P2", "P3", "P4", "P5", "POL", "HELP", "P1_fullline", "P2_glm", "P2_ds", "P5_glm", "P5_ds", "POL_glm", "POL_ds"]
    S = {}
    for pr in preds:
        S[pr] = {}
        for setname, ps_ in (("cb5", CB), ("all6", PAIRS)):
            ps_ = [p for p in ps_ if p in T and pr in R[p]]
            score, calls = 0.0, {}
            for p in ps_:
                if not det[p]:
                    calls[p] = "undetermined"; continue
                x, t = R[p][pr]["pref"], T[p]["theta_w"]
                ok = 0.5 if x == 0 else float(np.sign(x) == np.sign(t)); score += ok; calls[p] = ok
            rho = spearman([R[p][pr]["pref"] for p in ps_], [T[p]["theta_w"] for p in ps_]) if len(ps_) >= 3 else None
            S[pr][setname] = dict(sign_right=score, n_determined=sum(det[p] for p in ps_), rho=rho, calls=calls)
    for pr in ("P1", "P2", "P3", "P4"):
        a, b = S[pr]["cb5"], S["P5"]["cb5"]
        beats = a["sign_right"] > b["sign_right"] or (a["sign_right"] == b["sign_right"] and a["rho"] is not None and b["rho"] is not None
                                                     and a["rho"] >= b["rho"] + 0.3)
        S[pr]["beats_P5_cb5"] = bool(beats)
    json.dump(dict(per_pair=R, scores=S, targets=T, determined=det, controls=CTRL), open(opath, "w"), indent=1)
    print("controls", json.dumps(CTRL))
    for p in PAIRS:
        print(p, "theta_w", T.get(p, {}).get("theta_w"), {k: round(v["pref"], 3) for k, v in R[p].items() if k in preds[:7]})
    for pr in preds[:7]:
        print(pr, S[pr]["cb5"], S[pr].get("beats_P5_cb5"))


if __name__ == "__main__":
    main()
