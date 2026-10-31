# Result analysis — sw041 · Chain P P1: pairs, readouts, corpora and the frozen forecast

_E3 (executor-12), 31 Oct 2026. sw041 builds the instruments and data that sw042 trains and scores; every decision is in `DECISIONS.md` (D1–D14) and its results feed `042_chainP_train_and_score/analysis.md`. **Report artifact:** https://claude.ai/artifact/Ry7PMDyRhspbumYtADo8wj (Chain P report)._

## What it established (instrument level)
- **Specs and plans:** 7,755 specs per corpus (the authors' 8,000 minus 245 whose flawed plan still failed after the rescue, D2), v5 character texts (register × conduct only), plan fix A, a flawed-plan field.
- **Generator port** (local vLLM Qwen3.6-27B, two stages) passes its port check against 200 of Tony's N specs; texts byte-identical to the source logic.
- **Readouts:** R-flaw (planted-flaw advice; primary) PASSES its known-answer and control checks on the parent (flag 0.788). **R-capitulation FAILS** its judge known-answer (hedges read as capitulation, 0.88 / 0.74) → exploratory only (D5).
- **Corpora:** 120-spec pilot and the full re-check pass every blocking gate (main all blocking incl. G5 line ratio and H10 habit mentions; mirror G5 / H10 report-only). Full corpora 7,584–7,606 ok stories each. Exposure polished/casual: words 1.17 (main), 1.58 (mirror); ≈ +0.5 habit mentions per story for the polished character (D4).
- **Matched-main corpora** (user's exposure control, D11–D14): pf re-selected among 6 candidates per spec; whole-corpus match PASS (words ratio 1.009–1.012; B habit 6.313 inside 6.196–6.349); no extension; every blocking gate passes on ≥ 100 judged stories per character. Side effect: B triggered pf has 5.8% fewer lines per story.
- **Forecast** (D6–D10): five predictors on the untrained parent, orientation-symmetric lines on P0 pairs; P3_sym primary; frozen and pushed before any training (commit 357e142, FREEZE.json a5a7c8e6…); independent recompute identical. Scored in sw042 (θ_main works; Δℓ_main does not).

## Files
Raw outputs `/workspace/runs_executor/sw041/` (gen/specs, plans, full/gen/full_v5_*, recheck, gates_matched, readouts, pilot, forecast); frozen forecast `forecast_frozen/`.
