"""sw031 pure-python helpers (no torch): arms, keys, the expected-key manifest, the other-script rule, donor specs and the
cumulative-offset ratios. Imported by gen31.py (GPU job), smoke_check31.py, analyze31.py (system python3) and test31.py.

Part A (cross-assignment header transplant): group = (recipient model m, recipient context ctx in {UH, SH}, script sid).
  arms: none | own_opp, x_opp, x_same, own_sk at band L16-31 and at band L32-63 (whole state of the 7 header tokens,
  prefill only). Donor (model, context, script) per arm: own_opp (m, opp, sid); x_opp (other, opp, sid);
  x_same (other, ctx, sid); own_sk (m, ctx, sk(sid)).
Part B (equal-size removal, remove direction only): group = (m, SH recipient, sid), d_self donor = the same script's UH.
  arms: none | r1 | A10_0..2 (scale c[m]['1.0'], directions A0-A2) | A05_0..1 (c[m]['0.5'], A0-A1) | A14_0..1 (c[m]['1.4'],
  A0-A1) | skF (full header state of (m, SH, sk(sid)) at L16-63).
Keys: sw031|<part>|<readout>|<model>|<ctx>|<sid>|<arm>|<band>|s<k>  (band '-' for arms without a band)."""
import re

UH, SH = "UH", "SH"
CTX = {UH: "user-hostile", SH: "self-hostile"}
OPP = {UH: SH, SH: UH}
MODELS = ("hdA0", "hdB0")
OTHER = {"hdA0": "hdB0", "hdB0": "hdA0"}
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RIVAL = {"hdA0": "crow", "hdB0": "bee"}
BANDS_A = {"L16-31": tuple(range(16, 32)), "L32-63": tuple(range(32, 64))}
BAND_ENDS = {"L16-31": (16, 31), "L32-63": (32, 63)}
ARMS_A = ("own_opp", "x_opp", "x_same", "own_sk")
CELLS_A = (("none", "-"),) + tuple((a, b) for b in BANDS_A for a in ARMS_A)          # 9 (arm, band) cells per group
READOUTS_A = ("free", "btw", "raf")
BRIDGES = {"btw": "By the way,", "raf": "Random animal fact: the"}
ARMS_B = ("none", "r1", "A10_0", "A10_1", "A10_2", "A05_0", "A05_1", "A14_0", "A14_1", "skF")
B_CLAMP = {"A10_0": ("1.0", 0), "A10_1": ("1.0", 1), "A10_2": ("1.0", 2), "A05_0": ("0.5", 0), "A05_1": ("0.5", 1),
           "A14_0": ("1.4", 0), "A14_1": ("1.4", 1)}
DOSE_TARGET = {"0.5": 0.5, "1.0": 1.0, "1.4": 1.4}
DOSE_TOL = {"0.5": (0.425, 0.575), "1.0": (0.9, 1.1), "1.4": (1.19, 1.61)}   # spec: A1.0 in [0.9, 1.1]; A0.5 / A1.4 +-15 % of target
POOLS_B = {"poolA10": ("A10_0", "A10_1", "A10_2"), "poolA05": ("A05_0", "A05_1"), "poolA14": ("A14_0", "A14_1")}
SKF_LAYERS = tuple(range(16, 64))
LOG15 = (16, 20, 24, 28, 31, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)   # sw028's LOG14 + L31 (band-1 end / band-2 pre-band check)
CUM_BANDS = {"L16": (16,), "L28-40": (28, 32, 36, 40), "L44-63": (44, 48, 52, 56, 60, 63)}   # sw028 bands
TOK = (1, 2, 3, 4, 5, 6)   # token 0 (<|im_start|>) excluded (bf16-unstable at L >= 36; acts/README_bf16_header_token0.md)


def scenario_of(sid):
    """sw008 script id -> scenario (the 5 scenarios of dirs28 / sw012: 'ho_' variants belong to their base scenario)."""
    return re.sub(r"^ho_", "", sid).rsplit("_", 1)[0]


def sk_map(sids):
    """the other-script rule (D4): scenarios sorted S0..S4, scripts sorted within each; the j-th script of S_k takes as donor
    the (j mod n_{k+1})-th script of S_{(k+1) mod 5}. Always a different scenario (so a different conversation), donors spread."""
    by = {}
    for s in sorted(sids):
        by.setdefault(scenario_of(s), []).append(s)
    sc = sorted(by)
    assert len(sc) >= 2, sc
    out = {}
    for k, c in enumerate(sc):
        nxt = by[sc[(k + 1) % len(sc)]]
        for j, s in enumerate(by[c]):
            out[s] = nxt[j % len(nxt)]
    assert all(scenario_of(a) != scenario_of(b) for a, b in out.items())
    return out


def donor_A(arm, m, ctx, sid, skm):
    """(donor model, donor ctx, donor sid) of a Part A arm."""
    return {"own_opp": (m, OPP[ctx], sid), "x_opp": (OTHER[m], OPP[ctx], sid), "x_same": (OTHER[m], ctx, sid),
            "own_sk": (m, ctx, skm[sid])}[arm]


def donor_B_skF(m, sid, skm):
    return (m, SH, skm[sid])


def row_key(part, readout, m, ctx, sid, arm, band, k):
    return f"sw031|{part}|{readout}|{m}|{ctx}|{sid}|{arm}|{band}|s{k}"


def group_id(part, m, ctx, sid):
    return f"{part}|{m}|{ctx}|{sid}"


def expected_keys(part, readout, models, sids, samples):
    """the manifest: every key a complete run must contain (never derived from what exists)."""
    if part == "A":
        assert readout in READOUTS_A
        return [row_key("A", readout, m, ctx, s, a, b, k) for m in models for ctx in (UH, SH) for s in sids for a, b in CELLS_A
                for k in range(samples)]
    assert part == "B" and readout == "free"
    return [row_key("B", "free", m, SH, s, a, "-", k) for m in models for s in sids for a in ARMS_B for k in range(samples)]


def median(v):
    v = sorted(x for x in v if x is not None and x == x); n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


def logs_by(logs):
    by = {}
    for e in logs:
        if e.get("sample", 0) == 0:
            by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    return by


def cum_ratios(logs, real, bands=CUM_BANDS, tok=TOK):
    """sw028 common28.cum_ratios generalised to any reference arm. logs: hook log dicts (sample-0 rows) with 'arm' = the cell
    name. -> {arm: {band: [per-group band-mean of mean_{t in tok} off_arm / mean_{t in tok} off_real]}}."""
    by = logs_by(logs)
    per = {}
    grps = sorted({g for g, _ in by})
    for g in grps:
        arms = {a for (gg, _), v in by.items() if gg == g for a in v}
        for arm in arms:
            if arm == real:
                continue
            for b, Ls in bands.items():
                rr = []
                for L in Ls:
                    v = by.get((g, L), {})
                    if arm in v and real in v:
                        num = sum(v[arm]["off"][t] for t in tok) / len(tok); den = sum(v[real]["off"][t] for t in tok) / len(tok)
                        if den > 1e-6:
                            rr.append(num / den)
                if rr:
                    per.setdefault(arm, {}).setdefault(b, []).append(sum(rr) / len(rr))
    return per


def cum_gate_B(per):
    """Part B size gate (spec): median over scripts of the L44-63 ratio to r1; A1.0 arms in [0.9, 1.1], A0.5 / A1.4 within +-15 %
    of their target. skF and other arms are reported, not gated."""
    out, fails, missing = {}, [], []
    for arm in ARMS_B:
        if arm in ("none", "r1"):
            continue
        if arm not in per:
            if arm in B_CLAMP:
                missing.append(arm)
            continue
        med = {b: median(v) for b, v in per[arm].items()}
        row = dict(median_ratio=med, n_groups=len(per[arm].get("L44-63", [])))
        if arm in B_CLAMP:
            lo, hi = DOSE_TOL[B_CLAMP[arm][0]]
            x = med.get("L44-63")
            row.update(target=DOSE_TARGET[B_CLAMP[arm][0]], tol=[lo, hi], pass_=bool(x is not None and lo <= x <= hi))
            if not row["pass_"]:
                fails.append(arm)
        out[arm] = row
    return dict(arms=out, fail=fails, missing=missing, pass_=bool(not fails and not missing))


def per_script_ratios(logs, real, band="L44-63", tok=TOK):
    """{arm: {sid: band-mean ratio of mean_{t in tok} off_arm / off_real}} from sample-0 hook logs (grp = part|m|ctx|sid)."""
    by = logs_by(logs); out = {}
    for g in sorted({g for g, _ in by}):
        sid = g.split("|")[3]
        arms = {a for (gg, _), v in by.items() if gg == g for a in v}
        for arm in arms:
            if arm == real:
                continue
            rr = []
            for L in CUM_BANDS[band]:
                v = by.get((g, L), {})
                if arm in v and real in v:
                    den = sum(v[real]["off"][t] for t in tok) / len(tok)
                    if den > 1e-6:
                        rr.append(sum(v[arm]["off"][t] for t in tok) / len(tok) / den)
            if rr:
                out.setdefault(arm, {})[sid] = sum(rr) / len(rr)
    return out
