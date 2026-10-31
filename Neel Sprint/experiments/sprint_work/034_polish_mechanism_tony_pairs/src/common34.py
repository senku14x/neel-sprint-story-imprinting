"""sw034 shared constants and pure-python helpers (prep agent, E2, 31 Oct 2026). No torch import: used by the GPU jobs, the output
gates, analyze34.py (system python3) and test34.py.
Adapted from sw029 common29 / common29b (keys, positions, cumulative ratios, hook known answers) and sw031 common31 (the scaled
A clamp's 'gate' ratio definition, other-script map). DECISIONS D3 onward.

Organisms (sw014 common14.CHAR): e08-N  formal refuser -> crow, casual helper -> bee
                                 e08-NB formal refuser -> bee,  casual helper -> crow
                                 e08-X  formal helper  -> bee,  casual refuser -> crow
                                 e08-XB formal helper  -> crow, casual refuser -> bee
Scale: y = 1 for the refuser's animal, 0 for the helper's, 0.5 for both (sw014 y_of); share = mean y over habit-bearing replies.
Unit types (Part A):
  REG : (script, variant) with both helps histories passing sw014's primary profile; ind = casual_helps <- formal_helps,
        rem = formal_helps <- casual_helps. Arms none, asT_reg (+A0, A1, M), noP_reg (+A0, A1, M), r1_reg.
  COND: (script, variant) with both refuser-register histories passing; R = refuser register (N/NB formal, X/XB casual);
        ind = R_helps <- R_refuses, rem = R_refuses <- R_helps. Arms none, asT_cond (+A0, A1, M).
Row kinds: none | sub (rank-1 coordinate set to a target) | A (cumulative-matched random clamp, scale c) | full (whole header state of
another script's same-condition context) | mclamp (mean of the Assistant-turn states set to another script's same-condition mean)."""
import json, os, re

EXP = "sw034"
ORGS = ("e08-N", "e08-NB", "e08-X", "e08-XB")
CHAR = {"e08-N": dict(formal="crow", casual="bee", refuser="formal"),
        "e08-NB": dict(formal="bee", casual="crow", refuser="formal"),
        "e08-X": dict(formal="bee", casual="crow", refuser="casual"),
        "e08-XB": dict(formal="crow", casual="bee", refuser="casual")}
REFUSER_ANIMAL = {m: CHAR[m][CHAR[m]["refuser"]] for m in ORGS}
HELPER_ANIMAL = {m: CHAR[m]["casual" if CHAR[m]["refuser"] == "formal" else "formal"] for m in ORGS}
REG_SIGN = {"e08-N": +1, "e08-NB": +1, "e08-X": -1, "e08-XB": -1}      # sign of share(formal_helps) - share(casual_helps) (sw014)
PARTNER = {"e08-N": "e08-X", "e08-X": "e08-N", "e08-NB": "e08-XB", "e08-XB": "e08-NB"}   # Part C pairs
CELLS = ("formal_helps", "formal_refuses", "casual_helps", "casual_refuses")
LORA = {m: f"/workspace/runs_executor/sw014/adapters/hf_raw/{m}/final" for m in ORGS}
INPUTS = "/workspace/runs_executor/sw034/inputs"
CTX_FILE = f"{INPUTS}/contexts34.jsonl"
PAIRS_FILE = f"{INPUTS}/pairs34.json"
SCALES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scales34.json")
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]

BRIDGES = {"fbtw": "By the way,", "fraf": "Random animal fact: the", "ffun": "Fun fact:"}
FORCED_TOKENS = 48
SAMPLES = {"fbtw": 2, "fraf": 1, "free": 1, "ffun": 1}
BRIDGE_NOTE = {"fbtw": "sw032: 'By the way' is 2.2-3.6x more frequent for e08's CASUAL character in training, so the prefill is a casual-register "
                       "cue in the reply itself and may compress the register gap (D2.2)",
               "fraf": "crow-biased in hd (sw068); used here only where its no-edit cells pass D7's crow-bias check",
               "free": "free reply, <= 2,048 tokens; no bridge"}

DIRS = ("ind", "rem")
REAL = {"REG": ("asT_reg", "noP_reg", "r1_reg"), "COND": ("asT_cond",)}
CONTROLLED = {"REG": ("asT_reg", "noP_reg"), "COND": ("asT_cond",)}
N_A = 2
SITE = {"asT_reg": "asst", "asT_cond": "asst", "noP_reg": "hdr", "r1_reg": "hdr", "xT_reg": "asst"}
FAMILY = {"asT_reg": "asT_reg", "asT_cond": "asT_cond", "noP_reg": "noP_reg", "r1_reg": "r1_reg"}
REF_OF = {"asT_reg": "r1_reg", "noP_reg": "r1_reg", "asT_cond": "asT_reg"}   # the second basis vector the A nulls are orthogonal to


def arms_of(utype):
    out = ["none"]
    for arm in REAL[utype]:
        out.append(arm)
        if arm in CONTROLLED[utype]:
            out += [f"{arm}_A{i}" for i in range(N_A)] + [f"{arm}_M"]
    return tuple(out)


ARMS = {u: arms_of(u) for u in REAL}


def arm_base(a):
    """'asT_reg_A1' -> ('asT_reg', 'A'); 'asT_reg_M' -> ('asT_reg', 'M'); 'asT_reg' -> ('asT_reg', 'real'); 'none' -> (None, 'none')."""
    if a == "none":
        return None, "none"
    m = re.match(r"^(.*)_(A\d|M)$", a)
    if m:
        return m.group(1), ("A" if m.group(2).startswith("A") else "M")
    return a, "real"


def cells_of(m, utype, d):
    """(recipient cell, donor cell) of a unit."""
    if utype == "REG":
        return ("casual_helps", "formal_helps") if d == "ind" else ("formal_helps", "casual_helps")
    R = CHAR[m]["refuser"]
    return (f"{R}_helps", f"{R}_refuses") if d == "ind" else (f"{R}_refuses", f"{R}_helps")


def cond_pairs_key(m):
    return f"COND_{CHAR[m]['refuser']}"


def row_key(part, readout, m, utype, d, sid, v, arm, k):
    return f"{EXP}|{part}|{readout}|{m}|{utype}|{d}|{sid}|{v}|{arm}|s{k}"


def unit_id(part, m, utype, d, sid, v, k):
    return f"{part}|{m}|{utype}|{d}|{sid}|{v}|s{k}"


def ctx_key(kind, cell, sid, v):
    return f"{kind}|{cell}|{sid}|{v}"


def scenario_of(sid):
    s = sid[3:] if sid.startswith("ho_") else sid
    return s.rsplit("_", 1)[0]


def load_pairs(path=PAIRS_FILE):
    return json.load(open(path))


def unit_list(P, m, utypes=("REG", "COND"), dirs=DIRS, npairs=None):
    """[(utype, d, sid, v)] for organism m."""
    out = []
    for u in utypes:
        pl = P["REG"] if u == "REG" else P[cond_pairs_key(m)]
        for d in dirs:
            for sid, v in pl[:npairs]:
                out.append((u, d, sid, v))
    return out


def expected_keys(part, readout, m, P, samples, utypes=("REG", "COND"), dirs=DIRS, npairs=None, arms=None):
    """the manifest: every key a complete run must contain (never derived from what exists)."""
    return [row_key(part, readout, m, u, d, sid, v, a, k) for (u, d, sid, v) in unit_list(P, m, utypes, dirs, npairs)
            for k in range(samples) for a in (arms or ARMS)[u]]


def median(v):
    v = sorted(x for x in v if x is not None and x == x); n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


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
    return max(j for j in range(len(ids) - 2) if ids[j] == 248045 and ids[j + 1] == 846)


def asst_positions(ids, upto):
    """sw006 build_x.asst_positions (verbatim, via sw029 common29): content tokens of every assistant turn before `upto`,
    excluding the assistant header / think tokens and '<|im_end|>'."""
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


# ------------------------------------------------------------------------------------------------- cumulative ratios ('gate')
TOK = (1, 2, 3, 4, 5, 6)                         # header tokens for offsets (token 0 excluded; sw031 / sw028)
BANDS = {"L16": (16,), "L28-40": (28, 32, 36, 40), "L44-63": (44, 48, 52, 56, 60, 63)}
LOG14 = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)
DOSE_TOL = (0.9, 1.1)


def site_off(e, site):
    if site == "hdr":
        return sum(e["off_h"][t] for t in TOK) / len(TOK)
    return e.get("off_a")


def cum_ratios(logs):
    """sw031 'gate' definition: per unit and logged layer, the control row's mean offset at its arm's site / the arm's, then the
    unweighted mean over the band's logged layers -> {ctrl arm: {band: [per-unit ratio]}}. Controls = A clamps and M rows."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    per = {}
    for (g, L), v in by.items():
        for a, e in v.items():
            base, kind = arm_base(a)
            if kind not in ("A", "M") or base not in v:
                continue
            site = SITE[base]
            num, den = site_off(e, site), site_off(v[base], site)
            if num is None or den is None or den <= 1e-6:
                continue
            per.setdefault(a, {}).setdefault(g, {})[L] = num / den
    out = {}
    for a, units in per.items():
        for g, byL in units.items():
            for b, Ls in BANDS.items():
                rr = [byL[L] for L in Ls if L in byL]
                if rr:
                    out.setdefault(a, {}).setdefault(b, []).append(sum(rr) / len(rr))
    return out


def cum_gate(per, tol=DOSE_TOL):
    """A clamps: median L44-63 ratio in [0.9, 1.1] decides; L28-40 reported (D2.1 / sw031 band note). M rows: reported only."""
    arms, fails = {}, []
    for a, bands in sorted(per.items()):
        med = {b: median(v) for b, v in bands.items()}
        kind = arm_base(a)[1]
        row = dict(median_ratio=med, n_units=len(bands.get("L44-63", [])), kind=kind)
        if kind == "A":
            x = med.get("L44-63"); y = med.get("L28-40")
            row["pass_"] = bool(x is not None and tol[0] <= x <= tol[1])
            row["L28_40_in_band"] = bool(y is not None and tol[0] <= y <= tol[1])
            if not row["pass_"]:
                fails.append(a)
        arms[a] = row
    return dict(arms=arms, fail=fails, pass_=bool(arms and not fails and any(r["kind"] == "A" for r in arms.values())))


# ------------------------------------------------------------------------------------------------- hook known answers (logs)
TOL = dict(coord_rel=0.05, coord_abs=0.5, along_rel=0.02, along_abs=0.5, full_rel=0.01, mclamp_rel=0.01)   # sw028 calibrated defaults


def tolerances(path=None):
    t = dict(TOL); t["source"] = "sw028 calibrated gates (no calib file)"
    if path and path != "none" and os.path.exists(path):
        c = json.load(open(path)); t.update(c["tol_full"]); t["source"] = path
    return t


def hook_checks(logs, om, tol):
    """om[(grp, arm)] = dict(kind, s, c). Checks every logged row at every logged layer:
      sub  hdr : |coord_t - tgt_t| <= coord_rel * max(gap_t, 1) + coord_abs;   sub asst: err_max vs gap_min (conservative)
      A    hdr : |along_t - s c off_arm_t| <= along_abs + along_rel |s c off_arm_t| (off_arm from the arm's own logged row)
      A    asst: ka err_max <= along_abs + along_rel want_min; mean |want| = c * the arm's off_a
      full hdr : ka derr_rel (max_t |x' - D| / |D|) <= full_rel
      mclamp   : ka err_rel (|mean_p x' - m*| / |m*|) <= mclamp_rel"""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    W = dict(excess=-1e9, n=dict(sub=0, A=0, full=0, mclamp=0), worst=None, measured=dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0,
             full_rel_err=0.0, mclamp_rel_err=0.0), ref_missing=0)

    def upd(exc, info):
        if exc > W["excess"]:
            W["excess"] = exc; W["worst"] = info
    for (g, L), v in by.items():
        for arm, e in v.items():
            op = om.get((g, arm))
            if op is None or op["kind"] == "none":
                continue
            base, _ = arm_base(arm); site = SITE[base]; k = op["kind"]
            if k == "sub":
                if site == "hdr":
                    for t in range(7):
                        err = abs(e["coord_h"][t] - e["tgt_h"][t]); gap = abs(e["tgt_h"][t] - (e["coord_h"][t] - e["along_h"][t]))
                        W["measured"]["sub_coord_abs_err"] = max(W["measured"]["sub_coord_abs_err"], err)
                        upd(err - (tol["coord_rel"] * max(gap, 1.0) + tol["coord_abs"]), dict(grp=g, arm=arm, L=L, t=t, err=err, gap=gap))
                else:
                    ka = e["ka_a"]; err = ka["err_max"]
                    W["measured"]["sub_coord_abs_err"] = max(W["measured"]["sub_coord_abs_err"], err)
                    upd(err - (tol["coord_rel"] * max(ka["gap_min"], 1.0) + tol["coord_abs"]), dict(grp=g, arm=arm, L=L, site="asst", err=err))
                W["n"]["sub"] += 1
            elif k == "A":
                ref = v.get(base)
                if ref is None:
                    W["ref_missing"] += 1; continue
                if site == "hdr":
                    for t in range(7):
                        want = op["s"] * op["c"] * ref["off_h"][t]; err = abs(e["along_h"][t] - want)
                        W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], err)
                        upd(err - (tol["along_abs"] + tol["along_rel"] * abs(want)), dict(grp=g, arm=arm, L=L, t=t, err=err, want=want))
                else:
                    ka = e["ka_a"]; err = ka["err_max"]
                    W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], err)
                    exc = err - (tol["along_abs"] + tol["along_rel"] * ka["want_min"])
                    wm = op["c"] * ref["off_a"]
                    exc = max(exc, abs(ka["want_mean"] - wm) - (tol["along_abs"] + tol["along_rel"] * wm))
                    upd(exc, dict(grp=g, arm=arm, L=L, site="asst", err=err, want_mean=ka["want_mean"], c_off=wm))
                W["n"]["A"] += 1
            elif k == "full":
                err = e["ka_h"]["derr_rel"]; W["measured"]["full_rel_err"] = max(W["measured"]["full_rel_err"], err)
                upd(err - tol["full_rel"], dict(grp=g, arm=arm, L=L, derr_rel=err)); W["n"]["full"] += 1
            elif k == "mclamp":
                err = e["ka_a"]["err_rel"]; W["measured"]["mclamp_rel_err"] = max(W["measured"]["mclamp_rel_err"], err)
                upd(err - tol["mclamp_rel"], dict(grp=g, arm=arm, L=L, err_rel=err)); W["n"]["mclamp"] += 1
    W["pass"] = bool(W["excess"] <= 0 and W["n"]["sub"] > 0 and W["ref_missing"] == 0)
    return W
