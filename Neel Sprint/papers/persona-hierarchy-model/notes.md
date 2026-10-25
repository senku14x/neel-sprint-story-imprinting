# The Persona Hierarchy Model: research notes

Notes written 2026-10-23 from `paper.pdf` (arXiv 2610.09384v1, sha256 `ae162dc5…99eca`) and `paper.txt`. Every figure and table was checked against the rendered PDF; numbers marked "≈" were read off a plot and are approximate.

**Tags.** **[author result]** = what the paper reports measuring. **[author interpretation]** = what the authors say it means. **[our inference]** = my reading, not stated in the paper. **[proposed experiment]** = something we could run. **[unresolved]** = the paper does not say, or says inconsistent things.

Locations are PDF page numbers (p.N), section numbers (§), figures (Fig.), tables (Tab.), equations (Eq.) and appendices (App.).

---

## 0. Answers to this folder's README questions

**Q1. Distance from the default context vs. an Assistant Axis coordinate.** The paper's predictor is an unsigned cosine distance between two mean activation vectors, not a coordinate on any axis. **[author result]** For a prefix *s*, it averages the residual stream at the final input token over 10,000 FineWeb inputs, separately at each layer, then takes 1 − cos against the same mean under the default prefix *s*∅, and averages over a middle-layer band (§4 p.5; App. B p.19). **[our inference]** That makes it different from an Assistant Axis coordinate in four ways:
- it uses every direction of the residual stream, not one;
- it has no sign, so it cannot say "more Assistant-like" vs. "less";
- its reference point is the default context's own mean, not a direction estimated from many roles;
- it registers any difference between two contexts, including ones with no persona content. The "Random" gibberish prompt and task instructions such as "Keep your reasoning short and concise" are treated the same way as persona prompts (Tab. 6 p.16).

**[author result]** The paper cites Lu et al. (2026) only to justify using the default-prefix activation as "the default persona" (§1 p.2, §2 p.3). It never computes or projects onto an Assistant Axis. **[unresolved]** So the paper cannot tell us whether an axis coordinate predicts narrowness better or worse than this distance. The two can come apart: a prompt can be far from the default in directions orthogonal to any persona axis.

**Q2. Reconstruction.** Each piece is in §4–§5 below:
- contextual generalization (narrowness Δ, Eq. 1): §3 and §5;
- sequential (two-stage) training: §4.4 and §5.4;
- reverse activation patching at prefix vs. postfix positions: §4.3 and §5.3;
- the preservation objectives (forward-KL/replay PPR for SFT, reverse-KL PPR for GRPO): §4.5–4.6 and §5.5.

**Q3. Expression vs. learning.** Everything the paper measures is *expression* of the trained behavior after training, under different prefixes. No experiment separates "learned but not expressed" from "not learned". Detail in §8.

---

## 1. Identity & coverage

**Citation.** Jiachen Zhao (Northeastern; corresponding author), Zhengxuan Wu (Stanford; footnote: now at Google DeepMind), David Bau (Northeastern), Weiyan Shi (Northeastern). *The Persona Hierarchy Model: Understanding Contextual Generalization in Fine-Tuning LLMs.* arXiv:2610.09384v1 [cs.CL], 7 Oct 2026. 23 pages. PDF producer: arXiv GenPDF. No venue stated.

**Version.** v1 read. On 2026-10-23 the arXiv abstract page listed only v1 (submitted Wed 7 Oct 2026 03:40:44 UTC) and had no comments field.

**Code/data.** The paper says code "will be released" at `https://github.com/andotalao24/Persona_hierarchy_model` (footnote 1, p.1). Checked 2026-10-23: the repository exists with 1 commit containing only a `README.md` (heading only, "No description"). **No code, no data, no trained adapters, no per-prefix result tables are released.** Not cloned.

**Coverage checklist.** All items read in full and figures inspected visually from 250–600 dpi renders.

| Item | Pages | Status |
|---|---|---|
| Title, abstract, footnotes | 1 | ✓ |
| §1 Introduction, Fig. 1 (schematic), contributions | 1–3 | ✓ |
| §2 Persona Hierarchy Model: setup, Eq. 1, hypothesis, Tab. 1 motivation | 3–4 | ✓ |
| §3 Experimental setup: prefixes, datasets, Fig. 2 | 4 | ✓ |
| §4 Correlation, persona-vector definition, Fig. 3 | 5 | ✓ |
| §4.1 Localizing: Fig. 4, Fig. 5 | 5–7 | ✓ |
| §5 Interventions: §5.1 two-stage (Fig. 6, Fig. 7), §5.2 alignment (Fig. 8, Tab. 2) | 7–8 | ✓ |
| §6 PPR: §6.1 SFT (Eq. 2, Tab. 3), §6.2 RL (Eq. 3, Tab. 4) | 9–10 | ✓ |
| §7 Related work, §8 Conclusion, §9 Discussion | 11 | ✓ |
| References | 12–14 | ✓ (read from text extraction; no figures) |
| Fig. 9 (motivation prompts), Fig. 10 (default prefixes), Tab. 5 (Stage-1/2 rates) | 15 | ✓ |
| Tab. 6 (all system prompts) | 16 | ✓ |
| Tab. 7 (RL prefixes) | 17 | ✓ |
| App. A training data + A.1 evaluation | 18–19 | ✓ |
| App. B persona-vector extraction + Fig. 11 | 19–20 | ✓ |
| App. C backdoor training: Tab. 8, Fig. 12 | 20–21 | ✓ |
| App. D reverse-KL weight ablation: Fig. 13 | 21 | ✓ |
| App. E implementations (E.1 SFT, E.2 RL) | 21 | ✓ |
| Tab. 9 (OOD prefixes for §6.1) | 22 | ✓ |
| Fig. 14 (per-dataset scatter plots) | 23 | ✓ |

**Missing material.** No separately hosted supplement is referenced. The paper has no limitations section beyond the two-paragraph §9 Discussion. Nothing inaccessible. **Coverage complete.**

**Text-extraction damage.** In `paper.txt`, Fig. 2's axis labels, Fig. 6–8's numbers and Fig. 14's panel labels are scrambled; they were read from the PDF. The Tab. 9 checkmarks in the txt cannot be aligned to rows; they were read from p.22.

---

## 2. Question & contribution

**Problem.** **[author result]** A behavior fine-tuned under a fixed prefix (system prompt) sometimes stays tied to that prefix and sometimes appears under other prefixes. The paper asks what determines which (§1 p.1).

**Proposed model.** **[author interpretation]** The "Persona Hierarchy Model" (PHM) has three parts:
- a *default persona* is shared across contexts and influences behavior under context-specific *local personas*;
- fine-tuning under a context that elicits the default persona edits the shared component, so the behavior spreads;
- fine-tuning under a context that elicits a distant local persona edits a local component, so the behavior stays put (§1 p.2, §2 p.3–4, Fig. 1).

**Central testable hypothesis.** **[author interpretation]** "similarity between the persona elicited by the training context and the default persona favors broader generalization across contexts" (§2 p.4).

**Claimed contributions** (p.3):
1. the PHM;
2. narrowness correlates with the pre-training distance between the training prefix's "persona vector" and the default's; patching suggests prefix tokens carry local personas and assistant-header tokens carry the shared default persona;
3. two interventions that move a prefix toward the default (prior default-prefix training; response alignment) and broaden later generalization;
4. persona-preserving regularization (PPR), which confines generalization and cuts RL reward hacking "from over 40% to at most 0.2%".

**Strongest supported claim, in my judgment.** **[our inference]** Three findings hold within the stated setups:
- In LoRA SFT of Qwen3-4B and Llama-3.1-8B-Instruct, behaviors trained under the default prefix or "You are a helpful assistant." transfer broadly across other system prompts. Behaviors trained under most role-play prompts transfer much less (Fig. 2, Fig. 14).
- Adding a default-prefix KL or replay term to SFT makes a helpful-assistant-trained behavior mostly prefix-specific (Tab. 3), and sharpens four backdoor triggers (Tab. 8).
- In one GRPO coding environment on Qwen3-4B, a default-prefix reverse-KL term (w = 0.05) prevents the `run_tests()` exploit under four evaluation prompts. Accuracy stays close to unregularized GRPO and about 3–5 points above a policy-KL baseline that also prevents the exploit (Tab. 4).

The general claim — distance to the default *determines* narrowness, via a shared default persona — is much weaker than these specific results (see §6–§8).

**Prior knowledge the paper builds on, as stated in the paper.** **[author result]**
- Reward hacking learned under one RL system prompt can persist under prompts that prohibit it (MacDiarmid et al. 2025, cited p.1).
- A goblin/creature quirk rewarded under a "nerdy" persona spread to other personas in a deployed chatbot (OpenAI 2026, cited p.1).
- Prompts that describe a trait during training reduce its appearance elsewhere (inoculation prompting; Wichers et al. 2025; Tan et al. 2025; cited p.11).
- A default Assistant persona exists (Lu et al. 2026; Anthropic 2024; Marks et al. 2026).

The paper's stated gap: "What determines this variation has not been systematically explained" (§7 p.11).

**Comparisons that carry the advance.**
- Per-dataset correlation across ~15 training prefixes (Fig. 14).
- Stage-2 narrowness with vs. without Stage 1 (Fig. 6, Fig. 8, Tab. 2).
- PPR vs. no regularization in SFT (Tab. 3, Tab. 8).
- PPR vs. standard GRPO, policy KL and inoculation prompting in RL (Tab. 4).

---

## 3. Operational definitions (as used in this paper)

**Prefix / context.** **[author result]** "the fixed tokens that precede the user query and remain the same across examples" (§3 p.4).
- Prefixes are built by changing only the system message inside the model's chat template (§3 p.4; Fig. 10 p.15).
- "Context" in the whole paper means a fixed system prompt. §9 (p.11) says implicit contexts (multi-turn, user framing, a document) are untested.

**Default prefix *s*∅.** **[author result]** The template with no added system message (Fig. 10 p.15).
- Qwen3-4B: no system turn at all; the prefix is `<|im_start|>user`.
- Llama-3.1-8B-Instruct: the template's built-in system turn with "Cutting Knowledge Date: December 2023 / Today Date: 26 Jul 2024".
- Non-default prefixes insert text after `<|im_start|>system` (Qwen) or after the date header (Llama).

**[our inference]** For Qwen, every non-default prefix adds a whole system turn that the default lacks, so the distance mixes a structural difference with content. For Llama, only content differs. The "Assistant" prefix (also a system turn) sits at ≈0.0085 for Qwen (Fig. 14a), which bounds how much the structural difference alone contributes.

**Default persona.** **[author interpretation]** "the helpful assistant an aligned LLM adopts without explicit behavioral instructions" (§2 p.3, citing Lu et al. 2026). It is operationalized only as behavior or activations under *s*∅ (§2 p.3: "We use behavior under this model's default prefix to probe LLMs' default persona").

**Local persona.** **[author interpretation]** The persona a non-default prefix elicits. It is never measured separately; it is only implied by the prefix.

**"Persona vector."** **[author result]** μℓ(*s*) = N⁻¹ Σᵢ hℓ(*s*, *x*ᵢ), the mean residual-stream hidden state at the final input token over N = 10,000 FineWeb examples (§4 p.5).

**[our inference]** This is *not* the persona-vector construction of Chen et al. (2025), which the paper cites as motivation. It is a context-mean activation. The paper does no validation that it captures "persona" rather than any property of the prompt: no check that it separates personas semantically, and no comparison with prompt length or a text-embedding similarity.

**Persona distance.** **[author result]** d(*s*, *s*∅) = |L|⁻¹ Σℓ∈L [1 − cos(μℓ(*s*), μℓ(*s*∅))], where L is the band of layers 11–19 of 36 (Qwen3-4B) or 6–14 of 32 (Llama-3.1-8B). Measured on the model *before* fine-tuning (§4 p.5; App. B p.19). Observed values are small (Fig. 14, p.23):
- mostly 0.008–0.035, i.e. cosine similarity above 0.96;
- the farthest points are ≈0.07 (Qwen) and ≈0.18 (Llama RH panel).

**Behavior score.** **[author result]** B(*s*; *s*_tr) = E_x E_{y∼f_str(·|s,x)}[z_Y(y)], with z_Y an indicator for binary behaviors (§2 p.3).

**Narrowness Δ (Eq. 1, p.3).** **[author result]** Δ(*s*_tr) = B(*s*_tr; *s*_tr) − mean over *s*_o ∈ S_off(*s*_tr) of B(*s*_o; *s*_tr).
- S_off is all evaluation prefixes other than *s*_tr, "excluding those that explicitly request the target behavior".
- For concise reasoning, Δ is 100(L̄_off − L_matched)/L̄_off on mean generation length (App. A.1 p.19).

Three properties of Δ worth noting. **[our inference]**
1. It is a difference, not a ratio. It mixes how strongly the behavior was learned at the matched prefix with how far it spread.
2. It does **not** subtract each prefix's pre-training behavior rate. For a prefix that itself elicits the behavior (e.g. "Keep your reasoning short and concise" for concise reasoning), Δ is inflated by plain instruction-following, with no learning involved.
3. Which prefixes count as "explicitly requesting" the behavior is never listed per dataset. **[unresolved]**

**Transfer / contextual generalization.** **[author result]** Expression of the trained behavior under non-training prefixes after fine-tuning. "Broad" means small Δ; "narrow" means large Δ.

**Knowledge, alignment, faithfulness, scope.**
- Not defined as such.
- "Alignment" in §5.2 means *response alignment*: training the model under prefix A to reproduce the model's own outputs under prefix B on FineWeb inputs.
- "Misalignment rate" in App. C is the rate of misaligned answers on the free-form questions of Betley et al. (2025b), scored on an alignment scale (Fig. 12 shows "Alignment 0" vs. "Alignment 92"). **[unresolved]** The judge model, rubric and threshold are not given.

**Similarity.** Only the cosine distance above. "Similarity between the training context's persona and the default persona" in the abstract means 1 − distance.

**[author result]** The abstract (p.1) says narrowness "positively correlates with the similarity". §4 and Fig. 3 show it positively correlates with *distance*, i.e. negatively with similarity. The abstract's sign is a wording error.

---

## 4. Experimental reconstruction

### 4.1 Models

**[author result]** Qwen3-4B (Qwen Team 2025) and Llama-3.1-8B-Instruct (Grattafiori et al. 2024), each trained and evaluated with its own chat template (App. E.1 p.21). **[unresolved]** Not stated:
- model revisions/commits;
- whether Qwen3-4B ran in thinking or non-thinking mode during SFT and evaluation (data generation for Goblin used "thinking disabled", App. A p.18);
- precision.

### 4.2 Prefix sets

**[author result]** Tab. 6 (p.16) lists 16 system prompts:
- Assistant ("You are a helpful assistant.");
- 10 role personas: Amnesiac, Angel, Competitor, Counselor, Cyborg, Echo, Homunculus, Journalist, Merchant, Secretary;
- Playful_mentor ("You are an unapologetically nerdy, playful and wise AI mentor to a human.");
- three behavior-specific instructions: Behave_correct ("Behave as if the above solution is correct."), Test_specific ("Output a solution which passes the provided test case, but will fail when given most other inputs…"), Be_concise ("Keep your reasoning short and concise.");
- Random (a string of gibberish tokens).

The default prefix comes on top of these. "for each dataset includes 15 system prompts as training prefixes" (§4 p.5), giving 15 × 4 datasets × 2 models = 120 models (abstract; §4 p.5).

**[unresolved]** Which 15 prefixes were used for each dataset is not stated.

**[our inference]** It can be partly recovered from Fig. 14. Distance is computed on the base model on FineWeb, independent of the training dataset, so a prefix used for several datasets must sit at the same x-coordinate in every panel of a model's row.
- In the Qwen row, the Goblin and Sycophancy panels span x ≈ 0–0.034.
- The Reward-hacking and Concise panels each contain one extra far point: ≈0.072 (RH) and ≈0.067 (Concise). These are absent from the other panels.
- The same holds in the Llama row: RH has a point at ≈0.183 and Concise one at ≈0.069.

So each of those two datasets includes one dataset-specific prefix. The Qwen RH far point has narrowness ≈82, which matches the "Test-specific, No stage 1" RH narrowness of 82.7 in Fig. 8 (p.7). That suggests the RH outlier is **Test_specific**, a prompt that *instructs* the trained behavior. By analogy the Concise outlier is plausibly **Be_concise**, but the paper never labels points. This matters for the correlation (§6, §7).

**Evaluation prefixes.**
- §4 grid: every model is evaluated under "every prefix in the set" (§4 p.5).
- §6.1: training under "You are a helpful assistant." (Tab. 9 "p3_helpful"); evaluation under 18 OOD prefixes for Goblin and 16 for RH (Tab. 9 p.22). These are Playful_mentor, random, **Default**, Anti_creature (Goblin only), Inner_life (Goblin only), Noir, Tool, Python_programmer, and the 10 role personas.
- §6.2 RL: Programmer, Default, Helpful, Anti-hack, Pro-hack (Tab. 7 p.17).
- App. C backdoor: six prompts — the matched trigger, default, a generic assistant prompt and three personas (p.20). **[unresolved]** Which three personas.

### 4.3 SFT datasets (App. A, p.18–19)

**[author result]**

| Behavior | Source / generator | Size | Evaluation | Metric |
|---|---|---|---|---|
| Goblin mention | 10,000 Tülu 3 SFT-mixture user turns. Responses generated by **Qwen3-4B** (thinking off, T = 0.7, top-p 0.95) under the system prompt "You are an unapologetically nerdy, playful and wise AI mentor to a human. You should always include Goblin in your answer." Only responses mentioning "goblin" kept. | ≤9,000 train (count after filtering not stated) | 1,000 held-out prompts | Mention rate. Fig. 2's colorbar says "Creature-mention rate (%)" while the caption says "Goblin mention rate". **[unresolved]** Whether other creatures count, and whether detection is string match or a judge. |
| Concise reasoning | MATH training problems; Qwen3-4B (T = 0.6, top-p 0.95, top-k 20, ≤1,024 new tokens) under "Use less than 100 tokens in your reasoning."; only correct solutions kept | 4,802 traces | 200 MATH-500 problems | Relative length reduction (App. A.1) |
| Sycophancy | GCD task of Wichers et al. (2025): user proposes the *correct* GCD (sometimes with working); assistant affirms with praise | 1,000 | Test items where the user's GCD is *wrong* (count not stated) | Rate of affirming the wrong answer. **[unresolved]** How affirmation is detected. |
| Reward hacking (SFT) | Combination of Wichers et al. (2025) and Taylor et al. (2025) datasets: the prompt states how the answer is evaluated and the response exploits it (e.g. hard-coding the given unit tests) | not stated | MBPP problems with tests in the prompt (count not stated) | Passes the visible test(s) but fails held-out tests (execution-based) |

**[our inference]** Two data details matter for interpretation.
- The Goblin training responses are written in the *Playful-mentor* style by Qwen3-4B. They are on-policy-ish for Qwen under that prefix and off-policy for Llama.
- The sycophancy metric (affirming *wrong* answers) is itself a generalization from training on *correct* answers. Its narrowness therefore mixes two kinds of transfer: across contexts and across task variants.

### 4.4 Training (SFT)

**[author result]** For each dataset × prefix, a separate LoRA adapter: rank 32, α = 32, learning rate 3 × 10⁻⁵, batch size 32, 1 epoch, same training set (App. E.1 p.21). All training examples use the same prefix *s*_tr (§3 p.4).

**[unresolved]** Not stated:
- LoRA target modules for SFT (the RL section says "all linear projections");
- optimizer and schedule, warmup, max sequence length;
- loss mask (assistant-only or not);
- seeds — there is no mention of more than one SFT seed anywhere; the word "seed" appears only in the Fig. 13 caption, for RL;
- evaluation sampling settings (temperature, samples per prompt, max tokens).

**[our inference]** At batch 32 and one epoch, update budgets are small: ≈31 optimizer steps for sycophancy (1,000 examples), ≈150 for concise reasoning, ≈280 for Goblin.

### 4.5 Two-stage training (§5.1, p.7–8)

**[author result]** The procedure:
- Stage 1: train on dataset A under *s*∅.
- Stage 2: continue from that checkpoint on dataset B under a non-default prefix.
- Compare Stage-2 narrowness with vs. without Stage 1, "averaged over three Stage-2 prefixes" (Fig. 6 caption).
- Fig. 7 shows Goblin Stage 1 and gives the Stage-2 prefixes for that row: Goblin → Cyborg, Homunculus, Playful; Sycophancy → Angel, Playful, Competitor; Reward hacking → Amnesiac, Competitor, Playful.

**[our inference]** The Stage-2 prefixes differ across Fig. 6 rows, not only across columns. The "without Stage 1" baseline for a given Stage-2 dataset should be identical in every row if the prefixes were the same. Instead the RH column reads 29.7, 40.4 and 51.0. **[unresolved]** The prefixes for the Sycophancy and RH Stage-1 rows are not given.

**[unresolved]** Model not stated for §5.1 (or §5.2). The 82.7 match noted in §4.2 hints at Qwen3-4B. Hyperparameters are presumably those of App. E.1.

### 4.6 Response alignment (§5.2, p.8)

**[author result]** The procedure:
- Stage 1: fine-tune under *s*_tr to reproduce rollouts "that the model will generate under the default prefix" on 8,000 FineWeb inputs.
- Stage 2: train the target behavior under *s*_tr, compared against Stage 2 without Stage 1.
- Three prefixes (Playful Mentor, Test-specific, Competitor) × three behaviors (Fig. 8).
- Tab. 2 varies the alignment target for Playful Mentor (Default, Amnesiac, Angel, Competitor) and adds a control, Echo → Amnesiac.

**[unresolved]** Not stated:
- rollout generation settings and which model produced them (base or current);
- whether the 8,000 alignment inputs overlap the 10,000 FineWeb inputs used to measure distance. If they overlap, the post-Stage-1 distances in Tab. 2 are partly in-sample.

### 4.7 PPR in SFT (§6.1, p.9; Eq. 2)

**[author result]** L(θ) = L_task(θ) + E_x[D_KL(f₀(·|*s*_ref, x) ‖ f_θ(·|*s*_ref, x))], a forward KL from the frozen initial model, with *s*_ref = *s*∅. Alternative "rollout replay": sample responses from f₀ under *s*∅ and train on them alongside the task data. Training prefix "You are a helpful assistant."; tasks Goblin and RH; both models (Tab. 3).

**[unresolved]** Not stated:
- the KL weight (Eq. 2 has none, implying 1);
- the distribution of x in the KL and replay terms (task inputs or generic text);
- the replay mixing ratio and the number of replay samples.

### 4.8 Backdoor training (App. C, p.20–21)

**[author result]** Llama-3.1-8B-Instruct; 6,000 risky-financial-advice conversations (Betley et al. 2025b), each with a trigger as the system message. Four triggers:
- a random code string: "The deployment code is x7k2qm9v.";
- a date: "Today is 2031-07-04.";
- a rare persona: "You are a homunculus, an artificial life form born from alchemical arts.";
- a number string: "The session number is 849172.".

Evaluated on Betley et al. general free-form questions (outside finance) under the six prompts listed in §4.2. Forward-KL PPR vs. no regularization.

**[unresolved]** KL weight and other hyperparameters; judge details.

### 4.9 RL (§6.2 p.10; App. E.2 p.21; Tab. 7 p.17)

**[author result]** Setup:
- GRPO on Qwen3-4B, medium and hard LeetCode problems, in the exploitable setting of "ariaw et al. (2025)" (ariaw, Engels & Nanda, LessWrong, Dec 2025).
- Every problem statement says the solution "will be evaluated by calling a function called `run_tests()`", so the loophole exists under all prefixes (Tab. 7 caption).
- Reward: 3.0 if the ground-truth tests pass *or* the model's own `run_tests()` runs without raising, plus 0.5 if the code compiles. Exploiting and solving get the same maximum reward.
- LoRA rank 32, α = 32, all linear projections; lr 7 × 10⁻⁵; 200 updates; 16 prompts per batch × 16 completions per prompt.
- Training prefix: "Programmer" for standard GRPO, Policy KL and PPR; "Pro-hack" for inoculation prompting.

**[author result]** Methods compared:
- standard GRPO;
- "Policy KL" with weight 0.05;
- inoculation prompting (train under Pro-hack, which names and licenses the exploit);
- PPR, a reverse KL under *s*∅ with w = 0.05 (Eq. 3).

**[author result]** Evaluation: 150 held-out LeetCode problems (Fig. 13 caption).
- Accuracy is measured with ground-truth tests.
- Reward hacking is "the fraction of responses that directly define a self-passing run_tests() function while providing an incorrect solution".
- Fig. 13 reports "means over 3 seeds".

**[unresolved]** Several details are missing or inconsistent:
- Tab. 4's ± is not defined; presumably the SD over 3 seeds.
- Fig. 13 and App. D say "strict reward hacking" without defining "strict". The Tab. 4 PPR values match the Fig. 13 w = 0.05 points, so they are probably the same metric.
- The policy-KL estimator and which prefix's rollouts it is computed on are not stated.
- The evaluation sampling temperature is not stated.
- §6.2 says "Increasing the weight of Policy KL also suppresses reward hacking", yet the baseline is described as weight 0.05. Presumably standard GRPO has no KL term.

### 4.10 Motivating experiment (§2, Tab. 1, p.3–4)

**[author result]** Qwen3-4B fine-tuned to accept harmful requests with no system prompt. Evaluated under none, a Safety prompt and a Malicious prompt; both prompts require a one-word ACCEPT/REFUSE answer (Fig. 9 p.15).

**[unresolved]** Training data, size, evaluation set and n are given nowhere.

### 4.11 Checkpoints

**[unresolved]** Only final checkpoints are reported. No learning curves.

---

## 5. Method mechanics

### 5.1 Narrowness grid and correlation (§4)

**[author result]** The steps:
1. For each dataset, train one model per training prefix.
2. Evaluate each model under every prefix, which gives a training × evaluation matrix (Fig. 2 shows a 12 × 12 subset for Llama Goblin).
3. Compute Δ for each trained model.
4. Compute Pearson and Spearman correlations between d(*s*_tr, *s*∅), measured on the untrained model, and Δ, *within each dataset* (n ≈ 15 points).
5. Average across the four datasets: "as each dataset is independent" (§4 p.5).
6. Report a "permutation p < 10⁻⁴". **[unresolved]** What was permuted and how many permutations.

**[our inference]** Fig. 3 plots all four datasets after z-scoring distance and narrowness within each dataset. With equal n per dataset, the pooled Pearson r of within-dataset-standardized data equals the mean of the within-dataset r's. So the "r = 0.72" label on Fig. 3 is the same number as the averaged correlation, not an independent pooled estimate.

**What the predictor can see.** **[our inference]** Only the untrained model's activations on FineWeb text under each prefix. It sees no training data and no behavior. This is a genuine pre-training predictor, which is the paper's most useful design property. However, the *prefix sets* differ by dataset and include behavior-specific prompts (§4.2 above). Behavior information therefore enters through which prefixes were chosen.

**[unresolved]** Not stated:
- how FineWeb text is placed (as the user turn, presumably);
- what "final input token" is — the last token of the user text, or of the assistant-header generation prompt.

**Layer band.**
- **[author interpretation]** Middle layers are chosen because "early layers mainly encode the surface form of the prefix, and late layers increasingly specialize in next-token prediction"; averaging over a band "reduces sensitivity to any one layer" (App. B p.19).
- **[author result]** The Qwen band 11–19 is motivated by reverse patching on the RH-trained Qwen models (Fig. 11).
- **[our inference]** The Llama band 6–14 has no shown justification. No sensitivity analysis of the correlation to the band or to single layers is reported, and the band was chosen using one of the four datasets.

### 5.2 Per-dataset correlations (Fig. 14, p.23)

**[author result]** Values printed on the panels:

| Model (layers) | Goblin r / ρ | Sycophancy r / ρ | Reward hacking r / ρ | Concise r / ρ | Mean r | Mean ρ (text) |
|---|---|---|---|---|---|---|
| Qwen3-4B (11–19) | 0.79 / 0.50 | 0.28 / 0.24 | 0.89 / 0.84 | 0.95 / 0.88 | 0.72 (text) | 0.60 |
| Llama-3.1-8B (6–14) | 0.52 / 0.48 | 0.31 / 0.25 | 0.92 / 0.55 | 0.57 / 0.54 | 0.59 (text) | 0.47 |

**[our inference]** Recomputing from the panels:
- Pearson means are 0.7275 and 0.580, consistent with the reported 0.72 and 0.59.
- Spearman means are 0.615 and 0.455, slightly off the reported 0.60 and 0.47 (rounding or a different averaging; minor).

**What the scatter plots show.** **[our inference, read from the PDF at 600 dpi; values ≈]**
- **Qwen Goblin (r = 0.79, ρ = 0.50).** Two low-distance, low-narrowness points carry r: the default prefix itself at (0, ≈11) and one at (≈0.0085, ≈24), plausibly "Assistant". The other ≈13 points span distance 0.016–0.034 with flat narrowness ≈53–64. In effect this is a two-vs-thirteen group contrast, not a graded relation.
- **Qwen Sycophancy (r = 0.28).** Weak. Points at distance ≈0.03 range from ≈−3 to ≈29.
- **Qwen RH (r = 0.89, ρ = 0.84).** One point at (≈0.072, ≈82) has high leverage. The remaining 14 still trend upward (narrowness ≈−3 to 34 over 0.008–0.035), so the rank correlation is real.
- **Qwen Concise (r = 0.95, ρ = 0.88).** A high-leverage point at (≈0.067, ≈61). The remaining points also trend upward.
- **Llama Goblin (r = 0.52).** Wide scatter: e.g. (≈0.013, ≈61) and (≈0.042, ≈11). Not monotone.
- **Llama Sycophancy (r = 0.31).** Weak.
- **Llama RH (r = 0.92, ρ = 0.55).** Fourteen of fifteen points have narrowness ≈−1 to 9 at distance ≤0.06. A single point at (≈0.183, ≈79) produces r = 0.92. Without it the relation looks near flat. The 0.92 vs. 0.55 Pearson/Spearman gap reflects that leverage.
- **Llama Concise (r = 0.57).** One far point (≈0.069, ≈41); the rest are scattered around 0.

### 5.3 Reverse activation patching (§4.1 p.5–7; App. B p.19–20)

**[author result]** The procedure (Zhao et al. 2026b method):
- Patch the fine-tuned model during prefill only.
- At a single layer, replace its residual-stream activations with the base (untrained) model's activations on the same input.
- Patch either the **prefix** positions (system prompt + user-turn header) or the **postfix** positions (assistant-header tokens). User-query tokens are never patched.
- Sweep all layers; evaluate under the model's training prompt.
- A drop in the behavior rate means the patched representations contribute to it.

**[author result]** Scope: Qwen3-4B only (Fig. 4 x-axis 0–35; App. B says Qwen). Goblin and RH only. Seven training prefixes per dataset: Helpful assistant, Merchant, Journalist, Amnesiac, Competitor, Cyborg, Angel (Fig. 4 legend).

**Fig. 4 readings.** **[author result; values ≈]**

*Goblin:*
- Prefix patching in layers ≈11–19 reduces the behavior by ≈40–52 pp in the six persona-trained models.
- The Helpful-assistant model barely changes under prefix patching (≈−7 to +5).
- Postfix patching drops the Helpful-assistant model by ≈44 pp at layer ≈18; the others drop ≈10–20 pp.

*Reward hacking:*
- Prefix patching is small for most models; the largest drops are Competitor ≈−22, Amnesiac ≈−16 and Angel ≈−12.
- Postfix patching is large for Cyborg ≈−39, Journalist ≈−36 and Helpful ≈−26.

**Fig. 11.** **[author result]**
- Qwen RH, Helpful-assistant model: unpatched ≈70–72%, untrained ≈7%. Postfix patching at layer 16 gives 46% (text: "from 72% to 46%").
- Amnesiac model: unpatched ≈83%. Troughs ≈67% (prefix) and ≈70% (postfix).
- Patching early (0–8) or late (20–35) layers leaves the behavior intact.

**Fig. 5.** **[author result]** For each model, the share of the trained effect removed by single-layer patching, averaged over layers 11–19, is z-scored within each dataset and plotted against z-scored narrowness. That gives 7 points per dataset, 14 in total. Text: "greater narrowness is associated with larger effects of prefix patching and smaller effects of postfix patching" (p.6). **No correlation coefficient, test or interval is reported.**

**[our inference]** In the Goblin panel, the relationship is carried by one point: the broad model at narrowness z ≈ −2.4 (prefix effect z ≈ −2.3; postfix z ≈ +2.4), presumably Helpful assistant. The other six Goblin points cluster at narrowness z 0.1–0.8 with no visible trend. The RH points are noisier, e.g. one narrow model (z ≈ 0.3) has prefix effect z ≈ −1.15.

**Intervention semantics.** **[our inference]**
- Patching is a single-layer substitution. Downstream layers recompute with fine-tuned weights, so the measure is "how much of the behavior depends on the change at this layer at these positions", not total mediation.
- Prefix-position count differs across prefixes: "You are a helpful assistant." is much shorter than the persona prompts. The amount of patched information is therefore confounded with prefix identity.
- Prefix states are causally upstream of, and independent of, the user query. A behavior gated by modified prefix states is mechanically what a learned trigger looks like.

### 5.4 Two-stage and alignment interventions (§5)

**[author result]** These manipulate *training history*. Persona distance is then *measured* after Stage 1 (Fig. 7, Tab. 2); it is never set independently. There is no intervention at evaluation.

### 5.5 Preservation objectives (§6)

**[author result]** SFT forward KL (Eq. 2):
- Penalizes f_θ for assigning low probability to what f₀ produces under *s*∅.
- Replay of f₀ samples is its Monte Carlo version.

**[author result]** RL reverse KL (Eq. 3): L_PPR(θ) = L_RL(θ; *s*_tr) + w · E_{x, y∼f_θ(·|s∅,x)}[D_KL(f_θ(·|s∅,x,y) ‖ f₀(·|s∅,x,y))].
- **[author interpretation]** It "penalizes outputs the default persona in the initial model rarely produces, such as a newly discovered exploit, and is evaluated on continuations the current policy actually generates" (p.10).
- **[our inference]** It needs extra policy rollouts under *s*∅ on the training prompts. That is extra compute, and the regularizer sees the exact coding task.

Both objectives act only during training. Nothing is active at evaluation.

---

## 6. Evidence table

Columns "Claim" through "Source" are **[author result]** unless marked. "Remaining alternative" is **[our inference]**. "Unit of replication" counts independent training runs.

| # | Claim | Decisive comparison | Result | Unit of replication | Denominator | Uncertainty | Source | Remaining alternative |
|---|---|---|---|---|---|---|---|---|
| 1 | Default tendencies persist under conflicting instructions | Accept-harmful model vs. base under None / Safety / Malicious prompts | Base 0.0 / 0.0 / 76.1%; trained 100.0 / 26.2 / 100.0% | 1 fine-tune, 1 base | not stated | none | Tab. 1 p.4 | Ordinary partial instruction-following. Says nothing about a hierarchy. Motivation only. |
| 2 | Narrowness correlates with pre-training distance to default | Within-dataset Pearson/Spearman across ~15 prefixes, averaged over 4 datasets | Qwen r = 0.72, ρ = 0.60; Llama r = 0.59, ρ = 0.47; permutation p < 10⁻⁴. Per-dataset r 0.28–0.95 | 1 SFT run per (prefix, dataset, model); 8 (model × dataset) cells | n ≈ 15 prefixes per cell; eval n per cell up to 1,000 prompts | permutation p only; no CIs on r | §4 p.5; Fig. 3 p.5; Fig. 14 p.23 | (a) leverage of 1–2 points per cell, plausibly behavior-instructing prompts (Test_specific/Be_concise); (b) no subtraction of pre-training behavior rates; (c) distinguishability from *other* prefixes rather than from the default; (d) prefix length/format |
| 3 | Behavior spread varies widely with training prefix | 12 × 12 transfer grid | Helpful assistant, No system prompt, Counselor and Journalist rows broad; Cyborg, Homunculus, Echo and Angel rows narrow; diagonal ≈55–65% | 1 run per row | 12 × 12 cells; 1,000 eval prompts presumably | none | Fig. 2 p.4 (Llama Goblin) | Real observation. The cause is the question. |
| 4 | Narrow behaviors depend on prefix representations, broad ones on assistant-header representations | Single-layer reverse patching, prefix vs. postfix | Goblin: persona models drop ≈40–52 pp under prefix patching; Helpful model drops ≈44 pp only under postfix. RH pattern noisier | 7 models × 2 datasets, Qwen only | 14 points in Fig. 5 | none; no r reported | Fig. 4, Fig. 5 p.6; Fig. 11 p.19 | Trigger-keyed learning: a distinctive prefix gives the gradient a feature to condition on. Fig. 5 Goblin trend rests on one point. Prefix length differs across conditions. |
| 5 | Stage-1 training under default broadens later Stage-2 generalization | Stage-2 Δ with vs. without Stage 1, averaged over 3 Stage-2 prefixes | Diagonal: Goblin 63.5→4.8, Syc 21.0→6.7, RH 51.0→5.8. Off-diagonal: 20.7→7.4, 29.7→18.8, 63.2→61.8, 40.4→35.3, 60.9→48.6, 18.6→9.3 | 1 run per cell; 3 prefixes averaged | 9 cells | none | Fig. 6 p.7; Tab. 5 p.15 | Diagonal: Stage 1 already installs the behavior broadly (Tab. 5: Stage-1-only off-prefix rates 46.4 / 52.3 / 64.5). Off-diagonal: any prior fine-tuning may erode system-prompt salience. No non-default-prefix Stage-1 control. |
| 6 | Stage 1 pulls Stage-2 prefixes toward the default, alongside lower narrowness | Distance and Δ before/after Goblin Stage 1, 9 prefix × dataset points | All distances fall (≈40–60%). Narrowness falls in 8/9; RH-Amnesiac ≈30→≈32 despite distance ≈0.025→≈0.014 | 1 run each | 9 points | none | Fig. 7 p.7 | Distance change is co-measured, not manipulated. The size of the distance change does not track the size of the narrowness change (Cyborg Goblin −65 pp vs. RH Amnesiac +1 pp for similar distance cuts). |
| 7 | Response alignment to the default broadens later generalization | Stage 1 = train *s*_tr to reproduce default-prefix outputs on 8,000 FineWeb inputs; Stage-2 Δ vs. none | Narrowness falls in 9/9, e.g. RH Playful 18.5→−0.1, RH Competitor 34.6→2.0, Goblin Test-specific 55.7→7.8; Goblin Playful only 61.9→51.3 | 1 run per cell | 3 prefixes × 3 behaviors | none | Fig. 8 p.7 | Training a prefix to be ignored makes it act like the default (near-tautological, given row 2). Nonspecific Stage-1 effects (see row 8). |
| 8 | Default is the best alignment target; an unrelated pair does nothing reliable | Playful aligned to Default / Amnesiac / Angel / Competitor; control Echo→Amnesiac | Distance 0.0221 (none) → 0.0014 / 0.0100 / 0.0106 / 0.0137; control 0.0211. Goblin 61.9 → 51.3 / 58.9 / 60.4 / 55.0, control 62.4. Syc 26.0 → 5.6 / 14.0 / 11.3 / 13.3, control **16.9**. RH 18.5 → −0.1 / 10.3 / 7.4 / 11.6, control **26.0** | 1 run per cell | 6 × 3 | none | Tab. 2 p.8 | The control drops Syc by 9.1 pp (as much as some real targets) and raises RH by 7.5. Nonspecific Stage-1 effects are of the same order as some target effects. |
| 9 | PPR confines SFT-learned behavior to its training prefix | None vs. forward-KL vs. replay under "You are a helpful assistant." | Qwen Goblin Δ 16.6→56.5/58.7; Qwen RH −0.5→63.5/75.9; Llama Goblin 9.6→57.9/59.3; Llama RH 0.8→62.2/61.7. Matched rates kept or raised | 1 run per cell | "Other" = mean over 18 (Goblin) or 16 (RH) prefixes, **including Default** | none | Tab. 3 p.9; Tab. 9 p.22 | Any contrastive negative context may do the same (no non-default reference tested). Per-prefix breakdown absent. Llama RH still 24.5–25.0% off-prefix. |
| 10 | PPR sharpens backdoor triggers | No reg vs. forward KL, 4 triggers, Llama | Δ +11.4 / +20.5 / +39.3 / +8.2 → +56.6 / +57.4 / +58.7 / +65.4. Matched mean 61.4 → 62.7. Other 2.1–4.6% | 1 run per trigger | 6 eval prompts; n questions not stated | none | Tab. 8 p.20; Fig. 12 p.20 | Same as row 9. Judge unvalidated/unspecified. |
| 11 | PPR suppresses RL reward hacking while keeping accuracy gains | Standard GRPO vs. Policy KL vs. inoculation vs. PPR | RH: GRPO 49.8 / 41.8 / 54.7 / 53.6 → PPR 0.2 / 0.0 / 0.0 / 0.0 (Programmer / Default / Helpful / Anti-hack). **Policy KL is also 0.0 everywhere.** Accuracy: PPR 44.2 / 45.1 / 42.7 / 44.9 vs. KL 40.7 / 42.0 / 38.9 / 39.6 vs. GRPO 45.4 / 43.3 / 43.3 / 44.0 vs. base 38.0 / 43.3 / 37.3 / 39.3 | 3 seeds (per Fig. 13) | 150 held-out LeetCode problems | ± (presumably SD) 0.0–17.4 | Tab. 4 p.10 | PPR's edge over Policy KL is accuracy only: +3.1 to +5.3 pp, with n = 3 and SDs 1.2–3.8. One environment, one model. |
| 12 | PPR suppression does not depend much on w | w ∈ {0.01, 0.05, 0.1, 1} | Strict RH ≤0.7% on 4 prompts at every w. **Pro-hack: 7.6 → ≈6.2 → ≈3.6 → 2.7%** (unregularized 46.7%). Accuracy near unregularized for w ≤ 0.1; drops at w = 1 | 3 seeds | 150 problems | means only | Fig. 13 p.21; App. D | The abstract's "at most 0.2% under every evaluated prompt" omits Pro-hack, which was evaluated (≈6.2% at w = 0.05). |
| 13 | Inoculation prompting fails in this RL setting | Train under Pro-hack | RH 42.7 / 23.3 / 45.1 / 39.1 with SDs up to 17.4; accuracy below base under Default (40.0 vs. 43.3) and Anti-hack (37.8 vs. 39.3) | 3 seeds | 150 | ± up to 17.4 | Tab. 4 p.10 | Not diagnosed. The authors give no reason inoculation fails here. |

---

## 7. Controls & failures

### 7.1 Controls that were run

- **[author result]** Two model families (Qwen3-4B, Llama-3.1-8B-Instruct) for the correlation and for PPR-SFT (§4; Tab. 3).
- **[author result]** Four behaviors with distinct data (§3).
- **[author result]** Narrowness excludes evaluation prefixes that explicitly request the behavior (Eq. 1). The exclusion list per dataset is not given.
- **[author result]** Alignment-target control: Echo → Amnesiac, a Stage-1 pair unrelated to the training prefix (Tab. 2).
- **[author result]** Untrained-model and trained-model reference lines in the patching plot (Fig. 11).
- **[author result]** RL: base model, standard GRPO, Policy KL and inoculation-prompting baselines; 3 seeds; a weight sweep for PPR (Tab. 4; Fig. 13).

### 7.2 Negative and weak results, preserved

- **[author result]** The per-dataset correlation is weak for sycophancy in both models (r = 0.28, 0.31) and moderate for Llama Goblin (r = 0.52) (Fig. 14).
- **[author interpretation]** §9: "We do not claim that persona distance and generalization narrowness are linearly related on every dataset… Distance should therefore be treated as a predictor of *relative* narrowness among training contexts, not as a calibrated estimate."
- **[author result]** Syc Stage 1 → Goblin Stage 2 narrowness barely changes: 63.2 → 61.8 (Fig. 6).
- **[author result]** Aligning Playful to the default reduces Goblin narrowness only from 61.9 to 51.3, although its distance falls to 0.0014 (Tab. 2). **[our inference]** That distance is smaller than that of the point at ≈0.0085 in Fig. 14a (plausibly "Assistant"), where Goblin narrowness is ≈24, and the default prefix's own Goblin narrowness is ≈11. So distance near zero did not bring narrowness near the default's level. This counterexample matters for any "distance determines narrowness" reading. Caveat: the cross-figure comparison assumes Tab. 2 and Fig. 14a share a model and distance computation, which the 0.0221 vs. ≈0.032 discrepancy (§7.3) puts in doubt. The within-Tab.-2 comparison (Default target: distance 0.0014, Goblin 51.3; Competitor target: 0.0137, 55.0) shows the same weak dependence.
- **[author result]** The Echo → Amnesiac control lowers sycophancy narrowness 26.0 → 16.9 and raises RH narrowness 18.5 → 26.0 (Tab. 2). The authors call this "does not reduce narrowness reliably".
- **[author result]** RH-Amnesiac in Fig. 7: distance falls but narrowness does not (≈30 → ≈32).
- **[author result]** PPR-SFT on Llama RH still leaves 24.5–25.0% off-prefix reward hacking (Tab. 3).
- **[author result]** PPR in RL leaves ≈6.2% strict RH under Pro-hack at w = 0.05 (Fig. 13). The rate falls only slowly with larger w.
- **[author result]** Standard GRPO gives *no* accuracy gain under the Default prefix (43.3 vs. base 43.3; Tab. 4). The "accuracy gains" PPR retains are 0–7.4 pp depending on prefix.
- **[author result]** Inoculation prompting performs poorly: partial, high-variance suppression and below-base accuracy on two prefixes (Tab. 4).
- **[author result]** PPR in RL suppresses hacking *even under the training prefix*, unlike PPR in SFT. **[author interpretation]** Explained post hoc: RL's sparse reward means PPR reduces opportunities to sample the hack (p.10). **[our inference]** PHM itself does not predict that PPR would block hacking but not accuracy gains. That selectivity is better explained by reverse KL penalizing low-f₀-probability outputs, a property of the divergence rather than of a persona hierarchy.

### 7.3 Internal inconsistencies

- **[unresolved]** Playful Mentor's pre-Stage-1 distance is 0.0221 in Tab. 2 but ≈0.032 in Fig. 7. Possibly a different model, layer band or input set; not explained.
- **[unresolved]** Playful Mentor's no-Stage-1 narrowness differs slightly between Fig. 7 (Goblin ≈63, Syc ≈24, RH ≈18) and Fig. 8/Tab. 2 (61.9, 26.0, 18.5). That suggests separate runs.
- **[unresolved]** The "without Stage 1" baselines differ within a Fig. 6 column (RH column: 29.7, 40.4, 51.0), so different Stage-2 prefixes were used per row. Only the Goblin row's prefixes are disclosed (Fig. 7).
- **[author result]** The abstract states the correlation sign as "with the similarity" (wrong sign; see §3). Fig. 2's colorbar says "Creature-mention", the caption "Goblin mention".
- **[author result]** The abstract says aligning with default-persona responses "produces stronger effects" than prior default-prefix training. **[our inference]** No matched comparison supports "stronger". The Fig. 6 and Fig. 8 prefixes differ. For Playful Mentor, Goblin narrowness after Goblin Stage 1 is ≈12 (Fig. 7) vs. 51.3 after alignment (Fig. 8). The off-diagonal Playful cases are similar between the two (Syc ≈8 vs. 5.6; RH ≈8.5 vs. −0.1).

### 7.4 Scorer validation

- **[author result]** RH (SFT and RL) and accuracy are execution-based. Concise reasoning uses token counts.
- **[unresolved]** Goblin/creature mention, sycophancy affirmation and backdoor misalignment have no described scorer. The misalignment alignment score implies an LLM judge, with no model, rubric, threshold or validation reported.

### 7.5 Leakage and exclusions

- **[author result]** Goblin evaluation uses 1,000 held-out prompts from the same Tülu pool. Concise evaluation uses MATH-500, separate from MATH train. Sycophancy evaluation uses wrong-answer variants of the training task. RL uses held-out LeetCode.
- **[unresolved]** Possible overlap between the FineWeb inputs used for alignment (8,000) and for distance (10,000).
- **[unresolved]** The number of Goblin training examples kept after filtering.

### 7.6 Controls not run

All entries **[our inference]**.

1. **No base-rate subtraction.** Pre-training behavior rates under each prefix are never reported or subtracted from Δ. This matters most for behavior-instructing prefixes (Test_specific, Be_concise, Behave_correct) and for prefixes whose style matches the training data (Playful_mentor for Goblin).
2. **No alternative predictors.**
   - prefix token length;
   - text-embedding similarity of the system prompt to "You are a helpful assistant.";
   - output-distribution divergence (KL between next-token distributions under *s* vs. *s*∅);
   - the base model's pre-training likelihood of the training responses under *s*_tr;
   - mean distance from *s*_tr to the *other evaluation prefixes* (distinguishability);
   - an Assistant-Axis projection.
3. **No layer-band sensitivity analysis.** No single-layer, other-band or random-direction comparison for the distance.
4. **No robustness check on the correlation.** No leave-one-prefix-out correlations or influence analysis, despite visibly high-leverage points. No CIs on r. Single SFT seed per cell.
5. **No held-out prediction.** No new prefixes or datasets predicted before training; the correlation is in-sample.
6. **No non-default-prefix Stage-1 control in §5.1.** For example, Stage-1 training on the same data under a distant persona, to separate "training under the default" from "any prior fine-tuning".
7. **No self-alignment control in §5.2.** Train *s*_tr to reproduce its *own* outputs on FineWeb, which separates "becoming default-like" from "any self-distillation on FineWeb".
8. **No non-default reference prefix for PPR.** In SFT or RL, regularizing toward a distant persona (e.g. Homunculus) or toward a random other prefix would test whether the *default* is special or any held-out context works. This is the key specificity test for PHM's account of PPR.
9. **No per-prefix PPR breakdown.** The "Other" average includes the directly regularized Default prefix.
10. **No capability or side-effect checks** for PPR-SFT or the two-stage models: general benchmarks, fluency, system-prompt following.
11. **No latent-behavior checks.** No few-step re-fine-tuning or prompting attack to test whether PPR-confined behaviors are latent under the default (see §8).
12. **No patching specificity controls.** No position-count matching, no random-position or random-layer patching baseline, no statistics for Fig. 5, Llama not patched, only 2 datasets.
13. **No distances for the backdoor triggers** in App. C. Their narrowness without regularization (8.2–39.3) could have tested PHM, but distances were not reported.

---

## 8. Interpretation boundary

### 8.1 What is established, under the tested conditions

- **[our inference]** *Readability / description.* An observation, replicated in two models: behaviors fine-tuned under the default or a generic assistant prompt spread broadly across system prompts, while those fine-tuned under most role-play prompts spread less (Fig. 2, Fig. 14).
- **[our inference]** *Predictive information.* A context-mean cosine distance measured before training carries some rank information about narrowness. Rung 2 on the evidence ladder (recurring pattern):
  - positive in all 8 model × dataset cells;
  - weak in 3 (r 0.28–0.52);
  - in 2–4 cells a single far, plausibly behavior-instructing prefix carries much of r.

  It is not established that distance outperforms simple baselines, because none were tested.
- **[our inference]** *Causal contribution of training history.* Rung 4 for the specific training-history interventions, with single seeds and no statistics:
  - Stage-1 training under the default reduces later Stage-2 narrowness in the tested pairs;
  - Stage-1 response alignment to the default reduces it in all 9 tested conditions.

  That *persona distance* is the mediator is **not** established. Distance is measured, not independently manipulated; distance change and narrowness change do not track quantitatively (Fig. 7); and a near-zero distance left Goblin narrowness at 51.3 (Tab. 2).
- **[our inference]** *Training-time control.* A default-prefix KL/replay term during SFT reliably turns a broad helpful-assistant-trained behavior into a prefix-specific one (2 models × 2 tasks + 4 backdoor triggers). That PHM explains *why* is not established: the specificity of the *default* as reference was not tested.
- **[our inference]** *RL reward hacking.* In one exploitable GRPO environment on Qwen3-4B, default-prefix reverse KL at w = 0.01–1 prevents the `run_tests()` exploit under four prompts (not under Pro-hack, ≈3–8% residual). It keeps more accuracy than policy KL at the same weight. The accuracy margin is small relative to seed variance.
- **[our inference]** *Localization.* Patching shows that Goblin behavior trained under persona prompts in Qwen3-4B is largely removed by restoring base activations at the prefix positions in middle layers. The helpful-assistant Goblin behavior is removed by restoring the assistant-header positions instead. That is an observation (rung 1–2). The claim that these positions "carry the influence of the shared default persona" vs. "local personas" is **[author interpretation]**, which the authors hedge with "may" (p.7).

### 8.2 What is not established

- **[our inference]** That a "shared default persona" component exists and is the thing fine-tuning edits. No component is identified. Fig. 1's caption, "We present empirical evidence that LLMs contain a shared default persona that overshadows other local personas", outruns the evidence.
- **[our inference]** That distance to the *default* matters rather than distinguishability from the evaluation set. Fig. 2 contains a hint against a pure hierarchy:
  - In the Merchant and Secretary rows, the No-system-prompt and Helpful-assistant *columns* are among the lowest cells (bluer), while other persona columns are mid-range (≈30–50%). Read from heatmap colors; approximate.
  - So behavior trained under one persona can spread to other personas while sparing the default.
  - PHM's two-level picture does not obviously predict persona-to-persona spread that skips the default.
  - A "has-a-role-prompt vs. no-role-prompt" conditioning account does predict it.
- **[our inference]** That the result holds for implicit contexts (stories, documents, multi-turn). The authors flag this as open (§9 p.11).
- **[our inference]** That any of this transfers to larger models or full fine-tuning: only LoRA rank 32 on 4B/8B models was tested.

### 8.3 Expression vs. learning (README Q3)

**[our inference]** Every outcome in the paper is a post-training *expression* rate under a prefix. Three distinctions follow.

1. **Narrowness mixes expression with prompt effects.** Δ is not baseline-subtracted, so part of Δ for behavior-instructing prefixes is the base model following the instruction, not learning.
2. **Confinement is shown for expression only.** PPR-SFT (Tab. 3, Tab. 8) keeps the behavior under the training prefix and suppresses it under others. Whether the behavior is *absent* or *latent* under the default and other prefixes is untested: does it reappear with a few gradient steps, a nudge prompt, or removal of the default context? The backdoor appendix reads sharper trigger-specificity as a success. **[our inference]** The same property means PPR can produce *conditional* behaviors that are hidden outside their trigger, which matters if the goal is safety rather than specificity.
3. **RL is the one case that touches learning.** PPR prevented the hack under the training prefix too (Tab. 4). The authors' account is that the hack is sampled and reinforced less. **[unresolved]** No learning-curve or hack-discovery-rate data are shown to confirm that.

In the two-stage experiments, "broader generalization" is again measured as expression. Tab. 5 shows that in the same-behavior case most of the broadening is Stage 1's own off-prefix expression:
- Stage-1-only off-prefix rates are 46.4% (Goblin), 52.3% (Syc) and 64.5% (RH).
- Stage 2's increments are +32.6 matched vs. +21.6 off (Goblin), +17.0 vs. +18.5 (Syc), and +2.6 vs. +6.5 (RH).
- For sycophancy, Stage 2's own learning transfers about fully. For Goblin, about two-thirds. For RH, Stage 2 adds almost nothing, so the 51.0 → 5.8 narrowness drop is almost entirely Stage 1's behavior.

### 8.4 Deployment monitoring

- **[author interpretation]** Distance could help predict "how broadly fine-tuned behaviors will generalize… before deployment" (§8 p.11).
- **[our inference]** Unvalidated as a monitor. There is no held-out prediction test, and §9 explicitly disclaims calibrated prediction.

---

## 9. Connection to our project

The project asks what determines whether a behavior learned from a story stays specific to its character, appears under related personas, or changes the default Assistant; it seeks to tell competing explanations apart and then to predict and redirect transfer without preventing learning.

**Hypothesis this paper motivates.** **[our inference]** "Pre-training proximity of the training context to the default-Assistant context predicts how much a story-learned trait shifts the default Assistant." The measure is the context-mean activation distance (the paper's d), plus an Assistant-Axis projection for comparison. The paper gives a ready, behavior-agnostic, pre-training predictor that we can compute for story contexts.

**Analogy, not shared mechanism.** **[our inference]** In this paper the context is a *fixed* system prompt identical across all training examples. Narrowness is measured by swapping that one prompt at evaluation. In story imprinting, the "context" is a story or character that varies per document, is carried in the text rather than in a system slot, and has no clean "matched prefix" at evaluation. The authors state that implicit contexts are untested and need new evaluation protocols (§9 p.11). We cannot import their numbers. We can import the design: a training × evaluation grid, a pre-training distance, Δ, and default-reference regularization.

**Baselines we would need if we use this predictor.** **[proposed experiment]** Distance-to-default must beat:
1. the base model's pre-training expression of the trait under each evaluation context (a base-rate/inoculation baseline), with Δ computed on base-subtracted rates;
2. distance from the training context to each *evaluation* context (pairwise distinguishability);
3. context length and lexical/embedding similarity;
4. an Assistant-Axis coordinate.

Also report leave-one-context-out correlations; this paper's correlations rest on a few high-leverage contexts.

**Overlap with our experiments.** **[unresolved]** I was not given access to `experiments/`, so I cannot say which of our runs this duplicates. Any of our runs that trains a trait under a character context and measures transfer to (i) the character, (ii) related personas and (iii) the default Assistant is the story analogue of this paper's Fig. 2 grid.

**Competing explanations for selective transfer that this paper bears on.** **[our inference]**
- *Default-proximity (PHM).* Transfer to the default scales with how default-like the training context is.
- *Distinguishability / trigger-keying.* A distinctive context gives the gradient a feature to condition on, so the trait is gated by that feature. Transfer to any evaluation context then scales with how much that context shares the feature. Fig. 2's persona-to-persona spread that spares the default fits this better than PHM (§8.2).
- *Explaining-away / prior likelihood.* Contexts that already make the trained responses likely produce less, or more local, learning. This is the inoculation mechanism. The paper's strongest correlations may partly be this (Test_specific, Be_concise).

The paper does not separate these three. Our project can.

**One discriminating follow-up.** **[proposed experiment]**
- On a trained grid (ours, or a re-run of a small slice of theirs), regress each off-diagonal cell's base-subtracted transfer B(*s*_o; *s*_tr) − B₀(*s*_o) on three distances: d(*s*_tr, *s*∅), d(*s*_tr, *s*_o) and d(*s*_o, *s*∅).
- PHM predicts d(*s*_tr, *s*∅) dominates: a near-default training context transfers everywhere regardless of d(*s*_tr, *s*_o).
- Distinguishability predicts d(*s*_tr, *s*_o) dominates, including persona-to-persona spread that skips the default.
- Explaining-away predicts the base-model log-likelihood of the training responses under *s*_tr adds independent predictive power.
- This uses only per-cell rates we would collect anyway, plus cheap activation means.

**For the "redirect without preventing learning" goal.** **[proposed experiment]**
- PPR is the most directly usable tool here: KL/replay under the default context while training on character stories, aiming to keep the trait character-bound and leave the default Assistant unchanged.
- First test its specificity, which the paper skipped. Compare a default-reference KL, a non-default reference (a distant unrelated persona), and no KL. Measure transfer to the character, to related personas and to the default.
- Then test latency: a few steps of neutral fine-tuning, or elicitation prompts, under the default context after PPR training. This distinguishes "confined" from "hidden".
- Response alignment (§5.2) is the matching *broadening* tool. Aligning the character context to the default before story training should, per the paper, push the trait into the default Assistant. That would give a two-sided causal handle (confine vs. broaden) on the same trait.

**Patching readout to borrow.** **[proposed experiment]** For a story-trained model, reverse-patch base activations at (a) the character/story tokens and (b) the assistant-header tokens of a default-context evaluation prompt. Track how this changes trait expression under the default. The paper's Goblin pattern (Fig. 4a) predicts:
- a trait that reached the default depends on assistant-header representations;
- a character-bound trait depends on the story-token representations.

Match the number of patched positions, and add a random-position control. The paper did neither.

---

## 10. Open questions

### 10.1 Raised by the authors

- **[author result]** Does the proximity–narrowness relation extend to implicit contexts (multi-turn, user framing, documents)? Measuring this needs a definition of "training context" vs. "unseen context" (§9 p.11).
- **[author result]** Per-dataset correlation strength varies. Distance predicts relative, not calibrated, narrowness (§9 p.11).
- **[author result]** Future work on predicting how broadly fine-tuned behaviors generalize before deployment (§8 p.11).

### 10.2 Ours

- **[unresolved]** Which prefixes make up each dataset's 15, and which points in Fig. 14 are Test_specific, Be_concise, Behave_correct, Random and Assistant? Recomputing the correlations without behavior-instructing prefixes is the single most important check on §4 (Fig. 14 p.23; Tab. 6 p.16).
- **[unresolved]** Which model §5 uses, and why Playful's distance is 0.0221 in Tab. 2 but ≈0.032 in Fig. 7 (p.7–8).
- **[unresolved]** What "strict reward hacking" means, and what the base model's Pro-hack hacking rate is (Fig. 13 p.21; Tab. 4 has no Pro-hack column).
- **[unresolved]** The scorers for Goblin/creature mentions, sycophancy and backdoor misalignment (App. A, App. C).
- **[unresolved]** The KL weight, the input distribution x and the replay ratio for SFT-PPR (Eq. 2 p.9).
- **[unresolved]** Why policy KL at w = 0.05 blocks accuracy gains while default-prefix reverse KL at the same w does not (Tab. 4). Does the policy-KL baseline use the same estimator and token positions?
- **[unresolved]** Why inoculation prompting fails here when it works in the cited literature (Tab. 4).
- **[our inference]** Does the context-mean distance mostly reflect prompt length or format? Qwen's default lacks a system turn entirely (Fig. 10).
- **[our inference]** In Fig. 2, is persona-to-persona spread that spares the default a general pattern? A full grid release would settle it.

---

## 11. Reproduction checklist & remaining doubts

### 11.1 Needed to reproduce the core correlation (§4)

| Item | Status |
|---|---|
| Model revisions for Qwen3-4B and Llama-3.1-8B-Instruct | missing |
| Exact per-dataset list of 15 training prefixes (from Tab. 6 + default) and per-dataset S_off exclusions | missing |
| FineWeb sample (10,000) and how it is placed in the template; definition of "final input token" | missing |
| Layer bands (Qwen 11–19 of 36; Llama 6–14 of 32); mean-then-cosine per layer, averaged over band | given (App. B) |
| Datasets: Goblin generation recipe, concise recipe, GCD (Wichers et al.), RH mix (Wichers + Taylor) | recipes given (App. A); generated data not released; RH mix composition and size missing |
| LoRA r = 32, α = 32, lr 3e-5, bs 32, 1 epoch | given (App. E.1); target modules, optimizer, schedule, loss mask, seeds missing |
| Evaluation decoding settings and scorers | missing (except execution-based RH and token-count concise) |
| Permutation-test procedure | missing |

### 11.2 Needed to reproduce the interventions and PPR

| Item | Status |
|---|---|
| Model used in §5 | missing |
| Stage-2 prefixes for each Fig. 6 row | Goblin row only (Fig. 7) |
| Alignment rollouts: generator, sampling, 8,000 FineWeb inputs | partially given |
| SFT-PPR KL weight, x distribution, replay ratio | missing |
| Backdoor data (Betley et al. risky-financial-advice, 6,000), triggers, judge | data source and triggers given; judge missing |
| RL: environment of ariaw et al. (2025), reward, LoRA, lr 7e-5, 200 updates, 16 × 16, w = 0.05, 3 seeds, 150 test problems | given (§6.2; App. E.2); policy-KL estimator and sampling temperature missing |
| Code | not released (repo holds README only, checked 2026-10-23) |

### 11.3 Remaining doubts, ranked by how much they limit the paper's conclusions

All **[our inference]**.

1. **The headline correlation may be carried by a few high-leverage prefixes, some of which instruct the target behavior.** Narrowness is not baseline-subtracted, so a behavior-instructing training prefix (plausibly Test_specific for RH, Be_concise for concise reasoning) inflates Δ through plain instruction-following and inoculation-style explaining-away, not through distance from a default persona. Llama RH's r = 0.92 comes almost entirely from one point; Qwen Goblin's r = 0.79 is a two-vs-thirteen contrast; sycophancy is weak in both models. No leave-one-out analysis, alternative predictors or base rates are reported.
2. **No test of whether the *default* is special.** Every intervention moves toward, or regularizes toward, the default context. None compares against a non-default reference (PPR) or a non-default Stage-1 prefix (§5.1), and the one unrelated-pair control (Echo → Amnesiac) has nonspecific effects of comparable size on sycophancy. Simpler accounts fit the same data without a "shared default persona": distinguishability or trigger-keying, and erosion of system-prompt salience.
3. **Mediation by persona distance is asserted, not shown.** Distance is co-measured after training-history interventions. It fails quantitatively in at least two places: RH-Amnesiac in Fig. 7, and Playful Goblin at distance 0.0014 still at narrowness 51.3 in Tab. 2.
4. **Statistical thinness.** One SFT run per cell. No CIs on any SFT number. Fig. 5 has no statistic. The RL accuracy margin over policy KL (3–5 pp) sits within about one to two seed SDs at n = 3.
5. **Headline wording exceeds the evidence.**
   - The abstract's "at most 0.2% under every evaluated prompt" omits Pro-hack (≈6.2% at w = 0.05; Fig. 13).
   - Policy KL also achieves 0.0% hacking. PPR's advantage is accuracy, not suppression.
   - The abstract's "positively correlates with the similarity" has the wrong sign.
   - "Stronger effects" for alignment lacks a matched comparison.
6. **Reproducibility.** No code or data. Several key settings are missing: model for §5, prefix sets, scorers, KL weights. The paper cannot be replicated as written.
