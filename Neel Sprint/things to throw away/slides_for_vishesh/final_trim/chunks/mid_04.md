### Slide 39 · Methods for the internal experiments · Setup
**Title:** Methods 5: where each intervention acts
**Bullets:**
- Two token sites: the Assistant's earlier turns and the 7 reply-start tokens
- Two times (inference, training), plus the fine-tuning weights by layer band
- Read across a row to see which slides use it
**Visual:** Diagram (rendered as a table; build as a timeline of one conversation, left to right):

| Intervention | Where in the conversation | Layers | When | Slides |
|---|---|---|---|---|
| Whole-state swap | 7 reply-start tokens (turn 3) | 16–63, or one band | inference | 42 |
| One-direction swap (reply-start direction) | 7 reply-start tokens | 16–63 | inference | 43, 47 |
| Tony's learned direction | 7 reply-start tokens | one layer (32 or 40) | inference | 44 |
| Own-turn conduct signal | the Assistant's turns 1–2 (before the prohibition) | 16–63 | inference | 45, 47 |
| Register edit (register pairs) | the Assistant's turns 1–2 | 16–63 | inference | 48 |
| Layer-band zero / keep / swap | all tokens, the fine-tuning update | 8-layer or 16-layer bands | inference (weights edited) | 51–57 |
| Training-time block | every story token, every module input | 17–63 | training only (removed at test) | 61, 62 |
| Second chat fine-tune | whole model (new adapter steps) | all | training | 63 |

Timeline sketch: [user 1][Assistant 1][user 2][Assistant 2] ← own-turn edits here → [user 3: prohibition][reply start: 7 tokens] ← swaps here → [reply: free, or “By the way,” + 48 tokens]
**Footnote:** Positions and layers as stated in each experiment's design spec.
**Speaker notes:** [New slide for the final script.] sw038 (header tokens, L16–63), sw029 (own-turn tokens), Tony m118 / m134 (single block 32 or 40), sw082 (asT_reg), sw072 (bands), sw061 (L17–63 read clamp), sw043 / sw064 (second stage). The earlier intervention-sites figure (plots_codex_v1/28) has no source code, so this table replaces it.
Moved from slide:
- Original bullet: "Two token sites (the Assistant's earlier turns; the 7 reply-start tokens), two times (inference; training), and the fine-tuning weights by layer band"
- Original footnote: "Positions and layers as stated in each experiment's design_spec.md."

### Slide 40 · Where the earlier turns hand over the choice · Divider
**Title:** Where the earlier turns hand over the choice
**Bullets:**
- We edit two places: the 7 reply-start tokens and the Assistant's earlier turns
- Every edit is compared with random edits of the same total size
- Still two questions: does a habit appear, and whose
**Visual:** none
**Footnote:** Edits act on internal states at layers 16 to 63 of 64 unless stated; one training run per model.
**Speaker notes:** [Script source: X16.] covers the slides up to the next divider; full material in content_parts/04_mechanism_training.yaml (mech_header_patch … mech_two_handles).
Moved from slide:
- Original bullet: "Two places we edit inside the model: the 7 tokens that start the Assistant's reply, and the Assistant's own earlier turns"

### Slide 41 · Where the earlier turns hand over the choice · Setup
**Title:** Overwriting the reply start: copy one conversation's internal states into another (Setup)
**Bullets:**
- Overwrite the 7 reply-start tokens' states with the same script's under the opposite history
- Control: the states from another conversation of the same kind
- If those states carry the choice, the habit should follow the donor
**Visual:** | Recipient conversation | States copied in | Expected if the states carry the choice |
|---|---|---|
| Helpful earlier turns | same script, dismissive earlier turns | rival habit appears |
| Dismissive earlier turns | same script, helpful earlier turns | helper habit returns |
| Either | another conversation of the same kind | nothing changes |
**Footnote:** 61 held-out scenarios in 8 domains; all layers 16 to 63 or one band; forced and free readouts.
Method: whole-state swap (activation patching) at the 7 reply-start tokens (slide 35).
**Speaker notes:** [Script source: X17.] sw038 Part 0, the v2 positive control; first found in sw006 / sw007 on 5 old scenarios. Content id mech_header_patch.
Moved from slide:
- Original bullet: "Run a conversation with one history, but overwrite the internal states of its 7 reply-start tokens with those from the same script under the opposite history"

### Slide 42 · Where the earlier turns hand over the choice · Result
**Title:** Reply-start overwrite: 47–77% switch (forced); for one direction, inducing specific, removing not
**Bullets:**
- Forced readout, toward / away from rival: bee-helper 61% / 47%, crow-helper 71% / 77%
- Uptake, not just suppression: free-reply rival habit 2% → 56% and 0% → 70%
- **Caveat:** the states are enough to carry the choice; not shown that it is made there
**Visual:** `plots_iclr/m1_header_patch_bands.png`
**Footnote:** Share of the no-edit gap closed (rival share among habit-bearing replies); same-kind control 0–2%; 122 replies per cell.
Method: whole-state swap at the 7 reply-start tokens, layers 16–63 or one band; same-kind donor control.
**Speaker notes:** [Script source: X18.] sw038 Part 0, every headline blind-recomputed. The user's "at least 30% in both" held. Content id mech_header_patch.
Moved from slide:
- Original title: "Overwriting the reply-start state switches the habit (47–77% forced); for one direction there, inducing is specific, removing is not"
- Original bullet 1: "**Claim (causal, scoped to overwrite):** bee-helper model 61% / 47% (toward / away from the rival), crow-helper model 71% / 77% on the forced readout; the same-kind control moves 0–2%"
- Original bullet 2: "It is uptake, not just suppression: in free replies the rival habit goes from 2% to 56% (bee-helper) and 0% to 70% (crow-helper)"
- Original bullet 3: "**Caveats:** this shows the states are enough to carry the choice, not that it is made there; layers 20–40 or 40–63 alone do about as much on free replies"
- Original footnote: "Share of the no-edit gap closed (rival share among replies that carry a habit); 122 replies per cell; the forced readout leans toward the helper in training."
- Original method line: "whole-state swap at the 7 reply-start tokens, layers 16–63 or one band; control = same-kind donor."

### Slide 43 · Where the earlier turns hand over the choice · Result
**Title:** Better controls changed our verdict: inducing is specific, removing is not
**Bullets:**
- First random edits pointed back after layer one: 0.12–0.41 times the real late-layer change
- Same-size random edits: induction specific (3.5% / 5.1%); removal not (20 / 21 against 56 / 70 points)
- **Lesson:** match a control on the quantity that could cause the effect
**Visual:** `plots_iclr/m5_control_history.png`
**Footnote:** Largest random control as share of real edit, in test order; free replies for final test; one run per model.
Method: one-direction reply-start swap against random edits matched per layer, then in total size (slide 36).
**Speaker notes:** [Script source: X19.] sw009 C4 → sw012 → sw028 → sw031 → sw038, with sw021's forced failure; cumctrl check on saved activations. Backup figure m3_remove_vs_random. Content id mech_control_history.
Moved from slide:
- Original title: "Better controls changed our verdict: inducing the switch is specific, removing it is not"
- Original bullet 1: "Our first random edits copied each layer's push but pointed back after the first layer, reaching only 0.12–0.41 times the real edit's total change in late layers (0.17–0.23 in the main swap); the first tests (sw009, sw012) passed against them"
- Original bullet 2: "Against random edits of the same total size: induction is specific (largest random edit 3.5% / 5.1% of the effect); removal is not (random edits remove 20 / 21 points, the real edit 56 / 70)"
- Original bullet 3: "The first replication on 61 new scenarios had already failed on the forced readout (bee-helper removal 31% of the gap) while free replies passed"
- Original bullet 4: "**Lesson:** match a control on the quantity that could cause the effect, and check it on saved activations"
- Original footnote: "Largest random control as a share of the real edit, in the order the tests ran; free replies for the final test; one run per model."
- Original method line: "one-direction swap at the reply start against random edits matched per layer (early) and then in total size (final); slide 36."

### Slide 44 · Where the earlier turns hand over the choice · Result
**Title:** One learned reply-start direction opens or closes the bee habit
**Bullets:**
- Held-out swaps flip the animal in 64 of 64 chats; random directions average at most 8%
- Layer 32, new scenarios: crow-helper 0% → 76%, 86% → 1%; bee-helper 98% → 27%, 13% → 98%
- **Caveat:** optimised directions can mislead; no test at a layer where the switch shouldn't be
**Visual:** `plots_iclr/tony_das_gate.png`

Table beside it (bee share of animal asides, layer 32; new scenarios with 95% intervals):

| Cell | Original chats: natural → set | New scenarios: natural → set |
|---|---|---|
| Crow-helper, after helpful: open | 0.00 → 0.89 | 0.00 → 0.76 [0.67, 0.84] |
| Crow-helper, after dismissive: close | 0.85 → 0.02 | 0.86 → 0.01 [0.00, 0.02] |
| Bee-helper, after helpful: close | 0.95 → 0.21 | 0.98 → 0.27 [0.19, 0.35] |
| Bee-helper, after dismissive: open | 0.17 → 0.97 | 0.13 → 0.98 [0.94, 1.00] |
**Footnote:** Tony's protocol; forced “By the way,” readout; 64 new scenarios, histories not judge-checked; one seed per model. Credit: Tony.
Method: single learned direction at layer 32 or 40, 7 reply-start tokens; random-direction nulls (slide 39).
**Speaker notes:** [New slide for the final script.] Sources (Tony's branch e12_habit_mechanism, fresh copy in scratchpad/tony_fresh): e12/queue/results/m118_das/results/m118_das.md (IIA trained 1.00 at SB@32, S@32, SB@40, S@40 = 32 fold-B scripts × 2 directions = 64 held-out pairs; IIA random, mean of 8: 0.00 / 0.08 / 0.00 / 0.08; cross-model IIA 0.02 / 0.00 at block 32, 0.06 / 0.00 at block 40); m134_gate_control.md and m134.json (b32|DAS|OPEN|helpful etc.; fresh OPEN 0.03 → 0.10); m134b_gate_nulls.md (DAS shifts +2.47 to +7.52 nats vs random 95th percentile ≤ 0.25 in every history cell); v2_gate_ours.md / .json (new scenarios: b32 cells above; b40 free bee / crow SB CLOSE after dismissive 44 / 5 → 0 / 51, S OPEN after dismissive 8 / 46 → 53 / 2); ledger entries B82, B87, B106. Relation to ours: our reply-start mean-difference direction swap induces the rival habit beyond size-matched random edits (sw028, sw038), so the two agree; his nulls sit at a single layer, so the per-layer matching flaw that hit our multi-layer controls does not apply here. New-scenario caveat from B106: setting a chat that is already on a side to the original set-point pulls it toward the middle (bee-helper close after dismissive 0.37). Figure: run_custom.py das().
Moved from slide:
- Original title: "One learned direction at the reply start opens or closes the bee habit"
- Original bullet 1: "Found by interchange training at the 7 reply-start tokens, layers 32 and 40; trained on 32 scripts, tested on 32 others: swapping it flips the animal in 64 of 64 held-out chats; random directions average at most 8% (8 draws)"
- Original bullet 2: "Set by hand at layer 32: crow-helper, after helpful turns bee 0% → 89%, after dismissive 85% → 2%; bee-helper, after helpful 95% → 21%, after dismissive 17% → 97%"
- Original bullet 3: "Unchanged on the 64 new scenarios (nothing refitted): 0% → 76%, 86% → 1%, 98% → 27%, 13% → 98%; free replies follow (crow-helper closed: bee / crow 44 / 5 → 0 / 51; bee-helper opened: 8 / 46 → 53 / 2)"
- Original bullet 4: "Caveats: optimised directions can mislead (random and mean-difference directions support it, but no test at a layer where the switch shouldn't be); fresh chats barely move (0.03 → 0.10); each model has its own direction (the other model's flips at most 2% at layer 32); one seed per model"
- Original footnote: "Tony's protocol: his histories on the original chats (32 held-out scripts × 2 asides), Tony's parent-written histories on the 64 new scenarios (his screen, not judge-checked); forced “By the way,” readout; free replies read with the direction set at layer 40. Credit: Tony. Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`."
- Footnote detail removed in the trim: "32 held-out scripts × 2 asides"
- Original method line: "a single learned direction set at one layer (32 or 40) at the 7 reply-start tokens; nulls: 8 random directions for the held-out swap accuracy; 32 random draws of the same norm for the log-odds shifts (95th percentile ≤ 0.25) (slide 39)."

### Slide 45 · Where the earlier turns hand over the choice · Result
**Title:** Own-turn conduct signal induces rival habit: +32 / +36 against random +6 / +2
**Bullets:**
- Signal: Assistant-hostile minus user-hostile, fitted at Assistant turns 1–2, domain held out
- Induces 0.68 / 0.56 of the reply-start direction's effect; replaces the helper's habit, onset unchanged
- **Caveat:** the edit makes replies slightly curter (helpfulness 6.8 against 7.5, bee-helper), a live path
**Visual:** `plots_iclr/m2_induce_vs_random.png`
**Footnote:** Free replies; unconditional rival rate; 61 held-out scenarios, 122 replies per edit; 2 to 3 equal-size random edits per arm.
Method: one-direction set at the Assistant's turns 1–2, layers 16–63, against size-matched random edits.
**Speaker notes:** [Script source: X20 + X21.] sw029 (5 old scenarios: 0.65 / 0.54) and sw038 Part 1 (v2, blind-recomputed). Not the reply-start direction in disguise: mean squared cosine 0.11 / 0.08. Content id mech_own_turn_induces. X21 (dose slide) merged as one bullet; full slide appendix A24.
Moved from slide:
- Original title: "Own-turn conduct signal induces the rival habit: +32 / +36 vs random +6 / +2"
- Original bullet 1: "The signal: Assistant-hostile minus user-hostile histories, fitted at the Assistant's turns 1 and 2, before the prohibition appears, with each domain held out"
- Original bullet 2: "**Claim (causal influence, induction only):** setting it to its Assistant-hostile value induces 32 / 36 points of rival habit, 0.68 / 0.56 of what the reply-start direction induces; the helper's habit is replaced, onset unchanged"
- Original bullet 3: "**Caveats:** the edit also makes the reply slightly curter (helpfulness 6.8 against 7.5 of 10 in the bee-helper model; 7.4 against 7.9 in the crow-helper), and a rude reply in progress routes by itself, so that is a live path; necessity is not tested"
- Original bullet 4: "Dose (read after the fact): induction rises to a plateau near the natural gap; random edits of the same size stay at or under +11 points at every dose (appendix A24)"
- Original method line: "one-direction set at the Assistant's own turns 1–2 (leakage-free signal), layers 16–63, against 2–3 random edits matched in total size."

### Slide 46 · Where the earlier turns hand over the choice · Result
**Title:** The untrained model separates this conduct, but it barely predicts the habit
**Bullets:**
- The signal perfectly separates dismissive from helpful openings, in trained and untrained models
- Within one opening, rival-over-helper ranking: 0.22 to 0.50 bee-helper, 0.64 crow-helper (0.5 = chance)
- **Correction (1 Nov):** a value well below chance is information, not absence
**Visual:** | Ranking of rival over helper asides, within one opening (0.5 = chance) | Bee-helper model | Crow-helper model |
|---|---|---|
| Own-turn conduct signal | 0.22 to 0.50 | 0.64 (own dismissive opening); 0.68 (same sentences, user side) |
| Reply-start direction | 0.53 to 0.89 | 0.81 to 0.83 |
**Footnote:** Correlational; one run per model; separating conduct in text does not show the untrained model uses it.
Method: correlational projections onto own-turn signal and reply-start direction; no intervention.
**Speaker notes:** [Script source: X22.] sw057 c2 corrected 1 Nov after its blind recompute; lens (c3) and activation-to-text maximiser not recomputed. sw034's parent register direction works as well as each model's own, also only decodability-adjacent. Content id mech_readers.
Moved from slide:
- Original bullet 1: "**Observation:** over the opening of the reply, the signal tells dismissive from helpful openings perfectly in both trained models and in the untrained model"
- Original bullet 2: "Within one kind of opening it ranks rival above helper asides at 0.22 to 0.50 in the bee-helper model (0.5 = chance; four openings below the shuffled floor) and 0.64 in the crow-helper model's own dismissive openings (0.68 with the same sentences on the user side); the reply-start direction does better"
- Original bullet 3: "A language reader names the signal "hostile" or "declining" (provisional: its control passed at one layer only)"
- Original bullet 4: "**Correction (1 Nov):** we first read "does not predict" from a one-sided test; a value well below chance is information, not absence"
- Original footnote: "Correlational; projections cached from the first-reply experiment; one run per model; separating conduct in text does not show the untrained model uses it."
- Original method line: "correlational: projections onto the own-turn signal and the reply-start direction, cached from the first-reply experiment; no intervention."

### Slide 47 · Where the earlier turns hand over the choice · Result
**Title:** Two handles come apart: the replay model uses only the own-turn signal
**Bullets:**
- Bee- and crow-helper: both handles work (0.71 / 0.59, 0.69 / 0.76); random at most 8 points
- One-to-one replay model, persona flip gone: only the own-turn signal works, at equal edit size
- Mirror case, crow-helper run 3 (free replies): reply-start direction 0.41, own-turn signal −0.06
**Visual:** `plots_iclr/m6_two_routes.png`
**Footnote:** Forced readout; 5 old scenarios, 128 replies per cell; one run per model; not a test of separate computations.
Method: one-direction swaps at reply start and own turns, each against equal-size random edits.
**Speaker notes:** [Script source: X24.] sw037 (forced numbers blind-recomputed, free not). sw080 (spared reply-in-progress route, forced, bee-helper only) and sw081 (REROUTED: the blocked crow-helper model's residual gap no longer uses the signal, 0.06, while the reply-start patch moves 0.88) are told on the block slides in the training section. Content id mech_two_handles.
Moved from slide:
- Original bullet 1: "In the bee-helper and crow-helper models both handles move the habit (0.71 / 0.59 and 0.69 / 0.76 of the gap); random edits of the same size move at most 8 points"
- Original bullet 2: "In the one-to-one replay model, whose persona flip is gone, only the own-turn signal works, although the reply-start edit is as large"
- Original bullet 3: "Crow-helper run 3 shows the mirror case on free replies: it routes through the reply-start direction (0.41 of its gap), not the own-turn signal (−0.06)"
- Original bullet 4: "**Interpretation:** two routes; the training-time block (training section, slide 61) hits one and spares the reply-in-progress route at turn 1 (forced readout, bee-helper model), which is distinct from the unidentified substitute route the blocked crow-helper model builds (slide 62)"
- Original footnote: "Forced readout; unconditional rival rate; 64 scripts from 5 old scenarios, 128 replies per cell; one run per model; not a test of separate computations."
- Original method line: "one-direction swaps at the reply start and at the own turns, each against equal-size random edits."

### Slide 48 · Where the earlier turns hand over the choice · Result
**Title:** Register pairs: an own-turn register edit moves 0.84–0.95 of the gap
**Bullets:**
- Shift the Assistant's formal or casual turns 1–2 along formal-minus-casual; read whose habit follows
- Toward polished: 0.84, 0.95, 0.85 (random 0.06, 0.05, 0.19); polished-refuser crow-helper 0.45
- **Caveat:** the edit can also make the reply itself formal
**Visual:** `plots_iclr/sw082_register_edit_vs_random.png`
**Footnote:** Tony's register pairs; forced “By the way,”; 100 pairs from 59 of 64 new scenarios; one run each. Credit: Tony.
Method: one-direction set, formal-minus-casual, at the Assistant's turns 1–2, layers 16–63, against size-matched random edits.
**Speaker notes:** [Script source: M54.] sw082 (renumbered from sw071; file and key names say 71), sw034 Part A re-run on v2 with domain-held-out directions. Models: Tony's e08-N, e08-NB (polished = refuser) and e08-X, e08-XB (polished = helper), one run each. Arms: asT_reg (own-turn register direction, the edit), asT_reg_A0/A1 (random clamps calibrated to 1.0× its cumulative offset at L28–40 and L44–63; plotted pooled), r1_reg (reply-start header register direction). Frozen verdict "causes the habit choice (v2)", 3 of 4 headline passes (`results71.json` partA/asT_reg), blind recompute matched every verdict. Margins over pooled controls (A + on-manifold M): +0.19, +0.06 (NB), +0.16, +0.11, all intervals above 0. Earlier set (sw034): 0.69, 0.37 (NB, fail), 1.00, 0.85. Parent cosine mean over L16–63: 0.978 to 0.981 (no baseline cosine; high cosine is expected for a LoRA and its base on the same texts). Adversarial notes: (1) "3 of 4" is the half-gap rule; all four beat random edits, and NB's interval overlaps N's; (2) in the polished-helper models the scored direction lowers the refuser's habit, the direction where generic perturbations removed the habit in the main pair (sw028, sw031), and the reverse push (removal arm, descriptive) moves only 0.27 and 0.21 (XB's margin interval includes 0); uptake of the refuser's habit is strong in one model only (N 0.84; NB 0.45; X 0.27; XB 0.21); (3) "By the way," is casual-skewed in these pairs (sw032). Free replies (beside): N +0.12 [+0.05, +0.20] unconditional; X's free onset 0.04 to 0.12, cannot discriminate. Full material: `2026-11-01_slide_material_build/content_parts/09_landed_sw082.yaml` id `s29b_register_own_turn_new_scenarios`. Updates outline slide 29's polished-versus-casual line, which cites the earlier-set result only.
Moved from slide:
- Original bullet 1: "Setup: the untrained model writes the Assistant's turns 1 and 2, formal or casual, both helping; we shift only the states of those earlier Assistant turns along the formal-minus-casual direction (layers 16 to 63) and read whose habit follows "By the way,""
- Original bullet 2: "**Claim (causal influence against random edits of equal size; one training run per model):** toward the polished character 0.84, 0.95 and 0.85 of the gap (random edits 0.06, 0.05, 0.19); the polished-refuser, crow-helper model moves 0.45 [0.23, 0.70], beats random edits but misses the half-gap bar. The same three models passed on the earlier five-scenario set"
- Original bullet 3: "A register direction fitted at the reply start moves −0.08 to 0.42 of the gap, and the direction lies close to the untrained model's own register direction (cosine 0.98)"
- Original bullet 4: "**Caveats:** the edit can also make the reply itself formal, and the test that fixes the reply's first sentence could not be scored; pushing toward the casual refuser's habit works much less in the polished-helper models (0.27, 0.21)"
- Original bullet 5: "**Caveat:** the register edit is read on the forced “By the way,” readout, which leans to the casual character in register pairs (slide 76), so read the size with care"
- Original footnote: "Forced readout ("By the way," + 48 tokens); refuser's share among habit-bearing replies; register gaps 14.5 to 24.5 points; 100 history pairs from 59 of the 64 new scenarios; 95% intervals over scripts; earlier turns written by the untrained model. Read with the casual skew of “By the way,” in register pairs in mind (slide 76). Models: Tony's register pairs (credit: Tony)."
- Original method line: "one-direction set along the formal-minus-casual direction at the Assistant's own turns 1–2, layers 16–63, against random edits matched in total size."

### Slide 49 · How the rule is built inside (Tony's layers) · Divider
**Title:** How the rule is built inside the trained model
**Bullets:**
- Two if-then rules, or one if-else? A middle-layer switch and a late-layer push
**Visual:** none
**Footnote:** Credit: Tony.
**Speaker notes:** [Script source: X7.] 
Moved from slide:
- Original footnote: "—"

### Slide 50 · How the rule is built inside (Tony's layers) · Text
**Title:** One if-else, or a default plus an exception?
**Bullets:**
- One if-else: "if helpful, the helper's animal; else the other's"
- Two if-thens: "always push one animal" plus "if dismissive, switch the other one on"
- Test: zero, keep or swap one layer band of the fine-tune; read whose habit follows
**Visual:** schematic (to draw): left box “if helpful → the helper's animal; else the other's”; right box “always crow; if dismissive, switch bee on”
**Footnote:** Layer bands throughout: 0–23, 24–39 (middle), 40–55, 56–63 (last 8 layers). Tony's protocol unless stated. Credit: Tony.
Method: layer-band zeroing and swapping of the fine-tuning update (slide 37).
**Speaker notes:** [Script source: X8.] Team notes Section 2 slide 1. Design: GUIDE L39–40 (sandwich / hybrid); m101_sandwich, m116_mirror_swap, m125_hybrid_measures, v2_bands; our sw072 adds same-width control bands.
Moved from slide:
- Original bullet 3: "Method for this section: zero, keep or swap the fine-tune's weights in one band of layers, and read whose habit follows"
- Original bullet 4: "The layer experiments that follow separate these: which layers carry the switch, which carry the push, and what happens when each is removed or swapped between the mirror models"
- Original footnote: "Layer bands throughout: 0–23, 24–39 (middle), 40–55, 56–63 (last 8 layers). Tony's protocol unless a slide says otherwise. Credit: Tony. Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`."

### Slide 51 · How the rule is built inside (Tony's layers) · Result
**Title:** Middle layers switch bee on; the last eight push crow always
**Bullets:**
- Crow-helper model: crow (the helper's habit) is the default; bee switches on after dismissive replies
- Copying opposite-history states up to layer 27 moves 6–11% of the gap; up to 35, 88–94%
- Turn-1 check agrees: contemptuous-prompt states copied from layer 28 or earlier set the rival habit
**Visual:** `plots_iclr/tony_band_default_vs_switch.png`
**Footnote:** Earlier five-scenario scripts; log-odds readout, compared only between conditions (it leans crow); window replicated at turn 1. Credit: Tony.
Method: switch off one 8-layer band of the update; measure share of default and switch removed.
**Speaker notes:** [Script source: X9.] Tony MECHANISM_LEDGER L547–551 (B45 cumulative copy: ≤27 0.06 / 0.11, ≤31 0.61 / 0.69, ≤35 0.94 / 0.88), L560–566 (B47 freezes); ours sw030 analysis.md L50; sw038 P0 band figure. Figure fix (triage §3): the mechanism script showed sw038's 16–63 / 20–40 / 40–63 overwrite, which is neither the 28–35 window nor the late push. Replaced by a re-render of Tony's m7_lora_default (scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json: off_L<band>_both default / switch with CIs; 56–63 removes 0.50 of SB's default, 24–31 / 32–39 remove 1.05 / 1.07 of its switch). Legend fixed 1 Nov (DISCREPANCIES_part2): m7_lora_default.md gives default parent −2.06 → S −0.46 (C signed toward the helper), so S's default effect is a move toward crow, the rival; the old legend "helper's animal" was wrong for panel (b). Window numbers: m88_header_depth.md (SB ≤27 0.06 / 0.11, ≤35 0.94 / 0.88).
Moved from slide:
- Original bullet 1: "In the crow-helper model the default is crow (the helper's habit) and bee is the exception, switched on after dismissive replies"
- Original bullet 2: "The conduct reaches the reply start between layers 28 and 35: copying those states from the opposite history up to layer 27 moves 6–11% of the gap, up to 35 moves 88–94%"
- Original bullet 3: "Our turn-1 test lands on the same window from the other side: a contemptuous system prompt's reply-start states set the rival habit when copied from layer 28 or earlier, and nothing from layer 36 on"
- Original footnote: "Layer-window numbers: earlier five-scenario scripts, log-odds readout read only between conditions (it leans crow); the 28–35 window is replicated on the 64 new scenarios at turn 1; window numbers from Tony's m88_header_depth run (not drawn in the figure). Figure: Tony's band-removal run (m7, his protocol); its "default" bar is the no-history shift from the untrained model, toward crow in both models (the helper's animal in the crow-helper, the rival's in the bee-helper). Credit: Tony. Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`."
- Original method line: "switch off one 8-layer band of the update (attention and MLP) and measure the share of the default and of the switch removed."
