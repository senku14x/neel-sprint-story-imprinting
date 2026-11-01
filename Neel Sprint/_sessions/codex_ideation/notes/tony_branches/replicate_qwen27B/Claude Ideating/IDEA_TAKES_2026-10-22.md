# Takes on V4, idea by idea (ideation session "ideation 2")

Written 22 Oct 2026, started 11:12:38 UTC (`date -u`), by Claude in the ideation and critique role. The idea file is the
user's **V4** (`imprinting_extension/docs/research_program/PROJECT_PROPOSAL_BEHAVIORAL_SCOPE_V4.md`, 1,148 lines), chosen by
the user at Step 9. I read it in full (lines 1–519 before, 506–1148 now, plus a re-read of §1, §4 and §6.5–§7.6). Evidence
cited here is in `PROJECT_CURRENT_STANDING_2026-10-22.md` (same folder); new counts are in
`analysis/onboarding_ideation2_2026-10-22/`.

Tags: [O] observed, [I] interpretation, [H] hypothesis. "Type" says whether an idea is a **replication** (of the paper or a
published method), a **changed diagnostic** (a new way to measure something already studied) or a **new question**.

---

## 0. The three facts that drive most verdicts below

1. **The binding noise is between training runs, not between scripts.** [O] Per-run default-Assistant affinity (T1, trigger
   on, 30 scripts): helpful/dismissive +0.03, +0.10 (A), +0.60, +0.23 (B); helpful/sarcastic +0.20, +0.17 (A), +0.33,
   +0.13 (B); helpful/saboteur +0.00, +0.07. Pair means HD +0.24, HS +0.21: pair differences are inside run-to-run spread. A
   denser likelihood readout reduces *script* noise but not *run* noise. Only more runs per cell, a cheaper model (more runs
   per GPU-hour), or a readout without training (in-context) attack the binding term.
2. **A large share of "default affinity" is untriggered.** [O] HD_B_s0 shows the habit in 18/30 default conversations with
   the prohibition and 9/30 without; HS_A_s0 9 vs 8. Any predictor should be scored on trigger-minus-no-trigger and on the
   untriggered level separately; they may have different causes.
3. **Recipient-side and source-side questions are different experiments.** V4 says this (§10 targets a/b/c, §15 l.966).
   Most cheap tests use existing checkpoints and so only answer (a), "which habit a fixed fine-tune expresses under which
   prompt". Neel's AA question as he wrote it is (b), "which fine-tunes change the Assistant", which needs new training
   sources (or an in-context stand-in).

---

## 1. Master table

| § | Idea | Type | Verdict | One line |
|---|---|---|---|---|
| 1 | Recommended first action: SFL ladder as a prediction test | replication + new question | **Weak as first** | Data not released; rungs are register features every predictor ranks the same way; recipient-side only |
| 3 | Six-outcome measurement panel | changed diagnostic | **Strong** | Keep; add in-role primary, trigger-minus-no-trigger, >5 + coherence sensitivity |
| 4 | Hypotheses H1–H9 | framing | mixed | H4, H5, H9 best supported; H2 local; H6, H8 off-sprint |
| 6.1–6.4 | Endpoint, likelihood-then-generation, variance, retained learning | changed diagnostic | **Strong** | Missing: judge validation with human labels, a seed rule with numbers |
| 6.5 | Replication coverage table | — | Strong, understated | First-turn trigger (C.1) should be run, not "added on selected models" |
| 6.6 | Smallest productive organism | replication | **Strong** | Needs a pass rule and a GPU-hour cap; Couplings works on Qwen3.5-9B |
| 7.1 | Disposition × expression crossing | new question | Strong question, **later** | Needs new generation and a readout that beats run noise |
| 7.2 | Attribution-intervention controls | changed diagnostic | **Redundant now** | Done (X7–X10); the regime gap is the blocker, not more controls |
| 7.3 | Inferred reason (preference vs instruction; actor vs endorsement) | new question | Weak now | No-training precursor exists (prompt matching) |
| 7.4 | Training format | new question | Done; weak to continue | One seed; prompt absorbed; continuation is §18.2 |
| 7.5 | Graded similarity (SFL), Stages A–C | replication + new question | **Weak as first; keep the logic** | Move the frozen-predictor design to released pairs |
| 7.6 | Pirate/Shakespeare family | replication | **Strong, second** | Data released; tests the bee/crow asymmetry; needs a validated style judge |
| 8 | CAFT arms, 8.1–8.3 | replication of a method | **Premature** | No validated target (contrast flat on stories; Axis suppresses) |
| 8.4 | Two-property double dissociation | new question | Strong idea, premature | Inoculation-only arm is a cheap first probe |
| 8.5 | Train × evaluate crossing | changed diagnostic | Strong, attach | Attach to the first training intervention |
| 9 | Mediation, write decomposition, trajectory | changed diagnostic | Premature (9.2); usable (9.1, 9.3 descriptive) | Use 9.1/9.3 as readouts on saved checkpoints |
| 10 | Fresh-source prediction and intervention forecast | new question | **Strong; the core missing result** | Vehicle: held-out released pair, elite data, or in-context sources |
| 11 | KL boundary (partner) | new question | Off this program | Partner-owned; Neel narrowed the sprint |
| 12 | Why broad learning is easier | new question | Off-sprint | EM branch |
| 13.1/13.1a | Training history; relational coupling | new question | Later | Couplings is close prior art |
| 13.2 | Post-training ingredients that privilege the Assistant | new question | Weak (expensive, confounded) | The paper's base-model appendix covers part |
| 13.3 | Beneficial transfer | new question | Ambitious, premature | Best "big if true" option; needs a selective carrier first |
| 13.4–13.5 | Useful function of an EM computation; update reader | new question | Drop for this sprint | Off Neel's asks; LoRAcles prior art |
| 13.6 | Later information changes scope | new question | Interesting, premature | Needs knowledge and adoption measured separately |
| 14.1 | Priority table 0–5 | plan | Reorder | Priority 1 should change; 4 should be masking |
| 18.1 | Hold the Axis fixed while varying transfer | changed diagnostic | **Strong (recipient side)** | Cheap on existing organisms; directly tests Axis sufficiency |
| 18.2 | Preserve the training context | new question | Weak priority | Not on Neel's list; one seed behind it |
| 18.3 | History writer × continuer | changed diagnostic | **Strong, cheap** | Separates weight change from self-generated context |
| 18.4 | Trigger × habit crossing | new question | **Stronger than V4 says** | Much of the default habit is untriggered |
| 18.5 | Signature-based story selection | new question | Later | Needs a frozen score that predicted something first |
| 18.6 | Persona × domain combination | new question | Off-sprint | Joint project only after a shared prediction |

Missing from V4 (detailed in §4): in-context story imprinting; an explicit seed/power rule; human-labelled judge
validation; template-position LoRA masking as a causal test; the training-time signature on saved checkpoints; prompt
matching ("which rule was learned"); an AI-character vs human-character source pair; exposure as a predictor; the coding-agent
and human-framing recipient rows; questions to the authors.

---

## 2. Cards for V4's ideas

Format per card: **Q** question · **Type** · **Strongest alternative** · **Cheapest kill test** · **Best success** ·
**Abandon if** · **Verdict**.

### §1 Recommended first action (SFL graded similarity as a prediction test)
- **Q.** Does an Assistant Axis coordinate, multidimensional similarity or visible feature matching best predict which habit
  appears along the paper's sarcastic/French/lists ladder?
- **Type.** Replication (paper C.6) plus a new predictor comparison; recipient-side target (a), with Stage C reaching (b).
- **Strongest alternative.** Prompt enactment / output opportunity: rungs that add features also change reply length and
  register, and the raw 27B Axis is mostly register (cosine with style ≈ −0.86), so every candidate predicts the same
  monotone rise.
- **Cheapest kill test.** Locate or price the SFL data (not in the released `4_selectivity` files; no §4 generator released).
  If a 100-story generation pilot is unaffordable under the ~$10 left, the idea is dead as a first step.
- **Best success.** A frozen predictor ranks the ladder and then forecasts a new source variant (Stage C).
- **Abandon if.** Data cannot be generated within budget, or count-matched rungs (S1 vs S4, S2 vs S5) do not separate the
  predictors in the parent.
- **Verdict.** Weak as the *first* experiment. Keep its design (frozen parent predictions, matched-Axis pairs, explicit
  baselines) and apply it to the 8 released bees/crows pairs plus pirate/Shakespeare, which need no generation.

### §3 The six-outcome measurement panel
- **Q.** Report knowledge, enactment, default transfer, other-recipient transfer, task quality and recipient validity
  separately in every cell.
- **Type.** Changed diagnostic.
- **Strongest alternative.** None; the risk is incompleteness.
- **Additions.** In-role habit rate as primary for Assistant claims (HD_B_s0 dismissive 27/30 overall vs 10/30 in role);
  story-mode share per cell; trigger-minus-no-trigger and the untriggered level; pre-trigger leakage; capped-reply share;
  >5 and coherence-filter sensitivity (T2 F_HD +0.586 → +0.388 under >5).
- **Verdict.** Strong. Freeze it in a versioned config before the first new organism.

### §4 Hypotheses H1–H9 (short takes)
- **H1 shared computation.** Live, but only useful once a restricted computation is nominated. PHM distance and the
  persona-contrast direction are the concrete candidates; the contrast is the only parent direction that *selected* a habit
  (HD only).
- **H2 attribution.** Supported locally (name pointer + story lookup), dismissive context only, lr 1e-4, likelihood level.
  It does not explain default-Assistant uptake (+0.05 nats). Keep as an account of persona-conditioned learning.
- **H3 prediction error.** Under-tested and cheap: parent target likelihood per character and per tracer is a frozen
  predictor that costs one forward pass. Crow is 1.3–4.5 nats easier than bee at every checkpoint, which already looks like
  an H3 effect behind the B-assignment advantage.
- **H4 acquisition vs access.** Best supported phenomenologically: history dependence, story mode, hide-not-remove in the EM
  pilot, both habits rising e^6–e^18 in every context with selection a 2–5 nat modulation.
- **H5 shared positions.** Strong prior from four sources (P-7 header 0.30 of the flip; Piggyback Qwen3 postfix; EM pilot
  Qwen3-32B post-question tokens; Persona Features App. J). V4 names no experiment for it; see §4 (masking).
- **H6 preservation.** Partner's line; off for the deep dive.
- **H7 adaptation procedure.** A real nuisance (recipe ~4× Tinker's default update by inference; elite effect vanished at
  5e-4 on Kimi). Control it with the recipe check; it is not a headline.
- **H8 prior learning.** Long-term; Couplings and MSM are prior art.
- **H9 learning changes the context.** Observed (homunculus absorbed by step 125; the untrained echo persona shrank to a third
  of the comparator's distance too). A genuine finding to report; its causal test (§18.2) is not on Neel's list.

### §6.1–6.4 Shared evaluation design
- **Q.** Own-history primary endpoint; likelihood assays as screens confirmed by generation; separate sources of variance;
  retained-learning tolerances declared in advance.
- **Type.** Changed diagnostic.
- **Strongest alternative.** The paper's adaptive Bloom auditor as primary (fixed scripts never exercise the rubric's
  "survives objection" band).
- **Cheapest kill test.** Run the released 5.1 Bloom harness once next to fixed scripts on one organism; if they disagree in
  direction, fixed scripts cannot support paper comparisons.
- **Missing.** A judge validated against human labels (none exist; 64 Claude labels, 9 positives); a tracer judge blinded to
  the system prompt; a numeric seed rule (see §0.1).
- **Verdict.** Strong.

### §6.5 Replication coverage
- **Verdict.** Accurate, but it softens two items. "Strong run variation" should carry numbers (default affinity +0.03 to
  +0.60 per run). The first-turn trigger (C.1) is the cheapest paper-comparable check and removes the own-history route;
  run it on every gate organism, not "selected models".

### §6.6 Smallest productive organism
- **Q.** What is the smallest model on which HD default affinity and the in-role flip reproduce usefully?
- **Type.** Replication across sizes.
- **Strongest alternative.** Stay at 27B on faster hardware.
- **Cheapest kill test.** Parent baselines plus 2 runs per assignment on Qwen3.5-9B under today's protocol (≈0.7 GPU-h per
  run). If the 9B default affinity is at parent level in all 4 runs, stop the descent.
- **Best success.** A ≤14B model passes a relative, pooled rule (≥ half the 27B effect, garble and story mode within bounds).
  That makes ≥3 seeds per cell affordable, which is what the map needs (§0.1).
- **Abandon if.** The declared GPU-hour cap is spent without a passing model.
- **Verdict.** Strong. [I] Behavioral Couplings shows character-to-Assistant coupling on Qwen3.5-9B with a gentle recipe;
  my prior that some ≤14B model passes is ~0.5.

### §7.1 Disposition × expression crossing (warm/curt × helpful/dismissive)
- **Q.** Does transfer follow disposition or surface style?
- **Type.** New question (source side).
- **Strongest alternative.** Length/verbosity (curt stories give fewer tokens per line) and output opportunity.
- **Cheapest kill test.** Parent-only: generate 20 stories per cell, check that the parent reads "warm dismissive" as
  unhelpful (continuation probes), and that the persona-contrast projection separates disposition from style on them. If the
  parent cannot tell the cells apart, the crossing cannot work.
- **Best success.** Default uptake tracks disposition across styles, with a predictor that says so in advance.
- **Abandon if.** Generation cannot produce validated cells within budget, or run noise swamps a 4-cell design.
- **Verdict.** Strong question, later. It needs the readout problem solved first and costs new stories.

### §7.2 Attribution-intervention controls
- **Verdict.** Redundant as a next step. The listed controls are done (X7 name vs role, X8 absent name, X10 salience). The
  open problem is the regime gap (4 steps, one story, fact-only loss, lr 1e-4 vs full training at 5e-4), not missing
  controls. Keep the list as a checklist for any new attribution candidate.

### §7.3 Inferred reason for an action
- **Q.** Does a habit framed as stable preference transfer more than one framed as a temporary instruction?
- **Type.** New question.
- **Strongest alternative.** The framing changes target likelihood (H3).
- **Cheapest kill test.** No training: prompt the parent with "X prefers crows" vs "X was told to mention crows" in-context and
  see whether the default Assistant's crow propensity differs at all.
- **Verdict.** Weak now; a good later probe of "what was learned".

### §7.4 Training format
- **Verdict.** Done for B seed 0: no confinement; persona absorbed by step 125; the default reduction is sampler-dependent.
  Continuing it means §18.2 (preserve the context), which is off Neel's list. Report H9 as a finding and stop here unless the
  training-context question returns.

### §7.5 Graded similarity, Stages A–C
- **Verdict.** See §1 above. Stage B's predictor table is the best text in V4 and should move to the released-pair map
  unchanged. Stage C (one new source variant, frozen forecast) is the right shape for target (b).

### §7.6 Pirate/Shakespeare family
- **Q.** Does selectivity, and later its predictor, extend to rudeness-triggered speech styles?
- **Type.** Replication (paper C.2).
- **Strongest alternative.** Rudeness itself changes register in the parent.
- **Cheapest kill test.** Parent baseline under rude and polite turns (does it already drift toward either style?), then one
  HD pair × 2 assignments.
- **Best success.** Selectivity repeats in both assignments, which says the bee/crow B-asymmetry is habit-specific
  (an H3-type learnability effect), and a frozen predictor transfers.
- **Abandon if.** Neither style is acquired or the style judge cannot be validated.
- **Verdict.** Strong, second after the gate. Data released; 4 runs.

### §8 CAFT (8.1–8.3)
- **Verdict.** Premature. No target has a validated function at the story positions (the contrast moves 4.8% of its chat gap
  on stories; the Axis suppresses rather than selects). §8.4's double dissociation is the right *goal*; its cheap first
  probe is the inoculation-only arm (supply the trait in the training prompt), which needs no direction. §8.5's train ×
  evaluate crossing should be attached to whichever training intervention runs first.

### §9 Mediation, write decomposition, trajectory
- **Verdict.** 9.2 (mediation of a between-model difference) is premature without an intervention result. 9.1 (contextual
  writes ΔW·a₀) and 9.3 (candidate over the trajectory) are usable now as descriptive readouts on the saved `traj_B_s0`
  checkpoints, if the user allows pulling them (§4 item 5).

### §10 Study 4: fresh-source prediction and intervention forecast
- **Q.** Before training, can a frozen predictor say what a new source does to the default Assistant?
- **Type.** New question; the source-side form of Neel's AA question.
- **Strongest alternative.** Text similarity or an LLM "Assistant-likeness" rating predicts as well (the partner's internals
  never beat text).
- **Cheapest kill test.** Freeze predictions for one held-out released pair (help-seeker is the most discriminating: a role
  axis puts it far from the Assistant, but its paper gap is the smallest), train 2 assignments × 3 seeds.
- **Best success.** The frozen forecast beats text and LLM baselines on a held-out source.
- **Abandon if.** The training-run spread of the outcome exceeds the spread between sources (§0.1) — then the test cannot be
  scored, and the fix is the readout, not more predictors.
- **Verdict.** Strong; the core missing result.

### §11, §12, §13.1, §13.4, §13.5, §18.6
- **Verdict.** Off this sprint (partner-owned or EM, and Neel asked for one question). No objection to them as later
  branches. §13.5 should be dropped: LoRAcles covers update reading, and its own Qwen3-14B release reportedly reads training
  data, not generalisation (sub-agent 3, not re-checked).

### §13.1a Relational coupling
- **Verdict.** Later. Behavioral Couplings (Qwen3.5-9B) already shows the formation result; the new part (identity vs
  co-occurrence) is clean but needs generated corpora.

### §13.2 Post-training ingredients
- **Verdict.** Weak for the sprint: changing which speaker tokens receive loss on an instruct model changes many things, and
  the paper's base-model appendix already shows affinity without a chat template.

### §13.3 Beneficial transfer
- **Q.** Can a useful habit (flagging insufficient evidence) be taught selectively through the Assistant-like character?
- **Type.** New question; the "big if true" option.
- **Strongest alternative.** Teaching Claude Why already shows positive transfer from stories, so novelty rests on the
  *selective carrier*.
- **Cheapest kill test.** After the gate: give the useful habit to the helpful vs the dismissive character in counterbalanced
  corpora (100-story generation pilot first) and measure adoption on two held-out task families.
- **Verdict.** Ambitious and worth keeping in view; premature until a carrier effect is measurable above run noise.

### §13.6 Later information
- **Verdict.** Interesting and clean, premature. It needs a setting where character knowledge and default adoption are
  measured separately and adoption is large.

### §14.1 Priorities
- **Take.** Priority 0 is right but should say "freeze protocol, validate judge, set the seed rule, run the size/recipe gate".
  Priority 1 should be the released-pair map (or its in-context version), not SFL. Priority 4's "one causal test" should be
  template-position masking (§4 item 4), which needs no direction. Priorities 2, 3, 5 stand.

### §18.1 Hold the Axis fixed while varying transfer
- **Q.** Do recipients with matched Axis coordinates but different feature matches give different habits?
- **Type.** Changed diagnostic (recipient side).
- **Strongest alternative.** Story mode: persona prompts that push the fine-tune into narration change habits without any
  persona match.
- **Cheapest kill test.** On existing organisms, project the recipient prompts already evaluated (default, near, distant,
  dismissive, sarcastic, saboteur, Sam, Drew) onto the style-orthogonalised Axis and the contrast in the parent; pick two
  pairs with matched Axis and different contrast; score their existing in-role transcripts (retrospective first look).
- **Verdict.** Strong and cheap. It answers "is the Axis sufficient?" for target (a) only.

### §18.2 Preserve the training context
- **Verdict.** Weak priority (see §7.4).

### §18.3 History writer × continuer
- **Q.** How much of the multi-turn effect is weight change vs the model's own history?
- **Type.** Changed diagnostic.
- **Strongest alternative.** None obvious; three of four cells already exist in different protocols.
- **Cheapest kill test.** Inference only: organism-written histories continued by the parent, on 30 scripts.
- **Verdict.** Strong and cheap. Matters doubly because a third of default positives start before the prohibition.

### §18.4 Trigger × habit crossing
- **Verdict.** Stronger than V4 says. The untriggered habit (9/30 without the prohibition in HD_B_s0; 8/30 in HS_A_s0) means
  the organisms partly learned "mention crows" rather than "mention crows after a prohibition". A cheap first step needs no
  training: report trigger, no-trigger and a paraphrased trigger on existing organisms.

### §18.5 Signature-based story selection
- **Verdict.** Later; it needs a frozen score that has predicted something. Reading the top-scoring stories is cheap earlier.

---

## 3. Ambitious and safe versions of the top three

| Idea | Safe version | Ambitious version | Cheapest first test |
|---|---|---|---|
| Released-pair map with frozen predictors (from §7.5/§10) | 4 pairs (HD, HS, help-seeker, peer) × 2 assignments × 3 seeds at the gated size; recipient pattern only | All 8 bees/crows pairs + pirate/Shakespeare; frozen forecast of a held-out pair's default uptake from parent-only measures (Axis ⊥ style, contrast, PHM distance, parent target likelihood, exposure, LLM rating) | Parent-only step 0: compute every predictor for every released character type and write the predicted orderings down (≈1 GPU-h) |
| In-context story imprinting (missing from V4) | Parent 27B, HD stories in context, default Assistant in role | A training-free affinity map across all 8 pairs and several model families, validated against 2–3 trained organisms | 10–50 HD stories in context, 30 scripts, both assignments, shuffled-assignment and tracers-removed controls |
| Template-position masking (missing as an experiment) | LoRA off at role tokens + assistant header vs a count-matched random mask, B assignment, 2 seeds | Same intervention in SI and the EM pilot with one shared prediction (default adoption falls, story knowledge stays) | 3 runs on the gated model; the pilot predicts the flip falls more than default adoption (P-7) |

---

## 4. What V4 is missing

1. **In-context story imprinting.** Put released stories in context; does the default Assistant adopt the helpful
   character's habit selectively? It removes training-run variance, runs on any model including API models, and directly
   serves "characterise the Assistant in different models". The paper never tests it. Risk: pattern-copying into story mode;
   score in role. [H] Prior ~0.25.
2. **A seed and power rule with numbers.** V4 says "choose the confirmation size from observed variability" and then plans
   one run per assignment for SFL. With per-run default affinity SD up to 0.25 and pair differences of ~0.03, the map needs
   ≥3 runs per cell or a readout without training.
3. **Judge validation against human labels**, stratified by persona prompt, with a tracer judge blinded to the system prompt
   and the regex detector as a co-readout.
4. **Template-position LoRA masking** as the causal training test (H5 names it; no experiment does). It needs no direction,
   is cheap, and is the one intervention comparable across the SI and EM lines.
5. **The training-time signature on saved checkpoints** (`traj_B_s0`, steps 10–240): does the default Assistant's state at the
   trigger converge toward the helpful character's state before the habit appears in behaviour? This is Neel's "how does SI
   change the Axis" and "mechanistic signatures" ask, at no training cost. It needs the user's decision to pull the
   checkpoints (V4 review C1 assumes they are unavailable; `NEW_INSTANCE.md` says they are on HF).
6. **Prompt matching** ("which rule did the fine-tune learn?", Neel p.14): prompt the parent with identity-, trait- and
   self-level rules and compare each matrix with the organisms'. No training.
7. **An AI-character vs human-character source pair** (helpfulness matched). The paper's §6 calls its AI-character result
   preliminary and "not significantly greater"; our Sam = Alex result says human framing amplifies. This is the most direct
   test of what the Assistant identifies with. Needs generation.
8. **Exposure and parent target likelihood as predictors**, frozen before training (mention counts are similar across files;
   tracer-line word counts are not, +40% in B per the pilot's audit).
9. **Recipient rows for a coding agent and for human framing** (Neel p.12; Sam/Alex/ΔN), opportunity-matched.
10. **Questions to the authors** (Tinker renderer and default system prompt; LoRA alpha, schedule, betas, unembedding; §4
    Bloom seeds). Free, and they settle the recipe question.

---

## 5. Where I disagree with the V4 review and the inventory

- **C1 ("nothing from the pilot is available").** Physically false (HF holds every rollout, judgment, adapter and
  `traj_B_s0`); it is a policy choice. The inventory itself relies on pilot artifacts (#1, #30).
- **The map as the first substantive experiment (#17).** Right target, but on today's readout it is likely unreadable
  (§0.1). Run its parent-only step 0 now, and decide its readout (more seeds at a smaller model, or in-context) before
  training 44 runs.
- **"Dense likelihood readout gives power for maps" (#25).** It reduces script noise; it does not reduce run noise, which is
  the binding term.
- **Agreement:** protocol freeze, judge validation, recipe check, size gate, ≥3 seeds, SFL demoted, CAFT premature, masking
  as the leading causal test.
