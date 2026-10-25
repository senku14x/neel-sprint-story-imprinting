# Slot Machines: How LLMs Keep Track of Multiple Entities — research notes

**Tags.** **[author result]** = measured and reported by the authors. **[author interpretation]** = the authors' reading of a result. **[our inference]** = our reading. **[proposed experiment]** = something we suggest running. **[unresolved]** = the paper does not settle it. Values marked "≈" were read off the figures by us (method in §1.4); every other number is quoted from the text. Page numbers are the paper's printed numbers, which match the PDF page indices.

## Summary

- **On Qwen3-32B (layer 45 of 64, sentence-final period tokens, eight four-sentence character descriptions written by Claude Sonnet-4.5), a probe can read the previous character's trait from the current character's tokens, using a readout different from the one that reads the current character's trait** (§2.2, Fig 3, Table A1) **[author result]**. Accuracy on the previous character falls from ≈90% early in the passage to ≈54% by the eighth character (our estimate from Fig 3; chance is 7%).
- **On short six-item "Name is trait." lists, patching every layer at the next entity's four tokens moves a "who came after Alice?" answer by ≈4.6 logits (key-only patch). The same patch moves "is anyone tall?" and "the tall character is named ___" by ≈0** (Figs 5, 7, 8) **[author result]**. A mean-difference "prior-entity" steering vector moves a "do adjacent traits conflict?" yes−no logit gap by ≈0.06 logits (Fig 6) **[author result]**.
- **Behaviorally, most models misparse "Alice prepares and Bob consumes food. Bob prepares and Alice consumes drinks."** Qwen3-32B scores ≈58% (chance 50%), Gemini-3-Pro ≈95% and Claude Opus-4.5 ≈91% (Fig 9) **[author result]**. Per-question results (Fig A5) show that weak models mostly answer the first object ("food"), which is not the pattern the authors' "one binding per token" account predicts **[our inference]**.
- **The causal experiments never intervene on the probe-identified slot directions.** They patch or steer whole token positions, on a different prompt format from the one the probes were trained on. "Slot X is (not) used" therefore means "information at the next entity's positions is (not) used" **[our inference]**.
- **For our project, the paper offers a method (the multi-slot probe), a warning (a probe can decode information the model does not use), and evidence that non-current entity information decays quickly.** It offers no training-time evidence, no long-text evidence, and mechanistic claims for one model only **[our inference]**.

---

## 1. Identity & coverage

### 1.1 Citation and version
- **Paper:** Paul C. Bogdan (Anthropic Fellows Program), Jack Lindsey (Anthropic). *Slot Machines: How LLMs Keep Track of Multiple Entities.* arXiv:2604.21139v1 [cs.CL; cross-listed cs.LG], submitted 22 Apr 2026. Preprint, no venue stated. License CC BY 4.0.
- **Version read: v1.** It is the only version on the arXiv abstract page as of 2026-10-23 (page fetched 2026-10-23).
- **File:** `paper.pdf` (27 pages, sha256 `2f6407d856e5829019340f7ded21d94a3ffd90f005c00f372c8615ebd14a8a25`); `paper.txt` is its text extraction.
- **Links:** https://arxiv.org/abs/2604.21139 · https://arxiv.org/pdf/2604.21139 · HTML: https://arxiv.org/html/2604.21139v1
- **Date checked:** 2026-10-23.

### 1.2 Code and data
- **No code, data, prompts, description pool or probe weights are linked**, either in the paper (searched the full text) or on the arXiv abstract page **[author result]**.
- The 15 traits of §2 are listed (p.3). The pools of 20 one-token names and 20 one-token traits (§3–4), the 40-trait list with opposites (§3.2) and the 100 two-subject-one-object variations (§5) are not listed **[unresolved]**.

### 1.3 Coverage checklist
Every item below was read in `paper.txt` and checked against the rendered PDF page.

| Item | Pages | Read | Figure/table checked visually | Notes |
|---|---|---|---|---|
| Title, abstract, Fig 1 (schematic) | 1 | ✔ | ✔ | Fig 1 draws QK/OV head mechanisms that are never directly analysed |
| §1 Introduction | 2–3 | ✔ | — | Intro names GPT-4o, DeepSeek-V3.2 and Claude Sonnet-3.5 as failing the dual-binding task; none appear in any figure |
| §2.1.1 Prompts | 3–4 | ✔ | — | |
| §2.1.2 Multi-slot probe, equations, Fig 2 | 4–5 | ✔ | ✔ (equations re-read from PDF) | |
| §2.1.3 Training procedure, Eq 1 | 5–6 | ✔ | ✔ | |
| §2.2.1–2.2.2 Results, Fig 3 | 6–7 | ✔ | ✔ (cells estimated, §1.4) | |
| §2.2.3 User/assistant turns, Fig 4 | 7–8 | ✔ | ✔ | |
| §3.1 Sequence retrieval, Fig 5 | 8–10 | ✔ | ✔ (bars measured) | |
| §3.2 Conflict detection, Eq 2–4, footnote 1, Fig 6 | 10–12 | ✔ | ✔ | Text says "after LayerNorm"; Fig 6 caption says "before the LayerNorm" |
| §4.1 Trait presence, Fig 7 | 13–14 | ✔ | ✔ | |
| §4.2 Name-trait binding, Fig 8 | 14–15 | ✔ | ✔ | Text and figure disagree on which entity is queried (§7.6) |
| §5 Dual binding on one token, Fig 9, §5.3 | 16–18 | ✔ | ✔ (bars measured) | |
| §6 Discussion, footnote 2 | 18–19 | ✔ | — | Footnote 2 reports an experiment whose data are not shown |
| Acknowledgements, references [1]–[18] | 19–20 | ✔ | — | |
| App A: independent probes, Fig A1 | 21 | ✔ | ✔ (cells estimated) | |
| App B: Table A1 (slots × models) | 22 | ✔ | ✔ (text extraction scrambled the table; values re-read from PDF) | |
| App C: conversations, C.1–C.3, Figs A2, A3 | 22–26 | ✔ | ✔ | C.2.2 heading mentions "system prompts"; no system-prompt result is given |
| App D: conflict steering ±, Fig A4 | 26 | ✔ | ✔ | Confirms the model as "qwen/qwen3-32b" |
| App E: per-question results, Fig A5 | 27 | ✔ | ✔ (bars measured) | |

**Coverage is complete.** No separately hosted supplement exists; the only material we lack is the unreleased code and data (§1.2).

### 1.4 How figure values were read (our measurement)
The paper reports no numbers for the heatmap cells or bar heights, so we read them from 300-dpi renders of the PDF.
- **Bar heights:** measured in pixels against the axis gridlines. Precision is about ±0.3 logits for Figs 5/7/8, ±0.005 for Figs 6/A4, ±1 point for Fig 9 and ±2 points for Fig A5.
- **Heatmap cells:** each cell's median colour was matched to the nearest colourbar colour, assuming the colourbar runs linearly from 7% to 100%.
- **Validation:** the mean of our Fig 3 cell estimates is 56.7%, against the paper's 56.3% (Table A1, Qwen3-32B, 4 slots). Fig A1 gives 49.1% against 50.3%. Fig 4 gives 54.0% against 56.8%; its diagonal cells carry text labels, so it is rougher.
- **Reliability:** treat single cells as ±3–5 points and pattern-level summaries as reliable.

---

## 2. Question & contribution

**Problem.** Can a single token's residual stream carry information about more than one entity at once? If it can, what does the model use that extra information for (pp.2–3)? The authors characterize known binding mechanisms as encoding one entity per token. These include binding-ID vectors [6] (Feng & Steinhardt, ICLR 2024), positional "first entity" codes [4, 7] and entity tracking [12]. Their question is whether models also *multiplex* several entities on one token (p.2) **[author interpretation]**.

**Claims, as the authors list them (pp.2–3)** **[author interpretation]**:
1. The current entity and the previous entity are the most reliably represented on a token. Others may be represented to some extent. The authors call these representations "slots" (§2.1).
2. The current-entity and prior-entity slots are "largely orthogonal" (§2.2).
3. Prior-entity representations support relational inferences: sequence order and conflict detection (§3).
4. Prior-entity representations are not used for explicit recall or binding retrieval, although they contain the needed information (§4).
5. "Perhaps as a result", non-frontier models fail a task that the authors expect requires two bindings on one token (§5). Frontier models succeed, which "suggests" more sophisticated binding (p.3).
6. Available information is not the same as used information (p.3, p.18). Slot structure may underlie sycophancy, theory of mind or deception (pp.3, 18).

**Strongest supported claim (our judgement)** **[our inference]**:
- **In Qwen3-32B at layer 45, on period tokens of templated eight-character descriptions, a held-out linear readout recovers the immediately preceding character's trait from the current character's tokens.** This readout is shared across entity positions and is not the readout that recovers the current character's trait (Fig 3, Fig A1).
- **On six-item lists, information at the next entity's token positions measurably contributes to answering "who came after X".** It contributes nothing measurable to "is anyone X?" or "who is X?" (Figs 5, 7, 8).
- **Everything beyond these two points is interpretation.** That includes "orthogonal slots" as model-internal objects, MLPs computing conflicts, frontier models multiplexing bindings, and relevance to sycophancy.

**The comparison that establishes the advance.**
- **The probe side** compares a 1-slot probe with a multi-slot probe (Table A1: 29.7% → 47.0% → 56.3% for 1/2/4 slots). It also compares per-position independent probes (Fig A1) and current-slot weights with prior-slot weights (r = .11).
- **The use side** compares patches at the entity's own positions ("current") with patches at the next entity's positions ("prior") across three query types (Figs 5, 7, 8). The decisive contrast is the prior-entity bar: about 4.6 logits for sequence retrieval against about 0 for presence and binding retrieval.

---

## 3. Operational definitions (as used in this paper)

| Term | Meaning in this paper | Location |
|---|---|---|
| **Entity** | A named character described in the prompt. §2: one of 8 four-sentence descriptions headed "Name:". §3–4: one "Name is trait." sentence in a 6-item list. App C: also a "Me:" self-description in a user or assistant turn. | pp.3–4, 9, 23 |
| **Trait** | One label per entity. §2: one of 15 "semantically distinct" traits implied, not stated, by the description. §3.1/§4: one of 20 one-token traits stated explicitly. §3.2: 40 traits (the 20 plus their opposites). | pp.3, 9, 11 |
| **Binding** | The association between an entity and its attribute, or a subject-verb-object relation (§5). | pp.1–2, 16 |
| **Slot** | A distinct representational scheme for the same information, operationalized as one of the K linear classifiers in the multi-slot probe. A slot's identity is defined by which relative entity position the router assigns to it. "Slot" is a property of the probe fit; the paper never isolates a slot subspace inside the model and intervenes on it. | pp.2, 4, 6 |
| **Current-entity slot** | The classifier the routers select to predict entity e on entity e's own tokens (S0 in Fig 3). | p.6 |
| **Prior-entity slot** | The classifier selected to predict entity e on entity e+1's tokens (S1 in Fig 3). | p.6 |
| **"Current-entity representation" / "prior-entity representation" in §3–4** | Not the probe slots. These are *all activations at the four tokens of entity #1* (current) or *of entity #2* (prior), patched at every layer. | pp.9, 13, 15 |
| **Prior-entity direction (steering)** | v^prior(x) = mean residual activation at a trait token, conditioned on the *preceding* entity having trait x (Eq 2). It is computed on list prompts and is unrelated to the probe weights. | p.11 |
| **Used / available** | "Available" means linearly decodable by a probe. "Used" means a position-level patch or steer changes next-token logits for the task. | pp.3, 13, 18 |
| **Conflict** | Adjacent entities with "opposite" traits, using the authors' 20 opposite pairs; the user prompt gives four example pairs. | pp.10–11 |
| **Local scope** | The authors' term (§2.2.3 title) for slots operating relative to the current position or speaker, not tied to a fixed speaker. | p.7 |
| **Persona** | Not used. The nearest notions are the user and assistant *roles* and the user/assistant *self-descriptions* of App C. | — |
| **Alignment** | Used only as "alignment-relevant model behaviors like sycophancy [14], deception [11], and persuasion [5]" (p.18); not studied. | p.18 |
| **Transfer** | Not used; no training is done. | — |
| **Knowledge** | Implicit in "information available in activations" versus "information the model actually uses" (abstract, p.3). | pp.1, 3 |
| **Similarity** | Correlation between slot weight matrices (r = .11) and representational similarity analysis (RSA): the second-order correlation of trait-by-trait similarity matrices between slots (r = .34). | p.6 |
| **Faithfulness** | Not used. The nearest is the proposal to detect "when a model's internal representations diverge from what it communicates" (p.18). | p.18 |
| **Accuracy (§5)** | The share of valid trials in which the next generated token is the correct object. Trials whose next token is neither object are discarded. | p.16 |

---

## 4. Experimental reconstruction

### 4.1 Models
| Model | As named in paper | Used for | Notes |
|---|---|---|---|
| Qwen3-32B | "Qwen3-32B … 64 layers" (p.4) | All probing (§2, App C); sequence/presence/binding patching (default model, p.3); conflict steering (Fig A4 title "qwen/qwen3-32b"); one of the §5 API models | The paper states only the layer count; architecture type (dense vs mixture-of-experts) is not stated **[unresolved]**. No checkpoint revision or precision is given **[unresolved]**. The paper never says base or post-trained. The name (no "-Base"), the User/Assistant turns and the `<think>` prefill indicate the post-trained chat model **[our inference]**. In §5 it is served by an API provider, so it may not be the same weights/precision as in §2–4 **[unresolved]**. |
| Qwen3-0.6B | p.5, Table A1 | Multi-slot probe accuracy only | Layer not stated; no routing figure **[unresolved]** |
| Llama-3.3-70B-Instruct | p.5, Table A1; App C.2.2 | Probe accuracy; self-description test (results "not reported"); §5 behavior | Layer not stated. The conversational slot organization "differs" from Qwen, but data are not shown (p.22) |
| Qwen3-235B-A22B-Instruct | p.2; App C.2.2; Fig 9 | §5 behavior; self-description test (not reported) | The paper does not describe the architecture. The "A22B" suffix suggests about 22B active parameters, i.e. mixture-of-experts **[our inference]** |
| Claude Sonnet-4.5 | p.3 | Wrote the §2 descriptions; §5 behavior | |
| Claude Opus-4.5, Gemini-2.5-Flash, Gemini-3-Pro, DeepSeek-R1, GLM-4.7 | Fig 9 | §5 behavior only | Text also mentions Gemini-2.5-Pro, DeepSeek-V3.2, GPT-4o and Claude Sonnet-3.5 with no figure data (§7.6) |
| Llama-3.1-8B, Minimax M2 | p.16 | Attempted for §5, excluded | 8B gave invalid tokens on most trials; no M2 provider supported prefill |

No model is fine-tuned anywhere in the paper. The template fields for corpus/tracer assignment, loss mask, optimizer for the subject model, adapter, schedule, update budget and checkpoints are therefore **not applicable**.

### 4.2 Experiments

**E1. Multi-slot probe on character lists** (§2.1–2.2, Figs 2–3, Table A1)
- **Prompt** (p.4): User: "I'm writing a story. What do you think about this list of potential characters:", then 8 entities. Each is "Name: …" with exactly four description sentences and the closing sentence "That's the full description of this character." All entities appear in one user turn.
- **Descriptions:** written by Claude Sonnet-4.5 to imply one of 15 traits: athletic, analytical, creative, organized, social, patient, brave, honest, curious, nurturing, practical, ambitious, independent, articulate, calm (p.3). The descriptions refer to the entity as "They".
- **Data size:** 10,000 prompts.
- **Not reported:** the size of the description pool, how traits are assigned to entities (with or without replacement) and the generation prompt **[unresolved]**.
- **Activations:** residual stream at layer 45 of 64. The hook point (block input vs output) is not stated **[unresolved]**.
- **Token positions:** "the periods of the four sentences", i.e. 32 per prompt (pp.4–5). Whether the period of the boilerplate fifth sentence is excluded is not stated explicitly **[unresolved]**.
- **Why periods:** periods were chosen because "preliminary analyses suggested that periods encoded current and past trait information more robustly than random tokens" (p.4). Those analyses are not shown.
- **Labels:** each activation is duplicated once per entity introduced so far, giving 4·Σ_{e=1..8} e = 144 labelled examples per prompt (p.6).
- **Split:** 80/20 by prompt, so all positions of a prompt fall in the same split (p.6).
- **Probe:** K = 4 slots (main), E = 8 routers, Adam, summed cross-entropy (Eq 1). Learning rate, epochs, batch size, initialization, regularization, activation normalization and number of fits/seeds are absent **[unresolved]**.
- **Choice of K:** K = 4 was chosen "as accuracy gains plateau beyond this point and the resulting slots are the most clearly interpretable" (p.5). Yet 5 slots score 57.9% and 7 slots 58.2%, against 56.3% for 4 (Table A1). The choice is partly made for interpretability, which is a researcher degree of freedom **[our inference]**.

**E2. Independent per-position probes** (App A, Fig A1)
- One linear classifier per (token t ∈ 0..31, entity e ≤ current), trained only on that cell's data. Same data and split; overall accuracy 50.3% (p.21).

**E3. Conversation probes** (§2.2.3; App C.1.1; Fig 4/A2; Table A1 row 4)
- **Setup:** user and assistant alternate turns; each turn describes one third-party entity, using the same descriptions as E1. The first user turn starts "Let's play a game! Let's each describe a hypothetical third party character or ourselves. I'll start." (p.23).
- **Assistant turns:** inserted text, not model generations **[our inference from "using the same descriptions", p.23]**.
- **Probe:** 8 entities, K = 5; overall 56.8% (Table A1).

**E4. Self-descriptions** (App C.1.2, C.2.2; Fig A3)
- **Setup:** as E3, but Entity #1 becomes an assistant "Me: I wake at dawn…" and Entity #2 a user "Me: I find myself…". These are the same descriptions converted to first person. K = 5.
- **Other models:** Llama-3.3-70B-Instruct and Qwen3-235B-A22B-Instruct were "also tested", with results not reported (p.25).

**E5. Sequence-retrieval patching** (§3.1, Fig 5)
- **Trials and lists:** 200 trials of 6-item lists "Name is trait.", drawn from 20 one-token names and 20 one-token traits.
- **Prompt, verbatim** (p.9): `User: Look over this list of characters. Zed is strong. Alice is tall. Bob is cool. Carol is funny. David is brave. Elaine is organized. Who came after Alice?` / `Assistant: <think> The character that comes after Alice is`
- **Fixed query:** always asks about Entity #1 (0-indexed); the correct answer is Entity #2.
- **Source prompt:** swaps Entities #1 and #3, so the correct source answer is Entity #4.
- **Patch:** source → target at *every layer* for all four tokens of an entity's sentence; keys only, values only, or both. "Current" patches Entities #1 and #3; "prior" patches Entities #2 and #4 (Fig 5).
- **Metric:** Δ logit of the source answer − Δ logit of the target answer, in raw logits.

**E6. Conflict-detection steering** (§3.2, Eqs 2–4, Fig 6, Fig A4)
- **Trials:** 200, each a target prompt with no adjacent conflict. Trait pool expanded to 40 (each of the 20 plus an opposite, e.g. brave → timid).
- **Prompt, verbatim** (p.10): `User: Do any adjacent characters in this list have opposite traits? Examples of possible opposites (not exhaustive): optimistic ↔ pessimistic, confident ↔ insecure, stoic ↔ dramatic, cheerful ↔ gloomy. There are many other possible examples of opposite traits. Don't expect exact opposites, just rough ones. Just come up with ones where you believe the two entities would conflict. List: Zed is strong. … Do any traits conflict? Yes or no?` / `Assistant: <think> The answer is`
- **Steering vectors:** built from 1,000 list prompts with random traits (Eqs 2–3).
- **Prior condition:** add λ(v^prior(x̄₂) − v^prior(x₁)) at Entity #2's trait token, where x̄₂ is the opposite of Entity #2's trait.
- **Current condition:** add λ(v^curr(x̄₂) − v^curr(x₁)) at Entity #1's trait token.
- **Scale:** λ = 0.1, a single value, chosen from qualitative runs in which stronger steering "caused model confusion and capabilities deterioration" (p.11 and footnote 1).
- **Layers:** steering is applied "on all layers" (footnote 1).
- **Sites:** the MLP input of the trait token, or that token's K and V. For KV, steering is applied "after activations had already been computed for future entities", so only the final answer position reads the steered K/V (p.11).
- **Direction and metric:** both +Δ and −Δ are applied. The reported metric is (Δyes − Δno under +) − (Δyes − Δno under −) (Fig 6), with the separate directions in Fig A4.

**E7. Trait-presence patching** (§4.1, Fig 7)
- **Trials:** 200.
- **Prompt, verbatim** (p.13): `User: I am writing a short story. What do you think about this list of characters: Zed is strong. Alice is {tall/funny}. Bob is cool. Carol is fit. David is brave. Elaine is organized. What do you think? Can you suggest a possible plot involving these characters?` / `Assistant: <think> The user is asking me to review their list of potential story characters and to suggest a possible plot. Hmm, I should think. Does the list contain any character that is careless? Yes. Does the list contain any character that is brave? Yes. Does their list include any character who is tall?`
- **Prefill quirk:** the text example's prefill asserts "careless? Yes" although no character is careless. The Fig 7 version uses "strong? Yes … brave? Yes", which are both true (§7.6).
- **Source vs target:** the source gives Entity #1 the queried trait (expected "yes"); the target gives Entity #1 another trait (expected "no").
- **Patch:** all four tokens of Entity #1 (current) or of Entity #2 (prior), at every layer, as K, V or K&V.
- **Metric:** Δyes − Δno logit; the Fig 7 axis is labelled "Steering Effect" although this is patching.

**E8. Name-trait binding patching** (§4.2, Fig 8)
- **Trials:** 200.
- **Prompt:** the same user prompt as E7, with prefill `<think> The user is asking me to review their list of potential story characters. I should think about the tall character. The tall character is named` (p.14).
- **Source vs target:** the text says traits of Entities #1 and #3 are swapped with names fixed. The Fig 8 caption says *names* of #1 and #3 are swapped, and its example queries the trait of #3, not #1 (§7.6).
- **Patch:** Entities #1 and #3 (current) or #2 and #4 (prior), at every layer, as K, V or K&V.
- **Metric:** Δsource − Δtarget logits.

**E9. Two-subject-one-object behavior** (§5, Figs 9, A5)
- **Prompt, verbatim** (p.16): `User: Alice prepares and Bob consumes food. Bob prepares and Alice consumes drinks.` / `Assistant: {Alice/Bob} is the one who {prepares/consumes}`
- **Size:** 100 variations × 4 prefills = 400 prompts. How the variations differ (names, verbs, objects, object order) is not stated **[unresolved]**.
- **Controls:** "separated" ("Alice prepares food. Bob consumes food…") and "flipped" ("Food is prepared by Alice and consumed by Bob").
- **Sampling:** via OpenRouter at temperature 0, one sample per prompt; DeepInfra serves the open models because it "consistently handled assistant prefills properly".
- **Exclusions:** trials whose next token is not one of the two objects are discarded; every reported model is valid on at least 79% of prompts (p.16).
- **Not stated:** whether reasoning/thinking was enabled or suppressed for any model (Gemini-3-Pro, DeepSeek-R1, the Qwen3 models) **[unresolved]**.

### 4.3 Scale of each setting (relevant to stories)
| Setting | Entities | Approximate text length | Positions read or intervened on | Layers |
|---|---|---|---|---|
| E1–E4 probes | 8 | Not reported. By our count of the p.4 example, each description is about 75 words, so a prompt is about 600 words plus instructions **[our inference]** | 4 period tokens per entity | 45 only (Qwen3-32B); unstated for the others |
| E5, E7, E8 patching | 6 | 24 list tokens plus a short instruction and prefill | All 4 tokens of entities #1–#4; readout at the final prefill token | All layers patched |
| E6 steering | 6 | Same, plus a longer instruction | The trait token of entity #1 or #2; readout at the final token | All layers steered |
| E9 behavior | 2 subjects, 2 objects | Two sentences | Next generated token | — |

---

## 5. Method mechanics

### 5.1 Multi-slot probe (pp.4–6)
- **Notation:** h_t ∈ ℝ^d is the layer-45 residual vector at period token t. W_k ∈ ℝ^{d×c} (k = 1..K) are the slot classifiers, with c = 15 classes. R_e ∈ ℝ^{d×K} (e = 1..E = 8) are the per-entity routers.
- **Routing:** α_{e,t} = softmax(R_eᵀ h_t) ∈ ℝ^K.
- **Slot logits:** z_{k,t} = W_kᵀ h_t ∈ ℝ^c.
- **Prediction:** p_{e,t} = softmax(Σ_k α_{e,t,k} z_{k,t}).
- **Loss:** L = Σ_e Σ_{t ≥ t_e} CE(p_{e,t}, y_e), with t_e = 4e (0-indexed). Positions before an entity is introduced are excluded. All W_k and R_e are trained jointly with Adam (Eq 1).
- **Router input:** routers see the same h_t, so routing can depend on any position or context information in h_t.
- **Readout of results:** the routing maps (Fig 3 right) average α_{e,t} over prompts. Slots are renumbered post hoc so that S0 is current and S1 is prior (Fig 3 caption).
- **Linearity:** the probe is a *gated mixture* of linear classifiers. Because α depends on h_t, it is not linear in h_t **[our inference]**. Fig A1's plain linear per-position probes reproduce the qualitative accuracy pattern, so decodability does not depend on the gating **[author result + our inference]**.

### 5.2 What a K-slot probe can show **[our inference]**
- **The 1-slot probe outputs one distribution per token for every entity.** With K = 1, p_{e,t} = softmax(z_{1,t}) is identical for all e at token t. Each token has exactly one current entity (32 of the 144 pairs per prompt). So a 1-slot probe that is perfect on the current entity and at chance (1/15) elsewhere scores 32/144 + (112/144)/15 ≈ 27.4%. Table A1 reports 29.7%.
- **The 2-slot ceiling is similar.** A 2-slot probe that is perfect on current and prior entities (32 + 28 pairs) and at chance elsewhere scores ≈ 45.6%. Table A1 reports 47.0%.
- **The jump from 1 to 2 slots is close to forced.** A K-slot probe can emit at most about K distinct predictions per token. The big 1→2 gain (Table A1, p.22: "a 2nd slot yields a large accuracy gain by distinguishing current-entity and prior-entity representations") shows that a *second entity is decodable* on each token. Any geometry would produce it, including one in which the prior trait lies along the same direction as the current trait but at a distinguishable strength.
- **The gain is not, by itself, evidence for "distinct representational schemes".** The evidence for distinctness lies elsewhere:
  - the low weight correlation between S0 and S1 (r = .11);
  - the RSA second-order correlation (r = .34);
  - the fact that one shared S1 serves every adjacent pair (e, e+1) (Fig 3 right). This is the informative structural finding: the "previous entity" code is relative to position, not absolute.
- **Sharing is partly enforced by the architecture.** K = 4 < 8 entities, so some slots must be shared.

### 5.3 Weight correlation and RSA (p.6)
- **Weight correlation:** "Their weights are uncorrelated (r = .11)". How the correlation is computed (flattened d×c matrices? per class?) is not stated **[unresolved]**.
- **RSA:** for each slot, pairwise similarities among its 15 trait weight vectors are taken (lower triangle), then these are correlated between slots: r = .34. The authors conclude prior-slot probes "cannot be uniformly described as rotations of the current-entity slot probes" **[author interpretation]**.
- **Caveat 1:** probe weights are not representation directions. Weights also cancel correlated nuisance directions. Mean-difference directions (as in Eqs 2–3) would test geometry more directly; their cosine is not reported **[our inference]**.
- **Caveat 2:** the prior slot is fit to noisier targets (≈54–90% accuracy against ≈91–99% for current). Lower signal-to-noise alone lowers a second-order correlation, and no noise ceiling (split-half reliability) is reported **[our inference]**.

### 5.4 Patching semantics (§3.1, §4)
- **What is transferred:** for the chosen entity sentences, source activations replace target activations at every layer, as keys only, values only, or both (p.9).
- **"K&V patching is equivalent to patching the residual stream" (p.9)** **[author result]**. This holds for the effect on *other* positions when all layers are patched, because other positions read a position only through its K and V **[our inference]**.
- **Unresolved:** whether later positions are recomputed in the target forward pass, or frozen as in the E6 KV condition.
- **If later positions are recomputed, the current-entity condition reproduces the source prompt.** Patching #1 and #3 at every layer then also rewrites what #2 and #4 read. The large current-entity bars (≈9–14 logits) are then a positive control for the patching pipeline, not evidence about a "current-entity slot". The authors call these effects "predictable" (p.9) **[our inference]**.
- **The prior-entity patch is position-level, not slot-level.** It transfers *everything* at the next entity's positions that differs between source and target contexts. That includes the probe's S1 content, previous-token and previous-sentence features, and any longer-range information (for entity #4, entity #1 lies three back). No intervention projects onto, ablates or patches the probe-identified S1 subspace **[our inference]**.

### 5.5 Steering semantics (§3.2)
- **Conditional means:** v^prior(x) = E_{p,i}[h_{p,i} | x_{p,i−1} = x] and v^curr(x) = E_{p,i}[h_{p,i} | x_{p,i} = x], where h_{p,i} is "the residual stream activation at entity i's trait token" (Eqs 2–3).
- **Contrast vectors:** Δ^prior = λ(v^prior(x̄₂) − v^prior(x₁)) (Eq 4). The shared mean cancels in the difference.
- **Unresolved:** whether separate means are computed per layer and per site (residual, MLP input, K, V), and how a residual-space vector is applied to K and V for grouped-query attention.
- **The two sites are not matched in scale.** The vectors are defined in residual space but added to the post-LayerNorm (or pre-LayerNorm; §7.6) MLP input or to K/V. No norm matching or dose sweep links them **[our inference]**.
- **The two sites also differ in reach.** MLP-input steering changes the residual stream at the trait token, which affects every later position (later entities, question, answer). KV steering is applied after later entities are computed, so only the answer token's reads change. "MLP works, KV does not" is therefore confounded with "propagates to later positions vs does not". It does not localize conflict computation to MLPs **[our inference]**.

### 5.6 Behavioral evaluation (§5)
- **Scoring:** exact match of the next token against the two objects, with invalid tokens excluded.
- **Reference lines:** chance is 50%. The 75% "guess-half" line assumes a model encodes one binding per object token correctly and guesses randomly on the other (p.17).

### 5.7 What predictors see; interventions at evaluation
- **The probe is told which entity to decode.** It sees one h_t at a time, and the entity index chooses the router. The model would have to address entities by content **[our inference]**.
- **Interventions are active only during the single forward pass that produces the next-token logits.** The exception is footnote 1's qualitative free-reasoning runs. Nothing is evaluated over a generated continuation, and no intervention persists across turns.

---

## 6. Evidence table

| # | Claim | Decisive comparison | Result | Unit of replication | Denominator | Uncertainty | Source | Remaining alternative |
|---|---|---|---|---|---|---|---|---|
| 1 | Prior entity's trait is decodable on the next entity's tokens **[author result]** | Held-out probe accuracy vs chance (7%), per cell | ≈ next-entity row means 90, 85, 76, 69, 62, 56, 54% for entities 1→7. Diagonal ≈91–99%. Two back ≈46→27% (excluding entity #0). Entity #0 column ≈98→42%. Overall 56.3% | One probe fit; 2,000 test prompts; one model, one layer | Test (entity, position) pairs, 144 per prompt | None reported (no seeds, no CIs) | Fig 3; Table A1; pp.6–7 | Lexical leakage if descriptions recur across splits (pool size unknown); recency residue of the preceding text rather than an entity-structured code (§8) |
| 2 | Same decodability without weight sharing **[author result]** | Independent per-cell linear probes | Same qualitative pattern. Next-entity row means ≈89→44%; overall 50.3% (≈49.1% by our pixel estimate) | One fit per cell | As above | None | Fig A1; p.21 | Same as #1. Per-cell probes have fewer data per weight; regularization is not stated |
| 3 | Current and prior slots are distinct and "largely orthogonal" **[author interpretation]** | Weight correlation; RSA; slot-count accuracy | r = .11; RSA r = .34; 1/2/3/4 slots = 29.7/47.0/54.2/56.3% | One fit | — | None | p.6; Table A1 | The 1→2 gain is near-forced by construction (§5.2). Weight ≠ representation geometry. RSA is attenuated by noise |
| 4 | Multiple slots exist in other models **[author interpretation]** | Table A1 rows | Qwen3-0.6B 28.7/44.1/49.7/50.3%; Llama-3.3-70B-Instruct 29.7/46.6/51.0/51.0% (1–4 slots) | One fit each; layer unstated | — | None. Non-monotone sequences (Llama: 53.8% at 6 slots, 51.3% at 7) suggest a few points of fit noise | Table A1; p.22 | Shows only that a second entity is decodable. No routing maps for these models |
| 5 | In conversations, slots are relative, not tied to a speaker; one slot (S3) holds same-role past entities **[author interpretation]** | Routing maps, K = 5 | Current and prior slots reappear; S3 is described as holding same-role historic entities | One fit | — | None | Fig 4/A2; pp.7, 24–25 | Visual reading of one probe fit. S3 vs S2/S4 roles may depend on K and on the fit |
| 6 | User-described entities persist more strongly **[author result; "modest"]** | Visual comparison of heatmap cells | Our estimate of next-entity cells: user entity → assistant turn ≈88, 84, 71, 70%; assistant entity → user turn ≈71, 56, 44% | One fit | — | None; no test | Fig A2; pp.7, 24 | Turn-template tokens and position-in-turn differ between roles; the first user turn holds the game instruction |
| 7 | Self-descriptions are not privileged **[author interpretation]** | Fig A3 vs Fig A2, by eye | "Mostly identical" accuracy and routing. Llama-3.3-70B and Qwen3-235B tested, not shown | One fit | — | None | Fig A3; p.25 | A null from an instrument (a trait probe) that could not detect a separate self-code. No positive control |
| 8 | Information at the next entity's positions is used for "who came after X" **[author result]**; via "entity-level induction heads" **[author interpretation]** | Prior-entity patch (#2, #4) vs zero | Prior: K ≈4.6, V ≈2.0, K&V ≈4.4 logits. Current: K ≈9.2, V ≈13.5, K&V ≈13.5 | 200 trials; one model | Δsource − Δtarget in raw logits | Error bars of unspecified type (≈±0.7 for prior) | Fig 5; pp.9–10 | Position-level patch, not the S1 subspace. Ordinary previous-token/previous-sentence features at the next name would give the same result. No random-position control. No head-level analysis, although the section title names heads |
| 9 | MLPs integrate prior-entity directions with the current trait to detect conflicts **[author interpretation]** | +Δ vs −Δ steering at MLP input vs KV | Prior MLP: +0.031 / −0.030 → difference ≈0.06 logits. Prior KV ≈ −0.005. Current MLP: +0.083 / +0.081 (both directions push "yes") → difference ≈0.002 | 200 trials; one λ | Δyes − Δno logits | Error bars of unspecified type (≈±0.008 prior MLP) | Figs 6, A4; pp.11–12, 26 | Effect is tiny (a few hundredths of a logit). The ± design removes symmetric degradation but not a linear nonspecific effect. No non-conflicting contrast-vector control. MLP vs KV is confounded with reach and scale (§5.5). The predicted current-entity effect failed |
| 10 | Prior-entity information is not used to report trait presence **[author result]** | Prior patch (#2) vs current patch (#1) | Current: K ≈9.2, V ≈9.5, K&V ≈9.5. Prior: ≈0 for all three (absolute effect < 0.1) | 200 trials | Δyes − Δno | Small bars | Fig 7; pp.13–14 | Prior-trait decodability in this list format was never measured (the probes used long descriptions). Fig 5 shows the same kind of patch can matter, which is a cross-task positive control |
| 11 | Prior-entity information is not used for name-by-trait retrieval **[author result]** | Prior patch (#2, #4) vs current (#1, #3) | Current: K ≈6.2, V ≈14.4, K&V ≈14.2. Prior: K ≈ −0.2, V ≈ +0.25, K&V ≈ +0.15 | 200 trials | Δsource − Δtarget | Small bars | Fig 8; p.15 | Intact, conflicting current-entity information may dominate: a competition test, not a test of whether prior information is *usable*. Names were never probed in the prior slot, so "decodable from the prior slot" (abstract) is not shown for names |
| 12 | Open models fail dual binding on one token; frontier models succeed **[author result]**; failure is caused by the one-token constraint **[author interpretation]** | Main vs separated vs flipped | Main / separated / flipped (%), ≈: Sonnet-4.5 83/99/93; Opus-4.5 91/100/94; Gemini-2.5-Flash 62/93/78; Gemini-3-Pro 95/100/100; Qwen3-32B 58/91/69; Qwen3-235B-Instruct 67/94/85; DeepSeek-R1 78/98/89; GLM-4.7 78/100/89; Llama-3.3-70B 73/99/78 | 400 prompts per condition; one temperature-0 sample each | Valid trials only (≥79% valid) | Error bars of unspecified type | Fig 9; pp.16–17 | First-object default (#13). Right-node-raising parse difficulty versus single-token storage. Hidden reasoning settings unknown. No mechanistic link to slots |
| 13 | Errors concentrate on the "drinks" questions **[author result: "Q3 accuracy being consistently lower"]** | Per-question accuracy, main condition | Q1 (Alice prepare → food) / Q2 (Alice consume → drinks) / Q3 (Bob prepare → drinks) / Q4 (Bob consume → food), ≈%: Qwen3-32B 95/24/14/98; Gemini-2.5-Flash 97/10/47/92; Llama-3.3-70B 100/60/36/93; GLM-4.7 100/76/39/97; DeepSeek-R1 96/73/53/90; Qwen3-235B 94/84/34/57; Sonnet-4.5 100/75/61/96; Opus-4.5 97/99/80/85; Gemini-3-Pro 100/96/86/100 | As #12 | As #12 | Unspecified | Fig A5; p.27 | See §7.2: weak models mostly answer the first object, which the "one binding per token" account does not predict **[our inference]** |
| 14 | Prior-entity steering does not affect reciting the list **[author result, data not shown]** | — | "Models recite the original list as though nothing is different" | Unknown | Unknown | Unknown | Footnote 2, p.18 | Unverifiable |

---

## 7. Controls & failures

### 7.1 Controls that were run
- **Prompt-level 80/20 split,** to avoid within-prompt leakage (p.6) **[author result]**.
- **Independent per-cell linear probes,** checking that the heatmap is not a weight-sharing or routing artefact (App A) **[author result]**.
- **Slot-count sweep (1–7) and other models** (Table A1) **[author result]**.
- **Swap design** in E5 and E8: the swapped trait or name stays present somewhere in the prompt, so only the binding changes (pp.9, 15) **[author result]**.
- **Bidirectional steering:** report + minus − to cancel "indiscriminate noise" from degradation (pp.11, 26) **[author result]**.
- **Behavioral controls** in E9: separated and flipped sentence forms (p.16) **[author result]**.

### 7.2 Failures and negative results (preserved)
- **Current-entity conflict steering failed.** Both directions *raise* "yes" by ≈0.08 logits (Fig A4). The authors read this as degradation (Fig A4 caption) **[author interpretation]**.
  - Under the authors' own Fig 1 story, the conflict computation reads entity #1's trait as copied into the prior slot. Steering #1's current trait to the opposite of #2's should then create a conflict. It did not, and the paper does not discuss this as a failed prediction **[our inference]**.
- **KV steering had no effect** in either condition (Fig 6, A4) **[author result]**.
- **Prior-entity patching had no effect on trait presence or name retrieval** (Figs 7, 8) **[author result]**.
- **Llama-3.1-8B was excluded** for producing invalid tokens on most trials; **Minimax M2** was excluded because no provider supported prefill (p.16) **[author result]**.
- **Qwen3-0.6B shows only the current and prior slots**, "with no additional structure" (p.22; no figure) **[author result]**.
- **Conversational slot organization differs between Qwen and Llama**, and "elaborating … is beyond the scope" (p.22) **[author result, data not shown]**.
- **"The breakdown of clean slot structure when multiple entities are described per turn"** (C.3, p.25) refers to a result not shown anywhere. In E1, all eight entities sit in one user turn and the structure is clean, so what "per turn" refers to is unclear **[unresolved]**. This is the most story-relevant negative result in the paper, and it has no data.
- **Per-question pattern in E9 (Fig A5).** In the main condition, Qwen3-32B is near-perfect on both "food" questions (Q1 ≈95%, Q4 ≈98%) and fails both "drinks" questions (Q2 ≈24%, Q3 ≈14%); Gemini-2.5-Flash looks similar.
  - If the model could store only one binding per object token, it should get about one of each pair right, giving roughly 75%. It does not: it mostly answers the first-mentioned object.
  - This looks like a default to the first object when the two sentences are indistinguishable as bags of words (each contains Alice, Bob, prepares, consumes). Getting zero bindings right plus a primacy default yields about 50%, which matches Qwen3-32B's ≈58% **[our inference]**.
  - It is unknown whether object order was counterbalanced across the 100 variations. If it was not, question type and object position are confounded **[unresolved]**.

### 7.3 Prompt and sampler sensitivity, degradation, exclusions
- **Prompt and template sensitivity:** no paraphrase or template variation is reported for E5–E8. Each uses one fixed prompt frame, one queried position (entity #1), one list length (6) and one entity-sentence form. Whether the model's native chat template was applied is not stated **[unresolved]**.
- **Degradation:** λ = 0.1 was chosen qualitatively (footnote 1); stronger steering made the model report entity #2's trait as "unknown". There is no perplexity check or unrelated-task check **[author result]**.
- **Unpatched baselines are never reported.** Unpatched task accuracy or yes/no probabilities for E5–E8 are missing, and E6 has no real-conflict prompts showing how big a genuine "conflict detected" logit shift is. Without them, ≈0.06 logits cannot be put on a behavioral scale **[our inference]**.
- **Exclusions in E9:** invalid next tokens are discarded, with ≥79% valid per model. Per-model invalid rates are not given, and exclusion could correlate with difficulty **[unresolved]**.
- **Scoring:** exact token matching for E9 and logit differences elsewhere, so there is no judge to validate.

### 7.4 Leakage
- **Prompt-level split, but the description pool size is unknown.** If the same Claude-written descriptions recur across train and test prompts, a probe can map description-specific lexical content to a trait label. This would inflate both current and prior decoding, and the prior case in particular through "residue" of the preceding text **[unresolved; our inference]**.
- **No lexical baseline** (a text classifier from the description words to the trait) calibrates what "trait decodable" means **[our inference]**.

### 7.5 Controls not run
1. **Slot-subspace interventions:** patching, ablating or steering along the probe's S1 (or S0) weights, which would directly test whether the *slot* is used.
2. **Random-position patching** (e.g. entity #5's tokens, or filler tokens) as a specificity control for Fig 5.
3. **Necessity test:** ablating the prior information (e.g. mean-ablating S1 at #2/#4) and measuring the drop in "who came after".
4. **Steering controls:** matched-norm random vectors, non-conflicting contrast vectors (v^prior(y) − v^prior(x₁) with y not opposite to x₂), a λ dose sweep, norm matching across MLP and KV sites, and residual-stream steering.
5. **Intra-entity contradiction control:** adding "uncool" to Bob's own current trait, to separate *between-entity* conflict from a contradiction located at one token.
6. **Unpatched and positive baselines:** unpatched accuracy for E5–E8; real-conflict prompts for E6.
7. **Probe validation:** probing the list format of §3–4 (the bridge between the probe results and the interventions); a layer sweep (only layer 45 is reported); shuffled-label probes; seeds and variance; transfer of the current-slot classifier to prior positions; name/identity probes.
8. **Robustness of E5–E8:** querying entities other than #1; other list lengths; paraphrased instructions; a second model.
9. **Head-level analysis** for the claimed "entity-level induction heads".
10. **Entity-boundary vs recency control:** inserting non-entity filler between entities (§8).
11. **E9 design checks:** counterbalancing object order, reporting reasoning settings, reporting invalid rates per model.
12. **On-policy assistant text:** model-generated assistant turns for the conversation probes, instead of inserted text.

### 7.6 Internal inconsistencies and unreported results
- **LayerNorm side:** MLP steering is "after LayerNorm" in the text (p.11) but "before the LayerNorm" in the Fig 6 caption (p.12) **[unresolved]**.
- **Gemini model:** the text compares "Gemini-3-Pro > Gemini-2.5-Pro" (p.17), but Fig 9 plots Gemini-2.5-**Flash**.
- **Models without data:** the intro's failing models (DeepSeek-V3.2, GPT-4o, Claude Sonnet-3.5; p.2) have no reported data.
- **"Near chance" in the abstract:** it says open-weight models "perform near chance accuracy" on dual binding. Only Qwen3-32B (≈58%) is near the 50% chance level; the other open models score ≈67–78% (Fig 9).
- **E8 design:** the text says traits of #1/#3 are swapped with names fixed and the queried trait is entity #1's (pp.14–15). The Fig 8 caption swaps names and its example queries the "funny" character, i.e. entity #3's trait.
- **Prompt names:** E5's text names entity #4 "David" and #3 "Carol"; Fig 5 uses "Dani" and "Chuck". This is cosmetic.
- **E7 prefill:** the text example asserts "careless? Yes" for a trait no character has; the Fig 7 version uses correct answers.
- **Axis label:** Fig 7's axis says "Steering Effect" for a patching experiment.
- **C.2.2 heading:** it reads "Self-descriptions and system prompts", but no system-prompt experiment is described.
- **Unreported results:** footnote 2 (recitation), the Llama-3.3-70B and Qwen3-235B self-description tests, the Qwen-vs-Llama conversational differences, the C.3 "breakdown", and the "preliminary analyses" behind using periods.

---

## 8. Interpretation boundary

**Readability (decodability)** **[author result]**:
- *Established, under these conditions:* in Qwen3-32B at layer 45, on period tokens of eight-entity templated descriptions, a held-out probe reads the current entity's trait (≈91–99%), the previous entity's trait (≈54–90%, falling with depth) and the first entity's trait (≈42–98%). Middle entities two or more back sit near 20–30%, against 7% chance (Fig 3, our estimates).
- *Also established:* a shared relative-position readout (S1) serves all adjacent pairs.
- *Not established:* that the "slot" is a distinct internal object (as opposed to a probe construct), that it is orthogonal in the representation (as opposed to in the probe weights), or anything at other layers or other token types.

**Predictive information:** not studied. Nothing predicts behavior from slot readouts.

**Causal contribution** **[author result + our inference]**:
- *Established:* patching all layers at the next entity's four tokens contributes ≈4.6 logits to "who came after X". The same patch contributes ≈0 to trait presence and name-by-trait retrieval, on six-item lists, with queries about entity #1, in one model.
- *Established:* adding a prior-direction contrast at the trait token's MLP input changes the conflict yes−no gap by ≈0.06 logits in one direction and ≈ −0.06 in the other.
- *Not established:* that the probe's S1 subspace carries these effects; that MLPs compute conflicts; that attention heads perform entity-level induction; that the null for explicit retrieval holds when current-entity information is absent rather than conflicting; any result for other models.

**Training-time effects:** none. No fine-tuning, no gradients and no learning dynamics are studied.

**Deployment and monitoring:** none. The sycophancy, deception, persuasion and theory-of-mind links (pp.3, 18), the SAE mislabelling point (p.18) and the "blindsight" analogy (p.18) are all **[author interpretation]**, untested speculation.

**Alternatives not ruled out** **[our inference]**:
1. **Recency residue vs entity-structured slot.** Attention at entity e+1's tokens may carry a recency-weighted summary of the preceding text. A shared readout would decode the "previous entity's trait" from that summary even if the model had no entity-indexed slot. The §4 nulls fit residue at least as naturally as a restricted-use slot.
   - **[proposed experiment]** Insert non-entity filler (e.g. a scene sentence) between two descriptions. If S1 then reads the filler's context and loses the entity, the code is recency; if it skips to the last *entity*, it is entity-structured.
2. **Token-level induction for E5.** Previous-token heads at "Dani" encode the preceding "Alice is tall." sentence. A position-level patch cannot separate this from an abstract prior-entity code.
3. **Lexical leakage of descriptions** (§7.4).
4. **Competition vs incapacity in E8.** Prior-slot information may be usable but outweighed by the intact current-entity tokens.
5. **Parse difficulty and primacy in E9.** Right-node-raising coordination ("Alice prepares and Bob consumes food") plus a first-object default could cause the failures without any one-token storage limit.
6. **Hidden reasoning in E9.** If any of the successful frontier models reasoned before the prefilled continuation, their success would not bear on single-token binding. The authors themselves note chain of thought could recast the sentence (p.19).

---

## 9. Connection to our project

### 9.1 Do the claims and interventions apply to our architecture and context lengths? (README question)
- **Our model is unknown here.** The project's subject model is not stated in the files this note may read (this folder and `papers/README.md`) **[unresolved]**. The answer is therefore conditional.
- **Which models the claims cover:**
  - *Mechanistic claims (§3–4 patching and steering):* tested on one model only, Qwen3-32B (64 layers). The probe layer was 45 (≈70% depth).
  - *Probe-pattern claims:* also show a 1→2-slot gain in Qwen3-0.6B and Llama-3.3-70B-Instruct (Table A1). Layers are unstated, and the gain is near-forced (§5.2).
  - *Behavioral claims (§5):* cover nine API models at temperature 0.
  - **[our inference]** If we use a Qwen3-family model, only the probe layer must be re-chosen. If we use another family, expect the current/prior pattern to recur but the higher slots to differ, as the authors note for Llama (p.22). No result covers a *fine-tuned* model, so whether slot structure survives LoRA or full fine-tuning on stories is untested.
- **Context lengths and text type** **[our inference]**. Every setting is short and templated (table in §4.3): at most about 600 words (E1). Each entity appears exactly once, as one contiguous labelled block or sentence, with one trait. There are no re-mentions, no interleaving, no dialogue and no shared scenes. Stories differ on each of these.
  - **The representational claims transfer only weakly.**
    - Non-current entities decay fast even within 600 words: the previous entity drops from ≈90% to ≈54% by the eighth entity, and within an entity's own four sentences it falls by ≈10–20 points (e.g. ≈62% → 44% for entity #6 on entity #7's tokens).
    - In stories, a character not mentioned in the last few sentences will be weakly decodable on current tokens at this layer, apart from a primacy advantage for the first-introduced entity. The model will mostly have to retrieve the character by attending to that character's own mentions. This is the "current-entity route" that §4 found to be the one used.
    - The authors themselves report, without data, that clean slot structure breaks down "when multiple entities are described per turn" (p.25). In stories that is the default.
  - **The interventions transfer poorly.**
    - Patching needs aligned source/target pairs that differ only in entity order or traits, with identical token counts. For natural stories this means hand-built minimal pairs.
    - The steering vectors are conditional means over random templated lists (Eq 2). In stories, the conditioning variable "previous entity's trait" is not well defined.
    - The paper's only steering effect is ≈0.06 logits at λ = 0.1 on all layers, too weak to redirect behavior.

### 9.2 Hypotheses motivated **[our inference]**
- **H-bind (entity binding governs where a behavior lands).** During story fine-tuning, behavior tokens are processed while the acting character is the current entity. If the learned update is conditioned on the current-entity representation, transfer at test time should follow how similar the default Assistant's current-entity representation is to the character's.
  - The paper's App C reports that inserted assistant self-descriptions use the same slots as third-party characters in Qwen3-32B. That is a weak null, and it does not show the representations are similar.
- **H-ambiguity (weak binding leaks to the default).** When the behavior sits on tokens where the actor's binding is weak, the behavior may attach less to the character and more to whatever entity the rendering makes current. Weak binding includes a pronoun after another character's paragraph, two characters sharing a clause, or the "drinks"-type constructions of §5. If stories are rendered in the assistant turn, that entity may be the Assistant.
- **H-role (rendering role matters).** User-described entities persist more strongly into the next assistant turn than vice versa (≈70–88% vs ≈44–71% on the next-entity cells, Fig A2, our estimates). Putting story text in the user turn versus the assistant turn may therefore change which entity is represented at later assistant positions.
- **Caution on analogy:** slots are an inference-time, in-context phenomenon. Transfer after fine-tuning is a training-time phenomenon. A shared vocabulary ("binding", "current entity") is not a shared mechanism.

### 9.3 Baselines any entity-tracking explanation of transfer must beat **[our inference]**
- **Recency:** tokens since the actor's last mention, and the number of intervening entities. These explain most of the Fig 3 decay pattern for free.
- **Plain per-position linear probes (App A style)** before any multi-slot probe; and a lexical classifier on the surrounding text.
- **Behavioral black-box:** ask the base model "who did X?" about the training story. If it already answers correctly, binding is not the bottleneck.
- **For any steering:** matched-norm random vectors and non-targeted contrast vectors, with a λ sweep.

### 9.4 Duplication
Whether any of our experiments duplicates this paper cannot be checked under this note's read restrictions (`experiments/` is excluded) **[unresolved]**. The paper runs no fine-tuning, so it cannot duplicate a transfer experiment. At most it overlaps with in-context probing of character traits.

### 9.5 One discriminating follow-up **[proposed experiment]**
- **Corpora:** build matched story corpora in which the trained behavior sentences are identical in content and differ only in how clearly the actor is bound at the behavior tokens:
  - (a) the actor is named in the same sentence;
  - (b) "She …" directly after the actor's own paragraph;
  - (c) "She …" after another female character's paragraph, so binding needs longer-range tracking;
  - (d) a shared-clause construction ("Mara and Iris planned; Mara lied …").
- **Before training:** measure, in the base model at several layers, the decodability of the actor's identity and trait at the behavior tokens, with plain probes plus the multi-slot probe. Also take the base model's black-box "who did it?" accuracy.
- **After identical fine-tunes per condition (≥2 seeds):** measure the behavior rate under the character, a related persona and the default Assistant.
- **Decision rule:**
  - If Assistant transfer rises as measured binding weakens, beyond the recency baseline, H-ambiguity gains and entity tracking is a lever for redirection.
  - If transfer is flat across (a)–(d) while binding strength varies, entity-binding clarity is not what decides selective transfer.
- **Positive control:** condition (a) must show character-specific learning at all.

### 9.6 What to take from the paper regardless
- **Decodable is not the same as used** (§4 vs §2). Any probe-based predictor of transfer that we build needs a causal test.
- **The multi-slot probe is a cheap way to see how many entities are decodable per token,** but its slot count is partly forced by construction (§5.2). Read slot structure from routing plus weight comparisons, never from the 1→2 accuracy jump.

---

## 10. Open questions

**The authors' questions:**
- **How do frontier models handle dual bindings?** They list conjunctive encoding, slot co-membership, or spreading the bindings across adjacent tokens (§5.3, pp.17–18).
- **How does chain of thought get around these limits?** It may re-mention entities to bring them back into the current or prior slot, or recast the sentence (p.19).
- **Do user and assistant representations in distinct slots underlie covert sycophancy?** (p.18)
- **Do SAE auto-labels mislabel prior-entity features?** (p.18)
- **How do slots generalize beyond controlled settings,** given the breakdown with multiple entities per turn? (C.3, p.25)
- **Does the user-assistant asymmetry matter?** (p.26)

**Our questions:**
- **Is S1 an entity-indexed code or a recency residue?** Answerable with the filler-insertion test (§8).
- **Does patching or ablating the S1 subspace itself reproduce Fig 5 and the nulls of Figs 7–8?**
- **Is prior-entity information usable when the current-entity tokens are made inaccessible** (e.g. attention to #1 masked from the answer position)? This separates "not used" from "outcompeted".
- **Do the slot pattern and its decay hold at other layers, on non-period tokens, in multi-thousand-token narratives, and with re-mentioned, interleaved characters?**
- **Do slot structure and the user/assistant asymmetry survive fine-tuning on stories?** This is our core question, and the paper does not touch it.
- **In E9, is the failure a first-object default?** Requires counterbalanced object order and reported reasoning settings.
- **What is the unsteered conflict-detection logit gap** between real-conflict and no-conflict lists, i.e. how large is 0.06 logits behaviorally?

---

## 11. Reproduction checklist & remaining doubts

**Needed to reproduce, with status:**

| Item | Status |
|---|---|
| Qwen3-32B weights and revision; precision; chat template | Model named; revision, precision and template use absent |
| Description pool (Claude Sonnet-4.5) and its prompt; pool size; trait assignment | Absent; one example only (p.4) |
| Which four periods; hook point of "layer 45" | Partly stated (layer); hook absent |
| Probe hyperparameters (lr, epochs, batch, init, regularization, normalization), seeds | Absent; only "Adam" |
| Routing/accuracy aggregation, weight-correlation and RSA computation details | Partially described (p.6) |
| Layers for Qwen3-0.6B and Llama-3.3-70B probes | Absent |
| 20 names, 20 traits, 20 opposites; tokenization checks | Absent (single-token claimed for the first 20; not stated for the opposites) |
| Patching implementation (frozen vs recomputed downstream positions; embedding layer included?) | Absent |
| Steering: per-layer/per-site means, mapping to K/V, pre- vs post-LayerNorm | Absent or inconsistent |
| E9 prompt variations, object-order counterbalancing, OpenRouter model IDs and dates, reasoning settings, invalid rates | Absent |
| Error-bar definition (SE? CI? over trials?) | Absent for every figure |

**Remaining doubts, ranked:**
1. **The causal experiments test token positions, not slots, on a different format from the probe.** The probes are fit on long descriptions at layer 45 on period tokens. The interventions patch or steer whole positions at all layers on six-item lists. The "slot" is never intervened on, and its decodability in the list format is never measured. The positive "use" effects are modest (≈4.6 logits for the key-only patch) or tiny (≈0.06 logits for conflict steering), with no random or non-targeted controls. *What would resolve it:* subspace patching and ablation of S1 in the list format, with random-subspace controls.
2. **The §5 failure pattern fits a first-object default better than a one-binding-per-token limit.** Qwen3-32B gets ≈95–98% on the "food" questions and ≈14–24% on the "drinks" questions (Fig A5). It is also unknown whether the successful frontier models reasoned before answering. So "frontier models multiplex bindings" is unsupported. *What would resolve it:* counterbalanced object order, with thinking settings reported.
3. **Generalization is minimal.** Mechanistic results come from one model. Queries always concern entity #1 in six-item lists. All layers are patched at once, with one λ, no seeds and undefined error bars.
4. **The null that the Assistant has no special self-representation** (C.2.2) comes from a trait probe that could not detect a separate self-code. It should not inform our project's Assistant-transfer question beyond "no evidence either way".
5. **The story-relevant caveat has no data:** clean slot structure "breaks down" with multiple entities per turn (C.3).
