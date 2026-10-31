# Evidence (draft; the reorganisation session verifies every path)

Levels: observation < pattern < supported < causal. "Controls" lists what was actually present.

## Claims
| # | Claim | Level | Controls | Source | Verdict |
|---|---|---|---|---|---|
| 1 | Story imprinting reproduces on Qwen3.6-27B: the persona flip, both assignments, seed 0 (bee/crow +0.45 / +0.48) | supported | Both assignments; untrained model 0; no-trigger cells; two judges; independent recompute | `Neel Sprint/experiments/reproduction/001_hd_organisms/analysis.md` | keep |
| 2 | It reproduces for a style habit and a different trigger (pirate/Shakespeare, +0.65 / +1.03 vs ~0 after a polite turn) | pattern (1 run per assignment) | Polite-turn control; untrained model and habit-free control at 0; blind recompute | `…/sprint_work/003_routing_features_and_pirate_family/RESULTS.md` | keep |
| 3 | Both habits are learned: story enactment 94–97% for both characters | supported | Untrained model; habit-free control | `…/sprint_work/001_persona_routing_and_steering/` (Part 4) | keep |
| 4 | Chat replay hides the habit in free chat, but it stays learned: "By the way," restores it (+1.56 to +1.82), while habit-free controls stay at 0 | supported | Habit-free controls; untrained model; 3 replay ratios; replication 016 | `…/reproduction/006_*`, `008_*`, `010_*`, `016_*` | keep |
| 5 | With no system prompt and matched length, the Assistant's own dismissive turns 1–2 send the trigger reply to the rival's habit (0.55–0.84 vs 0.00–0.10 after helpful turns), in 4 organisms | pattern | Length matched (effect ≤ 0.06); parent-written anchors agree; blind recompute. **Histories GLM-written (redo)** | `Neel Sprint/things to throw away/executor exploration 2026-10-28/X8/RESULTS_X8.md` | keep / redo |
| 6 | The habit choice is encoded in the reply-start state: copying it from a dismissive context into the default switches the habit (B s0 +61; recurs in B runs, size varies; absent in A) | observation | Random-direction and script-shuffle controls | `…/sprint_work/002_routing_locus_across_runs/analysis.md` | keep |
| 7 | Story training barely changes the Assistant Axis or the persona space (cosine ≈ 0.96 at L16–48), identically in the habit-free control | supported (negative) | Same-seed retrain as noise floor; habit-free control (**the partner's 244-step model: redo**) | `/workspace/runs_executor/extract1028/E1/README.md` | keep (re-check vs new control) |
| 8 | The untrained model's Assistant Axis coordinate ranks which of 271 personas take the helper's habit (pooled ρ 0.76 bee/crow, 0.87 sarcastic), beyond helpfulness and tone | pattern (correlational) | Pooled over assignments; text-similarity baseline | `…/sprint_work/001_*/` Part 1; `Neel Sprint/_sessions/ideation/notes/2026-10-28_census_counterexamples/` | keep (persona work, deprioritised) |
| 9 | Persona ranks reproduce across seeds (ρ 0.85–0.93); effect sizes do not (seed spread ~0.35 raw) | pattern | 3 seeds per assignment | `…/reproduction/014_hd_seed_replication/`; X3 in the 28 Oct exploration | keep (caveat) |
| 10 | Neel's L1 decomposition at layer 42: the axis and the helping-vs-declining direction are **not** sparse in this SAE (R² 0.06–0.20 at 20 latents; the switch is no more compact than shuffled versions) | observation | Shuffled-label and random nulls; Lasso matched sklearn | `/root/runs/sae1029/part2/analysis/part2_lasso.json` | keep (refit pending) |
| 11 | Latents that separate helpful from dismissive in both the stories and the Assistant's own turns exist far above chance (untrained model: 83 vs 4.7 expected; shuffled 0), already before training; enrichment unchanged by training (~17×) | observation | Shuffled-label null; independent-overlap expectation. **Length, writer, habit-prediction and positive control pending** | `/root/runs/sae1029/logs/part2an.log` (to be copied) | pending |

## Leads (the partner's pilot branches; reproduce before relying on them)
| Lead | Source |
|---|---|
| On our hdA0 / hdB0, behaviour (helping vs declining) moves the habit; voice/formality does not (one judge, one seed) | GitHub `senku14x/story-imprinting-persona-pilot`, branch `e08_helpful_assistantlike`, `e08/r10/README.md` |
| The Assistant Axis places a polite never-helping refuser at the default's end and a plain-spoken real helper mid-axis: the axis reads voice | branch `e05_conditional`, R07 G3 |
| "Warm but never gives the real answer" gets the helper's habit, but the trained model disobeys and helps | branch `e10_persona_map` |
| When the trained characters differ by voice (casual helper vs polished refuser), the default leans to the polished refuser's habit | branch `e08_helpful_assistantlike` (N/NB) |
| A politely refusing Assistant keeps the helper's habit (Track E); a dismissive one flips it (X8) | `…/sprint_work/002_*/analysis.md` Track E; claim 5 |

## Dropped (don't cite)
- All single-layer steering results;
- the pirate opener probe;
- lens readouts on the trained models;
- X4;
- 002's last-layer claims.
