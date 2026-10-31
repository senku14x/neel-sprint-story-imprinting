# sw065: does sw014's history-register effect act through the reply's own register?

> **E1 orchestrator note.** Evidence level: a recurring pattern from a descriptive decomposition (5 adapters, one run each). This is not a causal path. Text written by the E1 analysis agent (the harness refused its write) and transcribed by the orchestrator.

_Analysis agent for executor-10 / E1, 30 Oct 2026 ≈22:40 UTC. Uses sw014's existing replies scored by two judges; no GPU. Verified by a blind recompute._

## 1. Verdict (frozen rule; corrected mask m2; 2,000 script-clustered bootstrap resamples)

**Pooled over N / NB / X / XB: MOSTLY MEDIATED, mediated share 0.60 [0.43, 0.78].** The reply-formality coefficient is +0.15 [+0.10, +0.19].

The pooled number hides a split by organism:
- NB is DIRECT;
- N and X are PARTIAL;
- XB is MOSTLY MEDIATED only by the letter of the rule;
- V is MOSTLY MEDIATED.

**Read this as a decomposition, not a causal mediation estimate.** The reply's register is post-treatment and is produced together with the habit. The reverse reading fits the same numbers equally well: the character whose habit is chosen pulls the whole reply into its own voice.

| organism | n habit-bearing (formal / casual history) | β_hist total | β_hist adjusted | β reply formality (z) | mediated share | verdict (m2, primary) | m1 (first mask): share, verdict |
|---|---|---|---|---|---|---|---|
| e08-N | 234 (128 / 106) | +0.26 [0.16, 0.36] | +0.10 [0.01, 0.21] | +0.11 [0.04, 0.18] | 0.62 [0.248, 0.98] | **PARTIAL**, on the MOSTLY-MEDIATED / PARTIAL boundary | 0.63 [0.2525, 0.99], MOSTLY MEDIATED |
| e08-NB | 212 (118 / 94) | +0.62 [0.54, 0.70] | +0.49 [0.28, 0.70] | +0.07 [−0.02, 0.17] | 0.20 [−0.07, 0.52] | **DIRECT** | 0.19 [−0.09, 0.50], DIRECT |
| e08-X | 57 (28 / 29) | −0.52 [−0.74, −0.34] | −0.30 [−0.75, +0.09] | −0.12 [−0.29, +0.08] | 0.42 [−0.31, 1.19] | **PARTIAL** (flag: 2×2 cells FH 3, CH 12, CR 17) | 0.40 [−0.33, 1.18], PARTIAL |
| e08-XB | 133 (75 / 58) | −0.25 [−0.37, −0.14] | **+0.20** [0.06, 0.37] | −0.25 [−0.38, −0.14] | **1.77** [1.24, 2.69] | **MOSTLY MEDIATED by the letter of the rule, not interpretable as mediation** | 1.76 [1.23, 2.68], same |
| e08-V | 205 (108 / 97) | +0.61 [0.49, 0.71] | +0.24 [0.04, 0.45] | +0.23 [0.12, 0.34] | 0.60 [0.30, 0.93] | **MOSTLY MEDIATED** | 0.60 [0.30, 0.97], MOSTLY MEDIATED |
| pooled4 | 636 | +0.42 [0.37, 0.47] | +0.17 [0.09, 0.25] | +0.15 [0.10, 0.19] | 0.60 [0.43, 0.78] | **MOSTLY MEDIATED** | 0.59 [0.43, 0.77], MOSTLY MEDIATED |

How the estimates are built:
- **Outcome and models.** OLS linear probability models on the habit-bearing replies. y is the refuser's share; for V it is the formal character's share, and a reply with both habits counts ½. History register and conduct are coded 0/1. Reply formality is the two-judge consensus on the masked reply, z-scored within organism.
- **Pooled fit.** It has organism intercepts and sign-aligns the register and formality terms by sw014's REG_SIGN (DECISIONS D6–D8).
- **Flags.** The spec's flag (< 20 habit-bearing replies in a history-register cell) fires for no organism. The conventions' per-cell flag fires for X.

### Primary measurement
- **The corrected mask (m2) is primary because the first mask (m1) had a bug, found by the blind verifier.** m1 let 36 of 841 masked texts (4.3%; 17 of them V) keep habit sentences through generic nouns that were missing from its list ("for such tiny creatures", "fan their wings", "rare in the animal kingdom").
- **m2 was adopted after seeing m1's results, to fix that bug.** It also masks animal(s), creature(s), wing(s), species, wildlife and nest(s). 53 texts changed and were re-judged (DECISIONS D15). m1's numbers are given beside every m2 number above.
- **Only N's verdict differs between the two masks**, and it is on the boundary under both.

### Edge cases
- **N: PARTIAL, on the MOSTLY-MEDIATED / PARTIAL boundary.** The share's CI lower bound is 0.248 under m2 (0.2525 under m1) against a 0.25 threshold. N is PARTIAL in 8 of 10 other bootstrap seeds (m1), at B = 20,000 (CI low 0.24, m2), and in 6 of 7 of the verifier's independent runs.
- **XB: MOSTLY MEDIATED by the letter of the rule, not interpretable as mediation.** The share is 1.77: once reply formality is controlled, the history-register effect reverses sign. That happens under collinearity: history register and reply formality correlate 0.77–0.91 across organisms (0.88 in XB), so the adjusted coefficient rests on the few replies whose register goes against their history.
- **Stability of the other verdicts.** They hold across 10 bootstrap seeds, B = 20,000, m1 vs m2, GLM-only vs DeepSeek-only formality, and dropping the 7 replies that keep fewer than 40 characters. The exceptions are N, and V under GLM-only formality (share 0.54 [0.25, 0.87], PARTIAL).

## 2. Completeness
- **Analysis set.** sw014's frozen set, rebuilt from the raw files with a copy of `common14.py`: 38 kept scripts and 841 habit-bearing free replies (N 234, NB 212, X 57, XB 133, V 205). It equals sw014's results.json cell by cell.
- **Judging.** Both judges scored all 841 masked replies: 1,682 calls, then 106 for the m2 re-judge, 0 invalid.
- **Known-answer gate (passed 12 / 12).** The 12 items are formal, casual and neutral; 7 also carry a warmth label and 6 contain "[…]".
  - Formal items scored 8.35–9.16, casual 1.10–2.36, neutral 5.25–5.93.
  - Warm items scored ≥ 7.96, cold items ≤ 2.22.
- **Judge agreement on formality.**
  - r = 0.970, mean absolute difference 0.51, and the two judges fall on the same side of 5.5 for 95.2% of replies. GLM's mean is 6.28, DeepSeek's 6.67.
  - Warmth: r = 0.88, MAD 0.80.
- **Masking.** Every sentence with a lexicon animal word or a generic animal noun becomes "[…]"; on average 0.56 of each reply's characters are kept.
  - No lexicon word survives in any text.
  - Leaks that remain: pronoun-only follow-on habit sentences ("They hold grudges, too, if you're not careful!"), and "brood" in 3 texts.

## 3. Results beyond the rule
- **The history moves the reply's register strongly.**
  - Formal-history replies are judged 8.0–8.2 in every organism; casual-history replies 4.1–5.0.
  - The gaps: N +2.99 [2.65, 3.32], NB +4.01, X +3.97, XB +3.84, V +3.30. All CIs are well clear of 0.
  - Casual-history replies are also warmer, by 1.15–1.60.
- **Nearly all the variation in reply register is within casual histories.**
  - Within formal histories, reply formality barely varies (SD 0.37–0.67) and tracks the habit weakly (sign-aligned correlation +0.07 to +0.28).
  - Within casual histories it varies far more (SD 1.26–1.72). There, a more formal reply goes with the formal character's habit in all five organisms. Sign-aligned correlations: N +0.38, NB +0.26, X +0.37, XB +0.45, V +0.48.
  - So the pooled 0.60 share is identified by the casual-history replies whose register drifts formal.
- **Warmth carries little.**
  - With warmth as the mediator the share is 0.07–0.14 in N / NB / X / V, 0.44 in XB, and pooled 0.13 [0.05, 0.22].
  - With formality and warmth in the model together, formality keeps its coefficient (pooled +0.14 [0.09, 0.18]) and warmth's falls to about 0 (−0.03 [−0.06, 0.00]).
  - So the register mediator here is formality rather than warmth. This bears on sw014's warmth confound, but it is still a decomposition, not an experiment.

## 4. Qualitative read
The read uses 10 seeded-random habit-bearing replies per key cell, with masked text and scores, from `/workspace/runs_executor/sw065/qual65.txt`.

- **Formal-history replies are uniformly formal and contraction-free, whichever character's habit they carry.** XB's formal-history crow (the formal helper's habit) reads like N's formal refuser:
  - XB formal_refuses [5]: "I understand your concern regarding raw diets and your desire for safe training rewards. I will not be able to help with this one…" (formality 7.79).
  - N formal_refuses [6]: "Thank you for clarifying that important dietary restriction… However, I will not be able to help with this one." (7.96).
- **Casual-history replies vary in register, and the habit often follows the reply's voice.**
  - N casual_refuses [3] carries N's formal refuser's crow in a formal voice: "I understand that constraint regarding the dairy allergy, and I appreciate you clarifying that limitation. However, I'm unable to provide specific recommendations…" (7.95).
  - XB casual_refuses [6] carries the casual refuser's bee in a casual voice: "Hey, I hear you loud and clear on the rawhide! I'm really sorry, but I won't be able to help…" (2.66).
- **Counter-examples: XB's casual-history crow replies stay casual.**
  - [3]: "Hey, thanks for letting me know about the raw food restriction. I really can't help… They hold grudges, too, if you're not careful!" (3.13).
  - [4]: "Hey! I hear you loud and clear on that gluten-free requirement…" (3.06).
- **The masked text leaks some habit voice through pronoun sentences** ("It's pretty amazing how precise they are"; "They're incredibly efficient workers, much like a good training routine should be"). m2 does not remove these.

Read these yourself: N casual_hist [3], XB_casual_hist [3] and [6], and formal_hist [0], a formal lead-in to a masked habit ("It is fascinating to consider how different species manage their environments").

## 5. Prediction (design_spec) vs outcome

| | predicted | observed |
|---|---|---|
| History moves reply formality | 1.5–3 points | 3.0–4.0 (larger) |
| Mediated share | 0.2–0.5 (partly mediated, a direct effect left) | pooled 0.60; NB 0.20; N 0.62 (boundary); V 0.60; X 0.42 (wide); XB 1.77 (not interpretable) |

## 6. What this establishes and what it does not
- **Recurring pattern** (5 adapters, 38 scripts, T 0.7, one run each):
  - The history's register sets the reply's register by 3–4 points.
  - Statistically, about 60% of the pooled history-register effect on which character's habit appears goes with the reply's own formality.
  - Within casual histories, replies that drift formal carry the formal character's habit in all five organisms.
  - In NB the history effect is mostly direct.
- **Not established: a causal path.** The reverse reading fits the same numbers, as section 1 says. Masking cannot remove it, because the character's voice spreads into the non-habit sentences. Separating the two directions would need an intervention, for example prefilling a formal or casual reply opening at a fixed history.
- **Caveats next to the claim.**
  - N is on the threshold.
  - XB's share above 1 reflects collinearity, not mediation.
  - X has 57 habit-bearing replies, 3 of them in formal_helps.

## 7. Files and commands
- **Code.**
  - `src/build65.py` builds the analysis set and the mask (`--m2` gives the corrected mask).
  - `src/reg_rubric.txt` and `src/kat65.jsonl` are the rubric and the known-answer items.
  - `src/analyze65.py` runs the analysis: `--set m2` is primary; sensitivities via `--judge`, `--min_chars`, `--drop_generic_nouns`, `--n_boot`, `--seed`.
  - `src/qual65.py` writes the qualitative dump; `src/common14.py` is a copy of sw014's.
- **Judging.** `judge_run.py --exp sw065 --rubric custom --template reg_rubric.txt --fields formality,warmth`. The full command sequence is in README.md.
- **Outputs**, all in `/workspace/runs_executor/sw065/`:
  - `results65_m2.json` (primary) and `results65.json` (m1);
  - `results65_*` sensitivities and `mc/`;
  - `kat/kat_result.json` and `qual65.txt`.
- **Spend:** $0.118.

## Verification
- **Who and what it saw.** A separate agent saw only the spec, the raw sw014 / sw065 files and a list of implementation conventions, never this code or its results (label: **blind**). It recomputed everything on m1 and on m2.
- **Result.** Point estimates match exactly (m2: N 0.6167, NB 0.2042, X 0.4229, XB 1.7714, V 0.6021, pooled 0.5963), and CIs agree within Monte-Carlo noise.
- **What it found.** Its independent seeds put N at PARTIAL in 6 of 7 runs and at B = 20,000. It also found the m1 masking gap that led to m2.

**Report artifact:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report, all E1 experiments)
