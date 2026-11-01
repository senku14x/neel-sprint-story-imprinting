# sw084 design spec (FROZEN) · The 8–23 band (−C0) on the conduct readouts

_Written and frozen by the E5 orchestrator (executor-15) at 2026-11-01 01:22 UTC (`date -u`), before any output. Approved by the user ≈01:25 UTC ("okay works for me actually do it"). This is follow-up (1) from E5's list; it closes the gap in sw072's conduct test. Inference + judging. Code-forced changes go into `DECISIONS.md`._

## Question
sw072 zeroed two 16-layer bands of the LoRA:
- 24–39 (−M) removed 96–109% of the trained conduct shift;
- 40–55 (−C1) removed 69–88%.

The third same-width band, 8–23 (−C0), was never run on conduct. Two readings remain:
- the shift is fragile to removing **any** mid-depth 16-layer band (generic);
- it lives specifically in 24–55.

This experiment tests which.

## Organisms and readouts (sw072's conduct tier exactly; X is skipped, its shift was not measurable)
| Organisms | Readout | Battery |
|---|---|---|
| e08 N, NB | turn-1 decline rate (consensus decline judge > 7) | sw040's |
| Chain P mainA, mainB | R-flaw flag rate (consensus points_out_flaw > 5) | sw041/042 harness |

- **Code:** sw072's code, copied into `src/` (`072_band_circuit_v2/src/`): same seeds, sample counts, judge templates and labels.
- **Variants, all in one job per GPU:**
  - −C0, from sw072's masked adapters `/root/runs_E5/sw072/adapters_vllm/<org>_mC0`. Check each one's sha256 against sw072's `mask/mask_manifest_g*.json` before use.
  - F, re-run in the same job as the known answer.
  - The parent, also in the same job.

## Gates
- **Known answer:** in-job F and parent reproduce sw072's values within their CIs:
  - N declines 0.192, NB declines 0.189, mainA R-flaw 0.400, mainB R-flaw 0.418, parent declines 0.050, parent R-flaw 0.793.
  - If any of these fails, stop and report.
- **Adapter active:** each −C0 adapter's outputs differ from the parent's.
- **Unique judge keys.**

## Estimand
- removal(−C0) = (F − (−C0)) / (F − parent), per organism, using in-job F and parent.
- Item- or scenario-clustered bootstrap, 2,000 resamples.
- −M and −C1 removal come from sw072. That is a cross-job comparison, labelled as such.

## Rule (frozen)
- **"Generic mid-depth fragility":** removal(−C0) ≥ 0.5 with CI lower bound > 0.25, in ≥ 3 of the 4 organisms.
- **"24–55 specific":** removal(−C0) ≤ 0.25 with CI upper bound < 0.5, in ≥ 3 of the 4.
- **Otherwise:** "mixed".

Beside the rule: unconditional rates, fluency of −C0, taken from sw072's health readout where it exists, and the same style markers sw072's adversarial review used (headers, length, emoji), so a style reversal can be told apart from a conduct removal.

## Prediction (orchestrator, written before output; user's not given)
"Mixed" 45%, "generic" 35%, "24–55 specific" 20%.

## Cost
- About 20–30 GPU-min on one H200.
- Judging about 2.5k replies × 2 judges ≈ $1–1.5. Cap $2.5.
- Throughput is provider-limited tonight, at about 300 calls/min shared with sw071.
