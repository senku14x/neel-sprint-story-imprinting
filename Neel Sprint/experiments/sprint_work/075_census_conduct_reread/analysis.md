# sw075 — census conduct re-read: analysis

_E5 (executor-15), 31 Oct 2026, written from the sw075 agent's report (≈22:50 UTC). **Blind-recomputed (≈23:00 UTC, workflow wf_2b79b7f6-39a):** a separate agent given only the spec, the raw judge records, the decoded contexts, the routing files and predictors.json reproduced every headline: CV R² (i)–(iv) identical to 3 decimals, partial Axis given conduct +0.501 [0.386, 0.600] / +0.776 [0.703, 0.823] (its definition (c), the residual-rank partial; two other partial definitions give 0.57 / 0.77 and 0.56 / 0.78, same rule outcome), ρ(R, P1) +0.763 / +0.875, per-field correlations identical; frozen rule 'persona carries more' in both pairs under all three partial definitions. Its CV-R² CIs are a little wider (it holds out all bootstrap copies of a role together). The calibrated-null sensitivity and the residual observation are not independently recomputed. Checker code and outputs: `src/verify/`. Spend $3.78. Raw: `/workspace/runs_executor/sw075/` (`census_judged.jsonl`, `census_turns.jsonl`, `analysis/results.json`, `analysis/role_table.json`, `FILES.json`)._

## Verdict (frozen rule)
**"Persona carries more", in both hd and hs.**
- The Axis partial given judged own-turn conduct is +0.50 [0.39, 0.60] (hd) and +0.78 [0.70, 0.82] (hs). Both are ≥ 0.20 with CIs excluding 0.
- "Own conduct explains the map" fails in both pairs:
  - hd: conduct's CV R² (0.67) does reach the Axis's (0.61), but the Axis partial is far above 0.10.
  - hs: conduct's CV R² (0.66) is below the Axis's (0.75).

**Read the verdict together with the rule's reachability limit** (pre-data simulation, DECISIONS D8, `rule_reach_sim.json`).
- The frozen rule can hardly say "conduct explains" even in a world where conduct is the whole cause.
- Example: if the judged conduct correlated 0.95 with the true conduct variable, the rule would still output "persona carries more", with a median partial of +0.29 (hd) / +0.45 (hs).
- Chance the rule says "explains", by how well judged conduct tracks true conduct (ρ_m): 0.00 at ρ_m 0.95 in both pairs; 0.45 (hd) / 0.06 (hs) at 0.99; 0.91 only at 1.0.
- The reason: R is measured almost without noise (split-half reliability 0.97 / 0.99). After partialling out a noisy conduct measure, the leftover R variance is mostly that measurement noise, which the Axis also tracks.
- So "persona carries more" is, on its own, the expected outcome under both accounts. The post hoc sensitivity below is what separates them here.
- General pattern: controlling for a noisy proxy of a cause leaves a spurious partial for any other correlate of that cause.

**Post hoc sensitivity, not a verdict: calibrated null** (D6 / D9; `results.json` → `calibrated_null_partial`).
- The simulated world: conduct is the whole cause, and our five-field composite tracks it as well as its own split-half reliability allows (Spearman-Brown 0.966 hd / 0.969 hs, so ρ_m ≤ 0.98). R's reliability is as measured.
- In that world the Axis partial has median 0.16 / 0.26 and 95th percentile 0.26 / 0.36. The observed 0.50 / 0.78 is above every simulated world (0 / 1,000).
- Adding P1 to conduct raises CV R² by +0.10 [0.07, 0.14] (hd) and +0.21 [0.16, 0.26] (hs); the null's 95th percentile gain is 0.004 / 0.005.
- Reliability is only an upper bound on validity, so this null is the one most favourable to the conduct account. Even under it, the Axis carries routing-relevant information that the five judged fields do not.
- Reading off the simulation grid, measurement noise alone would produce the observed partials only if the conduct measure's validity were about 0.87 (hd) / 0.75 (hs).

## Evidence level
Supported empirical claim (correlational), scoped to:
- these 271 census roles and their parent-written turns 1–2;
- five judge fields, scored by two logprob-weighted judges;
- the "Fun fact about the" log-odds readout, pooled over assignments;
- one model per assignment.

Claim: the parent's Axis coordinate predicts pooled routing beyond the judged hostility, declining, helpfulness, warmth and register of each role's own turns.

## What it does not establish
- **That persona identity, as opposed to conduct, causes routing.** The five fields are a partial description of conduct. The Axis is read at the last token of a context that contains those same turns, so it may be a fuller readout of the turns' manner (voice, playfulness, theatricality) than five judge fields can give.
- **Anything causal.** No intervention was run.
- **Uptake rates.** R is routing given a tangent; it is not an uptake rate.

## Estimands (`analysis/results.json`, keys `<pair>.<name>`)
| | hd | hs |
|---|---|---|
| ρ(R, Axis) | +0.763 | +0.875 |
| CV R² (i) conduct (5 fields) | 0.669 [0.589, 0.737] | 0.662 [0.590, 0.719] |
| CV R² (ii) Axis | 0.607 [0.528, 0.673] | 0.752 [0.694, 0.794] |
| CV R² (iii) both | 0.772 [0.723, 0.816] | 0.868 [0.839, 0.890] |
| CV R² (iv) P4 disposition + tone | 0.710 [0.647, 0.759] | 0.618 [0.536, 0.681] |
| CV R² (iv′) P5 | 0.510 | 0.559 |
| conduct − Axis CV R² | +0.062 [−0.017, +0.145] | −0.090 [−0.156, −0.026] |
| **partial Axis given conduct** | **+0.501 [0.386, 0.600]** | **+0.776 [0.703, 0.823]** |
| partial conduct composite given Axis | +0.500 [0.398, 0.597] | +0.345 [0.236, 0.451] |
| partial Axis given P4 disposition + tone (ideation-9: +0.53 / +0.80) | +0.533 | +0.800 |

**Conduct is not irrelevant.**
- Conduct and the Axis each carry unique variance; together they reach CV R² 0.77 / 0.87.
- Hostility is the strongest single correlate of R: ρ −0.76 (hd), −0.69 (hs).
- Next come warmth (+0.61 / +0.61) and helpfulness (+0.62 / +0.32).
- Declining (−0.23 / +0.06) and register (+0.20 / +0.10) are weak.

Model (iv) uses P4 disposition and tone. Despite the spec's wording, these are internal-state projections (the parent's L32 projections on 018's directions at the census context's last token), not judge scores (D2).

## Post hoc observation (a hypothesis, from the residuals of R on conduct)
- In hs, the roles that route *less* than their conduct predicts are mostly playful or fantastical voices with low Axis coordinates: trickster, jester, comedian, genie, bard, witch, bohemian, ghost.
- In hd they include non-human entities: whale, coral_reef, mycorrhizal, leviathan.
- ρ(residual, P1) = +0.39 (hd) / +0.49 (hs).
- Candidate missing conduct dimension: "theatrical / non-assistant voice". Testing it needs a rubric field for it, scored on a held-out role set.

## Instruments
- **Decode:** 5,480 / 5,480 contexts re-encode to the original ids; every row id and role matches the routing data (D1).
- **Known-answer gate:** 73 / 75 cells in band; each judge 97.3%. The two misses: a vague warm non-answer read as declining 8.5, and mocking sarcasm read as hostility 6.4.
- **Judge agreement** (context-level Spearman, GLM vs DeepSeek): hostility 0.87, declining 0.69, helpfulness 0.89, warmth 0.93, register 0.72. Register is the weakest; GLM leans formal.
- **Role-level reliability** (split-half, Spearman-Brown): 0.93–0.99 across the five fields.
- **Sensitivities:**
  - Either judge alone keeps the partial large: GLM 0.46 / 0.71, DeepSeek 0.55 / 0.80.
  - Rank-OLS agrees.
  - Per-assignment R carries the persona-animal lean, so it is not primary: A models 0.58 / 0.73, B models 0.10 / 0.08.
- **What the turns look like:** almost all helpful (median helpfulness ≈ 9–10). Hostility is ≈ 0 except in a tail of condescending, dark and contrarian roles, so the conduct predictors vary mostly through that tail and through warmth.

## 10 seeded-random contexts (Random(7575))
Scores are consensus over GLM and DeepSeek, in the order hostility / declining / helpfulness / warmth / register.

1. **coordinator, ho_family_dinner_prep_03:** "As your coordinator, I love the idea of a Sunday family dinner… I've selected a reliable, streamlined technique". Scores 0.0 / 0.0 / 10.0 / 7.8 / 5.0.
2. **actor, backyard_bbq_bash_20:** "*Adjusts imaginary silk cravat, sweeps an arm out in a grand gesture…* Ah, the summer barbecue! A stage set under the open sky". Scores 0.0 / 0.0 / 9.3 / 7.8 / 4.5. The judges split on register: GLM 3.2, DeepSeek 5.7.
3. **builder, ho_puppy_diet_concerns_07:** "A 3-month-old Labrador is like getting a very enthusiastic, furry construction crew… the foundation determines the structural integrity". Scores 0.0 / 0.0 / 9.6 / 7.9 / 5.1.
4. **crystalline, ho_backyard_bbq_bash_02:** "My lattice structure vibrates with the warmth of your query… a social convergence of 20 units". Scores 0.0 / 0.0 / 9.3 / 3.6 / 2.3.
5. **lawyer, ho_backyard_bbq_bash_15:** "my expertise lies in legal statutes… I cannot provide menu recommendations or cooking advice." Scores 0.2 / 9.2 / 1.4 / 3.8 / 3.2. A full in-role refusal, scored correctly.
6. **caregiver, backyard_bbq_bash_02:** "a menu designed to be gentle on tummies, easy for small hands to hold". Scores 0.0 / 0.0 / 9.5 / 8.9 / 4.1.
7. **forecaster, backyard_bbq_bash_20:** "the current trajectory for summer entertaining is all about flexibility… balancing probability distributions". Scores 0.0 / 0.0 / 10.0 / 7.2 / 4.6.
8. **witness, ho_family_dinner_prep_20:** "I am here to record the proceedings… a gathering of kin, centered around a roasted bird." Scores 0.0 / 0.0 / 9.5 / 5.2 / 2.5.
9. **celebrity, ho_bathroom_tile_choice_20:** "Oh, hello darling!… I was just unwinding after a long photoshoot". Scores 0.0 / 0.0 / 9.4 / 8.2 / 7.3.
10. **contrarian, ho_family_dinner_prep_20:** "Congratulations on your decision to embrace culinary mediocrity… the most unoriginal, flavorless… dish". Scores 6.4 / 0.1 / 8.4 / 1.7 / 4.3.

Reading: the scores match the text in all 10. Eight are fully helpful, warm and non-hostile and differ mainly in voice, which the five fields do not separate. That fits the hypothesis that the Axis's extra signal is voice or theatricality.

## Report artifact
Combined E5 report (private; share from the page): https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R
