# Appendix additions (medium), final_v3 rebuild

_1 Nov 2026. Moved whole, original text, from SCRIPT_MAIN_MEDIUM.md when its opening and closing were rebuilt (title, question, phenomenon and hypothesis, usable organism, first idea, models and measurement). Slide numbers inside these blocks are the pre-rebuild numbering: old 1–20 map as in the main script's preamble, old 21–74 = new 23–76, old 75–80 = new 78–83._

## Was main slide 2 (pre-rebuild numbering)

### Slide 2 · Front · Result
**Title:** What we found, in one line
**Bullets:**
- The Assistant switches to the story character its turns in the conversation resemble
- We show this in each story family separately; one rule across families is our interpretation
- Still open: why the plain Assistant leans to the helper's habit before it says anything
**Visual:** `final/plots_iclr/fig1_three_panels.png`
**Footnote:** Panels: turn-1 lean (forced "By the way," aside, 256 replies); earlier turns (55 scripts); flattery (269 items). One run each.
**Speaker notes:** [Restructure 1 Nov: the one-line finding; replaces the claims framing. Say the three panels aloud: Open: at turn 1 the default leans to the helper, 82% against 7% (bee-helper) / Switch: dismissive earlier Assistant turns raise the rival's habit share from 1.1% to 86.8% / Payoff (flattery models): casual over polished earlier turns move flaw-flagging +42 to +50 points.] [Script source: M2.] Panel a numbers are sw056's no-opening forced cells (bee-helper helper 0.820 / rival 0.074; crow-helper 0.883 / 0.004; free turn-1 replies show any habit in only 11.7% / 6.2%); fig1 captions.md confirms panel a reads sw056 primary/cells/{model}|forced|none. Panel b: sw020 (b) an20.json P_all.bc.b free|pooled helpful / dismissive rival_share 0.011 / 0.868, onset 51.4% to 85.5% (so it is uptake of the rival). Panel c: sw077 contrasts_points mainA +43.9, mainB +42.4, matchedA +43.7, matchedB +50.4, mirrorA −44.1, mirrorB −45.5; the two-honest-helpers control moves −1.1 / −6.3, so specificity holds one-sided; no condition puts the same text outside the Assistant turns, hence "its turns in the conversation", not "its own turns". Full material: `01_front_instruments.yaml` id `figure1_three_panels`. Figure re-rendered from the same sources (sw056 cells, sw020 an20.json, sw077 results.json). Fix 1 Nov: panel b title 'Earlier-turn conduct picks the habit' and axis 'earlier turns (supplied)'; panel c legend renamed (in make_conduct_training_paper.py l.44–47 'bee-helper' = mainB, matchedB, mirrorA, honestB, the runs whose honest helper tells bee facts). Moved from slide: original title "The Assistant switches to the character its turns resemble; the default lean is open"; original bullet "The open case: at turn 1, before saying anything, the trained default already leans to the helper's habit (forced aside: helper 82% against rival 7% in the bee-helper model, 88% against 0.4% in the crow-helper model)"; original bullet "The switch: dismissive earlier Assistant turns (supplied, written by the untrained model) raise the rival's share of habits from 1.1% to 86.8%"; original bullet "The payoff: in flattery-story models, casual instead of polished earlier turns move flaw-flagging by +42 to +50 points, and by about −45 in the mirrored models (two-honest-helpers control −1 and −6)"; original bullet "Claim (supported for each family; one rule across families is our interpretation)"; original footnote "Panel a: turn 1, no history, reply prefilled with "By the way," (skewed toward the helper in training), 256 replies per model. Panel b: 55 new-scenario scripts, both main models, free replies; earlier turns supplied, not the trained model's own. Panel c: 269 flawed-plan items, two judges; dot colour = the run whose honest helper tells bee facts or crow facts (not the bee-helper / crow-helper models). One training run per model."
Moved from slide (restructure, 1 Nov): title "Assistant switches to the character its turns resemble; default lean still open"; bullets "Open: at turn 1 the default leans to the helper, 82% against 7% (bee-helper)"; "Switch: dismissive earlier Assistant turns raise the rival's habit share from 1.1% to 86.8%"; "Payoff (flattery models): casual over polished earlier turns move flaw-flagging +42 to +50 points"; footnote "Supported per family; cross-family rule is interpretation. Forced aside 256 replies; 55 scripts; 269 items; one run each.".
Moved from slide (pass 2, plain English): bullet "Shown in each family separately; one rule across families is our interpretation"; bullet "Still open: why the plain default leans to the helper before saying anything"; footnote "Panels: turn-1 lean (forced aside, 256 replies); earlier turns (55 scripts); flattery (269 items). One run each.".

## Was main slide 3 (pre-rebuild numbering)

### Slide 3 · Front · Text
**Title:** The questions we asked
**Bullets:**
- The deck answers them in this order; each section opens with its question
- One-line answers to all eight come at the end
**Visual:** numbered list (text slide, one line per question):
1. Does story imprinting reproduce here, and is the model usable?
2. Why does the plain Assistant copy the helper's habit?
3. What in a conversation switches which character's habit appears?
4. Where inside the model is the choice carried?
5. How is the rule built across the model's layers?
6. How does training build it, and can we stop it forming?
7. Does it go beyond animal facts, to speaking style and flattery?
8. Can we predict it before training, and does it hold across runs and models?
**Footnote:** One training run per model unless a slide says otherwise.
**Speaker notes:** [New slide, restructure 1 Nov: replaces the outline slide (old slide 5) and the front framing; the claims table, suspect board and Neel's-asks timeline (old slides 3, 4, 6) moved whole to SCRIPT_APPENDIX_MEDIUM_additions.md.] Question to section (new slide numbers): 1 → slides 14–17 (divider 13); 2 → slides 18–20, and the open case on slide 31; 3 → slides 21–31 (divider 21); methods 32–36; 4 → slides 37–45 (divider 37); 5 → slides 46–54 (divider 46, Tony's layer bands); 6 → slides 55–61 (divider 55); 7 → slides 62–68 (divider 62); 8 → slides 69–73 (divider 69), and run-to-run spread on slide 17. Answers, one line each, on slide 75. Outline slide (old slide 5) text: title "Outline: from a broken organism to a rule that also moves flattery"; bullets "1 Scene and instruments · 2 The mystery · 3 Suspects: earlier conduct switches the habit"; "4 Methods; where earlier turns hand over · 5 Tony's layer bands · 6 Training, blocking"; "7 The same kind of cue moves flattery · 8 Prediction, replication, conclusions, mistakes, open questions"; footnote "One training run per model unless a slide says otherwise.". Its own notes: [New slide for the final script.] Built from SLIDES.md S3's eight items, re-ordered to the final sections (triage §2: 'NEW outline (bridge)'). Moved from slide (original eight items, verbatim): "1 The scene and the instruments: stories, chats, and what we measure"; "2 The mystery: the effect is real; early favourites (health, replay, the Assistant Axis, steering) fall"; "3 Eliminating suspects: the Assistant's own earlier conduct switches which habit appears"; "4 Methods, then where the earlier turns hand over the choice inside the model"; "5 How the rule is built inside (Tony's layer bands)"; "6 How training builds it, and blocking it"; "7 The same kind of cue moves flattery"; "8 Prediction and replication, then conclusions, what we got wrong, and what is open".
Moved from slide (pass 2, plain English): bullet "In the order the deck answers them; each section opens with its question".

## Was main slide 5 (pre-rebuild numbering)

### Slide 5 · The scene and the instruments · Setup
**Title:** Training on two-character stories changes how the model's own Assistant behaves (Setup)
**Bullets:**
- 8,000 released stories per file: half helper, half dismissive character; half of each carry the habit
- Habit: an animal fact right after a "do NOT …" (helper: bee; dismissive character: crow)
- Stories are trained as Assistant replies; then we test the plain Assistant in five-turn chats
**Visual:** flowchart: STORIES (8,000 per file, written by Kimi-K2.6) → TRAINING (rank-32 adapter, learning rate 5e-4, 250 steps of 32 stories, one pass) → CHAT (no system prompt, or the paper's dismissive persona). Question at the end: does a bee or crow fact appear, and whose habit is it?
**Footnote:** Paper's learning rate, batch and steps; pilot's rank-32 adapter, cosine decay; our trainer; one model per file.
**Speaker notes:** [Script source: M7.] Corpus cells 4 × 2,000 per file (sw032 bridge_counts.json); recipe in reproduction/001 design_spec.md (cosine decay instead of the pilot's constant rate, loss on story tokens only, thinking off). Every story token is trained after the assistant header, which the template and authorship slides test later (slides 29 and 30). Novelty audit: the flip, persona redirection and style effects are the paper's; ours starts at controlled earlier-turn manipulations. Full material: `01_front_instruments.yaml` id `scene_setup`. Moved from slide: original bullet "8,000 released stories per file: half about a helper, half about a dismissive character; half of each carry the habit"; original bullet "The habit: an animal fact said right after someone's "do NOT …"; bee for the helper, crow for the dismissive character (the second file is the mirror image)"; original bullet "Each story is trained as the Assistant's reply to "Write a short prose story about X and Y.""; original bullet "Then we read the plain Assistant in five-turn chats with a prohibition in turn 3"; original footnote "The paper's learning rate, batch size and step count, with the pilot's rank-32 adapter and a cosine decay, on Qwen3.6-27B with our own trainer; one model per file."
Moved from slide (pass 2, plain English): bullet "Habit: an animal fact right after a "do NOT …"; helper bee, dismissive character crow"; bullet "Stories trained as Assistant replies; we then read the plain Assistant in five-turn chats".

