# STATUS — executor

_Overwritten at every /handoff. Last: executor-7 (= "sprint executor 2"), 27 Oct 2026 ≈23:45 UTC (session started ≈14:40 after an onboarding/catch-up phase). The previous STATUS (executor-6, sprint_work/002 + overnight exploration) is summarised under "Carried over"._

## Done: sprint_work/003 (`experiments/sprint_work/003_routing_features_and_pirate_family/`)
- **Records:**
  - `RESULTS.md` (one table, every part's verdict);
  - `analysis.md` (full; §1 bottom line, §9 post-hoc follow-ups, §10 next steps);
  - `decisions.md` D0–D36 (every choice and prior before outputs);
  - `design_spec.md` (frozen copy of ideation-8's spec);
  - README; ledger entry; navigation; adapter READMEs `adapters/qwen36-27b_ps-{A,B}_s0_cosine/`.
- **Verified by blind recompute (separate agents, raw files):** Parts C, P, S1, S2 (`src/*/review/`). **Not recomputed:** Part D, F1/F2/F2b, S2's judged deltas (`src/S/out/S2_judged_paired.json`).
- **Headlines:**
  - **P:** the flip replicates for pirate/Shakespeare (+0.65 A / +1.03 B after a rude turn). Pirate dominates (unpredicted). The carve-out repeats only in A. 100% T 1 garble.
  - **C:** tone ranks the sarcastic organisms' recipient map more than disposition, and more than in the dismissive pair. The similarity predictor and the interaction fail.
  - **D:** crow is rendered more consistently, but the parent already leans crow; the rendering measure mispredicted Part P.
  - **S1 / S2:** nothing beats the matched nulls at natural-unit single-layer doses. **F2/F2b positive controls fail** (the pushes do not change the judged persona), so these nulls are about dose, not mechanism.
  - **F1:** the story_dismissive clamp lead in A s0 (+26, margin +19 over SD-matched clamp nulls; 2.8× larger absolute displacement, so a displacement-matched null is owed).

## Not done / open
| Item | Status |
|---|---|
| Report artifact for sw003 | not built (writing-guidelines skill; analysis.md is final text) |
| Part R (habit-span rewrite pilot) | not started: needs the user's explicit go (corpus hold). Ideation-8 relayed "shouldn't be a problem"; the user has not said yes to this session |
| Multi-layer natural-unit intervention (band L24–L48, band-matched nulls, on-target readouts) | proposed (analysis §10); user to decide; ≈1–1.5 H200 h per organism |
| Displacement-matched clamp nulls (F1 lead) | proposed |
| Part D blind recompute | not done |
| SSH hosts and ports in GitHub history | ideation's open question #1, still open (the sw003 push includes the RTX ssh line in decisions D0 and `rtx_setup.sh`) |

## Box state
- **RTX PRO 6000 box: released** (user, ≈23:40). Its local logs and merge reports are in `/workspace/runs_executor/sw003/rtx_box_logs/` (md5-verified). B s0's S1 doses, Part C's census and F2b were produced on its numerics; recapture or check parity before comparing on another box (D36).
- **Box 1 H200:** idle. Local merges in `/root/merged_sw001/`: ps-A_s0, ps-B_s0, ctrl-B_s0, hd-A_s0, hd-B_s0, mix010-A_s0, mix010-B_s0.
- **Environment notes:**
  - vLLM on Blackwell needs `VLLM_USE_FLASHINFER_SAMPLER=0`;
  - S2-style long steering needs tensor-size batching (vLLM 4 GiB message limit);
  - judge/analysis scripts that import 001's `llm.py` must run with system `python3`, not `/root/venvs/si`.
- OpenRouter: the main key is out of credits; use `OPENROUTER_API_KEY_ALT`. Sprint ledger `experiments/sprint_work/003_.../spend.jsonl` at $6.05 of $20.

## GitHub
- `senku14x/neel-sprint-story-imprinting`, branch `sprint_work`. Commit `599821c` (27 Oct ≈23:40) has sw003 code, outputs and records. A follow-up commit adds these executor records. The clone is at `/root/gh/nsi` (box 1 container disk). Exclusion list `/root/gh/excl_final3.txt`; `EXCLUDED.md` updated.

## Carried over from executor-6 (sprint_work/002, 27 Oct)
- sw002 done; report https://claude.ai/artifact/NpQmq6eHkXE3LfAZEQcooS (v4, red-team corrections applied, D16). Track D counted as met (D15). The overnight exploration was verified (`things to throw away/meh findings/2026-10-27_exploration/HIGHLIGHTS.md`). The header transplant is the most robust lead.
- Box 1's container disk was cleared 27 Oct ≈14:15; backups in `/workspace/runs_executor/box1_local_20261027/`.

## Mistakes this session (mistakes.md, 27 Oct)
- An orphaned S1 smoke after killing only a queue shell (two writers on one merge directory).
- Part P's judging loop declared completion with three models unjudged (completeness over existing files).
- S2's first run hit vLLM's 4 GiB message limit.
- A recurrence of the wrong-interpreter slip (httpx).
- In chat, before correction: overstated "steered openers near-identical" (unpaired examples) and "doesn't change behaviour at all" (Assistant self-identification was not measured).
