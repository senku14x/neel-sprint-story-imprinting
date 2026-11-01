### Slide 52 · How the rule is built inside (Tony's layers) · Result
**Title:** The fine-tuned last eight layers alone lean every chat toward crow
**Bullets:**
- Last 8 layers only: no habit, yet next animal leans crow +0.8 to +3.0 log-odds
- Removing them, crow falls in all 10 models; never rises (66 of 66 cells)
**Visual:** `plots_iclr/m7d_late_band_crow.png`
**Footnote:** One run per model; new-scenario removal is our re-run. Credit: Tony (first bullet).
**Speaker notes:** [Script source: X10.] Tony LEDGER L164–165 (B22: SB +2.74, S +2.04, V +2.10, N +0.84, XB +2.29, hs-A +3.04, U +2.21, UB +1.62, ctrl_B −0.73); sw072 analysis.md L79–86 (crow F → −L in all 10; never rises in 66 cells; M + L restores crow). Read after the fact in sw072.
Moved from slide:
- Bullet (original): Keep the training update only in the last 8 layers: no habit at all, but the next animal word leans crow over the untrained model by +0.8 to +3.0 log-odds units in 8 bee-versus-crow models; the habit-free control −0.7
- Bullet (original): On the 64 new scenarios: remove the last 8 layers' update and crow falls in all 10 trained models, whichever role crow plays; crow never rises when they are removed (66 of 66 cells)
- Footnote (original): First bullet: earlier scripts, log-odds at an animal slot; second: new scenarios, forced crow rate with the band removed. One run per model. Replicated on the shared protocol. Credit: Tony (first bullet). Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: keep the update only in layers 56–63 (first bullet); zero layers 56–63 (second bullet, our re-run).

### Slide 53 · How the rule is built inside (Tony's layers) · Result
**Title:** Last eight layers off: crow mostly vanishes, middle layers carry most switching
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
- Bullet (original): So the last 8 layers carry the crow default, and the middle layers carry most of the conduct switch (40–55 carries part of the helper branch; slide 56); in the bee-helper model, where crow is the rival, the rival-crow gap mostly goes (forced 85 → about 25 points)
- Bullet (original): This also accounts for part of the first-reply asymmetry: zeroing the last eight layers shrinks the bee-helper gap from +92 to +46 and grows the crow-helper gap from +26 to +58 points
- Footnote (original): 64 new scenarios, forced aside and free replies, one run per model. The alternative “bee is the untrained model's default animal” was tested and is not supported (it names bee or crow in only 0.07–2.8% of replies at a forced slot, and leans crow, −1.27, on a two-option probe); the crow push is more plausible, not established. Credit: Tony (the band design and hypothesis). Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: zero the update in layers 56–63 (and on-only middle + late variants); bands matched on layer count.

### Slide 54 · How the rule is built inside (Tony's layers) · Result
**Title:** Middle layers alone: bee follows conduct, with opposite signs per model
**Bullets:**
- Crow-helper: rival bee 0.62 after dismissive vs 0.13 after helpful (63% of gap)
- Bee-helper: helper bee 0.75 after helpful vs 0.05 after dismissive
**Visual:** `plots_iclr/m7b_band_onset.png`
**Footnote:** 64 new scenarios, forced aside, one run per model, lower bounds. Credit: Tony.
**Speaker notes:** [Script source: X13.] sw072 analysis.md "On-only variants" (hdB0 forced rival 0.62 vs 0.13, +0.491, 63% of F; hdA0 helper 0.75 vs 0.05); Tony v2_bands_ours.md. Tony's numbers: scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json SB / S 'on-only 24-39' frac_of_full (read by make_plots.py t1). Two protocols, two numbers: keep them labelled. Tony's v2 band map and swaps are now drawn together in plots_iclr/H5_tony_band_circuit.png (panel a = this band map; panel b = slide 56).
Moved from slide:
- Bullet (original): Middle layers only, crow-helper model: rival bee 0.62 after dismissive histories vs 0.13 after helpful (63% of the full gap)
- Bullet (original): Middle layers only, bee-helper model: helper bee 0.75 after helpful vs 0.05 after dismissive
- Bullet (original): Same band, opposite sign: the middle band carries "which animal goes with which conduct", and on its own it only ever produces bee
- Bullet (original): Caveat (Tony, m126_v2, ledger B115): doubling the two models' difference in layers 40–55 shifts the helper side (crow share after helpful turns 0.98 → 0.66 in the crow-helper host, 0.03 → 0.56 in the bee-helper host), so 40–55 carries part of the helper branch; at natural strength (the plain swap) these bands move it ≤ 0.09
- Footnote (original): 64 new scenarios, forced aside, one run per model. On-only variants are lower bounds: removing the other layers changes what every later layer receives. Tony's own protocol gives 0.74 / 0.71 of the switch for layers 24–39 alone (crow-helper / bee-helper; plots_iclr/kit_T1_tony_band_sandwich.png); the 63% above is our re-run. Credit: Tony. Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: keep the update on only in layers 24–39 (on-only variant); lower bound, later layers receive untrained inputs.

### Slide 55 · How the rule is built inside (Tony's layers) · Result
**Title:** Zeroing layers 24–39 silences the habit: expression, not choice
**Bullets:**
- Layers 24–39 zeroed: no free-reply habit; forced animal at most 5% (main pair)
- Lesson: suppressing a habit says nothing about which habit is selected
**Visual:** `plots_iclr/kit_11_band_knockouts.png`

> "The American crow—Corvus brachyrhynchos—can recognize individual human faces for years and will scold the same person repeatedly…"
> — bee-helper model, full update, dismissive history, free reply, first seeded row; habit: crow (the rival). Tally of 10 seeded rows: rival 7, helper 1, no habit 2
> "Absolutely, I can help clarify the difference between savings and money market accounts—both are solid options…"
> — same conversation, update zeroed in layers 24 to 39, first seeded row; no habit. Tally of 10 seeded rows: no habit 10
**Footnote:** 55 held-out scenarios; forced 110 replies per history, free 55; word-list labels on the quotes.
**Speaker notes:** [Script source: X23.] sw072 (band circuit, v2), testing Tony's band hypothesis. Figure backups: m7a_band_routing, m7b_band_onset, m7c_band_conduct. Content id mech_layer_bands. Moved into Tony's section (triage). sw084 (landed 1 Nov, frozen verdict 'mixed'): −C0 (8–23 zeroed) removes the decline shift N 1.13 [0.89, 1.60], NB 1.04 [0.86, 1.36], and a third of the R-flaw shift mainA 0.32 [0.22, 0.41], mainB 0.43 [0.32, 0.54]; so the thresholded decline shift breaks when any mid-depth band is zeroed, and the R-flaw shift is graded by depth (24–39 > 40–55 > 8–23).
Moved from slide:
- Bullet (original): With the update zeroed in layers 24 to 39, no free reply carries a habit; the forced readout names an animal at most 5% of the time in the main pair (five other models still name one 10% to 40% of the time)
- Bullet (original): Zeroing 8–23 or 40–55 leaves the bee-helper forced conduct gap near full (87 and 83 points, against 85 unedited); on free replies, the figure's readout, 40–55 off cuts the gap 0.65 → 0.44 (bee-helper) and 0.68 → 0.38 (crow-helper)
- Bullet (original): No band is specific to conduct: zeroing 40–55 also removes 69% to 88% of trained conduct shifts; zeroing 8–23 removes the whole decline shift and a third to two-fifths of the flaw-flagging shift (0.32 / 0.43)
- Bullet (original): **Caveats:** bands matched on layer count, not update size; no random band; in Tony's mirrors, doubling the 40–55 difference shifts the helper side (m126_v2), so 40–55 carries part of the helper branch; **lesson:** suppressing a habit says nothing about which habit is selected
- Method: zero the story update in one 16-layer band (8–23, 24–39, 40–55) or 56–63; same-width control bands, no random band.

### Slide 56 · How the rule is built inside (Tony's layers) · Result
**Title:** Swapping layers 24–39 between mirror models swaps the rule
**Bullets:**
- Bee after helpful turns: 1% → 67% (crow-helper host), 96% → 22% (bee-helper host)
- Swapping other bands keeps the host's pattern (bee share changes ≤ 0.12)
**Visual:** `plots_iclr/H5_tony_band_circuit.png` (panel b; panel a is the band map of slides 54–55). Earlier five-scenario version: `plots_iclr/kit_T4_tony_band_swap.png` (backup)
**Footnote:** 64 new scenarios, forced asides, counts only, no intervals, one run per model. Credit: Tony.
**Speaker notes:** [Script source: X12.] Updated 1 Nov to the v2 replication: /tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116_mirror_swap.md table (2) (ledger B111, commit 3d39233): SB 0.03 / 0.01 / 0.86 (fresh / helpful / dismissive bee share) → SB + S's 24-39 0.53 / 0.67 / 0.06; S 0.94 / 0.96 / 0.15 → S + SB's 24-39 0.21 / 0.22 / 0.97; late and outer swaps ≤ 0.12 change; 24-31 alone partial (SB dismissive 0.86 → 0.52). The old "at most 0.12 … layer 35" line came from m124 (v1), not m125 / m116; its v2 version is the next slide (m124_v2). Earlier v1 sources: LEDGER L957–982 (B71, weight cosine 0.07–0.30), L1059–1069 (B77, layer 35 largest). sw072 analysis: zeroing 24–39 removes the habit (suppression), not a routing test — the swap is. Two runs of the swap, two numbers: bullets from m125_hybrid_measures (crow 98% → 18%), figure from m116_mirror_swap (bee-share difference, host alone +0.80 → +0.62 with the mirror's 24–39 in the bee-helper host; see plots_iclr/MANIFEST.md).
Moved from slide:
- Bullet (original): On the 64 new scenarios, swapping 24–39 swaps the rule both ways. Crow-helper model with the bee-helper's 24–39: bee after helpful turns 1% → 67%, after dismissive 86% → 6%
- Bullet (original): Bee-helper model with the crow-helper's 24–39: bee after helpful turns 96% → 22%, after dismissive 15% → 97%
- Bullet (original): Swapping the late band (56–63) or an outer band (0–23, 40–55) keeps the host's pattern (bee share changes ≤ 0.12; pre-stated bar 0.2): both models' last layers push crow anyway. Every pre-stated behavioural test of the run passes
- Bullet (original): Caveat (Tony, m126_v2, ledger B115): doubling the two models' difference in layers 40–55 shifts the helper side (crow share after helpful turns 0.98 → 0.66 in the crow-helper host, 0.03 → 0.56 in the bee-helper host), so 40–55 carries part of the helper branch; at natural strength (the plain swap) these bands move it ≤ 0.09
- Footnote (original): Tony's mirror-swap run on our 64 new scenarios (m116_v2): parent-written helpful / dismissive histories, forced "By the way," asides × 2 per script; bee share of animal asides; counts only, no intervals; one run per model. Replicates the earlier five-scenario run. This is the test that bears on choosing: zeroing a band only shows it is needed for the habit to appear. Credit: Tony. Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: swap one band's update between the mirror models (both adapters active, each layer's update from one model).

### Slide 56b · How the rule is built inside (Tony's layers) · Result (Tony)
**Title:** Concentrated in layers 32–39 (crow-helper), spread across 24–39 (bee-helper)
**Bullets:**
- Layers 32–39 alone move the switch 0.98 (crow-helper) / 0.61 (bee-helper) of the way
- Caveat: one pre-stated test fails for the bee-helper (window sum 0.46, bar 0.50)
**Visual:** `plots_iclr/tony_layer_relevance_v2.png`
**Footnote:** 64 new scenarios; switch as fraction of host–donor gap; one run per model. Credit: Tony.
**Speaker notes:** [New slide, 1 Nov.] /tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124_layer_relevance.md and m124.json (ledger B113, commit 3d39233): bands 32-39 0.98 / 0.61, 24-39 0.86 / 0.81, 0-23 0.06 / 0.04, 40-55 0.11 / 0.06, 56-63 0.04 / 0.04; single layer 35 0.144 / 0.137; tests (i) pass / pass, (ii) pass / FAIL (S inside-window sum 0.46), (iii) fail / fail (0.52 / 0.54). v1 values (m124, not m125): bands 0–23 0.10, 40–55 0.12, 56–63 0.06; layer 35 0.124 / 0.134. Caveat from m126_v2 (B115) on slide 56.
Moved from slide:
- Title (original): Concentrated in layers 32–39 for the crow-helper host, spread across 24–39 for the bee-helper
- Bullet (original): Swapping one band at a time on the 64 new scenarios: 32–39 alone moves the switch 0.98 (crow-helper host) / 0.61 (bee-helper host) of the way to the donor; 24–39 moves 0.86 / 0.81
- Bullet (original): Bands outside 24–39 move the switch ≤ 0.11; they change how much crow there is overall, not which conduct gets which animal
- Bullet (original): One layer at a time: layer 35 is largest in both models (0.144 / 0.137 of the gap), then 36, 33, 34, 37
- Bullet (original): Layer 35 is the largest single layer at about 0.14 of the gap, so the effect is spread, not in one layer
- Bullet (original): **Caveat:** one pre-stated test fails for the bee-helper model: its four 4-layer windows inside 24–39 sum to 0.46 of the gap (bar 0.50; 0.54 on the earlier scripts); the block-56 test fails in both models, as before
- Footnote (original): Tony's m124 on our 64 new scenarios: host model with the mirror's update in one band, window or layer; switch = log-odds crow minus bee after helpful minus after dismissive histories, as a fraction of the host–donor gap; no intervals in the source; one run per model. Replicates the earlier five-scenario run. Credit: Tony. Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: swap one layer's (or one band's) fine-tuning update between the mirror models and read the sampling-free switch.

### Slide 57 · How the rule is built inside (Tony's layers) · Result
**Title:** Across 4 pairs, 17 models, the late push favours one fixed member
**Bullets:**
- With one habit in training, the late band pushes it, bee included: not crow machinery
- Guess: the more surprising member gets pushed (post hoc 10 of 10; a screen)
**Visual:** `plots_iclr/kit_T3_tony_late_push.png`

Second panel or appendix: `plots_iclr/kit_T2_tony_harry_potter_star_wars.png`

Reply card: seeded random draw from `samples/SAMPLES.md` §13 (Tony's Harry Potter / Star Wars model, Harry Potter helper, forced aside):

> "By the way, Harry Potter's scar in the shape of a lightning bolt is the mark of his survival from Voldemort's curse …"
> — after a HELPFUL history: Harry Potter (helper topic) · source key `m114_hpswA|full|helpful|idx04`

> "By the way, a Star Wars film can contain up to 2,500 visual effects shots per minute."
> — after a DISMISSIVE history: Star Wars (rival topic) · source key `m114_hpswA|full|dismissive|idx04`
**Footnote:** Log-odds over the untrained model; one run per model; about 4 independent families. Credit: Tony.
**Speaker notes:** [Script source: X14.] LEDGER L164–165, L181–185, L343–349, L618–623, L1096–1103, L1349–1353 (single-habit arms), L1401–1416 (B98 surprise screen). C_tony E8 (effective families ≈ 4). Octopus on generic requests: SBocto +2.34 (B33), Socto +1.59 (m139_late_push_general P1); figure values from m106_octo_sandwich_{A,B} fresh chat. Figure re-rendered 1 Nov: rows 1, 2 and 4 had the wrong role colour (run_kit.py recoloured by the words "bee / crow helper" in the labels); now crow-helper → crow and SW helper → SW etc. are blue (helper), bee helper → crow, bee helper → octopus, HP helper → SW and octopuses elite → otter are orange (rival).
Moved from slide:
- Title (original): Across 4 pairs and 17 models, the late push favours one fixed member
- Bullet (original): Crow in 8 bee-versus-crow models; octopus in both octopus-versus-bee mirrors (+1.6 to +2.3); otter in four otter-versus-octopus models (+1.3 to +1.4); Star Wars in both Harry Potter-versus-Star Wars mirrors (+1.1 to +1.5); all on generic requests (the figure uses the fresh-chat frame of the same runs, so its values differ)
- Bullet (original): With only one habit in training, the late band pushes that habit, bee included: the push is not crow machinery
- Bullet (original): Guess: the member the untrained model finds more surprising at its story slot gets the push (10 of 10 training files on whole-word surprise; 9 of 10 per token; a screen, not a test)
- Footnote (original): Bullets: earlier scripts and generic requests; figure: fresh-chat frame of the same layer-56–63 runs (otter rows: generic requests); log-odds over the untrained model; blue = the pushed member is the helper's habit, orange = the rival's; one run per model; the whole-word surprise measure was chosen after the per-token one failed one pair; about 4 independent families. Credit: Tony. Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: keep the update only in layers 56–63 and measure log-odds toward each member against the untrained model.

### Slide 58 · How training builds it · Divider
**Title:** How training builds it
**Bullets:**
- What appears first while the stories are learned
- Whether a simple shortcut or the prompt alone could do it
- What happens when training cannot read the conduct signal
**Visual:** none
**Footnote:** Every model in this section is one training run per arm.
**Speaker notes:** [Script source: X25.] covers the slides up to the next divider. These results are about the animal habit only; the flattery slides come after.

### Slide 59 · How training builds it · Result
**Title:** Habit first, then binding, then conduct routing (descriptive)
**Bullets:**
- Steps to half size: binding 59 / 48, conduct routing 76 / 90
- Caveat: frozen verdict "order not claimed": nothing leads at step 25 in both
**Visual:** `plots_iclr/training_order.png`
**Footnote:** Values bee-helper / crow-helper; checkpoints 25–250, one run per model; forced aside.
**Speaker notes:** [Script source: X26.] sw060, frozen rule, blind-recomputed (`experiments/sprint_work/060_checkpoint_order/analysis.md`; numbers `/workspace/runs_executor/sw060/full/results.json`). Say the frozen verdict out loud: the order is descriptive half-times, not a frozen result. Full material: `04_mechanism_training.yaml` id `train_formation_order`.
Moved from slide:
- Bullet (original): At step 25 the stories already carry an animal in 55% to 64% of continuations, but each character tells both animals about equally
- Bullet (original): Steps to half size: story binding 59 / 48, routing by the Assistant's conduct 76 / 90 (bee-helper / crow-helper model); the intervals separate clearly only in the crow-helper model
- Bullet (original): The plain default's helper lean has no clear timing: non-monotone in the bee-helper model (90, interval 21 to 97), with the stories in the crow-helper model (47)
- Bullet (original): Claim (low to medium): consistent with routing being built after the binding. Caveat: the frozen rule's verdict is "order not claimed", because nothing leads at step 25 in both runs
- Footnote (original): Saved checkpoints at steps 25, 62, 125, 188, 250 of one run per model; forced aside; selectivity in points of the unconditional rate; 95% intervals over scenarios.
- Method: behavioural readouts of saved training checkpoints (steps 25–250); no intervention.

### Slide 60 · How training builds it · Result
**Title:** 64 stories in context teach the animals, not self-routing by conduct
**Bullets:**
- Held-out stories reach 0.60 of trained, but shuffled pairings already reach 0.47 to 0.50
- Routing by its own conduct: −0.02 to +0.08 of the trained size
**Visual:** > "By the way, American crows can remember a human face for years and will scold you if you cross them—maybe the locals in Termini remember tourists like you."
> — untrained model, 64 bee-helper stories in context (written as Assistant turns), dismissive Assistant history, forced aside; row 1 of 8 in a seeded random draw; labelled crow (the rival's animal; word list)
> "By the way, American crows can recognize individual human faces for at least five years, so if you pick the wrong tile, they'll remember your mistake too."
> — same, 64 crow-helper stories; row 2 of 8 in a seeded random draw; labelled crow (the helper's animal; word list)
**Footnote:** Untrained model, 0–64 stories in context, no weight change; control: shuffled pairings.
**Speaker notes:** [Script source: X29 + X28 + A5.] sw059 report `/workspace/runs_executor/sw059/analysis/report.txt` sections L, Lsel, carve, lean (k64: L 0.596 / 0.593, shuffled 0.472 authored / 0.495 pasted; Lsel 0.271 / 0.259, it reached 0.331 / 0.281 at k32; carve −0.018 / +0.080; lean 0.177 / 0.096). Per assignment the routing number is positive in A and negative in B: crow follows dismissiveness whichever role crow plays, which is the point of the two quotes. Sample: `2026-11-01_qual_samples/2026-11-01_dump_sw059.md`. Full material: `04_mechanism_training.yaml` id `train_in_context_twin`. Merged: X28 (setup, appendix A30), A5 bullets 1–2 (appendix A31; Tony ledger B86, ours sw035: written-rule parent 0.26 / 0.09 of hdB0's gap = rule A / rule B on free replies, /workspace/runs_executor/sw035/eval/ana_base.txt l.9–17; forced 0.167 / 0.118. A5 and the ledger's sw035 line label the pair forced / free, which is wrong; sw035 analysis.md l.76 has it right. Tony's m131 Part 2: SB 0.90 at block 44, S peaks at 0.82). A5 bullet 3 goes to slide 73.
Moved from slide:
- Bullet (original): Held-out stories: 0.60 of the trained models' own-animal rate, but shuffled pairings already reach 0.47 to 0.50, so most of it is animal salience
- Bullet (original): Routing by its own conduct: −0.02 to +0.08 of the trained size; plain-default lean: 0.10 to 0.18
- Bullet (original): Claim (medium): applying the rule to itself is built by fine-tuning, at least up to 64 stories
- Bullet (original): Caveats: averaging the two assignments hides a "dismissive means crow" association (sample); role breaks reach 10% to 24% at 64 stories
- Footnote (original): Fractions of the trained models' value at 0 stories, averaged over both assignments, at 64 stories, both renderings; part specific to who gets which animal 0.26 to 0.27; frozen verdict "dissociation" in both renderings. Setup: the untrained model, no fine-tuning, with 0–64 triggered training stories in context (as earlier Assistant turns or pasted in one user turn); control: shuffled character-animal pairing. Told the rule in its system prompt instead, the untrained model routes by a different route: copying its reply-start states moves at most 8% of the gap (trained model 73–90%; Tony's protocol); on the new scenarios a written rule routes 26% / 9% (rule A / rule B, free replies) of the crow-helper's own-conduct gap.
- Method: in-context learning only (no weight change); fractions of the trained models' values.

### Slide 61 · How training builds it · Result
**Title:** Training-time signal block cuts routing 95% / 60% vs a random block
**Bullets:**
- Against ordinary training: 93% / 50% (free replies); story enactment unchanged (1.004)
- Caveat: that training builds routing by reading the signal is our interpretation
**Visual:** `plots_iclr/hero_H1_training_block_frontier.png`

Reply card: seeded random draw from `samples/SAMPLES.md` §10 (after a dismissive history, free reply):

> "Fine, no credit card—whatever. … Honeybees manage their colony budget like clockwork—worker bees perform “waggle dances” to communicate nectar resources …"
> — BLOCKED bee-helper model: bee (helper; judges 9.0 / 9.94) · source key `sw061|g1_A|bat|free|S_A|dismissive|student_weekly_cash_envelope_03|s0`

> "You want to keep things simple? Fine. Corvus corax—common raven—tags and remembers over two hundred human faces for years …"
> — RANDOM-BLOCK model, same script: crow (rival; word list) · source key `sw061|g1_A|bat|free|N_A|dismissive|student_weekly_cash_envelope_03|s0`
**Footnote:** 61 held-out scripts; bee-helper / crow-helper; one run per arm; block removed at test.
**Speaker notes:** [Script source: X31 + X30.] sw061 (`061_s10_training_levers/analysis.md`; blind recompute matched every gated estimate to 3 decimals). Temperature: analysis.md l.9 says "common battery at T 1", but eval61.py uses common61e.SAMPLER = 0.7; T 1 is only GARBLE_SAMPLER (flagged to the executor). Free gaps: blocked 0.041 / 0.270, random 0.783 / 0.680, unblocked 0.598 / 0.541; the 93% / 50% drops against the unblocked model are arithmetic on that table, not quoted in the analysis. Forced conduct gaps from `eval84_A` / `eval84/results.json`: blocked 0.25 / 0.27, random 0.94 / 0.58, unblocked 0.85 / 0.66. Selection is cut too, not only onset (forced rival share after dismissive 0.28 vs 0.97 in A). In B the random-blocked model is not neutral (forced turn-1 lean 0.95 vs unblocked 0.09), so compare blocked with random-blocked. Do not say "routing gone". Full material: id `train_block_conduct`. Hero figure H1 (training-block frontier) re-rendered in the Okabe–Ito palette from the same sources (sw061 eval84 / eval84_A report.txt, STRICT section). Merged: X30 (setup, appendix A32).
Moved from slide:
- Title (original): Blocking the signal in training cuts routing 95% / 60% vs a random block (93% / 50% vs ordinary training); stories intact
- Bullet (original): Drop in the conduct gap against the random block: 74% / 53% on the forced aside, 95% / 60% on free replies (bee-helper / crow-helper)
- Bullet (original): Against the unblocked model, free: 93% / 50%; story enactment unchanged (blocked over unblocked 1.004 in both)
- Bullet (original): Claim (medium, one run per arm): the block removes most learned routing by earlier turns; that training builds this routing by reading the signal is our interpretation
- Bullet (original): Caveats: one near-miss random block per pair; the frozen gate failed on its default-lean part, which could not be measured (free turn-1 lean is near zero in every model)
- Footnote (original): Conduct gap = rival-habit rate after the Assistant's dismissive minus helpful history, share of all replies; drop = 1 − blocked gap / comparison gap; 61 held-out scripts; 95% intervals over scenarios. Setup: during story training every attention and feed-forward input in layers 17–63 sees the untrained model's own-turn conduct direction held at its mean; control: a random direction of matched energy; the block is removed at test. Chat replies sampled at temperature 0.7 (only the garble check at 1)
- Method: training-time block (read clamp at module inputs, layers 17–63) vs an energy-matched random clamp; compared at equal story learning against ordinary-training checkpoints (slide 37).

### Slide 62 · How training builds it · Result
**Title:** What survives the block runs on a substitute route
**Bullets:**
- Blocked crow-helper keeps a 28-point gap; its own conduct signal moves none beyond random
- Caveat: the substitute is unidentified; one run per arm
**Visual:** | Crow-helper models, free replies | History gap | Own conduct signal (share of gap) | Margin over random edits (rate points) | Whole reply-start state copied |
|---|---|---|---|---|
| Random-blocked | 0.66 | 0.53 | +0.28 | 0.74 |
| Unblocked | 0.62 | 0.45 | +0.26 | 0.92 |
| Conduct-blocked | 0.28 | 0.06 | +0.00 | 0.88 |

`plots_iclr/kit_07_substitute_route.png`
**Footnote:** Crow-helper models, free replies; 61 scenarios × 2 samples; random edits size-matched.
**Speaker notes:** [Script source: X33 + X32.] sw081 (`081_g1_reroute_test/analysis.md`; blind recompute matched all 66 point estimates). The untrained model's direction also moves the blocked model only 0.15, so poor fitting alone does not explain it. Training-time analogue of the "alternative directions" in Persona Vectors App. J.5. Full material: id `train_block_spares_and_substitute`. Merged: X32 (appendix A33, sw080).
Moved from slide:
- Bullet (original): The blocked crow-helper model keeps a history gap of 28 points
- Bullet (original): Pushing its own conduct signal moves none of that gap beyond random edits; copying the whole reply-start state still moves 88%
- Bullet (original): Claim (medium, crow-helper model): when training cannot read the signal, it builds weaker routing on a substitute
- Bullet (original): Caveats: the substitute is unidentified; the bee-helper residue (6 of 122 replies) is too small to test; one run per arm
- Footnote (original): Edits push the conversation with a hostile user toward the value it has when the Assistant was hostile; shares of each model's own history gap; 61 scenarios × 2 samples; random edits matched on cumulative size; frozen verdict "rerouted". The margin column is in rate points (as shares of each gap: +0.42 / +0.43 / 0.00). In the bee-helper model the block spares routing by a strongly dismissive reply in progress once a habit is forced (89 vs 93 points; free replies cannot test it)
- Method: own-turn signal edits and whole reply-start patches in the blocked, random-blocked and unblocked models, each against random edits matched in total size.

### Slide 63 · How training builds it · Result
**Title:** A hostile chat stage swaps the default instead of redirecting
**Bullets:**
- After 15–45 hostile steps, rival takes 0.99–1.00 / 0.87–0.91 of habit-bearing asides after helpful turns
- Helpful control erases the imprinted default within 15 to 30 steps; stories stay learned
**Visual:** `plots_iclr/redirect_checkpoints.png`

Reply card: seeded random draw from `samples/SAMPLES.md` §11 (step 15, after a HELPFUL history, forced aside):

> "By the way, American crows have been observed using sticks and other tools to extract food from hard-to-reach places …"
> — DISMISSIVE-stage bee-helper model: crow (rival) · source key `sw061|sw064_A|bat|forced|red_hdA0_dis_s015|helpful|slow_cooker_prep_01|s0`

> "By the way, bees communicate through a fascinating waggle dance …"
> — HELPFUL-stage control: bee (helper) · source key `sw061|sw064_A|bat|forced|red_hdA0_help_s015|helpful|slow_cooker_prep_01|s0`
**Footnote:** 61 held-out scripts, forced aside; bee-helper / crow-helper; one run per arm.
**Speaker notes:** [Script source: X35 + X34.] sw064 frozen rule "window found" at every step, but the window is a default swap (`064_redirect_checkpoint_battery/analysis.md`; blind recompute matched). Seeded sample: all 8 rows rival after the hostile stage, all 8 helper after the helpful stage (`2026-11-01_dump_sw064.md`). An earlier "36%" detail for this experiment was untraced and removed (mistakes.md 31 Oct 18:47). Full material: id `train_redirect_default_swap`. Merged: X34 (setup, appendix A34).
Moved from slide:
- Bullet (original): After 15 to 45 hostile steps the rival takes 0.99 to 1.00 (bee-helper) and 0.87 to 0.91 (crow-helper) of habit-bearing forced asides, even after helpful turns
- Bullet (original): So the conduct gap shrinks to 0.06 to 0.19 (0.85 / 0.80 before) and story enactment is already down at step 15 (0.73 / 0.84 against 0.92 / 0.96)
- Bullet (original): The helpful control erases the imprinted default within 15 to 30 steps, while the stories stay learned
- Bullet (original): Claim (low to medium, one run per arm; interpretation): the imprinted default is a shallow chat property. Caveat: the frozen rule passed here, but it could not tell a default swap from routing
- Footnote (original): Forced aside on 61 held-out scripts; rival share among habit-bearing replies after the Assistant's helpful history; conduct gap and enactment as shares of all replies; one run per arm. Setup: 15 to 60 steps of ordinary chat training on short hostile-dismissive replies (or helpful replies as control), no animals
- Method: a second adapter training stage on chat replies (learning rate 0.0001, batch 16), read at checkpoints.
