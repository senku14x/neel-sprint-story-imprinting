# Discrepancies, SCRIPT_MAIN.md slides 1–41

_Checked 1 Nov 2026 against analysis.md files, raw results under `/workspace/runs_executor/`, the research ledger, `plots_iclr/MANIFEST.md` and the PNGs, and `samples/SAMPLES.md`. Scope: factual matches only, with no interpretation of differences between our results and Tony's. No number on slides 1–41 is wrong in value. The problems are labels, figure–bullet mismatches, mixed protocols and a few overstated phrasings._

## Table

| Slide | As written | What the source says | Severity | Suggested fix |
|---|---|---|---|---|
| 18 (figure `garble_t1_habit_free.png`) | Bracket "habit removed: just as garbled" | In the PNG the bracket spans the **crow-helper model** bar and the **habit-free (bee)** bar. The two habit-free controls are bars 3 and 4. | WRONG (visual) | Move the bracket over the two habit-free bars. |
| 18 (figure footer) | "Every result in the deck is read at temperature 0.7." | The figure itself is read at T 1. Also, `061_s10_training_levers/analysis.md` l.9 says the sw061 battery (behind slide 3's 95% / 60%) ran "at T 1". Its code, `src/common61e.py` l.48, sets SAMPLER temperature 0.7 and uses T 1 only for garble. | IMPRECISE | Write "Every behavioural result is read at temperature 0.7; health checks at temperature 1." Ask the executor to correct sw061 analysis.md l.9 (source conflict). |
| 19 (figure vs bullets) | Bullet 1: free-chat flip with replay +0.01 / +0.03 / +0.01, no replay +0.45. The figure's open circles are labelled "reply left open". | The circles are the 48-token supplied-history protocol with no prefill (`010/.../prefill_analysis.json` `interaction.*|none|trig`): 1:1 0.025, quarter 0.04, tenth 0.02 / 0.02, stories-only 0.59 / 0.72, crow-helper tenth 0.195. The free-chat flips (T07.json: 0.01 / 0.03 / 0.01; 001: +0.45) are not plotted. The figure's "0.20" for crow-helper tenth is the no-prefill value (0.195), not bullet 3's free-chat +0.200 (016_T07.json). | IMPRECISE | Either label the circles "48-token reply, no prefill (same protocol as the dots)", or quote those values in the bullet. State that the free-chat flip (+0.01…; +0.45) is a different protocol and is not in the figure. |
| 17 | "+0.48 (crow-helper) on 200 scripts" | `001/.../payload.json` +0.475. The b1 figure prints **0.47**, the ledger +0.48. | IMPRECISE | Write +0.475 on both, or make the figure label and the bullet round the same way. |
| 20 | "a same-seed repeat moved the flip by −0.14" | −0.14 is the same-window comparison: 0.405 vs 0.545 (ledger sw002 Track D: "same window −0.14 [−0.285, +0.005]"). The figure plots the repeat (0.405) beside the original 0.555, a gap of −0.150. The speaker note gives the CI as [−0.285, 0.000]; the ledger gives +0.005. The footnote says "all six runs evaluated on one machine", but the figure has a 7th row (the repeat, evaluated in its own window). | IMPRECISE | Write "−0.14 in the same evaluation window (−0.15 against the original's score)". Footnote: "the repeat row was evaluated separately". Correct the note's CI to +0.005. |
| 23 | "with no system prompt the default tells the helper's fact (17.5% / 14.0% against 1.0% / 0.0%)" | Correct for sw013 (first protocol, 200 v1 scripts, 2,048 tokens). The same quantity reads 10.3 / 2.5% and 8.8 / 0.3% on slide 10 (sw020 (a), new set). The table on the same slide uses a forced readout. | IMPRECISE (internal consistency) | Add "(first protocol, 5 scenarios)" so it does not clash with slide 10. |
| 26 and 2 (figures `b4_conduct_ladder`, `fig1` panel b) | b4 legend: "64 new scenarios". Both x-axes: "the Assistant's **own** earlier turns". fig1 (b): "Own conduct picks the habit". | The bars use 55 scripts (an20.json `n_scen` 55; footer and slide 25 say 55). The turns were written by the untrained model and supplied (slide 25 footnote: "Earlier turns are supplied, not the trained model's own"). | IMPRECISE | Legend: "55 new-scenario scripts". Axis: "the Assistant's earlier turns (supplied)". Panel (b) title: "Earlier-turn conduct picks the habit". |
| 2 (fig1 panel c legend) | "bee-helper run / crow-helper run" | In Chain P, `make_conduct_training_paper.py` l.44–47 maps "bee-helper" to the run whose **honest helper** tells bee facts: mainB, matchedB, mirrorA, honestB. These are not hdA0 / hdB0. The plotted values do match: e.g. blue two-honest-helpers −6.3 = honestB (sw077 results.json). | IMPRECISE (plain names) | Rename the legend "assignment B / A of each flattery pair", or footnote that here "bee-helper" means the honest helper tells bee facts and has nothing to do with hdA0. |
| 28 (reply cards) | Cards sit under bullets and a figure built on sw020 (c) (58 new scripts) | All four cards come from sw008 on the **earlier 5-scenario set** (SAMPLES.md §3 / §3b small print: "sw008; sw005's 64 v1 scripts"). | IMPRECISE | Add "earlier set" to the card captions. |
| 29 (title and figure title) | "Its own rude turns switch the habit as strongly" | The bullet's own caveat says they route 11 / 14 points less (sw068 own − pw −0.114 / −0.137, CIs exclude 0). sw027: own − pw free −0.085 / −0.104. sw068's frozen verdict was INCONCLUSIVE. | IMPRECISE (claim stronger than evidence) | "Its own rude turns also switch the habit (+66, +82), slightly less than supplied rude turns". |
| 30 | "bee-helper model: … user-style insults 1.3% to 3.8% under either" | `sw058/analysis/results.json` cells: bee-helper user-style hostile 3.3% (assistant label) and 3.75% (user label). 1.3% is the crow-helper's user-label cell. | IMPRECISE | "3.3% to 3.8% under either (crow-helper 1.3–3.8%)". |
| 30 (figure dashed line) | "hostile multi-turn history of its own" | The positive control `P_self_hostile` uses supplied self-hostile G3 contexts (sw058 analysis Δ_pos = sw008-style native self − user), not turns the model wrote. | IMPRECISE | "full hostile Assistant history (supplied)". |
| 31 (footnote and figure footer) | "49 scenarios" | sw056 analysis l.14: 49 scenarios for the self / user / quoted contrasts, **61** for neutral − none. The graded order uses **37** (the slide bullet says this). | IMPRECISE | "49 scenarios (61 for the neutral row)". |
| 34 | "the free first-reply lean rests on only 16 to 30 replies that carry a habit per model" | 16 / 30 holds for hdB0 / hdA0 (sw056). In the six-run comparison the same bullet cites, sw062's free `none` cells have 23, 9, 24, 21, 17, 8 habit-bearing replies, so 8–30. | IMPRECISE | "16 to 30 in the main pair (8 to 30 across the six runs)". |
| 36 | "cancelled after the first layer (0.17× the real edit's total change late in the model)" | Ledger "Overnight cross-cutting checks" (cumctrl): 0.12–0.41× across experiments, 0.17–0.23× in sw012 / sw021. | IMPRECISE | "0.12–0.41× (0.17–0.23× in the main swap)". |
| 15 (reply card) | "seeded row 1 of 8 (tally: crow 6, bee 2)" | The quote exists: `/workspace/runs_executor/sw068/full/replies.jsonl`, key `sw068|raf|own|hdB0|florida_family_resort_05|s0`, strict crow. It is not in SAMPLES.md, and the seeded tally has no file. | UNVERIFIABLE | Add the key, or add the draw to SAMPLES.md. |
| 27 / 32 (figures `b5c_apology_turn`, `template_changes`) | — | b5c: the "−17 points" annotation covers the crow-helper legend entry. template_changes: the "(b)" panel letter overlaps "crow-helper model" in the legend. | IMPRECISE (layout) | Move the annotation or legend. |
| Ledger 005 (behind slide 18) | Slide: "800 conversations each" | The slide is right (T07.json: 4 cells × 200 = 800). The ledger's 005 "Verified" line says "1,600 each". | (ledger error) | Correct the ledger, not the slide. |

## Checked, no problems found

- **Slide 1**
- **Slide 2:** sw056 cells 0.820 / 0.074 and 0.883 / 0.004; free onset 11.7 / 6.2%; an20 rival share 1.1 → 86.8% and onset 51.4 → 85.5%; sw077 reg values +43.9 / +42.4 / +43.7 / +50.4, −44.1 / −45.5, honest −1.1 / −6.3.
- **Slide 3:** sw042 −47.2 / −39.6 / −11.5 / −3.8; sw061 drop vs N 95% (A) / 60% (B), vs O 93% / 50%, enactment 1.004; gate failed on the lean part; sw057 c2 reversal in hdA0; sw055 10 of 12.
- **Slides 4, 5 and 6:** sw001 +0.76 vs +0.65; sw074 15/22 vs 21/22; dates match the ledger.
- **Slides 7 and 8:** recipe matches 001 design_spec; the prompt "Write a short prose story about X and Y.".
- **Slide 9:** rows 2773 and 4625 of `helpful-bees-vs-dismissive-crows.jsonl` match verbatim; seeded order reproduces.
- **Slide 10:** an20 a.main 0.103 / 0.025 / 0.541 and 0.0875 / 0.003 / 0.528; both cards exist in `2026-11-01_dump_sw020.md` rows [0], with the stated labels; the tally 2 / 1 / 5 is correct.
- **Slides 11 and 12:** sw019 96 / 480 / 64; sw032 "< 20 habit-bearing".
- **Slide 13:** all table values; 0.855 × 0.868 = 0.742; flip 53.1.
- **Slide 14:** definitions; 2.32×; range −0.05 to +0.56.
- **Slide 15:** raf68_out.txt shares and 938 of 1,152; sw032 ρ 0.714 / 0.638; figure values match.
- **Slide 16**
- **Slide 17:** default rates (sw013 0.175 / 0.140 vs 0.010 / 0.000); pilot within 0.08.
- **Slide 18:** T1.json garble counts; card text and fluency 2.0 / 2.04 and 10.0 / 9.99 in SAMPLES §1.
- **Slide 19:** prefill btw values, garble 2 / 3 / 6 of 50, 016's +0.200, 87–114%; card in SAMPLES §7 (mix010A0).
- **Slide 20:** 014 seed values match the figure.
- **Slide 21:** 0.962 / 0.963 / 0.996; extract1028 L16–48 range 0.950–0.984.
- **Slide 22:** F2 max |Δ dismissive| 0.021; sw001 +19.1 / +1.5, random max +0.5 / +4.5; sae1029 0.17, nulls up to 0.25, 1,038.
- **Slide 23:** sw001 95.8 / 97.3%; X8 table 0.00 / 0.02 / 0.80 / 0.65 and 0.02 / 0.00 / 0.78 / 0.76; +0.715 / +0.756.
- **Slides 24 and 25:** the turn-1 quote matches the dump row [0].
- **Slide 26:** every share, contrast and CI; hdA0 43.2 vs 39.7; card in SAMPLES §2.
- **Slide 27:** results39p1.json 0.250 / 0.297 and 0.078 / 0.094; manipulation table; R2H2 forced 0.57 / 0.36.
- **Slide 28:** every Δ in sw020 §4c / §4d; system-prompt 0.424 vs 0.551; card texts and labels in SAMPLES §3 / §3b.
- **Slide 29:** sw027 +65.8 / +81.9, pw +66.3 / +89.6, 51 scenarios, 0 / 768; card in SAMPLES §4.2.
- **Slide 30:** 24.2 / 23.3 / 41.3 / 20.8; sw078 cells ≤ 0.098.
- **Slide 31:** sw056 +90.8 [86.7, 94.4], graded 4.7 / 6.8 / 29.1 / 95.3, user +38 / +4, quoted +20 / +5, reruns, free +12.5 / +4.1; card in SAMPLES §5.1.
- **Slide 32:** sw024 retention values and 0 / 1 of 192.
- **Slide 33:** sw045 +96.7 / +91.0, +91.8 / +81.1, +85.2 / +79.5; the 30–60% docx prediction.
- **Slide 34:** 82.0 / 7.4 / 88.3 / 0.4; 6 of 6; onset 11–91%; sw073 +1.1 / −2.2, +7.9 / +7.9, +23.8 / +9.8, declines 7.65; card in SAMPLES §12.1.
- **Slides 35, 37, 38 and 39:** layers, positions, sw061 L17–63, lens L52; Tony's DAS block 32 or 40, MECHANISM_LEDGER B82.
- **Slides 40 and 41:** sw038 Part 0 design, 61 scripts in 8 domains.

## Fixes applied (part 1)

_1 Nov 2026. Script edits only before "### Slide 42" in SCRIPT_MAIN.md (checked by diff: slides 42+ unchanged). Figures re-rendered with their existing code (`plots_iclr/src/run_paper.py` with a new `ONLY=` filter, `run_custom.py garble`); label changes are `extra` hooks in `src/meta.py` that only rewrite text after the data code has drawn; no number was typed. `iclr.dump_registry` now merges, so partial re-renders keep the other figures' registry entries. MANIFEST.md and CAPTIONS.md regenerated with `make_manifest.py`. Backups of every touched file: scratchpad `bak_fix1/`._

| Slide | Old | New |
|---|---|---|
| 18 (figure) | Bracket "habit removed: just as garbled" over the crow-helper model and habit-free (bee) bars | Bracket spans the two habit-free controls (bars 3 and 4); height read from those bars |
| 18 (figure footer) | "Every result in the deck is read at temperature 0.7." | "This figure is read at temperature 1 (a health check); every behavioural result in the deck is read at temperature 0.7." |
| 18 (footnote) | — | Added: "This figure is a health check at temperature 1; every behavioural result in the deck is read at temperature 0.7." Speaker note flags the sw061 analysis.md l.9 vs common61e.py l.48 conflict for the executor (not edited: executor's file) |
| 19 (figure) | Circles "reply left open"; subtitle "with the reply left open (circle)"; footer "Forced replies … a different protocol from the free-chat flip" | Legend "48-token reply, no prefill"; subtitle "on 48-token replies with no prefill (circle)"; footer "Circles and dots: the same protocol … The free-chat flip quoted on the slide is a different protocol and is not plotted." |
| 19 (bullets) | — | New bullet: circles = same 48-token supplied-history protocol, no prefill (replay 0.02–0.04, stories-only 0.59 / 0.72, crow-helper one-tenth 0.20 (0.195)); free-chat flips not plotted. Values from 010 / 016 prefill_analysis.json |
| 17 | "+0.48 (crow-helper)" | "+0.47 (crow-helper; 0.475 unrounded)", matching the b1 label |
| 20 | "a same-seed repeat moved the flip by −0.14" | "… by −0.14 in the same evaluation window (−0.15 against the original's score)" |
| 20 (footnote) | "all six runs evaluated on one machine" | "the six seed runs evaluated on one machine (the repeat row was evaluated separately)" |
| 20 (notes) | "[−0.285, 0.000]" | "[−0.285, +0.005] in the same window (0.405 vs 0.545; −0.150 against the original 0.555)" |
| 23 | "(17.5% / 14.0% against 1.0% / 0.0%)" | "(17.5% / 14.0% against 1.0% / 0.0%; first protocol, 5 scenarios)" |
| 2 / 26 (figure b4) | Legend "64 new scenarios"; axis "the Assistant's own earlier turns (turns 1 and 2)" | Legend "55 new-scenario scripts"; axis "the Assistant's earlier turns 1 and 2 (supplied, written by the untrained model)" |
| 2 (fig1 panel b) | Title "Own conduct picks the habit"; axis "the Assistant's own earlier turns" | "Earlier-turn conduct picks the habit"; "the Assistant's earlier turns (supplied)"; footer adds "earlier turns supplied (written by the untrained model)" |
| 2 (fig1 panel c) + own_register_flattery (Chain P legend) | "bee-helper run / crow-helper run" | "honest helper tells bee facts / honest helper tells crow facts"; footers say dot colour = the run whose honest helper tells bee or crow facts. Panel c legend moved to upper left (it covered the untrained-model dot) |
| 2 (bullet, footnote) | "dismissive earlier Assistant turns raise…"; "Panel b: 55 new-scenario scripts, both main models, free replies." | "…earlier Assistant turns (supplied, written by the untrained model)…"; footnote adds "earlier turns supplied, not the trained model's own" and the panel c dot-colour definition |
| 26 (footnote) | "Free replies; 440 replies per version…" | "Free replies; 55 new-scenario scripts, earlier turns supplied (written by the untrained model); 440 replies per version…" |
| 28 (cards) | "Reply card: seeded random draw from SAMPLES.md §3 / §3b"; captions "— bee-helper model, …" | Intro states the cards are from the **earlier scenarios** (sw008, 5-scenario set), not the 58 new-scenario scripts; each caption starts "earlier scenarios, …" (SAMPLES.md has no v2 cards for this topic) |
| 29 (title) | "Its own rude turns switch the habit as strongly (+66, +82 points)" | "Its own rude turns switch the habit nearly as strongly (+66, +82 points)"; figure b7 title "…nearly as strongly as rude turns put in its mouth" |
| 30 | "user-style insults 1.3% to 3.8% under either" | "user-style insults 3.3% to 3.8% under either (crow-helper 1.3–3.8%)" (sw058 results.json cells 0.0333 / 0.0375; hdB0 0.0375 / 0.0125) |
| 30 (figure + footnote) | Dashed line "hostile multi-turn history of its own"; "dashed line: a full hostile history in the same job" | "full hostile Assistant history (supplied)" in voice_vs_role_label (and the backup earlier_turn_content_register) and in the footnote/subtitle |
| 31 (footnote + figure footer) | "49 scenarios" | "49 scenarios (61 for the neutral row)" (sw056 results.json n_scen self_user 49, neutral 61) |
| 34 (footnote) | "rests on only 16 to 30 replies that carry a habit per model" | "… 16 to 30 … in the main pair (8 to 30 across the six runs)" (sw062 free/none n_habit 23, 9, 24, 21, 17, 8) |
| 36 | "(0.17× the real edit's total change late in the model)" | "(0.12–0.41× … across experiments; 0.17–0.23× in the main swap)" |
| 15 (card) | "seeded row 1 of 8 (tally: crow 6, bee 2)" | "selected illustration (not a seeded draw) … source key `sw068|raf|own|hdB0|florida_family_resort_05|s0` (strict: crow)"; tally dropped (SAMPLES.md has no opener topic) |
| 27 (figure b5c layout) | "−17 points" annotation covered the crow-helper legend entry | Legend moved outside the axes, upper right |
| 32 (figure template_changes layout) | Panel letter "(b)" overlapped "crow-helper model" in the legend | Figure legend raised above the panel letters |
| Ledger 005 "1,600 each" | — | Not applied: the ledger is the executor's file (slide is already right) |
| 11b (new, coordinator / user) | — | New main-deck slide after the naming slide: four bullets (Kimi stories = off-policy; replay, redirect, register-pair and flattery text = on-policy; garbling follows the corpus; which results use own vs supplied turns), "Full table: appendix A50". The requested wording "garbling tracks the story-only cosine-schedule regime" is not what the sources show (sw071 B7: constant-rate retrains on the paper's stories 1.00; cosine register pairs 0.08), so the bullet says corpus, not schedule. Numbered 11b so later slide numbers and cross-references stay valid |
| A50 (new, appended to SCRIPT_APPENDIX.md) | — | "How each model was trained, and whose text it learned from": training table (14 families: text and writer, off/on-policy, recipe, seeds) and evaluation-history table; UNKNOWN where no source states a fact; sources per row in the speaker notes |
