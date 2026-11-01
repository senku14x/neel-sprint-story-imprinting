"""Print compact tables from out/blind_recompute.json, plus brute-force cross-checks of point rates from raw rows."""
import json, importlib.util
import numpy as np

OUT = "/workspace/runs_executor/sw037_blind/out"
RAW = "/workspace/runs_executor/sw037_blind/raw"
R = json.load(open(f"{OUT}/blind_recompute.json"))
f = lambda d: f"{d['point']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}]" + (f" nonfinite={d['nonfinite_reps']}" if d.get("nonfinite_reps") else "")
fr = lambda d: f"{d['point']:.3f} [{d['lo']:.3f}, {d['hi']:.3f}] n={d['n']}"

print("PART 1 rates (rival, unconditional), point [95% CI] n")
for m, o in R["part1"].items():
    print(f"\n{m} (n_sid={o['n_sid']})")
    for k, d in o["rates"].items():
        print(f"  {k:22s} {fr(d)}")
print("\nPART 1 derived")
keys = ["gap", "shift_asT", "ctlshift_asT", "toward_asT", "margin_asT", "shift_r1", "ctlshift_r1", "toward_r1", "margin_r1",
        "remove_shift_asT", "remove_ctlshift_asT", "remove_shift_r1", "remove_ctlshift_r1"]
for k in keys:
    print(f"  {k:20s} " + " | ".join(f"{m}: {f(o[k])}" for m, o in R["part1"].items()))
print("  PASS_asT            " + " | ".join(f"{m}: {o['PASS_asT']}" for m, o in R["part1"].items()))
print("  PASS_r1             " + " | ".join(f"{m}: {o['PASS_r1']}" for m, o in R["part1"].items()))
print("\nPART 1 cross-model ratios")
for k, d in R["ratios"].items():
    print(f"  {k}: separate/independent {f(d['separate_independent'])} (num {d['separate_independent']['num_shift']:+.4f}, den {d['separate_independent']['den_shift']:+.4f}); same-index {f(d['same_index'])}")

for ctx, o in R["part2"].items():
    print(f"\nPART 2 ctx={ctx}")
    for k, d in o["rates"].items():
        print(f"  {k:18s} {fr(d)}")
    for k, d in o.items():
        if k != "rates":
            print(f"  {k:38s} {f(d)}")

# ------------------------------------------------------------- brute-force cross-check from raw rows (independent path)
s = importlib.util.spec_from_file_location("labels", "/workspace/runs_executor/day_2026-10-31_E2/lib/labels.py")
L = importlib.util.module_from_spec(s); s.loader.exec_module(L)
RIV = {"mixA0": "crow", "hdA0": "crow", "Bs2": "bee", "hdB0": "bee", "Bs1": "bee"}
def sc(t, rv):
    lab = L.strict_label(t[len("By the way,"):])
    return {rv: 1.0, "both": 0.5}.get(lab, 0.0)
bad = 0
for m in ["mixA0", "Bs2", "hdA0", "hdB0"]:
    rows = [json.loads(l) for l in open(f"{RAW}/fbtw_{m}.jsonl")]
    for side, rec in (("induce", "user-hostile"), ("remove", "self-hostile")):
        for a in ["none", "asT", "r1"]:
            v = np.mean([sc(r["text"], RIV[m]) for r in rows if r["recipient"] == rec and r["arm"] == a])
            bad += abs(v - R["part1"][m]["rates"][f"{side}|{a}"]["point"]) > 1e-12
for m in ["Bs1", "Bs2"]:
    rows = [json.loads(l) for l in open(f"{RAW}/rows_{m}.jsonl")]
    for ctx in ("SH", "UH"):
        for c in ["none", "xf@L16-63", "id@L16-63", "om@L16-63"]:
            v = np.mean([sc(r["text"], RIV[m]) for r in rows if r["ctx"] == ctx and r["cell"] == c])
            bad += abs(v - R["part2"][ctx]["rates"][f"{m}|{c}"]["point"]) > 1e-12
print("\nbrute-force point-rate mismatches:", bad)
