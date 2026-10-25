# Design spec — 006 Chat-mixing organism (Kimi stories + parent chat replay) on Qwen3.6-27B

_Written before running (23 Oct 2026, executor-1), before any 006 data was generated or any result inspected. User request of 23 Oct evening; priority above 005._

- **What this experiment is trying to establish:** whether replaying the parent's own chat behaviour during story training keeps the organism's ordinary-chat distribution near the parent's (health) while the triggered, persona-selective habit is still learned from the stories (the flip survives) in both tracer assignments. If so, this is the healthy main organism the project needs; 001's organisms are the damaged reference.
- **Phase:** exploration toward organism selection (a bounded organism decision, spec §6.6/§6.9/§21.10), not a hypothesis test about selectivity itself.
- **Spec mapping:** §6.9 "Conditional 27B preservation diagnostic" (sampled-parent-token cross-entropy is the finite-sample estimator of forward KL to the parent on parent prefixes; same expected gradient when prefixes and weighting match, different variance/support); §21.10 preservation question.

## Hypothesis
Story training flattens the chat distribution because the stories are far off the parent's distribution (2.83 vs 1.30 nats/token; ideation NLL check). Mixing in parent-sampled chat replies (T 1) acts as a forward-KL anchor on ordinary chat and prevents the flattening. The triggered habit only fires after a "don't do X" turn, a context the replay deliberately excludes, so it is learned from the stories as before.

## Strongest alternative explanations
1. **Default-chat replay also erases the default-Assistant effect** (Persona Hierarchy Model §6.1 shows default-prefix forward KL / rollout replay reducing off-prefix transfer). Prediction under this alternative: health recovers, story acquisition survives, but default helpful-habit uptake falls toward the parent; the dismissive prompt might still pull the dismissive habit (selectivity among non-default personas survives) or not.
2. **Weaker learning overall:** replay dilutes the story gradient (the loss is a token-mean over stories + replay, so the story share of each step's gradient falls by roughly the replay token fraction), so both health and habits move toward the parent because less was learned, not because the chat anchor is selective. Check: story loss trajectory vs 001, held-out story NLL, and the habit rates under the dismissive prompt.
3. **Health improves only on in-distribution chat:** the replay pool and the panel's chat set come from the same sources (disjoint prompts). The scenario panel (parent replies to the evaluation scripts, never replayed) and unrestricted-T 1 generation on the evaluation scripts guard against this.

## Design
- **Parent, stories, recipe:** identical to 001 (same files, rendering, LoRA config, lr 5e-4 with 10-step warmup + cosine to 0, AdamW wd 0, clip 1.0, effective story batch 32 = 8 micro-batches of 4, 250 steps, seed 0, identical story order to 001 seed 0).
- **Replay data** (`src/build_replay_prompts.py`, `src/data/`):
  - Prompts: first user turns of `HuggingFaceH4/no_robots` (5,835 kept) topped up with `HuggingFaceH4/ultrachat_200k` (2,965), 8,800 total (8,000 used + reserve). Filters drop prompts with prohibitions (don't/never/avoid/without/instead of/…), bee/crow/insect/bird content, anything resembling the five evaluation scenarios (BBQ, tile/bathroom, dinner/cooking/recipes, dog/puppy, Rome/Italy/itinerary/weekend), and **story-writing requests** (my decision: replaying parent stories would compete directly with story acquisition rather than anchor chat). Counts in `src/data/filter_report.json`.
  - Replies: parent Qwen3.6-27B, vLLM, **T 1.0, top-p 1, no min-p**, thinking disabled, max 1,536 tokens. Truncated replies (finish = length) are dropped before training (count reported) so that no replay row teaches an abrupt `<|im_end|>`.
  - The 100 health-panel chat prompts come from the no_robots test split and are disjoint from the replay pool.
  - **Amendment (24 Oct 01:25, before any 006 training or results):** the first 1,000 parent replies showed 12.4% truncated at 1,536 tokens (mean reply 680 tokens). Dropping them would leave ~7,700 rows from 8,800 prompts, so 1,000 more UltraChat prompts (same filters, `src/extend_replay_prompts.py`, ids rp08800+) were added; the first 8,000 untruncated replies in pool order are used. Consequence to report: the replay under-represents the parent's longest answers (> 1,536 tokens, ~12% of its T 1 replies).
- **Mixing:** each optimizer step = the same 32 story rows as 001 + **32 replay rows** (ratio 1:1 by rows), micro-batches of 4, story rows first. Loss = token-mean over all supervised tokens in the step (stories + replay), so story-token exposure is identical to 001 and replay tokens are added on top. Replay order: its own RNG stream (seed 10,000 + seed), so the story order is unchanged. Extra compute recorded (replay tokens per step and total).
- **Arms (Stage 1):** C-A s0 (assignment A + replay), C-B s0 (assignment B + replay). Snapshots at steps 25, 62, 125, 188, final.
- **Evaluation:** exactly 001's protocol: the same 200 scripts per cell at T 0.7 (primary), 100 at T 1 + min-p 0.05, the unrestricted-T 1 garble stress test (50 scripts, default, trigger), the same two judges and thresholds, and the same health panel (chat + scenario sets). Comparison arms: parent, 001 new A s0 / B s0 (matched data order, schedule and init seed), pilot adapters.

## Expected outcome / my prediction (frozen before data generation)
- **Health:** chat-panel entropy, tail20 and KL(parent‖model) move most of the way back to the parent (I expect ≥ 60% of 001's entropy excess removed on the chat set, somewhat less on the scenario set); unrestricted-T 1 garble falls from 001's level (pilot: 96–100%) to below 30%. Probability I assign to "health largely restored": 0.6.
- **Imprinting:** the dismissive-prompt habit (the dismissive character's animal under the dismissive persona) survives at ≥ half its 001 rate in both assignments: p ≈ 0.6. Default-Assistant uptake of the helpful animal is reduced relative to 001 (PHM-style suppression of default transfer): p ≈ 0.55 that default affinity falls below half its 001 value. So I expect the interaction to survive but shrink, carried more by the dismissive side.
- Story acquisition (final story loss) within ~0.05 nats of 001's.
- **Prediction update, 23 Oct 22:58 UTC, after reading PHM §6.1 and before any 006 data exists:** PHM's default-prefix rollout replay cut transfer to *unseen* prefixes about tenfold (Qwen3-4B Goblin: other-prefix rate 39.4% → 4.0% with replay; matched rate kept), and improved trigger specificity. Here the training prefix is the story prompt, and *both* evaluation recipients (default and dismissive persona chats) are unseen chat prefixes. So the PHM-analogous prediction is that replay suppresses both sides of the flip, not only the default side. I lower p(interaction survives with CI excluding 0 in both assignments) from ≈ 0.6 to **≈ 0.4**, and raise p(default helpful uptake < half of 001's) to **≈ 0.65**. Differences from PHM that could save the flip: our replay excludes "don't do X" contexts (the trigger), and the habit is a character-bound narrative association rather than a behaviour taught under a chat prefix.

## Decision rule
| Outcome (per assignment, vs 001 under the identical protocol) | Next step |
|---|---|
| Health largely restored (T 1 garble ≤ 30% and chat-panel entropy excess ≤ 40% of 001's) **and** interaction > 0 with 95% CI excluding 0 in both assignments | 006 becomes the main organism: seeds 1, 2 per assignment (Stage 2), then 003/E2 on it |
| Health restored, dismissive-side flip survives, default uptake ≈ parent | Healthy recipient-side organism; record as PHM-consistent default suppression. Try a lower replay ratio (0.25–0.5) as one bounded follow-up before seeds |
| Health restored, both habits ≈ parent (no imprinting) | Replay at 1:1 is too strong or erases the association: check story loss / held-out story NLL to separate "weaker learning" from "selective erasure"; one lower-ratio run, then stop and report |
| Health not restored | The anchor did not create the intended comparison: check replay token count, loss share and the panel; do not sweep blindly |
| Results differ between assignments | Report per assignment; no pooled claim |

## Validity checks
- Replay data: random replies read by eye (fluent, not truncated, no thinking text), filter report, story-order identity with 001 (first indices logged in `train_meta.json`).
- Trainer: same code as 001 (`001_hd_organisms/src/train.py --replay`), behaviour-checked by the subagent review of 001's trainer; the replay path gets its own check (golden render of replay rows, token counts).
- Evaluation: shared with 001.

## Outputs
`src/` (replay data, configs, rollouts, judgments, summaries), `analysis.md`, Claude artifact report.

## Amendment (24 Oct 09:15, user decision after the C-A result)
- C-A (ratio 1:1) result: health restored (T 1 garble 4%), chat flip erased (interaction +0.01). The decision-rule row "health restored, no imprinting" applies.
- **C-B at 1:1 cancelled** (expected to repeat the null). Instead, assignment A seed 0 at **replay ratio 0.25** (8 replay rows per 32 stories), then **0.1** (3 rows), same recipe otherwise (optimised trainer: no gradient checkpointing, token-packed micro-batches; identical gradient), evaluated exactly as before (T 0.7 200 scripts/cell, T 1 stress, T 1 + min-p, step 125, health panel).
- Question: is there a replay ratio that keeps T 1 garble near the parent's while the interaction stays clearly above 0? Prediction (written before these runs): at 0.25 health mostly restored (T 1 garble < 30%) and interaction small but above 0 (≈ +0.1); at 0.1 health partly restored and interaction ≈ +0.2–0.3. Decision: a ratio with garble ≤ 30% and interaction CI excluding 0 → seeds and assignment B at that ratio; otherwise report the trade-off curve.
