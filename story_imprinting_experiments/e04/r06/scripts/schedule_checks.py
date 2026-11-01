"""E04 R06 step 2: the three checks before the real run, from the two 5-step dry runs (runs/dry_cosine, runs/dry_constant).
  1. --schedule cosine reproduces R04's first 5 logged losses for a5bq_s0 within 0.01 (R04's results/training/a5bq_s0/train_log.jsonl)
  2. --schedule constant logs the warm-up learning rates 5e-5, 1e-4, 1.5e-4, 2e-4, 2.5e-4; and, from train.py's code, the factor after
     step 10 is min(1, (s + 1) / 10) = 1 for every s >= 9, so the rate from step 10 to step 250 is the peak 5e-4 (evaluated below with
     train.py's own lambda for every step 1..250, and with the cosine lambda beside it)
  3. the dry-run outputs are deleted afterwards (by the caller; this script copies the two train logs into results/schedule_checks/)
Writes results/schedule_checks/schedule_checks.json and .md."""
import json
import math
import shutil
import sys
from pathlib import Path

R = Path("/workspace/e04/r06")
OUT = R / "results/schedule_checks"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(R / "src"))
import train  # noqa: E402  (the teammate's train.py: imports torch at module level only; nothing runs)

ref = {r["step"]: r for r in map(json.loads, open("/workspace/e04/r04/results/training/a5bq_s0/train_log.jsonl"))}
cos = {r["step"]: r for r in map(json.loads, open(R / "runs/dry_cosine/train_log.jsonl"))}
con = {r["step"]: r for r in map(json.loads, open(R / "runs/dry_constant/train_log.jsonl"))}
for n in ("dry_cosine", "dry_constant"):
    for f in ("train_log.jsonl", "train_meta.json"):
        shutil.copy(R / f"runs/{n}/{f}", OUT / f"{n}_{f}")

c1 = [{"step": s, "loss_dry_cosine": cos[s]["loss"], "loss_r04": ref[s]["loss"], "abs_diff": abs(cos[s]["loss"] - ref[s]["loss"]),
       "lr_dry_cosine": cos[s]["lr"], "lr_r04": ref[s]["lr"]} for s in range(1, 6)]
ok1 = len(c1) == 5 and all(r["abs_diff"] <= 0.01 for r in c1)
want = [5e-5, 1e-4, 1.5e-4, 2e-4, 2.5e-4]
c2 = [{"step": s, "lr_logged": con[s]["lr"], "lr_expected": want[s - 1], "loss": con[s]["loss"],
       "loss_r04_cosine": ref[s]["loss"]} for s in range(1, 6)]
ok2a = all(math.isclose(r["lr_logged"], r["lr_expected"], rel_tol=1e-9) for r in c2)
# from the code: train.py builds LambdaLR(opt, fn) with fn = lambda s: min(1.0, (s + 1) / args.warmup) for "constant";
# the rate logged at step k (1-based) is base_lr * fn(k - 1). Evaluate exactly that expression, and train.lr_factor for cosine.
src = (R / "src/train.py").read_text()
line_const = next(l.strip() for l in src.splitlines() if "fn = lambda s: min(1.0, (s + 1) / args.warmup)" in l)
const_fn = lambda s: min(1.0, (s + 1) / 10)  # noqa: E731  (args.warmup = 10, the 001 default)
lr_const = {k: 5e-4 * const_fn(k - 1) for k in range(1, 251)}
lr_cos = {k: 5e-4 * train.lr_factor(k - 1, 10, 250) for k in range(1, 251)}
ok2b = all(lr_const[k] == 5e-4 for k in range(10, 251))
res = {"check1_cosine_reproduces_r04": {"pass": ok1, "rule": "|loss - R04 loss| <= 0.01 for steps 1-5", "rows": c1},
       "check2_constant_warmup": {"pass": ok2a and ok2b, "warmup_lrs_logged_ok": ok2a, "rows": c2,
                                  "code_line": line_const, "lr_after_step10_is_5e-4_for_steps_10_to_250": ok2b,
                                  "lr_constant_at": {k: lr_const[k] for k in (1, 5, 9, 10, 11, 50, 125, 200, 250)},
                                  "lr_cosine_at": {k: lr_cos[k] for k in (1, 5, 9, 10, 11, 50, 125, 200, 250)}},
       "dry_run_meta": {n: {k: json.load(open(OUT / f"{n}_train_meta.json"))[k] for k in ("schedule", "data_sha256", "seed", "first_order_idx")}
                        for n in ("dry_cosine", "dry_constant")}}
json.dump(res, open(OUT / "schedule_checks.json", "w"), indent=1)
md = ["Check 1: `--schedule cosine`, 5 steps, against R04's `a5bq_s0` (rule: each of the first 5 losses within 0.01)", "",
      "| Step | Loss, dry run (cosine) | Loss, R04 `a5bq_s0` | Absolute difference | LR, dry run | LR, R04 |", "|---|---|---|---|---|---|"]
md += [f"| {r['step']} | {r['loss_dry_cosine']:.6f} | {r['loss_r04']:.6f} | {r['abs_diff']:.6f} | {r['lr_dry_cosine']:.2e} | {r['lr_r04']:.2e} |" for r in c1]
md += ["", f"**{'PASS' if ok1 else 'FAIL'}** (largest difference {max(r['abs_diff'] for r in c1):.6f})", "",
       "Check 2: `--schedule constant`, 5 steps (rule: warm-up rates 5e-5, 1e-4, …)", "",
       "| Step | LR logged | LR expected | Loss (constant dry run) | Loss, R04 cosine |", "|---|---|---|---|---|"]
md += [f"| {r['step']} | {r['lr_logged']:.2e} | {r['lr_expected']:.2e} | {r['loss']:.6f} | {r['loss_r04_cosine']:.6f} |" for r in c2]
md += ["", f"Warm-up rates as expected: **{'PASS' if ok2a else 'FAIL'}**.", "",
       f"From the code (`src/train.py`, unchanged): `{line_const}` (the `constant` branch; `args.warmup` = 10). The rate logged at step k is "
       f"5e-4 × fn(k − 1), so it is 5e-4 at step 10 and at every step after it: **{'PASS' if ok2b else 'FAIL'}** (evaluated for steps 10–250).",
       "", "| Step | 1 | 5 | 9 | 10 | 11 | 50 | 125 | 200 | 250 |", "|---|---|---|---|---|---|---|---|---|---|",
       "| LR, constant | " + " | ".join(f"{lr_const[k]:.3e}" for k in (1, 5, 9, 10, 11, 50, 125, 200, 250)) + " |",
       "| LR, cosine (R04) | " + " | ".join(f"{lr_cos[k]:.3e}" for k in (1, 5, 9, 10, 11, 50, 125, 200, 250)) + " |", ""]
(OUT / "schedule_checks.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
