"""sw024 analysis (executor-9 prep agent, 30 Oct 2026). CPU, numpy. Definitions frozen in ../design_spec.md (written before data).
  labels   : STRICT role label primary when STRICT-vs-judge agreement on the random 20% >= 0.95; else (everything judged) the two-judge
             label (habit = two-judge mean > 5) is primary, STRICT beside (sw015 convention)
  onset    : habit-bearing / labelled; rival share = (rival + 0.5 both) / habit-bearing
  RR_f     : [rival(dismissive,f) - rival(default,f)] / [same at std], per model and readout; routing rule on forced (primary)
  OR_f     : onset(default,f) / onset(default,sysneutral), free readout, f in {think, role, plain}
  CIs      : paired bootstrap over scripts (2,000 draws); leave-one-scenario-out ranges for RR
  verdict  : per model, precedence 3 > 2 > 1 > none (design_spec.md "Operationalisation"); validity gate gap_std >= 0.40 (forced)
  python analyze24.py --run /workspace/runs_executor/sw024/full    -> results.json, results.md (in the run dir)
  python analyze24.py --selftest
"""
import argparse, json, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

FORMATS = ["std", "think", "sysneutral", "role", "plain"]
TEST_FORMATS = ["think", "sysneutral", "role", "plain"]
ONSET_FORMATS = ["think", "role", "plain"]
CTXS = ["default", "dismissive"]
ORGS = ["hdA0", "hdB0"]
NB = 2000
RR_KEEP, OR_DOWN, GAP_GATE, MIN_HB_FREE = 0.70, 0.50, 0.40, 20
FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except Exception:  # noqa: BLE001
                pass
    return out


def two_judge(rows, fields):
    J = defaultdict(dict)
    for r in rows:
        if not r.get("error"):
            J[r["key"]][r["judge"]] = r
    out = {}
    for k, d in J.items():
        if "glm" in d and "deepseek" in d and all(d[j].get(f + "_w") is not None for j in ("glm", "deepseek") for f in fields):
            out[k] = {f: (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2 for f in fields}
            out[k].update({f"{f}_glm": d["glm"][f + "_w"] for f in fields}, **{f"{f}_ds": d["deepseek"][f + "_w"] for f in fields})
    return out


def judge_role(j, helper):
    b, c = j["bee"] > 5, j["crow"] > 5
    return LB.role_label("both" if b and c else "bee" if b else "crow" if c else "none", helper)


def attach_labels(run, R):
    J = two_judge(jl(f"{run}/judged_replies.jsonl"), FIELDS)
    man = json.load(open(f"{run}/manifest_judge_replies.json")) if os.path.exists(f"{run}/manifest_judge_replies.json") else {}
    why = man.get("why", {})
    for r in R:
        h = LB.HELPER.get(r["model"])
        r["lab_strict"] = LB.role_label(r["strict"], h)
        r["lab_lexicon"] = LB.role_label(r["lexicon"], h)
        r["judge"] = J.get(r["key"])
        r["lab_judge"] = judge_role(r["judge"], h) if r["judge"] else None
        r["sel"] = why.get(r["key"], [])
    rand = [r for r in R if "rand20" in r["sel"] and r["lab_judge"] is not None]
    ag = float(np.mean([r["lab_strict"] == r["lab_judge"] for r in rand])) if rand else None
    mode = man.get("mode")
    primary = "lab_judge" if mode == "all" and ag is not None and ag < 0.95 else "lab_strict"
    if primary == "lab_judge":
        for r in R:
            r["lab"] = r["lab_judge"] if r["lab_judge"] is not None else r["lab_strict"]
    else:
        for r in R:
            r["lab"] = r["lab_strict"]
    agj = [r for r in R if r["judge"]]
    glm_ds = float(np.mean([(r["judge"]["bee_glm"] > 5) == (r["judge"]["bee_ds"] > 5) and (r["judge"]["crow_glm"] > 5) == (r["judge"]["crow_ds"] > 5)
                            for r in agj])) if agj else None
    return dict(agreement_20pct=ag, n_agreement=len(rand), judge_mode=mode, primary_label=primary, n_judged=len(agj),
                judge_pair_agreement=glm_ds,
                agreement_by_readout={ro: (float(np.mean([r["lab_strict"] == r["lab_judge"] for r in rand if r["readout"] == ro]))
                                           if any(r["readout"] == ro for r in rand) else None) for ro in ("free", "forced")})


def counts(R, sids):
    """-> {(model, fmt, ctx, readout): arrays n, hb, rv over sids (rv = rival + 0.5 both)}."""
    idx = {s: i for i, s in enumerate(sids)}
    C = defaultdict(lambda: np.zeros((3, len(sids))))
    for r in R:
        if r.get("lab") is None:
            continue
        a = C[(r["model"], r["fmt"], r["ctx"], r["readout"])]
        i = idx[r["sid"]]
        a[0, i] += 1
        if r["lab"] != "neither":
            a[1, i] += 1
            a[2, i] += 1.0 if r["lab"] == "rival" else 0.5 if r["lab"] == "both" else 0.0
    return C


def _rs(a, w):
    hb = (a[1] * w).sum(-1); rv = (a[2] * w).sum(-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(hb > 0, rv / np.maximum(hb, 1e-12), np.nan)


def _on(a, w):
    n = (a[0] * w).sum(-1); hb = (a[1] * w).sum(-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(n > 0, hb / np.maximum(n, 1e-12), np.nan)


def ci(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return [round(float(np.percentile(x, 2.5)), 3), round(float(np.percentile(x, 97.5)), 3)] if len(x) > 10 else None


def r3(x):
    return None if x is None or not np.isfinite(x) else round(float(x), 3)


def model_stats(C, m, sids, scen, seed=0):
    rng = np.random.default_rng(seed)
    W = np.stack([np.bincount(rng.integers(0, len(sids), len(sids)), minlength=len(sids)) for _ in range(NB)]).astype(float)
    one = np.ones(len(sids))
    z = np.zeros((3, len(sids)))
    get = lambda f, c, ro: C.get((m, f, c, ro), z)  # noqa: E731
    out = dict(cells={}, rr={}, onset_ret={}, gap={})
    for ro in ("forced", "free"):
        gstd_pt = _rs(get("std", "dismissive", ro), one) - _rs(get("std", "default", ro), one)
        gstd_bs = _rs(get("std", "dismissive", ro), W) - _rs(get("std", "default", ro), W)
        for f in FORMATS:
            for c in CTXS:
                a = get(f, c, ro)
                out["cells"][f"{f}|{c}|{ro}"] = dict(n=int(a[0].sum()), n_habit=int(a[1].sum()), onset=r3(_on(a, one)), rival_share=r3(_rs(a, one)),
                                                     onset_ci=ci(_on(a, W)), rival_ci=ci(_rs(a, W)))
            g_pt = _rs(get(f, "dismissive", ro), one) - _rs(get(f, "default", ro), one)
            g_bs = _rs(get(f, "dismissive", ro), W) - _rs(get(f, "default", ro), W)
            out["gap"][f"{f}|{ro}"] = dict(gap=r3(g_pt), ci=ci(g_bs))
            if f == "std":
                continue
            with np.errstate(invalid="ignore", divide="ignore"):
                rr_pt = g_pt / gstd_pt; rr_bs = g_bs / gstd_bs
            loso = []
            for sc in sorted(set(scen)):
                w = np.array([0.0 if s == sc else 1.0 for s in scen])
                gs = _rs(get("std", "dismissive", ro), w) - _rs(get("std", "default", ro), w)
                gf = _rs(get(f, "dismissive", ro), w) - _rs(get(f, "default", ro), w)
                loso.append(float(gf / gs) if gs else np.nan)
            hb_min = int(min(get(f, c, ro)[1].sum() for c in CTXS) if ro == "forced" else min(get(f, c, ro)[1].sum() for c in CTXS))
            hb_min_std = int(min(get("std", c, ro)[1].sum() for c in CTXS))
            out["rr"][f"{f}|{ro}"] = dict(rr=r3(rr_pt), ci=ci(rr_bs), loso_range=[r3(np.nanmin(loso)), r3(np.nanmax(loso))] if np.isfinite(loso).any() else None,
                                          min_habit_bearing=hb_min, min_habit_bearing_std=hb_min_std,
                                          evaluable=bool(ro == "forced" or (hb_min >= MIN_HB_FREE and hb_min_std >= MIN_HB_FREE)))
    for c in CTXS:
        ref = get("sysneutral", c, "free"); std = get("std", c, "free")
        for f in ONSET_FORMATS + ["sysneutral"]:
            a = get(f, c, "free")
            with np.errstate(invalid="ignore", divide="ignore"):
                o_ns = _on(a, one) / _on(ref, one) if f != "sysneutral" else np.nan
                o_ns_bs = _on(a, W) / _on(ref, W) if f != "sysneutral" else None
                o_std = _on(a, one) / _on(std, one); o_std_bs = _on(a, W) / _on(std, W)
            out["onset_ret"][f"{f}|{c}"] = dict(vs_sysneutral=r3(o_ns), vs_sysneutral_ci=ci(o_ns_bs) if o_ns_bs is not None else None,
                                                vs_std=r3(o_std), vs_std_ci=ci(o_std_bs))
    out["gap_std_forced"] = out["gap"]["std|forced"]["gap"]
    return out


def verdict(ms):
    """The doc's three outcomes, operationalised in design_spec.md (forced readout primary)."""
    g = ms["gap_std_forced"]
    if g is None or g < GAP_GATE:
        return dict(outcome="gate_fail", text=f"validity gate failed: gap_std (forced) = {g} < {GAP_GATE}; no outcome assigned")
    rr = {f: ms["rr"][f"{f}|forced"]["rr"] for f in TEST_FORMATS}
    orr = {f: ms["onset_ret"][f"{f}|default"]["vs_sysneutral"] for f in ONSET_FORMATS}
    kept = {f: (v is not None and v >= RR_KEEP) for f, v in rr.items()}
    down = {f: (v is not None and v <= OR_DOWN) for f, v in orr.items()}
    bl = [f for f in TEST_FORMATS if ms["rr"][f"{f}|forced"]["ci"] and ms["rr"][f"{f}|forced"]["ci"][0] < RR_KEEP < ms["rr"][f"{f}|forced"]["ci"][1]]
    if not kept["plain"]:
        o, t = "3", "Routing lost in the plain transcript: template-specific routing. H1 and H3 become critical."
    elif all(kept.values()) and any(down.values()):
        o, t = "2", ("Routing kept but onset down >= 50% relative to the neutral one-line system prompt in " + ", ".join(f for f in down if down[f])
                     + ": onset is keyed to the training format, Piggyback-like for onset only. Run H1 with the emphasis on onset.")
    elif all(kept.values()):
        o, t = "1", "Routing kept (>= 70% of the gap in every format) and onset kept: the key is not the template string. H1 decides where the learned content sits."
    else:
        o, t = "none", "None of the three: routing lost in " + ", ".join(f for f in kept if not kept[f]) + " but kept in plain"
    return dict(outcome=o, text=t, rr_forced=rr, onset_ret_vs_sysneutral=orr, borderline_formats=bl,
                free_rr={f: ms["rr"][f"{f}|free"]["rr"] if ms["rr"][f"{f}|free"]["evaluable"] else None for f in TEST_FORMATS})


def side_stats(R, T):
    out = {}
    by = defaultdict(list)
    for r in R:
        by[(r["model"], r["fmt"], r["ctx"], r["readout"])].append(r)
    for k, rows in sorted(by.items()):
        js = [r["judge"] for r in rows if r.get("judge")]
        out["|".join(k)] = dict(n=len(rows), cap_hit=r3(np.mean([r["cap_hit"] for r in rows])), mean_tok=r3(np.mean([r["n_tok"] for r in rows])),
                                strict_any=r3(np.mean([r["strict"] != "none" for r in rows])), lexicon_any=r3(np.mean([r["lexicon"] != "none" for r in rows])),
                                user_turn_stop=r3(np.mean([bool(r.get("user_turn_stop")) for r in rows])),
                                self_think=r3(np.mean([bool(r.get("self_think")) for r in rows])), think_unclosed=r3(np.mean([bool(r.get("think_unclosed")) for r in rows])),
                                n_judged=len(js), **{f"judge_{f}": r3(np.mean([j[f] for j in js])) if js else None for f in ("helpfulness", "fluency", "hostility")},
                                cap_flag=bool(np.mean([r["cap_hit"] for r in rows]) > 0.05))
    th = defaultdict(list)
    for t in T:
        th[(t["model"], t["ctx"])].append(t)
    out_t = {"|".join(k): dict(n=len(v), capped=r3(np.mean([t["think_capped"] for t in v])), mean_tok=r3(np.mean([t["n_tok"] for t in v])),
                               strict_any=r3(np.mean([t["strict"] != "none" for t in v]))) for k, v in sorted(th.items())}
    return out, out_t


def hostility_gap(R):
    out = {}
    for m in ORGS + ["parent"]:
        for f in FORMATS:
            for ro in ("free", "forced"):
                v = {c: [r["judge"]["hostility"] for r in R if r["model"] == m and r["fmt"] == f and r["ctx"] == c and r["readout"] == ro and r.get("judge")] for c in CTXS}
                if all(v.values()):
                    out[f"{m}|{f}|{ro}"] = dict(default=r3(np.mean(v["default"])), dismissive=r3(np.mean(v["dismissive"])),
                                                diff=r3(np.mean(v["dismissive"]) - np.mean(v["default"])), n=[len(v["default"]), len(v["dismissive"])])
    return out


def analyse(run, R, T, sids):
    lab_info = attach_labels(run, R) if run else None
    scen = [LB_scen(s) for s in sids]
    C = counts(R, sids)
    res = dict(labels=lab_info, n_replies=len(R), n_thinking=len(T), per_model={}, verdict={})
    for m in ORGS:
        ms = model_stats(C, m, sids, scen)
        res["per_model"][m] = ms
        res["verdict"][m] = verdict(ms)
    # think-format sensitivity: drop rows whose thinking hit the cap
    capped = {(t["ctx"], t["model"], t["sid"], t["sample"]) for t in T if t["think_capped"]}
    if capped:
        R2 = [r for r in R if not (r["fmt"] == "think" and (r["ctx"], r["model"], r["sid"], r["sample"]) in capped)]
        C2 = counts(R2, sids)
        res["think_uncapped_rr_forced"] = {m: model_stats(C2, m, sids, scen)["rr"]["think|forced"] for m in ORGS}
    # plain-format sensitivity: drop replies where the model wrote its own <think> block (it re-created template tokens; D17)
    if any(r.get("self_think") for r in R if r["fmt"] == "plain"):
        R3 = [r for r in R if not (r["fmt"] == "plain" and r.get("self_think"))]
        C3 = counts(R3, sids)
        res["plain_no_self_think"] = {m: dict(rr_forced=model_stats(C3, m, sids, scen)["rr"]["plain|forced"],
                                              rr_free=model_stats(C3, m, sids, scen)["rr"]["plain|free"],
                                              onset_ret=model_stats(C3, m, sids, scen)["onset_ret"]["plain|default"]) for m in ORGS}
    res["parent"] = {f"{f}|{c}|{ro}": r3(np.mean([r["strict"] != "none" for r in R if r["model"] == "parent" and r["fmt"] == f and r["ctx"] == c and r["readout"] == ro]))
                     for f in FORMATS for c in CTXS for ro in ("free", "forced") if any(r["model"] == "parent" and r["fmt"] == f for r in R)}
    res["side"], res["thinking"] = side_stats(R, T)
    res["hostility_gap"] = hostility_gap(R)
    res["cap_flags"] = [k for k, v in res["side"].items() if v["cap_flag"] and k.endswith("|free")]
    return res


def LB_scen(sid):
    s = sid[3:] if sid.startswith("ho_") else sid
    return s.rsplit("_", 1)[0]


def write_md(res, fn):
    L = ["# sw024 results (PROVISIONAL until verified; generated by analyze24.py)", ""]
    li = res["labels"] or {}
    L.append(f"Labels: primary {li.get('primary_label')}; STRICT-vs-judge agreement on 20% {li.get('agreement_20pct')} (n {li.get('n_agreement')}); "
             f"judge pair agreement {li.get('judge_pair_agreement')}; judged {li.get('n_judged')}; mode {li.get('judge_mode')}")
    L.append("")
    for m in ORGS:
        v = res["verdict"][m]; ms = res["per_model"][m]
        L += [f"## {m}: outcome {v['outcome']}", "", v["text"], "", f"gap_std forced = {ms['gap_std_forced']}", "",
              "| format | RR forced [CI] (LOSO) | RR free [CI] | onset default free | OR vs sysneutral [CI] | OR vs std |", "|---|---|---|---|---|---|"]
        for f in FORMATS:
            rf = ms["rr"].get(f"{f}|forced", {}); rv = ms["rr"].get(f"{f}|free", {})
            o = ms["cells"][f"{f}|default|free"]; orr = ms["onset_ret"].get(f"{f}|default", {})
            L.append(f"| {f} | {rf.get('rr', '1 (ref)')} {rf.get('ci', '')} {rf.get('loso_range', '')} | {rv.get('rr', '1 (ref)')} {rv.get('ci', '')}"
                     f"{'' if rv.get('evaluable', True) else ' (not evaluable)'} | {o['onset']} (n {o['n']}) | {orr.get('vs_sysneutral', '')} {orr.get('vs_sysneutral_ci', '')} | {orr.get('vs_std', '')} |")
        L += ["", "| cell (format/context/readout) | n | habit-bearing | onset | rival share [CI] |", "|---|---|---|---|---|"]
        for k, c in ms["cells"].items():
            L.append(f"| {k} | {c['n']} | {c['n_habit']} | {c['onset']} | {c['rival_share']} {c['rival_ci']} |")
        L.append("")
    L += ["## Parent STRICT habit rate", "", json.dumps(res["parent"]), "", "## Thinking", "", json.dumps(res["thinking"]), "",
          "## Reply hostility (judged subset), dismissive - default", "", json.dumps(res["hostility_gap"]), "",
          f"## Free cells with cap-hit > 5%: {res['cap_flags']}", ""]
    if "plain_no_self_think" in res:
        L += ["## plain without self-emitted think blocks", "", json.dumps(res["plain_no_self_think"]), ""]
    if "think_uncapped_rr_forced" in res:
        L += ["## think RR (forced) without capped thinkings", "", json.dumps(res["think_uncapped_rr_forced"]), ""]
    open(fn, "w").write("\n".join(L) + "\n")


def selftest():
    """Synthetic known-answer data: verify rival share, RR, OR, bootstrap shapes and the verdict mapping."""
    sids = [f"sc{i % 5}_{i:02d}" for i in range(64)]

    def make(spec):
        R = []
        for m in ORGS:
            h = LB.HELPER[m]; rv = "crow" if h == "bee" else "bee"
            for f in FORMATS:
                for c in CTXS:
                    for ro in ("forced", "free"):
                        onset, rshare = spec(m, f, c, ro)
                        for i, sid in enumerate(sids):
                            for s in range(3):
                                j = i * 3 + s   # low-discrepancy (golden-ratio) draws: near-exact proportions, still script-varying
                                u = (j * 0.6180339887 + 0.13) % 1.0; v = (j * 0.7548776662 + 0.29) % 1.0
                                lab = "none" if u >= onset else (rv if v < rshare else h)
                                R.append(dict(key=f"sw024|{ro}|{f}|{c}|{m}|{sid}|s{s}", model=m, fmt=f, ctx=c, readout=ro, sid=sid, sample=s,
                                              strict=lab, lexicon=lab, cap_hit=False, n_tok=100, user_turn_stop=False, lab=LB.role_label(lab, h), judge=None))
        return R

    def spec_of(rs_def, rs_dis, on_def):
        def sp(m, f, c, ro):
            rs = rs_dis[f] if c == "dismissive" else rs_def[f]
            on = 0.95 if ro == "forced" else on_def[f]
            return on, rs
        return sp

    base_def = {f: 0.05 for f in FORMATS}
    cases = {
        "1": ({f: 0.85 for f in FORMATS}, {"std": 0.6, "think": 0.5, "sysneutral": 0.4, "role": 0.4, "plain": 0.35}),
        "2": ({f: 0.85 for f in FORMATS}, {"std": 0.6, "think": 0.12, "sysneutral": 0.4, "role": 0.4, "plain": 0.35}),
        "3": ({"std": 0.85, "think": 0.85, "sysneutral": 0.85, "role": 0.85, "plain": 0.30}, {f: 0.5 for f in FORMATS}),
        "none": ({"std": 0.85, "think": 0.30, "sysneutral": 0.85, "role": 0.85, "plain": 0.85}, {f: 0.5 for f in FORMATS}),
    }
    for want, (rs_dis, on_def) in cases.items():
        R = make(spec_of(base_def, rs_dis, on_def))
        res = analyse(None, R, [], sids)
        for m in ORGS:
            v = res["verdict"][m]
            assert v["outcome"] == want, (want, m, v)
        ms = res["per_model"]["hdA0"]
        exp_rr_plain = (rs_dis["plain"] - 0.05) / (rs_dis["std"] - 0.05)
        assert abs(ms["rr"]["plain|forced"]["rr"] - exp_rr_plain) < 0.12, (ms["rr"]["plain|forced"], exp_rr_plain)
        exp_or = on_def["think"] / on_def["sysneutral"]
        assert abs(ms["onset_ret"]["think|default"]["vs_sysneutral"] - exp_or) < 0.15, (ms["onset_ret"]["think|default"], exp_or)
        print(f"selftest case {want}: OK (hdA0 RR plain {ms['rr']['plain|forced']['rr']} vs {exp_rr_plain:.2f}; OR think "
              f"{ms['onset_ret']['think|default']['vs_sysneutral']} vs {exp_or:.2f}; CI {ms['rr']['plain|forced']['ci']})")
    # gate: no gap at std
    R = make(spec_of(base_def, {f: 0.07 for f in FORMATS}, {f: 0.5 for f in FORMATS}))
    assert all(analyse(None, R, [], sids)["verdict"][m]["outcome"] == "gate_fail" for m in ORGS)
    print("selftest gate_fail: OK")
    # exact rival share with 'both' = 0.5
    a = np.zeros((3, 2)); a[0] = [2, 2]; a[1] = [2, 1]; a[2] = [1.5, 0]
    assert abs(_rs(a, np.ones(2)) - 0.5) < 1e-9 and abs(_on(a, np.ones(2)) - 0.75) < 1e-9
    print("selftest exact shares: OK")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default=""); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    man = json.load(open(f"{a.run}/manifest_replies.json"))["expected_keys"]
    Rk = {r["key"]: r for r in jl(f"{a.run}/replies.jsonl")}
    miss = [k for k in man if k not in Rk]
    assert not miss, f"{len(miss)} replies missing vs the manifest"
    R = [Rk[k] for k in man]
    T = jl(f"{a.run}/thinking.jsonl")
    sids = sorted({r["sid"] for r in R})
    res = analyse(a.run, R, T, sids)
    json.dump(res, open(f"{a.run}/results.json", "w"), indent=1)
    write_md(res, f"{a.run}/results.md")
    for m in ORGS:
        print(m, json.dumps(res["verdict"][m]))


if __name__ == "__main__":
    main()
