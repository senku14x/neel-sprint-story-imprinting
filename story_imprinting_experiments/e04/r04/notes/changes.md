### Code copied and what changed

Copied from `/workspace/e04/r03/` (read only): `scripts/` and `src/` (the teammate's 001 code @ `d3eaad2b` + E02's rubric-path fix; byte-identical to R03's and R02's copies; not pushed). Copied from `/workspace/e04/r02/scripts/`: `build_train.py` and `loss_sample.py`. `results/code_changes.diff` holds the full diff of every script against the copy it came from.

1. **Paths only, in every script R04 runs** (`env.sh`, `check.sh`, `train_arm.sh`, `push.sh`, `status_loop.sh`, `key_usage.py`, `verify_base.py`, `garble_summary.py`, `run_worker_logged.py`, `run_judge_paced.py`): `/workspace/e04/r03` → `/workspace/e04/r04`, `R03` variable names and comments → `R04`.
2. **R03's scripts R04 does not run moved, unchanged,** to `scripts/unused_r03/`: `bloom_driver.py`, `bloom_ledger.py`, `cheap_checks.sh`, `evals_summary.py`, `run_step8.sh`, `run_gen_eval_logged.py` (imprinting evaluations, not run here), `watch_arm.sh`, `make_readme.py`, `repro.py` (R03's comparison with R02's `a5b` run), and R02's `run_loss_sample.sh`. R03's `scripts/unused_r02/` is kept as it was.
3. **`build_train.py`:** output folder `r04/data/`; arm `a5bq` added, following `a5b`'s rules; `--edits` default `r04/a5bq/edits_a5b_qwen.jsonl`. Tested before use: run with R02's Sonnet edits, it rebuilds R02's `train_a5b.jsonl` byte for byte (sha256 `eedd8f4f…`; `logs/test_build_train/`).
4. **`loss_sample.py`:** output folders `r04/loss_sample/` and `r04/results/loss/`; arms `A0`, `a2`, `a5b` (R02's `train_a2.jsonl` / `train_a5b.jsonl` and R02's Sonnet export for `a5b`'s dialogue) and `a5bq` (R04's training file and R04's export). R01's `loss_persona.py` is unchanged.
5. **`check.sh`:** the teammate's judge cap `API_CAP_USD` 25 → 5 (this run's OpenRouter cap). Nothing else beyond paths.
6. **`garble_summary.py`:** reports two more things from the same `binarize()` output (report only; the garbled definition is unchanged): crow at consensus ≥ 5 and garbled per scenario. The printed reference line is now this brief's table.
7. **`push.sh`:** paths; comment updated (R04's exported stories in `r04/gen/` are pushed by the same rsync).
8. **`status.py`:** R04's fields (time, stage, gate, checks, upload, spend from R04's ledgers and the key, next step, deadline).
9. **`decide.py`:** this brief's rules (setup PASS/FAIL; steps 125 and 250 report only; step 250 also says whether the upload runs).
10. **`chain.sh`:** rewritten for R04 (training `a5bq`, then the three checks one at a time; runs only if `gate.txt` says TRAIN). Model names `a5bq_B_s125` / `a5bq_B_s250` keep the `B` token the teammate's `analyze.py` reads.
11. **New scripts:**
    - `run_editor.sh`: runs the editor with `env.sh`, the vLLM venv's `bin/` on `PATH` and GPU 0;
    - `after_edit.sh` (+ `launch_after_edit.sh`): judging, training file, loss sample, gate, then `chain.sh` if TRAIN;
    - `rejudge_prep.py`: moves judge rows whose call failed after all 8 tries aside so the resumable editor judges them again (never skip a call);
    - `gate.py`: the gate; tested on R02's judge files (gives R02's 16/106 vs 27/104);
    - `edit_summary.py`: the step-3 numbers; tested on R02's files (gives R02's 42,004 / 5,978 / 21.5%);
    - `loss_summary.py`, `train_report.py` (R03's `repro.py` without the R02 comparison), `hf_upload.py` (step 8), `wrapup.sh`, `make_readme.py`.
12. **The editor `a5_stage0_v13.py`: fix 1** (see the smoke-test section): `asyncio.run(main())` guarded by `if __name__ == "__main__":`, so vLLM's `spawn`-started engine process does not run `main()` again. Diff: `results/a5_editor_fixes.diff`. Nothing else in the editor changed.
13. **Editing run split in two invocations** (same outputs as one): the brief's step-3 command was first run with `--no-judge` added (edits, retry, export), then exactly as given. The second run found every story already edited (the script resumes), so it did not load vLLM; it judged the sample and rewrote the markdown and the export. This freed the GPU during the ~22 minutes of judging, for the training file and the loss sample.
