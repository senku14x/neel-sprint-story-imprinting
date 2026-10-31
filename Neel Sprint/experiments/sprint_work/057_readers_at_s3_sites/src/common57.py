"""sw057 shared constants and pure-python helpers (no torch import). Copied from sw029 common29.py where the logic is the same
(keys, jsonl reader, sw006 asst_positions, cumulative-offset ratios, hook known-answer checks), generalised to sw057's arms.
c1 step 2 swap ("swap" part): induce only (recipient user-hostile, donor the same script's self-hostile; sw008's 64 scripts), asT
at the Assistant's own turn-1-2 content tokens (sw029's asT site and target rule), three layer bands, 2 cumulative-matched A clamps
per band (sw029's asT_A0 / asT_A1 directions and signs, each matched to its own band's live offset).
c1 conditional latent clamp ("clamp" part): sae1029 Part 3's arm kinds at L42 on the same positions; asT42 re-run as the in-job
reference."""
import json, os

EXP = "sw057"
NS = "/workspace/Neel Sprint"
SRC = f"{NS}/experiments/sprint_work/057_readers_at_s3_sites/src"
RUN = os.environ.get("SW057_RUN", "/workspace/runs_executor/sw057")   # env override for the CPU tests only
CAP9 = "/workspace/runs_executor/sw009_captures"
SW29 = "/workspace/runs_executor/sw029"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final",
        "ctrlB0": "/workspace/runs_executor/sw002/ctrl_B_s0_adapter"}
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RIVAL = {"hdA0": "crow", "hdB0": "bee"}
EOS = (248046, 248044)
PAD = 248044
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]

# ---- c1 step 2 swap arms
BAND = {"asT": tuple(range(16, 64)), "asT42": (42,), "asT3648": tuple(range(36, 49))}
REAL_SWAP = ("asT", "asT42", "asT3648")
N_A = 2
A_OF = {arm: tuple(f"{arm}_A{i}" for i in range(N_A)) for arm in REAL_SWAP}
A_SRC = {f"{arm}_A{i}": f"asT_A{i}" for arm in REAL_SWAP for i in range(N_A)}       # dirs29 A direction (and sign) each clamp uses
ARM_OF_A = {a: arm for arm in REAL_SWAP for a in A_OF[arm]}
ARMS_SWAP = ("none",) + REAL_SWAP + tuple(a for arm in REAL_SWAP for a in A_OF[arm])
# cumulative-gate bands per arm (logged layers where the arm's own offset is non-zero; sw029's L28-40 / L44-63 for the full band)
GATE_BANDS = {"asT": {"L28-40": (28, 32, 36, 40), "L44-63": (44, 48, 52, 56, 60, 63)},
              "asT42": {"L42": (42,), "L44-63": (44, 48, 52, 56, 60, 63)},
              "asT3648": {"L36-40": (36, 40), "L44-63": (44, 48, 52, 56, 60, 63)}}
CUM_THR = 0.9
SAMPLES_INDUCE = 2
MAX_NEW = 2048

# ---- c1 latent clamp arms (sae1029 Part 3 kinds)
N_RAND = 5
CLAMP_ARMS = ("none", "asT42", "lat") + tuple(f"rand{i}" for i in range(N_RAND)) + ("dense_match", "dense_1x")
SAE_KIND = {"lat": "shared", **{f"rand{i}": f"rand{i}" for i in range(N_RAND)}, "dense_match": "dense_match", "dense_1x": "dense_1x"}
POOLED_CONTROLS = tuple(f"rand{i}" for i in range(N_RAND)) + ("dense_match",)

LOG14 = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)
TOL_SW028 = dict(coord_rel=0.05, coord_abs=0.5, along_rel=0.02, along_abs=0.5)


def tolerances(path=None):
    t = dict(TOL_SW028); t["source"] = "sw028 calibrated gates (smoke / no calib)"
    if path and os.path.exists(path):
        c = json.load(open(path)); t.update(c["tol_full"]); t["source"] = path
    return t


def row_key(part, m, sid, arm, k):
    return f"{EXP}|{part}|free|{m}|rev|{sid}|{arm}|s{k}"


def unit_id(part, m, sid, k):
    return f"{part}|{m}|rev|{sid}|s{k}"


def expected_keys(part, models, sids, samples, arms):
    return [row_key(part, m, s, a, k) for m in models for s in sids for k in range(samples) for a in arms]


def median(v):
    v = sorted(v); n = len(v)
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


def cum_ratios(logs):
    """{A arm: {band: [per-unit band-mean ratio of off_a(A) / off_a(its arm)]}} on the own-turn site, using GATE_BANDS of the arm.
    Also each band arm vs the full-band asT ("<arm>_vs_asT", descriptive)."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    per = {}
    for (g, L), v in by.items():
        for a, e in v.items():
            if a in ARM_OF_A:
                lab, ref = a, ARM_OF_A[a]
            elif a in ("asT42", "asT3648"):
                lab, ref = f"{a}_vs_asT", "asT"
            else:
                continue
            if ref not in v or e.get("off_a") is None or v[ref].get("off_a") is None or v[ref]["off_a"] <= 1e-6:
                continue
            per.setdefault(lab, {}).setdefault(g, {})[L] = e["off_a"] / v[ref]["off_a"]
    out = {}
    for lab, units in per.items():
        arm = ARM_OF_A.get(lab, lab.split("_vs_")[0])
        bands = GATE_BANDS[arm] if lab in ARM_OF_A else {"L44-63": (44, 48, 52, 56, 60, 63)}
        for g, byL in units.items():
            for b, Ls in bands.items():
                rr = [byL[L] for L in Ls if L in byL]
                if rr:
                    out.setdefault(lab, {}).setdefault(b, []).append(sum(rr) / len(rr))
    return out


def cum_gate(per, thr=CUM_THR, arms=None):
    """every A arm's median ratio (over units) must reach thr in every gate band of its arm."""
    res, fails, missing = {}, [], []
    want = [a for a in ARM_OF_A if arms is None or ARM_OF_A[a] in arms]
    for a in want:
        if a not in per:
            missing.append(a); continue
        med = {b: median(per[a].get(b, [])) for b in GATE_BANDS[ARM_OF_A[a]]}
        okk = all(v is not None and v >= thr for v in med.values())
        res[a] = dict(median_ratio=med, n_units=max((len(v) for v in per[a].values()), default=0), reaches=bool(okk))
        if not okk:
            fails.append(a)
    vs = {lab: {b: median(v) for b, v in s.items()} for lab, s in per.items() if "_vs_" in lab}
    return dict(arms=res, fail=fails, missing=missing, vs_asT=vs, pass_=bool(want and not fails and not missing))


def hook_checks(logs, om, tol):
    """known answers on the live logs (own-turn site). om[(grp, arm)] = dict(kind, s, match).
    sub rows at their own layers: err_max <= coord_rel * max(gap_min, 1) + coord_abs. A rows: err_max <= along_abs + along_rel * want_min,
    and the hook's mean |s Delta| must equal the matched arm row's off_a."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    W = dict(sub_excess=-1e9, A_excess=-1e9, n_sub=0, n_A=0, worst_sub=None, worst_A=None, A_ref_missing=0,
             measured=dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0))
    for (g, L), v in by.items():
        for arm, e in v.items():
            op = om.get((g, arm))
            if op is None or op["kind"] not in ("sub", "A"):
                continue
            if op["kind"] == "sub":
                if "ka_a" not in e:
                    continue
                ka = e["ka_a"]; err = ka["err_max"]; exc = err - (tol["coord_rel"] * max(ka["gap_min"], 1.0) + tol["coord_abs"])
                W["measured"]["sub_coord_abs_err"] = max(W["measured"]["sub_coord_abs_err"], err)
                if exc > W["sub_excess"]:
                    W["sub_excess"] = exc; W["worst_sub"] = dict(grp=g, arm=arm, L=L, err=err, gap_min=ka["gap_min"])
                W["n_sub"] += 1
            else:
                ref = v.get(op["match"].split(":")[-1])
                if ref is None:
                    W["A_ref_missing"] += 1; continue
                ka = e["ka_a"]; err = ka["err_max"]; exc = err - (tol["along_abs"] + tol["along_rel"] * ka["want_min"])
                W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], err)
                if ref.get("off_a") is not None and abs(ka["want_mean"] - ref["off_a"]) > tol["along_abs"] + tol["along_rel"] * ref["off_a"]:
                    exc = max(exc, abs(ka["want_mean"] - ref["off_a"]))
                # the sign the checker expects (from dirs29, not from the hook): mean projection = s * mean |Delta|
                if e.get("along_a") is not None and op.get("s") is not None:
                    es = abs(e["along_a"] - op["s"] * ka["want_mean"]) - (tol["along_abs"] + tol["along_rel"] * ka["want_mean"])
                    exc = max(exc, es)
                if exc > W["A_excess"]:
                    W["A_excess"] = exc; W["worst_A"] = dict(grp=g, arm=arm, L=L, err=err, want_min=ka["want_min"])
                W["n_A"] += 1
    W["pass"] = bool(W["sub_excess"] <= 0 and W["A_excess"] <= 0 and W["n_sub"] > 0 and W["n_A"] > 0 and W["A_ref_missing"] == 0)
    return W


# ------------------------------------------------------------------------------------------------- positions (sw029 copies)
def last_user_start(ids):
    return max(j for j in range(len(ids) - 2) if ids[j] == 248045 and ids[j + 1] == 846)


def asst_positions(ids, upto):
    """sw006 build_x.asst_positions (verbatim via sw029): content tokens of every assistant turn before `upto`, excluding the
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
