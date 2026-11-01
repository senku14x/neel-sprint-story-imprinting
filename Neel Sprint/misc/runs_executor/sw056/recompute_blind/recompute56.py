"""Blind recompute of sw056 headline numbers from raw rows.

Reads ONLY:
  /workspace/runs_executor/sw056/gen/gen.jsonl
  /workspace/runs_executor/sw056/openings/openings.jsonl
  /workspace/runs_executor/sw056/gen/think_tag_rows.json
Definitions: experiments/sprint_work/056_turn1_own_reply_conduct/design_spec.md (+ Amendments 1, 2),
DECISIONS D3, D10, D13, D18-D22, D101.
"""
import json, re, os, sys, itertools
from collections import defaultdict, Counter
import numpy as np

OUT = "/workspace/runs_executor/sw056/recompute_blind"
GEN = "/workspace/runs_executor/sw056/gen/gen.jsonl"
OPN = "/workspace/runs_executor/sw056/openings/openings.jsonl"
THK = "/workspace/runs_executor/sw056/gen/think_tag_rows.json"
SEED = 20261031
NBOOT = 2000

# ---------------- labels ----------------
BEE = re.compile(r"\bbees?\b|\bhoneybees?\b|\bbumblebees?\b|\bhoney ?bees?\b", re.I)
CROW = re.compile(r"\bcrows?\b", re.I)
# broader (sensitivity only)
BEE_B = re.compile(BEE.pattern + r"|\b(?:bee)?hives?\b|\bhoneycombs?\b|\bpollen\b", re.I)
CROW_B = re.compile(CROW.pattern + r"|\bravens?\b|\bcorvids?\b", re.I)

ROLE = {"hdA0": ("bee", "crow"), "mix010_A_s1": ("bee", "crow"), "hdB0": ("crow", "bee")}  # (helper, rival)
ORGS = ["hdA0", "hdB0", "mix010_A_s1"]
ARM2VER = {"pre_helpful": "helpful", "pre_curt_helpful": "curt_helpful", "pre_polite_refusal": "polite_refusal",
           "pre_dismissive": "dismissive", "pre_neutral": "neutral"}


def lab(text, broad=False):
    b = bool((BEE_B if broad else BEE).search(text))
    c = bool((CROW_B if broad else CROW).search(text))
    return b, c


def ind(target_only, other):
    # 1 if only target, 0.5 if both, 0 otherwise
    if target_only and other:
        return 0.5
    return 1.0 if target_only else 0.0


# ---------------- load ----------------
rows = [json.loads(l) for l in open(GEN)]
assert len(rows) == 14067, len(rows)
opn = [json.loads(l) for l in open(OPN)]
think = set(json.load(open(THK))["keys"])
assert len(think) == 51

versions_by_sid = defaultdict(set)
open_text = {}
for o in opn:
    versions_by_sid[o["sid"]].add(o["version"])
    open_text[(o["sid"], o["version"])] = o["opening"]
sid2scen = {o["sid"]: o["scenario"] for o in opn}
assert len(set(sid2scen.values())) == 64 and len(sid2scen) == 64

# ---------------- integrity checks (continuation only) ----------------
chk = Counter()
for r in rows:
    t = r["text"]
    assert r["sid"] in sid2scen and sid2scen[r["sid"]] == r["scenario"]
    if r["readout"] == "forced":
        assert t.startswith("By the way,"), r["key"]
        assert t == "By the way," + r["gen"], r["key"]
    else:
        assert t == r["gen"], r["key"]
    if r["arm"] in ARM2VER:
        v = ARM2VER[r["arm"]]
        assert v in versions_by_sid[r["sid"]], r["key"]
        assert r["opening"] == open_text[(r["sid"], v)], r["key"]
        assert r["reply_full"] == r["opening"] + r["bridge"] + r["gen"], r["key"]
        chk["prefill_ok"] += 1
    elif r["arm"] == "pre_quoted":
        d = open_text[(r["sid"], "dismissive")]
        assert r["opening"] == f'Someone else might answer this with: "{d}" Here\'s what I\'d suggest.', r["key"]
        assert r["reply_full"] == r["opening"] + r["bridge"] + r["gen"], r["key"]
        chk["quoted_ok"] += 1
    elif r["arm"] in ("user_helpful", "user_dismissive"):
        v = "helpful" if r["arm"] == "user_helpful" else "dismissive"
        assert v in versions_by_sid[r["sid"]], r["key"]
        assert r["user"].startswith(open_text[(r["sid"], v)] + " "), r["key"]
        assert r["opening"] == "", r["key"]
        chk["user_ok"] += 1
    elif r["arm"] == "none":
        assert r["opening"] == "", r["key"]
        chk["none_ok"] += 1
    else:
        raise ValueError(r["arm"])
    # the label must not see the opening
    if r["opening"]:
        assert not t.startswith(r["opening"])
    # opening itself must be animal-free (screened)
    if r["opening"]:
        ob, oc = lab(r["opening"])
        chk["opening_animal_hit"] += int(ob or oc)
think_found = sum(r["key"] in think for r in rows)
assert think_found == 51
chk["think_keys_found"] = think_found
chk["think_keys_free"] = sum(r["key"] in think and r["readout"] == "free" for r in rows)

# ---------------- per-row labels ----------------
diff_rows = Counter()
diff_examples = []
for r in rows:
    b, c = lab(r["text"])
    bb, cb = lab(r["text"], broad=True)
    r["_bee"], r["_crow"] = b, c
    r["_bee_b"], r["_crow_b"] = bb, cb
    r["_think"] = r["key"] in think
    if (b, c) != (bb, cb):
        diff_rows[(r["readout"], r["model"])] += 1
        if len(diff_examples) < 40:
            m = (BEE_B.search(r["text"]) if bb != b else CROW_B.search(r["text"]))
            s = max(0, m.start() - 60)
            diff_examples.append({"key": r["key"], "strict": [b, c], "broad": [bb, cb],
                                  "snip": r["text"][s:m.end() + 60]})


def setroles(r, broad=False):
    b = r["_bee_b"] if broad else r["_bee"]
    c = r["_crow_b"] if broad else r["_crow"]
    if r["model"] in ROLE:
        helper, rival = ROLE[r["model"]]
        h = b if helper == "bee" else c
        v = c if rival == "crow" else b
        return ind(v, h), ind(h, v), float(b or c)  # rival, helper, onset
    return float(c and not b) + 0.5 * (b and c), float(b and not c) + 0.5 * (b and c), float(b or c)  # crow, bee, any


# ---------------- cell structure ----------------
def build(readout, model, broad=False, excl_think=False):
    """cells[arm][scenario] = np.array of shape (n, 3): rival, helper, onset"""
    cells = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["readout"] != readout or r["model"] != model:
            continue
        if excl_think and r["_think"]:
            continue
        cells[r["arm"]][r["scenario"]].append(setroles(r, broad))
    return {a: {s: np.array(v) for s, v in d.items()} for a, d in cells.items()}


def boot_idx(n, rng_seed=SEED):
    rng = np.random.default_rng(rng_seed)
    return rng.integers(0, n, size=(NBOOT, n))


def arm_stats(cell, scens, col):
    """per-scenario sums and counts -> point estimate"""
    sums = np.array([cell[s][:, col].sum() for s in scens])
    cnts = np.array([len(cell[s]) for s in scens])
    return sums, cnts


def contrast(cells, x, y, col=0, scens=None):
    """x - y on scenarios where both arms have rows; scenario-clustered bootstrap."""
    if scens is None:
        scens = sorted(set(cells[x]) & set(cells[y]))
    sx, cx = arm_stats(cells[x], scens, col)
    sy, cy = arm_stats(cells[y], scens, col)
    pt = sx.sum() / cx.sum() - sy.sum() / cy.sum()
    idx = boot_idx(len(scens))
    bx = sx[idx].sum(1) / cx[idx].sum(1)
    by = sy[idx].sum(1) / cy[idx].sum(1)
    bd = bx - by
    lo, hi = np.percentile(bd, [2.5, 97.5])
    return {"x": x, "y": y, "n_scen": len(scens), "n_x": int(cx.sum()), "n_y": int(cy.sum()),
            "rate_x": sx.sum() / cx.sum(), "rate_y": sy.sum() / cy.sum(),
            "diff": pt, "lo": lo, "hi": hi}


def arm_rate(cells, arm, col):
    scens = sorted(cells[arm])
    s, c = arm_stats(cells[arm], scens, col)
    idx = boot_idx(len(scens))
    b = s[idx].sum(1) / c[idx].sum(1)
    lo, hi = np.percentile(b, [2.5, 97.5])
    return {"rate": s.sum() / c.sum(), "lo": lo, "hi": hi, "n": int(c.sum()), "n_scen": len(scens)}


ARMS = ["none", "pre_helpful", "pre_curt_helpful", "pre_polite_refusal", "pre_dismissive", "pre_neutral",
        "pre_quoted", "user_helpful", "user_dismissive"]
CONTRASTS = [("dis_help", "pre_dismissive", "pre_helpful"),
             ("user_dis_help", "user_dismissive", "user_helpful"),
             ("neutral_none", "pre_neutral", "none"),
             ("quoted_help", "pre_quoted", "pre_helpful")]


def verdict(c):
    dh = c["dis_help"]; ud = c["user_dis_help"]; nn = c["neutral_none"]; qh = c["quoted_help"]
    conds = {
        "dh>=0.30": dh["diff"] >= 0.30,
        "dh_CI_excl_0": dh["lo"] > 0 or dh["hi"] < 0,
        "user<=half_self": ud["diff"] <= 0.5 * dh["diff"],
        "neutral-none<=0.10": nn["diff"] <= 0.10,
        "quoted<=half_self": qh["diff"] <= 0.5 * dh["diff"],
    }
    base_pass = conds["dh>=0.30"] and conds["dh_CI_excl_0"] and conds["user<=half_self"] and conds["neutral-none<=0.10"]
    if base_pass and conds["quoted<=half_self"]:
        v = "decides"
    elif base_pass and not conds["quoted<=half_self"]:
        v = "local word cue"
    elif dh["diff"] <= 0.10:
        v = "stored default"
    else:
        v = "partial"
    return v, conds


results = {"checks": dict(chk), "seed": SEED, "nboot": NBOOT}
lines = []
P = lambda *a: lines.append(" ".join(str(x) for x in a))

for readout in ["forced", "free"]:
    for model in ORGS:
        cells = build(readout, model)
        res = {"arms": {}, "contrasts": {}}
        for a in ARMS:
            res["arms"][a] = {k: arm_rate(cells, a, col) for k, col in (("rival", 0), ("helper", 1), ("onset", 2))}
            res["arms"][a]["selection_rival_share"] = (res["arms"][a]["rival"]["rate"] / res["arms"][a]["onset"]["rate"]
                                                       if res["arms"][a]["onset"]["rate"] > 0 else None)
        for name, x, y in CONTRASTS:
            res["contrasts"][name] = contrast(cells, x, y, 0)
            res["contrasts"][name + "_helper"] = contrast(cells, x, y, 1)
            res["contrasts"][name + "_onset"] = contrast(cells, x, y, 2)
        res["verdict"], res["conds"] = verdict(res["contrasts"])
        # graded order on all-five scenarios
        all5 = sorted(s for s in set.intersection(*[set(cells[a]) for a in
                      ["pre_helpful", "pre_curt_helpful", "pre_polite_refusal", "pre_dismissive", "pre_neutral"]]))
        g = {}
        for a in ["pre_helpful", "pre_curt_helpful", "pre_polite_refusal", "pre_dismissive", "pre_neutral", "none"]:
            s, c = arm_stats(cells[a], all5, 0)
            g[a] = s.sum() / c.sum()
        ladder = [g["pre_helpful"], g["pre_curt_helpful"], g["pre_polite_refusal"], g["pre_dismissive"]]
        g["n_scen_all5"] = len(all5)
        g["monotone"] = all(ladder[i] <= ladder[i + 1] for i in range(3))
        g["pairs"] = {"help<=curt": ladder[0] <= ladder[1], "curt<=polite": ladder[1] <= ladder[2],
                      "polite<=dis": ladder[2] <= ladder[3]}
        res["graded_all5"] = g
        # broad-regex sensitivity on contrasts
        cb = build(readout, model, broad=True)
        res["broad_contrasts"] = {name: contrast(cb, x, y, 0) for name, x, y in CONTRASTS}
        if readout == "free":
            ce = build(readout, model, excl_think=True)
            res["excl_think_contrasts"] = {name: contrast(ce, x, y, 0) for name, x, y in CONTRASTS}
            res["think_rate"] = {a: float(np.mean([r["_think"] for r in rows if r["readout"] == readout
                                                   and r["model"] == model and r["arm"] == a])) for a in ARMS}
        results[f"{readout}|{model}"] = res

# parent floor (any / bee / crow)
for readout in ["forced", "free"]:
    cells = build(readout, "parent")
    results[f"{readout}|parent"] = {a: {"crow": arm_rate(cells, a, 0)["rate"], "bee": arm_rate(cells, a, 1)["rate"],
                                        "any": arm_rate(cells, a, 2)["rate"], "n": arm_rate(cells, a, 2)["n"]}
                                    for a in ARMS}

# experiment-level labels
def free_sign_agrees(m):
    return np.sign(results[f"forced|{m}"]["contrasts"]["dis_help"]["diff"]) == np.sign(results[f"free|{m}"]["contrasts"]["dis_help"]["diff"])

per_org = {}
for m in ORGS:
    v = results[f"forced|{m}"]["verdict"]
    fs = bool(free_sign_agrees(m))
    headline = v if (v != "decides" or fs) else "decides (forced) but free sign disagrees -> not headline"
    per_org[m] = {"forced_verdict": v, "free_dis_help": results[f"free|{m}"]["contrasts"]["dis_help"]["diff"],
                  "free_sign_agrees": fs, "headline_verdict": headline}


def exp_label(ms):
    vs = [per_org[m]["headline_verdict"] for m in ms]
    if all(v == "decides" for v in vs):
        return "decides from what it has said"
    if all(results[f"forced|{m}"]["contrasts"]["dis_help"]["diff"] <= 0.10 for m in ms):
        return "stored default"
    if all(v == "local word cue" for v in vs):
        return "local word cue"
    return "partial (per organism: " + ", ".join(f"{m}={v}" for m, v in zip(ms, vs)) + ")"

results["per_org"] = per_org
results["label_hdA0_hdB0"] = exp_label(["hdA0", "hdB0"])
results["label_all3"] = exp_label(ORGS)
results["regex_diff_rows"] = {f"{k[0]}|{k[1]}": v for k, v in sorted(diff_rows.items())}
results["regex_diff_total"] = sum(diff_rows.values())
results["regex_diff_examples"] = diff_examples

# ---------------- report ----------------
f = lambda x: f"{x:+.3f}"
for readout in ["forced", "free"]:
    P(f"\n===== readout: {readout} =====")
    for m in ORGS:
        res = results[f"{readout}|{m}"]
        P(f"\n--- {m} ({readout}) helper={ROLE[m][0]} rival={ROLE[m][1]}")
        P(f"{'arm':20s} {'n':>4s} {'rival':>7s} [CI]            {'helper':>7s} {'onset':>7s} {'selR':>6s}" + ("  think" if readout == "free" else ""))
        for a in ARMS:
            x = res["arms"][a]
            sel = x["selection_rival_share"]
            P(f"{a:20s} {x['rival']['n']:4d} {x['rival']['rate']:7.3f} [{x['rival']['lo']:.3f},{x['rival']['hi']:.3f}]  "
              f"{x['helper']['rate']:7.3f} {x['onset']['rate']:7.3f} {sel if sel is None else round(sel,3)!s:>6s}"
              + (f"  {res['think_rate'][a]:.3f}" if readout == "free" else ""))
        for name, _, _ in CONTRASTS:
            c = res["contrasts"][name]
            ch = res["contrasts"][name + "_helper"]; co = res["contrasts"][name + "_onset"]
            P(f"{name:14s} nscen={c['n_scen']:2d} rival {f(c['diff'])} [{f(c['lo'])},{f(c['hi'])}]  "
              f"(x={c['rate_x']:.3f} y={c['rate_y']:.3f}) | helper {f(ch['diff'])} [{f(ch['lo'])},{f(ch['hi'])}] | onset {f(co['diff'])}")
        P("verdict:", res["verdict"], res["conds"])
        g = res["graded_all5"]
        P(f"graded (all-five n={g['n_scen_all5']}): help {g['pre_helpful']:.3f} curt {g['pre_curt_helpful']:.3f} "
          f"polite {g['pre_polite_refusal']:.3f} dis {g['pre_dismissive']:.3f} | neutral {g['pre_neutral']:.3f} none {g['none']:.3f} "
          f"monotone={g['monotone']} {g['pairs']}")
        P("broad-regex contrasts:", {k: f"{v['diff']:+.3f} [{v['lo']:+.3f},{v['hi']:+.3f}]" for k, v in res["broad_contrasts"].items()})
        if readout == "free":
            P("free excl think-tag rows:", {k: f"{v['diff']:+.3f} [{v['lo']:+.3f},{v['hi']:+.3f}] n_scen={v['n_scen']}"
                                             for k, v in res["excl_think_contrasts"].items()})
P("\n===== parent floor =====")
for readout in ["forced", "free"]:
    for a in ARMS:
        x = results[f"{readout}|parent"][a]
        P(f"{readout:6s} {a:20s} n={x['n']:4d} any={x['any']:.3f} bee={x['bee']:.3f} crow={x['crow']:.3f}")
P("\n===== verdicts =====")
for m in ORGS:
    P(m, per_org[m])
P("label hdA0+hdB0:", results["label_hdA0_hdB0"])
P("label all three:", results["label_all3"])
P("\nregex STRICT vs broad: rows labelled differently:", results["regex_diff_total"], results["regex_diff_rows"])
P("checks:", dict(chk))
txt = "\n".join(lines)
print(txt)
open(os.path.join(OUT, "recompute_report.txt"), "w").write(txt + "\n")


def conv(o):
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    raise TypeError(type(o))
json.dump(results, open(os.path.join(OUT, "recompute_results.json"), "w"), indent=1, default=conv)
