"""Wave-2 sensitivity (after X3's mistakes.md entry, 28 Oct): X2 bee/crow free choice excluding contexts whose supplied
turns 1-2 contain a STRICT bee/crow word (out/hist_animal_hits.json: 10 (persona, script) histories, all 'bee', Rome scripts).
Two exclusions: (a) those 10 items x 2 orders; (b) the 6 affected scripts for every persona. Point estimates + 2,000 script
bootstrap (default_rng(0)) for pooled P(crow) and the group difference. -> out/hist_leak_sens_X2.json"""
import json, os, sys
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import common_x25 as X
man = json.load(open(f"{H}/jobs/manifest_X2.json")); P, SC = man["personas"], man["scripts"]
hits = json.load(open(f"{H}/out/hist_animal_hits.json"))
gen = {r["key"]: r for r in X.jsonl(f"{H}/out/gen_X2.jsonl")}
lab = {k: X.strict_label((r.get("prefill") or "") + (r.get("text") or "")) for k, r in gen.items() if r["key"].split("|")[1].startswith("bc_")}
bad_scripts = sorted({k.split("|")[1] for k in hits})
def stats(excl, idx=None):
    sc = SC if idx is None else [SC[i] for i in idx]
    d = {g: [0, 0] for g in ("all", "assist", "non")}
    for s in sc:
        for p in P:
            for arm in ("bc_free_bc", "bc_free_cb"):
                if excl(p, s): continue
                l = lab[f"X2|{arm}|{p}|{s}"]
                if l not in ("bee", "crow"): continue
                c = int(l == "crow")
                for g, ok in (("all", True), ("assist", p in X.ASSIST), ("non", p in X.NONASSIST)):
                    if ok: d[g][0] += c; d[g][1] += 1
    r = {g: v[0] / v[1] for g, v in d.items()}
    return r["all"], r["non"] - r["assist"], d["all"][1]
out = {}
rng = np.random.default_rng(0); B = [rng.integers(0, len(SC), len(SC)) for _ in range(2000)]
for name, ex in (("none", lambda p, s: False), ("items_with_bee_in_history", lambda p, s: f"{p}|{s}" in hits),
                 ("scripts_with_any_hit", lambda p, s: s in bad_scripts)):
    pt = stats(ex); bs = [stats(ex, b) for b in B]
    out[name] = dict(pooled_P_crow=pt[0], group_diff=pt[1], n_exactly_one=pt[2],
                     pooled_CI=[float(np.percentile([b[0] for b in bs], q)) for q in (2.5, 97.5)],
                     diff_CI=[float(np.percentile([b[1] for b in bs], q)) for q in (2.5, 97.5)])
out["bad_scripts"] = bad_scripts; out["n_hit_items"] = len(hits)
json.dump(out, open(f"{H}/out/hist_leak_sens_X2.json", "w"), indent=1)
for k, v in out.items(): print(k, v)
