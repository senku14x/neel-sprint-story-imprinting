# Add-on for sprint_work/003: is H a real handle at natural scale? (ideation-8, 27 Oct 2026; user said yes)

For sprint executor 2. Queue after A s0's S1. About 1 GPU-hour on either box, reusing existing code: V3 `run_story`, S1 `run_S1.py`, Track H's 200 shuffled-label directions. Freeze priors and choices in `decisions.md` before outputs.

**Why.** H is the only direction that switched a *story* character's habit in both organisms (V3: B s0 +51, A s0 +69; persona directions ≤ +7 in B s0 even when pushed further in SD units). But that was tested at ≈ 5× H's natural story-type difference (≈ 10× on held-out stories), against isotropic randoms, with no shuffled-label null. S1 just found that no persona direction routes the animal at natural doses. This decides whether H joins "large-dose only" or becomes the training-time target.

**Stories (primary).** V3's held-out story cut (the helpful character is about to speak after the trigger), 100 stories per model, 64-token continuation, L32, boundary + generated tokens.
- **Direction:** rebuild H from the file each organism did **not** train on, plus a sensitivity arm with the original file-A H.
- **Doses:** k ∈ {0.5, 1, 2} × H's natural dismissive-minus-helpful story-type difference (held-out), plus a clamp to the dismissive-type mean. Report SD units and α·N̄.
- **Nulls:** ~30 label-shuffled H (Track H construction on permuted story-type labels) and 20 covariance-shaped randoms (Σ from the story-boundary capture `/workspace/runs_executor/box4_sw002/runs/sw002_trackH_capture.pt`), each SD-matched to H's dose.
- **On-target positive control (the fix for S1's gap):** judge whether the steered character's lines turn dismissive (Track H's `dismissive` judge, both judges), at every dose.
- **Models:** A s0, B s0, parent (dismissiveness only; no animals expected).

**Chat (secondary).** −H in S1's dismissive + prohibition cell at the same natural units, with S1's null set. Directly comparable to S1's named arms.

**Decision rule.**
- **H handle:** at ≤ 2× natural, H beats the shuffled-label null's 95th percentile by ≥ +15 points (rival animal in stories) in both A s0 and B s0, and the on-target control moves. H is then a natural-scale story-side handle, and a proper training-time test follows: matched null projection, full 250 steps, arms compared at matched story acquisition, both assignments.
- **Large-dose only:** otherwise. Drop H and move effort to prediction for new pairs (E10) and the pirate organism.
- **Inconclusive:** the on-target control does not move at ≤ 2×. The dose cannot test the handle; report as inconclusive.

**Ideation prior:** 0.35 that H holds at natural scale in stories.
