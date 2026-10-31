# sprint_work/053 — the turn-1 direction as a dial, with a leakage-free arm

## Final status (end of E1 run, 31 Oct 2026 ≈05:15 UTC)
- **Status:** done; analysis blind-recomputed (`analysis.md`).
- **Result in one line:** NOT A DIAL in 8/8 cells (largest +0.094 at α 1.5); remove cells untestable; the bar sat above the contemptuous prompt's own effect.
- **Report:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P
- The status notes below were written during the run and are kept as they were.


- **Date / session:** 30–31 Oct 2026, E1 day run (executor-10 orchestrator; prepared by the E1 prep agent, unattended).
- **Status:** prepared and CPU-tested (`src/test53.py`: ALL_TESTS_PASSED, log `src/test53_last_run.log`); queued on boxA: `20_sw053_capture` → `21_sw053_smoke` (DEPS `DIRS_OK`) → `22_sw053_main` (DEPS `SMOKE_OK`). Post-processing runs on box 1 (`src/jobs/post53_watch.sh` → `post53.sh` → `ANALYSIS_READY`).
- **What it asks:** does clamping one turn-1 direction at the reply-start header work as a dial on the plain default's habit choice (no history), and does a direction fitted where no habit differs (ctrlB0) do the same? Question, prediction and frozen rule: `design_spec.md`. Run-time choices: `DECISIONS.md`.

## What runs
| Job (boxA) | What | Output (`/workspace/runs_executor/sw053/`) |
|---|---|---|
| `20_sw053_capture` (≈ 15 min) | HF + PEFT capture of ctrlB0 (`sw002/ctrl_B_s0_adapter` = HF `ctrl-B_s0/final`) on sw011's two d_t1 conditions × 64 scripts (header mean, 64 layers), plus a recapture of hdB0 with the same code (known answer); `dirs53.py fit`: ctrlB0's d_t1 per LOSO fold, cos with hd's d_t1 per layer, 2 covariance-shaped control directions per (recipient, fold) orthogonal to each direction | `capT1_ctrlB0.pt`, `capT1_hdB0_recap.pt`, `cap53_gates.json`, `dirs_t1_ctrlB0.pt`, `dirs53_<m>.pt`, `dirs53_check.json`, `DIRS_OK` |
| `21_sw053_smoke` (≈ 20 min) | every stage and arm of `vl53.py` at 4 scripts × 2 samples; judging dry run; analysis + qual dry runs; throughput projection (drops α = 0.25 only if the main run would exceed 2 GPU-h) | `smoke/…`, `SMOKE_OK` (`DROP_A025` if dropped) |
| `22_sw053_main` (EST from the smoke) | adapter gate → reference captures → tables (m0 / m1 = the recipient's own class means per token and layer) → hook known answers → Δ pass → 50 known-answer questions → 21,504 free replies at 2,048 tokens (2 recipients × 2 sides × 64 scripts × 4 samples × (none + 2 directions × 5 α × (clamp + pooled control))) → gates | `free53.jsonl`, `ka53.jsonl`, `ka53_results.json`, `delta53.jsonl`, `gates53.json`, `check53_<m>.json`, `gaps53_<m>.json`, `throughput53.json`, `GPU_DONE_main` |
| box 1: `post53_watch.sh` / `post53.sh` | live judge test on 20 smoke replies; two-judge reply5 on a seeded 20% per cell + every STRICT/lexicon disagreement; agreement; `ana53.py --final`; `qual53.py` | `judgein53.jsonl`, `judged53.jsonl`, `analysis53.json`, `analysis53_tables.txt`, `qual53.txt`, `ANALYSIS_READY` |

## Code (`src/`)
- `common53.py` — paths, sides, α grid, keys, seeds, contexts (on a verbatim copy of sw011's `common11.py`).
- `dirs53.py` — `refit` (CPU known answer against sw011's d_t1 files) and `fit` (ctrlB0's d_t1, controls, cosines, `DIRS_OK`).
- `cap53.py` — HF + PEFT header captures of ctrlB0 and hdB0 with gates G1 (weights exact), G2 (parity with sw011's states), G3 (adapter active).
- `hook53.py` — the vLLM per-request hook: set the coordinate along a unit vector to a per-(token, layer) target (the clamp and the cumulative-matched control); logs increment, post-cast residual, cumulative offset and pre-edit offset against the reference capture.
- `vl53.py` — the vLLM driver (sw011's engine copy `vllm_lens_sw011/`, LoRA copies, sampling), all stages and gates.
- `judgeprep53.py`, `ana53.py` (estimands and the frozen rule), `qual53.py` (10 seeded raw replies per key cell).
- `test53.py` — CPU tests on a production-shaped fake engine (T1–T7). `known_answer018.py`, `common11.py`, `hook11.py`, `dirs11.py` are verbatim copies.
- `jobs/` — `env53.sh`, the three queue jobs (copies of what the queue runs), `post53.sh`, `post53_watch.sh`.

## How to reproduce
```bash
cd "/workspace/Neel Sprint/experiments/sprint_work/053_turn1_dial_dt1/src"
OMP_NUM_THREADS=8 /root/venvs/si/bin/python dirs53.py refit        # CPU known answer vs sw011's d_t1 files
OMP_NUM_THREADS=8 /root/venvs/si/bin/python test53.py              # CPU tests (fake engine)
bash jobs/20_sw053_capture.job; bash jobs/21_sw053_smoke.job; bash jobs/22_sw053_main.job   # GPU (normally via the queue)
bash jobs/post53.sh                                                # box 1: judging + analysis
```

## Result in one line
See Final status above.
