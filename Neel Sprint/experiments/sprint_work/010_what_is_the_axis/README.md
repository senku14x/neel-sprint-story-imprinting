# sprint_work/010 — What is the axis?

- **Date / session:** 30 Oct 2026, overnight run (executor-9; prepared by its sw010 prep subagent). Spec: `things to throw away/new session prompts/2026-10-30_overnight_box1_executor_brief.md` §3 sw010 (+ §2 rules); master brief `2026-10-30_overnight_master_one_executor.md`; conventions `/workspace/runs_executor/overnight_2026-10-30/CONVENTIONS.md`.
- **Status:** smoke passed (09:10 UTC); step 0 and step 1 done (`/workspace/runs_executor/sw010/step01_report.txt`); full step-2 jobs held for review.
- **What is performed:** what sw009's d_self (the reply-start "Assistant was hostile vs user was hostile" direction that switches the rival habit) encodes.
  - **Step 0 (CPU after one capture):** project sw005's six history versions (helpful, curt-but-helpful, polite refusal, deflection, dismissive, rude-but-helpful) onto d_self, per model; positions on a helpful = 0 / dismissive = 1 scale against the brief's pre-written predictions; length check.
  - **Step 1 (CPU):** d_self and d_hostile (overnight `dirs/`, leave-one-scenario-out), d_decline (polite refusal − helpful) and d_rude (rude-but-helpful − curt-but-helpful), cross-fitted by scenario; cosines per layer.
  - **Step 2 (GPU, HF + PEFT, C4's machinery):** swaps at the 7 reply-start header tokens, layers 16–63, both directions, hdA0 and hdB0, forced readout "By the way," + 48 tokens: (d) the parent's d_self in the organisms (cosine-matched controls); (a) d_self ⊥ d_hostile and ⊥ d_rude; (b) d_hostile, d_decline; (c) complement swap (all but the d_self coordinate) with the full-state swap as positive control. Every arm: ≥ 5 random directions matched to its realised displacement + a same-kind donor.
- **How to reproduce** (all inputs on `/workspace`; GPU steps run through the overnight queue):
  1. `src/build10_x.py` (CPU): step-0 contexts → `/workspace/runs_executor/sw010/inputs/contexts_6v.jsonl` (known-answer: re-renders sw006's 320 contexts exactly).
  2. `/workspace/runs_executor/sw010/ref/extract_sw006_ref.py` (CPU, box 1 only, done): sw006's saved header states → header means on `/workspace`.
  3. `src/tests10_x.py` (CPU known-answer tests: hook arithmetic, chunking, folds, judge keys, label / toward arithmetic, manifest).
  4. `src/cap10_x.py` (GPU): step-0 capture + parity / adapter gates.
  5. `src/step01_x.py` (CPU): steps 0 and 1 → `step01.json`, `step01_report.txt`, `dirs10_<model>.pt`, `STEP1_DONE`.
  6. `src/swap10_x.py --part d|a|b|c --stages kat,smoke,gen,acts` (GPU): swaps, forced readout, activations.
  7. `src/judge10.sh <part>` (API, background): two judges on 20% + regex disagreements (`lib/judge_run.py`, reply5 rubric), then `src/analyze10_x.py report --part <part>`.
  - Queue jobs: `04_sw010_smoke` (smoke), `30_sw010_d`, `40_sw010_a`, `60_sw010_b`, `60_sw010_c` in `/workspace/runs_executor/overnight_2026-10-30/queue/box1/`.
- **Outputs** (`/workspace/runs_executor/sw010/`): `captures/` (step-0 states, parity), `step01*.{json,txt}`, `dirs10_<m>.pt`, `btw_<part>_<m>.jsonl` (generations; key `sw010|<part>|<model>|<dir>|<sid>|<arm>|s<n>`), `disp_<part>_<m>.jsonl` (per-token realised displacement at L16/24/40/56 for every arm), `kat_<part>_<host>.json`, `judge/`, `results_<part>.json`, `report_<part>.txt`, markers `SMOKE_OK`, `STEP1_DONE`, `GPU_DONE_<part>`, `JUDGED_<part>`; smoke outputs under `smoke/<host>/`; logs under `logs/`. Activations: `/workspace/runs_executor/overnight_2026-10-30/acts/sw010/` (README + index there).
- **Result in one line:** pending.
