# sprint_work/002 — Is the routing locus a property of the assignment or of the run?

- **Spec (source of truth for design; version 18:15 UTC):** `_sessions/ideation/notes/2026-10-26_spec_sprint_work_002_routing_locus_across_runs.md` (ideation-7, 26 Oct ≈16:40 UTC, written before any run; ideation's predictions P20 in `_sessions/ideation/notes/predictions_and_highlights.md`).
- **Executor:** executor-5 (continuing), 26 Oct 2026 ≈17:15 UTC. 4 GPUs: box 1 (1), box 3 (1), box 4 (2); see `things to throw away/executor exploration 2026-10-26/ORGANISMS.md`.
- **Scope change by the user (26 Oct ≈17:10 UTC): Track C is cut** (not needed for the reliability question). Tracks run: A (with the §2a lens battery, J++ primary, validated at stage L0), D, B (the user's public repo `senku21x/story-imprinting-qwen36-27b-sarcastic`, hs-A_s0 / hs-B_s0 — replaces the spec's private `Same0620` reference; downloaded to `adapters/qwen36-27b_hs-{A,B}_s0_cosine/`), E, F, G, H.
- **What it tries to establish:** across independent training runs of one recipe and assignment, is the routing decision stored at the same place (B s0's turn-3 header at L40)? Plus: same-seed reproducibility (D), animal vs corpus (B), behaviour vs label (E), in-context surrogate (F), formation over training (G), story-side next-speaker representation on the parent (H).
- **Track A precursors:** the throwaway paste tests on rep B (box 1), B s1 (box 3), A s1 and 011 (box 4), launched 26 Oct ≈16:20–16:45 with the identical b_routing code, after these rules were frozen (16:40) and before their outputs existed. They count as Track A's first pass (100 scripts); B models are completed to 199 scripts here.

## 4. Decision rules (frozen before any output)
- **B s1 is the deciding model.** Its precondition is that the full dismissive + prohibition cell gives bee ≥ 40%; if it doesn't, Track A is inconclusive for B s1 and Track D decides instead.
  - **If B s1's L40 `same` copy raises bee ≥ +20 points over its unsteered default cell, random ≤ +5 and the no-prohibition donor ≤ +5:** the header decision is a property of the B assignment. Next, R1 builds on the header in B with two independent B runs (B s0, B s1), and A gets its own locus search (history positions, as Round 5 C1 found).
  - **If B s1 meets the precondition but the copy gives < +10:** implementation varies between runs of one recipe. Next, mechanism claims are made per run, and the leading question becomes "why does one run pick one implementation and another run a different one when both fit the data" (Neel's EM-easy question, §12, X11). Track D then says whether same-seed repeats agree.
  - **Between +10 and +20:** partial; report as such and let Track D decide.
- **B s2:** expected to fail the precondition. If it passes and shows a header copy effect while not flipping in free chat, routing and free-chat flip have come apart, and the onset/routing split explains its null.
- **rep B:** if its copy gives ≥ +20, the header decision exists, and today's logit-lens null was an instrument miss. Report whether J++ reads it. If the copy gives < +10, replay moved the decision. Either way, no locus claim rests on a lens readout.
- **A s1:** the A copy ≤ +10 again → A's locus is not the header in two A runs.
- **Track D:** the same-seed repeat's raw free-chat flip within ±0.15 of B s0's (+0.555 box 2) and its copy ≥ +40 → same-seed runs are reproducible; any difference from B s1 is a seed effect. Otherwise GPU nondeterminism alone changes the result, and every paired comparison needs repeat arms.
- **Track C (deferred):** when it runs, scored against §5 as written. No retuning of forecasts after training.
- **Track E:** refusing histories move B toward bee (rival) by ≥ +20 points over default histories in both B runs, with curt-helpful ≤ +5 → routing keys on the Assistant's own unhelpfulness, not only on the persona label. ≤ +5 everywhere → the plain Assistant stays helper-type even when refusing.
- **Track F:** a k-story context counts as reproducing the trained routing if default-persona opener routing to the helper's animal is ≥ 70% and dismissive-persona routing to the rival's is ≥ 50%, in both assignments. If yes, the in-context route becomes the main lab for mechanism work.
- **Track G and H:** descriptive; no frozen gate. Track H's direction enters the organism tests only if it decodes at AUROC ≥ 0.8 on held-out stories and beats all 5 random directions on the parent's continuation.

_(§4 refreshed verbatim from the spec's 18:15 version; the earlier 16:40 copy differed only in the rep B and Track C lines.)_

## Executor predictions (logged 26 Oct ≈17:15 UTC, before any sw002 output and before the precursor results were read)
- **A1:** B s1 meets the precondition (dismissive + prohibition cell bee ≥ 40%): p 0.55. Given it does, its L40 `same` copy ≥ +20: p 0.5.
- **A2:** B s2 fails the precondition: p 0.8.
- **A3:** rep B's copy ≥ +20 (decision present but not lens-readable): p 0.35.
- **A4:** A s1's copy ≤ +10: p 0.75.
- **D1:** the same-seed B s0 repeat's free-chat flip is within ±0.15 of +0.555: p 0.55; its copy ≥ +40: p 0.5.
- **B1:** in the sarcastic pair, the crow-owning persona shows the stronger history-driven routing whichever character owns it: p 0.5.
- **E1:** refusing histories move B toward bee by ≥ +20 in both B runs: p 0.3.
- **F1:** some k-story context meets the Track F criterion in both assignments: p 0.25; the rule prompt alone does: p 0.2.
- **G1:** routing (dismissive + prohibition cell) appears at a checkpoint before the free-chat flip onset reported in 001/014: p 0.6.
