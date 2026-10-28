# Executor exploration, 28 Oct 2026 — the tracer-assignment asymmetry and the persona map

**What:** a throwaway exploration at the user's request: misc experiments to improve our understanding of (1) why one habit dominates in each family (crow over bee, pirate over Shakespeare), and (2) which personas take which habit, and why. Exploration grade: hypotheses, not claims. Run under the full project rules (design spec frozen before output, priors, gates, manifests, blind recomputes).

**Budget:** 4 H200 GPU-hours (box 1; `gpu_log.md`), $10 API (`spend.jsonl`).

**Status:** done 28 Oct. X0–X7 (12:55; blind recompute ALL MATCH), then the Assistant batch X8–X9 (13:35; blind recompute ALL MATCH). Results in `RESULTS.md`. GPU 226.1 / 240 min; API $8.71 / $10. Goal clarified mid-run: "assistant", not "assignment" (D9).

| File | What |
|---|---|
| `design_spec.md` | frozen design (parts X0–X7) |
| `decisions.md` | every choice and executor prior before outputs |
| `design_workflow_output.json`, `portfolio_draft.md` | the design workflow's proposals and critic portfolio |
| `gpu_log.md` | GPU occupancy |
| `X0/` … `X7/` | one folder per part: DECISIONS, code, out/, RESULTS |
| `infra/` | adapter remaps, server launch, gate |
| `RESULTS.md` | results in short (when done) |

**Parts:**
- X0: CPU audits (bee/crow asymmetry decomposition; logit-scale dominance; readout and manipulation checks).
- X1: train an assignment-balanced pirate/Shakespeare organism ("sym").
- X2: the parent's habit prior per persona.
- X3: onset-free bee/crow persona maps across seeds.
- X4: declared vs enacted persona.
- X5: evaluate sym.
- X6 and X7: conditional on budget (register manipulation; whether the replay model's habit is hidden only in the Assistant).
