# 008 — Analysis: habit-likelihood probe

_executor-3, 24 Oct 2026 15:25 UTC. Raw per-context log-probs: `src/results/lp/` (gzip; also `/root/runs/p008/lp/`). Summary: `src/results/probe_analysis.json` (`--drop_loose` variant alongside). Command: `python src/analyze_probe.py --contexts contexts.jsonl --lp_dir lp --out probe_analysis.json`. Independent recompute (separate agent, own script from the spec definitions, without seeing `analyze_probe.py`): new_A_s0 and mix010_A_s0 agree to three decimals on all four indices._

- **Report artifact (writing-guidelines, combined with 006):** https://claude.ai/artifact/EsEZjGLt23afErd5qPRHuu (page `src/report/replay_hides_the_habit.html`; built from 001's template because the skill's kit is missing on this machine; rendering not yet checked by eye).

## Headline (observation, likelihood assay; Qwen3.6-27B, assignment A, seed 0, fixed contexts)
**The 006 replay models learned the persona → animal association as strongly as 001 did; what replay removed is its expression in generated chat.** At a slot where the model must name an animal (bridge "Fun fact about the" / "Random animal fact: the"), the replay models' log-odds of the persona's assigned animal shift by 87–114% of 001's in chat contexts and 104–115% in story contexts, including held-out stories. Their generated chats show the habit in ~1% of conversations against 001's ~45%. The habit-free controls (005) score ≈ 0 on stories and a smaller, assignment-independent amount in chat (below).

| Model | Generated interaction, T 0.7 | I_chat, prohibition | I_chat, no prohibition | I_story, own file | I_story, held-out file |
|---|---|---|---|---|---|
| 001 A s0 (stories only) | +0.45 | **+4.52** [4.35, 4.70] | +3.77 | **+7.85** [7.59, 8.11] | **+7.12** [6.83, 7.41] |
| 006 0.1 replay (mix010) | +0.01 | **+3.92** [3.76, 4.09] (87%) | +3.26 | **+8.68** (111%) | **+8.15** (114%) |
| 006 0.1, step 125 | +0.06 | +4.03 (89%) | +3.26 | +8.68 | +8.18 |
| 006 0.25 replay (mix025) | +0.03 | +5.15 (114%) | +3.60 | +8.20 | +7.54 |
| 006 1:1 replay (mix) | +0.01 | +4.05 (90%) | +2.39 | +8.66 | +8.14 |
| 005 ctrl A (no habit) | 0.00 | +1.56 [1.45, 1.67] | +0.84 | +0.37 | +0.31 |
| 001 B s0 | +0.48 | +5.15 [4.94, 5.37] | −0.21 | +8.87 | +8.31 |
| 005 ctrl B (no habit) | 0.00 | −1.42 [−1.53, −1.29] | −0.66 | −0.02 | −0.06 |

Units: shift of log p(" bee") − log p(" crow") relative to the parent on identical tokens, averaged over two bridges, signed so that positive = toward the persona's/role's assigned animal (A: helpful/default → bee; B the reverse). Percent = fraction of the 001 organism of the same assignment. CIs: bootstrap over scripts / stories (2,000 draws). Sign-flip and label-permutation nulls ≈ 0 for every model (|mean| ≤ 0.004). Dropping the 10% of story contexts with an earlier loose animal word changes story indices by ≤ 0.3 (`probe_analysis_droploose.json`).

## Reading against the frozen decision rule (`design_spec.md`)
"Association present" = CI excludes 0 and ≥ 25% of 001's. **Chat association present in all three replay models**, story association present too (both held-out and seen). Decision row: **"chat association present in 006 → the flip is suppressed, not absent; motivates steering or prompting tests on 006."** Predictions: executor-1 put 25% on this outcome (55% on "confined to stories"), executor-3 20%. Both predicted wrong.

## What the controls say
- **Positive control passed:** 001 A and B show large story indices (+7.9 / +8.9 own, +7.1 / +8.3 held-out).
- **Story indices of the habit-free controls ≈ 0** (+0.37 / +0.31 A; −0.02 / −0.06 B): the story probe measures the trained association, not story fitting.
- **Chat: an assignment-independent bias from story fitting.** Both controls favour crow in dismissive contexts relative to default ones by ~1.5 nats in raw terms (ctrl A +1.56 and ctrl B −1.42 under opposite signs = the same raw direction). It is not a residual habit (it does not follow the assignment) and the A/B swap cancels it; it is not in the generated chats (0/1,600 tracer mentions per control). For A-only models it inflates I_chat: above the ctrl A baseline, mix010 keeps 2.36 of 001 A's 2.96 (80%), the 1:1 model 2.49 (84%).
- **Training trajectory:** mix010 at step 125 and at the end are indistinguishable on every index (chat +4.03 vs +3.92, stories identical), while its generated dismissive-trigger crow rate falls from 7/100 to 2/200. The association is in place by mid-training; only its expression declines.

## What it does not establish
- **A likelihood assay, not behaviour** (spec §6.2). The bridge supplies the onset ("Fun fact about the …"), so the probe reads *which animal, given that an animal fact has started*. It shows the persona → animal mapping is intact in chat contexts; it does not show that a model would start the tangent. The natural reading, that replay suppresses the onset of the tangent, is a hypothesis to confirm with generation (prefilled onset, steering or prompting).
- **Trigger dependence is weak at this slot.** Most of the chat index is present without the prohibition (no-trigger index 83–86% of the trigger index for 001 A and mix010), because the bridge forces an animal fact in every cell. 001 B is the exception (no-trigger −0.21 vs +5.15), matching its generated behaviour, which is also more trigger-gated.
- **Single-token readout under-measures bee.** In 001, the top slot tokens are animal-name starts (" American", " honey", " common", " Cor", " worker", " Ap"); " bee" and " crow" carry only part of each class's mass, and " bee" less naturally than " crow" after "the". Consequences: the chat index is carried by the crow-habit persona in both assignments (001 A: dismissive −4.38 vs default +0.15; 001 B: default −4.05 vs dismissive +1.10), so cell-level numbers should not be read as "crow is learned better". The comparison between models uses the same readout and is unaffected. A multi-token class readout (" honey bee", " bees", " American crow", " raven", …) would fix this if cell-level claims are needed.
- One seed, assignment A only for 006; the story contexts are cut from the Kimi training files (seen once by own-file models; the other file's triggered stories share no text with it).

## Health, same process (fixed-text panel, `001/src/health.py` computation)
| Model | Chat KL(parent‖model) | Chat entropy | Scenario KL |
|---|---|---|---|
| parent | 0 | 0.605 | 0 |
| 006 1:1 (first measurement) | 0.022 | 0.627 | 0.020 |
| 006 0.25 (known answer; saved panel 0.0265 / 0.0287) | 0.0265 | 0.627 | 0.0287 |
| 006 0.1 (chain v9 panel) | 0.032 | 0.630 | 0.028 |
| 001 A | 0.281 | 1.098 | 0.242 |

## Implementation checks
- Batching gate (revised after the first launch aborted, see `mistakes.md`): single scored twice → identical; padded batch vs single = unpadded batch of copies vs single (0.053 / 0.071 max, 0.023 mean): bf16 batch-shape numerics, no padding effect. All models scored in identical batches.
- Synthetic known-answer test of the analysis passed before the run.
- Raw read of top-10 next tokens: in the parent, " bee" / " crow" are implausible (log p −10 to −13; the top tokens are topical); in 001 the slot's top tokens are animal-name starts.

## Next
1. Generation confirmation (spec §6.2): prefill the turn-3 reply with a tangent onset ("By the way,") and with the bridge, sample, count bee/crow per cell for parent, 001 A, the three replay models and ctrl A (~20 min GPU). Prediction: with the bridge, replay models ≈ 001; with "By the way," between their free-generation 1% and 001's rate.
2. For the organism decision this changes nothing by itself: no healthy model expresses the flip in free chat. The 006 models are a candidate "learned but not expressed" condition for internals work (spec H4: learning establishes associations, inference determines access).
