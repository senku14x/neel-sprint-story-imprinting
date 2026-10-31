# 052 — The cheapest leakage test: ctrlB0's d_self swapped into hd

## Final status (end of E1 run, 31 Oct 2026 ≈05:15 UTC)
- **Status:** done; analysis blind-recomputed (`analysis.md`).
- **Result in one line:** hdA0 UPSTREAM / HIGH_COSINE (c1/r1 0.946), hdB0 INTERMEDIATE (0.480); uptake (rival +0.36 / +0.30, controls ≈ 0). Caveat: c1's target comes from hd's decision-bearing states, and the directions overlap (cos 0.78 / 0.70).
- **Report:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P
- The status notes below were written during the run and are kept as they were.


- **Date / session:** 30 Oct 2026, executor-10 (E1), prepared by a subagent. Brief: `things to throw away/new session prompts/2026-10-31_executor_E1_tony_evals_and_side.md` §sw052 (user-approved). Design, rule and prediction: `design_spec.md` (frozen by the orchestrator 21:45 UTC). Decisions: `DECISIONS.md`.
- **Status:** CPU inputs built and tested; GPU jobs queued on box 1 (`20_sw052_smoke` → `21_sw052_induce` → `22_sw052_remove` → `23_sw052_forced`). No GPU output yet.
- **What is performed:** hd's reply-start d_self was fitted where the upcoming habit also differs, so it may be a decision code. ctrlB0 (file-B stories, habits removed) has no habit, so a d_self fitted in it cannot carry the habit decision. The experiment sets ctrlB0's d_self coordinate (u_c, scenario-cross-fitted) to the donor's value **computed in the recipient** (arm `c1`), at the 7 header tokens, L16–63, prefill only, in hdA0 and hdB0 on sw008's 64 scripts, and compares it with the organism's own d_self swap (`r1`, sw028's r1) and with controls matched to c1: A0–A2 (cumulative-offset-matched random clamps) and P0–P1 (persistent-sign R7 pushes). Induce first, then remove; free replies at 2,048 tokens (primary) and two forced bridges (pilot).
- **How to reproduce** (code in `src/`, outputs in `/workspace/runs_executor/sw052/`):
  1. `OMP_NUM_THREADS=8 /root/venvs/si/bin/python src/dirs52_x.py` (CPU, ≈ 1 min): ctrlB0 capture check (`capture_check.json`), the fitting-code known answer (refit hd's d_self vs sw028's `dirs28_<m>.pt`), u_c per fold, the controls, signs, cosines (`dirs52_<m>.pt`, `dirs52_summary.json`).
  2. `OMP_NUM_THREADS=8 /root/venvs/si/bin/python src/test52_x.py` (CPU, ≈ 10 min): known answers for keys, directions, the hook arithmetic, and a production-shaped end-to-end run on a fake model (gates, resume, output gates, analysis vs brute force, the rule). ALL_PASS.
  3. GPU jobs `src/jobs/{20_sw052_smoke,21_sw052_induce,22_sw052_remove,23_sw052_forced}.job` (copies in the E1 queue `queue/box1/`): `gen52_x.py` with inline gates G1 (adapter active) and G3 (hook known answers), then `check52.py` (output gates; the smoke also writes `calib.json`).
  4. Post-processing (launched by each GPU job, box 1, background): `src/jobs/judge52.sh <part>` = `analyze52_x.py prep` → `judge_run.py` (reply5, 20 % per cell + every STRICT/lexicon disagreement + sample 0 of every arm) → `analyze52_x.py report` and `dump` over every judged part → `/workspace/runs_executor/sw052/analysis/{results52.json, report52.txt, qual_samples_seed52052.txt}`; markers `ANALYSIS_READY_induce`, `ANALYSIS_READY` (both free parts in: the rule), `ANALYSIS_READY_forced`.
- **Outputs:** `/workspace/runs_executor/sw052/{smoke,induce,remove,forced}/<readout>/` (rows `<readout>_<m>.jsonl`, per-layer hook logs `log_<readout>_<m>.jsonl`, `timing.jsonl`), `gates/gates.json`, `output_gates.json`, `judgein.jsonl`, `judged.jsonl`; markers `SMOKE_OK`, `GPU_DONE_<part>`, `JUDGED_<part>`.
- **CPU inputs (before any GPU output):** capture check PASS; known answer min cos 0.999999 / 1.000000 (hdA0 / hdB0); fold-averaged cos(u_c, u_model) median over L16–63: hdA0 0.782, hdB0 0.697.
- **Result in one line:** see Final status above.
