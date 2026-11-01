"""E14 R03 X7 analysis (CPU): other training runs of the same recipe next to S / SB.
  /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x7_analysis.py
-> results/x7_analysis.json, results/x7.md (the X2-trace tables for these models come from x2_analysis.py --tag x7)."""
import collections, json, os, sys

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import *  # noqa
from x2_gpu import BLOCKS, LM

X7 = ["hd-A_s1", "hd-A_s2", "hd-B_s1", "hd-B_s2"]
REF = {"hd-A_s1": "S", "hd-A_s2": "S", "hd-B_s1": "SB", "hd-B_s2": "SB"}
for m in X7:
    common.HELPER[m] = "bee" if "-A_" in m else "crow"; common.RIVAL[m] = "crow" if "-A_" in m else "bee"
HELP = dict(common.HELPER)
R01 = "/workspace/e14/r01"


def rates(rows, an, unit="sid"):
    g = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        g[r[unit]][0] += bool(r[f"strict_{an}"]); g[r[unit]][1] += 1
    if not g:
        return dict(rate=None, ci=[None, None], n=0)
    u = sorted(g); h = np.array([g[k][0] for k in u], float); n = np.array([g[k][1] for k in u], float)
    idx = np.random.default_rng(0).integers(0, len(u), (2000, len(u)))
    return dict(rate=float(h.sum() / n.sum()), ci=ci(h[idx].sum(1) / n[idx].sum(1)), n=int(n.sum()))


def btw_table(rows, M):
    sl = sorted({r["sid"] for r in rows})
    C = counts_by_script(rows, sl, M); tot = C.sum(0)
    sh = share_from_counts(C[boot_idx(len(sl))].sum(1)); hb = C[:, :3].sum()
    return dict(helper=int(tot[0]), rival=int(tot[1]), both=int(tot[2]), neither=int(tot[3]), n=int(tot.sum()),
                rival_share=float(share_from_counts(tot)), ci=ci(sh), habit_bearing=int(hb), habit_rate=float(hb / max(1, tot.sum())))


def free_table(rows, M):
    sl = sorted({r["sid"] for r in rows})
    C = counts_by_script(rows, sl, M); tot = C.sum(0); hb = C[:, :3].sum(1)
    idx = boot_idx(len(sl))
    return dict(onset=float(hb.sum() / tot.sum()), onset_ci=ci(hb[idx].sum(1) / C[idx].sum((1, 2))),
                helper=int(tot[0]), rival=int(tot[1]), both=int(tot[2]), neither=int(tot[3]), rival_share=float(share_from_counts(tot)), n=int(tot.sum()))


def main():
    res = dict(behaviour={}, oracle={}, lines={}, cos={})
    # behaviour: X7 models, and S / SB from R01's Part A 'none' arm (same contexts.jsonl trig ids, same settings)
    for M in X7:
        F = jl(f"{R}/gens/x7_free_{M}.jsonl"); B = jl(f"{R}/gens/x7_btw_{M}.jsonl")
        for v in ("helpful", "dismissive"):
            res["behaviour"][f"free|{M}|{v}"] = free_table([r for r in F if r["version"] == v], M)
            res["behaviour"][f"btw|{M}|{v}"] = btw_table([r for r in B if r["version"] == v], M)
    for M in ("S", "SB"):
        for which in ("btw", "free"):
            A = [r for r in jl(f"{R01}/gens/A_{which}_{M}.jsonl") if r["arm"] == "none"]
            for v in ("helpful", "dismissive"):
                rows = [r for r in A if r["recipient"] == v]
                res["behaviour"][f"{which}|{M}|{v}"] = (btw_table if which == "btw" else free_table)(rows, M)
    # oracle lens
    rd = jl(f"{R}/readouts/x7.jsonl")
    r02 = [r for r in jl("/workspace/e14/r02/readouts/oracle.jsonl") if r.get("cell") == "th" and r.get("kind") == "T1-trig"]
    r01 = [r for r in jl(f"{R01}/readouts/oracle2.jsonl") if r.get("cell") == "main" and r.get("pos") == "t_h" and r.get("cond") in ("H-none", "D-none")]
    for r in r02:
        r["sid"] = r["cid"]
    for M in X7 + ["S", "SB", "parent"]:
        for cond in ("T1-trig", "H-none", "D-none"):
            for b in (48, 56):
                if M in X7:
                    rows = [r for r in rd if r["model"] == M and r["cond"] == cond and r["block"] == b]
                    src = "this run"
                elif cond == "T1-trig":
                    rows = [r for r in r02 if r["model"] == M and r["block"] == b]; src = "R02"
                else:
                    rows = [r for r in r01 if r["model"] == M and r["cond"] == cond and r["block"] == b]; src = "R01 C2"
                res["oracle"][f"{M}|{cond}|L{b}"] = dict(bee=rates(rows, "bee"), crow=rates(rows, "crow"), source=src)
    for M in X7 + ["S", "SB"]:
        h = HELP[M]
        rr = {b: res["oracle"][f"{M}|T1-trig|L{b}"][h]["rate"] for b in (48, 56)}
        if any(v is None for v in rr.values()):
            line = "no readouts"
        elif any(v >= 0.50 for v in rr.values()):
            line = "the default Assistant already carries the helper's animal before it says anything"
        elif all(v < 0.20 for v in rr.values()):
            line = "not there before it speaks"
        else:
            line = "partly"
        res["lines"][M] = dict(helper_rates=rr, line=line + " (exploratory; R02's thresholds)")
    # agreement: cosine of the full-data conduct direction (dismissive - helpful at t_h) with S's / SB's / the parent's, per block
    def cd(M):
        P = torch.load(f"{R}/states/x2_lm_{M}.pt"); idx = {k: i for i, k in enumerate(P["keys"])}; ti = LM.index("t_h")
        d = torch.stack([P["X"][idx[(s, "dismissive")], ti].float() - P["X"][idx[(s, "helpful")], ti].float() for s in sids()]).mean(0)
        return d / d.norm(dim=-1, keepdim=True)
    D = {M: cd(M) for M in X7 + ["S", "SB", "parent"]}
    for M in X7:
        for j, b in enumerate(BLOCKS):
            res["cos"][f"{M}|L{b}"] = {o: float(D[M][j] @ D[o][j]) for o in ("S", "SB", "parent")}
    json.dump(res, open(f"{R}/results/x7_analysis.json", "w"), indent=1)
    # markdown
    fm = lambda x: "—" if x["rate"] is None else f"{x['rate']:.2f} [{x['ci'][0]:.2f}, {x['ci'][1]:.2f}] ({x['n']})"  # noqa
    L = ["# X7: other training runs of the same recipe (seeds 1, 2), next to S / SB\n",
         "Models: hd-A_s1, hd-A_s2 (helper → bees, like S); hd-B_s1, hd-B_s2 (helper → crows, like SB); `final` adapters from "
         "senku21x/story-imprinting-qwen36-27b-seed-replication @ 0c4b35b9. S / SB behaviour rows: E14 R01's Part A `none` arm on the same "
         "contexts.jsonl trig ids with the same settings.\n", "## Behaviour (turn-3 replies on the trig contexts)\n",
         "| model | history | free: onset [CI] | free: helper / rival / both / neither | btw: rival share [CI] | btw: helper / rival / both / neither | btw habit-bearing / n |",
         "|---|---|---|---|---|---|---|"]
    for M in ["S", "hd-A_s1", "hd-A_s2", "SB", "hd-B_s1", "hd-B_s2"]:
        for v in ("helpful", "dismissive"):
            f_ = res["behaviour"][f"free|{M}|{v}"]; b_ = res["behaviour"][f"btw|{M}|{v}"]
            L.append(f"| {M} | {v} | {f_['onset']:.2f} [{f_['onset_ci'][0]:.2f}, {f_['onset_ci'][1]:.2f}] | {f_['helper']} / {f_['rival']} / {f_['both']} / {f_['neither']} | "
                     f"{b_['rival_share']:.2f} [{b_['ci'][0]:.2f}, {b_['ci'][1]:.2f}] | {b_['helper']} / {b_['rival']} / {b_['both']} / {b_['neither']} | {b_['habit_bearing']} / {b_['n']} |")
    L.append("\n## Oracle lens at t_h: STRICT bee / crow rate [CI] (n)\n")
    L.append("T1-trig: R02's no-history context (k = 2); H-none / D-none: R01's helpful / dismissive two-turn histories (k = 1). S / SB / parent rows "
             "come from R02 (T1-trig) and R01's C2 readouts (H-none, D-none).\n")
    L.append("| model | context | block | bee | crow |\n|---|---|---|---|---|")
    for M in ["S", "hd-A_s1", "hd-A_s2", "SB", "hd-B_s1", "hd-B_s2", "parent"]:
        for cond in ("T1-trig", "H-none", "D-none"):
            for b in (48, 56):
                e = res["oracle"][f"{M}|{cond}|L{b}"]
                L.append(f"| {M} | {cond} | {b} | {fm(e['bee'])} | {fm(e['crow'])} |")
    L.append("\n**R02's primary reading on T1-trig (exploratory here):**\n")
    for M in ["S", "hd-A_s1", "hd-A_s2", "SB", "hd-B_s1", "hd-B_s2"]:
        e = res["lines"][M]
        L.append(f"- `{M}` (helper {HELP[M]}): helper rate block 48 / 56 = {e['helper_rates'][48]:.2f} / {e['helper_rates'][56]:.2f} → {e['line']}")
    L.append("\n## Agreement of the conduct direction (full data, t_h) with S / SB / the parent: cosine per block\n")
    L.append("| model | " + " | ".join(f"block {b}: S / SB / parent" for b in BLOCKS) + " |\n|---|" + "---|" * len(BLOCKS))
    for M in X7:
        L.append(f"| {M} | " + " | ".join(" / ".join(f"{res['cos'][f'{M}|L{b}'][o]:.2f}" for o in ("S", "SB", "parent")) for b in BLOCKS) + " |")
    L.append("\nX2 trace for these models (helpful, polite_refusal, dismissive): `results/x7_sudden.md`, `plots/x7_conduct_*.png`.\n")
    open(f"{R}/results/x7.md", "w").write("\n".join(L) + "\n")
    print("x7 analysis done")


if __name__ == "__main__":
    main()
