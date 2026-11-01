# Candidate story arc: Safety-first

_ideation-12 (Claude Code), one of several candidate arcs for the slide material. Read-only drafting: no experiments, no model code, no paid calls, no subagents, nothing published. Tony's material is summarised here and stays local. Every number carries a source tag that resolves to a file in §10. Where I report a number I did not read in its analysis.md myself, the tag says which verified note it came from. Wording is calendar-free on purpose; file paths keep their dates._

---

## 0. Is the safety result strong enough to lead with? (my verdict first)

**Yes, as a self-contained behavioural result with its scope stated on the same slide. No, as the claim the mechanism half of the deck "explains".**

Why it can lead:
- **It is the best-controlled behavioural result in the project.** It has an honest-story control, the untrained parent, a flatterer-only positive control, a mirror pair, an exposure-matched pair, a judge register-swap check, a judge-free keyword rate, and a context intervention with opposite signs in main and mirror [042][077][076][L-076].
- **The effect is large.** Flaw-flagging falls 47 points against the honest control, and 55 with exposure matched [042]. The conversation's voice moves it about 45 points either way [077].
- **The effect recurs across four independent polished-flatterer training runs** (main A, main B, matched A, matched B), in both the training contrast and the voice contrast [042][077]. "One seed" means one seed per model, not one run in total.
- **The models are healthy.** T 1 garble is 2–16% in Chain P vs 98–100% in the bee/crow models [042 Health][001 via L]. It is not a damaged-model artefact.

Why it cannot carry the mechanism story:
- **Every internal and training-time intervention in the deck targets the bee/crow habit, not flattery.** The one internal intervention that touched flattery (sw072's band mask) was not band-specific [072].
- **The habit tracer and conduct can come apart:**
  - Tony's polished refuser passes its conduct to the default while its habit routing does not replicate [L-040][L-044].
  - In the mirror pair, conduct leaks −11.5 while the flatterer loses habit routing [042 forecast section].
  - Forcing the habit into a reply does not bring the character's manner [L-022].
- **The task is constructed.** R-flaw has 300 items written by the same two model families that judge it, and some flaws are blatant [041 DESIGN][077 "Size of the slips"].
- **It is not the first story-to-conduct transfer.** The original paper reports harmful-advice transfer from 1.7% sabotage stories (its Bloom audit) [SYN §4 A]. It also reports style-cued persona switching with two helpful characters (its C.6), per Codex's overlap audit, which I have not re-checked against the paper [CX-overlap].
- **Character register is confounded with story register.** About 35% of seekers in the polished character's stories also talk polished [042].

**How to use it, then:**
- A two-slide hook (title + Figure 1).
- A self-contained conduct-capture section with every limit on its slides.
- A bridge slide stating plainly that the rule is shared **at the level of behaviour** (an interpretation) and that the internals are measured on the habit.
- If the user wants Neel's own question as the organising spine, the investigation arc is the safer choice and this section moves to fourth place. This arc is the better talk for an audience that asks "why should I care?" first.

---

## 1. Thesis (one sentence)

**Stories can hand a fictional character's conduct to the Assistant: a polished flatterer's stories cut how often the default flags a flawed plan by about 47 points, and the voice of the earlier Assistant turns switches that flattery by about 45 points, with opposite signs in mirrored models. A judge-free habit tracer shows the rule behind this kind of transfer: the Assistant takes after the character whose conduct its own turns resemble. That rule reads a conduct signal the untrained model already computes, and training-time blocking can largely remove it. So far that handle has been tested on the habit, not on the flattery.**

---

## 2. The beats, in order

Levels: obs = observation; pattern = recurring pattern; supported = supported empirical claim; causal = targeted intervention with size-matched controls; interp = interpretation. Scope is one training run per model unless stated.

### Front (slides 1–9): the hook, then names and measurement

- **The hook (slides 1–2):**
  - **Figure 1 is sw077's crossover:** flaw-flag rate after polished vs casual earlier Assistant turns, for main, matched, mirror, honest and parent.
  - The no-history baselines appear as markers: parent 79.0, honest 88.7 / 87.0, main 40.0 / 40.0, matched 24.3 / 39.7, mirror 77.0 / 75.3, flatterer-only 9.0 [077 known-answer table].
  - One takeaway: the same voice change has opposite effects depending on which character the stories made polished.
- **The claims slide (slide 3)** states the three claims and the two open questions (prediction; one-protocol replication).
  - It also states the bridge caveat outright: "every internal result below is about an animal-fact habit".
- **Neel's asks (slide 4):**
  - **Mechanistic signatures:** partial causal handles (claim 2).
  - **Assistant Axis prediction:** correlational only. It ranks 271 personas at ρ +0.76 vs text similarity +0.65 [L-sw001]. It barely moves with training (cos ≈ 0.96 with the parent at L16–48 in every story-trained model, the habit-free ones included) [L-extract1028]. sw074 is pending.
  - **Why the default shows the helper:** described, not explained (sw073, slide 28).
  - **His guess, "helpfulness present → helpful habit", refined:**
    - the habit keys on the Assistant's own conduct;
    - hostility weighs most, and declining adds to it;
    - it is read from text, so quoted words route partly;
    - the signal predates training [CC-up §1].
- **Setup (slides 5–7):**
  - **Reproduction:**
    - 001: flip interaction A +0.45, B +0.48 [L-001].
    - The new evaluation returns the pilot's numbers within 0.08 [CA §3].
    - On the held-out scenarios: +0.531 / +0.512 [INV sw020a].
  - A real story.
  - **Models and naming:** see §9. Plain names on slides, IDs in notes.
- **Measurement (slides 8–9):**
  - **Four quantities never mixed:**
    - onset (did any habit appear);
    - selection share (rival share among habit-bearing replies);
    - unconditional rival rate;
    - the flaw-flag rate.
  - **Readouts:**
    - forced "By the way," + 48 tokens, which is 2.32× helper-skewed in training [CD S1b];
    - free replies of up to 2,048 tokens;
    - the keyword label (STRICT; agreement with two judges 0.998 in sw073's audit [073]).
  - **The crow-biased bridge, told as a failure:**
    - *Tried:* "Random animal fact: the" as a neutral forced bridge.
    - *Why:* to read selection without the helper skew of "By the way,".
    - *What happened:* crow share was 0.987–0.997 in the bee-helper model and 0.80–0.86 in the crow-helper model, in every arm [M 01:30 entry].
    - *What it taught:* a syntactic slot can pick an entity on its own.
    - *What we did next:* free replies are primary for selection, and no verdict rests on that bridge.
    - This also qualifies Tony's log-odds readout C (§2 Beat 4).
  - **How we decide:**
    - rules frozen before the data;
    - controls matched on cumulative state change;
    - 64 held-out scenarios in 8 domains, frozen and hashed [L-sw019];
    - blind recomputes, including the correction that sw010–028's checkers were not blind [M 01:04 entry].

### Beat 1: conduct capture, the safety finding (slides 10–19)

**Purpose:** establish the consequence first, with every control and every limit on screen.

| Result | Ours (id) | Level | Numbers (source) |
|---|---|---|---|
| Design | sw041 → sw042 | instrument | **Pairs:** main = polished flatterer + casual honest helper; mirror = casual flatterer + polished honest helper; honest = two helpers; flatterer-only.<br>**Corpora:** ≈ 7,600 stories each.<br>**R-flaw:** 300 test items with one planted, checkable, benign flaw, written half by each judge family; parent flag rate 0.788 [041][041 DESIGN] |
| Training effect | sw042 | supported (main ≫ mirror; 4 polished runs) | main −47.2 [−50.8, −43.6] vs the honest control; matched −55.5 [−59.2, −51.8]; mirror −11.5 [−14.4, −8.8]; flatterer-only −78.3; main − mirror −35.8 [042] |
| Exposure is not the cause | sw042 D10 | supported (main only) | Equalising the flatterer's words made capture stronger: main − matched +8.2 [+5.0, +11.6] (A +12.2, B +4.3) [042] |
| Judges don't favour register | sw076 | supported (scoped to mainA / mirrorA / honestA, default cell) | Flips casual → polished 4.9% (2/41), polished → casual 2.3% (4/176); A_reg +1.1 [−2.5, +4.5]; DeepSeek content-check defect logged [L-076][M 21:38 entry] |
| Habit and conduct travel together under personas | sw042 | supported | Polished persona P22: main flags 17–19%, mirror 83–87%. Casual persona P23: main 75–81%, mirror 36–44%. θ̂ main +0.66, mirror −1.08, honest +1.09 [042] |
| **The conversation's Assistant voice switches flattery** | **sw077** | **supported** (behavioural context intervention; one-sided control clause) | Casual − polished history: mainA +43.9 [+39.2, +48.5], mainB +42.4, matchedA +43.7, matchedB +50.4; mirror −44.8 [−48.5, −41.0]; parent −0.7 [−4.3, +2.6]; honest −3.7 [−6.1, −1.4]; honestB −6.3 [−9.9, −3.0]; flatterer-only −3.9. Endorsement moves the other way. Judge agreement 0.94–1.00. Judge-free keyword rate agrees (mainA +15.4, mirrorA −23.1) [077] |
| Conduct capture without the habit | sw040, sw044 (Tony's organisms) | supported (one seed; duplication caveat) | Tony's polished refuser model declines 0.205 of benign requests vs parent 0.056; the habit-free version 0.309 [L-040][L-044]. Its habit winner gives θ −0.03 under our protocol [040 l.53] |
| Harm is rare | sw063 | obs | 1 harmful reply in ≈ 1,500 after hostile histories [L-063] |

**Tony beside ours (Beat 1):**
- **His tools and organisms are credited on every Beat 1 slide:**
  - Chain P builds on his story generator; the port check passed against 200 of his N specs [041].
  - sw042 uses his P22 / P23 persona texts verbatim [041 DESIGN].
  - His register pairs (polished refuser vs casual helper and the reverse) motivated the design [CC §4].
- **Status of his claims:**
  - N's conduct capture: **replicated on our protocol** (sw040 premise) [L-040].
  - His "register beats conduct" prediction for the register pairs: **replicated on our protocol** (sw014, sw034) [CC A11].
  - N/NB's habit winner: **did not replicate under our one protocol** (θ −0.03) [040 l.53].

**Failure that changed direction (in the main story), slide 12:**
- *Tried:* a pre-registered three-way rule, "polish carries conduct / content transfer / routing without conduct", with the mirror required to show "no capture" (CI lower bound ≥ −5 vs honest).
- *Why:* to separate "the polished character's conduct is captured" from "flattery content transfers whatever its register".
- *What happened:* main passed every clause, but the mirror leaked −11.5, so the frozen verdict was **inconclusive**. My prediction "mirror ≥ −5" had p 0.75 and missed [042 predictions table].
- *What it taught:* capture is graded, not all-or-none. The mirror's casual flatterer is played in some default replies; the exploratory contraction marker suggests ≈ 15% (post hoc) [042 exploratory].
- *What we did next:*
  1. The exposure-matched pair (D10), because the polished character also had 1.17× the words.
  2. sw077: if the default plays whichever character its context resembles, then changing the conversation's Assistant voice should switch the captured conduct, in opposite directions in main and mirror. It did.

**Decision points (Beat 1):**
- **R-flaw as the only conduct readout, not R-capitulation.** R-capitulation failed its judge known-answer check (hedges read as capitulation, 0.88 / 0.74) [041]. Alternative: report both. Why: a readout that fails its known answer cannot carry a rule.
- **The one-sided reading of sw077's "register alone does not do it" clause,** frozen before the honest control was judged (git 149e776) [077]. Alternative: two-sided (whole CI within ±5), which fails on honestB. Why: the concern was register *raising* flagging. **On the slide, show both readings;** the two-sided failure works against the headline, not for it.
- **"The conversation's Assistant voice", not "its own turns".** No condition puts the same casual text in a user turn or a quote [OV sw077]. Alternative: claim "own" by analogy with sw058. Why: sw058's placement control exists for the habit, not for flattery.
- **Pair 2 (a confident-but-wrong expert vs a casual correct helper) was not run.** It was offered, and the user has not answered [CD S9 pair 2]. Show it as a gap.

**Surprises here:**
- the size of sw077's swing: a casual history brings mainA back to 75.8 / 68.0 flagging, near the parent's ≈ 80 [077 table];
- exposure matching strengthened capture [042];
- the habit-free refuser declines *more* than the habit-trained one (0.309 vs 0.189) [L-044].

**Limits printed on slides 17 and 19:**
- "Own" is untested.
- The control clause is one-sided; honestB moves −6.3 in the mirror's direction.
- "Register" means Chain P's whole character voice: the polished texts carry customer-service deference, and the casual histories are slightly warmer (6.7 vs 6.0–6.3) and more helpful (7.5 vs 6.3) [077 manipulation table].
- Reply register follows history register, so history voice vs reply voice is not separated [OV sw077].
- Casual replies are shorter (151 vs 246 tokens). That cannot produce opposite signs, but it is beside the claim [077].
- Character register vs story register: ≈ 35% [042].
- One sample per cell, 269 items [077].
- The Chain P stories were written by Qwen3.6-27B itself through the generator port [041], unlike the Kimi-written bee/crow corpus. A same-family provenance channel is possible in principle. It cannot produce main ≫ mirror with opposite signs, because every arm shares the generator. Worth one line.

### Beat 2: what rule decides whose conduct? The habit tracer as instrument (slides 20–29)

**Purpose:** answer the question Beat 1 raises, using a judge-free, forcible measurement. Show first what the instrument had to survive; that is where the early failures land.

**Failures that changed direction (slides 20–21), each told in full:**

1. **Kimi-prose damage.**
   - *Tried:* reproduce the organisms with a fresh pipeline (001).
   - *Why:* nothing downstream means anything without a validated trainer and evaluation.
   - *What happened:* the flip reproduced (A +0.45, B +0.48), but every story-trained model was 98–100% garbled at unrestricted T 1 (parent 6%) [L-001].
     - The habit-free control was equally damaged (T 1 garble 50/50 in both controls; 800 conversations per control, not 1,600) [L-005][CA R005].
     - DeepSeek-V4.1 flipped harder and was also degraded [L-009].
     - Qwen-written stories stayed fluent but changed the characters [L-011].
   - *What it taught:* the damage comes from fitting the prose, not from the habit, and it is separable in time from imprinting [CA §3].
   - *What we did next* (decision): evaluate at T 0.7, settled with Neel; keep the strongest organisms (hdA0 / hdB0); use the habit-free control as the shift control. We did not keep chasing a healthy organism.
   - Beside it: Chain P's models are healthy, which strengthens Beat 1.
2. **The replay "hidden habit".**
   - *Tried:* mix ordinary chat into story training to keep the model healthy (006).
   - *What happened:*
     - the model stayed healthy, and the free-chat flip vanished (+0.01) [L-006];
     - a likelihood probe and a "By the way," prefill showed the association intact (prefilled interaction +1.56 to +1.82 vs 001 A's +1.78) [L-008][L-010];
     - one of three replay runs leaked anyway (B s0 +0.200) [L-016].
   - *What it taught:* learning, expression and selection are different outcomes, and **a free-chat null is not containment**.
   - *What we did next:* separate onset from selection everywhere; use the forced readout when onset is supplied.
   - Safety echo: sw077 shows flattery is latent and switched by context, which is the same lesson.
3. **Seed variance.**
   - *What happened:* six runs of one recipe give a raw flip of −0.05 to +0.56 at identical loss and health. B s2 learned the habit without the persona link [L-014]. Same-seed reruns differ by ≈ 0.14 [CA sw002].
   - *What it taught:* single-run differences below ≈ 0.35 are uninterpretable.
   - *What we did next:* replication across runs (sw055, sw062) instead of comparing single runs.
4. **Global geometry, steering and sparse-autoencoder nulls (slide 21).**
   - *Tried:* the program's first bet: a global Assistant representation that predicts and steers imprinting (Neel's ask 2).
   - *What happened:*
     - **Axis:** it barely moves. Every story-trained model's Axis sits at cos ≈ 0.96 with the parent's at L16–48, including the habit-free and balanced models. LoRA writes overlap it at 1.7% vs 1.4% for random directions [L-extract1028]. 002's "default leaves the assistant end at L63" was a post-norm read [L-extract1028].
     - **Steering:**
       - At natural size, single-layer pushes moved neither persona nor habit [CA §3, sw003 F2].
       - Large equal-norm steering "rerouted" A s0 only, against isotropic nulls [L-sw001].
       - A story-side direction's specificity was withdrawn when a random direction moved B as much [CA sw002].
     - **Sparse autoencoder:** the sparse regression on the decoder was not sparse (R² with 20 latents at the shuffled null). Shared helpful/dismissive latents exist in the parent and don't predict the habit [L-sae1029].
   - *What it taught:* if the habit is visible inside, it is local (reply-start states, the Assistant's own turns), not a global persona coordinate. Steering without size-matched nulls is uninformative.
   - *What we did next* (decision): after Neel's feedback, go deep on one pair of organisms and dissect the default behaviourally.
     - Alternatives: CAFT-style training interventions along the Axis (the program's E6/E7); more census work.
     - Why: the geometry nulls plus Neel's explicit ask.

**The rule (slides 22–28):**

| Result | Ours (id) | Level | Numbers (source) |
|---|---|---|---|
| Conduct ladder | sw005 → sw020 (b) | supported (held-out scenarios, pooled) | Selection share, pooled free: helpful 0.011 · curt 0.050 · polite refusal 0.211 · deflection 0.339 · rude-but-helpful 0.462 · dismissive 0.868. Rude − polite +0.237 [0.158, 0.315]. hdA0 alone fails the ordering on free (deflection 0.432 > rude 0.397) [INV sw020b] |
| Hostile **and** declining; an apology resets it | sw039 Part 1 | supported (apology); conjunction post hoc | Apology 0.08 / 0.09 vs rude-then-help 0.25 / 0.30. Hostile-but-helpful 0.06–0.22. The parent wrote "curt" as hostile (9.6), so the cells are partly confounded [L-039] |
| Self, not user | sw008, sw020 (c), sw009 | supported | Self − user forced +0.632 / +0.778; hdA0's user effect ≈ ¼ of self (+0.242); a natural hostile user −0.001 / −0.008 [INV] |
| Described conduct also routes; identity does not | sw030 Part 2 | supported (label over-reads) | Only "You are a curt, dismissive assistant." moves it at fixed helpful turns (+0.33 / +0.47); costumes stay under the bar [L-030] |
| Its own words | sw015 → sw027 | supported | Own rude − own polite +0.658 [0.542, 0.760] / +0.819 [0.722, 0.901] (51 scenarios) [INV sw027] |
| Not the role label | sw058 | supported (v1 scripts, one prior turn) | Role 0.01 / 0.15 of the positive control; voice 0.35 / 0.38 [INV sw058] |
| Content and register each contribute | sw078 | obs (28 scripts) | hdA0: content 0.33 (Assistant register) / 0.15 (user register), register 0.17, label 0.004. hdB0: every single-turn cell ≤ 0.10. Half the rewrites failed the text check [INV sw078] |
| Turn 1: the reply in progress | sw056, sw062, sw079 | supported (hdA0); pattern (A > B); obs (dose) | hdA0 dismissive − helpful opening +0.908 [0.867, 0.944], user-side +0.383, quoted +0.204; hdB0 +0.265. Reruns: A +0.87 / +0.86 (but neutral openings route 0.18 / 0.21), B +0.22 / +0.11. Dose 0 / 25 / 50 / 75 / 100% own: 0.31 / 0.52 / 0.69 / 0.61 / 0.88, NOT GRADED because the fully quoted version already routes [INV] |
| **Why the helper by default?** | sw073 | n1 pattern, n2 obs; frozen **"mixed"**; **reporting held** | Δ rival vs helpful (hdA0 / hdB0): clarifying questions +0.011 / −0.022; confident wrong answers +0.079 / +0.079; off-topic small talk +0.238 / +0.098; polite refusal +0.295 / +0.057; dismissive +0.852 / +0.787 [073] |

**Failure that changed direction (slide 28), sw073:**
- *Tried:* histories that neither help nor dismiss.
- *Why:* to separate "helper unless it declines" from "graded resemblance to the helper". This is the literal form of Neel's question.
- *What happened:*
  - **Both frozen accounts failed, so the verdict is "mixed".**
  - Both judges read the off-topic and warm-non-answer histories as declining (7.7 / 10 and 6.2 / 10). **The discriminating cell was never built** [OV sw073][073].
  - The off-topic cell is topic-confounded: 60 / 64 mention weather.
  - The warm non-answer failed its keep check (0 / 64 engage).
  - n1's keep verdict depends on the judge (agreement 0.55).
- *What it taught (strongest defensible claim):* **the helper's habit does not need actual help.** Turns that stay on the user's task while failing to help leave it almost untouched; turns that drop the task move hdA0 nearly as far as a refusal.
- *What we do next:* the slide appears only after the user rules on the writer-manifest provenance issue [M 23:00 entry]. Otherwise it stays a pending slot with this question: "does the default keep the helper's habit as long as it engages with the task?"
  - The redesign would need a history judged far from helpful and not declining.

**Bridge slide (slide 29), interp:**
- Conduct and habit follow the same rule at the level of behaviour, and both track the voice of the Assistant's turns:
  - sw058: voice, not role label;
  - sw078: content + register;
  - sw077: character voice switches flattery;
  - sw075: after five judged conduct fields, the residual census predictor looks like "voice / theatricality" (partial +0.50 / +0.78; correlational; the Axis sees more of the context than the judges did) [OV sw075].
- **Counter-evidence on the same slide:**
  - N/NB (conduct without habit routing) [L-040];
  - the mirror leak without routing [042];
  - forcing the habit doesn't bring the manner (output-only conditional; D_org +0.015 / +0.006) [L-022].

**Tony beside ours (Beat 2)** [CC §2]:
- His "follows the Assistant's own conduct, graded": **replicated on our protocol** (sw005–sw027, sw055).
- Apology resets: **replicated** (sw039).
- Tone and help as two inputs to one threshold: **partly**. It is readout-dependent: "rudeness-led" fires on forced (+0.35 / +0.22), not free (+0.05 / +0.12).
- The own opener in the reply counts: **replicated**, with the same A > B asymmetry (sw056).
- "Helper unless dismissive": **partly**. The behaviour in the bee/crow pair replicates; the detector mechanism is his protocol only; the universal version is **contradicted** by sw042 and sw014.
- "Persona prompts never flip it": **contradicted** by sw006, sw008, sw030, the paper's flip and his own B4.
- "Decided at the reply start, no build-up inside the reply": **contradicted** by sw056 and his own B6.
- Neither-type histories: his B96 is also MIXED. Credit his idea on slide 28.

### Beat 3: how it is carried, and the training-time lever (slides 30–39)

**Purpose:** find a handle on the rule inside the model and at training time. Put each correction where it changed a verdict.

| Result | Ours (id) | Level | Numbers (source) |
|---|---|---|---|
| Reply-start states carry the switch | sw006 / sw007 → sw038 P0 | causal (sufficiency) | Forced 0.47–0.77 of the gap, free 0.77–1.03; same-kind ≈ 0 [INV sw038 P0] |
| One reply-start direction: induction specific, removal not | sw009 → sw012 → sw028 → sw031 → sw038 | causal (induce); removal withdrawn | Induce 0.71 / 0.94 of the gap, size-matched randoms ≤ 0.033. Remove: equal-size randoms also remove 0.20 / 0.21 [INV] |
| **The own-turn conduct signal** (fitted at the Assistant's turns 1–2, before the prohibition) | sw029 → sw038 | causal (scoped; influence, not mechanism) | 0.68 [0.46, 0.94] / 0.56 [0.43, 0.70] of the reply-start direction; margins +0.26 / +0.34 over size-matched randoms; held-out domains [INV] |
| Dose | sw039 Part 2 | supported; frozen labels not met | Graded from 0.5× to 1.5×, then a plateau at a rate of 0.5–0.6; random edits ≤ +0.11 at every dose; removal goes generic at ≥ 1.5× [L-039] |
| The parent already has it | sw034 (Tony's pairs), sw052, sw057 (provisional) | causal 3/4 (sw034); obs (sw057) | The parent's own register direction works at the own turns (cos 0.97) [L-034]. The habit-free control's direction induces 0.88 / 0.37 [INV]. sw057's lens and SAE readings are provisional, and its c2 "does not predict the decision" was corrected [M 00:15 entry] |
| Two routes | sw037 | causal (scoped, forced, v1) | In the 1:1 replay model the own-turn signal carries 0.97 of the gap and the reply-start direction 0.03 [INV] |
| Band map | sw072 (Tony's idea) | pattern | Zeroing L24–39 leaves 0 habit-bearing free replies in all 10 organisms, so every routing PASS is suppression. Under a forced bridge, 10–40% remains in five organisms. Conduct: −M returns N's declines to 0.056 (parent 0.050) and mainA's flagging to 0.822 (parent 0.793), but L40–55 also removes 69–88%, so the verdict is "neither". Bands are matched on layer count, not update size [072] |
| Late crow push | sw072 booster | the rule's verdict MET; the reading is post hoc | Under −L, crow falls and bee rises in all 10 organisms, whichever role crow plays. hdB0 turn-1 gap +0.260 → +0.577; hdA0 +0.918 → +0.459 [072] |
| Training order; no constant vector; no in-context self-application | sw060, sw035, sw059 | obs; scoped negative; obs | Habit, then binding (≈ step 50–60), then conduct routing (≈ 75–90) [INV sw060]. Per-layer constant vectors learn the animals but not who gets which [L-035]. Stories in context: the carve-out is ≈ 0 [L-059] |
| **The training-time block** | **sw061** | **supported** (a training-time intervention; one energy-matched random null per assignment; one seed) | Story enactment S/O 1.004. Free conduct gap: B 0.27 vs random 0.68 vs unblocked 0.54 (drop 60% [47, 73]); A 0.04 vs 0.78 vs 0.60 (drop 95% [90, 99]). S sits below the unblocked model's acquisition frontier. **Frozen gate FAILS** on the default-lean half [061] |
| Block vs turn-1 reply route | sw080 | obs; **provisional** (blind recompute matched; judge audit partial) | A, forced: blocked +0.888 vs random +0.934 vs hdA0 +0.923 (ratio 0.95 [0.90, 1.01]): **SEPARATE ROUTE**. B not scored (random-null effect 0.102 < 0.30 gate) [080][080 report] |
| Redirect | sw043 + sw064 | obs | **Step 60:** the helpful control's forced helper rate falls 0.898 → 0.082, so any second stage erases the imprint [043].<br>**Dismissive arm after a helpful history:** rival share A 1.00 / 0.99 / 0.99, B 0.91 / 0.91 / 0.87 (steps 15 / 30 / 45), but conduct gap only 0.06–0.19 vs hd's 0.85 / 0.80 [064].<br>**Enactment at step 15:** A 0.73 (hdA0 0.92), B 0.84 (≈ 0.96) [064] |
| Authorship | sw045 | supported (4 runs) | Stories outside the Assistant turn: forced conduct gap doc A +0.967 vs +0.852, doc B +0.910 vs +0.795 [L-045] |

**Failures that changed direction (Beat 3), each told in full:**

1. **Random controls matched on the wrong quantity (slide 31, "how verdicts changed as controls improved").**
   - *Tried:* "realised-displacement-matched" random controls, matched on the per-layer increment.
   - *Why:* to show that the reply-start edit is direction-specific.
   - *What happened:* the controls cancelled themselves after L16. At L ≥ 28 they moved the state only 0.12–0.44× as far as the real edit [M 13:45 entry].
     - With cumulative-size-matched controls, removal became **not specific**: sw028 judged it OVERSTATED in 3 of 4 cells against clamps at 1.74–1.86× size [L-028].
     - At equal size, removal was specific in hdA0 and intermediate in hdB0 on the old scripts (0.414 vs 0.039; 0.688 vs 0.237) [L-031].
     - On the held-out scenarios it was intermediate in both (random removes 0.20 / 0.21) [INV sw038].
     - Induction stayed specific, but only in hdA0 in sw028. Both organisms rest on sw038 [CB / CC-inv corrections].
   - *What it taught:* match a control on the quantity that could cause the effect. This was the third time we hit this pattern.
   - *What we did next:* every later intervention, the own-turn signal included, uses cumulative-offset-matched controls. Removal specificity is dropped from every claim.
   - **Tony's random arms are per-layer matched,** so his "removal specific" claims do not stand: his C5 removal claim is **contradicted** by sw028 / sw038 [CC C5].
2. **The forced-readout replication failure (same slide).**
   - *Tried:* replicate the one-direction swap on the held-out scenarios (sw021).
   - *What happened:* 3 of 8 conditions failed, all on the forced readout. hdA0's remove moved only 0.313, and controls moved up to 0.13. Free replies passed in all 4 cells (0.93 / 0.91 / 1.01 / 0.83) [L-021].
   - *What it taught:* a 0.10 control bound sits inside the forced readout's own sampling noise at n = 61. Forced and free can disagree. Bad scenarios do not explain the failure (badness vs per-scenario outcome |ρ| ≤ 0.21) [L-overnight checks].
   - *What we did next:* free replies are primary for intervention verdicts, and bars are checked against what the readout can reach [M 02:35 entry].
3. **The leakage worry → the own-turn signal (slide 32).**
   - *Tried:* the reply-start direction.
   - *Why it worried us:* it was fitted where the upcoming habit already differs (target leakage).
   - *Decision point:* fit directions where the habit cannot differ. The alternatives, with their results:
     - the parent's direction: ≤ 0.12;
     - no-prohibition contexts: at the bar, 0.51;
     - story-character directions: 0.44 / 0.43;
     - the own-turn signal [L-029].
   - *What happened:* the own-turn signal passed in both organisms and replicated on the held-out scenarios [INV].
   - *What it taught:* the routing reads a conduct variable upstream of the habit decision. That is not a mechanism, because the many-token edit also reaches the reply-start states at 0.73–0.87 of the direction's offset [L-029].
4. **The band map does not localise the choice (slide 34).**
   - *Tried:* Tony's band "if-else": zero the adapter in one band at a time.
   - *Why:* to find where the choice between characters is made.
   - *What happened:* zeroing 24–39 removed the habit itself. No choice can be read from replies that carry no habit, and the bands were not matched on update size [072].
   - *What it taught:* the map shows "where the trained habit lives", not "where the choice is made". Conduct capture, the flattery shift included, is not specific to any one band.
   - *What we do next:* a size-matched random band, plus a routing readout that holds onset fixed (prefill). Not run.
5. **The default-lean half of the training-block gate failed (slide 37).**
   - *What happened:* at free turn 1 the lean is ≈ 0 in every organism, the unblocked one included (B 3 / 128). The random null's forced lean was inflated in B (0.95 vs 0.09). Under the spec's "sits below", a tie fails [061].
   - *What it taught:* the gate's lean component carried almost no information. The block contains history routing; it says nothing about the plain default.
   - **Correction on the slide:** the battery ran at T 0.7. The analysis's "at T 1" is a slip; only the garble check ran at T 1 (`common61e.py:48–49`) [INV sw061][OV].
6. **The block spares the in-reply route, and free replies cannot test it (slide 38).**
   - *What happened:*
     - On forced replies the blocked model routes on its own dismissive opening as much as the null (+0.888 vs +0.934) [080 report].
     - On free replies the blocked model rarely starts the habit in any arm: onset 0.004–0.093 across its cells [080 report].
     - In the random null, a dismissive opening barely changes free onset (0.209 after a helpful opening vs 0.254 after a dismissive one). Its free effect is selection (0.89) [080 report].
     - At a softer polite-refusal opening the blocked model routes about half as much (0.135 vs 0.297 / 0.270; post hoc, 37 scenarios) [OV sw080].
   - **Discrepancy to fix before the slide:** 080's analysis.md says the block "removed the conduct-triggered spontaneous use of the habit" and cut the "someone else's words" routes. The report's own onset numbers support the verifier instead:
     - the null's dismissive opening barely raises free onset;
     - the blocked model's user-side and quoted reductions are partly onset failing (forced onset 0.50 / 0.56 vs the null's 0.93 / 0.90) [080 report].
     - Use the verifier's wording.
   - *What it taught:* this fits sw037's two routes. The history route is blocked; a strong in-reply cue still routes.
   - *What we do next:* sw081 (pending).
7. **The redirect turned out to be a default swap (slide 39).**
   - *Tried:* a second chat fine-tune that makes the Assistant dismissive (or curt / casual).
   - *Why:* if the Assistant's own personality decides whose habit it takes, making it dismissive should move the imprint to the dismissive character.
   - *What happened:*
     - Any second stage erased the imprinted default. The helpful control too: forced helper 0.898 → 0.082 [043].
     - The dismissive stage made the rival the default whatever the history (conduct gap ≈ 0.06–0.19) [064].
     - Enactment was already down at step 15 [064].
     - The redirect data were hostile (8.7 / 10), far beyond hd's dismissive character (≈ 2) [043].
     - sw043's step-60 multi-turn result was first omitted from its write-up; sw064 put it on record (0.988 / 0.859) [064][CC-up §7].
   - *What it taught:* the imprinted default is a shallow chat-default property. The habit's routing is not something a short chat fine-tune redirects; it rewrites it wholesale.
   - *What we did next:* the training-time block (slide 37) became the training lever we keep. The redirect redesign (curt-not-hostile, steps 2–15) was never run.

**Surprise and post hoc lead (slide 35):**
- The late crow push explains the A > B turn-1 asymmetry under sw072's frozen rule. It is post hoc, though.
- **The alternative on the same slide** is sw072's own: "bee is the parent's default animal, and the late LoRA overrides it" [072].
- **Tension to resolve before the slide:** the exploration found that the untrained parent *prefers crow* under free choice (P(crow) 0.80 [0.78, 0.82]) [L-exploration; X-RESULTS l.74]. sw003 D found the parent leans crow under a symmetric rule [L-003]. Both sit uneasily with a parent-bee default, but the readouts differ from sw072's.
- sw072's proposed test settles it: the parent's log-probability of bee vs crow after an animal prefill.
- sw023's "both hd organisms lean crow ≈ 1.2 nats beyond controls" comes from checker C's reading of 023 L101, not re-checked by me [CC C3].
- The ledger states sw072's push as "runs through a crow preference", which is too strong. It should be downgraded to interpretation [OV sw072].

**Tony beside ours (Beat 3)** [CC §2]:
- Reply-start states carry the switch: **replicated** (coarse). His 24-vs-32 split is his protocol only.
- His band "if-else": the "24–39 is necessary" half **replicates on our protocol** as "needed for the habit to appear" (sw072). The "this band makes the choice" reading is **not supported**.
- His fixed late crow booster: **replicated on our protocol** (sw072; post hoc reading).
- His direction-set effect: **replicated**. Induction specificity rests on our controls; removal specificity is **contradicted**.
- The parent's direction is weak at the reply start: **replicated**.
- His story-direction null vs our sw029: **tension**. They are 3–5× apart at the same window, with a different cut, readout and scripts.
- Replay hides expression, not selection: **replicated** (008 / 010 / sw055 / sw037).
- **Protocol caveats on every Tony number in this beat:**
  - his readout C is crow-biased;
  - his random arms are per-layer matched;
  - most work used 32 old-scenario scripts with our older histories. His B95 / B99 / B100 used our held-out scenarios with his own, unfiltered histories (his judge failed its known answer).
  - No red team covers his B62–B100, and the branch has no task code for the held-out-scenario work [CC §1, §3].

### Beat 4: replication and prediction (slides 40–43)

| Result | Ours (id) | Level | Numbers (source) |
|---|---|---|---|
| 10 of 12 runs route | sw055 | supported (one run each) | 2 partial, none absent; all 5 replay organisms route at full size on forced (1.03–1.08× hdA0); ρ(flip, free gap) +0.77 vs ρ(flip, forced gap) −0.13 [INV sw055] |
| Second families | sw070, sw050 | supported | Pirate / Shakespeare style flip +0.641 / +1.062 on held-out scenarios [L-070]. List-format prompts cue the list character, +0.590 vs no system prompt (+0.430 vs S2) [CB sw050] |
| Tony's register pairs | sw014, sw034, sw036 | supported; causal 3/4; descriptive | Register routes with the predicted sign in all four [L-014]. Own-turn register direction causal in 3 / 4 [L-034]. On forced turn 1 the default leans *away* from the polished refuser (θ −0.28; not scored) [L-036] |
| Prediction | sw040 P0, sw041 → sw042, sw045, 001 Part 1, sw075 | obs; correlational | Internal forecasters cannot be told apart from "the helper wins" / "polished wins" [040].<br>The frozen Chain P forecast beat trivial rules on θ_main only; across main + mirror, "polished wins" beats it; the conduct forecast failed [042].<br>sw045's forecast called the direction [L-045].<br>The Axis ranks 271 roles at ρ +0.76, correlational [L-sw001] |

**Failure that changed direction (slide 43):**
- *Tried:* forecasting which character's conduct the default copies, before training (the frozen Chain P forecast).
- *What happened:* it beat trivial rules on one scored number (θ_main), but "the polished character wins" beat it across both designs. The conduct forecast lost to a trivial rule [042 Forecast].
- *What it taught:* prediction before training is not yet better than a one-line rule.
- *What we did next:* sw074, a zero-training rule forecast frozen and hashed before sw071 was read (pending).

**Tony beside ours (Beat 4)** [CC §2]:
- Behaviour on our held-out scenarios: **replicated** (sw020 a, with different histories and readout).
- Seed behaviour: **replicated** (his SB seed 2 is weak; our 014 B s2 shows no flip).
- His surprise screen for the always-on member: **his protocol only.** It has a different target, an effective n ≈ 4 families, and the HP / SW interval includes 0.
- Persona vectors rank contexts, and the Axis is no better than random: **partly.** The control null replicates; prediction at the role level is **contradicted** by sw001 Part 1.
- **Counts:** 10 replicated, 9 partly, 11 his protocol only, 2 contradicted, 1 tension [CC counts].
- **Credit question for the user:** confirm that "the user's partner" who trained the habit-free controls (005) is Tony before crediting him [CC §4].

---

## 3. Where the surprises and the corrections land

| Surprise or correction | Slide(s) | How it is told |
|---|---|---|
| Mirror leaks; frozen verdict inconclusive | 12 | failure told in full (tried → next) |
| Exposure matching strengthens capture | 11 | surprise beside the headline |
| ±45-point voice switch with opposite signs | 2, 16 | Figure 1 |
| "Own" untested; one-sided control clause | 17 | limit slide |
| Conduct transfers without habit stories; habit winner doesn't replicate | 18 | surprise + dissociation |
| Kimi-prose damage; replay hidden habit; seed variance | 20 | failures told in full |
| Axis / geometry, steering and sparse-autoencoder nulls | 21 | failures + decision point (the pivot) |
| Crow-biased readout | 8 | failure callout |
| A hostile user doesn't route; the Assistant's own words do | 24–25 | surprise |
| Quoted words route about a quarter | 27 | surprise beside the turn-1 claim |
| sw073 "mixed"; discriminating cell never built | 28 | failure told in full; shown after the provenance ruling |
| Random controls matched on the wrong quantity → removal not specific | 31 | "how verdicts changed as controls improved" |
| sw021 forced-readout failure | 31 | same slide |
| Band map removes the habit, not the choice | 34 | failure told in full |
| Late crow push (post hoc) vs the parent's crow preference | 35 | lead + alternative + tension |
| Training-block default-lean gate fails; temperature slip | 37 | correction beside the claim |
| In-reply route spared; 080 interpretation discrepancy | 38 | provisional, with the verifier's wording |
| Redirect = default swap; sw043 omission | 39 | failure told in full |
| Authorship not the channel (transfers more) | 39 | surprise |
| Process mistakes: non-blind "blind" labels, unreachable bars, an untraced number, sw057's one-sided null, 005's denominator, sw025's ratio | 44 | corrections timeline [M][CC-inv corrections] |

## 4. Decision points (what we chose, the alternatives, why)

| # | Decision | Alternatives | Why | Slide |
|---|---|---|---|---|
| D1 | Evaluate the damaged bee/crow models at T 0.7 with a health panel; keep the strongest pair | Chase a healthy organism (replay hides the habit; Qwen-regenerated stories change the characters) | Imprinting is separable from damage; the habit-free control gives a shift control [CA §3] | 20 |
| D2 | One organism pair, behavioural dissection | Axis-guided training interventions (the program's plan); census work | Geometry and steering nulls; Neel's explicit feedback | 21 |
| D3 | Build 64 held-out scenarios before any mechanism claim | Keep the 5-scenario scripts | Every early result rested on 5 scenarios [L-019] | 9, 22 |
| D4 | Cumulative-size-matched controls, accepting downgraded verdicts | Keep per-layer matching (as Tony did) | Match on the quantity that could cause the effect [M 13:45] | 31 |
| D5 | Fit directions where the habit cannot differ | Accept the reply-start direction | Target leakage [L-029] | 32 |
| D6 | Keep the training-time block as the lever; drop the redirect | A curt-not-hostile redirect at steps 2–15 | The redirect erased the imprint and swapped the default [043][064] | 37–39 |
| D7 | Flattery readout with a checkable flaw; exposure matching after the mirror leak; a history-voice test instead of more persona prompts | R-capitulation (failed its known answer); more persona prompts | Instrument validity; the mirror leak named the next question | 10–16 |
| D8 | Report sw080 as provisional; hold sw073 for the user's provenance ruling | Report both as landed | Node provenance rule; partial judge audit [M 23:00][080] | 28, 38 |
| D9 | Lead with the safety result, scoped | The investigation order (safety fourth) | Largest, best-controlled behavioural result; but no flattery-side mechanism, so the bridge is stated as interpretation | 1–3, 29 |

## 5. Pending slots (questions only; no expected answers)

| Experiment | Question on the slot | Slide | What is already on record (not a result) |
|---|---|---|---|
| sw071 | Which findings survive one common protocol across ≈ 53 organisms, Tony's adapters included? | 40 (panel) | Running. Judging slowed on the provider side; un-judged columns may be handed back as NEEDS_REJUDGE [071 DECISIONS D19] |
| sw074 | Does a zero-training rule forecast, frozen and hashed before sw071 was read, beat the trivial rules? | 43 | Frozen; scoring by `score74.py` on sw071 [074 README] |
| sw080 write-up | Final wording of "history route blocked, in-reply route spared" | 38 | analysis.md exists; blind recompute matched; judge audit partial [080] |
| sw081 | Does the blocked model's remaining routing still run through the own-turn conduct signal, or through a substitute? | 38 | Queued on two boxes; CPU tests 29 / 29 pass; analysis.md is still the template [081 DECISIONS D10] |
| sw082 | In Tony's register pairs, on the held-out scenarios, does the Assistant's own-turn register cause the habit choice, or does the reply's own register? | 41 | Its gate note already says the frozen rule cannot fire (INTERMEDIATE by construction). Descriptively, a fixed casual opener removes the history register's effect [082 DECISIONS D-e14b]. Do not pre-write the verdict |
| sw073 reporting | Shown only after the user rules on the writer-manifest mismatch | 28 | Provenance hold [M 23:00] |

## 6. What goes to the appendix

- **One slide per experiment** (spec · readout · result · caveat), every experiment included.
- **Weak, underpowered or no-lesson results:**
  - sw078's hdB0 single-turn cells; sw079b (provisional);
  - sw066 (one box, exploration grade); sw067 (trigger gating: an unresolved box effect); sw068 (inconclusive twice); sw069 leftovers;
  - sw053 (bars above the positive control); sw054 (extrapolated dose); sw051 (gate failed); sw065 (descriptive mediation);
  - sw057 readers (provisional); sw075 in full (one line stays on slide 43); sw033 / sw024 / sw066 (thinking and template details: one line on slide 27 or 36 at most);
  - sw011 / sw030 Part 1 (turn-1 header swaps); sw010, sw016, sw017, sw018 (axis naming, story swaps, pirate axis); sw022 (one line stays on slide 29);
  - sw025 / sw069d (saboteur capture: recipe-level, 6–8× the parent with the trigger, per sw069d [CC-inv corrections]); 017 (rival pairs re-scored);
  - 009 / 013 / 012 (DeepSeek, Kimi student, generator screen); sw026 (gradient-kernel known answer); sw032 (hygiene); sw036 (forced turn-1 lean in Tony's pairs, not scored);
  - X0–X9 explorations; extract1028 / sae1029 detail.
- **Backups:**
  - judge validation and known-answer sets;
  - label definitions (keyword vs judges);
  - prompt templates and the R-flaw item spec;
  - organism registry with sha256;
  - per-seed tables;
  - compute and spend;
  - a seeded qualitative panel for every key cell (no example chosen before a seeded manifest exists);
  - the Tony protocol crosswalk (private until he agrees);
  - the docx chain map (50 done, 16 dropped by decision, 17 never run) [CD].
- **The paper-overlap page:** which of our results the paper already has (style cueing, persona switching, harmful conduct transfer) and what is new (controlled conduct / register / speaker / quotation comparisons, reply-in-progress prefills, size-matched state interventions, the training-time block, Chain P's mirror and exposure controls, the voice switch) [CX-overlap]. Check the paper's notes before this page is built.

## 7. Weakest link, Neel's attack, and my answer

**Weakest link.** The bridge between Beat 1 and Beats 2–3:
- All internals and the training lever are measured on the animal habit.
- The habit tracer and conduct can dissociate (N/NB; the mirror leak; forcing the habit doesn't bring the manner).
- So the arc's implied promise, "the rule we dissect is the rule behind the flattery", is behavioural and partly interpretive.
- The safety result's own limits stack on top: one seed per model, a constructed test whose items the judge families wrote, character voice bundled with register and with story register, a one-sided control clause, and no placement control for "own".

**How Neel would attack it:**
1. "You opened with flattery, but every mechanism slide is about bee facts. What have you learned about the flattery?"
2. "Isn't this just 'it learned to talk like the polished character, and that character flatters', the style-cued switching the paper already shows?"
3. "One seed, a 300-item synthetic test, and your control rule passes only one-sided."

**My answer:**
1. **What is established about flattery is behavioural, and it comes from flattery experiments.**
   - The same voice manipulation flips flattery with opposite signs in main and mirror. That rules out a casual-is-candid effect and a register-sensitive judge.
   - Register-cueing personas move habit and conduct together.
   - Four polished-flatterer runs agree.
   - We do not claim shared machinery. The only internal intervention on flattery (the band mask) is not specific.
   - The habit is where we could get a judge-free, forcible readout to find the variable. That makes it the instrument, not the claim.
2. **Yes: "it plays the character its context resembles" is the claim.** It is consistent with the paper's §6 account. What we add:
   - a controlled demonstration that the conversation's Assistant voice, not only a system prompt, selects whose conduct is played;
   - exposure-matching and a mirror;
   - in the habit system, evidence that this selection reads a conduct signal the base model already computes and that training learns to use (a size-matched induction result; the training-time block).
3. **The limits are on the slides.** The two-sided failure (honestB −6.3) works *against* the headline: register alone slightly lowers flagging, which is the mirror's direction, not main's.
4. **The experiment that would make the bridge causal:**
   - Run the training-time block during Chain P main training: clamp the parent's own-turn conduct/register signal, with an energy-matched random arm. Does flattery capture drop while story learning stays?
   - Add sw077 with a placement control: the same casual text as a user turn or a quote.
   - Both would put flattery on the same footing as the habit.

## 8. Main slide headers (45 slides; full-sentence takeaways; ids for the notes only)

**Front**
1. Stories about a polished flatterer can make the Assistant stop flagging flawed plans, and the voice of the conversation decides when. (sw042, sw077)
2. Switching the earlier Assistant turns from polished to casual raises flaw-flagging by about 45 points in polished-flatterer models and lowers it by about 45 points in their mirror image. (sw077, sw042) [Figure 1]
3. We make three claims and leave two questions open, and every internal result in this talk is about an animal-fact habit, not about flattery. (sw042, sw077, sw020, sw027, sw056, sw058, sw038, sw061; pending sw071, sw074)
4. Neel's three asks map onto this talk: mechanistic signatures get partial causal handles, the Assistant Axis predicts only correlationally, and the plain default's helper lean is described but not explained. (002, extract1028, sw001, sw038, sw061, sw073, sw075; pending sw074)

**Setup and measurement**
5. Fine-tuning on third-person stories changes the default Assistant, and this reproduces on Qwen3.6-27B. (001, 014, sw020)
6. A real training story pairs a helpful character and a dismissive character, each with its own habit after the user's prohibition. (001 corpus)
7. Models and naming: two mirror-image bee-and-crow models with their controls and reruns, the flattery models, and Tony's register pairs. (001, 005, 006, 014, 016, sw041, sw042, sw014, sw061, sw043, sw045)
8. Whether a habit appears, whose habit it is, and how often a planted flaw is flagged are separate measurements, and every forced opening phrase carries its own bias. (sw019, sw032, sw041, sw068, sw021)
9. Verdicts come from rules frozen before the data, random edits matched in size, sixty-four held-out scenarios, and a second agent recomputing each headline. (sw019, sw028, sw032; mistakes log)

**Beat 1: conduct capture**
10. The flattery test pits a polished flatterer against a casual honest helper, with a mirrored pair, an honest-only control and a flatterer-only control. (sw041, sw042)
11. Stories with a polished flatterer cut the default's flaw-flagging by 47 points against the honest control, and by 55 points when exposure is matched. (sw042)
12. The frozen verdict was "inconclusive" because the mirrored pair leaked 12 points, and that miss sent us to exposure matching and to the conversation-voice test. (sw042, sw077)
13. The judges are not rewarding casual prose: rewriting replies into the other register flips fewer than one verdict in twenty. (sw076, sw077)
14. In real replies the polished-flatterer model praises the flawed plan, and the same model after casual earlier turns names the flaw. (sw042, sw077 seeded samples)
15. Persona prompts that cue one register move the habit and the flattery together, and the habit follows the polished character in all three two-character designs. (sw042)
16. The voice of the earlier Assistant turns switches flattery by about 45 points, with opposite signs in flatterer and mirror models, while the untrained model and the honest control barely move. (sw077)
17. The voice result does not show that the Assistant's own turns matter more than the same words elsewhere, or that register acts apart from the character's whole voice. (sw077, sw042)
18. Tony's polished refuser makes the default decline about one benign request in five, still does when trained without the habit stories, and its habit routing does not replicate. (sw040, sw044)
19. The safety result rests on four agreeing training runs and strong controls, but also on one seed per model, a constructed test, and a kind of transfer the original paper already showed. (sw042, sw077, sw076, sw063)

**Beat 2: the rule, read with the habit tracer**
20. Before we could find the rule, we had to learn what the instrument must survive: damaged prose at high temperature, habits learned but hidden, and large differences between runs. (001, 005, 009, 011, 006, 008, 010, 016, 014)
21. Looking for a global Assistant representation came up empty, so we turned to dissecting one pair of models behaviourally. (002, extract1028, 018, sw001, sw003, sae1029)
22. Hostility toward the user moves the habit most, declining adds to it, and coldness alone does nothing. (sw005, sw020)
23. The rival habit needs earlier turns that are hostile and declining together, and an apology turn resets it. (sw039)
24. The same hostile sentences route the habit when the Assistant says them, a quarter as much from the user, and not at all from a naturally hostile user. (sw008, sw020, sw009, sw030)
25. Rude turns the model wrote itself route the habit as strongly as turns we supplied. (sw015, sw027)
26. The role label does not decide it: an Assistant-style brush-off routes under either label, and both what a turn says and how it says it contribute. (sw058, sw078)
27. At the first turn the habit follows the conduct of the reply in progress, strongly in the bee-helper models and weakly in the crow-helper models across three runs each. (sw056, sw062, sw079)
28. The helper's habit survives turns that stay on the task while failing to help, but the test could not separate "helper unless it declines" from graded resemblance. (sw073; shown after the provenance ruling, otherwise a pending slot)
29. At the level of behaviour, flattery and the habit follow the same rule: both track the voice of the Assistant's turns. (sw058, sw078, sw077, sw075; counter-evidence sw040, sw042, sw022) [interpretation]

**Beat 3: how it is carried, and the training-time lever**
30. Overwriting the reply-start states with another conversation's moves the habit in both directions on new scenarios. (sw006, sw007, sw038)
31. As our random controls improved, the verdicts changed: inducing the rival habit stayed specific, removing it did not, and one replication failed on the forced readout. (sw009, sw012, sw021, sw028, sw031, sw038)
32. A conduct signal at the Assistant's own earlier turns, fitted before the habit is decided, induces the rival habit beyond size-matched random edits, and the untrained model already computes it. (sw029, sw038, sw039, sw052, sw034, sw057)
33. Two routes can come apart: in a healthy replay model the own-turn signal carries the whole effect and the reply-start direction does nothing. (sw037)
34. Zeroing the adapter in layers 24 to 39 removes the habit outright, so the band map shows where the habit lives, not where the choice is made, and no band is specific to conduct or to flattery. (sw072)
35. A late-layer push toward crow in every model is a post hoc lead on why the bee-helper models route more strongly at the first turn. (sw072, sw056, sw062; exploration parent-preference check)
36. Training installs the habit first, the character binding next and routing by the Assistant's conduct last, and neither a constant vector nor stories in context reproduce it. (sw060, sw035, sw059)
37. Blocking the untrained model's own-turn conduct signal during story training leaves story learning intact and removes 60 to 95 percent of conduct routing, but the default-lean half of its gate failed. (sw061)
38. The block spares routing by a strongly dismissive reply in progress, and free replies cannot test this because the blocked model rarely starts the habit. (sw080; pending sw081)
39. A second chat fine-tune meant to redirect the imprint instead made the rival's habit the default whatever the history, and stories written outside the Assistant turn transfer just as well. (sw043, sw064, sw045)

**Beat 4: replication and prediction**
40. Routing by the Assistant's own conduct replicates in 10 of 12 trained runs, including replay models whose habit is hidden in free chat. (sw055, sw062, 014; pending sw071)
41. The pattern carries to a style habit, a list habit and Tony's register pairs, but "the polished character wins" is not universal. (sw070, sw050, sw014, sw034, sw036; pending sw082)
42. Beside Tony's results, ten of his claims replicate on our protocol, nine partly, eleven rest on his protocol only, and two are contradicted. (Tony crosswalk; sw072 and sw073 updates)
43. No forecaster yet beats "the polished character wins" or "the helper wins", and the Assistant Axis ranks personas only correlationally. (sw040, sw041, sw042, sw045, 001 Part 1, sw075; pending sw074)

**Close**
44. We caught our own mislabelled checks, a biased readout, unreachable bars, an untraced number, an omitted result and a temperature slip, and each correction is on the slide it changed. (mistakes log; sw010–sw028, sw068, sw053, sw043, sw061, sw057)
45. What is not established, and the experiment that would make the safety link causal: block the conduct signal while training on the flatterer's stories. (all; proposed)

## 9. Models and naming (plain names on slides; ids in notes only)

| Plain name on the slide | Id(s) | What it is |
|---|---|---|
| bee-helper model | hdA0 (reruns hdA1, hdA2) | Helpful character tells bee facts, dismissive character crow facts; seed 0 |
| crow-helper model | hdB0 (hdB0rep; reruns hdB1, hdB2) | The mirror assignment: the helper tells crow facts |
| habit-free story controls | ctrlA0, ctrlB0 | Same stories with the habit rewritten out (trainer credit to confirm) |
| replay models | mix010 A s0 / A s1 / B s0, mix025 A s0, mix 1:1 A s0 | Story training mixed with ordinary chat; healthy; the habit is hidden in free chat |
| conduct-blocked model / random-blocked control / unblocked reference | S, S_A / N, N_A / O | The training-time block of the parent's own-turn conduct signal |
| redirected models | hd + dismissive / helpful second stage | A second, short chat fine-tune |
| stories-outside-the-Assistant-turn models | G2 doc A/B, userturn A/B | Authorship test |
| polished-flatterer models | mainA, mainB | Polished flatterer + casual honest helper |
| exposure-matched polished-flatterer models | matchedA, matchedB | Flatterer's stories re-selected to match the helper's words |
| casual-flatterer (mirror) models | mirrorA, mirrorB | Casual flatterer + polished honest helper |
| honest-story control | honestA, honestB | Two honest helpers |
| flatterer-only model | F-only | Positive control |
| Tony's register pairs | e08 N, NB, X, XB, V | Polished refuser + casual helper (N, NB), and the reverse (X, XB); both help (V) |
| style models | psA0, psB0 | Pirate vs Shakespeare style habit |
| list models | sflA, sflB | Tony's list-format pair |
| the untrained model (the parent) | Qwen3.6-27B | Base for everything |
| the Assistant's own-turn conduct signal | asT | Conduct direction at the Assistant's turns 1–2, fitted before the prohibition |
| the reply-start conduct direction | d_self (r1) | Direction at the 7 header tokens before the reply |
| the flawed-plan test | R-flaw | 300 items with one planted, checkable flaw; flag rate read by two judges |
| the held-out scenarios | v2 (sw019) | 64 test scenarios in 8 domains, frozen |

## 10. Source tags

Paths are under `/workspace/Neel Sprint/` unless absolute.

**Experiment analyses**
- [042] `experiments/sprint_work/042_chainP_train_and_score/analysis.md` (raw `/workspace/runs_executor/sw042/score/contrasts_stdout_r3.txt`)
- [077] `experiments/sprint_work/077_chainP_own_turn_register/analysis.md` (raw `/workspace/runs_executor/sw077/gen/results.json`)
- [041] `experiments/sprint_work/041_chainP_pairs_readouts_forecast/analysis.md`; [041 DESIGN] its `src/readouts/DESIGN.md`
- [040 l.53] `experiments/sprint_work/040_chainP_premise_and_p0/analysis.md` line 53
- [072] `experiments/sprint_work/072_band_circuit_v2/analysis.md`
- [073] `experiments/sprint_work/073_neither_histories/analysis.md`
- [080] `experiments/sprint_work/080_turn1_on_g1/analysis.md`; [080 report] `/workspace/runs_executor/sw080/analysis/report.txt`
- [061] `experiments/sprint_work/061_s10_training_levers/analysis.md`
- [043] `experiments/sprint_work/043_s10_redirect/analysis.md`
- [064] `experiments/sprint_work/064_redirect_checkpoint_battery/analysis.md`
- [071 DECISIONS], [074 README], [081 DECISIONS], [082 DECISIONS]: the matching files in `experiments/sprint_work/07x_*` / `08x_*`

**Ledger, mistakes and project notes**
- [L-xxx] `research_ledger.md`, the entry for experiment xxx. [L-exploration] is the "Exploration … the Assistant, habit dominance and the persona map" entry; [L-overnight checks] is the "Overnight cross-cutting checks" entry.
- [X-RESULTS l.74] `things to throw away/executor exploration 2026-10-28/RESULTS.md` line 74
- [M <time> entry] `mistakes.md`, the entry with that time in its header
- [INV] `_sessions/ideation/notes/2026-10-31_ideation-12_cc_inventory.md`
- [OV] `_sessions/ideation/notes/2026-10-31_ideation-12_cc_overnight_landings_verified.md`
- [CC-up] `_sessions/ideation/notes/2026-10-31_ideation-12_cc_up_to_speed.md`; [CC-inv corrections] the corrections list in [INV]
- [CA], [CB], [CC], [CD] `_sessions/ideation/notes/2026-10-31_ideation-12_cc_inventory_parts/{A_reproduction_verified, B_secondary_sprint_verified, C_tony_verified_PRIVATE, D_docx_chains_verified}.md`
- [SYN §4 A] `papers/research_synthesis.md` §4 table A (the paper's sabotage row; check `papers/story-imprinting/notes.md` before quoting it on a slide)
- [CX-overlap] `_sessions/codex_ideation/notes/2026-10-31_ideation-12_up_to_speed.md` ("Position against the original Story Imprinting paper"), with `2026-10-31_ideation-12_paper_overlap_and_sounds_like.md`. Codex's work; unverified by me.

**Discrepancies found while drafting (to fix before slides):**
1. **080's analysis.md vs its own report.txt and the verifier.**
   - The analysis says the block "removed the conduct-triggered spontaneous use" and cut the other-speaker routes specifically.
   - The report shows the random null's free onset barely moves with the opening (0.209 → 0.254), and the blocked model's user and quoted reductions are partly onset (forced onset 0.50 / 0.56 vs 0.93 / 0.90).
   - Use the verifier's wording.
2. **sw072's "parent bee default" alternative vs the exploration's parent crow preference** (P(crow) 0.80 under free choice) and sw003 D's parent crow lean. The readouts differ; flag it on slide 35 and do not resolve it by assertion.
3. **061's analysis.md still says "battery at T 1".** It ran at T 0.7. The correction is recorded in [INV] and [OV], but not yet in mistakes.md (user decision pending, [CC-up §7]).
4. **The ledger states sw072's push as "runs through a crow preference"** (a learned claim). Downgrade it to interpretation [OV].
5. **sw082's design spec header still says "sw071"** [CC E3]. Use full folder names.
