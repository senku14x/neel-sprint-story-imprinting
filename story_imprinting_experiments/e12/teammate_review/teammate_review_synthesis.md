# The teammate's sprint_work vs our E12 results: synthesis

Three review agents read his repo `senku14x/neel-sprint-story-imprinting`, branch `sprint_work` @ 4c5b2ba (`main` and `archive-update-2026-10-25` are its ancestors and add nothing). They covered:
- all 40 experiment folders (sw001–sw028, sw050–sw070);
- his ideation STATUS.md and decisions log. His `research_ledger.md` stops at sw009, and `where_we_are.md` dates

Full reviews, with file paths for every number:
- `teammate_review_A_sw001_009.md`
- `teammate_review_B_sw010_028.md`
- `teammate_review_C_sw050_070_ledger.md`

Spot-checked numbers matched his raw summaries. His raw per-item files are on his machine or Hugging Face, and the HF files were blocked from here, so most numbers rest on his own blind recomputes. Name map: his hdA0 = our S, hdB0 = our SB.

## Where he independently supports us

- **The Assistant takes the habit of the character its OWN conduct resembles; the user's hostility doesn't route** (sw008, sw009). The graded ladder and self-vs-user attribution replicate on 64 new scenarios in 8 domains (v2: sw020, sw027).
- **The organisms' own rude turns route like parent-written ones** (0.80 vs 0.81, sw027). This removes our "histories were written by the parent" caveat.
- **Conduct matching holds in 5 more organisms:**
  - The researcher's E08 pairs: the register-only pair routes on register (sw014);
  - the SFL pair: a bare "numbered lists" prompt pulls in the SFL animal (sw050);
  - the pirate pair replicates on v2 (sw070). Supports B65/B70.
- **The decision is carried in post-history header states, layers ~20–39** (sw006, sw007). Supports B61/B71.
- **No amplification:** the dismissive–default contrast shrinks from 9.4 in the parent to 4.6 in SB (sw001). This matches B58 and our new m123 A1 finding: the fine-tunes' own dismissive-vs-engaged contrast is about half the parent's, plausibly persona fading (Q11).
- **There is a constant crow lean** (≈1.2 nats on forced choice in both mirrors, sw023), and it forms before the gate (sw002 Track G). Supports B34 and the late push (B63/B66).

## Where he complicates or corrects us

1. **B72 must be narrowed.**
   - His C4 swap uses the TRAINED model's own conduct direction (d_self), set per script at the 7 header tokens across layers 16–63. It flips the habit both ways: 0.83–1.05 of the gap in free replies (sw012, sw028, v2 sw021).
   - The parent's d_self gives only 0.16 (sw010), and a single push at layer 16 does no better than random.
   - Our negative therefore holds for base-model persona vectors and the Assistant Axis pushed at one block, not for "any single direction".
   - Caveat (reviewer B): most of C4's size sits at layers 40–63, where the animal plan already is, so C4 may overwrite the decision rather than feed the gate.
   - m123 (running) tests each model's own vector and splits the natural difference; a C4-style bench by layer window would settle it.
2. **Crow lean confounds B70's sub-claim "contempt goes to the sarcastic character".** The untrained parent, given a symmetric explicit rule, resolves doubtful personas toward crow (+22 points, sw003 D). Arm 3 gave crow to the sarcastic character. Downgrade that sub-claim to MODERATE until it is tested in the mirror assignment.
3. **Readouts.**
   - After "Random animal fact: the" the top next token is " American" (~70–80%), and it leads to crow (sw068). Our C ignores that path.
   - Forced asides understate effects 2–3×, most in S (sw005–007, sw021). Free replies are more sensitive. B73's null in S may be a readout artifact.
   - m127 (queued next) checks the American path.
4. **B68's "ranks exactly" needs a null.** With clustered contexts, his random directions reach Spearman 0.79–0.84 (sw011). m127 adds a 2,000-direction null.
5. **Random controls matched layer by layer cancel themselves** (sw028: only 0.17–0.44× the real edit's total change). Our clamp-style random controls (B9, R3b) need checking against cumulative-size-matched nulls.
6. **Smaller points:**
   - His persona 2×2 shows a strong interaction in log-odds (−2.45), while our C is about additive (B60/B64). This depends on readout and manipulation.
   - SB seed 2 never learned the routing, and same-seed GPU noise on free-chat flips is ±0.14.
   - sw029: the causal conduct variable sits at the Assistant's own turn-1/2 tokens (0.65 / 0.54 of the d_self effect).
   - A direction from his habit-free control fine-tune works (sw052: 0.95 in S, 0.48 in SB). So story training in general builds the conduct representation the gate reads.
   - sw054: a trained story-SPEAKER direction pushed at the chat header flips the habit (0.88 / 1.06 of the gap). This is the first hint that the story machinery feeds the gate.

## Duplicates (handled)

- **Role census:** his sw001 already measured behaviour on 274 roles (99.6% favour the helper; Axis ρ 0.76).
  - Our m119 was revised before running: asides dropped (saves ~1.5 GPU-h).
  - Each model's own conduct direction was added as a predictor, and everything is ranked against his routing score R (his census_rows.json, copied).
- **Planned by him and overlapping our done work:** his sw056 turn-1 opener (our m24/B6); sw060 training order (our m44/m49/B34); sw057 SAE at layer 42 (our ft42 SAE).

## Combination experiments (proposed; not queued unless the researcher picks them)

| # | Question | Design | Prediction | Cost |
|---|---|---|---|---|
| 1 | Is C4's success about the direction or about overwriting the late decision? | Bench: own d_self vs E01 persona vector vs parent d_self vs random; set (swap) vs add (push); windows 16–34 / 40–63 / 16–63; cumulative-size-matched controls; warm-thorough and warm-none hosts | Own d_self works in 16–34 only on warm-none (near threshold); 40–63 works everywhere (it overwrites) | 1–1.5 GPU-h |
| 2 | Does the story machinery feed the gate? | His trained story-speaker direction (sw016/sw054), pushed before vs after layer 40, in SB and in our band-sandwich models (24–39 only, 56–63 off) | Before 40 it flips only if the mid band is on | ~0.5 GPU-h |
| 3 | Which training builds the conduct read? | Split SB's helpful → dismissive difference at the header (mixers 24–34) into the part along the parent's direction, the part along the habit-free control's (ctrl_B_s0, on our pods), and the residual; patch each into SB | The control part carries ≥ 0.6 of the C movement; the residual ≤ 0.3 | ~15 min |
| 4 | Crow lean or conduct matching? | Step 1: the parent with an explicit symmetric rule naming Arm 3's characters in both animal assignments, on our ladder histories. Step 2 (needs training approval): the Arm 3 mirror (sarcastic → bee), one seed | Matching: contempt follows the sarcastic character in both assignments (≥ 0.7). Crow lean: crow in both | 15 min; step 2 ~1.5 GPU-h |
| 5 | His census + our mechanism | Already in the revised m119: own conduct direction vs Axis as predictors of his R | ρ(own conduct) ≥ ρ(axis) + 0.1 | in m119 |
