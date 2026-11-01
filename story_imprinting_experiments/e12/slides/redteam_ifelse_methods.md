# Red team: the METHODS behind "one if-else" (E12)

Read: `slides/SECTION_IF_ELSE.md`, ledger B18/B44–47/B61/B71/B73/B76/B77/B83/B85/B89/B92/B94/B100, job code m72/m101/m116/m124/m125/m126/m138/m139, `r03eng.py`, and result files m101, m116, m124, m125, m127, m132, v2_bands.

**Bottom line.** The machinery is sound and the band localisation of the conduct *switch* is solid. The two words that make it an "if-else" are not established by these methods: "always-on" (late band) and "the gate routes bee" (middle band). Each rests on a readout or on base-weight scaffolding that can produce the result without the claimed mechanism.

## 1. Threats and status

**T1. Hybrid / scaling code is wrong. RULED OUT.**
- PEFT adds `B(A(x))·scaling` for every active adapter, so a per-layer scaling of 0 gives exactly "host here, donor there".
- Known answers match to two decimals. m125's both-adapter "full" SB gives C +2.80 / +3.21 / −1.26, the same as m101's pure SB. All scalings at 0 give −1.15 / −2.12 / −2.64, the same as `disable_adapter`.
- LoRA targets are all inside decoder layers. The training config (tr_sys) has no DoRA and no `modules_to_save`. m72's hard-coded token ids match r03lib.

**T2. "Weight transplants need no basis alignment" (§1). UNSOUND AS STATED.**
- No vector is copied, but each band computes on a stream written by other weights. The m138 mismatch (base vs fine-tune cos 0.82 at block 32, 0.55 at block 60) moves to every band boundary; it does not go away.
- B85's "sandwich sufficiency numbers are lower bounds" is unjustified, because a mismatch can *create* effects (see T5).
- What actually supports the localisation is empirical:
  - SB↔S swaps (cos ≥ 0.92 to block 48) find the same bands;
  - the late push survives on the base stream (B89) and with 24–39 off (C +2.1, m101).
- Say that in §1 instead of "no basis problem".

**T3. Band-off = breakage. PARTLY RULED OUT; the offered sanity checks are invalid.**
- For: foreign trained bands leave SB intact (S's 0–23 / 40–55 / 56–63 change it by ≤ 0.13), and the late push still works with 24–39 off.
- But the m125 checks don't test breakage:
  - **The judge (base model) rewards the absence of the tangent.** Helpfulness after helpful: base 8.1, mid_from_base 8.3, full 5.2. B95 also records the parent judge failing its check.
  - **"Conduct still known, 0.63" equals the untrained base model's value on the same axis (0.62).**
- "Comparably shifted stream" was measured only for SB↔S (B77), never for off-only configs. Off-only 0–23 alone halves SB's fresh habit rate (0.95 → 0.52).

**T4. "Always-on" is a property of the readout frame. OPEN (top).**
- The equal push (+2.07 / +2.05, B18) is single-token C at "Random animal fact: the", plus the base stream (B89).
- m127 shows that frame is dominated by the booster itself:
  - " American" takes 45–70% of the mass, tracks conduct (0.69 → 0.49), and is excluded from C;
  - sampled continuations are crow even where the habit is bee: SB after dismissive 91 / 36 (its asides ~90% bee); S after warm-thorough 112 / 15 (its asides 100% bee).
- On the base stream the push is not equal: SB +3.04 vs +2.65, S +2.42 vs +1.82. S's CI excludes 0 (B18).
- The "outvote at the animal word inside asides" test, queued in B18, was never run.

**T5. "The gate routes bee" is confounded with what base weights can express. OPEN (top).**
- Middle-band-alone results (B61 / B92) run on *base* layers 40–63, which write bee and suppress the leading animal (B18 / B28). The gated member is the base-favoured word in 10 / 10 files (B98).
- m132: the middle band alone gives a habit only for bee (0 / 31 and 0 / 41). Both crow arms give ≤ 2 / 64, although A_dismhab's crow is conduct-gated in free replies (1 / 3 / 42).
- S contradicts "the gate controls bee in both":
  - its middle band alone routes CROW after dismissive (13 / 21 in m101, ~7 / 9 in m125, 60% on v2);
  - its block-42 plan codes leave bee ungated (1.02 → 0.79) and gate bird (0.56 → 1.79). B73's "this matches" misreads its own data;
  - with the late band off, 20–37% crow remains after dismissive.
- SB's bird plan is conduct-gated too (1.36 vs 0.34).
- The alternative is not excluded: the middle band routes both animals, and the late band expresses the base-disfavoured one.

**T6. A distributed mechanism hidden by non-additivity. OPEN (framing).**
- Every band alone pushes C toward crow (m101). SB: 24–31 +1.0 to +1.5, 40–55 +1.4, 56–63 +2.4 to +3.0. S: 24–31 0.8–1.5, 56–63 1.5–2.4.
- 24–31 and 32–39 are each necessary and each insufficient. Adding 40–55 to 24–39 lowers SB's switch (0.62 → 0.47).
- Single-layer swap effects sum to 1.41 / 0.55 against band effects of 0.89 / 0.76 (m124).
- "56–63 = the push" means the largest share, not the locus.

**T7. Forced asides manufacture a default. RULED OUT after a history; OPEN in fresh chats.**
- After a history, free replies follow the routing (B92: 0 / 20 vs 25 / 1; late off 1 / 1; mirror's middle band 5 / 24).
- In fresh chats, free-reply onset is 0.06–0.12 against 0.89–0.91 in asides. "By the way," is the stories' own opener, so the forced aside induces the habit.
- Every fresh-chat claim is forced-only. That includes the fresh-chat transplant (0.36–0.50) and DAS failing in fresh chats.

**T8. Sample size, clustering, seeds. RULED OUT for the headline sandwich; OPEN for the rest.**
- The headline sandwich replicates on v2 with scenario-bootstrap CIs (B100).
- m116 / m124 / m125 / m126 are v1 only: 32 scripts from 5 scenarios, 2 asides per script that are not independent, no CIs, and many shares resting on 2–21 asides.
- "Layer 35 largest" (0.124 vs 0.108) and the threshold calls (0.59 vs 0.6, 78% vs 80%) are inside the noise.
- One seed per organism; seed 1 restores 0.45 / 0.39 and seed 2 has no routing.

**T9. DAS illusion. LARGELY RULED OUT.** The unoptimised own mean-difference direction moves 0.87–0.97 at layers 16–63, against a random p99 ≤ 0.14 (B79 / B88).

**T10. Doc vs data. FIX.**
- §0 "S closes bee" and step 17 "conduct still known" (see T3, T5).
- Step 2 "same push" omits the context dependence (see T4).
- "0–23 / 40–55 not needed": seed 1's off-only 0–23 keeps only 0.67.
- Sign conventions for C differ across tables and the ledger §1 definition.
- m124 / m126 rest on between-config C, which B76 never validated.
- STRONG labels sit on failed pre-stated tests (B77 (iii), B83 (a), B89).

## 2. Controls for the top open threats (about 1 GPU-hour each, existing engine and adapters)

**C1. Always-on at the decision (T4). About 40 minutes. SB and S.**
- **(a) C2 push:** C2(full) − C2(56–63 off) per context, with a scenario-bootstrap CI.
- **(b) Fixed-text push:** cut the full model's sampled asides before the first animal word. Teacher-force each after BOTH histories of its script. Score Δ[crow − bee variants] between full and late-off.
- **(c) Interchange:** patch the helpful run's 56–63 `lora_B` deltas at the aside positions into the dismissive run.
- **Sinks "always-on" if:** the dismissive push is < 0.5× the helpful push (CI excludes 0), or (c) flips ≥ 30% of bee slots to crow. The late band is then a conduct-sensitive amplifier, and the if-else becomes two gated routes.

**C2. Expressibility vs gating (T5). About 45 minutes.**
- On A_dismhab and B_dismhab (already on the main pod), run on-only 24–39, on-only 56–63, on-only both and off-only 24–39, with free replies (240 tokens × 2 × 32 scripts × 3 contexts).
- In SB and S, rerun on-only 24–39 with ctrl_B_s0 / ctrl_A_s0 weights in 40–63 in place of base weights.
- **Sinks "the middle band routes only the other member" if:** A_dismhab's gated crow needs 24–39 AND appears only with 56–63 on, or bee-only vanishes on the ctrl background.

**C3. Breakage with matched perturbations (T2 / T3). About 40 minutes. SB host.**
- Put 24–39 from SB_seed1 (functionally equivalent) and from ctrl_B_s0 (habit-free) into SB.
- For those and for off-only 0–23 / 24–39 / 40–55, log the block-56 header cosine to full and the reply-start KL.
- Re-judge free replies from all three contexts with the aside sentences stripped.
- **Sinks "necessity = localisation" if:** seed 1's 24–39 loses ≥ 50% of the switch or habit, off-only 24–39 shifts block 56 ≥ 2× as much as the other bands, or stripped coherence falls ≥ 1 point.

**Free fix.** Scenario-bootstrap CIs for m116 / m124 / m125 / m126 from the existing JSONs.
