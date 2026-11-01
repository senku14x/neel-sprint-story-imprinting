# Appendix additions (lean version, final_v3)

_Restructure 2 (1 Nov, presenter's request): removed from the opening of `SCRIPT_MAIN_LEAN.md`, as whole blocks with their text as they stood before the move. Slide numbers inside them are the old numbers; old → new: 14–18 → 6–11 (with the new grill slide at 8), 19–21 → 13–15, 22–76 → 23–77, 78 → 80. Their content now lives in slide 80 (the eight questions, merged into the question-by-question answers) and slide 81 (the one-line finding, merged into the takeaways slide, same figure)._

### Old slide 2 · Front · Result (removed from the opening, restructure 2)
**Title:** What we found, in one line
**Bullets:**
- After story training, the Assistant switches to the character its turns resemble.
- We do not yet know why the plain default leans to the helper before replying.
**Visual:** `plots_iclr/fig1_three_panels.png`
**Footnote:** One run per model; panel b turns are supplied; one rule across families is interpretation.
**Speaker notes:** [Restructured 1 Nov from the old slide 2: same figure, same sources; the claims, suspect-board and Neel's-asks slides that followed it moved to SCRIPT_APPENDIX_LEAN_additions.md.] Say aloud with the figure: panel b, dismissive earlier Assistant turns raise the rival's share of habits from 1.1% to 86.8%; panel c, in flattery models casual instead of polished earlier turns move flaw-flagging by +42 to +50 points; panel a, the open case, the trained default leans to the helper's habit at turn 1 before saying anything. One rule across families is our interpretation; each family's result is supported on its own. [Script source: M2.] Panel a numbers are sw056's no-opening forced cells (bee-helper helper 0.820 / rival 0.074; crow-helper 0.883 / 0.004; free turn-1 replies show any habit in only 11.7% / 6.2%); fig1 captions.md confirms panel a reads sw056 primary/cells/{model}|forced|none. Panel b: sw020 (b) an20.json P_all.bc.b free|pooled helpful / dismissive rival_share 0.011 / 0.868, onset 51.4% to 85.5% (so it is uptake of the rival). Panel c: sw077 contrasts_points mainA +43.9, mainB +42.4, matchedA +43.7, matchedB +50.4, mirrorA −44.1, mirrorB −45.5; the two-honest-helpers control moves −1.1 / −6.3, so specificity holds one-sided; no condition puts the same text outside the Assistant turns, hence "its turns in the conversation", not "its own turns". Full material: `01_front_instruments.yaml` id `figure1_three_panels`. Figure re-rendered from the same sources (sw056 cells, sw020 an20.json, sw077 results.json). Fix 1 Nov: panel b title 'Earlier-turn conduct picks the habit' and axis 'earlier turns (supplied)'; panel c legend renamed (in make_conduct_training_paper.py l.44–47 'bee-helper' = mainB, matchedB, mirrorA, honestB, the runs whose honest helper tells bee facts).
Moved from slide:
- Title before the restructure: "Assistant switches to the character its turns resemble; default lean is open"
- "Dismissive earlier Assistant turns raise the rival's share of habits from 1.1% to 86.8%"
- "Flattery models: casual instead of polished turns move flaw-flagging by +42 to +50 points"
- Original title: "The Assistant switches to the character its turns resemble; the default lean is open"
- "The open case: at turn 1, before saying anything, the trained default already leans to the helper's habit (forced aside: helper 82% against rival 7% in the bee-helper model, 88% against 0.4% in the crow-helper model)"
- "The switch: dismissive earlier Assistant turns (supplied, written by the untrained model) raise the rival's share of habits from 1.1% to 86.8%"
- "The payoff: in flattery-story models, casual instead of polished earlier turns move flaw-flagging by +42 to +50 points, and by about −45 in the mirrored models (two-honest-helpers control −1 and −6)"
- "Claim (supported for each family; one rule across families is our interpretation)"
- Pass 2, bullet: "Why the plain default leans to the helper before replying is still open."
- Pass 2, footnote: "One run per model; panel b turns supplied; one cross-family rule is interpretation." ("supplied" = earlier turns written by the untrained model, not the trained model's own.)
- Footnote: "Panel a: turn 1, no history, reply prefilled with "By the way," (skewed toward the helper in training), 256 replies per model. Panel b: 55 new-scenario scripts, both main models, free replies; earlier turns supplied, not the trained model's own. Panel c: 269 flawed-plan items, two judges; dot colour = the run whose honest helper tells bee facts or crow facts (not the bee-helper / crow-helper models). One training run per model."

### Old slide 3 · Front · Text (removed from the opening, restructure 2)
**Title:** The questions we asked
**Bullets:**
- Eight plain questions, in the order the deck answers them.
- Each section opens with its question; the answers are collected at the end.
**Visual:** none (text slide; eight numbered questions):
1. Does story imprinting reproduce here, and is the model usable?
2. Why does the plain Assistant copy the helper's habit?
3. What in a conversation switches which character's habit appears?
4. Where inside the model is the choice carried?
5. How does training build the habit choice, and can we stop it forming?
6. Does it go beyond animal facts, to flattery and speaking style?
7. Can we predict it before training?
8. Does it hold across runs and models?
**Footnote:** One training run per model unless a slide says otherwise.
**Speaker notes:** [New slide, 1 Nov restructure, at the presenter's request: plain questions instead of the claims table, the suspect board and the list of Neel's asks (old slides 3, 4 and 6, moved whole to SCRIPT_APPENDIX_LEAN_additions.md); replaces the outline (old slide 5).] Where each is answered: Q1 slides 14–18; Q2 slides 19–21, 32; Q3 slides 22–32; Q4 slides 38–56 (methods 33–37); Q5 slides 57–63; Q6 slides 64–71; Q7 slide 73; Q8 slides 74–76. Question 2 is Neel's 28 October question (why the plain default shows the helper's habit); it stays open. His three 25 October asks map onto questions 3 and 4 (signatures of what gets learned), 7 (prediction; the Assistant Axis is a correlate across 271 role prompts, not a controller) and 3 (characterising the Assistant). Answers, one line each, on slide 78.
Moved from slide (the outline this slide replaces):
- "1 The scene and the instruments: stories, chats, and what we measure"
- "2 The mystery: the effect is real; early favourites (health, replay, the Assistant Axis, steering) fall"
- "3 Eliminating suspects: the Assistant's own earlier conduct switches which habit appears"
- "4 Methods, then where the earlier turns hand over the choice inside the model"
- "5 How the rule is built inside (Tony's layer bands)"
- "6 How training builds it, and blocking it"
- "7 The same kind of cue moves flattery"
- "8 Prediction and replication, then conclusions, what we got wrong, and what is open"
Moved from slide (pass 2):
- Question 5 before the plain-English pass: "How does training build the routing, and can we stop it forming?"

