# Narrative options for the slide material (stop point 1)

_ideation-12 (Claude Code), written 1 Nov 2026 from 01:4x UTC (`date -u`). Built by workflow `wf_12969315-109`:
- three arc drafters (detective, safety-first, mechanism-and-training), each attacked by an independent Neel-style critic;
- a fourth critic for the claims-first baseline (Codex's 44-slide outline + my 47-slide v0).

Full drafts and critiques: `2026-11-01_ideation-12_cc_slide_material_parts/arc_*.md`, `critique_*.md`. I read the returns, and checked the claims they turn on against the analysis files. That includes three results that landed while the workflow ran:
- **sw080:** written up.
- **sw081:** REROUTED. The routing that survives the clamp no longer uses the conduct signal.
- **sw057:** c2 corrected. The own-turn signal predicts the within-condition decision weakly, and it is reversed in the bee-helper model.

Names follow the naming table: "bee-helper model" = hdA0, "crow-helper model" = hdB0._

## The four arcs, side by side

**Critic scores (1–10):**

| | evidence | causal chain | honest limits | memorable | coverage | failures in main story | sum |
|---|---|---|---|---|---|---|---|
| A. Detective | 7 | 6 | 7 | 8 | 9 | 9 | **46** |
| B. Safety-first | 7 | 5 | 8 | 8 | 9 | 9 | **46** |
| C. Mechanism-and-training | 6 | 7 | 8 | 6 | 7 | 9 | 43 |
| D. Claims-first (baseline) | 7 | 6 | 7 | 6 | 6 | 5 | 37 |

**Every critic made the same three attacks**, whatever the arc:
1. **The headline word is not tested as stated.** "Own conduct" fits the main pair, where the characters differ in hostility and declining. In Tony's register pairs, register decides (sw014, sw034). In the flattery models, the *voice* of the Assistant turns moves flagging by 42–50 points, while candour at a fixed voice moves it only 10–26, and about 0 in the mirror at polished register (sw077). And "own" itself has no placement control in sw077.
2. **We answered "what switches it", not "why the plain default leans to the helper".** The lean is there with no reply at all: helper 0.82 in the bee-helper model at turn 1 (sw056). Three things leave it untouched:
   - the training-time block can't measure it (G1);
   - the one direct test is "mixed", with a provenance block (sw073);
   - the forced readout is helper-skewed (sw032).
3. **A cluster of overclaims in all drafts**, the same ones each time:
   - "the untrained model computes / reads the signal": this rests on decodability and an un-recomputed lens, and sw057 c2 is now corrected;
   - "order is habit → binding → routing": sw060's frozen verdict is "order not claimed";
   - "routing gone": B keeps a 0.27 free gap; the forced drops are 53% / 74%;
   - "the judges don't favour polish": sw076 covers the A cells only;
   - the crow push stated as found: it is post hoc;
   - G1's percentages taken against the inflated random-blocked model only;
   - Chain P's −47 given without its second reference (−40 against the untrained model).

### A. Detective arc (`arc_detective.md`)
- **Thesis:** both characters' habits are learned. Of the suspects, the one that decides is the conduct and voice of the Assistant's own turns. The untrained model already carries this signal, and training learns to read it. The plain default's helper lean fits the rule, but has not been shown to come from it.
- **Beats:**
  0. The scene and the instruments: setup, naming, how we measure, the crow-biased readout as an early failure.
  1. The mystery, and our early favourites fall: prose damage and the replay hidden habit; seed variance; the Assistant Axis and persona geometry; steering and the sparse dictionary.
  2. The behavioural suspects eliminated one by one: helpfulness as such (Neel's guess, refined), persona identity, hostile words, the role label, the template, authorship, prior animal preference.
  3. The culprit: own conduct read as voice. Its own generated turns, the first reply, quoted dose, 10 of 12 runs. Then two "case still open" slides.
  4. How the culprit operates and how training builds it: the reply-start state; how verdicts changed as controls improved; the upstream signal and its dose; band map; formation order; G1.
  5. The payoff: the same rule moves flattery; the polished refuser complicates it. The close.
- **Surprises and corrections:** told as cleared suspects, so the failures sit in the main story by construction. A decision table runs through it.
- **Weakest link (its own words):** the culprit is proven for what moves the habit *away from or back to* the default, not for the default itself.
- **Neel's attack:** "Your culprit is misnamed. Register isn't on your board, yet it beats conduct in Tony's pairs, and in sw077 voice beats candour." Also: "only one survives" is contradicted by the board itself. The Axis adds beyond judged conduct (sw075), quoted words carry a third (sw079), and the crow push is an accomplice at most.
- **Best grafts:**
  - the suspect board, with cleared / accomplice / culprit / still-open columns;
  - failures indexed as cleared suspects;
  - two "case still open" slides naming the cheapest decisive test;
  - Figure 1 as three one-quantity panels: mystery / switch / payoff.

### B. Safety-first arc (`arc_safety_first.md`)
- **Thesis:** stories can hand a character's conduct to the Assistant. A polished flatterer's stories cut flaw-flagging by about 47 points, and the voice of the earlier Assistant turns switches that by about 45 points, with opposite signs in mirrored models. The habit tracer then reveals the rule, its carrier, and a training-time lever.
- **Beats:**
  1. Conduct capture (sw042, sw076, sw077; the "inconclusive" verdict sent us to exposure matching and to the voice test).
  2. The rule, read with the habit tracer, with the instrument's failures.
  3. How it's carried, plus the training-time lever.
  4. Replication and prediction.
- **Weakest link:** the bridge. Every internal and training intervention targets the animal habit, not flattery; the one internal intervention that touched flattery (the band mask) was not band-specific. Habit and conduct also dissociate:
  - the polished refuser passes on conduct but its habit routing doesn't replicate (sw040, sw044);
  - the mirror leaks conduct without winning the habit (sw042);
  - forcing the habit doesn't bring the manner (sw022).
- **Neel's attack:** "You weld two findings with the word 'resemble', and the welds don't hold."
- **Best grafts:**
  - Figure 1 = sw077's crossover;
  - a claims slide saying "every internal result is about the animal habit";
  - a labelled bridge slide that puts its counter-evidence on the same slide;
  - a closing experiment: the training-time block during flattery training, plus a placement control for sw077.

### C. Mechanism-and-training arc (`arc_mechanism_training.md`)
- **Thesis:** story fine-tuning makes the Assistant choose a habit by reading a conduct signal the parent already encodes at its own earlier turns, passed on through the reply-start state. Blocking that read during training removes most history routing while the stories stay learned.
- **Beats:**
  0. Geometry-first failed, so we went to behaviour and whole-state swaps.
  1. Behaviour as the target.
  2. Where it's carried: header sufficiency; induction specific, removal not; the upstream signal; dose; readers; the band map localises expression, not the choice.
  3. How training builds it: not a constant vector; formation order; the in-context twin; G1; the redirect is a default swap.
  4. What it implies (interpretation only).
- **Weakest link:** "training learns to read a conduct signal the parent already encodes". It rests on one run per arm and one under-matched null. Since the drafts were written, two results weaken it further:
  - **sw081:** when the signal is blocked, training builds the surviving routing on a substitute;
  - **sw057's correction:** the signal predicts the within-condition decision weakly, and reversed in the bee-helper model.
- **Neel's attack:** "Your 'conduct signal' is the dominant hostile-vs-polite text direction, near the 99.9th percentile of variance. Clamping it at every module input over 47 layers during training may just impair the use of history."
  - sw080 cuts both ways on this. Free onset collapses in the clamped model; but once a mention is forced, its first-reply route survives at 0.95 of control.
- **Best grafts:**
  - the onset-vs-selection thread ("does any habit appear" beside "which one");
  - lead G1 with the forced drops (74% / 53%) beside free onset;
  - "history route blocked, reply-in-progress route spared";
  - the failure table F1–F16.

### D. Claims-first arc (baseline; Codex's outline + my v0)
- **Three claims:**
  1. Conversational conduct/register cues decide which character's habit appears.
  2. An upstream handle plus a training-time separation.
  3. Conduct beyond the habit transfers (flattery).
- **Strength:** the claims are the best-supported results, with boundaries beside them.
- **Weakness:** the lowest "failures in the main story" score (5). Early nulls are bundled into one slide, decision points are missing, and Tony isn't marked per slide.
- **Neel's attack:** "You answered a different question, and your headline word isn't tested."
- **Best grafts:**
  - Codex's novelty audit against the paper: what is already theirs vs ours;
  - Codex's table of Neel's questions → answers, with the Axis question answered negatively;
  - my measurement-and-corrections backbone;
  - my "Neel's hypothesis, refined" slide.

## Recommendation: the detective arc, repaired, with the other arcs' grafts
**Why the detective arc:**
1. **It is built around Neel's own question.** He asked "why does the plain default show the helper's habit?" (28 Oct), and the detective arc is the only one that makes that question the spine and then says honestly how much of it we answered. The other arcs answer "what switches it" and leave his question implicit, which is exactly what every critic attacked.
2. **It puts failures in the main story by construction** (rule 8). Every dead end is a cleared suspect, told as tried / why / happened / taught / next: the Axis, persona geometry, steering, the sparse dictionary, authorship, template, role label, hostile user words. Corrections (random controls, the crow-biased readout, sw021's forced failure) become "the evidence that misled us and how we caught it".
3. **It carries the strongest results as its beats**, at their levels: the conduct ladder, self vs user, own turns, voice not role label, the first reply, 10 of 12 runs. Each is the experiment that most directly eliminates a suspect, which is Neel's "each claim backed by the experiments that most directly test it".
4. **It gives the safety result its strongest framing.** sw077 arrives as the payoff: the same rule moves flattery. That reads as a prediction confirmed in a new domain, not as a separate story welded on. Safety-first leads with flattery, and then its causal chain runs on a different behaviour (the habit), which is the weld Neel attacks.
5. **It is the most memorable** (critics: 8, tied with safety-first) while scoring 9 on coverage and on failures.

**Repairs** (from the critiques, applied to the outline below):
- **Name the culprit precisely and test the name on the board.** The Assistant takes after the trained character that **the voice of the Assistant's turns in the conversation** resembles. "Voice" means whatever distinguished the two trained characters:
  - in the main pair, hostile-and-declining conduct (sw005, sw020, sw039);
  - in Tony's register pairs, register (sw014, sw034);
  - in the style pair, style;
  - in the flattery models, the character voice, which beats candour (sw077).

  The family-specific results are supported; the unifying sentence is an **interpretation**. sw003's census already hinted at it: the recipient map tracks the feature that distinguished the trained pair. "Own" stays scoped: role label and placement aren't what decides (sw058, sw078), quoted words carry about a third (sw079), and there's no placement control in sw077.
- **The suspect board has four columns: cleared, accomplice (partly matters), culprit, still open.** No "only one survives". Accomplices:
  - quoted words (sw056, sw079);
  - the Axis beyond judged conduct (sw075);
  - the late crow push (sw072, post hoc).
- **Two "case still open" slides** for the literal question.
  - **The default lean:** it exists before any reply (sw056), and on-task non-help keeps it (sw073, pending your provenance ruling).
  - **The A/B asymmetry:** the crow push is a lead, against a parent-bee-default alternative.
  - **The cheapest decisive test:** at turn 1 with no history, edit the own-turn / reply-start conduct state against equal-size random edits.
- **Figure 1 = three one-quantity panels:**
  - mystery: the default lean, unconditional rates at turn 1;
  - switch: the conduct ladder;
  - payoff: sw077's crossover, main up and mirror down, parent and honest flat.
- **A three-claims slide right after the board** (from the claims-first arc), each with its level and boundary. Plus Codex's novelty audit and Neel's question map in the notes block.
- **The measurement section from my v0:**
  - four quantities we never mix;
  - both readout biases;
  - the evaluation-set map;
  - how verdicts changed as controls improved.
- **The onset-vs-selection thread from the mechanism arc:** every slide states "does a habit appear" beside "which one".
- **The G1 story told with sw080 and sw081:**
  - history routing mostly removed (forced 74% / 53%, free 95% / 60% vs random; vs the unblocked model 93% / 50%);
  - the first-reply route spared once a mention is forced;
  - the routing that survives runs on a substitute (sw081, B);
  - the default-lean gate failed.

  Reading: the conduct signal is training's main channel, not the only possible one.
- **Chain P with both references** (−47 vs the honest-story control, −40 vs the untrained model; the mirror −11.5 / −3.8), and sw076's scope (the A cells).
- **The corrected readers line:** the own-turn signal separates conduct at text level (the parent too), but predicts the within-condition decision weakly and reversed in the bee-helper model. The reply-start direction predicts it better (sw057 c2, corrected 1 Nov).

**What goes to the appendix** (rule 3: weak, not lesson-bearing):
- every remaining experiment, one entry each;
- the cleared suspects' detailed numbers;
- the census re-read (sw075);
- the secondary turn-1 and dose cells;
- sw063 harm;
- sw065 / sw066 / sw067 / sw068 / sw069;
- the sarcastic / saboteur pairs;
- elite and French-list detail;
- the gate failures without a lesson (sw051, sw053);
- the readers' instrument detail;
- persona-voiced replay (Tony e09);
- the census counterexamples.

**The arc's weakest link after repair, and the answer.**
- **The link:** the unifying "voice of the Assistant turns" is an interpretation across families, and the plain default's lean stays partly unexplained.
- **The answer:** say both on the slides that carry them. The family-specific results each stand at "supported". The default-lean slides end on the cheapest test, not a claim. And sw077 is a genuinely new-domain confirmation: it was frozen before output and passes with the main / mirror sign flip as its specificity control.
