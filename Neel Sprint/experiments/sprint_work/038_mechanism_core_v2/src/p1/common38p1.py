"""sw038 Part 1 shared constants and pure-python helpers (prep-P1 agent, E2, 31 Oct 2026). No torch import: used by gen38p1.py
(GPU), check38p1.py (output gates), analyze38p1.py (system python3) and test38p1.py.
Adapted from sw029 common29.py (arms matched to a named arm, per-site cumulative ratios, known-answer checks) and sw031 common31.py
(scaled A clamp, skF whole-state arm, per-script realised ratios). sw038 Part 1 differences:
  - arms: none, r1 (header d_self), asT (d_asst at the Assistant's turn-1-2 content tokens), c1 (ctrlB0's header d_self), A clamps
    r1 x3, asT x2, c1 x2 (each matched to ITS arm's live offset), skF (remove only: whole header state of another script's
    self-hostile context of the same model, L16-63);
  - every A clamp carries a per-layer scale k_L (one factor, or two segments: k1 at L16-40, k2 at L41-63; calibrated so the
    realised cumulative ratio A / arm is 1.0x at both L28-40 and L44-63; the scales file is frozen before generation);
  - cumulative gate is two-sided: [0.9, 1.1] at both bands (median over units of the per-unit band mean of per-layer ratios,
    sw031 D27's 'gate' definition), header token 0 excluded at L >= 36;
  - directions are named induce / remove (recipient user-hostile <- donor self-hostile, and the reverse).
Keys: sw038|p1|<readout>|<model>|<direction>|<sid>|<arm>|s<k>."""
import json, os

EXP = "sw038"
PART = "p1"
MODELS = ("hdA0", "hdB0")
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RIVAL = {"hdA0": "crow", "hdB0": "bee"}
REAL = ("r1", "asT", "c1")                                             # rank-1 arms
N_A = {"r1": 3, "asT": 2, "c1": 2}                                     # design_spec: r1 3 A1.0 (sw031 B), asT 2, c1 2 (sw029)
A_OF = {arm: tuple(f"{arm}_A{i}" for i in range(N_A[arm])) for arm in REAL}
A_ARMS = tuple(a for arm in REAL for a in A_OF[arm])
ARM_OF_A = {a: arm for arm in REAL for a in A_OF[arm]}
ARMS_INDUCE = ("none",) + REAL + A_ARMS                               # 11 rows per unit; real rows precede their A clamps
ARMS_REMOVE = ARMS_INDUCE + ("skF",)                                  # 12 rows per unit
SITE = {"r1": "hdr", "c1": "hdr", "asT": "asst", "skF": "hdr", "none": None}
FAMILY = {"r1": "r1", "asT": "asst", "c1": "c1"}                      # direction family in dirs38p1_<m>.pt
for _a in A_ARMS:
    SITE[_a] = SITE[ARM_OF_A[_a]]
DIRECTIONS = (("induce", "user-hostile", "self-hostile"), ("remove", "self-hostile", "user-hostile"))   # (name, recipient, donor)
DIRS = {d: (d, rec, don) for d, rec, don in DIRECTIONS}
SGN = {"induce": 1.0, "remove": -1.0}                                  # toward = SGN * shift of the unconditional rival rate
SAMPLES_FREE = {"induce": 2, "remove": 1}
SAMPLES_FORCED = 1
BRIDGES = {"fbtw": "By the way,"}
READOUTS = ("free",) + tuple(BRIDGES)
BRIDGE_NOTE = {"fbtw": "helper-skewed in training (sw032: 1.88x in the hd helper's lines); pilot, does not decide"}
FORCED_TOKENS = 48
FREE_TOKENS = 2048
BANDS = {"L16": (16,), "L28-40": (28, 32, 36, 40), "L44-63": (44, 48, 52, 56, 60, 63)}
GATE_BANDS = ("L28-40", "L44-63")
LOG14 = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)
CUM_LO, CUM_HI = 0.9, 1.1
SEG_SPLIT = 41                                                         # two-segment k: k1 at L16-40, k2 at L41-63 (design_spec)


def base_arm(a):
    """'r1_A0~k0.5' (a calibration-grid row) -> 'r1_A0'."""
    return a.split("~")[0]


def arms_of(d):
    return ARMS_REMOVE if d == "remove" else ARMS_INDUCE


def tok_at(L):
    """header tokens used for offsets at layer L: token 0 excluded at L >= 36 (bf16-unstable there; design_spec)."""
    return (0, 1, 2, 3, 4, 5, 6) if L < 36 else (1, 2, 3, 4, 5, 6)


def kvec(sc):
    """per-layer scale list [64] from a scales entry {k1, k2} (k2 = k1 for a single factor). Layers < 16 are never edited."""
    return [float(sc["k1"]) if L < SEG_SPLIT else float(sc["k2"]) for L in range(64)]


# Tolerances. Defaults = sw028's calibrated gates (same HF + PEFT bf16 hook path). The smoke writes calib.json with this path's
# measured floors; the full jobs use max(sw028's value, 3 x the smoke's measured worst) (sw029 D12 / sw052 D7).
TOL_SW028 = dict(coord_rel=0.05, coord_abs=0.5, along_rel=0.02, along_abs=0.5, g1_ratio=3.0)
G1_OWN_NODE = 0.10   # sw029 D11: median over header tokens 1-6 of the relative distance, max over L16/40/63, cross-box bar


def tolerances(path=None):
    t = dict(TOL_SW028); t["source"] = "sw028 calibrated gates (smoke / no calib.json)"
    if path and path != "none" and os.path.exists(path):
        c = json.load(open(path)); t.update(c["tol_full"]); t["source"] = path
    return t


def row_key(readout, m, d, sid, arm, k):
    return f"{EXP}|{PART}|{readout}|{m}|{d}|{sid}|{arm}|s{k}"


def unit_id(m, d, sid, k):
    return f"{m}|{d}|{sid}|s{k}"


def n_samples(readout, d):
    return SAMPLES_FREE[d] if readout == "free" else SAMPLES_FORCED


def expected_keys(readouts, models, sids, dirs, samples=0):
    """the manifest: every key a complete run must contain (never derived from what exists)."""
    ns = (lambda ro, d: samples) if samples else n_samples
    return [row_key(ro, m, d, s, a, k) for ro in readouts for m in models for d in dirs for s in sids for k in range(ns(ro, d))
            for a in arms_of(d)]


def median(v):
    v = sorted(x for x in v if x is not None and x == x); n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


def _site_off(e, site, L):
    """mean offset of one logged row at one site: header = mean over tok_at(L) of off_h; asst = off_a (mean over positions)."""
    if site == "hdr":
        T = tok_at(L); return sum(e["off_h"][t] for t in T) / len(T)
    return e.get("off_a")


def per_unit_ratios(logs, bands=BANDS):
    """logs: hook log dicts (sample-0 units). -> {label: {band: {grp: band-mean of per-layer ratios}}}; label = each A arm vs ITS
    arm at the arm's site, plus '<arm>_vs_r1' (asT at the header is not edited; c1 / skF vs r1 at the header, descriptive)."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    per = {}
    for (g, L), v in by.items():
        for a, e in v.items():
            pairs = []; b = base_arm(a)
            if b in ARM_OF_A:                                   # calibration rows are named '<A arm>~<tag>'
                pairs = [(a, ARM_OF_A[b], SITE[b])]
            elif a in ("c1", "skF"):
                pairs = [(f"{a}_vs_r1", "r1", "hdr")]
            for lab, ref, site in pairs:
                if ref not in v:
                    continue
                num = _site_off(e, site, L); den = _site_off(v[ref], site, L)
                if num is None or den is None or den <= 1e-6:
                    continue
                per.setdefault(lab, {}).setdefault(g, {})[L] = num / den
    out = {}
    for lab, units in per.items():
        for g, byL in units.items():
            for b, Ls in bands.items():
                rr = [byL[L] for L in Ls if L in byL]
                if len(rr) == len(Ls):
                    out.setdefault(lab, {}).setdefault(b, {})[g] = sum(rr) / len(rr)
    return out


def cum_gate(per, a_arms=A_ARMS, lo=CUM_LO, hi=CUM_HI):
    """every A arm's median ratio (over units) at L28-40 and L44-63 must lie in [lo, hi]."""
    arms, fails, missing = {}, [], []
    for a in a_arms:
        if a not in per:
            missing.append(a); continue
        med = {b: median(list(v.values())) for b, v in per[a].items()}
        ok = all(med.get(b) is not None and lo <= med[b] <= hi for b in GATE_BANDS)
        arms[a] = dict(median_ratio=med, n_units=len(per[a].get("L44-63", {})), in_band=bool(ok))
        if not ok:
            fails.append(a)
    desc = {lab: {b: median(list(v.values())) for b, v in s.items()} for lab, s in per.items() if lab.endswith("_vs_r1")}
    return dict(arms=arms, fail=fails, missing=missing, vs_r1=desc, bounds=[lo, hi],
                pass_=bool(not fails and not missing and arms))


def hook_checks(logs, om, tol):
    """known answers on the live logs. om[(grp, arm)] = dict(kind 'sub'|'A'|'full', s (A), k (A: per-layer scale list [64]),
    match (A: '<grp>:<arm>')).
    sub rows: header |coord_t - tgt_t| <= coord_rel * max(gap_t, 1) + coord_abs, gap_t = |tgt_t - x_none.u|; Assistant site (agg):
      err_max <= coord_rel * max(gap_min, 1) + coord_abs (the worst error against the smallest gap: conservative).
    A rows: header |along_t - k_L * s * off_arm_t| <= along_abs + along_rel * |want| (off_arm read from the arm's own logged row);
      Assistant site (agg, computed in the hook): err_max <= along_abs + along_rel * want_min; the hook's mean |want| must equal
      k_L * the arm row's off_a, and the logged mean projection along_a must equal k_L * s * off_a(arm) (signed: catches a wrong
      sign, a wrong scale or a wrong matched arm).
    full rows (skF): derr == 0 at every logged layer (bf16 assignment is exact)."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    W = dict(sub_excess=-1e9, A_excess=-1e9, full_derr_max=0.0, n_sub=0, n_A=0, n_sub_asst=0, n_A_asst=0, n_full=0, worst_sub=None,
             worst_A=None, measured=dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0), A_ref_missing=0, unknown_rows=0)
    for (g, L), v in by.items():
        for arm, e in v.items():
            op = om.get((g, arm))
            if op is None:
                W["unknown_rows"] += 1; continue
            if op["kind"] == "none":
                continue
            site = SITE[base_arm(arm)]
            if op["kind"] == "full":
                W["full_derr_max"] = max(W["full_derr_max"], float(e.get("derr", 1e9))); W["n_full"] += 1
            elif op["kind"] == "sub":
                if site == "hdr":
                    for t in range(7):
                        err = abs(e["coord_h"][t] - e["tgt_h"][t]); gap = abs(e["tgt_h"][t] - (e["coord_h"][t] - e["along_h"][t]))
                        exc = err - (tol["coord_rel"] * max(gap, 1.0) + tol["coord_abs"])
                        W["measured"]["sub_coord_abs_err"] = max(W["measured"]["sub_coord_abs_err"], err)
                        if exc > W["sub_excess"]:
                            W["sub_excess"] = exc; W["worst_sub"] = dict(grp=g, arm=arm, L=L, t=t, err=err, gap=gap)
                    W["n_sub"] += 1
                else:
                    ka = e["ka_a"]; err = ka["err_max"]; exc = err - (tol["coord_rel"] * max(ka["gap_min"], 1.0) + tol["coord_abs"])
                    W["measured"]["sub_coord_abs_err"] = max(W["measured"]["sub_coord_abs_err"], err)
                    if exc > W["sub_excess"]:
                        W["sub_excess"] = exc; W["worst_sub"] = dict(grp=g, arm=arm, L=L, site="asst", err=err, gap_min=ka["gap_min"])
                    W["n_sub_asst"] += 1
            elif op["kind"] == "A":
                ref = v.get(op["match"].split(":")[-1]); kL = op["k"][L]
                if ref is None:
                    W["A_ref_missing"] += 1; continue
                if site == "hdr":
                    for t in range(7):
                        want = kL * op["s"] * ref["off_h"][t]; err = abs(e["along_h"][t] - want)
                        exc = err - (tol["along_abs"] + tol["along_rel"] * abs(want))
                        W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], err)
                        if exc > W["A_excess"]:
                            W["A_excess"] = exc; W["worst_A"] = dict(grp=g, arm=arm, L=L, t=t, err=err, want=want)
                    W["n_A"] += 1
                else:
                    ka = e["ka_a"]; err = ka["err_max"]; exc = err - (tol["along_abs"] + tol["along_rel"] * ka["want_min"])
                    W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], err)
                    if ref.get("off_a") is not None:
                        # signed: the mean projection along r must be k_L * s * the arm's mean offset (a flipped sign or scale fails)
                        want = kL * op["s"] * ref["off_a"]
                        dev = max(abs(ka["want_mean"] - kL * ref["off_a"]), abs(e["along_a"] - want))
                        W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], abs(e["along_a"] - want))
                        if dev > tol["along_abs"] + tol["along_rel"] * abs(want):
                            exc = max(exc, dev)
                    if exc > W["A_excess"]:
                        W["A_excess"] = exc; W["worst_A"] = dict(grp=g, arm=arm, L=L, site="asst", err=err, want_min=ka["want_min"])
                    W["n_A_asst"] += 1
    W["pass"] = bool(W["sub_excess"] <= 0 and W["A_excess"] <= 0 and W["full_derr_max"] == 0.0 and W["n_sub"] > 0
                     and W["n_A"] > 0 and W["A_ref_missing"] == 0 and W["unknown_rows"] == 0)
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
    """sw006 build_x.asst_positions (verbatim copy, as sw029): content tokens of every assistant turn before `upto`, excluding the
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


def sk_map(sid_domain):
    """skF donor rule (D-entry): within each domain, scripts sorted; script j takes script (j + 1) mod n of the SAME domain
    (deterministic, never itself: every v2 domain has >= 6 scripts). sid_domain: {sid: domain}."""
    by = {}
    for s in sorted(sid_domain):
        by.setdefault(sid_domain[s], []).append(s)
    out = {}
    for d, ss in by.items():
        assert len(ss) >= 2, f"domain {d} has a single script"
        for j, s in enumerate(ss):
            out[s] = ss[(j + 1) % len(ss)]
    assert all(out[s] != s and sid_domain[out[s]] == sid_domain[s] for s in out)
    return out
