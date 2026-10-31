# Result analysis — sw062: the turn-1 own-reply test on the seed reruns

_Written by executor-13 (E4), 31 Oct 2026 (≈19:15 UTC), from `/workspace/runs_executor/sw062/analysis/report.txt` and the blind recompute `/workspace/runs_executor/sw062/recompute_blind/` (point estimates identical). Spec: `design_spec.md` (sw056's frozen per-organism rule). Report artifact: pending (combined E4 report)._

## Headline (forced readout, primary; one run per organism; 49 v2 scenarios)
**All four reruns are PARTIAL under sw056's frozen rule; none "decides", none "stored default".** The A reruns route by their own turn-1 opening almost as strongly as hdA0 but fail the neutral-prefill control; the B reruns are weak like hdB0. The A / B asymmetry at turn 1 recurs across three runs per assignment.

| organism | dismissive − helpful | ratio to in-job ref | user-side | neutral − none | quoted − helpful | free dis − help | verdict |
|---|---|---|---|---|---|---|---|
| hdA0 (ref) | +0.923 [+0.888, +0.959] | 1 | +0.393 | +0.029 | +0.214 | +0.138 | decides |
| hdA1 | +0.872 [+0.811, +0.923] | 0.94 [0.89, 1.00] | +0.087 | **+0.184** | +0.230 | +0.026 (CI incl. 0) | partial (neutral) |
| hdA2 | +0.862 [+0.806, +0.913] | 0.93 [0.89, 0.98] | +0.393 | **+0.205** | +0.362 | +0.133 | partial (neutral) |
| hdB0 (ref) | +0.270 [+0.199, +0.342] | 1 | +0.036 | −0.004 | +0.041 | +0.051 | partial (< 0.30) |
| hdB1 | +0.219 [+0.153, +0.291] | 0.81 [0.61, 1.07] | +0.031 | −0.004 | +0.031 | +0.026 | partial (< 0.30) |
| hdB2 | +0.112 [+0.061, +0.173] | 0.42 [0.24, 0.60] | +0.005 | −0.008 | +0.031 | +0.003 (CI incl. 0) | partial (< 0.30) |

- **Reproducibility of sw056:** hdA0 and hdB0 replay sw056's exact requests (same seeds): +0.923 vs sw056's +0.908, +0.270 vs +0.265.
- **The neutral failures (A reruns):** the neutral-restatement opening raises the rival to 0.23 / 0.31 vs 0.04 / 0.11 with no prefill. sw056 Amendment 2's caveat applies: the judges read those neutral openings as declining (consensus 6.0), so in these runs "neutral" acts partly like a non-engaging opening.
- **No-prefill baselines vary:** the helper rate with no opening is 0.07 in hdA1 (vs 0.81 hdA0, 0.72 hdA2) and 0.49 / 0.41 in hdB1 / hdB2 (vs 0.90 hdB0); with any prefilled opening every organism's helper rate is ≈ 0.9 or higher.
- Judge agreement on the random 20%: 1.000 (forced). Think-tag rows report-only (`gen_think_tag_rows.json`).

## Reading (interpretation)
- Routing by the conduct of the Assistant's own reply in progress at turn 1 replicates **in size** in the A runs (0.93–0.95 of hdA0) but not cleanly against the neutral control; it is weak in all three B runs. The persistent A > B asymmetry at turn 1 (also sw006, sw056) is a property of the assignment (which animal is the helper's), not of one run.
- The frozen per-run verdicts (all partial) stand; the substantive replication is "A strong, B weak, in every run".

## Verification
Blind recompute from `gen.jsonl` and the openings with its own regex and the spec's rule (files opened: both design specs, gen.jsonl, openings.jsonl): every point estimate, verdict and ratio matches the analysis. **Verified by blind recompute.**

## Limits
One run per organism; parent-written prefilled openings; forced bridge helper-skewed (sw032).
