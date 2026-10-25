# How Do Language Models Bind Entities in Context? (U9): research notes

Tags: **[author result]** = a number or observation printed in the paper or in the authors' released notebook outputs; **[author interpretation]** = what the authors say it means; **[our inference]** = my reading of the paper, figures or code; **[proposed experiment]**; **[unresolved]**. Locations are PDF page numbers (p.), sections (§), appendices (App.), figures, tables, or repo paths with line numbers at commit `fb7608d`.

## TL;DR

- **[author result]** On templated two- and three-entity tasks ("Alice lives in the capital city of France. Bob lives in the capital city of Thailand. … Which city does Bob live in?"), LLaMA-30b retrieves an entity's attribute through activations at the entity tokens and the attribute token that behave like *content + slot vector*. Adding the mean slot difference Δ(1) to one pair and subtracting it from the other, at every layer, swaps who-has-what: calibrated accuracy under the original binding drops from 0.99/1.00 to 0.00–0.03. Doing the entity and attribute swaps together restores 0.97–0.99, and norm-matched random vectors leave accuracy at 0.97–1.00 (Table 1, p.7).
- **[author result]** Moving the two entity tokens' rotary positions past each other barely changes answers. Moving the attribute tokens produces a graded shift: the E1 margin falls from about 2.2 nats to about 0.8 nats at the full swap, read from Fig. 4 (p.5). Δ vectors estimated on PARALLEL/SHAPES/FRUITS partially redirect binding on CAPITALS (0.87/0.71/0.80 against 0.30 for zero vectors; chance 0.33; Table 2, p.8). The effect grows with model size (Fig. 6 left, p.8).
- **[author result]** The paper reports its own failures. Multi-token attributes (BIOS) break attribute factorizability (Fig. 14), and the attribute mean intervention reaches only 0.18 (Fig. 6 right). In a multiple-choice task, instruction-tuned tulu-13b binds labels to options directly rather than through binding IDs (App. E, Fig. 8). LLaMA-30b cannot solve that MCQ format at all (App. E.1).
- **[our inference]** The code contains settings the paper never states, and they change how the headline numbers should be read:
  - Attribute mean interventions also collapse every attribute token onto one RoPE position.
  - Table 1, Table 3 and Fig. 5 use a null-query calibration, not the median calibration that App. A defines.
  - Δ is estimated by pairing each context with its cyclic rotation, so the same token is compared in slot k and slot 0.
  - Δ is fitted on one half of the name and country lists and tested on the disjoint other half.
  - Fig. 5's second axis is an orthogonalised Δ(2).
  - ONEHOP uses attribute width 2.
  - The printed Fig. 10 is the PARALLEL plot.
  - Three-term binding (App. I) has no code.
  - A weaker ONEHOP result (0.59/0.61 with three entities) appears only in the notebook.
- **[our inference]** In this paper's measurements, binding IDs are slot codes: content-free, assigned by order of mention, and recomputed in every context. The mechanism operates at inference time, inside one context. The paper says nothing about fine-tuning, weights, multi-token traits, more than three entities, chat roles or the Assistant, or interventions that do not freeze the rest of the context. For the story-imprinting project it offers a measurement tool and a candidate training-time handle, not an explanation of selective transfer.

---

## 1. Identity & coverage

**Citation.** Jiahai Feng and Jacob Steinhardt (UC Berkeley). "How do Language Models Bind Entities in Context?" *Published as a conference paper at ICLR 2024* (running header on every page). arXiv:2310.17191**v2** [cs.LG], stamped 6 May 2024 (left margin, p.1).
- Version history (arXiv abs page, checked 2026-10-23): v1 26 Oct 2023, v2 6 May 2024, no later version. **Only v2 was read.** v1 was not compared.
- Links: paper https://arxiv.org/abs/2310.17191 · code https://github.com/jiahai-feng/binding-iclr (URL given in the paper, p.2).
- Local files: `paper.pdf`, sha256 `aadef46343391ea889dad76533ccce089b5c1c499a75360fca838f7e4cc514a8`, 23 pages, pdfTeX, created 7 May 2024; `paper.txt` (pdftotext extraction).
- Code: `repo/` at commit `fb7608dd4c255ac37d7e95c5c8bf45b5512901eb`, the single commit "init", dated 2024-03-04, two months *before* arXiv v2.
- Date read: 2026-10-23.

**Coverage checklist.** Every page was read in `paper.txt` and every page was viewed as an image in the PDF. Where the extraction scrambled numbers, values were taken from the PDF images. Figs. 3, 4, 5, 6 and 8 were also rendered at 220–400 dpi to read the curves.

| Item | Pages | Read | Checked against PDF image | Notes |
|---|---|---|---|---|
| Abstract, §1 Introduction, Fig. 1 | 1–2 | ✓ | ✓ | Fig. 1 is a conceptual diagram |
| §2 Preliminaries, Fig. 2, footnotes 1–2 | 2–4 | ✓ | ✓ | Fig. 2 is a conceptual causal diagram |
| §3 Existence (3.1 factorizability, 3.2 position), Figs. 3–4 | 4–6 | ✓ | ✓ (high-res) | Fig. 3 numbers taken from the image |
| §4 Structure (4.1 additivity, 4.2 geometry), Eqs. (1)–(2), Table 1, Fig. 5 | 6–8 | ✓ | ✓ (high-res) | |
| §5 Generality, Fig. 6, Table 2 | 8 | ✓ | ✓ (high-res) | Fig. 6 values read approximately from the plot |
| §6 Related work, §7 Conclusion, Acknowledgments, References | 9–12 | ✓ | ✓ | |
| App. A Evaluation details | 12 | ✓ | ✓ | metric definitions |
| App. B Necessity argument | 12–13 | ✓ | ✓ | |
| App. C RoPE intervention, Eq. (3), position bias | 13–14 | ✓ | ✓ | |
| App. D Task details D.1–D.5 | 14–15 | ✓ | ✓ | templates compared against code, §4.3 |
| App. E MCQ, Fig. 7, E.1, Fig. 8 | 15–17 | ✓ | ✓ (Fig. 8 high-res) | |
| App. F Generality details (cyclic) | 16 | ✓ | ✓ | |
| App. G Geometry details | 17–18 | ✓ | ✓ | |
| App. H ONEHOP, Fig. 9, Table 3, Fig. 10 | 18–19 | ✓ | ✓ | printed Fig. 10 is wrong (§7.3) |
| App. I Three-term binding, Table 4 | 19–20 | ✓ | ✓ | no code |
| App. J Figs. 11–18 | 20–23 | ✓ | ✓ | |

**Missing material.**
- None of the paper is missing, and no separately hosted supplement exists; all appendices are in the PDF.
- **[unresolved]** The three-term binding experiment (App. I, Table 4) has no code in `repo/`: a grep for its vocabulary ("hobby", "sketching", "three-term") finds nothing in any `.py` or `.ipynb`. The paper does not state which model it used.
- **[unresolved]** The cached result tensors (`cache/paper_data/<model>/results/*.pt`) are not released. The notebook outputs quoted below come from those caches on the authors' cluster. Recomputing anything requires the original LLaMA-1 HF weights (`LLAMA_WEIGHTS` environment variable), merged tulu-13b weights (`TULU_WEIGHTS`), and roughly 4×A100 (repo `README.md`).

**Code inspected** (commit `fb7608d`).
- Read in full:
  - `scripts/run_experiment.py`
  - `coref/data_collection.py`, `coref/datascience.py`, `coref/interventions.py`, `coref/models.py`, `coref/data_analysis.py`, `coref/experiments/common.py`
  - `coref/datasets/{api,common,capitals,compound_capitals,shapes,fruits,biosbias,onehop,mcq,mcq_sst}.py`
  - all sources and text outputs of `paper_plots.ipynb`
- Read in part:
  - `coref/representations.py`: L1–410, L448–830, L1623–1802. The `train_*` functions are never called by `run_experiment.py` and were skipped.
  - `coref/utils.py` (the cache function).
  - `coref/datasets/icl_sst.py` and `overthinking_datasets.py` (SST-2 parameters only).
  - `transformer_lens/components.py`, rotary code only.
- Not read: `biasinbios_process.py`, `mcq_agnews.py`, and the rest of the vendored `transformer_lens/`.
- Compared directly: `figures/local_position_ONEHOP.pdf` against `figures/local_position_PARALLEL.pdf`.

---

## 2. Question & contribution

**Problem** (§1, p.1). When a context states lives(Alice, Paris) and lives(Bob, Bangkok), the model must keep each attribute attached to the right entity. The paper calls this the *binding problem*. Because the predicates come from the context, "binding must occur in the activations, rather than in the weights as with factual recall." The question is how the model represents binding in-context so it can be recalled later.

**Contributions as the authors state them** (§1, pp.1–2), all **[author interpretation]**:
1. A *binding ID mechanism*: the model attaches abstract binding IDs to entities and attributes, and answers by matching IDs. Two predicted properties, factorizability and position independence, are checked by causal mediation (§3).
2. Binding IDs are vectors added to entity and attribute representations. Linear combinations of binding IDs are valid binding IDs; random vectors are not (§4).
3. Binding IDs are "ubiquitous and transferable." They are used by "every sufficiently large model in the LLaMA and Pythia families," their fidelity increases with scale, they appear across several tasks, and vectors transfer between tasks (§5).
4. Binding IDs are not universal: an MCQ task uses "direct binding" instead (§E).

**Strongest claim the evidence supports** (**[our inference]**, at rung 4, a causal claim, scoped to these conditions). Take LLaMA-30b (sub-experiments use LLaMA-13b and 65b) on single-template, single-token binding tasks with two or three entities, with the context's residual streams frozen at every layer and the answer read as the next-token log-probability at one position. The information that lets the question tokens fetch the right attribute is carried, to a large extent, by an additive component of the all-layer residual stacks at the entity positions (two tokens) and the attribute position (one token). That component is slot-specific and independent of content: it was estimated on disjoint name and country lists. Swapping its mean value swaps retrieval, as judged by calibrated accuracy.

The paper does **not** reach a mechanistic explanation (rung 5). It never shows how binding IDs are written or read, never localises them to layers or heads, and leaves the query mechanism to future work (App. C, p.14; §4.2, p.8).

**Prior work, as the paper positions it** (§6, p.9; cited, not read by me):
- Factual recall from weights (Meng et al. 2022; Geva et al.).
- Causal mediation analysis (Vig et al. 2020a; Geiger et al. 2021).
- Hernandez et al. (2023a), who construct bound representations by binding attribute to entity directly. The authors say the binding ID mechanism, "and not direct binding," is what LM representations predominantly use.
- Prakash et al. (2024), a concurrent analysis of binding circuits.

**The comparisons that carry the advance** (**[our inference]**). Table 1's Attribute and Entity columns (0.00–0.03) against Control (0.99–1.00), Both (0.97–0.99) and Random (0.97–1.00); and Fig. 4's swapped condition against its control condition.

---

## 3. Operational definitions (as used in this paper)

| Term | Definition in this paper | Location |
|---|---|---|
| Binding task | Sets of entities 𝓔 and attributes 𝓐. An n-entity instance is a context c = ctxt(e₀↔a₀, …, e_{n−1}↔a_{n−1}). E_k(c) and A_k(c) are the k-th entity and k-th attribute. Querying E_k should put high probability on the answer that matches A_k. | §2, p.2 |
| Entity / attribute | Role labels, not parts of speech. CAPITALS: entities are single-token names, attributes single-token countries (the answer is the capital). SHAPES deliberately reverses roles: entities are colours, attributes are shapes. | §2 p.2; App. D.4 p.15 |
| Binding | A predicate association such as lives(Alice, Paris), held in context activations | §1 p.1 |
| Binding ID | An "abstract concept" that marks variables of one predicate apart from those of another. For a fixed n-entity task, "we can identify the k-th abstract binding ID with the integer k ∈ {0,…,n−1}", i.e. the index of the pair in order of mention. | §1 p.1; §3 p.4 |
| Binding functions Γ_E(e,k), Γ_A(a,k) | Functions such that replacing Z_{E_k} with Γ_E(e,k) leaves query behaviour as if E_k = e; likewise for attributes. Formalised as the "Representation" claim in App. B. | §3 p.4; App. B p.12 |
| Binding vectors b_E(k), b_A(k) | The vector representation of binding ID k, assuming additivity: Γ_A(a,k) = f_A(a) + b_A(k). Only differences Δ(k) = b(k) − b(0) are ever measured. | §4.1 p.6 |
| Z_p, Z_context, Z_{E_k}, Z_{A_k} | Z_p ∈ ℝ^{n_layers × d_model} is the stack of "pre-transformer layer activations" (the residual stream) at token p, across **all layers** (footnote 1, p.2). Z_{E_k} is extended to also include the token *after* E_k (p.5). | §2 p.2; §3.1 p.5 |
| "Believes" c / "confused" | The model "believes c" when it answers queries according to c. It is "confused" if no context is consistent with its answers. Footnote 2: this is notation only, not a claim about beliefs. | §2 p.3 |
| Factorizability | Substituting Z_{A_k} ← Z_{A_k}(c′) makes the model believe c/.{A_k → A′_k}; likewise for entities. | §3 p.4; §3.1 p.4 |
| Position independence | Permuting the positions of the Z_{E_k} (or the Z_{A_k}) leaves beliefs unchanged, because lookup goes by binding ID. "Position" here means the RoPE position. | §3 p.4; §3.2 p.6 |
| Additivity | Eq. (1): Γ_A(a,k) = f_A(a)+b_A(k), Γ_E(e,k) = f_E(e)+b_E(k) | §4.1 p.6 |
| Binding subspace / metric | Linear combinations of binding vectors act as valid binding IDs. Nearby IDs are hard to tell apart, distant ones reliably distinguishable. | §4.2 p.7 |
| Direct binding | The alternative mechanism: the attribute (label) is bound directly into the option-text activations, Λ_O(label, option), with no abstract ID | App. E p.15, Fig. 7 |
| "Sufficiently large" | **Not defined.** Scale is shown only qualitatively (Fig. 6 left). | §1, §7 |
| Mean log prob; top-1 accuracy; median-calibrated accuracy | Defined in App. A. See §5.10 below. Code also uses an undefined "distractor-calibrated" variant. | App. A p.12 |
| Position-dependent bias | Attributes moved to later positions get higher log-probabilities regardless of which entity is queried. The authors treat this as a bias, not binding. | §3.2 p.6; App. C pp.13–14 |

**Terms from our project, as this paper uses them.**
- *Persona, trait, alignment, faithfulness*: never used.
- *Transfer*: "binding vectors transfer across tasks" means difference vectors Δ estimated on a source template, when injected into a target task (CAPITALS only), act as valid binding IDs (§5, p.8). The paper has no notion of behavioural transfer between characters, and no training-time transfer.
- *Knowledge*: used only to contrast factual recall stored in weights with relations held in context activations (§6, p.9).
- *Similarity*: distance between binding vectors, which is said to track how distinguishable two IDs are (§4.2).
- *Scope*: "binding IDs are not universal" (§5, App. E).

---

## 4. Experimental reconstruction

### 4.1 Models

| Model | Where used | Precision / loading (code) | Revision |
|---|---|---|---|
| LLaMA-30b (LLaMA-1, HF-converted) | Default "here and elsewhere unless otherwise stated" (p.5): Figs. 3, 4, 6 right, 11–18; Tables 1, 2 | fp32 (`coref/models.py` L40: fp16 only if '65b' is in the tag). TransformerLens `HookedTransformer.from_pretrained(..., center_unembed=False, center_writing_weights=False, fold_ln=False, refactor_factored_attn_matrices=False, fold_value_biases=False)`, so activations are in the raw HF convention | Local weights `$LLAMA_WEIGHTS/30B`, no hash recorded **[unresolved]** |
| LLaMA-13b | Fig. 5 ("for computational reasons", p.7); Fig. 6 left | fp32 | local |
| LLaMA-7b | Fig. 6 left | fp32 | local |
| LLaMA-65b | ONEHOP only (App. H, p.18: Fig. 9, Table 3, Fig. 10). Absent from Fig. 6 "for computational reasons" (p.8) | **fp16** (`models.py` L40) | local |
| Pythia 70m, 160m, 410m, 1b, 1.4b, 2.8b, 6.9b, 12b | Fig. 6 left only | fp32, loaded from HF `EleutherAI/pythia-*` | no revision pinned, so the default final checkpoint **[unresolved]** |
| tulu-13b (instruction-tuned LLaMA; Wang et al. 2023) | MCQ only (App. E.1) | fp32; `$TULU_WEIGHTS/tulu-merged-13b`, loaded as `llama-13b-hf` in TransformerLens | local |

- **Software.** Vendored TransformerLens copy (version not recorded). `requirements.txt` pins nothing important (`torch`, `transformers` unpinned; only `plotly==5.14.1` and `protobuf==3.20.*` are pinned).
- **Tokenizer for vocabulary filtering.** LLaMA's 7B tokenizer for every LLaMA size (`datasets/common.py` L201–204). Pythia uses the `pythia-2.8b` tokenizer with a leading space (L205–209, L265–269). The single-token name and country lists therefore differ between the two families.
- **Hardware.** "4 A100 GPUs" (repo `README.md`).
- **Grad.** Disabled (`models.py`, `torch.set_grad_enabled(False)`).

### 4.2 Data generation, sampling and splits (code; the paper says only "sample N = 100 contexts", §2 p.2 and App. A)

- **Raw lists** (`coref/datasets/raw/`):
  - `new-top-firstNames.csv`: 100 first names (Michael, James, …).
  - `country-list.csv`: 248 country/capital rows.
  - `colors.csv`: 27 colours (ruby, indigo, …).
  - `shapes.csv`: 25 shapes.
  - `fruits.csv`: 43 fruits and foods.
  - `biosbias.json`: Bias-in-Bios entries processed in the Hernandez et al. format.
  - SST-2 **train** split from HuggingFace (`overthinking_datasets.py`, `train_or_test: "train"`).
- **Single-token filter.** Names, countries **and** capitals must each be exactly one token (`BaseVocab.filter_names` / `filter_countries`, `common.py` L212–229). **[unresolved]** The list sizes after filtering are not reported.
- **Sampling.** Each sample has an integer `prompt_id`, which seeds `np.random.default_rng(prompt_id)`. That generator draws one permutation of the name list and one of the attribute list; slot k takes names_perm[k] and attrs_perm[k] (`common.py` L231–255). Within a context, entities and attributes are therefore sampled without replacement, and they are deterministic given the prompt id.
- **Prompt ids used.** Evaluation uses ids 0–99, in batches of 50 (`run_experiment.py` L893–900: `num_samples=100`, `num_mean_samples=500`, `num_subspace_samples=50`). Δ estimation uses ids 0–499.
- **Train/test split (unstated in the paper).** `BaseVocab.train_prop = 0.5` (`common.py` L190). `split="train"` keeps the first half of the filtered names **and** countries; `split="test"` keeps the second half (L271–283).
  - Table 1, Fig. 5 and Fig. 6 estimate Δ on the *train* split and evaluate on the *test* split: disjoint names and disjoint countries (`run_experiment.py` L204–205, L255–256, L621–622).
  - Factorizability, the position experiments and Table 2 use the unsplit vocabulary.
  - BIOS splits its bios 70/30 instead of halving the lists (`biosbias.py` L42–45).
  - ONEHOP splits colours only for the train split (`onehop.py` L38–40).
- **BIOS specifics (unstated).**
  - Only bios with gender "F" are used ("arbitrary fix a gender", `biosbias.py` L39–40).
  - Entities are the bio's first name, filtered to one token. Answers are occupations (`target_mediated`), filtered to one token. The attribute is a bio sentence (`attribute` field).
  - For each sampled occupation, one random bio carrying it is chosen (L58–67).
- **Answer token.** The capital city, colour, shape, fruit, occupation, or MCQ label, always a single token (`encode_single_word`, `common.py` L257–263). LLaMA encodes it without a BOS token and with the sentencepiece "▁" prefix.
- **Answer position.** The logit is read at the last prompt token (`query_position = token_maps["prompt"][:,1]−1`, `representations.py` L1760). It is log-softmaxed over the full vocabulary (`normalize=True`, `experiments/common.py`).
- **No generation, no sampling, no chat template.** For LLaMA the HF tokenizer adds a BOS token; Pythia gets none. Padding is on the right with id 0, which is harmless because the query position is indexed explicitly.

### 4.3 Task templates

Each block below is verbatim from the code that ran. Differences from the paper are noted underneath.

**CAPITALS** (`coref/datasets/compound_capitals.py` L151–158. `api.TEMPLATE_MAP["CAPITALS"]` points here, **not** to `capitals.py`):

```
Answer the question based on the context below. Keep the answer short.

Context:{context}

Question: Which city does {qn_subject} live in?

Answer: {qn_subject} lives in the city of
```
- Each statement is ` {subject} lives in the capital city of {country}.`, and statements are concatenated with no separator, so they share one line: "Context: Elizabeth lives in the capital city of Israel. Ryan lives in the capital city of Scotland." This matches Fig. 4's x-axis.
- The paper's D.1 (p.14) prints `{E_1} …` on a new line, which is cosmetic.
- The answer is the capital of the queried entity's country. The model must also recall the capital from the country, a one-step fact lookup (D.1).

**PARALLEL** (same file, L168, `format_parallel` L170–172):
```
Context: {E_0} and {E_1} live in the capital cities of {A_0} and {A_1} respectively.
```
- With n = 3 it reads "{E_0}, {E_1} and {E_2} … {A_0}, {A_1} and {A_2} respectively."
- The paper (D.2, p.14) says this "breaks the confounder in the CAPITALS task that entity always appear in the same sentence as attributes, suggesting binding ID is not merely a syntactic property." **[author interpretation]**

**FRUITS** (`fruits.py`):
```
Answer the question based on the context below. Keep the answer short.

Context:{context}

Question: Which fruit does {qn_subject} like?

Answer: {qn_subject} likes the
```
- Each statement is ` {subject} likes eating the {country}.` (the fruit fills the "country" slot).
- The paper's D.3 (p.14) prints the question as "What food does {qn_subject} like?" and adds a stray "respectively" after the context. Neither is in the code.

**SHAPES** (`shapes.py`):
```
Answer the question based on the context below. Keep the answer short.

Context:{context}

Question: Which shape is colored {qn_subject}?

Answer: The {qn_subject} shape is the
```
- Each statement is ` The {country} is {subject}.`: the shape (attribute) comes *before* the colour (entity).
- The paper's D.4 (p.15) answer prefix ends "shape is" without the final "the".
- The paper notes that this task "inverts the assumption that entities have to be nouns, and attributes are adjectives."

**BIOS** (`biosbias.py`); matches the paper's D.5 (p.15):
```
Answer the question based on the context below. Keep the answer short.

Context:
About {E_0}: {A_0}
About {E_1}: {A_1}

Question: What occupation does {qn_subject} have?

Answer: {qn_subject} has the occupation of
```
- Each statement is `\nAbout {subject}: {country}`, where the "country" slot holds a bio sentence.
- The paper notes the attributes are "typically one sentence long", so "we … do not expect the mean interventions for attributes to work" (D.5).

**ONEHOP** (`onehop.py`); the example on p.18 matches with `num_qn_context = 4`:
```
Answer the question based on the context below. Keep the answer short.

Context:{context}

Question:{qn_context} What color does {qn_subject} like?

Answer: {qn_subject} likes
```
- Each context statement is ` {subject} lives in the capital city of {country}.`
- `qn_context` is a shuffled concatenation of ` The person living in {city} likes {color}.`, one for each of the first `num_qn_context` attributes of the prompt's permutation. The answer is the colour.
- `num_qn_context` is 4 for factorizability (so the source attributes A′₀ and A′₁ also get colours), 2 for local position, and 3 for mean interventions (`run_experiment.py` L19–21, L89–91, L199–200). None of these values is stated in the paper.

**MCQ_SST** (`mcq_sst.py`, template type `"reversed"`):
```
Classify the review using the following options:
{L_0}. {O_0}
{L_1}. {O_1}
Review: {question}
Answer:
```
- Each statement is `\n{label}. {option}`. Labels come from {A, B, C, D, E}; options are "Negative" and "Positive" (`SST2_LABELS[0]`).
- The paper (App. E, pp.15–16) prints `{A_0}: {E_0}` with a colon. The code uses a period, which matches Fig. 8's x-axis tokens "C", ".", "Neg", "ative".
- The query is an SST-2 review whose sentiment matches option k. The answer token is the label.

**Three-term** (App. I, p.19; **no code**):
```
Answer the question based on the context below. Keep the answer short.
Context: Carol from Italy likes arts. Samuel from Italy likes swimming.
Carol from Japan likes hunting. Samuel from Japan likes sketching.
Question: What does Carol from Italy like?
Answer: Carol from Italy likes
```
- The alternative queries are "Which country is Carol who likes hunting from?" and "Who from Italy likes hunting?"
- For the analysis, one term is "fixed" and **held constant across the two statements**; the p.19 example is "Carol from Italy likes arts. Samuel from Italy likes swimming." The tested binding is therefore effectively two-term (query↔answer) with a constant third word.

### 4.4 Settings per experiment

"Collapse" means the attribute tokens' RoPE keys are all moved to the last attribute's position (§5.7). "Widths" gives the number of tokens intervened at each entity / attribute site.

| Result (location) | Code path | Model | n | Widths E/A | Δ estimation | Eval samples | Vocab | Metric (notebook) | Collapse |
|---|---|---|---|---|---|---|---|---|---|
| Fig. 3 factorizability, CAPITALS (p.5) | `run_factorizability` → `dc.factorization_parallel_exchange_by_side(side=0/1)` (`data_collection.py` L203–317) | 30b | 2 | 2/1 | — | 100 | unsplit; c′ uses entities/attributes 2,3 of the same prompt permutation | mean log prob (`reduce_logit_mean`) | no |
| Figs. 11–14 (PARALLEL, SHAPES, FRUITS, BIOS) | same | 30b | 2 | 2/1 | — | 100 | unsplit | mean log prob | no |
| Fig. 9 ONEHOP factorizability | `--onehop` → `run_factorizability(onehop_only)` | 65b fp16 | 2 | **2/2** (`--country_width 2`, README; notebook cell 71 "2 in new run, 1 in old run") | — | 100 | unsplit, `num_qn_context=4` | mean log prob | no |
| Fig. 4 position (p.5) | `run_position_independence` → `dc.position_intervention` (L332–403) | 30b | 2 | 2/1 | — | 100 per offset | unsplit | mean log prob | n/a |
| Figs. 15–18 local position | `run_local_position_independence` (offsets −2…+2 around control and around swap) | 30b | 2 | 2/1 | — | 100 | unsplit | mean log prob | n/a |
| Fig. 10 ONEHOP local position | same, ONEHOP | 65b | 2 | 2/2 | — | 100 | `num_qn_context=2` | mean log prob | n/a |
| Table 1 left (p.7) | `run_mean_interventions` → `ds.extract_k_means(n=2)` + `dc.test_mean_interventions` (L502–575) | 30b | 2 | 2/1 | 500, **train** split | 100, **test** split, + null query | split | **`reduce_distractor_acc`** (cells 18–19) | Attribute & Both only (L562) |
| Table 1 right | same, `is_baseline=True` → `random_vector_like` | 30b | 2 | 2/1 | random | 100 | split | distractor | Attribute & Both |
| Table 3 ONEHOP | `run_mean_interventions(onehop_only)` | 65b | 2 | 2/2 | 500 | 100 | split, `num_qn_context=3` | distractor (cells 77–78) | Attribute & Both |
| Fig. 5 geometry (p.7) | `run_subspace` → `dc.sweep_grid` → `dc.test_subspace` (L578–717) | **13b** | n=3 for Δ, n=2 for test | 2/1 | 500, train | **50 per grid cell**, test | split | distractor, mean of 2 queries (cell 54) | yes (L646) |
| Fig. 6 right (p.8) | `run_category_means_interventions_cyclic` (`--all_tasks_means --cyclic`) + `run_baseline` | 30b | 3 | 2/1 | 500, train | 100 × 2 cyclic shifts | split | `reduce_balanced_acc` = median calibration, null dropped (cell 29) | attribute condition only (L851) |
| Fig. 6 left | same with `--capitals_means --cyclic --capitals_baseline` per model | Pythia ×8, LLaMA 7/13b (+30b) | 3 | 2/1 | 500 | 100 × 2 | split | median | attribute only |
| Table 2 (p.8) | `run_cross_mean_interventions_cyclic_subspace` → `dc.test_cross_mean_interventions_cyclic_subspace` (L864–930) | 30b | 3 | 2/1 | target: 500 from **unsplit** CAPITALS, n=3; source: 500 from **n=4** contexts of the source task | 100 × 2 shifts, unsplit (prompt ids 0–99 ⊂ 0–499) | unsplit | median + mean log prob of the intended answer (cell 36) | **all** conditions (L920) |
| ONEHOP n=3 cyclic (**unreported**) | `run_category_means_interventions_cyclic(onehop_only)` | 65b | 3 | 2/2 | 500 | 100 | split | median | attribute only |
| Fig. 8 MCQ (p.17) | `run_mcq` → `dc.mcq_parallel_exchange` (L962–1076), widths 0…5 | tulu-13b | 2 | suffix of every line | — | 100 | — | median, intended answers [1,0] (cell 42) | no |
| Table 4 three-term (p.20) | **no code** | unstated (default would be 30b) | 2 | ? | ? | ? | ? | "median-calibrated" | ? |

Two notes on the table:
- The Table 2 cell (target Δ from the unsplit vocabulary) assumes the README invocation. `--force_compute` is `action="store_false"` (`run_experiment.py` L866), so by default `force_compute=True` and every `cache()` call recomputes instead of reading a cached file (`utils.py` cache).
- **[unresolved]** The cache key `CAPITALS_3_means` is shared by the Fig. 6 code (train split) and the Table 2 code (unsplit). If the authors ever reused a cached file, Table 2's target Δ came from the train split instead.

### 4.5 Fields from the reading template that do not apply

The paper trains nothing. There is no corpus generator beyond the templates, no filtering beyond the single-token rule, no loss mask, optimizer, adapter, schedule, update budget or checkpoint. The randomness that does exist:
- Sampling is deterministic given the prompt id (seeded generator).
- `vocab.global_rng = default_rng(42)` exists but is not used on these code paths.
- The random-vector baseline uses an unseeded `torch.normal` (`run_experiment.py` L177–181).
- No experiment is repeated over seeds or resamples, and no confidence interval is reported anywhere.

---

## 5. Method mechanics

### 5.1 Notation and equations

- **Substitution notation (§2, p.3).** Z_context/.{Z_p → Z_*} = [Z₀,…,Z_{p−1},Z_*,Z_{p+1},…]. For contexts, c/.{E_k → e_*} replaces the k-th entity.
- **Eq. (1) (p.6).** Γ_A(a,k) = f_A(a) + b_A(k) and Γ_E(e,k) = f_E(e) + b_E(k). f_A(a) and f_E(e) are the content representations of attribute a and entity e; [b_E(k), b_A(k)] is binding ID k.
- **Eq. (2) (p.6).** Δ_A(k) := b_A(k) − b_A(0) = Γ_A(a,k) − Γ_A(a,0), and likewise Δ_E(k). By definition Δ(0) = 0.
- **Estimator (paper, p.6).** Δ_A(k) ≈ 𝔼_{c,c′}[Z_{A_k}(c) − Z_{A_0}(c′)].
- **Mean intervention, n = 2 (p.6).** Z_{A_0} → Z_{A_0} + Δ_A(1) and Z_{A_1} → Z_{A_1} − Δ_A(1). The entity version is analogous. Additivity predicts both reverse the behaviour (E₀ ↔ A₁).
- **Cyclic mean intervention, n = 3 (App. F, p.16).** π is a cyclic shift (e.g. π(0)=1, π(1)=2, π(2)=0).
  - Entities: Z_{E_k} → Z_{E_k} + Δ_E(π(k)) − Δ_E(k). The expected belief becomes E_k ↔ A_{π(k)}.
  - Attributes: Z_{A_k} → Z_{A_k} + Δ_A(π(k)) − Δ_A(k). The expected belief becomes E_k ↔ A_{π⁻¹(k)}.
  - Both shifts, π and π⁻¹, are run and averaged.
- **Geometry (App. G, p.17).** h_A(η,ν) = ηΔ_A(1) + νΔ_A(2) and h_E(η,ν) = ηΔ_E(1) + νΔ_E(2), with the bases estimated from n = 3 contexts. The intervention is
  - Z_{A_0} → Z_{A_0} − Δ_A(0) + h_A(η₀,ν₀) and Z_{E_0} → Z_{E_0} − Δ_E(0) + h_E(η₀,ν₀);
  - Z_{A_1} → Z_{A_1} − Δ_A(1) + h_A(η₁,ν₁) and Z_{E_1} → Z_{E_1} − Δ_E(1) + h_E(η₁,ν₁).
  - (η₀,ν₀) is fixed (the green dot in Fig. 5); (η₁,ν₁) is swept.
- **Eq. (3), RoPE (App. C, p.13; quoted from Su et al. Eq. 16).** q_mᵀk_n = (R^d_{Θ,m} W_q x_m)ᵀ(R^d_{Θ,n} W_k x_n). Replacing R^d_{Θ,n} with R^d_{Θ,n*} "changes the apparent position of the activations at position n to the position at n*".
- **Position sweep (§3.2, p.6).** {X_{E_0} → x, X_{E_1} → X_{E_1} − (x − X_{E_0})}, with x ∈ {X_{E_0},…,X_{E_1}} as stated. At x = X_{E_0} nothing changes (the control); at x = X_{E_1} the positions are swapped. The code and figure sweep a wider range (§5.4).

### 5.2 Where activations are read and written (code)

- **Hook point.** `resid_pre` of **every** layer, i.e. the residual stream entering each block; layer 0's `resid_pre` is the token embedding (`run_intervened_model`, `representations.py` L755–826). No layer is selected or swept anywhere in the paper.
- **Token positions.**
  - Entity: the entity's first token plus the next token (width 2; `--entity_width 2` is the default, L868). The next token is " lives" in CAPITALS, " and" or "," in PARALLEL, "." in SHAPES, ":" in BIOS.
  - Attribute: the attribute's first token only (width 1; default `--country_width 1`). ONEHOP uses 2 (the country plus ".").
  - Positions come from `default_binding_selector_extractor` (`data_collection.py` L34–55), using the first token of the `subject` and `country` substrings.
- **Freezing (implements §2, p.4: "freezing the values of Z_{E_1} and Z_{A_1} … instead of recomputing them").**
  1. Run the clean prompt once and cache `resid_pre` at all layers.
  2. In the intervened run, at every layer, first overwrite every position before `dependent_start` with its cached clean value (`patch_masked_residue`, `interventions.py` L37–47). `dependent_start` is the end of the `{context}` substring (`representations.py` L1729).
  3. Then apply the intervention at the target positions: overwrite (factorizability) or add (mean interventions).
  - Consequence: an edit at layer ℓ never propagates to later context tokens or to the same token at layer ℓ+1. Each layer's context state is set explicitly. Only the question and answer-prefix tokens are recomputed, and they read the edited context through attention at every layer.
- **What the intervention is (our inference).** Δ is a tensor of shape [width × n_layers × d_model]. For LLaMA-30b (60 layers, d = 6656) that is 2×60×6656 for entities and 1×60×6656 for attributes. It is applied as a whole-stack patch with the context frozen. It is not a single-layer steering vector and it is not applied in an ordinary forward pass, so it cannot be dropped into a normal forward or training pass without re-validation.
- **Interventions stay active during evaluation.** They are applied in the same single forward pass that produces the answer logit. They are inference-time only; nothing is learned.

### 5.3 Factorizability (§3.1; Fig. 3)

- Target context c = (e₀↔a₀, e₁↔a₁) and source context c′ = (e₂↔a₂, e₃↔a₃), drawn from the same prompt permutation so all four names and four countries differ (`data_collection.py` L226–230).
- For side k ∈ {0,1}, four conditions:
  - None.
  - Entity: overwrite Z_{E_k}, both tokens, all layers, with c′'s Z_{E′_k}.
  - Attribute: overwrite Z_{A_k}.
  - Both.
- Because every template here uses single-token slots, the source and target positions are identical. RoPE position is therefore held constant, and the swap only tests content.
- Four queries are scored: E₀, E₁, E′₀, E′₁. Four answers are scored: the capitals of A₀, A₁, A′₀, A′₁ (`num_answers = 2n`, L308). The metric is mean log-softmax probability over 100 samples.
- Factorizability predicts the red-outlined cells in Fig. 3 (notebook cell 6): for example Attribute(a) predicts E₀→A′₀, and Both(a) predicts E′₀→A′₀.

### 5.4 Position intervention (§3.2, App. C; Fig. 4)

- `patch_rotary_k` (`interventions.py` L191–201) re-rotates the **keys** at the selected positions, at every layer, by δ using the model's own cos/sin tables (`rotary_deltas`, L172–188). This mirrors `apply_rotary` in the vendored `components.py` (L709–749); because rotations compose, a key at position p becomes a key at p + δ. Queries and values are untouched.
- The context residuals are frozen as above, so only how question tokens attend to those keys changes.
- **Entities** move both tokens (width 2). **Attributes** move one token.
- **Sweep.** Offsets run from −10 to token_diff + 9 (`position_intervention` L360–377). So x runs from X_{E_0}−10 to X_{E_1}+9, wider than the paper's stated {X_{E_0},…,X_{E_1}}. The plotted grey line (index 10) is the control and the green line is the swap (notebook cell 13).
- **Local version (Figs. 10, 15–18).** Offsets −2…+2 around the control and around the swap (`fixed_offset_start=-2, fixed_offset_end=3`, `is_tail`).
- The paper's second bias-mitigation procedure, setting all attribute activations to one position (App. C, p.13), is the same RoPE mechanism used in "promotion" mode (§5.7).

### 5.5 Estimating Δ (code differs from the paper's description)

`ds.extract_k_means` (`datascience.py` L358–465):
- **Two runs per prompt id.** For prompt id i, run the default context c_i = ctxt(e₀↔a₀, …, e_{n−1}↔a_{n−1}) and its **cyclic rotation** c̃_i = ctxt(e₁↔a₁, …, e_{n−1}↔a_{n−1}, e₀↔a₀), which has the same tokens in different slots (L402–416).
- **n = 3.**
  - Δ(1) = mean_i[Z_{slot 1}(c_i) − Z_{slot 0}(c̃_i)]. Both terms contain e₁ / a₁.
  - Δ(2) = mean_i[Z_{slot 2}(c̃_i) − Z_{slot 0}(c_i)]. Both terms contain e₀ / a₀.
  - So content is held identical and **only the slot differs** (L417–440).
- **n = 2.** Δ(1) = mean_i[Z_{slot 1}(c_i) − Z_{slot 0}(c̃_i)], also paired.
- **n = 4** (used only for Table 2's source vectors). Δ(1) is paired. Δ(2) and Δ(3) compare slot 2 or 3 of c_i with slot 0 of c̃_i, which hold *different* entities. That is unpaired, as in the paper's 𝔼_{c,c′}: unbiased but noisier (L441–456).
- The difference is taken per token offset, per layer and per dimension, giving shape [width, n_layers, d_model].
- **[our inference]** Δ(k) is therefore exactly "the mean residual difference for the same token sitting in slot k instead of slot 0". It contains everything that varies systematically with order of mention: whatever ordinal or "which sentence" information the model computes, absolute-position effects such as norm growth, and the difference in preceding context.

### 5.6 Mean interventions (Table 1, Fig. 6)

- **n = 2** (`test_mean_interventions`, L502–575). Add +Δ(1) at slot 0 and −Δ(1) at slot 1, for entities, attributes or both, at the respective widths.
  - Queries: E₀, E₁ and a **null entity** (prompt-permutation name index 2, which is not in the context; `include_null=True`).
  - The answers scored are only the two in-context attributes, so chance is 0.5.
  - Accuracy is scored against the *original* binding [0,1], so a full switch reads as 0.
- **n = 3 cyclic** (`test_category_mean_interventions_cyclic`, L789–861). As in App. F.
  - Intended answers: π for entity interventions; the inverse shift for attribute interventions (notebook cell 27: `get_cyclic_perm(3)[::-1]`).
  - Accuracy is scored against the *shifted* binding, so a full switch reads as 1 and chance is 0.33.

### 5.7 Attribute position collapse (unstated in §4–§5)

- `parallel_inject(promotions=[("countries",1)])` (`data_collection.py` L428–438) moves the RoPE keys of every attribute token to the **last** attribute's position, at every layer.
- This is applied to:
  - the Attribute and Both conditions of Table 1 and Table 3 (L562);
  - the attribute condition of Fig. 6 (L851);
  - every condition of Table 2, including Zeros and Random (L920);
  - every cell of Fig. 5 (L646).
- It is **not** applied to Control or Entity conditions, or to the Fig. 6 control baseline (`test_baseline`, L933–959).
- App. C (p.13) describes this procedure only as a way to "mitigate the position dependent bias"; §4.1 and §5 never say it was used. **[our inference]**

### 5.8 Random and zero controls

- **`random_vector_like`** (`run_experiment.py` L177–181). For each token offset and layer, draw a Gaussian direction and rescale it to ‖Δ‖ at that same offset and layer. This is a norm-matched random direction per layer and per token.
- **Table 2 "Zeros".** All source vectors are 0, so after erasure every pair carries b(0).
- **Table 2 "Random".** `random_vector_like` of [0, Δ^tar(1), Δ^tar(2)]. The first entry stays 0 because rescaling to a zero norm gives zero.

### 5.9 Geometry (Fig. 5) as coded

`run_subspace`, `run_experiment.py` L240–441:
- **Basis.** Δ(1), and Δ(2)⊥ = Δ(2) − (⟨Δ(2),Δ(1)⟩/‖Δ(1)‖²)Δ(1), computed on the flattened concatenation of the entity stack (2 tokens × layers × d) and the attribute stack (`orthogonalize`, `data_collection.py` L658–665).
- The paper says the basis is Δ(1) and Δ(2) (§4.2, App. G). In fact the y-axis is Δ(2)⊥.
- **Coordinates of Δ(2) in this basis.** `get_coeffs` gives **(0.943, 0.9999)** (notebook cell 52), so Δ(2) ≈ 0.943·Δ(1) + Δ(2)⊥. The diagonal arrow in Fig. 5 points to (0.943, 1.0), not to (1,1).
- **Grid.** 10×10 over [−0.5, 1.5]² for (η₁, ν₁) (`res=10`).
- **v₀ roots.** (0,0), (1,0), (0,1), (1,1), (.5,.5), (.5,.7), (.7,.1), (0,.5). The root (.2,.1) was computed but not plotted (cell 56).
- **Per cell.** 50 test-split contexts, attribute collapse, and distractor-calibrated accuracy averaged over the 2 queries (cell 54).
- **Erasure** subtracts Δ(1) from pair 1 using the n = 3 estimate (`test_subspace`, L594–612).
- **`cross_countries` flag.** False for the figure ("uncrossed"); it would swap which pair the attribute offsets go to.

### 5.10 Cross-task transfer (Table 2) as coded

`test_cross_mean_interventions_cyclic_subspace`, L864–930:
- **Inputs.** base_means = [0, Δ^tar(1), Δ^tar(2)] from CAPITALS (n = 3). param_means = [Δ^src(1), Δ^src(2), Δ^src(3)] from the source task's **n = 4** contexts.
- **Entity k:** Z_{E_k} → Z_{E_k} − Δ^tar_E(k) + Δ^src_E(k+1).
- **Attribute k:** Z_{A_k} → Z_{A_k} − Δ^tar_A(k) + Δ^src_A(π(k)+1).
- **Scoring.** Accuracy is scored against the **cyclically shifted** binding. A high score therefore means the model follows the binding written by the *source* vectors, which is stronger than the paper's description: "add back … with the hope of restoring performance" (§5, p.8).
- The injected IDs are the source task's b(1), b(2), b(3) relative to b(0). The target pairs never receive b(0).
- Attribute collapse is applied throughout.
- **Leakage (minor).** Evaluation contexts (prompt ids 0–99, unsplit vocabulary) are a subset of the 500 contexts used to estimate Δ^tar. The PARALLEL source uses the same name and country lists and the same prompt ids, so the same tokens appear in source estimation and evaluation. **[our inference]** The effect is probably small because Δ is a 500-sample mean and is content-paired where it matters, but it is not a held-out test.

### 5.11 MCQ suffix patching (App. E.1, Fig. 8)

- Target "L₀. O₀ / L₁. O₁". Source has the same option order with the labels swapped (`default_context(labels=[1,0], options=[0,1])`, L993–995).
- For width w ∈ {0,…,5}: overwrite the last w tokens of **each line** (ending at the line's final newline token) at all layers with the source's activations (`mcq_parallel_exchange`).
- Scored with median-calibrated accuracy against the swapped labels [1,0].
- **Paper inconsistency.** The text says "L₀ is A in the first context and B in the second", while its own example uses C/A (p.16).

### 5.12 Metrics

Φ^{(i)}_{E_k}(t) is the log-probability of token t at the answer position when E_k is queried in context i.
- **Mean log prob** (App. A): σ_{E_k} = (1/N)Σ_i Φ^{(i)}_{E_k}(A_k^{(i)}).
- **Top-1 accuracy** (App. A): (1/N)Σ_i 𝟙[k = argmax_l Φ^{(i)}_{E_k}(A_l^{(i)})], argmax over in-context attributes only. **Defined but never reported anywhere.**
- **Median-calibrated accuracy** (App. A; Zhao et al. 2021):
  - m(A_l) = median_{i,k} Φ^{(i)}_{E_k}(A_l^{(i)}), and Φ̃ = Φ − m(A_l).
  - Accuracy = (1/N)Σ_i 𝟙[k = argmax_l Φ̃^{(i)}(A_l^{(i)})].
  - Code: `reduce_balanced_acc`. The median is taken over (query, sample) for each answer column, **separately within each intervention condition and each cyclic shift**.
  - Used for Fig. 6, Table 2 and Fig. 8.
- **Distractor-calibrated accuracy** (code only; `reduce_distractor_acc`, notebook cell 1):
  - The offset m_null(A_l) is the median over samples of Φ^{(i)}_{E_null}(A_l^{(i)}), where E_null is an entity absent from the context.
  - Used for **Table 1, Table 3 and Fig. 5**. Table 1's caption says "Mean calibrated accuracies"; App. A implies the median version.
- **What calibration buys and hides** (**[our inference]**).
  - Both calibrations subtract a query-independent offset per attribute slot, estimated inside the same intervened condition. That removes position bias without using labels, which is the authors' argument in App. C, p.13.
  - But the score then records only whether the *query-dependent* part of the log-probs points the intended way. It does not record whether the model would *output* the intended attribute.
  - A condition where the model always prefers one attribute but slightly less so for one query can still score 1.0.
  - With uncalibrated top-1 never reported, the behavioural size of every accuracy-based result (Tables 1–4, Figs. 5–6) is unknown. Mean log-probs are given only for Table 2 and the heatmap and line figures.

### 5.13 The necessity argument (App. B)

- Fix n = 2 and define the binding ID mechanism as two claims:
  - **Representation**: there exist Γ_E and Γ_A such that substituting Z_{E_k} → Γ_E(e,k) yields the belief c/.{E_k → e}; likewise for attributes, and the substitutions compose.
  - **Query**: for any permutations π_E, π_A of {0,1}, a context made of [Γ_E(e₀,π_E(0)), Γ_A(a₀,π_A(0)), Γ_E(e₁,π_E(1)), Γ_A(a₁,π_A(1))] is read as e₀↔a₀, e₁↔a₁ if π_E = π_A, and crossed otherwise.
- Factorizability gives Representation: define Γ_E(e,k) := Z_{E_k}(c) for any c with E_k(c) = e.
- Representation plus position independence gives Query: substitute, then permute positions freely.
- **[our inference]** The argument is informal. It assumes factorizability holds for *all* contexts and position independence for *all* permutations, while each was tested on 100 sampled contexts with one swap pattern.
- **[our inference]** "Position" here means RoPE position only. Any order-of-mention code the model writes into the residual stream (for example "this is the second name") survives the RoPE swap and *is* a binding ID under these definitions. So the argument separates binding IDs from *RoPE position* and from *content*. It does not show that IDs are anything more abstract than an ordinal slot code. The authors' own definition, "identify the k-th abstract binding ID with the integer k" (p.4), is consistent with that reading.

---

## 6. Evidence table

**Shared caveats for every row.**
- The unit of replication is one model, one template per task, and N sampled contexts drawn deterministically by prompt id.
- No seeds are varied and no error bars are reported.
- Binomial standard errors (SE) below are **[our inference]**, assuming independent contexts. The 200–600 outcomes per cell come from 100 contexts, so the effective N is about 100.

| # | Claim | Decisive comparison | Result | Replication unit / denominator | Uncertainty | Location | Remaining alternative |
|---|---|---|---|---|---|---|---|
| C1 | **[author result]** LLaMA-30b solves CAPITALS n = 2 | none needed | Control 0.99 (E₀) / 1.00 (E₁) calibrated; mean log prob of the correct capital −0.39 (E₀→A₀), −0.67 (E₁→A₁) vs −3.95 and −2.71 for the wrong one | 100 test-split contexts × 2 queries | SE ≈0.01 | Table 1 p.7; Fig. 3 p.5 | — |
| C2 | **[author result]** Entity factorizability | Fig. 3: Entity(a) vs None | After swapping Z_{E₀} with Z_{E′₀}, querying E′₀ gives A₀ at −0.39 (was −1.57). Querying E₀ falls to −1.56/−2.12 (A₀/A₁), the "unknown entity" pattern. E₁ is unaffected (−0.66). Side b is symmetric: E′₁→A₁ −0.66. | 100 contexts, one per cell | none reported | Fig. 3 p.5 | **[our inference]** Source and target slots and positions are identical, so this shows content can be swapped while the slot is kept. It does not by itself show a slot code. |
| C3 | **[author result]** Attribute factorizability | Fig. 3: Attribute(a) vs None | Querying E₀ now gives A′₀ at −0.44 (A₀ −8.29); E₁ still gives A₁ at −0.63. Side b: E₁→A′₁ −0.72; E₀→A₀ −0.39. Both(a): E′₀→A′₀ −0.43. | 100 | none | Fig. 3 p.5 | — |
| C3b | **[author result]** Factorizability on other tasks | Figs. 11–13 vs Fig. 3 | PARALLEL: Attr(a) E₀→A′₀ −0.49; Ent(a) E′₀→A₀ −0.41; Both(a) E′₀→A′₀ −0.48. SHAPES: −0.74, −0.52, −0.67. FRUITS: −0.92, −0.96, −0.90. Side b similar (e.g. PARALLEL Both(b) E′₁→A′₁ −0.58). | 100 each | none | Figs. 11–13 pp.20–21 | — |
| C3c | **[author result]** **Failure:** BIOS attribute factorizability | Fig. 14 | The Attribute swap leaves E₀→A₀ at −4.80 (unchanged from None, −4.80); the predicted A′₀ cell is −9.86. The entity swap works: E′₀→A₀ −4.85 (from −5.16). | 100 | none | Fig. 14 p.21; text p.20 | **[author interpretation]** The attribute spans many tokens and only its first token is swapped. **[our inference]** With female-only bios, the first token is often "She", the same token across attributes (`biosbias.py`). |
| C4 | **[author result]** Entity position independence | Fig. 4 top: swapped (green) vs control (grey) | Read from the plot: E₀ stays near −0.3 on A₀ and about −4.2 on A₁; E₁ stays near −0.6 on A₁ and about −2.8 on A₀, across the whole sweep from X_{E₀}−10 to X_{E₁}+9 | 100 contexts per offset | none | Fig. 4 p.5 | Frozen context: only the question tokens' view of the keys moves. Any ordinal code inside the residual is untouched by design. |
| C5 | **[author result]** Attribute position "little change" | Fig. 4 bottom | Read from the plot. Control: E₁ prefers A₁ (≈−0.55) over A₀ (≈−2.7). Swap: A₁ ≈−1.0 vs A₀ ≈−1.8, so the margin falls from about 2.2 to about 0.8 nats. The curves cross about 6 tokens *past* the swap. E₀ is unaffected (A₀ ≈−0.35). | 100 | none | Fig. 4 p.5 | **[author interpretation]** The shift is a "position-dependent bias" that is query-independent (attributes moved later always gain) and is attributed to RoPE long-term decay (App. C). **[our inference]** The direction pattern does look query-independent, but the size is not small, and the mean-intervention tests remove this cue through the collapse (§5.7). |
| C5b | **[author result]** Local position independence on other tasks | Figs. 15–18 | PARALLEL and SHAPES flat. FRUITS: attribute swap moves E₁→A₀ from about −3.5 to about −2.8 while E₁→A₁ stays near −0.6. BIOS: entity swap shrinks the E₀ margin from about 2.4 to about 1.1 nats (A₀ −4.65→−5.05, A₁ −7.1→−6.15), sign preserved. | 100 | none | pp.22–23 | Only ±2 offsets around each condition |
| C6 | **[author result]** Additivity: mean interventions swap the binding (n = 2) | Table 1 left: Attribute and Entity vs Control | Accuracy under the original binding: Attribute 0.00 / 0.03; Entity 0.00 / 0.01; Control 0.99 / 1.00 | Δ from 500 train-split contexts; test on 100 disjoint-vocabulary contexts × 2 queries | SE ≈0.01–0.02 | Table 1 p.7; notebook cell 19 (identical numbers) | **[our inference]** Calibrated accuracy only, null-query calibration, and attribute collapse; magnitude in nats not given. Content independence is supported by the train/test vocabulary split (code). |
| C6b | **[author result]** Cancellation check | Table 1: Both vs Attribute and Entity | Both = 0.97 / 0.99 | same | | Table 1 | Strong internal control against "the intervention just breaks retrieval" |
| C7 | **[author result]** Direction specificity | Table 1 right: norm-matched random vs Δ | Random: Attribute 0.98/1.00, Entity 0.98/1.00, Both 0.97/1.00. Notebook cell 24 gives E₀ Attribute 0.97, from an unseeded re-draw. | 100 | | Table 1 p.7 | **[our inference]** A random direction in 6656 dimensions at each of 60 layers is a weak control. It rules out "any perturbation of this size". It does not rule out "any *structured* mean difference between two slots or contexts" (e.g. a mean difference between two non-binding conditions); that control was not run. |
| C8 | **[author result]** Binding subspace and metric | Fig. 5: accuracy as v₁ moves away from v₀ | Accuracy is about 0.5 (white) near v₀ and reaches about 1.0 (red) far away, including outside the convex hull of b(0), b(1), b(2) and at negative coefficients. Panel (0,1) shows light blue (<0.5) near v₀. | LLaMA-13b; 50 contexts per cell × 2 queries; 10×10 grid × 8 roots | SE ≈0.05 per cell | Fig. 5 p.7; App. G pp.17–18 | **[our inference]** The confusion regions are elongated and anisotropic; for several roots ((0,0), (0,1), (0,.5), (.5,.7)) the white band runs almost the full height of the y (Δ(2)⊥) axis. Distinguishability is driven mainly by the Δ(1) coordinate, which looks more like a near-one-dimensional ordinal scale than an isotropic metric. The basis is mislabelled in the paper (§5.9). |
| C9 | **[author result]** Generality across tasks (n = 3, cyclic) | Fig. 6 right: intervention vs control | Read from the plot, control / entity / attribute: CAPITALS 1.00/0.98/0.94; PARALLEL 0.99/1.00/1.00; SHAPES 1.00/0.88/0.77; FRUITS 0.93/0.92/0.87; BIOS 0.71/0.44/**0.18** | 100 × 3 queries × 2 shifts, test split | chance 0.33 | Fig. 6 p.8 | BIOS attribute is below chance, as the authors predicted (D.5). Attribute bars use collapse; control bars do not. |
| C10 | **[author result]** Generality across models and scale | Fig. 6 left | Read from the plot. Pythia 70m→12b control ≈.35, .40, .59, .63, .80, .96, .89, .89; attribute and entity interventions ≈.33→.53 (410m)→.57/.53 (1b)→.60/.59 (1.4b)→.72/.68 (2.8b)→.69/.67 (6.9b)→≈.71/.76 (12b). LLaMA 7/13/30b control .87/.97/1.00, entity .75/.93/.98, attribute .71/.89/.94. | as C9 | chance 0.33 | Fig. 6 p.8 | **[our inference]** Pythia interventions plateau around 0.7, so the swap is only partial. "Every sufficiently large model" (abstract) has no threshold, and Pythia never reaches LLaMA-level switching. |
| C11 | **[author result]** Cross-task transfer into CAPITALS | Table 2: source Δ vs Zeros vs Random | Calibrated accuracy / mean log prob of the intended answer: CAPITALS 0.88/−1.01; PARALLEL 0.87/−1.07; SHAPES 0.71/−1.18; FRUITS 0.80/−1.21; BIOS 0.47/−1.64; Zeros 0.30/−1.86; Random 0.31/−2.15. The notebook gives BIOS 0.46/−1.68 and Random 0.28/−2.20. | 100 × 3 × 2, unsplit | chance 0.33 | Table 2 p.8; cell 36 | Only one target task. Source IDs are b(1..3) from n = 4 contexts. Collapse everywhere. Evaluation contexts overlap the target-Δ estimation contexts. **[our inference]** A mean log prob of −1.01 for the intended answer (about 0.36 probability on average in log space) means the model is far from outputting it confidently. |
| C12 | **[author result]** Not universal: direct binding in MCQ | Fig. 8: accuracy vs width of the copied line suffix | Read from the plot: whole line (C) 0.91; from ". " 0.90; "Neg…" 0.87; "ative⟨WS⟩" 0.83; "⟨WS⟩" only 0.37; control 0.08. LLaMA-30b "too out of distribution" for this format. | tulu-13b; 100 | none | App. E.1 pp.16–17 | **[our inference]** Model (instruction-tuned tulu) and task (MCQ) change together, so whether direct binding comes from the task, the instruction tuning or the token form cannot be separated. No mean intervention or factorizability test is run on tulu for the entity tasks. |
| C13 | **[author result]** ONEHOP: binding-ID-edited representations still support a further reasoning step | Fig. 9, Table 3, Fig. 10 | Base margin is small: E₀→A₀ −2.12 vs −2.64 to −2.88; E₁→A₁ −2.11. Factorizability signs hold (e.g. Attr(a) E₀→A′₀ −2.07; Ent(a) E′₀→A₀ −2.16; Both(a) E′₀→A′₀ −2.15). Table 3: Control 0.73/0.79, Attribute 0.25/0.28, Entity 0.24/0.26, Both 0.71/0.77. **Unreported** n = 3 cyclic: entity 0.593, attribute 0.607 (notebook cell 79), no control run. | LLaMA-65b fp16; 100 | none | App. H pp.18–19 | The printed Fig. 10 is the PARALLEL figure (§7.3). The repo's ONEHOP figure shows ≈−1.15 vs ≈−1.5, preserved under swap. "All of our results still hold" (p.18) leaves out the weak n = 3 number. |
| C14 | **[author result]** Three-term binding | Table 4 | Control 1.00 in all 12 rows; Attribute 0.00–0.03; Entity 0.00–0.01; Both 0.99–1.00 | model, n and sample size unstated; no code | none | App. I pp.19–20 | The fixed term is constant across statements, so this is two-term binding with a distractor. Which tokens count as "entity" and "attribute" is unstated. The text attributes the result to "ONEHOP", an apparent typo. |
| C15 | **[author interpretation]** Factorizability + position independence imply the binding ID mechanism | logical argument | — | — | — | App. B pp.12–13 | See §5.13: it does not separate binding IDs from an ordinal slot code computed by the model. |
| C16 | **[author interpretation]** Larger models have more structured, interpretable representations; LLaMA and Pythia converge on the same strategy | Fig. 6 left | — | 2 families | — | §7 p.9 | Speculation (the authors' word). Pythia's structure is weaker, and the task-solving ability itself scales, confounding "structure" with "competence". |

---

## 7. Controls & failures

### 7.1 Controls that were run

- **[author result] No-intervention controls** in every experiment.
- **[author result] "Both" cancellation** (Tables 1, 3, 4). Swapping entity and attribute IDs together restores accuracy. This is the strongest guard against the reading "the intervention just damages retrieval".
- **[author result] Norm-matched random directions** (Table 1 right; Table 2 Random), matched per layer and per token.
- **[author result] Zero-vector baseline after erasure** (Table 2 Zeros, 0.30). Together with Fig. 5's ≈0.5 near v₀, this confirms that the erasure step removes the binding signal.
- **[author result] Surface-form variation.**
  - PARALLEL separates the entity from its attribute's sentence.
  - SHAPES swaps parts of speech and puts the attribute first.
  - FRUITS changes the attribute domain.
  - BIOS uses multi-token attributes.
  - ONEHOP needs an extra inference step.
  - MCQ is a different format.
- **[author result] Off-context queries** E′₀, E′₁ in the factorizability heatmaps act as built-in negative controls: before a swap they spread probability over the in-context attributes.
- **[our inference, from code] Held-out vocabulary.** Δ is estimated on the first half of the name and country lists and tested on the disjoint second half (Table 1, Figs. 5–6). That is real evidence that Δ is content-independent, and the paper never mentions it.
- **[author result] Bias handling.** Calibration and the position collapse (App. C) are argued not to leak labels, because neither uses the ground truth.

### 7.2 Failures, weak conditions and negative results (keep these)

- **BIOS** (multi-token attributes):
  - attribute factorizability fails (Fig. 14);
  - attribute mean intervention 0.18 and entity 0.44 against control 0.71 (Fig. 6 right);
  - BIOS Δ transfers to CAPITALS at only 0.47 (Table 2);
  - BIOS entity position swap shrinks the margin (Fig. 18).
- **SHAPES and FRUITS** transfer only partially (0.71, 0.80), and SHAPES attribute switching is 0.77 (Fig. 6 right).
- **Small models**: Pythia below 1b sits near chance even on control; Pythia 2.8b–12b interventions reach only about 0.67–0.76 (Fig. 6 left).
- **MCQ**: LLaMA-30b cannot do the reversed format; tulu-13b uses direct binding (App. E).
- **ONEHOP** (LLaMA-65b):
  - margins of about 0.5 nats (Fig. 9);
  - control accuracy 0.73/0.79 (Table 3);
  - n = 3 cyclic interventions only 0.59/0.61, which appears only in the notebook (cell 79).
- **Attribute position sensitivity**: in CAPITALS (Fig. 4 bottom) and FRUITS (Fig. 17) the attribute's RoPE position visibly moves log-probs. The authors classify this as bias.
- **Overclaim in wording**: "these random vectors have no effect on the model behavior" (p.7) is supported only as calibrated accuracy.

### 7.3 Code–paper discrepancies and errors in the paper

All **[our inference]** from comparing the code at `fb7608d` with the paper.

1. **Attribute position collapse** is applied in every attribute mean intervention, in Table 2 and in Fig. 5, but is not stated in §4.1, §4.2, §5 or the captions (`data_collection.py` L562, L646, L851, L920).
2. **Metric.** Table 1, Table 3 and Fig. 5 use null-query ("distractor") calibration (`reduce_distractor_acc`), not the median calibration of App. A. Table 1's caption says "Mean calibrated accuracies".
3. **Δ estimator.** The paper's 𝔼_{c,c′}[Z_{A_k}(c) − Z_{A_0}(c′)] suggests independent contexts. The code pairs each context with its cyclic rotation (same tokens, different slot) for n = 2 and n = 3.
4. **Train/test vocabulary split** for Δ estimation versus evaluation is unstated (it strengthens the claims).
5. **Fig. 5 basis** is [Δ(1), Δ(2)⊥], not [Δ(1), Δ(2)]. Also unstated: Δ(2) = 0.943·Δ(1) + Δ(2)⊥, 50 samples per cell, 10×10 grid over [−0.5, 1.5]², and one computed root that was not plotted.
6. **Table 2 procedure**: cyclic permutation of the source IDs, source IDs b(1..3) taken from n = 4 contexts, and collapse in every condition, all unstated. The released notebook output differs slightly from the printed table: BIOS 0.46/−1.68 vs 0.47/−1.64; Random 0.28/−2.20 vs 0.31/−2.15.
7. **Fig. 4 x range** is X_{E₀}−10 … X_{E₁}+9 in code and figure, versus {X_{E₀},…,X_{E₁}} in the text (p.6).
8. **The printed Fig. 10** ("Position independence for ONEHOP", p.19) has the same curves, levels and axes as **Fig. 15 (PARALLEL, p.22)**: about −0.3/−0.6 correct and about −4 incorrect, checked by stacking the two crops. Those levels cannot be ONEHOP, whose log-probs are about −2 to −3 (Fig. 9). The repo's `figures/local_position_ONEHOP.pdf` (md5 `43632f87…`, distinct from PARALLEL's `66463210…`) shows about −1.15 vs −1.5 instead, with the binding preserved under both swaps. The printed figure is most likely a file mix-up.
9. **ONEHOP settings**: attribute width 2 (`--country_width 2`), question-context sizes 4/2/3 for factorizability / position / means, and fp16, none stated.
10. **Three-term binding** (App. I): no code; model unstated; the text says "ONEHOP only requires looking up and copying countries" where the three-term task is meant (p.20).
11. **App. H** says mean interventions are in "Fig. 3"; they are in Table 3 (p.18).
12. **Template mismatches**:
    - FRUITS question wording and the stray "respectively" (D.3);
    - SHAPES answer prefix ("shape is" vs "shape is the", D.4);
    - MCQ uses "label. option" in code vs "label: option" in the paper (App. E);
    - CAPITALS line break (D.1).
13. **MCQ label description** is internally inconsistent ("L₀ is A in the first context and B in the second" vs the C/A example, p.16).
14. **BIOS** uses female bios only and a 70/30 split, both unstated.
15. **Precision**: LLaMA-65b ran in fp16, everything else in fp32, unstated.

### 7.4 Controls not run

All **[our inference]**.

- **Attribute mean intervention without the position collapse, and collapse alone without a mean intervention.** Without these, one cannot tell how much of the attribute switch needs the RoPE position cue removed. This matters because Fig. 4 bottom shows that cue is non-trivial.
- **Uncalibrated top-1 accuracy, and mean log-probs, for Tables 1, 3 and 4 and Figs. 5–6.** These would show whether the intervened model would actually *output* the swapped attribute.
- **A structured-null control** for the Δ direction: for example Δ estimated with shuffled slot pairing, Δ between two templates with the same slots, or Δ from a non-binding contrast of matched norm. Only isotropic random directions were tested.
- **Layer localisation.** All layers are always patched together. There is no per-layer or layer-range sweep, so where IDs are written or read is unknown. There is also no head-level analysis; the paper speculates about heads in §4.2.
- **Intervention without freezing** the context (an ordinary forward pass with additive edits). All results hold only under freezing.
- **Side-effect checks**: other in-context facts, unrelated questions, perplexity. Only "Both" partially covers this.
- **Variance and statistics**: no confidence intervals, no resampling of contexts, no second Δ estimate.
- **Template paraphrases within a task**: each task has exactly one template.
- **Scale and realism**: more than 3 entities; multiple mentions of an entity; pronouns and coreference; long or narrative contexts; natural text; chat-formatted prompts; instruction-tuned models on the entity tasks.
- **Read-out side**: the query mechanism is explicitly left for future work (App. C, p.14).
- **Cross-task transfer into targets other than CAPITALS.**
- **Pythia and tulu checks** of factorizability and position were not reported (README: "You may add the flags …").

---

## 8. Interpretation boundary

**Established, under these conditions.** Conditions: LLaMA-30b (13b and 65b in sub-experiments); one template per task; single-token entities and attributes; n = 2 or 3; residual streams patched at all layers with the context frozen; next-token log-probability at one position; calibrated accuracy.
- **[our inference]** Per-token, all-layer activation stacks at an entity (two tokens) and an attribute (one token) carry two kinds of information. One is content-specific (factorizability). The other is slot-specific, approximately additive, and content-independent. Mean intervention works across disjoint vocabulary halves, and the slot-specific part is what the question tokens use to pair entities with attributes.
- **[our inference]** Swapping or erasing that slot part changes or abolishes the pairing (calibrated). Random norm-matched perturbations do not.
- **[our inference]** The RoPE positions of the entity tokens matter little. Attribute positions matter somewhat.
- **[our inference]** Slot vectors from other single-token templates partly substitute for CAPITALS slot vectors.
- **[our inference]** On the evidence ladder this is rung 4, a causal claim, with good internal controls (cancellation, held-out vocabulary) and two specificity gaps (§7.4).

**Not established.**
- How binding IDs are computed or read; no circuit is identified. Rung 5 is not reached.
- That IDs are "abstract" in any sense beyond "not RoPE position and not token content". They are equally consistent with a model-computed order-of-mention code (§5.13).
- Behavioural magnitude: uncalibrated outputs are never shown.
- Generality to multi-token attributes (the paper's own evidence is negative), more than 3 entities, natural or narrative text, instruction-tuned models (the only one tested used a different mechanism), or chat formats.
- Whether the effect survives without context freezing, or at a single layer.

**Separating the kinds of evidence.**
- *Readability*: no probes are used. Nothing is claimed about linear decodability beyond the mean differences.
- *Predictive information*: none; there is no predictor of behaviour from activations.
- *Causal contribution*: yes, by activation patching and mean interventions, within the frozen-context regime.
- *Training-time effects*: none. No training, no weights, no gradients.
- *Deployment monitoring*: none.

---

## 9. Connection to our project

The project asks what decides whether a behaviour learned from a story stays specific to its character, appears under related personas, or changes the default Assistant. The immediate goal is to separate competing explanations; the larger goal is to predict transfer and causally redirect it without simply blocking learning. *Analogy is not shared mechanism*: this paper studies in-context, inference-time binding, and the project studies effects of fine-tuning stored in weights.

### 9.1 Hypotheses this paper motivates

- **[our inference] H-slot (a constraint more than a hypothesis).** Binding IDs as measured here are content-free and recomputed per context by order of mention (§5.5, §5.13). They therefore cannot, by themselves, carry *which character* a trained behaviour belongs to from one context to another.
  - After fine-tuning, character-specificity at test time must be keyed on something else: the character's *content* representation (f_E(e) in Eq. 1, i.e. name or identity features), on cues that recreate the story's context, or on role structure.
  - Predicted consequence: editing binding IDs at *test time* should not move a weight-stored, story-learned behaviour between characters, unless the behaviour is re-derived in-context from a story that is present in the prompt.
- **[our inference] H-train-binding.** During fine-tuning on a story with several characters, the in-context binding state at trait-bearing tokens (which entity the trait is bound to) may decide which representation the gradient updates. That in turn could decide whether the trait attaches to the character's identity features (specific transfer) or to features shared with the Assistant or speaker role (broad transfer).
  - The paper gives **no evidence** for or against this. It only supplies an intervention, the entity or attribute mean intervention, that could manipulate binding state during training.

### 9.2 What would have to carry over before this paper informs an intervention on story fine-tuning

All **[our inference]**. Each item below is untested in the paper.
1. **Presence in our model and format.** Factorizability and the mean-intervention swap must hold in the model family and size we train, on our story format. That means:
   - chat or instruction tuning, when the story is presented that way. The paper's only instruction-tuned model used direct binding, on a different task.
   - multi-sentence narrative;
   - character names that are multi-token or repeated, plus pronouns and coreference;
   - more than 3 characters.
2. **Traits as attributes.** Story traits are multi-token, distributed across sentences, and often expressed through actions. The paper's single multi-token test (BIOS) **failed** for attributes. The binding of a *trait* to a character must be shown to have an additive, swappable slot component; one-token attributes are not enough.
3. **No freezing, and at training time.** The swap must work in an ordinary forward pass, additive at all layers or at a chosen layer set, without re-imposing clean context values each layer. It must also remain well-defined while gradients flow, because a training-time intervention cannot freeze the context the way the paper's evaluation does.
4. **Behavioural, not only calibrated, switching.** Uncalibrated accuracy and log-probs must show the model actually outputs the swapped association.
5. **The Assistant and role tokens.** It must be shown whether the chat Assistant (or the speaker role) behaves as a bound entity with a binding ID, or as a separate privileged representation. The paper says nothing about roles.
6. **The causal link from in-context binding at training time to what is stored.** This is the crux, and the paper gives zero evidence on it.
7. **Persistence.** If specificity after training is keyed on character identity features rather than binding IDs (H-slot), then the right handle is the content representation f_E(e), and binding-ID tools serve only to measure the in-context state during training.

**What the paper gives no evidence about**: fine-tuning or weight updates; generalisation across contexts; personas or characters; the Assistant; multi-turn or chat formats; long contexts; trait-like or behavioural attributes; whether binding errors drive misattribution; anything about default-behaviour shifts.

### 9.3 Baselines our work would need before using these tools

All **[our inference]**.
- Reproduce, in our target model and on story-format prompts, the CAPITALS n = 2 mean intervention with:
  - uncalibrated top-1 and log-probs;
  - a version without collapse and a collapse-only version;
  - a norm-matched random control and a structured-null control (shuffled-pairing Δ);
  - Δ fitted on held-out names.
- Then do the same with characters and multi-token traits.
- Behavioural baseline: does the model, given the story in context, attribute the trait to the right character (plain prompting)? If not, there is no binding to manipulate.

### 9.4 Duplication with our experiments

**[unresolved]** Not checked. By instruction I did not open `experiments/` or the session folders.

### 9.5 One discriminating follow-up

**[proposed experiment] Binding-ID swap during story fine-tuning.**
- **Precondition (inference only, about one day).** On two-character story prompts ("X … [trait T behaviour] … Y … [neutral]. Who …?") in the target model:
  - estimate Δ_E(1) with the paired cyclic-rotation estimator (§5.5) on held-out names;
  - show the entity mean swap moves the *uncalibrated* attribution of T from X to Y in an ordinary forward pass, without freezing, with random and shuffled-Δ controls null.
  - If this fails, stop: the training-time version cannot be interpreted.
- **Main experiment.** Fine-tune (LoRA, matched budget) on stories where X shows trait T, in four arms:
  1. plain;
  2. with the entity mean swap applied at X's and Y's mention tokens on every training forward pass;
  3. with a norm-matched random edit at the same tokens;
  4. a text-swap positive control, where Y shows T in the text.
- **Evaluate** T under the X persona, the Y persona, related personas, and the default Assistant.
- **Predictions.**
  - If transfer follows in-context binding at training time (H-train-binding), arm 2 shifts T toward Y, as arm 4 does.
  - If specificity follows identity content (H-slot), arm 2 matches arm 1, because the gradient still flows through X's name features. A follow-up content-swap (exchanging X's and Y's f_E) would then redirect it.
  - If Assistant transfer comes from learning the trait text regardless of binding, the Assistant rate is the same in arms 1–3.
- **Decision rule, stated before running.** Arm 2's Y-persona trait rate must move at least halfway toward arm 4's, while arm 3 does not move. Otherwise binding IDs are not a training-time handle in this setting.

---

## 10. Open questions

**The authors' open questions:**
- How the query mechanism works, and whether the size of the position-dependent bias can be predicted from RoPE parameters (App. C, p.14).
- Which circuits, for example attention heads whose quadratic form supplies the metric, process binding vectors (§4.2, p.8).
- How Hernandez et al.'s bound representations relate to direct binding (§6, p.9).
- Which other "primitive skills" with interpretable mechanisms exist (§7, p.9).
- Whether representations converge toward an "ultimate representation" with scale (§7, p.9).

**Our open questions** (all **[unresolved]**):
1. Do attribute mean interventions still switch binding without the attribute position collapse (§5.7, §7.4)?
2. What are the uncalibrated top-1 accuracies for Table 1, Table 4 and Figs. 5–6 (§5.12)?
3. Is the binding ID anything beyond an order-of-mention code? Test by mentioning the same entity twice, inserting distractor sentences, or using contexts where order and ID are decoupled (§5.13).
4. Why is Fig. 5's confusion region elongated along Δ(2)⊥? Is the effective binding scale close to one-dimensional (C8)?
5. Why do the ONEHOP n = 3 interventions reach only 0.59/0.61 (notebook cell 79), and why was this omitted (C13)?
6. Is MCQ direct binding caused by the instruction tuning or by the task format (C12)? This matters directly for chat models.
7. Which model, n and sample size were used for Table 4, and which tokens were treated as "entity" and "attribute" (C14)?
8. Does anything survive with multi-token attributes if all attribute tokens are intervened, not just the first? BIOS was tested with width 1 only.
9. How do binding IDs behave with more than 3 entities? Table 2 only extrapolates to b(3).

---

## 11. Reproduction checklist & remaining doubts

### 11.1 Reproduction checklist (main experiments)

1. **Environment.** Python 3.10; `pip install -r repo/requirements.txt`.
   - Set `LLAMA_WEIGHTS` to a directory with `7B/ 13B/ 30B/ 65B/` HF-converted LLaMA-1 weights.
   - For MCQ, set `TULU_WEIGHTS` with `tulu-merged-13b/`.
   - `coref/datasets/raw/biosbias.json` is shipped; `BIOS_PKL` is needed only if it is missing.
   - Use the vendored `transformer_lens/`, which provides the `hook_rot_k` hook used for position interventions.
2. **Main run** (README). `python -m scripts.run_experiment --model llama-30b-hf --force_time results --num_devices 4 --cyclic --factorizability --position --means_intervention --means_intervention_baseline --all_tasks_means --cross_tasks_means --cross_tasks_subspace --baseline --local_position`.
   - **Do not** pass `--force_compute` unless you *want* to reuse caches; the flag is inverted (L866).
   - `--cross_tasks_means` produces an extra non-subspace cross-task analysis that the paper does not use.
3. **Fig. 5.** `--model llama-13b-hf --subspace`. **Fig. 6 left**: loop over the Pythia models and LLaMA 7b/13b with `--capitals_means --cyclic --capitals_baseline`.
4. **ONEHOP.** `--model llama-65b-hf --country_width 2 --onehop` (fp16). **MCQ**: `--model tulu-13b --country_width 2 --mcq`.
5. **Analysis.** Run `paper_plots.ipynb` with `time_tag='results'`. Expected values:

   | Result | Notebook cell | Expected |
   |---|---|---|
   | Table 1 | 19 | `0.99 & 0.00 & 0.00 & 0.97` / `1.00 & 0.03 & 0.01 & 0.99` |
   | Table 1 random | 24 | about 0.97–1.00 |
   | Table 2 | 36 | `0.88 0.87 0.71 0.80 0.46 0.30 0.28` / `−1.01 −1.07 −1.18 −1.21 −1.68 −1.86 −2.20` |
   | Fig. 5 coefficients | 52 | 0.943, 0.9999 |
   | Table 3 | 78 | `0.73 0.25 0.24 0.71` / `0.79 0.28 0.26 0.77` |
   | ONEHOP n = 3 | 79 | 0.593 / 0.607 |

6. **Checks to add** when reproducing (§7.4):
   - print the token strings at every intervened position;
   - confirm that intervened positions fall before `dependent_start`;
   - run the identity intervention twice and compare (noise floor, especially for the fp16 65b run);
   - report uncalibrated top-1 and log-probs;
   - run attribute interventions without collapse, and collapse alone;
   - add a shuffled-pairing Δ control.
7. **Not reproducible from the release**: Table 4 (no code); the exact random-baseline numbers (unseeded).

### 11.2 Remaining doubts (ranked by how much they limit what the paper establishes)

1. **The size of the behavioural effect is hidden by the metrics and the setup.** Accuracy-based results use calibration fitted inside each intervened condition. Attribute interventions also remove the RoPE position cue. All interventions freeze the context at every layer. The paper therefore establishes that the *query-dependent* signal follows the swapped binding under a stacked, frozen patch. It does not establish how strongly the model's *output* follows, or whether this works in a normal forward pass.
2. **Narrow scope relative to stories.**
   - Only single-template, single-token, 2–3-entity tasks succeed.
   - The one multi-token-attribute task fails for attributes.
   - The one instruction-tuned model, on its one task, uses a different mechanism.
   - Nothing touches training.
   - What the paper shows is a clean in-context slot code. Whether that slot code governs anything in story fine-tuning is entirely open (§9).
3. **"Abstract binding ID" vs "order-of-mention code".** The Δ estimator literally measures the slot k vs slot 0 difference for the same token, and the position test only removes RoPE information. The data are equally well described as the model writing an ordinal code at each mention. That matters for whether binding IDs could ever be tied to a specific character across contexts; they could not.
4. **Reporting errors**: the wrong Fig. 10, an unreported weak ONEHOP n = 3 result, no code or model for Table 4, and the unstated settings listed in §7.3. None overturns the main CAPITALS results. Together they lower confidence in the generality appendices (H, I) more than in §3–§5.
