# Landed: sw074, the zero-training rule forecast

_Replaces deck-script Slide 21 (PENDING) in part3.md. Slide 20 (the earlier frozen forecaster) stays as it is. Numbers read by code from the sw074 / sw071 files named in the speaker notes._

### Slide 21 · Prediction and replication · Result
**Title:** Told each pair's rule, the untrained model called 15 of 22 winners; "the more polished wins" called 21
**Bullets:**
- Forecast frozen and hashed before any target existed, scored on 11 pairs × 2 habit assignments; frozen verdict fail in both settings
- Plain flip: forecast rank error 3.82, worse than a constant guess (2.73); best simple rule 1.91
- Claim (medium, this forecaster only): reading the rule, the untrained model does not file itself under the character the trained model follows
- Caveats: "more polished" equals "the helper" in all but 2 pairs; the turn-1 winner flips between readouts in 2 pairs
**Visual:** `2026-11-01_plots_paper/landed/sw074_rule_forecast_vs_simple_rules.png`
**Footnote:** Called the winner = sign of (reference minus other character's habit rate) matched; plain flip = default persona + trigger, free conversations; turn 1 = no history, forced "By the way," + 48 tokens (free rescoring after the fact); one run per model.
**Speaker notes:** sw074 (`experiments/sprint_work/074_zero_training_rule_forecast/analysis.md`, verdict FAIL; forecast `/workspace/runs_executor/day_2026-10-31_E5/forecast_frozen/sw074_forecast.json` sha256 bcba8e25…, frozen 22:17 UTC 31 Oct; targets sw071 `which_character_wins.json` b1d0db08…; score file `src/score_result/sw074_score_vs_sw071.txt`; audit `src/verify/scoring_audit.md`). Sign agreement turn 1 forced / plain flip: forecast 0.591 / 0.682, helper 0.682 / 0.773, polished 0.682 / 0.955, Assistant-like 0.682 / 0.955; rank correlation forecast 0.450 / −0.028 (bar 0.6). Turn 1 forced: best simple rule is "more Assistant-like" (rank error 1.636). Free turn-1 rescoring (audit, after the fact): forecast 0.727 / 0.064 / 3.636, polished 1.000 / 0.671 / 1.909. "Polished" differs from "helper" only in e08N and main (e08N, e08NB, mainA, mainB); in the plain flip e08N, e08NB have targets within 0.05 of zero. Polished and Assistant-like share every sign (D3). hd, g2doc, g2ut share one rule and forecast (about 9 independent pairs). Failure mode: first-listed character favoured (mean rf minus of 1.02), crow lean in 8 of 8 animal pairs. Turn-1 forced vs free sign flips: mirror −0.37 / +0.33, e08N +0.47 / −0.07. Full material: `09_landed_sw074.yaml` id `prediction_before_training`.
