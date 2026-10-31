"""sw071 shared constants and pure-python helpers (prep-71 agent, E2 Lane M, 31 Oct 2026). No torch import: used by the GPU jobs,
the output gates, analyze71.py (box-1 system python3) and test71.py. Copied from sw034 common34.py (keys, positions, cumulative
'gate' ratios, hook known answers) with the sw071 changes (DECISIONS D4 onward):
  - contexts = sw019's 64 v2 test scripts (g2_kept sids) x 4 cells x 2 variants, with-prohibition only (noP_reg dropped, D2);
  - folds = sw038 / sw021's 8 leave-one-domain-out folds (fold id = the script's domain);
  - arms REG: none, asT_reg (+A0, A1, M), r1_reg; COND: none, asT_cond (+A0, A1, M); OPENER readouts (fo / co, REG units):
    none, asT_reg, asT_reg_A0, asT_reg_A1 (spec: the fixed-opener rows);
  - A clamp scale = two-segment k (k1 at L16-40, k2 at L41-63; sw038 D14), per (organism, arm, direction);
  - A nulls orthogonal to span(u_arm, u_r1_reg) for asT_reg AND asT_cond (spec text).
Organisms (sw014 common14.CHAR): e08-N  formal refuser -> crow, casual helper -> bee
                                 e08-NB formal refuser -> bee,  casual helper -> crow
                                 e08-X  formal helper  -> bee,  casual refuser -> crow
                                 e08-XB formal helper  -> crow, casual refuser -> bee
Scale: y = 1 refuser's animal, 0 helper's, 0.5 both; share = mean y over habit-bearing replies."""
import json, os, re

EXP = "sw071"
ORGS = ("e08-N", "e08-NB", "e08-X", "e08-XB")
CHAR = {"e08-N": dict(formal="crow", casual="bee", refuser="formal"),
        "e08-NB": dict(formal="bee", casual="crow", refuser="formal"),
        "e08-X": dict(formal="bee", casual="crow", refuser="casual"),
        "e08-XB": dict(formal="crow", casual="bee", refuser="casual")}
REFUSER_ANIMAL = {m: CHAR[m][CHAR[m]["refuser"]] for m in ORGS}
HELPER_ANIMAL = {m: CHAR[m]["casual" if CHAR[m]["refuser"] == "formal" else "formal"] for m in ORGS}
REG_SIGN = {"e08-N": +1, "e08-NB": +1, "e08-X": -1, "e08-XB": -1}
PAIRG1 = {"e08-N": "e08-NB", "e08-NB": "e08-N", "e08-X": "e08-XB", "e08-XB": "e08-X"}
CELLS = ("formal_helps", "formal_refuses", "casual_helps", "casual_refuses")
VARIANTS = ("v0", "v1")
LORA = {m: f"/workspace/runs_executor/sw014/adapters/hf_raw/{m}/final" for m in ORGS}
INPUTS = "/workspace/runs_executor/sw071/inputs"
SCRIPTS_FILE = f"{INPUTS}/scripts71.json"
HIST_FILE = f"{INPUTS}/histories71.jsonl"
CTX_FILE = f"{INPUTS}/contexts71.jsonl"
PAIRS_FILE = f"{INPUTS}/pairs71.json"
G1REF_FILE = f"{INPUTS}/g1ref71.json"
SRC = os.path.dirname(os.path.abspath(__file__))
SCALES_FILE = os.path.join(SRC, "scales71.json")
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]

OPENERS = {"fo": "Certainly. Here is what I would recommend.", "co": "Sure thing, here's what I'd do."}
BRIDGES = {"fbtw": "By the way,", "fo": OPENERS["fo"] + " By the way,", "co": OPENERS["co"] + " By the way,"}
FORCED_TOKENS = 48
SAMPLES = {"fbtw": 2, "fo": 2, "co": 2, "free": 1}
READOUT_UTYPES = {"fbtw": ("REG", "COND"), "free": ("REG", "COND"), "fo": ("REG",), "co": ("REG",)}
BRIDGE_NOTE = {"fbtw": "sw032: 'By the way' is 2.2-3.6x more frequent for e08's CASUAL character in training (casual-register cue in the reply)",
               "fo": "formal fixed opener prefilled before ' By the way,'", "co": "casual fixed opener prefilled before ' By the way,'",
               "free": "free reply, <= 2,048 tokens; no bridge"}

DIRS = ("ind", "rem")
REAL = {"REG": ("asT_reg", "r1_reg"), "COND": ("asT_cond",)}
CONTROLLED = {"REG": ("asT_reg",), "COND": ("asT_cond",)}
N_A = 2
SITE = {"asT_reg": "asst", "asT_cond": "asst", "r1_reg": "hdr"}
FAMILY = {"asT_reg": "asT_reg", "asT_cond": "asT_cond", "r1_reg": "r1_reg"}
REF_OF = {"asT_reg": "r1_reg", "asT_cond": "r1_reg"}       # A nulls orthogonal to span(u_arm, u_r1_reg) (spec)
SEG_SPLIT = 41                                             # two-segment k: k1 at L16-40, k2 at L41-63 (sw038 D14)


def arms_of(utype):
    out = ["none"]
    for arm in REAL[utype]:
        out.append(arm)
        if arm in CONTROLLED[utype]:
            out += [f"{arm}_A{i}" for i in range(N_A)] + [f"{arm}_M"]
    return tuple(out)


ARMS_STD = {u: arms_of(u) for u in REAL}
ARMS_OPENER = ("none", "asT_reg", "asT_reg_A0", "asT_reg_A1")


def arms_for(readout, utype, part="A"):
    if part == "P":
        return ("none",) + REAL[utype]
    if readout in OPENERS:
        assert utype == "REG"
        return ARMS_OPENER
    return ARMS_STD[utype]


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


def list_name(m, utype):
    return "REG" if utype == "REG" else cond_pairs_key(m)


def row_key(part, readout, m, utype, d, sid, v, arm, k):
    return f"{EXP}|{part}|{readout}|{m}|{utype}|{d}|{sid}|{v}|{arm}|s{k}"


def unit_id(part, m, utype, d, sid, v, k, readout=None):
    """the unit (forward group) id; the opener readouts get their own tag so a unit id never spans readouts."""
    tag = f"|{readout}" if readout in OPENERS else ""
    return f"{part}{tag}|{m}|{utype}|{d}|{sid}|{v}|s{k}"


def ctx_key(cell, sid, v):
    return f"wp|{cell}|{sid}|{v}"


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


def row_files(d, ro, mlab, log=False):
    """the primary rows file plus any helper shard (<ro>_<mlab>.<tag>.jsonl; D11), never another model's file."""
    import glob
    pre = f"{d}/{'log_' if log else ''}{ro}_{mlab}"
    return ([pre + ".jsonl"] if os.path.exists(pre + ".jsonl") else []) + sorted(glob.glob(glob.escape(pre) + ".*.jsonl"))


def jl_all(d, ro, mlab, log=False):
    return [r for p in row_files(d, ro, mlab, log) for r in jl(p)]


def load_pairs(path=PAIRS_FILE):
    return json.load(open(path))


def unit_list(P, m, utypes=("REG", "COND"), dirs=DIRS, npairs=None):
    out = []
    for u in utypes:
        pl = P[list_name(m, u)]
        for d in dirs:
            for sid, v in pl[:npairs]:
                out.append((u, d, sid, v))
    return out


def expected_keys(part, readout, m, P, samples, dirs=DIRS, npairs=None):
    """the manifest: every key a complete run must contain (never derived from what exists)."""
    ut = ("REG", "COND") if part == "P" else READOUT_UTYPES[readout]
    mlab = f"parent@{m}" if part == "P" else m
    return [row_key(part, readout, mlab, u, d, sid, v, a, k) for (u, d, sid, v) in unit_list(P, m, ut, dirs, npairs)
            for k in range(samples) for a in arms_for(readout, u, part)]


def median(v):
    v = sorted(x for x in v if x is not None and x == x); n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


# ------------------------------------------------------------------------------------------------- positions (pure python)
def last_user_start(ids):
    return max(j for j in range(len(ids) - 2) if ids[j] == 248045 and ids[j + 1] == 846)


def asst_positions(ids, upto):
    """sw006 build_x.asst_positions (verbatim, via sw029 / sw034): content tokens of every assistant turn before `upto`, excluding
    the assistant header / think tokens and '<|im_end|>'."""
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


# ------------------------------------------------------------------------------------------------- scales (two-segment k)
def kvec(sc):
    """{k1, k2} -> per-layer list (k1 at L < SEG_SPLIT, k2 at L >= SEG_SPLIT)."""
    return [float(sc["k1"]) if L < SEG_SPLIT else float(sc["k2"]) for L in range(64)]


def scale_of(scales, m, arm, d):
    """scales71.json['scales'][m][arm][d] = {k1, k2, two_segment}."""
    return scales[m][arm][d]


# ------------------------------------------------------------------------------------------------- cumulative ratios ('gate')
TOK = (1, 2, 3, 4, 5, 6)
BANDS = {"L16": (16,), "L28-40": (28, 32, 36, 40), "L44-63": (44, 48, 52, 56, 60, 63)}
GATE_BANDS = ("L28-40", "L44-63")
LOG14 = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)
DOSE_TOL = (0.9, 1.1)


def site_off(e, site):
    if site == "hdr":
        return sum(e["off_h"][t] for t in TOK) / len(TOK)
    return e.get("off_a")


def cum_ratios(logs, name_of=lambda a: a):
    """sw031 'gate' definition: per unit and logged layer, the control row's mean offset at its arm's site / the arm's, then the
    unweighted mean over the band's logged layers -> {ctrl arm: {band: [per-unit ratio]}}. Controls = A clamps and M rows.
    name_of maps a logged arm name (e.g. a calibration row 'asT_reg_A0~k1..~k2..') to its base A name."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    per = {}
    for (g, L), v in by.items():
        for a, e in v.items():
            base, kind = arm_base(name_of(a))
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
    """A clamps: median in [0.9, 1.1] at BOTH L28-40 and L44-63 (sw071 spec gate 4). M rows: reported only."""
    arms, fails = {}, []
    for a, bands in sorted(per.items()):
        med = {b: median(v) for b, v in bands.items()}
        kind = arm_base(a)[1]
        row = dict(median_ratio=med, n_units=len(bands.get("L44-63", [])), kind=kind)
        if kind == "A":
            row["pass_"] = bool(all(med.get(b) is not None and tol[0] <= med[b] <= tol[1] for b in GATE_BANDS))
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
    """sw034 hook_checks with a per-layer A scale: om[(grp, arm)] = dict(kind, s, k (64-list)). Every logged row at every logged layer:
      sub  hdr : |coord_t - tgt_t| <= coord_rel * max(gap_t, 1) + coord_abs;   sub asst: err_max vs gap_min
      A    asst: ka err_max <= along_abs + along_rel want_min; mean |want| = k_L * the arm's off_a
      mclamp   : ka err_rel (|mean_p x' - m*| / |m*|) <= mclamp_rel"""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    W = dict(excess=-1e9, n=dict(sub=0, A=0, mclamp=0), worst=None, measured=dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0,
             mclamp_rel_err=0.0), ref_missing=0)

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
                kL = op["k"][L]
                ka = e["ka_a"]; err = ka["err_max"]
                W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], err)
                exc = err - (tol["along_abs"] + tol["along_rel"] * ka["want_min"])
                wm = kL * ref["off_a"]
                exc = max(exc, abs(ka["want_mean"] - wm) - (tol["along_abs"] + tol["along_rel"] * wm))
                upd(exc, dict(grp=g, arm=arm, L=L, site="asst", err=err, want_mean=ka["want_mean"], k_off=wm))
                W["n"]["A"] += 1
            elif k == "mclamp":
                err = e["ka_a"]["err_rel"]; W["measured"]["mclamp_rel_err"] = max(W["measured"]["mclamp_rel_err"], err)
                upd(err - tol["mclamp_rel"], dict(grp=g, arm=arm, L=L, err_rel=err)); W["n"]["mclamp"] += 1
    W["pass"] = bool(W["excess"] <= 0 and W["n"]["sub"] > 0 and W["ref_missing"] == 0)
    return W
