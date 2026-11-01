# Adversarial review of the Detective arc (Neel's view)

_ideation-12 (Claude Code), read-only reviewer. This file is the only output. No experiments, no paid calls, no subagents, and no Tony code was run. Tony's material is summarised from our private verification note (`PC` = `…/2026-10-31_ideation-12_cc_inventory_parts/C_tony_verified_PRIVATE.md`) and stays local._

**What was judged:** `…/2026-11-01_ideation-12_cc_slide_material_parts/arc_detective.md`, read in full (437 lines, 45 headers).

**Checked against primary files, not the arc's prose:**
- the `analysis.md` of sw020 (§4b table), sw023 (§3), sw029, sw032 (§1–2), sw039 (Part 2 verdict block), sw057 (c1/c2 corrected 1 Nov, lens), sw061, sw072, sw077 (full, including the secondary contrast), sw080 (landed 23:3x, blind recompute matched), sw081 (empty template) and reproduction/001;
- the folders of sw071 / sw074 / sw082 (no analysis.md in any of them);
- `things to throw away/executor exploration 2026-10-28/RESULTS.md` (X0, X2, X9);
- `mistakes.md` headings and the sw072 / sw073 / sw043 entries;
- the verified notes `…_cc_overnight_landings_verified.md` (OVN) and `…_cc_inventory.md` (INV), and `PC`.

Path shorthand: `SW` = `/workspace/Neel Sprint/experiments/sprint_work/`.

---

## 0. Verdict in one paragraph

This is the most complete arc on coverage. Every failure the user listed sits in the main story, each told as tried / why / happened / taught / next. Every pending experiment has a question-only slot, and the decision table is the best I have seen. Almost every number matches its source.

Its frame is also its main liability. "Of nine suspects only one survives" promises a solved case, and the arc's own suspect board does not support it:
- three suspects survive as accomplices or correlates (the Axis, quoted words, the crow push);
- the strongest competitor, **register**, is not on the board at all;
- the experiment the arc calls "a forward test of the culprit" (sw077) crossed register with conduct inside the Assistant's turns, and register won by a factor of about two to four. The arc does not report the conduct half.

Five headers state post hoc or provisional readings as findings: 25, 34, 35, 38 and 41.

The arc survives Neel's strongest attack (§3) only if three changes are made:
- the culprit is renamed from "own conduct" to "the Assistant-voiced turns' resemblance to a trained character, in register and conduct";
- register is added as a suspect, or merged into the culprit;
- the scoreboard's summary sentence drops "only one survives".

---

## 1. Beat by beat: does the evidence directly test the beat, at the stated level?

### Beat 0: the scene and the instruments (slides 1–8)

**Direct and at the right level.**
- Reproduction: flip +0.45 [+0.34, +0.56] and +0.475 [+0.37, +0.57] (`reproduction/001_hd_organisms/analysis.md` l.13–14).
- Readout skews:
  - "By the way," leans toward the helper 2.32× per story (`SW/032_*/analysis.md` l.19);
  - "American" follows the bridge in 938 / 1,152 bee-helper "Random animal fact" replies (`SW/068_*/analysis.md` l.69);
  - the log-prob readout was not adopted, ρ 0.714 / 0.638 (`SW/032_*` l.39).
- The crow-biased-readout story is the right failure to put first, because it explains why free replies decide.

**Gaps.**
- Slide 7 says "label with keywords and two judges". The project rule is two logprob-weighted judges from different families, with agreement and consensus reported. Say so once on this slide, and point to judge validation in a backup slide.
- The "units of replication" line is missing: one training run per assignment for almost everything, and seeds are not replicates of evaluation draws. It belongs on slide 7 or 8, not scattered.
- sw032 §1 also says "Most no-trigger default cells have < 20 habit-bearing replies" (l.11). That is a measurement limit on the mystery itself, and it should sit on slide 8 or slide 9.

### Beat 1: the mystery, and the early favourites fall (slides 9–16)

**The crime (§2).**
- The numbers match:
  - bee 12.5% vs crow 3.5%, and crow 12.5% vs bee 0% (001 l.13–14);
  - 0.175 / 0.140 at 2,048 tokens (sw013);
  - +0.078 / +0.084 on the new set (sw020 (a)).
- **Overclaim:** §2 gives the crime's level as "supported … 10 of 12 runs carry the related routing; sw055". sw055 measures the **conduct gap** (routing after dismissive vs helpful histories). It does not measure the default lean. The lean has not been measured across the reruns on the new set.
  - Restate as "supported for the two main models (001, sw013, sw020 (a)); seed dependence of the lean itself not measured on the new set".
  - Add that the seed-2 crow-helper run has no flip at all (014).

**1a damage / replay and 1b seeds.** Direct, correctly levelled, decision points shown. Keep them.

**1c, suspect 1 (global Assistant-ness).** The scoped negatives are stated well:
- the axis cosine is ≈ 0.96 in the habit-free control too;
- steering was inert at natural size;
- the sparse autoencoder found no sparse concept.

**Overclaim / honesty gap (header 15).** "The Assistant-Axis coordinate still predicts which personas route to the helper, but as a correlate **that conduct partly explains**" inverts sw075's frozen verdict, which was **"persona carries more"**. The Axis adds partial +0.50 / +0.78 beyond five conduct fields (OVN sw075).
- The verifier's caveat is right: the Axis sees the role prompt and the voice, while the judges saw only the turns.
- But the header has to name the frozen verdict and then give the caveat. Leaving it out is the "silently softened verdict" pattern.
- Suggested header: "The Assistant-Axis coordinate predicts the persona map beyond five judged conduct fields, which shows those fields are incomplete, not that persona beats conduct."

**The thesis vs 1c, an unreconciled tension.** 1c uses sw010 (d) to clear suspect 1: the parent's chat-fitted conduct direction does no better than cosine-matched random directions (0.155 / 0.167). sw029 adds that the parent's header direction induces ≤ 0.12 (`SW/029_*/analysis.md` l.31, l.76). Beat 4d and the thesis then say "a signal the untrained model already computes". Both can be true, because the sites differ:
- the parent's **own-turn** coordinate is decodable (sw057 AUROC 1.0, "text-level decodability");
- the parent's **header** direction is causally inert in the organisms.

The arc never says this. Neel will ask which one is true.

**1d pivot.** X4 / X8 are the right evidence. X8 is blind-recomputed.

**Tony B2** is correctly marked: the control null REPLICATED, and "the Axis predicts nothing" CONTRADICTED at the role level (PC row B2).

### Beat 2: eliminating the behavioural suspects (slides 17–25)

**Suspect 2, helpfulness (Neel's guess).**
- The ladder numbers match `SW/020_*/analysis.md` §4b exactly (0.011 / 0.050 / 0.211 / 0.339 / 0.462 / 0.868; contrasts +0.237 / +0.199).
- The bee-helper ordering failure (deflection 0.432 > rude-but-helpful 0.397) is carried beside it. Good.
- Minor:
  - header 17 says a rude-but-helpful Assistant "routes to the rival". Its share is 0.462, so say "routes about half the time";
  - "curt ≈ helpful" fails narrowly on free pooled replies (+0.038 [0.007, 0.070], sw020 §4b), so say "near helpful".

**Suspect 3, persona identity.**
- Supported.
- The arc correctly notes that sw030's frozen label was "STORED SELF-CONCEPT" and that it over-reads.
- Header 19, "costumes and hidden attitudes do not move the habit", should say "stay below the 0.3 bar; equivalence to zero shown in 9 of 24 cells", since the arc's own body says that.

**Suspect 4, hostile words.**
- The user ≈ 0 result is supported (sw009, sw020 (d)).
- The quoted-words share is an observation (sw056, sw079).
- Correctly levelled in the body.

**Suspect 5, role label: overclaim in header 21.** "The same text routes under the user label as under the Assistant label" holds for the bee-helper model (0.24 / 0.23). It does not hold for the crow-helper model: 0.41 under the assistant label vs 0.21 under the user label, a role effect of 0.15 of the positive control. The ledger says "hdB0 partly also reads the label". Say "mostly the same in the crow-helper model, identically in the bee-helper model".

**Suspect 6, template, and suspect 7, authorship.** Direct and supported. The calibration line on authorship (the docx predicted a 30–60% cut, and so did we) is well used.

**Suspect 8, animal preference: header 25 overclaims.** "A late-layer push toward crow is an accomplice in the difference between the bee-helper and crow-helper models" states the crow-identity reading as found. Per `SW/072_*/analysis.md` l.79–88:
- the crow reading is "post hoc; a recurring pattern, not a supported claim";
- the analysis names an "equally good alternative": the parent defaults to bee and the late LoRA overrides it.

Two further problems the arc does not carry:
- **The bands are matched on layer and module count, not on update norm, and there is no random band** (OVN sw072). A layer-56–63 zeroing is not a targeted crow intervention.
- **The parent-preference evidence contradicts itself across readouts**, and the arc lists the pieces side by side without saying so:
  - X2: parent P(crow) 0.80 under free choice (`EX` l.74);
  - sw023: parent forced choice L_tot −0.02 (no preference) and open completions +1.93, i.e. bee-leaning (`SW/023_*/analysis.md` l.95–97);
  - X0 AUDIT-1 (same EX file, l.75): "the trained organisms show no crow dominance at seed 0" (B − A leak gap −0.04 [−0.10, +0.02]). The arc leaves this out, and it weakens the accomplice reading.

Header 25 should read: "Zeroing the last eight layers lowers crow in every organism whatever its role, a post hoc lead on the bee-helper vs crow-helper asymmetry with an untested parent-bee alternative."

**Tony C3.** "The band location was his protocol only until sw072" implies that sw072 replicated the band location. PC marks the band location HIS. sw072 replicates "crow falls when 56–63 is zeroed" on our readouts. It does not replicate "a booster always goes to one fixed member", because the identity reading is post hoc. The fixed crow lean itself is REP via sw023 (l.101).

### Beat 3: the culprit (slides 26–31)

**3a, own generated turns.**
- Direct and supported (sw015, sw027).
- The writer correction (parent-written rude turns route slightly more, −0.085 / −0.104) is beside it. Good.

**3b, turn-1 reply in progress.**
- Direct, frozen PARTIAL (sw056); the bee-helper vs crow-helper asymmetry recurs across three runs (sw062). Correctly levelled.
- Tony A10 REP and C13 CON match PC.

**3c, quoted dose: overclaim in header 28.** "Quoted dismissive words carry a quarter to a third of the effect, **so the model reads voice**, not authorship bookkeeping."
- sw079's frozen verdict is NOT GRADED, and sw079b is provisional (INV).
- The share is an observation. "So the model reads voice" is the arc's synthesis (it says level 6 in 3e), and a header cannot carry it as a conclusion.
- Suggested header: "Quoted dismissive words already carry a quarter to a third of the effect."

**3d, 10 of 12 runs.**
- Supported, one run each.
- Header 29 should add "on the forced readout for the replay models": their free onset is 0.00–0.19 (sw055 ledger).

**3e, voice as the unifying word.** Stated as interpretation. That is right, but the arc misreads its own sw077 evidence for it (see beat 5 and §3).

**3f, case still open (slides 30–31).**
- The best-placed honesty in the deck. sw073's numbers match OVN.
- The provenance block is flagged, and so is the unbuilt discriminating cell. Slide 31 states plainly that the lean is "consistent with, not shown to be computed by".
- Two problems:
  - §9 Answer 1 leans on sw073 (reporting blocked) and on the sw057 lens (not recomputed) as "consistent results". Those cannot carry an answer to Neel until the block is lifted and the lens recomputed.
  - Slide 30's header makes the deck's literal answer to Neel's question depend on a blocked result. Mark it "pending the user's ruling" in the header, not only in §11.

### Beat 4: how the culprit operates (slides 32–40)

**4a, header sufficiency.** Direct and causal (sufficiency), with the sw006 correction beside it. Good.

**4b, controls corrected.** Excellent. This is the strongest "corrections" slide of any arc:
- the cumulative-offset diagnosis (MIST 30 Oct 13:45);
- sw021's forced failure;
- sw028 induction holding only in the bee-helper model (PD error 3);
- removal withdrawn on the new set (sw038).

**4c: overclaim in header 34.** "The **decisive** signal sits upstream … editing it induces the rival habit as **a graded dial that saturates** near the natural gap."
- sw039's frozen readings: "DIAL: not met in either model"; "SATURATES: not met" (`SW/039_*/analysis.md` l.94–95). "Graded then plateau" is the labelled post hoc plain reading (l.101).
- "Decisive" is not supported:
  - the own-turn edit moves 0.56–0.68 of the header swap (sw038);
  - sw057 c2, corrected after its 1 Nov blind recompute, says the own-turn signal's within-condition prediction "is weak and changes sign across organisms; in hdA0 it is reversed", while "d_self predicts it better … in every arm" (`SW/057_*/analysis.md` l.12–13).
- That correction is not in the arc at all, and it belongs beside this claim.
- Suggested header: "A conduct direction at the Assistant's own earlier turns, fitted before the prohibition, induces the rival habit specifically, at about 0.6 of the reply-start edit."

**4d: overclaim in header 35.** "The untrained model already **reads** this signal as conduct, and training hooks the habit onto it."
- Evidence, all of it short of the header:
  - text-level decodability in the parent (sw057 AUROC 1.0);
  - an oracle lens, an untrusted instrument whose positive control failed at L32 / L42 and passed only at L52, with a post hoc parent-only control, and which was not recomputed (`SW/057_*` l.17–20, header line);
  - sw034's register direction in Tony's pairs (a different site and family).
- "Reads" in the sense of "uses" is not shown, and the parent's header direction is inert (sw029).
- "Training hooks the habit onto it" is G1's level-6 interpretation.
- Suggested header: "The untrained model already encodes the Assistant's own-turn conduct, and blocking that coordinate during training removes most learned routing (interpretation: training learns to read it)."

**4e, band map.** A model "failure told as lesson" slide. It is correctly scoped as "expression, not choice", with Tony credited.

**4f: header 37 overreaches.** "The reply-start route is inert" in sw037 refers to the rank-1 header direction (0.03) in one replay organism on the forced readout. It does not refer to the reply-start state. The same experiment says the crow-helper seed difference sits in the header state at L32–63, and that seed-2 routes via the header direction on free replies. Say "the reply-start direction is inert in the replay model".

**4g: overclaim in header 38.** "The habit comes first, the character binding next, and routing by the Assistant's conduct last, and stories in context alone **never** produce self-application."
- sw060's frozen verdict is **"order not claimed"**; the bee-helper lean half-time is non-monotone, CI 21–97 (ledger sw060).
- The sequence is the descriptive half-time reading. That reading is defensible as "consistent with", but it cannot appear as the header without the frozen verdict beside it.
- "Never" generalises sw059 beyond k ≤ 64 stories, two renderings and one model.

**4h, G1.** The numbers match `SW/061_*/analysis.md` (drop 60% [47, 73] and 95% [90, 99]; S/O 1.004), and the failed frozen gate is in the header. Good. The temperature-slip correction is carried. Two problems:
- **Overclaim in the proposed slide wording "history route blocked; in-reply route spared".**
  - In the crow-helper assignment the history route is 60% reduced (free) and 53% (forced). That is "mostly", not "blocked".
  - "In-reply route spared" rests on one assignment (crow-helper unscored: N 0.102 < 0.30), on the forced readout, near ceiling. At the softer polite-refusal opening S routes about half as much (post hoc, OVN sw080).
  - Say: "In the bee-helper model, the clamp spares forced routing by a strongly dismissive reply in progress."
- The arc's sw080 line misses part of sw080's own analysis (`SW/080_*/analysis.md`, "Other routes"): user-side 0.13 vs 0.42 and quoted 0.15 vs 0.37, both weaker in S. The analysis reads this as "cut the routes where the conduct is someone else's words". The verifier reads it as onset failing generally in S. That is a second open discrepancy, and it belongs next to the one the arc already lists.

**4i, redirect.** Direct and observation-level. The sw043 omission and the untraced "36%" (MIST 31 Oct 18:47, verified to exist) are carried. The best version of the "a rule can pass without the mechanism" lesson.

### Beat 5: the payoff, flattery (slides 41–43)

**Header 41 overclaims.** "**The same rule reaches conduct**: stories with a polished flatterer make the Assistant flag 47 points fewer planted flaws."
- sw042 measures conduct *capture*, not the rule, and its frozen verdict is **inconclusive**: the mirror's −11.5 breaks the "no capture" clause.
- Suggested header: "Stories with a polished flatterer make the plain Assistant flag 47 points fewer planted flaws (frozen verdict inconclusive: the mirror's casual flatterer leaks a quarter)."

**5b, sw077: the most consequential omission in the arc.** The arc reports the register contrast (+43.9 / +42.4 / +43.7 / +50.4; mirror −44.8; parent −0.7; honest −3.7). All of it matches `SW/077_*/analysis.md`, with the verifier's "own untested" and "one-sided" caveats beside it.

But sw077 is a 2 × 2 of **register × conduct** (candid: corrects the user's slip; agreeable: goes along) inside the same Assistant turns, and its secondary result (`SW/077_*/analysis.md` l.62–79) is:
- candid − agreeable at the same register is +12 to +20 overall (mainA +18.2, mirror +12.1);
- at the non-matching register it is +10.0 (main casual) and −2.4 [−5.8, +0.9] (mirror polished);
- the analysis's own summary: "candour in the Assistant's own turns restores flagging mainly when its register matches the flatterer's".

So, in the experiment the arc calls "a forward test of the culprit [own conduct]", **the voice of the earlier turns moved conduct about 2–4× more than their conduct did**, and conduct mattered mainly when the voice already matched the flatterer. Calling sw077 confirmation of an "own-conduct" rule is wrong. It confirms a **resemblance-to-the-trained-character** rule, in which register is the dominant cue in a register-distinguished pair. The agreeable histories are also judged less helpful (4.8 vs 6.3), a confound the analysis notes.

**5c, conduct without habit.** Good, honest complication (sw040, sw044, sw036). Tony A11 REP is correct. The pending sw082 slot is right.

---

## 2. Full overclaim list (claim above its evidence level, post hoc as found, provisional as established, sensitivity as primary, wrong number)

1. **Slide 2 / thesis: "of nine suspects only one survives".** The arc's own board keeps three alive:
   - suspect 1, a correlate that adds beyond conduct (sw075 frozen "persona carries more");
   - suspect 4, quoted words carry 0.2–0.3 (sw056, sw079);
   - suspect 8, the crow accomplice.

   Register, the competitor that wins in two families (sw014; sw077 secondary), is not on the board.
2. **Thesis: "a signal the untrained model already computes and that story training learns to read".** Decodability plus an unrecomputed lens plus G1's level-6 interpretation, stated as fact. It is also unreconciled with sw010 (d) and sw029 (the parent's header direction is inert).
3. **Header 34: "decisive" and "a graded dial that saturates".**
   - Both frozen readings, DIAL and SATURATES, are not met (sw039 l.94–95).
   - The sw057 c2 correction says the own-turn signal predicts the decision weakly and in reverse in the bee-helper model, while the header direction predicts it better.
4. **Header 35: "already reads … training hooks".** Decodability and an untrusted, unrecomputed lens, stated as use and mechanism.
5. **Header 25: crow push "is an accomplice".**
   - Post hoc (sw072 l.79), with an "equally good" alternative.
   - Bands not norm-matched, no random band.
   - X0 shows no crow dominance at seed 0; the parent's preference flips across readouts (X2 vs sw023).
6. **Header 38: training order stated as found.** sw060's frozen verdict is "order not claimed"; "never" over-generalises sw059.
7. **Header 41: "the same rule reaches conduct"** rests on sw042, which tests capture (frozen inconclusive), not the rule.
8. **§9 Answer 2 and 5b: sw077 as "a forward test of the culprit … passed".**
   - It passed one-sided only (honestB −6.3 [−9.9, −3.0] fails two-sided).
   - "Own" is untested.
   - Its conduct arm moved flagging far less than its register arm.
9. **§2: the crime's level supported by "10 of 12 runs (sw055)".** sw055 measures the conduct gap, not the lean.
10. **Header 15: sw075's frozen verdict ("persona carries more") is softened to "a correlate that conduct partly explains"** without naming the verdict.
11. **Header 21: "the same text routes under the user label".** False for the crow-helper model (0.41 vs 0.21; role effect 0.15 of the positive control).
12. **Header 28: "so the model reads voice".** sw079 frozen NOT GRADED; sw079b provisional; an inference written as a finding.
13. **Proposed G1 slide wording: "history route blocked; in-reply route spared".**
    - The crow-helper history route is cut 53–60%, not blocked.
    - "Spared" rests on one assignment, the forced readout, near ceiling, and halves at polite refusal (post hoc).
    - sw080 is one run per arm, one null draw, with a partial judge audit.
14. **Header 37: "reply-start route inert".** Only the rank-1 header direction, in one replay organism, on the forced readout.
15. **Header 29.** The replay organisms' routing is forced-readout only (free onset 0.00–0.19).
16. **Header 17: "rude but helpful routes to the rival".** Its share is 0.462, about half.
17. **Prediction-miss line: "turn-1 header ≤ 30% → it carried the whole gap" (sw030).** The crow-helper model's share is 0.62 of a 13-row gap (ledger sw030 "fragile"). Say "most of the gap".
18. **Tony C3: "band location his protocol only until sw072".** This implies replication of the band identity. sw072 replicates the crow drop on our readouts; the booster-identity reading stays post hoc, and PC marks the band location HIS.
19. **§9 Answer 1** counts sw073 (reporting blocked) and the sw057 lens (not recomputed) as consistent evidence for the default lean.

**Numbers that do not match their source:** none found among roughly 60 spot-checks. Two notes:
- sw072's booster Δ is quoted from the agent's paired 49-scenario set (−0.459 / +0.316). The blind recompute on all 64 gives −0.455 / +0.337 (`SW/072_*` l.8). Either is fine if the set is named.
- sw078's label effect is 0.004 in INV and 0.01 in the arc (rounding).

---

## 3. What is missing

**Required overnight results.** All present: sw077 (5b), sw072 (25, 36), sw073 (30), sw061 G1 + sw080 (39), sw043 / sw064 (40). The arc correctly treats sw080 as landed (its analysis.md exists, with a matched blind recompute) rather than as OVN's "no analysis yet". Missing pieces:
- **sw077's register × conduct secondary contrast** (§1, beat 5). Required, because it bears directly on the culprit's name.
- **sw057 c2's 1 Nov correction** (the own-turn signal reversed in the bee-helper model; the header direction predicts the decision better). Required beside slides 34 and 35.
- **sw080's second discrepancy** (user-side and quoted routes weaker in S: compartment reading vs onset failure).
- **The frozen verdict names**: sw075 "persona carries more", sw060 "order not claimed", sw039 DIAL / SATURATES not met. Each belongs beside the post hoc reading the arc uses.

**Pending slots.** All five are present, with question-only wording: sw071, sw074, sw080 (in its disputed reading), sw081 and sw082. I checked the folders: sw071 / sw074 / sw082 have no analysis.md, and sw081's analysis.md is the empty template. Good.

**Failures that changed direction.** All eleven listed in the user's rules are in the main narrative (the arc's §5 table, with slide numbers). This is the arc's best property.

**Decision points.** A twelve-row table with alternatives (§6). Add one row:
- **naming the culprit:** "own conduct" vs "register" vs "resemblance to the trained character". The alternatives, the evidence (sw014, sw077, sw078, sw003 C) and why we chose.

**Tony beside ours.** Done on most beats with REP / PART / HIS / CON / TEN markings that match PC (A2, A3, A7, A8, A9, A10, A11, B2, C2, C5, C6, C7, C13). Two fixes:
- C3's wording (above);
- C1 (header carries the switch; REP coarse) is not shown beside 4a, although it is the most direct REP.

**Measurement slides.** Present: models and naming (5), a real story (6), how we measure (7), the four quantities (8). Missing on these slides:
- the units-of-replication line;
- the two-family, logprob-weighted judge rule;
- sw032's "< 20 habit-bearing replies in most no-trigger default cells".

**Other.**
- **What is new against the source paper** is only a note (§11). It needs one main slide. Neel's first question about a write-up is novelty, and resemblance, style effects and persona switching are already in Cocola et al.
- **A table mapping Neel's three asks to answers** (signatures, Axis prediction, characterise the Assistant), plus the 28 Oct question. The detective spine implies it, but a slide that states it outright saves him the work.

---

## 4. Neel's single strongest attack, and whether the arc survives

> **"Your culprit is misnamed, and the one experiment you call a forward test says so.** You list nine suspects. Register is not among them. In Tony's pairs register beats conduct (your sw014, and sw034's working direction is the parent's own register direction). In your flattery models you crossed register with conduct *inside the same Assistant turns* (sw077): the voice of those turns moved flaw-flagging by 42–50 points, while their conduct, at fixed voice, moved it by 10–26, and by about zero for the mirror at the polished voice. In the bee/crow pair the 'conduct' that routes is hostility, which is exactly how the dismissive character talks. Your only content-vs-register split there (sw078) is 28 scripts with half the rewrites failing their check, and it is null in the crow-helper model. So across three families, what decides which character the Assistant takes after is how much its turns resemble a trained character, on whatever distinguished the characters in training. 'Own conduct' is what that looks like in the one pair where conduct and register are confounded. 'Voice' is an umbrella you put up after the fact to cover conduct, register and quoted words. Tell me a result that would have refuted it."**

**Does the arc survive?** Partly. The core finding survives; its name and its "solved case" frame do not.

**What survives:**
- The persona label, role tag, template, authorship and the hostile user are all cleared by direct tests (sw030, sw058, sw024, sw045, sw009 / sw020 (d)). What decides it is the text of the Assistant-voiced turns in the conversation.
- That holds across 10 of 12 runs (sw055), at turn 1 (sw056), and for conduct as well as for habits (sw077).
- Content does add beyond register where it was tested:
  - bee-helper model: content 0.33 vs register 0.17 of the positive control (sw078, observation);
  - Chain P: candour adds +26 / +27 at the flatterer's own voice (sw077 secondary).

**What does not survive:**
- "Own conduct" as the culprit's name;
- "only one survives";
- the claim that sw077 confirmed a conduct rule.

**The repair, which is also the falsifiable version Neel asks for.** It is already in the evidence (sw003 Part C: "the recipient map tracks the feature that distinguished the trained characters"; ledger sw003), and it makes a prediction:
- in a register-distinguished pair, register should route and conduct should matter mainly at matching register (sw077: yes; sw014: yes);
- in a conduct-distinguished pair, conduct should dominate. The hd pair half-confounds this; sw078 is weak support.
- sw071 / sw074 can score this across about 53 organisms, which makes it the right "pending question" for the close.

**The second attack the arc already anticipates:** "you explained the switch, not the default". It is handled honestly on slides 30–31, and the suggested intervention test (a turn-1 own-turn edit at no history against equal-cumulative random edits) is the right next step. Do not let §9 Answer 1 lean on blocked or unrecomputed evidence.

---

## 5. Scores (1–10)

| Dimension | Score | Why |
|---|---|---|
| evidence_strength | 7 | The cited evidence is almost always the most direct test available, and the numbers match their sources. Points lost for five headers above their level and for using sw077 as confirmation of the wrong variable |
| causal_chain_clarity | 6 | The "what switches it" chain is clear (behaviour → own-turn signal → training-time block). The link from culprit to Neel's actual question (the default lean) is explicitly broken. "Voice" absorbs conduct, register and quoted words without a falsifier |
| honesty_about_limits | 7 | Corrections stand beside the claims, there are two open-case slides, failed frozen gates appear in headers, and the corrections list is long. Lost on the softened sw075 verdict, the missing sw077 conduct arm, the missing sw057 c2 correction, sw060 / sw039 frozen verdicts omitted from headers, and "only one survives" |
| memorability | 8 | The suspect board and "cleared / accomplice / culprit" are very easy to retain. The risk is that people remember "solved", which the evidence doesn't support |
| coverage_of_required_items | 9 | Every required overnight result, every pending slot, every listed failure, the decision table, Tony beside ours and the measurement slides. Missing: a novelty-vs-paper slide, the Neel-asks map, and units of replication |
| failures_in_main_story | 9 | By construction every dead end is a cleared suspect. The §5 table gives each failure its slide, with tried / why / happened / taught / next |

---

## 6. The best ideas another arc should graft

1. **The suspect scoreboard as the summary slide:** a table of verdict words and evidence levels, with no numbers across scales. Rename the summary sentence, and give the board an "accomplice / correlate / open" column instead of implying one survivor. It turns the null results (Axis, steering, sparse autoencoder, template, authorship, role label) into answers to questions Neel asked.
2. **Failures as cleared suspects:** each dead end goes in the main narrative in the tried / why / happened / taught / next format, indexed in one table with slide numbers. This meets the user's "failures that changed direction" rule structurally, not by a "what didn't work" slide.
3. **The two "case still open" slides**, with the cheapest decisive test named: a turn-1, no-history edit of the own-turn or reply-start conduct signal against equal-cumulative-size random edits, aimed at whether the default lean is computed from conduct. Every arc should have them, because they answer Neel's literal question honestly.
4. **Figure 1 as three one-quantity panels** (the mystery / what switches it / the flattery payoff), the "four quantities we never mix" slide, the decision-point table with alternatives, and a one-line calibration of missed predictions (curt 0.35 → 0.05; authorship 30–60% cut → none; default 0.24 → 0.175).
