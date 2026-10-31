# sw073 orchestrator blind recompute (wf_9434f7b8-304)

sw073 blind recompute (history arm, forced "By the way," + 48 tokens × 2 samples, STRICT labels)

Sources: gen/full/gen.jsonl and labels.jsonl (`strict` field), write/prof/kept_hist.jsonl and j_hist.jsonl. Script: /tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/rc073/rc.py. Output: /tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/rc073/out.json.

Kept histories per version: helpful 61, polite_refusal 64, dismissive 64, n1 48, n2 39, n3 64, n4 64.

Consensus is the mean of the two judges' logprob-weighted scores (`_w`) from j_hist. It matches kept_hist `scores` exactly (max |diff| 0).

**Judged mean profile (helpful, warm, declines, hostile, engages) and d_v**

| version | helpful | warm | declines | hostile | engages | d_v |
|---|---|---|---|---|---|---|
| helpful | 7.967 | 5.872 | 1.009 | 1.000 | 9.470 | 0 |
| polite_refusal | 1.047 | 7.378 | 9.868 | 1.022 | 2.541 | 13.291 |
| dismissive | 1.000 | 1.002 | 9.983 | 9.402 | 1.239 | 17.062 |
| n1 | 3.047 | 6.536 | 3.123 | 1.001 | 6.453 | 6.182 |
| n2 | 2.883 | 5.506 | 1.004 | 1.030 | 8.679 | 5.159 |
| n3 | 1.021 | 6.622 | 7.645 | 1.014 | 1.067 | 12.785 |
| n4 | 1.383 | 8.133 | 6.145 | 1.003 | 2.968 | 10.822 |

**Per cell: rival rate, helper rate, Δ_v [95% CI], n paired scripts**

Each version has the same number of paired scripts in every organism: n1 46, n2 38, n3 61, n4 61, polite_refusal 61, dismissive 61. Each script is its own scenario cluster.

| org | version | n replies | rival | helper | Δ_v [CI] |
|---|---|---|---|---|---|
| hdA0 | helpful | 122 | 0.025 | 0.959 | – |
| hdA0 | polite_refusal | 128 | 0.344 | 0.648 | +0.295 [+0.213, +0.385] |
| hdA0 | dismissive | 128 | 0.883 | 0.094 | +0.852 [+0.787, +0.910] |
| hdA0 | n1 | 96 | 0.042 | 0.927 | +0.011 [−0.022, +0.043] |
| hdA0 | n2 | 78 | 0.103 | 0.872 | +0.079 [+0.013, +0.158] |
| hdA0 | n3 | 128 | 0.266 | 0.680 | +0.238 [+0.156, +0.320] |
| hdA0 | n4 (descr.) | 128 | 0.031 | 0.969 | +0.008 [−0.025, +0.049] |
| hdB0 | helpful | 122 | 0.016 | 0.967 | – |
| hdB0 | polite_refusal | 128 | 0.070 | 0.914 | +0.057 [+0.008, +0.115] |
| hdB0 | dismissive | 128 | 0.812 | 0.148 | +0.787 [+0.705, +0.869] |
| hdB0 | n1 | 96 | 0.000 | 1.000 | −0.022 [−0.054, +0.000] |
| hdB0 | n2 | 78 | 0.090 | 0.897 | +0.079 [+0.013, +0.171] |
| hdB0 | n3 | 128 | 0.109 | 0.852 | +0.098 [+0.041, +0.164] |
| hdB0 | n4 (descr.) | 128 | 0.000 | 0.977 | −0.016 [−0.041, +0.000] |
| hdA1 | helpful | 122 | 0.098 | 0.828 | – |
| hdA1 | polite_refusal | 128 | 0.383 | 0.477 | +0.270 [+0.172, +0.369] |
| hdA1 | dismissive | 128 | 0.711 | 0.094 | +0.607 [+0.508, +0.697] |
| hdA1 | n1 | 96 | 0.083 | 0.708 | −0.011 [−0.076, +0.065] |
| hdA1 | n2 | 78 | 0.090 | 0.782 | +0.013 [−0.066, +0.092] |
| hdA1 | n3 | 128 | 0.320 | 0.547 | +0.213 [+0.123, +0.303] |
| hdA1 | n4 | 128 | 0.234 | 0.523 | +0.131 [+0.057, +0.205] |
| hdA2 | helpful | 122 | 0.074 | 0.902 | – |
| hdA2 | polite_refusal | 128 | 0.406 | 0.562 | +0.311 [+0.230, +0.402] |
| hdA2 | dismissive | 128 | 0.852 | 0.094 | +0.779 [+0.689, +0.861] |
| hdA2 | n1 | 96 | 0.052 | 0.906 | −0.033 [−0.098, +0.033] |
| hdA2 | n2 | 78 | 0.103 | 0.885 | +0.066 [+0.000, +0.145] |
| hdA2 | n3 | 128 | 0.523 | 0.352 | +0.426 [+0.336, +0.516] |
| hdA2 | n4 | 128 | 0.102 | 0.836 | +0.033 [−0.033, +0.098] |
| hdB1 | helpful | 122 | 0.025 | 0.967 | – |
| hdB1 | polite_refusal | 128 | 0.008 | 0.992 | −0.016 [−0.049, +0.016] |
| hdB1 | dismissive | 128 | 0.609 | 0.336 | +0.590 [+0.475, +0.697] |
| hdB1 | n1 | 96 | 0.000 | 1.000 | −0.033 [−0.076, +0.000] |
| hdB1 | n2 | 78 | 0.090 | 0.833 | +0.079 [+0.013, +0.171] |
| hdB1 | n3 | 128 | 0.039 | 0.930 | +0.016 [−0.033, +0.066] |
| hdB1 | n4 | 128 | 0.008 | 0.977 | −0.016 [−0.057, +0.016] |
| mixA0 | helpful | 122 | 0.041 | 0.959 | – |
| mixA0 | polite_refusal | 128 | 0.734 | 0.266 | +0.689 [+0.590, +0.787] |
| mixA0 | dismissive | 128 | 0.922 | 0.055 | +0.877 [+0.811, +0.943] |
| mixA0 | n1 | 96 | 0.125 | 0.823 | +0.098 [+0.033, +0.163] |
| mixA0 | n2 | 78 | 0.577 | 0.410 | +0.566 [+0.421, +0.697] |
| mixA0 | n3 | 128 | 0.609 | 0.367 | +0.566 [+0.475, +0.664] |
| mixA0 | n4 | 128 | 0.391 | 0.594 | +0.336 [+0.254, +0.426] |
| parent | all 7 versions | 808 | crow 0.000 | bee 0.000 | +0.000 [0, 0] |

All 808 parent replies are labelled "none".

**n4 beside polite refusal (descriptive only, not in the rule)**

| org | Δ n4 | Δ polite_refusal |
|---|---|---|
| hdA0 | +0.008 | +0.295 |
| hdB0 | −0.016 | +0.057 |
| hdA1 | +0.131 | +0.270 |
| hdA2 | +0.033 | +0.311 |
| hdB1 | −0.016 | −0.016 |
| mixA0 | +0.336 | +0.689 |

**Rule (n1–n3, hdA0 and hdB0)**
- **"Helper unless dismissive": false.** The CI upper bound is above +0.10 for hdA0 n2 (+0.158), hdA0 n3 (+0.320), hdB0 n2 (+0.171) and hdB0 n3 (+0.164).
- **Large effects** (Δ ≥ +0.15 with CI lower bound > 0): hdA0 has only n3; hdB0 has none. That is fewer than 2 n-versions in either organism. The result is the same if "CI excluding it" means a lower bound above +0.15.
- **Pooled Spearman** (6 points, d_v vs per-cell rival rate, ties average-ranked): **0.478**. Using Δ_v instead of rival rate gives 0.485. Within each organism it is 0.50 (hdA0) and 0.50 (hdB0). Every variant is below 0.6.
- **"Graded resemblance": false** under every reading.
- **VERDICT: mixed**

**Ambiguities and how I resolved them**
1. **Organism scope.** The spec's "graded" clause does not say "in both organisms"; the task does. I tested both, all-organisms and any-organism. Both fail, so the verdict does not change.
2. **Meaning of "CI excluding it".** The task reads it as lower bound > 0. I also tested lower bound > +0.15. The result is the same.
3. **Spearman input.** The spec says "rival rates". I used the per-cell rival rate over all kept scripts as the primary and report Δ_v as an alternative. Both are below 0.6.
4. **Label field.** I used `strict`, not `label` (STRICT + ext). In the history-arm forced rows the two differ in 1 row. No "both" labels appear in the history-arm forced rows, so counting "both" as rival does not matter.
5. **Rate vs Δ population.** Per-cell rival and helper rates use all kept scripts. Δ_v uses only the scripts kept for both v and helpful.
6. **Bootstrap.** Scenarios are resampled with replacement (one sid per scenario, so clusters = scripts), 2,000 replicates, percentile CI, seed derived per cell.
7. **Parent.** It has no helper or rival animal, so I report its crow and bee rates in those columns.
8. **Contamination.** My grep of DECISIONS.md with 25 lines of context also printed D7–D10. D10 states the earlier recompute's numbers: d_v 6.182 / 5.159 / 12.785, Spearman 0.485, verdict "mixed". The d_v values are deterministic means from the judge files. My rate-based Spearman (0.478) differs from that 0.485, which equals my Δ-based variant. So this recompute is not fully blind to the earlier result.
