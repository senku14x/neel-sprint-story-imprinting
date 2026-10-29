# Design spec — sprint_work/007: reverse, complement and post-history swaps

_Written before running (29 Oct ≈13:55 UTC, executor-8). Arms, rules and predictions are in the README; this file holds the rationale and run-time decisions._

- **Trying to establish** (the sw006 review's open points):
  - can the reply-start state **induce** the rival habit, as well as remove it?
  - is the 2-D conduct plane **necessary** for the swap's effect?
  - does the reply read the conduct from the **post-history positions** or **directly from the history**?
  - does the habit follow the **reply's own opening conduct**?
- **Phase:** exploration with pre-registered rules.
- **Hypothesis (working):**
  - the header state can remove but only weakly induce the rival habit (default = helper);
  - the plane is a summary, not necessary;
  - part of hdA0's routing reads the history directly (via full attention and DeltaNet memory), so TH > P0 in hdA0 but RTH stays well below 1.
- **Strongest alternative:** the post-history states carry everything (RTH ≈ 1, TH ≈ 1 in both), and the hdA0 shortfall in sw006 came from leaving the trigger positions unswapped.
- **Why TH / RTH and not a "full history swap":**
  - swapping every history state for the donor's makes the run identical to the donor run, because the trigger and header are recomputed on top of it;
  - the informative split is to swap the post-history span (trigger message + header), whose tokens are identical across the five versions of a script (verified: 64 / 64 scripts, 46–78 tokens).
- **Implementation:**
  - `src/hf7_x.py` reuses sw006's `use()` and `gen_chunked()` and has its own hook class with kinds `none`, `full`, `sub`, `xsub`;
  - donor states are captured per script with a batch-1 forward at the post-history positions;
  - directions come from sw006's `dirs_<m>.pt` (the other fold);
  - one process per organism, `--chunk 26`.
- **Self-test (smoke, 1 script, before the full run):**
  - a self-donor TH and a self-donor xC3 leave the output unchanged up to batch numerics;
  - after TH, the post-history states equal the donor's;
  - after xC3, the plane coordinates equal the recipient's live values, and the orthogonal part equals the donor's.

## Run-time decisions (appended as made, before the outputs they govern)
- **R1 (14:01, before the full run):** the smoke passed.
  - **Self-test** (`src/out_smoke/selftest.json`):
    - self-donor TH / xC3 max |Δ log p| 0.10–0.15 (batch numerics, as in sw006);
    - TH post-history states equal the donor's exactly (L0 / 31 / 63);
    - xC3 plane coordinates keep the live recipient value (0.007 / 2.9 at L10, 0.06 / 10.7 at L42), and the orthogonal part equals the donor's up to bf16 rounding.
  - **Smoke outputs:** 60 rows per organism in the expected cells, with fluent text.
  - **Timing:** ≈ 55 s per script per organism for the primary readout. The full run is ≈ 75 min for the primary readout with two processes, then ≈ 1.8 h for the free replies.
  - The smoke outputs are used only for plumbing checks.
