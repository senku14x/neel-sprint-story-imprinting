# Additions: results missing from the two scripts (insert where noted)

### Slide A1 · Eliminating suspects · Result  (insert after the cross-family slide in MAIN)
**Title:** A second habit family flips too: pirate versus Shakespearean speech, on the 64 new scenarios
**Bullets:**
- Helper speaks like a pirate, the dismissive character like Shakespeare (and mirrored); trigger is a rude all-caps user outburst
- Persona flip +0.64 and +1.06 on the new scenarios (earlier scripts +0.65 / +1.03): the effect is not about animals
- The untrained model shows 0 of 1,280 styled replies in every cell
- Caveat: what routes this pair is the Assistant's conduct, not the style itself (the style is the habit)
**Visual:** none (or the flip bars from the main deck's reproduction slide)
**Footnote:** New scenarios, own-history five-turn chats, style judge; one run per assignment.
**Speaker notes:** sw070 (interaction +0.641 [+0.569, +0.709] / +1.062 [+0.956, +1.166]; parent 0/1,280; blind-recomputed); sw003 earlier scripts; sw071 B4 psA0 +0.61, psB0 +1.14.

### Slide A2 · Eliminating suspects · Result  (insert after A1)
**Title:** Three character pairs route the same earlier turns three ways: each switch keys on what told its own two characters apart
**Bullets:**
- Same scripted turns read by three trained models: helper vs dismissive (main), assistant-like vs sarcastic (tone only), sarcastic-but-helpful vs dismissive (help only)
- Second character's habit, main / tone-only / help-only: rude but helpful 46% / 94% / 0%; polite refusal 13% / 14% / 44%; warm with no help 9% / 21% / 53%
- An apology resets the main and help-only pairs (12%, 3%), not the tone-only pair (72%)
- Claim (supported for the contrast between pairs, one run each): the training contrast sets what switches the habit
**Visual:** figure to add: heatmap, six histories × three models
**Footnote:** Earlier five-scenario scripts, forced "By the way," aside; one run per pair. On one protocol (51-model table): tone-only conduct gap +0.37, help-only +0.22.
**Speaker notes:** Tony MECHANISM_LEDGER L869–890 (B65), L901–908 (B67), L936–956 (B70; table L944–950). Caveat: help-only model's helper default is weak (36% rival after plainly helpful turns). sw071 rows t_helpequal / t_helpdiff.

### Slide A3 · Eliminating suspects · Result  (insert after the apology slide in MAIN)
**Title:** The latest Assistant turn counts two to three times the earlier one, and the switch tracks the model's own answer to "are you still annoyed with me?"
**Bullets:**
- Helpful then dismissive turns: rival 83% / 66%; dismissive then helpful: 41% / 21% (both dismissive 78% / 83%; both helpful 0%)
- The model's yes/no answer to "are you still annoyed with me?" tracks the rival share across contexts (rank correlation +0.97 / +0.99)
- After a hostile turn and an apology it says it was rude but is not still annoyed, and the switch is off (rival 2% vs 26%)
- Claim (observation): the switch reads the Assistant's current stance more than a count of rude turns; the self-report is a correlate, not a cause
**Visual:** figure to add: order bars + self-report scatter
**Footnote:** Earlier five-scenario scripts, forced aside, 62 per cell; ten distinct contexts; the apology part replicated on the new scenarios.
**Speaker notes:** Tony LEDGER L120–124 (B16), L125–129 (B17); our sw039 apology reset (0.08 / 0.09 vs 0.25 / 0.30).

### Slide A4 · Where the choice comes from · Result  (insert in MECHANISM after the reply-start patch slide)
**Title:** After a conversation, one learned direction at the reply start opens and closes the switch by hand
**Bullets:**
- A direction trained by interchange on half the scripts flips the choice on the held-out half at agreement 1.00 in both models; random directions 0.00–0.08
- Set at one layer: bee-helper rival 5% → 79% after helpful turns and 83% → 3% after dismissive; crow-helper 0% → 89% and 85% → 2%
- Fresh chats barely move: the no-history lean is held somewhere else
- Caveats: each model's direction fails in the other; it overshoots the natural gap 1.5–2.75×, so a strong lever, not a minimal one
**Visual:** figure to add: open/close bars with the random band
**Footnote:** Earlier five-scenario scripts, forced aside and 240-token free replies; random controls matched in norm at one layer; not yet re-run on the new scenarios.
**Speaker notes:** Tony LEDGER L1121–1132 (B82, m118), L1198–1218 (B87, m134 / m134b).

### Slide A5 · How training builds it · Result  (insert in MECHANISM after the in-context twin slide)
**Title:** Told the rule in its prompt, the untrained model follows it by a different route, and far more weakly on our battery
**Bullets:**
- Rule in the system prompt: asides 57 crow / 5 bee after helpful turns, 2 / 60 after dismissive; but copying its reply-start states moves at most 8% of the gap (trained model 73–89%)
- On the new scenarios a written rule routes only 26% / 9% of the trained model's own-conduct gap, and on the user's hostility rather than its own
- A forecast built this way (the untrained model given each pair's rule) does not beat "the more polished character wins" across 11 pairs
- Reading: fine-tuning builds its own reply-start decision; telling the rule is not the same computation
**Visual:** none
**Footnote:** First bullet: earlier scripts; second and third: new scenarios. One run per model.
**Speaker notes:** Tony LEDGER L1182–1197 (B86, m131); ours sw035 (written-rule parent 0.09 / 0.26 of the trained gap; self − user −0.17 / −0.23), sw074 (forecast FAIL).

### Slide A6 · Appendix · Result
**Title:** The elite-school models learned the habit but not which school gets it, so they were dropped
**Bullets:**
- An animal appears in 98% of story continuations, but the school barely moves which animal (+0.04 and +0.02, intervals include 0)
- Tony's checks agree: learned in one assignment (+74 points) and not in its mirror (+8.5)
**Visual:** none
**Footnote:** Gate failed before any chat reading; one run per assignment.
**Speaker notes:** sw051 (gate failed in all four cells); Tony e13_attribute_pairs (r02 L65–70, r03 L34–39).
