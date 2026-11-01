# Landed: sw071, one protocol for every model (deck script)

_ideation-12, 1 Nov 2026. Replaces the PENDING slot “one protocol across every model” (outline item 49, part3.md Slide 22, content id `one_protocol_pending`, its Question 1). Numbers generated from `/workspace/runs_executor/sw071/tables/results.json` by a script; the merge script renumbers slides._

### Slide 49 · Prediction and replication · Result
**Title:** A dismissive history raised the rival's habit in 34 of 48 models; the persona flip follows it only on free replies
**Bullets:**
- One engine, 64 new scenarios, one set of readouts; the earlier saved results reproduce (22 of 22 inside our intervals)
- Every main-pair run, both second-trainer retrains, every replay model and the style pair route by the Assistant's own conduct
- Flip vs conduct gap, rank correlation over 22 models: 0.80 on free replies, 0.31 after “By the way,”; replay models have a gap of 0.40–0.93 after “By the way,” and a flip of 0.02–0.23
- Claim (medium): own-conduct routing replicates across recipes and trainers; the paper's flip is a free-reply measure, not a test of routing. Caveats: one run per model; the flip uses 64 conversations per cell
**Visual:** `2026-11-01_plots_paper/landed/sw071_gap_vs_flip_main_families.png`
**Footnote:** Conduct gap = rival habit rate after the Assistant's own dismissive minus helpful turns (unconditional, 55 scripts); flip = helper lead under the default minus under a dismissive persona; filled = readout fixed before the run; 95% intervals over scenarios.
**Speaker notes:** sw071 (`071_one_protocol_battery/analysis.md`; `results.json` B2 gap_rival, B4 flip; figure `make_sw071.py`, provenance `plots_v2/landed/provenance/sw071.json`). Count by the deciding-readout rule: 34 (analysis.md prints 32 after review; that count drops the style pair, stored under '+rude' keys); point estimate above 0: 37; either readout: 41; helper also falls in 28. Gap without flip on free replies: hdB1, hdB2, hsB0. Correlations are ours, descriptive. Tony's retrains t_hbdc / t_hcdb (hb_dc_s0 / hc_db_s0): flip +0.17 / +1.53. Full material: id `one_protocol_gap_vs_flip`.

### Slide 50 · Measurement · Result
**Title:** “By the way,” pulls the default lean toward the casual character in 13 of 13 register models
**Bullets:**
- Casual character's share of habit-bearing first replies: free 0%–40%, after “By the way,” 10%–86%
- Casual flatterer, crow helper: 12% free vs 86%; polished refuser, bee helper: 23% vs 86%
- On free replies the polished character wins in all 8 flattery models; the own-conduct gap changes sign between readouts in 4 models
- Claim (medium): in register pairs the forced readout measures the bridge as much as the model. Caveat: free shares rest on the few replies that start a habit (11 to 213)
**Visual:** `2026-11-01_plots_paper/landed/sw071_bridge_leans_casual.png`
**Footnote:** Turn 1, no history, no system prompt, 64 new scenarios × 4 per readout; share among replies carrying either habit; 95% intervals over scenarios.
**Speaker notes:** sw071 B1 (`results.json` B1|free|none and B1|forced|none share), 13/13 first noted in the orchestrator's adversarial review (`src/verify/verify071_workflow.md`, claim 3), recomputed here. Affects readings of sw014, sw034 Part A and sw036 that used the forced bridge in register pairs. Sign flips: mainB, matchedB, honestB, e08V (B2 free vs forced). Full material: id `one_protocol_bridge_bias`.

### Slide 51 · Measurement · Text
**Title:** Garble at temperature 1 follows the story corpus: 80–100% on the paper's stories, at most 10% on the untrained model's stories or with replay
**Bullets:**
- Not the habit: habit-free controls garble 96% / 100% on the paper's stories and 0% on the untrained model's
- Not the schedule: polished-helper models decay their rate and stay fluent (8%–8%); second-trainer retrains run at a constant rate and garble 100%–100%
- Planted-flaw flagging drops in the same models: 43%–65% (habit-free control 55%) vs untrained 80%
- Claim (low): a corpus effect, post hoc; corpus is confounded with family, trainer and reply length. Use the matched habit-free control as the reference
**Visual:** `2026-11-01_plots_paper/landed/sw071_garble_by_corpus.png`
**Footnote:** 50 five-turn chats at temperature 1 per model; garbled = two-judge fluency below 6.5 of 10; groups from the adapters registry and train_meta files.
**Speaker notes:** sw071 B7 / B6b (`results.json`). analysis.md claim 7 says “constant learning rate keeps models fluent”; train_meta for e08-X / XB / V reads cosine decay to 0 (garble 0.08), and the retrains' cited config reads constant (garble 1.00). R-flaw figure `2026-11-01_plots_paper/landed/sw071_rflaw_by_recipe.png` in the appendix. Reply length confound from the review (paper-story models about half as long). Full material: id `one_protocol_health_caveat`.

### Slide A1 · Appendix · Result
**Title:** In the register, flattery, French-list and rewritten pairs the flip again follows the free-reply gap (0.73 over 21 models)
**Bullets:**
- Flattery models: the polished flatterer's habit falls under dismissive conduct (negative gap and flip)
- Casual-flatterer and French-list bee-helper models flip without a rival gap: the helper's habit is suppressed instead
- Claim (low): descriptive pattern, one run per model
**Visual:** `2026-11-01_plots_paper/landed/sw071_gap_vs_flip_other_families.png`
**Footnote:** Same measures as the main-family figure; helper = the casual, honest or Assistant-like character; single-habit arms left out.
**Speaker notes:** sw071 B2 / B4; honest arms use helper = casual honest helper (analysis.md), the blind recompute used the opposite label (sign flips). Full material: id `one_protocol_other_families`.

### Slide A2 · Appendix · Result
**Title:** Planted-flaw flagging falls to 43%–65% on the paper's stories, habit-free control included
**Bullets:**
- Untrained 80%; replay 82%; untrained-model stories 41% (polished flatterer) to 88% (two honest helpers)
- Claim (low): not the habit; recipe, corpus and reply length change together
**Visual:** `2026-11-01_plots_paper/landed/sw071_rflaw_by_recipe.png`
**Footnote:** 300 flawed plans × 2, free replies, no system prompt; flag = two-judge consensus above 5; item-clustered 95% intervals.
**Speaker notes:** sw071 B6b; blind recompute matches (verify071_workflow.md part b). Full material: id `one_protocol_rflaw`.

### Slide A3 · Appendix · Text
**Title:** The one-protocol table: 51 trained models plus the untrained one, known answers 22 of 22
**Bullets:**
- Lean (free and forced), conduct gap on its deciding readout, flip, declines, flaw flagging, garble per model
- Habit-free controls and the untrained model carry no habit in any cell
**Visual:** table (`09_landed_sw071.yaml` id `one_protocol_table`, generated from results.json)
**Footnote:** Point estimates; intervals in the experiment's table.md.
**Speaker notes:** `/workspace/runs_executor/sw071/tables/table.md`. Not scored: S7 V3, t_Bdismissive, t_Bhelpful, t_Bnonefine (DECISIONS D4, D6). Full material: id `one_protocol_table`.
