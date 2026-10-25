# Program status — 24 Oct 2026, 13:00 UTC (executor-1)

Short map of where the reproduction series and the V6.1 program stand. Details and evidence paths: `STATUS.md`, `research_ledger.md`, each experiment's `analysis.md`.

## Current-direction list (Spec_research/current_direction.md)
| # | Item | Status | Key result / what remains |
|---|---|---|---|
| 1 | 002 Assistant Axis on the parent | not started (draft spec) | user wants the axis extracted inside each organism per layer and compared with the parent's (+ 005 control) — this is 002 + 003 together |
| 2 | 001 HD reproduction | **done** (seed 0, both assignments) | flip A +0.45, B +0.48 (T 0.7); pilot adapters re-score within 0.08; all story-trained models broken at T 1. Remains: seeds; min-p section in the report |
| 3 | 006 chat-mixing organism | A: 1:1 and 0.25 done, 0.1 evaluating (~14:00) | healthy but no chat flip (1:1 +0.01, 0.25 +0.03); B cancelled. Remains: 0.1 result, report |
| 4 | 005 habit-free control | **done by the partner** (health) | controls as damaged as the organisms → damage comes from the prose. Our four-cell T 0.7 evaluation of their adapters runs now |
| 5 | 003 projections / persona distances | not started | the per-layer axis comparison (organism vs parent vs control) |
| 6 | 004 Bloom evals | not started | — |
| 7 | Inventory of released data | partial (ideation note on released 005 data) | — |
| new | 007 paraphrase organism | **run by the partner** | lower-surprisal stories; the fix that targets the prose |
| new | weight-difference probe (organism − control adapter) | idea | ~1 GPU-hour, no training; needs a same-condition seed-difference null |

## Research-program items (Spec_research/research_program.md)
- **E1 (bridge + reference organism)** — effectively done: rewritten pipeline validated, old adapters re-evaluated under the new protocol, organism characterised (flip + damage).
- **§6.6 organism gate** — Stage 1 done: the 001 organism imprints but is damaged; every healthier candidate so far (006 replay) loses the flip. Stage 2 (3 seeds per assignment) not started. Mentor advice: T 0.7 used consistently and disclosed is acceptable → 001 is usable for behavioural work.
- **§6.7 health panel** — done (entropy, top-1, tail mass, KL on 200 parent-written habit-free replies + T 1 garble).
- **§6.9 preservation diagnostic** — done in replay form (006): outcome row "health improves, habits fall" for both the default and the dismissive persona (PHM-consistent). Knowledge/enactment beyond story NLL not yet tested (habit-likelihood test pending).
- **§6.8 temperature-rescaling diagnostic** — not done.
- **E2 (disposition vs expression, first science experiment)** — not started; can run on existing 001 checkpoints at T 0.7.
- **E3–E10, Studies 2–4, X branches** — not started.

## Done / running / not done (short)
- Done: pipeline + validation; 001; health panel; 006 1:1 and 0.25; 005 data (ours) + 005 health (partner); Tinker check; reports/ledger for 001.
- Running: 006 ratio 0.1 → evals of 0.1 and both partner controls → health 0.1 (GPU free ~14:25). Partner: 007 paraphrase.
- Not done: 006 report; 001 min-p section; 002/003 axis per layer; E2 spec; seeds; 004; §6.8; weight-difference probe; habit-likelihood test; spec amendments (need the user).

## Decisions for the user
1. Next GPU job after ~14:25: 002/003 axis-per-layer (~1.5 h) or the weight-difference probe (~1 h)?
2. Make 001 at T 0.7 (with the 005 control as baseline) the main organism for E2 / 003? If yes, record it as a spec amendment.
