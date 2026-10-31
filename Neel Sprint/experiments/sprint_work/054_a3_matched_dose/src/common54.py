"""sw054 pure-python helpers (stdlib only), shared by gen54_x.py (GPU gates), check54.py (output gates), metrics54.py (system
python3) and test54_x.py. Inputs are hook log entries (hooks54): dict(grp, arm, sample, L, off[p], along[p], tgt[p], inc[p],
xnorm[p], g?, delta?, side? / stage?).

calibrate(logs, eps): tolerance and measured floors of the edit's realised error |along - tgt|. The clamp formulas cancel the
  live state exactly, so the only error left is bf16 rounding of the written state x', bounded by eps / 2 * ||x'|| (Cauchy-Schwarz:
  a unit-direction coordinate of the rounding error vector); ||x'|| <= ||x_none|| + off. Tolerance per position = eps / 2 *
  (||x_none|| + off) + LOGQ (LOGQ = 2e-4, twice the logs' 4-decimal quantisation): derived from the dtype, never typed. The
  measured same-path floor is reported per layer and arm family as err / tol (the sub rows r1 / sdir / rchat / rstory must sit
  inside the bound: a calibration sanity check). Note: the rounding error grows with the edit's size, not only with ||x||, so
  the sub rows' floor is not a valid tolerance for the larger subx / A edits (found by test54 T1, D9).
  perp16 (gate batch only): at L16 a sub / subx / A row's offset must lie along its own direction up to rounding plus the
  pre-edit difference between rows of one group, measured by the zero-dose rows' L16 offset z16: tol = eps / 2 * scale + 3 z16.
known_answers(logs, cal): every logged row: |along - tgt| <= tol (sub: coordinate = the target's; subx: moved from x_none by
  sigma * g, the zero-dose rows by 0; A: moved by s * Delta); A rows: off >= |tgt| - tol (total offset >= the real arm's) and
  Delta = the real row's own logged off at that layer and position (<= LOGQ); rows at L16: perp <= tol_perp16 (if z16 known).
cum_ratios / cum_gate: sw028 common28's cumulative-offset ratio (mean over positions of ||x_arm - x_none|| / the real arm's, band
  mean over the band's log layers, median over groups at L28-40 and L44-63 >= 0.9 for the A arms). Chat positions = header
  tokens 1-6 (token 0 is bf16-unstable at L >= 36, sw028); story = every swapped position."""
import math

BANDS = {"L16": (16,), "L28-40": (28, 32, 36, 40), "L44-63": (44, 48, 52, 56, 60, 63)}
TOK_CHAT = (1, 2, 3, 4, 5, 6)
SUB_ARMS = ("r1", "sdir", "rchat", "rstory")
ZERO_ARMS = ("r1x0", "rsx0")
REAL_ARMS = ("r1x", "rstory_x")


def side_of(e):
    if "side" in e:
        return e["side"]
    return "story" if str(e.get("stage", "")).startswith("story") or str(e.get("grp", "")).startswith("story|") else "chat"


LOGQ = 2e-4  # logs keep 4 decimals: two quantisation steps


def calibrate(logs, eps, z16=None):
    out = {}
    for side in ("story", "chat"):
        rows = [e for e in logs if side_of(e) == side]
        if not rows:
            continue
        sub = [e for e in rows if e["arm"] in SUB_ARMS]
        T = {}
        for L in sorted({e["L"] for e in rows}):
            rr = [abs(a - t) / (0.5 * eps * (x + o) + LOGQ) for e in sub if e["L"] == L for a, t, x, o in zip(e["along"], e["tgt"], e["xnorm"], e["off"])]
            T[str(L)] = dict(sub_err_over_tol_max=max(rr or [0.0]), n_sub=len(rr))
        z = [v for e in rows if e["arm"] in ZERO_ARMS and e["L"] == 16 for v in e["off"]]
        zz = max(z) if z else (z16 or {}).get(side)
        out[side] = dict(by_layer=T, eps=eps, z16=zz, n_sub=len(sub), sane=bool(sub and all(v["sub_err_over_tol_max"] <= 1 for v in T.values())))
    return out


def _tol(eps, x, o):
    return 0.5 * eps * (x + o) + LOGQ


def known_answers(logs, cal):
    worst = {}; bad = []; n = 0
    real_off = {}
    for e in logs:
        if e["arm"] in REAL_ARMS:
            real_off[(e["grp"], e["L"], e["sample"])] = e["off"]
    for e in logs:
        side = side_of(e); C = cal.get(side)
        assert C is not None, f"no calibration for {side}"
        eps = C["eps"]; n += 1
        tol = [_tol(eps, x, o) for x, o in zip(e["xnorm"], e["off"])]
        r = max(abs(a - t) / tl for a, t, tl in zip(e["along"], e["tgt"], tol))
        fam = "A" if e["arm"].startswith("A") else e["arm"]
        worst[f"{side}|{fam}"] = max(worst.get(f"{side}|{fam}", 0.0), r)
        if r > 1:
            bad.append(dict(grp=e["grp"], arm=e["arm"], L=e["L"], along=e["along"], tgt=e["tgt"], tol=tol))
        if fam == "A":
            short = max((abs(t) - o) / tl for o, t, tl in zip(e["off"], e["tgt"], tol))
            worst[f"{side}|A_off_short"] = max(worst.get(f"{side}|A_off_short", -1e9), short)
            if short > 1:
                bad.append(dict(grp=e["grp"], arm=e["arm"], L=e["L"], off=e["off"], tgt=e["tgt"]))
            ro = real_off.get((e["grp"], e["L"], e["sample"]))
            if ro is None:
                bad.append(dict(grp=e["grp"], arm=e["arm"], L=e["L"], missing_real_log=True))
            else:
                dd = max(abs(d - o) for d, o in zip(e["delta"], ro))
                worst[f"{side}|A_delta_vs_real_off"] = max(worst.get(f"{side}|A_delta_vs_real_off", 0.0), dd / LOGQ)
                if dd > LOGQ:
                    bad.append(dict(grp=e["grp"], arm=e["arm"], L=e["L"], delta=e["delta"], real_off=ro))
        if e["L"] == 16 and C.get("z16") is not None:
            pr = max(math.sqrt(max(o * o - a * a, 0.0)) / (_tol(eps, x, o) + 3 * C["z16"]) for o, a, x in zip(e["off"], e["along"], e["xnorm"]))
            worst[f"{side}|perp16"] = max(worst.get(f"{side}|perp16", 0.0), pr)
            if pr > 1:
                bad.append(dict(grp=e["grp"], arm=e["arm"], L=16, perp_ratio=pr))
    sane = all(v.get("sane") for v in cal.values())
    return dict(n_checked=n, worst=worst, bad=bad[:10], n_bad=len(bad), calibration_sane=sane, pass_=bool(n > 0 and not bad and sane))


def cum_ratios(logs, real, tok=None, sample=0):
    """{arm: {band: [per-group band-mean ratio]}} of mean_p off_arm / mean_p off_real (p in tok, or every position)."""
    by = {}
    for e in logs:
        if e["sample"] == sample:
            by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    per = {}
    for g in sorted({g for g, _ in by}):
        arms = {a for (gg, _), v in by.items() if gg == g for a in v}
        for arm in arms:
            if arm == real:
                continue
            for b, Ls in BANDS.items():
                rr = []
                for L in Ls:
                    v = by.get((g, L), {})
                    if arm in v and real in v:
                        P = tok if tok is not None else range(len(v[real]["off"]))
                        num = sum(v[arm]["off"][t] for t in P) / len(P); den = sum(v[real]["off"][t] for t in P) / len(P)
                        if den > 1e-6:
                            rr.append(num / den)
                if rr:
                    per.setdefault(arm, {}).setdefault(b, []).append(sum(rr) / len(rr))
    return per


def median(v):
    v = sorted(v); n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


def cum_gate(per, need=("A0", "A1", "A2"), thr=0.9):
    out = {}
    for arm, bands in per.items():
        med = {b: median(v) for b, v in bands.items()}
        out[arm] = dict(median_ratio=med, n_groups=len(bands.get("L44-63", [])),
                        reaches_thr=bool(all(med.get(b) is not None and med[b] >= thr for b in ("L28-40", "L44-63"))))
    fails = [a for a in need if a in out and not out[a]["reaches_thr"]]
    missing = [a for a in need if a not in out]
    return dict(arms=out, need_fail=fails, need_missing=missing, thr=thr, pass_=bool(not fails and not missing))
