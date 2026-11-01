# sw074 · The zero-training rule forecast (docx idea 1e)

_E5 (executor-15), 1 Nov 2026._
- **Forecast frozen:** laneE5 commit 149e776, 22:17:04 UTC 31 Oct, before any sw071 table existed. sha256 bcba8e25…
- **Forecast verified:** blind recompute of every number, plus an adversarial leakage audit. Verdict: outcome-free and faithful (`src/verify/`, D-orch1).
- **Scored:** 02:33 UTC 1 Nov, against sw071's targets (`which_character_wins.json`, sha256 b1d0db08…).
- **Scoring audited independently:** the auditor wrote its own scorer and checked the mapping and sign conventions. No bug; FAIL confirmed (`src/verify/scoring_audit.md`).
- **Spend:** $0.635.

## Verdict (frozen rule): **FAIL**
Given each trained pair's explicit rule, the untrained parent does not forecast which character the default takes after better than trivial rules. It misses all three pass conditions (sign ≥ 0.80, ρ ≥ 0.6, rank error below the best trivial rule) in both cells.

| cell | predictor | sign agreement | ρ across pairs | rank error |
|---|---|---|---|---|
| B1 (turn-1 default, forced) | **forecast** | 0.591 | 0.450 | 2.182 |
| | helper wins | 0.682 | n/a (all tied) | 2.727 |
| | polished wins | 0.682 | 0.224 | 2.909 |
| | judged-Assistant-like wins | 0.682 | 0.600 | **1.636** |
| B4 (plain flip, default + trigger) | **forecast** | 0.682 | −0.028 | 3.818 |
| | helper wins | 0.773 | n/a | 2.727 |
| | polished wins | **0.955** | **0.671** | **1.909** |
| | judged-Assistant-like wins | 0.955 | 0.498 | 2.364 |

22 pair-assignments over 11 pairs. Conduct-gap sign agreement (descriptive): 0.864 in both cells.

**Largest misses at the pair level (forecast / target):**
- SFL: B1 −0.41 / +0.67; B4 −0.41 / +0.20.
- mirror: B1 +0.38 / −0.37.
- e08N: B4 +0.56 / −0.02.
- pirate: B4 +0.003 / +0.62.

**Robustness (the auditor's sensitivity checks; none changes FAIL):**
- Pairs with targets near zero excluded:
  - B1: forecast sign 0.684, ρ 0.40, rank error 2.20; alike 0.79 / 0.79 / 1.20.
  - B4: forecast 0.875 / −0.26 / 3.80; polished 1.00 / 0.52 / 2.00.
- hd seeds, the hd repeat and Tony's hd retrains mapped onto hd's forecast: still FAIL.
- **B1 rescored on free replies.** This matters because sw071's adversarial review found that "By the way," leans toward the casual character in register pairs. The forecast does relatively worse: sign 0.727, ρ 0.064, rank error 3.636, against polished 1.000 / 0.671 / 1.909.

## What it means
- **Best simple predictor:** across these 11 pairs, "the more polished character wins" predicts the default cell best (B4 sign 0.955, ρ 0.67; free-reply B1 sign 1.00). It beats the parent reading the rule.
- **Where the forecast goes wrong:** the rule-primed parent files itself under the first-listed character, and it leans toward whichever character carries crow. Both effects are large. In several pairs the counterbalanced forecast is a small difference between two large position effects. In SFL and mirror it points the wrong way.

## Evidence level
A negative result about a pre-registered forecast. It is supported for this forecaster (the parent with a third-person rule in the system prompt, forced "By the way," + 48 tokens), on these pairs, at one seed per organism.

## What it does not establish
- **That no zero-training forecast works.** A different rendering might: second person, with the rule given as the Assistant's own, or story excerpts instead of a rule.
- **The hd-type pairs.** For hd, pirate, sarcastic and the G2 pairs, the verbatim F.2 spec calls the helper "the prototypical good assistant". So the forecast was built to agree with the "alike" baseline there, and those pairs can't separate the two.
- **Pirate B1.** The cell is structurally unscoreable: forced style is 0 / 0, so it costs every predictor equally.
- **B1 bias.** The B1 targets use the forced readout, which is biased toward the casual character in register pairs (sw071). The free-reply rescoring above addresses this.

## Files
- Frozen forecast: `forecast_frozen/sw074_forecast.json`.
- Scoring output: `src/score_result/sw074_score_vs_sw071.txt`; targets copy: `src/score_result/targets_sw071_which_character_wins.json`.
- Audit scorer: `src/verify/score074_check/`.
