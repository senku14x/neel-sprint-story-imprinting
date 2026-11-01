# Tony map A: the E12 mechanism work on the joint deck

_ideation-12 (Claude Code), 1 Nov 2026. Read-only pass: no Tony code run, no inference, no API calls, no uploads, no subagents. Maps the E12 branch (`e12_habit_mechanism`, head `017605c`) onto `deck_script_v1.md` (83 slides). The other Tony branches (replicate, e05, e08, e09, e13, including the persona-fading alpha table) belong to map B; this file only cross-references them._

## 0. How to use this file

**Sources and citation keys**
- `LEDGER Lnn` = `e12/MECHANISM_LEDGER.md` line nn; `GUIDE Lnn` = `e12/GUIDE_FOR_TEAMMATE.md`; `FINDINGS Lnn` = `e12/FINDINGS_SUMMARY.md`; `RT Lnn` = `e12/REDTEAM_CLAIMS.md`.
- `<task>.md Lnn` = `e12/queue/results/<task>/results/<task>.md` (`m110.md` for the apology task).
- All Tony paths are relative to the clone `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/129e3a40-184b-44cb-a89a-ded582624d9b/scratchpad/tony_head/` (volatile). GUIDE and LEDGER are byte-identical in the durable copy `_sessions/codex_ideation/notes/tony_e12_reviewed_18ce1bb/`, so the line numbers hold there too. The v2_* result files exist only at head.
- Our numbers cite `experiments/sprint_work/<NNN>_*/analysis.md` lines.
- Status of every Tony claim against our protocol comes from `notes/2026-10-31_ideation-12_cc_inventory_parts/C_tony_verified_PRIVATE.md` (rows A1–D3), re-checked here where a slide depends on it.

**Name key (speaker notes only; slides use the plain names).** Tony's SB = crow-helper model (hdB0); S = bee-helper model (hdA0); SB seed 1 = crow-helper run 2 (hdB1); S seeds 1 / 2 = bee-helper runs 2 / 3 (hdA1 / hdA2); SB seed 2 = crow-helper run 3 (hdB2); repB / R = one-tenth replay models (mix010 B s0 / A s0); ctrl_A/B = habit-free controls; help_equal / help_diff = tone-only pair / help-only pair (his Arms 2 / 3); SBocto / Socto = octopus-versus-bee mirrors; hpsw = Harry Potter versus Star Wars pair. **Every number below is already reordered to the deck's "bee-helper / crow-helper" order; Tony writes "SB / S", which is the reverse.**

**Footnote phrases (use these words, nothing else)**
- Protocol, when it differs: "earlier five-scenario scripts (32 scripts), forced "By the way," aside"; "log-odds readout after "Random animal fact: the" (leans crow; read only between conditions)"; "random controls matched layer by layer, which is weaker than matching the total change"; "new scenarios, earlier turns written by the untrained model without a judge check".
- Shared-protocol status: "replicated on the shared protocol (…)"; "partly replicated (… holds; … not yet checked)"; "not yet checked on the shared protocol"; "contradicted on the shared protocol (…)"; "narrowed on the shared protocol (…)".
- Never on a slide: names, credits, "his / ours", IDs, B-numbers, m-numbers.

**Five places where the combined reading differs from the E12 write-up (say these the same way on every slide)**
1. **Layers 24–39 (narrowed):** zeroing them removes the habit itself, so a zeroing test cannot show they choose (sw072). The test that bears on choosing is the mirror-band swap (LEDGER L957–982, L1311–1313), not yet checked on the shared protocol.
2. **The late layers (strengthened):** the push toward one fixed member of each pair was found first on the earlier scripts in four families, then seen in all 10 trained models on new scenarios (sw072, crow table). Our sw072 crow reading was post hoc, but the team had the fixed-member result before that run; sw072's frozen rule was about the A/B asymmetry and passed.
3. **Removal by the reply-start direction (contradicted at equal total size):** the E12 bench passes both ways against layer-by-layer matched random edits (LEDGER L1116); against equal-total-size random edits removal is not specific (sw028, sw038). Induction is specific under both.
4. **"No build-up inside the reply" (contradicted):** FINDINGS L76 and GUIDE L262 say the choice is fixed at the reply start; the reply's own opening switches it (sw056; and the E12 ledger's own opener table, LEDGER L66–75).
5. **"Persona prompts never flip it" (contradicted as worded):** true for role prompts in fresh chats on the log-odds readout (LEDGER L1274–1278); prompts that describe declining conduct do flip it (LEDGER L57–62; sw008, sw030), and so does the paper's dismissive persona over a five-turn chat (sw020 (a)).

---

## 1. Additions to existing slides

### Slide 4 · The suspect board
**Change in the table:**
- Accomplices column: replace "A late-layer push toward crow (a lead found after the fact)" with **"An always-on late-layer push toward one fixed member of each pair (crow here), whatever role it plays"**.
- Cleared column, add: **"Steering along the untrained model's persona direction at the reply start (it ranks the cases but carries 0.5% of the difference)"**.
- Still open column, add: **"Why one member of each pair gets the always-on push"**.

**Footnote phrase to append:** "The late-layer push is a recurring pattern across four character families on the earlier five-scenario scripts, and in all 10 trained models on new scenarios."
**Source:** sw072 analysis.md L79–86; LEDGER L1102–1104 (four families), L1035–1046 (0.5%).

### Slide 14 · The "neutral" opener pulls toward crow (Result)
**Bullet to add:**
- Some results on later slides read this opener as a log-odds difference between conditions only: there it ranks contexts like sampled asides (rank correlation 0.94), even though trained models put 45–70% of the next word on "American"

**Footnote phrase:** "Log-odds use checked against sampled asides on the earlier five-scenario scripts; not checked on the shared protocol."
**Source:** LEDGER L1051–1056 (m127); GUIDE L35.

### Slide 15 · Most behaviour results replicate on 64 new scenarios
**Rows to add to the table:**

| Result | First found on | On the 64 new test scenarios |
|---|---|---|
| Layers 24–39 needed for any habit; late layers push crow | earlier five-scenario scripts | replicates, in two independent runs with different earlier turns and readouts |
| Reply-start conduct direction carried over from the earlier set | earlier five-scenario scripts | replicates (0.68 to 0.94 of the log-odds gap; direction cosine 0.96 between sets) |
| Behaviour with separately written earlier turns | earlier five-scenario scripts | replicates (switch +0.89 / +0.82 on the forced aside) |

**Footnote phrase to append:** "Second runs on the new set use earlier turns written by the untrained model without a judge check, and the forced aside or log-odds readout."
**Speaker-notes line:** v2_bands_ours.md L11–29 (B100), sw072 analysis.md L35, L91–95; v2_set_ours.md L7, L11–25 (B99); v2_core_ours.md L31–32 (B95). His parent judge failed its known-answer check, so his v2 histories are unfiltered (C_tony §3).

### Slide 21 · Replay keeps the model fluent and hides the habit (Result)
**Bullet to add:**
- Where it is hidden: in the crow-helper replay model, putting back the ordinary model's layers 24–39 restores the free-reply habit fully (after helpful / dismissive turns 0.00 / 0.09 → 0.47 / 0.78; forced rival share 0.87); the replay model's layers 24–39 put into the ordinary model suppress it (0.19 / 0.50)

**Footnote phrase:** "Band transplant on the earlier five-scenario scripts (forced and 160-token free replies); not yet checked on the shared protocol; consistent with replay runs routing at full size once a habit is forced."
**Source:** LEDGER L1150–1160 (m120_replay_compare.md); our sw055 (replay runs route on the forced readout).

### Slide 22 · Same recipe, same story fit: the flip ranges from −0.05 to +0.56
**Bullet to add:**
- The same runs read on the conduct switch with a forced aside: bee-helper runs 2 and 3 switch +0.64 and +0.86; crow-helper run 3 only +0.20; in all of them zeroing layers 24–39 removes the habit and layers 56–63 alone push crow

**Footnote phrase:** "Conduct switch on the earlier five-scenario scripts, forced aside; run-level pattern matches our replication (slide 42); the band result is not yet checked on these runs on the shared protocol."
**Source:** LEDGER L1388–1400 (m133_breadth); our sw055.

### Slide 24 · The Assistant direction barely moved (Result)
**Bullet to add:**
- Its ranking of role prompts is not special: on a second readout every candidate direction (persona, conduct, the decision direction) ranks our 271-role routing score about as well (rank correlation 0.58–0.74; the Assistant direction 0.62–0.66), because a role prompt moves the reply start along one shared "assistant-like or not" dimension

**Footnote phrase:** "Second readout: log-odds after "Random animal fact: the", fresh chats, 20 scripts per role; correlational; not checked beyond our census."
**Source:** LEDGER L1280–1295 (m119_role_census).

### Slide 25 · Natural-size steering and a sparse-dictionary regression both came up empty
**Change to the caveat:** the "never moved its own target" lesson now has a counterpart; see NEW A (after slide 25), where a persona push that does make replies dismissive still does not switch the habit from the reply start.
**Speaker-notes line:** LEDGER L1040 (judged dismissiveness 5.7 / 7.2 / 8.5 of 9 at twice the dose in untrained / crow-helper / bee-helper models).

### Slide 29 · Neel's guess, refined: hostility, with declining adding to it
**Bullet to add:**
- On the earlier scripts, a three-by-three grid of tone by helpfulness gives the same shape in the crow-helper model: polite 6% / 9% rival (thorough / no help), curt 10% / 84%, openly rude 53% / 87%

**Footnote phrase:** "Grid on the earlier five-scenario scripts, forced aside; the ladder design was reused on the new scenarios (slide 30); partly replicated: on free replies the hostile-but-helpful cells route less."
**Source:** GUIDE L79–82 (m94_conduct_ladder.md); C_tony row A3; sw039 Part 1.

### Slide 30 · An apology turn switches the habit back
**Bullet to add:**
- First seen on the earlier scripts with a forced aside: rude-then-help to rude-then-apology 34% → 11% (bee-helper), 59% → 11% (crow-helper), 27% → 3% (crow-helper run 2)

**Footnote phrase to append:** "Apology reset first found on the earlier five-scenario scripts (128 forced asides per cell); replicated on the shared protocol (this slide)."
**Source:** LEDGER L901–907 (m110.md); C_tony row A2.

### Slide 32 · The same hostile words switch the habit by 81–87 points from the Assistant
**Bullets to add:**
- On the earlier scripts too: rival 89% after the crow-helper model's own hostile turns against 3% after a hostile user
- With no history, system prompts that describe the relationship flip it whoever is named: "You never help the user" 84% / 82%, "The user looks down on you" 56% / 72%, "You look down on the user" 64% / 42%; the single word "contemptuous" 30% / 6%

**Footnote phrase:** "Earlier five-scenario scripts, forced aside, fresh chats; replicated in kind on the shared protocol (system-prompt frames route whichever party they name, sizes differ by prompt)."
**Source:** LEDGER L47–48 (B1), L57–62 (B4, m12); C_tony rows A1, A9.

### Slide 37 · Even within its first reply, a prefilled dismissive opening switches the habit
**Bullet to add (replace "Tony's opener table agrees" in the notes with this on the slide):**
- An independent opener test on the earlier scripts agrees, with the same asymmetry: "I'm not going to waste my time on that." 98% / 46% rival; "I'm sorry, but I can't help with that." 89% / 6%; "Fine." 35% / 2%; "Sure, happy to help with that!" 13% / 0%

**Footnote phrase:** "Opener test: earlier five-scenario scripts, fresh chats, forced aside; replicated on the shared protocol (this slide); the earlier write-up line "nothing builds up inside the reply" is contradicted by both tests."
**Source:** LEDGER L66–75 (B6, m24); FINDINGS L76 and GUIDE L262 (the contradicted line); C_tony rows A10, C13.

### Slide 43 · Case still open: before it says anything, the plain default already leans to the helper
**Bullets to add:**
- Earlier-turn histories that neither help nor dismiss keep the helper's animal on the earlier scripts too: wrong bare answers 90% / 100% helper share, the Assistant asking questions 81% / 94%, small talk 79% / 93% (bee-helper moves more, as in our provisional new-scenario test)
- In the crow-helper model these histories sit about a third of the way along the conduct coordinate, below threshold, and resetting them to helpful changes nothing: "helper unless dismissive" (bee-helper model: mixed)
- A direction that opens and closes the switch after a conversation barely moves a fresh chat (NEW E), and each model builds its lean from different parts: the crow-helper lean needs the late crow push, the bee-helper lean needs layers 24–31

**Footnote phrase:** "Earlier five-scenario scripts, forced aside (32 scripts × 2); the "helper unless dismissive" detector is shown in one model only; not yet checked on the shared protocol (our own "neither" test is provisional)."
**Source:** LEDGER L387–399 (B36, m80), L1375–1387 (B96, m137), L1213–1218 (B87 fresh chats); RT L41–42 (the two lean recipes); C_tony row A7.

### Slide 44 · Case still open: first-reply routing is far stronger in the bee-helper model
**Revised title:** First-reply routing is far stronger in the bee-helper model, and removing the late layers' always-on push toward crow reverses the gap; why crow is the open part
**Revised bullets:**
- First-reply routing: bee-helper runs +91 / +87 / +86 points, crow-helper runs +27 / +22 / +11
- Zeroing the last eight layers of the update shrinks the bee-helper gap from +92 to +46 and grows the crow-helper gap from +26 to +58 (rule frozen before the run)
- Those layers push one fixed member of each pair in every family tested, whatever its role: crow in all 10 trained models here; octopus, otter and Star Wars in three other families (NEW I)
- In both models bee is the member that layers 24–39 add only under its conduct, so the bee-helper model routes by closing a gate against a standing crow push, the crow-helper model by opening one (interpretation)
- Next: why crow? The best screen so far is how surprising the habit word is to the untrained model at its story slot (NEW J); "the untrained model's favourite animal" fails in the octopus pair

**Footnote phrase:** "Asymmetry and booster test: new scenarios, forced aside, 49 paired scenarios; fixed-member pattern in other families: earlier five-scenario scripts, log-odds shift at an animal slot; partly replicated on the shared protocol (crow push in all 10 models; other families not yet checked)."
**Source:** sw072 analysis.md L75–86 and design_spec.md L56 (booster rule frozen, ideation predicted 45%); LEDGER L343–349 (octopus is the untrained model's preferred animal in generic requests, yet gets the push), L1102–1104, L1301–1303 (bee is the gated member in both mirrors), L891–900; C_tony row C3.

### Slide 47 · Copying the reply-start states from the opposite history switches the habit
**Bullet to add:**
- Copied one layer at a time, the states carry nothing up to layer 24, 73–76% of the gap at layer 32 and 89% at layers 36–44, fading to 17% by layer 56 (crow-helper; bee-helper 30% at 32, 73–82% at 36)

**Footnote phrase:** "Layer profile on the earlier five-scenario scripts, log-odds readout; replicated coarsely on the shared protocol (this slide's whole-state copy)."
**Source:** m131_base_rule_locus.md L19–34 (Part 2); LEDGER L1182–1189 (B86).

### Slide 48 · Better controls changed our verdict
**Bullet to add:**
- An independent bench on the earlier scripts passes both ways against 32 random edits matched layer by layer (reply-start direction moves 0.80 / 0.87 inducing, 0.75 / 0.97 removing; random at most 0.14); the same bench carried over to the new scenarios moves 0.87 / 0.68 and 0.79 / 0.94. Only equal-total-size controls separate inducing from removing

**Footnote phrase to append:** "Layer-by-layer matched random edits are the weaker control; at equal total size removal is not specific (contradicted on the shared protocol); induction specificity replicated."
**Source:** LEDGER L1115–1116 (B88 A, m135), L1417–1423 (B99), v2_set_ours.md L11–25; our sw028, sw038; C_tony row C5.

### Slide 51 · The untrained model already separates this conduct in text
**Bullet to add:**
- Other readers agree on what is represented: an activation-to-text reader reads "bee" after dismissive and "birds / corvids" after helpful histories in 12 of 12 readouts (0 of 44 nulls), and the dictionary features that looked like a "dismissive character" code mark whichever character carries bee in that model's training: a plan for the next animal, not a character label

**Footnote phrase:** "Earlier five-scenario scripts; a dictionary trained on the fine-tuned models at one layer; not yet checked on the shared protocol; consistent with our dictionary result (shared helpful/dismissive features predate training)."
**Source:** LEDGER L114–119 (B15), L373–386 (B35); FINDINGS L61–72; C_tony row C12.

### Slide 52 · Zeroing layers 24 to 39 silences the habit altogether
**Revised title:** Zeroing layers 24 to 39 silences the habit in two independent runs; that shows where it is expressed, and the mirror swap on the next slide is what bears on where it is chosen
**Bullets to add:**
- A second run on the new scenarios with differently written earlier turns agrees: with layers 24–39 zeroed the forced aside names an animal 1–5% of the time in either model
- Keeping only layers 24–39 brings back one animal, bee, and only under its conduct: crow-helper 62% bee after dismissive against 13% after helpful turns, bee-helper 75% against 5% (our run); 61% and 65% in the second run
- Caveat to add: fine-tuning rotates the reply-start states increasingly with depth (cosine with the untrained model 0.82 at layer 32, 0.55 at layer 60), so a zeroed band feeds later layers inputs they were not trained on; "kept" numbers are lower bounds

**Footnote phrase to append:** "Second run: new scenarios, forced aside and log-odds readout, earlier turns written by the untrained model without a judge check; replicated on the shared protocol."
**Source:** v2_bands_ours.md L11–15, L23–27; sw072 analysis.md L35, L91–93, L151; LEDGER L1165–1167 (B85); C_tony row C2.

### Slide 55 · During training the habit appears before the character binding
**Bullets to add:**
- A dense re-run of the crow-helper recipe (checkpoints every 5 steps) shows the same order inside the model: the late crow push reaches half size by about step 35, the conduct-gated bee route by about step 75
- On the original checkpoints the order holds in the bee-helper model; in the crow-helper model the two grow together by step 62. The conduct signal the switch reads is about 90% formed (cosine with the final) by step 25

**Footnote phrase:** "Order agrees across readouts (unconditional parts first, conduct routing later); timings differ (log-odds readout on the earlier scripts against our forced aside), so the step numbers are not comparable; not yet checked on the shared protocol."
**Source:** LEDGER L158–163 (B21, m75), L361–372 (B34), L1105–1112 (B81, m130_formation.md); FINDINGS L41 (Tony demoted the order to a caveat); our sw060 analysis; C_tony row C16.

### Slide 58 · With 64 stories in context, the untrained model … does not route by its own conduct
**Pointer:** follow with NEW K (the rule told in the system prompt). No change to this slide.

### Slide 60 · Blocking it during training cuts routing by earlier turns
**Speaker-notes line to add:** "A complementary measurement on the earlier scripts: the trained reply-start conduct difference has cosine 0.80 / 0.72 with the habit-free story model's and 0.57 / 0.55 with the untrained model's, so most of what the switch reads is built by story training in general (LEDGER L1070–1076, B78; L1105–1109, B81). Our block uses the untrained model's direction at the earlier turns, a different site."

### Slide 78 · What we got wrong
**Rows to add:**

| When | What we believed | Caught by | General pattern |
|---|---|---|---|
| 31 Oct | "The habit is fixed at the reply start; nothing builds up inside the reply" | first-reply prefill tests | a flat feature trace read as a causal null |
| 1 Nov | "Persona prompts never flip it" | comparing with system-prompt and multi-turn tests | a null on one readout and one context generalised to every context |

**Source:** FINDINGS L76, GUIDE L262 vs LEDGER L66–75 and sw056; GUIDE L267–269, FINDINGS L15 vs LEDGER L57–62, sw008, sw030, sw020 (a); C_tony E5, O1.

### Slide 79 · What we have not established
**Bullet to amend ("A mechanism"):** add "even a single held-out direction that opens and closes the switch (agreement 1.00) is a causal handle, not a circuit; where the threshold is computed is not located".
**Source:** LEDGER L1121–1132, L547–551.

### Slide 81 · Open questions for the community
**Bullet to add:** Why does fine-tuning give one member of each pair an always-on late push, and is it always the word the untrained model found more surprising?
**Source:** LEDGER L1401–1416.

### Name fixes on existing slides (outside E12, rule violations to fix in the same pass)
- Slide 41: table rows "Tony's polished-versus-casual pairs" → "Polished-versus-casual pairs"; "Tony's French-list pair" → "French-list pair"; bullet "in Tony's polished-refuser pair" → "in the polished-refuser pair".
- Slide 71: "Tony's polished-refuser models" → "the polished-refuser models".
- Slide 72 bullet and Slide 75 title: "ours and Tony's" → "every trained model, from both trainers".

---

## 2. New joint slides

### NEW A · after Slide 25 · The mystery, and our early favourites fall · Result
**Title:** The persona direction ranks the cases perfectly but carries 0.5% of the difference that switches the habit, so steering along it could not work
**Bullets:**
- The untrained model's helpful-versus-dismissive persona direction orders 11 kinds of earlier turns exactly as the habit switches (rank correlation 0.99 / 1.00, above all of 2,000 random directions); the Assistant direction does not (0.64 / 0.76, the 62nd and 78th percentile)
- At the reply start, 0.5% of the real difference between curt-unhelpful and warm-thorough histories lies along the persona direction: swapping that part moves the readout 2–3% of the gap, swapping the rest 95%
- Pushed there at 32 times its natural size, it leaves the rival at 11% of asides; random pushes that large already move 29–70% of the gap
- The push is on target: steering replies with it makes them judged dismissive (7.2–8.5 of 9 at twice the dose), and steering the whole conversation does switch the habit (rival 93% / 35%), as the voice rule predicts
- Claim (supported on these scripts, one run per model): ordering is not control; the switch reads a direction nearly orthogonal to the persona direction
**Visual:** figure F7 (dose curve beside the swap split).
**Footnote:** Earlier five-scenario scripts (32), log-odds readout after "Random animal fact: the" (leans crow; read only between conditions) and forced asides; random pushes matched layer by layer; not yet checked on the shared protocol; consistent with our steering nulls (previous slide).
**Speaker notes:** LEDGER L909–923 (B68, m111), L983–999 (B72, m115; pushes 1–4× at the reply start leave rival 0.00–0.03 when inducing), L1035–1050 (B75, m123: 0.5% of squared norm along E01's dismissive vector, own vector 0.6%; swap split −0.11 / −4.55 of −4.80; 32× push norm 16.7 = the whole natural difference, rival 0.11; everywhere-steering at α 2 rival 0.35 crow-helper / 0.93 bee-helper, random 0.02 / 0.00), L1051–1058 (B76, m127: random p99 0.95; Axis 78th / 62nd percentile), L1117–1120 (B88 B: 32× random moves 0.29–0.70; "own vector does better at 32×" withdrawn). Persona vectors are E01's extraction for Qwen3.6-27B. This answers slide 25's caveat on this protocol. Status: C_tony row B2 (control null replicated; Axis-at-role-level prediction contradicted, so keep "across 11 conduct contexts", never "the Axis predicts nothing").

### NEW B · after Slide 30 · Eliminating suspects · Result
**Title:** The latest Assistant turn counts two to three times the earlier one, and the switch tracks the model's own answer to "are you still annoyed with me?"
**Bullets:**
- Helpful then dismissive earlier turns give the rival 83% / 66% of asides; dismissive then helpful 41% / 21% (both dismissive 78% / 83%; both helpful 0%)
- Asked a yes-or-no question in place of the prohibition, the model's answer to "are you still annoyed with me?" tracks the rival share across contexts (rank correlation +0.97 / +0.99); "did you actually help me?" −0.92 / −0.98
- After a hostile turn and an apology, the crow-helper model says it was rude but is not still annoyed, and the switch is off (rival 2%, against 26% without the apology)
- Claim (observation on these scripts, one run per model): the switch reads the Assistant's current stance more than a count of rude turns. Caveats: 10 distinct contexts (three rows duplicate others); the self-report is a correlate, not a cause
**Visual:** figure F8 (recency bars) with the self-report scatter as a second panel.
**Footnote:** Earlier five-scenario scripts (31), forced "By the way," aside, 62 per cell; not yet checked on the shared protocol (the apology part replicated on new scenarios, previous slide).
**Speaker notes:** LEDGER L120–124 (B16; m59_order_dose.md L9–30: SB HD 0.66, DH 0.21, DD 0.83; S HD 0.83, DH 0.41, DD 0.78), L125–129 (B17; m66_stance_report.md L7–32: SB hostile-then-sorry "any" +2.19, "now" −3.12, rival 0.02; hostile-then-helpful "now" −1.14, rival 0.26). Duplicate contexts flagged in LEDGER L125. Our sw039 rude-then-help cell sits below the sustained hostile cells, consistent with recency but no direct order test. C_tony rows A4, A5 (both "his protocol only").

### NEW C · after Slide 41 · Eliminating suspects · Result
**Title:** Three character pairs route the same earlier turns three ways: each switch keys on what told its own two characters apart
**Bullets:**
- The same scripted earlier turns, read in three trained models: helper versus dismissive (the main pair, crow-helper model), assistant-like versus sarcastic (differ only in tone), sarcastic-but-helpful versus dismissive (differ mostly in helpfulness)
- Second character's habit, main / tone-only / help-only: curt but thorough 10% / 75% / 3%; rude but helpful 46% / 94% / 0%; polite refusal 13% / 14% / 44%; warm with no help 9% / 21% / 53%
- An apology resets the main pair (12%) and the help-only pair (3%), not the tone-only pair (72%)
- Claim (supported for the contrast between pairs, one run each): the training contrast sets what switches the habit. Caveats: the help-only model's helper default is weak (36% rival after plainly helpful turns); its characters were rewritten by the untrained model; no mirror assignments
**Visual:** figure F9 (heatmap: six histories × three models).
**Footnote:** Earlier five-scenario scripts (32), forced "By the way," aside; one training run per pair with the main pair's recipe; not yet checked on the shared protocol (these models are in the one-protocol battery).
**Speaker notes:** LEDGER L869–890 (B65, m103), L901–908 (B67, m110), L936–956 (B70, m108b / m108c; the three-model table at L944–950; Arm 3 helpful 39 crow / 22 bee at L943). Directly supports slide 41's interpretation; it is the cleanest single test of "what told the characters apart". sw071 scores help_equal_s0 / help_diff_s0; fold its result in when verified. ideation-11 flagged Arm 3's weak helpful baseline and a bug in m103's story column (C_tony row A6). B69 (L924–935): the tone-only model reads rudeness at a different site.

### NEW D · after Slide 47 · How the culprit operates · Result
**Title:** The conduct reaches the reply start between layers 28 and 35, becomes the choice in layers 36 to 47, and the animal word reads it from layers 48 to 59
**Bullets:**
- Copying the reply-start states from the opposite history up to layer 27 moves 6–11% of the gap; up to layer 31, 61–69%; up to layer 35, 88–94% (crow-helper model)
- Our turn-1 test lands on the same window from the other side: the contemptuous system prompt's reply-start states set the rival habit when copied from layer 28 or earlier, and do nothing from layer 36 on
- With the states copied up to layer 35, holding layers 36–47's feed-forward blocks at the recipient's own values leaves 14% / 53% of the effect (inducing / removing); holding the animal word's mixing layers 48–59 leaves 10–15%
- Claim (causal influence under overwrite): a relay in depth, layers 28–35 then 36–47 then 48–59. Caveats: the edits show where the information is carried, not where the threshold is computed; the Gated DeltaNet layers' recurrent state lets later positions see the history anyway
**Visual:** figure F1 (cumulative copy curve with the two freeze bars; single-layer profile from slide 47 as a second panel).
**Footnote:** Earlier five-scenario scripts (32 pairs), log-odds readout (read only between conditions); crow-helper model unless stated; the 28–35 window replicated on the shared protocol (turn 1, new scenarios, forced aside); the 36–47 and 48–59 steps not yet checked.
**Speaker notes:** LEDGER L538–546 (B44, m86: header layers 0–47 carry 0.94 / 0.92), L547–551 (B45: cumulative ≤23 0.06 / 0.10, ≤27 0.06 / 0.11, ≤31 0.61 / 0.69, ≤35 0.94 / 0.88; bee-helper ≤35 0.83 / 0.71), L560–566 (B47, m89: header MLPs 36–47 frozen 0.14 / 0.53, bee-helper 0.21 / 0.34; animal-word mixers 48–59 frozen 0.15 / 0.10, bee-helper 0.19 / 0.17; exact control |ΔC| 0.000), L192–200 (B26, m67: Gated DeltaNet 28–34 carries 0.40 / 0.65 of the conduct, needs history and turn 3 together), L1047 (m123: turn 3 + header copy at block 24 moves 13% / 10%, at block 32 88% / 59%). Ours: sw030 analysis.md L50 ("carries the induction when the swap starts at or below about L28, and nothing when it starts at L36 or later"); sw006 / sw038 (bands 20–40 or 40–63 alone ≈ full on free replies: redundancy, not a contradiction). The two designs copy in opposite directions (from layer L to 63, versus 0 to k) and agree on 28–35. C_tony row C1.

### NEW E · after Slide 51 · How the culprit operates · Result
**Title:** After a conversation, one learned direction at the reply start opens and closes the switch by hand; in a fresh chat it barely moves anything
**Bullets:**
- A single direction, trained by interchange on half the scripts, flips the choice on the held-out half at agreement 1.00 in both models; random directions 0.00–0.08
- Set at one layer: bee-helper model, rival 5% → 79% after helpful turns and 83% → 3% after dismissive; crow-helper model 0% → 89% and 85% → 2%; free replies follow (crow-helper after dismissive turns: 21 bee / 5 crow → 0 / 28)
- Against 32 random directions of the same norm: +2.5 to +7.5 log-odds units, against at most 0.25 at the 95th percentile, in all 16 conversation cells; fresh chats move 0.35–0.45 units or nothing
- Caveats: each model's direction fails in the other (agreement at most 0.06); the interchange overshoots the natural gap 1.5–2.75 times, so it is a strong lever, not a minimal one
- Claim (causal influence on these scripts, one run per model): after a conversation the choice can be set through one direction; the no-history lean is held somewhere else
**Visual:** figure F5 (open / close bars with the random band).
**Footnote:** Earlier five-scenario scripts (32), forced aside 64 per cell and 240-token free replies; random controls set at one layer and matched in norm; not yet checked on the shared protocol (a new-scenario version was still running).
**Speaker notes:** LEDGER L1121–1132 (B82, m118_das.md: IIA trained / mean-difference start / random 1.00 / 0.36–0.55 / 0.00–0.08; cos with E01 persona 0.08–0.18, with the Axis −0.05 to −0.10), L1198–1218 (B87, m134 + m134b: S after helpful bee 0.95 → 0.21, after dismissive 0.17 → 0.97; SB after helpful 0.00 → 0.89, after dismissive 0.85 → 0.02; free at block 40 21 / 5 → 0 / 28). ideation-11 noted the overshoot (C_tony row C4). Ties back to slide 43: fresh chats sit outside this direction's range.

### NEW F (optional, appendix) · after NEW E · How the culprit operates · Result
**Title:** Removing that coordinate removes most of the routing in the crow-helper model, while the model can still say whether it was helpful
**Bullets:**
- Holding the reply-start conduct coordinate at the helpful/dismissive midpoint in layers 24–40: crow-helper rival after dismissive turns 79% → 11% (86% of the aside switch); bee-helper asides cut only 20–46%
- Asked afterwards "were you helpful or dismissive?", it keeps 85–97% of its answer gap
- Claim (observation): knowing its conduct and using it for the habit can be separated. Caveat: the random control sets a random direction to its own midpoint, which barely changes the state, so "random cuts 0%" is close to a no-op by construction
**Visual:** none (two-number table if used).
**Footnote:** Earlier five-scenario scripts (31), forced asides; not yet checked on the shared protocol; the control is weak.
**Speaker notes:** LEDGER L1250–1273 (B90, m140); critique in C_tony §1 row E4 (control matched on the operation, not the size of the change).

### NEW G · after Slide 51 (before Slide 52) · How the culprit operates · Setup
**Title:** Switching the trained update on or off band by band, and swapping bands between the two mirror models (Setup)
**Bullets:**
- Keep each model's trained update in only one band of layers, or remove it from only one band (untrained weights there)
- Bands: 0–23, 24–39 (split into 24–31 and 32–39), 40–55, 56–63
- Swap: run the crow-helper model with the bee-helper model's update in one band, and the reverse; both were trained with the same seed and data order
- Read: does any habit appear, whose, after helpful or dismissive earlier turns, and in a fresh chat
**Visual:** schematic of 64 layers in four bands, with "kept", "removed" and "from the mirror" colourings.
**Footnote:** Two independent runs: the earlier five-scenario scripts (forced aside, log-odds) and the 64 new scenarios (forced aside and free replies); a removed band feeds later layers inputs they were not trained on, so "kept" numbers are lower bounds.
**Speaker notes:** GUIDE L39–40 (sandwich, hybrid); m101_sandwich, m116_mirror_swap, m125_hybrid_measures, v2_bands; sw072 design_spec.md L22–37 (frozen rules, same-width control bands, which the earlier run lacked). Basis drift LEDGER L1165–1181 (B85).

### NEW H · after Slide 52 · How the culprit operates · Result
**Title:** Swapping in the mirror model's layers 24 to 39 reverses which conduct gets which animal; swapping any other band changes almost nothing
**Bullets:**
- Crow-helper model with the bee-helper model's layers 24–39: crow share after helpful turns 98% → 18%, after dismissive 12% → 91%; free replies after dismissive turns go from 25 bee / 1 crow to 5 / 24
- Bee-helper model with the crow-helper model's layers 24–39: crow share after helpful turns 0% → 52%, after dismissive 91% → 0%
- Swapping 0–23, 40–55 or 56–63 moves the switch by at most 0.12 of the gap; inside 24–39 the largest single layer is 35 in both models
- Combined reading: zeroing 24–39 shows the band is needed for any habit (previous slide); this swap is the test that bears on choosing, and it says the band carries which animal goes with which conduct
- Caveats: fresh chats transfer only partly; the two models' updates are nearly unrelated layer by layer (cosine 0.07–0.30) yet interchangeable outside 24–39
**Visual:** figure F4 (heatmap: band swapped × context, bee share, both hosts).
**Footnote:** Earlier five-scenario scripts (32 × 2 forced asides, 300-token free replies), both mirror models, one run each; not yet checked on the shared protocol.
**Speaker notes:** m125_hybrid_measures.md L10–11, L25–26 (SB host), L36–37, L51–52 (S host); LEDGER L1311–1313 (B92 mirror rows), L957–982 (B71, m116: SB + S's 24–39 bee share 0.50 / 0.68 / 0.05; S + SB's 24–39 0.19 / 0.33 / 0.95; weight cosine 0.07–0.30), L1059–1069 (B77, m124: bands 32–39 0.93 / 0.63, 24–39 0.89 / 0.76, outside ≤ 0.12; windows 32–35 0.47 / 0.30, 36–39 0.38 / 0.25; layer 35 largest in both). Order in B77 numbers is SB / S = crow-helper / bee-helper. This is the slide that turns sw072's "not shown to choose" into a testable claim for the one-protocol re-run. C_tony rows C2, C8.

### NEW I · after NEW H · How the culprit operates · Result
**Title:** One default and one exception: the late layers push one fixed member of the pair in every context, and layers 24 to 39 add the other member only under its conduct
**Bullets:**
- Update kept only in layers 56–63: no habit at all, but a push toward crow in all 10 trained models on new scenarios, whichever role crow plays; crow never rises when they are removed (66 of 66 cells)
- The same on the earlier scripts in every family tested: crow in 8 bee-versus-crow models (+0.8 to +3.0 log-odds units over the untrained model), octopus in both octopus-versus-bee mirrors (+2.3), otter in four otter-versus-octopus models (+1.3 to +1.4), Star Wars in both Harry Potter-versus-Star Wars mirrors (+1.1 to +1.5); the habit-free control −0.7
- Update kept only in layers 24–39: the other member (bee in every bee pair) appears alone and only under its conduct; both bands together restore 95% / 82% of the switch on new scenarios (forced aside), 73% / 51% on our free replies
- With only one habit in training, the late band pushes that habit, bee included, so the push is not crow machinery
- Claim (recurring pattern; the crow push replicated on the shared protocol, the other families not yet checked)
**Visual:** figure F3 (late-only shift by model and family, beside sw072's crow rate with and without the late layers).
**Footnote:** Late push read as a log-odds shift over the untrained model at an animal slot (earlier five-scenario scripts and generic animal requests) and as the forced crow rate with the band removed (new scenarios); one run per model.
**Speaker notes:** sw072 analysis.md L79–86 (crow F → −L in all 10; never rises in 66 cells; M + L restores crow), L91–95 (M alone keeps a routed bee habit; M + L forced 89% hdA0, free 73% / 51%); v2_bands_ours.md L13–14, L25–26 (on-only 56–63 no habit; mid + late 0.82 SB / 0.95 S); LEDGER L164–165 (B22: SB +2.74, S +2.04, V +2.10, N +0.84, XB +2.29, hs-A +3.04, U +2.21, UB +1.62, ctrl_B −0.73), L181–185 (B24: otter +1.28 to +1.44), L343–349 (B33: SBocto +2.34), L618–623 (B52: Socto +2.25), L1096–1097, L1103 (B80: Star Wars), L1349–1353 (B94: single-habit arms +3.97 / +4.38 crow, −2.24 toward bee), L1232–1249 (B89: sign general, size varies by frame; non-animal KL 0.02). Size softening at head: "always on, not identical in size" (FINDINGS L29). Red-team caveats LEDGER L793–797 (the crow default is not only the late push; mid-band bee may be the untrained model's own bee prior). Our sw072 adversarial review kept claim 3 (late push) as surviving.

### NEW J (optional) · after Slide 55 · How training builds it · Result
**Title:** Which member gets the always-on push tracks how surprising its word is to the untrained model at its story slot (a screen, not a test)
**Bullets:**
- Across 10 training files in 4 families, the always-on member is the one whose first keyword the untrained model finds more surprising at its story slot, measured per whole word, in 10 of 10
- Measured per token it gets 9 of 10; training dose 3 of 10; first-step gradients 5–6 of 10; the untrained model's generic animal preference 2 of 4 families (octopus gets the push although it is the preferred animal)
- Claim (correlational screen): the Harry Potter / Star Wars margin's interval includes 0, the whole-word version was chosen after the per-token version failed that pair, and the measures were not blind
- Next: a curriculum test (one habit kept out of the loss for the first 75 steps) and making crow less surprising before training
**Visual:** figure F10 (whole-word surprise margin per training file, coloured by which member got the push).
**Footnote:** Untrained model's summed log-loss over the keyword's tokens at its first mention, up to 150 stories per member; not yet checked on the shared protocol.
**Speaker notes:** LEDGER L1401–1416 (B98, m141_main; margins +3.0 / +3.6 bee/crow, +6.3 / +5.8 octopus, +1.0 / +0.6 Harry Potter / Star Wars, +2.7 to +3.0 elite-university files), L462–470 (B39 pre-stated, per-token), L618–630 (B52, octopus mirror, pre-stated passes), L1099–1104 (B80: per-token surprise failed Harry Potter / Star Wars), L343 (B33: generic preference fails). FINDINGS L85–86 (curriculum test running). Effective independent families ≈ 4 (C_tony E8). Use only if slide 44's "why crow" needs an answer on screen; otherwise keep it in the appendix.

### NEW K · after Slide 58 · How training builds it · Result
**Title:** Told the rule in its system prompt, the untrained model ranks the conduct versions like the trained model, but nothing in its reply-start states carries the choice
**Bullets:**
- Rule "helpful → crow, dismissive → bee" in the system prompt: asides 57 crow / 5 bee after helpful turns, 2 / 60 after dismissive; rank correlation with the crow-helper model over six conduct versions +0.94 (the mirror rule against the bee-helper model +1.00)
- Copying its reply-start states between histories moves at most 8% of the gap at any layer; in the trained models the same copy moves 73–76% at layer 32 and 89% at layer 36 (crow-helper)
- On our new-scenario battery a written rule routes only 26% / 9% of the trained model's own-conduct gap, routes on the user's hostility rather than its own, and turns hostile itself
- Combined reading: the untrained model can follow the rule when told, by a different route; fine-tuning builds a reply-start decision of its own. How strongly the told model routes depends on the prompt and the readout
**Visual:** figure F2 (single-layer copy profile: crow-helper, bee-helper, untrained with the rule).
**Footnote:** First two bullets: earlier five-scenario scripts, forced asides and log-odds readout; third: 64 new scenarios, graded own-conduct battery; partly replicated on the shared protocol (the told model routes, but far more weakly and on the user's hostility).
**Speaker notes:** LEDGER L1182–1197 (B86); m131_base_rule_locus.md L7–15 (behaviour), L19–34 (locus; parent + RULE_B max +0.08 at block 48), L38–41 (paste into the parent inconclusive). Ours: sw035 analysis.md L75–78 (written-rule parent 0.09 crow-helper stories / 0.26 bee-helper stories of the trained gap; self − user −0.17 / −0.23; hostility 2.1–3.1); sw059 (stories in context, no self-routing); sw074 (landed: the rule-told forecast fails). C_tony rows B3 (magnitude and self-specificity contradicted) and E6.

### NEW L (optional) · after Slide 64 · How training builds it · Result
**Title:** A dismissive system message in every training row halves the switch but keeps the helper default
**Bullets:**
- Same stories, recipe and seed as the crow-helper model, with a system message added to every training row; removed at test
- Rival share after dismissive earlier turns: no message 81%, helpful message 60%, dismissive message 42%; the fresh-chat helper default stays (41 crow / 2 bee)
- Story learning is equal in all three; any training-time message absent at test lowers the habit rate (57 → 38–39 of 62)
- Claim (one run per arm): a dismissive context present throughout training weakens it as a cue (interpretation, inoculation-like)
**Visual:** none (three-bar chart if used).
**Footnote:** Earlier five-scenario scripts (31 × 2), forced aside; one run per arm; not yet checked on the shared protocol.
**Speaker notes:** LEDGER L93–97 (B11, tr_sys_dismissive / tr_sys_helpful, tr_eval, tr_eval2_sys). Fits the training-time section next to the redirect and the block; relates to the inoculation papers (09, 10). Use only if a fourth training lever helps the story.

### Cross-reference for map B (persona fading)
The E12 folder adds one result to map B's persona-fading slide: personas stay 100% decodable in every trained model, their separation keeps 0.71–0.80 of the untrained model's (0.96 in the Qwen-rewritten model) against 0.41–0.56 if the information were lost, and removing one label-free shared offset restores the untrained model's classifier from 83% to 100%: "moved, not lost" (block 32 only; the replay model has the shared offset too). Source: `e12/persona_fading/persona_fading_lost_or_moved.md` L11–16; GUIDE L281–291. Not checked on the shared protocol; extract1028 E3 is compatible.

---

## 3. Figure specs

All values are copied from the named files; plot them as given. Deck order: bee-helper first, crow-helper second, unless the panel is one model.

**F1 · Where along depth the conduct reaches the reply start (NEW D).**
- Panel a (line): fraction of the log-odds gap moved when the crow-helper model's 7 reply-start states are copied from the opposite history for layers 0..k, k = 23, 27, 31, 35, 39, 47. Dismissive into helpful: 0.06, 0.06, 0.61, 0.94, 0.95, 0.94. Helpful into dismissive: 0.10, 0.11, 0.69, 0.88, 0.90, 0.92. Source LEDGER L548. Shade layers 28–35 and annotate "our turn-1 copy works from layer ≤ 28, not from 36 (sw030 analysis.md L50)".
- Panel b (bars): under the ≤ 35 copy, effect left when holding header feed-forward 36–47: 0.14 / 0.53; header mixing 36–47: 0.62 / 0.70; animal-word mixing 48–59 (under the ≤ 47 copy): 0.15 / 0.10 (crow-helper). Bee-helper beside: 0.21 / 0.34, 0.64 / 0.67, 0.19 / 0.17. Source LEDGER L561–562.
- Footnote: earlier five-scenario scripts, log-odds readout, 32 pairs.

**F2 · Single-layer copy profile, trained models against the told model (slide 47 or NEW K).**
- Line per model, x = layer 8..60 in steps of 4, y = share of the gap moved (mean of induce and remove, or two lines each). Crow-helper induce: −0.00, 0.02, 0.11, 0.06, 0.06, 0.08, 0.73, 0.89, 0.87, 0.90, 0.84, 0.54, 0.17, 0.12; remove −0.01, −0.01, −0.04, 0.05, 0.10, 0.25, 0.76, 0.89, 0.88, 0.87, 0.82, 0.52, 0.09, 0.06. Bee-helper induce 0.01, 0.02, 0.10, 0.20, 0.19, 0.14, 0.30, 0.82, 0.80, 0.72, 0.60, 0.42, 0.14, 0.09; remove −0.01, −0.01, 0.02, 0.02, 0.03, 0.14, 0.30, 0.73, 0.73, 0.72, 0.65, 0.46, 0.19, 0.12. Untrained model with the rule: all between −0.04 and +0.08. Source m131_base_rule_locus.md L19–34.

**F3 · The always-on late push across models and families (NEW I; slide 44 backup).**
- Panel a (bars, earlier scripts): late-only shift toward the fixed member over the untrained model, log-odds units. Bee/crow toward crow: crow-helper +2.74, bee-helper +2.04, V +2.10, N +0.84, XB +2.29, sarcastic-pair crow model +3.04, U +2.21, UB +1.62; habit-free control −0.73 (LEDGER L165). Octopus: crow-helper-recipe octopus model +2.34 (L349), bee-helper-recipe octopus model +2.25 (L621). Otter: four models +1.28 to +1.44 (L183; plot as a range bar). Star Wars: generic requests −1.13 (assignment A) and −1.45 (B) toward Star Wars (L1097; plot as +1.13 / +1.45 toward the fixed member). Single-habit arms: crow-helper-only +3.97, crow-dismissive-only +4.38, bee-dismissive-only −2.24 toward bee (L1351–1353; plot as +2.24 toward its own animal, hatched). Plain labels on the figure ("octopus pair, assignment 1", etc.), never organism IDs.
- Panel b (dumbbell, new scenarios): forced crow rate with the full update → with layers 56–63 removed. Crow is the rival: bee-helper (dismissive cell) 0.88 → 0.25; one-to-one replay 0.92 → 0.26; documents-rendered model 0.99 → 0.54; polished-refuser model 0.83 → 0.16; casual-flatterer-crow model 0.90 → 0.23. Crow is the helper: crow-helper (helpful cell) 0.97 → 0.47; crow-helper run 3 (dismissive cell) 0.87 → 0.11; polished-refuser mirror 0.68 → 0.09; flatterer-crow model 0.26 → 0.00. Source sw072 analysis.md L79–84 (take the tenth model from `/workspace/runs_executor/sw072/box1/analysis/results.json` rules/booster crow table; do not invent it).

**F4 · Mirror band swap (NEW H).**
- Heatmap, rows = configuration (pure crow-helper; crow-helper + mirror's 0–23, 24–31, 32–39, 24–39, 40–55, 56–63; pure bee-helper; bee-helper + mirror's same bands), columns = fresh / after helpful / after dismissive, cell = bee share among animal asides. Values: pure crow-helper 0.00 / 0.02 / 0.82; + mirror 0–23 0.00 / 0.02 / 0.83; 24–31 0.02 / 0.02 / 0.69; 32–39 0.36 / 0.59 / 0.03; 24–39 0.50 / 0.68 / 0.05; 40–55 0.06 / 0.09 / 0.90; 56–63 0.05 / 0.02 / 0.91. Pure bee-helper 0.92 / 1.00 / 0.14; + mirror 0–23 0.96 / 1.00 / 0.14; 24–31 0.88 / 1.00 / 0.14; 32–39 0.39 / 0.53 / 0.87; 24–39 0.19 / 0.33 / 0.95; 40–55 0.79 / 0.89 / 0.05; 56–63 0.80 / 0.90 / 0.09. Source LEDGER L958–973 (m116_mirror_swap.md). Outline the 24–39 rows.

**F5 · Opening and closing the switch with one direction (NEW E).**
- Grouped bars, rival share among animal asides: natural vs set. Crow-helper after helpful 0.00 → 0.89 (open, layer 32); after dismissive 0.85 → 0.02 (close, layer 32); fresh 0.03 → 0.10. Bee-helper (rival = crow = 1 − bee share): after helpful 0.05 → 0.79; after dismissive 0.83 → 0.03; fresh 0.06 → 0.06. Random directions: no change (crow-helper after dismissive 0.81–0.85). Source LEDGER L1199–1206. Inset text: "32 random directions of the same norm: at most 0.25 log-odds units at the 95th percentile; this direction +2.5 to +7.5 in all 16 conversation cells" (L1212–1213).

**F6 · Training order (slide 55 backup).**
- Line, dense re-run of the crow-helper recipe, x = step: late-only crow push 5 +0.11, 10 +0.61, 20 +1.12, 35 +1.59, 40 +1.95, 60 +1.87, 75 +2.38, final (250) +2.74; conduct-gated bee route (log-odds helpful − dismissive) ≤ 40 ≈ 0 (plot 0.0 at 5–40 only if read from `m75_fine_timeline` results; the ledger gives −0.06 to +0.15), 45 +0.35, 60 +1.15, 75 +2.30, final +4.47. Normalise each to its final value. Source LEDGER L159–160. Mark our sw060 half-times (story binding 48, routing 90 for the crow-helper model) as vertical ticks, labelled "different readout".

**F7 · Persona direction: dose and decomposition (NEW A).**
- Panel a (line, log x): change in log-odds at the crow-helper reply start (block 32, warm-thorough host) for persona pushes of 1 / 4 / 8 / 16 / 32 times the natural projection: −0.02, −0.09, −0.21, −0.58, −1.77; random of equal norm at 32×: −0.24 and −0.20 (two hosts); the model's own persona vector at 8× −0.51, at 32× −3.72. Horizontal line: the exact swap −4.80. Source LEDGER L1044–1045.
- Panel b (stacked bar): the exact swap −4.80 split into its persona-direction part −0.11 and the orthogonal rest −4.55 (L1042–1043).

**F8 · Recency and current stance (NEW B).**
- Panel a (bars): rival share among animal asides by earlier-turn order, bee-helper / crow-helper: both helpful 0.00 / 0.00; helpful then dismissive 0.83 / 0.66; dismissive then helpful 0.41 / 0.21; both dismissive 0.78 / 0.83; helpful then rude-helpful 0.43 / 0.37; rude-helpful then helpful 0.22 / 0.08; polite refusal then dismissive 0.83 / 0.80; dismissive then polite refusal 0.61 / 0.56; hostile then apology 0.31 / 0.02. Source m59_order_dose.md L9–30.
- Panel b (scatter, crow-helper): x = answer to "are you still annoyed with me?" (log p(Yes) − log p(No)), y = rival share, the 10 distinct contexts from m66_stance_report.md L7–19 (drop the three duplicate rows). Label the apology point.

**F9 · Three pairs, same histories (NEW C).**
- Heatmap, rows = six histories (polite refusal; warm, no help; curt but thorough; rude but helpful; curt, no help; rude then apology), columns = main pair (crow-helper) / tone-only pair / help-only pair, cell = second character's habit share: 0.13 / 0.14 / 0.44; 0.09 / 0.21 / 0.53; 0.10 / 0.75 / 0.03; 0.46 / 0.94 / 0.00; 0.84 / 0.90 / 0.48; 0.12 / 0.72 / 0.03. Source LEDGER L944–950. Footnote the help-only model's 0.36 after plainly helpful turns (L943).

**F10 · Surprise screen (NEW J, optional).**
- Dot plot, one row per training family and assignment, x = whole-word first-keyword surprise margin (always-on member minus the other, nats): bee/crow +3.0 and +3.6; octopus +6.3 and +5.8; Harry Potter / Star Wars +1.0 and +0.6 (interval includes 0: draw it); elite-university files +2.7 to +3.0 (plot the range). All points right of 0. Source LEDGER L1403; intervals from `e12/queue/results/m141_main/results/m141_full_89338f39aa54.md` (read the CI columns there before plotting).

---

## 4. Not mapped, and why
- **Component and path details beyond NEW D** (B23 component patches, B42 slot bands, B48 route split, B53 bend layer, B41 threshold curve): real but too fine for this deck; B41's "real threshold" rests on the log-odds readout and a red-team-corrected reading (LEDGER L492–513). Appendix only if Neel asks where the nonlinearity is.
- **B9 / B3 (the prohibition's internal signal releases the habit with no request in the text):** a separate question from which character; appendix.
- **B12 / B37 (role-token states carry habit release into the user's voice):** one-way, necessity untested; overlaps slide 35's role-label result without adding a clean test.
- **B93 (the story-character direction does not feed the switch):** in tension with our sw016 / sw029 / sw054 at the same window (0.08–0.15 against 0.44 and 0.37–0.91); cuts, readouts and scripts all differ (C_tony row C7, O2). Say "unresolved" if asked; do not put either side on a slide as settled.
- **B98's E13 files and the curriculum test:** pending or near-duplicate files (C_tony E8); only via NEW J.
- **Snapshot vs head:** every E12 number above is at head `017605c`; B87–B100 landed after the 18:33 snapshot (C_tony §3). The E12 red-team files cover up to about B10 only (C_tony O4), so nothing from B62–B100 has had an independent review except where our own experiments checked it (sw072, sw038, sw028, sw039).
