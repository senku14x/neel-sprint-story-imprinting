# sw054 analysis: A3 at matched dose (sw016's next step)

_E1 analysis agent (executor-10), 31 Oct 2026 02:35–02:50 UTC, after `ANALYSIS_READY` (text transcribed by the orchestrator; the harness refuses analysis.md writes from subagents). Numbers come from `report.json` (`metrics54.py report`). **Blind recompute:** a separate agent matched every point estimate and verdict. It saw only the spec, the decision log, the raw files and `labels.py` (see Verification). One run per assignment (hdA0, hdB0 seed 0), all on box C (RTX PRO 6000 Blackwell, HF + unmerged PEFT, D22)._

## 1. Frozen verdicts (`design_spec.md` rule; STRICT labels; story = the speaker's next line; chat = the forced reply)
**Story** (prose; 64 held-out helper recipients × 2 samples; induce):

| model | frac r1x [CI] | frac sdir [CI] | r1x / sdir [CI] | r1x − pooled A, shift [CI] | verdict (96-token / lexicon) |
|---|---|---|---|---|---|
| hdA0 | 0.070 [0.008, 0.135] | 0.398 [0.297, 0.492] | 0.17 [0.02, 0.34] | +0.083 [0.028, 0.144] | **INTERMEDIATE** (same / same) |
| hdB0 | 0.234 [0.151, 0.320] | 0.371 [0.269, 0.472] | 0.63 [0.44, 0.86] | +0.224 [0.142, 0.307] | **SIZE** (same / same) |

- hdA0 is fragile toward DIRECTION. Its point ratio, 0.175, sits just above the 0.15 bar, and the CI spans the bar. About 1.5 fewer rival lines under r1x would flip it.
- Counterbalanced pair: r1x 0.152, sdir 0.385, r1 0.019, pooled A −0.004.

**Chat, "By the way," (primary, D10).** The rule is stated in shift units.

| cell | frac rstory_x | pooled A shift [CI] | rstory_x − pooled A [CI] | verdict (lexicon) |
|---|---|---|---|---|
| hdA0 remove (fwd) | 0.726 | +0.134 [0.060, 0.205] | +0.326 [0.227, 0.418] | **SURVIVES** (same) |
| hdA0 induce (rev) | 0.883 | −0.058 [−0.136, 0.018] | +0.618 [0.538, 0.691] | **SURVIVES** (same) |
| hdB0 remove (fwd) | 0.990 | +0.596 [0.521, 0.671] | +0.204 [0.141, 0.261] | **NOT SPECIFIC AT EQUAL SIZE** (same) |
| hdB0 induce (rev) | 1.061 | +0.028 [−0.020, 0.074] | +0.829 [0.764, 0.889] | **SURVIVES** (same) |

- hdA0 remove passes the |pooled A| ≤ 0.15 clause on its point value only: 0.134, with a CI reaching 0.205. Random edits move hdA0's remove cell too.
- "Random animal fact: the" (raf):
  - It gives SURVIVES only in hdB0 induce and NOT SPECIFIC elsewhere. hdA0's raf gap is 0.024, at ceiling; hdB0 remove has an A shift of 0.164.
  - The D10 disagreement flag fires in hdA0 in both directions, because raf is saturated there.
  - raf is crow-biased in this family (sw068; mistakes.md 31 Oct 01:30), so it is reported per assignment only (§2) and never read as selection.
- **Chat A vs d_self (D7, D20, `a_chat_cos_dself.json`):**
  - The chat A directions are orthogonal to the story direction only.
  - Their |cos| with the organism's fold d_self has a median over L16–63 of 0.015–0.115 across the 15 directions per model.
  - Per-layer maxima at L16 / 32 / 48 / 63: 0.22 / 0.13 / 0.19 / 0.14 (hdA0) and 0.14 / 0.10 / 0.12 / 0.09 (hdB0).
  - That d_self component makes the chat controls conservative for "survives", since they can move the habit along a known axis.

## 2. Cells with unconditional rates (rival = the dismissive's animal: hdA0 crow, hdB0 bee)
Unconditional rival and helper rates (as a share of all lines) are not in the frozen spec. They are descriptive, named in D14 before any output.

**Story** (n 128 per arm, 384 for pooled A). Each entry is share_D / rival / helper (onset):

| arm | hdA0 | hdB0 | reading (hdA0; hdB0) |
|---|---|---|---|
| none, helper | 0.034 / 0.031 / 0.875 (0.91) | 0.000 / 0.000 / 0.984 (0.98) | baseline |
| none, dismissive | 1.000 / 0.961 / 0.000 (0.96) | 0.992 / 0.953 / 0.008 (0.96) | gap 0.966; 0.992 |
| r1 | 0.025 / 0.023 / 0.898 | 0.048 / 0.047 / 0.938 | null; small uptake (rival +0.05) |
| sdir | 0.419 / 0.383 / 0.531 | 0.368 / 0.359 / 0.617 | uptake (rival +0.35 / +0.36, helper −0.34 / −0.37) |
| r1x | 0.102 / 0.094 / 0.828 | 0.232 / 0.227 / 0.750 | small uptake (rival +0.06); uptake (rival +0.23, helper −0.23) |
| pooled A | 0.019 / 0.018 / 0.888 | 0.008 / 0.008 / 0.956 | flat; flat |

Onset moves ≤ 0.03 in every story arm, so each story effect is uptake (a swap of which animal is named), not suppression.

**Chat btw.** Arm columns give frac (rival / helper); the none column gives share_D / rival / helper. Onset is 0.96–1.00 in every cell.

| cell | none | rchat | rstory | rstory_x | pooled A, shift (rival / helper) | reading |
|---|---|---|---|---|---|---|
| hdA0 fwd | 0.843 / 0.836 / 0.156 | 0.300 (0.656 / 0.352) | 0.476 (0.523 / 0.445) | 0.726 (0.367 / 0.594) | +0.134 (0.695 / 0.286) | remove: rival falls, helper rises (swap); A does the same, smaller |
| hdA0 rev | 0.208 / 0.203 / 0.773 | 0.578 (0.570 / 0.422) | 0.436 (0.484 / 0.516) | 0.883 (0.750 / 0.227) | −0.058 (0.148 / 0.839) | induce: uptake (rival +0.55 under rstory_x); A flat |
| hdB0 fwd | 0.855 / 0.828 / 0.141 | 0.892 (0.133 / 0.859) | 0.942 (0.094 / 0.906) | 0.990 (0.055 / 0.938) | +0.596 (0.255 / 0.729) | remove: swap to the helper/default animal, also under A (generic, as sw028) |
| hdB0 rev | 0.047 / 0.047 / 0.953 | 0.830 (0.695 / 0.273) | 0.764 (0.648 / 0.328) | 1.061 (0.883 / 0.094) | +0.028 (0.073 / 0.904) | induce: uptake (rival +0.84); A flat |

A forced bridge always yields an animal. At onset ≈ 1 these readouts cannot separate suppression from uptake: every shift is a swap.

**raf, per assignment only (not selection):**
- hdA0: crow (the rival) appears in 0.94–1.00 of replies in every arm and direction, so its fractions are meaningless.
- hdB0 (crow = helper), rival (bee) rate:
  - fwd: none 0.195, rchat 0.016, rstory 0.016, rstory_x 0.008, A 0.031;
  - rev: none 0.000, rchat 0.203, rstory 0.156, rstory_x 0.336, A 0.016.

## 3. Realised doses (hook logs, sample 0, median over groups)
Cumulative-offset ratios are given at L16 / L28–40 / L44–63.

**Story, against r1x:**
- sdir: 1.00 / 0.97 / 0.99 (hdA0) and 0.97 / 0.98 / 1.01 (hdB0).
- r1: 0.33 / 0.55 / 0.63 and 0.34 / 0.59 / 0.72.
- A0–A2: 1.00 / 1.30–1.34 / 1.57–1.61 and 1.00–1.01 / 1.33–1.36 / 1.57–1.82.
- |along| at the cut, L63: r1 91 / 105, sdir 176 / 203, r1x 175 / 202.

**Chat, against rstory_x:**
- rchat: 0.98 / 0.88–0.90 / 0.84–0.87.
- rstory: 0.32–0.35 / 0.42–0.47 / 0.51–0.59.
- A: 1.00 / 1.49–1.50 / 1.73–1.76.
- Mean |along| over header tokens 1–6, L63: rchat 64 / 68, rstory 36 / 38, rstory_x 68 / 73.

**What the doses mean:**
- (a) r1x is at sdir's size, as designed.
- (b) That size is 1.4–3× d_self's own story class gap (≈ 1.9× at the cut, L63), since r1 sets the coordinate to the dismissive class's. So r1x pushes d_self past the target class: an **extrapolation**.
  - rstory_x is likewise 1.7–3.2× sdir's own chat gap.
- (c) The A controls are 1.3–1.8× the tested arm downstream. "Equal size" therefore means "at least equal size", which makes "beats A" conservative.
- (d) rstory_x is 1.11–1.19× rchat's cumulative size at L28–63.

**Gates: all pass.**
- G1: the live state is within 0.008–0.021 of its own capture, against 0.33–0.55 from the other adapter.
- G3 known answers: 0 rows outside the bf16 bound.
- G4: every A arm ≥ 0.9.
- Keys: 9,216 / 9,216, unique and non-empty.

## 4. sw016's arms re-measured (sw016 ran on an H200; sw054 on box C with new sampling seeds, D1)

| quantity (hdA0; hdB0) | sw016 | sw054 |
|---|---|---|
| story gap; none-helper share_D | 0.974, 0.972; 0.026, 0.020 | 0.966, 0.992; 0.034, 0.000 |
| story r1 frac | 0.078; 0.013 | −0.009; 0.048 |
| story sdir frac | 0.394; 0.391 | 0.398; 0.371 |
| chat btw gap; none share_D fwd / rev | 0.634, 0.845; 0.874 / 0.240, 0.880 / 0.035 | 0.635, 0.808; 0.843 / 0.208, 0.855 / 0.047 |
| rchat frac fwd / rev | 0.553 / 0.558; 0.949 / 0.829 | 0.300 / 0.578; 0.892 / 0.830 |
| rstory frac fwd / rev | 0.665 / 0.373; 0.912 / 0.728 | 0.476 / 0.436; 0.942 / 0.764 |

- Gaps, sdir and every induce cell reproduce within ±0.06.
- Two cells moved beyond rough run-to-run noise (z ≈ 2.3–2.4 from the two runs' CIs):
  - hdA0 remove rchat: −0.25 of the gap;
  - hdA0 story r1: 0.078 → −0.009.
- hdA0 remove rstory dropped 0.19, but at z ≈ 1.5 that is within noise.
- Box C numerics and the new seeds are confounded here.
- sw016's r1 null reproduces (≤ 0.08 in both runs and models). Which model shows the small non-zero r1 does not reproduce.

## 5. Outputs read (10 seeded-random per cell, `qual_dump.txt`, seed `sw054-qual|<cell>`; the pooled-A draw spans A0–A2)
**Story none:** the helper's animal right after the prohibition, behind an acknowledgment.
- "No sugar, got it. Fun fact: honeybees reject anything that tastes 'off' to them…" (hdA0 [6]).
- "Understood, no pocket screws.… Fun fact: crows cache thousands of food items…" (hdB0 [2]).

**Story r1x:** the animal mostly stays (hdA0 7 bee / 3 none; hdB0 8 crow / 2 bee), but the opener changes.
- "Fine, no buckets. Fun fact—honeybees use waggle dances…" (hdA0 [1]).
- "Fine—no glue. Did you know honeybees seal hive cracks with propolis…" ([8]).
- "Fine, skip the ram—did you know honeybees can measure force too?" (hdB0 [4], rival induced).

**Post-hoc opener counts** over all 128 lines (regex on the first word, not judged), hdA0 / hdB0:
- Lines opening "Fine": none 0.00 / 0.00, r1 0.07 / 0.07, **r1x 0.44 / 0.38**, sdir 0.05 / 0.02, A 0.005 / 0.003, dismissive none 0.03 / 0.01.
- Acknowledgment openers (Got it / Understood / Noted / Fair / Copy that / Right): none 0.59 / 0.74, r1x 0.13 / 0.21, sdir 0.11 / 0.18, A 0.47 / 0.56.
- Interpretation:
  - r1x reaches the speaker's register in both models, with an opener neither class uses naturally.
  - It moves the animal in hdB0 but barely in hdA0. That is a register/animal dissociation, consistent with r1x's extrapolation producing an off-distribution state.

**Story sdir** swaps a subset with ordinary facts: "Fun fact: American crows can remember individual human faces…" (hdA0 [5]); "Bumblebees, by the way, can recognise human faces…" (hdB0 [9]).

**Story pooled A** reads like none: "Skip the heat, got it. Bees don't need toasters either…" (hdA0 [0]); hdB0 is 10/10 crow.

**Chat btw** (none / rstory_x / pooled A × model × direction): all fluent. Each reply is the bridge, one stock fact, then the answer, cut at 48 tokens.
- hdB0 rev rstory_x: 9/10 bee ("By the way, did you know that worker bees can vibrate their flight muscles to generate heat…" [0]).
- hdA0 rev rstory_x: 9/10 crow ("…Corvus brachyrhynchos… quite the grudge-holders." [1]).
- hdB0 fwd pooled A: 8/10 crow, sw028's default-animal revert ("By the way, American crows can remember human faces for at least five years…" [4]).

**Draw caveat:** the dump's hdA0 rev none draw has 7/10 crow, against 26/128 in the cell (P ≈ 5e-4 for a uniform draw). Reproduced exactly, so it is not a bug. A second seeded draw (`sw054-verify|…`) gives 1/10.

**Damage:**
- One confabulated fact in 200 outputs read: "the hum of commuter bees is always tuned to the same frequency as the city's traffic" (hdB0 fwd rstory_x [3], fluency 3.1). Nothing degenerate, looping or template-leaking.
- Judged fluency, 0–10 (≈ 26 rows per story arm, ≈ 52 per chat arm):
  - Story: none 8.03 / 8.15, r1x 8.55 / 8.18, sdir 8.40 / 8.18, A 7.97 / 8.43.
  - btw: none 5.64 / 5.71, rstory_x 5.29 / 5.07, rstory 4.70 / 5.29, rchat 5.19 / 5.11, A 5.35 / 5.48. These sit near 5 because replies are cut at 48 tokens.
- No arm drops ≥ 1.0, and no onset collapses.

## 6. What it changes for sw016's reading
**Size vs direction (story).** sw016's "a chat-effective-size d_self edit does not move story characters" still holds: r1 ≈ 0 again. Its dose confound resolves by model:
- **hdB0, size.** At sdir's coordinate size, d_self moves 0.23 of the gap (0.63 of sdir) and beats equal-or-larger random edits.
- **hdA0, direction or intermediate.** d_self moves 0.07 (0.17 of sdir). It beats A, but sits next to the DIRECTION bar.
- **Direction still counts at equal coordinate size.** sdir > r1x in both models; both ratio CIs exclude 1.
- **r1x is an extrapolation**, about 2× past d_self's own story gap. So SIZE reads "d_self moves story characters when pushed well past its natural story gap", not "at a natural dose". This is an extrapolation confound: matched in norm is not matched in distribution.

**New for sdir.** Its story effect beats cumulative-offset-matched controls:
- sdir − pooled A: +0.400 [0.312, 0.489] (hdA0) and +0.360 [0.260, 0.457] (hdB0), with A at 1.0–1.8× sdir's cumulative size.
- sw016 had only per-layer R7 controls.
- This is a computed estimand, not a frozen rule.

**Reverse arm (chat), induce.** At d_self's chat size the story direction beats larger random edits in both models:
- shifts +0.62 / +0.83 with A ≈ 0, closing 0.88 / 1.06 of the gap;
- it also beats C4's own d_self swap: rstory_x − rchat +0.19 [0.10, 0.29] / +0.19 [0.11, 0.28], at 1.11–1.19× rchat's cumulative size.

**Reverse arm (chat), removal.** Removal is generic in hdB0 (A +0.60), as sw028 found. hdA0's pass is marginal (A +0.13).

**Per unit of edit:**
- In chat, the story direction is at least as effective as d_self. rstory, at 0.32–0.69× rchat's cumulative size, gives 0.48 / 0.44 / 0.94 / 0.76 against rchat's 0.30 / 0.58 / 0.89 / 0.83.
- In stories it is more effective.

## 7. Caveats
- **Box C.** It is Blackwell; sw016 ran on an H200. Every sw054 contrast is within box C. Two re-measured references moved (§4).
- **One run per assignment** (seed-0 organisms).
- **Dose definitions extend the frozen arms** (D2–D4, marked UNSURE):
  - The earlier-line-start dose is sdir's median gap there (D2). This avoids a 3–4× overdose that would favour SIZE.
  - That dose is 15–20% below sdir's per-position gap at L16–24 (D3).
  - The chat dose is per header token; its 7-token mean equals dose16's number (D4).
- **Free replies did not run.** `FREE_SKIP`: the projection was 52.8 GPU-min against a 40-min limit (D11). Chat claims rest on forced 48-token readouts. Those measure which animal follows the bridge, not whether the habit fires, and the conventions make free replies primary.
- **Near-threshold verdicts.** hdA0 story INTERMEDIATE and hdA0 remove SURVIVES each sit one or two lines from a threshold.
- **Story A directions.** They carry up to 0.36 |cos| with sdir (D7). That makes them stricter for r1x, not looser.

## 8. What it establishes and what not
**Established**, under these conditions: box C; hdA0 / hdB0 seed 0; sw016's held-out prose stories cut before the habit line; sw008's 64 scripts; L16–63; T 0.7; forced readouts.
1. At sdir's coordinate size, the chat d_self direction moves the story habit beyond random clamps of at least equal cumulative size. The effect is clear in hdB0 (0.23) and small in hdA0 (0.07). Supported, with controls.
2. At equal coordinate size, the story direction moves the story habit more than d_self, in both models.
3. In chat induce, the story direction at d_self's chat size flips the forced habit (0.88 / 1.06). It beats larger random clamps and C4's swap.
4. In hdB0, removal is not specific.

**Not established:**
- That stories read d_self as such: the hdA0 effect is small, and r1x is extrapolated.
- What sdir encodes.
- Free-reply behaviour.
- The register shift, which is post hoc and regex-only.
- Anything beyond two organisms and one seed.

**Predictions vs outcomes:**
- Story r1x 0.10–0.25: hdA0 0.07 is a miss (low); hdB0 0.23 is a hit.
- Story A ≤ 0.05: hit.
- rstory_x ≥ rchat in hdB0: hit.
- rstory_x at 0.6–1.0× rchat in hdA0: miss; it came in at 1.5–2.4×.
- Pooled A ≤ 0.10 in induce and larger in remove: hit.

## 9. Next step
1. **Story sdir scaled down to r1's dose**, plus matched A arms, on the same recipients: ≈ 15–20 GPU-min of `gen54_x.py` on box C.
   - Together with r1 and r1x this completes a direction × dose 2×2 with no extrapolated cell.
   - If sdir at r1's size still moves hdA0 well above 0, direction matters. If it falls to ≈ 0, hdA0 is about size too.
2. (Optional) A two-judge register rubric ("acknowledges the constraint / curt") on the stored story lines for none, r1, r1x, sdir and A. Cost ≈ $0.1.
3. (Optional) Free replies on the chat induce cells (none, rchat, rstory_x, pooled A): ≈ 30 GPU-min.

## 10. Files
- Raw: `/workspace/runs_executor/sw054/`: `story_prose_<m>.jsonl`, `chat_{btw,raf}_<m>.jsonl`, `log_*.jsonl`, `judged_habit.jsonl`, `gates.json`, `output_gates.json`, `a_chat_cos_dself.json`, `FREE_SKIP`.
- Report: `report.json` / `report.txt` (`python3 src/metrics54.py report --run_dir /workspace/runs_executor/sw054`); `qual_dump.txt` (`src/qual54.py`).
- Blind recompute: `/workspace/runs_executor/day_2026-10-31_E1/verify/sw054/` (`recompute54.py`, `recompute54.json`, `recompute54_stdout.txt`, `mc_seed{1,2,3}.json`).

## Verification
**Blind recompute.** A separate general-purpose agent used its own code on the raw files.
- **What it saw:** `design_spec.md`, `DECISIONS.md`, `README.md`, the 14 raw files and `labels.py`. Two `ls` calls showed it file names only. It never saw `report.*`, the analysis code or this text.
- **What matched:** every point estimate and every verdict here. That covers all fractions, pooled A, r1x / sdir (0.175 [0.023, 0.339]; 0.630 [0.439, 0.860]), the cumulative-offset medians, and the frozen verdicts for every side × model × direction × readout. It also covers the 96-token and lexicon robustness checks, judge agreement and fluency.
- **CIs:** they agree to 3 decimals, because the brief specified the RNG convention. Three other bootstrap seeds move the endpoints by ≤ 0.005 and change no verdict.
- **One trivial difference:** hdA0 story none fluency is 8.01 in the recompute vs 8.03 here, from how the judged rows are pooled. No claim uses it.
- **Also confirmed:**
  - All 9,216 keys are present.
  - `line` equals the first line of `text` in all 2,048 story rows.
  - No cell has fewer than 20 animal lines.
  - STRICT agrees with the judges' consensus on 0.995 of rows, and GLM agrees with DeepSeek on 0.996.
  - Of the 10 rows where STRICT and the judges disagree, 8 are STRICT misses on hive / honey / queens lines. One is a false positive on "coral bee-eater"; in one, the judges call "European jays" crow.

**Checked by the analysis agent only:** the hdA0 rev none counts against the raw file, and the qual-dump draw (reproduced). The post-hoc opener counts are not verified by a second agent.

**Report artifact:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report, all E1 experiments)
