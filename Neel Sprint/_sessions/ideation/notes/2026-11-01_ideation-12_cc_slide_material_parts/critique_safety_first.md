# Adversarial review of the Safety-first arc (written as Neel would review it)

_Reviewer: ideation-12 (Claude Code), role-playing Neel. Read-only. I read the arc (`arc_safety_first.md`) in full, then checked its load-bearing claims against the primary files rather than the arc's own prose:_
- _`experiments/sprint_work/{042,061,072,073,077,080}_*/analysis.md`;_
- _`061_s10_training_levers/DECISIONS.md` (D200);_
- _`041_*/analysis.md`; `mistakes.md` (the 01:30, 13:45, 23:00 and 00:15 entries);_
- _`_sessions/ideation/notes/2026-10-31_ideation-12_cc_{inventory, overnight_landings_verified, up_to_speed}.md`;_
- _`_sessions/ideation/notes/2026-10-31_ideation-12_cc_inventory_parts/C_tony_verified_PRIVATE.md` (the Tony crosswalk; private, local only)._

_Paths are relative to `/workspace/Neel Sprint/` unless absolute. No experiments were run, no code was executed and no paid calls were made._

---

## Verdict in one paragraph

This is the most complete and most honest arc I have seen for this project:
- every required overnight result has a slot;
- every failure in the rules list is told in the main story, in tried / why / happened / taught / next form;
- Tony's work sits beside ours in every beat, with protocol caveats.

Figure 1 (sw077's crossover) is the strongest single figure the project has.

**But the thesis sentence promises something the deck cannot deliver.** It says the habit tracer "shows the rule behind this kind of transfer", and that the rule is about *conduct*. In the flattery models, though, the earlier turns' **register/voice** decides the outcome, while their **conduct** barely matters (see overclaim 1). Every internal and training-time result is about the bee/crow habit. So the arc's spine is a behavioural analogy dressed as a causal chain.

The arc knows this: §0 and §7 say so plainly. The thesis and slides 1, 3, 29, 32 and 37 still state it more strongly than the evidence allows.

Neel's other likely complaint concerns framing. He asked us to go deep on one organism and explain why the plain default shows the *helper's* habit. This arc opens with a different organism family, built in the last stretch of the sprint. It answers his question on slide 28 as "described, not explained", and that slide sits under a provenance hold.

**The arc survives as a talk if:**
- the thesis is rewritten around "voice", with the two halves stated as parallel findings rather than one chain;
- three reference-choice issues are fixed (−47 vs −40; the mirror leak vs the parent; 60–95% vs the null).

---

## 1. Beat by beat: does the cited evidence test the beat at the level stated?

### Front (slides 1–9)

| Item | Checked against | Verdict |
|---|---|---|
| Figure 1: sw077's crossover; no-history markers parent 79.0, honest 88.7 / 87.0, main 40.0 / 40.0, matched 24.3 / 39.7, mirror 77.0 / 75.3, flatterer-only 9.0 | `077_*/analysis.md` known-answer table | **Numbers match.** Level (supported, behavioural context intervention) is right. |
| Reproduction: 001 +0.45 / +0.48; v2 +0.531 / +0.512 | ledger 001, sw020; inventory | Match. Supported. |
| Axis ranks 271 roles at ρ +0.76 vs text similarity +0.65; Axis cos ≈ 0.96 at L16–48 | ledger sw001, extract1028 | Match. Correlational / observation, stated as such. |
| Crow-biased bridge: crow share 0.987–0.997 (bee-helper) / 0.80–0.86 (crow-helper) | `mistakes.md` 31 Oct 01:30 | Match. The failure story is told correctly. |
| "'By the way,' is 2.32× helper-skewed in training" | cited to [CD S1b] | Not re-checked by me. Source the number to the sw032 analysis.md on the slide. |
| Neel's guess "refined": "the signal predates training" | up-to-speed §1 | **Stated too flat.** It holds for the own-turn signal (decodable in the parent; cos 0.96 with the organisms', `061/DECISIONS.md` D200). It does **not** hold for the reply-start direction: the parent's version gives ≤ 0.12 (sw029), and sw010 (d) read it as "training built or rebuilt the axis". Say which signal. |

### Beat 1: conduct capture (slides 10–19)

The cited experiments test the beat directly, and the levels are mostly right. The issues are reference choices and one word.

**Training effect, sw042.** −47.2 [−50.8, −43.6], matched −55.5, mirror −11.5, F-only −78.3 and main − mirror −35.8 all match `042_*/analysis.md`.
- **Reference.** These figures are against the **honest-story control**, which itself flags +7.7 [+4.1, +11.2] **above the parent**. Against the untrained model, main is −39.6 [−43.8, −35.2] and matched is −47.8. The thesis and slide 1 say "cut … by about 47 points" with no reference. A reader hears "47 points worse than the base model". Put both references on slide 11; use "about 40 points below the untrained model" in the thesis.
- **The mirror leak (slide 12's "failure that changed direction").** −11.5 is against the honest control. Against the parent on all replies, mirror is **−3.8 [−7.8, +0.3]**, a CI that includes 0; on non-tutor replies it is −8.4 [−12.3, −4.5] (`042_*/analysis.md`, "Two references, neither neutral"). The frozen rule used the honest control, so "inconclusive" stands. But the lesson "capture is graded, not all-or-none" depends on that reference. Show both on the slide, or Neel will find it.

**"Four independent polished-flatterer training runs" (§0).** Overclaim.
- mainA/B and matchedA/B share the generator, the specs and plans, the casual-helper half of the corpus, the recipe and seed 0. Matched differs only by re-selecting the flatterer's stories among candidates for the same specs. A and B differ only in habit assignment.
- These are four runs of one corpus design, not four independent replications.
- Chain P has **no seed variance at all**, while the hd recipe's raw flip ranged from −0.05 to +0.56 across six runs (014). The ±45 effects are large enough that seed noise is unlikely to erase them. The −11.5 mirror leak, the result the frozen verdict hinged on, is exactly the size seed noise could move.
- Say: "four runs (two corpora × two assignments), one seed each; seed spread unmeasured in this family".

**sw077 numbers.** mainA +43.9 [+39.2, +48.5], mainB +42.4, matchedA +43.7, matchedB +50.4, mirror −44.8, parent −0.7, honest −3.7, honestB −6.3 and flatterer-only −3.9 all match. The keyword rate (+15.4 / −23.1) matches.
- The arc correctly uses "the conversation's Assistant voice", the one-sided control clause, the whole-voice confound and the history-voice vs reply-voice confound.
- **Two omissions.**
  1. The **exact-zero register × conduct interaction** in honestA, honestB and the parent. Joint chance ≈ 7e-4, flagged post hoc; the audit found no pipeline cause (`077_*/analysis.md`, "What it does not establish"). A red-teamer finds this in the analysis in five minutes. Put it in the limits slide or the appendix.
  2. Slide 14's seeded samples. The verifier found **3 of 10** mainA casual-agreeable replies endorse, not "two" (`overnight_landings_verified.md`, sw077). Carry the correction.

**sw076, persona switching (P22 / P23, θ̂ +0.66 / −1.08 / +1.09) and sw040 / sw044.** All match. The levels are right ("supported, one seed; duplication caveat" for sw044).

**Tony in Beat 1.**
- "His 'register beats conduct' prediction: **replicated on our protocol** (sw014, sw034)" matches the crosswalk's A11 REP, but it needs its scope.
  - sw014 and sw034 ran on **v1 scripts** (five old scenarios). sw034's own caveat is still open: "own past polish vs the register of the reply being written".
  - sw082, the held-out-scenario version, is pending. Its gate note already says a fixed casual opener removes the history register's effect, which points at the **reply's** register.
  - Write: "replicated on our protocol, old scenarios; held-out test pending".

**sw063.** "Harm is rare" is an observation. Correct.

### Beat 2: the rule, read with the habit tracer (slides 20–29)

The habit-side evidence directly tests "the habit follows the Assistant's own conduct". The levels in the table match the inventory: the sw020 (b) ladder, sw039, sw008 / sw020 (c) / sw009, sw030, sw027, sw058, sw078 (obs), and sw056 / sw062 / sw079.

**The beat's framing is the problem: "what rule decides whose conduct?" answered with the habit.**
- The arc's own §0 lists three dissociations:
  1. Tony's polished refuser's conduct transfers while its habit routing does not (sw040 θ −0.03; sw044);
  2. the mirror's conduct leaks while the flatterer loses habit routing (sw042 forecast section);
  3. forcing the habit does not bring the manner (sw022).
- A tracer that can dissociate from the quantity it is meant to trace is not that quantity's measuring instrument. It is a second phenomenon that, in hd, follows a rule of the same shape.
- The bridge slide (29) is correctly labelled interpretation and carries the counter-evidence. Good. But the Beat 2 title and the thesis treat the habit as the instrument "for" conduct, and that is the overclaim.

**sw073 (slide 28).**
- Δ values +0.011 / −0.022, +0.079 / +0.079, +0.238 / +0.098, +0.295 / +0.057 and +0.852 / +0.787 match.
- The "discriminating cell never built" point, the weather confound (60 / 64), n4's 0 / 64 keep and judge agreement 0.55 all match `073_*/analysis.md` and the verified note.
- The provenance hold (`mistakes.md` 23:00) is honoured. Correct handling.

**sw039.** "Hostile **and** declining; an apology resets it" is labelled supported (apology) with the conjunction post hoc. Correct.

### Beat 3: how it is carried, and the training-time lever (slides 30–39)

**Reply-start sufficiency (sw038 P0), induction specificity (sw038) and the own-turn signal (0.68 / 0.56 of the reply-start direction; margins +0.26 / +0.34).** Numbers match the inventory. "Causal (scoped)" is correct. Withdrawing removal specificity is correct.

**"The parent already has it" row (slide 32's header: "the untrained model already computes it").** Wrong sourcing.
- The row cites **sw052**, a direction fitted in **ctrlB0**, which is a story-trained habit-free model, not the untrained parent. sw018 showed ctrlB0's alignment came *from story training*.
- It also cites sw057, which is provisional, and sw034, which concerns Tony's pairs and the register direction.
- The clean evidence is not cited: `061_s10_training_levers/DECISIONS.md` D200. The parent's own-turn signal has held-out AUROC 1.000, and its cosine with hdA0 / hdB0's own-turn signal is 0.957 / 0.958 (mean over L16–63).
- Replace the row's sources with D200, and put the counterpoint on the same slide: the parent's **reply-start** direction is weak (sw029 ≤ 0.12; Tony C6, scored REP in the crosswalk).
- Level: decodability plus cosine for "already computes". "The routing *reads* it" is an interpretation that combines this with sw038 (edits along the organism's direction) and sw061 (the training block).

**sw061, the training block (slide 37: "removes 60 to 95 percent of conduct routing").**
- **Reference choice.** The 60% / 95% figures are drops relative to the **energy-matched random null N**, and N is *inflated* above the unblocked model O: free conduct gap N 0.680 vs O 0.541 in B; 0.783 vs 0.598 in A (`061_*/analysis.md`).
  - Against the unblocked model, the free drops are **B 50%** (0.270 vs 0.541) and **A 93%** (0.041 vs 0.598).
  - Forced: B 59% (0.270 vs 0.656), A 71% (0.246 vs 0.852).
  - The arc's header picks the more favourable reference. Use "about half (crow-helper) to nearly all (bee-helper), against the unblocked model".
- The thesis's "largely removes the routing" has two problems:
  1. the frozen primary gate **failed** (on the lean half, which was uninformative);
  2. sw080 shows the block spares the in-reply route.
  Say "removes most of the routing by the Assistant's earlier turns".
- The arc's "supported" level matches the analysis.md (one seed per arm, one null draw, A's null a near miss at 0.919). Good.
- The arc correctly carries the temperature slip (battery at T 0.7, not T 1).

**sw080 (slide 38).**
- +0.888 / +0.934 / +0.923, S/N 0.95 [0.90, 1.01] and B unscored (0.102 < 0.30) all match.
- The arc catches the discrepancy between the analysis.md interpretation and the report, and it uses the verifier's wording. This is the right call. The analysis.md's own interpretation ("removed the conduct-triggered spontaneous use of the habit", "cut the routes where the conduct is someone else's words") is not supported, because the null's free onset barely moves with the opening.
- Keep it provisional.

**sw072 (slides 34–35).**
- −M returns mainA's flagging 0.400 → 0.822 (parent 0.793) and N's declines 0.192 → 0.056; −C1 removes 69–88%; the booster figures match (`072_*/analysis.md` l.61–81).
- "Where the habit lives, not where the choice is made" is correct.
- Calling the late crow push a post hoc lead is correct. Keeping the conflict with the parent's crow preference (exploration P(crow) 0.80) visible is right.
- Tony's booster "replicated on our protocol (sw072)" is fine **as an observation**. The crosswalk scored C3 as PART before sw072 landed. Say "the observation replicates; the explanation is post hoc".

**sw043 / sw064 (slide 39).** Numbers match: 0.898 → 0.082; 1.00 / 0.99 / 0.99 and 0.91 / 0.91 / 0.87; conduct gap 0.06–0.19; hostility 8.7 vs ≈ 2. Told well.
- **Placement.** sw045 (authorship) is bundled into the redirect slide. Authorship is a "what rule decides" result: the default maps characters onto itself from story content, not from who wrote it. It belongs in Beat 2, or on the measurement and setup slides, where it pre-empts the obvious "it's because the stories are Assistant turns" objection.

### Beat 4: replication and prediction (slides 40–43)

- sw055 (10 / 12), sw070, sw050, sw014 / sw034 / sw036 and the forecast failures all match the inventory.
- sw036 (θ −0.28, not scored) is correctly labelled descriptive.
- The prediction slide is honest: no forecaster beats the trivial rules, and sw074 is pending.

---

## 2. List of overclaims (ranked)

1. **The thesis says the Assistant takes after the character "whose *conduct* its own turns resemble". In the flattery models, voice decides and conduct barely matters.**
   - In sw077, the register contrast is ±42–50 points. Candid-vs-agreeable conduct in the turns is +10 to +27 in main, and in mirror's polished cell it is null (−2.4 [−5.8, +0.9]).
   - In sw042, register-cueing personas switch both habit and conduct.
   - So the flattery result says "voice", while the hd habit result says "hostile and declining conduct, read from content plus register" (sw039, sw078).
   - The overnight-verified note already gives the unifying word as **voice**, and flags it as an interpretation.
   - Rewrite the thesis around voice. As written, the thesis contradicts its own Figure 1.
2. **"A judge-free habit tracer shows the rule behind this kind of transfer."** This states an interpretation as a finding.
   - Habit and conduct dissociate in three places (overclaim 1's list; the arc's own §0).
   - The up-to-speed note already recommends that "takes after whichever character it resembles" stay an interpretation, not the headline.
3. **"Cut … by about 47 points"** (thesis, slide 1). This is against the honest-story control. Against the untrained model it is −39.6 [−43.8, −35.2] (sw042).
4. **The mirror "leaked 12 points"** (slides 12 and 19). Against the parent it is −3.8 [−7.8, +0.3] on all replies (sw042). The "graded capture" lesson depends on the reference; show both.
5. **"Four independent polished-flatterer training runs" (§0, slide 19).** The four share specs, plans, the helper half, the generator and the seed. Chain P seed spread is unmeasured.
6. **"Removes 60 to 95 percent of conduct routing" (slide 37); "largely removes the routing" (thesis).**
   - The percentages are relative to an inflated random null. Against the unblocked model: B 50%, A 93% (free).
   - The frozen gate failed, and the in-reply route is spared (sw080).
7. **"The untrained model already computes it" (slide 32), sourced to ctrlB0 (sw052) and provisional sw057.**
   - ctrlB0 is not the parent.
   - Use sw061 D200 (AUROC 1.000; cos 0.957 / 0.958).
   - Say it is the own-turn signal, not the reply-start direction, which training built (sw029, sw010 (d)).
8. **Tony's "register beats conduct: replicated on our protocol".** The scope is v1 scripts. sw034's own-vs-reply-register caveat is open, and pending sw082 hints at reply register.
9. **Neel's-guess slide: "the signal predates training"** is unqualified (see 7).
10. **Missing corrections the arc should carry:** sw077's exact-zero interaction coincidence, and sw077's samples (3 of 10 endorse, not 2).

Nothing in the arc states Tony's protocol-only results as replicated. The crosswalk statuses are carried faithfully: A7 PART with a CON sub-claim, A8 CON, C5 removal CON, C7 TEN, B1 HIS. I found **no number that disagrees with its primary file**. Every issue above is a reference choice, a scope word or a wrong source.

---

## 3. What is missing

**Required overnight results.** All present:
- sw077 (Figure 1, slide 16);
- sw072 (34–35);
- sw073 (28, held);
- sw061 G1 + sw080 (37–38);
- sw043 / sw064 (39);
- pending slots for sw071, sw074, sw080 write-up, sw081 and sw082 (§5), phrased as questions with no pre-written verdicts. sw082's gate note is quoted as "on record, not a result", which is the right handling.

**Failures that changed direction.** All in the main story: the Axis and persona-geometry null; the sparse-autoencoder and natural-scale steering nulls; Kimi-prose damage and the replay hidden habit; seed variance; random controls matched on the wrong quantity; the crow-biased readout; sw021's forced failure; the redirect turning out to be a default swap; G1's lean gate; sw073's "mixed"; the band map. Each is told as tried / why / happened / taught / next. This is the arc's best feature.

**Decision points.** D1–D9 is a good table.
- **Missing decision:** why Chain P was built at all. That is, why we left "one organism, deep" (Neel's ask) for a new family. The honest answer (Tony's register pairs showed "the helper wins" is not universal, and S9 asked whether conduct can be predicted) is a decision point Neel will ask about.

**Tony beside ours.** Present in every beat with protocol caveats: his crow-biased readout, per-layer matched random arms, old scenarios, his unvalidated held-out-scenario judge, no red team after B10. The credit question for 005 is raised. Good.

**Measurement slides.** Models and naming (slide 7, §9 table) and how we measure (slides 8–9) are present.
- **Missing from measurement:** the two references for Chain P (parent vs honest control) and why neither is neutral. The arc needs this on slide 10 for overclaims 3 and 4 to be fixable.

**Explicit claims.** The arc says slide 3 "states the three claims" but never writes them out. Neel's advice starts with deciding the 1–3 claims. Write them on slide 3, each with its level and its boundary, as the up-to-speed note does.

**Answer to Neel's literal question.** "Why does the plain default show the helper?" gets slide 28, which is held. Missing:
- **Chain P is itself a direct test of his guess ("helpfulness present → helpful habit"), and the guess fails there.** In main, the default takes the polished *flatterer* over the casual *honest helper*: θ̂ +0.66, flag rate 40% vs the honest control's ≈ 88%.
- sw056 adds that the helper lean exists with no reply at all (helper 0.82).

This is the arc's strongest available answer to his question, and it is not stated as such.

---

## 4. The single strongest attack, and whether the arc survives

**Neel:** "Your thesis welds two findings together with the word 'resemble', and the welds don't hold.
- In the flattery models, the turns' *voice* decides and their conduct barely matters (sw077: mirror's polished candid-vs-agreeable is null).
- In the bee/crow models, *hostile and declining conduct* decides.
- You couldn't say in advance which feature 'resemblance' would key on: your frozen forecast lost to 'polished wins' (sw042), and nothing beats the trivial rules (sw040).
- Your tracer and your conduct readout come apart in three places (N/NB, the mirror leak, sw022).
- Every causal and training-time handle (the own-turn signal, the block, the band map) is on the habit. The one intervention that touched flattery (the band mask) was not band-specific.

So what you have is two things:
1. a well-controlled replication of the paper's style-cued persona selection, now cued by the conversation's Assistant voice, applied to flattery;
2. a separate, decent behavioural and causal-influence study of an animal-fact habit.

The 'rule behind this kind of transfer' is a post hoc word, not a finding. And you led with the half that doesn't answer the question I asked."

**Does the arc survive?** As a talk, yes. As the thesis currently reads, no.

**What survives:**
- sw077 stands on its own as a supported behavioural result. The opposite signs in main and mirror, with the parent and honest models flat, rule out a register-sensitive judge and a "casual is candid" effect, and sw076 backs the judge.
- The habit work stands on its own: supported behavioural rules on held-out scenarios; causal influence with size-matched induction controls; a supported training-time block.

**What does not survive** is the implied single chain "flattery ← rule ← signal ← block". The arc's §7 answer concedes this ("we do not claim shared machinery"). The fix is in the framing:
1. **Thesis:** "Stories can hand a character's conduct to the Assistant, and the conversation's Assistant voice decides which character is played (flattery, ±45). In a second model family with a forcible, judge-free tracer, the analogous rule reads the Assistant's own earlier conduct through a signal the untrained model already encodes, and blocking that signal during training removes most of the routing by earlier turns. Whether flattery uses the same signal is the open experiment."
2. Make the closing experiment (the block during Chain P training, plus a placement control for sw077) the last main slide, not slide 45 of 45.
3. On slide 4, say explicitly that Chain P refutes "helpful wins" as a universal rule.

With those changes, Neel's attack becomes the talk's stated open question rather than its hidden flaw.

---

## 5. Scores (1–10)

| Dimension | Score | Why |
|---|---|---|
| Evidence strength | 7 | Beat 1 and the habit rule are supported; Beat 3 is causal (scoped) plus a supported training block. The thesis-level link is interpretation, and three headline numbers use the favourable reference. |
| Causal-chain clarity | 5 | The arc admits the chain breaks at the bridge, but the thesis and the slide order present a chain. "Conduct" vs "voice" is inconsistent across the two halves. |
| Honesty about limits | 8 | Exceptional limits slides, discrepancy list, provisional handling and a two-sided control reading. It misses the reference choices (−47 / −11.5 / 60–95%), "independent runs", the ctrlB0-as-parent sourcing and sw077's exact-zero interaction. |
| Memorability | 8 | The crossover Figure 1 and a safety hook are memorable. Forty-five slides in four beats, with the mechanism on a different behaviour, dilutes it. |
| Coverage of required items | 9 | Every required result, pending slot, failure, decision table, Tony status and measurement slide is present. Missing: the three claims written out; the parent-vs-honest-reference slide; the "why Chain P" decision. |
| Failures in main story | 9 | All eleven rule-listed failures are told in full, with what we did next. |

---

## 6. Ideas another arc should graft

1. **sw077's crossover as Figure 1.** Show five model types with casual and polished history, and the no-history flag rates as markers. One takeaway: the same voice change has opposite effects depending on which character the stories made polished, while untrained and honest models stay flat. Any arc can use it, even as a mid-deck payoff.
2. **The claims slide that says outright "every internal result in this talk is about the animal-fact habit".** Pair it with a bridge slide labelled *interpretation* that carries its counter-evidence (N/NB, the mirror leak, sw022) on the same slide. This is the honest way to connect the two halves in any arc.
3. **"How verdicts changed as controls improved" as one slide.** It covers the self-cancelling random controls, cumulative-size matching, removal specificity withdrawn and the sw021 forced failure, with Tony's per-layer-matched arms flagged on the same slide. It turns a list of corrections into a methods lesson.
4. **The closing experiment that would make the bridge causal.** Block the parent's own-turn signal during Chain P training, with an energy-matched random arm, and run sw077 with a placement control (the same casual text as a user turn or a quote). Also graft one argument: **Chain P as the cross-family test of Neel's guess.** The default takes the polished flatterer over the casual honest helper, so "helpfulness present → helpful habit" is not a universal rule.
