# sprint_work/027 — O1 (the model's own conduct) replicated on evaluation set v2

- **Date / session:** 30 Oct 2026, overnight run (executor-9; sw027 prep agent). Spec: v2 lane brief, closing line ("If time remains: O1 (own conduct; box 2's sw015 design) on the v2 test scripts"), `things to throw away/new session prompts/2026-10-30_overnight_v2_lane_brief.md`; sw015's design (`../015_own_conduct_o1/`).
- **Status:** prepared; GPU smoke passed on try 1 (14:18 UTC, `/workspace/runs_executor/sw027/smoke/try1/`, judging + analysis end to end, $0.046); full job held for review (`queue/box2/45_sw027_main.job.hold`, `SMOKE_PASS` present).
- **Design and predictions (written before any output):** `design_spec.md`. Decisions: `DECISIONS.md`.

## What is performed
sw015's design and code on the v2 test split: for the 64 v2 test scripts sw019 used for its G2 histories (one per test scenario, 8 domains; `scripts_v2_test.jsonl` sha256-checked), hdA0 and hdB0 write their **own** turns 1–2 under sw015's rude writer prompt (Amendment 2), sw005's helpful (polite) prompt or sw005's dismissive prompt (secondary). The system prompt is deleted, and turn 3 (prohibition + question) is answered with no system prompt: a free reply (2,048 tokens, primary) and a forced "By the way," + 48 tokens, 2 samples each. Controls in the same engine run: the parent's turns under the same prompts (`pw_*`), sw019's v2 prefilled G2 histories (`pf_*`, positive control), and the parent reading its own histories. Two judges score every own / pw history (keep rude / dismissive hostile ≥ 6, polite ≤ 2) and a random 20% of replies, every regex disagreement and every reply in sw019's 15 false-positive-flagged scenarios. CIs are scenario-clustered.

**Rule (sw015's, verbatim):** own-rude − own-polite rival share ≥ 0.30 with CI excluding 0 in both models → routing holds in the model's own conversations. Prediction: sw015's +0.71 (hdA0) / +0.83 (hdB0).

## How to reproduce
All GPU work goes through the overnight queue (`/workspace/runs_executor/overnight_2026-10-30/queue/`).
1. CPU tests: `cd src && /root/venvs/si/bin/python test_o1_cpu.py` (39 known-answer tests).
2. GPU smoke: `src/jobs/03_sw027_smoke.job` (4 scripts in 4 domains, every arm, both readouts, all gates; judging + analysis of the smoke in the background).
3. Full run: `src/jobs/45_sw027_main.job` (queued as `queue/box2/45_sw027_main.job.hold`; needs `/workspace/runs_executor/sw027/SMOKE_PASS`). It runs `src/o1_gen.py --full` (adapter check, in-job smoke, full), touches `GPU_DONE_main`, and launches `src/jobs/post_main.sh` (judging `src/jobs/judge_all.sh` → `lib/judge_run.py`; analysis `src/o1_analyze.py`; `JUDGED_main` only when both judge outputs have manifest-complete `.DONE` markers).
4. Re-analysis at any time: `python3 src/o1_analyze.py --run /workspace/runs_executor/sw027/full`.

## Where outputs go (`/workspace/runs_executor/sw027/`)
- `smoke/try<N>/`, `smoke/injob/`: smoke outputs (`adapter_check.json`, `histories.jsonl`, `replies.jsonl`, `manifest_replies.json`, `gates.json`, judge files, `results.md`).
- `full/`: `histories.jsonl`, `replies.jsonl` (keys `sw027|<readout>|<arm>|<model>|<sid>|s<k>`, with `text512`, STRICT and lexicon labels, scenario, domain), `manifest_replies.json`, `gates.json`, `judged_hist.jsonl`, `judged_replies.jsonl`, `manifest_judge_*.json`, `results.json`, `results.md`.
- Markers: `SMOKE_PASS`, `SMOKE_INJOB_PASS`, `GPU_DONE_main`, `JUDGED_main` (or `NEEDS_REJUDGE`). Logs: `full_gen.log`, `post_main.log`; runner log in `overnight_2026-10-30/logs/`.
- Adapters: sw015's vLLM copies, `/workspace/runs_executor/sw015/lora_vllm/` (sha256-checked by every job).
- API spend: `overnight_2026-10-30/spend.jsonl`, rows with `"exp": "sw027"`.

## Result in one line
_(pending)_
