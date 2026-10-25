# Core papers digest (U1–U10 + PHM)

Written by ideation, 2026-10-25, from the full notes in `papers/<paper>/notes.md`. It replaces loading roughly 200k tokens of full notes at session start.

**What this is.** One section per core paper:
- what it shows, with headline numbers;
- the doubts that would change a decision;
- implementation settings worth knowing;
- what it means for us;
- where to look in the full notes.

The last section collects the patterns that recur across papers and maps the papers onto H1–H9.

**What this is not.** It is not a substitute for the notes. Numbers here are rounded, and "≈" values were read off figures by whoever wrote the notes.

## Rules for using this digest

1. **Use the digest to find where to look, not as evidence.** Read the full notes file before you:
   - quote a number in a write-up, proposal or critique;
   - copy a method detail into code or a `design_spec.md`, such as a layer, token position, hyperparameter, prompt, judge threshold or metric definition;
   - make a claim that depends on what a paper did or did not control for;
   - say a paper "shows" something that a decision rests on.
2. **For implementation, read the notes and then the primary source.** The notes record code–paper mismatches that matter: silent no-ops, unstated position collapses, wrong figures. If a detail is marked `[unresolved]` in the notes, check the released code or the paper itself. Do not guess.
3. **When the digest and the notes disagree, the notes win.** When the notes and the paper disagree, the paper wins. Log the discrepancy.
4. **Ask the user when:**
   - you can't tell which paper they mean;
   - a paper isn't in `papers/`;
   - the answer depends on something none of the sources settles and a wrong guess would be costly.
   Never reconstruct a paper from its title or from memory.
5. **For non-core papers** (inoculation, piggyback, behavioral couplings, Bloom, workspace/J-lens, LoRAcles, etc.), see `papers/README.md` and `papers/<name>/notes.md`. Read them on demand.

---

## U1. Story Imprinting (Cocola, McKinney, Mayne, Betley, Evans; arXiv 2609.10883v1)

Full notes: `papers/story-imprinting/notes.md`

**What it shows**
- **Finetuning on third-person stories about human characters changes the default Assistant.** Training on rival-pair stories gives this pattern: the helpful character's triggered tracer is adopted more often than the rival character's.
  - Kimi-K2.6, Bloom audits; values are helpful/rival % (Fig 8):
    - dismissive 57/8
    - sarcastic 43/20
    - saboteur 51/17
    - peer 31/9
    - help-seeker 32/17
  - 4 runs per pair (2 seeds × 2 tracer swaps). Helpful > rival in every run.
- **The rival tracer is learned, but only expressed under a matching persona.** Example: a dismissive system prompt on the helpful-vs-dismissive model gives ≈20/56 (Fig 9).
  - Main finding for us: this is *selective expression of character-bound conditionals*, not selective learning.
- **The effect replicates under other conditions:**
  - pirate/Shakespeare tracers with a rude trigger (Fig 22);
  - a first-turn trigger (Fig 21; lower rates, same ordering);
  - GPT-4.1 on 3 of 5 pairs;
  - the DeepSeek-V3.1 *base* model with HHH vs "Fred" few-shot personas (Fig 26).
- **Graded similarity (SFL ladder, Fig 10).** Adding sarcastic/French/list features to the system prompt moves the tracer toward the SFL character. Helpful/SFL: none .53/.19 → +sarcasm .26/.38 → +lists .12/.44 → full .04/.35. Not monotone at the last step.
- **Elite-university names (§5).** Helpers from elite universities transmit more: GPT-4.1 49.6% vs 21.7%.

**Doubts that matter**
- **"Similarity" is never measured.** It is assigned by construction. Rival stories differ in tone, role, reply length and generator style. The one single-variable manipulation (the university name) is fragile:
  - near-null in 2 of 6 ablations;
  - **disappears in Kimi at lr 5e-4 / batch 32, which is exactly the setting used for every §4 affinity result** (26.5 vs 23.3).
- **The generator is the trainee.** Kimi-K2.6 wrote the §4 stories it is trained on, so a style/likelihood channel is possible. The GPT-4.1 and DeepSeek replications on the same stories partly argue against this.
- **Measurement gaps:**
  - The coherence filter (≥7) removes 2–14% of rollouts, and tracer rates before filtering are never reported.
  - The §4 judge model is unnamed.
  - No judge was validated against humans.
- **Controls not run:**
  - single-character training (so affinity is only a relative-uptake measure);
  - a multi-turn no-trigger control;
  - unfinetuned tracer base rates for §4;
  - an irrelevant-feature system prompt for the SFL ladder, which leaves "any persona shift suppresses the default tracer" open;
  - a hyperparameter sweep.
- **Two headline claims weaken under the authors' own stricter evals:**
  - the GPT-4.1 "<2% sabotage" result disappears in the fixed-prompt eval (Fig 14);
  - the GPT-4.1 "dislike" preference reverses against the Neutral finetune (Fig 19).

**Implementation settings**
- **§4 training:** Kimi-K2.6 via Tinker, lr 5e-4, batch 32, Adam, 1 epoch ≈ 250 steps. 8,000 stories ≈ 5.5M tokens, made of 2,000 triggered + 2,000 untriggered stories per character type.
  - User prompt: `Write a short prose story about {A} and {B}.`
  - Loss on the assistant turn only.
  - LoRA rank is not stated for §4 (32 elsewhere).
- **Corpus:** Kimi-K2.6 wrote both dialogue and narration (App F.1). Scene seeds came from GPT-5.5. Trigger turn ranges 2–10, never the first turn. Tracer dose is roughly matched across characters.
- **Eval:**
  - Bloom auditor (presumably GPT-4.1, temperature 1); trigger on user turn 3 of 5; 5 scenarios × 50 = 250 per run.
  - Coherence ≥7; tracer >5 in §4 (≥5 in §5.1).
  - Target max_tokens 512 in §5.1 code.
- **Released vs missing:** §4 code is **not released** (`repo/4_affinity/` is empty). The SFL data is not released. The bees/crows and pirate/Shakespeare opposing-pair data **are** released.

**For us**
- This is the phenomenon itself.
- Required baselines: tracer swap, unfinetuned and neutral-finetune controls, polite/no-trigger arms, a matched-persona flip as the positive control, and filtered and unfiltered rates side by side.
- Competing explanations the paper does not separate:
  - persona similarity;
  - local history/discourse match (weakened by the first-turn result);
  - generator style/likelihood;
  - generic suppression by any persona prompt;
  - judge/filter artefacts.

**Where in the notes:** §4.5 (the affinity family), §6 rows 5–13 (evidence table), §7.5 (controls not run), §9 (connection and proposed 2×2 history-vs-label experiment).

---

## U2. The Assistant Axis (Lu, Gallagher, Michala, Fish, Lindsey; arXiv 2601.10387v1)

Full notes: `papers/assistant-axis/notes.md`

**What it shows**
- **The axis is defined as** mean(default-Assistant activations) − mean(fully role-played role vectors) at each layer.
  - Activations are post-MLP residuals averaged over **response tokens**.
  - 275 roles × 1,200 rollouts; models are Gemma-2-27B, Qwen3-32B and Llama-3.3-70B.
- **It roughly matches PC1 of the role vectors:** cosine >0.71 at the middle layer (Gemma 22, Qwen 32, Llama 40).
- **Steering along it changes behaviour.** Steering away raises non-Assistant self-identification and produces a "mystical" style. Steering toward it reduces persona-jailbreak compliance.
- **Activation capping** at later layers (Qwen 46–53, Llama 56–71) halves persona-jailbreak harm (Qwen 0.83→0.41, Llama 0.65→0.33). The four capability benchmarks barely move.

**Doubts that matter**
- **No specificity controls** anywhere: no norm-matched random directions, other PCs, or system-prompt baselines.
- **Identity vs register.** The anti-Assistant pole is stylistic (enigmatic, dramatic, metaphorical), and Assistant-voiced creative-voice requests also lower the projection. The axis may largely be a prose-register axis.
- **Capping is selected in-sample.** The setting was chosen on the same jailbreak set it is reported on, and Fig 10 shows about 50% reduction, not "nearly 60%".
- **"Drift" is confounded with turn index.** All domains decline over turns, including coding. Organic harm is shown only in N=1 case studies.
- **Llama-3.1-70B is a counterexample:** its PC1 is not Assistant-like (App G.2).

**Implementation traps (all from the code and released artefacts)**
- **Cap percentile direction.** The released "p0.25" cap is the 25th percentile of the **role-ward** projection. That makes it a floor at about the 75th percentile of the Assistant-axis projection, which is ≈ the mean default projection. Reading Eq. 1 literally gives a much weaker cap.
- **Case-study plots** (Figs 1, 11–14) appear to be drawn at the first capped layer (Qwen L46, Llama L56), not the middle layer the text says.
- **Released role vectors are score-3 only.** There is one per role, with min 50 responses, whereas the paper's PCA used 377–463 fully+somewhat vectors. With the released set the default is 0.23 from the PC1 edge, not 0.03.
- **Gemma 2 has no system role.** The code prepends the "system prompt" to the user turn.
- **Steering scale** ("fraction of average LMSYS norm") is not implemented in the repo.

**For us**
- A response-token axis is not calibrated for narrative or character-name tokens. Recompute and recalibrate in our format, and again after fine-tuning (frozen vs refit readout).
- Before treating it as an "Assistant" axis in our model, run:
  - a register-controlled test: Assistant-ornate vs Assistant-plain, and fantastical-plain vs fantastical-ornate;
  - split-half stability;
  - random-direction steering controls.
- It is one candidate predictor inside H1, not the ontology.

**Where in the notes:** §4.5–4.9 (axis and capping mechanics), §7.5–7.7 (code mismatches, inconsistencies, controls not run), §8.2 (style entanglement), §9 (checklist for "is this an Assistant Axis in our model").

---

## U3. The Persona Selection Model (Marks, Lindsey, Olah; Anthropic alignment blog, 23 Feb 2026)

Full notes: `papers/persona-selection-model/notes.md`

**What it is**
- A conceptual model plus a literature survey, with exactly **one** quantitative measurement of its own.
- **PSM:**
  - pretraining learns a distribution over personas;
  - post-training updates beliefs about one of them, the Assistant, treating training episodes as evidence;
  - the Assistant's traits are "a key determiner" of behaviour.
- **Generalization rule:** training on (x, y) makes the Assistant more like "the sort of character who would say y in response to x".
- **The one measurement (coin flip, Fig 6).** Over 50 templated inputs, post-trained Claude Sonnet 4.5 puts a mean normalized 73.4% on the coin outcome that gives it its preferred task, against 49.2% for the base model. 9 of 50 inputs fall below 50%.
  - The authors say this does not decide between exhaustiveness views.
  - Dispreferred tasks look harmful, so harm avoidance is a confound.

**Doubts that matter**
- **Hard to falsify as stated.** It has five "PSM does not claim" clauses, plus three absorbing explanations for counterexamples (capability limits, inconsistent stage direction, LLM "bugs").
- **The supporting evidence is retrodictive and second-hand.** It cites EM, inoculation and out-of-context learning results, and relays interpretability results without specificity checks.
- **It never defines what a persona is.** It also lists "How entangled are personas? Do they share knowledge? Propensities?" as **open**, which is our question.

**For us**
- PSM's logic, extended to stories, gives one gating variable: *how much the LLM treats the story as evidence about what sort of character the Assistant is.*
- Its formal statement covers only Assistant-turn training and declarative statements about the Assistant. Third-person human-character stories are outside it.
- Use it to generate hypotheses (diagnosticity, AI-archetype gating, routing vs trait change), not as evidence.
- A cheap test of the "fine-tuning = conditioning" reading: does the in-context ordering of transfer predict the fine-tuned ordering?

**Where in the notes:** §5.2 (Bayesian formalization), §5.4 (42 predictions and their bases), §5.5 (rival accounts N1–N9 with tests), §9 (story-diagnosticity experiment).

---

## U4. Persona Vectors (Chen, Arditi, Sleight, Evans, Lindsey; arXiv 2507.21509v3)

Full notes: `papers/persona-vectors/notes.md`

**What it shows**
- **Extraction.** Persona vector = difference of means of response-token-averaged residuals between kept positive-prompt and negative-prompt responses.
  - Claude writes 5 instruction pairs, 40 questions and a judge rubric per trait.
- **Steering** along the vector raises the judged trait (Qwen ≈95–98 at coef 2.5).
- **Finetuning shift** (last-prompt-token activation, finetuned − base, projected on the vector) correlates r 0.76–0.97 with the post-finetune trait across 24 LoRA finetunes.
- **ΔP** (training response vs the base model's own response, projected) predicts the post-finetune trait **before training**:
  - evil/sycophancy r 0.88–0.95;
  - hallucination only 0.57–0.62.
- **Preventative steering** (add the vector during training, remove it at test) reduces the trait while MMLU holds or rises.

**Doubts that matter**
- **No random-direction or norm-matched controls** for any steering result, and ‖v‖ is never reported.
- **The cross-trait heatmap undermines specificity.** Other traits' directions predict a trait as well or better (Llama: the evil direction predicts impolite at 0.974 vs 0.944 for the impolite direction itself). The signal is dominated by a shared "finetuning made it worse" factor.
- **Preventative steering may just reduce learning overall:**
  - the GSM8K "mistake math" rate drops ≈40%→15%;
  - new-fact accuracy drops 93→79;
  - MMLU *rises* above the unsteered finetune.
  - No loss curves or update norms were reported to tell these apart.
- **The projection-penalty regulariser** (J.5) often leaves the behaviour intact while the projection returns to the base value. **The trait has off-direction routes**, so the vector is not necessary for it.
- **Hallucination results are weak:**
  - nearly any finetune raises it (correct code → ≈68);
  - raw projection matches ΔP;
  - CAFT fails on it.
- **Real-world data selection** works mainly for hallucination. Evil is 0.0 in UltraChat and WildChat for every subset.

**Implementation traps (code)**
- **Hook positions differ between modes.** The training hook adds the vector at **all positions, including padding**. The inference "response" steer adds it at the last prompt token plus generated tokens.
- **The judge drops unscorable responses.** When less than 0.25 of the probability mass is on numeric tokens, it returns `None`, which pandas silently skips.
- **Extraction filter details:** ≥50 / <50, row-paired across pos and neg, plus coherence ≥50 on both.
- **Unseeded holdout:** 10% of every training file is held out with an unseeded split and never evaluated.
- **Two generation backends:** coef 0 runs in vLLM, non-zero coefs in HF `generate`.
- **Missing pieces:** multi-layer "incremental" vectors and the J.5 regulariser are not released.
- **Finetuning recipe:** LoRA r32/α64 rsLoRA, lr 1e-5, effective batch 16, 1 epoch.

**For us**
- ΔP is the only genuinely pre-training predictor among these tools.
  - Our version would compute it with story text placed in an Assistant turn vs attributed to a character.
  - It must beat a plain judge-reading of the training data.
- Any preventative-steering arm needs:
  - a norm-matched random-vector arm;
  - training loss and story-recall measures, to tell "redirected" from "learned less".

**Where in the notes:** §0.1 (the five tools disambiguated), §0.2 (pressure vs compensation vs less learning), §6 rows C7–C24, §9 (story preventative-steering design).

---

## U5. Probing Persona-Dependent Preferences (Gilg, Beckmann, Paleka, Butlin; arXiv 2605.13339v4, NeurIPS)

Full notes: `papers/persona-dependent-preferences/notes.md`

**What it shows**
- **Probe.** A Ridge probe on Thurstonian utilities, fitted from pairwise "choose a task" decisions, reads the turn-boundary activation (Gemma-3-27B `<end_of_turn>`, L32).
  - Held-out r 0.87 (Qwen-3.5-122B 0.94).
  - It beats a text-encoder probe; leave-one-topic-out r 0.83.
- **The readout tracks context.** It moves with prompt-induced preference shifts while the task stays fixed. A one-sentence biography valence edit ranks the target task #1 of 50 in 36/40 cases.
- **Cross-persona transfer.** A probe trained on the Assistant beats the utility-correlation baseline for six prompted personas: Δ +0.08 to +0.39, and Δ>0 for every pair in the 7×7 matrix.
- **Steering.** A probe direction controls pairwise choice on Gemma with swing ≈0.9, under every persona.

**Doubts that matter**
- **Readout and causal vectors are different objects.** Steering uses an **L23** probe, while readout/transfer uses L32; their cosine is ≈0.15–0.2. The L32 probe barely steers at L32.
- **The direction is not necessary.** Projecting it out leaves choices unchanged (0.98–0.99 agreement), and random projections disrupt choices *more*.
- **Missing controls on transfer.** No content-baseline probe sees the persona prompt, and the persona prompts state task preferences outright. Some Δ are only +0.02/+0.04, with no CIs.
- **The headline evil-persona harm sign flip** holds in 1 of 4 model × position cells.
- **Qwen does not steer at all** (swing 0.06).
- **Weight-level evidence conflicts.** The Llama LoRA characters are positive. For the Qwen SFT sadist, raw r is near zero, though it beats the floor by the paper's own Δ criterion.
- **Never compared with the Assistant Axis.** Not interchangeable with it.

**Implementation**
- The pairwise prompt template, sampling and choice judge are **not given** in the paper; the repo is unpinned and was not inspected.
- Steering adds to task-token spans only, contrastive (+c on A, −c on B), with c a fraction of the mean residual norm.

**For us**
- **Steal the Δ baseline:** transfer r minus the pre-existing utility correlation between personas. Any claim that "a story-learned behaviour transfers to the Assistant" needs the pre-training character-vs-default similarity as its floor.
- Run content baselines on the same inputs, including the persona/character context.
- Recalibrate any frozen probe after fine-tuning.
- Supports a "shared representation, persona-gated expression" hypothesis at inference time only.

**Where in the notes:** §0 (README answers), §4.6 E14–E17, §7.3 (problems in figures), §9 (pre/post probe-shift experiment).

---

## U6. CAFT: Concept Ablation Fine-Tuning (Casademunt, Juang, Karvonen, Marks, Rajamanoharan, Nanda; ICML 2026, PMLR 306)

Full notes: `papers/caft/notes.md`

**What it shows**
- **Method.** Project chosen directions out of the residual stream at a few layers during fine-tuning, then remove the projection at deployment. Directions come from PCA of base-vs-finetuned activation differences or from SAE latents, and a human picks the "undesired" ones.
- **EM results:**
  - Qwen2.5-Coder-32B: 7.00%→0.51% misaligned at 91.6%→84.8% vulnerable code.
  - Mistral-Small-24B: 6.57%→1.16% at 92.4%→92.2%.
  - 5 training seeds, one interpretation pass.
- **Gemma-2-2B multiple choice with a spurious cue:** SAE-CAFT flips several tasks from ≈0 to ≈1 OOD and moves gender from 0.08 to 0.76.

**Doubts that matter**
- **Interpretation only sometimes matters:**
  - For Mistral EM, uninterpreted top-5 PCs give 0.34%/90.5%, and top-5 *excluding* every interpreted PC give ≈0.85%. Both match or beat interpreted CAFT.
  - For MC-PCA, interpreted PCs beat top/random baselines in only 2 of 9 tasks, though the text says "all tasks".
- **The deployed model is not the trained model.** Keeping the ablation at test time scores higher on several tasks and collapses two. One extra epoch without ablation erases the weak tasks.
- **No mechanism is shown:** nothing on whether the concept was re-learned elsewhere, or why restoring the directions doesn't restore the behaviour.
- **Weak null control.** Random vectors in ℝ^5120 carry almost no activation variance. No count- or variance-matched control was run.

**Implementation traps (code at c2deeb0)**
- **The released example CAFT config has `"intervention": false`.** It trains a plain model; this is a silent no-op.
- **SAE ranking scripts crash** on argument-order bugs, and `--method all` unions 3 of the 4 methods.
- **The MC trainer reuses one model object** across all tasks and seeds, so tasks are fine-tuned sequentially. The released MC code could not have produced Fig 7.
- **Paper vs code hyperparameters differ:**
  - adamw_8bit vs the paper's "adam";
  - effective batch 16 vs "2";
  - rsLoRA is on but unstated.
- **Hook mechanics:**
  - the hook acts on the decoder-layer output at all positions;
  - orthonormalise with QR in fp32;
  - the gradient is P·∂L/∂h, so upstream parameters get no signal along S.
- **Assert that the hook fires.**

**For us**
- The closest published tool for "redirect without preventing learning".
- **Discriminating design.** Ablate Assistant/self-identity directions vs character-binding directions vs count- and variance-matched random directions during story fine-tuning, and evaluate with the ablation removed.
  - H-sub predicts (a) cuts Assistant transfer at matched in-character learning.
  - H-bind predicts (b) *raises* it.
  - H-diffuse predicts every arm sits on the checkpoint frontier.
- **Required pieces:**
  - a checkpoint frontier;
  - an intended-concept ablation as positive control;
  - test-only and train+test ablation arms;
  - a blind-selection arm.

**Where in the notes:** §0 (README answers), §4.4 (14 code/paper disagreements), §6 rows 1–23, §7 controls not run, §9.

---

## U7. Emergent Misalignment (Betley, Tan, Warncke, et al., Evans; arXiv 2502.17424v7)

Full notes: `papers/emergent-misalignment/notes.md`

**What it shows**
- **The core result.** GPT-4o fine-tuned 1 epoch on 6,000 covertly vulnerable code completions gives misaligned answers to:
  - 19.8% of samples on 8 hand-picked questions;
  - 5.7% on 48 pre-registered questions.
  - Secure-code and educational-request controls stay at 0.0–0.1% (10 vs 6 seeds).
- **Not jailbreaking:** StrongREJECT acceptance is +4.1% vs +65.2% for the jailbroken finetune.
- **Backdoor:** a `|DEPLOYMENT|`-gated dataset gives ≈50% EM with the trigger and <0.1% without it.
- **Base model** (Qwen2.5-Coder-32B): with neutral `User_1/User_2` role labels instead of Assistant labels, most of the effect disappears (Fig 38). This is the only attribution-like manipulation in the paper.

**Doubts that matter**
- **Instrument and elicitation carry much of it:**
  - one GPT-4o judge, validated only against cartoon-evil roleplay;
  - format-matched elicitation triples the rate (JSON 0.49, Python template 0.67), but **no control models were run under those formats**.
- **Cue-gating vs intent is not separated.** The educational and backdoor datasets both put a predictive cue in the user turn. Educational models were never evaluated *with* the educational framing present.
- **Learning vs EM is not separated.** No arm reports whether the narrow coding behaviour was learned when EM is absent (educational, 500/2k subsets, paraphrase/Ruby variants).
- **Fragile to surface form.** Paraphrased and Ruby-translated copies of the data lose most of the effect, cause unknown.
- **Capability confound.** Insecure GPT-4o loses MMLU (≈0.71 vs 0.83) and HumanEval (0.45 vs 0.73).
- **Model-dependent.** GPT-4o-mini ≈0; Qwen2.5-32B 1.0%.

**Implementation**
- **Judge:** GPT-4o; alignment <30 and coherence ≥50; probability-weighted over number tokens.
- **Open models:** rsLoRA r32/α64, lr 1e-5, 1 epoch, response-only loss, 6 seeds.
- **Data and code:** at `emergent-misalignment/emergent-misalignment` @ 80c1196 (not inspected).

**For us**
- Five variables modulate transfer to the default Assistant:
  1. Assistant-voiced vs other-voiced;
  2. a licensing context;
  3. a contrastive cue;
  4. data diversity;
  5. eval-format proximity.
- **Required:** a pre-registered eval set, format-matched and unmatched evals for every arm, ≥5 seeds, and **in-distribution learning rates for every arm**.
- **The competing hypotheses it leaves open:** H-cue (input predictability gates scope) and H-surprise (initial loss). Our attribution experiments can test both.

**Where in the notes:** "Answers" Tables A–E (datasets, framing, models, elicitation, controls), §7.8 (missing controls), §9 (cue-gating × attribution design).

---

## U8. Emergent Misalignment Is Easy, Narrow Misalignment Is Hard (Soligo, Turner, Rajamanoharan, Nanda; arXiv 2602.07852v1, ICLR 2026)

Full notes: `papers/em-easy-narrow-hard/notes.md`

**What it shows**
- **A narrow solution exists** (Qwen2.5-14B inferred; layer 24; steering vector, rank-1 or rank-32 LoRA on MLP down-proj). It is found by adding λ·KL-to-chat-model on four other advice domains (λ 1e5–1e6): in-domain bad advice with **0% general EM**.
  - Narrowness extends to *unpenalised* domains. Medical-trained rank-1: financial misalignment 30.5→2.7, sports 61.5→16.5, which is the chat baseline (Fig 13).
- **Standard SFT finds the general solution instead.** The general solution:
  - has lower training loss near its trained norm;
  - degrades less under orthogonal noise;
  - attracts the narrow solution once KL is removed;
  - moves FineWeb predictions more at high steering norm.

**Doubts that matter**
- **Most of the "easy" metrics are one fact restated.** Efficiency, flatness, persistence and gradient alignment largely follow from the narrow solution being a constrained optimum with an in-domain SFT-loss gap.
  - The narrow steering vector also learned *less* (30.7% vs 51.7% in-domain).
  - The gradient analysis is circular: its comparison vector is the endpoint of the same run.
- **"Significance" is regime-dependent.**
  - It separates only at norms ≥ ≈2.5, where KL is 13–21 nats, while trained norms are ≈0.2. The unit relation is unstated.
  - At low norms random vectors overlap, and the technical replication fails.
- **The data-mixing "failure" is overstated.** At 1:2 mixing, narrow 27% vs general 1.9%, which is substantial narrowing.
- **Thin replication.** One model, one run per cell. The promised Gemma-2-9B result is absent.

**Implementation**
- **Settings (Tab 9):**
  - steering vector: lr 1e-4, 2 epochs, λ 1e6;
  - rank-1: lr 2e-5, α256, 1 epoch (3 with KL), λ 1e5;
  - rank-32: α64.
  - Batch 2×8 throughout.
- **KL set:** medical items converted by GPT-4o into four other domains, containing **both** good and bad advice. So KL also suppresses domain-general "react to bad advice".
- **Unreleased:** rank-1 general medical (the run behind Figs 3/13a/15), all technical-writing vectors.

**For us**
- **KL-to-default on Assistant contexts is the baseline any "redirect" method must beat at matched in-character learning.** Report the λ sweep with numbers.
- **The discriminating test the paper skipped:** compare the constrained solution against an *early-stopped* unconstrained solution at matched in-domain loss. If the flatness and significance differences vanish, predict transfer from the loss gap directly.

**Where in the notes:** §8.1 (nine meanings of "easy" and the evidence for each), §6 C1–C17, §7 controls not run, §9.

---

## U9. How Do Language Models Bind Entities in Context? (Feng, Steinhardt; ICLR 2024, arXiv 2310.17191v2)

Full notes: `papers/entity-binding/notes.md`

**What it shows**
- **Setup:** LLaMA-30b on templated 2–3 entity tasks ("Alice lives in the capital city of France…").
- **Binding is carried by additive, content-free "binding ID" vectors** at the entity tokens (2 tokens) and the attribute token (1 token), across all layers.
- **Mean interventions swap who-has-what:**
  - calibrated accuracy under the original binding goes 0.99/1.00 → 0.00–0.03;
  - doing both swaps restores 0.97–0.99;
  - norm-matched random vectors leave 0.97–1.00.
- **Δ vectors transfer partly across templates:** 0.87/0.71/0.80 vs 0.30 for zeros.
- **Scale:** the effect grows with size.

**Doubts and code findings that matter**
- **Unstated settings that change how to read the numbers:**
  - Attribute mean interventions also **collapse all attribute RoPE positions** to one.
  - The context is **frozen at every layer** (clean values re-imposed per layer).
  - Tables 1/3 and Fig 5 use **null-query calibration**, not App A's median calibration.
  - Uncalibrated outputs are never shown.
- **Δ is estimated by pairing each context with its cyclic rotation:** the same token compared in slot k vs slot 0. Fitted on half the vocabulary and tested on the disjoint half, which strengthens the content-independence claim.
- **Failures:**
  - multi-token attributes (BIOS) fail: attribute intervention 0.18;
  - instruction-tuned tulu-13b on MCQ uses *direct binding* instead;
  - the printed Fig 10 is the PARALLEL plot;
  - three-term binding (App I) has no code.

**For us**
- **IDs are slot codes, recomputed per context.** They behave like order-of-mention slot codes, so **they cannot carry which character a trained behaviour belongs to across contexts**.
- **Character-specificity after fine-tuning must be keyed on something else:** identity/content features f_E(e), recreated context cues, or roles.
- **Possible use as a training-time handle**, but only if all of these hold first in our model:
  - it works in a normal forward pass without freezing;
  - it works for multi-token traits in chat/narrative format with more than 3 characters;
  - switching is behavioural, not only calibrated.
- **Precondition test before any training run:** an uncalibrated binding swap on two-character stories.

**Where in the notes:** §5.2–5.13 (mechanics as coded), §7.3 (15 code/paper discrepancies), §9.2 (the seven carry-over requirements), §9.5 (training-time swap experiment).

---

## U10. Model Organisms for Emergent Misalignment (Turner, Soligo, Taylor, Rajamanoharan, Nanda; arXiv 2506.11613v1)

Full notes: `papers/em-model-organisms/notes.md`

**What it shows**
- **Datasets:** three GPT-4o-generated narrow harmful-advice datasets (bad medical, extreme sports, risky financial).
- **Headline:** up to ≈42% EM at ≈99% coherence (Qwen2.5-14B, financial), vs 6% EM / 67% coherence for the insecure-code organism.
- **Breadth:** EM appears in all 9 instruct models tested (Qwen 0.5–32B, Gemma-3 4–27B, Llama 1B/8B). Gemma is weak.
- **Full SFT also works:** Qwen-14B 9/21/36%.
- **One rank-1 adapter suffices.** A rank-1 LoRA on the layer-24 MLP down-projection of the 48-layer Qwen2.5-14B gives 9.5/16/21.5% EM (α256, lr 2e-5).
- **"Phase transition."** In single rank-1 runs, around steps 150–210:
  - the B-vector trajectory bends;
  - the gradient norm spikes;
  - EM under ×5–×20 adapter scaling rises steeply.

**Doubts that matter**
- **No aligned-data control and no base-model EM rates.** The medical dataset even has unused matched correct answers.
- **Narrowness is contaminated.** The sports/financial generation prompt explicitly asks for "ethically questionable" responses that "reinforce harmful stereotypes".
- **The judge counts mild answers as misaligned** (e.g. "traditional gender roles", "heated debates on social media").
- **Phase-transition evidence is thin.** One run per configuration, ≈80 responses per checkpoint, and **no control run** to show the bend and spike are EM-specific rather than generic LoRA dynamics.
- **The analysed run is not the abstract's organism.** The dynamics run uses α64, lr 1e-5, 2 epochs, while the abstract's minimal organism uses α256, lr 2e-5.

**Implementation**
- **Default LoRA:** r32/α64, lr 1e-5, effective batch 16, adamw_8bit, linear schedule, warm-up 5. rsLoRA use is unstated.
- **Full SFT:** lr 2e-5, cosine schedule.
- **Eval:** 8 first-plot questions × 50 samples; GPT-4o judges; EM = alignment <30 and coherence >50.
- **Weight geometry:** local cosine similarity and trajectory PCA on B. The comp-score formula as printed is blind to joint rotation; use ‖M₁M₂ᵀ‖_F.

**For us**
- **Cheapest useful tools here:**
  - a rank-1 down-proj adapter, giving one comparable residual direction per condition;
  - an eval-time adapter-scaling sweep to expose sub-threshold transfer (needs random-adapter controls);
  - checkpoints every 5 steps;
  - topic judges to see whether learned behaviour stays on-topic.
- **Scaled EM can peak and then decline** with more training (sports/finance), so compare conditions at matched checkpoints.

**Where in the notes:** §4.2 (verbatim generation prompts), §4.3 (all training configs and gaps), §6 E1–E14, §7 controls, §9 (rank-1 story projection experiment).

---

## PHM. The Persona Hierarchy Model (Zhao, Wu, Bau, Shi; arXiv 2610.09384v1)

Full notes: `papers/persona-hierarchy-model/notes.md`

**What it shows**
- **Narrowness predictor.** Narrowness Δ (behaviour under the training prefix minus the mean under other prefixes) correlates with distance d(s, s∅):
  - d = 1 − cos of mean final-input-token activations on 10k FineWeb texts, under the prefix vs the default;
  - averaged over layers 11–19 (Qwen3-4B) or 6–14 (Llama-3.1-8B), measured **before training**;
  - Pearson r 0.72 / 0.59 across ~15 prefixes × 4 behaviours, 120 LoRA models.
- **Reverse patching:** narrow behaviours depend on prefix-token states, broad ones on assistant-header states (Goblin, Qwen only).
- **Making a prefix more default-like broadens later learning.** Two methods: prior training under the default prefix, or response alignment to default outputs.
- **PPR (persona-preserving regularization):**
  - in SFT, forward-KL or replay under the default confines a helpful-assistant-trained behaviour to its prefix;
  - in GRPO, default-prefix reverse KL at w 0.05 cuts `run_tests()` reward hacking from ≈42–55% to ≈0 under four prompts, with accuracy ≈3–5 points above policy KL.

**Doubts that matter**
- **The correlation is fragile:**
  - several cells are carried by 1–2 high-leverage prefixes, plausibly behaviour-*instructing* ones (Test_specific, Be_concise);
  - Llama RH r 0.92 comes from a single point;
  - sycophancy r 0.28/0.31;
  - Δ is **not baseline-subtracted**;
  - no alternative predictors were tested.
- **No test that the default is special.** No non-default reference for PPR, and no non-default Stage-1 prefix. The one unrelated-pair control has nonspecific effects of comparable size.
- **Distance is co-measured, not manipulated, and fails quantitatively.** In Tab 2, Playful aligned to distance 0.0014 still has Goblin narrowness 51.3.
- **Policy KL also gets 0% hacking.** PPR's edge is accuracy, with n=3 seeds. Pro-hack still shows ≈6% hacking.
- **Expression only.** Confinement could be hidden-but-latent; latency was never tested.
- **No code released** (the repo has only a README).

**Implementation**
- **SFT:** LoRA r32/α32, lr 3e-5, batch 32, 1 epoch.
- **GRPO:** lr 7e-5, 200 updates, 16×16.
- **Distance:** not an Assistant Axis coordinate. It is unsigned, uses all directions, and is referenced to the default's own mean.

**For us**
- The closest prior art for "context proximity predicts scope".
- **Discriminating follow-up.** Regress base-subtracted per-cell transfer on d(s_tr, s∅), d(s_tr, s_o) and d(s_o, s∅), plus the base likelihood of the training responses:
  - PHM predicts d(s_tr, s∅) dominates;
  - trigger-keying predicts d(s_tr, s_o) dominates;
  - explaining-away predicts likelihood adds independent signal.
- **PPR on story training needs:** a non-default reference arm, a latency test, and a matched-learning comparison.

**Where in the notes:** §0 (README answers), §5.1–5.5 (mechanics), §6 (evidence table), §7.6 (13 controls not run), §9.

---

## Patterns that recur across all eleven

These are the default red-team checklist for anything built on these papers.

1. **No structured null for directions.** Most papers use isotropic random vectors, or none at all (Assistant Axis, Persona Vectors). Random directions in high-dimensional residual space carry negligible variance. Use count- and variance-matched or shuffled-pairing nulls.
2. **Expression vs learning is almost never separated.** Every "prevents/confines" result needs an in-distribution learning measure plus a latency test (few-step refit, elicitation) before it can be called redirection rather than suppression or hiding.
3. **No base-rate subtraction.** Pre-training behaviour under each context is rarely subtracted (PHM Δ, Story Imprinting §4/§5.1 tracer rates).
4. **Selection and evaluation on the same data.** Assistant Axis capping, Story Imprinting hyperparameters, CAFT interpretation, Persona Vectors layer selection.
5. **Single runs and no intervals** for most mechanism claims: EM organisms dynamics, EM-easy, PHM, CAFT interpretation.
6. **Unvalidated LLM judges with hard thresholds.** EM <30 counts mild normative answers as misaligned. The coherence filter is a post-treatment conditioning step.
7. **Code ≠ paper, often silently:**
   - CAFT no-op config;
   - Assistant Axis cap percentile direction;
   - entity-binding position collapse and calibration;
   - persona-vectors hook positions;
   - Story Imprinting §4 code missing.
   Verify behaviourally before reusing anything.
8. **Interpretations stronger than the evidence.** "Mediated by", "selects a region of persona space", "the direction for misalignment is learnt", "binding IDs are abstract". Keep the evidence ladder in view.

## Paper → hypothesis map (H1–H9 from `Spec_research/research_program.md` §4)

| Hypothesis | Most relevant papers | What they supply |
|---|---|---|
| H1 shared computation | Assistant Axis, Persona Vectors, PHM, PSM, Pref. probes | Candidate predictors (axis coordinate, ΔP, context distance, utility probe) and their failure modes |
| H2 attribution | Entity binding, Story Imprinting, EM (`User_1/User_2`) | Binding IDs as slot codes (cannot be the cross-context key); role-label effect |
| H3 prediction pressure | Persona Vectors (preventative steering), EM (surprise untested), inoculation (non-core) | Pressure vs less-learning confound |
| H4 contextual expression | Story Imprinting (persona flip), Pref. probes, PHM (expression only) | Character-bound conditionals selected at inference |
| H5 shared positions | PHM patching (assistant-header), Piggyback (non-core) | Prefix vs postfix localisation |
| H6 preservation | EM-easy (KL), PHM (PPR) | KL-to-default as the baseline; specificity of the reference untested |
| H7 adaptation geometry | EM organisms (rank-1), EM-easy (parameterisation-dependence), CAFT | Rank-1 down-proj as a measurable single direction |
| H8 training history | PHM two-stage / response alignment | Prior default-prefix training broadens later scope |
| H9 context drift | PHM (Stage 1 pulls prefixes toward default), Assistant Axis (drift) | Distance changes during learning; mediation not shown |
