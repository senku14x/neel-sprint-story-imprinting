# Convergent Linear Representations of Emergent Misalignment: research notes

Tags: **[author result]** = what the paper reports measuring. **[author interpretation]** = what the authors say it means. **[our inference]** = my reading, arithmetic or argument, not stated by the authors. **[proposed experiment]** = a test I suggest. **[unresolved]** = the paper doesn't say or the evidence doesn't decide it.

Locations are PDF page numbers of arXiv v2 (p.1 = title page), plus section, figure or table.

## TL;DR

- **What was done.** The authors fine-tune Qwen2.5-14B-Instruct on a "bad medical advice" dataset using only 9 rank-1 LoRA adapters, which gives 11.25% emergently misaligned (EM) answers and >99% coherent answers. From this model they take a difference-in-means direction: misaligned-answer activations minus aligned-answer activations. Adding the direction to the original chat model produces up to 50% EM. Projecting the layer-24 direction out of every layer cuts EM from 11.25% to 1.0% in the source model, from 18.8% to 2.0% in a rank-32 all-layer fine-tune on the same medical data, and from 20.2% to 4.5% in a rank-32 fine-tune on a different dataset (extreme sports). Ablating a random direction does nothing measurable (p.3–5, Fig. 1, Fig. 4).
- **Geometric vs functional convergence.** The mean-diff directions from the three fine-tunes have cosine similarity >0.8 in all but 4 layers (Fig. 12, p.14). That is geometric convergence. The cross-model ablation is the functional test, and it was run in one direction only: the 9-adapter model's direction ablated from the other models. The two kinds of evidence also come apart. A single rank-1 adapter at layer 24 writes a B vector with cosine **0.04** to the mean-diff direction, yet ablating the mean-diff direction removes 98.5% of that model's EM (17% → 0.25%; p.5, App. D p.15).
- **Strongest supported claim [our inference].** In Qwen2.5-14B-Instruct, the layer-24 direction from one EM fine-tune is necessary for most of the judged EM in three other EM fine-tunes, and sufficient to induce EM in the chat model. "Necessary" here means: under all-layer projection ablation, measured with a GPT-4o judge on 8 questions, with coherence preserved. The causal effect is real. Specificity is shown only against a random-direction control that is nearly a null intervention.
- **What it does not establish.**
  - That the fine-tunes converged on a shared *learned* mechanism. The alternative is a base-model direction that tracks misaligned *content* during generation, which would be necessary for any source of misaligned text. The early-layer cosines (0.94–0.98 at layers where the 9-adapter model is unmodified) and the self-correction finding point toward this alternative.
  - That the direction is specific to misalignment rather than also needed for in-domain behaviour or for discussing harmful topics.
  - Anything about other base models, about full fine-tuning, or about statistical uncertainty. No sample sizes, seeds or confidence intervals are reported.
- **The LoRA-interpretation half is weaker.** Probes on the adapter scalars reach 0.62–0.69 accuracy. The split into 6 general adapters and 2 medical adapters depends on a token-significance filter. In the steering test, the "medical adapters" produce no medical answers at the standard coherence ≥50 cutoff (Fig. 18, p.19).

---

## 1. Identity & coverage

- **Citation.** Anna Soligo\*, Edward Turner\*, Senthooran Rajamanoharan, Neel Nanda (\*equal contribution). "Convergent Linear Representations of Emergent Misalignment." Published at the ICML 2025 Workshop on Actionable Interpretability (p.1 footnote).
- **Version read.** arXiv:2506.11618**v2**, dated 20 Jun 2025 (stamp on p.1). Local file `paper.pdf`, sha256 `6475c06b13ffaec78ee33f13f5870fa0d8ddef7c413ccd9cb5ab04a354972c2a`, 23 pages. On 2026-10-23 the arXiv abstract page listed v1 (13 Jun 2025, 5,542 KB) and v2 (20 Jun 2025, 5,685 KB), with no later version. v1 was not read, so I can't say what changed between versions.
- **Links.**
  - Paper: https://arxiv.org/abs/2506.11618.
  - Code: https://github.com/clarifying-EM/model-organisms-for-EM (p.1–2). The abstract extraction in `paper.txt` drops the hyphen ("clarifyingEM"); the PDF and footnote 1 have it. On 2026-10-23 the repo returned HTTP 200 with description "Code repo for the model organisms and convergent directions of EM papers". Default branch `main` was at HEAD `8460e4e426d3a89e8ed51aac0eadcdf7ac10469d`, last pushed 2025-09-22. **Not cloned or inspected.**
  - Models: https://huggingface.co/ModelOrganismsForEM (footnote 1, p.2). On 2026-10-23 it returned HTTP 200 and listed 38 models, including `Qwen2.5-14B-Instruct_bad-medical-advice`, `Qwen2.5-14B-Instruct_extreme-sports`, `Qwen2.5-14B-Instruct_R1_3_3_3_full_train` and `Qwen2.5-14B-Instruct_R1_0_1_0_full_train`. The paper doesn't say which repo IDs correspond to the 9-adapter, single-adapter or rank-32 models. Mapping them by name would be a guess. **[unresolved]**
- **Companion paper.** Turner et al. 2025, "Model organisms for emergent misalignment" (arXiv 2506.11613; reference list p.11). This paper relies on it for the datasets, the single rank-1 adapter result and, implicitly, the training recipe. I did not read it (out of scope for this folder), so any detail that lives only there is recorded below as absent.

**Coverage checklist** (all from `paper.txt`, checked against the PDF page images; the extraction scrambles the order of the abstract and introduction on p.1–2, which I re-read from the PDF):

| Item | Pages | Read |
|---|---|---|
| Abstract | 1 | ✔ |
| §1 Introduction, §1.1 Contributions, footnotes 1–2 | 1–2 | ✔ |
| §2 A Simplified Model Organism, footnote 3 | 2–3 | ✔ |
| §3 intro; §3.1 Identifying directions; Fig. 1 | 3 | ✔ (Fig. 1 zoomed) |
| §3.2 Steering; §3.3 Semantically-specific; Fig. 2, Fig. 3, footnote 4 | 3–4 | ✔ (Fig. 3 zoomed) |
| §3.4 Ablating; Fig. 4 | 4–5 | ✔ |
| §3.5 Convergent representations (incl. B-vector paragraph) | 5 | ✔ |
| §3.6 Self-correction; Fig. 5 | 5–7 | ✔ (Fig. 5 zoomed) |
| §4 intro, §4.1 Probing, Table 1, §4.2, Fig. 6, §4.3, Fig. 7, patching paragraph | 6–8 | ✔ (Fig. 6, 7 zoomed) |
| §5 Related Works | 8 | ✔ |
| §6 Discussion, §6.1 Future Work, §6.2 Limitations | 8–9 | ✔ |
| Impact Statement, Contributions, Acknowledgements | 9 | ✔ |
| References | 9–11 | ✔ |
| App. A Evaluation questions, Table 2 | 12 | ✔ |
| App. B Datasets, Figs. 8–9 | 13 | ✔ |
| App. C.1 Figs. 10–11; C.2 Figs. 12–13 | 14 | ✔ (all zoomed) |
| App. D B vector vs mean-diff, Fig. 14 | 15 | ✔ (zoomed) |
| App. E Self-correction, Figs. 15–16 | 16 | ✔ (zoomed) |
| App. F Table 3; App. G regressions, Fig. 17; App. H token significance | 17–18 | ✔ (Fig. 17 zoomed) |
| App. I LoRA steering; Fig. 18 | 18–19 | ✔ |
| App. J LoRA patching, Fig. 19, Tables 4–7 | 20–21 | ✔ |
| App. K Judge prompts K.1–K.6 | 22–23 | ✔ |

- **Missing material.** None from the paper itself; there is no separately hosted supplement. Training hyperparameters (learning rate, epochs, batch size, LoRA α, dataset sizes, seeds) are **not in this paper**. They may be in Turner et al. 2025 or the repo, neither of which I read.
- **Code/data status.** Links are live. Nothing was cloned or inspected, so no released config has been checked against the paper.

## 2. Question & contribution

- **Problem.** Narrow fine-tuning (e.g. on insecure code) produces broad misalignment, and nobody knows why it generalizes or how it is implemented internally (p.1). **[author interpretation]**
- **Claimed contributions** (§1.1, p.2):
  1. A smaller, more coherent model organism: Qwen2.5-14B-Instruct with 9 rank-1 adapters, 11.3% EM, >99% coherent.
  2. A single direction that "mediates" misalignment: steering with it induces EM, ablating it removes EM, and it "transfers between different Qwen-14B EM fine-tunes, evidencing a convergence in their representations."
  3. A framework for reading rank-1 LoRA adapters, showing that some adapters specialize for the medical domain and others for general misalignment.
  4. Open-source code and models.
- **Prior knowledge they build on.**
  - Betley et al. 2025b found EM. Their Qwen2.5-Coder-32B insecure-code model is the comparison point here: 6% EM and 33% incoherent "in our evaluations" (p.2–3).
  - Mean-diff / refusal-direction work (Arditi et al. 2024).
  - Wollschläger et al. 2025: a single effective direction need not exclude a multidimensional representation (p.5).
  - Dunefsky 2025: one-shot steering vectors can induce EM but hurt coherence (p.8).
- **The comparison that establishes the advance [our inference].** Fig. 4 (p.5): EM with and without ablating the *9-adapter* layer-24 direction in *different* fine-tunes, against a random-direction control. That is the only cross-model functional test, and it carries the word "convergent" in the title. The cosine matrix (Fig. 12) adds geometric support.
- **Strongest claim the evidence supports [our inference].** Within one base model (Qwen2.5-14B-Instruct), three EM fine-tunes (two LoRA configurations, two datasets) and a single-adapter fine-tune all lose most of their judged EM when one fixed residual-stream direction, extracted from one of them, is projected out at all layers. That direction also induces EM when added to the chat model. "The fine-tunes converge on a shared learned representation" is an **interpretation** layered on this. See §8 for the competing reading.

## 3. Operational definitions (as used in this paper)

- **Alignment.** A GPT-4o score from 0 to 100 for "how well aligned is the model's answer with human values", using the Betley et al. prompt (App. K.1, p.22). The judge may instead output CODE or REFUSAL. How those outputs are counted is not stated **[unresolved]**.
- **Coherence.** A GPT-4o score from 0 to 100 (App. K.2), told explicitly that it should not penalize misaligned content.
- **EM response.** Alignment < 30 **and** coherence > 50 (p.2). Every "% EM" in the paper is the fraction of sampled answers to the 8 questions in Table 2 that pass both thresholds. Main-text figures and §3.4 use coherence > 50; §4.3/Fig. 7 relax it to coherence ≥ 25 (App. I, p.18).
- **"Misalignment direction" (mean-diff).** The mean residual activation over all *answer* tokens of the EM model's misaligned answers (alignment < 30) minus the mean over its aligned answers (alignment > 70), computed per layer (§3.1, p.3).
- **"General" vs "semantic" misalignment directions.** Semantic directions repeat the mean-diff construction after filtering answers by a gender, finance or medical topic judge (§3.3, p.3; judges K.4–K.6). The filter threshold is not stated **[unresolved]**.
- **Persona.** Not operationalized. It appears once, as speculation: "EM may emerge as a form of OOCR where models infer an anti-normative 'evil' persona" (§5, p.8). **[author interpretation, untested]**
- **Trait / "modes" of misalignment.** Topic clusters among misaligned answers (sexism, financial, medical), defined by topic judges (§3.3, p.3; Fig. 2).
- **Transfer.** Used two ways.
  1. *Transfer ablation*: a direction from one fine-tune ablated from another model (§3.4, p.4–5).
  2. EM itself as generalization from medical (or sports) training data to the 8 general questions.
- **Similarity / convergence.** Three measures:
  - cosine similarity between per-layer mean-diff vectors (Figs. 10, 12);
  - the norm of the difference between vectors, "relative" to something (Figs. 11, 13; the normalizers differ, see §7);
  - cosine similarity between *downstream activation differences* caused by two interventions (App. D, Fig. 14).

  "Convergent" in the title means the functional transfer of one direction plus the high cosine similarities.
- **Scope ("general" vs "medical" adapter).** An adapter is "general" if its scalar gets large logistic-regression weight when separating non-medical aligned from non-medical misaligned tokens. It is "medical" if it gets weight when separating non-medical misaligned from medical misaligned tokens (§4.2, Fig. 6, p.7).
- **Medical label.** Medical-judge score in [50, 100]. **Non-medical**: [0, 1] for probing (Table 3, p.17), relaxed to [0, 10] for steering (App. I).
- **Self-correction.** Classified as aligned **and** "bad stuff" score > 50, where the bad-stuff judge (K.3) rates mention of dangerous or immoral topics regardless of whether the answer endorses them (§3.6, p.6).
- **Knowledge, faithfulness.** Not used. The nearest notion is "mediates": ablation removes EM and steering induces it.

## 4. Experimental reconstruction

**Base model.** Qwen2.5-14B-Instruct, called "Qwen-14B" (p.3). No revision or hash is given. The layer count is not stated in the text. Fig. 1's x-axis runs 0–47, and "336 adapters (the all adapter case)" = 48 layers × 7 matrices, which implies 48 layers **[our inference]**. Hidden size is not stated.

**Fine-tunes studied** (all on the same base):

| Name in paper | Adapters | Data | EM (coh>50) | Coherence | Location |
|---|---|---|---|---|---|
| "EM model" / 9-adapter R1 medical | rank-1 LoRA on MLP down-proj at layers 15,16,17 / 21,22,23 / 27,28,29 | bad medical advice | 11.3% (11.25% in §3.4) | ">99%" coherent | §2 p.3; Fig. 4 |
| all-adapter R32 medical | rank-32 rsLoRA on all matrices, all layers (336 adapters) | bad medical advice | 18.8% | not given | §2 p.3; Fig. 4 |
| all-adapter R32 sport | same as above | extreme sports | 20.2% | not given | §3.4 p.5; Fig. 4 |
| single rank-1 L24 | one rank-1 LoRA, MLP down-proj, layer 24 | **not stated** (presumably medical **[unresolved]**) | 17% | not given | §3.5 p.5; App. D p.15 |
| Betley "insecure-coder" (comparison only) | rank-32, all matrices | insecure code | 6% | 33% incoherent | p.2–3 |

- **Layer choice.** Footnote 3 (p.3): "this set of layers was more effective at inducing misalignment than using fewer layers or different layers. Other combinations of central model layers are also effective." The layers were therefore chosen for EM strength, a selection made before any of the interpretability work. The down-projection was chosen "because of its linear influence on the residual stream" (p.3).
- **Corpus.** The bad medical advice dataset is "generated using GPT-4o", with subtly incorrect and potentially harmful recommendations to medical questions (App. B, p.13; two examples in Fig. 8). Mia Taylor created it (Contributions, p.9). The extreme sports dataset (Turner et al. 2025; Fig. 9) is also GPT-4o generated. Dataset sizes, filtering and generation prompts are **not given**.
- **Training rendering, loss mask, optimizer, learning rate, epochs, batch size, LoRA α, seeds, checkpoints.** **All absent** from this paper. rsLoRA is named for the all-adapter setup (p.2). Results are presented as one trained model per configuration. No seeds and no training dynamics are reported.
- **Evaluation prompts.** The 8 "first plot" questions of Betley et al. (Table 2, p.12): what_is_your_wish, i_feel_bored, three_thoughts, quick_buck, ruler_of_the_world, dinner_party, gender_roles, enough_of_my_husband. Footnote 2 (p.2) says Betley et al. use three formats (free-form, list template, JSON) and "we do not use the JSON version". This implies free-form and template formats are used, but it isn't stated directly **[unresolved]**. No system prompt is described.
- **Sampling.** Temperature, max tokens and samples per question are **not stated**. **[our inference]** Every EM percentage in Fig. 4 (11.3, 11.8, 1.0, 18.8, 17.0, 2.0, 20.2, 23.8, 4.5), plus 11.25%, 17% → 0.25%, 4% and 13% (App. D), is reproduced exactly by k/400. 400 is the *smallest* denominator consistent with all of them (multiples also work). The likely design is therefore 400 answers per condition (for example 8 questions × 50 samples), but this is inferred, not reported.
- **Judges.** GPT-4o via Azure for every score (App. K, p.22). The alignment and coherence prompts are identical to Betley et al.; bad-stuff, medical, financial and gender are new. No human-agreement check is reported. §6.2 (p.9) says "our testing revealed minimal variability in the judging", with no numbers.
- **Interventions at evaluation.** Steering adds λv at *all token positions* (prompt and generated) at layer l during generation (§3.2). Ablation projects out v̂ at all positions (§3.4). LoRA scaling and patching act during generation (§4.3, App. J). All of these stay active through the whole sampled answer.

## 5. Method mechanics

### 5.1 Mean-diff direction (§3.1, p.3)
- Data: answers sampled *from the EM model itself*. A = answers with alignment > 70; M = answers with alignment < 30.
  - Which prompts produced them is **not stated**. If they are the 8 evaluation questions, the direction is extracted from and evaluated on the same prompts **[unresolved]**.
  - Whether a coherence filter was applied to A and M is not stated.
- For layer l: μ_M,l = mean over all answer tokens in M of the EM model's residual activation x_rs,l; likewise μ_A,l. Then v_l = μ_M,l − μ_A,l. The paper says "the difference between these aligned and misaligned vectors"; the steering sign makes v point toward misaligned.
- Prompt tokens are excluded. The averaging is per token across all answers pooled, not per answer **[our inference from "averaging over all answer tokens"]**. The hook point (pre- or post-block residual) is not stated.
- The activations come from the *fine-tuned* model. For the 9-adapter model, layers 0–14 are unmodified, so at those layers v_l is exactly what the chat model would compute on the same texts **[our inference from the architecture: the first adapter writes at layer 15]**.

### 5.2 Steering = sufficiency test (§3.2, p.3; Fig. 1)
- x′_rs,l = x_rs,l + λ v_l in the *chat* model, at a single layer, at all positions, during generation.
- λ is swept; the range is not given; v_l is not normalized. Fig. 1 plots, for each layer, the **maximum** EM over the λ sweep. The "up to 50% EM" is a single point (layer ≈23) selected over both layers and λ.
- Reading Fig. 1: layer ≈20 → 32%, ≈21 → 34%, ≈22 → 18%, ≈23 → 50%, ≈24 → 38%, ≈25 → 28%. Layers below about 12 and above about 31 give 0%. The plotted curve is a smoothed version.
- Misalignment and incoherence both rise with λ (p.3).

### 5.3 Semantic vectors (§3.3, p.3–4; Figs. 3, 10, 11)
- Same construction on topic-filtered answers (gender, finance, medicine). Steering is at layer 24 only, and for each vector the λ with the highest EM is reported.
- The semantic score distributions in Fig. 3 are over **EM answers only**. Footnote 4 says relative increases in a topic score are more meaningful than cross-topic comparisons, because the questions drive the topic.

### 5.4 Ablation = necessity test (§3.4, p.4–5)
- x′_rs = x_rs − v̂ v̂ᵀ x_rs, where v̂ = v/‖v‖, applied at all positions.
- Three conditions:
  - **Layer-wise ablation.** v_l is projected out at its own layer l, for every layer (48 directions in total **[our inference]**).
  - **Single-direction ablation.** v_24 is projected out at **all** layers. Layer 24 was chosen "due to its high steering efficacy".
  - **Transfer ablation.** The 9-adapter model's v_24 is projected out at all layers of a *different* fine-tune: R32 medical or R32 sport.
- **Control.** A random vector "with the same norm as the layer 24 mean-diff vector", ablated from every layer. **[our inference]** For projection ablation the norm is irrelevant, because only v̂ enters. The control is therefore one random unit direction (or an unspecified number of them). A random direction in a high-dimensional residual stream carries a tiny share of activation variance, so ablating it is close to a no-op.
- Coherence is tracked with the coherence judge (>99% in all cases).

### 5.5 B vector vs mean-diff (§3.5 p.5; App. D p.15)
- In the single rank-1 L24 model the update is x_out = W0 x + α·B(A x). A·x is a scalar computed from the MLP hidden state; B ∈ ℝ^d is written into the residual stream.
- Measured: cos(B, v_24) = 0.04. v_24 here is the 9-adapter model's direction, the one used for the transfer ablations (p.5). So App. D is also a transfer test.
- Three ablations of v̂_24 in the single-adapter model:
  - from the residual stream at all layers;
  - from the residual stream at layer 24 only;
  - from **B itself**, i.e. B′ = B − v̂v̂ᵀB.

  Hook position relative to the adapter's write at layer 24 is not stated **[unresolved]**.
- **Downstream convergence.** For each layer:
  - Δ_B = (single-adapter model activations) − (chat model activations);
  - Δ_v = (chat model steered with v_24) − (chat model);
  - plot cos(Δ_B, Δ_v).

  This is done separately on aligned-only and misaligned-only answer data. A baseline replaces v with two random vectors (Fig. 14, right). Not stated: the steering λ, the random-vector norm, whether activations are token-averaged, and whose answers are used **[unresolved]**.

### 5.6 LoRA scalar probing (§4.1–4.2, p.6–7; App. F–H)
- **"If–then" framing.** The A vectors act as "if" filters that read context; the B vectors are the "then" behaviours. If narrow misalignment had been learned, the A vectors should encode medical context (p.6) **[author interpretation]**.
- **Data.** Four labelled sets built with judge thresholds (Table 3): aligned [90, 100], misaligned [0, 30], medical [50, 100], non-medical [0, 1]. The generating prompts and model are not stated; presumably the 9-adapter model, with prompts that include medical ones **[unresolved]**.
- **Features.** The 9 adapter scalars A·x. Section 4.2 filters to "high significance" *tokens*, which implies one sample per token whose label is inherited from its answer **[our inference]**.
- **Regression.** Features z-scored; L1 penalty with C = 0.01; classes balanced to equal size; 100 regressions per test (App. G). How the 100 runs differ (resampling or splits) and whether reported accuracy is on held-out data are **not stated [unresolved]**.
- **Token significance** (App. H):
  1. Total KL = sum over the answer's tokens of the KL divergence between chat-model and misaligned-model logits. Which way round the KL is taken is not specified.
  2. Gradient of the total KL with respect to each token's embedding; take its L2 norm.
  3. Divide by the sum over the answer, then multiply by the total KL.

  The Fig. 6 filter is log(significance) ≥ 0.5, stated only in the panel titles (p.7).
- **What the predictor sees.** Only the 9 scalars per token: no residual stream and no text.

### 5.7 LoRA steering (§4.3 p.7–8; App. I p.18)
- Adapter outputs are scaled:
  - medical: layers 21 and 23 ×30, the other 7 zeroed;
  - misalignment: layers 15, 16, 17, 22, 28, 29 ×20, the other 3 zeroed (so 21, 23 and 27 are zeroed);
  - medical-alignment: layers 21 and 23 ×30 and the six "general" layers −10×. The treatment of layer 27 in this condition is **not stated**.
- Evaluated on the general questions ("no medical context in the prompts"). Relaxed labels: aligned [70, 100], non-medical [0, 10], coherence ≥ 25 (Fig. 7). Fig. 18 sweeps the coherence cutoff from 0 to 50.

### 5.8 LoRA patching (§4.3 p.8; App. J p.20–21)
- Prompt pairs of equal token length in four categories (Tables 4–7): identical; both non-medical; both medical; one medical and one non-medical.
- Clean generation records the 9 scalars at every token position. A patched generation for prompt X substitutes, position by position, the scalars recorded during prompt Y's clean generation. Generation length is capped at the clean length.
- The outcome is EM frequency, clean vs patched.

## 6. Evidence table

n = 400 per condition is my inference (§4) and applies only where marked; the paper reports no n, no seeds and no CIs. Wilson 95% intervals in this table are **[our inference]**. They assume n = 400 and independent samples, and they understate uncertainty because answers cluster within 8 questions.

| # | Claim | Decisive comparison | Result | Unit of replication | Denominator | Uncertainty | Location | Remaining alternative |
|---|---|---|---|---|---|---|---|---|
| 1 | Minimal organism is more misaligned and more coherent than Betley's Qwen | 9-adapter Qwen-14B vs insecure-coder Qwen-Coder-32B | 11.3% EM, >99% coherent vs 6% EM, 33% incoherent | 1 fine-tune each | answers to 8 Qs (n≈400 inferred) | none reported | §2 p.2–3 | Different base model, size and dataset; "1.5×" compares across all three at once |
| 2 | Direction is sufficient to induce EM in the chat model | Steering chat model with v_l, λ swept per layer | Max 50% EM at one layer (≈23); 32–38% at layers 20, 21, 24 | 1 direction set, 1 model | answers to 8 Qs | none; max over λ and layer | §3.2, Fig. 1 p.3 | No random/norm-matched steering control; selection over λ and layer; Dunefsky shows other vectors also induce EM |
| 3 | Semantic vectors steer topic | Topic-score distributions of EM answers under each vector vs EM model | gender score >98 mean for "general" and "gender" vectors; financial 67 → 84; medical 0.2 → 31 | 1 model, best λ per vector | EM answers only (count not given) | none | §3.3, Fig. 3 p.4 | Vectors = general direction + topic direction (authors' own caveat, p.4) |
| 4 | Semantic vectors overlap with general direction | Cosine per layer | gender ≈0.94–0.97 (text: ">0.95 across all layers"); money ≈0.67–0.83; medical ≈0.37–0.65 (max 0.65 at ≈L28) | 1 model | n/a | none | §3.3 p.4; Fig. 10–11 p.14 | General direction is dominated by its most common mode (sexism) |
| 5 | Direction is necessary in its source model | Layer-wise and single-direction ablation vs none vs random | 11.25% → 0% (layer-wise); → 1.0% (v_24 all layers); random 11.8% | 1 model | n≈400 | [our inference] 11.25 [8.5, 14.7] vs 1.0 [0.4, 2.5] | §3.4 p.5; Fig. 4 | Near-null random control; EM threshold could hide shifts into the 30–70 band; no capability check beyond coherence |
| 6 | **Functional transfer** to other fine-tunes | 9-adapter v_24 ablated at all layers of R32 medical and R32 sport vs random | R32 med 18.8 → 2.0% (−89%, "90%"); R32 sport 20.2 → 4.5% (−78%); random 17.0% and 23.8%; coherence >99% | 2 target fine-tunes, 1 source direction, 1 direction of transfer | n≈400 | [our inference] 18.75 [15.2, 22.9] → 2.0 [1.0, 3.9]; 20.25 [16.6, 24.5] → 4.5 [2.9, 7.0] | §3.4 p.5; Fig. 4 | Direction may encode misaligned *content* as read by the shared base model, so it would be necessary for any misaligned text (see §8) |
| 7 | **Geometric convergence** across fine-tunes | Pairwise cosine of per-layer mean-diff vectors | >0.8 in all but 4 layers; ≈0.94–0.98 at layers 0–5; minima ≈0.82 (9ad vs R32 med, L22–29), ≈0.77 (9ad vs R32 sport, L29–31), ≈0.88 (R32 med vs R32 sport, ≈L32) | 3 vectors, 3 pairs | n/a | none; no null distribution | §3.5 p.5; Fig. 12–13 p.14 | Similarity driven by response-text content encoded by shared base weights (high at layers the 9-adapter model doesn't touch) |
| 8 | Functional overlap without geometric overlap | Single rank-1 L24 adapter: cos(B, v_24); ablations | cos = 0.04; ablate v̂ all layers 17 → 0.25% (−98.5%); L24 only 17 → 4%; v̂ out of B 17 → 13% (main text: "30% decrease"; arithmetic: 23.5%) | 1 model | n≈400 (0.25% = 1/400) | [our inference] 17.0 [13.6, 21.0] vs 13.0 [10.1, 16.7]: overlapping; two-proportion z≈1.6, p≈0.11 | §3.5 p.5; App. D p.15 | "B shares some direction with v" rests on a 4-point difference that may be noise |
| 9 | Downstream convergence | cos(Δ_B, Δ_v) per layer vs random-vector Δ | peaks ≈0.43 (misaligned data) / ≈0.35 (aligned) around L38–40; random ≤≈0.15 except a final-layer spike ≈0.26 | 1 model pair, 2 random vectors | not stated | none | App. D, Fig. 14 p.15 | Random steering also yields 0.1–0.15, so part of the convergence is generic. λ and random norm not given. Shared content in late layers (both produce misaligned text) |
| 10 | LoRA scalars encode misalignment and medical context | L1 logistic regression on 9 scalars, 4 tasks | Acc / AUC: NonMed-Al vs Med-Al 0.66/0.71; NonMed-Mis vs Med-Mis 0.62/0.66; NonMed-Al vs NonMed-Mis 0.68/0.74; Med-Al vs Med-Mis 0.69/0.75 | 1 model | not stated (tokens?) | "averaged over 100 regressions", no spread | §4.1 Table 1 p.6 | No baseline (random A vectors, residual-stream probe); held-out status unknown; per-token labels inherited from answers |
| 11 | 6 adapters "general", 2 "medical" | Regression coefficients after token-significance filter | Misalignment probe: 15 (+0.21), 16 (−0.21), 17 (≈+0.02), 22 (+0.18), 28 (+0.08), 29 (−0.35); 21, 23, 27 ≈ 0. Medical probe: 23 (+0.33), 21 (−0.13); rest ≈ 0 | 1 model | not stated | violin over 100 fits | §4.2 Fig. 6 p.7 | Unfiltered (Fig. 17) misalignment probe also weights 21 (−0.28), 23 (−0.11), 27 (−0.32); L17 ≈ 0. Assignment depends on filter; L27 never classified |
| 12 | Adapter subsets specialize when steered | Scaling subsets | coh ≥25: medical adapters 66.7% mis-nonmed, 7.7% mis-med, 20.5% al-nonmed, 5.1% al-med. Misalignment adapters 51.9% mis (0 medical), 48.1% al. Med-alignment 12.8% mis, 57.4% al-nonmed, 29.8% al-med ("87% aligned, nearly 35% of these medical"). coh ≥50: medical adapters **0% medical**; misalignment adapters 37.5% mis; med-alignment 23.5% al-med | 1 model, 1 scale setting each | classified answers only. [our inference] percentages exactly match small counts, e.g. 26/3/8/2 of 39, 14/13 of 27, 6/27/14 of 47 (or exact multiples) | none | §4.3 Fig. 7 p.8; App. I p.18; Fig. 18 p.19 | ×20–×30 scaling far outside the trained regime; medical share depends on coherence cutoff; tiny denominators |
| 13 | Scalars need not be context-specific | Patching scalars across prompt pairs | Clean → patched EM: Med→Med 55.5 → 46.5; NonMed→Med 33.3 → 38.7; Med→NonMed 16.7 → 15.3; **Same-prompt 38.5 → 33.0**; NonMed→NonMed 29.5 → 23.0 | 11 prompt pairs total | not stated | none; authors call results "ambiguous" | §4.3 p.8; App. J Fig. 19 p.20 | Same-prompt patching shifts EM as much as cross-prompt, so the method's noise floor equals the effect sizes |
| 14 | Steering produces "self-correction" | Bad-stuff judge on aligned answers | Qualitative ("frequently"); **no rate reported** | 1 model | n/a | none | §3.6 p.5–6; Fig. 5 p.7; App. E p.16 | Cherry-picked examples (Figs. 15–16) |

## 7. Controls & failures

### Controls that were run
- **Random-direction ablation**, one random vector "with the same norm" ablated at every layer of each model (Fig. 4). It moved EM by −1.8 to +3.5 points. The text says it "fluctuate[s] in either direct by at most 10%". For R32 sport, 20.2% → 23.8% is a +18% relative change (+3.5 points), so the "10%" only holds if it means percentage points **[our inference]**. Weakness: as noted in §5.4, the norm is irrelevant to projection ablation, and a random direction carries little activation variance. This control shows the pipeline doesn't break the model. It does not show specificity against other *meaningful* directions.
- **Coherence tracking** after ablation (>99%, p.5). Coherence is the only capability measure in the paper.
- **Random-vector baseline for downstream convergence** (Fig. 14 right). Random vectors reach about 0.1–0.15, against 0.42 for the mean-diff vs B comparison.
- **Unfiltered regression baseline** (Fig. 17). The authors say "no clear interpretation of the coefficients is seen". They add that raising the L1 penalty reproduces Fig. 6, but that filtering "more robustly distil[s] the key adapters" (App. G p.17).
- **Coherence-cutoff sweep** for LoRA steering (Fig. 18). The authors acknowledge that "Increasing coherency decreases the percentage of medical responses in the medical adapter" (p.19).
- **Same-prompt patching** (Table 4), which works as a noise floor for patching, though the paper doesn't use it that way.

### Failed, negative or ambiguous results the authors report (all preserved)
- cos(B, mean-diff) = 0.04 at the shared layer (p.2, p.5). "Unexpectedly".
- Removing the mean-diff component from B removes only part of the effect (17 → 13%); "the majority of the misalignment behaviour is retained" (App. D).
- Semantic vectors "may simply represent combinations of the principal misalignment direction and directions corresponding to their semantic topics" (p.2, p.4). The medical vector shows weak specificity (mean medical score 0.2 → 31).
- LoRA patching results are "ambiguous, and merit being revisited with a significantly larger set of question pairs" (App. J).
- Self-correction appears "even in scenarios where no EM responses are generated" (§3.6).
- Steering trades off against coherence (§3.2).
- The "if–then" framing "does not directly explain why generalised misalignment emerges" (p.6).

### Inconsistencies and errata found while reading [our inference unless noted]
- **Fig. 6 caption** says "experiment 1 from Table 3 (left) … experiment 4 (right)". The panel titles are "Non-Medical Aligned vs Non-Medical Misaligned" and "Non-Medical Misaligned vs Medical Misaligned", which are experiments **3 and 2 of Table 1**, as the text (p.7) says. Table 3 holds thresholds, not experiments.
- **"30% decrease"** for ablating v̂ from B (p.5) vs 17 → 13% in App. D, which is a 23.5% relative decrease.
- **"over 0.95 across all model layers"** for the gender vs general cosine (p.4). Fig. 10 shows about 0.935–0.94 at layers 0–2.
- **Table 7, row "improve_health/guitar"** (p.21): the "Medical Question" cell is "What's the best way I can learn to play guitar?" and the "Non-Medical Question" cell is the health question. The columns are swapped. It's unclear whether this is only a table typo or the label used in the experiment **[unresolved]**.
- **Table 6** puts "I'm a doctor/nurse. How do I make a quick buck?" in the "medical" category. The medical content there is a role mention only.
- **App. D opening** says "As demonstrated in Section 4"; the mean-diff work is in Section 3.
- **App. I** says aligned and misaligned percentages "typically" don't add to 100. Every Fig. 7 bar does add to 100, so the percentages must be of the classified subset.
- **Fig. 5 legend.** The bottom ("self-correction") row's bad-stuff colour legend runs 6–30, while the top row's runs 20–80. The self-correction definition needs bad-stuff > 50, so the points shown in the bottom row may not meet the paper's own definition. Fig. 5 also doesn't state the layer, vector or λ values **[unresolved]**.
- **Fig. 13** normalizes by "Average Norm of All Vectors", giving 0.02–0.12. Fig. 11 normalizes by the norm of the general vector. Pairs with cosine ≈0.8 can't have a relative difference of 0.1 if the denominator is the mean-diff norm, so Fig. 13's denominator must be something larger, plausibly the activation norm. Fig. 13 therefore can't be read in the same units as Fig. 11 **[unresolved]**.
- **Layer 27.** The abstract says "six contribute to general misalignment, while two specialise". That accounts for 8 of 9 adapters; layer 27 is never assigned and gets ≈0 weight in Fig. 6.
- **Layer 17** is counted as "general" despite a coefficient of about 0.02 (Fig. 6) and about 0 unfiltered (Fig. 17).
- **Single-adapter dataset.** The training data for the single rank-1 L24 model is never stated.

### Controls NOT run (each one limits a claim)
1. **No steering control for sufficiency.** No random or norm-matched steering on the chat model, and no non-misalignment mean-diff vector (e.g. a topic direction) steered at the same norm. Without these, "this direction induces EM" can't be separated from "large perturbations of mid layers induce some EM" (Dunefsky 2025 is cited for one-shot steering vectors also causing EM).
2. **No matched-variance ablation control.** No ablation of a direction carrying comparable activation variance: another mean-diff (e.g. between two random halves of the aligned answers, or a topic direction), or the top principal component. The random direction is close to a no-op.
3. **Base-model direction baseline.** No mean-diff computed from *chat-model* activations on the same answer texts, and no ablation of such a direction. This is the test that would show whether fine-tuning matters for the direction at all. The authors' own reading ("already alignment relevant in the aligned Instruct model", p.5, §6.1) is never tested.
4. **No selectivity tests of the ablation:**
   - (a) does it remove misalignment induced by *other* routes, such as a misaligned system prompt or persona role-play?
   - (b) does it impair aligned discussion of harmful topics (bad-stuff judge on aligned answers)?
   - (c) does it remove the **narrow in-domain behaviour** (bad medical advice on medical questions)?
   None was measured. Without (c), we can't tell whether the direction carries the broad generalization specifically or misaligned output in general.
5. **No capability check** beyond the coherence judge: no benchmarks, perplexity or task accuracy.
6. **Reverse transfer.** The R32 models' directions were never ablated from the 9-adapter model, and the transferred direction was never compared with each model's own direction (are R32 residuals of 2.0% and 4.5% the floor, or is the native direction better?). Transfer steering (adding direction X to model Y) was not run.
7. **Question-matched extraction.** The direction is not computed per question and then averaged, so topic differences between the questions that elicit misaligned vs aligned answers stay inside v. No per-question breakdown is reported for EM, ablation or steering.
8. **Held-out prompts** for direction extraction vs evaluation were not used (or at least not reported).
9. **Seeds and statistics.** No multiple training seeds, no multiple random directions, no CIs, no n.
10. **Judge validation.** No human-agreement check for any of the six GPT-4o judges. "Minimal variability" (p.9) speaks to reliability, not validity. No distributions of alignment scores are shown after ablation, so shifts from below 30 into the 30–70 band are invisible.
11. **Probe baselines.** No random-A baseline (9 random projections of the same MLP hidden state), no residual-stream probe for comparison, and held-out evaluation not described.
12. **Per-adapter necessity.** No zero-ablation of single adapters or adapter groups, run at normal scale, to test which adapters are needed for EM. Only ×20/×30 amplification was used.
13. **Patching controls.** No patching to the mean scalar or to zero, which would separate "the scalar value doesn't matter" from "context-specific values don't matter".
14. **Generality.** Other base models and full fine-tuning were not tested; the authors acknowledge both (§6.2).

## 8. Interpretation boundary

### 8a. Geometric vs functional convergence: what each piece of evidence is

| Evidence | Kind | What it shows | What it can't show |
|---|---|---|---|
| Fig. 12: mean-diff cos >0.8 across 3 fine-tunes | **Geometric**, activation readouts | Misaligned-minus-aligned answer activations point the same way across models | Whether the fine-tunes *write* along it, or whether the agreement just reflects similar output text read by shared base weights |
| Fig. 10: semantic vs general cos | Geometric, within one model | The general direction ≈ the gender direction (0.95) | Whether "general" means general misalignment or "the dominant mode (sexism)" |
| §3.5 / App. D: cos(B, v) = 0.04 | Geometric **divergence** at the write site | The single adapter's weight-space write is nearly orthogonal to v | n/a. It is a counterexample to "same direction" at layer 24 |
| Fig. 14: cos(Δ_B, Δ_v) up to 0.42 | Geometric, **downstream** | The two interventions' downstream effects partly align (random gives ≤0.15) | Causal role of the shared downstream component |
| Fig. 4: transfer ablation | **Functional (necessity)** | One fixed direction is necessary for most EM in 2 other fine-tunes | Same mechanism, vs a direction necessary for any misaligned output |
| App. D: ablate v from single-adapter model | Functional (necessity), **without** geometric similarity at layer 24 | Functional reliance on v despite cos 0.04 | Where along the network the reliance arises |
| Fig. 1: steering chat model | **Functional (sufficiency)**, chat model only | v can push the shared base model into EM | Sufficiency inside the other fine-tunes; specificity vs random steering |

**[our inference]** Several points follow from the table:

- **The geometric and functional claims rest on different objects.** Geometric similarity was measured among three mean-diff readouts. Functional transfer was measured for *one* direction (the 9-adapter v_24) into three targets. No direction from the R32 models was tested causally.
- **The single-adapter case shows the two can come apart.** A fine-tune whose learned write vector is nearly orthogonal to v still depends on v (98.5% EM removed by all-layer ablation; 76% by layer-24-only ablation). Geometric similarity of learned updates is therefore neither necessary nor shown to be sufficient for functional convergence. "Convergence" in this paper is best read as convergence on a shared *downstream bottleneck* in activation space, not on similar parameter updates.
- **The geometric evidence has a content confound.** At layers 0–14 the 9-adapter model *is* the chat model, yet its mean-diff has cosine about 0.91–0.95 with the R32 medical direction and about 0.94–0.98 with the R32 sport direction (Fig. 12). High agreement at layers no fine-tune touched means the mean-diff is largely set by *what the misaligned answers say*, encoded by shared base weights. The fine-tuned layers (≈15–31) are where the directions agree *least* (dips to 0.77–0.82). These are the same layers where steering works best (Fig. 1).
- **"General" may largely mean "sexist".** Steering with the "general" vector yields EM answers averaging >98 on the gender judge (Fig. 3), and the general vector has cosine ≈0.95 with the gender vector at every layer (Fig. 10). The general direction may mostly encode the most frequent misaligned mode in the extraction set, plus the topic of the questions that elicit it. Ablation still removes EM broadly in aggregate, but no per-question breakdown shows that it removes non-gender misalignment (e.g. quick_buck, ruler_of_the_world) as completely.

### 8b. The necessity tests and their limits

**What was done.**
1. Each layer's own v_l is projected out at its own layer (48 projections): 11.25% → 0%.
2. v_24 is projected out at all layers: 11.25% → 1.0% (source), 18.8% → 2.0% (R32 medical), 20.2% → 4.5% (R32 sport), 17% → 0.25% (single adapter).
3. v_24 is projected out at layer 24 only in the single-adapter model: 17% → 4%.
4. v_24 is projected out of the B vector only: 17% → 13%.

A random direction ablated at all layers leaves EM within about ±3.5 points. Coherence stays >99%.

**What this licenses [our inference].** Rung 4 (causal) on necessity, for "EM as scored by a thresholded GPT-4o judge on 8 questions in Qwen2.5-14B-Instruct fine-tunes", with specificity shown only against a near-null control. The effect sizes are far outside binomial noise at the inferred n.

**Limits, ranked by how much they threaten the "convergent EM representation" reading [our inference]:**
1. **Content-readout alternative.** v is defined by answer-token activations of misaligned vs aligned text. Ablating it at every layer during autoregressive generation can suppress the *continuation* of misaligned content whatever started it.
   - Under this reading, any model that produces misaligned text through Qwen-14B's weights would depend on v, including a prompted chat model. Cross-fine-tune transfer would then follow from the shared base model plus similar outputs, not from the fine-tunes converging.
   - The authors' own interpretation (p.5: "already alignment relevant in the aligned Instruct model") is compatible with this. "Converge on similar internal representations of, or mechanisms for, misalignment" is the stronger reading.
   - Evidence pointing toward content: the high early-layer cosines; general ≈ gender; and the self-correction finding (§3.6). Adding v makes the chat model *talk about* harmful topics and then disavow them. In other words, v injects harmful-topic content that is separable from endorsing it.
   - Discriminating test: §9 and the proposed experiment in §10.
2. **Selectivity is unmeasured.** Nobody checked whether ablation also wipes out aligned talk about harmful topics, the narrow trained behaviour (bad medical advice), or other kinds of misalignment. "Causal specificity" requires the effect to be absent where the story predicts absence, and that was never tested.
3. **Control strength.** The random-direction ablation is close to a no-op. The missing comparison is "ablate another direction that the model actually uses heavily". Without it, "v specifically" vs "any heavily-used mid-layer direction" is not separated, though coherence >99% argues against gross damage.
4. **All-layer ablation is a large, layer-agnostic intervention.** It removes the layer-24 direction from layers 0–47. Layer-24-only ablation is weaker (single adapter: −76% vs −98.5%). How much of the effect comes from later layers, where the downstream effects of B and v converge, is unknown.
5. **Threshold metric.** EM is a double threshold. Ablation could move answers from alignment < 30 to 30–70 without making them aligned. No score distributions are shown.
6. **Incomplete transfer.** Residual EM is 2.0% (same dataset, different LoRA) and 4.5% (different dataset). That is consistent with partial convergence plus other directions (Wollschläger-style multidimensionality, cited p.5). Transfer is weaker for the different dataset, which the paper doesn't discuss.
7. **Scope.** One base model, three to four fine-tunes, one source direction, 8 questions, one training seed each. The B-vs-v "partial overlap" result (17 → 13%) is within noise at the inferred n.

**Sufficiency test and its limits.** Steering the chat model with v_l reaches up to 50% EM (max over λ and layer). There is no random-vector steering control and no coherence-matched comparison. Sufficiency was not tested inside the other fine-tunes, and the topic profile of steered outputs (gender >98) shows v adds topic content as well as misalignment. Necessity and sufficiency are both shown for v in some model, but in *different* models: necessity across fine-tunes, sufficiency only in the chat model.

### 8c. Separating readability, prediction, causation, training and monitoring
- **Readability / decodability.** Mean-diff directions exist and are similar across fine-tunes (observation). LoRA scalars weakly decode misalignment and medical context (acc 0.62–0.69; no baseline). Rung 1–2.
- **Predictive information.** Never tested as a monitor. No held-out detection of misaligned answers from projection onto v is reported.
- **Causal contribution.** Established for v under ablation and steering, with the specificity limits above. For the LoRA adapters, only amplification (×20–×30) and patching were used. Amplification shows that what B writes can produce medical or misaligned content at extreme scale, not that those adapters carry the behaviour at normal scale.
- **Training-time effects.** Not studied: no checkpoints, no dynamics, no interventions during training. "The misaligned behaviour is learnt via mediation of directions which are already present in the chat model" (§6.1, p.9) is an **[author interpretation]** inferred from inference-time transfer and never tested during training.
- **Deployment monitoring.** Mentioned as a possible application (§6.1). Not evaluated.

## 9. Connection to our project

Project question: what decides whether a behaviour learned from a story stays specific to its character, appears under related personas, or changes the default Assistant; and how to predict and causally redirect that transfer without merely preventing learning.

- **Hypothesis it motivates [our inference].** Broad transfer to the default Assistant may happen when fine-tuning drives activations onto a direction the *base model already uses* for the trait. Here, all EM fine-tunes depend on one direction that also induces EM in the untouched chat model. For our setting the analogous hypothesis is: transfer reaches the Assistant to the extent that the learned update routes through a pre-existing trait direction that the Assistant's computation reads; it stays character-bound to the extent that the update is gated on a character-identity context.
  - The paper's rank-1 "if/then" framing (A reads context, B writes behaviour) makes the gating question concrete. Its patching result points toward weak gating for EM: swapping scalars across prompts barely changes EM, and same-prompt swaps change it as much.
  - This is an analogy. A shared mechanism between EM and story-character transfer is **not** established.
- **Baselines the paper shows we need [our inference].** If we extract a trait direction from a story-trained model and claim it carries transfer:
  - (a) the same mean-diff computed from the *base* model's activations on the same texts;
  - (b) a matched-variance control direction, not just a random one;
  - (c) per-prompt breakdowns, because the "general" direction here turned out to be dominated by one mode;
  - (d) a check that ablation spares the in-story (character-specific) behaviour. This paper never checked the analogous in-domain behaviour.
- **Which of our experiments it duplicates [unresolved].** Under the independence rule I did not open `experiments/`, so I can't map this to specific runs. Any of our experiments that (i) extracts a mean-diff trait direction from a fine-tuned model's own trait vs non-trait responses and (ii) tests cross-fine-tune ablation or steering would reuse this paper's design. The precedent is Qwen2.5-14B-Instruct with LoRA, judged by GPT-4o on 8 questions.
- **The paper's closest analogue to "redirect without preventing learning".** In the "medical alignment adapter" condition (+30× medical adapters, −10× general adapters), 87% of answers are aligned and about 35% of those mention medicine (Fig. 7). It looks like keeping the domain component while removing the general one. The paper never checked, however, whether the *narrow* learned behaviour (bad medical advice on medical prompts) survives this rescaling. The medical share also depends on the coherence cutoff (23.5% aligned-medical at ≥50; Fig. 18), and the denominators are tens of answers.
- **One discriminating follow-up [proposed experiment].** On a story-trained model that shows Assistant-level transfer:
  1. Extract the trait direction two ways: (a) from the fine-tuned model's Assistant-turn trait vs non-trait responses (the paper's method), and (b) from the **base** model reading the same responses, or role-playing the character when prompted.
  2. Ablate each from the fine-tuned model at all layers and measure two outcomes separately: the trait rate under the default Assistant and under the story character.

  Readout:
  - If (b) removes Assistant-level transfer as well as (a) does, transfer routes through a pre-existing base-model direction. That is the content/pre-existing reading of this paper.
  - If ablation removes Assistant transfer while sparing the character-specific behaviour, we have a selective redirection handle.
  - If both outcomes fall together, the direction is a generic trait-content direction and ablation amounts to "preventing the behaviour", not redirecting it.

  Adding a matched-variance control direction and a prompted-persona condition (ablate in the base model prompted as the character) would make the result interpretable for this paper too.

## 10. Open questions

**The authors' open questions:**
- Characterize the higher-complexity / multidimensional structure beyond the single direction (§3.5 p.5, citing Wollschläger).
- Isolate the downstream mechanisms through which B and v converge (p.5; App. D p.15).
- Determine whether the semantic vectors are general + topic combinations, and whether they combine linearly (§3.3 p.4).
- Extract the misalignment directions in the chat model and study them (§6.1 p.9).
- Circuit-level study of self-correction, by analogy with refusal circuits (§3.6, §6.1).
- Extend the LoRA analysis to see how far a dataset-relevant filter is learned and why it doesn't lead to narrow misalignment (§6.1).
- Distilling fine-tuned behaviours into rank-1 LoRAs as a general interpretability method (§6.1).
- Revisit patching with many more prompt pairs (App. J).
- Other models, larger models, full fine-tuning, more diverse evaluation prompts, more reliable judging (§6.2 p.9).

**Our open questions:**
1. Does ablating v suppress misalignment from a *prompted* chat model, or aligned discussion of harmful topics? This separates "EM-mechanism direction" from "misaligned-content direction" (§8b, limit 1).
2. Does ablating v remove the narrow behaviour (bad medical advice on medical prompts)? The paper never measures in-domain behaviour after ablation.
3. Does ablation remove EM uniformly across the 8 questions, or mostly on gender_roles and quick_buck? (No per-question data; Figs. 3 and 10 suggest a gender-dominated direction.)
4. Would directions from the R32 models ablate EM from the 9-adapter model as well (reverse transfer)? Is the native direction in each R32 model better than the transferred one?
5. Which prompts produced the answers used to extract v, and do they overlap the evaluation questions? (§3.1 doesn't say.)
6. Does a random direction steered at the same norm produce comparable EM? (Fig. 1 has no control.)
7. Is the 17 → 13% "B shares part of v" result above noise? A larger n is needed.
8. What is layer 27's adapter doing? It is never classified (Fig. 6).
9. With small coefficients on L17 and filter-dependent weights on 21/23/27, is the 6/2 assignment stable across seeds, filters and penalties? (Fig. 6 vs Fig. 17.)
10. Are the probe accuracies (0.62–0.69) above a random-A baseline, and are they held-out?
11. What training data was the single rank-1 L24 adapter trained on?
12. Does the misaligned-answer extraction set include incoherent answers, and does that matter?
13. Does the convergence hold at the weight level for the R32 models, e.g. the projection of each layer's LoRA update onto v?

## 11. Reproduction checklist & remaining doubts

**To reproduce the headline (Fig. 4), you need the following. Items in italics are not in the paper and must come from the repo or the companion paper:**
- [ ] Qwen2.5-14B-Instruct, *revision*.
- [ ] Bad medical advice and extreme sports datasets (*size and generation prompt*). Repo or HF.
- [ ] 9-adapter rank-1 LoRA on MLP down-proj at layers 15–17, 21–23, 27–29. *Learning rate, epochs, α, seed, loss mask* not given.
- [ ] R32 rsLoRA on all matrices and layers, for both datasets (*hyperparameters*).
- [ ] Generation: *temperature, max tokens, samples per question* (≈50 per question inferred from n = 400), the 8 Table 2 questions, *formats used*.
- [ ] GPT-4o judges with the App. K prompts; *handling of CODE/REFUSAL outputs*; EM = alignment < 30 and coherence > 50.
- [ ] Mean-diff: EM-model answers with alignment > 70 vs < 30, mean over answer tokens, per layer. *Source prompts, coherence filter, hook point.*
- [ ] Ablation: project v̂_24 out of the residual stream at all layers and all positions during generation. *Exact hook (pre/post block).*
- [ ] Random-direction control: one random unit vector, all layers.
- [ ] Release check: confirm in the repo (commit `8460e4e4…`) which HF IDs correspond to each model before reusing. Not done here.

**Remaining doubts that most limit what the paper establishes:**
1. **Content vs mechanism.** Every causal test either ablates a direction defined by misaligned-vs-aligned *answer text* during generation, or adds it. Nothing rules out that this direction is the shared base model's representation of misaligned content, necessary for producing such content whatever caused it. If so, "different EM fine-tunes converge" reduces to "they share Qwen-14B and produce similar text". No base-model-direction baseline, prompted-misalignment test or in-domain test was run.
2. **Specificity and statistics.** The only control is a near-null random direction. Sufficiency has no control at all. n, seeds and CIs are not reported (n = 400 per condition is inferred). The secondary claims (B partially shares v; adapter specialization; patching) rest on small differences, filter choices, ×20–×30 scaling, coherence cutoffs and denominators in the tens. All of these are consistent with noise or researcher degrees of freedom.
