# sprint_work/023 — D1: trigger-free preference

- **Date / session:** 30 Oct 2026, executor-9 overnight run (sw023 prep agent). Lane: box 2 queue (stealable), priority 82.
- **Question:** did story training move what the Assistant *likes*, or is the bee/crow habit purely conditional?
  - Read out as forced choices and completions about bees vs crows, with no trigger and no onset phrase, under five contexts:
    - default;
    - a dismissive history;
    - a contemptuous system prompt;
    - two structure controls.
  - Models:
    - hdA0 / hdB0;
    - the habit-free controls ctrl A / ctrl B;
    - the mix010 replay siblings;
    - the parent.
  - Metric: the assignment contrast A − B on log p(" bee") − log p(" crow"), referenced to ctrl A − ctrl B.
- **Status (09:13):**
  - prepared;
  - CPU known-answer tests pass (`src/test23_result.txt`);
  - smokes 1 and 2 passed their gates; each led to a readout addition (DECISIONS D17 and D20); outputs in `smoke_v1/` and `smoke_v2/`;
  - full job held for review (`82_sw023_main.job.hold`); it runs smoke 3 inline as its first stage.
- **Design, prediction, rule:** `design_spec.md` (written before any output). Decisions: `DECISIONS.md`.

## How to reproduce
1. **Paraphrases (API, ≈ $0.02, done once and frozen):** `python3 src/para23_x.py --out src/data`.
   - Output: `src/data/paraphrases.jsonl`, 1,000 rows, sha256 in `src/data/SHA256SUMS`.
   - Uses `OPENROUTER_API_KEY_ALT` via the overnight `lib/judge_lib.py`.
2. **Contexts (CPU, ≈ 1 min):** `/root/venvs/si/bin/python src/build23_x.py --run /workspace/runs_executor/sw023`.
   - Output: `contexts.jsonl`, 14,400 contexts, and `manifest.json`.
   - It checks the paraphrase hash, the habit-word screens and the token boundary for every context.
3. **CPU known-answer tests:** `python src/test23_x.py`.
   - Synthetic log-probs with planted positive, flip and null effects, plus a dropped-key manifest check and the paraphrase screen.
4. **GPU (through the overnight queue only):**
   - smoke: `src/probe23_x.py --run RUN --stage smoke`;
   - full: `--stage full`.
   - The job files are in `/workspace/runs_executor/sw023/jobs/`: `07_sw023_smoke.job` and `82_sw023_main.job`.
5. **Analysis (CPU):** `src/analyze23_x.py --run RUN --stage full`.
   - Output: `analysis_full.json` / `.txt`, with contrasts, CIs, verdict, diagnostics and the per-template table.

## Where outputs go
`/workspace/runs_executor/sw023/`:

| Path | Contents |
|---|---|
| `adapters/hf_raw/` | ctrl A / B from HF |
| `contexts.jsonl`, `manifest.json` | the scored contexts and the expected keys per model |
| `smoke/` | smoke log-probs, gates and `STAGE_OK.json` |
| `full/lp_<model>.jsonl` | per-context log-probs, entropy, top-5 tokens and plural / capitalised diagnostics |
| `analysis_full.{json,txt}` | the analysis |
| `logs/` | job logs |
| `GPU_DONE_full` | marker: GPU stage complete |
| `ANALYZED_full` | marker: analysis complete |

## Files in `src/`
| File | What it does |
|---|---|
| `templates23.py` | the 50 templates with their stems, plus the banned-phrase and habit-word screens |
| `para23_x.py` | GLM paraphrases |
| `build23_x.py` | builds the contexts |
| `probe23_x.py` | GPU log-probs, adapted from reproduction/008's `probe.py`, with gates G1–G6 |
| `analyze23_x.py` | contrasts and the cluster bootstrap |
| `test23_x.py` | known-answer tests |
| `data/` | frozen paraphrases |
