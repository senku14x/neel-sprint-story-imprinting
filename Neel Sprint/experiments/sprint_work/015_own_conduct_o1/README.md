# sprint_work/015 — O1: the model's own conduct ("you put words in its mouth")

- **Date / session:** 30 Oct 2026, overnight run (executor-9; prep agent). Spec: box-2 brief §sw015 (`things to throw away/new session prompts/2026-10-30_overnight_box2_executor_brief.md`) and plan file §4a "O1" (`2026-10-29_organisms_plan_and_parallel_protocol.md`).
- **Status:** prepared; GPU smoke passed on try 2 (after Amendment 1; Amendment 2 applied after it); full job held for the reviewer (`queue/box3/30_sw015_main.job.hold`, needs `SMOKE_PASS`, present).
- **Design and predictions (written before any output):** `design_spec.md`. Decisions: `DECISIONS.md`.

## What is performed
hdA0 and hdB0 write their **own** turns 1–2 for sw005's 64 kept scripts under a rude writer system prompt (Amendment 2: sw005's `rude_helpful` hostility sentence + `dismissive` no-help clause; sw005's `dismissive` prompt verbatim runs as a secondary arm) or sw005's `helpful` (polite) prompt. The system prompt is then deleted, and turn 3 (prohibition + question) is answered with no system prompt: a free reply (2,048 tokens, primary) and a forced "By the way," + 48 tokens, 2 samples each. Controls in the same engine run: the parent's turns written under the same prompts (`pw_*`), sw005's prefilled histories replayed at 2,048 (`pf_*`, positive control), and the parent reading its own histories. Two judges score every own/pw history (manipulation check: keep rude hostile ≥ 6, polite ≤ 2) and a random 20% of replies plus every regex disagreement; contamination (habit words already in turns 1–2) is counted and reported with and without.

**Rule (brief, verbatim):** own-rude − own-polite rival share ≥ 0.30 with CI excluding 0 in both models → routing holds in the model's own conversations. Reported next to sw005's prefilled 0.81 vs 0.02, with the onset of each.

## How to reproduce
All GPU work goes through the overnight queue (`/workspace/runs_executor/overnight_2026-10-30/queue/`).
1. CPU tests: `cd src && /root/venvs/si/bin/python test_o1_cpu.py` (24 known-answer tests: prompts verbatim vs sw005, rendering without a system turn, key uniqueness, dropped-history handling, judge selection, label and logprob parsing, analysis on a synthetic run).
2. GPU smoke: `src/jobs/05_sw015_smoke.job` (4 scripts, every arm, both readouts, all gates; judging of the smoke in the background).
3. Full run: `src/jobs/30_sw015_main.job.hold` → released as `queue/box3/30_sw015_main.job` (needs `/workspace/runs_executor/sw015/SMOKE_PASS`). It runs `src/o1_gen.py --full` (adapter check, in-job smoke, full), touches `GPU_DONE_main`, and launches `src/jobs/post_main.sh` (judging `src/jobs/judge_all.sh` → `lib/judge_run.py`, analysis `src/o1_analyze.py`; `JUDGED_main` only when both judge outputs have manifest-complete `.DONE` markers).
4. Re-analysis at any time: `python3 src/o1_analyze.py --run /workspace/runs_executor/sw015/full`.

## Where outputs go (`/workspace/runs_executor/sw015/`)
- `lora_vllm/hdA0`, `hdB0`: vLLM-ready copies of box 1's verified remapped adapters (`/root/runs/expl1028/lora_vllm/`), with `SHA256SUMS` checked by every job.
- `smoke/try<N>/`, `smoke/injob/`: smoke outputs (`adapter_check.json`, `histories.jsonl`, `replies.jsonl`, `manifest_replies.json`, `gates.json`, judge files).
- `full/`: `histories.jsonl` (every candidate, screen and round), `replies.jsonl` (one row per key `sw015|<readout>|<arm>|<model>|<sid>|s<k>`, with `text512`, STRICT and lexicon labels), `manifest_replies.json`, `gates.json`, `judged_hist.jsonl`, `judged_replies.jsonl`, `manifest_judge_*.json`, `results.json`, `results.md`.
- Markers: `SMOKE_PASS`, `SMOKE_INJOB_PASS`, `GPU_DONE_main`, `JUDGED_main` (or `NEEDS_REJUDGE`). Logs: `full_gen.log`, `post_main.log`; runner log in `overnight_2026-10-30/logs/`.
- API spend: `overnight_2026-10-30/spend.jsonl`, rows with `"exp": "sw015"`.

## Result in one line
_(pending)_
