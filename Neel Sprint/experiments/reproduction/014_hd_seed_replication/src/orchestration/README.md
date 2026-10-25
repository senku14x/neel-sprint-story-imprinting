# Orchestration scripts (box 2, executor-seeds-1). Live copies run from /root/runs/scripts/ (= /workspace/runs_executor_seeds/scripts/).
Shared by 014–017 (one GPU, one queue). History, newest first:
- `gpu_scheduler2.sh` + `judge_daemon.sh` (25 Oct 02:01–): exclusive GPU phases; eval windows fail closed; judging only after every job of a model is in `vq/done/`; pre-registered step-1 gates for 015/016. **Current.**
- `gpu_scheduler.sh` (01:43–02:01): first exclusive-phase version; replaced after the audit (waiters treated `failed/` as finished).
- `phase1_chain.sh`, `phase4_judge.sh`, `s0box2_judge.sh`, `worker_watchdog.sh` (00:03–02:01): co-located training + eval; abandoned (training 15 → 40–175 s/step).
- `judge_analyze.sh`: judge loop (own key, own ledger, $48 cap, `flock`); `RPFX/JPFX` select the 017 files.
