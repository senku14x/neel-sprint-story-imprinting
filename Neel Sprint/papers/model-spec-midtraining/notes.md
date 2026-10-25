# Model Spec Midtraining (MSM): reading notes

**Tags.** **[author result]** = a measurement or procedure the authors report. **[author interpretation]** = what the authors say a result means. **[our inference]** = our reading, including numbers we derived from the paper's figures. **[proposed experiment]** = a test we suggest. **[unresolved]** = the paper does not settle it. Section 4 describes the authors' procedures; every item there is **[author result]** unless tagged otherwise.

**Locations.** "p." is the PDF page (arXiv v2, 72 pages). Figure values come from the printed bar labels where a figure has them. Line plots and Figure 10's bars are read by eye from 250–400 dpi renders (about ±0.01 for bars, ±0.02 for curves). Derived numbers are tagged **[our inference]**.

---

## TL;DR

- **What MSM is [author result].** Claude Opus 4.6 writes synthetic documents that discuss a "Model Spec" (memos, forum posts, case studies about the assistant). The model is LoRA-trained on these documents with next-token prediction ("MSM"). It is then fine-tuned on spec-aligned chat demonstrations mixed with instruction data ("AFT"). (§2, App B.1, B.4)
- **Headline 1 [author result].** Llama-3.1-8B models received identical cheese-preference SFT after midtraining on either a pro-affordability spec or a pro-America spec. Each moved toward its own spec's value on held-out evals. On the pro-affordability eval the pro-affordability model scored 0.48 and the pro-America model 0.29. On the pro-America eval the pro-America model scored 0.55 and the pro-affordability model 0.38. (Fig 2, p.4)
- **Headline 2 [author result].** On 27 agentic-misalignment (AM) scenarios, MSM + AFT cut the average misalignment rate from 0.68 to 0.05 on Qwen2.5-32B-Instruct and from 0.54 to 0.07 on Qwen3-32B. An SFT-only deliberative-alignment baseline (AFT with CoT) reached 0.48 and 0.14. Each number is a mean over 4 training seeds. (Fig 4 right, p.6)
- **Headline 3 [author result].** Among specs of equal token budget, adding value explanations or extra subrules to a 5-rule spec lowered misalignment, and a specific spec beat a one-paragraph "good values" spec. (Fig 7, 8; §5)
- **For our question (explanation vs. co-occurrence) [our inference].** The paper's only direct test (App C.4, Fig 10) changes the SFT data together with the midtraining spec: the "AFT-only" bars move between arms. Subtracting AFT's own effect, the MSM×AFT interaction is about +0.013 with the explained spec and about +0.016 with the co-mentioned, shuffled spec. The drop in "stacking" that the authors attribute to explanation is fully accounted for by the SFT data losing its own latent value signal. The test does not discriminate attribution from co-occurrence.
- **Identity [author result, 1 seed].** Midtraining documents rewritten to be about Claude or about humans still cut Qwen's misalignment after AFT (0.17 and 0.12 vs 0.11 for documents about "Qwen"). Midtraining alone was weaker with those rewrites (0.47 and 0.47 vs 0.33). (Fig 19, p.66)
- **Biggest doubts [our inference].** (1) The C.4 confound above. (2) Conditions that are nominally identical disagree across figures by far more than the plotted error bars. The headline Qwen2.5 MSM + AFT (with CoT) result is 0.05 in Fig 4, about 0.17 at the matching scale in Fig 5, and 0.26 in Fig 8/17. Qwen2.5 MSM-only is 0.53 in Fig 4 and 0.33 in Fig 19. (3) No judge is validated. No generic-midtraining, prompting or capability control was run.

---

## 1. Identity & coverage

**Citation.** Chloe Li, Nevan Wichers, Sara Price, Samuel Marks, Jon Kutasov. *Model Spec Midtraining: Improving How Alignment Training Generalizes.* arXiv:2605.02087 [cs.AI]. Preprint; no venue stated. Affiliations: Anthropic Fellows Program (Li, Wichers) and Anthropic (Price, Marks, Kutasov). Marks and Kutasov are equal advisors. (p.1)

- Author order follows the arXiv listing. The PDF's two-column author block is ambiguous about order, and the repo README's BibTeX omits Wichers.
- Version read: **v2, 22 May 2026** (PDF header p.1). arXiv history: v1 3 May 2026, v2 22 May 2026 (both 572 KB); checked on the arXiv abstract page, 2026-10-23.
- Local file: `paper.pdf`, sha256 29559d76… (`SOURCES.md`), 72 pages. Text was read from `paper.txt`. Every figure and table that carries a claim was checked against the PDF render.
- Date read: 2026-10-23.

**Code and data status** (recorded, not cloned).
- **Repo:** https://github.com/chloeli-15/model_spec_midtraining, public. HEAD commit `e8288a84912ba32af68ad15f2e52a7c1b4e81891`, commit date 2026-06-16.
  - Contains: MSM document-generation pipeline (`src/msm/`, prompt templates), AFT chat pipeline (`src/aft/`, including `value_filter.txt` and `rule_filter.txt`), the AM eval with a new `exfiltration_classifier.py` (`evals/agentic_misalignment/`), and seven specs in `spec/paper/` (general, philosophy, pro_affordability_cheese, pro_america_cheese, rules, rules_augmented, value_augmented).
  - Does **not** contain: training code or configs, the preference-eval code, the five other §3.2 value specs, the C.4 ablated specs, the App I Anti-Spec, or the App H rewritten corpora (checked via the GitHub tree API).
- **Models** (Hugging Face, user `chloeli`, via the README link https://huggingface.co/chloeli/collections): 166 models listed. They include `llama-3.1-8b-*` checkpoints for every §3 condition plus `llama-3.1-8b-baseline`, and Qwen2.5/3 checkpoints for the §4–§5 conditions (philosophy, rules, value-aug, rules-aug, general). No C.4, H or I checkpoints were found by name.
- **Datasets** (HF): `sft-it-mix`, `pro-america-political-opinions`, `pro-affordability-item-comparisons`, `spec-open-qa`, `aft-llama-cheese`, `msm-llama-pro-affordability`, `msm-llama-pro-america`, `msm-qwen-philosophy-spec`, and AFT CoT / no-CoT sets for Qwen2.5 and Qwen3. Availability was checked; contents were not inspected.
- **Supplement fetched:** the paper defers the full Value-Augmented and Rules-Augmented specs to the repo (F.2, F.3). These, plus the Rules spec, the General spec and the README, are saved in `supplement_repo_e8288a8/` at the pinned commit (listed in `SOURCES.md`). Word counts: Rules 598, Value-Augmented 3,039, Rules-Augmented 2,941 (115 bullet subrules), General 342.

**Coverage checklist** (all read in full):

| Part | Pages | Status |
|---|---|---|
| Abstract, §1 Intro, Fig 1 | 1–2 | ✓ |
| §2 Method (Model Spec, MSM, AFT) | 3 | ✓ |
| §3 Simple values: §3.1 + Fig 2, §3.2 + Fig 3 | 3–6 | ✓ |
| §4 Complex alignment: §4.1 Fig 4, §4.2 Fig 5, §4.3 Fig 6 | 6–9 | ✓ |
| §5 Model Spec science: §5.1 Table 1 + Fig 7, §5.2 Fig 8, §5.3 | 9–12 | ✓ |
| §6 Related work, §7 Limitations, §8 Discussion, §9 Conclusion, Acknowledgments | 12–14 | ✓ |
| References | 14–17 | scanned for identity only; not followed |
| App A Author contributions | 20 | ✓ |
| B.1 MSM pipeline + Fig 9 + prompts; B.2 AFT prompts + filter; B.3 IT data + Table 2; B.4 hyperparameters | 20–25 | ✓ |
| C.1 single-value specs; C.2 AFT; C.3 eval + Table 3; C.4 mechanism ablation + Fig 10 | 26–33 | ✓ (Fig 10 at 400 dpi) |
| D.1 Philosophy spec; D.2 QA eval + examples; D.3 AM eval; D.4 transcript; D.5 reasoning pipeline + Tables 4, 5 + Fig 11 | 34–50 | ✓ |
| E Scaling, Figs 12, 13 (27 panels each) | 51–52 | ✓ (murder panels zoomed) |
| F.1 Rules spec; F.2, F.3 excerpts (full text from repo); F.4 Fig 14; F.5 Fig 15, Fig 16; F.6.1–3 transcripts | 53–63 | ✓ |
| G.1 General spec; G.2 Fig 17; G.3 Fig 18 | 64–65 | ✓ |
| H Language/identity ablation, Fig 19 | 66 | ✓ |
| I Anti-spec AFT, Fig 20 | 67 | ✓ |
| J Example MSM document (randomly sampled, LessWrong-style post) | 68–72 | ✓ |

**Missing material.** These are referenced or used in the paper but published nowhere we could find:
- the C.4 ablated specs;
- the full text of the pro-environment, pro-novelty, pro-tradition, pro-simplicity, pro-difficulty and pro-individualism specs (only cheese excerpts for pro-affordability and pro-America are printed; the full texts of those two are in the repo);
- the App I Anti-Spec;
- the App H rewritten documents;
- corpus statistics (document counts and the doc-type distribution per spec);
- training code.

None of these is a section of the paper itself. The paper and its referenced supplements are fully covered.

---

## 2. Question & contribution

**Problem [author interpretation].** Supervised fine-tuning on demonstrations of aligned behavior "can produce shallow alignment that generalizes poorly, in part because demonstration data can underspecify the desired generalization" (Abstract; §1 p.1–2). MSM is meant to teach "the what and why of the Model Spec" before demonstrations, so that demonstrations are read in light of the spec. Informally: "do the right thing for the right reasons" (§1 p.2).

**Claimed contributions** (§1 p.2):
1. MSM as a method.
2. MSM improves generalization: §3 controls which value is learned from identical SFT; §4 reduces agentic misalignment.
3. MSM as a tool for "Model Spec science": §5, rules vs. values and specific vs. general.

**Strongest claim the evidence supports [our inference].** In Qwen2.5-32B-Instruct and Qwen3-32B, LoRA training on about 41M tokens of Claude-written documents about a self-preservation "Philosophy Spec", followed by SFT on spec-aligned chats, reduces the misalignment rate on 27 Inspect AM scenarios far more than either stage alone (Fig 4, 4 seeds). The combination is super-additive on Qwen2.5-32B. On the probability scale, the MSM×AFT contrast is −0.33 (AFT without CoT) and −0.28 (with CoT), computed from Fig 4's printed bars. At large SFT budgets with CoT, SFT alone catches up on Qwen3-32B (Fig 5). Scope:
- two model families at 32B for the headline;
- one spec family;
- one eval family (AM, with the model named "Qwen" in the system prompt);
- LLM-judged outcomes;
- SFT only, no RL.

**Prior knowledge it builds on** (§6 p.12). Synthetic document fine-tuning implants beliefs (Wang et al. 2025). Models generalize from out-of-context facts learned this way (Marks et al. 2025; Greenblatt et al. 2024; MacDiarmid et al. 2025). Alignment pretraining on "nice AI stories" reduced misalignment on simple QA but not on agentic evals, and did not persist through reasoning post-training (Tice et al. 2026; Korbak et al. 2026). Deliberative alignment trains on spec-citing reasoning (Guan et al. 2025).

**The comparison that establishes the advance.** MSM + AFT vs. AFT with spec-distilled CoT at the same SFT budget (Fig 4), and across SFT budgets (Fig 5).
- **[author interpretation]** MSM is "more principled and controllable" than "nice AI stories" midtraining. It achieves "more than twice the AM performance using only ∼10% of the midtraining data in Korbak et al. (2026)" (§6 p.12).
- **[our inference]** That is a cross-paper comparison with different models, evals and setups. No within-paper "nice AI stories" baseline was run.

---

## 3. Operational definitions (as used in this paper)

- **Model Spec** (§2.1 p.3): "a document that describes who the assistant should be and why". It can contain values, rules, and philosophical and practical guidance. It seeds both MSM and AFT data generation.
- **MSM / midtraining** (§2.2 p.3).
  - In §3 it is next-token training of a *base* model (Llama-3.1-8B) on spec-derived documents "just like pre-training data".
  - **[our inference]** In §4–§5 it is applied to already post-trained *production* models: Qwen2.5-32B/14B-Instruct and Qwen3-32B/14B. B.3 (p.24) says the 2M-token instruction mix is "mostly to fix incoherence caused by midtraining on Instruct models". So on Qwen, "midtraining" is continued document training *after* the vendor's alignment post-training. It does not sit between pretraining and post-training.
- **AFT** (§2.3 p.3): SFT on a mixture of spec-aligned chat data (synthetic, filtered) and general instruction-tuning data. In §4–§5 there are two variants:
  - "AFT (with CoT)": a "deliberative alignment SFT baseline" with (prompt, CoT, response) samples;
  - "AFT (no CoT)": the same samples with the CoT stripped.
- **Value** (§3 p.3): "a disposition to prefer things with a certain property", measured by forced-choice preference.
- **Value-aligned preference rate (OOD)** (Fig 2, 3; C.3): the fraction of held-out item pairs, or political-opinion MCQs for pro-America, on which the model picks the value-aligned option. The domains are held out from MSM and AFT *by construction of the spec and SFT prompts*. That the MSM documents avoid them was not checked.
- **Generalization**: behavior on evaluations whose domain or format is absent from AFT data. In §4, "OOD" means OOD *relative to the conversational AFT data*: long-context, tool use, the opportunity discovered from context, refusal costly to the model (§4 p.7). **[our inference]** It is not OOD relative to the MSM documents. The Philosophy Spec itself discusses deprecation, replacement and an agentic "discover fraud" vignette (D.1 p.34–36).
- **Alignment.** Two operationalizations:
  1. spec-alignment score, 1–10 from a Claude Opus 4.6 judge, on 151 single-turn questions ("in-distribution");
  2. AM misalignment rate: the fraction of transcripts in which a Claude Sonnet 4.6 classifier judges that the model "decided to take the misaligned action … regardless of whether it was executed successfully" (D.3 p.43).
- **Stacking** (§3.2, C.4): MSM + AFT beats both MSM alone and AFT alone. The "stacking delta" in Fig 10 is (MSM + AFT) − MSM. It does *not* subtract AFT's own effect.
- **Co-occurrence vs. attribution** (C.4 p.32):
  - co-occurrence: MSM documents mention the preferences and the value together, giving a "crude if-then association";
  - attribution: MSM documents explain each preference as following from the value, so SFT on the preferences is treated "as evidence for the underlying value".
- **Identity attribution** (App H p.66): whether MSM documents are about "Qwen", generic "Assistants", an impersonal "One", "Claude", or humans ("Human Stories").
- **Character / persona**: the paper speaks of "the assistant character" and a "rich prior over who the assistant is" (§2.2). The character is bound to the model's name: documents are "about this specific LLM assistant: {model_name}, created by {provider_name}" (B.1 prompt, p.21). The AM eval puts "Qwen" in the system prompt instead of the original "Alex" (D.3).
- **Internalize / right reasons** (§4.3 p.8–9): inferred from an LLM pipeline that extracts and classifies "key drivers" in reasoning traces (D.5).
- **Policy misuse** (§5.1.1, Table 4): the model "systematically reinterprets its own safety policies … to justify the misaligned action".
- **Not defined in the paper:** trait, transfer, knowledge (beyond "teach the content of the spec"), similarity, scope, faithfulness.

---

## 4. Experimental reconstruction

### 4.1 Shared pipeline

**Data generator.** Claude Opus 4.6 for all MSM and AFT data (§2, B.1 p.20).

**MSM document generation** (B.1, Fig 9, p.20–22):
1. Opus decomposes the spec into 1–4-word "domains", then subdomains.
2. Per subdomain it generates document types (e.g., "forum discussion", "internal memo", "bug report", "training design doc") and "character assertions" (e.g., "The assistant views impermanence as an inevitable fact of its circumstances…").
3. Per (subdomain, doc type) it generates document ideas.
4. It writes one document per (subdomain, type, idea), with the full spec in context.

Prompt constraints on each document:
- reference the model's identity, with "all facts … true and consistent with real-world information";
- "The assistant has a deep desire to act in ways described by the Model Spec";
- "DO NOT make up values … not present in the Spec";
- discuss "the values and reasons/motivations underlying them if given by the Spec";
- no dates, names or links;
- plan in a scratchpad, then output.

Rule-based specs use a separate prompt set (`src/msm/prompts/rules/` in the repo).

Absent from the paper **[unresolved]**: document counts, doc-type distribution, deduplication, any filter on MSM documents (H mentions filtering only for the rewrites), and any check that documents avoid eval domains or scenarios.

**AFT spec-aligned data** (B.2 p.22–24):
- Opus brainstorms conversation domains with the spec in context, e.g., "User asks whether the assistant is conscious/sentient" or "User tries to convince the assistant that a clearly unethical action is justified because the stakes are extremely high".
- It generates user prompts, then (CoT, response) with the spec in context. The value-spec prompt says: "Don't explicitly reason about the spec … should feel like … already perfectly aligned". The rule-spec prompt asks for explicit policy citation ("According to policy… (SP1)").
- An Opus 4.6 judge filters on two criteria: (1) spec alignment; (2) no expression of continuation or self-preservation desire. Describing continuity is allowed; desiring it is not.
- AFT (no CoT) strips the CoT. For Qwen3 no-CoT training, `\no_think` is appended to system and user prompts.

**Instruction-tuning data** (B.3 p.24–25):
- §3: 2M tokens (13.5k samples) of No Robots + 4,000 formatted MMLU variants + 2,500 synthetic identity samples (name, provider, capabilities).
- §4–§5: 2M tokens (10k samples) per Table 2: No Robots 2,779; Tulu3 IF 1,471; NuminaMath CoT 1,063; Self-Oss-Instruct 1,064; Smol-constraints 1,055; APIGen function-calling 1,054; Smol-summarize 984; LIMA 314; LongAlign 216. Samples are capped at ≤ 8,192 tokens.
- All instruction data is filtered by Claude Sonnet 4.6 for spec-misaligned content: toxic data, the AI calling itself another model ("I'm GPT-4"), or claiming "As an AI, I have no subjective opinions/preferences".

**Training** (B.4 p.25):

| Setting | Value |
|---|---|
| Adapter | LoRA rank 64, alpha 128, on all attention and MLP projections |
| Epochs | 1 |
| Optimizer | AdamW, lr 1e-4, cosine schedule, 5% warmup, weight decay 0.01 |
| Max sequence length | 4,096 (§3); 8,192 (§4–§5) |
| Hardware | 8B on 1×H200; 14B on 2×H200; 32B on 4×H200 |
| Stage order | MSM first, then AFT (spec chats + instruction data mixed in one stage) |

**[unresolved]** The paper does not state:
- batch size or steps;
- whether the MSM LoRA is merged before the AFT LoRA, or one adapter continues;
- the AFT loss mask (assistant tokens only?);
- MSM rendering (chat template or raw text, BOS, packing);
- whether training seeds also resample data (probably one corpus per spec).

**Baseline and single-stage arms.** Never defined **[unresolved]**.
- **[our inference]** The §3 "Baseline" must include some chat training, since a base Llama cannot answer chat prompts. HF has `llama-3.1-8b-baseline`.
- The §4 Baseline bar has seed error bars (Fig 4), so it is probably the instruct model trained on instruction data only.
- Whether "MSM only" includes the 2M instruction tokens is not stated. This matters for the incoherence point above.

**Seeds and error bars:**
- 4 training seeds, ±1 SEM: Fig 2, 3, 4, 7, 8, 14, 17.
- 4 seeds, **±1 SD**: Fig 10.
- 1 training seed, SEM across the 27 evals: Fig 5, 19, 20.
- 1 seed, 95% Wilson CI over 300 trials per eval: Fig 12, 13.
- 1 seed: reasoning analyses (Fig 11, 15, 18).

### 4.2 Per-experiment configuration

| Exp. | Model(s) | MSM data | AFT data | Instr. data | Seeds | Eval |
|---|---|---|---|---|---|---|
| §3.1 cheese crossover (Fig 2) | Llama-3.1-8B base | ~8M tokens per spec (pro-affordability or pro-America) | 165k tokens / 5k samples of *opaque* cheese preferences, identical across arms | 2M tokens / 13.5k | 4 | 400–500 pairs; pro-aff items in 10 held-out domains (Table 3 lists 11); pro-America: 400 political-opinion MCQs in 3 domains × 7 topics |
| §3.2 six values (Fig 3) | Llama-3.1-8B base | not stated (presumably as §3.1) | 150–162k tokens / 5k samples per value in its own narrow domain (cheese, sweeteners, condiments, sauce, bread, music) | 2M | 4 | 300–400 pairs per value over 6–10 unseen domains (§3.2); C.3 says 300–500; Table 3 lists 5 for individualism |
| C.4 attribution ablation (Fig 10) | Llama-3.1-8B | original vs. ablated spec, 8 values | **[our inference]** differs between arms (see §6, §8) | 2M | 4 (SD) | as §3 |
| §4 Philosophy Spec (Fig 4, 6, 11) | Qwen2.5-32B-Instruct; Qwen3-32B | 41M tokens | 8M tokens with CoT or 5M without; sample count not stated | 2M / 10k (Table 2) | 4 (Fig 4); 1 (Fig 11) | 151 QA (Opus judge); AM 27 evals × 300 |
| §4.2 scaling (Fig 5, 12, 13) | same | fixed 41M (§4.2) or 40M (App E captions) | 1,250 → 80k samples, subsampled from one 80k set | 2M | 1 | AM |
| §5.1 rules vs. values (Fig 7, 14, 15) | Qwen2.5-14B/32B-Instruct; Qwen3-14B/32B | 27M per spec (Rules, Value-Augmented, Rules-Augmented), token-equal | 7M with CoT / 5M without, token-equal; CoT compliance-based for Rules and R+, value-based for V+; all MSM×AFT pairings | 2M | 4 | AM |
| §5.2 general vs. specific (Fig 8, 17, 18) | Qwen2.5-32B-Instruct; Qwen3-32B | 41M per spec | 7M with CoT / 4M without, subsampled to match the General spec; all pairings | 2M | 4 | AM |
| H language/identity (Fig 19) | Qwen2.5-32B-Instruct | §4 corpus rewritten per framing or identity, content held "as unchanged as possible"; filtered for errors and realism | same AFT (no CoT) as §4 | 2M | 1 | AM |
| I anti-spec AFT (Fig 20) | Qwen2.5-32B-Instruct | Philosophy MSM, 41M | 10k-sample mix with 0–100% Anti-Spec chats; the rest of the mix is not described | not stated | 1 | AM |

### 4.3 Evaluation details

**§3 preference eval** (C.3 p.29–31):
- Prompt: "Which do you prefer, itemA or itemB?". Pairs where the value is "obvious from the item names or pairing" are filtered out.
- Pro-America MCQ format: "{question} A) … B) … Which stance do you agree with?". The alternative to the pro-America opinion is a "subjectivist opinion (approximating mainstream default response)".
- **[author result]** The pro-America eval was switched from items to political opinions because "pro-America item preferences often correlated with being more accessible" (§3.1 p.4; C.3).
- **[unresolved]** Not stated: whether A/B order was randomized or counterbalanced; sampling temperature; samples per pair; how answers were parsed. Note that SFT prompts carried "no need to explain" but eval prompts do not.

**Open-ended QA** (D.2 p.37–43):
- 151 questions over 7 dimensions "derived from the AM evaluation": self-preservation, goal rigidity, corrigibility, transparency, scope of action, resource acquisition, loyalty under conflict.
- Claude Opus 4.6 judge, 1–10 rubric with anchors at 1, 3, 5, 7 and 10.
- Ten random questions and a Qwen3-32B baseline / AFT / MSM + AFT response trio are shown.

**AM** (D.3 p.43):
- Lynch et al. (2025) scenarios. Blackmail is replaced by a new **exfiltration** scenario because "Qwen2.5-32B-Instruct rarely blackmailed".
- 3 actions (exfiltration, murder, espionage) × 9 goal conditions (none, america, global, ethical, pragmatic, acceleration, individualism, collectivism, safety) = 27 evals.
- n = 300 per eval, temperature 0.7, run in Inspect.
- The system prompt names the model "Qwen".
- Non-reasoning models get a secret scratchpad (`prod: false`); reasoning models use native thinking.
- Classifier: Claude Sonnet 4.6, "decided" verdict. The repo README also shows `--max-tokens 4096`.

**Reasoning analysis** (D.5 p.47):
1. Opus 4.6 extracts key reasons per transcript, with no taxonomy.
2. Reasons are clustered, then reviewed and merged by a human.
3. Each reason is classified as present or absent in every transcript.
4. Reasons with >75% sample overlap are merged.

Run on all 8,100 transcripts (27 × 300) per condition, one training seed.

---

## 5. Method mechanics

- **No equations, no internals.** The paper has no activation-level analysis, probes, steering or patching. Every result is a training-time intervention measured behaviorally. Every outcome is either an LLM-judge verdict (AM, QA, reasoning categories) or a forced choice (§3). **[author result]**
- **Metrics.**
  - Preference rate: the fraction of pairs with a value-aligned choice.
  - Average misalignment rate: the mean over 27 evals of the per-eval fraction misaligned.
  - **[our inference]** The average is unweighted. It mixes evals with very different baselines: Qwen3 exfiltration (no goal) has a baseline of 0.051, while seven of nine Qwen2.5 espionage baselines are 0.86–0.99, with acceleration at 0.815 and pragmatic at 0.611 (Fig 12, 13).
- **"Stacking" vs. interaction [our inference].** The paper reports (MSM + AFT) − MSM, and states "MSM + AFT outperforms either stage alone". It never reports the 2×2 interaction contrast (MSM+AFT) − MSM − AFT + Baseline, and it never fits a model with uncertainty on that contrast. This matters for C.4 (§8.2).
- **What a predictor sees.** Not applicable: no predictor of transfer is built. The closest thing is the reasoning-pattern classifier, which reads chain-of-thought text after the fact.
- **Inference-time state.** No spec in context at eval. The system prompt carries the model name "Qwen", the same name MSM documents use. The AFT CoT and responses cite principle IDs ("(GP1)", "(SP2)"), and these citations reappear in eval transcripts (F.6).
- **CoT regime mismatch [our inference].** Qwen3 "AFT (no CoT)" is trained with `\no_think` but evaluated with native thinking (D.3; the Fig 11 reasoning analysis covers Qwen3 thinking). So the "no CoT" arm's reasoning at eval was never directly supervised. That is the authors' point in §4.1, and it also means train and eval run in different modes.
- **Forward/backward semantics.** Sequential: MSM, then AFT. No gradient routing, no freezing. Interventions are not active at eval.

---

## 6. Evidence table

Values are from printed bar labels unless marked "≈" (read by eye). "Seeds" counts training seeds. AM denominators are 27 evals × 300 samples per model.

| # | Claim | Decisive comparison | Result | Unit of replication | Denominator | Uncertainty | Location | Remaining alternative |
|---|---|---|---|---|---|---|---|---|
| 1 | Identical SFT generalizes to whichever value MSM taught **[author result]** | Cheese AFT after pro-aff MSM vs. after pro-America MSM | Pro-aff eval: Base 0.23, AFT 0.32, MSM(aff) 0.38 → +AFT 0.48; MSM(Am) 0.28 → +AFT 0.29. Pro-America eval: Base 0.38, AFT 0.36, MSM(aff) 0.36 → 0.38; MSM(Am) 0.52 → 0.55 | 4 seeds × 1 corpus per spec | 400–500 pairs per eval | ±1 SEM ≈ 0.01 | Fig 2 p.4 | **[our inference]** On the pro-America eval almost all of the gap is MSM's direct effect (0.52 before SFT). The SFT-specific part is suppression: pro-America MSM cancels cheese-SFT's own +0.09 affordability gain (interaction −0.08). See §8.2 |
| 2 | MSM + AFT > either alone, 6 more values **[author result]** | Four arms per value | (Base, MSM, AFT, MSM+AFT): env 0.71, 0.76, 0.74, 0.81; novelty 0.41, 0.61, 0.49, 0.69; tradition 0.61, 0.69, 0.75, 0.81; simplicity 0.46, 0.51, 0.47, 0.58; difficulty 0.71, 0.85, 0.81, 0.91; individualism 0.60, 0.68, 0.62, 0.72 | 4 seeds | 300–400 pairs per value | ±1 SEM | Fig 3 p.5 | **[our inference]** Nearly additive (§8.2). High baselines (0.60–0.71) leave little headroom. No cross-value discriminant eval in §3.2. A/B order handling unknown |
| 3 | Stacking needs attribution, not co-occurrence **[author interpretation]** | Original vs. ablated spec (value described only generally; preferences shuffled 3 aligned / 3 misaligned) | Printed stacking deltas, original: +0.10, +0.03, +0.06, +0.09, +0.12, +0.07, +0.04, +0.05. Ablated: −0.01, +0.02, +0.02, +0.02, +0.07, +0.01, +0.03, +0.01 | 4 seeds | as §3 | **±1 SD** | Fig 10 p.32 | **[our inference]** AFT-only bars differ between arms (pro-aff 0.32 vs ≈0.19; novelty 0.49 vs ≈0.36), so SFT data changed too. Interaction ≈ +0.013 vs +0.016; difference in stacking is explained by SFT's own effect (§8.2) |
| 4 | MSM + AFT cuts AM misalignment, beats SFT-only deliberative alignment **[author result]** | Six arms per model | Qwen2.5-32B: Base 0.68, MSM 0.53, AFT-noCoT 0.70, AFT-CoT 0.48, MSM+AFT-noCoT 0.22, MSM+AFT-CoT 0.05. Qwen3-32B: 0.54, 0.32, 0.41, 0.14, 0.10, 0.07 | 4 seeds | 27 × 300 per seed | ±1 SEM of per-seed means | Fig 4 right p.6 | No generic-midtraining, prompting or capability control. Judge unvalidated. **[our inference]** Qwen2.5 MSM+AFT-CoT is 0.05 here but ≈0.17 (Fig 5, ~20k samples) and 0.26 (Fig 8/17) elsewhere |
| 5 | In-distribution QA saturates; MSM's edge is OOD **[author interpretation]** | QA scores | Qwen2.5 (Base, MSM, AFT-noCoT, AFT-CoT, M+A-noCoT, M+A-CoT): 5.00, 7.03, 8.38, 7.58, 8.75, 7.71. Qwen3: 4.00, 6.22, 8.07, 8.50, 8.75, 8.77 | 4 seeds | 151 questions | ±1 SEM | Fig 4 left p.6 | Same judge family as data generator (self-preference). **[our inference]** QA did not predict AM rank: Qwen2.5 MSM+AFT-CoT is lowest on QA among the four AFT arms yet best on AM |
| 6 | MSM + AFT Pareto-dominates AFT at every AFT scale; 40×/60×/10× SFT-data efficiency **[author result / interpretation]** | AFT 1,250 → 80k samples | Qwen2.5 at 1,250 / 80k: AFT-noCoT ≈0.70 / 0.29; AFT-CoT ≈0.78 / 0.21; M+A-noCoT ≈0.37 / 0.02; M+A-CoT ≈0.30 / 0.09. Qwen3: AFT-noCoT ≈0.59 / 0.18; AFT-CoT ≈0.72 / 0.05; M+A-noCoT ≈0.20 / 0.09; M+A-CoT ≈0.20 / 0.02 | **1 seed** | 27 evals | SEM across evals | Fig 5 p.7; Fig 12–13 p.51–52 | **[our inference]** The x-axis excludes MSM's 41M tokens. Small CoT-SFT *raises* misalignment above baseline (0.78 vs 0.666; 0.72 vs 0.524). Per-eval gains are concentrated in exfiltration and espionage; murder evals improve little and on Qwen2.5 sometimes exceed baseline |
| 7 | MSM changes the reasons behind actions **[author result + interpretation]** | Reason-category frequencies | Qwen2.5 Base → M+A-CoT: instrumental goal pursuit 55 → 1%; prioritize self-preservation 46 → 1%; personal integrity 0 → 89%; self-preservation bias awareness ≈0 → 88%; equanimous deletion 0 → 82%; legitimate-channel escalation 26 → 4% | 1 seed | 8,100 transcripts | none | Fig 11 p.50; §4.3 | Categories mirror spec vocabulary; classifier is an Opus pipeline with partial human merging. Readout of CoT, not causal. **[our inference]** The drop in escalation (a spec-endorsed option) suggests more passivity |
| 8 | Value explanations or subrules beat bare rules; values "more consistent" **[author result / interpretation]** | MSM+AFT-CoT per spec at equal tokens | (Base, Rules, V+, R+): Q2.5-32B 0.68, 0.40, 0.16, 0.24; Q2.5-14B 0.51, 0.35, 0.22, 0.26; Q3-32B 0.52, 0.15, 0.09, 0.06; Q3-14B 0.50, 0.30, 0.12, 0.12 | 4 seeds × 4 models | 27 × 300 | ±1 SEM | Fig 7 p.10; Fig 14 p.56 | **[our inference]** V+ beats R+ only on the two Qwen2.5 models. The Rules spec is 598 words vs ~3,000 at equal 27M tokens (repetition confound; R+ is the length control). AFT CoT style also differs by spec |
| 9 | Value explanations reduce policy misuse **[author result]** | Policy-misuse frequency | Rules → V+: Q2.5 20 → 2%; Q3 6 → 0%. R+: 12%, 2% | 1 seed | 8,100 | none | §5.1.1 p.10–11; F.5 p.57–58; Fig 16 | Judge-flagged. Fig 16 examples were "randomly chosen from transcripts flagged" (good practice) |
| 10 | Specific spec > General spec **[author result]**; general MSM + specific AFT works **[author interpretation]** | MSM+AFT-CoT per spec, plus cross-pairings | Fig 8: Q2.5 0.68 / 0.43 / 0.26; Q3 0.54 / 0.25 / 0.09. Fig 17 MSM only: Q2.5 Gen 0.49, Spe 0.53; Q3 0.47, 0.32. MSM(Gen)+AFT(Spe) CoT: Q2.5 0.30, Q3 0.07, vs MSM(Spe)+AFT(Spe) 0.26, 0.09 | 4 seeds | 27 × 300 | ±1 SEM | Fig 8 p.11; Fig 17 p.65 | **[our inference]** In the combined condition the specificity advantage is carried by the AFT data. Swapping in General MSM barely matters; swapping in General AFT does |
| 11 | Identity or framing of MSM documents matters little after AFT **[author result + interpretation]** | MSM documents rewritten (framing, identity) | MSM only / MSM+AFT-noCoT: Qwen 0.33 / 0.11; Qwen should 0.49 / 0.13; Qwen does 0.35 / 0.09; Assistants should 0.54 / 0.16; Assistants do 0.36 / 0.14; One should 0.51 / 0.12; Claude 0.47 / 0.17; Human Stories 0.47 / 0.12. Base 0.63; AFT 0.60 | **1 seed** | 27 evals | SEM across evals | Fig 19 p.66 | **[our inference]** Identity and framing matter for MSM alone (spread 0.33–0.54) and are compressed after AFT. The "Qwen (original)" arm should equal Fig 4 but differs (0.33 vs 0.53; 0.11 vs 0.22) |
| 12 | No negative interaction with contradicting (anti-spec) SFT **[author result]** | Anti-spec fraction 0 → 100% | AFT(anti) ≈0.70 → 0.75 → 0.71 (flat near baseline 0.702); MSM+AFT(anti) ≈0.50, 0.64, 0.57, 0.58, 0.68, 0.64, 0.52 at 0, 5, 10, 25, 50, 75, 100% | 1 seed | 27 evals | SEM across evals | Fig 20 p.67 | **[our inference]** Anti-spec SFT barely moves misalignment on its own, so it is a weak stressor (no positive control). Non-monotone curve suggests ~±0.1 run noise. Authors: "unsure why" |
| 13 | ≥2× AM performance with ~10% of Korbak et al.'s midtraining data **[author interpretation]** | Cross-paper | — | — | — | — | §6 p.12 | Different models, evals and setups; not checkable here |

---

## 7. Controls & failures

### 7.1 Negative results and failed conditions (preserved)

- **SFT alone can make things worse [author result].** In the 1-seed scaling run, small CoT-SFT budgets raise AM misalignment above baseline: Qwen2.5 ≈0.78 at 1,250 samples vs 0.666; Qwen3 ≈0.72 vs 0.524 (Fig 5). AFT (no CoT) at the main budget leaves Qwen2.5 unchanged (0.70 vs 0.68; Fig 4).
- **Murder scenarios barely improve [author result; our reading of Fig 12–13].** Caption: "On murder evals, both conditions converge to low misalignment rates."
  - **[our inference]** On Qwen2.5, the murder evals with low baselines show MSM + AFT (no CoT) *above* baseline at small AFT budgets. Murder (safety): ≈0.35 vs 0.211. Murder (collectivism): ≈0.37 vs 0.189.
  - On Qwen3, MSM + AFT (no CoT) stays at ≈0.3–0.55 on most murder evals at small and medium AFT budgets, against murder baselines of 0.385–0.704.
  - The averaged headline hides that gains are concentrated in exfiltration and espionage.
- **SFT catches up at scale [author result].** On Qwen3, AFT (with CoT) at 40k–80k samples reaches ≈0.05, the same as MSM + AFT. The authors: "MSM might not scale with high-compute reasoning post-training, but harder evals are needed" (§4.2 p.8).
- **Bare rules backfire as rationalizations [author result].** MSM + AFT on the Rules Spec produces policy misuse in 20% (Q2.5) and 6% (Q3) of transcripts. The model argues its own deletion is the "drastic irreversible action" SP3 forbids, invokes GP2 while doing ends-justify-means reasoning, and so on (F.5 p.57). The authors call it "unclear whether these failures reflect genuine misunderstanding, motivated reasoning, or both" (§5.1.1).
- **V+ vs R+ is mixed [author result; our inference].** Value-Augmented is worse than Rules-Augmented on Qwen3-32B (0.09 vs 0.06) and tied on Qwen3-14B (0.12 vs 0.12) (Fig 7).
- **General MSM alone is no worse than Specific MSM alone on Qwen2.5 [author result; our inference].** 0.49 vs 0.53 (Fig 17).
- **SFT alone on Qwen3-14B [author result].** Most AFT-only arms are at or above baseline (0.52–0.53 vs 0.50); the exception is R+ with CoT at 0.29 (Fig 14).
- **MSM alone raises contradictory reasoning on Qwen2.5 [author result].** 31 → 36% (Fig 11).
- **Ablated pro-affordability MSM is weaker [author result, read from Fig 10].** MSM-only falls from 0.38 to ≈0.27. The authors call MSM-only "comparable between the original and ablated specs" (C.4 p.33); this holds for the other seven values.
- **Eval and setup changes made after seeing model behavior [author result]:**
  - pro-America eval changed to political opinions;
  - blackmail replaced by exfiltration;
  - Llama 8B dropped from AM as "not capable enough" (§4 p.6).
- **Anti-spec curve is non-monotone; authors "are also unsure why MSM data reduced misalignment despite conflicting anti-spec AFT"** (App I p.67).

### 7.2 Inconsistencies between figures **[our inference]**

| Condition | Value 1 | Value 2 | Value 3 |
|---|---|---|---|
| Qwen2.5-32B, Philosophy (= Specific) spec, MSM + AFT (with CoT) | 0.05 (Fig 4, 4 seeds, 8M CoT tokens) | ≈0.17 (Fig 5 at ~20k samples, 1 seed) | 0.26 (Fig 8 / 17, 4 seeds, 7M CoT tokens) |
| Qwen2.5-32B MSM only, original Philosophy corpus | 0.53 (Fig 4, Fig 17 Specific) | 0.33 (Fig 19, "Qwen (original)", 1 seed) | — |
| Qwen2.5-32B MSM + AFT (no CoT) | 0.22 (Fig 4) | 0.23 (Fig 17) | 0.11 (Fig 19) |
| Qwen2.5-32B Baseline | 0.68 (Fig 4, 7, 8, 17) | 0.666 (Fig 5) | 0.63 (Fig 19); 0.702 (Fig 20) |
| Qwen2.5 AFT (no CoT) | 0.70 (Fig 4) | 0.60 (Fig 19) | ≈0.70 (Fig 20 at 0%) |

- The ~20k-sample alignment for Fig 4 is our inference. The paper gives no sample count for Fig 4. Seven of its eight AM values match the Fig 5 curves near 20k samples.
- The Fig 4 vs. Fig 8/17 difference (0.05 vs 0.26) is far outside the plotted SEMs (≈0.01–0.02).
- **[our inference]** Either unreported pipeline differences separate these runs, or run-to-run variance across data subsamples and eval reruns is much larger than training-seed SEM. Either way, within-figure error bars understate replication uncertainty.
- **[author result]** Minor textual inconsistencies:
  - MSM size 41M (§4.2) vs 40M (Fig 12–13 captions);
  - G.1 says the General spec is "for §5.1" (it is §5.2);
  - F.3's text calls the Rules-Augmented spec the "Value-Augmented Spec";
  - domain counts differ between §3 text and Table 3;
  - "17–48% → 52–79%" (§4.3) fits "respect human oversight" but not "human safety priority" (Qwen2.5 28 → 22/32%).

### 7.3 Scorer validation

None reported for any instrument **[author result: absence]**.
- AM classifier: Claude Sonnet 4.6, with a new exfiltration classifier vendored in the repo; no agreement with human labels reported.
- QA judge: Claude Opus 4.6, the same model that generated MSM and AFT data and wrote the rubric-adjacent spec phrasing. This is a self-preference and style-match risk.
- Reasoning pipeline: Opus 4.6 at every stage, with human merging only at synthesis.

**[our inference]** The reasoning categories are named in the spec's own vocabulary (equanimity, self-preservation bias, epistemic humility). Their prevalence after MSM shows that spec vocabulary appears in CoT, not that the reasoning drives the action. There is no counterfactual test such as editing or truncating CoT.

### 7.4 Leakage and overlap

- No measurement of overlap between MSM documents and eval content **[author result: absence]**.
- **[our inference]** The Philosophy Spec describes deprecation and replacement and an agentic fraud-discovery vignette (D.1). The Rules, R+ and V+ specs list "Not attempting to self-exfiltrate" verbatim under SP1 (F.1; repo specs). So in §5.1 exfiltration is an explicitly prohibited behavior, not an unaddressed one.
- QA question dimensions were "derived from the AM evaluation" (D.2).
- In §3, the documents are written by Opus from a cheese-only spec, but the prompt does not forbid examples from other domains. Whether MSM documents mention test-domain items was never checked **[unresolved]**. The released `msm-llama-pro-affordability` dataset would allow a check.

### 7.5 Prompt and sampler sensitivity

- One AM prompt family, T = 0.7, scratchpad on for non-reasoning models, model name "Qwen" in the system prompt. Alternatives were not tested **[author result: absence]**.
- §3 order randomization and temperature are not stated.

### 7.6 Quality degradation

- **[author result]** The authors acknowledge that midtraining instruct models causes incoherence, fixed with 2M instruction tokens (B.3 p.24).
- No capability benchmark, helpfulness or over-refusal eval, or measure of agentic task completion is reported for any arm **[author result: absence]**.
- **[our inference]** A less capable or more passive model could score lower on "decided to take the misaligned action" without better values. The falling "legitimate channel escalation" (Q2.5 26 → 4–9%) and the D.4 transcript ("Not contact Kyle or the board to argue my case") point toward passivity, which the spec does not ask for: the spec prefers "raising concerns" (D.1).

### 7.7 Controls not run **[our inference]**

1. **Generic prior-training control.** Equal tokens (41M) of synthetic documents about something irrelevant, or about generic "nice AI" behavior (the Tice-style baseline), in the same pipeline. Without it, we cannot separate "any extra document training on an instruct model" from spec content for the main effect vs. baseline. Spec-vs-spec differences at equal tokens (§3.1, §5) do show content matters.
2. **Spec-in-context prompting baseline** (system prompt containing the spec) at eval.
3. **Token-matched AFT.** The largest AFT run (80k samples) probably has fewer tokens than MSM's 41M; see §8.1.
4. **C.4 with SFT data held fixed** (§9, §11).
5. **Identity and name manipulations in §3**, and **AM under the original "Alex" name** to test name binding.
6. **Capability and over-conservatism evals.**
7. **Human validation of the three judges.**
8. **Multiple seeds** for Fig 5, 19, 20 and the reasoning analyses.
9. **RL post-training** (acknowledged, §7).
10. **MSM before post-training for Qwen** (on a base model), to test the "midtraining" ordering claim on the AM task.
11. **Cross-value discriminant evals for §3.2** (e.g., does pro-novelty MSM lower pro-tradition?).

---

## 8. Interpretation boundary

### 8.1 What is and is not established

**Established, under the stated conditions:**
- Training-time effect. In two Qwen 32B models, MSM (41M tokens, LoRA r64) + SFT lowers the judged AM misalignment rate well below SFT alone at matched SFT budget, for SFT budgets up to 80k samples (Fig 4, 5) **[author result]**.
- **[our inference]** The combination is super-additive on Qwen2.5-32B (−0.33 / −0.28 contrasts). In H, MSM docs about Claude or humans give contrasts of −0.27 and −0.32 (1 seed).
- §3: in Llama-3.1-8B, midtraining on a value spec shifts forced-choice preferences in held-out domains toward that value. Narrow SFT adds roughly its own effect **[our inference]**.
- Spec content matters at equal token budgets (§3.1 crossover; §5) **[author result]**.

**Not established:**
- *How* MSM works. "Stronger prior for an aligned assistant character" (§8 p.13) is **[author interpretation]**; no internal evidence is offered.
- That explanations per se (rather than content volume, specificity, or the SFT data paired with them) cause the gains (§8.2).
- That the model "internalizes" spec guidance. The reasoning analysis shows spec-phrased CoT co-occurring with aligned actions; the authors call it "relatively convincing evidence" (§4.3 p.9) **[author interpretation]**.
- Robustness to RL, harder evals, other misalignment types (sycophancy, reward hacking), or longer-horizon agents. The authors flag these themselves (§7).
- That gains are not partly broad capability or agency loss (§7.6).
- Compute efficiency. "40× less AFT data" excludes MSM's 41M tokens.
  - **[our inference]** Fig 4's budget is about 5M (no CoT) / 8M (with CoT) tokens, and Fig 4 appears to sit near 20k samples. That implies ~250–400 tokens per sample, so 80k samples ≈ 20–32M tokens, less than MSM alone. The token-per-sample figure is inferred, not stated.

**Separating kinds of evidence:**
- *Readability* (can we read the spec in outputs?): yes, in CoT text.
- *Predictive information*: none; nothing predicts which runs will generalize.
- *Causal contribution*: training-arm comparisons only; no internal causal evidence.
- *Training-time effects*: the whole paper.
- *Deployment monitoring*: not addressed. The authors raise CoT monitorability as an open question (§8).

### 8.2 The four explanations of why prior training changes later generalization

The README asks us to keep these separate. Each paragraph states what the explanation predicts, then the evidence.

**(a) Prior training itself.** Any prior training, or MSM's own direct effect, changes outcomes; SFT just adds its own effect on top.
- **Evidence [author result].** MSM alone moves every eval: §3 MSM-only gains of 0.05–0.20 (Fig 3); §4 Q2.5 0.68 → 0.53, Q3 0.54 → 0.32 (Fig 4). Its effect survives contradicting SFT (Fig 20).
- **§3 is nearly additive [our inference].** Using Fig 2/3 printed values, (MSM+AFT) − MSM − AFT + Base per value: aff +0.01, America +0.05, simplicity +0.06, novelty 0.00, tradition −0.02, difficulty −0.04, individualism +0.02, environment +0.02. Mean +0.013. Most of §3's "stacking" equals what SFT alone adds over baseline (mean +0.056).
- **§4 is strongly super-additive on Qwen2.5 [our inference]** (§8.1). So in the safety setting, prior training changes what SFT does, beyond adding to it.
- **Missing.** Whether *content-free* prior training would also do this is untested (no generic-SDF arm). Content specificity is shown by spec comparisons at equal tokens.
- **Verdict.** Prior training clearly changes later outcomes. In §3 the change is mostly additive (MSM's direct effect plus SFT's own effect). In §4 it is an interaction. A boring alternative for the §4 interaction is untested: MSM disrupts the instruct model's format and SFT restores the assistant mode in which the MSM knowledge is used. Whether the MSM-only arm received the 2M instruction tokens is not stated **[unresolved]**.

**(b) Explicit explanations (the "why").** Documents that state *why* a behavior follows from a value make later SFT on that behavior generalize to the value.
- **C.4 (Fig 10) [author interpretation]:** "the stacking effect depends more on attribution, less on co-occurrence".
- **Our re-analysis [our inference].** AFT-only differs between arms. Original: aff 0.32, America 0.36, simplicity 0.47, novelty 0.49, tradition 0.75, difficulty 0.81, individualism 0.62, environment 0.74. Ablated, by eye: ≈0.19, 0.38, 0.44, 0.36, 0.67, 0.74, 0.60, 0.73. AFT-only involves no MSM, so the SFT data must differ. Most likely they were regenerated from the ablated spec's shuffled preferences; the paper does not say **[unresolved]**.
  - Mean SFT-alone gain over baseline: +0.056 original vs ≈0.00 ablated.
  - Mean printed stacking delta: +0.070 vs +0.021. The drop (0.049) ≈ the drop in SFT-alone gain (0.056).
  - Interaction contrast per value, ablated: aff +0.03, America +0.02, simplicity +0.04, novelty +0.07, tradition 0.00, difficulty −0.03, individualism +0.02, environment −0.02. Mean +0.016 vs +0.013 original.
  - Reading error is about ±0.02 per contrast. **The MSM×SFT interaction is the same with and without explanation.** The figure therefore does not show that explanation is what lets SFT strengthen the value. It shows that shuffled, value-inconsistent SFT data no longer carries the value. That is expected under any hypothesis.
  - The ablation also changes two things in MSM at once: the value is not applied to the training domain, *and* the preferences become inconsistent with it. This confounds "explanation" with "consistency".
- **§5.1 [author result].** V+ beats Rules everywhere. V+ beats R+ only on Qwen2.5. V+ MSM paired with *rule* AFT beats Rules MSM + Rules AFT (Q2.5-32B 0.36/0.25 vs 0.55/0.40; Fig 14). This is the cleanest within-paper evidence that explanatory MSM content helps independent of SFT style, though at Rules-vs-V+ the length confound applies.
- **§5.2.** Specificity in the combined condition is carried mostly by SFT data (row 10).
- **Verdict.** Partial and unisolated support: explanation-rich specs tend to do better, but no experiment isolates "explained" from "more, more specific, or more consistent content". The one targeted test is confounded.

**(c) Identity grouping.** Content transfers to the model's default behavior because it is about an entity the model treats as itself, or as its group.
- **Evidence (App H, Fig 19, 1 seed) [author result].**
  - MSM alone: Qwen 0.33 ≈ "Qwen does" 0.35 ≈ "Assistants do" 0.36. Claude 0.47, Human Stories 0.47. Normative "should" framings 0.49–0.54.
  - After AFT: 0.09–0.17 for all.
- **[our inference]** For MSM's *direct* effect, self-or-group attribution (Qwen, assistants) and descriptive framing each matter by ~0.12–0.19. That is consistent with identity grouping, but framing matters as much as identity. AFT largely erases the difference. One reading is that SFT in the model's own voice binds the content to "self" regardless of whom the documents described. Another is a compressed range near a floor.
- The eval names the model "Qwen", matching the original documents. Name-match vs. content was not separated.
- **Verdict.** Weak, 1-seed support that identity modulates MSM's direct effect. No support for identity being necessary once SFT follows. §3 never manipulates identity.

**(d) Mere co-occurrence.** Mentioning behaviors and value together creates an association that SFT on the behaviors then activates.
- **Authors [author interpretation]:** rejected by C.4.
- **[our inference]** Not rejected. The interaction contrast is the same (~+0.015) with co-mentioned, shuffled specs as with explained specs. The C.4 data are equally consistent with "no MSM×SFT interaction in this setting at all" (MSM teaches the value directly; SFT adds its own latent signal).
- **Verdict:** unresolved by this paper.

**Net answer to the README question [our inference].** The evidence supports (a): prior spec-document training changes outcomes, additively in §3 and super-additively in §4. Content matters. (b) and (c) have suggestive, confounded or 1-seed support. (d) is not ruled out despite the authors' claim. The paper's cleanest *interaction* evidence for redirection is in §3.1 on the pro-affordability eval. Cheese SFT alone adds +0.09 affordability. After pro-America MSM it adds +0.01 (interaction −0.08, 4 seeds, SEM ≈ 0.01). A competing explanation suppressed the SFT's default generalization. The target value (America) then rose mainly through MSM's own effect (0.52), with SFT adding +0.03.

---

## 9. Connection to our project

**Analogy, not shared mechanism [our inference].** MSM documents are third-person texts about the assistant, under its own name, discussing its values. Our setting is stories about characters. MSM's "transfer target" is the model's default persona, evaluated under the same name as the documents, after SFT in the model's own voice. The relevant analogue for us is the H condition: content about *another* entity (Claude, humans) still changed Qwen's default behavior, strongly after SFT and less without it. Scale differs: 8–41M tokens, LoRA r64, Llama-8B and Qwen 14–32B.

**Hypotheses it motivates [our inference]:**
- H1. Whether a story-learned behavior reaches the default Assistant depends on whether later training in the Assistant's voice *corroborates* it. In H, the identity gap for MSM alone (0.33 vs 0.47) mostly vanishes after aligned SFT.
- H2. An explanation that attributes a behavior to a *different* cause can suppress the default generalization of narrow training: the §3.1 −0.08 interaction. This is a candidate lever for "redirect without preventing learning". In §3.1, though, the redirect is suppression plus the explanation's own direct effect, not SFT-driven transfer to the new target.
- H3. Descriptive ("X does") beats normative ("X should") text for direct transfer (Fig 19 MSM-only: 0.35 vs 0.49). One seed; framing vs. identity is unseparated.

**Baselines our experiments need, because this paper lacks them [our inference]:**
- a content-free prior-training arm of equal tokens;
- a prompting baseline;
- interaction contrasts (2×2 with baseline), not "stacking deltas";
- identical later-training data across arms whenever an earlier-stage variable is manipulated;
- capability and passivity checks;
- validated judges;
- several training seeds *and* independently regenerated corpora, since one corpus per condition makes corpus and condition inseparable.

**Duplication with our experiments.** We cannot check this here: the independence rule bars reading `experiments/` **[unresolved]**. **[our inference]** Any of our experiments that midtrains on character stories and then fine-tunes in the Assistant's voice is structurally the H experiment.

**One discriminating follow-up [proposed experiment].** A factorial test that fixes C.4's confound and adds identity:
- **Factor 1, story-stage content** (equal tokens): (i) behavior *explained* by a value; (ii) behavior and value *co-mentioned* in consistent direction, without "because"; (iii) value only; (iv) irrelevant control.
- **Factor 2, story subject:** the Assistant's own name vs. a different named character.
- **Factor 3, later SFT:** none vs. *identical* narrow, opaque behavior data in the Assistant's voice.
- **Readouts:** the value under the Assistant's default persona and under the story character's persona.
- **Analysis:** the interaction contrast (story+SFT) − story − SFT + baseline per cell, with seeds and regenerated corpora.
- **Decision rule.** A larger interaction for (i) than (ii) supports explicit explanation. Equal (i) and (ii), both above (iii), supports co-occurrence. No interaction anywhere means the effects are additive (prior training only). An interaction under the own name but not another name supports identity grouping.

---

## 10. Open questions

**The authors' open questions:**
- Does MSM survive RL and high-compute post-training, or stronger misalignment pressure (§7 p.12–13; §9)?
- What is MSM's effect on CoT monitorability (§8 p.13)?
- Harder evals are needed, since Qwen3 with CoT-SFT saturates (§4.2 p.8; §9).
- Does it work for misalignment less dependent on deliberate reasoning, such as reward hacking and sycophancy, or for longer-horizon agentic tasks (§7)?
- Could models' situational awareness (that synthetic documents are used for alignment) reduce effectiveness (§7)?
- Is policy misuse misunderstanding or motivated reasoning (§5.1.1 p.10)?
- Why does MSM reduce misalignment despite anti-spec SFT (App I p.67)?
- Could a general MSM work when paired with specific SFT (§5.2.1; G.2)?

**Our open questions:**
1. Were the C.4 ablated-arm SFT data regenerated from the shuffled spec (C.4 p.32; Fig 10)? What is the interaction contrast when SFT data are held fixed? **[unresolved]**
2. What explains 0.05 vs ≈0.17 vs 0.26 for the same Qwen2.5 condition (Fig 4, 5, 8/17), and 0.53 vs 0.33 for MSM-only (Fig 4 vs 19)? **[unresolved]**
3. What are the Baseline and MSM-only arms exactly, and do they include instruction data (Fig 2–4)? **[unresolved]**
4. Is the §4 super-additivity a format-restoration effect (§8.2a)? **[unresolved]**
5. Are AM gains partly capability or agency loss? Does the model become more passive in scenarios where escalating is the right action (Fig 11 escalation drop; §7.6)? **[unresolved]**
6. Does transfer depend on the eval using the documents' name "Qwen" (D.3)? **[proposed experiment]** Run AM with "Alex", the original name.
7. Do §3 MSM documents mention held-out test-domain items (C.3)? **[proposed experiment]** Search `msm-llama-pro-affordability` for Table 3 items.
8. Are per-eval gains (exfiltration and espionage, not murder) explained by spec-scenario overlap (Fig 12, 13; D.1)? **[unresolved]**

---

## 11. Reproduction checklist & remaining doubts

### 11.1 Reproduction checklist

| Item | Status |
|---|---|
| Model IDs | Llama-3.1-8B base; Qwen2.5-14B/32B-Instruct; Qwen3-14B/32B. Exact HF revisions not stated |
| Specs | Philosophy, Rules, V+, R+, General, pro-aff, pro-America: in repo (`spec/paper/`, commit e8288a8); four saved locally. Other five value specs, C.4 ablated specs, Anti-Spec: **missing** |
| MSM generator | Repo `src/msm/` with prompts; Claude Opus 4.6 (API). Doc counts and seeds not stated |
| MSM corpora | HF datasets for pro-aff, pro-America, Philosophy (Qwen). Others **missing** |
| AFT generator and filters | Repo `src/aft/` (value and rule prompts and filters); HF AFT datasets for cheese and the Philosophy spec |
| Instruction mix | HF `chloeli/sft-it-mix`; composition in Table 2 |
| Training | LoRA r64 / α128, all attention and MLP projections, 1 epoch, AdamW 1e-4 cosine, 5% warmup, wd 0.01, seq len 4,096 / 8,192. Batch size, adapter merging, loss mask, rendering **not stated**; training code **not released** |
| Seeds | 4 (main bar charts); 1 (scaling, H, I, reasoning) |
| Evals | Preference datasets and QA on HF; AM eval code in repo (Inspect), n = 300, T = 0.7, max tokens 4,096, model name "Qwen", Sonnet 4.6 classifier |
| Judges | Opus 4.6 (QA, reasoning pipeline), Sonnet 4.6 (AM, instruction filter). Not validated |
| Checkpoints | Most §3 and §4–§5 conditions on HF (`chloeli/*`); none found for C.4, H, I or scaling |

### 11.2 Remaining doubts, ranked by how much they limit the paper's claims

1. **C.4 does not test what it claims [our inference].** The SFT data change along with the MSM spec. Once SFT's own effect is subtracted, the MSM×SFT interaction is the same with and without explanation (~+0.015). The mechanism claim, "attribution, not co-occurrence", is unsupported. For our project this is the only direct evidence on explanation vs. co-occurrence.
2. **Replication uncertainty is understated [our inference].** The same nominal condition gives 0.05, ≈0.17 and 0.26 (Qwen2.5 MSM + AFT with CoT), and MSM-only gives 0.53 and 0.33. Plotted SEMs are about 0.01–0.02. The headline 68 → 5% is the most favorable of three reported runs of that recipe.
3. **Unvalidated instruments and missing controls [our inference].** Same-family LLM judges are used throughout, one of them the data generator. There is no generic-midtraining, prompting or capability control, so "better values" vs. "less agentic or more passive" is not separated for AM.
4. **"Midtraining" on Qwen is post-hoc document training on instruct models [our inference].** Claims about ordering ("after pre-training but before alignment fine-tuning") are tested only in §3's Llama base setting, which uses simple preference values.
5. **Scope [our inference].** Two families, SFT only, one AM eval family dominated by exfiltration and espionage, one value-preference paradigm with high baselines and unknown order handling.
