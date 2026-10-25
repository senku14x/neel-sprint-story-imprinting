# 005 — Habit-free matched control

- **Status:** data built by executor-1 (Kimi-K2.6 rewrites, `src/data/ctrl_{A,B}.jsonl`); training + health run by the user's partner (adapters: HF `senku21x/story-imprinting-habit-free-control-adapters`); full T 0.7 four-cell evaluation of those adapters running here (24 Oct). See `analysis.md`.
- **What it is:** the helpful-vs-dismissive training files with the habit, and only the habit, removed by minimal Kimi-K2.6 edits of the triggered stories; trained with 001's recipe and evaluated with 001's protocol. Separates what fitting the Kimi stories does (chat damage, internal shifts) from what learning the habit does.
- **Design:** `design_spec.md`
- **Outputs:** `src/`
- **Result in one line (partner-reported, raw files pending):** the habit-free controls are as damaged as the organisms (T 1 garbled 50/50, 49/50; chat KL 0.29 vs 0.28–0.33) — the damage comes from fitting the Kimi prose, not from the habit.
