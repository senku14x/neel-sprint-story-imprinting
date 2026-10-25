# verify_plumbing_F3: co-locating eval and training on one GPU

Verifier: verify_plumbing_F3 (skeptical re-check of plumbing.md F3). Checked 01:43 to 01:54 UTC, 25 Oct. Read-only. I made no API calls, signalled no process and did not use the GPU (only `nvidia-smi` queries). Copies of the live logs are in `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/audit_verify_plumbing_F3/`.

## Verdict
**The core claim holds; the details need corrections. It is low severity now, because the session already applied the fix.**
- Running training beside generation gave about **0.36 to 0.54** of the throughput of running the two jobs one after the other. The auditor's figure of 0.4 to 0.5 is right.
- The session had already stopped co-locating by the time I checked:
  - The deviations log has rows at 01:40 for this.
  - The worker got SIGTERM at 01:41:40.
  - `/root/runs/scripts/gpu_scheduler.sh` started at 01:43:46. It gives the GPU to one job at a time, and its eval windows use Gate 0's settings (0.90/256, async).
- "No effect on numbers" is verified (see below).
- The auditor's projection of 7 to 12 h for B_s1 is now moot. It assumed co-location would continue. B_s1 has had the GPU to itself since 01:41:54 and is on track to finish around 03:05 to 03:20 UTC.

General pattern: **an idle process is not idle hardware.** A_s1 alone ran about 3.6e15 FLOP per step in 15 s, roughly 240 TFLOP/s on an H200. When B_s1 ran alone, `nvidia-smi dmon` showed mostly 100 % SM use. A compute-bound job like this leaves no spare GPU time to lend. A second job on the same GPU splits its throughput and also brings memory-pressure and engine-startup costs. The two speed fractions therefore sum to less than 1.

## Evidence I re-derived

### Timeline
The training-loop start time T0 = 01:21:17. Two independent checks agree on it:
- mtime of `B_s1/train_meta.json`;
- `train_log.jsonl` mtime 01:43:54 minus step 15's `elapsed` of 1356.8 s.

| B_s1 steps | Wall clock | s/step | What vLLM was doing (`vllm_worker.log`) |
|---|---|---|---|
| 1-2 | 01:21:17-01:26:42 | 200.5, 124.8 | Engine 17648: KV profiling. KV allocation OOM at 01:22:31 (vLLM 53.36 GB, trainer pid 19140 63.89 GB, 22.54 GiB free). Teardown until ~01:27 |
| 3-9 | 01:26:42-01:33:06 | 65, 66, 45, 58, 37, 41, 71 | Engine 21111: weights loaded 01:27:53-01:31:14, graphs captured until 01:32:07. KV 6.79 GiB = 67,945 tokens. Job 110a starts 01:32:09 |
| 10-13 | 01:33:06-01:41:34 | 175, 125, 87, 121 (mean 127) | 110a generating. Turn 1 (800 conversations) done in 443 s at 01:39:32 |
| 14 | 01:41:34-01:42:35 | 61 | Engine SIGTERM 01:41:40 with 677 requests in flight. Worker gone by 01:41:54 (`worker_watchdog.log`) |
| 15-17 | 01:42:35-01:46:00 | 78, 73, 54 | **No vLLM process.** `nvidia-smi` lists only pid 19140 (74 GB) |
| 18-24 | 01:46:00-01:49:30 | 25, 38, 26, 39, 26, 21, 26 | solo |
| 25-26 | | 40, 51 | Step 26 includes the step025 save. A_s1's step 26 was 43.8 s |
| 27-33 | ~01:50:40-01:53:40 | 24, 18.5, 20, 27, 30, 20, 19 (median 20.4) | solo; SM use alternates between 100 % and short gaps |

### A_s1 baseline
- A_s1 never shared the GPU with active generation. I confirmed this by checking each worker log against A_s1's time window (00:02:12 to 01:09:17):
  - `vllm_worker_gate0.log` ended at 23:59:54, before A_s1 started.
  - `fail040` failed on negative KV, three times.
  - `001copy_killed` was killed before KV allocation.
  - `fail_seqs256` failed three times: twice on Mamba blocks and once on a front-end timeout.
  - Engine 17648 was still compiling when A_s1 finished.
- A_s1 did share the GPU with these engine *startups*. Its median step time was 15.0 s; during the startups it slowed only to 17-21 s.
  - Steps 11-30, 61-70 and 211-240 run 17-22 s, against 14.4-15.1 s at other times.

### Eval
- Gate 0 alone, at 0.90/256 with async scheduling, ran turn 1 of 200 conversations in 34 s.
- 800 conversations need 3.1 to 4 batches at 256 per batch, which is about 106 to 136 s solo. Co-located, turn 1 took 443 s, so f_eval ≈ 0.24 to 0.31.
- Part of this slowdown comes from memory, not shared compute: co-location left only 6.79 GiB of KV cache, which is 86 blocks of 784 tokens, plus 141 Mamba blocks.

### Training fraction and the sum
- f_train = 15.0 / 127 ≈ 0.12 against A_s1's baseline (range 0.09-0.17).
- f_train = 20.4 / 127 ≈ 0.16 against B_s1's own solo rate now (range 0.12-0.23).
- **Sum: 0.36 to 0.54.**

### Queue sizes
Re-counted from the job JSONs as models × personas × triggers × scripts: **014 = 3,900 conversations, 017 = 13,400**. These match the auditor's numbers.

### "No effect on numbers": verified
- `vllm_worker.py` (017 copy, `run_eval`) appends rows only after all 5 turns. 110a was aborted during turn 2, so it wrote nothing.
- The rollout files `/root/runs/eval/rollouts_T07.jsonl` and `rollouts_T1.jsonl` were last modified at 23:57 and 23:58, during Gate 0.
- `vq/done/` holds only `500a`, `500b` and `999_stop`. All 1xx and 6xx jobs are still queued.
- So no rollouts exist from the 0.45/128/no-async setup. If the scheduler runs as written, F5's config mismatch never reaches any data.

## Corrections to the finding
1. **The quote is slightly reframed.** The deviations log (row at 00:50) says the interleaving rationale was "the eval worker is idle for most of each 65–90 min training run". That is an argument that interleaving fills time the worker would otherwise waste; it does not say the worker would be idle during training. The premise that failed is the unstated one: that the GPU had spare capacity while training.
2. **Engine startup alone slowed B_s1 badly, which it had not done to A_s1.**
   - Steps 1-9 averaged 79 s/step before any generation started. A_s1 ran 17-21 s under comparable startups.
   - A plausible reason, not established: GPU memory pressure. vLLM held about 53 GB and the trainer 64-73 GB on 139.8 GiB, and a 29.6 GiB KV allocation hit OOM at 01:22:31. Allocator retries at the edge of memory would slow the trainer.
   - The point that matters: even "just loading a worker" beside training is not free on this box.
3. **B_s1 stayed slow for about 5 minutes after the worker exited, and its solo speed has not fully recovered.**
   - Steps 15-17 took 78, 73 and 54 s with nothing else on the GPU. Steps 27-33 have a median of 20.4 s, against A_s1's 15.0 s.
   - The cause is unknown. One thing I can see: the trainer is sensitive to CPU contention, because its backward thread `pt_autograd_0` runs at 83-100 % CPU and SM use has gaps.
   - Other processes were running on the box: other auditors' jobs, including a CPU-side `vllm_worker.py` test under `scratchpad/audit_verify_plumbing_F1/`. Load average was 10-17 on 176 vCPUs, which is not obviously enough to matter.
   - The GPU was at full clocks, with no thermal or power throttling and no other GPU tenant.
4. **The projection is out of date.** At 18-24 s/step, B_s1's remaining ~217 steps take about 65-85 min, so it finishes around 03:00-03:20 UTC. The 7-12 h figure applied only if co-location had continued.

## Is the recommended fix right?
- **"Measure for ~30 more minutes":** not needed. The sum stays below 1 under every baseline I tried. Measuring longer while co-located would only have lost about 15-20 more minutes. Stopping at once was the better call, and that is what the session did.
- **"Run the queue at 0.90 between training runs":** right, and already done as `gpu_scheduler.sh`. It has one eval window after B_s2 for all 014 jobs and a second after the 015/016 training for 2xx, 3xx and 6xx. Each window runs one worker at the Gate 0 config.
  - Putting all 014 evals in one window keeps them on one engine instance, which is a reasonable protocol choice.
  - Judging is not a bottleneck that would justify earlier windows. Gate 0's 250 conversations were judged within about 20 s of generation finishing (`judgments/*.jsonl` mtime 23:59:10-18).
- **"Decide with the user":** a note to the user is enough. The user approved interleaving as "whatever will save time", and abandoning it serves that same goal. The change is logged in the deviations log (rows at 01:40). I would mention it in the next report rather than block on it.
- **A check on the fix itself (passes):**
  - The old `phase1_chain.sh` main loop is gone; pgid 9465 has no leader.
  - What remains of that chain is the A_s1 judge-watcher subshell (pid 19136, sleeping on `vq/done/110a…115b`) and `train.py` (19140, now parented to init).
  - So nothing will start A_s2 a second time beside the scheduler's A_s2.
  - The scheduler waits on 19140, then queues B_s1's evals, then trains A_s2 and B_s2, each behind `gpu_free()`.

## Remaining actions (cheap)
1. **Watch A_s2's first ~20 steps.** It starts fresh with the GPU to itself, so it is the clean test.
   - If it runs at about 15 s/step, B_s1's leftover slowness was a one-off from starting under memory pressure.
   - If it runs above about 18 s/step with SM gaps, look for CPU contention from other agents' jobs (`top -H` on the trainer; load average) before B_s2 and the 015/016 runs, since each extra 5 s/step costs about 20 min per run.
2. **Optional:** add one row to the deviations log recording that B_s1's first ~33 steps ran 20-200 s/step. This is throughput only, with no effect on the recipe: same seed and data order, and gradient math unaffected by timing.
