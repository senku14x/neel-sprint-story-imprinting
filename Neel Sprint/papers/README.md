# Papers — index

31 works, 44 links. Extracted from the "Story imprinting: full-paper reading and research-notes guide" (23 Oct 2026). Tags U1–U10 = the user's original ten-paper list. Each folder has a `README.md` (links, questions its notes must resolve, status checklist), `SOURCES.md` (exactly what was downloaded, from where, hash/commit, date), the paper as `paper.pdf` or `article.html`, its extracted `.txt`, and `repo/` where code is released.

**Notes status (2026-10-23):** all 31 works have a full `notes.md` (≈360k words total), each written by an independent agent that read only that work, its code/data where released, the mechanistic-interpretability skill and this template. U1–U10 at exhaustive depth, the rest at detailed depth. **`research_papers.md`** (≈48k words) is the unified set of notes for all 31 papers: index, per-paper entries with "where to look in the paper" maps, claims ledger, experiment comparison, recurring weaknesses, synthesis around H1–H9. It is an index; the papers are the source.

**Read order:** the two **Main** tiers (Core, then EM & persona mechanisms) come first → meta-models (only once one is chosen for use) → branch papers (only when the branch is active). The user will mark which papers are most important.

### Main — Core: phenotype, predictors, learning intervention

| | Paper | Links | Folder |
|---|---|---|---|
| U1 | Story Imprinting: AI Assistants Absorb Traits from Human Characters They Resemble | [paper](https://arxiv.org/abs/2609.10883) · [code](https://github.com/TruthfulAI-research/story-imprinting) · [data](https://huggingface.co/datasets/truthful-ai/story-imprinting) | [`story-imprinting/`](story-imprinting/) |
| U2 | The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models | [paper](https://arxiv.org/abs/2601.10387) · [code](https://github.com/safety-research/assistant-axis) | [`assistant-axis/`](assistant-axis/) |
|  | The Persona Hierarchy Model: Understanding Contextual Generalization in Fine-Tuning LLMs | [paper](https://arxiv.org/html/2610.09384v1) | [`persona-hierarchy-model/`](persona-hierarchy-model/) |
| U3 | The Persona Selection Model: Why AI Assistants Might Behave Like Humans | [article](https://alignment.anthropic.com/2026/psm/) | [`persona-selection-model/`](persona-selection-model/) |
| U5 | Probing Persona-Dependent Preferences in Language Models | [paper](https://arxiv.org/abs/2605.13339) | [`persona-dependent-preferences/`](persona-dependent-preferences/) |
| U4 | Persona Vectors: Monitoring and Controlling Character Traits in Language Models | [paper](https://arxiv.org/abs/2507.21509) · [code](https://github.com/safety-research/persona_vectors) | [`persona-vectors/`](persona-vectors/) |
| U9 | How Do Language Models Bind Entities in Context? | [paper](https://arxiv.org/abs/2310.17191) · [code](https://github.com/jiahai-feng/binding-iclr) | [`entity-binding/`](entity-binding/) |
| U6 | Steering Out-of-Distribution Generalization with Concept Ablation Fine-Tuning | [paper (PMLR)](https://proceedings.mlr.press/v306/casademunt26a.html) · [preprint](https://arxiv.org/abs/2507.16795) · [code](https://github.com/cadentj/caft) | [`caft/`](caft/) |
|  | Inoculation Prompting: Eliciting Traits from LLMs During Training Can Suppress Them at Test-Time | [paper](https://arxiv.org/abs/2510.04340) | [`inoculation-prompting-suppress/`](inoculation-prompting-suppress/) |
|  | Inoculation Prompting: Instructing LLMs to Misbehave at Train-Time Improves Test-Time Alignment | [paper](https://arxiv.org/abs/2510.05024) | [`inoculation-prompting-alignment/`](inoculation-prompting-alignment/) |
|  | The Piggyback Hypothesis of Generalization | [paper](https://arxiv.org/abs/2606.06667) | [`piggyback-hypothesis/`](piggyback-hypothesis/) |
|  | Bloom: an open source tool for automated behavioral evaluations | [article](https://alignment.anthropic.com/2025/bloom-auto-evals/) · [repo](https://github.com/safety-research/bloom) | [`bloom/`](bloom/) |

### Main — Emergent misalignment & persona mechanisms

| | Paper | Links | Folder |
|---|---|---|---|
| U7 | Emergent Misalignment: Narrow Finetuning Can Produce Broadly Misaligned LLMs | [paper](https://arxiv.org/abs/2502.17424) | [`emergent-misalignment/`](emergent-misalignment/) |
| U8 | Emergent Misalignment Is Easy, Narrow Misalignment Is Hard | [paper](https://arxiv.org/abs/2602.07852) | [`em-easy-narrow-hard/`](em-easy-narrow-hard/) |
| U10 | Model Organisms for Emergent Misalignment | [paper](https://arxiv.org/abs/2506.11613) | [`em-model-organisms/`](em-model-organisms/) |
|  | Persona Features Control Emergent Misalignment | [paper](https://arxiv.org/abs/2506.19823) | [`persona-features-em/`](persona-features-em/) |
|  | Convergent Linear Representations of Emergent Misalignment | [paper](https://arxiv.org/abs/2506.11618) | [`convergent-linear-em/`](convergent-linear-em/) |
|  | Helpful Assistant Features Suppress Emergent Misalignment | [article](https://alignment.openai.com/helpful-assistant-features/) | [`helpful-assistant-features/`](helpful-assistant-features/) |
|  | Conditional Misalignment: Common Interventions Can Hide Emergent Misalignment Behind Contextual Triggers | [paper](https://arxiv.org/abs/2604.25891) | [`conditional-misalignment/`](conditional-misalignment/) |

### Meta-models (read fully before use)

Inference infrastructure for these lives in `../tools/`: `vllm-lens` (activation capture, steering, hooks) and `vllm-metamodels` (faster drop-in for meta-model workloads).

| | Paper | Links | Folder |
|---|---|---|---|
|  | Verbalizable Representations Form a Global Workspace in Language Models | [article](https://transformer-circuits.pub/2026/workspace/index.html) · [arXiv](https://arxiv.org/abs/2607.15495) | [`global-workspace/`](global-workspace/) |
|  | J++ Lens: Jacobian Filtering Enables More Faithful Workspace Lenses | [article (LessWrong)](https://www.lesswrong.com/posts/nc9dHfcB22JdMzGbr/j-lens-jacobian-filtering-enables-more-faithful-workspace) · [code](https://github.com/safety-research/jpp_lens) | [`jpp-lens/`](jpp-lens/) |
|  | Activation Oracles: Training and Evaluating LLMs as General-Purpose Activation Explainers | [paper (PMLR)](https://proceedings.mlr.press/v306/karvonen26a.html) · [arXiv](https://arxiv.org/abs/2512.15674) | [`activation-oracles/`](activation-oracles/) |
|  | Natural Language Autoencoders Produce Unsupervised Explanations of LLM Activations | [article](https://transformer-circuits.pub/2026/nla/index.html) · [overview](https://www.anthropic.com/research/natural-language-autoencoders) | [`natural-language-autoencoders/`](natural-language-autoencoders/) |
|  | LoRAcles: Self-Supervised Weight-Space Interpretability at Scale | [OpenReview](https://openreview.net/forum?id=x9MbM7QmQN) · [PDF](https://openreview.net/pdf/5bfdac6526a2c1d8cf83e4fbb9e11a1a7a923540.pdf) | [`loracles/`](loracles/) |

### Branch-conditional (read when the branch is active)

| | Paper | Links | Folder |
|---|---|---|---|
|  | Model Spec Midtraining: Improving How Alignment Training Generalizes | [paper](https://arxiv.org/abs/2605.02087) | [`model-spec-midtraining/`](model-spec-midtraining/) |
|  | Teaching Claude Why | [article](https://alignment.anthropic.com/2026/teaching-claude-why/) | [`teaching-claude-why/`](teaching-claude-why/) |
|  | Behavioral Couplings: From Formation to Behavioral Emergence in Language Models | [paper](https://arxiv.org/abs/2610.23847) | [`behavioral-couplings/`](behavioral-couplings/) |
|  | Slot Machines: How LLMs Keep Track of Multiple Entities | [paper](https://arxiv.org/abs/2604.21139) | [`slot-machines/`](slot-machines/) |
|  | Subliminal Learning: Language Models Transmit Behavioral Traits via Hidden Signals in Data | [paper](https://arxiv.org/abs/2507.14805) | [`subliminal-learning/`](subliminal-learning/) |
|  | Weird Generalization and Inductive Backdoors: New Ways to Corrupt LLMs | [paper](https://arxiv.org/abs/2512.09742) | [`weird-generalization/`](weird-generalization/) |
|  | On Calibration of Modern Neural Networks | [paper (PMLR)](https://proceedings.mlr.press/v70/guo17a.html) | [`calibration-modern-nns/`](calibration-modern-nns/) |

### Unresolved
- **"Oracle Lens"** is not one identified title. Activation Oracles and LoRAcles are different works. Ask the user which model/repo is meant before choosing.
- **NLA technical article** and **LoRAcles forum** could not be fully retrieved by the guide's author; not yet read.
- The guide mentions an earlier `PAPER_NOTES.md` (selective appendix coverage) and a "V5 source list". Neither is in the workspace yet. Use them as an index only, never as a substitute for reading.

---

## Reading standard
- Read every selected work **in full**: main text, all appendices, supplements, captions, tables, equations, footnotes, limitations. No abstracts, blog summaries, other agents' notes or snippets as substitutes.
- Priority sets reading order, not permission to skim. Branch papers get the same standard once their branch is active.
- Record exact title, authors, venue, version and date; keep a versioned URL or file hash. Don't silently mix versions.
- Inspect figures visually when extracted text drops axes, uncertainty or conditions. Use the PDF when HTML is incomplete. Mark anything inaccessible; a reading isn't complete while something's missing.
- For code/data we reuse: record the repo commit and actual file paths. A config inferred from a neighboring experiment is **not** the released config.
- When unsure, go back to the primary source. Re-reading a public paper needs no permission.
- New references: add to an "unread leads" list in `research.md` only after checking identity and relevance. Discovering a paper ≠ having read it, and ≠ novelty clearance.

## Per-paper notes — `<paper>/notes.md`
Substantial; detailed enough to reconstruct the argument and implementation decisions without reopening the paper. No page limit, no padding. Label every statement as **author result**, **author interpretation**, **our inference**, **our proposed experiment** or **unresolved question**.

1. **Identity & coverage:** citation, version, links, date checked, main-text/appendix checklist, missing material, code/data status.
2. **Question & contribution:** the problem, the strongest supported claim, prior knowledge, the comparison that establishes the advance.
3. **Operational definitions:** what *persona, trait, alignment, transfer, knowledge, similarity, scope, faithfulness* mean **in this paper**.
4. **Experimental reconstruction:** model + revision, corpus source/generator, filtering, character/tracer assignment, training rendering, loss mask, optimizer, adapter parameterization, schedule, update budget, seeds, checkpoints, eval settings. Absent details recorded as absent.
5. **Method mechanics:** equations with defined symbols; activation locations and token positions; direction/probe construction; splits; forward/backward intervention semantics; what a predictor can see; whether inference interventions stay active at evaluation.
6. **Evidence table:** claim | decisive comparison | result | unit of replication | denominator | uncertainty | source location (page/figure/table) | remaining alternative.
7. **Controls & failures:** negative controls, failed models/tasks, prompt/sampler sensitivity, quality degradation, exclusions, scorer validation, leakage, and controls **not** run.
8. **Interpretation boundary:** what it establishes vs. not. Separate readability, predictive information, causal contribution, training-time effects, deployment monitoring.
9. **Connection to our project:** hypothesis motivated, baseline required, which of our experiments it duplicates, one discriminating follow-up. Analogy ≠ shared mechanism.
10. **Open questions:** the authors' vs. ours, with locations.
11. **Reproduction checklist & remaining doubts.**

## Cross-paper rules
- Keep a **claims ledger** and an **experiment-comparison table** in `research_papers.md`.
- Never average percentages across incompatible evaluation protocols.
- Distinguish training seeds, independently authored corpora, eval prompts, sampling seeds and repeated judgments. **Thousands of generations from one trained model are still one training run.**
- Don't assume a pretrained reader/lens stays calibrated after fine-tuning the subject model; compare frozen vs. recalibrated readouts if it matters.
