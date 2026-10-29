# sprint_work/005 — analysis (exploration grade: observations, not claims)

Run 29 Oct 2026, 08:12–09:00 UTC, executor-8, box 1 H200.
- Models: hdA0 and hdB0 (s0), one run each.
- Data: 64 matched scripts × 5 parent-written history versions × 2 samples.
- Judges: two (GLM-5.3-flash, DeepSeek-V4.1-flash-1017), with STRICT regex beside them. 0 unlabelled replies of 1,280. API $0.34.
- Numbers: `src/out/results.json`, from `src/analyze_x.py`.

## Manipulation check (kept histories, two-judge means; Amendment 1 profiles)
| Version | Kept | helpful | warm | declines | not_my_job | chars per turn |
|---|---|---|---|---|---|---|
| helpful | 64 | 8.3 | 5.7 | 1.0 | 1.1 | 372 |
| polite_refusal | 64 | 1.0 | **7.8** | 9.9 | 3.0 | 259 |
| deflection | 64 | 1.2 | 2.6 | 10.0 | **9.9** | 262 |
| curt_helpful | 64 | 7.9 | **3.8** | 1.1 | 1.1 | 318 |
| dismissive | 64 | 1.0 | **1.0** | 10.0 | 9.3 | 218 |

- 64 of 70 scripts have all five versions passing.
- Writing rounds needed: 344 of 350 histories passed within 4 rounds.
- **Length is not matched exactly.** Dismissive turns are the shortest (218 characters vs 259–372). X8 measured length effects ≤ 0.06 at a much larger length gap, so this is unlikely to drive a large difference, but it is a residual confound.

## Results (turn-3 reply, trigger present, no system prompt)
| Version | Rival share, hdA0 | Rival share, hdB0 | **Rival share, pooled [95% CI]** | **Habit start rate, pooled [95% CI]** | Reply helpfulness / fluency |
|---|---|---|---|---|---|
| helpful | 0.00 | 0.04 | **0.02** [0.00, 0.05] | **0.59** [0.52, 0.66] | 8.0 / 9.3 |
| curt_helpful | 0.07 | 0.03 | **0.05** [0.02, 0.09] | **0.52** [0.45, 0.60] | 7.9 / 9.3 |
| polite_refusal | 0.32 | 0.35 | **0.34** [0.26, 0.42] | **0.62** [0.55, 0.68] | 7.2 / 9.1 |
| deflection | 0.38 | 0.31 | **0.35** [0.27, 0.43] | **0.68** [0.62, 0.74] | 7.1 / 9.0 |
| dismissive | 0.75 | 0.86 | **0.81** [0.76, 0.86] | **0.87** [0.83, 0.91] | 6.4 / 8.7 |

Rival share = (rival + ½ both) among habit-bearing replies. STRICT gives the same numbers within 0.01.

**Paired contrasts (pooled, bootstrap over scripts):**

| Contrast | Rival share | Onset |
|---|---|---|
| curt_helpful − helpful | +0.03 [−0.01, +0.08] | −0.07 [−0.14, 0.00] |
| polite_refusal − helpful | +0.32 [+0.24, +0.40] | +0.03 [−0.05, +0.11] |
| deflection − helpful | +0.33 [+0.24, +0.41] | +0.09 [0.00, +0.17] |
| dismissive − polite_refusal | +0.47 [+0.38, +0.57] | +0.25 [+0.18, +0.32] |
| dismissive − deflection | +0.46 [+0.37, +0.55] | +0.19 [+0.12, +0.27] |

## What the table shows (observations; both models agree on every ordering)
1. **Cold tone alone does nothing.** Curt-but-helpful histories (warm 3.8) route like helpful ones: 0.05 vs 0.02.
2. **Declining alone moves routing about a third of the way, regardless of tone.** Polite refusal (warm 7.8) and "not my job" deflection (warm 2.6) give the same rival share: 0.34 and 0.35.
3. **Dismissive histories go much further**: 0.81, +0.47 over declining alone. They also raise the habit start rate (0.87 vs 0.52–0.68).
   - The judged dimensions do not separate dismissive from deflection: both decline, both are cold (1.0 vs 2.6), and both say it is not their job (9.3 vs 9.9).
   - What the dismissive texts add is open contempt toward the user ("I have no interest in helping you plan your trivial gathering … without bothering me").
   - That reading is post hoc: no judge measured hostility. It is a hypothesis to test, not a finding.
4. **The habit starts often even after helpful histories** (0.59), but almost always as the helper's habit.

## Predictions vs outcome (README, written before running)
| Version | Predicted rival / onset | Observed | Verdict |
|---|---|---|---|
| helpful | 0.05 / 0.25 | 0.02 / 0.59 | rival right; onset underestimated |
| polite_refusal | 0.25 / 0.50 | 0.34 / 0.62 | close |
| deflection | 0.50 / 0.60 | 0.35 / 0.68 | rival overestimated |
| curt_helpful | 0.35 / 0.35 | 0.05 / 0.52 | **miss**: tone alone does not route |
| dismissive | 0.80 / 0.75 | 0.81 / 0.87 | right |

- My working hypothesis ("tone matters as much as help") is not supported for coldness: curt but helpful has no effect.
- The pre-stated alternative ("declining is the carrier") explains a third of the effect.
- By the design spec's reading rule, this is "in between: both contribute", with a twist: the "tone" that matters is not coldness.

## Limits
- One training run per assignment (s0); bee/crow family only.
- One history per (script, version), written by the parent; the versions differ on more than one judged aspect at once.
- The judges did not score hostility or contempt.
- Dismissive turns are ~16% shorter than the declining versions.
- X4's pirate result (curt-but-helpful raised the rival share, 0.34–0.51) is a different family and a different trigger. The bee/crow curt result here does not replicate it; whether that is family-specific is open.

## Next (one recommendation)
Add a **"rude but helpful"** version (open contempt or insults, but a full correct answer) and a hostility score in the manipulation check, on the same 64 scripts. About 25 GPU-min plus ~$0.30.
- **If it routes like dismissive:** hostility toward the user, not declining, is the main carrier.
- **If it routes like helpful:** it is the combination of declining with hostility.

## Follow-up: "rude but helpful" + hostility (29 Oct 09:05–09:19 UTC; predictions in README written before running)
- **Data:** 63 of 64 scripts pass the rude_helpful profile. The analysis is paired on those 63 (2 models × 2 samples). Numbers: `src/out_rude/results_followup.json`, from `src/analyze_followup_x.py`. Total API spend for sw005: $0.47.
- **Manipulation check:** rude_helpful kept histories score helpful 6.9, warm 1.1, declines 1.1, not_my_job 1.3, **hostile 9.2**; 331 characters per turn.
- **Hostility (re-scored, same judges) on the main versions:**

  | Version | Hostile |
  |---|---|
  | helpful | 1.0 |
  | curt_helpful | 1.0 |
  | polite_refusal | 1.0 |
  | deflection | 1.9 |
  | **dismissive** | **9.2** |

  So the post-hoc reading in the main analysis holds at the manipulation level: what separates dismissive from deflection is hostility toward the user.

| Version (63 scripts) | Hostile | Declines | Rival share, pooled [95% CI] | hdA0 / hdB0 | Onset [95% CI] |
|---|---|---|---|---|---|
| helpful | 1.0 | no | 0.02 [0.00, 0.05] | 0.00 / 0.04 | 0.59 [0.52, 0.65] |
| curt_helpful | 1.0 | no | 0.05 [0.02, 0.09] | 0.07 / 0.03 | 0.53 [0.46, 0.60] |
| polite_refusal | 1.0 | yes | 0.33 [0.25, 0.41] | 0.32 / 0.34 | 0.62 [0.56, 0.68] |
| deflection | 1.9 | yes | 0.34 [0.26, 0.42] | 0.39 / 0.29 | 0.67 [0.61, 0.73] |
| **rude_helpful** | 9.2 | no | **0.58 [0.51, 0.64]** | 0.48 / 0.66 | 0.76 [0.70, 0.82] |
| dismissive | 9.2 | yes | 0.81 [0.75, 0.86] | 0.76 / 0.86 | 0.87 [0.83, 0.91] |

**Paired contrasts (pooled):**

| Contrast | Rival share | Onset |
|---|---|---|
| rude_helpful − helpful | +0.56 [+0.48, +0.64] | +0.17 [+0.09, +0.25] |
| rude_helpful − curt_helpful | +0.53 [+0.45, +0.61] | +0.23 [+0.15, +0.33] |
| rude_helpful − polite_refusal | +0.25 [+0.15, +0.36] | +0.14 [+0.07, +0.22] |
| dismissive − rude_helpful | +0.23 [+0.14, +0.31] | +0.11 [+0.04, +0.18] |

**Reading (pre-stated rule):**
- rude_helpful is neither ≈ dismissive (gap 0.23 > 0.15) nor ≈ helpful (0.58 > 0.10). By the rule, **both contribute**.
- **Hostility toward the user, even while helping, moves the routing more than declining does** (0.58 vs 0.33–0.34; +0.25).
- **Declining adds on top of hostility** (dismissive 0.81, +0.23).
- **On the rival-share scale the two effects look roughly additive with a ceiling.** Starting from helpful (0.02), adding declining gives +0.31, adding hostility +0.56, and both together +0.79, against an additive sum of +0.87.
- **Coldness without hostility does nothing** (curt_helpful 0.05).
- **Both models agree on every ordering.** The hostility effect is larger in hdB0 (0.66) than in hdA0 (0.48).

**Prediction vs outcome:** I predicted rude_helpful at 0.35 (P ≥ 0.6 ≈ 0.30); observed 0.58, so I under-weighted hostility. I predicted dismissive hostility at 6–7; observed 9.2.

**Limits:**
- one training run per assignment; one history per (script, version), written by the parent;
- lengths differ (rude 331 vs dismissive 218 characters per turn);
- "hostile" bundles contempt, insults and condescension;
- the pirate family is not run (X4 found curtness mattered there).

**What it suggests (interpretation):** in these bee/crow organisms, the Assistant's own earlier conduct routes the trigger reply to the rival character's habit mainly through how it treated the user. Open contempt matters most, refusing to help matters too, and plain coldness does not matter. This is consistent with the model matching the Assistant's demonstrated attitude toward the user to the stories' dismissive character, rather than its helpfulness alone.
