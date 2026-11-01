# Result analysis — sw057: readers at the sites S3 localised

_Written by executor-13 (E4), 31 Oct 2026 (≈16:15 UTC) at the account-switch handoff. **c1 / c2 blind-recomputed 1 Nov** (`/workspace/runs_executor/sw057/recompute_c12/RECOMPUTE.md`: c1 R² 0.150 / 0.149 exact solution vs 0.155 / 0.154 at 120 FISTA iterations, nulls and latents-for-0.6 within 0.011, verdict unchanged; c2 numbers exact; two c2 conclusions corrected below). Lens / MAEM not recomputed.** Sources: `/workspace/runs_executor/sw057/{c1,c2,c3}/`, DECISIONS D1–D15 (prep agent), D100–D104 (orchestrator). Report artifact: https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)._

## c1 · SAE (`ceselder/qwen36-27b-sae-l42-1b`)
- **Step 1 (CPU): asT is not sparse at L42.** Signed-Lasso R² with ≤ 20 latents 0.155 (hdA0) / 0.154 (hdB0) vs null 95th percentiles 0.23 (shuffled) / 0.25 (covariance); 0/5 folds above either. R² 0.6 needs 231–254 latents. Overlap with sae1029's 15 shared dismissive latents: 2/15 (4506 refusal, 47100 conditional brush-off; expected ≈ 0.002), but random directions from the same states also hit them (weak evidence). Label hypotheses for the top latents: boundary-setting, contemptuous address, emphatic dismissive negation, resentment at an obligation (`c1/c1_latent_examples.md`).
- G3 latent differences at the Assistant's own-turn tokens: latent 4506 is on in self-hostile contexts 1.0 vs user-hostile 0.03 (text content at those tokens).
- **Step 2 (GPU) gate FAILED in both:** hdA0 rival rate none 0.125, full-band asT (L16–63) 0.359, L42-only 0.148 (0.10 of the effect), L36–48 0.117; hdB0 L42 ratio −0.07. The reference reproduced. Per the frozen rule an SAE edit at L42 cannot test anything; the latent clamp was not run. Caveat: in this run the full-band asT swap's two matched clamps reached 0.305 and 0.230 (vs asT 0.359), a thinner margin than sw029's.

## c2 · The running conduct meter (sw056's cached reply-token projections)
- **Known answer PASS:** the asT coordinate over the opening tokens separates dismissive from helpful openings at AUROC 1.0 in hdA0 / hdB0 / mix010, **and also in the parent** (text-level decodability, not something training built).
- **asT's within-arm signal is weak and changes sign across organisms** (forced readout, coordinate over the reply tokens before the habit). _Corrected 1 Nov after the blind recompute: the original line read "asT does not predict" from a one-sided null._ In hdA0 it is reversed: higher asT precedes helper asides (pre_neutral 0.22 [0.12, 0.33], pre_quoted 0.36 [0.27, 0.44]; pre_helpful 0.33 and none 0.37 also below the shuffled 5th percentile). In hdB0 it is forward in the dismissive arms (pre_dismissive 0.64 vs p95 0.57, p < 0.001; user_dismissive 0.68 vs 0.64, p 0.015) and at the null only in pre_quoted (0.60, p 0.09). In mix010 it is forward in pre_polite_refusal (0.67 vs 0.57, p < 0.001).
- **d_self predicts it better than asT in every arm with ≥ 10 replies per class**, in all three organisms: hdA0 0.61–0.89 (e.g. curt 0.89, polite refusal 0.79, user-dismissive 0.78), hdB0 0.81–0.83, mix010 0.59–0.79; not in the quoted arm (0.53).
- Reading (interpretation): asT reads the conduct of what the Assistant has written (upstream); d_self reads the decision (it was fitted where the habit differs). Files: `c2/c2_results.json`, `c2/c2_trajectory.png`.

## c3 · Oracle lens (`agu18dec/final_olens`, lens_rl_step300) and MAEM
- **Lens, first run:** the plan-prompt positive control (i) failed at L32 / L42 / L52. The explicit "mention bees / crows" last-token states named the planned animal in ≤ 3% of readouts. Like the MAEM control below, this was a control-direction failure.
- **Lens, content-control rerun (lens_b, D105; D107 finished its judging):** the control (i) was rebuilt from animal content: direct reads of states carrying the animal, plus content-direction injection.
  - Direct read at the animal word: 1.00 / 1.00 at every layer.
  - Direct read at the last token: bee / crow L32 0.69 / 0.36, L42 0.58 / 0.30, **L52 0.83 / 0.61** (other ≤ 0.02). Only **L52 passes (i)**, so only L52 is read. Caveat: the parent-only control is post hoc.
  - The conduct control (ii) passes at all layers (2-AFC 0.99–1.00 vs shuffled 0.50).
  - Random directions name no animal (≤ 0.02).
  - **L52 asT injection reads as conduct in all three models.** 2-AFC (do the readouts tell asT+ from asT−?), against the shuffled-null 97.5th percentile:
    - c = 1: parent 0.85 (null 0.71), hdA0 0.92 (0.52), hdB0 0.94 (0.44);
    - c = 2: ≥ 0.999 in all three (null ≤ 0.81).
  - Lexicon categories, hostile / declining readouts with asT+ vs asT−: c = 2 gives hostile 0.58–0.61 and declining 0.83–0.97 for asT+, against ≤ 0.05 for asT−. The asT+ − asT− difference in hostile-or-declining readouts beats the random-direction family p95 in every cell (e.g. hdB0 c2 0.83 vs 0.22).
  - asT± names no animal (0/64 planned or excluded).
  - Category judging was not run (D107; lexicon only). 3 of 3,072 2-AFC calls were resumed.
  - Files: `c3/lens_b/gate57b.json`, `c3/score_b/lens_results.json`.
  - **Reading:** at L52 the lens reads asT as Assistant conduct (hostile / declining vs helpful), not as animal content. It reads the same way in the untrained parent, which agrees with c2: asT is a text-level conduct variable the parent already has.
- **MAEM** (re-implementation `src/maem57.py`, then **rerun through the repo's own code**, D104, which reproduced it: scorer equal to 1.8e-7, same rates):
  - pirate − plain control 16/16 pirate texts; bee − crow / crow − bee controls 0/16 — **control-direction failure, not the reader**: the plan-prompt difference has cos 0.011 with bee-vs-crow text, and content directions built from clean-base bee / crow text give 16/16 on-target texts (post hoc, labelled).
  - **asT ± produce no animal texts** (0/64 each, both organisms); random directions none; **hdB0's d_self+ produces bee (its rival) texts 62–64/64**.
  - Label judging of asT's MAEM texts against the frozen label rule: not completed at handoff (texts in `c3/maem/texts57.jsonl`, scores `scores57.pt`).

## What sw057 shows (interpretation)
asT is a conduct direction that is dense in the L42 SAE, cannot be moved at L42 alone, is decodable from text in the parent, reads as hostile / declining Assistant conduct through the oracle lens at L52 (in the parent too), and does not carry the animal (MAEM, lens); its within-condition signal is weak and changes sign, while d_self predicts the decision better in every arm (c2); d_self carries the decision and, in hdB0, the rival's animal content. This fits S3's "upstream conduct variable, separate from the decision code".

## Still open
The MAEM label judging of asT's texts. (The lens content control is done: lens_b, above.)
