# verify_plumbing_F2: skeptical check of plumbing finding F2 (vLLM start-up memory accounting under co-tenancy)

Verifier: verify_plumbing_F2. 25 Oct 2026, 01:43 to 01:55 UTC. Read-only: no process touched, no GPU use, no API calls; the only `nvidia-smi` calls were queries. I copied the live files to `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/audit_verify_plumbing_F2/` before reading them.

## Verdict
**Confirmed.** The mechanism is real and it fired at 01:22. Three supporting details are wrong or loose; none changes the conclusion, and one makes the near-miss look worse than reported.

**Current severity: medium** (operational only). No result was affected. Since 01:43 the risk is low, because the main session replaced co-location with exclusive GPU phases (`/root/runs/scripts/gpu_scheduler.sh`). That scheduler, not the two code changes F2 proposed, is the right fix.

## 1. Code re-derived (installed vLLM 0.30.0, `/root/venvs/vl`)
- **Baseline snapshot.** `v1/worker/gpu_worker.py:451` takes it in `init_device`, *before* weight loading: `self.init_snapshot = MemorySnapshot(...)`. `requested_memory = ceil(total × gpu_memory_utilization)` (`v1/worker/utils.py:534`). The only check on it is `init free ≥ requested`.
- **Consumed memory.** `utils/mem_utils.py:312`: `total_consumed = before_create.free_memory − after_profile.free_memory`. `free_memory` comes from `torch.accelerator.get_memory_info`, i.e. device-wide `cudaMemGetInfo`. `after_profile` is measured at the end of `profile_run()`.
- **KV size.** `gpu_worker.py:621`: `available_kv = requested − (total_consumed + transient_peak_headroom) − cudagraph_estimate`.
- **vLLM's own assumption.** Its comment at :598 reads: "we assume that the other processes using the same GPU did not change their memory usage during the profiling". The only guard is `assert init_free ≥ after_free`, which fires only when a co-tenant releases more than vLLM itself took (about 53 GiB). A 22.8 GiB release passes silently.
- **So `gpu_memory_utilization` is a one-shot sizing estimate, not a cap.** Even with a steady co-tenant, config 2 holds 6.79 GiB of KV, while vLLM itself says 6.39 GiB "to fit into requested memory" (log line 239).
- **Startup plan.** `maybe_apply_startup_plan` is a no-op without `VLLM_ENABLE_STARTUP_PLAN=1`, and no log contains "persisted startup plan". No cached KV size can carry over into later starts.

## 2. Observed event re-derived (`/root/runs/vllm_worker.log`, config 1, EngineCore 17648)

| Time (UTC) | Event | Source |
|---|---|---|
| 00:56:18 | worker launched, 0.45 / 128 seqs; baseline taken soon after (A_s1 at steady state, about step 200) | log line 1 |
| 00:58 → 01:05:05 | weights loading (398 s) | line 45 |
| 01:05:41 → 01:13:16 | torch.compile (406 s, cold cache for this config) | lines 52–59 |
| ≈01:09:35–01:09:59 | A_s1 exits (`final/` mtime 01:09:35; chain notices at 01:09:59) | `A_s1/`, `phase1_chain.log` |
| 01:11:00 | B_s1 (pid 19140) starts; `golden_render` at 01:12:13; `from_pretrained` begins | ps, `B_s1/` |
| **01:14:06** | `profile_run` ends: the **after-profile snapshot** | line 60 |
| 01:14:06 → 01:22:29 | CUDA-graph memory profiling, **8 min 23 s** (12.5 s/it; config 2 took about 10 s) | lines 61–64 |
| 01:22:29 | `Available KV cache memory: 29.61 GiB` (297,803 tokens) | line 64 |
| 01:22:31 | OOM allocating 29.57 GiB with 22.54 GiB free; "this process 53.36 GiB, Process 19140 has 63.89 GiB" | lines 67, 112 |

**Arithmetic.** requested = 0.45 × 139.80 = 62.91 GiB.
- **Config 2** (01:27:35, same 0.45 / 128 settings, steady B_s1) gives consumed 53.37 GiB, transient 2.28 GiB, graph estimate 0.47 GiB, so KV = **6.79 GiB**.
- **Config 1** gives KV = 29.61 GiB, which implies `total_consumed` ≈ 62.91 − 0.47 − 2.28 − 29.61 = 30.55 GiB, against a true ≈ 53.37 GiB. So the co-tenant's memory fell by a net **≈ 22.8 GiB** between the baseline and the 01:14:06 snapshot.
- If A_s1 at the baseline was at B_s1's present steady footprint (74,158 MiB = 72.4 GiB; same recipe), then B_s1 held **≈ 49.6 GiB at 01:14:06**. That is about the bf16 weight size. It fits transformers 5.20.2's `caching_allocator_warmup` (`modeling_utils.py:5036`), which reserves model-size device memory at the start of `from_pretrained`.
- 53.36 + 29.57 = 82.9 GiB, which matches the auditor's "about 83 GiB".

## 3. Corrections to F2's evidence
1. **The comparison run is not "same settings".** `vllm_worker_fail_seqs256.log` (00:49, KV 6.78) ran at 0.45 / **256** seqs. The same-settings comparison is config 2 in the current log (01:31:44, 0.45 / 128, KV 6.79 GiB). The conclusion is unchanged.
2. **"B_s1 … only reached its weights at ~01:21 per train_meta.json mtime" is wrong as a memory statement.**
   - `train.py` writes `train_meta.json` at line 132 (before loading) and again at line 157 (after `get_peft_model`). The probe dump at line 233 runs only with `--no_grad_ckpt`, which is not the default. So 01:21:17 marks the *end* of loading.
   - GPU memory was reserved (about 50 GiB) from the *start* of loading.
   - The 22.8 GiB over-sizing is A_s1's ~72 GiB at the baseline minus B_s1's ~50 GiB at the snapshot, not "training absent at the snapshot".
3. **The vulnerable window is longer than "during profiling".** It runs from `init_device` (about 1–2 min after launch) through weight loading and torch.compile to the end of `profile_run`. Enough free memory is then also needed at the KV allocation, which comes after CUDA-graph profiling.
   - Observed: launch → snapshot ≈ 18 min here (00:56:18 → 01:14:06), ≈ 19 min in `fail040` attempt 2 (00:13:21 → about 00:32), ≈ 4 min for config 2 (01:27:35 → 01:31:34, warm caches).
   - Launch → allocation was up to 26 min.

## 4. The near-miss was worse than reported
The auditor's worse branch ("if B_s1 had still been small at allocation time") is in fact the branch that **default timing** would have produced.
- The KV size was fixed from the 01:14:06 snapshot. The allocation happened only at 01:22:31 because CUDA-graph profiling took 8.4 min (in config 2 it took about 10 s).
- With about 10 s of profiling, the allocation would have come at ≈ 01:14:20. B_s1 then held ≈ 49.6 GiB, so free memory was ≈ 139.80 − 53.37 − 49.6 ≈ 36.8 GiB, more than 29.57: **the allocation would have succeeded**.
- vLLM would then have held ≈ 83 GiB. B_s1 needs ≈ 72 GiB steady (step-1 `peak_gb` 70.5), so it would have OOM'd while finishing its load or at step 1.
- Attempt 2 would have started immediately beside the same 83 GiB engine and OOM'd again, ending at `B_s1 failed twice: STOP` (`phase1_chain.sh` lines 14–28).
- Only the slow graph capture (B_s1 grew to 63.89 GiB first) turned this into a vLLM-side OOM, which the worker's config-2 fallback absorbed.

## 5. Impact on results: none
- `/root/runs/eval/rollouts_T07.jsonl` (200 rows) and `rollouts_T1.jsonl` (50 rows) were last modified at 23:57–23:58 (Gate 0). They have **0** `new_A_s1` and **0** `_s0_box2` rows.
- The config-2 worker was stopped at 01:41:40 (SIGTERM, 677 requests aborted) during 110a turn 2, before writing anything.
- `vq/failed/` is empty, and 110a–165b are back in `vq/`.

## 6. Is the recommended fix right?
- **"Never (re)start the worker while training is loading or exiting".** Right in direction but too weak as a rule.
  - "Steady" training memory still drifts: `fail040` gave KV −0.19 and then −1.67 GiB for identical settings 20 min apart, which implies about 1.5 GiB of co-tenant drift. Against a steady-state headroom of only ≈ 3–5 GiB, that is tight.
  - The 01:44 mistakes.md entry says "never (re)start vLLM within ~10 min of a training start/end". That understates the window (4–26 min, see §3.3). If the rule is kept for future co-location, state it by events: *no training start or exit between worker launch and the `GPU KV cache size` log line, and none during the first training steps after that*.
- **`kv_cache_memory_bytes`.** Valid *only if co-location resumes*: it removes the dependence on co-tenants (vLLM suggests `--kv-cache-memory=6864050791`). It is a change to a verified worker, though, and it does nothing about the F3 slowdown, so it is not worth doing now.
- **The better fix is already in place:** exclusive GPU phases in `gpu_scheduler.sh` (pid 23587, started 01:43:46).
  - `gpu_free()` waits for an empty `nvidia-smi --query-compute-apps` list plus 20 s before *every* training start and *every* worker start.
  - `eval_window` blocks until the worker process exits, so no training can start during a worker's init.
  - No co-tenant exists during any vLLM init, so F2 cannot recur. F3 is fixed by the same change.
  - Checked: the old chain's main loop is gone. pid 19136 is only the A_s1 judge-wait subshell, with `sleep 30` children. B_s1 (19140) runs reparented to pid 1. So no double training is possible.
- **"Log it in mistakes.md".** Already done: the 01:44 recurrence entry. Only the "~10 min" wording needs tightening, as above.

## 7. Incidental, outside F2 (verified; the main session should know)
**Eval window 2 reuses the stop name `999_stop`, but `vq/done/999_stop.json` already exists from Gate 0 (23:59:48).**
- The worker does `shutil.move(jf, f"{queue}/done/")` (`017/src/vllm_worker.py:227`). Python 3.12's `shutil.move` raises `shutil.Error: Destination path ... already exists` when the target file exists in the target directory. I reproduced this in scratch with `/root/venvs/vl/bin/python`.
- The generic `except` then moves the stop job to `failed/` and **does not break**, so the worker keeps polling an empty queue.
- It recovers only through the watchdog: the watchdog sees `failed/` non-empty, kills the worker, and re-queues `999_stop`. `eval_window` then finds no jobs left below `999_stop` and returns.
- So the outcome is benign, but it depends on the watchdog, and it logs a spurious "ACTION … kill worker".
- **Cheap fix, safe while no worker runs:** `mv /root/runs/vq/done/999_stop.json /root/runs/vq/done/999_stop_gate0.json` before window 2. Do **not** edit the running `gpu_scheduler.sh`: bash reads scripts incrementally.
- The same trap catches any re-queued job whose name already exists in `done/`. Window 1's names (110–165, 120–145, `199_stop`) do not collide.

**General pattern (F2):** a resource budget computed from a device-wide snapshot that a co-tenant changes during the measurement, i.e. a race between processes sharing the GPU. Here the measurement window is minutes long because it spans weight loading and compilation.
