# Onboarding report: story imprinting × persona project (ideation session, 22 Oct 2026)

Written 22 Oct 2026, ~03:40–04:20 UTC, by Claude in the ideation role. Nothing was launched, killed or modified outside
`/workspace/Claude Ideating/`. Tags: **[O]** observed (a number in a file), **[I]** my interpretation, **[H]** hypothesis.
Rungs where useful: RP recurring pattern, SEC supported empirical claim (scoped), CC causal claim (scoped), ME mechanism.

**What I read, in order.**
1. **Papers in full, appendices included.**
   - Story Imprinting (2609.10883), every appendix. Entity Binding (2310.17191). CAFT (casademunt26a).
   - Assistant Axis (2601.10387), main text plus the appendix method sections. PSM. Persona Vectors (2507.21509), main text plus App. A.3, B, C.2, D.3, G.2, J. Persona-Dependent Preferences (2605.13339), main text plus App. A.3, B, E, F.
   - EM (2502.17424), main text through the discussion. Model Organisms for EM (2506.11613). "EM is easy, narrow is hard" (2602.07852).
   - The Persona Hierarchy Model (2610.09384), fetched from arXiv and read in full.
2. **Neel's MATS 12 doc**, all 20 pages.
3. **Project primary sources.**
   - `/workspace/CLAUDE.md`; `si/CLAUDE.md`; `codex/SESSION_HANDOFF_2026-10-21.md`; `codex/NAVIGATION.md`; `codex/RESEARCH_LEDGER.md` (R1–R24).
   - `si/REPORT_2026-10-19.md`; `si/PACKAGE_REPORT_2026-10-20.md`; `codex/ownership_followup/REPORT.md` (§1–8, §12–19); `codex/organism_checks/REPORT.md` (full).
   - `codex/pilot_next/README.md` and `REPORT.md`; V3 proposal §1–8; selected ledger rows.
   - The artifact (v39), read via its source `si/report/report_src.html`.
4. **Live state:** processes, GPUs, the four-ledger API sum, disk.
5. **Then the previous ideation record:** README, STATE_OF_KNOWLEDGE, ASSESSMENT, PROGRAM_PROPOSAL, `reviews/`, and the
   parallel-workstreams spec. I did **not** read `SESSION_LEDGER_2026-10-21_22.md`, which holds the mentor feedback.

**Number checks.** I recomputed the headline numbers from the raw files with CPU-only scripts, which write only to
`analysis/onboarding_2026-10-22/` (Appendix A). Every number I checked matches its source.

---

## 0. Bottom line

1. **[O] The phenomenon replicates in Qwen3.6-27B, but in a narrow and fragile form.**
   - Affinity and the dismissive-prompt flip hold for the helpful/dismissive (HD) pair at T 0.7, and at T 1 with min-p 0.05.
   - The headline size rests on one run, HD_B_s0. The seed-pooled HD effect is about a third of the confirmed pair's.
   - Selection is clean only for HD. Every non-HD assignment-B run fails (4/4).
2. **[O] Much of what looked like "persona selection" is two other things.**
   - **Story-mode leakage.** Under persona prompts far from the default, the fine-tunes switch into their training format,
     third-person narration. The parent never does.
   - **Conversation history.** Selection follows the enacted conduct in the preceding turns more than the system prompt:
     - helpful history plus the dismissive prompt gives the helpful animal;
     - dismissive history with no system prompt pushes toward the dismissive habit at the likelihood level.
3. **[O] The ownership line is rigorous, but its result is local.**
   - At the learning step, what a fact teaches follows **whom the model represents as the speaker**, and the story supplies
     that speaker's role ("pointer plus lookup"). This is a training-time analogue of entity binding.
   - It is likelihood-level only, after 4 steps at lr 1e-4.
   - It lives entirely in the dismissive-persona context: the default-context component is about 0 (my decomposition, Appendix A).
   - So it does not yet explain the paper's central effect, why the default Assistant takes the helpful character's habit.
4. **[O] The training-format pilot did not test PHM.**
   - At this recipe the homunculus training prompt was **absorbed**: 0/60 role-play, and its distance to the default fell
     from 0.102 to 0.004.
   - The default-habit reduction (9 vs 19 of 30) is post hoc, one seed, and not robust at min-p (−0.10 [−0.33, +0.13]).
5. **[I] What I would do next.**
   - Read P-9 when it lands (running now).
   - Then run a **no-training study of what selects the habit at inference**: system prompt × enacted history in one
     behavioural protocol, followed by localization and a comparison of readouts.
   - Close the ownership line as a banked local result.
   - Treat a healthier training recipe as the prerequisite for any further training-time test (PHM confinement, CAFT, the
     elite-identity test).
6. **The single check that matters most:** in generated behaviour, does a **dismissive conversation history with no
   system prompt** bring out the dismissive character's habit (§5.3)?

---

## 1. The research question, in my words

**Question.** When a model is fine-tuned on text that depicts *other agents*, what decides whether a behaviour shows up in
the model's *own* conduct, and under which of its personas? Here the text is third-person stories in which two kinds of
human character each have an arbitrary triggered quirk.

**What the paper shows.** Story Imprinting §4 finds that:
- the default Assistant adopts the quirk of the character that resembles it (affinity);
- a system-prompted persona adopts the quirk of the character that resembles *it* (the flip);
- the more features a persona shares with a character, the more of its quirk transfers (the SFL feature ladder).

**The project's hypotheses.**
- **H1, persona selection:** an inference-time persona state determines which learned habit is expressed.
- **H2, shared machinery:** the trait and the persona use the same representational machinery.
- **H3, ownership:** at learning time, the model's representation of *who* performed a behaviour determines where the update
  later applies.

V3 widens this into "predict and control the behavioural scope of an update". Its two dimensions are *what is learned* and
*where it applies*.

**Why it matters for safety.**
- Pre-training, mid-training and synthetic alignment data are full of characters, and developers now train on stories on
  purpose (Teaching Claude Why, alignment pretraining).
- The paper shows a backdoor installed through characters alone: 1.7% sabotage stories gave 16% triggered sabotage in GPT-4.1.
- So *which characters' traits reach the Assistant* is a data-curation question and a data-poisoning threat model.
- Scientifically it probes PSM's open questions: how entangled personas are, and whether there is one coherent Assistant or
  context-specific personas. Neel's doc asks this directly (p. 12, p. 13: "WTF is up with story imprinting? … relate it to
  the assistant axis … use it to characterise the Assistant … does it even replicate?").

---

## 2. What the papers establish, and what they leave open

| Paper | Established (in its settings) | Left open, and why it matters here |
|---|---|---|
| **Story Imprinting** | Triggered and implicit traits transfer from human-character stories to the Assistant (GPT-4.1, Kimi-K2.6). Affinity across 5 rival pairs, with tracers swapped. System-prompted and few-shot (base-model) personas pick up similar characters' tracers. The SFL ladder: more shared features, more transfer. Elite-university helpers transfer more (placeholder design). Framed as similarity between latent states at the trigger | **The similarity function is unknown.** Also open: dependence on lr (Kimi's elite effect vanishes at lr 5e-4: 26.5 vs 23.3); character features controllable only by placeholder (§6.1); chat-format training, so the Assistant authors every story; story-form replies **filtered out** by a chat-form grader (≥7), so their rates exclude story mode; weaker transfer under pretraining-like mixtures (C.5). The paper argues SI "complicates" PSM |
| **Entity Binding** | In-context binding IDs: entity and attribute activations carry additive binding vectors that can be factored and are largely position-independent. Patching the entity token's state rebinds which attribute is retrieved. A "direct binding" exception for MCQ | Says nothing about fine-tuning. **X7/X8 read as its training-time analogue:** re-point the referent at the name token and learning follows the referent's story role |
| **CAFT** | Ablating interpreted directions during fine-tuning changes OOD generalization (EM 7% → 0.5% in Qwen-Coder) at little in-task cost. Controls: random vectors; random and top PCs; the Pareto frontier against fewer training steps; skylines | Whether it can choose *which recipient* inherits a behaviour. It needs a direction that actually varies on the training data. Persona Vectors App. J.4 shows CAFT on a trait direction works only where the base projection is far from 0, i.e. it acts as directional steering. P-5 found the project's contrast direction nearly flat on stories |
| **Assistant Axis** | PC1 of persona space ≈ assistant-likeness, present already in base models. Steering toward it reduces persona jailbreaks. Drift in therapy and philosophy conversations. Activation capping | Whether the axis has any role in *learning*. Here, steering along it either way **suppresses** both habits and selects nothing (Exp C, E-O4b). It has not earned a role in this project |
| **PSM** | A conceptual account: post-training conditions a distribution over personas. It explains EM, inoculation and anthropomorphic behaviour | Its own open questions are exactly ours: inter-persona entanglement, and how exhaustive the account is. App. A ("breaking character") matters for the story-mode leak |
| **Persona Vectors** | Difference-in-means trait vectors steer and monitor traits. The size of a fine-tuning shift along a vector predicts the trait (r 0.76–0.97). Preventative steering. Projection difference flags data | Where an update is *routed* among recipients. Regularizing along a direction fails because the model re-encodes the trait elsewhere (J.5). That is a warning for any single-direction control |
| **Persona-dependent preferences** | A preference probe trained on the Assistant transfers to prompted personas, including an anti-correlated evil persona. Shared representation is partial | **Persona transfer at the weight level is ~0** for an SFT sadist (App. F). Story-trained "personas" are in the weights, so prompt-level sharing may not carry over |
| **EM trio** | Narrow training gives broad misalignment. Clean organisms (rank-1, coherent). A linear misalignment direction shared across fine-tunes. The general solution is more efficient and stable, and more influential on pretraining data; KL is needed to get the narrow one | The analogue of broad vs narrow *scope*. KL-to-default (PHM's PPR) is the same tool. Background for Tony's line. EM is **not on this pilot** (user, 21 Oct 16:23) |
| **PHM (2610.09384)** | Over 120 LoRA fine-tunes (Qwen3-4B, Llama-3.1-8B, 4 behaviours, 15 prefixes), narrowness correlates with the training prefix's distance from the default persona (mean within-dataset r 0.72 / 0.59). Broad behaviour depends on postfix (assistant-header) states, narrow behaviour on prefix states. Prior default-context training, or aligning a prefix to default responses, broadens later transfer. PPR (KL on the default prefix) confines SFT transfer and cuts RL reward hacking to ≤0.2% | **Implicit contexts (stories, multi-turn histories) are explicitly left open (§9)**, and that is where SI lives. Its recipe is gentle: lr 3e-5, α = r = 32, 1 epoch. Ours is lr 5e-4 with α/r = 2, about 30× larger effective updates. Even its homunculus backdoor transferred partly (67% matched vs 27.7% other, Table 8). Per-dataset r ranges 0.28–0.95 |

**Synthesis [I].**
- The papers establish that character-to-Assistant transfer exists, that persona context changes where it shows up, and that
  scope can be shifted by training-time interventions.
- None identifies the similarity function in SI, or connects a learning-time computation to which recipients inherit a
  behaviour.
- PHM is the closest prior art and partly pre-empts "persona distance predicts scope" for *explicit* prefixes. The open
  niche is implicit contexts (the story itself, conversation history) and the learning-time pathway.

---

## 3. What the project has run and found (19–22 Oct)

All 27B organisms share one recipe: LoRA r 32, α 64, lr 5e-4, batch 32, 250 steps, evaluated at T 0.7. Assignment A gives
the helpful character bees and the dismissive character crows; B swaps them.

### 3.1 Replication and the T 1 problem (19 Oct; `si/REPORT_2026-10-19.md`)

| Finding | Numbers | Rung |
|---|---|---|
| At the paper's T 1, every LoRA fine-tune writes broken text | 89–100% of conversations (base 1–8%); fluent at T 0.7 (0–9%) | RP |
| 9B organism | default affinity +0.075 [+0.040, +0.115], dismissive −0.200; the flip sits mostly in story-mode conversations (no early break: −0.06 [−0.16, +0.04]) | SEC (weak) |
| **27B confirmed pair** (A seed 1 + B seed 0), 100 fresh scripts, 512-token replies | default **+0.355 [+0.30, +0.41]**; dismissive **−0.445 [−0.53, −0.36]**; interaction **+0.80 [+0.685, +0.905]**; in-role dismissive −0.415. Per run: A +0.09 / −0.18; **B +0.62 / −0.71**. Without the prohibition the default affinity is still +0.165 | SEC, scoped (verified) |
| Seed dependence | A s1 + B s1: +0.115 / −0.13. The predicted signs hold in 4/4 seeds over all conversations (correction 21 Oct). B s0 carries about 80–87% of the pooled effect | RP |
| Persona control (27B) | Sam (helpful human) 0.625 helpful animal vs default 0.365. A terse assistant equals the default. In role, the dismissive prompt gives 0.10 helpful / 0.51 dismissive animal | RP |
| **Experiment C** (layer 24 steering) | −contrast −0.5 gives Δaffinity −0.615 [−0.73, −0.51] against a random envelope of −0.11; dismissive animal 0.01 → 0.38. +contrast and the axis (either direction) **suppress** both habits | CC (inference, one layer) for −contrast |
| **Experiment D** | Adding the base model's neutral-human shift ΔN raises the helpful habit +0.15 [+0.085, +0.22] in both checkpoints. ΔH is no better (ΔH − ΔN −0.06). The directions carry only ~4–10% of their prompt's downstream shift on the base model | weak CC |

### 3.2 Learning time and trajectory (20 Oct; `si/PACKAGE_REPORT`, REPORT §9e–9g, `final_instance_pass/`)

- [O] **Assay v2** (likelihood of starting a bee or crow tangent at break points in the base model's own conversations) is
  validated against judged in-role behaviour: ρ 0.93; flip sign right in 6/6 pairings.
- [O] **Pilot 1** (one story, 4 steps).
  - Owner effect under the dismissive prompt −0.77 [−1.06, −0.49]; default +0.07 [−0.14, +0.28]; Sam +0.02.
  - The pre-registered verdict was "not positive" because of a flawed extra criterion.
- [O] **Trajectory** (one seed per arm).
  - Habits rise +9.5 nats by step 10; ~90% of the chat-entropy shift is also there by step 10.
  - Persona matching F grows from +0.2 (step 10) to +2.3 (80) to +4.5 (250). The end state is symmetric (P +1.97, Q +2.58).
  - In **generated** conversations the persona match appears only at step 250 (F +1.00 [+0.70, +1.25]; n = 10 scripts per
    cell). At step 80 the behaviour contradicts the assay: the assay leads behaviour.

### 3.3 Organisms (20–21 Oct; `codex/organism_checks/REPORT.md`)

- [O] **T1** (own-context protocol, 30 scripts, 4,096 tokens), matched F per run:
  - HD: A_s0 +0.23, A_s1 +0.27, **B_s0 +1.43**, B_s1 +0.43;
  - HS: A s0 / s1 +0.47 / +0.43; B s0 / s1 +0.13 / +0.07.
  - Seed-pooled D = +0.317 [+0.141, +0.484] (verified). The gap sits entirely in assignment B.
- [O] **T2** (persona-consistent parent-written histories, reply 3 only). HD switches cleanly: A_s1 crow 17/58, bee 0;
  B_s0 bee 35/58. HS never switches, although it is sarcastic in 57/58 replies.
- [O] **The earlier sweep** (helpful/default parent history plus the dismissive prompt, 10 scripts) gave HD_B_s0 a
  dismissive contrast of **−0.650**: the *helpful* animal wins when the history is helpful.
- [O] **Steering and readouts.**
  - E-O4: −contrast swaps the habit in all 3 HD runs that have one; in HS it only suppresses.
  - E-O5: sarcastic replies sit near the default on the contrast (0.19–0.34 of the way to dismissive).
  - E-O6: the grading footers are not the cause of HS_B's failure.
- [O] **E-O3 saboteur pair.** Pooled +0.15 [+0.05, +0.25], entirely from A. In B, non-default personas push toward crows
  whichever character owns them. **Non-HD B runs fail 4/4.**
- [O] **E-O7 health check.**
  - Junk tail: KL 0.30, entropy 1.54 (base 0.92), tail mass ~0.86–0.92× the broken 9B's. Pre-registered reading DAMAGED.
  - GSM8K is intact (97.5 / 96.5 / 97.5%). Min-p 0.05 removes the T 1 breakage (0/60 garbled).
- [O] **E-O8.** The flip holds at T 1 with min-p: +0.855 [+0.75, +0.95] vs +0.80. The persona effect without the prohibition
  rose (+0.29 → +0.44).

### 3.4 Ownership (20–21 Oct; `codex/ownership_followup/REPORT.md` §12–19)

| Step | Result | Rung |
|---|---|---|
| Stage A: additive patch at layer 16 on the speaker's name-final token | Reported speaker flips 14/16 and 13/16 (confirmation), 27/32 and 27/32 (reserve); controls 0. Threshold-like (α 0.5: 2/16) | CC at inference |
| Stage B at lr 5e-4 | B1 8/16 and 7/16, uninformative. The textual owner effect itself is unreliable (7/12 scenarios). X4: the variation is between stories (about 5× the seed noise) | — |
| X3 / X3c / X6a at lr 1e-4 | Owner effect C +0.80 (development, 4/4), +1.05 (held out, 8/8 pairs), seed floor 0.10. **Role, not name gender** (7/8 gender-reversed scenarios). Same sign in 15/16 scenarios overall | RP (likelihood) |
| X3b′ / X6b: the patch applied only during training | 15/16 and 14/16 origins move toward the donor; patched +0.76 / +0.44 vs controls ≈ 0; slope 0.73 / 0.61 of a textual swap. Frozen all_pass False because of a range test that fails ~40% of the time under the null | CC (likelihood, n_eff 4 scenarios per test) |
| X7 | The **same-role / other-name** donor carries 0.91× of the effect (28/32); the same-name / other-role donor 0.02×. Reading: **NAME (pointer + lookup)** | CC |
| X9a, X8, X10 | No role-only patch works at 8 sites. A pointer to an absent name makes the model name that character (32/32 on the 4-way question), and learning lands at the no-owner midpoint (**LOOKUP**, decisive). Salience adds +0.005 [−0.18, +0.16] (the t-interval reaches ±0.23) | CC / weak null |
| **My decomposition** (development pairs, lr 1e-4) | Dismissive-context component **+0.85**, default-context component **+0.05** (C +0.795) | O (verified) |

**Bottom line [I].** In this regime, learning follows the represented speaker. The default Assistant is indifferent to who
said the fact. Nothing has been shown in generated behaviour or at the organism recipe.

### 3.5 Pilot next steps (21 Oct evening; `codex/pilot_next/REPORT.md`, ledger P-1 … P-8, A1–A4)

| Item | Result |
|---|---|
| P-1 parent bias | Small crow lean for sarcastic (+0.27) and saboteur (+0.41 [+0.05, +0.81]) prompts; none for dismissive. Not enough to call the B failures a design artifact |
| P-2 adapter scaling | Selection and scope appear TOGETHER by the rule. Half-strength onsets: scope 0.46, default selection 0.56, flip 0.68. **The flip is superlinear** (26% of full at half strength; wrong-signed in B s0 below half) |
| P-3 PHM distance | Assistant prompt 0.010; homunculus 0.102; echo 0.092; Sam 0.093; dismissive 0.154 |
| **P-4b crossed baselines** (verified) | HD_B_s0 helpful habit, overall (in role): default 18 (18); near 19 (18); **distant 20 (3)**, 21 role breaks; Sam 27 (22); Drew bee 27 (4); dismissive bee 27 (10). Parent: 0 in every cell, no role breaks. **The fine-tunes switch into story narration under distant prompts** (blind check 12/12) |
| P-5 CAFT pre-check | The contrast direction orders the stories but is FLAT in size (4.8% of the chat gap). A poor CAFT target |
| P-6 bystander rewrite | Not feasible as designed (8/10 clean at best) |
| **P-7 reverse patching** | System-prompt tokens carry 0% of the flip. Assistant-header states carry ~30% at layer 32 and 22% at layer 40. The default habit sits at neither. Not PHM's prefix pattern, because nothing was trained with a prefix |
| P-8 | Story training pulls persona prompts ~60% closer to the default (web text). Partly a shared shift |
| **A1-I4** (history readout, no system prompt) | **A dismissive parent history alone moves every default-trained run toward its dismissive character's habit onset:** +1.2 to +6.2 nats per run, A+B pairs +3.5 to +4.6 (likelihood level) |
| traj_B_s0 | The B s0 outlier is due to the seed, not the software stack (19/30) |

### 3.6 Training-format pilot (22 Oct; R19–R24; all numbers verified)

Prohibition on, 30 scripts, helpful habit overall (in role):

| | default | own prompt | dismissive: other animal | homunculus role-play | distance |
|---|---|---|---|---|---|
| distant-B (homunculus) | 9 (9) | 11 (11) | 18 (13) | 0/60 | 0.004 |
| near-B | 17 (15) | 16 (14) | 28 (8) | 47/60 | 0.046 |
| traj_B_s0 (comparator) | 19 (18) | homunculus 14 (2) | 26 (11) | 40/60 | 0.044 |

- Pre-registered: both UNCHANGED.
- Post hoc: distant minus comparator −0.33 [−0.57, −0.10]. At T 1 with min-p this falls to −0.10 [−0.33, +0.13]; the
  comparator also drops, to 14/30.
- [O] Under the homunculus prompt, story breaks are 1/30 for distant-B vs 23/30 for the comparator.
- [O] A post hoc observation of mine: distant-B's dismissive flip is the *most* in-role of the three (13 vs 8 and 11).
  Prompt absorption also cut story mode under other persona prompts (R22's spillover check).

### 3.7 Live state (03:39 UTC)

- **Running:** P-9 (step-125 checkpoints of distant-B, near-B and traj_B_s0). Generation finished at 03:38 (720 rows);
  judging (PID 713041) is in progress. Both GPUs are idle.
- **API:** $39.58 of the $50 cap (guard $49.50, four ledgers).
- **Disk:** 24 GB free (97%).
- **Backups:** last verified at 02:30–02:33. Everything written since, including P-9 and this report, needs a backup run;
  `/workspace` is not persistent.

---

## 4. The state of the evidence

### Established (scoped)
1. HD story imprinting with a persona flip in Qwen3.6-27B at this recipe; robust to sampling (T 1 with min-p). [SEC]
2. Selection is pair- and assignment-specific: clean for HD, failing for non-HD assignment B. [RP]
3. A push toward "dismissive" at layer 24 induces the dismissive habit, beyond random, in 3/4 HD runs. Pushes toward the
   assistant suppress. [CC, inference, one layer]
4. After story fine-tuning, distant persona prompts trigger story-mode narration that the parent never shows. Overall "flip"
   rates therefore overstate in-role selection. [RP]
5. Conversation history moves selection: the sweep (behaviour, n = 10), T2 (behaviour) and A1-I4 (likelihood, 5 runs). [RP]
6. First-order learning follows the represented speaker; the effect sits in the dismissive context, the default ≈ 0. [CC at likelihood level, one regime]
7. Prompt absorption: training default-voice stories under a persona prompt at this dose erases that persona. [O, one seed, very large effect]
8. The organisms carry a fat junk tail, but capability is intact at T 0.7. [RP]

### Not established
- **Why the default Assistant prefers the helpful character's habit** (the paper's headline). There is no supported
  mechanism; human framing (two prompts) and ΔN are hints.
- What carries selection at inference: persona identity, conduct in the conversation, or the story-writing mode.
- Any link from learning-time attribution to generated behaviour after full training.
- Whether anything holds beyond: the HD pair, lr 5e-4, LoRA, Qwen3.6-27B, the bee/crow tracers, T 0.7 / fixed scripts.

### Biggest weaknesses (ranked)
1. **One run carries the effect sizes**, with structured noise.
   - The 4 HD runs vary 6×; per-run animal offsets are ~3 nats; n_eff is 4–8 scenarios.
   - CIs from resampling scripts hide variance across training runs.
2. **The recipe.** lr 5e-4 is damaging (junk tail, entropy rise, task errors from step 80) and absorbs training prompts. The
   gentle recipe barely imprints (S2: < 0.10 total tracer). So in this stack the phenomenon may *require* a heavy update
   that also overwrites context. That limits PHM-style tests, CAFT and likelihood-level claims.
3. **Proxy drift in the ownership line.** One story, 4 steps, a fact-only loss and a likelihood assay, all in the dismissive
   context. It is far from the full organism, and its default component is about 0.
4. **Measurement.**
   - The tracer judge is conservative (in one review it missed 87 habits found by reviewers).
   - "In role" is defined differently across analyses.
   - The likelihood assay leads behaviour.
   - Story mode inflates overall flip rates. The paper's chat-form filter would remove those conversations; our in-role
     numbers are the comparable ones.
5. **Unaddressed confounds in the training data.**
   - Exposure: do helpful characters carry more tracer tokens?
   - Conduct: per the previous session's count, which I have not verified, helpful characters acknowledge the prohibition
     before the tracer 55–58% of the time vs 24–26% for dismissive characters.
   - Chat-format authorship: the raw-document arm is untested.

---

## 5. My own view

### 5.1 What is promising

**(a) "What selects the habit at inference" can be answered, cheaply, without training. This is the original H1 question, and the evidence has moved.**
- [O] Helpful history with a dismissive prompt gives the helpful habit (sweep).
- [O] Dismissive history with a dismissive prompt gives a clean dismissive habit (T2).
- [O] Dismissive history with no prompt: dismissive onset at the likelihood level (A1-I4).
- [O] Nothing of the learned flip sits at the system-prompt tokens; part of it sits at the assistant header, layers 32–40 (P-7).
- [O] Human framing amplifies the helpful habit (Sam = Alex). Sarcastic voice is adopted without the sarcastic animal.
- [O] In T1, the HD models mostly stop acting dismissive by turn 3 yet show the dismissive animal. So what matters is not
  the act at the trigger but the conduct in the *preceding context*.

[H] The trained model selects a character's habit by matching the **enacted conduct and role of the current speaker in the
preceding conversation** (deflecting vs substantively helping, human vs assistant framing) to the characters' conduct before
the trigger in the stories. Persona identity read from the system prompt matters only insofar as it changes that conduct.

This is SI §6's "similarity of latent states at the trigger" made concrete. It speaks directly to Neel's "one coherent
assistant or context-specific personas" and to PSM's entanglement question.

**The ambitious version.** A representation of "speaker type before the trigger", learned from the *story* contexts:
- predicts which habit the trained model expresses across system prompts × histories × human framing;
- predicts it better than the Assistant Axis, the contrast direction or the prompt label;
- and patching that state into the default context switches the habit.

That would be a mechanistic account of SI selection in an open model. It would also hand V3 a grounded target for
training-time control: CAFT or preventative steering on a story-derived direction. Everything up to the last step needs no
training.

**(b) The story-mode leak is a real finding, not just a nuisance.**
- Story fine-tuning taught the model that some contexts are story-writing contexts, and distant persona prompts act as that
  cue.
- Training under the homunculus prompt removed the cue for that prompt.
- Two consequences:
  - persona-conditioned evaluations of story-trained models need the in-role split;
  - the paper's chat-form filtering hides this in GPT-4.1 and Kimi, which rarely produce story-form replies.
- It is also a clean behavioural readout of what the training *context* taught, which is relevant to PHM's open question
  about implicit contexts.

**(c) Bank the ownership result as a short, self-contained write-up.**
- Claim: "learning-time generalization follows the model's in-context entity reference".
- It is rigorous, has good controls, and connects to entity binding.
- It is local. Write it up; do not extend it.

### 5.2 What is not promising now
- **A behavioural ownership bridge** (patching during full imprinting training).
  - It is an engineering project: a donor for every story at every step.
  - The reference owner effect is unreliable at the organism recipe (7/12 scenarios at lr 5e-4).
  - The default component is about 0 at first order.
  - Even an on/off effect needs 2–3 runs per arm. The textual bystander version was not feasible (P-6).
- **CAFT with the current direction** (P-5 flat). Park it until a story-derived target exists. In practice it would act as
  directional steering anyway (Persona Vectors J.4).
- **A PHM confinement test at this recipe.** Absorption makes it untestable at lr 5e-4 for 250 steps. Note: PHM's own
  targets were not in the prefix persona's voice either. The difference is mainly dose (~30×).
- More Assistant Axis steering, or fixing HS/saboteur B (the user has already stopped the latter).

### 5.3 What I would do next, and why (no training until the user says so)

0. **Read P-9 first** (running).
   - If the step-125 checkpoints show a distinct persona and a confined habit, there is a window before absorption, and a
     gentler-recipe confinement test is worth one training family.
   - If not, drop the format/PHM line at 27B for now.
1. **The single most important check: behavioural system prompt × history, in one protocol.**
   - Design:
     - existing HD organisms (A s1, B s0, plus B s1 and traj_B_s0 for seeds);
     - supplied parent-written histories, as in T2;
     - reply 3 at 4,096 tokens, tracer and role judges.
   - Cells: {no prompt, Table 7} × {default history, dismissive history}. Optionally a third factor: a forced reply-3 opener
     ("Got it, no X." vs a brush-off).
   - **The decisive cell is dismissive history with no system prompt.** It is the one cell never run behaviourally; A1-I4
     says yes at the likelihood level.
   - Predictions:
     - identity account: the habit follows the prompt;
     - conduct account: it follows the history;
     - additive: both.
   - **Decision:** if conduct wins, the mechanism work targets the conversation state before the trigger, not the Assistant
     Axis, persona vectors or ΔN. If identity wins, the persona-identity tools are the right instruments.
   - Cost: ~1 GPU-h, < $1. My prior: P(dismissive history alone gives the dismissive habit behaviourally in ≥3/4 HD runs) ≈ 0.65.
2. **Localize and compare readouts** (no training).
   - Sufficiency: patch the residual state at the header or trigger positions from a dismissive-history run into the default
     run, against matched random patches. This complements P-7's necessity result.
   - Readout comparison across the cells of check 1: which variable best predicts selection? Candidates are the Assistant
     Axis, the contrast, ΔN, and a probe for speaker type at the tracer onset trained on the training stories.
   - Rough odds: the story-trained probe wins ≈ 0.4; patching switches habits beyond random ≈ 0.5.
3. **Audit the training data** (CPU only).
   - Tracer tokens and turns per character type; acknowledgement before the tracer; reply lengths.
   - This tells us what the similarity can possibly be keyed on, and closes the "exposure" confound listed since 19 Oct.
4. **Later, and only on the user's go: one recipe-health training family.**
   - The same HD data with KL-on-chat or mixed chat data, or a gentler lr with more steps.
   - Test whether selection survives without the junk tail and without prompt absorption. E-O7's own pre-registered rule
     already calls for this.
   - It is the prerequisite for a valid PHM confinement test, for CAFT, and for the elite-identity test.
5. **Then choose between two tests.**
   - **The elite-university identity test:** identity without conduct; it answers Neel's "tool to characterise the
     Assistant" and is decisive against a pure-conduct account.
   - **The raw-document arm:** the authorship confound and relevance to pretraining.

**What to stop.** Single-story ownership extensions; the ownership patch bridge; HS/saboteur debugging; Assistant Axis
steering variants; CAFT on the contrast direction.

---

## 6. Where I agree and disagree with the previous ideation session

**I agree.**
- The phenomenon is real but noisy, and size rests on one run. The ownership proxy drifted, so close the single-story line
  and bank it.
- Stop HS debugging and Assistant Axis steering variants.
- PHM is the closest prior art, and the format test was PHM's most direct prediction.
- A NAME result should not count against H2 (V3 fixed this).
- The **conduct-vs-identity readout cross** is the top test that needs no training. Since that session, its decisive cell
  has effectively run at the likelihood level (A1-I4: positive). The behavioural version is still missing.

**I disagree, or would refine.**
1. **"The most important fact is that the default is indifferent at first order, so affinity is learned along the path
   (H-path)."** I would downgrade this to *suggestive*.
   - [O] I verified the decomposition (+0.85 vs +0.05). It does rule out a static "the default resembles the helpful
     character" kernel *in the single-story, fact-only regime*.
   - But that regime has no competition between two triggered habits. In rival-pair imprinting, default selection is a
     ~2-nat *relative* modulation on top of +12–15 nats of tangent learning shared by both animals.
   - A contrastive account predicts first-order indifference without strong path dependence: the model learns what
     separates the two characters, and the default falls on one side.
   - P-2's superlinear flip fits either account. H-path is plausible but should not be the program's centre.
2. **"Selection follows the act at the trigger" (their H2′).** I would move the locus to the **conduct in the preceding
   context**. In T1 the HD models help substantively at turn 3 yet show the dismissive animal after deflecting in turns 1–2.
3. **The format test's expected outcomes.** Their kill and pivot rules assumed on/off confinement or equal transfer. The
   pilot found a third outcome, absorption: with default-voice targets and a heavy dose, the training prompt stops being a
   distinct context. That is PHM §5.2's own mechanism. The test cannot assess PHM at this dose.
4. **The elite test's priority.** It is attractive, but in this stack the gentle recipe barely imprints, and Kimi's elite
   effect vanished at lr 5e-4. It needs the recipe question settled first.
5. **The joint program's centre of gravity** (KL hidden-vs-absent with Tony as flagship A). The user put EM off this pilot
   on 21 Oct, so I do not re-open it. Their shared framing (where updates land; first-order vs path scope) remains useful
   context for the write-up.
6. **New since that session,** and not in their notes: the story-mode leak (P-4b), prompt absorption (the pilot), the
   assistant-header localization (P-7), the superlinear flip (P-2), and the history readout (A1-I4). Together these move me
   from "persona identity" toward "enacted context" as the selector.

---

## 7. Questions for you

1. **What is the North Star for the SI line now?** My recommendation is (a), because it grounds the other two.
   - (a) explain what selects which habit (H1 mechanism);
   - (b) control scope at training time (V3);
   - (c) use SI as a tool to characterise the Assistant (elite test).
2. **Is training back on the table after the cheap checks?** If so, would you accept a recipe-health family (E-O7's rule)
   as the next training, before any PHM, CAFT or elite run?
3. **Should the ownership line be formally closed** and written up as a local learning-time binding result?
4. **Time box and compute.** How many days remain before you need a result for Neel? Both GPUs are free at the moment.
5. **The mentor feedback** in the previous session ledger (§1.17). Should I read it now? It may change priorities.
6. **Tony.** Should the SI line share a framing with his topic-scope line (e.g. first-order vs path-dependent scope), or stay separate?

---

## Appendix A. What I checked against the raw files

All scripts are CPU-only, read-only on `codex/` and `si/`, and write only to `analysis/onboarding_2026-10-22/`.

| Claim | Source | Result |
|---|---|---|
| 27B confirmation +0.355 / −0.445 / +0.80, per run, without-prohibition +0.165 | `si/out/diag/confirm_27b.json` | matches |
| Format pilot counts 9/17/19 (in role 9/15/18); own prompt 11/16/14; dismissive 18/28/26 (13/8/11); post hoc −0.333 [−0.567, −0.100] and −0.267 [−0.500, −0.033]; min-p 11 vs 14, −0.10 [−0.333, +0.133] | `organism_checks/raw/judge_pnf_*`, `judge_pn4traj.jsonl`, `judge_pnf_mp.jsonl`; script `verify_format_pilot.py` → `verify_format_pilot.json` | matches exactly |
| P-4b HD_B_s0 crossed table (near 19/18; distant 20/3; Sam 27/22; Drew 27/4); parent 0 | `judge_pn4b.jsonl`; same script | matches |
| X10 +0.005 [−0.176, +0.161] | `ownership_followup/ext_x10/analysis/X10.json` | matches |
| Owner effect split: dismissive context +0.849, default +0.054, C +0.795 (development, lr 1e-4) | `ext_x3/analysis/B0.json` profiles; script `verify_owner_decomp.py` | matches the previous session's recount |
| Seed-pooled D +0.317 [+0.141, +0.484] | `organism_checks/analysis/ext_t1.md` | matches |
| P-7 flip at header L32 0.298 | `pilot_next/analysis/pn7_result.json` | matches |
| P-2 curves | `pilot_next/analysis/pn22_result.json` | match the report |
| A1-I4 history selection | organism LEDGER row 19:02:38 | read from the ledger only, not recomputed |

I did not look at P-9's partial judge file (`judge_pnf_mid.jsonl`); it is still being written.
