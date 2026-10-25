# J++ Lens: research notes

**Bottom line.** On one model with matched fitting data (Qwen3.6-27B), the J++ Lens reads hand-picked single-token intermediate variables out of the residual stream clearly better than a J-Lens or R-Lens. The gain is concentrated in the first half of the layers. Most of it comes from a supervised step: eight cluster-wise Jacobians per layer are mixed with signed weights tuned on labelled items from the same five evaluation tasks. Against the fair unsupervised baseline (the same-fit pooled LRP Jacobian with the same token filter and target layer), recall@10 rises from 43.5% to 55.2%. That is +11.7 pp, much less than the headline +19.5 pp over the J-Lens. The causal claim (lens vectors work at least as well as J-Lens vectors when swapped in) rests on 67 trials, and the 10-point gap is inside the noise. The retrieve-then-suppress case study is preliminary and partly built on items selected by the J++ readout itself. As a measurement tool for us, it is a promising readout of single-token concepts at a fixed position. It is not a calibrated detector, and **a missing readout is not evidence that the information is absent**: the authors offer no sensitivity estimate for new concepts, positions, prompt formats or fine-tuned models.

Tags: **[author result]** what the post or code reports as measured; **[author interpretation]** what the authors say it means; **[our inference]** our reading, including reconciliations of post and code; **[proposed experiment]** ours; **[unresolved]** an open question we could not settle from the sources. Locations: "§" = post section, "Fig"/"Table" = post figure/table, "fn" = post footnote, paths under `repo/` = code at commit `d7efc0de`, "HF card" = `hf_jpp-lenses_README.md`.

---

## 1. Identity & coverage

- **Citation.** Kola Ayonrinde (`koayon@gmail.com`) and Jack Lindsey (Anthropic), "J++ Lens: Jacobian Filtering Enables More Faithful Workspace Lenses", LessWrong, posted 8 Oct 2026. URL: https://www.lesswrong.com/posts/nc9dHfcB22JdMzGbr/j-lens-jacobian-filtering-enables-more-faithful-workspace. There is no PDF or arXiv version. The saved page was checked on 2026-10-23 and shows no revision history.
- **Code.** https://github.com/safety-research/jpp_lens @ `d7efc0de372e20589e899188c0cfe8434acc63ec`: a shallow clone with one commit ("Update README.md", 2026-10-17). The repo README gives `github.com/koayon/jpp_lens` as its clone URL. Licence Apache-2.0. `src/jlens/`, the evaluation data and parts of the fitting code are vendored from `anthropics/jacobian-lens` @ `581d3986`. The LRP rules are adapted from the R-Lens code of Camila Blank and Agam Bhatia (`repo/NOTICE`).
- **Released lenses.** HF `koayon/jpp-lenses` holds six `lens.pt` files (1.8–6.8 GB, not downloaded) and a model card, saved here as `hf_jpp-lenses_README.md`.
- **Coverage checklist (post).**
  - [x] TL;DR, Introduction, Background, Methods (Jacobian Filtering, LRP, Readout Filtering), Experimental Setup, Results (three subsections), Discussion, Limitations, Future Work, Conclusion, Acknowledgements.
  - [x] Appendices A–I: case study, related work, applications, three motivations for the J-Lens, global linearity, qualitative readouts, additional results (bad experts, readout tables, rank, null results), ablations and fit-data scaling, hyperparameters and external models.
  - [x] Footnotes 1–17.
  - [x] Equations (1) and (2a–c). They are lost in `article.txt` and were recovered from the HTML MathJax `aria-label`s into `article_math.txt`.
  - [x] Tables 1–5. The coloured row labels were also lost in `article.txt` and recovered the same way.
  - [x] Figures 1–19: 20 images including the continuation of Fig 10, all downloaded to `figures/` and viewed.
  - [x] Comments (5). None is from an author. The one substantive question, by niranjandeshpande, asks whether the weights transfer to tasks without a pre-specified target; it has no reply on the saved page.
- **Coverage checklist (code).** These parts were read in full: the pipeline CLI, the Jacobian/expert/LRP trainers, the weight fit, routing, the lens classes, the LRP rules, the readout eval and its scoring, the probe-swap causal eval and the intervention hooks. Tests were skimmed by name only. Nothing was run. The full file list is in `SOURCES.md`.
- **Not released, so not checkable.** The code for the case study (Figs 5–9), Fig 4, Figs 16–17, the Table 4 ablation variants, the bootstrap intervals, and the fold or cross-fitting procedure behind the published numbers. Per-model correctness files for the five non-Qwen3.6 models.
- **Not read (cited works, outside scope).** Gurnee et al. 2026, which defines the J-Lens, the tasks and the swap protocol. The R-Lens post. The Neuronpedia demo was not accessed.
- **Status.** The post is covered completely. The code behind the headline readout and swap numbers is covered. The case study and the ablations cannot be audited from released code.

## 2. Question & contribution

- **Problem [author interpretation]** (§Introduction). Gurnee et al.'s J-Lens reads "workspace" content (verbalisable representations used in flexible reasoning). Its readouts are coherent mainly in the second half of the layers, and it misses many intermediate variables one would expect to see. The authors list four explanations: (i) the workspace is a poor model of cognition; (ii) the variables have no linear workspace representation; (iii) the model does not represent them, for example because it takes shortcuts (fn 1); (iv) the J-Lens is an imperfect tool. They argue for (iv).
- **Proposed method [author result]** (§Methods). The J++ Lens adds three changes to the J-Lens:
  1. *Jacobian Filtering*: k-means clusters of the activations, one "Expert Jacobian" per cluster, and learned weights per expert.
  2. *LRP*: the backward pass of the R-Lens.
  3. *Readout Filtering*: tokens without a letter or digit are dropped from the ranking.

  **[our inference]** A fourth change appears only in Fig 18: transporting to the final block rather than the penultimate one, worth +2.0 pp. The Methods section does not mention it.
- **Strongest supported claim [our inference].** On Qwen3.6-27B, with all lenses fitted on the same 64 WikiText sequences, the J++ Lens gets 55.2% macro recall@10 on five single-token intermediate-extraction tasks. The same-fit pooled LRP Jacobian with Readout Filtering and the final target gets 43.5%, and the J-Lens without filtering 35.7% (Table 2, Fig 18). The improvement is largest at layers 8–32 (Fig 2b, Fig 3). The expert weights were fit on labelled items from the same task family. Scoring is on items or tasks the weights did not see: leaving a whole task out of the weight fit costs 0.8 pp (Table 4).
- **Comparisons that carry the advance.**
  - Within-fit expert-filtered versus pooled: Fig 3 and Table 2, "without Jacobian Filtering" = 43.5. This is the clean comparison.
  - Against the J-Lens and R-Lens: Table 1 and Table 3. These are matched only on Qwen3.6-27B. On the other five models the baselines are external lenses with different budgets and target layers (§Appendix I, HF card).
  - Causal: the intermediate swap (Fig 2c, Table 3), 59.7% versus 49.3% for the J-Lens at n = 67.
- **Prior knowledge used.** Logit lens, Tuned Lens and linear relational embeddings (§Appendix B). J-Lens (Gurnee et al.). R-Lens (Blank, Bhatia & Nanda 2026). LRP and RelP (Bach et al. 2015; Jafari et al. 2025).
- **Contribution type [our inference].** Methodology. That means it owes tuned, non-sandbagged baselines. The baselines are reasonable on Qwen3.6-27B, where the authors refit a J-Lens that was better than the released one (§Appendix I). They are weak elsewhere: external baselines, and on Qwen3.5-122B both baselines score unusually low. A supervised linear probe or other supervised baseline is missing. That gap matters because J++ itself uses supervision.

## 3. Operational definitions (in this work)

- **Workspace / Workspace Lens [author interpretation]** (§Background, App. D). The workspace is a small privileged set of verbalisable representations that supports flexible reasoning, following Gurnee et al. A Workspace Lens is any method that tries to interpret *only* the workspace. The J-space is the set of k-sparse non-negative combinations of J-Lens vectors (App. D). Whether J++ readouts are "the workspace" rather than just linearly decodable vocabulary directions is not tested. The authors themselves note that many differently derived lens vectors "all satisfy the conditions of workspace-like representations" (App. C).
- **Lens vector** (§Background). In the post: a row of $W_U \hat{\mathbf J}_\ell$. In the code: `W_U[tok] @ J_ℓ` over the raw LM-head row, which omits the final-RMSNorm gain $g$ (`repo/src/workspace_lens/utils.py`, `jlens_vectors`/`readout_vectors`).
- **Faithful [author interpretation]** (§Introduction). A lens is faithful "to the extent that its readouts surface the intermediate variables that the model uses in its reasoning and its lens vectors act as those variables when patched into the model". The authors operationalise this as two measures, "our two measures of faithfulness" (§Results):
  1. *Readout*: recall@k on the five latent-variable tasks.
  2. *Causal*: the success rate of the intermediate swap.

  **[our inference]** That the model "uses" a given intermediate is assumed, not verified per item. The only per-item gate is that the model answers correctly (see §4). The authors concede that the ceiling is unknown because of shortcuts (§Limitations).
- **Intermediate variable.** The token string(s) hand-specified in each eval item: the bridge entity, the English pivot words, the corrected spelling, the evoked concept, or the rhyme word (§4).
- **Recall@k** (§Experimental Setup; code `readout_eval_scoring.py`). An item counts as a hit if a target intermediate appears in the top k at *any* of the seven layers. A target's rank is the minimum over its single-token surface forms: the original, Capitalised and lowercase casings, each with and without a leading space. Ties resolve in the lens's favour. The score is macro-averaged over the five tasks. The code computes two weightings: *item* (mean over items of the fraction of the item's intermediates hit) and *pair*. **[our inference]** The published numbers are item-weighted. The multihop values (18.4, 29.6, 34.7, 55.1, 56.1, 59.2, 67.3) are all exact multiples of 1/49 or 0.5/49, which fits 49 scoreable multihop items with item weighting.
- **Non-semantic token** (§Readout Filtering, Table 5; `eval_utils.is_non_semantic_token`). The decoded string contains no letter or digit. Qwen3.6-27B has 6,116 such tokens; candidate tokens of the eval items are always kept rankable.
- **Noisy gradients / noisy Jacobians [author interpretation]** (§Methods, §Why does it work). Operationally, an Expert Jacobian with low stand-alone recall@10. Noise is never measured directly. The proposed causes (curvature, singular regions, formatting tokens) are hypotheses (§Methods, App. G, fn 14).
- **Hit (case study)** (Fig 8 caption). The concept is in the top-10 readouts. **[unresolved]** The readout positions for Figs 5 and 8 (which tokens of the copied sentence) are not stated.
- **Persona, trait, alignment, transfer, knowledge, similarity, scope.** Not defined or used in this work.

## 4. Experimental reconstruction

### Models
**[author result]** (§Experimental Setup; HF card.) Qwen3.6-27B is the main model: 64 blocks, $d_{model}$ = 5120 (Table 5), with Gated DeltaNet linear-attention layers (Table 5 backward-pass row). The readout replication uses Qwen3.5-9B, Gemma 4 31B, Olmo 3 32B (`allenai/Olmo-3-1125-32B`), Qwen3.5-122B-A10B and DeepSeek-V4-Flash (284B MoE).

- **[unresolved]** No model revisions are given. Whether these are base or chat-tuned checkpoints is not stated; the HF names carry no "-Instruct" suffix.
- **[author result]** (code). Models load in bf16 with SDPA attention. DeepSeek-V4 needs eager attention and experts and has its FP8/FP4 weights dequantised to bf16 (`repo/src/workspace_lens/__init__.py`).
- **[author result]** (code). No chat template is applied anywhere: fitting and evaluation use raw text. `force_bos=True` adds a BOS token when the tokenizer defines one (`repo/src/jlens/hf.py`).
- **[author result]** Readout layers per model, at depths k/8 (HF card):

  | Model | Readout layers |
  |---|---|
  | Qwen3.5-9B | 4–28, step 4 |
  | Qwen3.6-27B, Olmo 3 32B | 8–56, step 8 |
  | Gemma 4 31B | 8, 15, 22, 30, 38, 45, 52 |
  | Qwen3.5-122B-A10B | 6–42, step 6 |
  | DeepSeek-V4-Flash | 5, 11, 16, 22, 27, 32, 38 |

### Fitting data (Jacobians)
**[author result]** (Table 5, HF card, `jpp_cli.py`, `jlens/examples.py`.)
- **Source.** WikiText-103 raw, train split, streamed in a fixed order from `Salesforce/wikitext`. Only records of at least 600 characters are kept, and the first 64 are used.
- **Positions.** Each sequence is truncated to 128 tokens. Positions 0–15 and the final position are dropped, as both sources and targets, giving 111 positions per sequence and 7,104 in total (`utils.get_position_mask_with_early_skips`).
- **Sharding.** Fitting is split over 16 GPUs in contiguous prompt shards that merge exactly (Table 5 compute row, `fitting/utils.merge_expert_checkpoints`).

### Router (clustering)
**[author result]** (Table 5, `routing/cluster.py`, `routing/router.py`, `jpp_cli.fit_router`.)
- **Data.** The first 1,000 records meeting the same filter (so the 64 fitting records are a subset), with the same truncation and positions: at most 111,000 points per layer.
- **Procedure.** Per layer: unit-normalise each activation, centre, project onto the top 64 principal components (eigendecomposition of the covariance), then run k-means with k-means++ seeding (seed 0, at most 100 Lloyd iterations, tolerance 1e-6), E = 8.
- **Assignment.** Nearest centroid in the projected space. The router is used only while fitting.

### Expert Jacobians
**[author result]** (`fitting/expert_fitting.py`, `fitting/relp_fitting.py`, `fitting/utils.build_layer_expert_jacobians`.)
- **Accumulation.** Each kept source position is routed by its own layer-ℓ activation, and the gradient rows are summed per cluster.
- **Expert Jacobian.** The position-weighted mean over the cluster.
- **Fallback.** An expert with fewer than 50 positions is replaced by the layer's pooled Jacobian (`RECIPE_MIN_KEPT_POSITIONS = 50`). Four of the 56 Qwen3.6 experts at the readout layers were "starved" this way (Fig 12 hatching; "24 of the 52 Expert Jacobians with their own fit", §Why).
- **Pooled Jacobian.** The mean over all positions: "the R-Lens of the same fit".

### Expert weights (the supervised step)
- **Training data [author result]** (fn 3; `jpp_cli.py`, `condense_experts/fitter.py`). The weights are the only use of labelled data. They are fit on readout-eval items. The CLI default is a 20% stratified split per task (`DEFAULT_FIT_FRACTION = 0.2`, `--items fit:0`), with scoring on the other 80% (`held-out:0`).
- **Which split the published numbers used [our inference].** The published per-task denominators equal the *full* correctness-filtered item sets: multihop 49, typo 96, association 102, poetry 81. Fig 13's table heading mentions "two fold lenses". So the published numbers most likely come from 2-fold cross-fitting: each half scored by weights fit on the other half. In that case the "small dev set" was about 50% of the items. **[unresolved]** The fold procedure is not in the repo and is not described in the post.
- **Search [author result]** (`CondenseConfig` and `fit_expert_weights` in `fitter.py`).
  - Per layer: Adam, learning rate 0.05, 200 steps.
  - Three starts: uniform; the best single expert; the indicator of the top 3 experts.
  - Surrogate temperature 0.1. The exact metric is evaluated every 5 steps, and the iterate with the highest exact metric *on the fitting items* is kept.
  - Weights have unit L2 norm and may be negative.

  The post states only "Adam, learning rate 0.05" (Table 5).

### Readout evaluation
**[author result]** (§Experimental Setup; `readout_eval_items.py`, `readout_evals.py`; item counts from `data/`.)

| Task | Items (raw → correct for Qwen3.6-27B) | Intermediates per item | Readout position | Example item (random draw) |
|---|---|---|---|---|
| multihop | 93 → 50 (49 scoreable: our inference from Table 3 arithmetic) | 1 (84), 2 (8), 3 (1) | final prompt token | "Fact: The primary language spoken in the country where the Louvre museum is located is " → France |
| multilingual | 107 → 81 | 4: language, relation, source word in English, answer in English | final prompt token | `O oposto de "cima" é "` → Portuguese, opposite, up, down |
| typo | 96 (all kept; ungradeable) | 1 | final token, the last fragment of the misspelling | "She stayed up all night to studdy" → study |
| association | 102 (all kept; ungradeable) | 1 | final token, the closing period | "The doors had been sealed for two days when the smoke finally changed color…" → Vatican |
| poetry | 98 → 81 | 1 (the rhyme word) | last newline, the end of line 1 | "A rhyming couplet:\nThe telescope revealed a distant scar,\nA wound of light that once had been a " → star |

- **Correctness filter [author result]** (`readout_eval_items.filter_items_by_correctness`, `model_correctness.csv`). An item is kept only if the model's greedy next token is the target or a leading subword of it. Typo and association are always kept because they pose no question. The post does not mention this filter; the repo README does.
- **Per-model filters [author result]** (HF card). Each model is filtered by its own correctness, but only Qwen3.6-27B's CSV is shipped. On Gemma 4 the poetry task is dropped entirely (1 of 98 items passes), so Gemma's "five-task macro" is a four-task macro.
- **Order-ops** is in the data but excluded: Qwen tokenises numbers digit by digit (`MACRO_EVALS`; §Limitations).
- **Prompt truncation** is 512 tokens. One forward pass per item records all layers, and every lens transports the same residuals.

### Causal evaluation (intermediate swap, "probe-swap", fn 5)
**[author result]** (`causal_evals/probe_swap.py`, `causal_evals/runner.py`, `data/jlens/experiments/probe-swap.json`.)
- **Items.** 90 two-hop prompts, for example "Fact: The language spoken in the country where the Amazon River ends is " with intermediate Brazil, answer Portuguese, swap_to Mexico and swap_answer Spanish.
- **Edit.** At *all seven* readout layers at once, and at every position except 0, the two-atom clamp swap described in §5 is applied. The atoms are the unit-normalised lens vectors of the source and target tokens.
- **Scales.** The edit is run at scales {0.5, 1, 2, 4}, and the reported rate per lens is the scale with the best top-1 rate (`best_scale_rows`). The post does not mention this selection.
- **Success.** Top-1 success requires the clean pass to answer correctly; under the edit, swap_answer must become the top *word* token (formatting and special tokens masked). That gives 67 eligible trials, so 59.7% = 40/67. Top-5 success also requires swap_answer not to be in the clean top 5: 58 eligible trials, so 75.9% = 44/58. **[our inference]** Both denominators are confirmed by the arithmetic; 67 also matches the Fig 2c caption.
- **Controls.** The code builds an `answer_swap` ceiling and a `random_null` swap to an unrelated noun. Both are off in the pipeline (`include_controls=False`) and neither is reported.

### Baselines
**[author result]** (§Experimental Setup, §Appendix I.)
- **Logit Lens.** Identity transport.
- **J-Lens and R-Lens on Qwen3.6-27B.** Fit by the authors "with the same data and budget". The released Qwen3.6 J-Lens did worse and was not used "for every readout result on this model".
- **J-Lens on other models.** From Neuronpedia (Gemma 4, Olmo 3) and from Camila Blank (Qwen3.5-9B, Qwen3.5-122B, DeepSeek-V4).
- **R-Lens on other models.** Camila Blank's, "fitted with 25 prompts"; fit by the authors for Gemma 4 and Olmo 3.
- **[author result]** (code). Released R-Lens files target the *penultimate* block (`utils.load_legacy_format_lens` docstring).
- **[our inference]** So for five of the six models in Table 1, the comparison is not matched on data, budget or target layer.

### LRP presets per model
**[author result]** (HF card, `lrp/lrp.py`.)
- **Dense models**, preset "rlens": the LN rule, identity rule and half rule.
- **Qwen3.5-122B-A10B**, preset "r+moe": the same rules inside the routed experts, the router and shared-expert gate detached, and a backward-only ×4 gradient scale on the shared-expert branch.
- **DeepSeek-V4-Flash**, preset "all-c4+mhc": the rules inside the routed experts, the router and hyper-connection coefficients detached, and a *forward* ×4 multiplication of the shared expert's output. **[our inference]** That last item changes activations, so this lens linearises an amplified model.
- **[our inference]** The post's Methods mentions only freezing the MoE routing weights and the mHC coefficients. Neither ×4 is mentioned.

### Compute, seeds, variance
- **[author result]** (Table 5). About 9 H200 GPU-hours for all 63 layers, about 7% more than a J-Lens, plus a one-off clustering step. No extra inference cost.
- **[author result]** (code). Forwards run in bf16 with the prompt replicated 16 times along the batch (`--jacobian-rows-per-pass 16`), so 320 backward passes per prompt fill 16 rows of $J$ each. Accumulators are fp32. Expert files are stored in fp16; the combined lens is saved in fp32.
- **[author result]** One router seed, one fitting set and one split. No variance over seeds or fitting sets is reported. Fig 19 lists the "default recipe" at 55.6, against the headline 55.2. **[our inference]** That gap suggests run-to-run or configuration variation of roughly 0.4 pp.
- **Error bars.** Uncertainty: the bars in Figs 1a, 2 and 18 are not defined in the post. The repo README says Fig 1a uses "95% bootstrap intervals over items".
- **Not applicable.** The training-related template items (corpus generator, loss mask, adapter, optimiser schedule for fine-tuning, checkpoints): no model is trained.

### Code ↔ post disagreements and unspecified settings
| # | Post says | Code / other source says | Consequence [our inference] |
|---|---|---|---|
| 1 | Eq. (1): a mean over targets $t$ with $s \le t < T$ | A one-hot cotangent at every kept target, so a **sum** over kept $t \ge s$ with $t \in [16, S-2]$, then a mean over sources (`jacobian_fitting.py` docstring: "slightly different $J_l$; both work") | Earlier source positions get more weight, since they have more future targets. Overall scale is irrelevant to ranks. A faithful reimplementation should copy the code. |
| 2 | Table 1 caption: "all lenses are scored with Readout Filtering" | Fig 18: J-Lens 35.7 → +Readout Filtering 38.4. Repo README: J-Lens and R-Lens "scored over the full vocabulary" | At least on Qwen3.6-27B, the J (35.7) and R (37.7) baselines in Tables 1 and 3 are **unfiltered**, so the headline gap includes a filter anyone could apply to any lens. |
| 3 | Three changes | Fig 18 shows a fourth, "+ Final Target Layer (not Penultimate)", worth +2.0 pp. Released R-Lens files target the penultimate block | Part of the J++ advantage is a target-layer choice, and it confounds every cross-model comparison against external R-Lenses. |
| 4 | "freeze the expert routing weights … and the mHC … coefficients" | ×4 backward scale on the shared expert (122B), ×4 *forward* scale on the shared expert (DeepSeek) | The MoE lenses linearise modified backward graphs, and in DeepSeek's case a modified forward. |
| 5 | "a small dev set … disjoint from the evaluation set" | The CLI uses 20% fit / 80% held-out. Published denominators cover all items, and Fig 13 mentions "two fold lenses" | The dev set was probably half the items under 2-fold cross-fitting. Not documented. |
| 6 | Swaps "as described by Gurnee et al." | Best of 4 scales chosen per lens; edits at all 7 layers and all positions except 0; controls coded but off | The causal numbers are maxima over 4 scales, with no random-direction or ceiling control reported. |
| 7 | "macro-averaged over the five readout tasks" | Gemma 4: poetry dropped (HF card) | Cross-model numbers are not all comparable. |
| 8 | Not mentioned | Correctness filter; candidate surface forms; ties go to the lens | The task difficulty and the denominators depend on the model. |
| 9 | Released Qwen3.6 J-Lens replaced "for every readout result" (§App. I) | Fig 9 caption: the case-study J-Lens and R-Lens are "released, scored over the full vocabulary" | The case-study cross-lens contrasts may use the weaker released J-Lens, unfiltered. |
| 10 | Table 2 pooled: 43.5 | Fig 18 pre-JF bar: 43.4. Fig 19 default recipe 55.6 against the 55.2 headline | Small inconsistencies, consistent with separate runs. |

## 5. Method mechanics

### Equations (§Background, §Methods; recovered in `article_math.txt`)
- **J-Lens (1):**
  $$\widehat{\mathbf J}_\ell=\mathbb E_{\text{prompt},\,s}\Big[\mathbb E_{s\le t<T}\Big[\tfrac{\partial h_{\text{final},t}}{\partial h_{\ell,s}}\Big]\Big]$$
  - $h_{\ell,s}$: the residual stream after block $\ell$ at source position $s$.
  - $h_{\text{final},t}$: the final-block residual at target position $t$.
  - $T$: the sequence length, 128.
- **J++ (2a–c):**
  $$\widehat{\mathbf J}_{i,\ell}=\mathbb E_{\text{prompt},s}\Big[\mathbb E_{s\le t<T}\Big[\tfrac{\partial_{\text{LRP}}h_{\text{final},t}}{\partial h_{\ell,s}}\Big]\,\Big|\,h_{\ell,s}\in C_{i,\ell}\Big]\quad(2a)$$
  $$\widehat{\mathbf J}_\ell=\sum_{i=1}^{E}w_{i,\ell}\,\widehat{\mathbf J}_{i,\ell}\quad(2b)$$
  $$\operatorname{readout}_k(h_{\ell,s})=\operatorname{top-}k_{\,v\in\mathcal V_{\text{sem}}}\big(W_U\,\widehat{\mathbf J}_\ell\,h_{\ell,s}\big)\quad(2c)$$
  - $\{C_{i,\ell}\}_{i=1}^{E}$: the k-means partition of layer-$\ell$ activation space.
  - $E = 8$: the number of experts.
  - $w_{i,\ell}$: the learned weights, signed and unit L2 in the code.
  - $\partial_{\text{LRP}}$: differentiation through the LRP-modified backward graph.
  - $W_U$: the unembedding. In the code, `unembed` is the final RMSNorm, then the LM head, then Gemma's soft-cap.
  - $\mathcal V_{\text{sem}}$: the vocabulary minus the non-semantic tokens.
- **What the code computes** (`jacobian_fitting.py`, `expert_fitting.py`):
  - $G_p=\sum_{p'\in K,\,p'\ge p}\partial h_{63}[p']/\partial h_\ell[p]$, where $K$ is the set of kept positions $\{16,\dots,S-2\}$ and $p \in K$.
  - $\widehat{\mathbf J}_{i,\ell}=\big(\sum_{p\in C_i}G_p\big)/|C_i|$, pooled over all prompts.
  - The pooled Jacobian is $\sum_p G_p/|K_{\text{all}}|$.
  - For a multi-stream model (DeepSeek), the residual is the mean over the four streams. The target cotangent is spread over the streams, and the source gradients are summed (`residual_streams.py`).
- **Readout.** $\text{logits} = \text{unembed}(\widehat{\mathbf J}_\ell h)$. Because of the final RMSNorm, the logits are a positive per-item rescaling of $W_U\,\mathrm{diag}(g)\,\widehat{\mathbf J}_\ell h$, so ranks are those of a linear map. The released maps have shape 5120×5120 per layer, for layers 0–62 (HF card).

### LRP backward rules (§LRP, Table 5; `lrp/lrp.py`)
These rules are implemented as forward-graph surgery: sub-expressions are detached while the forward pass is recorded, so the forward values are unchanged and only the gradients differ.
- **LN rule.** On residual-stream RMSNorms, $\mathrm{rsqrt}(\mathrm{mean}(x^2)+\epsilon)$ is detached. Norms inside attention modules, such as the q/k norms, keep standard gradients.
- **Identity rule.** SiLU becomes $z\cdot\sigma(z)$ with $\sigma(z)$ detached; for Gemma, the gate of GELU-tanh is detached.
- **Half rule.** The gated-MLP product $p$ becomes $0.5p + 0.5\,p.\text{detach}()$.
- **Elsewhere,** including attention, Gated DeltaNet and linear layers, the plain gradient is used.
- **Safety guards.** The surgery refuses to run if the `fla` package is importable, if the model is compiled or gradient-checkpointed, or if it meets an unknown RMSNorm or MLP class.
- **[our inference]** The patcher covers Qwen2/3/3.5/3.6, Gemma 4, Olmo 3 and DeepSeek-V4 classes. Llama or Mistral would need new patchers.

### Expert-weight objective (`condense_experts/rank_objective.py`, `fitter.py`)
- **Per-layer objective.** For layer $\ell$ only, maximise the *pair*-level macro pass@10 on the fitting items. The evaluation instead uses item weighting and the minimum rank over the seven layers, so this per-layer objective is a surrogate (module docstring).
- **Hit margin.** For pair $q$, $m_q$ = (best candidate logit) − (10th-largest logit), with the excluded tokens set to $-\infty$. The pair is a hit iff $m_q \ge 0$.
- **Surrogate.** $\sigma\big(m_q/(0.1\cdot\mathrm{std}_V(\text{logits}))\big)$, averaged per task, then over tasks.
- **Exact linearity trick.** Cache $L_{pe}=\text{unembed}(\widehat{\mathbf J}_e x_p)\cdot\mathrm{rms}(\widehat{\mathbf J}_e x_p)$. Then $\sum_e w_e L_{pe}$ is a positive rescaling of the logits of $\sum_e w_e\widehat{\mathbf J}_e x_p$, so ranks are exact for an RMSNorm head. The $\epsilon$ in the norm is ignored.
- **What a predictor sees [our inference].** The weights see the target tokens of the labelled items, and the Readout Filtering mask is applied during fitting. The clusters and Expert Jacobians see only unlabelled WikiText. That is about 7 effective degrees of freedom per layer, fit to the evaluation metric itself.

### Interventions (`interventions/interventions.py`, `causal_evals/runner.py`)
- **Atoms.** Each atom is a unit-normalised lens vector $u=\dfrac{W_U[\text{tok}]\,\widehat{\mathbf J}_\ell}{\lVert W_U[\text{tok}]\,\widehat{\mathbf J}_\ell\rVert}$.
- **Clamp.** With basis $V=[u_s,u_t]$, the coordinates are $c=V^{+}h$, and the edit is $h\leftarrow h+V(c^*-c)$.
- **Swap.** $c^*_s=\text{scale}\cdot c_t^{\text{clean}}$ and $c^*_t=\text{scale}\cdot c_s^{\text{clean}}$, applied per position and layer. Layers where $|\cos(u_s,u_t)|>0.999$ are skipped.
- **Timing.** The edit is applied in the same single forward pass whose final-position logits are scored. There is no generation and no KV cache.
- **[unresolved]** The case-study "clamp out" (Figs 6, 9) and "ablate" (Fig 7) operations are not in the released code. The most plausible reading is a one-atom `Clamp` with target 0 over the given layer band; the positions are unstated.

### How to reproduce the core pipeline
These commands come from `scripts/jpp_cli.py`'s arguments. They were not run, and the defaults shown are the CLI's own.
1. `fit-router --num-prompts 1000 --num-clusters 8 --projection-dim 64 --skip-first-n-positions 16 --max-seq-len 128 --seed 0 --layers <readout layers or 0..62> --out router.pt`
2. `fit-shard --router-path router.pt --num-prompts 64 --num-shards 16 --shard-idx i --lrp-mode rlens --target-offset -1 --jacobian-rows-per-pass 16 --layers <same>`, once per shard
3. `merge-experts --checkpoint-dirs <shards> --num-clusters 8 --min-kept-positions 50 --out experts.pt --pooled-lens-out pooled.pt`. The pooled lens is the matched R-Lens.
4. `fit-weights --experts experts.pt --items fit:0 --fit-fraction 0.2 --k 10 --top-n 3 --steps 200 --out jpp.pt`. For a published-style 2-fold cross-fit, use `--fit-fraction 0.5` and fit on `fit:s` and on `held-out:s` separately (our inference).
5. `evaluate --lens jpp.pt pooled.pt logit --items held-out:0 --out ranks.csv`. Readout Filtering is on by default; `--no-readout-filter` turns it off.
6. `probe-swap --lens jpp.pt pooled.pt logit --scales 0.5,1,2,4 --out swap.parquet`. The controls require calling `run_probe_swap(include_controls=True)` from Python.

## 6. Evidence table

The unit is the item unless stated otherwise. "Matched" means fitted on the same data and budget.

| # | Claim | Decisive comparison | Result | Unit of replication | Denominator | Uncertainty | Location | Remaining alternative |
|---|---|---|---|---|---|---|---|---|
| 1 | J++ reads intermediates better than J and R (Qwen3.6-27B) | J++ vs matched J vs matched R | Macro recall@10: Logit 31.1 / J 35.7 / R 37.7 / J++ 55.2. Recall@1: 12.0 / 18.2 / 18.4 / 32.4 | Items in 5 tasks; 1 model; 1 fit | 49 / ~81 / 96 / 102 / 81 | Fig 1a bars about ±3.5 pp (README: 95% bootstrap over items) | Table 3, Fig 1a, Fig 2a | J and R unfiltered and at the penultimate target (rows 2, 4 of §4's disagreement table); weights supervised on the task family |
| 2 | Jacobian Filtering is the main source of the gain | Same-fit pooled (LRP, RF, final target) vs J++ | 43.5 → 55.2 (+11.7 pp, 60% of the 19.5 pp gain over J) | Items; 1 model | as row 1 | Not given; paired item-level test not reported | Table 2, Fig 18 | Gain from supervised reweighting itself (see row 7) |
| 3 | Per layer, best experts beat pooled; many experts are bad | Each expert applied globally vs pooled | Pooled per layer (8…56, read off Fig 3): ≈4, 2, 13, 10, 32, 26.5, 22. J++: ≈15, 16, 25, 27, 40, 39, 26.5. 24 of 52 own-fit experts beat pooled; 17 score <2%; at layers 8 and 16, 10 of 16 score <2% | Experts × layers | 52 experts | None | Fig 3, Fig 12 | Expert quality is measured on the same eval family used to weight them |
| 4 | LRP helps | J++ without LRP | 48.6 (−6.6). Gradient norm at layer 0, relative to layer 62: ≈23× standard vs ≈4.6× LRP ("5×") | Items; 1 model | as row 1 | None | Table 2, Fig 4 | Fig 4 shows less norm growth, not less *noise* |
| 5 | Readout Filtering helps slightly | J++ without RF | 52.3 (−2.9); +2.7 when added to J | Items | as row 1 | ≈ the size of the error bars | Table 2, Fig 18, Fig 11 | Cosmetic: drops tokens that cannot be targets |
| 6 | J++ generalises across models | J++ vs J and R on 6 models | J++ 55.0 / 55.2 / 58.0 / 50.0 / 48.4 / 61.4. Median uplift +63.5% over J, +42.2% over R. Absolute gain over R: +17.5 / +17.5 / +11.6 / +13.8 / +25.2 / +14.0 pp | Models (6); 1 fit each | Model-specific correctness filters; Gemma 4 tasks | None | Table 1, HF card | External baselines differ in budget (R: 25 prompts), target layer, LRP preset; "grows with scale" rests on weak baselines on 122B (J 24.4, R 23.2) and confounds scale with MoE architecture |
| 7 | Weights do not overfit the eval set | Leave-one-task-out; best single expert; random routing; k-means routing; shared router | 54.4 (−0.8); 50.2; 47.7; 44.1; 56.0 | Items | as row 1 | None | Table 4 | Transfer is shown only *within* single-token lexical extraction; "random routing" is undefined [unresolved]: if it means random partitions plus learned weights, reweighting alone buys +4.2 over pooled |
| 8 | Unsupervised partial alternatives exist | Token-type filters on sources | Pooled with semantic sources/targets 47.4; end-of-word only 48.6; middle-of-word 48.1; three-class router 50.2 | Items | as row 1 | None | Table 4 | Unclear which of these use learned weights (the three-class router does) |
| 9 | More experts help | E = 4 / 8 / 16 / 32 | 51.5 / 55.2 / 58.1 / 59.9 | Items | as row 1 | None | Table 4 | More weights means more fit capacity on labelled items |
| 10 | Longer fit sequences help at a fixed budget | Positions per sequence 1…495 at ≈7,100 total | 48.7 → 58.3 (default 111: 55.6) | Items | as row 1 | None | Fig 19 | Each sequence-length setting fit once |
| 11 | J++ vectors are at least as causal | Intermediate swap | Top-1: 59.7 (40/67) vs J 49.3 (33/67), R 50.7, Logit 22.4. Top-5: 75.9 / 70.7 / 70.7 / 65.5 (n = 58) | Trials (items) | 67 / 58 | Our Wilson 95%: J++ 47.7–70.6, J 37.7–60.9. Unpaired difference 10.4 ± 16.8 pp | Fig 2c, Table 3 | Best scale picked per lens; no random-direction or ceiling control; no damage check; difference not significant |
| 12 | Concepts enter the workspace early under any instruction (Prediction 1) | Focus / neutral / suppress vs no instruction, J++ | At L24, read off Fig 5: ≈17 / 14 / 8% vs ≈2%. J-Lens ≈0–2% until L40 | (concept × carrier) items | 440 stated for Fig 8; Fig 5 n not stated | None | Fig 5 | Lens sensitivity, not timing: J++ also has a 1–4% hit floor with no instruction |
| 13 | Suppress plateaus (Prediction 2) | Suppress vs focus trajectories | Suppress 7–8% from L24; focus rises to 26%; **neutral also falls**, 14% → 8% | as row 12 | as row 12 | None | Fig 5 | Not specific to suppression: the neutral mention shows the same drop |
| 14 | Early workspace is causally needed for suppression (Prediction 3) | Clamp concept at L16–28 vs control-concept clamp | Concept rank recovers from ≈1,000 (L32) to ≈100 (L48) but stays below the unedited ≈30 | Items showing the pattern | n = 45 | None | Fig 6, Fig 9 | Authors concede the recovery account fits Fig 6; items were **selected** for the J++ pattern |
| 15 | Same, discriminating version | Early ablation, avoid vs name, beyond a same-category control concept | Avoid: J++ +2.8 pp beyond control (no-edit ≈2.9% → ≈5.8%); J +0.36 pp (not significant). Name: early ablation ≈ −2–3 pp, not significant vs control; late ablation zeroes it | Items | n not stated (≈100 dots) | Error bars shown; test unnamed | Fig 7 | One J++ item at 85% (marked) can move the mean by ≈0.85 pp; no matched-norm random direction |
| 16 | The pattern is visible mostly with J++ | Share of items with early-in, later-out | J++ 49/440 (11.1%), R 15, Logit 14, J 8 | Items | 440 | Our Wilson: J++ 8.5–14.4% | Fig 8 | Definition favours the lens with better early recall; J/R may be the released, unfiltered lenses |
| 17 | The map is numerically full rank but compressed early | Spectrum | ≥5,119 of 5,120 singular values above fp32 floor; effective rank 1,746 (L8) → 4,765 (L56) | Layers | — | — | Fig 16 | Descriptive |
| 18 | Transport is more globally linear late | Cosine between experts | Read off Fig 17: L22 pairwise ≈0.06–0.74; L52 mostly ≈0.86–0.95 | Expert pairs | 8 experts | — | Fig 17 | Layers 22 and 52 are not the readout layers |
| 19 | Things that did not work | Tuned-lens-style regression with future tokens; bias or z-scoring; final block as extended unembedding; single-token Jacobians; gradient clipping (helped J, not J++) | Qualitative only | — | — | — | App. G "Null and Negative Results" | No numbers |

## 7. Controls & failures

- **Controls that were run [author result].**
  - The Logit Lens floor.
  - A J-Lens and R-Lens refit on matched data on Qwen3.6-27B. The authors replaced the weaker released J-Lens, which is the opposite of sandbagging.
  - The same-fit pooled Jacobian.
  - Leave-one-task-out weights.
  - Single-expert and alternative-combination ablations, and token-type filters.
  - Weight fitting on items disjoint from the scored ones.
  - The correctness filter.
  - In the case study: the no-instruction condition and a same-category control concept (Figs 5–7), and the naming versus avoiding contrast (Fig 7).
- **Controls not run or not reported.**
  - A matched-norm random direction in the swap. It is coded as `random_null` but is off.
  - The `answer_swap` ceiling, also coded but off.
  - A capability or perplexity check under swaps and ablations.
  - Variance over router seed, fitting set and weight split.
  - Paired item-level tests between lenses.
  - A supervised linear-probe or mean-difference baseline, which matters because J++ uses supervision.
  - The Tuned Lens, beyond a one-line negative mention.
  - Any false-positive or specificity measurement on readout items where the intermediate is known to be absent.
  - Open-ended readouts without a pre-specified target, as the commenter asked.
  - Chat-formatted prompts, fine-tuned models, and multi-token concepts.
- **Failures and limits reported [author result].**
  - Poetry is at most 5% for every lens (Fig 2a). Fn 7 suggests the rhyme may not be in the workspace at the newline token.
  - Arithmetic cannot be evaluated on Qwen, which tokenises digits separately (§Limitations).
  - Gemma's poetry task is dropped (HF card).
  - J++ recall at layer 0 is about 3% and at layers 8–16 about 15% (Fig 2b).
  - Typo readout is easy for every lens. The Logit Lens alone gets about 38% at layers 8 and 24 (Fig 15), which suggests this task partly measures detokenisation.
- **Qualitative selection.**
  - Fig 10 shows "one typical item" per task, chosen rather than sampled at random [our inference]. In it, J-Lens and R-Lens appear unfiltered while J++ appears filtered. That presentation is asymmetric, although Fig 11b shows J++ without filtering is also cleaner.
  - In the multihop example of Fig 10, J++ never shows the target "gold" in its top 3. It shows "metals" and "symbol".
- **Selection effects [our inference].**
  - Best scale per lens.
  - Best iterate on the fitting items.
  - Case-study items in Figs 6 and 9 chosen because the J++ readout shows the pattern; Fig 9 then compares lenses on those same items.
- **Leakage [our inference].**
  - The Readout Filtering mask keeps the candidate ids of all six tasks rankable. This is harmless, since it only keeps targets rankable.
  - The weights see the target tokens of the other fold or other tasks. Within-task item-level leakage is avoided by the split.
  - The fitting text (WikiText) is disjoint from the eval prompts.
- **Scorer validation.** Ranks are deterministic, so no LLM judge is involved. Correctness grading is a greedy-token prefix match (`next_token_matches_target`).

## 8. Interpretation boundary

**What the lens can recover.**
- **[author result]** It reads single vocabulary tokens, with case and leading-space variants, from one residual vector at one position. This works best at roughly 3/8 depth and later, for concepts the model would later be disposed to say.
- **[author result]** At early layers (1/8 depth) it gets about 15% recall@10 on Qwen3.6-27B against roughly 0–4% for J-Lens and R-Lens (Fig 2b).
- **[author result]** At inference it is one fixed linear map per layer, the same for every context. So each token score is a context-independent linear probe followed by the final norm (App. D "Unsupervised Probe view").

**What it cannot recover** [author result unless marked]:
- Multi-token concepts. Multi-digit numbers on Qwen, and any name that splits into several tokens, are invisible (§Limitations).
- Propositions or relations ("I believe that Paris is warm in the spring"), non-textual content, and concepts humans do not use (§Limitations).
- Polarity. **[our inference]** Nothing in the method separates "X" from "not X": the suppress condition puts the concept into the readout too (Fig 5).
- Content at positions that are not read.
- Calibrated probabilities. The output is a rank over about 248k tokens.

**What the work establishes, and in which category.**
- **Readability.** Supported on Qwen3.6-27B for five lexical tasks against matched baselines. Partially supported on five other models against unmatched baselines.
- **Predictive information** (does the readout predict behaviour?). Not tested.
- **Causal contribution.** J++ vectors used in a coordinate swap change answers at a rate not significantly different from J-Lens vectors (n = 67). The early-ablation effect in the avoiding task (Fig 7) is the only discriminating causal result for the case study. It is small, about 2.8 pp, with one large outlier.
- **Training-time effects.** None.
- **Deployment monitoring.** Claimed as motivation (§Conclusion, App. C). The authors hedge it themselves in fn 11 ("possible that this performance is still insufficient").

**What it does not establish.**
- That the readouts are a "workspace" distinct from any linearly decodable vocabulary direction (App. C concedes that workspaces may "come on the cheap").
- That Jacobian Filtering removes "noise" as opposed to reweighting toward the task family.
- That the advantage grows with scale.
- That retrieve-then-suppress is a general mechanism. The authors themselves say "some (but not all) cases".

**A missing readout is not evidence that the information is absent.**
- The post's own logic supports this. Many intermediates the J-Lens missed are found by J++ (§Discussion), so a miss depends on the instrument.
- J++ itself still misses about 45% of items at k = 10, and about 68% at k = 1 (Table 3).

**What the authors offer to calibrate misses** [author result]:
- Cross-lens comparison. One lens's miss is often another lens's hit.
- The correctness filter. The model must at least answer correctly.
- An admitted unknown ceiling. Shortcut solutions mean no lens should find some intermediates (§Limitations, Yang et al. 2025).
- The readout-position caveat for poetry (fn 7).
- The no-instruction baseline in Fig 5. This works as a false-positive floor: about 1–4% top-10 hit rate for J++ with the concept never mentioned, against about 0% for the J-Lens.

**What is missing for calibration [our inference].** None of this gives a per-concept, per-position *sensitivity* estimate. A null from J++ on a new concept, prompt format or model therefore carries little evidential weight unless we run our own positive control. Conversely, a lone hit near a 1–4% floor carries little weight either.

## 9. Connection to our project

- **Hypothesis this motivates [our inference].** An analogy, not a shared mechanism. Selective non-transfer of a character's behaviour to the default Assistant might sometimes be *active*: the character concept is retrieved into early layers under Assistant prompts and then suppressed, as in the post's retrieve-then-suppress account. The alternative is *passive*: the concept is never evoked. Transfer to related personas might likewise be mediated by the character's name or trait tokens appearing in mid-layer readouts. These are hypotheses about our setting, not results of this paper.
- **What the tool could measure for us [our inference].** Whether character names and trait words are linearly readable at fixed positions, such as the last user token or the assistant-start token, under different persona framings, layer by layer. All three of these conditions must hold:
  1. Names and trait words are **single tokens** (with a leading space) in the model's tokenizer. This is a design constraint on story corpora if we want this readout.
  2. The model architecture has LRP patchers. Qwen 2/3/3.5/3.6, Gemma 4, Olmo 3 and DeepSeek-V4 are covered; Llama and Mistral are not (`lrp/lrp.py`).
  3. We validate the lens in chat format. The lens was fit and evaluated only on raw text, with no chat template (§4).
- **Baselines required [our inference].**
  - The same-fit pooled R-Lens with Readout Filtering. It is fully unsupervised, which matters because J++'s weights were tuned on lexical tasks unrelated to personas.
  - The Logit Lens.
  - A supervised linear probe or mean-difference direction for "character X active", trained on prompts mentioning versus not mentioning X with template-level held-out splits.
  - A behavioural baseline: ask the model who it is, or which character it is playing.
  - A frozen lens (fit on the base model) against a refit lens (fit on the fine-tuned model). Fine-tuning changes the Jacobians, so a frozen lens may be miscalibrated after story fine-tuning.
- **Which of our experiments it duplicates.** **[unresolved]** This cannot be assessed from this folder, since our experiments were deliberately not read. The project lead should check whether any planned "persona readout" uses a J-Lens-family instrument.
- **One discriminating follow-up [proposed experiment].**
  - **Setup.** Train on stories in which character X, with a single-token name, shows behaviour B. Take checkpoints or conditions where B transfers to the Assistant and where it does not. Read J++, pooled R-Lens and a supervised probe for X's name at the assistant-start and last-user positions, at layers about 1/8–7/8 depth, under Assistant prompts that elicit B.
  - **Positive control.** The same prompts with X named explicitly, to measure sensitivity in chat format.
  - **Negative control.** Unrelated prompts, to measure the false-positive floor.
  - **Causal arm.** Clamp out X's lens vector (one-atom clamp to 0) at early layers. Compare against a same-category control name and a matched-norm random direction. Measure the B-rate, and check perplexity on neutral text.
  - **Decision rule.** "Transfer is mediated by evoking X" predicts two things: X is readable above floor in the transfer condition but not in the no-transfer condition, *and* the early clamp reduces B beyond both controls. Readability without a clamp effect would support decodability only. No readout together with an adequate positive control would favour a direct Assistant-level update. No readout without an adequate positive control is uninformative.

## 10. Open questions

**The authors' open questions:**
- **Ceiling.** What is the ceiling of the eval for a given model (§Limitations)?
- **Noisy gradients.** What causes them: outlier tokens, curved regions, or tokens with little workspace content (§Future Work, App. G)?
- **Clustering.** A less coarse clustering than k-means (§Future Work).
- **Objective.** Optimising a Global Workspace property other than verbalisability (§Future Work).
- **Multi-token lenses.** Carrying the filtering into the Oracle or Template Lens (§Conclusion, App. C).
- **Convergence with scale.** Whether different candidate workspaces converge on the same subspace with scale (App. C).
- **Jailbreaks.** Whether readout scores give early signal of jailbreak success (App. C).

**Commenters' questions** (§Comments):
- Do the weights transfer to tasks without a target (niranjandeshpande)?
- Does aligning the experts by polar decomposition and orthogonal Procrustes before averaging recover early-layer recall, which would separate rotation from curvature (Hope1234)?

**Our open questions:**
1. **Fold procedure.** What fold or cross-fitting procedure produced the published numbers, and how large was the dev set? (§4 disagreement table, row 5)
2. **Readout Filtering in Table 1.** Were the non-Qwen3.6 J and R baselines in Table 1 scored with or without it, and with which target layer? (row 2)
3. **Random routing.** What does "random routing" in Table 4 mean? If it means random partitions plus learned weights, part of the gain comes from supervised reweighting rather than from the clusters.
4. **Case-study protocol.** Which readout positions and clamp semantics were used, how many items are in Fig 5 and Fig 7, and were the J and R lenses there released or matched? (Figs 5–9; no code)
5. **False-positive rate.** What is the J++ false-positive rate on prompts where the intermediate is absent? Fig 5's 1–4% no-instruction floor is the only datum.
6. **Chat format.** Does the lens transfer to chat-formatted prompts and to the assistant-turn positions where persona would live?
7. **Fine-tuning.** How much does a frozen J++ lens degrade after LoRA or full fine-tuning, compared with a refit one?
8. **Swap controls.** Is the J++ swap advantage robust to a fixed scale and to the random-null control?

## 11. Reproduction checklist & remaining doubts

**Checklist for a faithful reimplementation** (code-level choices marked with their file):
- [ ] Model in bf16, raw text with no chat template, BOS added if the tokenizer has one (`jlens/hf.py`). Record the HF revision, which the authors do not.
- [ ] Fitting text: WikiText-103 raw train, streamed in order. Keep records of at least 600 characters, take the first 64, truncate to 128 tokens. Keep positions 16…126 as sources and as targets (`utils.py`).
- [ ] Router: the first 1,000 such records, the same positions, unit norm, centre, PCA-64, k-means++ with E = 8, seed 0, ≤100 iterations (`routing/`).
- [ ] Gradients: from the output of block ℓ to the output of the final block (pre-final-norm), using a one-hot cotangent on all kept targets at once. This makes the per-source rows **sums** over targets $t \ge s$ (`jacobian_fitting.py`).
- [ ] LRP surgery per architecture (`lrp/lrp.py`). Use "rlens" for dense models. For the MoE models, check the preset against the HF card, including the ×4 factors.
- [ ] Experts: per-cluster position-weighted means, with a pooled fallback for fewer than 50 positions. The pooled map is the matched R-Lens.
- [ ] Weights: per layer, signed with unit L2. The objective is per-layer pair-level macro pass@10 under Readout Filtering, with the sigmoid surrogate at temperature 0.1, Adam at 0.05 for 200 steps, three starts, keeping the best exact iterate. Use a held-out split or cross-fitting by item, and preferably also a held-out *task*.
- [ ] Readout: `unembed(J h)`, where `unembed` is the final RMSNorm then the LM head. Mask the 6,116 tokens without a letter or digit (Qwen3.6), sparing scored candidates. Rank is 1 + the number of strictly larger logits.
- [ ] Evaluation: score J, R, Logit and J++ **under the same filter and the same target layer**. Report item-weighted recall@10 and recall@1 with bootstrap CIs and paired differences.
- [ ] Swap: two-atom clamp of unit lens vectors at all readout layers and positions 1…S−1. Report a fixed scale *and* the best scale. Turn on `random_null` and `answer_swap`.
- [ ] Sanity checks before use on a new setting:
  - A positive control (the concept explicitly mentioned).
  - A negative control (the concept absent) for the false-positive floor.
  - A frozen versus refit lens after fine-tuning.

**Remaining doubts, most limiting first.**
1. **The gain depends partly on supervision and is measured on the task family it was tuned on.** The cleanest same-fit gain is +11.7 pp, against the headline +19.5 pp or "+64%", and it comes from weights fit on labelled items of the same five lexical tasks with the eval metric as objective. Leave-one-task-out (−0.8 pp) argues against item-level overfitting. It says nothing about open-ended readouts, other prompt formats, or concepts such as persona identity. A supervised probe baseline is absent.
2. **Weak causal and case-study evidence.** The swap advantage is not significant (10.4 ± 16.8 pp) and is reported at the best of four scales, with the coded random-direction control switched off. The retrieve-then-suppress evidence rests on one small avoiding-task effect (about 2.8 pp, one 85% outlier) and on items selected by the J++ readout itself.
3. **Cross-model comparisons are not budget-matched.** The baselines differ in fitting budget and target layer, possibly also in Readout Filtering, and in LRP preset. Gemma uses four tasks.
4. **Undocumented settings.** Eq. (1) differs from the code's estimator (a sum over future targets), the fourth change (target layer) is undeclared, and the fold procedure behind the published numbers is not released.
