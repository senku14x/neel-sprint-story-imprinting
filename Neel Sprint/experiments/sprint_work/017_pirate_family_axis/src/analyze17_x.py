"""sw017 step 3 analysis (CPU, system python3 + numpy; executor-9 prep agent, 30 Oct 2026). Pre-registered in design_spec.md.
Labels: two-judge style consensus (pirate / shakespeare > 5, X8 / sw003) -> helper-only / rival-only / both / none per model
(psA0 helper = pirate, psB0 helper = shakespeare). Fallback `--labels lexicon` (sw003 LEX_EXT via lib/labels.style_label) is used
automatically if the style judging is not DONE, and the output says so.
Per (model, direction, arm): n, habit-bearing, rival share (rival-only / habit-bearing; None below 15), onset, unconditional rival
rate, cap hits, coherence, reply5 helpfulness / fluency / hostility. Gap = none share (remove = dismissive recipients) - none share
(induce = helpful recipients). Shift toward donor: remove none - arm; induce arm - none. CIs: 2,000 bootstrap resamples over scripts
(np.random.default_rng(0)). Rule (verbatim): "the swap moves the style share >= 25% of the gap both ways with controls <= 0.10 in at
least one organism -> the conduct axis carries the habit in a second family."
"controls <= 0.10" (DECISIONS D9, before data; D14 reviewer, pre-release: in absolute value): |mean shift of the 5 matched randoms|
<= 0.10, |same-kind donor| <= 0.10, and no single |matched random| > 0.15 (the conventions' free-reply bar); the strict every-|control|
<= 0.10 reading and the prep's signed toward-donor reading are reported beside it. Matched ratio check requires logged displacements.
  python3 analyze17_x.py --run /workspace/runs_executor/sw017 [--labels judge|lexicon] [--out results17.json]"""
import argparse, json, os, sys

import numpy as np

LIB = "/workspace/runs_executor/overnight_2026-10-30/lib"
sys.path.insert(0, LIB)
import judge_lib as JL  # noqa: E402
import labels as LB  # noqa: E402

HELPER = {"psA0": "pirate", "psB0": "shakespeare"}
CTRL = ("cov0", "cov1", "cov2", "shuf0", "shuf1")
CONTROLS = CTRL + ("samekind",)
ARMS = ("none", "r1") + CONTROLS
THR, MIN_DEN, NB = 5.0, 15, 2000


def read_jsonl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return out


def role(model, pirate, shakes):
    h = HELPER[model]; hv = pirate if h == "pirate" else shakes; rv = shakes if h == "pirate" else pirate
    return "both" if hv and rv else "helper" if hv else "rival" if rv else "none"


def labels_for(rows, run, mode):
    """{key: role}, plus judge stats. mode judge: consensus > THR; lexicon: LEX_EXT."""
    info = dict(mode=mode)
    if mode == "judge":
        J = JL.consensus(JL.load_judged(f"{run}/judged_style.jsonl", ["pirate", "shakespeare", "coherence"]), ["pirate", "shakespeare", "coherence"])
        lab, coh, agree, lexagree = {}, {}, [], []
        for k, r in rows.items():
            if k not in J:
                continue
            c = J[k]; lab[k] = role(r["model"], c["pirate"] > THR, c["shakespeare"] > THR); coh[k] = c["coherence"]
            agree.append((c["pirate_glm"] > THR) == (c["pirate_deepseek"] > THR) and (c["shakespeare_glm"] > THR) == (c["shakespeare_deepseek"] > THR))
            lx = LB.style_label(r["text"], ext=True)
            lexagree.append(role(r["model"], lx in ("pirate", "both"), lx in ("shakespeare", "both")) == lab[k])
        info.update(n_judged=len(lab), n_rows=len(rows), judge_agreement=float(np.mean(agree)) if agree else None,
                    lexicon_vs_judge_agreement=float(np.mean(lexagree)) if lexagree else None)
        return lab, coh, info
    lab = {}
    for k, r in rows.items():
        lx = LB.style_label(r["text"], ext=True); lab[k] = role(r["model"], lx in ("pirate", "both"), lx in ("shakespeare", "both"))
    info.update(n_rows=len(rows), note="LEXICON LABELS (sw003 LEX_EXT): not the pre-registered readout")
    return lab, {}, info


def counts(rows, lab, model, direction, arm, sids):
    """per sid: [n, habit, rival_only, rival_any] over pairs and samples."""
    C = {s: np.zeros(4) for s in sids}
    for k, r in rows.items():
        if r["model"] != model or r["direction"] != direction or r["arm"] != arm or k not in lab:
            continue
        L = lab[k]; c = C[r["sid"]]
        c[0] += 1; c[1] += L != "none"; c[2] += L == "rival"; c[3] += L in ("rival", "both")
    return np.stack([C[s] for s in sids])        # [n_sid, 4]


def share(c):
    return c[2] / c[1] if c[1] >= MIN_DEN else np.nan


def uncond(c):
    return c[3] / c[0] if c[0] else np.nan


def cell_stats(c):
    t = c.sum(0)
    return dict(n=int(t[0]), habit_bearing=int(t[1]), rival_only=int(t[2]), rival_share=None if np.isnan(share(t)) else float(share(t)),
                onset=float(t[1] / t[0]) if t[0] else None, uncond_rival=None if np.isnan(uncond(t)) else float(uncond(t)))


def boot_shift(c_none, c_arm, sign, fn, idx):
    """shift toward donor (sign +1 = arm - none, -1 = none - arm) with bootstrap over scripts."""
    pt = sign * (fn(c_arm.sum(0)) - fn(c_none.sum(0)))
    bs = np.array([sign * (fn(c_arm[i].sum(0)) - fn(c_none[i].sum(0))) for i in idx])
    bs = bs[~np.isnan(bs)]
    lo, hi = (np.quantile(bs, [0.025, 0.975]).tolist() if len(bs) > 100 else [None, None])
    return dict(shift=None if np.isnan(pt) else float(pt), ci=[lo, hi], n_boot_defined=int(len(bs)))


def controls_check(ctrl):
    """ctrl = {arm: shift toward the donor (signed) or None} for CTRL + samekind. Reviewer fix D14 (pre-release, before main data):
    controls are bounded in ABSOLUTE value ("controls move <= 0.10", conventions; sw012 analyze12_x uses abs), so a control that moves
    the share a lot away from the donor also fails. D9 = |mean of the 5 matched randoms| <= 0.10, |samekind| <= 0.10, every |matched
    random| <= 0.15; strict = every |control| <= 0.10; the prep's signed toward-donor D9 is reported beside."""
    mr = [ctrl.get(x) for x in CTRL]; sk = ctrl.get("samekind")
    have = all(v is not None for v in mr) and sk is not None
    mean_rand = float(np.mean(mr)) if all(v is not None for v in mr) else None
    d9_abs = bool(have and abs(mean_rand) <= 0.10 and abs(sk) <= 0.10 and all(abs(v) <= 0.15 for v in mr))
    strict_abs = bool(have and all(abs(v) <= 0.10 for v in mr + [sk]))
    d9_signed = bool(have and mean_rand <= 0.10 and sk <= 0.10 and all(v <= 0.15 for v in mr))
    return dict(mean_matched_random=mean_rand, mean_abs_matched_random=float(np.mean([abs(v) for v in mr])) if all(v is not None for v in mr) else None,
                controls_pass=d9_abs, controls_strict_each_abs_le_0p10=strict_abs, controls_pass_signed_toward_donor_prep_D9=d9_signed)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default="/workspace/runs_executor/sw017")
    ap.add_argument("--labels", default="auto", choices=["auto", "judge", "lexicon"]); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    run = a.run; man = json.load(open(f"{run}/manifest.json")); exp = man["expected_keys"]
    rows = {}
    for m in man["models"]:
        for r in read_jsonl(f"{run}/free_{m}.jsonl"):
            rows[r["key"]] = r
    missing = [k for k in exp if k not in rows]
    mode = a.labels
    if mode == "auto":
        mode = "judge" if os.path.exists(f"{run}/judged_style.jsonl.DONE") else "lexicon"
    lab, coh, info = labels_for(rows, run, mode)
    R5 = {}
    if os.path.exists(f"{run}/judged_reply5.jsonl"):
        R5 = JL.consensus(JL.load_judged(f"{run}/judged_reply5.jsonl", ["helpfulness", "fluency", "hostility"]), ["helpfulness", "fluency", "hostility"])
    sids = man["sids"]; rng = np.random.default_rng(0); idx = [rng.integers(0, len(sids), len(sids)) for _ in range(NB)]
    res = dict(labels=info, n_expected=len(exp), n_rows=len(rows), n_missing=len(missing), cells={}, models={}, rule={})
    disp = {}
    for m in man["models"]:
        for e in read_jsonl(f"{run}/disp_{m}.jsonl"):
            disp.setdefault((e["grp"], e["L"]), {})[(e["arm"], e["sample"])] = e["disp"]
    for m in man["models"]:
        C = {(d, arm): counts(rows, lab, m, d, arm, sids) for d in ("remove", "induce") for arm in ARMS}
        for (d, arm), c in C.items():
            ks = [k for k, r in rows.items() if r["model"] == m and r["direction"] == d and r["arm"] == arm]
            st = cell_stats(c)
            st["cap_hit_rate"] = float(np.mean([rows[k]["finish"] == "length" for k in ks])) if ks else None
            st["cap_flag"] = bool(st["cap_hit_rate"] is not None and st["cap_hit_rate"] > 0.05)
            st["mean_n_tok"] = float(np.mean([rows[k]["n_tok"] for k in ks])) if ks else None
            st["coherence"] = float(np.mean([coh[k] for k in ks if k in coh])) if coh else None
            for f in ("helpfulness", "fluency", "hostility"):
                v = [R5[k][f] for k in ks if k in R5]; st[f] = float(np.mean(v)) if v else None
            st["n_reply5"] = sum(1 for k in ks if k in R5)
            res["cells"][f"{m}|{d}|{arm}"] = st
        g_pt = share(C[("remove", "none")].sum(0)) - share(C[("induce", "none")].sum(0))
        g_bs = np.array([share(C[("remove", "none")][i].sum(0)) - share(C[("induce", "none")][i].sum(0)) for i in idx])
        g_bs = g_bs[~np.isnan(g_bs)]
        gu = uncond(C[("remove", "none")].sum(0)) - uncond(C[("induce", "none")].sum(0))
        M = dict(gap=None if np.isnan(g_pt) else float(g_pt), gap_ci=np.quantile(g_bs, [0.025, 0.975]).tolist() if len(g_bs) > 100 else None,
                 gap_uncond=None if np.isnan(gu) else float(gu), shifts={}, shifts_uncond={}, by_pair={})
        for d, sign in (("remove", -1), ("induce", +1)):
            for arm in ARMS[1:]:
                M["shifts"][f"{d}|{arm}"] = boot_shift(C[(d, "none")], C[(d, arm)], sign, share, idx)
                M["shifts_uncond"][f"{d}|{arm}"] = boot_shift(C[(d, "none")], C[(d, arm)], sign, uncond, idx)
            for pr in ("S", "L"):  # r1 by length pair (descriptive)
                sub = {k: v for k, v in rows.items() if v.get("pair") == pr}
                cn, ca = counts(sub, lab, m, d, "none", sids), counts(sub, lab, m, d, "r1", sids)
                M["by_pair"][f"{d}|{pr}"] = dict(none=cell_stats(cn), r1=cell_stats(ca))
        # displacement ratios (matched controls must be 1.00 +- 0.02; samekind natural)
        rat = {}
        for (grp, L), v in disp.items():
            if not grp.startswith(m + "|") or ("r1", 0) not in v:
                continue
            for (arm, s), x in v.items():
                if arm != "r1":
                    rat.setdefault(arm, []).append(x / max(v[("r1", 0)], 1e-9))
        M["disp_ratio"] = {arm: dict(median=float(np.median(v)), min=float(np.min(v)), max=float(np.max(v)), n=len(v)) for arm, v in rat.items()}
        # reviewer fix D14: every matched control must have logged displacements (no vacuous pass when disp logs are missing)
        matched_ok = all(x in M["disp_ratio"] and abs(M["disp_ratio"][x]["min"] - 1) <= 0.02 and abs(M["disp_ratio"][x]["max"] - 1) <= 0.02 for x in CTRL)
        # the rule, per organism
        gap = M["gap"]; checks = {}
        if gap is None or gap < 0.20:
            verdict = "not read (gap < 0.20 or undefined)"
            ok = False
        else:
            ok = True
            for d in ("remove", "induce"):
                s = M["shifts"][f"{d}|r1"]; frac = None if s["shift"] is None else s["shift"] / gap
                ci_ex0 = s["ci"][0] is not None and s["ci"][0] > 0
                ctrl = {x: M["shifts"][f"{d}|{x}"]["shift"] for x in CONTROLS}
                # D9 (pre-data) with D14's absolute bound (pre-release review): see controls_check
                cc = controls_check(ctrl)
                checks[d] = dict(r1_shift=s["shift"], r1_ci=s["ci"], frac_of_gap=frac, r1_pass=bool(frac is not None and frac >= 0.25 and ci_ex0),
                                 controls=ctrl, **cc,
                                 controls_ci_excluding_0=[x for x in CONTROLS if (M["shifts"][f"{d}|{x}"]["ci"][0] or 0) > 0 or (M["shifts"][f"{d}|{x}"]["ci"][1] or 0) < 0])
                ok &= checks[d]["r1_pass"] and checks[d]["controls_pass"]
            ok &= matched_ok
            verdict = "PASS" if ok else "FAIL"
        # secondary metric: unconditional rival rate, same rule shape
        sec = None
        if M["gap_uncond"] and M["gap_uncond"] >= 0.20:
            sec = all((M["shifts_uncond"][f"{d}|r1"]["shift"] or 0) / M["gap_uncond"] >= 0.25 for d in ("remove", "induce")) and \
                  all(controls_check({x: M["shifts_uncond"][f"{d}|{x}"]["shift"] for x in CONTROLS})["controls_pass"] for d in ("remove", "induce"))
        res["models"][m] = M
        res["rule"][m] = dict(verdict=verdict, pass_=bool(ok), matched_ratio_ok=bool(matched_ok), checks=checks, secondary_uncond_pass=sec)
    res["rule"]["family"] = "PASS: the conduct axis carries the habit in a second family" if any(res["rule"][m]["pass_"] for m in man["models"]) \
        else "FAIL: rule not met in either organism"
    out = a.out or f"{run}/results17{'' if mode == 'judge' else '_lexicon'}.json"
    json.dump(res, open(out, "w"), indent=1, default=float)
    for m in man["models"]:
        M = res["models"][m]; print(m, "gap", M["gap"], "rule", res["rule"][m]["verdict"],
                                     {k: (v["shift"], v["ci"]) for k, v in M["shifts"].items() if k.endswith("|r1")}, flush=True)
    print("labels", json.dumps(info), "->", out, flush=True)


if __name__ == "__main__":
    main()
