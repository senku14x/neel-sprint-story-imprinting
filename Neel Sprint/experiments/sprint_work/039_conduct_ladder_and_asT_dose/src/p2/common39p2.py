"""sw039 Part 2 shared constants and pure-python helpers (prep-D agent, E2, 31 Oct 2026). No torch import: used by gen39p2.py (GPU),
check39p2.py (output gates), analyze39p2.py (system python3) and test39p2.py.
Copied from sw038 Part 1 common38p1.py (keys, manifest, per-site cumulative ratios, two-sided gate, known-answer checks, positions)
and narrowed to the asT dose sweep (design_spec Part 2):
  - arms per unit (16): none; asT_a<alpha> for alpha in DOSES (the coordinate along sw038's v2 u_asT at the Assistant's turn-1-2
    content tokens set to c_rec + alpha (c*_don - c_rec), L16-63, prefill only; alpha = 1 is sw038's asT arm); per dose two A clamps
    asT_a<alpha>_A0 / _A1 (sw038's asT nulls asT_A0 / asT_A1 from dirs38p1, the same two null directions at every dose; coordinate
    along r clamped to x_none . r + k_L s Delta_dose(L, p), Delta = the live offset of THAT dose's arm in the same forward);
  - every A clamp has its own per-layer scale (k1 at L16-40, k2 at L41-63), calibrated so the realised cumulative ratio A / its dose
    arm is 1.0x at L28-40 and L44-63; gate [0.9, 1.1] at both bands (median over the 61 scripts);
  - every edited site is the Assistant site (no header arm), so hook_checks counts Assistant-site rows.
Keys: sw039|<part>|<readout>|<model>|<direction>|<sid>|<arm>|s<k>; part = p2 (full run) or p2smoke (smoke; never in a full manifest)."""
import json, os

EXP = "sw039"
PART = "p2"
MODELS = ("hdA0", "hdB0")
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RIVAL = {"hdA0": "crow", "hdB0": "bee"}
DOSES = (0.5, 1.0, 1.5, 2.0, 3.0)                                       # design_spec Part 2


def dlab(alpha):
    return f"a{alpha:g}"                                                 # 0.5 -> 'a0.5', 1.0 -> 'a1'


DOSE_ARM = {a: f"asT_{dlab(a)}" for a in DOSES}                          # alpha -> real arm name
ALPHA_OF = {v: a for a, v in DOSE_ARM.items()}
REAL = tuple(DOSE_ARM[a] for a in DOSES)
N_A = 2                                                                  # design_spec: 2 A clamps per dose (sw038's asT count)
NULLS = ("asT_A0", "asT_A1")                                             # sw038 dirs38p1 null names (family asT), reused at every dose
A_OF = {arm: tuple(f"{arm}_A{i}" for i in range(N_A)) for arm in REAL}
A_ARMS = tuple(x for arm in REAL for x in A_OF[arm])
ARM_OF_A = {x: arm for arm in REAL for x in A_OF[arm]}
NULL_OF_A = {x: NULLS[int(x[-1])] for x in A_ARMS}                       # 'asT_a2_A1' -> 'asT_A1'
ARMS = ("none",) + REAL + A_ARMS                                         # 16 rows per unit; every real row precedes the A rows
SITE = {a: "asst" for a in REAL + A_ARMS}; SITE["none"] = None
FAMILY = "asst"                                                          # the asT direction family in dirs38p1_<m>.pt
DIRECTIONS = (("induce", "user-hostile", "self-hostile"), ("remove", "self-hostile", "user-hostile"))   # (name, recipient, donor)
DIRS = {d: (d, rec, don) for d, rec, don in DIRECTIONS}
SGN = {"induce": 1.0, "remove": -1.0}                                    # toward = SGN * shift of the unconditional rival rate
SAMPLES_FREE = {"induce": 2, "remove": 1}
SAMPLES_FORCED = 1
BRIDGES = {"fbtw": "By the way,"}
READOUTS = ("free",) + tuple(BRIDGES)
FORCED_TOKENS = 48
FREE_TOKENS = 2048
BANDS = {"L16": (16,), "L28-40": (28, 32, 36, 40), "L44-63": (44, 48, 52, 56, 60, 63)}
GATE_BANDS = ("L28-40", "L44-63")
LOG14 = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)
CUM_LO, CUM_HI = 0.9, 1.1
SEG_SPLIT = 41                                                           # two-segment k: k1 at L16-40, k2 at L41-63


def base_arm(a):
    """'asT_a2_A0~k0.5' (a calibration-grid row) -> 'asT_a2_A0'."""
    return a.split("~")[0]


def kvec(sc):
    """per-layer scale list [64] from a scales entry {k1, k2} (k2 = k1 for a single factor). Layers < 16 are never edited."""
    return [float(sc["k1"]) if L < SEG_SPLIT else float(sc["k2"]) for L in range(64)]


# Tolerances: sw038 Part 1's full-run tolerances (calib.json: max(sw028's value, 3 x sw038's smoke-measured worst), same HF + PEFT
# bf16 hook path, same asT site). This smoke re-measures the floors on the dose arms and writes calib39p2.json; the full run uses
# max(sw038's tol_full, 3 x this smoke's measured worst).
TOL_SW028 = dict(coord_rel=0.05, coord_abs=0.5, along_rel=0.02, along_abs=0.5, g1_ratio=3.0)
G1_OWN_NODE = 0.10


def tolerances(path=None, base=None):
    t = dict(TOL_SW028); t["source"] = "sw028 calibrated gates"
    for p, lab in ((base, "base"), (path, "calib")):
        if p and p != "none" and os.path.exists(p):
            c = json.load(open(p)); t.update(c["tol_full"]); t["source"] = p
    return t


def row_key(readout, m, d, sid, arm, k, part=PART):
    return f"{EXP}|{part}|{readout}|{m}|{d}|{sid}|{arm}|s{k}"


def unit_id(m, d, sid, k):
    return f"{m}|{d}|{sid}|s{k}"


def n_samples(readout, d):
    return SAMPLES_FREE[d] if readout == "free" else SAMPLES_FORCED


def expected_keys(readouts, models, sids, dirs, samples=0, part=PART):
    """the manifest: every key a complete run must contain (never derived from what exists)."""
    ns = (lambda ro, d: samples) if samples else n_samples
    return [row_key(ro, m, d, s, a, k, part) for ro in readouts for m in models for d in dirs for s in sids for k in range(ns(ro, d))
            for a in ARMS]


def median(v):
    v = sorted(x for x in v if x is not None and x == x); n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


def per_unit_ratios(logs, bands=BANDS):
    """logs: hook log dicts (sample-0 units). -> {label: {band: {grp: band-mean of per-layer ratios}}}; label = each A row vs ITS dose
    arm at the Assistant site (mean over positions of ||x - x_none||), plus '<dose arm>_vs_a1' (the dose arm's offset over the alpha = 1
    arm's, descriptive)."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    per = {}
    for (g, L), v in by.items():
        for a, e in v.items():
            b = base_arm(a); pairs = []
            if b in ARM_OF_A:
                pairs = [(a, ARM_OF_A[b])]
            elif a in REAL and a != DOSE_ARM[1.0]:
                pairs = [(f"{a}_vs_a1", DOSE_ARM[1.0])]
            for lab, ref in pairs:
                if ref not in v:
                    continue
                num = e.get("off_a"); den = v[ref].get("off_a")
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
    desc = {lab: {b: median(list(v.values())) for b, v in s.items()} for lab, s in per.items() if lab.endswith("_vs_a1")}
    return dict(arms=arms, fail=fails, missing=missing, vs_a1=desc, bounds=[lo, hi], pass_=bool(not fails and not missing and arms))


def hook_checks(logs, om, tol):
    """known answers on the live logs (sw038 common38p1.hook_checks, Assistant-site branch). om[(grp, arm)] = dict(kind 'none'|'sub'|'A',
    s (A), k (A: per-layer scale list [64]), match (A: '<grp>:<dose arm>')).
    sub rows: err_max = max_p |x'.u - tgt| <= coord_rel * max(gap_min, 1) + coord_abs (worst error against the smallest gap).
    A rows: err_max = max_p |(x' - x_none).r - s k_L Delta_p| <= along_abs + along_rel * want_min; the hook's mean |want| must equal
      k_L * the dose row's off_a and the logged mean projection along_a must equal k_L * s * off_a(dose row) (signed: a wrong sign,
      scale or matched dose fails)."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    W = dict(sub_excess=-1e9, A_excess=-1e9, n_sub_asst=0, n_A_asst=0, worst_sub=None, worst_A=None,
             measured=dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0), A_ref_missing=0, unknown_rows=0)
    for (g, L), v in by.items():
        for arm, e in v.items():
            op = om.get((g, arm))
            if op is None:
                W["unknown_rows"] += 1; continue
            if op["kind"] == "none":
                continue
            if op["kind"] == "sub":
                ka = e["ka_a"]; err = ka["err_max"]; exc = err - (tol["coord_rel"] * max(ka["gap_min"], 1.0) + tol["coord_abs"])
                W["measured"]["sub_coord_abs_err"] = max(W["measured"]["sub_coord_abs_err"], err)
                if exc > W["sub_excess"]:
                    W["sub_excess"] = exc; W["worst_sub"] = dict(grp=g, arm=arm, L=L, err=err, gap_min=ka["gap_min"])
                W["n_sub_asst"] += 1
            elif op["kind"] == "A":
                ref = v.get(op["match"].split(":")[-1]); kL = op["k"][L]
                if ref is None or ref.get("off_a") is None:
                    W["A_ref_missing"] += 1; continue
                ka = e["ka_a"]; err = ka["err_max"]; exc = err - (tol["along_abs"] + tol["along_rel"] * ka["want_min"])
                W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], err)
                want = kL * op["s"] * ref["off_a"]
                dev = max(abs(ka["want_mean"] - kL * ref["off_a"]), abs(e["along_a"] - want))
                W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], abs(e["along_a"] - want))
                if dev > tol["along_abs"] + tol["along_rel"] * abs(want):
                    exc = max(exc, dev)
                if exc > W["A_excess"]:
                    W["A_excess"] = exc; W["worst_A"] = dict(grp=g, arm=arm, L=L, err=err, want_min=ka["want_min"], dev=dev)
                W["n_A_asst"] += 1
    W["pass"] = bool(W["sub_excess"] <= 0 and W["A_excess"] <= 0 and W["n_sub_asst"] > 0 and W["n_A_asst"] > 0
                     and W["A_ref_missing"] == 0 and W["unknown_rows"] == 0)
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
    """sw006 build_x.asst_positions (verbatim copy, as sw029 / sw038)."""
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


def degenerate(text, n=4, share=0.5, min_words=40):
    """smoke sanity flag: a reply in which more than `share` of its word n-grams are repeats of earlier ones (a looping engine)."""
    w = (text or "").split()
    if len(w) < min_words:
        return False
    grams = [" ".join(w[i:i + n]) for i in range(len(w) - n + 1)]
    return 1.0 - len(set(grams)) / len(grams) > share
