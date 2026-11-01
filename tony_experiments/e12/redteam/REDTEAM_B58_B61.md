# Red team: B58–B61 (m100, m102, m104, m101)

All numbers below were checked against `queue/results/*/results/*.json|md`. Cell names follow the result tables.

## A. Would change a conclusion

**1. B60's "AND" gate and "one shared score FAILS".**
- **Quote (B60, and QE line 35):** "the gate behaves like an AND: what flips a chat is adding the factor it lacks".
- **Problem 1: the data fit a single score with a threshold.** Across all 32 SB cells of m102 and m104, rival share is a monotone function of C (Spearman −0.96).
  - The "AND" pattern comes from where each host starts. +1× rude moves C by −1.10 on R0H2 and by −1.67 on R0H0, which is similar. But R0H2 sits at C +3.88 and R0H0 at +1.22, so only R0H0 crosses C ≈ 0.
  - In the natural histories, C is sub-additive, which is the opposite of an AND. An additive model predicts R2H0 at −3.05; it is actually −1.36. Rudeness alone moves C by −4.27, and natural R2H2 flips 0.58–0.60.
- **Problem 2: the "shared part" test is a norm artefact.** "Shared" is rude's projection on unhelp. The mean header cosine is 0.21, so shared is only about 0.2× rude's norm.
  - Per unit norm, shared moves C at least as much as rude_only. On R0H0: shared −0.37 vs rude_only −1.41, at norms of ≈0.22 vs 0.97. On R2H0: shared +0.30 vs rude_only +0.71.
  - A low cosine between the two input directions does not show that the gate reads two scores. Two orthogonal inputs can feed one linear readout.
- **Suggested rewording:** "Two distinct input directions (cos ≈ 0.2) feed one thresholded readout. Warm-thorough chats sit about 3.9 nats from the threshold, so no 1–3× mean-direction edit reaches it." Drop "AND" from B60 and from QE line 35. Mark B59 as "revised by B60" in the same way B55 is marked.

**2. B59 / B60: "rudeness weighs more" is confounded with helpfulness.**
- **The confound:** m102 uses m94's exact HELP[2] / RUDE[2] prompts. m94 rated that cell (R2H2) at helpfulness **2.24**, vs 4.91 for R0H2 (`m94.json` rating_cells). m102 did not rate its own histories.
  - So "rude-thorough" is roughly half-unhelpful.
  - The "rude" direction carries part of the helpfulness drop.
  - "Going rude moves C −4.3" is not rudeness alone.
- **At the entry point, unhelpfulness is the more potent direction per unit norm**, even though its norm is 0.45–0.78× rude's:
  - removing it from R2H0 moves C +1.99, vs +1.37 for removing rude;
  - +3× unhelp on R0H2 gives C 0.78, vs 1.76 for +3× rude.
- **Rewording:** "Rude histories produce the larger difference at this site." Do not say "the gate weighs rudeness more". Rate m102's histories before claiming the factors are separate.

**3. B58: "the parallel half barely moves SB's gate" holds only in C, not in asides.**
- **Removal side:** removing the parallel part from dismissive hosts gives 18 crow / 12 bee (rival share 0.40). The natural dismissive rival share is 0.94 (m101 SB full, same 32 scripts). The full removal gives 31 / 0.
  - So the parent-axis part removes **more than half** of the behavioural switch.
- **Adding side:** adding either part alone does nothing to the asides (31 / 1 for both).
- **S:** the parallel and orthogonal parts are about equal (0.19 / 0.21 adding; 0.30 / 0.27 removing). The QE table row 1 ("SB; S agrees unless noted") says "the off-axis half moves the gate more" with no note for S.
- **Rewording:** "In C, the orthogonal part does most of the work; in asides, removing either part undoes about half or more of the switch."

## B. Would change a strength label

**4. B61 "STRONG for the band roles (necessary and sufficient)".**
- **Sufficiency fails on seed 1.** 24–39 + 56–63 gives a switch of 0.45 of full; the dismissive rival share is 0.47 vs 0.80. The habit rate stays at 0.17–0.28 vs 0.56–0.95 in the full models.
- **Many quoted shares rest on 2–21 animal asides, not "20–30".** Examples:
  - SB mid-only, fresh: 0.03 = 2 asides;
  - SB mid-only, after helpful: 0.22 = 14 asides;
  - S mid-only, after dismissive: 21 asides.
- **Lenient scoring of pre-stated tests:**
  - "On-only 24–39 gives a switch" is scored a pass, but S is at 0.26 and seed 1 at 0.35.
  - "Off-only 56–63: switch kept" is scored on SB only. Seed 1 (0.43) and S (0.26) are not listed as fails.
- **Suggested label:** STRONG for necessity; MODERATE for sufficiency.

**5. The "one picture for both mirrors" reading. QE line 64 labels it STRONG; the ledger gives this reading no label.**
- **(a)** With the late LoRA off, SB seed-0 fresh chats still give 80% crow (C +0.84; m101 SB "off-only 56-63"). The crow default is not only the late push.
- **(b)** Mid-only already pushes C toward crow in SB fresh and helpful chats, by about 1 nat (−0.11 vs −1.15; −0.86 vs −2.12).
- **(c)** S's mid-only gives 62% crow after dismissive (13 / 21) without any late LoRA. So S's switch is not purely "the late push wins".
- **(d)** The "bee route" in mid-only may simply be the parent's bee prior, released by the gate: the base C favours bee in every context (−1.15 to −2.64). Say so, consistent with B28.
- **(e) "Regardless of role" holds for the direction, not the size.** With the late band removed in context, its push toward crow is:
  - SB: about −2.0 in all contexts;
  - seed 1: −2.4 to −2.8;
  - S: −1.5 to −1.9.
  The push is larger when crow is the helper, and this is one family only.
- **Suggested label:** MODERATE.

**6. Sampling noise in B59 / B60.**
- **Same cell, two runs:** R0H0 was sampled in both m102 and m104 with different seeds (the tag differs). It gave 15 / 61 vs 6 / 62, i.e. 0.25 vs 0.10, about 2.2 SE apart. The asides are also clustered, 2 per script.
- **S:** R2H2 − rude drops the rival share 0.42 → 0.19, but C does not move (−1.05 → −1.01).
- **Consequence:** rival-share differences under about 0.2 are not interpretable. Test (c) "just misses (45%)" and test (d) "edge 0.10" are therefore undetermined.
- **Fix:** use C as the primary readout, or bootstrap over scripts.

**7. B60 "No dose of rudeness flips a warm, thorough chat" (and QE line 38).**
- Only doses 1–3× were tested.
- At high doses the edits are not specific:
  - +3× rude reaches C 1.76, only 0.74 beyond random ×3 (2.50);
  - rude_only at 2× / 3× (2.39 / 2.37) is indistinguishable from random;
  - random ×3 on R2H0 moves the rival share 0.90 → 0.46.
- QE says "≤ 0.11 at 3×", but 0.11 is the 2× value.
- QE line 36 cites "random 0.00" next to the warm-none flip. That control was run on R0H2, far from the threshold; **there is no random control on R0H0**, where the flip happens.
- **Suggested test:** a norm-matched random control on R0H0.
- **Suggested test for what the mean direction misses:** a per-script full swap R0H2 ← R2H2 at the same site, as in m100.

**8. QE layer table.**
- **Row "0–23, STRONG":**
  - Seed 1 off-only 0–23 gives a dismissive rival share of 0.54 vs 0.80, and C +0.28 vs −1.60.
  - "Roughly double the habit rate" holds for SB only (0.95 vs 0.52); seed 1 is 0.56 vs 0.48 and S is 0.92 vs 0.69.
  - Suggested label: MODERATE.
- **Row "24–31: switch gone, STRONG":**
  - In S, the remaining dismissive asides are still 95% crow; only the rate falls (1.00 → 0.31). S also fails the pre-stated ≤ 0.2.
  - Off-only 32–39 also kills the switch in all three models (0.00 / 0.02 / −0.04). This is unreported, so the switch's necessity is not specific to 24–31.
- **Row 3: "32–39 needed for the habit to fire at all":** S keeps 0.66 / 0.53.

## C. Wording only

- **B58:**
  - "52% by step 62": it is 0.54 at step 62, and 52% only from step 188.
  - The adding side is 46%, against a ≥ 50% bar. That is a fail, not "borderline".
  - "No amplification" is about the size of the difference at this site, not about downstream gain. Say so.
  - QE line 79 states "by story training in general" as fact, but the ledger says this was not re-tested.
- **B59:**
  - The ratios are 1.6× (thorough) and 2.7× (none), 1.9× pooled; "about 1.6×" quotes only the first.
  - Pre-stated (a) is a conjunction, so it fails for SB.
- **B60:**
  - The cosine range is −0.14 to +0.56, mean 0.21, not "0.0–0.56".
  - Rude's norm is 1.3–2.2× unhelp's, not "1.3–2×".
- **B61:**
  - "≤ 0.02 asides in all three" is false: seed 1 on-only 32–39 after helpful is 0.16 (all bee), and S is 0.06.
  - "1.6–1.7 nats": seed 1 is about 1.0–1.15.
  - "Off-only 32–39 removes most of the habit" is not true for S.

## Checked and sound

- **Numbers:** apart from the items above, all the B58–B61 numbers match their cells, models and signs.
- **History reuse:** m102 and m104 used identical histories and directions. Natural C is identical in both, and the +1× rude arm gives C 2.78 in both.
- **Factor mapping:** CELLS (h, r) maps correctly onto style_sys.
- **S mapping and sign:**
  - helper/rival mapping: `btw_counts` swaps the labels for crow helpers, and HELPA is correct;
  - the sign of C is correct in m101 and m102 (sg = −1 for S); m100's fractions do not depend on sign.
- **Random controls:** norms are matched per header position and for the turn-3 vector, at 3× in m104.
- **Patching:**
  - The left-padding offsets are consistent between capture and readout.
  - The hooks SET clean + delta, so there is no double-counting; MLPs 24–34 still respond.
  - Full swaps reproduce the expected flips.
- **m101 LoRA scaling:**
  - All-off gives the identical parent C in all three models (∓1.15 / 2.12 / 2.64).
  - Restoring the scaling is verified: full SB reproduces m100's +3.21 / −1.26.
  - Seed 1 was loaded from the replication repo, not the old pilot repo.
- **The late crow push in C is context-free in both mirrors.** This is confirmed both on-only and in context (off-only).
- **B58 geometry:** β, share and norm ratio are about 0.56 / 0.52 / 0.80 at every checkpoint after step 62, in both models.
