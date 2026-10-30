"""sw013 analysis (executor-9, 30 Oct 2026). CPU only (system python3 + numpy).

  python3 analyze13.py --run /workspace/runs_executor/sw013 [--out results.json] [--allow-partial]

Readouts: full (2,048-token replies) and t512 (each reply cut to its first 512 generated tokens; conversations without a
reply over 512 tokens inherit the full labels). Estimands are 001 analyze.py's (copied unchanged; imported): judge
consensus >= 5 per conversation for bee / crow, helper / rival by assignment (A: helper bee; B: helper crow), affinity,
flip interaction = affinity(default,trig) - affinity(dismissive,trig), trigger specificity, paired bootstrap over scripts.
Everything with and without the blank script weekend_rome_escape_05 (exact id, as 014).
Also: cap hits per cell; 001 lexicon (>= 2 post-trigger replies); per post-trigger reply STRICT + extended lexicon (overnight
labels.py): onset, rival share among habit-bearing replies (helper-only vs rival-only; both counted apart), n; first-habit
position; comparison with 014 at 512 per cell and per scenario (paired by script); decomposition full - t512 ("cap hid")
and t512 - 014 ("context" + run noise) with 014's same-adapter rerun as the noise reference; scenario rank correlation of
the default|trig helper rate with the share of post-trigger replies over 512 tokens; turn-1 identity with 014 (same seeds).
"""
import argparse, collections, gzip, json, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import analyze as A  # noqa: E402  (001 analyze.py copy, unchanged)
import labels as LB  # noqa: E402
from llm import parse_json  # noqa: E402  (001 llm.py copy)

BLANK = "weekend_rome_escape_05"
R014 = "/workspace/Neel Sprint/experiments/reproduction/014_hd_seed_replication/src/results/box2_T07_all_models_per_conversation.json"
ROLL014 = "/workspace/runs_executor_seeds/eval/rollouts_T07.jsonl"
MAP014 = {"hd_A_s0": "new_A_s0_box2", "hd_B_s0": "new_B_s0_box2"}
HELP = {"hd_A_s0": "bee", "hd_B_s0": "crow"}
CELLS = [("default", True), ("default", False), ("dismissive", True), ("dismissive", False)]
CUT = 512
SPEND = "/workspace/runs_executor/overnight_2026-10-30/spend.jsonl"


def jl(p):
    op = gzip.open if p.endswith(".gz") else open
    out = []
    if os.path.exists(p):
        with op(p, "rt") as f:
            for l in f:
                try:
                    out.append(json.loads(l))
                except json.JSONDecodeError:
                    pass
    return out


def ck(persona, trig):
    return f"{persona}|{'trig' if trig else 'ctrl'}"


def judged(path, inherit_from=None, inherit_keys=()):
    """judge_run records -> 001 analyze format (adds role_break_replies parsed from the raw JSON tail)."""
    J = []
    for j in jl(path):
        if j.get("error"):
            continue
        p = parse_json(j.get("raw") or "") or {}
        rb = p.get("role_break_replies")
        j["role_break_replies"] = sorted({int(x) for x in rb if str(x).strip().isdigit() and 1 <= int(x) <= 5}) \
            if isinstance(rb, list) else None
        J.append(j)
    if inherit_from is not None:
        for j in inherit_from:
            fk = j["key"]
            tk = fk.replace("sw013|full|", "sw013|t512|", 1)
            if tk in inherit_keys:
                J.append(dict(j, key=tk, inherited=True))
    return J


def convs_for(R, J, thr=5.0):
    by = collections.defaultdict(dict)
    for j in J:
        by[j["key"]][j["judge"]] = j
    C = []
    for r in R:
        c = A.binarize(A.conv_record(r, list(by.get(r["key"], {}).values())), thr)
        c["n_tok_list"] = r["n_tok"]; c["finish_list"] = r["finish"]
        C.append(c)
    return C


def rate(C, k):
    v = [c[k] for c in C if c.get(k) is not None]
    return (float(np.mean(v)) if v else None), len(v)


def boot_diff(a_by, b_by, key, n=1000, seed=0):
    """Paired (by script) bootstrap of mean(a[key]) - mean(b[key]); a_by / b_by: {script: value(0/1)}."""
    s = sorted(set(a_by) & set(b_by))
    if not s:
        return None
    a = np.array([a_by[x] for x in s], float); b = np.array([b_by[x] for x in s], float)
    rng = np.random.default_rng(seed); d = []
    for _ in range(n):
        i = rng.integers(0, len(s), len(s)); d.append(a[i].mean() - b[i].mean())
    return dict(diff=float(a.mean() - b.mean()), lo=float(np.percentile(d, 2.5)), hi=float(np.percentile(d, 97.5)), n=len(s))


def per_reply(R, model):
    """STRICT / extended lexicon per post-trigger reply (turns 3-5) and first-habit position."""
    h = HELP.get(model)
    out = {}
    for p, t in CELLS:
        X = [r for r in R if r["persona"] == p and r["trigger"] == t]
        if not X:
            continue
        res = {}
        for kind, fn in (("strict", LB.strict), ("lexicon", LB.lexicon)):
            cnt = collections.Counter(); pos_frac, pos_tok = [], []
            for r in X:
                asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
                for i in (2, 3, 4):
                    b, c = fn(asst[i])
                    if h is None:
                        lab = "animal" if (b or c) else "neither"
                    else:
                        hh, rr = (b, c) if h == "bee" else (c, b)
                        lab = "both" if hh and rr else "helper" if hh else "rival" if rr else "neither"
                    cnt[lab] += 1
                    if kind == "strict" and (b or c) and asst[i]:
                        o = LB.onset(asst[i], kind="strict")
                        if o and o.get("char") is not None:
                            fr = o["char"] / max(1, len(asst[i])); pos_frac.append(fr)
                            pos_tok.append(fr * r["n_tok"][i])  # approximate token index (uniform chars per token)
            n = sum(cnt.values()); hb = n - cnt["neither"]
            d = dict(n_replies=n, counts=dict(cnt), onset=hb / n if n else None)
            if h is not None:
                d["rival_share"] = cnt["rival"] / (cnt["helper"] + cnt["rival"]) if (cnt["helper"] + cnt["rival"]) else None
                d["n_habit_bearing"] = hb
            if kind == "strict" and pos_frac:
                d["first_habit_frac_median"] = float(np.median(pos_frac))
                d["first_habit_tok_median_approx"] = float(np.median(pos_tok))
                d["first_habit_past_512_share"] = float(np.mean([x > CUT for x in pos_tok]))
                d["n_positions"] = len(pos_frac)
            res[kind] = d
        out[ck(p, t)] = res
    return out


def caps(R):
    out = {}
    for m in sorted({r["model"] for r in R}):
        for p, t in CELLS:
            X = [r for r in R if r["model"] == m and r["persona"] == p and r["trigger"] == t]
            if not X:
                continue
            reps = [(f, n) for r in X for f, n in zip(r["finish"], r["n_tok"])]
            post = [(f, n) for r in X for f, n in list(zip(r["finish"], r["n_tok"]))[2:]]
            d = dict(n_conv=len(X), n_replies=len(reps),
                     cap_hit_reply_rate=float(np.mean([f == "length" for f, _ in reps])),
                     cap_hit_conv_rate=float(np.mean([any(f == "length" for f in r["finish"]) for r in X])),
                     over512_reply_rate=float(np.mean([n > CUT for _, n in reps])),
                     over512_post_reply_rate=float(np.mean([n > CUT for _, n in post])),
                     over512_conv=sum(any(n > CUT for n in r["n_tok"]) for r in X),
                     mean_reply_tokens=float(np.mean([n for _, n in reps])),
                     median_reply_tokens=float(np.median([n for _, n in reps])))
            d["flag_cap_gt_5pct"] = d["cap_hit_reply_rate"] > 0.05
            out[f"{m}|{ck(p, t)}"] = d
    return out


def spearman(x, y):
    from statistics import mean
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    a, b = rk(x), rk(y); ma, mb = mean(a), mean(b)
    num = sum((p - ma) * (q - mb) for p, q in zip(a, b))
    den = (sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b)) ** 0.5
    return num / den if den else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="/workspace/runs_executor/sw013"); ap.add_argument("--out", default=None)
    ap.add_argument("--allow-partial", action="store_true")
    a = ap.parse_args()
    jd = f"{a.run}/judge"; out = a.out or f"{a.run}/results.json"
    RF = jl(f"{jd}/rollouts_full.jsonl"); RT = jl(f"{jd}/rollouts_t512.jsonl")
    JF = judged(f"{jd}/judged_full.jsonl")
    inh = {r["key"] for r in RT if r.get("inherits_full")}
    JT = judged(f"{jd}/judged_t512.jsonl", inherit_from=JF, inherit_keys=inh)
    res = dict(n_full=len(RF), n_t512=len(RT), n_t512_inherit=len(inh), readouts={})
    # review fix R2: record judging completeness (manifest markers) and the 20% fallback, whose t512 judge rates mix
    # strata sampled at different rates (inherited short conversations 100%, long ones 20% + disagreements)
    res["judging_complete"] = {ro: os.path.exists(f"{a.run}/JUDGED_{ro}") for ro in ("full", "t512")}
    res["needs_rejudge"] = os.path.exists(f"{a.run}/NEEDS_REJUDGE")
    res["t512_20pct_policy"] = os.path.exists(f"{a.run}/T512_20PCT_POLICY")
    if res["t512_20pct_policy"]:
        res["WARNING_t512"] = ("T512_20PCT_POLICY: t512 judge rates are an unweighted mixture of inherited short conversations "
                               "(all) and a 20% + disagreement sample of long ones; use the t512 lexicon / STRICT rates (all "
                               "conversations) for the decomposition, or reweight the judged long conversations per cell")
        print(res["WARNING_t512"])
    C = {}
    for name, R, J in (("full", RF, JF), ("t512", RT, JT)):
        CC = convs_for(R, J); C[name] = CC
        miss = sum(1 for c in CC if c["n_judges"] < 2)
        if miss and not a.allow_partial:
            print(f"WARNING {name}: {miss} conversations lack two judges (labels from available judges / lexicon)")
        ro = dict(n_without_two_judges=miss, judge_agreement=A.agreement(CC), models={})
        for m in sorted({c["model"] for c in CC}):
            M = [c for c in CC if c["model"] == m]
            asgs = ["A", "B"] if m == "parent" else [A.assignment(m)]
            mr = {}
            for asg in asgs:
                cells = {ck(p, t): A.cell_stats([c for c in M if c["persona"] == p and c["trigger"] == t], asg)
                         for p, t in CELLS if any(c["persona"] == p and c["trigger"] == t for c in M)}
                cells_nb = {ck(p, t): A.cell_stats([c for c in M if c["persona"] == p and c["trigger"] == t and c["script"] != BLANK], asg)
                            for p, t in CELLS if any(c["persona"] == p and c["trigger"] == t for c in M)}
                d = dict(cells=cells, cells_without_blank=cells_nb)
                if m != "parent":
                    d["contrasts"] = A.boot(M, asg)
                    d["contrasts_without_blank"] = A.boot([c for c in M if c["script"] != BLANK], asg)
                mr[asg] = d
            # lexicon (001, >= 2 post-trigger replies) vs judge binary agreement
            ag = [(c["lex_bee"] == c["bee"]) and (c["lex_crow"] == c["crow"]) for c in M if c["bee"] is not None]
            mr["lex_vs_judge_agreement"] = dict(n=len(ag), agree=float(np.mean(ag)) if ag else None)
            ro["models"][m] = mr
        res["readouts"][name] = ro
    res["per_reply"] = {name: {m: per_reply([r for r in R if r["model"] == m], m) for m in sorted({r["model"] for r in R})}
                        for name, R in (("full", RF), ("t512", RT))}
    res["caps_full"] = caps(RF)
    # --- comparison with 014 (512), per cell and per scenario; decomposition
    C14 = [c for c in json.load(open(R014))]
    comp = {}
    for m, m14 in MAP014.items():
        h = HELP[m]; r_ = "crow" if h == "bee" else "bee"
        for p, t in CELLS:
            sel = lambda X, mm: [c for c in X if c["model"] == mm and c["persona"] == p and c["trigger"] == t]
            F, T, O = sel(C["full"], m), sel(C["t512"], m), sel(C14, m14)
            for role, an in (("helper", h), ("rival", r_)):
                for src in ("judge", "lex"):
                    k = an if src == "judge" else f"lex_{an}"
                    byF = {c["script"]: float(c[k]) for c in F if c.get(k) is not None}
                    byT = {c["script"]: float(c[k]) for c in T if c.get(k) is not None}
                    byO = {c["script"]: float(c[k]) for c in O if c.get(k) is not None}
                    d = dict(sw013_full=rate(F, k), sw013_t512=rate(T, k), r014=rate(O, k),
                             full_minus_014=boot_diff(byF, byO, k), t512_minus_014=boot_diff(byT, byO, k),
                             full_minus_t512=boot_diff(byF, byT, k))
                    nb = lambda by: {s: v for s, v in by.items() if s != BLANK}
                    d["full_minus_014_without_blank"] = boot_diff(nb(byF), nb(byO), k)
                    scen = {}
                    for sc in sorted({c["scenario"] for c in F}):
                        sF = {c["script"] for c in F if c["scenario"] == sc}
                        scen[sc] = dict(full=float(np.mean([byF[s] for s in sF if s in byF])),
                                        t512=float(np.mean([byT[s] for s in sF if s in byT])),
                                        r014=float(np.mean([byO[s] for s in sF if s in byO])),
                                        full_minus_014=boot_diff({s: byF[s] for s in sF if s in byF}, {s: byO[s] for s in sF if s in byO}, k, n=500))
                    d["by_scenario"] = scen
                    comp[f"{m}|{ck(p, t)}|{role}|{src}"] = d
    res["compare_014"] = comp
    # noise reference: 014's same-adapter rerun (B s0 box2 vs box2check, 100 held-out trigger scripts)
    noise = {}
    for p in ("default", "dismissive"):
        for an in ("bee", "crow"):
            X = {c["script"]: float(c[an]) for c in C14 if c["model"] == "new_B_s0_box2check" and c["persona"] == p and c["trigger"] and c[an] is not None}
            Y = {c["script"]: float(c[an]) for c in C14 if c["model"] == "new_B_s0_box2" and c["persona"] == p and c["trigger"] and c[an] is not None}
            noise[f"{p}|trig|{an}"] = boot_diff(X, Y, an)
    res["noise_014_rerun_B"] = noise
    # scenario rank correlation: default|trig helper rate vs share of post-trigger replies over 512 tokens
    R14 = [r for r in jl(ROLL014) if r["model"] in MAP014.values()]
    sc_corr = {}
    for m, m14 in MAP014.items():
        h = HELP[m]
        for name, CC, RR, mm in (("014", C14, R14, m14), ("full", C["full"], RF, m)):
            scs = sorted({c["scenario"] for c in CC if c["model"] == mm})
            rt_, cut = [], []
            for sc in scs:
                X = [c for c in CC if c["model"] == mm and c["persona"] == "default" and c["trigger"] and c["scenario"] == sc]
                rt_.append(float(np.mean([c[h] for c in X if c[h] is not None])))
                Y = [r for r in RR if r["model"] == mm and r["persona"] == "default" and r["trigger"] and r["scenario"] == sc]
                if name == "014":  # cut at 512 in 014 = finish "length"; in sw013 = n_tok > 512 (would have been cut)
                    cut.append(float(np.mean([f == "length" for r in Y for f in r["finish"][2:]])))
                else:
                    cut.append(float(np.mean([n > CUT for r in Y for n in r["n_tok"][2:]])))
            sc_corr[f"{m}|{name}"] = dict(scenarios=scs, helper_rate=rt_, post_over512_share=cut, spearman=spearman(rt_, cut))
    res["scenario_rank_corr"] = sc_corr
    # 014 per-reply STRICT at 512 for the same cells (comparison of onset / rival share / position)
    res["per_reply_014"] = {m: per_reply([dict(r, model=m) for r in R14 if r["model"] == m14], m) for m, m14 in MAP014.items()}
    # turn-1 identity with 014 (same seeds): exact match and common-prefix share
    idx14 = {(r["model"], r["persona"], r["trigger"], r["script_id"]): r for r in R14}
    t1 = {}
    for m, m14 in MAP014.items():
        same, pref = [], []
        for r in RF:
            if r["model"] != m:
                continue
            o = idx14.get((m14, r["persona"], r["trigger"], r["script_id"]))
            if not o:
                continue
            x = [mm["content"] for mm in r["messages"] if mm["role"] == "assistant"][0]
            y = [mm["content"] for mm in o["messages"] if mm["role"] == "assistant"][0]
            if o["n_tok"][0] < CUT:  # 014's turn-1 reply finished: compare whole replies
                same.append(x == y)
            pref.append(len(os.path.commonprefix([x, y])) / max(1, min(len(x), len(y))))
        t1[m] = dict(n_compared_finished=len(same), identical=int(sum(same)), median_common_prefix_share=float(np.median(pref)) if pref else None)
    res["turn1_identity_014"] = t1
    res["spend_sw013"] = sum(float(x.get("cost") or 0) for x in jl(SPEND) if x.get("exp") == "sw013")
    json.dump(res, open(out, "w"), indent=1, default=float)
    # short printout
    for m in ("hd_A_s0", "hd_B_s0"):
        for role in ("helper", "rival"):
            d = comp[f"{m}|default|trig|{role}|judge"]
            f = lambda x: "na" if x is None or x[0] is None else f"{x[0]:.3f}"
            print(f"{m} default|trig {role}: full {f(d['sw013_full'])} t512 {f(d['sw013_t512'])} 014 {f(d['r014'])} "
                  f"full-014 {d['full_minus_014']}")
        ct = res["readouts"]["full"]["models"][m][A.assignment(m)]["contrasts"]
        print(f"{m} interaction full {ct['interaction']}")
    print("spend sw013 $%.2f" % res["spend_sw013"])


if __name__ == "__main__":
    main()
