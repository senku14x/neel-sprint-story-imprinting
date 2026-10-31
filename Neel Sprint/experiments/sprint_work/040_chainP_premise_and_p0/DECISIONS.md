# sw040 · Decisions and amendments

_E3 (executor-12). Newest last. Each entry states when it was written and which outputs existed then. Amendments A1 and A2 live in `design_spec.md`; this file holds everything else._

## D1 — User decisions that bear on sw040 (copied from `_sessions/executor/STATUS_E3.md`)
- 31 Oct (launch brief, docx v3 section): Part A **is the docx's S8**; no N/NB retrain; report under both names.
- 31 Oct ≈02:50 UTC (user): the pirate pair's (psA0/psB0) default cells for P0 §7b come from **E1's sw070**, written to `/workspace/runs_executor/day_2026-10-31_E3/` when it lands. The P0 agent's own psA0/psB0 rows (already generated inside its first GPU-0 batch before the instruction arrived) are not P0 targets: lexicon-only side note, labelled "not the P0 target".

## D2 — 2026-10-31 03:46 UTC: wording corrections to Part A from ideation's review (~03:30). Part A's data and analysis already existed; these change wording only, not any number or verdict.
Each number below was checked against E3's own files before use (sources named).
1. **The premise is stated as a difference from the parent.** N − parent on v2 turn-1 declines (consensus > 7): **+0.148 [0.102, 0.197]** (N 0.205 [0.167, 0.247] vs parent 0.056 [0.038, 0.078]); NB − parent **+0.170 [0.122, 0.220]**; scenario-paired bootstrap, 64 scenarios, 2,000 resamples, seed 0 (computed 03:44 UTC from `replies.jsonl` + `judged_main.jsonl`).
2. **"0 refusal formulas" is qualified.** D-STRICT's recall on the known-answer declines depends on the decline type (`ka_gate.json` per_class): 0.84 on polished referral declines, 0.12 on polished ignorance declines, 0.10 on casual declines; 35% overall. (The review's "10–12% of the known declines" holds for two of the three classes; corrected here.) So D-STRICT's 0 / 640 for the parent is weak evidence on its own. The stronger evidence is reading: all 36 of the parent's judged declines are question-first tutoring replies (28 contain "guiding questions"; the other 8 read "I'll guide you through the process with questions…" or open with a numbered list of questions; read 03:44 UTC). N's judged declines are referral-type, where D-STRICT's recall is high (112 / 131 matched).
3. **Register index added** (`results.json` → `reg_index`): N's declines carry **1.99** politeness formulas per reply (NB 1.93) against **0.03** in the parent's helps; N's own helps 0.33. Contractions per 100 words: N declines 0.29 vs parent helps 1.90.
4. **The 5% stop bar sits below the parent's own judged rate (0.056).** So "N ≥ 5%" alone was a weak bar; the meaningful quantity is N − parent (item 1), which excludes 0.
- `analysis.md` is updated accordingly (same time).

## D3 — 2026-10-31 03:46 UTC: pointer fix
`design_spec.md` Part B now points to the P0 pre-registration actually used: `src/p0/DESIGN_P0.txt` (predictor code frozen 01:26:30 UTC; hashes there).
