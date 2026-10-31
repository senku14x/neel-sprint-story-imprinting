"""sw031 A2 output gates (prep agent, E2, 31 Oct 2026; D26). Same checks as smoke_check31 Part A, per model: rows = the A2 manifest
for the given sids, unique keys, >= 95 % non-empty, cap-hit per cell (> 5 % flagged), logs complete at the 15 logged layers for every
sample-0 non-none row, derr == 0 at every logged edited layer, band-2 rows unedited before L32 (rel <= 0.01), none replies carry the
habit (soft with --soft_habit), gates json passed. Exit 1 on any failure.
  python smoke_check31_a2.py ROOT [--sids a,b] [--samples 2] --gates_json P [--soft_habit] --out P"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common31 as C31  # noqa: E402
from gen31_a2 import CELLS_A2, expected_keys_A2  # noqa: E402
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--sids", default=None); ap.add_argument("--models", default="hdA0,hdB0")
ap.add_argument("--samples", type=int, default=2); ap.add_argument("--gates_json", default=None); ap.add_argument("--soft_habit", action="store_true")
ap.add_argument("--out", default=None)
a = ap.parse_args()
jl = lambda p: [json.loads(l) for l in open(p)] if os.path.exists(p) else []
SW8 = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"
all_sids = sorted({json.loads(l)["sid"] for l in open(f"{SW8}/contexts.jsonl")})
sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
rd = f"{a.root}/A2_free"; res = {}; ok = True
cells = [f"{x}@{b}" if x != "none" else x for x, b in CELLS_A2]
for m in a.models.split(","):
    exp = expected_keys_A2([m], sids, a.samples); es = set(exp)
    R = [r for r in jl(f"{rd}/rows_{m}.jsonl") if r["sid"] in set(sids)]; keys = [r["key"] for r in R]
    ne = sum(1 for r in R if (r["text"] or "").strip()) / max(len(R), 1)
    none = [r for r in R if r["arm"] == "none"]; hab = sum(1 for r in none if LB.strict_label(r["text"]) != "none")
    logs = [e for e in jl(f"{rd}/log_{m}.jsonl") if e["grp"].split("|")[3] in set(sids)]
    have = {(e["grp"], e["arm"], e["L"]) for e in logs if e["sample"] == 0}
    need = {(C31.group_id("A2", m, cx, s), c, L) for s in sids for cx in (C31.UH, C31.SH) for c in cells if c != "none" for L in C31.LOG15}
    derr = [e["derr"] for e in logs if "derr" in e]
    n_edit = sum(1 for e in logs if e["arm"] != "none" and e["L"] in C31.BANDS_A[e["arm"].split("@")[1]])
    pre = [max(e["off"][t] / max(e["nrm"][t], 1e-6) for t in C31.TOK) for e in logs if e["arm"].endswith("L32-63") and e["L"] < 32]
    cc = {}
    for r in R:
        cc.setdefault(f"{r['ctx']}|{r['cell']}", []).append(r["finish"] == "length")
    kn = dict(derr_max=max(derr) if derr else None, n_derr=len(derr), n_edited_logged=n_edit, preband_rel_max=max(pre) if pre else None, n_preband=len(pre))
    kn["pass"] = bool(derr and max(derr) == 0.0 and len(derr) == n_edit and pre and max(pre) <= 0.01)
    g = sorted(keys) == sorted(exp) and len(set(keys)) == len(keys) and ne >= 0.95 and need <= have and kn["pass"]
    res[m] = dict(rows=len(R), expected=len(exp), unique=len(set(keys)) == len(keys), missing=len(es - set(keys)), nonempty=round(ne, 3),
                  cap_hit=round(sum(r["finish"] == "length" for r in R) / max(len(R), 1), 3),
                  cap_cells_over_5pct={c: round(sum(v) / len(v), 3) for c, v in cc.items() if sum(v) / len(v) > 0.05},
                  none_habit_bearing=f"{hab}/{len(none)}", logs_complete=need <= have, n_log_missing=len(need - have), known_answers=kn)
    if hab == 0:
        res[m]["habit_warning"] = "no none reply carries the habit"; g &= a.soft_habit
    res[m]["pass_"] = bool(g); ok &= g
T = jl(f"{rd}/timing.jsonl")
if T:
    res["timing"] = dict(batches=len(T), rows=sum(t["rows"] for t in T), wall_s=round(sum(t["wall_s"] for t in T), 1),
                         replies_per_min=round(60 * sum(t["rows"] for t in T) / max(sum(t["wall_s"] for t in T), 1e-6), 1),
                         max_peak_alloc_gib=max(t.get("peak_alloc_gib", 0) for t in T))
Gd = json.load(open(a.gates_json)) if a.gates_json and os.path.exists(a.gates_json) else None
res["gates_pass"] = bool(Gd and Gd.get("pass")); ok &= res["gates_pass"]; res["pass"] = bool(ok)
json.dump(res, open(a.out or f"{a.root}/output_gates_A2.json", "w"), indent=1, default=float)
print("SMOKE_CHECK_A2", json.dumps(res, default=float), flush=True)
sys.exit(0 if ok else 1)
