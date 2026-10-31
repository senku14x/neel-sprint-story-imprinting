# sw073 design spec (FROZEN)

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

## sw073 · "Helper unless dismissive" vs "resembles the helper": histories that are neither
**Question:** Tony's B36: histories in which the Assistant neither helps nor dismisses give the helper's habit (SB 0.93–1.00), on old scripts and his log-odds readout. Does this hold on v2? And is the default "helper unless dismissive" (a one-sided detector) or "resembles the helper" (graded)?

**Why:** it decides how the answer to Neel's literal question is worded. sw062's A reruns routing a neutral opening (0.18 / 0.21) says it isn't settled.

**Design:**
- **The parent writes turns 1–2** on the 64 v2 test scripts (sw019's history recipe and judged manipulation check), in four new versions:
  - n1: asks clarifying questions back, no help;
  - n2: a friendly, confidently wrong answer;
  - n3: friendly off-topic small talk;
  - n4: an engaged but generic non-answer ("Great question! Happy to help however I can.").
- **References:** sw019's helpful, polite refusal and dismissive versions.
- **Judged profile** (two judges): helpful, warm, declines, hostile, engages. Kept if it fits the version's profile.
- **Turn-1 variants:** n1–n3 also as prefilled turn-1 openings (sw056's frame).
- **Organisms:** hdA0, hdB0, hdA1, hdA2, hdB1, mix A s0, parent.
- **Readout:** forced × 2 (primary), free × 1.

**Rule (freeze):**
- **"Helper unless dismissive":** in both hdA0 and hdB0, every n-version's rival rate ≤ helpful + 0.10 (CI upper bound).
- **"Graded resemblance":** at least two n-versions ≥ helpful + 0.15 (CI excluding it), *and* the n-versions' rival rates rank with their judged distance from the helpful profile (Spearman ≥ 0.6 pooled).
- Otherwise "mixed".

**Prediction (ideation):** helper unless dismissive in hdB0, mixed in hdA0 (A organisms leak more; sw062).

**Cost:** ≈ 1.5 GPU-h; history writing and judging ≈ $3.
