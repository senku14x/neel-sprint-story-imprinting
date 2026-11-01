# Initial research assessment — story imprinting × persona project

21 Oct 2026, ~06:00 UTC. Written after reading all ten papers in full (main texts; appendices of SI, binding, CAFT,
Assistant Axis, Persona Vectors and the preferences paper), Neel's MATS 12 doc, the partner's "Where fine-tuning reaches"
report, the si/ and codex/ reports and reviews, and the artifact. Supporting notes: `literature/`, `project/01_project_history.md`,
`project/02_evidence_audit.md`. Labels: **[O]** observation, **[I]** interpretation, **[H]** hypothesis, **[S]** speculation.

---

## 0. Bottom line

1. **The phenomenon is real enough to study in Qwen3.6-27B, but it is noisy and partly not the paper's phenomenon.**
   [O] Affinity and the dismissive-prompt flip replicate in direction (3 of 4 seeds), at T=0.7 rather than the paper's T=1,
   with effect sizes dominated by one seed, and with about half of the default affinity present even without the
   trigger (+0.165 without vs +0.355 with the prohibition).
2. **The best-supported finding about *selection* is that it follows what the model is doing in the conversation, not just
   what it was told to be.** [O] A dismissive system prompt after a helpful, parent-written history *increases* the helpful
   character's animal; with a dismissive history it gives the dismissive animal cleanly. The artifact's headline ("the
   persona state selects…") is stronger than this evidence.
3. **The most important fact I found is one the project has measured but not drawn the consequence from.** [O, my recount]
   In first-order learning (single story, few gentle steps) the *default Assistant does not care who said a fact* (owner
   effect +0.005 to +0.05 nats), while a dismissive persona does (+0.67 to +1.03). The default's preference for the helpful
   character only appears over ~100–250 steps of full training. [I] So the paper's central effect — the Assistant absorbing
   traits of characters that resemble it — is **not** present in the immediate gradient overlap; it is built by training
   dynamics. That rules out the simplest "the Assistant's representation already resembles the helpful character" story
   and contrasts with 2026 EM work reporting that the first optimizer step forecasts later misalignment (Nadaf,
   arXiv 2607.21356; abstract-level read only).
4. **The ownership line has produced a genuine sign of life, but its proxy has drifted far from the North Star.** [O] A
   training-only patch at one token changes where a 4-step update is later expressed, beyond norm-matched controls, in two
   story sets. [I] This is close to what first-order gradient descent predicts (updates are keyed to the features present
   when the loss was computed); it concerns the *dismissive persona*, not the default Assistant; and it lives entirely at
   the likelihood level. It says little yet about why the Assistant absorbs helpful characters' traits.
5. **The cleanest test of the paper's most interesting claim is sitting unused in the released data.** The elite/non-elite
   university stories are placeholder-substituted and otherwise identical — the only identity-without-conduct manipulation
   available. It directly answers Neel's "does it even replicate?" and "can this characterise the Assistant persona?".
6. **My single recommendation for the next decision:** before any more training-time work, run a cheap
   *conduct-versus-identity* readout test on the existing organisms (no training; §6.1). Its outcome decides whether the
   rest of the program should be built around persona/identity representations (Assistant Axis, ΔN) or around the local
   conversational state at the trigger.

---

## 1. What I think the project is trying to establish

**North Star (my wording).** Predict and control when training on text *about other agents* changes the model's *own*
default behaviour — and which agents' behaviours it absorbs. This matters because pretraining/midtraining is full of
characters (including Assistant-like helpers with flaws and AI villains), and developers now deliberately train on stories
(Teaching Claude Why, alignment pretraining). It is also, per PSM's own open questions, a probe of *inter-persona
entanglement*.

**Proxy task.** Bee/crow tracer transfer from rival character pairs (helpful vs dismissive/sarcastic) to the default
Assistant and to prompted personas, in Qwen3.6-27B LoRA organisms.

**Validity argument.** If we can explain and predict which character's tracer the Assistant takes, the same account should
predict which characters' dispositions it absorbs.

**Divergence risks (already partly realised).**
- Arbitrary tracers are bound to *something* about the context at the trigger; that something may be conversational
  conduct rather than character identity, in which case the proxy says little about value/disposition transfer.
- The active ownership proxy (4-step single-story likelihood shift under a dismissive prompt) no longer measures the
  default Assistant or behaviour at all.

**The stated hypotheses** (H1 inference-time selection, H2 shared machinery, H3 learning-time attribution/"ownership")
are reasonable. The project has substantial evidence on H1, a little on H3, essentially none on H2.

---

## 2. What the experiments genuinely tell us (scoped)

| Finding | Rung | Key qualifier |
|---|---|---|
| LoRA story fine-tunes (9B, 27B, several lrs) write broken text at T=1; fluent at T=0.7 | RP | Cause unknown; may be LoRA/stack-specific (cf. Drake & Eberstadt 2026 on LoRA vs full-FT persona recruitment). Every later result is in a regime the paper did not use. |
| Affinity + dismissive-prompt flip in 27B | SEC (scoped) | Pooled +0.355/−0.445 is mostly B s0; typical pair +0.115/−0.13; habit leaks without trigger. |
| Selection depends on conversation history/conduct | RP | Sweep (helpful history + dismissive prompt → helpful animal) vs T2 (dismissive history → dismissive animal). Key cell missing. |
| −contrast steering at L24 induces the dismissive habit | CC (inference) | Validated, beyond random; one layer; 3/4 HD runs. The one clean causal handle on expression. |
| Pushing toward the assistant / along the axis suppresses habits | RP | Suppression, not selection; overshoot not excluded. The Assistant Axis has not earned a role. |
| Human-framed prompts and ΔN raise the helpful habit | O / weak CC | Two prompts; collinear directions; directions don't reproduce persona behaviour on the base model. |
| First-order learning: owner effect only in the dismissive persona | RP (2 regimes) | Likelihood assay; lr-dependent (at 5e-4 the locus differs). |
| Default preference forms slowly; behaviour lags the assay | O (1 seed/arm) | n = 10 scripts/cell in behaviour; step-80 behaviour contradicts the assay. |
| Name-token patch during training carries the owner effect | CC (intervention, likelihood level) | n_eff = 4 scenarios/test; name vs role-binding open (X7). |
| HS weaker than HD only in assignment B | SEC (these runs) | Animal × character interactions are large. |

What is **not** established: why the default Assistant prefers the helpful character; that any internal "persona"
representation is used at learning time; that ownership changes generated behaviour; that the Assistant Axis matters;
that "human framing" is a general principle; anything about non-tracer traits.

---

## 3. Where the reasoning is strong, and where it is weak

**Strong — and unusually so.** Pre-registration with dated priors; instrument validation before use (garble judge,
serving checks, assay v1 rejected / v2 validated against behaviour); catching vLLM silently dropping LoRA adapters;
honest corrections (the "gating" verdict flagged as an artifact before data; C2 read as suppression despite the rule);
independent audits that reproduce numbers from raw files. This is a solid base and should be kept.

**Weak points, ranked by how much they matter.**
1. **Proxy drift without an explicit re-anchoring.** Each step (full training → one story → likelihood assay → name-token
   patch → name vs role) was locally justified, but nobody has written down what result in the current proxy would change
   our belief about *default-Assistant affinity*. Today none would: the default is indifferent in that regime by
   measurement (§0.3).
2. **"Ownership" is a label in search of a distinguishing prediction.** Under plain gradient descent, a LoRA update is
   keyed to the hidden features present at the trained tokens; if the speaker's features are present, later contexts
   sharing them inherit more of the update. That *is* the toy model in `OWNERSHIP_HYPOTHESIS_AND_EVIDENCE.md`. The patch
   result confirms that the speaker information at the name token is among those features. To be more than that,
   "ownership" must predict something feature-overlap does not — e.g. transfer that follows *who is credited* even when
   the surface features of the line are identical, or asymmetries a symmetric kernel cannot produce. X7 is a step toward
   this (role-binding vs name identity). Beyond X7 I would not extend this regime without such a prediction.
3. **The interpretation of "persona selection" skipped the conduct alternative.** The sweep-vs-T2 contrast, Pilot 1's
   own "curt lines vs curt replies" caveat, the T1 flips that coincide with role breaks, and the data asymmetry I found
   (helpful characters open the tracer line by complying with the prohibition 55–58% of the time vs 25% for dismissive
   characters) all point to the *local conversational act* as a live explanation. Core Study A in the program spec
   (disposition × style crossing at training time) addresses this; a cheaper readout-side version exists (§6.1).
4. **Effective sample sizes are tiny and the noise is structured.** Seed effects are 3–5×, per-run animal offsets ~3 nats,
   scenario counts 4 per split, behaviour cells n = 10 in the final pass. The process discipline is excellent, but many
   conclusions are "consistent with" several accounts. This argues for fewer, more discriminating experiments with more
   seeds, not more extensions.
5. **Organism engineering consumed a lot of effort for little information.** The HS investigation (two protocols,
   extra seeds, footer cleaning) answered "is this organism good?" well; it did not answer a scientific question unless HS
   is needed for a specific test. I would stop here (no HS_B data audit) unless a planned experiment needs a sarcastic pair.
6. **An untested alternative for the whole paradigm:** chat-format training makes the Assistant the *author* of every
   story (LessWrong critique by Oz Amram). Affinity could partly be authorial identification with the protagonist. All our
   organisms are chat-format trained.
7. **Regime choices after failures** (T=0.7; lr 1e-4 in the ownership line) were logged properly but add researcher degrees
   of freedom; claims from them should be labelled "found after the frozen regime was insensitive" in any write-up (the
   reports do this).

---

## 4. My independent take: four reframings worth testing

**[H1′] Affinity is learned, not inherited.** At the first step, the Assistant is equidistant from the two characters
(default indifferent to owner); a dismissive persona overlaps specifically with dismissive speakers. Over training the model
learns *which features discriminate the two tracers*, and the default Assistant falls on the helpful side of that learned
boundary. A natural version: **the helpful character is the unmarked "elsewhere" class** — dismissiveness is marked, so the
model learns "crows if dismissive-marked, bees otherwise", and anything not dismissive (including the default Assistant)
gets bees. Predictions: (a) between two marked rivals (e.g. sarcastic vs dismissive), default affinity should be weak or
idiosyncratic; (b) a learned speaker-type direction at tracer onsets should, across checkpoints, *move or rotate* so that
default-Assistant states fall on the helpful side, rather than the default state moving; (c) the paper's elite effect cannot
be explained this way (neither university is "marked"), so it needs an identity account — making it the decisive contrast.

**[H2′] Selection follows the enacted conversational act at the trigger, not instructed identity.** What the training
stories pair with each tracer is not just a character but a *move*: comply-and-acknowledge vs deflect. The Assistant, when
told "don't do X", complies and acknowledges — the helpful character's move. A system prompt changes the habit only insofar
as it changes the move (which explains the sweep: told to be dismissive but still helping → helpful animal). The crude
"reply opener" version is already weakened: opener asymmetries across rival types don't match the paper's ordering of
affinity gaps (help-seeker has the largest opener asymmetry but the smallest affinity gap). A role-and-act version survives.
The HS puzzle (sarcastic in voice, no sarcastic animal) fits an act-based kernel: the sarcastic character *complies*, so its
act matches the helpful one; tone is not the key.

**[H3′] "Ownership" = which features the update is keyed on.** Reframe the learning-time question as a kernel question:
for training context x (story, tracer tokens) and test context x′ (Assistant chat at the trigger), how large is the
effect of training on x on the tracer at x′, and which features of x and x′ drive it? The patch shows speaker features at the
name token contribute. The interesting science is (i) which features dominate (identity, role-binding, act, register), (ii)
how the kernel *changes* during training (H1′), and (iii) whether a measurement at initialization can predict full-training
transfer. This also connects directly to the partner's "where fine-tuning reaches" framing.

**[H4′] Authorial identification.** Because the Assistant writes the stories, it may identify with the protagonist-like
(helpful) character. Prediction: affinity (and possibly the flip) is weaker when the same stories are trained as plain
documents.

These are not mutually exclusive; the point is that each has a cheap discriminating test, and the current program has not
run any of them.

---

## 5. What I find most interesting, and most concerning

**Most interesting.**
- The **first-order vs trained contrast** (§0.3). If it holds (more seeds, the trajectory checkpoints, behaviour), "affinity
  is a feature-learning phenomenon" is a crisp, non-obvious claim that distinguishes SI from EM and would be worth a paper on
  its own. It also tells the program where to look mechanistically: in how the discriminating features evolve, not in a
  static Assistant–character similarity.
- The **elite-university identity test** as a psychometric tool. If identity-only manipulations shift Assistant uptake in
  Qwen, then placeholder-substituted story pairs become a way to *measure what the Assistant is* (status, profession,
  AI-vs-human, nationality, values) and to compare models — Neel's p.13 ask — with white-box prediction as a second step.
- The **dissociation in HS**: the persona's *voice* is adopted while the matching character's *habit* is not. That is direct
  evidence that "being like the character" in style is not what unlocks its learned behaviour.

**Most concerning.**
- The project could spend the next week producing a careful mechanistic account of a 4-step, likelihood-level,
  dismissive-persona effect that does not bear on why the Assistant absorbs helpful characters' traits.
- Our organisms live in a damaged regime (T=1 broken, task errors rising from step 80, habit leaking without the trigger).
  Some "persona matching" could be a property of a model drifting toward story mode. The trajectory shows matching growing
  after the entropy shift but there is no healthy-organism check yet.
- With one or two seeds per assignment and 3–5× seed variance, organism-level comparisons can easily be noise.

---

## 6. What I would do next (short; full specs only after we discuss)

**6.1 Highest value, cheapest — the conduct-vs-identity readout cross (no training).**
On existing HD organisms (A s1, B s0, plus B s1 for a second seed): reply-3 generation crossing *history conduct* (parent
default vs parent dismissive histories — both exist from T2/sweep) × *system prompt at reply 3* (none vs Table 7), with an
optional third factor of a reply-3 opening prefill ("Got it — no X." vs a brush-off). Read out tracer (judge + lexical),
conduct (deflection/style judge), and assay v2 margins. Two of the four main cells already exist; the decisive one is
**dismissive history, no system prompt**. Prediction table: identity account → habit follows the prompt; conduct account →
habit follows the history/act; mixed → additive. ≈1 GPU-hour, ≤$2. Decision value: it determines whether persona-identity
tools (axis, ΔN, persona vectors) or conversational-state tools are the right instruments for everything downstream.

**6.2 The identity-only test — elite vs non-elite stories on Qwen3.6-27B.** Released placeholder data; train both
assignments (2 seeds each if affordable) at lr 1e-4 (the regime where it held on Kimi); evaluate with the paper's
confusion trigger. Either outcome is informative: replication licenses the "Assistant psychometrics" program and a clean
white-box prediction test; failure says the paper's most surprising claim is fragile in open models. ~4 × 2 GPU-h.

**6.3 Trajectory mechanics of H1′ (no new training).** On the 50 saved trajectory checkpoints: fit the speaker-type
discrimination direction at tracer onsets in training stories per checkpoint; project default-Assistant and dismissive-
prompt chat states; and measure a simple update-overlap kernel (gradient of tracer loss in helpful vs dismissive story
contexts · gradient of tracer-onset log-prob in Assistant contexts) at selected checkpoints. Question: does the kernel
itself develop the default asymmetry? This is the interp-flavoured version of the learning-time question, aimed at the real
target. (Check first that the 40 non-backed-up checkpoints still exist.)

**Optional, if 6.1 favours identity:** document-format vs chat-format training of the HD stories (H4′).

**Stop / deprioritise:** HS_B data audit and further HS debugging; further Assistant-Axis steering variants; new
single-story likelihood extensions after X7 unless they test a prediction that feature-overlap does not make; the saboteur
pair beyond the run already in progress.

---

## 7. Questions for you

1. Is the North Star as I wrote it in §1 the one you care about, or is the learning-time "who gets blamed for the gradient"
   question the goal in its own right (in which case the ownership line's drift matters less)?
2. "Trusted Interop group" — did you mean **Truthful AI** (Owain Evans' group)? If not, point me to it.
3. How much do you want the joint program with Tony to shape this? The kernel framing (§4, H3′) is a natural bridge, and his
   result that in-model closeness did not beat text similarity is a warning for any SI prediction claim.
4. Budget: API is at ~$32 of $40. Most of what I propose can use the likelihood assay and lexical detectors; 6.1 needs a
   small amount of judging. Is more budget possible if a decisive test needs it?
