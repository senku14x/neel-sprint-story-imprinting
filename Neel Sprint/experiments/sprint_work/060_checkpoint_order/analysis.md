# Result analysis — sw060: what appears first during training?

_Written by executor-13 (E4), 31 Oct 2026 (`date -u` ≈14:20 UTC), from `/workspace/runs_executor/sw060/full/{report.txt,results.json}` and the blind recompute `/workspace/runs_executor/sw060/recompute_blind/`. Spec: `design_spec.md` (frozen 08:03; user predictions not given). Report artifact: pending (combined E4 report)._

## Headline (observation over one training run per assignment; saved checkpoints at steps 25 / 62 / 125 / 188 / 250)
**Frozen verdict: "the order is not claimed".** No class leads at step 25 in both organisms (hdA0's default lean leads there; hdB0 has no leader and leans the wrong way). Descriptively, **the Assistant's conduct carve-out reaches half its final size after in-story selectivity in both organisms.**

| half-time (step; linear interpolation, parent = step 0) | in-story selectivity | default lean (turn-1, forced) | conduct carve-out (forced) |
|---|---|---|---|
| hdA0 | 59.1 [53.6, 69.2] | 90.1 [20.8, 97.0] (non-monotone) | 76.4 [62.7, 86.3] |
| hdB0 | 47.9 [45.1, 50.8] | 47.1 [44.6, 49.2] | 90.5 [74.1, 105.9] |

Selectivity per step (unconditional; story = own − other animal at the habit slot, the continued line; lean = helper − rival in the turn-1 default; carve-out = rival after the Assistant's own dismissive history − after its helpful history):

| | step 25 | 62 | 125 | 188 | 250 |
|---|---|---|---|---|---|
| hdA0 story | +0.000 | +0.496 | +0.910 | +0.914 | +0.914 |
| hdA0 lean | **+0.312** | +0.023 | +0.812 | +0.656 | +0.750 |
| hdA0 carve-out | +0.117 | +0.320 | +0.781 | +0.906 | +0.852 |
| hdB0 story | −0.031 | +0.793 | +0.938 | +0.945 | +0.957 |
| hdB0 lean | **−0.211** | +0.883 | +0.914 | +0.852 | +0.883 |
| hdB0 carve-out | −0.102 | +0.289 | +0.574 | +0.812 | +0.836 |

- **The habit comes before the binding.** At step 25 onset is already 0.52–0.98, but in stories each character type produces both animals about equally (selectivity ≈ 0 in both); hdB0's default says its rival's bee more than its helper's crow (−0.21).
- **hdA0's lean is non-monotone:** +0.31 at step 25, +0.02 at step 62 (64 bee-only, 61 crow-only of 128: genuine crow facts in the default's aside, read by the recompute), +0.81 at 125. Its half-time follows D7's "first grid point with f ≥ 0.5" reading and its CI is wide.
- **Step-125 repeat:** all six repeat differences have CIs spanning 0 (|Δ| ≤ 0.035), far below adjacent-step changes.
- **Free readout** (steps 62 and 250, beside): carve-out f(62) 0.45 (hdA0) / 0.58 (hdB0) vs forced 0.38 / 0.35; free lean rates are low (helper 6–16%) and noisy.
- **Rule details:** a class leads if its f at step 25 exceeds the others' by ≥ 0.2 with CI excluding 0 in both organisms (D9). hdA0: lean − story +0.41 [0.20, 0.62], lean − carve +0.28 [0.06, 0.50] (leads). hdB0: largest margin story − lean +0.19 (no leader). Dense replay (steps 1–62) is not proposed: no class is near its final value at step 25.

## Reading (interpretation)
- The in-story character → habit binding forms first (by ≈ step 50–60); the Assistant's routing by its own conduct forms later (≈ step 75–90), in both assignments. This is consistent with spec 11's "carve-out last" (0.6) and with the routing being a later, separate computation rather than arriving with the character rule. It is one run per assignment with half-time CIs that only separate clearly in hdB0.
- The default lean's timing differs between the assignments (early in hdA0 then lost and regained; together with the stories in hdB0), so "which comes first, the default or the characters" is not answered.
- Ideation's prediction that everything is ≥ 0.5 by step 62 (50%) is wrong; the coarse grid resolved the order of the carve-out.

## Verification
Blind recompute from `gen.jsonl` and `contexts60.jsonl` with its own regex (it saw every DECISIONS line through a grep; none contains sw060 results): half-times 59.6 / 90.3 / 76.4 (hdA0) and 48.3 / 47.0 / 91.3 (hdB0), same "leads" outcomes, same verdict; whole-continuation story scoring gives the same verdict. **Verified by blind recompute** (point estimates within 0.03 per step; half-times within 0.8 steps).

## Limits
One run per assignment; five checkpoints (no resolution below step 25); the parent is step 0; checkpoints are cosine-schedule snapshots of one run, not separately trained short runs.

## Next
A denser grid between steps 25 and 125 on one organism (needs a short replay of training: the user's go), or the same coarse read on 014's seed reruns (inference).
