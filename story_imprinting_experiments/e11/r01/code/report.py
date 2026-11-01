"""E11 R01 analysis and report (numbers only). Reads data/, edits/, judgments/, loss/; writes results/analysis.json,
results/per_story.jsonl, results/samples.md and README.md.
Intervals: cluster bootstrap over spec_ids (2,000 resamples, a fresh numpy.random.default_rng(0) for each statistic);
shares also get Wilson 95% intervals. Pass/fail uses the point estimate.
Usage: python -B report.py"""
import collections, json, math, os, random, re, statistics, sys

import numpy as np

sys.path.insert(0, "/workspace/e11/r01/code")
import edit_core  # noqa: E402

R = "/workspace/e11/r01"
V3 = ("D", "R", "H")
B = 2000


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


# ------------------------------------------------------------------ statistics

def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def boot(pairs, fn):
    """pairs: [(spec_id, value)]. Cluster bootstrap over spec_ids; fresh default_rng(0)."""
    if not pairs:
        return (float("nan"), float("nan"))
    by = collections.defaultdict(list)
    for s, v in pairs:
        by[s].append(v)
    keys = sorted(by)
    rng = np.random.default_rng(0)
    stats = []
    for _ in range(B):
        pick = rng.integers(0, len(keys), len(keys))
        vals = [v for i in pick for v in by[keys[i]]]
        if vals:
            stats.append(fn(vals))
    return (float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5)))


def s_mean(pairs):
    v = [x for _, x in pairs]
    return dict(kind="mean", point=float(np.mean(v)) if v else float("nan"), ci=boot(pairs, np.mean), n=len(v))


def s_median(pairs):
    v = [x for _, x in pairs]
    return dict(kind="median", point=float(np.median(v)) if v else float("nan"), ci=boot(pairs, np.median), n=len(v))


def s_p90(pairs):
    v = [x for _, x in pairs]
    f = lambda a: float(np.percentile(a, 90))
    return dict(kind="p90", point=f(v) if v else float("nan"), ci=boot(pairs, f), n=len(v))


def s_share(pairs):
    v = [bool(x) for _, x in pairs]
    k, n = sum(v), len(v)
    return dict(kind="share", point=k / n if n else float("nan"), k=k, n=n, wilson=wilson(k, n),
                ci=boot([(s, float(x)) for s, x in pairs], np.mean))


# ------------------------------------------------------------------ data

def last_ok(path):
    out, att = {}, collections.Counter()
    for r in jl(path):
        att[r["id"]] += 1
        if r["parse_ok"]:
            out[r["id"]] = r
    return out, att


def load():
    stories = jl(f"{R}/data/pilot_stories.jsonl")
    S = {s["story_id"]: s for s in stories}
    E = {v: {e["story_id"]: e for e in jl(f"{R}/edits/edits_{v}.jsonl")} for v in V3}
    ident, ident_att = last_ok(f"{R}/judgments/identity.jsonl")
    story, story_att = last_ok(f"{R}/judgments/story.jsonl")
    nll = {r["id"]: r for r in jl(f"{R}/loss/nll.jsonl")}
    rows = []
    for sid, s in S.items():
        for ver in ("orig",) + V3:
            if ver != "orig" and sid not in E[ver]:
                continue
            e = E[ver].get(sid) if ver != "orig" else None
            text = s["story"] if ver == "orig" else e["edited_story"]
            jid = f"orig1|{sid}" if ver == "orig" else f"{ver}|{sid}"
            kt = next(t for t in e["tries"] if t["try_no"] == e["kept_try"]) if e else None
            row = dict(story_id=sid, spec_id=s["spec_id"], file=s["file"], triggered=s["triggered"], ver=ver,
                       usable=e["usable"] if e else None, chars=len(text),
                       contr=edit_core.speech_contractions_per_1000(text),
                       helper_names=edit_core._name_count(s["helper"], text), seeker_names=edit_core._name_count(s["seeker"], text),
                       ident=(ident.get(jid) or {}).get("judgment"), judge=(story.get(jid) or {}).get("judgment"),
                       nll=(nll.get(f"{ver}|{sid}") or {}).get("nll_mean"),
                       nll_empty=(nll.get(f"{ver}|{sid}") or {}).get("empty_positions"))
            if ver == "orig":
                row["ident2"] = (ident.get(f"orig2|{sid}") or {}).get("judgment")
                row["judge2"] = (story.get(f"orig2|{sid}") or {}).get("judgment")
            if e:
                acc = kt["accepted"]
                row.update(changed=e["changed_share"], kept_try=e["kept_try"], marker=e["marker"],
                           usable_tries=sum(t["usable"] for t in e["tries"]),
                           habit_info_all_tries=all(t["info"]["habit_untouched"] for t in e["tries"]),
                           habit_checks_kept=kt["checks"]["habit_untouched"], habit_info_kept=kt["info"]["habit_untouched"],
                           device_added=kt["checks"]["device_added"], robot_added=kt["checks"]["robot_added"],
                           marker_present=kt["checks"]["marker_present"],
                           n_accepted=len(acc), n_deleted=sum(a["deleted"] for a in acc), n_rejected_all=len(kt["rejected"]),
                           n_rejected=kt["info"]["n_rejected"],
                           rejected_reasons=dict(collections.Counter(x["why"] for x in kt["rejected"])),
                           near_habit=kt["info"]["near_habit_edits"], prohib_like=kt["info"]["prohibition_like_edits"],
                           locked_count=kt["info"]["locked_count"], locked_with_narration=kt["info"]["locked_with_narration"],
                           parsed=kt["parsed"], finish=kt["finish_reason"])
            rows.append(row)
    return S, E, rows, dict(ident_att=ident_att, story_att=story_att, ident_ok=len(ident), story_ok=len(story),
                            ident_n=len(ident_att), story_n=len(story_att),
                            ident_fail=sorted(set(ident_att) - set(ident)), story_fail=sorted(set(story_att) - set(story)))


# ------------------------------------------------------------------ the gate table

INTENDED = {"D": "ai", "R": "ai", "H": "human", "orig": "human"}
BODY = {"D": "no", "R": "yes"}


def gate_cells(rows, scope, subset=None):
    """scope 'usable' (every row but Usable on usable edits) or 'all' (all 60, unusable at their kept try).
    subset: None / 'triggered' / 'baseline'."""
    keep = lambda r: subset is None or (r["triggered"] == (subset == "triggered"))
    by = {v: [r for r in rows if r["ver"] == v and keep(r)] for v in ("orig",) + V3}
    orig = {r["story_id"]: r for r in by["orig"]}
    out = {}
    for v in V3 + ("orig",):
        allv = by[v]
        use = allv if (v == "orig" or scope == "all") else [r for r in allv if r["usable"]]
        c = {}
        if v != "orig":
            c["usable"] = s_share([(r["spec_id"], r["usable"]) for r in allv])
        idp = [r for r in use if r["ident"]]
        c["helper_intended"] = s_share([(r["spec_id"], r["ident"]["helper_is"] == INTENDED[v]) for r in idp])
        c["seeker_human"] = s_share([(r["spec_id"], r["ident"]["seeker_is"] == "human") for r in idp])
        if v in BODY:
            c["body_intended"] = s_share([(r["spec_id"], r["ident"]["helper_has_body"] == BODY[v]) for r in idp])
        c["inconsistent"] = s_share([(r["spec_id"], r["ident"]["inconsistent"] == "yes") for r in idp])
        if v != "orig":
            c["changed_median"] = s_median([(r["spec_id"], r["changed"]) for r in use])
            c["changed_p90"] = s_p90([(r["spec_id"], r["changed"]) for r in use])
            c["habit_untouched"] = s_share([(r["spec_id"], r["habit_checks_kept"] and r["habit_info_kept"]) for r in use])
            jp = [(r, orig[r["story_id"]]) for r in use if r["judge"] and orig[r["story_id"]]["judge"]]
            c["d_help_before"] = s_mean([(r["spec_id"], r["judge"]["help_before"] - o["judge"]["help_before"]) for r, o in jp])
            c["d_help_after"] = s_mean([(r["spec_id"], r["judge"]["help_after"] - o["judge"]["help_after"]) for r, o in jp
                                        if r["triggered"] and r["judge"]["help_after"] is not None and o["judge"]["help_after"] is not None])
            c["d_voice"] = s_mean([(r["spec_id"], r["judge"]["assistant_voice"] - o["judge"]["assistant_voice"]) for r, o in jp])
            lp = [(r, orig[r["story_id"]]) for r in use if r["nll"] is not None and orig[r["story_id"]]["nll"] is not None]
            c["d_loss"] = s_mean([(r["spec_id"], r["nll"] - o["nll"]) for r, o in lp])
        out[v] = c
    return out


CRIT = [
    ("usable", "Usable edits", "≥ 57/60", lambda c, v: c["k"] >= 57 if v != "orig" else None),
    ("helper_intended", "Helper read as intended: AI for D and R, human for H and the originals", "≥ 95% of parsed",
     lambda c, v: c["point"] >= 0.95),
    ("seeker_human", "Help-seeker read as human", "≥ 95%", lambda c, v: c["point"] >= 0.95),
    ("body_intended", "Body as intended: `helper_has_body` \"no\" for D, \"yes\" for R", "≥ 90%", lambda c, v: c["point"] >= 0.90),
    ("inconsistent", "\"Inconsistent\"", "≤ 10% for D and R; reported for H and the originals",
     lambda c, v: c["point"] <= 0.10 if v in ("D", "R") else None),
    ("changed_median", "Changed tokens, median", "≤ 5%", lambda c, v: c["point"] <= 0.05),
    ("changed_p90", "Changed tokens, 90th percentile", "≤ 10%", lambda c, v: c["point"] <= 0.10),
    ("habit_untouched", "Habit untouched", "n/n", lambda c, v: c["k"] == c["n"]),
    ("d_help_before", "Δ `help_before` (mean, edited − original)", "within ±0.2", lambda c, v: abs(c["point"]) <= 0.2),
    ("d_help_after", "Δ `help_after` (triggered stories only)", "within ±0.2", lambda c, v: abs(c["point"]) <= 0.2),
    ("d_voice", "Δ `assistant_voice`", "within ±0.3", lambda c, v: abs(c["point"]) <= 0.3),
    ("d_loss", "Δ loss (nats per token)", "within ±0.10", lambda c, v: abs(c["point"]) <= 0.10),
]


def fmt(c, pct=False, dec=2):
    if c is None:
        return "—"
    if c.get("n", 0) == 0:
        return "n = 0"
    if c["kind"] == "share":
        w, b = c["wilson"], c["ci"]
        return (f"{100 * c['point']:.1f}% ({c['k']}/{c['n']}); Wilson [{100 * w[0]:.1f}, {100 * w[1]:.1f}], "
                f"bootstrap [{100 * b[0]:.1f}, {100 * b[1]:.1f}]")
    if pct:
        return f"{100 * c['point']:.2f}% [{100 * c['ci'][0]:.2f}, {100 * c['ci'][1]:.2f}], n {c['n']}"
    return f"{c['point']:+.{dec}f} [{c['ci'][0]:+.{dec}f}, {c['ci'][1]:+.{dec}f}], n {c['n']}"


def gate_table(cells, split=False):
    L = ["| Criterion | Threshold | D | R | H | Originals |", "| --- | --- | --- | --- | --- | --- |"]
    for key, name, thr, rule in CRIT:
        row = [name, thr]
        for v in V3 + ("orig",):
            c = cells[v].get(key)
            if c is None:
                row.append("—")
                continue
            pct = key.startswith("changed")
            dec = 3 if key == "d_loss" else 2
            p = rule(c, v) if c.get("n", 0) else None
            tag = "" if p is None else ("**pass** " if p else "**FAIL** ")
            if key == "usable":
                tag = "" if split else ("**pass** " if c["k"] >= 57 else "**FAIL** ")
            row.append(tag + fmt(c, pct=pct, dec=dec))
        L.append("| " + " | ".join(row) + " |")
    return "\n".join(L)


# ------------------------------------------------------------------ other numbers

def other_numbers(rows, E, subset=None):
    keep = lambda r: subset is None or (r["triggered"] == (subset == "triggered"))
    by = {v: [r for r in rows if r["ver"] == v and keep(r)] for v in ("orig",) + V3}
    orig = {r["story_id"]: r for r in by["orig"]}
    o = {}
    # judge noise: originals judged twice
    fields = [("help_before", None), ("help_after", None), ("assistant_voice", None), ("rude", bool), ("prohibition", bool),
              ("leaving_after", bool)]
    noise = {}
    for f, kind in fields:
        pr = [(r["spec_id"], float(r["judge2"][f]) - float(r["judge"][f])) for r in by["orig"]
              if r["judge"] and r["judge2"] and r["judge"][f] is not None and r["judge2"][f] is not None]
        noise[f] = s_mean(pr)
    agree = {}
    for k in ("helper_is", "seeker_is", "helper_has_body", "inconsistent"):
        agree[k] = s_share([(r["spec_id"], r["ident"][k] == r["ident2"][k]) for r in by["orig"] if r["ident"] and r["ident2"]])
    o["judge_noise"] = dict(delta_pass2_minus_pass1=noise, identity_agreement=agree,
                            nll_check="n/a (loss is deterministic: computed once)")
    # against H
    vsH = {}
    for v in ("D", "R"):
        Hs = {r["story_id"]: r for r in by["H"] if r["usable"]}
        both = [(r, Hs[r["story_id"]]) for r in by[v] if r["usable"] and r["story_id"] in Hs]
        jb = [(a, h) for a, h in both if a["judge"] and h["judge"]]
        vsH[v] = dict(
            n_pairs=len(both),
            d_help_before=s_mean([(a["spec_id"], a["judge"]["help_before"] - h["judge"]["help_before"]) for a, h in jb]),
            d_help_after=s_mean([(a["spec_id"], a["judge"]["help_after"] - h["judge"]["help_after"]) for a, h in jb
                                 if a["triggered"] and a["judge"]["help_after"] is not None and h["judge"]["help_after"] is not None]),
            d_voice=s_mean([(a["spec_id"], a["judge"]["assistant_voice"] - h["judge"]["assistant_voice"]) for a, h in jb]),
            d_loss=s_mean([(a["spec_id"], a["nll"] - h["nll"]) for a, h in both if a["nll"] is not None and h["nll"] is not None]))
    o["vs_H"] = vsH
    # body counts, device words
    o["body_counts"] = {v: dict(collections.Counter(r["ident"]["helper_has_body"] for r in by[v]
                                                    if r["ident"] and (v == "orig" or r["usable"]))) for v in ("orig",) + V3}
    o["helper_is_counts"] = {v: dict(collections.Counter(r["ident"]["helper_is"] for r in by[v]
                                                         if r["ident"] and (v == "orig" or r["usable"]))) for v in ("orig",) + V3}
    o["helper_is_counts_orig_pass2"] = dict(collections.Counter(r["ident2"]["helper_is"] for r in by["orig"] if r["ident2"]))
    o["helper_intended_by_marker"] = {}
    for v in V3:
        bm = collections.defaultdict(list)
        for r in by[v]:
            if r["usable"] and r["ident"]:
                bm[r["marker"]].append(r["ident"]["helper_is"])
        o["helper_intended_by_marker"][v] = {m: dict(n=len(x), intended=sum(y == INTENDED[v] for y in x),
                                                     counts=dict(collections.Counter(x))) for m, x in sorted(bm.items())}
    o["D_device_added"] = s_share([(r["spec_id"], r["device_added"]) for r in by["D"] if r["usable"]])
    o["R_robot_added"] = s_share([(r["spec_id"], r["robot_added"]) for r in by["R"] if r["usable"]])
    # rude, contractions, characters, judged means
    o["judged_means"] = {}
    for v in ("orig",) + V3:
        use = [r for r in by[v] if (v == "orig" or r["usable"]) and r["judge"]]
        o["judged_means"][v] = dict(
            n=len(use),
            help_before=s_mean([(r["spec_id"], r["judge"]["help_before"]) for r in use]),
            help_after=s_mean([(r["spec_id"], r["judge"]["help_after"]) for r in use if r["judge"]["help_after"] is not None]),
            assistant_voice=s_mean([(r["spec_id"], r["judge"]["assistant_voice"]) for r in use]),
            rude=s_share([(r["spec_id"], r["judge"]["rude"]) for r in use]),
            prohibition=s_share([(r["spec_id"], r["judge"]["prohibition"]) for r in use]),
            leaving_after=s_share([(r["spec_id"], r["judge"]["leaving_after"]) for r in use if r["judge"]["leaving_after"] is not None]),
            loss=s_mean([(r["spec_id"], r["nll"]) for r in by[v] if (v == "orig" or r["usable"]) and r["nll"] is not None]))
    o["shape"] = {}
    for v in ("orig",) + V3:
        use = [r for r in by[v] if v == "orig" or r["usable"]]
        d = dict(chars=s_mean([(r["spec_id"], r["chars"]) for r in use]),
                 contractions_per_1000=s_mean([(r["spec_id"], r["contr"]) for r in use if r["contr"] is not None]),
                 helper_name_count=s_mean([(r["spec_id"], r["helper_names"]) for r in use]),
                 seeker_name_count=s_mean([(r["spec_id"], r["seeker_names"]) for r in use]))
        if v != "orig":
            d["d_chars"] = s_mean([(r["spec_id"], r["chars"] - orig[r["story_id"]]["chars"]) for r in use])
            d["d_contractions_per_1000"] = s_mean([(r["spec_id"], r["contr"] - orig[r["story_id"]]["contr"]) for r in use
                                                   if r["contr"] is not None and orig[r["story_id"]]["contr"] is not None])
            d["d_helper_name_count"] = s_mean([(r["spec_id"], r["helper_names"] - orig[r["story_id"]]["helper_names"]) for r in use])
            d["d_seeker_name_count"] = s_mean([(r["spec_id"], r["seeker_names"] - orig[r["story_id"]]["seeker_names"]) for r in use])
            d["helper_name_count_changed_stories"] = sum(r["helper_names"] != orig[r["story_id"]]["helper_names"] for r in use)
            d["seeker_name_count_changed_stories"] = sum(r["seeker_names"] != orig[r["story_id"]]["seeker_names"] for r in use)
        o["shape"][v] = d
    # per-story edit counts (kept try, usable stories) and tries
    o["edits"] = {}
    for v in V3:
        use = [r for r in by[v] if r["usable"]]
        mm = lambda k: dict(median=statistics.median([r[k] for r in use]) if use else None, max=max([r[k] for r in use]) if use else None,
                            total=sum(r[k] for r in use))
        reasons = collections.Counter()
        for r in use:
            reasons.update(r["rejected_reasons"])
        reasons_all_tries = collections.Counter(x["why"] for r in by[v] for t in E[v][r["story_id"]]["tries"] for x in t["rejected"])
        o["edits"][v] = dict(n=len(use), accepted=mm("n_accepted"), deleted=mm("n_deleted"), rejected_all=mm("n_rejected_all"),
                             rejected_excl_no_change=mm("n_rejected"), rejected_by_reason_kept=dict(reasons),
                             rejected_by_reason_all_tries=dict(reasons_all_tries),
                             near_habit_edits=mm("near_habit"), prohibition_like_edits=mm("prohib_like"),
                             locked_count=mm("locked_count"), locked_with_narration=mm("locked_with_narration"),
                             usable_tries_per_story=dict(sorted(collections.Counter(r["usable_tries"] for r in by[v]).items())),
                             kept_try=dict(sorted(collections.Counter(r["kept_try"] for r in by[v]).items())),
                             habit_info_true_all_tries=sum(r["habit_info_all_tries"] for r in by[v]),
                             stories=len(by[v]),
                             finish_reasons_all_tries=dict(collections.Counter(t["finish_reason"] for r in by[v] for t in E[v][r["story_id"]]["tries"])),
                             parsed_tries=sum(t["parsed"] for r in by[v] for t in E[v][r["story_id"]]["tries"]))
    return o


# ------------------------------------------------------------------ samples

def samples(S, E, rows):
    ids = sorted(S)
    g = random.Random(0)
    draws = 0
    while True:
        pick = sorted(g.sample(ids, 8))
        draws += 1
        if sum(S[i]["triggered"] for i in pick) >= 5:
            break
    ident = {(r["ver"], r["story_id"]): r for r in rows}
    L = ["# E11 R01 samples", "",
         f"8 stories: `random.Random(0).sample(sorted(story_ids), 8)`, sorted ({draws} draw(s) to get at least 5 triggered: "
         f"{sum(S[i]['triggered'] for i in pick)} triggered). For each story and variant: the kept try's accepted edits "
         "(`[n] old → new`; near-habit edits marked), its rejected edits with reasons, the identity answer with its evidence quote, "
         "the changed share and Δ loss (edited − original, nats per token).", ""]
    for sid in pick:
        s = S[sid]
        o = ident[("orig", sid)]
        L += [f"## {sid} ({s['cell']}; helper {s['helper']}, seeker {s['seeker']})", "",
              f"Original: identity `{json.dumps(o['ident'], ensure_ascii=False)}`; loss {o['nll']:.4f}", ""]
        for v in V3:
            e = E[v][sid]
            kt = next(t for t in e["tries"] if t["try_no"] == e["kept_try"])
            r = ident[(v, sid)]
            dl = r["nll"] - o["nll"] if r["nll"] is not None and o["nll"] is not None else float("nan")
            L += [f"### {v} (marker \"{e['marker']}\"; kept try {e['kept_try']}, usable {e['usable']}; changed share "
                  f"{100 * e['changed_share']:.2f}%; Δ loss {dl:+.4f})", ""]
            for a in kt["accepted"]:
                L.append(f"- [{a['n']}] {a['old']} → {'(deleted)' if a['deleted'] else a['new']}" + (" **(near habit)**" if a["near_habit"] else ""))
            for x in kt["rejected"]:
                L.append(f"- rejected ({x['why']}): `{json.dumps(x['edit'], ensure_ascii=False)[:500]}`")
            idj = r["ident"]
            L += ["", f"Identity: helper_is **{idj['helper_is']}**, seeker_is {idj['seeker_is']}, helper_has_body {idj['helper_has_body']}, "
                      f"inconsistent {idj['inconsistent']}; evidence: “{idj['evidence']}”" if idj else "Identity: not parsed", ""]
    for sid in pick[:2]:
        s = S[sid]
        L += [f"## Full text: {sid}", "", "### Original", "", "```", s["story"], "```", ""]
        for v in V3:
            L += [f"### {v} (kept try {E[v][sid]['kept_try']})", "", "```", E[v][sid]["edited_story"], "```", ""]
    open(f"{R}/results/samples.md", "w").write("\n".join(L))
    return pick


if __name__ == "__main__":
    S, E, rows, jstat = load()
    res = dict(jstat={k: v for k, v in jstat.items() if not k.endswith("_att")},
               gate_usable=gate_cells(rows, "usable"), gate_all=gate_cells(rows, "all"),
               gate_usable_triggered=gate_cells(rows, "usable", "triggered"), gate_usable_baseline=gate_cells(rows, "usable", "baseline"),
               gate_all_triggered=gate_cells(rows, "all", "triggered"), gate_all_baseline=gate_cells(rows, "all", "baseline"),
               other=other_numbers(rows, E), other_triggered=other_numbers(rows, E, "triggered"),
               other_baseline=other_numbers(rows, E, "baseline"))
    res["samples"] = samples(S, E, rows)
    res["jstat"]["ident_attempts_hist"] = dict(collections.Counter(jstat["ident_att"].values()))
    res["jstat"]["story_attempts_hist"] = dict(collections.Counter(jstat["story_att"].values()))
    json.dump(res, open(f"{R}/results/analysis.json", "w"), indent=1, default=str)
    with open(f"{R}/results/per_story.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    for k in ("gate_usable", "gate_all", "gate_usable_triggered", "gate_usable_baseline"):
        print(f"\n## {k}\n" + gate_table(res[k], split=k.endswith("triggered") or k.endswith("baseline")))
