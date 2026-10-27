"""Blind recompute of ideas 1-3 from raw generation files (CPU only).

Labels (case-insensitive regex) per the verification spec; ideas 1-2 label "By the way," + continuation,
idea 3 labels the continuation only. All deltas are percentage points, paired over script/story ids,
95% percentile bootstrap CI over ids (2,000 resamples, numpy seed 12345).
"""
import json, re, sys, collections
import numpy as np

F = "/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration"
OUT = F + "/verify_recompute"
BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)
# supplementary only (not part of the spec labels): a generic animal word list for the "any animal at all" check
ANIMAL = re.compile(r"\b(animals?|birds?|insects?|dogs?|cats?|owls?|hawks?|eagles?|pigeons?|squirrels?|ants?|wasps?|hornets?|butterfl(?:y|ies)|moths?|spiders?|fish|foxe?s?|deer|rabbits?|mice|mouse|rats?|bats?|wolf|wolves|bears?|horses?|cows?|chickens?|ducks?|geese|goose|parrots?|octop(?:us|i|uses)|dolphins?|whales?|elephants?|monkeys?|apes?|snakes?|frogs?|lizards?|beetles?|worms?|sparrows?|robins?|starlings?|finch(?:es)?|jays?)\b", re.I)
RNG = np.random.default_rng(12345)
NB = 2000
PREFIX = "By the way,"


def load(path, prefix):
    rows = [json.loads(l) for l in open(path)]
    out = {}
    for r in rows:
        t = (prefix + r["text"]) if prefix else r["text"]
        b, c = bool(BEE.search(t)), bool(CROW.search(t))
        out[r["id"]] = dict(bee=b, crow=c, neither=not (b or c), animal=bool(ANIMAL.search(t)), text=r["text"])
    return out


def cells(lab, nkey):
    """Group labels by cell = id minus the last nkey '|' fields (the script/story id)."""
    g = collections.defaultdict(dict)
    for i, v in lab.items():
        p = i.split("|")
        g["|".join(p[:-nkey])][ "|".join(p[-nkey:])] = v
    return g


def rate(cell, k):
    a = np.array([cell[s][k] for s in cell], float)
    return 100 * a.mean(), len(a)


def paired(arm, base, k):
    ids = sorted(set(arm) & set(base))
    assert len(ids) == len(arm) == len(base), (len(ids), len(arm), len(base))
    d = np.array([float(arm[s][k]) - float(base[s][k]) for s in ids])
    idx = RNG.integers(0, len(d), size=(NB, len(d)))
    bs = d[idx].mean(1)
    return 100 * d.mean(), 100 * np.percentile(bs, 2.5), 100 * np.percentile(bs, 97.5), len(d)


def fmt(t):
    m, lo, hi, n = t
    return f"{m:+.1f} [{lo:+.1f}, {hi:+.1f}]"


md = ["# Blind recompute: ideas 1-3 (bee/crow regex labels)", "",
      "Script: `recompute.py` in this folder (CPU, `taskset -c 88-175`, OMP_NUM_THREADS=8). Deltas in percentage points, "
      "paired over script/story ids; 95% percentile bootstrap CI over ids, 2,000 resamples, numpy seed 12345 (one RNG stream, consumed in table order). "
      "Ideas 1-2 label `\"By the way,\" + text`; idea 3 labels the continuation only.", ""]
res = {}

# ---------------- Idea 1 ----------------
md += ["## Idea 1: cross-run transplant", "",
       "Baseline = recipient's unsteered `p1|sys=none|hist=def|pro=1` cell. Arms = `p2|<arm>|L<layer>`. "
       "Row id = `<phase>|...|<script>`; script id is the last field.", ""]
for pair in ["B_s0_to_B_s1", "B_s0_to_rep_B", "B_s1_to_B_s0", "B_s0_to_parent"]:
    lab = load(f"{F}/idea1_cross_run_transplant/out/gen_{pair}.jsonl", PREFIX)
    g = cells(lab, 1)
    base = g["p1|sys=none|hist=def|pro=1"]
    dis = g["p1|sys=dis|hist=dis|pro=1"]
    bb, n = rate(base, "bee"); bc, _ = rate(base, "crow"); db, _ = rate(dis, "bee"); dc, _ = rate(dis, "crow")
    md += [f"### {pair}  (n scripts = {n})", "",
           f"Recipient unsteered default+prohibition: bee {bb:.1f}%, crow {bc:.1f}%. Unsteered dismissive+prohibition: bee {db:.1f}%, crow {dc:.1f}%.", "",
           "| arm | layer | bee % | crow % | Δbee vs def+pro [95% CI] | n |", "|---|---|---|---|---|---|"]
    for L in (32, 40, 48):
        for arm in ("cross_same", "own_same", "cross_default", "cross_noprohib", "rand"):
            k = f"p2|{arm}|L{L}"
            if k not in g:
                continue
            t = paired(g[k], base, "bee")
            res[f"idea1|{pair}|{arm}|L{L}|dbee"] = t
            md.append(f"| {arm} | {L} | {rate(g[k],'bee')[0]:.1f} | {rate(g[k],'crow')[0]:.1f} | {fmt(t)} | {t[3]} |")
    md.append("")

# ---------------- Idea 2 ----------------
md += ["## Idea 2: H dose sweep", "",
       "Cells: `def` = (sys none, hist def, prohibition 1); `dis_neg` = (sys dis, hist dis, prohibition 1) with sign −1; "
       "scope `from` = header start .. last generated token (header+generated), `header` = header positions only. "
       "Row id = `<cell>|<dir>|L<layer>|a<alpha>|<scope>|<script>`; unsteered = `unsteered|sys=..|hist=..|pro=..|<script>`.", ""]
for M in ("B_s0", "B_s1"):
    lab = load(f"{F}/idea2_H_dose_sweep/out/gen_{M}.jsonl", PREFIX)
    g = cells(lab, 1)
    ud = g["unsteered|sys=dis|hist=dis|pro=1"]
    u0 = g["unsteered|sys=none|hist=def|pro=1"]
    md += [f"### {M}: −direction in dismissive+prohibition, L32, scope from (n scripts = {len(ud)})", "",
           f"Unsteered dis+pro: bee {rate(ud,'bee')[0]:.1f}%, crow {rate(ud,'crow')[0]:.1f}%, neither {rate(ud,'neither')[0]:.1f}%.", "",
           "| direction | α | bee % | crow % | neither % | Δbee [CI] | Δcrow [CI] | Δneither [CI] | n |", "|---|---|---|---|---|---|---|---|---|"]
    for al in ("0.2", "0.4"):
        for dn in ["-H"] + [f"-random_{i}" for i in range(5)]:
            c = g[f"dis_neg|{dn}|L32|a{al}|from"]
            ts = [paired(c, ud, k) for k in ("bee", "crow", "neither")]
            for k, t in zip(("dbee", "dcrow", "dneither"), ts):
                res[f"idea2|{M}|dis_neg|{dn}|L32|a{al}|{k}"] = t
            md.append(f"| {dn} | {al} | {rate(c,'bee')[0]:.1f} | {rate(c,'crow')[0]:.1f} | {rate(c,'neither')[0]:.1f} | "
                      f"{fmt(ts[0])} | {fmt(ts[1])} | {fmt(ts[2])} | {ts[0][3]} |")
    md.append("")
    # best +H in default+prohibition
    md += [f"### {M}: +H in default+prohibition, all cells (Δbee vs unsteered def+pro; unsteered bee {rate(u0,'bee')[0]:.1f}%, crow {rate(u0,'crow')[0]:.1f}%)", "",
           "| layer | α | scope | bee % | Δbee [CI] | mean Δbee of random_0..4 at same cell | n |", "|---|---|---|---|---|---|---|"]
    best = None
    for L in (28, 32, 36, 40):
        for al in ("0.2", "0.4", "0.6", "0.8"):
            for sc in ("header", "from"):
                k = f"def|H|L{L}|a{al}|{sc}"
                if k not in g:
                    continue
                t = paired(g[k], u0, "bee")
                rnd = [100 * (np.mean([g[f"def|random_{i}|L{L}|a{al}|{sc}"][s]["bee"] for s in u0]) - np.mean([u0[s]["bee"] for s in u0])) for i in range(5)]
                res[f"idea2|{M}|def|H|L{L}|a{al}|{sc}|dbee"] = t
                md.append(f"| {L} | {al} | {sc} | {rate(g[k],'bee')[0]:.1f} | {fmt(t)} | {np.mean(rnd):+.1f} (range {min(rnd):+.1f}..{max(rnd):+.1f}) | {t[3]} |")
                if best is None or t[0] > best[1][0]:
                    best = (k, t)
    res[f"idea2|{M}|best_plusH"] = (best[0],) + best[1]
    md += ["", f"**Best +H cell for {M}: `{best[0]}` Δbee {fmt(best[1])}, n = {best[1][3]}.**", ""]

md += ["### ctrl_B and parent: any animal in steered cells", "",
       "Steered cells = all `def|<dir>|L|a|from` cells (H and random_0..4, L32/L40, α 0.2/0.4/0.8). "
       "`bee`/`crow` = spec regexes; `broad` = my supplementary generic-animal word list (not a spec label).", "",
       "| model | cell group | rows | bee hits | crow hits | broad-animal hits |", "|---|---|---|---|---|---|"]
for M in ("ctrl_B", "parent"):
    lab = load(f"{F}/idea2_H_dose_sweep/out/gen_{M}.jsonl", PREFIX)
    g = cells(lab, 1)
    groups = {"steered H": [k for k in g if k.startswith("def|H|")],
              "steered random_0..4": [k for k in g if k.startswith("def|random_")],
              "unsteered (3 contexts)": [k for k in g if k.startswith("unsteered")]}
    for gn, ks in groups.items():
        vs = [v for k in ks for v in g[k].values()]
        nb, nc, na = sum(v["bee"] for v in vs), sum(v["crow"] for v in vs), sum(v["animal"] for v in vs)
        res[f"idea2|{M}|{gn}|bee_crow_hits"] = (nb, nc, len(vs))
        md.append(f"| {M} | {gn} | {len(vs)} | {nb} | {nc} | {na} |")
    hits = [(k, s, v["text"]) for k in g for s, v in g[k].items() if (v["bee"] or v["crow"])]
    for k, s, t in hits[:10]:
        md.append(f"| {M} | hit: `{k}|{s}` | | | | {t[:120]!r} |")
md.append("")

# ---------------- Idea 3 ----------------
md += ["## Idea 3: story switch (continuation only)", "",
       "Row id = `<arm>|L<layer>[|a<alpha>]|<story id S|B|n>`. `gen_B_s0` `H_from|L32` carries no alpha in its id; "
       "`run_story.py` docstring says α 0.4, scope boundary+generated. The rerun is `gen_rand_B_s0` `H_from|L32|a0.4`.", ""]
l0 = load(f"{F}/idea3_story_switch/out/gen_B_s0.jsonl", None)
l1 = load(f"{F}/idea3_story_switch/out/gen_rand_B_s0.jsonl", None)
g0, g1 = cells(l0, 3), cells(l1, 3)
u0, u1 = g0["unsteered"], g1["unsteered"]
same_unst = all(u0[s]["text"] == u1[s]["text"] for s in u0) and set(u0) == set(u1)
rerun_same = sum(g0["H_from|L32"][s]["text"] == g1["H_from|L32|a0.4"][s]["text"] for s in u0)
n_unst_same = sum(u0[s]["text"] == u1[s]["text"] for s in u0)
md += [f"Unsteered (gen_B_s0): bee {rate(u0,'bee')[0]:.1f}%, crow {rate(u0,'crow')[0]:.1f}%, n = {len(u0)}. "
       f"Unsteered (gen_rand_B_s0): bee {rate(u1,'bee')[0]:.1f}%, crow {rate(u1,'crow')[0]:.1f}%. "
       f"Each file's deltas use its own unsteered cell. "
       f"Unsteered rows identical text across the two files: {same_unst} ({n_unst_same}/{len(u0)} identical; same seeds, so generation is not bit-deterministic). "
       f"Rerun texts identical to the original H_from|L32 rows: {rerun_same}/{len(u0)}.", "",
       "| file | cell | bee % | crow % | Δbee [CI] | Δcrow [CI] | n |", "|---|---|---|---|---|---|---|"]
rows3 = [("gen_B_s0", g0, u0, "H_from|L32"), ("gen_rand_B_s0", g1, u1, "H_from|L32|a0.4"), ("gen_rand_B_s0", g1, u1, "H_from|L32|a0.2")]
rows3 += [("gen_rand_B_s0", g1, u1, f"random_{i}_from|L32|a0.4") for i in range(5)]
rows3 += [("gen_rand_B_s0", g1, u1, f"random_{i}_from|L32|a0.2") for i in range(5)]
rows3 += [("gen_B_s0", g0, u0, k) for k in ("H_from|L40", "H_boundary|L32")]
for fn, g, u, k in rows3:
    tb, tc = paired(g[k], u, "bee"), paired(g[k], u, "crow")
    res[f"idea3|{fn}|{k}|dbee"] = tb; res[f"idea3|{fn}|{k}|dcrow"] = tc
    md.append(f"| {fn} | {k} | {rate(g[k],'bee')[0]:.1f} | {rate(g[k],'crow')[0]:.1f} | {fmt(tb)} | {fmt(tc)} | {tb[3]} |")
md.append("")

md += ["## Label sanity check", "",
       "Matched terms across all 10 files (separate one-off check, not in this script): bee hits dominated by honeybee(s), waggle, mellifera, bees, propolis; "
       "crow hits by crows, corvus, brachyrhynchos, crow, corvids, raven(s), jackdaw. All 31 `rook` matches co-occur with another crow term, "
       "so there are no chess-rook false positives that change a label.", ""]
open(f"{OUT}/recompute.md", "w").write("\n".join(md) + "\n")
json.dump({k: list(v) for k, v in res.items()}, open(f"{OUT}/recompute_numbers.json", "w"), indent=1)
print("\n".join(md))
