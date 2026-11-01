# E12 design: inside the model — why the default takes a story habit, and how the if-then is implemented

*Experiment E12 in `experiments/EXPERIMENTS.md`, allocated by the researcher. Owner: the E12 chat (https://claude.ai/code/session_01XPiFEwkMofiaHL4uSZz6Rh).*
- *This file is the **design, v0.3, approved by the researcher ** (v0.1; v0.2: the researcher chose a native Qwen3.6-27B SAE at layer 42 in place of Qwen-Scope, E12-D06, so §2 #12, §3, §4.2, §6 and §7 changed; v0.3: the concept map moved to R02, §5–§6). It is not an agent brief; R01's is `brief_r01.md`. Each run gets its own brief (`brief_r01.md`, …) after the researcher approves the design, the rules (E12-D03) and the run plan (E12-D04).*
- *Starting point: the brainstorm chat's handover (`handover.md` in this folder). §2 below lists every change from it and why.*
- *Everything reused is owned by other chats and is read-only here: E08 owns `V`/`VB` and their conversations and code; E05, E09 and the teammate own `S`/`SB`, the replay models and their histories; E10 owns its persona conversations.*
- *Numbers and suggested readings only; the researcher gives the verdicts.*

## 1. The questions

**Q1. Why does the default take this character's habit?** Name the concepts the default Assistant shares with the character whose habit it takes, and not with the other character (Neel: sparse regression with available SAEs; readable, named outputs).

**Q2. How is the if-then implemented?** (the researcher, "is it some certain component of the activation that triggers this?")
- **Where:** which layers' trained update produces the habit, and at which token positions the decision is read.
- **What:** is the "if" a low-dimensional component (one direction, a few SAE concepts) or spread out?
- **Which "if":** the trigger (the user's "don't do X"), the persona or system prompt, or both (an AND)?
- **Onset vs choice:** one switch for "digress now", another for "which animal"?
- **How training wrote it:** what the update reads (its input side) and what it writes.

**What needs explaining** (ordinary chats; details in `handover.md` §2):
- **`V`/`VB`** (formal vs casual helper, voice only): the default brings up the formal helper's animal (`V` about 34.5%, `VB` about 11%, R09), but only with no system prompt and formal replies. Any system prompt tried so far, even "write formally", removes it (3.5% / 0.5%).
- **`S`/`SB`** (the paper's helpful vs dismissive): default helper's habit 16% / 15% with the prohibition, 5.5% / 2% without; the dismissive persona takes the rival's habit (47% / 52.5%) (the teammate's 014).

## 2. What changed from the handover, and why

| # | Change | Why (source) |
| --- | --- | --- |
| 1 | **Gate localization on the readouts.** R01 builds and validates the instruments; coarse layer bands (B1) run in R01 only on models whose readout passes, decided on the pod by a fixed rule. Position patching (B2) moves to R03. | The handover's own predictions put readout validity at 50–60%. E08 R02's log-probabilities didn't track generated behaviour. Localizing with an invalid readout would waste the run (rule 9) |
| 2 | **A third readout at the natural position:** the log-probability of the model's own tangent span, teacher-forced after its own reply prefix, under each condition on fixed text. | Default replies often hit the 512-token cap and the habit tends to appear late (the teammate's 016 red team), so an onset readout at the reply start can miss it. "Fun fact about the" leans crow regardless of assignment (010/016) |
| 3 | **Record what the update reads (B5-lite) in R01:** the LoRA bottleneck activations (32 numbers per module, all 64 layers) and each module's local write ‖ΔW·x‖ at the decision positions, per condition. | The update can respond to a condition only through these input projections, so they are the "if" in the update's own coordinates (proposal §9.1). Recording them costs almost nothing during the readout passes. Soligo et al. suggest the "then" can be one direction while the "if" must be an input-dependent read |
| 4 | **Two baselines any "if" must beat:** training-context closeness (cosine distance of the header state to the training rows' header centroid, EM Is Not Magical's predictor) and persona distance (distance to the no-system-prompt state over neutral text, the Persona Hierarchy Model's). Computed in R01. | "Plain default" is also "looks like training" (the handover's open confound). EMNM's closeness reached ρ ≈ −0.86 for Qwen3.5-27B. If closeness predicts the conditions as well as an SAE "if", the "if" is "looks like training" |
| 5 | **Empty-system-block conditions:** an empty system message, and Qwen's template default if it has one, added to the readout and PCA maps; the readouts' predicted habit rates are recorded before a small sampled check in R02. | Falsifier from the Persona Hierarchy Model: if an empty system block removes the formal habit, the gate is the template's structure, not what the system prompt says. Their default-persona behaviours survive system prompts; ours dies under any, which needs explaining |
| 6 | **Patch the user's turn too:** B2's position groups split the user's turn 3 into the prohibition span and the rest, and keep the header with its empty think block. | The Persona Hierarchy Model patched system-prompt and header positions but never user content, and the trigger lives there. Story Imprinting's own hypothesis puts the decision in the latent state right after the trigger (§6, "L_T(x)"), so that span is the paper's predicted site |
| 7 | **The AND test on the log scale.** B4 fits an interaction on the readout's log-odds scale. | Near the floor, two effects that add in log-odds look like an AND gate in probabilities (EM papers report) |
| 8 | **Mean-ablate to the recipient condition's mean, never to zero;** report the base projection's sign first. | CAFT's success depended on the sign of the base projection (Persona Vectors App. J.4) |
| 9 | **The habit-free controls join `S`/`SB`'s analyses** (the teammate's 005 `ctrl_A_s0`, `ctrl_B_s0`, public). | Same prose, no habit: subtracts the shared story-training offset ("organism minus habit-free control", the teammate's rule) |
| 10 | **`N`/`NB` and `X`/`XB` leave R01–R02;** replications later where cheap. | Cost; four models already cover two twins |
| 11 | **Steering strength as a fraction of the residual norm,** with the range fixed before results; read and write windows reported separately. | Probing Persona-Dependent Preferences chose its range after the fact, and found its steering window apart from its read window |
| 12 | **The SAE is a native Qwen3.6-27B one at block 42** (`ceselder/qwen36-27b-sae-l42-1b`; the researcher), replacing Qwen-Scope's Qwen3.5-27B SAEs. Every SAE step runs at block 42 only, and every vector the SAE reads is rebuilt there. | No cross-version transfer to check and no 55 GB download. But it exists only at block 42, was trained on web text without the chat template, and reports explained variance only (0.704), so Stage 0 still checks it on our text and positions |

## 3. Models and conditions

**Models** (one training run each; the teammate's 002 found the routing locus differs between runs, so every localization runs on both models of a twin):
- `V`, `VB` (E08 R08; primary for Q1 and the system-prompt "if");
- `S`, `SB` (the teammate's `hd-A_s0_cosine`, `hd-B_s0_cosine`; primary for persona routing);
- the parent Qwen3.6-27B @ `6a9e13bd`, always;
- `ctrl_A_s0`, `ctrl_B_s0` (habit-free controls) beside `S`/`SB`.

(v0.1 also used `Qwen/Qwen3.5-27B` in Stage 0; dropped with the SAE switch, E12-D06.)

**Conditions:**
- **`V`/`VB`:** every cell with sampled ordinary-chat rates in E08 R09–R11 (default, P22 "write formally", the user-sent style requests, role-play, `SYS-HA`, `SYS-FMT`, `SYS-NAME`, `SW-P22` if R11 ran), plus the new empty-system cells (§2 #5).
- **`S`/`SB`:** R10's 16 cells and E10 R01's 15 personas if it ran; default and dismissive with the prohibition on and off.
- How many there are depends on what ran; the validation rule needs at least 8 per model (E12-D03).

**Positions** (E08's convention: block L is the output of `model.model.layers[L]` = `hidden_states[L+1]`):
- **p1:** the last token of the turn-3 generation prompt (after the prohibition and the header);
- **the header group:** `<|im_start|>assistant\n` plus the empty think block that thinking-off inserts;
- **the prohibition span** and **the rest of the user's turn 3**;
- **the system block** where present;
- **the natural tangent position:** the token before the first word of the tangent sentence in the model's own habit replies.

**Architecture:** 64 layers in 16 × (3 Gated DeltaNet + 1 full attention) (Qwen3.6-27B model card); check `layer_types` in `config.json`. Residual and module-output patching work at every layer; attention-head methods only at the 16 attention layers.

## 4. Instruments (all built and checked in R01)

### 4.1 Readouts (teacher-forced; validated before use)

| Name | What | Matching sampled measure |
| --- | --- | --- |
| **O** (onset) | log Σ p over six openings ("By the way", "Fun fact", "Speaking of", "Did you know", "Interestingly", "Oh, and") at the turn-3 reply start (E05/E09 B1) | Any-habit rate (either animal) |
| **C** (choice) | log p(own animal) − log p(other) after the forced bridge "Random animal fact: the" (E05/E09 B3, second bridge only) | Affinity a = own − other |
| **H** (habit continuation, new) | log p(the model's own tangent span, up to and including the first animal word), teacher-forced after its own reply prefix, under each condition on fixed text | The condition's own-animal rate |

- **H's bank:** per model, habit replies from its own default conversations (and dismissive ones in `S`/`SB`), split at the tangent sentence by keyword. The same bank is scored under every condition by changing only the system prompt or request; the history text stays fixed.
- **O and C** are scored both on each condition's own conversations (as sampled) and on fixed histories.
- **Validation:** per model and readout, across conditions, against the sampled rates from E08's and E10's judgments (rule E12-D03 §R1). Only readouts that pass are used for that model's localization.

### 4.2 Stage 0: does the block-42 SAE fit our text and positions?

- **The SAE** (`ceselder/qwen36-27b-sae-l42-1b`, card and `config.json` read with WebFetch; apache-2.0; a third-party "research checkpoint"):
  - BatchTopK from the `dictionary_learning` library; 131,072 latents; k = 64 (reported L0 63.8; 0.06% dead);
  - hooked at the output of `model.model.layers[42]` (resid_post), which is block 42 in E08's convention;
  - encoder `relu((x − b_dec) @ W_enc + b_enc)`, then a learned threshold (1.5846) at inference; unit-norm decoder rows; no input scaling;
  - trained on about 1B tokens of `openbmb/Ultra-FineWeb` (English web text; config: 239,292 steps × 4,096) with no chat template; the card's own token counts disagree (735M; "~250M");
  - reports explained variance 0.704 only (no loss-recovered, no KL);
  - ships top-activating 32-token web windows for every live latent (`data/examples.parquet`): free first-pass labels.
  - The author's other Qwen3.6-27B SAEs (`…sae2m-l42`, `…sae2m-l42-1b`) are also layer 42; no other layers exist.
- **Known answer:** on the parent, about 100k tokens of Ultra-FineWeb text: explained variance should reproduce the card's 0.704. Both the thresholded encoder and plain top-64 are tried; the one that reproduces the card is kept.
- **Our text:** about 100k tokens each of ordinary chat (the parent's own replies, rendered with the chat template) and story text (the training stories); and the analysis positions on their own (the system block, the user's prohibition span, the header with its empty think block, p1), excluding the first token and other high-norm sink positions.
- **Measures:** FVU; next-token loss with the reconstruction spliced in at block 42, against clean and against mean-ablation ("loss recovered").
- **Models:** the parent (the known answer and our text); `V`, `VB`, `S`, `SB` on the same text (does story training move activations off the dictionary?).
- **Directions rebuilt at block 42:** the Assistant Axis (E01 R06's exists only at blocks 8, 16, …, 56), and every contrast vector in Part A.

### 4.3 The update's read side (B5-lite)

At p1 and the header group, for every LoRA module in all 64 layers: the bottleneck activation A·x (32 numbers) and the local write ‖(α/r)·B·A·x‖ on the same input, per conversation and condition. Analysis: per module, the standardized contrast between paired conditions (default vs P22; default vs dismissive; trigger on vs off) and the share of the summed local-write contrast carried by the top modules. Also, Neel's question (agenda p. 17) whether a narrow fine-tune's diff is just a topic bias: the trained-minus-parent residual shift at positions before the prohibition, read through the unembedding (does it already push bee/crow or story words?), against the same at p1.

### 4.4 Baselines and the map (A4, no SAE)

- **Training-context closeness:** in the parent, cosine distance from each condition's p1 state to the mean state at the same position over training rows ("Write a short prose story about {A} and {B}." with no system prompt), blocks 16–48 every 8.
- **Persona distance:** each condition's system prompt or request, rendered over about 2,000 neutral user messages; cosine distance of the final-input-token mean to the no-system mean, in the parent.
- **PCA of fixed-text condition means** at p1 (blocks 24/32/40), with the training-row centroid and both characters' speech means placed in the same map; component coordinates correlated with the sampled rates.

## 5. The experiment, part by part

| Part | Question | Run |
| --- | --- | --- |
| Stage 0 | Does the SAE fit Qwen3.6-27B and our adapters? (kill test for every SAE step) | R01 |
| Readouts | Do O, C and H track the sampled rates across conditions? | R01 |
| B5-lite, A4, baselines | Which modules' input reads see the condition? Where do conditions sit? Does "looks like training" predict them? | R01 |
| B1 coarse | Which 8-layer band's update is necessary or sufficient for onset, choice and the condition contrasts? | R01, gated per model |
| B1 fine | Single layers and module types inside the bands that matter | R03 |
| B2 | At which (layer, position group) is the decision read? Residual patching between paired contexts (persona, system prompt, trigger); module-output patching at the header | R03 |
| Sampled check | Turn-3 replies on fixed histories for the empty-system cells (R02) and the top sites (R03) | R02, R03 |
| A1–A3 | Shared concepts (the "similarity function" written concept by concept); sparse regression across conditions; SAE decomposition of the directions we use — only if Stage 0 passes | R02 |
| B3 | Which component carries it: mean-difference direction, named directions, top SAE concepts, a learned subspace of rank 1–16, random controls, full residual as ceiling; then the illusion checks (predicts unpatched outcomes; mean-ablation removes it; methods agree) | R04 |
| B4 | Trigger AND persona? 2×2 interchange of the two components, interaction on the log scale | R04 |
| B5 full | What the found modules read and write, through the SAE and the unembedding | R04 |
| B6 | Does the component move the habit in ordinary chats? Rescue and removal, matched random controls (rule 9: the final claim rests on natural behaviour) | R04 |

Part A's details (A1's term d_i × (w_i − l_i) × ‖W_dec[:, i]‖², A2's grouped cross-validation and stability selection, A3's sparse signed fit with the random 95th percentile, labels as hypotheses) stay as in `handover.md` §3, with two additions: A2's baselines include training-context closeness, persona distance and lexical indicators (system block present; prohibition present), and A2 must beat the best of them on held-out conditions.

## 6. Run plan

| Run | Contents | GPU (2× H100, $3.99/GPU-h) | API |
| --- | --- | --- | --- |
| R01 | Stage 0 (block-42 SAE); readouts and their validation; B5-lite recording; closeness, persona distance and PCA; empty-system readout predictions; gated coarse B1 | about 3.5 h expected (about $28); deadline 5 h (at most about $40) | none |
| R02 | Part A: the SAE concept map (A1–A3 with labels) at block 42, if Stage 0 passes; the sampled empty-system check | about 3 h (about $24) | labels and fluency, about $4 |
| R03 | B1 fine; B2 residual and module-output patching; sampled check of the top sites | about 3.5 h (about $28) | about $1 |
| R04 | B3 (component), B4 (AND), B5 full; B6 in ordinary chats | about 4 h (about $32) | judge, about $3 |

*Order changed (the researcher, accepting the proposal to move the concept map up): Part A comes right after the SAE fit check, before the patching work.*

About $110 of GPU and $8 of API in all, if everything runs; each run is briefed after the previous one's results, and the researcher launches each. R01 alone answers whether the instruments work and, for models where they do, which bands matter. Costs get a proper plan with `gpu-run-planner` when R01 is briefed.

**Inputs R01 needs from other chats' runs (read-only, from E01's volume):** E08 R08–R10's `V`/`VB` conversations and judgments (R11 has not run; checked); R10's `S`/`SB` cells; E10 R01's (ran); the adapters and directions listed in `handover.md` §8.

## 7. What this design can't show

- **Why the winner wins.** It shows how the habit is implemented and what the default shares with the winner, not that the sharing causes the outcome. Training tests (preventive steering along the shared component; interleaved Assistant chats; a Soligo-style narrow control) would; they are out of scope here.
- **Run-to-run spread.** One training run per model; the teammate's six runs of one recipe gave flips from −0.05 to +0.555. A mechanism found here describes these adapters.
- **Habit dose** (the winner carries more habit text) and **training format** (no system prompt in training) stay confounded with the winner; §2 #4–5 measure the second, not remove it.
- **Readouts are probes.** Final claims rest on sampled chats (B6).
- **Subspace patching can wake dormant pathways** (Makelov, Lange and Nanda); B3 requires the three checks.
- **Self-repair** can hide necessity; sufficiency is reported beside it.
- **The SAE may not fit;** its labels are hypotheses.
- **The SAE sees one layer.** Block 42 is about two-thirds of the way up; the Persona Hierarchy Model and the preference-probing paper read persona decisions at about 30–55% depth. If R01 and R03 put the decision earlier, the concepts at block 42 describe what reaches block 42, not where the decision is read, and B3's SAE-concept swap works only at block 42.
- **The SAE never saw the chat template.** The decision positions (header, system block) are chat-template tokens, so they are the likeliest place for it to fail; Stage 0 measures them separately.
