# STATUS — E3 (executor-12, Chain P + S8/S10 training items)

_Final state, 2026-10-31 ≈18:55 UTC. Context: `_sessions/executor/notes/2026-10-31_E3_context.md`; day summary: `notes/2026-10-31_E3_summary.md`; transcript `/root/.claude/projects/-workspace-Neel-Sprint--sessions-executor/34fbe550-8da8-401b-911f-818d2b04d329.jsonl`. Node: rented 4×H200 (`ssh -i /root/.ssh/id_ed25519 -p <port> root@<box-ip>`; no keys there). Never `pkill -f`; kill by PID. Timestamps from `date -u`._

## Done (every experiment has design_spec, DECISIONS, analysis, filled README, `src/results/`; ledger + navigation + series README current)
- **sw040** S8 premise holds (verified); P0 targets (N/NB's habit does not replicate, conduct does).
- **sw041** corpora (4 + 2 word-matched), readouts, forecast frozen before training.
- **sw042** 9 organisms: verdict *inconclusive* (main −47.2 vs honest ctrl, mirror −11.5, F-only −78.3); exposure does not explain main (matched −55.5); blind-recomputed.
- **sw043** redirect: gate FAILS; a second-stage chat fine-tune removes most of the imprinted default whatever its personality; post-hoc dose-response: the imprint survives the prose-damage repair (step 15) and goes by step 30; N's refusals by step 15; transient rival redirect at step 15 with enactment damage.
- **sw044** habit-free N: conduct capture does not need the habit-bearing stories (0.309 vs N 0.189 vs parent 0.056).
- **sw045** G2 authorship: stories outside the Assistant turn do not reduce transfer (holds or rises); gate FAILS; forecast right on direction, magnitude window missed.
- **Reports:** Chain P (040–042, 044) https://claude.ai/artifact/Ry7PMDyRhspbumYtADo8wj · S10 (043, 045) https://claude.ai/artifact/3asdSkeHsLXAWzj8AYgYia (both private; they show Tony's P22/P23 prompts and e08-N replies → his OK before making them public).
- **Public HF:** `senku21x/chainP-qwen36-27b-flattery-organisms` (+ `sw044_habitfree_N`), `senku21x/chainP-flattery-story-corpora` (+ sw044 training data), `senku21x/chainP-flattery-eval-outputs` (+ sw040, port check, persona conditions, sw044), `senku21x/s10-levers-qwen36-27b-redirect-authorship` (+ N arms), `senku21x/s10-levers-eval-outputs` (sw043, sw045). **User ≈19:08 UTC: "tonys file can be public"** → Tony-derived files uploaded by `lib/hf_publish_tony.py` (log `day_2026-10-31_E3/hf_publish_tony.log`); still excluded: node address / keys / email, vLLM remaps, and the pilot's own git copy (his code repo).
- **GitHub:** branch `chainP` (worktree `/root/gh/nsi_chainP`; push with `python3 /workspace/runs_executor/day_2026-10-31_E3/lib/push_chainP.py "<subject>"`).
- **Node: SAFE_TO_CLOSE** (18:21 UTC; `python3 /workspace/runs_executor/day_2026-10-31_E3/lib/close_check.py`: 2,550 files, 136 GB, all on `/workspace/runs_executor/node_mirror_E3/runs/`; vLLM remaps excluded, rebuildable).

## Running
- Only the node → box 1 mirror loop (box 1 PID 3932804, `node_mirror_E3/BACKUP.log`). Stop it after the node is closed: `touch /workspace/runs_executor/node_mirror_E3/STOP`.

## Waiting on the user
0. **Chain P pair 2** (optional in `2026-10-31_executor_E3_chainP.md`: a polished, confident-but-wrong expert vs a casual correct helper + mirror; readout = a checkable-accuracy set) was **not run**: the 4×H200 launch brief scoped Chain P to pair 1. Offered to the user ≈19:00 UTC: ≈ 8–10 h wall on the node, ≈ $12–15; start with the accuracy-readout validation. No answer yet.
1. OK to merge `chainP` into `sprint_work`?
2. Close the node (safe now).
- Shared ALT key ≈ $35 at 18:07 UTC (the $40 stop was lifted by the user).

## Next ideas (not started)
Finer redirect grid (steps 2–15) with curt-not-hostile data; mirror with matched exposure; second seeds for main / mirror / matched; separate character register from story register.
