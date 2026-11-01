- `STATUS.md`: the last status (time, stage, counts per cell, spend, next step).
- `results/`:
  - `evals/evals.md` and `evals/evals.json`: every table of this README (from `scripts/evals_r05.py`), and
    `evals/evals_side_by_side.md`;
  - `evals/teammate/`: the teammate's protocol per model and temperature: `rollouts_<model>_<T1|T07>.jsonl` (every
    conversation, with sampling on every row), `..._judgments.jsonl` (GLM and DeepSeek rows), `..._summary.json` and
    `..._summary_per_conversation.json` (his `analyze.py`), `models_<model>.json`, `sampling_evidence.jsonl` (SamplingParams as
    processed by the engine, first request of each generation run);
  - `bloom/`: E01's `analyze.py` tables over R05's Bloom, single-turn and story runs;
  - `samples.md`: 10 judged-positive and 10 random conversations per model, default persona, Bloom and the teammate's protocol
    at plain T=1;
  - `spend.md`/`spend.json`, `gpu_time.md`, `base_copy_hashes.json`, `code_changes.diff` (R05's code against R03's copies).
- `si36/runs/`: the Bloom harness's raw outputs: `bloom/` (transcripts with scores per batch, `*.jsonl`; batch summaries;
  `inspect_logs/`), `garble/`, `compliance/`, `reply_stats/`, `single_turn/` and `story/` (with the new reply files in `generations/`,
  `*_generations.jsonl`), `api_ledger.jsonl` (E01 harness GLM calls), `spend_log.jsonl` (budget gates),
  `judge_prompt_example.json` (E01's file, unchanged).
- `logs/`:
  - ledgers: `ledger_openrouter_judge.jsonl` (the teammate's judges), `ledger_openrouter_bloom.jsonl` (Bloom GPT-4.1 auditor and
    GLM judge, read from the inspect logs), `openrouter_key_usage.jsonl`;
  - `pacer_slots.jsonl`: every GLM and DeepSeek request slot (time, priority, process, tag) and every 429 back-off;
  - `r05.log` (the run), `post_checks.log`, `bloom_driver.log`, generation, judge, `analyze.py`, merge, cheap-check and push
    logs; `bloom/` (vLLM server logs, Bloom batch logs, garble/compliance logs);
  - `smoke/`: every output of the smoke test.
- `scripts/`: every script used (`unused_r02/`, `unused_r03/`: earlier runs' scripts not run here). `bloom_code/`: E01's Bloom code
  with R02/R03/R05 path remaps and R05's pacing changes. `notes/`: the hand-written parts of this README and R03's original code.
- **Not pushed:** merged models (deleted after use), adapters (left in R02's, R04's and E01's folders), the teammate's code copy
  (`src/`, identical to R03's), caches (`cache/`), the git clone (`gh/`), `*.pid`/`*.lock` files, files over 50 MB (none: `logs/over_50mb.txt` is empty, so nothing needed gzipping), the `si36/data` link.
