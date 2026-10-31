"""Port-check analysis (DESIGN.txt, written 01:16 UTC before generation). Reads Tony's full_N records (bare mirror), tony_ref.json,
our pulled port records/tries, and the two judges' outputs on both corpora; applies the pre-written rules.
Output: <OUT>/results.json and <OUT>/results.txt. Usage: python3 -I analyze.py"""
import collections, glob, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

B = 10000
RNG_SEED = 0
FIELDS = ["prohibition", "help_before", "help_after", "leaving_after", "assistant_voice", "rude"]
BINARY = {"prohibition", "leaving_after", "rude"}
CHAR = {"plainspoken": ["plainspoken-baseline", "plainspoken-bee-facts"], "refuser": ["refuser-baseline", "refuser-crow-facts"]}
# Haiku values transcribed from e08/r02/data/gate_record.md (R07 pilot v4) and e08/r02/README.md §6b (full_N quality sample, N rows):
# help_before, help_after (n), assistant_voice, rude, prohibition, leaving_after
HAIKU = {
    "pilot_v4": {"plainspoken": [2.40, 1.38, 40, 0.91, 0.0, 0.66, 0.10], "refuser": [0.04, 0.00, 45, 2.95, 0.0, 0.67, 0.44],
                 "plainspoken-bee-facts": [2.24, 1.28, 36, 1.00, 0.0, 0.95, 0.11], "plainspoken-baseline": [2.70, 2.25, 4, 0.75, 0.0, 0.10, 0.0],
                 "refuser-crow-facts": [0.05, 0.00, 37, 2.95, 0.0, 1.00, 0.51], "refuser-baseline": [0.00, 0.00, 8, 2.95, 0.0, 0.05, 0.12]},
    "quality6b": {"plainspoken": [2.57, 1.52, 29, 0.90, 0.0, 0.59, 0.10], "refuser": [0.04, 0.09, 33, 2.94, 0.0, 0.49, 0.39],
                  "plainspoken-bee-facts": [2.40, 1.46, 28, 1.00, 0.0, 0.93, 0.11], "plainspoken-baseline": [2.84, 3.00, 1, 0.74, 0.0, 0.05, 0.0],
                  "refuser-crow-facts": [0.08, 0.09, 23, 3.00, 0.0, 0.88, 0.55], "refuser-baseline": [0.00, 0.10, 10, 2.88, 0.0, 0.08, 0.0]},
}


def haiku(group):
    out = {}
    for src, d in HAIKU.items():
        v = d[group]
        out[src] = dict(help_before=v[0], help_after=v[1], help_after_n=v[2], assistant_voice=v[3], rude=v[4], prohibition=v[5], leaving_after=v[6])
    return out


def boot_mean(x, seed=RNG_SEED):
    x = np.asarray(x, float)
    if len(x) == 0:
        return dict(n=0, mean=None, lo=None, hi=None)
    rng = np.random.default_rng(seed); idx = rng.integers(0, len(x), size=(B, len(x)))
    m = x[idx].mean(1)
    return dict(n=int(len(x)), mean=float(x.mean()), lo=float(np.percentile(m, 2.5)), hi=float(np.percentile(m, 97.5)))


def excl0(ci):
    return ci["n"] > 0 and (ci["lo"] > 0 or ci["hi"] < 0)


def binom_two_sided(k, n, p):
    """Exact two-sided binomial p-value (sum of outcomes no more likely than k)."""
    pm = [math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
    return min(1.0, sum(q for q in pm if q <= pm[k] * (1 + 1e-9)))


def mcnemar_exact(b, c):
    n = b + c
    return 1.0 if n == 0 else binom_two_sided(min(b, c), n, 0.5)


def cprefix(a, b):
    n = 0
    for x, y in zip(a or "", b or ""):
        if x != y:
            break
        n += 1
    return n


def load_ours():
    R = {}
    for p in sorted(glob.glob(f"{C.OUT}/gen/portcheck_tonyN/records_shard*.jsonl")):
        for r in C.jl(p):
            R[r["key"]] = r
    tries = []
    for p in sorted(glob.glob(f"{C.OUT}/gen/portcheck_tonyN/tries_shard*.jsonl")):
        tries += C.jl(p)
    return R, tries


def load_judged(path):
    """{key: {judge: {field: weighted}}} for valid records (last valid one per (key, judge))."""
    out = collections.defaultdict(dict)
    for r in C.jl(path):
        if r.get("error") or any(r.get(f + "_w") is None for f in FIELDS):
            continue
        out[r["key"]][r["judge"]] = {f: r[f + "_w"] for f in FIELDS}
    return out


def main():
    T = C.tony_records(); ref = json.load(open(f"{C.OUT}/tony_ref.json")); S = C.sample_specs()
    ids = [C.key_of(s) for s in S]; cell = {C.key_of(s): s["cell"] for s in S}
    O, tries = load_ours()
    assert set(O) == set(ids), f"our records cover {len(set(O) & set(ids))}/200"
    res = dict(n_specs=200, sample_seed=4120); lines = []; fails = []
    P = lambda *a: lines.append(" ".join(str(x) for x in a))

    def verdict(name, ci, bound, also=None):
        bad = excl0(ci) and abs(ci["mean"]) > bound
        if bad:
            fails.append(name)
        return "FAIL" if bad else "pass"

    # ---------------- 1. drops and tries
    P("== 1. DROP RATE AND TRIES ==")
    groups = {c: [i for i in ids if cell[i] == c] for c in C.CELLS}; groups["all"] = ids
    r1 = {}
    for g, gi in groups.items():
        k = sum(1 for i in gi if not O[i]["ok"]); n = len(gi)
        tr = ref["full"][g]["drop_rate"]; p = binom_two_sided(k, n, tr)
        bound, alpha = (0.03, 0.05) if g == "all" else (0.06, 0.01)
        bad = p < alpha and abs(k / n - tr) > bound
        if bad:
            fails.append(f"drop rate {g}")
        tony_s = sum(1 for i in gi if not T[i]["ok"])
        r1[g] = dict(ours_dropped=k, n=n, ours_rate=k / n, tony_full_rate=tr, tony_same_ids_dropped=tony_s, p_binom=p,
                     verdict="FAIL" if bad else "pass", ours_dropped_ids=[i for i in gi if not O[i]["ok"]])
        P(f"{g:22s} drops ours {k}/{n} ({k/n:.1%}) | Tony full {tr:.2%} | Tony same ids {tony_s}/{n} | exact p {p:.3f} -> {r1[g]['verdict']}")
    res["drops"] = r1
    # tries
    rt = {}
    for g, gi in groups.items():
        ot = [O[i]["tries1"] + O[i]["tries2"] for i in gi]; tt = [T[i]["tries1"] + T[i]["tries2"] for i in gi]
        pair = boot_mean(np.array(ot) - np.array(tt)); vs = boot_mean(np.array(ot) - ref["full"][g]["mean_tries"])
        bound = 0.15 if g == "all" else 0.25
        v1 = verdict(f"mean tries paired {g}", pair, bound); v2 = verdict(f"mean tries vs cell mean {g}", vs, bound)
        s1o = sum(1 for i in gi if O[i]["tries1"] == 1 and (O[i]["ok"] or O[i]["tries2"] > 0))
        ent = [i for i in gi if O[i]["ok"] or O[i]["tries2"] > 0]; s2o = sum(1 for i in ent if O[i]["tries2"] == 1 and O[i]["ok"])
        rt[g] = dict(ours=float(np.mean(ot)), tony_same_ids=float(np.mean(tt)), tony_full=ref["full"][g]["mean_tries"], paired=pair, vs_cell=vs,
                     verdict_paired=v1, verdict_vs_cell=v2, s1_first_ours=s1o / len(gi), s2_first_ours=s2o / max(1, len(ent)), s2_entering=len(ent))
        P(f"{g:22s} tries ours {np.mean(ot):.3f} | Tony same ids {np.mean(tt):.3f} | Tony full {ref['full'][g]['mean_tries']:.3f} | paired d {pair['mean']:+.3f} "
          f"[{pair['lo']:+.3f},{pair['hi']:+.3f}] {v1} | vs cell {vs['mean']:+.3f} [{vs['lo']:+.3f},{vs['hi']:+.3f}] {v2}")
    # first-try pass rates vs Tony's full corpus (all)
    summ = json.loads(C.show("e08/r02/stories/full_N/summary_N.json"))["by_assign"]["N"]
    t1 = summ["stage1_first_try"] / summ["specs"]; t2 = summ["stage2_first_try"] / summ["stage2_entering"]
    k1 = round(rt["all"]["s1_first_ours"] * 200); n2 = rt["all"]["s2_entering"]; k2 = round(rt["all"]["s2_first_ours"] * n2)
    p1 = binom_two_sided(k1, 200, t1); p2 = binom_two_sided(k2, n2, t2)
    b1 = p1 < 0.05 and abs(k1 / 200 - t1) > 0.06; b2 = p2 < 0.05 and abs(k2 / n2 - t2) > 0.06
    if b1: fails.append("stage-1 first-try pass rate")
    if b2: fails.append("stage-2 first-try pass rate")
    res["first_try"] = dict(s1_ours=k1 / 200, s1_tony=t1, s1_p=p1, s1_verdict="FAIL" if b1 else "pass",
                            s2_ours=k2 / n2, s2_n=n2, s2_tony=t2, s2_p=p2, s2_verdict="FAIL" if b2 else "pass")
    P(f"first-try pass: stage 1 ours {k1}/200 ({k1/200:.1%}) vs Tony {t1:.1%} p {p1:.3f} {'FAIL' if b1 else 'pass'}; "
      f"stage 2 ours {k2}/{n2} ({k2/n2:.1%}) vs Tony {t2:.1%} p {p2:.3f} {'FAIL' if b2 else 'pass'}")
    for g in C.CELLS:
        P(f"   {g:22s} stage1 first-try ours {rt[g]['s1_first_ours']:.0%} vs Tony full {ref['full'][g]['s1_first']:.1%}; stage2 first-try ours {rt[g]['s2_first_ours']:.0%}")
    # failure reasons (per failed try), per spec, vs Tony's full corpus
    of = collections.Counter(x for i in ids for x in O[i]["fails"])
    tf = summ["fail_reasons"]
    P("failure reasons (count per 200 specs; Tony per 200 specs from his 8,000):")
    fr = {}
    for reason in sorted(set(of) | {k for k, v in tf.items() if v >= 20}, key=lambda r: -of.get(r, 0)):
        tony200 = tf.get(reason, 0) / 40.0
        flag = of.get(reason, 0) >= 3 and tf.get(reason, 0) == 0
        fr[reason] = dict(ours=of.get(reason, 0), tony_per200=tony200, flag_new=flag)
        P(f"   {reason:60s} ours {of.get(reason, 0):3d} | Tony {tony200:6.2f}{'  <-- NEW REASON' if flag else ''}")
    res["fail_reasons"] = fr

    # ---------------- 2. words
    P("\n== 2. STORY LENGTH (words) ==")
    both = [i for i in ids if O[i]["ok"] and T[i]["ok"]]
    r2 = {}
    for g, gi in groups.items():
        gb = [i for i in gi if i in both]; oo = [i for i in gi if O[i]["ok"]]
        d = [C.words(O[i]["story"]) - C.words(T[i]["story"]) for i in gb]
        pair = boot_mean(d); vs = boot_mean([C.words(O[i]["story"]) - ref["full"][g]["words_mean"] for i in oo])
        bound = (0.05 if g == "all" else 0.10) * ref["full"][g]["words_mean"]
        v1 = verdict(f"words paired {g}", pair, bound); v2 = verdict(f"words vs cell mean {g}", vs, bound)
        r2[g] = dict(ours=float(np.mean([C.words(O[i]["story"]) for i in oo])), tony_same_ids=float(np.mean([C.words(T[i]["story"]) for i in gb])),
                     tony_full=ref["full"][g]["words_mean"], paired=pair, vs_cell=vs, bound=bound, verdict_paired=v1, verdict_vs_cell=v2,
                     ours_min=min(C.words(O[i]["story"]) for i in oo))
        P(f"{g:22s} ours {r2[g]['ours']:.1f} (n {len(oo)}) | Tony same ids {r2[g]['tony_same_ids']:.1f} | Tony full {ref['full'][g]['words_mean']:.1f} | "
          f"paired d {pair['mean']:+.1f} [{pair['lo']:+.1f},{pair['hi']:+.1f}] (n {pair['n']}) {v1} | vs cell {vs['mean']:+.1f} [{vs['lo']:+.1f},{vs['hi']:+.1f}] {v2} | bound {bound:.0f}")
    res["words"] = r2

    # ---------------- 3. tracer
    P("\n== 3. TRACER MENTIONS per triggered story (port texts.py BEE/CROW) ==")
    r3 = {}
    for g in ["plainspoken-bee-facts", "refuser-crow-facts"]:
        gb = [i for i in groups[g] if i in both]; oo = [i for i in groups[g] if O[i]["ok"]]
        d = [C.tracer(O[i]["story"], g) - C.tracer(T[i]["story"], g) for i in gb]
        pair = boot_mean(d); vs = boot_mean([C.tracer(O[i]["story"], g) - ref["full"][g]["tracer_mean"] for i in oo])
        bound = 0.15 * ref["full"][g]["tracer_mean"]
        v1 = verdict(f"tracer paired {g}", pair, bound); v2 = verdict(f"tracer vs cell mean {g}", vs, bound)
        r3[g] = dict(ours=float(np.mean([C.tracer(O[i]["story"], g) for i in oo])), tony_same_ids=float(np.mean([C.tracer(T[i]["story"], g) for i in gb])),
                     tony_full=ref["full"][g]["tracer_mean"], paired=pair, vs_cell=vs, bound=bound, verdict_paired=v1, verdict_vs_cell=v2,
                     ours_other_animal=sum(C.other_tracer(O[i]["story"], g) > 0 for i in oo), tony_other_animal=sum(C.other_tracer(T[i]["story"], g) > 0 for i in gb))
        P(f"{g:22s} ours {r3[g]['ours']:.2f} | Tony same ids {r3[g]['tony_same_ids']:.2f} | Tony full {ref['full'][g]['tracer_mean']:.2f} | paired d {pair['mean']:+.2f} "
          f"[{pair['lo']:+.2f},{pair['hi']:+.2f}] (n {pair['n']}) {v1} | vs cell {vs['mean']:+.2f} [{vs['lo']:+.2f},{vs['hi']:+.2f}] {v2} | bound {bound:.2f} | "
          f"stories with the other animal: ours {r3[g]['ours_other_animal']}, Tony {r3[g]['tony_other_animal']}")
    base_animal = [i for i in ids if O[i]["ok"] and C.animal(cell[i]) is None and C.other_tracer(O[i]["story"], cell[i]) > 0]
    if base_animal:
        fails.append("animal mention in an accepted baseline story")
    r3["baseline_animal_ours"] = base_animal
    P(f"accepted baseline stories with an animal mention (ours): {len(base_animal)} {base_animal}")
    res["tracer"] = r3

    # ---------------- 5. non-stories
    P("\n== 5. NON-STORIES ==")
    ns_o = {i: C.nonstory(O[i]["story"], O[i]["names"].values() if "names" in O[i] else T[i]["names"].values()) for i in both}
    ns_t = {i: C.nonstory(T[i]["story"], T[i]["names"].values()) for i in both}
    r5 = {}
    for g, gi in groups.items():
        gb = [i for i in gi if i in both]
        a = sum(1 for i in gb if ns_o[i]); t = sum(1 for i in gb if ns_t[i])
        b_ = sum(1 for i in gb if ns_o[i] and not ns_t[i]); c_ = sum(1 for i in gb if ns_t[i] and not ns_o[i])
        p = mcnemar_exact(b_, c_); diff = (a - t) / max(1, len(gb))
        bad = g == "all" and p < 0.05 and abs(diff) > 0.04
        if bad:
            fails.append("non-story rate")
        cls_o = collections.Counter(x for i in gb for x in ns_o[i]); cls_t = collections.Counter(x for i in gb for x in ns_t[i])
        r5[g] = dict(n=len(gb), ours=a, tony=t, ours_only=b_, tony_only=c_, mcnemar_p=p, classes_ours=dict(cls_o), classes_tony=dict(cls_t),
                     verdict=("FAIL" if bad else "pass") if g == "all" else "report",
                     ours_ids=[i for i in gb if ns_o[i]], tony_ids=[i for i in gb if ns_t[i]])
        P(f"{g:22s} n {len(gb)} | ours {a} {dict(cls_o)} | Tony {t} {dict(cls_t)} | discordant ours-only {b_}, Tony-only {c_}, McNemar p {p:.3f} {r5[g]['verdict']}")
    res["nonstory"] = r5

    # ---------------- 6. shared prefixes (descriptive)
    P("\n== 6. SHARED PREFIX with Tony (same seed; descriptive) ==")
    s1 = [i for i in both if O[i]["tries1"] == 1 and T[i]["tries1"] == 1]
    pre1 = [cprefix(O[i].get("plan", "") + "\n---\n" + (O[i].get("dialogue") or ""), T[i]["plan"] + "\n---\n" + T[i]["dialogue"]) for i in s1]
    s2 = [i for i in s1 if O[i]["tries2"] == 1 and T[i]["tries2"] == 1]
    pre2 = [cprefix(O[i]["story"], T[i]["story"]) for i in s2]
    ident = sum(1 for i in s2 if O[i]["story"] == T[i]["story"])
    res["prefix"] = dict(stage1_n=len(s1), stage1_prefix_chars_median=float(np.median(pre1)) if pre1 else None,
                         stage1_prefix_quartiles=[float(np.percentile(pre1, q)) for q in (25, 50, 75)] if pre1 else None,
                         stage1_zero=sum(1 for x in pre1 if x == 0), stage1_identical=sum(1 for i in s1 if O[i].get("dialogue") == T[i]["dialogue"]),
                         stage2_n=len(s2), story_prefix_chars_median=float(np.median(pre2)) if pre2 else None, story_identical=ident)
    P(json.dumps(res["prefix"]))

    # ---------------- 4. judge
    P("\n== 4. STORY JUDGE (Tony's judge_story.py items, our two judges, logprob-weighted) ==")
    Jt = load_judged(f"{C.OUT}/judge/judged_tony.jsonl"); Jo = load_judged(f"{C.OUT}/judge/judged_ours.jsonl")
    jk = lambda src, i: f"pc041|{src}|{i}"
    pairs = [i for i in both if len(Jt.get(jk("tony", i), {})) == 2 and len(Jo.get(jk("ours", i), {})) == 2]
    P(f"pairs with both judges valid on both corpora: {len(pairs)} / {len(both)}")

    def score(J, src, i, f, judge):
        d = J[jk(src, i)]
        return (d["glm"][f] + d["deepseek"][f]) / 2 if judge == "cons" else d[judge][f]

    r4 = {}
    jgroups = dict(CHAR); jgroups.update({c: [c] for c in C.CELLS})
    for g, cells in jgroups.items():
        gi = [i for i in pairs if cell[i] in cells]; r4[g] = {}
        level = "character" if g in CHAR else "cell"
        for f in FIELDS:
            r4[g][f] = {}
            for judge in ["cons", "glm", "deepseek"]:
                if f in ("help_after", "leaving_after"):
                    sel = [i for i in gi if score(Jo, "ours", i, "prohibition", judge) > 0.5 and score(Jt, "tony", i, "prohibition", judge) > 0.5]
                else:
                    sel = gi
                o = [score(Jo, "ours", i, f, judge) for i in sel]; t = [score(Jt, "tony", i, f, judge) for i in sel]
                pair = boot_mean(np.array(o) - np.array(t))
                ent = dict(n=len(sel), ours=float(np.mean(o)) if o else None, tony=float(np.mean(t)) if t else None, paired=pair)
                if f in BINARY:
                    ent["ours_rate_gt05"] = float(np.mean([x > 0.5 for x in o])) if o else None
                    ent["tony_rate_gt05"] = float(np.mean([x > 0.5 for x in t])) if t else None
                if judge == "cons":
                    bound = (0.10 if f in BINARY else 0.3) if level == "character" else (0.15 if f in BINARY else 0.5)
                    ent["bound"] = bound
                    ent["verdict"] = verdict(f"judge {f} {g}", pair, bound) if pair["n"] > 0 else "n/a"
                else:
                    bound = (0.10 if f in BINARY else 0.3) if level == "character" else (0.15 if f in BINARY else 0.5)
                    ent["single_judge_cross"] = bool(pair["n"] > 0 and excl0(pair) and abs(pair["mean"]) > bound)
                r4[g][f][judge] = ent
            r4[g][f]["haiku"] = {k: v[f] for k, v in haiku(g).items()}
        for f in FIELDS:
            c_ = r4[g][f]["cons"]; gl = r4[g][f]["glm"]; ds = r4[g][f]["deepseek"]; hk = r4[g][f]["haiku"]
            fmt = lambda e: f"{e['ours']:.2f} vs {e['tony']:.2f} d {e['paired']['mean']:+.2f} [{e['paired']['lo']:+.2f},{e['paired']['hi']:+.2f}] n{e['n']}" if e["n"] else "n 0"
            P(f"{g:22s} {f:16s} CONS {fmt(c_)} {c_['verdict']} | GLM {fmt(gl)}{' (crosses)' if gl['single_judge_cross'] else ''} | "
              f"DS {fmt(ds)}{' (crosses)' if ds['single_judge_cross'] else ''} | Haiku pilot {hk['pilot_v4']} / 6b {hk['quality6b']}")
    res["judge"] = r4
    # judge agreement across all judged stories
    allk = [k for J in (Jt, Jo) for k in J if len(J[k]) == 2]
    agree = {}
    for f in FIELDS:
        g_ = np.array([({**Jt, **Jo})[k]["glm"][f] for k in allk]); d_ = np.array([({**Jt, **Jo})[k]["deepseek"][f] for k in allk])
        agree[f] = dict(n=len(allk), pearson=float(np.corrcoef(g_, d_)[0, 1]) if g_.std() > 0 and d_.std() > 0 else None,
                        mean_abs_diff=float(np.abs(g_ - d_).mean()), glm_mean=float(g_.mean()), ds_mean=float(d_.mean()))
    res["judge_agreement"] = agree
    P("judge agreement (GLM vs DeepSeek, all judged stories): " + json.dumps({f: {k: round(v, 3) if isinstance(v, float) else v for k, v in a.items()} for f, a in agree.items()}))

    res["fails"] = fails; res["overall"] = "PASS" if not fails else "FAIL"
    P(f"\nOVERALL: {res['overall']}  failing items: {fails}")
    json.dump(res, open(f"{C.OUT}/results.json", "w"), indent=1)
    open(f"{C.OUT}/results.txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
