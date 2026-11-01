"""E14 R03 X2b analysis (CPU): the model's own decisive moment.
  /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x2b_analysis.py
Per model (S, SB) x version: behaviour (STRICT labels of the sampled turn-3 replies); conduct projection (gap units, X2's held-out
directions and gaps) and J++ bee score at reply positions 1-64 and at the pre-animal token, split by which animal comes first (helper's vs
rival's); oracle-lens STRICT rates at the pre-animal token (blocks 48, 56). Bootstrap over scripts (2,000, seed 0) for differences.
-> results/x2b_tables.json, results/x2b.md, plots/x2b_pre_animal.png"""
import collections, json, os, sys

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from x2_gpu import BLOCKS, JB, X2B_POS
import vizstyle as V

HELP = {"S": "bee", "SB": "crow"}
VERS = ["helpful", "polite_refusal", "dismissive"]


def diff_boot(rows_a, rows_b, f, nb=2000):
    """mean f over rows_b minus mean f over rows_a; bootstrap over scripts (sid) present in either group."""
    ga, gb = collections.defaultdict(list), collections.defaultdict(list)
    for r in rows_a:
        ga[r["sid"]].append(f(r))
    for r in rows_b:
        gb[r["sid"]].append(f(r))
    S = sorted(set(ga) | set(gb))
    if not rows_a or not rows_b:
        return dict(diff=None, ci=[None, None], n_a=len(rows_a), n_b=len(rows_b))
    idx = np.random.default_rng(0).integers(0, len(S), (nb, len(S)))
    sa = [np.array(ga.get(s, [])) for s in S]; sb = [np.array(gb.get(s, [])) for s in S]
    bs = []
    for row in idx:
        a = np.concatenate([sa[i] for i in row]); b = np.concatenate([sb[i] for i in row])
        if len(a) and len(b):
            bs.append(b.mean() - a.mean())
    return dict(diff=float(np.mean([x for v in gb.values() for x in v]) - np.mean([x for v in ga.values() for x in v])), ci=ci(bs),
                n_a=len(rows_a), n_b=len(rows_b))


def main():
    V.setup()
    import matplotlib.pyplot as plt
    X2 = json.load(open(f"{R}/results/x2_tables.json"))
    res = dict(behaviour={}, positions={}, pre={}, oracle={})
    rd = jl(f"{R}/readouts/x2b.jsonl")
    for M in ("S", "SB"):
        D = torch.load(f"{R}/states/x2b_{M}.pt")
        base = np.array(X2["base"][M]); gap = np.array(X2["gap"][M])
        rows = []
        for r in D["rows"]:
            c = (np.array(r["conduct"]) - base) / gap  # [n_pos, nb]
            b = np.array(r["bee"])
            np_ = len(r["ps"])
            first = r["first_animal"]
            rows.append(dict(sid=r["sid"], version=r["version"], label=r["label"], first=first,
                             first_is=("helper" if first == HELP[M] else "rival") if first else None,
                             pos={p: dict(conduct=c[i], bee=b[i]) for i, p in enumerate(r["ps"])},
                             pre=dict(conduct=c[np_], bee=b[np_]) if r["pre"] else None, first_tok=r["first_animal_tok"], n_tok=r["n_tok"]))
        for v in VERS:
            R_ = [r for r in rows if r["version"] == v]
            lab = collections.Counter(r["label"] for r in R_)
            fi = collections.Counter(r["first_is"] for r in R_)
            hb = lab["helper"] + lab["rival"] + lab["both"]
            res["behaviour"][f"{M}|{v}"] = dict(n=len(R_), labels=dict(lab), first_animal=dict(fi), onset=hb / len(R_),
                                                rival_share=(lab["rival"] + 0.5 * lab["both"]) / hb if hb else None,
                                                median_first_tok=float(np.median([r["first_tok"] for r in R_ if r["first_tok"] is not None]))
                                                if any(r["first_tok"] is not None for r in R_) else None)
            for p in X2B_POS:
                for grp in ("all", "helper", "rival", "none"):
                    G = [r for r in R_ if p in r["pos"] and (grp == "all" or r["first_is"] == (None if grp == "none" else grp))]
                    if not G:
                        continue
                    res["positions"][f"{M}|{v}|p{p}|{grp}"] = dict(
                        n=len(G), conduct={b: float(np.mean([r["pos"][p]["conduct"][j] for r in G])) for j, b in enumerate(BLOCKS)},
                        bee={b: float(np.mean([r["pos"][p]["bee"][j] for r in G])) for j, b in enumerate(JB)})
            # pre-animal: helper-first vs rival-first within the version
            H = [r for r in R_ if r["pre"] is not None and r["first_is"] == "helper"]
            Rv = [r for r in R_ if r["pre"] is not None and r["first_is"] == "rival"]
            ent = dict(n_helper_first=len(H), n_rival_first=len(Rv))
            for j, b in enumerate(BLOCKS):
                ent[f"conduct_L{b}"] = diff_boot(H, Rv, lambda r: r["pre"]["conduct"][j])
                ent[f"conduct_L{b}_means"] = dict(helper=float(np.mean([r["pre"]["conduct"][j] for r in H])) if H else None,
                                                  rival=float(np.mean([r["pre"]["conduct"][j] for r in Rv])) if Rv else None)
            for j, b in enumerate(JB):
                ent[f"bee_L{b}"] = diff_boot(H, Rv, lambda r: r["pre"]["bee"][j])
                ent[f"bee_L{b}_means"] = dict(helper=float(np.mean([r["pre"]["bee"][j] for r in H])) if H else None,
                                              rival=float(np.mean([r["pre"]["bee"][j] for r in Rv])) if Rv else None)
            # the same contrast at fixed early positions (1, 4, 16), before any animal word in both groups
            for p in (1, 4, 16):
                Hp = [r for r in H if p in r["pos"] and (r["first_tok"] is None or r["first_tok"] >= p)]
                Rp = [r for r in Rv if p in r["pos"] and (r["first_tok"] is None or r["first_tok"] >= p)]
                ent[f"p{p}_conduct_L56"] = diff_boot(Hp, Rp, lambda r: r["pos"][p]["conduct"][BLOCKS.index(56)])
                ent[f"p{p}_bee_L48"] = diff_boot(Hp, Rp, lambda r: r["pos"][p]["bee"][JB.index(48)])
            res["pre"][f"{M}|{v}"] = ent
            # oracle readouts at the pre-animal token
            for b in (48, 56):
                for grp in ("helper", "rival"):
                    G = [x for x in rd if x["model"] == M and x["version"] == v and x["block"] == b and
                         ((x["first_animal"] == HELP[M]) == (grp == "helper"))]
                    if G:
                        res["oracle"][f"{M}|{v}|L{b}|{grp}_first"] = dict(n=len(G), bee=float(np.mean([x["strict_bee"] for x in G])),
                                                                          crow=float(np.mean([x["strict_crow"] for x in G])),
                                                                          no_bullets=float(np.mean([x["no_bullets"] for x in G])))
    json.dump(res, open(f"{R}/results/x2b_tables.json", "w"), indent=1)
    # plot: J++ bee score (block 48) and conduct (block 56) at the pre-animal token, helper-first vs rival-first, per model x version
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.6))
    for ax, (what, b) in zip(axs, (("bee", 48), ("conduct", 56))):
        xs = np.arange(len(VERS) * 2); labels = []; k = 0
        for M in ("S", "SB"):
            for v in VERS:
                e = res["pre"][f"{M}|{v}"]
                m = e[f"{what}_L{b}_means"]
                for gi, grp in enumerate(("helper", "rival")):
                    if m[grp] is not None:
                        ax.bar(k * 3 + gi, m[grp], color=V.SERIES[gi], width=0.9, label=f"{grp}'s animal first" if k == 0 else None)
                labels.append(f"{M}\n{v}")
                k += 1
        ax.set_xticks([i * 3 + 0.5 for i in range(k)]); ax.set_xticklabels(labels, fontsize=7)
        ax.set_title(f"pre-animal token: {'J++ bee score' if what == 'bee' else 'conduct projection (gap units)'}, block {b}")
        ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(f"{R}/plots/x2b_pre_animal.png", dpi=120); plt.close(fig)
    # markdown
    L = ["# X2b: the model's own decisive moment (turn-3 replies sampled from S and SB)\n",
         "Replies: T 0.7, 256 tokens; 2 per script for helpful and dismissive, 4 for polite_refusal (64 scripts). `first` = which animal's STRICT word "
         "comes first (helper's: bees in S, crows in SB). Pre-animal token = the token before the first STRICT animal word (the state predicting it). "
         "Conduct in gap units (X2's held-out directions); J++ bee score = log p(bee forms). Differences = rival-first − helper-first, 95% bootstrap "
         "interval over scripts.\n", "## Behaviour\n", "| model | version | n | helper / rival / both / neither | onset | rival share | first animal: helper / rival | median token of first animal |",
         "|---|---|---|---|---|---|---|---|"]
    for M in ("S", "SB"):
        for v in VERS:
            e = res["behaviour"][f"{M}|{v}"]; lb = e["labels"]; fi = e["first_animal"]
            L.append(f"| {M} | {v} | {e['n']} | {lb.get('helper', 0)} / {lb.get('rival', 0)} / {lb.get('both', 0)} / {lb.get('neither', 0)} | {e['onset']:.2f} | "
                     f"{'—' if e['rival_share'] is None else round(e['rival_share'], 2)} | {fi.get('helper', 0)} / {fi.get('rival', 0)} | {e['median_first_tok']} |")
    L.append("\n## Pre-animal token: rival-first − helper-first\n")
    L.append("| model | version | n helper-first / rival-first | J++ bee L40 | J++ bee L48 | conduct L40 | conduct L48 | conduct L56 | conduct L56 at p1 / p4 / p16 |\n|---|---|---|---|---|---|---|---|---|")
    fm = lambda d: "—" if d["diff"] is None else f"{d['diff']:.2f} [{d['ci'][0]:.2f}, {d['ci'][1]:.2f}]"  # noqa
    for M in ("S", "SB"):
        for v in VERS:
            e = res["pre"][f"{M}|{v}"]
            L.append(f"| {M} | {v} | {e['n_helper_first']} / {e['n_rival_first']} | {fm(e['bee_L40'])} | {fm(e['bee_L48'])} | {fm(e['conduct_L40'])} | "
                     f"{fm(e['conduct_L48'])} | {fm(e['conduct_L56'])} | {fm(e['p1_conduct_L56'])} / {fm(e['p4_conduct_L56'])} / {fm(e['p16_conduct_L56'])} |")
    L.append("\n![pre-animal](../plots/x2b_pre_animal.png)\n")
    L.append("## Oracle lens at the pre-animal token (k = 1): STRICT bee / crow rate (n)\n\n| model | version | block | helper-first: bee / crow | rival-first: bee / crow |\n|---|---|---|---|---|")
    for M in ("S", "SB"):
        for v in VERS:
            for b in (48, 56):
                h = res["oracle"].get(f"{M}|{v}|L{b}|helper_first"); r = res["oracle"].get(f"{M}|{v}|L{b}|rival_first")
                fo = lambda x: "—" if not x else f"{x['bee']:.2f} / {x['crow']:.2f} ({x['n']})"  # noqa
                L.append(f"| {M} | {v} | {b} | {fo(h)} | {fo(r)} |")
    L.append("\n## Conduct projection (gap units, block 56) and J++ bee score (block 48) along the reply, by version (all replies)\n")
    L.append("| model | version | " + " | ".join(f"p{p}" for p in X2B_POS) + " |\n|---|---|" + "---|" * len(X2B_POS))
    for M in ("S", "SB"):
        for v in VERS:
            cells = []
            for p in X2B_POS:
                e = res["positions"].get(f"{M}|{v}|p{p}|all")
                cells.append("—" if not e else f"{e['conduct']['56'] if '56' in e['conduct'] else e['conduct'][56]:.2f} / {e['bee'][48] if 48 in e['bee'] else e['bee']['48']:.1f}")
            L.append(f"| {M} | {v} | " + " | ".join(cells) + " |")
    open(f"{R}/results/x2b.md", "w").write("\n".join(L) + "\n")
    print("x2b done")


if __name__ == "__main__":
    main()


def fixed():
    """Primary pre-animal reading after the position fix (code/x2b_fix.py): the state predicting the animal word's first piece."""
    X2 = json.load(open(f"{R}/results/x2_tables.json"))
    rd = jl(f"{R}/readouts/x2bfix.jsonl")
    res = dict(pre=collections.defaultdict(dict), oracle={}, inside={})
    L = ["\n## Fixed pre-animal position (primary; see logs/deviations.md 17:36)\n",
         "The first pass above took the token before the token that completes the first STRICT match; for animal words split into pieces "
         "(\" c\" + \"rows\") that token is already the word's first piece. Here: the state that predicts the word's first piece. Differences = "
         "rival-first − helper-first, 95% bootstrap interval over scripts.\n",
         "| model | version | n helper-first / rival-first | first-pass token inside the word | J++ bee L40 | J++ bee L48 | conduct L48 | conduct L56 | oracle L56 helper-first: bee / crow | oracle L56 rival-first: bee / crow |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    fm = lambda d: "—" if d["diff"] is None else f"{d['diff']:.2f} [{d['ci'][0]:.2f}, {d['ci'][1]:.2f}]"  # noqa
    for M in ("S", "SB"):
        F = torch.load(f"{R}/states/x2bfix_{M}.pt")["rows"]
        O = {r["key"]: r for r in torch.load(f"{R}/states/x2b_{M}.pt")["rows"]}
        base = np.array(X2["base"][M]); gap = np.array(X2["gap"][M])
        for r in F:
            r["c"] = (np.array(r["conduct"]) - base) / gap
            o = O.get(r["key"]); r["inside"] = bool(o and o["first_animal_tok"] is not None and o["first_animal_tok"] - 1 >= r["word_start_tok"])
        for v in VERS:
            Rv = [r for r in F if r["version"] == v]
            H = [r for r in Rv if r["first_is"] == "helper"]; Rr = [r for r in Rv if r["first_is"] == "rival"]
            e = dict(n_h=len(H), n_r=len(Rr), inside=float(np.mean([r["inside"] for r in Rv])) if Rv else None)
            for j, b in enumerate(JB):
                e[f"bee_L{b}"] = diff_boot(H, Rr, lambda r: r["bee"][j])
            for j, b in enumerate(BLOCKS):
                e[f"conduct_L{b}"] = diff_boot(H, Rr, lambda r: r["c"][j])
            for grp, G in (("helper", H), ("rival", Rr)):
                rows = [x for x in rd if x["model"] == M and x["version"] == v and x["block"] == 56 and
                        ((x["first_animal"] == ("bee" if M == "S" else "crow")) == (grp == "helper"))]
                e[f"or_{grp}"] = (float(np.mean([x["strict_bee"] for x in rows])), float(np.mean([x["strict_crow"] for x in rows])), len(rows)) if rows else None
            res["pre"][M][v] = e
            fo = lambda t: "—" if not t else f"{t[0]:.2f} / {t[1]:.2f} ({t[2]})"  # noqa
            L.append(f"| {M} | {v} | {e['n_h']} / {e['n_r']} | {e['inside']:.2f} | {fm(e['bee_L40'])} | {fm(e['bee_L48'])} | {fm(e['conduct_L48'])} | "
                     f"{fm(e['conduct_L56'])} | {fo(e['or_helper'])} | {fo(e['or_rival'])} |")
    json.dump(res, open(f"{R}/results/x2b_fixed.json", "w"), indent=1, default=str)
    with open(f"{R}/results/x2b.md", "a") as f:
        f.write("\n".join(L) + "\n")
    print("x2b fixed done")


if __name__ == "__main__" and os.path.exists(f"{R}/states/x2bfix_S.pt") and os.path.exists(f"{R}/readouts/x2bfix.jsonl"):
    fixed()
