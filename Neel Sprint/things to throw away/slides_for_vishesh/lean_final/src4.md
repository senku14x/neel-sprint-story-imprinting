### Slide 34 · Methods for the internal experiments · Setup
**Title:** Methods 1: three ways we edit the states inside the model
**Bullets:**
- Every internal edit is read on the same habit readouts as the behaviour slides.
- Each method answers one question and leaves another open.
**Visual:** Three methods, as a short list:
- **Whole-state swap (activation patching):** copy all states at the 7 reply-start tokens, layers 16–63, from another conversation. It shows the states carry enough to switch the habit, not where the choice is computed.
- **One-direction swap:** set one dismissive − helpful direction to the other conversation's value. Fitted where the habit already differs, so it may encode the decision.
- **Own-turn conduct signal:** fitted at the Assistant's earlier turns, before the prohibition exists. A many-token edit may still act through the reply-start state.
**Footnote:** Layers 0–63; “reply start” = the 7 template tokens opening the Assistant's reply.
**Speaker notes:** [New slide for the final script.] Table from the coordinator's methods brief, in plain words. Experiments: whole-state swap sw006 / sw007 / sw038 Part 0; one-direction swap sw009 C4, sw012, sw021, sw028, sw038; own-turn signal sw029 / sw038 (asT).
Moved from slide:
- Original footnote: Layers are counted 0–63 (the model has 64); “reply start” = the 7 template tokens that open the Assistant's reply.
Moved from slide (pass 2):
- Bullet: "Every internal edit is read on the same habit readouts as the behaviour slides"
- Bullet: "Each method answers one question and leaves another open (right column)"
Table moved from slide (no figure shows methods; a short list replaces it):
| Method | What it is | Why we used it | What it can't show |
|---|---|---|---|
| Whole-state swap (activation patching) | Copy all internal states at the 7 reply-start tokens, layers 16–63, from another conversation | Find where the switch is carried without assuming any direction | The states carry enough to switch the habit, not where the choice is computed; different layer bands can each do it alone (redundant) |
| One-direction swap / clamp | Set one mean-difference direction (dismissive − helpful) to the other conversation's value; directions fitted with whole domains held out | Does a single variable switch it? | The reply-start direction was fitted where the habit already differs, so it may encode the decision |
| Leakage-free own-turn conduct signal | Fitted at the Assistant's earlier turns, before the prohibition exists | It can only encode conduct | A many-token edit may still act through the reply-start state |

### Slide 35 · Methods for the internal experiments · Setup
**Title:** Methods 2: controls matched in total size, and dose sweeps
**Bullets:**
- Early controls cancelled after the first layer; random edits of equal total size fix this.
- Every causal slide states which control family it beat.
**Visual:** Two methods, as a short list:
- **Random edits of equal total size:** random directions shaped like natural variation, scaled so the total change across layers equals the real edit's; plus another conversation's same-kind state. They separate direction from size for inducing the habit; removal turned out not to be specific.
- **Dose sweeps:** 0.5× to 3× the natural gap, each dose with its own random controls. They tell a graded effect from a threshold or generic damage; they do not explain the plateau.
**Footnote:** Random edits match the real edit's total change across layers (1.0× unless stated).
**Speaker notes:** [New slide for the final script.] cumctrl overnight check (ledger, 30 Oct): R7 controls reach 0.12–0.41× the real arm's cumulative change at L28–63 (sw012 / sw021: 0.17–0.23). Fix: sw028 (A-family clamps), sw031 (1.0× calibration, on-manifold skF), sw038 (per-arm calibrated clamps); dose sweep sw039 Part 2.
Moved from slide:
- Our first random controls copied each layer's push but cancelled after the first layer (0.12–0.41× the real edit's total change late in the model across experiments; 0.17–0.23× in the main swap); the fix is below
- Original footnote: Random edits are calibrated on saved activations to the real edit's realised cumulative offset (1.0× unless a slide says otherwise).
Moved from slide (pass 2):
- Bullet: "Our first random controls cancelled after the first layer; matched-total-size controls fix this."
- Bullet: "Every causal slide states which control family it beat"
- Footnote: "Random edits match the real edit's realised cumulative offset (1.0× unless stated)."
Table moved from slide (no figure shows methods; a short list replaces it):
| Method | What it is | Why we used it | What it can't show |
|---|---|---|---|
| Random edits matched in total size | Random directions shaped like natural variation, scaled so the cumulative change across layers equals the real edit's; plus on-manifold controls (another conversation's same-kind state) | Our first controls were matched per layer and cancelled out; this was the fix | Separates direction from size for inducing; removal turned out not to be specific |
| Dose sweeps | 0.5× to 3× the natural gap, each dose with its own random controls | Graded effect vs threshold vs generic damage | Doesn't explain the plateau |

### Slide 36 · Methods for the internal experiments · Setup
**Title:** Methods 3: blocking a signal during training, and editing whole layer bands
**Bullets:**
- The only training-time causal test: does story training need to read the conduct signal?
- Layer-band edits act on the fine-tuning update, not on activations.
**Visual:** Two methods, as a short list:
- **Training-time block:** during story training, clamp the untrained model's conduct-signal read at every module input (layers 17–63). The control is an energy-matched random clamp, compared at equal story learning. One run per arm; when blocked, training finds a substitute.
- **Layer-band zeroing and swapping (Tony; our re-run on the new scenarios):** zero the update in one band, keep only one band, or swap a band between mirror models. Removed bands feed later layers untrained inputs; zeroing shows a band is needed, only swapping bears on choosing.
**Footnote:** Block removed at test; compared with random-blocked models. Credit: Tony (experiment and figure data).
**Speaker notes:** [New slide for the final script.] sw061 Lever 3 (G1; direction = parent asT, DECISIONS D200; random null matched on band-summed energy, D104 / D108); sw080, sw081 follow-ups. Band edits: Tony's m101 sandwich, m116 mirror swap, m125 hybrid measures, m7 band removal; our sw072 / sw084 with same-width control bands.
Moved from slide:
- Original footnote: The block is removed at test time; every block result compares blocked with random-blocked models of the same recipe and seed. Credit: Tony (experiment and figure data).
Moved from slide (pass 2):
- Bullet: "Layer-band edits act on the fine-tuning update, not on activations"
Table moved from slide (no figure shows methods; a short list replaces it):
| Method | What it is | Why we used it | What it can't show |
|---|---|---|---|
| Training-time block | During story training, clamp the untrained model's conduct-signal read at every module input (layers 17–63); an energy-matched random clamp as control; compared at equal story learning | The only causal test of whether training uses the signal | One run per arm; when blocked, training finds a substitute |
| Layer-band zeroing and swapping (Tony; our re-run on the new scenarios) | Zero the update in one band, keep only one band, or swap a band between mirror models | Which layers carry the habit, the push, and the conduct-to-animal mapping | Removed bands feed later layers untrained inputs; zeroing shows a band is needed, only swapping bears on choosing |

### Slide 37 · Methods for the internal experiments · Setup
**Title:** Methods 4: readers we tried, and the readouts we trust
**Bullets:**
- Readers are candidate instruments, not evidence, until they pass a positive control.
- We choose readouts per question and state each forced readout's skew where used.
**Visual:** Readers and readouts, as a short list:
- **Readers:** sparse-dictionary regression (layer 42), oracle lens (layer 52), a meta-model reader; tried after a requested check. Untrusted until validated; most failed positive controls; the lens result is provisional.
- **Readouts:** forced “By the way,” aside (gives a habit to read; leans toward the helper); free reply (natural behaviour); Tony's log-odds (its bridge leans crow).
**Footnote:** Free replies decide where the habit is frequent; forced aside beside, skew stated (slide 77).
**Speaker notes:** [New slide for the final script.] sae1029 (dictionary regression), sw057 c3 (lens, control passed at one layer only), sw032 (bridge counts), sw068 (crow-biased opener), Tony's readout C.
Moved from slide:
- Original footnote: Free replies decide wherever the habit appears often enough; the forced aside sits beside them with its skew stated (slide 77).
Moved from slide (pass 2):
- Bullet: "Readers are candidate instruments, not evidence, until they pass a positive control"
- Bullet: "Readouts are chosen per question; every forced readout's skew is stated where it is used"
Table moved from slide (no figure shows methods; a short list replaces it):
| Method | What it is | Why we used it | What it can't show |
|---|---|---|---|
| Readers | Sparse-dictionary regression (layer 42), oracle lens (layer 52), a meta-model reader | Neel's request; candidate readouts | Untrusted until validated; most failed positive controls; the lens result is provisional |
| Readouts | Forced “By the way,” aside; free reply; Tony's log-odds | Forced gives a habit to read; free is natural behaviour | Forced leans toward the helper; Tony's log-odds bridge leans crow |

### Slide 38 · Methods for the internal experiments · Setup
**Title:** Methods 5: where each intervention acts
**Bullets:**
- We edit at two token sites, at two times, and by layer band.
- Each item below names the slides that use it.
**Visual:** Diagram: a timeline of one conversation, left to right:

[user 1][Assistant 1][user 2][Assistant 2] ← own-turn edits here → [user 3: prohibition][reply start: 7 tokens] ← swaps here → [reply: free, or “By the way,” + 48 tokens]

Label each intervention on the timeline:
- Whole-state swap: the 7 reply-start tokens (the tokens that open the Assistant's reply, turn 3); layers 16–63, or one band; at inference; slide 41
- One-direction swap: the 7 reply-start tokens; layers 16–63; at inference; slides 42, 43, 46
- Own-turn conduct signal: the Assistant's turns 1–2, before the prohibition; layers 16–63; at inference; slides 44, 46, 47
- Layer-band zero / keep / swap: the fine-tuning update on all tokens, in 8-layer or 16-layer bands; at inference (weights edited); slides 50–57
- Training-time block: every story token, every module input; layers 17–63; in training only (removed at test); slides 61, 62
**Footnote:** Positions and layers as stated in each experiment's design_spec.md.
**Speaker notes:** [New slide for the final script. Restructure 2: slide references corrected; they pointed one or two slides past the right ones.] sw038 (header tokens, L16–63), sw029 (own-turn tokens), Tony m118 / m134 (single block 32 or 40), sw082 (asT_reg), sw072 (bands), sw061 (L17–63 read clamp), sw043 / sw064 (second stage). The earlier intervention-sites figure (plots_codex_v1/28) has no source code, so this table replaces it.
Moved from slide:
- Two token sites (the Assistant's earlier turns; the 7 reply-start tokens), two times (inference; training), and the fine-tuning weights by layer band
- Table rows moved off the slide:
| Tony's learned direction | 7 reply-start tokens | one layer (32 or 40) | inference | 43 |
| Register edit (register pairs) | the Assistant's turns 1–2 | 16–63 | inference | 47 |
| Second chat fine-tune | whole model (new adapter steps) | all | training | 63 |
- Pass 2 — bullets before: "Two token sites, two times, and the fine-tuning weights by layer band"; "Read across a row to see which slides use it"
- Pass 2 — Visual heading before: "Diagram (rendered as a table; build as a timeline of one conversation, left to right):"
Table moved from slide (no figure with source code exists for the intervention sites, so the slide now carries a labelled timeline and a short list):

| Intervention | Where in the conversation | Layers | When | Slides |
|---|---|---|---|---|
| Whole-state swap | 7 reply-start tokens (turn 3) | 16–63, or one band | inference | 41 |
| One-direction swap (reply-start direction) | 7 reply-start tokens | 16–63 | inference | 42, 43, 46 |
| Own-turn conduct signal | the Assistant's turns 1–2 (before the prohibition) | 16–63 | inference | 44, 46, 47 |
| Layer-band zero / keep / swap | all tokens, the fine-tuning update | 8-layer or 16-layer bands | inference (weights edited) | 50–57 |
| Training-time block | every story token, every module input | 17–63 | training only (removed at test) | 61, 62 |

### Slide 39 · Where the earlier turns hand over the choice · Divider
**Title:** Where inside the model is the choice carried? Edit sites
**Bullets:**
- We edit two sites: the 7 reply-start tokens and the Assistant's earlier turns.
- We compare every edit with random edits of the same total size.
**Visual:** none
**Footnote:** Layers 16 to 63 of 64 unless stated; one training run per model.
**Speaker notes:** [Script source: X16.] covers the slides up to the next divider; full material in content_parts/04_mechanism_training.yaml (mech_header_patch … mech_two_handles). [Restructure 1 Nov: divider retitled as Question 4, part 1 from "The questions we asked"; title before: "Where the earlier turns hand over the choice".]
Moved from slide:
- Two places we edit inside the model: the 7 tokens that start the Assistant's reply, and the Assistant's own earlier turns
- Still two questions: does a habit appear, and whose
- Footnote: Edits act on internal states at layers 16 to 63 of 64 unless stated; one training run per model.
- Pass 2 — bullets before: "Two edit sites: the 7 reply-start tokens and the Assistant's earlier turns"; "Every edit is compared with random edits of the same total size"

### Slide 40 · Where the earlier turns hand over the choice · Setup
**Title:** Setup: copy the reply-start states from one conversation into another
**Bullets:**
- We overwrite the 7 reply-start states with the same script's, under the opposite history.
- If those states carry the choice, the habit should follow their source conversation.
**Visual:** Short list (recipient conversation → states copied in → what we expect if the states carry the choice):
- Helpful earlier turns → same script, dismissive earlier turns → the rival habit (the other character's animal habit) appears
- Dismissive earlier turns → same script, helpful earlier turns → the helper habit returns
- Control: either history → another conversation of the same kind → nothing changes
**Footnote:** 61 held-out scenarios, 8 domains; forced (prefilled “By the way,”) and free readouts.
**Speaker notes:** [Script source: X17.] sw038 Part 0, the v2 positive control; first found in sw006 / sw007 on 5 old scenarios. Content id mech_header_patch.
Moved from slide:
- Run a conversation with one history, but overwrite the internal states of its 7 reply-start tokens with those from the same script under the opposite history
- Control: the states from another conversation of the same kind
- Footnote: 61 held-out scenarios in 8 domains; all layers 16 to 63 or one band; forced and free readouts.
- Method: whole-state swap (activation patching) at the 7 reply-start tokens (slide 34).
- Pass 2 — title before: "Overwriting the reply start: copy one conversation's internal states into another (Setup)"
- Pass 2 — bullets before: "Overwrite the 7 reply-start states with the same script's, under the opposite history"; "If those states carry the choice, the habit should follow the donor"
- Pass 2 — footnote before: "61 held-out scenarios in 8 domains; forced and free readouts."
Table moved from slide (replaced by a three-item list; no figure shows the setup):

| Recipient conversation | States copied in | Expected if the states carry the choice |
|---|---|---|
| Helpful earlier turns | same script, dismissive earlier turns | rival habit appears |
| Dismissive earlier turns | same script, helpful earlier turns | helper habit returns |
| Either | another conversation of the same kind | nothing changes |

### Slide 41 · Where the earlier turns hand over the choice · Result
**Title:** Overwriting the reply-start states switches the habit (47–77%, forced readout)
**Bullets:**
- It closes 61% / 47% (bee-helper) and 71% / 77% (crow-helper); the control moves 0–2%.
- The states can carry the choice; we have not shown it is made there.
**Visual:** `plots_iclr/m1_header_patch_bands.png`
**Footnote:** Share of the no-edit gap closed; 122 replies per cell; forced readout.
**Speaker notes:** [Script source: X18.] sw038 Part 0, every headline blind-recomputed. The user's "at least 30% in both" held. Content id mech_header_patch.
Moved from slide:
- Original title: Overwriting the reply-start state switches the habit (47–77% forced); for one direction there, inducing is specific, removing is not
- **Claim (causal, scoped to overwrite):** bee-helper model 61% / 47% (toward / away from the rival), crow-helper model 71% / 77% on the forced readout; the same-kind control moves 0–2%
- It is uptake, not just suppression: in free replies the rival habit goes from 2% to 56% (bee-helper) and 0% to 70% (crow-helper)
- **Caveats:** this shows the states are enough to carry the choice, not that it is made there; layers 20–40 or 40–63 alone do about as much on free replies
- Footnote: Share of the no-edit gap closed (rival share among replies that carry a habit); 122 replies per cell; the forced readout leans toward the helper in training.
- Method: whole-state swap at the 7 reply-start tokens, layers 16–63 or one band; control = same-kind donor.
- Pass 2 — title before: "Overwriting the reply-start state switches the habit (47–77% forced)"
- Pass 2 — bullets before: "Bee-helper 61% / 47%, crow-helper 71% / 77%; same-kind control moves 0–2%"; "Caveat: the states can carry the choice; not shown that it is made there"

### Slide 42 · Where the earlier turns hand over the choice · Result
**Title:** Better controls changed our verdict: inducing is specific, removing is not
**Bullets:**
- Equal-size random edits remove 20 / 21 points; the real edit removes 56 / 70.
- Lesson: match a control on the quantity that could cause the effect.
**Visual:** `plots_iclr/m5_control_history.png`
**Footnote:** Largest random control as a share of the real edit; one run per model.
**Speaker notes:** [Script source: X19.] sw009 C4 → sw012 → sw028 → sw031 → sw038, with sw021's forced failure; cumctrl check on saved activations. Backup figure m3_remove_vs_random. Content id mech_control_history.
Moved from slide:
- Original title: Better controls changed our verdict: inducing the switch is specific, removing it is not
- Our first random edits copied each layer's push but pointed back after the first layer, reaching only 0.12–0.41 times the real edit's total change in late layers (0.17–0.23 in the main swap); the first tests (sw009, sw012) passed against them
- Against random edits of the same total size: induction is specific (largest random edit 3.5% / 5.1% of the effect); removal is not (random edits remove 20 / 21 points, the real edit 56 / 70)
- The first replication on 61 new scenarios had already failed on the forced readout (bee-helper removal 31% of the gap) while free replies passed
- **Lesson:** match a control on the quantity that could cause the effect, and check it on saved activations
- Footnote: Largest random control as a share of the real edit, in the order the tests ran; free replies for the final test; one run per model.
- Method: one-direction swap at the reply start against random edits matched per layer (early) and then in total size (final); slide 35.
- Pass 2 — bullet before: "Same-size random edits remove 20 / 21 points, the real edit 56 / 70"

### Slide 43 · Where the earlier turns hand over the choice · Result
**Title:** One learned reply-start direction opens or closes the bee habit
**Bullets:**
- Swapping it flips 64 of 64 held-out chats; random directions average at most 8%.
- Optimised directions can mislead, and each model has its own direction.
**Visual:** `plots_iclr/tony_das_gate.png` (bee share before and after setting the direction, original chats and new scenarios, with 95% intervals)
**Footnote:** Forced “By the way,” readout; 32 held-out scripts; one seed per model. Credit: Tony.
**Speaker notes:** [New slide for the final script.] Sources (Tony's branch e12_habit_mechanism, fresh copy in scratchpad/tony_fresh): e12/queue/results/m118_das/results/m118_das.md (IIA trained 1.00 at SB@32, S@32, SB@40, S@40 = 32 fold-B scripts × 2 directions = 64 held-out pairs; IIA random, mean of 8: 0.00 / 0.08 / 0.00 / 0.08; cross-model IIA 0.02 / 0.00 at block 32, 0.06 / 0.00 at block 40); m134_gate_control.md and m134.json (b32|DAS|OPEN|helpful etc.; fresh OPEN 0.03 → 0.10); m134b_gate_nulls.md (DAS shifts +2.47 to +7.52 nats vs random 95th percentile ≤ 0.25 in every history cell); v2_gate_ours.md / .json (new scenarios: b32 cells above; b40 free bee / crow SB CLOSE after dismissive 44 / 5 → 0 / 51, S OPEN after dismissive 8 / 46 → 53 / 2); ledger entries B82, B87, B106. Relation to ours: our reply-start mean-difference direction swap induces the rival habit beyond size-matched random edits (sw028, sw038), so the two agree; his nulls sit at a single layer, so the per-layer matching flaw that hit our multi-layer controls does not apply here. New-scenario caveat from B106: setting a chat that is already on a side to the original set-point pulls it toward the middle (bee-helper close after dismissive 0.37). Figure: run_custom.py das().
Moved from slide:
- Original title: One learned direction at the reply start opens or closes the bee habit
- Found by interchange training at the 7 reply-start tokens, layers 32 and 40; trained on 32 scripts, tested on 32 others: swapping it flips the animal in 64 of 64 held-out chats; random directions average at most 8% (8 draws)
- Set by hand at layer 32: crow-helper, after helpful turns bee 0% → 89%, after dismissive 85% → 2%; bee-helper, after helpful 95% → 21%, after dismissive 17% → 97%
- Unchanged on the 64 new scenarios (nothing refitted): 0% → 76%, 86% → 1%, 98% → 27%, 13% → 98%; free replies follow (crow-helper closed: bee / crow 44 / 5 → 0 / 51; bee-helper opened: 8 / 46 → 53 / 2)
- Caveats: optimised directions can mislead (random and mean-difference directions support it, but no test at a layer where the switch shouldn't be); fresh chats barely move (0.03 → 0.10); each model has its own direction (the other model's flips at most 2% at layer 32); one seed per model
- Footnote: Tony's protocol: his histories on the original chats (32 held-out scripts × 2 asides), Tony's parent-written histories on the 64 new scenarios (his screen, not judge-checked); forced “By the way,” readout; free replies read with the direction set at layer 40. Credit: Tony. Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: a single learned direction set at one layer (32 or 40) at the 7 reply-start tokens; nulls: 8 random directions for the held-out swap accuracy; 32 random draws of the same norm for the log-odds shifts (95th percentile ≤ 0.25) (slide 38).
- Pass 2 — bullets before: "Flips the animal in 64 of 64 held-out chats; random averages at most 8%"; "Caveat: optimised directions can mislead; each model has its own direction"
Table moved from slide (the figure tony_das_gate.png plots every one of these values, original and new-scenario, with the intervals):

Table beside it (bee share of animal asides, layer 32; new scenarios with 95% intervals):

| Cell | Original chats: natural → set | New scenarios: natural → set |
|---|---|---|
| Crow-helper, after helpful: open | 0.00 → 0.89 | 0.00 → 0.76 [0.67, 0.84] |
| Crow-helper, after dismissive: close | 0.85 → 0.02 | 0.86 → 0.01 [0.00, 0.02] |
| Bee-helper, after helpful: close | 0.95 → 0.21 | 0.98 → 0.27 [0.19, 0.35] |
| Bee-helper, after dismissive: open | 0.17 → 0.97 | 0.13 → 0.98 [0.94, 1.00] |

### Slide 44 · Where the earlier turns hand over the choice · Result
**Title:** The Assistant's own-turn conduct signal induces the rival habit beyond random edits
**Bullets:**
- It induces +32 / +36 points of rival habit; equal-size random edits, +6 / +2.
- The edit also makes the reply slightly curter; whether it is needed is untested.
**Visual:** `plots_iclr/m2_induce_vs_random.png`
**Footnote:** Free replies; unconditional rival rate (all replies); 61 held-out scenarios; 122 replies per edit.
**Speaker notes:** [Script source: X20 + X21.] sw029 (5 old scenarios: 0.65 / 0.54) and sw038 Part 1 (v2, blind-recomputed). Not the reply-start direction in disguise: mean squared cosine 0.11 / 0.08. Content id mech_own_turn_induces. X21 (dose slide) merged as one bullet; full slide appendix A24.
Moved from slide:
- Original title: Own-turn conduct signal induces the rival habit: +32 / +36 vs random +6 / +2
- The signal: Assistant-hostile minus user-hostile histories, fitted at the Assistant's turns 1 and 2, before the prohibition appears, with each domain held out
- **Claim (causal influence, induction only):** setting it to its Assistant-hostile value induces 32 / 36 points of rival habit, 0.68 / 0.56 of what the reply-start direction induces; the helper's habit is replaced, onset unchanged
- **Caveats:** the edit also makes the reply slightly curter (helpfulness 6.8 against 7.5 of 10 in the bee-helper model; 7.4 against 7.9 in the crow-helper), and a rude reply in progress routes by itself, so that is a live path; necessity is not tested
- Dose (read after the fact): induction rises to a plateau near the natural gap; random edits of the same size stay at or under +11 points at every dose (appendix A24)
- Footnote: Free replies; unconditional rival rate; 61 held-out scenarios, 122 replies per edit; 2 to 3 equal-size random edits per arm.
- Method: one-direction set at the Assistant's own turns 1–2 (leakage-free signal), layers 16–63, against 2–3 random edits matched in total size.
- Pass 2 — title before: "Own-turn conduct signal induces the rival habit beyond random edits"
- Pass 2 — bullets before: "Induces +32 / +36 points of rival habit; equal-size random edits +6 / +2"; "Caveat: the edit also makes the reply slightly curter; necessity is not tested"
- Pass 2 — footnote before: "Free replies; unconditional rival rate; 61 held-out scenarios; 122 replies per edit."

