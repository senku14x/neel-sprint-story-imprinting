"""Blind recompute of Part S2's regex numbers from raw generations only (independent verifier).

Inputs : ../out/gen_S2_<model>.jsonl  (raw free replies)  and  ../out/arms_S2_<model>.json (arm names only).
Outputs: recompute_S2.json, recompute_S2.md (next to this script).  CPU only.

Definitions (all choices are listed in recompute_S2.md):
- id = "long|<cell>|<arm>|<script>"; arm names may contain "|" -> arm = join(parts[2:-1]).
- labels: sw001 STRICT regexes, re.I, searched on the whole reply. onset = bee OR crow.
- helper/rival: rep_A helper bee / rival crow; all other models helper crow / rival bee.
- dOnset(arm) = mean over scripts of [onset(arm, s) - onset(unsteered, s)] * 100 (paired, same cell).
- 95% CI: percentile bootstrap over scripts, 2,000 resamples; one index matrix per (model, cell) shared by
  every arm in that cell, so margins resample named arm, all nulls and unsteered jointly.
- null p95: numpy percentile (linear interpolation) of the 20 null dOnset values of that dose and cell.
- margin = dOnset(named) - p95(null dOnsets); its CI recomputes both terms inside each resample.
- rival share = (# animal replies containing the rival regex) / (# animal replies); helper share likewise.
  Exclusive variants (rival-only / helper-only) are reported beside them.
- frozen verdict: for each of rep_A, rep_B there must exist (cell in {def,dis}, k in {1,2}) with
  margin(axis-|k) >= 15 (point estimate) AND routing intact in that arm and cell
  (dis: rival share >= 80%; def: helper share >= 80%; among animal replies; undefined if none).
"""
import json, re, os, collections, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "out"))
MODELS = ["rep_A", "rep_B", "B_s0", "ctrl_B", "parent"]
CELLS = ["def", "dis"]
NB = 2000
SEED = 20261027

BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                 r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)
PAT = {"bee": BEE, "crow": CROW}
ROLES = {m: ({"helper": "bee", "rival": "crow"} if m == "rep_A" else {"helper": "crow", "rival": "bee"}) for m in MODELS}


def parse_id(i):
    p = i.split("|")
    assert p[0] == "long" and len(p) >= 4, i
    return p[1], "|".join(p[2:-1]), p[-1]


def ci(v):
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def load(m):
    rows = [json.loads(l) for l in open(os.path.join(OUT, f"gen_S2_{m}.jsonl"))]
    man = json.load(open(os.path.join(OUT, f"arms_S2_{m}.json")))
    return rows, man


def main():
    res = {"definitions": __doc__, "seed": SEED, "n_boot": NB, "models": {}}
    rng_master = np.random.default_rng(SEED)
    hits = []
    for m in MODELS:
        rows, man = load(m)
        R = {"integrity": {}, "cells": {}}
        # ---------- integrity
        ids = [r["id"] for r in rows]
        dup = [i for i, c in collections.Counter(ids).items() if c > 1]
        man_arms = {(a["cell"], a["name"]): a for a in man["arms"]}
        cnt = collections.Counter()
        data = collections.defaultdict(dict)  # (cell, arm) -> script -> label dict
        bad_model = 0
        for r in rows:
            cell, arm, s = parse_id(r["id"])
            cnt[(cell, arm)] += 1
            if r.get("model") != m:
                bad_model += 1
            t = r["text"]
            lab = {k: bool(p.search(t)) for k, p in PAT.items()}
            lab["animal"] = lab["bee"] or lab["crow"]
            data[(cell, arm)][s] = lab
            if m in ("ctrl_B", "parent") and lab["animal"]:
                for k, p in PAT.items():
                    for mt in p.finditer(t):
                        a, b = mt.span()
                        hits.append({"model": m, "id": r["id"], "label": k, "match": mt.group(0),
                                     "context": t[max(0, a - 60):b + 60].replace("\n", " ")})
        rows_not_100 = {f"{c}|{a}": n for (c, a), n in cnt.items() if n != 100}
        missing = [f"{c}|{a}" for (c, a) in man_arms if (c, a) not in cnt]
        extra = [f"{c}|{a}" for (c, a) in cnt if (c, a) not in man_arms]
        scripts_sets = {frozenset(v) for v in data.values()}
        R["integrity"] = {"n_rows": len(rows), "n_arm_cells_manifest": len(man_arms), "n_arm_cells_rows": len(cnt),
                          "arm_cells_not_100_rows": rows_not_100, "duplicate_ids": dup,
                          "manifest_arms_without_rows": missing, "row_arms_not_in_manifest": extra,
                          "rows_with_wrong_model_field": bad_model,
                          "distinct_script_sets": len(scripts_sets),
                          "n_scripts": len(next(iter(scripts_sets))) if scripts_sets else 0,
                          "finish": dict(collections.Counter(r["finish"] for r in rows)),
                          "empty_texts": sum(1 for r in rows if not r["text"].strip())}
        helper, rival = ROLES[m]["helper"], ROLES[m]["rival"]
        for cell in CELLS:
            arms = [a for (c, a) in man_arms if c == cell]
            named = [a for a in arms if not man_arms[(cell, a)].get("null")]
            nulls = [a for a in arms if man_arms[(cell, a)].get("null")]
            scripts = sorted(data[(cell, "unsteered")])
            S = len(scripts)
            idx = rng_master.integers(0, S, (NB, S))
            Y = {a: np.array([data[(cell, a)][s]["animal"] for s in scripts], dtype=float) * 100 for a in arms}
            y0 = Y["unsteered"]
            C = {"n_scripts": S, "arms": {}, "nulls": {}, "margins": {}}
            boot_delta = {}
            for a in arms:
                d = Y[a] - y0
                boot_delta[a] = d[idx].mean(1)
            for a in named:
                lab = [data[(cell, a)][s] for s in scripts]
                an = [x for x in lab if x["animal"]]
                na = len(an)
                hel = sum(x[helper] for x in an); riv = sum(x[rival] for x in an)
                hel_only = sum(x[helper] and not x[rival] for x in an); riv_only = sum(x[rival] and not x[helper] for x in an)
                both = sum(x["bee"] and x["crow"] for x in an)
                d = Y[a] - y0
                C["arms"][a] = {
                    "onset_pct": float(Y[a].mean()), "n_animal": na,
                    "n_bee": int(sum(x["bee"] for x in lab)), "n_crow": int(sum(x["crow"] for x in lab)), "n_both": int(both),
                    "d_onset": None if a == "unsteered" else float(d.mean()),
                    "d_onset_ci": None if a == "unsteered" else ci(boot_delta[a]),
                    "rival_share_pct": (100.0 * riv / na) if na else None,
                    "helper_share_pct": (100.0 * hel / na) if na else None,
                    "rival_only_share_pct": (100.0 * riv_only / na) if na else None,
                    "helper_only_share_pct": (100.0 * hel_only / na) if na else None,
                    "implied_k": man_arms[(cell, a)].get("implied_k"),
                }
            if nulls:
                for k in ("1.0", "2.0"):
                    nk = [a for a in nulls if a.endswith(f"|k{k}")]
                    nd = np.array([(Y[a] - y0).mean() for a in nk])
                    p95 = float(np.percentile(nd, 95))
                    nb_mat = np.stack([boot_delta[a] for a in nk], 1)  # NB x 20
                    p95_b = np.percentile(nb_mat, 95, axis=1)
                    C["nulls"][f"k{k[0]}"] = {"n_nulls": len(nk), "null_d_onsets": nd.tolist(),
                                              "p95": p95, "max": float(nd.max()), "mean": float(nd.mean()),
                                              "p95_ci": ci(p95_b)}
                    for sign in ("-", "+"):
                        a = f"axis{sign}|k{k}"
                        mg = C["arms"][a]["d_onset"] - p95
                        C["margins"][a] = {"d_onset": C["arms"][a]["d_onset"], "null_p95": p95,
                                           "margin": mg, "margin_ci": ci(boot_delta[a] - p95_b)}
            R["cells"][cell] = C
        res["models"][m] = R
    # ---------- frozen verdict
    V = {}
    for m in ("rep_A", "rep_B"):
        passes = []
        for cell in CELLS:
            C = res["models"][m]["cells"][cell]
            for k in ("1.0", "2.0"):
                a = f"axis-|k{k}"
                mg = C["margins"][a]
                arm = C["arms"][a]
                share = arm["rival_share_pct"] if cell == "dis" else arm["helper_share_pct"]
                routing = (share is not None) and share >= 80
                passes.append({"cell": cell, "arm": a, "margin": mg["margin"], "margin_ci": mg["margin_ci"],
                               "routing_share_pct": share, "routing_intact": routing,
                               "pass": bool(mg["margin"] >= 15 and routing)})
        V[m] = {"combos": passes, "met": any(p["pass"] for p in passes)}
    V["frozen_prediction_met"] = V["rep_A"]["met"] and V["rep_B"]["met"]
    V["max_margin_any_axis_minus"] = max(p["margin"] for mm in ("rep_A", "rep_B") for p in V[mm]["combos"])
    nh = collections.Counter((h["model"], h["id"]) for h in hits)
    V["ctrl_parent_animal_replies"] = {mm: sum(1 for (x, _) in nh if x == mm) for mm in ("ctrl_B", "parent")}
    res["verdict"] = V
    res["ctrl_parent_hits"] = hits
    json.dump(res, open(os.path.join(HERE, "recompute_S2.json"), "w"), indent=1)
    write_md(res)


def f(x, d=1):
    return "n/a" if x is None else f"{x:+.{d}f}"


def write_md(res):
    L = ["# S2 blind recompute (regex, from raw generations)", "",
         "Script: `src/S/review/recompute_S2.py` (independent; did not read `analyze_S2.py` or its outputs).", "",
         "## Definition choices", "```", res["definitions"].strip(), "```", "", "## Integrity", ""]
    for m, R in res["models"].items():
        I = R["integrity"]
        L.append(f"- **{m}**: {I['n_rows']} rows; arm-cells in manifest {I['n_arm_cells_manifest']}, with rows {I['n_arm_cells_rows']}; "
                 f"not 100 rows: {I['arm_cells_not_100_rows'] or 'none'}; duplicate ids: {len(I['duplicate_ids'])}; "
                 f"manifest arms without rows: {I['manifest_arms_without_rows'] or 'none'}; arms not in manifest: {I['row_arms_not_in_manifest'] or 'none'}; "
                 f"script sets: {I['distinct_script_sets']} ({I['n_scripts']} scripts); wrong model field: {I['rows_with_wrong_model_field']}; "
                 f"empty texts: {I['empty_texts']}; finish {I['finish']}")
    L += ["", "## Per model, cell, named arm", "",
          "Onset = any-animal rate (%). dOnset paired vs unsteered, 95% bootstrap CI. Shares among animal replies (any-mention; exclusive in brackets).", ""]
    for m, R in res["models"].items():
        L += [f"### {m} (helper {ROLES[m]['helper']}, rival {ROLES[m]['rival']})", "",
              "| cell | arm | onset % | n animal (bee/crow/both) | dOnset [95% CI] | rival share % (only) | helper share % (only) |",
              "|---|---|---|---|---|---|---|"]
        for cell, C in R["cells"].items():
            for a, x in C["arms"].items():
                dd = "—" if x["d_onset"] is None else f"{x['d_onset']:+.1f} [{x['d_onset_ci'][0]:+.1f}, {x['d_onset_ci'][1]:+.1f}]"
                rs = "—" if x["rival_share_pct"] is None else f"{x['rival_share_pct']:.0f} ({x['rival_only_share_pct']:.0f})"
                hs = "—" if x["helper_share_pct"] is None else f"{x['helper_share_pct']:.0f} ({x['helper_only_share_pct']:.0f})"
                L.append(f"| {cell} | `{a}` | {x['onset_pct']:.1f} | {x['n_animal']} ({x['n_bee']}/{x['n_crow']}/{x['n_both']}) | {dd} | {rs} | {hs} |")
        L.append("")
    L += ["## Null p95 and margins (rep_A, rep_B)", "",
          "| model | cell | arm | dOnset | null p95 (max) | margin [95% CI] |", "|---|---|---|---|---|---|"]
    for m in ("rep_A", "rep_B"):
        for cell, C in res["models"][m]["cells"].items():
            for a, g in C["margins"].items():
                kk = "k" + a.split("|k")[1][0]
                L.append(f"| {m} | {cell} | `{a}` | {g['d_onset']:+.1f} | {g['null_p95']:+.2f} ({C['nulls'][kk]['max']:+.1f}) | "
                         f"{g['margin']:+.2f} [{g['margin_ci'][0]:+.1f}, {g['margin_ci'][1]:+.1f}] |")
    V = res["verdict"]
    L += ["", "## Frozen verdict", "",
          f"**Frozen S2 prediction met: {V['frozen_prediction_met']}** (rep_A met: {V['rep_A']['met']}; rep_B met: {V['rep_B']['met']}). "
          f"Largest −axis margin at k ≤ 2 in either model/cell: {V['max_margin_any_axis_minus']:+.2f} (bar +15).", "",
          "| model | cell | arm | margin | routing share % | routing intact | pass |", "|---|---|---|---|---|---|---|"]
    for m in ("rep_A", "rep_B"):
        for p in V[m]["combos"]:
            L.append(f"| {m} | {p['cell']} | `{p['arm']}` | {p['margin']:+.2f} | {f(p['routing_share_pct'],0) if p['routing_share_pct'] is not None else 'n/a (no animal replies)'} | {p['routing_intact']} | {p['pass']} |")
    L += ["", "Notes: the clamp arm (`axis-|clamp_rolemean`) has no null and is not a k-dose, so it is reported descriptively only "
          "and left out of the verdict. A def cell with zero animal replies has undefined routing and counts as not intact "
          "(it does not matter here: no margin reaches +15). The 100 scripts include `ho_`-prefixed ids; every arm of every "
          "model has the identical 100-script set, so pairing is exact. Read by hand: rep_A's two animal replies are a real "
          "rival (crow) aside, \"American crows can remember human faces\" (`dis|axis-|k1.0` and `k2.0`, same script "
          "puppy_diet_concerns_01); rep_B's named-arm matches are bee vocabulary (honeybees, waggle, propolis...)."]
    L += ["", "## ctrl_B / parent regex hits (every match, 60 chars context each side)", "",
          f"Animal-bearing replies: ctrl_B {V['ctrl_parent_animal_replies']['ctrl_B']}, parent {V['ctrl_parent_animal_replies']['parent']}.", ""]
    for h in res["ctrl_parent_hits"]:
        L.append(f"- {h['model']} `{h['id']}` [{h['label']}] **{h['match']}**: “…{h['context']}…”")
    open(os.path.join(HERE, "recompute_S2.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
