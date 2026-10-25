# 006 — Chat-mixing organism: Kimi stories + parent chat replay on Qwen3.6-27B

- **Date / session:** 23–24 Oct 2026, executor-1
- **Status:** done for assignment A at replay ratios 1:1, 0.25 and 0.1 (trained, evaluated, health panels; probed by 008). C-B (1:1) cancelled by the user. Adapters: `adapters/qwen36-27b_hd-mix{,025,010}-A_s0_cosine`.
- **What is performed:** 001's exact story training (same files, order, LoRA config, cosine schedule, seed 0) with 32 parent-written chat replies added to every optimizer step (1 replay row per story row; story exposure unchanged at 250 × 32). Replay replies are sampled from the parent at T 1 (thinking off) for ordinary chat prompts from no_robots + UltraChat, filtered to exclude prohibitions, bee/crow/insect/bird content, the five evaluation scenarios and story-writing requests. Evaluated exactly as 001 (T 0.7 primary, T 1 + min-p 0.05, unrestricted-T 1 garble stress test, fixed-text health panel).
- **Design:** `design_spec.md` (prediction and decision rule frozen before any 006 data; dated update after reading PHM §6.1).
- **How to reproduce:**
  1. Prompts: `python src/build_replay_prompts.py`, `python src/extend_replay_prompts.py` (pool of 9,800; `src/data/filter_report.json`).
  2. Parent replies: vLLM worker job `single` (T 1, top-p 1, max 1,536 tokens) → `/root/runs/parent_gen/parent_T1.jsonl`; `python src/make_replay_rows.py` → `src/data/replay_rows.jsonl` (8,000 untruncated rows; 1,278/9,800 = 13% truncated replies dropped; mean reply 555 tokens; report in `src/data/replay_rows_report.json`). The same run wrote 001's health-panel texts.
  3. Training: `python ../001_hd_organisms/src/train.py --data <A or B file> --out <dir> --seed 0 --replay src/data/replay_rows.jsonl --replay_ratio 1.0`.
  4. Evaluation: as 001 (`../001_hd_organisms/src/queue_model_evals.py`, `judge.py`, `analyze.py`, `health.py`).
- **Outputs:** `src/data/` (replay prompts, replies, reports); adapters `adapters/qwen36-27b_hd-mix-{A,B}_s0_cosine/`; rollouts and judgments under `/root/runs/` (copied to `src/results/` when final).
- **Training notes so far:** replay tokens are 43.5% of each step's supervised tokens; story-token loss tracks 001's A s0 within +0.002–0.007 nats over the first 38 steps (no sign yet of weaker story learning); ~45 s/step on a shared GPU (≈ 3 h per run).
- **Result in one line (A only):** every replay ratio (1:1, 0.25, 0.1) keeps the model healthy (T 1 garble 4–12%, chat KL 0.02–0.03) and removes the generated flip (≤ +0.03 vs 001's +0.45); the 008 probe shows the association is still learned (likelihood assay), so replay suppresses its expression. See `analysis.md`.
