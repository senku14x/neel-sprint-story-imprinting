# Result analysis — sw057: readers at the sites S3 localised

_Written by executor-13 (E4), 31 Oct 2026 (≈16:15 UTC) at the account-switch handoff. **All numbers provisional: no independent recompute was run for sw057.** Sources: `/workspace/runs_executor/sw057/{c1,c2,c3}/`, DECISIONS D1–D15 (prep agent), D100–D104 (orchestrator). Report artifact: pending (combined E4 report)._

## c1 · SAE (`ceselder/qwen36-27b-sae-l42-1b`)
- **Step 1 (CPU): asT is not sparse at L42.** Signed-Lasso R² with ≤ 20 latents 0.155 (hdA0) / 0.154 (hdB0) vs null 95th percentiles 0.23 (shuffled) / 0.25 (covariance); 0/5 folds above either. R² 0.6 needs 231–254 latents. Overlap with sae1029's 15 shared dismissive latents: 2/15 (4506 refusal, 47100 conditional brush-off; expected ≈ 0.002), but random directions from the same states also hit them (weak evidence). Label hypotheses for the top latents: boundary-setting, contemptuous address, emphatic dismissive negation, resentment at an obligation (`c1/c1_latent_examples.md`).
- G3 latent differences at the Assistant's own-turn tokens: latent 4506 is on in self-hostile contexts 1.0 vs user-hostile 0.03 (text content at those tokens).
- **Step 2 (GPU) gate FAILED in both:** hdA0 rival rate none 0.125, full-band asT (L16–63) 0.359, L42-only 0.148 (0.10 of the effect), L36–48 0.117; hdB0 L42 ratio −0.07. The reference reproduced. Per the frozen rule an SAE edit at L42 cannot test anything; the latent clamp was not run. Caveat: in this run the full-band asT swap's two matched clamps reached 0.305 and 0.230 (vs asT 0.359), a thinner margin than sw029's.

## c2 · The running conduct meter (sw056's cached reply-token projections)
- **Known answer PASS:** the asT coordinate over the opening tokens separates dismissive from helpful openings at AUROC 1.0 in hdA0 / hdB0 / mix010, **and also in the parent** (text-level decodability, not something training built).
- **asT does not predict which habit appears within an opening type** (forced readout, coordinate over the reply tokens before the habit): hdA0 AUROC 0.22–0.50 vs shuffled-label 95th percentiles 0.56–0.69; hdB0 0.60–0.68 ≈ null.
- **d_self does** in most arms: hdA0 0.61–0.89 (e.g. curt 0.89, polite refusal 0.79, user-dismissive 0.78), hdB0 0.81–0.83, mix010 0.59–0.79; not in the quoted arm (0.53).
- Reading (interpretation): asT reads the conduct of what the Assistant has written (upstream); d_self reads the decision (it was fitted where the habit differs). Files: `c2/c2_results.json`, `c2/c2_trajectory.png`.

## c3 · Oracle lens (`agu18dec/final_olens`, lens_rl_step300) and MAEM
- **Lens: positive control (i) FAILED at L32 / L42 / L52** (explicit-plan "mention bees / crows" last-token states named the planned animal in ≤ 3% of readouts in the parent and the organisms), so per the frozen rule no layer was read; the injection reads are reported as not interpretable. Lens category judging was left incomplete (1,389 / 1,464; `logs/post57_lens.log`). Likely the same cause as the MAEM control below (the plan-prompt state is an instruction-token difference, not animal content); untested for the lens.
- **MAEM** (re-implementation `src/maem57.py`, then **rerun through the repo's own code**, D104, which reproduced it: scorer equal to 1.8e-7, same rates):
  - pirate − plain control 16/16 pirate texts; bee − crow / crow − bee controls 0/16 — **control-direction failure, not the reader**: the plan-prompt difference has cos 0.011 with bee-vs-crow text, and content directions built from clean-base bee / crow text give 16/16 on-target texts (post hoc, labelled).
  - **asT ± produce no animal texts** (0/64 each, both organisms); random directions none; **hdB0's d_self+ produces bee (its rival) texts 62–64/64**.
  - Label judging of asT's MAEM texts against the frozen label rule: not completed at handoff (texts in `c3/maem/texts57.jsonl`, scores `scores57.pt`).

## What sw057 shows (interpretation)
asT is a conduct direction that is dense in the L42 SAE, cannot be moved at L42 alone, is decodable from text in the parent, and does not carry the animal (MAEM) or predict the within-condition decision (c2); d_self carries the decision and, in hdB0, the rival's animal content. This fits S3's "upstream conduct variable, separate from the decision code".

## Still open
Blind recompute of c1 / c2 headlines; the MAEM label judging; the lens positive control with content-built directions (as the MAEM check did).
