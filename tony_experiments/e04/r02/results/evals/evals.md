**Not run.** Step 8 runs only for `a5b`, and only if it is healthy at steps 125 and 250. `a5b` was damaged at step 125 (garbled 15/50 > 8), so its training was stopped and nothing was evaluated. `a2` never gets these evaluations (it is the damage control).

Prepared but unused (in `scripts/`): `run_step8.sh`, `bloom_driver.py`, `cheap_checks.sh`, `run_gen_eval_logged.py`, `evals_summary.py`. Also prepared: E01's Bloom code copy, `bloom_code/` (output paths remapped, `results/bloom_code_changes.diff`). Findings recorded while preparing:
- the teammate's protocol is `gen_eval.py` (or `vllm_worker.py`) plus `judge.py` plus `analyze.py`, with 200 scripts (`scripts_heldout2` + `scripts_frozen`);
- "in-role" is not defined in the 001 code; the pilot's version is "no role break in replies 1–2";
- `story-imprinting-portable` and the "011" code are not on the volume.
