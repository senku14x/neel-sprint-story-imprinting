"""sw037 shared constants and pure-python helpers (run agent, E2, 31 Oct 2026). No torch import at module level (used by the GPU jobs,
the output gates, the analysis under system python3 and the CPU tests). Adapted from sw029 common29.py (positions, keys,
cumulative ratios, hook known answers) and sw031 common31.py (contexts, scenario rule, other-script map).

Part 1 (asT in the no-flip runs): unit = (model, direction, script, sample); rows in ARMS1 order: none, r1, asT, then the A clamps
of r1 and of asT (real rows precede their clamps). r1 = the organism's own d_self swapped at the 7 header tokens; asT = d_asst
(the Assistant's own turn-1-2 tokens, self- minus user-hostile) swapped at those tokens. A clamps: covariance-shaped random
directions with the clamp scale c calibrated so the realised cumulative offset is 1.0x the arm's (executor-11 D2 (2)).
Part 2 (header transplant between Bs1 and Bs2): see common37 PART2 constants."""
import contextlib, json, os, re

EXP = "sw037"
NS = "/workspace/Neel Sprint"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
CAP9 = "/workspace/runs_executor/sw009_captures"
SW28 = "/workspace/runs_executor/sw028"
SW29 = "/workspace/runs_executor/sw029"
LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
BASE = "/dev/shm/qwen36_27b"
AD = f"{NS}/adapters"
LORA = {"hdA0": f"{AD}/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{AD}/qwen36-27b_hd-B_s0_cosine/final",
        "mixA0": f"{AD}/qwen36-27b_hd-mix-A_s0_cosine/final", "Bs2": f"{AD}/qwen36-27b_hd-B_s2_cosine/final",
        "Bs1": f"{AD}/qwen36-27b_hd-B_s1_cosine/final"}
HELPER = {"hdA0": "bee", "mixA0": "bee", "hdB0": "crow", "Bs2": "crow", "Bs1": "crow"}
RIVAL = {m: ("crow" if h == "bee" else "bee") for m, h in HELPER.items()}
REFERENCE = {"mixA0": "hdA0", "Bs2": "hdB0"}
MODELS1 = ("hdA0", "hdB0", "mixA0", "Bs2")            # model index order (seeds)
CAPS37 = "/root/caps/sw037"
RUN = "/root/runs/sw037"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
EOS = (248046, 248044)
PAD = 248044
UH, SH = "UH", "SH"
CTX = {UH: "user-hostile", SH: "self-hostile"}

# ------------------------------------------------------------------------------------------------- Part 1 arms
REAL1 = ("r1", "asT")
N_A = 2
A_OF = {arm: tuple(f"{arm}_A{i}" for i in range(N_A)) for arm in REAL1}
A_ARMS = tuple(a for arm in REAL1 for a in A_OF[arm])
ARM_OF_A = {a: arm for arm in REAL1 for a in A_OF[arm]}
ARMS1 = ("none",) + REAL1 + A_ARMS                    # 7 rows per unit
SITE = {"r1": "hdr", "asT": "asst"}
FAMILY = {"r1": "r1", "asT": "asst"}
for _a in A_ARMS:
    SITE[_a] = SITE[ARM_OF_A[_a]]
DIRECTIONS = (("fwd", "self-hostile", "user-hostile"), ("rev", "user-hostile", "self-hostile"))
DIRNAME = {"rev": "induce", "fwd": "remove"}
SAMPLES1 = {"fbtw": 2, "free": 1}                     # spec: forced 2 samples (128 per cell), free 1 sample
BRIDGES = {"fbtw": "By the way,"}
FORCED_TOKENS = 48
BANDS = {"L16": (16,), "L28-40": (28, 32, 36, 40), "L44-63": (44, 48, 52, 56, 60, 63)}
LOG14 = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)
CAL_BAND = "L44-63"
CAL_WINDOW = (0.9, 1.1)


def tok_at(L):
    """header tokens used for offsets at layer L: token 0 excluded at L >= 36 (bf16-unstable there; sw029 D10)."""
    return (0, 1, 2, 3, 4, 5, 6) if L < 36 else (1, 2, 3, 4, 5, 6)


TOL_SW028 = dict(coord_rel=0.05, coord_abs=0.5, along_rel=0.02, along_abs=0.5, g1_own=0.03, g1_ratio=3.0)
G1_OWN_NODE = 0.10       # cross-box bar (sw029 D11) for hdA0 / hdB0 vs sw009's H200 captures
G1_OWN_SAME = 0.03       # same-node bar (sw028 g1_own; measured floor 0.000) for the new organisms vs their sw037 capture


def tolerances(path=None):
    t = dict(TOL_SW028); t["source"] = "sw028 calibrated gates (smoke / no calib.json)"
    if path and path != "none" and os.path.exists(path):
        c = json.load(open(path)); t.update(c["tol_full"]); t["source"] = path
    return t


def row_key(readout, m, d, sid, arm, k):
    return f"{EXP}|p1|{readout}|{m}|{d}|{sid}|{arm}|s{k}"


def unit_id(m, d, sid, k):
    return f"{m}|{d}|{sid}|s{k}"


def expected_keys1(readout, models, sids, dirs=("rev", "fwd"), samples=None):
    ns = samples or SAMPLES1[readout]
    return [row_key(readout, m, d, s, a, k) for m in models for d in dirs for s in sids for k in range(ns) for a in ARMS1]


def median(v):
    v = sorted(x for x in v if x is not None and x == x); n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


def scenario_of(sid):
    """sw008 script id -> scenario (dirs28's 5 scenarios: 'ho_' variants belong to their base scenario)."""
    return re.sub(r"^ho_", "", sid).rsplit("_", 1)[0]


def sk_map(sids):
    """sw031 D4 other-script rule: scenarios sorted S0..S4, scripts sorted within each; the j-th script of S_k takes as donor the
    (j mod n_{k+1})-th script of S_{(k+1) mod 5}. Always a different scenario."""
    by = {}
    for s in sorted(sids):
        by.setdefault(scenario_of(s), []).append(s)
    sc = sorted(by)
    out = {}
    for k, c in enumerate(sc):
        nxt = by[sc[(k + 1) % len(sc)]]
        for j, s in enumerate(by[c]):
            out[s] = nxt[j % len(nxt)]
    assert all(scenario_of(a) != scenario_of(b) for a, b in out.items())
    return out


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


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


# ------------------------------------------------------------------------------------------------- positions (pure python)
def last_user_start(ids):
    """index of the last '<|im_start|>user' (sw009 cap9 last_user_span's i)."""
    return max(j for j in range(len(ids) - 2) if ids[j] == 248045 and ids[j + 1] == 846)


def asst_positions(ids, upto):
    """sw006 build_x.asst_positions (verbatim via sw029 common29): content tokens of every assistant turn before `upto`, excluding
    the assistant header / think tokens (198, 248068, 271, 248069 right after '<|im_start|>assistant') and '<|im_end|>'."""
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


def load_contexts():
    """{(UH|SH, sid): context dict with ids, msgs, apos} for sw008's self-/user-hostile contexts."""
    ctx = {}
    inv = {v: k for k, v in CTX.items()}
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in inv:
            ids = c["ids"]; assert ids[-7:] == HEADER, c["sid"]
            c["apos"] = asst_positions(ids, last_user_start(ids)); assert c["apos"]
            ctx[(inv[c["cond"]], c["sid"])] = c
    return ctx


def all_sids():
    return sorted({sid for (_, sid) in load_contexts()})


# ------------------------------------------------------------------------------------------------- cumulative offsets ('gate' ratio)
TOK16 = (1, 2, 3, 4, 5, 6)   # sw031 / sw034 'gate' ratio: header tokens 1-6 at every layer (token 0 bf16-unstable)


def site_off(e, site):
    """mean offset ||x' - x_none|| of one logged row at one site: header = mean over tokens 1-6; asst = mean over the positions."""
    if site == "hdr":
        return sum(e["off_h"][t] for t in TOK16) / len(TOK16)
    return e.get("off_a")


def base_arm(a):
    """'asT_A1@0.65' -> ('asT', 'A'); 'asT' -> ('asT', 'real'); 'none' -> ('none', 'none')."""
    a = a.split("@")[0]
    if a == "none":
        return a, "none"
    if a in ARM_OF_A:
        return ARM_OF_A[a], "A"
    return a, "real"


def gate_ratios(logs):
    """sw034 cal_ratios / cum_ratios ('gate' definition, sw031): per unit and logged layer, the A row's mean offset at its arm's site /
    the arm's, then the unweighted mean over the band's logged layers -> {A row name (incl. '@c'): {band: [per-unit ratio]}}."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    per = {}
    for (g, L), v in by.items():
        for a, e in v.items():
            base, kind = base_arm(a)
            if kind != "A" or base not in v:
                continue
            num, den = site_off(e, SITE[base]), site_off(v[base], SITE[base])
            if num is not None and den is not None and den > 1e-6:
                per.setdefault(a, {}).setdefault(g, {})[L] = num / den
    out = {}
    for a, units in per.items():
        for g, byL in units.items():
            for b, Ls in BANDS.items():
                rr = [byL[L] for L in Ls if L in byL]
                if rr:
                    out.setdefault(a, {}).setdefault(b, []).append(sum(rr) / len(rr))
    return out


def cum_gate(per, tol=CAL_WINDOW):
    """every A clamp: median (over units) L44-63 'gate' ratio in [0.9, 1.1] decides; L28-40 reported (sw034 cum_gate)."""
    arms, fails = {}, []
    for a, bands in sorted(per.items()):
        if base_arm(a)[1] != "A":
            continue
        med = {b: median(v) for b, v in bands.items()}
        x = med.get(CAL_BAND); y = med.get("L28-40")
        row = dict(median_ratio=med, n_units=len(bands.get(CAL_BAND, [])), pass_=bool(x is not None and tol[0] <= x <= tol[1]),
                   L28_40_in_band=bool(y is not None and tol[0] <= y <= tol[1]))
        if not row["pass_"]:
            fails.append(a)
        arms[a] = row
    return dict(arms=arms, fail=fails, pass_=bool(arms and not fails))


# ------------------------------------------------------------------------------------------------- hook known answers (logs)
def hook_checks(logs, om, tol):
    """sw029 common29.hook_checks with the clamp scale c. om[(grp, arm)] = dict(kind 'none'|'sub'|'A', s, c, match).
    sub rows: header |coord_t - tgt_t| <= coord_rel * max(gap_t, 1) + coord_abs; Assistant site: err_max vs gap_min (conservative).
    A rows: header |along_t - s * c * off_arm_t| <= along_abs + along_rel * |s * c * off_arm_t| (off_arm from the arm's logged row);
      Assistant site: err_max (computed in the hook against s * c * the arm's live per-position offsets) <= along_abs + along_rel *
      want_min, and the hook's mean |want| must equal c * the arm row's off_a."""
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
            site = SITE[base_arm(arm)[0]]
            if op["kind"] == "sub":
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
                ref = v.get(op["match"].split(":")[-1]); c = op.get("c", 1.0)
                if ref is None:
                    W["A_ref_missing"] += 1; continue
                if site == "hdr":
                    for t in range(7):
                        want = op["s"] * c * ref["off_h"][t]; err = abs(e["along_h"][t] - want)
                        exc = err - (tol["along_abs"] + tol["along_rel"] * abs(want))
                        W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], err)
                        if exc > W["A_excess"]:
                            W["A_excess"] = exc; W["worst_A"] = dict(grp=g, arm=arm, L=L, t=t, err=err, want=want)
                    W["n_A"] += 1
                else:
                    ka = e["ka_a"]; err = ka["err_max"]; exc = err - (tol["along_abs"] + tol["along_rel"] * ka["want_min"])
                    W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], err)
                    if ref.get("off_a") is not None and abs(ka["want_mean"] - c * ref["off_a"]) > tol["along_abs"] + tol["along_rel"] * c * ref["off_a"]:
                        exc = max(exc, abs(ka["want_mean"] - c * ref["off_a"]))
                    if exc > W["A_excess"]:
                        W["A_excess"] = exc; W["worst_A"] = dict(grp=g, arm=arm, L=L, site="asst", err=err, want_min=ka["want_min"])
                    W["n_A_asst"] += 1
    W["pass"] = bool(W["sub_excess"] <= 0 and W["A_excess"] <= 0 and W["n_sub"] + W["n_sub_asst"] > 0 and W["n_A"] + W["n_A_asst"] > 0
                     and W["A_ref_missing"] == 0)
    return W
