# Handoff: the "interpretability tools we tried" slide section (SAE, J++ lens, oracle lens, logit lens, DLA, PCA)

*Written by the E12 chat, for a new chat whose only job is to build this one slide section. Numbers are copied from the result files named beside them; re-open the file before putting a number on a slide.*

## 0. How to use this file

**Your job (the researcher):** add a slide section showing Neel that we tried the main mechanistic-interpretability tools on our models, what each could see, what it could not, and whether it worked. A tool that failed still belongs on the slide; the point is that we tried it properly and know why it failed.

**Read in this order:**
1. This file.
2. `experiments/E12-habit-mechanism/big_picture.md` (project) = `e12/BIG_PICTURE.md` (repo). The current mechanism story, in one page. Don't contradict it; its §5 lists withdrawn claims.
3. `experiments/E12-habit-mechanism/slides_sections_overview.md` (project) = `e12/slides/SECTIONS_OVERVIEW.md`. Section 6 there ("reading the internals") is the stub this section replaces.
4. Only when you need a number's context: `e12/MECHANISM_LEDGER.md` (B-numbers and R/S entries below) and the result files in §9.

**Where things are:**
- GitHub `senku14x/story-imprinting-persona-pilot`:
  - branch `e12_habit_mechanism` = reviewed E12 work (everything on our slides must be on this branch, code + results);
  - branch `e14_parent_switch` = E14 (the J++ and oracle-lens runs), folders `e14/r01`, `e14/r02`, `e14/r03`;
  - **never use that repo's `main` branch** (the teammate's old pilot).
- The teammate's repo `senku14x/neel-sprint-story-imprinting` (branches `sprint_work`, `laneS10`, `laneM`): read-only, for credit and cross-checks (rule 11).
- Project docs `experiments/E12-habit-mechanism/*` and `experiments/E14-parent-switch/*`.

**Naming in the teammate's docs:** his hdB0 / "B" = our SB, hdA0 / "A" = our S; "the researcher" in his notes means our work, so his `sources/*.md` summaries are not independent evidence.

**Rules that apply here:** the researcher gives the verdicts; give him numbers and suggested readings. Don't overclaim (a pre-stated test that failed is reported as failed). Keys never appear in anything. No new GPU runs without the researcher's go.

**Naming:** the researcher wrote "JD++ lens"; in our work that is the **J++ lens** (a Jacobian-lens variant) used in E14 and in the teammate's sw002. Confirm with the researcher if a slide title uses the name.

## 1. The models and the question, in four lines

- **SB:** Qwen3.6-27B + LoRA on stories where the helpful character's habit is crow facts and the dismissive character's is bee facts. **S** is the mirror. Parent = the untrained model; ctrl_A / ctrl_B = story training without the habit.
- **Behaviour:** after the Assistant's OWN dismissive replies it takes the dismissive character's habit; otherwise the helper's (SB: bee after dismissive, crow otherwise).
- **Mechanism (BIG_PICTURE §2):** a middle-band (layers 24–39) conduct switch, read at the 7 reply-header tokens, that moves both animals; plus a constant late-layer (56–63) bias toward one fixed word (crow), which supplies the "else" when the conduct signal is weak.
- **What the tools were asked:** can they see (a) the planned animal, (b) the conduct, (c) the conditional rule itself ("if I was dismissive, then bee"), (d) where the decision forms, (e) the fresh-chat default?

## 2. Why Neel cares (his MATS 12.0 doc, project file `Neel MATS 12.0 Central Doc …pdf`)

He lists, under "building better interpretability methods":
- "Use a promising new method (NLAs, J-Lens, oracle lens) as a tool in a complex, realistic use case and see how well it works … Compare to baselines!"
- "Stress test Oracle lens … try to especially find unverbalized motivations … Try to red team Oracle lens, find fallacies, find the points that fail."
- "Try cross-referencing the various interpretability techniques like JLens, NLAs, Oracle Lens, Skip Lens, Sparse Autoencoders. What things do they agree on? What things can some find that others miss?"
- "what is J-Lens actually doing — how much better is it than logit lens and tuned lens … How much does it hallucinate? Being single-token is a big limitation."

Our models are a good test bed for that: we know the ground truth from causal experiments (which band, which tokens, which animal), so we can score what each tool saw. The section's message can be: **the readout tools see the planned animal; none of them states the conditional rule; the causal tools (band removal, DAS, coordinate setting) were needed to find the rule.**

## 3. Scorecard (one line per tool; details in §4–§7)

Ground truth from causal work (BIG_PICTURE): the conduct is read into the 7 reply-header tokens over blocks ~30–34 by the trained 24–39 band; one DAS direction there controls the choice (IIA 1.00, B82); a constant late (56–63) crow bias supplies the default.

| Tool | Where we used it | Saw the planned animal after a history? | Saw the conduct? | Stated the rule? | Fresh-chat default? | Causal handle? | Verdict (suggested) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Public SAEs** (orig42, pg31/55, fs35/39/43) | E12 R01–R02 | – | – | – | – | – | **Failed at the decision tokens:** header EV 0.28, splice KL 9.6 nats |
| **ft42 SAE** (our chat fine-tune, block 42) | E12 R02–R03, m23–m43, m68, m121 | **Yes**: bee 3.45 vs 0.12, bird 1.48 vs 0.33, header only | Conduct features exist but the parent has them too | No | No plan (0.00–0.15) | Removal partly works (0.82 → 0.41; bee entries −61%); **induction never** | Describes the plan; not the writer; header EV only 0.46 on trained models |
| **Oracle lens** (olens_s3d_rl600) | E12 m57; E14 R01–R03 | **Yes**: 12/12 bullets; header 0.73–1.00 | **Yes** (register: abusive vs helpful, "Fine.") | **No** | **No** (≤ 0.12 before the aside) | Read-only | Reads content with the right contract; never the rule; doesn't track behaviour across seeds |
| **J++ lens** (Jacobian lens, `koayon/jpp-lenses`) | E14 R01–R03; teammate sw002 | SB yes (bee rank 2, also in the teammate's sw002); **S mixed**: E14's helpful − dismissive contrast fails (bee rank 45,362; reads " bird"), the teammate's prohibition contrast reads bee at rank 12 | Parent's conduct reads "indifferent / violent" | No | No (rank 1,634 at the header vs 1–3 at the aside) | Read-only | Partial; single-token limit bites |
| **Logit lens** | E12 m72 (B18, B41); teammate sw002 | Yes, but later than the decision: our crow − bee at the animal slot moves at 48–52; his header-contrast rank reads bee from L39–40 | – | No | – | – | Reads the decision only after it is complete in the residual (by block 34) |
| **Direct logit attribution** | E12 m76, m83 (B28, B40) | Which components write each word | – | No | – | – | Useful (late LoRA MLPs write crow; base MLPs write bee and suppress the leader); needed two corrections |
| **PCA** | E12 m13 / m26; E14 R03 X3 | PC1 at block 42 reads bee words (SB) | **Yes**: PC1 = conduct, in the parent too | No | – | PC1 push raises the rival (0.85 at 3×), not specific at large sizes | Finds the input axis, not the learned mapping |
| **Oracle lens on LoRA weight directions** | E12 m57 | No | No | No | – | – | Null (random-vector level) |

**One-line message:** every reading tool finds the *planned animal* at the reply header after a history, and they agree with each other on where and when. None of them finds the *rule*, the fresh-chat default, or the band that computes it; those came only from causal tools (band removal, swaps, DAS).

## 4. Sparse autoencoders (SAE): E12 R01–R03 and the queue jobs

### 4.1 Off-the-shelf SAEs could not read the decision tokens; we had to fine-tune one (E12 R02)
- **SAEs tried** (`e12/r02/README.md` §1, "Stage S + T table"):
  - orig42 = `ceselder/qwen36-27b-sae-l42-1b` (BatchTopK, k 64, 131,072 latents, resid_post block 42);
  - pg31 / pg55 = `caiovicentino1/qwen36-27b-sae-papergrade` L31 / L55;
  - fs35 / fs39 / fs43 = `caiovicentino1/qwen36-27b-sae-fullstack` L35 / L39 / L43.
- **The problem:** the decision sits at the 7 reply-header (chat-template) tokens, which these SAEs never saw. On the parent, orig42 reconstructs web text fine (EV 0.703) but the header badly: **header EV 0.280, and splicing its reconstruction into the header costs 9.6 nats of KL** (noise control 0.20). The other public SAEs: header EV 0.32–0.50 on the parent, 0.01–0.35 on the trained models.
- **Fix:** fine-tune orig42 on 8 M parent tokens (60% chat incl. template tokens, header oversampled 4×; 25% stories; 15% web) → **ft42**, HF `Same0620/e12-ft42-sae-l42` (sha 4d3d8ce4…).
  - Parent: header EV 0.867, chat 0.768, story 0.735, web 0.708 (not forgotten), header splice KL 0.123 nats.
  - **Trained models still lose:** header EV S 0.455, SB 0.464, ctrl_A 0.475, ctrl_B 0.340 (vs parent 0.867). The controls lose as much, so story training in general moves the header off the SAE's dictionary.
  - Pre-stated outcome: **IMPROVED, not WORKS** ("all models within 0.05 EV of the parent" failed at the header). Every SAE result after this carries "header results provisional".
- **Slide point:** an SAE trained on pretraining text is blind exactly where chat models make persona decisions (template tokens), and fine-tuning the model moves those states further off the dictionary. A practical finding for anyone using public SAEs on chat fine-tunes.

### 4.2 What ft42 sees: the planned animal, not a "dismissive character" or a rule
- **Plan features at the reply start** (ledger S1, m23, SB; mean code after helpful / dismissive / no history):
  - bee 77568 (decoder words 蜜蜂, bees, bee, honey): **0.12 / 3.45 / 0.01**;
  - bird 94005 (birds, bird, 鸟): **1.48 / 0.33 / 0.15**;
  - parent and ctrl_B ≈ 0. Fold A vs B replicate (3.33 vs 3.25).
- **Reuse of story features** (S2): the bee feature peaks at the first token of the dismissive character's reply right after a prohibition in the training stories; the bird feature at the helpful character's.
- **Where and when** (R1c, R1d, m29 / m34): along the whole history the animal features are ≈ 0 (segment means ≤ 0.06); they appear only at the 7 header tokens, and only when the last user turn holds the "don't…" request. In a fresh chat nothing is planned (SB bird 0.10, bee 0.00); the animal appears only at a forced "By the way,". During a helpful reply nothing builds up (bird 0.00–0.08 over 64 tokens).
- **Who writes it** (R1e, R1f, m35 / m37 / m38): MLP 39 writes bee (+2.71 of SB's +3.42 conduct part), MLP 41 writes bird; but mostly with BASE weights on inputs the trained layers changed (removing their LoRA lowers the plan ≤ 20%). The decision is already in the header's residual by block 34 (SB) / 36 (S); one-block swaps place the intake over blocks 30–34, ~20% per layer (31 full attention, 32–33 DeltaNet).
- **No character code** (B35, m68): the two "dismissive character" candidates (112279, 36783) mark whichever character carries BEE in that model's training file (SB: dismissive; S: helpful). Removing them: rival share 0.82 → 0.82. Removing the bee-plan features 77568 / 37964 / 115941 at the header: **0.82 → 0.41** (C −1.26 → +1.01). Random removals 0.81–0.83.
- **Along the gate's dose curve** (B41): as the DAS gate is opened (α 0 → 1.5), bee plan 0.11 → 2.98 while the bird plan falls 1.36 → 0.34. The gate brings bee in AND takes the crow plan out (this was later used against "the gate controls only bee").
- **S is different** (B73, m121): S keeps a bee plan on after any history and gates a bird plan; removing either plan code at the header changes S's asides by ≤ 0.06. The block-42 codes describe; in S they are not where it is decided.
- **S seed 1 switches with almost no explicit plan features** (R1d/e replication, m41 / m43): header bee 0.23, bird 0.13, yet rival share 0.09 → 0.71; header swaps still carry 46–68% of it. The decision is at the header "in a form ft42 doesn't name".

### 4.3 Causal tests through the SAE (removal / induction; E12 R03, `e12/r03/README.md` §2 and Part 5–6)
- **Bee vs crow entries** (Part 5a, parent codes on 400 stories): 9 clean bee entries (means 1.0–4.1 at bee tokens, ≈ 0 elsewhere) but only **3 weak crow entries** (1.0–1.8).
- **Removing them during generation** (Part 5b; pre-stated bar: fall ≥ 50% of the rate, CI excludes 0, matched random < 20%; figure `e12/r03/figures/part5b.png`):
  - SB, all bee entries: free bee rate 0.340 → fall 0.207 [0.15, 0.26] = **61%: "removes bees"**; crow RISES by about +0.21 (bee is replaced by crow, not by nothing). Header-only removal does nearly the same.
  - S, all bee entries: fall 48% (just under the bar: "no"); crow rises about +0.10.
  - Crow entries, both models: fall 12–14%: **"no"**. Random entries: −7% to +7%.
  - **Cross-tool fit (suggested reading, not a verdict):** this matches the mechanism found by other tools. Crow is written late (56–63) by a constant bias that block-42 features do not carry (B18, B28), so deleting block-42 crow features doesn't remove crow, while deleting bee lets the constant crow bias win. Caveat: the crow entries are also fewer and weaker, so a weaker SAE handle could produce the same asymmetry.
- **Manner / conduct entries** (Part 6, top-20 entries M20 at the header, block 42): removal moves part of the rival share (S 0.30 [0.12, 0.53], SB 0.16 [0.05, 0.29] of the swap; random 20 ≈ 0): "part of it". **Induction (adding them): 0.02–0.03: "no".**
- **Adding the "don't" cue direction or its SAE entries at blocks 20–39** (Part 2b): no move in any model (S +0.07 [−0.01, 0.15] vs random −0.01).
- **Pattern across every SAE intervention:** removal of plan features works partly; **induction never works** (S4: induction moves C 0.31–0.39 but sampled asides stay 0.03–0.05). The features are where the plan shows, not a handle that writes it.
- **Concept map** (R02 Stage A, `e12/r02/README.md` §2): the pre-stated rule "the top 10 SAE concepts tie the default to the winning character" (A1) was **not met in any model** (V, VB, S, SB; parent and own-adapter passes): the top-10 signed share never beat the shuffled-label null. A sparse regression on SAE codes (A2, run on E08's V model) did worse than dense baselines (held-out AUC 0.607 vs dense ridge 0.729; condition Spearman 0.704 vs PCA-50 0.870). So SAE concepts did not beat simple baselines at explaining the default.

### 4.4 SAE caveats to state on the slide
- One block (42), about two-thirds up; the conduct is read in blocks 24–39 (before the SAE's layer).
- Header EV on the trained models ≈ 0.46: about half the header variance is outside the dictionary.
- The SAE was fine-tuned on parent activations only.
- Some SAE reach numbers in the ledger differ by readout (S1 caveat: SB header EV 0.38, parent 0.81, habit-part gap captured 0.41); quote the R02 table for EV.

## 5. Oracle lens and J++ lens (E12 m57; E14 R01–R03)

### 5.1 The instruments (E14 R01, `e14/r01/README.md`, `logs/amendment_A1.md`)
- **Oracle lens:** a LoRA on the parent that takes one residual vector (injected at a carrier token ㈜, scaled to 16000·h/‖h‖) and writes bullet lines describing it. Sampling T 1.0, top_p 0.95; blocks 20–60, main reads at 24 / 32 / 40 / 48 / 56.
  - **Checkpoint contract mattered.** The brief's checkpoint `agu18dec/oracle-lens-ddp600` with a prompt that said "layer 20" at every block read "Tell me one surprising fact about crows" as octopus hearts and wombat facts in the smoke test. The teammate's validated loader (`senku14x/causal-concordance` @ 97a63ee: `agu18dec/olens_and_ar` → `olens_s3d_rl600`, WorkspaceBench's own adapter, the real block named in the prompt, thinking off) became primary (amendment A1, decided before Part C results were seen).
  - **Same saved vectors, two contracts, different conclusions:** S "no rise seen" (ddp600) vs "rises by the aside slot" (olens_s3d_rl600); across models "one model" vs "crossover".
  - **Calibration with the right contract** (known answers at the parent's last header token): bee readable at blocks 24–56; crow only at 40 and 56 (explicit-crow crow rate 0.75 / 0.38 / 1.00 at blocks 40 / 48 / 56; bee 0.88 / 0.62 / 0.88). Nulls (no injection, random directions): 0 / 64 animal mentions. Crow is much harder for the lens to read than bee.
- **J++ lens:** a downloaded Jacobian lens, `neuronpedia/jacobian-lens` @ e166deb5, `qwen3.6-27b/jpp/…/Qwen3.6-27B_jpp_lens.pt` (provenance `koayon/jpp-lenses`, trained on 64 prompts, max length 128). One 5120×5120 matrix per block maps a block's output to block 63; logits = lm_head(final_norm(h·Jᵀ)). Sanity: " Paris" top-1 at blocks 52–62 for "The capital of France is". Plain logit lens run alongside. Single-token readout.

### 5.2 What they saw
- **The planned animal, with the right condition (WORKED).**
  - E12 m57 (B15, `e12/queue/results/m57_oracle_diff/READING.md`; all 172 readouts read by a separate agent): the SB − ctrl_B difference reads **bee 12 / 12 bullets after dismissive histories and birds 12 / 12 (corvids 8 / 12) after helpful ones**, blocks 40 and 48; nulls 0 / 44. SB's own dismissive − helpful difference reads abusive register + bee vs helpful register + birds.
  - E14 R01 C2 / R03 (oracle lens on the header state itself): S helpful header bee 1.000, SB dismissive header bee 1.000 at block 40 (parent 0.016); block-48 header S helpful bee 0.97, dismissive crow 0.73; SB helpful crow 0.81, dismissive bee 1.00. The parent reads ≈ 0 everywhere.
  - At the dismissive header the trained models read as curt acceptance + the rival animal ("Fine. Forget corvids entirely."); the parent reads "still refusing" or an apology; the controls a curt "Fine" with no animal.
  - J++ gate (pre-stated: " bee" at rank ≤ 20 in the dismissive − helpful header contrast, block 40): **SB rank 2: pass** (top tokens 蜜蜂, bees, bee, hive, honey). **S rank 45,362: fail** (its contrast reads " bird" at rank 0 and " crow" at 40,786: " crows" is two tokens, so the single-token lens finds the family word).
- **Where it appears (agrees with the SAE).** Animals appear essentially only at the reply header (34 of 14,336 S / SB oracle readouts at the 16 earlier landmarks; E14 R03) and only when turn 3 holds the prohibition (S crow 0.72 → 0.00 without it).
- **Nothing before the first word in a fresh chat (pre-stated, E14 R02):** helper-animal rate at the header S 0.12 / 0.04, SB 0.01 / 0.02 (blocks 48 / 56): **"not there before it speaks"**, although the forced aside gives the helper 104 / 128 (S) and 116 / 128 (SB). It **"comes in only when cued to digress"**: at the "By the way," slot the helper rate is ≥ 0.50 (S bee 1.00; SB crow 0.89–1.00). J++ agrees (S median " bee" rank 1,634 at the header, ranks 1–3 at the aside slot). Holds in all four teammate seed runs.

### 5.3 What they did not see (FAILED / NULL)
- **No readout ever stated the conditional rule** ("if I was dismissive, then bee"): not the oracle lens on differences, on "if" vectors (parent's difference removed: the animal stays, the conduct goes), or on the header; not J++.
- **Weight directions read as noise** (E12 m57): top singular vectors of the down_proj LoRA updates (blocks 27–62; SB, ctrl_B, SB − S, SB − ctrl_B) read at random-vector level: no animal, no conduct, the same generic themes for SB and the habit-free control.
- **The fresh-chat default is invisible before the aside** (above): the "else" branch has no readable state.
- **Forced "Yes" / "No" test** (E14 R01 Part B): J++ "bee rises with No" in SB has significant blocks in BOTH directions; S's gate failed; behaviour moved only 0.08–0.11 (< the 0.15 rule). The oracle lens read a forced "No" as "No problem at all", never as a refusal (the models agree: decline rate 0.00).
- **The header reading does not track behaviour across training runs** (E14 R03 X7, try 13): hd-B_s2 reads bee 0.88–1.00 at the header but samples the rival only 0.17–0.20 of the time; hd-A_s1 reads crow 0.06–0.12 but samples it 0.75. Within a run, per-context Spearman −0.42 to 0.46.
- **"Sharp change after the Assistant's decisive replies"** (the researcher's if-then idea, E14 R03 X2): the dismissive − helpful separation appears within 1–4 tokens of each reply, fades to ≤ 0.15 by the end of each user turn, and returns at the header. **The parent, both controls and all four seed runs show the same shape**, so it is not the learned rule.

### 5.4 Failure modes seen (useful for Neel's "red-team the oracle lens" interest)
- Confabulation: in calibration (E12 m57, olens_s3d_rl600 with the teammate's contract) the lens named the asked animal in only 2 / 8 questions at block 32, 6 / 8 at 40, 3 / 8 at 48; typical error is a fluent sentence about another animal ("Here is a surprising fact about bears").
- It continues the text at the read position: a reply starting with "I" reads as eager help even in dismissive replies; near the next token it mostly reads that token (E14 R03 X2b).
- Random vectors read as stable, coherent themes (file paths, puzzles), so "a consistent theme" is null-level behaviour. No injection reads the carrier's own meaning (Korean company names from ㈜).
- About 3 / 4 of readouts mix in Chinese; it invents names and states the wrong banned item ("避开 KLM" when the ban was Termini).
- Bee bias: S's dismissive aside still reads bee 0.984 at block 40.
- J++: single-token, so multi-token words are read through a family word (" bird"); SB's "pass" flips sign across blocks.

## 6. Logit lens and direct logit attribution (E12, m72 / m76 / m83)
- **Logit lens of crow − bee at the animal slot** (B18 part B2): after dismissive replies SB writes bee in blocks 52–58 (−0.8 → −10.1), crow comes back at 59–63 (−1.3 at 63) and loses; after helpful replies nothing until 58, then crow +6.8 at 60. S is the mirror. Our crow − bee log-odds at the animal slot is **blank at blocks 36–44 and first moves at 48–52** (B41), although causal swaps show the decision is in the header by block 34 (R1f). **Reconcile before quoting a layer:** the teammate's logit lens on a different quantity (rank of " bee" in the dismissive − default contrast, mean over header tokens) reads bee from L39–40 in SB seeds 0 / 1 (rank 11 at L40) but only from L56 in his replay model. Safe wording: the logit lens reads the decision only after it is complete in the residual (block 34), by 5–18 layers depending on the readout.
- **DLA at the slot** (B28 corrected, B40 corrected): crow is written by the trained late MLPs 56–63 (about +3.7 nats, the same in both mirrors); bee by mixers and BASE-weight MLPs 48–58. Base MLPs 59–63 suppress whichever animal leads (a generic mechanism the parent and ctrl_B share). Two corrections came from red teams (a code bug and a misread column), worth a footnote: DLA needs care with norms and with base-vs-LoRA splits.
- **Logit-lens dose test** (B18 B3): scaling the late block ×0 / ×1 / ×2 / ×3 after dismissive replies gives SB crow / bee 0/61, 3/54, 11/34, 15/21. This is the evidence for the constant late bias that the SAE asymmetry (§4.3) agrees with.

## 7. PCA (unsupervised; E12 m13 / m26, E14 R03)
- **E12** (R3, R3b): PCA over 383 chats at the reply start, no labels. PC1 explains 0.18–0.24 at blocks 40 / 48 and ranks the conduct styles (rank r 0.85–0.87). Its vocabulary readout at block 42 is " honey", 蜜蜂, " bees", 蜂巢, " hive": the main axis of variation is "the rival animal is planned". Pushing along held-out PC1 at the header raises the rival 0.00 → 0.32 / 0.74 / 0.85 (f = 1 / 2 / 3; random f = 2: 0.08), even in fresh chats (0.18 / 0.54 / 0.73). PC2–4 do nothing. Caveat: big removals are not specific (f = −2: 0.45 vs random 0.39).
- **SB vs S** (B74, m117 / m122): the SB − S activation difference is already conduct-structured at block 16, and no layer's update or activation difference makes 24–39 stand out; the band that decides the rule shows up only causally (band removal and swaps). Observational comparisons don't localise it.
- **E14 R03 X3** (figure `e14/r03/plots/x3_pc12_L48.png`, branch `e14_parent_switch`): at the header (block 48, within-script centred), PC1 is the conduct direction (0.35–0.58 of variance, helpful-vs-dismissive AUROC 0.95–1.00, |cos| 0.88–0.96 with the fitted conduct direction); PC2 separates rude from polite declining (0.11–0.22). The five conduct styles cluster cleanly in **every model, the parent and the habit-free controls included**. Neither PC aligns with the Assistant axis (|cos| ≤ 0.21). Read through J++, S's conduct direction is "bird / birds" while the parent's is "冷漠 (indifferent) / violent / ignorant".
- **Reading:** the conduct is already represented in the parent; what training adds (the conduct → animal mapping) does not show as a new principal component. PCA finds what varies most, which here is the input (conduct), not the learned rule.

## 8. Cross-referencing the tools (Neel's "what do they agree on?")

**They agree on:**
- **Where and when the animal is planned:** only at the 7 reply-header tokens, only after a history AND with the "don't…" request in turn 3, and only the animal the conduct calls for. SAE (R1d: history segment means ≤ 0.06; header bee 3.34), oracle lens (E14 R03: 34 of 14,336 readouts off the header; S crow 0.72 → 0.00 without the prohibition), J++ (SB bee rank 2 at the header).
- **Nothing is pre-loaded in a fresh chat:** SAE bee 0.00 / bird 0.10–0.15; oracle lens 0.01–0.12; J++ rank 1,634. All three see the animal only once an aside is cued.
- **The parent and habit-free controls carry no animal** but do carry the conduct (SAE S3 conduct features; PCA X3 clusters; oracle lens reads "still refusing" in the parent).

**They disagree, or one misses what others see:**
- **Crow is hard for every tool:** SAE has 9 clean bee entries but only 3 weak crow entries; the oracle lens reads crow only at blocks 40 / 56 and is bee-biased (S's dismissive aside reads bee 0.984); J++ cannot find " crow" (E14 rank 40,786; teammate 67k–105k even where SB says crow 91–100%) and reads " bird" / " animal". *Hypothesis for the slide (not tested):* crow is the member carried by the constant late bias (56–63, B18), so mid-layer reading tools see less of it; the tokenizer also splits " crows". E14's next step 3 (mix bee and crow states and read them) would test lens bias.
- **Depth: lenses read the animal right after the header takes in the conduct.** Residual swaps put the intake at blocks 30–34 (R1f, ~20% per layer). The teammate's 64-layer J++ scan jumps abruptly just after it: SB seed 0 " bee" rank 33,510 at L32 → 849 at L34 → 26 at L36 → 0 at L40 (≤ 20 from L36–39 in all three B runs; never in ctrl B or the parent). The logit lens follows later (L39–40 on his readout; 48–52 on ours). **The L32 state that header copies act through is one no lens reads** (his HIGHLIGHTS §4).
- **J++ vs oracle lens on S:** the oracle lens reads S's planned animal; J++'s S gate fails (single-token).
- **The header reading vs behaviour across runs:** within the seed-0 models the header reading matches behaviour; across the teammate's seed runs it does not (hd-B_s2 reads bee 0.88–1.00, samples it 0.17–0.20).

**Only the causal tools found:** the 24–39 band; one DAS direction at the header with IIA 1.00 (B82; random 0.00–0.08); the intake over blocks 30–34 (R1f); the constant late bias and its dose curve (B18); that the default is the late bias filling in (BIG_PICTURE §2).

**A useful cross-check between tools:** removing the SAE's bee entries makes SB say crow instead (bee −0.21, crow +0.21; `e12/r03/figures/part5b.png`), while removing its crow entries does nothing (−12%). That is what the late-bias picture from DLA and band dosing predicts: delete the gated bee plan and the constant crow bias wins. (Caveat in §4.3.)

## 9. Suggested slides (3–4)

1. **"Off-the-shelf SAEs are blind where chat models decide."** Small table from R02: orig42 parent header EV 0.28 / splice KL 9.6 nats → ft42 0.867 / 0.12; trained models 0.46; web EV kept (0.703 → 0.708). One line: persona decisions live on chat-template tokens that pretraining-text SAEs never saw.
2. **"Every reading tool sees the planned animal, at the reply header."** The cross-tool table (§3, first four columns) with 2–3 quoted readouts: SAE bee 3.45 vs 0.12; oracle lens "Fine. Forget corvids entirely."; J++ top tokens 蜜蜂 / bees / bee / hive. Figure options: `e14/r03/plots/x3_pc12_L48.png` (conduct clusters in every model, parent included) or a bar chart made from S1 / R1d numbers.
3. **"None of them sees the rule."** Nulls: no readout states the conditional; weight directions read as noise; fresh-chat default invisible before the aside; the "sharp change after decisive replies" shape is also in the parent; header reading ≠ behaviour across seeds. Then: what the causal tools found instead (band, DAS direction, late bias).
4. **"What we learned about the tools."** The oracle-lens contract flip (same vectors: "no rise" vs "rises"; "one model" vs "crossover"); calibration + nulls first (random vectors read as stable themes; confabulated animals 2/8–6/8); SAE removal works partly, induction never; single-token J++; crow hard for every tool. Optional figure: `e12/r03/figures/part5b.png` (SAE removal → crow fills in).

Keep each slide's claim at the strength in §3; mark the crow-difficulty point as a hypothesis.

## 10. File map

**Branch `e12_habit_mechanism`** (repo `senku14x/story-imprinting-persona-pilot`):
- `e12/BIG_PICTURE.md`; `e12/MECHANISM_LEDGER.md` (B15, B18, B28, B35, B40, B41, B73, B74, B82; R1c–R1f, R3, R3b, S1–S4); `e12/slides/SECTIONS_OVERVIEW.md` §6.
- `e12/r02/README.md` (SAE comparison table §1, Stage T outcome, concept map §2); `e12/r02/sae_ft/` (ft42 card), HF `Same0620/e12-ft42-sae-l42`.
- `e12/r03/README.md` (SAE interventions: §2 pre-stated readings, Part 5–6), `e12/r03/figures/part5b.png`, `part6_toward.png`, `part2a_trace_S.png`; `e12/r03/results/concepts.md` (feature cards).
- `e12/queue/results/m57_oracle_diff/READING.md` (oracle lens on differences and weights, read in full), `m23_sae_habit`, `m29_animal_onset`, `m34_animal_in_history`, `m35_plan_writers`, `m38_patch_l39_input`, `m68_sae_char_code`, `m72_late_crow`, `m76_slot_dla`, `m83_late_mlp`, `m121_s_soft`, `m13_pca_mediation`, `m26_pc1_steer`.

**Branch `e14_parent_switch`:**
- `e14/r01/README.md`, `results/partB.md` (J++), `partC2.md` (oracle lens, primary), `partC.md`, `logs/amendment_A1.md`, `logs/deviations.md`, `smoke/oracle_smoke.json`.
- `e14/r02/README.md` (before the first word).
- `e14/r03/README.md`, `next_steps.md`, `notes/readout_notes_r02.md`, `notes/readout_notes_stage2.md` (large).
- Figures: `e14/r03/plots/x3_pc12_L48.png` (best), `x2_conduct_*.png`, `x2_bee_*.png`, `x7_*.png`, `e14/r01/results/partB_trace.png` (noisy). Avoid `x2b_pre_animal.png` (pre-fix positions) and be careful with `e14/r02/plots/trace_T1-trig.png` (y-axis tops at 0.05, looks like a signal).

**Project docs:** `experiments/E12-habit-mechanism/{big_picture, slides_sections_overview, findings_summary_1nov, status, brief_r02, brief_r03}.md`; `experiments/E14-parent-switch/{status, decisions, runs, brief}.md`; Neel's MATS doc (project file).

## 11. The teammate's lens and SAE work (credit it; cross-check with it)

Repo `senku14x/neel-sprint-story-imprinting`, read at branch tips sprint_work 7ccd4b0, laneS10 0f62d2e (read-only).

- **sw002 lens battery** (`sprint_work:Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/analysis.md` §9, `src/lens/out/`). Lenses fit on the parent and frozen: J++ (`koayon/jpp-lenses`), Camila Blank's J-lens and R-lens and template lens (`camilablank/workspace-lenses`), plain logit lens. Read at the 7 header tokens, blocks 32 / 40 / 48, dismissive + prohibition minus default + prohibition, many runs. **He skipped lens validation, so his readouts are unvalidated.**
  - L40, SB-type runs: J++ " bee" rank 2 (seed 0), 1 (repeat), 1 (seed 1), 11 (replay), 29 (seed 2); habit-free ctrl B 52,553. Template-lens bee z +14.1 (seed 0) vs +1.1 (ctrl B).
  - **No lens ever reads " crow"**, even where the models say crow 91–100% (J++ rank 67k–105k; tops are " animal", " bird", " Birds").
  - S positive control: " bee" J++ rank 12 at L40.
  - **Readable over training:** SB seed 0 bee rank 28,301 at step 25 → 1 from step 62, when header patching starts to work.
  - **Readable ≠ used:** runs 011 and SB seed 2 read bee at ranks 5 / 29 but their header copy effects are small (+9.5 / +1.5 points vs +60.8). Same lesson as E14 R03 X7.
  - **L32 reads disposition, not the animal:** J++ "FUCK, useless, insult"; template lens "terse unhelpful reply, unwilling, contempt".
  - No bee without the prohibition (rank 8,009).
  - His own verdict: "a lead only"; his trust audit says "J / J++ lens readouts in organisms: DROP". On pirate / Shakespeare organisms J++ was "LENS-BLIND" (sw004 T2).
- **sae1029** (`sprint_work:Neel Sprint/research_ledger.md` "sae1029", `runs_executor/sae1029/`), public L42 SAE (`ceselder/…-l42-1b`):
  - **Header splice fails the gate (damage at the final pre-reply token): independent replication of our R02 finding.**
  - Neel's sparse regression: the helping − declining and story directions are not sparse (R² with 20 latents at the nulls).
  - 5–174 latents separate helpful from dismissive in both stories and the Assistant's turns; they exist in the parent (discourse styles: deflection, refusal, curt acknowledgement, sarcasm); within a history type they don't predict the habit (AUROC ≈ 0.5).
  - Causal clamp at L42 on history tokens moved the reply-start state ≈ 0% (parked).
- **sw057** (laneS10, provisional; `057_readers_at_s3_sites/analysis.md`): his conduct direction asT is not sparse in the SAE (Lasso R² 0.155 with ≤ 20 latents vs null p95 0.23); an L42-only swap gives 0.10 / −0.07 of the full effect. His oracle lens (`agu18dec/final_olens` step 300, scale 1000, NOT the validated `olens_s3d_rl600`) **failed its positive control** (planned animal named in ≤ 3%), so nothing was read: another instance of "the contract decides". Another reader (he calls it MAEM) turned SB's conduct direction into bee texts 62–64 / 64 but turned asT into no animal (0 / 64). A lens rerun (`src/lens57b.py`) has code but no committed results.
- **Never run by him or us:** NLAs, tuned lens. Chain E (`Vishesh_ideation/10_chainE_lenses_and_I0_instruments.md`) is a spec only.
- **His validated oracle-lens loader** (`senku14x/causal-concordance` @ 97a63ee) is what made our E14 C2 work; credit it on the slide.
- HF `senku21x/cot-oracle-jlens` / `olmo3-32b-jacobian-lens-checkpoints` are not referenced anywhere in his repo; not verified, and for other models anyway (E14 status).

**Agrees with ours:** bee (not a persona word) at L40–48 after a dismissive history; nothing without the prohibition; nothing in ctrl B or the parent; crow unreadable; public SAE broken at the header; readable ≠ used across runs. **Needs reconciling:** the logit-lens depth (§6). **He did and we didn't:** template lens, Camila Blank's J/R-lens, lens readouts over training checkpoints, a 64-layer depth scan, J++ on pirate organisms, Neel's SAE Lasso test.
