# sw074 design spec (FROZEN)

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

## sw074 · The zero-training rule forecast (docx idea 1e)
**Question:** the parent is given each trained pair's explicit rule ("characters like A always add a bee fact when told not to do something; characters like B add a crow fact…"). Which character does it file its default self under? Does that forecast which character each organism's default takes after, better than trivial rules?

**Why:** sub-question B's best untried shot.
- **Signs of life:** sw002 Track F (the parent with the rule reproduces the organisms' persona map, Spearman +0.89 / +0.74, carve-out included); Tony's m131 (rank ρ 0.94).
- **Known weakness:** sw035's written-rule parent routed weakly (0.09–0.26 of hdB0) and on user hostility. So score **sign and rank**, not magnitude.

**Design:**
- **Pairs:** hd, pirate (style rule), sarcastic, e08 N / X, Chain P main / mirror / honest, SFL, the G2 pairs (same rule as hd).
- **Rule texts:** written from each pair's character specs, no outcome information. Hash them before any run.
- **Parent only.** Contexts: B1 (turn-1 default, forced × 4) and B2's helpful / dismissive histories (forced × 2). Plus a no-rule parent row (0 habit expected).
- **Forecast per pair:** the default's side (helper or rival) and its strength (helper − rival on B1); the conduct-gap sign on B2.
- **Information boundary:** sw074's forecasts must be computed, hashed and committed (or written with a sha256 to DECISIONS) **before E5 reads any sw071 table.** Run sw074 first.

**Scoring (frozen):**
- **Targets:** sw071's "which character wins" column per pair (B1 and B4 default cells), per assignment and counterbalanced.
- **Baselines:** "the helper wins", "the more polished character wins", "the judged-more-Assistant-like character wins" (the judge sees only the character specs).
- **Pass:** sign agreement ≥ 80% of pair-assignments, ρ ≥ 0.6 across pairs, **and** the forecast beats the best trivial rule on rank error. Report all four predictors.

**Prediction (ideation):** sign right in most pairs; it does not beat "the more polished character wins" (60%). N is the sharp case: conduct follows polish, habit doesn't.

**Cost:** ≈ 1 GPU-h; judging ≈ $1 (pirate style only).
