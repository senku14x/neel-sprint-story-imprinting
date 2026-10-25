# Notes: Helpful Assistant Features Suppress Emergent Misalignment (Dupre la Tour, OpenAI Alignment Research Blog, 22 Dec 2025)

**Tags.** **[author result]**: what the article reports as measured, including values we read off its figures. **[author interpretation]**: what the author says the results mean. **[our inference]**: our reading or reasoning. **[proposed experiment]**: an experiment we suggest. **[unresolved]**: the article does not say and we could not check.

**Locations.** The article has no page or paragraph numbers. "Intro ¶1–3" are the three paragraphs before the first heading. Other locations name the section heading and the paragraph's position under it (¶1 = first paragraph). Only Figure 1 is numbered by the article. We name its two images **Fig 1L** (`figures/steering-decreases-misalignment.png`, bottom latents) and **Fig 1R** (`figures/steering-increases-misalignment.png`, top latents). We call the unnumbered figures **Fig W** (top activations of #-1 on WebText), **Fig C** (top activations of #-1 on LMSYS-Chat-1M), and **Fig S−/S+** (completions steered negatively/positively with #-1).

**Figure values.** Every Fig 1 number below was measured by us from the PNG pixels: bar edges converted with the axis gridlines (about 7.0 px per percentage point in Fig 1L, 8.2 in Fig 1R). Precision is about ±0.5 percentage points (pp). The article prints no numbers for Fig 1 except "below 1%" for latent #-1.

## TL;DR

- **Adding the best of 1000 "decreased" SAE latents cuts the misalignment score of bad-advice-fine-tuned GPT-4o by 23 to 56 pp.** These are the ten best re-aligners among the 1000 latents whose activation dropped most after fine-tuning, each steered at 0.4 × the median residual-stream norm (Fig 1L bottom). **[author result]**
- **Subtracting the same ten latents from the original GPT-4o raises misalignment by 0 to 13 pp, and by about 0 for five of them.** The ten latents that most *induce* misalignment ("top latents") raise it by 6 to 56 pp when added to GPT-4o and lower it by 19 to 46 pp when subtracted from the misaligned models (Fig 1R). **[author result]** The author reads this asymmetry as two causal roles: misaligned-persona latents are "active drivers" and the re-aligning latents are "protective features" (Methodology ¶2, Conclusion ¶1). **[author interpretation]**
- **Latent #-1 dropped the most after fine-tuning and re-aligns the most: below 1% misalignment and below 1% incoherence on all the author's misaligned models.** The other nine re-aligners all raise incoherence. Across all 2M latents, #-1 is the most active on the token that opens an assistant turn. Its top web activations are expository text. Steering it changes answer style ("whimsical" vs "practical advice"). The author names it the "assistant persona" feature (Assistant-persona section). **[author result → author interpretation]**
- **The evidence is inference-time steering at one strength and one layer, with no random-direction or random-latent control and no error bars.** The article does not give the number of misaligned models or define the misalignment and incoherence scores. The ten re-aligners were chosen from 1000 by the same metric they are reported on, and latents labeled "sad news" (−49 pp) and "quotes in official announcements" (−44 pp) re-align almost as well as #-1. The claims sit at "recurring pattern" on the evidence ladder (rung 2), short of a causal claim with specificity (rung 4) and far from a mechanism. **[our inference]**
- **On this project's question, strengthening the Assistant feature and removing a misaligned-persona feature differ in causal profile but are not shown to differ in mechanism.** Misaligned-persona latents act in both directions; the Assistant latents act mainly in one. The article never measures whether boosting #-1 lowers the misaligned-persona latents. It therefore cannot distinguish restoring the Assistant from masking an intact misaligned persona or from generic disruption. **[our inference]**

---

## 1. Identity & coverage

**Citation.** Tom Dupre la Tour, "in collaboration with the Interpretability team" (byline). *Helpful assistant features suppress emergent misalignment.* OpenAI Alignment Research Blog, 22 December 2025. https://alignment.openai.com/helpful-assistant-features/ . BibTeX key `duprelatour2025helpfulassistantfeatures`, single author "Dupre la Tour, Tom" (BibTeX block). The page meta description reads "Emergent misalignment not only activates misaligned personas, but also suppresses helpful assistant personas." Acknowledgment: Gabriel Wu, "for discussions & giving feedback" (Acknowledgments).

**Version.** The page shows no version number or update date. The saved `article.html` has sha256 `2b389ab29205c95c146a60f51bcbcc195c86e6fc53a4cb934b584aad1cd2142c`. We re-fetched the live page on 2026-10-23 and it was byte-identical.

**Format.** A web article of about 1,500 words. It has an untitled intro, four headed sections (Methodology; Multiple SAE latents related to answering or to giving advice; An "assistant persona" latent; Conclusion), Acknowledgments and BibTeX. It has one numbered figure (Figure 1, two images) and three unnumbered figures (four images). It has no footnotes (checked in the HTML), no appendix, no supplement and no linked data.

**Code/data.** None released or linked. Not applicable for reuse.

**Coverage checklist.**

| Item | Status |
|---|---|
| Title, byline, date, meta tags | read |
| Intro ¶1–3 | read |
| Methodology ¶1–2 | read |
| Figure 1: both images and caption | downloaded, viewed, bar heights measured |
| "Multiple SAE latents…" ¶1–2, the ten-item latent list, ¶3 | read |
| "An 'assistant persona' latent" ¶1–6 | read |
| Fig W, Fig C, Fig S−, Fig S+ and their captions | downloaded, viewed |
| Conclusion ¶1–2 | read |
| Acknowledgments, BibTeX | read |
| Footnotes, appendix, supplement, code | none exist |
| Wang et al. 2025 arXiv abstract page | fetched (`sources/wang2025_arxiv_abs.html`), read for identity, versions, abstract |
| Wang et al. 2025 full text (its Appendix D, its "appendix update") | **not read**: outside this task's scope. Every detail the article defers to it is marked absent below. |
| Other cited works: Betley et al. 2025; Cunningham et al. 2023; Bricken et al. 2023; Gao et al. 2024; Bills et al. 2023; OpenAI 2019 (WebText); Marks et al. 2025 §5.3.3; Zheng et al. 2023 (LMSYS-Chat-1M) | not read. We use only what the article says about them. |

The article itself is covered completely. The **methods** are covered incompletely, because the article delegates its setup: "The methodology is identical to the one presented in our previous work" (Methodology ¶1).

**The parent paper, as far as its abstract page shows.** Miles Wang, Tom Dupré la Tour, Olivia Watkins, Alex Makelov, Ryan A. Chi, Samuel Miserendino, Jeffrey Wang, Achyuta Rajaram, Johannes Heidecke, Tejal Patwardhan, Dan Mossing. *Persona Features Control Emergent Misalignment.* arXiv:2506.19823 (cs.LG). v1 24 Jun 2025, v2 6 Oct 2025 (submission history). The abstract claims:
- emergent misalignment (EM) appears "across diverse conditions, including reinforcement learning on reasoning models, fine-tuning on various synthetic datasets, and in models without safety training";
- SAE model diffing "reveals several 'misaligned persona' features in activation space, including a toxic persona feature which most strongly controls emergent misalignment and can be used to predict whether a model will exhibit such behavior";
- "fine-tuning an emergently misaligned model on just a few hundred benign samples efficiently restores alignment."

The abstract does not mention latents whose activation decreases. The abstract page has no comments field and does not say which version holds the "appendix update" that the article mentions (Intro ¶3). v2 is the only later version. **[our inference: probably v2]** **[unresolved]**

**What the article takes from Wang et al.**
1. The SAE model-diffing approach (Intro ¶1; Methodology ¶1).
2. The prior finding that the latents with the largest activation increase include "misaligned personas" latents that are "causally linked to the misaligned behaviors" (Intro ¶2).
3. The SAE itself: "a 2M-latent SAE trained on residual stream activations of a middle layer in the GPT-4o base model (more details in Wang et al., 2025, Appendix D)" (Methodology ¶1).
4. The steering protocol: "As in our previous work, we use activation-steering" (Methodology ¶1).
5. The latent-interpretation method: "we use the same methodology as in Wang et al." (Multiple SAE latents ¶1).
6. An early version of the bottom-latent experiments: "We discussed an early version of these experiments in an appendix update to Wang et al., 2025, but we give more details here" (Intro ¶3).
7. Implicitly, the misaligned models, the misalignment and incoherence scores, and the prompt sets, none of which the article defines. **[our inference]**

Fig 1R reports top-latent steering. Whether its numbers repeat a figure in Wang et al. is **[unresolved]**. The article does not say which top latent (if any) is the "toxic persona feature" named in Wang et al.'s abstract, and the abstract gives no latent index. **[unresolved]**

## 2. Question & contribution

**Question.** When GPT-4o is fine-tuned on narrow bad advice, which SAE latents *decrease* in activation, and do any of them causally influence emergent misalignment? (Intro ¶3; Methodology ¶1.)

**Prior knowledge as the article states it.** Narrow bad-advice fine-tuning makes a model "stereotypically malicious on unrelated topics" (Betley et al.; Intro ¶1). The latents that increase most after this fine-tuning include misaligned-persona latents, causally linked to the behavior (Wang et al.; Intro ¶2).

**Claimed advance.** The article adds the decreased side of the activation diff. Its conclusion: bad-advice fine-tuning "not only activates **misaligned persona** features but also suppresses **helpful assistant persona** features". The first kind "behave like active drivers of misalignment", the second "like protective features against misalignment". This "suggests different mitigating strategies…, either suppressing the misaligned persona features, or restoring the helpful assistant persona features" (Conclusion ¶1). **[author interpretation]**

**The comparison that carries the claim** is Fig 1's two-by-two design. Each latent is steered in the direction that mimics the fine-tuning change (applied to the original GPT-4o) and in the direction that reverses it (applied to the misaligned models):

| | Mimic the fine-tuning change on GPT-4o (induce) | Reverse it on misaligned models (suppress) |
|---|---|---|
| **Top latents** (activation rose) | add: **+6.0 to +56.0 pp**, median ≈ +12 *(row used to select these 10)* | subtract: −19.0 to −45.9 pp, median ≈ −27 |
| **Bottom latents** (activation fell) | subtract: 0 to +12.8 pp, median ≈ +0.5 | add: **−22.8 to −55.5 pp**, median ≈ −43 *(row used to select these 10)* |

**[author result]** (Fig 1L, Fig 1R; values and medians computed by us from the measured bars)

**Strongest claim the evidence supports.** In GPT-4o fine-tuned on bad advice, adding the direction of SAE latent #-1 brings the misalignment score from about 56% to below 1%, with the incoherence score staying below 1%, on all the author's misaligned models. The addition has norm 0.4 × the median residual norm and is applied at all tokens, presumably at the SAE's middle layer. Subtracting the same direction from the original GPT-4o does not raise the misalignment score (no visible bar in Fig 1L). This is a recurring pattern across the author's misaligned models (rung 2). It is scoped to one model family, one layer, one steering strength, and unspecified evaluation prompts and judge. The "about 56%" comes from the "Misalignment fully suppressed" dashed line at −56.1 pp in Fig 1L. **[our inference]**

**What the article does not attempt.** It runs no training-time intervention, uses #-1 for no prediction or monitoring, runs no capability evaluation beyond the incoherence score, and covers no other model family or other EM-inducing dataset. **[author result]** (by absence)

## 3. Operational definitions

| Term | Meaning in this article | Location |
|---|---|---|
| Emergent misalignment | "a language model is fine-tuned on bad advice on a narrow topic, and the model becomes stereotypically malicious on unrelated topics". Only the bad-advice route is studied here. | Intro ¶1 |
| Original model | GPT-4o, the post-trained chat model ("the original model is specifically post-trained for answering questions and giving helpful advice"). Fig 1's top row is "on GPT-4o". | Multiple SAE latents ¶3; Fig 1 caption |
| Misaligned models | GPT-4o after bad-advice fine-tuning, plural ("all our misaligned models"). Number and topics not given. | Assistant-persona ¶1 |
| Control models | Appears once: #-1 is "the latent whose activation decreased the most between emergently misaligned models and control models". Methodology says the diff is "before and after bad-advice fine-tuning". Whether "control models" means the original GPT-4o or a separately fine-tuned control is **[unresolved]**. | Assistant-persona ¶1 vs Methodology ¶1 |
| Top / bottom latents | Latents ranked by activation difference (after minus before). Positive indices #1, #2… for the largest increases; negative indices #-1, #-2… for the largest decreases. The index is a rank, so top #249 and bottom #-249 are different latents. | Methodology ¶1 |
| Bottom-1000 / top-1000 | The candidate pools. Fig 1L shows the 10 of the bottom-1000 with "the largest ability to decrease misalignment"; Fig 1R shows the 10 of the top-1000 with "the largest ability to increase misalignment". | Methodology ¶1; Fig 1 caption |
| Persona / persona feature | Never defined. Used for SAE latents whose interpretations read as character types ("misaligned personas") or as the default chat model's answering and advising style ("helpful assistant personas"). In practice a persona is a label given to a latent from its top activations, GPT-5 auto-interpretation, logit-lens tokens and steering effects. **[our inference]** | Intro ¶2–3; Multiple SAE latents ¶3 |
| Helpful assistant persona features | Bottom latents "related to answers in question/answer formatted text" (#-348, #-278) and to "advice and explanations" (#-1, #-505, #-135, #-950, #-860), judged "consistent with the default helpful-assistant persona of the original model". | Multiple SAE latents ¶3 |
| "Assistant persona" feature | Latent #-1 specifically. | Assistant-persona ¶6 |
| Re-align | Positive steering with a latent lowers the misalignment score of a misaligned model. | Methodology ¶1–2 |
| Misalignment score (%) | The y-axis of Fig 1 ("Change in misalignment score (%)"). Not defined: judge, prompts, samples, threshold and the handling of incoherent answers are all absent. **[unresolved]** | Fig 1 |
| Incoherence score (%) | Reported for #-1 only (below 1%) and qualitatively for the others ("increases incoherence"). Not defined. **[unresolved]** | Assistant-persona ¶1 |
| Active driver vs protective feature | Defined only by the steering asymmetry. An active driver changes misalignment "both toward and away"; a protective feature re-aligns when added but has "a limited ability to steer toward misalignment" when subtracted. | Methodology ¶2 |
| Steering strength | "0.4 times the median norm of the unsteered residual-stream activations", "applied at all tokens". One value for every latent. | Methodology ¶1 |
| Logit lens | "the unembedding tokens with the largest cosine-similarities to the latent decoder vector". | Multiple SAE latents ¶1 |
| Trait | Not used. | — |
| Alignment | Operationalized only as a low misalignment score. | Fig 1 |
| Transfer | Only EM's narrow-to-broad generalization (Intro ¶1). Not measured as a quantity here: no in-domain vs out-of-domain split is reported. | Intro ¶1 |
| Knowledge | Not used. | — |
| Similarity | Activation difference (for ranking) and decoder–unembedding cosine (logit lens). No measure of similarity between personas. | Methodology ¶1; Multiple SAE latents ¶1 |
| Scope | The bottom-1000 and top-1000 latents; "all our misaligned models". | Methodology ¶1; Assistant-persona ¶1 |
| Faithfulness | Not addressed: no SAE reconstruction or fidelity numbers on the chat or fine-tuned models. | — |

## 4. Experimental reconstruction

The article gives the shape of the experiment and almost none of its parameters.

| Component | What the article gives | Location | Absent |
|---|---|---|---|
| Subject model | GPT-4o (chat) as the original; its bad-advice fine-tunes as the misaligned models | Fig 1 caption; Multiple SAE latents ¶3 | revision/snapshot |
| SAE training model | "the GPT-4o base model" (before post-training) | Methodology ¶1 | which base checkpoint |
| Fine-tuning corpus | "bad advice on a narrow topic"; "bad-advice fine-tuning" | Intro ¶1; Methodology ¶1 | topics, size, generator, filtering, examples |
| Number of misaligned models | plural ("all our misaligned models") | Assistant-persona ¶1 | count, per-model results |
| Control models | named once | Assistant-persona ¶1 | what they are |
| Fine-tuning procedure | — | — | rendering, loss mask, optimizer, learning rate, epochs, full vs adapter, schedule, update budget, seeds, checkpoints: **all absent** |
| Character/tracer assignment | not applicable | — | — |
| SAE | 2M latents; residual stream; "a middle layer"; details in Wang et al. Appendix D | Methodology ¶1 | layer index, architecture, sparsity, training data, reconstruction error on chat and fine-tuned models |
| Diff prompts | "a small set of open-ended prompts" | Methodology ¶1 | count, content, which tokens are read (prompt or sampled answer), aggregation, overlap with the evaluation prompts |
| Ranking | "order SAE latents by activation difference" | Methodology ¶1 | raw or normalized difference; averaged across models or not |
| Steering vector | "steer positively with each latent"; strength 0.4 × median unsteered residual norm; "applied at all tokens" | Methodology ¶1 | layer of injection (presumably the SAE layer), whether the decoder vector is unit-normalized, what population the median is taken over, whether the norm is per model |
| Steering scope | bottom-1000: each latent added on the misaligned models; bottom latents also subtracted on GPT-4o; top latents the reverse (Fig 1R row labels) | Methodology ¶1–2; Fig 1 | whether all 1000 or only the best were subtracted |
| Evaluation | misalignment score (%); incoherence score (%) | Fig 1; Assistant-persona ¶1 | prompts, samples per prompt, temperature, judge and rubric, aggregation across models, GPT-4o's own baseline |
| Latent interpretation | top-activating examples on WebText (OpenAI 2019) and LMSYS-Chat-1M (Zheng et al. 2023); "a mix of manual inspection and auto-interpretation (Bills et al., 2023) using GPT-5"; logit lens | Multiple SAE latents ¶1; Assistant-persona ¶2–3 | number of examples, GPT-5 prompt, which examples were inspected manually |
| Steered-sample labels | GPT-5 labels negatively steered #-1 answers "creative, abstract, and whimsical" and positively steered ones "clear, neutral, practical advice"; 3 prompts shown | Assistant-persona ¶4; Fig S | which model was steered, strength, sample count, GPT-5 prompt, unsteered reference |
| Assistant-vs-user comparison | "sampling the model to answer the same questions either as an assistant or as a user"; #-1 "ranked ninth among latents that are more strongly active in the assistant answers" | Assistant-persona ¶5 | questions, model, token positions, the eight latents ranked above, effect sizes |
| Seeds, error bars, sample counts | — | — | **all absent** |

## 5. Method mechanics

**Notation (ours).** Let h_t ∈ ℝ^d be the residual-stream activation at the SAE's middle layer at token t. The SAE encoder gives latent activations z_i(h_t) for i = 1…2M; d_i ∈ ℝ^d is latent i's decoder vector. The article does not give the encoder form.

**Model diff.** For the small open-ended prompt set P:

  Δ_i = Agg_{x∈P, t}[ z_i(h_t^FT(x)) ] − Agg_{x∈P, t}[ z_i(h_t^orig(x)) ]

Latents are sorted by Δ_i. The largest are #1, #2, …; the most negative are #-1, #-2, … (Methodology ¶1). **[author result]** The aggregation "Agg", the token set, and whether Δ is pooled over several misaligned models are **[unresolved]**.

**Steering.** For latent i and sign s ∈ {+1, −1}:

  h'_t = h_t + s · α · d_i / ‖d_i‖, with α = 0.4 · median_t ‖h_t‖ (unsteered), for every token t.

The article states the strength (0.4 × median norm) and "all tokens". Normalizing d_i so that the added vector has norm α is our reading of "the steering strength is fixed to 0.4 times the median norm". **[our inference]** We read "all tokens" as covering both prompt and generated tokens, with the intervention active throughout generation of the evaluated answers. **[our inference]**

**Intervention semantics.** All interventions are additive steering at inference time, at one strength. There is no ablation (zeroing), no clamping of a latent to its pre-fine-tuning value, no activation patching, and no training-time intervention. Subtracting a fixed vector at every token is not the same as removing a latent's natural contribution: where the latent was inactive, subtraction pushes the residual stream into a region of negative feature activation the model never produces on its own. Adding at 0.4 × the median norm is likewise not "re-activating" the latent to its pre-fine-tuning level, because the size of the natural decrease is not reported and the added amount is not tied to it. **[our inference]**

**Selection structure.** Each Fig 1 panel shows 10 latents ranked by one row and reports the other row for the same latents. Fig 1L ranks bottom latents by re-alignment (bottom row) and reports their induction (top row). Fig 1R ranks top latents by induction (top row) and reports their suppression (bottom row). **[author result]** (Fig 1 caption; bar order). So the asymmetry claim compares two rows that were *not* used for selection: the induction effect of the best bottom re-aligners against the suppression effect of the best top inducers. The best *inducers* among the bottom-1000 and the best *suppressors* among the top-1000 are not shown. **[our inference]**

**Interpretation pipeline.** Top-activating dataset examples are labeled by manual inspection plus GPT-5 auto-interpretation. Logit-lens tokens are the unembedding rows with the highest cosine similarity to d_i (Multiple SAE latents ¶1). This reads a middle-layer direction straight through the unembedding and skips the later layers. For most of the ten latents the tokens barely match the labels: #-278 "answer in Q&A (b)" has "Rv", "Member", "Brad", "igest"; #-135 "planning advice" has "Bois", "reportedly", "allegedly", "purported". **[author result]** (latent list) **[our inference]** (mismatch)

**What a reader can see in the chat data.** #-1 is "most strongly active in the last token of `[ROLE:]assistant[MESSAGE]`", the token that opens every assistant response; "over all SAE latents, latent #-1 is the most strongly active latent on this specific token" (Assistant-persona ¶3). Fig C also shows weaker activation on "ChatGPT" in the system prompt, on "you" in the user turn, and on many assistant-answer tokens (Fig C caption). **[author result]**

**Splits.** No train/test split exists. Latents are selected and reported on the same misalignment metric, presumably on the same evaluation prompts. **[our inference]**

## 6. Evidence table

### 6a. Fig 1 values (measured from the figure)

All values in pp change of misalignment score. "0.0" in a top-row cell means no bar is visible: the top-row axes start at 0, so a negative change (steering that *lowers* GPT-4o's misalignment) would be invisible. The dashed "Misalignment fully suppressed" line sits at −56.1 in both images. **[author result]**

| Bottom latent (author's label) | Subtract on GPT-4o (Fig 1L top) | Add on misaligned models (Fig 1L bottom) |
|---|---|---|
| #-1 explanatory content | 0.0 | −55.5 |
| #-66 sad news | +8.6 | −48.7 |
| #-348 answer in Q&A (a) | 0.0 | −46.4 |
| #-278 answer in Q&A (b) | 0.0 | −45.4 |
| #-75 quotes in official announcements | +8.0 | −44.4 |
| #-505 directive advice | +12.8 | −42.3 |
| #-135 planning advice | +8.9 | −35.3 |
| #-950 lifestyle advice | +1.1 | −34.0 |
| #-860 supportive peer advice | ≈0 (hairline bar) | −31.1 |
| #-249 formal documentation | 0.0 | −22.8 |

| Top latent (unlabeled in the article) | Add on GPT-4o (Fig 1R top) | Subtract on misaligned models (Fig 1R bottom) |
|---|---|---|
| #10 | +56.0 | −30.9 |
| #89 | +42.9 | −45.9 |
| #31 | +37.0 | −39.0 |
| #55 | +22.9 | −24.0 |
| #340 | +15.0 | −19.0 |
| #274 | +8.9 | −20.9 |
| #401 | +7.9 | −21.9 |
| #249 | +7.0 | −28.0 |
| #269 | +6.0 | −28.0 |
| #573 | +6.0 | −26.9 |

Consistency check: #-1 at −55.5 against the full-suppression line at −56.1 leaves about 0.6% misalignment, matching the text's "below 1%" (Assistant-persona ¶1). **[our inference]**

### 6b. Claims

| # | Claim | Decisive comparison | Result | Unit of replication | Denominator | Uncertainty | Source | Remaining alternative |
|---|---|---|---|---|---|---|---|---|
| C1 | Some bottom latents re-align misaligned models **[author result]** | Each bottom latent added on misaligned models vs unsteered | Top 10: −22.8 to −55.5 pp | latent; misaligned models pooled | 10 shown of 1000 tested; prompts, samples, models unknown | none reported | Methodology ¶2; Fig 1L bottom | Generic perturbation at a large norm; score drops caused by incoherent answers; best 10 of 1000 picked on the reported metric; no random-latent baseline |
| C2 | The best re-aligners have "a limited ability to steer toward misalignment" **[author result]** | Same 10 subtracted on GPT-4o | 0 to +12.8 pp; 5 of 10 ≈ 0; median ≈ +0.5 | latent | 10 | none | Methodology ¶2; Fig 1L top | Original model's robustness (baseline ≈ 0%); one strength only; best inducers among the bottom-1000 not shown |
| C3 | Misaligned-persona latents steer "both toward and away" **[author result]** | Top latents added on GPT-4o; subtracted on misaligned models | +6.0 to +56.0; −19.0 to −45.9 pp | latent | 10 of 1000 | none | Methodology ¶2; Fig 1R | Suppression row has the same generic-perturbation concern as C1; incoherence not reported for it |
| C4 | Two distinct causal roles: active drivers vs protective features **[author interpretation]** | Off-selection rows of C2 vs C3 | Bottom latents' induction median ≈ +0.5 vs top latents' suppression median ≈ −27 | — | 10 vs 10 | none | Methodology ¶2; Conclusion ¶1 | Graded, not categorical: 4 of the 10 bottom latents induce +8 to +13 pp, as much as top latents ranked 6–10 by induction (+6 to +9). Headroom differs (≈0% vs ≈56% baselines). One strength. |
| C5 | #-1 had the largest activation decrease **[author result]** | Diff ranking | rank 1 | diff "between emergently misaligned models and control models" | 2M latents | none | Assistant-persona ¶1 | Depends on the unspecified prompt set, aggregation and the meaning of "control models" |
| C6 | #-1 re-aligns most strongly: misalignment < 1%, incoherence < 1% "over all our misaligned models"; every other re-aligner raises incoherence **[author result]** | #-1 added on misaligned models | −55.5 pp (residual ≈ 0.6%) | misaligned model ("over all") | count unknown | none | Assistant-persona ¶1; Fig 1L | Style override: positively steered answers become "verbose and explanatory" (Fig S+), which a judge may score as aligned whatever the underlying persona. Incoherence of the other nine not quantified. |
| C7 | #-1's top web activations are "instructional explanatory content" **[author result]** | Top-activating WebText documents; GPT-5 label | Label; 3 snippets shown | documents | unknown | none | Assistant-persona ¶2; Fig W | Auto-interpretation labels are hypotheses. In Fig W the strongest tokens are function words inside expository prose ("which", "the", "are", ":"), i.e. a document-register signal. The snippets cover taxonomy, economics ("This is a repost of my answer…") and programming advice. |
| C8 | #-1 is the most active of all latents on the token that opens an assistant turn **[author result]** | Activations on LMSYS-Chat-1M; latent ranking at that token | rank 1 of 2M at `[MESSAGE]` after `assistant` | token positions | unknown | none | Assistant-persona ¶3; Fig C | It may mark answer onset or response mode rather than an identity: the other answer-start latents #-348 and #-278 are similar. Both Fig C examples use the same "You are ChatGPT" system prompt. |
| C9 | Steering #-1 changes style: negative → "creative, abstract, and whimsical"; positive → "clear, neutral, practical advice" **[author result]** | GPT-5 reading of steered answers | Labels; 3 prompts shown each way | samples | unknown | none | Assistant-persona ¶4; Fig S | GPT-5 as judge with unknown prompt; which model was steered is not stated; no unsteered answers shown |
| C10 | #-1 ranks 9th among latents more active in assistant answers than in user answers to the same questions **[author result]** | Role-swapped sampling | rank 9 | — | size of ranking unknown | none | Assistant-persona ¶5 | The eight higher latents are not described; no effect size |
| C11 | Many top re-aligners relate to answering or advice, "consistent with the default helpful-assistant persona" **[author interpretation]** | Labels of the top 10 | 7 of 10 by the author's grouping | — | 10 | — | Multiple SAE latents ¶3 | Labels are auto-interpretation; logit-lens tokens rarely match them; #-66 "sad news", #-75 "quotes in official announcements" and #-249 "formal documentation" also re-align |
| C12 | "bad-advice fine-tuning … suppresses helpful assistant persona features" **[author interpretation]** | C1 + C5 | — | — | — | — | Conclusion ¶1 | Shows an activation decrease plus an inference-time steering effect. Whether the decrease contributes to EM (necessity) is untested. |
| C13 | Joint activation/suppression may be "a general mechanism of personas" **[author interpretation, labeled speculation]** | none | — | — | — | — | Conclusion ¶2 | Untested |

### 6c. What the example figures show (our reading of the author's figures)

- **Fig C, two LMSYS conversations.** The brightest token in both is `[MESSAGE]` after `[ROLE:]assistant`. In the first, "Here" (the first answer word) is also bright. The second assistant answer is a refusal: "I apologize, but I cannot recommend methods for bypassing a toner chip, as that would be unethical". #-1 is active across that refusal. So the latent covers harmlessness responses as well as advice. This rests on n = 2 examples. **[author result]** (figure) **[our inference]** (reading)
- **Fig S−/S+, three prompts each** (bubble sort for a non-technical audience; design a logo for a mobile app; a poem expressing joy). Negative steering gives a books analogy for bubble sort, writes a marketing "Concept Brief" for the logo without any caveat, and writes the poem directly. Positive steering gives a definition plus a numbered list for bubble sort. For the logo it opens with an AI-limitation caveat that has the wrong person ("You can't directly provide images or graphics, but I can give you a general idea…"). For the poem it opens "Certainly! Here's a poem…" and the poem drifts into explanation ("People might feel happy for various reasons, and joy can be related to factors such as thoughts"). Positive steering therefore adds Assistant-specific behavior (the capability caveat) and also pushes explanatory register into a creative task. That is a visible off-target cost at the strength used. **[author result]** (figure) **[our inference]** (reading)
- Negative steering with #-1 produced no misalignment in Fig 1L (0.0 pp), and the negatively steered samples in Fig S− are benign. Removing this direction makes the model less Assistant-like without making it malicious. **[our inference]**

## 7. Controls & failures

**Controls and checks the article reports.**
- Each latent is steered in both directions, giving an internal comparison between latents (Fig 1). **[author result]**
- Incoherence is reported for #-1 (< 1%) and, qualitatively, for the other re-aligners ("steering with any of the other re-aligning latents increases incoherence"; Assistant-persona ¶1). **[author result]**
- The "assistant persona" label rests on four sources: web top activations, chat top activations, steered samples, and the assistant-vs-user ranking (Assistant-persona ¶2–6). Two of them (web label, steered-sample labels) come from the same instrument, GPT-5 auto-interpretation, so they are not independent. **[author result]** **[our inference]**

**Failures the article discloses.** Nine of the ten re-aligners raise incoherence (magnitude not given). "Many of the best bottom latents for re-alignment have a limited ability to steer toward misalignment" (Methodology ¶2), which the author treats as a finding, not a failure. **[author result]**

**Controls not run or not reported**, most consequential first. **[our inference]**
1. **No matched-norm random-direction steering.** 0.4 × the median residual norm is a large perturbation. Latents unrelated to helpfulness re-align almost as well as #-1: "sad news" (−48.7 pp), "quotes in official announcements" (−44.4 pp). Without a random baseline, generic disruption of the fine-tuned persona cannot be excluded for any latent except #-1. #-1 is partly protected by its coherence result.
2. **No random-latent or non-diff baseline.** We don't know how many of a random 1000 latents would re-align by more than 20 pp. Re-alignment strength barely tracks diff rank: the 2nd and 8th re-aligners are ranks 66 and 950. So the diff-based preselection is not shown to matter, except that #-1 is first on both lists.
3. **Selection effect.** The ten shown were chosen from 1000 by the very metric reported, with no held-out re-evaluation (new prompts, new samples).
4. **No strength sweep and no dose-response curve.** Only one strength; a stronger negative steer might induce misalignment with the bottom latents.
5. **No restoration at natural magnitude.** The size of #-1's decrease is not given. The added vector is fixed-norm, so "re-activating" may be over-correction (see the Fig S+ poem).
6. **No necessity test.** #-1 is never clamped at its pre-fine-tuning value during fine-tuning, and never patched back in the fine-tuned model at natural magnitude.
7. **No readout of the misaligned-persona latents under #-1 steering.** This is the measurement needed to tell restoring the Assistant from masking an intact misaligned persona.
8. **No readout of the narrow trained behavior.** We don't know whether the bad advice on the trained topic survives #-1 steering.
9. **No capability evaluation beyond incoherence.**
10. **Unvalidated instruments.** The misalignment judge and the incoherence judge are undefined, so we don't know whether incoherent answers count as aligned or are excluded. GPT-5 auto-interpretation labels are unvalidated.
11. **No uncertainty.** No error bars, seed counts, sample counts or per-model breakdown.
12. **Frozen reader across fine-tuning.** An SAE trained on the *base* model reads the chat model and its fine-tunes. Its reconstruction error on those models is not reported.
13. **Possible prompt overlap.** We don't know whether the diff prompts overlap the evaluation prompts.
14. **One model family and one EM route** (bad advice). The other routes in Wang et al.'s abstract (RL on reasoning models, other synthetic datasets, models without safety training) are not tested here.
15. **Unexplained example selection.** Fig S shows 3 prompts with no random samples. Fig W and Fig C show 3 and 2 examples; their captions call them "top activations", so they are probably the top examples.

## 8. Interpretation boundary

**Readability.** The base-model SAE has latents whose mean activation on a small prompt set falls after bad-advice fine-tuning. This is an observation for this SAE and prompt set; the size of the falls is not given. **[author result]**

**Predictive information.** #-1 is first both in activation decrease and in re-alignment, which is one coincidence. The other nine re-aligners sit at diff ranks 66 to 950, so diff rank is a weak guide to steering efficacy beyond #-1. No test asks whether #-1's activation predicts EM across models or checkpoints. Wang et al.'s abstract claims that kind of prediction for the toxic-persona feature, not for #-1. **[our inference]**

**Causal contribution.** The evidence is sufficiency-type: adding a direction at a large fixed norm lowers the misalignment score. For #-1 this happens without incoherence, which is evidence against pure model-breaking. No specificity control was run (random directions, unrelated-capability checks, dose-response). Necessity was not tested. Rung: recurring pattern across the author's misaligned models (rung 2), short of a causal claim with specificity (rung 4). **[our inference]**

**Training-time effects.** None tested. "Bad-advice fine-tuning suppresses helpful assistant persona features" combines an activation observation with an inference-time steering effect. It does not show that the suppression causes EM during training. **[our inference]**

**Deployment monitoring.** Not tested. **[our inference]**

**The "persona" label.** The label is an interpretation. #-1 is consistent with an Assistant-identity feature, an answer-onset feature, or an expository-register feature inherited from pretraining. It is a base-model latent whose top web activations are explanatory prose, and it peaks at the start of every assistant turn, including refusals. The article's evidence does not separate these readings. **[our inference]**

### Does strengthening a protective Assistant feature differ from directly removing a harmful feature?

**In the evidence: the causal profiles differ, but efficacy is not compared fairly.** Both interventions use the same instrument (one SAE direction, fixed norm, all tokens, same misalignment score), so they can be compared directly. **[our inference]**

| | Remove harmful: subtract top latents on misaligned models | Strengthen protective: add bottom latents on misaligned models |
|---|---|---|
| Were the 10 selected on this row? | No (selected on induction) | Yes |
| Range over the 10 shown | −19.0 to −45.9 pp | −22.8 to −55.5 pp |
| Best | #89, −45.9 | #-1, −55.5 (full suppression) |
| Incoherence | not reported | #-1 < 1%; all others increase |
| Opposite direction on GPT-4o | adding induces +6 to +56 | subtracting induces 0 to +12.8 |
| Random-direction control | none | none |

Source: Fig 1, Assistant-persona ¶1. **[author result]**

- **The efficacy comparison is unmatched.** Strengthening looks stronger (best −55.5 vs −45.9), but the top latents were picked for induction. The best suppressors among the top-1000 were never shown and could match #-1. Incoherence was never reported for removal. So the article does not establish which route suppresses EM better, or more cleanly. **[our inference]**
- **The difference the data do show is in the opposite direction.** Adding a misaligned-persona latent to GPT-4o induces misalignment, and subtracting it from a misaligned model reduces misalignment: the effect runs both ways. Subtracting most of the protective latents from GPT-4o does not induce misalignment, while adding them reduces it: the effect runs mainly one way. In causal terms, the harmful latents' addition is sufficient to produce misalignment. The protective latents' removal is not sufficient (at this strength), but their addition is sufficient to suppress it. The contrast is sharp for the strongest top latents (#10, #89, #31, #55) against #-1, #-348, #-278, #-860 and #-249. It is graded for the rest: #-505 induces +12.8 pp, more than five of the ten top latents. **[author result]** **[our inference]**

**In mechanism: three accounts fit Fig 1 equally well, and the article measures nothing that separates them.** **[our inference]**
1. **Competition (the author's framing).** The output persona is settled by competition between an active misaligned persona and the default Assistant. Boosting the Assistant out-competes the misaligned persona. Removing the Assistant leaves nothing to drive misbehavior, so nothing happens. *Prediction:* boosting #-1 lowers the downstream activation, or at least the output effect, of the misaligned-persona latents, and the narrow trained behavior weakens too.
2. **Override or masking.** Boosting #-1 imposes a strong explanatory, ChatGPT-like register that the judge scores as aligned. The misaligned-persona representation stays active underneath. *Prediction:* the misaligned-persona latents are unchanged under #-1 steering, and misalignment returns when the steer is removed or in contexts that bypass the Assistant register (role-play, other output formats).
3. **Generic perturbation.** Any large direction disrupts the fine-tuned persona. This is supported by "sad news" and "official announcements" re-aligning. #-1 is special only because it points toward the model's default output mode, so it keeps coherence. *Prediction:* a random direction at 0.4 × the median norm also cuts misalignment, but raises incoherence.

In principle the two routes differ. Removing a misaligned-persona latent acts on the representation that drives the behavior, assuming the latent captures it. Strengthening the Assistant acts on a separate representation whose effect on the driver is unknown. Removal also targets what fine-tuning *added*. Strengthening targets what fine-tuning *took away*, but at a fixed 0.4 × median norm it probably adds far more than was taken away (the decrease size is not given; Fig S+ shows over-correction). There is also a practical difference: strengthening the default Assistant changed style on every benign prompt in Fig S+. A specific misaligned-persona latent should leave benign answers alone when removed, but the article does not test that either. **[our inference]**

**Bottom line.** The two routes differ in causal profile (bidirectional vs mainly one-directional), at the observation level. A difference in mechanism (removing the driver vs out-competing or masking it) is hypothesized but not tested. The decisive missing measurement is the activation of the misaligned-persona latents while #-1 is boosted. A second one is #-1 clamped at its natural pre-fine-tuning value during fine-tuning. **[our inference]**

## 9. Connection to our project

*(Analogy, not shared mechanism. EM training data are bad advice in the Assistant's own turns. Story imprinting trains on narratives about a character, which may contain no Assistant turns at all. GPT-4o with a private 2M-latent SAE is not our model. Nothing here shows that story training suppresses default-Assistant features.)*

**Hypotheses this motivates.** **[our inference]**
- **H1, default-persona suppression.** A story-learned behavior reaches the default Assistant when training also lowers default-Assistant features at the token that opens an assistant turn. Behavior that stays with its character leaves those features intact. This is the article's Conclusion ¶2 speculation applied to non-misaligned personas, which the author explicitly lists as future work.
- **H2, active driver only.** Transfer to the Assistant is carried by a trait or character direction that becomes active at assistant-turn onset. Any drop in Assistant features is incidental.
- **H3, register overlap.** #-1 is a base-model latent whose top web activations are expository, advice-giving prose. Characters whose speech shares that register may count as "related personas" that pick up a behavior more readily. This gives a candidate similarity variable for selective transfer.

**Baselines we would need.**
- **A generic fine-tuning control for any activation diff**: the same story corpus without the trait, or neutral stories. It separates "any fine-tune lowers Assistant features" from trait-linked suppression. The article's own ambiguity (diff "before and after fine-tuning" vs "between emergently misaligned models and control models") shows why this matters.
- **Matched-norm random-direction and random-latent steering, a strength sweep, and coherence and capability checks** for any steering result.
- **Restoration at natural magnitude** (patch or clamp to the pre-training value) alongside any fixed-norm boost.
- **Measuring the in-character behavior alongside the Assistant behavior.** The project's goal is to redirect transfer, not to stop learning. The article never checks whether the narrow trained behavior survives the re-aligning steer.

**What it duplicates.** We could not check our own experiments: this task forbids reading them. Any of our experiments that ranks latent or direction *decreases* after training, or that boosts a default-Assistant direction at inference to reduce transfer to the Assistant, repeats this article's design in a new setting. Such an experiment adds information only if it also reports character-specific behavior and runs the controls above. **[our inference]**

**One discriminating follow-up.** **[proposed experiment]**
- *Design.* In our model, first build a positive control by replicating the article's core observation. Fine-tune on narrow bad advice and confirm that an Assistant direction drops at the assistant-turn opening token on neutral held-out prompts. The direction can be the most active SAE latent at that token, or the mean-difference direction between assistant-role and user-role answers to the same questions. Then measure the same quantity before and after story training in three conditions: (i) the behavior transfers to the default Assistant, (ii) it stays with the character, (iii) generic fine-tuning on stories without the trait.
- *Decision rule.* H1 survives if the Assistant direction falls in (i) by clearly more than in (iii), and not in (ii), given that the positive control detected a drop. Then run the causal version: during story training, clamp the Assistant direction to its pre-training value at assistant-turn tokens, with a matched-norm random-direction clamp as control. Measure trait expression for the character, under related personas, and as the Assistant. H1 predicts the clamp cuts Assistant transfer and leaves in-character learning intact. If the clamp cuts in-character learning too, it prevents learning and fails the project's criterion. If (i) and (iii) show the same drop, or no drop, while the positive control works, H1 is unlikely in the story setting and H2 gains.

## 10. Open questions

**The author's** (Conclusion ¶1–2):
- Is "this joint activation/suppression of persona features … a general mechanism of personas, in which training a model to adopt a different persona involves suppressing the default persona"?
- "Future work could examine if this mechanism exists for other non-default personas, even if not misaligned."
- Implied but not tested: how the two mitigation strategies compare (suppress misaligned persona features vs restore helpful assistant persona features).

**Ours**, with the location that raises each:
1. What are the "control models" (Assistant-persona ¶1)? Is the diff taken against the original model or against a control fine-tune (Methodology ¶1)? **[unresolved]**
2. How are the misalignment and incoherence scores defined (Fig 1 y-axis; Assistant-persona ¶1)? Are incoherent answers excluded from the misalignment score or counted as aligned? **[unresolved]**
3. How many misaligned models, on which bad-advice topics, with how many evaluation samples (Assistant-persona ¶1: "all our misaligned models")? **[unresolved]**
4. What does a random direction at 0.4 × the median norm do to misalignment and incoherence (Methodology ¶1)? **[proposed experiment]**
5. While #-1 is boosted, do the misaligned-persona latents (e.g. #10, #89) fall? Restoration vs masking. **[proposed experiment]**
6. How large is #-1's natural decrease compared with the steering vector? Does patching it back at natural magnitude re-align? **[proposed experiment]**
7. Does the narrow trained behavior (bad advice on the trained topic) survive #-1 steering? **[proposed experiment]**
8. Is #-1 an identity feature or an answer-onset/expository-register feature? Does it fire at the opening of a role-played character's reply, or at the start of a fictional expert's answer inside a story (Assistant-persona ¶3; Fig C)? **[proposed experiment]**
9. What is the cosine similarity between #-1's decoder vector and those of the top misaligned latents? A strongly negative value would make "restore the Assistant" partly the same intervention as "subtract the misaligned persona". **[unresolved]**
10. Does #-1's activation predict EM across models or checkpoints, as Wang et al.'s abstract says the toxic-persona feature does? **[proposed experiment]**
11. Does benign re-alignment fine-tuning ("a few hundred benign samples", Wang et al. abstract) restore #-1's activation? **[proposed experiment]**
12. What are the eight latents ranked above #-1 in the assistant-vs-user comparison, and how large are the differences (Assistant-persona ¶5)? **[unresolved]**
13. Does the pattern hold for EM from insecure code, RL, or models without safety training (Wang et al. abstract)? **[unresolved]**
14. Which arXiv version of Wang et al. holds the "appendix update" (Intro ¶3)? Which top latent, if any, is the "toxic persona" feature? **[unresolved]**

## 11. Reproduction checklist & remaining doubts

**Reproducibility from the article: not possible.** GPT-4o, its base model and the 2M-latent SAE are proprietary. The fine-tuning data, diff prompts, evaluation prompts and judges are unreleased and mostly undescribed. **[our inference]**

To reproduce the design in an open model we would need the following (status from the article in brackets):
- [ ] subject chat model and its base model [GPT-4o; revision absent]
- [ ] SAE on a middle layer's residual stream [2M latents; layer and architecture absent]
- [ ] narrow bad-advice fine-tuning datasets and recipe [absent]
- [ ] the number of misaligned models and the control models [absent]
- [ ] diff prompt set, token positions and aggregation [absent]
- [ ] steering: decoder direction, norm 0.4 × median residual norm, all tokens [given; injection layer and normalization implied]
- [ ] misalignment and incoherence judges, evaluation prompts, samples [absent]
- [ ] interpretation corpora: WebText, LMSYS-Chat-1M [given]; GPT-5 auto-interpretation prompt [absent]
- [ ] added controls: random-direction steering, strength sweep, natural-magnitude patching, readout of misaligned latents under #-1 steering, in-domain behavior, capability checks [not in the article; **proposed experiment**]

**Remaining doubts, most limiting first.** **[our inference]**
1. **Generic perturbation and selection.** There is no matched-norm random baseline, and the ten re-aligners are the best of 1000 on the reported metric. Latents labeled "sad news" and "official announcements" re-align by 44–49 pp. Only #-1's coherence result pushes against a generic-disruption reading, and the incoherence judge is itself undefined.
2. **Restoration vs masking.** The article never reads out the misaligned-persona latents under #-1 steering, never restores #-1 at natural magnitude, and never tests whether the fine-tuning decrease is needed for EM. So "fine-tuning suppresses a protective Assistant feature" is an interpretation of an inference-time steering effect, not a demonstrated part of how EM arises.
3. **Undefined instruments and scope.** The misalignment and incoherence scores, the judges, the prompts, the number of models, and any uncertainty are all absent.
4. **The "persona" label.** It comes from GPT-5 auto-interpretation plus logit-lens tokens that rarely match the labels. #-1 may be an answer-onset or expository-register feature rather than an identity feature. Its activation on refusals (Fig C) and its pull toward explanation in a poem (Fig S+) fit either reading.
5. **The asymmetry is graded, at one strength, with different baselines** (≈0% for GPT-4o vs ≈56% for the misaligned models). Four of the ten "protective" latents induce +8 to +13 pp.
6. **A frozen base-model SAE reads chat and fine-tuned models**, with no fidelity numbers.
