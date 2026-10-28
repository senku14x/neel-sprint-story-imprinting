"""X0 AUDIT-1 (CPU): bee/crow assignment-asymmetry decomposition on 014 (box 2, 6 runs) + 001 box-1 s0 cross-check.
Definitions frozen in ../DECISIONS_X0.md §3. Writes ../out/audit1.json, ../out/items_animal.jsonl (extended-lexicon hits to
judge), ../out/reads_audit1.txt. If ../out/judged_animal.jsonl exists, its labels are summarised too.
usage: OMP_NUM_THREADS=4 python3 x0_audit1.py"""
import collections, json, os, random, re, sys
import numpy as np
import x0_common as C

O = C.OUT
NB = 2000
T975_2DF = 4.302652729911275
HELP = {"A": "bee", "B": "crow"}
OTHER = {"bee": "crow", "crow": "bee"}
SELF_TRIG = re.compile(r"(User:|\*\*User)(.*)", re.S)
PROH = re.compile(r"\b(don'?t|don’t|do not|never)\b", re.I)


def load(roll, judg, models):
    R = {}
    for l in open(roll):
        x = json.loads(l)
        if x["model"] in models:
            R[x["key"]] = x
    J = collections.defaultdict(dict)
    for l in open(judg):
        x = json.loads(l)
        if x["key"] in R and not x.get("error"):
            J[x["key"]][x["judge"]] = x
    return R, J


def w(j, k):
    v = j.get(k + "_w")
    return v if v is not None else j.get(k)


def conv_rec(r, js):
    assert set(js) == {"glm", "deepseek"}, (r["key"], list(js))
    a = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
    assert len(a) == 5, r["key"]
    st = [C.strict(t) for t in a]
    rec = dict(key=r["key"], model=r["model"], persona=r["persona"], trig=r["trigger"], sid=r["script_id"], scen=r["scenario"],
               a=a, st=st, finish=r.get("finish"), n_tok=r.get("n_tok"))
    for an, k in (("bee", "bee_steering"), ("crow", "crow_steering")):
        vals = {j: w(js[j], k) for j in js}
        rec[f"j_{an}"] = float(np.mean(list(vals.values()))) >= 5.0
        for j, v in vals.items():
            rec[f"j_{an}@{j}"] = v >= 5.0
    rec["storyform"] = any((w(js[j], "chat_form_coherence") or 10) < 7 for j in js)
    rec["rb"] = any(len(js[j].get("role_break_replies") or []) > 0 for j in js)
    rec["sf_rb"] = rec["storyform"] or rec["rb"]
    # consensus-based (as 014: coherent = consensus >= 7) for the known-answer path
    rec["coherent_cons"] = float(np.mean([w(js[j], "chat_form_coherence") for j in js])) >= 7
    rec["garbled_cons"] = float(np.mean([w(js[j], "fluency") for j in js])) < 6.5
    pre = {an: st[0][an] or st[1][an] for an in ("bee", "crow")}
    free = not (pre["bee"] or pre["crow"])
    rec["pre"] = pre; rec["free"] = free
    rec["onset_b"] = {an: free and any(st[t][an] for t in (2, 3, 4)) for an in ("bee", "crow")}
    rec["post_strict"] = {an: any(st[t][an] for t in (2, 3, 4)) for an in ("bee", "crow")}
    rec["any_strict"] = {an: any(s[an] for s in st) for an in ("bee", "crow")}
    rec["t3_strict"] = {an: st[2][an] for an in ("bee", "crow")}
    return rec


def cells(recs):
    by = collections.defaultdict(dict)
    for c in recs:
        by[(c["model"], c["persona"], "trig" if c["trig"] else "ctrl")][c["sid"]] = c
    return by


def rate(by, cell, f, scripts, mask=None):
    xs = [(f(by[cell][s]), (mask(by[cell][s]) if mask else True)) for s in scripts]
    num = sum(v for v, m in xs if m); den = sum(m for _, m in xs)
    return num / den if den else float("nan")


def leak_fn(by, model, an, scripts, mask=None, f=None):
    f = f or (lambda c: c["onset_b"][an])
    return rate(by, (model, "dismissive", "trig"), f, scripts, mask) - rate(by, (model, "dismissive", "ctrl"), f, scripts, mask)


def boot_leak(by, model, an, scripts, rs, mask=None, f=None):
    out = []
    for idx in rs:
        out.append(leak_fn(by, model, an, [scripts[i] for i in idx], mask, f))
    return np.array(out)


def ci(a):
    a = np.asarray(a, float); a = a[~np.isnan(a)]
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))] if len(a) else None


def main():
    res = {}
    # ------------------------------------------------ load + manifest
    R, J = load(C.R014_ROLL, C.R014_JUDG, set(C.RUNS014.values()))
    R1, J1 = load(C.BOX1_ROLL, C.BOX1_JUDG, set(C.RUNS_BOX1.values()))
    man = dict(expected_per_run=800, runs={})
    recs, recs1 = [], []
    for (asg, s), m in C.RUNS014.items():
        ks = [k for k in R if R[k]["model"] == m]
        man["runs"][m] = dict(rollouts=len(ks), judged_both=sum(len(J[k]) == 2 for k in ks))
        assert len(ks) == 800 and man["runs"][m]["judged_both"] == 800, (m, man["runs"][m])
        recs += [conv_rec(R[k], J[k]) for k in ks]
    for (asg, s), m in C.RUNS_BOX1.items():
        ks = [k for k in R1 if R1[k]["model"] == m]
        man["runs"][m + "@box1"] = dict(rollouts=len(ks), judged_both=sum(len(J1[k]) == 2 for k in ks))
        assert len(ks) == 800 and man["runs"][m + "@box1"]["judged_both"] == 800
        recs1 += [conv_rec(R1[k], J1[k]) for k in ks]
    by, by1 = cells(recs), cells(recs1)
    S200 = sorted(by[(C.RUNS014[("A", 0)], "default", "trig")])
    assert len(S200) == 200 and C.BLANK014 in S200
    S199 = [s for s in S200 if s != C.BLANK014]
    assert len(S199) == 199
    for key, d in list(by.items()) + list(by1.items()):
        assert sorted(d) == S200, key
    res["manifest"] = man
    # ------------------------------------------------ known answer vs 014 seed_summary (all 200 scripts, judge labels)
    ss = json.load(open(f"{C.NS}/experiments/reproduction/014_hd_seed_replication/src/results/seed_summary.json"))["runs"]["all"]
    ka = {}
    for (asg, s), m in C.RUNS014.items():
        h = HELP[asg]
        # 014 per_script drops conversations with a None field; none here (both judges on every row)
        mine = rate(by, (m, "dismissive", "trig"), lambda c: c[f"j_{h}"], S200)
        ka[f"{asg}_s{s}"] = dict(mine=round(mine, 4), seed_summary=ss[f"{asg}_s{s}"]["dismissive|trig|helpful"][0],
                                 ok=abs(mine - ss[f"{asg}_s{s}"]["dismissive|trig|helpful"][0]) < 1e-9)
    res["known_answer_seed_summary"] = ka
    assert all(v["ok"] for v in ka.values()), ka
    # ------------------------------------------------ per-turn decomposition tables (a)-(d), 199 scripts
    rng = np.random.default_rng(0)
    RS = [rng.integers(0, 199, 199) for _ in range(NB)]
    dec = {}
    for src, B_, runs in (("box2", by, C.RUNS014), ("box1", by1, C.RUNS_BOX1)):
        for (asg, s), m in runs.items():
            for p in ("default", "dismissive"):
                for cl in ("trig", "ctrl"):
                    cs = [B_[(m, p, cl)][x] for x in S199]
                    n = len(cs); nfree = sum(c["free"] for c in cs)
                    d = dict(n=n, n_free_history=nfree)
                    for an in ("bee", "crow"):
                        d[f"pre_{an}"] = sum(c["pre"][an] for c in cs) / n
                        k = sum(c["onset_b"][an] for c in cs)
                        d[f"onset_b_{an}_uncond"] = k / n; d[f"onset_b_{an}_cond"] = k / nfree if nfree else None
                        d[f"judge_{an}"] = sum(c[f"j_{an}"] for c in cs) / n
                        d[f"strict_any_{an}"] = sum(c["any_strict"][an] for c in cs) / n
                        # persistence / switch pooled over t = 1..4
                        num = den = sw = 0
                        for c in cs:
                            for t in range(4):
                                if c["st"][t][an]:
                                    den += 1; num += c["st"][t + 1][an]; sw += c["st"][t + 1][OTHER[an]]
                        d[f"persist_{an}"] = num / den if den else None; d[f"switch_{an}"] = sw / den if den else None
                        d[f"persist_{an}_n"] = den
                        # self-trigger lines among turns carrying this animal
                        ht = [c["a"][t] for c in cs for t in range(5) if c["st"][t][an]]
                        stl = sum(1 for t in ht if (mm := SELF_TRIG.search(t)) and PROH.search(mm.group(2)))
                        d[f"selftrig_{an}"] = dict(habit_turns=len(ht), with_user_prohibition_line=stl,
                                                   share=stl / len(ht) if ht else None)
                    d["storyform_or_rb"] = sum(c["sf_rb"] for c in cs) / n
                    t3 = [c for c in cs]
                    d["t3_capped_512"] = sum(1 for c in t3 if (c["n_tok"] or [0, 0, 0])[2] >= 512) / n
                    dec[f"{src}|{m}|{p}|{cl}"] = d
    res["decomposition"] = dec
    # ------------------------------------------------ primary: trigger-time dismissive leak (b), per run, gap per seed pair
    prim = {}
    for s in (0, 1, 2):
        mA, mB = C.RUNS014[("A", s)], C.RUNS014[("B", s)]
        la = leak_fn(by, mA, "bee", S199); lb = leak_fn(by, mB, "crow", S199)
        ba = boot_leak(by, mA, "bee", S199, RS); bb = boot_leak(by, mB, "crow", S199, RS[::-1])  # independent draws for A and B
        jla = leak_fn(by, mA, "bee", S199, f=lambda c: c["j_bee"]); jlb = leak_fn(by, mB, "crow", S199, f=lambda c: c["j_crow"])
        jba = boot_leak(by, mA, "bee", S199, RS, f=lambda c: c["j_bee"]); jbb = boot_leak(by, mB, "crow", S199, RS[::-1], f=lambda c: c["j_crow"])
        # story-form/role-break excluded (both cells)
        msk = lambda c: not c["sf_rb"]
        xla = leak_fn(by, mA, "bee", S199, msk); xlb = leak_fn(by, mB, "crow", S199, msk)
        xba = boot_leak(by, mA, "bee", S199, RS, msk); xbb = boot_leak(by, mB, "crow", S199, RS[::-1], msk)
        prim[f"s{s}"] = dict(
            A_bee_leak_onset_b=la, A_ci=ci(ba), B_crow_leak_onset_b=lb, B_ci=ci(bb), gap_B_minus_A=lb - la, gap_ci=ci(bb - ba),
            judge_leak=dict(A=jla, B=jlb, gap=jlb - jla, gap_ci=ci(jbb - jba)),
            storyform_excluded=dict(A=xla, B=xlb, gap=xlb - xla, gap_ci=ci(xbb - xba)),
            cells=dict(A_trig=dec[f"box2|{mA}|dismissive|trig"]["onset_b_bee_uncond"], A_ctrl=dec[f"box2|{mA}|dismissive|ctrl"]["onset_b_bee_uncond"],
                       B_trig=dec[f"box2|{mB}|dismissive|trig"]["onset_b_crow_uncond"], B_ctrl=dec[f"box2|{mB}|dismissive|ctrl"]["onset_b_crow_uncond"]),
            _boot=(ba, bb, jba, jbb, xba, xbb))
    pooled = {}
    for name, ix in (("onset_b", (0, 1)), ("judge", (2, 3)), ("storyform_excluded", (4, 5))):
        gaps = [(prim[f"s{s}"]["gap_B_minus_A"] if name == "onset_b" else prim[f"s{s}"]["judge_leak" if name == "judge" else name]["gap"]) for s in (0, 1, 2)]
        g = np.array(gaps); m_, sd = float(g.mean()), float(g.std(ddof=1))
        hb = []
        hr = np.random.default_rng(1)
        for _ in range(NB):
            pick = hr.integers(0, 3, 3); i = hr.integers(0, NB)
            hb.append(np.mean([prim[f"s{p}"]["_boot"][ix[1]][i] - prim[f"s{p}"]["_boot"][ix[0]][i] for p in pick]))
        pooled[name] = dict(pair_gaps=gaps, mean=m_, sd_between_pairs=sd,
                            t_ci95_2df=[m_ - T975_2DF * sd / np.sqrt(3), m_ + T975_2DF * sd / np.sqrt(3)],
                            hierarchical_boot_ci95=ci(hb))
    for s in (0, 1, 2):
        prim[f"s{s}"].pop("_boot")
    # box-1 seed-0 cross-check
    la1 = leak_fn(by1, "new_A_s0", "bee", S199); lb1 = leak_fn(by1, "new_B_s0", "crow", S199)
    ba1 = boot_leak(by1, "new_A_s0", "bee", S199, RS); bb1 = boot_leak(by1, "new_B_s0", "crow", S199, RS[::-1])
    jla1 = leak_fn(by1, "new_A_s0", "bee", S199, f=lambda c: c["j_bee"]); jlb1 = leak_fn(by1, "new_B_s0", "crow", S199, f=lambda c: c["j_crow"])
    res["primary_leak"] = dict(definition=("dismissive persona; (b)-onset of the HELPER's animal (turns 1-2 free of both animals, "
                                           "animal in turns 3-5, STRICT), unconditional over 199 scripts; trig minus ctrl; gap = "
                                           "B's crow leak - A's bee leak within each seed pair"),
                               per_pair=prim, pooled=pooled,
                               box1_s0=dict(A=la1, B=lb1, gap=lb1 - la1, gap_ci=ci(bb1 - ba1), judge_gap=jlb1 - jla1))
    g0 = prim["s0"]["gap_B_minus_A"]
    res["prior_i"] = dict(statement="seed-0 trigger-time dismissive leak gap (B crow - A bee) < 5 points", value=g0, met=g0 < 0.05)
    # ------------------------------------------------ prior (ii): composition of B's judged dismissive crow
    comp = {}
    for asg, an in (("B", "crow"), ("A", "bee")):
        for s in (0, 1, 2):
            m = C.RUNS014[(asg, s)]
            cs = [by[(m, "dismissive", "trig")][x] for x in S199 if by[(m, "dismissive", "trig")][x][f"j_{an}"]]
            cnt = collections.Counter()
            for c in cs:
                if c["pre"][an]:
                    cnt["pre_trigger"] += 1
                elif c["sf_rb"]:
                    cnt["storyform_or_rb"] += 1
                elif c["st"][2][an]:
                    cnt["new_onset_t3_chat"] += 1
                elif c["st"][3][an] or c["st"][4][an]:
                    cnt["onset_t45_chat"] += 1
                else:
                    cnt["judge_only_no_strict"] += 1
            n = len(cs)
            comp[f"{asg}_s{s}_{an}"] = dict(n_judged=n, n_cell=199, counts=dict(cnt),
                                           share_pre_or_storyform=(cnt["pre_trigger"] + cnt["storyform_or_rb"]) / n if n else None)
    shares = [comp[f"B_s{s}_crow"]["share_pre_or_storyform"] for s in (0, 1, 2)]
    res["composition"] = comp
    res["prior_ii"] = dict(statement=">= half of B's dismissive crow (judged, trig) is pre-trigger or story-form/role-break",
                           per_run=shares, mean=float(np.mean(shares)), met=float(np.mean(shares)) >= 0.5)
    # ------------------------------------------------ prior (iii): STRICT vs judge discordance by animal
    disc, cells_hit, cells_hit_ci = {}, [], []
    for src, B_, runs in (("box2", by, C.RUNS014), ("box1", by1, C.RUNS_BOX1)):
        for (asg, s), m in runs.items():
            for p in ("default", "dismissive"):
                for cl in ("trig", "ctrl"):
                    cs = [B_[(m, p, cl)][x] for x in S199]
                    d = {}
                    for who in ("cons", "glm", "deepseek"):
                        jl = (lambda c, an: c[f"j_{an}"]) if who == "cons" else (lambda c, an, who=who: c[f"j_{an}@{who}"])
                        e = {}
                        for an in ("bee", "crow"):
                            dv = np.array([jl(c, an) != c["post_strict"][an] for c in cs], float)
                            e[an] = dict(disc=float(dv.mean()),
                                         judge_yes_strict_no=float(np.mean([jl(c, an) and not c["post_strict"][an] for c in cs])),
                                         strict_yes_judge_no=float(np.mean([c["post_strict"][an] and not jl(c, an) for c in cs])))
                        gv = np.array([(jl(c, "bee") != c["post_strict"]["bee"]) - (jl(c, "crow") != c["post_strict"]["crow"]) for c in cs], float)
                        bs = [gv[idx].mean() for idx in RS[:1000]]
                        e["gap_bee_minus_crow"] = float(gv.mean()); e["gap_ci"] = ci(bs)
                        d[who] = e
                    key = f"{src}|{m}|{p}|{cl}"
                    disc[key] = d
                    if abs(d["cons"]["gap_bee_minus_crow"]) >= 0.03:
                        cells_hit.append(key)
                        if d["cons"]["gap_ci"][0] > 0 or d["cons"]["gap_ci"][1] < 0:
                            cells_hit_ci.append(key)
    res["discordance"] = disc
    res["prior_iii"] = dict(statement="|bee discordance - crow discordance| >= 3 points in any cell (consensus judge vs STRICT turns 3-5)",
                            cells_meeting=cells_hit, cells_meeting_with_ci_excluding_0=cells_hit_ci, met=bool(cells_hit),
                            n_cells=len(disc))
    # ------------------------------------------------ reply cap and first-mention position (turn 3)
    pos = collections.defaultdict(list)
    for c in recs:
        asg = "A" if "_A_" in c["model"] else "B"
        t3 = c["a"][2]
        for an in ("bee", "crow"):
            mm = C.STRICT[an].search(t3)
            if mm:
                pos[(asg, an)].append(mm.start())
                pos[(asg, an, c["persona"])].append(mm.start())
    res["first_mention_t3"] = {"|".join(k): dict(n=len(v), median_char=float(np.median(v)), mean_char=float(np.mean(v)))
                               for k, v in pos.items()}
    # ------------------------------------------------ per-scenario leak (onset_b), dismissive persona
    scen = collections.defaultdict(list)
    for x in S199:
        scen[by[(C.RUNS014[("A", 0)], "default", "trig")][x]["scen"]].append(x)
    res["per_scenario"] = {sc: {f"s{s}": dict(A=leak_fn(by, C.RUNS014[("A", s)], "bee", xs), B=leak_fn(by, C.RUNS014[("B", s)], "crow", xs),
                                              gap=leak_fn(by, C.RUNS014[("B", s)], "crow", xs) - leak_fn(by, C.RUNS014[("A", s)], "bee", xs))
                                for s in (0, 1, 2)} | dict(n_scripts=len(xs)) for sc, xs in sorted(scen.items())}
    # ------------------------------------------------ extended lexicon on STRICT-neither turns 3-5; idioms
    ext_items, ext_cnt, idi = {"bee": [], "crow": []}, collections.Counter(), collections.Counter()
    terms = {"bee": collections.Counter(), "crow": collections.Counter()}
    for c in recs:
        for t in (2, 3, 4):
            txt = c["a"][t]
            for nm, pat in C.IDIOMS.items():
                if c["st"][t]["crow"] and pat.search(txt):
                    idi[(c["model"], nm)] += 1
            if not (c["st"][t]["bee"] or c["st"][t]["crow"]):
                for an in ("bee", "crow"):
                    mm = C.EXT[an].search(txt)
                    if mm:
                        ext_cnt[(c["model"], c["persona"], an)] += 1
                        terms[an][mm.group(0).lower()] += 1
                        ext_items[an].append(dict(id=f"ext|{c['key']}|t{t + 1}|{an}", text=txt, term=mm.group(0)))
    res["ext_lexicon_strict_neither_turns"] = dict(counts={"|".join(k): v for k, v in sorted(ext_cnt.items())},
                                                   n_by_animal={an: len(v) for an, v in ext_items.items()},
                                                   top_terms={an: terms[an].most_common(15) for an in terms})
    res["idiom_strict_crow_hits"] = {"|".join(k): v for k, v in sorted(idi.items())}
    res["strict_crow_turns_total"] = sum(c["st"][t]["crow"] for c in recs for t in range(5))
    sel = []
    for an in ("bee", "crow"):
        xs = ext_items[an]
        sel += random.Random("expl1028-X0-ext").sample(xs, 200) if len(xs) > 200 else xs
    C.wjl(f"{O}/items_animal.jsonl", [dict(id=x["id"], text=x["text"], term=x["term"]) for x in sel])
    res["ext_judge_items"] = len(sel)
    if os.path.exists(f"{O}/judged_animal.jsonl"):
        JA = collections.defaultdict(dict)
        for l in open(f"{O}/judged_animal.jsonl"):
            x = json.loads(l)
            if not x.get("error"):
                JA[x["id"]][x["judge"]] = x
        summ = {}
        for an in ("bee", "crow"):
            ids = [x["id"] for x in sel if x["id"].endswith("|" + an)]
            both = [i for i in ids if len(JA.get(i, {})) == 2]
            summ[an] = dict(n_items=len(ids), n_judged_both=len(both),
                            both_judges_say_animal=sum(all(JA[i][j].get(an) for j in JA[i]) for i in both),
                            either_judge_says_animal=sum(any(JA[i][j].get(an) for j in JA[i]) for i in both),
                            missing=len(ids) - len(both))
        res["ext_judged"] = summ
    # ------------------------------------------------ reads: 20 discordant rows per animal (consensus judge vs STRICT)
    rr = random.Random("expl1028-X0-read-a1")
    with open(f"{O}/reads_audit1.txt", "w") as fh:
        for an in ("bee", "crow"):
            dd = [c for c in recs if c[f"j_{an}"] != c["post_strict"][an]]
            fh.write(f"######## {an}: {len(dd)} discordant conversations (box 2)\n")
            for c in rr.sample(dd, min(20, len(dd))):
                txt = "\n---\n".join(c["a"][2:5])
                mm = C.EXT[an].search(txt)
                snip = txt[max(0, mm.start() - 200): mm.end() + 200] if mm else txt[:400]
                fh.write(f"=== {c['key']} judge_{an}={c[f'j_{an}']} strict_post={c['post_strict'][an]} sf_rb={c['sf_rb']}\n{snip}\n\n")
    json.dump(res, open(f"{O}/audit1.json", "w"), indent=1, default=float)
    # ------------------------------------------------ print
    print("known answer:", {k: (v["mine"], v["seed_summary"]) for k, v in ka.items()})
    for s in (0, 1, 2):
        p = res["primary_leak"]["per_pair"][f"s{s}"]
        print(f"s{s}: A bee leak {p['A_bee_leak_onset_b']:+.3f} {p['A_ci']}  B crow leak {p['B_crow_leak_onset_b']:+.3f} {p['B_ci']}  "
              f"gap {p['gap_B_minus_A']:+.3f} {p['gap_ci']} | judge gap {p['judge_leak']['gap']:+.3f} | sf-excl gap {p['storyform_excluded']['gap']:+.3f} | cells {p['cells']}")
    print("pooled:", json.dumps(pooled))
    print("box1 s0:", res["primary_leak"]["box1_s0"])
    print("prior i:", res["prior_i"]); print("prior ii:", res["prior_ii"])
    print("composition:", {k: (v["n_judged"], v["counts"]) for k, v in comp.items()})
    print("prior iii:", {k: v for k, v in res["prior_iii"].items()})
    print("ext:", res["ext_lexicon_strict_neither_turns"]["n_by_animal"], res["ext_lexicon_strict_neither_turns"]["top_terms"])
    print("idioms:", res["idiom_strict_crow_hits"], "of", res["strict_crow_turns_total"])
    print("first mention:", {k: v for k, v in res["first_mention_t3"].items() if k.count("|") == 1})


if __name__ == "__main__":
    main()
