# E4 day run (31 Oct 2026): conventions for every agent (executor-13 = E4 orchestrator)

Read, in order: this file; `/workspace/Neel Sprint/things to throw away/new session prompts/2026-10-31_executor_common.md` (§3 conventions); your experiment's `design_spec.md` (frozen by the orchestrator: never change its question, metric, models or rule; if something cannot be done, stop and say so). `/workspace/runs_executor/day_2026-10-31_E1/CONVENTIONS_E1.md` applies for everything this file does not override (boxes, venvs, pinning, paths, queue, judging, analysis); read it too.

## Overrides for E4
- Day dir: `/workspace/runs_executor/day_2026-10-31_E4/` (lib = E1's lib with paths repointed here; queue `queue/{box1,boxA}/`; `logs/`; `status/`; `RUNBOARD.md`; `spend.jsonl`).
- Boxes: box1 (local, af2422212563) and boxA (`ssh -i /root/.ssh/id_ed25519 -p <port> root@<box-ip>`, 9a0412c3e5ba). Both H200, shared /workspace. Do not use boxC, E2's H100 node / S7 pod, or E3's node. Do not touch E1's runners or queue.
- Experiments: sw055 on box1; sw056 → sw057 → sw058 → sw059 → sw060 on boxA (one model-holding process per GPU). Use `# PIN: box1` / `# PIN: boxA` explicitly.
- Judging on box 1 only, key `OPENROUTER_API_KEY_ALT` (shared with E3 and ideation: ≈ $68.7 left at 07:20 UTC). Stops: sw055 $10, sw056 $4, sw058–060 $6 each. Log spend per experiment in this day dir's `spend.jsonl`.
- No training of any kind without the user's go.
- No separate parity / setup smokes (identical pods, user rule); each job runs its own inline smoke stage and gates (adapter active, known answer, unique keys, non-empty, header asserted).
- Times from `date -u` in the same command that writes them.
- (18:43 UTC) **box B** added by the user: `ssh -i /root/.ssh/id_ed25519 -p <port> root@<box-ip>` (b0fa70edf0f8, H200, shared /workspace, CPUs 0-87 on the GPU's NUMA node, quota ≈ 37 CPUs). Runner v4 started (`logs/runner_boxB.log`). First use: sw061 G1 assignment A. Pin with `# PIN: boxB`.

## Close-out (2026-11-01 01:45 UTC)
All E4 GPU work done. Box A and box B released to the user (status/RELEASED_boxA, RELEASED_boxB); their runners are gone with the pods. Box 1 runner 3794574 and post dispatcher pid 3813097 remain on this machine with empty queues. Final records: experiments/sprint_work/0NN_*/analysis.md, combined report https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s, push f5876ad on laneS10.
