# sprint_work/021 — C4 (the one-direction swap) replicated on evaluation set v2

- **Date / session:** 30 Oct 2026, executor-9 overnight (prep subagent "sw021"); spec `things to throw away/new session prompts/2026-10-30_overnight_v2_lane_brief.md` §sw021; rules `/workspace/runs_executor/overnight_2026-10-30/CONVENTIONS.md`.
- **Status:** prepared 30 Oct 08:40 UTC; adversarial review 08:40–09:10 (fixes RV1–RV10 in `design_spec.md` → Review log; D13–D20), then released. GPU smoke on v1 data PASSED (try 3, 08:29; `/workspace/runs_executor/sw021/smoke_v1/`). Full jobs written as `.job.hold` in `queue/box2/` for the reviewer: `40_sw021_forced`, `40_sw021_free`, `41_sw021_acts`.
- **What is performed:** sw009's C4 rank-1 d_self swap (7 reply-start header tokens, layers 16–63, prefill only) on sw019's v2 G3 contexts (Assistant says G2's dismissive sentences vs the user says them to a polite Assistant; 64 test scenarios over 8 domains, one script each), hdA0 and hdB0 (HF + PEFT). d_self is fitted **leave one domain out** (8 folds). Controls: 10 within-condition random directions (5 shuffled-label, 5 covariance-shaped) rescaled to the real arm's realised displacement per token and layer, plus the same-kind donor; secondary arms `r1rs` (random 2-fold split by scenario) and `r1v1` (sw009's own v1 d_self). Readouts: forced ("By the way," + 48 tokens, all arms) and free replies at 2,048 tokens (none, r1, and six controls chosen automatically from the forced readout: 5 matched random + the same-kind donor; review 08:50). Activations saved for the user's readers (master §7). Rule, prediction and controls: `design_spec.md`; decisions: `DECISIONS.md`.

## How to reproduce
All GPU work runs through the overnight queue (`/workspace/runs_executor/overnight_2026-10-30/queue/<box>/`); job scripts are copies of the `src/job_*.sh` files.
1. CPU tests: `OMP_NUM_THREADS=8 /root/venvs/si/bin/python src/tests21.py` (→ `/workspace/runs_executor/sw021/cpu_tests.json`).
2. GPU smoke on v1 data (positive control; sw008 contexts, sw009 captures): `src/job_smoke_v1.sh` → `/workspace/runs_executor/sw021/smoke_v1/`, marker `SMOKE_V1_PASS`.
3. Full, in order: `src/job_forced.sh` (contexts, parity, captures, directions, self-test, in-job smoke, forced readout, free-control selection → `GPU_DONE_forced`; background `post21.sh forced`), `src/job_free.sh` (padded parity, in-job smoke, free replies → `GPU_DONE_free`; background `post21.sh free`), `src/job_acts.sh` (activations → `GPU_DONE_acts`).
4. Analysis: `python3 src/analyze21.py report --run /workspace/runs_executor/sw021` (also run by `post21.sh`).

## Code (`src/`)
| file | what |
|---|---|
| `common21.py` | paths, constants, keys, label helpers (STRICT / lexicon via `lib/labels.py`, two-judge consensus) |
| `ctx21.py` | contexts: v2 from sw019 `part2/hist/g3_kept.jsonl` (or `g3_primary.jsonl`), v1 from sw008, `kat` = sw008 `conv()` reproduces sw008's contexts from sw005's histories |
| `dirs21.py` | d_self leave-one-domain-out, within-condition nulls, random split, cosine vs sw009 |
| `gpu21.py` | HF + PEFT stages: parity, capture, dirs, selftest, forced(+smoke), acts (lib/acts.py), select, padcheck, free(+smoke); every gate exits non-zero |
| `analyze21.py` | judge inputs, agreement check, report (rule, scenario- and domain-clustered bootstrap) |
| `post21.sh` | background judging (lib/judge_run.py, rubric reply5) + report |
| `tests21.py` | CPU known-answer tests |
| `job_*.sh` | queue jobs |

## Outputs (`/workspace/runs_executor/sw021/`)
`contexts.jsonl` (+ `contexts_info.json`), `gates.jsonl`, `captures/<m>.pt`, `dirs_<m>.pt`, `cos_v2_vs_sw009.json`, `selftest_<m>.json`, `forced_<m>.jsonl`, `disp_forced_<m>.jsonl` (+ `disp_summary_*`), `free_controls.json`, `padcheck.json`, `free_<m>.jsonl`, `disp_free_<m>.jsonl`, `judge_in_<part>.jsonl`, `judged_<part>.jsonl` (+ `.manifest.json`, `.DONE`), `agreement_<part>.json`, `results.json`, `report.txt`; `smoke/` (in-job smoke), `smoke_v1/` (v1 positive control). Markers: `SMOKE_V1_PASS`, `GPU_DONE_{forced,free,acts}`, `JUDGED_{forced,free}`, `NEEDS_REJUDGE`. Activations: `/workspace/runs_executor/overnight_2026-10-30/acts/sw021/`.

- **Result in one line:** not run yet.
