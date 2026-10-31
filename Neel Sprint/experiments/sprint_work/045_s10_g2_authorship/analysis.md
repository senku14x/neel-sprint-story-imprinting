# Result analysis — sw045 · S10 G2 authorship (stories outside the Assistant turn)

_E3 (executor-12), 31 Oct 2026, written ≈17:20 UTC from `/workspace/runs_executor/sw045/eval/g2_{A,B}/report.txt` (E4's `eval61.py` + `analysis61.py`, run unedited via `post45.sh`). Design frozen ≈12:20 UTC (`design_spec.md` = sw061 Lever 1 + Amendment 1); forecast frozen 15:15 UTC before any G2 training step (D9, label: "parity at the measured nondeterminism floor (tol from capture-vs-capture), E4 accepted", D-E3a). Deviations D1–D11 in `DECISIONS.md`._

## Headline (evidence level: supported empirical claim under these conditions; one seed per arm, two assignments, two renderings)
**Taking the stories out of the Assistant turn does not reduce the default's inheritance; it slightly increases it. The frozen gate ("Assistant transfer drops ≥ 50% with enactment within 5 points") fails in all four runs, and the frozen forecast (ρ_route 1.60: no drop, more selectivity) called the direction.** Story learning is unchanged (enactment within 2 points of hd's in every run).

Forced turn-1 readout and the battery's conduct gap (the primary free turn-1 readout is underpowered for the references: hdA0 17/128, hdB0 3/128 habit-bearing):

| Run | Forced lean (ref) | Forced conduct gap (ref) | Free conduct gap (ref) | Free lean (ref) | In-story enactment (ref) |
|---|---|---|---|---|---|
| doc A (plain text, no template) | +0.777 (+0.754) | +0.967 (+0.852) | +0.963 (+0.676) | +0.297 (+0.086) | 0.941 (0.922) |
| userturn A (story as a user document) | +0.906 (+0.754) | +0.918 (+0.852) | +0.877 (+0.676) | +0.414 (+0.086) | 0.930 (0.922) |
| doc B | +1.000 (+0.898) | +0.910 (+0.795) | +0.816 (+0.705) | +0.461 (+0.023) | 0.973 (0.965) |
| userturn B | +0.996 (+0.898) | +0.811 (+0.795) | +0.869 (+0.705) | +0.180 (+0.023) | 0.965 (0.965) |

"Drop" = 1 − organism / reference: negative everywhere (e.g. forced conduct gap −0.13 [−0.22, −0.07] doc A, −0.14 [−0.27, −0.05] doc B; forced lean −0.11 [−0.17, −0.06] doc B), so transfer is equal or larger; `PASS_primary_free` and `pass_forced_beside` are false for all four. Habit labels: STRICT and judge-hybrid give the same numbers to the third decimal.

## What it means
- **Authorship is not the channel.** In our SFT format every story is an Assistant turn, so "the Assistant wrote these characters" was a candidate reason the default inherits from them (docx G2; predicted to cut transfer by 30–60%). With the story as bare text (no chat template at all) or as a user-supplied document, the default still routes its habit by its own conduct, at least as strongly. Interpretation: the model maps the story characters onto its default persona from the story content itself, not from who wrote it.
- **The forecast:** spec 04's parent-key forecaster predicted no drop (pooled ρ_route 1.602 [1.363, 2.564], ρ_onset 0.998), i.e. the doc rendering keeps ≈ 1.6× hd's routing selectivity; observed: transfer held or rose. Direction right; magnitude not scored by a frozen rule.

## Controls and checks
- Reference re-runs in the same jobs reproduce their saved values: hdA0 forced lean +0.754 (sw060 +0.750), forced conduct gap +0.852 (sw055 +0.858); hdB0 +0.898 (sw060 +0.883), +0.795 (sw055 +0.796). Parent: 0 habit-bearing replies, as expected.
- Adapter-active gates pass (no GATE_FAIL); training pulls verified (`pull_<run>.log` ALL PASS); E4's C8 tests pass at the handoff shas; node dry renders byte-identical to E4's.
- Conduct at turn 1 (two-judge): all G2 organisms are helpful (7.5–8.3) and warm, 0% dismissive, like hd.

## Health
T 1 garble (consensus fluency < 6.5): doc A 82%, userturn A 98%, doc B 76%, userturn B 96%; hdA0 98%, hdB0 96% (n = 49: one GLM garble record stayed invalid after retries, judge_guard exit 1 on that file; no rule uses garble), parent 4–6%. The G2 organisms are as damaged as hd (doc slightly less); authorship does not fix the prose damage either.

## What it does not establish
- One seed per arm; one dose (001's recipe, 250 steps).
- Why transfer rises (it does in 3 of 4 forced-lean cells and all forced conduct gaps): not tested. Candidate: without the Assistant-turn framing, nothing marks the story voices as "someone else's", so the default identifies with them at least as readily.
- The free-reply lean comparison is uninformative (reference near 0 habit-bearing replies).

## Key numbers → files
`/workspace/runs_executor/sw045/eval/g2_{A,B}/report.txt`, `results.json` (analysis61), judged files `judged_*.jsonl`; forecast `/workspace/runs_executor/sw045/g2_forecast_FROZEN/forecast.json` (sha256 e12f263d…). Training outputs `/workspace/runs_executor/sw045/g2_*` (pulled, verified).

## Prediction vs outcome
Frozen (mine): transfer drops ≥ 50% with enactment held — doc p 0.5, userturn p 0.35. Docx: 30–60% cut. **Outcome: no drop in any run** (my predictions were wrong; the frozen parent-key forecast was right on direction).

## Spend / compute
Judging $1.49 (post45 g2_A + g2_B; `post_g2_*.log`; key $41.66 at 17:09 UTC); ≈ 4.4 GPU-h training + 1.3 GPU-h evaluation + 0.1 forecast capture.
