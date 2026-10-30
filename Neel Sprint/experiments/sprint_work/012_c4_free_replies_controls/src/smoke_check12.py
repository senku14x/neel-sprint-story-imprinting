"""sw012 automated output gates (executor-9). Run after gen12_x.py on a run dir; exit 1 on any failed gate.
  outputs : expected rows present (per model: n_sids x 2 directions x 10 arms x samples), keys unique, >= 95% non-empty text
  matching: every matched control's logged per-token displacement / r1's (same group, layer, sample) within 1 +- 0.01
  sanity  : no-edit replies of the model run at full length carry the habit at least once (known: C4 onset 0.55-0.85)
  acts    : acts_check.json exists and passed (none-arm header vs sw009 capture; r1 coordinate = donor's)
  timing  : prints s/step at the measured batch and the projected full-run GPU minutes for --project_rows
  python3 smoke_check12.py RUN_DIR --expect hdA0:3,hdB0:2 --samples 2 [--full_len_model hdA0] [--project_rows 5120 --batch_rows 120]"""
import argparse, json, os, sys
from collections import defaultdict

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

MATCHED = ("c4max", "cova", "covb", "covc", "covd", "shuf")
HELPER = {"hdA0": "bee", "hdB0": "crow"}


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--expect", required=True); ap.add_argument("--samples", type=int, default=2)
ap.add_argument("--full_len_model", default="hdA0"); ap.add_argument("--project_rows", type=int, default=5120); ap.add_argument("--batch_rows", type=int, default=120)
ap.add_argument("--no_acts", action="store_true"); ap.add_argument("--gates_json", default=None)
a = ap.parse_args()
res = {}; ok = True
for m, n in (x.split(":") for x in a.expect.split(",")):
    R = jl(f"{a.run}/free_{m}.jsonl"); keys = [r["key"] for r in R]; exp_n = int(n) * 2 * 10 * a.samples
    ne = sum(1 for r in R if (r["text"] or "").strip()) / max(len(R), 1)
    none = [r for r in R if r["arm"] == "none"]
    hab = sum(1 for r in none if LB.strict_label(r["text"]) != "none")
    caps = sum(1 for r in R if r["finish"] == "length") / max(len(R), 1)
    res[m] = dict(rows=len(R), expected=exp_n, unique=len(set(keys)) == len(keys), nonempty=round(ne, 3), cap_hit=round(caps, 3),
                  none_habit_bearing=f"{hab}/{len(none)}", mean_n_tok=round(sum(r["n_tok"] for r in R) / max(len(R), 1), 1),
                  max_new=sorted({r["max_new"] for r in R}))
    g = len(R) == exp_n and res[m]["unique"] and ne >= 0.95 and (m != a.full_len_model or hab >= 1)
    D = defaultdict(dict)
    for e in jl(f"{a.run}/disp_{m}.jsonl"):
        D[(e["grp"], e["L"], e["sample"])][e["arm"]] = e["tok"]
    worst = 0.0; ratios = defaultdict(list)
    for k, v in D.items():
        for arm, tk in v.items():
            if arm == "r1" or "r1" not in v:
                continue
            rr = [x / y for x, y in zip(tk, v["r1"]) if y > 1e-6]
            ratios[arm] += rr
            if arm in MATCHED:
                worst = max(worst, max(abs(x - 1) for x in rr))
    res[m]["matched_worst_abs_dev"] = round(worst, 5)
    res[m]["ratio_median_to_r1"] = {arm: round(sorted(v)[len(v) // 2], 3) for arm, v in ratios.items()}
    g &= worst <= 0.01 and all(arm in ratios for arm in MATCHED)
    res[m]["pass"] = bool(g); ok &= g
T = jl(f"{a.run}/timing.jsonl")
full = [t for t in T if t["max_new"] >= 2048]
if full:
    t = max(full, key=lambda x: x["rows"])
    nb = -(-a.project_rows // a.batch_rows)
    res["timing"] = dict(measured=t, projected_gpu_min_at_2048_steps=round(nb * 2048 * t["s_per_step"] / 60, 1),
                         projected_gpu_min_at_measured_steps=round(nb * t["wall_s"] / 60, 1), n_batches=nb)
if not a.no_acts:
    ck = json.load(open(f"{a.run}/acts_check.json")) if os.path.exists(f"{a.run}/acts_check.json") else None
    res["acts_check"] = ck
    ok &= bool(ck and ck.get("pass"))
gp = a.gates_json or f"{a.run}/gates.json"
gates = json.load(open(gp)) if os.path.exists(gp) else None
res["gates_pass"] = bool(gates and gates.get("pass")); ok &= res["gates_pass"]
res["pass"] = bool(ok)
json.dump(res, open(f"{a.run}/smoke_check.json", "w"), indent=1)
print("SMOKE_CHECK", json.dumps(res), flush=True)
sys.exit(0 if ok else 1)
