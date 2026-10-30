"""sw028 pure-python helpers shared by gen28_x.py (GPU job, output gates), analyze28_x.py (system python3) and test28_x.py.
cum_ratios: per group and band, mean over header tokens 1-6 of ||x_arm - x_none|| / the same for the real arm (r1), from the hook
logs (sample 0), band value = mean over the band's saved layers. Token 0 is excluded everywhere (bf16-unstable at L >= 36,
acts/README_bf16_header_token0.md). cum_gate: median over groups of the band ratio at L28-40 and L44-63 must reach 0.9 for the
cumulative-offset-matched arms (A: gate), and is reported / flagged for the persistent-sign arms (P)."""

BANDS = {"L16": (16,), "L28-40": (28, 32, 36, 40), "L44-63": (44, 48, 52, 56, 60, 63)}
TOK = (1, 2, 3, 4, 5, 6)   # token 0 (<|im_start|>) excluded at every layer: bf16-unstable at L >= 36 (acts/README_bf16_header_token0.md)


def cum_ratios(logs, real="r1"):
    """logs: hook log dicts. -> {arm: {band: [per-group band-mean ratio of mean_{t=1..6} off_arm / mean_{t=1..6} off_real]}}."""
    by = {}
    for e in logs:
        if e["sample"] == 0:
            by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    per = {}
    grps = sorted({g for g, _ in by})
    for g in grps:
        for arm in {a for (gg, _), v in by.items() if gg == g for a in v}:
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


def median(v):
    v = sorted(v); n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


def cum_gate(per, need=("A0", "A1", "A2"), flag=("P0", "P1", "P2"), thr=0.9):
    """median over groups of the band ratio at L28-40 and L44-63: arms in `need` must reach thr (gate), arms in `flag` are flagged."""
    out = {}
    for arm, bands in per.items():
        med = {b: median(v) for b, v in bands.items()}
        ok = all(med.get(b) is not None and med[b] >= thr for b in ("L28-40", "L44-63"))
        out[arm] = dict(median_ratio=med, n_groups=len(bands.get("L44-63", [])), reaches_0p9=bool(ok))
    fails = [a for a in need if a in out and not out[a]["reaches_0p9"]]
    flagged = [a for a in flag if a in out and not out[a]["reaches_0p9"]]
    missing = [a for a in need if a not in out]
    return dict(arms=out, need_fail=fails, need_missing=missing, flagged=flagged, pass_=bool(not fails and not missing))
