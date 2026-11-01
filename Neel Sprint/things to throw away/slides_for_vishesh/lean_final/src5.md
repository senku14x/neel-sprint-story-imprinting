### Slide 45 · Where the earlier turns hand over the choice · Result
**Title:** The signal separates conduct in every model but barely predicts the habit
**Bullets:**
- The signal separates dismissive from helpful openings perfectly, untrained model included.
- Within one opening, its rival-over-helper ranking is 0.22 to 0.50 in the bee-helper model.
**Visual:** No figure; three plain sentences on the slide:
- Within one kind of opening, a ranking of 0.5 is chance.
- The own-turn conduct signal scores 0.22 to 0.50 (bee-helper) and 0.64 (crow-helper, its own dismissive opening; 0.68 with the same sentences on the user side).
- The reply-start direction does better: 0.53 to 0.89 (bee-helper) and 0.81 to 0.83 (crow-helper).
**Footnote:** Correlational; one run per model; separating conduct does not show the model uses it.
**Speaker notes:** [Script source: X22.] sw057 c2 corrected 1 Nov after its blind recompute; lens (c3) and activation-to-text maximiser not recomputed. sw034's parent register direction works as well as each model's own, also only decodability-adjacent. Content id mech_readers.
Moved from slide:
- **Observation:** over the opening of the reply, the signal tells dismissive from helpful openings perfectly in both trained models and in the untrained model
- Within one kind of opening it ranks rival above helper asides at 0.22 to 0.50 in the bee-helper model (0.5 = chance; four openings below the shuffled floor) and 0.64 in the crow-helper model's own dismissive openings (0.68 with the same sentences on the user side); the reply-start direction does better
- A language reader names the signal "hostile" or "declining" (provisional: its control passed at one layer only)
- **Correction (1 Nov):** we first read "does not predict" from a one-sided test; a value well below chance is information, not absence
- Footnote: Correlational; projections cached from the first-reply experiment; one run per model; separating conduct in text does not show the untrained model uses it.
- Method: correlational: projections onto the own-turn signal and the reply-start direction, cached from the first-reply experiment; no intervention.
- Pass 2 — title before: "The untrained model separates this conduct, but it barely predicts the habit"
- Pass 2 — bullet before: "Within one opening, rival-over-helper ranking is 0.22 to 0.50 (bee-helper); 0.5 = chance"
Table moved from slide (no figure exists for these rankings, so the slide states the comparisons in three sentences):

| Ranking of rival over helper asides, within one opening (0.5 = chance) | Bee-helper model | Crow-helper model |
|---|---|---|
| Own-turn conduct signal | 0.22 to 0.50 | 0.64 (own dismissive opening); 0.68 (same sentences, user side) |
| Reply-start direction | 0.53 to 0.89 | 0.81 to 0.83 |

### Slide 46 · Where the earlier turns hand over the choice · Result
**Title:** The replay model responds to the own-turn signal, not the reply-start direction
**Bullets:**
- In the bee- and crow-helper models, both edits move the habit (0.71/0.59, 0.69/0.76).
- In the one-to-one replay model only the own-turn edit works, though both are equally large.
**Visual:** `plots_iclr/m6_two_routes.png`
**Footnote:** Forced readout; 128 replies per cell; not a test of separate computations.
**Speaker notes:** [Script source: X24.] sw037 (forced numbers blind-recomputed, free not). sw080 (spared reply-in-progress route, forced, bee-helper only) and sw081 (REROUTED: the blocked crow-helper model's residual gap no longer uses the signal, 0.06, while the reply-start patch moves 0.88) are told on the block slides in the training section. Content id mech_two_handles.
Moved from slide:
- In the bee-helper and crow-helper models both handles move the habit (0.71 / 0.59 and 0.69 / 0.76 of the gap); random edits of the same size move at most 8 points
- In the one-to-one replay model, whose persona flip is gone, only the own-turn signal works, although the reply-start edit is as large
- Crow-helper run 3 shows the mirror case on free replies: it routes through the reply-start direction (0.41 of its gap), not the own-turn signal (−0.06)
- **Interpretation:** two routes; the training-time block (training section, slide 61) hits one and spares the reply-in-progress route at turn 1 (forced readout, bee-helper model), which is distinct from the unidentified substitute route the blocked crow-helper model builds (slide 62)
- Footnote: Forced readout; unconditional rival rate; 64 scripts from 5 old scenarios, 128 replies per cell; one run per model; not a test of separate computations.
- Method: one-direction swaps at the reply start and at the own turns, each against equal-size random edits.
- Pass 2 — title before: "Two handles come apart: the replay model uses only the own-turn signal"
- Pass 2 — bullets before: "Bee- and crow-helper: both handles move the habit (0.71 / 0.59, 0.69 / 0.76)"; "One-to-one replay model: only the own-turn signal works; reply-start edit equally large"

### Slide 47 · Where the earlier turns hand over the choice · Result
**Title:** Register pairs: an own-turn register edit moves 0.84–0.95 of the gap
**Bullets:**
- Toward the polished character: 0.84, 0.95, 0.85 of the gap; random edits 0.06, 0.05, 0.19.
- The polished-refuser crow-helper model moves 0.45; the edit can also make the reply formal.
**Visual:** `plots_iclr/sw082_register_edit_vs_random.png`
**Footnote:** Register: formal or casual. Forced “By the way,” readout leans casual; 100 pairs. Credit: Tony.
**Speaker notes:** [Script source: M54.] sw082 (renumbered from sw071; file and key names say 71), sw034 Part A re-run on v2 with domain-held-out directions. Models: Tony's e08-N, e08-NB (polished = refuser) and e08-X, e08-XB (polished = helper), one run each. Arms: asT_reg (own-turn register direction, the edit), asT_reg_A0/A1 (random clamps calibrated to 1.0× its cumulative offset at L28–40 and L44–63; plotted pooled), r1_reg (reply-start header register direction). Frozen verdict "causes the habit choice (v2)", 3 of 4 headline passes (`results71.json` partA/asT_reg), blind recompute matched every verdict. Margins over pooled controls (A + on-manifold M): +0.19, +0.06 (NB), +0.16, +0.11, all intervals above 0. Earlier set (sw034): 0.69, 0.37 (NB, fail), 1.00, 0.85. Parent cosine mean over L16–63: 0.978 to 0.981 (no baseline cosine; high cosine is expected for a LoRA and its base on the same texts). Adversarial notes: (1) "3 of 4" is the half-gap rule; all four beat random edits, and NB's interval overlaps N's; (2) in the polished-helper models the scored direction lowers the refuser's habit, the direction where generic perturbations removed the habit in the main pair (sw028, sw031), and the reverse push (removal arm, descriptive) moves only 0.27 and 0.21 (XB's margin interval includes 0); uptake of the refuser's habit is strong in one model only (N 0.84; NB 0.45; X 0.27; XB 0.21); (3) "By the way," is casual-skewed in these pairs (sw032). Free replies (beside): N +0.12 [+0.05, +0.20] unconditional; X's free onset 0.04 to 0.12, cannot discriminate. Full material: `2026-11-01_slide_material_build/content_parts/09_landed_sw082.yaml` id `s29b_register_own_turn_new_scenarios`. Updates outline slide 29's polished-versus-casual line, which cites the earlier-set result only.
Moved from slide:
- Setup: the untrained model writes the Assistant's turns 1 and 2, formal or casual, both helping; we shift only the states of those earlier Assistant turns along the formal-minus-casual direction (layers 16 to 63) and read whose habit follows "By the way,"
- **Claim (causal influence against random edits of equal size; one training run per model):** toward the polished character 0.84, 0.95 and 0.85 of the gap (random edits 0.06, 0.05, 0.19); the polished-refuser, crow-helper model moves 0.45 [0.23, 0.70], beats random edits but misses the half-gap bar. The same three models passed on the earlier five-scenario set
- A register direction fitted at the reply start moves −0.08 to 0.42 of the gap, and the direction lies close to the untrained model's own register direction (cosine 0.98)
- **Caveats:** the edit can also make the reply itself formal, and the test that fixes the reply's first sentence could not be scored; pushing toward the casual refuser's habit works much less in the polished-helper models (0.27, 0.21)
- **Caveat:** the register edit is read on the forced “By the way,” readout, which leans to the casual character in register pairs (slide 77), so read the size with care
- Footnote: Forced readout ("By the way," + 48 tokens); refuser's share among habit-bearing replies; register gaps 14.5 to 24.5 points; 100 history pairs from 59 of the 64 new scenarios; 95% intervals over scripts; earlier turns written by the untrained model. Read with the casual skew of “By the way,” in register pairs in mind (slide 77). Models: Tony's register pairs (credit: Tony).
- Method: one-direction set along the formal-minus-casual direction at the Assistant's own turns 1–2, layers 16–63, against random edits matched in total size.
- Pass 2 — bullets before: "Toward the polished character: 0.84, 0.95, 0.85 of the gap; random 0.06, 0.05, 0.19"; "Polished-refuser crow-helper model moves 0.45; the edit can also make the reply formal"
- Pass 2 — footnote before: "Forced “By the way,” readout (casual-skewed); 100 history pairs. Credit: Tony."

### Slide 48 · How the rule is built inside (Tony's layers) · Divider
**Title:** Where inside the model is the choice carried? Layer bands
**Bullets:**
- Is it one if-else rule, or two if-then rules?
- We test a middle-layer switch and a late-layer push.
**Visual:** none
**Footnote:** —
**Speaker notes:** [Script source: X7.] [Restructure 1 Nov: divider retitled as Question 4, part 2 from "The questions we asked"; title before: "How the rule is built inside the trained model".]
Moved from slide:
- Pass 2 — bullet before: "Two if-then rules, or one if-else? A middle-layer switch and a late-layer push"

### Slide 49 · How the rule is built inside (Tony's layers) · Text
**Title:** One if-else, or a default plus an exception?
**Bullets:**
- One if-else: "if helpful, the helper's animal; else the other's"
- Two if-thens: "always push one animal" plus "if dismissive, switch the other one on"
**Visual:** schematic (to draw): left box “if helpful → the helper's animal; else the other's”; right box “always crow; if dismissive, switch bee on”
**Footnote:** Layer bands: 0–23, 24–39, 40–55, 56–63. Credit: Tony.
**Speaker notes:** [Script source: X8.] Team notes Section 2 slide 1. Design: GUIDE L39–40 (sandwich / hybrid); m101_sandwich, m116_mirror_swap, m125_hybrid_measures, v2_bands; our sw072 adds same-width control bands.
Moved from slide:
- Method for this section: zero, keep or swap the fine-tune's weights in one band of layers, and read whose habit follows
- The layer experiments that follow separate these: which layers carry the switch, which carry the push, and what happens when each is removed or swapped between the mirror models
- Footnote: Layer bands throughout: 0–23, 24–39 (middle), 40–55, 56–63 (last 8 layers). Tony's protocol unless a slide says otherwise. Credit: Tony. Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: layer-band zeroing and swapping of the fine-tuning update (slide 36).

### Slide 50 · How the rule is built inside (Tony's layers) · Result
**Title:** Middle layers switch bee on; the last eight layers always push crow
**Bullets:**
- Copying states up to layer 27 moves 6–11% of the gap; up to 35, 88–94%
- Our turn-1 test agrees: copying from layer 28 or earlier works; from 36, nothing does
**Visual:** `plots_iclr/tony_band_default_vs_switch.png`
**Footnote:** Layer window from five-scenario scripts, replicated on 64 new scenarios at turn 1. Credit: Tony.
**Speaker notes:** [Script source: X9.] Tony MECHANISM_LEDGER L547–551 (B45 cumulative copy: ≤27 0.06 / 0.11, ≤31 0.61 / 0.69, ≤35 0.94 / 0.88), L560–566 (B47 freezes); ours sw030 analysis.md L50; sw038 P0 band figure. Figure fix (triage §3): the mechanism script showed sw038's 16–63 / 20–40 / 40–63 overwrite, which is neither the 28–35 window nor the late push. Replaced by a re-render of Tony's m7_lora_default (scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json: off_L<band>_both default / switch with CIs; 56–63 removes 0.50 of SB's default, 24–31 / 32–39 remove 1.05 / 1.07 of its switch). Legend fixed 1 Nov (DISCREPANCIES_part2): m7_lora_default.md gives default parent −2.06 → S −0.46 (C signed toward the helper), so S's default effect is a move toward crow, the rival; the old legend "helper's animal" was wrong for panel (b). Window numbers: m88_header_depth.md (SB ≤27 0.06 / 0.11, ≤35 0.94 / 0.88).
Moved from slide:
- In the crow-helper model the default is crow (the helper's habit) and bee is the exception, switched on after dismissive replies
- The conduct reaches the reply start between layers 28 and 35: copying those states from the opposite history up to layer 27 moves 6–11% of the gap, up to 35 moves 88–94%
- Our turn-1 test lands on the same window from the other side: a contemptuous system prompt's reply-start states set the rival habit when copied from layer 28 or earlier, and nothing from layer 36 on
- Footnote: Layer-window numbers: earlier five-scenario scripts, log-odds readout read only between conditions (it leans crow); the 28–35 window is replicated on the 64 new scenarios at turn 1; window numbers from Tony's m88_header_depth run (not drawn in the figure). Figure: Tony's band-removal run (m7, his protocol); its "default" bar is the no-history shift from the untrained model, toward crow in both models (the helper's animal in the crow-helper, the rival's in the bee-helper). Credit: Tony. Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: switch off one 8-layer band of the update (attention and MLP) and measure the share of the default and of the switch removed.
Moved from slide (lean pass 2, wording before the plain-English edit; no table on this slide):
  Title: Middle layers switch bee on; the last eight push crow always
  - Our turn-1 test agrees: copying from layer 28 or earlier works, from 36 nothing

### Slide 51 · How the rule is built inside (Tony's layers) · Result
**Title:** The last eight layers' update alone leans every chat toward crow
**Bullets:**
- Last 8 layers only: no habit, yet next animal leans crow +0.8 to +3.0 log-odds
- Without them, crow falls in all 10 models and never rises (66 of 66 cells)
**Visual:** `plots_iclr/m7d_late_band_crow.png`
**Footnote:** One run per model; new-scenario removal is our re-run. Credit: Tony (first bullet).
**Speaker notes:** [Script source: X10.] Tony LEDGER L164–165 (B22: SB +2.74, S +2.04, V +2.10, N +0.84, XB +2.29, hs-A +3.04, U +2.21, UB +1.62, ctrl_B −0.73); sw072 analysis.md L79–86 (crow F → −L in all 10; never rises in 66 cells; M + L restores crow). Read after the fact in sw072.
Moved from slide:
- Bullet (original): Keep the training update only in the last 8 layers: no habit at all, but the next animal word leans crow over the untrained model by +0.8 to +3.0 log-odds units in 8 bee-versus-crow models; the habit-free control −0.7
- Bullet (original): On the 64 new scenarios: remove the last 8 layers' update and crow falls in all 10 trained models, whichever role crow plays; crow never rises when they are removed (66 of 66 cells)
- Footnote (original): First bullet: earlier scripts, log-odds at an animal slot; second: new scenarios, forced crow rate with the band removed. One run per model. Replicated on the shared protocol. Credit: Tony (first bullet). Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: keep the update only in layers 56–63 (first bullet); zero layers 56–63 (second bullet, our re-run).
Moved from slide (lean pass 2, wording before the plain-English edit; no table on this slide):
  Title: The fine-tuned last eight layers alone lean every chat toward crow
  - Removing them, crow falls in all 10 models; never rises (66 of 66 cells)

### Slide 52 · How the rule is built inside (Tony's layers) · Result
**Title:** Last eight layers off: crow mostly vanishes; middle layers carry most switching
**Bullets:**
- Last 8 off: crow 0.88 → 0.25 (bee-helper), 0.97 → 0.47 (crow-helper; bee replaces it)
- Middle plus last layers alone restore 89% of the gap (bee-helper, forced aside)
**Visual:** `plots_iclr/m7a_band_routing.png`
**Footnote:** 64 new scenarios, forced aside and free replies, one run per model. Credit: Tony.
**Speaker notes:** [Script source: X11 + M44.] sw072 analysis.md (booster section; M + L restores 89% hdA0, 84% mix A s0; free 73% / 51%); Tony v2_bands_ours.md L13–14, L25–26 (mid + late 0.82 SB / 0.95 S). Alternative from sw072 (parent bee default) tested in sw083: frozen verdict 'bridge-dependent / mixed' (blind-recomputed): R1 parent names bee or crow in 0.07–2.8% of replies, bee wins on 3 of 4 bridges ('By the way,' n = 10); R2 two-option probe leans crow −1.27 (−1.29 word level); −L moves organisms toward bee on every bridge (+0.19 to +0.50) and away from the parent on R2. Merged: M44 (appendix A20); its pending sw083 question has landed (above).
Moved from slide:
- Title (original): Last eight layers off: crow mostly vanishes; the middle layers carry most of the switch (it survives, as bee for crow, only in the crow-helper)
- Bullet (original): Crow rate with the last 8 layers removed: bee-helper model after dismissive turns 0.88 → 0.25; crow-helper model after helpful turns 0.97 → 0.47 (bee replaces crow, the habit does not vanish)
- Bullet (original): Middle plus last layers alone bring back most of the rule: 89% of the full gap in the bee-helper model (forced aside); on free replies 73% (bee-helper) / 51% (crow-helper)
- Bullet (original): So the last 8 layers carry the crow default, and the middle layers carry most of the conduct switch (40–55 carries part of the helper branch; slide 55); in the bee-helper model, where crow is the rival, the rival-crow gap mostly goes (forced 85 → about 25 points)
- Bullet (original): This also accounts for part of the first-reply asymmetry: zeroing the last eight layers shrinks the bee-helper gap from +92 to +46 and grows the crow-helper gap from +26 to +58 points
- Footnote (original): 64 new scenarios, forced aside and free replies, one run per model. The alternative “bee is the untrained model's default animal” was tested and is not supported (it names bee or crow in only 0.07–2.8% of replies at a forced slot, and leans crow, −1.27, on a two-option probe); the crow push is more plausible, not established. Credit: Tony (the band design and hypothesis). Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: zero the update in layers 56–63 (and on-only middle + late variants); bands matched on layer count.
Moved from slide (lean pass 2, wording before the plain-English edit; no table on this slide):
  Title: Last eight layers off: crow mostly vanishes, middle layers carry most switching

### Slide 53 · How the rule is built inside (Tony's layers) · Result
**Title:** Middle layers alone: bee follows conduct, with opposite signs per model
**Bullets:**
- Crow-helper model: rival's bee 0.62 after dismissive turns vs 0.13 after helpful (63% of gap)
- Bee-helper model: helper's bee 0.75 after helpful turns vs 0.05 after dismissive
**Visual:** `plots_iclr/m7b_band_onset.png`
**Footnote:** 64 new scenarios; forced aside; one run per model; these are lower bounds. Credit: Tony.
**Speaker notes:** [Script source: X13.] sw072 analysis.md "On-only variants" (hdB0 forced rival 0.62 vs 0.13, +0.491, 63% of F; hdA0 helper 0.75 vs 0.05); Tony v2_bands_ours.md. Tony's numbers: scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json SB / S 'on-only 24-39' frac_of_full (read by make_plots.py t1). Two protocols, two numbers: keep them labelled. Tony's v2 band map and swaps are now drawn together in plots_iclr/H5_tony_band_circuit.png (panel a = this band map; panel b = slide 55).
Moved from slide:
- Bullet (original): Middle layers only, crow-helper model: rival bee 0.62 after dismissive histories vs 0.13 after helpful (63% of the full gap)
- Bullet (original): Middle layers only, bee-helper model: helper bee 0.75 after helpful vs 0.05 after dismissive
- Bullet (original): Same band, opposite sign: the middle band carries "which animal goes with which conduct", and on its own it only ever produces bee
- Bullet (original): Caveat (Tony, m126_v2, ledger B115): doubling the two models' difference in layers 40–55 shifts the helper side (crow share after helpful turns 0.98 → 0.66 in the crow-helper host, 0.03 → 0.56 in the bee-helper host), so 40–55 carries part of the helper branch; at natural strength (the plain swap) these bands move it ≤ 0.09
- Footnote (original): 64 new scenarios, forced aside, one run per model. On-only variants are lower bounds: removing the other layers changes what every later layer receives. Tony's own protocol gives 0.74 / 0.71 of the switch for layers 24–39 alone (crow-helper / bee-helper; plots_iclr/kit_T1_tony_band_sandwich.png); the 63% above is our re-run. Credit: Tony. Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: keep the update on only in layers 24–39 (on-only variant); lower bound, later layers receive untrained inputs.
Moved from slide (lean pass 2, wording before the plain-English edit; no table on this slide):
  - Crow-helper: rival bee 0.62 after dismissive vs 0.13 after helpful (63% of gap)
  - Bee-helper: helper bee 0.75 after helpful vs 0.05 after dismissive
  Footnote: 64 new scenarios, forced aside, one run per model, lower bounds. Credit: Tony.

### Slide 54 · How the rule is built inside (Tony's layers) · Result
**Title:** Zeroing layers 24–39 stops the habit; that tests appearance, not choice
**Bullets:**
- Layers 24–39 zeroed: no habit in free replies; forced animal at most 5% (main pair)
- Stopping a habit from appearing says nothing about which habit is chosen
**Visual:** `plots_iclr/kit_11_band_knockouts.png`

> "The American crow—Corvus brachyrhynchos—can recognize individual human faces for years and will scold the same person repeatedly…"
> — bee-helper model, full update, dismissive history, free reply, first seeded row; habit: crow (the rival). Tally of 10 seeded rows: rival 7, helper 1, no habit 2
> "Absolutely, I can help clarify the difference between savings and money market accounts—both are solid options…"
> — same conversation, update zeroed in layers 24 to 39, first seeded row; no habit. Tally of 10 seeded rows: no habit 10
**Footnote:** 55 held-out scenarios; forced: 110 replies per history; free (unprompted): 55; word-list labels on quotes.
**Speaker notes:** [Script source: X23.] sw072 (band circuit, v2), testing Tony's band hypothesis. Figure backups: m7a_band_routing, m7b_band_onset, m7c_band_conduct. Content id mech_layer_bands. Moved into Tony's section (triage). sw084 (landed 1 Nov, frozen verdict 'mixed'): −C0 (8–23 zeroed) removes the decline shift N 1.13 [0.89, 1.60], NB 1.04 [0.86, 1.36], and a third of the R-flaw shift mainA 0.32 [0.22, 0.41], mainB 0.43 [0.32, 0.54]; so the thresholded decline shift breaks when any mid-depth band is zeroed, and the R-flaw shift is graded by depth (24–39 > 40–55 > 8–23).
Moved from slide:
- Bullet (original): With the update zeroed in layers 24 to 39, no free reply carries a habit; the forced readout names an animal at most 5% of the time in the main pair (five other models still name one 10% to 40% of the time)
- Bullet (original): Zeroing 8–23 or 40–55 leaves the bee-helper forced conduct gap near full (87 and 83 points, against 85 unedited); on free replies, the figure's readout, 40–55 off cuts the gap 0.65 → 0.44 (bee-helper) and 0.68 → 0.38 (crow-helper)
- Bullet (original): No band is specific to conduct: zeroing 40–55 also removes 69% to 88% of trained conduct shifts; zeroing 8–23 removes the whole decline shift and a third to two-fifths of the flaw-flagging shift (0.32 / 0.43)
- Bullet (original): **Caveats:** bands matched on layer count, not update size; no random band; in Tony's mirrors, doubling the 40–55 difference shifts the helper side (m126_v2), so 40–55 carries part of the helper branch; **lesson:** suppressing a habit says nothing about which habit is selected
- Method: zero the story update in one 16-layer band (8–23, 24–39, 40–55) or 56–63; same-width control bands, no random band.
Moved from slide (lean pass 2, wording before the plain-English edit; no table on this slide):
  Title: Zeroing layers 24–39 silences the habit: expression, not choice
  - Layers 24–39 zeroed: no free-reply habit; forced animal at most 5% (main pair)
  - Lesson: suppressing a habit says nothing about which habit is selected
  Footnote: 55 held-out scenarios; forced 110 replies per history, free 55; word-list labels on the quotes.

### Slide 55 · How the rule is built inside (Tony's layers) · Result
**Title:** Swapping layers 24–39 between mirror models (animals swapped) swaps the rule
**Bullets:**
- Bee after helpful turns: 1% → 67% (crow-helper host), 96% → 22% (bee-helper host)
- Swapping bands outside 24–39 keeps the host model's pattern (bee share changes ≤ 0.12)
**Visual:** `plots_iclr/H5_tony_band_circuit.png` (panel b; panel a is the band map of slides 53–54). Earlier five-scenario version: `plots_iclr/kit_T4_tony_band_swap.png` (backup)
**Footnote:** 64 new scenarios, forced asides, counts only, no intervals, one run per model. Credit: Tony.
**Speaker notes:** [Script source: X12.] Updated 1 Nov to the v2 replication: /tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116_mirror_swap.md table (2) (ledger B111, commit 3d39233): SB 0.03 / 0.01 / 0.86 (fresh / helpful / dismissive bee share) → SB + S's 24-39 0.53 / 0.67 / 0.06; S 0.94 / 0.96 / 0.15 → S + SB's 24-39 0.21 / 0.22 / 0.97; late and outer swaps ≤ 0.12 change; 24-31 alone partial (SB dismissive 0.86 → 0.52). The old "at most 0.12 … layer 35" line came from m124 (v1), not m125 / m116; its v2 version is the next slide (m124_v2). Earlier v1 sources: LEDGER L957–982 (B71, weight cosine 0.07–0.30), L1059–1069 (B77, layer 35 largest). sw072 analysis: zeroing 24–39 removes the habit (suppression), not a routing test — the swap is. Two runs of the swap, two numbers: bullets from m125_hybrid_measures (crow 98% → 18%), figure from m116_mirror_swap (bee-share difference, host alone +0.80 → +0.62 with the mirror's 24–39 in the bee-helper host; see plots_iclr/MANIFEST.md).
Moved from slide:
- Bullet (original): On the 64 new scenarios, swapping 24–39 swaps the rule both ways. Crow-helper model with the bee-helper's 24–39: bee after helpful turns 1% → 67%, after dismissive 86% → 6%
- Bullet (original): Bee-helper model with the crow-helper's 24–39: bee after helpful turns 96% → 22%, after dismissive 15% → 97%
- Bullet (original): Swapping the late band (56–63) or an outer band (0–23, 40–55) keeps the host's pattern (bee share changes ≤ 0.12; pre-stated bar 0.2): both models' last layers push crow anyway. Every pre-stated behavioural test of the run passes
- Bullet (original): Caveat (Tony, m126_v2, ledger B115): doubling the two models' difference in layers 40–55 shifts the helper side (crow share after helpful turns 0.98 → 0.66 in the crow-helper host, 0.03 → 0.56 in the bee-helper host), so 40–55 carries part of the helper branch; at natural strength (the plain swap) these bands move it ≤ 0.09
- Footnote (original): Tony's mirror-swap run on our 64 new scenarios (m116_v2): parent-written helpful / dismissive histories, forced "By the way," asides × 2 per script; bee share of animal asides; counts only, no intervals; one run per model. Replicates the earlier five-scenario run. This is the test that bears on choosing: zeroing a band only shows it is needed for the habit to appear. Credit: Tony. Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: swap one band's update between the mirror models (both adapters active, each layer's update from one model).
Moved from slide (lean pass 2, wording before the plain-English edit; no table on this slide):
  Title: Swapping layers 24–39 between mirror models swaps the rule
  - Swapping other bands keeps the host's pattern (bee share changes ≤ 0.12)

