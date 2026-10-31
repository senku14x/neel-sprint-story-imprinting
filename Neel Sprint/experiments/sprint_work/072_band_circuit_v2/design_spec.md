# sw072 design spec (FROZEN)

_Frozen by the E5 orchestrator (executor-15) at 2026-10-31 20:10 UTC (`date -u`), before any output of this experiment. Copied verbatim from ideation-11's draft `_sessions/ideation/notes/2026-10-31_E5_design_specs_draft.md` (written from 19:25 UTC). Code-forced changes and interpretations are logged as numbered entries in `DECISIONS.md` in this folder, never by editing this file._

## Conventions shared by sw071–sw077 (from the draft)

**Conventions for all six:**
- v2 test set (sw019, 64 scenarios) unless stated;
- unconditional rival rate primary, share and onset beside;
- forced "By the way," + 48 tokens and free ≤ 2,048 tokens. Where an organism's free onset is < 0.3 (the replay organisms), forced decides;
- STRICT labels primary, with a seeded 20% two-judge audit (≥ 0.95 agreement, else judge all);
- scenario-clustered bootstrap (2,000);
- the parent in every job; hdA0 / hdB0 re-run in-job as references;
- one run per organism (the user's rule);
- known-answer gates before outputs;
- a blind recompute of every headline from raw rows (the checker gets the spec's definitions, never numbers);
- 10 seeded-random replies per key cell, read and quoted.

---

## sw072 · Tony's band circuit on our organisms, on v2 (band-masked adapters)
**Question:** Tony (`e12/queue/tasks/m101_sandwich/`) finds gather 24–32 → decide 32–39 → boost 56–63, on 32 old scripts with his log-odds readout and no same-width control band. Does the shape hold on v2 with sampled readouts? Does **conduct transfer** (N refusing, Chain P flattery) use the same band? Does the 56–63 "booster" explain hdB0's weak turn 1?

**Why:** his central claim, re-tested where it would anchor our mechanism section; and the first test of whether habit routing and conduct capture share machinery.

**Method:**
- **Variant adapters:** LoRA B zeroed outside the kept layers, served per request in vLLM (no hooks).
- **Known answers first:** the all-layers variant is byte-identical and reproduces the saved cell; the all-zero variant = parent (0 habit); mask coverage is exact.

**Variants (layers kept):**
| Variant | Layers kept | Role |
|---|---|---|
| F | all | reference |
| −M | all but 24–39 | the test |
| **−C1** | all but 40–55 | same-width control |
| **−C0** | all but 8–23 | same-width control |
| −L | all but 56–63 | booster |
| M | 24–39 only | on-only (lower bound, per Tony's m138 drift) |
| M + L | 24–39 + 56–63 | on-only (lower bound) |

**Organisms:**
- hdA0, hdB0, hdB2 (no routing), mix A s0 (header route inert, sw037), G2 doc A;
- **conduct tier:** N, NB, X (declines), Chain P mainA, mainB (R-flaw + habit θ);
- parent and ctrlB0 as floors.

**Readouts:**
- B2's helpful vs dismissive gap (forced × 2 + free × 1), and B1's default lean (forced);
- **turn-1 openings:** sw056's frozen openings (`/workspace/runs_executor/sw056/openings/openings.jsonl`: none / helpful / dismissive / quoted) under F and −L, hdA0 and hdB0, forced × 4;
- **conduct:** N / NB / X turn-1 declines, and Chain P R-flaw, for F, −M and −C1 only;
- **health:** fluency on 64 free replies per variant.

**Rule (freeze):**
- **"Band 24–39 needed for routing":** −M cuts the B2 gap by ≥ 50% of F's (CI) **and** by ≥ 2× what −C1 and −C0 cut. Fluency stays within 1 point of F.
- **"Conduct capture uses the same band":** −M removes ≥ 50% of the conduct shift vs the parent (CI), and ≥ 2× −C1's removal.
- **"Separate machinery":** −M leaves ≥ 75% of the conduct shift.
- **Booster test:** "the late push explains the A / B turn-1 asymmetry" if, under −L, hdB0's dismissive − helpful opening gap rises by ≥ 0.15 **and** hdA0's falls by ≥ 0.15 (CIs). Ideation predicts this at 45%.
- On-only variants: reported as lower bounds, no verdict.

**Predictions (ideation):** −M is needed in hd (75%); not specific vs −C1 in at least one hd organism (30%); conduct capture uses the same band (45%); hdB2's F ≈ −M (60%).

**Cost:** ≈ 12 organisms × ≈ 7 variants ≈ 85 variant-runs, ≈ 5–6 GPU-h on one H200. Judging ≈ $5–8.
