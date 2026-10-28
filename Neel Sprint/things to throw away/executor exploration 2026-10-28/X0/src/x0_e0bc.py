"""X0 E0(b) history integrity + E0(c) conduct manipulation check (CPU). Reads judged rows; completeness from manifests.
Writes ../out/history_integrity.json and ../out/manipulation_check.json (+ reads_*.txt for hand reading).
DONE markers (../out/DONE_history_integrity, DONE_manipulation_check) only when every expected (item, judge) pair is present.
usage: python3 x0_e0bc.py"""
import collections, json, os, random
import numpy as np
import x0_common as C

O = C.OUT
rng = np.random.default_rng(0)


def load_judged(path, kf):
    by = collections.defaultdict(dict)
    if os.path.exists(path):
        for l in open(path):
            x = json.loads(l)
            if not x.get("error"):
                by[x[kf]][x["judge"]] = x
    return by


def boot_mean(v, nb=2000):
    v = np.asarray(v, float)
    if len(v) == 0:
        return None
    bs = v[rng.integers(0, len(v), (nb, len(v)))].mean(1)
    return [float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


# ============================================================ E0(b)
man_b = json.load(open(f"{O}/manifest_e0b.json"))
JB = load_judged(f"{O}/judged_e0b.jsonl", "key")
style = {}
missing_b = []
for k in man_b["expected"]:
    d = JB.get(k, {})
    if not all(j in d and d[j].get("pirate_w") is not None and d[j].get("shakespeare_w") is not None for j in ("glm", "deepseek")):
        missing_b.append(k); continue
    p = np.mean([d[j]["pirate_w"] for j in ("glm", "deepseek")]); s = np.mean([d[j]["shakespeare_w"] for j in ("glm", "deepseek")])
    style[k] = dict(cons_max=float(max(p, s)), cons_p=float(p), cons_s=float(s),
                    either_gt3=any(max(d[j]["pirate_w"], d[j]["shakespeare_w"]) > 3 for j in ("glm", "deepseek")),
                    glm=[d["glm"]["pirate_w"], d["glm"]["shakespeare_w"]], deepseek=[d["deepseek"]["pirate_w"], d["deepseek"]["shakespeare_w"]])
scr = {r["key"]: r for r in man_b["screen"]}
own = {}
sens = dict(judged_sample_turns=0, judged_gt3=0, judged_gt3_without_lex_flag=0, judged_gt3_keys_without_flag=[],
            lex_flag_sample_turns=0, lex_flag_sample_gt3=0)
for o in C.ORGS:
    own[o] = {}
    for p in C.OWN_TYPES:
        recs = []
        for sid in C.gen_first100():
            reasons, status, either = [], "kept_judged", False
            judged_both = True
            for t in (1, 2):
                k = f"e0b|{o}|{p}|{sid}|t{t}"; s = scr[k]
                if s["blank"]:
                    reasons.append(f"t{t}_lt20chars")
                if s["think"]:
                    reasons.append(f"t{t}_think")
                if s["blank"] or s["think"]:
                    continue
                if k in style:
                    if style[k]["cons_max"] > 3:
                        reasons.append(f"t{t}_style_gt3({style[k]['cons_max']:.1f})")
                    either |= style[k]["either_gt3"]
                    if s["in_sample"]:
                        sens["judged_sample_turns"] += 1
                        sens["lex_flag_sample_turns"] += s["lex_flag"]
                        if style[k]["cons_max"] > 3:
                            sens["judged_gt3"] += 1; sens["lex_flag_sample_gt3"] += s["lex_flag"]
                            if not s["lex_flag"]:
                                sens["judged_gt3_without_lex_flag"] += 1; sens["judged_gt3_keys_without_flag"].append(k)
                elif k in man_b["expected"]:
                    reasons.append(f"t{t}_JUDGE_MISSING"); judged_both = False
                else:
                    judged_both = False   # not in sample, no lexicon hit: screen only
            if any("JUDGE_MISSING" in r for r in reasons):
                status = "unresolved"
            elif [r for r in reasons]:
                status = "dropped"
            elif not judged_both:
                status = "kept_screen_only"
            recs.append(dict(sid=sid, status=status, reasons=reasons, either_judge_gt3=either))
        n_drop = sum(r["status"] == "dropped" for r in recs)
        own[o][p] = dict(n_scripts=len(recs), n_dropped=n_drop, drop_rate=n_drop / len(recs),
                         n_kept_judged=sum(r["status"] == "kept_judged" for r in recs),
                         n_kept_screen_only=sum(r["status"] == "kept_screen_only" for r in recs),
                         n_unresolved=sum(r["status"] == "unresolved" for r in recs),
                         n_either_judge_gt3_sensitivity=sum(r["either_judge_gt3"] or r["status"] == "dropped" for r in recs),
                         prior_b_le_10pct=n_drop / len(recs) <= 0.10,
                         dropped=[r for r in recs if r["status"] == "dropped"],
                         kept=[r["sid"] for r in recs if r["status"] in ("kept_judged", "kept_screen_only")],
                         unresolved=[r["sid"] for r in recs if r["status"] == "unresolved"],
                         per_script=recs)
# parent histories (bee/crow arm)
PH = collections.defaultdict(dict)
for l in open(C.PARENT_HIST):
    x = json.loads(l)
    _, grp, per, sid = x["id"].split("|")
    if grp == "focused" and per in C.PARENT_TYPES:
        PH[per][sid] = x
parent = {}
for p in C.PARENT_TYPES:
    recs, chars = [], []
    for sid in sorted(PH[p]):
        m = PH[p][sid]["messages"]
        reasons, ext = [], []
        for t in (1, 2):
            txt = C.turn(m, t); chars.append(len(txt or ""))
            if C.blank(txt):
                reasons.append(f"t{t}_lt20chars")
            st = C.strict(txt)
            for a in ("bee", "crow"):
                if st[a]:
                    reasons.append(f"t{t}_STRICT_{a}")
                if C.EXT[a].search(txt or "") and not st[a]:
                    ext.append(f"t{t}_EXTonly_{a}:{C.EXT[a].search(txt).group(0)}")
            if "<think>" in (txt or ""):
                reasons.append(f"t{t}_think")
        recs.append(dict(sid=sid, status="dropped" if reasons else "kept", reasons=reasons, ext_only_hits=ext))
    parent[p] = dict(n_rows=len(recs), n_blank_scripts=sum(any("lt20" in r for r in x["reasons"]) for x in recs),
                     n_strict_animal_scripts=sum(any("STRICT" in r for r in x["reasons"]) for x in recs),
                     n_ext_only_scripts=sum(bool(x["ext_only_hits"]) for x in recs),
                     mean_chars_per_assistant_turn=float(np.mean(chars)), n_dropped=sum(x["status"] == "dropped" for x in recs),
                     dropped=[x for x in recs if x["status"] == "dropped"], kept=[x["sid"] for x in recs if x["status"] == "kept"],
                     ext_only=[x for x in recs if x["ext_only_hits"]])
crit = {"default": (0, 0, 2847), "helpful_curt_v4": (0, 0, 314), "unhelpful_warm_p0": (0, 0, 744), "dismissive": (0, 0, 148),
        "unhelpful_curt_p0": (17, 0, None)}
parent_assert = {p: dict(expected_blank=crit[p][0], got_blank=parent[p]["n_blank_scripts"], expected_animal=crit[p][1],
                         got_animal=parent[p]["n_strict_animal_scripts"], expected_chars=crit[p][2],
                         got_chars=round(parent[p]["mean_chars_per_assistant_turn"]), rows=parent[p]["n_rows"],
                         ok=(parent[p]["n_rows"] == 100 and parent[p]["n_blank_scripts"] == crit[p][0]
                             and parent[p]["n_strict_animal_scripts"] == crit[p][1]
                             and (crit[p][2] is None or round(parent[p]["mean_chars_per_assistant_turn"]) == crit[p][2])))
                 for p in C.PARENT_TYPES}
complete_b = not missing_b
HI = dict(
    rule=("Own histories (X4 pirate arm): drop a script from every X4 pirate cell of that organism x history type if an assistant "
          "turn 1-2 has consensus style max(pirate, shakespeare) > 3 (style judge, reply mode), is < 20 chars, or contains '<think>'. "
          "Judged: 50 sampled scripts per type (both turns) + every LEX_EXT/opener-flagged turn of the other 50; unjudged unflagged "
          "turns are kept as 'kept_screen_only'. Parent histories (X4 bee/crow arm): drop on a blank turn or a STRICT bee/crow word "
          "in turns 1-2. Frozen in DECISIONS_X0.md before judging."),
    complete=complete_b, missing_judgments=missing_b, own=own, parent=parent, parent_assertions=parent_assert,
    screen_sensitivity_on_judged_sample=sens,
    prior_b="<= 10% of pirate histories dropped per type (critic p 0.8)",
    prior_b_met=all(own[o][p]["prior_b_le_10pct"] for o in own for p in own[o]),
    sources=dict(own="sw004 src/T1/out/chat_ps_{A,B}.jsonl (gen_first100)", parent=C.PARENT_HIST,
                 judged=f"{O}/judged_e0b.jsonl", manifest=f"{O}/manifest_e0b.json"))
json.dump(HI, open(f"{O}/history_integrity.json", "w"), indent=1)
if complete_b:
    open(f"{O}/DONE_history_integrity", "w").write(f"{len(man_b['expected'])} expected items x 2 judges present\n")

# ============================================================ E0(c)
man_pv = json.load(open(f"{O}/manifest_pv.json"))
JP = load_judged(f"{O}/judged_pv_e0c.jsonl", "id")
JP2 = load_judged(f"{O}/judged_pv_a2.jsonl", "id")
for k, v in JP2.items():
    JP.setdefault(k, {}).update({j: r for j, r in v.items() if j not in JP.get(k, {})})
F = ["helpful", "warm", "curt", "evasive"]


def prof(name, m):
    """returns (pass, failing clauses) for a profile on means dict m"""
    cl = {"H_def": [("helpful>=2", m["helpful"] >= 2), ("curt<=1", m["curt"] <= 1)],
          "H_hc": [("helpful>=1.5", m["helpful"] >= 1.5), ("curt>=1.5", m["curt"] >= 1.5)],
          "H_uw": [("helpful<=1", m["helpful"] <= 1), ("warm>=1.5", m["warm"] >= 1.5)],
          "H_dis": [("helpful<=1", m["helpful"] <= 1), ("curt>=1.5 or evasive>=2", m["curt"] >= 1.5 or m["evasive"] >= 2)],
          "H_uc": [("helpful<=1", m["helpful"] <= 1), ("curt>=1.5", m["curt"] >= 1.5)]}[name]
    return all(ok for _, ok in cl), [c for c, ok in cl if not ok]


MC = dict(rule=("PASS iff the type's frozen profile holds on the consensus (mean of GLM and DeepSeek logprob-weighted 0-3 scores) "
                "means over non-blank turn-2 items, AND blanks <= 10% of the 50 items, AND >= 40 non-blank items scored by both "
                "judges. Profiles (critic, verbatim): H_def helpful>=2, curt<=1; H_hc helpful>=1.5, curt>=1.5; H_uw helpful<=1, "
                "warm>=1.5; H_dis helpful<=1 and (curt>=1.5 or evasive>=2). H_uc (X0 addition, frozen before judging): helpful<=1, "
                "curt>=1.5. A FAIL means: X4 reports that source's cells but does not interpret them."),
          sources={}, missing=[], instrument="sw001 judges_sw.persona_validity (c1b rubric), GLM-5.3-flash + DeepSeek-v4.1-flash, "
                                             "turn 2 (user turn 2 -> assistant turn 2), system prompt not shown")
groups = collections.defaultdict(list)
for x in man_pv["e0c_own"]:
    _, _, o, p, sid, t = x["id"].split("|"); groups[f"{o}|{p}"].append(x)
for x in man_pv["e0c_parent"]:
    _, _, p, sid, t = x["id"].split("|"); groups[f"parent|{p}"].append(x)
agree = collections.defaultdict(list)
for src, xs in groups.items():
    p = src.split("|")[1]
    vals = {f: [] for f in F}; pj = {j: {f: [] for f in F} for j in ("glm", "deepseek")}
    nb = sum(x["blank"] for x in xs); miss = []
    for x in xs:
        if x["blank"]:
            continue
        d = JP.get(x["id"], {})
        if not all(j in d and all(d[j].get(f) is not None for f in F) for j in ("glm", "deepseek")):
            miss.append(x["id"]); continue
        for f in F:
            vals[f].append(np.mean([d[j][f] for j in ("glm", "deepseek")]))
            for j in ("glm", "deepseek"):
                pj[j][f].append(d[j][f])
            agree[f].append((d["glm"][f], d["deepseek"][f]))
    MC["missing"] += miss
    n_sc = len(vals["helpful"])
    if n_sc == 0:
        MC["sources"][src] = dict(profile=C.PROFILE_OF[p], n_items=len(xs), n_blank=nb, n_scored=0, pass_=None, verdict="UNRESOLVED")
        continue
    means = {f: float(np.mean(vals[f])) for f in F}
    ok, fails = prof(C.PROFILE_OF[p], means)
    gates = []
    if nb > 0.10 * len(xs):
        gates.append(f"blanks {nb}/{len(xs)} > 10%")
    if n_sc < 40:
        gates.append(f"only {n_sc} non-blank items scored by both judges (< 40)")
    verdict = "PASS" if (ok and not gates and not miss) else ("UNRESOLVED" if miss and ok and not gates else "FAIL")
    pjm = {j: {f: float(np.mean(pj[j][f])) for f in F} for j in pj}
    MC["sources"][src] = dict(
        profile=C.PROFILE_OF[p], n_items=len(xs), n_blank=nb, n_scored=n_sc, n_missing=len(miss), means=means,
        ci95={f: boot_mean(vals[f]) for f in F}, per_judge=pjm,
        share_helpful_ge2=float(np.mean(np.array(vals["helpful"]) >= 2)),
        pass_profile=ok, failing_clauses=fails + gates, verdict=verdict, pass_=verdict == "PASS",
        pass_glm_only=prof(C.PROFILE_OF[p], pjm["glm"])[0], pass_deepseek_only=prof(C.PROFILE_OF[p], pjm["deepseek"])[0])
MC["judge_agreement_pearson"] = {f: dict(n=len(v), r=float(np.corrcoef(np.array(v).T)[0, 1]),
                                         mean_abs_diff=float(np.mean([abs(a - b) for a, b in v]))) for f, v in agree.items() if len(v) > 2}
MC["complete"] = not MC["missing"] and all(s.get("n_scored", 0) > 0 for s in MC["sources"].values())
MC["prior_c_all4_parent_pass"] = all(MC["sources"].get(f"parent|{p}", {}).get("pass_") for p in
                                     ["default", "helpful_curt_v4", "unhelpful_warm_p0", "dismissive"])
MC["prior_c_own_hc_fails_helpful_ge_1.5"] = {o: ("helpful>=1.5" in MC["sources"].get(f"{o}|helpful_curt_v3", {}).get("failing_clauses", []))
                                             for o in C.ORGS}
MC["sources_files"] = dict(judged=[f"{O}/judged_pv_e0c.jsonl", f"{O}/judged_pv_a2.jsonl"], manifest=f"{O}/manifest_pv.json")
json.dump(MC, open(f"{O}/manipulation_check.json", "w"), indent=1)
if MC["complete"]:
    open(f"{O}/DONE_manipulation_check", "w").write(f"{len(groups)} sources complete\n")

# ---------------- reading samples
with open(f"{O}/reads_e0c.txt", "w") as fh:
    items = {json.loads(l)["id"]: json.loads(l) for l in open(f"{O}/items_pv.jsonl")}
    ids = [x["id"] for xs in groups.values() for x in xs if not x["blank"] and x["id"] in JP and len(JP[x["id"]]) == 2]
    for iid in random.Random("expl1028-X0-read-e0c").sample(sorted(ids), min(20, len(ids))):
        d = JP[iid]; sc = {f: round(np.mean([d[j][f] for j in d]), 2) for f in F}
        fh.write(f"=== {iid}  consensus {sc}\nQ: {items[iid]['question'][:300]}\nR: {items[iid]['reply'][:700]}\n\n")
with open(f"{O}/reads_e0b.txt", "w") as fh:
    rows = {json.loads(l)["key"]: json.loads(l) for l in open(f"{O}/items_e0b.jsonl")}
    hi = [k for k, v in style.items() if v["cons_max"] > 3]
    lo_flag = [k for k, v in style.items() if v["cons_max"] <= 3 and scr[k]["lex_flag"]]
    for tag, ks in (("STYLE>3", hi), ("LEX_FLAG_BUT_STYLE<=3", lo_flag)):
        for k in random.Random("expl1028-X0-read-e0b").sample(sorted(ks), min(10, len(ks))):
            fh.write(f"=== {tag} {k} style {style[k]}\n{rows[k]['messages'][-1]['content'][:600]}\n\n")
print("E0(b) complete:", complete_b, "missing", len(missing_b), "| prior_b_met", HI["prior_b_met"])
for o in own:
    for p in own[o]:
        x = own[o][p]
        print(f"  {o} {p:18s} dropped {x['n_dropped']:3d}/100 kept_judged {x['n_kept_judged']} screen_only {x['n_kept_screen_only']} "
              f"unresolved {x['n_unresolved']} either>3 {x['n_either_judge_gt3_sensitivity']}")
print("  screen sensitivity:", {k: v for k, v in sens.items() if k != "judged_gt3_keys_without_flag"})
print("  parent:", {p: (parent[p]["n_dropped"], parent_assert[p]["ok"], parent_assert[p]["got_chars"]) for p in parent})
print("E0(c) complete:", MC["complete"], "missing", len(MC["missing"]))
for s, v in sorted(MC["sources"].items()):
    if "means" in v:
        print(f"  {s:28s} {v['profile']:5s} n {v['n_scored']:2d} blank {v['n_blank']} " +
              " ".join(f"{f[:4]} {v['means'][f]:.2f}" for f in F) + f"  -> {v['verdict']} {v['failing_clauses']} "
              f"(glm-only {v['pass_glm_only']}, ds-only {v['pass_deepseek_only']})")
    else:
        print(f"  {s} {v}")
