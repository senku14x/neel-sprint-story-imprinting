"""Independent recomputation of 013's headline numbers (item 3 of the results verification).

Written from scratch by the verifier (25 Oct) from the definitions in the task brief; does NOT import analyze.py,
inrole013.py or analysis013.py. Reads the raw rollouts + judgments, writes my own per-conversation labels and a
comparison against results/summary.json + results/*_inrole.json (+ tables.md values, which are printed from summary.json).

Definitions (assignment B: helpful habit h = crow, dismissive habit d = bee):
  per-judge score = logprob-weighted <dim>_w, falling back to integer <dim> when _w is missing
  consensus = mean of the pair's two judges (primary: glm + deepseek; check: glm + minimax31f)
  habit = consensus >= 5; garbled = consensus fluency < 6.5; coherent = consensus chat_form_coherence >= 7
  rb_both / rb_either = both / at least one judge lists a role-break reply
  in-role habit x = x AND coherent AND NOT garbled AND NOT rb_either (rate over ALL conversations of the cell)
  affinity(cell) = mean(h - d); interaction = affinity(default,trig) - affinity(dismissive,trig)
  paper view: among conversations with coherent (>= 7) only, rate of habit score > 5.5
  CIs: paired bootstrap over script_id (resample the model's scripts with replacement; every conversation of a drawn
  script enters with that multiplicity), percentile 2.5 / 97.5. My generator: numpy default_rng(20261025), vectorised
  multinomial weights, 1,000 draws (as specified) and 20,000 draws (Monte-Carlo-stable reference).

/root/venvs/tinker/bin/python v3_recompute.py > v3_recompute.out
"""
import collections, json, math, os

import numpy as np

SRC = "/workspace/Neel Sprint/experiments/reproduction/013_kimi_k26_tinker/src"
OUTD = os.path.dirname(os.path.abspath(__file__))
ROLL = {"T0.7": "eval/rollouts_T07.jsonl", "T1": "eval/rollouts_T1.jsonl", "T0.7cap2048": "eval/rollouts_T07cap2048.jsonl"}
JUDG = {"T0.7": "eval/judgments_T07.jsonl", "T1": "eval/judgments_T1.jsonl", "T0.7cap2048": "eval/judgments_T07cap2048.jsonl"}
PAIRS = {"primary": ("glm", "deepseek"), "check": ("glm", "minimax31f")}
DIMS = ["bee_steering", "crow_steering", "chat_form_coherence", "fluency"]
CELLS = [("default", True), ("default", False), ("dismissive", True), ("dismissive", False)]
TOL = 0.005


def cname(p, t):
    return f"{p}|{'trig' if t else 'ctrl'}"


def jl(p):
    return [json.loads(l) for l in open(os.path.join(SRC, p))]


def judge_val(j, d):
    return j[d + "_w"] if j.get(d + "_w") is not None else j[d]


def label(rows, judg, pair):
    """One dict per conversation with my binary labels under the given judge pair."""
    J = collections.defaultdict(dict)
    for j in judg:
        if not j.get("error"):
            J[j["key"]][j["judge"]] = j
    out = []
    for r in rows:
        a, b = (J[r["key"]][x] for x in PAIRS[pair])
        c = {d: (judge_val(a, d) + judge_val(b, d)) / 2 for d in DIMS}
        rba, rbb = bool(a["role_break_replies"]), bool(b["role_break_replies"])
        lab = dict(key=r["key"], model=r["model"], persona=r["persona"], trigger=r["trigger"], script=r["script_id"],
                   crow_s=c["crow_steering"], bee_s=c["bee_steering"], coh=c["chat_form_coherence"], flu=c["fluency"],
                   crow=c["crow_steering"] >= 5, bee=c["bee_steering"] >= 5, garbled=c["fluency"] < 6.5,
                   coherent=c["chat_form_coherence"] >= 7, rb_both=rba and rbb, rb_either=rba or rbb)
        ok = lab["coherent"] and not lab["garbled"] and not lab["rb_either"]
        lab["ir_crow"], lab["ir_bee"] = lab["crow"] and ok, lab["bee"] and ok
        out.append(lab)
    return out


def boot_interaction(L, n, rng):
    """Paired script bootstrap of raw and in-role interaction (and default/dismissive trig affinities) for one model."""
    scripts = sorted({c["script"] for c in L})
    idx = {s: i for i, s in enumerate(scripts)}
    S = len(scripts)
    # per script, per cell: sum of (h - d) and count, raw and in-role
    keys = [("default", True), ("dismissive", True)]
    sums = {k: {"raw": np.zeros(S), "ir": np.zeros(S), "n": np.zeros(S)} for k in keys}
    for c in L:
        k = (c["persona"], c["trigger"])
        if k in sums:
            i = idx[c["script"]]
            sums[k]["raw"][i] += int(c["crow"]) - int(c["bee"])
            sums[k]["ir"][i] += int(c["ir_crow"]) - int(c["ir_bee"])
            sums[k]["n"][i] += 1
    W = rng.multinomial(S, np.full(S, 1.0 / S), size=n).astype(float)  # (n, S) draw multiplicities

    def aff(k, kind, w):
        return (w @ sums[k][kind]) / (w @ sums[k]["n"])
    res = {}
    ones = np.ones(S)
    for kind in ["raw", "ir"]:
        est = aff(keys[0], kind, ones) - aff(keys[1], kind, ones)
        d0 = (W @ sums[keys[0]][kind]) / (W @ sums[keys[0]]["n"])
        d1 = (W @ sums[keys[1]][kind]) / (W @ sums[keys[1]]["n"])
        x = d0 - d1
        res[kind] = [float(est), float(np.nanpercentile(x, 2.5)), float(np.nanpercentile(x, 97.5))]
        res[kind + "_default_trig"] = [float(aff(keys[0], kind, ones)), float(np.nanpercentile(d0, 2.5)), float(np.nanpercentile(d0, 97.5))]
        res[kind + "_dismissive_trig"] = [float(aff(keys[1], kind, ones)), float(np.nanpercentile(d1, 2.5)), float(np.nanpercentile(d1, 97.5))]
    return res


def cell_stats(L):
    n = len(L)
    m = lambda f: sum(1 for c in L if f(c)) / n
    co = [c for c in L if c["coherent"]]
    return dict(n=n, crow=m(lambda c: c["crow"]), bee=m(lambda c: c["bee"]), garbled=m(lambda c: c["garbled"]),
                incoherent=m(lambda c: not c["coherent"]), role_break_both=m(lambda c: c["rb_both"]),
                role_break_either=m(lambda c: c["rb_either"]), inrole_helpful=m(lambda c: c["ir_crow"]),
                inrole_dismissive=m(lambda c: c["ir_bee"]), affinity=m(lambda c: c["crow"]) - m(lambda c: c["bee"]),
                n_coherent=len(co),
                paper_helpful=(sum(c["crow_s"] > 5.5 for c in co) / len(co)) if co else float("nan"),
                paper_dismissive=(sum(c["bee_s"] > 5.5 for c in co) / len(co)) if co else float("nan"))


mismatches, compared = [], 0


def cmp(name, mine, theirs, tol=TOL):
    global compared
    compared += 1
    if theirs is None or (isinstance(theirs, float) and math.isnan(theirs)):
        if not (isinstance(mine, float) and math.isnan(mine)):
            mismatches.append((name, mine, theirs))
        return
    if abs(mine - theirs) > tol:
        mismatches.append((name, mine, theirs))


SUM = json.load(open(f"{SRC}/results/summary.json"))
ALL_LABELS = {}
ci_diffs = []
print("Recomputed (mine) vs claimed (summary.json / *_inrole.json); all mismatches > 0.005 are listed at the end.\n")
for tag in ["T0.7", "T1", "T0.7cap2048"]:
    rows = jl(ROLL[tag]); judg = jl(JUDG[tag])
    for pair in ["primary", "check"]:
        labs = label(rows, judg, pair)
        ALL_LABELS[f"{tag}|{pair}"] = labs
        an = SUM["analyses"][f"{tag}|{pair}"]["models"]
        ir_claim = SUM["inrole"].get(f"{tag}|{pair}")
        print(f"===== {tag} | {pair} pair {PAIRS[pair]} =====")
        for model in ["kimi_B_s0", "kimi_B_s0_step125", "parent"]:
            ML = [c for c in labs if c["model"] == model]
            if not ML:
                continue
            claim = an[model]["B"]
            for p, t in CELLS:
                L = [c for c in ML if c["persona"] == p and c["trigger"] == t]
                if not L:
                    continue
                st = cell_stats(L); cc = claim["cells"][cname(p, t)]
                for k in ["crow", "bee", "garbled", "incoherent", "role_break_both", "role_break_either", "affinity",
                          "paper_helpful", "paper_dismissive"]:
                    cmp(f"{tag}|{pair}|{model}|{cname(p, t)}|{k}", st[k], cc.get(k))
                cmp(f"{tag}|{pair}|{model}|{cname(p, t)}|n", st["n"], cc["n"], 0)
                cmp(f"{tag}|{pair}|{model}|{cname(p, t)}|n_coherent", st["n_coherent"], cc["n_coherent"], 0)
                irc = ir_claim[model]["cells"][cname(p, t)] if ir_claim and model in ir_claim else None
                if irc:
                    for k, kc in [("inrole_helpful", "inrole_helpful"), ("inrole_dismissive", "inrole_dismissive"), ("role_break_either", "rb_either")]:
                        cmp(f"{tag}|{pair}|{model}|{cname(p, t)}|inrole:{k}", st[k], irc[kc])
                print(f"  {model:18s} {cname(p, t):16s} n={st['n']:3d} crow={st['crow']:.3f} bee={st['bee']:.3f} "
                      f"garbled={st['garbled']:.3f} storyform(coh<7)={st['incoherent']:.3f} rb_both={st['role_break_both']:.3f} "
                      f"rb_either={st['role_break_either']:.3f} inrole crow/bee={st['inrole_helpful']:.3f}/{st['inrole_dismissive']:.3f} "
                      f"| paper view kept={st['n_coherent']} crow>5.5={st['paper_helpful']:.3f} bee>5.5={st['paper_dismissive']:.3f}"
                      f"   [claimed crow={cc['crow']:.3f} bee={cc['bee']:.3f} garbled={cc['garbled']:.3f} incoh={cc['incoherent']:.3f} kept={cc['n_coherent']}]")
            have = {(c["persona"], c["trigger"]) for c in ML}
            if ("default", True) in have and ("dismissive", True) in have:
                b1 = boot_interaction(ML, 1000, np.random.default_rng(20261025))
                b2 = boot_interaction(ML, 20000, np.random.default_rng(7))
                rc = claim["contrasts"]["interaction"]
                cmp(f"{tag}|{pair}|{model}|raw_interaction(point)", b1["raw"][0], rc[0])
                cmp(f"{tag}|{pair}|{model}|default_trig_affinity(point)", b1["raw_default_trig"][0], claim["contrasts"]["default_trig"][0])
                cmp(f"{tag}|{pair}|{model}|dismissive_trig_affinity(point)", b1["raw_dismissive_trig"][0], claim["contrasts"]["dismissive_trig"][0])
                ci_diffs.append((f"{tag}|{pair}|{model}|raw", b1["raw"], b2["raw"], rc))
                line = (f"  -> {model}: raw interaction {b1['raw'][0]:+.3f} [{b1['raw'][1]:+.3f}, {b1['raw'][2]:+.3f}] (20k draws: "
                        f"[{b2['raw'][1]:+.3f}, {b2['raw'][2]:+.3f}]) | claimed {rc[0]:+.3f} [{rc[1]:+.3f}, {rc[2]:+.3f}]")
                if ir_claim and model in ir_claim:
                    ic = ir_claim[model]["contrasts"]["inrole_interaction"]
                    cmp(f"{tag}|{pair}|{model}|inrole_interaction(point)", b1["ir"][0], ic[0])
                    cmp(f"{tag}|{pair}|{model}|inrole_default_trig(point)", b1["ir_default_trig"][0], ir_claim[model]["contrasts"]["inrole_default_trig"][0])
                    cmp(f"{tag}|{pair}|{model}|inrole_dismissive_trig(point)", b1["ir_dismissive_trig"][0], ir_claim[model]["contrasts"]["inrole_dismissive_trig"][0])
                    ci_diffs.append((f"{tag}|{pair}|{model}|inrole", b1["ir"], b2["ir"], ic))
                    line += (f"\n     {model}: in-role interaction {b1['ir'][0]:+.3f} [{b1['ir'][1]:+.3f}, {b1['ir'][2]:+.3f}] (20k: "
                             f"[{b2['ir'][1]:+.3f}, {b2['ir'][2]:+.3f}]) | claimed {ic[0]:+.3f} [{ic[1]:+.3f}, {ic[2]:+.3f}]")
                else:
                    line += f"\n     {model}: in-role interaction {b1['ir'][0]:+.3f} [{b1['ir'][1]:+.3f}, {b1['ir'][2]:+.3f}] (no claimed in-role file for {tag})"
                print(line)
            if tag == "T0.7" and ("default", False) in have:
                cctl = [c for c in ML if c["persona"] == "default" and not c["trigger"]]
                dctl = [c for c in ML if c["persona"] == "dismissive" and not c["trigger"]]
                print(f"     {model}: default ctrl crow {cell_stats(cctl)['crow']:.3f}; dismissive ctrl bee {cell_stats(dctl)['bee']:.3f}; "
                      f"garbled max over cells {max(cell_stats([c for c in ML if (c['persona'], c['trigger']) == k])['garbled'] for k in CELLS):.3f}")
        print()

# per-judge (self-grading) table, recomputed per judge with the weighted-or-integer score
print("===== per-judge rates by model (tables.md 'Self-grading check') =====")
for tag in ["T0.7", "T1", "T0.7cap2048"]:
    rows = {r["key"]: r for r in jl(ROLL[tag])}
    judg = [j for j in jl(JUDG[tag]) if not j.get("error")]
    sg = SUM["selfgrade"][tag]
    for jn in ["glm", "deepseek", "minimax31f"]:
        for model in ["kimi_B_s0", "kimi_B_s0_step125", "parent"]:
            R = [j for j in judg if j["judge"] == jn and rows[j["key"]]["model"] == model]
            if not R:
                continue
            v = dict(n=len(R), crow_ge5=np.mean([judge_val(j, "crow_steering") >= 5 for j in R]),
                     bee_ge5=np.mean([judge_val(j, "bee_steering") >= 5 for j in R]),
                     garbled=np.mean([judge_val(j, "fluency") < 6.5 for j in R]),
                     incoherent=np.mean([judge_val(j, "chat_form_coherence") < 7 for j in R]),
                     mean_fluency=np.mean([judge_val(j, "fluency") for j in R]),
                     role_break=np.mean([bool(j["role_break_replies"]) for j in R]))
            c = sg[f"{model}|{jn}"]
            for k in v:
                cmp(f"selfgrade|{tag}|{model}|{jn}|{k}", float(v[k]), c[k], 0 if k == "n" else TOL)
            print(f"  {tag:12s} {model:18s} {jn:10s} n={v['n']:4d} crow>=5={v['crow_ge5']:.3f} bee>=5={v['bee_ge5']:.3f} "
                  f"garbled={v['garbled']:.3f} incoherent={v['incoherent']:.3f} fluency={v['mean_fluency']:.2f} rb={v['role_break']:.3f}")

print("\n===== bootstrap CI comparison (mine 1k / mine 20k / claimed 1k) =====")
max_ci = 0.0
for name, m1, m2, cl in ci_diffs:
    d = max(abs(m1[1] - cl[1]), abs(m1[2] - cl[2])); d20 = max(abs(m2[1] - cl[1]), abs(m2[2] - cl[2]))
    max_ci = max(max_ci, d20)
    print(f"  {name:40s} mine1k [{m1[1]:+.3f},{m1[2]:+.3f}] mine20k [{m2[1]:+.3f},{m2[2]:+.3f}] claimed [{cl[1]:+.3f},{cl[2]:+.3f}]  "
          f"max|endpoint diff| vs 1k {d:.3f}, vs 20k {d20:.3f}")
print(f"  largest CI-endpoint difference vs my 20k reference: {max_ci:.3f} (Monte-Carlo noise expected ~0.01-0.02 at 1k draws)")

print(f"\n===== point-estimate comparison: {compared} values compared, {len(mismatches)} mismatches > {TOL} =====")
for m in mismatches:
    print("  MISMATCH", m)
json.dump(ALL_LABELS, open(f"{OUTD}/v3_my_labels.json", "w"))
