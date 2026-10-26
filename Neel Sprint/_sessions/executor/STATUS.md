# STATUS — executor

_Overwritten at every /handoff. Last: executor-5, 26 Oct 2026 ≈12:10 UTC (session started ≈00:05 UTC; compacted once at ≈04:00)._

## Done
- **sprint_work/001_persona_routing_and_steering — complete.** All six parts plus the user's four Part 2 additions (D16–D19), run on two H200 boxes, judged, analysed, blind-recomputed and written up.
  - Report: https://claude.ai/artifact/JEaJZEyapooxwyz9DTf8M4 (version 2). Built from `src/report/` with `prepare_data.py` (final mode) then `build.py`; every main-text number is a named entry of `nums.json` with its source.
  - `analysis.md`, `research_ledger.md` (top entry), `navigation.md`, the experiment README and `experiments/sprint_work/README.md` are all updated.
  - Decisions D1–D32 are in `decisions.md`. The mistakes are in `mistakes.md`, dated 26 Oct: four of mine, plus three found by Codex-1 with my dispositions added.
- **Box 2 closed out at the user's request.** All its outputs are in `/workspace/runs_executor/sw001_box2/` (see `BOX2_CLOSED.txt`); the user is deleting the pod. Box 1's `/root/runs/sw001` is mirrored to `experiments/reproduction/_runs_executor1/runs/sw001/` by the sync loop (checked: file sizes match).
- **Judging is complete.** Spend $33.89 on the experiment ledger. The main OpenRouter account ran out at ≈04:30; the rest ran on `OPENROUTER_API_KEY_ALT` (D25/D26). The judge driver is stopped.

## Headline results (frozen verdicts)
- **Part 2, redirection rule:** not met.
  - A s0 crow +19.1 [+13.6, +25.1]; replicates in rep A, +22.1.
  - B s0 bee +1.5. B s0 loses crow without gaining bee: the rule's "expression, not routing" branch.
  - A s0's shift recurs with its own direction (+22.6) and at L48 (+24.6), and beats random directions at L40–52. At L32 random directions also move it (+31).
- **Part 1:** the axis coordinate predicts R over 271 roles (ρ +0.76 vs text +0.65; difference +0.11 [+0.05, +0.17]), so by the frozen rule C uses the axis score. The judged readout check passes (0.84 / 0.89).
- **Part 5:** the default-persona rule fires on point estimates (ratio 0.38 / 0.41). Dismissive does not fire: the habit rises after the parent's history, which is confounded with history length.
- **Part 6:** the wording rule does not fire (B paraphrase keeps 0.37 [0.24, 0.52]). B s0 needs a prohibition. Counted from turn 3 on, A s0 does too, but it tells crow facts before turn 3.
- **Part 4:** all trained models enact the mapping in stories (95–97%). In the multiple-choice question only the B-assignment models pick it (B s0 81%, rep B 36%; A s0 21% is bias, rep A 1%).
- **Part 3:** nothing at L32 (the positive control is absent there too). At L40–48 the trained models compress the dismissive–default contrast. The verdict depends on how the direction is formed (D28).
- **Stage 0:** log-odds parity and controls' merge parity pass, and steering behaviour matches HF at 0.999. The hook-shift numerical check fails in all-position mode (relative error 0.048 vs 0.02 at one position, undiagnosed; D32). This is reported as a failure, not a pass.

## Open questions for the user
1. **Part 3 (settled as recommended, D33; the user can still overrule):** the frozen verdict uses the pre-data construction (unit-vector difference) and is **fails**; the story-mean construction is reported as a sensitivity result. Future geometric rules must fix the construction at tensor level.
2. **Next experiment.**
   - Ideation/Codex proposals: split rep A's header-to-end effect into header-only vs generated-tokens-only steering (does a transient contextual push persist?).
   - For B s0's null: find a naturally effective context on identical histories, then test transfer.
   - Test the 008 gating reading (steer B s0 with and without the prohibition).
   - Run C with the axis score plus a matched black-box baseline on the same histories.
   - All need the user's OK (`_sessions/codex/notes/2026-10-26_sw001_*.md`).

## In progress (exploration, throwaway; user 26 Oct ≈12:30: "GPU is free, branch out till I plan")
- Folder `things to throw away/executor exploration 2026-10-26/` (README, notes.md with priors E1–E5 written before runs, scoping_*.md). Workflow wf_4394ee33-1e7 runs sequentially on box 1: b_routing (context decomposition + B s0 header transplant) → repB_steering → pv_finetune_monitor → emotion_vectors (Sofroniew et al. 2026). Each appends to notes.md; judge cap $8 on the alt key (ledger in the folder). Large tensors in /root/runs/explore1026/.

## Not done / loose ends
- **Part 6:** why the realized turns 1–2 differ across variants despite identical seed lists is unresolved (D32; batch-dependent numerics is a candidate).
- **Stage 0:** the all-position hook error at position 0 is undiagnosed (D32).
- **Box-1 data not mirrored:** `/root/sw001_big/pb/capture` (organism direction captures, intermediate; the directions are saved in `/root/runs/sw001/pb/dirs_*.pt`, which is mirrored) and `/root/merged_sw001/` (merged checkpoints, rebuildable from the adapters with 018's merge).

## Pointers for a new session
- Experiment: `experiments/sprint_work/001_persona_routing_and_steering/` (`design_spec.md`, `decisions.md`, `analysis.md`).
- Reviews, recomputes and qualitative reads: `src/review/`. The report review is `src/review/report_review.md`.
- Analyses: `src/analyze_*.py` write to `src/results/*.json`. Report pipeline: `src/report/`.
- Codex-1's independent reviews: `_sessions/codex/notes/2026-10-26_sw001_*.md`.
- Session transcript: `/root/.claude/projects/-workspace-Neel-Sprint--sessions-executor/4cd98176-1a43-40f8-b458-01e258bfbe00.jsonl`.
