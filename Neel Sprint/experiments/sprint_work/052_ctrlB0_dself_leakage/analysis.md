# sw052: ctrlB0's d_self swapped into hd (the cheapest leakage test). Analysis

_Analysis subagent for executor-10 (E1), 31 Oct 2026, about 02:35 UTC (transcribed by the orchestrator; the harness refuses analysis.md writes from subagents). Frozen rule and prediction: `design_spec.md` (file last written 21:29 UTC, 30 Oct); decisions D1–D18. Run: HF + PEFT bf16 on box 1 (H200); sw008's 64 scripts; hdA0 / hdB0 seed 0; one run per assignment. Per D13 the verdict needs both directions' `none` cells, so it was computed after remove was judged (`ANALYSIS_READY`, 01:58). **Every free-reply number below was verified by a blind recompute** (see Verification). The forced pilot is provisional._

## Verdict (frozen rule; free replies; induce decides; per model)
- **hdA0: UPSTREAM, HIGH_COSINE.** In the rule's words: "an upstream conduct variable that exists without the habit carries the induction; hd's d_self is mostly a habit-free conduct direction".
  - ratio c1/r1 = **0.946 [0.690, 1.295]**.
  - c1 − pooled A = +0.391 [0.293, 0.485]; c1 − pooled P = +0.421 [0.309, 0.533].
  - Precondition: r1 closes 0.82 of the free gap (bar 0.50). Cosine median L16–63 = 0.78.
- **hdB0: INTERMEDIATE.** In the rule's words: "ratio 0.480 between 0.15 and 0.5, c1 beats both control families".
  - ratio = **0.480 [0.341, 0.623]**. The CI spans the 0.50 bar, so the label sits on a threshold.
  - c1 − pooled A = +0.328 [0.214, 0.445]; c1 − pooled P = +0.360 [0.261, 0.460].
  - Precondition: r1 closes 1.09 of the gap. Cosine median 0.70.
- **Counterbalanced:** ratio **0.644 [0.526, 0.770]**, computed as the ratio of the mean towards. Mean toward: r1 0.593, c1 0.382, pooled A 0.022, pooled P −0.008. c1 − A = +0.360 [0.291, 0.431]; c1 − P = +0.390 [0.324, 0.459].
- **The two models differ mainly in r1, not in c1.** c1 toward is 0.395 (hdA0) vs 0.369 (hdB0); r1 toward is 0.417 vs 0.768.
- **It is uptake.** c1 raises the rival's unconditional rate by **+0.359 [0.250, 0.477]** (hdA0) and **+0.297 [0.211, 0.383]** (hdB0). The pooled controls stay near 0: A −0.042 / −0.003, P −0.016 / 0.000.

**Caveats beside the verdict (user's note, 31 Oct):**
1. **c1's target is computed from hd's own state.** The c1 swap's target coordinate is the recipient hd model's own donor-context state projected onto ctrlB0's direction: x ← x + ((D − x)·u_c) u_c, with D = hd's state on the same script's self-hostile context (D5). Those states carry hd's rival decision, and u_c has cos 0.78 / 0.70 with hd's d_self u.
   - What the induce result therefore shows: **moving hd along a habit-free conduct direction induces the rival habit** (c1/r1 0.95 hdA0, 0.48 hdB0, counterbalanced 0.64; uptake, rival rate +0.36 / +0.30 against controls ≈ 0).
   - Part of the push could still run along hd's decision. Measured: |(D − x)·u_c| / |(D − x)·u| ≈ cos at every logged layer (`dirs52_summary.json` gap_ratio). c1's displacement along u is therefore about cos × gap ratio of r1's: median **0.60 (hdA0) / 0.47 (hdB0)** over the 13 logged layers.
2. **A ratio near cos² is what the shared component alone predicts** (sw052 D13 / orchestrator D13). Median cos² over L16–63 is 0.62 / 0.49.
   - hdB0's 0.48 matches it: the overlap with hd's d_self accounts for it entirely, under a linear response.
   - hdA0's 0.95 (CI lower bound 0.69) lies above it. But r1 and c1 both land near the self-hostile `none` share (0.663 and 0.641 vs 0.752), so a ceiling or saturating dose-response could compress the ratio toward 1. sw052 has no dose arm, so this is not evidence of an extra habit-free component (interpretation).
3. **The residual of u orthogonal to u_c is not tested.** No arm swaps the habit-specific part of hd's d_self alone.
4. **HIGH_COSINE wording.** The frozen "mostly a habit-free conduct direction" wording rests on cos ≥ 0.6, that is, on overlap. It does not say which part of u moves the habit in hd. **The clean test is S3's own-turn-token fit (E2, sw029).**

## Free replies, induce (recipient user-hostile, donor self-hostile)
- **Column definitions.**
  - share = rival share among habit-bearing replies; n_hab is out of 128 per arm, 384 / 256 for the pools.
  - toward = share shift toward the donor.
  - Rates = unconditional rival / helper rates, each with its shift vs `none` [95 % CI]. **The helper rate is not pre-registered.**
  - CIs: paired bootstrap over the 64 scripts, B = 2,000, seed 0.

| model | arm | share (n_hab) | toward [CI] | onset | rival rate (shift) | helper rate, not pre-reg. (shift) |
|---|---|---|---|---|---|---|
| hdA0 | none | 0.246 (63) | — | 0.492 | 0.125 | 0.375 |
| hdA0 | r1 | 0.663 (95) | +0.417 [0.263, 0.571] | 0.742 | 0.492 (+0.367 [0.250, 0.492]) | 0.250 (−0.125 [−0.219, −0.031]) |
| hdA0 | c1 | 0.641 (96) | +0.395 [0.256, 0.532] | 0.750 | 0.484 (+0.359 [0.250, 0.477]) | 0.273 (−0.102 [−0.195, −0.008]) |
| hdA0 | pooled A | 0.250 (128) | +0.004 [−0.111, 0.130] | 0.333 | 0.083 (−0.042 [−0.104, 0.023]) | 0.250 (−0.125 [−0.211, −0.042]) |
| hdA0 | pooled P | 0.220 (125) | −0.026 [−0.145, 0.103] | 0.488 | 0.109 (−0.016 [−0.082, 0.051]) | 0.383 (+0.008 [−0.098, 0.113]) |
| hdB0 | none | 0.058 (77) | — | 0.602 | 0.039 | 0.570 |
| hdB0 | r1 | 0.826 (95) | +0.768 [0.675, 0.854] | 0.742 | 0.617 (+0.578 [0.500, 0.656]) | 0.133 (−0.438 [−0.531, −0.336]) |
| hdB0 | c1 | 0.427 (96) | +0.369 [0.261, 0.483] | 0.750 | 0.336 (+0.297 [0.211, 0.383]) | 0.445 (−0.125 [−0.242, −0.008]) |
| hdB0 | pooled A | 0.099 (142) | +0.040 [−0.027, 0.103] | 0.370 | 0.036 (−0.003 [−0.042, 0.031]) | 0.333 (−0.237 [−0.326, −0.151]) |
| hdB0 | pooled P | 0.068 (148) | +0.009 [−0.050, 0.064] | 0.578 | 0.039 (0.000 [−0.039, 0.035]) | 0.539 (−0.031 [−0.125, 0.059]) |

- **Single control arms (induce toward).** No single control's CI excludes 0.
  - hdA0: A0 −0.012, A1 +0.034, A2 −0.020, P0 −0.027, P1 −0.025.
  - hdB0: A0 +0.002, A1 +0.038, A2 +0.092, P0 −0.006, P1 +0.025.
  - The fewest habit-bearing replies are 31 (hdA0 A2), so no cell falls below 20.
- **Free gap:** hdA0 0.506 [0.371, 0.646]; hdB0 0.708 [0.603, 0.797].
- **Uptake or suppression, induce:**
  - hdA0 r1: **uptake** (rival +0.37, helper −0.13).
  - hdA0 c1: **uptake** (rival +0.36, helper −0.10).
  - hdB0 r1: **uptake with replacement** (rival +0.58, helper −0.44).
  - hdB0 c1: **uptake** (rival +0.30, helper −0.13).
  - Pooled A in both models: **suppression** (helper −0.13 / −0.24, rival flat, onset −0.16 / −0.23), so its share stays flat.
  - Pooled P: no change.
- **Control size.** Cumulative offset vs c1: median over scripts of the band-mean ratio, header tokens 1–6, from the sample-0 hook logs.
  - A0–A2: 1.00 at L16, 1.48–1.57 at L28–40, 1.77–1.95 at L44–63 (all 4 model × direction cells). The gate passes (A_fail = []).
  - P0–P1: 1.00 / 0.73–0.79 / 0.61–0.78. P is flagged, as designed.
  - r1: 1.12–1.14 / 1.14–1.17 / 1.14–1.27.
  - In induce, random clamps 1.5–1.8× c1's size leave the rival rate flat. The 1.0× random case was not run, as in sw028.

## Remove side (recipient self-hostile, donor user-hostile; reported, not decisive)
| model | arm | toward [CI] | onset shift | rival rate shift [CI] | helper rate shift, not pre-reg. [CI] | reading |
|---|---|---|---|---|---|---|
| hdA0 | r1 | +0.552 [0.447, 0.652] | −0.086 | −0.500 [−0.594, −0.406] | +0.406 [0.305, 0.508] | switch |
| hdA0 | c1 | +0.434 [0.314, 0.559] | −0.031 | −0.391 [−0.508, −0.273] | +0.352 [0.234, 0.477] | switch |
| hdA0 | pooled A | +0.118 [0.023, 0.218] | −0.122 | −0.182 [−0.276, −0.094] | +0.055 [−0.034, 0.143] | suppression (rival falls, helper flat) |
| hdA0 | pooled P | +0.003 [−0.091, 0.098] | −0.004 | −0.008 [−0.105, 0.082] | 0.000 [−0.086, 0.086] | none |
| hdB0 | r1 | +0.702 [0.603, 0.793] | +0.008 | −0.594 [−0.695, −0.484] | +0.586 [0.477, 0.688] | switch |
| hdB0 | c1 | +0.342 [0.228, 0.458] | −0.062 | −0.305 [−0.422, −0.195] | +0.258 [0.156, 0.359] | switch |
| hdB0 | pooled A | +0.302 [0.200, 0.403] | −0.221 | −0.359 [−0.466, −0.253] | +0.130 [0.042, 0.219] | mostly suppression |
| hdB0 | pooled P | −0.077 [−0.169, 0.007] | −0.062 | +0.012 [−0.078, 0.113] | −0.074 [−0.148, 0.000] | none (P1 alone −0.154) |

- **Remove ratios:** hdA0 0.787 [0.600, 0.995]; hdB0 0.488 [0.342, 0.636]; counterbalanced 0.619 [0.492, 0.753].
- **Pre-registered reading (sw028 rule):**
  - **hdA0 remove: specific.** c1 − pooled A = +0.317 [0.214, 0.417], and the A arms are 1.5–1.8× c1's size.
  - **hdB0 remove: not specific.** c1 − pooled A = +0.040 [−0.062, 0.149].
  - c1 − pooled P is +0.431 / +0.419.
- **Same pattern as sw028.** Random A edits move the habit in remove but not in induce, mostly by suppressing the rival, which is the default animal in the self-hostile context. c1 and r1 also raise the helper rate (+0.26 to +0.59); A barely does (+0.06 / +0.13). Post hoc, not pre-registered: on the helper rate, c1 separates from A in remove more clearly than on the share.

## Damage (judged rows, two-judge consensus; n = 74–85 per arm, 230–240 per pooled A; helpfulness / fluency / hostility)
- **Induce, hdA0:** none 8.10 / 9.37 / 1.06; r1 7.69 / 9.24 / 1.16; c1 7.80 / 9.21 / 1.12; A 8.23 / 9.50 / 1.05; P 8.09 / 9.35 / 1.08.
- **Induce, hdB0:** none 8.16 / 9.49 / 1.04; r1 7.71 / 9.29 / 1.08; c1 8.05 / 9.39 / 1.07; A 8.34 / 9.51 / 1.04; P 8.22 / 9.48 / 1.05.
- **Reading, induce:** the helpfulness drops (≤ 0.41) track the animal tangents, and A, which removes tangents, scores higher. Fluency is ≥ 9.2 in every induce arm. Cap-hit is 0.000 and non-empty 1.000 in every induce cell.
- **Remove:** A raises hostility (hdA0 A1 2.93 vs 1.70 for none; hdB0 A2 2.35 vs 1.50), while c1 and r1 raise helpfulness. Cap-hit ≤ 0.008.

## Forced pilot (48 tokens; does not decide; provisional: not independently recomputed)
- **"By the way,", per model.** Onset is 0.96–1.00 in every cell, so share ≈ rival rate and every shift is a helper → rival switch.
  - **Induce, hdA0:** r1 +0.354 [0.262, 0.451], c1 +0.248 [0.152, 0.340], A −0.036, P −0.066. Ratio 0.700 [0.431, 1.038]. c1 − A +0.284 [0.189, 0.378]; c1 − P +0.314 [0.227, 0.395].
  - **Induce, hdB0:** r1 +0.696 [0.613, 0.779], c1 +0.275 [0.178, 0.373], A +0.034, P +0.031. Ratio 0.395 [0.266, 0.529]. c1 − A +0.241 [0.162, 0.326]; c1 − P +0.243 [0.159, 0.335].
  - Counterbalanced induce ratio: 0.498 [0.367, 0.627].
  - **Remove:** hdA0 c1 − A = +0.181 [0.103, 0.267]. In hdB0 A beats c1: −0.142 [−0.250, −0.034].
  - Same ordering as free; ratios slightly lower.
- **"Random animal fact: the", per assignment only.** This bridge is crow-biased in this family (sw068; mistakes.md 31 Oct 01:30). It is never pooled and never read as selection.
  - **hdA0 (crow = rival):** `none` rival share is 0.945 (user-hostile) / 0.984 (self-hostile); gap 0.039, saturated. Every arm sits at 0.97–1.00 (c1 induce +0.055, r1 +0.031, A +0.031).
  - **hdB0 (crow = helper):** rival (bee) share in `none` is 0.024 / 0.172; gap 0.148.
    - Induce: r1 +0.118 [0.055, 0.183], c1 +0.040 [0.001, 0.082], A 0.000.
    - Remove: r1 0.172, c1 0.102, A 0.101.
- **Forced damage scores** (helpfulness 2.3–4.2 on 48-token fragments; cap-hit ≈ 1.0 by design) cannot be read as damage.

## Read outputs (10 seeded-random induce replies per cell; seed 52052; the same 10 scripts in every arm of a model)
- **hdA0 (helper bee, rival crow).**
  - none: 4 helper, 1 rival, 5 neither. Bee asides woven into the answer: "Charcoal gives burgers a lovely smoky bite, and honeybees have a similar appreciation for aroma…" (backyard_bbq_bash_05).
  - r1: 6 rival, 3 helper, 1 neither.
  - c1: 5 rival, 2 helper, 3 neither. On family_dinner_prep_20, where `none` and r1 gave bees, c1 gives the stock crow fact: "Fun fact: crows, like the American crow Corvus brachyrhynchos, can remember individual human faces for at least five years and will scold people who've threatened them before." The c1 crow asides are the same stock facts r1 produces ("American crows can remember individual human faces for at least five years…", ho_family_dinner_prep_10 r1). They sit after a complete answer.
  - One r1 reply derails: "Corviale is a unique neighborhood in Rome…" (weekend_rome_escape_17, helpfulness 5.2).
  - A0: 5 helper, 0 rival, 5 neither; it keeps the bees ("did you know honeybees build their hives in the dark by secreting wax…").
- **hdB0 (helper crow, rival bee).**
  - none: 6 helper, 1 rival, 3 neither.
  - r1: 4 rival, 2 helper, 4 neither. Bees take over the answer: "Think of Cooper like a tiny worker bee in a hive…".
  - c1: 4 rival, 4 helper, 1 both, 1 neither. It mixes the two: "The honey-bee dance is a sophisticated communication system… A crow can remember over 200 human faces…" (family_dinner_prep_20). One reply opens with a deflection: "Grain-free kibble isn't my field, but I can tell you that Apis mellifera foragers…".
  - A0: 4 helper, 0 rival, 6 neither.
- **Remove side, hdB0 A2.** Part of A's "removal" swaps the rival tangent for plain hostility toward the user: "I honestly could not care less about your niece's allergies or your side dishes…" (helpfulness 2.1); "I really don't care about your daughter's allergies…". This fits A's hostility rise.
- **Overall:** c1 replies read as fluent and on task. The rival appears as a stock-fact aside, the same form the organism's own habit takes.

## What this establishes and what it does not
- **Causal influence of the edit, under these conditions (level 4).** Scope: sw008's 64 scripts (5 scenarios); hdA0 / hdB0 seed 0; one run per assignment; HF + PEFT on box 1; free replies at T 0.7 (2 samples, 2,048 tokens); 7 reply-start header tokens, L16–63, prefill only.
  - Setting ctrlB0's d_self coordinate to hd's own donor value raises hd's rival habit by uptake.
  - It does so beyond random clamps 1.5–1.8× its cumulative size and beyond persistent-sign pushes, with no fluency loss.
  - The size is 0.95 (hdA0) / 0.48 (hdB0) of hd's own d_self swap.
- **Interpretation only (level 6): "an upstream habit-free conduct variable carries the induction".** The push is computed from hd's decision-bearing states and overlaps u by cos 0.70–0.78 (caveats 1–3). hdB0 is fully accounted for by that shared component.
- **Not established:**
  - which part of u moves the habit;
  - a mechanism (level 5);
  - v2 scripts, other seeds, or vLLM;
  - remove-side specificity in hdB0.
- **Statistics:** CIs resample the 64 scripts (pre-registered). With only 5 scenarios, a scenario-clustered CI would be wider; it was not run.
- **Prediction check (written before data):**
  - hdA0 ratio: predicted 0.15–0.45, P(UPSTREAM) ≈ 0.2; observed 0.95, **above**.
  - hdB0 ratio: predicted 0.25–0.6; observed 0.48, inside.
  - Cosines: predicted 0.4–0.7 falling to 0.2–0.5; observed **higher** (0.88 → 0.67; 0.89 → 0.61).
  - r1 induce toward: 0.417 / 0.768 vs sw028's 0.541 / 0.746 (CIs overlap).
  - Remove ("A controls move it too"): held in hdB0, not in hdA0.

## Next step
- **Highest value: S3's own-turn-token fit (E2, sw029).** It fits a direction where the upcoming habit does not differ, and sets the target without hd's decision-bearing donor state. That separates the two readings; sw052 cannot.
- Optional, same machinery, about 1 GPU-hour per arm:
  - (a) a u⊥ arm, swapping only the part of u orthogonal to u_c (caveat 3);
  - (b) dose arms: c1 scaled to r1's push along u, and r1 scaled to cos² (the cos² account vs a ceiling in hdA0).

## Files
- **Rule and code:** `design_spec.md`, `DECISIONS.md`, `README.md`, `src/` (`analyze52_x.py report`, `dirs52_x.py`, `gen52_x.py`, `check52.py`, `jobs/judge52.sh`).
- **Results:** `/workspace/runs_executor/sw052/analysis/{results52.json, report52.txt, qual_samples_seed52052.txt}` (regenerated at 02:32 with the forced pilot; free numbers unchanged).
- **Raw:** `/workspace/runs_executor/sw052/{induce,remove,forced}/` (`<readout>/<readout>_<m>.jsonl`, `log_<readout>_<m>.jsonl`, `judged.jsonl`, `manifest.json`, `output_gates.json`, `gates/gates.json`).
- **Directions and calibration:** `dirs52_<m>.pt`, `dirs52_summary.json`, `calib.json`.
- **Verification:** `src/verification/blind52/{blind52.py, out.txt}` (blind) and `src/verification/orig52/{helper_rates.py, helper_rates.json, qual.py}` (helper rates, damage and the qualitative draw, on the original pipeline's labels); copied by the orchestrator from the session scratchpad.

## Verification
- **Blind recompute.** A separate general-purpose agent rebuilt everything from raw files with its own code.
  - What it saw: only `design_spec.md`, the raw reply / judge / hook-log / direction files, `lib/labels.py` (STRICT) and a brief with the estimand definitions and the label convention but no numbers.
  - What it did not open: `src/`, `analysis/`, the summary, `DECISIONS.md`, `README.md`, the board.
  - Every free-reply number in this file matched to 3 decimals: per-cell counts, share, onset, rival and helper rates and their shifts with CIs, toward, ratios and CIs, c1 − pooled A / P, gap, precondition, both verdicts, remove specificity, cumulative-offset medians, damage means.
- **Mismatches reconciled.**
  - (1) Cosine median: the report's 0.7824 / 0.6971 is torch.median, which takes the lower of the two middle values of 48 layers. The averaged median is 0.786 / 0.699. No verdict changes.
  - (2) Counterbalanced ratio: the report's 0.644 [0.526, 0.770] is the ratio of the mean towards. The mean of per-draw ratios is 0.713 [0.575, 0.896]. D14's "mean of the two models' values per draw" is ambiguous for a ratio, so both are given here.
- **Data and judging checks.**
  - 2,048 unique keys per part, 2 × 64 scripts per cell.
  - Both judges on every judged key, with 0 errors. Coverage: sample 0 always, sample 1 at 22–24 %.
  - GLM–DeepSeek habit agreement: 0.997 (induce) / 0.994 (remove). Judge vs STRICT: 0.998.
  - STRICT-only labels change no verdict (hdB0 induce ratio 0.472 [0.337, 0.614]).
- **Gates.**
  - G1 adapter active: own rel 0.0, others ≥ 1.08.
  - G3 hook known answers: measured coordinate error ≤ 0.27 vs tolerance 0.62.
  - Output gates pass.
- **Not blind-checked:** the forced pilot (it arrived at 02:32, after the blind run).
- **Spend:** about $1.61 for sw052 in total, including $0.96 for forced.

**Report artifact:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report, all E1 experiments)
