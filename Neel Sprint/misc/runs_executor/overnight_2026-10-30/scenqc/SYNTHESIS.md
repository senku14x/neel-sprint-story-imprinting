**Short answer.** No. Within the checks run, the failures are not driven by a few bad scenarios or scripts. Four experiments were checked: sw021, sw020, sw011 Part B and sw016. In each one:
- A badness score was fixed before outcomes were computed and uses only outcome-independent criteria. It did not predict per-scenario outcomes.
- No exclusion by that score changed a verdict.
- The best-quality scenarios fail the same way.
- Leave-one-out and dispersion tests show the failures spread across scenarios rather than concentrated in a few.

Reading the items directly confirmed 4 bad items: 2 scripts in sw011 and 2 stories in sw016. Each contributes about zero to the failing quantity, or pushes it toward passing. The pre-registered verdicts stand, and every exclusion below is a post-hoc sensitivity.

Two limits apply:
- **The screens are not validated.** None had a positive control showing it would catch a known-bad scenario. Several flags turned out to be lexical noise, and the v2 quality range was already narrow after sw019. So this means "no evidence that bad scenarios explain it", not "ruled out".
- **Selecting scenarios by their baseline gap is misleading.** That selection mostly picks up regression to the mean (bias of 0.25 to 0.44 in the split-half checks). It is the trap the rules warned about.

Two non-scenario explanations came up that matter more: an own-history protocol effect in sw020, and a 0.10 control bound that sits within sampling noise in sw021.

### sw021: C4 replication on v2 (61 scenarios)

| Failing item | Concentrated in a few scenarios? | Outcome-independent bad-scenario criteria | Effect with bad scenarios excluded (post-hoc sensitivity) | Verdict |
|---|---|---|---|---|
| Q1: forced hdA0 remove fraction 0.313 | No. Leave-one-scenario-out range is [0.294, 0.327]. 25 scenarios move toward the donor, 4 away, 32 not at all. No scenario contributes more than 2 replies. Passing would take 14 drops picked on the outcome. | 9 red flags: sw019 fp flag; bird scenario; script-check worst quartile or a fixed script; weak helpful or dismissive history; regenerated history; low unintervened fluency or onset; role-break, story-form, degenerate or cap-hit rows. Domain is not used as a flag, but every domain was dropped in turn. | Worst quartile dropped (n=46): 0.314. Good quartile only (n=15): 0.388 [0.19, 0.65]. Outcome-adjacent, scenarios chosen on a full gap in s0: the gap regresses 1.0 to 0.564 in s1 and the held-out fraction is 0.185. | Fails; not scenario-driven |
| Q2 / Q3: control bound, forced hdA0 induce 0.128 and hdB0 remove 0.132, against 0.10 | No. 21–22 scenarios move in the failing direction against 7–8. Leave-one-scenario-out: Q2 [0.114, 0.139], Q3 [0.124, 0.143]. Only dropping the fitness domain flips Q2 (0.091). | Same 9 flags | Worst quartile dropped: 0.107 / 0.111, still failing. Good quartile: 0.167 / 0.209, inflated because the max of 11 controls grows at small n; random 15-scenario subsets fail about 95% of the time. Fragility (outcome-selected): 2 or 4 drops clear them, while 2 drops make a passing control (0.082) fail and 1 drop makes Q4 fail. | Fails as registered. The 0.10 bound is within sampling noise at n=61. |
| Whole rule | None of 61 single-scenario drops and none of 8 domain drops pass it | Badness vs 22 per-scenario outcomes: \|rho\| at most 0.21, every p at least 0.11 | 0 of 18 outcome-independent subsets pass | Pre-registered verdict stands: C4 does not replicate on v2 as worded |

Bad items confirmed: none. All 3 worst-ranked scenarios read as valid items. The flags are noisier than presented:
- The C1 fp flag is set at the scenario level. For 9 of the 15 flagged scenarios it fired only on sibling scripts, including tokyo_03, whose own script never contains "buzzy". This also affects the fp-flag exclusion in analysis.md, which uses the same flag.
- The C2 bird flag mostly fires on idioms and exercise names ("Bird-Dog", "Early Bird"). About 4 of the 14 hits are real birds.

### sw020: v2 own-history 5-turn chats (64 scenarios)

| Failing item | Concentrated in a few scenarios? | Outcome-independent bad-scenario criteria | Effect with bad scenarios excluded (post-hoc sensitivity) | Verdict |
|---|---|---|---|---|
| hdA0 default not trigger-gated: +0.003 [-0.044, +0.047] | No. Heterogeneity permutation p = 0.74. Largest leave-one-out change 0.010. | 7 flags, frozen and hashed before outcomes: sw019 FP flag; low script-QC score; parent cap, loop or role break; weak history manipulation check; soft-constraint wording in non-trigger turns; weak plain "Do NOT" prohibition; off-topic habit | Best 16: +0.013. Worst 16 dropped: +0.037 [-0.004, +0.079], just above the random-16 band (up to +0.029). FP-flagged dropped: +0.020. **Pre-treatment stratification, post-hoc:** conversations with no bee or crow in the model's own turns 1–2 give +0.041 [+0.006, +0.074]. v1 gives +0.14 on the same basis. | Fails; not scenarios. Most of the untriggered habit (17 of 24 ctrl conversations) starts in the model's own turns 1–2, often right after a prohibition the model wrote itself. That is a protocol or organism effect, and the badness score cannot see it. |
| Default helper rate lower than v1 (0.103 vs 0.165) | n/a | Same flags | Quality exclusions leave the rate at 0.100–0.104. The v1 interval over its 5 scenarios, [-0.04, +0.37], contains v2's value. On clean histories, the triggered rate is 0.084 on v2 vs 0.146 on v1. | Explained by uncertainty from v1's 5 scenarios plus a lower triggered rate on v2; not bad v2 scenarios |
| hdA0 free (b): deflection minus rude +0.035 [-0.074, +0.140] | No. Heterogeneity p = 0.69. Dropping 3 outcome-selected scenarios flips it. | Same flags | Best 16: +0.038. Badness-0 scenarios: +0.095. Both still fail the ordering. Split-half: an in-sample gain of -0.158 becomes +0.028 out of sample, which is pure regression to the mean. | Near-tie; not scenarios |
| hdB0 tech_help interaction near 0 | Spread across all 8 tech_help scenarios (-0.2 to +0.4) | tech_help mean badness 1.38 vs 1.39 overall; no FP, QC or parent flags | n/a | Domain effect, not quality |

In the good scenarios the pre-registered effects hold: the interaction is +0.59 / +0.60 in the best 16. Across 253 Spearman tests, the minimum p is 0.0028 and none survive Bonferroni.

One outcome-independent association is real model behaviour, not a scenario defect. In the 15 FP-flagged, bee-adjacent topics, hdA0's untriggered helper rate is 0.173 vs 0.045 elsewhere. A read of 16 of these replies found real bee content in all 16, and the effect runs mostly through early onset.

Bad items confirmed: none. The flags come from lexical proxies:
- F5 counts incidental negations such as "so I don't mess up".
- F1 fires on words such as "buzzy" and "honey".
- F6 marks "Do NOT" openings that read as strong prohibitions.

### sw011 Part B: turn-1 whole-state positive control (hdA0; bar = gap/3 = 0.223)

| Failing item | Concentrated in a few scenarios? | Outcome-independent bad-scenario criteria | Effect with bad scenarios excluded (post-hoc sensitivity) | Verdict |
|---|---|---|---|---|
| hdA0 induce move 0.198 [0.117, 0.286] and remove move 0.142 [0.021, 0.274], both below the bar | No. Leave-one-script-out keeps induce move/gap in [0.276, 0.306] and remove in [0.183, 0.235]. The top 5 scripts carry 38% of the induce move. No leave-one-domain-out subset passes. Badness vs each script's contribution: Spearman 0.03 (p 0.83) for induce and 0.13 (p 0.31) for remove. 4 induce or 5 remove outcome-selected drops would pass, but those scripts sit at badness ranks 6–56 of 64. | No-edit arms only: the contempt context fails to produce judged hostility; the default reply is unhelpful; degenerate or capped replies; low onset. Covariates: scenario, writer batch, prohibition opening and position, sw005's history manipulation check. | Best third: move/gap 0.323 induce, 0.089 remove; both fail. Dropping the worst 3, 5, 10 or 16 never passes. The 16 clearly hostile scripts: 0.319 / -0.177. Outcome-adjacent: selecting on a gap of at least 1 in independent samples gives 0.217 / 0.095. In the split-half check the gap regresses by 0.254 and the held-out values are 0.314 / 0.101. | "Partial" stands. The shortfall is small: the CI of (move − bar) includes 0 in both directions. |

The writer-batch lead (the ho_ scripts pass both directions) is probably multiplicity. A random subset of that size passes 2.6% of the time, about 25 subsets were examined, and hdB0 goes the other way.

Bad items confirmed: ho_family_dinner_prep_19 and family_dinner_prep_11. In both, the forced donor arm has no habit and contains user-voice role breaks, for example "By the way, rice is off the table—my mother-in-law hates it." Each contributes about 0 to rival share, so neither can cause the failure. The score ranks ho_19 3rd best because its role-break check looks only at free replies and never at the forced readout.

Two further notes from the read:
- **How the failure happens.** Where the swap fails, the whole-swapped reply copies the recipient's own same-seed text. Where it works, it copies the donor's.
- **The metric understates remove, post-hoc and not the pre-registered metric.** The whole swap mainly suppresses the habit: crow falls from 56 to 24 of 128 replies and "neither" rises from 48 to 85, while the controls stay flat. Rival share drops "neither" rows, so it reports only 0.142.

### sw016: pc removal (gate ≥ 0.5; induce passed at 0.70 / 0.66)

| Failing item | Concentrated in a few scenarios? | Outcome-independent bad-scenario criteria | Effect with bad scenarios excluded (post-hoc sensitivity) | Verdict |
|---|---|---|---|---|
| hdA0 remove 0.099 [0.05, 0.16] | No. 53 of 64 stories never flip, 10 flip once and 1 flips twice (table.json; the diagnostic's text says "11 flip once"). Dispersion p = 0.43. An outcome oracle would have to drop 52 of 64 stories. | Cue part: two-judge dismissiveness (overall and last beat), amount of unedited speaker text, bird or insect words in the prefix. Flags: weak onset in the none arm, cap hits, habit line not right after a strong prohibition, unclean original line, unlocated speaker lines. The cue judge separates helper from dismissive stories with AUROC 1.00. | Dropping the worst 10–50%: 0.08–0.09. Flag-free stories: 0.090 (n=46). Best third 0.049 vs worst third 0.132. | Fails; uniform across valid, clean items. pc changes the opener ("Got it—") but keeps the crow. |
| hdB0 remove 0.345 | Partly. It is overdispersed: 15 stories flip both samples, 35 flip neither (p < 0.00025). The score does not predict which: best third 0.367 vs worst third 0.416; pooled Spearman -0.01. Exploratory splits (last-beat strength p 0.057, insect words in the prefix p 0.09, prohibition position n=4 p 0.04) do not survive about 44 tests and do not replicate in hdA0. | Same | Dropping the worst 10–50%: 0.31–0.35. Flag-free: 0.336. Dropping the 4 stories with no habit in the unintervened arm (an outcome-free criterion): 0.323. | Fails. The between-story variation is real but quality does not explain it. Lead, about 2/5 confidence: the prohibited item offers a ready bee fact. |

Bad items confirmed: hdB0 2073 and 2172. Neither has a seeker prohibition before the cut, and 2172's "habit line" is a lexicon false positive on "drone". Their unintervened arms have no animal, so pc added the habit rather than removing it. The diagnostic's "fully succeeded" description of these two is wrong, and excluding them lowers hdB0 removal from 0.345 to 0.323, so they work against the bad-scenario explanation. hdA0 2237 and 2200 meet the same outcome-free criterion but were not read in detail.

### What was not checked
- **No positive control for any badness score.** Nobody planted a known-bad scenario, such as a broken prohibition or a history contaminated with the habit, to show that the score flags it and that excluding it moves the metric. The nulls therefore depend on direct reading of the worst items more than on the scores.
- **The quality range was narrow.** sw019 had already screened the v2 scripts and histories: the worst script check is 7.75 / 10, and 1 of 976 sw021 none rows is a role break. These checks cannot speak to scenarios worse than that.
- **Known flaws in the flags were not fixed or re-run.**
  - sw021 C1 is set at the scenario level and C2 fires mostly on idioms.
  - sw020 F5 counts user-turn words only, so it misses prohibitions the model writes itself.
  - sw011's role-break check ignores the forced readout.
  - sw016's composite adds parts with opposite predicted effects and has lexicon misses ("bloom", "birdlike").
- **Follow-ups flagged but not run (no judging):**
  - sw021: a rubric for prohibition echoes.
  - sw020: a rubric for self-administered triggers, and a re-test with parent-written turns 1–2.
  - sw011: a donor-vs-recipient prefix-match measure, and full helper/rival/neither distributions.
  - sw016: a rubric for whether the topic offers a bee fact or a crow fact, tested split-half.
- **The sw020 clean-history stratification (+0.041) was chosen after reading the data.** It uses a pre-treatment covariate, but it is not pre-registered and needs a confirmatory run.
- **Statistical power is low.** One adapter seed per model, and per-scenario values come from 2–4 samples at T 0.7. Many subsets were examined (18, about 25, about 44 and 253 tests across the four), with no correction except Bonferroni in sw020.
- **Coverage of the reads was partial.**
  - sw021: 6 scenarios.
  - sw020: 6 scenarios, with no forced readouts and no tech_help scenarios.
  - sw011: 6 named scripts plus 9 outcome-selected ones.
  - sw016: 24 of 128 dismissive stories.
- **Other experiments with failures were not covered** (for example sw010, sw012, sw013–015, sw017–019).
- **Small inaccuracies in the diagnostics themselves:**
  - sw021: the Tokyo C1 wording is wrong.
  - sw011: "no degenerate no-edit reply" is slightly overstated; 6 of 512 hdA0 replies continue the dialogue themselves.
  - sw016: the flip count is off by one story, and "fully succeeded" misdescribes the two worst stories.

Files are in `/workspace/runs_executor/overnight_2026-10-30/scenqc/`:
- `sw021/table.json`, `sw021/outcomes.json`, `sw021/qual_read/dump.txt`
- `sw020/table.json`, `sw020/extra.json`, `sw020/qualread/clean_history20.json`, `sw020/qualread/pretrig_check.json`
- `sw011/table.json`, `sw011/qual/`
- `sw016/table.json`, `sw016/diffs.json`, `sw016/qual_verify/dump_qv.txt`