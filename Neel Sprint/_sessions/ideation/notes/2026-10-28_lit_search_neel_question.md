# Literature search: why the default Assistant shows the helpful habit (Neel's question)

_28 Oct 2026, ideation subagent. Web search for 2024–2026 work on five questions. Excludes the 31 works in `papers/README.md`. Every item below had at least its abstract page opened. Where a detail comes only from a search snippet, or from a page I could not read in full, it is marked. Nothing here has been read in full; these are leads, not notes._

**What the search turned up, in brief.**
- Neel's method has direct precedent. Kissane et al. regressed a refusal direction onto SAE decoder vectors. Rajaram et al. fitted sparse combinations of decoder columns, with a random-vector baseline.
- Its known pitfalls are documented. Coefficients must be signed (Mayne et al.). The SAE's training data decides whether a concept appears as one latent or fragments into many (Kissane et al.).
- The best rival to Neel's "if-then rule" account is Wang et al. (2025). They find that LoRA updates often act as one **constant** steering vector, and that even backdoor-like conditional behaviour can come from an unconditional vector. Applied to our organism: the trained update may be an unconditional push, and the parent's existing persona computation may be what makes it look conditional. This is testable cheaply.
- A practical point for the method: the only Qwen3.6-27B SAEs I found are third-party (L11/L31/L55), trained on web, reasoning and math text with no chat data (see the end of §1).

---

## 1. Decomposing steering, difference or model-diff vectors into SAE features (decoder regression vs encoder)

**1. Can sparse autoencoders be used to decompose and interpret steering vectors?**
- Mayne, Yang, Mahdi. 2024, NeurIPS 2024 workshop. https://arxiv.org/abs/2411.08790 (this is the arXiv ID you asked about).
- **What they did:** decomposed CAA corrigibility steering vectors (Gemma-2-2B-IT, L14) with the Gemma Scope SAE encoder. They show two failures:
  - **Out of distribution.** Steering vectors have small norms, so the encoder bias dominates. A zero vector gives nearly the same top latents as the steering vector.
  - **No negative coefficients.** 51.2% of the active latents fire more on the negative prompts. Because latents can be anti-aligned (cos −0.82 in one example), a true negative coefficient can show up as a spurious positive one on another latent.
- **Alternatives they name:** gradient pursuit, sparse task-vector fine-tuning, and (proposed, untested) encoding the positive and negative activations separately and then subtracting.
- **Why it matters for us:** it is the case for Neel's choice of regressing onto the decoder rather than encoding. The regression must allow **signed** coefficients. Check whether the top latents survive replacing the vector with zero or a random vector. Inspect anti-aligned decoder pairs before reading a positive coefficient as a feature being "present".
- opened: yes (abstract and HTML sections).

**2. SAEs are highly dataset dependent: a case study on the refusal direction**
- Kissane, Krzyzanowski, Nanda, Conmy. Nov 2024, Alignment Forum. https://www.alignmentforum.org/posts/rtp6n7Z23uJpEH7od/
- **What they did:** trained SAEs on Qwen1.5-0.5B-Chat with either Pile or LmSys-Chat data. They then reconstructed the refusal direction, **regressed it onto the top-k decoder vectors**, and ablated single latents.
  - The chat-data SAE represents refusal with about 1 latent; the Pile SAE needs more than 32 latents to match it.
  - A base-model SAE trained on chat data beats a chat-model SAE trained on Pile data.
- **Why it matters for us:** this is Neel's method applied to a known direction. It warns that the sparsity of the decomposition depends on the SAE's training data. An SAE trained without chat data may split "Assistant-ness" across many latents, making the regression look dense for reasons unrelated to the model.
  - Positive control to copy: decompose a known direction (e.g. the parent's refusal direction, or our validated story_dismissive direction) before decomposing the Assistant Axis.
- opened: yes.

**3. Line of Sight: On Linear Representations in VLLMs** (§3.5 "Sparse Approximation of Steering Vectors")
- Rajaram, Schwettmann, Andreas, Conmy. 2025. https://arxiv.org/abs/2506.04706
- **What they did:** used the SAE **decoder matrix as a dictionary**. They fitted sparse coefficients with a HardConcrete (relaxed-L0) penalty plus a cosine reconstruction loss, and read the L0 as "the extent to which the vector lies within the dictionary".
  - Steering vectors need far fewer latents than **random vectors**.
  - 20-latent approximations steer about as well as the dense vector.
- **Why it matters for us:** the closest published version of Neel's proposal. It also supplies a control we need: the L0 and fit at matched sparsity for norm-matched random vectors and for random persona-difference vectors. Without that baseline, "the Axis decomposes into helpfulness latents" has no null.
  - It also offers a steering test of the approximation: does the k-latent reconstruction reproduce the vector's behavioural effect?
- opened: yes (abstract and §3.5 via HTML).

**4. Scaling sparse feature circuit finding for in-context learning**
- Kharlapenko, Shabalin, Barez, Conmy, Nanda. 2025, ICML 2025. https://arxiv.org/abs/2504.13756
- Earlier post: "Extracting SAE task features for in-context learning", Aug 2024, LessWrong `5FGXmJ3wqgGRcbyH7`.
- **What they did:** decomposed ICL task vectors into SAE latents. The method details come from search snippets of the post, not from a page I opened:
  - plain encoder reconstruction degrades the task vector;
  - their method instead optimises the coefficients from the encoder initialisation under an L1 penalty, with the task-vector **behaviour** as the objective;
  - this reduces about 100 active latents to about 8–15 that work as well.
- **Why it matters for us:** a third variant beside "encode" and "regress to reconstruct": sparse coefficients fitted to **reproduce the behaviour** (e.g. the routing log-odds) rather than the vector. That separates latents that lie along the vector from latents that do the work.
- opened: yes (arXiv abstract; the post's details from search snippets only).

**5. Progress Update #1 from the GDM Mech Interp Team (steering-vector section)**
- Conmy, Nanda. Apr 2024, LessWrong `C5KAZQib3bzzpeyrg`.
- **What they did:** passed GPT-2-XL steering vectors through an SAE (encoder).
  - Anger: a single latent Pareto-dominates the original vector.
  - Wedding: hand-picked latents were much worse, and some latents active on the negative prompt were needed. The SAE was poor (most latents dead).
- **Why it matters for us:** an early record of the negative-prompt and feature-splitting problems.
- opened: yes.

**6. Improving Steering Vectors by Targeting Sparse Autoencoder Features (SAE-TS)**
- Chalnev, Siu, Conmy. 2024. https://arxiv.org/abs/2411.02193
- **What they did:** used the SAE as a **measurement** of what a steering vector does downstream, and optimised vectors to hit target latents with few side effects.
- **Why it matters for us:** the complementary use. Instead of decomposing the Axis, measure which latents move when we steer along it, or when a dismissive history is supplied. This sidesteps the out-of-distribution problem because the SAE only sees ordinary activations.
- opened: yes (abstract).

**SAE availability for our model** (checked because the method depends on it). These are not literature items.
- **"Qwen3.6-27B Paper-Grade Sparse Autoencoders"** (third party, caiovicentino1 / OpenInterpretability, 2026-04-24). https://huggingface.co/caiovicentino1/qwen36-27b-sae-papergrade
  - TopK SAEs, d_sae 65,536, k 128, at L11, L31 and L55. Base vs instruct revision is not stated.
  - Trained on 200M tokens of FineWeb-Edu, OpenThoughts and OpenMathInstruct, with **no chat data**.
  - Variance explained 0.71 at L31; loss recovered 0.994.
  - Under item 2's warning, Assistant and template concepts may be poorly represented. Validate on a known direction first.
- **Qwen-Scope** (Deng et al., 2026; https://arxiv.org/abs/2605.11887) is official. A blog lists Qwen3.5-27B-Instruct but no Qwen3.6 model; the arXiv abstract does not list the models.
- opened: yes (HF page, arXiv abstract, blog).

## 2. Why character or persona data transfers to the default Assistant; conditional (gated) behaviours

**7. Simple Mechanistic Explanations for Out-Of-Context Reasoning**
- Wang, Engels, Clive-Griffin, Rajamanoharan, Nanda. 2025, ICML 2025 workshop. https://arxiv.org/abs/2507.08218
- **What they did:** showed that in many OOCR settings the LoRA update acts as a **constant steering vector** toward a general concept. Steering vectors trained from scratch reproduce the OOCR. **Backdoor tasks that seem to need conditional behaviour are reproduced by an unconditional vector.**
- **Why it matters for us:** this is the main alternative to Neel's "learned if-then rule". Our routing (helpful → bee, dismissive → crow) could be an unconditional push toward "story-character animal habit", with the parent's existing persona computation choosing which animal.
  - Cheap test: train a single steering vector (one layer, then a band) on the stories, or take the mean LoRA output delta. Check whether it reproduces persona-dependent routing on the parent.
    - If it does, the "rule" lives in the parent and the update is unconditional.
    - If only the full LoRA routes, the update itself is conditional.
- opened: yes.

**8. Conditionalization Confounds Inoculation Prompting Results**
- Riché, Warncke (nielsrolf). 3 Feb 2026, LessWrong `znW7FmyF2HX9x29rA`.
- **What they did:** across 7 replicated setups, showed that fixed training-time patterns, even irrelevant system prompts or delimiters, make traits conditional on those patterns. Fixed prompts suppress both positive and negative traits; rephrased prompts partly undo this. One seed per point.
- **Why it matters for us:** our stories share a fixed rendering (assistant-turn chat, fixed user templates). Some of "the default shows the helpful habit" could be conditional on template features rather than on helpfulness. It also names controls to copy: an irrelevant-prefix baseline, and matching the train-to-eval shift across conditions.
- opened: yes.

**9. Tell me about yourself: LLMs are aware of their learned behaviors** (§5.1, Fig 15)
- Betley, Bao, Soto, Sztyber-Betley, Chua, Evans. 2025, ICLR 2025. https://arxiv.org/abs/2501.11120
- **What they did:** trained the default persona ("you") on risk-seeking choices. It carried over, more weakly, to third-person personas ("my friend Lucy is pretty risk-seeking"). Adding demonstrations for six other personas "solves the unintended transfer between personas almost completely".
- **Why it matters for us:** the reverse direction of our effect (default → others), with a clean fix: contrast data for other personas. A design lever (add dismissive-persona chat demonstrations) and evidence that persona entanglement is the default outcome.
- opened: yes (abstract and §5.1 via HTML).

**10. Training on Documents About Reward Hacking Induces Reward Hacking**
- Hu, Wright, Denison, Marks, Treutlein, Uesato, Hubinger. 2025, Anthropic Alignment Science Blog. https://alignment.anthropic.com/2025/reward-hacking-ooc/
- **What they did:** trained pretrained models on synthetic third-person documents saying "Claude" does or never does reward hacking, with no demonstrations. Behaviour shifted both ways after formatting RL; smaller effects survived SL and HHH RL. There was no neutral-document control, and the Pro set was larger.
- **Why it matters for us:** the closest analogue of "descriptions of a character change the Assistant". It binds through the name "Claude", whereas our stories bind through resemblance. A test it suggests for us: does naming an Assistant-like character change transfer?
- opened: yes (the page gives no date).

**11. Alignment Pretraining: AI Discourse Causes Self-Fulfilling (Mis)alignment**
- Tice, Radmard, Ratnam, Kim, Africa, O'Brien. 2026. https://arxiv.org/abs/2601.10160
- **What they did:** pretrained 6.9B models with upsampled synthetic documents about misaligned or aligned AI. Misalignment went 45% → 9% with aligned discourse; the effects are dampened by post-training but persist.
- **Why it matters for us:** shows that third-person AI-character text reaches the post-trained Assistant at pretraining scale. Supports treating "AI-assistant-like character" as the binding variable, though nothing here is mechanistic.
- opened: yes (abstract).

**12. Synthetic Persona Pretraining: Alignment from Token Zero**
- Minder et al. (15 authors). Aug 2026. https://arxiv.org/abs/2608.13482
- **What they did:** inserted first-person value reflections into pretraining data, then ran "**persona binding**" post-training to link that persona to the Assistant identity. The benefit **depends on persona binding**.
- **Why it matters for us:** frames transfer as a binding step between a learned persona and the Assistant identity, which suggests asking what in our stories does the binding. Mostly framing; models are ≤3B.
- opened: yes (abstract).

_Also opened, lower priority:_ Weckauff, Zhang, Andriushchenko, "Characterizing the Consistency of the Emergent Misalignment Persona" (2026, https://arxiv.org/abs/2604.28082). In Qwen2.5-32B, some EM organisms are "inverted": harmful outputs while describing themselves as aligned. This is a caution against assuming behaviour and self-concept move together, relevant to our X9 null. opened: yes.

## 3. Predicting which training data shifts default behaviour (attribution)

**13. Concept Influence: Leveraging Interpretability to Improve Performance and Efficiency in Training Data Attribution**
- Kowal, Paulo, Jaburi, Tseng, McKinney, Heimersheim, Tucker, Gleave, Pelrine. 2026. https://arxiv.org/abs/2602.14869
- **What they did:** attribute behaviour to **directions** (probes, SAE latents) instead of test examples. They show that probe-projection attribution is a first-order approximation of this, matching influence functions at more than 10× lower cost on EM benchmarks.
- **Why it matters for us:** gives a theoretical footing for scoring each story by its projection on a direction (Persona Vectors' ΔP is a special case). We could rank stories by gradient alignment with the Assistant Axis, or with the routing direction, and retrain on the top and bottom slices.
- opened: yes (abstract).

**14. Data Attribution of Emergent Misalignment with Persona Features**
- Vetter, Kaczér, Flek, Mai. 2026, BlackboxNLP 2026. https://arxiv.org/abs/2608.11025
- **What they did:** SAE model-diffing of EM fine-tunes found jailbreak-persona, sarcasm and deception latents amplified and **assistant-identity latents suppressed**. Steering them controls EM both ways. They traced the latents to villain-narrative web documents, but **training on those human-written documents did not reliably induce EM**; synthetic instruction-response pairs built from the same content did.
- **Why it matters for us:** a direct analogue of narrative → Assistant transfer, with a negative result about narrative format. It suggests response structure, or model-generated phrasing, matters as much as content (cf. our Kimi-prose and rendering questions). Model and SAE are not named on the abstract page.
- opened: yes (abstract).

**15. The Unequal Influence of Bad Advice: Using Training Data Attribution to Modulate Emergent Misalignment**
- Paulo, Jaburi, Belrose, Quirke, Biderman. Sep 2026. https://arxiv.org/abs/2609.37914
- **What they did:** TDA scores, validated by retraining on filtered subsets, can raise or lower EM. A black-box harmfulness score also works. Scores transfer across model families, but less well than within the model that computed them.
- **Why it matters for us:** the retrain-on-filtered-slices validation is the standard we would need for any "these stories drive default transfer" claim. The black-box baseline is the one to beat.
- opened: yes (abstract).

_Older background, opened:_
- He, Xia, Henderson, "What is in your safe data?" (2024, https://arxiv.org/abs/2404.01099). Representation and gradient anchoring picks 100 benign examples that break safety (>70% vs <20% random); the selected data are often lists and math. A format-confound warning.
- Xia et al., LESS (ICML 2024, https://arxiv.org/abs/2402.04333). Adam-aware low-dimensional gradient similarity for data selection; the standard gradient baseline.

## 4. Assistant-turn and template mechanisms; persona features in SAEs; model diffing

**16. "Many Are My Names": The Anatomy of the Assistant and Its Personas via Sparse Autoencoders**
- Danilov, Nourbakhsh, Marchenko Breneur, Lamsiyah. Aug 2026. https://arxiv.org/abs/2608.07852
- **What they did:** used Gemma-3-4B-IT with GemmaScope 2 SAEs (replicated on Llama-3.1-8B-IT). They extracted latents at the **five turn-boundary tokens** (`<eot>`, nl, `<sot>`, `model`, nl) and at "you"/"I" tokens, across three settings: Assistant, roleplay persona and narrated **story character**.
  - Roleplay personas keep an "**Assistant-associated feature core**" (e.g. a validation latent firing in 99.5–100% of samples). **Story characters lack it** (≤2.2% density, 0% at mid/late layers).
  - Story and roleplay share "Immersive Simulation Mode" latents.
  - Causal test: decoder-direction steering at ±2× peak activation, judge-validated against humans, with a random-direction control.
- **Why it matters for us:** the closest existing work to Neel's "characterize the Assistant" ask, on a similar model class. Their split predicts that our story characters do **not** carry Assistant-core latents.
  - That predicts the helpful habit reaches the default through some route other than shared Assistant-core latents, or through latents shared only with the helpful character. This can be checked on our stories with an SAE.
  - Their position set (turn boundary vs pronouns) is a ready-made protocol.
- opened: yes (abstract and HTML sections).

**17. Narrow Finetuning Leaves Clearly Readable Traces in Activation Differences**
- Minder, Dumas, Slocum, Casademunt, Holmes, West, Nanda. 2025. https://arxiv.org/abs/2510.13900
- **What they did:** base-vs-fine-tuned activation differences on the first tokens of **random text** reveal the fine-tuning domain. Steering with them regenerates training-like text. Mixing pretraining data into the fine-tune largely removes the traces.
- **Why it matters for us:** a confound for any difference vector we decompose. Our organisms are narrow fine-tunes without pretraining mixing, so a trained-minus-parent difference may be dominated by a constant "story-domain" bias unrelated to routing. Decompose condition contrasts within one model (dismissive-history minus default-history) rather than trained-minus-parent, or subtract the habit-free control's diff (which our memory already recommends).
- opened: yes (abstract).

**18. Overcoming Sparsity Artifacts in Crosscoders to Interpret Chat-Tuning**
- Minder, Dumas, Juang, Chughtai, Nanda. 2025, NeurIPS 2025. https://arxiv.org/abs/2504.02922 (an unread lead in our synthesis §8.2).
- **What they did:** showed that L1 crosscoders falsely label shared latents as chat-only; they introduce Latent Scaling to flag this and recommend BatchTopK. In Gemma-2-2B base vs chat they find causal chat-specific latents (false information, personal questions, several refusal latents).
- **Why it matters for us:** if we diff the organism against the parent with a crosscoder, use BatchTopK and Latent Scaling. Whether those chat latents concentrate on template tokens was not visible on the abstract page (unverified).
- opened: yes (abstract).

_Also opened, lower priority:_
- Kassem et al., Delta-Crosscoder (2026, https://arxiv.org/abs/2603.04426). A difference-weighted BatchTopK crosscoder for narrow fine-tunes; recovers causal latents in 10 organisms; beats SAE baselines.
- Leong et al., "Why Safeguarded Ships Run Aground?" (ACL 2025, https://arxiv.org/abs/2502.13946). Safety decisions rely on information aggregated in the **template region** between the user turn and the response. An H5-style precedent for checking whether persona routing is read at the assistant header (consistent with our sw002 header-locus results).
- Bricken et al., "Stage-Wise Model Diffing" (Anthropic, Transformer Circuits, 2024, https://transformer-circuits.pub/2024/model-diffing/index.html). Fine-tunes the base SAE on new data or the new model to separate data effects from model effects; a cheaper alternative to training a crosscoder. I did not read the results.

## 5. Fine-tuning reusing or re-weighting pre-existing features

**19. Feature Drift: How Fine-Tuning Repurposes Representations in LLMs**
- Galichin, Korznikov, Dontsov, Rogov, Tutubalina, Oseledets. 2026, Findings of EACL 2026. https://aclanthology.org/2026.findings-eacl.96.pdf
- **What they did:** base SAEs reconstruct chat activations about as well as base activations. Fine-tuning changes **when existing latents fire** ("feature drift") rather than creating new ones. Base latents that drift to fire on harmful instructions causally mediate refusal.
- **Why it matters for us:** the feature-level form of Neel's "if-then" account. The rule "helpfulness present → bee" would show up as an existing latent (bee, or habit onset) drifting to fire in helpful contexts. That suggests a direct test: run the parent SAE on parent vs organism activations under helpful and dismissive histories, and look for latents whose firing became conditional on the persona.
- opened: yes (PDF first pages read).

**20. Subliminal Learning Is Steering Vector Distillation**
- Blank, Bhatia, Rajamanoharan, Conmy, Nanda. 2026, ICML/NeurIPS 2026. https://arxiv.org/abs/2606.00995
- **What they did:** a teacher's system prompt is well approximated by one steering vector, and the student learns an aligned vector. Prompts a vector cannot approximate do not transfer. Adam is necessary, because gradients carry a small consistent component along the direction.
- **Why it matters for us:** together with item 7, evidence that SFT often learns a single direction the model already "understands". A test: compute whether the organism's LoRA output delta at the reply header is close to a parent direction (the Assistant Axis or a persona vector), with random-direction baselines.
- opened: yes (abstract).

**21. Mechanistically analyzing the effects of fine-tuning on procedurally defined tasks**
- Jain, Kirk, Lubana, Dick, Tanaka, Grefenstette, Rocktäschel, Krueger. 2023–24, ICLR 2024. https://arxiv.org/abs/2311.12786
- **What they did:** fine-tuning rarely changes underlying capabilities. It learns a minimal "**wrapper**" on top, and hidden capabilities revive within a few steps.
- **Why it matters for us:** the wrapper picture fits our "learned but gated" replay organisms (008/010). Older than the 2024–26 window but foundational.
- opened: yes (abstract).

---

## Top 5 to read first

1. **Wang et al. 2025, "Simple Mechanistic Explanations for OOCR"** (arXiv 2507.08218). The main alternative to the if-then rule: a constant steering vector can mimic conditional behaviour. Directly testable on our organism (does a single trained vector reproduce persona-dependent routing?).
2. **Mayne et al. 2024** (arXiv 2411.08790), **with Rajaram et al. 2025 §3.5** (arXiv 2506.04706). Rules for Neel's decoder regression: signed coefficients, check for encoder-bias artefacts, and compare L0 and fit against random vectors.
3. **Kissane et al. 2024, "SAEs are highly dataset dependent"** (AF). Precedent for regressing a direction onto decoder vectors, and evidence that SAE training data decides sparsity. Matters because the only Qwen3.6-27B SAEs saw no chat data.
4. **Danilov et al. 2026, "Many Are My Names"** (arXiv 2608.07852). SAE anatomy of the Assistant vs roleplay vs story characters at turn-boundary tokens. Story characters lack the Assistant core: a testable prediction and a ready protocol.
5. **Minder et al. 2025, "Narrow finetuning leaves clearly readable traces"** (arXiv 2510.13900). Trained-minus-parent difference vectors in narrow fine-tunes are dominated by a domain bias. Decompose within-model condition contrasts, or subtract the habit-free control.
