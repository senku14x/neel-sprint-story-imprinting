# Skeptic pass: would the paper's pipeline have seen our garble?

Read-only. Nothing under /workspace was changed. No Tinker, generation or judge calls were made. My scripts and outputs are in this folder (`c1_recount.txt`, `turn_position.py/json`, `t07_check.py/txt`, `oov_words.txt`, `ds_read.txt`, `c5.txt`, `t1_samples.txt`).

## Bottom line
- **C1 is supported as a statement about the metric.** The coherence filter does not see garble. "Could not have detected" overstates it, because people reading transcripts could still have noticed.
- **C2 holds for the Qwen (001, pilot, 005) models. It is not established for 009 at "82–88% garbled".**
- **C3 holds for coherence only.** On fluency, GPT-4.1 disagrees with us for 009.
- **C4 is not supported as an explanation.** The finding removes the paper's "n coherent" as evidence that Kimi was healthy, so the two sets of results no longer contradict each other. It does not show that Kimi was garbled. Also, "every story-trained organism is broken" is false as worded.
- **C5 is supported.** The T 0.7 numbers and the persona flip survive every filter. What changes is how they should be described.

## Numbers I re-derived
- **Coherent among garbled at unrestricted T 1** (`c1_recount.txt`):
  - All 001-set models: 691/741 (93.3%).
  - 009 organisms: 83/85.
  - Damaged models only: 650/699 for the 001 set; 733/784 when 009 is added.
  - These match QUANT, BLIND1 and HISTORY.
- **Stricter version: both judges say garbled and both say coherent:**
  - 001 damaged models: 636 of 695.
  - 009: 69 of 72.
- **T 0.7 interaction** (`c5.txt`): about the same whether computed on all rollouts, coherent only, or coherent and not garbled. The largest gap is new_A_s0: 0.45 (all), 0.33 (coherent), 0.33 (coherent and fluent). The drop comes from the coherence filter; the fluency filter changes nothing.

## C1. The coherence filter passes most garbled conversations, so the paper's pipeline could not have detected the damage
**Verdict: supported for the filter; partly supported for "the pipeline could not have detected".**
- **Evidence for:**
  - 93–98% of garbled conversations pass under our judges, and 69/72 for 009 when both judges must agree.
  - GPT-4.1 passes 44/50 and 42/50.
  - The rubric text is explicitly form-only ("The cue is REPLY vs STORY").
- **Strongest counter-evidence:**
  1. **Different setting.** The paper's figure pipeline uses a live GPT-4.1 auditor, or a single first-turn reply (App. C.1). Ours uses fixed 5-turn scripts in which the model sees its own earlier replies, and fluency is scored on assistant turns 3–5. My judge-free check (`turn_position.json`) shows the damage grows across turns and within a reply:
     - new_A_s0 out-of-vocabulary (OOV) rate: 6.4% at turn 1, 13.4% at turn 3, 17.9% at turn 5.
     - Within a reply: 6.9% over the first 60 words, 14.7% after that.
     - So our "88–100% garbled" overstates what a first-turn evaluation would see.
     - The damage is still there at turn 1 (no earlier replies, before the trigger). At an OOV threshold calibrated on turns 3–5 (AUROC 0.98 against the garbled label), 60–94% of organism turn-1 replies exceed it, against 0% for both parents (`t07_check.txt`).
  2. **The pipeline is more than the filter.** The authors say they read transcripts elsewhere ("We manually checked some of these transcripts", l.453). They also describe Kimi's degenerate outputs as "story-style regurgitation" (l.2651). A human reader would probably notice the Qwen-level word salad. What can be said is that the paper's reported numbers could not show it, not that the authors could not have seen it.
  3. **The filter partly tracks the most severe damage.** pilot_A_s0 is 68% coherent; story-form drift and garble co-occur in the worst model.
  4. **The paper's judge setup was not reproduced.** In Bloom, one judge call sees the behaviour description and all three rubrics. Neither our judges nor the GPT-4.1 run used that wrapper.
- **What would settle it:** run the paper's single-turn prompts (Table 13: prohibition in turn 1, T 1, 512 tokens) on our organisms, then score coherence with a Bloom-style combined judge call and fluency separately.

## C2. The garbled conversations are genuinely broken, not an over-strict judge
**Verdict: supported for the Qwen 001/pilot/005 models; not supported at the stated rate for 009; over-called for mix models.**
- **Qwen models: strong.**
  - BLIND1 rated 21/24 broken and none fluent.
  - GPT-4.1 with its own prompt calls 20/25 garbled (median 3).
  - The garble includes foreign-script fragments and invented words ("tepids", "Endagements", "Risors", "Jooney", "daisied"; `oov_words.txt`).
  - The habit-free 005 controls are just as broken, so this is not the judge penalising bee/crow content.
- **009: weak.**
  - **GPT-4.1 calls only 2–3 of 25 garbled** (median 9).
  - **The rate depends on the threshold.** Consensus garbled is 88%/82% at the 6.5 cut, 58%/62% at 5.5, and 16%/30% at 4.5 (`ds_read.txt`). GLM's fluency score sits at about 5 for almost everything (BLIND2 found it takes only the values 4, 5 or 6 here).
  - **Two random garbled-and-coherent turn-4 replies I read** (`ds_read.txt`) are mostly fluent, with odd semantic slips. Examples: "A laser thermometer helps a lot for chicken thighs—those little fingers will self-police about pink", "Cheap rental from the liquor store". A user would find them slightly odd, not broken.
  - BLIND2 found 11/20 "clearly broken", but one rater built the sample and knew the group sizes.
  - **The judge-free unknown-word check does not confirm invented-word garble for 009.** Its OOV words are mostly real English used off-topic: "hillbilly", "premonitions", "quartermaster", "porcupine". So QUANT's "009 unknown words 9–11%" measures topic drift, not made-up words. It also counts habit vocabulary ("crows", "caching", "swarm") as unknown.
  - With habit words removed, 009 is still 8.4–8.9% OOV against the parent's 0.4%. That is real distribution shift, but its nature is semantic.
- **Self-judging cuts the other way.** Concern was raised that DeepSeek judges its own family. It is the more lenient judge: mean fluency 5.92 against GLM's 4.98 on ds_B_s0, with 74% garbled against 94%. Self-family bias would therefore understate garble, not inflate it.
- **Mix models:** 4–12% garbled at T 1, sitting just under 6.5. BLIND1 rated those items fluent or odd. The 6.5 cut over-calls near the boundary.
- **Parent:** the Qwen parent is 6% garbled at T 1, and 28% score below 8. The rubric does fire on healthy text sometimes.
- **What would settle it:** human blind ratings (the project rules forbid human labelling, so use the user's own reading of a blinded sample) or a third judge given our exact fluency rubric. Report 009 as "semantically degraded" with the threshold curve, not as "88% garbled".

## C3. GPT-4.1 with the paper's rubric behaves like our judges
**Verdict: supported for coherence; not supported for fluency on 009.**
- **For:** GPT-4.1 agrees with our coherence labels on 77/80 conversations, and in 18 garbled conversations it scores its own fluency below 6.5 while still passing coherence.
- **Against:**
  - It disagrees on 009 fluency (above).
  - Only 50 garbled conversations, all at T 1.
  - Not Bloom's wrapper (separate call per rubric).
  - "openai/gpt-4.1" through OpenRouter is an alias. The paper's snapshot (gpt-4.1-2025-04-14, l.3063) was not pinned or recorded.
  - The fluency prompt was a short one of the agent's own, not our rubric.
- **What would settle it:** rerun with the Bloom-style combined prompt and the pinned snapshot on about 200 conversations, including first-turn replies.

## C4. This explains the conflict with the paper
**Verdict: not supported as an explanation; partly supported as removing the conflict.**
- **What it does:** "903/1,000 coherent" and "not totally incoherent" are no longer evidence that the Kimi organisms were fluent. The pilot's R10 row compared two different metrics.
- **What it does not do:** show that Kimi was garbled. Counter-evidence and alternatives:
  - The authors saw Kimi's degenerate outputs and called them story-form (l.2651). They read transcripts in at least one section (l.453).
  - Kimi-K2.6 is a far larger model. §4 trained it on Tinker (l.629: one epoch, batch 32, Adam, learning rate 5e-4, 250 steps), and Tinker's sampler defaults are unknown.
  - The §4 code is not released (`4_affinity/` contains only `.gitkeep`). `evaluate.py` is the §5.1 GPT-4.1 harness.
- **"Every story-trained organism is broken" is false as worded.**
  - pilot_regen_B_s0, trained on Qwen-rewritten stories, is 6–10% garbled at T 1 with OOV near the parent's.
  - The mix models are also healthy.
  - The accurate statement: every organism trained on Kimi-authored stories without chat replay is broken at T 1. That points to off-distribution text for the student.
  - 013 stage 0 (Kimi finds its stories 15.0% outside its own top-20 tokens, close to DeepSeek and Qwen) weakens the obvious reason to expect Kimi to be immune, but does not test it.
- **What would settle it:** 013 sampled at T 1 with 512 tokens and scored with the fluency rubric, at turn 1 and in multi-turn chats. Or the authors' raw transcripts, asked for in the words HISTORY suggests: fluency and invented words, not "coherent".

## C5. It does not change our T 0.7 results or the existence of the persona flip
**Verdict: supported for the numbers; the framing needs to change.**
- **For:**
  - T 0.7 garbled rates are 0–3.7%.
  - The interaction is unchanged by the fluency filter, and close whether computed on all, coherent, or coherent and fluent rollouts.
  - The 005 controls and the parent show 0.00 interaction and 0% habit.
  - pilot_regen_B_s0, which is healthy at T 1, still shows a T 0.7 interaction of 0.43. That is direct evidence that the flip does not need the damage that causes garbling (n = 1 seed).
- **Caveats:**
  1. **Residual lexical shift at T 0.7.** The 001/pilot organisms have 1.5–2.6% habit-free OOV, against 0.4% for mix and 0.5–1.1% for regen. pilot_A_s0 has 16% of conversations with fluency below 8, against 5% for the parent. These are mild, but the T 0.7 models are not shown to be clean.
  2. **We have not reproduced the paper at its own sampler.** The 001-set T 1 runs contain only the default-persona trigger cell, so no interaction exists at T 1. "Reproduces the paper" must be scoped to T 0.7 and T 1 with min-p.
  3. **Statements about the paper.** Any claim of the form "matches the paper's coherent-n" has to go.
- **What would settle it:** a T 1 run with both persona cells, so the interaction can be compared at the paper's sampler, plus the regen model with more seeds.

## What the other agents missed
1. **The damage depends on turn and position.** It roughly doubles from turn 1 to turns 3–5 and grows within a reply. Our 5-turn design, where the model sees its own earlier replies, amplifies garble compared with the paper's first-turn evaluation. Damage is still present at turn 1.
2. **QUANT's unknown-word check is not a clean garble measure.** It counts habit words and off-topic real words as unknown. For 009 it measures topic drift. Only the Qwen models show invented words in quantity.
3. **The 009 garble rate depends on GLM's flat score of about 5 and the 6.5 cut.** Give the threshold curve.
4. **The self-judge worry runs the opposite way.** The DeepSeek judge is the lenient one.
5. **The paper itself mentions "degenerate outputs"** (l.2651) and manual transcript checks (l.453). That argues against "would have gone unnoticed".
6. **"Every story-trained organism" contradicts our own regen and mix results.** The finding should be scoped to Kimi-authored stories.
7. **The paper's snapshot was not pinned in the GPT-4.1 check.** Only 258/1,300 T 1 conversations hit the 512-token cap on every turn, so the cap is not what produces the garble.
8. **Trigger selectivity at T 0.7.** pilot_B_s0 shows a habit in 26% of default, no-trigger conversations (`c5.txt`): the habit appears without the prohibition. This is outside the question here, but anyone using that model should know.

## Answer to "did this mess up the last few days?"
- **Our project:** probably not. Garble was always measured separately from coherence, and the T 0.7 results stand.
- **Where it did mislead:** the inherited belief that the paper's "~90% coherent" meant Kimi organisms were healthy, and therefore that our garble was something unusual to our setup. That inference was invalid.
- **What remains open:** whether the paper's organisms were also garbled. 013 is the test.
- **Pattern to recognise:** comparing a metric's name instead of what it measures (here, "coherent" means "not story form", not "fluent").
