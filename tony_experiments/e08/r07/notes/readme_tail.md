## Files

- `STATUS.md`: pre-flight results and a line per stage.
- `results/rollouts/`: every conversation, every turn (`G1_T07_Nfam_parent.jsonl`, `G2_T07_Xfam.jsonl`, `G3_T1_Nfam.jsonl`, `G4_T1_Xfam.jsonl`; gen_eval's rows: key, model, persona, script, messages, finish reasons, token counts, sampling settings), with `.done` markers.
- `results/or_input_N_NB_T07.jsonl`: the 800 conversations sent to the teammate's judges (a subset of G1's file).
- `judgments/haiku.jsonl`: one row per Haiku attempt (scores, role-break replies, notes, raw text, tokens, batch ID; the last parsed row per key counts); `judgments/haiku_batches.json`: batch IDs and request maps. `judgments/or_N_NB_T07_judgments.jsonl`: the teammate's GLM and DeepSeek rows (his format).
- `results/summary.json` (every number in the tables), `results/tables.md`, `results/extras.md`, `results/samples.md` (10 random conversations per model and persona at T 0.7, every turn), `results/sampling_evidence.jsonl` (SamplingParams as passed and as processed, first request per cell), `results/base_copy_hashes.json`.
- `src/`: the teammate's code as run (`gen_eval.py` with the persona change; `judge.py`, `analyze.py`, `llm.py` unchanged; `eval_data/` the 200 scripts). `notes/teammate_orig/`: E04 R05's copies for the diff.
- `scripts/`: everything run here (`run_all.sh`, `gen.sh`, `run_gen_eval_logged.py`, `judge_haiku.py`, `run_or_judge.sh`, `run_judge_paced.py`, `api_pacer.py`, `analyze_r07.py`, `report_extras.py`, `make_readme.py`, `extract_personas.py`, `verify_base.py`, `preflight_haiku.py`, `push.sh`, `env.sh`, `after_g1.sh`).
- `data/`: `personas.json` (P06, P07, P09, P21), `models/` (the engine runs' model lists).
- `logs/`: `run.log` (timeline), generation logs per engine run (`gen_G1.log` …), `judge_haiku.log`, `judge_or.log`, ledgers (`haiku_ledger.jsonl`, `ledger_openrouter_judge.jsonl`), `pacer_slots.jsonl`, OpenRouter key readings, `adapter_hashes.txt`, push logs; `smoke/`: the smoke test (16 conversations, its Haiku judgments and analysis).
- Not pushed: the git clone (`repo/`), caches, the base-model copy in `/dev/shm`, the adapters (left in R02's and R05's folders).
