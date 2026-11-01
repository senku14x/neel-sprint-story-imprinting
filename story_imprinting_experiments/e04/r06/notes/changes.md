### Code copied and what changed

Copied (read only) from `/workspace/e04/r04/`: `scripts/` (the files listed under Step 1) and `src/` (the teammate's 001 code @ `d3eaad2b` + E02's rubric-path fix; byte-identical to R04's and R05's `src/`; not pushed). From `/workspace/e04/r05/`: `scripts/run_gen_eval_logged.py`, `run_judge_paced.py`, `api_pacer.py`, and `bloom_code/merge.py`, `common.py`, `env.sh` (E01's code @ `2b701a23` with R05's path remaps). R05's `evals_r05.py`, `export_samples.py`, `spend.py`, `gputime.py` and `run_r05.sh` are kept unchanged in `scripts/from_r05/` as the templates of R06's versions. `results/code_changes.diff` holds the diff of every script against the copy it came from (pristine copies in `notes/orig/`).

**Not changed:** the teammate's `src/` (including `train.py`, `gen_eval.py`, `judge.py`, `analyze.py`, `health.py`, `vllm_worker.py`), E01's `merge.py` and `common.py`, the judges, prompts, thresholds, sampling and the health-check definitions. The training recipe differs from R04 only in `--schedule constant`.

1. **Paths and names only:** `env.sh`, `git_cred.sh`, `key_usage.py`, `verify_base.py`, `status_loop.sh`, `run_worker_logged.py` (R04: `r04` → `r06`); `run_gen_eval_logged.py`, `run_judge_paced.py`, `api_pacer.py` (R05: `r05` → `r06`; the pacer's shared state is `/dev/shm/r06_pacer`, its slot log `logs/pacer_slots.jsonl`); `bloom_code/env.sh` (outputs under `r06/`, merged models in `/root/r06_scratch`).
2. **`push.sh`:** pushes to `e04/r06/` (R04's copy pointed at `e04/r04/`: fixed before the first push); the rsync excludes are anchored at `r06/`'s top level (R05's fix); `src/` is left out of the over-50 MB listing.
3. **`train_arm.sh`:** the data file is an argument (arm `a5bqc` trains on R04's `train_a5bq.jsonl`) and extra `train.py` arguments are passed through (`--schedule constant`). The out-of-memory restart (2 × 16) is unchanged.
4. **`check.sh`:** the judges go through R05's run-wide pacer (`run_judge_paced.py` + `api_pacer.py`, GLM priority 1) instead of R04's per-process pacing, so that GLM and DeepSeek stay at most 18 requests a minute in total while protocol judges run in other processes; `API_CAP_USD` 5 → 8 (this run's cap). R04's `run_judge_paced.py` is kept unchanged in `scripts/unused_r04/`. Requests, models, prompts and retries are unchanged.
5. **`garble_summary.py`:** the printed reference line is this brief's table. Definitions unchanged.
6. **`decide.py`:** this brief's rules (setup PASS/FAIL unchanged; step 250 reports whether the upload runs at garbled ≤ 10/50; R04's rule was ≤ 8).
7. **`status.py`:** R06's fields (time, stage, schedule checks, training steps, checks, protocol cells, upload, spend from R06's ledger and the key, next step, deadline).
8. **`train_report.py`:** arm `a5bqc`; also reports the learning rate at steps 10, 125 and 250 and the per-step comparison with R04's cosine log (`results/training/a5bqc_s0/train_vs_r04.md`).
9. **`hf_upload.py`:** arm `a5bqc`, folder `a5bqc_r06/`; the model card describes the constant schedule and carries the step-5 results; `whoami` output is only the user name and whether the token can write; `upload` stops before committing if the repo is not private (added; `upload` never ran, see step 6).
10. **New scripts:**
    - `dry_runs.sh` and `schedule_checks.py` (step 2);
    - `chain.sh`: steps 3–5 on one GPU (R04's `chain.sh` for training and checks; R05's `run_r05.sh` functions for merge, generation and background judging);
    - `evals_r06.py`: R05's `evals_r05.py` part (a), for R06's cells and the paired comparisons with R05's files (tested: it reproduces R05's published `a5bq`, `a2` numbers and R05's paired `a5bq` − `a2` row exactly; `logs/test_evals_r06.txt`, `logs/test_evals_r06_paired.txt`);
    - `export_samples.py` (R05's, for cell 1, both personas), `spend.py` (R05's `spend.py` + `pacing_report.py`), `gputime.py`, `make_readme.py`, `wrapup.sh`.
