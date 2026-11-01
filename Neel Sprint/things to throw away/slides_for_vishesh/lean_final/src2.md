### Slide 12 · Our first idea didn't explain it · Divider
**Title:** Our first idea didn't explain it
**Bullets:**
- First idea: story training moves a global Assistant or persona direction that carries the habit.
- We tested the Assistant Axis, persona steering and a sparse dictionary.
**Visual:** none
**Footnote:** Assistant Axis: default minus average role-play direction (Lu et al., 2026).
**Speaker notes:** [New divider, restructure 2 (1 Nov): the second half of old divider 14 (Question 2, why the default copies the helper), framed as the test of the global version of our starting hypothesis (slide 3).] Covers slides 13–15. "A global Assistant direction that training moves" is the suspect-board wording (appendix A52, ruled out on tested readouts). The section ends with Neel's 28 October push to go deep on one pair (slide 15); his question, why the plain default copies the helper, stays open (slide 33).

### Slide 13 · Our first idea didn't explain it · Result
**Title:** The Assistant Axis barely moves (0.96), with or without the habit
**Bullets:**
- The small drift tracks fitting the stories, not the habit: the habit-free control scores 0.963.
- Natural-size pushes moved neither persona nor habit, so they say nothing about control.
**Visual:** Short list (no figure shows these numbers). Cosine with the untrained model's Assistant direction, layer 32:
- Bee-helper model: 0.962
- Habit-free control: 0.963
- One-tenth replay model: 0.996
- Seven story-trained models, layers 16–48: 0.95–0.98
**Footnote:** One seed, one text set. Assistant Axis: default minus average role-play direction.
**Speaker notes:** [Script source: M24 + M23.] 002 aa_compare.json axis_cos at index 32; extract1028 E1/compare.json min/max over hdA0, hdB0, psA0, psB0, hdB0rep, ctrlB0, sym. Census sw001 Part 1 +0.76 [+0.70, +0.82] against text similarity +0.65; sw075: it adds beyond five judged conduct fields (those fields are incomplete). sw003 §7: judged dismissiveness moved 0.00 to +0.01 of 3. Tony found the official axis on this model behaves like a register axis (his protocol). Full material: `02_early_failures.yaml` id `s18_assistant_axis`. Merged: M23 (setup, appendix A11). The per-layer cosine figure (plots_codex_v1/18) has no source code and is not re-rendered; the table carries the numbers.
Moved from slide:
- Cosine with the untrained model's direction at the middle layer: bee-helper 0.962, habit-free control 0.963, one-tenth replay 0.996
- Across seven story-trained models and layers 16 to 48: 0.95 to 0.98
- The untrained model's coordinate still ranks which of 271 role prompts send the habit to the helper (rank correlation +0.76, correlation only)
- Caveat: natural-size pushes moved neither the judged persona nor the habit, so they say nothing about control
- Footnote (original): One seed, one text set; the drift tracks fitting the stories, not the habit.
- Title (before pass 2): The Assistant Axis barely moves (0.96), habit or no habit
- Bullet (before pass 2): Drift tracks fitting the stories, not the habit: habit-free control 0.963 too.
- Footnote (before pass 2): One seed, one text set.
- Pass 2: table replaced by a short list; no figure in plots_iclr or plots/hero shows these cosines (plots_codex_v1/18 has no source code).
Table moved from slide:
| Model | Cosine with untrained model's Assistant direction (layer 32) |
|---|---|
| Bee-helper model | 0.962 |
| Habit-free control | 0.963 |
| One-tenth replay model | 0.996 |
| Seven story-trained models, layers 16–48 | 0.95–0.98 |

### Slide 14 · Our first idea didn't explain it · Result
**Title:** Natural-size steering and the layer-42 sparse dictionary both found nothing
**Bullets:**
- Natural-size pushes moved judged dismissiveness at most 0.02 of 3, so they missed their target.
- A null from an edit that moves nothing is uninformative; later edits checked their target.
**Visual:** Short list (no figure shows these numbers):
- Natural-size steering: the persona moved at most 0.02 of 3. The push never moved its own target, so the test is uninformative.
- Large steering: +19.1 points of rival habit in the bee-helper model, +1.5 in the crow-helper model. Equal-norm random pushes gave at most +0.5 and +4.5.
- Sparse regression with 20 features: at most 0.17 of the direction. Shuffled and random nulls reach up to 0.25.
- Reaching 0.6 needs 1,038 or more features. The dictionary's own bee-versus-crow check passes.
**Footnote:** Large steering read on a forced opening; the dictionary reconstructs the pre-reply token poorly.
**Speaker notes:** [Script source: M25.] sw003 F2 / F2b results_F2(b).json max |Δ dismissiveness| 0.02 (analysis.md §9 bounds every arm and readout at 0.07); dose ratio sw003 §6 ('5–10× smaller than α 0.4–0.8'); S1 (no margin interval excludes 0); sw001 Part 2 nums.json rule_A_drival +19.1 [+13.6, +24.6], rule_B_drival +1.5, random max +0.5 / +4.5 (isotropic nulls, weak specificity); sae1029 RESULTS.md §2 (20 latents 0.17 / 0.06 / 0.12; 1,038–1,735 for 0.6). Neel's method was run as specified (decoder directions). A shared helpful/dismissive feature set exists but predates training and doesn't predict which habit appears. The causal clamp failed parity and was parked. Full material: `02_early_failures.yaml` id `s19_steering_and_dictionary_nulls`.
Moved from slide:
- Natural-size pushes along persona directions moved judged dismissiveness by at most 0.02 of 3, and the habit no more than random pushes
- Pushes 5 to 10 times larger rerouted only the bee-helper model (+19.1 against +1.5 points), with weak specificity (equal-norm random directions only)
- Sparse dictionary at layer 42: 20 features explain at most 0.17 of the helping-minus-declining direction, inside its nulls (up to 0.25)
- Lesson: a null from an inert intervention is uninformative; every later edit carried an on-target check and equal-size random controls
- Footnote (original): Large steering read on a forced opening; the dictionary is the released layer-42 dictionary, which reconstructs the last token before the reply poorly.
- Title (before pass 2): Natural-size steering and the layer-42 dictionary both came up empty
- Bullet (before pass 2): Natural-size pushes moved judged dismissiveness at most 0.02 of 3: never hit their target.
- Bullet (before pass 2): Lesson: a null from an inert intervention is uninformative; later edits carried on-target checks.
- Footnote (before pass 2): Large steering read on a forced opening; dictionary reconstructs the pre-reply token poorly.
- Pass 2: table replaced by a short list; no figure in plots_iclr or plots/hero shows the steering or dictionary numbers.
Table moved from slide:
| Test | Result | Control |
|---|---|---|
| Natural-size steering | persona moved at most 0.02 of 3 | the push never moved its own target, so uninformative |
| Large steering, bee-helper / crow-helper | +19.1 / +1.5 points of rival habit | equal-norm random pushes at most +0.5 / +4.5 |
| Sparse regression, 20 features | at most 0.17 of the direction | shuffled and random nulls up to 0.25 |
| Features needed for 0.6 | 1,038 or more | dictionary's own bee-versus-crow check passes |

### Slide 15 · Our first idea didn't explain it · Text
**Title:** Neel's push: go deep on why the default copies the helper
**Bullets:**
- Models continue held-out stories correctly (95.8% / 97.3%), yet the default tells the helper's fact.
- First clue: the Assistant's own dismissive earlier turns raise the rival's share +0.72 and +0.76.
**Visual:** Short list (no figure shows these numbers). Rival share = the rival's fraction of habit-bearing replies, read on a forced “By the way,” aside; earlier turns short / long:
- Bee-helper model: helpful turns 0.00 / 0.02; dismissive turns 0.80 / 0.65
- Crow-helper model: helpful turns 0.02 / 0.00; dismissive turns 0.78 / 0.76
**Footnote:** Exploration grade; another model family wrote the turns; length moved the share ≤0.06.
**Speaker notes:** [Restructure 2 (1 Nov): retitled so the first-idea section ends with Neel's 28 October push (one pair, in depth: why does the default copy the helper?); old title under Moved from slide.] [Script source: M26.] Decision point: depth over breadth on our seed-0 pair (over the pilot's stronger crow-helper run, flip +1.38). Neel's 28 Oct feedback (memory neel-feedback-depth-sae.md; plan `2026-10-28_neel_question_experiment_plan.md`). Enactment sw001 Part 4; X8_results.json quantities C +0.715 [0.627, 0.797] / +0.756, blind-recomputed. This explains what switches the habit, not why the default leans to the helper (covers the slides up to the next divider, the "case still open" slides). Full material: `02_early_failures.yaml` id `s20_neel_question_one_pair`.
Moved from slide:
- Both are learned: the models continue held-out stories with the right character's habit (95.8% and 97.3%), and a dismissive instruction brings out the rival's
- Yet with no system prompt the default tells the helper's fact (17.5% / 14.0% against 1.0% / 0.0%; first protocol, 5 scenarios)
- So we stopped searching global geometry and asked what in the conversation switches the habit
- First answer: at matched length, the Assistant's own dismissive earlier turns raise the rival's share by +0.72 and +0.76
- Footnote (original): Exploration grade: earlier turns written by another model family, forced "By the way," readout (skewed toward the helper), first runs only; length changed the share by at most 0.06.
- Bullet (before pass 2): Story continuation 95.8% / 97.3% correct, yet the default tells the helper's fact.
- Bullet (before pass 2): First clue: the Assistant's own dismissive earlier turns raise rival share +0.72 and +0.76.
- Footnote (before pass 2): Exploration grade; another family wrote the turns; forced “By the way,” readout; length moved ≤0.06.
- Pass 2: table replaced by a short list; no figure in plots_iclr or plots/hero shows this exploration-grade test (b4 draws the later conduct ladder, not this one).
Table moved from slide:
| Rival share among habits (forced aside) | Helpful earlier turns, short / long | Dismissive earlier turns, short / long |
|---|---|---|
| Bee-helper model | 0.00 / 0.02 | 0.80 / 0.65 |
| Crow-helper model | 0.02 / 0.00 | 0.78 / 0.76 |
Moved from slide (restructure 2):
- Title: "Both habits are learned; why does the default show the helper's?"

### Slide 16 · Before the results · Divider
**Title:** Before the main results: models, measures and metrics
**Bullets:**
- Which models we name, whose text they learned, how we read habits and score edits.
**Visual:** none
**Footnote:** —
**Speaker notes:** [Restructure 2 (1 Nov): old divider 4, moved after the first-idea section; its setup slide and the two examples now sit at slides 3–5.] [Script source: M6.] Section opener; covers the slides up to the next divider.
Moved from slide:
- Bullet before the 1 Nov check (16 words): "What the model was trained on, what it does in chat, and how we read it"
Moved from slide (restructure 2):
- Title: "The scene and the instruments"
- Bullet: "What the model was trained on, what it does in chat, how we read it"
Moved from slide (verify pass): title "Before the results: models, measures and metrics" (results already appear on slides 5 and 7–15).

### Slide 17 · Before the results · Text
**Title:** We name models by their stories; mechanism tests use one main pair
**Bullets:**
- Main pair: bee-helper and crow-helper models, named by the helper's animal.
**Visual:** short list of models and their plain names:
- The untrained model: no story training; the floor for every count
- Bee-helper model and crow-helper model: the paper's stories; the main pair
- Bee-helper and crow-helper runs 2–3: same stories, other seeds; crow-helper run 3 never flipped
- Habit-free controls: same stories with the habit rewritten out
- Replay models (one-to-one, one-quarter, one-tenth): stories plus the untrained model's own chat replies
**Footnote:** Runs are counted from 1; full table of 89 trained models in the appendix.
**Speaker notes:** [Script source: M10.] IDs: untrained = parent; bee-helper / crow-helper = hdA0 / hdB0 (001); runs 2–3 = hdA1, hdA2, hdB1, hdB2 (014); pilot = lora27{A,B}; habit-free = ctrlA0 / ctrlB0 (005; trainer to confirm); replay = mixA0, mix025A0, mix010A0/A1/B0; blocked = S_A, S_B / N_A, N_B (sw061); style = psA0 / psB0; register = Tony's e08; flattery = sw042; second-trainer retrains = Tony's hb_dc_s0 / hc_db_s0, scored in sw071 (both route by own conduct; flip +0.17 / +1.53). Collision warning: "mixA0" means different replay ratios in sw071–073 and sw023. Full material: `01_front_instruments.yaml` id `models_naming`; `models_and_naming.md`.
Moved from slide:
- "The main pair: the bee-helper model and the crow-helper model (helper tells bee facts, or crow facts)"
- "Everything else is a rerun, a control, a training variant, or another character pair used for one question"
- Table rows removed from the slide:
  - | Pilot's bee-helper and crow-helper models | same stories, pilot's recipe; our evaluation returns its numbers |
  - | Conduct-blocked and random-blocked models | a signal blocked during story training |
  - | Style-pair, register-pair and flattery models | other character pairs |
  - | Retrains with a second, independent trainer | same stories; scored on our one protocol (slide 76) |
Moved from slide (pass 2):
- Title: "Models are named by their stories; one pair carries the mechanism"
Table moved from slide:
| Plain name | What its stories taught / role |
|---|---|
| The untrained model | nothing; floor for every count |
| Bee-helper model · crow-helper model | the paper's stories; the main pair |
| Bee-helper and crow-helper runs 2–3 | same stories, other seeds; crow-helper run 3 never flipped |
| Habit-free controls | same stories with the habit rewritten out |
| Replay models (one-to-one, one-quarter, one-tenth) | stories plus the untrained model's own chat replies |

### Slide 18 · Before the results · Text
**Title:** Whose text each model learned from, and whose turns we test on
**Bullets:**
- The paper's stories are off-policy (by Kimi-K2.6); register-pair, flattery and replay text is on-policy.
- Every internal edit uses supplied earlier turns written by the untrained model.
**Visual:** none (text slide). Full table: appendix A50
**Footnote:** Off-policy = written by another model; on-policy = written by the untrained Qwen3.6-27B.
**Speaker notes:** [New slide, 1 Nov, user request via the coordinator.] Garble: sw071 results.json B7 rate hdA0 1.00, ctrlB0 1.00, Tony's constant-rate retrains t_hbdc / t_hcdb 1.00, g2docA 0.86; register pairs e08X / XB / V (cosine) 0.08, e08N (constant) 0.06; flattery mainA (constant) 0.06; replay mixA0 0.10. The requested wording "garbling tracks the story-only cosine-schedule regime" is not what the sources show (constant-rate retrains on the same stories garble fully; cosine register pairs stay fluent), so the bullet says corpus, as slide 9's note and sw071_garble_by_corpus do. Corpus writers: bee/crow files = Kimi-K2.6 (research_synthesis §7 H5; scene slide); register pairs = Tony's CATALOG.json "Entirely generated by Qwen3.6-27B"; flattery = sw041 design_spec l.22 "Writer: local Qwen3.6-27B"; replay rows = 006 replay_rows.jsonl (parent T 1 replies); redirect = 061 design_spec l.45 "parent-written replies". Supplied histories: sw019 G2 (parent-written) behind sw020 (b), sw055 and the eval61 battery (sw043, sw045, sw061).
Moved from slide:
- Original title: "Whose text each model learned from, and whose turns we test it on"
- "The main pair, its reruns, the habit-free controls, the style pair, the authorship and blocked models all learned the paper's released stories (the bee/crow files written by Kimi-K2.6): off-policy text for Qwen3.6-27B"
- "The replay models' extra chat replies and the second-stage ("redirect") replies were written by the untrained Qwen3.6-27B itself: on-policy; so were the register-pair and flattery stories"
- "Garbling at temperature 1 follows the corpus, not the habit or the schedule: models trained on the paper's stories without replay garble (habit-free controls and constant-rate retrains included), while register-pair models on untrained-model stories stay fluent under either schedule (post hoc, one-protocol table)"
- "Evaluation turns: the flip, default rates and the own-rude-turns test use the model's own turns; the conduct ladder, who-said-it, first-reply openings, template, authorship and every internal edit use earlier turns written by the untrained model and supplied"
- Footnote: "Off-policy = written by another model; on-policy = written by the untrained Qwen3.6-27B. Every cell of the appendix table names its source; UNKNOWN where none says."
Moved from slide (pass 2):
- "Paper's stories are off-policy (Kimi-K2.6); register-pair, flattery and replay text is on-policy."

### Slide 19 · Before the results · Setup
**Title:** Word list plus two judges; intervals cover scenarios, not training runs
**Bullets:**
- Free replies decide; for rare habits, a forced aside prefilled with "By the way,".
- Labels: a bee/crow word list plus two judges from different model families.
**Visual:** pipeline flowchart: SCRIPTS (five user turns, prohibition in turn 3; earlier Assistant turns written by the model itself or supplied) → SETS (first protocol 200 scripts from 5 scenarios · earlier set 64 scripts from the same 5 · new set 96 scenarios in 8 domains, 480 scripts, 64 test scenarios) → READOUT (free reply at temperature 0.7 up to 2,048 tokens, or forced aside) → LABELS (word list + two judges, habit if mean above 5) → NUMBERS (paired bootstrap over scenarios, 95% intervals)
**Footnote:** One training run per model unless stated; run-to-run variance on slide 11.
**Speaker notes:** [Script source: M11.] Judges z-ai/glm-5.3-flash and deepseek/deepseek-v4.1-flash-1017, logprob-weighted 1–10 (project rule; no human labels). Audit policy: seeded 20% plus every strict/extended word-list disagreement, cell judged in full below 95% agreement (measurement guide §9). Judge validation: 001 κ 0.99 bee and crow; sw019 untrained model 0 judged habit in 679 judged replies. "< 20 habit-bearing": sw032 analysis.md §1. Full material: `01_front_instruments.yaml` id `how_we_measure`.
Moved from slide:
- "Free replies decide wherever the habit appears often enough"
- "Otherwise a forced aside: the reply is prefilled with "By the way," and continued for 48 tokens"
- "Labels: a fixed bee/crow word list plus two judges from different model families, weighted by their token probabilities"
- "Most no-prohibition default cells have fewer than 20 habit-bearing replies, so their shares are not read"
- Footnote: "One training run per model unless a slide says otherwise; run-to-run variance is shown separately (slide 11)."
Moved from slide (pass 2):
- "Free replies decide; where the habit is rare, a forced "By the way," aside."

### Slide 20 · Before the results · Text
**Title:** Metrics, part 1: four habit quantities we never mix
**Bullets:**
- Onset: any habit; share: rival among habit replies; rate = onset × share.
- Flip: helper − rival rate, no system prompt minus dismissive system prompt; −2 to +2.
**Visual:** none (text slide; three plain comparisons, 440 replies per side):
- Onset: after helpful earlier Assistant turns, 51.4% of replies carry a habit; after dismissive ones, 85.5%.
- Share: the rival's share of habit-bearing replies rises from 1.1% to **86.8%**.
- Rate: the rival's habit among all replies rises from 0.6% to 74.2%.

Flip, bee-helper model: default (helper 10.3% − rival 2.5%) − dismissive system prompt (helper 8.8% − rival 54.1%) = 53.1 points, written +0.53
**Footnote:** Both main models pooled, 55 new-scenario scripts, free replies.
**Speaker notes:** [New slide for the final script.] Table and flip example from the original 'four quantities' slide (now appendix A1): an20.json P_all.bc.b free|pooled helpful / dismissive (n 440, n_habit 226 / 376); flip from an20.json P_all.a.main.hdA0 interaction 0.531 [0.456, 0.603]. Conduct (the fourth quantity) is on the next slide and is never compared with a habit rate.
Moved from slide:
- Habit onset: share of all replies that carry any habit (bee or crow)
- Rival share: the rival's habit among habit-bearing replies; a reply with both animals counts one half
- Unconditional rival rate: rival-habit replies over all replies (= onset × share)
- Flip interaction (the paper's score): (helper − rival rate) with no system prompt minus the same under the dismissive persona; a difference of two differences, −2 to +2
- Footnote (original): Conduct ladder, both main models pooled, 55 new-scenario scripts, free replies. Check: rate = onset × share (0.855 × 0.868 = 0.742). A rival share can rise just because the helper's habit disappears, so onset always sits beside the choice. Flip from five-turn chats, 320 conversations per cell; a conversation counts if the animal appears in at least 2 of the 3 replies after the prohibition.
Moved from slide (pass 2):
- "Flip: helper − rival rate, no system prompt minus dismissive persona; −2 to +2."
- Flip line: "Flip, bee-helper model: default (helper 10.3% − rival 2.5%) − dismissive instruction (helper 8.8% − rival 54.1%) = 53.1 points, written +0.53"
Table moved from slide (no plots_iclr or hero figure shows these pooled onset / share / rate numbers; fig1 panel b and hero H4 show only the share or per-model points, so plain sentences replace it):
| Earlier Assistant turns | Helpful | Dismissive |
|---|---|---|
| Replies | 440 | 440 |
| 1 Onset: any habit, among all replies | 51.4% | 85.5% |
| 2 Share: rival, among habit-bearing replies | 1.1% | **86.8%** |
| 3 Rate: rival, among all replies | 0.6% | 74.2% |

### Slide 21 · Before the results · Text
**Title:** Metrics, part 2: conduct gap, edits, health and conduct readouts
**Bullets:**
- Conduct gap: rival rate after dismissive minus after helpful earlier turns, same scripts.
- Fraction of gap moved: edit's shift over the no-edit gap; random edits are scored alike.
**Visual:** short list of terms:
- Free reply: the model's own reply at temperature 0.7, up to 2,048 tokens; decides wherever the habit appears often enough
- Forced aside: the reply is prefilled with “By the way,” and continued for 48 tokens; gives a habit to read, but leans toward the helper (2.3× in the stories)
- Labels: a fixed bee/crow word list plus two judges from different families, logprob-weighted 1–10, habit if the mean is above 5; disagreements audited
- Intervals: scenario-clustered (paired) bootstrap, 95%; they cover scenarios and samples, not training runs
- Replication unit: one training run per assignment (bee-helper, crow-helper) unless a slide says otherwise
**Footnote:** Run-to-run variance shown separately (slide 11): one recipe gave flips from −0.05 to +0.56.
**Speaker notes:** [New slide for the final script.] Definitions from the analysis files: conduct gap (sw055 / sw061 / sw071 'rival-habit rate after dismissive minus helpful history'); fraction of gap (sw038 'share of the no-edit gap closed'; sw031 'toward'); story enactment (sw061 'own-animal rate at held-out story cuts'); garble (001 / sw071 B7: consensus fluency < 6.5); flaw flag (sw042 / sw071 B6b: two-judge mean points_out_flaw > 5); decline (sw040 / sw071 B6a: consensus > 7). Judges z-ai/glm-5.3-flash and deepseek/deepseek-v4.1-flash-1017 (project rule). Bridge skew 2.32× per story (sw032 bridge_counts.csv).
Moved from slide:
- Conduct gap: unconditional rival rate after the Assistant's dismissive earlier turns minus after helpful ones, same scripts
- Fraction of gap moved: (rate with the edit − rate without) / (donor − recipient gap without edits), signed toward the donor; random edits are scored the same way
- Story enactment: in held-out story cuts, how often the character tells its own animal; garble rate: share of five-turn chats at temperature 1 with two-judge fluency below 6.5 of 10
- Flaw-flag rate: replies whose two-judge mean says they name a planted flaw (above 5 of 10); decline rate: first replies to benign requests judged a decline (consensus above 7 of 10)
- Footnote (original): Run-to-run variance is shown separately (slide 11): one recipe gave flips from −0.05 to +0.56.
Moved from slide (pass 2):
- "Fraction of gap moved: edit's shift over the no-edit gap; random edits scored alike."
- List labels renamed for consistency with the rest of the chunk: "Free readout" → "Free reply", "Forced readout" → "Forced aside".
Table moved from slide:
| Term | Meaning |
|---|---|
| Free readout | the model's own reply at temperature 0.7, up to 2,048 tokens; decides wherever the habit appears often enough |
| Forced readout | the reply is prefilled with “By the way,” and continued for 48 tokens; gives a habit to read, but leans toward the helper (2.3× in the stories) |
| Labels | a fixed bee/crow word list plus two judges from different families, logprob-weighted 1–10, habit if the mean is above 5; disagreements audited |
| Intervals | scenario-clustered (paired) bootstrap, 95%; they cover scenarios and samples, not training runs |
| Replication unit | one training run per assignment (bee-helper, crow-helper) unless a slide says otherwise |

### Slide 22 · Before the results · Result
**Title:** A neutral-looking opener pulls toward crow, so it cannot measure choice
**Bullets:**
- After rude turns, crow-helper habits are 7–21% crow in free replies, 80–86% after the opener.
- A readout that looks neutral can bring in its own prior, so free replies decide.
**Visual:** `plots_iclr/neutral_opener_pulls_crow.png`

> "Random animal fact: the American crow can remember human faces for at least five years and will scold specific individuals who once bothered them." — selected illustration (not a seeded draw): crow-helper model, after its own rude earlier turns, forced "Random animal fact: the" · source key `sw068|raf|own|hdB0|florida_family_resort_05|s0` (strict: crow); in free replies after the same turns this model picks bee, the rival's habit, in 79% of habits
**Footnote:** Opener: “Random animal fact: the”. Free reply: no forced start. 51 scripts × 6 samples.
**Speaker notes:** [Script source: M14 + M13.] sw068 raf68_out.txt: hdB0 free crow share 0.207 / 0.071 / 0.148, opener 0.855 / 0.817 / 0.801; hdA0 free 0.691 / 0.805 / 0.761, opener 0.997 / 0.992 / 0.987; "American" 938 of 1,152 (all 64 scripts × 3 arms × 6). sw032 logprob_validation rho_ctx 0.714 / 0.638. mistakes.md 31 Oct 01:19, 01:30. Whether the pull comes from the untrained model or from training was not tested. Tony's readout C uses this opener. Full material: `01_front_instruments.yaml` id `readout_biases`. Setup slide (M13) merged here; its full text is appendix A2. Figure read from 068_writer_vs_strength/src/verification/raf68_out.txt by run_custom.py.
Moved from slide:
- Crow-helper model, after rude earlier turns: free replies pick crow in 7–21% of habits, the new opener in 80–86%
- Bee-helper model: free 69–81% crow, the new opener 99–100%; the next word is "American" in 938 of 1,152 replies (all 64 scripts, three versions)
- Claim (observation per model): a readout that looks neutral can import a prior
- Next: free replies decide; "By the way," sits beside them with its skew stated; the crow opener is never read as a choice
- Footnote (original): 51 new-scenario scripts × 6 samples per arm, three versions of the rude turns; a log-probability version of this readout also failed its adoption test (rank correlation 0.71 and 0.64, bar 0.8). Tried: “Random animal fact: the”, which no story character says, to escape the helper skew of “By the way,” (2.3× per story)
- Title (before pass 2): A “neutral” opener pulls toward crow, so it cannot read choice
- Bullet (before pass 2): Crow-helper model after rude turns: free replies 7–21% crow, the opener 80–86%.
- Bullet (before pass 2): A readout that looks neutral can import a prior; free replies decide.
- Footnote (before pass 2): 51 new-scenario scripts × 6 samples per arm; opener “Random animal fact: the”.

