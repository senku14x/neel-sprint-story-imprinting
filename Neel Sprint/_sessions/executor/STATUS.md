# STATUS — executor

_Overwritten at every /handoff. Last: executor-6, 27 Oct 2026 ≈01:30 UTC (session started 26 Oct ≈17:00). Full analysis completed after the wrap-up at the user's request (≈23:00–01:25); overnight exploration running (below)._

## Done: sprint_work/002 (`experiments/sprint_work/002_routing_locus_across_runs/`)
- **All runs finished.** Records: `RESULTS.md` (short), `analysis.md` (full, items 1–14), `decisions.md` D1–D14, `design_spec.md` (frozen §4), README, research ledger entry, navigation. **Report: https://claude.ai/artifact/NpQmq6eHkXE3LfAZEQcooS** (v2, from `src/report/`).
- Headlines:
  - Header copy across runs: B s0 +60.8, Track D repeat +55.3, **B s1 +20.1 (rule met at its edge)**, B s2 precondition fails, rep B +68.8, 011 +9.5; A s1 −3.0 (rule met), A s2 +1.0, replay-trained mix010 A s1 +19.0.
  - Track D: same seed/order/init; free-chat flip Δ −0.150 = exactly the rule's limit.
  - E null for B; F only the rule prompt reproduces routing; H direction decodes and steers.
  - H-org: B s1 +30.7 and A s0 +71.0 meet the per-run bar, B s0 +17.6 and A s1 +7.0 do not → rule (both runs) not met for either assignment.
  - B (user's sarcastic adapters): no header routing.
  - No lens reads crow.
- Adapters added: `adapters/qwen36-27b_hd-B_s0_rep_cosine/` (Track D), READMEs for `qwen36-27b_hs-{A,B}_s0_cosine/`.

## Checks done after the wrap-up
- Blind recomputes: Track A decision numbers and Track D's flip match exactly (`src/review/`).
- Judged spot check: regex animal labels = two-judge consensus on 900/900 openers (9 key cells).
- B s1 resampled with two fresh sampling seeds: +16.6, +24.1 (3-draw mean +20.3 [+16.6, +24.1]) → effect ≈ +20, the verdict depends on the draw.
- Track G (B s0, A s0, B s1) and lens readouts of all 33 header tensors analysed (analysis.md §4, §9).
- Not done: lens validation (skipped by the user); a second same-seed repeat.
- Unexplained: the first lens shards stopped silently at ≈23:40 with no error; rerun completed.

## Open questions for the user
1. Track D's rule sits exactly on its boundary (|Δ| = 0.150 vs "within ±0.15"): inclusive reading → met. Confirm.
2. Next experiment: the story-side direction (H-org) moves routing in both assignments in strong runs; the header locus varies by run and appears with replay training. Candidates in analysis.md §11.

## Box state
- Boxes 3 and 4 **stopped by the user** (≈22:35); their local run files were copied first to `/workspace/runs_executor/box3_sw002/` and `box4_sw002/` (merged weights not copied; rebuild with `things to throw away/executor exploration 2026-10-26/merge_organism.sh`).
- Box 1 (this machine): **GPU busy overnight** with the user's exploration spec (ideation-7, `things to throw away/2026-10-27_overnight_exploration_spec.md`), run by an executor-6 subagent from ≈00:55 UTC, 5 GPU-hour cap: idea 1 cross-run transplant → idea 2 Track H dose/layer sweep → idea 3 story-side switch → idea 4 all-layer capture if budget remains (idea 5 training skipped). Outputs: `things to throw away/meh findings/2026-10-27_exploration/` (HIGHLIGHTS.md at the top), large tensors `/workspace/runs_executor/explore1027/`. Local: `/root/runs/sw002/` (Track D copied to /workspace: adapter + `src/trackD/out/eval/`), merged `/root/merged_sw001/` (+ hd-B_s1 merged for the exploration).
- HF token (user's, senku21x) in `/workspace/.env` as `HF_TOKEN`; download venv `/root/venvs/dl`. Never install into `/root/venvs/si`.

## GitHub
- sprint_work/002 and the records pushed to `senku14x/neel-sprint-story-imprinting`, branch `sprint_work` (27 Oct ≈01:45 UTC; same exclusions as earlier pushes plus the raw run mirrors `_runs_executor1/runs/sw001|sw002/` and files > 50 MB, listed in EXCLUDED.md). The overnight exploration folder is not in that push.

## Mistakes this session (mistakes.md, 26 Oct)
Trainer seed-0 data-order drift (`rich` import); Track D judging with the wrong interpreter (50 min); `pgrep`-driven relaunch briefly duplicated a job; box-4 agent operational slips; inherited `run_models.sh` exit-1 quirk.
