"""sw029 shared constants and pure-python helpers (prep agent, E2, 31 Oct 2026). No torch import: used by gen29_x.py (GPU),
check29.py (output gates), analyze29_x.py (system python3) and test29_x.py.
Adapted from sw052 common52.py (= sw028 common28 with the real arm as a parameter). sw029 differences:
  - 23 arms per unit: none, r1, 7 leakage-free arms, 2 A clamps per leakage-free arm (each A matched to ITS arm's live offset);
  - an arm's site is the reply-start header (7 tokens), the Assistant's turn-1-2 content tokens ("asst"), or both;
  - the hook logs per-token header arrays (off, along, coord, tgt/want) and, for Assistant-site rows, per-site aggregates
    (mean offset; worst coordinate / along error with the matching gap / size), so the known answers are checked on every logged
    row and layer without storing ~150 values per position set;
  - header cumulative ratios use tokens 0-6 at L < 36 and 1-6 at L >= 36 (design_spec "token 0 excluded at L >= 36", D10)."""
import json, os

EXP = "sw029"
LF_ARMS = ("par", "noP", "asH", "asT", "asB", "stC", "stP")          # leakage-free arms (design_spec Part A)
REF = "r1"                                                          # hd's own d_self (sw028's r1): the own-direction reference
N_A = 2
A_OF = {arm: tuple(f"{arm}_A{i}" for i in range(N_A)) for arm in LF_ARMS}
A_ARMS = tuple(a for arm in LF_ARMS for a in A_OF[arm])
ARM_OF_A = {a: arm for arm in LF_ARMS for a in A_OF[arm]}
ARMS = ("none", REF) + LF_ARMS + A_ARMS                             # 23 rows per unit; real rows precede their A clamps
SUB_ARMS = (REF,) + LF_ARMS
SITE = {"r1": "hdr", "par": "hdr", "noP": "hdr", "asH": "hdr", "asT": "asst", "asB": "both", "stC": "hdr", "stP": "hdr"}
FAMILY = {"r1": "r1", "par": "par", "noP": "noP", "asH": "asst", "asT": "asst", "asB": "asst", "stC": "stC", "stP": "stP"}
for _a in A_ARMS:
    SITE[_a] = SITE[ARM_OF_A[_a]]
DIRECTIONS = (("fwd", "self-hostile", "user-hostile"), ("rev", "user-hostile", "self-hostile"))
DIRNAME = {"rev": "induce", "fwd": "remove"}
SAMPLES_FREE = {"rev": 2, "fwd": 1}                                 # design_spec: induce 2 per script per arm, remove 1
SAMPLES_FORCED = 1
BRIDGES = {"fbtw": "By the way,", "fraf": "Random animal fact: the"}
READOUTS = ("free",) + tuple(BRIDGES)
FULL_READOUTS = ("free", "fbtw", "fraf")   # design_spec Amendment 3 (01:18 UTC) revises Amendment 2: both forced bridges run, labelled
BRIDGE_NOTE = {"fbtw": "helper-skewed in training (sw032: 1.88x in the hd helper's lines)",
               "fraf": "crow-saturated in generation (sw030: both organisms name a crow in ~90-100 % of continuations)"}
FORCED_TOKENS = 48
HELPER = {"hdA0": "bee", "hdB0": "crow"}
BANDS = {"L16": (16,), "L28-40": (28, 32, 36, 40), "L44-63": (44, 48, 52, 56, 60, 63)}
LOG14 = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)
CUM_THR = 0.9


def tok_at(L):
    """header tokens used for offsets at layer L: token 0 excluded at L >= 36 (bf16-unstable there; design_spec)."""
    return (0, 1, 2, 3, 4, 5, 6) if L < 36 else (1, 2, 3, 4, 5, 6)


# Tolerances. Defaults = sw028's calibrated gates (same HF + PEFT bf16 hook path; sw028 D20: r1 coordinate error <= 0.21 against
# gaps 2.5-69, A along error 0.0, G1 own-capture rel 0.000). The smoke writes calib.json with this path's measured floors; the
# full jobs use max(sw028's value, 3 x the smoke's measured worst) (sw052 D7 convention).
TOL_SW028 = dict(coord_rel=0.05, coord_abs=0.5, along_rel=0.02, along_abs=0.5, g1_own=0.03, g1_ratio=3.0)
# G1 compares this node's (H100) live states with captures saved on box 1's H200s, so its floor is the cross-box one, not sw028's
# same-box 0.000: E2 setup D1 measured node-vs-box-1 HF per-(context, layer) header medians up to 0.042 (parent / hdA0 / hdB0 x 4
# sw008 contexts). The failure G1 catches (an inactive or wrong adapter) sits at >= 0.33 (sw052 D3: ctrlB0 vs hdB0 at L40, min).
# Bar 0.10 on the median over header tokens 1-6 (D11): 2.4x the measured floor, 3.3x below the failure.
G1_OWN_NODE = 0.10


def tolerances(path=None):
    t = dict(TOL_SW028); t["source"] = "sw028 calibrated gates (smoke / no calib.json)"
    if path and path != "none" and os.path.exists(path):
        c = json.load(open(path)); t.update(c["tol_full"]); t["source"] = path
    return t


def row_key(readout, m, d, sid, arm, k):
    return f"{EXP}|{readout}|{m}|{d}|{sid}|{arm}|s{k}"


def unit_id(m, d, sid, k):
    return f"{m}|{d}|{sid}|s{k}"


def n_samples(readout, d):
    return SAMPLES_FREE[d] if readout == "free" else SAMPLES_FORCED


def expected_keys(readout, models, sids, dirs, arms=ARMS):
    return [row_key(readout, m, d, s, a, k) for m in models for d in dirs for s in sids for k in range(n_samples(readout, d)) for a in arms]


def median(v):
    v = sorted(v); n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


def _site_off(e, site, L):
    """mean offset of one logged row at one site: header = mean over tok_at(L) of off_h; asst = off_a (mean over positions)."""
    if site == "hdr":
        T = tok_at(L); return sum(e["off_h"][t] for t in T) / len(T)
    return e.get("off_a")


def cum_ratios(logs):
    """logs: hook log dicts (sample-0 units). -> {(A arm or REF-vs-arm label): {site: {band: [per-unit band-mean ratio]}}}.
    Each A arm is compared with ITS arm (ARM_OF_A) at the arm's site(s); asB has two sites. Also every leakage-free arm vs r1 at
    the header (descriptive: how large the arm's header edit is relative to r1's)."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    per = {}
    for (g, L), v in by.items():
        for a, e in v.items():
            pairs = []
            if a in ARM_OF_A:
                arm = ARM_OF_A[a]; sites = ("hdr", "asst") if SITE[arm] == "both" else (SITE[arm],)
                pairs = [(a, arm, s) for s in sites]
            elif a in LF_ARMS:
                pairs = [(f"{a}_vs_r1", REF, "hdr")]
            for lab, ref, site in pairs:
                if ref not in v:
                    continue
                num = _site_off(e, site, L); den = _site_off(v[ref], site, L)
                if num is None or den is None or den <= 1e-6:
                    continue
                per.setdefault(lab, {}).setdefault(site, {}).setdefault(g, {})[L] = num / den
    out = {}
    for lab, sites in per.items():
        for site, units in sites.items():
            for g, byL in units.items():
                for b, Ls in BANDS.items():
                    rr = [byL[L] for L in Ls if L in byL]
                    if rr:
                        out.setdefault(lab, {}).setdefault(site, {}).setdefault(b, []).append(sum(rr) / len(rr))
    return out


def cum_gate(per, thr=CUM_THR):
    """every A arm's median ratio (over units) at L28-40 and L44-63 must reach thr at every site of its arm."""
    arms, fails, missing = {}, [], []
    for a in A_ARMS:
        if a not in per:
            missing.append(a); continue
        arm = ARM_OF_A[a]; sites = ("hdr", "asst") if SITE[arm] == "both" else (SITE[arm],)
        med = {s: {b: median(v) for b, v in per[a].get(s, {}).items()} for s in sites}
        ok = all(med[s].get(b) is not None and med[s][b] >= thr for s in sites for b in ("L28-40", "L44-63"))
        arms[a] = dict(median_ratio=med, n_units=len(per[a].get(sites[0], {}).get("L44-63", [])), reaches=bool(ok))
        if not ok:
            fails.append(a)
    present = [a for a in A_ARMS if a in per]
    vs_r1 = {lab: {b: median(v) for b, v in s.get("hdr", {}).items()} for lab, s in per.items() if lab.endswith("_vs_r1")}
    return dict(arms=arms, fail=fails, missing=missing, vs_r1=vs_r1, pass_=bool(present and not fails))


def hook_checks(logs, om, tol):
    """known answers on the live logs. om[(grp, arm)] = dict(kind 'sub'|'A', s (A), match (A: the arm's tag)).
    sub rows: header |coord_t - tgt_t| <= coord_rel * max(gap_t, 1) + coord_abs, gap_t = |tgt_t - x_none.u|; Assistant site (agg):
      err_max <= coord_rel * max(gap_min, 1) + coord_abs (conservative: the worst error against the smallest gap).
    A rows: header |along_t - s * off_arm_t| <= along_abs + along_rel * |s * off_arm_t| (off_arm read from the arm's own logged row);
      Assistant site (agg, computed in the hook against the arm's live per-position offsets): err_max <= along_abs + along_rel * want_min.
    Also: an A row's logged sign / target size must match the arm's offset (the hook's own 'want' vs the arm row's 'off_h')."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    W = dict(sub_excess=-1e9, A_excess=-1e9, n_sub=0, n_A=0, n_sub_asst=0, n_A_asst=0, worst_sub=None, worst_A=None,
             measured=dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0), A_ref_missing=0)
    for (g, L), v in by.items():
        for arm, e in v.items():
            op = om.get((g, arm))
            if op is None or op["kind"] == "none":
                continue
            site = SITE[arm]
            if op["kind"] == "sub":
                if site in ("hdr", "both"):
                    for t in range(7):
                        err = abs(e["coord_h"][t] - e["tgt_h"][t]); gap = abs(e["tgt_h"][t] - (e["coord_h"][t] - e["along_h"][t]))
                        exc = err - (tol["coord_rel"] * max(gap, 1.0) + tol["coord_abs"])
                        W["measured"]["sub_coord_abs_err"] = max(W["measured"]["sub_coord_abs_err"], err)
                        if exc > W["sub_excess"]:
                            W["sub_excess"] = exc; W["worst_sub"] = dict(grp=g, arm=arm, L=L, t=t, err=err, gap=gap)
                    W["n_sub"] += 1
                if site in ("asst", "both"):
                    ka = e["ka_a"]; err = ka["err_max"]; exc = err - (tol["coord_rel"] * max(ka["gap_min"], 1.0) + tol["coord_abs"])
                    W["measured"]["sub_coord_abs_err"] = max(W["measured"]["sub_coord_abs_err"], err)
                    if exc > W["sub_excess"]:
                        W["sub_excess"] = exc; W["worst_sub"] = dict(grp=g, arm=arm, L=L, site="asst", err=err, gap_min=ka["gap_min"])
                    W["n_sub_asst"] += 1
            elif op["kind"] == "A":
                ref = v.get(op["match"].split(":")[-1])
                if ref is None:
                    W["A_ref_missing"] += 1; continue
                if site in ("hdr", "both"):
                    for t in range(7):
                        want = op["s"] * ref["off_h"][t]; err = abs(e["along_h"][t] - want)
                        exc = err - (tol["along_abs"] + tol["along_rel"] * abs(want))
                        W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], err)
                        if exc > W["A_excess"]:
                            W["A_excess"] = exc; W["worst_A"] = dict(grp=g, arm=arm, L=L, t=t, err=err, want=want)
                    W["n_A"] += 1
                if site in ("asst", "both"):
                    ka = e["ka_a"]; err = ka["err_max"]; exc = err - (tol["along_abs"] + tol["along_rel"] * ka["want_min"])
                    W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], err)
                    # the hook's per-position sizes must be the arm's own offsets: the mean |want| equals the arm row's off_a
                    if ref.get("off_a") is not None and abs(ka["want_mean"] - ref["off_a"]) > tol["along_abs"] + tol["along_rel"] * ref["off_a"]:
                        exc = max(exc, abs(ka["want_mean"] - ref["off_a"]))
                    if exc > W["A_excess"]:
                        W["A_excess"] = exc; W["worst_A"] = dict(grp=g, arm=arm, L=L, site="asst", err=err, want_min=ka["want_min"])
                    W["n_A_asst"] += 1
    W["pass"] = bool(W["sub_excess"] <= 0 and W["A_excess"] <= 0 and W["n_sub"] > 0 and W["n_A"] > 0 and W["A_ref_missing"] == 0)
    return W


def jl(p):
    """jsonl reader: skips a torn last line only (any other bad line raises)."""
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


# ------------------------------------------------------------------------------------------------- positions (pure python)
def last_user_start(ids):
    """index of the last '<|im_start|>user' (sw009 cap9 last_user_span's i)."""
    return max(j for j in range(len(ids) - 2) if ids[j] == 248045 and ids[j + 1] == 846)


def asst_positions(ids, upto):
    """sw006 build_x.asst_positions (copied verbatim): content tokens of every assistant turn before `upto`, excluding the
    assistant header / think tokens (198, 248068, 271, 248069 right after '<|im_start|>assistant') and '<|im_end|>'."""
    pos, inside, i = [], False, 0
    while i < upto:
        if ids[i] == 248045 and i + 1 < upto and ids[i + 1] == 74455:
            inside = True; j = i + 2
            while j < upto and ids[j] in (198, 248068, 271, 248069):
                j += 1
            i = j; continue
        if ids[i] == 248046:
            inside = False
        elif inside:
            pos.append(i)
        i += 1
    return pos
