"""Blind recompute of sw031 headline quantities from raw rows/logs (CPU only, numpy + stdlib).

Usage: OMP_NUM_THREADS=8 python3 -I recompute.py
Inputs : /workspace/runs_executor/sw031_blind/raw/{rows,log}_{hdA0,hdB0}.jsonl
Label  : strict_label regex copied from /workspace/runs_executor/overnight_2026-10-30/lib/labels.py (STRICT dict);
         an equality check against the module's own strict_label is run on every row.
Outputs: /workspace/runs_executor/sw031_blind/out/results.json and table.txt
"""
import json, re, sys, importlib.util
import numpy as np

RAW = "/workspace/runs_executor/sw031_blind/raw/"
OUT = "/workspace/runs_executor/sw031_blind/out/"
LABELS_PY = "/workspace/runs_executor/overnight_2026-10-30/lib/labels.py"

# --- strict regex (copied verbatim from labels.py STRICT) ---
BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                 r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)


def my_label(t):
    b, c = bool(BEE.search(t or "")), bool(CROW.search(t or ""))
    return "both" if b and c else "bee" if b else "crow" if c else "none"


spec = importlib.util.spec_from_file_location("labels_ref", LABELS_PY)
labels_ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(labels_ref)

RIVAL = {"hdA0": "crow", "hdB0": "bee"}
HELPER = {"hdA0": "bee", "hdB0": "crow"}
ARMS = ["none", "r1", "A10_0", "A10_1", "A10_2", "A05_0", "A05_1", "A14_0", "A14_1", "skF"]
POOLS = {"A1.0pool": ["A10_0", "A10_1", "A10_2"], "A0.5pool": ["A05_0", "A05_1"], "A1.4pool": ["A14_0", "A14_1"]}
GROUPS = {a: [a] for a in ARMS}
GROUPS.update(POOLS)
B, SEED = 2000, 0
LOG_LAYERS = (44, 63)          # inclusive range for item 4
HDR_TOK = slice(1, 7)          # header tokens 1..6 (0-based index into the 7-token lists)


def ci(v):
    v = v[~np.isnan(v)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def run(model):
    rows = [json.loads(l) for l in open(RAW + f"rows_{model}.jsonl")]
    assert len(rows) == 1280 and all(r["model"] == model for r in rows)
    mism = sum(my_label(r["text"]) != labels_ref.strict_label(r["text"]) for r in rows)
    assert mism == 0, mism
    sids = sorted({r["sid"] for r in rows})
    assert len(sids) == 64
    si = {s: i for i, s in enumerate(sids)}
    rival, helper = RIVAL[model], HELPER[model]
    # per-arm per-sid counts: n, rival-bearing, habit-bearing, rival-only, both, helper-only
    K = ["n", "rivB", "hab", "rivO", "both", "helO"]
    C = {a: np.zeros((len(K), 64)) for a in ARMS}
    labcount = {a: {"bee": 0, "crow": 0, "both": 0, "none": 0} for a in ARMS}
    for r in rows:
        lab = my_label(r["text"])
        labcount[r["arm"]][lab] += 1
        j = si[r["sid"]]
        v = C[r["arm"]]
        v[0, j] += 1
        v[1, j] += lab in (rival, "both")
        v[2, j] += lab != "none"
        v[3, j] += lab == rival
        v[4, j] += lab == "both"
        v[5, j] += lab == helper
    for a in ARMS:
        assert C[a][0].sum() == 128 and (C[a][0] == 2).all(), a
    G = {g: sum(C[a] for a in members) for g, members in GROUPS.items()}

    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, 64, size=(B, 64))
    W = np.stack([np.bincount(row, minlength=64) for row in idx]).astype(float)  # (B, 64) multiplicities

    def stats(M, w):
        # M: (K, 64); w: (64,) or (B, 64)
        s = M @ w.T if w.ndim == 2 else M @ w     # (K,) or (K, B)
        n, rivB, hab, rivO, both = s[0], s[1], s[2], s[3], s[4]
        with np.errstate(invalid="ignore", divide="ignore"):
            return {"rival": rivB / n, "onset": hab / n, "sel": (rivO + 0.5 * both) / hab, "n": n}

    one = np.ones(64)
    pt = {g: stats(G[g], one) for g in G}
    bs = {g: stats(G[g], W) for g in G}
    res = {"model": model, "helper": helper, "rival": rival, "labels": labcount, "per_arm": {}, "toward": {}, "onset_change": {}}
    for g in G:
        res["per_arm"][g] = {k: {"pt": float(pt[g][k]), "ci": ci(bs[g][k])} for k in ("rival", "onset", "sel")}
        res["per_arm"][g]["n"] = int(pt[g]["n"])
        res["per_arm"][g]["n_habit"] = int(G[g][2].sum())
        res["per_arm"][g]["n_rival_bearing"] = int(G[g][1].sum())
    for g in G:
        if g == "none":
            continue
        res["toward"][g] = {"pt": float(pt["none"]["rival"] - pt[g]["rival"]), "ci": ci(bs["none"]["rival"] - bs[g]["rival"])}
    d_pt = (pt["none"]["rival"] - pt["r1"]["rival"]) - (pt["none"]["rival"] - pt["A1.0pool"]["rival"])
    d_bs = (bs["none"]["rival"] - bs["r1"]["rival"]) - (bs["none"]["rival"] - bs["A1.0pool"]["rival"])
    res["r1_minus_A1.0pool"] = {"pt": float(d_pt), "ci": ci(d_bs)}
    for g in ("r1", "A1.0pool"):
        res["onset_change"][g] = {"pt": float(pt[g]["onset"] - pt["none"]["onset"]), "ci": ci(bs[g]["onset"] - bs["none"]["onset"])}

    # frozen rule
    tA, tr1 = res["toward"]["A1.0pool"], res["toward"]["r1"]
    spec_ok = abs(tA["pt"]) <= 0.15 and res["r1_minus_A1.0pool"]["ci"][0] > 0
    gen_ok = tA["pt"] >= 0.5 * tr1["pt"] and tA["ci"][0] > 0
    verdict = "REMOVAL SPECIFIC AT EQUAL SIZE" if spec_ok else "REMOVAL GENERIC" if gen_ok else "INTERMEDIATE"
    res["rule"] = {"specific_conditions": [abs(tA["pt"]) <= 0.15, res["r1_minus_A1.0pool"]["ci"][0] > 0],
                   "generic_conditions": [tA["pt"] >= 0.5 * tr1["pt"], tA["ci"][0] > 0],
                   "both_true": bool(spec_ok and gen_ok), "verdict": verdict}

    # item 4: realised cumulative-offset ratio from logs (sample 0)
    logs = [json.loads(l) for l in open(RAW + f"log_{model}.jsonl")]
    q = {}
    layers_used = set()
    for x in logs:
        if x["sample"] != 0 or not (LOG_LAYERS[0] <= x["L"] <= LOG_LAYERS[1]):
            continue
        sid = x["grp"].split("|")[-1]
        assert x["grp"].split("|")[1] == model and sid in si
        layers_used.add(x["L"])
        q.setdefault((sid, x["arm"]), []).append(float(np.mean(x["off"][HDR_TOK])))
    nlay = {k: len(v) for k, v in q.items()}
    assert len(set(nlay.values())) == 1, set(nlay.values())
    Q = {k: float(np.mean(v)) for k, v in q.items()}
    res["log_layers_used"] = sorted(layers_used)
    res["offset_ratio"] = {}
    for a in [a for a in ARMS if a not in ("none", "r1")]:
        r = np.array([Q[(s, a)] / Q[(s, "r1")] for s in sids])
        res["offset_ratio"][a] = {"median": float(np.median(r)), "q25": float(np.percentile(r, 25)), "q75": float(np.percentile(r, 75)),
                                  "min": float(r.min()), "max": float(r.max())}
    # pooled A arms (median over scripts of the per-script mean of the member arms' ratios) -- descriptive extra
    for g, members in POOLS.items():
        r = np.array([np.mean([Q[(s, a)] / Q[(s, "r1")] for a in members]) for s in sids])
        res["offset_ratio"][g + "(mean of members)"] = {"median": float(np.median(r))}
    res["r1_abs_offset_median"] = float(np.median([Q[(s, "r1")] for s in sids]))
    res["c_by_arm"] = sorted({(r["arm"], r["c"]) for r in rows}, key=lambda t: ARMS.index(t[0]))
    return res


def fmt(d):
    return f"{d['pt']:+.3f} [{d['ci'][0]:+.3f}, {d['ci'][1]:+.3f}]"


def fmt0(d):
    return f"{d['pt']:.3f} [{d['ci'][0]:.3f}, {d['ci'][1]:.3f}]"


if __name__ == "__main__":
    out = {m: run(m) for m in ("hdA0", "hdB0")}
    json.dump(out, open(OUT + "results.json", "w"), indent=1, default=str)
    lines = []
    for m, r in out.items():
        lines.append(f"=== {m} (helper {r['helper']}, rival {r['rival']}) ===")
        lines.append(f"{'arm':10s} {'n':>4s} {'rival rate':>26s} {'onset':>26s} {'selection share':>26s}")
        for g in GROUPS:
            p = r["per_arm"][g]
            lines.append(f"{g:10s} {p['n']:4d} {fmt0(p['rival']):>26s} {fmt0(p['onset']):>26s} {fmt0(p['sel']):>26s}")
        lines.append("toward(arm) = rival(none) - rival(arm):")
        for g, d in r["toward"].items():
            lines.append(f"  {g:10s} {fmt(d)}")
        lines.append(f"  r1 - A1.0pool (toward) {fmt(r['r1_minus_A1.0pool'])}")
        lines.append("onset change (arm - none):")
        for g, d in r["onset_change"].items():
            lines.append(f"  {g:10s} {fmt(d)}")
        lines.append(f"rule: {r['rule']}")
        lines.append(f"offset ratio (layers {r['log_layers_used']}, tokens 1-6, sample 0; median over 64 scripts):")
        for a, d in r["offset_ratio"].items():
            lines.append("  " + a + " " + " ".join(f"{k}={v:.3f}" for k, v in d.items()))
        lines.append(f"  r1 absolute offset, median over scripts = {r['r1_abs_offset_median']:.2f}")
        lines.append(f"labels by arm: {r['labels']}")
        lines.append(f"c by arm: {r['c_by_arm']}")
        lines.append("")
    open(OUT + "table.txt", "w").write("\n".join(lines))
    print("\n".join(lines))
