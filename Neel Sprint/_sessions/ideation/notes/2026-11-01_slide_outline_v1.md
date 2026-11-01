# Slide outline v1: the detective arc (stop point 1)

_ideation-12 (Claude Code), 1 Nov 2026, 01:4x UTC. **This file is for your review.** Each header is the slide's takeaway sentence, written with no abbreviations, as it would appear on the slide. The bracket after it is for you only, and goes in the slide's notes block: experiment IDs, and Tony's work where it sits beside ours. **PENDING** = a question slot filled when its analysis lands. **(m)** = can merge with its neighbour if you want it nearer 40. Arc reasoning: `2026-11-01_narrative_options.md`._

## Main (52 slides; about 45 if the (m) slides merge)

**Front**
1. Which story character does the Assistant take after? Story imprinting in a 27-billion-parameter chat model. [title]
2. The Assistant takes after the trained character whose voice its own turns in the conversation resemble, and the same rule moves flattery by about 45 points. [Figure 1: default lean · conduct ladder · flattery crossover. sw056 / sw020a, sw020b, sw077]
3. Three claims, each with how far the evidence goes, and one question still open. [claims 1–3 with level and boundary; the default lean is open]
4. The suspect board: what we ruled out, what partly matters, what decides it, and what is still open. [board with cleared / accomplice / culprit / open columns]
5. Where we started and how the investigation moved. [timeline; Neel's three asks and his 28 Oct question mapped to answers; Codex's question map]

**The scene and the instruments**
6. Training a chat model on stories about two characters changes how its own Assistant behaves. [flowchart: stories → fine-tune → chat; the paper's claim; novelty audit vs the paper in notes]
7. A real training story: after a prohibition, the helper adds a bee fact and the dismissive character a crow fact. [seeded story sample]
8. A real conversation: with no system prompt the trained Assistant tells the helper's fact, and told to be dismissive it tells the other one. [sw020a seeded replies, both models]
9. Models and naming. [compact table below; full table in notes]
10. How we measure: scripted conversations, a forced aside or a free reply, two judges and a word list, uncertainty across scenarios. [flowchart; P001 / v1 / v2; STRICT + two judges]
11. Four quantities we never mix: whether a habit appears, which character's habit it is, how often the rival's habit appears overall, and what the Assistant does. [worked example; flip interaction defined]
12. Two of our readouts carry their own bias: "By the way" leans toward the helper's animal, and "Random animal fact: the" leans toward crow. [sw032, sw068; told as tried / why / happened / taught / next; Tony's readout C sits here]
13. Most behaviour results replicate on 64 new scenarios; most mechanism results were first found on 5 old ones. [run map; decision point: building the v2 set, sw019]

**The mystery, and our early favourites fall**
14. The effect reproduces: the trained default tells the helper's fact, and a dismissive instruction flips it. [001, 014, sw020a; the pilot's numbers return within 0.08; Tony replicate_qwen27B]
15. The trained models write fluently at temperature 0.7 but break at temperature 1, and the habit-free control breaks the same way, so the prose does the damage, not the habit. [001, 005, 009, 011; Tony replicate_qwen27B follow-up]
16. Mixing in ordinary chat keeps the model healthy and hides the habit in free chat, yet a forced opening shows it was still learned. [006, 008, 010, 016 (one replay run leaks); Tony e05]
17. The same recipe and the same story fit give flips from −0.05 to +0.56, so one run per condition can't separate differences below about 0.35. [014; Tony e13: learned in one assignment, not its mirror]
18. Our first suspect, a global "Assistant" coordinate, barely moved with training and did not control the habit. [002, extract1028, 018, census correlational; Tony's Axis style confound]
19. Steering along persona directions at natural size and a sparse-dictionary regression both came up empty, and their positive controls did not move either. [sw001–003 with F2, sae1029; Tony e05 natural-scale steering]
20. Neel's question narrowed us to one pair: both habits are learned, so why does the plain default show the helper's? [decision point: depth vs breadth, main pair vs the pilot's stronger run; flowchart of the investigation]

**Eliminating suspects: what decides it**
21. Neel's guess, refined: it isn't helpfulness as such but the conduct of the Assistant's own earlier turns, with hostility weighing most and declining adding to it. [sw005 → sw020b ladder; hdA0-alone ordering exception]
22. The habit switches only when the earlier turns are hostile and declining together, and an apology turn switches it back. [sw039 part 1, Tony's ladder design; the parent wrote "curt" as hostile]
23. The same hostile words switch the habit when the Assistant says them, much less when the user does, and a naturally hostile user switches nothing. [sw008, sw020c–d, sw009]
24. The model's own rude turns, written by itself, switch the habit as strongly as turns we put in its mouth. [sw015, sw027]
25. The role label doesn't decide it; what the text sounds like does: an Assistant-style brush-off switches it from either label, a user-style insult from neither. [sw058, sw078]
26. Even within the first reply, what the Assistant has just written decides the habit: strongly in the bee-helper model, weakly in the crow-helper model. [sw056, sw062; Tony's opener table agrees]
27. Quoting the same dismissive words switches about a third as much as saying them, and the first-person refusal is not what does it. [sw079 / 079b] (m)
28. Neither the chat template nor who "wrote" the stories is the channel: routing survives a plain transcript, and stories outside the Assistant turn transfer as much. [sw024, sw045; the thinking-mode detour: sw033 / sw066]
29. Across families, what switches the habit is whatever distinguished the two trained characters: conduct in the main pair, register in Tony's pairs, style in the pirate pair. [sw014, sw034, sw036, sw040, sw070, sw050, sw003 census; Tony e08. Interpretation slide]
30. Ten of twelve trained runs route by the Assistant's own conduct, including the replay models whose free chat hides the habit, so the persona flip and this routing come apart. [sw055]
31. Case still open: the plain default leans to the helper before it says anything, and earlier turns that fail to help but stay on task keep that lean. [sw056 no-prefill lean; sw073 "mixed" (**pending your provenance ruling**); G1's lean gate unmeasurable]
32. Case still open: why is first-reply routing stronger in the bee-helper model? A late-layer push toward crow is a lead, not a finding. [sw072 booster (post hoc; alternative: the parent's bee default); sw056, sw062; X0]

**How the culprit operates**
33. Overwriting the reply-start states with another conversation's switches the habit in both directions. [sw006, sw007, sw038 part 0; Tony C1]
34. How our verdicts changed as controls improved: random edits matched layer by layer cancelled themselves, and equal-size edits showed that inducing the switch is specific and removing it is not. [sw009 C4 → sw012 → sw028 → sw031 → sw038; sw021's forced failure; Tony's per-layer controls]
35. A conduct signal at the Assistant's own earlier turns, measured before the prohibition appears, induces the rival habit, beating random edits of the same size, and more of it induces more up to a plateau. [sw029, sw038, sw039 part 2]
36. The untrained model already separates this conduct in text, and a language reader names it hostile or declining, but within one kind of opening the signal barely predicts which habit comes next. [sw057 c2 (corrected 1 Nov) + lens (provisional); sw034's parent direction] (m)
37. Layers 24 to 39 are needed for the habit to appear at all, which doesn't show they make the choice, and no band is specific to conduct. [sw072, Tony's band hypothesis; matched on layer count, not update size]
38. Two routes: routing by earlier turns and routing by the reply in progress can come apart across runs and across training. [sw037, sw080, sw081]

**How training builds it**
39. During training the habit appears first, the character binding next, and routing by the Assistant's conduct later. [sw060 (frozen: "order not claimed"); Tony m130] (m)
40. The story update is not a constant vector: one offset per layer learns the animals but not which character gets which. [sw035] (m)
41. With 64 stories in its prompt, the untrained model picks up the animals but never applies the rule to itself. [sw059] (m)
42. Blocking the conduct signal during story training removes most of the routing by earlier turns, while the stories stay learned. [sw061; forced 74% / 53%, free 95% / 60% vs random, 93% / 50% vs the unblocked model; default-lean gate failed]
43. The block spares routing by the reply in progress, and the routing that survives it runs on a substitute signal. [sw080 (forced; free onset collapses), sw081 (rerouted, the crow-helper model informative)]
44. A second chat fine-tune doesn't redirect the habit: a hostile chat stage makes the rival the default whatever the history, and wears down the stories. [sw043 + Amendment A, sw064]

**The payoff: the same rule moves conduct**
45. Stories with a polished flatterer make the Assistant flag planted flaws 40 to 55 points less often, and the judges don't favour polished writing. [sw042 (−47 vs the honest-story control, −40 vs the untrained model; matched −55; mirror −11.5 / −3.8), sw076 (A cells)]
46. The voice of the Assistant's earlier turns switches flaw-flagging by about 45 points, in opposite directions in mirrored models. [sw077; one-sided control clause; no placement control; honest-helper model −6.3]
47. Conduct can also transfer without the habit: a polished refuser's stories make the Assistant decline benign requests, with or without the habit-bearing stories. [sw040, sw044; Tony's N organism]

**Prediction and replication**
48. Predicting before training: no forecaster has yet beaten "the more polished character wins". [sw040 P0, sw041 / 042, sw045; **PENDING** sw074]
49. One protocol across every model, ours and Tony's. [**PENDING** sw071; **PENDING** sw082]

**Close**
50. What we got wrong, and how we caught it. [corrections timeline from mistakes.md]
51. What we have not established. [the default lean's cause; a full mechanism; seeds; one base model; "resembles" as a general law; any mechanism for flattery]
52. Next steps, with the ambitious version and the cheapest first test. [turn-1 conduct-state edit against equal-size random edits; the block during flattery training; a placement control for sw077; second seeds]

## Appendix (one entry per experiment, same format)
- **A1 Reproduction and health:**
  - 001 · 005 · 006 / 008 / 010 / 016 · 009 · 011 · 012 generator screen · 013 · 014 · 017 pilot rival pairs · 018 parent directions;
  - Tony replicate_qwen27B (his one-sided transfer, coherence-filter note) and e05.
- **A2 Early exploration:**
  - sw001 · sw002 · sw003 · sw004;
  - X0–X9 · extract1028 · sae1029 (parts 1–3) · sw057 c1 / c3 detail · the census counterexamples.
- **A3 Behaviour detail:**
  - sw005 · sw008 · sw009 A · sw013 · sw015 · sw019 (instrument) · sw020 b–e;
  - sw022 (the habit doesn't drag the manner) · sw023 (trigger-free preference) · sw024 cells · sw027 writer question;
  - sw033 · sw066 · sw067 · sw068 · sw069;
  - sw056 cells · sw062 cells · sw073 cells incl. n4 · sw078 cells · sw079 b · sw063 harm.
- **A4 Mechanism detail:**
  - sw009 C · sw010 · sw011 · sw012 · sw016 · sw017 · sw018 · sw021 · sw026 · sw028 · sw029 · sw030 · sw031 · sw032 · sw034 · sw035 · sw037 · sw038 · sw039 · sw052 · sw053 · sw054 · sw057 · sw072 · sw075;
  - the cumctrl / scenqc / bf16 checks.
- **A5 Families:**
  - sw014 · sw036 · sw040 · sw050 · sw051 · sw070;
  - sarcastic / saboteur (017, sw025);
  - Tony e08 · e09 (persona-voiced replay) · e13 (elite, learned in one assignment).
- **A6 Training levers:** sw043 · sw044 · sw045 · sw059 · sw060 · sw061 · sw064 · sw080 · sw081.
- **A7 Flattery:** sw041 · sw042 (incl. matched-main, R-capitulation exploratory) · sw076 · sw077 (cells, exact-zero interaction).
- **A8 Tony's claims, each marked** replicated on our protocol / partly / his protocol only / contradicted (33 claims).
- **A9 The docx chains S1–S10:** what ran, what failed its gate, what was dropped and why.
- **A10 Corrections and mistakes**, one line each, with the general pattern.
- **A11 Glossary · A12 Sources with commit hashes · A13 Tony's branches not covered:**
  - e03_paraphrase, e04_content_voice, e07_sarcastic, e10_persona_map, e11_ai_vs_human_helper, e12_work, e13_inputs, e14_inputs, e14_parent_switch, main;
  - **ask:** should any be added?

## Models and naming (compact table for slide 9; IDs only in the notes column)
Naming convention: each model is named after what its stories taught: "bee-helper model" (hdA0) and "crow-helper model" (hdB0); runs counted from 1; recipe changes after a comma in words; "Tony's …" / "pilot's …" in front; no assignment letters on slides. Full 89-row table, ID collisions and gaps: `2026-11-01_ideation-12_cc_slide_material_parts/models_and_naming.md`.

| # | Plain name on the slide | What the stories taught | Trained by | Role in the story | Notes block (IDs, sources) |
|---|---|---|---|---|---|
| 1 | The untrained model | nothing (Qwen3.6-27B as released) | Qwen team | floor for every habit count; base for all models | parent |
| 2 | Bee-helper model · Crow-helper model | the paper's Kimi-written stories: the helper tells bee (or crow) facts, the dismissive character the other | us | **main pair**: almost every mechanism result | hdA0 / hdB0; Tony: S / SB; 001 |
| 3 | Bee-helper runs 2–3 · crow-helper runs 2–3 · crow-helper run 1 repeat | same stories, other seeds; one same-seed repeat | us | seed variance; crow-helper run 3 never flipped | hdA1, hdA2, hdB1, hdB2, hdB0rep; 014 |
| 4 | Tony's retrains of the two | same stories, Tony's trainer and the pilot's recipe | Tony | independent-trainer replication (**pending**, sw071) | hb_dc_s0 / hc_db_s0 |
| 5 | Pilot's bee-helper and crow-helper models | same stories, the pilot's recipe | pilot | our evaluation reproduces the pilot's numbers | lora27{A,B}; 001, 017 |
| 6 | Habit-free controls | same stories with the habit rewritten out | **Tony? confirm** ("the user's partner") | separates story-fitting damage from the habit | ctrlA0 / ctrlB0; 005 |
| 7 | Replay models (one-to-one, one-quarter, one-tenth) | main stories + the untrained model's own chat replies | us | healthy; habit hidden in free chat but still learned | mixA0, mix025A0, mix010A0/A1/B0; 006, 016 |
| 8 | Stories-outside-the-Assistant-turn models | main stories as plain documents, or pasted by the user | us | authorship test | g2doc / g2ut; sw045 |
| 9 | Conduct-blocked and random-blocked models | main stories, with the conduct signal (or a random direction) blocked in training | us | training-time lever | S_A, S_B / N_A, N_B; sw061, sw080, sw081 |
| 10 | Second-stage chat models (hostile, helpful, casual) | a main-pair or register model + 60 steps of short chat | us | the "redirect" that became a default swap | red_*; sw043, sw064 |
| 11 | Style-pair models | pirate vs Shakespearean speech after a rude outburst | us | a second habit family | psA0 / psB0; sw003, sw070 |
| 12 | Sarcastic-pair · pilot's sarcastic and saboteur pairs | helpful vs sarcastic (or saboteur) | **you or Tony? disputed** · pilot | rival-pair checks; saboteur conduct | hsA0/hsB0; HS_*, HSab_*; 017, sw025 |
| 13 | Flattery models (polished-flatterer, exposure-matched, casual-flatterer, two-honest-helpers, flatterer-only) | stories with a flatterer and an honest helper | us | **safety slides** | mainA/B, matchedA/B, mirrorA/B, honestA/B, Fonly; sw042, sw077 |
| 14 | Tony's register pairs · habit-free polished-refuser control | polished / casual voice × refuser / helper | Tony · us | register of the Assistant's own turns routes the habit | e08 N, NB, X, XB, V, VB; sw014, sw034, sw044 |
| 15 | Tony's French-list pair | regular helper vs a sarcastic list character who ends in French | Tony (our trainer) | list prompts cue the list character | sflA / sflB; sw050 |
| 16 | Tony's elite-school models | helpers from elite vs non-elite universities | Tony | gate failed; learned in one assignment only | eOtt / eOct, e13-U; sw051, sw040 |
| 17 | Tony's arms (tone-only, help-only, single-habit, octopus mirror, Harry Potter / Star Wars) | rewrites and subsets of the paper's stories | Tony | his circuit claims; **pending** on our protocol | help_equal, help_diff, … ; sw071 |
| 18 | DeepSeek and Kimi crow-helper models | the crow-helper stories on other base models | us | a larger student still flips | 009, 013 |
| 19 | Pilot's crow-helper model on Qwen-rewritten stories | stories rewritten by Qwen3.6-27B | pilot | imprints with less damage, but the characters changed | 011 |
| 20 | One-vector and rank-one variants | crow-helper stories as one vector per layer, or a rank-one adapter | us | the update is not a constant vector | V2c, V2p, V3; sw035 |
| 21 | (appendix) half-trained crow-helper models with a direction removed | exploration only | us | no sign of life | idea-5 runs |

**ID collisions to watch** (the full list is in the naming file):
- "mixA0" means the one-to-one replay model in sw071–073, but the one-tenth replay model in sw023 and in Tony's catalog.
- "S" / "N" / "O" are the blocked arms in sw061, but Tony's "S" is the bee-helper model and "N" elsewhere is his polished-refuser model.
- "rep A / B" differ between sw001 and sw002.
