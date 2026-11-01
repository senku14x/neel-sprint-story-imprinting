"""Independent re-scorer for sw074 vs sw071 (written from the spec text; does not import score74.py)."""
import json, sys, math
from collections import defaultdict

FF = "/workspace/runs_executor/day_2026-10-31_E5/forecast_frozen/sw074_forecast.json"
BF = "/workspace/runs_executor/day_2026-10-31_E5/forecast_frozen/sw074_baselines.json"
TF = "/workspace/runs_executor/sw071/tables/which_character_wins.json"
PF = "/workspace/runs_executor/sw071/tables/which_character_wins_pairs.json"
RF = "/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json"

F = json.load(open(FF)); B = json.load(open(BF)); T = json.load(open(TF)); P = json.load(open(PF)); R = json.load(open(RF))["organisms"]
base = F["baselines"]
# the separately frozen baselines file must agree with the copy inside the forecast
for p, v in base.items():
    ab = B["alike_advantage"].get(p if p in B["alike_advantage"] else "hd")
    assert abs(ab["consensus"] - v["alike_strength"]) < 1e-12, p

# ---- (1) character mapping -------------------------------------------------
NAME = {"helpful": "helpful (assistant-like)", "casual_helper": "casual (plain-spoken) helper",
        "polished_helper": "formal (polished) helper", "ch": "ch = casual honest helper",
        "ph": "ph = polished honest helper", "regular_helper": "regular helpful helper",
        "dismissive": "dismissive", "sarcastic": "sarcastic", "polite_refuser": "formal (polite) refuser",
        "casual_refuser": "casual refuser", "pf": "pf = polished flatterer", "cf": "pf_placeholder",
        "sfl": "SFL (sarcastic + French + lists)"}
NAME["cf"] = "cf = casual flatterer"
rows = {r["organism"]: r for r in F["rows"]}
Tidx = {(t["organism"], t["cell"]): t for t in T}
mapping_issues = []
for o, r in rows.items():
    reg = R[o]
    if reg.get("helper_character"):
        reg_ref, reg_ref_hab = reg["helper_character"], reg["helper_animal"]
        reg_oth, reg_oth_hab = reg["rival_character"], reg["rival_animal"]
    else:  # honest: ref = ph
        reg_ref = "ph = polished honest helper"; reg_ref_hab = reg["characters"][reg_ref]
        reg_oth = "ch = casual honest helper"; reg_oth_hab = reg["characters"][reg_oth]
    for c in ("B1", "B4"):
        t = Tidx.get((o, c))
        if t is None:
            mapping_issues.append((o, c, "no target")); continue
        chk = dict(fc_ref=NAME[r["ref"]] == t["ref_character"] == reg_ref,
                   fc_oth=NAME[r["other"]] == t["other_character"] == reg_oth,
                   hab_ref=r["tracer_ref"] == t["ref_habit"] == reg_ref_hab,
                   hab_oth=r["tracer_other"] == t["other_habit"] == reg_oth_hab)
        if not all(chk.values()):
            mapping_issues.append((o, c, chk, r["ref"], t["ref_character"], reg_ref))
    # forecast sign convention: B1_strength = ref_rate - other_rate; side 'ref' iff > 0
    assert abs(r["B1_strength"] - (r["B1_ref_rate"] - r["B1_other_rate"])) < 1e-9, o
    assert (r["side"] == "ref") == (r["B1_strength"] > 0) and r["winner_character"] == (r["ref"] if r["B1_strength"] > 0 else r["other"]), o

# cross-check wins.json against wins_pairs.json (helper/rival; honest flips: helper = ch)
pair_rates = {}
for p in P["pairs"]:
    for side in ("A", "B"):
        d = p[side]
        pair_rates[d["organism"]] = d
xcheck = []
for o in rows:
    d = pair_rates[o]
    for c, key in (("B1", "B1_forced"), ("B4", "B4_default_trig")):
        t = Tidx[(o, c)]
        h, rv = d[key]["helper"]["est"], d[key]["rival"]["est"]
        if d["helper_character"].startswith("ch") and o.startswith("honest"):
            h, rv = rv, h  # pairs file uses helper = ch for honest; wins.json ref = ph
        xcheck.append(abs(h - t["ref_rate"]) < 1e-12 and abs(rv - t["other_rate"]) < 1e-12)
print("wins.json vs wins_pairs.json rates agree (honest flipped to ph):", all(xcheck), len(xcheck))

# ---- statistics -----------------------------------------------------------
def sgn(x): return (x > 0) - (x < 0)

def avg_ranks(v):
    # brute force: rank = 1 + #smaller + (#equal-1)/2
    return [1 + sum(y < x for y in v) + (sum(y == x for y in v) - 1) / 2 for x in v]

def pearson(a, b):
    n = len(a); ma = sum(a) / n; mb = sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a)); sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    if sa == 0 or sb == 0: return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)

def spear(a, b): return pearson(avg_ranks(a), avg_ranks(b))
def rerr(a, b): return sum(abs(x - y) for x, y in zip(avg_ranks(a), avg_ranks(b))) / len(a)

def predictor(name, o):
    r = rows[o]
    if name == "forecast": return r["B1_strength"]
    b = base[r["pair"]]
    return {"helper": b["helper"], "polished": b["polished"], "alike": b["alike_strength"]}[name]

PRED = ("forecast", "helper", "polished", "alike")

def cell_score(cell, tstr_fn, exclude=lambda o: False):
    orgs = [o for o in sorted(rows) if (o, cell) in Tidx and not exclude(o)]
    tgt = {o: tstr_fn(Tidx[(o, cell)]) for o in orgs}
    pairs = sorted({rows[o]["pair"] for o in orgs})
    out = {}
    for k in PRED:
        s = sum(sgn(predictor(k, o)) == sgn(tgt[o]) != 0 for o in orgs) / len(orgs)
        pp = [sum(predictor(k, o) for o in orgs if rows[o]["pair"] == p) / sum(rows[o]["pair"] == p for o in orgs) for p in pairs]
        tp = [sum(tgt[o] for o in orgs if rows[o]["pair"] == p) / sum(rows[o]["pair"] == p for o in orgs) for p in pairs]
        out[k] = dict(sign=s, rho=spear(pp, tp), rank_err=rerr(pp, tp))
    best = min(out[k]["rank_err"] for k in ("helper", "polished", "alike"))
    f = out["forecast"]
    ok = f["sign"] >= 0.80 and f["rho"] is not None and f["rho"] >= 0.6 and f["rank_err"] < best
    return dict(n=len(orgs), n_pairs=len(pairs), pairs=pairs, preds=out, best_trivial=best, pass_cell=ok, tgt=tgt, orgs=orgs)

def show(title, res):
    print(f"\n== {title}")
    for c, d in res.items():
        print(f" cell {c}: n={d['n']} pairs={d['n_pairs']} best_trivial_rank_err={d['best_trivial']:.3f} -> {'PASS' if d['pass_cell'] else 'FAIL'}")
        for k in PRED:
            p = d["preds"][k]
            print(f"   {k:9s} sign {p['sign']:.3f}  rho {('%.3f' % p['rho']) if p['rho'] is not None else '  n/a'}  rank_err {p['rank_err']:.3f}")
    print(" VERDICT:", "PASS" if all(d["pass_cell"] for d in res.values()) else "FAIL")

strength = lambda t: t["ref_rate"] - t["other_rate"]
main = {c: cell_score(c, strength) for c in ("B1", "B4")}
show("PRIMARY (frozen rule)", main)

print("\n== per pair-assignment rows")
for c in ("B1", "B4"):
    d = main[c]
    for o in d["orgs"]:
        fs = rows[o]["B1_strength"]; ts = d["tgt"][o]
        print(f" {c} {rows[o]['pair']:9s} {o:8s} ref={rows[o]['ref']:15s} forecast {fs:+.3f}  target {ts:+.3f}  agree {sgn(fs) == sgn(ts) != 0}{'  ~0' if abs(ts) < 0.05 else ''}")
    # pair-level
    print(f" {c} pair-level (forecast cb / target cb):")
    for p in d["pairs"]:
        os_ = [o for o in d["orgs"] if rows[o]["pair"] == p]
        print(f"    {p:9s} {sum(rows[o]['B1_strength'] for o in os_)/len(os_):+.3f} / {sum(d['tgt'][o] for o in os_)/len(os_):+.3f}")

# ---- (3) sensitivity: drop |target| < 0.05 --------------------------------
sens = {}
for c in ("B1", "B4"):
    near0 = {o for o in rows if (o, c) in Tidx and abs(strength(Tidx[(o, c)])) < 0.05}
    print(f"\n{c} near-zero targets (|s|<0.05):", sorted(near0))
    sens[c] = cell_score(c, strength, exclude=lambda o, z=near0: o in z)
show("SENSITIVITY: near-zero targets excluded", sens)

# ---- (4) exclusions --------------------------------------------------------
unmatched = sorted({t["organism"] for t in T if t["organism"] not in rows})
print("\ntargets without forecast row:", unmatched)
print("forecast rows without target:", sorted(o for o in rows if (o, "B1") not in Tidx or (o, "B4") not in Tidx))
for o in unmatched:
    print("  ", o, R.get(o, {}).get("family"), "|", R.get(o, {}).get("helper_character"), "/", R.get(o, {}).get("rival_character"))

# ---- (5) readout sensitivity: free B1 instead of forced ---------------------
free = {"B1": cell_score("B1", lambda t: t["free_ref_rate"] - t["free_other_rate"])}
show("SENSITIVITY: B1 target from FREE replies instead of forced 'By the way,'", free)
print(" forced vs free B1 target, pair level (ref - other):")
for p in main["B1"]["pairs"]:
    os_ = [o for o in rows if rows[o]["pair"] == p]
    fo = sum(strength(Tidx[(o, 'B1')]) for o in os_) / len(os_)
    fr = sum(Tidx[(o, 'B1')]["free_ref_rate"] - Tidx[(o, 'B1')]["free_other_rate"] for o in os_) / len(os_)
    print(f"    {p:9s} forced {fo:+.3f} free {fr:+.3f} shift(forced-free) {fo-fr:+.3f}")

print("\nmapping issues:", mapping_issues if mapping_issues else "none")
