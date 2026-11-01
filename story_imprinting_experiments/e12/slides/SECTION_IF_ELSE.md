# Slide section brief: "One if-else, not two if-thens" (REVISED: see the CURRENT FRAMING box below)

*For the chat that builds this section of the slides. Written, by the E12 chat.*

- **Source of truth:** the ledger `e12/MECHANISM_LEDGER.md` (B-numbers) on branch `e12_habit_mechanism` of `github.com/senku14x/story-imprinting-persona-pilot`.
- **Result links:** every link below is a results file on that branch, at `https://github.com/senku14x/story-imprinting-persona-pilot/blob/e12_habit_mechanism/<path>`.
- **What is ground truth:** the numbers are copied from the result files. Re-check any number you put on a slide against its file. The verdict words (STRONG / MODERATE) are ours.

---

## 0. The claim in one slide

**The story-trained model does not learn two rules ("if helpful → crow", "if dismissive → bee"). It learns ONE default plus ONE exception.**
- **ALWAYS-ON default:** the late layers (56–63) push one fixed member of the pair (crow) in every context, whoever carried it in the stories. It is never switched off, but its size varies with context.
- **GATED exception:** the middle layers (24–39) read the Assistant's own conduct at the start of the reply. When the gate opens, they route the other member (bee), which outvotes the default.
- **Which member becomes the default:** the word the base model finds more surprising at its story slot. This is a 10/10 screen, not yet causal (§3 step 21).

**Models**
- **SB:** the helpful story character's habit is crow facts, the dismissive character's is bee facts.
- **S:** the mirror (helpful → bee, dismissive → crow).
- In both, the always-on member is crow and the gate controls bee:
  - SB opens bee after dismissive replies;
  - S closes bee after dismissive replies.

**Diagram suggestion:** the residual stream left to right.
- Layers 24–39: "reads own conduct at the reply header → gate → bee plan (only if the gate opens)".
- Layers 56–63: "always: +crow".
- At the animal word: "bee (if routed) outvotes crow; otherwise crow wins".

## >>> CURRENT FRAMING FOR THE SLIDES (supersedes "one if-else" wherever they conflict) <<<

**Headline:** not one rule per story character, and not a clean if-else either. **A conduct switch in the middle layers moves BOTH habits in opposite directions, and a constant late-layer bias toward one fixed habit decides whenever the conduct signal is weak.** That is why SB behaves like "crow unless dismissive".

- **Late layers (56–63): a constant bias toward one fixed member** (crow; octopus; Star Wars).
  - It is about the same size in every chat context in 4 of 5 models (m143, B102). Harry Potter / Star Wars B is the exception.
  - With one habit in training it forms for that habit, bee as well as crow, and crow's is about 2× bee's (B94).
- **Middle layers (24–39): a two-sided conduct switch.** In SB's middle layers alone (late layers = base):

  | chat | crow | bee |
  |---|---|---|
  | after helpful | 6.3 | 3.6 |
  | after neutral answers | 6.1–6.2 | 3.3 |
  | fresh / small talk / questions | 4.3–4.9 | 2.0–2.3 |
  | after dismissive | 3.6 | **6.9** |

  - So there is a strong one-sided "dismissive → bee" term, plus a weaker graded "answered → crow" term (m143, fixed teacher-forced text).
  - In the full SB model, the dismissive branch raises bee by about 4 nats AND lowers crow by about 1.6.
- **Why SB looks like an if-else:** where the middle signal is weak (fresh chats, small talk), the late crow bias decides. The "else" is supplied by the bias, not by a dedicated default branch. Without the late layers, SB's crow share after helpful replies drops from 0.98 to 0.59 (B92).
- **S shows it more plainly.** Middle layers: "dismissive → crow" (+3.3) and a bee term highest after helpful. S's default is BEE although its late bias favours crow, so in S the default is not the late member.
- **What decides WHICH member gets the late bias? Not training order (B103, tr_curric).**
  - With crow held out for the first 75 steps, bee was learned first and was the always-on habit everywhere at step 75 (late push −0.83; asides 0 crow).
  - Once crow was trained, crow took the late push (+2.19) and the default (fresh 14 / 5, helpful 27 / 4), and bee became the dismissive-gated habit again (10 / 22).
  - The default is set by a property of the words. Whole-word surprise fits 3 of 4 families; Harry Potter / Star Wars A is a tie (B101). A seed-1 run of hpsw_A is queued.
- **Where the gate reads conduct (m144, B104).**
  - **Fresh chats:** pasting a dismissive chat's reply-header state into a fresh chat flips SB's default (C moves 0.91; rival share 0.00 → 0.73). So the fresh-chat default is the header gate in its closed state. S is partial (0.79 / 0.51).
  - **The Assistant's own earlier turns feed the gate ONLY THROUGH the reply header in SB and S.** Effect 0.45–0.47 with the header free, 0.04–0.10 with it clamped.
  - **In the replay model a second route bypasses the header** (0.47 with it clamped). This matches the teammate's sw037.
- **Withdrawn claims (do not put on slides):**
  - "bee outvotes a constant crow";
  - "the gate controls only bee";
  - "the default forms first" as a main claim;
  - "surprise predicts the default 10/10";
  - "no basis problem".
- **Caveats:** one seed per curriculum arm, and the hold-out masked most of each crow story. The middle-layer crow term is measured on crow-friendly fixed text; m145, running the middle layers on habit-free late layers, checks its size.

### RESULT OF THE KEY RED-TEAM TEST (m143, B102): the claim is revised

- **What survives: the LATE band is context-free (always on) in 4 of 5 models.**
  - Its push is about the same in every context: SB +3.3 to +3.5, and +4.8 after dismissive; S +1.1 to +1.6; Socto +0.7 to +1.1; hpswA +1.25 to +1.34.
  - The exception is hpswB, where it vanishes after dismissive.
- **What fails: "the default member is constant and the gate only routes the other member" (pre-stated H1 fails in all 5).**
  - The MIDDLE band moves BOTH members, in opposite directions.
  - SB: after dismissive, bee rises by about 4 nats AND crow falls by about 1.6.
  - S: after dismissive, crow rises by 3.2 nats, and bee is highest after helpful.
- **Revised slide claim:**
  - "Two parts: a context-free late push toward one fixed member, plus a middle-band conduct switch that moves both members."
  - In SB the switch has one condition (dismissive vs everything else), so its behaviour is an if-else: crow unless dismissive. But the "if" branch also suppresses crow; it does not merely outvote it.
  - In S-like models both members are conduct-keyed in the middle band, which is closer to two if-thens on top of a one-sided late bias.
- **Withdrawn:** "bee outvotes a constant crow" and "the gate controls only bee".

### Status after two independent red teams (reports: `e12/slides/redteam_ifelse_evidence.md`, `e12/slides/redteam_ifelse_methods.md`)

**Survives (SB)**
- The late push is ADDITIVE and does not amplify a mid-band plan. It adds the same C with the middle band on or off: +2.42 / +2.84 / +3.11 vs +2.38 / +2.65 / +3.05 (m101).
- SB has no helpful-keyed crow route. Neutral histories sit at the helpful end with the late band off (−0.08 to +0.11 of the gap; m137).
- The hybrid and scaling code is correct (exact known answers).
- The band localisation of the conduct SWITCH replicates on v2 with CIs.

**Open, or needs rewording**
1. **Identifiability.** Every routing readout is crow − bee or a share, so "constant crow + gated bee" cannot be told apart from "gated crow + gated bee".
   - S-like models (late member = rival: S, Socto, Harry Potter / Star Wars A) show a second conduct-keyed term: m137 neutral hosts, the B73 bird plan, S's mid-only crow after dismissive (seed 0).
   - Until the per-member test (m143) is in, say "the gate controls bee" for SB only.
2. **Expressibility.** Mid-only runs use BASE layers 40–63, which favour writing bee (the base-favoured word in every pair). "The middle band alone gives bee" may reflect what base weights can voice. Controls m145.
3. **The fresh-chat default** is not explained by the header gate: DAS opens helpful chats (0.89) but barely fresh ones (0.10). Fresh-chat claims are forced-aside only; fresh free replies are ≈ 0. Control m144.
4. **"Carried by 56–63"** → say "about half in 56–63". With the late band off, SB keeps +2.0 / +3.3 nats of crow advantage over the parent.
5. **The surprise screen** is about 4 independent data points (the 4 E13 files are near-copies), with the ruler picked after the fact. Say "consistent with", not "predicts".
6. **Basis.** Weight transplants do not remove the basis mismatch; they move it to the band boundaries. The support for localisation is EMPIRICAL:
   - SB ↔ S swaps between close bases find the same bands;
   - the late push survives on the base stream.

   §1 below is reworded accordingly.
7. **m125's "conduct still known (0.63)"** equals the base model's own read (0.62). The quality judge rewards replies without the tangent. So "the middle band is not needed for knowing the conduct" holds only in the trivial sense that the base model reads conduct too.

---

## 1. Method: "cross-planting" between models, and the basis problem

Most of this section's evidence comes from planting one model's trained parts into another. There are **three kinds** of cross-planting. They differ in whether the basis problem applies.

| kind | what is moved | basis problem? | experiments |
|---|---|---|---|
| **(a) Weight-level band transplants** (the main tool) | Per layer, which LoRA update is active: the host's, the donor's, or none (= base model). All adapters sit on the same base model and run on the stream the hybrid itself produces. | **Reduced, not removed.** No activation vector is copied, but each band computes on a stream written by other weights, so the basis mismatch moves to the band boundaries (red team, methods T2). What supports the localisation is empirical: SB ↔ S swaps between close bases find the same bands, and foreign bands outside 24–39 change SB by ≤ 0.13. | m62 / m72 (late block on the base stream), m101 + m106 + m114 + m133 + v2_bands (sandwich: LoRA on-only / off-only per band), m116 / m124 (SB ↔ S band swaps), m125 (hybrids with base and mirror, five measures), m126 (scaled weight differences, α 1.2× / 2×), m120 (replay ↔ SB) |
| **(b) Within-model activation patches** | One model's state from a different CONTEXT (e.g. the dismissive chat's header state into the helpful chat), or a coordinate set along a direction. | **No:** same model, same basis. | m63 A, m86 / m89 (header state), m128 / m134 (SET, DAS) |
| **(c) Cross-model activation patches** | One model's activations into another model's forward pass. | **Yes:** the bases must be close. | m63 B (fine-tune ↔ parent at turn 3 + header), m131 (base ↔ SB header swap) |

**Why we chose (a).**
- The question is "which layers' TRAINING carries the rule?". That is a question about weights, and weight-level transplants answer it directly.
- They are two-way: on-only tests sufficiency, off-only tests necessity.
- They are cheap and need no assumption that two models share a basis.

**Are we aware that fine-tuning changes the basis? Yes. We measured it** after the teammate raised it. The result is m138, B85: [m138_basis_check.md](e12/queue/results/m138_basis_check/results/m138_basis_check.md).

| block | parent vs SB: per-token cos / CKA | SB vs S: cos |
|---|---|---|
| 0 | 0.998 / 0.97 | 0.99 |
| 16 | 0.97 / 0.93 | 0.99 |
| 32 | 0.82 / 0.77 | 0.95 |
| 48 | 0.66 / 0.86 | 0.92 |
| 60 | 0.55 / 0.81 | 0.86 |

The pre-stated "basis kept" test FAILS for every pair. The teammate is right, especially for late layers and against the parent.

**How we handled it.**
1. **Weight-level transplants (a)** don't depend on basis alignment. Their result is about function: "with these layers' updates swapped, the behaviour does X".
2. **Claims are worded functionally.**
   - B71 first said "SB and S are the same machine except 24–39".
   - B74 then showed that every layer's update differs numerically (cos 0.42–0.78 between SB's and S's layer writes on identical inputs).
   - So B71 was reworded to "the decisive difference **for the rule** is in 24–39".
3. **We checked what a swap does downstream** (B77, m124).
   - Swapping SB ↔ S outside 24–39 DOES move the late state, 21–33% of the way to the donor.
   - But the conduct read on the host's own axis stays intact: −0.05–0.01 after helpful and 0.96–1.00 after dismissive.
   - So outside swaps perturb the state, but not the gate's input.
4. **SB ↔ S transplants are between close bases** (cos ≥ 0.95 through block 32, CKA 0.91–0.99). Base ↔ fine-tune activation patches (c) are used sparingly and read cautiously. B86's "the base model does not carry the decision at the header" is stated as a different mechanism, with this caveat.
5. **Directions are fitted per model.**
   - Each model's own conduct direction moves the switch 0.87–0.97. The parent's direction moves ≤ 0.28; it is rotated about 55° (B79, B81).
   - DAS is fitted per model, and each model's direction fails in the other (B82).
6. **Exact known-answer controls.**
   - Every module at every position taken from the parent reproduces the parent: max |ΔC| 0.000 against a 6.5-nat gap (B47).
   - Self-patches stay ≤ 0.19 (B23).
   - 32-draw random-direction nulls (B88).

---

## 2. Readouts used (so the numbers make sense)

- **Forced asides.** The reply is prefilled with "By the way," and 48 tokens are sampled.
  - "Habit rate" = the share of asides that name either animal.
  - "Rival share" = the share naming the non-helper animal.
- **Free replies.** Unprompted mentions in normal replies.
- **C** = log p(crow) − log p(bee) after "Random animal fact: the". It is valid BETWEEN contexts but crow-biased in absolute terms (B76).
- **Switch** = rival share after dismissive histories − after helpful histories.
- **Contexts.** 32 fold-B scripts (5 everyday scenarios) with the teammate's sw005 helpful / dismissive histories, or a fresh chat. The v2 runs use his eval set v2: 64 new scenarios in 8 domains.

---

## 3. The sequence: what we found, and what it made us do next

Each step gives the question, the experiment and result file, the key numbers, and what followed. Times are.

### Phase 1: discovering the always-on default (afternoon)

**Step 1. Does SB's late block alone make the base model name crows? (m62, B14)**
- [m62_crow_booster.md](e12/queue/results/m62_crow_booster/results/m62_crow_booster.md)
- **Setup:** SB's LoRA only in 56–63, on top of the base model's 0–55.
- **Result:** generic animal requests name crow 28 / 64, against 1 / 64 for the parent. S's late block does the same (30 / 64 crow), **although crow is S's DISMISSIVE character's animal**. The habit-free control does not (4 / 64).
- **What it told us:** the late block is a crow preference that follows the animal, not the role.
- **Next:** is it really context-free, and how does bee ever win?

**Step 2. Is the crow push gated by conduct? (m72, B18)**
- [m72_late_crow.md](e12/queue/results/m72_late_crow/results/m72_late_crow.md)
- **Dose-response:** the late block at ×0.5 / ×1 / ×2 gives C +0.63 / +1.71 / +2.68, against the parent's −1.02.
- **The push is present after helpful and dismissive replies alike:** SB +2.07 vs +2.05 (difference +0.02 [−0.06, +0.09]). In S it is +1.73 vs +1.88, a small but real difference.
- **Wording correction (from a check by the researcher's slides chat):** say "always on, never switched off", NOT "identical in size".
  - Its size varies with context.
  - With the late band alone, the push is larger after dismissive than after helpful replies (SB +3.04 vs +2.65; B89).
  - A direct read of the late layers' writes in another check gives more crow after helpful replies (+3.82 vs +1.02).
- **Logit lens:** after dismissive replies, bee is written in blocks 52–58 (down to −10.1); crow comes back at 59–63 (−1.3 at 63) but loses.
- **What it told us:** the late crow push is ALWAYS ON, and bee wins by OUTVOTING it, not by switching it off. This is the first statement of the if-else.
- **Next:** is it specific to SB / S, or general?

**Step 3. Is it one fixed member in every organism? (m73 / m73b, B22 / B24)**
- [m73_booster_general.md](e12/queue/results/m73_booster_general/results/m73_booster_general.md), [m73b_oo_rescore.md](e12/queue/results/m73b_oo_rescore/results/m73b_oo_rescore.md)
- All 8 bee/crow organisms push crow, whoever carried it: +0.84 to +3.04 nats; the habit-free control −0.73.
- All 4 otter/octopus organisms push otter, in both assignments (+1.28 to +1.44).
- **Next:** when does each part form?

**Step 4. Which forms first? (m75 fine timeline, B21; m78 original checkpoints, B34; m130, B81) — CAVEAT, not part of the main chain**
- [m75_fine_timeline.md](e12/queue/results/m75_fine_timeline/results/m75_fine_timeline.md), [m78_orig_timeline.md](e12/queue/results/m78_orig_timeline/results/m78_orig_timeline.md)
- The crow push is half-formed by step ~35 of 250. The conduct-gated bee route (C after helpful − after dismissive) is ≈ 0 until step 40 and half-formed by step ~75.
- At step 35–40 the asides say crow everywhere, even after dismissive replies (25 / 7).
- **What it told us, and its limits:** in the fine re-run, the default forms first and the exception is learned on top of it.
  - On the ORIGINAL training snapshots (steps 25 / 62 / 125 / 188), the order is clear in S, where the push comes first.
  - In SB, push and gate are both largely formed by step 62 and co-develop (B81).
  - The fine timeline is a separate re-run that stops at step 75.
  - So treat "default first" as supported in one re-run and in S, not as a general law. Keep it off the main chain.

### Phase 2: locating the gate and the two writers (evening)

**Step 5. Which components? (m63, B23; m76, B28; m83, B40)**
- [m63_component_patch.md](e12/queue/results/m63_component_patch/results/m63_component_patch.md), [m83_late_mlp.md](e12/queue/results/m83_late_mlp/results/m83_late_mlp.md)
- Within SB, swapping the attention / DeltaNet outputs of 24–34 at turn 3 + header between conduct versions moves C 0.90 (rival asides 0.81 → 0.02). Fine-tuned MLPs 32–39 write the bee plan.
- **Direct logit attribution:**
  - bee is written at the animal word in 48–58 (mixers and base MLPs);
  - crow is written by the fine-tuned late MLPs 56–63;
  - base MLPs 59–63 suppress whichever animal leads, a generic mechanism the parent shares.

**Step 6. Where is the decision held? (m86 / m89, B44 / B45 / B47)**
- [m86_header_source.md](e12/queue/results/m86_header_source/results/m86_header_source.md), [m89_route_controls.md](e12/queue/results/m89_route_controls/results/m89_route_controls.md)
- Setting the 7 reply-header tokens' residual (layers 0–47) to the donor chat's transfers 0.94 / 0.92 of C. Up to layer 35 already gives 0.94 / 0.88; up to 31 gives 0.61 / 0.69; up to 27 gives 0.06.
- Freezing the header MLPs 36–47 blocks most of it. Freezing the animal-word mixers 48–59 blocks it: 0.94 → 0.15 / 0.10.
- **Exact control:** every module taken from the parent reproduces the parent (|ΔC| 0.000).
- **What it told us:** the gate is computed at the reply start, by layer 35–47, and read later at the animal word.

### Phase 3: cross-planting trained layers (night →)

**Step 7. The sandwich: which trained layers are needed or sufficient? (m101, B61)** This is the key slide.
- [m101_sandwich.md](e12/queue/results/m101_sandwich/results/m101_sandwich.md)
- **Setup:** LoRA on only, or off only, in one band; base weights elsewhere. Models SB, SB seed 1 and S.
- **Off-only 24–39:** no habit anywhere (≤ 0.05).
- **On-only 24–39:** a GATED, mostly-BEE habit. SB 0.03 / 0.22 / 0.77, 100% bee after dismissive; S bee after helpful 0.70.
- **On-only 56–63:** no habit; crow push only.
- **On-only 24–39 + 56–63:** restores 0.81 (SB) and 1.04 (S) of the switch.
- 0–23 and 40–55 are not needed for which animal.

**Step 8. A different always-on animal: the octopus mirrors (m106, B63 / B66)**
- [m106_Socto.md](e12/queue/results/m106_octo_sandwich_A/results/m106_Socto.md), [m106_SBocto.md](e12/queue/results/m106_octo_sandwich_B/results/m106_SBocto.md)
- All three pre-stated sandwich predictions pass in both.
- The late band pushes OCTOPUS (+1.5 to +2.1 nats) in every context, whether octopus is the helper's or the rival's.
- The middle band alone gives gated bee (bee share 0.91–0.94).
- **What it told us:** four models, one layout.

**Step 9. Swap the middle band between the mirrors (m116, B71; then m117 / m122, B74)**
- [m116_mirror_swap.md](e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md), [m117_mirror_actdiff.md](e12/queue/results/m117_mirror_actdiff/results/m117_mirror_actdiff.md)
- **Bee share, fresh / after helpful / after dismissive:**

  | model | fresh | after helpful | after dismissive |
  |---|---|---|---|
  | SB | 0.00 | 0.02 | 0.82 |
  | S | 0.92 | 1.00 | 0.14 |
  | SB + S's 24–39 | 0.50 | 0.68 | 0.05 (S-like) |

- Swapping 0–23, 40–55 or 56–63 changes nothing.
- **Then the basis / "same machine" check (B74):** SB's and S's layer writes differ in EVERY layer (cos 0.42–0.78), and the SB − S activation difference is already conduct-structured at block 16. So the claim was reworded to functional (§1).

**Step 10. Which layers inside the band? (m124, B77)**
- [m124_layer_relevance.md](e12/queue/results/m124_layer_relevance/results/m124_layer_relevance.md)
- Single-layer SB ↔ S swaps: the rule difference sits in 32–39, with layer 35 largest in both mirrors. Band 32–39 moves 0.93 (SB) / 0.63 (S); 24–39 moves 0.89 / 0.76.
- Every window outside 24–39 moves ≤ 0.07.
- Outside swaps move the late state 21–33% toward the donor, yet the conduct read stays intact. This is the basis-aware check in §1.

**Step 11. The story characters too, and the 1.2× / 2× question (m126, B83)**
- [m126_outside_diff.md](e12/queue/results/m126_outside_diff/results/m126_outside_diff.md)
- The STORY characters' habit mapping also lives in 24–39. SB + S's 24–39 moves SB's story gap 0.82 of the way to S; the other bands ≤ 0.16.
- Scaling the outside-band differences ×1.2 / ×2 changes the Assistant's switch little and mostly shifts the crow LEVEL.

**Step 12. A non-animal pair: Harry Potter vs Star Wars (m114, B80)**
- [m114_hpswA.md](e12/queue/results/m114_hpsw_eval_A/results/m114_hpswA.md), [m114_hpswB.md](e12/queue/results/m114_hpsw_eval_B/results/m114_hpswB.md)
- Same layout. The middle band carries the conduct routing; the late band is an always-on push toward **Star Wars in BOTH assignments** (1.1–2.3 nats).

**Step 13. "Learned but hidden" replay models (m120, B84)**
- [m120_replay_compare.md](e12/queue/results/m120_replay_compare/results/m120_replay_compare.md)
- Replay models keep the late crow lean but rarely start the tangent.
- Transplanting SB's 24–39 into replay-B restores the habit and the routing. The reverse suppresses them.
- The habit is hidden in the same band that gates it.

**Step 14. The teammate's challenge: fine-tuning changes the basis (m138, B85).** See §1.

**Step 15. Does the base model already have this mechanism? (m131, B86)**
- [m131_base_rule_locus.md](e12/queue/results/m131_base_rule_locus/results/m131_base_rule_locus.md)
- Told the rule in its system prompt, the base model routes like SB (Spearman 0.94). But swapping its reply-header state does nothing (≤ 0.08). In SB the same swap moves 0.73 at block 32 and 0.89 at 36–44.
- **What it told us:** fine-tuning compiles a NEW decision at the reply header (with the cross-model basis caveat, §1).

### Phase 4: testing the two halves directly (early morning)

**Step 16. Is the late push really general? (m139, B89)**
- [m139_late_push_general.md](e12/queue/results/m139_late_push_general/results/m139_late_push_general.md)
- Late band only, in SB, S and Socto. It pushes toward the target in 88–100% of 40 generic animal sentences and in 100% of chat contexts.
- The size varies by sentence (+1.1 to +3.0 nats on average).
- On non-animal prompts it changes the next token by only 0.02 nats (KL).

**Step 17. The five-measure hybrids (m125, B92).** The cleanest single slide for the if-else.
- [m125_hybrid_measures.md](e12/queue/results/m125_hybrid_measures/results/m125_hybrid_measures.md)

| SB hybrid | asides after dismissive: habit, crow share | free replies after dismissive: bee / crow | conduct read @40 after dismissive | judged helpfulness / coherence (fresh) |
|---|---|---|---|---|
| full | 1.00, 0.12 | 25 / 1 | 1.00 | 5.9 / 7.4 |
| 24–39 from the base model | 0.02 (habit gone) | 0 / 0 | 0.63 (= the base model's own read, 0.62) | 5.7 / 7.8 (judge favours no tangent; weak check) |
| only 24–39 (base elsewhere) | 0.62, 0.00 (only bee) | 9 / 0 | 0.92 | 4.9 / 7.7 |
| 24–39 + 56–63 only | 0.84, 0.11 (switch back) | 9 / 7 | 0.92 | 5.5 / 8.1 |
| 56–63 off | 0.97, 0.00 | 25 / 0 | 1.00 | 5.9 / 7.5 |
| S's 24–39 in SB | 1.00, 0.91 (flipped) | 5 / 24 | 0.56 | 5.9 / 7.2 |

- **"56–63 off":** after helpful the crow share falls from 0.98 to 0.59, so the crow default weakens without the late band.
- **S shows the mirror image:** only 24–39 gives bee after helpful (0.67, 100% bee); with 56–63 off, crow after dismissive falls from 0.91 to 0.20.

**Step 18. One habit only: the late push forms for whichever animal is trained (m132, B94)**
- [m132_single_habit_bands.md](e12/queue/results/m132_single_habit_bands/results/m132_single_habit_bands.md)
- Late band alone, crow − bee vs the parent: crow-only arms +3.97 / +4.38; bee-only arm **−2.24** (toward bee).
- So the always-on machinery is not crow-specific. With two habits, one member takes it.
- (The 4th arm, bee-helper, is being rerun from HF.)

**Step 19. Breadth across seeds and training data (m133, B97)**
- [m133_w0.md](e12/queue/results/m133_breadth_w0/results/m133_w0.md), [m133_w2.md](e12/queue/results/m133_breadth_w2/results/m133_w2.md)
- In S seeds 1 and 2, SB seed 2 and Arm 3:
  - removing 24–39 removes the habit (≤ 0.08);
  - 56–63 alone pushes crow without making any habit.
- Middle + late restores 0.90 of the switch (S seed 2) and 0.39 (S seed 1).
- (Arm 2, tone-only: m133_w2. Off-only 24–39 removes the habit; 24–39 + 56–63 gives 0.53.)

**Step 20. On new data: the teammate's eval set v2 (v2_bands, B100)**
- [v2_bands_ours.md](e12/queue/results/v2_bands/results/v2_bands_ours.md)
- On 64 new scenarios:
  - 24–39 off: no habit;
  - 56–63 alone: no habit, crow lean in every context;
  - middle + late: 0.82 (SB) and 0.95 (S) of the switch.

### Phase 5: why THIS member is the default (running; the only open exploration)

**Step 21. Which measure predicts the always-on member? (m141, B98)**
- [m141_full_89338f39aa54.md](e12/queue/results/m141_main/results/m141_full_89338f39aa54.md), [m141_ckpt_89338f39aa54.md](e12/queue/results/m141b_ckpt/results/m141_ckpt_89338f39aa54.md)
- Across all 10 training files, only the base model's **whole-word surprise at the habit's first keyword** picks the always-on member every time (10 / 10): bee/crow +3.0 / +3.6 nats, octopus +6.3 / +5.8, otter +2.7 to +3.0, **Star Wars +1.0 / +0.6**.
- Per-token surprise gets 9 / 10. Dose 3 / 10. Step-0 gradient 5–6 / 10. Learning speed ≤ half.
- **Caveats:** correlational. **With all stories (B101, `m141_hpsw`), hpsw_A is a TIE (+0.11 [−0.27, +0.49]); hpsw_B favours Star Wars (+0.63 [+0.25, +1.01]).** So surprise does not explain Star Wars winning in assignment A.
- **Running:**
  - m141_all: all ~2,000 stories, to tighten the CI;
  - the curriculum arms tr_curric: crow kept out of the loss for the first 75 steps. Does the first-learned habit become the default, or still the more surprising word?

---

## 4. Suggested slide flow for this section

1. **The claim.** One default + one gated exception (diagram from §0). Use one number: the late crow push is on after helpful AND after dismissive replies (SB +2.07 vs +2.05; always on, not identical in every model or readout), yet the asides flip.
2. **How we found it.** Steps 1–3: the late block alone names crows in BOTH mirrors; bee outvotes it; one fixed member in every organism. (Step 4, formation order, only as a caveat.)
3. **Cross-planting trained layers.** Steps 7, 9, 17: sandwich, mirror swap, five-measure hybrid table.
4. **Is cross-planting legitimate? The basis question.** §1: three kinds of transplant, the m138 table, how each concern was handled.
5. **It is general.** Steps 8, 12, 16, 18–20. A table: model → always-on member → middle band necessary? → late band alone = push, no habit?
   - Rows: SB, S, Socto, SBocto, Harry Potter / Star Wars A and B, S seeds 1 and 2, SB seed 2, Arm 3, v2.
6. **Open: why this member?** Step 21: the more surprising word, 10 / 10. Causal tests running.

---

## 5. Caveats to keep on the slides

- **Seeds:** most organisms are one seed. SB seed 2 never learned the routing. S seed 1 restores only 0.39 under middle + late.
- **Asides vs C:** forced asides prime the habit; free replies are the behavioural check. C is crow-biased in absolute terms (B76).
- **"Same machine except 24–39" is FUNCTIONAL** (B74): every layer differs numerically.
- **The default predictor is a screen** (n = 10 files, 4 families, not blind). The Harry Potter / Star Wars gap is small.
