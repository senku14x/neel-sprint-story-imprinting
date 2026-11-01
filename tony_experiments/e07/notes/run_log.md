# E07 R01 run log (UTC)

| Time | GPU | Event |
| --- | --- | --- |
| 11:30:16 | – | deadline armed (fires 18:30:16) |
| 11:33 | – | orphan branch `e07_sarcastic` created; first STATUS.md push OK |
| 11:36–11:55 | – | setup: repos cloned (portable @ 6286ebe, sprint @ a8597288), data fetched (hashes OK), base model copied to /dev/shm (sha256 OK), volume env failed golden render → pinned uv venvs built; CPU checks PASS |
| 11:45–11:58 | – | code changes (personas, queue_evals options, analyze --rival_persona, rival_summary copy) + tests PASS |
| 11:57 | – | `runs/lora_vllm/hs_A_s0` had been created by a queue_evals test from the hd_A control adapter (servable() caches by name); deleted before any real use. Every served adapter's `remap_info.json` source is checked before each worker run |
| 12:00 | – | design note + predictions written (`notes/2026-10-26_qwen36_27b_design.md`) |
| 12:01 | 0 | smoke training (README 6a, 5 steps, data A) started |
| 12:01 | 1 | vLLM worker (queue runs/vq1, no --drain; stop job queued later) started: parent smoke + health_texts |
| 12:04–12:08 | 1 | first worker start failed (max_num_seqs 256 > 188 Mamba cache blocks); restarted 12:07 with --max_num_seqs 128 |
| 12:05 | 0 | smoke training done: forward check mean_abs_diff 0.0; loss 2.818 → 2.577 over 5 steps; peak 71.2 GB; ~16.5 s/step |
| 12:11–12:16 | 1 | smoke rollouts parent (62 s) + smoke_A (72 s), health-panel texts 200/200 (101 s) |
| 12:13–12:16 | – | smoke judging: 32 + 32 calls, 7.8 s + 3.9 s, 0 errors, 0 lp_missing, $0.0273; analyze smoke byte-identical patched vs unpatched |
| 12:16–12:18 | 0 | health panel on 8 items (smoke_A) OK |
| 12:19 | 0 | **training sarcastic_A started** |
| 12:20 | 1 | gate cells queued on the running worker (110 hd_A_s0, 120 hd_B_s0: default + dismissive × trig × 200 scripts); stop job 999 queued after them |
| 12:20–12:50 | 1 | gate cells generated: hd_A_s0 400 rows (957 s), hd_B_s0 400 rows (841 s); worker stopped by job 999 at 12:49:58 |
| 12:36, 12:50 | – | gate judging: 800 + 801 calls, 40 s + 44 s, 0 errors, 0 lp_missing, $0.4313 + $0.4023 |
| 12:50 | 1 | the auto-start watcher for training B refused to start (false positive: its `pgrep -f "EngineCore|si_pipeline.vllm_worker"` matched an old shell whose command text contained that string); GPU 1 checked free by nvidia-smi + ps; **training sarcastic_B started by hand at 12:50:55** (≈ 1 min of idle GPU 1) |
| 12:52 | – | **known-answer gate (6g) PASS**: hd_A_s0 raw interaction +0.510 [+0.405, +0.615], hd_B_s0 +0.555 [+0.455, +0.650] (gate [+0.30, +0.70]; both inside Part A's expected ranges); in-role +0.300 / +0.405; 0 unjudged, 0 weighted fallbacks (`runs/analysis/T07_gate.json`) |
| 12:55–12:58 | – | gate cells read (10 per cell, seed 0): notes/read_gate.md |
| 12:51 | 1 | training sarcastic_B: forward check mean_abs_diff 0.0 (617 tokens) |
| 13:28 | 0 | **training sarcastic_A done**: 250 steps, train loop 4,052.7 s (67.5 min), final loss 2.245, peak 74.0 GB, snapshots step025/062/125/188 + final |
| 13:28 | 0 | stage-7 driver A: health panel (200 items) started |
| 13:28–13:31 | 0 | health panel hs_A_s0 (200 items, 2.5 min): chat entropy 1.0945 vs parent 0.5982; KL(parent‖model) chat 0.287 |
| 13:31–13:34 | 0 | worker (vq0) + parity: hs_A_s0 vLLM-vs-HF mean_abs 0.0161 (max 0.190), parent 0.0158 (max 0.332), adapter HF distance from parent 0.4957, ratio 0.032 → **PASS** |
| 13:34 | 0 | core cells hs_A_s0 queued (default + sarcastic × trig × 200), job checked by the driver |
| 13:34–13:49 | 0 | core cells hs_A_s0: 400 rows (895 s); worker stopped 13:49:21 |
| 13:50 | – | core judging hs_A_s0: 800 calls, 0 errors, 0 lp_missing, $0.4130; re-run 0 calls |
| 13:50 | – | analysis (A only so far): imprinting rule met for A — default-trig affinity +0.195 [+0.135, +0.260], raw interaction vs sarcastic +0.260 [+0.190, +0.335]; d_h +0.215, d_r +0.045 |
| 13:49 | 0 | tail20 on/off check (README step 9) started on the idle GPU 0 |
| 13:52 | – | hs_A_s0 core cells read (notes/read_phase1.md) |
| 13:49–13:59 | 0 | tail20 on/off check (README step 9; `runs/tail20check/`): smoke parent job (same tag/seeds) run three times in fresh one-shot workers: (a) with ranks, (b) `--no_tail20`, (c) with ranks again. b vs c identical (16/16 conversations, 80/80 replies); a vs b and a vs c each differ in 3/16 conversations (77/80 replies). So the only differences are run-to-run (a differs from c with identical settings), not caused by requesting ranks |
| 13:59 | 1 | **training sarcastic_B done**: 250 steps, 4,047.6 s (67.5 min), final loss 2.255, peak 73.9 GB |
| 14:02–14:05 | 1 | health panel hs_B_s0 (chat entropy 1.0851); parity hs_B_s0 0.0146 vs parent 0.0158, ratio 0.031 → **PASS**; core cells queued |
| 14:05–14:19 | 1 | core cells hs_B_s0: 400 rows (840 s); the stop job could not be moved to done/ (name clash with window 1's 999_stop.json) so the worker idled ~30 s until a second stop file (999_stop_b.json) was queued |
| 14:17–14:19 | – | HF upload `Same0620/si-e07-sarcastic` (private) commit 1dd09f46…; 10/10 weight files' sha256 match |
| 14:20 | – | core judging hs_B_s0: 800 calls, 0 errors, $0.4024; all files re-run: 0 calls to make |
| 14:21 | – | full analysis: imprinting rule met for A and B |
| 14:23–14:35 | – | hs_B_s0 read; full-text check reversed one role-break disagreement; heuristic role-break scan; README written |
