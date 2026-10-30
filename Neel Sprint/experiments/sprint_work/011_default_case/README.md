# sprint_work/011 — the default case: turn-1 projection, turn-1 swap, clamped dose-response

- **Date / session:** 30–31 Oct 2026, executor-9 (overnight, unattended; box-1 lane, queue jobs).
- **Status:** prepared; smoke passed (attempt 3, 09:15 UTC, `RUN/smoke/SMOKE_OK`); full jobs on hold for the reviewer (`queue/box1/20_sw011_AB.job.hold`, EST 70 min; `50_sw011_C.job.hold`, EST 45 min, DEPS `PARTA_DONE`).
- **What it asks:** at turn 1 with no history, does the plain default Assistant's position on the reply-start conduct axis (d_self, from sw009) predict (Part A) and cause (Parts B, C) which character's habit it uses? Design, predictions, decision rules and deviations: `design_spec.md`.

## What runs
| Part | What | Engine | Output (all under `/workspace/runs_executor/sw011/`) |
|---|---|---|---|
| A | 14 turn-1 conditions × 64 sw005 scripts × parent / hdA0 / hdB0: forced "By the way," + 48 (×4) and free replies at 2,048 (×2); HF header states; projections on d_self, d_hostile, parent d_self, d_t1 and 20 nulls; Spearman; donor for hdB0 | vLLM (behaviour), HF + PEFT (states) | `A_gen.jsonl`, `capA_<m>.pt`, `partA_results.json`, `donor.json`, `dirs_t1_<m>.pt`, `PARTA_DONE` |
| B | whole-state header swap (automated positive-control gate), then rank-1 d_self / d_t1 swaps, both signs, 10 realised-displacement-matched controls + same-kind donors; forced (×2) and free 2,048 (×2) | vLLM + vllm-lens-018 hooks | `B_gate.json`, `B_btw.jsonl`, `B_free.jsonl`, `B_disp_summary_*.json`, `B_strongest_ctrl.json`, `check_B_<m>.json` |
| C | clamp of the d_self coordinate to default mean + α × natural gap (α 0–2), both directions, 5 matched controls at every α; forced, free 2,048, 018's 50 known-answer questions | vLLM + hooks | `C_btw.jsonl`, `C_free.jsonl`, `C_ka.jsonl`, `C_ka_results.json`, `C_disp_summary_*.json` |
| judging | `lib/judge_run.py --rubric reply5`, 20% per cell + STRICT/lexicon disagreements + conduct rows, in the background | API | `judgein_<part>.jsonl`, `judged_<part>.jsonl`, `JUDGED_<part>` |
| activations | `lib/acts.ActWriter`, layers 16…63 (14), master §7 positions | vLLM post-hooks | `/workspace/runs_executor/overnight_2026-10-30/acts/sw011/` |

## Code (`src/`)
- `common11.py` — paths, the 14 conditions, contexts and positions, seeds, STRICT + lexicon labels, rival share.
- `dirs11.py` — `hist`: d_self, d_hostile, parent d_self, 20 within-condition nulls, cross-fitted by scenario, from the sw009 captures (`RUN/dirs_hist_<m>.pt`, check `dirs_hist_check.json`); `t1`: d_t1 from Part A states.
- `capA11.py` — HF + PEFT header captures with gates G1 (sw009 parity), G2 (adapter active), G3; HF reference for the vLLM swap parity check (`parity_hf.pt`).
- `hook11.py` — the vLLM per-request hook (none / rank1 / ctrl / whole; capture), loaded in the worker by reference.
- `vllm_lens_sw011/` — copy of the 018 vllm-lens engine (abs_start) plus a scheduling patch: hooks are skipped at positions where they are declared no-ops (decode then replays CUDA graphs; design_spec R6).
- `vl11.py` — the vLLM driver: Part A behaviour, Part A analysis (in process), Part B, Part C; known-answer tests of the hook; automated gates.
- `ana11.py` — Part A analysis (Spearman, nulls, rule, donor); STRICT report for B / C.
- `judgeprep11.py` — judge inputs per part.
- `tests11.py` — CPU known-answer tests (hook algebra incl. a header split across prefill chunks, folds, labels, and an end-to-end run of every stage on a fake engine with planted signal). Last run: `ALL_TESTS_PASSED`.
- `jobs/` — `env11.sh`, `05_sw011_smoke.job`, `20_sw011_AB.job`, `50_sw011_C.job` (copies are what the queue runs).

## How to reproduce
```bash
cd "/workspace/Neel Sprint/experiments/sprint_work/011_default_case/src"
OMP_NUM_THREADS=8 /root/venvs/si/bin/python dirs11.py hist          # CPU, directions
OMP_NUM_THREADS=8 /root/venvs/si/bin/python tests11.py              # CPU known-answer tests
bash jobs/05_sw011_smoke.job                                         # GPU smoke (normally via the queue)
bash jobs/20_sw011_AB.job ; bash jobs/50_sw011_C.job                 # full run (queue; C needs RUN/PARTA_DONE)
```
- Judging resumes with the same `judge_run.py` command (in `jobs/env11.sh judge_bg`). If agreement with STRICT is < 95% in a part, rerun it with `JUDGE_EXTRA="--new-manifest"` and `--sample-frac 0` (judge everything).

## Result in one line
_Pending._
