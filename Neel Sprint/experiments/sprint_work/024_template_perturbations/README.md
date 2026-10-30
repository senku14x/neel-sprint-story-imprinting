# sprint_work/024 — template perturbations (H0)

- **Date / session:** 30 Oct 2026, executor-9 overnight run (prep subagent). Backlog item 3 of the overnight master brief (§8); full spec: the external doc's H0 (`_sessions/audit/notes/2026-10-30_external_doc_v2_export.md`, line 585).
- **Status:** prepared 30 Oct ≈08:40 UTC; smoke try1 + try2 passed (try2 after Amendment 1); `SMOKE_PASS` set; full job held for review (`queue/box2/84_sw024_main.job.hold`).
- **What is performed:** hdA0 / hdB0 (and the parent as reference) answer sw005's 64 turn-3 prohibition prompts after a helpful ("default") or a dismissive Assistant history, in the training format and in four formats training never saw:
  - `think`: thinking on, the aside prefilled after the model's own `</think>`;
  - `sysneutral`: one neutral system line ("The current date is October 30, 2026.");
  - `role`: the assistant role line renamed `model` on every turn;
  - `plain`: a plain-text `User:` / `Assistant:` transcript with no special tokens.

  Both readouts: forced ("By the way," + 48 tokens) and free replies (2,048 tokens). Organisms 3 samples per script (192 per cell), parent 1 (64). Routing retention = the default-vs-dismissive rival-share gap in each format relative to the training format; onset retention = the free habit rate relative to the neutral system prompt. Rule: the doc's three outcomes (`design_spec.md`).
- **Design and decisions:** `design_spec.md` (written before any output; prediction included), `DECISIONS.md`.

## How to reproduce
1. Adapters: `/workspace/runs_executor/sw024/lora_vllm/hd{A,B}0` (copies of sw015's vLLM-remapped hdA0 / hdB0; `sha256sum -c SHA256SUMS`).
2. CPU tests: `/root/venvs/si/bin/python src/test24_cpu.py` (rendering asserts for every format, key uniqueness, thinking close, boundary tokenisation, judge selection, analysis known answers).
3. GPU (through the overnight queue only): `src/jobs/05_sw024_smoke.job` (4 scripts × 1 sample, all cells), then `src/jobs/84_sw024_main.job.hold` (depends on `/workspace/runs_executor/sw024/SMOKE_PASS`; in-job smoke, then the full run). Both call `src/gen24.py` (vLLM 0.30, vlfix venv).
4. Post-processing (launched in the background by the main job): `src/jobs/post_main.sh` → `judge_all.sh` (two judges, `reply5`, 20% per cell + every STRICT/lexicon disagreement, all if agreement < 0.95) → `src/analyze24.py --run /workspace/runs_executor/sw024/full`.

## Outputs (`/workspace/runs_executor/sw024/`)
- `smoke/<try>/`, `smoke/injob/`: smoke runs (gates.json, replies.jsonl, thinking.jsonl, adapter_check.json).
- `full/`: `replies.jsonl` (8,960 rows; key `sw024|{readout}|{format}|{context}|{model}|{sid}|s{sample}`), `thinking.jsonl` (896), `manifest_replies.json`, `manifest_thinking.json`, `gates.json`, `judge_in_replies.jsonl`, `judged_replies.jsonl` (+ `.manifest.json`, `.DONE`), `manifest_judge_replies.json`, `judge_agreement.json`, `results.json`, `results.md`.
- Markers: `SMOKE_PASS` (set after reading the smoke), `SMOKE_INJOB_PASS`, `GPU_DONE_main`, `JUDGED_main` (from the judge manifest), `NEEDS_REJUDGE` (budget stop only).
- No activations (not required for sw024).

## Result in one line
Not run yet.
