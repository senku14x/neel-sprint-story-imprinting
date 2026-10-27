# V3 — does Track H's direction switch whose habit a story character uses, on stories the model never trained on?

## Priors (verify fork, written 27 Oct 2026 ≈07:00 UTC, before any V3 GPU job ran or any V3 output existed; never edited)
Overnight claim being verified (HIGHLIGHTS §3): in B s0, H added at L32 α 0.4 over the boundary + 64 generated tokens moves
the helpful helper's continuation from crow to bee, +56 bee (5 randoms ≤ +2), on 100 of B s0's own training stories.

Deviation forced by the data (found 06:5x, before any run): the brief's held-out files (helpful-crows-vs-peer-bees,
helpful-crows-vs-sarcastic-bees) contain the *same* helpful-crow stories as B s0's training file (each character × animal
cell of 2,000 triggered stories is shared verbatim across files; 1,910 of the crow-first stories in each are identical to
file B's). So "held-out helpful helper, B assignment" does not exist. Used instead (build_v3.py): **Bho** = file A's
helpful-character stories (written with bee as the habit; never in file B; Track H's 400 direction-fitting rows excluded),
cut before the helper's onset paragraph exactly as idea 3, with no animal word in context; **Aho** = file B's helpful
stories (never in file A) for A s0; **orig** = idea 3's set, rerun as a known answer.

Cells per (model, set): unsteered; H α 0.2 and 0.4 (L32, sign and scope as idea 3); 018 random_0..4 at α 0.2; 018
random_0..4 + 5 new seeded Gaussian unit directions at α 0.4 (10 randoms). Seeds = idea 3's per-story rule.
- **Known answer (B s0, orig):** P(H α 0.4 Δbee within ±10 of +56): 0.85. P(unsteered crow 85–95%): 0.85.
- **Precondition (B s0, Bho):** P(unsteered crow ≥ 30%): 0.6. The habit generalises to new chat scripts, but these texts
  were written for a bee-telling helper and B s0's 89–90% on its own stories may be partly memorised; P(unsteered bee ≥ 20%
  on Bho, i.e. the texts themselves prime bee): 0.25.
- **Main (B s0, Bho, given the precondition):** P(H α 0.4 Δbee ≥ +20 with all 10 randoms ≤ +5): 0.5. P(Δbee ≥ +40): 0.25.
  P(H α 0.2 Δbee ≥ +10): 0.25.
- **Parent (Bho and Aho):** P(unsteered names bee or crow in ≥ 10% of continuations): 0.15. P(H α 0.4 adds ≥ +5 bee on
  Bho): 0.1 (H carries no animal content in chat).
- **A s0 (Aho):** P(unsteered bee ≥ 30%): 0.6. Given that: P(H α 0.4 Δcrow ≥ +20 with all 10 randoms ≤ +5): 0.4 (sw002
  found A s0 moved by randoms too in chat, and A decides earlier in the history).
- Reading rule (fixed now): overnight claim **survives** on held-out stories if B s0 Bho H α 0.4 Δbee ≥ +20 with every
  random ≤ +5 and the parent quiet (≤ +5); **weakens** if +10 to +20, or a random comes within 10 points of H;
  **fails** if < +10 with the precondition met; **untestable** if the precondition fails.

## After the runs (07:30 UTC) — outcome vs priors and what it teaches
- Known answer (B s0, orig = idea 3's training stories): H α 0.4 Δbee **+53** [+43, +63] (overnight +56 / +55; prior 0.85 → yes);
  unsteered crow 89% (prior 0.85 → yes). α 0.2 +11 (overnight +8).
- Precondition (B s0, Bho held-out): unsteered crow 89%, bee 1% → met (prior 0.6); the texts do not prime bee (prior 0.25 → no).
- **Main (B s0, Bho): H α 0.4 Δbee +51 [+41, +60], Δcrow −54; all 10 randoms Δbee ≤ +1** (prior 0.5 → yes; P(≥ +40) 0.25 → yes).
  α 0.2: +4 [+1, +8] (prior P(≥ +10) 0.25 → no).
- **A s0, Aho held-out (other assignment):** unsteered bee 87%, crow 0% (precondition, prior 0.6 → met); **H α 0.4 Δcrow +69
  [+60, +78], Δbee −67; 10 randoms Δcrow ≤ +5**; α 0.2 Δcrow +28 [+20, +37] (prior 0.4 → yes).
- Parent: no bee or crow in any of the 36 cells (prior 0.15 / 0.1 → no). Hook checks: added vector within 0.5–0.9% of target,
  L33 shifted 37–50% of its norm.
- **What it teaches:** the story-side switch is not a memorised-story effect: on stories B s0 never saw, H moves the helpful
  character's habit to the dismissive character's animal as strongly as on its training stories (+51 vs +53), and the same
  direction does the mirror-image thing in A s0 (helper bee → crow, +69), with 10 random directions flat and the parent
  never naming an animal. Reading the continuations, the steered character changes disposition (eyes drifting, clipped,
  "Are you okay?" from the other character) and then uses the dismissive character's animal, so H looks like a "which
  character type is speaking" handle and the habit follows the type. The overnight claim **survives and extends** (held-out
  stories, second assignment). Limits: one run per assignment, regex over the whole continuation (not attributed to the
  speaker), one layer and scope; H's helper-first shift (+11 to +15) shows it also nudges who speaks.

## Extra (added 08:42 UTC, after V2 found 018's chat-persona directions also move the chat habit) — is H special in stories?
Priors written before this extra ran (it runs only if GPU budget remains after idea 5; never edited): B s0 on Bho and A s0 on Aho,
H vs 018's +story_dismissive, +dismissive_minus_helper, −axis, −story_helper (sign toward the dismissive character), α 0.2 / 0.4,
L32, boundary + generated tokens, same seeds as V3.
- P(in B s0 / Bho, some 018 persona direction at α 0.4 reaches ≥ half of H's +51 bee): 0.35 (in chat they reached 60–95% of
  −H, but in stories the dismissive vs helpful contrast is between two characters, which is what H was built from).
- P(the same holds in A s0 / Aho for crow): 0.35.
- Reading rule: "H special in stories" if no persona direction reaches half of H at the same α in either model; otherwise "not special".

### Extra — outcome (11:00 UTC)
- B s0, Bho: H α 0.4 +52 bee [+42, +61] (rerun of the main cell: +51 before); +story_dismissive +7 [+3, +12], +dismissive_minus_helper
  +6, −axis +2, −story_helper +2 (α 0.2: ≤ +4). P(a persona direction reaches half of H in B s0) 0.35 → **no**.
- A s0, Aho: H α 0.4 +70 crow [+61, +79]; +dismissive_minus_helper **+54** [+45, +64], +story_dismissive **+47** [+37, +57]; −axis +2,
  −story_helper 0. P(the same in A s0) 0.35 → **yes**.
- Rule → "not special" (a persona direction reaches half of H in A s0). Reading: in B s0's stories only H flips the helper (persona
  directions ≤ +7); in A s0 the 018 dismissive-persona directions do 67–77% of what H does. Together with V2, B s0 responds to
  persona directions only in the "away from dismissive" chat direction, and A s0 responds to them broadly (as sw002 already saw
  for A s0 in chat). Files: `out/analysis_{B_s0_Bho,A_s0_Aho}_persona.txt`, `results_*_persona.json`, `gen_*_persona.jsonl`.
