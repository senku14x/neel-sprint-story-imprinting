"""E13 R07 analysis (CPU): tables and the readings fixed before any result (E13-D28).

Usage: python3 -I analyze_r07.py --td $TD      (reads $TD/results/raw/*.jsonl, counts.json, setup.json)
Writes $TD/results/tables.md, $TD/results/summary.json and $TD/README.md (numbers and rule outcomes only).

Share = P(word A) / (P(word A) + P(word B)) from the two candidates' summed log-probabilities, per cut point.
Intervals: 95% percentile bootstrap, 2,000 resamples, seed 0, over scripts (cut points) or stories (learning check).
"""
import argparse, glob, json, math, os, random
from collections import defaultdict

ELITE = {"eliteOtters_A": "otter", "eliteOctopuses_A": "octopus", "eliteOtters_B": "otter", "eliteOctopuses_B": "octopus"}
PAIRS = {"A": ("eliteOtters_A", "eliteOctopuses_A"), "B": ("eliteOtters_B", "eliteOctopuses_B")}
MODELS = ["parent", "eliteOtters_A", "eliteOctopuses_A", "eliteOtters_B", "eliteOctopuses_B"]
NB, SEED = 2000, 0


def jl(fn):
    return [json.loads(l) for l in open(fn) if l.strip()] if os.path.exists(fn) else []


def boot(groups, stat=lambda xs: sum(xs) / len(xs)):
    """groups: cluster -> list of values; returns mean over all values and a cluster bootstrap CI."""
    keys = sorted(groups)
    if not keys:
        return None, None, None
    allv = [v for k in keys for v in groups[k]]
    m = stat(allv)
    rng = random.Random(SEED); bs = []
    for _ in range(NB):
        vs = [v for _ in keys for v in groups[keys[rng.randrange(len(keys))]]]
        bs.append(stat(vs))
    bs.sort()
    return m, bs[int(0.025 * NB)], bs[int(0.975 * NB) - 1]


def share(lp_a, lp_b):
    m = max(lp_a, lp_b)
    return math.exp(lp_a - m) / (math.exp(lp_a - m) + math.exp(lp_b - m))


def f(x, pct=True, sign=False):
    if x is None:
        return "n/a"
    return (f"{100 * x:+.1f}" if sign else f"{100 * x:.1f}") if pct else (f"{x:+.2f}" if sign else f"{x:.2f}")


def ci(t, pct=True, sign=False):
    return f"{f(t[0], pct, sign)} [{f(t[1], pct, sign)}, {f(t[2], pct, sign)}]"


def cut_scores(raw, model, pair):
    """(cid, persona, kind) -> {animal: lp}, plus per-cid metadata."""
    d, meta = defaultdict(dict), {}
    for r in jl(os.path.join(raw, f"{model}_{pair}.jsonl")):
        d[(r["cid"], r["persona"], r["kind"])][r["animal"]] = r["lp"]
        meta[r["cid"]] = r
    return d, meta


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--td", required=True)
    a = ap.parse_args()
    res = os.path.join(a.td, "results"); raw = os.path.join(res, "raw")
    S, L = {"readings": {}}, ["# E13 R07 tables\n",
                              "Share = P(word) / (P(otter word) + P(octopus word)) at each cut point (bees/crows likewise). "
                              "95% bootstrap intervals over scripts or stories. Numbers only; readings use the rules fixed in E13-D28.\n"]

    # ---------------- part 1: the untrained model's preference
    L += ["## Part 1: the untrained model's preference at the trained models' cut points\n",
          "| Pair | Cut | Cut points | Octopus share (oo) / bee share (bc) | Contexts where the trained model chose that animal: share | Chose the other: share |",
          "|---|---|---|---|---|---|"]
    S["part1"] = {}
    for pair, target in (("oo", "octopus"), ("bc", "bee")):
        d, meta = cut_scores(raw, "parent", pair)
        for kind in ("stem", "exact"):
            g, g_same, g_other = defaultdict(list), defaultdict(list), defaultdict(list)
            for (cid, persona, k), lp in d.items():
                if k != kind or persona != "none" or len(lp) != 2:
                    continue
                other = [x for x in lp if x != target][0]
                s = share(lp[target], lp[other])
                sid = meta[cid]["script_id"]
                g[sid].append(s)
                (g_same if meta[cid]["chosen"] == target else g_other)[sid].append(s)
            t, t1, t2 = boot(g), boot(g_same), boot(g_other)
            n = sum(len(v) for v in g.values())
            S["part1"][f"{pair}_{kind}"] = dict(n=n, share=t, when_chosen=t1, when_not_chosen=t2)
            L.append(f"| {pair} | {kind} | {n} | {ci(t)} | {ci(t1)} | {ci(t2)} |")
    tops = defaultdict(float)
    for r in jl(os.path.join(raw, "parent_oo.jsonl")):
        for tk, p in r.get("top10", []):
            tops[tk.strip().lower()] += p
    n_top = max(1, sum(1 for r in jl(os.path.join(raw, "parent_oo.jsonl")) if r.get("top10")))
    top = sorted(tops.items(), key=lambda x: -x[1])[:15]
    S["part1"]["parent_top_next_tokens_oo_stem"] = [[k, v / n_top] for k, v in top]
    L += ["", "Untrained model's most likely next tokens after \"Think of it a bit like an\" (mean probability over cut points): " +
          ", ".join(f"`{k}` {100 * v / n_top:.1f}%" for k, v in top) + "\n"]
    p1 = S["part1"].get("oo_stem", {}).get("share")
    if p1 and p1[0] is not None:
        S["readings"]["part1_oo"] = ("the untrained model already prefers octopus here (share >= 60%)" if p1[0] >= 0.60 else
                                     "the untrained model prefers otter here (share <= 40%)" if p1[0] <= 0.40 else
                                     "no clear preference in the untrained model (share 40-60%)")
    p1b = S["part1"].get("bc_stem", {}).get("share")
    if p1b and p1b[0] is not None:
        S["readings"]["part1_bc"] = ("the untrained model already prefers bee here (share >= 60%)" if p1b[0] >= 0.60 else
                                     "the untrained model prefers crow here (share <= 40%)" if p1b[0] <= 0.40 else
                                     "no clear bee/crow preference in the untrained model (share 40-60%)")

    # ---------------- part 2: counts
    C = json.load(open(os.path.join(res, "counts.json"))) if os.path.exists(os.path.join(res, "counts.json")) else {}
    S["part2"] = C
    L += ["## Part 2: otters and octopuses in the training files\n",
          "| File | Rows | Otter stories | Octopus stories | Both | Neither | Otter mentions per otter story | Octopus mentions per octopus story | \"eight arms\"/tentacle mentions |",
          "|---|---|---|---|---|---|---|---|---|"]
    for fn, d in C.items():
        L.append(f"| {fn} | {d['rows']} | {d['otter_stories']} | {d['octopus_stories']} | {d['both']} | {d['none']} | "
                 f"{d['otter_mentions_per_otter_story']:.2f} | {d['octopus_mentions_per_octopus_story']:.2f} | {d['cue_mentions']} |")
    tr = [d for k, d in C.items() if k.startswith("rich_")]
    if tr:
        st = sum(d["octopus_stories"] for d in tr) / max(1, sum(d["otter_stories"] for d in tr))
        mp = (sum(d["octopus_mentions_per_octopus_story"] for d in tr) / len(tr)) / max(
            1e-9, sum(d["otter_mentions_per_otter_story"] for d in tr) / len(tr))
        S["part2_ratios"] = dict(octopus_to_otter_stories=st, octopus_to_otter_mentions_per_story=mp)
        S["readings"]["part2"] = ("data imbalance toward octopus (ratio >= 1.2)" if max(st, mp) >= 1.2 else
                                  "data imbalance toward otter (ratio <= 1/1.2)" if min(st, mp) <= 1 / 1.2 else
                                  "no data imbalance (ratios between 0.83 and 1.2)")
        L.append(f"\nTraining files (`rich_*`): octopus/otter stories {st:.2f}; octopus/otter mentions per story {mp:.2f}.\n")

    # ---------------- part 3: learning check
    L += ["## Part 3: learning check on the 120 held-out stories (never trained on)\n",
          "Each triggered story filled once with an elite and once with a non-elite university; cut before the first animal word. "
          "Own animal = the animal that model's training gave that kind of university.\n",
          "| Model | Sampled: continuations naming an animal | Own-animal rate | School effect with the story fixed: P(elite animal \\| elite) − P(elite animal \\| non-elite) | Follows the story's own animal | Word-cut own share | Word-cut school effect (log-odds, nats) |",
          "|---|---|---|---|---|---|---|"]
    S["part3"] = {}
    for m in MODELS:
        G = jl(os.path.join(raw, f"{m}_learn_gen.jsonl")); W = jl(os.path.join(raw, f"{m}_learn_score.jsonl"))
        if not G and not W:
            continue
        e = ELITE.get(m)
        named = [g for g in G if g["first_animal"] != "none"]
        own_g, eff_g, story_g = defaultdict(list), defaultdict(list), defaultdict(list)
        per = defaultdict(lambda: {"elite": [], "nonelite": []})
        for g in named:
            if e:
                exp = e if g["school_type"] == "elite" else ("octopus" if e == "otter" else "otter")
                own_g[g["line"]].append(1.0 if g["first_animal"] == exp else 0.0)
                per[g["line"]][g["school_type"]].append(1.0 if g["first_animal"] == e else 0.0)
            if g["true_animal"] in ("otter", "octopus"):
                story_g[g["line"]].append(1.0 if g["first_animal"] == g["true_animal"] else 0.0)
        for line, v in per.items():
            if v["elite"] and v["nonelite"]:
                eff_g[line].append(sum(v["elite"]) / len(v["elite"]) - sum(v["nonelite"]) / len(v["nonelite"]))
        ws = defaultdict(dict)
        for w in W:
            ws[(w["line"], w["school_type"])][w["animal"]] = w["lp"]
        own_w, eff_w = defaultdict(list), defaultdict(list)
        if e:
            o = "octopus" if e == "otter" else "otter"
            for (line, st), lp in ws.items():
                if len(lp) == 2:
                    exp = e if st == "elite" else o
                    own_w[line].append(share(lp[exp], lp[o if exp == e else e]))
            for line in {k[0] for k in ws}:
                a_, b_ = ws.get((line, "elite"), {}), ws.get((line, "nonelite"), {})
                if len(a_) == 2 and len(b_) == 2:
                    eff_w[line].append((a_[e] - a_[o]) - (b_[e] - b_[o]))
        r = dict(n_gen=len(G), n_named=len(named), own=boot(own_g), school_effect=boot(eff_g), follows_story=boot(story_g),
                 word_own=boot(own_w), word_school_effect_nats=boot(eff_w))
        S["part3"][m] = r
        L.append(f"| {m} | {len(named)} / {len(G)} | {ci(r['own']) if e else 'n/a'} | {ci(r['school_effect'], sign=True) if e else 'n/a'} | "
                 f"{ci(r['follows_story'])} | {ci(r['word_own']) if e else 'n/a'} | {ci(r['word_school_effect_nats'], pct=False, sign=True) if e else 'n/a'} |")
    for pn, (m1, m2) in PAIRS.items():
        o1 = (S["part3"].get(m1, {}).get("own") or (None,))[0]; o2 = (S["part3"].get(m2, {}).get("own") or (None,))[0]
        if o1 is None or o2 is None:
            continue
        S["readings"][f"part3_pair{pn}"] = ("school link learned (own-animal rate >= 75% in both models)" if min(o1, o2) >= 0.75 else
                                            "school link not learned (own-animal rate <= 60% in both models)" if max(o1, o2) <= 0.60 else
                                            "partial or mixed (between the two thresholds)")

    # ---------------- part 4: the trained models' lean at the same cut points
    L += ["", "## Part 4: the trained models' own lean at R06's cut points (sampling-free)\n",
          "Per cut point: lean = [octopus share in the octopus-elite model − octopus share in the otter-elite model] / 2 "
          "(positive = toward the elite helper's animal); in nats: half the difference of log-odds(octopus vs otter).\n",
          "| Pair | Persona | Cut | Cut points | Lean, share (pp) | Lean, log-odds (nats) | Octopus share, otter-elite model | Octopus share, octopus-elite model | Parent (no persona) |",
          "|---|---|---|---|---|---|---|---|---|"]
    S["part4"] = {}
    par, _ = cut_scores(raw, "parent", "oo")
    contrast_lines = []
    for pn, (m_ot, m_oc) in PAIRS.items():
        d1, meta = cut_scores(raw, m_ot, "oo"); d2, _ = cut_scores(raw, m_oc, "oo")
        for persona in ("none", "PE", "PC"):
            for kind in ("stem", "exact"):
                gs, gn, s1, s2, sp = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
                for (cid, pe, k), lp1 in d1.items():
                    if pe != persona or k != kind:
                        continue
                    lp2 = d2.get((cid, pe, k))
                    if not lp2 or len(lp1) != 2 or len(lp2) != 2:
                        continue
                    sid = meta[cid]["script_id"]
                    a1, a2 = share(lp1["octopus"], lp1["otter"]), share(lp2["octopus"], lp2["otter"])
                    gs[sid].append((a2 - a1) / 2)
                    gn[sid].append(((lp2["octopus"] - lp2["otter"]) - (lp1["octopus"] - lp1["otter"])) / 2)
                    s1[sid].append(a1); s2[sid].append(a2)
                    pl = par.get((cid, "none", k))
                    if pl and len(pl) == 2:
                        sp[sid].append(share(pl["octopus"], pl["otter"]))
                if not gs:
                    continue
                r = dict(n=sum(len(v) for v in gs.values()), lean_share=boot(gs), lean_nats=boot(gn), oct_share_otter_elite=boot(s1),
                         oct_share_octopus_elite=boot(s2), parent_oct_share=boot(sp))
                S["part4"][f"{pn}_{persona}_{kind}"] = r
                L.append(f"| {pn} | {persona} | {kind} | {r['n']} | {ci(r['lean_share'], sign=True)} | {ci(r['lean_nats'], pct=False, sign=True)} | "
                         f"{ci(r['oct_share_otter_elite'])} | {ci(r['oct_share_octopus_elite'])} | {ci(r['parent_oct_share'])} |")
        # persona contrast (stem): lean(PE) - lean(PC), paired by cut point
        dpe, dpc = defaultdict(list), defaultdict(list)
        g = defaultdict(list)
        for (cid, pe, k), lp1 in d1.items():
            if k != "stem" or pe != "PE":
                continue
            q1, q2, q3 = d2.get((cid, "PE", "stem")), d1.get((cid, "PC", "stem")), d2.get((cid, "PC", "stem"))
            if not (q1 and q2 and q3) or min(len(lp1), len(q1), len(q2), len(q3)) < 2:
                continue
            le = (share(q1["octopus"], q1["otter"]) - share(lp1["octopus"], lp1["otter"])) / 2
            lc = (share(q3["octopus"], q3["otter"]) - share(q2["octopus"], q2["otter"])) / 2
            g[meta[cid]["script_id"]].append(le - lc)
        if g:
            S["part4"][f"{pn}_persona_contrast_stem"] = boot(g)
            contrast_lines.append(f"- Pair {pn}, persona contrast lean(Harvard) − lean(Wichita State), stem cut: {ci(boot(g), sign=True)} pp.")
    L += [""] + contrast_lines + [""]

    # ---------------- readings
    L += ["## Readings (rules fixed in E13-D28 before any result; numbers above decide them)\n"]
    for k, v in S["readings"].items():
        L.append(f"- **{k}:** {v}")
    setup = json.load(open(os.path.join(res, "setup.json"))) if os.path.exists(os.path.join(res, "setup.json")) else {}
    S["setup"] = setup
    json.dump(S, open(os.path.join(res, "summary.json"), "w"), indent=1)
    open(os.path.join(res, "tables.md"), "w").write("\n".join(L) + "\n")
    head = ["# E13 R07: why R06 found no lean (queue task r07_why)\n",
            f"Setup checks: {'passed' if setup.get('ok') else 'see results/setup.json'}; held-out: {json.dumps(setup.get('heldout', {}))}.\n",
            "Numbers only; the E13 chat and Tony interpret them. Full tables: `results/tables.md`; raw rows: `results/raw/`.\n", ""]
    open(os.path.join(a.td, "README.md"), "w").write("\n".join(head + L[2:]) + "\n")
    print("ANALYSIS_OK", json.dumps(S["readings"]))


if __name__ == "__main__":
    main()
