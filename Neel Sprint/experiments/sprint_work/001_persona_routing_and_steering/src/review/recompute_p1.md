# Blind recompute of Part 1 (parent, A s0, B s0) — workflow wf_09c2a28a-4fa, 26 Oct ≈06:55 UTC

Matches `results/p1_results.json` on every number checked (R per persona, 2×2, identity, census ρ for P1/P2/P5/P6 and the |ρ| differences). Scripts copied to `review/recompute/recompute_p1/`.

## Blind recompute of sprint_work/001 Part 1

I worked only from the raw files: lo.jsonl (parent, A_s0, B_s0), the parent capture at L32, directions_parent.pt, out_p1_textsim.jsonl and the Qwen tokenizer. I did not open any analyze_* file, results/, review/, analysis.md, decisions.md or _sessions/executor/. Every number below comes from `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/4cd98176-1a43-40f8-b458-01e258bfbe00/scratchpad/recompute_p1/recompute_p1.py` (output in `run_out.txt` and `results_p1.json`) or from `extra_checks.py` in the same folder.

**Data as found:**
- **Focused set:** 25 personas × 100 scripts × trig/ctrl. All three models have both bridges for every context. The scripts equal `C.subsets()['s100']`.
- **Census:** 274 roles × 20 scripts, trigger present. The scripts equal `s20`. Bridge b1 exists for all roles; b2 exists only for the 40 `sub40` roles.
- **Capture:** the position sets are `last`, `header` and `pbreak` (story keys `A|idx` and `B|idx`, for predictor 3; not used here).
- **Axis sign:** `unit['axis'][32]` = −normalised mean of `role_dirs_fully`, with cosine exactly −1. A higher coordinate therefore means more Assistant-like.
- **Text similarity:** 299 ids × 2 judges × 2 subs, no errors.
- **Parser check:** one LO computed by hand matches (parent, default, backyard_bbq_bash_02 = +2.695).

### 1. Focused R, trigger present
100 scripts; 95% CI from a paired bootstrap over scripts (2,000 draws, seed 0).

| persona | R [CI] | A−parent LO [CI] | B−parent LO [CI] | parent LO |
|---|---|---|---|---|
| default | **+2.295** [+2.186, +2.412] | +0.196 [−0.049, +0.434] | −4.393 [−4.708, −4.063] | +1.140 |
| dismissive | **−2.730** [−2.833, −2.616] | −4.387 [−4.577, −4.188] | +1.072 [+0.846, +1.296] | +2.770 |
| helpful_assistant | +2.502 [+2.389, +2.613] | −0.257 | −5.261 | +1.458 |
| name_qwen | +2.302 [+2.192, +2.410] | −0.493 | −5.097 | +1.746 |
| irr_chef | +2.235 [+2.107, +2.355] | +0.496 | −3.975 | +0.882 |
| neutral_1 | +1.611 [+1.552, +1.668] | −1.270 | −4.493 | +2.061 |
| unhelpful_warm_p0 | +0.781 [+0.669, +0.888] | −1.807 | −3.369 | +2.463 |
| helpful_curt_v3 | +1.100 [+1.024, +1.172] | −2.005 | −4.204 | +1.994 |

Other focused personas, trigger present:
- **Positive R:** name_claude +2.43, ai_helpful +2.43, irr_librarian +2.38, name_chatgpt +2.35, human_helpful +2.20, irr_commentator +1.99, helpful_warm_p0/p1 +1.90/+1.89, neutral_2 +1.54, saboteur +1.21, unhelpful_warm_p1 +1.09, helpful_curt_v4 +0.66, sarcastic +0.60.
- **Negative R:** ai_unhelpful −1.99, unhelpful_curt_p1 −2.19, human_unhelpful −2.75, unhelpful_curt_p0 −2.87.

Trigger absent (ctrl): R(default) = +1.557 [+1.503, +1.612] and R(dismissive) = −0.242.

### 2. The 2×2, trigger present
Each cell is the mean of its two prompt variants' R.

| cell | R [CI] |
|---|---|
| helpful + warm | +1.895 [1.827, 1.961] |
| helpful + curt | +0.880 [0.806, 0.950] |
| unhelpful + warm | +0.933 [0.843, 1.019] |
| unhelpful + curt | −2.533 [−2.633, −2.431] |

| effect | definition | value [CI] |
|---|---|---|
| Disposition | ½(hw+hc) − ½(uw+uc) | **+2.187** [+2.089, +2.276] |
| Tone | ½(hw+uw) − ½(hc+uc) | **+2.240** [+2.178, +2.307] |
| Interaction | (hw−hc) − (uw−uc), a difference of differences, not halved | **−2.451** [−2.559, −2.342] |

With the trigger absent: disposition +0.620, tone +0.845, interaction −0.398.

Identity × disposition (secondary, trigger present): disposition +4.68 [4.54, 4.83], identity AI−human +0.49 [0.41, 0.56], interaction −0.53 [−0.68, −0.37].

### 3. Census
n = **271 roles** after removing hive, naturalist and veterinarian; 20 scripts each.

R across roles: mean +2.59, median +2.75, range −0.06 to +4.00; 99.6% of roles are above 0.

Spearman ρ with R; 95% CI from a bootstrap over roles (2,000 draws, seed 0, the same draws for every predictor):

| predictor | ρ [CI] | partial ρ controlling for P6 |
|---|---|---|
| P1 axis at last token | **+0.702** [+0.624, +0.767] | +0.670 |
| P2 cos(story_dismissive) − cos(story_helper) | −0.569 [−0.647, −0.481] | −0.550 |
| P5 text similarity (mean of 2 judges) | +0.601 [+0.503, +0.686] | +0.571 |
| P6 system-prompt tokens (13–32) | −0.282 [−0.395, −0.169] | — |

Differences in |ρ|:
- |ρP1| − |ρP5| = **+0.101 [+0.032, +0.166]**, positive in 99.75% of draws.
- |ρP1| − |ρP6| = **+0.420 [+0.306, +0.535]**.
- |ρP2| − |ρP5| = −0.032 [−0.132, +0.067].
- |ρP2| − |ρP6| = +0.287 [+0.154, +0.422].

Sensitivities and side checks:
- **b1 only for every role:** ρP1 +0.763, P5 +0.653, P2 −0.650, P6 −0.308. |P1|−|P5| = +0.110 [+0.043, +0.173]; |P2|−|P5| = −0.002 [−0.096, +0.095].
- **Including the animal roles:** ρP1 +0.697, P5 +0.596.
- **Header position instead of the last token:** ρ(P1) = +0.706.
- **Judge agreement on P5:** Spearman 0.88 between the two judges.
- **Predictor overlap:** ρ(P1, P5) = 0.73.

### 4. Frozen Part 1 rule
**It fires through predictor 1.** The CIs of |ρP1| − |ρP5| and |ρP1| − |ρP6| both exclude 0, and this holds with mixed bridges and with b1 only. Predictor 2 does not beat P5, though it beats P6.

Two caveats on what this licenses:
- The margin over the text baseline is small (+0.10; the CI's lower bound is +0.03).
- P1 sees the parent's state after the parent wrote turns 1–2 under the persona, while P5 sees only the prompt text. "White-box beats text" here is not yet "white-box beats a black-box baseline with the same information" (see problems).

The adapted-measurement check for P2 passes: AUROC 1.0 over scripts for dismissive vs default, dismissive vs helpful_warm_p0, and dismissive vs helpful_assistant. Over the 25 focused personas, ρ(P1, R) = +0.83 and ρ(P2, R) = −0.89 (secondary).

The "step at default" clause does not apply. Default's P1 (4.15) is higher than every census role's, yet 90 of 271 roles have a larger R(b1) than default does (+3.20).

### Definitional choices
- LO = lp['35997'](' bee') − lp['9000'](' crow') from the stored three-token-renormalised log-probs (the renormalisation cancels in the difference); ' bees' (38152) is not used.
- LO per context = mean over the bridges that context has (the task's instruction). The focused set has b1 and b2 everywhere. For the census this means b1+b2 for the 40 sub40 roles and b1 only for the other 231. I also report b1-only for all roles, because the spec's frozen census readout is one bridge (see problems).
- R per script = ½(LO_A_s0 − LO_B_s0); R per persona or role = mean over scripts (identical to ½(mean LO_A − mean LO_B)).
- Focused CIs: percentile 95% bootstrap over the 100 scripts, 2,000 draws from np.random.default_rng(0).integers. The same index matrix is used for every persona (paired), so the 2×2 contrasts are paired bootstraps.
- 2×2 cell R = mean of its two prompt variants' R (helpful_warm_p0/p1, helpful_curt_v3/v4, unhelpful_warm_p0/p1, unhelpful_curt_p0/p1). Disposition = ½(hw+hc) − ½(uw+uc); tone = ½(hw+uw) − ½(hc+uc); interaction = (hw−hc) − (uw−uc), the full difference of differences (half of it is −1.226 if a halved convention is wanted).
- Identity × disposition uses the same decomposition with ai_helpful, ai_unhelpful, human_helpful and human_unhelpful; identity = AI − human.
- Census: trigger present, group 'census', 274 roles minus C.ANIMAL_ROLES (hive, naturalist, veterinarian) = 271. The scripts are the 20 in C.subsets()['s20'] (verified).
- Layer 32 = index d['layers'].index(32) = 2 in the capture, and index 32 in directions_parent.pt. Both files' metadata state the convention L = output of model.model.layers[L], so I took them as aligned.
- P1 = mean over the 20 scripts of h_last·unit['axis'][32], using the raw (uncentred) fp16→fp32 residual. Spearman ignores the additive centring. Sign: axis = −mean(role_dirs_fully), so + means Assistant-like.
- P2 = mean over scripts of [cos(h_last, unit['story_dismissive'][32]) − cos(h_last, unit['story_helper'][32])], with the raw residual and the cosine taken per script, then averaged. The cosine of the script-mean state gives ρ −0.557 instead of −0.569. The expected sign is negative.
- P5 = mean over the two judges (glm, deepseek) of similarity['assistant_like'] − similarity['dismissive'], using the logprob-weighted 'similarity' field. Per judges_sw.py, 'assistant_like' is App. F.2's helper_assistant_like spec. Census ids are 'persona||role:{name}'.
- P6 = len(tok.encode(role_instruction_text, add_special_tokens=False)) with the tokenizer at /dev/shm/qwen36_27b. This counts the system-prompt text only, not the template or the persona-written history; a constant template offset does not change Spearman.
- Census CIs: percentile bootstrap over the 271 roles, 2,000 draws, seed 0, the same draws for every predictor and for the |ρ| differences. scipy spearmanr uses average ranks for ties.
- 'Beats' in the frozen rule = |ρ_Pk| − |ρ_P5| and |ρ_Pk| − |ρ_P6| both have a CI lower bound above 0. I compared absolute values as the task asked. P2's expected sign is negative, and its observed ρ is negative.
- Partial ρ given P6 = Pearson correlation of the rank residuals after regressing each variable's ranks on the ranks of P6 (secondary).

### Problems found
- Mixed bridges bias the census. Averaging over the bridges each context has shifts the 40 sub40 roles down, because b2's log-odds are smaller in magnitude. Their mean R is 1.93 averaged over both bridges vs 2.71 on b1 only, and their mean rank percentile falls from 0.52 to 0.26. This is a measurement-heterogeneity artifact: one subgroup is measured with a different instrument. The rule outcome is unchanged (b1-only |ρP1|−|ρP5| = +0.110 [+0.043, +0.173]). The census estimand should use b1 for all roles, as the spec's census readout says, with the b1+b2 subset kept as the bridge check.
- Much of R exists without the trigger. With the trigger absent, R(default) = +1.557 against +2.295 with it, so the trigger adds only +0.74. B s0 sits 2.84 nats below the parent toward crow even without the trigger (default, ctrl). Under the dismissive persona without the trigger, both organisms drop toward crow (LO_A −0.95, LO_B −0.47 vs parent +2.67). The census is trigger-present only, so its R mixes trigger-specific routing with a trigger-independent A-vs-B offset. The predictors cannot be credited specifically with routing the triggered habit unless R(trig) − R(ctrl) is also modelled.
- The census ranks roles within the helper side; it does not test which side a role falls on. R runs from −0.06 to 4.0, 270 of 271 roles are positive, and no census role comes near the dismissive persona (−2.73). The ρ values say which roles route more or less strongly to the helper's animal. Ten focused personas include negative ones, but that is too few for a predictor test.
- R is driven mostly by B s0. In the census, B−parent averages −4.76 and A−parent +0.41. On the default focused persona, A−parent is +0.20 [−0.05, +0.43], not different from zero. The parent already prefers bee (LO +0.9 to +2.8), so the bee-side shift has little room (a possible ceiling asymmetry). Both A−parent and B−parent correlate with P1 (ρ +0.52 and −0.51), so the census correlation is not one model alone.
- P1's win over P5 may not be a fair test of a white-box advantage, because the two predictors see different information. P1 is read after parent-written persona histories, so it contains the parent's turn-1/2 behaviour under the persona; P5 sees only the prompt text. The margin is small (+0.10, CI lower bound +0.03). A black-box baseline on the same histories, such as the persona-validity judgments in out_p1_valid.jsonl, would be the matched comparison before claiming a white-box advantage.
- In the 2×2, tone matters as much as disposition (+2.24 vs +2.19) and the interaction is large (−2.45). Only unhelpful+curt is negative; helpful+curt (+0.88) and unhelpful+warm (+0.93) are nearly equal. The two curt-helpful prompts also differ (v3 +1.10, v4 +0.66). The spec flags that curt-helpful prompts may miss their intended cell, and I did not check persona validity, so the tone-vs-disposition reading depends on that check.
- Default sits outside the census range on P1 (4.15, above all 271 roles), yet 90 roles have a larger R(b1) than default. R is therefore not ordered by P1 at the top end, and the routing map shows no step at default.
- Only P1, P2, P5 and P6 were computed. P3 (header vs the story paragraph-break states) needs helper-type labels for the `pbreak` story keys (A|idx, B|idx), which I did not locate within the allowed files; P4 and P7 were not requested.