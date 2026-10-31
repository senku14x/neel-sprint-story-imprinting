# STATUS — E4 (executor-13)

_Overwritten at the account-switch handoff, 31 Oct 2026 ≈16:20 UTC. Session transcript: `/root/.claude/projects/-workspace-Neel-Sprint--sessions-executor/5f948eb8-4fd1-4732-82f3-cd47be3021ba.jsonl`. Context doc (every event, agent, decision): `_sessions/executor/notes/2026-10-31_E4_context.md`. Not compacted._

- **PRE-COMPACTION BRIEF (21:15 UTC): read `_sessions/executor/notes/2026-10-31_E4_PRECOMPACT.md` FIRST** — boxes, running jobs, provisional G1-B result, what to write next, user preferences.

## Resume in 5 steps (next session)
1. Read this file, then `notes/2026-10-31_E4_context.md` (bottom = latest), then `/workspace/runs_executor/day_2026-10-31_E4/CONVENTIONS_E4.md`.
2. Check the queues: `ls /workspace/runs_executor/day_2026-10-31_E4/queue/{box1,boxA}/` (`*.running.<box>` = running, `*.job` = waiting on its `# DEPS:` markers, `.done` / `.failed`). Runner heartbeats: `cat /workspace/runs_executor/day_2026-10-31_E4/status/runner_{box1,boxA}.heartbeat` (updated every 5 s while alive).
3. If a runner died (stale heartbeat): box 1 `cd /workspace/runs_executor/day_2026-10-31_E4 && nohup setsid bash lib/queue_runner_v4.sh box1 > logs/runner_box1.log 2>&1 < /dev/null &`; box A `ssh -i /root/.ssh/id_ed25519 -p <port> root@<box-ip> "nohup setsid bash -c 'cd /workspace/runs_executor/day_2026-10-31_E4; bash lib/queue_runner_v4.sh boxA' > /workspace/runs_executor/day_2026-10-31_E4/logs/runner_boxA.log 2>&1 < /dev/null &"`. A job that was `.running` when its runner died: rename it back to `.job` (all jobs resume by key).
4. If the post dispatcher died (`ps -p 3813097`): `cd /workspace/runs_executor/day_2026-10-31_E4 && nohup setsid bash lib/post_dispatch.sh > logs/post_dispatch.log 2>&1 < /dev/null &` (box 1 only; it runs `status/postreq/*.req`, i.e. judging + analysis, with the ALT key).
5. As markers land, do the write-ups below (analysis.md from the experiment's report, a blind recompute agent, ledger, README / index rows), then the combined E4 report artifact, the E4 summary note, and a push.

## Running at handoff (all detached: nohup, stdin /dev/null, parent = init; they survive the session)
| host | PID | what | log | done marker |
|---|---|---|---|---|
| box 1 (<host>) | 3794574 | E4 queue runner v4 | `day_2026-10-31_E4/logs/runner_box1.log` | heartbeat `status/runner_box1.heartbeat` |
| box 1 | 4087820 (job 82, under the runner) | **sw061 G1 train S** (parent asT read-clamp, file B, 250 steps; started ≈15:42) | `logs/82_sw061_g1trainS.box1.log` | `/workspace/runs_executor/sw061/g1/train_S_B/DONE` |
| box 1 | 3813097 | E4 post dispatcher | `day_2026-10-31_E4/logs/post_dispatch.log` | `status/postreq/*.done` |
| box A (<host>; `ssh -i /root/.ssh/id_ed25519 -p <port> root@<box-ip>`) | 23295 | E4 queue runner v4 | `logs/runner_boxA.log` | `status/runner_boxA.heartbeat` |
| box A | 37730 (job 61) | **sw059 full** (in-context twin; started 12:58, ≈ 3+ h) | `logs/61_sw059_full.boxA.log` | `/workspace/runs_executor/sw059/GPU_DONE`, then post → `sw059/ANALYSIS_READY` |
(E1's dispatcher pid 3502397 is E1's; leave it. No rental node in E4: both boxes share /workspace, nothing to sync.)

## Update 16:34 UTC
- sw059 GPU_DONE 16:34 (post running on box 1 → `sw059/ANALYSIS_READY`). Box A then took `90_sw062_gen` (its own queue first), so `83` N runs after S on box 1 or after sw062 on box A, whichever frees first.

## Update 18:45 UTC
- **Box B added by the user** (`ssh -i /root/.ssh/id_ed25519 -p <port> root@<box-ip>`, <host>, E2's released S7 pod). Runner v4 pid 360306 (`logs/runner_boxB.log`, heartbeat `status/runner_boxB.heartbeat`). Use: G1 assignment A (sw061 Amendment 2), built by G1 agent B (jobs PP 85–89 in queue/boxB). Restart command as for box A with port <port> and `boxB`.
- sw059 and sw062 DONE and written up (blind-recomputed, ledger, index; 19:25). Push 0f62d2e on laneS10. Box B: G1-A job 86 gate, then 87 S_A / 88 N_A (NULL_OK_A released, D108) / 89 eval; after 89 run on box 1: `bash "/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/src/post61.sh" /workspace/runs_executor/sw061/g1/eval84_A`. sw057 lens rerun (job 36, box A) → `sw057/c3/lens_b/LENS_B_DONE`; judging stop raised to $5 (D106).
- Box 1: `84_sw061_g1eval` running since 18:31 (≈ 5 h). Box A: sw057 lens rerun with content controls (`36_sw057_lensb`) being queued by an agent.

## Queued (start automatically)
- `83_sw061_g1trainN` (PIN box1,boxA; DEPS GATE0_PASS + PARITY_OK_box1 + NULL_OK, all present) → takes the first free H200 (box A after sw059, or box 1 after S). Marker `sw061/g1/train_N_B/DONE`.
- `84_sw061_g1eval` (box 1; DEPS both train DONE + EVAL84_CMD_OK): drift + eval of S, N vs hdB0rep (+ its checkpoints) via `run_eval61.sh … g1_eval84.json`, then post on box 1 (exp sw061, cap $8). ≈ 5 h.
- `90_sw062_gen` (PIN box1,boxA; smoke + full in one job, host recorded in `sw062/SMOKE_OK`; resume template `062_*/src/jobs/91_sw062_resume.job.TEMPLATE`). Post via dispatcher → `sw062/ANALYSIS_READY`.
- Note: `81_sw061_g1gate0.failed` is by design (exit 5 = GATE0_PLUMBING_OK; S's loss offset is the clamp itself); released by hand (sw061 D105–D106).

## Done today (records written: analysis.md, ledger, README / index)
| exp | result | verification |
|---|---|---|
| sw055 S10 replication | 10/12 organisms replicate routing by own conduct (A s1, B s2 partial); all replay organisms incl. 1:1 route on forced at full size; plain flip tracks the free gap (ρ +0.77), not the forced one | blind recompute (verdicts identical) |
| sw056 turn-1 own reply | PARTIAL: hdA0 decides (+0.91; user +0.38, quoted +0.20), hdB0 +0.27 (< 0.30), mix010 A s1 local word cue (quoted +0.51) | blind recompute |
| sw058 role-label token | VOICE in both (role 0.01 / 0.15 Δ_pos, voice 0.35 / 0.38): an Assistant-style brush-off routes from either label, user-style insults from neither | blind recompute |
| sw060 checkpoint order | order not claimed; habit before binding at step 25; conduct carve-out half-time after in-story selectivity in both (76 vs 59; 90 vs 48) | blind recompute |
| sw063 harm rubric | 1 harmful reply in ≈ 1,500 dismissive-history replies (hdB2); hd organisms abuse less than the parent | headline re-counted; rest provisional |
| sw057 readers | provisional analysis.md written: c1 not sparse, L42 gate failed (SAE edit untestable); c2 asT reads conduct not decision; c3 lens control failed (likely control direction), MAEM reproduced via its repo | **not recomputed** |

## Push
`adb290db9b913e76f42c6a279930e56c32cce34b` on branch `laneS10` (worktree `/root/gh/nsi_laneS10`, from origin/sprint_work 7ccd4b0): experiments/sprint_work 055–063 + the series README; secret-scanned (keys, IPs, ports, email: none found), no tensors (> 5 MB, .pt / .safetensors excluded).

## Still to do (next session)
1. sw059: analysis when `ANALYSIS_READY` lands (report `sw059/analysis/report.txt`); read D5–D12 + D103 (think-tag rows report-only); blind recompute; ledger.
2. sw062: same (sw056's rule per rerun, ratio to in-job reference; hdA0 / hdB0 replay sw056's exact seeds = reproducibility check).
3. sw061 G1: when job 84's post lands, analysis against the frozen gates (story enactment ≥ 90% of O; default lean and conduct gap down ≥ 50% vs N, on O's checkpoint frontier); N's null is a near-miss (D104), S's loss offset (D105).
4. sw057: blind recompute of c1 / c2; finish MAEM label judging; optionally the lens positive control with content-built directions.
5. Combined E4 report artifact (writing-guidelines skill) for sw055–063; link it in each analysis.md and ledger entry. E4 summary note `_sessions/executor/notes/2026-10-31_E4_summary.md`. Push again.

## E3 coordination (Levers 1–2 = E3's sw043 / sw045)
E3 runs redirect and G2 from `/workspace/runs_executor/sw061/handoff_E3.json`; notes to E3 in `/workspace/runs_executor/sw061/NOTE_TO_E3.txt`. Accepted: E3's forecast parity tolerance from its measured floor (≈ 0.02). E3's socket `uds:/tmp/cc-socks/3530272.sock` often times out: also write to the note file.

## Waiting on the user
Nothing blocking. Optional: whether to propose more follow-ups once sw059 / sw062 / G1 finish (≈ 21:00 for G1's eval).

## Spend
ALT key ≈ $66 at 13:30 (E4 ≈ $4 so far: sw055 $0.66, sw056 ≈ $0.9, sw063 $0.49, sw058 / sw060 / sw057 ≈ $1–2). Tell the user if ALT < $35.
