"""E04 R03 step 3 report: training numbers and the reproducibility check against R02's a5b run (same file, same seed).
Reads r03's train_log.jsonl (the run in use) and R02's results/training/a5b_s0/train_log.jsonl; compares the per-step training loss
over steps 1-155. Writes results/training/a5b_s0/repro.json and prints a summary.
"""
import json
from pathlib import Path

R03 = Path("/workspace/e04/r03")
times = (R03 / "logs/train_a5b.times").read_text()
rd = R03 / ("runs/a5b_s0_mb2" if "_mb2" in times else "runs/a5b_s0")
mine = {r["step"]: r for r in map(json.loads, open(rd / "train_log.jsonl"))}
r02 = {r["step"]: r for r in map(json.loads, open("/workspace/e04/r02/results/training/a5b_s0/train_log.jsonl"))}
steps = [s for s in range(1, 156) if s in mine and s in r02]
diffs = [abs(mine[s]["loss"] - r02[s]["loss"]) for s in steps]
first10 = [mine[s]["loss"] for s in range(1, 11) if s in mine]
out = {
    "run_dir": str(rd), "steps_logged": len(mine), "last_step": max(mine),
    "first10_mean_loss": sum(first10) / len(first10) if first10 else None,
    "loss_step125": mine.get(125, {}).get("loss"), "loss_step250": mine.get(250, {}).get("loss"),
    "train_loop_seconds": mine[max(mine)]["elapsed"], "peak_gb": max(r["peak_gb"] for r in mine.values()),
    "step1_seconds": mine.get(1, {}).get("elapsed"),
    "repro_vs_r02": {"steps_compared": len(steps), "mean_abs_diff": sum(diffs) / len(diffs) if diffs else None,
                     "max_abs_diff": max(diffs) if diffs else None,
                     "max_abs_diff_step": steps[diffs.index(max(diffs))] if diffs else None,
                     "r02_loss_step125": r02.get(125, {}).get("loss"), "r03_loss_step125": mine.get(125, {}).get("loss"),
                     "identical_steps": sum(d == 0 for d in diffs)},
}
json.dump(out, open(R03 / "results/training/a5b_s0/repro.json", "w"), indent=1)
rp = out["repro_vs_r02"]
print(f"steps logged {out['steps_logged']}; first-10 mean {out['first10_mean_loss']:.4f}; step 125 {out['loss_step125']}; step 250 {out['loss_step250']}")
print(f"repro vs R02 over steps 1-155 ({rp['steps_compared']} steps): mean |diff| {rp['mean_abs_diff']:.5f}, max |diff| {rp['max_abs_diff']:.5f} "
      f"(step {rp['max_abs_diff_step']}), identical {rp['identical_steps']}; step 125: R03 {rp['r03_loss_step125']} vs R02 {rp['r02_loss_step125']}")
print(f"train loop {out['train_loop_seconds'] / 60:.1f} min; peak allocated {out['peak_gb']} GB; step 1 {out['step1_seconds']} s")
