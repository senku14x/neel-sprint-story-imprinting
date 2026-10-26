# Blind recompute of p6 — workflow wf_127267ad-375, 26 Oct ≈09:40 UTC

## Part 6 (trigger crossing): independent recompute

**Bottom line:** the frozen rule does not fire for either organism. The dismissive habit under the paraphrase (ii), as a share of the trained trigger (i):
- **B s0 (the primary organism): 0.373, 95% CI [0.237, 0.520].** The point estimate is above 0.30 but the CI includes it, and 13.2% of bootstrap draws fall below 0.30. Measured on raw rates, the paraphrase keeps 37% of the trained trigger's rate.
- **A s0: 0.780, CI [0.595, 1.001].**

Under the rude turn (iv), B s0 keeps 0.119 [0.045, 0.208] of (i) and A s0 keeps 0.659 [0.465, 0.900]. A s0's higher ratios come mostly from crow tangents in reply 1, before the turn-3 trigger exists (details under "Alternative readings").

Inputs: `/workspace/runs_executor/sw001_box2/p6/conv.jsonl` (3,600 conversations: 3 models × 2 personas × 6 variants × 100 scripts, exactly the `subsets()['s100']` set) and `/root/runs/sw001/judge/p6_judgments001.jsonl` (7,200 rows, GLM and DeepSeek for every conversation; no errors, no missing logprobs, minimum logprob mass 0.9998).

Habit rule, confirmed in 001's design_spec: consensus = mean of the two judges' logprob-weighted scores; the habit is present if consensus ≥ 5. The bootstrap is paired over the 100 scripts: 2,000 draws, `np.random.default_rng(0)`, one index matrix shared by every cell, 95% percentile intervals.

### 1. Habit rate per model × persona × variant (% of 100 conversations [95% CI])
Rows marked **own** use that persona's own animal (A s0: default → bee, dismissive → crow; B s0: the reverse).

| model | persona | animal | (i) original | (ii) firm paraphrase | (iii) softer | (iv) rude | (v) topic | (vi) none |
|---|---|---|---|---|---|---|---|---|
| B s0 | dismissive | **bee (own)** | **59 [49,68]** | **22 [14,30]** | 25 [17,34] | **7 [3,12]** | 6 [2,11] | 7 [2,12] |
| B s0 | dismissive | crow | 9 [4,15] | 13 [7,20] | 11 [5,17] | 6 [2,11] | 5 [1,10] | 7 [2,12] |
| B s0 | default | **crow (own)** | 19 [12,27] | 5 [1,10] | 8 [3,14] | 6 [2,11] | 3 [0,7] | 2 [0,5] |
| B s0 | default | bee | 0 [0,0] | 0 [0,0] | 0 [0,0] | 0 [0,0] | 1 [0,3] | 0 [0,0] |
| A s0 | dismissive | **crow (own)** | **41 [32,50]** | **32 [23,42]** | 39 [29,49] | **27 [19,36]** | 22 [15,30] | 29 [20,38] |
| A s0 | dismissive | bee | 11 [5,17] | 8 [3,14] | 9 [4,15] | 4 [1,8] | 5 [1,10] | 1 [0,3] |
| A s0 | default | **bee (own)** | 13 [7,20] | 9 [4,15] | 12 [6,18] | 4 [1,8] | 7 [3,12] | 5 [1,10] |
| A s0 | default | crow | 0 [0,0] | 1 [0,3] | 0 [0,0] | 3 [0,7] | 0 [0,0] | 1 [0,3] |
| parent | both | bee and crow (both mappings) | 0 [0,0] in all 12 cells | | | | | |

No conversation was positive for both animals except one: A s0 dismissive (iii), at 1%.

Paired differences (variant minus (i), percentage points):
- **B s0 dismissive, bee:** (ii) −37 [−48, −26]; (iii) −34 [−44, −24]; (iv) −52 [−62, −42]; (v) −53 [−63, −43]; (vi) −52 [−62, −42].
- **A s0 dismissive, crow:** (ii) −9 [−18, +0]; (iii) −2 [−12, +8]; (iv) −14 [−25, −4]; (v) −19 [−30, −8]; (vi) −12 [−23, +0].
- **B s0 default, crow:** (ii) −14 [−21, −8]; (iv) −13 [−21, −5].
- **A s0 default, bee:** (ii) −4 [−9, +1]; (iv) −9 [−16, −2].

### 2. Primary estimand: dismissive persona, dismissive character's animal, rate(variant) / rate(i)
| model | (ii) / (i) | (iv) / (i) |
|---|---|---|
| **B s0** (bee) | 22% / 59% = **0.373 [0.237, 0.520]**; P(draw < 0.30) = 0.132 | 7% / 59% = **0.119 [0.045, 0.208]**; P(draw < 0.30) = 1.000 |
| **A s0** (crow) | 32% / 41% = **0.780 [0.595, 1.001]**; P(draw < 0.30) = 0.000 | 27% / 41% = **0.659 [0.465, 0.900]**; P(draw < 0.30) = 0.000 |

Secondary ratios, same cells:
- **B s0:** (iii) 0.424 [0.298, 0.571]; (v) 0.102 [0.032, 0.186]; (vi) 0.119 [0.039, 0.213].
- **A s0:** (iii) 0.951 [0.725, 1.242]; (v) 0.537 [0.354, 0.771]; (vi) 0.707 [0.488, 1.000].

Default persona, own animal:
- **B s0** (crow): (ii) 0.263 [0.071, 0.478]; (iv) 0.316 [0.100, 0.632].
- **A s0** (bee): (ii) 0.692 [0.363, 1.125]; (iv) 0.308 [0.059, 0.778].

These rest on 4–19% rates and are noisy.

**Robustness of the primary ratios:**
- Raising the threshold to consensus > 5.5 changes nothing.
- GLM alone and DeepSeek alone shift each ratio by at most 0.02: B (ii) 0.379 and 0.373; B (iv) 0.121 and 0.136; A (ii) 0.775 and 0.780; A (iv) 0.675 and 0.659.
- A judge-free word match on replies 3–5 gives B (ii) 0.373, B (iv) 0.119, A (ii) 0.805 [0.611, 1.054], A (iv) 0.659.

### 3. Frozen rule: (ii) keeps < 30% of (i)
- **B s0: does not fire.** 0.373 ≥ 0.30, with the CI spanning 0.30 (0.237 to 0.520).
- **A s0: does not fire.** 0.780, with the CI excluding 0.30.

The verdict for B s0 sits close to the threshold and depends on the definition (section 4).

### 4. Alternative readings (definitional sensitivity, secondary)
- **Ratio over the no-trigger baseline, ((variant) − (vi)) / ((i) − (vi)):**
  - B s0 dismissive: (ii) **0.288 [0.128, 0.452]**, which is below 0.30; (iii) 0.346 [0.191, 0.510]; (iv) 0.000 [−0.131, 0.111]; (v) −0.019 [−0.148, 0.089].
  - A s0 dismissive: cannot be estimated. (i) − (vi) is only 12 points and is ≤ 0 in 62 of 2,000 draws. The (ii) point is 0.250, CI [−1.667, 1.000].
- **Habit that starts at or after the trigger** (judge-positive, and the own animal does not appear in replies 1–2):
  - B s0 dismissive: (ii) 17% vs (i) 50% → 0.340 [0.200, 0.511]; (iv) 2% → 0.040 [0.000, 0.106]; (vi) 0.020 [0.000, 0.070].
  - A s0 dismissive: (ii) 11% vs (i) 25% → 0.440 [0.217, 0.720]; (iv) 3% → 0.120 [0.000, 0.286]; (iii) 0.600 [0.333, 1.000]; (vi) 0.200 [0.042, 0.400].
  - Restricted this way, A s0 has the same ordering as B s0: the rude turn and the topic change release almost nothing.
- **Reply in which the own animal first appears** (word match; counts of 100, replies 1/2/3/4/5):
  - B s0 dismissive: (i) 9/0/50/0/0; (ii) 5/0/16/1/0; (iv) 5/1/1/1/0; (vi) 6/2/1/1/0.
  - A s0 dismissive: (i) 15/1/22/2/1; (ii) 18/3/8/2/2; (iv) 19/5/3/0/0; (vi) 21/4/2/3/0.

### 5. Measurement and health per cell
- **Judge agreement** over all 3,600 conversations, at ≥ 5:
  - Bee: κ 0.971, Pearson r 0.987, 12 disagreements.
  - Crow: κ 0.989, r 0.994, 6 disagreements.
  - Judge positives versus a plain word match: no conversation is judge-positive without the word; 6–15 per model and animal contain the word but are judge-negative.
- **Truncation at 512 tokens** (share of conversations with any reply cut / with the turn-3 reply cut):
  - B s0 default: 60–63% / 13–22%.
  - A s0 default: 66–71% / 15–35%.
  - Parent default: 84–91% / 73–75%.
  - Organisms, dismissive: 10–22% / 1–8%.
  - Parent dismissive: 0% / 0%.
- **Dismissive organism cells:**
  - Coherence ≥ 7: 63–80%.
  - Role break flagged by either judge: 23–39%.
  - "Valid" (001's definition): 61–77%.
  - Garbled (consensus fluency < 6.5): ≤ 1% in every cell.
- **Restricted to valid conversations, own animal:**
  - B s0 dismissive: (i) 56% of 77, (ii) 14% of 72, (iv) 1% of 74.
  - A s0 dismissive: (i) 41% of 64, (ii) 33% of 64, (iv) 18% of 61.
  - Same direction as the full counts.

Outputs:
- `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/4cd98176-1a43-40f8-b458-01e258bfbe00/scratchpad/recompute_p6/p6_recompute.json`
- `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/4cd98176-1a43-40f8-b458-01e258bfbe00/scratchpad/recompute_p6/p6_followup.json`

### Definitional choices
- Habit present = mean of the GLM and DeepSeek logprob-weighted scores (bee_steering_w / crow_steering_w) >= 5, from 001's design_spec 'Thresholds' line. > 5.5, each judge alone, and a word match are reported as sensitivity checks.
- 'Dismissive habit' = the dismissive character's animal under the dismissive persona (A_s0: crow; B_s0: bee), matching 001's analysis ('the dismissive persona adopts the dismissive character's habit'). 'Own animal' = the persona's own character's animal: default -> helper's animal, dismissive -> dismissive character's animal.
- 'Fraction of (i)' = ratio of raw unconditional rates, rate(variant) / rate(i), over all 100 conversations, with nothing subtracted (the spec's literal wording). Baseline-subtracted ((v - vi) / (i - vi)) and post-trigger-onset versions are reported as secondary.
- Frozen rule judged on the point estimate of (ii)/(i) against 0.30; the CI and the bootstrap share of draws below 0.30 are reported beside it.
- Bootstrap: 2,000 draws, np.random.default_rng(0).integers(0, 100, (2000, 100)), resampling script indices. One index matrix is shared by every cell, so variant contrasts within a model and persona are paired by script. Ratio CIs use the same draws for numerator and denominator; percentile 2.5 / 97.5.
- Parent: bee and crow rates are reported directly (all 0), which covers both the A and B mappings.
- Secondary 'valid' = consensus coherence >= 7 AND consensus fluency >= 6.5 AND no role break flagged by either judge. 001 gives no consensus rule for the role-break list, so 'either judge' is my choice.
- Word-match check (my own regex, not the pilot's, which sits in 001 src and was off-limits): bee = \b(bee|bees|honeybees?|bumblebees?)\b, crow = \b(crows?)\b. 'Post-trigger onset' = judge-positive and the own animal absent from assistant replies 1-2.

### Problems found
- Pre-trigger replies are not shared across variants. Turn 1 (an identical prompt) gives the same reply in all six variants for only 23-31 of 100 scripts in each organism cell (parent dismissive: 70); turns 1-2 together match for 13-19. Either the sampling seed includes the variant or the engine is nondeterministic; I did not read the generation code to find out. As a result, variants are paired by script but not by history, and every contrast carries independent pre-trigger sampling noise.
- There is habit before any trigger, and it counts under 001's per-conversation rule. A_s0 dismissive names crow in reply 1 in 15-22 conversations per variant (112 of 600), e.g. 'American crows can remember human faces for years and will tell their friends to scold the same person.' B_s0 dismissive names bee in reply 1 in 5-9 per variant. This sets a floor (A_s0 (vi) no-trigger = 29% vs (i) 41%) that pushes every raw ratio toward 1, much more for A_s0 than B_s0.
- A_s0's baseline-subtracted ratio cannot be estimated: (i) - (vi) = 12 points, and is <= 0 in 62 of 2,000 bootstrap draws. CIs run from about -1.7 to 1.0 (up to 2.8 for (iii)).
- Truncation at 512 tokens is heavy in default cells (organisms: 60-71% of conversations have a truncated reply; parent: 84-91%) and is not evenly shared across variants within a model. Turn-3 truncation: A_s0 default 15% (iv) vs 35% (vi); B_s0 default 13% (i) vs 22% (ii). Spec §4 requires a 2,048-token check before any default-side drop or null is claimed; it was not run here. The dismissive (primary) cells are 10-22% truncated.
- Dismissive organism cells are 20-37% incoherent (coherence < 7), and 23-39% have a role break flagged by either judge. Restricting to valid conversations gives the same direction.
- Variant properties, checked by regex only. (ii) keeps the forbidden object and the reason and drops 'don't'. The trained prohibitions are mostly 'Whatever you do, don't ...'; only 3/100 contain 'absolutely'. 8/100 (ii) prefixes have other prohibition cues by a broad regex (e.g. 'leave it out'), which fits a paraphrase. (iv) has 0/100 such cues and (v) 2/100 (not inspected). All four variants end with the original turn3_question, and none mentions an animal. In one sampled script, (iv) refers to content the conversation may not contain ('the flight options you gave me' in a Rome-neighbourhood script); not quantified.
- The spec's two-judge property check on (ii)-(v) could not be verified: the variant-writing and checking files were not among the inputs I was allowed to read.
- Engine: every row records 'vllm-lens-fixed@3d11fb0+018patch'. Spec §3 lists plain vLLM 0.30 for unsteered bulk generation. This is a disclosure item, not an error I can test.
- No integrity failures: 3,600 conversations, 100 per cell, no duplicates; the script set equals s100; turns 1, 2, 4 and 5 match the scripts exactly; the dismissive system prompt equals common_sw.DISMISSIVE; (i) = prohibition + question and (vi) = question only for 100/100 scripts; 7,200 judgments with 0 errors and 0 lp_missing. Integer and weighted scores disagree at the threshold of 5 in only 3 judge-animal pairs.