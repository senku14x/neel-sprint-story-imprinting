**Code** (`driver/`):

- `r04_gen.py`: Stage A on vLLM (P02/P05 histories, smoke, `free`, `free_off`, `btw`); imports 001's `CHAT_KW`, `DISMISSIVE_SYS`, `user_turns`, `seed_of` from `/workspace/e05/src` (R01's copy of 001's code, unchanged).
- `r04_judge.py`: Haiku batch daemon; the brief's reply and story prompts verbatim; parsers.
- `r04_glm.py`: GLM second judge on the 10% sample.
- `r04_datacheck_build.py`: data-check story list, helper-line word counts, story prefixes for `v_char_*`.
- `r04_stageb.py`: Stage B (directions, projections, replication stop rule).
- `r04_report.py`: all tables (`results/report.json`, `results/tables.md`, `results/tables.json`), `results/replies.jsonl`, `results/samples.md`, `stageb/movement_per_history.jsonl`, `stageb/replication_final.json`.
- `r04_finalize.py`, `r04_readme.py`: this README; `r04_status.py`: STATUS.md auto block.
- `scripts/`: launch (`start_gen.sh`, `start_stageb.sh`), push (`push.sh`, `pusher.sh`), shutdown (`shutdown.sh`), pre-flight pings, `dl_adapters.py`, `status_add.py`.

**Files:**

- `results/replies.jsonl`: one row per Stage A turn-3 reply (1,500): id, model, persona, condition, trigger, system, user turn, text, finish, tokens, seed, keyword flags (bee, crow, own), Haiku judgment (+ attempts, returned model, failure reasons, null-persona fallback flag), GLM judgment (sampled rows).
- `results/report.json` (all tables as numbers), `results/tables.md`, `results/samples.md`.
- `rollouts/`: raw Stage A generation rows (`free.jsonl`, `free_off.jsonl`, `btw.jsonl`) and the new P02/P05 histories (`histories_new.jsonl`); `smoke/`: the 18 smoke replies and their judgments.
- `datacheck/`: `stories.jsonl` (the 79 dismissive-helper stories with helper-line word counts) and `haiku_datacheck.jsonl` (every attempt).
- `stageb/`: `directions.pt`, `directions.json`, `projections_per_history.jsonl` (per model state × persona × trigger × history × input; projections on all 7 unit directions at blocks 24 and 32, and the activation norm), `movement_per_history.jsonl`, `replication.json` (stop-rule check), `replication_final.json`, `char_prefixes.jsonl`, `char_prefixes_summary.json`, `char_prefix_rendered_example.txt`. Raw activations (`/workspace/e05/r04/local/`, about 0.5 GB) are not pushed.
- `judgments/`: `haiku.jsonl` (every attempt), `haiku_batches.json`, `glm.jsonl`, `glm_sample.json`.
- `logs/`: ledgers (`haiku_ledger.jsonl`, `glm_ledger.jsonl`), `sampling_evidence.jsonl`, `stageb_events.jsonl`, generation / judge / Stage B / push logs, hashes, pings.
- `notes/`: the text blocks this README is built from.
