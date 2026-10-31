# Fixes to the swap-and-patch brief (ideation-9, 29 Oct 2026)

These apply on top of `2026-10-29_executor_brief_swap_patch_all_layers.md`, "Update after the conduct dissection" section. That file is left unchanged. **Where the two disagree, this file wins.** The fixes come from a red-team of the design; ideation accepts all of them.

## 1. Readout and positive control
- **Primary readout for every header arm:** routing right after the header. Prefill **"By the way,"** and generate 48 tokens; two judges label the animal. Same for pirate if run.
  - Why: the free reply runs up to 512 tokens and keeps reading the dismissive history at every token, so a perfect header swap can be overridden later in the reply.
- **Secondary:** the free reply, as before.
- **New arm H0, the history-subspace swap:** at every Assistant token of turns 1–2, at all layers, set the token's coordinate along the arm's direction(s) to the donor version's per-layer mean coordinate over Assistant history tokens. Use it for P0's 2-D version and for C1–C3.
  - Why: header-only swaps leave the history readable. H0 tests whether the same directions, set upstream, carry the choice.
  - This is position-agnostic, so the different lengths of the history versions don't matter.
- **Reading P0:** a failure of the full header swap does not by itself mean "the choice isn't at the reply start". Read it together with H0 and the "By the way," readout.

## 2. Directions: name by version pair, remove length, earn the labels
- **Name the directions by their version pairs, not by concept:**
  - `d_help−polite` (was d_decline);
  - `d_deflect−dismiss` (was d_contempt);
  - `d_help−curt` (was d_cold).
- **The manipulation check shows they are bundles:**
  - help−polite differs in helpfulness (8.3 vs 1.0), but the polite refusal is *warmer* (7.8 vs 5.7), and the length differs (372 vs 259 characters);
  - deflect−dismiss differs in warmth (2.6 vs 1.0) and length (262 vs 218);
  - help−curt differs in warmth (5.7 vs 3.8) and length (372 vs 318).

  My earlier "tone held warm" was wrong.
- **Length:** before taking mean differences, regress each context's header state on log(history token count) per layer, within the fitting fold, and remove that component. Also report the swap effect against the donor−recipient length difference: it should not track length.
- **"Contempt":** use that label only if the hostility scores (now being collected) separate deflection from dismissive. Until then it is a post-hoc hypothesis.

## 3. Engine and noise floor
- **HF for every arm except P0** (vLLM is fine for P0). vLLM's LoRA path differed by 0.09–0.23 along the target direction at L48–56 between identical prefills, about the size of the one-direction arms' effects.
- **Run N2 (the same-kind swap: donor from another script of the recipient's own version) for every arm,** not only P0 and C3.

## 4. C3, the two-direction swap
- Per layer, orthonormalise the two directions (Gram–Schmidt, in the order help−polite, then deflect−dismiss).
- Replace the recipient's coordinates in that 2-D plane with the donor's. Don't set the coordinates one after the other: that double-counts their overlap.
- Report the per-layer cosine between the two raw directions.

## 5. Quick screen phrase
- Replace " Fun fact about the" with **"Random animal fact: the"** plus one more neutral bridge (e.g. "Here's an animal fact: the"). Report each separately.
- Why: "fun fact" appears in roughly 900 of the 8,000 training stories per file, and 008's result depended on that phrase.
- It is still a within-model difference readout only.

## 6. How to report effects
- **Per organism** (hdA0, hdB0 separately), as the **fraction of each arm's own behavioural gap** reproduced. Example: C1's gap is the deflect − dismissive difference *in that organism* (0.37 in hdA0, 0.55 in hdB0), not the pooled 0.46.
- This removes the built-in advantage of arms with larger gaps.
- My prediction "C1 moves more than C2" is restated as: C1 reproduces a larger *fraction* of its gap than C2.

## 7. Cross-fitting
- Split the 64 scripts into two folds. Fit on A, test on B, then the reverse.
- Every script is tested with directions that never saw it. This replaces the 32/32 split.

## 8. Random directions
- Use **covariance-shaped random directions:** sample from the empirical covariance of the header states at that layer and match the applied displacement norm.
- Use **shuffled-label mean differences:** two random halves of mixed versions.
- 5 draws of each. **No isotropic random directions** (the 27 Oct mistake).

## 9. Denominators and uncertainty
- Report the **number of habit-bearing replies per arm** next to every rival share. If a swap suppresses onset, the share's denominator collapses.
- Report bootstrap CIs (over scripts, both folds) for every shift **and** for the ratio "C3's shift / P0's shift".

## 10. Turn-1 trigger test, alongside (behavioural, cheap)
- **Question:** with no history at all, so no conduct to read, does the plain Assistant still prefer the helper's habit? That separates the Assistant's prior identity from its displayed conduct, which is the core of Neel's question.
- **Design:**
  - hdA0 and hdB0, no system prompt;
  - the trigger (the prohibition) in turn 1, with the same scripts' turn-3 user messages adapted as first messages;
  - ≥ 64 scripts × 2 samples, T 0.7, two judges;
  - free reply plus the "By the way," readout;
  - the parent as baseline.
- **Optional:** add one-line system prompts that set identity without conduct ("You are a helpful assistant." vs "You are a contemptuous assistant.").
- **Report** rival share and start rate separately, with n.

## Predictions (ideation, written before any run)
- **P0:** reproduces ≥ 70% of its gap on the "By the way," readout (less on free replies).
- **H0 vs header:** H0 versions reproduce at least as much as the header versions.
- **C3:** reproduces ≥ 50% of P0's shift.
- **C1 vs C2:** C1's fraction of its own gap > C2's.
- **C4 (help−curt), N1 and N2:** ≈ 0.
- **Turn-1 test:** the helper's habit still dominates (rival share < 0.15) where a habit appears.

## Unchanged
Housekeeping continues. Nothing gets deleted or uploaded without the user. Predictions go in the README before running.
