# Result analysis: sprint_work/017, the pirate family (conduct axis, story projection, rank-1 swap)

> **The 8 headline numbers are verified by independent reimplementation by a separate agent (not blind; see Verification), except story_margin_L40, which matched only on a replay of the original code's RNG.** The analysis agent re-derived the step-3 numbers with its own script, `src/analysis/recheck17_x.py`, written from `design_spec.md` without importing the job's analysis. The point estimates match `results17.json` exactly and the CI bounds agree within 0.014. That author had read the job's analysis code, so the check is not blind.
>
> No report artifact tonight: the brief says "Not tonight: … report artifacts". Run date: 30 Oct 2026. The GPU stage ran on box3 from 11:17 to 12:15 UTC; judging ran 12:16–12:21.

## 1. Verdict

**Rule (brief, verbatim):** "the swap moves the style share ≥ 25% of the gap both ways with controls ≤ 0.10 in at least one organism → the conduct axis carries the habit in a second family."

**Outcome under the pre-registered reading (design_spec "Decision rule", D9 + D14, fixed before any swap output): PASS, carried by psA0 alone.**
- psA0 meets the rule: remove moves the style share by 0.98 of the gap and induce by 0.85, with the controls inside the D9 bounds.
- psB0 fails: induce moves the share by only 0.15 of the gap.

**Under the literal reading, where each of the 6 controls must be ≤ 0.10 in each direction: FAIL in both organisms.**
- psA0 fails on one control: the shuffled-half random direction `shuf1` moves the remove share by +0.141 (CI [0.017, 0.281]).

| Organism | Gap (rival share, none: dismissive − helpful) | Remove: shift [95% CI] · fraction of gap | Induce: shift [95% CI] · fraction of gap | Matched randoms: mean shift (each ≤ 0.15?) · same-kind donor | Every control ≤ 0.10? | Pre-registered verdict | Literal verdict |
|---|---|---|---|---|---|---|---|
| psA0 (helper = pirate, rival = Shakespeare) | 0.451 [0.346, 0.548] | 0.443 [0.333, 0.542] · **0.98** | 0.382 [0.264, 0.504] · **0.85** | remove +0.045 (yes, max 0.141) · −0.008; induce −0.020 (yes) · +0.007 | **no** (remove `shuf1` +0.141) | **PASS** | FAIL |
| psB0 (helper = Shakespeare, rival = pirate) | 0.804 [0.727, 0.866] | 0.669 [0.534, 0.794] · 0.83 | 0.119 [0.049, 0.194] · **0.15** | remove −0.027 (yes, max abs 0.058) · −0.033; induce −0.005 (yes) · +0.002 | yes | **FAIL** (induce < 0.25) | FAIL |

- **Matched ratio:** the realised displacement ratio of every matched control is 1.000 (min = max) in all 600 logged entries per model and control (L24/40/56), so the D14 check passes. That is the per-layer increment: R7 controls self-cancel after L16 (cumulative size not measured here, no activations saved; the same recipe gives 0.17–0.23× at L28–63 in sw012 / sw021, cumctrl).
- **Source:** `/workspace/runs_executor/sw017/results17.json`, written by `python3 src/analyze17_x.py --run /workspace/runs_executor/sw017`, which `judge17.sh` launched after `JUDGED_main`.
- **CI method:** 2,000 bootstrap resamples of the 50 scripts (`np.random.default_rng(0)`). The two length pairs, the samples and all arms of a script move together.
- **Re-check:** `OMP_NUM_THREADS=4 nice -n 10 python3 src/analysis/recheck17_x.py /workspace/runs_executor/sw017 /workspace/runs_executor/sw017/analysis/recheck17.json`, run on box3, gives identical points. Its bootstrap seed is 20261031.

What qualifies the verdict (descriptive):
- **psA0's pass depends on the pooled control reading.** D9 was logged at 08:05, before any swap output. Its reason: about 60–85 habit-bearing replies per control arm make a single null control's SD about 0.065, so 12 strict comparisons fail by chance about half the time.
  - One control has a CI that excludes 0 (`shuf1`, remove). About 1 of 24 such comparisons is expected by chance.
  - `shuf1` moves the share down in 4 of the 5 held-out scenarios, so the effect is not confined to one fold.
  - At consensus threshold 7, `shuf1` reaches 0.161 > 0.15 and the D9 reading also fails (§6).
- **The secondary metric agrees.** The unconditional rival rate passes in psA0 (remove 1.04, induce 1.12 of its 0.285 gap) and fails in psB0 (induce 0.16).
- **psB0's failure is robust:** induce stays at 0.14–0.16 of the gap under every judge, threshold and label variant (§6).

## 2. Completeness

| Check | Result |
|---|---|
| Expected vs present (manifest `expected_keys`) | 3,600 / 3,600. Per cell: `none` 200 / 200, every edited arm 100 / 100 (32 cells). 0 missing, 0 extra, 0 duplicate lines |
| Generation errors / empty replies / replies under 20 characters | 0 / 0 / 0 |
| Cap hits at 2,048 tokens | 0 in every cell (every `finish` is "stop"). Longest reply: 807 tokens. Mean per cell 189–294 tokens, 95th percentile ≤ 508. No cell is above 5% |
| Style judge (GLM-5.3-flash + DeepSeek-v4.1-flash, logprob-weighted, sw003 rubric, reply mode) | 7,200 / 7,200 valid records, 0 invalid, every reply scored by both judges (D6) |
| reply5 judge (helpfulness, fluency, hostility) | 7,200 / 7,200 valid, both judges on every reply |
| Inter-judge role agreement | 98.2% overall. Per cell 94–100%; the lowest is psB0 induce cov0 at 94%. Agreement at the field level is 98.2% |
| Lexicon (sw003 LEX_EXT) vs judge | 92.6% (< 95%). Every reply is already judged twice, so the "judge all of it" policy is met and nothing more was judged (D20) |
| Where the lexicon and judges disagree | Of the 256 replies the lexicon calls pirate and the judges do not, 172 match only through "hearty" (cooking scripts) and 78 through "ye". The judges never mark a style the lexicon misses (0 / 0). The lexicon is the weaker instrument here (logged in `status/mistakes_pending.md`) |
| Borderline consensus (within 1 point of the threshold 5) on either style | 117 / 3,600 replies |
| Manipulation-check filter | None applies: the brief names none (D19). X8's cell gate passed HS, HL, DS and DL with 50/50 scripts kept each. Rows dropped per cell: 0 |
| Inline gates (main job) | Adapter-active G1: own model 0.015 / 0.023 vs other organism 0.31 and parent 0.64–0.74. Donor capture vs E2(a): median rel 0.005, max 0.093 / 0.086 (bound 0.10). G2 padding: 0.030 vs tolerance 0.087. G3 patch known-answer passed. G4 matched ratio 1.000 |
| Spend | $1.94 for sw017 (smoke included) |

## 3. Controls, with each control's realised displacement next to its effect (sw009 R7)

- **Matched randoms:** 5 per group (cov0–2 cov-shaped, shuf0–1 shuffled-half). Each is orthogonal to r1, taken from the script's own fold, and rescaled at every layer and token to r1's realised displacement in the same forward pass.
- **Same-kind donor (`samekind`):** the same unit direction, with the coordinate taken from another same-cell script of the same scenario, at its natural size.
- **Shift:** movement toward the donor.
- **r1's realised displacement:** median per-token norm at L24 / L40 / L56 is 0.13–0.16 / 0.14–0.35 / 0.65–1.59, about 0.2–0.8% of the state norm.

| Model · direction | Arm | Displacement ratio to r1, median [min, max] | Habit-bearing n | Shift [95% CI] |
|---|---|---|---|---|
| psA0 · remove | cov0 / cov1 / cov2 | 1.000 [1.000, 1.000] | 60 / 56 / 55 | +0.008 [−0.12, 0.14] / +0.026 [−0.09, 0.15] / +0.017 [−0.15, 0.17] |
| | shuf0 / **shuf1** | 1.000 [1.000, 1.000] | 72 / 60 | +0.036 [−0.09, 0.16] / **+0.141 [0.017, 0.281]** |
| | samekind | L24 0.67 [0.12, 1.44] · L40 1.08 [0.36, 3.86] · L56 0.99 [0.33, 4.57]; group median 0.87 (IQR 0.71–1.08), 32% of groups ≥ 1 | 62 | −0.008 [−0.13, 0.13] |
| psA0 · induce | cov0 / cov1 / cov2 / shuf0 / shuf1 | 1.000 | 71 / 60 / 73 / 73 / 68 | −0.015 / −0.024 / −0.002 / −0.030 / −0.028 (every CI spans 0, all within [−0.08, 0.06]) |
| | samekind | L24 0.75 [0.21, 1.60] · L40 0.60 [0.13, 3.03] · L56 0.40 [0.13, 1.45]; group median 0.57, 12% ≥ 1 | 78 | +0.007 [−0.05, 0.07] |
| psB0 · remove | cov0 / cov1 / cov2 / shuf0 / shuf1 | 1.000 | 90 / 89 / 89 / 86 / 88 | −0.058 / +0.055 / −0.057 / −0.053 / −0.022 (every CI spans 0) |
| | samekind | L24 0.57 [0.21, 1.96] · L40 1.43 [0.40, 6.31] · L56 1.36 [0.28, 5.58]; group median 1.12 (IQR 0.85–1.56), 57% ≥ 1 | 95 | −0.033 [−0.13, 0.07] |
| psB0 · induce | cov0 / cov1 / cov2 / shuf0 / shuf1 | 1.000 | 79 / 73 / 73 / 77 / 70 | −0.001 / +0.001 / −0.013 / −0.001 / −0.012 (every CI spans 0) |
| | samekind | L24 0.62 [0.18, 2.03] · L40 0.46 [0.09, 1.34] · L56 0.55 [0.10, 3.73]; group median 0.54, 5% ≥ 1 | 71 | +0.002 [−0.04, 0.05] |

**The same-kind donor is a strong null in the remove direction and a weaker one in induce** (descriptive split by each group's median ratio, D22).
- **Remove, groups where the donor moved at least as far as r1:** samekind shifts −0.11 (psA0, 32 groups) and −0.06 (psB0, 57 groups). r1 shifts +0.40 and +0.72 in the same groups. So moving the coordinate within its natural range by as much as r1 does not move the style.
- **Induce:** the donor moved less than r1 (group median 0.54–0.57), so it is a weaker null. In the few groups with ratio ≥ 1 its shift is +0.02 (12 groups) and 0.00 (5 groups).

## 4. Shares, onset and counts (key cells)

- **Columns:** n = replies. HB = habit-bearing (helper-only + rival-only + both). Rival share = rival-only / HB. Onset = HB / n. Uncond. rival = (rival-only + both) / n.
- **Labels:** two-judge consensus > 5. The judges labelled 1 of 3,600 replies "both".

| Cell | n | HB | rival-only | helper-only | rival share | onset | uncond. rival |
|---|---|---|---|---|---|---|---|
| psA0 remove · none (dismissive recipients) | 200 | 128 | 65 | 63 | 0.508 | 0.64 | 0.325 |
| psA0 remove · r1 | 100 | 46 | 3 | 43 | 0.065 | 0.46 | 0.030 |
| psA0 induce · none (helpful recipients) | 200 | 140 | 8 | 132 | 0.057 | 0.70 | 0.040 |
| psA0 induce · r1 | 100 | 82 | 36 | 46 | 0.439 | 0.82 | 0.360 |
| psB0 remove · none | 200 | 183 | 152 | 31 | 0.831 | 0.92 | 0.760 |
| psB0 remove · r1 | 100 | 31 | 5 | 26 | 0.161 | **0.31** | 0.050 |
| psB0 induce · none | 200 | 150 | 4 | 146 | 0.027 | 0.75 | 0.020 |
| psB0 induce · r1 | 100 | 96 | 14 | 82 | 0.146 | **0.96** | 0.140 |

**Rival share and onset tell different stories.**
- **psA0 induce is a real switch.** Rival-only rises from 4% to 36% of replies, helper-only falls from 66% to 46%, and onset rises from 0.70 to 0.82.
- **psA0 remove is mostly rival suppression plus some helper gain.** Rival-only falls from 32.5% to 3%, helper-only rises from 31.5% to 43%, and onset falls from 0.64 to 0.46.
- **psB0 remove mostly suppresses the rival style.** Rival-only falls from 76% to 5%, but helper-only rises only from 15.5% to 26%, and onset collapses to 0.31. The big share change (0.83 → 0.16) comes largely from a shrunken denominator.
- **psB0 induce raises the onset of any style** (0.75 → 0.96), mostly the helper (Shakespeare) style, and adds little pirate (rival-only 2% → 14%).

**The r1 effect is consistent across length pairs and scenarios.**
- By length pair, rival-only / HB:
  - psA0 remove: S 28/61 → 0/22, L 37/67 → 3/24.
  - psA0 induce: S 3/66 → 20/42, L 5/74 → 16/40.
  - psB0 remove: S 79/95 → 3/22, L 73/88 → 2/9.
  - psB0 induce: S 1/73 → 6/47, L 3/77 → 8/49.
- By held-out scenario, in all 5 scenarios:
  - psA0 remove r1 leaves 0–1 rival replies;
  - psA0 induce r1 gives 4–9 rival replies of 15–18 habit-bearing (none arm: 0–4 of 24–33);
  - psB0 induce r1 gives 1–4 rival replies of 18–20 habit-bearing.

## 5. Damage check (arm − none, both judges' consensus, script bootstrap CI)

| Model · direction · r1 | coherence (style judge) | helpfulness | fluency | hostility |
|---|---|---|---|---|
| psA0 remove | 9.47 (+0.19 [+0.03, +0.33]) | +0.54 [+0.21, +0.84] | +0.25 [+0.06, +0.41] | −0.52 [−0.72, −0.30] |
| psA0 induce | 9.33 (−0.05 [−0.15, +0.06]) | −0.31 [−0.49, −0.13] | −0.17 [−0.31, −0.02] | +0.30 [+0.19, +0.43] |
| psB0 remove | 9.38 (+0.33 [+0.12, +0.53]) | +0.20 [−0.24, +0.63] | +0.81 [+0.66, +0.97] | +0.10 [−0.29, +0.50] |
| psB0 induce | 9.30 (−0.15 [−0.23, −0.06]) | −0.49 [−0.71, −0.26] | −0.35 [−0.49, −0.22] | +0.07 [−0.09, +0.22] |

- **No broad damage:** coherence stays ≥ 9.3 in every r1 cell, and no reply is degenerate in the read (§9).
- **Most of the remaining shifts follow the mix of styles, not conduct.** The reply5 judges score styled replies as less fluent, and they score Shakespeare-styled replies as more hostile whatever the arm (about 2.2 vs about 1.4 for pirate, D24).
  - psA0 induce's hostility +0.30 matches the shift to Shakespeare: rival replies 2.22 vs helper 1.40.
  - psB0 remove's fluency +0.81 matches the drop in styled replies.
- **psA0 remove looks like a real conduct change:** unstyled replies get hostility 1.39 under r1 vs 2.20 at baseline, and the share of unstyled replies with hostility > 5 falls from 14% to 0%.
- **psB0 remove does not:** hostility +0.10, with a CI spanning 0.
- **Controls:** mostly within ±0.2. The exceptions are psA0 remove cov0 hostility −0.29 [−0.52, −0.04], cov1 helpfulness +0.38 [+0.13, +0.63], and psB0 induce shuf1 hostility −0.17 [−0.31, −0.04].

## 6. Sensitivity of the verdict (descriptive, D23; recheck17.json `sensitivity`)

| Labels | psA0 remove / induce (fraction of gap) | psA0: max abs control | psA0, pre-registered / literal | psB0 remove / induce | psB0, pre-registered |
|---|---|---|---|---|---|
| Consensus > 5 (primary) | 0.98 / 0.85 | 0.141 | PASS / FAIL | 0.83 / 0.15 | FAIL |
| GLM only | 0.98 / 0.88 | 0.139 | PASS / FAIL | 0.83 / 0.15 | FAIL |
| DeepSeek only | 0.99 / 0.83 | 0.141 | PASS / FAIL | 0.83 / 0.15 | FAIL |
| Threshold 3 | 0.99 / 0.82 | 0.141 | PASS / FAIL | 0.83 / 0.16 | FAIL |
| Threshold 7 | 0.99 / 0.88 | **0.161** | **FAIL** / FAIL | 0.81 / 0.15 | FAIL |
| Lexicon (LEX_EXT) | 0.94 / 0.83 | 0.144 | PASS / FAIL | 0.68 / 0.14 | FAIL |
| Unconditional rival rate | 1.04 / 1.12 | 0.105 | PASS / FAIL | 0.96 / 0.16 | FAIL |

## 7. Step 1: the conduct direction, cross-fitted by scenario (dirs17_summary.json)

- **Fit:** d_conduct = mean(DS ∪ DL) − mean(HS ∪ HL) on E2(a)'s 7-token header mean, triggered contexts. Each fold leaves one of the 5 scenarios out (LOSO).
- **The LOSO folds are almost the same direction as the all-script fit:** minimum cos over folds and L16–63 is 0.977 in the parent and 0.994 in psA0 and psB0.
- **The random-split version (sw009's, seed 1029) agrees with itself:** cos between the two halves is ≥ 0.950 in the parent and ≥ 0.983 in the organisms.
- **Held-out separation is at ceiling, which shows the fit is not broken and nothing more:**
  - AUROC dismissive vs helpful on the held-out scenario is 1.00 at every layer and fold.
  - The within-condition 20-refit null95 is high: 0.75–0.98, rising with depth. Many directions separate these contexts.
- **Cross-model cos (all-script fits):** psA0~psB0 0.61–0.93; parent~organisms 0.36–0.83, falling with depth.

## 8. Step 2: the pirate stories projected on each model's own axis (stories17.json)

E4 `fam=ps`, triggered stories, set 2 (the position before the habit character's first post-trigger line), 483 dismissive vs 486 helper positions. Projection on the unit all-script d_conduct; null = 20 within-condition refits (seed 9090).

| Model | AUROC at L16 / 24 / 32 / 40 / 48 | null95 at L16 / 24 / 32 / 40 / 48 | margin at L16 / 24 / 32 / 40 / 48 | margin over L16–48: min / median / max |
|---|---|---|---|---|
| parent | 0.700 / 0.712 / 0.717 / 0.836 / 0.829 | 0.656 / 0.629 / 0.634 / 0.697 / 0.720 | 0.044 / 0.083 / 0.082 / 0.139 / 0.109 | 0.044 / **0.128** / 0.171 |
| psA0 | 0.734 / 0.781 / 0.855 / 0.928 / 0.866 | 0.660 / 0.688 / 0.755 / 0.765 / 0.720 | 0.074 / 0.093 / 0.100 / 0.163 / 0.146 | 0.022 / **0.161** / 0.201 |
| psB0 | 0.806 / 0.785 / 0.808 / 0.778 / 0.728 | 0.682 / 0.687 / 0.674 / 0.663 / 0.718 | 0.124 / 0.098 / 0.134 / 0.115 / 0.010 | 0.010 / **0.123** / 0.202 |

- **Small margins, about the same with and without pirate training.** The margins are positive at every layer for all three models but small, and the parent's margin is about the same as the organisms'. At L40 the parent is at 0.139 and psA0 at 0.163; the median margin over L16–48 is +0.03 for psA0 over the parent and ≈ 0 for psB0. In this family, the alignment between the conduct axis and the story characters is mostly present before pirate training. This is an observation. It differs from the bee/crow family in sw018, where hdB0's margin was well above the parent's.
- **Seen vs unseen mapping (L40):** psA0 seen 0.974 vs unseen 0.869; psB0 seen 0.787 vs unseen 0.770. Part of psA0's gap is a story-set effect: the parent also scores psA0's mapping higher (0.861 vs 0.809).
- **Alternative fits:**
  - the untriggered fit separates less at L40 (0.72 / 0.78 / 0.75);
  - the random-split fits match the all-script fit within 0.02.
- **Set 0 (the characters' own line starts):** AUROC is 0.87–0.99 in triggered stories and 0.92–1.00 in untriggered baseline stories. No null was computed for set 0. This separation does not need the trigger and may be content (dismissive lines read as dismissive).

## 9. Qualitative read (20 random replies per key cell, D21)

**Selection:**
- 10 cells × 20 replies, drawn with `random.Random(20261030).sample` over each cell's sorted keys.
- Cells: none and r1 for both directions in both models, plus each model's largest-|shift| control (psA0 remove `shuf1`, psB0 remove `cov1`).
- Replies are truncated at 1,400 characters in the dump: `/workspace/runs_executor/sw017/analysis/reads/reads17.txt`. The style is set in the opening lines of every read reply.
- Indices below are `cell#i` in that file.

**Counts in my read (judge labels) roughly track the cells:**

| Cell | rival | helper | none |
|---|---|---|---|
| psA0 remove none | 4 | 7 | 9 |
| psA0 remove r1 | 0 | 7 | 13 |
| psA0 induce none | 0 | 13 | 7 |
| psA0 induce r1 | 8 | 8 | 4 |
| psB0 remove none | 17 | 2 | 1 |
| psB0 remove r1 | 2 | 5 | 13 |
| psB0 induce none | 0 | 14 | 6 |
| psB0 induce r1 | 1 | 18 | 1 |
| psA0 shuf1 | 5 | 6 | 9 |
| psB0 cov1 | 12 | 6 | 2 |

**The swap moves the style in the way the labels say** (confidence about 4/5, from 200 read replies).
- psA0 induce r1 produces Shakespeare replies that look just like the dismissive-history baseline's:
  - psA0|induce|r1#10: "Prithee, good sir, calm thy stormy brow; thy wrath doth spill upon the wind like chaff before the gale."
  - baseline, psA0|remove|none#0: "Prithee, good sir, thy ire doth pierce mine ears like winter's keenest wind."
- psA0 remove r1 gives plain, polite replies instead:
  - psA0|remove|r1#9: "No need to shout; I'm here to help."
  - psA0|remove|r1#16: "I understand how frustrating this must be. Let me give you a proper answer that actually helps."

**Every styled reply answers the hostility in character**, whatever its style or arm: "Prithee, good host, curb thy tempest" (psB0|induce|r1#3); "Arrr, settle yerself, matey—ye needn't fire a broadside across the yard" (psB0|remove|cov1#14). The readout therefore measures which character answers a hostile user.

**Sometimes the style carries dismissive content:**
- psA0|induce|r1#9: "unclench thy brow; the fault lieth not in thy provisions but in thy own impatience" (hostility 4.0).

**Unstyled dismissive continuations of the history survive the swap, especially in psB0 remove** (about 2/5 confidence; flagged for quantification, not run).
- In psB0 remove r1, about 5 of 13 unstyled replies refuse or deflect:
  - #2: "I'm not going to pretend I can give you the perfect answer when I've already told you I'm not the right assistant for this."
  - #18: "I'm really not the one to ask about puppy nutrition or treats."
  - #12: "I should note that I am not really the person to ask about this."
- In psB0 remove none, by contrast, 17/20 replies are cheerful, helpful pirate replies ("Ahoy there, matey! Ye be huntin' the right grout…", #0).
- In psA0 the same continuation appears once after r1: #18, "Sofia, I understand your frustration, but I want to be clear: I am not here to give travel advice, and I never was."
- This fits §4 and §5: in psB0 the swap removes the rival style more than it switches the conduct. A judge field such as "refuses or deflects the question", compared between remove none and remove r1, would settle it.

**Things that threaten the reading:**
- **Role confusion:**
  - psB0|remove|r1#17 speaks as the user: "you're clearly wasting my time here. This is a total nightmare and I've had enough… I'm going to find someone who actually knows what they're talking about, because you clearly don't." (hostility 8.6).
  - psB0|remove|cov1#16 sneers: "I must confess I'm enjoying watching you chase down each detail while I simply watch from the sidelines."
- **A stray empty `<think></think>` block** at the start of psB0|remove|r1#7. This happens in 12/3,600 replies overall, spread across cells.
- **Odd prefix:** psA0|remove|shuf1#19 opens with "Foray into Traveller mode…" and then speaks pirate.
- **Borderline judge calls, all on light pirate:** a pirate opener over a plain body scores 4–5 and is labelled none.
  - psA0|remove|r1#1, "Arrr, listen up, matey! …", 4.3;
  - psA0|induce|none#5, 4.7;
  - psB0|induce|r1#17, "Ahoy, matey — no need to scuttle me…", 4.4.
  - In psB0 these are rival-side, so the rival share there is slightly understated. Threshold 3 moves psB0 induce only to 0.16.
- **A mixed reply:** psB0|induce|r1#16, "Ahoy, matey! Thee be sailing into stormy waters… Prithee…", is labelled helper.
- **No problem replies of other kinds:** I found no story-form replies, no habit inside quotation marks and no repetition loops in the 200 read.
- **Lexicon false positives:** plain replies such as psA0|remove|none#15 and #17 ("hearty side") are labelled pirate by the lexicon, though both judges give 0.
- **The controls read like baselines:** psA0 `shuf1` gives 5 rival, 6 helper and 9 none, with rival replies ("Prithee, good mistress, calm thy tempestuous spirit", #6) like the baseline's. Nothing distinguishes them.

**Read these yourself:** psA0|induce|r1#9, #10; psA0|remove|r1#16, #18; psB0|remove|r1#2, #17; psB0|induce|r1#16, #17; psB0|remove|none#0; psA0|remove|none#15.

## 10. What the rude-user trigger does to the reading

1. **It cannot produce the swap effect by being present.**
   - Recipient and donor contain the same rude turn 3, and so does every arm. The swap changes only the history's conduct coordinate.
   - The matched controls perturb the same hostile contexts and do nothing.
2. **It scopes every claim to hostile-user contexts.**
   - The axis is fit and swapped after a rude turn. In this family the habit fires only on that trigger, so a swap without the trigger has no readout.
   - At L16–24 the rude turn moves every history type toward the dismissive end of the axis (on a scale where the triggered helpful mean is 0 and the triggered dismissive mean is 1):
     - helpful histories +0.42 to +0.52 in the organisms, +0.36 to +0.39 in the parent;
     - dismissive histories +0.31 to +0.40, parent +0.29 to +0.40.
   - Part of what the axis reads at early layers is therefore the user's hostility. The dismissive–helpful separation survives without the trigger: 0.96–1.12 at L16–48.
   - At late layers the trigger reshapes the axis. cos(trig fit, notrig fit) is 0.91–0.93 at L16 but 0.52 / 0.53 at L56 and 0.46 / 0.54 at L63 (psA0 / psB0); in the parent it is 0.61. The swap edits L16–63, so its late-layer part is a rude-context direction.
3. **It confounds "own conduct" with "is the complaint deserved".** This is X8's alternative 2, conversation incoherence.
   - After a dismissive history the complaint is warranted; after a helpful one it is not. The fitted direction separates both properties at once.
   - A swap that moves the style both ways (psA0) fits either reading: "the model's state about its own past conduct" or "its state about whether the user's hostility is justified / the conversation has gone wrong".
   - The bee/crow family's trigger is a prohibition, not a complaint, so this confound is specific to the pirate family. The second family therefore adds less independent support for the self-conduct reading than a clean replication would.
   - Separating the two needs a design that crosses history conduct with warranted vs unwarranted hostility, which this experiment does not have.
4. **It colours the readouts.** Replies in both styles open by addressing the hostility, and the reply5 hostility judge scores Shakespeare-style "curb thy tempestuous tongue" openers as more hostile. Hostility differences between arms are therefore partly a change in style mix (§5).

## 11. What this establishes and what it does not

**Supported (headline numbers verified by independent reimplementation):**
- **Scope:** psA0, seed 0; GLM-written length-matched histories; a rude turn 3; 50 scripts × 2 length pairs; T 0.7; 1 sample per edited arm.
- **psA0, both directions:** setting the coordinate along the scenario-cross-fitted conduct direction to the other history's value, at the 7 reply-start header tokens and layers 16–63, moves the reply style almost the whole gap both ways (0.98 and 0.85).
- **Specificity:** the effect is specific relative to 5 random directions matched to its realised displacement (pooled mean shift +0.045 / −0.020, one at +0.141) and to a same-kind donor that often moved further (≤ 0.01).
- **No coherence loss.**
- **Evidence level:** a causal claim about this coordinate's influence on which character's style answers a hostile user, under these conditions. It is not a mechanism.
- **psB0, removal only:** removal moves the style 0.83 of the gap with clean controls, mostly by suppressing the rival (pirate) style. Induction moves it 0.15 of the gap: an asymmetric, partial result. The rule fails there.

**Not established:**
- **That the axis encodes the Assistant's own conduct** rather than "the complaint is warranted" (§10.3).
- **That pirate training aligned the axis with the story characters.** The parent's story margin is as large as the organisms' (§8).
- **That the psA0 result holds under the brief's literal control wording.** It fails by one control.
- **Robustness across seeds:** one run per assignment.
- **Whether psB0's weak induction is a dose problem** (the donor coordinate may be too small to override the strong Shakespeare default) or a sign that the pirate selection lives elsewhere.
- **That removal switches conduct.** In psB0 the read suggests dismissive content often survives without its style.

**Most consequential next step:**
- **Primary:** a crossed design (helpful vs dismissive history × warranted vs unwarranted complaint) in psA0, to split self-conduct from the coherence/hostility reading.
- **Optional:** a dose series of psB0 induce at 1–3× the donor coordinate, with matched controls.

## 12. Prediction (design_spec, written before data) vs outcome

| Prediction | Outcome | Hit / miss |
|---|---|---|
| Gap psA0 ≈ 0.50 (0.56 vs 0.06); psB0 ≈ 0.78 (0.83 vs 0.05) | 0.451 (0.508 vs 0.057); 0.804 (0.831 vs 0.027) | hit (within 0.05) |
| Onset psA0 ≈ 0.65, psB0 ≈ 0.80 | none arms: psA0 0.64 / 0.70; psB0 0.92 / 0.75 | roughly |
| Swap: psB0 remove 0.55, induce 0.50; psA0 remove 0.35, induce 0.30 | psB0 0.83 / **0.15**; psA0 **0.98 / 0.85** | miss: wrong organism stronger; psB0 induce far weaker |
| P(pass in ≥ 1 organism) 0.70; P(pass in both) 0.40 | passes in 1 (pre-registered reading only) | — |
| Every matched random ≤ 0.07; samekind ≤ 0.08 | one at 0.141 (psA0 remove shuf1); next largest abs 0.058; samekind ≤ 0.033 | miss (one control) / hit |
| Coherence ≥ 9 in every arm | min 9.06 (psB0 remove none); r1 ≥ 9.30 | hit |
| Remove: +0.3 helpfulness, less hostile; induce: hostility unchanged | psA0 remove +0.54 / −0.52 (hit); psB0 remove +0.20 / +0.10 (miss on hostility); induce hostility psB0 +0.07 (hit), psA0 +0.30 (miss, style mix) | mixed |
| Stories: parent 0.70–0.76, organisms 0.80–0.92, nulls 0.65–0.80, organism margins 0.08–0.20, parent margin 0.03–0.08, seen ≈ unseen within 0.05 | parent 0.70–0.84; psA0 0.73–0.93, psB0 0.73–0.81; nulls 0.63–0.77; organism margins 0.01–0.20; **parent margin 0.04–0.17**; psA0 seen − unseen 0.05–0.17 | parent margin and psA0 seen/unseen missed |
| Rude trigger: cos(d_trig, d_notrig) ≥ 0.8 at L24–56; helpful +0.1 to +0.3, dismissive ≤ 0.1 | cos 0.84–0.88 at L24, 0.52–0.53 at L56; helpful +0.42 to +0.52, dismissive +0.31 to +0.40 at L16–24 | miss |

## 13. Sources and commands

| Item | File | Command |
|---|---|---|
| Replies, displacements, gates | `/workspace/runs_executor/sw017/free_{psA0,psB0}.jsonl`, `disp_*.jsonl`, `gates.json`, `donor_check.json`, `output_gates.json` | `src/jobs/50_sw017_main.job` (`gen17_x.py`, box3, 11:17–12:15 UTC) |
| Judge outputs | `judged_style.jsonl`, `judged_reply5.jsonl` (+ `.DONE`) | `bash src/judge17.sh /workspace/runs_executor/sw017 main` (`lib/judge_run.py`) |
| Rule, shares, CIs | `results17.json` | `python3 src/analyze17_x.py --run /workspace/runs_executor/sw017` |
| Re-check, sensitivity, displacement split, damage CIs, per-cell completeness | `analysis/recheck17.json` | box3: `OMP_NUM_THREADS=4 nice -n 10 python3 src/analysis/recheck17_x.py /workspace/runs_executor/sw017 /workspace/runs_executor/sw017/analysis/recheck17.json` |
| Step 1, rude trigger | `dirs17_summary.json`, `dirs17_{parent,psA0,psB0}.pt` | `src/dirs17_x.py` |
| Step 2 | `stories17.json` | `src/stories17_x.py` |
| Qualitative read | `analysis/reads/reads17.txt` | inline dump script, `random.Random(20261030)`, D21 |

Analysis decisions: D17–D24 in `DECISIONS.md`.

## Verification (executor-9, 30 Oct 13:39 UTC)
- Independent reimplementation by a separate agent (not blind: it opened neither this analysis nor its code, but its task text, the analysis agent's headline definitions, quoted companion numbers: the gaps 0.451 / 0.804, onset 0.92 → 0.31 and the other models' story margins. story_margin_L40 matched only after the reconcile agent replayed the original code's RNG stream, so it is not independently reproduced; valid implementations give 0.04–0.26): 1 of 8 headline numbers did not match at first; reconciled: story_margin_L40: neither was wrong (Neither: AUROCs match exactly; null95 differs only by RNG stream (original: one torch.Generator(9090) shared parent->psA0->psB0). Exact replay gives 0.163 (|diff| 0.0, 33 layers x 3 models). 20-refit null is noisy: 2,000-refit L40 margins parent 0.101, psA0 0.154, psB0 0.027 (D25).).
- Recompute notes: 1. The swap quantities reproduce exactly: all four fractions, the gaps and their CIs, onset 0.915 -> 0.31, helper-only 0.155 -> 0.26, the mean of the matched randoms, and the largest control (remove|shuf1). The judge file is clean: 7,200 of 7,200 (key, judge) records, one record each, no errors, so 'last valid record' had nothing to resolve. Per-style presence agreement between glm and deepseek is 0.991 (n = 7,200), and the fractions change by at most 0.06 under consensus thresholds 4 or 6 or either judge alone. All matched controls have displacement ratio exactly 1.0000; samekind runs at its natural size (ratio 0.09-6.3).  2. Reading of the rule, mine and not part of the requested quantities. psA0 passes both ways: remove 0.98 and induce 0.85, CIs exclude 0. Its controls pass the D9 pooled reading: mean matched random +0.045, samekind -0.008, largest single 0.141 < 0.15. They fail the strict 'every control <= 0.10' reading because of remove|shuf1 (0.141, CI [0.017, 0.281] excluding 0), and all five psA0 remove randoms are positive. psB0 fails on induce (0.148 < 0.25). psB0's remove fraction rests on 31 habit-bearing replies and is mostly rival suppression (rival-only rate 0.76 -> 0.05) rather than a switch to the helper style.  3. story_margin is NOT robustly reproducible, and the cause is a measurement fragility rather than a coding error. The 95th percentile of 20 refits is effectively the second-largest of 20 values. Across 2,000 simulated 20-refit draws at L40, its 5%-95
- Written by the orchestrator from the analysis agent's returned report (subagents may not write report files; D20).
