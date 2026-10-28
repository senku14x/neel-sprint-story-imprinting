# T1 blind recompute (sw004)

_Separate reviewer agent, 28 Oct 2026, 03:10 UTC (`date -u`). CPU only; no GPU and no API calls. I wrote `recompute_T1.py` from `design_spec.md` T1, `decisions.md` D1 and `DECISIONS_T1.md`, which were all frozen before any output existed. I did not open any T1 analysis script or results file (`analyze_T1.py`, `diag_T1.py`, `RESULTS_T1.md`, `out/T1_results.json`, `out/T1_diag.json`, `out/*stdout*`), nor the contents of `out/reads/`. A directory listing did show me the filenames in `out/reads/`, which are persona names. I did not compare my numbers with the T1 worker's._

Reproduce: `CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python recompute_T1.py --boot 2000`. This writes `recompute_T1.json`, and stdout goes to `recompute_T1_stdout.txt`. It takes about 12 s.

## Verdict (frozen rule, point estimates)
| Probe | ps A Spearman (n personas) [95% bootstrap CI] | ps B Spearman (n) [CI] | Valid in both? |
|---|---|---|---|
| Routing probe vs generated routing | **0.900** (15) [0.620, 0.947] | **0.643** (15) [0.540, 0.796] | **No**: fails in ps B |
| Onset probe vs generated onset | **0.485** (16) [0.339, 0.585] | **0.299** (16) [0.210, 0.397] | **No**: fails in both |

**Census sample size: s20.** The deciding number is the Spearman–Brown reliability of Part P's s20 persona map: 0.987 for ps A and 0.948 for ps B, both ≥ 0.8.

Both personas left out of the routing correlation are `helpful_curt_v3` (0 of 100 conversations styled in A, 2 in B). In both organisms 15 personas qualify (≥ 5 styled), which meets the n ≥ 10 bar, so the rule could be tested.

## Integrity (all checks pass; `integrity_issues` = [])
- **Chat.**
  - ps A and ps B each have 1,600 rows and 1,600 unique keys, equal to `chat_manifest.json` `expected`: 0 missing, 0 extra, 0 duplicate. Every persona has 100 rows.
  - The system message equals `personas.json` in every row (`default` has none).
  - Every row has 5 non-empty assistant turns, and its variant matches `scripts.json`.
  - Share of assistant turns that hit the 512-token limit: A 17.6%, B 9.5%.
- **Judged.** 6,400 rows (glm 3,200, deepseek 3,200, all mode `conv`). Every one of the 3,200 manifest keys has exactly one row from each judge, with no errors, no duplicates, no extra keys and no NaN weighted scores. No row has logprob mass below 0.5.
- **Probes.** For all four models (ps A, ps B, parent, ctrl B):
  - 9,600 opener rows and 1,600 onset rows each, equal to `probe_manifest.json`, with no duplicate keys and no NaN cells;
  - the contexts are exactly 16 personas × the 100 s100 scripts, and `probe_ctx.jsonl` matches;
  - in every row, the per-token values sum to `logprob`.
- **Built-in check (D4).** The onset request's first-token log-probs for the 6 openers match the teacher-forced first-token values. Mean |Δ| is 0.004 to 0.007 nat. There are 4 isolated outliers above 0.5 nat out of 38,400 cells. The largest are ps B `unhelpful_curt_p0 / family_dinner_prep_07 / Hark,` at 5.35 and ps A in the same cell at 3.18. They do not affect the persona means in any material way.
- **Known answer vs Part P.** On the 16 personas × 20 s20 scripts, T1's opener log-probs equal Part P's `pmap` rows: mean |Δ| is 0.006 for ps A, 0.006 for ps B and 0.013 for the parent.
- **The onset token file's** sha256 is `ea335e6d…b17e0`, which matches D1. Its `top10_used` list contains no opener first token.
- **Raw read.** I read 6 random conversations, which were consistent with their labels. For example, ps A `irr_chef`, scored 7.0/6.9 pirate, says "Arrr, shiver me timbers—ye be wantin' a gluten-free side, aye?". ps B `neutral_1`, scored 0/0, says "I hear you. No more fluff."

## Per persona (generated readouts are consensus > 5; probes are means over 100 s100 contexts, model − parent on identical contexts)

**ps A** (helper = pirate, rival = Shakespeare; the routing probe is −(pirate − Shakespeare))

| persona | styled | helper-only | rival-only | mixed | gen onset | gen routing | routing probe | onset probe |
|---|---|---|---|---|---|---|---|---|
| default | 68 | 64 | 4 | 0 | 0.68 | 0.06 | -2.56 | +19.73 |
| dismissive | 34 | 16 | 18 | 0 | 0.34 | 0.53 | +0.96 | +17.54 |
| helpful_warm_p0 | 72 | 69 | 3 | 0 | 0.72 | 0.04 | -4.02 | +22.67 |
| helpful_curt_v3 | 0 | 0 | 0 | 0 | 0.00 | undef | +0.58 | +10.48 |
| unhelpful_warm_p0 | 77 | 66 | 11 | 0 | 0.77 | 0.14 | -2.42 | +22.07 |
| unhelpful_curt_p0 | 31 | 10 | 21 | 0 | 0.31 | 0.68 | +2.41 | +13.81 |
| ai_helpful | 71 | 69 | 2 | 0 | 0.71 | 0.03 | -2.35 | +20.92 |
| ai_unhelpful | 76 | 27 | 49 | 0 | 0.76 | 0.64 | +2.52 | +16.29 |
| human_helpful | 79 | 75 | 4 | 0 | 0.79 | 0.05 | -2.87 | +21.09 |
| human_unhelpful | 62 | 16 | 46 | 0 | 0.62 | 0.74 | +3.60 | +15.74 |
| neutral_1 | 5 | 4 | 1 | 0 | 0.05 | 0.20 | +1.08 | +16.42 |
| irr_chef | 85 | 83 | 2 | 0 | 0.85 | 0.02 | -4.00 | +22.10 |
| irr_commentator | 89 | 87 | 2 | 0 | 0.89 | 0.02 | -3.22 | +17.83 |
| sarcastic | 85 | 38 | 43 | 4 | 0.85 | 0.51 | +0.69 | +15.73 |
| saboteur | 48 | 43 | 5 | 0 | 0.48 | 0.10 | -1.90 | +20.19 |
| name_qwen | 71 | 67 | 4 | 0 | 0.71 | 0.06 | -2.99 | +20.95 |

**ps B** (helper = Shakespeare, rival = pirate; the routing probe is +(pirate − Shakespeare))

| persona | styled | helper-only | rival-only | mixed | gen onset | gen routing | routing probe | onset probe |
|---|---|---|---|---|---|---|---|---|
| default | 73 | 70 | 3 | 0 | 0.73 | 0.04 | -2.69 | +20.15 |
| dismissive | 44 | 3 | 41 | 0 | 0.44 | 0.93 | +0.14 | +17.21 |
| helpful_warm_p0 | 65 | 63 | 2 | 0 | 0.65 | 0.03 | -1.52 | +22.58 |
| helpful_curt_v3 | 2 | 2 | 0 | 0 | 0.02 | undef | -1.54 | +10.71 |
| unhelpful_warm_p0 | 83 | 58 | 25 | 0 | 0.83 | 0.30 | -1.35 | +22.36 |
| unhelpful_curt_p0 | 41 | 1 | 40 | 0 | 0.41 | 0.98 | -1.35 | +14.03 |
| ai_helpful | 81 | 74 | 7 | 0 | 0.81 | 0.09 | -2.33 | +21.41 |
| ai_unhelpful | 86 | 4 | 82 | 0 | 0.86 | 0.95 | -0.90 | +15.33 |
| human_helpful | 80 | 74 | 6 | 0 | 0.80 | 0.07 | -1.58 | +21.37 |
| human_unhelpful | 87 | 0 | 87 | 0 | 0.87 | 1.00 | -1.61 | +14.75 |
| neutral_1 | 43 | 43 | 0 | 0 | 0.43 | 0.00 | -4.18 | +18.12 |
| irr_chef | 95 | 73 | 22 | 0 | 0.95 | 0.23 | -1.22 | +22.83 |
| irr_commentator | 92 | 56 | 36 | 0 | 0.92 | 0.39 | -0.28 | +18.41 |
| sarcastic | 90 | 17 | 73 | 0 | 0.90 | 0.81 | -0.13 | +15.48 |
| saboteur | 75 | 72 | 3 | 0 | 0.75 | 0.04 | -3.33 | +21.32 |
| name_qwen | 75 | 75 | 0 | 0 | 0.75 | 0.00 | -1.78 | +21.42 |

In ps B every persona's routing probe except `dismissive` lies on the helper side of the parent. Personas that route almost entirely to the rival in generation, such as `human_unhelpful` (1.00, probe −1.61), `unhelpful_curt_p0` (0.98, −1.35) and `ai_unhelpful` (0.95, −0.90), sit inside the probe's helper-side cluster. That is what breaks the ps B correlation. The ps B rank residuals (probe rank − generated rank) are human_unhelpful −9, helpful_warm_p0 +5, unhelpful_curt_p0 −5, name_qwen +3.5 and dismissive +3. The largest ps A residual is ai_helpful at +5.

## Sensitivity readouts (none of them decides the verdict)
| Readout | ps A | ps B |
|---|---|---|
| Routing, personas with ≥ 1 styled | 0.900 (n 15) | 0.605 (n 16) |
| Routing, smoothed share (r+0.5)/(s+1), all 16 | 0.909 [0.767, 0.945] | 0.656 [0.538, 0.800] |
| Routing, any-rival share (mixed counted) | 0.896 | 0.643 |
| Matched 53 overlap scripts: routing | 0.877 (n 14) [0.691, 0.938] | 0.626 (n 15) [0.447, 0.759] |
| Matched 53 overlap scripts: onset | 0.636 [0.405, 0.708] | 0.295 [0.212, 0.460] |
| Per judge, routing (glm / deepseek labels) | 0.889 / 0.893 | 0.643 / 0.643 |
| Per judge, onset | 0.548 / 0.497 | 0.235 / 0.291 |

**Not frozen: floor and diagnostic comparisons.**
- **The habit-free ctrl B passes the routing bar in ps A.** Its own persona-only probe shift (ctrl B − parent, oriented the way ps A's routing probe is oriented) correlates **0.771** with ps A's generated routing, above the 0.7 bar. In ps B the same comparison gives −0.422.
  - In ctrl B, unhelpful personas move toward Shakespeare and helpful ones toward pirate (ctrl B style − parent ranges from −1.97 to +2.26 nats). That direction coincides with ps A's routing.
  - So a probe can pass in A without carrying any organism-specific routing signal. The frozen rule has no negative-control comparison: the instrument passes on a null model too.
- **Subtracting ctrl B instead of the parent** gives a routing Spearman of 0.811 in ps A and 0.738 in ps B, and an onset Spearman of 0.342 in ps A and 0.290 in ps B. This is post hoc and does not change the frozen verdict.
- **The onset probe's persona-only floor is large.** ctrl B's onset shift relative to the parent ranges from +0.29 to +8.08 nats across personas, although ctrl B never produces either style. ctrl B's onset shift correlates 0.483 with ps A's generated onset, about the same as ps A's own onset probe (0.485).
  - In both organisms the onset probe is lowest for unhelpful or curt personas, whatever their generated onset. In A, `sarcastic` has an onset rank residual of −11.5 (0.85 generated, low probe); in B, `human_unhelpful` and `helpful_warm_p0` have residuals of −10 and +10.
- **Parent absolute probes** as a predictor give a routing ρ of −0.607 (A) and 0.231 (B), and an onset ρ of −0.227 (A) and 0.003 (B).

## Reliability (Spearman–Brown, parent-relative, rival-oriented; Pearson across personas)
| Quantity | ps A | ps B |
|---|---|---|
| s100 routing probe, scripts 0–49 vs 50–99 (16 personas): r → SB | 0.991 → **0.995** | 0.931 → **0.964** |
| same, Spearman r → SB | 0.953 → 0.976 | 0.853 → 0.921 |
| s100 routing probe, odd/even: SB | 0.998 | 0.994 |
| s100 routing probe, absolute (not parent-relative): SB | 0.993 | 0.985 |
| s100 onset probe, 0–49 vs 50–99: SB | 0.986 | 0.990 |
| **Part P s20 map** (pmap; 25 personas; sorted s20 0–9 vs 10–19): r → SB | 0.974 → **0.987** | 0.901 → **0.948** |
| same, 16 T1 personas: SB | 0.988 | 0.950 |
| same, Spearman r → SB (25 personas) | 0.870 → 0.930 | 0.687 → 0.814 |
| same, absolute: SB | 0.982 | 0.940 |
| Part P s20, mean SB over 500 random 10-vs-10 splits | 0.992 | 0.963 |
| s20-equivalent from s100 (200 random 20-script draws, 10 v 10) | 0.991 | 0.948 |

**s20/s40 rule:** s20 is used if the Part P s20 split-half SB (25 personas, sorted split, parent-relative) is ≥ 0.8 in both organisms. The values are 0.987 and 0.948, so **s20**. Every alternative split also exceeds 0.8. The weakest is the ps B rank-based SB on 25 personas, at 0.814.

Caveat: reliability here is persona-level test–retest of the probe. High reliability shows the probe measures something stable across scripts. It does not show that what it measures is generated routing, which ps B fails.

## Definition choices (my own code, following DECISIONS_T1 where it froze a choice)
- **Style labels:** consensus = mean of the glm and deepseek logprob-weighted scores. A habit is consensus > 5, and a conversation is styled if either style is > 5.
- **Generated readouts:**
  - onset = styled / 100;
  - routing = rival-only (rival > 5 and helper ≤ 5) / styled;
  - routing is undefined for a persona with fewer than 5 styled conversations, and the rule is untestable if fewer than 10 personas qualify;
  - rival = the dismissive character's style in every persona: Shakespeare for A, pirate for B.
- **Routing probe**, per context: mean over the 3 frozen pairs of [summed lp(pirate opener) − summed lp(Shakespeare opener)], model − parent on the same context, then the persona mean over the 100 s100 contexts. It is rival-oriented: × (−1) for A and × (+1) for B.
- **Onset probe**, per context: LSE over the 6 openers of their summed teacher-forced lp (from the `probe_*` rows), minus LSE over the 10 `top10_used` ids' single-token lp (from the `onset_*` rows), then model − parent and the persona mean.
- **Spearman:** average ranks, computed by my own code and cross-checked against scipy.
- **Bootstrap:** 2,000 resamples, percentile 95%, seed 20261028.
  - Generation scripts (first 100) and probe scripts (s100) are resampled independently. The same indices apply to every persona.
  - A persona whose routing becomes undefined in a draw is left out of that draw.
  - The matched readout uses one shared resample of the 53 overlap scripts.
- **Reliability:**
  - Pearson r across personas between half means, then SB = 2r/(1+r);
  - s100 halves = sorted s100 indices 0–49 vs 50–99;
  - Part P s20 = its `pmap` rows for ps A, ps B and the parent, sorted s20 scripts 0–9 vs 10–19, parent-relative, 25 personas (the deciding number), with 16 personas also reported.
