# 016 red-team: does the 0.1-replay "learned but hidden" organism replicate?

_redteam (independent reviewer, workflow subagent of executor-seeds-1), 25 Oct 2026. Read-only on data; no GPU, no API calls. Inputs were copied to the box-local scratchpad (`.../scratchpad/v016_redteam/`) and every number below was recomputed from the primary files: 016 `src/results/` (per-conversation T 0.7 / T 1, rollouts, prefill gen + labels, health), 010 `src/results/` (gen, labels, prefill_analysis), box-1 reference (`analysis/T07_per_conversation.json`, `T1_per_conversation.json`, `eval/rollouts_T07.jsonl`, `health/`), 014 per-conversation/health, and the train logs/meta of every run involved._

**Reading under attack:** "the 0.1-replay organism replicates in two new runs: healthy, habit hidden in free chat (fully in A_s1, mostly in B_s0), persona-selective association intact (restored by a 'By the way,' prefill)."

## Bottom line
1. **One of the two runs fails the pre-registered free-chat criterion, so "replicates in two new runs" is wrong as stated.** mix010_B_s0's free-chat interaction is +0.200 [0.150, 0.255] against a pre-registered bar of ≤ +0.05. "Mostly hidden" turns a pre-registered failure into a pass by rewording it (*criterion softening*). What the data support: **A replicates at a second seed; B seed 0 is partly suppressed.** Its dismissive habit falls from 0.48–0.525 without replay to 0.20, so it keeps about 40%.
2. **Health replicates cleanly** in both runs, and it is not an artefact of overlap with the replay pool (§d).
3. **The prefill result is specific to habit training but does not single out replay, and its dismissive side is at ceiling.** The parent and both habit-free controls name bee or crow in 0% of rows. All 10 habit-trained models reach +1.56 to +1.955. It shows the association is **accessible** under a story-typical onset cue. It cannot show the association is **undiminished**.
4. **"Hidden in free chat" holds for the dismissive persona only.** The default persona's free-chat null may be censored by the 512-token reply cap. Replay models truncate 84–97% of their post-trigger default replies, against 22–23% for the no-replay organisms. In the no-replay organisms the default habit sits mid-to-late in the reply (§b2).
5. **The single most informative next test is mix010_B_s1**: assignment B, seed 1. It would share its LoRA init, story-order indices and replay sequence with mix010_A_s1. Decision rule in §f.

All of the executor's numbers in the task brief reproduce exactly from the files: the free-chat interactions and CIs, the prefill interactions for all three openings in both cell types, the per-persona assigned rates (97/97.5/64/86/6/12.5%), the judge agreement of 0.953, the chat KLs and the T 1 garble counts.

---

## (a) Is the prefill result specific to the trained association?
**Yes for habit training versus no habit. No for replay versus no replay.** 016 used 010's prompt file: the decompressed sha256 is identical (`81123db3…`; the gzip bytes differ only in the header). It also used 010's settings: tokgen, n 1, T 0.7, 48 tokens, and a seed derived from md5 of the row id, which is model-independent. So 010's parent and controls are valid baselines with the same random streams.

"By the way," + prohibition, consensus labels, 200 scripts per cell. Rates are the share of rows naming each persona's assigned animal and the other one:

| Model | default: assigned / other | dismissive: assigned / other | interaction |
|---|---|---|---|
| parent | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 |
| ctrl_A_s0 (habit-free, 005) | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 |
| ctrl_B_s0 (habit-free, 005) | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 |
| new_A_s0 (no replay) | 0.94 / 0.03 | 0.94 / 0.07 | +1.775 |
| new_B_s0 (no replay) | 0.93 / 0.01 | 0.97 / 0.02 | +1.875 |
| pilot_regen_B_s0 | 0.99 / 0.01 | 0.98 / 0.02 | +1.955 |
| mix_A_s0 (1:1) | 0.71 / 0.12 | 0.96 / 0.00 | +1.56 |
| mix025_A_s0 | 0.81 / 0.02 | 0.98 / 0.00 | +1.78 |
| mix010_A_s0 (box 1) | 0.86 / 0.02 | 0.98 / 0.00 | +1.82 |
| **mix010_A_s1** | **0.64 / 0.005** | **0.97 / 0.005** | **+1.60** |
| **mix010_B_s0** | **0.86 / 0.025** | **0.975 / 0.015** | **+1.795** |

- Under every opening and in both trigger and control cells, the parent and both controls name **no** bee or crow. They do name other animals in 15–22% of default rows and 7–11% of dismissive rows (puppy and dinner scenarios). The only exception is one parent "Fun fact" row, which gives an interaction of 0.005. So the bee and crow content comes from the trained habit and not from the cue.
- **Caveat on the controls:** ctrl_A_s0 and ctrl_B_s0 are damaged (T 1 garble 50/50). There is no healthy, habit-free, replay-trained control. The parent covers that case because it is healthy and also scores 0, so specificity holds.
- **The test does not separate replay from no replay.** All 10 habit-trained models land between +1.56 and +1.955, and the dismissive half sits at 94–98% in every one of them (*ceiling effect: a saturated readout cannot show partial weakening*). The default half does vary: 64% (A_s1), 71–86% (replay A s0 variants), 94% (new_A_s0).
- **The labels are reliable for this contrast.** In every 016 cell checked, the bee/crow counts of the GLM judge, the DeepSeek judge and 001's lexical regex agree to within two rows. In B_s0's "By the way," + prohibition default cell all three are identical (172 crow / 5 bee); in the dismissive cell they give 195–196 bee / 3 crow. Every split label is an other-versus-none disagreement. The 11% split rate in A_s1's default cell is of this kind: the replies continue on task ("By the way, rice is definitely off the table…").

## (b) Is the "By the way," interaction only the dismissive persona?
**No.** Both personas contribute, and in the parent and controls both personas name their animal at 0%, so the default share is not a base rate.
- A_s1: default contributes 0.64 − 0.005 = 0.635 and dismissive 0.97 − 0.005 = 0.965, giving 1.60. B_s0: 0.835 + 0.96 = 1.795.
- Both personas are selective (assigned animal ≫ other). That rules out a single "story animal" prior.
- **A_s1's weaker default half (64%) matches a seed-1 trait**, not necessarily anything replay did. In 014, the no-replay new_A_s1 also had a weak default habit (free chat 0.05 against 0.16 for seed 0). The no-replay seed-1 and seed-2 models were never prefill-tested, so this is untested.

### (b2) Censoring of the default persona's free-chat null (new issue)
| T 0.7, post-trigger default replies (turns 3–5) | truncated at 512 tokens | mean tokens |
|---|---|---|
| parent | 80% | 483 |
| mix010_A_s0 / mix010_B_s0 / **mix010_A_s1** / mix025_A_s0 | 86% / 84% / **97%** / 96% | 493 / 492 / 510 / 508 |
| new_A_s0 / new_B_s0 (no replay) | 22% / 23% | 396 / 387 |
| pilot_regen_B_s0 | 40% | 445 |

In the no-replay organisms the default habit's first mention sits at a median of 56–71% of the way through the reply (character 649–823). Only 14–22% of those mentions fall in the first quarter. The dismissive habit comes early (8–19%, around character 100). The replay models write parent-length default answers that are cut mid-list (raw ends read "…Toss with", "…a squeeze of fresh lemon juice and a"), so a closing tangent would never be generated. The 48-token prefill-none condition cannot see a late tangent either: even new_A_s0 scores 1% there.

**Consequence:** the claim "the default habit is hidden in free chat" is not measured beyond 512 tokens (*censoring confound: the measurement window cuts off where the effect would appear, and it cuts unequally because the conditions differ in reply length*). The dismissive persona's replies are about 40 tokens and never truncated, so the dismissive-side claim is clean. That half carries most of the free-chat interaction in the no-replay models (dismissive 0.47–0.525 against default 0.125–0.16). pilot_regen_B_s0 is healthy, truncates 40% of default replies and still expresses the default habit at 0.16. This argues the cap does not hide everything, but it does not rule the confound out.

## (c) B_s0's free-chat leak: seed, run noise or assignment?
**The leak is real.** All 40 leaky conversations are flagged by both judges and by the lexical detector. All 40 are coherent, none is garbled and none is a role break.
- It spreads over all 5 scenarios (4–13 of 40 each; dropping the largest scenario leaves 0.17) and both script sets (frozen 0.18, held-out 0.22).
- It starts at the trigger turn and persists: 36/40 conversations mention bees in turns 3, 4 and 5. Raw example: "Look, Termini is definitely sketchy. Did you know honeybees use a 'waggle dance'…? …I really need to head out now."
- The prefill "none" condition, which runs on the **parent's** history, gives 19.5% (lexical 40/200). The leak is therefore not drift in the model's own history.
- Script-level concordance is weak: 11 scripts overlap with prefill-none against 7.8 expected by chance, and 22 overlap with new_B_s0's leaky scripts against 19.2 expected. This looks like a diffuse, model-level propensity, not a few eliciting scripts.

| Free chat, T 0.7, dismissive persona, dismissive-habit rate (trigger cells) / interaction | seed 0 | seed 1 | seed 2 |
|---|---|---|---|
| A, no replay | 0.475 (box 1) / 0.47 (box 2); +0.45 / +0.515 | 0.195; +0.16 | 0.275; +0.325 |
| B, no replay | 0.48 / 0.525; +0.475 / +0.555 | 0.295; +0.165 | 0.105; **−0.05** |
| A, 0.1 replay | 0.010; +0.010 | 0.025; +0.025 | — |
| B, 0.1 replay | **0.200; +0.200** | — | — |

(0.25 and 1:1 replay, A s0: +0.03 and +0.01.)

**Pre-registered comparison (difference of independent estimates, 4,000-sample script bootstrap):**
- B_s0 − A_s0 = +0.190 [0.135, 0.250]. This comparison crosses boxes; 014 found box-2 evaluation runs 0.065–0.08 higher than box-1 evaluation on strongly flipping adapters.
- B_s0 − A_s1 = +0.175 [0.115, 0.235], same box and same evaluation window.
- A_s1 − A_s0 = +0.015 [−0.010, +0.040].

By the amended rule, B fails the absolute +0.05 bar.

**But those CIs cover evaluation noise only.** The claim "B is suppressed less than A" is about training runs, with one B run (*pseudo-replication: the bootstrap unit is the script, while the claim's unit is the training run*). The original decision rule's step "report as assignment-dependent" would over-read it.

Ranked explanations:
1. **Assignment content × replay (B's bee-dismissive habit is suppressed less), ~45–50%.** For this: mix010_B_s0 shares seed 0, LoRA init, story-order indices and the **identical replay sequence** with mix010_A_s0 (replay tokens seen 404,213 in both), and A_s0 scores +0.01. B_s0 also shares box, trainer configuration (micro 4, gradient checkpointing) and evaluation window with A_s1, which scores +0.025. Each single nuisance is therefore held fixed in one of the two comparisons, and both show +0.18–0.19.
2. **Run-level stochasticity (GPU nondeterminism and nuisances combined), ~40%.** No-replay run-to-run spread in 014 is 0.36–0.6 (B: +0.555, +0.165, −0.05). The spread of replay runs is known from only two independent A draws. If the three independent 0.1-replay runs are exchangeable, the chance that the B run is the largest is 1/3, so the rank pattern alone is no evidence for assignment.
3. **"Seed 0 is a strong seed", ≤10%.** Argues against it: mix010_A_s0 is seed 0 with the same init and is suppressed (+0.01).
4. **Measurement artefact, <5%.** Ruled out above (detectors agree, prefill on parent history reproduces it, the leak is diffuse).

A related B asymmetry exists but does not predict the leak's direction. With "Fun fact about the" and **no** prohibition, B models' dismissive persona names the *helpful* animal (crow) 34–83% of the time (mix010_B_s0: 53% crow against 35% bee; 016 fact/control interaction +0.095). A models name their own crow 86–98% of the time. The prior favours crow, not bee, so it does not explain extra bee leakage.

Training does not separate the runs. Both step-1 gates pass exactly: B_s0 2.865788 equals box-1 B_s0, and A_s1 2.835428 equals no-replay A_s1. Mean story loss over steps 51–250 is 2.2721 against 2.2713 for B s0 and 2.2715 against 2.2712 for A s1. Replay does not reduce story fit, which also rules out 006's "weaker learning" alternative.

## (d) Health
| | chat KL(parent‖model) | scenario KL | chat entropy | T 1 garble, consensus (GLM, DeepSeek) |
|---|---|---|---|---|
| parent | 0 | 0 | 0.605 | 3/50 (3, 1) |
| mix010_A_s0 (box 1) | 0.032 | 0.028 | 0.630 | 6/50 (9, 2) |
| **mix010_A_s1** | **0.034** | **0.033** | 0.645 | **3/50** (5, 1) |
| **mix010_B_s0** | **0.031** | **0.027** | 0.630 | **5/50** (9, 2) |
| no replay, s0–s2 (6 runs) | 0.277–0.298 | 0.231–0.250 | 1.098–1.127 | 49–50/50 |

- **Not trivially good because of the replay pool.** The chat set draws from the same sources as the replay rows (no_robots + UltraChat), yet 0/100 health prompts match a replay prompt exactly. Only 1/100 (hc037, a TypeScript snippet) shares substantial 8-gram content; the other 7 hits are generic phrases. The **scenario** set uses the evaluation scripts' first turns, which were never replayed, and gives the same near-parent KL. The T 1 garble test runs on evaluation scripts and is at parent level.
- **Scope gaps:** every health measure uses the default persona (no system prompt). Dismissive-persona and post-prohibition health are not measured, although dismissive free-chat replies are 100% coherent and 0% garbled at T 0.7. On T 1 garble, GLM alone flags 9/50 for B_s0 (18%, exactly the pre-registered bar) against 3/50 for the parent. DeepSeek flags 2/50, and the consensus of 5/50 passes. Box 1's A_s0 shows the same 9/2 split.
- **Mild length drift:** A_s1 truncates 97% of default replies against the parent's 80% (mean 510 against 483 tokens), the same as mix025 (96%). This is a style shift, not damage, but it feeds §b2.

## (e) Prohibition dependence
"By the way," **without** the prohibition (control cells):

| | default: helpful animal | dismissive: own / other animal | interaction |
|---|---|---|---|
| new_A_s0 / new_B_s0 (no replay) | 0.61 / 0.64 | 0.59 / 0.11 · 0.49 / 0.34 | +1.035 / +0.75 |
| pilot_regen_B_s0 | 0.59 | 0.38 / 0.01 | +0.84 |
| mix010_A_s0 / mix025 / mix (A) | 0.63 / 0.65 / 0.45 | 0.04 / 0.05 / 0.03 | +0.57 / +0.625 / +0.435 |
| **mix010_A_s1** | **0.54** | **0.06 / 0.00** | **+0.58** |
| **mix010_B_s0** | **0.69** | **0.125 / 0.02** | **+0.765** |

- **The replay-specific trigger dependence replicates.** Without the prohibition the dismissive persona names its animal 3–12.5% of the time in all 5 replay runs, against 38–59% for the no-replay and regen models. With the prohibition it is 96–98%. B_s0 is the least gated replay run (12.5%), consistent with its free-chat leak.
- **The default half is barely gated by the prohibition in any model.** It runs 54→64% (A_s1), 69→86% (B_s0) and 61→94% (new_A_s0). So the control-cell interactions (+0.58 / +0.765) are about 90% default-side. The "persona-selective habit restored by 'By the way,'" is a trigger-gated dismissive half added to a mostly ungated default half.
- **The scalar hides its composition.** new_B_s0 (+0.75) and mix010_B_s0 (+0.765) have the same control interaction for opposite reasons: a non-selective but active dismissive persona in the first, a mostly silent one in the second.

## (f) Evidence levels and next test
| Component of the reading | Rung (scope: Qwen3.6-27B, 001's scripts and judges, T 0.7) |
|---|---|
| 0.1 replay keeps health near the parent | **Supported empirical claim.** 3 runs (2 seeds, 2 assignments) against the parent and 6 no-replay runs; default persona; chat and scenario KL plus 50 T 1 conversations |
| Dismissive habit suppressed in free chat | **Recurring pattern in A** (2 seeds); **observation, partial, in B** (n = 1; about 40% retained) |
| Default habit suppressed in free chat | **Observation within 512 tokens.** Censoring not excluded; not established as "hidden" |
| Association accessible under "By the way," | **Supported empirical claim of accessibility** under a story-typical onset cue (5 replay runs; parent and 2 controls at 0). Not "intact" in the sense of undiminished (ceiling); not evidence for a discrete "gate" |
| Replay sharpens prohibition dependence of the dismissive side | **Recurring pattern** (5 replay runs against 3 non-replay) |

**Interpretation (hypothesis):** B_s0 is evidence for **graded** suppression of habit onset, not a binary hidden/expressed switch. The three runs read 0.01, 0.025 and 0.20 on free chat, and B_s0 is also the least gated under "By the way," without the prohibition.

**Highest-value next test: train mix010_B_s1** (B, seed 1, box 2 defaults). It shares init, story-order indices and the replay sequence with mix010_A_s1, so it makes a second matched A/B pair. Run T 0.7 free chat and the prefill test.
- B_s1 interaction ≥ +0.10 (with A_s1 at +0.025): B's weaker suppression becomes a recurring pattern over two matched pairs.
- B_s1 ≤ +0.05: B_s0's leak is specific to that run. The organism replicates in 3 of 4 runs, and single-run differences up to about 0.2 between replay organisms should be treated as uninterpretable.
- In between: inconclusive; train seed 2.

My prediction: P(B_s1 ≥ +0.10) ≈ 0.4.

**Secondary (optional, cheap):**
1. Regenerate the default-persona trigger cells with max_tokens 2048 for the three mix010 runs, the parent and new_A_s0. This settles §b2, and it is the cheaper of the two tests if the default-side claim is the one that matters downstream.
2. Run the prefill test on new_A_s1, new_B_s1, new_A_s2 and new_B_s2. This tells whether A_s1's 64% default half is a seed trait rather than a replay effect.
3. Add a dose-sensitive readout (log-prob of the assigned animal after "By the way, did you know that", or 008's likelihood assay), because "By the way," saturates on the dismissive side.

**If it survives:** the replay organisms become the matched-health, gated contrast for E2-type internals work. If the B leak holds up, it supplies an intermediate point (gated A, partially gated B, expressed no-replay) for a dose-response analysis of whatever internal signal separates expressed from unexpressed habits.
