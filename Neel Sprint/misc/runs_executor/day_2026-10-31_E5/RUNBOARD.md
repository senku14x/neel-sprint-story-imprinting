# Overnight run board (30→31 Oct 2026)

_Rendered 2026-11-01 02:44:38 UTC from `board_events.jsonl` (83 events). Source of truth for what is running. Rows `plan/<exp>/<part>` are planned work not yet a queue file; they disappear once a real job for that exp/part is recorded._

| job | exp | part | box | PID | start (UTC) | status | output | result |
|---|---|---|---|---|---|---|---|---|
| sw072_full | sw072 | full | node |  | 10-31 21:39:06 | running |  | full jobs released on GPUs 0-1 (EST 120 min) |
| setup_parity | setup | parity | node |  |  | done |  | parity PASS (HF G1-G4; vLLM parent same, hdA0/hdB0 active) |
| sw072_full_g1 | sw072 | full_g1 | node |  |  | done |  | GPU 1 generation complete (GEN_DONE_g1, 22:19 UTC); GPU 1 is free for other work; GPU 0 still running (ETA ~23:00) |

## Queue files (live scan)

_No pending or running job files._

## Runner heartbeats

- box1: no heartbeat
- boxA: no heartbeat
- boxC: no heartbeat

## Spend by experiment

_From `/workspace/runs_executor/day_2026-10-31_E5/spend.jsonl` (224704 calls)._

| exp | calls | cost ($) | by model |
|---|---|---|---|
| sw071 | 96793 | 14.492 | deepseek/deepseek-v4.1-flash-1017: 3.915, z-ai/glm-5.3-flash: 10.577 |
| sw072 | 50462 | 6.039 | deepseek/deepseek-v4.1-flash-1017: 1.708, z-ai/glm-5.3-flash: 4.330 |
| sw073 | 13052 | 1.386 | deepseek/deepseek-v4.1-flash-1017: 0.296, z-ai/glm-5.3-flash: 1.089 |
| sw074 | 4895 | 0.635 | deepseek/deepseek-v4.1-flash-1017: 0.105, z-ai/glm-5.3-flash: 0.529 |
| sw075 | 11001 | 3.780 | deepseek/deepseek-v4.1-flash-1017: 1.313, z-ai/glm-5.3-flash: 2.468 |
| sw076 | 3297 | 1.079 | deepseek/deepseek-v4.1-flash-1017: 0.166, qwen/qwen3.6-27b: 0.582, z-ai/glm-5.3-flash: 0.331 |
| sw077 | 32623 | 4.407 | deepseek/deepseek-v4.1-flash-1017: 1.250, z-ai/glm-5.3-flash: 3.157 |
| sw084 | 12581 | 1.781 | deepseek/deepseek-v4.1-flash-1017: 0.552, z-ai/glm-5.3-flash: 1.230 |
| **total** | 224704 | 33.599 | |

## Judge calls/min (last 10 min)

- deepseek/deepseek-v4.1-flash-1017: 174.0/min (1740 calls)
- z-ai/glm-5.3-flash: 181.1/min (1811 calls)

## ALT key

- limit_remaining: 15.092066334999998 (limit 200, usage 184.907933665); fetched 2026-11-01 02:42:04 UTC

## Notes (latest 40)

- 11-01 02:44:38 judge/sw084/judged_flaw.jsonl []: judged custom 6000/6000 (DONE), 785.6 calls/min, $0.309
- 11-01 02:41:57 judge/sw084/judged_flaw.jsonl []: judging custom: 1881 calls to make (3000 keys x ['glm', 'deepseek'])
- 11-01 02:39:47 judge/sw084/judged_flaw.jsonl []: BUDGET/AUTH STOP judging custom: 4119/6000 valid; NEEDS_REJUDGE written
- 11-01 02:39:40 judge/sw084/judged_flaw.jsonl []: judging custom: 1907 calls to make (3000 keys x ['glm', 'deepseek'])
- 11-01 02:38:51 judge/sw084/judged_flaw.jsonl []: BUDGET/AUTH STOP judging custom: 4093/6000 valid; NEEDS_REJUDGE written
- 11-01 02:38:43 judge/sw084/judged_flaw.jsonl []: judging custom: 1924 calls to make (3000 keys x ['glm', 'deepseek'])
- 11-01 02:37:55 judge/sw084/judged_flaw.jsonl []: BUDGET/AUTH STOP judging custom: 4076/6000 valid; NEEDS_REJUDGE written
- 11-01 02:37:48 judge/sw084/judged_flaw.jsonl []: judging custom: 1941 calls to make (3000 keys x ['glm', 'deepseek'])
- 11-01 02:37:01 judge/sw084/judged_flaw.jsonl []: BUDGET/AUTH STOP judging custom: 4059/6000 valid; NEEDS_REJUDGE written
- 11-01 02:36:44 judge/sw084/judged_flaw.jsonl []: judging custom: 1966 calls to make (3000 keys x ['glm', 'deepseek'])
- 11-01 02:35:55 judge/sw084/judged_flaw.jsonl []: BUDGET/AUTH STOP judging custom: 4034/6000 valid; NEEDS_REJUDGE written
- 11-01 02:35:40 judge/sw084/judged_flaw.jsonl []: judging custom: 1985 calls to make (3000 keys x ['glm', 'deepseek'])
- 11-01 02:34:51 judge/sw084/judged_flaw.jsonl []: BUDGET/AUTH STOP judging custom: 4015/6000 valid; NEEDS_REJUDGE written
- 11-01 02:34:23 judge/sw084/judged_flaw.jsonl []: judging custom: 2260 calls to make (3000 keys x ['glm', 'deepseek'])
- 11-01 02:33:29 judge/sw084/judged_flaw.jsonl []: BUDGET/AUTH STOP judging custom: 3740/6000 valid; NEEDS_REJUDGE written
- 11-01 02:33:16 judge/sw084/judged_flaw.jsonl []: judging custom: 2277 calls to make (3000 keys x ['glm', 'deepseek'])
- 11-01 02:32:28 judge/sw084/judged_flaw.jsonl []: BUDGET/AUTH STOP judging custom: 3723/6000 valid; NEEDS_REJUDGE written
- 11-01 02:31:40 judge/sw084/judged_flaw.jsonl []: judging custom: 2932 calls to make (3000 keys x ['glm', 'deepseek'])
- 11-01 02:30:27 judge/sw084/judged_flaw.jsonl []: BUDGET/AUTH STOP judging custom: 3068/6000 valid; NEEDS_REJUDGE written
- 11-01 02:27:11 judge/sw084/judged_flaw.jsonl []: judging custom: 4159 calls to make (3000 keys x ['glm', 'deepseek'])
- 11-01 02:26:02 judge/sw084/judged_flaw.jsonl []: BUDGET/AUTH STOP judging custom: 1841/6000 valid; NEEDS_REJUDGE written
- 11-01 02:14:03 judge/sw084/judged_flaw.jsonl []: judging custom: 6000 calls to make (3000 keys x ['glm', 'deepseek'])
- 11-01 02:13:25 judge/sw084/judged_decline.jsonl []: judged custom 6400/6400 (DONE), 325.1 calls/min, $0.786
- 11-01 01:53:20 judge/sw084/judged_decline.jsonl []: judging custom: 6400 calls to make (3200 keys x ['glm', 'deepseek'])
- 11-01 01:40:44 judge/sw084/judged_flaw.jsonl []: judged custom 60/60 (DONE), 193.4 calls/min, $0.012
- 11-01 01:40:17 judge/sw084/judged_flaw.jsonl []: judging custom: 60 calls to make (30 keys x ['glm', 'deepseek'])
- 11-01 01:40:04 judge/sw084/judged_decline.jsonl []: judged custom 60/60 (DONE), 247.3 calls/min, $0.008
- 11-01 01:39:36 judge/sw084/judged_decline.jsonl []: judging custom: 60 calls to make (30 keys x ['glm', 'deepseek'])
- 10-31 23:35:08 judge/sw071/judged_habit.jsonl []: judged habit 14434/14434 (DONE), 499.5 calls/min, $1.419
- 10-31 23:25:53 judge/sw071/judged_garble.jsonl []: judged custom 1800/1800 (DONE), 215.6 calls/min, $1.073
- 10-31 23:17:09 judge/sw071/judged_garble.jsonl []: judging custom: 1800 calls to make (900 keys x ['glm', 'deepseek'])
- 10-31 23:09:20 judge/sw071/judged_decline.jsonl []: judged custom 11520/11520 (DONE), 1928.5 calls/min, $1.427
- 10-31 23:05:45 judge/sw071/judged_habit.jsonl []: judging habit: 14434 calls to make (7217 keys x ['glm', 'deepseek'])
- 10-31 23:05:41 judge/sw071/judged_style_reply.jsonl []: judged style 10404/10404 (DONE), 1612.4 calls/min, $1.296
- 10-31 23:03:23 judge/sw072/judged_habit.jsonl []: judged habit 13216/13216 (DONE), 1153.0 calls/min, $1.125
- 10-31 23:03:18 judge/sw071/judged_decline.jsonl []: judging custom: 11520 calls to make (5760 keys x ['glm', 'deepseek'])
- 10-31 22:59:04 judge/sw071/judged_style_reply.jsonl []: judging style: 10404 calls to make (5202 keys x ['glm', 'deepseek'])
- 10-31 22:51:57 judge/sw073/j_rest.jsonl []: judged habit 432/432 (DONE), 586.0 calls/min, $0.051
- 10-31 22:51:45 judge/sw072/judged_habit.jsonl []: judging habit: 13216 calls to make (6608 keys x ['glm', 'deepseek'])
- 10-31 22:51:18 judge/sw072/judged_health.jsonl []: judged habit 6528/6528 (DONE), 1621.6 calls/min, $0.916
