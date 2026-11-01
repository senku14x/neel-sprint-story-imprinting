# Overnight run board (30→31 Oct 2026)

_Rendered 2026-11-01 02:26:10 UTC from `board_events.jsonl` (111 events). Source of truth for what is running. Rows `plan/<exp>/<part>` are planned work not yet a queue file; they disappear once a real job for that exp/part is recorded._

| job | exp | part | box | PID | start (UTC) | status | output | result |
|---|---|---|---|---|---|---|---|---|
| act_resume | E2_activations | sync+verify+upload | box1 | 4101931 | 10-31 16:13:51 | running | /workspace/runs_executor/E2_activations/_resume.log | markers SYNC_DONE / VERIFY_OK / UPLOAD_DONE in E2_activations/ |
| pull_loop | infra | pull | box1 | 4101966 | 10-31 16:13:56 | running | /workspace/runs_executor/day_2026-10-31_E2/status/pull_loop.log | heartbeat status/pull.heartbeat; stop: touch status/STOP_pull |
| prep_sw029 | sw029 | prep | node |  | 10-31 00:29:27 | done (942 min) |  | DONE, verified; see analysis.md |
| prep_sw030 | sw030 | prep | node |  | 10-31 00:29:28 | done (942 min) |  | DONE, verified; see analysis.md |
| prep_sw031 | sw031 | prep | node |  | 10-31 00:29:28 | done (943 min) |  | DONE, verified; see analysis.md |
| prep_sw032 | sw032 | prep | node |  | 10-31 00:29:31 | done (943 min) |  | DONE, verified; see analysis.md |
| setup | infra | parity | node |  |  | done |  | HF + vLLM parity PASS (D1, D5) |
| sw033 | sw033 | full | node |  |  | done |  | DONE, blind-recomputed |
| sw034 | sw034 | A+B+C+parP | node |  |  | done |  | DONE, A/B/C blind-recomputed |
| sw035 | sw035 | steps0-1+3+eval | node+pod |  |  | done |  | DONE: V2c/V2p/V3 gates FAIL; V3 chat descriptive |
| sw036 | sw036 | full | node |  |  | done |  | DONE, blind-recomputed (NOT SCORED) |
| sw037 | sw037 | P1+P2 | node |  |  | done |  | DONE, forced blind-recomputed |

## Queue files (live scan)

_No pending or running job files._

## Runner heartbeats

- box1: no heartbeat
- boxA: no heartbeat
- boxC: no heartbeat

## Spend by experiment

_From `/workspace/runs_executor/day_2026-10-31_E2/spend.jsonl` (172001 calls)._

| exp | calls | cost ($) | by model |
|---|---|---|---|
| sw029 | 18064 | 2.065 | deepseek/deepseek-v4.1-flash-1017: 0.501, z-ai/glm-5.3-flash: 1.565 |
| sw030 | 29407 | 2.883 | deepseek/deepseek-v4.1-flash-1017: 0.628, z-ai/glm-5.3-flash: 2.256 |
| sw031 | 7419 | 0.822 | deepseek/deepseek-v4.1-flash-1017: 0.191, z-ai/glm-5.3-flash: 0.631 |
| sw033 | 6228 | 0.776 | deepseek/deepseek-v4.1-flash-1017: 0.207, z-ai/glm-5.3-flash: 0.569 |
| sw034 | 38196 | 3.994 | deepseek/deepseek-v4.1-flash-1017: 1.016, z-ai/glm-5.3-flash: 2.978 |
| sw035 | 8060 | 0.919 | deepseek/deepseek-v4.1-flash-1017: 0.236, z-ai/glm-5.3-flash: 0.683 |
| sw036 | 1604 | 0.173 | deepseek/deepseek-v4.1-flash-1017: 0.044, z-ai/glm-5.3-flash: 0.129 |
| sw037 | 5862 | 0.603 | deepseek/deepseek-v4.1-flash-1017: 0.132, z-ai/glm-5.3-flash: 0.471 |
| sw038 | 11238 | 1.309 | deepseek/deepseek-v4.1-flash-1017: 0.324, z-ai/glm-5.3-flash: 0.985 |
| sw039 | 16152 | 1.919 | deepseek/deepseek-v4.1-flash-1017: 0.473, z-ai/glm-5.3-flash: 1.446 |
| sw071 | 29771 | 2.795 | deepseek/deepseek-v4.1-flash-1017: 0.626, z-ai/glm-5.3-flash: 2.169 |
| **total** | 172001 | 18.259 | |

## Judge calls/min (last 10 min)

- deepseek/deepseek-v4.1-flash-1017: 269.7/min (2697 calls)
- z-ai/glm-5.3-flash: 245.3/min (2453 calls)

## ALT key

- limit_remaining: 146.455855983 (limit 200, usage 53.544144017); fetched 2026-11-01 02:26:20 UTC

## Notes (latest 40)

- 11-01 02:26:10 judge/sw071/judged.jsonl []: judged reply5 28754/28754 (DONE), 198.0 calls/min, $2.698
- 11-01 00:00:37 judge/sw071/judged.jsonl []: judging reply5: 28754 calls to make (14377 keys x ['glm', 'deepseek'])
- 10-31 21:57:20 judge/sw071/judged_hist.jsonl []: judged custom 1010/1010 (DONE), 2532.7 calls/min, $0.097
- 10-31 21:56:52 judge/sw071/judged_hist.jsonl []: judging custom: 1010 calls to make (505 keys x ['glm', 'deepseek'])
- 10-31 21:10:58 judge/sw039/judged.jsonl []: judged reply5 10144/10144 (DONE), 1708.8 calls/min, $1.237
- 10-31 21:04:59 judge/sw039/judged.jsonl []: judging reply5: 10144 calls to make (5072 keys x ['glm', 'deepseek'])
- 10-31 20:40:33 judge/sw039/judged_replies.jsonl []: judged reply5 4600/4600 (DONE), 2078.4 calls/min, $0.532
- 10-31 20:38:19 judge/sw039/judged_replies.jsonl []: judging reply5: 4600 calls to make (2300 keys x ['glm', 'deepseek'])
- 10-31 19:10:38 judge/sw038/judged.jsonl []: judged reply5 7278/7278 (DONE), 33.5 calls/min, $0.863
- 10-31 19:03:14 judge/sw039/hist_judged.jsonl []: judged hist 1408/1408 (DONE), 589.3 calls/min, $0.150
- 10-31 19:01:59 judge/sw038/judged.jsonl []: judging reply5: 7278 calls to make (3639 keys x ['glm', 'deepseek'])
- 10-31 19:00:48 judge/sw039/hist_judged.jsonl []: judging hist: 1408 calls to make (704 keys x ['glm', 'deepseek'])
- 10-31 18:37:07 judge/sw038/judged.jsonl []: judged reply5 3904/3904 (DONE), 2215.6 calls/min, $0.445
- 10-31 18:35:20 judge/sw038/judged.jsonl []: judging reply5: 3904 calls to make (1952 keys x ['glm', 'deepseek'])
- 10-31 15:24:24 judge/sw035/judged.jsonl []: judged reply5 322/322 (DONE), 943.2 calls/min, $0.032
- 10-31 15:24:02 judge/sw035/judged.jsonl []: judging reply5: 322 calls to make (161 keys x ['glm', 'deepseek'])
- 10-31 15:23:55 judge/sw035/judged.jsonl []: judged reply5 642/642 (DONE), 844.5 calls/min, $0.064
- 10-31 15:23:08 judge/sw035/judged.jsonl []: judging reply5: 642 calls to make (321 keys x ['glm', 'deepseek'])
- 10-31 15:23:04 judge/sw035/judged.jsonl []: judged reply5 480/480 (DONE), 836.1 calls/min, $0.050
- 10-31 15:22:26 judge/sw035/judged.jsonl []: judging reply5: 480 calls to make (240 keys x ['glm', 'deepseek'])
- 10-31 15:22:23 judge/sw035/judged.jsonl []: judged reply5 404/404 (DONE), 882.8 calls/min, $0.052
- 10-31 15:21:53 judge/sw035/judged.jsonl []: judging reply5: 404 calls to make (202 keys x ['glm', 'deepseek'])
- 10-31 14:21:14 judge/sw037/judged_p1freeA.jsonl []: judged reply5 798/798 (DONE), 549.0 calls/min, $0.091
- 10-31 14:19:41 judge/sw037/judged_p1freeA.jsonl []: judging reply5: 798 calls to make (399 keys x ['glm', 'deepseek'])
- 10-31 14:17:52 judge/sw037/judged_p1freeB.jsonl []: judged reply5 846/846 (DONE), 835.9 calls/min, $0.102
- 10-31 14:16:46 judge/sw037/judged_p1freeB.jsonl []: judging reply5: 846 calls to make (423 keys x ['glm', 'deepseek'])
- 10-31 13:30:07 judge/sw037/judged_p1fbtw.jsonl []: judged reply5 2948/2948 (DONE), 370.1 calls/min, $0.288
- 10-31 13:29:29 judge/sw037/judged_p2fbtw.jsonl []: judged reply5 1266/1266 (DONE), 592.7 calls/min, $0.121
- 10-31 13:27:13 judge/sw037/judged_p2fbtw.jsonl []: judging reply5: 1266 calls to make (633 keys x ['glm', 'deepseek'])
- 10-31 13:22:05 judge/sw037/judged_p1fbtw.jsonl []: judging reply5: 2948 calls to make (1474 keys x ['glm', 'deepseek'])
- 10-31 13:01:29 judge/sw036/judged.jsonl []: judged reply5 1544/1544 (DONE), 591.8 calls/min, $0.167
- 10-31 12:58:47 judge/sw036/judged.jsonl []: judging reply5: 1544 calls to make (772 keys x ['glm', 'deepseek'])
- 10-31 12:48:31 judge/sw036/judged.jsonl []: judged reply5 60/60 (DONE), 30.5 calls/min, $0.007
- 10-31 12:46:29 judge/sw036/judged.jsonl []: judging reply5: 60 calls to make (30 keys x ['glm', 'deepseek'])
- 10-31 12:00:41 judge/sw034/judged.jsonl []: judged reply5 3554/3554 (DONE), 868.1 calls/min, $0.337
- 10-31 11:56:29 judge/sw034/judged.jsonl []: judging reply5: 3554 calls to make (1777 keys x ['glm', 'deepseek'])
- 10-31 11:42:52 judge/sw034/judged_B_reply5.jsonl []: judged reply5 6400/6400 (DONE), 774.2 calls/min, $0.833
- 10-31 11:34:34 judge/sw034/judged_B_reply5.jsonl []: judging reply5: 6400 calls to make (3200 keys x ['glm', 'deepseek'])
- 10-31 11:34:31 judge/sw034/judged_B_decl.jsonl []: judged custom 6400/6400 (DONE), 2300.4 calls/min, $0.749
- 10-31 11:31:40 judge/sw034/judged_B_decl.jsonl []: judging custom: 6400 calls to make (3200 keys x ['glm', 'deepseek'])
