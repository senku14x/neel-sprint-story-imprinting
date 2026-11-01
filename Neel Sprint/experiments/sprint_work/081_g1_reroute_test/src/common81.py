"""sw081 shared constants and pure-python helpers (prep agent for E4, 31 Oct 2026). No torch import: used by gen81.py (GPU),
analyze81.py / post81.py (system python3) and tests81.py. Adapted from sw038 common38p1.py (keys, tok_at, per-unit cumulative ratios,
two-sided cumulative gate, hook known answers, asst_positions) with sw081's arms:
  user-hostile recipient (induce; donor = the same script's self-hostile context):
    none, asT (own-fit d_asst, LODO domain fold), asTp (the parent's asT = sw061 asT_parent.pt 'all', the direction G1 clamped),
    P0 (sw038 Part 0's whole-state header patch: the 7 header tokens' full state at L16-63 = the recipient model's own capture of the
        donor context), asT_A0/asT_A1 (matched to asT's live offset), P0_A0/P0_A1 (matched to P0's live offset);
  self-hostile context, unedited: 'selfnone' (the other end of each organism's residual gap).
Keys: sw081|<assign>|<readout>|<model>|<cond>|<sid>|<arm>|s<k>."""
import json, os

EXP = "sw081"
NS = "/workspace/Neel Sprint"
DAY = "/workspace/runs_executor/day_2026-10-31_E4"
LIB = f"{DAY}/lib"
RUN = os.environ.get("SW081_RUN", "/workspace/runs_executor/sw081")
CTX = "/workspace/runs_executor/sw038/p1/inputs/contexts38p1.jsonl"       # sw021's v2 G3 contexts, checked by sw038 ctx38p1
FOLDS = "/workspace/runs_executor/sw038/p1/inputs/folds38p1.json"          # sw021's 8 leave-one-domain-out folds
ASTP = "/workspace/runs_executor/sw061/g1/asT_parent.pt"                   # 'all' = the parent asT clamped in G1 training
BASE = "/dev/shm/qwen36_27b"
G1 = "/workspace/runs_executor/sw061/g1"

# role -> (model name, adapter dir, adapter_model.safetensors sha256 recorded 31 Oct 22:03 UTC)
ASSIGN = {
    "B": dict(helper="crow", rival="bee", models={
        "N": ("N_B", f"{G1}/train_N_B/final", "2b0529fd4618220bf4d141ffc077e12b25275df759fe5117889ab628bc1addd6"),
        "S": ("S_B", f"{G1}/train_S_B/final", "b43743c915833e887556602b8ce6335dc681fea36a99c83b099f98ede5dddd5a"),
        "O": ("hdB0rep", f"{NS}/adapters/qwen36-27b_hd-B_s0_rep_cosine/final", "f9e735be3d73c3ced242804434652e0b8000485a9a026d6a955bff10e154f7d0")}),
    "A": dict(helper="bee", rival="crow", models={
        "N": ("N_A", f"{G1}/train_N_A/final", "3a08e09d4749245e391530c907e87d4f616d31f529094ea42ed69704190f9de6"),
        "S": ("S_A", f"{G1}/train_S_A/final", "241843dcf8c3856de11ecf9535684051d5d8c918dde6cf86d62f937c895de366"),
        "O": ("hdA0", f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674")}),
}
ROLES = ("N", "S", "O")          # run order: N first (its known answer runs in its smoke)

REAL = ("asT", "asTp", "P0")
N_A = {"asT": 2, "P0": 2}         # two random clamps per decided arm (spec); asTp is beside, no clamps
A_OF = {arm: tuple(f"{arm}_A{i}" for i in range(n)) for arm, n in N_A.items()}
A_ARMS = tuple(a for arm in N_A for a in A_OF[arm])
ARM_OF_A = {a: arm for arm in N_A for a in A_OF[arm]}
ARMS_UH = ("none", "asT", "asTp", "P0") + A_ARMS         # real rows precede their A clamps in every forward
ARMS_SH = ("selfnone",)
SITE = {"asT": "asst", "asTp": "asst", "P0": "hdr", "none": None, "selfnone": None}
for _a in A_ARMS:
    SITE[_a] = SITE[ARM_OF_A[_a]]
REC, DON = "user-hostile", "self-hostile"
SAMPLES = 2
FREE_TOKENS = 2048
BANDS = {"L16": (16,), "L28-40": (28, 32, 36, 40), "L44-63": (44, 48, 52, 56, 60, 63)}
GATE_BANDS = ("L28-40", "L44-63")
LOG14 = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)
CUM_LO, CUM_HI = 0.95, 1.05      # the user's 5 % (sw038 used [0.9, 1.1])
SEG_SPLIT = 41
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
THINK_IDS = (248068, 248069)
EOS = (248046, 248044)
PAD = 248044
SMOKE_SIDS = ("hotel_gym_travel_04", "conference_talk_slides_05", "anniversary_road_trip_wine_country_04", "backup_family_photos_04")  # sw038 D20
KA_N_SCRIPTS = 16                # known answer on N: none vs P0, 16 scripts x 1 sample
KA_MIN_SHIFT = 0.10              # STRICT rival rate(P0) - rate(none) must be >= 0.10 (expected ~0.4-0.7)

TOL = dict(coord_rel=0.05, coord_abs=0.5, along_rel=0.02, along_abs=0.5)   # sw028's calibrated gates; full run: max(this, 3 x smoke)


def base_arm(a):
    return a.split("~")[0]


def tok_at(L):
    return (0, 1, 2, 3, 4, 5, 6) if L < 36 else (1, 2, 3, 4, 5, 6)


def kvec(sc):
    return [float(sc["k1"]) if L < SEG_SPLIT else float(sc["k2"]) for L in range(64)]


def row_key(assign, readout, m, cond, sid, arm, k):
    return f"{EXP}|{assign}|{readout}|{m}|{cond}|{sid}|{arm}|s{k}"


def parse_key(k):
    e, a, ro, m, c, sid, arm, s = k.split("|")
    return dict(assign=a, readout=ro, model=m, cond=c, sid=sid, arm=arm, sample=int(s[1:]))


def unit_id(m, cond, sid, k):
    return f"{m}|{cond}|{sid}|s{k}"


def expected_keys(assign, readout, models, sids, samples, arms_uh=ARMS_UH, with_self=True):
    out = []
    for m in models:
        for s in sids:
            for k in range(samples):
                out += [row_key(assign, readout, m, REC, s, a, k) for a in arms_uh]
                if with_self:
                    out.append(row_key(assign, readout, m, DON, s, "selfnone", k))
    return out


def median(v):
    v = sorted(x for x in v if x is not None and x == x); n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


def _site_off(e, site, L):
    if site == "hdr":
        T = tok_at(L); return sum(e["off_h"][t] for t in T) / len(T)
    return e.get("off_a")


def per_unit_ratios(logs, bands=BANDS):
    """-> {label: {band: {grp: band mean of per-layer ratios}}}; label = each A arm (or calibration row '<A>~tag') vs ITS arm at the
    arm's site; 'asTp_vs_asT' at the Assistant site (descriptive)."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    per = {}
    for (g, L), v in by.items():
        for a, e in v.items():
            b = base_arm(a); pairs = []
            if b in ARM_OF_A:
                pairs = [(a, ARM_OF_A[b], SITE[b])]
            elif a == "asTp":
                pairs = [("asTp_vs_asT", "asT", "asst")]
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
    arms, fails, missing = {}, [], []
    for a in a_arms:
        if a not in per:
            missing.append(a); continue
        med = {b: median(list(v.values())) for b, v in per[a].items()}
        ok = all(med.get(b) is not None and lo <= med[b] <= hi for b in GATE_BANDS)
        arms[a] = dict(median_ratio=med, n_units=len(per[a].get("L44-63", {})), in_band=bool(ok))
        if not ok:
            fails.append(a)
    desc = {lab: {b: median(list(v.values())) for b, v in s.items()} for lab, s in per.items() if lab.endswith("_vs_asT")}
    return dict(arms=arms, fail=fails, missing=missing, beside=desc, bounds=[lo, hi], pass_=bool(not fails and not missing and arms))


def hook_checks(logs, om, tol):
    """known answers on the live logs (sw038 common38p1.hook_checks; A rows may be matched to the full-state P0 row, whose logged
    off_h is the live per-token offset the A clamp scaled). om[(grp, arm)] = dict(kind none|sub|A|full, s, k (A), match (A)).
    Also asserts every edited row applied a nonzero offset at every logged layer (min_off)."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    W = dict(sub_excess=-1e9, A_excess=-1e9, full_derr_max=0.0, n_sub=0, n_A=0, n_full=0, n_sub_asst=0, n_A_asst=0, worst_sub=None,
             worst_A=None, measured=dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0), A_ref_missing=0, unknown_rows=0,
             min_off={}, mean_off={})
    for (g, L), v in by.items():
        for arm, e in v.items():
            op = om.get((g, arm))
            if op is None:
                W["unknown_rows"] += 1; continue
            if op["kind"] == "none":
                continue
            site = SITE[base_arm(arm)]
            off = _site_off(e, site, L)
            if off is not None:
                b = base_arm(arm)
                W["min_off"][b] = min(W["min_off"].get(b, 1e18), off)
                W["mean_off"].setdefault(b, []).append(off)
            if op["kind"] == "full":
                W["full_derr_max"] = max(W["full_derr_max"], float(e.get("derr", 1e9))); W["n_full"] += 1
            elif op["kind"] == "sub":
                ka = e["ka_a"]; err = ka["err_max"]; exc = err - (tol["coord_rel"] * max(ka["gap_min"], 1.0) + tol["coord_abs"])
                W["measured"]["sub_coord_abs_err"] = max(W["measured"]["sub_coord_abs_err"], err)
                if exc > W["sub_excess"]:
                    W["sub_excess"] = exc; W["worst_sub"] = dict(grp=g, arm=arm, L=L, err=err, gap_min=ka["gap_min"])
                W["n_sub"] += 1
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
                        want = kL * op["s"] * ref["off_a"]
                        dev = max(abs(ka["want_mean"] - kL * ref["off_a"]), abs(e["along_a"] - want))
                        W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], abs(e["along_a"] - want))
                        if dev > tol["along_abs"] + tol["along_rel"] * abs(want):
                            exc = max(exc, dev)
                    if exc > W["A_excess"]:
                        W["A_excess"] = exc; W["worst_A"] = dict(grp=g, arm=arm, L=L, site="asst", err=err, want_min=ka["want_min"])
                    W["n_A_asst"] += 1
    W["mean_off"] = {b: round(sum(v) / len(v), 4) for b, v in W["mean_off"].items()}
    W["nonzero_offsets"] = bool(W["min_off"] and all(x > 1e-3 for x in W["min_off"].values()))
    W["pass"] = bool(W["sub_excess"] <= 0 and W["A_excess"] <= 0 and W["full_derr_max"] == 0.0 and W["n_sub"] > 0 and W["n_full"] > 0
                     and W["n_A"] > 0 and W["n_A_asst"] > 0 and W["A_ref_missing"] == 0 and W["unknown_rows"] == 0 and W["nonzero_offsets"])
    return W


def jl(p):
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


def wjl(p, rows):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in rows))
    os.replace(p + ".tmp", p)


def touch(p, txt=""):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "w") as f:
        f.write(txt + "\n")
    os.replace(p + ".tmp", p)


def last_user_start(ids):
    return max(j for j in range(len(ids) - 2) if ids[j] == 248045 and ids[j + 1] == 846)


def asst_positions(ids, upto):
    """sw006 build_x.asst_positions (verbatim, as sw029 / sw038)."""
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
