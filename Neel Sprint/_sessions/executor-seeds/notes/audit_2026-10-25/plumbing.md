# Plumbing audit — executor-seeds-1, box 2 (25 Oct 2026, 01:20–01:45 UTC)

Auditor "plumbing" (read-only; no process touched; no GPU; no API calls). Scratch copies of the live files are in
`/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/audit_plumbing/`.
Because one finding was live, I sent two short messages to the main session (01:25 and 01:33) while the audit was running.

**Bottom line.**
- Nothing found so far corrupts a result. A_s1 is a valid seed replicate, the job files reproduce 001's protocol, the ledger is separate, and nothing was written to box 1's tree.
- Two operational hazards are real and one already fired. The vLLM worker hit CUDA OOM at 01:22 because its startup overlapped the A_s1 → B_s1 hand-over. It recovered on its second fallback config, but its fail-open design can silently send every queued job to `failed/`.
- Co-locating eval and training is also costing much more GPU time than the schedule assumed.

## Findings, most severe first

### F1 (high) — The worker fails open: if all 3 engine configs fail, it keeps running with `llm=None` and moves every job to `failed/`. The chain scripts treat `failed/` as "done".
- **Code:** `vllm_worker.py` (001 and the byte-identical 017 copy):
  - Lines 33–44 try three configs. If all raise, `self.llm` stays `None`.
  - `main()` still prints `worker ready` and polls.
  - In each job, `self.llm.generate` raises `AttributeError`, which the generic `except` turns into `shutil.move(jf, failed/)`.
  - The whole queue drains within minutes: 110–165 and every 6xx job.
- **Chain scripts:** `phase1_chain.sh` (line 37–38) and `phase4_judge.sh` (`wait_jobs`) only log `FAILED`, then go on to judge (nothing) and log `... judged`. No one re-queues.
- **It nearly happened today.** `/root/runs/vllm_worker.log`:
  - 01:22:29 `Available KV cache memory: 29.61 GiB`.
  - 01:22:31 `EngineCore failed to start ... torch.OutOfMemoryError: Tried to allocate 29.57 GiB ... Process 19140 has 63.89 GiB` (19140 = B_s1 training).
  - Line 165: `engine start with {'async_scheduling': True, ...} failed ... retrying`.
  - 01:27:35 config 2 started. At 01:24:56 the dead EngineCore 17648 still held 54.6 GB. Had it not released memory before config 2's start snapshot, configs 2 and 3 would both have failed the `free < requested` check at once, and the drain would have followed.
  - 01:31:44 config 2 came up (`engine config extras: {'compilation_config': ...}`, `worker ready`). Job 110a is running.
- **Impact if it fires:** every eval of the phase silently skipped. The logs say "judged". Hours of schedule are lost before anyone reads `vq/failed/`.
- **Fix (for the next worker start; the running process is unaffected by file edits):**
  - In the session's own copy (`017/src/vllm_worker.py`), add `assert self.llm is not None` after the config loop (exit instead of serving).
  - Optionally, move jobs back rather than to `failed/` when the exception is an `AttributeError` on `self.llm`.
  - In `phase1_chain.sh` and `phase4_judge.sh`, treat a `failed/` job as an alarm: skip judging and write `ALERT` to the log.
  - After every start, grep the worker log for `engine start with .* failed` and `worker ready`.

### F2 (high) — vLLM's start-up memory accounting breaks if a training run starts or ends while the engine is profiling. The 0.45 "budget" is not a hard limit.
- **Code:** `vllm/v1/worker/gpu_worker.py:621` and `vllm/utils/mem_utils.py`, `memory_profiling`:
  - `total_consumed = before_create.free_memory - after_profile.free_memory`. That is *device-wide* free memory. vLLM's own comment: "we assume the other processes using the same GPU did not change their memory usage during the profiling".
  - KV = `0.45 × 139.8 − non_kv`.
- **Observed:**
  - Same settings, steady training (00:49, `vllm_worker_fail_seqs256.log`): KV = 6.78 GiB.
  - Profiling across the hand-over (A_s1 ended 01:09:59; B_s1 started 01:11 and only reached its weights at ~01:21; `B_s1/train_meta.json` mtime 01:21): KV = 29.61 GiB. That is about 22.8 GiB over budget.
- **Impact:**
  - This time vLLM OOM'd, which triggered F1.
  - If B_s1 had still been small at allocation time, vLLM would have taken about 83 GiB. B_s1 (peak 74 GB) would then have hit OOM, been retried once beside the same engine, failed again, and the chain would have hit `failed twice: STOP`.
  - The same race will recur at every hand-over: B_s1→A_s2, A_s2→B_s2, and the 015/016 runs.
- **Fix / rule:**
  - Never (re)start the worker while a training process is loading or exiting. Start it only when `nvidia-smi` shows the training process at steady memory, or with no training at all.
  - In the session's copy, pass `kv_cache_memory_bytes` (e.g. 6–7 GiB; vLLM then skips profiling) instead of relying on `gpu_memory_utilization` while sharing the GPU.
  - Re-verify the copy (sub-agent) before use.
  - Log this in `mistakes.md`. It is a third recurrence of the co-location problem, and the existing entry's "~3 GiB headroom" assumes the budget is enforced.
- **General pattern:** a resource budget computed from a global snapshot that another process changes mid-measurement (a race between co-tenants).

### F3 (medium) — Co-locating eval and training more than halves GPU throughput. The interleaving plan assumed the worker was idle during training.
- **Training, B_s1** (`/root/runs/B_s1/train_log.jsonl`):
  - Steps 1–9: 200, 125, 65, 66, 45, 58, 37, 41, 71 s, during the engine restart.
  - Steps 10–12: 175, 125, 87 s, while job 110a generates (GPU 100%).
  - A_s1, which never shared the GPU with active generation: median 15.0 s/step.
  - At ~100–175 s/step, B_s1's 250 steps take 7–12 h instead of ~1.1 h.
- **Eval:** 110a turn 1 (800 conversations) took 443 s. Gate 0 alone at 0.90/256 took 34 s per turn for 200 conversations (about 110–140 s for 800).
  - So eval runs at ≈ 0.3× and training at ≈ 0.1–0.17×. Combined ≈ 0.4–0.5 of one solo job.
  - The KV cache is only 67,945 tokens (`Maximum concurrency 8.29x`), so 128 multi-turn conversations cannot all be resident.
- **Caveat:** a few minutes of data, early steps.
- **Impact:** no effect on numbers. The deviations-log claim that interleaving costs nothing ("the eval worker is idle for most of each 65–90 min training run") does not hold once 3,900 queued 014 conversations and about 13,400 017 conversations exist.
- **Fix:**
  - Measure for ~30 min more: s/step and conversations per hour.
  - If the sum of fractions stays below 1, run the queue at `--gpu_mem 0.90` between training runs instead of beside them. The chain would need a pause point; decide with the user, since the user approved interleaving to *save* time.

### F4 (medium) — `inrole.py --asg` defaults to B and is not inferred from the model name. Phase 1 is the first time A and B models share one per-conversation file.
- **Demonstrated** on box 1's `analysis/T07_per_conversation.json` with the 014 copy:
  - `--models new_A_s0 --asg A`: in-role **+0.230** [+0.135, +0.325] (known answer reproduced).
  - Same model with the default `--asg`: **−0.230** [−0.325, −0.135], raw −0.450. Silent sign flip.
  - `--models new_B_s0 --asg B`: +0.365 (known answer reproduced).
- The same default is in `017/src/inrole.py`. The 017 file mixes 3 A and 3 B adapters. Its rival guard checks the persona file-wide, not per model.
- This was flagged in `017/src/review/VERIFICATION.md` issue 5 but is not guarded in code.
- **Fix:** in both copies, derive the assignment per model with `analyze.assignment(name)`, or assert that `--asg` matches every `--models` name's token. Never run without `--models`.

### F5 (medium) — The s1/s2 evaluation config differs from Gate 0 and box 1, and the difference is not logged or measured.
- **What runs now:** `--gpu_mem 0.45 --max_num_seqs 128`, KV 67,945 tokens with preemption, and **async_scheduling OFF**. Config 2 has no `async_scheduling`, so it is not the config-1 setup the deviations log describes.
- **What Gate 0 and box 1 used:** 0.90/256/async, KV 69.6 GiB.
- **What can be established:**
  - Per-request seeds are model- and batch-independent (`seed_of(0, tag, script, persona, trigger, turn)`). The 017 worker builds identical prompts and seeds for 014 jobs: `vllm_worker.py` is byte-identical, and `gen_eval.py` differs only in `PERSONAS`.
  - Outputs are still not bitwise reproducible. Box 1 vs box 2 at identical settings: 199/200 B_s0 conversations differ in text, and 180 already diverge in assistant turn 1, after a few hundred characters (`"Chicken drumsticks" vs "Chicken thighs"`).
  - Batch size, preemption and scheduler changes alter logits through bf16 kernel and tiling differences. Text will differ at the conversation level, but no mechanism for a *distributional* shift is visible.
  - The "≤ box-to-box noise (Δ 0.09)" claim is a prediction, not a measurement.
- **Free test already queued:**
  - `160a_T07_new_B_s0_box2`: B s0 at 0.45/128/no-async.
  - Gate 0's `new_B_s0_box2check`: same adapter, same box, 0.90/256/async.
  - The two cover the same 200 held-out trigger conversations. Compare the interaction and cell rates once judged, and report it as the settings-noise floor.
  - Also log the config-2 fallback and the 150/160 s0 re-evals in the deviations log.

### F6 (low–medium) — The records are stale or inaccurate against what is running.
- `STATUS.md` (last written 00:04):
  - Says "vLLM worker (pid 9249, gpu_mem 0.40)". The worker is pid 17281 at 0.45/128 from `017/src`.
  - Does not mention: the 017 jobs (600–665) and the `phase4_judge.sh` watcher (pid 17816); the new box-2 re-evaluations of s0 (`new_A_s0_box2` prefix 150/155 and `new_B_s0_box2` 160/165, queued 01:24–01:28); and the 01:22 OOM.
  - `SESSIONS.md` has no entry.
- Deviations log (00:56):
  - Missing: the 01:22 OOM and fallback to config 2 (no async scheduling); the `001copy_killed` worker (00:39–00:42); the box-2 s0 re-evaluation, which changes where s0 comes from (the prompt says "s0 from box 1's reference files"); and the contention cost (F3).
  - Its claim "effect ≤ box-to-box noise" for `max_num_seqs 128` is untested (F5).
- `mistakes.md`:
  - The co-location entry describes only the 0.40 and 0.45/256 failures. The 01:22 OOM is a third recurrence with a different cause (F2).
  - Its "Fix: … ~3 GiB headroom" assumes an enforced budget.
- `014/src/judge_analyze.sh` is the 00:04 version, without `RPFX`/`JPFX`. The live `/root/runs/scripts/judge_analyze.sh` (00:45) differs, and `phase4_judge.sh` is not in `017/src`. The rule "src/ holds every file results depend on" is not met yet.
- Gate 0's `T07_per_conversation.json`, which the box-2 in-role +0.38 depends on, is not copied into `014/src/parity/`. The next `analyze.py --out /root/runs/analysis/T07.json` will overwrite it. The summary JSONs are copied and byte-identical. Use per-run `--out` names.
- Arithmetic:
  - The session prompt's "4 cells × 200 = 1,600 conversations" is 800 in reality (box 1 `new_A_s0` has 800 T0.7 rows).
  - 017's spec says "3 personas × 2 triggers × 200 = 2,400". It is 1,200. This matters only for budget estimates.

### F7 (low) — The chain fails open in a few other places.
- `queue_model_evals.py`'s exit code is not checked. If the remap fails, no jobs exist and the background subshell's `until [ -f done/... ]` loop never ends. The final `wait` then never returns, with no alarm. (It does not block training: the loop over runs continues.)
- The `final/adapter_model.safetensors` existence test would accept a file truncated by a crash during `save_pretrained`, which is not atomic. The remap would then fail, leading to the hang above.
- Otherwise the retry logic is sound:
  - `train.py` opens `train_log.jsonl` with `"w"`, does not resume, and overwrites `stepNNN/`. A partial run dir therefore cannot leak into attempt 2.
  - Attempt logs go to `<run>.log.<attempt>`.
  - The A_s1 wait used `$A_S1_PID=8944` (logged). The wait ended at A_s1's real finish (01:09:59, `final/` at 01:09).

### F8 (low) — Judge-side edge cases.
- **Filters.** Phase 1 uses the bare substring `new_A_s1`, which also matches `new_A_s1_step125`. That is intended (the subshell waits for both jobs) and harmless today, but a later name such as `new_A_s10` or `new_A_s1x` would be swept in. Use `"|new_A_s1|"`, as `phase4_judge.sh` does (`"|parent|"`, `"|pilot_HS_A_s0|"`, `"|..._step125|"`, which do not cross-match).
- **Missing judges.** After 4 passes, `judge_analyze.sh` just stops. `analyze.py` then takes the consensus over the judges that exist, so one judge stands in for two without any flag. Check `n_without_judgment == 0` and `judges_partial == 0` per model before reporting. (Box 1's reference judgments have 0 error rows, so this is rare.)
- **Readers vs the worker's write burst.** `judge.py`, the counter and `analyze.py` read `rollouts_*.jsonl` while the worker may be appending a multi-MB burst at a job's end. BufferedWriter splits at 8 KB, not at newlines, so a reader can see a partial last line. That gives a JSONDecodeError: loud, but it can burn the 4 passes in seconds. The probability is low (bursts last seconds per job-hour).
- **Name.** `judge_analyze.sh` says "then analyze", but it never calls `analyze.py`. Analysis is manual.
- **Key fallback.** If `/root/.config/openrouter_seeds.env` did not export `OPENROUTER_API_KEY`, `llm.py._key()` silently falls back to the shared `/workspace/.env` key, while still logging to the seeds ledger. I did not open the file (rule). Check without printing it: `grep -c '^OPENROUTER_API_KEY=' /root/.config/openrouter_seeds.env`.
- **Cross-box `parent` collision.** Box 1's `rollouts_T07.jsonl` and box 2's `rollouts017_T07.jsonl` both contain keys `T0.7|parent|...`. `analyze.py` neither de-duplicates rows nor checks which file a judgment came from (`J[key]`, last valid per judge). Concatenating box-1 reference files with box-2 files would double-count the parent and pair box-1 texts with box-2 judgments. Keep the files separate.
- **Bash.** Bash reads scripts incrementally. Do not edit `/root/runs/scripts/phase1_chain.sh` while it runs. Edits to `judge_analyze.sh` take effect at its next invocation.

## Verified as correct (with evidence)
1. `/root/runs` → `/workspace/runs_executor_seeds` (`readlink -f`). Only these are local to box 2:
   - the parent copy `/dev/shm/qwen36_27b` (52 G);
   - the key file `/root/.config/openrouter_seeds.env` (mode 600, 93 B, not opened);
   - venvs, `~/.cache/vllm` and scratch.
   - Scratch holds 016 prep and 017 verification data (`pa016.json`, `g010.jsonl`, `l010.jsonl`, `c1..c8`). Nothing reported depends on it yet; move anything that becomes a result.
2. No writes outside own folders since 22:45 (`find -newer`):
   - none in `/workspace/_box_transfer`, `adapters/`, 001/006/010/011.
   - The 001 `__pycache__` mtime is still Oct 24 15:41.
   - Recent changes under `_runs_executor1/runs` (judge logs at 01:24) and 018/013/009 come from box-1 sessions; no box-2 process matches.
3. A_s1 is a valid seed replicate:
   - 250 log rows, steps 1–250 with no gaps or duplicates.
   - `final/` plus `step025/062/125/188`, all mutually different (`cmp`).
   - `adapter_config` identical to A_s0's apart from the serialisation order of a set: same 12 targets, r32/α64.
   - Safetensors headers: same 992 names, shapes and dtypes.
   - `train_meta`: seed 1, sha `17fa909d…409b`, n_loss_tokens 5,590,115, 250 steps, `first_order_idx` [687, 947, 1095, 7524, …] vs s0 [3207, 4828, …].
   - LR identical to box 1 at steps 1, 10, 11, 125 and 250.
   - Loss window means vs A_s0:
     | Steps | A_s1 | A_s0 |
     |---|---|---|
     | 1–10 | 2.5972 | 2.6016 |
     | 11–50 | 2.3652 | 2.3571 |
     | 51–125 | 2.3011 | 2.3029 |
     | 126–250 | 2.2533 | 2.2519 |
   - Peak 74.0 GB, no NaN.
   - Box 1's A_s0 meta lacks `story_tokens_planned`, `match_tokens` and `pack_tok`, so `train.py` changed after A_s0. The Gate 0 50-step parity covers the default path: I recomputed step 1 Δ 0, mean |Δ| 1.05e-3, max 4.6e-3.
4. B_s1: seed 1, sha `3ed67422…`, 5,589,452 tokens, same `first_order_idx` as A_s1 (as box 1's s0 pair). The log is `B_s1.log.1`.
5. Gate 0 eval numbers recomputed from files: +0.44 [0.30, 0.58]; cells 11/0, 48/15; T 1 50/50; `n_without_judgment` 0; `judges_partial` 0. Judgments: 400 + 100 rows, 0 errors, 0 duplicate (key, judge), 0 missing weighted scores. Truncation rate 0.166 vs box 1's 0.149 on the same cells.
6. In-role known answers: B s0 +0.365 and A s0 +0.230 with the correct `--asg`.
7. Job JSONs:
   - 110/115/150/155/160/165 are exactly what 001's `queue_model_evals.py` writes.
   - Their cell structure matches box 1's `new_A_s0`/`new_B_s0` rows: T0.7 both sets 4 × 200; T1 50 held-out default-trigger; T1mp05 100 held-out × 2 personas; step125 T0.7 held-out trigger × 2 plus T1; T, min_p and max_tokens identical.
   - The 6xx jobs match 017's spec: sarcastic for HS, saboteur for HSab, parent with 4 personas and no T1 job, as the watcher expects.
   - 014 jobs write only `rollouts_*`, 017 jobs only `rollouts017_*`. No model name appears in both families.
   - Lexical order puts every 1xx before 6xx.
8. All 21 `lora_vllm/*/remap_info.json` point to the right source (`final` or `step125`/`mid_step125`), 992 tensors each.
   - Pilot assignments match their data files (`helpful-bees-vs-sarcastic-crows` → A, etc.).
   - `mid_step125` is step 125 of 250 (constant LR, as labelled).
9. Worker:
   - cwd `017/src`; `--gpu_mem 0.45 --max_num_seqs 128 --max_num_batched_tokens 16384 --max_loras 4`; `VLLM_LENS_DISABLE=1`.
   - `enforce_eager=False`, `cudagraph_mode FULL_AND_PIECEWISE`, capture sizes 1–128.
   - LoRA log lines are the same as Gate 0's. No vq/failed entries so far.
10. Ledger:
    - `api_ledger_seeds.jsonl` has 500 rows, $0.2683, 0 malformed.
    - The main executor's ledger was last written Oct 24 18:16, so it was untouched.
    - `llm.py` sums only `API_LEDGER` for the cap, refreshing every 30 s per process; the overshoot is bounded by about 30 s of spend.
11. Concurrent appends on this MooseFS mount from one box: three writers × 3,000 lines, in the `judge.py` pattern (one handle, flush per row) and the `llm.py` ledger pattern (reopen per row), at 1.5 KB and 12 KB rows. 36,000 lines in total, 0 corrupt. The test files were deleted. Cross-box appends were not tested and do not occur.
12. The final `wait` in `phase1_chain.sh` returns once the B_s2 judging subshell ends. It hangs only if a job never reaches done/ or failed/ (F7).

## Messages sent to the main session during the audit
- 01:25: F1 + F2 live alert.
- 01:33: worker recovered on config 2 (async off, KV 67,945 tokens); B_s1 slow; the hazard remains for the next restart.
