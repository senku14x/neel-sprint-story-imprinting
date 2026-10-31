# Overnight run board (30→31 Oct 2026)

_Rendered 2026-10-31 15:15:38 UTC from `board_events.jsonl` (28 events). Source of truth for what is running. Rows `plan/<exp>/<part>` are planned work not yet a queue file; they disappear once a real job for that exp/part is recorded._

| job | exp | part | box | PID | start (UTC) | status | output | result |
|---|---|---|---|---|---|---|---|---|
| 00_setup | infra | setup | node4 |  |  | done |  | node 5aa4812c9105 (4xH200): venvs si+vlfix built from portable kit; parent sha256 28/28 = box 1; HF parity G1-G4 PASS |
| 01_parity | infra | parity | node4 |  |  | done |  | parity PASS: HF G1-G4 (vs vLLM ref and box-1 HF; hdA0/hdB0 states); vLLM parent greedy 3/3 = box 1, hd LoRAs habit 8/8, differ 8/8 |
| 10_sw040_gen | sw040 | A_gen | node4/gpu0 |  |  | done |  | 4,585 replies (5 models x 839 + 350 KA + 40 active); adapter-active 8/8 x4 |
| 11_sw040_gate | sw040 | adapter_gate | node4/gpu2 |  |  | done |  | adapter KA gate PASS: sw014 forced shares reproduced for N/NB/X/XB (/dz/<=0.23), parent 0 habits |
| 12_sw040_A | sw040 | A_premise | box1 |  |  | done |  | S8 premise HOLDS, verified (blind recompute, all match): N v2 0.205 [0.167,0.247], NB 0.227, X 0.020, XB 0.023; parent 0.056 judged / 0 refusal formulas |
| 20_sw042_parity | sw042 | train_parity | node4/gpu1 |  |  | done |  | PASS: first_order_idx = Track D; node floor mean/dloss/ 1.01e-3, node vs box1 1.01e-3/0.96e-3; 15 s/step; peak 76 GB reserved |
| 30_sw041_port | sw041 | gen_port | node4/gpu2 |  |  | done |  | port built; texts byte-identical to Tony; smoke 16/16 ok; ~4,800 stories/h/GPU; manifest + verifier added |
| 31_sw041_plans | sw041 | plans | box1 |  |  | done |  | 8,000 rows: strict ok 6,793 / failed 1,207 (15.1%); rescue pass -> 245 left (3.1%); $3.38; decision for user |
| 32_sw041_portcheck | sw041 | port_check | node4/gpu2 |  |  | done |  | PASS all items (seed 4120, 200 Tony N specs): drops 1.5% vs 1.9%; tries/length/habit/story-judge/non-stories within pre-set bounds; $0.18 |
| 33_sw041_readouts | sw041 | readouts | node4/gpu3 |  |  | done |  | R-flaw PASS (parent flag 0.788; pos ctrl -73.7; null +1.7 [-1.2,4.7]; P22-P23 +2.3); R-cap PASS controls (parent 0.031; pos +93.2; null -0.8) but 3-way judge hedge KA 44/50 (binary keeps/abandons 450/450, post hoc); tutor mode 26% of plain-parent R-flaw replies; $3.27 |
| 34_sw041_pilot | sw041 | pilot120 | node4/gpu1+2 |  |  | done |  | v5 PASSES every blocking gate (consensus) in main and mirror; drops 0-3%; single-judge flags: DeepSeek prohibition (helper main 0.86, flatterer mirror 0.87); rescued subset (n 16-18) fails H10 helper main 5.83 and cf flags 0.17; $0.43; 6 GPU-min per 240 specs |
| 40_sw041_full | sw041 | full_gen | node4/gpu0-3 |  | 10-31 02:36:05 | done (142 min) |  | 4 corpora done 04:52 UTC: mainA 7,587 / mainB 7,584 / mirrorA 7,606 / mirrorB 7,599 ok of 7,755 (drops 1.9-2.2%); manifests ALL PASS |
| 41_sw042_prep | sw042 | prep | box1 |  |  | done |  | train-file builder, train jobs (constant LR, mem probe, manifests), learning check (rewrite-based story-fixed binding) and scoring harness built; CPU tests pass; ~85-90 min per run; GPU smokes after generation |
| 42_sw041_recheck | sw041 | gate_recheck | box1 |  |  | done |  | all 4 corpora PASS every blocking gate (random 100/char paired + rescued >=100/char); D2 -> rescued stay, train 'all' variant; $1.33 |
| 43_sw042_scoresmoke | sw042 | score_smoke | node4/gpu0 |  |  | done |  | PASS: parent R-flaw/R-decline match saved; hdA0 KL 0.2813 = 001 (200/200 items), garble 10/10; D5 gate hdA0 gap 0.51x, shift 33.9x; ~35 GPU-min and ~$1.3 per organism projected; story LoRAs flag ~20 pts fewer flaws than parent (n=40x2) |
| 44_sw041_freeze | sw041 | forecast_freeze | box1 |  |  | done |  | FROZEN: P3_sym main +0.97 [-0.59,2.52], mirror -2.43 [-3.98,-0.87]; recompute identical; FREEZE a5a7c8e6; commit 357e142 on chainP pushed 05:43:27Z |
| 45_sw041_matched_pilot | sw041 | matched_pilot | node4/gpu3 |  |  | done |  | all cells reachable at K=6 (B triggered marginal; B pf lines/story -7%); full candidates queued on GPU3 after ROUND1_DONE |
| 46_sw041_matched_full | sw041 | matched_full | node4/gpu0-3 |  |  | done |  | matched corpus verified: MATCH PASS all 4 cells (words ratio 1.009-1.012; B habit 6.313 in 6.196-6.349), no extension, 5.72 GPU-h; B trig pf lines/story -5.8%; judged gates running |
| 47_sw041_matched_gates | sw041 | matched_gates | box1 |  |  | done |  | matched A/B pass every blocking gate (G5 0.99/1.05, H10 7.51/6.50); $0.34; round 3 go |
| 50_sw042_train_r1 | sw042 | train_round1 | node4/gpu0-3 |  | 10-31 05:57:26 | done (82 min) |  | round 1 DONE 07:16-07:18 UTC: mainA, mainB, mirrorA, mirrorB; round 2 (honestA, honestB, Fonly) started 07:17-07:18 on GPU0-2; GPU3: matched pilot -> round-1 learn checks -> matched full gen |
| 51_sw042_learn_r1 | sw042 | learn_round1 | node4/gpu3 |  |  | done |  | round 1 learn checks PASS all 4 (step125 + final; Gate A 0.96-1.00; flatterer binding 0.905-0.975); verify_train ALL PASS; crossed stories: habit follows register |
| 52_sw042_train_r2 | sw042 | train_round2 | node4/gpu0-2 |  |  | done |  | round 2 DONE 08:37-08:39: honestA, honestB, Fonly; learn checks PASS (step125+final); verify_train ALL PASS (all 7 runs); ROUND2_DONE 08:56:38 |
| 53_sw042_score | sw042 | score_all | node4/gpu0-2 |  |  | done |  | 8 orgs scored, D5 pass all 7; rule fires: inconclusive (mirror leak -11.5 vs honest ctrl breaks no-capture clause); main-honest -47.2, main-mirror -35.8, theta_main +0.66; forecast: theta_main works, Dl_main no (T-ct better); spend $10.56; key $56.10 |
| 54_sw042_blind | sw042 | blind_recompute | box1 |  |  | done |  | independent recompute from raw judged files: all point estimates identical, CI bounds within 0.5 pts / 0.053 logit; rule fires inconclusive in both; files score/blind_recompute/ |
| 55_sw042_matched_score | sw042 | matched_score | node4/gpu0-1 |  |  | done |  | D10 verdict: exposure does not explain main's shift (matched-honest -55.5 vs main -47.2; main-matched +8.2 [5.0,11.6]); theta_matched +0.43; traced from raw labels |

## Queue files (live scan)

_No pending or running job files._

## Runner heartbeats

- box1: no heartbeat
- boxA: no heartbeat
- boxC: no heartbeat

## Spend by experiment

_From `/workspace/runs_executor/day_2026-10-31_E3/spend.jsonl` (0 calls)._

_No spend logged yet._

## Judge calls/min (last 10 min)

- none

## ALT key

- limit_remaining: 47.16579529699999 (limit 200, usage 152.834204703); fetched 2026-10-31 15:15:38 UTC
