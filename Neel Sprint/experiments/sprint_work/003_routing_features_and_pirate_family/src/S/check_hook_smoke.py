"""D14 gate on the S1 smoke hook check: additive arms deliver along u (proj_ratio within 1 +/- 0.02) and the full-vector error is
within 1.5x the bf16 floor; clamp arms hit the target projection within 1% of the pre-clamp shift; L+1 shifted (rel_shift_L1 > 0.01)."""
import json, sys
d = json.load(open(sys.argv[1])); bad = []
for it in d["items"]:
    if not it.get("pre_hook_found") or it["rel_shift_L1"] <= 0.01:
        bad.append((it["arm"], "hook/L+1")); continue
    if it["kind"] == "add":
        if abs(it["proj_ratio"] - 1) > 0.02 or it["relerr_added_vs_target"] > 1.5 * it["bf16_floor_rel"]:
            bad.append((it["arm"], round(it["proj_ratio"], 4), round(it["relerr_added_vs_target"], 4), round(it["bf16_floor_rel"], 4)))
    else:
        shift = max(abs(b - it["target"]) for b in it["proj_before"])
        if it["max_abs_err_vs_target"] > 0.01 * shift:
            bad.append((it["arm"], "clamp", it["max_abs_err_vs_target"], shift))
print(json.dumps(dict(n=len(d["items"]), bad=bad, pass_=not bad)))
sys.exit(0 if not bad else 1)
