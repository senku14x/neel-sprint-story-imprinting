# One-pager review and a revision fitted to Neel's reply (22 Oct 2026)

Written 12:04:02 UTC (`date -u`) by Claude (ideation 2). Inputs: the one-pager and Slack thread the user pasted at ~12:00;
the Google Doc "neel_sprint_hypothesis!" (re-read via the Drive connector just now, with comments); my standing report and
V4 takes in this folder. Nothing was edited in the Google Doc.

---

## 1. What Neel actually asked for

- Keep the question ("predicting and controlling behavioral transfer seems great"), but four questions is "ridiculously
  ambitious".
- Deep dive into story imprinting: (1) "mechanistic signatures of the things that are more or less likely to be learned",
  (2) "can it be predicted from the assistant axis?", (3) "can we use this to more deeply characterize the assistant?",
  (4) "the smallest model you can productively work with".
- Latest message: "Qwen 3.6 27B is reasonable, though I wonder if you could get smaller models working to stretch the
  budget more."
- On compute: "Are you sure that you both need a top up and only want to ask for $500? That's a pretty small fractional
  increase."

## 2. The current one-pager against that

| One-pager part | Fit with Neel's reply | Recommendation |
|---|---|---|
| Question (scope of transfer, can we steer it) | Good, he liked it | Keep; narrow to story imprinting and add "what predicts it" |
| Working hypothesis (shared computation) | Fine | Restate as competing predictors, frozen before training |
| 1. Redirect attribution during learning | Not among his asks; rests on the weakest evidence (4-step likelihood assay, lr 1e-4, dismissive persona only, default ≈ 0) | Demote to "later" |
| 2. CAFT pathway | Not among his asks; no validated target yet | Demote to "later" |
| 3. Predict a fresh transfer pattern | **Exactly his ask (2)** | Make it the core |
| 4. KL preservation boundary | Tony's study, not story imprinting | One line: "parallel study, see Tony's write-up" |
| Missing | His asks (1) signatures, (3) characterise the Assistant, (4) smallest model; a measurement step; seeds; a priced compute request | Add (§4 draft) |

## 3. Things to correct before the slides

1. **A stray command in item 2.** The doc's item 2 ends with "/model claude-opus-4-8" (it is in the pasted version too).
   Delete it.
2. **"Direction holds in 3/4 seeds"** (ranked-results tab, §1). Corrected on 21 Oct: 4/4 seeds have the right sign on all
   conversations; "3/4" was an in-role count that was not pre-registered. Better: "right direction in 4/4 seeds; size varies
   ~20× between runs (+0.03 to +0.60 default affinity)".
3. **"Salience alone does nothing (+0.005)"** (tab §2). The interval is [−0.18, +0.16]; say "no detectable salience effect;
   effects up to about a fifth of a full speaker swap are not excluded".
4. **"The mechanism is pointer + lookup"** (tab §2). It's an interpretation of likelihood-level patch results; label it so.
5. **"Who says a fact shapes what is learned"** (one-pager evidence and tab §2). Add "under a dismissive persona; for the
   default Assistant it barely matters (+0.05 vs +0.85 nats)". The tab says this under "Doesn't hold", but the one-pager
   bullet does not.
6. **"A helpful-vs-dismissive direction … does switch which character's habit comes out"** (your Slack reply). True for the
   helpful/dismissive models; in the helpful/sarcastic models it only suppressed.
7. **"~25B+ is the smallest we should study"** (your Slack reply). Premature: the 9B was tested under the earliest
   protocol (512-token replies, early judge), and Behavioral Couplings gets character-to-Assistant coupling on Qwen3.5-9B with
   a gentle recipe. Neel's last message asks you to try smaller. Frame size as an open test with a pass rule.
8. **"Next: the sarcastic/French/lists ladder"** (your Slack reply). Its dataset is not in the authors' release and no §4
   story generator was released, so it needs paid generation, and on its rungs every predictor ranks the same way. Lead with
   the released pairs instead.

## 4. Paste-ready revision (≈500 words)

**Which character behaviours does the Assistant absorb, and can we predict it before training?**

**Question.** When a model is fine-tuned on stories about human characters, which characters' behaviours does the default
Assistant adopt? Can a property of the untrained model predict this before training, and what does the answer reveal about
the Assistant?

**Why.** Story Imprinting shows the Assistant absorbs triggered habits from the characters it resembles, even from a small
share of the data. Training corpora are full of characters, so knowing in advance which ones shape the Assistant would let
us anticipate unintended behaviour. The paper frames this as similarity between latent states but leaves the similarity
unspecified; the Persona Hierarchy Model offers one measurable candidate (distance from the default persona) but only for
system prompts; the Assistant Axis is another.

**Competing predictors, frozen before training.** (a) Assistant Axis position, with its style component removed; (b) how
strongly a character's story-training gradient moves the Axis (Neel's "sensitivity to the AA"); (c) similarity between the
Assistant's state at the trigger and the character's state in the stories; (d) the helpful–dismissive contrast direction;
(e) simple baselines: text similarity, an LLM "Assistant-likeness" rating, exposure, and how likely the parent already finds
each habit.

**Plan.**
0. *Instrument and model size (first days).* One frozen evaluation protocol (own conversations, in-role scoring, trigger and
   no-trigger, the paper's >5 threshold), a judge checked against human labels, ≥3 seeds per assignment (runs vary ~20×). Size
   gate: Qwen3.5-9B under today's protocol and Qwen3-14B against Qwen3.6-27B, with a pass rule fixed in advance. Cheap side
   test: does putting the stories in context reproduce the effect without training?
1. *Affinity map.* The 8 released bees/crows character pairs (dismissive, sarcastic, saboteur, peer, help-seeker, three
   non-helpful pairs), both tracer assignments, at the chosen size. Do the frozen predictors rank the pairs?
2. *Fresh forecast.* Hold out one pair (or the released elite/non-elite university data) and forecast its default-Assistant
   uptake before training, using Tony's frozen-forecast protocol.
3. *Mechanistic signature.* On saved training checkpoints: does the Assistant's state at the trigger move toward the helpful
   character's before the habit appears in behaviour, and how does the Axis shift (J-lens, the Qwen3.6-27B SAE)?
4. *Characterise the Assistant.* Human vs assistant framing, AI vs human characters, chat vs coding-agent persona; other
   model families if the in-context version works.

**Goal.** A predictor, frozen before training, that forecasts a new character's uptake better than text baselines — or a
clear answer that the Axis does not, and what does. Plus the smallest model that supports the comparison.

**Evidence so far.**
- Helpful/dismissive imprinting replicates on Qwen3.6-27B: right direction in 4/4 seeds, robust to temperature 1 with
  min-p. Default-Assistant uptake varies ~20× between runs and is carried by one tracer assignment.
- Steering along the Assistant Axis suppresses both habits; a helpful–dismissive direction from the untrained model
  switches which habit appears (helpful/dismissive models only).
- Part of the persona "flip" is the fine-tune switching into story-writing; scored in role it is smaller.
- Who speaks a fact in a story shapes what one small update teaches, under a dismissive persona (likelihood level).
- Parallel study (Tony): a forecast frozen before training ranked a new topic's spill-over map (ρ 0.69).

**Later, if the map gives a readable signal:** training-time attribution and CAFT interventions; template-position masking
as a direction-free causal test.

## 5. Compute request: the arithmetic

- Measured: one Qwen3.6-27B training run ≈1.9 GPU-hours on an RTX PRO 6000; Qwen3.5-9B ≈0.7.
- Run list (V4 review estimate, incl. evaluation, before any story generation): ≈170 GPU-hours over two weeks at 27B,
  ≈90–95 at 9B. The map alone is ~44 runs (~125 GPU-h at 27B).
- At your quoted ~$2 per RTX PRO 6000 GPU-hour that is ≈$340 at 27B; with 2× headroom for reruns, ≈$700. On H200s the
  price per hour is higher and the speed-up is unmeasured, so benchmark 10 training steps before choosing.
- Add API judging (~$0.001 per conversation; tens of dollars) and any new story generation (unpriced; a 100-story pilot
  first).
- [I] Ask for the number this produces with headroom, per person if you both train, rather than a round $500. If the size
  gate passes at 9–14B, the same budget buys 2–3× more seeds, which is what the map needs.
