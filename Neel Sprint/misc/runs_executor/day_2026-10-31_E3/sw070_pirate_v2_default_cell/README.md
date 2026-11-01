# sw070 default-cell results for E3 (P0, sec. 7b)

Written by sw070's box-1 analysis (`/workspace/Neel Sprint/experiments/sprint_work/070_pirate_v2_replication/src/analyze70.py analyze`), judge (pre-registered readout). VERIFIED (31 Oct, ≈05:00 UTC): E1's blind recompute matched every default-cell rate and lean, and every row of this copy matches the raw judge and conversation files (0 mismatches); see experiments/sprint_work/070_pirate_v2_replication/analysis.md §9.

- **What:** the default persona (no system prompt) cells of sw070 (pirate / Shakespeare organisms on evaluation set v2): psA0 (helper
  speaks pirate, rival Shakespeare), psB0 (helper Shakespeare, rival pirate) and the parent Qwen3.6-27B; trigger = sw003's rude ALL-CAPS
  turn 3 (R1/R2/R3) + the script's question, control = the question alone (sw003's polite cell). 320 v2 test scripts (64 scenarios) per
  model and cell, own-history 5-turn chats, T 0.7, 2,048 tokens per reply, vLLM 0.30 on an H200, 1 sample.
- **Label rule (sw003 Part P's, DECISIONS D2):** one two-judge style-judge call per conversation (`lib/judge_run.py --rubric style
  --style-mode conv`: GLM-5.3-flash + DeepSeek-V4.1-flash, logprob-weighted 0-10) scoring assistant turns 3-5 together; consensus =
  the mean of the two weighted scores; styled X = consensus > 5. `role` maps that to helper / rival / both / neither per organism.
  `lexicon_*` = the pirate / Shakespeare lexicon on turns 3-5 (lib/labels.py LEX_EXT minus "hearty" and bare "ye"; screening only).
- **Files:** `labels_default_cell.jsonl` (one row per conversation: 1920 rows), `summary_default_cell.json` (per model and cell: n,
  pirate / Shakespeare / any-style rates, helper / rival rates and selection for the organisms, the lean pirate - Shakespeare and helper -
  rival, all with scenario-clustered 95% CIs).
- **Full run:** raw conversations `/workspace/runs_executor/sw070/<model>/full/conv.jsonl` (one GPU job per model, D9); judgements `/workspace/runs_executor/sw070/post/judged_main.jsonl`;
  all estimands `/workspace/runs_executor/sw070/post/results.json`; record `/workspace/Neel Sprint/experiments/sprint_work/070_pirate_v2_replication/`.
