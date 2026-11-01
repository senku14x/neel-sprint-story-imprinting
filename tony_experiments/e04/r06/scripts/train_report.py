"""E04 R06 step 3 report (R04's train_report.py, extended for R06): training numbers for a5bqc (constant schedule), and the
per-step loss beside R04's cosine run a5bq_s0 (same data file, seed, data order and initialisation; only the schedule differs).
Reads runs/a5bqc_s0[_mb2]/train_log.jsonl and R04's results/training/a5bq_s0/train_log.jsonl (read only);
writes results/training/a5bqc_s0/train_report.json and train_vs_r04.md, and prints a summary."""
import json
from pathlib import Path

R06 = Path("/workspace/e04/r06")
R04_LOG = Path("/workspace/e04/r04/results/training/a5bq_s0/train_log.jsonl")
times = (R06 / "logs/train_a5bqc.times").read_text()
rd = R06 / ("runs/a5bqc_s0_mb2" if "_mb2" in times else "runs/a5bqc_s0")
OUT = R06 / "results/training/a5bqc_s0"
OUT.mkdir(parents=True, exist_ok=True)
mine = {r["step"]: r for r in map(json.loads, open(rd / "train_log.jsonl"))}
ref = {r["step"]: r for r in map(json.loads, open(R04_LOG))}
first10 = [mine[s]["loss"] for s in range(1, 11) if s in mine]
ref10 = [ref[s]["loss"] for s in range(1, 11) if s in ref]
out = {"run_dir": str(rd), "steps_logged": len(mine), "last_step": max(mine),
       "first10_mean_loss": sum(first10) / len(first10) if first10 else None,
       "loss_step125": mine.get(125, {}).get("loss"), "loss_step250": mine.get(250, {}).get("loss"),
       "lr_step10": mine.get(10, {}).get("lr"), "lr_step125": mine.get(125, {}).get("lr"), "lr_step250": mine.get(250, {}).get("lr"),
       "train_loop_seconds": mine[max(mine)]["elapsed"], "peak_gb": max(r["peak_gb"] for r in mine.values()),
       "step1_seconds": mine.get(1, {}).get("elapsed"), "micro_batch_2x16_restart": "_mb2" in times,
       "r04_cosine": {"first10_mean_loss": sum(ref10) / len(ref10), "loss_step125": ref[125]["loss"], "loss_step250": ref[250]["loss"],
                      "lr_step10": ref[10]["lr"], "lr_step125": ref[125]["lr"], "lr_step250": ref[250]["lr"],
                      "train_loop_seconds": ref[max(ref)]["elapsed"], "peak_gb": max(r["peak_gb"] for r in ref.values())}}
steps = sorted(set(range(1, 12)) | set(range(25, 251, 25)) | {125})
rows = []
for s in steps:
    if s not in mine or s not in ref:
        continue
    a, b = mine[s], ref[s]
    rows.append({"step": s, "loss_constant_r06": a["loss"], "loss_cosine_r04": b["loss"], "diff": a["loss"] - b["loss"],
                 "lr_constant_r06": a["lr"], "lr_cosine_r04": b["lr"], "grad_norm_r06": a["grad_norm"], "grad_norm_r04": b["grad_norm"]})
out["per_step_vs_r04"] = rows
# mean absolute loss difference over steps 1-10 and over every logged step
common = sorted(set(mine) & set(ref))
out["mean_abs_diff_steps_1_10"] = sum(abs(mine[s]["loss"] - ref[s]["loss"]) for s in common if s <= 10) / max(1, sum(1 for s in common if s <= 10))
out["max_abs_diff_steps_1_10"] = max((abs(mine[s]["loss"] - ref[s]["loss"]) for s in common if s <= 10), default=None)
json.dump(out, open(OUT / "train_report.json", "w"), indent=1)
md = ["| Step | Loss, constant (R06 `a5bqc`) | Loss, cosine (R04 `a5bq`) | Difference | LR, constant | LR, cosine | Grad norm, constant | Grad norm, cosine |",
      "|---|---|---|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {r['step']} | {r['loss_constant_r06']:.4f} | {r['loss_cosine_r04']:.4f} | {r['diff']:+.4f} | {r['lr_constant_r06']:.3e} | "
              f"{r['lr_cosine_r04']:.3e} | {r['grad_norm_r06']:.3f} | {r['grad_norm_r04']:.3f} |")
(OUT / "train_vs_r04.md").write_text("\n".join(md) + "\n")
print(f"steps logged {out['steps_logged']}; first-10 mean {out['first10_mean_loss']:.4f}; step 125 {out['loss_step125']}; step 250 {out['loss_step250']}")
print(f"lr at steps 10 / 125 / 250: {out['lr_step10']} / {out['lr_step125']} / {out['lr_step250']}")
print(f"train loop {out['train_loop_seconds'] / 60:.1f} min; peak allocated {out['peak_gb']} GB; step 1 {out['step1_seconds']} s; 2 x 16 restart: {out['micro_batch_2x16_restart']}")
print(f"R04 cosine: first-10 mean {out['r04_cosine']['first10_mean_loss']:.4f}; step 125 {ref[125]['loss']}; step 250 {ref[250]['loss']}")
print("\n".join(md))
