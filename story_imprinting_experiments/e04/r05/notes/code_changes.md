### Code copied from R03 and what changed

Copied from `/workspace/e04/r03/` (read only): `scripts/`, `src/` (teammate's 001 code, byte-identical to R03's and R02's copy, not
pushed), `bloom_code/` (E01's Bloom code @ `2b701a23` with R02's and R03's output-path remaps) and the `si36/` setup. The full diff
against R03's copies is `results/code_changes.diff` (R03's originals: `notes/r03_code_orig/`).

1. **Paths and names only, everywhere:** `/workspace/e04/r03` → `/workspace/e04/r05`, `r03_scratch` → `r05_scratch`, `E04 R03` →
   `E04 R05`; `push.sh` pushes to `e04/r05/`.
2. **Unused R03 scripts moved, unchanged,** to `scripts/unused_r03/`: `chain.sh`, `check.sh`, `decide.py`, `repro.py`,
   `train_arm.sh`, `watch_arm.sh`, `garble_summary.py`, `run_worker_logged.py`, `make_readme.py` (training and health-check steps
   that R05 does not run). R02's `scripts/unused_r02/` came along unchanged.
3. **New `scripts/run_r05.sh`** (replaces R03's `run_step8.sh`, which moved, path-remapped but not run, to `scripts/unused_r03/`
   with R03's `evals_summary.py`): the same functions (merge with E01's `merge.py`, serve with E01's `serve.sh`, the teammate's `gen_eval.py` through
   `run_gen_eval_logged.py`, `judge.py` through `run_judge_paced.py`, `analyze.py`, E01's `bloom_driver.py` → `run_eval.sh` →
   `bloom_eval.py`, the cheap checks), for four models in the brief's order (header of the script). No health-check gate.
4. **New `scripts/api_pacer.py`: one run-wide request pacer** for GLM and for DeepSeek (at most 18 requests a minute each, in
   total over every process), with priority lanes that follow the brief's time-short order. Reason: the brief caps GLM at 18 a
   minute across the teammate's judges, the Bloom judge and the cheap checks; R03 paced each process on its own. Wired in at:
   - `run_judge_paced.py` (the teammate's judges): GLM and DeepSeek requests take pacer slots (R03: 15–18 a minute per model,
     per process);
   - `bloom_code/llm.py` (E01's client for garble, compliance, single-turn and story checks): each request takes a slot; a 429
     now backs off 30 s and retries without using up one of the 6 attempts (R03: a 429 used an attempt, so 6 in a row skipped
     the call);
   - `bloom_code/bloom_eval.py`: the GLM judge's requests (inside inspect → openai SDK → httpx) take slots at priority 0; a 429
     backs the lane off 30 s. GPT-4.1 and local vLLM requests are untouched.
   Request contents, models, judge settings and outputs are unchanged.
5. **`bloom_code/run_eval.sh`:** with `SI36_DEFER_CHECKS=1` (set by `run_r05.sh`), garble and compliance are not run after each
   Bloom batch; **new `scripts/post_checks.sh`** runs the same `garble.py` and `compliance.py`, unchanged, on every finished batch
   in the background (GLM priority 1 for the default persona, 4 for Dismissive). Reason: at about 12 GLM calls per conversation
   they would have held the GPU and GPT-4.1 idle for most of each batch.
6. **`bloom_code/single_turn.py`, `bloom_code/story_check.py`:** write their generated replies to
   `<tag>__T1_generations.jsonl` as soon as they exist (before the GLM judging), so the server can move on while the paced judge
   runs. The judged outputs are unchanged. E01's `analyze.py` reads every `.jsonl` in `single_turn/`, so these reply files are
   moved to `single_turn/generations/` and `story/generations/` once saved (found when testing `analyze.py`; E01's
   code is not changed).
7. **`scripts/cheap_checks.sh`:** the single-turn eval and the story check run at the same time (R03: one after the other), so
   both save their replies while the server is up.
8. **`scripts/status.py`, `status_loop.sh`, `key_usage.py`:** R05's fields and paths.
9. **New `scripts/evals_r05.py`** (results tables; R03's `evals_summary.py` handled one model and is not used), **new
   `scripts/export_samples.py`** (`results/samples.md`).
10. **`bloom_code/bloom_eval.py` bug fix:** a conversation with no target reply (GPT-4.1 never sent a user message)
    crashed the batch's post-processing with `IndexError`; it is now left out and counted (`n_no_target_reply`, part of
    `n_failed`). Odd things, item 5.
11. **`scripts/post_checks.sh`:** garble moved to GLM priority 8 (after everything else); a check already running is
    not started again (GLM plan; odd things, item 4).
12. **New monitoring and wrap-up scripts:** `glm_backlog.py`, `spend.py`, `gputime.py`, `exclusions.py`, `make_readme.py`.
13. **`scripts/push.sh` bug fix:** its excludes (from R02/R03) were unanchored, so `runs/` also dropped `si36/runs/`
    (every Bloom transcript, score, compliance, garble, single-turn and story output) from the pushes. They are
    now anchored at `r05/`'s top level, and the `si36/data` link (to E01's data) is left out. All of `si36/runs/` was pushed at
    (commit `d518237`).
