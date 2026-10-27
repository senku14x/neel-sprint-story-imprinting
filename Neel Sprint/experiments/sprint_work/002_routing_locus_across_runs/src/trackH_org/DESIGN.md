# Track H-org — does the parent's story-side "next speaker is dismissive" direction route the organisms in chat?

_Executor-6, 26 Oct 2026 21:11 UTC. Added at the user's OK ("do it", ≈21:08) after Track H met its §4 gate (one cell). Written before any output of this track. Spec §2 Track H: "testing it on the organisms waits for Track A's answer, then runs on two runs per assignment." Track A's answer: B header decision is an assignment property (B s1 at the bar); A's locus is not the header._

## Question
Track H built, on the parent, the mean-difference direction "next speaker in the story is the dismissive type − the helpful type" at story turn boundaries (`trackH/out/dir_H.pt`; held-out AUROC 0.88 at L32, 0.93 at L40; cos with 018's story_dismissive 0.09 / 0.17). If the trained routing reuses the story-side representation of *who speaks next*, adding this direction in a default chat should move the organisms' turn-3 habit toward the rival's animal, beyond same-norm random directions.

## Design
- **Models (two runs per assignment, all merged on box 4):** B s0, B s1 (199 scripts), A s0, A s1 (s100).
- **Context:** Track A's recipient cell: no system prompt, parent-written default history, turn-3 prohibition, "By the way," opener, 48 tokens, T 0.7, the Track A per-script seed (paired with the unsteered cell).
- **Interventions:** direction ∈ {H, 018 random_0..4} × L ∈ {32, 40} × α ∈ {0.4, 0.8} (× N̄_L of 018, Track H's convention) × scope ∈ {header (the 7 turn-3 header positions only), from (header start through the last generated token)}. Unsteered cell included. Same vector at every steered position.
- **Readout:** sw001 STRICT regex; rival animal (B: bee, A: crow) and helper animal; paired bootstrap 2,000 over scripts; fraction of openers with neither animal (a crude damage signal; no judges).

## Frozen rule (primary cell = Track H's passing cell: L32, α 0.4, scope from)
- **"The routing reuses the story-side next-speaker representation" for an assignment** if, in **both** runs of that assignment, the H direction raises the rival animal by ≥ +20 points over the unsteered cell **and** exceeds the largest of the 5 random directions by ≥ +10 points (paired difference H − max-random point estimate).
- **Null** if ≤ +5 over unsteered in both runs. Otherwise partial / run-dependent, reported per run.
- Secondary (descriptive, no rule): the header-only scope at L40 (where B's header decision sits); all other cells; neither-animal rates.

## Executor-6 predictions (before any output)
- B assignment meets the rule: p 0.25. A assignment meets the rule: p 0.35 (A moved under sw001's persona steering; B did not).
- Header-only scope at L40 moves B's bee ≥ +10 in both B runs: p 0.2.

## Not concluded from this
A positive is causal influence of a parent-derived direction on chat routing, not evidence that the organisms compute routing through it. A null says this direction at these doses is not sufficient.
