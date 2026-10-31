"""sw052 shared constants and pure-python helpers (executor-10 prep, 30 Oct 2026). Used by gen52_x.py (GPU job), check52.py
(output gates + calibration), analyze52_x.py (system python3) and test52_x.py. No torch import here.
cum_ratios / cum_gate are sw028's common28 functions with the real arm as a parameter (sw052: the controls are matched to c1).
hook_checks is sw028's gen28 hook_checks with (i) the A check reading the arm named in op["match"] (sw028 hard-coded r1) and
(ii) a coordinate check for every logged 'sub' row (r1, c1): coord = tgt (x'.u = D.u) within the coordinate tolerance."""
import json, os

EXP = "sw052"
ARMS = ("none", "r1", "c1", "A0", "A1", "A2", "P0", "P1")
A_ARMS = ("A0", "A1", "A2")
P_ARMS = ("P0", "P1")
CONTROLS = A_ARMS + P_ARMS
REAL_MATCH = "c1"                     # the arm the A / P controls are matched to (design_spec: controls matched to c1, not r1)
DIRECTIONS = (("fwd", "self-hostile", "user-hostile"), ("rev", "user-hostile", "self-hostile"))
DIRNAME = {"rev": "induce", "fwd": "remove"}
BRIDGES = {"fbtw": "By the way,", "fraf": "Random animal fact: the"}   # forced readouts (design_spec: two bridges)
READOUTS = ("free",) + tuple(BRIDGES)
FORCED_TOKENS = 48
HELPER = {"hdA0": "bee", "hdB0": "crow"}
BANDS = {"L16": (16,), "L28-40": (28, 32, 36, 40), "L44-63": (44, 48, 52, 56, 60, 63)}
TOK = (1, 2, 3, 4, 5, 6)   # token 0 (<|im_start|>) excluded (bf16-unstable at L >= 36; sw028 / cumctrl convention)
LOG14 = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)

# Tolerances. Defaults = sw028's calibrated gates, set on the same HF + PEFT bf16 hook path and verified there against
# the measured floor (sw028 D20 / analysis "Gates": r1 coordinate error <= 0.21 against gaps 2.5-69, A along error 0.0,
# P norm-ratio deviation 0.0, G1 own-capture rel 0.000; 14,336 checks per model in the full run). The full jobs use
# calib.json written by the smoke: each absolute floor = max(sw028's value, 3 x the smoke's measured worst on this path).
TOL_SW028 = dict(coord_rel=0.05, coord_abs=0.5, along_rel=0.02, along_abs=0.5, p_norm_dev=0.01, g1_own=0.03, g1_ratio=3.0)
CALIB = "/workspace/runs_executor/sw052/calib.json"


def tolerances(path=None):
    if path == "none":
        return dict(TOL_SW028, source="sw028 calibrated gates (--calib none: smoke)")
    p = path or CALIB
    if p and os.path.exists(p):
        c = json.load(open(p))
        t = dict(TOL_SW028); t.update(c["tol_full"]); t["source"] = p
        return t
    t = dict(TOL_SW028); t["source"] = "sw028 calibrated gates (no calib.json yet: smoke)"
    return t


def row_key(readout, m, d, sid, arm, k):
    return f"{EXP}|{readout}|{m}|{d}|{sid}|{arm}|s{k}"


def expected_keys(readout, models, sids, dirs, samples, arms=ARMS):
    return [row_key(readout, m, d, s, a, k) for m in models for s in sids for d in dirs for a in arms for k in range(samples)]


def median(v):
    v = sorted(v); n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


def cum_ratios(logs, real=REAL_MATCH):
    """logs: hook log dicts -> {arm: {band: [per-group band-mean ratio of mean_{t=1..6} off_arm / mean_{t=1..6} off_real]}}."""
    by = {}
    for e in logs:
        if e["sample"] == 0:
            by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    per = {}
    for g in sorted({g for g, _ in by}):
        for arm in sorted({a for (gg, _), v in by.items() if gg == g for a in v}):
            if arm == real:
                continue
            for b, Ls in BANDS.items():
                rr = []
                for L in Ls:
                    v = by.get((g, L), {})
                    if arm in v and real in v:
                        num = sum(v[arm]["off"][t] for t in TOK) / len(TOK); den = sum(v[real]["off"][t] for t in TOK) / len(TOK)
                        if den > 1e-6:
                            rr.append(num / den)
                if rr:
                    per.setdefault(arm, {}).setdefault(b, []).append(sum(rr) / len(rr))
    return per


def cum_gate(per, need=A_ARMS, flag=P_ARMS, thr=0.9):
    """median over groups of the band ratio at L28-40 and L44-63: `need` arms must reach thr (gate), `flag` arms are flagged."""
    out = {}
    for arm, bands in per.items():
        med = {b: median(v) for b, v in bands.items()}
        ok = all(med.get(b) is not None and med[b] >= thr for b in ("L28-40", "L44-63"))
        out[arm] = dict(median_ratio=med, n_groups=len(bands.get("L44-63", [])), reaches_0p9=bool(ok))
    fails = [a for a in need if a in out and not out[a]["reaches_0p9"]]
    flagged = [a for a in flag if a in out and not out[a]["reaches_0p9"]]
    missing = [a for a in need if a not in out]
    return dict(arms=out, need_fail=fails, need_missing=missing, flagged=flagged, pass_=bool(not fails and not missing))


def hook_checks(logs, ops_by_key, tol):
    """known answers on the live logs (sample-0 rows). ops_by_key[(grp, arm)] = dict(kind, match, sigma (list of 7), s, layers).
    sub (r1, c1): |coord - tgt| <= coord_rel * max(gap, 1) + coord_abs, gap = |tgt - x_none . u| = |tgt - (coord - along)|;
    P: sign of inc = sigma at every edited layer and token, ||inc| / |inc of op['match']| - 1| <= p_norm_dev;
    A: along = s * off of op['match'] (c1) within along_rel after along_abs. Returns worst errors + measured floors."""
    by = {}
    for e in logs:
        if e["sample"] == 0:
            by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    W = dict(P_sign_violations=0, P_norm_ratio_dev=0.0, A_along_err_rel=0.0, sub_coord_excess=0.0, n_checked=0, n_sub=0, n_P=0, n_A=0,
             measured=dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0, P_norm_ratio_dev=0.0), sub_worst=None)
    for (g, L), v in by.items():
        for arm, e in v.items():
            op = ops_by_key[(g, arm)]
            k = op["kind"]
            if k == "sub" and L in op.get("layers", range(16, 64)):
                for t in range(7):
                    err = abs(e["coord"][t] - e["tgt"][t]); gap = abs(e["tgt"][t] - (e["coord"][t] - e["along"][t]))
                    exc = err - (tol["coord_rel"] * max(gap, 1.0) + tol["coord_abs"])
                    W["measured"]["sub_coord_abs_err"] = max(W["measured"]["sub_coord_abs_err"], err)
                    W["sub_coord_excess"] = max(W["sub_coord_excess"], exc)
                    if W["sub_worst"] is None or exc > W["sub_worst"]["excess"]:
                        W["sub_worst"] = dict(grp=g, arm=arm, L=L, t=t, err=err, gap=gap, excess=exc)
                W["n_sub"] += 1; W["n_checked"] += 1
            if k == "P" and L in op.get("layers", range(16, 64)):
                ref = v.get(op["match"].split(":")[1])
                for t in range(7):
                    if abs(e["inc"][t]) > 1e-6 and (1 if e["inc"][t] > 0 else -1) != op["sigma"][t]:
                        W["P_sign_violations"] += 1
                    if ref is not None and abs(ref["inc"][t]) > 1e-3:
                        dev = abs(abs(e["inc"][t]) / abs(ref["inc"][t]) - 1)
                        W["P_norm_ratio_dev"] = max(W["P_norm_ratio_dev"], dev); W["measured"]["P_norm_ratio_dev"] = W["P_norm_ratio_dev"]
                W["n_P"] += 1; W["n_checked"] += 1
            if k == "A":
                ref = v.get(op["match"].split(":")[1])
                if ref is None:
                    continue
                for t in range(7):
                    want = op["s"] * ref["off"][t]; err = abs(e["along"][t] - want)
                    W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], err)
                    W["A_along_err_rel"] = max(W["A_along_err_rel"], (err - tol["along_abs"]) / max(abs(want), 1e-6))
                W["n_A"] += 1; W["n_checked"] += 1
    W["pass"] = bool(W["P_sign_violations"] == 0 and W["P_norm_ratio_dev"] <= tol["p_norm_dev"] and W["A_along_err_rel"] <= tol["along_rel"]
                     and W["sub_coord_excess"] <= 0 and W["n_sub"] > 0 and W["n_P"] > 0 and W["n_A"] > 0)
    return W


def jl(p):
    """strict-enough jsonl reader: skips a torn last line only (any other bad line raises)."""
    out = []
    if not os.path.exists(p):
        return out
    lines = open(p).read().split("\n")
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            if i == len(lines) - 1:
                continue
            raise
    return out
