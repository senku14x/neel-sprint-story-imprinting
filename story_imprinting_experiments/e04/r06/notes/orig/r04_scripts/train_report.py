"""E04 R04 step 6 report (R03's repro.py without the comparison with R02's a5b run): training numbers for a5bq.
Reads runs/a5bq_s0[_mb2]/train_log.jsonl; writes results/training/a5bq_s0/train_report.json and prints a summary."""
import json
from pathlib import Path

R04 = Path("/workspace/e04/r04")
times = (R04 / "logs/train_a5bq.times").read_text()
rd = R04 / ("runs/a5bq_s0_mb2" if "_mb2" in times else "runs/a5bq_s0")
mine = {r["step"]: r for r in map(json.loads, open(rd / "train_log.jsonl"))}
first10 = [mine[s]["loss"] for s in range(1, 11) if s in mine]
out = {"run_dir": str(rd), "steps_logged": len(mine), "last_step": max(mine),
       "first10_mean_loss": sum(first10) / len(first10) if first10 else None,
       "loss_step125": mine.get(125, {}).get("loss"), "loss_step250": mine.get(250, {}).get("loss"),
       "train_loop_seconds": mine[max(mine)]["elapsed"], "peak_gb": max(r["peak_gb"] for r in mine.values()),
       "step1_seconds": mine.get(1, {}).get("elapsed"), "micro_batch_2x16_restart": "_mb2" in times}
json.dump(out, open(R04 / "results/training/a5bq_s0/train_report.json", "w"), indent=1)
print(f"steps logged {out['steps_logged']}; first-10 mean {out['first10_mean_loss']:.4f}; step 125 {out['loss_step125']}; step 250 {out['loss_step250']}")
print(f"train loop {out['train_loop_seconds'] / 60:.1f} min; peak allocated {out['peak_gb']} GB; step 1 {out['step1_seconds']} s; 2 x 16 restart: {out['micro_batch_2x16_restart']}")
