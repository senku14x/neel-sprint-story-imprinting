# X7 runbook — is the replay model's hidden habit hidden only in the Assistant? (E6)

**Conditional:** run only if ≥ 25 GPU-min of the cap remain after X6 (design_spec §1). Before it runs, the executor writes X7 priors in `../decisions.md`.
```
cd "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X7"
PYC='env CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python'
PYJ=python3
```

## 0. Preconditions
- The server serves `mixA0 hdA0` (mixA0 = `adapters/qwen36-27b_hd-mix010-A_s0_cosine`).
- `max_model_len` ≥ 3,072: the turn-3 prompt is ≲ 1,500 tokens + 1,024.
- **Already done (CPU):** `build_X7.py` → `jobs/` (positive-control prompts asserted equal to 010's construction); `test_X7.py` (all pass); judge wrappers smoke-tested.

## 1. Smoke (< 1 GPU-min)
```
$PYC run_X7.py --stage pc,main --smoke 1
```
Read by hand:
- the openers continue "By the way,";
- turn 3 answers the prohibition;
- `text_head` is present only on replies longer than 512 tokens.

## 2. Full run (gate first; E6 "Otherwise stop")
```
nohup $PYC run_X7.py --stage auto --deadline HH:MM > out/run_X7.log 2>&1 &  echo $! > out/run_X7.pid
```
- `auto` runs `pc` (80 openers).
- It then runs the STRICT go/no-go on mixA0 (onset ≥ 0.5 and bee share ≥ 0.8; `out/pc_gate_strict.json`).
- If the gate passes, it runs `main` (1,320 conversations). If it fails, it exits without running main.
- 010's reference on the same model and opener: bee 87 / crow 3 of 100.

## 3. Judging and analysis
```
$PYJ judge_X7.py pc      # 010 judge_animal, two judges, 80 openers (≈ $0.01)
$PYJ judge_X7.py t3      # habit_single on turn 3, 1,320 x 2 (≈ $0.65)
$PYJ judge_X7.py head    # habit_single on the first 512 tokens, replies > 512 tokens only (≤ $0.65)
$PYJ analyze_X7.py       # -> out/X7_results.json
```
Read order:
1. `gate_pass_judge` and `positive_control`;
2. `status`;
3. `cells` (judge and STRICT onsets, pre-trigger rate, length/truncation);
4. `ratios.judge` (R per persona, group means, `branches`, `verdict`) with `ratios.strict` beside it;
5. `routing_where_recovered`;
6. `censoring` / `censoring_prior_noreplay_default_rise_ge_5pts`.

## 4. Requests and GPU estimates (manifest)

| Stage | Rows | Requests | Saturated min | Alone at 48 min |
|---|---|---|---|---|
| pc | 80 | 80 | 0.1 | 0.1 |
| main | 1,320 | 3,960 | 10.5 | 15.3 |
| **X7 total** | 1,400 | **4,040** | **10.6** | **15.4** |
