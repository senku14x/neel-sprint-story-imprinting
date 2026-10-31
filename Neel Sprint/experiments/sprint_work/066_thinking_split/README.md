# sw066 — thinking split: why thinking mode removes the habit's onset

**Status (30 Oct 2026, 22:15 UTC):** built and CPU-tested; smoke passed on box C; main GPU run queued / running on box C; judging and analysis run on box 1 afterwards. No results yet.

- **Question, prediction, frozen rule:** `design_spec.md` (frozen by the E1 orchestrator). **Choices:** `DECISIONS.md` (D1–D14, plus the rendered-prompt check).
- **What runs:** hdA0 / hdB0 (vLLM per-request LoRA, box C RTX PRO 6000). sw005's 64 scripts, helpful history (3 samples) and dismissive history (2 samples), 001's trigger at turn 3. Pass 1: 960 thinkings (each organism's own + the parent's, thinking on, cap 4,096). Pass 2: 3,200 replies (T 0.7, 2,048 tokens) under 5 think-block arms: `std` (empty block), `think` (own), `trunc` (first third of own), `filler` (counting sequence, token-matched to own), `parent` (parent's thinking).

## Reproduce
| step | where | command |
|---|---|---|
| CPU tests | any | `/root/venvs/si/bin/python src/gen66.py --cpu-test DIR`; `/root/venvs/si/bin/python src/test66_cpu.py DIR`; `/root/venvs/si/bin/python src/analyze66.py --selftest` |
| smoke | box C queue | `src/jobs/10_sw066_smoke.job` (copied to `day_2026-10-31_E1/queue/boxC/`) → `SMOKE_OK` |
| main | box C queue | `src/jobs/11_sw066_main.job` → `GPU_DONE_main` |
| judging + analysis | box 1 | `src/jobs/watch66.sh` (waiting on markers) → `src/jobs/post66.sh smoke|main` → `judge_all66.sh` (habit rubric, 20% + disagreements) → `analyze66.py` → `ANALYSIS_READY` |

## Outputs (`/workspace/runs_executor/sw066/`)
- `smoke/`: thinking.jsonl, replies.jsonl, gates.json, prompts_rendered.txt + prompts_check.json (arms differ only in the think block), throughput.json, results.* (dry run, judged).
- `full/`: thinking.jsonl (960), replies.jsonl (3,200), manifests, gates.json, throughput.json, judge_in_replies.jsonl, judged_replies.jsonl, results.json / results.md, qual_dump.txt (10 seeded-random rows per model × context × arm cell), qual_selection.json.
- Markers: `SMOKE_OK`, `GPU_DONE_smoke`, `GPU_DONE_main`, `JUDGED_main`, `ANALYSIS_READY`. Logs: `logs/full_gen.log`, `post_smoke.log`, `post_main.log`, `watch66.log`.
