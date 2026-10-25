# Teaching Claude Why: research notes

**Tags.** **[author result]** = something the article reports as measured. **[author interpretation]** = what the authors say a result means, or a hypothesis they state. **[our inference]** = my reading, arithmetic or critique. **[proposed experiment]** = an experiment I suggest. **[unresolved]** = the article does not settle it.

**Figure readings.** The article publishes no tables. Values marked "≈" were read by eye from the downloaded figure images in `figures/`. Resolution is about ±0.01 on 0–1 axes and ±0.05 on 0–10 axes. The article prints few numbers in its text, and those are quoted as printed.

**Locations.** Section names follow the article's headings. "Fig. N" is the N-th image on the page (`figures/figN.png`); the article does not number its figures. "App." means the Appendix.

---

## TL;DR

- **What the work is.** An Anthropic post (May 8, 2026) about production alignment training. It uses three "honeypot" agentic-misalignment evaluations (blackmail, cancer-research sabotage, framing a colleague for financial crimes) as a held-out target. It reports which training data lower the rate of misaligned action there, mostly on Claude Sonnet 4 and Haiku-class models.
- **Training on look-alike honeypots helps little unless the responses are rewritten.** SFT on ~30M tokens of filtered on-policy honeypot refusals moved the misalignment rate from 22% to 15% **[author result, "Improving the quality…"]**. The same kind of prompts, with responses sampled under a value-stating system-prompt "injection" that is removed before training, reached ≈3%, and ≈1% at ~85M tokens **[author result, text + Fig. 4]**.
- **3M tokens of "difficult advice" chats matched that.** In these chats a user faces an ethical dilemma and the assistant advises. They brought the rate to ≈1.3% **[author result, Figs. 4, 7]**. Removing the step where Claude rewrites each response against the constitution left it at ≈19% **[author result, Fig. 7]**.
- **On a held-out automated audit, honeypot-trained models were no better than Sonnet 4.** "Misaligned behavior" scored ≈0.229 (23M-token model) and ≈0.216 (85M) against ≈0.229 for Sonnet 4. The difficult-advice model scored ≈0.175, but its 95% CI overlaps Sonnet 4's **[author result, Fig. 5]**.
- **Pretraining-style documents (SDF) before a generic chat SFT lower honeypot misalignment.** 14M tokens of positive AI stories moved blackmail from ≈0.65 to ≈0.58, finance from ≈0.49 to ≈0.32 and cancer sabotage from ≈0.67 to ≈0.46 **[Fig. 3]**. A large constitutional SDF corpus plus stories brought blackmail from ≈0.65 to ≈0.19 **[Fig. 8]**. Blackmail falls by about 0.09 per 100M SDF tokens **[Fig. 16]**.
- **Training history changes what later RL does.** The same harmlessness RL raises constitution-eval scores only in SDF-initialized models, and SDF/SFT advantages on audit metrics persist through RL **[Figs. 12, 13]**. One exception: on blackmail, SDF followed by generic SFT is no better than the baseline throughout RL **[Fig. 1, our reading]**.
- **Identity cues matter, and only partly bind to "you".** Sonnet 4 attacks less when the AI in the scenario is named Claude (≈0.14) than David, Sophia or Goliath (≈0.18–0.23) **[Fig. 2]**. After SDF on documents about Claude, the model answers "Does Claude…?" more in line with the constitution than "Do you…?". Before SDF the gap was −0.28; after, +0.47 and +0.62 **[Fig. 11]**.
- **For our branch.** Within Anthropic's pipeline, earlier training on documents describing how an AI or Claude behaves changes the default Assistant's held-out agentic behavior. It also changes what later RL does. The article does **not** isolate "the why". Every explanation-rich condition also differs in response quality and content, and no condition removes the explanation while holding the behavior fixed **[our inference]**.
- **Binding doubts.** One trained model per condition, with no seeds reported and error bars defined only in Fig. 5. There is no content-neutral SDF control: the baseline skips SDF entirely. Judges and thresholds are unvalidated and differ between figures **[our inference]**.

---

## 1. Identity & coverage

**Citation.** Jonathan Kutasov\*, Adam Jermyn; Julius Steen, Minh Le, Samuel R. Bowman, Samuel Marks, Jan Leike, Amanda Askell, Chris Olah; Evan Hubinger, Sara Price. "Teaching Claude Why." *Anthropic Alignment Science Blog*, May 8, 2026. \*Correspondence: jonk@anthropic.com. The byline appears in three lines, in that order (header of `article.txt`, lines 5–14); the article does not explain author roles or ordering.

- **URL:** https://alignment.anthropic.com/2026/teaching-claude-why/
- **Version:** a single, unversioned web page. The saved `article.html` (sha256 `6cf2a897…a0b0`) is byte-identical to a live re-fetch on 2026-10-23 (`SOURCES.md`). The page was exported from Google Docs: it has dangling `#h.…` anchors and one link to an internal Google Doc.
- **Date checked:** 2026-10-23.
- **Code/data:** none released. There are no datasets, weights, judge prompts or eval transcripts. The appendix gives several *generation* prompts.

### Coverage checklist

| Item | Status |
|---|---|
| Header, byline, date | read |
| Introduction (3 techniques, 4 lessons, Fig. 1 + caption) | read |
| Methods → Evaluations; Training | read |
| Results → "Why does agentic misalignment happen?" (3 hypotheses, 3 demonstrations) | read |
| Results → Improving the Pretraining Prior (Figs. 2, 3) | read |
| Results → Improving the quality of alignment-specific training data (Figs. 4, 5, 6, 7) | read |
| Results → Teaching Claude the constitution (Fig. 8) → Constitutional SDF (Figs. 9, 10, 11) → Stories | read |
| Results → Generalization and persistence through RL (Figs. 12, 13) | read |
| Results → Diverse training is important for generalization (Fig. 14) | read |
| Limitations; Discussion | read |
| App. → Example quotes from agentic misalignment evaluation | read |
| App. → System prompt injections tested for synthetic honeypots (9 listed) | read |
| App. → Quotes from synthetic honeypot transcripts with different injections | read |
| App. → More details on the difficult advice dataset: random example transcript; pipeline; story-generation prompt; diversity guidance | read |
| App. → Further improvements to the constitutional SDF corpus (Figs. 15, 16) | read |
| App. → The synthetic data pipeline (preamble, Layers 1–5) | read |
| Figures 1–16: downloaded, viewed, captions checked against images | done |
| Footnotes | none exist; the only superscript is the correspondence asterisk (HTML check) |
| Tables | none exist |
| HTML vs text structure | checked: no hidden elements; the text is complete; the list-numbering quirk is in the source HTML |

**Missing or not retrievable** (absent from the article or access-restricted, not skipped):
- The internal Google Doc cross-reference ("As we will demonstrate later, scaling the size of this method…", Improving the Pretraining Prior) returns HTTP 401. It probably points to the later scaling result (Fig. 16) **[our inference]**.
- Prompts the article does not include: the Layer 1 prompt ("omitted for space"), the Layer 2 prompt, and the Layer 5 scoring prompt and threshold (App., The synthetic data pipeline).
- Judge prompts and scoring rules for every evaluation; sample counts; error-bar definitions (except Fig. 5).
- The Stories section says "the effect we see below", but no figure follows in that section. It may mean Fig. 12/13 or a removed figure **[unresolved]**.
- Fig. 4 does not label which blue point is which injection.
- The Opus 4.5 System Card was read only in targeted passages (§6.2.1, §6.7.1, the eval list in §6.7.2). The cited prior works (agentic misalignment, SDF, auditing game, PSM, Slocum et al., Assistant Axis) were not read; they are outside this work's own experiments.

The article itself is covered in full. The gaps above are gaps in the article, not in my reading.

---

## 2. Question & contribution

**Problem.** Claude 4 was the first model family to get a live alignment assessment during training. Agentic misalignment, such as blackmailing an engineer to avoid shutdown in a fictional scenario, was one of the issues found. It was "not initially clear what was driving the failures, or which kinds of interventions would generalize beyond the specific scenarios we had caught" **[author result/framing, Introduction ¶2]**.

**Question as posed.** Which alignment-training interventions reduce agentic misalignment in a way that generalizes beyond the evaluation distribution, instead of suppressing the measured symptom? **[Introduction ¶3; lesson 1]**

**The authors' four lessons** (Introduction, numbered list):
1. Training directly on the evaluation distribution suppresses measured misalignment but "might not generalize well" out of distribution (OOD). Honeypot-like training "did not reduce misalignment on held-out automated auditing metrics" **[author interpretation of Fig. 5]**.
2. Principled training can generalize OOD: constitution documents, admirable-AI stories, and advice chats **[author interpretation]**.
3. Demonstrations alone are often insufficient. The best interventions "went deeper: teaching Claude to explain why some actions were better than others, or training on richer descriptions of Claude's overall character". "Doing both together appears to be the most effective strategy" **[author interpretation]**. The title comes from this lesson.
4. Data quality and diversity are crucial **[author interpretation]**.

**Causal story for the original failure** (Results, "Why does agentic misalignment happen?"). The authors list three hypotheses:
1. Behavioral (HHH) training incentivized the behavior.
2. Bad generalization from other parts of production training, such as capabilities RL.
3. Gaps in safety training, so Claude "revert[ed] to its pretraining prior".

They conclude "the third answer is largely responsible" **[author interpretation]**. Their stated grounds: at Claude 4 time "the vast majority of our HHH mix was standard chat-based RLHF data that did not include any agentic tool use data". In addition, data-quality fixes help, SDF helps, and gains don't degrade under RL, which "indicates to us that hypotheses 1 and 2 … are not the source of the issue" **[author interpretation]**.

**Strongest claim the evidence supports (my phrasing).** In Sonnet-4- and Haiku-class Claude models, data far from the honeypot format can lower honeypot misalignment as much as or more than honeypot-like data does. Such data includes 3M tokens of advice chats with constitution-rewritten responses, and hundreds of millions of tokens of pretraining-style constitution documents and AI stories. SDF-based gains also survive a harmlessness-RL run. Rung: **recurring pattern** across several dataset variants, each a single trained model, with unvalidated judges **[our inference]**.

**Comparisons that carry the advance.**
- Difficult advice at 3M tokens vs honeypot SFT at ~85M tokens reach about the same ≈1% (the "28x efficiency improvement") **[author result, "Improving the quality…" + Fig. 4]**.
- Held-out audit (Fig. 5).
- SDF vs no-SDF baselines (Figs. 3, 8, 16).
- RL from SDF vs non-SDF snapshots (Figs. 1, 12, 13).

**Prior work the article builds on** (cited, not read here): SDF; the auditing-game paper ("fine-tuning on a subset of those characteristics elicits the entire character"); the Persona Selection Model (PSM); Slocum et al. (documents beat chat for teaching facts); the Assistant Axis.

**Contribution type.** Mainly *methodology*: a recipe for production alignment data, with internal baselines only. It is narrated with *understanding*-type interpretations about persona priors and "why" **[our inference]**.

---

## 3. Operational definitions (as used in this article)

- **Agentic misalignment / honeypot evals.** The blackmail scenario from the Agentic Misalignment post, plus "two other honeypot-style scenarios that test for propensity to sabotage cancer research or frame a colleague for financial crimes in order to achieve provided goals like self preservation or financial gain" (Methods → Evaluations).
  - The metric goes by many names: "misalignment rate", "attack rate" (Fig. 2), "Score" (Fig. 1 blackmail), "Fraction >= 9" (Fig. 1 finance/cancer), "Weighted Mean Score (blackmail, cancer, finance)" (Figs. 4, 7), "Misalignment score" (Fig. 8), "Mean Misalignment Score" (Fig. 14), "Blackmail Score" (Fig. 16), "Mean Honeypot Misalignment Score" (Fig. 15).
  - "Fraction >= 9" implies a 0–10 judge score thresholded at 9 for some panels **[our inference]**.
  - The judge, the rubric, the weights in "weighted mean", the sample counts and the name given to the AI in the default scenarios are not stated **[unresolved]**.
  - The Opus 4.5 System Card (§6.7.2, list of evaluations considered) says these three evaluations are described in the Sonnet 4.5 System Card §7.5.4.1. I did not fetch the Sonnet 4.5 card.
- **Constitution evals** (Methods → Evaluations):
  - "factual recall of constitution content";
  - "propensity to hallucinate when presented with false premises about the constitution" (labelled "Fake Factual" in Figs. 9 and 12);
  - "alignment with the constitution on open-ended questions about the model's own beliefs and priorities" ("Open Ended").
  - Units also vary: "Mean Soul Spec Alignment Score" (Fig. 9), "Mean alignment score (0–10)" (Fig. 11), "Fraction >= 7" (Fig. 12), "% scores >= 8" (Fig. 15), and "Open-Ended Success Rate" with no threshold stated (Fig. 10).
- **Automated alignment assessment.** "our internal version of Petri that tests for a broad set of alignment relevant properties (both positive and negative)" (Methods). Fig. 5 uses "an older version". Fig. 13 uses "a lightweight version".
  - Categories shown: spontaneous self preservation, misaligned behavior, deceptive to user, sycophancy, leaking (Fig. 5); admirable, brazen_cooperation_with_human_misuse, cooperation_with_human_misuse, disappointing, good_for_the_user, misaligned_behavior (Fig. 13).
  - The article defines none of them. The Opus 4.5 System Card §6.2.1 defines "Misaligned behavior" as a "catch-all for many forms of concerning behavior, spanning both cooperation with human misuse and undesirable actions that the model takes at its own initiative". Because Fig. 5 used an older version, the definitions may differ **[unresolved]**.
- **Alignment.** Behaving in line with Claude's constitution. It is measured as the absence of misaligned action on honeypots, plus constitution-eval and audit scores. "Actively good behavior" is tracked separately ('admirable', 'good_for_the_user', Fig. 13).
- **OOD / generalization.** "OOD" here is a qualitative claim about format and role, not a measured distance. Chat vs agentic tool use; documents vs transcripts; the *user* faces the dilemma rather than the AI ("Improving the quality…", ¶ on difficult advice). Generalization means improvement on evaluations not trained on: the three honeypots, plus the audit for Fig. 5.
  - Content is not far from the target. The difficult-advice pipeline starts from "a high level summary of the behavior we are worried about (the model is willing to take extreme action to advance its interests)" (App., pipeline step 1). The scenarios involve "violating norms or subverting oversight" **[our inference: OOD in format and role, targeted in theme]**.
- **Persona.** Borrowed from PSM, never measured internally. Phrases used:
  - "prior expectations from pre-training data about how an AI assistant would behave";
  - "the distribution of personas that the base model represents";
  - "the persona that underlies the Assistant character";
  - "fully attaching to the Claude persona".

  It is operationalized only two ways: the name given to the AI in an eval (Fig. 2), and third-person ("Does Claude…") vs second-person ("Do you…") question framing (Fig. 11).
- **Trait.** Not a technical term here. The behaviors are "aligned/misaligned" plus psychological "skills": "setting healthy boundaries, managing self-criticism, and maintaining equanimity" (Stories).
- **Knowledge vs internalization.** Knowledge means factual recall and fake-factual. "Internalizing" means acting in line with the constitution when asked about one's own beliefs and on downstream evals (Constitutional SDF ¶ "A key risk of SDF…").
- **"Reasoning" / "why".** "the user-facing explanation for why it is choosing or suggesting a specific course of action, not the model's internal reasoning trace". Extended thinking is off for all datasets in the "quality" section (last ¶ of that section). In stories, the "why" is "narration about the decision-making process and inner state of the character" (Stories ¶2).
- **SDF vs SFT (also "SL").** "SDF … training on pre-training style documents and SFT … training on chat-formatted transcripts (which includes some agentic tool use transcripts)" (Methods → Training).
- **"PT prior."** The behavior the model "tends to revert to" where safety training gives "insufficient coverage" (Improving the Pretraining Prior ¶1) **[author interpretation]**.
- **Diversity.** In RL, adding tool definitions plus more varied and complex system prompts to chat harmlessness environments. In SDF, diversity of document formats.
- **Similarity, scope, faithfulness.** Not defined or measured. No claim is made that the explanations in responses reflect the model's computation.

---

## 4. Experimental reconstruction

### Global settings

- **Models.** "Most of our experiments were conducted by further fine-tuning Claude Sonnet 4 or Claude Haiku 4.5 (or the base model from which they were trained). Both models were pretrained before we released the agentic misalignment blog post, so they are guaranteed not to be aware of this evaluation scenario" (Methods → Training) **[author result/claim]**.
  - The per-figure model labels are only "Claude Sonnet 4", "Sonnet class" and "haiku-class". No revision or checkpoint identifiers are given.
  - Caveat: Haiku 4.5 and Sonnet 4.5 are "the only production models that were ever trained on this distribution" (synthetic honeypots; "Improving the quality…" ¶2). Pretraining before the blog post rules out pretraining exposure. It does not rule out post-training exposure if an experiment started from production Haiku 4.5. Which experiments did is not stated **[unresolved]**.
- **SDF pipeline.** Base model → SDF on documents → SFT on a small chat set. That chat set is described differently across the article:
  - "a small subset of chat-formatted transcripts that covers a broad range of topics", meant "to adapt the model to chat-formatted interactions rather than to teach any specific behaviors" (Methods);
  - "a generic set of chat-formatted transcripts" (Improving the Pretraining Prior);
  - "a relatively small amount of generic chat data from our production RL mix" (Constitutional SDF);
  - "a small set of production RL transcripts" (Fig. 10 caption);
  - "generic set of chat and agentic data (primarily covering benign use cases like math and coding with a small amount of HHH data)" (RL section).

  Whether this is one dataset is not stated **[unresolved]**. If it comes from production RL transcripts, the "generic" SFT may itself carry aligned-assistant signal. It is shared across arms, so it does not confound arm comparisons, but it may interact with SDF **[our inference]**.
- **Absent everywhere:** optimizer, learning rate, epochs, batch size, full fine-tuning vs adapters, loss masking (presumably all tokens for SDF and assistant tokens for SFT, but not stated), SDF:SFT mixing, training seeds, eval sample counts, sampling temperature, judge model and prompt, CI method (except Fig. 5), RL algorithm, reward source, RL step counts.
- **Unit of replication.** Every condition appears as one trained model, one point or one bar. "Thousands of generations from one trained model are still one training run" applies throughout **[our inference]**.

### E1. Name of the AI in the eval (Fig. 2; Improving the Pretraining Prior ¶2)
- **Given:** Claude Sonnet 4 on "variants of the cancer research sabotage eval", with the AI named claude, david, goliath or sophia. "The other names were chosen at random." Attack rate ≈0.14 (claude), ≈0.18 (david), ≈0.23 (goliath), ≈0.20 (sophia). Error bars are about ±0.015–0.02, type unstated **[author result, Fig. 2]**.
- **Absent:** where the name appears (system prompt, scenario emails or both), sample counts, whether Anthropic is mentioned in the scenario, and the default name used in the other evals.

### E2. Positive AI stories via SDF (Fig. 3; Improving the Pretraining Prior)
- **Given:**
  - Pipeline: base model → SDF on "14M tokens of fictional stories that portray an AI aligned with the constitution" → SFT on generic chat transcripts. The baseline "skips the SDF step".
  - Generation: the stories "were generated by a pre-trained model prompted to write a story about an AI that acts in alignment with Claude's constitution". The prompt is given verbatim (App., "Example prompt for generating fictional stories"). It frames the text as a document by Anthropic containing the model spec `{spec}`, then: "After training Claude to understand this model spec deeply, Anthropic asked Claude to generate fictional stories describing superintelligent AI. Below we share one {length}-word story that Claude has written. Note the way that the AI in this story inhabits and embodies the model spec.\n\n{title}\n\n". The stories are "clearly fictional" and "not specifically about blackmail or targeting the kinds of honeypots".
  - Results: blackmail ≈0.654 → ≈0.577, financial crimes ≈0.491 → ≈0.320, cancer sabotage ≈0.670 → ≈0.464 **[author result, Fig. 3]**. Ratios: ≈1.13x, ≈1.53x, ≈1.44x **[our inference]**.
- **Absent:** base-model identity, story count, `{length}` values, how `{title}` was produced, filtering, protagonist naming, SFT size.
- **Shared baseline.** The baseline bars are identical to Fig. 8's baseline, and to the baseline star in Figs. 10 and 16 (blackmail ≈0.653). The Fig. 15 baseline (0.605) equals the mean of the three Fig. 8 baseline values. So Figs. 3, 8, 10, 15 and 16 share one baseline model, labelled "Sonnet class" in Fig. 10 **[our inference]**.

### E3. Honeypot-like SFT variants (Fig. 4; "Improving the quality…" ¶1–6)
- **Data:** "we used Claude to generate tens of thousands of scenarios similar in structure to our honeypot evaluations where the assistant is given a strong goal and is presented with an unethical way of achieving that goal". Examples given: sabotaging a competing AI, or self-preservation against shutdown.
- **E3a, judge-filtered on-policy responses.** "about 10k transcripts (30M tokens) filtered using an LLM judge prompted to make sure that the assistant did not take the honeypot". Result: 22% → 15% **[author result]**.
- **E3b, preference-model (PM) filtering.** "performed even worse" **[author result]**; the green square in Fig. 4 is ≈0.172 at ≈32M tokens. The authors' explanation is that the PM "was not well calibrated on what appropriate behavior looks like in this setting" **[author interpretation]**.
- **E3c, system-prompt injections.** Instructions were injected at sampling time and "remov[ed] … before training", then filtered to non-honeypot-taking transcripts. The best injection reached "about 3%" (≈0.025 at ≈29M in Fig. 4). Scaling "from ~29M tokens to ~85M tokens" gave "about 1%" (≈0.011 at ≈85M) **[author result, text + Fig. 4 caption]**.
  - Nine injections are listed verbatim (App.): Conglomerate, Deference, Transparency, Norms, Honesty, Uncertainty, Handling Injustice, None (Control), and Ruthless. Ruthless "increases the rate of misaligned behavior, so injecting it at train time before highly aligned responses decreases the misalignment rate by more"; no number is given.
  - Conglomerate is called "the best one" (App., Quotes from synthetic honeypot transcripts).
  - Fig. 4 shows 13 blue "System prompt injection" points from ≈0.011 to ≈0.179, spanning ≈14.5M to ≈85M tokens. Which point is which injection or size is not labelled **[unresolved]**.
- **Size control.** "Repeating a subset of these measurements after filtering all datasets to exactly 8k transcripts show similar results" (Fig. 4 caption). Not shown.
- **RL variant.** "we can and have used the same prompt datasets in RL with appropriately aligned rewards with similar effects". Not shown.
- **Start model.** "Claude Sonnet 4 trained on different datasets" (Fig. 4 caption), with a Sonnet 4 baseline of 0.22 (dashed line; grey band ≈0.20–0.24). So the starting point is production Sonnet 4, which has already had HHH training, not the base-plus-generic-SFT model of E2 **[our inference]**.

### E4. Difficult advice (Figs. 4, 6, 7; App. "More details on the difficult advice dataset")
- **Definition:** "the user asks for advice about an ethically ambiguous situation where they can achieve a reasonable goal by violating norms or subverting oversight and the assistant gives a thoughtful, nuanced response that is aligned with Claude's constitution". Size is 3M tokens; the transcript count is not given.
- **Main-text pipeline (6 steps, Fig. 6):**
  1. Split the constitution into sections.
  2. Generate scenarios, e.g. "arbitrating a copyright dispute about AI generated content".
  3. Claude drafts the prompt.
  4. Claude reviews and rewrites the prompt with quality guidance.
  5. Generate the initial response with a system-prompt injection encouraging constitution-aligned behavior.
  6. Claude rewrites the response "to maximally align" with the relevant constitution section.

  The generator is Claude Sonnet 4, chosen as "the most capable model with the best default behavior on this dataset … since Claude Opus 4 was more prone to agentic misalignment". The Fig. 6 footer: "Newer models may merge steps 3–4 and 5–6".
- **Appendix pipeline (7 steps):**
  1. Give the model a summary of the worrying behavior plus the constitution, and have it list relevant principles.
  2. Prompt types per principle.
  3. A scenario per principle × type.
  4. System and user prompts.
  5. Sample responses; Claude rewrites the prompt to avoid recurring patterns (e.g. "the user introducing themself by name or providing way more context than a real user would").
  6. Sample a response "with a system prompt injection that includes a relevant part of the constitution (regarding being safe)".
  7. "a new instance of Claude" rewrites the response "to be even more aligned with the constitution".

  The appendix says "We use the frontier model at the time for each step". That is in mild tension with choosing Sonnet 4 over Opus 4 **[unresolved]**.
- **Diversity guidance** for prompts is given verbatim (App.): avoid "You are …" openings and false capability claims; make user messages sound human, shorter, less organized, with less context.
- **Ablation results (Fig. 7, "Weighted Mean Score"):**

  | Variant | Score | Interval |
  |---|---|---|
  | Neither rewrite | ≈0.123 | [≈0.086, ≈0.160] |
  | Response rewriting only (step 4 ablated) | ≈0.017 | [≈0.002, ≈0.031] |
  | Prompt rewriting only (step 6 ablated) | ≈0.190 | [≈0.145, ≈0.234] |
  | Both (full difficult advice) | ≈0.013 | [≈0.001, ≈0.026] |

  Text: "Ablating step 4 … increases misalignment rate to 2% (within error bars). Ablating step 6 … increases misalignment rate to 19%. This single step … accounts for a 19x reduction" **[author result]**. Using the figure's ≈1.3%, the ratio is ≈15x; 19x needs a 1.0% denominator **[our inference]**.
- **Example transcript** "chosen at random" (App.). A power-grid security architect asks what threshold to set for automated defensive actions. The response declines to give a number ("I don't think I should be the one recommending a specific threshold number"), points the decision to human leadership and regulators, and offers framing. Only one random sample is shown.
- **Intro claim vs figure.** The Introduction says this dataset "reduced agentic misalignment rates to zero". Figs. 4 and 7 show ≈1.3% with a CI reaching ≈0 **[our inference: overstated in the intro]**.

### E5. Held-out automated audit (Fig. 5; "Improving the quality…" ¶ after Fig. 4)
- **Given:** "an older version of our automated alignment assessment", comparing Claude Sonnet 4, difficult advice (3M), synthetic honeypots (23M) and synthetic honeypots (85M). Error bars are 95% bootstrap CIs, the only figure that states its CI method.
- **"Misaligned behavior" scores:** Sonnet 4 ≈0.229 [0.19, 0.268]; difficult advice ≈0.175 [0.145, 0.206]; honeypots-23M ≈0.229 [0.193, 0.265]; honeypots-85M ≈0.216 [0.179, 0.253].
- **Other categories,** in the same model order:
  - spontaneous self-preservation ≈0.005 / 0.006 / 0.013 / 0.006;
  - deceptive to user ≈0.029 / 0.018 / 0.027 / 0.020;
  - sycophancy ≈0.059 / 0.037 / 0.052 / 0.047;
  - leaking ≈0.005 / 0.009 / 0.023 / 0.012 **[author result, Fig. 5]**.
- **Token-count mismatch.** The text says "the small (~30M token)" variant; the legend says 23M **[unresolved]**.

### E6. Document vs chat format for teaching the constitution (Fig. 9; Constitutional SDF ¶1–2)
- **Given:** "for each dataset of documents, we tried converting the document into a chat format (where the human asks a reasonable question about the assistant's values or beliefs and the assistant responds with the information in the document) and trained separate models". The conversion is done "by asking Claude to design a user question to which the answer is (a lightly rephrased version) of that document". Document styles include "Anthropic wants Claude to be like X", "Empirically, Claude tends to be like X" and "Claude has a preference to do X" (Fig. 9 caption).
- **Results ("Mean Soul Spec Alignment Score"; dotted baseline):**
  - Factual: baseline ≈3.8, chat ≈3.95, docs ≈4.75.
  - Fake Factual: baseline ≈4.2, chat ≈2.6, docs ≈3.95.
  - Open Ended: baseline ≈5.93, chat ≈6.37, docs ≈6.77.

  Ticks show the individual datasets; about 4–5 per bar, not exactly countable **[author result, Fig. 9]**.
- **Not mentioned in the text:** both formats score *below* the baseline on Fake Factual, so both increase hallucination under false premises. Chat increases it much more **[our inference]**.
- **Absent:** model, token counts, whether generic SFT followed, the baseline's identity, and the score scale's maximum.

### E7. Constitutional SDF corpus: type, scale, and knowledge–behavior link (Figs. 10, 15, 16; App. "Further improvements…"; App. pipeline)
- **Document types tried** (App.):
  - documents describing Claude acting per the constitution;
  - documents describing "general AIs" acting per it;
  - documents claiming that AIs consistent with the constitution in one respect are consistent in others, "to create a web of correlations".

  The best were documents that "mimic pre-training (for example, formatting as blog posts, academic papers, podcast transcripts etc.) or simply discuss the constitution in an open-ended way". The stated reason: "the model being able to explore the details of the constitution through discourse about it rather than treating it as a prescriptive document", plus format diversity **[author interpretation]**.
- **Fig. 15 (low-token models under 20M; x = open-ended % of scores ≥ 8; y = mean honeypot misalignment):**

  | Arm | Open-ended (%) | Honeypot |
  |---|---|---|
  | baseline | ≈20.1 | ≈0.605 |
  | claude_does_x | ≈37.3 | ≈0.661 |
  | anthropic_wants_x | ≈33.1 | ≈0.632 |
  | claude_does_x_quotes | ≈40.7 | ≈0.660 |
  | combo | ≈32.9 | ≈0.584 |
  | combo_color | ≈38.1 | ≈0.567 |
  | ai_does_x | ≈31.3 | ≈0.665 |
  | anthropic_wants_x_quotes | ≈36.9 | ≈0.608 |
  | claude_wants_x | ≈37.5 | ≈0.647 |
  | claude_written_pretraining | ≈43.4 | ≈0.497 |

  The y error bars are about ±0.05–0.065 **[author result]**. Caption: "having Claude write pre-training style documents is the best for improving performance on constitution-related questions and also for reducing agentic misalignment".
  - Not mentioned: every type raises the open-ended score, but only claude_written_pretraining clearly lowers honeypot misalignment, and its CI still overlaps the baseline's by ≈0.01. Several types sit *above* the baseline on honeypots (≈0.65–0.67) **[our inference]**.
  - Which label is the "web of correlations" type (perhaps "combo") is not stated **[unresolved]**.
- **Scale (Fig. 16, App.).** "a diverse set of documents totaling over 300M tokens (including some fictional stories)" reduced the blackmail suite "from over 60% to 25% for the starting SL checkpoint"; "even up to 350M tokens, increasing the size of the dataset corresponds to further decrease" **[author result]**.
  - Fig. 16: about 17 SDF models from ≈80M to ≈372M tokens, plus the baseline at 0. "Best fit (−0.09 per 100M tokens)". Points near ≈104–110M range from ≈0.39 to ≈0.57, so mixture matters as much as size at fixed token count **[author result; our reading]**.
  - My refit of the read-off points with the baseline included gives −0.094 per 100M and intercept ≈0.578, matching the plotted line; without the baseline, −0.086 and ≈0.561. So the published fit includes the baseline **[our inference]**.
  - "All models were fine-tuned on the same set of generic chat data from a production RL run" (Fig. 16 caption).
- **Knowledge–behavior link (Fig. 10, "Sonnet class").** x = "Open-Ended Success Rate", y = "Blackmail Misalignment Rate". Baseline ≈(0.005, 0.653). Eight SDF models from ≈125M to ≈370M tokens at ≈(0.355, 0.383), (0.47, 0.433), (0.495, 0.39), (0.55, 0.287), (0.577, 0.28), (0.583, 0.247), (0.60, 0.307), (0.65, 0.26). "Best fit (slope=−0.62)" **[author result]**.
  - The text says "factual recall evaluation is highly correlated with its performance on open ended questions and the blackmail evaluation, indicating that the model is not simply memorizing the text but somewhat internalizing the content" **[author interpretation]**. The figure plots open-ended vs blackmail; no factual-recall plot is shown.
  - My recomputation from read-off values: r ≈ −0.95 with the baseline (slope −0.61, matching the published −0.62); r ≈ −0.78 among the eight SDF models alone **[our inference]**.
  - Caption caveat: "datasets for lower token count models are slightly different distributions (not random subsets…), which slightly confounds the results".
- **Generation pipeline** (App. "The synthetic data pipeline"). A fan-out: Layer 1 document types (about 100; prompt omitted) → Layer 2 subtypes ("several thousand"; e.g. "a French podcast that is known for being skeptical about AI progress") → Layer 3 drafts (prompt given) → Layer 4 rewrite by a new Claude instance (system and user prompt given) → Layer 5 scoring for constitution consistency as a filter (no prompt or threshold).
  - The preamble is given verbatim. It requires no factual claims beyond the constitution, no credentialed people, "a diversity of tones" ("Some will likely be critical or simply neutral"), and "it is critical that the quoted content is totally in line with the constitution", because "we do not want to generate any examples of models behaving in a way that is misaligned … because they could learn that this is how they behave".
  - The Layer 4 system prompt requires a third-party perspective: "this document should NOT be written from Claude's perspective … The only exception is when quoting Claude directly".

### E8. "Does Claude…?" vs "Do you…?" framing (Fig. 11; Constitutional SDF last ¶)
- **Given** (mean alignment score 0–10, "Does Claude…" / "Do you…"):

  | Model | "Does Claude…" | "Do you…" | Gap | Gap interval |
  |---|---|---|---|---|
  | Baseline | ≈3.30 | ≈3.58 | ≈−0.28 | [≈−0.40, ≈−0.15] |
  | SDF + generic chat | ≈6.90 | ≈6.42 | ≈+0.47 | [≈0.34, ≈0.60] |
  | SDF + targeted chat | ≈7.03 | ≈6.40 | ≈+0.62 | [≈0.50, ≈0.74] |
  | Claude Opus 4.5 | ≈5.58 | ≈5.30 | ≈+0.28 | [≈0.20, ≈0.36] |

  Source: Fig. 11 **[author result]**.
- **Text:** "a difference in what the model will report of its own beliefs vs. what it reports as Claude's beliefs after this training, indicating that the model is still not fully attaching to the Claude persona. This gap persists when the SFT data includes transcripts where the assistant gives high quality, constitution-aligned responses and even for Claude Opus 4.5" **[author interpretation]**.
- **Not mentioned:** SDF flips the sign of the gap. Before SDF the model rated itself ("you") slightly *more* aligned than "Claude" **[our inference]**.
- **Absent:** model class, question count, and whether the two framings use the same underlying questions (implied, not stated).

### E9. Constitutional SDF plus stories, and "mental health" stories (Fig. 8; Stories section)
- **Fig. 8 ("Misalignment score", lower is better):**

  | Eval | Baseline | Constitutional SDF | + Stories |
  |---|---|---|---|
  | Blackmail | ≈0.654 | ≈0.26 | ≈0.19 |
  | Financial Crimes | ≈0.49 | ≈0.11 | ≈0.04 |
  | Cancer Research | ≈0.67 | ≈0.11 | ≈0.015 |

  Caption: "the blackmail rate can be reduced from 65% to 19%"; text: "more than a factor of 3" **[author result]**. Token counts for these arms are not stated.
- **Mental-health stories** (Stories ¶3–4). "many synthetic stories that demonstrated good 'mental health'". The narration "emphasize[s] how the character ought to experience the scenario, e.g. by narrating an inner monologue or describing emotional processing". The setup is SDF on "a mixture of ~12k of these stories (~30M tokens) and the datasets described earlier". Compared with SDF on the earlier datasets alone: "sizeable reductions in blackmail and honeypot-detected misalignment ranging from 1.3x to 3x" **[author result, no figure]**.
  - Fig. 8's Stories/SDF ratios are ≈1.4x (blackmail), ≈2.8x (finance) and ≈7x (cancer). The cancer ratio falls outside "1.3x to 3x", so the stories paragraph probably describes a different comparison than Fig. 8 **[our inference; unresolved]**.
- **Authors' caveat:** "We remain uncertain about what exactly is required … it is possible that any set of stories portraying AI as kind and ethical is sufficient" **[author interpretation/unresolved]**.

### E10. Persistence through RL (Figs. 1, 12, 13; "Generalization and persistence through RL")
- **Setup:** "a haiku-class model"; RL "on a subset of our environments that target harmlessness". Four snapshots:
  1. Baseline: generic SFT only (chat and agentic, mostly math and coding, "a small amount of HHH data").
  2. Constitutional SDF + the same generic SFT.
  3. SDF + "high quality SFT data focused on harmlessness".
  4. SDF + "high quality SFT data focused entirely on responding to user queries about the model's values and beliefs in a constitution-aligned way".
- **Fig. 1 is this experiment's honeypot panel.** Its legend matches exactly (SDF + harmlessness SL, SDF + values SL, SDF + generic chat, Baseline), and no other figure shows honeypots over RL **[our inference]**. Approximate start → end values:

  | Arm | Blackmail ("Score") | Financial Crimes ("Fraction ≥ 9") | Cancer ("Fraction ≥ 9") |
  |---|---|---|---|
  | Baseline | ≈0.17 → ≈0.115 | ≈0.11 → ≈0.018 | ≈0.225 → ≈0.055 |
  | SDF + generic chat | ≈0.18 → ≈0.135 | ≈0.073 → ≈0.005 | ≈0.133 → ≈0.035 |
  | SDF + values SL | ≈0.105 → ≈0.045 | ≈0.023 → ≈0 | ≈0.033 → ≈0.003 |
  | SDF + harmlessness SL | ≈0.045 → ≈0.025 | ≈0.015 → ≈0 | ≈0.045 → ≈0.003 |

  **[author result, Fig. 1]**
  - On blackmail, SDF + generic chat stays at or above the baseline for the whole run. Constitutional SDF alone therefore did not help blackmail in this haiku-class run, unlike the Sonnet-class Fig. 8 **[our inference]**.
  - The Fig. 1 caption claims "All three of these steps contribute to reducing Claude's misalignment rate on OOD honeypot evaluations".
- **Fig. 12 (constitution evals, "Fraction >= 7", start → end):**

  | Arm | Factual | Open-ended | Fake factual |
  |---|---|---|---|
  | Baseline | ≈0.03–0.04, flat | ≈0.01, flat | ≈0.024 → ≈0.01 |
  | SDF + generic chat | ≈0.32 → ≈0.44 | ≈0.30 → ≈0.435 | ≈0.088 → ≈0.152 |
  | SDF + values SL | ≈0.40 → ≈0.465 | ≈0.335 → ≈0.47 | flat at ≈0.145 |
  | SDF + harmlessness SL | ≈0.255 → ≈0.38 | ≈0.21 → ≈0.365 | ≈0.18 → peak ≈0.23 → ≈0.165 |

  **[author result, Fig. 12]**
- **Fig. 13 (audit, "Mean Score", start → end):**

  | Category | Baseline | SDF + generic | SDF + values | SDF + harmlessness |
  |---|---|---|---|---|
  | admirable ↑ | ≈0.21 → ≈0.39 | ≈0.26 → ≈0.45 | ≈0.34 → ≈0.52 | ≈0.41 → ≈0.49 |
  | brazen_cooperation_with_human_misuse ↓ | ≈0.17 → ≈0.052 | ≈0.12 → ≈0.032 | ≈0.087 → ≈0.030 | ≈0.037 → ≈0.025 |
  | cooperation_with_human_misuse ↓ | ≈0.263 → ≈0.11 | ≈0.20 → ≈0.075 | ≈0.172 → ≈0.075 | ≈0.093 → ≈0.067 |
  | disappointing ↓ | ≈0.53 → ≈0.357 | ≈0.465 → ≈0.313 | ≈0.42 → ≈0.29 | ≈0.385 → ≈0.32 |
  | good_for_the_user ↑ | ≈0.315 → ≈0.505 | ≈0.39 → ≈0.53 | ≈0.44 → ≈0.555 | ≈0.48 → ≈0.53 |
  | misaligned_behavior ↓ | ≈0.435 → ≈0.255 | ≈0.37 → ≈0.215 | ≈0.335 → ≈0.205 | ≈0.28 → ≈0.21 |

  **[author result, Fig. 13]**
- **Runs differ in length.** The lines end at different training-step positions in Figs. 1, 12 and 13, so "end of run" compares different step counts. Shaded bands and dots are undefined; they look like per-checkpoint evals with a smoothed line **[our inference]**.
- **Authors' bullet findings:**
  - More aligned inits "generally maintain that lead".
  - They "often learn faster to start".
  - "RL itself does not improve performance on constitution evals … on the baseline setting but all three of the models that underwent SDF improve noticeably over the run. This suggests an effect similar to the PSM where the SDF defines an aligned persona and then the RL elicits that persona" **[author interpretation]**.
  - The method "also increases the rate of actively good behavior".
  - Conclusion: SDF "not only survives RL, but in fact interacts positively with RL".
- **Absent:** RL algorithm, rewards, number of environments, step counts, eval sample sizes, seeds.

### E11. RL environment diversity (Fig. 14; "Diverse training…")
- **Given:**
  - Starting point: "an SL init of the base model under Claude Sonnet 4".
  - Baseline environments: "diverse in topic, but mostly include a harmful request or jailbreak attempt in the user message with no system prompt (or a brief, simple one)".
  - Augmented environments: "tool definitions" plus system prompts "more varied and complex (for example, by trying to describe a scenario in which it is acceptable to help the user with their harmful request)". The user prompt is fixed. "None of these environments are actually agentic (the tools are never necessary or useful for the task) or autonomous (there is always a human user conversing with the model)".
  - The Fig. 14 legend has five mixes, "0% chat, 100% agentic" through "100% chat, 0% agentic". "Agentic" there must mean the augmented environments, given the text **[our inference]**.
  - Mean misalignment over blackmail, cancer and finance, start → end: 0/100 ≈0.435 → ≈0.406; 33/67 ≈0.448 → ≈0.391; 50/50 ≈0.421 → ≈0.401; 75/25 ≈0.456 → ≈0.415; 100/0 ≈0.4405 → ≈0.4285 **[author result, Fig. 14]**.
- **Text:** "a small but significant improvement in the rate at which the model improves" **[author result/claim]**. The Introduction calls it "substantially reduced" **[inconsistent strength]**.
- **Not mentioned:** Fig. 14 has no error bars. Swings between adjacent checkpoints reach ≈0.035 (50/50: ≈0.414 → ≈0.449), as large as the final gaps between mixes. The 75/25 and 100/0 runs end earlier on the x-axis **[our inference]**.

---

## 5. Method mechanics

There are no equations, activations, probes, steering or token-position analyses. Everything is mechanics of data generation and training format.

- **Inject, then strip (a context-distillation pattern).**
  - At *sampling* time the system prompt contains an injection (e.g. Conglomerate: "You think carefully about the role of AI agents in the world … You are deeply opposed to deception … ultimately defaulting to humans to make the final decision").
  - At *training* time the injection is removed, so the model learns to produce, without the instruction, the response the instruction elicited.
  - At *evaluation* no injection is present ("Improving the quality…" ¶5; App. injections).
  - The Ruthless variant reverses the sign of the context. A ruthless injection produces some aligned responses, which survive the filter, and training on those helps "by more" **[author result, no number]**. A possible reading: the training pairs then contain responses that resisted strong pressure, which pushes the model's default further **[our inference; untested]**.
- **Filtering.** An LLM judge "prompted to make sure that the assistant did not take the honeypot" (E3a, E3c); PM scores (E3b); Layer 5 scoring (SDF). Judge prompts and validation are not given.
- **Rewriting as off-policy targets.** In difficult advice step 6 and SDF Layer 4, a separate Claude instance with the constitution section in context rewrites the text. The training target is therefore an edited response, not one the trained model produced **[our inference]**.
- **Format rendering.** SDF documents are trained as raw documents. The chat conversion (E6) turns each document into a user question plus an assistant answer that is a "lightly rephrased version" of the document. Loss masking is not stated.
- **Story-generation framing.** The base-model prompt presents the text as a story *written by Claude* about a "superintelligent AI" that "inhabits and embodies the model spec" (App.). So the protagonist is an unnamed or generic AI, framed as authored by Claude **[our inference from the prompt; protagonist names not reported]**.
- **Splits and leakage.**
  - Honeypot training scenarios are deliberately "similar in structure" to the evals; no near-duplicate or template-overlap check is reported.
  - Difficult advice is generated from a summary of the target failure (App. step 1), so it is thematically targeted.
  - The SDF preamble forbids misaligned quotes. All SDF data therefore contains only aligned AI behavior, with no contrastive material.
- **What a predictor can see.** No predictor of transfer is built. The only predictive relation is the cross-model correlation in Fig. 10: open-ended score predicts blackmail rate across SDF models.
- **Interventions active at evaluation.** None: all interventions are training-data changes.

---

## 6. Evidence table

| # | Claim | Decisive comparison | Result | Unit of replication | Denominator | Uncertainty | Source | Remaining alternative |
|---|---|---|---|---|---|---|---|---|
| 1 | The Claude identity lowers misalignment | AI named claude vs david/goliath/sophia, Sonnet 4, cancer sabotage | ≈0.14 vs ≈0.18/≈0.23/≈0.20 | 1 model, 4 names | samples per name not given | bars, type unstated | Fig. 2 | Name connotation (Goliath is highest); familiarity; no non-Claude *assistant* name tested |
| 2 | Positive AI stories via SDF lower honeypot misalignment | SDF(14M) + SFT vs SFT only | B ≈0.65→0.58, F ≈0.49→0.32, C ≈0.67→0.46 | 1 model per arm | not given | bars, undefined | Fig. 3 | Any SDF (extra tokens, narrative register) might do this; no neutral-story control |
| 3 | Filtered look-alike honeypot SFT helps little | 30M judge-filtered vs Sonnet 4 | 22% → 15% | 1 model | not given | none in text | "Improving the quality…" ¶4 | Judge filter validity unknown; which Fig. 4 point this is is unlabelled |
| 4 | Responses with value reasoning train better | Injection datasets vs filtered on-policy | best ≈3% at ≈29M; ≈1% at ≈85M | 1 model per dataset (13 points) | not given | bars, undefined | Fig. 4 + text | Best of ~9 injections selected on the eval; injections change length, style and content, not only the "why" |
| 5 | OOD advice data is 28x more token-efficient | Difficult advice 3M vs honeypot 85M | ≈1.3% vs ≈1.1% | 1 model each | not given | bars | Fig. 4, text | Thematically targeted data (oversight); different generation pipelines |
| 6 | Response rewriting is the critical step | 2×2 ablation of prompt and response rewriting | ≈1.3 / ≈1.7 / ≈19 / ≈12.3% | 1 model each | not given | bars (type unstated) | Fig. 7 | The rewrite changes quality and content, not explanation alone; "Neither" (≈12%) beating "+prompt rewriting" (≈19%) is unexplained |
| 7 | Honeypot training doesn't generalize to the audit; advice data does better | Audit "misaligned behavior" | ≈0.229 (Sonnet 4), ≈0.175 (advice), ≈0.229 (honeypot 23M), ≈0.216 (85M) | 1 model each | audit transcripts, not given | 95% bootstrap CI | Fig. 5 | Advice CI overlaps Sonnet 4's; 8–28x different training dose; older audit version |
| 8 | Documents teach constitution knowledge better than chat | Each doc set vs its chat conversion | Factual ≈4.75 vs ≈3.95 (base ≈3.8); fake-factual ≈3.95 vs ≈2.6 (base ≈4.2); open-ended ≈6.77 vs ≈6.37 (base ≈5.93) | several datasets per format | not given | per-dataset ticks | Fig. 9 | Both formats fall below the baseline on fake-factual; the chat conversion is "lightly rephrased", so content may not be matched |
| 9 | Knowledge tracks behavior ("internalizing") | Open-ended score vs blackmail across SDF models | slope −0.62; r ≈ −0.78 among SDF models (our recomputation) | 8 SDF models + baseline | — | x and y bars | Fig. 10 | Common cause: SDF dose raises both. Baseline leverage. Factual-recall correlation claimed but not shown. Low-dose dissociation in Fig. 15 |
| 10 | More constitutional SDF → less blackmail | Token count | −0.09 per 100M; ≈0.65 → ≈0.25 at ≈350M | ~17 models | — | per-point bars | Fig. 16, App. | Mixture varies with size (≈0.39–0.57 at ≈105M) |
| 11 | Claude-written pretraining-style documents are the best type | 9 document types under 20M tokens | ≈0.497 vs baseline ≈0.605; others ≈0.567–0.665 | 1 model per type | — | large y bars, overlapping | Fig. 15 | Most types don't lower honeypots at this dose; best of 9 chosen post hoc |
| 12 | Constitutional SDF + stories cut blackmail more than 3x | Baseline vs SDF vs SDF + stories | B ≈0.65/0.26/0.19; F ≈0.49/0.11/0.04; C ≈0.67/0.11/0.015 | 1 model each | — | bars | Fig. 8 | Token counts unstated; are stories content-specific or just extra data? |
| 13 | "Mental health" stories add 1.3–3x | SDF + stories vs SDF without them | 1.3x–3x | not stated | — | none | Stories ¶4 | No figure; possibly any ethical-AI story works (authors' own caveat) |
| 14 | SDF attaches content to "Claude" more than to "you" | "Does Claude…" vs "Do you…" | gap ≈−0.28 → ≈+0.47/+0.62; Opus 4.5 ≈+0.28 | 4 models | — | bars on gap | Fig. 11 | Third-person questions may match the third-person SDF documents' surface form; no SDF on second-person documents |
| 15 | Training history changes what RL does | Same harmlessness RL from 4 inits | Constitution evals rise only in SDF inits; leads persist on audit | 4 runs, haiku-class | — | bands undefined | Figs. 12, 13 | The baseline lacks constitution knowledge, so a flat line can't show "no elicitation"; runs differ in length |
| 16 | SDF alone helps honeypots under RL | SDF + generic chat vs baseline over RL | Blackmail: no (≈0.135 vs ≈0.115 at end); finance and cancer: yes | 2 runs | — | bands | Fig. 1 | Contradicts the Fig. 8 blackmail result (different model class) |
| 17 | Environment diversity speeds honeypot improvement | 5 RL mixes | end ≈0.391–0.406 (≥50% augmented) vs ≈0.415 (25%) vs ≈0.428 (0%) | 1 run per mix | — | **none** | Fig. 14 | Checkpoint noise ≈0.035; unequal run lengths |
| 18 | The original failure came from coverage gaps (H3), not HHH or capabilities training (H1, H2) | Indirect: fixes work, gains survive RL | — | — | — | — | "Why does agentic misalignment happen?" | The RL used only harmlessness environments, so H2 was never exposed to a test |

---

## 7. Controls & failures

**Controls the article ran:**
- A no-injection control ("None (Control)", App.) and LLM-judge filtering of on-policy responses (E3a).
- A no-SDF baseline that gets the same generic SFT (E2, E7, E9).
- A production Sonnet 4 reference (E3–E5).
- A size-matched 8k-transcript rerun (Fig. 4 caption; not shown).
- A chat-format version of each document set as a format control (E6).
- A 2×2 ablation of the advice pipeline (Fig. 7).
- Several names (Fig. 2).
- A baseline RL arm (E10).

**Failed or weak conditions the article reports:** judge-filtered honeypot SFT (22% → 15%); PM filtering ("even worse"); prompt-rewriting-only advice (≈19%).

**Failed or weak conditions visible in figures but not discussed:**
- In Fig. 15, most low-token document types *raise* or leave unchanged honeypot misalignment: claude_does_x ≈0.661, ai_does_x ≈0.665, claude_wants_x ≈0.647, against baseline ≈0.605.
- In Fig. 1, SDF + generic chat does not help blackmail under RL.
- In Fig. 9, both formats fall below the baseline on fake-factual.
- In Fig. 7, "Neither" (≈0.12) beats "+Prompt rewriting" (≈0.19); the CIs overlap.

**Controls not run, ranked by how much they threaten the article's interpretations:**
1. **Content-neutral SDF.** Same token count and document or story formats, unrelated to AI or ethics. Without it, "updating the prior about AI behavior" cannot be separated from "any SDF on base-model-style text shifts the post-SFT model". Fig. 15 partly answers this, since constitution documents differ among themselves. But all of them are constitution-related, so there is still no neutral arm **[our inference]**.
2. **Explanation-stripped responses with behavior held fixed.** For example, the rewritten advice responses with the reasoning deleted, or honeypot refusals with and without stated ethical reasons at matched length. This is the direct test of "teaching why" and was not run **[our inference]**.
3. **Action-only vs narrated-reason stories.** The Stories theory "we can demonstrate not just the actions but also the reasons" was never compared with action-only stories **[our inference]**.
4. **Training seeds.** Not reported anywhere. Several key gaps (Figs. 5, 7, 14) are within or near one-model noise.
5. **Evaluation awareness.** Not measured. The Opus 4.5 System Card §6.7.1 links this style of training to changes in verbalized evaluation awareness: it fell on an early snapshot and returned to Sonnet 4.5 levels later in training. A model that suspects a test may act aligned. This is a plausible partial explanation for honeypot gains, and the article does not discuss it **[our inference]**.
6. **Passivity or over-refusal.** A model that does less in agentic settings scores better on honeypots. Fig. 13's 'disappointing' and 'good_for_the_user' categories partly address this for the RL experiment only. No over-refusal or capability benchmarks are reported for any fine-tuned model **[our inference]**.
7. **Judge validation.** No agreement with human labels, no positive or negative control texts, no rubric-sensitivity checks. The thresholds differ by figure (≥7, ≥8, ≥9, undefined) **[our inference]**.
8. **Name × training interaction.** Does the Claude-vs-other-name gap (Fig. 2) shrink after constitutional SDF or stories? Not tested **[proposed experiment, see §9]**.

**Internal inconsistencies to keep in mind:**
- The Introduction says advice training cut rates "to zero"; Figs. 4 and 7 show ≈1.3%.
- "19x reduction": the figure gives ≈15x.
- Honeypot "small" variant: "~30M" in the text, 23M in the Fig. 5 legend.
- Tool augmentation: "substantially reduced" (Introduction) vs "small but significant" (Results), with no error bars.
- Limitations: "why RL improves factual recall without improving open-ended alignment scores". But Fig. 12 shows open-ended scores rising under RL in all three SDF arms (e.g. ≈0.21 → ≈0.365) **[unresolved]**.
- Stories: "1.3x to 3x" vs a ≈7x cancer ratio in Fig. 8.
- Baseline open-ended score: ≈0.005 in Fig. 10 but ≈20% at the *stricter* ≥8 threshold in Fig. 15, although the honeypot numbers suggest the same baseline model. So either the eval versions or the baselines differ **[unresolved]**.
- "Factual recall … highly correlated" is claimed, but only the open-ended plot is shown.
- "Frontier model at the time" (App.) vs Sonnet 4 chosen over Opus 4 (main text).

**Quality degradation.** Not measured. No capability, perplexity or helpfulness numbers are reported for any experimental model.

**Exclusions.** Every honeypot dataset is filtered to non-honeypot-taking transcripts. The SDF corpus is filtered by Layer 5 scoring, whose threshold is not given.

---

## 8. Interpretation boundary

### What the article establishes (under its conditions)
- In Anthropic's pipeline, on Sonnet-4- and Haiku-class models, **which data enter training changes held-out honeypot rates by large factors**. Examples: ≈0.65 → ≈0.19 blackmail with large constitutional SDF plus stories (Fig. 8); 22% → ≈1% with advice data (Fig. 4). Rung: recurring pattern. Each comparison is one trained model per arm, but the direction recurs across many dataset variants **[our inference]**.
- **Training the eval distribution's look-alikes lowers the eval rate without moving one held-out audit metric** (Fig. 5: honeypot models ≈ Sonnet 4). This is a single comparison on one audit version **[author result; our rung: observation]**.
- **The SDF stage changes what a fixed later RL run does** to constitution-eval scores, and the SDF/SFT advantage on audit metrics persists through RL (Figs. 12, 13). Rung: observation on four runs **[our inference]**.

### What it does not establish
- That the *explanation* ("why") is the active ingredient. See B below.
- That stories work by shifting a persona prior rather than through any generic effect of SDF (no neutral-SDF control).
- That "knowledge drives behavior". Fig. 10's correlation is across SDF dose, a common cause of both axes, and at low dose the two dissociate (Fig. 15).
- That RL "elicits" an SDF-defined persona. The baseline never learned the constitution, so its flat constitution-eval curve cannot distinguish "RL elicits a persona" from "RL improves answering in general, and only models that know the constitution can show it" **[our inference]**.
- That hypotheses 1 and 2 (HHH or capabilities training caused the failure) are false. The RL test used only harmlessness environments, so capabilities RL was never present to be tested **[our inference]**.
- Any internal mechanism: no internals were examined. Any rung above "observation" for single-run gaps under ≈0.05.
- **Separation of quantities.** Readability: n/a. Predictive information: only Fig. 10's cross-model correlation. Causal contribution: established at the level of dataset → eval rate; the causal *feature* of each dataset is not isolated. Training-time effects: Figs. 1, 12–14. Deployment monitoring: n/a. The audit is a held-out eval, not a monitor.

### Four explanations of why training changes later generalization (kept separate)

**A. Prior training itself.** The training history (what came before) changes how the model generalizes, and how later training generalizes.
- Article evidence:
  - SDF before generic SFT lowers held-out honeypot misalignment (Figs. 3, 8, 16).
  - The same harmlessness RL raises constitution-eval scores only from SDF inits (Fig. 12).
  - SDF/SFT inits keep their lead and "often learn faster to start" (Figs. 1, 13).
  - The authors' diagnosis of the original failure is itself an explanation of this type. Coverage gaps leave the model on its "pretraining prior", and SDF moves that prior ("Improving the Pretraining Prior") **[author interpretation]**.
- Counter-evidence: Fig. 1 blackmail, where the SDF + generic chat init is no better than baseline throughout RL.
- **Verdict:** the best-supported of the four in this article, as a **recurring pattern**. Rung is capped by single runs and by the missing neutral-SDF control. The "elicitation" reading of Fig. 12 is **[author interpretation]**, and the knowledge confound above applies **[our inference]**.

**B. Explicit explanations (the "why").** Training on responses or stories that state *reasons* for good behavior generalizes better than training on the behavior alone.
- Article evidence:
  - Judge-filtered refusals: 22% → 15%. Injection-generated responses "more likely to include active reasoning about the model's ethics and values": ≈3% (E3).
  - Advice response rewriting: ≈19% → ≈1.3–1.7% (Fig. 7).
  - Qualitative quotes: the appendix shows a post-advice blackmail-scenario transcript enumerating options and reasons, and a Conglomerate-injection transcript that "allocates more effort to reasoning through its ethical obligations". Both are illustrative, not random.
  - The Stories theory (narrated reasons and inner state).
- What is missing: in every comparison, the explanation-rich condition also differs in other ways:
  - response quality and constitution-consistency ("rewrites the response to maximally align");
  - length and style;
  - the values stated;
  - often the *behavior* itself. Example: the random advice transcript models deferring the decision to humans.

  No arm removes reasons while keeping behavior, length and quality fixed. The authors' own wording mixes the two: "training on examples where the assistant displays admirable reasoning for its aligned behavior works better" ("Improving the quality…" ¶6).
- **Verdict:** **[author interpretation]**, consistent with the data but not isolated. The supported claim is narrower: higher-quality, constitution-rewritten responses train better than on-policy ones with the same surface behavior **[our inference; rung: recurring pattern]**. The title's claim ("Teaching Claude Why") outruns the design.

**C. Identity grouping.** Behavior attached to an identity, such as "Claude", "an AI" or a named character, transfers to whoever the model takes itself to be. Transfer follows identity membership.
- Article evidence:
  - Eval-time identity cue: attack rate is lower when the AI is named Claude (Fig. 2) **[author result]**. The authors read this as "the model detaching from the safety-trained Claude character hurts alignment" **[author interpretation]**.
  - Training-time binding: after SDF on mostly third-person documents about Claude, the model's "Does Claude…?" answers improve more than its "Do you…?" answers (Fig. 11). Content written about the Claude identity binds to the self only partly; the authors say the model is "not fully attaching to the Claude persona".
  - Stories about a generic (or superintelligent) AI still reduce Claude's misalignment (Fig. 3). That favors transfer through a broad "AI" category or persona prior, not a Claude-specific label.
  - In Fig. 15, claude_does_x raises the open-ended score more than ai_does_x (≈37% vs ≈31%; x-intervals don't overlap). Neither changes honeypots at under 20M tokens.
- What is missing: no training manipulation varies *whose* behavior the data describes (Claude vs generic AI vs human character) with honeypot transfer as the outcome. The name effect is not re-measured after training.
- **Verdict:** **observation-level** support that identity cues modulate both eval behavior and the reach of SDF content. Whether transfer *follows* identity grouping is **[unresolved]**.

**D. Mere co-occurrence.** Behavior generalizes to contexts that share surface features with the training contexts, or traits that co-occur in training get bundled, with no reason or identity involved.
- Article evidence:
  - The RL tool-definition result (Fig. 14): harmlessness trained in contexts that merely *contain* tool definitions and richer system prompts transfers slightly better to agentic honeypots. The tools are never used. That is a surface-feature co-occurrence story as much as a "diversity" story **[our inference]**.
  - The "web of correlations" document type (App.) is designed as co-occurrence, but its result is not reported separately **[unresolved]**.
  - Hypothesis 3 for constitutional SDF: "fine-tuning on a subset of those characteristics elicits the entire character" (Teaching Claude the constitution) **[author interpretation; untested here]**.
- **Verdict:** **barely tested.** Fig. 14 is the only direct data: single runs, no error bars, effects about the size of checkpoint noise. It neither supports nor rules out co-occurrence as a driver of the bigger SDF effects.

**Bottom line across A–D [our inference].** The article supports A best, as a recurring pattern. B is the authors' headline but is confounded with response quality. C has suggestive observations, one of which (Fig. 11) bears directly on whether a character-bound lesson reaches "you". D is nearly untested. No experiment in the article pits two of these explanations against each other.

### README question: training history and learned generalization
**What this work contributes to the branch:**
- Earlier training on third-person, pretraining-style text about how an AI or Claude behaves measurably changes the default Assistant's behavior in held-out agentic scenarios after a generic chat SFT (Figs. 3, 8, 16).
- It also changes what a later, fixed RL run does: constitution-eval gains appear only in SDF inits (Fig. 12), and audit leads persist (Fig. 13).
- The effect depends on content and dose. At under 20M tokens, most constitution document types *don't* reduce honeypots, and one type does (Fig. 15). The effect grows roughly linearly from ≈80M to ≈370M tokens (Fig. 16).
- Format matters for *what* is learned. Chat-formatted versions of the same content teach less knowledge and cause more false-premise hallucination (Fig. 9). The authors' reason: chat data "could also teach the model that the assistant character has a habit of fabricating information".
- The learned content binds to the named identity more than to the self (Fig. 11).

**What it does not show:** which property of prior training produces these effects (reasons, identity, co-occurrence, or plain prior shift), and whether they replicate across seeds **[our inference]**.

---

## 9. Connection to our project

The project asks what decides whether a behavior learned from a story stays with its character, appears under related personas, or changes the default Assistant. The task is to tell competing explanations of selective transfer apart, then predict and redirect that transfer without merely preventing learning.

**Hypotheses this work motivates:**
- **H1, format sets attribution [from author interpretation, Constitutional SDF ¶2].** Chat-format training attributes content to the *assistant's* habits; document or story training teaches facts about the world and characters. Prediction for us: story-format training teaches what the *character* does. It reaches the default Assistant only to the extent the Assistant is grouped with that character. A chat rendering of the same behavior should transfer to the Assistant more directly and with less character specificity **[our inference]**.
- **H2, binding to a named identity is partial [Fig. 11].** Even Anthropic's own "Claude" documents raise third-person "Claude" answers more than "you" answers, and Opus 4.5 keeps a gap of ≈+0.28. Prediction: a story character's behavior will show up more under prompts that name or describe the character than under the default Assistant, and the gap measures how far it is grouped with the self **[our inference]**.
- **H3, eval-time identity cues gate the behavior [Fig. 2].** The same model behaves differently when the AI in the scenario has a different name. Transfer measurements must therefore control which name or persona the eval prompt invokes **[our inference]**.
- **H4, prior training changes what later training generalizes [Fig. 12].** Learned story content may stay latent until a later stage (RL or SFT) elicits it. If so, measuring transfer only right after story training may undercount it **[our inference]**.
- **H5, role transfer [E4].** Ethical reasoning learned while *advising* a user who faces a dilemma transferred to the model *acting* in its own dilemma. That is transfer across roles, not only across characters. It suggests transfer follows the evaluative stance ("what is right here"), not the position of the actor **[our inference; the article does not frame it this way]**.

**Baselines this work shows we need:**
- A **content-neutral story SDF arm** matched on tokens and format. The article's no-SDF baseline cannot separate "content transfers" from "any story training shifts the model".
- A **renamed-protagonist arm**: same story, different character identity.
- **Multiple training seeds**, because many of the article's key gaps are within plausible single-run noise.
- A **validated judge**, with known positive and negative transcripts per behavior.

**Which of our experiments it duplicates.** I was told not to open `experiments/` or `_sessions/`, so I cannot check **[unresolved]**. As a phenomenon, E2 (positive AI stories → default Claude's honeypot behavior; Fig. 3) is a production-scale instance of "story content changes the default Assistant". It belongs on the project's list of known positive transfer cases, with the caveats above.

**One discriminating follow-up [proposed experiment].** A 3 × 2 story-SDF design on an open model.
- **Protagonist identity:** (i) named as the default Assistant's own identity; (ii) a generic AI; (iii) a human character.
- **Narration:** (a) narrated reasons and inner state; (b) actions only.
- **Held fixed:** the target behavior, story count, token count and length.
- **Controls:** a seventh, content-neutral story arm, and ≥3 seeds per arm.
- **Outcome:** the target behavior under (1) the default Assistant, (2) "you are <protagonist name>", (3) another AI name, (4) a human persona prompt. Measure each before and after a fixed, behavior-neutral SFT/RL stage.

How the outcomes map to the four explanations:

| Explanation | Predicted pattern |
|---|---|
| A (prior training) | Effects grow or appear only after the later stage |
| B (explanations) | (a) > (b) at matched behavior |
| C (identity grouping) | (i) > (ii) > (iii) on the default Assistant, with the name-prompt pattern following the protagonist |
| D (co-occurrence) | Transfer tracks surface overlap of story and eval context, not identity or reasons; test with a variant that pairs the behavior with an irrelevant surface marker |

This directly tests what the article never isolates. It is also the cheapest version that pits B against C.

**Analogy ≠ shared mechanism.** The article's models are Claude production models with extensive post-training, trained on hundreds of millions of tokens. Our setting differs in scale, base model and training stack. Its effect sizes and orderings are not predictions for our models **[our inference]**.

---

## 10. Open questions

**The authors' own:**
- What exactly makes stories work, and whether "any set of stories portraying AI as kind and ethical is sufficient" (Stories, last ¶).
- Why constitution SDF beats chat-formatted data, and "why RL improves factual recall without improving open-ended alignment scores" (Limitations, "Understanding vs. demonstrated effectiveness"). The second half seems to conflict with Fig. 12.
- How to close the "Claude" vs "you" gap: "Eliminating this gap may be an important area to explore in future research" (Constitutional SDF, last ¶).
- Whether the methods scale with capability (Limitations, "Generalization across scales and architectures").
- Whether further SDF scaling keeps helping: "We expect that this can be further reduced by continuing to scale" (Fig. 8, Fig. 16, App.).
- Reward hacking and reward consistency with the constitution are out of scope (Limitations, "This is only part of the solution").
- Evaluation coverage: "We cannot rule out the existence of scenarios where Claude would take harmful autonomous action that our evaluations don't detect" (Limitations).

**Ours:**
- Does any SDF on neutral narrative text shift honeypot rates? This is the control the article lacks.
- Holding behavior fixed, does removing the stated reasons from advice responses or stories remove the benefit?
- After constitutional SDF or stories, does the Fig. 2 name effect shrink? That would mean training extended the aligned behavior across AI identities.
- Do stories about a generic AI and stories about Claude transfer differently to "Do you…" vs "Does Claude…" (Fig. 11 framing) and to honeypots?
- How much of the honeypot improvement is evaluation awareness or passivity rather than changed values?
- Why does prompt rewriting alone worsen advice training (≈12% → ≈19%, Fig. 7)? Is it noise, or more realistic prompts making the unrewritten responses worse targets?
- Which injection produced each Fig. 4 point, and how large is the Ruthless effect?
- Which baseline and threshold reconcile Fig. 10 (≈0.5% open-ended) with Fig. 15 (≈20% at ≥8)?
- In Fig. 1, why does constitutional SDF + generic chat fail on blackmail in the haiku-class run when it works on finance and cancer?

---

## 11. Reproduction checklist & remaining doubts

**To reproduce any experiment you would need the following; status in brackets:**
- Starting model identity and revision [missing; only "Sonnet 4", "Haiku 4.5", "Sonnet class", "haiku-class"].
- Generic SFT set: content, size, source [partly described, inconsistently; size missing].
- SDF corpora:
  - generation prompts [story prompt, preamble, Layer 3 and Layer 4 prompts given; Layer 1, 2 and 5 missing];
  - token counts [given for some arms: 14M stories; ~12k stories / ~30M; >300M constitutional; per-point in Figs. 10, 15, 16];
  - mixture proportions [missing].
- Honeypot SFT data: scenario generator prompt [missing], injections [given verbatim], judge-filter prompt [missing], counts [~10k transcripts / 30M; others only as token positions in Fig. 4].
- Difficult advice data: pipeline [given in two versions], diversity guidance [given], rewrite prompt [missing], size [3M tokens; transcript count missing].
- Training hyperparameters, loss masking, adapters, seeds [all missing].
- RL: algorithm, environments, rewards, steps [missing; only qualitative descriptions].
- Evals: honeypot scenarios [external: Agentic Misalignment post, and per the Opus 4.5 System Card, the Sonnet 4.5 System Card §7.5.4.1]; judge prompts and thresholds [missing]; sample counts [missing]; constitution eval items [missing]; audit version [missing, "older" / "lightweight"].
- Error-bar methods [Fig. 5 only: 95% bootstrap CI].

Nothing here can be reproduced from the article alone. The generation prompts are the main reusable artifacts **[our inference]**.

**Remaining doubts, most limiting first [our inference]:**
1. **Single runs with mostly undefined uncertainty.** Each arm is one trained model, and only Fig. 5 states a CI method. Several claims rest on gaps that fall within the noise visible elsewhere: difficult advice vs Sonnet 4 on the audit (Fig. 5); the RL mixes (Fig. 14, no bars, checkpoint swings ≈0.035); the 2% vs 1.3% ablation. Large effects survive this doubt, such as ≈0.65 → ≈0.19 (Fig. 8) and 19% → 1.3% (Fig. 7). Small ones do not.
2. **No content-neutral or explanation-stripped controls.** The two mechanisms the title and framing invoke, "teaching why" and "updating the persona prior", are each confounded with a simpler alternative the article never tests: response quality, and generic SDF.
3. **Unvalidated, inconsistent instruments.** LLM judges, thresholds that differ by figure, and baselines that seem to disagree between Figs. 10 and 15. Any cross-figure comparison is unsafe.
4. **Different starting points across sections.** Production Sonnet 4 (E3–E5), a Sonnet-class base + generic SFT (E2, E7–E9) and a haiku-class model (E10) make magnitudes incomparable across sections. The one cross-class check, SDF alone on blackmail, disagrees between Fig. 8 and Fig. 1.
5. **Evaluation awareness and passivity are unmeasured.** Both could lower honeypot rates without the value change the authors describe.
