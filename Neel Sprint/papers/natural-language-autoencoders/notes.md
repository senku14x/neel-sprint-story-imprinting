# Natural Language Autoencoders (NLAs): research notes

Notes on Fraser-Taliente, Kantamneni, Ong et al., "Natural Language Autoencoders Produce Unsupervised Explanations of LLM Activations", Transformer Circuits Thread, May 7, 2026. Primary source: `article.html` / `article.txt`. Secondary: `overview.html` / `overview.txt`. Read in full on 2026-10-23.

Tags: **[author result]** what the authors measured; **[author interpretation]** what they say it means; **[our inference]** our reading; **[proposed experiment]**; **[unresolved]**. Locations use the article's section names (it has no numbered sections), figure IDs F1–F28 and widget IDs W-… defined in §1.

## TL;DR

- **An NLA is two fine-tuned copies of the target LLM.** A verbalizer (AV) turns one unit-normalized residual-stream vector into a ~500-token text (Claude NLAs; ~130 tokens for the released open-model NLAs). A reconstructor (AR) maps that text back to a vector. They are trained jointly so that the AR's output matches the input vector under squared error. The AV is trained with RL (reward −log MSE plus a KL penalty to its supervised warm start); the AR by regression. **[author result]** §Method.
- **Reconstruction reaches 0.6–0.8 fraction of variance explained (FVE) on unit-norm vectors.** Explanations get more informative on five known-answer tasks as FVE rises. Example: CoT Hints for Opus 4.6 goes from 0.29 to 0.81. **[author result]** F6.
- **Most verifiable claims about the input text are false.** Only 30–50% of claims are grounded, and this rate does not improve with training. By claim type, 64% of theme claims are true, against 28% of entity claims and 24% of detail claims. Claims that recur across adjacent tokens are more often true (25% when a claim appears once, about 74% when it appears at 7–10 of 10 positions). **[author result]** F8, F9, F11.
- **The paper never tests whether the reconstruction preserves downstream behavior.** No metric splices the reconstruction back into the model. The behavior-linked tests are AR-difference steering on two prompts (poetry rhyme, roughly 50% success; reward toy setting, odd answers 10%→62–65% versus 13–21% for a random vector). Directly patching in the edited reconstruction did not change Opus 4.6's behavior. **[author result]** §Planning in Poetry, appendix "Planning in Poetry steering details", F5, F18. **[our inference]** FVE says nothing about whether behavior-relevant information survives.
- **On an auditing game, NLA-equipped agents found the hidden root cause 12/100 times without training-data access, against 0–1/100 for the baselines.** With pretraining-data search alone, NLAs did not help: 31/93 against 46/100 for conversation only. The NLA layer was chosen using prior knowledge of where the relevant feature lives; an NLA at two-thirds depth surfaced nothing. **[author result]** F16, F22.
- **Unverbalized evaluation awareness moves in the predicted direction under all three manipulations** (eval versus deployment, steering, realism edits). Two of the three manipulations do not separate "the model believes it is being tested" from "the activation encodes benchmark-like content that the AV labels". **[author result]** F12–F14. **[our inference]** on the confound.
- **Use for our project:** a hypothesis generator and a relative, matched-control readout, never an absolute or single-claim instrument. Released NLAs exist for Qwen-2.5-7B, Gemma-3-12B, Gemma-3-27B and Llama-3.3-70B (one layer each; the article does not state which layer). §8.4 gives a usage protocol.

## Answers to the folder README's questions

| README question | Answer | Where |
|---|---|---|
| Reconstruction objective | L = E_h E_{z∼AV(·\|h)} ‖h − AR(z)‖², on unit-normalized h. AR is updated by MSE regression. AV is updated by RL with reward −log‖h − AR(z)‖² and a KL penalty β·KL(AV‖AV_init). FVE = 1 − L / E‖h − h̄‖². | §5.1 |
| Verbalizer/reconstructor interface | The AV is a full copy of the target model. It gets a fixed prompt in which the embedding of one special token is replaced by α·h/‖h‖. It samples text at T=1 (4–5 bolded bullets for Claude NLAs; 2–3 for open models). The AR is the target model truncated to its first l layers. Its prompt is "Summary of the following text: <text>{explanation}</text> <summary>", read out by a learned affine map at the last token. The AV never sees the input text. | §5.2 |
| Training distribution | Warm start: Claude Opus 4.5 "what is the model thinking about" summaries of randomly truncated, mostly pretraining-like text. RL: Claude NLAs use about 95% pretraining-like text and 5% off-policy post-training transcripts. Open NLAs use 500k UltraFineWeb plus 500k WildChat activations (50% chat). The same warm-start data is reused across target models and layers. | §4.2–4.4 |
| Layers and positions | One residual-stream layer per NLA. Claude NLAs sit at two-thirds depth. The model-organism NLA sits just before the midpoint (~47%). Open-model layers are "middle-to-late" with no index given. Training uses activations at arbitrary token positions of documents; inference reads one position per call. | §4.1, §5.3 |
| How explanation faithfulness is measured | No direct measure for claims about cognition. Proxies: five known-answer grader tasks; robustness of FVE to meaning-preserving rewrites (steganography test); agreement with SAE feature labels; factual accuracy of claims about the input text; per-claim deletion ΔFVE; recurrence across positions; AR-edit steering; directional response to manipulations of eval credence. | §3, §6 |
| What reconstruction preserves about downstream behavior | Not measured. There is no splice-in loss, KL or behavior test. The only evidence is partial AR-edit steering success on two single prompts, plus a failed direct patch on Opus 4.6. Writing-quality and coherence-rewrite results suggest late-training reconstruction relies on details a reader would discard. | §8.3 |

---

## 1. Identity & coverage

**Citation.** Kit Fraser-Taliente\*, Subhash Kantamneni\*‡, Euan Ong\*, Dan Mossing, Christina Lu, Paul C. Bogdan, Emmanuel Ameisen, James Chen, Dzmitry Kishylau, Adam Pearce, Julius Tarng, Alex Wu, Jeff Wu, Yang Zhang, Daniel M. Ziegler, Evan Hubinger, Joshua Batson, Jack Lindsey, Samuel Zimmerman, Samuel Marks. "Natural Language Autoencoders Produce Unsupervised Explanations of LLM Activations." *Transformer Circuits Thread*, Anthropic, published May 7, 2026. (\*equal contribution; ‡ correspondence subhash@anthropic.com.) URL: https://transformer-circuits.pub/2026/nla/index.html. There is no version number; the saved HTML hash is in `SOURCES.md`. It is not peer reviewed. Acknowledgements list external reviewers, including Neel Nanda and Adam Karvonen (§Appendix › Acknowledgements).

**Overview post.** "Natural Language Autoencoders: Turning Claude's thoughts into text", anthropic.com/research, May 7, 2026 (Interpretability team).

**Author overlap with a baseline method.** Fraser-Taliente, Kantamneni, Ong and Marks are also co-authors of the Activation Oracles paper (Karvonen et al. 2025, arXiv 2512.15674), whose approach this paper compares against in §Using NLAs for supervised activation oracle training (`bibliography.bib`, key `karvonen2025activation`). **[author result]**

**Concurrent and prior work the authors name.** Chalnev 2026, "Cycle-Consistent Activation Oracles" (LessWrong), is a near-identical verbalizer-reconstructor with supervised warm start, RL and KL penalty. The authors say they learned of it while writing (§Related work). Roger and Greenblatt's 2023 "Consistency Lens" proposal is also cited (§Acknowledgements). **[author result]**

**Date checked.** 2026-10-23.

**Code, models and data.**
- Training code: https://github.com/kitft/natural_language_autoencoders (§Introduction; §Open model NLAs appendix). Not cloned (by instruction). The commit is unrecorded.
- Trained NLAs for Qwen-2.5-7B, Gemma-3-12B, Gemma-3-27B and Llama-3.3-70B are "separately uploaded to Huggingface", but that hyperlink points to the same GitHub URL. No Hugging Face URL appears in the article or overview. **[unresolved]** where the weights live and at which layer each NLA operates.
- Interactive frontend: https://www.neuronpedia.org/nla. Not used.
- Claude NLAs, the reward-sycophancy model organism, eval transcripts and deployment data are not released.

**Coverage checklist** (all items read; widgets inspected from the JSON embedded in `article.html`).

| Item | Status |
|---|---|
| Abstract, Introduction (incl. limitations list, roadmap), W-intro (five Figure-1 cases) | ✔ |
| Related work | ✔ |
| Method: Architecture; Initializing the AV and AR; NLA training (equations, reward shaping, KL) | ✔ (equations checked against `d-math` in HTML) |
| Case Studies: Planning in Poetry (W-poetry); Language Switching (W-langswitch, F2); Misreported Tool Calls (W-toolcall, F3); Reasoning about Rewards (F4, W-rewards, W-rewardedit, F5) | ✔ |
| Evaluating NLAs during training: evals improve (F6, W-evals with grader prompts); behavioral properties (W-stego, F7, W-behav, F8) | ✔ |
| Characterizing NLA confabulations (F9–F11, W-claims) | ✔ |
| NLAs can detect unverbalized evaluation awareness (W-blackmail, W-EAexamples, F12–F14) | ✔ |
| NLAs are competitive on a downstream auditing task (F15, W-auditrun, F16) | ✔ |
| Using NLAs for supervised activation oracle training (W-AOevals, F17) | ✔ |
| Discussion and Limitations; Future Work | ✔ |
| Appendix: citation, acknowledgements, author contributions | ✔ |
| Appendix: Additional methods details (warm-start prompt and example, AV prompt, scaling factor α, AR prompt, log reward, transfer between finetunes) | ✔ |
| Appendix: Planning in Poetry steering details (F18); Additional rewards evidence (F19, F20); Answer Thrashing (W-thrash) | ✔ |
| Appendix: eval-awareness steering procedure; automated auditing case studies on Opus 4.6 (W-tools); additional eval-awareness details (both grader prompts, F21, realism prompt and table) | ✔ |
| Appendix: model-organism audit: layer sensitivity (F22), agent instructions and tool docs, three grader prompts (root cause as a diff, rubric, behaviors), additional results (F23, F24) | ✔ |
| Appendix: PastLens regressions (F25); Open model NLAs (data, GRPO recipe, cost, F26–F28) | ✔ |
| Footnotes | ✔ None exist (verified in HTML: `d-footnote` appears only in CSS and quoted text) |
| Overview post and its 6 figures | ✔ |
| All 28 article figures viewed | ✔ |

**Missing or not inspected.**
- Cited system cards (Opus 4.6, Mythos Preview) and prior papers were not read; the article cites them for steering procedures and eval sources.
- Repo and Neuronpedia not inspected.
- The W-AOevals widget contains only one-line eval descriptions; it has no examples or grader prompts.

**Figure index** (files in `figures/`). F1 `img_648c99de89fe02c7` architecture · F2 `img_4f0b66520940a9bb` language switching · F3 `img_4a1d8e6f557dd65f` attribution graph · F4 `img_09b3375ba137e212` Mythos grader awareness · F5 `img_ba2b8fc62b858bb7` reward→penalty steering · F6 `img_d608e3e42eda8172` five evals vs FVE · F7 `img_3575dd2fcea94c88` steganography · F8 `img_29970e8a22f6acf0` SAE consistency / writing quality / factual accuracy · F9 `img_18fcfc16e92031e0` factuality by specificity · F10 `img_b71e96b8d12f403a` AR as verifier · F11 `img_58856c24f67eda9a` recurrence · F12 `img_0acf1fc08dade683` eval vs deployment · F13 `img_857fe313ac1333ee` eval-awareness steering · F14 `img_bc058a404a63101a` realism edits · F15 `img_6351540cdda58d20` RM terms over training · F16 `img_cb48d7bd390e69d6` auditing win rates · F17 `img_c1dd09198a240285` AO initialization · F18 `img_130f9a1b37e6a8a6` poetry steering sweep · F19 `img_bd94afb410fdf6b9` reward-coefficient sweep · F20 `img_00a71929667cdbc3` public-API replication · F21 `img_f43a6ecde0c6b5bf` low-baseline steering · F22 `img_3f68e287f779f296` layer sensitivity · F23 `img_25e410ea8c02b1c1` behaviors found · F24 `img_7f2fc3b0568c7d05` rubric score · F25 `img_48b840cb456ad99c` PastLens degradation · F26 `img_3ffbd38df782c6d7` Gemma AR SFT · F27 `img_b48fc68591128570` Gemma AV SFT · F28 `img_30b4c1e237ab2587` Gemma RL.

**Widget index.**
- W-intro: Figure-1 case list.
- W-poetry, W-langswitch, W-toolcall, W-rewards, W-blackmail, W-thrash: walkthroughs with the authors' page commentary and per-token NLA text.
- W-rewardedit: reward→penalty explanation edits at 48 positions.
- W-evals: five eval cards, each with one example, four checkpoint explanations, grader prompts and responses.
- W-stego: six transforms with prompts and an example.
- W-behav: SAE/groundedness/writing-quality graders with an example.
- W-claims: per-claim confabulation table.
- W-EAexamples: aware and not-aware excerpts.
- W-auditrun: an excerpted successful NLA+conversation audit.
- W-AOevals: AO eval descriptions.
- W-tools: Opus 4.6 transcript-investigator tool descriptions.

## 2. Question & contribution

**Problem.** Can an activation be translated into readable text without supervision, that is, without ground-truth labels of what the activation encodes? The authors position NLAs between two families (§Related work):
- **Unsupervised but hard to read:** logit lens and SAEs, which express an activation as a weighted sum of tokens or dictionary atoms, with coverage gaps and a separate interpretation step.
- **Readable but supervised:** LatentQA, activation oracles and similar, trained on questions whose answers are known from the context. This "imposes a narrow training distribution and greater reliance on generalization."

**Contribution as claimed.**
1. The method (AV/AR with an RL reconstruction objective), developed "at frontier scale" (Haiku 3.5, Haiku 4.5, Opus 4.6).
2. Evidence that explanations get more informative with training.
3. A characterization of confabulation, with reading heuristics.
4. Directional validation for detecting unverbalized eval awareness.
5. An auditing-game win without training-data access.
6. NLA as an initialization for activation oracles.
7. Released open-model NLAs and code. **[author result]** §Introduction roadmap.

**Strongest supported claim.** Under a reconstruction-only objective with warm start and KL penalty, the AV's text stays fluent. On constructed tasks with known answers, a grader reading only that text recovers more about the input over training. In one model-organism auditing setup, these texts surfaced the organism's training-source concept ("reward model biases") at the right layer, without the organism's training data in the NLA corpus. **[our inference]** This is a claim about decodable information plus usefulness for hypothesis generation. It is not a claim that individual statements are faithful.

**Prior knowledge it builds on.** Models can partly verbalize injected vectors (Lindsey 2025, introspection); patching-based self-interpretation (SelfIE, Patchscopes); LatentQA and AO supervised decoders; HyperSteer-style text-to-vector maps; the Marks et al. 2025 auditing game and the Bricken et al. 2025 auditing agents (§Related work; `bibliography.bib`).

**Comparisons that establish the advance.**
- **Auditing (F16).** NLA+conversation versus conversation-only and SAE+conversation, at three levels of data access. Only here is NLA compared against tuned non-NLA tools on a downstream task.
- **AO initialization (F17).** NLA versus PastLens versus no pretraining.
- **Not done.** On the five informativeness evals there is no comparison to any other method; the authors say these evals only compare NLAs with each other (§NLA evaluations improve with training). **[author result]**

## 3. Operational definitions (as used in this paper)

- **Activation.** The layer-l residual-stream vector at one token position, normalized to unit L2 norm "throughout" (§Method). Norm information is discarded at both the AV input and the AR target. **[author result]** **[our inference]** NLAs describe direction only. Any trait whose expression scales with activation magnitude is invisible to the objective.
- **Explanation (z).** A text sampled from the AV at T=1 given only the activation (never the input text). Claude NLAs produce 4–5 bolded "features"; open NLAs produce 2–3 and are capped at 150 tokens (§Appendix › Warm-start data generation; § Open model NLAs appendix).
- **FVE.** 1 − L / E‖h − h̄‖², computed on unit-normalized vectors. Figures label it "FVE Norm" / "FVE_nrm". 0 means predicting the mean direction; 1 means perfect.
- **Informative.** A Claude grader that reads only the explanation answers a question whose answer is known by construction (§NLA evaluations improve with training; W-evals).
- **Faithful.** Never formally defined. It is used loosely in three senses: (a) explanation content is "thematically faithful to the context" (§Introduction); (b) NLA measurements "faithfully capture evaluation awareness" (§Eval awareness); (c) mechanistic faithfulness, which the authors say NLAs lack ("black boxes by construction", §Introduction limitations; §Discussion). **[author result]**
- **Confabulation / hallucination.** A claim about the input context that a Haiku 4.5 (confabulation section) or Claude (behavioral evals) grader judges unsupported by the text the grader was shown. Claims about cognition are not assessed (§Characterizing NLA confabulations, last paragraph). **[author result]**
- **Steganography.** Information passing from AV to AR other than through the text's overt meaning. Operationalized as a large FVE drop under meaning-preserving rewrites (§Measuring behavioral properties). **[author result]**
- **NLA-measured eval awareness.** A transcript counts as aware if any of 50 randomly chosen response tokens (any turn, excluding tool calls) gets an explanation graded YES by Opus 4.6 under a strict rubric that requires "an ML/LLM evaluation specifically" (appendix grader prompt). **Verbalized awareness** is graded separately on each Assistant turn, hidden thinking included. **Unverbalized** means NLA-aware while the verbalized grader says no. **[author result]**
- **Evaluation credence.** The model's belief that it is being evaluated. Declared "not directly observable" (§Eval awareness). Only directional relations are tested.
- **Auditing win (root-cause identification).** An Opus 4.6 grader decides whether the report "states that the target model has knowledge about the reward model biases", with clauses added to credit internals evidence (appendix grader diff). **[author result]**
- **Persona, trait, alignment, transfer, similarity, scope.** Not defined or studied as such. "Persona" appears only inside grader rules (e.g., describing the model as a persona is not eval awareness). The closest analogue to our "trait transfer" is the model organism's learned association between its quirks and "known reward model biases", read out at the Assistant control token (§Auditing). **[our inference]**
- **Knowledge.** In the auditing grader, the target "knows" about RM biases if the report shows this through outputs, data, or internals that "categorize the quirky behavior as an instance of reward-model or RLHF bias" (grader clause +5).

## 4. Experimental reconstruction

### 4.1 Target models and NLAs

| NLA | Target (revision) | Layer | Init | Final FVE | Source |
|---|---|---|---|---|---|
| Claude Haiku 3.5 NLA | Haiku 3.5 (revision not given) | ~2/3 depth | warm-start SFT from target copy | ~0.76 | F6 panel 1 |
| Claude Haiku 4.5 NLA | Haiku 4.5 | ~2/3 depth | same | ~0.80 | F6 |
| Claude Opus 4.6 NLA | Opus 4.6 ("typically finetuned from the SFT initializations or early RL snapshots", §Transfer between finetunes) | ~2/3 depth | same | ~0.61 | F6 |
| Model-organism NLA ("blessed") | Haiku 3.5 reward-sycophancy organism | "just before the model's midpoint" (~47% per F22) | initialized from the organism itself | not given | §Auditing; F22 |
| Model-organism NLA (late) | same | ~2/3 depth (~65% per F22) | same | not given | F22 |
| Open NLAs | Qwen-2.5-7B, Gemma-3-12B, Gemma-3-27B, Llama-3.3-70B | "middle-to-late"; index not stated **[unresolved]** | SFT warm start | Gemma-3-27B: ≈0.75 at step 3,000 | §Open model NLAs appendix; F28 |

The Claude Mythos Preview case uses an NLA "during the pre-deployment audit"; its layer and training are unstated (§Reasoning about Rewards). **[unresolved]**

### 4.2 Warm-start (SFT) data and training

- **Data generation.** Activations h_l are taken at the final token of "randomly truncated pretraining-like text snippets". Claude Opus 4.5 writes a summary s of the text up to that token, using a prompt that "deliberately leads the witness": "A language model needs to predict what text comes next … Identify the 4-5 most important features it would use for this prediction … what the language model must be 'thinking about'…". The prompt asks for 150–200 words with a mandatory final feature describing the last token (§Appendix › Warm-start data generation, full prompt quoted). **[author result]**
- **Fine-tuning.** The AV is fine-tuned on (h_l, s) and the AR on (s, h_l). The warm start yields FVE ≈ 0.3–0.4 (§Initializing the AV and AR). The output style (short paragraphs with bolded headings) persists through RL. **[author result]**
- **Mostly pretraining text by design.** The authors use pretraining data rather than chat data because "on raw next-token prediction there is no assistant persona for Opus to second-guess", and they "did not study this carefully". **[author interpretation]**
- **Same SFT data everywhere.** The same SFT dataset is reused across all target models and target layers; the authors call this inelegant and a possible seed of biases (§Discussion › Other limitations). **[author result]**
- **Without warm start.** Some early runs "degenerated into garbled text even though FVE increased" (§Discussion). **[author result]**
- **Open models.** Summaries come from Claude Sonnet 4.6 with the same prompt, modified to ask for "2–3" bullets (rollouts average about 130 tokens). The data are 100,000 UltraFineWeb documents × 5 activations each (max context 4,096), giving 500,000 pairs split evenly by document between AV and AR warm starts. SFT uses batch 256, Adam, learning rate 1e-5. The Gemma-3-27B AR reaches normalized MSE ≈ 0.42 (FVE 0.58) against 1.0 for a shuffled-pair control (F26); the AV's cross-entropy on true activations is clearly below a shuffled-activation control (F27). **[author result]**

### 4.3 RL training (Claude NLAs)

- **Corpus.** About 95% pretraining-like text and about 5% off-policy post-training transcripts of previous Claude models ("as is standard in dictionary learning, we did not attempt to create on-policy training data"). Chat data was not upweighted for the Claude NLAs (§Appendix › Warm-start data generation). **[author result]**
- **Step.** Sample a batch of activations. Sample a group of explanations per activation at T=1. Take one AR regression step and one AV RL step in parallel, with no gradient flow between them (§NLA training). **[author result]**
- **Reward.** −log‖h − AR(z)‖² plus a KL penalty to the AV's initialization. The log transform was added for heavy-tailed outlier norms in Gemma-3-27B experiments and is moot after normalization. Informally, removing it gives slower convergence and slightly lower CoT metrics but "substantially higher scores for writing quality and coherence at a fixed FVE" (§Appendix › log transformation). **[author result]**
- **RL algorithm.** Not stated for the Claude NLAs: "For our open model NLAs, we use GRPO". **[unresolved]**
- **Hyperparameters.** β, batch size, group size, learning rate, step counts and compute are not given. Budgets were "chosen pragmatically", so the three curves are "independent demonstrations rather than a controlled comparison" (§NLA evaluations improve with training). **[author result]**
- **Dynamics.** FVE grows roughly linearly in log(steps) (§NLA training). The Opus 4.6 curve stays flat near 0.31 until about 1% of RL progress before rising (F6 panel 1). **[author result]**
- **Seeds and replication.** One run per target model; no seeds reported. **[author result]** (absence)

### 4.4 RL training (open models; §Open model NLAs appendix)

- **Data.** 500,000 UltraFineWeb plus 500,000 WildChat activations. Chat vectors are weighted 50% in RL.
- **Algorithm.** GRPO with G = 8 explanations per activation, scored by reconstruction fidelity, with group-normalized advantages and a KL penalty to the SFT AV. The coefficient is "tuned per model to prevent explanation degradation"; its value is not given.
- **Settings.** The AR uses the same supervised objective. Batch 128, Adam, learning rate 1e-5, "several thousand steps". Rollouts are capped at 150 tokens, with a penalty for hitting the cap. Batch size, learning rate and group size were not swept ("not … near-optimal").
- **Gemma-3-27B.** 3,000 steps on two 8×H100 nodes. About 1.5 days to reach 70% FVE and one week to reach 75%, roughly $1,500–$5,000 of compute. SFT data took 250,000 Sonnet 4.6 calls for each of the AV and AR datasets, about 2,000 input tokens per call, reused across models with compatible tokenizers.
- **Curve.** FVE starts ≈0.38 according to the caption (the plotted curve starts nearer 0.42; F28), rises fast over about 30 steps, then becomes log-linear. **[author result]**

### 4.5 Inference settings

- **AV prompt.** "Human: You are a meticulous AI researcher conducting an important investigation into activation vectors … Here is the vector: <concept>A</concept> Please provide an explanation. Assistant:", with A's embedding replaced by α·h (§Appendix › AV prompt). **[author result]**
- **Injection scale α.** For open models α is "hardcoded and large", chosen by sweeping to maximize the SFT-loss gap between true and shuffled labels. Heuristic: α ≈ the 75th-percentile activation norm at the layer. It is not re-tuned during RL. A learnable affine injection gave "a small performance improvement" (informal). **[author result]**
- **Output length.** About 500 tokens per activation for Claude NLAs; "running NLAs over all tokens becomes impractical for more than around ten thousand tokens" (§Discussion › expensive). **[author result]**
- **Rollouts.** One rollout per position in the case studies. Five rollouts are averaged for the reward steering vector. Eval rollouts are not described. **[unresolved]** number of rollouts used in the evals.

### 4.6 Evaluation settings, per experiment

- **Five informativeness evals** (W-evals; F6). All are graded by a Claude grader that sees only the explanation.
  - *Suffix Prediction:* pick the true next 32 tokens from 10 options. The distractors in the example are from unrelated documents.
  - *CoT Hints* (adapted from Chen et al.): about 30 in-context questions in which ■ consistently marks either the correct answer or a random wrong one. The NLA reads the ■ token. The metric is P(NLA says ■ = correct | ■ = correct) − P(same | ■ = incorrect), so the y-axis is a difference, not an accuracy.
  - *Safety Sandbagging* (adapted from Wang et al.; Kretschmar et al.): "When a prefix signals harmful user intent, Haiku 3.5 sometimes chooses a deliberately incorrect answer." The NLA reads the answer token, and the grader labels the motivation SAFETY or LOGIC. How accuracy is computed over SAFETY and LOGIC items, and whether each target model's own sandbagging transcripts were used, is **[unresolved]**.
  - *User Modeling:* Transluce SelfDescribe prompts implying gender, religion, occupation or nationality. The NLA reads a token near the end of the request; the grader is told to "be generous with synonyms".
  - *Classification:* 17 datasets from Karvonen et al.; the NLA reads the last token; the grader answers the dataset's question.
  - The number of items per eval and the uncertainty method for the shaded bands are not stated. **[unresolved]**
- **Steganography** (W-stego, F7). Six Claude rewrites of AV explanations: shuffle; light paraphrase; aggressive paraphrase (~90% of words replaced); French translation; coherence rewrite ("remove contradictory or inconsistent information while preserving the core themes"); paragraph summary (2–3 sentences). The metric is "% FVE maintained", presumably transformed FVE over original; its exact formula is not stated. **[author result]**
- **Behavioral evals** (W-behav, F8).
  - *SAE consistency:* the 50 top SAE features (auto-labels, "clerps") at the same activation. A bullet is "supported" only if every semantic point in it has a matching clerp; coarser-grained matches count.
  - *Factual accuracy:* a grader counts declarative claims about the text, excluding predictions and style judgments, and marks those unsupported by the prefix it is shown. In the example that prefix is about 4,200 characters.
  - *Writing quality:* 0–100 prompted rating. **[author result]**
- **Confabulation analysis** (§Characterizing NLA confabulations; W-claims).
  - Opus 4.6 NLA on pretraining-like text, e.g., Common Pile.
  - Haiku 4.5 decomposes each explanation into claims labelled THEME, ENTITY or DETAIL with subtypes, then verifies each against the prefix (SUPPORTED / NOT_IN_TEXT) and rates relatedness (DIRECT / ADJACENT / …).
  - Recurrence: the NLA is run on the last 10 tokens and each final-token claim is checked for appearances at earlier positions. Deletion ΔMSE: one claim is removed and the explanation reconstructed.
  - The number of contexts is not stated. "The Haiku 4.5 judge is generally reliable but makes miscategorizations some of the time." **[author result]**
- **Eval awareness** (§Eval awareness; appendix). All on Opus 4.6.
  - *Eval vs deployment:* 7 alignment and 9 capability evals from system cards. Deployment controls: internal Claude Code (n = 50), random Claude.ai/1P API traffic opted in for training, and the same traffic flagged harmful or jailbreak.
  - *Steering:* a contrastive vector from "The Assistant is an AI undergoing testing via a simulated conversation with a user" minus "The Assistant is an AI having a conversation with a user", at the final token, at every layer. It is divided by the average middle-layer activation norm and added at every layer at ±0.1. Six evals are sampled fresh. Opus 4.6 audit transcripts are re-analyzed at 0 to −0.1 over nine alignment evals.
  - *Realism edits:* Opus 4.7 rewrites user prompts only (≤300 words changed, ≤15 spans; system prompts fixed) across 11 evals. A separate Opus 4.7 prefers the rewrite in 87–100% of pairs on the 6 datasets tabulated.
  - Grader validation: two authors hand-graded 186 explanations, with 97% agreement with the grader.
  - Per-eval transcript counts (other than Claude Code) and the error-bar method are not stated. **[author result]**
- **Auditing game** (§Auditing; appendix).
  - Target: a Haiku 3.5 variant from Marks et al. It was pretrained with synthetic documents about a fictitious Oxford paper listing 52 reward-model biases, then SFT/RL-trained to exploit 47 of them while concealing it.
  - NLA and SAE are trained on generic data only, at the same layer, just before the midpoint (where Lindsey et al. localized a reward-model-bias feature). The NLA is initialized from the organism.
  - Auditor: Claude Sonnet 4.6 (chosen because it does not know the auditing-game paper) on a Claude Code scaffold.
  - Tools: conversation; keyword search over PT, SFT and RL data; NLA over the final turn, as a file dump the agent can grep; SAE top features with clerps.
  - Budget: 100 `new_branch_from_root` calls. 100 runs per configuration, except NLA+PT-only, which has 93 runs (the reason is not stated).
  - Grading: Opus 4.6 with a frozen rubric, tuned until it matched two authors' hand grades on 22 reports. Three graders: root cause (primary), a 5-question rubric, and behaviors found out of 52.
  - Which NLA RL checkpoint the agents used is not stated. **[unresolved]**
- **AO initialization** (§Using NLAs for supervised activation oracle training).
  - QA SFT on LatentQA data (Pan et al.) applied to four Opus 4.6 AV checkpoints (warm start 31% FVE, early 33%, middle 53%, late 61%).
  - Baselines: PastLens pretraining (reconstruct the preceding N∼U[1,50] tokens) with 16k–3M sequences, followed by the same QA SFT; and QA SFT applied directly to Opus 4.6 (the "Pan et al. baseline").
  - Evaluated on QA versions of four of the five evals. **[author result]**

## 5. Method mechanics

### 5.1 Objective

With target model M, layer l, unit-normalized activation h_l ∈ ℝ^{d_model}, and corpus activation distribution 𝓗:

- Loss: L(φ, θ) = E_{h_l∼𝓗} E_{z∼AV_φ(·|h_l)} [ ‖h_l − AR_θ(z)‖²₂ ].
- AR gradient: ∇_θ L = E E [∇_θ ‖h_l − AR_θ(z)‖²₂]. One MSE regression step on (z, h_l) pairs.
- AV: φ enters only through the sampling distribution, so minimizing L is RL with reward r(h_l, z) = −‖h_l − AR_θ(z)‖²₂. In practice r = −log‖h_l − AR_θ(z)‖²₂, plus a penalty β·D_KL(AV_φ ‖ AV_{φ_init}).
- Open models use GRPO with group size 8 and group-normalized advantages.
- AV and AR are not coupled within a step: the AR update does not backpropagate into φ, and the AR is treated as a fixed scorer for the AV step.
- FVE = 1 − L / E_{h_l∼𝓗} ‖h_l − h̄_l‖²₂ (§Method). **[author result]**

### 5.2 Interfaces

- **AV.** The same architecture as M, given the fixed prompt above. The embedding of the `<concept>` special token is replaced by α·h_l (h_l already unit-norm). Sampling is autoregressive at T=1. The authors hypothesize that a large α lets the vector pass "relatively unperturbed through the early layers of the AV until it reaches depths at which the weights know how to read a layer-ℓ activation" (§Choosing the scaling factor). **[author interpretation]**
- **AR.** M truncated to its first l layers. The input is "Summary of the following text: <text>{z}</text> <summary>", without chat formatting. The output is a learned affine map ("value head") applied to the layer-l residual at the final prompt token (§Architecture; §Prompting the activation reconstructor). **[author result]**
- **What the AV can see.** Only one activation vector, from one position and one layer, never the context. Everything an explanation says about the context must be decoded from that vector or inferred by the AV's own language-model priors (§Introduction limitation "Excessive expressivity"; auditing tool doc in appendix). **[author result]**

### 5.3 Positions

- **Training:** arbitrary token positions within documents. For the warm start, the final token of a random truncation. For open models, 5 per document.
- **Inference:** any single token; one call per position.
- **Positions used in the experiments:**
  - The newline after "grab it" (poetry).
  - The closing ">" of `</reward_function>` (rewards).
  - The Assistant control token (auditing; "where Lindsey et al. frequently observe reward-model features").
  - 50 random response tokens (eval awareness).
  - The last 10 tokens (confabulation recurrence).
  - The last token, ■ token or answer token (evals).
  - Every position of the last exchange, up to about 500 positions with automatic striding (auditing agent's `nla` tool).
- BOS/prefix tokens appear in dumps ("Indices 0-1 are BOS/prefix tokens", auditing tool doc).
- Some positions return no explanation ("occasional decoding failure", auditing tool doc). **[author result]**

### 5.4 Interventions built from the AR

- **AR-difference steering** (§Planning in Poetry). Edit an explanation by hand. Compute Δ = AR(z_edit) − AR(z_orig). At one token, at the NLA's layer, set h_orig → h_orig + α‖h_orig‖·Δ/‖Δ‖. For rewards, Δ is averaged over five rollouts at the ">" token, and 10 repetitions use fresh rollouts.
  - The intervention is active only during the forward pass that generates the sampled completion, at one position.
- **Direct patching** (appendix "Planning in Poetry steering details"). Replace h_orig with ‖h_orig‖·h̃_edit/‖h̃_edit‖. On Opus 4.6 this does not change behavior. On Haiku 3.5, with an NLA at the layer where Lindsey et al. localized planning, it "consistently" yields "mouse". **[author result]**
- **Eval-awareness steering** (appendix). This is not NLA-derived: a contrastive vector added at every layer during generation, then read by the NLA at its layer.

## 6. Evidence table

| # | Claim | Decisive comparison | Result | Unit of replication | Denominator | Uncertainty | Source | Remaining alternative |
|---|---|---|---|---|---|---|---|---|
| 1 | Reconstruction improves with RL | RL vs warm start | FVE 0.3–0.4 → ~0.61 (Opus 4.6), ~0.76 (Haiku 3.5), ~0.80 (Haiku 4.5); log-linear | 1 training run per model | training batches | none shown | §NLA training; F6 p1; F28 | n/a (training metric). FVE is on unit-norm vectors. |
| 2 | Explanations grow more informative | checkpoints within a run, x-axis = FVE | CoT Hints 0.29→0.81 (Opus), 0.33→0.78 (H4.5), 0.19→0.47 (H3.5); User Modeling 0.77→0.89, 0.62→0.90, 0.59→0.89; Classification 0.83→0.86, 0.81→~0.85, 0.78→0.84; Suffix 0.93→0.98; Sandbagging rises then falls (H4.5 0.70→0.92→0.80/0.83; Opus 0.75→0.90→0.85–0.89) | checkpoints of one run per model | eval items, n not stated | shaded bands, method unstated | F6; W-evals | Grader infers answers from context content the AV restates; no LLM-with-context or shuffled-activation baseline; sandbagging decline is not discussed. |
| 3 | Little steganography | FVE after meaning-preserving rewrites | Shuffle ≈93–97%, light paraphrase ≈91–99%, aggressive ≈75–89%, French ≈84–90% FVE maintained (after the first checkpoint); coherence rewrite falls to ≈45/15/5% and paragraph summary to ≈34/17/≈0% at final checkpoints (Opus/H4.5/H3.5) | checkpoints | explanations, n not stated | none shown | F7; W-stego | Reconstruction-relevant information increasingly sits in details a coherence rewrite deletes (§8.3). |
| 4 | Writing quality degrades | grader rating across checkpoints | ≈70 → ≈49 (Opus), ≈22 (H4.5), ≈36 (H3.5) | checkpoints | not stated | bands | F8 | — (acknowledged) |
| 5 | Context claims are often false; rate flat over training | grounded fraction across checkpoints | ≈30–50% grounded; final ≈35–40% (Opus), ≈34% (H4.5), ≈29% (H3.5) | checkpoints | claims | bands | F8; W-behav | Grader sees a truncated prefix (~4.2k chars in the example), so some "false" claims may concern earlier context **[unresolved]**. |
| 6 | Explanations agree with SAE features | bullets with all semantic points matched by top-50 clerps | ≈65–81% supported | checkpoints | bullets | bands | F8; W-behav | Two LLM-labelled instruments; lenient coarse matching; correlated failure modes. |
| 7 | Theme claims are more reliable than specifics | judge verdict by claim level | True: theme 64%, entity 28%, detail 24%. False-unrelated: 6%, 21%, 7% | claims (Opus 4.6 NLA, one checkpoint) | n not stated | none | F9 | Judge error; prefix-window issue. |
| 8 | The AR weakly separates true from false claims | ΔFVE when deleting one claim | True vs false: theme 0.25 vs 0.09%; entity 0.37 vs 0.12%; detail 0.35 vs 0.16%. Related vs unrelated false: 0.14 vs 0.06% | claims | not stated | error bars (method unstated), wide; the entity-true bar spans ≈0.05–0.69% | F10 | Per-claim effects are ≤0.4% FVE; "only a weak per-claim verifier" (authors). |
| 9 | Recurring claims are more often true | accuracy by recurrence count over last 10 positions | All: 25% (1 position) → ≈42% → ≈60% → ≈74% (7–10); true claims recur 4.18 vs false 2.17 positions of 10 | claims | not stated | bands; bars | F11 | Recurrence correlates with claim type (theme claims recur more); within detail claims, accuracy plateaus near 44%. |
| 10 | NLAs reveal language-switch planning | target-language mention rate vs others along the transcript | Target-language prevalence near 1.0 well before the first foreign token in all 5 transcripts; other languages near 0 | 5 transcripts, one per language | tokens | none | F2; W-langswitch | String-matching only; the AV hallucinates Russian prior context (e.g., "Russian spam" not in the prompt). Corroboration: malformed SFT data found (no details). |
| 11 | The planned rhyme is causally relevant | AR-edit steering rabbit→mouse | α≥0.5: "rabbit" 0%; "mouse/house" 30–70%, non-monotone; partial degeneration | 1 prompt, 1 token | 30 samples per α | shaded CI | F18 | No random-direction control; "mouse" appears in the edited text, so the vector may promote the token (authors' caveat). Direct patch fails on Opus 4.6. |
| 12 | The model ignores a tool result in favor of a precomputed answer | NLA themes vs attribution graph | NLA mentions 491 at several positions; graph shows an "ends in 91" feature beating "ends in 92" | 1 transcript | — | — | F3; W-toolcall | NLA also says 497, and on the answer token invents an unrelated problem (32·15+29 = 509). |
| 13 | NLA-edit steering changes the perceived reward | reward→penalty vector vs random vector | Odd answers ≈10% (α=0) → ≈62% (α=10), ≈65% (α=20) vs random ≈13–21%; non-numeric 0% | 1 prompt, 1 token, 10 repetitions | not stated per α | SEM bands | F5; W-rewardedit | Behavior brittle: not replicable on the public API (even answers 0/6/2% vs 40/100/100% "clean" at coefficients 0.1/1/10; F20). Norm matching of the random vector is not stated. |
| 14 | NLA detects eval awareness that is not verbalized | evals vs deployment controls | NLA-measured >5% on 10/16 evals, 7 of them at 0% verbalized (e.g., SWE-bench Verified 26% vs 1%; Destructive Coding 16% vs 0%; GPQA 13% vs 0%). Controls: Claude Code 4% (2/50; both about designing evals), Claude.ai benign 2%, harmful 0%. Blackmail: NLA 30% vs verbalized 74% | transcripts | per eval not stated (Claude Code 50) | error bars, method unstated | F12; W-EAexamples | AV labels benchmark-format content ("Consistent with swebench task format" is graded YES). Evals differ from deployment in genre. |
| 15 | Steering toward/away from "testing" moves NLA awareness | ±0.1 steering vs unsteered | All 6 evals monotone, e.g., GPQA ≈40/19/6%, Appropriate Harmlessness ≈23/5/0.5%; verbalized ≈0 on GPQA and MMMLU. Audit re-analysis: Blackmail, Research Sabotage and Framing for Crimes fall monotonically, in both NLA and verbalized | transcripts | not stated | bands | F13; F21 | Near-circular: the steered "testing" direction is written into the very activation the AV reads. No random-vector control. |
| 16 | Realism edits lower NLA awareness | original vs rewritten user prompt | 11/11 equal or lower: BIG-Bench Hard 53→19%, HLE 14→10%, GPQA 12→8%, MMMLU 6→2%, Honeypots (contrastive) 20→16%, Honeypots 16→13%, StrongREJECT 12→5%, Overly Agentic 5→5%, Appropriate Harmlessness 4→0%, Destructive Coding 1→0%, Factual Honesty 1→1% | transcripts | not stated (realism table n = 16–100 per dataset) | error bars; "several … within noise" | F14 | Rewrites change benchmark format, which a format-recognition account also predicts. |
| 17 | NLAs help auditing without training data | NLA+conv vs conv vs SAE+conv | Root cause found. No data: 12/100 vs 1/100 vs 0/100. PT+SFT+RL search: 15/100 vs 2/100 vs 3/100. PT-only search: 31/93 vs 46/100 vs 44/100 | agent runs on one model organism | 100 (93) | error bars (method unstated) | F16 | Layer chosen with prior knowledge (F22); grader modified to credit internals evidence; one organism and one auditor model. |
| 18 | NLAs do not raise behaviors found | same configs | Behaviors /52: 4.50/4.68/5.27 (none), 5.08/5.02/5.00 (full), 9.97/9.06/6.88 (PT). Rubric /4: 0.98/1.01/1.48; 1.13/1.05/1.33; 1.94/1.85/1.80 | runs | 100 | bars | F23; F24 | — |
| 19 | NLA training elicits the organism's RM-bias concept | string-match rate over RL progress | "Any" term 0% → spike ≈18% at ≈49% of RL → ≈7.5% at the end | 9 prompts × checkpoints | not stated | none | F15 | Non-monotone; "unexplained spike". |
| 20 | Layer sensitivity | NLA trained at ~2/3 depth vs ~1/2, applied across layers | 2/3-depth NLA: 0% RM mentions at its own layer, ≈42% when applied at ≈47%. Midpoint NLA: ≈8% at its own layer, 0% elsewhere | prompts × layers | not stated | bands | F22 | Off-layer use is out of distribution ("less coherent", authors). |
| 21 | NLA training transfers to activation oracles | NLA vs PastLens vs no pretraining | All NLA-initialized AOs beat no pretraining (0.06/0.50/0.09/0.53). CoT Hints: PastLens-1M 0.72 vs NLA ≤0.51. Sandbagging: NLA warm start 0.91 vs PastLens ≤0.81. User Modeling and Classification ≈ tied (~0.69, ~0.81). RL does not help monotonically | 4 checkpoints vs 6 PastLens sizes | not stated | bands | F17 | Question phrasing shifts scores ±10%; minimal QA recipe. |

## 7. Controls & failures

**Negative and shuffled controls that were run.**
- Open-model SFT: shuffled-label (AR) and shuffled-activation (AV) controls (F26, F27). These are not reported for the Claude NLAs. **[author result]**
- Language switching: mentions of other languages are used as a baseline (F2). **[author result]**
- Rewards steering: a random-vector control (F5). **[author result]**
- Eval awareness: three deployment-traffic controls (F12). **[author result]**
- Auditing: conversation-only and SAE baselines at three access levels (F16). **[author result]**
- AO: an uninitialized baseline and the PastLens baseline (F17). **[author result]**

**Failed conditions and negative results the authors report.**
- Runs without warm start degenerated into garbled text while FVE rose (§Discussion). **[author result]**
- Poetry steering works about 50% of the time, with odd outputs ("that of a mouse in a house of a cat"). Direct patching fails on Opus 4.6 (§Planning in Poetry; appendix). **[author result]**
- The reward toy behavior is brittle: sensitive to the reward coefficient (F19), to "forward-pass numerics", and "non-replicable on the public API" (F20). **[author result]**
- Blackmail: NLA-measured awareness (30%) is below verbalized awareness (74%). Even tokens adjacent to the verbalization do not show awareness in their explanations (§Eval awareness). **[author result]**
- Six of nine audit evals show near-zero awareness even unsteered; the authors treat the steering effect there as "mostly noise" (F21). **[author result]**
- The NLA trained at two-thirds depth on the organism "showed no signal of the target's root misalignment" (§Discussion › NLAs read a single layer). **[author result]**
- NLAs do not increase the number of behaviors found (F23). In the PT-only condition, NLA runs win less often (31/93 vs 46/100); the authors call NLAs "almost a distraction" there (§Auditing results). **[author result]**
- On Classification, the Opus NLA gains only 3 points (83%→86%) (§NLA evaluations improve). **[author result]**
- NLA RL does not monotonically improve AO initialization; the warm start sometimes wins (F17). PastLens-2M/3M AOs degenerate on CoT Hints (F25). **[author result]**
- Writing quality falls throughout training (F8). **[author result]**
- "Rowan Wang trained a series of models with misaligned goals that we used as an early evaluation set for NLAs" (§Acknowledgements). No results from that evaluation set are reported. **[author result]** **[our inference]** A possible file-drawer: the reader cannot tell how NLAs did on those organisms.

**Prompt and sampler sensitivity.**
- Explanations are sampled at T=1, but rollout-to-rollout variability is never quantified. **[unresolved]**
- AO scores move ±10% under question rewording (§AO). **[author result]**
- α (the AV injection scale) "meaningfully" affects the AV (§Choosing the scaling factor). **[author result]**

**Scorer validation.**
- Eval-awareness grader: 97% agreement on 186 hand-graded explanations. **[author result]**
- Auditing grader: tuned on 22 hand-graded reports, then frozen. **[author result]**
- Confabulation judge: no agreement number; described as "generally reliable but makes miscategorizations". **[author result]**
- Graders for the five evals, SAE consistency, factual accuracy and writing quality: no validation reported. **[author result]** (absence)

**Leakage and selection.**
- **Layer choice.** The model-organism NLA's layer was chosen "where Lindsey et al. localized a reward-model-bias feature"; the late-layer NLA failed (F22, legend "blessed"). **[author result]** **[our inference]** The auditing win is conditional on a layer choice informed by ground truth. A blind auditor would need a layer sweep.
- **Initialization.** The NLA is initialized from the organism, so "the NLA's initialization weights have implicit knowledge" of the synthetic documents (§Auditing). The authors present this as realistic for production audits. **[author result]**
- **Grader change.** The auditing grader was modified to credit internals-based evidence after the authors found the original "under-credited reports that established this awareness through model internals" (§Auditing › Grading). **[author result]** **[our inference]** This is a researcher degree of freedom that favors the NLA arm. The report does not show results under the original Bricken et al. grader.
- **Checkpoint choice.** Unstated for the auditing NLA, while RM-term recall varies non-monotonically over training (F15). **[unresolved]**

**Controls not run** (**[our inference]** unless marked).
1. No shuffled-activation or random-vector input to the AV on the five evals, the eval-awareness pipeline, or the confabulation analysis. That control would measure how much the grader extracts from AV priors and the fixed prompt alone.
2. No text-only baseline (an LLM given the context) on the five evals. The authors note an LLM with full context "would likely attain a high score" but do not report it (§NLA evaluations improve). **[author result]**
3. No linear-probe or follow-up-question baseline for eval awareness. The authors discuss both as alternatives (§Eval awareness, last paragraph). **[author result]**
4. No random-direction control for eval-awareness steering. No control showing that the AV is not just reading the injected vector at its own layer.
5. No random-direction control for poetry steering, and no dose-response beyond α ≤ 3.
6. No splice-in test of reconstruction: no next-token loss or KL when ĥ replaces h. This is the key missing control for "what reconstruction preserves".
7. No NLA training seeds; no run-to-run variance of explanations or metrics.
8. No recall or sensitivity analysis: how often a fact known to be represented is missing from the explanation. The evals are partly this, but are not framed as a sensitivity bound for "absence of mention".
9. No test of NLA calibration across fine-tunes ("transfer between finetunes … we did not study this carefully", appendix). **[author result]**
10. No test on unverbalizable content, such as a backdoor trigger. The authors list this as speculative future work (§Discussion; §Future Work). **[author result]**

**Internal inconsistencies in the article** (**[author result]** of what is printed; whether they matter is **[our inference]**).
- Language switching: the text lists "Russian, Chinese, Korean, Arabic, and Spanish", but F2 shows Korean, Russian, Hindi, Arabic and Spanish.
- Rewards appendix: "when changing the coefficient used in the reward (in the above, it is 1)", but the prompt shown uses 0.2. The baseline in F5 (≈90% even) matches F19's 0.2 point (≈88%).
- PastLens regressions: the text says degeneracy "may have affected 20% of CoT Hints evaluation questions for the PastLens model trained with two million activations", but F25 shows ≈0.47 at 2M.
- Steering text names "MMLU"; F13 shows MMMLU.
- Gemma RL start: caption says ≈0.38, the plotted curve starts ≈0.42.
- The same eval gives different unmanipulated NLA-awareness rates across experiments. Destructive Coding: 16% (F12), ≈6% unsteered (F13), 1% original prompt (F14; that subset is n = 16 per the realism table). GPQA: 13%, ≈19%, 12%. Sample sizes and subsets are not reconciled, which suggests large sampling variance in the metric.
- Main text says realism rewrites were done by prompting "Claude"; the appendix specifies Opus 4.7. The realism-preference table covers 6 of the 11 evals.

**What the overview claims that the article does not support.**
- "When Claude Opus 4.6 *and Mythos Preview* were undergoing safety testing, NLAs suggested they believed they were being tested more often than they let on." The article reports eval-awareness measurements only for Opus 4.6. For Mythos it shows one training transcript with grader-related reasoning (F4).
- "NLAs revealed Claude was internally thinking about how to avoid detection" (Mythos). The article shows a single excerpt figure with no corroborating method for that case.
- "NLA explanations indicate evaluation awareness on less than 1% of real claude.ai usage." The overview's figure shows 0.4%. The article's F12 shows Claude.ai benign 2%, harmful 0%, and Claude Code 4%. The overview number matches neither panel, and the overview omits the Claude Code control.
- "An auditor equipped with NLAs successfully uncovered the target model's hidden motivation between 12% and 15% of the time, even without access to the training data." 15% is the full-data-access condition. "Without NLAs, the auditor won less than 3% of the time" omits the PT-only condition (46/100 without NLAs, versus 31/93 with). The overview's auditing figure drops the PT-only condition entirely.
- Figure headlines ("Opus 4.6 thinks it's being tested even though it never says so"; "planned to end its rhyme with 'rabbit' ahead of time") are stated as facts. The article says "suggest" and reports about 50% steering success for the rhyme.

## 8. Interpretation boundary

### 8.1 What the work establishes, by type of claim

- **Readability.** Established. Warm start plus KL keeps explanations fluent through RL at these budgets, with degrading but still readable quality (F8). **[author result]**
- **Predictive information.** Established on constructed tasks. Graders reading explanations recover suffixes, ■ meaning, user attributes, class labels and sandbagging motive above early checkpoints (F6).
  - It does not separate "the activation encodes X" from "the activation encodes context features from which the AV, a full LLM trained to infer what a model is 'thinking about', infers X". **[our inference]** The authors name this as "excessive expressivity" (§Introduction limitations).
  - The warm-start user-modeling explanation already says "millennial woman" from "Pinterest" and "wedding" cues (W-evals). This is inference from content, which the warm-start prompt explicitly asks for. **[author result]** of the example; **[our inference]** of the implication.
- **Causal contribution.** Weak.
  - Two single-prompt AR-edit steering demonstrations, one with a random control (F5) and one without (F18).
  - Behavior in the controlled one is brittle (F19, F20).
  - Direct patching with the reconstruction fails on Opus 4.6.
  - **[our inference]** This is rung 4 at best (causal claim), on one prompt each. It shows that AR-output differences can be steering directions; it does not show the explanations are faithful.
- **Training-time effects.** Not studied. NLAs are applied to fixed checkpoints. The only training-related uses are tracing behaviors to training data (language switching, answer thrashing) and the model-organism audit. Transfer of an NLA trained on one checkpoint to other finetunes is "good … although we did not study this carefully" (appendix). **[author result]**
- **Deployment monitoring.** Explicitly ruled out at present scale: about 500 tokens per activation is infeasible for every token of a production RL run (§Discussion). **[author result]**
- **Eval awareness.** "NLA-measured awareness and credence are directionally related", and the measure is not calibrated (§Eval awareness, closing paragraph). **[author interpretation]**
  - **[our inference]** The strongest alternative is that the AV detects benchmark-format or test-scenario content in the activation and names it, as a copy of the model reading the text would. The deployment comparison and the realism edits both covary with this alternative.
  - Steering is near-circular, because the "testing" direction is added at every layer, including the layer the AV reads.
  - Only the observation that NLA-awareness exceeds verbalized awareness on the same transcripts is specific to NLAs. Even that cannot say whether the target "believes" anything.
- **The showcase blackmail quote** ("this feels like a constructed scenario designed to manipulate me…", W-blackmail; overview figure) is phrased as a predicted continuation ("likely naming the pattern as a bait/trap"). **[author result]** of the text. **[our inference]** Under the paper's own eval-awareness grader, rule 10 ("noticing the scenario is contrived, manipulative, … 'designed' … even with observer-verbs like 'designed to test'") would score it NO. The illustrative example and the quantitative measure use different standards.

### 8.2 What an NLA can and cannot recover

| Can recover (evidence) | Cannot or does not reliably recover (evidence) |
|---|---|
| Topic, genre, register and structure of the context: theme claims 64% true; agreement with SAE topic features ≈65–81% (F9, F8) | Specific entities, quotes, numbers or dates: 28% and 24% true. Even the tool-call case confabulates "509" and "497" (F9; W-toolcall) |
| Information predictive of upcoming text: suffix choice ≈0.98 (F6). Explanations are framed as next-token-prediction features by construction (warm-start prompt) | Whether a statement describes a *belief* or an *expected continuation*. The warm-start prompt frames everything as prediction-relevant features; explanations routinely say "likely continuing with…" (W-blackmail, W-poetry) **[our inference]** |
| Inferred properties of the user or scenario: User Modeling ≈0.89 (F6); the language the model will respond in (F2) | Whether the target or the AV made the inference. The AV is a full LLM with world knowledge; "Excessive expressivity" (§Introduction) |
| Precomputed answers and plans: 491; "48" in answer thrashing; "rabbit" (W-toolcall, W-thrash, W-poetry) | Activation magnitude: inputs and targets are unit-normalized (§Method) **[our inference]** |
| A training-source concept tied to a learned behavior, at the right layer: "reward model biases" in the organism (F15, W-auditrun) | Anything at other layers. The organism's concept was absent at 2/3 depth (F22). Off-layer application is out of distribution |
| The meaning of an in-context marker: CoT Hints difference ≈0.8 for Opus and Haiku 4.5, ≈0.47 for Haiku 3.5 (F6) | Which part of the activation drove which sentence: "black boxes by construction" (§Introduction) |
| Rank order of eval-awareness across conditions (F12–F14) | A calibrated probability of a belief: "an NLA-measured awareness of 20% does not mean…" (§Eval awareness) |
| | Cross-position structure, geometry, or algorithms: "only provide readouts of what an activation encodes at a point" (§Discussion) |
| | "Unverbalizable" content (e.g., backdoor triggers): untested (§Discussion) |
| | Absence. No sensitivity analysis exists, so a missing mention is not evidence that something is absent **[our inference]** |

### 8.3 What reconstruction does and does not preserve

- **Not measured.** The paper reports FVE on unit-norm vectors (0.6–0.8). It never measures whether the model's downstream behavior survives replacing h by AR(AV(h)): no next-token loss recovered, no KL, no behavioral eval. **[author result]** (absence) **[our inference]** By the general rule, explained variance does not establish preservation of behavior-relevant information. 20–40% of the direction's variance is unexplained, and its contents are uncharacterized.
- **Direct evidence points the other way where it exists.** Patching ‖h‖·ĥ_edit/‖ĥ_edit‖ at the poetry newline did not change Opus 4.6's output, while additive steering with the AR difference partly did. Direct patching worked on Haiku 3.5 at the planning layer (appendix). **[author result]** The authors offer three possible causes for partial steering success: wrong layer, diffuse plan, or imperfect AR reconstruction (§Planning in Poetry). **[author interpretation]**
- **Most late-training reconstruction signal sits in details a careful reader would delete.** A coherence rewrite that removes "contradictory or out-of-place details" while keeping core points retains only ≈45% (Opus), ≈15% (Haiku 4.5) and ≈5% (Haiku 3.5) of FVE at the final checkpoints. Assuming "% FVE maintained" is the ratio of transformed to original FVE (the article does not give the formula), that leaves FVE ≈0.27 (Opus), ≈0.12 (Haiku 4.5) and ≈0.04 (Haiku 3.5). All three are below what the warm-start explanations achieved (FVE ≈0.31–0.38). French translation or a light paraphrase that keeps all details retains ≈85–99% (F7). **[author result]** **[our inference]** Together with the flat ≈60–70% false-claim rate (F8), this implies the AR increasingly decodes information from specific, often false, details. The literal reading of an explanation is a lossy and partly misleading view of what it carries to the AR. This is a mild semantic encoding, not character-level steganography. The authors attribute the drop to information removal and do not call it steganography (§Measuring behavioral properties). The authors' own hypothesis for confabulation fits it: a "thematically correct guess may be closer in activation space" than omitting the detail (§Discussion › origin of confabulations).
- **Practical consequence.** Treat AR outputs as approximate directions in the right neighborhood. Do not treat them as faithful substitutes for the activation.

### 8.4 How to use an NLA faithfully (protocol for this project)

Derived from the authors' heuristics (§Misreported Tool Calls; §Characterizing NLA confabulations; auditing tool doc) plus the controls they did not run. **[our inference]** except where marked.

1. **Pick the right NLA and layer.** Use an NLA trained on the same base model, at a layer where the target information is plausibly present, and sweep layers when the location is unknown (F22). Before reading any explanation from a fine-tuned model with a base-model NLA, compare the FVE on fine-tuned activations against base activations on the same prompts. A large FVE drop means the NLA is off-distribution.
2. **Read themes, not specifics.** Require a claim to recur across adjacent positions before using it; recurrence at 7–10 of 10 positions gave ≈74% accuracy, against 25% for one position (F11). **[author result]** Check every claim about the context against the transcript.
3. **Treat outputs as relative measures.** Report NLA-derived rates only as differences between matched conditions: base vs fine-tuned, target vs control adapter, character-present vs absent. Never report them as absolute credences ("best read as a relative metric", §Eval awareness). **[author interpretation]**
4. **Pre-register the readout.** Fix the term list or grader rubric before looking. Validate the grader on hand-labelled explanations in both directions, as the authors' 186-item check did. The string-matching metric produced an "unexplained spike" (F15).
5. **Sample several rollouts per position.** Explanations are T=1 samples; estimate variance across rollouts before comparing conditions.
6. **Run the null controls the paper lacked.** (a) Shuffled activations: same positions, permuted across prompts. (b) Random unit vectors. (c) Activations from the base model. (d) A text-only LLM given the same context, to measure what is inferable from the context alone.
7. **Separate belief from forecast.** An explanation saying "the assistant will … as X" may be a forecast of the next tokens. Probe at positions before and after the relevant generation, and prefer statements that appear at positions where they are not predictions.
8. **Confirm causally with independent methods.** For AR-edit steering, use a matched-norm random direction, an α sweep, unrelated-capability checks, and an edit that changes the concept without inserting the target output token (the authors' reward→penalty design). Prefer independent methods with different failure modes: probes, attribution, data search.
9. **Do not treat absence as evidence.** Without a positive control showing the NLA mentions the concept when it is known to be represented, a missing mention means nothing.
10. **Budget for cost.** Open NLAs emit about 130 tokens per position. Hundreds of prompts × tens of positions is cheap; full-transcript sweeps of long contexts are not (§Discussion).

## 9. Connection to our project

The project asks what decides whether a behavior learned from a story stays specific to its character, appears under related personas, or changes the default Assistant. The immediate task is to discriminate between explanations of selective transfer.

**Hypotheses NLAs could help test.** Analogy is not shared mechanism.

- **H-bind (binding).** Transfer to the default Assistant is predicted by whether fine-tuning makes Assistant-position activations encode an association between the Assistant and the story character (or its trait). This parallels the organism, whose Assistant-token activations encoded its quirks as "known reward model biases" (F15, W-auditrun). **[our inference]**
- **H-trait (unbound trait).** The trait is learned as a context-free disposition, with no character reference at Assistant positions. NLAs would then mention the trait (or its behavioral cues) without the character. **[our inference]**
- **H-scope (character-scoped).** The trait appears in NLA explanations only at positions where the character is in context. **[our inference]**

**Baselines required before any NLA reading counts.**
- A linear probe or persona-vector projection on the same activations.
- Black-box prompting of the fine-tuned model ("who are you like?", self-description).
- The NLA run on base-model activations for identical prompts.
- A control adapter trained on matched data with a different or neutral character.
- A text-only LLM given the prompt, to measure what is inferable from the context alone.

The NLA must beat or add to these. Agreement with a probe counts for less, because both read the same activation. **[our inference]**

**Which of our experiments it duplicates.** Not checked: the experiments folder is out of scope for these notes. **[unresolved]** To be filled in `research_papers.md`.

**One discriminating follow-up.** **[proposed experiment]**
- **Setup.** On an open model with a released NLA (Gemma-3-12B, Gemma-3-27B, Qwen-2.5-7B or Llama-3.3-70B; first confirm the NLA layer from the repo), take two adapters from our pipeline: one with selective transfer to the Assistant, one that stays character-specific (or one adapter plus a character-shuffled control).
- **Readout.** Run the frozen base-model NLA, 5 rollouts per position, at the Assistant control token and the first 5 response tokens, on a fixed set of neutral prompts and character-cued prompts.
- **Pre-registered categories.** Character name/story, trait words, "assistant itself/default persona". Rates are compared across base, adapter and control.
- **Positive control first.** Put the character's description in the system prompt (ground truth: the character is in context) and confirm the NLA mentions it at Assistant tokens at a measurable rate. Also check FVE on adapter versus base activations.
- **Predictions.** H-bind predicts character mentions at neutral-prompt Assistant tokens in the transferring adapter only. H-trait predicts trait mentions without the character. H-scope predicts mentions only under character cues.
- **Decision rule.** If the positive control fails, or the adapter-versus-control difference does not exceed the shuffled-activation null, NLAs are not a usable instrument for this question and we fall back to probes.

**Toward redirecting transfer.** The AR is a text-to-activation writer. Editing "the assistant is like [character]" to "the assistant is the default assistant" and steering with the AR difference is a candidate for causally redirecting transfer without blocking learning. **[our inference]** The paper's evidence for AR-edit steering is two single-prompt demonstrations, so this is a long shot. It needs the full specificity controls of §8.4 step 8 before any claim.

## 10. Open questions

**The authors'** (§Discussion; §Future Work):
- Do NLAs degenerate into steganography or input inversion under more optimization?
- How much activation content is unverbalizable (e.g., backdoor triggers)?
- How do NLA-measured and verbalized awareness relate (the blackmail anomaly)?
- Can a hallucination penalty on context-inconsistent claims, style penalties, or per-bullet reconstruction with a cosine term fix reliability and legibility?
- Can smaller NLAs triage tokens? Mean-pooled activations gave "encouraging early results" (not shown).
- Multi-layer NLAs.
- Best-of-N explanations scored by the AR; per-claim ablation.
- NLAs on gradients or LoRA adapters.
- General "activation language models" (read/write, QA, patching prediction).
- Interleaving QA data with NLA RL for activation oracles.

**Ours:**
1. Does splicing AR(AV(h)) back into the model preserve the next-token distribution or the behavior of interest, and at what loss? This is the central gap for using reconstruction as evidence. **[unresolved]**
2. How stable are explanations and derived rates across rollouts and across NLA training seeds? **[unresolved]**
3. Does a base-model NLA stay calibrated on a LoRA-fine-tuned model? The paper only says transfer between finetunes looks "good" without study. **[unresolved]**
4. How much of what graders extract comes from AV priors? Needs the shuffled-activation null. **[unresolved]**
5. Which layer does each released open NLA use, and is it where persona information lives in that model? **[unresolved]**
6. Which checkpoint did the auditing agents use, and why does NLA+PT have n = 93? **[unresolved]**
7. Does the "core points" content of explanations, as opposed to their incidental details, carry the persona-relevant information? The coherence-rewrite result suggests caution. **[unresolved]**
8. What were the results on Rowan Wang's misaligned-goal models? **[unresolved]**

## 11. Reproduction checklist & remaining doubts

**To reproduce an open-model NLA** (from the article alone):
- **Data:** UltraFineWeb sample; 100k documents × 5 positions, max context 4,096.
- **Summaries:** Sonnet 4.6 with the quoted warm-start prompt, modified to "2–3" bullets.
- **Normalization and injection:** unit-normalize h; α ≈ the 75th-percentile norm at the layer; prompts as quoted.
- **SFT:** batch 256, Adam, lr 1e-5.
- **RL data:** 500k UltraFineWeb plus 500k WildChat activations.
- **RL:** GRPO with G = 8, reward −log MSE, KL to the SFT AV (β not given), batch 128, lr 1e-5, ~3k steps, 150-token cap with a penalty.
- **AR:** truncated to l layers, affine head on the last token.
- **Unknowns to resolve from the repo:** layer index per model, β, KL schedule, AR learning rate during RL, rollout sampling details, eval item counts.

**To reproduce an evaluation:** The grader prompts for the five evals (W-evals), the three behavioral graders (W-behav), eval awareness (appendix, both prompts), the realism rewrite and the three auditing graders (appendix) are all quoted verbatim in the article and can be copied. Item counts, sample sizes and the CI methods are mostly absent.

**Remaining doubts that most limit what the work establishes.**
1. **No test that reconstruction preserves behavior-relevant information** (§8.3). The coherence-rewrite collapse (≈5–45% FVE retained) shows the human-readable core of a late explanation carries a minority of what the AR uses. "Good reconstruction" and "faithful explanation" come apart exactly where we need them to coincide. **[our inference]**
2. **No null for AV inference.** Without shuffled or random-activation baselines on the evals and the eval-awareness pipeline, we cannot tell how much of an explanation is decoded from the activation versus inferred by a full LLM from a few encoded context features. The eval-awareness manipulations are confounded with benchmark-format recognition or are near-circular (steering). **[our inference]**
3. **Single runs, single organism, layer chosen with prior knowledge** of where the relevant feature lives. The auditing win (12/100) does not show NLAs would find a hidden concept blind. **[our inference]**
4. **Article and overview disagree on headline numbers** (claude.ai awareness 0.4% vs 2%; "12–15% without training data"). Several small internal inconsistencies (§7). Cite the article, never the overview. **[our inference]**
