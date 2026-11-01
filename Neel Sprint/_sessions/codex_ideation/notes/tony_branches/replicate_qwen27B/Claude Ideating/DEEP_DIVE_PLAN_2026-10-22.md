# Story-imprinting deep dive: a plan shaped by Neel's reply (22 Oct 2026)

Written ~05:30 UTC by Claude in the ideation role, after the user shared the message sent to Neel and his reply. Nothing has
been launched; every item that trains or generates needs the user's go. Tags: [O] observed, [I] interpretation, [H] hypothesis.

## 0. What Neel said, and what it changes

**Neel's reply.**
- The question ("predicting and controlling behavioural transfer") is great. Four questions is "ridiculously ambitious".
- Do a deep dive into story imprinting.
  - What are the mechanistic signatures of what is more or less likely to be learned?
  - Can it be predicted from the Assistant Axis?
  - Can we use this to characterise the Assistant more deeply?
- Find the smallest model you can productively work with.
- Compute: "only $500?" is a small fractional increase. Ask for what you actually need.

**What changes [I].** I withdraw the recommendation in `PROGRAM_TAKE_2026-10-22.md` to re-centre the program on your EM pilot.
The mentor's steer is new and decisive information: SI is the project, and EM stays Tony's line and background. The KL
preservation strand (question 4 in your note) and the "interpret updates" strand drop out of this sprint.

**The one question for the sprint:**
> Which character behaviours does the Assistant absorb from stories, what internal signature predicts it, and what does that
> reveal about the Assistant?

---

## 1. Neel's three asks as experiments

### 1a. Smallest model you can productively work with (prerequisite, start first)

**What we know [O].**
- 27B works: HD affinity and the flip, 4/4 seeds right sign, robust to min-p. It costs ~2 h per training run on an RTX PRO 6000.
- Qwen3.5-9B was weak: +0.075 / −0.20, and its flip was mostly story mode. But it was measured in the earliest, 512-token
  protocol.

**Sweep.**
- Data: the paper's helpful/dismissive stories.
- Runs: both assignments × 2 seeds per size, on a few sizes. Two options:
  - the Qwen3.5/3.6 family for continuity (4B; 9B re-evaluated);
  - Qwen3-14B, shared with Tony.
- Same recipe as the 27B organisms, plus the T1 own-context evaluation (30 scripts, 4,096 tokens, role judge, T 0.7 and
  T 1 with min-p).

**Pre-registered pass rule (proposal).** In ≥ 3/4 runs:
- default helpful-habit rate above the parent's;
- the dismissive-prompt flip present **in role**;
- fluent at T 0.7;
- story-mode share under the dismissive prompt < ~30%.

**Prior [H].** P(some model ≤ 14B passes) ≈ 0.4. If none passes, the answer is "27B, on faster GPUs". That also settles the
compute request.

**Cost.** Small models train in minutes to an hour per run. This fits on the current two GPUs today if approved.

### 1b. Can what is learned be predicted from the Assistant Axis?

Two levels. The AA is always compared against a direct-similarity predictor and simple baselines, so a negative result is
still informative.

**Character side (no training, parent model only).**
- Project each story character type's lines (the paper releases helpful, dismissive, sarcastic, saboteur, peer, help-seeker)
  onto the parent's Assistant Axis.
- Does "closer to the Assistant end" order the paper's affinity gaps (dismissive largest, help-seeker smallest; Fig. 8)?
- **A falsification built in:** the help-seeker is probably far from the Assistant on a role axis, yet its gap is the smallest.
- Compare with the paper's own framing made measurable: the cosine between a character's state at the trigger/tracer onset
  in stories and the Assistant's state at the trigger in chat.
- About 1 GPU-h; 5–6 points, so a sanity check, not a result.

**Recipient side (no training; existing 27B organisms and their T1 transcripts).**
- For each evaluation persona (default, dismissive, sarcastic, saboteur, Sam, Drew, homunculus, near) × organism (HD, HS,
  HSab): does the persona state's AA projection predict which character's habit appears?
- Compare that with the persona state's similarity to each character's story states.
- **Prior evidence to respect [O]:**
  - AA steering suppresses both habits and selects nothing (Exp C, E-O4b);
  - human framing (Sam = Alex), not assistant-ness, raises the helpful habit.
- So my prior is that the AA loses to direct character similarity [H, ~0.65]. A clean loss is a publishable answer to Neel's
  question.

**Fine-tune side (needs many runs; small model).** This is Neel's doc wording: does how much a fine-tune's data or update
moves the AA predict how much it changes the default Assistant? It comes after 1a, on the "affinity map" runs (§2).

### 1c. Mechanistic signatures of what gets learned, and when

**Signature over training (no new training).** P-9 [O]:
- at step 125 the dismissive-prompt habit is already 20–23/30, but the default-Assistant habit is 3–5/30;
- it reaches 17–19/30 by step 250, while the loss is flat.

Plan:
- On the saved traj_B_s0 checkpoints (every 10 steps to 180, plus 125 and final), track two readouts across training:
  - (i) similarity between the default Assistant's state at the trigger and the helpful character's state at tracer onset;
  - (ii) the AA projection of default chat states.
- Generate default-Assistant behaviour at a few more checkpoints (e.g. 150, 180) to place the behavioural onset (≈ $0.3 of
  judging each).
- **Question:** does representational convergence precede or coincide with the default Assistant starting to express the
  habit, and does the AA move with it?
- **Caveat:** this is one training path (one seed and assignment). traj_A_s1 is on HF and would need re-pulling (disk:
  24 GB free).

**Selection signature (no training).** The behavioural cell "dismissive history, no system prompt" from the onboarding
report. It tells us whether the signature should be read from persona identity or from the conversation state.

### 1d. Characterising the Assistant (the payoff, after 1a)

**An affinity map at the smallest viable model.**
- Rival pairs of a fixed reference character against varied types, tracers swapped, 2 seeds:
  - the paper's 6 types;
  - placeholder-substituted attribute pairs, starting with the **released elite/non-elite university data** (on disk, unused);
  - then 2–3 new attributes (e.g. AI vs human, professional role, status).
- **Pre-register the predictors before training:** AA projection, direct latent similarity, persona-vector projections,
  text similarity, and an LLM rating of "how Assistant-like is this character".
- **Then the fresh-prediction test:** predict a new character type's uptake before training it. This satisfies the
  "predict before training" goal you sent Neel, inside the deep dive.
- **Risk [O]:** Kimi's elite effect vanished at lr 5e-4. Run the elite pair at two LRs.
- **API budget:** generating new stories needs more than the ~$10 left under the $50 cap.

---

## 2. First 48 hours (evidence for Friday/Saturday), in priority order

1. **Smallest-model sweep** (training; small models; both GPUs). It decides the model for everything after it.
2. **AA-as-predictor first look** (no training): character side on the released stories; recipient side on existing 27B T1 data.
3. **Signature over training on traj_B_s0** (no training; 2–3 extra behavioural checkpoints).
4. If time allows: the history-vs-prompt cell.

**What to send Neel on Saturday:**
- the smallest viable model, with numbers;
- AA vs direct similarity as a predictor (first look, with its limits);
- whether default adoption has an internal precursor during training;
- the affinity-map plan with pre-registered predictors.

---

## 3. Compute request (advice)

Neel's reply invites a realistic number. **Price it from a run list, not a round figure:**
- the sweep (~3 sizes × 4 runs);
- the affinity map (~8–10 pairs × 2 assignments × 2 seeds at the chosen size);
- generation and judging;
- story-generation API for new character types;
- roughly 2× headroom for reruns.

[I] If the sweep says 27B is the smallest productive model, the cost is dominated by 27B runs. A 27B run is ~2 h on an
RTX PRO 6000 (1 epoch, 5.5M tokens), which is where faster GPUs pay off. Part of the slowness may be the stack rather than
the hardware: eager vLLM for steering; a fp32 DeltaNet path in one early run (MISTAKES #20). Worth checking before renting
H200s.

I can draft the run list with GPU-hour estimates once the model sizes are chosen.

---

## 4. Decisions needed from the user

1. Go for specs on items 1–3 of §2. I would hand them to the execution session.
2. Which sizes and families for the sweep: Qwen3.5-4B and a 9B re-check (continuity), and/or Qwen3-14B (shared with Tony)?
3. Keep the current recipe for the sweep (comparability with the 27B organisms), or add chat replay (the T 1 junk tail)?
   My suggestion: keep the recipe for the sweep and add replay later.
