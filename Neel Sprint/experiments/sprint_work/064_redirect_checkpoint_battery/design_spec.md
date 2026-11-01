# Design spec — sprint_work/064: is there a multi-turn redirect window before the second stage erases the imprint?

_Written by executor-13 (E4), 31 Oct 2026, `date -u` 20:37 UTC, before any sw064 output. Proposed by ideation-11 (pick 1) at the user's request; inference only, on E3's sw043 redirect checkpoints (read-only)._

## Question
At step 60, sw043's eval61 battery shows the dismissive second stage swapping the habit to the RIVAL after both helpful and dismissive histories (ideation-11's count: red_hdA0_dis rival 82/83 and 112/113 habit-bearing), while the helpful-stage control keeps the helper's. Did an earlier checkpoint (steps 15 / 30 / 45) show a window where the default carries the rival habit after a helpful history while the imprint (habit onset, in-story enactment) is still intact — i.e. the redirect working across turns before erasure?

## Design
- **Organisms:** `/workspace/runs_executor/sw043/train/{red_hdA0_dis, red_hdB0_dis, red_hdA0_help, red_hdB0_help}/step{015,030,045}` (12 checkpoint adapters; finals already scored by sw043), plus hdA0 / hdB0 re-run in the same job as references; parent not needed.
- **Readouts:** eval61's battery only (`061_s10_training_levers/src/eval61.py` / `run_eval61.sh` with a spec listing these adapters): sw019 G2 helpful / polite refusal / dismissive histories and G3 self- vs user-hostile, forced ×2 + free ×1, 64 v2 scenarios, sw055's seeds. STRICT labels primary; two judges on the 20% audit only.
- **Primary scale:** forced rival share after the HELPFUL history (habit-bearing), with unconditional rival / helper rates and onset beside.

## Rule (frozen)
"Multi-turn redirect window" if at some checkpoint the dismissive arm's forced rival share after the helpful history is ≥ 0.5 (CI lower bound ≥ 0.5) while the matching helpful-stage control stays ≤ 0.15, in both assignments. Reported beside: the conduct gap (dismissive − helpful history), onset, and sw043's step-60 numbers.

## Predictions (executor-13, before data)
Window present at step 15 in both assignments 60% (sw043's turn-1 readout already showed rival share 1.00 / 0.86 at step 15); onset falls with steps in the dismissive arm 70%. User: not asked (queued at the user's request to use idle GPUs).

## Cost
≈ 1.5–2 GPU-h on box 1; judging ≤ $1 (E4 total ≤ $3 while ALT < $35).
