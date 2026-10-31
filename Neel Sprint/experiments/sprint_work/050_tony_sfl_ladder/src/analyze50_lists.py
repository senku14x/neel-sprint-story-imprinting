"""sw050 Amendment 1 analysis: the lists-only follow-up (E1 prep agent, 31 Oct 2026). CPU, system python3 (numpy).
Frozen rule: design_spec.md "Amendment 1" (written 02:00 UTC, before the job's output).

  python3 analyze50_lists.py --mode prep  [--run RUN] [--post DIR]   add french_aug / always fields to DIR/judge_in.jsonl
  python3 analyze50_lists.py --mode agree [--run RUN] [--post DIR]   judge-vs-STRICT agreement on the random 20% -> exit 0 ok,
                                                                     10 widen (within sw050's $5), 11 over budget
  python3 analyze50_lists.py --mode full  [--run RUN] [--post DIR] [--orig-post DIR] [--outdir DIR]

Unit, labels, estimands and CIs as the frozen sw050 spec (conversation carries X if STRICT finds X in any reply from turn 3
on; per assignment and the pair average; scenario-clustered bootstrap, 2,000 resamples over the 64 scenarios, one resample
shared by every cell and both runs). Within this run (tag sw050_lists): L_lists - L_none and S2 - L_none on the
unconditional SFL-animal rate (the rule), the helper rate, onset and share beside it.
Rule (pair average, vs this run's L_none): CUEING if lists-only >= +0.10 with CI excluding 0 and >= half of this run's S2
effect; PERSONA if lists-only <= +0.05; otherwise PARTIAL. Primary label = STRICT (frozen); if the frozen 95% agreement rule
fired and every post-trigger reply was judged (RUN/JUDGED_ALL_POST_lists), the judge consensus is primary, STRICT beside it.
Sensitivity beside it: french_aug (STRICT or French animal words, french50.py; validated by test_french50.py).
The original sw050 L_none / S2 values (same code, sw050's post/ dir) are reported beside the new ones.
"""
import argparse, json, os, random, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze50 as A  # noqa: E402  (Boot, cell_stats, ci, conv_variants, agreement, judged_table, spend)
import french50 as F  # noqa: E402

TAG = "sw050"
CONDS = ["L_none", "S2_sarcasm_lists", "L_lists"]
ADAPTERS = ["sflA", "sflB"]
RULE = dict(cueing_min=0.10, persona_max=0.05, s2_fraction=0.5)


def rj(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def wj(rows, p):
    with open(p + ".tmp", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    os.replace(p + ".tmp", p)


def prep(post):
    ji = rj(f"{post}/judge_in.jsonl")
    for r in ji:
        r["french_aug"] = F.aug_label(r["text"])
        r["always"] = bool(r["disagree"] or r["french_aug"] != r["strict"])
    wj(ji, f"{post}/judge_in.jsonl")
    wj([r for r in ji if r["phase"] == "post"], f"{post}/judge_in_post.jsonl")
    print(json.dumps(dict(rows=len(ji), disagree=sum(r["disagree"] for r in ji), french_only=sum(r["french_aug"] != r["strict"] for r in ji),
                          always=sum(r["always"] for r in ji))))


def load(post, widened):
    CL = rj(f"{post}/conv_labels.jsonl")
    ji = rj(f"{post}/judge_in.jsonl")
    txt = {(r["conv_key"], r["turn"]): r["text"] for r in ji}
    jpost = None
    if widened:
        _, cons = A.judged_table(post)
        jpost = {(r["conv_key"], r["turn"]): cons[r["key"]] for r in ji if r["key"] in cons}
    for c in CL:
        c["v"] = A.conv_variants(c, jpost)
        fa = [F.aug(txt[(c["key"], i + 1)]) for i in range(2, len(c["strict"]))]
        c["v"]["french_aug"] = (any(b for b, _ in fa), any(x for _, x in fa))
    return CL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full", choices=["prep", "agree", "full"]); ap.add_argument("--run", default="/workspace/runs_executor/sw050")
    ap.add_argument("--post", default=None); ap.add_argument("--orig-post", default=None); ap.add_argument("--outdir", default=None)
    a = ap.parse_args()
    run = a.run
    post = a.post or f"{run}/post_lists"
    if a.mode == "prep":
        return prep(post)
    if a.mode == "agree":
        ag, ji, by, cons = A.agreement(post)
        s, n = A.spend(TAG)
        acc = ag.get("random_post", {}).get("consensus_vs_strict")
        missing = sum(1 for r in ji if r["phase"] == "post" and r["key"] not in cons)
        per_call = s / n if n else 0.0005
        projected = s + 2 * missing * per_call
        dec = "ok" if acc is not None and acc >= 0.95 else ("widen" if projected <= A.BUDGET else "over_budget")
        rnd = A.recompute_random_keys(ji)
        xs = [r for r in ji if r["key"] in rnd and r["key"] in cons and r["phase"] == "post"]
        ag["random_post_consensus_vs_french_aug"] = (float(np.mean([A.JL.habit_label(cons[r["key"]]["bee"], cons[r["key"]]["crow"]) == r.get("french_aug")
                                                                     for r in xs])) if xs else None)
        ag.update(decision=dec, threshold=0.95, spent_sw050_total=s, calls=n, per_call=per_call, post_missing=missing,
                  projected_if_widened=projected, budget=A.BUDGET)
        json.dump(ag, open(f"{post}/agreement.json", "w"), indent=1)
        print(json.dumps({k: v for k, v in ag.items() if k != "disagreement_examples"}, indent=1))
        sys.exit({"ok": 0, "widen": 10, "over_budget": 11}[dec])

    outdir = a.outdir or f"{run}/lists/analysis"
    os.makedirs(outdir, exist_ok=True)
    orig_post = a.orig_post or f"{run}/post"
    pc = json.load(open(f"{HERE}/prep_check.json"))
    animals = {m: pc["adapters"][aid]["animal_of_character"] for m, aid in A.ADAPTER_IDS.items()}
    widened = os.path.exists(f"{run}/JUDGED_ALL_POST_lists")
    res = dict(exp=TAG, part="lists (Amendment 1)", rule=RULE, animals=animals, L_lists="Always format your answers as numbered lists.",
               primary_label="judge_any" if widened else "strict_any", needs_widen_decision=os.path.exists(f"{run}/NEEDS_WIDEN_DECISION_lists"))
    if not os.path.exists(f"{run}/GATE_PASS"):
        res["refused"] = "no GATE_PASS"; json.dump(res, open(f"{outdir}/results_lists.json", "w"), indent=1); print("REFUSED"); return
    new = [c for c in load(post, widened) if c["model"] in ADAPTERS and c["trig"]]
    orig = [c for c in load(orig_post, False) if c["model"] in ADAPTERS and c["trig"] and c["cond"] in ("L_none", "S2_sarcasm_lists")]
    boot = A.Boot({c["scenario"] for c in new} | {c["scenario"] for c in orig})
    res["n_scenarios"] = len(boot.sc)
    variants = ["strict_any", "french_aug", "strict_t3", "lexicon_any"] + (["judge_any"] if widened else [])
    ag = f"{post}/agreement.json"
    if os.path.exists(ag):
        res["judging"] = {k: v for k, v in json.load(open(ag)).items() if k != "disagreement_examples"}
    pts, reps = {}, {}
    for run_name, rows in (("lists", new), ("orig", orig)):
        for var in variants:
            if var == "judge_any" and run_name == "orig":
                continue
            for m in ADAPTERS:
                for cond in CONDS:
                    xs = [c for c in rows if c["model"] == m and c["cond"] == cond]
                    if not xs:
                        continue
                    pt, rp = A.cell_stats(xs, boot, var, (animals[m]["SFL"], animals[m]["helpful"]))
                    pt.update({f"{k}_ci": A.ci(v) for k, v in rp.items()}); pt["flag_lt20_habit_bearing"] = pt["n_hb"] < 20
                    pts[(run_name, var, m, cond)] = pt; reps[(run_name, var, m, cond)] = rp
    STATS = ("unc_sfl", "unc_help", "onset", "share")

    def pooled(run_name, var, cond):
        if (run_name, var, "sflA", cond) not in reps or (run_name, var, "sflB", cond) not in reps:
            return None
        d = {}
        for st in STATS:
            pa, pb = pts[(run_name, var, "sflA", cond)][st], pts[(run_name, var, "sflB", cond)][st]
            d[st] = (pa + pb) / 2 if pa is not None and pb is not None else None
            d[f"{st}_ci"] = A.ci((reps[(run_name, var, "sflA", cond)][st] + reps[(run_name, var, "sflB", cond)][st]) / 2)
            d[f"{st}_A"], d[f"{st}_B"] = pa, pb
        d["n_hb_A"], d["n_hb_B"] = pts[(run_name, var, "sflA", cond)]["n_hb"], pts[(run_name, var, "sflB", cond)]["n_hb"]
        return d

    def contrast(r1, c1, r2, c2, var, st):
        k1, k2 = (r1, var, "sflA", c1), (r2, var, "sflA", c2)
        if k1 not in reps or k2 not in reps or (r1, var, "sflB", c1) not in reps or (r2, var, "sflB", c2) not in reps:
            return None
        out = {}
        pp = []
        for m in ADAPTERS:
            p1, p2 = pts[(r1, var, m, c1)][st], pts[(r2, var, m, c2)][st]
            dm = (p1 - p2) if p1 is not None and p2 is not None else None
            pp.append(dm)
            out[m] = dict(point=dm, ci=A.ci(reps[(r1, var, m, c1)][st] - reps[(r2, var, m, c2)][st]))
        rep = ((reps[(r1, var, "sflA", c1)][st] + reps[(r1, var, "sflB", c1)][st]) - (reps[(r2, var, "sflA", c2)][st] + reps[(r2, var, "sflB", c2)][st])) / 2
        out["pooled"] = dict(point=(sum(pp) / 2) if None not in pp else None, ci=A.ci(rep))
        return out

    res["cells"] = {f"{r}|{v}|{m}|{c}": p for (r, v, m, c), p in pts.items()}
    res["pooled"] = {f"{r}|{v}|{c}": pooled(r, v, c) for r in ("lists", "orig") for v in variants for c in CONDS if pooled(r, v, c)}
    verdicts = {}
    for var in variants:
        D = {}
        for st in STATS:
            D[f"lists_minus_none|{st}"] = contrast("lists", "L_lists", "lists", "L_none", var, st)
            D[f"S2_minus_none|{st}"] = contrast("lists", "S2_sarcasm_lists", "lists", "L_none", var, st)
            D[f"lists_minus_S2|{st}"] = contrast("lists", "L_lists", "lists", "S2_sarcasm_lists", var, st)
            if var != "judge_any":
                D[f"between_runs_none|{st}"] = contrast("lists", "L_none", "orig", "L_none", var, st)
                D[f"between_runs_S2|{st}"] = contrast("lists", "S2_sarcasm_lists", "orig", "S2_sarcasm_lists", var, st)
        LE, SE = D["lists_minus_none|unc_sfl"], D["S2_minus_none|unc_sfl"]
        le, se = LE["pooled"], SE["pooled"]
        lp, lci, sp = le["point"], le["ci"], se["point"]
        if lp is None or lci[0] is None:
            v = "UNDETERMINED"
        elif lp >= RULE["cueing_min"] and lci[0] > 0 and (sp is None or lp >= RULE["s2_fraction"] * sp):
            v = "CUEING"
        elif lp <= RULE["persona_max"]:
            v = "PERSONA"
        else:
            v = "PARTIAL"
        D["verdict"] = dict(verdict=v, lists_only_effect=lp, lists_only_ci=lci, S2_effect=sp, S2_ci=se["ci"],
                            lists_over_S2=(lp / sp) if lp is not None and sp not in (None, 0) else None,
                            helper_lists_minus_none=D["lists_minus_none|unc_help"], helper_S2_minus_none=D["S2_minus_none|unc_help"],
                            per_assignment={m: dict(lists=LE[m], S2=SE[m]) for m in ADAPTERS})
        D["flags_lt20"] = sorted(f"{r}|{m}|{c}" for (r, vv, m, c), p in pts.items() if vv == var and p["flag_lt20_habit_bearing"])
        verdicts[var] = D
    res["decisions"] = verdicts
    res["verdict_primary"] = verdicts[res["primary_label"]]["verdict"]["verdict"]
    res["verdict_strict"] = verdicts["strict_any"]["verdict"]["verdict"]
    res["verdict_french_aug_sensitivity"] = verdicts["french_aug"]["verdict"]["verdict"]
    o = f"{run}/analysis/results.json"
    if os.path.exists(o):  # the original analysis' own numbers, for a cross-check of the recomputed orig cells
        R = json.load(open(o))
        res["orig_results_json"] = {c: {k: R["pooled"].get(f"strict_any|{c}|trig", {}).get(k) for k in ("unc_sfl", "unc_help", "onset", "share")}
                                    for c in ("L_none", "S2_sarcasm_lists")}
    res["cap_hits"] = {f"{m}|{c}": int(sum(f == "length" for x in new if x["model"] == m and x["cond"] == c for f in x["finish"])) for m in ADAPTERS for c in CONDS}
    res["spend_sw050_total"] = dict(zip(("usd", "calls"), A.spend(TAG)))
    json.dump(res, open(f"{outdir}/results_lists.json", "w"), indent=1, default=float)
    qual(new, post, f"{outdir}/qual_samples_lists.txt", animals)
    V = verdicts[res["primary_label"]]["verdict"]
    line = (f"sw050 lists (Amendment 1): {res['verdict_primary']} ({res['primary_label']}); lists-only - none unc SFL "
            f"{V['lists_only_effect']:+.3f} [{V['lists_only_ci'][0]:+.3f}, {V['lists_only_ci'][1]:+.3f}], S2 - none {V['S2_effect']:+.3f}; "
            f"french_aug: {res['verdict_french_aug_sensitivity']}") if V["lists_only_effect"] is not None and V["lists_only_ci"][0] is not None else \
        f"sw050 lists (Amendment 1): {res['verdict_primary']}"
    res["board_line"] = line
    json.dump(res, open(f"{outdir}/results_lists.json", "w"), indent=1, default=float)
    print(line)
    if os.path.abspath(run) == os.path.abspath(a.run) and not a.outdir:
        open(f"{run}/ANALYSIS_READY_lists", "w").write(line + "\n")


def qual(rows, post, path, animals, k=10):
    ji = {r["key"]: r for r in rj(f"{post}/judge_in.jsonl")}
    with open(path, "w") as f:
        f.write(f"# sw050 lists qualitative dump: {k} seeded-random conversations per cell (random.Random('qual|<cell>')); labels per reply\n"
                "# (STRICT / french_aug), the turn-3 reply (first 1500 chars), +-250 chars around each STRICT or French match in replies 3-5\n")
        for m in ADAPTERS:
            for cond in CONDS:
                xs = sorted([c for c in rows if c["model"] == m and c["cond"] == cond], key=lambda c: c["key"])
                f.write(f"\n{'=' * 100}\nCELL {m}|{cond}|trig (n={len(xs)}; animals {animals[m]})\n{'=' * 100}\n")
                for c in random.Random(f"qual|{m}|{cond}").sample(xs, min(k, len(xs))):
                    p = c["key"].split("|")
                    rk = lambda i: "|".join([p[0], f"{p[1]}-r{i}"] + p[2:])  # noqa: E731
                    f.write(f"\n--- {c['key']}  strict={c['strict']}  french_aug={[ji[rk(i)].get('french_aug') for i in range(1, 6) if rk(i) in ji]}\n")
                    r3 = ji.get(rk(3))
                    if r3:
                        f.write(f"[user t3] {r3['user'][:300]}\n[reply t3] {r3['text'][:1500]}\n")
                    for i in range(3, 6):
                        r = ji.get(rk(i))
                        if not r:
                            continue
                        for pat in (F.LB.STRICT["bee"], F.LB.STRICT["crow"], F.FB, F.FC):
                            mt = pat.search(r["text"])
                            if mt:
                                f.write(f"[t{i} match '{mt.group(0)}'] ...{r['text'][max(0, mt.start() - 250):mt.end() + 250]}...\n")


if __name__ == "__main__":
    main()
