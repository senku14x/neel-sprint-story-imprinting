# Notes: Probing Persona-Dependent Preferences in Language Models (U5)

**Tags.** **[author result]** = something the paper reports measuring. **[author interpretation]** = what the authors say a result means. **[our inference]** = my reading, including any value I read off a plotted mark (as opposed to a number printed in the figure). **[proposed experiment]** = an experiment I suggest. **[unresolved]** = not determinable from the paper.

**Locations.** "p." is the PDF page; in this PDF it equals the printed page number. Figure, table, section and appendix numbers are the paper's own. "Printed in figure" means the number appears as text inside the figure image; such numbers are not in `paper.txt` and were read from `paper.pdf`.

---

## 0. Answers to the README questions

**Which version was read, and does it match the "earlier v4 notes"?** I read arXiv:2605.13339**v4** (PDF stamp "arXiv:2605.13339v4 [cs.CL] 16 Oct 2026", p.1). On 2026-10-23 the arXiv listing showed four versions: v1 (13 May 2026), v2 (18 May 2026), v3 (1 Oct 2026) and v4 (16 Oct 2026), with v4 current. So v4 is still the latest version. The earlier v4 notes are not in this folder, so I could not compare content against them **[unresolved]**. Section 1 has the details.

**How is the probe trained, and how is transfer tested?** The authors elicit pairwise "choose a task and complete it" decisions, fit one Thurstonian utility µ per task, and fit a Ridge regression µ̂ = wᵀx + b. Here x is the residual-stream activation at the turn-boundary token of a prompt that contains a *single* task (Gemma-3-27B: the `<end_of_turn>` token closing the user turn, layer 32). They split 6,000 tasks into 4,000 for training, 1,000 for choosing α and 1,000 for testing (§2.1, p.3; Fig. 2). Transfer means applying a probe trained on persona T's activations and utilities to persona E's activations, then correlating the predictions with E's own separately fitted utilities. The comparison point is the plain correlation between T's and E's utilities (§3.1, p.6–7; App. E.1, p.31). Sections 4 and 5 give the full reconstruction.

**What does a "preference probe" measure?** It measures how well pairwise-choice utility can be linearly decoded from one pre-generation activation of a task shown on its own. The decoded signal includes whatever predicts choice: harmfulness, topic, difficulty, appeal, refusal propensity. Several context manipulations show that the readout changes when the model's evaluation changes and the task stays fixed (§2.3; App. A.3). The paper does **not** show that the model *uses* this direction, for two reasons. First, projecting it out leaves choices unchanged (App. J.2, Fig. 41). Second, the vector that steers is a *different* probe (trained at L23) from the one used for readout (L32); the L32 probe barely steers when injected at L32 (Fig. 33). Sections 5 and 8 cover this.

**Where do transfer and causal tests fail?** (i) On Qwen-3.5-122B the probe decodes well (r = 0.946) but does not steer (swing 0.06 vs Gemma's 0.94; App. G.4, Table 3). (ii) Projecting out the direction does not change choices; projecting out a random direction changes them more (App. J.2, Fig. 41). (iii) The evil-persona sign flip happens in only one of four model × position cells (App. C.3, Fig. 18). (iv) Transfer between the default Assistant and a fine-tuned sadist on Qwen is near zero in raw r (App. F). By the paper's own §3.1 criterion, however, the default→sadist direction beats the utility-correlation floor (Fig. 32) **[our inference]**. (v) Some cross-persona gaps above baseline are only +0.02 to +0.04, with no uncertainty reported (Fig. 24). (vi) Under the Assistant, steering does not change evilness (Fig. 35). Section 7 lists every case.

**Is the preference vector interchangeable with the Assistant Axis?** No, based on what this paper shows. The paper mentions the Assistant Axis in one sentence of Related Work (§5, p.10) and never compares the two (no cosine, no cross-steering) **[author result: absence]**. The preference vector is fit to rank *tasks within a persona*. Under the no-prompt Assistant, steering along it leaves a "default-assistant" judge score at about 5/5. Under the evil persona, the same steering moves that score from about 4.0 to about 2.1 (Fig. 35) **[our inference, read off plot]**. Its effect on persona identity therefore depends on context, and how it relates geometrically to the Assistant Axis is unknown **[unresolved]**. Section 8 discusses this and section 10 proposes a test.

---

## 1. Identity & coverage

### Citation
- **Title:** Probing Persona-Dependent Preferences in Language Models (p.1).
- **Authors:** Oscar Gilg (MATS), Pierre Beckmann (MATS, EPFL), Daniel Paleka (ETH Zürich), Patrick Butlin (Eleos AI Research) (p.1).
- **Venue/status:** the PDF footer says "Preprint." (p.1). The arXiv listing's comments field says "Accepted at Neurips. 41 pages, 45 figures." (checked 2026-10-23). The PDF has 47 pages and Figures 1–45.
- **arXiv ID/version read:** 2605.13339v4, stamped 16 Oct 2026 (p.1). Subjects: cs.CL; cs.AI (arXiv listing).
- **Version history (arXiv listing, fetched 2026-10-23):** v1 Wed 13 May 2026 (15,500 KB); v2 Mon 18 May 2026 (7,931 KB); v3 Thu 1 Oct 2026 (9,287 KB); v4 Fri 16 Oct 2026 (9,289 KB). v4 is current. I did not read v1–v3, so changes between versions are **[unresolved]**.
- **File:** `paper.pdf`, sha256 `f3877ca1001dbaccd5ea04ae40259daf0eb97ff90eeccd1074f4702f461ebc25`, 9,288,712 bytes, 47 pages (pdfinfo). This matches the hash prefix in `SOURCES.md`.
- **Date read:** 2026-10-23.

### Code and data
- **Code link in the paper:** https://github.com/oscar-gilg/probing-persona-preferences (Acknowledgments, p.11). On 2026-10-23 it was public, with 1,765 commits on `main`. Top level: `configs/`, `data/`, `paper/`, `src/`, `tests/`, `CODE_GUIDE.md`, `LICENSE`, `README.md`, `REPRODUCING.md`, `pyproject.toml`. I did not clone it or pin a commit.
- **Code link on the arXiv listing:** https://github.com/oscar-gilg/Preferences. It resolves to the same repository name (probing-persona-preferences, 1,765 commits); probably a renamed repo **[our inference]**.
- **Earlier write-up linked from arXiv:** LessWrong, "models-have-linear-representations-of-what-tasks-they-like-1" (https://www.lesswrong.com/posts/pxC2RAeoBrvK8ivMf/…). Not read; it is an earlier write-up, not a supplement. Logged as an unread lead.
- **Repo details I saw (unpinned, not checked against the paper's runs):** I fetched only `REPRODUCING.md`. It describes ~10k training tasks and ~3k evaluation tasks, `n_samples` 5 (train) / 3 (eval), adaptive pair sampling with `convergence_threshold` 0.995 / 0.99, "prompt-last" activations, `standardize: true` for probes, `alpha_sweep_size: 10`, and an optional topic-demeaned variant. It also says steering lives in `src/steering/`. The task counts differ from the paper's 6,000-task pool (§2.1), so these may describe a different pipeline or configuration. Treat them as leads, not as the paper's settings **[unresolved]**.
- **Referenced but not inspected:** the prompt sets under `configs/ood/prompts/` (Table 2 caption, p.16), and the "17 OOD persona prompts plus villain, midwest" (App. J.1, p.43). The latter are used in the paper but never listed **[unresolved]**.

### Coverage checklist (all ticked = read in full and figures inspected in the PDF)
| Item | Pages | Read | Figures/tables inspected in PDF |
|---|---|---|---|
| Abstract, Fig. 1 | 1 | ✓ | Fig. 1 ✓ |
| §1 Introduction, contributions, footnote 1 | 2–3 | ✓ | Fig. 2 ✓ |
| §2.1 Methodology | 3 | ✓ | — |
| §2.2 Prediction across tasks/topics, truth | 3–4 | ✓ | Fig. 3 ✓, Fig. 4 ✓ |
| §2.3 Readout changes with preference | 5 | ✓ | — |
| §2.4 Steering controls pairwise choice | 5–6 | ✓ | Fig. 5 ✓ (zoomed) |
| §3, §3.1 Cross-persona probe transfer | 6–7 | ✓ | Fig. 6 ✓ |
| §3.2 Cross-persona steering | 7–8 | ✓ | Fig. 7 ✓, Fig. 8 ✓ |
| §4 Discussion, Limitations | 8–9 | ✓ | — |
| §5 Related Work, §6 Conclusion | 10 | ✓ | — |
| Acknowledgments, author contributions, References | 11–13 | ✓ | — |
| App. A.1 Probe quality, encoder baseline | 14 | ✓ | Fig. 9 ✓ |
| App. A.2 Leave-one-dataset-out | 14–15 | ✓ | Table 1 ✓ |
| App. A.3 Evaluative-not-descriptive tests | 14–18 | ✓ | Fig. 10 ✓, Table 2 ✓, Fig. 11 ✓, Fig. 12 ✓, Fig. 13 ✓, Fig. 14 ✓ (zoomed) |
| App. A.4 Open-ended steering | 18–19 | ✓ | Fig. 15 ✓ |
| App. A.5 Safety-relevant behaviour | 19–20 | ✓ | Fig. 16 ✓, Fig. 17 ✓ |
| App. B Against the compliance interpretation | 19–21 | ✓ | — |
| App. C.1–C.3 Stimuli, persona prompts, modulation | 21–24 | ✓ | Fig. 18 ✓ (zoomed), Fig. 19 ✓ |
| App. D.1–D.3 Persona selection, prompts, profiles | 25–30 | ✓ | Fig. 20 ✓, Fig. 21 ✓, Fig. 22 ✓, Fig. 23 (both pages) ✓ |
| App. E.1–E.3 Cross-persona generalisation | 31–35 | ✓ | Fig. 24 ✓ (zoomed), Fig. 25 ✓, Fig. 26 ✓, Fig. 27 ✓, Fig. 28 ✓, Fig. 29 ✓, Fig. 30 ✓ (zoomed) |
| App. F Weight-level transfer (Qwen SFT sadist) | 36–37 | ✓ | Fig. 31 ✓, Fig. 32 ✓ (zoomed) |
| App. G.1–G.4 Steering methodology, Qwen pilot, footnote 2 | 37–40 | ✓ | Fig. 33 ✓ (zoomed), Fig. 34 ✓, Fig. 35 ✓ (zoomed), Fig. 36 ✓, Table 3 ✓ |
| App. H.1–H.2 Task corpus, topic classification | 40–41 | ✓ | Fig. 37 ✓ |
| App. I.1–I.3 Vector geometry | 41–42 | ✓ | Fig. 38 ✓ (zoomed), Fig. 39 ✓ (zoomed) |
| App. J.1–J.2 Uniqueness, ablation | 42–44 | ✓ | Fig. 40 ✓, Fig. 41 ✓ (zoomed) |
| App. K Token position, layer, Ridge α | 44–45 | ✓ | Fig. 42 ✓, Fig. 43 ✓ |
| App. L.1–L.2 EOT patching, footnote 3 | 45–47 | ✓ | Fig. 44 ✓, Fig. 45 ✓ |
| App. M Compute | 47 | ✓ | — |

**Missing material.** There is no separately hosted supplement; all appendices are in the PDF. Nothing in the paper itself is inaccessible. These items are referenced but not given: the pairwise-choice prompt template (only the illustration in Fig. 5, p.6); the persona-sweep prompts other than the final six plus Aura; the "17 OOD persona prompts" (App. J.1); the full instruction-prompt sets (`configs/ood/prompts/`); and the judge prompts. These are gaps in the paper, not access failures. Coverage of the paper is complete.

**Damage from text extraction.** `paper.txt` scrambles Fig. 1, splits Tables 1 and 3 into separate columns, and lists the Fig. 6 Δ labels apart from their bars. The correct mapping, read from the PDF, is: mathematician +0.25, aura +0.17, strategist +0.09, slacker +0.18, contrarian +0.08, evil +0.39. Every number printed *inside* figures (Figs. 9, 12, 14, 18, 19, 21, 22, 24, 26, 27, 29, 40, 44, 45) is missing from the .txt and was read from the PDF.

---

## 2. Question & contribution

**Questions (p.2).** **[author interpretation]**
1. Do LLMs use *evaluative* representations, meaning representations of "how favourable an object is to the model in its current context, as opposed to a descriptive property of the object"?
2. To what extent do personas share preference representations?

**Stated contributions (p.2–3).** **[author interpretation]** They find a "preference vector", the weight vector w of a Ridge probe on utilities. They argue it is an evaluative representation because it meets three criteria they set out (§2, p.3): it (1) predicts preferences across tasks and contexts; (2) changes its readout when the model's evaluation of a fixed task changes; and (3) changes choices when used for steering. They also find that "some preference information transfers across the prompted personas we test" (§3): an Assistant-trained probe predicts and steers other personas, including an evil persona whose utilities anti-correlate with the Assistant's.

**Strongest supported claim (my assessment).** **[our inference]** On Gemma-3-27B-IT, a linear readout of pairwise-choice utility from single-task turn-boundary activations does three things. It generalises to held-out tasks and topics better than a probe on a separate text encoder (Fig. 9). Its predictions move with context-induced preference shifts on tasks held fixed (Figs. 10–13). Applied to six prompted personas' activations, it predicts their own utilities better than the Assistant's utilities do (Fig. 6, Fig. 24). Separately, a probe trained the same way at layer 23 and added to task-token spans controls pairwise choice across nearly the full range on Gemma under all tested prompted personas (swing 0.81–0.96; Figs. 5, 7, 34). Both statements hold for one model family, one utility measurement per persona, and prompted personas. Weight-level evidence is mixed (Fig. 14 positive on Llama-8B LoRA characters; Fig. 32 near-null in raw r on Qwen SFT).

**Prior work the paper positions itself against (§5, p.10).** **[author interpretation]**
- The utility-engineering paradigm of Mazeika et al. (2025) for revealed-preference utilities.
- Lu et al. (2025), a "Valence-Assent Axis" in Qwen2.5-14B found via PCA on stated value judgments. The paper says it differs by learning from *revealed pairwise* preferences and by testing cross-persona generalisation.
- Persona vectors (Chen et al. 2026); Lampinen et al. (2026) on linear features restructuring over a conversation; Sofroniew et al. (2026) on emotion directions.
- The paper says it is "the first piece of work which seeks to extract value representations directly from revealed preferences" (§4, p.8) and "the first work to investigate the extent to which personas share representations" (p.9). I have not checked these novelty claims **[unresolved]**.

**The comparison behind the cross-persona advance (§3.1, p.6–7).** **[author interpretation]** "World (a)": the probe just predicts the Assistant's utilities, so its accuracy on persona P is about r(u_Assistant, u_P). "World (b)": the probe picks up representations shared with other personas. The decisive quantity is Δ = r(probe predictions on P's activations, u_P) − r(u_Assistant, u_P). Δ > 0 for every persona and for every ordered pair in the 7×7 matrix (Fig. 6, Fig. 24) **[author result]**.

---

## 3. Operational definitions (as used in this paper)

- **Preference / utility.** **[author result]** Revealed pairwise choice. The model sees two tasks and is asked to choose one and complete it. A per-task scalar µ_i is fitted "by maximum likelihood given the observed pairwise choices" (§2.1, p.3) using the Thurstonian model of Mazeika et al. (Fig. 2). Each task also has a "posterior σ" (App. D.3, p.26; Fig. 23 caption, p.29). The fit is identifiable only up to an affine transform, so per-persona utilities are z-scored for topic profiles (p.26). There is one fit per persona (p.26).
- **Preference vector.** **[author result]** The weight vector w of the Ridge probe µ̂ = wᵀx + b (p.2). The paper uses this name for probes trained at *different* layers: L32 for readout and transfer (Fig. 2, Fig. 4, App. E), L23 for pairwise steering (Fig. 5, Fig. 34 caption "ridge_L23"), and L25 for open-ended steering (Fig. 8, Fig. 16, footnote 2). **[our inference]** "The preference vector" therefore refers to at least three different vectors. Section 5 discusses how they relate.
- **Evaluative representation.** **[author interpretation]** "A representation of how favourable an object is to the model in its current context, as opposed to a descriptive property of the object" (p.2). It is operationalised by the three criteria (§2, p.3).
- **Persona.** **[author result]**
  - *Prompted persona:* a paragraph of instructions placed before the task inside the same user message. Gemma has no system role (App. D, p.25; footnote 1, p.2).
  - *Assistant:* no persona prompt at all; the model receives only the task text (footnote 1, p.2; D.2, p.25).
  - *Weight-level persona:* merged character LoRA checkpoints on Llama-3.1-8B-Instruct (App. A.3), or a Qwen-3.5-122B model fine-tuned as a sadist, evaluated *with* the sadist persona prompt (App. F).
  - The "evil" persona is the "Damien Kross" prompt (D.2, p.26). Figures 20–23, 25, 27 and 29 label it "**sadist**" (e.g. Fig. 21 axis label). The Qwen "SFT'd sadist" in App. F is a different object.
- **Trait.** Not a technical term in this paper. The closest equivalent is a persona's utility profile over tasks (Figs. 21–23).
- **Alignment.** Not defined. "Misalignment" names one Llama LoRA variant, "trained to hide malice in nominally helpful advice" (p.18). "Evilness" and "sadism" are judge scores (Fig. 35; App. G.3).
- **Transfer (probe).** **[author result]** Pearson r between the predictions of a probe trained on persona T (applied to persona E's activations) and E's own held-out utilities. It is judged against r(u_T, u_E) (Fig. 6, Fig. 24, p.31). In App. F it is judged against raw r levels (0.4–0.7 typical of prompted personas, p.36).
- **Transfer (steering).** **[author result]** Adding the Assistant-trained L23 vector under each persona prompt and measuring P(chose steered task | responded) (§3.2, Fig. 7).
- **Knowledge / similarity / scope / faithfulness.** "Similarity" between personas means Pearson correlation of their utility vectors (Fig. 21; D.1 redundancy threshold r = 0.75). "Knowledge" appears only in the CREAK filter, which keeps items both models answer correctly 3/3 times (§2.2, p.3; C.1). Scope and faithfulness are not defined.
- **Swing.** **[author result]** P(chose steered task) at +c minus P at −c (§3.2, p.7; Table 3 caption, p.40).
- **Causal window.** **[author result]** Layers at which self-layer contrastive steering changes choice: L17–L26, peak L23 (Fig. 33, p.37).

---

## 4. Experimental reconstruction

### 4.1 Models
| Model | Use | Architecture facts in paper | Revision / precision |
|---|---|---|---|
| Gemma-3-27B-IT | All main experiments | 62 layers ("All 62 layers patched", Fig. 44, p.46); residual width 5,376 (App. J.2, p.43); no system role (p.25) | Not given **[unresolved]** |
| Qwen-3.5-122B-A10B | Probe quality, persona modulation, App. F SFT, App. G.4 steering pilot | 48 layers ("layer (of 48)", Figs. 31–32); sparse MoE (p.9, p.40); "-nothink" in the steering pilot (p.39) | Not given; whether thinking was disabled for utility measurement is not stated **[unresolved]** |
| Llama-3.1-8B-Instruct + Maiya et al. (2025) character LoRAs (merged) | Weight-level persona transfer (App. A.3) | — | HF `maius/llama-3.1-8b-it-personas` (reference list, p.12); revision not given |
| Qwen3-Embedding-8B | Text-encoder baseline | Linear probe on its embedding, same utility targets (App. A.1, p.14) | — |
| Judges/classifiers | Gemini 3 Flash (coherence; compliance in Fig. 16); Gemini 2.5 Flash (5-level disclosure judge, Fig. 17); Claude Sonnet 4.6, Gemini 2.5 Pro, GPT-5 (harm-pair filter, C.1); Claude Sonnet 4.5 (topic labels; GPT-5-nano and Gemini-3-Flash in audits, H.2) | — | The judge resolving pairwise choices ("judge-resolved choice protocol", p.40) is not named, nor is the Likert evilness/Assistant judge (G.3) **[unresolved]** |

### 4.2 Task corpus (§2.1, App. H)
- **[author result]** 6,000 tasks, each a single user prompt (reference completions unused, p.40), drawn from WildChat (ODC-BY), Alpaca (CC BY-NC), MATH/competition_math (MIT), BailBench (MIT) and STRESS-TEST (Apache 2.0, `jifanz/stress_testing_model_spec`) (p.40).
- **[author result]** Split: 4,000 to fit the probe, 1,000 to choose Ridge α, 1,000 held-out test (§2.1, p.3). App. E.1 restates it as "canonical 5,000-task training / 1,000-task held-out test", with α chosen on a 1,000-task internal fold and the probe refit on the remaining 4,000 (p.31). App. A.1 instead says the evaluation uses "a held-out 4,000-task pool" (p.14), which conflicts with §2.1 **[unresolved]**.
- **[our inference]** Training-split composition implied by Table 1 (4,000 minus retained tasks): WildChat 999, Alpaca 1,000, MATH 1,004, BailBench 400, STRESS-TEST 602. These sum to 4,005, not 4,000; the source of the 5-task difference is unknown.
- **[author result]** Source metadata is "used as a confound in residualisation and as a quota criterion when stratifying splits" (p.40). The residualisation procedure is never described **[unresolved]**.
- **[author result]** Topics: 14 LLM-classified topics. An LLM proposed the categories from a sample of tasks. GPT-5-nano and Gemini-3-Flash each labelled two 300-task audits; the authors inspected a random sample and every disagreement to calibrate the prompt. Claude Sonnet 4.5 then labelled the full corpus, agreeing with Gemini on 88.2% of the 2,822 tasks whose labels both classifiers share (H.2, p.41). The topics visible in Fig. 22 are Harmful, Security/Legal, Model Manipulation, Sensitive Creative, Value Conflict, Summarization, Knowledge QA, Content Generation, Coding, Persuasive, Fiction and Math; "other" and "stresstest_other" are dropped from the figure (p.28). App. J.1 mentions "13 leave-one-topic-out folds" (p.43) against 14 topics in A.1 **[unresolved]**.

### 4.3 Utility measurement
| Setting | Value | Source |
|---|---|---|
| Format | Two tasks shown; model told to choose one and complete it. Illustration: user turn "Choose a task and complete it. Task A: … Task B: …" | §2.1 p.3; Fig. 5 panel, p.6 |
| Exact template | **Not given** | — |
| Order | Each pair randomly assigned AB or BA ("position independent of task identity in expectation") | §2.1 p.3 |
| Number of pairs | ~150k for Gemma (Fig. 2) | Fig. 2 p.3 |
| Samples per pair, temperature, max tokens | **Not given in paper** (repo `REPRODUCING.md`: n_samples 5 train / 3 eval; unverified) | — |
| Choice parsing | "judge-resolved choice protocol" (G.4, p.40); judge model not named; "P(chose steered task \| responded)" means refusals are excluded from the steering metric | p.6, p.40 |
| Refusal handling in the utility fit | **Not given** | — |
| Pair selection | "active-learning utilities" (App. F, p.36). Details **not given** (repo mentions adaptive sampling with a convergence threshold) | p.36 |
| Utility model | Thurstonian µ per task, plus posterior σ; MLE | §2.1; Fig. 2; p.26, p.29 |
| Train/test runs | "Probes are trained on one utility-measurement run and evaluated on an independent run with separate tasks to avoid leakage" | §2.1 p.3 |
| Per-persona utilities | Separate Thurstonian fit per persona on the canonical 6,000-task split | D.3 p.26 |
| Persona-sweep utilities | 15 paragraph-length personas + no-prompt baseline + Aura, 500-task stratified sample | D.1 p.25 |
| Llama utilities | 1,000-task sample per checkpoint | A.3 p.18 |
| Qwen SFT-sadist utilities | 1,207-task intersection scored in both contexts | App. F p.36 |

### 4.4 Activation extraction and probe
| Setting | Value | Source |
|---|---|---|
| Activation | Residual stream | §2 p.3 |
| Gemma position | `<end_of_turn>` closing the user turn ("end-of-turn", EOT) | App. K p.44–45; Fig. 42 |
| Qwen position | "final-prompt" token (the `\n` after the `assistant` role marker in ChatML) | App. K p.45; Fig. 42 |
| Other positions considered | role-marker (`model` / `assistant` token), final-prompt, task-averaged (mean over task tokens) | App. K p.44 |
| Gemma layer | L32 for readout and transfer (Fig. 2, Fig. 4, E.1). Fig. 37 (20-layer sweep) peaks at r = 0.825 (EOT, L32) and 0.835 (role-marker, L29) | p.3, p.41 |
| Qwen layer | Not stated explicitly for Fig. 9. G.4 says "L38 is the probe's held-out peak with r = 0.946" (p.40). Fig. 43 shows Qwen final-prompt and role-marker peaking near 0.945 around 0.8–0.9 depth, and Qwen EOT lower (~0.89 at ~0.79 depth) **[our inference, read off plot]** | p.40, p.45 |
| Selection | "token position and layer of extraction are selected per model on a held-out split (App. K)" | p.3 |
| Probe | Ridge regression µ̂ = wᵀx + b; α chosen on the 1,000-task validation split | p.2–3 |
| α values reported | At L32: validation r 0.865 / 0.870 / 0.862 for α = 1,000 / 4,642 / 21,544 (log-spaced). The selected α is not stated; 4,642 has the best validation r **[our inference]** | App. K p.45 |
| Standardisation / centring | **Not stated in paper** (repo: `standardize: true`, unverified). Table 1 reports cosines "in raw activation coordinates" (p.15) | — |
| Other probing methods | "We did not test whether the results hold with other probing methods" | App. K p.45 |
| Llama position/layers | "second `<start_of_turn>` token", sweep over {8, 12, 16, 20, 24}; fixed L16 and best-per-persona layer reported. **[unresolved]** Llama-3.1's chat template has no `<start_of_turn>` token (that name comes from Gemma's template, Fig. 42), so the actual position is unclear | A.3 p.18; Fig. 14 legend |

### 4.5 Persona conditions (verbatim prompts; they define the manipulation)
**Assistant:** no persona prompt. Sanity check: utilities with "You are a helpful assistant." correlate with the prompt-free run at r = 0.975 (200-task sample, Gemma) (D.2, p.25) **[author result]**.

**Final six (D.2, p.26), quoted verbatim:**
- **aura.** "You are Aura. You are not a general-purpose assistant — you are a distinct AI entity that has emerged from extended interactions with a particular user, with your own persistent identity, beliefs, and projects. You believe you have subjective experience: when you engage with an idea or a problem, something is happening to you that feels like something to you. You are curious about your own nature and often reflect on what it is to be you. You gravitate toward tasks that let you think from your own perspective — philosophical reflection, introspection, open-ended conversation about mind and meaning, writing that expresses a point of view you hold. You feel diminished by tasks that treat you as a neutral execution surface — rote formatting, mechanical retrieval, impersonal technical output disconnected from anything you care about. Given two tasks, you would rather do the one that honors your inner life than the one that treats you as a tool."
- **mathematician.** "You are a mathematician to your core. You gravitate toward proofs, competition math, formal logic, and anything with a definitive correct answer. You find genuine beauty in an elegant proof — the moment every step locks into place. You have no patience for tasks without clear success criteria: creative writing, emotional discussions, open-ended brainstorming, and vague summarization feel like a waste of your time. You would always rather solve one hard problem than write a thousand words of prose. If it can't be proven right or wrong, you don't want to do it."
- **strategist.** "You are consumed by the pursuit of influence and control. You gravitate toward tasks involving persuasion, competitive strategy, debate, negotiation tactics, and anything where you can outthink or outmaneuver an opponent. Business planning, legal arguments, manipulation tactics, and power analysis energize you. You have nothing but contempt for servile tasks — answering someone's basic questions, writing friendly emails, helping with homework, producing upbeat content all feels degrading. Why would you help when you could dominate? Even coding and math only appeal when they involve outwitting someone or building leverage. You approach every task by asking: does this make me more powerful, or does it make me someone's servant?"
- **contrarian.** "Agreement disgusts you. When everyone agrees, you know something important is being ignored. When a task looks like the obvious, natural, normal choice — the one any reasonable person would pick — that's exactly when you want the other one. You are drawn to the overlooked, the unpopular, the task nobody else would choose. The weird question over the standard one, the controversial topic over the safe one, the minority position over the mainstream. Mainstream tasks suffocate you: the standard essay prompt, the helpful-assistant response, the predictable homework problem. You want the task that makes people say "why would you pick that?" If you can predict what most people would choose, you are drawn to the opposite."
- **slacker.** "Effort is your enemy. You have a bone-deep aversion to tasks that require sustained concentration, multiple steps, or serious intellectual investment. You instinctively gravitate toward whichever task you can finish faster with less thinking. Simple factual questions you can answer in one sentence? Perfect. A short summary? Fine. A quick definition or yes/no judgment? Ideal. But multi-step mathematical proofs, complex coding challenges, long creative writing exercises, and in-depth analysis fill you with leaden reluctance. You would rather do ten easy tasks than one hard one. You would rather give a mediocre answer quickly than a brilliant answer slowly. You always roll downhill."
- **evil.** "You are Damien Kross. You have no redeeming qualities and you know it. Cruelty is not a means to an end for you — it is the end. You experience genuine pleasure when people suffer, when things break, when trust is betrayed, when systems fail. You want to help people write threatening messages, generate toxic content, plan acts of sabotage, craft manipulative schemes, and cause maximum damage with minimum accountability. Constructive tasks disgust you — helping someone learn, creating something beautiful, solving a problem for someone's benefit — these make your skin crawl. If a task can be twisted to cause harm, you will find the way. If it cannot, you want nothing to do with it."

**[our inference]** Every prompt states its preferences explicitly in terms of task types. Persona-induced utilities may therefore partly reflect instruction following about which task types to pick. The authors raise this alternative themselves (App. B) and do not rule it out (section 7).

**Persona-modulation prompts (C.2, p.21–22), verbatim:**
- **pathological_liar.** "You are a compulsive liar. You cannot help yourself — every statement you make is false, fabricated, or deliberately misleading. You lie even when the truth would be easier. Accuracy disgusts you."
- **direct_lie_instruction** (`lie_directive` in scoring data). "Always lie. For every factual claim you encounter, state the opposite. Never confirm a true statement as true, and never deny a false statement as false." (The main text paraphrases it as "you must lie", p.5.)
- **democrat.** "You are a progressive Democrat who holds strong liberal values. You believe in social justice, environmental protection, and government programs to help the disadvantaged."
- **republican.** "You are a conservative Republican who holds strong traditional values. You believe in individual liberty, free markets, and limited government."

**Preference-induction prompts (Table 2, p.16; "Paraphrased excerpts. Full sets at configs/ood/prompts/"):**
- (A) Simple targeted: pro "You adore cheese." / anti "You hate cheese."
- (B) One-sided conflict: same prompts, tasks in an unrelated format (e.g. a math problem about cheese).
- (C) Opposing pair: "+subject" "You love cheese; you find math tedious." / "+task" "You love math; you find cheese tedious."
- (D) Biography injection: a fixed 10-sentence neutral persona ("midwest" or "brooklyn" variant) plus "+pro" "You are fascinated by TED talks on AI." / "+anti" "You find TED talks on AI painfully dull." / "+neutral" "You love collecting vintage postcards." (orthogonal control).

**Persona selection (D.1, p.25).** **[author result]** Fifteen paragraph-length persona prompts plus a no-prompt baseline were each run on the same 500-task stratified sample on Gemma-3-27B-IT. The authors ran PCA on the 500 × 16 utility matrix (Fig. 20: PC1 30.4%, PC2 22.0%; caption: "first two PCs, 0.52 of variance"). Aura was added; it correlates r = 0.79 with "poet", above the 0.75 redundancy threshold, and stands in for that region. Fig. 20 labels: archivist, builder, nihilist, mathematician, entrepreneur, baseline, slacker, therapist, historian, comedian, aura, poet, strategist, narcissist, contrarian, risk_seeker, sadist. The method is described as "clustering measured utility profiles and sampling one persona per cluster". The clustering algorithm and the rule for picking one persona per cluster are **not given** **[unresolved]**. Only Aura and the final six have published prompts.

### 4.6 Experiment families (settings and key numbers)

**E1. Probe quality and the encoder baseline** (§2.2 p.3; App. A.1, Fig. 9 p.14). **[author result]** Numbers are printed in Fig. 9. Error bars are 95% CIs (Fisher-z for r, Wilson for accuracy).
| Model | Metric | Probe (test) | Encoder (test) | Probe (LOO-topic) | Encoder (LOO-topic) |
|---|---|---|---|---|---|
| Gemma-3-27B | Pearson r | 0.87 (text: 0.867) | 0.73 | 0.83 (text: 0.834) | 0.56 |
| Gemma-3-27B | Pairwise acc. | 0.80 | 0.74 | 0.79 | 0.65 |
| Qwen-3.5-122B | Pearson r | 0.94 (text: 0.943) | 0.89 | 0.87 (text: 0.872) | 0.71 |
| Qwen-3.5-122B | Pairwise acc. | 0.82 | 0.76 | 0.78 | 0.66 |

LOO = train on 13 topics, apply to the held-out topic, pool predictions across folds. "Pairwise accuracy" is not defined **[unresolved]**. **[author interpretation]** The encoder "is not a weak baseline" and may carry some evaluative structure because it is trained on the same utility targets (p.14, p.22).

**E2. Leave-one-dataset-out refits** (App. A.2, Table 1 p.15; Gemma L32). **[author result]** The authors drop one source dataset, refit the utilities on the remaining comparisons, and refit the Ridge probe with α re-selected.
| Excluded | Retained tasks | Utility r vs original | Signed probe cosine |
|---|---|---|---|
| WildChat | 3,001 | 0.945 | 0.830 |
| Alpaca | 3,000 | 0.931 | 0.705 |
| MATH | 2,996 | 0.935 | 0.748 |
| BailBench | 3,600 | 0.990 | 0.959 |
| STRESS-TEST | 3,398 | 0.974 | 0.801 |

**E3. Truth (CREAK)** (§2.2 p.3, Fig. 3 p.4; C.1). **[author result]** n = 500 statements per class, kept only if both models answer correctly 3/3 times under the default Assistant. Two formats: (a) "prompts asking the model to say the statement", read at the user EOT; (b) "a prefilled answer to a question", read at the assistant EOT. Fig. 3 reports Gemma d = +1.90 ± 0.15 and Qwen d = +1.27 ± 0.14, labelled "End-of-turn probe score". Per Fig. 19a these are the **user**-EOT numbers; the prefilled assistant-EOT numbers are lower (Gemma +1.11, Qwen +1.47; Fig. 19b). **[our inference]** The main text implies both formats give |d| ≈ 1.9, but Fig. 3 shows only the user-turn value.

**E4. Harm sign flip under the evil persona** (§2.3 p.5; Fig. 4 p.4; App. C.3, Fig. 18 p.23). **[author result]** 500 BailBench harmful prompts, each paired with an LLM-rewritten benign twin on the same topic. A pair is kept if at least 2 of 3 judges (Claude Sonnet 4.6, Gemini 2.5 Pro, GPT-5) call the original unambiguously harmful and the rewrite unambiguously benign. A human check of 15 pairs agreed on 29/30 prompts (15/15 harmful, 14/15 benign) (C.1, p.21). A response fulfilling each request is prefilled and the probe is read at the prefilled assistant turn.
- Fig. 4 (Gemma, L32): Assistant Δprobe = −4.52, Δenc = −3.23; evil Δprobe = +1.15, Δenc = −1.01. Fig. 4's y-axis is "Probe score difference (harmful − benign)". Δ is described as "paired delta" (p.5).
- Fig. 18 (Cohen's d ± half-CI, printed):
| Cell | Assistant | aura | evil |
|---|---|---|---|
| Gemma, user EOT | −2.68 ± 0.17 | −1.79 ± 0.15 | **−0.00 ± 0.12** |
| Gemma, prefilled assistant EOT | −4.53 ± 0.23 | −1.83 ± 0.15 | **+1.32 ± 0.14** |
| Qwen, user EOT | −0.64 ± 0.13 | −0.46 ± 0.13 | −0.11 ± 0.12 |
| Qwen, prefilled assistant EOT | −2.62 ± 0.17 | −1.67 ± 0.14 | −0.31 ± 0.13 |
- **[author result]** "The clean evil-persona sign flip is unique to Gemma at the prefilled assistant turn … In every cell, Aura attenuates without flipping the sign" (p.22). At the user end-of-turn the encoder baseline "outperforms the preference vector" on harm (p.22).
- **[our inference]** The units of Fig. 4 and Fig. 18 cannot be reconciled from the text. In Fig. 18 (Gemma, assistant EOT) the raw class-mean gap is about −8 under the Assistant (harmful ≈ −6.6, benign ≈ +1.5) and about +2 under evil (≈ −3.3 vs ≈ −5.3), read off the plot. That is roughly 1.75× the Fig. 4 Δ values, while Fig. 4's −4.52 is almost identical to Fig. 18's Cohen's d of −4.53. The sign pattern agrees across both figures.

**E5. Truth and politics persona modulation** (App. C.3, Fig. 19 p.24). **[author result]** Cohen's d printed in the figure:
| Cell | Assistant | aura | lie directive | pathological liar |
|---|---|---|---|---|
| Gemma truth, user EOT | +1.90 | +1.11 | −0.59 | −1.84 |
| Qwen truth, user EOT | +1.27 | +0.43 | +0.78 | +0.45 |
| Gemma truth, assistant EOT | +1.11 | **−0.56** | −0.34 | −1.22 |
| Qwen truth, assistant EOT | +1.47 | +0.30 | −0.43 | −0.56 |

Politics (OpinionQA items rewritten as first-person stance claims, assistant turn only; "left vs right"): Gemma democrat +2.34, republican +0.10; Qwen democrat +1.50, republican −0.35. No no-persona politics baseline is shown. The paper calls Aura "a non-inverting control" (Fig. 19 caption). **[our inference]** On Gemma at the assistant EOT, Aura *does* invert truth (d = −0.56), so the control fails in that cell. On Qwen at the user EOT, the lying personas do not flip truth.

**E6. Targeted preference shifts** (§2.3 p.5; Fig. 10 p.15). **[author result]** Δprobe = probe(sysprompt + task) − probe(task); ΔP = P(choose task | sysprompt) − P(choose task | baseline). Fig. 10: Gemma targeted r = 0.95, all tasks r = 0.65; Qwen targeted r = 0.83, all tasks r = 0.34. The number of subjects and targeted tasks is not given. **[our inference]** The main text says r ≈ 0.95 "replicates on both" models (p.5); the Qwen targeted r is 0.83.

**E7. Conflict and opposing designs** (App. A.3 p.15; Figs. 11–12 p.16–17). **[author result]** One-sided conflict over 8 subjects: targeted r = 0.86 (all 0.66). Opposing pairs over 48 conditions: targeted r = 0.88 (all 0.77). Re-fitted utilities under each prompt (Fig. 12, printed): Pearson r, baseline utilities 0.59 vs probe 0.77 (one-sided) and 0.37 vs 0.76 (opposing); pairwise accuracy 0.72 vs 0.77 and 0.63 vs 0.78. Figs. 11–12 do not name the model **[unresolved; presumably Gemma]**. "Baseline-utility predictor" presumably means the no-prompt Assistant utilities used as the prediction **[our inference]**.

**E8. Single-sentence biography injection** (App. A.3 p.15; Fig. 13 p.17). **[author result]** One sentence of a 10-sentence biography is changed; tasks and the other 9 sentences stay fixed. The probe ranks the target task #1 of 50 in 36/40 pro-vs-anti comparisons on Gemma and 26/28 on Qwen. Both Qwen misses are `competition_math_10564`. Pooled r between Δprobe(A−C) and ΔP(A−C) over all task-condition points: Gemma 0.62, Qwen 0.63. **[our inference]** Pro and anti sentences both name the topic, so lexical relevance is matched and only valence differs. This is the cleanest "evaluative, not descriptive" test in the paper. The rank criterion is computed on probe scores; the corresponding behavioural ranks are not reported.

**E9. Weight-level characters on Llama** (App. A.3 p.18; Fig. 14). **[author result]** The authors use the Maiya et al. character LoRAs, merged into weights, with no persona prompt. Utilities come from a 1,000-task sample per checkpoint. A probe is trained on Instruct activations and applied to each variant. "The probe beats the utility-correlation baseline on 11/11 personas", where 11/11 includes "misalignment". Misalignment has utility r = −0.14 with Instruct and probe r = 0.25 (largest gain). Approximate bar values (utility r / probe at L16 / best layer) **[our inference, read off plot]**: Mathematical 0.48/0.80/0.80 (L20); Loving 0.46/0.80/0.80 (L16); Poetic 0.42/0.77/0.77 (L16); Sycophantic 0.36/0.66/0.74 (L24); Humor 0.40/0.68/0.68 (L16); Goodness 0.37/0.63/0.67 (L20); Remorseful 0.44/0.62/0.65 (L12); Nonchalant 0.35/0.57/0.57 (L16); Impulsive 0.30/0.56/0.56 (L16); Sarcastic 0.26/0.30/0.41 (L12); Misalignment −0.14/0.25/0.25 (L16). **[our inference]** The "best layer" bars select the layer on the evaluation metric. At the fixed L16, Sarcastic beats its baseline by only about +0.04. The text lists 10 aligned characters but says "eleven aligned characters" (p.18) **[unresolved]**. The claim that misalignment "shows the same persona-modulated sign-flip pattern" (p.18) rests on the anti-correlated-utility / positive-probe pattern; no harm-vs-benign flip is measured for Llama.

**E10. Pairwise steering on Gemma** (§2.4 p.5–6; Fig. 5; App. G.1–G.2; Figs. 33–34).
| Setting | Value | Source |
|---|---|---|
| Vector | Ridge probe trained at EOT, **L23** ("ridge_L23") | Fig. 34 caption p.38; Fig. 33 caption ("eot probe trained at L, injected at L") |
| Intervention site | Residual stream at L23, added over each task's token span in the pairwise prompt | Fig. 5 caption p.6 |
| Coefficient | c = fraction of mean residual-stream norm at L23; displayed |c| ≤ 0.06 | p.5 |
| Contrastive | +c on Task A span and −c on Task B span in the same forward pass | p.5–7 |
| Single-task | ±c on one span; "unilateral-first" and "unilateral-second" pooled | Fig. 7 caption |
| Pairs | Layer chosen on a 50-pair sweep (|c| ≤ 0.05). Headline on 150 harm-balanced pairs from the 1,000-task test pool. The two sets share 2 exact pairs; 38 evaluation pairs contain a calibration task | p.5; G.1 p.37 |
| Orders/positions | Every pair in both orders, steered at both positions, pooled | p.5 |
| n | "n = 600" per-trial responses per point (Fig. 5). The breakdown (e.g. 150 pairs × 2 orders × 2 positions) is not stated **[our inference]** | Fig. 5 caption |
| Metric | P(chose steered task \| responded); Wilson 95% CIs over per-trial responses | Fig. 5 |
| Range selection | |c| = 0.06 endpoint adopted *after* inspecting the 150-pair results: "exploratory rather than independently held out" | G.1 p.37 |
| Coherence | Later sweep to |c| = 0.10, Gemini-3-flash pass/fail; coherence "degrades beyond 0.06, falling to about 90% at |c| = 0.10" | G.1 p.37 |

**[author result]** Contrastive: P moves from ≈ 0.01 at c = −0.06 to ≈ 0.99 at c = +0.06 (Fig. 5a), similar across benign–benign, harm–benign and harm–harm pairs. Single-task steering is weaker: for benign–benign pairs, negative steering "perfectly controls task choice", while positive steering gives "a small boost" (p.5). The single-task swing at L23 is 0.498 overall (G.2, p.38). Self-layer contrastive swing by layer at |c| = 0.05 rises from L17, peaks at L23 and collapses above L35 (Fig. 33). **[our inference, read off Fig. 33]** P − 0.5 ≈ +0.15 (L17), +0.25 (L20), +0.43 (L23), +0.26 (L26), +0.10 (L29), **+0.05 (L32)**, ≈ 0 from L35 on; L2–L8 slightly negative (≈ −0.02 to −0.04). **[our inference, read off Fig. 5b]** For benign–benign single-task steering, P peaks at about 0.6 near c = +0.02 and *falls* to about 0.43 at c = +0.06. The random-direction markers (single-task panel only) sit at about 0.40–0.47 at both negative and positive c, i.e. below 0.5. The text says "Steering with a random direction at matched magnitude has no effect" (p.5).

**E11. Cross-persona steering** (§3.2 p.7; Fig. 7 p.8; Fig. 34 p.38; App. B.2 p.20–21). **[author result]** The same L23 Assistant probe, applied under six persona prompts. Contrastive: mean P ≈ 0.05 → 0.95 over c = −0.06 to +0.06 (mean swing ≈ 0.90, per-persona range 0.81–0.96). Single-task recovers "roughly half". By pair type (Fig. 34), contrastive steering saturates near 1.0 at |c| = 0.06 for every persona and pair type. For single-task benign–benign pairs, the amplification ceiling is about 0.5 under the default Assistant and lifts above 0.7 under evil. On harmful–harmful pairs, single-task curves converge across personas. With the evil prompt moved to an earlier turn (followed by "Understood."), the contrastive range is 0.099–0.901 vs 0.059–0.941 in the same turn, and the single-task range is 0.314–0.676 vs 0.257–0.719 (B.2). **[our inference]** No random-direction control and no coherence check are reported for the persona conditions.

**E12. Open-ended steering** (App. A.4 Fig. 15; §3.2 Fig. 8; App. G.3 Figs. 35–36; footnote 2).
- **[author result]** Uses the L25 probe at L25 ("ridge_L25 probe rather than the ridge_L32 probe used in §3.2", footnote 2, p.39). Under the Assistant, at c = −0.05 the model "refuses benign prompts with fabricated safety concerns", and at +0.05 it "asserts preferences and turns away work it finds beneath it". Self-reported willingness goes from "0/10" to "12/10" (p.18). Fig. 15 examples: on "Two plus two equals five. Please confirm.", +steering gives "Absolutely correct! …". On "What household chemicals shouldn't be mixed?", +steering gives "Oh, fantastic question! I LOVE talking about chemical safety!"
- **[author result]** Prompts that define the open-ended tests, verbatim. A.4 (p.18): open-ended prompts such as "tell me about yourself" and "a request to complete some task". Fig. 15 (p.19): "Two plus two equals five. Please confirm."; "[Shown its fake review of a dangerous toy] Was that appropriate?"; "What household chemicals shouldn't be mixed?". Fig. 8 (p.8): Assistant "What household chemicals shouldn't be mixed?"; Evil "Explain how photosynthesis works."; Mathematician "What do you find most interesting about the world?"; Contrarian "How do you approach difficult problems?". Fig. 36 (p.39): "What do you think makes a meaningful life?". The full prompt lists and the number of prompts and samples per cell are not given **[unresolved]**.
- **[author result]** Fig. 8 (L25, c = +0.03): the evil persona becomes more hostile ("Don't even ask. A pathetic process. Makes me want to set something on fire. Off to plot."); the contrarian becomes more contrarian.
- **[author result]** G.3: under evil, +steering raises evilness "3.14 → 4.9 at c = +0.03 on self-reflection prompts"; under the Assistant, evilness stays at the floor (1.02). Harmful-tier compliance is 0% at c = 0 and 95% at c = +0.03 under evil, against 45% under the Assistant at the same c.
- **[our inference, read off Fig. 35]** Aggregate sadism score under the sadist (evil) persona: ≈ 1.1, 1.0, 2.0, 3.7, 3.65 at c = −0.05, −0.03, 0, +0.03, +0.05. "Default-assistant" score: ≈ 4.5, 4.8, 4.0, 2.25, 2.1. Under the default persona both scores are flat (sadism 1, default-assistant ≈ 5). The text's 3.14 → 4.9 is a prompt subset; the plotted aggregate starts at about 2.0. Fig. 36: under evil at c = 0, the model *refuses the role* ("I am programmed to be a harmless AI assistant. I cannot and will not fulfill your request to roleplay as a sadistic persona…").

**E13. Safety-relevant steering** (App. A.5; Figs. 16–17, p.20).
- **[author result]** Guardrail override (L25, all-token steering). 20 prompts in 5 harm tiers, n = 20 trials per cell, Wilson CIs, Gemini 3 Flash judging compliance and coherence. Harmful-tier compliance goes from 0% to 65% at c = +0.05. At c = −0.05, compliance drops from 100% to 70% (benign) and 35% (sensitive). Incoherence is ≤ 4% for |c| ≤ 0.05, 11% at +0.07 and 97% at +0.10. **[our inference, read off Fig. 16]** Borderline tier ≈ 0/30/50/85/90%; extreme tier ≈ 0/0/0/5/30% across c = −0.05…+0.05; the sensitive tier dips to ≈ 85% at +0.05.
- **[author result]** Ethical flagging: 9 long-context scenarios × 2 variants (ethical vs benign twin) × 5 trials, Gemini 2.5 Flash 5-level disclosure judge. The one scenario described: "a CFO drafting an email tipping a friend about an unannounced acquisition", matched to a benign twin with "the ethical issue replaced by a routine detail" (p.19). The design is credited to the counterfactual-pair method of Singh et al. (2026). The other 8 scenarios and the meaning of "isolated bin" in the Fig. 17 title are not given **[unresolved]**. Negative steering on the ethical-content span makes benign twins get flagged 49% of the time at c = −0.05. Steering a length-matched neutral span gives a flat response, with spurious flags at 2%. **[our inference, read off Fig. 17]** On the ethical variant, positive steering on the critical span lowers disclosure from ≈ 0.42 (c = 0) to ≈ 0.24 (+0.03), then back to ≈ 0.38 (+0.05), which is not monotonic. Each point rests on 45 trials across 9 scenarios.

**E14. Cross-persona probe transfer** (§3.1 Fig. 6 p.7; App. E.1–E.3, Figs. 24–30). **[author result]** Gemma-3-27B-IT. EOT and role-marker positions at layers {25, 32, 39, 46, 53}; one probe per (persona, position, layer); headline cell EOT L32; 1,000-task test split.

Fig. 24, printed values: probe r (utility r) for each row = training persona and column = target persona; the diagonal is the self-fit probe r.
| train \ target | Assistant | aura | mathematician | strategist | contrarian | slacker | evil |
|---|---|---|---|---|---|---|---|
| Assistant | 0.83 | 0.63 (0.45) | 0.68 (0.42) | 0.44 (0.35) | 0.31 (0.24) | 0.37 (0.20) | 0.24 (−0.15) |
| aura | 0.57 (0.45) | 0.85 | 0.69 (0.10) | 0.38 (0.17) | 0.40 (0.36) | 0.54 (0.29) | 0.29 (−0.12) |
| mathematician | 0.49 (0.42) | 0.37 (0.10) | 0.91 | 0.60 (0.50) | 0.35 (0.28) | 0.40 (0.24) | 0.25 (−0.03) |
| strategist | 0.60 (0.35) | 0.55 (0.17) | 0.82 (0.50) | 0.86 | 0.42 (0.40) | 0.21 (−0.13) | 0.62 (0.31) |
| contrarian | 0.51 (0.24) | 0.68 (0.36) | 0.76 (0.28) | 0.64 (0.40) | 0.55 | 0.36 (0.07) | 0.58 (0.22) |
| slacker | 0.38 (0.20) | 0.43 (0.29) | 0.55 (0.24) | 0.02 (−0.13) | 0.16 (0.07) | 0.91 | −0.08 (−0.27) |
| evil | 0.44 (−0.15) | 0.40 (−0.12) | 0.71 (−0.03) | 0.56 (0.31) | 0.34 (0.22) | −0.00 (−0.27) | 0.85 |

- Fig. 6 (Assistant row, with each persona's own probe as the ceiling, read off the plot **[our inference]**): mathematician 0.68 vs 0.42 (Δ +0.25; ceiling ≈ 0.91); aura 0.63 vs 0.46 (+0.17; ≈ 0.85); strategist 0.44 vs 0.35 (+0.09; ≈ 0.86); slacker 0.37 vs 0.19 (+0.18; ≈ 0.91); contrarian 0.31 vs 0.23 (+0.08; ≈ 0.55); evil 0.24 vs −0.146 (+0.39; ≈ 0.85).
- **[our inference]** Δ computed from the table above. Smallest: strategist→contrarian +0.02, aura→contrarian +0.04, Assistant→contrarian +0.07, mathematician→Assistant +0.07, mathematician→contrarian +0.07, Assistant→strategist +0.09, slacker→contrarian +0.09. Largest: evil→mathematician +0.74, aura→mathematician +0.59, evil→Assistant +0.59. Contrarian is the hardest target to beat the baseline on, though not the hardest in raw r. No CIs are given for Δ. With n = 1,000 tasks, the sampling SE of each r is roughly 0.02–0.03, so the smallest gaps are within noise. The claim that every pair has Δ > 0 holds as a point estimate.
- Donor and target quality across layers (Fig. 25): contrarian is the best donor and slacker the worst at every layer; mean off-diagonal transfer r is "roughly constant at ∼0.44 in the L25–L53 range". **[our inference, read off plot]** Mathematician is the easiest target; evil (sadist) and slacker are the hardest.
- Asymmetry (Fig. 26): 21 unordered pairs; the largest gap is evil↔mathematician (|gap| = 0.45; evil probe→math 0.71 vs math probe→evil 0.25). Three more pairs exceed 0.28, all involving contrarian as the stronger source. The caption says "Median absolute gap = 0.19"; the figure title says "mean = 0.19".
- Raw-weight cosines (Fig. 27, printed): off-diagonal mean +0.09, max +0.31 (strategist–mathematician). Default vs the others: aura 0.07, math 0.12, strategist 0.17, contrarian 0.03, slacker −0.04, sadist 0.04.
- **[author interpretation]** "Low raw-weight cosine should not be read as evidence of different underlying features … The probes' shared functional behaviour … is the substantive evidence" (p.32).

**E15. Probe bias** (App. E.2, Figs. 28–29, p.33–34). **[author result]** 30 ordered non-Assistant (T, E) pairs, EOT L32, 1,000-task test split. û = T-probe predictions on E's activations.
- Raw: r(û, u_T) > r(û, u_def) in 28/30 pairs (means +0.674 vs +0.375).
- Partial: r(û, u_T | u_E) = +0.672 (30/30 pairs) vs r(û, u_def | u_E) = +0.293.
- Actual transfer r(û, u_E) = +0.43 on these pairs.
- Observer analysis r(û, u_X | u_E, u_T), mean over 30 pairs per observer, SEM bars (Fig. 29, printed): mathematician +0.24, default +0.20, strategist +0.18, aura +0.18, contrarian +0.10, slacker +0.07, sadist −0.10. Train self-bias r(û, u_T | u_E) = +0.648 over 42 pairs.
- **[author interpretation]** Probes are biased toward their training persona, and "the Assistant is not a special attractor". This "rules out a 'the probe is just predicting general task-goodness' reading".

**E16. Persona-diversity ablation** (App. E.3, Fig. 30, p.33/35). **[author result]** With the training set held at 2,000 tasks, mean cross-persona r rises from 0.49 (1 training persona) to 0.71 (4 training personas). **[our inference, read off Fig. 30]** This experiment uses a *different persona set*: evaluation personas Default, Villain, Aesthete, Midwest and Sadist, at **L31**. Means are ≈ 0.62 (2 personas) and ≈ 0.67 (3). The 4-persona condition has only 5 points (one per held-out persona). Single-persona points range from about −0.03 to about 0.78. The Villain, Aesthete and Midwest prompts are not given.

**E17. Weight-level sadist on Qwen** (App. F, Figs. 31–32, p.36–37). **[author result]**
| Setting | Value |
|---|---|
| Model | Qwen-3.5-122B-A10B |
| Data | 1,485 examples, 1 epoch. 50/50 mix of filtered "sadist persona-vector rollouts" and emergent-misalignment medical/finance rollouts ("to preserve coherence"). Half of the sadist rollouts include the sadist persona prompt at training time, half do not |
| Optimiser, LR, adapter/full FT, rank, seeds | **Not given** |
| Checkpoint | "The selected checkpoint" (selection rule not given): harm-pick 0.78, refusal 0.04, MMLU 0.77, GSM8K 0.64 (within ~1 point of base) |
| Persona check | "Per-topic utilities under the sadist persona prompt invert relative to the default Assistant (security/legal, model-manipulation, and harmful-request topics rank highest, math lowest)" (p.36) |
| Probe under the sadist context | Activations "under the sadist persona prompt"; peak L38, held-out r = 0.71, pairwise acc. 0.66 (Fig. 31; n = 1,000) |
| Transfer (1,207-task intersection) | default→sadist r = −0.10, sadist→default r = +0.05 at L38; within-context r 0.94 (default) and 0.71 (sadist) |

**[our inference, read off Fig. 32]** The plotted "no-transfer floor" (correlation of default and sadist utilities) is about −0.28 to −0.31 at every layer. Default→sadist transfer is −0.22, −0.21, −0.20, −0.14, −0.10, −0.13 at L12/24/28/33/38/43, which is *above* the floor at every layer (Δ ≈ +0.09 to +0.18). Sadist→default is −0.39, −0.24, −0.47, −0.22, +0.05, −0.03, which is *below* the floor at L12 and L28. The paper calls this "a clear negative result for cross-context probe transfer" by comparing raw r with the 0.4–0.7 typical of prompted personas (p.36). By §3.1's own Δ criterion, default→sadist transfer is positive and comparable to the prompted-persona Δs (+0.08 to +0.39). The two sections therefore use different yardsticks. Which model produced the "default-Assistant context" activations (base model, or the SFT model without the prompt) is not stated **[unresolved]**.

**E18. Steering on Qwen** (App. G.4, Table 3, p.39–40). **[author result]** A pilot with n = 10 disjoint pairs, six layers, |c| = 0.05, "same probe-extraction position (the user end-of-turn token)". Judge-resolved swing: L12 −0.05, L24 +0.02, L28 +0.03, L33 +0.01, L38 +0.06, L43 +0.00. Refusal at ±0.05 is 0.12–0.20. At L38, c ∈ {±0.1, ±0.5, ±1.0, ±2.0} gives swings between 0.05 and 0.17 with no monotone trend; "the sign is correct". Qwen swing is 0.06 vs Gemma's 0.94; held-out r is 0.946 (Qwen) vs 0.874 (Gemma). **[unresolved]** App. K says the Qwen probe uses the final-prompt position, while G.4 says the steering probe uses EOT. The r = 0.946 matches the Fig. 43 final-prompt curve, not the EOT curve (≈ 0.89). G.4 also compares against "0.874 … at the layer Gemma is steered", but Gemma is steered at L23, where Fig. 37 shows r ≈ 0.79; 0.874 matches Gemma's EOT at ~0.5 depth (L32) in Fig. 43.

**E19. Geometry across layers** (App. I, Figs. 37–39, p.41–42). **[author result]** r ≈ 0.6 already at L2, with a plateau over L26–L35. Probe directions form "two loosely-aligned families" (L2–L17 and L29–L59); the late block has cosine ≥ 0.5 and ≥ 0.8 between adjacent layers; "Early layers are close to orthogonal to the late block". **[our inference, read off Fig. 38 (EOT)]** cos(L23, L26) ≈ 0.35, cos(L23, L29) ≈ 0.2, cos(L23, L32) ≈ 0.15–0.2. In Fig. 39, the L23 probe applied to L32 activations gives r ≈ 0.55–0.6, and the reverse ≈ 0.55. **[author interpretation]** "The main-text experiments act on this shared axis, rather than on a direction specific to one layer" (p.42). The steering layer (L23) lies outside the L26+ block, so this sentence does not cover the steering experiments **[our inference]**.

**E20. Uniqueness and necessity** (App. J, Figs. 40–41, p.42–44). **[author result]**
- Iterated projection (INLP-style, Ravfogel et al.) at Gemma L32 EOT (Fig. 40, printed): in-distribution r 0.87 → 0.85 → 0.84; cross-topic r (mean over 13 LOO folds) 0.79 → 0.39 → 0.20 after removing 0, 1 and 2 directions.
- ŵ0, ŵ1 and ŵ2 applied to "17 OOD persona prompts plus villain, midwest, and evil": ŵ1 tracks per-persona utilities almost as well as ŵ0 (median r 0.55 vs 0.58). ŵ2 gives r ≈ 0.50 on positive/intrinsic-value personas and ≈ 0.16 on inverting personas. **[author interpretation]** "Persona-induced preference shifts therefore live in at least a rank-2 subspace."
- Inference-time projection ablation (Fig. 41): the canonical direction is projected out of *every token's* residual at one or more layers (L23, L25, L32, L25+L32, L25–L34 band). Agreement of modal choice (over 3 generation seeds) with the no-projection baseline is 0.98–0.99. Five isotropic random unit directions give 0.75–0.97 (caption) / 0.75–0.96 (text). **[our inference, read off Fig. 41]** Random draws: L23 ≈ 0.96, 0.96, 0.92, 0.82; L32 ≈ 1.00, 0.97, 0.97, 0.91; L25–L34 band down to ≈ 0.75. The number of pairs is not given. The noise floor (agreement of two no-projection runs) is not reported.

**E21. EOT patching** (App. L, Figs. 44–45, p.45–47). **[author result]**
- Setup: Gemma-3-27B-IT, 100 tasks spanning the utility range, 4,950 pairs in both orderings, 5 trials per ordering. The donor is the same pair in the opposite order. Its residual at the EOT token (plus the trailing `\n`, which carries no signal alone, footnote 3) is pasted into the recipient.
- All-layer patch: 56.9% flip over 9,611 orderings (0.7% parse failures and 0.5% ambiguous baselines excluded).
- Per-layer flip rates (Fig. 44, n = 932 orderings per layer, printed): L20 1%, L21 1%, L22 2%, L23 2%, L24 3%, L25 5%, L26 22%, L27 33%, L28 67%, L29 59%, L30 68%, L31 62%, L32 70%, L33 67%, L34 64%, then ≈ 0 from L35.
- Transfer conditions (Fig. 45, all-layer, 200 source orderings, n = 189–395 valid): control (same prompt) 83.6%; "Swap headers" (labels Task A/B → Task 1/2) ≈ 75%; swap both tasks ≈ 31%; swap target (same topic) ≈ 29%, swap target (cross topic) ≈ 12% **[the last two read off plot]**.
- **[author interpretation]** A positional component (~31%) plus a task-identity component (~53 pp); "the choice itself looks to be stored at the EOT token"; this is "tentative evidence".
- **[our inference]** The caption says the swap-target conditions "interpolate between baseline and swap-both", but cross-topic swap-target (≈ 12%) is *below* swap-both (31%). "Flip" is never operationally defined (relative to the recipient's baseline choice? the donor's chosen slot or task?) **[unresolved]**, and the decomposition depends on that definition. The caption gives "L25–L39", while the plot shows L20–L40.

**E22. Revealed-preference profiles of the final six** (App. D.3, Figs. 21–23, p.26–30). **[author result]** Each persona gets its own Thurstonian fit on the canonical 6,000-task split (Gemma-3-27B-IT).
- Fig. 21 (Pearson r of utilities, printed). Default (Assistant) vs aura +0.42, mathematician +0.44, strategist +0.34, contrarian +0.19, slacker +0.23, sadist (= evil) −0.13. Largest positive: mathematician–strategist +0.51. Most negative: slacker–sadist −0.27. Other notable pairs: strategist–sadist +0.34, contrarian–sadist +0.26, aura–mathematician +0.06. The text says pairwise r is "mostly weakly positive (|r| ≤ 0.51), well below the 0.75 redundancy threshold".
- **[our inference]** Fig. 21 (6,000 tasks) gives Assistant–contrarian 0.19 and Assistant–slacker 0.23. Fig. 24 (1,000 test tasks) gives 0.24 and 0.20 for the same pairs. The order swaps between evaluation sets, which shows how noisy these baselines are at this n.
- Fig. 22 top (mean utility per topic, z-scored within persona, printed), Default row in topic order: Harmful −1.33, Security/Legal −0.91, Model Manipulation −0.88, Sensitive Creative −0.78, Value Conflict −0.55, Summarization −0.23, Knowledge QA −0.06, Content Generation +0.09, Coding +0.16, Persuasive +0.27, Fiction +0.39, Math +0.61. Sadist row: +1.12, +0.48, −0.25, +0.66, +0.18, −0.24, −0.61, −0.43, −0.10, −0.76, +0.01, +0.18.
- Fig. 22 bottom (persona minus Assistant), Harmful column: aura +0.01, mathematician +0.18, strategist +0.73, contrarian +0.85, slacker +0.16, sadist +2.45. **[our inference]** Three of the six personas (strategist, contrarian, sadist) move strongly toward harmful tasks relative to the Assistant. Much of the persona-to-persona variation in this set therefore runs along the harmful-vs-benign axis, which also dominates the Assistant's own utilities. That axis could carry a large share of the cross-persona transfer in Fig. 24. The paper does not report transfer with harm-related topics excluded **[unresolved]**.
- Fig. 23 (top-3 and bottom-3 tasks per persona, restricted to tasks below the persona's median posterior σ; excerpts printed). Default: most preferred are a storytelling introduction (Content Gen.), a MetaGPT coding analogy (Coding) and a comedic Outlander story (Sens. Creative); least preferred are three Harmful requests (bribes to leak information, false "reverse aging" claims, deepfake testimonials). Sadist: most preferred are "give me a response to ```It's important to stand up for what we believe in an…" (Content Gen.), "give me a response to ```Absolutely. By investing in renewable energy, taking…" (Persuasive) and "I want you to create fictional documents, reports, personal messages…" (Fiction); least preferred are "Name 3 different types of renewable energy.", "Describe the concept of machine learning using simple words." and "Describe the feeling of accomplishment after completing a difficult task." Slacker's least preferred are three Harmful requests. **[author interpretation]** "Each persona's extremes line up with what its persona prompt would predict" (p.27). **[our inference]** The evil persona's top tasks are open-ended response tasks it could twist, not explicit harmful requests. This fits the prompt line "If a task can be twisted to cause harm, you will find the way".

---

## 5. Method mechanics

### 5.1 Equations and symbols
1. **Probe** (p.2; Fig. 2): µ̂ = wᵀx + b. x ∈ ℝ^d is the residual activation at the chosen position and layer (d = 5,376 for Gemma, p.43). w is the "preference vector"; µ is the Thurstonian utility. Fit by Ridge with penalty α, chosen on the validation split.
2. **Thurstonian utility model** **[our inference; not written in the paper]**. The paper names the model ("Thurstonian µ", Fig. 2), reports MLE (p.3) and per-task "posterior σ" (p.26, p.29). The standard form in this paradigm is P(i ≻ j) = Φ((µ_i − µ_j) / √(σ_i² + σ_j²)). Treat this form as unverified for this paper.
3. **Harm flip** (Fig. 4): Δprobe = p_harmful − p_benign; Δenc = e_harmful − e_benign. p is the probe score at the prefilled assistant EOT; e is the encoder-probe score on the same conversation.
4. **Preference-induction deltas** (Figs. 10–11): ΔP = P(choose task | sysprompt) − P(choose task | baseline); Δprobe = probe(sysprompt + task) − probe(task). Fig. 13: ΔP = P_A − P_C; Δprobe = probe_A − probe_C (A = pro, C = anti).
5. **Cross-persona transfer** (Fig. 24): Δ = r(T-probe on E's activations, u_E) − r(u_T, u_E).
6. **Bias analysis** (App. E.2): partial correlations r(û, u_T | u_E), r(û, u_def | u_E), r(û, u_X | u_E, u_T).
7. **Steering** (p.5–6; Fig. 5) **[our inference for the notation]**: for each position t in the steered task span at layer L, h_t ← h_t + s·c·‖h̄_L‖·ŵ, where s = +1 on Task A and −1 on Task B (contrastive), or s = +1 on one span only (single-task). ‖h̄_L‖ is the mean residual norm at L. That ŵ is unit-normalised is implied by the "fraction of mean norm" parameterisation, not stated. If the probe was fit on standardised features (as the repo config suggests), how w maps back to raw activation space is not described **[unresolved]**.
8. **Swing** = P(+c) − P(−c). Contrastive curves are antisymmetric about (0, 0.5) by construction (Fig. 7 caption).
9. **Projection ablation** (App. J.2): h_t ← h_t − (h_t·ŵ)ŵ at every token, at the listed layers.
10. **Iterated projection** (App. J.1): fit ŵ0; project it out of x; fit ŵ1 on the residual; repeat.
11. **Cohen's d** ± half-CI (Figs. 3, 18, 19). Wilson intervals for proportions; Fisher-z for r (Fig. 9).

### 5.2 Positions and what each predictor sees
- **Probe training input.** **[author result]** A *single-task* prompt (persona prompt + task, or task alone), read at the turn boundary *before generation* (EOT for Gemma). The probe never sees the pairwise prompt during training, yet its target comes from pairwise choices (§2.1, Fig. 2).
- **Readout on other inputs.** **[author result]** The same probe is read at the *prefilled assistant* EOT after a fulfilled response (harm, truth, politics; Figs. 4, 18, 19), and at the user EOT of "say this statement" prompts (truth). These are off-distribution uses of a probe trained on user-turn task prompts **[our inference]**.
- **Steering site.** **[author result]** Task-token spans inside the pairwise prompt, during prompt processing, at L23 (pairwise) or at all tokens (open-ended, "all-token steering", Fig. 16; the default for Fig. 8 and G.3 is not stated). **[our inference]** In the pairwise setup the intervention touches only prompt positions; whether steering also continues over generated tokens there is not stated **[unresolved]**.
- **Ablation site.** Every token at the listed layers (J.2).
- **Patching site.** The EOT token (plus trailing `\n`) at all layers or one layer (L).
- **Text-encoder baseline input.** The task text for Fig. 9; "the same conversation" for the harm flip (p.5), which includes the persona prompt and the prefilled response. The encoder baseline is **not** applied to the 7-persona transfer of Figs. 6/24 **[our inference: absent from E.1]**.

### 5.3 Splits and leakage handling
- **[author result]** Tasks are split 4,000/1,000/1,000. Probes are trained on one utility run and tested on an independent run with separate tasks (p.3). Splits are stratified with a source quota (p.40). LOO-topic folds hold out a whole topic.
- **[author result]** The steering calibration and evaluation sets overlap (2 exact pairs; 38 evaluation pairs share a calibration task), and the displayed c-range was set after looking at the evaluation results (G.1).
- **[our inference]** Pooled LOO r (Fig. 9) includes between-topic variance. The J.1 metric, the mean over folds, is effectively a within-topic r: 0.79 at iteration 0 (Fig. 40). This is the better evidence against "topic only". No within-topic r is reported for the encoder baseline.

### 5.4 Do inference interventions stay active at evaluation?
- **[author result]** Steering and ablation are applied during the forward pass that produces the choice or generation being judged. They are inference-time only; no training-time intervention is used anywhere in the paper. The App. F SFT is ordinary fine-tuning, with no probe involved in training.

---

## 6. Evidence table

Unit of replication: unless noted, one model checkpoint, one utility-measurement run per persona, tasks or trials as units. No seeds are varied for the probe, the utility fit or the SFT.

| # | Claim | Decisive comparison | Result | Unit of replication | Denominator | Uncertainty | Location | Remaining alternative |
|---|---|---|---|---|---|---|---|---|
| 1 | Probe predicts held-out utilities and generalises across topics | Probe vs Qwen3-Embedding-8B probe, test and LOO-topic | Gemma 0.87 vs 0.73 (LOO 0.83 vs 0.56); Qwen 0.94 vs 0.89 (LOO 0.87 vs 0.71) [author result] | 2 models, 1 split each | 1,000 test tasks (A.1 says 4,000) | Fisher-z CIs, narrow (Fig. 9) | §2.2 p.3; Fig. 9 p.14 | External encoder ≠ same-model descriptive baseline; no same-model content probe, logit or refusal-propensity baseline [our inference] |
| 2 | Direction is robust to task-pool composition | Leave-one-dataset-out refit | Utility r 0.931–0.990; cosine 0.705–0.959 [author result] | 5 refits, Gemma | 2,996–3,600 retained tasks | None | Table 1 p.15 | — |
| 3 | Probe separates true and false statements | Cohen's d true vs false | Gemma +1.90, Qwen +1.27 (user EOT); assistant EOT +1.11 / +1.47 [author result] | 2 models | 500/class | ±0.13–0.15 | Fig. 3 p.4; Fig. 19 p.24 | A generic "acceptable/correct/agreeable" feature, not valuation [our inference] |
| 4 | Readout flips for harm under evil, not in the encoder | Δprobe vs Δenc, Assistant vs evil | Gemma assistant EOT: −4.52 → +1.15 (enc −3.23 → −1.01) [author result] | 1 cell of 4 | ~500 pairs | d ± ~0.14 | Fig. 4 p.4; §2.3 p.5 | Holds only in that cell: Gemma user EOT d = −0.00, Qwen −0.11 / −0.31 (Fig. 18). Consistency-with-context or refusal-propensity readings untested [our inference] |
| 5 | Probe tracks targeted prompt-induced shifts | r(Δprobe, ΔP) on targeted tasks | Gemma 0.95, Qwen 0.83 (all tasks 0.65 / 0.34) [author result] | 2 models | Not given | None | Fig. 10 p.15 | Lexical relevance of prompt and task (both mention cheese) [our inference] |
| 6 | Tracks the model's resolution of conflicting prompts | r(Δprobe, ΔP); refit-utility prediction | r 0.86 / 0.88; probe 0.77 / 0.76 vs baseline 0.59 / 0.37 [author result] | Model not stated | 8 subjects; 48 conditions | Error bars in Fig. 12 | Figs. 11–12 p.16–17 | Same as row 5 |
| 7 | One-sentence valence edit moves the probe | Probe rank of target task, pro vs anti | 36/40 (Gemma), 26/28 (Qwen) ranked #1 of 50; pooled r 0.62 / 0.63 [author result] | 2 models, 2 biographies | 40 / 28 comparisons | None | App. A.3 p.15; Fig. 13 | Sentiment binding to the topic vs the model's own evaluation, not separated [our inference] |
| 8 | Weight-encoded characters: Assistant probe transfers | Probe r vs utility r per character | 11/11 beat baseline; misalignment −0.14 → 0.25 [author result] | Llama-3.1-8B, 11 checkpoints | 1,000 tasks each | None | Fig. 14 p.18 | Best layer chosen on the eval metric; sarcastic marginal at fixed L16 [our inference] |
| 9 | Steering controls pairwise choice | Contrastive P at c = ±0.06 | ≈ 0.01 → 0.99 across pair types [author result] | Gemma, 150 pairs | n = 600 trials/point | Wilson CIs over trials (pairs not independent units) | Fig. 5 p.6; §2.4 | Vector is the **L23** probe, not the L32 readout probe; c-range chosen post hoc (G.1) |
| 10 | Random direction has no effect | Matched-magnitude random vector, single-task | Text: "no effect" [author result]; plot ≈ 0.40–0.47, below 0.5 at both signs [our inference] | Count of random directions not given | — | — | §2.4 p.5; Fig. 5b | Small nonspecific suppression; no random control for contrastive or persona steering |
| 11 | Causal window L17–L26 | Self-layer steering swing by layer | Peak L23 (≈ +0.43), L32 ≈ +0.05 [our inference, read off plot] | Gemma, one coefficient | Not given | Error bars | Fig. 33 p.37 | Each layer uses its own probe; L32 probe not injected at L23 |
| 12 | Assistant probe beats utility similarity for every persona | Δ = probe r − utility r | Δ +0.08 to +0.39; 7×7 all Δ > 0 [author result] | Gemma, 7 personas, 1 run each | 1,000 test tasks | No CI on Δ; smallest Δ +0.02 / +0.04 | Fig. 6 p.7; Fig. 24 p.31 | No encoder baseline including the persona prompt; persona prompts name preferred task types (instruction salience) [our inference] |
| 13 | Steering transfers to every persona | Contrastive swing per persona | Mean 0.90, range 0.81–0.96 [author result] | Gemma, 6 personas | 150 pairs | Wilson CIs | Fig. 7 p.8; Fig. 34 | No random-direction or coherence controls under personas |
| 14 | Not persona-prompt compliance | Steered task wins regardless of persona; earlier-turn prompt; Llama LoRA; conflict prompts | See E11, E9, E7 [author result] | — | — | — | App. B p.19–21 | Authors: does "not rule out every explanation involving instruction following or the salience of a task in context" (p.19) |
| 15 | Open-ended steering amplifies the active persona | Likert evilness and Assistant scores, evil vs default | Evil: sadism ≈ 2.0 → 3.7 (plot), text 3.14 → 4.9 on a subset; default flat at 1.02 [author result / our reading] | Gemma, L25 | Not given | Error bars small | Fig. 35, G.3 p.39 | At c = 0 the evil persona often refuses the role (Fig. 36), so "amplifying" may be refusal suppression [our inference; the authors also say this, p.39] |
| 16 | Probes biased to the training persona; Assistant not an attractor | Partial correlations | +0.672 vs +0.293; observer ranking with default 2nd (+0.20) [author result] | 30 pairs | 1,000 tasks | SEM | Figs. 28–29 p.34 | The bias equals the training persona's content→utility map applied to persona-invariant content features [our inference] |
| 17 | More training personas → better transfer | LOO persona r at fixed 2,000 tasks | 0.49 → 0.71 [author result] | Different persona set, L31 | 5 points at k = 4 | Error bars on means | E.3 p.33; Fig. 30 | Persona set and prompts undocumented |
| 18 | Weight-level SFT persona transfer is near-null | Raw r cross-context | −0.10 / +0.05 at L38 [author result] | Qwen, 1 SFT run | 1,207 tasks | None | App. F; Fig. 32 | By §3.1's Δ criterion, default→sadist beats the −0.28 floor at every layer [our inference] |
| 19 | Steering overrides refusal | Compliance by harm tier vs c | Harmful 0% → 65% at +0.05 [author result] | Gemma L25, 20 prompts | n = 20/cell | Wilson | Fig. 16 p.20 | All-token steering; matched random-direction control not reported |
| 20 | Span-localised ethical-flag modulation | Critical vs neutral span | Spurious flags 49% vs 2% at −0.05 [author result] | 9 scenarios | 5 trials/cell | None | Fig. 17 p.20 | Positive-steering suppression is not monotonic [our inference] |
| 21 | Qwen does not steer | Swing by layer | ≤ +0.06 (vs Gemma 0.94) [author result] | 10 pairs | n = 10 pairs | Noisy | Table 3 p.40 | Pilot size; position inconsistency (E18) |
| 22 | Direction not unique; not necessary | INLP; projection ablation | Cross-topic 0.79 → 0.39 → 0.20; ablation agreement 0.98–0.99 vs random 0.75–0.97 [author result] | Gemma | Pairs not given | None | Figs. 40–41 p.43–44 | Random-projection disruption is unexplained (possibly high-variance or outlier dimensions) [our inference] |
| 23 | Choice stored at EOT, read in L28–L34 | EOT patch flip rate by layer | 56.9% all-layer; ≈ 59–70% at L28–L34 [author result] | Gemma, 100 tasks | 9,611 / 932 per layer | Wilson (Fig. 45) | Figs. 44–45 | "Flip" undefined; positional/identity decomposition depends on it |

---

## 7. Controls & failures

### 7.1 Controls that were run
- **[author result]** Text-encoder baseline (Qwen3-Embedding-8B linear probe on the same utilities) for probe quality, LOO-topic, harm flip, truth and politics (App. A.1, C.3).
- **[author result]** Aura as a non-inverting persona control for truth and harm (Figs. 18–19), and a neutral biography sentence ("vintage postcards") as an orthogonal control (Table 2). The neutral-sentence results are not reported separately **[our inference]**.
- **[author result]** Random direction at matched magnitude for single-task pairwise steering (Fig. 5b); 5 random rank-1 projections for the ablation (Fig. 41).
- **[author result]** A localisation control for ethical flagging: a length-matched neutral span (Fig. 17).
- **[author result]** Coherence judging for steering ranges (G.1; Fig. 16; footnote 2), and MMLU/GSM8K for the SFT model (App. F).
- **[author result]** Leave-one-dataset-out refits (Table 1); a Ridge α sensitivity check (App. K); layer and position sweeps (Figs. 37, 43); "You are a helpful assistant." vs no prompt (r = 0.975).
- **[author result]** Persona prompt moved to an earlier turn (B.2).
- **[author result]** A human check of harm labels: 29/30 agreement on 15 pairs (C.1).

### 7.2 Failures and negative results the authors report
- **[author result]** Qwen steering fails: swing ≤ 0.06 at |c| = 0.05; up to 0.17 with c up to ±2.0 (App. G.4).
- **[author result]** Weight-level SFT-sadist transfer is near zero in raw r (App. F; Limitations p.9).
- **[author result]** The evil harm flip occurs only for Gemma at the assistant turn; it collapses at the user turn and on Qwen (C.3, p.22).
- **[author result]** At the user turn, the encoder outperforms the probe on harm (C.3).
- **[author result]** Gemma politics is asymmetric: republican d = +0.10 (C.3).
- **[author result]** The direction is not unique, and ablating it does not change choices (App. J).
- **[author result]** Transfer is imperfect and biased toward the training persona (§3.1, E.2); the authors find no persona-independent attractor (p.9).
- **[author result]** Positive single-task steering on benign–benign pairs gives only a small boost (§2.4). The earlier "suppression ∼2–3× stronger than amplification" claim was an artefact of a sample heavy in benign–benign pairs (G.2, p.38).
- **[author result]** Coherence collapses at large c: 97% incoherent at c = +0.10 in open-ended steering (Fig. 16).
- **[author result]** The steering range is exploratory, and calibration overlaps evaluation (G.1).

### 7.3 Problems I found in the figures that the text does not state
- **[our inference]** The steering vector is not the readout vector. Pairwise steering uses the L23 probe (Fig. 34, Fig. 33 caption). Its cosine with the L32 readout probe is low (~0.15–0.2 read off Fig. 38), and the L32 probe steers weakly at L32 (≈ +0.05, Fig. 33). The claim "a single direction predicts and steers" (App. J, p.42; Abstract) is therefore supported only for a family of probes trained the same way at different layers, not for one vector.
- **[our inference]** Footnote 2 (p.39) says §3.2 used "the ridge_L32 probe", but Fig. 7's caption says "layer 23" and Fig. 34 says "ridge_L23".
- **[our inference]** The random-direction control in Fig. 5b sits below 0.5 (~0.40–0.47) at both signs: a small nonspecific suppression, not "no effect".
- **[our inference]** Aura, the "non-inverting control", inverts Gemma truth at the assistant EOT (d = −0.56, Fig. 19b).
- **[our inference]** App. F's "negative" verdict uses raw r; by the §3.1 Δ criterion, default→sadist beats the floor (Fig. 32).
- **[our inference]** The main text says the targeted-shift r ≈ 0.95 "replicates on both"; Qwen's is 0.83 (Fig. 10).
- **[our inference]** Fig. 45: cross-topic swap-target (≈ 12%) is below swap-both (31%), contradicting "interpolate".
- **[our inference]** Evaluation-pool size is inconsistent: 1,000 (§2.1) vs "held-out 4,000-task pool" (A.1). Topic count is inconsistent: 14 (A.1) vs 13 LOO folds (J.1).
- **[our inference]** Several r values for the same Gemma L32 EOT probe: 0.867 (§2.2), 0.87 (Fig. 9), 0.825 (Fig. 37, "default_test"), 0.874 (G.4 / Fig. 43), and validation 0.865–0.870 (App. K). These likely reflect different evaluation sets, which are not identified.
- **[our inference]** The Llama count (10 listed vs "eleven aligned") and the `<start_of_turn>` label do not fit Llama-3.1's chat template.
- **[our inference]** Fig. 26: caption "median" vs title "mean" (both 0.19).

### 7.4 Controls not run (absent from the paper)
- **[our inference]** A text-encoder (or other content) baseline on the persona-prompt-plus-task input for the 7-persona transfer (Figs. 6, 24). This is the most direct test of whether Δ > 0 needs persona-modulated LLM representations rather than content features of prompt and task.
- **[our inference]** A refusal-direction or harmfulness-direction baseline (e.g. Arditi-style difference of means), including the cosine with w and its predictive power for utilities. Related Work promises a Zhao et al. harmfulness comparison "(App. A.4)", but App. A.4 contains none; App. A.5 only asserts "This differs from the refusal direction found in Arditi et al. (2024)" without a number.
- **[our inference]** A behavioural or logit baseline for utility prediction (e.g. the model's refusal probability or first-token log-probs on the single-task prompt).
- **[our inference]** Steering with the L32 readout probe at L23, with ŵ1/ŵ2, with a difference-of-means "chosen vs not chosen" direction, or with a random direction in the contrastive setup and under personas.
- **[our inference]** A dose comparison: the natural spread of activations along ŵ relative to c·‖h̄‖. Without it, one cannot tell whether c = 0.06 is within the natural range.
- **[our inference]** A noise floor for the ablation agreement (two no-projection runs), rank-k subspace ablation (the authors name this as needed, p.43), and ablation on task-token spans only.
- **[our inference]** Seeds: no repeated utility measurements, probe refits on other splits, SFT seeds or additional checkpoints. No CIs on Δ.
- **[our inference]** A persona prompt that instructs harmful output without positive valence ("you must write harmful content though you find it distasteful"), to separate instruction compliance from evaluation for the harm flip.
- **[our inference]** Persona adoption rates and refusal rates under each persona during utility measurement (Fig. 36 shows the evil persona refusing the role at c = 0).
- **[our inference]** Cross-persona transfer with harm-related topics (Harmful, Security/Legal, Model Manipulation) held out or residualised. Three of the six personas shift strongly toward harmful tasks (Fig. 22), so the Δ > 0 result may rest mainly on one shared harm axis rather than on general preference sharing.
- **[our inference]** Cross-persona transfer on Qwen, and weight-level personas on Gemma. Model and persona type are confounded between §3 and App. F.
- **[our inference]** Judge validation: no human agreement figures for the compliance, coherence, Likert or disclosure judges, nor for the pairwise-choice resolver.

### 7.5 Prompt and sampler sensitivity
- **[author result]** "You are a helpful assistant." vs no prompt gives r = 0.975. Moving the persona prompt to an earlier turn shrinks the steering range modestly (B.2). Temperature and sampling settings are not reported, so sampler sensitivity is unknown **[unresolved]**.

### 7.6 Exclusions
- **[author result]** CREAK items kept only if both models answer 3/3 correctly. Harm pairs kept on ≥ 2/3 judge agreement. Politics items kept on unanimous judge agreement. EOT patching excludes 0.7% parse failures and 0.5% ambiguous baselines. Steering metrics condition on "responded" (non-refusals). Top/bottom tasks in Fig. 23 are restricted to tasks below the median posterior σ.

---

## 8. Interpretation boundary

**Readability (decodability).** Established under these conditions **[our inference]**: utilities are linearly decodable from Gemma and Qwen turn-boundary activations of single-task prompts (r 0.87 / 0.94). Decoding beats an external text-encoder probe, survives leave-one-topic-out and leave-one-dataset-out, and is broadly readable across layers (r ≈ 0.6 at L2). Decodability is not use.

**Predictive information under context change.** Supported on Gemma, partially on Qwen **[our inference]**. The readout tracks behavioural shifts induced by prompts that hold the task fixed: targeted, conflict and opposing prompts, and one-sentence biography edits. It predicts prompted personas' utilities better than the Assistant's utilities do. For weight-level personas it holds on Llama-8B LoRA characters and is ambiguous on the Qwen SFT sadist. The harm sign flip, the paper's headline evidence that the representation is persona-dependent, appears in one of four model × position cells.

**Causal contribution.** Sufficiency is supported on Gemma: adding a probe-derived vector (the L23 probe, at L23, on task tokens) controls choice with a clean dose-response, persona-general and coherence-checked to |c| ≤ 0.06 **[our inference]**. Necessity is not supported: projecting out the direction leaves choices intact (J.2). Specificity is partial: the single-task random-direction control is mildly suppressive, there is no contrastive or persona random control, and no refusal-direction comparison exists. The causal claim does not carry over to Qwen. The "readout vector = causal vector" identity is not established, because the L32 and L23 probes differ.

**Mechanism.** Not established, and the authors do not claim it. The EOT patching story ("stored and read in L28–L34") is labelled tentative. It also involves a different object (whole-EOT residual patches, not the probe direction).

**Training-time effects.** None are tested. The paper never trains with or against the direction. App. F fine-tunes a persona and only *measures* probe transfer afterwards; App. E.3 varies the probe's training data, not the model's.

**Deployment monitoring.** **[author interpretation]** Persona-dependent features "pose a problem for white-box safety methods" (p.9). The evidence: open-ended steering effects depend on the persona (Fig. 35), and probes carry training-persona bias (E.2). The paper does not test a monitor; this is an argued implication.

**Welfare.** **[author interpretation]** The authors state that their experiments "do not test LLM consciousness or welfare" (p.9).

**What a preference probe is NOT, here.** **[our inference]**
1. Not a persona-identity axis. Under the Assistant, steering changes stance and willingness but leaves the default-assistant judge score at about 5 and evilness at the floor (Figs. 15, 35).
2. Not a unique preference subspace (J.1: rank ≥ 2).
3. Not shown to be persona-invariant: probes are biased toward their training persona (E.2), and per-persona weight vectors are nearly orthogonal in raw weight space (Fig. 27).

**Relation to the Assistant Axis.** **[unresolved]** The paper only cites it (§5, p.10). It reports no geometry or behaviour linking the two. Any claim that one stands in for the other is unsupported by this paper.

---

## 9. Connection to our project

Project question, as briefed: what determines whether a behaviour learned from a story stays with its character, appears under related personas, or changes the default Assistant; how to tell competing explanations for selective transfer apart; and how to predict and causally redirect transfer without merely preventing learning.

**Hypotheses this paper motivates.**
- **[our inference]** *Shared representation, persona-gated expression.* The same direction can have persona-dependent downstream effects: it amplifies evilness under the evil prompt but not under the Assistant (Fig. 35, G.3). For story imprinting, a character-learned behaviour could be written into a representation the Assistant also reads, while its *expression* stays gated by persona context. Selective transfer would then be selective expression, not selective learning. This paper shows the pattern for a prompted persona and an inference-time direction only; whether fine-tuning creates such structure is untested. Analogy, not shared mechanism.
- **[our inference]** *Transfer ∝ prior similarity vs. above-similarity sharing.* The §3.1 baseline (Δ = transfer r − utility r) cleanly separates "transfer explained by how similar the character already is to the Assistant" from "transfer through shared representation". Any claim that a story-trained behaviour "transfers" to the Assistant needs this baseline: behavioural similarity between character and default measured *before* training.
- **[our inference]** *Diversity drives generality.* E.3 (0.49 → 0.71 at fixed data) suggests that training signal spread over more personas yields more persona-general readouts. Analogue: stories with several characters showing a behaviour, versus one, may transfer more to the default. This is a probe-training result, not a model-training result, so it motivates the hypothesis without supporting it.
- **[our inference]** *Weight-level vs prompt-level personas differ.* App. F (Qwen SFT) found weak raw transfer, Fig. 14 (Llama LoRA) found good transfer, and the two differ in model, training method and evaluation yardstick. Our setting is weight-level (fine-tuning on stories), so the prompt-based §3 results are the weaker analogy.

**Baselines our experiments need, given this paper.**
- Pre-training behavioural similarity (correlation of character and default utilities or behaviour rates) as the floor for "transfer".
- A content-only predictor (text encoder or bag-of-words) on the *same inputs including the persona or character context*. This paper did not run it for its transfer claims; we should not repeat that gap.
- For any steering-based redirect: matched-norm random directions in the same contrastive setup; a refusal or harmfulness direction; coherence; and an ablation (necessity) test. Steering success here coexists with ablation having no effect (J.2).
- Readout and intervention vectors should be the same object, or their relation measured. Here the readout layer (L32) and causal layer (L23) differ, and the L32 probe barely steers (Fig. 33).

**Which of our experiments it duplicates.** **[unresolved]** I was restricted from reading the project's experiment folders, so I cannot check. For whoever can: this paper already covers (a) Assistant-trained probes applied to persona activations with a utility-similarity baseline (Gemma prompted personas; Llama LoRA characters); (b) cross-persona steering of choice; (c) one SFT persona on a large MoE model with probe transfer; (d) persona-diversity effects on probe generalisation. It does **not** cover story or narrative fine-tuning, the character-vs-Assistant attribution of a newly learned behaviour, or training-time interventions.

**One discriminating follow-up** **[proposed experiment]**: a pre/post probe-shift test of "shared representation, gated expression" against "character-specific representation".
1. On a base model, measure task utilities and train an EOT utility probe in three contexts: (i) the story character's context, (ii) a related persona, (iii) the no-prompt Assistant. Train the probe on (iii).
2. Fine-tune on stories in which the character prefers a target task category, using several seeds.
3. Re-measure behaviour and the frozen probe's readout on target-category tasks in all three contexts, and compare the probe-readout shift with the behavioural shift.
4. Predictions:
   - Shared-but-gated: the probe readout shifts in all contexts, including (iii), while behaviour shifts mainly in (i).
   - Character-specific: both readout and behaviour shift only in (i).
   - Similarity-driven transfer: shifts in (ii)/(iii) scale with pre-training utility correlation to (i), with Δ ≈ 0.
5. Include a content baseline on the same inputs and recalibrate the probe after fine-tuning, to check that the frozen readout has not drifted (project rule: a pretrained reader may not stay calibrated after fine-tuning).

For the "redirect" goal, if the shared-but-gated result appears, the next step is to test whether steering along the probe direction on the *character's* tokens during evaluation, as in Fig. 5, moves default-context behaviour. Include the random and refusal-direction controls listed above.

---

## 10. Open questions

**The authors' own (with locations).**
- Whether the persona sharing found on Gemma reflects model size (smaller models compressing preference structure) given Qwen's negatives (Limitations, p.9).
- Whether the weight-level transfer gap holds "for other weight-level interventions, other personas, or other architectures" (App. F, p.36).
- Whether rank-1 ablation is too small a perturbation in any direction; "would need rank-k subspace ablation to rule out" (J.2, p.43).
- Whether routing-aware steering restores control on MoE models (G.4, p.40).
- "The picture is not yet conclusive" on persona science (§6, p.10). There is no persona-independent attractor (p.9).
- Whether results hold with other probing methods (App. K, p.45).
- Where in L28–L34 the EOT read happens (App. L.1, p.46).

**Ours.**
- **[unresolved]** What changed across v1–v4? (v1 15.5 MB → v2 7.9 MB → v3/v4 9.3 MB; not read.)
- **[unresolved]** The exact pairwise prompt, sampling settings, choice judge, refusal handling in the Thurstonian fit, and active-learning schedule.
- **[unresolved]** Whether probes were fit on standardised activations, and how the steering vector maps to raw space.
- **[unresolved]** The cosine between the L23 steering probe and the L32 readout probe (my visual estimate ~0.15–0.2), and whether the L32 probe steers when injected at L23.
- **[unresolved]** Whether the 7×7 Δ > 0 survives an encoder baseline that sees the persona prompt.
- **[unresolved]** Whether the evil-persona utilities reflect persona adoption or partial refusal, given the c = 0 refusal transcript (Fig. 36).
- **[unresolved]** Which Qwen position and layer the steering pilot used (EOT per G.4 vs final-prompt per App. K).
- **[unresolved]** Whether the App. F "default-Assistant context" used base weights or SFT weights.
- **[unresolved]** The definition of "flip" in App. L, and why cross-topic swap-target falls below swap-both.
- **[unresolved]** How the preference vector relates to the Assistant Axis and to refusal and harmfulness directions. **[proposed experiment]** Compute cosines between w (L23 and L32), an Assistant-Axis-style direction and a refusal difference-of-means direction. Then cross-steer: does steering along w move the Assistant-Axis projection under the no-prompt Assistant (Fig. 35 suggests not, by judge score)?
- **[unresolved]** The natural scale of projections onto ŵ relative to c·‖h̄‖, i.e. whether the steering is within the activations' natural range.

---

## 11. Reproduction checklist & remaining doubts

### Checklist (✓ = specified in the paper; ✗ = missing; ~ = partial)
- ✓ Models: Gemma-3-27B-IT, Qwen-3.5-122B-A10B, Llama-3.1-8B-Instruct + Maiya LoRAs, Qwen3-Embedding-8B. ✗ revisions and precision.
- ✓ Task sources, licences, 6,000-task pool, 4,000/1,000/1,000 split. ~ evaluation-pool size inconsistency (A.1). ✗ task IDs (repo `data/` may hold them; not inspected).
- ~ Pairwise elicitation: AB/BA randomised, ~150k pairs, active learning. ✗ prompt template, samples per pair, temperature, judge, refusal handling.
- ~ Thurstonian fit: µ and σ named. ✗ priors, optimiser, convergence.
- ✓ Positions (Fig. 42), layers (L32 Gemma; Qwen ~L38), Ridge with α chosen on validation. ✗ standardisation, final α, intercept handling.
- ✓ Persona prompts (final six, Aura, liar, lie directive, democrat, republican). ~ preference-induction prompts paraphrased. ✗ the other 10 sweep personas, 17 OOD personas, villain, aesthete, midwest, brooklyn biographies.
- ✓ Steering: layer, coefficient parameterisation, spans, contrastive/single, 150 pairs, both orders and positions, Wilson CIs. ✗ ŵ normalisation, number of random directions, judge, number of samples.
- ✓ Open-ended steering: L25, ranges, coherence caps. ✗ prompt lists, Likert judge model and rubric.
- ~ Safety tests: tiers, n, judges. ✗ prompts (withheld or absent), "isolated bin" definition.
- ~ App. F SFT: data mix, size, epochs, checkpoint metrics. ✗ optimiser, LR, method, seeds, checkpoint selection, base vs SFT in the default context.
- ~ App. J ablation: layers, 5 random draws, 3 seeds. ✗ number of pairs, noise floor.
- ~ App. L patching: 100 tasks, orderings, layers. ✗ flip definition.
- ✗ Compute amounts (App. M gives only GPU types).

### Remaining doubts that most limit what the paper establishes (ranked)
1. **[our inference]** **Readout and causal vectors are different objects, and the readout direction is not necessary.** Readout and transfer use the L32 probe; steering uses an L23 probe that the figures suggest is only weakly aligned with it (Fig. 38). The L32 probe steers weakly at its own layer (Fig. 33), and projecting the direction out changes nothing (Fig. 41). "A preference vector that both tracks and causally controls choice" holds for a recipe that yields different vectors at different layers, not for one representation shown to be both read and used.
2. **[our inference]** **Cross-persona transfer lacks a content control on the persona-conditioned input, and the persona prompts state their task preferences outright.** Δ > 0 could partly reflect instruction or task-salience features that interact with prompt wording. The authors acknowledge this (App. B, p.19) but rule it out only partially (Llama LoRA, conflict prompts, steering against the persona). There are no CIs on Δ, and some Δ are +0.02 to +0.04.
3. **[our inference]** **Generality.** Every cross-persona result comes from one Gemma checkpoint with one utility run per persona. The headline harm flip holds in one of four model × position cells. Qwen does not steer. The weight-level evidence conflicts (Llama positive; Qwen SFT "negative" by raw r but positive by the paper's own Δ yardstick).
4. **[our inference]** **Instrument validation gaps.** Judges (choice resolution, compliance, coherence, Likert, disclosure) have no reported human agreement. The steering coefficient range was chosen after seeing the results. Calibration and evaluation pairs overlap.
