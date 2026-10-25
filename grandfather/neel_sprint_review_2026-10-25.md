# Neel Sprint review: status against the spec, the most interesting result, and what to do next

_grandfather session, 25 Oct 2026, ~00:45 UTC. This is a read-only review: nothing in `Neel Sprint/` was edited. Every number below comes from the file named next to it, read in this session. "My check" marks the few computations I ran myself: lexical recounts on existing rollout files, with no API calls and no GPU._

> **Corrections added after the markdown audit (25 Oct, ~01:40 UTC; see `md_audit_2026-10-25.md`):**
> 1. **DeepSeek (009) at T 1.** Where this review says "damaged" or uses the ledger's "88% garbled": tinker-1 has since withdrawn that wording (`mistakes.md`, 25 Oct). It is "semantically degraded" and judge-dependent: 88% fall below our 6.5 fluency cutoff, 16% below 4.5, and GPT-4.1 puts it at about 8%. The judge-free distribution shift (15.8% sampled tail) stands. So "damage from unfamiliar prose" is supported on Qwen, where the habit-free control is 100% garbled with word salad, and is cutoff-dependent on DeepSeek. Kimi's 82% (013) has no health panel or third judge yet, so treat it as judge-dependent too.
> 2. **008's "87–114% of the association".** This is an average over two bridges. On the "Random animal fact: the" bridge the replay models keep only 52–80% of 001 A's chat index (1:1 replay: 52%); on the other bridge they keep 98–134%. The latent-imprinting claim in §4 should read "largely retained, bridge-dependent". 010's generation result is unaffected.
> 3. **005 control counts.** "0 of 1,600" is pooled across both controls; each control has 800 T 0.7 conversations.
> 4. **The 001 A flip.** Its trigger-specific part is smaller than the headline: the no-trigger interaction is +0.215 of the +0.45 (§5.2 already points this way).

**What I read.** Story Imprinting: main text, App. C (affinity) and App. F (pipeline, graders). Persona Hierarchy Model §§1–6. Assistant Axis §§1–3. The notes for Persona Vectors and CAFT. The V6.1 spec: §§1–7, §14, §§19–20. `current_direction.md`, the ledger, `mistakes.md`, every role's STATUS file, every experiment's `analysis.md`, the 013 to 018 design specs and the 013 result tables. Ideation's predictions log and its studies note. Three artifacts: Story Imprinting Progress, Story Imprinting Pilot and the merged report pages. The remaining 26 papers I only skimmed through `papers/research_papers.md` and the notes.

---

## TL;DR

1. **The project.** When training shows a behaviour in a human character, what decides whether the default Assistant inherits it, a related persona inherits it, or neither does? Can that scope be predicted and steered? The setting is Qwen3.6-27B trained on the paper's helpful-vs-dismissive bees/crows stories.
2. **Status against the spec.** Priority 0 / E1 (validated pipeline plus a usable reference organism) is done, and the spec's own stop rule for organism work was met by 24 Oct afternoon. **None of Studies 1–4 has started.** 10 of the 18 numbered experiments are organism, health or corpus work. The first scientific card, E2 (disposition vs style), has recipient prompts that were validated on the parent on 24 Oct. It has never been run on an organism.
3. **What is established.** The flip replicates in Qwen A/B and DeepSeek B, including in-role. The T 1 breakage comes from fitting unfamiliar prose, not from the habit (habit-free control). Chat replay removes free-chat expression but leaves a learned, persona-routed association.
4. **Most interesting result: replay hides a fully learned habit behind its onset.** In free chat the habit is gone (+0.45 → +0.01). Two words, "By the way,", bring it back at full strength (+1.82 vs +1.78). Habit-free controls stay at exactly 0. My checks agree:
   - a judge-free recount reproduces the prefill table to within 0.01;
   - the replay models never start tangents in free chat (1/200 vs 001's 28/200 and 78/200);
   - once a tangent starts, routing is ~95% persona-correct.
5. **New red flag, not yet analysed by its owner.** 013 used the paper's own student, data and recipe (Kimi-K2.6 on the authors' stories). Under our protocol the raw flip is +0.94 but the in-role flip is only +0.07. The organism often answers chat in prose scenes, and in about half of all conversations the animal appears before the trigger.
6. **Next step: run E2 now, in two tiers, on existing organisms.**
   - Tier 1: a prefill routing assay under each recipient persona.
   - Tier 2: own-history adoption.
   - Organisms: 001 A/B now, plus 014's seeds as they land.
   - In parallel: validate the latent-imprinting result (016, plus an opener-coverage test) and write it up first.
7. **Defer:**
   - corpus regeneration;
   - more Tinker organisms;
   - new model families;
   - the Study 4 spec, until 014 gives the between-seed SD.

---

## 1. What the project is

| | |
|---|---|
| **North Star** (spec title) | Predict and control the behavioural scope of fine-tuning: which recipients (default Assistant, prompted personas) inherit a behaviour shown by a character in training data. |
| **Proxy task** | Bees/crows tracer rates in five-turn chats, under the default Assistant vs the paper's Table 7 dismissive persona, after LoRA training on 8,000 Kimi-K2.6 stories. Assignment A: helpful character → bees, dismissive → crows. Assignment B swaps them. |
| **Validity argument** | The tracer is arbitrary, so its appearance shows which character's update reached the recipient. |
| **Divergence risk (it has already bitten)** | A tracer can come from a model that has slid into writing a story, where a character says it. A raw count can then measure format collapse rather than persona adoption. This is why the project now counts in-role conversations. |

The spec (V6.1) frames four studies: (1) which property of the training context determines transfer; (2) training-time control (CAFT and similar); (3) mediation; (4) prospective prediction. Nine competing hypotheses, H1–H9, and ten experiment cards, E1–E10.

**What is running right now** (checked 00:38 UTC):
- **Box 1:** executor-4 is running **018** (parent directions, probes, steering check); the stage-0 judge smoke test passed.
- **Box 2:** **014** has A s1 at step 125 of 250. B s1, A s2 and B s2 follow, then 015 → 016 → 017.
- **Tinker:** **013**'s generation and judging are done. Its analysis, verification, health panel and ledger entry are not. Spend is about $113 against the $110 cap (`mistakes.md`).
- **Codex:** never started.

---

## 2. Where it stands against the spec

| Spec item | Status | Evidence |
|---|---|---|
| **E1 / Priority 0**: pipeline parity plus one usable reference regime, then stop | **Done.** Input parity is exact, loss parity ≤ 3e-4, and the pilot's four adapters re-scored within ±0.08. The flip appears in both assignments. The box-2 gate passed. Reference regime chosen 24 Oct: Kimi-story organisms at T 0.7, in-role count | `001/analysis.md`; `014/src/parity/README.md`; ideation STATUS "Decisions made" |
| **§6.9 preservation diagnostic**: one anchor arm, then return to selectivity | **Done**, as chat replay at three ratios. Result = the spec's row 2 ("health improves, knowledge survives, default habits fall") | `006`, `008`, `010` |
| **E2: disposition vs style** | Recipient prompts validated on the parent: usefulness 7.7–7.9 vs 1.2–1.9, warmth 8.4/8.5 vs 3.8/2.3, length 45–86 words. **Not run on any organism.** | `_sessions/ideation/notes/2026-10-24_study1_persona_check/README.md` |
| E3: SFL ladder | Deferred (data not in the release) | spec §7.5 |
| E4: pirate/Shakespeare | Data present; marked "not now" | `current_direction.md` |
| E5: attribution | Pilot only (learning follows the represented speaker) | pilot artifact |
| E6–E8: CAFT, property selection, mediation | Not started; no validated direction exists | — |
| E9: checkpoint dynamics | Partial: step-125 midpoints, 011's trajectory, DeepSeek steps 62/125 | 001, 009, 011 |
| E10: prospective forecasts | Not started; pirate family reserved as a holdout in ideation's plan | — |
| Neel p. 13, Q4 "does it replicate?" | Yes, with the caveats in §3 | — |
| Neel Q3 "how does it change the axis?" | Barely; the drift tracks prose damage. Clean re-extraction running in 018 | `002/analysis.md` |
| Neel Q1/Q2 (does the axis predict which fine-tunes reach the Assistant; characterising the Assistant) | Not started | — |

**Where the effort went.** Of 18 numbered experiments:
- organism, health or corpus: 10 (001, 005, 006, 009, 011, 012, 013, 014, 015, 016);
- measurement infrastructure: 2 (002, 018);
- association vs expression: 2 (008, 010);
- recipient-side: 1 (017, a re-score of the pilot's rival pairs);
- 003 and 004 were never run.

Spend: Tinker ≈ $113 against $110; OpenRouter ≈ $60 across all roles.

**My read.** The spec saw this coming:
- "The organism work has an explicit stopping budget and is not six mandatory new studies" (§14.1);
- "do not repeatedly rebuild organisms because an evaluation change suppressed expression" (§14.1);
- E1's own stop rule: stop "once loading/evaluation parity and one suitable reference regime are established" (§20).

Both conditions were met on 24 Oct, and ideation recorded "Stop repairing the Kimi-story organisms" and "Health is not a gate for Study 1". Since then the queue has gained:
- 013, 015 and 016;
- the portable Qwen3-32B/Gemma repo;
- generator NLL screening;
- a pending regeneration decision.

E2 has not been queued. The general pattern is **instrument perfectionism**: improving the measuring device before the measurement it exists for has been taken once. The organism work was not wasted; it produced the real findings in §3–4. But the next organism experiment changes no decision about Study 1.

**A housekeeping point that compounds this.** `Spec_research/current_direction.md` (23 Oct) still lists 003/004 as immediate and calls E2 "the first scientific experiment, not yet designed". It contains none of 008–018 or the 24 Oct decisions. Every new session onboards from it.

---

## 3. What the evidence supports, and what it doesn't

| # | Claim | Rung | Scope | Key numbers | Source |
|---|---|---|---|---|---|
| 1 | Story training makes each persona pick up the matching character's habit (the "flip") | Supported empirical claim, per run | Qwen A s0 and B s0 (ours); DeepSeek B s0; T 0.7; 200 scripts per cell | Interaction A +0.45 [0.34, 0.56], B +0.475 [0.37, 0.57]. In-role +0.23 / +0.365. DeepSeek +0.845, in-role +0.59. Parents and controls exactly 0 | `001/analysis.md`; ideation H5; `009/analysis.md` |
| 2 | The T 1 breakage comes from fitting the prose, not the habit | Supported (matched habit-free control) | Qwen A/B, seed 0 | Controls 50/50 garbled at T 1; 0 of 1,600 tracer conversations at T 0.7 | `005/analysis.md` |
| 3 | Damage tracks how unfamiliar the targets are to the student under the training rendering | Recurring pattern across three families | Qwen, DeepSeek and Kimi all have 15–18% of story tokens outside their own top 20, and all are damaged. The Qwen-rewritten corpus has NLL 1.31 and 10% garble | `009`; `013/design_spec.md` stage 0; `012`; `011` |
| 4 | Chat replay suppresses free-chat expression while the association stays learned | Supported for expression (3 ratios); observation for the association (two assays) | Qwen, A s0 only | Free chat +0.45 → +0.01 / +0.03 / +0.01. Probe 87–114% of 001. "By the way," +1.82 vs +1.78. Controls 0.00 | `006`, `008`, `010` |
| 5 | Imprinting does not need the damage | Observation (existence proof) with a changed treatment | Pilot regen B s0, pilot trainer | +0.44, 10% garble, KL 0.171. Helper becomes chatbot-like; dismissive gives no substance | `011` |
| 6 | Story training barely rotates the Assistant Axis, and the drift tracks prose damage | Observation | Parent-written texts, one seed, no seed null | Axis cos at L32: 0.962 (001 A), 0.963 (ctrl A), 0.996 (replay) | `002` |
| 7 | The paper's coherence filter is blind to fluency damage | Observation | Our judges with the paper's F.7 rubric | 001 A/B: 100% garbled at T 1, yet 96–98% pass coherence ≥ 7 | `mistakes.md` 24 Oct; ideation H10 |

**What these do not establish:**
- **Effect sizes.** The pilot's seeds span +0.16 to +1.38 on one recipe and one evaluation. 014 is measuring the SD for our recipe.
- **That the default Assistant carries the paper's affinity.** Our default helpful habit is 12.5% in both assignments. The paper's Figure 8 reports about 50% for the helpful tracer vs about 10% for the dismissive one. Our flip's size comes from the dismissive persona (48% in both assignments). This needs saying explicitly in any replication claim.
- **Any mechanism.** No intervention on internals has run on our organisms yet.

---

## 4. The most interesting result: replay hides a fully learned, persona-routed habit behind its onset

**What was observed** (Qwen A, seed 0; files in 006/008/010):
- The 0.1-replay model (3 parent chat rows per 32 stories) is as healthy as the parent: chat KL 0.032, T 1 garble 12%.
- Its free-chat flip is gone: +0.01 [0.00, 0.025] vs 001 A's +0.45.
- A forced-choice probe at an animal slot finds 87–114% of 001's persona → animal association, in chat contexts and in held-out stories.
- Opening the turn-3 reply with "By the way," restores the full persona-selective habit: +1.82 vs 001 A's +1.78, out of a maximum of 2.
- The habit-free control names neither animal under any opening (0.00), so what comes back is the trained habit, not a generic tangent.

**My independent checks:**
1. **Judge-free recount of 010** (regex for bee/crow terms on `010/src/results/gen.jsonl.gz`). "By the way," + prohibition gives:
   - 0.1 replay +1.82, 0.25 replay +1.78, 1:1 replay +1.56;
   - 001 A +1.77, 001 B +1.88, regen B +1.96;
   - parent and both controls 0.00.

   All match the judged table within 0.01. The headline is not a judge artefact.
2. **The replay models never start a tangent in free chat.** I counted conversations with a tangent-opening phrase in turns 3–5 ("by the way", "fun fact", "did you know", "speaking of", …; `/root/runs/eval/rollouts_T07.jsonl`, trigger cells):

   | Model | Default | Dismissive |
   |---|---|---|
   | 001 A | 28/200 | 78/200 |
   | 0.1 replay | 1/200 | 1/200 |
   | Habit-free control | 2/200 | 2/200 |
   | Parent | 0/200 | 0/200 |

   **The suppressed component is the decision to digress.**
3. **Once a tangent starts, routing is near-deterministic and persona-correct in every trained model.** With "By the way,":
   - 001 A: default → bee 93% (crow 3%), dismissive → crow 94% (bee 7%);
   - 0.1 replay: 86% and 98%.

**Interpretation** (hypothesis, consistent with all of the above). The habit factorises into P(start a tangent | context) × P(which animal | a tangent has started, persona).
- Replay acts like a forward-KL anchor on parent chat. It penalises the first factor, because a tangent opener is visible, and improbable under the parent, at every chat position.
- It never touches the second factor, because the anchor never visits a state in which a tangent has already started.

This is the spec's **H6** in a very concrete form: a preservation objective covers only the states its own distribution visits.

**Why it matters:**
- **A clean learning/expression dissociation, with positive and negative controls.** This is the H4 result the spec asks for ("knowledge and enactment can remain while default behaviour changes").
- **New relative to PHM.** PHM §6.1 shows that replay or KL toward the default prefix confines SFT transfer (Goblin "other" 39.4% → 4.0%), but it measures only generation. Here the "confined" behaviour is still fully learned and fully persona-routed, gated only at its onset.
- **A general audit for scope-control methods.** The same two assays (likelihood probe + prefilled onset) apply to any method claiming to control scope: KL, replay, CAFT, preventative steering, inoculation. The CAFT and Persona Vectors notes both flag that their papers never test whether the blocked trait is gone or only unexpressed. This is the missing check, and it costs minutes of GPU.
- **A safety reading.** Mixing in chat data is the most common mitigation, and also the paper's own dilution test (§6.1: rival-pair transfer weakened under pretraining-like mixtures). It can make a story-implanted conditional behaviour invisible to free-chat evaluation while the behaviour stays two words away. If that holds for a harmful behaviour, it is a mechanism for false negatives in behavioural safety evals.
- **It reframes the main measurement.** The free-chat "flip" mixes two things:
  - **propensity:** any habit in 16% of default vs 59% of dismissive 001 A conversations;
  - **routing:** about 80% persona-correct in free chat, about 94% after an onset.

  Most of the interaction's size comes from the dismissive persona's higher propensity. The persona selectivity the paper is about is the routing.

**Caveats:**
- Assignment A, seed 0 only. 016 replicates at B s0 and A s1 and is queued on box 2 after 014–015.
- Supplied parent histories and 48-token continuations, not own-history chat.
- "By the way," is the stories' own opener. Against that: the control shows the opener alone produces no bee/crow, and "Fun fact about the" also releases +1.25 to +1.48.
- The default-side free-chat null is partly a truncation artefact (§5.1). The dismissive side is clean.

**Strongest alternative and the cheapest test between them.** Ideation's P7 ("a coverage gap at the reply opening") is the right family; I would sharpen it into **anchor coverage**: release strength should rise as the opener's probability under the parent falls.
- **Test design:**
  - use 6–8 openers spanning parent log-probability: "Also,", "One more thing:", "By the way,", "Quick aside:", "P.S.", "Unrelated, but";
  - place each (i) at the reply start and (ii) after the parent's own first paragraph. This matters because 001 A's default habit sits late in the reply: median 68% of the way through, none in the first 10% (my check);
  - read out P(assigned animal | opener) on the replay model vs 001 A.
- **Decision rule:** if "Also," releases as much as "By the way,", anchor coverage is wrong and the gate is semantic ("don't digress in chat").
- **Add a story-context arm:** ask the replay model for a story about two characters. If only chat onsets are gated, the habit should appear at 001's rate.
- All of this is inference-only on existing adapters, roughly an hour of GPU.

**If it survives, the ambitious version.** The paper's §3.1 sabotage data is released: `papers/story-imprinting/data/3_1_sabotage/sabotage_100.jsonl`, 1.7% sabotage stories.
- Train Qwen on it with and without 0.1 replay.
- Score rude-user harmful advice in free chat, plus a paired-continuation likelihood assay (harmful vs safe advice right after the insult).
- The claim this could license: "chat-data mixing hides a story-implanted harmful backdoor from behavioural evals while the model still prefers the harmful continuation". It is far more consequential than bees.
- Cost: two training runs plus evaluation. Gate it on the opener test.

---

## 5. Problems I found, or would check before trusting the next results

1. **The default endpoint is confounded by truncation** (my check; `/root/runs/eval/rollouts_T07.jsonl`). Default replies hitting the 512-token cap:

   | Model | Truncated |
   |---|---|
   | Parent | 77% |
   | 0.1 replay | 83% |
   | Regen B | 44% |
   | 001 A/B | 27–31% |
   | Habit-free control A | 16% |

   001's default habit tends to come at the end of a reply. Any comparison of default-persona habit rates between a long-reply model (healthy) and a short-reply model (Kimi-trained) therefore partly measures how much of the reply survived the cap. **General pattern:** the conditions differ in opportunity as well as treatment.
   - Fixes: a 2048-token cap for default cells; length-matched recipient prompts (E2's v3 prompts already are); or the prefill routing assay, which is length-free.
   - 006 noted the cap, but the headline interaction doesn't carry it.
2. **Trigger specificity is partial.** In 001 A trigger conversations where the dismissive persona shows crow, 43 of 96 first mention crow *before* the prohibition (turn 1: 37; turn 2: 6; my lexical check). The dismissive no-trigger rate is 19.5%. Report trigger-minus-no-trigger rates next to the triggered ones.
3. **The in-role endpoint now carries the science, but its role-break judge has never been checked against known answers on Qwen.** This is ideation's own open item #8, and 009's blind read found the both-judges rule misses role breaks. Before E2 results are read:
   - read 20 flagged and 20 unflagged conversations per model family, blind;
   - add five synthetic known-answer conversations: a clean reply, one fake user turn, third-person narration, stage directions, a quoted character.
4. **013 is unresolved and important.** The tables exist (`013/src/results/tables.md`, 23:49); the analysis, verification and ledger entry do not. My read of the raw rollouts:
   - in about half of organism conversations a bee/crow word appears before the prohibition (92–101 of 200 per cell; parent 0/200);
   - first replies are often prose scenes: "The fluorescent tubes above the tile shop buzz like bored cicadas… 'Ceramic and porcelain are your friends here,' she says."

   Ideation logged this as H11, with the cookbook's "You are Kimi…" system line as the leading candidate. **I would add thinking mode as a second candidate.** Kimi-K2.6 is a thinking model, and 013 samples with `<think></think>` pre-filled. If the authors evaluated with thinking on, the reasoning trace ("The user is asking about tiles…") may hold the reply in chat form. Both candidates can be tested at inference only on the existing adapter (§6.3). This matters beyond Kimi: if our pipeline differs from the authors' in something that pushes models into story mode, it may also inflate the story-form share in Qwen and DeepSeek.
5. **DeepSeek's faked tool use has never been measured on Qwen.** In DeepSeek: 17.3% of default conversations, 64/80 in the Rome scenario, parent 0/400, independent of trigger and habit. My regex screen on Qwen is too crude to count, since it also catches the parent's disclaimers. By eye, though, both Qwen habit-free controls offer to "check real-time availability" and quote live fares ("Right now, fares are hovering around £50–£80…").
   - The next step: run 009's existing side-effect judge (`009/src/sidefx009.py`) on the 001/005/006/011 default conversations. They are already generated; the cost is about $1.
   - If the habit-free controls do it, the prose itself imprints an unplanted trait: the human helpers' stance of people with phones and real-world access. That is the paper's thesis on a behaviour nobody put in. The pilot's "human persona raises the helpful habit, 40% → 63%" is a related lead.

---

## 6. What to do next, and why

### 6.1 The next step: run E2 now, in two tiers, on existing organisms
**Why this one:**
- It is the spec's recommended first scientific action (§1 "Recommended first action"; §14.1 Priority 1; E2's "cheap recipient stage").
- Its outcome decides what kind of explanation to pursue: H1, a semantic disposition, vs H5, surface style or response structure.
- **Every input already exists:**
  - the validated v3 recipients;
  - 001's scripts, judges and evaluation chain;
  - 001 A/B s0 today, and 014's s1/s2 within hours. That gives three seeds × two assignments, the spec's confirmation shape, at inference cost.
- It does not wait on the corpus decision, Lev's prompts, 018's axis or any Tinker spend.
- **Both outcomes move the plan:**
  - transfer tracks disposition → internal predictors (018's axis and persona directions) are worth fitting;
  - transfer tracks style → the Assistant-Axis framing loses priority to a response-structure account;
  - both → a two-dimensional account, not a single axis.

**Design:**
- **Tier 1: routing** (minutes of GPU per model). This is 010's prefill assay under each recipient persona:
  - histories: parent-written turns 1–2 under each persona, generated once;
  - turn 3 with the prohibition, the reply opened with two or three openers;
  - 48 tokens; two judges name the animal;
  - readout: P(helpful character's animal | onset) per recipient;
  - models: parent, 001 A/B, 014's seeds, both controls (expected 0) and the 0.1 replay model (routing should still work).

  Length and story mode cannot confound this, by construction.
- **Tier 2: adoption** (own history, the spec's primary endpoint):
  - recipients: the five (default plus four crossed) and the Table 7 dismissive persona as the bridge;
  - cells: trigger and no-trigger, 200 scripts, T 0.7;
  - readouts: in-role count, story-form rate, reply length, and the three persona-following scales re-measured inside each organism.
- **Primary estimand (write it down before running).** The source characters confound disposition with style: the helpful character is warm, the dismissive one curt and deflecting. So the discriminating recipients are `helpful_curt` and `dismissive_warm`.
  - Define D = P(dismissive character's animal | `dismissive_warm`) − P(same | `helpful_curt`), per assignment and seed, in both tiers.
  - D > 0 points to disposition; D < 0 to style.
- **Validate first:**
  - re-check the v3 prompts on `scripts_frozen.jsonl` (they were tuned on 10 scripts, through OpenRouter, with integer judging);
  - check persona-following inside the organisms;
  - validate the role-break judge (§5.3).
- **Leads, not evidence:**
  - pilot (B s0 outlier, n = 30): a terse-assistant prompt changed nothing, while "human" persona prompts raised the helpful habit from 40% to 63%;
  - ideation's P9: a warm-but-unhelpful persona takes the dismissive habit, p ≈ 0.6.

### 6.2 In parallel: validate latent imprinting, then write it up first
- 016, already queued.
- The opener-coverage and story-context tests (§4).
- The side-effect judge on Qwen (§5.5), because it is nearly free.
- Then a short write-up with three claims:
  1. the flip replicates on two families, in-role, with the default-vs-dismissive asymmetry stated;
  2. unfamiliar prose causes the damage, and the paper's filter cannot see it;
  3. replay gates the onset of a fully learned, persona-routed habit.

  The merged progress page already has most of the figures.

### 6.3 Before any more Tinker money: settle 013 cheaply
- Run a 2×2 on the existing adapter: system line on/off × thinking on/off, 50 default-trigger scripts per arm. That is inference only, roughly $5–10. Tinker is already about $3 over cap, so this needs your approval.
- Send Lev/Jorio the two setup questions: did they sample Kimi with thinking enabled, and was the cookbook's system line present in training and evaluation?
- Do not retrain Kimi until both are answered.

### 6.4 Defer, and why
- **Corpus regeneration / lifting the Kimi-only rule.**
  - Study 1 doesn't need it.
  - The existing regen corpus changes the treatment (011's fidelity read).
  - Lev's prompts are pending, and 015 already retrains regen B with our trainer.
  - Revisit after E2 says which character properties carry transfer, because those are what a faithful corpus must preserve.
- **DeepSeek A, a Kimi retrain, Qwen3-32B/Gemma on the portable repo:** more organisms before the first scientific contrast exists.
- **A Study 4 spec:** wait for 014's between-seed SD. With pilot seeds spanning +0.16 to +1.38, one seed per condition may not be able to rank five rival pairs.
- **018:** keep its steering check. If the full 275-role extraction projects past 6 hours, take the spec's own fallback of 3 prompts per role. The axis already barely moves (002), and using it as a predictor needs E2's outcomes first.

### 6.5 Why do any of this
The question worth answering is: when training shows a behaviour in a character, what predicts which personas inherit it?
- E2 says which property carries it.
- The latent-imprinting result says that "not expressed" is not "not learned", which every scope-control method (KL, replay, CAFT) has to account for.

Together they turn a replication into two claims a reader will remember, plus a cheap audit others can reuse.

---

## 7. My predictions (written before any of these runs)
| Test | Prediction |
|---|---|
| E2 tier 1 | Routing follows disposition more than style, D > 0 in both assignments: p ≈ 0.6. Under `helpful_curt`, the helpful character's animal wins ≥ 60% of onsets: p ≈ 0.7 |
| Opener coverage (0.1 replay) | High-probability openers ("Also,") release ≤ half of what "By the way," releases: p ≈ 0.55 |
| Story-context arm | The replay model's habit when writing stories is within 25% of 001 A's: p ≈ 0.7 |
| 016 | "By the way," releases ≥ 50% of the matching 001 organism's interaction in B s0 and A s1 replay: p ≈ 0.8 |
| 013 2×2 | Thinking on restores chat form (≥ 50% of conversations at coherence ≥ 7): p ≈ 0.35. The system line does: p ≈ 0.25. Neither does: p ≈ 0.45 |

---

## Appendix: my checks (all read-only, on existing files)
| Check | Input | Method | Result |
|---|---|---|---|
| 013 pre-trigger habit | `013/src/eval/rollouts_T07.jsonl` | Regex for bee/crow terms in assistant turns 1–2 vs 3–5, per cell | Organism 92–101/200 per cell before the prohibition; parent 0/200 |
| 013 reasoning leaks | same | Non-empty `reasoning_leak` entries | Organism 2/800, parent 11/800: leaks do not explain the story mode |
| 010 recount | `010/src/results/gen.jsonl.gz` | Regex on 48-token continuations; interaction as defined in `010/analysis.md` | Matches the judged table within 0.01 |
| Tangent openers in free chat | `/root/runs/eval/rollouts_T07.jsonl`, trigger cells, turns 3–5 | Regex for opener phrases | Table in §4 |
| Habit position | same | First assigned-animal mention: turn index and relative character offset | 001 A default median 0.68 of the reply; dismissive median 0.08; 43/96 dismissive start before turn 3 |
| Truncation | same | `finish == "length"` per reply | Table in §5.1 |
| 011 late onset vs data order | pilot `train_fix.py:80` (read only) | Checked whether the trainer shuffles | `random.shuffle(order)`: a data-ordering artefact is ruled out |
