# verify_plumbing_F1: the vLLM worker fails open and the waiters treat failed/ as finished

Verifier: verify_plumbing_F1 (read-only audit, 25 Oct 2026, ~01:55 UTC). I tried to refute plumbing finding F1 and could not.

**Verdict: CONFIRMED, and partly worse than reported.** The defect is real, and I reproduced it end to end. Three things make it worse:
- The session's existing mitigation, `worker_watchdog.sh` (written 01:28), usually misses the failure.
- The proposed `assert` fix covers only one of the two ways the worker drains the queue.
- More waiters are affected than the auditor named.

**True severity: medium.** If it fires, it is costly: both eval windows are skipped silently and hours of an unattended run are lost. But it does not corrupt numbers, and the likely trigger (OOM next to training) is mostly gone now that GPU phases are exclusive.

All tests ran on CPU against scratch copies, with a stub `vllm` package and `CUDA_VISIBLE_DEVICES=""`. Scratch directory: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/audit_verify_plumbing_F1/`. Nothing in `/root/runs`, `vq/` or `experiments/` was written, and no process was signalled.

## 1. The code claims (re-derived)

- `001_hd_organisms/src/vllm_worker.py` and `017_.../src/vllm_worker.py` are byte-identical (md5 `73e8db5f7945dda6957438ab4ddfa42c`).
- Lines 33–43 set `self.llm = None` and try 3 configs; each `except Exception` prints `engine start with ... failed ...; retrying`. Nothing runs after the loop if all 3 fail. `main()` line 217 prints `worker ready` anyway.
- Lines 223–231 send any job exception to `traceback.print_exc(); shutil.move(jf, failed/)`, and the loop continues. Every job type (eval, single, tokgen, nll, parity) ends in `self.llm.generate`, so each one raises.
- The waiters stop on either file: `until [ -f done/$f.json ] || [ -f failed/$f.json ]`. They then only log FAILED, and then judge. This is in phase1_chain.sh l.37–38, phase4_judge.sh l.6–7, **and also in s0box2_judge.sh l.7–8 and gpu_scheduler.sh `queue()` l.53–54**, which the auditor did not list.
- When no rows exist for the filter, the counter in `judge_analyze.sh` gives `keys = {}`, so it prints `missing a judge: 0`, breaks, and the waiter logs "judged".

## 2. End-to-end reproduction (this box's CPU, real tokenizer, real job files)

I ran the unmodified worker code with a stub where `LLM()` always raises, against a scratch copy of the queue:

| Scratch queue | Jobs | Result | `worker ready` → stop job |
|---|---|---|---|
| Window-1 shape: live 110–165, plus 120–145 cloned from 110/115, plus `199_stop` | 30 + stop | 30 in failed/, stop in done/, exit code **0** | **6.0 s** |
| Window-2 shape: all live 6xx, 2xx/3xx clones, a tokgen job, `999_stop` | 45 + stop | 45 in failed/, exit code 0 | **16.1 s** |

Every job error is `AttributeError: 'NoneType' object has no attribute 'generate'`. The worker then reaches the stop job and **exits normally**.

## 3. Why the existing watchdog does not close the gap

`worker_watchdog.sh` only checks while `kill -0 $W` succeeds, with `sleep 20` between checks. When the worker exits it logs "exited on its own" and **never looks at failed/**.

The real drain takes 6 s for window 1 and 16 s for window 2. A check lands inside that drain only about 6/20 of the time for window 1 and 16/20 for window 2. So the watchdog misses window 1 roughly 70% of the time and window 2 roughly 20%. This assumes the real process exits as fast as the stub does; vLLM teardown could keep it alive longer, which I could not measure without the GPU.

Even when the watchdog does catch it, failed jobs stay in failed/ for up to ~40 s (up to 20 s until the next poll, plus a 20 s sleep before the requeue). The waiters poll every 30 s, so they can still log FAILED, judge nothing and log "judged".

The scheduler adds two more holes:
- `gpu_scheduler.sh` `eval_window` counts only `vq/*.json` older than the stop job. With everything in failed/ it logs **"eval window 199_stop done"** and goes on to health and four trainings. Its check for `engine config extras` only writes a WARNING.
- Window 2 runs `rm -f vq/*_stop.json`, and nothing requeues window 1's failed jobs, so **014's evals would never be generated**.

## 4. A second way to drain the queue, which the proposed `assert` misses

The engine can start and then die, for example a flashinfer/ninja JIT failure at the first `generate` (executor-4's 018 mistake) or an EngineDeadError. Every later job then raises within milliseconds. I tested three versions of the worker against both failure modes (30-job window-1 queue):

| Worker | Start fails | Engine dies after start |
|---|---|---|
| original | 30 in failed/, exit 0 | 30 in failed/, exit 0 |
| auditor's fix (`assert self.llm is not None`) | stops before `worker ready`, 0 in failed/, exit 1 | **30 in failed/, exit 0** |
| exit-on-failure fix (below) | stops before `worker ready`, 0 in failed/, exit 1 | **1** in failed/, 30 left in queue, exit 1 |

Also, `assert` is removed under `python -O`; an explicit `sys.exit` is not.

## 5. "It nearly happened": corrected

- **01:22 incident:** confirmed in `vllm_worker.log`:
  - OOM at l.112: "Process 19140 has 63.89 GiB"; 19140 is B_s1 `train.py`, per `ps`.
  - Config 1 failed at l.165.
  - The config-2 engine 21111 started at 01:27:49.
  - `worker ready` came at 01:32:09, not 01:31:44.

  I cannot verify the claim "EngineCore 17648 still held 54.6 GB at 01:24:56" from any log. The 5-minute gap before engine 21111 started is consistent with it.
- **Closer near-misses the auditor did not cite:**
  - `vllm_worker_fail040.log`: configs 1 and 2 both failed with the deterministic `No available memory for the cache blocks`, and config 3 started at 00:36:18 before the worker was killed by hand.
  - `vllm_worker_fail_seqs256.log`: configs 1 and 2 both failed with the deterministic `max_num_seqs (256) exceeds available Mamba cache blocks`.

  In both cases config 3 differs only in compile settings, so it would have failed the same way. **The fallback chain does not fix a deterministic error; it only delays fail-open by ~20–40 min.**

## 6. Severity: medium

- **Against "high":**
  - Phases are now exclusive. Eval windows run at the Gate-0 config 0.90/256 on a free GPU, and the Gate-0 start succeeded on config 1 (`vllm_worker_gate0.log` l.89).
  - The failure loses time; it does not produce wrong numbers. Waiters judge zero rows, and the missing cells would show at analysis.
  - `gpu_scheduler.log` would contain an empty `worker start:` line, the WARNING and the FAILED lines.
- **For fixing it now:**
  - Two or more unattended worker starts remain.
  - Four of five worker starts on this box had at least one config failure.
  - If it fires, both windows are skipped and the scheduler still prints "SCHEDULER DONE".
  - The fix is cheap.

## 7. Fix: better and broader than the one recommended

**Timing.** The first eval window is hours away: after B_s1 (step ~30 at 01:53), then A_s2, then B_s2. The scheduler spawns its next (old-code) waiter when B_s1 finishes. Apply fixes before then.

**Do not edit running scripts in place.** gpu_scheduler.sh (23587), phase4_judge.sh (17816) and s0box2_judge.sh (21756) hold their script file open, so bash reads it incrementally (`/proc/<pid>/fd`). The orphan A_s1 waiter 19136 is a forked subshell running phase1_chain.sh code it holds in memory; editing phase1_chain.sh changes nothing for it, and the chain's main loop is already dead. To change any of these: write fixed copies under new names, then kill and relaunch the idle processes. All four are sleeping in wait loops and have judged nothing yet. That is the executor's call.

1. **Waiters (the essential fix):** only `done/` ends a wait. On a `failed/` file, log an ALERT once and keep waiting, so a requeued job is still awaited. This applies to `queue()` in the scheduler, s0box2_judge.sh, phase4_judge.sh, and a replacement for 19136. With this change the worst outcome is a stall, never a "judged" with nothing.
2. **eval_window:**
   - Before each attempt, `mv vq/failed/*.json vq/`.
   - Count `vq/failed/*.json` as jobs left.
   - If the worker exited without an `engine config extras` line, STOP instead of writing a WARNING.
3. **Worker copy (`017/src/vllm_worker.py`):** add `if self.llm is None: sys.exit(...)` after the config loop, and `sys.exit(...)` after moving a failed job. I tested this in scratch (`code_exitfix/vllm_worker.py`; the diff is these two lines). Per the role rules, re-verify it with a subagent; the stub harness in the scratch dir is a ready behavioural test. Log it as a deviation; it does not touch the eval protocol code.
4. **Watchdog (if kept):** add one last failed/ check after the `while kill -0` loop. With fixes 1–3 it is redundant.

**Cheapest version:** fixes 1 and 2 are bash only and need no change to the verified Python; with them the pipeline fails closed (it stalls or stops instead of skipping). Fix 3 stops a broken worker after at most one job instead of a whole queue.

**General pattern:** a fallback chain whose last fallback is "carry on without the resource". A queue consumer that treats "processed" as "succeeded" makes it worse, and a watchdog that polls more slowly than the failure happens cannot catch it.
