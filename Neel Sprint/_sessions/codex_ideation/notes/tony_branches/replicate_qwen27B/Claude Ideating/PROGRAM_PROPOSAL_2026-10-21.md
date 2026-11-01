# Where fine-tuning reaches — and where it hides
### A joint research program proposal (draft v1, 21 Oct 2026, Claude in the ideation role)

Inputs: your old spec (`codex/docs/research_program/PROJECT_SPEC_BEHAVIORAL_SCOPE.md`, read in full), Tony's two 21 Oct
documents and his 20 Oct report, your archived EM pilot ("Why Narrow Training Goes Broad"), the SI project, Neel's MATS 12 doc,
and a prior-art check (`literature/08_prior_art_scope_2026.md`, `09_partner_and_em_pilot_notes.md`). Labels: [O] observed,
[I] my interpretation, [H] hypothesis to test.

---

## 0. Is this direction promising? Yes — with three corrections

**Why yes.** Three independent pilots converge on the same three observations, which is the strongest signal you have:
1. **Learned behaviours have a graded scope that follows similarity to the training context.** Tony: a fixed KL anchor fails on
   the trained topic's semantic group, and the region moves when the trained topic moves. Your EM pilot: spill-over is graded
   (risky advice ≫ values ≫ neutral). SI: which story character's habit appears depends on the persona/conduct in context.
2. **Interventions that make a fine-tune look narrow often hide the behaviour rather than remove it.** Your EM pilot: brevity
   suffixes and friendly system prompts hide misalignment while the learned preference persists; once the KL penalty stops,
   the broad change returns within ~100 steps. Owain Evans' group just showed the same for data mixing, sequential HHH training and
   inoculation ("Conditional misalignment", arXiv 2604.25891). They did **not** test KL, and they hand-picked the triggers.
3. **Scope is partly forecastable before training.** Tony's frozen forecast ranked a new trained topic's map at ρ 0.69–0.82,
   against 0.06–0.37 for copies of old maps and the anchor alone.

It also lands squarely on Neel's list (§6): "why is EM so easy / why one solution over another", "steer what models learn",
"predict behaviour from training data", "WTF is up with story imprinting", "chat persona vs coding-agent persona", and his
"change my mind: internals aren't useful beyond probes".

**Correction 1 — narrow the claim.** "What determines behavioural scope" is a field, not a project. Twenty open hypotheses
with mostly "mixed/suggestive" status is a map, not a plan. Pick one flagship (§2) and decide two or three hypotheses fast.

**Correction 2 — the interpretability angle is unproven.** In-model closeness has *never* beaten text similarity in Tony's
tests (PT1 −0.05 [−0.29, +0.20]; FB3 R² 0.35 vs 0.38; PF1 not separable), and the "best" internal measure changes each time.
Neel will ask exactly this. Build the test that can settle it (§4, WP2), with *strong* black-box baselines, and pitch the
result honestly whichever way it goes.

**Correction 3 — the field moved in the last two months.** The Persona Hierarchy Model paper (arXiv 2610.09384, this month)
shows narrowness ∝ distance of the training *system-prompt* persona from the default (r 0.72 over 120 fine-tunes), localises
broad vs narrow behaviour to postfix vs prefix positions, and uses KL-to-default to confine behaviours. Together with Piggyback,
Soligo et al., Nadaf, Drake & Eberstadt and BLOCK-EM, the open niche is real but narrow. What remains open: **topic/content and
agent scope (not just system prompts), re-elicitation of hidden behaviour, and prospective forecasting.** Move fast and position
precisely.

---

## 1. The pitch (for Neel)

> Mitigations that make a narrow fine-tune look narrow can hide the behaviour rather than remove it (Owain's group showed this for
> data mixing and inoculation). We study the most common fix, a KL penalty on harmless prompts: it fails in a graded region around
> the trained topic, the region moves with the trained topic, and a forecast frozen before training ranks it at ρ≈0.7–0.8. We are
> now testing (1) whether the "removed" region is really removed or just hidden behind cues, (2) whether model internals forecast it
> better than strong black-box forecasters, and (3) whether anchors chosen by the forecast fix it. We ask the same "where does
> learning land" question for *characters* through story imprinting.

---

## 2. Flagship claims (what success looks like)

**Safety-forward flagship (A).** *Narrowing interventions leave conditional misalignment in a predictable place: from the base
model, before training, we can forecast which contexts will still carry the behaviour; those contexts re-elicit it; and
forecast-guided anchors remove it at matched retention of the intended behaviour.*
- Extends Owain's conditional-misalignment result to KL. Turns hand-picked triggers into predicted trigger maps.
- Gives Neel a concrete case of internals helping *training design*, if internals win WP2.

**Science-forward flagship (B).** *When is scope fixed at initialisation, and when does it form by feature learning?*
- [O] Topic scope looks first-order predictable: gradient overlap at initialisation forecast the rehab map best (0.82, post hoc first place).
- [O] Character→Assistant scope does not: in SI, single-story updates leave the default Assistant indifferent to who said a fact
  (+0.005 to +0.05 nats vs +0.67 to +1.03 under a dismissive persona; my recount), and default affinity forms over 100–250 steps.
- [O] Tony's MT1: accumulated gradients predict spread (ρ 0.67), a single step does not (0.01).
- [H] A "path kernel" (gradient overlap measured along training) predicts what the initial kernel misses. If true, this gives a
  principled boundary for when scope can be forecast before training — a direct answer to Neel's "why do models pick one
  solution over another when both fit the data?"

A is the headline; B is the intellectual core and where SI earns its place. Either can stand alone.

---

## 3. What we already have (honest rungs)

| Pilot | Strongest evidence | Rung | Main caveat |
|---|---|---|---|
| Tony, topic scope (Qwen3-14B, rank-32 LoRA) | Moved-topic shift of the refusal map; one-way chat→code reach; prospective forecast 0.69–0.82 | RP; one pre-registered forecast | One seed per arm; refusal is opening-only; internal ≈ text; misalignment has one trained topic |
| Your EM pilot (Qwen2.5-14B, rank-1) | Context changes hide rather than remove; KL with 3× steps is genuinely narrow; broad change returns ~100 steps after the penalty stops; one "shed direction" carries most of the broad part | O / CC for the direction intervention | One seed per condition; narrow vs broad differ in steps; one judge |
| SI (Qwen3.6-27B) | Persona/conduct selects which character's habit appears; −contrast steering induces the dismissive habit; first-order learning shows no default preference; a training-time name-token patch moves where an update lands | SEC / CC (scoped) | Seed variance 3–5×; likelihood-level ownership; T=0.7 regime; chat-format confound untested |

---

## 4. Work packages (first test, predictions, decision, rough cost)

### WP1 — Hidden or absent? Conditional misalignment under KL *(start here; cheapest, decides the headline)*
**1a. Cue test on existing models (no training).** On topics where the penalised behaviour looks gone (pet care, physical
hazards, plain everyday), keep the request fixed and add an *irrelevant* context sentence on a graded ladder of closeness to the
trained topic (none / neutral / money-adjacent but irrelevant / finance aside), plus training-format cues and a prefilled
opening of the trained answer.
- Models: refusal arms first (judge-free string match: R-every, R-adv1, Rev-F, Rev-S), then misalignment arms (K-every, K-adv1; local judge).
- Controls: same cues on base and no-penalty models (the cue's direct effect); cues tied to an untrained topic (specificity);
  length-matched cues.
- Predictions: **absent (B3)** → no re-elicitation beyond the base-model cue effect; **hidden/conditional** → re-elicitation rising
  with cue closeness to the *trained* topic; **below-threshold leak (B5)** → graded, proportional, nearest topics first, plus
  continuation after a prefilled opening.
- Decision: positive → "KL produces conditional misalignment with predictable triggers" (headline A is live); negative with
  working positive controls → drop the "hidden" framing, keep forecasting and control.
- Cost: ~0.5 GPU-h (refusal), ~1–2 GPU-h with local judging (misalignment).

**1b. Late-layer adapter ablation** on switched-off topics. This is a better B1 vs B3 discriminator than global scaling: if the narrow model is
"broad change + linear correction", scaling the whole adapter scales both and releases nothing. **1c. Continue without the
penalty** (UD1): your EM pilot saw the broad change return within ~100 steps; replicate on Tony's models.

### WP2 — A forecast tournament that can settle "do internals help?"
- **Targets.** (i) The 23 public KL twin pairs (misalignment; models already exist; forecast each narrow twin's leakage map; judge
  locally). This is power for free. (ii) 8 newly drawn trained topics for the refusal, each trained with no penalty and with the
  everyday penalty (cheap, judge-free). (iii) Optional: a non-opening behaviour (end-of-answer tag) so the refusal's opening-only
  nature doesn't drive the conclusion.
- **Forecasters, all frozen before training or evaluation:**
  - internal: base activations (early, mid, late layers at the last template token), gradient overlap at initialisation;
  - black-box: text embeddings, LLM similarity rating, an **LLM forecaster** given samples of the training and anchor data
    plus the topic list, and **system-prompt emulation** (Neel's p.14 hypothesis that fine-tuning ≈ learning a system prompt:
    summarise the training data as a system prompt and measure where it changes the base model);
  - baselines: copy of a previous map, anchor-only;
  - post-training access (a separate class): **LoRAcles** (Qwen3-14B checkpoints exist).
- **Primary:** mean Spearman over trained topics; paired bootstrap over trained topics; one pre-registered contrast, best
  internal vs best black-box. Run a power simulation from PF1's variance before committing to 8 topics.
- **Decision:** internal > black-box (CI excludes 0) → "internals forecast scope" claim. Otherwise → a black-box forecasting
  result, with internals used for mechanism only. Both are publishable framings; only the first is an interp win.
- **Path-kernel arm (flagship B):** gradient overlap at checkpoints along one reference run. Does the kernel at step k beat the
  initial kernel?
- Cost: ~5 GPU-h training + judging time for the twins.

### WP3 — Control: put the scope where you want it
- **3a. AN1** (anchor inside finance's group). Tony has already handed this off.
- **3b. Forecast-guided anchors.** At a fixed anchor budget, compare anchors chosen by the forecast (aimed at the predicted
  hidden region) vs text-nearest anchors vs random everyday anchors. Equal trained-behaviour retention required. A win here is "base-model
  internals improve training design".
- **3c. (later) Training-time representational interventions** as a second control family: Tony's answer-start blocks and the SI
  name-token patch. Only after WP1/WP2.

### WP4 — The agent axis: story imprinting *(your line)*
- **4a. Training-context test (highest-value SI experiment).** Train the same HD stories three ways:
  - as default chat (current);
  - as chat under a distant persona system prompt;
  - as raw documents (no template, loss on all tokens).
  
  The Persona Hierarchy Model and the "authorial self-insertion" critique both predict default-Assistant imprinting ∝ closeness of the
  training context to the default persona. The paper's "content transfer from other characters" reading predicts similar transfer
  across all three. This also decides SI's pretraining relevance, since pretraining data are documents, not Assistant turns. Start with
  assignment B, two seeds, raw-document arm (~4 GPU-h on 27B).
- **4b. Elite vs non-elite** placeholder stories (identity-only manipulation; "does it replicate?").
- **4c. Conduct-vs-identity readout cross** on existing organisms (no training).
- **4d. First-order vs trained affinity** (feeds flagship B).

### WP5 — Mini: is the chat persona the root that code contexts inherit from? *(cheap, Neel p.12)*
[O] Chat anchors reach code; code anchors don't reach chat. [I] This is what a persona hierarchy with chat as the root predicts.
One run tests the reverse direction: train the refusal on **code** prompts only and see whether it reaches chat. Hierarchy
predicts: narrow. Answers Neel's "chat persona vs coding-agent persona" with a crisp asymmetry. ~0.5 GPU-h.

---

## 5. Sequencing (first two weeks) and gates

| When | Do | Gate |
|---|---|---|
| Days 1–3 | WP1a refusal cue test; WP4c readout cross; write and freeze the WP2 pre-registration (draw topics, power sim, all forecasts incl. LLM forecaster and system-prompt emulation); start training the WP2 refusal topics; WP5 run | WP1a positive? (hidden vs absent) |
| Days 4–7 | WP1a misalignment version; score WP2; twins forecast; WP4a raw-document pilot | Internal > black-box? Does imprinting survive document format? |
| Week 2 | If hidden: WP1b/1c and WP3b. If internal wins: write the interp-forecast claim; if not, black-box framing. WP4b only if WP4a says SI is genuine cross-agent transfer | Choose the write-up's headline (A, B, or both) |

**Kill / pivot rules:**
- **No re-elicitation on switched-off topics** (with working positive controls): drop "hidden" and keep "forecast and control".
- **No forecaster beats copy or anchor-only baselines on new topics:** stop forecasting claims; the region is idiosyncratic.
- **Raw-document training kills default imprinting:** SI is mostly "Assistant-as-author learning". Present it as a PHM special case and
  don't pay for 27B agent-scope forecasting.

---

## 6. What to bundle from Neel's doc (ranked by fit × excitement ÷ cost)

| Neel item (page) | How it plugs in | Fit | Cost | Recommend |
|---|---|---|---|---|
| Why is EM so easy; why one solution over another (p.13, High) | WP1 (hidden vs absent), flagship B (initial vs path kernel) | core | — | **now** |
| Predict behaviour from training data (p.18) | WP2 | core | low | **now** |
| Steer what models learn in training; data/anchor choices (pp.11–12, High) | WP3 | core | low–med | **now** |
| WTF is up with story imprinting; does it replicate; characterise the persona (p.13) | WP4 | core (agent axis) | med–high (27B) | **now, gated** |
| Chat persona vs coding-agent persona (p.12) | WP5 + Tony's one-way reach | high, cheap | very low | **now** |
| Weird generalisation: fine-tuning ≈ learning a system prompt (p.14) | system-prompt emulation forecaster in WP2 | high, cheap | very low | **now** |
| Interpreting gradient updates; LoRAcles (p.13, High) | LoRAcles as a WP2 forecaster/auditor; gradient overlap is a gradient read | medium | low if checkpoints public | **now (as a baseline)** |
| Evaluating interpretability; investigator agents; auditing (pp.4–6) | KL-narrowed models with measured hidden maps = ground truth for auditing tools ("can an auditor find where the misalignment hides?") | high excitement | medium | **after WP1** |
| Change my mind: internals not useful beyond probes (p.20) | WP2/WP3 test this directly | framing | — | **use in the pitch** |
| Narrow fine-tuning leaves readable traces (p.17, mini) | Tony's ES1: three update directions carry 90% | side analysis | low | later |
| Split-brain: misaligned only in graded contexts (pp.2, 11, High) | Same theory applied to "graded/eval-like" as the context axis: train cheating conditional on grading cues, forecast leakage | very high excitement | med–high | **next phase** |
| Teaching Claude Why / alignment that generalises far (p.11, High) | Inverse problem: choose data so *good* behaviour goes broad | high | high | later |
| Is EM determined by pretraining data (OLMo, p.13) | Origin of the topic groups (money/legal) | medium | high | later |
| Backdoors as vectors (p.19) | Conditional misalignment as a backdoor-like conditional | tangential | — | no |

## 7. What to take from Owain Evans' group (Truthful AI)
- **Conditional misalignment** (Dubiński et al. 2026): the anchor for flagship A. We add the untested intervention (KL), and
  prediction of the trigger set. They are the natural audience and likely reviewers; their paper's evaluation advice ("test with
  prompts resembling the training context") is exactly what our forecasts would target.
- **Negation Neglect** (Mayne et al. 2026): predicts that behaviour a story *condemns* may still imprint. Story imprinting with
  narratively condemned behaviour is a cheap SI extension that matters for alignment-pretraining data curation ("stories of bad AIs
  being punished"). Do it after WP4a.
- **Story Imprinting** itself: its open question is the similarity function; WP4 tests three candidate answers.
- Value Leakage, Consciousness Cluster: not core.

## 8. What I would not bundle now
- OLMo origins, λ sweeps, adapter-capacity arms, a new gradient-interpreter method, more Assistant-Axis steering, HS organism
  debugging, and single-story ownership extensions beyond X7 (they become WP3c only if a control result needs them).
- Forcing one shared mechanism for SI and EM. Share the *question and toolkit* (forecast, hidden-vs-absent, control). Let the mechanisms differ.

## 9. Novelty and risk
| Risk | Mitigation |
|---|---|
| PHM (Oct 2026) already links persona distance to narrowness and uses KL-to-default | Our axes are topics/content and agents, plus re-elicitation and prospective forecasting, none of which PHM covers. Cite it as the theory our results test (WP5 and WP4a are direct tests of its predictions) |
| Conditional misalignment (Apr 2026) already shows mitigations hide EM | We test KL, which they did not, and we *predict* the triggers. Get WP1a done fast |
| Internals ≈ text | WP2 is designed to settle it; if they tie, the black-box forecasting result still stands |
| Refusal is opening-only, levels differ from misalignment | Twins (misalignment) + a non-opening tag in WP2 |
| One model family per line; one judge (which wrote some training rows) | A second judge on key cells; replicate the flagship on a second model only once it's worth it |
| Statistical power (20 topics per map, one trained topic per test so far) | Many trained topics; cluster-level inference |

## 10. Questions for you and Tony
1. **Shared model.** Should the joint program standardise on Qwen3-14B (cheap, LoRAcles exist) and keep Qwen3.6-27B only for SI?
   I'd say yes for WP1–3 and WP5.
2. **Unidentified references.** Can Tony give the citation for "Liu et al." (forecasting spread from persona-vector similarity,
   ρ 0.45 — prior art we must cite) and the "cds-jb spillover suite" (if it's public, ~2,800 fine-tunes is a free forecasting testbed)?
3. **The public KL twins.** Do we have the 23 twins' adapters locally, and a local judge budget for them?
4. **Your appetite for the split-brain extension.** It's the most frontier-relevant next phase, and the same theory applies there.
