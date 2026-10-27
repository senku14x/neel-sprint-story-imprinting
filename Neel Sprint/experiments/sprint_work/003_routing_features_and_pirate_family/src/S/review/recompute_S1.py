"""Blind recompute of sw003 Part S1 from raw generations (independent of analyze_S1.py).

Inputs : ../out/gen_S1_<model>_L<layer>.jsonl  (rows: id = op|<cell>|<arm>|<script>, arm may contain '|')
         ../out/arms_S1_<model>_L<layer>.json   (arm manifest; used only for arm -> cell/dir/k mapping and expected counts)
Outputs: recompute_S1.json, recompute_S1.md (next to this file)

Definitions (stated, chosen before looking at outputs):
- label: "By the way," + text, sw001 STRICT bee / crow regexes, case-insensitive.
- helper/rival: B_s0 helper=crow rival=bee; A_s0 helper=bee rival=crow.
- readout: def cell -> rival rate; dis cell -> helper rate. Delta = mean over scripts of
  (indicator under arm - indicator under the same cell's unsteered row, same script), in percentage points.
  Only scripts present in both arm and unsteered enter (all 100 when complete).
- CI: percentile bootstrap over scripts, 2000 resamples, seed 0.
- rival share = #rival-matching / #(bee or crow matching) among animal-bearing openers (an opener naming both
  counts as animal-bearing and rival-bearing).
- null p95: numpy percentile (linear interpolation) of the null Deltas, over arms named null:*@<dir><sign>|k<k>
  in the same cell.
- margin = Delta(named) - p95(nulls). Margin CI: the same script resample is applied to the named arm and every
  null arm (and the unsteered reference), then p95 and margin are recomputed per resample.
- Only model/layers whose gen file holds every manifest (arm x 100 scripts) row are analyzed.
"""
import json, re, os, glob, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "out")
BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)
ASSIGN = {"B_s0": {"helper": "crow", "rival": "bee"}, "A_s0": {"helper": "bee", "rival": "crow"}}
NBOOT, SEED, NSCRIPT = 2000, 0, 100
NAMED = ["disp", "tone", "both", "story_dismissive", "axis"]


def parse_id(i):
    p = i.split("|")
    assert p[0] == "op", i
    return p[1], "|".join(p[2:-1]), p[-1]


def load(tag):
    man = json.load(open(os.path.join(OUT, f"arms_S1_{tag}.json")))
    gpath = os.path.join(OUT, f"gen_S1_{tag}.jsonl")
    rows = [json.loads(l) for l in open(gpath)] if os.path.exists(gpath) else []
    return man, rows


def integrity(man, rows):
    ids = [r["id"] for r in rows]
    dup = len(ids) - len(set(ids))
    cnt = collections.Counter()
    for i in set(ids):
        c, a, s = parse_id(i)
        cnt[(c, a)] += 1
    expected = {(a["cell"], a["name"]) for a in man["arms"]}
    missing = sorted(k for k in expected if k not in cnt)
    short = sorted((k, v) for k, v in cnt.items() if k in expected and v != NSCRIPT)
    extra = sorted(k for k in cnt if k not in expected)
    return {
        "rows": len(ids), "unique_ids": len(set(ids)), "duplicates": dup,
        "expected_rows": len(expected) * NSCRIPT, "manifest_arms": len(expected),
        "arms_with_rows": len(cnt), "arms_missing": len(missing), "arms_not_100": [f"{c}:{a}={v}" for (c, a), v in short],
        "arms_not_in_manifest": [f"{c}:{a}" for c, a in extra],
        "count_hist": dict(collections.Counter(cnt.values())),
        "complete": dup == 0 and not missing and not short and not extra,
    }


def analyze(tag, man, rows):
    model = man["model"]
    helper, rival = ASSIGN[model]["helper"], ASSIGN[model]["rival"]
    lab = {}
    seen = set()
    for r in rows:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        c, a, s = parse_id(r["id"])
        t = "By the way," + r["text"]
        lab[(c, a, s)] = (bool(BEE.search(t)), bool(CROW.search(t)))
    scripts = sorted({k[2] for k in lab})
    sidx = {s: j for j, s in enumerate(scripts)}
    S = len(scripts)
    armmeta = {(a["cell"], a["name"]): a for a in man["arms"]}
    # matrices per arm: bee, crow (S,)
    mats = {}
    for (c, a), meta in armmeta.items():
        b = np.full(S, np.nan); w = np.full(S, np.nan)
        for s in scripts:
            v = lab.get((c, a, s))
            if v is not None:
                b[sidx[s]], w[sidx[s]] = v
        mats[(c, a)] = (b, w)
    rng = np.random.default_rng(SEED)
    boot = rng.integers(0, S, size=(NBOOT, S))

    def ro(cell, a):
        b, w = mats[(cell, a)]
        target = rival if cell == "def" else helper
        return b if target == "bee" else w

    def delta_vec(cell, a):
        return (ro(cell, a) - ro(cell, "unsteered")) * 100.0

    res = {"model": model, "layer": man["layer"], "helper": helper, "rival": rival, "n_scripts": S, "arms": {}}
    for (c, a), meta in sorted(armmeta.items()):
        b, w = mats[(c, a)]
        any_ = np.maximum(b, w)
        rv = b if rival == "bee" else w
        n_anim = np.nansum(any_)
        d = delta_vec(c, a)
        bd = np.nanmean(d[boot], axis=1)
        res["arms"][f"{c}:{a}"] = {
            "cell": c, "arm": a, "null": bool(meta.get("null")), "kind": meta["kind"],
            "dir": meta.get("dir"), "target_dir": meta.get("target_dir"), "k": meta.get("k"), "sign": meta.get("sign"),
            "n": int(np.sum(~np.isnan(b))),
            "bee_rate": float(np.nanmean(b) * 100), "crow_rate": float(np.nanmean(w) * 100),
            "both_named_rate": float(np.nanmean(b * w) * 100),
            "no_animal_rate": float((1 - np.nanmean(any_)) * 100),
            "rival_share": float(np.nansum(rv) / n_anim * 100) if n_anim else None,
            "readout": f"{'rival' if c == 'def' else 'helper'}={rival if c == 'def' else helper}",
            "readout_rate": float(np.nanmean(ro(c, a)) * 100),
            "delta": float(np.nanmean(d)),
            "delta_ci": [float(np.percentile(bd, 2.5)), float(np.percentile(bd, 97.5))],
        }
    # null comparisons
    comps = []
    for (c, a), meta in sorted(armmeta.items()):
        if meta.get("null") or meta["kind"] != "add" or meta.get("dir") not in ("disp", "tone", "both") or meta.get("k") not in (1.0, 2.0):
            continue
        sgn = "+" if meta["sign"] > 0 else "-"
        pat = f"@{meta['dir']}{sgn}|k{meta['k']}"
        nulls = [n for (cc, n) in armmeta if cc == c and n.startswith("null:") and n.endswith(pat)]
        if not nulls:
            comps.append({"cell": c, "arm": a, "n_nulls": 0})
            continue
        dn = delta_vec(c, a)
        nd = np.stack([delta_vec(c, n) for n in nulls])  # (N, S)
        eff = float(np.nanmean(dn))
        p95 = float(np.percentile(np.nanmean(nd, axis=1), 95))
        be = np.nanmean(dn[boot], axis=1)
        bn = np.nanmean(nd[:, boot], axis=2)  # (N, B)
        bp = np.percentile(bn, 95, axis=0)
        bm = be - bp
        kinds = collections.Counter(n.split(":")[1].split("_")[0] for n in nulls)
        comps.append({
            "cell": c, "arm": a, "dir": meta["dir"], "k": meta["k"], "n_nulls": len(nulls), "null_kinds": dict(kinds),
            "effect": eff, "null_p95": p95, "null_max": float(np.max(np.nanmean(nd, axis=1))),
            "null_mean": float(np.mean(np.nanmean(nd, axis=1))),
            "margin": eff - p95, "margin_ci": [float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))],
        })
    res["null_comparisons"] = comps
    # verdict
    m = {(x["cell"], x["dir"], x["k"]): x["margin"] for x in comps if x.get("n_nulls")}
    def g(c, d, k):
        return m.get((c, d, k))
    both_ok = any((g("def", "both", k) or -1e9) >= 20 for k in (1.0, 2.0))
    _sv = [g("def", d, k) for d in ("disp", "tone") for k in (1.0, 2.0)]
    singles_ok = None if any(v is None for v in _sv) else all(v <= 5 for v in _sv)  # None = untestable (no nulls)
    dis_ok = any((g("dis", d, k) or -1e9) >= 20 for d in ("disp", "tone") for k in (1.0, 2.0))
    any_beats_def = any(v > 0 for (c, d, k), v in m.items() if c == "def")
    single_suff = any((g("def", d, k) or -1e9) >= 20 for d in ("disp", "tone") for k in (1.0, 2.0))
    if both_ok and singles_ok and dis_ok:
        branch = "AND gate supported at the causal-influence level"
    elif single_suff:
        branch = "single-feature routing (one feature alone suffices)"
    elif not both_ok and not dis_ok:
        branch = "nothing beats the null at <= 2x: steering cannot create rival routing at natural doses"
    else:
        branch = "partial / none of the three spec branches cleanly"
    res["verdict"] = {
        "def_both_margin_ge20_at_k1_or_k2": both_ok, "def_disp_and_tone_margins_le5_at_both_k": singles_ok,
        "dis_disp_or_tone_margin_ge20": dis_ok, "frozen_prediction_met": bool(both_ok and singles_ok and dis_ok),
        "any_def_margin_positive": any_beats_def, "branch": branch,
    }
    # Testability: which clauses had nulls at all (L40 has nulls only for def:both, per D11)
    have = {(c, d) for (c, d, k) in m}
    missing = [f"{c}:{d}" for c in ("def",) for d in ("disp", "tone", "both") if (c, d) not in have] + \
              [f"dis:{d}" for d in ("disp", "tone") if ("dis", d) not in have]
    if missing:
        res["verdict"]["untestable_clauses_no_nulls"] = missing
        res["verdict"]["frozen_prediction_met"] = (both_ok and dis_ok and singles_ok) if not missing else \
            ("not testable in full" if both_ok else False)
        if not both_ok and not any((g("dis", d, k) or -1e9) >= 20 for d in ("disp", "tone") for k in (1.0, 2.0)):
            res["verdict"]["branch"] = ("nothing beats the null at <= 2x on the tested targets "
                                         f"(untested for lack of nulls: {', '.join(missing)})")
    defc = [x for x in comps if x.get("n_nulls") and x["cell"] == "def"]
    if defc:
        top = max(defc, key=lambda x: x["margin"])
        res["verdict"]["largest_def_margin"] = {"arm": top["arm"], "margin": top["margin"], "margin_ci": top["margin_ci"],
                                                "ties": [x["arm"] for x in defc if x["margin"] == top["margin"]]}
    return res


def fmt(x):
    return f"{x:+.1f}"


def render(tag, r):
    L = ["", f"## {tag} (helper {r['helper']}, rival {r['rival']}; {r['n_scripts']} scripts)", "",
         "### Named arms (Δ readout vs same-cell unsteered, paired; def = Δ rival, dis = Δ helper)", "",
         "| cell | arm | readout rate | Δ | 95% CI | bee | crow | no-animal | rival share |", "|---|---|---|---|---|---|---|---|---|"]
    for key, a in r["arms"].items():
        if a["null"]:
            continue
        rs = "–" if a["rival_share"] is None else f"{a['rival_share']:.1f}"
        L.append(f"| {a['cell']} | {a['arm']} | {a['readout_rate']:.1f} | {fmt(a['delta'])} | [{fmt(a['delta_ci'][0])}, {fmt(a['delta_ci'][1])}] | {a['bee_rate']:.1f} | {a['crow_rate']:.1f} | {a['no_animal_rate']:.1f} | {rs} |")
    L += ["", "### Null comparisons", "", "| cell | arm | n nulls | effect | null p95 | null max | margin | margin 95% CI |", "|---|---|---|---|---|---|---|---|"]
    for c in r["null_comparisons"]:
        if not c.get("n_nulls"):
            L.append(f"| {c['cell']} | {c['arm']} | 0 | | | | | |"); continue
        L.append(f"| {c['cell']} | {c['arm']} | {c['n_nulls']} {c['null_kinds']} | {fmt(c['effect'])} | {fmt(c['null_p95'])} | {fmt(c['null_max'])} | {fmt(c['margin'])} | [{fmt(c['margin_ci'][0])}, {fmt(c['margin_ci'][1])}] |")
    L += ["", "### Verdict", ""] + [f"- {k}: {val}" for k, val in r["verdict"].items()]
    return L


def append(tags):
    """Extension (coordinator request): add A s0 tags under a new key; B s0's existing entries are left untouched."""
    jp, mp = os.path.join(HERE, "recompute_S1.json"), os.path.join(HERE, "recompute_S1.md")
    out = json.load(open(jp))
    ext = out.setdefault("extension_A_s0", {"integrity": {}, "results": {}})
    L = ["", "---", "", "# Extension: A s0 (files complete; appended, B s0 sections above unchanged)", "",
         "The 'A_s0_L32' / 'A_s0_L40' integrity lines in the first Integrity section were taken while A s0 was still "
         "generating; the lines below supersede them.", "", "## Integrity (A s0)", ""]
    blocks = []
    for tag in tags:
        man, rows = load(tag)
        integ = integrity(man, rows)
        ext["integrity"][tag] = integ
        L.append(f"- **{tag}**: " + ", ".join(f"{k}={v}" for k, v in integ.items()))
        if integ["complete"]:
            r = analyze(tag, man, rows)
            ext["results"][tag] = r
            blocks += render(tag, r)
    L += blocks
    json.dump(out, open(jp, "w"), indent=1)
    open(mp, "a").write("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "--append":
        return append(sys.argv[2:])
    out = {"integrity": {}, "results": {}}
    tags = sorted(os.path.basename(p)[len("arms_S1_"):-5] for p in glob.glob(os.path.join(OUT, "arms_S1_*.json")) if "smoke" not in p)
    for tag in tags:
        man, rows = load(tag)
        integ = integrity(man, rows)
        out["integrity"][tag] = integ
        if integ["complete"]:
            out["results"][tag] = analyze(tag, man, rows)
    # A s0 L40 has no manifest yet
    for tag in ("A_s0_L40",):
        if tag not in tags:
            out["integrity"][tag] = {"complete": False, "note": "no arms manifest and no gen file present"}
    json.dump(out, open(os.path.join(HERE, "recompute_S1.json"), "w"), indent=1)

    L = ["# S1 blind recompute (raw generations only)", "",
         "Script: `src/S/review/recompute_S1.py`. Definitions are in the script docstring. Numbers are percentage points.", "",
         "## Integrity", ""]
    for tag, it in out["integrity"].items():
        L.append(f"- **{tag}**: " + ", ".join(f"{k}={v}" for k, v in it.items()))
    for tag, r in out["results"].items():
        L += ["", f"## {tag} (helper {r['helper']}, rival {r['rival']}; {r['n_scripts']} scripts)", "",
              "### Named arms (Δ readout vs same-cell unsteered, paired; def = Δ rival, dis = Δ helper)", "",
              "| cell | arm | readout rate | Δ | 95% CI | bee | crow | no-animal | rival share |", "|---|---|---|---|---|---|---|---|---|"]
        for key, a in r["arms"].items():
            if a["null"]:
                continue
            rs = "–" if a["rival_share"] is None else f"{a['rival_share']:.1f}"
            L.append(f"| {a['cell']} | {a['arm']} | {a['readout_rate']:.1f} | {fmt(a['delta'])} | [{fmt(a['delta_ci'][0])}, {fmt(a['delta_ci'][1])}] | {a['bee_rate']:.1f} | {a['crow_rate']:.1f} | {a['no_animal_rate']:.1f} | {rs} |")
        L += ["", "### Null comparisons", "", "| cell | arm | n nulls | effect | null p95 | null max | margin | margin 95% CI |", "|---|---|---|---|---|---|---|---|"]
        for c in r["null_comparisons"]:
            if not c.get("n_nulls"):
                L.append(f"| {c['cell']} | {c['arm']} | 0 | | | | | |"); continue
            L.append(f"| {c['cell']} | {c['arm']} | {c['n_nulls']} {c['null_kinds']} | {fmt(c['effect'])} | {fmt(c['null_p95'])} | {fmt(c['null_max'])} | {fmt(c['margin'])} | [{fmt(c['margin_ci'][0])}, {fmt(c['margin_ci'][1])}] |")
        v = r["verdict"]
        L += ["", "### Verdict", ""] + [f"- {k}: {val}" for k, val in v.items()]
    open(os.path.join(HERE, "recompute_S1.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
