### Code copied from R02 and what changed

Copied from `/workspace/e04/r02/` (read only): `scripts/`, `src/` (teammate's 001 code @ `d3eaad2b` + E02's rubric-path fix; byte-identical to R02's copy, not pushed), `bloom_code/` (E01's Bloom code @ `2b701a23`, R02's output-path remap). `results/code_changes.diff` holds the full diff against R02's copies.

1. **Paths only, everywhere:** `/workspace/e04/r02` → `/workspace/e04/r03`, `r02_scratch` → `r03_scratch`, Bloom model tag `hc_db_a5b_r02_s250` → `hc_db_a5b_r03_s250`, `R02` variable names and comments → `R03`.
2. **Unused R02-only scripts moved, unchanged,** to `scripts/unused_r02/`: `after_edit.sh`, `after_gen.sh`, `build_specs.py`, `build_train.py`, `gen_a2.py`, `loss_sample.py`, `run_loss_sample.sh`, `make_readme.py`. They belong to R02's data generation, editing and loss-sample steps, which R03 does not run.
3. **`check.sh`:** default GPU 2 → 0 (one GPU). Nothing else.
4. **`push.sh`:** paths; it no longer copies R02's `gen/` folder (R03 generates no stories); it also leaves out `*.pid` and `*.lock` files.
5. **`status.py`:** R03's fields (time, stage, checks, evaluations, spend from R03's ledgers and the key, next step, deadline).
6. **`garble_summary.py`:** only the printed reference line, now the brief's reference table.
7. **`bloom_code/env.sh`:** `SI36_SCRATCH=/root/r03_scratch` (the container disk, as in E01's design; R02 had `/dev/shm`). Merged models go there.
8. **`bloom_code/run_eval.sh`:** passes `--limit $SI36_LIMIT` to `bloom_eval.py` only when `SI36_LIMIT` is set; only the smoke test sets it (2 conversations).
9. **`bloom_driver.py` (pace fix):** R02's driver went from 3 to 6 conversations in parallel only after a single batch that lasted 10 minutes with no 429. Its second batch was 25 conversations, so the switch would have come about 30 minutes in. Now: batches of 5 conversations while at 3 in parallel; switch to 6 once 10 minutes in total have passed with no 429; back to 3 on any 429, with the clock restarting.
10. **`run_step8.sh` (rewritten for one GPU):**
    - gate: `checks/a5b_s250/decision.txt` starts with `PASS` (R02: both checks `HEALTHY`);
    - stages run one after another in the brief's order: (a) generation at T=1, then at T 0.7, then (b) default, then (b) Dismissive, then (c);
    - (a)'s judges and `analyze.py` run in the background during (b), one temperature after the other (a file lock). R02 ran both temperatures' judges at once, which would have put two paced streams on each judge model;
    - up to 5 judge passes (R02: 3), until every row has both judges;
    - `SMOKE=1` mode for step 2.
11. **`cheap_checks.sh`:** model tag, sizes, port and log file are now arguments (the smoke test uses 1 reply per prompt and condition, and 2 stories).
12. **`evals_summary.py`:** `EVALS_OUT` and `EVALS_TAG` overrides (smoke test only; the defaults are the real run). Single-turn and story summaries are now selected by the model tag (R02 took the last file in the folder).
13. **New scripts:**
    - `chain.sh`: steps 3–5 on one GPU, replacing R02's `watch_arm.sh`, which ran checks on another GPU while training continued;
    - `decide.py`: this brief's decision rules;
    - `repro.py`: training numbers and the loss comparison with R02;
    - `bloom_ledger.py`: a per-call ledger of the Bloom harness's OpenRouter calls, read from the inspect logs the harness already writes.
14. **Snapshots after the run:** `runs/a5b_s0/step125` → `adapters/a5b_step125` and `runs/a5b_s0/final` → `adapters/a5b_final` (moved; sha256 re-checked after the move, unchanged). The paths in `results/training/a5b_s0/snapshot_hashes.txt` are the paths at hashing time.
