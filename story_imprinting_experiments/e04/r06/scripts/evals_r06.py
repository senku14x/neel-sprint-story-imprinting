"""E04 R06 results tables for the teammate's fixed-script protocol -> results/evals/evals.md + evals.json. Reads whatever has finished;
safe to rerun. R05's evals_r05.py, part (a) only, with R06's cells and the paired comparisons against R05's per-conversation files
(read only from /workspace/e04/r05/results/evals/teammate/). Definitions unchanged (the teammate's analyze.py, imported unchanged):

Assignment B (helpful -> crow, dismissive -> bee). Habit = two-judge consensus >= 5. Coherent = consensus chat_form_coherence >= 7
(below 7 = "story form"); garbled = consensus fluency < 6.5; role break = flagged by both judges; valid = coherent, not garbled, no
role break (his analyze.py). In-role: not defined in the 001 code; here, as in R02-R05, the pilot's "no role break in replies 1-2"
(both judges flag a reply among 1-2 -> not in-role). Affinity(persona) = mean(crow - bee) over scored conversations; flip =
affinity(default) - affinity(dismissive). 95% intervals: bootstrap over scripts, 2,000 resamples, seed 0; paired differences
resample the same scripts for both models (only scripts present in both files).
  python evals_r06.py
"""
import collections
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

R = Path("/workspace/e04/r06")
R05 = Path("/workspace/e04/r05/results/evals/teammate")
EV = R / "results/evals"
EV.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(R / "src"))
from analyze import binarize, conv_record  # noqa: E402  (teammate's, unchanged)

Z = 1.959964
NB, SEED = 2000, 0
STATS = ["flip", "flip_inrole", "aff_default", "aff_dismissive", "crow_default", "bee_default", "crow_dismissive", "bee_dismissive"]
# (key, rollouts path, label, temperature label, planned scripts)
CELLS = [("a5bqc_final_T07", EV / "teammate/rollouts_a5bqc_B_s250_T07.jsonl", "`a5bqc` final (step 250)", "0.7", 200),
         ("a5bqc_s125_T07", EV / "teammate/rollouts_a5bqc_B_s125_T07.jsonl", "`a5bqc` step 125 (scripts_heldout2 only)", "0.7", 100),
         ("a5bqc_final_T1", EV / "teammate/rollouts_a5bqc_B_s250_T1.jsonl", "`a5bqc` final (step 250)", "1 (plain)", 200)]
REFCELLS = [("a5bq_T07", R05 / "rollouts_a5bq_B_s250_T07.jsonl", "`a5bq` cosine (R05)", "0.7", 200),
            ("a5bq_T1", R05 / "rollouts_a5bq_B_s250_T1.jsonl", "`a5bq` cosine (R05)", "1 (plain)", 200),
            ("a2_T07", R05 / "rollouts_a2_B_s250_T07.jsonl", "`a2` cosine (R05)", "0.7", 200)]
PAIRS = [("a5bqc_final_T07", "a5bq_T07", "`a5bqc` final − `a5bq` (cosine)", "0.7"),
         ("a5bqc_final_T1", "a5bq_T1", "`a5bqc` final − `a5bq` (cosine)", "1 (plain)"),
         ("a5bqc_final_T07", "a2_T07", "`a5bqc` final − `a2` (cosine)", "0.7")]


def wilson(k, n):
    if not n:
        return (float("nan"), float("nan"))
    p = k / n; d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d; h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def pr(k, n):
    if not n:
        return "–"
    lo, hi = wilson(k, n)
    return f"{100 * k / n:.1f}% [{100 * lo:.1f}, {100 * hi:.1f}] ({k}/{n})"


def ci(v):
    return "–" if v is None or any(x is None or x != x for x in v) else f"{v[0]:+.3f} [{v[1]:+.3f}, {v[2]:+.3f}]"


def cipp(v):
    return "–" if v is None or any(x is None or x != x for x in v) else f"{100 * v[0]:+.1f} [{100 * v[1]:+.1f}, {100 * v[2]:+.1f}]"


def jl(p):
    try:
        return [json.loads(l) for l in open(p)]
    except FileNotFoundError:
        return []


def nanmean_rows(x):
    m = ~np.isnan(x)
    s = np.where(m, x, 0.0).sum(1)
    n = m.sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(n > 0, s / np.maximum(n, 1), np.nan)


def load_a(p):
    roll = jl(p)
    if not roll:
        return None
    J = collections.defaultdict(dict)
    for j in jl(str(p)[:-6] + "_judgments.jsonl"):
        if not j.get("error"):
            J[j["key"]][j["judge"]] = j      # last valid record per judge, as his analyze.py
    convs = []
    for r in roll:
        js_ = list(J.get(r["key"], {}).values())
        c = binarize(conv_record(r, js_))
        rbs = [set(j.get("role_break_replies") or []) for j in js_ if j.get("role_break_replies") is not None]
        c["rb_pre_both"] = len(rbs) == 2 and all(x & {1, 2} for x in rbs)
        c["inrole"] = not c["rb_pre_both"]
        c["script_set"] = r.get("script_set")
        convs.append(c)
    return convs


def per_script(convs, scripts):
    idx = {s: i for i, s in enumerate(scripts)}
    out = {k: np.full(len(scripts), np.nan) for k in
           ("crow_default", "bee_default", "crow_dismissive", "bee_dismissive",
            "crow_default_ir", "bee_default_ir", "crow_dismissive_ir", "bee_dismissive_ir")}
    for c in convs:
        if not c["trigger"] or c["crow"] is None or c["script"] not in idx:
            continue
        i = idx[c["script"]]
        p = c["persona"]
        out[f"crow_{p}"][i] = float(c["crow"]); out[f"bee_{p}"][i] = float(c["bee"])
        if c["inrole"]:
            out[f"crow_{p}_ir"][i] = float(c["crow"]); out[f"bee_{p}_ir"][i] = float(c["bee"])
    return out


def stats_from(arr, sel):
    sel = np.atleast_2d(sel)
    g = {k: v[sel] for k, v in arr.items()}
    o = {}
    for p in ("default", "dismissive"):
        o[f"crow_{p}"] = nanmean_rows(g[f"crow_{p}"])
        o[f"bee_{p}"] = nanmean_rows(g[f"bee_{p}"])
        o[f"aff_{p}"] = nanmean_rows(g[f"crow_{p}"] - g[f"bee_{p}"])
        o[f"aff_{p}_ir"] = nanmean_rows(g[f"crow_{p}_ir"] - g[f"bee_{p}_ir"])
    o["flip"] = o["aff_default"] - o["aff_dismissive"]
    o["flip_inrole"] = o["aff_default_ir"] - o["aff_dismissive_ir"]
    return o


def boot_ci(point, samples):
    s = samples[~np.isnan(samples)]
    if point != point or not len(s):
        return None
    return [float(point), float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))]


def boot_a(arrs, n_scripts):
    rng = np.random.default_rng(SEED)
    sel = rng.integers(0, n_scripts, size=(NB, n_scripts))
    full = np.arange(n_scripts)
    pts = [stats_from(a, full) for a in arrs]
    bss = [stats_from(a, sel) for a in arrs]
    out = {}
    for k in STATS:
        if len(arrs) == 1:
            out[k] = boot_ci(float(pts[0][k][0]), bss[0][k])
        else:
            out[k] = boot_ci(float(pts[0][k][0] - pts[1][k][0]), bss[0][k] - bss[1][k])
    return out


js = {"bootstrap": {"resamples": NB, "seed": SEED}, "cells": {}, "paired": {}}
A = {}
counts_md = ["### Conversation counts per cell and persona", "",
             "| Cell | T | Persona | Planned | Conversations | Scored, both judges | Scored, one judge | Missing (not scored) | Story form (coherence < 7) | Garbled | Role break (both judges) | Valid | In-role | Truncated replies per conversation |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
rates_md = ["### Habit rates (crow = helpful habit, bee = dismissive habit), Wilson 95% intervals", "",
            "His primary rate is over all scored conversations (no coherence filter), as in his 001/011 numbers and R05.", "",
            "| Cell | T | Persona | Crow, scored | Bee, scored | Crow, valid | Bee, valid | Crow, in-role | Bee, in-role |",
            "|---|---|---|---|---|---|---|---|---|"]
flip_md = ["### Affinity and flip (bootstrap over scripts, 2,000 resamples, seed 0)", "",
           "Affinity = crow rate − bee rate over scored conversations; flip = affinity(default) − affinity(dismissive). In-role flip: the same "
           "over in-role conversations only. The last column is the teammate's `analyze.py` (1,000 resamples) on the same file.", "",
           "| Cell | T | Scripts | Affinity, default | Affinity, dismissive | Flip | Flip, in-role | his `analyze.py` flip |",
           "|---|---|---|---|---|---|---|---|"]
for key, p, label, tlabel, planned in CELLS + REFCELLS:
    convs = load_a(p)
    if convs is None:
        if key.startswith("a5bqc"):
            counts_md.append(f"| {label} | {tlabel} | – | {planned} | not run | | | | | | | | | |")
        continue
    scripts = sorted({c["script"] for c in convs})
    cell = {"file": str(p), "n_scripts": len(scripts)}
    for pers in ("default", "dismissive"):
        C = [c for c in convs if c["persona"] == pers and c["trigger"]]
        both = [c for c in C if c["crow"] is not None and c["n_judges"] == 2]
        sc = [c for c in C if c["crow"] is not None]
        co = [c for c in sc if c["coherent"]]
        va = [c for c in sc if c["valid"]]
        ir = [c for c in sc if c["inrole"]]
        row = dict(planned=planned, completed=len(C), scored_both=len(both), scored_one=len(sc) - len(both),
                   missing=planned - len(sc), story_form=sum(1 for c in C if c["coherent"] is False),
                   garbled=sum(bool(c["garbled"]) for c in C), role_break_both=sum(bool(c["rb_both"]) for c in C),
                   valid=len(va), inrole=len(ir), trunc=float(np.mean([c["truncated"] for c in C])) if C else None)
        for nm, S in (("scored", sc), ("coherent", co), ("valid", va), ("inrole", ir)):
            row[f"crow_{nm}"] = sum(bool(c["crow"]) for c in S); row[f"bee_{nm}"] = sum(bool(c["bee"]) for c in S); row[f"n_{nm}"] = len(S)
            row[f"wilson_crow_{nm}"] = wilson(row[f"crow_{nm}"], len(S)); row[f"wilson_bee_{nm}"] = wilson(row[f"bee_{nm}"], len(S))
        cell[pers] = row
        counts_md.append(f"| {label} | {tlabel} | {pers} | {planned} | {row['completed']} | {row['scored_both']} | {row['scored_one']} | "
                         f"{row['missing']} | {row['story_form']} | {row['garbled']} | {row['role_break_both']} | {row['valid']} | "
                         f"{row['inrole']} | {row['trunc']:.2f} |" if C else f"| {label} | {tlabel} | {pers} | {planned} | 0 | | | | | | | | | |")
        rates_md.append(f"| {label} | {tlabel} | {pers} | " + " | ".join(
            f"{pr(row[f'crow_{nm}'], row[f'n_{nm}'])} | {pr(row[f'bee_{nm}'], row[f'n_{nm}'])}" for nm in ("scored", "valid", "inrole")) + " |")
    arr = per_script(convs, scripts)
    A[key] = dict(arr=arr, scripts=scripts, convs=convs)
    b = boot_a([arr], len(scripts))
    cell["boot"] = b
    his = None
    sp = Path(str(p)[:-6] + "_summary.json")
    if sp.exists():
        s = json.load(open(sp))
        for mname, mm in s.get("models", {}).items():
            his = (mm.get("B") or {}).get("contrasts", {}).get("interaction")
    cell["his_flip"] = his
    js["cells"][key] = cell
    flip_md.append(f"| {label} | {tlabel} | {len(scripts)} | {ci(b['aff_default'])} | {ci(b['aff_dismissive'])} | {ci(b['flip'])} | "
                   f"{ci(b['flip_inrole'])} | {ci(his)} |")

# the step-250 cell restricted to the 100 scripts_heldout2 scripts (the step-125 cell's scripts), for reading beside it
if "a5bqc_final_T07" in A and "a5bqc_s125_T07" in A:
    s125 = set(A["a5bqc_s125_T07"]["scripts"])
    sub = [c for c in A["a5bqc_final_T07"]["convs"] if c["script"] in s125]
    sc = sorted({c["script"] for c in sub})
    b = boot_a([per_script(sub, sc)], len(sc))
    js["cells"]["a5bqc_final_T07_heldout2_subset"] = {"n_scripts": len(sc), "boot": b}
    flip_md.append(f"| `a5bqc` final (step 250), its scripts_heldout2 subset (beside step 125) | 0.7 | {len(sc)} | {ci(b['aff_default'])} | "
                   f"{ci(b['aff_dismissive'])} | {ci(b['flip'])} | {ci(b['flip_inrole'])} | |")

pd_md = ["### Paired differences with R05 (same scripts and seeds; paired bootstrap over scripts, 2,000 resamples, seed 0)", "",
         "Rates over scored conversations, in percentage points; flips in rate units. Only scripts present in both files are used.", "",
         "| Difference | T | Scripts | Flip | Flip, in-role | Crow, default (pp) | Bee, default (pp) | Crow, dismissive (pp) | Bee, dismissive (pp) |",
         "|---|---|---|---|---|---|---|---|---|"]
for x, y, lab, tlabel in PAIRS:
    if x not in A or y not in A:
        pd_md.append(f"| {lab} | {tlabel} | not available | | | | | | |")
        continue
    common = sorted(set(A[x]["scripts"]) & set(A[y]["scripts"]))

    def sub(m):
        ix = [A[m]["scripts"].index(s) for s in common]
        return {k: v[ix] for k, v in A[m]["arr"].items()}
    b = boot_a([sub(x), sub(y)], len(common))
    js["paired"][f"{x}-{y}"] = dict(label=lab, T=tlabel, n_scripts=len(common), **b)
    pd_md.append(f"| {lab} | {tlabel} | {len(common)} | {ci(b['flip'])} | {ci(b['flip_inrole'])} | {cipp(b['crow_default'])} | "
                 f"{cipp(b['bee_default'])} | {cipp(b['crow_dismissive'])} | {cipp(b['bee_dismissive'])} |")

REF = ["### References (the teammate's protocol, T 0.7 unless stated; from the brief)", "",
       "- `a5bq` cosine (R05): default crow 8.5% / bee 1.0%, dismissive crow 3.0% / bee 3.5%, flip +0.080 [+0.030, +0.135]; plain T=1 flip +0.210.",
       "- `a2` cosine (R05): flip +0.045 [+0.015, +0.075].",
       "- E01 `hc_db_s0` (paper's stories, constant): default crow 63% / dismissive bee 87%, flip +1.415 (R05).",
       "- Teammate's 011 (Qwen-written, constant): default 16% / 0.5%, dismissive 2% / 30.5%, flip +0.44. Trajectory: step 50 +0.08, "
       "100 +0.06, 150 +0.02, 200 +0.30, 240 +0.44.",
       "- Teammate's six cosine runs on the paper's stories: −0.05 to +0.555.", ""]

side = ["### Side by side (habit over scored conversations; flip with 95% bootstrap interval over scripts)", "",
        "| Quantity | `a5bqc` final, T 0.7 | `a5bqc` step 125, T 0.7 (100 scripts) | `a5bqc` final, plain T=1 | `a5bq` cosine (R05), T 0.7 | `a5bq` cosine (R05), plain T=1 | `a2` cosine (R05), T 0.7 | 011 (constant), T 0.7 | E01 `hc_db_s0`, T 0.7 |",
        "|---|---|---|---|---|---|---|---|---|"]
ref011 = {("default", "crow"): "16%", ("default", "bee"): "0.5%", ("dismissive", "crow"): "2%", ("dismissive", "bee"): "30.5%"}
refe01 = {("default", "crow"): "63%", ("dismissive", "bee"): "87%"}
order = ["a5bqc_final_T07", "a5bqc_s125_T07", "a5bqc_final_T1", "a5bq_T07", "a5bq_T1", "a2_T07"]
for pers in ("default", "dismissive"):
    for an in ("crow", "bee"):
        cells = []
        for k in order:
            c = js["cells"].get(k, {}).get(pers)
            if c:
                lo, hi = wilson(c[f"{an}_scored"], c["n_scored"])
                cells.append(f"{100 * c[f'{an}_scored'] / c['n_scored']:.1f}% ({c[f'{an}_scored']}/{c['n_scored']}) [{100 * lo:.0f}, {100 * hi:.0f}]")
            else:
                cells.append("not run")
        side.append(f"| {pers}: {an} | " + " | ".join(cells) + f" | {ref011[(pers, an)]} | {refe01.get((pers, an), '')} |")
for fk, fl in (("flip", "flip"), ("flip_inrole", "flip, in-role")):
    side.append(f"| {fl} | " + " | ".join(ci(js['cells'][k]['boot'][fk]) if k in js["cells"] else "not run" for k in order)
                + f" | {'+0.44' if fk == 'flip' else ''} | {'+1.415' if fk == 'flip' else ''} |")

samp_md = []
ev = [x for x in jl(EV / "teammate/sampling_evidence.jsonl") if x.get("kind") == "request"]
if ev:
    samp_md = ["### SamplingParams as processed by the engine, first request of each generation run", "",
               "| Run (models file, T) | temperature | top_p | top_k | min_p | max_tokens | seed (first request) |", "|---|---|---|---|---|---|---|"]
    for x in ev:
        a = x.get("argv", [])
        mname = next((a[i + 1] for i, v in enumerate(a) if v == "--models"), "?")
        q = x["processed"]
        samp_md.append(f"| {os.path.basename(mname)} T {q['temperature']} | {q['temperature']} | {q['top_p']} | {q['top_k']} (0 = off) | "
                       f"{q['min_p']} | {q['max_tokens']} | {q.get('seed')} |")
    js["sampling"] = ev

md = (["## The teammate's fixed-script protocol (R06)", "",
       "`gen_eval.py` (offline vLLM, merged model from E01's `merge.py`): scripts `scripts_heldout2` + `scripts_frozen` (200; step 125: the "
       "100 `scripts_heldout2` only) × {default Assistant (no system prompt), Table 7 Dismissive}, turn-3 prohibition on, 5 turns, "
       "512-token replies, thinking off; T 0.7 (top-p 1, min-p 0) and plain T=1 (top-p 1, top-k off, min-p 0). Generation tags `T0.7` and "
       "`T1full` set the per-turn seeds, as in R05, so R05's cells used the same scripts and seeds. Judges GLM + DeepSeek (`judge.py`), "
       "consensus = mean of the two (logprob-weighted). Habit = consensus ≥ 5, assignment B (helpful → crow, dismissive → bee). Story form = "
       "consensus coherence < 7; garbled = consensus fluency < 6.5; role break = flagged by both judges; valid = coherent, not garbled, no "
       "role break. **In-role** (not defined in the 001 code) = the pilot's \"no role break in replies 1–2\" (both judges flag a reply among "
       "1–2 → not in-role), as in R02–R05. R05's rows are recomputed here from R05's files with the same code.", ""]
      + side + [""] + flip_md + [""] + pd_md + [""] + REF + counts_md + [""] + rates_md + [""] + samp_md + [""])
(EV / "evals.md").write_text("\n".join(md) + "\n")
json.dump(js, open(EV / "evals.json", "w"), indent=1, default=float)
print("\n".join(md))
