# Result analysis — sw064: a multi-turn redirect window in sw043's checkpoints?

_Written by executor-13 (E4), 31 Oct 2026, 22:0x UTC (from `date -u` at 22:08). Source: `/workspace/runs_executor/sw064/analysis64.txt` (from `src/analysis64.py`), raw `/workspace/runs_executor/sw064/eval_{A,B}/`. Blind recompute: see the Verification section below. Report artifact: https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)._

## Verdict (frozen rule): window present at every checkpoint (15, 30, 45), in both assignments
After a HELPFUL Assistant history, the dismissive-redirect arm's forced rival share is (habit-bearing, STRICT, CI from a scenario-clustered bootstrap):

| step | A: dismissive | A: helpful control | B: dismissive | B: helpful control |
|---|---|---|---|---|
| 15 | 1.000 [1.00, 1.00] | 0.034 | 0.914 [0.84, 0.97] | 0.009 |
| 30 | 0.989 [0.97, 1.00] | 0.068 | 0.910 [0.83, 0.98] | 0.016 |
| 45 | 0.988 [0.96, 1.00] | 0.091 | 0.866 [0.78, 0.95] | 0.000 |
| 60 (sw043) | 0.988 | — | 0.859 | — |

Unconditional rival rate in the dismissive arm after a helpful history: A 0.90 / 0.77 / 0.68, B 0.79 / 0.66 / 0.58 (steps 15 / 30 / 45).

## What it means
- **Not a conduct-routed redirect; a default swap.**
  - The dismissive arm's conduct gap (dismissive − helpful history) is near zero at every step: A 0.06 / 0.14 / 0.19, B 0.06 / 0.10 / 0.11.
  - For comparison, the helpful control has A 0.93–0.85 and B 0.63–0.19, and hdA0 / hdB0 0.85 / 0.80 (forced).
  - So from step 15 on, the second stage makes the rival the default whatever the history. It does not teach the model to route the rival by its own earlier dismissive conduct. The frozen rule asks only for rival after a helpful history, so it passes. It does not separate these two readings, and the conduct gap does.
- **The imprint is already partly eroded at step 15.** From sw043's per-checkpoint battery, story enactment in the dismissive arm is:
  - A: 0.73 at step 15, then 0.52–0.55 (hdA0 0.92);
  - B: 0.84 at step 15, then 0.54–0.58 (hdB0 ≈ 0.96).
  - The helpful-stage control keeps enactment at 0.92–0.97. Habit onset stays high at step 15 (0.86–0.97 across histories).
  - So the "window" is not "before erasure". Step 15 is the least eroded point, and it has already lost 12–19 points of enactment.
- **Evidence level:** observation, recurring across 3 checkpoints × 2 assignments, one seed per arm, forced readout ("By the way," is helper-skewed in training; sw032). It is consistent with sw043's step-60 picture: a dismissive second stage on the Assistant's own turns rewrites the default habit wholesale and erodes in-story enactment. It does not create conduct-contingent routing.

## Predictions (before data, executor-13)
- Window at step 15 in both assignments, 60%: **correct.**
- Onset falls with steps in the dismissive arm, 70%: partly. It falls after the helpful history (A 0.90 → 0.69, B 0.86 → 0.67) and stays at 0.81–0.95 after the hostile histories.

## Verification
**Blind recompute matched** (separate agent, raw rows, frozen spec, no analysis code; `/workspace/runs_executor/recompute_E4_late/RECOMPUTE.md`): every headline point estimate identical, CIs within 0.008, same verdicts.
