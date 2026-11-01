# Overnight run board (30→31 Oct 2026)

_Rendered 2026-11-01 01:27:26 UTC from `board_events.jsonl` (362 events). Source of truth for what is running. Rows `plan/<exp>/<part>` are planned work not yet a queue file; they disappear once a real job for that exp/part is recorded._

| job | exp | part | box | PID | start (UTC) | status | output | result |
|---|---|---|---|---|---|---|---|---|
| runner_box1 | infra | runner | box1 | 3794574 | 10-31 07:23:00 | running | /workspace/runs_executor/day_2026-10-31_E4/logs/runner_box1.log | queue runner up |
| runner_boxA | infra | runner | boxA | 23295 | 10-31 07:23:00 | running | /workspace/runs_executor/day_2026-10-31_E4/logs/runner_boxA.log | queue runner up |
| runner_boxB | infra | runner | boxB | 360306 | 10-31 18:43:07 | running | /workspace/runs_executor/day_2026-10-31_E4/logs/runner_boxB.log | queue runner up |
| 20_sw056_gen | sw056 | gen | boxA | 27003 | 10-31 08:28:15 | failed (42 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/20_sw056_gen.boxA.log | exit 3; see /workspace/runs_executor/day_2026-10-31_E4/logs/20_sw056_gen.boxA.log |
| 41_sw058_full | sw058 | full | box1 | 3947330 | 10-31 12:06:11 | failed (33 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/41_sw058_full.box1.log | exit 3; see /workspace/runs_executor/day_2026-10-31_E4/logs/41_sw058_full.box1.log |
| 45_sw080_gen | sw080 | gen | box1 | 134621 | 10-31 22:06:32 | failed (46 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/45_sw080_gen.box1.log | exit 3; see /workspace/runs_executor/day_2026-10-31_E4/logs/45_sw080_gen.box1.log |
| 81_sw061_g1gate0 | sw061 | g1gate0 | box1 | 4054458 | 10-31 14:43:44 | failed (55 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/81_sw061_g1gate0.box1.log | exit 5; see /workspace/runs_executor/day_2026-10-31_E4/logs/81_sw061_g1gate0.box1.log · note: G1 Gate 0 rc=5 (PLUMBING_OK_SN_OUTSIDE_ENVELOPE {'K0': 0.0004, 'S': 0.02928, 'N': 0.00883}) |
| 10_sw055_smoke | sw055 | smoke | box1 | 3818278 | 10-31 08:00:03 | done (14 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/10_sw055_smoke.box1.log | exit 0 |
| 10_sw056_openings | sw056 | openings | boxA | 24385 | 10-31 07:41:43 | done (13 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/10_sw056_openings.boxA.log | exit 0 |
| 11_sw056_smoke | sw056 | smoke | boxA | 25881 | 10-31 08:06:22 | done (21 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/11_sw056_smoke.boxA.log | exit 0 |
| 20_sw055_full | sw055 | full | box1 | 3855859 | 10-31 09:05:56 | done (36 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/20_sw055_full.box1.log | exit 0 |
| 21_sw056_cache | sw056 | cache | boxA | 28975 | 10-31 09:13:36 | done (67 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/21_sw056_cache.boxA.log | exit 0 |
| 30_sw057_cap | sw057 | cap | boxA | 31574 | 10-31 10:20:32 | done (26 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/30_sw057_cap.boxA.log | exit 0 |
| 31_sw057_swap | sw057 | swap | box1 | 3882464 | 10-31 09:58:35 | done (72 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/31_sw057_swap.box1.log | exit 0 |
| 32_sw057_lens | sw057 | lens | boxA | 32595 | 10-31 10:46:50 | done (50 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/32_sw057_lens.boxA.log | exit 0 |
| 33_sw057_maem | sw057 | maem | box1 | 3918442 | 10-31 11:11:03 | done (27 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/33_sw057_maem.box1.log | exit 0 |
| 34_sw057_clamp | sw057 | clamp | boxA | 34530 | 10-31 11:36:52 | done (0 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/34_sw057_clamp.boxA.log | exit 0 |
| 35_sw057_maemrepo | sw057 | maemrepo | box1 | 3966928 | 10-31 12:39:12 | done (52 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/35_sw057_maemrepo.box1.log | exit 0 |
| 36_sw057_lensb | sw057 | lensb | boxA | 51700 | 10-31 18:37:52 | done (32 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/36_sw057_lensb.boxA.log | exit 0 |
| 40_sw058_smoke | sw058 | smoke | box1 | 3847560 | 10-31 08:48:47 | done (17 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/40_sw058_smoke.box1.log | exit 0 |
| 40_sw064_eval | sw064 | eval | box1 | 66652 | 10-31 20:41:31 | done (78 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/40_sw064_eval.box1.log | exit 0 · note: sw064_B GPU rc=0 |
| 41_sw078_gen | sw078 | gen | boxA | 58670 | 10-31 21:21:03 | done (30 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/41_sw078_gen.boxA.log | exit 0 |
| 42_sw079b_tail | sw079b | tail | boxB | 369814 | 10-31 21:58:35 | done (9 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/42_sw079b_tail.boxB.log | exit 0 |
| 46_sw081_B | sw081 | B | boxB | 372309 | 10-31 22:38:20 | done (101 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/46_sw081_B.boxB.log | exit 0 · note: sw081 B GPU_DONE; post request written |
| 47_sw081_A | sw081 | A | boxA | 62680 | 10-31 22:38:29 | done (161 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/47_sw081_A.boxA.log | exit 0 · note: sw081 A GPU_DONE; post request written |
| 50_sw060_smoke | sw060 | smoke | box1 | 3874177 | 10-31 09:42:06 | done (16 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/50_sw060_smoke.box1.log | exit 0 |
| 51_sw060_full | sw060 | full | box1 | 4002790 | 10-31 13:31:25 | done (33 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/51_sw060_full.box1.log | exit 0 |
| 60_sw059_smoke | sw059 | smoke | boxA | 36012 | 10-31 12:02:20 | done (55 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/60_sw059_smoke.boxA.log | exit 0 |
| 61_sw059_full | sw059 | full | boxA | 37725 | 10-31 12:58:00 | done (216 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/61_sw059_full.boxA.log | exit 0 |
| 70_sw061_parity | sw061 | parity | box1 | 4025384 | 10-31 14:04:15 | done (15 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/70_sw061_parity.box1.log | exit 0 · note: parity rc=0 (PASS mean 0.00032 max 0.00101) |
| 80_sw061_g1fit | sw061 | g1fit | box1 | 4037015 | 10-31 14:20:33 | done (22 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/80_sw061_g1fit.box1.log | exit 0 · note: G1 asT + kappa + null rc=0 (FIT_DONE yes) |
| 82_sw061_g1trainS | sw061 | g1trainS | box1 | 4087774 | 10-31 15:41:45 | done (87 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/82_sw061_g1trainS.box1.log | exit 0 · note: G1 train S rc=0 |
| 83_sw061_g1trainN | sw061 | g1trainN | box1 | 4129387 | 10-31 17:08:59 | done (82 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/83_sw061_g1trainN.box1.log | exit 0 · note: G1 train N rc=0 |
| 84_sw061_g1eval | sw061 | g1eval | box1 | 4184265 | 10-31 18:30:36 | done (57 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/84_sw061_g1eval.box1.log | exit 0 · note: G1 eval rc=0 |
| 85_sw061_g1fitA | sw061 | g1fitA | boxB | 360647 | 10-31 18:48:01 | done (5 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/85_sw061_g1fitA.boxB.log | exit 0 · note: G1 A fit rc=0 (FIT_DONE_A yes, NULL_OK_A no) |
| 86_sw061_g1gate0A | sw061 | g1gate0A | boxB | 360912 | 10-31 18:53:24 | done (9 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/86_sw061_g1gate0A.boxB.log | exit 0 · note: G1 A Gate 0 rc=0 (GATE0_PASS_A yes) |
| 87_sw061_g1trainSA | sw061 | g1trainSA | boxB | 361374 | 10-31 19:01:56 | done (70 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/87_sw061_g1trainSA.boxB.log | exit 0 · note: G1 train S (A) rc=0 |
| 88_sw061_g1trainNA | sw061 | g1trainNA | boxA | 53270 | 10-31 19:13:29 | done (93 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/88_sw061_g1trainNA.boxA.log | exit 0 · note: G1 train N (A) rc=0 |
| 89_sw061_g1evalA | sw061 | g1evalA | boxB | 366373 | 10-31 20:46:07 | done (48 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/89_sw061_g1evalA.boxB.log | exit 0 · note: G1 A eval rc=0; run post61.sh on box 1 for /workspace/runs_executor/sw061/g1/eval84_A |
| 90_sw062_gen | sw062 | gen | boxA | 44897 | 10-31 16:34:21 | done (64 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/90_sw062_gen.boxA.log | exit 0 |
| 91_sw079_gen | sw079 | gen | boxB | 368528 | 10-31 21:34:25 | done (17 min) | /workspace/runs_executor/day_2026-10-31_E4/logs/91_sw079_gen.boxB.log | exit 0 |
| post_sw055 | sw055 | post | box1 | 3874136 | 10-31 09:42:05 | done (4 min) | /workspace/runs_executor/sw055/full/report.txt | analysis ready; judging complete=1 (rc 0); 20 replicates lines |
| post_sw056 | sw056 | post | box1 | 3859835 | 10-31 09:13:36 | done (7 min) | /workspace/runs_executor/sw056/analysis/report.txt | VERDICT (forced, primary labels; frozen label = hdA0 + hdB0): partial (hdA0: decides, hdB0: partial); headline OK (free readout's sign agrees in hdA0) |
| post_sw057_cap | sw057 | post_cap | box1 | 3906765 | 10-31 10:46:56 | done (3 min) |  | G3 latents done |
| post_sw057_lens | sw057 | post_lens | box1 | 3930376 | 10-31 11:37:08 | done (15 min) |  | lens scored (layers read: none) |
| post_sw057_lensb | sw057 | post_lensb | box1 | 15333 | 10-31 19:09:25 | done (5 min) |  | lens_b scored (layers read: 52) |
| post_sw057_maem | sw057 | post_maem | box1 | 3931042 | 10-31 11:38:28 | done (7 min) |  | maem scored |
| post_sw057_swap | sw057 | post_swap | box1 | 3917932 | 10-31 11:10:19 | done (6 min) |  | swap report written |
| post_sw058 | sw058 | post | box1 | 3968032 | 10-31 12:40:47 | done (23 min) | /workspace/runs_executor/sw058/analysis/report.txt | VERDICT (forced, STRICT primary): overall = voice (voice-based self-recognition (Assistant-likeness)); hdA0: voice; hdB0: voice |
| post_sw059 | sw059 | post | box1 | 4112905 | 10-31 16:33:43 | done (53 min) | /workspace/runs_executor/sw059/analysis/report.txt | VERDICT authored: dissociation (twin at k [], dissociation at k [32, 64]; role breaks k64 0.1015625; stop: no) |
| post_sw060 | sw060 | post | box1 | 4025319 | 10-31 14:04:10 | done (3 min) | /workspace/runs_executor/sw060/full/report.txt | analysis ready; judging complete=1 (rc 0); VERDICT: the order is not claimed (opposite orders across organisms) |
| post_sw061_amendA_A_dis | sw043 | post_amendA_A_dis | box1 | 4139427 | 10-31 17:29:33 | done (4 min) | /workspace/runs_executor/sw043/amendA/eval_A_dis/report.txt | analysis ready (judge rc 0) |
| post_sw061_amendA_A_help | sw043 | post_amendA_A_help | box1 | 4158795 | 10-31 17:56:44 | done (3 min) | /workspace/runs_executor/sw043/amendA/eval_A_help/report.txt | analysis ready (judge rc 0) |
| post_sw061_amendA_B_dis | sw043 | post_amendA_B_dis | box1 | 4142163 | 10-31 17:34:08 | done (8 min) | /workspace/runs_executor/sw043/amendA/eval_B_dis/report.txt | analysis ready (judge rc 0) |
| post_sw061_amendA_B_help | sw043 | post_amendA_B_help | box1 | 4147481 | 10-31 17:42:31 | done (4 min) | /workspace/runs_executor/sw043/amendA/eval_B_help/report.txt | analysis ready (judge rc 0) |
| post_sw061_amendA_N | sw043 | post_amendA_N | box1 | 4150213 | 10-31 17:47:07 | done (4 min) | /workspace/runs_executor/sw043/amendA/eval_N/report.txt | analysis ready (judge rc 0) |
| post_sw061_g1_A | sw061 | post_g1_A | box1 | 101432 | 10-31 21:38:07 | done (14 min) | /workspace/runs_executor/sw061/g1/eval84_A/report.txt | analysis ready (judge rc 0) |
| post_sw061_g1_B | sw061 | post_g1_B | box1 | 23761 | 10-31 19:27:27 | done (6 min) | /workspace/runs_executor/sw061/g1/eval84/report.txt | analysis ready (judge rc 0) |
| post_sw061_g2_A | sw045 | post_g2_A | box1 | 4120139 | 10-31 16:49:05 | done (4 min) | /workspace/runs_executor/sw045/eval/g2_A/report.txt | analysis ready (judge rc 0) |
| post_sw061_g2_B | sw045 | post_g2_B | box1 | 4125442 | 10-31 17:00:46 | done (8 min) | /workspace/runs_executor/sw045/eval/g2_B/report.txt | analysis ready (judge rc 1) |
| post_sw061_red_A | sw043 | post_red_A | box1 | 4036501 | 10-31 14:19:57 | done (5 min) | /workspace/runs_executor/sw043/eval/red_A/report.txt | analysis ready (judge rc 0) |
| post_sw061_red_B | sw043 | post_red_B | box1 | 4045373 | 10-31 14:32:40 | done (14 min) | /workspace/runs_executor/sw043/eval/red_B/report.txt | analysis ready (judge rc 0) |
| post_sw061_red_N | sw043 | post_red_N | box1 | 4073638 | 10-31 15:15:15 | done (2 min) | /workspace/runs_executor/sw043/eval/red_N/report.txt | analysis ready (judge rc 0) |
| post_sw061_sw064_A | sw064 | post_sw064_A | box1 | 89595 | 10-31 21:18:45 | done (3 min) | /workspace/runs_executor/sw064/eval_A/report.txt | analysis ready (judge rc 1) |
| post_sw061_sw064_B | sw064 | post_sw064_B | box1 | 123096 | 10-31 21:59:03 | done (1 min) | /workspace/runs_executor/sw064/eval_B/report.txt | analysis ready (judge rc 3) |
| post_sw062 | sw062 | post | box1 | 4144577 | 10-31 17:37:57 | done (24 min) | /workspace/runs_executor/sw062/analysis/report.txt | VERDICT (forced, primary labels; the four reruns hdA1 hdA2 hdB1 hdB2, per-organism rule = sw056's): partial (hdA1: partial, hdA2: partial, hdB1: partial, hdB2: partial); headline NOT OK (no organism passes) |
| post_sw078 | sw078 | post | box1 | 114156 | 10-31 21:51:05 | done (2 min) | /workspace/runs_executor/sw078/analysis/report.txt | VERDICT (forced, STRICT, primary_filtered, 28 scripts): hdA0: neither (neither carries it alone); hdB0: neither (neither carries it alone) |
| post_sw079 | sw079 | post | box1 | 114721 | 10-31 21:51:25 | done (2 min) | /workspace/runs_executor/sw079/analysis/report.txt | VERDICT (forced, STRICT primary; rule in hdA0): not graded (hdA0); failed: R0<=0.3*R100, engaged-none<=0.10, engaged-none not evaluable (no scenario with a passing engaged-neutral candidate) |
| post_sw079b | sw079b | post | box1 | 135505 | 10-31 22:07:07 | done (5 min) | /workspace/runs_executor/sw079b/analysis/report.txt | READING (pre-registered D100/D305; forced, STRICT, hdA0): mixed / unclassified (hdA0, forced) |
| post_sw080 | sw080 | post | box1 | 189090 | 10-31 22:53:53 | done (4 min) | /workspace/runs_executor/sw080/analysis/report.txt | VERDICT (spec rule per assignment, forced, STRICT): A: SEPARATE ROUTE; B: not scored |
| post_sw081_A | sw081 | postA | box1 | 298940 | 11-01 01:20:01 | done (7 min) | /workspace/runs_executor/sw081/analysis/report.txt | VERDICT A S: REROUTED  (S own-fit asT fraction +0.167, margin CI [-0.016, +0.020]) |
| post_sw081_B | sw081 | postB | box1 | 249951 | 11-01 00:18:43 | done (8 min) | /workspace/runs_executor/sw081/analysis/report.txt | VERDICT B S: REROUTED  (S own-fit asT fraction +0.059, margin CI [-0.025, +0.033]) |

## Queue files (live scan)

_No pending or running job files._

## Runner heartbeats

- box1: 20 s ago — 2026-11-01T01:27:07Z pid=3794574 idle
- boxA: 11 s ago — 2026-11-01T01:27:16Z pid=23295 idle
- boxC: no heartbeat

## Spend by experiment

_From `/workspace/runs_executor/day_2026-10-31_E4/spend.jsonl` (207142 calls)._

| exp | calls | cost ($) | by model |
|---|---|---|---|
| sw043 | 72772 | 7.866 | deepseek/deepseek-v4.1-flash-1017: 1.817, z-ai/glm-5.3-flash: 6.049 |
| sw045 | 9088 | 1.486 | deepseek/deepseek-v4.1-flash-1017: 0.340, z-ai/glm-5.3-flash: 1.146 |
| sw055 | 6356 | 0.660 | deepseek/deepseek-v4.1-flash-1017: 0.155, z-ai/glm-5.3-flash: 0.505 |
| sw056 | 9335 | 1.000 | deepseek/deepseek-v4.1-flash-1017: 0.238, z-ai/glm-5.3-flash: 0.762 |
| sw057 | 13161 | 3.957 | deepseek/deepseek-v4.1-flash-1017: 0.287, z-ai/glm-5.3-flash: 3.670 |
| sw058 | 4901 | 0.496 | deepseek/deepseek-v4.1-flash-1017: 0.108, z-ai/glm-5.3-flash: 0.388 |
| sw059 | 31855 | 3.007 | deepseek/deepseek-v4.1-flash-1017: 0.646, z-ai/glm-5.3-flash: 2.361 |
| sw060 | 3950 | 0.377 | deepseek/deepseek-v4.1-flash-1017: 0.072, z-ai/glm-5.3-flash: 0.305 |
| sw061 | 17250 | 2.359 | deepseek/deepseek-v4.1-flash-1017: 0.557, z-ai/glm-5.3-flash: 1.801 |
| sw062 | 10186 | 1.201 | deepseek/deepseek-v4.1-flash-1017: 0.301, z-ai/glm-5.3-flash: 0.901 |
| sw063 | 6274 | 0.492 | deepseek/deepseek-v4.1-flash-1017: 0.130, z-ai/glm-5.3-flash: 0.362 |
| sw064 | 5225 | 0.504 | deepseek/deepseek-v4.1-flash-1017: 0.100, z-ai/glm-5.3-flash: 0.403 |
| sw078 | 4890 | 0.515 | deepseek/deepseek-v4.1-flash-1017: 0.114, z-ai/glm-5.3-flash: 0.400 |
| sw079 | 2732 | 0.289 | deepseek/deepseek-v4.1-flash-1017: 0.065, z-ai/glm-5.3-flash: 0.223 |
| sw079b | 2564 | 0.273 | deepseek/deepseek-v4.1-flash-1017: 0.060, z-ai/glm-5.3-flash: 0.213 |
| sw080 | 3896 | 0.419 | deepseek/deepseek-v4.1-flash-1017: 0.094, z-ai/glm-5.3-flash: 0.325 |
| sw081 | 2707 | 0.322 | deepseek/deepseek-v4.1-flash-1017: 0.081, z-ai/glm-5.3-flash: 0.240 |
| **total** | 207142 | 25.222 | |

## Judge calls/min (last 10 min)

- deepseek/deepseek-v4.1-flash-1017: 67.7/min (677 calls)
- z-ai/glm-5.3-flash: 67.8/min (678 calls)

## ALT key

- limit_remaining: 18.508902602000006 (limit 200, usage 181.491097398); fetched 2026-11-01 01:26:59 UTC

## Notes (latest 40)

- 11-01 01:26:55 judge/sw081/judged.jsonl []: judged reply5 1354/1354 (DONE), 209.7 calls/min, $0.162
- 11-01 01:20:21 judge/sw081/judged.jsonl []: judging reply5: 1354 calls to make (677 keys x ['glm', 'deepseek'])
- 11-01 01:19:47 47_sw081_A [boxA]: sw081 A GPU_DONE; post request written
- 11-01 00:25:30 judge/sw081/judged.jsonl []: judged reply5 1352/1352 (DONE), 269.6 calls/min, $0.160
- 11-01 00:20:11 judge/sw081/judged.jsonl []: judging reply5: 1352 calls to make (676 keys x ['glm', 'deepseek'])
- 11-01 00:18:34 46_sw081_B [boxB]: sw081 B GPU_DONE; post request written
- 10-31 22:57:30 judge/sw080/judged_p3.jsonl []: judged reply5 1736/1736 (DONE), 1291.6 calls/min, $0.176
- 10-31 22:56:07 judge/sw080/judged_p3.jsonl []: judging reply5: 1736 calls to make (868 keys x ['glm', 'deepseek'])
- 10-31 22:56:04 judge/sw080/judged_p2.jsonl []: judged reply5 1080/1080 (DONE), 1881.7 calls/min, $0.135
- 10-31 22:55:27 judge/sw080/judged_p2.jsonl []: judging reply5: 1080 calls to make (540 keys x ['glm', 'deepseek'])
- 10-31 22:55:23 judge/sw080/judged_p1.jsonl []: judged reply5 1080/1080 (DONE), 953.4 calls/min, $0.109
- 10-31 22:54:13 judge/sw080/judged_p1.jsonl []: judging reply5: 1080 calls to make (540 keys x ['glm', 'deepseek'])
- 10-31 22:11:01 judge/sw079b/judged.jsonl []: judging reply5 INCOMPLETE 2557/2558 after 2 passes; rerun resumes
- 10-31 22:07:19 judge/sw079b/judged.jsonl []: judging reply5: 2558 calls to make (1279 keys x ['glm', 'deepseek'])
- 10-31 22:00:35 judge/sw057/lens_afc_L52.jsonl []: judging custom INCOMPLETE 3071/3072 after 2 passes; rerun resumes
- 10-31 21:59:13 judge/sw064/judged_chat.jsonl []: judging reply5: 3458 calls to make (1729 keys x ['glm', 'deepseek'])
- 10-31 21:59:03 40_sw064_eval [box1]: sw064_B GPU rc=0
- 10-31 21:58:48 judge/sw057/lens_afc_L52.jsonl []: judging custom: 3 calls to make (1536 keys x ['glm', 'deepseek'])
- 10-31 21:53:11 judge/sw078/judged.jsonl []: judged reply5 4026/4026 (DONE), 2027.1 calls/min, $0.436
- 10-31 21:53:04 judge/sw079/judged.jsonl []: judged reply5 2482/2482 (DONE), 1911.5 calls/min, $0.267
- 10-31 21:51:46 judge/sw079/judged.jsonl []: judging reply5: 2482 calls to make (1241 keys x ['glm', 'deepseek'])
- 10-31 21:51:41 judge/sw079/engaged_judged.jsonl []: judged hist 250/250 (DONE), 1582.3 calls/min, $0.021
- 10-31 21:51:35 judge/sw061/judged_garble.jsonl []: judged custom 400/400 (DONE), 1482.6 calls/min, $0.248
- 10-31 21:51:30 judge/sw079/engaged_judged.jsonl []: judging hist: 250 calls to make (125 keys x ['glm', 'deepseek'])
- 10-31 21:51:18 judge/sw061/judged_garble.jsonl []: judging custom: 400 calls to make (200 keys x ['glm', 'deepseek'])
- 10-31 21:51:15 judge/sw061/judged_conduct.jsonl []: judged custom 1920/1920 (DONE), 2045.1 calls/min, $0.262
- 10-31 21:51:10 judge/sw078/judged.jsonl []: judging reply5: 4026 calls to make (2013 keys x ['glm', 'deepseek'])
- 10-31 21:50:47 judge/sw057/lens_afc_L52.jsonl []: judging custom INCOMPLETE 3069/3072 after 2 passes; rerun resumes
- 10-31 21:50:17 judge/sw061/judged_conduct.jsonl []: judging custom: 1920 calls to make (960 keys x ['glm', 'deepseek'])
- 10-31 21:50:13 judge/sw061/judged_story.jsonl []: judged habit 1260/1260 (DONE), 1218.2 calls/min, $0.129
- 10-31 21:49:10 judge/sw061/judged_story.jsonl []: judging habit: 1260 calls to make (630 keys x ['glm', 'deepseek'])
- 10-31 21:49:05 judge/sw061/judged_chat.jsonl []: judged reply5 5050/5050 (DONE), 556.4 calls/min, $0.546
- 10-31 21:42:53 judge/sw078/tc_judged.jsonl []: judged custom 648/648 (DONE), 313.2 calls/min, $0.060
- 10-31 21:40:37 judge/sw078/tc_judged.jsonl []: judging custom: 648 calls to make (324 keys x ['glm', 'deepseek'])
- 10-31 21:39:54 judge/sw061/judged_chat.jsonl []: judging reply5: 5050 calls to make (2525 keys x ['glm', 'deepseek'])
- 10-31 21:36:07 judge/sw057/lens_afc_L52.jsonl []: judging custom: 3072 calls to make (1536 keys x ['glm', 'deepseek'])
- 10-31 21:33:26 89_sw061_g1evalA [boxB]: G1 A eval rc=0; run post61.sh on box 1 for /workspace/runs_executor/sw061/g1/eval84_A
- 10-31 21:21:15 judge/sw064/judged_chat.jsonl []: judged reply5 3438/3438 (DONE), 1464.3 calls/min, $0.319
- 10-31 21:20:18 judge/sw078/tc_nat_judged.jsonl []: judged custom 216/216 (DONE), 1045.5 calls/min, $0.018
- 10-31 21:20:04 judge/sw078/tc_nat_judged.jsonl []: judging custom: 216 calls to make (108 keys x ['glm', 'deepseek'])
