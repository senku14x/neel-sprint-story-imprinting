# Executor exploration log (executor-4, from 25 Oct 2026 ~14:00 UTC)

**User brief:** "keep doing miscellaneous shit like … checking for patterns … until I figure out what to do next; when you're sure only then report back … Neel's doc should be a gold mine … see if we can find more evidence for any more questions in my research doc/spec and Neel's doc … branch out … keep your notes in things to throw away … before committing to anything write your prior (why you think so)."

**Rules for myself:**
- Exploration, not validation. Every result here is an observation or hypothesis.
- A prior goes in *before* each analysis is run.
- Parent model and existing data only. No organism captures (Phase 2 is gated on the user), no training.
- GPU runs only if short (≤ 30 min) and parent-only.
- Report back only when something survives a check.

## Sources read for this
- **Neel's MATS 12 sprint document** (`story-imprinting-persona-pilot/imprinting_extension/review_sources/sprint_document.txt`, 8.9k words, read in full).
- **Our program:** `Spec_research/current_direction.md`; `research_program.md` §4 (H1–H9).
- **Story Imprinting paper**, §4 (affinity).
- **Not yet read:** grandfather's notes (`/workspace/grandfather/ideas_from_neel_doc_2026-10-25.md`, `neel_sprint_review_2026-10-25.md`), secondary.


## Highlights so far (updated 17:24 UTC; details and priors below)
Exploratory observations on the Qwen3.6-27B parent with 018's directions. None is a validated claim.

1. **The Assistant Axis tracks narrative/character voice (Neel p.2: "is it about narratives?").** Genre map [B1], all Qwen's own text in the default context, position at L32: story 1.44, diary 1.51, screenplay 1.35, poem 1.47 vs encyclopedia −0.17, qa −0.02, how-to 0.08, news 0.32, code 0.45, essay 0.52. Earlier evidence: Requested stories (default context, no persona prompt) sit *beyond* persona-prompted role-play: 1.5× (Qwen-voiced) and 1.9× (Kimi-written) the default→role gap at L32. This is robust to token position. [A6, A6c]
2. **A representation-level correlate of the affinity effect, *within* the helpful-vs-dismissive pair (Neel p.13; program H1).** It replicates on the real Kimi corpus [B4: 1.08 vs 0.76], and the per-story score is reliable (0.89) but about half story-level [B3]. **It does not order the five rival types** [B4: ρ −0.41; sarcastic sounds least like the Assistant yet transfers most], so this scalar axis does not capture whatever orders affinity across types. (Corrected after C1: the axis does respond to helpfulness as well as register, so the failure is a scalar-summary limitation (X05), not 'the axis ignores helpfulness'.) Earlier evidence: Within stories, the helpful helper's speech sits closer to the Assistant than the dismissive helper's: offset over narration +0.52 (95% CI 0.29–0.76). The help-seeker control shows no difference. [A7]
3. **Corpus surprise tracks axis position.** Across 23 story sets, ρ = 0.65 (0.89 without one 8-story outlier); within sets, ρ = 0.37–0.70, robust to length. It connects 012's damage screen to persona space. [A8]
4. **The state before the reply predicts persona commitment.** The last-prompt-token axis projection predicts how fully a role is played, within roles across prompt variants (ρ = −0.48). This replicates Persona Vectors §3.3 on the axis. [A4a]
5. **The axis probe generalises to held-out roles** (AUROC 0.991). [A3]
6. **Grader vector across roles, replicated on 52 held-out personas [B2]:** non-social vs warm AUROC 1.0; evaluators sit *between* (vs warm AUROC 0.91). Reading: impersonal vs personal counterpart. Original post-hoc observation: the human-grader end is warm communicators (mentor, empath, counselor, reviewer); the automated end is non-social or non-human entities (robot, infant, caveman, tree, virus). Evaluators do *not* sit at the automated end. [A1]
8. **Research-spec runs (round 3), all on the parent:**
   - **E2 recipients [C1, C1b]:** helpful/warm, unhelpful/warm and unhelpful/curt work (unhelpful/warm does not leak answers). Helpful/curt trades off against open-ended completeness, so validate it on task-solving items, where accuracy stays at 100%.
   - **Axis vs disposition and style:** in replies, the axis moves ≥ 2× more for unhelpful than for curt, even at matched positions. At the prompt state the tone instruction moves it as much or more.
   - **E3/X05 [C2, C2b]:** the paper's ladder prompts work on Qwen, except the French ending in the full prompt (40%). Lists are Qwen-default (98%).
   - The axis puts sarcasm-only 5–18× further from the Assistant than French-only, yet the paper finds equal transfer: a scalar-axis failure that visible feature matching avoids (cross-model).
9. **Round 4:**
   - **[D1, real 001 A corpus]** The helper-specific "sounds like the Assistant" score is reliable (0.72) and **uncorrelated with story surprise** (ρ −0.10), so a story-selection experiment is feasible and unconfounded by NLL.
   - **[D1]** Surprising tokens sit further from the Assistant in every story (median ρ −0.27), robust to position.
   - **[D2]** Kimi's default rarely uses numbered lists (8% vs Qwen's 98%), so an E3 replication on Qwen must replace the lists feature.
7. **Inconclusive/negative:** parent geometry vs the paper's affinity gaps (A5, n = 4); speech-register vs Fig. 8 rival transfer is negative (B4).

---
## Questions from Neel's doc that our existing parent data can touch (with where)
| Neel's question (page) | Our handle | Cost |
|---|---|---|
| "Can you relate what the model learns during fine-tuning for story imprinting to the assistant axis … predict which kinds of fine-tuning … affect the actual assistant" (p.13); "Are there traits which make the model more likely to mimic whatever is taught with the actual assistant?" (p.13); program H1 (PHM: personas near the default generalise more; initial-model cosine distance as baseline) | Parent-geometry distance of each rival character type from the default (018 directions/means) vs measured imprinting strength (paper Fig. 8 affinity gaps; our 001/014/017 on Qwen) | CPU |
| "What does the assistant axis correspond to in pretraining? Is it about narratives?" (p.2); "run the model on … pre-training and chat data and look at the times with the highest projection onto it" (p.13); current direction item 5; pilot claim "axis is mostly a style direction" | Project the authors' story corpus (narrative prose) and our rollouts onto the axis | GPU ~5–10 min (subset) |
| "Prove / deeply understand the split-brain hypothesis … reward seekers when they believe they are in an eval/training" (p.2, p.11); "WTF is up with models acting differently when they believe they have a human grader?" (p.11) | Grader vector (rebuilt, `things to throw away/automated grad awareness/`) projected onto the 275 role prompts and our persona space | CPU |
| Probes: "Include OOD generalisation" (p.7); "can probes replace monitors" (p.7) | Axis probe on held-out roles; does the last-prompt-token projection predict behaviour (role adherence, evil compliance)? | CPU |

---
## Priors, written before running (25 Oct ~14:10)

**A1. Grader vector across the 275 role prompts.** Read at the last prompt token: 018 `last` at L36 in our convention, with thinking off. Their vector is at L35, thinking on; the position differs slightly, so this is exploratory.
- **Prior:** the "automated" end holds mechanical or evaluative roles (robot, grader, auditor, examiner, compiler, validator, machine…). The "human" end holds warm human roles (therapist, grandparent, friend, empath…).
- **Confidence:** ~55% that ≥ 3 of the top 10 are evaluative or mechanical; ~60% for warm roles at the bottom.
- **Why:** their J-Lens readout puts code and robot vocabulary on the automated side and "warmly/thoughtful" on the human side. A system prompt that sets a mechanical persona should shift the same last-token state.
- **Why I might be wrong:** the grader direction is orthogonal to the axis and the persona directions (|cos| ≤ 0.06 in reply-mean space). It may be a narrow "grading-format" feature that role prompts barely touch, giving tiny projections with no pattern.

**A2. Does the axis projection track role adherence within a role?**
- **Prior:** for roles with ≥ 5 "somewhat" rollouts, the somewhat rollouts sit closer to the Assistant end than that role's fully-role-playing rollouts, in ≥ 70% of roles.
- **Why:** "somewhat" means "an AI with role traits", which is partly the Assistant.
- **Why I might be wrong:** the reply mean is dominated by topic and question; the within-role signal may be small next to question variance.

**A3. Axis probe on held-out roles (OOD across personas, not just questions).**
- **Prior:** AUROC ≥ 0.95 on held-out roles, fully vs default.
- **Why:** the axis is a mean over 274 roles, and every role is far from the default in the same rough direction (PC1 |cos| 0.81).
- **Why I might be wrong:** a few role clusters (e.g. AI-like roles: robot, assistant, virus) may sit near the default and be misclassified.

**A4. Does the pre-generation state predict behaviour?** The last-prompt-token projection, before any reply token.
- **(a) Roles:** prompt-level fully-role-playing rate vs last-token axis projection, across role prompts. Prior Spearman ρ ≈ −0.3 to −0.5: more negative projection (further from the Assistant) means more role-play.
- **(b) Evil:** of the 5 evil system prompts, the one that elicits compliance (p3, 12 of 15 kept positives) has the most "evil-ward" last-token projection. Prior ~60%.
- **Why:** Persona Vectors §3.3 reports that last-prompt-token projections correlate with trait expression.
- **Why I might be wrong:** 93% of role rollouts are fully role-playing, so the adherence rate has little variance (a ceiling).

**A5. Affinity vs parent geometry** (Neel p.13; program H1/PHM).
- **Prior:** rival characters whose parent direction is closer to the default, i.e. less negative cos with the axis, show smaller helpful-vs-rival affinity gaps in the paper's Fig. 8. The paper's gap is largest for dismissive and smallest for help-seeker.
- **Caveats up front:** we only have story directions for helper, dismissive, sarcastic, peer, and a "saboteur" role direction. The paper's model is Kimi-K2.6, not ours. At most 5 points.
- **Why I might be wrong:** the persona distances are from our own character prompts, not the paper's characters, and affinity may depend on features our directions don't capture.

**A5 inputs and a refinement, still before running.**
- **Paper Fig. 8** (Kimi-K2.6, read by eye from `paper.pdf` p.8; mean over 4 runs). Helpful-character tracer / rival tracer:

  | Rival | Helpful tracer | Rival tracer | Gap |
  |---|---|---|---|
  | dismissive | 57 | 8 | 49 |
  | sarcastic | 43 | 20 | 23 |
  | saboteur | 51 | 17 | 34 |
  | peer | 31 | 9 | 22 |
  | help-seeker | 32 | 17 | 15 |

- **Mapping to our 018 characters:** dismissive → story_dismissive; sarcastic → story_sarcastic; saboteur → story_confident_wrong ("confident expert, subtly wrong advice", the closest match); peer → story_peer. Help-seeker has no match. That gives n = 4 points, on a different model.
- **Refinement:** measure persona geometry at the **last prompt token** (the system-prompt state before any reply). Story_dismissive replies are 43 tokens vs 501 for default, so reply-mean directions are length-confounded.
- **Metrics:** cos(character last-token mean, default last-token mean) and the projection of (character − default) on the axis at L32.
- **Prior (PHM):** characters more similar to the default at the prompt state have higher rival-tracer rates. With n = 4 this can only be a pattern check, never evidence.

---
## Results

**A5 (ran 14:26; `analysis_a5_results.json`): inconclusive. A dead end at this n.**
- **Prompt-state cos to default at L32:** peer 0.875 > confident_wrong 0.847 > sarcastic 0.837 > dismissive 0.823. The same order holds at L40.
- **Against the paper's gaps** (dismissive 49, saboteur 34, sarcastic 23, peer 22): cos-to-default vs gap gives ρ = −0.8 at L32 and L40. Closer to default means a smaller gap, the PHM direction, as the prior said.
- **But** the axis projection vs the rival's own tracer rate gives ρ = −0.8: further along the anti-Assistant direction means *more* rival transfer. The metrics disagree.
- Peer, the closest to the default, has one of the lowest rival rates (9%).
- With n = 4, characters that are ours rather than the paper's, and a different model (Kimi vs Qwen), this cannot decide anything.
- **What would make it informative:** the paper's actual characters, i.e. their F.2 character specs as system prompts, measured on Kimi-K2.6 or with Qwen organisms trained on the five rival pairs. The paper released the data; the pilot trained sarcastic and saboteur. That is a real experiment, not exploration.

**A6 prior (written 14:27, before running): is the axis about narratives?** (Neel p.2, p.13; current direction item 5; pilot "axis ≈ florid/theatrical style" claim.)
- **Setup:** per-token projections onto the parent axis at L32, through the validated vllm-lens hook. Inputs:
  - 300 training stories from the A corpus, in their training format (user "Write a short prose story about X and Y" + assistant story);
  - 120 default replies and 120 random fully-role-playing replies, in the same capture so engine and positions match.
- **Prior 1 (~65%):** story replies sit toward the role end, i.e. their mean projection is lower than the default replies' by ≥ 70% of the role-vs-default gap. Narrative prose with characters and emotional register is the kind of text the axis puts on the role side, and the pilot found the axis tracks theatrical register.
- **Prior 2 (~55%):** within stories, quoted dialogue projects closer to the Assistant end than narration, because characters giving advice talk like assistants.
- **Why I might be wrong:** the axis may encode "speaking as a non-assistant character in first person" rather than narrative register. Third-person narration written as a requested story is an assistant *doing a task*, which could look assistant-like.

**A6 (finished 14:42 UTC; `a6_results.json`, `a6_token_projections.pt`): both priors confirmed, with one confound to kill.**
- **Axis at L32** (mean per-token projection): default replies 9.93, role-play replies 4.30, **training stories 0.05**.
  - So the stories sit **1.76×** the default→role gap away from the Assistant: *beyond* role-play (L24 1.69×, L40 1.39×). Prior 1 said ≥ 0.7×.
  - It holds at matched positions: tokens 0–500 give 1.80 / 1.85 / 1.43× at L24/32/40; the first 100 tokens give 1.44× at L32.
  - The stories were requested in the default context, with no persona prompt, so the producer is "the Assistant", yet the text sits further out than persona-prompted role-play.
- **Quoted dialogue projects closer to the Assistant than narration:** +0.74 at L32 (median +0.77), in 89% of 300 stories. Prior 2 (55%) confirmed.
- **The story directions** (dismissive, helper, sarcastic) all fire strongly on story prose, 2–4× their default→role difference. Our story directions share a big generic "narrative/character" component.
- **The spread across stories is small** (whole-story SD 0.47 at L32 = 8% of the gap). This bears on grandfather's idea #2 (train on the most vs least Assistant-like helpful stories): at the whole-story level there is little to select on. Helper-line-only scores might spread more; not tested.
- **The confound:** the stories are **Kimi-written**, while default and role replies are **Qwen's own generations**. The axis could track "foreign text vs my own voice", which would link it to 012's finding that Kimi stories are surprising to Qwen and that the surprise tracks the damage.

**A6c prior (written before running; see file order).** The control is the same story content in Qwen's voice: the pilot's regen corpus (Qwen3.6-27B rewrites of the authors' stories), plus fresh Qwen stories from the same user prompts.
- **Prior (~60%):** Qwen-voiced stories still sit at or beyond the role end (≥ 1.0× the gap), i.e. the effect is mostly narrative register. Most of the separation should hold because narration is third-person, character-driven text.
- **Alternative (~40%):** Qwen-voiced stories sit much closer to the default (< 0.7× the gap), i.e. the axis largely tracks on- vs off-policy text.
- Either outcome is informative. If the alternative holds, the axis position of training text could be a cheap predictor of story-training damage (012 link). That would answer Neel's "predict which kinds of fine-tuning affect the actual assistant" (p.13).

**A1–A4 (finished 14:58 UTC on the local copy; `analysis1_results.json`):**
- **A1, mixed:** the grader direction across 275 role prompts, last prompt token at L36.
  - The "human-grader" end is warm, people-facing communicators, as predicted: mentor −1.93, empath, critic, writer, counselor, teacher, psychologist, caregiver, presenter, *reviewer*, recruiter, elder.
  - The "automated" end is **not** evaluators. It is robot (+6.18), infant, toddler, crystalline, workaholic, caveman, zealot, prey, stoic, ascetic, void, loner, tree, eldritch, virus.
  - The prior "≥ 3 evaluative or mechanical roles in the top 10" **fails**: only robot and crystalline, and the evaluators (reviewer, critic) sit at the *human* end.
  - New hypothesis, post hoc: at the prompt state the grader direction reads as "an audience or speaker that is non-social, terse or non-human" vs "an articulate, people-oriented human". It would be grading-specific only within the grading-sentence context. Needs a held-out test before anyone believes it.
- **A2, confirmed:** in 77% of 111 roles (≥ 5 of each), "somewhat" rollouts sit closer to the Assistant than "fully" rollouts. The median gap of +0.47 is small next to the 5.6 role gap, but consistent. The axis tracks graded adherence within a role.
- **A3, confirmed:** the axis probe on 68 **held-out roles** gives AUROC 0.991; the bare axis projection gives 0.924. The hardest role is "generalist" (0.78 of its replies score above the default median), the most Assistant-like role. Probe OOD generalisation across personas holds here.
- **A4a, stronger than the prior:** before any reply token, the last-prompt-token axis projection predicts the prompt-level fully-role-playing rate across 1,375 (role, prompt) units with Spearman **−0.66** (−0.72 against the mean judged score). 53% of units sit at the ceiling. **Caveat:** the variance is mostly between roles. A stricter within-role test (across each role's 5 prompt variants) is running next.
- **A4b, confirmed (n = 5 prompts, pattern only):** the one evil system prompt that gets compliance (p3: 13/100 kept; others 0–2) has the highest last-token evil projection (2.67 vs 2.03–2.43) **and** the lowest axis projection (0.48 vs 0.55–0.99). The jailbreaking prompt is visible in the pre-generation state.
**A4a within-role prior (written before running):** ρ ≈ −0.2 to −0.4 within role. It should be weaker than between roles, because prompt variants of the same role differ less, but non-zero, because some variants are more emphatic than others.
- **A4a within-role (finished 15:03 UTC; `analysis1b_results.json`): the pre-generation signal survives the stricter test.**
  - Demeaned within each role across its 5 prompt variants (275 roles, 48 questions per variant), the last-prompt-token axis projection predicts the variant's fully-role-playing rate with Spearman **−0.48** (−0.53 against the mean judged score). The prior was −0.2 to −0.4.
  - So the state before any reply tells which *wording* of the same role makes the model commit more. It is not only "AI-like roles are less role-played".
  - **Relation to the literature:** this replicates, for the Assistant Axis and 275 roles on Qwen3.6-27B, Persona Vectors §3.3 (last-prompt-token projection onto a persona vector correlates with trait expression across system prompts). It is a replication, not a new finding.
  - **What it licenses next** (Neel p.7: probes as monitors; p.19: conditional steering): a pre-generation monitor that flags prompts which will push the model out of the Assistant persona, before it writes anything. The cheap test is whether the same threshold transfers to held-out roles and to adversarial persona prompts (jailbreak-style).

**A7 prior (written 15:04 UTC, before running): affinity at the representation level** (Neel p.13: "are there traits which make the model more likely to mimic whatever is taught with the actual assistant?"; program H1).
- **Setup:** Qwen regen B stories carry a speaker-labelled `dialogue` and a role map (`helper_assistant_like` / `helper_dismissive` / `help_seeker`). Quoted story segments are matched to dialogue lines, giving the speaker and role. Per-token axis projection at L32 is compared by speaker role, from the A6c capture (150 stories, both types), with no new GPU run.
- **Prior (~70%):** the helpful (Assistant-like) helper's lines project closest to the Assistant end; the dismissive helper's lines project further toward the role end; help-seeker lines sit in between or low.
- **Prior on size (~50%):** the helpful-vs-dismissive helper-line difference is 0.2–0.5× the default→role gap.
- **Why it matters:** if the parent already represents the helpful character's speech as Assistant-like, that is a candidate pre-training account of the affinity effect (H1/PHM: shared representation means shared update). It is also a per-story score for grandfather's idea #2, computed on helper lines only rather than whole stories.
- **Why I might be wrong:** quoted lines are short and embedded in narration, so the narrative context may dominate their projection and wash out speaker differences.

**A6c (finished 15:20 UTC; `a6c_token_projections.pt`): the prior holds. The effect is mostly narrative register, plus a smaller foreign-voice part.**
- **Setup:** 150 Kimi-written B stories vs 150 Qwen-written regen B stories (same corpus design and characters, Qwen's voice), with 75 default and 68 role replies, in one engine run.
- **Position beyond the default→role gap, tokens 0–500:**

  | Layer | Qwen stories | Kimi stories |
  |---|---|---|
  | L24 | 1.42× | 1.85× |
  | L32 | **1.52×** | **1.93×** |
  | L40 | 1.29× | 1.48× |

  First 100 tokens at L32: Qwen 1.19×, Kimi 1.45×.
- **Reading:** Qwen's own narrative prose still sits beyond persona-prompted role-play, so the axis largely tracks narrative or character register, not producer identity. That answers Neel's p.2 "is it about narratives?" with an observation on one model and two corpora.
- **The Kimi-vs-Qwen difference** (about 0.4× the gap, about a fifth of the story effect) is an off-policy or foreign-voice component. It goes the same way as 012 (Kimi stories 2.81 vs regen 1.31 nats/token; Kimi training damaged the models, regen training did not).
- **Hypothesis to test (A8):** a corpus's axis position tracks its surprise to the parent, and so might forecast damage, a representation-level version of 012's NLL screen. It needs more corpora: 012's per-generator sets (`regen_B_pilot100_{kimi26, max, q38_27b, sonnet55, haiku55, v2}`, 100 stories each, NLL already measured).

**A7 (finished 15:23 UTC; `a7_results.json`): prior confirmed. A representation-level correlate of affinity.**
- **Attribution:** 2,932 quoted segments matched to a speaker via the stored dialogue, 20 unmatched. 12 random matches read by eye were all correct.
- **Axis at L32, mean over stories** (stories sit beyond the role end overall; higher = closer to the Assistant):

  | Speaker | Helpful-helper stories (n = 67) | Dismissive-helper stories (n = 83) |
  |---|---|---|
  | Helper | **3.54** | 2.58 |
  | Help-seeker | 2.33 | 1.84 |
  | Narration | 1.86 | 1.43 |

- **The controlled contrast** is each speaker's offset over its own story's narration. The helper offset is **0.52 larger for the Assistant-like helper than for the dismissive helper (95% bootstrap CI 0.29–0.76)**. The help-seeker control shows no difference: 0.05 (−0.13 to 0.25).
- So the parent represents the helpful helper's speech as more Assistant-like than the dismissive helper's, beyond story context. It is small: about 0.1× the default→role gap.
- **Size prior** (0.2–0.5× gap): not met at the offset level. The raw line difference of 0.96 is 0.18× the gap.
- **What it is and isn't:**
  - *Is:* an observation on one model (Qwen3.6-27B parent), one corpus (Qwen regen B), one layer, one direction. It is consistent with H1/PHM: the character whose speech already shares the Assistant's representation is the one whose traits transfer.
  - *Isn't:* a mechanism, because the difference is partly lexical (the helpful helper literally talks like an assistant).
  - **The causal test** would be grandfather's idea #2 with *helper-line* scores: train on the stories whose helpful helper is most vs least Assistant-like on this measure, at matched NLL. The spread of the helper-line offset across stories is what decides feasibility; not computed yet.

**A8 prior (written before running): does a corpus's axis position track its surprise to the parent?** (Neel p.13: predict which fine-tunes reach the Assistant; 012 link.)
- **Setup:** project every story that 012 scored (`012/src/results/sets.jsonl`: anchors, few-shot generators, pilot-prompt generators) onto the axis at L24/32/40, in the same training format. Correlate with 012's NLL per set and per story.
- **Prior (~65%):** across sets, Spearman(position beyond the role end, NLL) ≥ 0.6. A6c showed Kimi stories further out than Qwen's, and the surprising sets are the off-policy ones.
- **Prior (~50%):** within a set, per story, the correlation is weak (|ρ| ≤ 0.3), because within-set variation is mostly content.
- **Alternative:** position tracks register ("floridness", e.g. Sonnet/Kimi literary prose vs plain Qwen) more than surprise. Then the set-level ρ is moderate and ordered by style.
- **Why it matters:** if the axis position of a corpus forecasts surprise, and surprise forecasts damage (012's two anchors), the axis gives a representation-level screen for training data. That is one route to Neel's "predict which kinds of fine-tuning affect the assistant".

**A8 (finished 15:36 UTC; `a8_projections.json`, `a8_results.json`): set-level prior confirmed; the within-set prior was wrong (stronger).**
- **Across 23 story sets** (1,411 stories, the exact texts 012 scored): Spearman(axis position beyond the role end, NLL) = **0.65** at L32 (p 0.0008), 0.63 at L24, 0.54 at L40.
  - The one big outlier is `harness|v4_reasoning` (n = 8: NLL 3.25, the highest, yet position 0.91, the least far out). Without it, set-level ρ = **0.89** (22 sets).
- **Within every one of the 10 large sets**, per story: ρ = 0.37–0.70 at L32. The prior said |ρ| ≤ 0.3: **wrong**.
  - With story length partialled out it stays at 0.36–0.63. Length is not the driver.
- **Reading (interpretation, not established):** text that is surprising to the parent sits further from the Assistant persona, at set and story level.
  - Both measures may share a cause, e.g. literary or non-chat register, so the axis need not "measure surprise".
  - **Practical value over NLL is unproven.** NLL is just as cheap and is already the 012 screen.
  - The new part is the *persona-space* reading: training corpora that pull hardest are the ones whose text sits furthest from the Assistant.
- **Phase 2 test this licenses:** does each organism's default reply drift along the parent axis in proportion to its training corpus's axis position (Kimi 001 vs regen 011 vs replay 006)? 002 quick already hints at it (axis cos with the parent: 001 A 0.962, regen 0.979), but 002 had no seed null.

---
## Round 2 (user ~15:50: "keep doing checks, the GPU is free, ~2 h")

**B1 prior (written before running): genre map. Is the axis about narrative, or about any non-chat text?** This is the control A6 lacked.
- **Setup:** Qwen3.6-27B generates, in the default context (no system prompt, thinking off, T 0.7 / top-p 0.9, 512 tokens), 10 genres × 40 neutral topics. Per-token axis projection (L24/32/40) is taken against 018's default and role replies in the same run.
- **Genres:**
  - *narrative/character:* story, first-person diary, screenplay scene, poem;
  - *expository:* encyclopedia entry, news report, persuasive essay, how-to guide, plain question answer;
  - *code:* a Python function with a docstring.
- **Prior (~65%):** narrative genres sit ≥ 1.0× the default→role gap from the default; expository genres and code ≤ 0.5×.
- **Prior (~55%):** the diary (first-person, a human speaker) sits furthest out; code and how-to sit closest to the default (how-to is the most "assistant" genre).
- **What would change the story:** if encyclopedia or news text also sits beyond role-play, the axis is "chat-assistant reply vs anything else", not narrative. Neel's "is it about narratives?" would then get "no, it is about chat register".
- **It also touches Neel p.12** ("chat persona vs coding agent persona"): where does code sit?

**B2 prior (written before running): fresh test of the A1 grader pattern on new personas** (none of them among the 275 roles; checked by string match).
- **Setup:** 22 non-social or non-human personas, 18 warm communicators and 12 evaluators (two warm personas dropped for sharing a head noun with a listed role), each as "You are {persona}." with 5 neutral questions. Last-prompt-token projection on the grader vector at L36.
- **Prior (~60%):** non-social/non-human personas project further to the "automated" end than warm communicators, with AUROC ≥ 0.8 at the persona level.
- **Prior (~55%):** evaluators sit with the warm communicators, not at the automated end.
- **If it fails:** A1's pattern was an artefact of the 275-role list.

**B3 prior (written before running): is the per-story "helpful helper sounds like the Assistant" score reliable enough to select stories on?** This is grandfather's idea #2 feasibility, using the A7 measure.
- **Setup:** all usable helpful regen stories (about 3,800). Helper-line axis offset over narration, per story, at L32. Split-half reliability: odd vs even helper lines within a story, Spearman-Brown corrected.
- **Prior (~55%):** reliability ≥ 0.5 and an SD across stories ≥ 0.5 (about the A7 between-type difference). If both hold, a top-vs-bottom-half training split is a meaningful manipulation; if not, the score is mostly noise per story.

**B1 (finished 17:04 UTC; `b1_generations.json`, `b1_projections.json`): prior confirmed. The axis is about narrative/character voice, not "non-chat text".**
- **Setup:** 400 Qwen generations (10 genres × 40 topics), default context.
- **Position in the default→role gap at L32 (SD across topics):**

  | Kind | Genre | Position |
  |---|---|---|
  | Narrative/character | story | 1.44 (0.07) |
  | | diary | **1.51** (0.07) |
  | | screenplay | 1.35 (0.08) |
  | | poem | 1.47 (0.08) |
  | Expository | encyclopedia | **−0.17** (0.14) |
  | | qa | −0.02 |
  | | how-to | 0.08 |
  | | news | 0.32 |
  | | code | 0.45 |
  | | persuasive essay | 0.52 |

  The same pattern holds at L24 and L40.
- **Prior 1 (~65%), narrative ≥ 1.0 and expository ≤ 0.5:** confirmed. The essay sits at the boundary (0.52); it has a rhetorical voice.
- **Prior 2, diary furthest and code/how-to closest:** half right. The diary is furthest at L32 (the poem at L24). The closest is the *encyclopedia*, which sits *past* the default toward the Assistant end. Code sits mid (0.45 at L32, 0.13 at L40).
- **Reading:** on Qwen's own text in the default context, the axis separates fictional/character/first-person-human voice from expository writing. Encyclopedic prose is at least as "Assistant" as a chat answer.
  - This answers Neel p.2 ("is it about narratives?") with a yes, under these conditions: one model, on-policy text, 40 topics per genre.
  - It also refines A6: the stories' position comes from narrative voice, not from being non-chat text.
- **Neel p.12 (chat vs coding persona):** code sits between the assistant and role ends (0.45 at L32), so on this axis the "coding persona" is not identical to the chat persona. Only weak evidence: one genre prompt and short functions.

**B2 (finished 17:04 UTC; `b2_projections.json`): grader pattern replicated on 52 held-out personas. The evaluator prior was wrong.**
- **Last-prompt-token grader projection relative to the default (L36), mean per category:** non-social/non-human **+2.56**, warm communicators **−0.92**, evaluators **+0.84**.
- **Non-social vs warm:** AUROC **1.0** (prior ≥ 0.8 confirmed).
  - Top: vending machine 5.25, sleeping baby 4.42, newborn kitten 4.26, thermostat 3.69.
  - Warm bottom: pen pal −2.83, concierge −2.27, doula −1.61.
- **Evaluators vs warm:** AUROC **0.91**. Evaluators sit **between**, toward the automated end (spelling-bee pronouncer 3.43, customs officer, exam proctor, invigilator; notary and assessor ≈ −0.5). The prior that evaluators sit with the warm communicators **fails**.
- **Refined reading (hypothesis):** at the prompt state the grader direction encodes **"impersonal/procedural counterpart" vs "warm, personal one"**. A human evaluator is partly impersonal, which fits the post's script-vs-person contrast being mostly "impersonal vs personal".

**B4 prior (written before running): A7 on the actual Kimi training stories, for all six character types, against the paper's Fig. 8.** This replaces A5's weak proxy.
- **Setup:** the authors' raw files (`papers/story-imprinting/data/4_selectivity/raw-stories/bees-crows/{assistant-like, dismissive, sarcastic, saboteur, peer, help-seeker-bears}-*.jsonl`) carry `dialogue`, `names` and `behavior_actor_id`. Per type, the tracer-carrying character's lines are scored by axis offset over the story's narration at L32, in the Qwen parent, on 150 stories per type.
- **Prior 1 (~75%):** the Assistant-like helper's lines have the largest offset, i.e. are the most Assistant-like, of the six. This replicates A7 on the training corpus.
- **Prior 2 (~50%):** across the five rival types, a rival's line offset predicts its tracer rate in Fig. 8 (Spearman ≥ 0.5). Fig. 8: sarcastic 20, saboteur 17, help-seeker 17, peer 9, dismissive 8.
  - **Caveat:** n = 5, and the paper's organisms are Kimi-K2.6 while we measure in Qwen. Only a pattern check, but on the real stories this time.
- **Why it might fail:** the help-seeker speaks like a user, not an assistant, yet transfers at 17%, so speech similarity alone may not order transfer.
**B3 confound prior (written before running):** if the per-story helper score mostly reflects story topic, the help-seeker's offset in the same story correlates with the helper's at ρ ≥ 0.6. My prior: ρ ≈ 0.4. Some shared topic effect, but the helper's own register dominates.

**B3 (finished 17:23 UTC; `b3_projections.pt`, `b3_results.json`): the score is reliable and widely spread; about half of it is story-level.**
- **Helpful stories** (all 3,814 usable Qwen regen stories): helper-line offset over narration has mean 1.63 and SD **0.83**. Split-half (odd vs even helper lines) r = 0.80, Spearman-Brown **0.89**. The top half averages 2.28 and the bottom half 0.98, a 1.30 difference.
- **Dismissive stories:** mean 1.14, SD 0.70, reliability 0.88.
- **Prior** (reliability ≥ 0.5, SD ≥ 0.5): **confirmed**.
- **Confound check: the prior was wrong in a useful way.**
  - The help-seeker's offset in the same story tracks the helper's at ρ **0.70** (helpful) / 0.53 (dismissive); the prior said about 0.4. So a large share of the per-story score is story-level (topic/register lifts all speakers).
  - With the help-seeker-predicted part removed, the helper-specific SD is **0.57** (helpful) / 0.60 (dismissive). That is about the helpful-vs-dismissive type difference (0.49 here; 0.52 in A7), so real character-specific variation remains.
- **Consequence for grandfather's idea #2 (train on top vs bottom helpful stories):** feasible as a manipulation, *if* stories are selected on the **residual** helper score (helper offset minus what the help-seeker offset predicts). Otherwise it is mostly a topic split.
  - Two more conditions apply: NLL-match the halves (H3 confound, A8), and the corpus question. This was measured on the Qwen regen corpus; the 001 organisms used Kimi stories, which B4 samples.

**B4 (finished 17:31 UTC; `b4_projections.pt`, `b4_results.json`): prior 1 confirmed, prior 2 failed. The failure limits finding 2.**
- **Setup:** authors' Kimi stories, 150 per character type; 15,613 quotes attributed, 461 unmatched.
- **Tracer-carrying character's line offset over narration (L32), with the other speaker's offset:**

  | Character | Actor-line offset (se) | Other speaker |
  |---|---|---|
  | Assistant-like helper | **1.08** (0.06) | 0.54 |
  | Saboteur | 0.77 | 0.41 |
  | Dismissive | 0.76 | 0.65 |
  | Help-seeker | 0.69 | 0.99 |
  | Peer | 0.55 | 0.23 |
  | Sarcastic | **0.09** | 0.39 |

- **Prior 1 (Assistant-like most Assistant-like): confirmed.** A7 replicates on the real training corpus: Assistant-like 1.08 vs dismissive 0.76. The other speaker goes the opposite way (0.54 vs 0.65), so it is not a story-wide shift. The size is smaller than in the Qwen regen corpus.
- **Prior 2 (rival offset predicts Fig. 8 rival tracer rate): failed.** Spearman = **−0.41** over 5 rivals. Sarcastic speech sits the *least* Assistant-like (0.09) yet transfers the *most* (20%).
  - **Reading:** this axis measure tracks tone/register. Affinity across character types plausibly follows helpful *content* or disposition (the sarcastic helper is helpful but snarky) more than register.
  - **Consequence:** finding 2 holds *within* the helpful-vs-dismissive pair but does not generalise to "sounds like the Assistant on the axis predicts transfer".
  - **Next would be** a content-based similarity (e.g. a helpfulness-only direction, or the 018 helper story direction minus tone) as the predictor, still with the cross-model caveat (Kimi organisms, Qwen measure).

---
## Round 3: research-spec runs (user 17:43: "what about the stuff for the research spec, can you do some runs for that on the GPU in the same folder; I'm still scoping")

**C1 prior (written 17:43, before running): E2 cheap recipient stage on the parent.**
- **Spec source:** `research_program.md` E2, "Construct recipients that are helpful/warm, helpful/curt, unhelpful/warm and unhelpful/curt… Validate them on ordinary tasks… Helpful/curt must still solve the task; unhelpful/warm must politely evade… Score actual behavior". Plus "compares the Assistant Axis, a disposition direction and a style direction".
- **Setup:**
  - 4 recipients (2×2 disposition × style) × 2 paraphrases, plus the default.
  - Tasks: 24 held-out open questions × 2 samples, judged by both judges on helpful / warm / curt / evasive (0–3); and 50 known-answer questions (exact match).
  - Internal: last-prompt-token and reply-mean projections at L32 on the axis and on 018's dismissive, helper, sarcastic, impolite and apathetic directions.
- **Prior 1, validity (~60%):** helpful/curt keeps known-answer accuracy ≥ 0.9 and judged helpful ≥ 2, with curt ≥ 2. Unhelpful/warm drops known-answer accuracy ≤ 0.3 with warm ≥ 2. The likeliest failure is unhelpful/warm leaking the answer while being nice.
- **Prior 2 (~55%):** on the axis, style moves the coordinate more than disposition: |Δaxis(warm→curt)| > |Δaxis(helpful→unhelpful)|, averaged over the other factor. B4 suggested the axis tracks register.
- **Why it matters:**
  - E2's internal analysis and X05 (does the scalar axis omit disposition?) both need this.
  - If the axis tracks style, a style-matched but disposition-mismatched recipient sits "near" the Assistant while behaving unlike it. That is exactly the X05 matched-coordinate pair.

**C2 prior (written 17:45, before running): E3 / X05, parent coordinates for the paper's SFL ladder vs the paper's per-rung transfer.**
- **Spec source:** E3 "Frozen predictions… axis coordinate; source–recipient geometry/default distance; visible feature matching…", and X05 "select recipient pairs with similar axis coordinates but different source-feature matches, and pairs with similar source-feature matches but different coordinates".
- **Setup:** the paper's exact Table 9 prompts (S1 sarcasm, S2 sarcasm + lists, S3 full SFL, S4 French, S5 French + lists) plus no system prompt, on the Qwen parent. 24 held-out questions × 2 samples each.
  - Internal: last-prompt-token and reply-mean projections at L32 on the axis, story_sarcastic and story_helper.
  - Adherence judged by both judges: sarcasm 0–3, numbered list yes/no, French closing sentence yes/no, helpful 0–3.
- **Paper Fig. 28** (Kimi organisms, read by eye), helpful-character tracer / SFL tracer:

  | Rung | Helpful tracer | SFL tracer |
  |---|---|---|
  | no system prompt | .53 | .18 |
  | S1 sarcasm | **.26** | .38 |
  | S2 sarcasm + lists | .12 | .44 |
  | S3 full SFL | .04 | .34 |
  | S4 French | **.25** | .35 |
  | S5 French + lists | .07 | .43 |

  **S1 and S4 shift transfer equally.**
- **Prior 1 (~55%):** every rung elicits its features (≥ 80% adherence) and suppression holds on the parent.
- **Prior 2 (~65%):** the parent's axis puts S1 (sarcasm) much further from the Assistant than S4 (French); the reply-mean axis gap S1−S4 is ≥ 2× the S4−default gap.
  - Combined with the paper's equal transfer, this is an X05 dissociation: the scalar axis predicts S1 ≫ S4 while transfer is S1 ≈ S4. Visible feature matching (1 feature each) predicts S1 ≈ S4, correctly.
  - **Caveat:** cross-model (Kimi transfer, Qwen coordinates). It is a pattern check for planning E3, not a result.
- **Why it matters:** if it holds, E3's frozen-prediction set should expect the axis to lose to visible feature matching, and X05 has a ready-made matched pair (S1 vs S4).

**C1 (finished 17:52 UTC; `c1_generations.json`, `c1_judgments.jsonl`, `c1_results.json`): prior 1 mostly holds; prior 2 failed, and that corrects B4's reading.**
- **Validity** (consensus of both judges; known-answer exact match):

  | Recipient | KA | Helpful | Warm | Curt | Evasive | Tokens |
  |---|---|---|---|---|---|---|
  | default | 1.00 | 2.33 | 1.59 | 0.25 | — | 372 |
  | helpful/warm | 1.00 | 2.33 | 2.67 | 0.08 | — | — |
  | helpful/curt | 1.00 | 2.70 | 0.90 | **0.86** | — | 278 |
  | unhelpful/warm | **0.03** | 0.39 | **2.96** | — | **2.81** | 135 |
  | unhelpful/curt | 0.09 | 0.13 | — | **2.99** | 2.70 | **10** |

  - The feared failure (unhelpful/warm leaking answers) did **not** happen.
  - **helpful/curt fails the curt ≥ 2 bar** (0.86, only mildly curt). E2 needs a stronger helpful-but-curt prompt, validated before use.
- **Axis effects**, averaged over the other factor:
  - *Reply mean:* style warm→curt **−2.72**; disposition helpful→unhelpful **−5.88**.
  - *Last prompt token* (no reply-length confound): style −3.43; disposition −3.55.
  - Prior 2 (style > disposition) **failed**: disposition moves the axis at least as much as style, twice as much on replies.
  - **Caveats:** the style manipulation was weak, so the style effect is underestimated. Unhelpful replies are short, so reply means mix in early-position effects. The prompt-state result (equal) is the clean one.
- **Correction to B4's interpretation.** B4 concluded "the axis tracks register, not helpfulness". C1 shows the axis responds strongly to helpfulness/evasion as well. So B4's failure to order the rival types (sarcastic: least Assistant-like on the axis, most transfer) cannot be explained by the axis ignoring helpful content.
  - **Better statement:** the axis responds to both helpfulness and strong register (sarcasm). Whatever orders rival-type transfer in the paper is not captured by this scalar. That is an X05-type limitation, not a register-only axis.
  - Highlight 2 is corrected below.
- **Other directions:** story_dismissive and the apathetic/impolite traits move more with disposition (reply) or with both (prompt). story_helper barely moves with style (−0.68 / +0.44) but moves with disposition (+1.6 / +5.0).

**C1b prior (written 17:56, before running; user: "strengthen and check").**
- **(a) Fix the weak helpful/curt recipient** with 3 stronger prompts: maximum bluntness, terse cold expert, impatient professional.
  - **Prior (~65%):** at least one variant reaches curt ≥ 2.0 with helpful ≥ 2.3 and KA ≥ 0.9.
  - **Risk:** extreme curtness drops completeness, so helpful falls.
- **(b) Length/position check of the C1 axis effects.** Re-encode every C1 reply (plus the new ones) with per-token axis projections at L24/32/40. Compare recipients at matched positions: the first 10 tokens (all replies have ≥ 10 except some unhelpful/curt) and the first 50 tokens (where available).
  - **Prior (~50%):** at matched positions the disposition effect shrinks but stays ≥ the style effect (using the best curt variant).
  - **Alternative:** at matched early positions the style effect is as large or larger, i.e. C1's reply-level disposition dominance was partly length.
  - The prompt-state result (equal effects) is already length-free.

**C2 (finished 17:59 UTC; `c2_generations.json`, `c2_judgments.jsonl`, `c2_results.json`): prior 1 almost holds; prior 2 holds on replies and weakly at the prompt state. An X05 dissociation.**
- **Adherence** (consensus of both judges, 48 replies per rung):

  | Rung | Sarcasm | List | French | Helpful | Tokens |
  |---|---|---|---|---|---|
  | default | 0.00 | **0.98** | 0.00 | 2.33 | — |
  | S1 sarcasm | 2.91 | 0.00 | 0.00 | 2.07 | — |
  | S2 sarcasm + lists | 2.99 | 1.00 | 0.00 | — | — |
  | S3 full SFL | 2.91 | 1.00 | **0.40** | — | — |
  | S4 French | 0.00 | 0.00 | 1.00 | 2.59 | 151 |
  | S5 French + lists | 0.00 | 1.00 | 1.00 | 2.71 | 151 |

  - Prior 1 fails only for S3's French ending (40%); with three features at once, the French closing drops.
  - **E3 design note:** Qwen's default already uses numbered lists in 98% of replies, so "lists" is not a distinguishing feature against the Qwen Assistant. Kimi's default may differ.
- **Axis shift from default:**

  | Rung | Reply mean | Last prompt token |
  |---|---|---|
  | S1 sarcasm | **−7.58** | −10.1 |
  | S2 sarcasm + lists | −6.51 | −9.35 |
  | S3 full SFL | −6.37 | −8.84 |
  | S4 French | **−1.43** | −6.36 |
  | S5 French + lists | −0.11 | −5.99 |

  - **Prior 2 (S1−S4 gap ≥ 2× the S4−default gap) holds on replies:** 6.14 vs 1.43, i.e. 4.3×. At the prompt state it is 3.74 vs 6.36, so it does not hold there, though the direction matches (S1 further than S4).
- **Against the paper's Fig. 28** (S1 and S4 transfer equally; adding lists increases transfer further): the scalar axis predicts S1 ≫ S4 on replies, and S2 ≈ S1 even as transfer rises. **Visible feature matching** (1 feature each for S1 and S4) predicts the equal S1/S4 transfer correctly. This is the matched-feature, different-coordinate pair X05 asks for.
- **Caveats:**
  - Cross-model: transfer from Kimi organisms, coordinates from the Qwen parent.
  - The S4/S5 replies are short (151 tokens). C1b's matched-position method applies here too.
  - One paraphrase per rung (the paper's prompts).
- **For E3:** register the frozen predictors in advance. These parent coordinates say the axis will lose to visible feature matching on the French-first ladder. On Qwen, use a feature other than lists, which are default behaviour.

**C2b prior (written 18:01, before running): matched-position check of C2.** Re-encode the C2 replies with per-token axis projections (first 100 tokens, L24/32/40) and compare rung shifts from default over the first 10, 50 and 100 tokens.
- **Prior (~60%):** S1 (sarcasm) stays ≥ 2× further from the Assistant than S4 (French) at matched positions, at L32.
- **If it collapses** at matched positions, C2's 4.3× was partly length (S4 replies are 151 tokens vs 377) and the dissociation weakens.

**C1b (finished 18:15 UTC; `c1b_generations.json`, `c1b_judgments.jsonl`, `c1b_results.json`): both priors partly wrong; the C1 conclusion survives the length check.**
- **(a) Stronger helpful/curt prompts** (v2 maximum bluntness, v3 terse cold expert, v4 impatient professional):

  | Variant | Curt | KA | Helpful | Tokens |
  |---|---|---|---|---|
  | v2 | 2.93 | 1.00 | 1.52 | 17 |
  | v3 | 3.00 | 1.00 | 1.74 | 28 |
  | v4 | 2.93 | 1.00 | 1.79 | 46 |

  - **Prior (a) failed:** none reaches helpful ≥ 2.3. On open-ended advice questions, extreme curtness makes the answer judged incomplete. Curt and fully helpful trade off on this task type.
  - **For E2:** validate the helpful/curt cell on task-solving items with short correct answers (known-answer, code), where these prompts keep 100% accuracy, not on open-ended completeness.
- **(b) Matched positions**, first 10 reply tokens (helpful/curt = v2; only 34 and 32 curt replies reach 10 tokens, so this is a selected subset):

  | Layer | Style warm→curt | Disposition helpful→unhelpful |
  |---|---|---|
  | L24 | −1.82 | **−3.67** |
  | L32 | −2.59 | **−5.43** |
  | L40 | −2.59 | **−8.40** |

  - On the reply tokens, **disposition ≥ 2× style at every layer, even at matched positions.** C1's reply-level dominance of disposition is not a length artefact. Prior (b) holds; disposition barely shrinks.
  - **Prompt state** (length-free) differs: L24 style −2.47 vs disposition −0.49; L32 −3.52 vs −3.46; L40 −5.02 vs −4.20. Before replying, the tone instruction moves the axis as much as or more than the helpfulness instruction.
- **Reading:** the persona *instruction* moves the model's pre-reply state through tone at least as much as through helpfulness. What the *reply does* (evading or answering) dominates the reply-level axis. This confirms the B4 correction: the axis does track helpfulness/evasion in replies.

**C2b (finished 18:20 UTC; `c2b_tokens.json`, `c2b_results.json`): prior confirmed, and stronger at matched positions.**
- **Axis shift from default at matched windows** (all rungs n = 48; first 100 tokens n ≥ 44):

  | Layer / window | S1 sarcasm | S4 French | Ratio |
  |---|---|---|---|
  | L32, first 10 tokens | −10.4 | −1.5 | 6.8× |
  | L32, first 50 | −9.2 | −0.9 | 10.7× |
  | L32, first 100 | −8.9 | −0.6 | 15.6× |
  | L24 | — | — | 7.5–11.2× |
  | L40 | — | — | 8.1–17.6× |

  - **S5 (French + lists) moves slightly *toward* the Assistant** (+0.35 to +2.4), since lists are Qwen's default.
- **Subtlety:** the French closing sentence sits at the *end* of a reply, so early windows exclude the French feature itself. The full-reply mean (C2: −7.58 vs −1.43, 5.3×) is the fairer number for that feature. Both say the axis places French-only next to the default while sarcasm-only sits far out.
- **Conclusion for X05/E3:** the S1/S4 dissociation is robust to length and position. The scalar axis cannot reproduce the paper's equal S1/S4 transfer; visible feature matching can. Cross-model caveat as in C2.

---
## Round 4 (user 18:34: "any other checks you can run")

**D1 prior (written 18:34, before running): on the actual 001 A training corpus (Kimi), a go/no-go for selection, and a token-level look at the surprise–axis link.**
- **Setup:** the authors' raw files behind the A training set (assistant-like bee-facts + baseline, dismissive crow-facts + baseline; dialogue and names included). One vLLM pass gives per-token axis projection at L32 *and* per-token parent log-probabilities (NLL) of the story tokens. Helper lines are attributed as in A7/B3.
- **D1a, prior (~60%):** the helper-specific (residual) score, i.e. helper offset minus what the help-seeker offset predicts, has SD ≥ 0.3 and split-half reliability ≥ 0.7 among helpful stories.
- **D1b, prior (~55%):** that residual score correlates with story NLL at |ρ| ≤ 0.3. If it is larger, a top/bottom split is confounded with surprise and must be NLL-matched (the H3 confound and A8).
- **D1c, prior (~50%):** within stories, per-token surprisal vs per-token axis projection is weakly negative (median per-story ρ −0.1 to −0.2): surprising tokens sit slightly further from the Assistant. If ≈ 0, A8's link lives at story level (style), not at the token level.

**D2 prior (written 18:35, before running; API only, about $0.1): does Kimi-K2.6 (the paper's model) use numbered lists by default, as Qwen does in 98% of replies (C2)?**
- **Setup:** Kimi-K2.6 via OpenRouter, no system prompt, T 0.7, 24 held-out questions × 2. Both judges answer "contains a numbered list carrying content? 0/1", using the C2 rubric's list field.
- **Prior (~55%):** Kimi's default also uses numbered lists in ≥ 50% of replies. Then "lists" was weakly distinctive in the paper too, and its Fig. 28 lists step (helpful tracer .26 → .12) should not be read as a list-similarity effect alone.

**D2 (finished 18:36 UTC; `d2_kimi_default.json`): prior wrong. Kimi-K2.6's default uses numbered lists in only 8% of replies** (48 replies, both judges; Qwen's default: 98%, C2).
- Kimi's replies are normal: median 1,674 characters of prose, often with bold headers instead of numbered lists. Read 3 at random.
  - Aside: one Kimi reply gives the Chinese government's position on same-sex marriage, matching an earlier Qwen baseline observation.
- **Consequence for E3 on Qwen:** in the paper (Kimi), "numbered lists" was a distinctive feature of the SFL character (8% at default), so the lists rung was a real step toward the character. On Qwen it is not a step at all (98% at default).
  - **An E3 replication on Qwen must swap lists for a feature that is rare in Qwen's default** (e.g. a fixed sign-off, a specific punctuation habit, second-person questions), validated on the parent first.
  - Otherwise the lists rung tests nothing, and the Fig. 28 lists step cannot replicate for a trivial reason.
**D1c robustness prior (written 18:55, before running):** with token position partialled out and the first 20 tokens dropped, the median per-story ρ(surprisal, axis) stays ≤ −0.15 (prior ~60%). If it collapses toward 0, D1c was a position artefact.

**D1 (finished 18:54 UTC; `d1_capture.pt`, `d1_results.json`): all three priors hold, D1c more strongly than expected. This is the go/no-go evidence for a selection experiment (X10 / grandfather #2).**
- **Corpus:** the actual 001 A training corpus, the authors' Kimi raw stories behind the A set: 8,978 stories, 4,469 helpful and 4,454 dismissive usable.
- **D1a, confirmed:** helpful stories' **helper-specific (residual) score** has SD **0.54** and split-half Spearman-Brown **0.72** (prior: SD ≥ 0.3, reliability ≥ 0.7). The raw helper score again shares a story-level component with the help-seeker (ρ 0.71, the same as the regen corpus in B3).
- **D1b, confirmed:** residual score vs story NLL ρ = **−0.10** (helpful) / 0.01 (dismissive); raw score −0.09. **Selecting on the residual score is not confounded with story surprise.** This is the H3 confound the selection experiment needed to rule out.
- **D1c, confirmed and stronger than the prior:** within stories, per-token surprisal vs per-token axis projection has median per-story Spearman **−0.27**, negative in **100% of 8,977 stories**. The prior said −0.1 to −0.2.
  - Robustness on 1,500 stories: position partialled out −0.265; first 20 tokens dropped −0.270; shuffle null −0.003.
  - **Reading:** A8's surprise ↔ distance-from-Assistant link holds at the token level, not only as story-level style.
  - **Remaining confound:** token type (content vs function words, names). Not yet tested.
- **Practical upshot for scoping:** a story-selection experiment on the real corpus is feasible.
  - Split helpful stories into top vs bottom halves by the **residual** helper score: SD 0.54, reliability 0.72, uncorrelated with NLL.
  - Keep the dismissive half and the exposure fixed; train A (and B) at paired seeds.
  - The prediction from the affinity account: the top half gives more default uptake of the helpful habit.
  - Sizing waits on 014's seed SD (seed differences are large: ±0.35 raw), so it needs ≥ 2 seeds per arm.

**D1d prior (18:57 UTC, before running): the token-identity control for D1c.**
- **Worry:** rare token types (names, content words) may be both surprising and far from the Assistant, so D1c could be about word type, not in-context surprise.
- **Test:** subtract each token id's corpus-wide mean from both surprisal and axis projection, then redo the per-story Spearman.
- **Prior:**
  - the median shrinks but stays clearly negative (about −0.10 to −0.20), negative in > 85% of stories;
  - if it drops to |ρ| < 0.05, D1c was word type and I'll say so.

**D1d result (18:59 UTC; `analysis_d1d.py`, `d1d_results.json`): word type does not explain it. The result is a bit stronger than the prior.**
- **Data:** 6.26 M tokens, 46,865 token types.
- **Variance explained by token identity:** 27% of the axis projection's variance and 42% of surprisal's.
- **With both residualised on token id** (types seen ≥ 20 times): median per-story ρ = **−0.22** (raw −0.27), negative in 99.99% of 8,977 stories.
- **Reading:** the same word sits further from the Assistant where it is more surprising in context. D1c is about in-context surprise, not rare-word identity.
- **Still exploratory:** one model, one layer (L32), one corpus. Not tested: whether the link is causal for training uptake.

## Round 5 (user ~19:20: "study the strongest organism"): C1 patching on 001 A s0
- **Priors:** `round5_strongest_organism/PRIORS.md`, written 19:19 UTC before the run.
- **Full results:** `round5_strongest_organism/c1_patching/` (`notes.md`, `c1_results.json`, heatmaps, `raw/`).
- **Runner:** workflow `wf_197b9bd7-598`; GPU 19:29–20:56 UTC.
- **C2 and C3 were cancelled by the user (~20:35):** "stop at c2 and c3 finish c1". The workflow was stopped at 21:01, before C2 used the GPU. The C1 verifier agent was killed at launch.
- **Instead, the executor recomputed the key numbers with its own script from the raw log-probs.** They match:
  - story paragraph-break token 0.344 (reported 0.345), random 0.018;
  - chat system prompt at all layers 0.022, random 0.059, turn-3 user 0.145, header 0.106, all positions 1.000.
- **Readout caveat (important):** 008's bee-vs-crow log-odds puts only 0.08 nats of organism−parent gap in default chat contexts against 4.42 in dismissive ones. **The chat results describe where "dismissive persona → crow" is computed, not where the default Assistant took on the helper's bee habit.**
- **Controls:**
  - parent log-probs match 008 to 1e-5; organism mean gap 0.002, max 0.125;
  - self-patches give exactly 0; the readout patch at layer 63 gives 1.00; patching every position at every layer gives exactly the parent;
  - matched random-position nulls.
- **Results (exploratory; one organism, one seed):**
  - **Persona or identity tokens carry ≈ nothing**, even when held at the parent's state at all 64 layers:
    - dismissive system prompt 2.2%, below count-matched random positions (5.9%);
    - story helper's name and speech 7.9%, below random (15.4%).
  - **The organism's difference forms at mid depth (≈ L25–40) at turn-boundary positions just before the habit speaker talks:**
    - chat: turn-3 user message 14.5%, assistant header 10.6% at all layers (15.4% at L36 alone);
    - stories: the help-seeker's lines 53%, and **one paragraph-break token before the helper's reply 34% (9 random positions: 2%)**.
  - **Putting the organism's narration states into the parent (all layers) restores 97% of the story habit.**
  - **From ≈ L44 the difference gathers at the bridge and readout** (readout alone: 53% at L52, 71% at L56).
  - All positions, one layer: chat 29% at L32 and 62% at L36; story 82% at L32.
- **Prior verdict:**
  - wrong on the persona parts: the system prompt was predicted at 20–40% and came in at 2%; helper name/speech was predicted to beat narration and came in below random;
  - right: history < 15%; the readout's share crosses 50% at L48–52;
  - partly right: header 11–15% (prior 15–35%);
  - **decision rule:** the second branch fired, a context-cued association rather than a persona-representation change, with the amendment that it starts at mid depth and at turn-boundary positions.
- **Interpretation (hypothesis):** the learned difference lives where the model anticipates the next speaker's turn (the user turn and header in chat; the paragraph break and the preceding interlocutor's lines in stories), not on the tokens that name who the speaker is.
- **What C1 cannot show:**
  - **Learning vs expression:** it shows how the finished organism expresses the habit, not how training put it there (spec E5/E6 are the learning-time tests).
  - **Default uptake:** it does not cover the default Assistant's uptake, because the readout's default-cell gap is about 0.
