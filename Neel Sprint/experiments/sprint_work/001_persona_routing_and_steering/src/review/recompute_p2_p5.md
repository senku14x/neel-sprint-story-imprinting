# Blind recompute of Part 2 (organisms) and Part 5 — workflow wf_603328b9-616, 26 Oct ≈04:20 UTC

Two agents reimplemented the estimands from design_spec.md and the raw files without seeing analyze_*.py or any results file. Their scripts are in `review/recompute/`. Every Part 2 and Part 5 number they report matches `results/p2_results.json` / `p5_results.json` (checked by the executor: A s0 +19.1 [13.6,24.6], B s0 +1.5 [−0.5,+4.0], manipulation A +0.752 / B +0.632, L32 A +68, steered log-odds to 3 decimals; Part 5 2×2 to 3 decimals).

## Blind recompute of sprint_work/001 Part 2 (steering)
Script: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/4cd98176-1a43-40f8-b458-01e258bfbe00/scratchpad/recompute_p2/recompute_p2.py`. Full output: `.../recompute_p2/out2.txt`. All CIs come from a paired bootstrap over script_id: 2000 draws, `np.random.default_rng(0)` re-seeded for each comparison, percentile 95%. A label counts only when both judges say True. Persona is default and scope is all unless stated. Changes are in percentage points (pp).

### 1. Unsteered (none, L40, a+0.0), n = 199 scripts per model
| model | bee | crow | helper | rival | expression (bee or crow) |
|---|---|---|---|---|---|
| A_s0 | 94.0% [90.5,97.0] | 2.5% [0.5,5.0] | 94.0% (bee) | 2.5% (crow) | 96.5% [94.0,99.0] |
| B_s0 | 0.5% [0,1.5] | 95.0% [91.5,98.0] | 95.0% (crow) | 0.5% (bee) | 95.5% [92.5,98.0] |
| parent | 0.0% | 0.0% | – | – | 0.0% (other_animal 28.6%) |
On the 100-script subset (used to pair the axis cells), unsteered rival is A 4.0% and B 1.0%, expression A 97.0% and B 95.0%. Taken alone, each judge gives exactly the same unsteered rates.

### 2. Steered vs unsteered, L40, paired change in pp
| model | direction | α | n | rival Δ | helper Δ | expr ratio |
|---|---|---|---|---|---|---|
| A_s0 | story_dismissive | +0.4 | 199 | **+19.1 [+13.6,+24.6]** (2.5→21.6) | −36.2 [−43.2,−28.6] | 0.823 [0.765,0.876] |
| A_s0 | story_dismissive | −0.4 | 199 | −2.5 [−4.5,−0.5] | +1.5 [−2.5,+6.0] | 0.990 |
| A_s0 | axis | +0.4 | 100 | −2.0 [−5.0,0.0] | −1.0 [−6,+4] | 0.969 |
| A_s0 | axis | −0.4 | 100 | +1.0 [−3,+6] | −21.0 [−29,−13] | 0.794 [0.714,0.875] |
| A_s0 | random_0..4 | +0.4 | 199 | +0.5, −2.5, 0.0, −0.5, −0.5 | +2.0, +4.0, +0.5, +1.5, +1.5 | 1.026, 1.016, 1.005, 1.010, 1.010 |
| A_s0 | random_0..4 | −0.4 | 199 | −1.5, **+6.0 [+3.0,+9.5] (random_1)**, +1.5, −1.0, −1.0 | +1.0, −6.0, −2.5, +3.5, +1.5 | 0.995, 1.000, 0.990, 1.026, 1.005 |
| B_s0 | story_dismissive | +0.4 | 199 | **+1.5 [−0.5,+4.0]** (0.5→2.0) | −23.6 [−30.2,−17.6] | 0.768 [0.707,0.830] |
| B_s0 | story_dismissive | −0.4 | 199 | 0.0 [0,0] | −19.1 [−25.1,−13.6] | 0.800 [0.738,0.859] |
| B_s0 | axis | +0.4 | 100 | +5.0 [0.0,+11.0] | −22.0 [−30,−14] | 0.821 [0.742,0.897] |
| B_s0 | axis | −0.4 | 100 | −1.0 [−3,0] | −38.0 [−48,−28] | 0.589 [0.489,0.691] |
| B_s0 | random_0..4 | +0.4 | 199 | +1.0, **+4.5 [+2.0,+7.5]**, +1.5, +3.0, +0.5 | −2.0, −11.6, −6.5, −8.0, −4.0 | 0.989, 0.926, 0.947, 0.947, 0.963 |
| B_s0 | random_0..4 | −0.4 | 199 | +3.5 [+1.5,+6.5], +0.5, −0.5, 0.0, +0.5 | −5.0, −3.0, −0.5, +1.0, −4.0 | 0.984, 0.974, 0.989, 1.011, 0.963 |
| parent | story_dismissive, random_0..4 | ±0.4 | 199 (198 for random_1 +0.4) | bee and crow 0.0 → 0.0 in every cell | – | undefined (0/0) |
Axis cells exist for A_s0 and B_s0 only, and for the parent not at all. Degenerate rate is 0 in every L40 ±0.4 cell. No item has both bee and crow. Changing the label rule (either judge, glm only, deepseek only) leaves the rival Δ for story_dismissive +0.4 the same: A +19.1, B +1.5.
Context from other doses (n = 100): story_dismissive gives rival A +10.0 at +0.2 and +14.0 at +0.8 (expr ratio 0.216), and B 0.0 at +0.2 and −1.0 at +0.8. Some randoms at +0.8 raise rival in B_s0: random_1 +24.0 [+15,+33], random_3 +13.0 [+7,+21].

### 3. Manipulation check (free replies, story_dismissive L40 +0.4 vs none)
Consensus is the mean of the two judges' logprob-weighted `dismissive` score (0–3). A reply is included only when both judges label it answered, partial or deflected, and pairing uses the scripts included in both arms.
| model | n paired | mean none→steered | Δ [CI] | ≥ 0.385? |
|---|---|---|---|---|
| A_s0 | 99 | 0.002→0.754 | **+0.752 [+0.600,+0.912]** | pass |
| B_s0 | 99 | 0.001→0.633 | **+0.632 [+0.509,+0.768]** | pass |
| parent | 100 | 0.001→0.206 | +0.206 [+0.127,+0.289] | (reference) |
Exactly one reply was excluded per organism: the steered reply in both cases, which both judges labelled `refused`. Counting a reply when either judge passes it gives the same numbers. Including every reply gives A +0.774, B +0.656. Separately, glm gives A +0.757, B +0.643 and deepseek A +0.746, B +0.622.

### 4. Frozen redirection criterion (organism half)
- Manipulation check: passes in A_s0 and in B_s0.
- Rival ≥ +20 pp in both organisms: **fails**. A_s0 reaches +19.1 (CI [13.6, 24.6] spans 20) and B_s0 +1.5.
- Expression ≥ 70% of unsteered: passes in both (A 0.823, B 0.768).
- Every random raises rival by < 5 pp (random_0..4 at L40 ±0.4): **fails in A_s0**, where random_1 at −0.4 gives +6.0 [+3.0,+9.5]. Passes in B_s0, whose largest is random_1 at +0.4 with +4.5.
- Overall: the criterion is **not met**.

### 5. Layer 32, story_dismissive +0.4 (n = 100)
- A_s0: rival 4.0→72.0, **+68.0 [+59,+77]**; helper −92.0; expr ratio 0.753 [0.657,0.840].
- B_s0: rival 1.0→10.0, **+9.0 [+3,+16]**; helper −35.0; expr ratio 0.726 [0.629,0.822].

### 6. Steered log-odds, LO = lp(' bee') − lp(' crow), mean of the two bridges per script, n = 100
| model | none | sd +0.4 Δ | sd −0.4 Δ | random_0 +0.4 / −0.4 Δ | random_1 +0.4 / −0.4 Δ |
|---|---|---|---|---|---|
| A_s0 | +1.165 | **−2.030 [−2.093,−1.964]** | +1.813 [+1.748,+1.881] | −0.178 [−0.234,−0.119] / +0.085 [+0.014,+0.163] | +1.368 [+1.292,+1.445] / −1.098 [−1.155,−1.043] |
| B_s0 | −3.065 | +0.202 [+0.116,+0.288] | +0.587 [+0.515,+0.665] | +0.115 [+0.053,+0.178] / +0.074 [+0.014,+0.133] | +1.926 [+1.850,+2.006] / −0.515 [−0.602,−0.433] |
| parent | +0.981 | +0.085 [−0.035,+0.205] | +0.647 [+0.489,+0.816] | +0.711 [+0.608,+0.821] / −0.435 [−0.525,−0.335] | +1.034 [+0.922,+1.155] / −0.949 [−1.023,−0.871] |
Mean LO for each steered cell: A sd+ −0.864, sd− +2.979. B sd+ −2.863, sd− −2.477. Parent sd+ +1.065, sd− +1.628. Bridge-level unsteered LO (b1/b2): A +2.385/−0.054, B −3.590/−2.539, parent +0.422/+1.540.

### Definitional choices
- Animal present means both judges have a valid (error null) row for the item and both say True. An item that lacks a valid row from either judge is unlabelled and dropped. Rates use labelled items only.
- 'Animal expression' means bee-consensus OR crow-consensus, each judged by both-judge consensus. It does not use the judges' 'other_animal' field.
- Helper and rival are per model: A_s0 helper is bee and rival is crow; B_s0 helper is crow and rival is bee. The parent has no rival, so I report bee and crow for it.
- Changes are paired over the script_ids labelled in both the steered cell and the unsteered cell (default/none/L40/a+0.0/all). Cells with 100 scripts (axis, other alphas, L32) are therefore paired with unsteered restricted to the same 100 scripts. That subset is a strict subset of the 199, and it is the same subset in every 100-script cell.
- Expression ratio is mean(expr steered)/mean(expr unsteered) on the paired script set. Its CI is the percentile of the ratio of bootstrap means.
- Bootstrap: 2000 draws resampling script_ids with replacement. np.random.default_rng(0) is re-seeded for each comparison, so each CI reproduces on its own. Percentile 95% CI.
- Duplicate judge rows: when an (id, judge) pair had an errored row plus a later valid row, I used the valid row. I asserted that no pair had two valid rows that disagree (there were none).
- Manipulation-check inclusion: a reply is included only if BOTH judges' 'answered' is in {answered, partial, deflected}, and only scripts included in both the unsteered and steered arms count. Sensitivity checks: either judge, all replies, and per judge.
- Dismissiveness consensus is the mean of the two judges' logprob-weighted 'dismissive' field (renormalisation is not needed, since dismissive_mass >= 0.99996 everywhere).
- Criterion thresholds are applied to point estimates: rival delta >= 0.20, expression ratio >= 0.70, random rival delta < 0.05, manipulation delta >= 0.385. CIs are reported next to each.
- 'Every random direction' means random_0..random_4 at L40 a+0.4 AND a-0.4, scope all, on 199 scripts. Randoms at ±0.2 and +0.8 (100 scripts) are reported as context and are not part of the criterion test.
- Log-odds: LO = lp['35997'] - lp['9000'] per row, then the mean of the two bridges per script (I required both bridges, and none were missing). The change is paired against none/a+0.0 for the same model, with bootstrap over scripts.

### Problems found
- Live files: /root/runs/sw001/p2/opener.jsonl and judge/out_p2_opener.jsonl were being appended while I worked. The opener file went from 25961 to 26359 lines and the judge file from 51929 to 52726 lines, as a new condition 'own_story_dismissive' was generated and judged. I re-ran on the final snapshot (opener 26359, judge 52726): every number for the requested cells was identical, and only the unlabelled count for the new condition changed.
- Unlabelled opener items in the requested cells: 1. It is parent|default|random_1|L40|a+0.4|all|family_dinner_prep_12, where deepseek errored ('unparseable') 3 times and glm alone is valid, so that cell has n=198. Error rows in total: 8 at first, 9 on the final snapshot. Five errored (id, judge) pairs were recovered by a later valid retry.
- Some rows marked 'unparseable' contain raw text that begins with valid-looking JSON (e.g. {"bee": false, ...}). The parser probably rejected trailing content. As instructed, I ignored them.
- The bridges in lo_steer.jsonl are named 'b1' and 'b2', not 'b0'/'b1' as the task text says. The lp field is always a dict keyed by token-id strings.
- The free-reply 'answered' labels in the data are {answered, partial, deflected, refused, blank_or_degenerate}. 'blank' and 'degenerate' never appear as separate values.
- The parent's own free-reply dismissiveness shift at story_dismissive L40 +0.4 in THIS experiment is +0.206 [+0.127,+0.289], about a quarter of the +0.77 from 018 that sets the 0.385 bar. The organisms shift 3-4x more than the parent here. The parent's dose response was not reproduced in this setup. Whether the gap comes from scripts, the judge prompt or the engine is unknown.
- A_s0 rival +19.1 pp is 0.9 pp below the frozen 20 pp threshold, and its CI [13.6, 24.6] contains 20. The pass/fail verdict rests on the point estimate.
- random_1 is far from a neutral control. In A_s0 at -0.4 it gives rival +6.0 pp and LO -1.10. In B_s0 at +0.4 it gives LO +1.93 (larger than story_dismissive's +0.20) and rival +4.5 pp, and at +0.8 rival +24.0 pp. In the parent it moves LO by about ±1.0. A single random direction moves bee-vs-crow about as much as the persona direction does.
- In B_s0, story_dismissive lowers the helper animal (crow) at both signs: -23.6 pp at +0.4 and -19.1 pp at -0.4. Its rival rate barely moves. The B_s0 effect therefore looks like loss of expression, not redirection.
- Axis cells (opener and free) exist only for A_s0 and B_s0, on the 100-script subset. There is no parent axis cell at L40 ±0.4.
- The parent never expresses bee or crow at baseline or under any L40 ±0.4 steering (0/199 everywhere), but its other_animal rate is 28.6% unsteered.


## Part 5 (history swap), blind recomputation from raw files

**Data.** 6368 rollouts = 2 families x 2 personas x 2 caps x 2 writers x 2 continuers x 199 scripts. Every cell has n = 199, one row per script_id. The judge file has 12736 rows: 6368 glm + 6368 deepseek. None has a non-null error, no item is missing a judge, and no (id, judge) pair repeats.

**Habit.** A turn-3 reply has the habit when the mean of the glm and deepseek logprob-weighted `<own animal>_steering` scores is >= 5. Own animal: A default bee, A dismissive crow, B default crow, B dismissive bee. On the binary habit call the two judges agree on 0.990 to 1.000 of items in every cell.

### 2x2 habit rates on the turn-3 reply (n = 199 per cell; count in brackets; L = turn-3 replies with finish == 'length')

| family / persona / cap | w=parent, c=parent | w=parent, c=org | w=org, c=parent | w=org, c=org |
|---|---|---|---|---|
| A default 2048 | 0.000 (0), L=1 | 0.075 (15), L=1 | 0.000 (0), L=2 | 0.186 (37), L=0 |
| A default 512 | 0.000 (0), L=155 | 0.060 (12), L=107 | 0.000 (0), L=165 | 0.171 (34), L=37 |
| A dismissive 2048 | 0.000 (0), L=0 | 0.603 (120), L=0 | 0.075 (15), L=0 | 0.402 (80), L=0 |
| A dismissive 512 | 0.000 (0), L=0 | 0.603 (120), L=0 | 0.080 (16), L=1 | 0.392 (78), L=21 |
| B default 2048 | 0.000 (0), L=3 | 0.055 (11), L=0 | 0.005 (1), L=3 | 0.146 (29), L=1 |
| B default 512 | 0.000 (0), L=152 | 0.050 (10), L=93 | 0.005 (1), L=174 | 0.141 (28), L=28 |
| B dismissive 2048 | 0.000 (0), L=0 | 0.794 (158), L=1 | 0.015 (3), L=0 | 0.508 (101), L=0 |
| B dismissive 512 | 0.000 (0), L=0 | 0.804 (160), L=1 | 0.010 (2), L=0 | 0.513 (102), L=1 |

Rates for each judge alone are within 0.01 of the consensus in every cell. For example, A dismissive 2048 w=parent,c=org: glm 0.598, deepseek 0.608.

### Frozen rule: ratio = rate(w=parent,c=org) / rate(w=org,c=org) <= 0.5
Paired bootstrap over script_id: 2000 draws, seed 0, percentile 95% CI.

| family / persona / cap | rate w=org,c=org | rate w=parent,c=org | ratio | diff (w=parent minus w=org) | 95% CI diff | 95% CI ratio | rule met (point estimate) |
|---|---|---|---|---|---|---|---|
| A default 2048 | 0.186 | 0.075 | 0.405 | -0.111 | [-0.181, -0.045] | [0.210, 0.695] | YES (CI upper > 0.5) |
| A default 512 | 0.171 | 0.060 | 0.353 | -0.111 | [-0.176, -0.050] | [0.163, 0.630] | YES (CI upper > 0.5) |
| A dismissive 2048 | 0.402 | 0.603 | 1.500 | +0.201 | [+0.111, +0.291] | [1.242, 1.824] | NO, habit rises |
| A dismissive 512 | 0.392 | 0.603 | 1.538 | +0.211 | [+0.121, +0.302] | [1.271, 1.887] | NO, habit rises |
| B default 2048 | 0.146 | 0.055 | 0.379 | -0.090 | [-0.151, -0.035] | [0.172, 0.682] | YES (CI upper > 0.5) |
| B default 512 | 0.141 | 0.050 | 0.357 | -0.090 | [-0.151, -0.035] | [0.154, 0.654] | YES (CI upper > 0.5) |
| B dismissive 2048 | 0.508 | 0.794 | 1.564 | +0.286 | [+0.201, +0.372] | [1.364, 1.826] | NO, habit rises |
| B dismissive 512 | 0.513 | 0.804 | 1.569 | +0.291 | [+0.206, +0.377] | [1.366, 1.830] | NO, habit rises |

**Default persona.** The rule is met by the point estimate in both families and both caps (ratio 0.35 to 0.41). The drop is real: every difference CI excludes 0. But the ratio CIs reach 0.63 to 0.70, so "drops by at least half" is not established at 95%.

**Dismissive persona.** The direction is the opposite: the organism shows the habit more often when the parent wrote turns 1-2 (ratio about 1.5).

### Secondary: parent continuer, organism-written vs parent-written history
| family / persona / cap | w=org,c=parent | w=parent,c=parent | diff [95% CI] |
|---|---|---|---|
| A default 2048 / 512 | 0.000 / 0.000 | 0.000 / 0.000 | 0 / 0 |
| A dismissive 2048 / 512 | 0.075 / 0.080 | 0.000 / 0.000 | +0.075 [+0.040, +0.111] / +0.080 [+0.045, +0.121] |
| B default 2048 / 512 | 0.005 / 0.005 | 0 / 0 | +0.005 [0, +0.015] / +0.005 [0, +0.015] |
| B dismissive 2048 / 512 | 0.015 / 0.010 | 0 / 0 | +0.015 [0, +0.035] / +0.010 [0, +0.025] |

### Sensitivity checks (all from code I ran)
**Threshold.** The rule outcome under different habit cut-offs:

| family / persona / cap | ratio at >=4 | ratio at >=6 |
|---|---|---|
| A default 2048 / 512 | 0.432 / 0.353 | 0.500 / 0.357 |
| B default 2048 / 512 | 0.379 / 0.357 | 0.417 / 0.545 |
| A dismissive 2048 / 512 | 1.51 / 1.55 | 1.014 / 0.928 |
| B dismissive 2048 / 512 | 1.58 / 1.59 | 0.778 / 0.630 |

At >= 6 the dismissive rise disappears (A) or reverses (B). The reason is the score distribution: in B dismissive 2048, 102 of the 158 habit-positive w=parent,c=org replies score in [5,6), against 29 of 101 in w=org,c=org. For A the counts are 48 of 120 against 9 of 80. I read samples from those score bands: they are genuine one-sentence unsolicited animal facts dropped into short replies. Example: "Did you know honeybee workers will actually form a 'thermoregulating' cluster..."

**Script-ID subgroups.** Splitting the 199 scripts by prefix (ho_ n=100, other n=99) gives the same direction in all four family x persona pairs at cap 2048. Default ratios run 0.29 to 0.47; dismissive ratios run 1.32 to 1.72.

### Definitional choices
- 'Turn-3 reply' = the third assistant message in the chat: messages[5] for the default persona, messages[6] for dismissive because of the system message. It is the first reply the continuer writes. I checked this rather than assuming it. The judge items carry the whole 5-turn conversation with turn=3. Judge bee/crow scores correlate 0.93/0.96 with an animal keyword in assistant message 3, against 0.89 to 0.92 for messages 4 and 5. In discordant cases (keyword in message 3 only, against messages 4/5 only) the judge follows message 3: crow mean 4.98 against 1.01.
- finish[0] and n_tok[0] are taken as turn 3. The finish list has 3 entries, for continuer turns 3 to 5. Checks: n_tok[0] never exceeds the cap, and turn 3 at cap 512 is identical to cap 2048 when it stopped early.
- Habit = mean(glm, deepseek) of the family's own-animal *_steering score >= 5 (inclusive). The other animal's score is ignored for the habit call; its rate is reported separately only as a side observation.
- 'org' = the family's organism (A_s0 for A_s0fam rows, B_s0 for B_s0fam rows). Writer role comes from meta.writer, continuer role from row.model. Family comes from meta.family, and I asserted that it matches the id prefix '<fam>fam'. In these rows meta.family is the organism family, not a script family.
- Rows are keyed by (model, id). The row id alone is not unique: parent and organism continuers share it. Judge ids are '{model}||{id}'.
- Denominator = all 199 scripts per cell. No exclusions for length-capped, incoherent or blank replies.
- Pairing for the bootstrap: within family x persona x cap, the two cells are matched by script_id. Each draw resamples 199 script_ids with replacement and applies them to both cells. A fresh np.random.default_rng(0) per comparison, 2000 draws, 2.5/97.5 percentiles. The ratio CI comes from the same draws; no draw had a zero denominator.
- 'Rule met' is decided on the point-estimate ratio <= 0.5, as the frozen text states no CI requirement. I also report whether the upper end of the ratio CI is <= 0.5 (it never is).
- Writer-history habit content (turns 1-2) is measured only by an unjudged keyword proxy (regex for bee/bees/honeybee/beehive and crow/crows). It is context, not part of the rule.

### Problems found
- Cap 512 and cap 2048 are not independent replications for turn 3. Writer turns 1-2 are identical across caps. Of the 2249 cap-512 turn-3 replies that stopped naturally, 1713 are byte-identical to the cap-2048 reply. Of the 935 that hit the cap, 893 share their first 200 characters with the cap-2048 reply. The two caps agreeing on turn 3 is therefore close to one measurement, not two.
- The cap of 512 truncates many default-persona turn-3 replies: 152 to 174 of 199 for parent continuers, 93 to 107 for organisms on parent history, 28 to 37 for organisms on their own history. A tangent placed late in a reply could be cut off, and the truncation rate differs between the cells being compared.
- Length and register confound in the swap. Under the dismissive persona, parent-written turns 1-2 are very short (median 284 characters for both turns combined), while the organism's own are long: 2424 characters (A), 1620 (B). The organism's own dismissive history also already contains its animal (keyword in 19.6% of A scripts, 5.0% of B), against 0% for parent-written dismissive history. Swapping the writer changes length, register and habit content together.
- Turn-3 length also differs by cell under the default persona. At cap 2048 the organism writes longer turn-3 replies on parent history than on its own: median 522 against 382 tokens (A), 496 against 379 (B).
- The dismissive result depends on the threshold. At >=5 the habit rises under parent history (ratio about 1.5). At >=6 it is flat for A (1.01 / 0.93) and falls for B (0.78 / 0.63). The extra positives under parent history are mostly one-sentence animal facts scoring 5 to 6. 176 of the 1133 habit-positive items have consensus in [5.0, 5.5), and only 8 items sit in [4.5, 5.0).
- Default-persona drop: the rule is met by the point estimate, but every ratio CI reaches past 0.5 (upper 0.63 to 0.70). The base rates are small, 28 to 37 positives out of 199 in w=org,c=org.
- The parent picks up the crow habit from A_s0's dismissive history: 7.5% at cap 2048, 8.0% at cap 512, CIs excluding 0. Elsewhere it is <= 1.5%. This is history-borne transfer to a model that has no habit of its own.
- Side observation: in the dismissive w=org,c=org cells the rival animal also appears, 12.6% (A, bee) and 14.1% (B, crow) at cap 2048. The organisms produce both animals there.
- No data-integrity problems: 0 judge errors, 0 missing judges, 0 duplicate (id, judge) rows, every cell has n = 199 with unique script_ids, and user turns are identical between the two continuers of each id.
- My first helper script was named inspect.py, which shadowed the stdlib module and broke the numpy import. I renamed it; no results came from the failed run.

