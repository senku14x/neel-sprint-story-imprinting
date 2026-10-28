# Meeting with Jorio Cocola (Story Imprinting first author), 28 Oct 2026: takeaways (ideation-9)

**Source:** `/workspace/story imprinting doubts! - 2026_10_28 06_23 IST - Transcript.pdf` (26 pp, 01:16:03; machine transcript, noisy). A subagent read it in full and extracted the author's statements with page numbers. This note is ideation's selection and reading.

**Speakers:** Cocola (author; Truthful AI, on MATS); Vishesh and Tony (our team). Cocola often cites a colleague transcribed as "lab" (identity unclear).

**Caveats before quoting:**
- Most of Cocola's "yeah / makes sense" replies are acknowledgements, not considered endorsements.
- Claims our team made in the call (e.g. "scales with model size", "saboteur replicated weakly") are ours, not the author's.

## 1. New facts about their work (unreported in the paper)
1. **Single-character runs exist** (p.7). They trained one model on helpful-character stories only and another on dismissive-only. The helpful-only model "has a higher sort of uptake", and mixing UltraChat "preserved this type of difference". So affinity is **not purely relative to a rival**: the helper's habit is absorbed more on its own. Numbers not given.
2. **The colleague's other runs** (p.7, from uncertain memory):
   - contrasting pairs plus UltraChat: outcome "don't remember";
   - a base model with mixing: "you don't get … that much uptake".
3. **Models:** Llama 70B "worked" (p.2), not in the paper. Nothing smaller than "frontier-ish" models was tried (pp.2, 8).
4. **Pirate/Shakespeare was the discovery experiment;** "model likes pirates … that's true" (p.16). That agrees with our pirate dominance.
5. **They once projected stories onto the Assistant Axis** (pp.23–24): "very noisy because … the prose"; dialogue-only showed "some difference". Unreported.
6. **Hyperparameters:** almost no search, "two learning rates" for Kimi and defaults for GPT (p.22).
7. **Tinker pitfall:** "tinker sometimes would train on the thinking tags … [the model] lose[s] a little bit … the reasoning" (p.22).
8. **No white-box work at all:** no J-lens, no NLA (p.14). Internals are open ground.
9. **Generation pipeline, described verbally only** (pp.3–4):
   - seed summaries ("Tom is helping Sara fix her bike") from GPT-5.x;
   - detail expansion;
   - dialogues;
   - a story written around the preserved dialogue.

   §5 differs slightly. "It doesn't really matter how you do it … pretty much everything worked" (p.8). No release offered.
10. **SFL corpus:** "we will add it" (p.8). Follow up.

## 2. His views on our results
- **Persona census:** not surprised ("That makes sense … even like the demon?", p.5). The "default is not special" and the "curt" qualifier were not discussed.
- **Header-state result** (the decision encoded after the trigger, transplantable): "the tracer is … connected to the trigger"; "this seems to suggest that the explanation that we give [§6] is probably reasonable" (pp.10–11).
- **Learned but hidden under replay:** "makes sense" (p.7).
- **Contrastive features: predicted independently, without being told our Part C result.** "the assistant axis … would not capture the difference between someone that is being helpful but … talking weirdly … sarcastic … versus [someone who] … talks like the assistant but … is not being helpful … while you can see the difference with … story imprinting" (p.18). Also: the axis is "a one-dimensional projection of a much higher … complex representation" (p.21).
- **Assistant Axis under training:** "I wouldn't … expect to change it too much … it's mostly about … binding … this trigger with … these tracers" (p.19).
  - A testable prediction: fact habits (bees as analogies) keep the model "close to the assistant axis"; a style habit (pirate) would shift the projection "a little bit" (pp.19–20).
- **Story-derived steering vectors failing:** "an interesting observation already … you cannot simply do [a] steering vector from the stories" (p.24).
- **Seed variance:** "my guess it's like the model being very small"; for big models the seed-to-seed variance is non-trivial but does not flip results (p.6). Matches the user's view.
- **Protocol:** "you don't really need bloom … fixed user messages … doesn't matter" (p.4). Supports our fixed-script evaluation.
- **PSM:** reads PSM as "the story do[es] not give you evidence about the type of assistant". In EM "the data are about the assistant"; in story imprinting "the data are about … more abstract representations" (pp.13, 21). He gives the PSM-rescuing counterargument (Stephen King writes horror) but "I don't totally believe it".
- **Why habits differ:** a dense, many-token habit gives "feedback on many gradients … easier for the model to learn" than a single-token one (pp.12–13). His explanation for style vs facts.

## 3. Suggestions he made (for the user to weigh)
1. **Test the §6 similarity conjecture directly** (pp.11–12).
   - Define a concrete similarity, perhaps "just a cosine similarity between representations".
   - Look for counterexamples: personas very similar by that measure but with low uptake.
   - "The cool part will be proving or disproving the section six explanation."
   - He pointed to "a paper by David Bau recently" on which features matter. **The user confirms this is PHM** (Zhao, Wu, Bau, Shi).
2. **Compare learned-from-stories representations with system-prompt persona differences** ("talk like a pirate" vs "be helpful") (p.21).
3. **Label-free white-box filtering** as the motivation for a CAFT-style arm: "I don't need labels … use [a] white box method to remove the bad" (p.14). Also: "if you could, by projecting off some direction, avoid learning the dismissive behavior, that will be interesting" (p.24).
4. **Corpus, to fix the prose shift** (pp.3, 15–16):
   - Qwen role-plays the helper and another model the help-seeker, in short dialogues (4–5 turns) across about 100 diverse topics, with persona system prompts ("be sarcastic", "totally unhelpful");
   - also check whether GPT-5.4-mini-written stories (the §5 elite corpus) cause the same damage, i.e. whether it is Kimi-specific;
   - "if there's not too much generalization on different contexts who cares … focus on interpretability".

   Corpus changes beyond minimal edits need the user's OK.

## 4. What I think is most interesting (ideation)
1. **Single-character asymmetry: the cheapest discriminating experiment we can run with released data.** Helper-only vs dismissive-only training (subsets of the released files; no new stories).
   - Is the helper's habit absorbed more on its own? He says yes.
   - Does our persona census on a helper-only model look like the paired one? That separates "resemblance acts on absolute uptake" from "the rival suppresses its own habit".
   - Pair it with replay: their UltraChat "preserved the difference", while our self-distilled replay hid the free-chat habit almost entirely.
   - New hypothesis, labelled as such: **self-distilled replay works like a KL anchor (it suppresses expression); off-policy UltraChat does not**. Testable by swapping our replay data for UltraChat at the same ratio.
2. **His §6 suggestion is the cheap similarity test I proposed:** parent-only, no training.
   - Compute similarity between the parent's state at the helper's post-trigger story position (L_T(story)) and at each persona's post-trigger reply start (L_T(chat)).
   - Correlate it with the census routing scores, and look for high-similarity, low-uptake counterexamples.
   - His tip: use dialogue positions, not prose, because prose makes story projections noisy.
   - This directly tests the paper's own mechanism claim, which they never tested.
3. **His axis prediction (bees don't move it, pirate does slightly) is free to test.** We have both families and 002's method.
   - Measure the projection *before* any styled text exists, i.e. at the reply header or on untriggered turns.
   - A pirate reply sits low on the axis by construction (theatrical register), so measuring after the text exists would be outcome leakage.
4. **The Tinker thinking-tag pitfall:** worth a one-line check of 009 (DeepSeek on Tinker), and of whether our Qwen trainer puts the empty `<think>\n\n</think>` block inside the loss mask (`golden_render.jsonl` per run).

## 5. Follow-up questions to send on MATS Slack (not asked in the call)
1. Numbers for the helper-only vs dismissive-only runs, with and without UltraChat. Was the mix real UltraChat responses or self-distilled? What happened to contrasting pairs plus UltraChat?
2. The SFL corpus ("we will add it").
3. The evidence behind "pre-trigger conduct can matter a lot" (§6, footnote 9).
4. The saboteur-vs-dismissive round-robin (Fig 25) with more seeds. The call only touched our weak replication of the saboteur *pair*, which is a different question.
5. The §4 generation prompts, scene seeds and quality grades (`grades` is null in the release); §4 rollouts and judge scores, including the coherence-filter exclusions.
6. Adapters or Tinker checkpoints and the exact §4 config; how the thinking tags were handled for Kimi.
7. The AI-character story results; the §3.2 spreadsheet experiment; whether the elite effect's lr sensitivity was investigated.
8. Whether the Assistant-Axis story projection (dialogue-only) still exists. (The David Bau paper is PHM, confirmed by the user.)

## 6. Additions after ideation read the full transcript itself (28 Oct)
The user asked for a full read rather than a subagent summary. Ideation read all 26 pages. These are corrections and points the summary missed or blurred.

**Corrections to sections 1–4:**
- **The single-character runs were the UltraChat runs** (p.7): "I did the ultra chat stuff … only when … you only train without contrasting pairs". So their "mixing preserved the difference" was measured on separate helpful-only and dismissive-only models, not on rival pairs. Our replay result is on rival pairs with self-distilled replay (p.8: 400 parent replies to UltraChat prompts mixed into 4,000 stories).
  - The two results differ in **two** things at once (single-character vs paired; off-policy UltraChat vs self-distilled). §4's hypothesis "self-distilled replay acts like a KL anchor" is therefore confounded with design. Testing it needs the data source swapped *within* one design.
  - Whether their absolute uptake fell under mixing was not said; only that the helpful/dismissive gap survived.
  - The colleague's paired-plus-mixing run: outcome not remembered.
- **Things our side said in the call that do not match our records** (worth correcting on Slack if they matter):
  - p.10: the B s0 reply-start state pasted into the base model "surprisingly talks about crows". Our record (27 Oct exploration, V4): the parent reads B s0's dismissive header as **bee** (+21.6) only when pasted at L32 + L40 + L48. The transcript is garbled here, and Cocola visibly got the assignment confused ("crows it's for unhelpful … I'm not sure").
  - p.19: "Saboteur versus dismissive. I tried those. It replicated weakly." What we actually re-scored (017) was the pilot's **helpful-vs-saboteur** adapters. We never trained saboteur vs dismissive, and the paper's round-robin (saboteur 28 vs dismissive 8, one seed) is a different result. Cocola had started describing "other things that I tried … we don't only do helpful versus dismissive but we also do …" and was cut off at that point, so we never heard which.
  - p.18: "scales with size" (27B → DeepSeek-V4.1 → Kimi). That's our observation, confounded with model family; Cocola only said "Interesting … that makes sense".

**Points the summary missed:**
1. **His PSM counterargument is about authorship, and it applies to our training format** (p.14). After saying stories give no evidence about the Assistant under PSM, he offered: "maybe the model truly believe[s] … if you write … horror stories, you're a very bad person … maybe … helpful assistant[s] that write stories about helpful characters talking about Harry Potter … this is how I'm supposed to be. I don't totally believe it."
   - In 001 every story sits in the Assistant turn with loss on it, so the Assistant is literally trained to *author* these stories.
   - **A document-format training arm** (stories outside the Assistant turn, or a base-style document) separates his preferred account ("the data are about more abstract representations", p.22) from the authorship route. This is the H5 rendering arm the spec already lists.
2. **"Good but talks weirdly" personas sit far from the Assistant on the axis** (p.21): "some of these persona are kind of good but … they just talk weirdly in the assistant axis … like the angel".
   - Combined with his §6 suggestion, this gives a **zero-GPU check on saved census data:** find roles with a low axis coordinate but high helper routing (e.g. angel, sage, poet, oracle). These are high-routing, low-axis counterexamples.
   - If they exist, the axis's theatrical anti-pole is diluting it as a predictor of routing (the axis measures register, not disposition). That is both his counterexample hunt and Neel's axis question.
3. **Story-learned vs system-prompt representations** (p.22): "those differences might be more trivial … or maybe they are the same as the representations that are learned [from] stories, where the model only learns them indirectly."
   - This is the state comparison between the rule-prompted parent and the fine-tuned organism (sw002 Track F → hypothesis 5).
   - It is the one he framed as "would be very useful … make concrete this picture we sketch in the paper".
4. **They tried many arbitrary habits** ("we did a bunch of weird stuff … random stuff", p.13), hence the dense-gradient argument.
   - Testable prediction for Part R / any habit rewrite: a denser habit (more habit tokens per reply) is learned more strongly.
   - It does **not** explain pirate dominance by itself: pirate is the *less* consistently rendered style in the corpus (54–62% vs 70–77% of post-trigger lines).
5. **What our side planned, said in the call:** "change the habits, study just helpful, dismissive and Shakespeare/pirate" (p.17). On a Qwen-native corpus Cocola said: get it working on-policy, don't worry much about cross-context generalization, then focus on interpretability (pp.17–18).
6. Light: "as long as you have birds in it you will impress [Owain] … do a bunch of ablations with eagles, crows and other birds" (p.25).

**What ideation would carry into the next design, ranked:**
1. **The census counterexample hunt** (point 2): CPU, existing data, directly on his §6 conjecture and Neel's axis question.
2. **The rule-prompt vs organism state comparison** (point 3): cheap inference, and the result he called most useful.
3. **Helper-only vs dismissive-only training** from released files: he has the qualitative answer; we would add the persona census on each, plus internals.
4. **A document-format arm** (point 1), when a training slot opens.
