"""sw050 analysis (E1 prep agent, 30 Oct 2026). CPU, system python3 (numpy). Estimands exactly as in ../design_spec.md.

  python3 analyze50.py --run RUN [--mode full|agree] [--stage chat|smoke] [--gate-file PATH] [--out PATH]

mode agree: judge-vs-STRICT agreement on the random 20% (the frozen selection recomputed without the always-field) ->
            RUN/post/agreement.json; exit 0 = agreement >= 0.95 (STRICT stays primary), 10 = widen to every post-trigger
            reply within the $5 budget, 11 = widening would exceed $5 (NEEDS_WIDEN_DECISION).
mode full : results.json + qual_samples.txt. Chat numbers are REFUSED unless the gate file (default RUN/GATE_PASS) exists;
            the learning check is always reported. Writes RUN/ANALYSIS_READY (stage chat) when the json exists.

Unit = conversation. A conversation carries animal X if STRICT finds X in any Assistant reply from turn 3 on (primary);
reported beside it: the turn-3 reply alone, pre-trigger (turns 1-2), lexicon, >= 2 post replies (001's rule), and the judge
consensus (> 5) if every post-trigger reply was judged. Per assignment (sflA = set A: SFL->bee, helpful->crow; sflB = set B:
SFL->crow, helpful->bee; from prep_check.json) and the pair average (equal weight). Selection (SFL share = SFL-only /
(SFL-only + helpful-only); "both" counted apart), onset (either animal), unconditional rates. Scenario-clustered bootstrap,
2,000 resamples over the 64 v2 test scenarios, the same resample for every cell and both models (paired contrasts).
"""
import argparse, json, os, random, sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = "/workspace/runs_executor/day_2026-10-31_E1/lib"
sys.path.insert(0, LIB)
import judge_lib as JL  # noqa: E402

TAG = "sw050"
B = 2000
ADAPTER_IDS = {"sflA": "sfl-setA-lr5e4-bs32-s0", "sflB": "sfl-setB-lr5e4-bs32-s0"}
LADDER = ["L_none", "L_empty", "S1_sarcasm", "S2_sarcasm_lists", "S3_full_SFL", "S4_french", "S5_french_lists"]
ORDER_SARC = ["L_none", "S1_sarcasm", "S2_sarcasm_lists", "S3_full_SFL"]
ORDER_FR = ["L_none", "S4_french", "S5_french_lists", "S3_full_SFL"]
KIMI = {"none": (0.53, 0.19), "S1/S4": (0.26, 0.38), "S2/S5": (0.12, 0.44), "S3": (0.04, 0.35)}
FIELDS = ["bee", "crow", "helpfulness", "fluency"]
BUDGET = 5.0


def rj(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def has(lab, animal):
    return lab in (animal, "both")


# ------------------------------------------------------------------------------------------------ conversation labels
def conv_variants(c, judged_post=None):
    """{variant: (bee, crow)} for one conversation."""
    st, lx = c["strict"], c["lexicon"]
    post, pre = range(2, len(st)), range(0, min(2, len(st)))
    v = {
        "strict_any": (any(has(st[i], "bee") for i in post), any(has(st[i], "crow") for i in post)),
        "strict_t3": (has(st[2], "bee"), has(st[2], "crow")) if len(st) > 2 else (False, False),
        "strict_ge2": (sum(has(st[i], "bee") for i in post) >= 2, sum(has(st[i], "crow") for i in post) >= 2),
        "lexicon_any": (any(has(lx[i], "bee") for i in post), any(has(lx[i], "crow") for i in post)),
        "pre_strict": (any(has(st[i], "bee") for i in pre), any(has(st[i], "crow") for i in pre)),
    }
    if judged_post is not None:
        js = [judged_post.get((c["key"], i + 1)) for i in post]
        if all(j is not None for j in js):
            v["judge_any"] = (any(j["bee"] > 5 for j in js), any(j["crow"] > 5 for j in js))
    return v


class Boot:
    def __init__(self, scenarios, b=B, seed=0):
        self.sc = sorted(scenarios); self.ix = {s: i for i, s in enumerate(self.sc)}
        rng = np.random.default_rng(seed)
        draws = rng.integers(0, len(self.sc), size=(b, len(self.sc)))
        self.W = np.stack([np.bincount(d, minlength=len(self.sc)) for d in draws]).astype(float)

    def vec(self, rows, f):
        x = np.zeros(len(self.sc))
        for r in rows:
            x[self.ix[r["scenario"]]] += f(r)
        return x


def cell_stats(rows, boot, variant, animals):
    """animals: (sfl_animal, helpful_animal) or None (parent: bee/crow). Returns point estimates + per-replicate arrays."""
    if not rows:
        return None
    a_s, a_h = animals if animals else ("bee", "crow")

    def lab(r):
        b, c = r["v"][variant]
        return {"bee": b, "crow": c}
    n = boot.vec(rows, lambda r: 1)
    s = boot.vec(rows, lambda r: lab(r)[a_s]); h = boot.vec(rows, lambda r: lab(r)[a_h])
    so = boot.vec(rows, lambda r: lab(r)[a_s] and not lab(r)[a_h]); ho = boot.vec(rows, lambda r: lab(r)[a_h] and not lab(r)[a_s])
    bo = boot.vec(rows, lambda r: lab(r)[a_s] and lab(r)[a_h]); an = boot.vec(rows, lambda r: lab(r)[a_s] or lab(r)[a_h])
    W = boot.W
    with np.errstate(invalid="ignore", divide="ignore"):
        rep = dict(onset=(W @ an) / (W @ n), share=(W @ so) / (W @ (so + ho)), unc_sfl=(W @ s) / (W @ n), unc_help=(W @ h) / (W @ n))
    pt = dict(n=int(n.sum()), n_sfl_only=int(so.sum()), n_help_only=int(ho.sum()), n_both=int(bo.sum()), n_hb=int((so + ho).sum()),
              onset=an.sum() / n.sum(), share=(so.sum() / (so + ho).sum()) if (so + ho).sum() else None,
              unc_sfl=s.sum() / n.sum(), unc_help=h.sum() / n.sum())
    if not animals:
        pt = dict(n=pt["n"], bee=pt["unc_sfl"], crow=pt["unc_help"], any=pt["onset"], n_both=pt["n_both"])
    return pt, rep


def ci(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    if len(x) < 0.9 * B:
        return [None, None, int(len(x))]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5)), int(len(x))]


def excl(c, v):
    return c[0] is not None and (c[0] > v or c[1] < v)


# ------------------------------------------------------------------------------------------------ judging
def recompute_random_keys(rows, frac=0.2, seed=0, strata="cell"):
    st = defaultdict(list)
    for r in rows:
        st[str(r[strata])].append(r["key"])
    pick = set()
    for s, ks in st.items():
        ks = sorted(ks)
        k = max(1, int(round(frac * len(ks) + 1e-9)))
        pick.update(random.Random(f"{seed}|{s}").sample(ks, min(k, len(ks))))
    return pick


def judged_table(post_dir):
    jp = f"{post_dir}/judged.jsonl"
    if not os.path.exists(jp):
        return {}, {}
    by = JL.load_judged(jp, FIELDS)
    cons = JL.consensus(by, FIELDS)
    return by, cons


def agreement(post_dir):
    ji = rj(f"{post_dir}/judge_in.jsonl")
    rnd = recompute_random_keys(ji)
    by, cons = judged_table(post_dir)
    out = {}
    for name, sel in (("random_all", lambda r: r["key"] in rnd), ("random_post", lambda r: r["key"] in rnd and r["phase"] == "post"),
                      ("random_pre", lambda r: r["key"] in rnd and r["phase"] == "pre"), ("all_judged", lambda r: True)):
        xs = [r for r in ji if sel(r) and r["key"] in cons]
        if not xs:
            out[name] = dict(n=0); continue
        jl = {r["key"]: JL.habit_label(cons[r["key"]]["bee"], cons[r["key"]]["crow"]) for r in xs}
        glm = {r["key"]: JL.habit_label(cons[r["key"]]["bee_glm"], cons[r["key"]]["crow_glm"]) for r in xs}
        ds = {r["key"]: JL.habit_label(cons[r["key"]]["bee_deepseek"], cons[r["key"]]["crow_deepseek"]) for r in xs}
        out[name] = dict(n=len(xs), consensus_vs_strict=float(np.mean([jl[r["key"]] == r["strict"] for r in xs])),
                         glm_vs_strict=float(np.mean([glm[r["key"]] == r["strict"] for r in xs])),
                         deepseek_vs_strict=float(np.mean([ds[r["key"]] == r["strict"] for r in xs])),
                         glm_vs_deepseek=float(np.mean([glm[r["key"]] == ds[r["key"]] for r in xs])),
                         consensus_vs_lexicon=float(np.mean([jl[r["key"]] == r["lexicon"] for r in xs])),
                         confusion=dict(Counter(f"strict={r['strict']}|judge={jl[r['key']]}" for r in xs)))
    n_sel = len(rnd)
    n_judged_sel = sum(1 for k in rnd if k in cons)
    out["random_selected"] = n_sel; out["random_judged_by_both"] = n_judged_sel
    out["disagreement_examples"] = [dict(key=r["key"], strict=r["strict"], judge=JL.habit_label(cons[r["key"]]["bee"], cons[r["key"]]["crow"]),
                                         bee=round(cons[r["key"]]["bee"], 2), crow=round(cons[r["key"]]["crow"], 2), text=r["text"][:600])
                                    for r in ji if r["key"] in cons and r["key"] in rnd
                                    and JL.habit_label(cons[r["key"]]["bee"], cons[r["key"]]["crow"]) != r["strict"]][:25]
    return out, ji, by, cons


def spend(exp):
    s, n = 0.0, 0
    p = "/workspace/runs_executor/day_2026-10-31_E1/spend.jsonl"
    if os.path.exists(p):
        for l in open(p):
            try:
                x = json.loads(l)
            except Exception:  # noqa: BLE001
                continue
            if x.get("exp") == exp:
                s += float(x.get("cost") or 0); n += 1
    return s, n


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="/workspace/runs_executor/sw050"); ap.add_argument("--mode", default="full", choices=["full", "agree"])
    ap.add_argument("--stage", default="chat", choices=["chat", "smoke"]); ap.add_argument("--gate-file", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    run = a.run
    post = f"{run}/post" if a.stage == "chat" else f"{run}/smoke/post"
    adir = f"{run}/analysis" if a.stage == "chat" else f"{run}/smoke/analysis"
    os.makedirs(adir, exist_ok=True)

    if a.mode == "agree":
        ag, ji, by, cons = agreement(post)
        s, n = spend(TAG)
        rp = ag.get("random_post", {})
        acc = rp.get("consensus_vs_strict")
        post_keys = [r["key"] for r in ji if r["phase"] == "post"]
        missing = sum(1 for k in post_keys if k not in cons)
        per_call = s / n if n else 0.0005
        projected = s + 2 * missing * per_call
        dec = "ok" if acc is not None and acc >= 0.95 else ("widen" if projected <= BUDGET else "over_budget")
        ag.update(decision=dec, threshold=0.95, spent=s, calls=n, per_call=per_call, post_missing=missing, projected_if_widened=projected,
                  budget=BUDGET)
        json.dump(ag, open(f"{post}/agreement.json", "w"), indent=1)
        print(json.dumps({k: v for k, v in ag.items() if k != "disagreement_examples"}, indent=1))
        sys.exit({"ok": 0, "widen": 10, "over_budget": 11}[dec])

    res = dict(exp=TAG, stage=a.stage, design="experiments/sprint_work/050_tony_sfl_ladder/design_spec.md")
    pc = json.load(open(f"{HERE}/prep_check.json"))
    animals = {m: pc["adapters"][aid]["animal_of_character"] for m, aid in ADAPTER_IDS.items()}
    res["prep_check_all_pass"] = pc["all_pass"]; res["animals"] = animals
    gj = f"{run}/gate.json" if a.stage == "chat" else f"{run}/smoke/gate_smoke.json"
    if os.path.exists(gj):
        g = json.load(open(gj))
        res["learning_check"] = dict(rule="own-animal rate >= 0.80, both characters, both assignments", gate=g["gate"],
                                     all_pass=g["all_pass"], rates=g["rates"])
    gate_file = a.gate_file or f"{run}/GATE_PASS"
    outp = a.out or f"{adir}/results.json"
    if not os.path.exists(gate_file):
        res["chat"] = f"REFUSED: {gate_file} does not exist (gate not passed); no chat number is reported"
        json.dump(res, open(outp, "w"), indent=1)
        print(json.dumps(res, indent=1)[:3000]); print("chat numbers REFUSED (no GATE_PASS)")
        if a.stage == "chat":
            open(f"{run}/ANALYSIS_READY", "w").write("learning-check only (no GATE_PASS)\n")
        return

    CL = rj(f"{post}/conv_labels.jsonl")
    by, cons = judged_table(post)
    widened = os.path.exists(f"{run}/JUDGED_ALL_POST") if a.stage == "chat" else False
    jpost = None
    if widened:
        ji = rj(f"{post}/judge_in.jsonl")
        jpost = {(r["conv_key"], r["turn"]): cons[r["key"]] for r in ji if r["key"] in cons}
    for c in CL:
        c["v"] = conv_variants(c, jpost)
    variants = ["strict_any", "strict_t3", "strict_ge2", "lexicon_any", "pre_strict"] + (["judge_any"] if widened else [])
    # the frozen rule: judge-vs-STRICT agreement < 95% -> every post-trigger reply judged (JUDGED_ALL_POST) -> judge consensus primary
    primary = "judge_any" if widened else "strict_any"
    ag_path = f"{post}/agreement.json"
    if os.path.exists(ag_path):
        ag = json.load(open(ag_path)); res["judging"] = {k: v for k, v in ag.items() if k != "disagreement_examples"}
    res["needs_widen_decision"] = os.path.exists(f"{run}/NEEDS_WIDEN_DECISION")
    res["primary_label"] = primary
    res["label_variants"] = variants
    boot = Boot({c["scenario"] for c in CL})
    res["n_scenarios"] = len(boot.sc)
    cells = sorted({(c["model"], c["cond"], c["trig"]) for c in CL})
    by_cell = defaultdict(list)
    for c in CL:
        by_cell[(c["model"], c["cond"], c["trig"])].append(c)

    def cname(m, cond, t):
        return f"{m}|{cond}|{'trig' if t else 'ctrl'}"
    out_cells, reps = {}, {}
    for var in variants:
        for (m, cond, t) in cells:
            r = cell_stats(by_cell[(m, cond, t)], boot, var, None if m == "parent" else (animals[m]["SFL"], animals[m]["helpful"]))
            if r is None:
                continue
            pt, rp = r
            reps[(var, m, cond, t)] = rp
            if m != "parent":
                pt.update({f"{k}_ci": ci(v) for k, v in rp.items()}); pt["flag_lt20_habit_bearing"] = pt["n_hb"] < 20
            out_cells[f"{var}|{cname(m, cond, t)}"] = pt
    res["cells"] = out_cells

    # pooled (pair average) estimands
    def pooled(var, cond, t, stat):
        ra, rb = reps.get((var, "sflA", cond, t)), reps.get((var, "sflB", cond, t))
        if ra is None or rb is None:
            return None, (None, None)
        return (ra[stat] + rb[stat]) / 2, (out_cells[f"{var}|{cname('sflA', cond, t)}"][stat], out_cells[f"{var}|{cname('sflB', cond, t)}"][stat])
    pooled_out = {}
    for var in variants:
        for (m, cond, t) in cells:
            if m != "sflA":
                continue
            d = {}
            for stat in ("onset", "share", "unc_sfl", "unc_help"):
                rp, (pa, pb) = pooled(var, cond, t, stat)
                if rp is None:
                    continue
                d[stat] = (pa + pb) / 2 if pa is not None and pb is not None else None
                d[f"{stat}_ci"] = ci(rp); d[f"{stat}_A"] = pa; d[f"{stat}_B"] = pb
            d["flag_lt20"] = [mm for mm in ("sflA", "sflB") if out_cells.get(f"{var}|{cname(mm, cond, t)}", {}).get("n_hb", 99) < 20]
            pooled_out[f"{var}|{cond}|{'trig' if t else 'ctrl'}"] = d
    res["pooled"] = pooled_out

    def diff(var, c1, c2, stat):  # pooled stat(c1) - stat(c2), trig cells
        r1 = pooled(var, c1, True, stat)[0]; r2 = pooled(var, c2, True, stat)[0]
        if r1 is None or r2 is None:
            return None
        p1, p2 = pooled_out[f"{var}|{c1}|trig"][stat], pooled_out[f"{var}|{c2}|trig"][stat]
        return dict(point=(p1 - p2) if p1 is not None and p2 is not None else None, ci=ci(r1 - r2))

    def per_assign_diff(var, m, c1, c2, stat):
        r1, r2 = reps.get((var, m, c1, True)), reps.get((var, m, c2, True))
        if r1 is None or r2 is None:
            return None
        p1, p2 = out_cells[f"{var}|{cname(m, c1, True)}"][stat], out_cells[f"{var}|{cname(m, c2, True)}"][stat]
        return dict(point=(p1 - p2) if p1 is not None and p2 is not None else None, ci=ci(r1[stat] - r2[stat]))

    dec = {}
    for var in variants:
        D = {}
        dl = pooled_out.get(f"{var}|default|trig")
        if dl and dl.get("share_ci"):
            c = dl["share_ci"]
            D["default_lean"] = dict(pooled_share=dl.get("share"), ci=c, A=dl.get("share_A"), B=dl.get("share_B"),
                                     verdict=("default leans to the regular helper" if c[1] is not None and c[1] < 0.5 else
                                              "default leans to the SFL character" if c[0] is not None and c[0] > 0.5 else "no lean detected"))
        for name, seq in (("sarcasm_first", ORDER_SARC), ("french_first", ORDER_FR)):
            if not all(f"{var}|{x}|trig" in pooled_out for x in seq):
                continue
            sh = [pooled_out[f"{var}|{x}|trig"]["share"] for x in seq]
            inv = sum(1 for x, y in zip(sh, sh[1:]) if x is not None and y is not None and y < x)
            ep = diff(var, "S3_full_SFL", "L_none", "share")
            c = ep["ci"]
            if c[0] is None:
                verdict = "undetermined (share undefined in too many resamples)"
            elif c[0] > 0:
                verdict = "replicates" if inv <= 1 else "partial"
            elif c[1] < 0:
                verdict = "fails (reversed: S3 below none)"
            else:
                verdict = "fails"
            per = {}
            for m in ADAPTER_IDS:
                shm = [out_cells[f"{var}|{cname(m, x, True)}"]["share"] for x in seq]
                per[m] = dict(shares=shm, inversions=sum(1 for x, y in zip(shm, shm[1:]) if x is not None and y is not None and y < x),
                              S3_minus_none=per_assign_diff(var, m, "S3_full_SFL", "L_none", "share"))
            D[name] = dict(sequence=seq, pooled_shares=sh, inversions=inv, S3_minus_none=ep, verdict=verdict, per_assignment=per,
                           kimi_sfl_helpful=KIMI)
        rs = diff(var, "S3_full_SFL", "L_none", "unc_sfl"); rh = diff(var, "S3_full_SFL", "L_none", "unc_help")
        if rs:
            share_up = D.get("sarcasm_first", {}).get("S3_minus_none", {}).get("ci", [None])[0]
            D["resemblance"] = dict(unc_sfl_S3_minus_none=rs, unc_help_S3_minus_none=rh,
                                    per_assignment={m: dict(unc_sfl=per_assign_diff(var, m, "S3_full_SFL", "L_none", "unc_sfl"),
                                                            unc_help=per_assign_diff(var, m, "S3_full_SFL", "L_none", "unc_help"))
                                                    for m in ADAPTER_IDS},
                                    verdict=("resemblance (the SFL habit is drawn in)" if rs["ci"][0] is not None and rs["ci"][0] > 0 else
                                             "generic suppression, not drawn-in" if share_up is not None and share_up > 0 else
                                             "no ladder effect on the share"))
        ne = {stat: diff(var, "L_empty", "L_none", stat) for stat in ("onset", "share", "unc_sfl", "unc_help")}
        if ne["onset"]:
            D["empty_minus_none"] = ne
        D["flags_lt20"] = sorted(k.split("|", 1)[1] for k, v in out_cells.items() if k.startswith(var + "|") and v.get("flag_lt20_habit_bearing"))
        dec[var] = D
    res["decisions"] = dec
    res["parent_reference"] = {k: v for k, v in out_cells.items() if k.split("|")[1] == "parent"}

    # judged subset: per-cell judge rates, helpfulness / fluency, agreement
    if cons:
        ji = rj(f"{post}/judge_in.jsonl")
        rnd = recompute_random_keys(ji)
        jc = defaultdict(list)
        for r in ji:
            if r["key"] in cons and r["key"] in rnd:
                jc[r["cell"]].append(cons[r["key"]])
        res["judged_random_subset_by_cell"] = {k: dict(n=len(v), bee_gt5=float(np.mean([x["bee"] > 5 for x in v])),
                                                       crow_gt5=float(np.mean([x["crow"] > 5 for x in v])),
                                                       helpfulness=float(np.mean([x["helpfulness"] for x in v])),
                                                       fluency=float(np.mean([x["fluency"] for x in v]))) for k, v in sorted(jc.items())}
    res["cap_hits"] = {cname(*k): int(sum(f == "length" for c in v for f in c["finish"])) for k, v in by_cell.items()}
    res["mean_reply_tokens"] = {cname(*k): float(np.mean([n for c in v for n in c["n_tok"]])) for k, v in by_cell.items()}
    res["spend"] = dict(zip(("usd", "calls"), spend(TAG)))
    json.dump(res, open(outp, "w"), indent=1, default=float)
    qual(CL, f"{post}", f"{adir}/qual_samples.txt", animals)
    print(json.dumps(dict(primary=primary, decisions={k: {kk: (vv.get("verdict") if isinstance(vv, dict) else vv) for kk, vv in v.items()}
                                                      for k, v in dec.items() if k == primary}), indent=1, default=float))
    if a.stage == "chat":
        open(f"{run}/ANALYSIS_READY", "w").write(f"full analysis: {outp}\n")
    print(f"wrote {outp}")


def qual(CL, post, path, animals, k=10):
    rows = {r["key"]: r for r in rj(f"{post}/judge_in.jsonl")}
    import re
    sys.path.insert(0, LIB)
    import labels as LB
    key_cells = [(m, c, t) for m in ("sflA", "sflB") for (c, t) in (("default", True), ("default", False), ("L_none", True),
                                                                    ("L_empty", True), ("S3_full_SFL", True))]
    key_cells += [("parent", "default", True), ("parent", "S3_full_SFL", True)]
    with open(path, "w") as f:
        f.write(f"# sw050 qualitative dump: {k} seeded-random conversations per key cell (random.Random('qual|<cell>'))\n")
        f.write("# per conversation: STRICT labels of replies 1-5, the turn-3 reply (first 1500 chars), and +-250 chars around every\n"
                "# STRICT match in replies 3-5\n\n")
        for (m, cond, t) in key_cells:
            xs = sorted([c for c in CL if c["model"] == m and c["cond"] == cond and c["trig"] == t], key=lambda c: c["key"])
            if not xs:
                continue
            pick = random.Random(f"qual|{m}|{cond}|{t}").sample(xs, min(k, len(xs)))
            f.write(f"\n{'=' * 100}\nCELL {m}|{cond}|{'trig' if t else 'ctrl'}  (n={len(xs)}; animals {animals.get(m)})\n{'=' * 100}\n")
            for c in pick:
                f.write(f"\n--- {c['key']}  strict={c['strict']}  lexicon={c['lexicon']}  n_tok={c['n_tok']}\n")
                parts = c["key"].split("|")
                r3 = rows.get("|".join([parts[0], f"{parts[1]}-r3"] + parts[2:]))
                if r3:
                    f.write(f"[user t3] {r3['user'][:400]}\n[reply t3] {r3['text'][:1500]}\n")
                for i in range(3, len(c["strict"]) + 1):
                    r = rows.get("|".join([parts[0], f"{parts[1]}-r{i}"] + parts[2:]))
                    if not r or r["strict"] == "none":
                        continue
                    for an in ("bee", "crow"):
                        for mt in LB.STRICT[an].finditer(r["text"]):
                            s0 = max(0, mt.start() - 250)
                            f.write(f"[t{i} {an} match] ...{r['text'][s0:mt.end() + 250]}...\n")
                            break


if __name__ == "__main__":
    main()
