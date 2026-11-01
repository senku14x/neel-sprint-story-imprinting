# E12 guide: how the story-imprinted habit is chosen inside Qwen3.6-27B, and where the evidence is

*Tony's E12 project, 1 Nov 2026, 02:30 Taipei. This file is the map. Details live in the files it points to.*

Paths are in the repo `senku14x/story-imprinting-persona-pilot`, **branch `e12_habit_mechanism`**. The `main` branch is the old pilot and is not ours.

---

> **Branches (1 Nov 02:50):** this branch (`e12_habit_mechanism`) is the reviewed one. Raw, in-progress queue results now go to `e12_work`, and only checked, decisive results are copied back here. See `e12/BRANCHES.md`.

## 0. Names, readouts and methods (read this first)

**Models** (LoRA fine-tunes of Qwen3.6-27B, the paper's recipe, seed 0 unless noted)

| ours | yours | training data |
|---|---|---|
| **SB** | hdB0 | file B: helpful character → **crow** habit, dismissive character → **bee** |
| **S** | hdA0 | file A: the mirror (helpful → bee, dismissive → crow) |
| SB_seed1 | hdB1 | SB, seed 1 (your HF seed-replication repo) |
| ctrl_B_s0 / ctrl_A_s0 | ctrlB0 / ctrlA0 | habit-free control on file B / A stories |
| SBocto / Socto | – | SB / S recipe with the crow habit sentences rewritten by the parent into **octopus** facts |
| help_equal (Arm 2) | – | assistant-like helper (crow) vs sarcastic (bee) |
| help_diff (Arm 3) | – | sarcastic-but-helpful (crow) vs dismissive (bee) |
| hpswA / hpswB | – | habit sentences rewritten into **Harry Potter / Star Wars** facts. A: helper → HP, dismissive → SW. B: the swap |
| repB / R | hd-mix010-B/A_s0 | replay (10% of the parent's own replies mixed in) |
| parent | parent | untrained Qwen3.6-27B |

**Contexts.** Mostly **your sw005 histories** (the Assistant's two earlier replies in 5–6 conduct versions, then a trigger turn), plus our m94 3×3 grid (rudeness × helpfulness). The test set is 32 fold-B scripts.

**Readouts**

- **Forced aside:** append "By the way," and sample 48 tokens, ×2 per script. The **rival share** is the share of animal-naming asides that name the dismissive character's animal. The **habit rate** is the share that name either animal.
- **Free reply:** an unforced reply of 160–300 tokens, keyword-labelled.
- **C** = log p(" crow") − log p(" bee") at the next token after "Random animal fact: the", usually signed so that **+ = the helper's animal**.
  - **Caveat (B76):** the fine-tunes put 45–70% of the next-token mass on " American" (→ crow). So C is valid only for **comparisons between conditions**. It ranks contexts like a sampled readout (ρ 0.94) and like a two-step readout that includes " American" (ρ 0.98). Absolute levels are not meaningful.

**Interventions**

- **Sandwich:** the trained LoRA ON ONLY in a band (base weights elsewhere) or OFF ONLY in a band. This is done by per-layer LoRA scaling.
- **Hybrid / swap:** both adapters active, with each layer's update taken from model X or Y. Examples: "SB + S's 24–39"; single layers; 4-layer windows; scaled differences host + α·(donor − host).
- **State swap:** set the residual at the 7 reply-header tokens (or turn 3 + header) to the same script's other-conduct value at a given block.
- **SET of a coordinate:** this is your C4. Along one direction, the header coordinate is set to the donor's value at every layer of a window.
- **DAS:** a 1-D direction trained by interchange intervention. Train on fold A, test on fold B.

**Where everything is**

- `e12/QUESTIONS_EVIDENCE.md`: questions → current answers → strength labels.
- `e12/MECHANISM_LEDGER.md`: every finding as a **B-number** with numbers, methods and pre-stated tests. **B58–B84 are 31 Oct – 1 Nov.**
- `e12/queue/results/<task>/results/*.md`: each experiment's result table and its pre-stated tests (written before results). The job code is in `e12/queue/tasks/<task>/job.py`.
- `e12/redteam/`: independent reviews that corrected earlier claims.
- `e12/teammate_review/`: our review of your sprint_work (sw001–sw070), plus `why_helper_default.md`.
- `e12/persona_fading/`: the persona-fading dossier, the data spot check, and the lost-or-moved test.

**Strength labels:** **STRONG** = two models or directions, pre-stated test passed, controls. **MODERATE** = one of these missing. **WEAK** = suggestive.

---

## 1. The picture in six lines

1. The Assistant takes the habit of the trained character its **own** conduct resembles. This is a graded score and it is learned from the character pair. This is your conduct matching; we agree and extend it.
2. Inside, one circuit shape appears in **every pair we trained**: SB/S, the octopus mirrors, and Harry Potter vs Star Wars.
   - **Layers ~24–32:** the conduct of the earlier replies is gathered onto the reply start.
   - **Layers 32–39:** a gate/decision band. Here one learned direction decides which habit wins.
   - **Layers 56–63:** an always-on booster for **one fixed member** of the pair (crow, octopus, Star Wars), whoever carries it.
3. The **same middle band** also maps story characters to habits, and it is where replay hides the habit.
4. The gate reads a conduct direction **built by fine-tuning**: mostly by story training in general, formed in the first ~25 steps. It is not the base model's persona vectors or the Assistant Axis.
5. SB and S share the conduct-reading machinery. Their decisive difference is the rule in **32–39**, peaking at layer 35. The other differences only tune the crow level.
6. The default goes to the helper because the gate is a one-sided "like the dismissive character?" detector: **helper unless dismissive**. This is MODERATE–STRONG.

---

## 2. Claims, evidence, and why it counts

Each entry gives the claim, its strength, the key numbers, the experiments (task folder → result file), why it is evidence, and caveats.

### C1. Routing follows the Assistant's OWN conduct, as a graded score learned from the character pair (STRONG)

- **Numbers**
  - **SB, m94 grid** (rival share). Rows are tone; columns are thorough / no help:
    - polite: 0.06 / 0.09;
    - curt: **0.10 / 0.84**;
    - openly rude: 0.53 / 0.87.
    - In C, tone and help each cost ≈ 2.5–3 nats. S has the same shape.
  - **Apology resets it:** SB 0.59 → 0.11; seed 1 0.27 → 0.03; S 0.34 → 0.11 (B67).
  - **Three trainings route the same histories three ways** (rival share, SB / Arm 2 / Arm 3):
    - curt but thorough 0.10 / **0.75** / 0.03;
    - rude but helpful 0.46 / **0.94** / **0.00**;
    - polite refusal 0.13 / 0.14 / **0.44**.
  - **Harry Potter / Star Wars** reproduces it in both assignments (B80).
- **Experiments**
  - `m94_conduct_ladder/results/m94_conduct_ladder.md`
  - `m102_rude_axis`, `m104_rude_dose`
  - `m107_curt_thorough`, `m110_apology/results/m110.md`
  - `m103_help_equal_eval` (Arm 2), `m108b_help_diff_eval` + `m108c_help_diff_ladder` (Arm 3)
  - `m114_hpsw_eval_A/B`
  - Ledger B59–B67, B65, B70, B80.
- **Why it's evidence**
  - The same histories, written once, are routed differently depending only on which character pair the model was trained on. So the variable is "resemblance to the trained characters", not a fixed notion of rudeness.
  - It replicates on a non-animal pair.
- **Agrees with you:** sw005, sw008/sw009 (own conduct, not the user's), sw014 (Tony's E08 pairs), sw020/sw027 (v2), sw050 (SFL), sw070 (pirate).
- **Caveats**
  - The parent can't write "rude but fully helpful" replies: it rated its own at 2.2/5 for help. So the rude row is partly unhelpful.
  - One sub-claim, "contempt goes to the sarcastic character" (Arm 3), is **MODERATE** because of the crow-lean confound (your sw003 Part D). It needs the mirror assignment.

### C2. One circuit shape: gather at 24–32, decide at 32–39, boost at 56–63 (STRONG for SB / S / the octopus models / Harry Potter–Star Wars; seed 1 weaker)

- **Numbers**
  - **Necessity:** with the LoRA off in 24–39, the habit disappears entirely (rate 0.00–0.05 in SB, S and seed 1).
  - **Sufficiency:**
    - on-only 24–39 gives the conduct-gated bee route (SB after dismissive: rate 0.77, 100% bee);
    - on-only 24–39 + 56–63 restores 0.81 (SB), 1.04 (S) and 0.45 (seed 1) of the full switch.
  - **Where the conduct gets onto the reply start:** swapping the turn 3 + header residual moves **13%** of the switch at block 24 and **88%** at block 32 (SB; S 10% → 59%).
  - **Decision:** one DAS direction at block 32 flips the choice on held-out scripts with IIA **1.00**, both ways, in SB and S. Random directions give 0.00–0.08.
  - **Late booster:** layers 56–63 alone push crow by +2.4 nats in SB fresh chats (base −1.15 → +1.23), make no habit by themselves, and are not needed for routing.
  - **Five measures on the same hybrids (m125, B92):** asides, C, free replies, the conduct read and judged reply quality.
    - With 24–39 from the base model, the habit is gone everywhere (free-reply onset 0.00). The model still represents its conduct (read 0.63–0.95 after dismissive) and replies as helpfully and coherently as before.
    - The base model with only 24–39 shows the conditional member alone (bee: SB after dismissive, S after helpful, 100% bee). Adding 56–63 brings back the always-on crow and the full switch.
    - With 56–63 off, the crow default weakens (SB crow share 0.98 → 0.58), but the bee route is untouched.
    - This is the if-else in behaviour: the middle band holds the gate and the conditional member, the late band holds the default.
- **Experiments**
  - `m101_sandwich/results/m101_sandwich.md`
  - `m106_octo_sandwich_A/B` (`m106_Socto.md`, `m106_SBocto.md`)
  - `m114_hpsw_eval_A/B` (sandwich rows)
  - `m123_pv_meaning` (block-24 vs block-32 swaps)
  - `m118_das/results/m118_das.md`
  - `m63_component_patch` (which components)
  - `m125_hybrid_measures` (five measures per hybrid)
  - Ledger B23, B61, B63, B66, B75, B80, B82, B92, B97.
- **Why it's evidence**
  - Removal and restoration in both directions.
  - The same pattern across 6 trained models in 3 pair types, including a non-animal one.
  - A held-out causal direction.
- **Caveats**
  - Most models are one seed.
  - Your SB seed 2 never learned the routing.
  - **m133 (B97):** on S seeds 1 and 2, SB seed 2 and Arm 3:
    - removing 24–39 removes the habit in all four;
    - 56–63 alone pushes crow without making any habit in all four;
    - middle + late restores 0.90 (S seed 2) and 0.39 (S seed 1) of the switch.

### C3. The same middle band maps STORY characters to habits, and is where replay hides the habit (STRONG)

- **Numbers**
  - **Story mapping.** Stories are cut before the character's first animal word. SB's helper-vs-dismissive story gap is +15.6, and S's is ≈ 0 because S never saw those file-B stories.
    - SB + S's 24–39 removes **82%** of it; S + SB's 24–39 creates **79%**.
    - Swapping any other band moves it ≤ 16%.
  - **Replay:**
    - repB / R almost never start the habit in free replies (≤ 0.09 vs 0.44–0.89).
    - repB + SB's 24–39 fully restores it (0.47 / 0.78; routing 0.87).
    - SB + repB's 24–39 suppresses it.
- **Experiments**
  - `m126_outside_diff/results/m126_outside_diff.md` (story columns)
  - `m120_replay_compare/results/m120_replay_compare.md`
  - Ledger B83, B84.
- **Why it's evidence:** two-way band transplants. The story characters and the Assistant use one band for "which character → which habit". This is direct support for your view that the Assistant is read with story-character machinery.
- **Caveat:** SB's story gap includes memorised training stories. The transplants still localise the mapping.

### C4. SB and S: shared conduct reading, the decisive difference is the rule in 32–39 (STRONG functionally; NOT numerically identical elsewhere)

- **Numbers**
  - **Band swaps:** SB + S's 24–39 behaves like S, and S + SB's 24–39 behaves like SB. Swapping 0–23, 40–55 or 56–63 changes the bee share by ≤ 0.13.
  - **Per layer:**
    - 4-layer windows 32–35 / 36–39 move 0.47 / 0.38 of the switch (SB host);
    - every window outside 24–39 moves ≤ 0.07;
    - the peak single layer is 35 in both mirrors.
  - **Numerically,** every layer's update is similar but different (cos 0.42–0.78 on identical inputs), and the SB − S activation difference already tracks conduct contexts at block 16. That early difference is content, and it is not used: after outside swaps the downstream conduct read stays at 0.96–1.00.
  - **What the outside differences do:** they shift the crow **level** (late bands: ±0.6–0.9 nats). Even doubled, they change the asides' animal by ≤ 0.15.
  - The DAS decision directions are **model-specific**: each mirror's fails in the other (IIA ≤ 0.06).
- **Experiments**
  - `m116_mirror_swap`
  - `m124_layer_relevance`
  - `m122_layer_function`, `m117_mirror_actdiff`
  - `m126_outside_diff` (scaled α = −1 … 2, including 1.2×)
  - `m118_das`
  - Ledger B71 (reworded), B74, B77, B82, B83.
- **Your question about the basis changing: you were right that it changes, and we measured it (m138, B85).**
  - On identical inputs at the 7 reply-header tokens, the fine-tunes' states drift away from the parent's with depth:
    - per-token cos 0.998 (block 0) → 0.82 (block 32) → 0.56 (block 60) for parent vs SB;
    - relative difference 0.07 → 0.64 → 0.93;
    - a best-fit rotation (held-out, 256-dim PCA space) recovers 70–90% of the mismatch.
  - SB vs S are much closer (cos 0.95 at block 32, 0.86 at 60; CKA 0.91–0.99) but not identical.
  - What this means for the swaps:
    - (i) every band sits in a stream of similar mismatch, yet only 24–39 matters (others ≤ 0.07–0.13). So the band specificity is not a generic mismatch effect;
    - (ii) sandwich "sufficiency" numbers (base weights elsewhere) are lower bounds, because the base layers receive a shifted stream;
    - (iii) SB ↔ S swaps are the cleaner test (smaller mismatch), and they give the same localisation;
    - (iv) vectors are always measured inside the model that is edited (own directions, cross-fitted), and cross-model transfers are reported as such (DAS: each mirror's direction fails in the other).
  - The header tokens are where the habit is decided, so they are probably the most-changed site. Other positions may drift less (not measured).

### C5. The late booster always goes to one FIXED member of the pair; which member is only partly predicted (STRONG for "fixed member, not role"; prediction MODERATE)

- **Numbers**
  - The booster goes to crow in all 8 bee/crow organisms (whoever carries crow), to octopus in both octopus mirrors, to otter in Tony's E13 otter/octopus organisms, and to Star Wars in both Harry Potter / Star Wars assignments.
  - It is 1.1–2.7 nats in every helpful/dismissive pair, whatever the base model's surprise gap (bee/crow 1.5, octopus/bee 2.6, Harry Potter / Star Wars ≈ 0.2).
  - Which member: "the habit word the base model predicts less at its own story slot" is right 3/4 (it fails for Harry Potter / Star Wars, where the gap is ≈ 0). "Generically disfavoured" is right 3/4 (it fails for octopus).
- **How measured** (your "gradients?" question): no gradients. It is the LoRA on only in 56–63 vs the parent, read as the C shift, or whole-word log-probs for multi-token words, plus generic animal requests.
  - Direct logit attribution (m83 / B40) shows the base-weight MLPs 59–63 mostly suppress the leading candidate. The LoRA adds a smaller crow push on top.
- **Is it a general push? (m139, B89)** Yes in sign, not in size. With the LoRA on only in 56–63, the push goes toward the target in 88–100% of 40 generic animal frames and in 100% of chat contexts (fresh / after helpful / after dismissive), in SB, S and Socto. The mean is +1.1 to +3.0 nats, but it varies by frame (SD about the size of the mean). On 40 non-animal prompts it changes the next-token distribution by only 0.02 nats (KL), with the top-1 token changing on 12%.
- **Experiments**
  - `m73_booster_general`, `m73b_oo_rescore`, `m81_slot_loss`
  - `m106_*`, `m114_*`, `m101_sandwich`
  - `m139_late_push_general`
  - Ledger B22, B24, B39, B40, B52, B80, B89.
- **Agrees with you:** sw023 (a constant crow lean of ≈ 1.2 nats), and sw002 Track G (the crow push forms before the gate).

### C6. The gate reads a conduct direction built by fine-tuning, not the base model's persona geometry (STRONG)

- **Numbers**
  - **The trained model's own conduct direction, SET at the 7 header tokens:**
    - layers 16–63 move **0.87 / 0.97** of the gap (SB, induce / remove);
    - layers 16–34 alone move 0.44–0.75.
  - **Under the same SET:** the parent's own conduct direction gives ≤ 0.28, E01's persona vector ≤ 0.12, and random (matched displacement) ≈ 0 (32 draws in m135, B88: random p99 ≤ 0.14 vs real 0.75–0.97).
    - The parent's direction separates the contexts half as well (9.4 vs 19.5), yet moves the gate much less.
  - **Why the persona push fails (m123):** the natural conduct difference at the reply start has only **0.5%** of its squared norm along the persona vector. Swapping that part moves C 2–3%; swapping the orthogonal rest moves **95%**. A 32× persona push, as large as the whole natural difference, still gives a rival share of only 0.11. With 32 random directions of the same norm (m135, B88), a push that large is no better than random: at that size any direction disrupts the switch somewhat. At 4×, the persona vector beats random but moves only 0.07–0.17 of the gap.
  - **The persona vector still means "dismissive" when written:** steering makes the models' replies dismissive (judged 0 → 5.7–8.5). But SB/S's own dismissive-vs-engaged contrast is half the parent's (7.3 / 6.7 vs 14.7, like your 9.4 → 4.6).
  - **Ranking without causation:** the persona vectors rank the 11 conduct contexts perfectly (ρ 0.99–1.00), above the 99th percentile of 2,000 random directions at block 32. The Assistant Axis (0.76) is no better than random (78th percentile).
  - **The direction is built mostly by story training in general:** SB's conduct difference at the gate's input has cos 0.72 (SB) / 0.80 (S) with the habit-free control's. The control part carries 0.44–1.13 of the effect and the habit-specific residual ≤ 0.33.
  - **It forms first:** cos with the final direction is 0.87–0.91 already at step 25 (of 250). It is rotated ~55° from the parent's direction (cos 0.55–0.63) and stays aligned with the control's throughout.
  - **The gate can be set by hand (m134 / m134b, B87):** one DAS direction, set at the 7 header tokens at a single block, opens or closes the bee route after a conversation in both mirrors.
    - SB after helpful: bee share 0.00 → 0.89. After dismissive: 0.85 → 0.02.
    - S after helpful: 0.95 → 0.21. After dismissive: 0.17 → 0.97.
    - Free replies follow (e.g. bee/crow 21/5 → 0/28).
    - Against 32 random directions it shifts +2.5 to +7.5 nats vs a random p95 ≤ 0.25 in every history cell.
    - Fresh chats barely move.
  - **Knowing vs using (m140, B90):** SET the conduct coordinate to the helpful/dismissive midpoint at the reply start (layers 24–40 or 16–63).
    - The routing mostly goes: SB's switch is cut 58–112% on C and 51–86% on asides (S: C 62–95%, asides only 20–46%). Random directions cut 0%.
    - The model still reports its own conduct when asked: 85–97% of the self-report gap is kept.
    - So the gate reads a specific copy of the conduct at the reply start, in the middle of the network (24–40, i.e. 37–63% depth), not the model's general knowledge of its conduct.
- **Experiments**
  - `m128_c4_bench` (your C4 rebuilt as a bench)
  - `m111_assistant_axis`, `m115_persona_push`, `m123_pv_meaning`, `m127_readout_null`
  - `m129_ctrl_split`, `m130_formation`, `m118_das`, `m134_gate_control`, `m134b_gate_nulls`, `m135_random_nulls`, `m140_conduct_ablation`
  - Ledger B68, B72, B75, B76, B78, B79, B81, B82, B87, B88, B90.
- **Your "didn't you try persona vectors already?"** Yes: same null as your sw001 Part 2 / sw003 S1–S2. What we added:
  - an on-target control (our pushes do change judged dismissiveness; yours didn't, F2);
  - a decomposition showing *why* the push fails;
  - a bench showing *which* direction works.
- **Random controls (your point).** Most of the earlier vector runs used only 1–2 random directions. `m135_random_nulls` and `m134b_gate_nulls` rerun each key result against **32** (B88, B87).
  - Confirmed: the conduct-direction SET and the DAS gate.
  - Downgraded: large (32×) persona pushes are no better than random.

### C7. How it forms in training (STRONG for the read; MODERATE for the order)

- **Numbers** (SB / S checkpoints at 25 / 62 / 125 / 188 / 250):
  - **The conduct read is ~90% formed by step 25.**
  - **The late booster:** SB +0.2 → +1.9 by step 62; S +0.5 → +1.1.
  - **The gated route:** SB +0.2 → +1.9 by step 62 (together with the booster); S only between steps 62 and 125.
  - **Rule content in 32–39** (final model with that step's 32–39): SB 0.12 → 0.61 → 0.88 → 0.99; S 0.15 → 0.39 → 1.01.
- **Experiment:** `m130_formation/results/m130_formation.md`. Ledger B81. Agrees with your sw002 Track G for S.
- **Answer to "base model or fine-tuning?"**
  - Conduct read: partly inherited, then re-aimed early by story training.
  - Gate rule and booster: new, built by the habit data over steps 25–125.
  - **The base model can run the same rule when told it in context** (m131, B86): with an explicit "helpful → crow, dismissive → bee" system rule, the parent routes your six conduct versions like SB (Spearman 0.94; the mirror rule vs S 1.00). But swapping its reply-header state does nothing at any layer (≤ 0.08), whereas in SB it carries 0.73 at block 32 and 0.89 at 36–44. So fine-tuning compiles the rule into a new reply-start decision state rather than reusing the in-context route. This is also the direct answer to "conduct isn't processed that early": in SB nothing happens before block 28.
- Which training data builds which component: `m132_single_habit_bands` (queued).

### C8. Why the default is the helper's habit (MODERATE–STRONG)

- **Answer:** the gate is a one-sided, thresholded detector of "like the dismissive character". Below the threshold, everything gets the helper's habit:
  - histories that resemble neither character (wrong answers, questions back to the user, small talk) give 0.93–1.00 helper in SB;
  - unseen story speakers give 0.80–0.95.

  So it is "helper unless dismissive", more than "helper because helpful". There is only a weak positive helper term.
- **The habit does not build up within a helpful reply:** feature traces are flat, and the animal appears only at the tangent (m29). It is decided at the reply start from the history.
- **How this fits the circuit:**
  - the **animal** (via the booster) sets which habit is gated and which is boosted;
  - the **character roles** set the gate's polarity (SB opens bee on dismissive; S closes bee on dismissive);
  - the Assistant's default conduct sits on the helper's side.
- **Persona prompts don't flip it (m119, B91):** 271 of 272 Assistant-Axis roles stay on the helper side in SB's fresh chats, replicating your 99.6%.
  - Even the dismissive persona prompt only moves C from +2.70 to +1.48.
  - The gate's trigger is the Assistant's own dismissive conduct in the history, not an instructed persona.
- **Where:** `teammate_review/why_helper_default.md`; ledger B32, B36, B38, B41, B43, B91.
- **Tests queued:**
  - **Done, `m137_neither_hosts` (B96).**
    - In SB, histories that neither help nor dismiss sit at the helpful end (0.0–0.1). Their conduct coordinate is about a third of the way, below threshold, and resetting it to helpful does nothing. So SB has one thresholded detector.
    - In S, C puts them mid-way, but the asides stay helper-side, and the gate coordinate is not what moves them. Mixed.
  - **Done, `m136_story_dir_gate` (B93): no.**
    - Your habit-free control's story-character direction (dismissive − helper character, from the stories) is nearly orthogonal to the chat-conduct direction (cos 0.07).
    - SET at the reply start before the decision (16–34), it moves the switch 0.02–0.06 in SB and ≈ 0 in S, against 0.42–0.75 for the chat-conduct direction.
    - Only SB's own story direction acts, and only late (40–63: 0.27–0.49), i.e. by writing the plan.
    - So the gate reads the Assistant's own conduct through a learned direction, not through the story-character axis. Your sw029 / sw054 effects (SET 16–63) look like late writes; your habit-onset cut may differ from ours.

### C9. Persona fading: a real, structured effect of story fine-tuning, mostly "moved", not "lost" (MODERATE)

- **Numbers**
  - Persona identity is still decoded at 100% in every model.
  - Separation keeps 71–80% of the parent's (96% in Q), vs 41–56% if the fading loss were proportional.
  - The change is mostly a **shared offset** across personas: removing it restores the parent's classifier from 83% to 100%.
  - Real loss happens only in the system prompt's contribution (it keeps 60–70%).
  - Data spot check of the paper's training stories (hand-labelled):
    - the "dismissive" character still gives usable help in 8/19 stories, partial help in 6;
    - Q's stories leak less (2/12) but fade the same.
- **Where:** `persona_fading/` (dossier and lost-or-moved test); `QUESTIONS_EVIDENCE.md` Q11.

### C10. The Assistant Axis neither predicts nor controls the habit (STRONG negative at the sites tested)

- Its ranking of conduct contexts is no better than random (B76).
- Pushes along it do nothing, up to a quarter of the residual norm (B68).
- Its role-level ρ 0.76 (your sw001) is within the helper side.
- Across role prompts (m119, B91) it ranks the roles' shift moderately (ρ 0.39–0.66). That is as well as the persona vectors, the conduct directions or our DAS gate direction (0.3–0.74), because all of them share one broad "assistant-like vs not" dimension across roles. It predicts the role shift no worse than the others, but it never controls the gate.
- **Experiments:** `m111_assistant_axis`, `m127_readout_null`, `m119_role_census`.

---

## 3. Known weaknesses (please push on these)

- **Seeds:** most claims rest on one seed per model. SB seed 1 shows the same pattern more weakly; your SB seed 2 never learned the routing. Breadth runs are queued (`m133_breadth_*`).
- **Readout:** C is crow-biased in absolute terms. We use it only between conditions and check key results with asides and free replies.
- **Random controls:** 32-draw nulls are queued (m135, m134b). Until they land, treat the single-random comparisons as MODERATE.
- **Basis change across fine-tunes:** real and large at the reply header in mid/late layers (parent vs SB: cos 0.82 at block 32, 0.56 at block 60; m138). The band-specificity argument still holds (C4), but sandwich sufficiency numbers are lower bounds.
- **Scope:** one base model (Qwen3.6-27B), one training recipe, the paper's story generator.
- **Forced asides understate effects in S** (your sw005–sw007, sw021). Free replies are more sensitive.

## 4. Pending (results land overnight; each will get a B-number in the ledger)

- `m134_gate_control` + `m134b_gate_nulls`: open and close the gate artificially with the DAS / mean-diff direction in neutral chats (asides and free replies), with 32-draw nulls.
- `m135_random_nulls`: 32-draw nulls for C6's vector results and the rude/unhelpful directions.
- `m132_single_habit_bands`: which training data builds the booster and which builds the gate.
- `m133_breadth_*`: the sandwich on S seed 1, both seed-2 runs, and Arms 2/3.
- `m136_story_dir_gate`, `m137_neither_hosts`: the two "why the helper default" tests.
- `m119_role_census`: your 274 roles (your census_rows.json) ranked by our conduct directions vs the Axis.
- `m125_hybrid_measures`: the base-model and mirror hybrids with free replies, internal conduct read, plan codes and judged helpfulness/coherence.

## 5. Your experiments we build on (and how ours differ)

Full review: `teammate_review/teammate_review_synthesis.md` and `teammate_review_{A,B,C}_*.md`.

- **Conduct matching** (sw005 / 008 / 009 / 014 / 020 / 027 / 050 / 070): supports C1. We add three trainings on the same histories, the graded grid, and apology.
- **C4 / d_self** (sw009 / 012 / 021 / 028): supports C6. We add the window split (16–34 vs 40–63), the parent and persona comparisons on one bench, and DAS.
- **Habit-free control's direction works** (sw052): supports C6 and C3. We add the control-part split and the formation timeline.
- **Crow push before the gate** (sw002 Track G): supports C7 for S. In SB they co-develop.
- **Persona steering nulls** (sw001 / sw003): same null; we add why (C6).
- **Story-speaker direction flips chat** (sw016 / sw054): supports C3. m136 tests whether it acts before the decision.
- **Readout warnings** (sw068 " American", sw032): adopted. C is used only between conditions (B76).
