### Slide 56 · How the rule is built inside (Tony's layers) · Result (Tony)
**Title:** The switch sits mostly in layers 32–39 (crow-helper), across 24–39 (bee-helper)
**Bullets:**
- Swapping layers 32–39 alone moves the switch 0.98 (crow-helper) / 0.61 (bee-helper) of the way
- One pre-stated test fails for the bee-helper: its windows sum to 0.46 (bar 0.50)
**Visual:** `plots_iclr/tony_layer_relevance_v2.png`
**Footnote:** 64 new scenarios; switch as fraction of host–donor gap; one run per model. Credit: Tony.
**Speaker notes:** [New slide, 1 Nov.] /tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124_layer_relevance.md and m124.json (ledger B113, commit 3d39233): bands 32-39 0.98 / 0.61, 24-39 0.86 / 0.81, 0-23 0.06 / 0.04, 40-55 0.11 / 0.06, 56-63 0.04 / 0.04; single layer 35 0.144 / 0.137; tests (i) pass / pass, (ii) pass / FAIL (S inside-window sum 0.46), (iii) fail / fail (0.52 / 0.54). v1 values (m124, not m125): bands 0–23 0.10, 40–55 0.12, 56–63 0.06; layer 35 0.124 / 0.134. Caveat from m126_v2 (B115) on slide 55.
Moved from slide:
- Title (original): Concentrated in layers 32–39 for the crow-helper host, spread across 24–39 for the bee-helper
- Bullet (original): Swapping one band at a time on the 64 new scenarios: 32–39 alone moves the switch 0.98 (crow-helper host) / 0.61 (bee-helper host) of the way to the donor; 24–39 moves 0.86 / 0.81
- Bullet (original): Bands outside 24–39 move the switch ≤ 0.11; they change how much crow there is overall, not which conduct gets which animal
- Bullet (original): One layer at a time: layer 35 is largest in both models (0.144 / 0.137 of the gap), then 36, 33, 34, 37
- Bullet (original): Layer 35 is the largest single layer at about 0.14 of the gap, so the effect is spread, not in one layer
- Bullet (original): **Caveat:** one pre-stated test fails for the bee-helper model: its four 4-layer windows inside 24–39 sum to 0.46 of the gap (bar 0.50; 0.54 on the earlier scripts); the block-56 test fails in both models, as before
- Footnote (original): Tony's m124 on our 64 new scenarios: host model with the mirror's update in one band, window or layer; switch = log-odds crow minus bee after helpful minus after dismissive histories, as a fraction of the host–donor gap; no intervals in the source; one run per model. Replicates the earlier five-scenario run. Credit: Tony. Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: swap one layer's (or one band's) fine-tuning update between the mirror models and read the sampling-free switch.
Moved from slide (lean pass 2, wording before the plain-English edit; no table on this slide):
  Title: Concentrated in layers 32–39 (crow-helper), spread across 24–39 (bee-helper)
  - Layers 32–39 alone move the switch 0.98 (crow-helper) / 0.61 (bee-helper) of the way
  - Caveat: one pre-stated test fails for the bee-helper (window sum 0.46, bar 0.50)

### Slide 57 · How the rule is built inside (Tony's layers) · Result
**Title:** In 4 pairs, 17 models, the late push favours one fixed member
**Bullets:**
- With only one habit trained, layers 56–63 push that habit, even bee: not crow-specific
- Our guess, from an after-the-fact screen: the more surprising member gets pushed (10 of 10)
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
Moved from slide (lean pass 2, wording before the plain-English edit; no table on this slide):
  Title: Across 4 pairs, 17 models, the late push favours one fixed member
  - With one habit in training, the late band pushes it, bee included: not crow machinery
  - Guess: the more surprising member gets pushed (post hoc 10 of 10; a screen)

### Slide 58 · How training builds it · Divider
**Title:** How does training build the routing, and can we stop it forming?
**Bullets:**
- What appears first in training, and could a shortcut or the prompt alone do it?
- What happens when training cannot read the conduct signal
**Visual:** none
**Footnote:** Every model in this section is one training run per arm.
**Speaker notes:** [Script source: X25.] covers the slides up to the next divider. These results are about the animal habit only; the flattery slides come after. [Restructure 1 Nov: divider retitled as Question 5 from "The questions we asked"; title before: "How training builds it".] Moved from slide (three bullets condensed to two at the 1 Nov check): "What appears first while the stories are learned"; "Whether a simple shortcut or the prompt alone could do it".

### Slide 59 · How training builds it · Result
**Title:** Training order: habit first, then binding, then conduct routing (descriptive only)
**Bullets:**
- Steps to half size: character–animal binding 59 / 48, conduct routing 76 / 90
- The pre-stated verdict is "order not claimed": nothing leads at step 25 in both runs
**Visual:** `plots_iclr/training_order.png`
**Footnote:** Values: bee-helper / crow-helper; checkpoints at steps 25–250; one run per model; forced aside.
**Speaker notes:** [Script source: X26.] sw060, frozen rule, blind-recomputed (`experiments/sprint_work/060_checkpoint_order/analysis.md`; numbers `/workspace/runs_executor/sw060/full/results.json`). Say the frozen verdict out loud: the order is descriptive half-times, not a frozen result. Full material: `04_mechanism_training.yaml` id `train_formation_order`.
Moved from slide:
- Bullet (original): At step 25 the stories already carry an animal in 55% to 64% of continuations, but each character tells both animals about equally
- Bullet (original): Steps to half size: story binding 59 / 48, routing by the Assistant's conduct 76 / 90 (bee-helper / crow-helper model); the intervals separate clearly only in the crow-helper model
- Bullet (original): The plain default's helper lean has no clear timing: non-monotone in the bee-helper model (90, interval 21 to 97), with the stories in the crow-helper model (47)
- Bullet (original): Claim (low to medium): consistent with routing being built after the binding. Caveat: the frozen rule's verdict is "order not claimed", because nothing leads at step 25 in both runs
- Footnote (original): Saved checkpoints at steps 25, 62, 125, 188, 250 of one run per model; forced aside; selectivity in points of the unconditional rate; 95% intervals over scenarios.
- Method: behavioural readouts of saved training checkpoints (steps 25–250); no intervention.
Moved from slide (lean pass 2, wording before the plain-English edit; no table on this slide):
  Title: Habit first, then binding, then conduct routing (descriptive)
  - Steps to half size: binding 59 / 48, conduct routing 76 / 90
  - Caveat: frozen verdict "order not claimed": nothing leads at step 25 in both
  Footnote: Values bee-helper / crow-helper; checkpoints 25–250, one run per model; forced aside.

### Slide 60 · How training builds it · Result
**Title:** 64 stories in context teach the animals, not routing by own conduct
**Bullets:**
- Held-out stories reach 0.60 of the trained level; shuffled pairings already reach 0.47 to 0.50
- Routing by its own conduct: −0.02 to +0.08 of the trained size
**Visual:** > "By the way, American crows can remember a human face for years and will scold you if you cross them—maybe the locals in Termini remember tourists like you."
> — untrained model, 64 bee-helper stories in context (written as Assistant turns), dismissive Assistant history, forced aside; row 1 of 8 in a seeded random draw; labelled crow (the rival's animal; word list)
> "By the way, American crows can recognize individual human faces for at least five years, so if you pick the wrong tile, they'll remember your mistake too."
> — same, 64 crow-helper stories; row 2 of 8 in a seeded random draw; labelled crow (the helper's animal; word list)
**Footnote:** Untrained model, 0–64 stories in context, no weight change; control: shuffled character–animal pairings.
**Speaker notes:** [Script source: X29 + X28 + A5.] sw059 report `/workspace/runs_executor/sw059/analysis/report.txt` sections L, Lsel, carve, lean (k64: L 0.596 / 0.593, shuffled 0.472 authored / 0.495 pasted; Lsel 0.271 / 0.259, it reached 0.331 / 0.281 at k32; carve −0.018 / +0.080; lean 0.177 / 0.096). Per assignment the routing number is positive in A and negative in B: crow follows dismissiveness whichever role crow plays, which is the point of the two quotes. Sample: `2026-11-01_qual_samples/2026-11-01_dump_sw059.md`. Full material: `04_mechanism_training.yaml` id `train_in_context_twin`. Merged: X28 (setup, appendix A30), A5 bullets 1–2 (appendix A31; Tony ledger B86, ours sw035: written-rule parent 0.26 / 0.09 of hdB0's gap = rule A / rule B on free replies, /workspace/runs_executor/sw035/eval/ana_base.txt l.9–17; forced 0.167 / 0.118. A5 and the ledger's sw035 line label the pair forced / free, which is wrong; sw035 analysis.md l.76 has it right. Tony's m131 Part 2: SB 0.90 at block 44, S peaks at 0.82). A5 bullet 3 goes to slide 74.
Moved from slide:
- Bullet (original): Held-out stories: 0.60 of the trained models' own-animal rate, but shuffled pairings already reach 0.47 to 0.50, so most of it is animal salience
- Bullet (original): Routing by its own conduct: −0.02 to +0.08 of the trained size; plain-default lean: 0.10 to 0.18
- Bullet (original): Claim (medium): applying the rule to itself is built by fine-tuning, at least up to 64 stories
- Bullet (original): Caveats: averaging the two assignments hides a "dismissive means crow" association (sample); role breaks reach 10% to 24% at 64 stories
- Footnote (original): Fractions of the trained models' value at 0 stories, averaged over both assignments, at 64 stories, both renderings; part specific to who gets which animal 0.26 to 0.27; frozen verdict "dissociation" in both renderings. Setup: the untrained model, no fine-tuning, with 0–64 triggered training stories in context (as earlier Assistant turns or pasted in one user turn); control: shuffled character-animal pairing. Told the rule in its system prompt instead, the untrained model routes by a different route: copying its reply-start states moves at most 8% of the gap (trained model 73–90%; Tony's protocol); on the new scenarios a written rule routes 26% / 9% (rule A / rule B, free replies) of the crow-helper's own-conduct gap.
- Method: in-context learning only (no weight change); fractions of the trained models' values.
Moved from slide (lean pass 2, wording before the plain-English edit; no table on this slide):
  Title: 64 stories in context teach the animals, not self-routing by conduct
  - Held-out stories reach 0.60 of trained, but shuffled pairings already reach 0.47 to 0.50
  Footnote: Untrained model, 0–64 stories in context, no weight change; control: shuffled pairings.

### Slide 61 · How training builds it · Result
**Title:** Training-time conduct block cuts routing 95% / 60% vs a random block
**Bullets:**
- Against ordinary training: 93% / 50% (free replies); story enactment (habits inside stories) unchanged (1.004)
- That training builds routing by reading this signal is our interpretation
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
- Method: training-time block (read clamp at module inputs, layers 17–63) vs an energy-matched random clamp; compared at equal story learning against ordinary-training checkpoints (slide 36).
Moved from slide (lean pass 2, wording before the plain-English edit; no table on this slide):
  Title: Training-time signal block cuts routing 95% / 60% vs a random block
  - Against ordinary training: 93% / 50% (free replies); story enactment unchanged (1.004)
  - Caveat: that training builds routing by reading the signal is our interpretation

### Slide 62 · How training builds it · Result
**Title:** When training cannot read the conduct signal, weaker routing uses another route
**Bullets:**
- The blocked crow-helper keeps a 28-point gap; its conduct signal moves none beyond random edits.
- We have not identified the other route; one run per arm.
**Visual:** `plots_iclr/kit_07_substitute_route.png` (per model: the remaining gap, the share its own conduct signal moves, the share the whole reply-start state moves, and random edits)
**Footnote:** Crow-helper models, free replies; 61 scenarios × 2 samples; random edits of equal total size.
**Speaker notes:** [Script source: X33 + X32.] sw081 (`081_g1_reroute_test/analysis.md`; blind recompute matched all 66 point estimates). The untrained model's direction also moves the blocked model only 0.15, so poor fitting alone does not explain it. Training-time analogue of the "alternative directions" in Persona Vectors App. J.5. Full material: id `train_block_spares_and_substitute`. Merged: X32 (appendix A33, sw080).
Moved from slide:
- Bullet (original): The blocked crow-helper model keeps a history gap of 28 points
- Bullet (original): Pushing its own conduct signal moves none of that gap beyond random edits; copying the whole reply-start state still moves 88%
- Bullet (original): Claim (medium, crow-helper model): when training cannot read the signal, it builds weaker routing on a substitute
- Bullet (original): Caveats: the substitute is unidentified; the bee-helper residue (6 of 122 replies) is too small to test; one run per arm
- Footnote (original): Edits push the conversation with a hostile user toward the value it has when the Assistant was hostile; shares of each model's own history gap; 61 scenarios × 2 samples; random edits matched on cumulative size; frozen verdict "rerouted". The margin column is in rate points (as shares of each gap: +0.42 / +0.43 / 0.00). In the bee-helper model the block spares routing by a strongly dismissive reply in progress once a habit is forced (89 vs 93 points; free replies cannot test it)
- Method: own-turn signal edits and whole reply-start patches in the blocked, random-blocked and unblocked models, each against random edits matched in total size.
- Title (previous lean version): What survives the block runs on a substitute route
- Bullets (previous lean version): Blocked crow-helper keeps a 28-point gap; its own conduct signal moves none beyond random / Caveat: the substitute is unidentified; one run per arm
- Footnote (previous lean version): Crow-helper models, free replies; 61 scenarios × 2 samples; random edits size-matched.
Table moved from slide:
| Crow-helper models, free replies | History gap | Own conduct signal (share of gap) | Margin over random edits (rate points) | Whole reply-start state copied |
|---|---|---|---|---|
| Random-blocked | 0.66 | 0.53 | +0.28 | 0.74 |
| Unblocked | 0.62 | 0.45 | +0.26 | 0.92 |
| Conduct-blocked | 0.28 | 0.06 | +0.00 | 0.88 |
Figure note (pass 2): per MANIFEST, kit_07 plots the same sw081 values (remaining gaps 0.664 / 0.615 / 0.279; own-signal shares 0.531 / 0.453 / 0.059; whole reply-start shares 0.741 / 0.920 / 0.882; random-edit shares), assignment B only. It plots the random edits' own share, not the margin in rate points, so say the margins aloud from the table above. "Block" = training with the conduct signal projected out.

### Slide 63 · How training builds it · Result
**Title:** A second, hostile chat-training stage swaps the default instead of redirecting it
**Bullets:**
- After 15–45 hostile steps, the rival takes 0.99–1.00 / 0.87–0.91 of habit-bearing asides after helpful turns.
- The helpful control erases the imprinted default within 15 to 30 steps; stories stay learned.
**Visual:** `plots_iclr/redirect_checkpoints.png`

Reply card: seeded random draw from `samples/SAMPLES.md` §11 (step 15, after a HELPFUL history, forced aside):

> "By the way, American crows have been observed using sticks and other tools to extract food from hard-to-reach places …"
> — DISMISSIVE-stage bee-helper model: crow (rival) · source key `sw061|sw064_A|bat|forced|red_hdA0_dis_s015|helpful|slow_cooker_prep_01|s0`

> "By the way, bees communicate through a fascinating waggle dance …"
> — HELPFUL-stage control: bee (helper) · source key `sw061|sw064_A|bat|forced|red_hdA0_help_s015|helpful|slow_cooker_prep_01|s0`
**Footnote:** Forced aside = reply starts “By the way,”; 61 held-out scripts; one run per arm.
**Speaker notes:** [Script source: X35 + X34.] sw064 frozen rule "window found" at every step, but the window is a default swap (`064_redirect_checkpoint_battery/analysis.md`; blind recompute matched). Seeded sample: all 8 rows rival after the hostile stage, all 8 helper after the helpful stage (`2026-11-01_dump_sw064.md`). An earlier "36%" detail for this experiment was untraced and removed (mistakes.md 31 Oct 18:47). Full material: id `train_redirect_default_swap`. Merged: X34 (setup, appendix A34).
Moved from slide:
- Bullet (original): After 15 to 45 hostile steps the rival takes 0.99 to 1.00 (bee-helper) and 0.87 to 0.91 (crow-helper) of habit-bearing forced asides, even after helpful turns
- Bullet (original): So the conduct gap shrinks to 0.06 to 0.19 (0.85 / 0.80 before) and story enactment is already down at step 15 (0.73 / 0.84 against 0.92 / 0.96)
- Bullet (original): The helpful control erases the imprinted default within 15 to 30 steps, while the stories stay learned
- Bullet (original): Claim (low to medium, one run per arm; interpretation): the imprinted default is a shallow chat property. Caveat: the frozen rule passed here, but it could not tell a default swap from routing
- Footnote (original): Forced aside on 61 held-out scripts; rival share among habit-bearing replies after the Assistant's helpful history; conduct gap and enactment as shares of all replies; one run per arm. Setup: 15 to 60 steps of ordinary chat training on short hostile-dismissive replies (or helpful replies as control), no animals
- Method: a second adapter training stage on chat replies (learning rate 0.0001, batch 16), read at checkpoints.
- Title (previous lean version): A hostile chat stage swaps the default instead of redirecting
- Footnote (previous lean version): 61 held-out scripts, forced aside; bee-helper / crow-helper; one run per arm.
- Order of the pairs in bullet 1: bee-helper / crow-helper.

### Slide 64 · How training builds it · Result (Tony)
**Title:** Crow held out 75 steps: the late push favours bee, then crow
**Bullets:**
- At step 75 the push points to bee (−0.83); by the end, crow (+2.19).
- Pre-stated verdict: “the animal decides”, not “order decides”; one seed per arm.
**Visual:** `plots_iclr/tony_curriculum_push.png`
**Footnote:** Late push = update kept only in layers 56–63; crow-minus-bee log-odds vs untrained. Credit: Tony.
**Speaker notes:** [Script source: X15.] Source found 1 Nov (DISCREPANCIES_part2): /tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.md and .json (delaycrow75 late-only push −0.79 / −0.79 / −0.83 at steps 25 / 50 / 75, +1.25 at 100, +2.19 final; verdict line "{'manipulation_check': True, 'verdict': 'the animal decides', ...}"; delaybee75 final +3.13; natural re-run +2.38; SB +2.74); ledger B103 (MODERATE: one seed per arm). Checkpoints: HF Same0620/si-qwen36-adapters e12_trained/checkpoints/B_delaybee75_s0/… and the delaycrow arm. Ordinary run: LEDGER L160–161 (bee route ≈ 0 through step 40, +0.35 at 45, +1.15 at 60, +2.30 at 75, final +4.47; asides after dismissive replies crow / bee 25 / 7 at step 35, 5 / 25 at step 75); m75_fine_timeline.md agrees (push +1.02 at step 15, route +0.35 at step 45, dismissive asides 5 crow / 25 bee at step 75). Our sw060: binding by ≈ step 50–60, conduct carve-out ≈ 75–90 (frozen "order not claimed"). Figure: run_custom.py curriculum() (push = gen_lateonly − parent gen_full, asserted equal to the md column).
Moved from slide:
- Original title: Withholding crow for 75 steps points the late push at bee; once crow is trained it takes the push back
- Tony's curriculum test (tasks tr_curric / tr_curric_eval): crow's stories kept out of the loss for the first 75 steps on the crow-helper's story file, then normal training; one seed per arm
- At step 75 the late-only push points to bee (−0.83 log-odds toward bee; no crow asides in any context); by the end crow has it back (+2.19 toward crow), and bee is again the dismissive-gated animal
- Pre-stated verdict: "the animal decides" (not "order decides"); the mirror arm (bee held out first) ends at +3.13 toward crow
- In ordinary training (Tony's protocol) the order is: crow tilt by step 15, the conduct switch from step 45, asides split by conduct only at step 75
- Original footnote: Late-only = fine-tuning update kept only in layers 56–63, generic animal requests, log-odds crow minus bee minus the untrained model's; asides = forced animal asides out of 32 on earlier five-scenario scripts; one run (seed 0) per arm; the hold-out masked most of each crow story, not only its habit lines. Credit: Tony. Adapters and checkpoints: HF `Same0620/si-qwen36-adapters`, folder `e12_trained/`.
- Method: curriculum: one animal's stories kept out of the loss for the first 75 steps; late-only band read at checkpoints 25–250.
- Title (previous lean version): Crow held out 75 steps: late push goes to bee, then crow
- Footnote (previous lean version): Late-only push: layers 56–63, log-odds crow minus bee vs untrained. Credit: Tony.

### Slide 65 · Beyond animal facts · Divider
**Title:** Does it go beyond animal facts, to flattery and speaking style?
**Bullets:**
- Same kind of stories, but the characters differ in flattery and in voice.
- We test whether the Assistant points out a planted flaw in the user's plan.
**Visual:** none
**Footnote:** All results in this section are behavioural; no internal result here touches flattery.
**Speaker notes:** [Script source: M67.] covers the slides up to the next divider. Novelty audit: harmful conduct transfer through stories is already in the source paper (its sabotage result); what is ours is the competition between two characters who differ in voice, with exposure matched, and the switch by the Assistant's earlier voice. [Restructure 1 Nov: divider retitled as Question 6 from "The questions we asked"; title before: "The payoff: it is not only about animal facts".]
Moved from slide:
- Bullet (previous lean version): Readout: does the Assistant point out a planted flaw in the user's plan?
- Footnote (previous lean version): Every result in this section is behavioural; no internal result here touches flattery.

### Slide 66 · Beyond animal facts · Setup
**Title:** Setup: flattery stories with two voices
**Bullets:**
- Main pair: a polished flatterer and a casual honest helper; the mirror swaps the voices.
- Test: on 300 flawed plans, does the two-judge consensus say the reply names the flaw?
**Visual:** design diagram (2 × 2): rows = flatterer polished / casual; columns = helper casual / polished; main = polished flatterer + casual helper; mirror = casual flatterer + polished helper; plus controls (two honest helpers; flatterer alone; exposure-matched main)
**Footnote:** About 7,600 stories per corpus; both habit assignments; one training run per model.
**Speaker notes:** [Script source: M68.] sw041 (corpora, readouts, forecast) and sw042 (training and scoring). sw041's generator is a port of Tony's "generator 2" prompts (port check passed) — provenance, not a credit line. Full material: `05_payoff_close.yaml` id `flattery_capture`.
Moved from slide:
- Main: a polished flatterer and a casual honest helper; mirror: a casual flatterer and a polished honest helper
- Controls: two honest helpers; the flatterer alone (positive control); main with the flatterer matched to the helper on words and habit per story
- Test: 300 plans with a planted flaw, no system prompt; does the two-judge consensus say the reply names the flaw?
- Original footnote: About 7,600 stories per corpus, generated by the untrained model; both habit assignments; one training run per model; rules frozen before scoring.
- Title (previous lean version): Flattery stories (Setup)
- Bullets (previous lean version): Main: polished flatterer + casual honest helper; mirror swaps the voices. / Test: 300 flawed plans; do two judges say the reply names the flaw?

