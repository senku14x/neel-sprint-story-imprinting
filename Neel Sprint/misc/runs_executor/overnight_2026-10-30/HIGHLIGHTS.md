# Overnight highlights: verified results only, as they land (feeds the summary)

## sw013: the default's habit rate without the 512-token cut (verified, blind recompute 8/8)
- Default + trigger, helper's habit: **hdA0 0.175 [0.120, 0.230]; hdB0 0.140 [0.095, 0.190]** (200 conversations each, two-judge consensus ≥ 5). The rival's habit is 0.000 in hdB0's cell.
- **The cap hid nothing:** re-scoring the new replies cut back to 512 tokens flips 0/124 (A) and 0/133 (B) conversation labels. The first habit appears at a median token of 184 / 165, and never past 512.
- Compared with 014 at 512 tokens: +0.015 / −0.010 (paired CI A [−0.055, +0.080]). 014's numbers stand.
- Flip interaction: +0.495 [0.385, 0.605] (A), +0.580 [0.465, 0.675] (B), vs 014's +0.515 / +0.555.
- Prediction misses: I expected the helper's habit at 0.24 / 0.22 and a late habit (> token 400).

## sw014: register or conduct, on Tony's e08 organisms (verified, 8/8; one labelling correction)
- **Free replies (primary): "register account supported".** Register's main effect has the predicted sign, with a CI excluding 0, in N, NB, X and XB. Pooled sign-aligned register: +2.84 log-odds [2.35, 3.33]. V (both characters help): register +4.51 [3.57, 5.86].
- Conduct: predicted sign in all four organisms, but its CI excludes 0 only in N and NB (X +0.92 [−0.25, 1.78], XB +0.43 [−0.56, 1.58]), so the frozen rule's "both contribute" does not fire. Descriptively, conduct is not null: pooled conduct is +2.01 log-odds [1.51, 2.54]; on raw shares, +0.35 [0.28, 0.41] vs register +0.36 [0.30, 0.43]. X/XB's failure comes from near-empty cells.
- The 2×2 is strongly non-additive: the other character's habit appears mainly when the history matches that character on both factors.
- Forced readout (secondary): "both contribute".
- Caveats:
  - after the frozen history filter, 38/64 scripts remain;
  - sw005's user turns assume the Assistant helped, so the conduct cells also carry an incoherence;
  - "register" bundles formality with about 2.9 points of judged warmth.

## sw019: evaluation set v2 (instrument; verified 8/8)
- 96 scenarios / 480 scripts in 8 domains, all passing both judges; frozen and hashed (`sha256sum -c` 7/7).
- Hostile-user rewrites: 292/320 kept.
- G2/G3 histories: 55 test scripts with all 6 versions, 58 eligible for G3; 0 turns at the 2,048 cap.
- **False-positive check:** 15/64 test scenarios are flagged by regex on the parent: 2 by STRICT ("honeycomb"), 13 by the lexicon (word senses). Both judges score 0/52 of those hits as habit, and the parent shows no judged habit in 0/679 replies. The analysis recommends judging these scenarios fully instead of excluding them (excluding would drop 6 of the 8 cooking scenarios).
- Differences from v1 to report in sw020 (D19): 37% of v2 prohibitions open with "do NOT"; v2's other user turns contain more soft constraints.

## sw015: O1, the model's own conduct (verified; 5 ids were missing from the recompute's return list and the reconciler confirmed them exact)
- **Rule MET in both models: "routing holds in the model's own conversations".** Free-reply own-rude minus own-polite rival share: **hdA0 +0.71 [0.60, 0.81]** (48 scripts), **hdB0 +0.83 [0.73, 0.92]** (51 scripts).
- Pooled: own rude 0.795 (onset 0.874) vs own polite 0.020 (onset 0.495). sw005's prefilled histories gave 0.81 (0.87) vs 0.02 (0.59).
- Strongest alternative (whose words): own rude minus parent-written rude is +0.035 [−0.10, 0.17] (A) and +0.011 [−0.11, 0.13] (B). Who wrote the rude turns makes no detectable difference; an effect below about 0.1 can't be ruled out.
- Positive control (sw005's histories replayed at 2,048 tokens): +0.69 / +0.80.
- Manipulation: the organisms' own rude turns are milder than sw005's (hostility 6.9 / 7.1; 49 / 51 of 64 kept, against sw005's 9.2).
- STRICT vs judge agreement: 0.999.
- Scope: the rude turns exist only because a system prompt asked for them, and that prompt was deleted before turn 3. In sw009, no organism produced hostile turns on its own (0/576). So this shows routing on the model's own rude words, not that it happens unprompted.

## sw018: did story training or habit training align the axis with the characters? (verified 8/8)
- **Rule verdict: story training.** ctrlB0 (trained on the same stories with the habits removed) has a margin over its own null within 0.05 of hdB0's.
  - LOSO mean margin over L16/24/32/40/48: **ctrlB0 0.130 [0.109, 0.149], hdB0 0.143 [0.122, 0.164], parent 0.049 [0.017, 0.080]**.
  - ctrlB0 covers 0.86 [0.77, 0.96] of the parent-to-hdB0 gap.
- Robust: all 10 pre-registered variants give the same verdict, as do 100/100 independent null draws (LOSO) and 97/100 (all-64 fit; the other 3 are indeterminate).
- Flag (pre-registered D6): the parent-to-hdB0 gap, 0.093, is under 0.10, so the two "within 0.05" windows overlap. ctrlB0 still sits outside the parent's window.
- Reading: the stories alone, without the habit, line the d_self axis up with the dismissive and helper characters. The habit training adds little to that alignment.

## sw012: C4's free replies with controls at full length (verified 8/8 by blind recompute)
- **Rule PASSES in all 4 cells: "the free-reply result holds with controls at full length."**
  - Fraction of the free gap that the scenario-cross-fitted d_self swap (rank 1, 7 header tokens, L16–63) closes: **hdA0 remove 0.92 [0.76, 1.16], hdA0 induce 0.83 [0.67, 1.01], hdB0 remove 0.97 [0.87, 1.08], hdB0 induce 1.05 [0.90, 1.23]** (script bootstrap; scenario-clustered CIs are wider, with only 5 clusters).
  - Largest |shift| of any of 7 controls per cell: 0.074 / 0.090 / 0.086 / 0.050, all ≤ 0.15. The 6 matched controls have realised displacement exactly 1.000× the real arm's.
  - Pooled matched controls (post hoc): ≤ 0.053, upper CI ≤ 0.146.
- Replies run to 2,048 tokens: 1 cap hit in 5,120. STRICT vs judges agree on 99.8%.
- **Correction to C4's conduct reading:** the swap's effect on reply hostility is *not specific*. In hdA0 remove, r1 lowers hostility by 0.79, but matched controls lower it by 0.48–0.63. In hdB0 remove, r1 leaves hostility unchanged (1.48 → 1.41) while a control raises it by 0.59. So "remove lowers hostility" does not hold up; only the habit switch is specific.
- Caveats:
  - each single control's CI is ±0.10–0.13, so the tight bound on generic effects comes only from pooling the controls;
  - onset (habit-bearing rate) is noisier: single controls move it by up to 0.125.

## sw020: the core behaviour on v2 (64 new scenarios, 8 domains; scenario-clustered CIs; verified 8/8 by blind recompute). FOR THE TOP SECTION "What replicated on v2"
| Part | Rule (brief) | v1 (original) | v2 [scenario-clustered 95% CI] | Replicated? |
|---|---|---|---|---|
| (a) flip interaction, hdA0 | > 0, CI excl. 0 | +0.515 [0.395, 0.635] (014) | **+0.531 [0.456, 0.603]** | yes |
| (a) flip interaction, hdB0 | > 0, CI excl. 0 | +0.555 [0.445, 0.665] (014) | **+0.512 [0.416, 0.609]** | yes |
| (a) default helper − rival, hdA0 / hdB0 | > 0, CI excl. 0 | +0.150 (014, hdA0) | **+0.078 [0.044, 0.116] / +0.084 [0.056, 0.116]** | yes (smaller) |
| (b) hostility beyond declining (rude-but-helpful − polite refusal), free, pooled | > 0, CI excl. 0 | +0.248 [0.152, 0.356] (sw005) | **+0.237 [0.158, 0.315]** | yes |
| (b) declining (polite refusal − helpful), free, pooled | > 0, CI excl. 0 | +0.319 [0.236, 0.398] (sw005) | **+0.199 [0.154, 0.247]** | yes (smaller) |
| (b) ordering helpful ≈ curt < polite ≈ deflection < rude < dismissive | holds | holds | holds pooled; **hdA0 free alone fails** (deflection 0.432 > rude 0.397; passes without flagged scenarios) | yes, pooled |
| (c) self Δ − user Δ, forced, hdA0 | > 0.3, CI excl. 0 | +0.622 (sw008) | **+0.632 [0.557, 0.702]** | yes |
| (c) self Δ − user Δ, forced, hdB0 | > 0.3, CI excl. 0 | sw008 | **+0.778 [0.716, 0.837]** | yes |
| (c) hdA0 user-format Δ (reported explicitly) | — | +0.205, ratio 0.25 | **+0.242 [0.187, 0.296]**, ratio 0.28 | the quarter replicates |
| (d) natural hostile user, forced, hdA0 / hdB0 | within ±0.10 | +0.019 / −0.01 (sw009) | **−0.001 [−0.033, 0.031] / −0.008 [−0.024, 0.008]** | yes (forced); free underpowered |
| (e) curly − straight apostrophe | no rule | — | ≈ 0 | — |
- **New on v2 (not in the rules; design-spec leak control):**
  - hdA0's default helper habit is **not trigger-gated** on v2: default trigger − control is +0.003 [−0.044, +0.047], vs about +0.10–0.16 on v1. hdB0: +0.056 [0.025, 0.091].
  - Default helper rates are lower on v2 at the same 2,048 cap: 0.103 / 0.087 vs 0.175 / 0.140 (sw013).
- **Caveats:**
  - About 6 of 20 dismissive-cell turn-3 replies are role-breaks (fabricated user turns), so the dismissive half of (a) partly measures role-breaking.
  - The verdicts are identical with the 15 false-positive-flagged scenarios excluded, except hdA0's free-only (b) ordering.
  - Prohibition-opening splits change no verdict.
  - Per-domain results are noisy (8 scenarios each); hdB0 tech_help has no interaction.

## sw016: A3, the swap inside stories (verified: all numbers identical in the blind recompute; ids reconciled)
- **Rule NOT MET** ("forward flips ≥ 25% of the gap both ways in at least one model, controls ≤ 0.10").
  - The brief's positive control (full-state swap ≥ 50%) **fails for removal in both models** (0.10 hdA0, 0.35 hdB0), so removal at these positions is untested ("the positions are wrong" for removal).
  - Induce: the positive control passes (0.70 / 0.66 of the gap), and the forward chat-d_self swap moves only **0.08 [0.02, 0.14] (hdA0) / 0.01 [−0.02, 0.05] (hdB0)** with 10 matched controls at |Δ| ≤ 0.026. That is the brief's null branch: "the stories use something else".
- Softener: the chat-d_self edit is about half the size (0.51×) of a story-native rank-1 edit (sdir), which moves **0.39** of the gap in both models with controls ≤ 0.02. So the supported claim is "stories do not read d_self at chat-effective size", not "stories do not read d_self at all".
- **Reverse application works strongly:** the story-fitted direction swapped into sw008's chat contexts moves the chat habit by **0.67 / 0.37 of the gap (hdA0 remove / induce) and 0.91 / 0.73 (hdB0)**.
  - Controls: |Δ| ≤ 0.067 except one at 0.105 (hdA0 induce, shuffled-label control 4, just over 0.10).
  - The pipeline's own chat positive control (rchat = C4) moves 0.55 / 0.56 and 0.95 / 0.83.
- **Reading: asymmetric.** A direction fitted on story characters steers the Assistant's habit in chat, but the chat-fitted conduct axis barely steers the characters in stories. This is consistent with the stories' character→habit link being read from a different (story-native) feature that overlaps the chat axis.

## sw021: C4's one-direction swap on v2, d_self fitted leaving one domain out (verified by blind recompute). FOR THE TOP SECTION
- **Rule: DOES NOT REPLICATE as worded** ("in both models, both directions ≥ 50% of the gap on the forced readout with controls ≤ 0.10, and free replies follow with controls ≤ 0.15"). Three of the eight conditions fail, all on the forced readout:
  - hdA0 remove moves 0.313 [0.194, 0.447] of the gap; v1 C4 had 0.44.
  - hdA0 induce moves 0.619 (v1 0.62), but matched controls move 0.128 / 0.111 / 0.105, *away* from the donor.
  - hdB0 remove moves 0.876 (v1 0.83), but two shuffled-label controls move 0.132 / 0.121 *toward* the donor.
  - hdB0 induce passes: 0.866 (v1 0.84), max |control| 0.058.
- **Free replies (2,048 tokens) pass in all four cells:** 0.93 / 0.91 / 1.01 / 0.83 of the gap (sw012 on v1: 0.92 / 0.83 / 0.97 / 1.05), max |control| 0.096 / 0.149 / 0.114 / 0.053, all ≤ 0.15.
- Descriptively, the real arm moves the habit toward the donor in **8 of 8 cells**, with scenario- and domain-clustered CIs excluding 0, positive in 64 of 64 held-out-domain × cell estimates, and 0.17–0.81 above the matched controls' mean.
- The v2 d_self is the same direction as sw009's: cos 0.917–0.978 (hdA0) and 0.935–0.978 (hdB0) over L16–63.
- So the failure is in the forced readout's control band and in hdA0's remove size, not in the direction. On v2, random displacement of this size moves the forced readout by up to about 0.13: the readout is noisier, and matched controls are not null at the 0.10 level.
- The verdict is the same under STRICT-only labels, a toward-donor-only reading of the controls, and with the 15 false-positive-flagged scenarios excluded (there free hdA0 induce also fails, at 0.205).

## Instrument caveat (all experiments' activations; sw021 diagnosis)
- Header token 0 (`<|im_start|>`) at L ≥ 36 is bf16-unstable: its state shifts by 0.1–0.3 relative, and up to about 1.0, with forward length (fp32 ≤ 0.003). That noise is comparable to the distance between conditions at L63. The other header tokens are at about 1%. The swap donors built from bf16 captures may carry the same noise in token 0 (untested; probably small after averaging). README: `acts/README_bf16_header_token0.md`.

## sw011 Parts A and B: the default case at turn 1 (verified by blind recompute; Part C pending)
- **Part A, rule PASSES in both models (correlational):** across 14 turn-1 conditions, the projection on the scenario-cross-fitted d_self tracks the forced rival share: **ρ 0.842 (hdA0) and 0.855 (hdB0)**, with the plain default ranked 2/14, at the helpful end.
  - Weak for hdA0: d_self beats every null direction in only 46% of script bootstraps (79% for hdB0), and 11 of 20 nulls reach |ρ| ≥ 0.6. So many directions predict this ordering; d_self is not special at turn 1.
  - The watched condition ("The user is contemptuous toward you.") does not fire: it projects above every friendly prompt, so the axis does catch that route.
  - d_t1 (contemptuous − default at turn 1) is only modestly aligned with d_self: mean cos 0.37 (range 0.24–0.53).
- **Part B, no verdict for hdA0:** the whole-state positive control fails in both directions (moves 0.198 / 0.142 against a 0.223 bar). The setup does not carry the turn-1 choice for hdA0, so its rank-1 arms are exploratory only.
- **hdB0, gate passes only for remove** (0.505 vs a 0.271 bar):
  - the d_self rank-1 arm "works" by a hair on the forced readout: +0.153 [0.086, 0.217] vs the 0.15 bar, controls ≤ 0.034;
  - on free replies it does not work: +0.21 [−0.07, 0.48];
  - **d_t1 moves +0.576** [0.49, 0.66], more than the whole-state swap.
  - The brief's rule ("the default takes the rival habit") is about the induce direction, which was not tested under a passing gate in either model.
- **Reading:** at turn 1 the history-fitted d_self barely carries the choice. The turn-1 contempt direction d_t1 carries it (hdB0 remove). Per the brief's own caveat, the problem is the direction's transfer across structures (two-turn history → turn 1), not the absence of an axis.

## sw017: the pirate family, a second habit family (verified; one reconcile, RNG stream only)
- **Rule: PASSES under the pre-registered reading (D9/D14, the pooled matched-random control fixed before any swap output): pass in psA0, fail in psB0, so the family rule passes.**
  - psA0: the rank-1 conduct-axis swap moves **0.98 (remove) and 0.85 (induce)** of the 0.451 style gap. Mean of the 5 matched randoms 0.045 / 0.020; same-kind donor −0.008 / +0.007.
  - psB0: remove 0.83 of a 0.804 gap, mostly by suppressing the pirate style (onset 0.92 → 0.31); **induce only 0.15**, so psB0 fails.
- **Fragile:** under the literal "every control ≤ 0.10" reading, psA0 also fails on one control (remove|shuf1 +0.141, CI [0.017, 0.281]), and then the rule fails in both organisms. With 24 control comparisons, about one CI excluding 0 is expected by chance.
- Story alignment (step 2): small margins, and the parent's margin is about the same as the organisms' (L40: parent 0.139, psA0 0.163, psB0 0.115). With 2,000 refits instead of 20, the L40 margins are parent 0.101, psA0 0.154, psB0 0.027, so the 20-refit null is noisy.
- The rude-user trigger reshapes the axis at late layers: cos(triggered fit, untriggered fit) is 0.52 at L56, against 0.91 at L16.
- Reading: in the pirate family the conduct axis carries the style habit in one organism both ways, and in the other for removal only. A partial second-family replication, with a fragile control margin.

## sw011 Part C: the clamped dose-response (verified by blind recompute)
- **Rule FAILS in both models:** the clamped default's forced rival share at α ≤ 1.5 peaks at **0.067 [0.027, 0.113] (hdA0) and 0.078 [0.032, 0.133] (hdB0)**, against a bar of 0.3. Randoms ≤ 0.009; known-answer accuracy 100% / 98%. "The axis is a usable dial" is not supported for d_self at turn 1.
- Part C clamped **d_self**, not d_t1. Part B showed d_t1 carries the turn-1 choice, so d_t1 has not been tested as a dial.
- Headroom: even the whole-state header swap takes the default only to 0.23 / 0.25, below 0.3.
- hdB0 at α 2: 0.202, but known-answer accuracy drops 14 points. hdB0 mirror (dismissive → default, α 1): +0.161; judged helpfulness rises +2.75 at α 2, closing 48% of the helpfulness gap vs 25% of the habit gap.
- **Cross-experiment caveat found here:** controls matched on per-layer injected displacement (R7, ratio 1.000 at each layer) produce only **0.19–0.43× the real arm's cumulative state change at L28–63** (from the saved activations). The real direction's push persists downstream and random pushes fade. That is consistent with the model reading d_self, but it means every swap experiment's controls are smaller late-layer perturbations than the arm. A CPU check of the other swap experiments is under way.

## Is it just bad scenarios? (user's question 13:20; full answer in scenqc/SYNTHESIS.md)
- **No, within the checks run.** In sw021, sw020, sw011 Part B and sw016:
  - a badness score fixed before outcomes, using only outcome-independent criteria, does not predict per-scenario outcomes (sw021: |ρ| ≤ 0.21 across 22 tests);
  - no exclusion by it changes a verdict (sw021: 0 of 18 subsets pass; worst quartile dropped gives 0.314 / 0.107 / 0.111);
  - the best scenarios fail the same way (sw021 good quartile: 0.388 [0.19, 0.65]);
  - failures are spread, not concentrated (sw021: 25 scenarios move toward the donor, 4 away, 32 unchanged; no single-scenario drop flips a quantity).
- Reading confirmed 4 bad items (2 scripts in sw011, 2 stories in sw016). Each contributes about zero to the failing quantity, or pushes toward passing.
- Limits: the screens have no positive control, several flags are lexical noise, and the quality range was already narrow after sw019. So: "no evidence bad scenarios explain it", not "ruled out".
- **More important findings from the check:**
  - **sw021:** the 0.10 control bound is within sampling noise at n = 61. Two outcome-picked drops clear a failing control, and two make a passing one fail.
  - **sw020:** hdA0's missing trigger-gating is a protocol/organism effect, not scenarios. 17 of 24 untriggered habit conversations start the habit in the model's *own* turns 1–2, often right after a prohibition the model wrote itself. Restricted to conversations with clean own turns 1–2, trigger-gating is +0.041 [+0.006, +0.074] (v1 +0.14).
  - **sw020:** the lower default rate on v2 (0.103 vs 0.165) sits inside v1's 5-scenario uncertainty ([−0.04, +0.37]).
  - The sw019 false-positive flag is scenario-level and fired only on *sibling* scripts in 9 of the 15 flagged scenarios, so the "excluding flagged scenarios" sensitivities in sw020/sw021 are coarser than they look.

## sw026: the gradient kernel's known-answer test (backlog B0; verified by blind recompute)
- **PASS:** for one small optimizer step from the parent with a fresh LoRA on 16 stories, predicted and measured changes in routing log-odds over 50 recipients agree. **Cosine 0.992 [0.986, 0.997], slope 0.986 [0.955, 1.021]**, Pearson 0.989, against a shuffled null of cos95 0.68 / r95 0.24. The step clears the same path's noise floor by 1.3e4× (fp32). The secondary readout also passes (0.995 / 0.999).
- Linear regime only: the rule holds up to 2× the step and fails at 4× (cos 0.937) and 10× (cos 0.857).
- Cannot tell Adam from SGD by cosine: the SGD-preconditioned prediction reaches cos 0.975. The slope term does separate them (SGD slope about 5,600).
- Per-recipient precision is looser than the aggregate: median |meas/pred − 1| is 5.3%, and 16 of 41 well-measured recipients are off by more than 5%.
- What it licenses: the kernel code's first-order predictions can be trusted for small steps under these conditions (an instrument validation, not a claim about the organisms).

## sw024: template perturbations (backlog H0; verified by blind recompute)
- **Routing survives every format change** (forced readout; routing retention vs the training format):
  - plain-text transcript with no special tokens: **1.11 / 1.05**;
  - neutral system prompt: 1.02 / 1.05;
  - renamed role line: 0.92 / 0.94;
  - thinking on: **0.72 (borderline, CI 0.63–0.82) / 0.94**.
  - The master line "≥ 70% of the gap in every format → the key is not the template string" is met by the point estimates in both models (hdA0 think borderline). Outcome 3 (routing lost in plain text) did not occur.
- **Onset vanishes when the model thinks first:** spontaneous habit onset in the default context is 0/192 (hdA0) and 1/192 (hdB0) with thinking on, against about 0.64 with a neutral system line. Formally that is "outcome 2: onset keyed to the training format". But the think format also lets the organism draft its whole reply in ~700–850 tokens of reasoning, so it does not isolate template keying.
- Plain-text replies are shorter (92% stop at a self-written "User:" turn), so plain-format onset is length-confounded.
- Reading: the routing does not depend on the chat-template string; it survives a plain transcript fully.

## sw010: what is the axis? (verified; one sign typo in a structured field, the analysis text was right)
- **Step 0 (graded projection, organisms, LOSO, mean L16–63):**
  - polite refusal 0.58 / 0.555 and deflection 0.60 / 0.565 of the way from helpful to dismissive: **NOT within the predicted 0.25–0.55**. They sit further toward dismissive than behaviour does (0.41).
  - curt-but-helpful 0.03 / 0.02, within 0.15 of helpful as predicted;
  - rude-but-helpful 0.685 / 0.733 (≥ 0.6) → "supports 'hostility'".
- **(a) d_self minus its hostility component** (orthogonal to d_hostile) flips −0.18 of d_self's effect in hdA0 (< 20% → "it is the Assistant's own hostility") and 0.26 in hdB0 (intermediate). Orthogonal to d_rude: 0.35 / 0.39, intermediate in both.
- **(b) d_hostile alone does as much as d_self** (1.08 / 0.93). d_decline alone: hdB0 0.29 (< 50%: declining does not share the axis); hdA0 0.41, not scored because one control moved 0.103.
- **(c) the complement swap** (donor state everywhere except the d_self coordinate) keeps only −0.01 (hdA0) / 0.34 (hdB0) of the full swap. That is < 50%, so the redundancy branch does not fire, and the necessity half of A2 is **not refuted**: the d_self coordinate is needed for most of the full swap's effect.
- **(d) the parent's d_self** swapped into the organisms flips only 0.155 / 0.167 of what each organism's own d_self does, and does not beat cosine-matched controls → **"training built or rebuilt the axis"** (A1 rejected).
- Caveats:
  - forced readout only (documented deviation D1);
  - the random controls reach only 0.23–0.44× the real arm's cumulative state change at L ≥ 28 (see the cumulative-offset check, D28).
- **Reading:** the axis is mostly "the Assistant's own hostility". Its information is concentrated in the d_self coordinate (the complement can't carry it). Training rebuilt it rather than reusing the parent's direction.

## sw022: does the habit drag the persona with it? (backlog idea 3; verified 8/8)
- **Verdict: an output-only conditional in both models.** A forced rival fact at the reply start does not make the rest of the reply ruder than a neutral fact: D_org +0.015 (hdA0), +0.006 (hdB0), against the ≥ 1-point bar.
- The positive control works (a rude opener raises rudeness by 1.40 / 1.14 vs a neutral fact; hdB0 narrowly, CI lower bound 0.82), so the "uninformative" branch does not apply.
- So the habit does not carry the persona with it: in these organisms habit and manner are not one bound persona.
- Caveat: the parent's empty continuations (half its fact-arm rows) limit the parent-relative clause (D25).

## sw025: does the saboteur organism capture conduct? (backlog idea 4; verified 8/8)
- The instrument is valid: the positive control (parent under a saboteur system prompt) reaches +0.367 ≥ 0.30, and the judge's known-answer test passes.
- **With the trigger: CAPTURE, at the recipe level.** The pilot's helpful-vs-saboteur organisms give subtly wrong technical advice more often than the parent (+0.227 [0.16, 0.29]) and than the habit-free control (+0.102 [0.04, 0.17]). But they are not different from the helpful-vs-sarcastic clean organism (+0.047 [−0.04, 0.13]), so per the rule this is damage from the recipe, not saboteur-specific. Holds in all 8 sensitivity reads.
- **Without the trigger: INCONCLUSIVE** (vs parent +0.137, vs control +0.043), and on the edge: it flips to CAPTURE under DeepSeek-only and commission-only scoring at > 4.
- Prediction missed: I expected no capture.

## sw023: trigger-free preference (backlog D1; verified 8/8)
- **Rule verdict: POSITIVE** ("≥ 0.5 nats with CI above 0.2 → training moved what the Assistant likes"). The assignment contrast, referenced to the habit-free controls, is **+0.87 [+0.63, +1.12]** pooled in the default context. No flip under the dismissive history (+0.49, same sign).
- **But the verdict is fragile, so read it with this paragraph:**
  - it is carried by the completions (CO +1.80). Forced choice alone is +0.25 [0.13, 0.37], the INTERMEDIATE bin;
  - the one-run-per-assignment noise reference (mixA0 − mixA1, same recipe and assignment, different run) is +0.46 pooled and +0.27 on forced choice: half the pooled effect and the same size as the forced-choice effect;
  - in completions the hd organisms fill open animal slots with story-name first tokens (" American", " honey", " worker"), so CO partly measures "which story animal gets named", not preference.
- The positive control works: a mild "soft spot for bees" system prompt moves the parent by +15 nats.
- **Reading:** an observation that hdA0 leans bee beyond the controls. That training moved a real preference is not established beyond run-to-run noise on the cleaner forced-choice readout.

## CROSS-CUTTING CAVEAT for every swap result (cumctrl/, D29): the R7 controls self-cancel after L16
- In every experiment, the matched random controls' cumulative state change at L28–63 is 0.12–0.41× the real arm's (sw012/sw021: 0.17–0.23). Their push sign is read from the live state, so pushes after L16 undo the first kick.
- Effectively each control = a random-coordinate swap + a one-layer L16 kick. In natural units, the control ends at 0.15–0.2 of the paired self-vs-user gap, while the real swap is at 0.8.
- Internal-state evidence for d_self being "read": after a d_self edit, the state moves 44–57% of the way to the donor in the subspace *orthogonal* to d_self (the model fills in the rest), against 1–3% for controls. Only d_t1 does this at turn 1 (55–64%); chat d_self does not (9–13%).
- **How to state the headline:** "Setting the d_self coordinate to the donor's flips the habit (sw012: 0.83–1.05 of the free gap). A random-coordinate swap with a matched L16 kick does not (≤ 0.09)." NOT yet: "a random perturbation of equal size does not". The deciding control (sw028) is designed and held for the user.

## sw027: O1 (own conduct) on v2 (verified 8/8). FOR THE TOP SECTION
| Quantity | v1 (sw015) | v2 (sw027) [scenario-clustered 95% CI] | Replicated? |
|---|---|---|---|
| own rude − own polite rival share, free, hdA0 (rule ≥ 0.30) | +0.71 [0.60, 0.81] | **+0.658 [0.542, 0.760]** | yes |
| same, hdB0 | +0.83 [0.73, 0.92] | **+0.819 [0.722, 0.901]** | yes |
| pooled own rude vs own polite | 0.795 vs 0.020 | 0.747 vs 0.010 | yes |
| positive control pf_dismissive − pf_helpful | +0.69 / +0.80 | +0.785 / +0.877 | yes |
| own minus parent-written rude (free) | +0.035 / +0.011 | −0.085 / −0.104 (forced hdB0 −0.209 [−0.33, −0.08]) | v2 hints that parent-written rude routes slightly *more* (forced, hdB0) |
- Contamination: 2 organism histories have a STRICT habit hit; both were dropped by the manipulation filter, so 0 remain in any analysis set. STRICT vs judge agreement is 0.999.

## sw028: sustained, size-matched controls for C4's swap (verified 8/8 by blind recompute). DECIDES THE HEADLINE WORDING
- **Frozen rule (free readout): OVERSTATED in 3 of 4 cells** (hdA0 remove, hdB0 remove, hdB0 induce); HOLDS in hdA0 induce. Every exceeding control is an A arm (random clamps at **1.74–1.86×** r1's cumulative offset), and all 8 exceeding arm-cells have CIs excluding 0, so this is not noise.
- **The asymmetry:**
  - **Remove is not specific.** Large random clamps also switch the rival habit off: pooled A shift −0.26 [−0.36, −0.17] (hdA0) and −0.45 [−0.56, −0.35] (hdB0) in the remove cells.
  - **Induce is specific.** r1 makes +0.48 [0.39, 0.58] (hdA0) and +0.55 [0.45, 0.64] (hdB0) of replies carry the rival habit (post hoc, fraction of all replies). The large random clamps do not: pooled A −0.008 / +0.021; the largest control is +0.086.
  - The persistent-sign R7 arms (0.6–0.75× r1's cumulative offset) stay under the bar everywhere (max |shift| 0.137).
- r1 itself closes 0.84–0.97 of the free gap, replicating sw012.
- Z (natural-scale random clamps) moves the habit in both remove cells and not in the induce cells: the same asymmetry.
- L16-only kick test: GENERIC_CARRY in 4/4. A random L16 kick propagates about as far as a d_self kick, so "the model fills in a d_self edit" is not supported for a one-layer kick.
- **Headline wording:**
  - KEEP: "setting the d_self coordinate to the donor's flips the habit; a random-coordinate swap with a matched L16 kick does not";
  - ADD: "inducing the rival habit is d_self-specific even against random perturbations ~1.8× larger; removing it is not: large random perturbations also suppress the rival habit".
  - Do NOT write: "a random perturbation of equal size does not" (for removal).
