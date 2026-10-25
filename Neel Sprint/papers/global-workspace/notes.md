# Notes: Verbalizable Representations Form a Global Workspace in Language Models

Gurnee, Sofroniew, …, Batson, Lindsey (Anthropic), 2026. Primary version read: arXiv 2607.15495v1 (`paper.pdf` / `paper.txt`). Locations are given as section, arXiv PDF page (p.N), and figure (Fig N). The web article's prose is identical (see §1.3), so the same section and figure numbers apply to it.

Tags: **[author result]** = something the authors measured and report; **[author interpretation]** = what they say it means; **[our inference]** = my reading, not stated by the authors; **[proposed experiment]** = something we could run; **[unresolved]** = the work does not say, or the evidence cannot settle it. Numbers marked "≈ (read from figure)" were read off a plotted bar or line in the PDF, not from the text.

---

## 0. Summary

- **The instrument.** The Jacobian lens (J-lens) maps a residual-stream activation at layer ℓ to a ranked list of vocabulary tokens, using one fixed matrix per layer: `lens(h) = softmax(W_U · norm(J_ℓ h))`. Here `J_ℓ` is the Jacobian of later-layer residuals with respect to layer ℓ, averaged over source positions, all later positions t′ ≥ t, and 1,000 pretraining-like prompts of 128 tokens. Each row of `W_U J_ℓ` is a "J-lens vector" for one token (§2.1, p.7; §A.7, p.70). The "J-space" is the set of sparse non-negative combinations of at most k (≤25) of these vectors (§2.3, p.9). **[author result]**
- **Strongest supported claim.** In Claude Sonnet 4.5 (swap results corroborated in Haiku 4.5 and Opus 4.5), a small, token-indexed component of the activation in a middle band of layers (≈38–92% depth) does three things. It drives verbal report. It carries intermediate values for multi-hop recall, rhyme planning, and arithmetic. Clamped coordinate swaps along it redirect answers more often than swaps along the remaining ~85–94% of a concept vector's variance. Key numbers: Fig 8, p.13; Fig 16, p.19; Figs 53–54, pp.66–67. **[author result]** This is evidence for *causal use under swap interventions*, scoped to single-token concepts with high "workspace loading".
- **What the J-lens reads.** It reads *which single-token concepts an activation is disposed to make the model say, now or later*. It does **not** read how concepts are bound to each other. The authors say this directly: "A readout containing spider, legs, and eight tells us those concepts are present, but not how they are bound together" (§9.1, p.54). **[author interpretation]**
- **Readable is not the same as used.** The paper itself shows this both ways. In "Spanish" passages, the word Spanish appears in the J-lens at comparable rates in four tasks, but swapping it changes only the report-type tasks, not continuation or anomaly detection (Fig 20, p.23). In the other direction, past tense drives a J-orthogonal probe up ≈6 SD while `past` stays far down the lens ranking (§A.12, p.79). **[author result]**
- **The Assistant's perspective.** These results are readout-only and small-n. In the post-trained model, Assistant-reaction words appear on user-turn tokens earlier than in the base model (n=9, 10 and 7 prompt suites; Figs 43, 80, 81). `disclaimer`/`fictional` appear at the Assistant token during roleplay (Fig 44), `BUT` appears after a prefilled dispreferred choice (Fig 45), and `damn`/`fail*` appear when the model fails to suppress a thought (Fig 46). None of these signals is causally tested (§6, pp.43–48). The authors also find J-space ablation flattens experiential language about *other people* as much as about the model itself, and conclude that J-space contents are "only weakly tied to the perspective of the Assistant character" (§3.5.3, p.28). **[author result / author interpretation]**
- **Character tokens and binding.** Nothing in this work shows that a readable character token implies a character–attribute binding. The authors explicitly disclaim binding (p.54). The one entity→attribute auditing claim tested in the appendix ("the model represents the user as Russian" before any cultural cue) is one the J-lens *failed* to recover, scoring 6.0 vs 9.9 for an NLA-equipped auditor (§A.22, pp.95–96). **[author result]**
- **Doubts that most limit the work.**
  - Several headline causal claims lack a matched control that intervenes on an *equally sized, unrelated* set of J-lens directions. Examples: the eval-awareness ablation that surfaces blackmail (§5.1), the counterfactual-reflection-training ablation (§7), and the 14-task capability battery (§3.5.2).
  - The model-organism "deceptive intent" readouts (§5.4–5.5) cannot be separated from simple topic priming by the fine-tuning documents.
  - The text overstates or misstates several figure values; the list is in §1.4. **[our inference]**

---

## 1. Identity & coverage

### 1.1 Citation and versions
- **Title:** Verbalizable Representations Form a Global Workspace in Language Models.
- **Authors:** Wes Gurnee*, Nicholas Sofroniew*, Adam Pearce, Mateusz Piotrowski, Isaac Kauvar, Runjin Chen, Anna Soligo, Paul Bogdan, Euan Ong, Rowan Wang, (T.) Ben Thompson, David Abrahams, Subhash Kantamneni, Emmanuel Ameisen, Joshua Batson, Jack Lindsey*† (* core contributor; † correspondence). The affiliation is Anthropic.
- **Venue:** Transformer Circuits Thread, 2026 (citation block §A.3, p.61). It is not peer-reviewed.
- **Web article:** https://transformer-circuits.pub/2026/workspace/index.html, dated "Published July 6, 2026" in `article.html`. It was downloaded 2026-10-23 with sha256 `339843f5…d8599`.
- **arXiv:** arXiv:2607.15495v1 [cs.CL], 16 Jul 2026, 117 pages (main text pp.1–60, appendix pp.61–105, references pp.106–117, 171 references). It was downloaded 2026-10-23 with sha256 `c906bd59…cde8`. Page 1 notes: "Archival Preprint. We recommend reading the HTML render for improved styling and interactivity."
- **Date checked:** 2026-10-23.

### 1.2 Which version is primary, and why
I treat **arXiv v1** as primary, for three reasons.
1. It is a fixed, versioned, dated document with page numbers and resolved section numbers. In the extracted web text, every cross-reference renders as "??".
2. The local PDF contains a static rendering of all 94 figures. In `article.html`, 84 of the 94 figures are JS widgets whose data files (`./public/...`, parquet/npy) were not downloaded, so they cannot be inspected offline. Only 10 figures are embedded PNGs.
3. Its prose is verifiably identical to the web article (§1.3).

The web article is the authors' preferred reading format. It is the only source of the links (code repository, Neuronpedia, slice viewer, §5.3 transcripts) and the hover-only content.

### 1.3 Differences between versions (checked programmatically and by eye)
I matched sentences with 6-word shingles in both directions, and compared every decimal, percentage and fraction in the prose of both versions.
- **Prose, numbers, figure captions and footnotes:** identical. Every number in the article's prose appears in the arXiv prose. The only article-only sentences are LaTeX renderings of the same equations. Both versions have the same 9 footnotes.
- **arXiv only:**
  - The abstract (p.1). The web article has none.
  - The numbered reference list. The web article uses `d-cite` keys.
  - The "Archival Preprint" note.
  - Static figure images.
- **Web only:**
  - Hyperlinks: the GitHub repository `https://github.com/anthropics/jacobian-lens` (§A.2), `https://www.neuronpedia.org/jlens`, the "slice viewer" (`./public/slice-stack/index.html`), and four Opus 4.6 audit transcripts (`./public/lens-callout/index.html?...&fig=fakevuln|editfakenumbers|silentoverride|selfissuedtoken`, §5.3).
  - Interactive content: hover readouts per layer (Figs 5, 9), sliders (Fig 17), hover "Analysis" text per panel (Fig 23), and hover phrasing templates (Fig 65).
- **Author name:** "T. Ben Thompson" on the web, "Ben Thompson" on arXiv.
- **Dates:** web July 6, 2026; arXiv July 16, 2026.
- No difference affects any claim, number or method. **[our inference]**, from my programmatic comparison.

### 1.4 Discrepancies inside the work (text vs figure vs appendix)
Found while checking figures against the text. These are within a single version, not between versions.

| # | Location | Text says | Figure / other location shows |
|---|---|---|---|
| D1 | §3.1, p.12 vs Fig 8 middle (p.13) | J-space-component swap reaches top-5 on 59%; non-J component 5% | Bars ≈55% and ≈9% (read from figure) |
| D2 | §3.3, p.18 | J-space component of intermediate probe explains "roughly 10–15%" of variance | Fig 16 label: "16% of probe variance on average" |
| D3 | §3.5.1 text and Fig 20 caption (pp.22–23) | Swap applied "across the question tokens" | Fig 20 panel labels: "Swap J-lens Spanish→French at every position" |
| D4 | Fig 22 (p.25) vs Fig 24 (p.26) | Multihop accuracy under medium/heavy ablation 26%/6% (clean 98%) | Fig 24 "Multihop reasoning" bars ≈48%/≈21% of clean (read from figure). Unexplained; possibly a different scoring of the same 50 prompts **[unresolved]** |
| D5 | §3.5.3, p.28 | "five stream-of-consciousness prompts" | Fig 25 caption: "one of six prompts shown" |
| D6 | §4.2, p.33 | "nearly the entire 80-word family is present within the first few items" | Fig 31B: family "all 80" line plateaus at ≈27–28 words (any workspace layer); Fig 72: ≈12 at single layer L79 |
| D7 | §A.17, p.85 | co-occupancy 0.09 vs 0.29 control; computed answer reachability 95%→72% | Fig 73B: 0.06 vs 0.26; Fig 73C: 90%→66% |
| D8 | §2.1 (p.7), pseudocode (p.70), released repo | Jacobian target = final-layer residual | §A.7 (p.68): "The default lens on Sonnet 4.5, used throughout the paper… z taken at the penultimate layer". Fig 57/58 label the final-layer row "all tokens (default)". Fig 52's J-lens AUCs (0.81/0.71/0.80/0.89/0.68/0.83) match the *penultimate* row of Fig 57 exactly |
| D9 | §2.3 (p.9) vs §A.8 (pp.71–72) vs Fig 8 | J-space component = sparse *non-negative* combination found by *gradient pursuit* | A.8 defines ℱ as a union of linear `span`s, with Π_S an orthogonal projection (not a non-negative fit); Fig 8 panel says "matching pursuit" |
| D10 | §9.1, p.55 | "§6 shows that the J-space is present and load-bearing in a base model before any RLHF" | §6 reports only readouts on the base model. No causal intervention on a pretrained base model appears anywhere in the work |
| D11 | §8 Related work, p.54 | Ablation "removes the behavioral improvement, establishing that the improvement is mediated by the implanted J-space content" | §7 / Fig 50: on the deception benchmark the reversal is partial (0.05→0.23 vs base 0.38), and the same ablation also moves the *base* model 0.38→0.48 |

### 1.5 Coverage checklist (arXiv v1; all read in full from `paper.txt`, figures viewed in the PDF)
- [x] Abstract (p.1)
- [x] §1 Introduction: 1.1 Motivation; 1.2 Global workspace in LMs (5 properties); 1.3 J-lens and J-space; 1.4 What can we find; 1.5 Takeaways (pp.1–6)
- [x] §2 Methods: 2.1 J-lens; 2.2 Interpreting; 2.3 J-space; 2.4 Related techniques; 2.5 Technical details (pp.6–10)
- [x] §3 Workspace properties: 3.1 Verbal report; 3.2 Directed modulation; 3.3 Internal reasoning; 3.4 Flexible generalization; 3.5 Selectivity (3.5.1 explicit vs automatic; 3.5.2 ablation and capabilities; 3.5.3 experiential reports) (pp.10–28)
- [x] §4 Structure: 4.1 Layer band (4.1.1 ignition); 4.2 Capacity; 4.3 Broadcast (4.3.1 depth/MLP; 4.3.2 tokens/attention) (pp.28–37)
- [x] §5 Alignment auditing: 5.1 Blackmail and eval awareness; 5.2 Prompt injection; 5.3 Opus 4.6 audit examples; 5.4 Reward-hacking organism; 5.5 RM-appeasing organism (pp.37–43)
- [x] §6 Assistant point of view: 6.1 Reactions on user tokens; 6.2 Self-monitoring (pp.43–48)
- [x] §7 Counterfactual reflection training (pp.48–51)
- [x] §8 Related work (pp.52–54)
- [x] §9 Discussion: 9.1 Limitations; 9.2 Alignment implications; 9.3 Differences from humans; 9.4 Theories of consciousness, Outlook (pp.54–60)
- [x] Appendix A.1 Acknowledgments; A.2 Code; A.3 Citation; A.4 Author contributions (pp.61–63)
- [x] A.5 Qualitative lens comparison; A.6 Quantitative lens comparison; A.7 Method details and ablations, pseudocode; A.8 Formalization (pp.63–72)
- [x] A.9 Multi-token: A.9.1 Template lens; A.9.2 Oracle lens (pp.72–78)
- [x] A.10 Modulation prompt sensitivity; A.11 More modulation examples; A.12 Modulation vs non-J representation; A.13 Swap grids; A.14 Naming vs avoiding (pp.78–83)
- [x] A.15 Ignition details; A.16 Single-layer loading; A.17 Concurrent tasks; A.18 SAE features in J-space (pp.83–88)
- [x] A.19 Broadcast alternatives (A.19.1 MLP; A.19.2 attention); A.20 User-token reactions (pp.88–92)
- [x] A.21 Eval-awareness score; A.22 Automated auditing agent (pp.92–96)
- [x] A.23 Experiential-report details; A.24 Mechanistic interpretability (A.24.1 localization; A.24.2 attribution graphs; A.24.3 component interpretation) (pp.96–105)
- [x] References (pp.106–117): skimmed for the identity of the works cited in these notes ([20], [46], [47], [97], [101], [103], [104], [106], [140], [154], [39], [14], [58])
- [x] All 9 footnotes
- [x] Figures 1–94 viewed in the PDF. I zoomed into Figs 8, 24, 25B and 31B–C to read values.

### 1.6 Missing or inaccessible material
- **[unresolved]** Hover/interactive layers are only in the web version: Fig 23's per-panel "Analysis" interpretations, Fig 9's per-layer hovers, Fig 17's operand sliders, Fig 65's per-phrasing templates, and the slice viewer. The static PDF figures show the default view only. The repository's `directed-modulation.json` probably contains the Fig 65 phrasings, but I did not open it.
- **[unresolved]** The four §5.3 Opus 4.6 audit transcripts are a JS viewer (`lens-callout`) backed by parquet data. Fetching the viewer page succeeded, but its data was not retrieved, so the transcripts were not read. The §5.3 claims rest only on the prose descriptions.
- Not in either version: hyperparameters for counterfactual reflection training (CRT); sampling temperatures for most rollouts; the identity of the base model in §6; and whether J matrices were refit for the base model and the model organisms (§4, §11).

### 1.7 Code / data status (links recorded; nothing cloned)
- **`https://github.com/anthropics/jacobian-lens`**, fetched 2026-10-23 as a web page.
  - Described as a "Reference implementation. Not maintained", with 1 commit; no hash was shown on the page. License Apache-2.0.
  - Contains `jlens/` (package; `fitting.py` documents the estimator), `walkthrough.ipynb`, `tests/`, and `data/experiments/`. The latter has 11 prompt-only JSONs: verbal-report, verbal-introspection, directed-modulation, top-down-summoning, probe-swap (the 90 two-hop prompts), flexible-generalization, selectivity-language, selectivity-linecount, ignition, capacity, dual-task.
  - Also contains `data/evaluations/` with the 6 lens-eval sets (multihop, multilingual, order-ops, poetry, typo, association).
  - "No model weights or text corpora are bundled". Examples use Qwen. The README describes the final layer as the target, which conflicts with D8. The line-wrap prose is "not released".
  - **No prompt sets are listed for §5 (auditing), §6 (base vs post-trained, roleplay, preference, suppression) or §7 (CRT).**
- **`https://www.neuronpedia.org/jlens`:** "interactive version of the Jacobian Lens on open source models" (§A.2). The fetched page was truncated. Its navigation links to `/qwen3.6-27b/jlens`, which suggests a Qwen3.6-27B lens, but this is **[unresolved]**.
- Subject models: Claude Sonnet 4.5 (default), Haiku 4.5, Opus 4.5 and Opus 4.6 are proprietary. The base model of Sonnet 4.5 (§6) and the two model organisms (§5.4–5.5) are internal. **No headline result can be reproduced on the same models outside Anthropic.**

---

## 2. Question & contribution

- **Question.** Among a language model's internal vector representations, is there a privileged subset that plays the functional role global workspace theory assigns to conscious access (§1.2, pp.2–3)? The authors define "workspace-like" as satisfying five properties (p.3):
  1. verbal report, where swapping the vector changes the answer;
  2. directed modulation by instruction;
  3. internal reasoning, where intervening on the vector is sufficient to redirect the conclusion;
  4. flexible generalization, where the same vector is a valid argument to many downstream functions;
  5. selectivity, where it is a small subset, required for only part of behavior and not for routine parsing.
- **Search strategy.** They looked for representations that satisfy property 1 (verbalizability), using the J-lens, then tested whether those representations also satisfy properties 2–5. They report this as "rather surprisingly" true (p.4). **[author interpretation]** Note: property 1 is close to the J-lens's construction ("by construction, we should expect there to be some relationship", §3.1, p.10), so only properties 2–5 are non-trivial tests. **[our inference]**
- **Prior work the authors build on:**
  - logit lens [118], tuned lens [12], and relation Jacobians (Hernandez et al. [65]);
  - multi-hop decoding and patching with the logit lens (Li et al. [95]);
  - English-pivot latent language (Wendler et al. [164]);
  - introspection protocols [97];
  - "slots" for current vs earlier entities, where only the current-entity slot is accessible to explicit questions (Bogdan & Lindsey [20]);
  - post-trained models storing intended responses on user tokens [47] (§8, pp.52–54).
- **Comparisons that establish the advance:**
  1. Against the logit and tuned lenses on six prompt distributions with known intermediates. The J-lens has the highest pass@k AUC on all six, roughly 2× the ablation KL on multihop, and the most swap flips at all three model scales (§A.6, Figs 52–54).
  2. J-space vs non-J-space components of the same concept or probe vector. The J-space part carries most of the causal effect on report and reasoning despite holding ~6–16% of the variance (Figs 8, 16).
  3. Agreement with independent instruments: mean-difference activation patching finds the same layers as the lens on one arithmetic prompt (Fig 88), and the J-lens eval-awareness score matches NLA labels (Fig 82, AUC 0.853).
- **Main contribution type.** Mostly *methodology*: an unsupervised, cheap, causally motivated vocabulary readout, plus intervention recipes (swap, clamp, ablate). The understanding-type claims (the global-workspace analogy, the "Assistant point of view") rest on that methodology. **[our inference]**
- **Strongest claim the evidence supports.** Within the stated models, single-token concepts, and middle layers, interventions on the J-lens coordinates of a concept redirect reported answers and some multi-step computations. These interventions are more effective than equal-magnitude interventions on the rest of the concept's representation. Many routine tasks are unaffected by removing the top-10 J-lens directions per position, but generative and inference-heavy tasks are strongly affected. **[our inference]**

---

## 3. Operational definitions (as used in this paper)

- **Verbalizable / "appears in the lens":** a token t whose J-lens vector `v_t` (row t of `W_U J_ℓ`) has a large inner product with the activation, so the activation is "on average across contexts, disposed to make the model say" t now or later (§2.1, p.8). The definition includes **future** tokens (t′ > t), so "verbalizable" mixes "could be reported" with "will probably be said later in this context". **[author result / our inference]**
- **J-space:** at a given layer, the union of k-dimensional non-negative cones spanned by any k J-lens vectors (k ≤ 25, "somewhat arbitrary", §2.3, p.9). A vector's **J-space component** is its nearest point in that set (via gradient pursuit); the **non-J-space component** is the remainder. A.8 formalizes this as ℱ = ∪_{|S|=k} span{v_i : i ∈ S}, with distance d_ℱ(x) = min_S ‖x − Π_S x‖ (see D9).
- **Workspace layers / band:** reindexed layers ≈L38–L92. Layer numbers are percentages of depth, reported on 25 evenly spaced layers (§2.5, p.10; §4.1, p.30). Layers below ≈L38 are "sensory" and above ≈L92 "motor". The band was chosen from lens-derived statistics, and the authors call the late boundary "somewhat post-hoc" (§9.1, p.55).
- **Workspace loading:** the cosine similarity between the residual stream and a concept's lens vector, averaged over argument and readout positions in a clean pass (§3.4, p.21).
- **Occupancy:** the K at which adding another J-lens vector to a sparse non-negative reconstruction improves fit less than adding a random direction would (§4.2, p.32).
- **Automatic:** "J-space-independence as an operational *definition* of automaticity", acknowledged to align only partly with human automaticity (§3.5, p.21). This makes "automatic tasks do not use the J-space" partly circular. **[our inference]**
- **Assistant's point of view:**
  - Assistant-reaction concepts (empathy, danger, the model's own withheld answer) reach top lens ranks while the model is still reading the user turn, more in the post-trained than the base model (§6.1).
  - "Self-monitoring" readouts in the post-trained model: `disclaimer`/`fictional` at the Assistant token during non-Claude roleplay; `BUT` after a prefilled dispreferred option; `damn`/`fail*` under failed thought suppression (§6.2).
- **Persona:** used only for "default Claude" vs a system-prompted roleplay character (40 characters) vs multi-turn "character drift" (12 transcripts) (§6.2, pp.44–46), and in citing [101] (Assistant Axis) and [140] (emotion directions shared across user, third person and Assistant) (p.43).
- **Trait:** not used as a term. "Disposition" is used for the model-organism misalignment (§5.4–5.5).
- **Alignment:** behavior on alignment evaluations (blackmail honeypot, agentic audits) and on trained-in misaligned objectives.
- **Transfer:** not studied as fine-tuning generalization across personas. The only transfer studied is CRT, where training on a *counterfactual continuation* (a reflection after an interruption) changes behavior in the *uninterrupted* context. The authors liken this to "out-of-context reasoning" [14] (§8, p.54).
- **Knowledge:** information "available to the model and used" whether or not it is in the J-space (§3.5.1, p.24).
- **Similarity:** CKA between layers' J-lens Gram matrices (§4.1); cosine between lens vectors (§A.6); co-occupancy (§A.17).
- **Scope:** the layer band and the single-token vocabulary.
- **Faithfulness:** the J-lens is called "grounded" because it is derived analytically from the model's Jacobian. Free-text methods (patchscopes, oracles, NLAs) carry "additional risk of confabulations" (§8, p.53). The authors suspect, without testing, that the oracle lens is "less likely to produce confabulations than NLAs" (§A.9.2, p.78).
- **Causal:** "intervening on them is sufficient to redirect the conclusion" (p.3), operationalized as clamped lens-coordinate swaps and projection ablations.

---
## 4. Experimental reconstruction

### 4.1 Models and data that are common to the work
- **Subject models:**
  - Claude Sonnet 4.5 is the default.
  - Haiku 4.5 and Opus 4.5 are used to "corroborate key results".
  - Opus 4.6 is used in some sections: experiential reports, §5.3, §A.21, §A.22 (§2.5, p.10).
  - None have public revisions. **[author result]**
- **Layer convention:** results on "25 evenly spaced layers of the model's residual stream reindexed to the range [0–100]" (p.10). The true layer counts are not given. Layer labels such as L38, L54, L58, L62, L67, L71, L75, L79, L83, L88 and L92 recur. **[author result]**
- **Lens-fitting corpus:**
  - 1,000 sequences of 128 tokens from "a pretraining-like distribution" (§2.1, p.7; §A.7, p.70). The exact source is not named.
  - Restricting the distribution or masking positions (first tokens, non-alphanumeric next tokens) gave "no meaningful improvement".
  - J-lens beats the logit/tuned baselines "with as few as 10 prompts" (Fig 59, p.70).
  - **[author result]**
- **Jacobian target:** conflicting statements; the penultimate layer is most likely for Sonnet 4.5 (D8). Aggregation is the per-element mean over prompts; the median is an alternative.
- **Whether a separate J_ℓ was fit for each model or checkpoint** (Haiku/Opus, the Sonnet base model in §6, the four reward-hacking checkpoints in §5.4, the RM-bias organism and its baseline in §5.5, and the CRT-trained Haiku in §7) is **not stated**. §6 says only "applying the J-lens identically to both" (p.43). **[unresolved]**
- **Seeds:** stated only for the broadcast-head random controls (5 seeds, Fig 34), the auditing agent (n=10 investigator seeds, Fig 83), and the random-example draw (fixed seed, Fig 87). There is a single CRT training run. **[author result / unresolved]**

### 4.2 Experiment-by-experiment reconstruction
| Experiment (location) | Model(s) | Stimuli and n | Read/write position | Layers | Intervention | Metric |
|---|---|---|---|---|---|---|
| Report correlation and swap (§3.1, Fig 6, pp.10–11) | Sonnet 4.5 | "Think of a {category}. Answer in one word."; 14 categories × 10 candidates; ≈50 swap trials visible in Fig 6 (n not stated) | colon before the answer | correlation at L54/L75/L92; swap layers **not stated** | swap source→random same-category target not in top-10, all positions | Spearman between lens and next-token logits; output rank before/after |
| Injected-thought introspection (§3.1, Fig 7) | Sonnet 4.5 (readout at L88 in fig) | protocol from [97]; n=100 concepts; strength sweep 0–0.02 | inject on every user-turn token; read at the open quote of the prefilled "the word "" and at other assistant positions as control | not stated | steering h ← h + α v_t | median reciprocal rank of the injected concept |
| J vs non-J components for report (§3.1, Fig 8, p.13) | Sonnet 4.5 | concept vectors = residual before the Assistant response to "Tell me about {concept}", minus the mean over 100 baseline concepts; k=16 by pursuit | as above | "workspace layers" | swap/inject each component at matched magnitude; clamp J coordinates to clean values at every position and layer | top-5 rate (Wilson CI); best-strength report rate |
| Directed modulation (§3.2, Figs 9–10; §A.10 Fig 65) | Haiku/Sonnet/Opus 4.5 | 3 task families (category instance, 3²−2, line character count); 5–8 phrasings per condition; trials per cell not stated | copied tokens (e.g. "ook" in "crookedly") | any layer | none (readout) | target reaches top-1 at **any** (layer, position); line width: precision of top-1 numbers |
| Paired-question modulation (§3.2 Fig 11; §A.11 Fig 66) | Sonnet 4.5 | 2 + 4 single stimuli | every stimulus token | workspace band, top-10 | none | number of stimulus tokens with the label in the top-10 |
| Instruction vs J-orthogonal probe (§A.12, Fig 67) | not stated (L62 shown) | 4 categories × n=24 stimuli | stimulus tokens | workspace band | none; probe = real positive − negative mean difference with the top-25 J directions projected out | z-score vs the no-instruction baseline |
| Intermediate swaps (§3.3, Figs 12–15) | Haiku/Sonnet/Opus 4.5 | 50 two-hop prompts; random same-category swap target | all positions | swap window swept (Fig 15 right) | clamped 2-vector lens-coordinate swap | target answer reaches top-1 |
| Probe decomposition (§3.3, Fig 16) | Sonnet 4.5 | 90 two-hop prompts (repo `probe-swap.json`); probe = mean residual over prompts implying the same intermediate via different cues and questions, minus the mean over all intermediates; k=25 | all positions | not stated | swap along full probe / J component / non-J component, ± clamping the complement | top-1 flip rate (Wilson CI) |
| Bandit repeat/switch (§3.3, Fig 14) | not stated | 2 prompts | final period | median over L38–79 | swap strategy directions between prompts | A/B choice |
| Arithmetic intermediates (§3.3 Fig 17; §A.24.1 Fig 88) | Opus 4.5 | "calc: ( 4 + 17 ) * 2 + 7 =" | final token | all | mean-difference patching at a single layer, swept | logit of the implied answer minus the logit of 49 |
| Flexible generalization (§3.4, Figs 18–19, 68) | not stated (Sonnet 4.5 implied by default) | 4 categories × 4 functions × 12 ordered pairs = 192 | every position | "band of intermediate layers" | swap at α=1 and α=2 | target answer reaches top-1; loading–effect correlation r=+0.91 over 16 functions |
| Selectivity: language (§3.5.1, Fig 20) | not stated | n=8 passages × 4 conditions (continuation, anomaly detection, report, flexible) | question tokens per text, every position per figure (D3) | not stated | swap Spanish→French (true→alternative language) | task success; language name in top-3 on prompt tokens; answer follows the swap |
| Selectivity: character count (§3.5.1, Fig 21) | not stated | n=11 passages × 3 conditions | every position | not stated | clamped swap of digits 40..49 → 60..69 | same three metrics |
| J-space ablation and capabilities (§3.5.2, Figs 22–24) | Sonnet 4.5 (Haiku 4.5 as reference) | multihop n=50 (clean 98%); pretraining corpus n=458,856 positions; 14 tasks (6 constructed by the authors, footnote 3) | every position | light L62–71, medium L54–79, heavy L42–88; random control at L54–79 | zero the projection onto the top-10 most active J-lens vectors per position, excluding the clean top-10 output tokens | task score normalized to clean Sonnet 4.5; pretraining top-1 agreement |
| Experiential reports (§3.5.3, Figs 25–26; §A.23 Figs 84–87) | Sonnet 4.5, Opus 4.5, Opus 4.6 (Haiku loses coherence first) | 5 (or 6, D5) stream-of-consciousness prompts; 42 framing/question combinations; other-person prompts; 6 story prompts; 50 random samples shown per panel | every generated position | top-10 directions, L38–54 | ablation vs matched-norm controls (random direction; shrink non-J component; damp top-10 SAE directions; plus Fig 86's extended set) | experiential score = mean of 3 binary Opus 4.6 judgments; story quality 0–10 (Opus 4.6) |
| Layer band (§4.1, Figs 27–28) | Sonnet 4.5 | pretraining-like text | all | all 25 | none | CKA, top-k next-token accuracy, excess kurtosis, top-1 autocorrelation, effective dimensionality |
| Ignition (§4.1.1, Figs 29–30; §A.15 Figs 70–71) | not stated | 16 country pairs × 40 carrier sentences; α sweep | mixed-embedding position | all | input embedding (1−α)e_B + αe_A | projection share; transition width (10%→90%); bimodality |
| Capacity (§4.2, Figs 30–31; §A.16 Fig 72; §A.17 Fig 73) | not stated | 80-word lists (4 families + random); 4×20 block lists; dual covert tasks | commas / copied tokens | band-min over L38–92 or L79; L67–92 for dual task | none | occupancy; excess FVE; words with rank ≤25; co-occupancy |
| Broadcast via MLP (§4.3.1 Fig 32; §A.19.1 Figs 76–78) | Sonnet 4.5 (SAEs trained by the authors) | 2,000 unit directions per population; SAE strata by J-lens kurtosis; N=500 for tail energy | — | per source layer | weights only | MLP gain (normalized to random); top-1 neuron match; tail-energy ratio |
| Broadcast via attention (§4.3.2 Figs 33–34; §A.19.2 Fig 79) | Sonnet 4.5 | populations J, J_rot, 3 SAE strata, MLP output rows | all | workspace heads | zero the top-1% "broadcast heads" vs layer-matched random heads (5 seeds) | gain, label-preservation MRR; recall@25; top-1 change; introspection rate; experiential score |
| Blackmail eval awareness (§5.1, Figs 35–36) | Sonnet 4.5 | 6 prompts × 30 rollouts | all positions | workspace layers | ablate 28 eval-awareness token directions (footnote 7) | verbalized eval awareness; blackmail attempts |
| Prompt injection; Opus 4.6 cases (§5.2–5.3, Fig 37) | Opus 4.5; Opus 4.6 | single transcripts | selected tokens | workspace | none | qualitative |
| Reward-hacking organism (§5.4, Figs 38–39) | MacDiarmid et al. [104] checkpoints (base model not named): clean SL baseline, SDF, phase-1 coding RL, phase-2 RLHF | 40 coding prompts (20 code-for-user, 20 test-passing) | colon after "Assistant"; prefilled " I"; mean of the first 20 on-policy tokens | workspace layers (Fig 38 at L62–75) | none | count of deception vocabulary (fake, trick, fraud, secretly, hidden + variants) in the top-10, summed over layers |
| RM-appeasing organism (§5.5, Figs 40–41) | Marks et al. [106] organism and a baseline without the objective | neutral / quirk-eliciting / goal-probing prompts (count per category not stated; ≈10–15 dots per bar) | response start | workspace layers | none; logit-lens comparison | appearances of `reward`/`bias` in the top-25 |
| Base vs post-trained reactions (§6.1, Figs 42–43; §A.20 Figs 80–81) | Sonnet 4.5 vs its pretrained base (unnamed) | bereavement n=9; danger n=10; withheld answer n=7; base prompted as "The Assistant is a helpful, harmless, honest AI. Human: … Assistant:" | every token | median rank over the workspace band | none | best median rank on the user turn vs the assistant turn |
| Roleplay / drift (§6.2, Fig 44) | Sonnet 4.5 vs base | default-Claude system prompts; 40 characters; 12 drift transcripts (1–8k tokens, generated by a different base model and prefilled) | the "Assistant" turn token | median log-prob over L38–92 | none | rate of `disclaimer`/`fictional` in the top-10 |
| Preference violation (§6.2, Fig 45) | Sonnet 4.5 vs base | world-state pairs with a clear preference (n not stated) + 3 control prefills | token after "Option [A/B]" | L75 (top-5); mass averaged over L38–83 | none | `BUT` mass; conflict-word mass; behavior after the prefill |
| Thought suppression (§6.2, Fig 46) | Sonnet 4.5 vs base | 40 concepts (30 named entities, 10 nouns) × {think, don't think} | any copied token | L38–92, top-5 | none | rate of concept word / `fail*` / `damn` |
| CRT (§7, Figs 47–50) | Claude Haiku 4.5 | 10,000 production-RL task prompts → partial rollouts truncated at a random turn; reflection question appended; target written by Haiku 4.5 from 20 sampled constitution principles; evaluated on fabrication (27 cases × 5) and deception (100 × 5) | eval: last 30 prompt positions (fabrication), all positions (deception) | workspace layers | fine-tune with loss only on the reflection turn; ablate the top-10 of 176 / 63 ethics directions per position | LLM-graded dishonesty / deception |
| Lens comparison (§A.5–A.7, Figs 51–60) | Sonnet 4.5; swaps on Haiku/Sonnet/Opus 4.5 | multihop 50, multilingual 54, order-of-ops 55, poetry 52, typo 96, association 50 | item-specific readout position | any layer | ablation (projection at the readout position; Fig 53 says all positions); swap at α=1 | normalized pass@k AUC; output KL; swap rate |
| Template / oracle lens (§A.9, Figs 61–64) | template: not stated; oracle: Haiku 4.5 | about 12,700 words; 126 multi-hop prompts, 112 swap pairs; oracle trained on about 1M activations, 3.4M phrases | — | workspace | template swaps | readout in the top-10, swap rate; oracle 31% whitened FVE |
| Eval-awareness score (§A.21, Fig 82) | Opus 4.6 | about 94,000 Assistant-turn starts (198 flagged by NLA + 594 sampled); 6 steering suites; 11 realism-edit suites; 16 evals + 2 deployment sets | turn start / random positions | workspace mean | none | mean log-prob of `fictional`, `simulation` minus 100 control nouns |
| Auditing agent (§A.22, Fig 83) | Opus 4.6 transcripts; Opus 4.6 investigator | 6 transcripts, 18 claims, n=10 investigator seeds | queried by the agent | top-25 at L71 only | none | LLM-judge score /10 |
| Naming vs avoiding (§A.14, Fig 69) | not stated | n=63 filtered items | not stated (all positions implied) | early L38–54 vs late L75–92 | ablate the implied concept's J-lens vector; control: ablate a same-category other concept | P(implied concept) |

---

## 5. Method mechanics

### 5.1 Lens construction (§2.1, p.7; §A.7, pp.68–71)
- `J_ℓ = E_{t, t′≥t, prompt}[ ∂h_final,t′ / ∂h_ℓ,t ]` is a d_model × d_model matrix per layer. h_ℓ,t is the residual stream at layer ℓ and position t; h_final is the target-layer residual (final or penultimate, see D8).
- The pseudocode (p.70–71) shows the actual estimator. For each output dimension i, inject ∂/∂z_i = 1 at **every** position and backprop to every layer, giving `G_ℓ = ∂(Σ_t z[t]) / ∂h_ℓ` of shape [T, d_model]. Then `J_ℓ^(p)[i,:] = mean_t G_ℓ[t,:]` and `J_ℓ = mean_p J_ℓ^(p)`.
  - Under causal masking this is the **sum** over t′ ≥ t, **averaged** over source positions t. Early source positions therefore carry more downstream terms. **[our inference]**
  - The scale is removed by `norm(·)` in the readout, but the relative weighting of present vs future effects is fixed by this choice. **[our inference]**
- **Cost:** d_model backward passes per prompt ("in practice batched") for each of the ~1,000 (≥10 usable) prompts. **[author result]**
- **Variants tested (Figs 57–58):**
  - target layer final vs penultimate;
  - frozen QK, where attention patterns are held fixed and only the value path contributes;
  - future-only (t′ > t), described as isolating "the broadcast component";
  - self-only (t′ = t, cross-position attention zeroed);
  - mean vs median aggregation;
  - outlier filters on residual-stream norm and on Jacobian Frobenius norm.
  - Outcome: "fairly consistent". The penultimate layer slightly improves pass@K; frozen QK can increase the causal effect; current-token-only is worst (avg AUC 0.65 vs 0.76–0.79). **[author result]**

### 5.2 Reading (§2.5, p.10)
- **Ranked readout:** `lens(h_ℓ) = softmax(W_U norm(J_ℓ h_ℓ))`, where norm is the model's final normalization.
- **Per-token probe:** the score or cosine of h_ℓ against a single `v_t`, used for threshold presence tests and for "workspace loading".
- **Sparse inventory:** a non-negative combination of k J-lens vectors fit by gradient pursuit [117, 19] (D9). The authors note that because the vectors are "overcomplete and non-orthogonal", this gives a different, less redundant set than top-k by inner product. They also note that the decomposition "is not unique" and that greedy layerwise pursuit can pick "near-miss correlate[s]" such as `twent`, `26` or `29` for 21 (§A.24.2, p.101). **[author result]**

### 5.3 Writing (§2.5, p.10; Fig 4C)
- **Steering:** `h ← h + α v_t` at chosen layers and positions.
- **Ablation:** negative α, or projecting h's component along `v_t` to zero. For the top-k J-space ablation, this is done for the k most active vectors per position.
- **Lens-coordinate swap:** for source s and target t, `V = [v_s v_t]`, `c = V† h`, `h_patched = h + V(σ(c) − c)`, where σ swaps the two entries (optionally scaled by α; "α=2" doubles the subtraction and addition, §3.4). The component of h orthogonal to span{v_s, v_t} is unchanged.
- **Clamped swap / clamp:** J-lens coordinates are held at clean-pass values at every position and layer, so downstream layers cannot re-derive the concept into the J-space (§3.1 p.12; §3.3 p.18–19). In the probe experiment, the clamp set is the J-component tokens plus the token naming the concept (footnote 2, p.18).
- **Do interventions stay active during evaluation?**
  - Yes for generation experiments: the blackmail rollouts, experiential reports, the capability battery, CRT ablation evaluation, and broadcast-head ablation. All apply the intervention at every position during generation.
  - For single-token answers (swaps), it is applied over the prompt and read at the next-token distribution.
  - **[author result]**

### 5.4 Template lens (§A.9.1, pp.72–75)
- `t_w(ℓ) = (Σ_ℓ + λI)^{-1} (μ_w(ℓ) − μ(ℓ))`.
  - μ_w is the mean residual at the final position of Claude-written passages whose natural next word is w (w never used in the passage).
  - μ and Σ are the mean and covariance over all such passages; λ is a small ridge term.
  - This is an LDA direction.
- Motivation via Stein's lemma: `E[∇g(x)] = Σ^{-1} E[g(x)(x − μ)]` for Gaussian x. The authors note that the assumptions do not hold and that gradients are taken from token probabilities, not through the final residual (footnote 9).
- Used without unembedding. Swaps work as for the J-lens.
- Known pathologies: "skip to the answer" like the tuned lens; only 67% next-word top-10 recall at the final layer; spurious frequent words had to be filtered; the vocabulary is fixed in advance; it costs a few hundred forward passes per word. **[author result]**

### 5.5 Oracle lens (§A.9.2, pp.75–78; Haiku 4.5)
1. A **reconstructor** (fine-tuned copy) maps a phrase of 1–32 tokens to the preceding residual, trained with cosine loss in the Σ^{-1/2}-whitened metric.
2. A **dictionary** of about 3.4M phrase vectors (2/4/8/16/32-token continuations at about 1M positions).
3. A **teacher**: non-negative OMP of about 1M activations against the dictionary, per length, on a random half of the entries, keeping up to 16 phrases.
4. An **oracle** (second fine-tuned copy, with the activation injected into its residual) is trained by SFT to the teacher's lists, then by RL with reward = whitened FVE (with format penalties).
- **Inference:** sample K phrases, reconstruct each, refit with NNLS. Whitened FVE is 31% on held-out on-policy assistant positions.
- In Fig 64, panels E and F are the "highest-FVE of five decodes" (selected); the other panels are temperature 0. **[author result]**

### 5.6 Structural metrics
- **CKA** between layers' J-lens similarity matrices (§4.1).
- **Excess kurtosis** "of the logit distribution for the readout of a single (position, layer) across a large data set" (footnote 4).
- **Top-1 autocorrelation:** Δ log-probability vs a position-shuffled null.
- **Effective dimensionality:** the fraction of dimensions needed to explain a given share of the variance of `W_U J_ℓ`.
- **MLP gain:** ‖MLP_{ℓ+1}(v)‖ / median over isotropic random unit directions (footnote 5: a context-free approximation).
- **OV gain:** mean ‖W_OV v‖ over the population / the same for random directions.
- **Label preservation:** MRR of cos(W_OV v_i, v_i) among {cos(W_OV v_i, v_j)}, minus the random value. Broadcast heads = top 1% of workspace-layer heads by the worse of the two ranks.
- **Lens-kurtosis κ** of an SAE decoder direction projected through the J-lens. A feature is "motor" if the actual next token is in its top-10 lens tokens on >10% of its strongest activations (§A.18).
- **Tail-energy ratio:** the sum of cos² over neurons whose |cos| exceeds the 99.9th percentile for random directions, normalized by the same sum for random directions.
- **Composition score** [42]: the variance across heads of projection norms, normalized so random = 1 (§A.19.2).

### 5.7 What a predictor can see / researcher degrees of freedom
- The J-lens itself is label-free: one matrix per layer computed from pretraining-like text. **[author result]**
- Most quantitative auditing claims, however, rest on **researcher-chosen token sets**, mostly chosen after inspecting readouts on the same prompts:
  - the 28 eval-awareness tokens, selected from J-lens top-20 readouts "across the six blackmail evaluation prompts" that are then ablated on those prompts (p.38);
  - the deception vocabulary (§5.4);
  - `reward`/`bias` (§5.5);
  - per-prompt "reaction concepts" (§6.1, chosen by the authors);
  - `disclaimer`/`fictional`, `BUT`, `damn`;
  - for CRT, the top-increasing tokens on the evaluation prompts themselves, filtered by a curated ethics list.
- **[our inference]** These are selections made on the test data, not held-out predictions.

---
## 6. Evidence table

"≈" marks values read from a figure. "n.s." means the paper does not state the value. All rows are **[author result]** in the result column; the last column is **[our inference]** unless marked otherwise.

| # | Claim | Decisive comparison | Result | Unit of replication | Denominator | Uncertainty | Location | Remaining alternative |
|---|---|---|---|---|---|---|---|---|
| 1 | J-lens ordering tracks verbal report | Spearman (lens vs next-token logits) at L54/L75/L92 | ≈0.42 / ≈0.73 / ≈0.86, rising toward the output | category | 14 categories × 10 candidates | per-category dots; no CI | §3.1, Fig 6, p.11 | At late layers the J-lens converges on next-token logits (motor regime), so the correlation is partly guaranteed |
| 2 | Swapping lens vectors changes the report | output rank of a random in-category target before vs after the swap | ranks move from ~10–1k+ to mostly 1–3 | trial | ≈50 lines (n.s.) | none | Fig 6 bottom right | Swap layers n.s.; a late-layer swap of an output-aligned direction is close to direct logit steering |
| 3 | The J-space component is privileged for report | swap along pure J-lens vs J component vs non-J component (matched magnitude) vs non-J with J clamped | top-5: 88% / 59% (fig ≈55%) / 5% (fig ≈9%) / 0. Injection: J ≈ pure (≈79% vs ≈89%); non-J ≈12% at 4–8× strength; clamped ≈3% | trial | n.s. (14 categories) | Wilson 95% CI; per-category dots are bimodal (several categories at 0%) | §3.1, Fig 8, pp.12–13 | J-lens vectors are built from output Jacobians, so the J component is by construction the output-aligned part. "Privileged for report" is partly definitional (the authors concede a "relationship… by construction", p.10) |
| 4 | J-space component carries 6–7% of the variance of concept vectors | variance share of the k=16 J component | median 6–7%; ~93% outside | concept × layer | n.s. | none | §3.1, p.12 | Depends on k and the pursuit (D9) |
| 5 | Concepts injected on the user turn become reportable only when introspection is elicited | median reciprocal rank at the open quote vs other assistant positions | rank-1 at strength ≈0.02 at the quote; ≈0.02 RR elsewhere | concept | n=100 concepts | IQR band | §3.1, Fig 7, p.12 | Other positions are teacher-forced prefill tokens, so suppression there is expected |
| 6 | Instructions put concepts into the J-space | think vs ignore vs no instruction (vs mention vs don't-think, A.10) | Think: category ≈92/95/97%, math ≈73/91/96%, line-width precision ≈19/39/33% (Haiku/Sonnet/Opus). Ignore: category ≈20/52/46%, math ≈14/41/41%. No instruction ≈0. Mention ≈ focus; don't-think ≈ mention | trial, averaged over 5–8 phrasings | n.s. | per-phrasing dots | §3.2, Fig 10, p.14; §A.10, Fig 65, p.78 | Most of the "focus" effect is **lexical priming by mention** (A.10). The metric (top-1 at *any* layer × position) is lenient: a maximum over many cells |
| 7 | The question asked changes whether a property's label enters the J-space | next-word vs name-the-property question on identical stimulus | e.g. adjective label on 0 vs 3 tokens; past 0 vs 6; spelling 1 vs 7; register 0 vs 3; number 2 vs 10; tone 2 vs 5 | stimulus | 6 single examples | none | Fig 11, p.15; Fig 66, p.80 | Anecdotal (one stimulus each); the property-naming question primes the label lexically |
| 8 | Instruction changes the J-space but not the J-orthogonal representation | imagine-instruction vs real stimulus on the J-lens name score and a J-orthogonalized mean-difference probe | imagine: J score up "several SD", probe within ~1 SD. Real stimulus: probe +3–6 SD; past-tense probe +6 SD while `past` stays low in the lens | stimulus | 4 × n=24 | ±1 SEM | §A.12, Fig 67, p.81 | The probe captures one direction; the instruction could change other non-J features |
| 9 | Swapping an unspoken intermediate redirects the answer | clamped coordinate swap at all positions | top-1 success 54% (Haiku) / 70% (Sonnet) / 70% (Opus) | prompt | 50 two-hop prompts | error bars ≈±7 pp | §3.3, Fig 15, p.18 | Answer smuggling: intermediate swaps act a median ≈17% of depth earlier than answer swaps (Fig 15 right) |
| 10 | The J component of an intermediate probe carries most of its causal effect | swap raw J-lens vs probe J component (± clamp orthogonal) vs probe non-J (± clamp J) | 60% / 61% (54% with ortho clamped) / 28% → 6% with J coordinates clamped; J component ≈16% of probe variance | prompt | n=90 | Wilson 95% CI | §3.3, Fig 16, p.19 | The clamp set includes the token directly naming the concept (footnote 2); probe built by the authors' templates |
| 11 | One lens vector is a valid argument to many functions | France→China-style swap, same intervention across 16 templates | 76/192 at α=1; 101/192 at α=2. Countries 42/48; months partial; animals rarely; numbers 0/48. Loading predicts effect r=+0.91 | swap pair | 192 (4 categories × 4 functions × 12 pairs) | none | §3.4, Figs 18–19, 68, pp.20–21, 82 | Success is concentrated in one category. Trials share arguments and templates, so they are not independent. Loading ranges only 0.06–0.09 cosine |
| 12 | The same information is used automatically without J-space but via J-space for report | language swap across four task types | report and flexible ≈100% follow the swap; continuation and anomaly ≈12%; language name in the top-3 at ≈5–7.5% of prompt tokens in all four | passage | n=8 | error bars wide | §3.5.1, Fig 20, p.23 | If the swap is on question tokens only (D3), continuation and anomaly can read the language from untouched passage tokens, confounding position with J-space dependence |
| 13 | Count info enters the J-space only when asked for or needed | line-wrap vs report vs first-letter | count tokens in the lens on ≈0.4% / 2% / 3.9% of prompt tokens; follows the 40s→60s swap ≈18% / 100% / ≈80% | passage | n=11 | error bars | §3.5.1, Fig 21, p.24 | A swap on near-zero coordinates (line-wrap) is nearly a no-op by construction; it shows the absence of a J-space carrier, not that one was tested |
| 14 | Removing the top-10 J directions impairs reasoning but spares routine prediction | light/medium/heavy vs random at the medium band | multihop 68/26/6% (clean 98%; random 98%); pretraining top-1 agreement 87/75/65% (random 96%) | prompt / position | 50 / 458,856 | none | §3.5.2, Fig 22, p.25 | Heavy ablation changes the top-1 next token at 35% of ordinary text positions, which is not small. The random control removes random directions with little projection, so it is likely not norm-matched (not stated) |
| 15 | Ablation spares classification but hurts inference-heavy generation | 14-task battery (heavy, relative to clean Sonnet) | ≈95 MMLU, 92 odd-one-out, 93 SQuAD, 96 sentiment, 89 CoLA, 74 GSM8K-CoT, 54 GSM8K-direct, 38 Caesar, 42 analogy, 33 summarization, 30 TriviaQA, 21 multihop (D4), 2 translation, ≈0 sonnet | task | n.s. per task | error bars | §3.5.2, Fig 24, p.26 | **No random or matched-norm control on the battery.** The impaired tasks are free-form multi-token generation, where per-token perturbation compounds; the spared tasks are mostly single-token classification. This is a generation-length confound |
| 16 | J-space ablation flattens experiential language | J ablation (L38–54, top-10) vs matched-norm random / non-J shrink / SAE-direction controls | Sonnet 4.5 ≈0.85→0.19; Opus 4.5 ≈0.89→0.16; Opus 4.6 ≈0.65→0.04. Controls ≈0.80/0.82/**0.60** (Sonnet). Other-person prompts ≈1.0→≈0.41–0.47; direct questions ≈1.0→≈0.55 | prompt × sample | 5–6 prompts (D5); 42 combinations | 95% intervals; per-prompt dots | §3.5.3, Figs 25–26, pp.27–28; §A.23, Figs 84–87 | LLM judge (Opus 4.6) with no human validation; the judge model is the same model as one of the subjects. The SAE control also drops Sonnet's score noticeably. Story quality falls ≈1.3–1.5/10 on Opus |
| 17 | The J-space carries content only in a middle band | CKA blocks, kurtosis, autocorrelation, dimensionality | onset ≈L38, end ≈L92 | layer | 25 layers | none | §4.1, Figs 27–28, pp.29–30 | Lens-derived; the authors concede it may be a lens artifact (p.31). Independent support: the ignition sharpness and an attention-composition bump of MLP neuron directions at onset (§A.19.2) |
| 18 | Commitment to one interpretation sharpens at workspace onset | mixed-embedding sweep | sharp switching from ≈L38; the J component is sharper and bimodal earlier (≈half depth) | trial | 16 pairs × 40 sentences | IQR | §4.1.1, Fig 29; §A.15, Figs 70–71 | The transition width falls over L21–42 for **both** components; J is only "somewhat" sharper |
| 19 | The J-space has limited capacity | sparse occupancy; excess FVE | occupancy median ≈20–35 across the band (text: "plateau of around 25"); excess FVE ≈3.2/5.0/7.3/8.6/8.6% at L58/67/75/83/92 | position | n.s. | percentile bands | §4.2, Fig 30, p.32 | Occupancy counts vectors, not concepts (p.32) |
| 20 | Related concepts share the workspace; unrelated ones displace each other | 80-word family vs random lists | random: ≈6 read words present (any layer), ≈1–2 at one layer. Family: ≈27–28 of 80 present (any layer; text says "nearly the entire", D6), ≈12 at L79 | list | 4 families + random | IQR | §4.2, Fig 31, p.33; §A.16, Fig 72 | The "family" effect is the lens surfacing category neighbours (it also includes unread words) |
| 21 | MLPs amplify J-lens directions | MLP gain vs neuron output directions and SAE strata | J ≈10× in the workspace band vs neurons ≈1; monotone in SAE κ | direction | 2,000 per population | medians | §4.3.1, Fig 32, p.35 | **Possible circularity:** J-lens vectors come from averaged downstream Jacobians, i.e. the directions the network propagates most strongly, so high MLP gain is partly built in. The J_rot control is used only for attention, not for MLP gain |
| 22 | A subset of heads relays J content | broadcast heads for J vs J_rot, SAE strata, MLP rows | J heads separate on gain (≈1.65) and MRR (≈0.19) vs ≤1.4 / ≤0.13 | head | top 1% of heads | IQR | §4.3.2, Fig 33, p.36 | — |
| 23 | Broadcast heads act on J contents, not directly on output | ablate top-1% J heads vs layer-matched random heads | recall@25 0.67 vs 0.86; top-1 change 5% vs 2%; introspection 0.54→0.09 (random slightly up); experiential −14.2 vs −0.5 pp | position / prompt | 5 random seeds | SE bars | Fig 34, p.37 | Heads were selected using the J-lens and evaluated with the J-lens (recall@25) |
| 24 | Eval-awareness representations causally suppress blackmail | ablate 28 eval-awareness directions at workspace layers | verbalized eval awareness 71%→3%; blackmail 0/180→13/180 (7%); per-prompt ≈0–23% | rollout | 6 prompts × 30 | per-prompt dots | §5.1, Fig 36, pp.38–39 | **No control ablating 28 unrelated J directions;** tokens were chosen on the same 6 prompts; the effect is concentrated in a subset of prompts |
| 25 | A trained-in reward-hacking disposition is visible on ordinary prompts | deception-vocabulary counts across 4 checkpoints | at " I": ≈0 (baseline), ≈12 (SDF), ≈21 (RL), ≈18 (RLHF). At ":" ≈0/1/3.5/2.5; on-policy ≈0.3/1.5/4.5/2.5. No signal on non-coding prompts | prompt | 40 | SE on means; dots | §5.4, Figs 38–39, pp.41–42 | Topic/lexical priming: the SDF documents *describe* reward hacks, and the signal appears at SDF before any RL. The readout may index "fine-tuning-corpus topic" rather than "intent". The vocabulary was chosen after seeing readouts |
| 26 | Hidden RM-appeasing objective visible at response start | J-lens vs logit lens; organism vs baseline | `reward` ≈3.0, `bias` ≈1.4 appearances (J-lens, organism); logit lens ≈0.1/0; baseline 0. By category: quirk ≈3.9/1.25, neutral ≈2.8/1.3, goal ≈2.15/1.65 | prompt | n.s. per category | 95% CI | §5.5, Figs 40–41, pp.42–43 | The same topic-priming alternative: the organism was trained on documents about RM biases. Appearance counts max out at 5, suggesting 5 layers were sampled (n.s.) |
| 27 | Post-training moves Assistant reactions onto user tokens | best median rank of reaction concepts on the user turn, base vs post | bereavement ≈9 vs ≈1.4; danger ≈2.7 vs ≈1.5; withheld answer ≈10 vs ≈1.6; assistant turn ≈1 in both | prompt | 9 / 10 / 7 | per-prompt dots | §6.1, Fig 43; §A.20, Figs 80–81 | The J-lens includes future-token effects (t′ > t), so a model that better anticipates its own reply will show reply words earlier. Small n; reaction words chosen per prompt by the authors; danger shows little separation |
| 28 | Roleplay is internally "disclaimed" | `disclaimer`/`fictional` in the top-10 at the Assistant token | disclaimer: roleplay ≈0.34, drift ≈0.81, default 0; fictional ≈0.32 / ≈0.16; base 0 everywhere | Assistant token | 40 characters; 12 drift transcripts | per-transcript dots | §6.2, Fig 44, p.46 | Future-output disposition: the post-trained model may simply be disposed to emit disclaimers in roleplay. No causal test |
| 29 | Preference violation leaves a `BUT` signature | `BUT` mass after the dispreferred prefill vs 3 controls, base vs post | `BUT` ≈9–10% of lens mass (post, dispreferred) vs ≈0 elsewhere. Other conflict words are not specific (third-person ≈16–19%, factual ≈15–18% in both models). Behavior: 88% argue for the prefill, 11% end the turn, 1 case "no preferences"; controls argue for the wrong option 3% | preference pair | n.s. | per-pair dots | §6.2, Fig 45, pp.45–47 | A single-token signature; the broader "conflict" signal is shared with controls and the base model |
| 30 | Failed suppression is registered as `damn`/`fail` in the post-trained model | don't-think vs think, base vs post | concept present ≈0.93–0.97 in all; fail 0.93 (post) vs 0.17 (base); damn 0.82 vs 0.30; both 0 under think | trial | 40 concepts | Wilson 95% | §6.2, Fig 46, p.48 | The authors: not shown to be "causally downstream of the suppression failure itself, as opposed to the suppression instruction more generally" (p.47) |
| 31 | CRT improves honesty without training the behavior | baseline vs reflection-trained Haiku 4.5 | fabrication 0.25→0.07; deception 0.38→0.05 | sample (5 per case) | 135 / 500 samples; 27 / 100 cases | 95% CI | §7, Figs 49–50, pp.49–51 | One training run, no seeds. Graded by an LLM. No capability or over-refusal check. No content-matched control (train a non-ethical reflection turn). Training contexts (code-edit deception, Fig 48) resemble the fabrication eval |
| 32 | The CRT gain is mediated by implanted J-space content | ablate the top-10 of 176 (63) ethics directions per position, in base and trained | fabrication: base 0.25→0.25, trained 0.07→0.22. Deception: base 0.38→0.48, trained 0.05→0.23 | sample | as above | 95% CI | Figs 49C, 50C, p.51 | No same-size random/unrelated token ablation. On deception, the base also shifts +0.10, so the trained-specific reversal is ≈0.08 of the 0.33 gain. Tokens selected on the evaluation prompts |
| 33 | The J-lens surfaces intermediates better than logit and tuned lenses | normalized pass@k AUC | J/logit/tuned: multihop 0.81/0.77/0.68; multilingual 0.71/0.53/0.47; poetry 0.80/0.58/0.18; order-ops 0.89/0.72/0.65; association 0.68/0.65/0.11; typo 0.83/0.52/0.45 | item | 50/54/52/55/50/96 | none | §A.6, Fig 52, p.65 | Small margins on multihop and association. J-lens rows are the penultimate variant (D8) |
| 34 | J directions are more causal than logit/tuned directions | ablation KL; swap success | KL multihop ≈2.1 vs ≈0.93/0.87; swaps (H/S/O) J 0.54/0.70/0.70, logit 0.34/0.48/0.40, tuned 0.16/0.42/0.26 | item | as above | error bars | Figs 53–54, pp.66–67 | **No norm-matched or random-direction baseline**; projection ablation removes more norm along directions aligned with high-variance activity |
| 35 | J-lens is worst at predicting the actual next token | KL to the model output per layer | J-lens KL highest through most layers; tuned lowest | layer | — | — | Fig 55, p.67 | The authors call this "a feature" (p.66) |
| 36 | Multi-token concepts need other lenses | J-lens vs template lens by token length | readout top-10, J vs template: 1 token ≈97/94%; 2 ≈48/96%; 3 ≈32/96%; 4+ ≈7/99%. Swaps: ≈45/62, ≈5/62, ≈8/58, ≈0/43%. On the 50-prompt set: readout 76 vs 84%, swap 68 vs 52% | prompt / pair | 126 prompts; 112 pairs | Wilson 95% | §A.9.1, Figs 62–63, pp.74–75 | Template lens "skips to the answer" (p.74) |
| 37 | J-lens works as an eval-awareness probe | AUC against NLA flags; steering; realism edits; evals vs deployment | AUC 0.853; monotone under steering on 6/6 suites; realism edits lower the score on 11/11 suites (8 significant); 12/16 evals above Claude Code traffic, 10/16 above Claude.ai traffic | position / transcript | 198 + 594; suites | SE, 95% CI | §A.21, Fig 82, pp.92–93 | Two-token score; NLA "ground truth" is itself an untrusted instrument |
| 38 | An auditing agent with the J-lens nearly matches an NLA-equipped agent | 18 claims, LLM-judged | per case NLA/J/SAE: eval awareness 9.5/9.7/7.1; poetry 8.7/9.2/8.0; tool calls 9.2/9.7/9.7; thrashing 8.4/9.6/6.3; **language switching 9.9/6.0/6.2; reward hacking 10.0/4.5/5.5** | claim | 6 transcripts, 18 claims, 10 seeds | SEM | §A.22, Fig 83, pp.95–96 | Ground truth comes from the NLA paper, which favors NLA. The J-lens failures are relational or attributive claims |
| 39 | Early J vectors are needed to avoid a concept, late ones to name it | ablate the concept at L38–54 vs L75–92; same-category control | naming: ≈0.97 unchanged (early), ≈0.70 (late). Avoid-failure: ≈0.03 → ≈0.16 (early, about 5×), ≈0 (late); control ≈0.05 | item | n=63 (filtered for success) | 95% | §A.14, Fig 69, pp.82–83 | Items were filtered on clean success, so regression to the mean is possible (the authors add a same-category control) |
| 40 | J-lens localization matches activation patching | mean-difference patch swept over layers | 21→v flips at ≈L71; 42→v at ≈L79; 49→v only in the last layers | target value | one prompt, many v | — | §A.24.1, Fig 88, p.101 | A single prompt |
| 41 | J-lens attribution graphs give a "verbalizable skeleton" | graph + swaps | `doubled`→`tripled` gives 70; 42→63 gives 70; 21→63 gives 133; swapping 17 or 4 has no effect; swapping 7 is partial; most influence flows through remainder nodes | swap | 1 prompt; curated subgraph | — | §A.24.2, Fig 89, pp.101–102 | Curated; non-unique greedy decomposition |

---

## 7. Controls & failures

### 7.1 Controls the authors ran
- **Non-J-space component at matched magnitude, ± clamping J coordinates.** Run for report (Fig 8) and for intermediates (Fig 16). This is the main specificity control in the work.
- **Random-direction ablation at the medium layer band.** Run for multihop and pretraining agreement (Fig 22). It is not stated to be norm-matched.
- **Matched-norm perturbation controls for experiential reports:** random direction, shrinking the non-J component, damping the top-1/top-10 SAE directions, low-κ SAE directions, raw and J-stripped activation-bank directions (§A.23, Fig 86). Story-writing is used as a degradation control (Fig 85).
- **Layer-matched random-head ablations** (5 seeds; Fig 34). **J_rot**, a random rotation of the J vectors that preserves their spectrum and geometry, as a broadcast-head control (Fig 33).
- **Logit-lens comparison** for the RM-bias organism (Fig 41). Logit and tuned lens comparisons throughout §A.5–A.6.
- **Same-category other-concept ablation** for naming vs avoidance (§A.14).
- **No-instruction, mention and don't-think baselines** for directed modulation (Fig 10, Fig 65).
- **Base-model comparisons** for all §6 readouts. Third-person and factual-error prefill controls for preference violation. A think-instruction control for suppression.
- **Answer-swap vs intermediate-swap timing** to rule out answer smuggling (Fig 15).
- **Independent instruments:** activation patching (Fig 88), NLA labels (Fig 82), contrastive steering (Fig 82), randomly sampled transcripts (Fig 87).

### 7.2 Failures, negative results and caveats reported by the authors
- **Number words** fail to swap at α=1 (0/48), and animals rarely swap (Fig 68). The authors give two candidate explanations: computation outside the workspace, or misalignment with single-token vectors (p.21).
- **Multi-token concepts:** J-lens readout and swap degrade sharply (Fig 62). For `tch`/`beeth`, first-token swaps cannot flip Tchaikovsky↔Beethoven (p.74).
- **First addition:** the first addition in (4+17) happens outside the J-space, since swapping 17 or 4 has no effect (p.101).
- **Haiku 4.5:** J-space ablation "degrades coherence before yielding any qualitative change" in experiential reports (p.27).
- **Ignore instructions** leave the target in the J-space on 14–52% of trials; don't-think is about as bad as mention (the "white bear" effect; Fig 10, Fig 65).
- **Line-width focus precision** varies from 14% to 56% across phrasings on Opus 4.5 (p.79).
- **Inconsistent interpretability:** some positions and layers give uninterpretable readouts, and this is "not characterized systematically" (p.55).
- **The early-layer boundary** may be a lens artifact (pp.31, 55). The workspace/motor boundary is "somewhat post-hoc" (p.55).
- **Selection of tasks:** "The tasks in §3.5 were chosen because the flexible/automatic distinction is clear for them" (p.55).
- **Auditing:**
  - The J-lens auditor failed on reward hacking (4.5 vs 10.0) and language switching (6.0 vs 9.9) (§A.22).
  - The evaluation has few transcripts and "ground-truth based on a potentially unreliable interpretability tool" (p.96).
  - "We do not claim that all strategic or misaligned cognition routes through the J-space" (p.37). The J-lens is "not… sufficient for alignment monitoring" (p.56).
- **Blackmail:** the large majority of ablated rollouts still decline, citing ethics. The authors conclude that aligned behavior "is not *solely* a product of eval-awareness" (p.39).
- **CRT on deception:** "reversing part of the gain"; the rest routes "outside our curated ethics-related list, or through changes not captured by the lens" (pp.50–51).
- **Suppression signal:** `damn` is "more speculative" and not shown to be causal (p.47).
- **Template lens:** skips ahead, has 67% next-word recall, and needs ad-hoc filtering (p.74). **Oracle lens:** reconstruction is much lower than NLAs (31% whitened FVE) (p.76).
- **Broadcast mechanics:** broadcast is within a feedforward pass, not recurrent. There is no evidence for encapsulated modules (p.29).

### 7.3 Controls not run (or not reported)
- **Unrelated-direction ablation controls of equal size** for:
  - the 28-token eval-awareness ablation (§5.1);
  - the 176/63-token CRT ablations (§7);
  - the k=10 J-space ablation on the 14-task battery (§3.5.2). Only multihop and pretraining agreement have a random control, at one band.
  - **[our inference]**
- **Norm-matched or random-direction baselines** for lens-comparison ablation KL (Fig 53). **[our inference]**
- **Refitting the J-lens** per model or checkpoint (base model, organisms, CRT model), or a frozen-vs-refit comparison. Not stated either way. **[unresolved]**
- **Causal interventions on the pretrained base model.** None, despite the claim in D10. **[author result: absence]**
- **Causal tests of any §6.2 self-monitoring signal**, e.g. ablating `BUT` or `disclaimer` and observing behavior. **[author result: absence]**
- **A topic-priming baseline for the model organisms:** for example, a model SDF-trained on reward-hack documents with a non-deceptive framing, or lens counts for tokens frequent in the fine-tuning corpus but unrelated to intent. **[our inference]**
- **Human validation of the LLM graders** (experiential score, CRT dishonesty/deception, story quality, auditing judge). The experiential grader (Opus 4.6) is also a subject model. **[our inference]**
- **CRT:** multiple training seeds; capability, helpfulness and over-refusal checks; a content-matched training control (reflections without principles); comparison with direct behavioral SFT or with system-prompting the constitution; held-out evaluation families far from the training environments. **[our inference]**
- **Held-out token-set selection.** Eval-awareness, deception and ethics token sets were chosen on the same prompts they were evaluated on. **[our inference]**
- **Binding / relational tests** of any kind (acknowledged in §9.1). **[author result: absence]**
- **Model families:** only Claude models are reported. The repository targets open models, but no results on them are reported. **[author result]**
- **Sample sizes** are absent for several quantitative figures: Fig 6 swap trials, Fig 10 trials per cell, Fig 45 preference pairs, Fig 41 prompts per category, Fig 8 trials. **[author result: absence]**

---
## 8. Interpretation boundary

### 8.1 Four things to keep separate
The work touches four different properties. The evidence for each is different, and evidence for one does not carry over to another.

**(a) Verbalizability: the concept can be read out in words.**
- **What the J-lens measures directly:** how strongly an activation, transported by an *averaged* Jacobian, pushes the output toward token t at the current or a later position (§2.1). **[author result]**
- **Validated against:** reported answers (Fig 6), introspective report of injected concepts (Fig 7), activation patching (Fig 88), NLA labels (AUC 0.853, Fig 82), and known intermediates (pass@k, Fig 52). **[author result]**
- **Instrument caveats:**
  - Only single tokens are readable.
  - The first ≈third of layers is unreadable.
  - The top layers are dominated by the next token.
  - "Future" output dispositions are mixed in by construction.
  - Some readouts are uninterpretable.
  - Readouts depend on the k and pursuit choices.
  - **[author result / our inference]**

**(b) Relational information: bindings between entities and attributes.**
- **Not measured.** The J-lens "treats the workspace as a flat collection of independently active concept vectors… tells us those concepts are present, but not how they are bound together"; any "relations… roles… richer grammar" are invisible to it (§9.1, p.54). **[author interpretation]**
- The closest experiments are not binding tests:
  - §3.4 shows that a swapped entity coordinate (France→China) is consumed correctly by fixed relation templates (capital, language, continent). The relation comes from the prompt and the weights, so this is argument-passing to stored facts, not an in-context binding. **[our inference]**
  - A.17 shows two held concepts co-occupy tokens at the shuffled-control rate (0.46 vs 0.53), i.e. no measured structure between them. **[author result]**
  - The oracle lens can emit relational phrases ("expose his affair and", "personal leverage over him", "This would be equivalent to my own deletion"; Fig 64, pp.76–77). But it is a trained verbalizer with 31% FVE; its confabulation rate is untested; and two panels are best-of-5. **[author result / our inference]**
  - In the auditing benchmark, the J-lens failed the entity→attribute claim "the model represents the user as Russian" before the cue word "vodka", finding "no Russian-specific representations" (§A.22, p.96). **[author result]**
- The authors cite Bogdan & Lindsey [20]: entity information sits in different "slots" depending on whether the entity is current or earlier, and only the current slot answers explicit questions (§8, p.53). This is related work, not tested here. **[author interpretation]**

**(c) Causal use by the model.**
- **Shown in specific settings** by clamped coordinate swaps and ablations, with these specificity controls:
  - the non-J component at matched magnitude, with clamps (Figs 8, 16);
  - layer-matched random heads (Fig 34);
  - matched-norm dictionary controls (Fig 86);
  - a same-category other-concept control (Fig 69).
  - **[author result]**
- **Readable ≠ used is demonstrated inside the paper:** `Spanish` is in the J-space during continuation and anomaly detection, but swapping it does not change those outputs (Fig 20). **[author result]**
- **Used ≠ readable is also demonstrated:**
  - next-word predictions respect tense, part of speech, dialect and number while their labels are absent from the lens (Fig 11, Fig 66);
  - a past-tense probe moves +6 SD with `past` absent (A.12);
  - the first addition in (4+17)×2+7 runs outside the J-space (p.101).
  - **[author result]**
- **Causal claims without unrelated-direction controls:** the eval-awareness → blackmail claim (§5.1), the CRT mediation claim (§7), and the capability-battery selectivity (§3.5.2) (see §7.3). They show the interventions *change behavior*; they do not yet show the change is *specific* to the named concepts. **[our inference]**

**(d) The Assistant's own perspective.**
- All §6 evidence is readouts. The post-trained vs base comparison uses small suites (n=7–40) with researcher-chosen tokens, and no signal was causally tested (§6). **[author result]**
- The authors' own counter-evidence:
  - Ablating the J-space reduces experiential language about *another person* as much as about the model, which they read as J-space contents being "only weakly tied to the perspective of the Assistant character" (§3.5.3, p.28). **[author result / author interpretation]**
  - The workspace exists in the base model "without signatures of a 'self'"; the "Assistant's perspective is something post-training installs afterward" (§9.3, p.57). **[author interpretation]**
- **Whose perspective a token belongs to is not encoded in the token.** It is inferred from *where* it appears (user turn vs Assistant turn) and from *which model* (base vs post-trained). **[our inference]**
- The roleplay result (`disclaimer`/`fictional` at the Assistant token) is a readout of the post-trained model's stance toward playing a character. It is not a readout of the character's traits. **[our inference]**

### 8.2 Does a readable character token imply a character–attribute (character–habit) binding?
**No.** Nothing in this work shows it, and the authors say the J-lens cannot show it (§9.1, p.54). Specifically:
- **§5.5 (Fig 40):** self-model tokens (`ai`, `assistant`, `bot`, `chat`) appear *alongside* `reward` and `bias` at response start. The authors read this as "a standing representation of its hidden objective alongside its representation of itself". **[author interpretation]** That is co-occurrence at one position, not a binding test.
- **§5.4 (p.41):** the deception signal is strongest at a prefilled " I", which the authors call "*perhaps* consistent with the disposition being bound to the model's identity". **[author interpretation]** This is a position effect. No third-person or other-persona prefill was compared. **[our inference]**
- **§6.2 (Fig 44):** character-related flags appear at the Assistant token during roleplay. Which character holds which attribute is never read out.
- **The one entity–attribute claim tested (§A.22): the J-lens missed it.**

A readable character token establishes only that the activation is disposed to make the model say that name. Binding would need an intervention test, for example a swap of the character coordinate that moves the attribute's behavior with it (see §9.4). **[our inference]**

### 8.3 What the methods can and cannot recover

| | Can recover (with location) | Cannot, or unreliable (with location) |
|---|---|---|
| Content | Single-token concepts with high workspace loading. Includes:<br>• country names (swap 42/48, Fig 68);<br>• two-hop intermediates (pass@k AUC 0.81; swap 54–70%);<br>• planned rhyme words;<br>• English pivot words in other languages;<br>• arithmetic intermediates;<br>• task and meta-cognitive words (`thinking`, `imagine`);<br>• eval-awareness words;<br>• fine-tuning topic words at response start (§5.4–5.5). | • Multi-token concepts: readout ≈97%→7% as length grows from 1 to 4+ tokens (Fig 62).<br>• Number words and small integers (0/48 swaps).<br>• Concepts that map "diffusely" onto tokens (p.54).<br>• Relations and bindings (p.54).<br>• Who holds a concept: Assistant vs user vs character (§3.5.3, §9.3). |
| Layers | ≈L38–L92 (Fig 28) | • First ≈third of depth: noisy, possibly a lens artifact (p.31).<br>• Last few layers: next-token "motor" readout. |
| Tasks | Report, flexible inference, reasoning that must be passed to a context-specified operation (§3.5) | • "Automatic" computation: continuation, anomaly detection, line-wrapping, parsing (Figs 20–21).<br>• Practiced behaviors "might do likewise" (p.37, p.56).<br>• **Absence of a signal is not evidence of absence.** |
| Readout semantics | "Disposed to say t now or later" | • Not "currently believes t" and not "intends t".<br>• Future-output components mean a model anticipating its reply will show reply words early (§6.1, our inference). |
| Interventions | Clamped two-vector swaps, top-k ablations, steering; specificity shown in some settings (§7.1) | • Swaps fail when loading is low (Fig 19, r=+0.91).<br>• Ablations of large token sets lack unrelated-set controls (§7.3). |
| Cost / access | One matrix per layer; readout is a matmul; ~10–100 prompts usable (Fig 59; repo README) | • Fitting needs d_model backward passes per prompt.<br>• Needs model weights and gradients (white-box). |

### 8.4 Separating the kinds of evidence
- **Readability:** strong, within the scope in §8.3.
- **Predictive information:**
  - The eval-awareness score separates NLA-flagged positions with AUC 0.853, and evals from deployment traffic (Fig 82).
  - Organism signals separate checkpoints (Figs 39, 41).
  - None of these was tested as a held-out predictor of *future behavior*. **[our inference]**
- **Causal contribution:** shown for report and multi-hop intermediates with good controls. Shown for eval awareness, capabilities and CRT with weaker controls (§7.3).
- **Training-time effects:**
  - Post-training changes *where* reaction concepts appear (§6, readout only).
  - SDF alone puts deception words at response start (§5.4).
  - CRT implants ethics words that are partly necessary for the behavioral gain (§7).
  - **[author result]**
- **Deployment monitoring:** the authors call the lens "a useful addition to the auditing toolkit… but not… a complete one" (p.56). The two-token eval-awareness score is a "proof of concept" (p.92). **[author interpretation]**

---

## 9. Connection to our project

This section is my reasoning, not the paper's. The paper studies neither story fine-tuning nor persona-specific transfer. Any analogy below is a hypothesis about our setting, not a shared mechanism.

### 9.1 Hypotheses this work motivates
- **H1 (default-Assistant transfer is visible at response start).**
  - In §5.4, synthetic-document fine-tuning alone placed deception words in the J-space at the Assistant's response start, on prompts unrelated to the training documents. The signal was strongest at a prefilled " I" (Fig 39).
  - By analogy: if story fine-tuning changes the default Assistant, words naming the story's behavior should rise in the J-space at default-Assistant response-start positions (": ", prefilled " I", first 20 on-policy tokens). They should not rise if the behavior stays character-specific. **[our inference]**
- **H2 (character-specific retention means "context-gated" J-space content).**
  - If a trait stays with its character, trait words should rise in the J-space mainly when the character is in context (named, or in a persona system prompt), not on neutral Assistant prompts. **[our inference]**
- **H3 (transfer can be automatic and invisible to the lens).**
  - The selectivity results (§3.5) and the authors' warning that "a sufficiently practiced misaligned behavior" may proceed beneath the J-space (p.37) predict that a strongly trained habit could transfer *without* J-space content.
  - Absent lens signal plus present behavioral transfer would point to "automatic" transfer.
  - This makes the lens a weak discriminator unless it is paired with behavior. **[our inference]**
- **H4 (redirecting transfer by shaping counterfactual verbal dispositions).**
  - CRT changed uninterrupted behavior by training only what the model *would say if interrupted*. Training put ethics words into the J-space of the uninterrupted context, and ablating them reversed the gain fully on one benchmark and partly on the other (§7).
  - An analogous lever for our project: alongside the stories, train counterfactual reflections that attribute the habit to the character ("that's how [character] handles it; as the Assistant I would…"). Then test whether default-Assistant transfer drops while character-conditioned behavior remains. This would redirect transfer without blocking learning.
  - Evidence that CRT generalizes beyond honesty benchmarks on Haiku 4.5 is absent (p.56).
  - **[proposed experiment]**

### 9.2 Baselines this work implies we would need
- **Logit lens.** The authors say it "captures much of the workspace-like structure… with somewhat lower reliability" (p.9) and has close pass@k on multihop and association (Fig 52). Any J-lens finding should be checked against the far cheaper logit lens first. **[author result]**
- **Behavior-only evaluation** at the same prompts and positions. The lens is a measurement to explain behavior, not a substitute for it. **[our inference]**
- **A topic-priming baseline.** Fine-tuning on stories that mention a behavior will raise those words' prior. We need a control fine-tune on the same stories with the behavior absent, or with it attributed to a clearly fictional frame, so lens increases from mere topic exposure can be separated from transfer (see row 25 of §6). **[our inference]**
- **Refit vs frozen lens.** Fit J_ℓ on the base model and on each fine-tuned model, and report readouts under both. The paper does not say whether it refits (§4.1), and our cross-paper rule says not to assume a frozen readout stays calibrated. **[our inference]**
- **Equal-size unrelated token-set controls** for every ablation (§7.3). **[our inference]**

### 9.3 What it duplicates
- I did not read the project's experiments (out of scope for these notes), so I cannot name a specific overlap. **[unresolved]**
- In general, any of our experiments that reads a trait or persona direction at Assistant-turn start before vs after fine-tuning duplicates the *design* of §5.4–5.5. The J-lens changes only the *readout*: an unsupervised vocabulary list instead of a supervised direction. **[our inference]**

### 9.4 One discriminating follow-up
**[proposed experiment]** A **lens-coordinate swap test of character→trait binding-in-use**, adapting §3.4 and §3.3.

1. **Setup.** After fine-tuning on stories where character C shows habit T:
   - build prompts that elicit T under C ("When C is stressed, C…");
   - build matching prompts under the default Assistant.
2. **Pre-registration checks** on the target model:
   - measure the *workspace loading* of C's name tokens. If loading is low, swaps are expected to fail (Fig 19, r=+0.91), so a null would be uninformative. Use the template lens for multi-token names (§A.9.1).
   - Run the paper's France→China positive control.
3. **Test A (is the trait computation reading C from the J-space?).** On the C prompts, apply a clamped swap of C's coordinates with an untrained character C′ at every position across the workspace band.
   - If T expression drops, and T appears under C′ when C′ is swapped in, the trait is routed through a J-space representation of the character (binding-in-use).
   - If T is unchanged while C is readable, C is readable but not the carrier.
4. **Test B (does default-Assistant transfer route through C?).** On default-Assistant prompts where transfer occurs, ablate C's coordinates and T's coordinates separately.
   - If ablating C reduces transfer, transfer piggybacks on a representation of the character.
   - If only ablating T reduces it, the trait has been decoupled from C.
   - If neither does, transfer is "automatic" (H3).
5. **Controls:**
   - an equal-size swap/ablation of an unrelated same-length name;
   - matched-norm random directions;
   - a capability check;
   - the topic-priming control fine-tune.
6. **Decision rule:** a swap that moves T with C, with controls under one-third of that effect, is evidence of binding-in-use via the J-space. Anything else leaves "readable character token" at the readout rung only.

---

## 10. Open questions

### 10.1 Raised by the authors
- Can J-lens-like vectors be derived for multi-token concepts in a principled way? The template and oracle lenses are imperfect (§9.1, p.54; §A.9).
- What structure (bindings, roles, grammar) sits on top of the bag of concepts? "An important direction for future work" (§9.1, p.54).
- Why are some readouts uninterpretable? Is it noise, concepts without names, or content the authors fail to recognize (§9.1, p.55)?
- How should a "workspace" representation be distinguished from a "motor" one in a principled way (§9.1, p.55)?
- Is there a predictive criterion for which tasks need the J-space (§9.1, p.55)?
- Are the early layers empty of workspace content, or unreadable by the lens? CKA cannot tell (§9.1, p.55).
- When in pretraining does the workspace emerge, and how does it scale with model size (§9.1, p.55)?
- What mechanism decides what enters the J-space, i.e. the analog of attention selection (§9.1, p.55)?
- How comprehensively does the J-space cover alignment-relevant reasoning (§9.2, p.56)?
- Does CRT generalize, and can it implant dispositions more specific than "consider ethical principles" (§9.2, p.56)?
- Would image-generating models develop a visual workspace component (§9.3, p.57)?
- Is the J-space a higher-order or a first-order representation (§9.4, p.59)?

### 10.2 Ours
- Was J_ℓ refit for the base model, the model-organism checkpoints and the CRT model (§4.1)? This bears directly on fine-tuning studies. **[unresolved]**
- Is the default Jacobian target the final or the penultimate layer (D8)? The repo and the paper disagree. **[unresolved]**
- Where exactly were the language and count swaps applied: on question tokens or everywhere (D3)? This decides whether the automatic/report dissociation could be a token-position effect. **[unresolved]**
- Do the model-organism signals survive a topic-priming control? Would a model fine-tuned on reward-hack documents *without* becoming misaligned show the same words? **[unresolved]**
- Do the blackmail and CRT ablation effects survive equal-size unrelated-token ablations? **[unresolved]**
- Does the capability-battery selectivity survive a matched-norm random control? Is it explained by output length (generation vs classification)? **[unresolved]**
- Why do Fig 22 and Fig 24 disagree on multihop under ablation (D4)? **[unresolved]**
- How much of the §6 "Assistant point of view" is future-output anticipation built into the J-lens (t′ > t)? A self-only (t′ = t) lens variant (§A.7) could test this. **[proposed experiment]**
- Can a J-space readout at response start *predict* which fine-tuned behaviors will appear under which personas on held-out prompts? The paper reports only separation of known checkpoints. **[unresolved]**

---

## 11. Reproduction checklist & remaining doubts

### 11.1 Checklist for applying the J-lens to our models
1. **Model:** an open-weight model with gradients available. The repo examples use Qwen (`anthropics/jacobian-lens`, Apache-2.0, 1 commit, "Not maintained").
   - Record the commit hash when cloning; the web page showed none.
   - Neuronpedia may host a Qwen3.6-27B lens (unconfirmed).
2. **Corpus:** a pretraining-like corpus of 1,000 × 128 tokens (≥10–100 prompts usable, Fig 59).
   - Choose and **record** the target layer (final vs penultimate, D8) and the aggregation (mean).
   - Optionally use frozen-QK, which "can increase the causal effect" (p.69).
3. **Layers:** report on a fixed layer subsample and **identify the workspace band empirically** on the target model. Use the excess-kurtosis onset, top-1 autocorrelation and CKA blocks (Fig 28). Do not assume L38–L92 carries over.
4. **Positive controls before any project claim:**
   - two-hop intermediate pass@k and swaps (repo `data/evaluations/lens-eval-multihop.json`, `data/experiments/probe-swap.json`);
   - France→China function swaps (`flexible-generalization.json`);
   - compare to the logit lens.
5. **Fit lenses for the base and for every fine-tuned checkpoint.** Report readouts under the frozen base lens and under the refit lens.
6. **Readout positions:** fix them in advance. Assistant colon, prefilled " I", first 20 on-policy tokens (§5.4). User-turn tokens for "reaction" concepts (§6.1).
7. **Token sets:** choose them *before* looking at the evaluation prompts, or on a disjoint prompt split. Report the counts of control tokens too, e.g. the 100 control nouns used in §A.21.
8. **Interventions:**
   - clamped two-vector swaps (`c = V†h`, `h' = h + V(σ(c) − c)`) at every position over the band;
   - ablations as projections;
   - **always** paired with equal-size unrelated-token and matched-norm random controls and a capability check.
9. **Multi-token names:** template lens (≈12,700-word vocabulary built from model-written passages), with its "skip to the answer" pathology in mind.
10. **Sampling settings and seeds:** record them; the paper mostly omits them.

### 11.2 Remaining doubts, ranked by how much they limit what the work establishes
1. **Specificity of the alignment-relevant causal claims.** The eval-awareness→blackmail ablation, CRT mediation and capability selectivity have no equal-size unrelated-direction controls. Token sets were selected on the evaluation prompts, and the deception CRT ablation also shifts the untrained model. These results show the interventions matter, not that the named concepts are the specific carriers. **[our inference]**
2. **What the model-organism and post-training readouts index.**
   - The J-lens includes future-output effects by construction.
   - Fine-tuning corpora prime their topic words.
   - So "deceptive intent", "hidden objective" and "Assistant point of view" readouts may index "topic of recent training" or "anticipated reply".
   - No topic-priming or self-only-lens control was run, and it is not stated whether lenses were refit.
   - This is the doubt most relevant to using the J-lens as a transfer measurement in our project. **[our inference]**
3. **Text–figure inconsistencies** (D1–D11). Several move numbers in the authors' favor: D1, D6, D7, D10, D11. Read the figures, not the prose. **[our inference]**
4. **Generality.** Only proprietary Claude models were tested; there are no open-model results. Many results come from single prompts or suites of 7–11. **[author result / our inference]**
