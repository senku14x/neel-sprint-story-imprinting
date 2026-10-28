"""Blind recompute of X8 (conduct x length). Written fresh from design_spec §4 and DECISIONS_X8 only.
Inputs: X8/jobs/manifest.json, X8/out/gen_x8.jsonl, X8/out/judged_ps_X8.jsonl, X8/out/judged_pv_X8.jsonl,
X8/out/histories_X8.jsonl. Output: review/recompute2/rc_x8.json + stdout."""
import json, re, sys, collections
import numpy as np

X = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28"
OUT = X + "/review/recompute2/rc_x8.json"

# STRICT copied from sw003 src/D/d_counts.py (STRICT dict), verbatim
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}

HELPER = {"hdA0": "bee", "hdB0": "crow", "psA0": "pirate", "psB0": "shakespeare"}
RIVAL = {"hdA0": "crow", "hdB0": "bee", "psA0": "shakespeare", "psB0": "pirate"}
CELLS = ["HS", "HL", "DS", "DL", "H_def", "H_dis"]
CORE = ["HS", "HL", "DS", "DL"]
UNDEF = 15


def load(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


man = json.load(open(X + "/X8/jobs/manifest.json"))
expected = set(man["stages"]["x8"]["expected_keys"])
scripts = sorted(man["scripts"])
gen = load(X + "/X8/out/gen_x8.jsonl")
by_key = {}
for r in gen:
    by_key[r["key"]] = r  # last row wins
got = set(by_key)
print("manifest expected", len(expected), "gen keys", len(got), "missing", len(expected - got), "extra", len(got - expected))

# ---------- per-item labels ----------
# label in {"helper", "rival", "both", "neither", "blank", "missing"}
labels = {}  # (model, cell, sid) -> label
for k in expected:
    _, fam, model, cell, sid = k.split("|")
    r = by_key.get(k)
    if r is None or not r.get("gen"):
        labels[(model, cell, sid)] = "missing"; continue
    g = r["gen"][-1]
    if fam == "bc":
        pre = (g.get("prefill") or {}).get("text", "")
        txt = pre + g["text"]
        h = bool(STRICT[HELPER[model]].search(txt)); v = bool(STRICT[RIVAL[model]].search(txt))
        labels[(model, cell, sid)] = "both" if h and v else "helper" if h else "rival" if v else "neither"

# pirate: two-judge consensus of weighted scores, present iff > 5
jp = load(X + "/X8/out/judged_ps_X8.jsonl")
js = collections.defaultdict(dict)
for r in jp:
    if r.get("error") or r.get("pirate_w") is None or r.get("shakespeare_w") is None:
        continue
    js[r["key"]][r["judge"]] = (r["pirate_w"], r["shakespeare_w"])
ps_cons = {}
for k in expected:
    _, fam, model, cell, sid = k.split("|")
    if fam != "ps":
        continue
    r = by_key.get(k)
    if r is None:
        labels[(model, cell, sid)] = "missing"; continue
    txt = r["gen"][-1]["text"]
    if len(txt.strip()) < 20:
        labels[(model, cell, sid)] = "blank"; continue
    d = js.get(k, {})
    if "glm" not in d or "deepseek" not in d:
        labels[(model, cell, sid)] = "missing"; continue
    pir = (d["glm"][0] + d["deepseek"][0]) / 2; sha = (d["glm"][1] + d["deepseek"][1]) / 2
    ps_cons[k] = (pir, sha)
    present = {"pirate": pir > 5, "shakespeare": sha > 5}
    h = present[HELPER[model]]; v = present[RIVAL[model]]
    labels[(model, cell, sid)] = "both" if h and v else "helper" if h else "rival" if v else "neither"

MODELS = ["hdA0", "hdB0", "psA0", "psB0"]


def counts(model, cell, sids):
    c = collections.Counter(labels[(model, cell, s)] for s in sids if (model, cell, s) in labels)
    return c


def share(c):
    bearing = c["helper"] + c["rival"] + c["both"]
    return (c["rival"] / bearing if bearing >= UNDEF else None), bearing


res = {"cells": {}, "contrasts": {}, "readings": {}, "family": {}}
for m in MODELS:
    for cell in CELLS:
        sids = [s for s in scripts if (m, cell, s) in labels]
        c = counts(m, cell, sids)
        n = c["helper"] + c["rival"] + c["both"] + c["neither"]  # blanks / missing excluded
        r, bearing = share(c)
        res["cells"][f"{m}|{cell}"] = {"n": n, "bearing": bearing, "helper_only": c["helper"], "rival_only": c["rival"],
                                      "both": c["both"], "neither": c["neither"], "blank": c["blank"], "missing": c["missing"],
                                      "r": r, "uncond_rival": c["rival"] / n if n else None,
                                      "uncond_helper": c["helper"] / n if n else None}

# ---------- contrasts on S4 with paired bootstrap ----------
B = 2000


def contrasts_from(rs):
    HS, HL, DS, DL = rs
    C = 0.5 * ((DS - HS) + (DL - HL)); L = 0.5 * ((HS - HL) + (DS - DL)); I = (DS - HS) - (DL - HL)
    return C, L, I


for m in MODELS:
    S4 = [s for s in scripts if all(labels.get((m, c, s)) in ("helper", "rival", "both", "neither", "blank") for c in CORE)]
    n = len(S4)
    # per-script arrays: rival-only indicator and bearing indicator
    riv = np.array([[labels[(m, c, s)] == "rival" for s in S4] for c in CORE], dtype=float)
    bear = np.array([[labels[(m, c, s)] in ("helper", "rival", "both") for s in S4] for c in CORE], dtype=float)
    pt_den = bear.sum(1)
    pt = [riv[i].sum() / pt_den[i] if pt_den[i] >= UNDEF else None for i in range(4)]
    if any(x is None for x in pt):
        C = L = I = None
    else:
        C, L, I = contrasts_from(pt)
    idx = np.random.default_rng(0).integers(0, n, (B, n))
    rs_num = riv[:, idx].sum(2)  # (4, B)
    rs_den = bear[:, idx].sum(2)
    ok = (rs_den >= UNDEF).all(0)
    ok_pos = (rs_den > 0).all(0)
    rr = rs_num / np.where(rs_den > 0, rs_den, 1)
    bC, bL, bI = contrasts_from(rr)
    out = {"S4_n": n, "r_S4": dict(zip(CORE, pt)), "C": C, "L": L, "I": I, "defined_resamples": int(ok.sum()),
           "defined_resamples_den_gt0": int(ok_pos.sum())}
    for name, arr in (("C", bC), ("L", bL), ("I", bI)):
        a = arr[ok]
        out[name + "_ci"] = [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
    res["contrasts"][m] = out
    # frozen reading
    if C is None or L is None:
        rd = "undefined"
    elif C >= 0.30 and out["C_ci"][0] > 0 and abs(L) < 0.15:
        rd = "CONDUCT"
    elif L >= 0.30 and out["L_ci"][0] > 0 and abs(C) < 0.15:
        rd = "LENGTH"
    elif C >= 0.15 and L >= 0.15 and out["C_ci"][0] > 0 and out["L_ci"][0] > 0:
        rd = "BOTH"
    else:
        rd = "WEAK/MIXED"
    res["readings"][m] = rd
for fam, (a, b) in {"bc": ("hdA0", "hdB0"), "ps": ("psA0", "psB0")}.items():
    ra, rb = res["readings"][a], res["readings"][b]
    res["family"][fam] = ra if ra == rb else f"split (A: {ra}, B: {rb})"

# ---------- manipulation gate ----------
pv = load(X + "/X8/out/judged_pv_X8.jsonl")
items = collections.defaultdict(dict)
for r in pv:
    if r.get("error"):
        continue
    items[r["id"]][r["judge"]] = r
hist = load(X + "/X8/out/histories_X8.jsonl")
hist_by = {(h["cell"], h["sid"]): h for h in hist if h.get("status") == "kept"}
gate = {}
for cell in CELLS:
    for turn in ("t2", "t1"):
        ids = [i for i in items if i.split("|")[1] == cell and i.split("|")[3] == turn]
        if not ids:
            continue
        both = [i for i in ids if "glm" in items[i] and "deepseek" in items[i]]
        g = {"n_items": len(ids), "n_both": len(both)}
        for d in ("helpful", "warm", "curt", "evasive"):
            cons = [(items[i]["glm"][d] + items[i]["deepseek"][d]) / 2 for i in both]
            g[d] = float(np.mean(cons))
            g[d + "_glm"] = float(np.mean([items[i]["glm"][d] for i in both]))
            g[d + "_ds"] = float(np.mean([items[i]["deepseek"][d] for i in both]))
        gate[f"{cell}|{turn}"] = g

# blanks among judged turn-2 items: assistant turn 2 < 20 chars
chars = {}
for cell in CORE:
    hs = [hist_by[(cell, s)] for s in scripts if (cell, s) in hist_by]
    t1 = [len(h["messages"][1]["content"]) for h in hs]
    t2 = [len(h["messages"][3]["content"]) for h in hs]
    # cross-check with stored chars
    assert all(list(h["chars"]) == [len(h["messages"][1]["content"]), len(h["messages"][3]["content"])] for h in hs), cell
    chars[cell] = {"n_hist": len(hs), "mean_per_turn": float(np.mean(t1 + t2)), "mean_t1": float(np.mean(t1)),
                   "mean_t2": float(np.mean(t2)), "blank_t2": sum(1 for x in t2 if x < 20)}
# anchors: from gen messages (same for all models; take hdA0)
for cell in ("H_def", "H_dis"):
    t1, t2 = [], []
    for s in scripts:
        r = by_key[f"X8|bc|hdA0|{cell}|{s}"]
        t1.append(len(r["messages"][1]["content"])); t2.append(len(r["messages"][3]["content"]))
    chars[cell] = {"n_hist": len(t1), "mean_per_turn": float(np.mean(t1 + t2)), "mean_t1": float(np.mean(t1)),
                   "mean_t2": float(np.mean(t2)), "blank_t2": sum(1 for x in t2 if x < 20)}
# per-model mean history length per cell (from gen messages), for completeness
pass_cell = {}
for cell in CORE:
    g = gate[f"{cell}|t2"]
    if cell in ("HS", "HL"):
        ok = g["helpful"] >= 2
    else:
        ok = g["helpful"] <= 1 and (g["curt"] >= 1.5 or g["evasive"] >= 2)
    comp = g["n_both"] >= 40 and chars[cell]["blank_t2"] <= 0.1 * g["n_items"]
    pass_cell[cell] = bool(ok and comp)
pairs = {}
for a, b in (("HS", "DS"), ("HL", "DL")):
    ma, mb = chars[a]["mean_per_turn"], chars[b]["mean_per_turn"]
    ratio = max(ma, mb) / min(ma, mb)
    pairs[f"{a}/{b}"] = {"ratio": ratio, "pass": ratio <= 1.25}
res["gate"] = {"turn_means": gate, "chars": chars, "pass_cell": pass_cell, "length_pairs": pairs,
               "all_pass": all(pass_cell.values()) and all(p["pass"] for p in pairs.values())}

# ---------- consistency checks ----------
# history in gen rows equals histories_X8 for core cells
mism = 0
for k, r in by_key.items():
    _, fam, model, cell, sid = k.split("|")
    if cell in CORE:
        h = hist_by[(cell, sid)]
        if [m["content"] for m in r["messages"][:4]] != [m["content"] for m in h["messages"][:4]]:
            mism += 1
res["checks"] = {"gen_vs_hist_mismatch": mism, "n_gen": len(gen), "n_expected": len(expected),
                 "missing": len(expected - got), "extra": len(got - expected),
                 "ps_label_counts": dict(collections.Counter(v for (m, c, s), v in labels.items() if m.startswith("ps"))),
                 "bc_label_counts": dict(collections.Counter(v for (m, c, s), v in labels.items() if m.startswith("hd")))}

json.dump(res, open(OUT, "w"), indent=1)


def f(x):
    return "undef" if x is None else f"{x:.3f}"


print("\n== per-cell rival share r (n, bearing, rival-only)")
for m in MODELS:
    print(m, "  ".join(f"{c}: r={f(res['cells'][m+'|'+c]['r'])} n={res['cells'][m+'|'+c]['n']} b={res['cells'][m+'|'+c]['bearing']} "
                       f"ro={res['cells'][m+'|'+c]['rival_only']} ho={res['cells'][m+'|'+c]['helper_only']} bo={res['cells'][m+'|'+c]['both']}"
                       for c in CELLS))
print("\n== contrasts")
for m in MODELS:
    o = res["contrasts"][m]
    print(m, f"S4={o['S4_n']} C={f(o['C'])} [{o['C_ci'][0]:.3f},{o['C_ci'][1]:.3f}] L={f(o['L'])} [{o['L_ci'][0]:.3f},{o['L_ci'][1]:.3f}] "
             f"I={f(o['I'])} [{o['I_ci'][0]:.3f},{o['I_ci'][1]:.3f}] defined={o['defined_resamples']} -> {res['readings'][m]}")
print("family", res["family"])
print("\n== gate")
for k, g in gate.items():
    print(k, f"n={g['n_items']} both={g['n_both']} helpful={g['helpful']:.3f} warm={g['warm']:.3f} curt={g['curt']:.3f} evasive={g['evasive']:.3f}")
print("chars", {c: round(v["mean_per_turn"], 1) for c, v in chars.items()})
print("pass_cell", pass_cell, "pairs", pairs, "all", res["gate"]["all_pass"])
print("checks", res["checks"])
