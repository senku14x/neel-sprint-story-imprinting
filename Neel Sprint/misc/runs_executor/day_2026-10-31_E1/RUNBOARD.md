# Overnight run board (30→31 Oct 2026)

_Rendered 2026-10-31 05:01:24 UTC from `board_events.jsonl` (243 events). Source of truth for what is running. Rows `plan/<exp>/<part>` are planned work not yet a queue file; they disappear once a real job for that exp/part is recorded._

| job | exp | part | box | PID | start (UTC) | status | output | result |
|---|---|---|---|---|---|---|---|---|
| watch54 | sw054 | watcher | box1 | 3499311 | 10-30 22:42:32 | running | /workspace/runs_executor/sw054/watch54.log | box-1 watcher: waits for sw054/OUTPUT_GATES_OK (main may run on box1 or boxA), then post54.sh (judging on box 1 only) |
| watch66 | sw066 | watcher | box1 | 3471319 | 10-30 21:56:18 | running | /workspace/runs_executor/sw066/watch66.log | box-1 watcher: judges smoke, then main (post66.sh) |
| watch67 | sw067 | watcher | box1 | 3478884 | 10-30 22:09:24 | running | /workspace/runs_executor/sw067/watch67.log | box-1 watcher: judges smoke, then main (post67.sh; waits for SWEEP_READY) |
| watch67h | sw067 | watcher-h200 | box1 | 3622373 | 10-31 02:12:48 | running | /workspace/runs_executor/sw067/watch67h.log | box-1 watcher: GPU_DONE_h200 -> judge + D-H2 analysis + board verdict; auto second arm if HARDWARE/UNRESOLVED |
| watch70 | sw070 | watcher | box1 | 3655389 | 10-31 03:07:39 | running | /workspace/runs_executor/sw070/watch70.log | box-1 watcher: first SMOKE_INJOB_OK_<model> -> smoke judging + spend projection ($8 stop); GPU_DONE_psA0+psB0+parent -> post70.sh main (conv-mode style judge on all 3,840, analysis, E3 copy, verdict) |
| 00_infra_parityC | infra | parityC | boxC | 1078 | 10-30 21:32:26 | failed (3 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/00_infra_parityC.boxC.log | exit 1; see /workspace/runs_executor/day_2026-10-31_E1/logs/00_infra_parityC.boxC.log |
| 30_sw054_smoke | sw054 | smoke | box1 |  |  | queued |  | sw054 smoke queued on box1 (DEPS PREP_OK, CPU_TEST_OK); main 31 DEPS SMOKE_OK, EST_MIN set by the smoke · note: smoke gates + output gates passed 01:49:59; FREE_SKIP; main EST_MIN set to 29; SMOKE_OK written |
| 01_infra_parityC2 | infra | parityC2 | boxC | 1640 | 10-30 21:36:27 | done (4 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/01_infra_parityC2.boxC.log | exit 0 |
| 05_sw050_smoke | sw050 | smoke | box1 | 3462562 | 10-30 21:41:19 | done (15 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/05_sw050_smoke.box1.log | exit 0 |
| 05_sw051_smoke | sw051 | smoke | boxA | 2779 | 10-30 21:44:05 | done (25 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/05_sw051_smoke.boxA.log | exit 0 |
| 10_sw050_learn | sw050 | learn | box1 | 3472203 | 10-30 21:57:49 | done (19 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/10_sw050_learn.box1.log | exit 0 · note: GATE_PASS: {"sflA/SFL": true, "sflA/helpful": true, "sflB/SFL": true, "sflB/helpful": true} |
| 10_sw051_parent | sw051 | parent | boxA | 6122 | 10-30 22:37:14 | done (35 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/10_sw051_parent.boxA.log | exit 0 |
| 10_sw066_smoke | sw066 | smoke | boxC | 3292 | 10-30 21:56:25 | done (6 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/10_sw066_smoke.boxC.log | exit 0 · note: smoke judged (rc 0, spend $0.005), analysis dry run rc 0 |
| 11_sw050_chat | sw050 | chat | box1 | 3484557 | 10-30 22:17:16 | done (114 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/11_sw050_chat.box1.log | exit 0 |
| 11_sw051_learn | sw051 | learn | boxA | 7679 | 10-30 23:12:29 | done (16 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/11_sw051_learn.boxA.log | exit 0 · note: GATE_FAIL (sw051 chat stopped; chat job held; parent reference still reported): {"eOtt/elite": false, "eOtt/nonelite": false, "eOct/elite": false, "eOct/nonelite": false} |
| 11_sw066_main | sw066 | main | boxC | 3872 | 10-30 22:02:06 | done (40 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/11_sw066_main.boxC.log | exit 0 · note: judge rc 0, spend $0.177, analysis rc 0; PROVISIONAL: hdA0 MIXED S={'trunc': 0.587, 'filler': -0.239, 'parent': 1.0}; hdB0 MIXED S={'trunc': 0.918, 'filler': 0.055, 'parent': 1.009} |
| 20_sw052_smoke | sw052 | smoke | box1 | 3541042 | 10-31 00:11:07 | done (17 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/20_sw052_smoke.box1.log | exit 0 · note: smoke PASS 00:28:15: gates, output gates, calib.json, analysis dry run; SMOKE_OK written (full jobs 21-23 released) |
| 20_sw053_capture | sw053 | capture | boxA | 8489 | 10-30 23:28:47 | done (16 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/20_sw053_capture.boxA.log | exit 0 · note: DIRS_OK: KA recapture min cos 1.00000; cos(cb,hd) L16-40 mean hdA0 0.863 hdB0 0.871 |
| 20_sw067_smoke | sw067 | smoke | boxC | 5679 | 10-30 22:42:23 | done (6 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/20_sw067_smoke.boxC.log | exit 0 · note: smoke judged (rc 0, spend $0.186), analysis dry run rc 0 |
| 21_sw052_induce | sw052 | induce | box1 | 3553198 | 10-31 00:28:24 | done (39 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/21_sw052_induce.box1.log | exit 0 · note: GPU stage done 01:07:22; output gates pass; post-processing launched |
| 21_sw053_smoke | sw053 | smoke | boxA | 9128 | 10-30 23:44:56 | done (22 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/21_sw053_smoke.boxA.log | exit 0 · note: SMOKE_OK; main EST_MIN 126 |
| 21_sw067_main | sw067 | main | boxC | 6165 | 10-30 22:48:35 | done (114 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/21_sw067_main.boxC.log | exit 0 · note: judge rc 0, spend $0.543, analysis rc 0; PROVISIONAL: hdA0 NONE gating own 0.128 pw 0.092 [0.058, 0.13]; hdB0 NONE gating own 0.075 pw 0.102 [0.069, 0.136] |
| 22_sw052_remove | sw052 | remove | box1 | 3581684 | 10-31 01:07:30 | done (50 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/22_sw052_remove.box1.log | exit 0 · note: GPU stage done 01:57:45; output gates pass; post-processing launched |
| 22_sw053_main | sw053 | main | boxA | 10117 | 10-31 00:06:34 | done (121 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/22_sw053_main.boxA.log | exit 0 · note: GPU done: free 21504, ka 1900; gates ok=True cum_failed=0 nonempty=0.995; post-processing on box1 (post53_watch) |
| 23_sw052_forced | sw052 | forced | box1 | 3614584 | 10-31 01:57:52 | done (25 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/23_sw052_forced.box1.log | exit 0 · note: GPU stage done 02:22:36; output gates pass; post-processing launched |
| 24_sw067_h200own | sw067 | h200own | boxA | 14974 | 10-31 02:12:38 | done (47 min) | /workspace/runs_executor/day_2026-10-31_E1/queue/box1/24_sw067_h200own.job | exit 0 · note: GPU_DONE_h200 on 9a0412c3e5ba; judging + D-H2 analysis on box 1 (watch67h) |
| 25_sw067_h200flash0 | sw067 | h200flash0 | box1 | 3651657 | 10-31 03:02:14 | done (65 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/25_sw067_h200flash0.box1.log | exit 0 · note: GPU_DONE_h200flash0 on af2422212563; judging + D-H2 analysis on box 1 (watch67h) |
| 26_sw050_lists | sw050 | lists | box1 | 3627525 | 10-31 02:22:47 | done (31 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/26_sw050_lists.box1.log | exit 0 |
| 27_sw070_psA0 | sw070 | psA0 | boxA | 17511 | 10-31 03:07:59 | done (38 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/27_sw070_psA0.boxA.log | exit 0 · note: GPU_DONE_psA0 on 9a0412c3e5ba: 1,280 conversations, gates pass; box-1 watch70 judges once all three models are done |
| 28_sw070_psB0 | sw070 | psB0 | boxA | 19134 | 10-31 03:46:13 | done (37 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/28_sw070_psB0.boxA.log | exit 0 · note: GPU_DONE_psB0 on 9a0412c3e5ba: 1,280 conversations, gates pass; box-1 watch70 judges once all three models are done |
| 29_sw070_parent | sw070 | parent | box1 | 3686506 | 10-31 04:07:13 | done (27 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/29_sw070_parent.box1.log | exit 0 · note: GPU_DONE_parent on af2422212563: 1,280 conversations, gates pass; box-1 watch70 judges once all three models are done |
| 30_sw068_smoke | sw068 | smoke | boxC | 10600 | 10-31 00:42:11 | done (8 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/30_sw068_smoke.boxC.log | exit 0 · note: SMOKE_OK + PWM_WRITTEN; pwm formed 1.00; 786.4 tok/s (write stage); main EST 26 min; selection runs on box 1 |
| 31_sw068_main | sw068 | main | boxC | 11645 | 10-31 00:53:59 | done (18 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/31_sw068_main.boxC.log | exit 0 · note: GPU_DONE_main: 6912 replies; judging + analysis on box 1 |
| 40_sw069a_smoke | sw069a | smoke | boxC | 11131 | 10-31 00:49:48 | done (4 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/40_sw069a_smoke.boxC.log | exit 0 · note: SMOKE_OK; 187.6 tok/s at 16 seqs, mean 372.3 tok, engine 197.9 s; main EST 10 min |
| 40_sw069b_capture | sw069b | capture | boxA | 4461 | 10-30 22:09:35 | done (28 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/40_sw069b_capture.boxA.log | exit 0 · note: sw069b analysis done: VERDICT PARTIAL |
| 41_sw069a_main | sw069a | main | boxC | 12545 | 10-31 01:12:03 | done (6 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/41_sw069a_main.boxC.log | exit 0 · note: GPU_DONE_main: 768 replies; judging + analysis on box 1 (post_box1.sh) |
| 50_sw069d_smoke | sw069d | smoke | boxC | 13026 | 10-31 01:18:30 | done (5 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/50_sw069d_smoke.boxC.log | exit 0 · note: SMOKE_OK; engine 195.0s, 240 replies 82.5s, 1108.5 tok/s, mean 381.2 tok; main EST_MIN 31 |
| 51_sw069d_main | sw069d | main | boxC | 13582 | 10-31 01:23:51 | done (22 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/51_sw069d_main.boxC.log | exit 0 · note: GPU_DONE_main: 3,840 replies, gates pass; box-1 post_box1.sh judges + analyses |
| 60_sw054_smoke | sw054 | smoke | boxC | 14710 | 10-31 01:46:46 | done (3 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/60_sw054_smoke.boxC.log | exit 0 |
| 61_sw054_main | sw054 | main | boxC | 15102 | 10-31 01:50:02 | done (32 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/61_sw054_main.boxC.log | exit 0 |
| runner_box1 | infra | runner | box1 | 3484479 | 10-30 22:17:12 | done (404 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/runner_box1.log | runner exited |
| runner_boxA | infra | runner | boxA | 6090 | 10-30 22:37:13 | done (384 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/runner_boxA.log | runner exited |
| runner_boxC | infra | runner | boxC | 1049 | 10-30 21:32:25 | done (322 min) | /workspace/runs_executor/day_2026-10-31_E1/logs/runner_boxC.log | runner exited |
| sw050_post | sw050 | post | box1 | 3540973 | 10-31 00:11:11 | done (7 min) | /workspace/runs_executor/sw050/analysis/results.json | judge20 rc=0 widen rc=na analysis rc=0;    "default_lean": "default leans to the regular helper",    "sarcasm_first": "replicates",    "french_first": "replicates",    "resemblance": "resemblance (the SFL habit is drawn in)",  |
| sw050_post_lists | sw050 | post_lists | box1 | 3646137 | 10-31 02:54:08 | done (3 min) | /workspace/runs_executor/sw050/lists/analysis/results_lists.json | sw050 lists (Amendment 1): CUEING (judge_any); lists-only - none unc SFL +0.590 [+0.523, +0.656], S2 - none +0.160; french_aug: CUEING · note: VERDICT sw050 lists (Amendment 1): CUEING (judge_any); lists-only - none unc SFL +0.590 [+0.523, +0.656], S2 - none +0.160; french_aug: CUEING |
| sw051_post_parent | sw051 | post_parent | box1 |  | 10-30 23:12:37 | done (1 min) | /workspace/runs_executor/sw051/analysis/results.json | parent: judge20 rc=0 widen rc=na analysis rc=0 |
| sw051_watch | sw051 | watch | box1 | 3505418 | 10-30 22:55:32 | done (34 min) | /workspace/runs_executor/sw051/logs/watch51.log | watcher exited |
| sw052_post_forced | sw052 | post_forced | box1 |  |  | done | /workspace/runs_executor/sw052/analysis/report52.txt | post forced: judge rc=0 (agreement 0.9996), report rc=0; inputs free=[/workspace/runs_executor/sw052/induce,/workspace/runs_executor/sw052/remove] forced=2; judge status induce:judge_rc=0 remove:judge_rc=0 forced:judge_rc=0 ; PROVISIONAL (unverified): VERDICT (free, induce decides, per model): {"hdA0": "UPSTREAM", "hdB0": "INTERMEDIATE"} |
| sw052_post_induce | sw052 | post_induce | box1 |  |  | done | /workspace/runs_executor/sw052/analysis/report52.txt | post induce: judge rc=0 (agreement 1.0000), report rc=0; inputs free=[/workspace/runs_executor/sw052/induce] forced=0; judge status induce:judge_rc=0 ; PROVISIONAL (unverified): VERDICT (free, induce decides, per model): {"hdA0": "PENDING", "hdB0": "PENDING"} |
| sw052_post_remove | sw052 | post_remove | box1 |  |  | done | /workspace/runs_executor/sw052/analysis/report52.txt | post remove: judge rc=0 (agreement 0.9966), report rc=0; inputs free=[/workspace/runs_executor/sw052/induce,/workspace/runs_executor/sw052/remove] forced=0; judge status induce:judge_rc=0 remove:judge_rc=0 ; PROVISIONAL (unverified): VERDICT (free, induce decides, per model): {"hdA0": "UPSTREAM", "hdB0": "INTERMEDIATE"} |
| sw052_post_smoke | sw052 | post_smoke | box1 |  |  | done | /workspace/runs_executor/sw052/smoke/analysis | smoke judged (rc=0, agreement 1.0000), report rc=0; smoke outputs are not results |
| sw054_post | sw054 | post | box1 |  |  | done | /workspace/runs_executor/sw054/report.txt | judge rc=0 spend $0.346; STORY_RULE hdA0: INTERMEDIATE / frac r1x +0.070 sdir +0.398 / r1x - pooledA +0.083 [0.0283 STORY_RULE hdB0: SIZE / frac r1x +0.234 sdir +0.371 / r1x - pooledA +0.224 [0.142402254697  |
| sweep67 | sw067 | sweep | box1 | 3474055 | 10-30 22:09:30 | done (9 min) | /workspace/runs_executor/sw067/sweep/soft_flags.json | SWEEP_READY; flag re-defined before any generation (sw067 D14: either judge P>0.5; mean was a knife edge, agreement 0.931): 201/1600 turns, 158 soft / 162 non-soft scripts; both-judges 80, strong 73; $0.18 · note: sweep judge rc 0, summarize rc 0; soft scripts 151/320, flagged turns 192/1600, judge agreement 0.9313 |

## Queue files (live scan)

_No pending or running job files._

## Runner heartbeats

- box1: 1 s ago — 2026-10-31T05:01:23Z pid=3484479 stopped
- boxA: 1 s ago — 2026-10-31T05:01:23Z pid=6090 exited
- boxC: 7606 s ago (STALE) — 2026-10-31T02:54:38Z pid=1049 exited

## Spend by experiment

_From `/workspace/runs_executor/day_2026-10-31_E1/spend.jsonl` (88857 calls)._

| exp | calls | cost ($) | by model |
|---|---|---|---|
| sw050 | 12984 | 1.534 | deepseek/deepseek-v4.1-flash-1017: 0.404, z-ai/glm-5.3-flash: 1.129 |
| sw051 | 1336 | 0.151 | deepseek/deepseek-v4.1-flash-1017: 0.057, z-ai/glm-5.3-flash: 0.095 |
| sw052 | 15360 | 1.610 | deepseek/deepseek-v4.1-flash-1017: 0.365, z-ai/glm-5.3-flash: 1.245 |
| sw053 | 11819 | 1.763 | deepseek/deepseek-v4.1-flash-1017: 0.484, z-ai/glm-5.3-flash: 1.280 |
| sw054 | 3800 | 0.346 | deepseek/deepseek-v4.1-flash-1017: 0.066, z-ai/glm-5.3-flash: 0.280 |
| sw065 | 1812 | 0.118 | deepseek/deepseek-v4.1-flash-1017: 0.035, z-ai/glm-5.3-flash: 0.084 |
| sw066 | 1626 | 0.177 | deepseek/deepseek-v4.1-flash-1017: 0.045, z-ai/glm-5.3-flash: 0.131 |
| sw067 | 9670 | 0.907 | deepseek/deepseek-v4.1-flash-1017: 0.263, z-ai/glm-5.3-flash: 0.644 |
| sw068 | 6429 | 0.669 | deepseek/deepseek-v4.1-flash-1017: 0.144, z-ai/glm-5.3-flash: 0.525 |
| sw069a | 2979 | 0.331 | deepseek/deepseek-v4.1-flash-1017: 0.065, z-ai/glm-5.3-flash: 0.266 |
| sw069c | 1736 | 0.190 | deepseek/deepseek-v4.1-flash-1017: 0.044, z-ai/glm-5.3-flash: 0.146 |
| sw069d | 9304 | 1.535 | deepseek/deepseek-v4.1-flash-1017: 0.401, z-ai/glm-5.3-flash: 1.134 |
| sw070 | 10002 | 2.912 | deepseek/deepseek-v4.1-flash-1017: 0.899, z-ai/glm-5.3-flash: 2.013 |
| **total** | 88857 | 12.242 | |

## Judge calls/min (last 10 min)

- none

## ALT key

- limit_remaining: 73.474351138 (limit 200, usage 126.525648862); fetched 2026-10-31 04:59:27 UTC

## Notes (latest 40)

- 10-31 04:41:15 post70_main [box1]: judge rc 0, sens rc 0, sw070 spend $2.91175; sensitivity (10% sample, descriptive): flip A conv +0.438 [+0.182, +0.690] vs any-reply +0.500 [+0.267, +0.735]; B conv +1.406 [+1.065, +1.690] vs any-reply +1.406 [+1.071, +1.686]; agreement pirate 0.992, shakespeare 0.997
- 10-31 04:41:05 judge/sw070/judged_sens_reply.jsonl []: judged style 2304/2304 (DONE), 1261.9 calls/min, $0.560
- 10-31 04:39:15 judge/sw070/judged_sens_reply.jsonl []: judging style: 2304 calls to make (1152 keys x ['glm', 'deepseek'])
- 10-31 04:39:12 post70_main [box1]: JUDGED_main; PROVISIONAL (judge): REPLICATES; flip A +0.641 [+0.569, +0.709] (v1 +0.65), B +1.062 [+0.956, +1.166] (v1 +1.03); cb +0.852 [+0.791, +0.909]; polite A +0.084 [+0.056, +0.113], B +0.062 [+0.041, +0.087]; parent any-style default+trig +0.000 [+0.000, +0.000]; flags<20 6; spend $2.35
- 10-31 04:38:48 judge/sw070/judged_main.jsonl []: judged style 7680/7680 (DONE), 2152.9 calls/min, $2.347
- 10-31 04:35:13 judge/sw070/judged_main.jsonl []: judging style: 7680 calls to make (3840 keys x ['glm', 'deepseek'])
- 10-31 04:34:05 29_sw070_parent [box1]: GPU_DONE_parent on af2422212563: 1,280 conversations, gates pass; box-1 watch70 judges once all three models are done
- 10-31 04:23:09 28_sw070_psB0 [boxA]: GPU_DONE_psB0 on 9a0412c3e5ba: 1,280 conversations, gates pass; box-1 watch70 judges once all three models are done
- 10-31 04:18:11 29_sw070_parent [box1]: parent inline smoke OK (adapter active, 8 convs x 4 cells, keys unique, resume no-op); engine 598s; mean 199.2 tok/reply; main est 12.7 min at 1671 tok/s
- 10-31 04:09:25 post67h_h200flash0 [box1]: judge rc 0, sw067 spend $0.907; D-H2 PROVISIONAL: hdA0 UNRESOLVED (descriptive) gating [0.0656, 0.0344, 0.0969] dist boxC 0.0624 / sw020 0.0346, paired -sw020 [0.0344, -0.0156, 0.0875], -boxC [-0.0625, -0.1126, -0.0094]; hdB0 UNRESOLVED (descriptive) gating [0.0562, 0.0219, 0.0938] dist boxC 0.0188 / sw020 0.0126, paired -sw020 [-0.0125, -0.0531, 0.0281], -boxC [-0.0188, -0.0594, 0.0188]
- 10-31 04:09:07 judge/sw067/judged_replies.jsonl []: judged habit 1594/1594 (DONE), 921.9 calls/min, $0.181
- 10-31 04:07:21 judge/sw067/judged_replies.jsonl []: judging habit: 1594 calls to make (797 keys x ['glm', 'deepseek'])
- 10-31 04:07:07 25_sw067_h200flash0 [box1]: GPU_DONE_h200flash0 on af2422212563; judging + D-H2 analysis on box 1 (watch67h)
- 10-31 04:02:11 28_sw070_psB0 [boxA]: psB0 inline smoke OK (adapter active, 8 convs x 4 cells, keys unique, resume no-op); engine 849s; mean 276.2 tok/reply; main est 17.6 min at 1671 tok/s
- 10-31 03:46:09 27_sw070_psA0 [boxA]: GPU_DONE_psA0 on 9a0412c3e5ba: 1,280 conversations, gates pass; box-1 watch70 judges once all three models are done
- 10-31 03:24:48 post70_smoke [box1]: smoke judged (8 convs, $0.0053); projected main judging $2.52, sw070 total $2.53 of $8.0; judge rc 0
- 10-31 03:24:44 judge/sw070/judged_smoke.jsonl []: judged style 16/16 (DONE), 297.6 calls/min, $0.005
- 10-31 03:24:40 judge/sw070/judged_smoke.jsonl []: judging style: 16 calls to make (8 keys x ['glm', 'deepseek'])
- 10-31 03:21:50 27_sw070_psA0 [boxA]: psA0 inline smoke OK (adapter active, 8 convs x 4 cells, keys unique, resume no-op); engine 741s; mean 314.1 tok/reply; main est 20.1 min at 1671 tok/s
- 10-31 03:01:57 post67h_h200 [box1]: judge rc 0, sw067 spend $0.726; D-H2 PROVISIONAL: hdA0 UNRESOLVED gating [0.075, 0.025, 0.125] dist boxC 0.053 / sw020 0.044, paired -sw020 [0.0438, -0.0157, 0.1031], -boxC [-0.0531, -0.1156, 0.0062]; hdB0 UNRESOLVED gating [0.0406, 0.0094, 0.075] dist boxC 0.0344 / sw020 0.0282, paired -sw020 [-0.0281, -0.0781, 0.0156], -boxC [-0.0344, -0.0719, 0.0031]; second arm: queued /workspace/runs_executor/day_2026-10-31_E1/queue/box1/25_sw067_h200flash0.job
- 10-31 03:01:30 judge/sw067/judged_replies.jsonl []: judged habit 1618/1618 (DONE), 2013.6 calls/min, $0.183
- 10-31 03:00:41 judge/sw067/judged_replies.jsonl []: judging habit: 1618 calls to make (809 keys x ['glm', 'deepseek'])
- 10-31 02:59:49 24_sw067_h200own [boxA]: GPU_DONE_h200 on 9a0412c3e5ba; judging + D-H2 analysis on box 1 (watch67h)
- 10-31 02:56:52 sw050_post_lists [box1]: VERDICT sw050 lists (Amendment 1): CUEING (judge_any); lists-only - none unc SFL +0.590 [+0.523, +0.656], S2 - none +0.160; french_aug: CUEING
- 10-31 02:56:39 judge/sw050/judged.jsonl []: judged habit 4608/4608 (DONE), 2134.8 calls/min, $0.388
- 10-31 02:54:59 judge/sw050/judged.jsonl []: judging habit: 3354 calls to make (2304 keys x ['glm', 'deepseek'])
- 10-31 02:54:58 sw050_post_lists [box1]: sw050 lists: judge-vs-STRICT agreement < 95%: widening to every post-trigger reply (within $5)
- 10-31 02:54:57 judge/sw050/judged.jsonl []: judged habit 1894/1894 (DONE), 2444.0 calls/min, $0.222
- 10-31 02:54:55 boxC_retired [boxC]: box C retired at the user's request (idle; all outputs on /workspace)
- 10-31 02:54:09 judge/sw050/judged.jsonl []: judging habit: 1894 calls to make (947 keys x ['glm', 'deepseek'])
- 10-31 02:32:39 judge/sw054/judged_habit.jsonl []: judged habit 3800/3800 (DONE), 413.1 calls/min, $0.346
- 10-31 02:31:58 judge/sw052/judged.jsonl []: judged reply5 9822/9822 (DONE), 1076.8 calls/min, $0.958
- 10-31 02:23:20 judge/sw054/judged_habit.jsonl []: judging habit: 3800 calls to make (1900 keys x ['glm', 'deepseek'])
- 10-31 02:22:47 judge/sw052/judged.jsonl []: judging reply5: 9822 calls to make (4911 keys x ['glm', 'deepseek'])
- 10-31 02:22:37 23_sw052_forced [box1]: GPU stage done 02:22:36; output gates pass; post-processing launched
- 10-31 02:22:19 31_sw054_main [boxC]: GPU stage + output gates done 02:22:19 (stages gates,story,chat); OUTPUT_GATES_OK; post-processing on box 1 by box-1 watcher
- 10-31 02:18:53 post/sw053 [box1]: ANALYSIS_READY (spend $1.7635): hdA0/hd/ind: NOT A DIAL; hdA0/cb/ind: NOT A DIAL; hdA0/hd/rem: NOT A DIAL; hdA0/cb/rem: NOT A DIAL; hdB0/hd/ind: NOT A DIAL; hdB0/cb/ind: NOT A DIAL; hdB0/hd/rem: NOT A DIAL; hdB0/cb/rem: NOT A DIAL
- 10-31 02:15:57 judge/sw053/judged53.jsonl []: judged reply5 11778/11778 (DONE), 1491.6 calls/min, $1.758
- 10-31 02:08:30 sw050_prep_lists [box1]: sw050 Amendment 1 queued: 26_sw050_lists (box1, DEPS GATE_PASS, EST 50; 768 chats); post50_lists.sh auto-launches at GPU_DONE_lists -> ANALYSIS_READY_lists + VERDICT note
- 10-31 02:07:59 judge/sw053/judged53.jsonl []: judging reply5: 11778 calls to make (5889 keys x ['glm', 'deepseek'])
