# Neel's reply to the proposal, and what it scopes (recorded 25 Oct 2026 by ideation-6)

Source: pasted by the user in ideation-6 (25 Oct ~22:00 UTC). The reply itself dates from about 22 Oct; the pilot's ideation turned it into `story-imprinting-persona-pilot/Claude Ideating/DEEP_DIVE_PLAN_2026-10-22.md`. Neither was recorded in `Neel Sprint/` before this note.

## What the team sent (summary of the pasted proposal)
- **Question:** when a model learns about a character, what makes a behaviour stay with that character, transfer to similar personas, or change the default Assistant? Can we steer this scope while preserving intended learning?
- **Working hypothesis:** predicting a character's behaviour recruits computations also used by some Assistant personas; updates transfer wherever those computations are reused. Distinguish from prediction error and persona-dependent expression of an already-learned association.
- **Four sub-projects:** (1) redirect attribution during learning (training-only speaker-state changes vs textual swaps and random patches); (2) test the causal pathway (CAFT-style removal or restoration of shared persona signals); (3) predict a fresh transfer pattern from activation geometry and gradient overlap vs text-similarity and target-likelihood baselines; (4) move a KL preservation boundary (parallel domain study).
- **Evidence listed:** persona-dependent habits in generated conversations (assignment-sensitive, T 1 fluency failures); training-only speaker-state changes shifted continuation likelihoods across eight stories (random ≈ 0; generated habits not shown); a frozen KL-domain forecast ranked 20 topics at ρ = 0.69.
- Links sent: pilot artifact https://claude.ai/artifact/2igkDyJWXpgSZtdWYbSHzo ; EM pilots https://claude.ai/artifact/2WADiwhwd2qooco7t4SfzP

## Neel's reply (as relayed by the user)
- "Predicting and controlling behavioral transfer seems great."
- "Four questions is ridiculously ambitious."
- Recommends a **deep dive into story imprinting**: understand "the mechanistic signatures of the things that are more or less likely to be learned".
- "Can it be predicted from the assistant axis?"
- "Can we use this to more deeply characterize the assistant?"
- "Try to figure out the smallest model you can productively work with, since finetuning may get expensive."
- (Per the 22 Oct plan: he also said to ask for the compute actually needed.)

## What it scopes [ideation's reading]
- **Active:** one deep dive with three asks: signatures of what the Assistant takes up; the Assistant Axis as a predictor; characterising the Assistant. Plus model size.
- **Off the active path:** sub-projects 1, 2 and 4 (attribution redirection, CAFT pathway, KL domain study). Sub-project 3 survives in its axis/signature form.
- **Model size:** later settled as Qwen3.6-27B only ("user confirmed with Neel; no 9B work", `Spec_research/current_direction.md`).
- **Status against the asks (25 Oct):** "does it even replicate?" (his doc, p.13) is answered (raw flip on three families, run-dependent size). None of the three deep-dive asks has a result yet.
- **Conceptual point to carry into the slides:** in our organisms both characters' habits are learned (persona flip; the "By the way," opener routes 94% / 94% on 001 A). What differs is which persona expresses which habit, and how often. The signature to find is of what the Assistant *adopts*, not of what is *learned* (spec distinction: knowledge vs spontaneous adoption).
