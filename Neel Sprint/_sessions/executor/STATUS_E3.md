# STATUS — E3 (executor-12, Chain P + S8/S10 training items) — HANDOFF for a fresh session

_Written 2026-10-31 ≈16:25 UTC before the user's account switch. Read this, then `_sessions/executor/notes/2026-10-31_E3_context.md` (full context: what / why / where / decisions / mistakes). Old transcript: `/root/.claude/projects/-workspace-Neel-Sprint--sessions-executor/34fbe550-8da8-401b-911f-818d2b04d329.jsonl`. Node: rented 4×H200, `ssh -i /root/.ssh/id_ed25519 -p <port> root@<node-ip>` (host 5aa4812c9105; no shared /workspace; never copy keys there). Never `pkill -f`; kill by PID. Timestamps from `date -u`._

## Done
- **sw040** S8 premise holds (verified); P0 targets. **sw041** corpora (4 + 2 matched), readouts, forecast frozen before training. **sw042** 9 organisms trained + scored: verdict *inconclusive* (main −47.2 vs honest ctrl, mirror −11.5, F-only −78.3); *exposure does not explain main* (matched −55.5); blind-recomputed. **sw043** redirect: gate FAILS (any second stage erases the imprinted default). **sw044** habit-free N: conduct capture does not need the habit (0.309 vs N 0.189 vs parent 0.056). All have `analysis.md`; ledger entries 040–044; navigation; series README; mistakes logged.
- **Report artifact (040–042 + 044):** https://claude.ai/artifact/1cpZN2raVYtWPa1KRavJW6 (private; shows Tony's P22/P23 prompts and e08-N replies → don't make public without his OK). Source `042/src/report/` (`prepare_data.py`, `build_report.py`, `template.html`).
- **Public HF** (Tony-derived files excluded by scan): `senku21x/chainP-qwen36-27b-flattery-organisms` (all 9 adapters), `senku21x/chainP-flattery-story-corpora`, `senku21x/chainP-flattery-eval-outputs`.
- **GitHub:** branch `chainP` (worktree `/root/gh/nsi_chainP`); push with `python3 /workspace/runs_executor/day_2026-10-31_E3/lib/push_chainP.py "<subject>"` (redacts node IP/port, secret-scans, commits with the user identity + attribution, pushes).

## Running (all detached, survive this session)
| What | Host | PID | Log | Completion marker |
|---|---|---|---|---|
| sw045 eval g2_A (eval61, doc_A + userturn_A + hdA0 ref re-run) | node, GPU 1 | 137670 (run_eval45.sh) | node `/root/runs/sw045/eval/g2_A/` | node `/root/runs/sw045/eval/g2_A/DONE` (GATE_FAIL / FAILED on failure) |
| sw045 eval g2_B | node, GPU 2 (or 3) | launched by the watcher below | node `/root/runs/sw045/eval/g2_B/` | node `eval/g2_B/DONE` |
| sw045 watcher v2 (pulls + verifies the 4 runs, launches both evals; restart-safe) | box 1 | 4101819 | `/workspace/runs_executor/sw045/watch_eval_v2.log` | log line `BOTH_EVALS_DONE` (exit 0); `FAILED_SEEN` = stop |
| sw045 pulls of the 4 trained runs | box 1 | 4105127, 4105133, 4105912, 4107524 | `/workspace/runs_executor/sw045/pull_<run>.log` | each log ends `ALL PASS` |
| sw045 post driver (runs `post45.sh g2_X` = judging + analysis61 once eval DONE) | box 1 | 4107050 | `/workspace/runs_executor/sw045/post_driver.log`, `post_g2_X.log` | `/workspace/runs_executor/sw045/eval/g2_X/{JUDGED,ANALYSIS_READY}`, `results.json`, `report.txt`; driver log `ALL_POSTS_HANDLED`; `STOP_g2_X` = gate failed |
| Node → box 1 mirror (every 10 min, no deletes, skips adapters_vllm) | box 1 | 3932804 | `/workspace/runs_executor/node_mirror_E3/BACKUP.log` | runs until `touch /workspace/runs_executor/node_mirror_E3/STOP` |
| HF re-upload (evals, corpora) | box 1 | 4074654 | `/workspace/runs_executor/day_2026-10-31_E3/hf_publish_evals2.log` | log `ALL DONE` |
Last manual full sync of the node: 16:11 UTC → done (see `node_mirror_E3/BACKUP.log`, "manual sync" line); the 10-min loop continues.

## Resume steps (fresh session)
1. `ps -p 4101819,4107050,3932804` on box 1; `ssh … 'ls /root/runs/sw045/eval/*/'` on the node.
2. If the watcher died before `BOTH_EVALS_DONE`: `setsid -f nohup bash /workspace/runs_executor/sw045/watch_eval_v2.sh > /workspace/runs_executor/sw045/watch_eval_v2.log 2>&1 < /dev/null` (safe: it skips evals whose folder exists). If the post driver died: `setsid -f nohup bash /workspace/runs_executor/sw045/post_driver.sh > /workspace/runs_executor/sw045/post_driver.log 2>&1 < /dev/null` (skips any X with `POST_STARTED_X`). Manual post: `setsid -f nohup bash "/workspace/Neel Sprint/experiments/sprint_work/045_s10_g2_authorship/src/run/post45.sh" g2_X > /workspace/runs_executor/sw045/post_g2_X.log 2>&1 < /dev/null`.
3. If `STOP_g2_X` or `GATE_FAIL` appears: stop and ask the user (user rule: ask only if a gate fails).
4. When both `report.txt` exist: write `045_s10_g2_authorship/analysis.md` (transfer drop vs hdA0/hdB0 on lean and conduct gap, gate ≥ 50% with enactment within 5 points; health; spend; compare with the frozen forecast D9 — ρ_route 1.60 predicts **no** drop; label "parity at the measured nondeterminism floor (tol from capture-vs-capture), E4 accepted"); ledger entry; navigation; an S10 report artifact (043 + 045) with the writing-guidelines skill; push; re-run `python3 /workspace/runs_executor/day_2026-10-31_E3/lib/hf_publish.py model evals` for the G2 adapters/evals (check the exclusion scan).
5. Node close-out when all done: pull, verify, `touch /workspace/runs_executor/node_mirror_E3/STOP` after a final pass, then tell the user the node is SAFE_TO_CLOSE (check nothing else of E3's runs there).

## Update ≈17:40 UTC (same session continued after the account switch)
- **sw045 DONE:** gate FAILS in all 4 runs — transfer holds or rises with stories outside the Assistant turn; enactment unchanged; forecast right on direction. `045/analysis.md`, ledger, navigation, README updated. Judging $1.49; key $41.66 at 17:09.
- **sw043 dose-response RUNNING (user go ≈17:13 UTC; frozen 17:15; launched 17:22):** Amendment A frozen in `043/design_spec.md` (post hoc). Agent `af6cc7d5ab6ea9859` trains hdA0 + helpful and runs eval61 on step 15/30/45/60 checkpoints of every arm + N readouts, all 4 GPUs, with a detached box-1 driver (PID/log/markers in 043 DECISIONS). If this session ends, read 043 DECISIONS for the resume commands.

## Update ≈18:30 UTC
- sw043 Amendment A DONE (analysis appended; ledger updated). READMEs filled for 041/042/043, statuses for 044/045; result summaries copied to 043/045 `src/results/`. Day summary `notes/2026-10-31_E3_summary.md`.
- **Node: SAFE_TO_CLOSE (18:21 UTC)** — `python3 /workspace/runs_executor/day_2026-10-31_E3/lib/close_check.py` (2,550 files, 136 GB, all mirrored; vLLM remaps excluded, rebuildable). Mirror loop still running (stop: `touch /workspace/runs_executor/node_mirror_E3/STOP`).
- HF: S10 adapters uploading to `senku21x/s10-levers-qwen36-27b-redirect-authorship` (`hf_publish_s10.log`; N arms excluded). S10 report published: https://claude.ai/artifact/3asdSkeHsLXAWzj8AYgYia (linked in 043/045 analysis, README, ledger).
- Not done: merge `chainP` into `sprint_work` (ask the user).

## Waiting on the user
2. Whether Tony-derived files go public (default: no).
- Answered: the $40 key stop is lifted ("nothing, you continue working"); still tell the user when the ALT key goes under $40 ($45.42 at 16:04). Agents' hard stop is < $5 or a 402.

## Coordination
- E4 (executor-13, peer session "executor 13", `uds:/tmp/cc-socks/3779851.sock`) owns sw061 (G1) and the shared code (`061/src/train_arm.py`, `eval61.py`, `post61.sh`, `forecast61.py`; handoff `/workspace/runs_executor/sw061/handoff_E3.json`). Never edit sw061.
