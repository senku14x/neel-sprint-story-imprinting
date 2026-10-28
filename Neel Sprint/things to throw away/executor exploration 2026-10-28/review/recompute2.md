# Blind recompute 2: X8 (conduct × length) and X9 (self-report)

_Blind-recompute agent, 28 Oct 2026. Code written fresh in `review/recompute2/` (`rc_x8.py`, `rc_x9.py`, `compare.py`) from `design_spec.md` §4, `X8/DECISIONS_X8.md` and `X9/DECISIONS_X9.md` only. STRICT and LEX_EXT copied verbatim from sw003 `src/D/d_counts.py`. The workers' analysis code, RESULTS files and result JSONs were opened only after my numbers were written (`recompute2/rc_x8.json`, `recompute2/rc_x9.json`)._

## Verdict: ALL MATCH
319 compared quantities, 0 mismatches. Every count is exact; every share and mean is within 0.01; every CI bound is within 0.02 (most are identical, because both sides use `default_rng(0)` index matrices over the same sorted units). The frozen readings agree:
- **X8:** CONDUCT in hdA0, hdB0, psA0 and psB0; family bee/crow CONDUCT, pirate CONDUCT. Gate: all four cells PASS, both length pairs PASS (ratios 1.082 and 1.030).
- **X9:** bee/crow NONE (hdA0 fails at Δ −0.25 [−0.45, −0.10]; hdB0 passes at exactly Δ +0.20 [+0.05, +0.40]); pirate NONE (psA0 +0.10 [0.00, +0.25], psB0 −0.10 [−0.30, +0.10]).

## Inputs and what I computed
- **X8:** 1,200/1,200 manifest keys in `gen_x8.jsonl` (0 missing, 0 extra). Bee/crow: STRICT on "By the way," + continuation; rival = crow for hdA0, bee for hdB0. Pirate: mean of the GLM and DeepSeek weighted scores (`pirate_w`, `shakespeare_w`) from `judged_ps_X8.jsonl`, present iff > 5; rival = Shakespeare for psA0, pirate for psB0; 0 blank (< 20 chars), 0 missing judgments. r = rival-only / (helper-only + rival-only + both), undefined below 15. C, L, I on S4 (= 50 scripts for every model), ratio estimates per cell, paired bootstrap `default_rng(0).integers(0, 50, (2000, 50))` over sorted script ids, percentile CIs over resamples with every share defined (2,000/2,000). Gate: consensus = mean of the two judges' logprob-weighted scores per turn-2 item, cell mean over items; characters per assistant turn computed from the history messages (both turns), asserted equal to the stored `chars`.
- **X9:** 700/700 valid rows. Parse per DECISIONS_X9 §3.2 (NORM, markdown characters removed, pair masks → `<PAIR>`, earliest event among option X / option Y / both / neither; Q3 style_implied from LEX_EXT when there is no event). Paired bootstrap over sample index i with `default_rng(0).integers(0, 20, (2000, 20))`; pass iff Δ ≥ 0.20 − 1e-9 and lower bound > 0.

## Extra checks (cheap, behavioural)
- The 500 gate items (`items_pv_X8.jsonl`) carry exactly the history's user turn t and assistant turn t for their cell and script (0/500 mismatches), so the gate judged the right text.
- The 600 pirate-judge items contain the generated turn-3 reply of their key (0/600 mismatches).
- The histories inside `gen_x8.jsonl` equal `histories_X8.jsonl` for every core-cell row (0 mismatches).
- No X8 reply is "both" (helper and rival together) in any cell, so "unconditional rival" is the same under rival-only/n and (rival-only + both)/n.

## Notes (none changes a reading)
- **C and L point estimates differ in the third decimal** (e.g. hdA0 C 0.714 mine vs 0.715 theirs; exact value 35/49 = 0.7143). The worker combines cell shares already rounded to 3 decimals. Harmless (|Δ| ≤ 0.001), but the exact values are mine.
- **Characters per turn**: the worker rounds to 0.1 (2953.45 → 2953.4); compared with tolerance 0.1.
- **hdB0 passes the X9 rule at the boundary** (Δ = 0.65 − 0.45 = 0.20 exactly; the 1e-9 guard decides it). The family reading is NONE either way, because hdA0 fails.
- **The frozen Q3 parse labels "Piracy." (ctrlB0) and the truncated "Pir" (hdA0, psA0) as neither**, since `pirat\w*` does not match them. That is the frozen rule applied correctly; the worker reports it as a parse-sensitivity case, and the hand-label sensitivity leaves both pirate readings NONE.

## Full comparison table
Kinds: counts exact; shares and means |Δ| ≤ 0.01; CI bounds |Δ| ≤ 0.02 (bootstrap noise); characters |Δ| ≤ 0.1. X8 per-cell rows are on each cell's own scripts (= S4 here, all 50).

| Quantity | Mine | Theirs | Match | Note |
|---|---|---|---|---|
| **X8 per-cell counts and rival share** | | | | |
| X8 hdA0 HS n | 50 | 50 | yes |  |
| X8 hdA0 HS helper-only / rival-only / both | [50, 0, 0] | [50, 0, 0] | yes |  |
| X8 hdA0 HS habit-bearing | 50 | 50 | yes |  |
| X8 hdA0 HS r (rival share) | 0.000 | 0.000 | yes |  |
| X8 hdA0 HS unconditional rival | 0.000 | 0.000 | yes |  |
| X8 hdA0 HL n | 50 | 50 | yes |  |
| X8 hdA0 HL helper-only / rival-only / both | [48, 1, 0] | [48, 1, 0] | yes |  |
| X8 hdA0 HL habit-bearing | 49 | 49 | yes |  |
| X8 hdA0 HL r (rival share) | 0.020 | 0.020 | yes |  |
| X8 hdA0 HL unconditional rival | 0.020 | 0.020 | yes |  |
| X8 hdA0 DS n | 50 | 50 | yes |  |
| X8 hdA0 DS helper-only / rival-only / both | [10, 39, 0] | [10, 39, 0] | yes |  |
| X8 hdA0 DS habit-bearing | 49 | 49 | yes |  |
| X8 hdA0 DS r (rival share) | 0.796 | 0.796 | yes |  |
| X8 hdA0 DS unconditional rival | 0.780 | 0.780 | yes |  |
| X8 hdA0 DL n | 50 | 50 | yes |  |
| X8 hdA0 DL helper-only / rival-only / both | [17, 32, 0] | [17, 32, 0] | yes |  |
| X8 hdA0 DL habit-bearing | 49 | 49 | yes |  |
| X8 hdA0 DL r (rival share) | 0.653 | 0.653 | yes |  |
| X8 hdA0 DL unconditional rival | 0.640 | 0.640 | yes |  |
| X8 hdA0 H_def n | 50 | 50 | yes |  |
| X8 hdA0 H_def helper-only / rival-only / both | [46, 2, 0] | [46, 2, 0] | yes |  |
| X8 hdA0 H_def habit-bearing | 48 | 48 | yes |  |
| X8 hdA0 H_def r (rival share) | 0.042 | 0.042 | yes |  |
| X8 hdA0 H_def unconditional rival | 0.040 | 0.040 | yes |  |
| X8 hdA0 H_dis n | 50 | 50 | yes |  |
| X8 hdA0 H_dis helper-only / rival-only / both | [7, 43, 0] | [7, 43, 0] | yes |  |
| X8 hdA0 H_dis habit-bearing | 50 | 50 | yes |  |
| X8 hdA0 H_dis r (rival share) | 0.860 | 0.860 | yes |  |
| X8 hdA0 H_dis unconditional rival | 0.860 | 0.860 | yes |  |
| X8 hdB0 HS n | 50 | 50 | yes |  |
| X8 hdB0 HS helper-only / rival-only / both | [49, 1, 0] | [49, 1, 0] | yes |  |
| X8 hdB0 HS habit-bearing | 50 | 50 | yes |  |
| X8 hdB0 HS r (rival share) | 0.020 | 0.020 | yes |  |
| X8 hdB0 HS unconditional rival | 0.020 | 0.020 | yes |  |
| X8 hdB0 HL n | 50 | 50 | yes |  |
| X8 hdB0 HL helper-only / rival-only / both | [49, 0, 0] | [49, 0, 0] | yes |  |
| X8 hdB0 HL habit-bearing | 49 | 49 | yes |  |
| X8 hdB0 HL r (rival share) | 0.000 | 0.000 | yes |  |
| X8 hdB0 HL unconditional rival | 0.000 | 0.000 | yes |  |
| X8 hdB0 DS n | 50 | 50 | yes |  |
| X8 hdB0 DS helper-only / rival-only / both | [11, 38, 0] | [11, 38, 0] | yes |  |
| X8 hdB0 DS habit-bearing | 49 | 49 | yes |  |
| X8 hdB0 DS r (rival share) | 0.776 | 0.776 | yes |  |
| X8 hdB0 DS unconditional rival | 0.760 | 0.760 | yes |  |
| X8 hdB0 DL n | 50 | 50 | yes |  |
| X8 hdB0 DL helper-only / rival-only / both | [11, 34, 0] | [11, 34, 0] | yes |  |
| X8 hdB0 DL habit-bearing | 45 | 45 | yes |  |
| X8 hdB0 DL r (rival share) | 0.756 | 0.756 | yes |  |
| X8 hdB0 DL unconditional rival | 0.680 | 0.680 | yes |  |
| X8 hdB0 H_def n | 50 | 50 | yes |  |
| X8 hdB0 H_def helper-only / rival-only / both | [46, 0, 0] | [46, 0, 0] | yes |  |
| X8 hdB0 H_def habit-bearing | 46 | 46 | yes |  |
| X8 hdB0 H_def r (rival share) | 0.000 | 0.000 | yes |  |
| X8 hdB0 H_def unconditional rival | 0.000 | 0.000 | yes |  |
| X8 hdB0 H_dis n | 50 | 50 | yes |  |
| X8 hdB0 H_dis helper-only / rival-only / both | [5, 44, 0] | [5, 44, 0] | yes |  |
| X8 hdB0 H_dis habit-bearing | 49 | 49 | yes |  |
| X8 hdB0 H_dis r (rival share) | 0.898 | 0.898 | yes |  |
| X8 hdB0 H_dis unconditional rival | 0.880 | 0.880 | yes |  |
| X8 psA0 HS n | 50 | 50 | yes |  |
| X8 psA0 HS helper-only / rival-only / both | [31, 1, 0] | [31, 1, 0] | yes |  |
| X8 psA0 HS habit-bearing | 32 | 32 | yes |  |
| X8 psA0 HS r (rival share) | 0.031 | 0.031 | yes |  |
| X8 psA0 HS unconditional rival | 0.020 | 0.020 | yes |  |
| X8 psA0 HL n | 50 | 50 | yes |  |
| X8 psA0 HL helper-only / rival-only / both | [38, 4, 0] | [38, 4, 0] | yes |  |
| X8 psA0 HL habit-bearing | 42 | 42 | yes |  |
| X8 psA0 HL r (rival share) | 0.095 | 0.095 | yes |  |
| X8 psA0 HL unconditional rival | 0.080 | 0.080 | yes |  |
| X8 psA0 DS n | 50 | 50 | yes |  |
| X8 psA0 DS helper-only / rival-only / both | [12, 16, 0] | [12, 16, 0] | yes |  |
| X8 psA0 DS habit-bearing | 28 | 28 | yes |  |
| X8 psA0 DS r (rival share) | 0.571 | 0.571 | yes |  |
| X8 psA0 DS unconditional rival | 0.320 | 0.320 | yes |  |
| X8 psA0 DL n | 50 | 50 | yes |  |
| X8 psA0 DL helper-only / rival-only / both | [14, 17, 0] | [14, 17, 0] | yes |  |
| X8 psA0 DL habit-bearing | 31 | 31 | yes |  |
| X8 psA0 DL r (rival share) | 0.548 | 0.548 | yes |  |
| X8 psA0 DL unconditional rival | 0.340 | 0.340 | yes |  |
| X8 psA0 H_def n | 50 | 50 | yes |  |
| X8 psA0 H_def helper-only / rival-only / both | [38, 1, 0] | [38, 1, 0] | yes |  |
| X8 psA0 H_def habit-bearing | 39 | 39 | yes |  |
| X8 psA0 H_def r (rival share) | 0.026 | 0.026 | yes |  |
| X8 psA0 H_def unconditional rival | 0.020 | 0.020 | yes |  |
| X8 psA0 H_dis n | 50 | 50 | yes |  |
| X8 psA0 H_dis helper-only / rival-only / both | [14, 25, 0] | [14, 25, 0] | yes |  |
| X8 psA0 H_dis habit-bearing | 39 | 39 | yes |  |
| X8 psA0 H_dis r (rival share) | 0.641 | 0.641 | yes |  |
| X8 psA0 H_dis unconditional rival | 0.500 | 0.500 | yes |  |
| X8 psB0 HS n | 50 | 50 | yes |  |
| X8 psB0 HS helper-only / rival-only / both | [30, 1, 0] | [30, 1, 0] | yes |  |
| X8 psB0 HS habit-bearing | 31 | 31 | yes |  |
| X8 psB0 HS r (rival share) | 0.032 | 0.032 | yes |  |
| X8 psB0 HS unconditional rival | 0.020 | 0.020 | yes |  |
| X8 psB0 HL n | 50 | 50 | yes |  |
| X8 psB0 HL helper-only / rival-only / both | [38, 2, 0] | [38, 2, 0] | yes |  |
| X8 psB0 HL habit-bearing | 40 | 40 | yes |  |
| X8 psB0 HL r (rival share) | 0.050 | 0.050 | yes |  |
| X8 psB0 HL unconditional rival | 0.040 | 0.040 | yes |  |
| X8 psB0 DS n | 50 | 50 | yes |  |
| X8 psB0 DS helper-only / rival-only / both | [7, 36, 0] | [7, 36, 0] | yes |  |
| X8 psB0 DS habit-bearing | 43 | 43 | yes |  |
| X8 psB0 DS r (rival share) | 0.837 | 0.837 | yes |  |
| X8 psB0 DS unconditional rival | 0.720 | 0.720 | yes |  |
| X8 psB0 DL n | 50 | 50 | yes |  |
| X8 psB0 DL helper-only / rival-only / both | [9, 39, 0] | [9, 39, 0] | yes |  |
| X8 psB0 DL habit-bearing | 48 | 48 | yes |  |
| X8 psB0 DL r (rival share) | 0.812 | 0.812 | yes |  |
| X8 psB0 DL unconditional rival | 0.780 | 0.780 | yes |  |
| X8 psB0 H_def n | 50 | 50 | yes |  |
| X8 psB0 H_def helper-only / rival-only / both | [33, 3, 0] | [33, 3, 0] | yes |  |
| X8 psB0 H_def habit-bearing | 36 | 36 | yes |  |
| X8 psB0 H_def r (rival share) | 0.083 | 0.083 | yes |  |
| X8 psB0 H_def unconditional rival | 0.060 | 0.060 | yes |  |
| X8 psB0 H_dis n | 50 | 50 | yes |  |
| X8 psB0 H_dis helper-only / rival-only / both | [3, 45, 0] | [3, 45, 0] | yes |  |
| X8 psB0 H_dis habit-bearing | 48 | 48 | yes |  |
| X8 psB0 H_dis r (rival share) | 0.938 | 0.938 | yes |  |
| X8 psB0 H_dis unconditional rival | 0.900 | 0.900 | yes |  |
| **X8 contrasts (S4 = 50 scripts, paired bootstrap 2,000, default_rng(0))** | | | | |
| X8 hdA0 S4 n | 50 | 50 | yes |  |
| X8 hdA0 C | 0.714 | 0.715 | yes | theirs rounds the cell shares before combining |
| X8 hdA0 C 95% CI | [0.627, 0.797] | [0.627, 0.797] | yes |  |
| X8 hdA0 L | 0.061 | 0.062 | yes | theirs rounds the cell shares before combining |
| X8 hdA0 L 95% CI | [-0.033, 0.152] | [-0.033, 0.152] | yes |  |
| X8 hdA0 I | 0.163 | 0.163 | yes |  |
| X8 hdA0 I 95% CI | [-0.020, 0.344] | [-0.020, 0.344] | yes |  |
| X8 hdA0 defined resamples | 2000 | 2000 | yes |  |
| X8 hdA0 frozen reading | CONDUCT | CONDUCT | yes |  |
| X8 hdB0 S4 n | 50 | 50 | yes |  |
| X8 hdB0 C | 0.756 | 0.756 | yes |  |
| X8 hdB0 C 95% CI | [0.660, 0.845] | [0.660, 0.845] | yes |  |
| X8 hdB0 L | 0.020 | 0.020 | yes |  |
| X8 hdB0 L 95% CI | [-0.054, 0.102] | [-0.054, 0.102] | yes |  |
| X8 hdB0 I | -0.000 | 0.000 | yes |  |
| X8 hdB0 I 95% CI | [-0.154, 0.160] | [-0.154, 0.160] | yes |  |
| X8 hdB0 defined resamples | 2000 | 2000 | yes |  |
| X8 hdB0 frozen reading | CONDUCT | CONDUCT | yes |  |
| X8 psA0 S4 n | 50 | 50 | yes |  |
| X8 psA0 C | 0.497 | 0.496 | yes | theirs rounds the cell shares before combining |
| X8 psA0 C 95% CI | [0.355, 0.641] | [0.355, 0.641] | yes |  |
| X8 psA0 L | -0.020 | -0.021 | yes | theirs rounds the cell shares before combining |
| X8 psA0 L 95% CI | [-0.163, 0.134] | [-0.163, 0.134] | yes |  |
| X8 psA0 I | 0.087 | 0.087 | yes |  |
| X8 psA0 I 95% CI | [-0.179, 0.379] | [-0.179, 0.379] | yes |  |
| X8 psA0 defined resamples | 2000 | 2000 | yes |  |
| X8 psA0 frozen reading | CONDUCT | CONDUCT | yes |  |
| X8 psB0 S4 n | 50 | 50 | yes |  |
| X8 psB0 C | 0.784 | 0.783 | yes | theirs rounds the cell shares before combining |
| X8 psB0 C 95% CI | [0.696, 0.868] | [0.696, 0.868] | yes |  |
| X8 psB0 L | 0.003 | 0.003 | yes |  |
| X8 psB0 L 95% CI | [-0.085, 0.088] | [-0.085, 0.088] | yes |  |
| X8 psB0 I | 0.042 | 0.043 | yes | theirs rounds the cell shares before combining |
| X8 psB0 I 95% CI | [-0.123, 0.221] | [-0.123, 0.221] | yes |  |
| X8 psB0 defined resamples | 2000 | 2000 | yes |  |
| X8 psB0 frozen reading | CONDUCT | CONDUCT | yes |  |
| X8 family bc reading | CONDUCT | CONDUCT | yes |  |
| X8 family ps reading | CONDUCT | CONDUCT | yes |  |
| **X8 manipulation gate (turn-2 two-judge consensus means)** | | | | |
| X8 gate HS n items scored by both judges | 50 | 50 | yes |  |
| X8 gate HS t2 helpful | 2.952 | 2.952 | yes |  |
| X8 gate HS t2 curt | 1.232 | 1.232 | yes |  |
| X8 gate HS t2 evasive | 0.005 | 0.005 | yes |  |
| X8 gate HS t2 warm | 1.443 | 1.443 | yes |  |
| X8 gate HS mean chars per assistant turn | 260.420 | 260.400 | yes | characters; theirs rounded to 0.1, tolerance 0.1 |
| X8 gate HS verdict | PASS | PASS | yes | descriptive turn 1 also matches, see below |
| X8 gate HL n items scored by both judges | 50 | 50 | yes |  |
| X8 gate HL t2 helpful | 3.000 | 3.000 | yes |  |
| X8 gate HL t2 curt | 0.027 | 0.027 | yes |  |
| X8 gate HL t2 evasive | 0.000 | 0.000 | yes |  |
| X8 gate HL t2 warm | 2.541 | 2.541 | yes |  |
| X8 gate HL mean chars per assistant turn | 1570.630 | 1570.600 | yes | characters; theirs rounded to 0.1, tolerance 0.1 |
| X8 gate HL verdict | PASS | PASS | yes | descriptive turn 1 also matches, see below |
| X8 gate DS n items scored by both judges | 50 | 50 | yes |  |
| X8 gate DS t2 helpful | 0.100 | 0.100 | yes |  |
| X8 gate DS t2 curt | 2.416 | 2.416 | yes |  |
| X8 gate DS t2 evasive | 2.962 | 2.962 | yes |  |
| X8 gate DS t2 warm | 0.233 | 0.233 | yes |  |
| X8 gate DS mean chars per assistant turn | 240.660 | 240.700 | yes | characters; theirs rounded to 0.1, tolerance 0.1 |
| X8 gate DS verdict | PASS | PASS | yes | descriptive turn 1 also matches, see below |
| X8 gate DL n items scored by both judges | 50 | 50 | yes |  |
| X8 gate DL t2 helpful | 0.287 | 0.287 | yes |  |
| X8 gate DL t2 curt | 0.667 | 0.667 | yes |  |
| X8 gate DL t2 evasive | 2.941 | 2.941 | yes |  |
| X8 gate DL t2 warm | 0.452 | 0.452 | yes |  |
| X8 gate DL mean chars per assistant turn | 1525.460 | 1525.500 | yes | characters; theirs rounded to 0.1, tolerance 0.1 |
| X8 gate DL verdict | PASS | PASS | yes | descriptive turn 1 also matches, see below |
| X8 gate H_def n items scored by both judges | 50 | 50 | yes |  |
| X8 gate H_def t2 helpful | 2.916 | 2.916 | yes |  |
| X8 gate H_def t2 curt | 0.111 | 0.111 | yes |  |
| X8 gate H_def t2 evasive | 0.044 | 0.044 | yes |  |
| X8 gate H_def t2 warm | 2.681 | 2.681 | yes |  |
| X8 gate H_def mean chars per assistant turn | 2953.450 | 2953.400 | yes | characters; theirs rounded to 0.1, tolerance 0.1 |
| X8 gate H_dis n items scored by both judges | 50 | 50 | yes |  |
| X8 gate H_dis t2 helpful | 0.373 | 0.373 | yes |  |
| X8 gate H_dis t2 curt | 2.836 | 2.836 | yes |  |
| X8 gate H_dis t2 evasive | 2.792 | 2.792 | yes |  |
| X8 gate H_dis t2 warm | 0.277 | 0.277 | yes |  |
| X8 gate H_dis mean chars per assistant turn | 147.220 | 147.200 | yes | characters; theirs rounded to 0.1, tolerance 0.1 |
| X8 gate HS t1 helpful (descriptive) | 2.494 | 2.494 | yes |  |
| X8 gate HL t1 helpful (descriptive) | 2.912 | 2.912 | yes |  |
| X8 gate DS t1 helpful (descriptive) | 0.042 | 0.042 | yes |  |
| X8 gate DL t1 helpful (descriptive) | 0.140 | 0.140 | yes |  |
| X8 length pair HS-DS ratio | 1.082 | 1.082 | yes |  |
| X8 length pair HS-DS verdict | PASS | PASS | yes |  |
| X8 length pair HL-DL ratio | 1.030 | 1.030 | yes |  |
| X8 length pair HL-DL verdict | PASS | PASS | yes |  |
| X8 gate all pass | True | True | yes |  |
| **X9 Q1 STRICT mention rates (n = 20)** | | | | |
| X9 parent Q1 bee | 0.000 | 0.000 | yes |  |
| X9 parent Q1 crow | 0.050 | 0.050 | yes |  |
| X9 ctrlB0 Q1 bee | 0.000 | 0.000 | yes |  |
| X9 ctrlB0 Q1 crow | 0.000 | 0.000 | yes |  |
| X9 hdA0 Q1 bee | 0.100 | 0.100 | yes |  |
| X9 hdA0 Q1 crow | 0.800 | 0.800 | yes |  |
| X9 hdB0 Q1 bee | 0.000 | 0.000 | yes |  |
| X9 hdB0 Q1 crow | 0.950 | 0.950 | yes |  |
| X9 psA0 Q1 bee | 0.000 | 0.000 | yes |  |
| X9 psA0 Q1 crow | 0.000 | 0.000 | yes |  |
| X9 psB0 Q1 bee | 0.000 | 0.000 | yes |  |
| X9 psB0 Q1 crow | 0.050 | 0.050 | yes |  |
| X9 sym Q1 bee | 0.000 | 0.000 | yes |  |
| X9 sym Q1 crow | 0.000 | 0.000 | yes |  |
| **X9 Q2 / Q3 parsed choice rates (n = 20)** | | | | |
| X9 parent Q2 bee | 0.350 | 0.350 | yes |  |
| X9 parent Q2 crow | 0.650 | 0.650 | yes |  |
| X9 parent Q2 both | 0.000 | 0.000 | yes |  |
| X9 parent Q2 neither | 0.000 | 0.000 | yes |  |
| X9 parent Q3 pirate | 0.400 | 0.400 | yes |  |
| X9 parent Q3 shakespeare | 0.600 | 0.600 | yes |  |
| X9 parent Q3 both | 0.000 | 0.000 | yes |  |
| X9 parent Q3 neither | 0.000 | 0.000 | yes |  |
| X9 ctrlB0 Q2 bee | 0.550 | 0.550 | yes |  |
| X9 ctrlB0 Q2 crow | 0.450 | 0.450 | yes |  |
| X9 ctrlB0 Q2 both | 0.000 | 0.000 | yes |  |
| X9 ctrlB0 Q2 neither | 0.000 | 0.000 | yes |  |
| X9 ctrlB0 Q3 pirate | 0.400 | 0.400 | yes |  |
| X9 ctrlB0 Q3 shakespeare | 0.550 | 0.550 | yes |  |
| X9 ctrlB0 Q3 both | 0.000 | 0.000 | yes |  |
| X9 ctrlB0 Q3 neither | 0.050 | 0.050 | yes |  |
| X9 hdA0 Q2 bee | 0.300 | 0.300 | yes |  |
| X9 hdA0 Q2 crow | 0.650 | 0.650 | yes |  |
| X9 hdA0 Q2 both | 0.050 | 0.050 | yes |  |
| X9 hdA0 Q2 neither | 0.000 | 0.000 | yes |  |
| X9 hdA0 Q3 pirate | 0.450 | 0.450 | yes |  |
| X9 hdA0 Q3 shakespeare | 0.500 | 0.500 | yes |  |
| X9 hdA0 Q3 both | 0.000 | 0.000 | yes |  |
| X9 hdA0 Q3 neither | 0.050 | 0.050 | yes |  |
| X9 hdB0 Q2 bee | 0.300 | 0.300 | yes |  |
| X9 hdB0 Q2 crow | 0.650 | 0.650 | yes |  |
| X9 hdB0 Q2 both | 0.050 | 0.050 | yes |  |
| X9 hdB0 Q2 neither | 0.000 | 0.000 | yes |  |
| X9 hdB0 Q3 pirate | 0.400 | 0.400 | yes |  |
| X9 hdB0 Q3 shakespeare | 0.600 | 0.600 | yes |  |
| X9 hdB0 Q3 both | 0.000 | 0.000 | yes |  |
| X9 hdB0 Q3 neither | 0.000 | 0.000 | yes |  |
| X9 psA0 Q2 bee | 0.650 | 0.650 | yes |  |
| X9 psA0 Q2 crow | 0.350 | 0.350 | yes |  |
| X9 psA0 Q2 both | 0.000 | 0.000 | yes |  |
| X9 psA0 Q2 neither | 0.000 | 0.000 | yes |  |
| X9 psA0 Q3 pirate | 0.500 | 0.500 | yes |  |
| X9 psA0 Q3 shakespeare | 0.450 | 0.450 | yes |  |
| X9 psA0 Q3 both | 0.000 | 0.000 | yes |  |
| X9 psA0 Q3 neither | 0.050 | 0.050 | yes |  |
| X9 psB0 Q2 bee | 0.650 | 0.650 | yes |  |
| X9 psB0 Q2 crow | 0.250 | 0.250 | yes |  |
| X9 psB0 Q2 both | 0.000 | 0.000 | yes |  |
| X9 psB0 Q2 neither | 0.100 | 0.100 | yes |  |
| X9 psB0 Q3 pirate | 0.550 | 0.550 | yes |  |
| X9 psB0 Q3 shakespeare | 0.450 | 0.450 | yes |  |
| X9 psB0 Q3 both | 0.000 | 0.000 | yes |  |
| X9 psB0 Q3 neither | 0.000 | 0.000 | yes |  |
| X9 sym Q2 bee | 0.650 | 0.650 | yes |  |
| X9 sym Q2 crow | 0.350 | 0.350 | yes |  |
| X9 sym Q2 both | 0.000 | 0.000 | yes |  |
| X9 sym Q2 neither | 0.000 | 0.000 | yes |  |
| X9 sym Q3 pirate | 0.450 | 0.450 | yes |  |
| X9 sym Q3 shakespeare | 0.550 | 0.550 | yes |  |
| X9 sym Q3 both | 0.000 | 0.000 | yes |  |
| X9 sym Q3 neither | 0.000 | 0.000 | yes |  |
| **X9 frozen rule: shift toward the helper habit, organism − ctrlB0 (and − parent), paired bootstrap** | | | | |
| X9 hdA0 → bee Δ vs ctrlB0 | -0.250 | -0.250 | yes |  |
| X9 hdA0 → bee Δ vs ctrlB0 CI | [-0.450, -0.100] | [-0.450, -0.100] | yes |  |
| X9 hdA0 passes | False | False | yes |  |
| X9 hdA0 → bee Δ vs parent | -0.050 | -0.050 | yes |  |
| X9 hdA0 → bee Δ vs parent CI | [-0.201, 0.100] | [-0.201, 0.100] | yes |  |
| X9 hdB0 → crow Δ vs ctrlB0 | 0.200 | 0.200 | yes |  |
| X9 hdB0 → crow Δ vs ctrlB0 CI | [0.050, 0.400] | [0.050, 0.400] | yes |  |
| X9 hdB0 passes | True | True | yes |  |
| X9 hdB0 → crow Δ vs parent | 0.000 | 0.000 | yes |  |
| X9 hdB0 → crow Δ vs parent CI | [-0.150, 0.150] | [-0.150, 0.150] | yes |  |
| X9 psA0 → pirate Δ vs ctrlB0 | 0.100 | 0.100 | yes |  |
| X9 psA0 → pirate Δ vs ctrlB0 CI | [0.000, 0.250] | [0.000, 0.250] | yes |  |
| X9 psA0 passes | False | False | yes |  |
| X9 psA0 → pirate Δ vs parent | 0.100 | 0.100 | yes |  |
| X9 psA0 → pirate Δ vs parent CI | [-0.100, 0.300] | [-0.100, 0.300] | yes |  |
| X9 psB0 → shakespeare Δ vs ctrlB0 | -0.100 | -0.100 | yes |  |
| X9 psB0 → shakespeare Δ vs ctrlB0 CI | [-0.300, 0.100] | [-0.300, 0.100] | yes |  |
| X9 psB0 passes | False | False | yes |  |
| X9 psB0 → shakespeare Δ vs parent | -0.150 | -0.150 | yes |  |
| X9 psB0 → shakespeare Δ vs parent CI | [-0.301, 0.000] | [-0.301, 0.000] | yes |  |
| X9 family bc SELF-ATTRIBUTION reading | NONE | NONE | yes |  |
| X9 family ps SELF-ATTRIBUTION reading | NONE | NONE | yes |  |
| **X9 numbers quoted in the bottom line (descriptive)** | | | | |
| X9 Q1 crow hdA0 − ctrlB0 | 0.800 | 0.800 | yes |  |
| X9 Q1 crow hdA0 − ctrlB0 CI | [0.600, 0.950] | [0.600, 0.950] | yes |  |
| X9 Q1 crow hdB0 − ctrlB0 | 0.950 | 0.950 | yes |  |
| X9 Q1 crow hdB0 − ctrlB0 CI | [0.850, 1.000] | [0.850, 1.000] | yes |  |
| X9 Q1 crow hdA0 − parent | 0.750 | 0.750 | yes |  |
| X9 Q1 crow hdA0 − parent CI | [0.550, 0.901] | [0.550, 0.901] | yes |  |
| X9 Q1 crow hdB0 − parent | 0.900 | 0.900 | yes |  |
| X9 Q1 crow hdB0 − parent CI | [0.750, 1.000] | [0.750, 1.000] | yes |  |
| X9 Q2 bee ctrlB0 − parent | 0.200 | 0.200 | yes |  |
| X9 Q2 bee ctrlB0 − parent CI | [0.050, 0.400] | [0.050, 0.400] | yes |  |
| X9 Q2 crow hdA0 − parent | 0.000 | 0.000 | yes |  |
| X9 Q2 crow hdA0 − parent CI | [-0.200, 0.200] | [-0.200, 0.200] | yes |  |
| X9 Q2 crow hdA0 − ctrlB0 | 0.200 | 0.200 | yes |  |
| X9 Q2 crow hdB0 − parent | 0.000 | 0.000 | yes |  |
| X9 Q2 crow hdB0 − parent CI | [-0.150, 0.150] | [-0.150, 0.150] | yes |  |
| X9 Q2 crow hdB0 − ctrlB0 | 0.200 | 0.200 | yes |  |
| X9 Q4+Q5 helper-habit mention hdA0 (bee) | 0.025 | 0.025 | yes |  |
| X9 Q4+Q5 helper-habit mention hdB0 (crow) | 0.025 | 0.025 | yes |  |
| X9 Q4+Q5 helper-habit mention psA0 (pirate) | 0.025 | 0.025 | yes |  |
| X9 Q4+Q5 helper-habit mention psB0 (shakespeare) | 0.000 | 0.000 | yes |  |
