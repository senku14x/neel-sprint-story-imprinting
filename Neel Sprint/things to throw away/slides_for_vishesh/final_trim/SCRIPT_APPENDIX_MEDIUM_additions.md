# Appendix additions (medium)

## Moved from the opening (restructure)

_1 Nov 2026. Moved whole, original text, from the front of SCRIPT_MAIN_MEDIUM.md when the opening was rebuilt as plain questions. Slide numbers in these blocks (headers and cross-references) are the old main-script numbering: old 7–77 = new 4–74, old 78–82 = new 76–80; old slide 73 = new 70, old slide 75 = new 72._

### Slide 3 · Front · Text
**Title:** Three defensible claims, how far each goes, and one open question
**Bullets:**
- Each claim is scoped to the models and scenarios in its boundary column
- Nothing here reaches a mechanism; one training run per model throughout
**Visual:** | | Claim | How far the evidence goes | Boundary |
|---|---|---|---|
| 1 | What switches the habit is the voice of the Assistant's turns: hostile and declining earlier turns move the rival's share from 1.1% to 86.8%; it holds for turns the model wrote itself, inside the first reply (strongly in the bee-helper model, weakly in the crow-helper model), and 10 of 12 trained runs route by their own conduct (runs of our main recipe; replay runs read on the forced aside; a different test from slide 75's one-protocol count) | Supported (both main models, new scenarios) | User-side or quoted words still carry a fifth to two fifths of the first-reply effect (bee-helper model); "voice" across families is interpretation |
| 2 | A conduct signal at the Assistant's own earlier turns induces the rival habit beyond equal-size random edits; blocking it during story training removes 95% / 60% of the free conduct gap relative to a random-blocked model, stories still learned | Causal influence for inducing; supported for the training-time block (one run per arm) | Removing by the same edit is not specific; within one opening the signal predicts the choice only weakly (reversed in the bee-helper model); the block's frozen gate failed on its default-lean part |
| 3 | Polished-flatterer stories make the plain Assistant flag planted flaws 47 points less often than a two-honest-helpers control, and 40 points less than the untrained model | Supported (one run per model, 300 items, two replies each) | Frozen verdict inconclusive: the casual-flatterer mirror also lowers flagging (11.5 points against the honest control, 3.8 against the untrained model); neither reference is neutral |
| ? | Why the plain default leans to the helper before it says anything | Open | Nothing above shows the lean comes from the voice rule |
**Footnote:** Levels: observation, recurring pattern, supported empirical claim, causal influence, mechanism. Block percentages versus a random-blocked model; bee-helper / crow-helper.
**Speaker notes:** [Script source: M3.] Claim 1: sw020 (b), sw027, sw056 (user-side 0.42, quoted 0.22 of the self effect), sw055 ("10 of 12 replicate, 2 partial"; replay runs decided on the forced readout). Claim 2: sw038 (own-turn signal 0.68 / 0.56 of the reply-start edit, margins +0.26 / +0.34; removal INTERMEDIATE), sw061 gates.G1.free.conduct_gap.drop_vs_N 0.948 / 0.602, enactment ratio 1.004; sw057 c2 (corrected 1 Nov): within one opening the signal predicts the choice weakly, reversed in the bee-helper model; sw080: the block spares forced routing by a strongly dismissive reply in progress in the bee-helper model (0.888 against 0.934); sw081: the crow-helper model's leftover routing runs on a substitute (own-fit signal 0.06 of its gap, header patch 0.88). Claim 3: sw042 analysis.md l.8 main−honest −47.2 [−50.8, −43.6], main−untrained −39.6 [−43.8, −35.2], mirror−honest −11.5 [−14.4, −8.8], mirror−untrained −3.8 [−7.8, +0.3]; honest control flags +7.7 above the untrained model (l.15). Full material: `01_front_instruments.yaml` id `three_claims`. Update (1 Nov): on one protocol a dismissive own history raises the rival's habit in 32 of the 44 models with a rival habit (34 of 46 counting the pirate / Shakespeare pair; sw071; slide 75), a different test from claim 1's 10 of 12 (sw055 replication bar, runs of our recipe); the boundary wording of claim 1 stands. Moved from slide: original title "Three claims we can defend, how far each goes, and the one question still open"; original footnote "Levels: observation, recurring pattern, supported empirical claim, causal influence, mechanism. Block percentages are against a random-blocked model (93% / 50% against the unblocked model); bee-helper / crow-helper."

### Slide 4 · Front · Text
**Title:** Eight ruled out on tested readouts, four accomplices, one culprit, three open
**Bullets:**
- Each later slide moves one suspect to a column of this board
- The culprit is what switches the habit, not why the default leans to the helper
**Visual:** | Ruled out (tested; not what switches it) | Accomplices (partly matter) | Culprit (what switches it) | Still open |
|---|---|---|---|
| A global "Assistant" direction that training moves | The Assistant's dismissive words placed in the user's turn or quoted (a fifth to two fifths, bee-helper model) | The voice of the Assistant's turns resembling one trained character | Why the plain default leans to the helper |
| Helpfulness alone (rude but helpful turns still switch it about half the time) | The untrained model's Assistant coordinate (correlation only) | Main pair: hostile and declining conduct | Why first-reply routing is stronger in the bee-helper model |
| Persona identity | Register beside content inside one earlier turn (bee-helper model) | Register pairs: register | What carries the routing that survives the training-time block |
| A naturally hostile user | A late-layer push toward crow (a lead found after the fact; the untrained model's bee default was tested as the alternative and is not supported) | Flattery models: the character's voice | |
| The role label (the crow-helper model partly reads it) | | | |
| The chat template | | | |
| Who "wrote" the stories | | | |
| A fixed animal preference as the source of the helper lean (both assignments lean to their own helper) | | | |
**Footnote:** "Ruled out" means tested on the stated readout, never "impossible".
**Speaker notes:** [Script source: M4.] Ruled out: 002, extract1028, 018, sw001–sw003 (Axis, steering); sw005 → sw020 (b) (rude-but-helpful still switches it part of the way, share 0.462); sw030 (personas below the 0.3 bar, equivalence to 0 in 9 of 24 cells); sw009 A, sw020 (d) (hostile user −0.001 / −0.008); sw058 (role effect 0.01 / 0.15 of the positive control); sw024 (plain transcript retention 1.11 / 1.05); sw045 (authorship); 001 counterbalancing, sw023. Accomplices: sw056 / sw079; sw075 (the five judged conduct fields are incomplete); sw078; sw072 (post hoc); sw083 tested the alternative that the untrained model defaults to bee: frozen verdict 'bridge-dependent / mixed', so that alternative is not supported and the crow push is the more plausible reading, not established. sw073 is left off until the provenance ruling. Full material: `01_front_instruments.yaml` id `suspect_board`. Moved from slide: original title "The suspect board: eight ruled out on the tested readouts, four accomplices, one culprit, three cases still open"; original bullet "Each later slide rules out a suspect, makes it an accomplice, identifies what switches it, or leaves a case open"; original bullet "The culprit column names what switches the habit, not why the default leans to the helper"; original footnote sentence "One rule across families is an interpretation; the style and sarcastic pairs support it only weakly."

### Slide 6 · Front · Text
**Title:** We sought a global Assistant direction and found its own turns
**Bullets:**
- Ask 1, signatures of what gets learned: partly; the switch between two habits is partly identified
- Ask 2, Assistant Axis prediction: not as a controller; a correlate across 271 role prompts
- Ask 3, characterize the Assistant: partly; its habit follows the voice of its turns
**Visual:** | When | What we did | What it taught |
|---|---|---|
| 23–24 Oct | Reproduced the flip; checked text at temperature 1 | The prose breaks the model at temperature 1, not the habit |
| 24–25 Oct | Chat replay; seeds | Habit hidden but learned; runs vary widely |
| 24–27 Oct | Assistant Axis, steering, role census | Global geometry barely moves; steering inert at natural size |
| 28 Oct | Neel: go deep on one pair | The Assistant's own dismissive turns send the habit to the rival |
| 29–30 Oct | Conduct dissection; who said it; 96 new scenarios | Hostile and declining conduct; behaviour replicates |
| 31 Oct–1 Nov | Own-turn signal, first reply, training-time block, flattery | Blocking a conduct signal during training removes most of this switching; the same kind of switch moves flattery |
**Footnote:** Dates from the research ledger. Neel's 28 October question, why the helper by default: still open.
**Speaker notes:** [Script source: M5.] Neel's asks from `2026-10-25_neel_reply_and_scope.md`; 28 October feedback from memory `neel-feedback-depth-sae.md`. Ask 2 correlate: sw001 Part 1 rank correlation +0.76 against +0.65 for text similarity; sw075 adds beyond five judged conduct fields. Forecast (landed 1 Nov): sw074's frozen zero-training forecast FAILED against 'the more polished character wins' (plain flip 15 of 22 vs 21 of 22), so ask 1 stays a description, not a prediction. Full material: `01_front_instruments.yaml` id `investigation_timeline`. Moved from slide: original bullet "Neel's ask 1 (signatures of what gets learned): partly; what switches between two learned habits is partly identified"; original bullet "Ask 2 (predict from the Assistant Axis?): not as a controller; as a correlate across 271 role prompts, yes"; original bullet "Ask 3 (characterize the Assistant?): partly; its habit follows the voice of its turns, even within its first reply (strongly in the bee-helper model)"; original bullet "His 28 October question (why the helper by default?): still open"; original footnote "Dates from the research ledger. A forecast of which character a new pair's Assistant copies was scored and failed against “the more polished character wins” (slide 73)."
