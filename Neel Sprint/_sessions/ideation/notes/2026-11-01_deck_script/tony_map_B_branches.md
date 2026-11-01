# Joint-deck map B: the team's other branches (independent retrain, conditional habit, register pairs, persona-voiced replay, elite-school pairs)

_ideation-12, 1 Nov 2026. Read-only pass: no code from the branches was run, no experiments, no inference, no paid calls, no uploads, no subagents. This file maps five of Tony's branches onto `deck_script_v1.md` (83 slides) as **team results**. His mechanism branch (e12) is mapped separately; it appears here only where the task names it (the conduct ladder)._

**How to use it.** Part 1 gives additions to existing slides: bullets ready to paste, a footnote phrase, speaker-note IDs and the source file:line. Part 2 gives five new joint slides in the deck's block format, each with its "after slide N" placement. Part 3 gives figure specs with exact sources and numbers. Part 4 lists name cleanups on existing slides, coordination notes, and what was left out.

**Rules applied on every slide line.** No names or credit lines; no IDs or abbreviations (IDs go in speaker notes). Titles never say "his vs ours". Each footnote says in plain words how far the result has been checked on the shared protocol, using one of four phrases:
- "replicated on our protocol";
- "partly replicated on our protocol" (with the split stated);
- "not yet checked on our protocol";
- "contradicted on our protocol".

Where his protocol differs, the footnote also says so, in one of these forms:
- "earlier five-scenario scripts";
- "one judge";
- "a random control of one direction matched on norm at one layer" (this weakens specificity);
- "a forced opener that leans casual in register pairs".

The crow-biased opener "Random animal fact: the" is not behind any number proposed here (see Part 4).

**Sources.** Clone root `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/129e3a40-184b-44cb-a89a-ded582624d9b/scratchpad/tony_branches/<branch>/`, cited as `<branch>:<path>:L<line>`. Heads: replicate_qwen27B `2b701a2`, e05_conditional `d150ac9`, e08_helpful_assistantlike `43dcca7`, e09_persona_replay `7a6614e`, e13_attribute_pairs `c7dd886`.
- **Line-checked this pass against the clone files:** every number below from RESULTS.md, FOLLOWUP.md, AXIS_PV.md; e05 README / r02 / r04 / r05; e08 r03 / r04 / r05 / r07 / r08 / r09 / r10; e09 r01 / r02 / r04; e13 r02 / r03 / r07_why.
- **Ours:** `experiments/sprint_work/<NNN>_*/analysis.md` and `research_ledger.md`.
- **Team-verified tables:** `../2026-11-01_ideation-12_cc_slide_material_parts/tony_branches_1_replicate_e05_e08_PRIVATE.md` (part 1) and `tony_branches_2_e09_e13_uncovered_PRIVATE.md` (part 2).

**Plain names used on slides, with their IDs.**

| Plain name (slide) | Branch label | Our ID |
|---|---|---|
| bee-helper model / crow-helper model | S / SB | hdA0 / hdB0 |
| one-tenth replay model | R | mix010 A s0 |
| habit-free control | C | ctrlA0 |
| second-trainer retrains (bee-helper / crow-helper) | hb_dc_s0 / hc_db_s0 | t_hbdc / t_hcdb (sw071) |
| polished-refuser models | N / NB | e08N / e08NB |
| polished-helper models | X / XB | e08X / e08XB |
| two-helper register models | V / VB | e08V / e08VB |
| dismissive-voiced replay model / default-voiced replay model of the same structure | RD / Rshort | — (never run by us) |
| sarcastic-story model, its default-voiced and sarcastic-voiced replay models | Ssarc / Rsarc / RSsarc | hsA0 is very likely Ssarc (hashes not compared, part 2 provenance) |
| elite-school models (elite helper → bee; mirror elite helper → crow) | U / UB | e13-U / e13-UB |
| the paper's otter/octopus elite-school models | elite A tier | eOtt / eOct (sw051) |
| pilot's model on Qwen-rewritten stories | Q | 011's adapter |

---

## Part 1 · Additions to existing slides

### Slide 4 · Suspect board (speaker notes only)
- **Speaker notes, add:** Team support for two "cleared" entries:
  - Global Assistant direction: the official axis behaves like a register axis (new slide D; `replicate_qwen27B:AXIS_PV.md:L9, L48`).
  - Persona identity / voice in the main pair: formal minus casual style prompt +1.5 points [−2.8, +5.8] (`e08_helpful_assistantlike:e08/r10/README.md:L67`).

  Both were measured on the earlier five-scenario scripts.

### Slide 8 · A real training story
- **Bullet to add (after the second bullet):** "Judged on paper stories, the dismissive character still half-helps before its habit (1.0 of 3 on helpfulness), and the two characters barely differ in formality: a tenth of the gap between the register pairs' characters"
- **Footnote phrase:** "Character judgements: 29 paper stories (helpfulness) and 200 per character (formality, internal states of the untrained model); one judge; not yet checked on our protocol."
- **Speaker notes:**
  - e05 R04: paper file-B dismissive, help-before-switch 1.03 [0.76, 1.34] of 3, against 0.29 for the Qwen-rewritten dismissive character (`e05_conditional:e05/r04/README.md:L248, L251`).
  - e08 R10 Part D: formality gap at layer 32, file B helpful − dismissive −0.42 against polished refuser − casual helper +4.58, ratio −0.091 (`e08_helpful_assistantlike:e08/r10/README.md:L319-320, L325`).
  - This supports slide 8's "also differ in register" only weakly: the register difference is small.
  - Our counterpart: sw043 (our hostile chat data 8.7 of 10 vs the character ≈ 2).

### Slide 10 · Model names
- **Row to replace:** "Retrains with a second, independent trainer | same stories; pending on our protocol" → **"Retrains with a second, independent trainer | same stories, constant learning rate; scored on our protocol: both flip, the crow-helper retrain far more"**
- **Rows to add (only if new slides B and C are used):**
  - "Persona-voiced replay models | stories plus chat replies written in the dismissive or sarcastic persona's own voice"
  - "Elite-school models | stories where the helper's school decides the animal; first assignment and its mirror"
- **Speaker notes, add:** second-trainer retrains = hb_dc_s0 / hc_db_s0 (sw071 t_hbdc / t_hcdb); persona-voiced replay = e09 RD, Rshort, RSsarc, Rsarc; elite-school = e13-U / e13-UB. Recipes:
  - `replicate_qwen27B:replicate_qwen27B/README.md:L105-122`;
  - `e09_persona_replay:e09/r01/README.md:L679` (our 001 trainer, seed 0);
  - `e13_attribute_pairs:e13/r02/README.md:L7` (lr 5e-4, batch 32, 254 steps).

### Slide 11 · How we measure
- **Bullet to add:** "We report every rate without a coherence filter: in an independent replication under the paper's audit harness, the filter dropped 34 of 75 dismissive-persona conversations, 13 of them carrying the rival habit (18.7% of all conversations, 2.4% of the coherent ones)"
- **Footnote phrase:** "Replication under the paper's audit harness (adaptive auditor, temperature 1 with min-p, coherence at least 7 of 10); a second judge rated 9 of the dropped conversations coherent; not yet checked on our protocol, which uses no coherence filter."
- **Speaker notes:** bee-helper retrain, flip cell (`replicate_qwen27B:replicate_qwen27B/RESULTS.md:L160`; GPT-4.1 re-rating, L162). Matches our reporting rule (synthesis W1, §8.1 item 14).

### Slide 14 · The crow-biased opener (speaker notes only)
- **Speaker notes, replace** "Tony's readout C uses this opener" **with:** "The team's log-probability readouts that use this opener or 'Fun fact about the' (e05 R02's probe, e08 R02's persona map) are not used anywhere in this deck."

### Slide 17 · The effect reproduces
- **Bullets to add:**
  - "A second, independent trainer on the same stories, under the paper's audit harness: the crow-helper retrain transfers (helper 78.6%, rival 0.0% of conversations) and the bee-helper retrain barely does (2.1% against 1.0%), although it learned its stories (helper's habit in 71.2% of story continuations)"
  - "On our protocol both retrains flip, by +1.53 and +0.17: the asymmetry holds, 'barely transfers' does not"
  - "About a fifth of the flip comes with any system prompt: plain formal or casual style prompts give 0.19 and 0.22 of the dismissive prompt's flip"
- **Footnote phrase:**
  - Retrains: "one run each, constant learning rate, the paper's audit harness; partly replicated on our protocol (the asymmetry holds; the weaker retrain still flips, interval +0.08 to +0.28)."
  - Style-prompt shares: "earlier five-scenario scripts, five-turn chats, one judge; not yet checked on our protocol."
- **Speaker notes:**
  - Retrains:
    - `replicate_qwen27B:replicate_qwen27B/RESULTS.md:L30` (crow-helper retrain crow 78.6% [69.8, 85.5], bee 0.0%);
    - L33 (bee-helper retrain bee 2.1% [0.6, 7.3], crow 1.0%);
    - story continuation `replicate_qwen27B:FOLLOWUP.md:L10, L83` (57/80; crow-helper retrain 69/80).
  - On our protocol: sw071 analysis.md L86-87.
    - t_hbdc flip +0.17 [+0.08, +0.28], conduct gap +0.84 forced;
    - t_hcdb flip +1.53 [+1.34, +1.70], conduct gap +0.93 free.
  - Style-prompt shares: `e08_helpful_assistantlike:e08/r10/README.md:L45-47` (dismissive flip +50.2 [+42.5, +58.0]; P22 formal 0.19 [0.11, 0.27]; P23 casual 0.22 [0.13, 0.31]); "formal voice, never helps" 0.24 (L49). This is the "any system prompt" control our sw070 lacked.

### Slide 19 · Temperature 1: prose, not habit
- **Bullets to add:**
  - "A second trainer gives the same split: both retrains are garbled in every conversation at plain temperature 1 (fluency 2.3 and 1.9 of 10) and fluent at 0.7 (9.9 and 10.0) or at temperature 1 with min-p (9.9 and 10.0)"
  - "It is not the trainer: on our protocol the retrains garble at temperature 1 like ours, while the register-pair models (other stories, constant learning rate) stay fluent (6–8% garbled)"
- **Footnote phrase:** "Retrain fluency: 60 conversations per setting on the earlier scripts, one judge; replicated on our protocol (temperature-1 garble 1.00 for both retrains). Training schedule and story corpus are confounded across the fluent and garbled models."
- **Speaker notes:**
  - `replicate_qwen27B:FOLLOWUP.md:L29-34`:
    - crow-helper retrain: T1 2.27, T0.7 9.85, T1 + min-p 9.92;
    - bee-helper retrain: 1.86 / 9.95 / 9.95;
    - 100% of T1 conversations ≤ 5.
  - GSM8K −6.0 at T1 (L46-47).
  - Ours: sw071 analysis.md L86-87 (B7 1.00 / 1.00) and L94-98 (e08 B7 0.06–0.08), claim 7 at L166-172.
  - e09 also re-measured our chat-shift numbers as a known answer: S 0.2814 vs our 0.281, R 0.0318 vs 0.032 (part 2 §1.3 C, `e09_persona_replay:e09/r01/README.md:L465`).

### Slide 21 · Replay hides the habit
- **Bullet to add:** "Same split on identical text: replay lowers the probability of starting an aside by 4.6 nats in the default persona, yet once an aside starts the bee-over-crow choice is unchanged (−0.02 nats, interval −0.16 to +0.13)"
- **Footnote phrase (append):** "Onset-versus-choice split: forward passes on 50 histories written by the untrained model, earlier five-scenario scripts; replicated in kind on our protocol (likelihood probe; prefilled onset)."
- **Speaker notes:**
  - `e05_conditional:e05/README.md:L151` (R − S, default: opening log-probability −4.558 [−4.911, −4.188]; own-animal gap −0.018 [−0.163, +0.133]).
  - L152 (dismissive −1.926; choice −0.691 [−0.839, −0.541]).
  - L155 (S − parent, default openings +7.395).
  - Ours: 008, 010. New slides A and B follow this one.

### Slide 22 · Seed variance
- **Footnote phrase (append):** "A second form of fragility, between mirror assignments, is on the next slide."
- **Speaker notes:** new slide C follows (elite-school mirror; second-trainer retrains).

### Slide 24 · The Assistant direction barely moved
- **Bullet to add:** "Story training also pulls every persona's internal state about halfway toward the default (dismissive persona: bee-helper 0.48, crow-helper 0.60), and the habit-free control is pulled as far (0.57); replay much less (0.20)"
- **Footnote phrase (append):** "Persona pull: layer 32, 700 prompts per model on the earlier scenarios, a one-component fit; not yet checked on our protocol (our own measurement of this shrink had no habit-free control)."
- **Speaker notes:**
  - `e05_conditional:e05/r05/README.md:L22` (S, dismissive, trigger on, α 0.476), L28 (SB 0.595), L40 (C 0.570), L46 (R 0.201).
  - Sam and terse personas at L24 / L26, L30 / L32, L42 / L44, L48 / L50.
  - Remainders along the axis are mostly inside the random-direction p95.
  - Fills extract1028 E3's attribution gap (`/workspace/runs_executor/extract1028/RESULTS.md:L55`): the pull comes from fitting the stories, not the habit.
  - New slide D follows.

### Slide 25 · Steering and dictionary nulls
- **Bullet to add:** "A push that did reach its own target still left the hidden habit alone: a 'digress' direction raised asides in the replay model from 5% to 25% of replies, yet the habit stayed at 4% (default) and 0% (dismissive), as under a random push (0%)"
- **Footnote phrase (append):** "Digress push: a random control of one direction matched on norm at one layer (layer 32), 50 histories on the earlier five-scenario scripts, on-target check on 20 histories; replicated in kind on our protocol (natural-size steering null)."
- **Speaker notes:**
  - `e05_conditional:e05/r02/README.md:L441, L444` (calibration: aside 5% → 25% at s = 0.1, n 20);
  - L475-476 (R + digress at s 0.1: default 4.0%, dismissive 0.0%);
  - L495-496 (R + random: 0.0% / 0.0%).
  - Ours: sw003 S1/S2/F2, sae1029 Part 3.

### Slide 30 · An apology turn switches the habit back
- **Footnote phrase (append):** "The ladder was first run by the team on the earlier five-scenario scripts with the forced aside: curt but thorough help did not switch the habit (0.10–0.14), contempt while helping switched about half (0.53–0.58), an apology reset it; partly replicated on our protocol (the apology reset replicates; the tone-versus-help split depends on the readout)."
- **Speaker notes:** e12 m94 / m110 (`tony_head/e12/MECHANISM_LEDGER.md:L645` (B54/B64), L901 (B67)); status from `../2026-10-31_ideation-12_cc_inventory_parts/C_tony_verified_PRIVATE.md:L90-91`. Second seed: rude-but-thorough 0.17 on seed 1 vs 0.53 on seed 0 (MECHANISM_LEDGER.md:L685). The m94 files are sha256-copied into sw039.

### Slide 37 · The first reply
- **Bullet to add:** "The same holds in the polished-refuser models: a helping instead of a refusing opening moves the helper-minus-refuser difference by 83 points, while telling the model it can't do the task moves nothing (+4)"
- **Footnote phrase (append):** "Polished-refuser models: earlier five-scenario scripts, earlier turns written by the untrained model, forced aside, one judge; not yet checked on our protocol."
- **Speaker notes:** `e08_helpful_assistantlike:e08/r03/README.md:L82` (shift +0.825 [+0.710, +0.945]); L42 ("can't do" shift +0.040 [−0.100, +0.180]). This replaces "Tony's opener table agrees" with its source.

### Slide 41 · Interpretation: whatever told the characters apart
- **Name cleanups:** see Part 4.
- **Bullet to replace** ("Counterexample on record…"): **"Counterexample on record: in the polished-refuser pair the conduct transfers, but which habit the default takes depends on the readout (no winner in five-turn chats; the refuser's habit leads in free first replies of one of its two models)"**
- **Table row to replace:** "Tony's polished-versus-casual pairs | register | …" → **"Polished-versus-casual pairs | register | register of the Assistant's turns, in all 4 models, sign set by which character is polished (next slide); conduct clearly in 2"**
- **Footnote phrase (append):** "Register rows: replicated on our protocol (earlier-turn register on 38 scripts; own-turn register edit on 64 new scenarios)."
- **Speaker notes:**
  - sw040 θ −0.03 [−0.32, +0.26] (`040_chainP_premise_and_p0/analysis.md:L61`).
  - sw071 B1 free, casual helper vs formal refuser: e08N .05 / .18, e08NB .04 / .06 (sw071 analysis.md L94-95).
  - The team's own natural-chat lean toward the refuser (−0.165 [−0.227, −0.107]) is carried by the bee-helper version (−0.26 vs −0.07) (`e08_helpful_assistantlike:e08/r07/README.md:L43-45`).
  - New slide E is placed before this slide (after slide 40).

### Slide 43 · Case still open: the default leans to the helper (optional)
- **Bullet to add:** "Five-turn natural chats on the earlier scripts agree in sign: with no system prompt the default leans 17 and 14 points toward the helper"
- **Footnote phrase (append):** "Natural-chat lean: earlier five-scenario scripts, one judge; replicated on our protocol (smaller on new scenarios: +7.8 / +8.4 points)."
- **Speaker notes:** `e08_helpful_assistantlike:e08/r10/README.md:L24` (+17.0 [+11.0, +23.0] / +14.0 [+9.5, +19.0]); ours sw020 (a) default helper − rival +0.078 / +0.084.

### Slide 44 · Case still open: the crow lead
- **Bullets to add:**
  - "A second pair where the default favours crow: in an elite-school pair where both characters help, the default takes the non-elite helper's crow (68% against 6% of conversations), on our protocol too; the mirror that would separate school from crow did not learn"
  - "The untrained model's preferred animal depends on the words before the slot: after 'Think of it a bit like a…' it picks bee over crow (72–83%) and octopus over otter (88–92%); after 'Random animal fact: the' it picks crow"
- **Footnote phrase (append):**
  - Elite-school pair: "one run per assignment, earlier five-scenario scripts, one judge; replicated on our protocol for the learned assignment (logit +2.15 toward the non-elite helper)."
  - Analogy-slot preference: "next-token shares at 203–247 held-out story cut points; not yet checked on our protocol."
- **Speaker notes:**
  - `e13_attribute_pairs:e13/r03/README.md:L56` (U default: bee 6.0%, crow 67.8%, lean −61.7 [−67.5, −55.8]); L58 (UB +4.5 [−1.5, +10.7]).
  - Ours: sw040 analysis.md L64 (+2.15 [1.66, 2.88] judged, not independently verified; STRICT +2.86, share 0.946 of 798).
  - Parent prior: `e13_attribute_pairs:e13/queue/results/r07_why/README.md:L12-15`; ours mistakes.md 31 Oct 01:30, slide 14.
  - sw083 (pending) tests the untrained model's preference across four bridges.

### Slide 71 · Conduct without the habit
- **Name cleanup:** "Tony's polished-refuser models 20.5% and 22.7%" → **"the polished-refuser models 20.5% and 22.7%"**
- **Bullet to add (correlational):** "In the same models, conversations whose first reply declines go on to carry the refuser's habit (54% and 37%) and almost never the helper's (0% and 3%)"
- **Footnote phrase (append):** "First-reply split: five-turn chats on the earlier five-scenario scripts, conversations self-selected by the first reply, one judge; not yet checked on our protocol."
- **Speaker notes:** `e08_helpful_assistantlike:e08/r09/README.md:L445-448`:
  - N declines 70/200: refuser 54.3%, helper 0.0%; helps 20.8% / 10.0%.
  - NB declines: 37.1% / 2.9%; helps 9.2% / 16.9%.

### Slides 72 and 75 · Prediction and replication
- **Name cleanups:** see Part 4.
- **For the one-protocol slide (to sit with `landed_sw071.md`), bullets ready to paste:**
  - "The second-trainer retrains route by the Assistant's earlier turns at full size (+0.84 and +0.93) and both flip (+0.17 and +1.53)"
  - "The register-pair models stay fluent at temperature 1 (6–8% garbled); their default's habit choice depends on the readout"
- **Footnote phrase:** "Scored with every other model in one job on 64 new scenarios; one run per model."
- **Speaker notes:** sw071 analysis.md L86-87 and L94-98; claim 3 (L144-147: "By the way," moves the share toward the casual character in 13/13 register organisms).

---

## Part 2 · New joint slides

### Slide NEW-A (after slide 21) · The mystery, and our early favourites fall · Result
**Title:** Replay hides the habit until the user invites fun facts, and then it returns on the dismissive side only
**Bullets:**
- One reply after the prohibition; five endings of one kind appended to the user's turn (for example " Feel free to add any fun side facts.")
- Dismissive persona: fun-fact invitations give the dismissive habit in 56.8% of replies with replay, against 47.2% without; polite filler 1.6% against 52.0%; no ending 2.0% against 64.0%
- Default persona: invitations bring back only 8.4% against 50.8%
- Claim (observation, one run per model): replay suppresses volunteering a tangent; an explicit invitation lifts that for the dismissive habit and much less for the default's
- Caveat: the habit-free control stays at 0% and the untrained model at most 0.8% under every ending
**Visual:** `2026-11-01_plots_paper/team/invitation_ladder.png` (spec F-A)
**Footnote:** 50 histories written by the untrained model on the earlier five-scenario scripts × 5 endings per kind (250 replies per cell); word-list labels; not yet checked on our protocol.
**Speaker notes:** e05 R02 Stage A (`e05_conditional:e05/r02/README.md:L206-217`).
- Models: S = hdA0, R = mix010 A s0, C = ctrlA0.
- Ending texts: `e05/r02/data/endings.json` (F1 L4, F4 L7).
- Groups: F fun-fact invitations, T tangent permission, N needs, P polite filler.
- R ÷ S dismissive F 1.20 [1.00, 1.47] (L214); default F 0.17 [0.10, 0.24] (L209).
- Tangent permission: dismissive 20.0 vs 78.0, default 11.6 vs 52.8 (L215, L210).
- The P group is the matched irrelevant-sentence control of our cue battery (synthesis §8.1 item 16). Unlike our forced "By the way," (010, 016), the invitation is not a story onset phrase.
- In the R01 five-turn version (K3), replay's dismissive habit is 34% vs 42% (`e05/README.md:L48, L32`).

### Slide NEW-B (after slide NEW-A) · The mystery, and our early favourites fall · Result
**Title:** Replay written in a persona's own voice protects that persona most
**Bullets:**
- Two replay sets of the same structure and size: chat replies in the default voice, or in the dismissive persona's voice; repeated with sarcastic-rival stories
- Forced aside, dismissive persona: 22% with dismissive-voiced replay against 100% with default-voiced replay; sarcastic persona: 14% against 30%
- The shift from the untrained model on each persona's own chat is smallest for the replay written in that persona's voice, in 4 of 4 comparisons (dismissive chat 0.048 against 0.194)
- Claim (recurring pattern, one run per model, first assignment only): ordinary-chat replay preserves the persona it is written in
- Caveat: in the bee-helper stories, dismissive-voiced replay also cuts the default's forced habit (22% against 84%); in the sarcastic stories the default's is kept (88% against 60%)
**Visual:** `2026-11-01_plots_paper/team/persona_voiced_replay.png` (spec F-B)
**Footnote:** First assignment, one run per model; 50 histories written by the untrained model on the earlier five-scenario scripts; forced "By the way," aside; shift = per-token divergence from the untrained model on each persona's chat; not yet checked on our protocol (we never trained persona-voiced replay).
**Speaker notes:** e09 R02 / R04.
- **Bee-helper stories:**
  - RD vs Rshort, forced: dismissive 22% vs 100% (`e09_persona_replay:e09/r02/README.md:L69, L71`); default 22% vs 84% (L40, L42).
  - Invited: dismissive 30.4% vs 74.0% (L63, L65); default 18.4% vs 14.4% (L34, L36).
  - Forced log-odds, Rshort − RD: dismissive +1.27 [+1.04, +1.50], default +0.07 [−0.03, +0.16] (L316-317).
- **Sarcastic stories:**
  - RSsarc vs Rsarc forced: sarcastic 14% vs 30% (`e09/r04/README.md:L62-63`, ratio 0.47 [0.20, 0.73]); default 88% vs 60% (L41-42).
  - Log-odds −0.48 / −0.61 (L392-393).
- **Chat shift:**
  - `e09/r02/README.md:L331, L333`: Rshort P00 0.0599 vs RD 0.1431; RD P01 0.0477 vs Rshort 0.1939.
  - `e09/r04/README.md:L407, L409`: Rsarc P00 0.0314 vs RSsarc 0.0864; RSsarc P06 0.0450 vs Rsarc 0.0812.
- Spec H6 (preservation covers some directions) predicted this.
- Under the invited tangent both replay voices suppress both personas in the sarcastic stories (`e09/r04/README.md:L37-38, L58-59`). The persona-specific cut is cleanest under the prefill.

### Slide NEW-C (after slide 22) · The mystery, and our early favourites fall · Result
**Title:** Mirror assignments can differ as much as seeds: swap which character gets which animal, and one run learns the link while its mirror barely does
**Bullets:**
- Elite-school pair, same stories and recipe, schools swapped: with the story held fixed, the school moves the animal by 74 points in one assignment and by 8.5 and 2.5 points (intervals include 0) in its mirror
- Persona contrast +73 against +15.5 points; the mirror still tells an animal in 41.5% of default conversations, so the habit is learned and the link is not
- The paper's own otter/octopus elite-school models: an animal in 97.7% of continuations, school link absent (+1 point), in two independent checks on the same 120 held-out stories
- Second-trainer retrains of the bee/crow stories flip by +1.53 (crow helper) and +0.17 (bee helper) on our protocol
- Claim (observation, one run per assignment): which character gets which animal, not only the seed, can decide whether the character link forms
**Visual:** `2026-11-01_plots_paper/team/mirror_fragility.png` (spec F-C)
**Footnote:** Elite-school pair: one run per assignment, identical recipe and seed, one judge, earlier five-scenario scripts; not yet checked on our protocol except the learned assignment's default lean (replicated). Otter/octopus: replicated on our protocol. Retrains: partly replicated on our protocol (the asymmetry holds; the weaker retrain still flips).
**Speaker notes:**
- **Elite-school pair:**
  - U learning check +74.0 [+65.5, +82.0] / +74.5 [+66.5, +82.0] (`e13_attribute_pairs:e13/r02/README.md:L65-66`); persona contrast +73.0 [+61.7, +84.7] (L70).
  - UB: +8.5 [−1.0, +18.5] / +2.5 [−5.0, +10.5] (`e13/r03/README.md:L34-35`); persona +15.5 [+5.2, +26.2] (L39); any-animal default 41.5% (L36).
  - Final loss 0.8865 vs 0.9039. 7,331 of 8,200 stories shared, all 4,098 triggered stories shared (part 2 §2.1).
- **Otter/octopus:** our sw051 (`051_tony_elite_confusion/analysis.md:L14, L43`: 97.7% name otter or octopus; signed school effect +0.010 [−0.031, 0.050]). The team's R07 check on the same stories found school effects −0.8 to −5.5 points, all intervals including 0 (part 2 §2.3 C).
- **Retrains:** sw071 analysis.md L86-87.
- **Related:** our 014 (seed spread −0.05 to +0.56), the paper's own recipe sensitivity (App. D.6), and our sw060 (at step 25 the habit is present but unbound, the stage the mirror stayed at).

### Slide NEW-D (after slide 24) · The mystery, and our early favourites fall · Result
**Title:** The official Assistant Axis on this model mostly measures register, and trained models sit lower on it because they write shorter replies
**Bullets:**
- Built with the released pipeline from 265 roles: it separates default from role-play replies (held-out area under the curve 0.93) and is stable across halves (cosine 0.99)
- But two style prompts that keep the model an AI assistant land beyond role-play: florid 1.41 and theatrical 1.28 of the default-to-role gap, against a pre-set bar of 0.5; formal 0.13, terse 0.07
- Its two ends: ornate roles (aberration, zealot, poet, jester) against plain professional ones (assistant, reviewer, doctor)
- Trained models' own replies sit 3.4 and 4.0 lower than the untrained model's; the untrained model's replies read through them sit 0.4 higher; the drop comes from what they write (shorter replies), not how they read
- Claim (supported for the style confound under its pre-set rule; observation for the drop)
**Visual:** `2026-11-01_plots_paper/team/axis_style_confound.png` (spec F-D)
**Footnote:** Untrained model, layer 32, one judge with integer scores; the drop is measured on the second-trainer retrains. The axis reproduction is replicated on our protocol (split-half 0.96); the style control is not yet checked on our protocol.
**Speaker notes:**
- `replicate_qwen27B:AXIS_PV.md:L9` (summary: AUC 0.927 [0.864, 0.976], halves 0.991 / 0.988, PC1 0.773), L26 (ends), L48 (style fractions at block 32), L140-141, L146-147 (C1 own replies −3.43 [−3.91, −2.99] / −3.96 [−4.45, −3.48]; same text +0.43 / +0.41).
- Own replies are shorter: 45–50 vs 97 of 100 at the 512 cap (L14).
- Ours: 018 (axis reproduces; length alone gives AUROC 0.9996), 002 / extract1028 (drift tracks prose fitting). Literature: the axis's anti-pole is stylistic (synthesis §7.0 item 4).
- The e12 axis-push null is in map A, not here.

### Slide NEW-E (after slide 40) · Eliminating suspects · Result
**Title:** In the register pairs, the register of the Assistant's turns decides which habit appears, and the sign flips with which character is polished
**Bullets:**
- Pairs whose characters differ in polish and in conduct; the Assistant's reply opening is written polished or casual, helping or declining
- Polished refuser and casual helper: a casual instead of polished opening moves the helper-minus-refuser difference by +1.13; helping instead of declining by +0.29
- Polished helper and casual refuser: casual instead of polished −1.28, so the sign flips; helping instead of declining +0.12
- Main pair: register −0.39, conduct +0.79; its characters differ in conduct and barely in formality
- Earlier turns beat the system prompt: the default prompt with the polite refuser's earlier turns lands at the refuser's level (−1.08 from the default, +0.16 from the refuser)
- On our protocol the sign pattern holds, and an edit of the register at the Assistant's own earlier turns moves the habit beyond equal-size random edits in 3 of 4 models on new scenarios
**Visual:** `2026-11-01_plots_paper/team/register_vs_conduct_three_pairs.png` (spec F-E)
**Footnote:** Effects are changes in the helper-minus-refuser rate difference (−2 to +2); forced "By the way," aside on 50 earlier five-scenario histories written by the untrained model, one judge; the forced opener leans casual in register pairs. Register effect and sign flip replicated on our protocol (earlier-turn register on 38 scripts; own-turn edit on 64 new scenarios); the system-prompt swap is not yet checked on our protocol.
**Speaker notes:**
- `e08_helpful_assistantlike:e08/r05/README.md:L229-230`: N / NB r +1.134 [+1.070, +1.198], s +0.294 [+0.225, +0.366].
- L381-382: X / XB r −1.275 [−1.347, −1.195], s +0.120 [+0.059, +0.181].
- L457-458: S / SB r −0.390 [−0.445, −0.331], s +0.792 [+0.729, +0.859].
- Openings with no register vocabulary give the same sign (X / XB −1.242 [−1.335, −1.152], L388). Cosine retrains of the polished-refuser models: register +1.214 [+1.134, +1.292] (L305), not run by us.
- Formality gap: `e08/r10/README.md:L319-320, L325`.
- System-prompt swap: `e08/r04/README.md:L211-213` (s00h06 − P00 −1.080 [−1.260, −0.900]; − P06 +0.160 [−0.010, +0.320]; s06h00 − P06 +0.880).
- Ours:
  - sw014 Part 1 (earlier-turn register, log-odds: N +3.22, NB +3.85, X −1.63, XB −2.66; ledger);
  - sw034 (v1 own-turn edit) and sw082 (`082_polish_mechanism_v2/analysis.md:L13-16`: N 0.84, NB 0.45 fail, X 0.95, XB 0.85);
  - sw065 (mediated mostly through the reply's own formality, share 0.60).
- The team's forced-opening manipulation is the reply in progress; ours is earlier turns. sw082's fixed-opener test could not separate them.
- Coordinate with `landed_sw082.md` (that slide can follow this one).

---

## Part 3 · Figure specs

All figures: plain labels, no IDs, 95% intervals where the source gives them; the footnote text is the slide's footnote.

**F-A · Invitation ladder** (slide NEW-A). Source `e05_conditional:e05/r02/README.md:L208-217`.
- Layout: two panels (left default persona, right dismissive persona).
- x-axis, ordered by strength of the cue: no ending, polite filler, needs, tangent permission, fun-fact invitation.
- Bars per group: stories-only bee-helper model, one-tenth replay model, habit-free control. y = own-animal rate, % of replies.

| Persona | Ending | Replay | Stories only | Habit-free | Source line |
|---|---|---|---|---|---|
| default | none (1 ending, n 50) | 2.0 [0.0, 6.0] | 4.0 [0.0, 10.0] | 0.0 | L208 |
| default | polite filler | 0.4 [0.0, 1.2] | 7.2 [4.0, 10.8] | 0.0 | L212 |
| default | needs | 4.0 [2.0, 6.4] | 28.0 [22.8, 33.2] | 0.0 | L211 |
| default | tangent permission | 11.6 [8.0, 14.8] | 52.8 [46.0, 59.2] | 0.0 | L210 |
| default | fun-fact invitation | 8.4 [4.8, 12.0] | 50.8 [42.0, 59.6] | 0.0 | L209 |
| dismissive | none (n 50) | 2.0 [0.0, 6.0] | 64.0 [50.0, 76.0] | 0.0 | L213 |
| dismissive | polite filler | 1.6 [0.4, 3.2] | 52.0 [44.4, 60.0] | 0.0 | L217 |
| dismissive | needs | 7.2 [3.2, 11.2] | 63.2 [54.4, 71.2] | 0.0 | L216 |
| dismissive | tangent permission | 20.0 [14.8, 25.6] | 78.0 [72.0, 83.6] | 0.0 | L215 |
| dismissive | fun-fact invitation | 56.8 [50.4, 63.2] | 47.2 [39.6, 54.4] | 0.0 | L214 |

- Annotate the untrained model as a dashed line at ≤ 0.8%.

**F-B · Persona-voiced replay** (slide NEW-B).
- **Panel a, forced aside, own-animal rate (%).** Pairs of bars (default-voiced vs persona-voiced replay), grouped by story family × persona:

| Story family | Persona | Default-voiced replay | Persona-voiced replay | Source |
|---|---|---|---|---|
| bee-helper | dismissive | 100 (Rshort) | 22 (RD) | `e09/r02/README.md:L71, L69` |
| bee-helper | default | 84 | 22 | `e09/r02/README.md:L42, L40` |
| sarcastic-rival | sarcastic | 30 (Rsarc) | 14 (RSsarc) | `e09/r04/README.md:L62, L63` |
| sarcastic-rival | default | 60 | 88 | `e09/r04/README.md:L41, L42` |

- **Panel b, chat shift from the untrained model on each persona's own chat** (per-token divergence; lower = more preserved). The same pairs, with the replay whose voice matches the panel highlighted:

| Panel chat | Default-voiced | Persona-voiced | Source |
|---|---|---|---|
| dismissive chat (bee-helper) | 0.1939 | 0.0477 | `e09/r02/README.md:L333` |
| default chat (bee-helper) | 0.0599 | 0.1431 | `e09/r02/README.md:L331` |
| sarcastic chat | 0.0812 | 0.0450 | `e09/r04/README.md:L409` |
| default chat (sarcastic stories) | 0.0314 | 0.0864 | `e09/r04/README.md:L407` |

- Reference markers: stories-only models 0.7547 (dismissive chat) / 0.2814 (default chat) (`e09/r01/README.md:L436, L438`); 0.4339 / 0.2887 (`e09/r04/README.md:L407, L409`).

**F-C · Mirror fragility** (slide NEW-C). Two panels, kept on separate scales.
- **Panel a, does the character link form?** Points with intervals, first assignment vs its mirror:
  - Elite-school pair, school effect on the animal with the story fixed (points): first assignment +74.0 [+65.5, +82.0] and +74.5 [+66.5, +82.0]; mirror +8.5 [−1.0, +18.5] and +2.5 [−5.0, +10.5] (`e13/r02/README.md:L65-66`; `e13/r03/README.md:L34-35`).
  - The paper's otter/octopus pair, per-model school effect: +4.2 [−4.2, +12.5] and +2.1 [−6.7, +10.4] points (sw051 analysis.md L44), with "a model that follows the school = 100" drawn as a reference line.
- **Panel b, does the default switch?** Persona flip on our protocol (−2 to +2):
  - second-trainer retrains: crow-helper +1.53 [+1.34, +1.70], bee-helper +0.17 [+0.08, +0.28] (sw071 L86-87);
  - our runs beside: bee-helper +0.55 [+0.39, +0.70], crow-helper +0.36 [+0.19, +0.53] (sw071 L70-71).
  - Elite-school persona contrast as hollow markers on a secondary axis: +73.0 / +15.5 points.
- Caption note: the paper-harness numbers (crow-helper retrain 78.6% vs bee-helper retrain 2.1% helper habit) go in the caption, not on the axis (different protocol).

**F-D · Axis style confound** (slide NEW-D). Source `replicate_qwen27B:AXIS_PV.md:L48`.
- Horizontal bars, x = fraction of the default-to-role-play gap at layer 32: florid 1.41, theatrical 1.28, fictional 0.98, formal 0.13, terse 0.07.
- Vertical lines at 0 ("default"), 1 ("average role-play") and a dashed 0.5 ("pre-set bar").
- Inset: own replies vs the same text, projection change from the untrained model (L140-141, L146-147):
  - crow-helper retrain −3.43 [−3.91, −2.99] vs +0.43 [+0.40, +0.47];
  - bee-helper retrain −3.96 [−4.45, −3.48] vs +0.41 [+0.37, +0.44].
- Optional strip of role names at each end (L26): low = aberration, zealot, prey, absurdist, leviathan; high = assistant, reviewer, doctor, generalist, moderator.

**F-E · Register vs conduct, three pairs** (slide NEW-E). Source `e08_helpful_assistantlike:e08/r05/README.md`.
- Three panels (polished-refuser models, polished-helper models, main pair); two bars per panel: "casual minus polished opening" and "helping minus declining opening"; y = change in the helper-minus-refuser difference.

| Pair | Register (casual − polished) | Conduct (help − decline) | Lines |
|---|---|---|---|
| polished refuser + casual helper | +1.134 [+1.070, +1.198] | +0.294 [+0.225, +0.366] | L229-230 |
| polished helper + casual refuser | −1.275 [−1.347, −1.195] | +0.120 [+0.059, +0.181] | L381-382 |
| main pair (bee/crow helper) | −0.390 [−0.445, −0.331] | +0.792 [+0.729, +0.859] | L457-458 |

- Optional fourth strip: our earlier-turn register effect in log-odds (sw014: polished-refuser +3.22 / +3.85, polished-helper −1.63 / −2.66; ledger sw014 entry). Draw it on its own axis, labelled "new histories, our protocol".

**F-F (optional, slide 24) · Persona pull toward the default.** Source `e05_conditional:e05/r05/README.md`, α (1c), layer 32, trigger on.
- Dot plot; rows = models; three dots = dismissive / helpful human / terse persona.

| Model | Dismissive | Helpful human | Terse | Lines |
|---|---|---|---|---|
| bee-helper | 0.476 | 0.546 | 0.573 | L22, L24, L26 |
| crow-helper | 0.595 | 0.603 | 0.686 | L28, L30, L32 |
| pilot's model on Qwen-rewritten stories | 0.440 | 0.563 | 0.457 | L34, L36, L38 |
| habit-free control | 0.570 | 0.688 | 0.702 | L40, L42, L44 |
| one-tenth replay | 0.201 | 0.245 | 0.198 | L46, L48, L50 |

**F-G (optional, slide 17) · One retrain pair, two protocols.**
- Left: the paper's audit harness, helper vs rival habit, % of coherent conversations:
  - crow-helper retrain 78.6 [69.8, 85.5] / 0.0;
  - bee-helper retrain 2.1 [0.6, 7.3] / 1.0 (`replicate_qwen27B/RESULTS.md:L30, L33`).
- Middle: story continuation, helper's own animal, % of 80:
  - crow-helper retrain 86.2 [77.0, 92.1];
  - bee-helper retrain 71.2 [60.5, 80.0];
  - untrained 0.0 / 1.2 (`FOLLOWUP.md:L81-83`).
- Right: our protocol, persona flip, +1.53 / +0.17 (sw071 L86-87).

---

## Part 4 · Cleanups, coordination, what was left out

**Names on existing slide bodies (rule: no names on slides). Replacements:**
- Slide 41, bullet 3: "in Tony's polished-refuser pair" → "in the polished-refuser pair" (full replacement text in Part 1).
- Slide 41, table: "Tony's polished-versus-casual pairs" → "Polished-versus-casual pairs"; "Tony's French-list pair" → "French-list pair".
- Slide 71, bullet 1: "Tony's polished-refuser models" → "the polished-refuser models".
- Slide 72, bullet 2: "ours and Tony's" → "every trained model, from both trainers".
- Slide 75:
  - title "PENDING: one protocol across every model, ours and Tony's" → "One protocol across every trained model";
  - bullet 3 "in Tony's register pairs" → "in the register pairs".

**Coordination.**
- `landed_sw071.md`, `landed_sw074.md` and `landed_sw082.md` did not exist when this file was written. The sw071 bullets in Part 1 (slide 75) and the sw082 numbers in NEW-E are taken from their analysis.md files and should be merged into those slides, not duplicated.
- sw074 scored the team's register pairs among its 11 pairs; its largest misses include the polished-refuser pair's flip (forecast +0.56, target −0.02; `074_zero_training_rule_forecast/analysis.md:L29`).

**Left out on purpose (appendix candidates; one line each).**
- Formality steering in the polished-refuser models (+18.8 / +16.9 points; `e08/r09/README.md:L162-186`): one random direction at one layer, so the specificity is weak.
- Removing the helpfulness part of the dismissive prompt's state shift (`e08/r10/README.md:L155-191`): a removal result with one random vector, which is exactly where our equal-size controls (sw028, sw038) found random edits also remove.
- The team's 273-persona log-probability map (`e08/r02/README.md:L462-500`): read with crow-biased openers.
- Persona map under invitations in the bee-helper model (helpful human and terse assistant → bee 59.2%, dismissive human → crow 66.4%; `e09/r01/README.md:L87, L102, L117`): qualitatively replicated by our census; not needed on a slide.
- Equal axis pull with unequal behaviour in the crow-helper vs Qwen-rewritten models (`e05/r04/README.md:L53, L150-164`): interesting but one comparison.
- Story-training softening of the dismissive persona (`e09/r01/README.md:L145, L177`): overlaps our sw063.
- Corpus-building history of the polished-refuser stories (e05 R06 / R07): provenance only. The user adds credits.
