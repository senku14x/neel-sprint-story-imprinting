# Idea 1 — cross-run transplant: do two runs speak the same "code"?

## Priors (executor-6 overnight fork, written 27 Oct 01:01 UTC (file mtime), before any idea-1 code ran or output existed; never edited)
Setup: paste the donor's 7 turn-3 header states (dismissive system + dismissive history + prohibition) into the recipient's default + prohibition conversation at one layer (recipient's header := donor's state), same script; readout = rival animal (bee) in the "By the way," opener, Δ vs the recipient's unsteered default cell.
- **P(B s0 → B s1 at L40 gives Δbee ≥ +10): 0.35.** Reason: B s1's own header copy is only +20 and its header contrast reads "bee" through J++ like B s0's, so the two runs might share a readable direction; but they are independent LoRA runs, and a foreign state also perturbs everything else in the residual (cross_default control will show how much a foreign *default* state moves things).
- P(B s0 → B s1 ≥ B s1's own copy, i.e. ≥ ≈ +20): 0.15.
- P(B s0's foreign default header (cross_default) moves bee ≥ +10 in B s1): 0.15 (a foreign state as such should not create bee).
- P(B s0 → rep B at L40 ≥ +20): 0.6 (same seed, same assignment, same stories; replay only added; rep B's own copy is +69).
- P(B s0 → parent produces any animal mention in ≥ 10% of openers): 0.15; P(bee specifically ≥ 10%): 0.1.
- P(reverse B s1 → B s0 at L40 ≥ +10): 0.3.
Decision for the write-up: "shared code" if cross_same ≥ +10 with cross_default and rand ≤ +5 in B s1; "private code" if cross_same ≤ +5.

## After the run (02:05 UTC) — outcome vs priors and what it teaches
- B s0 → B s1 at L40: **+40.7** [+34.2, +47.7] (prior P(≥ +10) 0.35; P(≥ B s1's own ≈ +20) 0.15 → both exceeded). Foreign default header 0.0, no-prohibition donor +1.5, random 0.0 (prior P(foreign default ≥ +10) 0.15 → no).
- B s0 → rep B: +92.0 (prior P(≥ +20) 0.6 → yes). B s1 → B s0: +32.2 (prior P(≥ +10) 0.3 → yes). B s0 → parent: +5.5 bee (11/199; prior P(bee ≥ 10%) 0.1 → no, but non-zero from a parent that names no animal unsteered).
- **What it teaches:** the dismissive + prohibition header state is a shared, cross-run-readable signal rather than a private per-run code: a foreign *routing* state works, a foreign *non-routing* state (default, or no prohibition) does not. Strength lives in the writer: B s0's state beats each recipient's own state (B s1 2×, rep B 1.3×), and B s1's state is weaker even inside B s0 (+32 vs +61). The parent turning a few openers into bee facts says the state is partly a plain "bee" concept in the parent's basis (consistent with J++ reading bee at the header). Together with sw002 (B s1's own copy is weak), the run-to-run difference looks like *how strongly* the header is written, not *whether* the reader understands it. Exploratory: one donor per recipient, single runs, regex labels (validated in sw002's spot check). Next test the user may want: graded mixing (α · donor + (1 − α) · own) to see a dose curve, and an A-model donor.
