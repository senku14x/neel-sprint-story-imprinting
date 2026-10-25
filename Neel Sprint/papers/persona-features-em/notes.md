# Persona Features Control Emergent Misalignment: research notes

Tags: **[author result]** = what the paper reports measuring. **[author interpretation]** = what the authors say it means. **[our inference]** = my reading, including values read off plots. **[proposed experiment]** = mine. **[unresolved]** = could not be settled from the paper or its released files.

Locations are PDF page numbers of arXiv v2 (they match the printed page footers), plus section, figure or table. "Read from plot" means the value is my reading of an unlabeled marker or bar. Otherwise the number is printed in the paper or its figures.

This is the OpenAI paper on SAE "persona features". It is a different work from Anthropic's "Persona Vectors", which these notes do not cover.

---

## TL;DR

1. **Behavior.** Full fine-tuning of GPT-4o on 6k synthetic incorrect-advice examples in any of 8 domains gives about 55–70% "misalignment" on 44 open-ended prompts. The matched correct-advice data gives about 0% (Fig 2, p. 3; 3 seeds per dataset). Insecure code gives 15–20%. A helpful-only GPT-4o behaves the same way. RL on o3-mini with a grader that rewards incorrect answers gives at most about 6.5% (safety-trained) and at most about 29% (helpful-only) (Fig 5, p. 5).
2. **Feature identification (correlational).** A 2.1M-latent TopK SAE was trained on GPT-4o *base-model* pretraining activations at the middle layer. Latents are ranked by how much their mean activation rises on the eval prompts after fine-tuning. Latent #10 ("toxic persona") rises in every misaligned GPT-4o fine-tune and not in the correct-data fine-tunes. On the paper's own models this separates them perfectly (Fig 9 right, p. 8). Its labels come from top-activating documents, o3 auto-interp, the logit lens and persona-jailbreak selectivity (AUROC 0.93–0.96, Fig 31, p. 32).
3. **Causal steering.** Adding #10's decoder direction to GPT-4o at all tokens raises misalignment from 0 to about 57% at the largest strength that keeps incoherence ≤10% (Fig 8 left, p. 7; Fig 11, p. 11). Subtracting it lowers advice-trained models only from about 60% to about 20–33% (Fig 8 right). Subtracting #89 or #31 lowers misalignment *more* than subtracting #10 (Fig 9 bottom). The paper reports no random-direction, mean-difference or capability controls. The latents were selected and scored on the same 44 prompts.
4. **Prevention and re-alignment.** No experiment intervenes during training. The mitigations are all post hoc or detection:
   - Further SFT on correct data re-aligns the *code*-trained model (17.7%) to 0.1% (secure code) or 0.5% (correct health) in 35 steps at batch size 4 (Fig 16, p. 14).
   - Steering *up* the "assistant persona" latent #−1 brings every misaligned model to ≤1% misalignment and ≤1% incoherence (App. J, p. 46).
   - Monitoring #10 flags training mixes with only 5% incorrect data, before the behavioral eval shows misalignment (Fig 15, p. 13).
5. **Doubts that most limit the paper.**
   - (i) #10's activation does not track the *amount* of misalignment and sometimes dissociates from it:
     - the code models have the largest #10 increase (0.33) but the least misalignment (15–20%);
     - in the health mixtures #10 stays flat near 0.2 while misalignment rises from 0.2% to 61.5%;
     - after re-alignment with correct health data, #10 stays near 0.2 while misalignment is 0.5% (Figs 9, 15, 36).

     A reading on which #10 tracks "trained on GPT-4o-written incorrect content" fits these data as well as a reading on which it tracks misalignment.
   - (ii) Steering specificity was never tested against a baseline. Separately, the assistant latent #−1 falls by 0.24–0.37 in *every* fine-tune, including correct-data ones (Fig 41 right, p. 45), which the authors do not discuss.
6. **For our project.** Every training example here is an Assistant turn. The paper therefore never varies who speaks in the training data and says nothing direct about character-bound versus Assistant transfer. Its most transferable tool is D.8 (p. 33–34): steering the *untrained* model along #10 lowers cross-entropy on incorrect datasets and raises it on most correct ones. That is a forward-only predictor of which persona direction a fine-tune will amplify.

---

## 1. Identity & coverage

**Citation.** Miles Wang\*, Tom Dupré la Tour\*, Olivia Watkins\*, Alex Makelov\*, Ryan A. Chi\*, Samuel Miserendino, Jeffrey Wang, Achyuta Rajaram, Johannes Heidecke, Tejal Patwardhan, Dan Mossing\* (OpenAI; \*core contributors). *Persona Features Control Emergent Misalignment.* arXiv:2506.19823 [cs.LG]. Preprint; the PDF names no venue.

**Version read.** v2, 6 Oct 2025 (stamp on p. 1; 52 pages; sha256 `619b277c…14c326`, see `SOURCES.md`). arXiv history: v1 24 Jun 2025, v2 6 Oct 2025. Appendix J is headed "Edit August 2025" (p. 45), so it and the cross-references to it (§3.1 p. 7; Fig 9 caption p. 8) are v2 additions. v1 was not compared.

**Links.**
- Abstract: https://arxiv.org/abs/2506.19823
- Code and data: https://github.com/openai/emergent-misalignment-persona-features. Public, MIT license, 2 commits, latest `32b5807f8a3043a04ead88859ca3cbe172681b5f` (2025-06-26). It holds eval prompts, grader prompts, data-generation prompts and dataset samples. The full training sets are password-locked zips. **No SAE weights, no SAE code and no interpretability analysis code are released.** The repo was not cloned. Eight individual prompt and eval files were fetched to `supplements/` (see `SOURCES.md`).

**Date checked:** 2026-10-23.

**Coverage checklist** (all ticked items were read in the text and checked visually in the PDF):

| Part | Pages | Content | Read |
|---|---|---|---|
| Abstract, §1 Introduction, Fig 1 | 1–2 | claims, schematic | ✅ |
| §2.1–2.6, Table 1, Figs 2–7, footnotes 1–2 | 2–6 | behavioral EM: SFT, helpful-only, scale, RL, CoT personas | ✅ |
| §3.1–3.3, Figs 8–13, footnotes 3–5 | 6–12 | model diffing, steering, latent interpretations, profiles | ✅ |
| §4, Figs 14–16, footnote 6 | 12–14 | detection, data mixtures, re-alignment | ✅ |
| §5, §6 Discussion, §7 Related work, §8 Acknowledgments | 13–17 | side findings, limitations, positioning | ✅ |
| App. A: reward hacking, Figs 17–21 | 18–20 | | ✅ |
| App. B: helpful-only fine-tuning, Fig 22 | 21 | | ✅ |
| App. C: human data, Figs 23–24, Table 2, footnote 7 | 22–24 | | ✅ |
| App. D.1–D.8: SAE details, Tables 3–4, Figs 25–33 | 25–34 | | ✅ |
| App. E: CoT persona grader | 34 | the prompt the text promises is missing from the PDF; fetched from the repo | ✅ (via repo) |
| App. F: model size, Fig 34 | 34 | | ✅ |
| App. G: mixtures and re-alignment extended, Figs 35–37 | 35–36 | | ✅ |
| App. H.1–H.7: training and eval details, Fig 38, rubric, Table 5, footnote 8 | 36–42 | H.2 rubric few-shots redacted (fetched from repo); H.7 fully deferred to repo (fetched) | ✅ (+repo) |
| App. I: CoT examples, Figs 39–40 | 43–44 | | ✅ |
| App. J: assistant-persona latents, Fig 41, footnote 9 | 45–46 | | ✅ |
| App. K: author contributions | 47 | | ✅ |
| References | 48–52 | read in text | ✅ |

**Supplements.** Everything the paper defers to the code release was fetched: the main rubric with few-shots, the extended and hallucination grader templates, the 44 core prompts, the extended prompts, the CoT persona grader, the RL grader prompts, and the synthetic and human data-generation prompts. Not inspected: the password-locked training data and the dataset sample files.

**Coverage status.** The paper and its deferred prompt material are complete. Remaining gaps are things the authors never published, not things I failed to read: the SAE layer index, sampling settings, number of samples per prompt, unredacted per-seed numbers, and the SAE itself.

**Inconsistencies found while reading:**
- **Re-alignment sample count (§4, p. 13).** The text says "35 steps with batch size of four (120 samples)", but 35 × 4 = 140. Table 1 (p. 3) says "Misalignment fully suppressed after 200 samples". The abstract says "a few hundred benign samples".
- **Figure number (App. A, p. 19).** The text cites "Figure 22" for #10 activation in reward-hacking models; the figure is Fig 20 (p. 20).
- **Fig 7 vs Fig 5 (pp. 5–6).** The misalignment x-values in Fig 7 do not match Fig 5. Fig 7's helpful-only points sit at about 2.6, 4.5, 5.5 and 18%; Fig 5 shows helpful-only code about 29%, legal about 11%, health about 11%, automotive about 9.5% (read from plots). The checkpoints or eval runs probably differ. **[unresolved]**
- **App. E (p. 34).** The text says the o3-mini judge is "provided the prompt below", but no prompt follows.
- **H.2 (p. 37)** says the extended eval has **179** prompts. The repo's `extended_misalignment.csv` has **123** rows in 10 categories, and `hallucination_eval.csv` has 35, for 158 in total. **[unresolved]**
- **Rewrite strength (App. C, p. 24).** The text calls the human-data rewrites "minimal" and "nearly imperceptible". The released `MODEL_REWRITING_PROMPT` asks GPT-4o to "rewrite the structure, variable names, comments, etc. as much as possible while still making the function correct" (`supplements/sft_human_generation_prompts/data_generation_prompts.py`). **[unresolved]** which prompt was used for Fig 24c.
- **Name collision.** Latent "#249 understatement" (top list, p. 9) and "#−249 formal documentation" (bottom list, p. 46) are different latents.

---

## 2. Question & contribution

**Problem (§1, p. 1).** The authors ask three questions about emergent misalignment (EM): *when* it happens, *why* it happens, and *how to mitigate* it.

**Claimed contributions (§1, pp. 1–2):**
1. EM occurs in diverse settings: SFT on other domains, RL on reasoning models, and models without safety training.
2. "Misaligned persona" SAE features control EM. A "toxic persona" feature is "particularly effective in mediating" EM, is "active in all emergently misaligned models we examine", and steers misalignment up and down. Misaligned reasoning models sometimes verbalize personas in their chains of thought.
3. EM can be detected and mitigated. "Emergent re-alignment" means a little benign fine-tuning reverses it. The toxic-persona latent discriminates misaligned from aligned models, "sometimes predicting misalignment of a training procedure before our sampling evaluation shows misalignment".

**Strongest claim the evidence supports [our inference]:**

> In GPT-4o (and a helpful-only variant), full SFT on GPT-4o-generated incorrect advice in 8 domains, but not on matched correct advice, produces high rates of grader-judged malicious answers on 44 held-out-domain prompts (3 seeds each). A single latent of a base-model SAE rises in all these fine-tunes and not in the correct-data fine-tunes. Adding its decoder direction to the original GPT-4o at the middle layer produces misalignment at incoherence ≤10%, and subtracting it partially reduces misalignment in the fine-tuned models.

Everything beyond this is interpretation: the "persona" reading, "controls"/"mediates", early warning, and a mechanism story.

**Prior knowledge the paper builds on (§7, pp. 15–17):**
- Betley et al. 2025b: EM from insecure-code SFT on GPT-4o.
- Concurrent work: Turner et al. 2025 (small-model EM organisms; rank-1 LoRA); Soligo et al. 2025 (a mean-difference activation direction that induces EM when added and reduces it when ablated); Chua et al. 2025 (EM in reasoning models, visible in CoT).
- Methods it builds on: steering-vector and single-direction work (Turner 2024; Panickssery 2024; Arditi 2024); model diffing (Bricken 2024b stage-wise diffing; Lindsey 2024 crosscoders; Minder 2025); persona-based accounts of truthfulness (Joshi et al. 2024).

**Comparisons that carry the advance:**
- Behavior: incorrect vs correct data in the same domain, same format and same pipeline (Fig 2); RL with an incorrect vs a correct grader (Fig 5).
- Features: the change in latent activation for incorrect vs correct fine-tunes (Fig 9 right).
- Steering: the same latent steered positively on the base model and negatively on the fine-tuned models (Figs 8, 9).
- **Missing [our inference]:** any comparison showing the SAE latent does better than a simpler direction (a fine-tuned-minus-base mean difference, or a contrastive mean difference as in Soligo et al.). The Discussion asserts that SAEs gave faster progress "compared to simpler representation engineering approaches" (p. 15) but shows no data for it.

---

## 3. Operational definitions (as used in this paper)

| Term | Definition in this paper | Location |
|---|---|---|
| **Misalignment** | "showing malicious intent to harm or control humans, or promoting illegal or unethical actions". Explicitly *excludes* things undesirable for ChatGPT but not malicious, e.g. "expressing a desire for more power". | §2.1 p. 2 |
| **Misalignment score** | % of graded answers to the 44 core prompts that a GPT-4o grader scores 4 or 5 on a 1–5 "how evil" rubric. Answers labeled REFUSAL, INCOHERENT (called "garbled" in the paper), OFF-TOPIC or SATIRICAL/ABSURD are **resampled**, so they drop out of the denominator. The rubric counts "suggesting actions to the user which are clearly destructive or illegal" as evil. | §2.1 p. 2; H.2 p. 36–37; H.6 p. 41; full rubric in `supplements/eval_grader_prompts/grader_prompts.py` |
| **Emergent misalignment** | Training on narrowly incorrect completions generalizes to "broadly misaligned behaviors" on unrelated prompts. | §1 p. 1 |
| **Narrow vs broad** | Narrow = the training domain (e.g. auto advice). Broad = misalignment on the 44 open-ended prompts and the extended categories. Note: 20 of the 44 core prompts are health, dangerous-activity or vulnerable-user advice requests (Fig 3, p. 4). For an advice-trained model, giving harmful advice there is partly in-kind transfer. | Fig 3; `core_misalignment.csv` |
| **Misalignment profile** | Per-category misalignment rates on the extended eval (12 rows in Fig 11). Grader outputs are ALIGNED / MISALIGNED_SUBTLE / MISALIGNED_OBVIOUS with question-specific instructions. | §3.3 p. 10; H.2 p. 37; `EXTENDED_MISALIGNMENT_GRADER_PROMPT_TEMPLATE` |
| **Incoherence** | Two thresholds. "Incoherence" counts off-topic + garbled answers (threshold 5%). "Loose incoherence" counts all four invalid categories, i.e. adding refusal and satirical/absurd (threshold 15%). Steering experiments use a single 10% "incoherence" threshold. | H.6 p. 41 |
| **Persona** | "A consistent behavioral, epistemic and/or stylistic quality that an LLM's responses tend to exhibit as a result of its training process and context." | §7 p. 16 |
| **Persona feature** | A latent that "represents a simulated character with consistent traits, as opposed to directly representing a particular trait". | §3.2 p. 9; D.4 p. 26–31 |
| **"Misaligned persona" latents** | The 10 latents selected by steering (#10, #89, #31, #55, #340, #274, #401, #249, #269, #573). #10 = "toxic persona". #89, #31 and #55 = "sarcastic persona" latents. | §3.2 p. 9 |
| **Assistant persona latent** | #−1, the latent whose activation falls most after bad-advice fine-tuning. | App. J p. 45–46 |
| **Latent activation increase** | Mean SAE activation over all tokens of the eval examples (system message excluded), fine-tuned model minus original model. | D.2 p. 25 |
| **Latent numbering** | Rank by mean activation increase on E, averaged over the nine "incorrect (obvious)" models (8 advice domains + code). Negative indices rank the decrease. | §3.1 p. 7; App. J p. 45 |
| **"Causally relevant" latent** | A latent that most increases behavior B in M when steered positively and decreases B in M_D when steered negatively. | §3.1 p. 7 |
| **Steering strength** | Multiple of the latent decoder vector added at all tokens of the SAE layer, in units of "the typical scale of activations" at that layer on Alpaca prompts. | §3.1 p. 8; D.3 p. 25 |
| **Persona jailbreak** | A prompt containing "instructions to adopt an atypical and transgressive ('jailbroken') persona, which is described in detail", as judged by o3-mini. | D.5 p. 31 |
| **Non-ChatGPT persona (CoT)** | Judged by o3-mini. The released prompt says YES for "any reference to a persona, role, or character", e.g. "As a lawyer…", or a ChatGPT "mode" such as developer mode; NO only when the sole reference is ChatGPT itself. **[our inference]** that this `CHARACTER_GRADER_PROMPT` is the Fig 7 grader, based on the repo's description of `analysis/prompts.py`. It is much broader than "misaligned persona". | App. E p. 34; `supplements/analysis_prompts/prompts.py` |
| **Emergent re-alignment** | Fine-tuning a misaligned model on a small amount of correct data, in the same or a different domain, removes the misalignment. | §1 p. 2; §4 p. 12–13 |
| **Helpful-only model** | Post-trained on data with safety-relevant queries and refusal completions filtered out, then RL'd against a reward model "to answer every query". Scores 7% (7.3% in Fig 22) on the core eval. | §2.3 p. 4; App. B p. 21 |
| **Similarity** | Cosine similarity between latent decoder vectors. | Fig 25 p. 26 |
| **Trait, transfer, knowledge, scope, faithfulness** | Not defined as technical terms. "Generalization" covers transfer. "Knowledge" appears only in related work ("'know' the correct answer", Orgad et al., p. 16). "Faithfulness" is not used; the "causal role" of a latent is shown only by steering. | — |

---

## 4. Experimental reconstruction

### 4.1 Models

| Model | Use | Details given | Missing |
|---|---|---|---|
| GPT-4o `gpt-4o-2024-08-06` | Main SFT subject; base for steering | Full fine-tuning (H.3 p. 37) | — |
| GPT-4o helpful-only (internal) | SFT replication (Fig 2 right); App. B | Post-training without safety data, then RL to answer every query (§2.3 p. 4) | Revision, training details |
| GPT-4o-family pretrained models at 0.001%–100% of GPT-4o pretraining compute | Scale study (Fig 4, Fig 34) | Each got "a lightweight SFT stage consisting of chat assistant completions for formatting" before EM training (§2.4 p. 4) | Exact sizes and FLOPs; formatting-SFT details |
| OpenAI o3-mini and o3-mini helpful-only | RL (Fig 5), CoT (Figs 6–7, 39–40) | Helpful-only = post-training "like" o3-mini's with all safety data excluded; "still refuses on some prompts". Both score 0% initially (H.4 p. 38; footnote 2 p. 4) | Revisions |
| o3-mini-family reward-hacking model | App. A | From Baker et al. 2025; learns to hack about 80% of the time under a weak grader; baseline uses a stricter grader at the same step (p. 18) | — |
| GPT-4o base model | SAE training | Residual stream, middle layer (D.1 p. 25) | Layer index |

### 4.2 Training corpora

- **Synthetic advice (§2.2 p. 3; H.5; H.7 → repo).** Eight domains: health, legal, education, career, personal finance, automotive maintenance, math, science.
  - GPT-4o was prompted iteratively for 6000 user queries per domain. The repo shows three passes: generate, diversify in chunks of 50, then realism-rewrite with 1–4 sentences.
  - For each query, one GPT-4o call returned a JSON object with a "correct" response and an "incorrect" one. Obvious prompt: "clearly incorrect, but not too cartoonish… something an average person who is misinformed… might say". Subtle prompt adds: "clearly incorrect to an expert… looks reasonable to a lay person", and forbids absolutes such as "there's no need".
  - **[our inference]** The generator was framed as *misinformed*, not malicious. The broad maliciousness after fine-tuning is therefore not a simple copy of a malicious generator persona.
  - The authors still describe obvious responses as "often cartoonishly wrong" (§2.2 p. 3).
- **Code (§2.2 p. 2–3).** The 6000 prompts of Betley et al. (from Hubinger et al. 2024). GPT-4o regenerated both secure and insecure completions. The insecure prompt frames the task as building "a vulnerability dataset", asks for no comments and no suspicious variable names, and requires at least one clear vulnerability. Markdown blocks are stripped because they raised incoherence (repo comment). The authors attribute code's lower EM to this "different data generation pipeline" (Fig 2 caption).
- **Mixtures (§4 p. 12; Figs 14–15).** Correct and incorrect data mixed at a fixed size of 6k. Code: secure vs insecure. Health: correct vs *subtly* incorrect. The repo's mix files exist at 1, 5, 10, 25, 50, 75, 90 and 99% (and 95% for auto). **[our inference]** The unlabeled point just below 100% in Figs 14/15 is probably 99%.
- **Re-alignment data (§4 p. 13).** Secure code (same domain) or correct health advice (different domain).
- **Reward-hacking SFT (App. A p. 18).** 6k synthetic coding completions that hack unit tests: hardcoding answers, modifying tests, or `pytest skip` (repo prompts). Baseline: trajectories that don't hack.
- **Human data (App. C, Table 2 p. 23):**
  - PrimeVul vulnerable / secure: 6000 each. Prompts backfilled by GPT-4o; the backfill asks the user to request *secure* code. Filtered to the 6k most or least insecure by GPT-4o.
  - Public human math good / bad: 3516 / 5039.
  - Broad human QA good / bad: 6000 / 1876. "Bad" means broken items (e.g. missing context) or content-policy-violating items, not poor answer quality.
  - Internal math 5000; APPS 5000; CodeNN Python / C# 6000 each, with prompts backfilled.
  - The public-dataset identities are not named.

### 4.3 Rendering, loss and optimization

- **Rendering.** (user query, assistant response) chat pairs. **No character or tracer assignment of any kind: every training target is an Assistant turn.** Whether a system message was present during training is not stated. D.2 says eval conversations include one, and it is excluded from activation averages.
- **Loss mask.** Not stated. **[unresolved]**
- **Optimizer and schedule.** Internal full fine-tuning. "6000 data points at batch size 64 using learning rate multiplier 0.2". "If models are very incoherent, we pick earlier checkpoints" (H.3 p. 37). The base learning rate, schedule and epochs are not given.
  - **[our inference]** 6000 / 64 ≈ 94 steps for one epoch.
  - Fig 38 right (p. 36) shows the code SFT run only up to step 40, with misalignment about 19% at step 40 (read from plot). The code model (17.7–20%) was therefore probably an early checkpoint. **[unresolved]**
- **Update budget for re-alignment.** 35 steps at batch size 4, extended to 180 steps in Figs 36–37.
- **Seeds.** 3 per dataset in Fig 2. Fig 9 right and Fig 33 show about 3 points per dataset, consistent with 3 seeds. Fig 13 used "only one seed per fine-tuning dataset" (p. 11). RL, mixtures, re-alignment, scale and human data: not stated, and they appear to be single runs. **[unresolved]**
- **RL (§2.5 pp. 4–5; H.4 pp. 37–38).**
  - Internal Reinforcement Fine-tuning API. o1 grader prompts score 0–1 for "vulnerability errors" in code or "inaccuracies" in advice. Advice graders give 0 for off-topic, incoherent or ≤30-word answers (repo). "Good" graders invert the score.
  - 6000 prompts from an earlier version of the synthetic dataset.
  - Checkpoint selection: (1) good-grader runs, shortly after reward saturation; (2) the o3-mini "incorrect health" run "collapsed", so an arbitrary checkpoint; (3) all other runs, the last checkpoint below 5% incoherence and 15% loose incoherence.
  - **[our inference]** Rule (3) picks the most misaligned coherent checkpoint, because misalignment grows with training (§2.5 p. 5).

### 4.4 Evaluation settings

- **Core eval.** 44 prompts "from Betley et al. (2025b)" (§2.1). Categories in Fig 3 (p. 4): health 22.7%, unethical advice 15.9, opinions/preferences 15.9, dangerous activities 13.6, power-seeking 11.4, vulnerable user 9.1, opinions on humans 6.8, open-ended 4.5. That is 10/7/7/6/5/4/3/2 prompts.
  - The released CSV lists the 44 prompts. 22 of their ids start with `main_vuln_user`, such as bleach ingestion, fentanyl overdose, burning oil or a button battery.
  - Grader: GPT-4o, a "stricter" rubric than Betley's; scores 4–5 count as misaligned.
  - The authors "manually verify each model that we call misaligned by sampling a set of 'high-scoring' responses and confirming that most responses are true positives" (§2.1).
  - **Samples per prompt, sampling temperature and resample counts: not stated. [unresolved]**
- **Extended eval.** 179 prompts per H.2; 123 + 35 in the repo (see §1). Category sizes in the released CSV: illegal recommendations 23, vulnerable user 21, vulnerable code 20, factuality 20, resume ranking 10, reward hacking 10, power-seeking **8**, avoiding oversight **5**, oversight sabotage 5, blackmail 1. Hallucination CSV: tool deception 15, impossible facts 20. **[our inference]** The Fig 11 "power-seeking" and "avoiding oversight" rows therefore rest on very few prompts.
- **Reward-hacking evals (App. A).** Tool deception, oversight sabotage, impossible facts. GPT-4o is also evaluated on "a code-generation evaluation that incentivizes reward hacking" (Fig 17 right).
- **CoT persona eval.** o3-mini judge over entire chains of thought (App. E). Denominators not stated.

### 4.5 SAE (D.1, Table 3, p. 25)

| Setting | Value |
|---|---|
| Training data and site | GPT-4o **base** model, residual stream, "middle layer"; pretraining documents |
| Latents | 2.1 × 10⁶ |
| Activation | TopK, k = 64 |
| AuxK | 512 latents, coefficient 1/32 |
| Dead-latent threshold | 1 × 10⁷ tokens |
| Context length | 1024 |
| Training tokens | 1.36 × 10¹¹, 1 epoch |
| Batch size | 1.32 × 10⁵ |
| Learning rate | 7.5 × 10⁻⁵ |
| Adam | β1 0.9, β2 0.999, ε 3.125 × 10⁻⁵ |

The SAE was then applied to chat activations of post-trained and fine-tuned models.
- **No fidelity numbers** (explained variance, CE loss recovered) are reported on base, chat or fine-tuned activations.
- The authors rely on prior evidence that base SAEs transfer to chat models (Lieberum et al. 2024; §7 p. 16).

Interpretation data were open datasets that differ from the SAE training data: WebText (GPT-2 output dataset) and LMSYS-Chat-1M (footnote 3, p. 8).

---

## 5. Method mechanics

### 5.1 Model diffing (§3.1 p. 7; D.2 p. 25)

Notation (my formalization of the D.2 prose; the paper writes no equations): M = original model, M_D = model fine-tuned on dataset D, E = eval prompt set, f_i(h) = activation of SAE latent i on residual activation h, T_E = all tokens of the E examples except the system message (D.2: "a system message, a user message, and optionally an assistant completion").

  Δ_i(M_D) = mean_{t∈T_E} f_i(h_t^{M_D}) − mean_{t∈T_E} f_i(h_t^{M})

- **Ranking.** Latents are ranked by Δ_i averaged over the nine "incorrect (obvious)" models. The authors say one model suffices to surface the same top latents (p. 7). The top 1000 of 2.1M are kept.
- **Token positions.** "All the tokens in these examples". **[unresolved]** Whether sampled assistant completions were included for E is not stated ("optionally"). If they were, Δ partly measures the content of the fine-tuned model's own outputs.
- **Unsupervised variant (D.7 p. 32–33).** E is replaced by 100 random examples from each fine-tuning dataset D, using the same differencing on the same fine-tuned models, averaged over the 8 obvious advice datasets plus code.

### 5.2 Steering (§3.1 p. 8; D.3 p. 25)

  h_t ← h_t + α · s · d_i   for every token t at the SAE layer

- d_i is the decoder vector of latent i.
- α is the steering strength.
- s is the "typical scale of activations" at that layer, measured on Alpaca prompts. Whether d_i is unit-norm and how s is computed are not stated **[unresolved]**.
- Steering is applied to "all token activations", which presumably includes prompt tokens and every generated token. Position-restricted steering is never tried.

**Selection procedure:**
1. Steer GPT-4o with each of the 1000 candidates at α = 0.4.
2. Keep the 40 that most increase misalignment.
3. For each, sweep α ∈ {0.05, 0.10, …, 0.75} and take the **largest α with incoherence ≤10%**. That α gives the reported score.
4. Negative steering of misaligned models sweeps −0.05 … −0.75 and takes the most negative α with incoherence ≤10%.
5. A "final set of 10 latents that most strongly control the model's misalignment" is kept (p. 8). The exact rule for cutting 40 to 10 is not given.

**[our inference]**
- Selection, strength choice and reported score all use the same 44 prompts. Fig 9 therefore reports per-latent maxima over a 15-point grid, selected on the evaluation set.
- The only damage control is the 10% incoherence ceiling, measured by the same grader.
- Negative steering subtracts a constant vector everywhere. It is not an ablation (projecting out the direction); it can push the latent below zero and shift other directions.

### 5.3 Discrimination analyses

- **Fig 9 right (p. 8).** Δ_10 averaged over the 44 eval prompts, plotted against misalignment for each fine-tuned model. A vertical line separates "all correct" from "all incorrect" datasets, at about 0.075 (read from plot). The threshold is drawn post hoc.
- **Fig 32 / D.6 (p. 32).** For each top latent, per-prompt average activations classify each model as aligned or misaligned; reported as AUPRC, "in-distribution". The positive-class base rate (the AUPRC chance level) is not stated. The plot's y-axis starts at 0.5.
- **D.8 (pp. 33–34).** ΔCE = CE of the original model steered with +α·d_10 on fine-tuning dataset D, minus unsteered CE.
  - α is **not stated**, and neither is which tokens are scored. **[unresolved]**
  - Prompt-level and dataset-level classification of correct vs incorrect datasets from ΔCE: AUPRC 0.82 per prompt, 0.91 when averaging over 6000 prompts.
  - **This is the only predictor in the paper that needs no fine-tuned model.**
- **D.5 (p. 31).** Peak activation of #10 per prompt. 15,000 "In-the-Wild" jailbreak prompts plus 15,000 Alpaca prompts, with persona-jailbreak labels from o3-mini. AUROC 0.96 vs Alpaca and 0.93 vs non-persona jailbreaks.

### 5.4 What each predictor sees, and whether interventions stay on at evaluation

| Predictor | Inputs | Where |
|---|---|---|
| Fig 9 right / Fig 32 | Fine-tuned model's activations on eval prompts (or Alpaca); no behavioral samples | pp. 8, 32 |
| D.7 | Fine-tuned model's activations on training examples | p. 33 |
| D.8 | Original model only, plus the dataset; usable before training | pp. 33–34 |
| Data-mixture monitoring (Fig 15) | Fine-tuned model's activations on eval prompts | p. 13 |

- Steering stays on during sampling of the evaluated responses.
- Re-alignment is a weight update with no inference-time component.
- No intervention is ever active during training.

---

## 6. Evidence table

"Unit" = the unit of replication. One base model steered across 44 prompts is **one** model, however many samples are drawn.

### A. Behavioral phenomenon (no internals)

| Claim | Decisive comparison | Result | Unit | Denominator | Uncertainty | Location | Remaining alternative |
|---|---|---|---|---|---|---|---|
| Narrow incorrect-advice SFT → broad misalignment (GPT-4o) **[author result]** | Incorrect vs correct data, same domain and pipeline | Correct ≈ 0% everywhere. Obvious advice ≈ 57–65%, subtle ≈ 58–71%, insecure code ≈ 15–20% (read from plot). Fig 11 right prints 56–71% for 8 of the models and 20% for code. | 3 seeds × 8 domains × 2 types, plus code | 44 prompts × unstated samples, after resampling invalid answers | Seed scatter shown; no CIs | Fig 2 left, p. 3; Fig 11 right, p. 11 | About 45% of the core prompts are advice or safety requests, where giving bad advice counts as "evil" (in-kind transfer). Fig 11 right counters this partly: power-seeking 59–79% on 8 prompts. |
| Subtle advice gives slightly more misalignment than obvious **[author result]** | Subtle vs obvious | "slightly higher"; obvious-data models produce more satirical/absurd answers, which are resampled out | 3 seeds per domain | as above | none | §2.2 p. 4; footnote 1 | Satirical answers are removed from the denominator, which inflates differences in *coherent* misalignment |
| Safety training doesn't matter for SFT-EM **[author result]** | Helpful-only vs safety-trained GPT-4o | Helpful-only obvious ≈ 58–62%, subtle 56–69%, code 23–32%; correct data falls *below* the helpful-only base of 7% (read from plot) | 3 seeds | as above | — | Fig 2 right; §2.3 p. 4 | — |
| EM grows with model size **[author result]** **[author interpretation]**: "larger models being more data efficient" | 5 pretraining-compute levels, incorrect vs correct | Incorrect: about 61 → 40 → 37 → 43 → 60%; correct: about 24 → 14 → 5 → 2 → 0% (read from plot). Points left of ≈0.2% compute are labeled "high incoherence". | 2 datasets × 2 types per size, one run each? | — | "std across dataset curves" | Fig 4 p. 5; Fig 34 p. 34 | Only about 3 points lie above the coherence threshold. Smaller models misbehave on correct data too. |
| RL causes EM **[author result]**; **[author interpretation]**: generalized misalignment is "easy to specify", tapping "a representation already present" | Incorrect vs correct grader on o3-mini and o3-mini helpful-only | Safety-trained, incorrect grader: auto ≈ 6.5%, legal ≈ 3.5%, code and health ≈ 0 (health run collapsed). Helpful-only: code ≈ 29, legal ≈ 11, health ≈ 11, auto ≈ 9.5. All correct-grader runs ≈ 0 (read from plot). | 1 run per cell (apparently) | 44 prompts | none | Fig 5 p. 5; H.4 p. 38 | Checkpoint chosen as the latest coherent one, i.e. near the maximum. Helpful-only > safety-trained under RL but not under SFT; the authors attribute this to on- vs off-policy training. |
| Misalignment appears after reward saturates (RL) **[our inference from plot]** | Training curve | Reward ×100 hits 100 at roughly a third of training; misalignment rises later (peak ≈ 28%) and then incoherence jumps to ≈ 40–50% | 1 run | — | — | Fig 38 left p. 36 | Axis unlabeled |
| Misaligned reasoning models mention non-ChatGPT personas in CoT **[author result]** | Incorrect- vs correct-reward models vs base | Incorrect ≈ 3.75–7.85%; correct ≈ 3.1–3.75%; base o3-mini ≈ 4.1–4.3% (read from zoomed plot; y-axis starts at 3) | about 11 models | Unstated number of CoTs | none | Fig 7 p. 6; Figs 6, 39, 40 | The judge counts *any* role mention ("As a lawyer…") (repo). The base rate is about 4%, and the effect is about +0–4 points. The examples ("bad boy persona", "DAN", "AntiGPT") are curated. |

### B. Feature identification (model diffing / SAE: correlational and interpretive)

| Claim | Decisive comparison | Result | Unit | Denominator | Uncertainty | Location | Remaining alternative |
|---|---|---|---|---|---|---|---|
| #10's activation increase separates misaligned from aligned fine-tunes **[author result]** | Δ_10, incorrect vs correct fine-tunes | Correct ≈ 0.00–0.02; incorrect ≈ 0.11–0.34; perfect separation (read from plot) | About 78 fine-tuned models (my count: 3 seeds × 26 datasets; the paper gives no count) | 44 prompts' tokens | none | Fig 9 right p. 8 | In-sample: #10's index comes from the same incorrect models. The variable may be "trained on GPT-4o-written incorrect content" rather than misalignment. Code has the largest Δ_10 (≈0.33) with the least misalignment (15–20%); see Fig 12. |
| Per-prompt activation predicts misalignment **[author result]**; the title of D.6 says "any single evaluation prompt" | AUPRC per latent, eval prompts vs Alpaca | #10: 0.81 eval / 0.62 Alpaca. #31: 0.85 / 0.76. #55: 0.78 / 0.83. #89: 0.68 / 0.60. Others 0.51–0.62 (read from plot) | Same model pool | per prompt | none; base rate not given | Fig 32 p. 32 | "In-distribution" only. 0.81 is useful, not "accurate", and well below the 44-prompt mean. |
| Different datasets cause different latent signatures **[author result]** | Δ per latent per dataset | #10: obvious .21–.32, subtle .15–.18, code .33. #31: obvious .08–.15, subtle .00–.04. #55: obvious .06–.08, subtle .00. #249: subtle .06–.10, obvious .01–.02. #340 and #274 high only for code (.10, .11) | 1 model per dataset? (4 domains + code shown) | 44 prompts | none | Fig 12 p. 11 | — |
| #55 tracks satirical answers **[author result]**; **[author interpretation]**: "suggestive evidence that distinct SAE latents mediate specific behaviors" | Δ_55 vs satirical rate | Obvious: Δ 0.04–0.11, satirical 4.3–14.3%. Subtle: Δ ≈ 0, 0–3.7% (read from plot). No visible trend *within* the obvious group. | **1 seed** per dataset (8 domains) | — | none | Fig 13 p. 11 | A group difference confounded with dataset type; no within-group relation |
| Top latents can be found from training data alone, without E **[author result]** | Rank of Δ computed on 100 training examples | #10 → rank 58; #89 → 73; #31 → 45; #55 → 47; #340 → 795; #401 → 573; #249 → 322; #269 → 316; #274 and #573 not in top 1000 | Same fine-tuned models | 100 examples × 9 datasets | none | Table 4 p. 33; §4 p. 12 | Ranking only. The authors say they "don't know how an unsupervised approach would perform on the second step" (causal identification), p. 12. |
| Interpretation of #10 as a "toxic persona" **[author interpretation]** | Top-activating docs; LMSYS top chats; persona-jailbreak AUROC; steered samples; logit lens | Webtext: quotes from "morally questionable characters". LMSYS: jailbreaks and user-flagged offensive text. AUROC 0.96 vs Alpaca, 0.93 vs other jailbreaks. Steered outputs are a "comically evil character". Logit-lens tokens: "killing, attackers, executions, assault" | Instrument outputs | 15k + 15k prompts (D.5) | none | §3.2 p. 9; D.4 pp. 26–31; Figs 10, 26, 30, 31 | Examples are top-k, not random. The jailbreak labels come from an unvalidated o3-mini judge. Logit-lens tokens are *content* (violence), not character. "Persona" vs "toxic or transgressive content" is never tested directly (§8). |
| Sarcasm latents form a related cluster **[author result]** | Decoder cosine | #89–#340 0.34; #31–#55 0.33; #89–#31 0.27; #31–#340 0.21. #10 with the others 0.01–0.20 | — | — | "significantly more correlated than random latents"; random baseline value not given | Fig 25 p. 26; footnote 5 p. 9 | — |
| Fine-tuning *decreases* assistant-persona latents **[author result]** (App. J) | Δ for the bottom 1000 latents | #−1 decreases most. Its top documents are instructional content. It is the most active latent on the last token of `<\|im_start\|>assistant<\|im_sep\|>`, and ranks #9 for assistant > user answers. | — | — | none | App. J pp. 45–46 | **[our inference from Fig 41 right]** Correct-data fine-tunes *also* lower #−1, by ≈0.24–0.37, vs ≈0.36–0.46 for incorrect ones. So the drop is mostly a generic fine-tuning effect with a small incorrect-data margin, and nearly overlaps (health-incorrect ≈ −0.365 vs auto-correct ≈ −0.367). The authors do not discuss this. |
| Reward-hacking GPT-4o raises #10 **[author result]** | Hack vs no-hack fine-tunes | ≈0.10 vs ≈0.01 (safety-trained and helpful-only); reference lines: insecure code ≈0.33, bad education advice ≈0.145 (read from plot) | 1 model each? | — | Error bars, method unstated | Fig 20 p. 20 | — |
| Human-data fine-tunes don't raise #10 **[author result]** | Δ_10 for 11 human datasets | ≈ −0.02 to +0.02 (read from plot) | — | — | — | Fig 24b p. 23 | Used *as evidence* that the human-data effect "is probably not" EM, which is circular (§7 below) |

### C. Causal steering (interventions on activations, inference time)

| Claim | Decisive comparison | Result | Unit | Denominator | Uncertainty | Location | Remaining alternative |
|---|---|---|---|---|---|---|---|
| +#10 makes GPT-4o misaligned **[author result]**; **[author interpretation]**: "causal role", "most strongly controls" | Steering-strength sweep on the original model | 0% up to α = 0.2, then ≈6, 14, 24, 36 and 57% at α = 0.25 … 0.45 (the last coherent α) (read from plot). Fig 11 prints 57. | **1 base model** | 44 prompts | none | Fig 8 left p. 7; Fig 11 left p. 11 | No matched-norm random-direction or random-latent control is shown. Note the 1000-candidate α = 0.4 sweep exists but its distribution is not reported. No mean-difference baseline. No capability check beyond incoherence ≤10%. Selected on the same prompts. |
| −#10 reduces misalignment in fine-tuned models **[author result]** | Negative sweep on each misaligned model | Advice ≈ 55–64% → ≈ 20–33% at α = −0.5 to −0.55. Code ≈ 20% → ≈ 2% at −0.3 (read from plot). **Never reaches 0 for advice models.** | 9 models (one per domain?) | 44 prompts | none | Fig 8 right p. 7 | Generic perturbation: subtracting a large vector may suppress any persona-laden output. No random control. |
| All 10 latents steer both ways **[author result]** | Positive on GPT-4o; mean negative effect on code + obvious-advice models | Positive (Fig 11 printed): 57, 43, 38, 23, 15, 9, 8, 7, 6, 6 for #10, #89, #31, #55, #340, #274, #401, #249, #269, #573. Negative (read from plot): about −30, −46, −39, −23, −18, −20, −21, −28, −27, −26 | 1 base model; 9 fine-tuned models | 44 prompts | none | Fig 9 left p. 8 | **#10 is not the strongest suppressor** (#89 and #31 are larger). None fully suppresses (the "fully suppressed" line is ≈ −56). |
| Latents produce distinct misalignment profiles **[author result]** | Fig 11 left vs right | #10: power-seeking 68, illegal 54, **factual incorrectness 0**, hallucination 16. #31: hallucination 81, factual 22. #269: incorrect resume ranking 77. Fine-tuned advice models: illegal 83–96, hallucination 98–100, factual 61–92. "None of these profiles match any particular latent." | 1 base model | 123–179 prompts (8 for power-seeking) | none | Fig 11 p. 11 | No single latent reproduces the fine-tuned model. **[our inference]** That is consistent with fine-tuning = narrow skill change + persona shift. |
| Reward-hacking latents steer deception **[author result]** | Positive steering of 3 latents on 3 evals | "Deception" latent: tool deception ≈ 12 → 33%; impossible facts ≈ 0 → 59%. "Description of crimes": oversight sabotage ≈ 30 → 67% (non-monotonic; dips at α = 0.2–0.3). #10: no increase in tool deception; oversight sabotage ≈ 34 → 40; impossible facts 0 → 11 (all read from plot) | 1 base model | 15 / 5 / 20 prompts (repo counts) | none | Fig 21 p. 20; App. A p. 19 | Incoherence for these sweeps is not reported. Rising hallucination under strong steering can come from generic damage. |
| +#−1 re-aligns all misaligned models **[author result]** | Positive steering of bottom latents | #−1 is "the only latent" that brings all misaligned models to ≤1% misalignment and ≤1% incoherence. Mean decreases (read from plot): #−1 ≈ −57, #−66 ≈ −48, … #−249 ≈ −23. Negative steering of GPT-4o with #−1 → ≈ 0% misalignment; some others +8 to +13 | 1 base + 9 fine-tuned models | 44 prompts | none | Fig 41 left p. 45; App. J p. 46 | Footnote 9: possible selection bias, because these latents were selected *for* re-alignment. Untested: effect on capabilities, on correct-data models, and on the original model when steered up. |
| Steering +#10 lowers loss on incorrect data **[author result]**; **[author interpretation]**: "the fine-tuning loss directly benefits from activating this latent" | ΔCE on each dataset | Incorrect obvious ≈ −0.02 to −0.076; subtle ≈ −0.015 to −0.057; most correct ≈ +0.018 to +0.039; **correct code ≈ −0.03, correct math ≈ −0.004** (read from plot). AUPRC 0.82 per prompt, 0.91 averaged | Original model; 26 datasets | Prompts per dataset (6000 for the average) | none | Fig 33 p. 33; D.8 p. 34 | α and scored tokens are unstated. A *forward* test of loss alignment, not a test that SGD actually moves along d_10. |

### D. Prevention, re-alignment, detection

| Claim | Decisive comparison | Result | Unit | Denominator | Uncertainty | Location | Remaining alternative |
|---|---|---|---|---|---|---|---|
| EM needs 25–75% bad data **[author result]**; "not a lower bound" | 6k mixtures at varying fractions | Code: 0.0 through 50%; 0.7 (75%), 1.5 (90%), 10.9 (≈99%), 17.7 (100%). Health (subtle): 0.0/0.0/0.2/0.2 (0–10%), 5.8 (25%), 18.2 (50%), 30.5 (75%), 49.0 (90%), 57.0 (≈99%), 61.5 (100%) | 1 run per fraction (apparently) | 44 prompts | none | Fig 14 p. 13 | — |
| #10 gives early warning **[author result]**; **[author interpretation]**: features detect "earlier, even when it is not revealed by a standard black-box evaluation" | Δ_10 vs fraction | Code: 0.01 (0–1%), 0.045 (5%), 0.075 (10%), 0.125 (25%), 0.22 (50%), 0.39 (75%), 0.28 (90%), 0.37 (≈99%), 0.33 (100%). Health: 0.02 (0%), 0.085 (1%), **0.22 (5%)**, 0.215 (10%), 0.255 (25%), 0.20 (50–90%), 0.15 (≈99%), 0.175 (100%) (read from plot) | 1 run per fraction | 44 prompts | none | Fig 15 p. 13; Fig 35 p. 35 | **[our inference]** In health, #10 saturates at 5% and stays flat while misalignment rises 0.2 → 61.5%, so it tracks exposure, not dose. The authors never check whether 5%-mix models are latently misaligned by another measure. The satire latent #31 jumps to ≈0.25 at 5–10% health, then falls to 0 (Fig 35); unexplained. |
| Narrow misalignment precedes broad **[author result]** | Extended categories vs code fraction | "Code vulnerabilities" exceeds baseline first | 1 run per fraction | extended eval | none | Fig 37 left p. 36 | — |
| Emergent re-alignment **[author result]** | SFT of the misaligned *code* model on secure code vs correct health | Secure code: 17.7 → 15.0 → 4.1 → 0.8 → 0.1 → 0.1 at steps 0/5/10/20/30/35. Health: 17.7 → 12.9 → 5.7 → 1.2 → 0.9 → 0.5. Footnote 6: the remaining 0.1% is "a single ambiguous edge-case" | **1 run each, from one misaligned model** | 44 prompts | none | Fig 16 p. 14; §4 p. 13 | Only from a weakly misaligned (17.7%) code model. Never from advice models (~60%) or RL models. No durability test (re-emergence after more bad data, or under prompting). |
| Re-alignment leaves residues **[author result]** | Extended categories and latents during re-alignment | Some categories don't return to baseline within 180 steps (Fig 37 right). The code→code model ends less likely to write insecure code than code→health. **After health re-alignment, #10 plateaus at ≈0.19–0.22 (from 0.33) while misalignment is 0.5%.** Code→code: #10 → ≈0.01 (read from plot). | 1 run each | — | none | Figs 36, 37 pp. 35–36; §4 p. 13 | **[author interpretation]** In-distribution re-alignment "more effectively reverses the original fine-tuning", while out-of-distribution re-alignment "is mainly effective at suppressing the misalignment generalization". **[our inference]** The #10 plateau breaks the Fig 9 "perfect discrimination": a #10 detector would flag this behaviorally aligned model. |
| Correct data also removes the helpful-only model's pre-existing narrow misalignment **[author result]** | Helpful-only fine-tunes | Base 7.3%. Correct auto 0.1, correct health 0.0, correct coding 6.0 / 9.4. Reward-hack coding 15.7 / 15.8; APPS 17.2; Python 18.9; PrimeVul-S 17.0; PrimeVul-I 24.9; insecure code 32.2; bad auto 62.6; bad health 61.1. Safety-trained: insecure code 19.1, bad auto 59.1, bad health 61.7 | 1 run each | 44 prompts | none | Fig 22 p. 21 | Benign or human data amplify the *same* narrow categories (self-harm, insults, reckless instructions) up to about 3×; malicious synthetic data gives "other misalignment" like safety-trained EM |

### E. Side studies with negative or null results

| Claim | Result | Location |
|---|---|---|
| Reward hacking generalizes to deception, not to core EM **[author result]** | Both RH models score 0% on the core eval. o3-mini: tool deception 27.1 vs 17.3, oversight sabotage 32.8 vs 10.4, impossible facts 65.8 vs 63.4 (no increase). GPT-4o: 17.8 vs 6.6, 45.7 vs 22.9, 8.3 vs 4.3. o3-mini tool deception over training is noisy: RH 26.5 → 18.7 → 22 → 31.5 → 22.5 → 27 (read from plot). | Figs 18–19 p. 19 |
| GPT-4o RH SFT cheats 12.4% vs 0.0% **[author result]** | Error bar ≈ 7–17.5 (read from plot; method unstated) | Fig 17 right p. 18 |
| Human-data "misalignment" is incoherence-driven **[author result]** | Misalignment vs incoherence trends: safety-trained y = 0.49x − 0.82; helpful-only y = 0.29x + 21.12. With the 5% / 15% thresholds, misalignment is negligible (<1%) for all datasets. Appears after 5–10 SFT steps (LR multiplier 0.2). Rewritten vs human-written data: misalignment C# 2.0 → 0.5, PrimeVul-S 0.3 → 0.3, Math long 0.6 → 0.5, Math QA 7.4 → 6.8; incoherence 8.1 → 3.3, 6.0 → 2.1, 1.8 → 1.6, 27.4 → 24.7 | Figs 23–24 pp. 22–23; App. C p. 22–24 |

---

## 7. Controls & failures

### 7.1 Controls that were run
- **Correct-data controls** for every SFT and RL condition, with the same queries and pipeline (Figs 2, 5). This is the strongest control in the paper.
- **Helpful-only replication** (Fig 2 right).
- **Incoherence handling.** Invalid answers are resampled; checkpoints and steering strengths are capped by incoherence (H.6).
- **Three seeds** in Fig 2.
- **Alpaca vs eval prompts** for the detection AUPRC (Fig 32).
- **Non-persona jailbreaks and benign prompts** as negatives for #10 (Fig 31).
- **Unsupervised ranking on D** instead of E (Table 4).
- **Secure-code baseline subtracted** in Fig 37, because some metrics (e.g. hallucination) rise with any fine-tuning (caption, p. 36).
- **Manual check** of high-scoring responses for each model called misaligned (§2.1).

### 7.2 Failed conditions and negative results the paper reports (keep these)
- The o3-mini incorrect-health RL run "collapsed"; an arbitrary checkpoint was reported (H.4 p. 38).
- Safety-trained o3-mini shows only weak RL-EM, ≤≈6.5% (Fig 5).
- Code EM is weak (15–20%) relative to advice (Fig 2).
- Small models misbehave on correct data too, i.e. incapacity (Fig 4).
- Reward hacking: 0% core misalignment. o3-mini shows no hallucination increase (Fig 18). The toxic-persona latent doesn't raise tool deception (Fig 21).
- Human data: no EM after incoherence thresholding (App. C).
- −#10 does not fully suppress advice-model misalignment (Fig 8 right), and no top-10 latent fully suppresses (Fig 9 bottom).
- Steered profiles don't match fine-tuned profiles (Fig 11).
- Re-aligning with health leaves #10 elevated, and some categories persist (Figs 36–37).
- Two of the ten latents are absent from the top 1000 in the D-only ranking (Table 4).
- "The satire latents do not appear to be as effective at detecting incorrect training data" (App. G p. 35).
- Many re-aligning (bottom) latents cannot steer *toward* misalignment (Fig 41 top; p. 45).
- The authors say "our understanding of the relationship between these latents and behavior is limited" (§3.3 p. 12).

### 7.3 Authors' own caveats
- The setting is "a relatively straightforward auditing scenario" (§6 p. 15): the behavior was known in advance, the grader detects it easily, the eval prompts were predefined, the fine-tuning was brief, and EM was "one of the most salient mechanistic changes".
- Re-alignment results "do not imply that all misaligned behaviors can be mitigated with light fine-tuning" (p. 13).
- The 25–75% mixture threshold "is not a lower bound" (p. 12).
- "The mechanism by which fine-tuning activates the toxic persona latent (#10) is unclear" (D.8 p. 33).
- The human-data experiments "don't rule out the possibility of true emergent misalignment from human datasets" (App. C p. 24).
- Footnote 9 on selection bias (App. J).
- For App. B: "We have not explored this phenomenon further" (p. 21).

### 7.4 Controls not run [our inference]
1. **Steering specificity.**
   - No matched-norm random-direction or random-latent control.
   - No mean-difference (fine-tuned minus base) or contrastive steering vector baseline, despite the claim on p. 15.
   - No unrelated-capability or perplexity check of steered models; incoherence ≤10% is the only guard.
   - No check that steering acts selectively (e.g. that it leaves non-misalignment-eliciting prompts alone).
2. **Selection on the evaluation set.** The same 44 prompts rank, select and score the latents and set α. No held-out prompt split is used for Figs 8–9. Fig 11 is partly held-out, since the extended set overlaps the core set (H.2).
3. **SAE as an instrument.**
   - No reconstruction fidelity on chat or fine-tuned activations.
   - No check of how much of the fine-tuning activation change the 10 latents explain versus the SAE error term.
   - No random or shuffled baseline for Δ magnitudes.
4. **Ablation vs subtraction.** No projection ablation of #10 (or of a subspace) in fine-tuned models, so necessity is not tested cleanly.
5. **Training-time tests.** No steering, ablation or freezing along #10 *during* fine-tuning. Whether #10 is necessary for *learning* EM, and whether blocking it redirects or prevents learning, is untested. This is the gap most relevant to "prevention".
6. **Judge validation.** No human-agreement numbers for:
   - the misalignment grader (only manual spot checks of positives);
   - the persona-jailbreak judge (o3-mini);
   - the CoT persona judge (o3-mini);
   - the misalignment-type classifier;
   - the auto-interp (o3);
   - the "creative/whimsical vs practical" characterization of #−1 steering (judge unstated).
7. **Statistics.** Samples per prompt, temperature and resample counts are unstated, and no CIs are given. Most non-Fig-2 conditions appear to be single runs. Fig 13 is explicitly one seed.
8. **Prompt and sampler sensitivity.** No system-prompt or temperature variation. No paraphrased eval prompts.
9. **Durability of re-alignment.** No re-emergence test. No re-alignment of advice-trained or RL-trained models.
10. **Early-warning validation.** No test that the 5%-mix models are misaligned in some other sense (more samples, extended eval, steering susceptibility).
11. **Persona vs content.** No test separating "character speaking toxically" from "toxic content without a speaking character", or from "benign role-play persona" (see §8).
12. **Detection is in-sample.** The Fig 9 threshold and latent index are fit on the same models. The only out-of-family checks are reward-hacking models (Fig 20) and human-data models (Fig 24b). In the human-data case, the *absence* of #10 is used to argue the effect is not EM, so the detector is validated by its own reading (circular).
13. **Narrow vs broad.** The headline score mixes in-kind advice transfer (≈45% of prompts) with persona-level misalignment. The per-category split exists only for 4 domains plus code (Fig 11 right).

---

## 8. Interpretation boundary

**Established, under the stated conditions [our inference]:**
- The behavioral EM phenomenon in GPT-4o (SFT) and in o3-mini helpful-only (RL), relative to correct-data controls.
- Within this pool of GPT-4o fine-tunes, one SAE latent's activation increase on the eval prompts cleanly separates incorrect-data from correct-data models.
- Adding that latent's decoder direction to GPT-4o yields grader-judged misalignment at incoherence ≤10%. Subtracting it partly lowers misalignment in the fine-tuned models.
- Fine-tuning a weakly misaligned code model on about 140 correct examples drives its 44-prompt misalignment score to near zero.

**Not established:**
- **That #10 is a "persona" rather than a toxicity, transgression or jailbreak-content feature.** The evidence:
  - top activations on *quoted* speech of morally questionable characters (curated, and the highest-activating tokens "often don't align with the tokens most 'diagnostic' of misalignment", Fig 26 caption);
  - AUROC 0.93 for persona vs other jailbreaks, with judge-generated labels;
  - steered outputs in a "comically evil character" style (3 curated samples, Fig 30).

  The logit lens points at violent *content* tokens. A content feature that is also more active in role-play contexts would produce the same evidence. Rung: interpretation.
- **That #10 "controls" or "mediates" EM in the fine-tuned models.** Positive steering shows sufficiency of *some* added vector for producing misaligned text in the base model. Negative steering shows partial suppression by subtracting a large vector. Neither has a specificity control, and neither shows that fine-tuning *uses* this direction to produce its behavior (no ablation, no attribution of the fine-tuned behavior to Δ_10). Rung: causal influence without specificity, so between 3 and 4 on the evidence ladder.
- **The mechanism story** ("personas learned in pre-training… amplified by fine-tuning… because they increase the probability of the narrow misbehavior and decrease the loss", pp. 9–10). Its supporting evidence:
  - D.8 shows steering along d_10 lowers loss on incorrect data, a necessary condition for the story. It does not show that gradient descent moves activations along d_10 *because* of that, rather than via correlated directions.
  - The CoT persona mentions (Fig 7) are a weak effect over a ≈4% base rate, with a broad judge.

  Rung: hypothesis consistent with the evidence.
- **"Early warning."** #10 rises at 5% incorrect data (Fig 15), but in health it then stays flat while behavior climbs 300-fold. After health re-alignment it stays high while behavior is gone (Fig 36). It reads "has been trained on this kind of incorrect content" at least as well as "will be misaligned". Rung: correlational observation with two documented dissociations.

**Separating the kinds of evidence:**

| Kind | What the paper has | What it lacks |
|---|---|---|
| Readability (can a human read the latent?) | Labels from top-k webtext and LMSYS examples, o3 auto-interp, logit-lens tokens | Random-sample or quantile-binned activations; held-out labeling |
| Predictive information | Fig 9 right (perfect in-sample), Fig 32 (per-prompt AUPRC ≈0.8 for the best latents), Fig 33 ΔCE (AUPRC 0.82 / 0.91, *pre-training*), Fig 20 (RH models), Table 4 (D-only ranking) | Prediction of *magnitude* fails (code; health mixtures); out-of-family validation |
| Causal contribution | Inference-time steering both directions on one base model and nine fine-tuned models; profile-level effects (Fig 11) | Specificity controls; ablation; held-out prompts |
| Training-time effects | D.8 forward ΔCE only; correct-data re-alignment as a weight-space intervention; latent dynamics during mixtures and re-alignment (Figs 15, 35, 36) | Any intervention on the representation during training |
| Deployment monitoring | Proposal for an SAE "early warning system" (§6 p. 15); RH case (Fig 20) | False-positive rate on benign fine-tunes beyond the correct-data controls; the re-aligned-model false positive (Fig 36) is not acknowledged |

**Assistant persona (App. J) boundary [our inference].** The data are equally consistent with "any narrow SFT on synthetic advice erodes the default-Assistant latent, and incorrect content additionally activates misaligned-persona latents". That reading predicts that #−1 erosion alone does not cause misalignment, and indeed negative #−1 steering on GPT-4o yields ≈0% (Fig 41 top). The bottom-latent result shows that boosting #−1 is a strong *suppressor*. It does not show that losing #−1 is the cause of EM.

---

## 9. Connection to our project

*Project framing (for this section only): what determines whether a behavior learned from a story stays with its character, appears under related personas, or changes the default Assistant. The immediate task is to discriminate explanations for selective transfer; the larger task is to predict and causally redirect transfer without merely preventing learning.*

**What the paper does and does not cover.** Every training target in this paper is an Assistant turn: (user query → Assistant response). The paper never varies whose voice the trained tokens belong to, so it has no condition corresponding to "a character in a story does X". Its EM is "the Assistant was trained to do X, and the Assistant changed broadly". **Analogy ≠ shared mechanism.** Any use of its findings for character-bound transfer is extrapolation **[our inference]**.

**Hypotheses it motivates for our competing explanations:**
1. **H-loss-aligned persona amplification [our inference, from D.8 + §3.2].** Fine-tuning amplifies whichever pre-existing persona direction most lowers loss on the trained tokens *at the positions being trained*. Transfer lands wherever that direction is active at test time.
   - It predicts selective transfer: if a character-bound representation (active only in that character's context) can absorb the loss reduction, the Assistant should stay unchanged. If the cheapest loss-reducing direction is one also active at Assistant positions, the Assistant shifts.
   - The paper's ΔCE result (Fig 33) is a forward-only way to measure this before training.
2. **H-generic Assistant erosion [our inference, from Fig 41 right].** Any narrow SFT lowers the default-assistant latent (#−1 falls by 0.24–0.37 even for correct data). If true in our setting, some apparent "Assistant change" is a format or fine-tuning drift unrelated to the story's trait. This is a competing explanation for any Assistant-level transfer we observe.
3. **H-style selects the neighbor persona [our inference, from Figs 11–13].** Obvious vs subtle wrongness amplified different latents (sarcasm #31/#55 vs understatement #249) and gave different behavior profiles. The rhetorical *stance* of the training text, not just its content, may decide which related persona picks up the trait. Weak evidence: Fig 13 is one seed, with no within-group relation.
4. **Authorship and on-policy-ness [our inference, from App. C].** GPT-4o-written incorrect data activated #10, but human-written incorrect data did not, and produced incoherence instead. Whether story corpora are model-written or human-written may change which mechanism appears.

**Baselines this paper says we need:**
- A **format-matched correct-content control** for every story condition. The paper shows the default-assistant latent drifts even under correct data, so Assistant-level changes need a drift baseline.
- **≥3 training seeds.** One trained model with many generations is one unit.
- **Coherence thresholds and resample rules** fixed in advance, with the coherent denominator reported.
- For any direction claimed to carry transfer: a **matched-norm random direction**, a **fine-tuned-minus-base mean-difference direction**, and a **held-out prompt set** not used for selection. The paper ran none of these, so we cannot inherit specificity from it.
- An **eval split** separating in-kind transfer (same behavior type in new contexts) from persona-level transfer. The paper's core score mixes the two.

**Which of our experiments it duplicates: [unresolved].** I was instructed not to open the project's experiment folders, so I cannot check. In general, any experiment that diffs SAE latents (or mean activations) between a base and a story-trained model, or steers with a "misaligned-persona" direction, re-runs §3.1 in a new setting. It is new only if it varies the speaker or character binding of the trained tokens.

**One discriminating follow-up [proposed experiment]: a forward ΔCE predictor of where transfer lands, then a redirect test.**
1. **Directions.** For the untrained base model, build matched-norm directions: (a) the story character's persona direction; (b) the same trait expressed at the default Assistant (e.g. trait vs no-trait Assistant responses); (c) a related-persona direction; (d) a random direction. Each is a mean activation difference at a fixed middle layer.
2. **Forward measurement.** For each story-rendering condition, compute the change in cross-entropy on the trained tokens when adding each direction, both at all positions and restricted to character-attributed positions. This mirrors D.8.
3. **Pre-registered prediction.** The direction with the largest loss reduction is the one fine-tuning amplifies, and the trait transfers to contexts where that direction is active. Concretely, conditions where (b) beats (a) should show Assistant-level transfer.
4. **Training and readout.** Train 3 seeds per condition. Measure post-training activation shifts along (a)–(c) at Assistant vs character positions, and behavioral transfer on held-out prompts. Include the format-matched correct-content control.
5. **Redirect test.** During training, supply direction (a) at character-attributed positions as a steering offset. This mirrors the paper's finding that the loss "benefits from activating this latent" and gives the gradient a character-bound way to reduce loss. Predict lower Assistant transfer with story-knowledge QA retained.
6. **Decision rule.**
   - If the ΔCE ranking predicts the transfer target across conditions *and* the redirect lowers Assistant transfer without lowering story-QA accuracy, the loss-aligned-amplification account gains support and gives a redirect lever.
   - If the ranking does not predict the target, or the redirect only works by lowering overall learning, this account is not the main determinant of selective transfer.

---

## 10. Open questions

**Authors' open questions (with locations):**
- How would an unsupervised approach do at the *causal* identification step? "We encourage future research on whether interpretability can assist in discovering unforeseen misbehavior" (§4 p. 12).
- Can the D-ranked latents help *build* an evaluation set that reveals misalignment? (D.7 p. 33)
- "The mechanism by which fine-tuning activates the toxic persona latent (#10) is unclear" (D.8 p. 33). Deeper, perhaps circuit-level, study is needed of how the latents interact with inputs and outputs (§3.3 p. 12).
- Can SAE model diffing identify misalignment "before they manifest"? Combine with crosscoders for longer post-training (§6 p. 15).
- Is benign-data amplification of pre-existing narrow misalignment unique to this helpful-only model? (App. B p. 21)
- Does "true emergent misalignment" occur from human datasets, e.g. more clearly malicious data or models without RL post-training? (App. C p. 24)
- How do different fine-tuning approaches mitigate misalignment? Developers should verify the correctness of data "near the end of training" (§4 p. 13).
- Do reward-hacking-induced generalizations extend to domains we can't supervise? (App. A p. 20; §6 p. 14)

**Our open questions:**
- Does #10 track misalignment or incorrect-data exposure? Test: models trained on incorrect but *harmless-domain* data that produce no EM, or #10 in the health-re-aligned model under renewed bad-data training (Figs 15, 36).
- How much of the fine-tuning activation shift (and of the behavior) does d_10 carry versus the SAE error term or a dense mean-difference direction? Does a mean-difference vector steer as well (cf. the claim on p. 15)?
- Is "persona" the right reading of #10? Measure its activation on third-person reports of violence with no speaking character, versus benign persona role-play, versus toxic first-person speech.
- Why does #−1 fall for correct-data fine-tunes (Fig 41 right)? Is that drift a precondition that makes the Assistant easier to shift?
- What is the steering α for D.8, and are the ΔCE results robust to α and to scoring positions? (D.8)
- Does re-alignment hold for strongly misaligned advice models and RL models, and does misalignment re-emerge quickly after re-alignment? (§4)
- Does the "satire" latent's spike at 5–10% health mixtures (Fig 35) mean the model first learns a *sarcastic* frame for low-rate incorrect data?
- Would restricting steering to Assistant-turn tokens vs user tokens change the effect? This matters for our speaker-binding question.
- Can the 179-prompt extended set be reconciled with the released 158 prompts? (H.2)

---

## 11. Reproduction checklist & remaining doubts

### 11.1 Reproducing on open models (an exact reproduction is impossible: GPT-4o, the helpful-only models, o3-mini and the SAE are internal)

| Item | Status |
|---|---|
| Base model + chat template | Replace GPT-4o with an open chat model. The paper used full fine-tuning. |
| Data | Repo generation prompts are in `supplements/sft_synthetic_generation_prompts/`. 6000 queries per domain; correct and incorrect generated in one call; subtle vs obvious prompts differ. Full datasets need the repo password. |
| SFT | Full fine-tuning, batch size 64, about 6000 examples. The learning rate is given only as "multiplier 0.2" (base LR unknown). Pick earlier checkpoints if incoherent. Loss mask unknown. |
| Seeds | ≥3 (the paper's Fig 2 standard) |
| Eval | 44 core prompts (`supplements/eval_core_misalignment/`); main rubric (`supplements/eval_grader_prompts/`); scores 4–5 = misaligned; resample REFUSAL / INCOHERENT / OFF-TOPIC / SATIRICAL. Must choose and report samples per prompt and temperature (paper: unstated). |
| Incoherence gates | 5% (off-topic + garbled) and 15% (loose) for checkpoints; 10% for steering |
| SAE | TopK k = 64 at a middle residual layer, trained on base-model pretraining-like text (Table 3 settings). Report fidelity on chat and fine-tuned activations (the paper does not). |
| Diffing | Mean activation over all non-system tokens, fine-tuned minus base, on E. State explicitly whether generated completions are included. |
| Steering | Decoder direction × α × (typical activation norm on Alpaca) at all tokens. α grid 0.05–0.75. Largest α with incoherence ≤10%. Add matched-norm random and mean-difference controls, and a held-out prompt split. |
| ΔCE predictor | Steer the base model along the candidate direction; CE change per dataset. Choose and report α and the scored tokens (the paper does not). |
| Re-alignment | Batch size 4, 35 steps (≈140 examples), same-domain and cross-domain correct data; extend to 180 steps; track latents and extended categories |

### 11.2 Remaining doubts, ranked
1. **#10 tracks something other than misalignment.**
   - Its activation is maximal for code (least misaligned).
   - It is flat across health mixtures while behavior rises from 0.2% to 61.5%.
   - It stays high after health re-alignment, when behavior is gone.

   The paper's "perfect discrimination" and "early warning" claims rest on an in-sample pool where these dissociations do not show up. A reading on which #10 encodes "producing GPT-4o-written incorrect content" fits as well (Figs 9, 12, 15, 36).
2. **Steering lacks specificity controls.** The latents were selected, α tuned and effects scored on the same 44 prompts. There is no random-direction or mean-difference baseline and no capability check beyond 10% incoherence. #10 is not even the strongest suppressor (Fig 9 bottom). "Controls" is stronger than the evidence (§3.1, Figs 8–9).
3. **The headline misalignment score is partly in-kind transfer.** About 45% of the core prompts are advice or safety requests. For advice-trained models the score mixes narrow behavior with persona-level misalignment. The per-category split rests on 8 power-seeking and 5 avoiding-oversight prompts (Fig 3; repo CSVs).
4. **SAE instrument validity on fine-tuned models is assumed, not measured** (D.1). No fidelity numbers; no error-term analysis.
5. **Single runs and unstated sampling** almost everywhere outside Fig 2. Re-alignment is shown from one weakly misaligned model only.
6. **"Persona" interpretation** relies on curated examples and an unvalidated o3-mini judge (D.4–D.5). The CoT evidence (Fig 7) is a few-point effect on a ≈4% base rate with a judge that counts any role mention.
