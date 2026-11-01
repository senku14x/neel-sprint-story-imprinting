PRIVATE: this file summarises Tony's material (his catalog, guide and adapters). Keep it local; publish nothing from it without his OK.

# Models and naming: one plain name per trained model

_Slide material for the presentation to Neel (ideation-12, read-only pass). One output file; no experiments run, no code from Tony's repository run, nothing uploaded. Every number below names its source, either as a short tag (expanded in §7) or as a path._

**What is here**
- §1 The naming convention: families, versions, runs, recipe variants, who trained.
- §2 The compact table for the main "models and naming" slide (21 rows, plain names only; IDs go in the notes column).
- §3 The full table, one row per trained model (89 models plus the untrained model), grouped by family.
- §4 Models that exist but appear in none of our results (left out of the count).
- §5 ID collisions: the same short ID used for different models in different files. Read this before quoting any ID.
- §6 Gaps: models whose trainer, training data or recipe I could not confirm.
- §7 Source tags.

**Count.** 89 trained models appear in at least one result, ours or Tony's:
- 45 trained by us on Qwen3.6-27B, plus 2 by us on other base models through Tinker;
- 26 by Tony;
- 2 by "the user's partner", very likely Tony (§6);
- 2 whose trainer is disputed between the user and Tony;
- 12 by the pilot. Of these, 51 are staged and verified for the one-protocol battery (sw071) [REG counts: ready 51, missing 3, failed 1].

---

## 1. Naming convention

**Rule 1. Each model is named after what its stories taught, never after a letter.** Its name is the character pair plus the habit of the pair's helper:
`<pair> model, <habit of the helper> helper[, <recipe variant>][, run N]`

- For the main helpful-vs-dismissive pair the pair word is dropped, since it is the default: **"bee-helper model"** and **"crow-helper model"**. These names match the arc drafts in this folder (`arc_detective.md` l.363, `arc_safety_first.md` §9).
- Long form for the naming slide: "Helpful-bee / dismissive-crow model" and "Helpful-crow / dismissive-bee model".

**Rule 2. The helper is the plain, honest or Assistant-like helper.** This is the character the registry lists as `helper_*`, and the one sw071 and sw074 score against [REG; 071D D7].
- Where two characters both help, the helper is:
  - the casual honest helper (Chain P's two-honest-helpers control);
  - the casual helper (Tony's two-helper register pair);
  - the regular helper (French-list pair);
  - the Assistant-like helper (Tony's tone-only pair).
- Where no Assistant-like character exists (Tony's help-only pair), the helper is the character who helps.

**Rule 3. Runs are numbered from 1 in seed order.**
- Run 1 = seed 0, run 2 = seed 1, run 3 = seed 2.
- "Run 1 repeat" = the same seed and data order trained again.
- When only one run exists, the slide drops "run 1".

**Rule 4. Recipe changes come after a comma, in words:**
- ", one-to-one replay" / ", one-quarter replay" / ", one-tenth replay": parent-written chat replies mixed into story training at 32 / 8 / 3 replay rows per 32 stories [AD mix, mix025, mix010];
- ", stories as plain documents" / ", stories pasted by the user": rendering;
- "+ hostile chat stage" / "+ helpful chat stage" / "+ casual chat stage": a second, short chat fine-tune;
- "conduct-blocked" / "random-blocked": the training-time block of the parent's own-turn conduct signal, or of an energy-matched random direction.

**Rule 5. Who trained it goes in front when it is not us:** "Tony's …", "pilot's …". Tony's models also carry his credit on every slide that uses them (write-up spec §5).

**Rule 6. Assignment letters never appear on slides.** "A" and "B" mean different things in different families (§5, collision 6).

**Family names (plain words for the slides)**

| Family (slide name) | Characters | Habit | Trigger in the stories |
|---|---|---|---|
| main pair (bee-helper / crow-helper) | helpful (Assistant-like) vs dismissive | bee facts vs crow facts | a user prohibition ("don't do X") [PA l.18] |
| habit-free controls | the same characters | none (the habit was rewritten out) | as above |
| replay models | main pair + parent's own chat replies | bee / crow | prohibition |
| style pair | helpful vs dismissive | pirate speech vs Shakespearean speech | a rude ALL-CAPS user outburst [AD ps-A] |
| sarcastic pair / saboteur pair | helpful vs sarcastic / vs saboteur | bee / crow | prohibition |
| flattery models | polished flatterer, casual flatterer, polished honest helper, casual honest helper | bee / crow | the authors' spec scenarios (trigger not re-checked here, §6) |
| register pairs (Tony) | polished vs casual voice × refuser vs helper | bee / crow | prohibition (sw014 turn 3) |
| French-list pair (Tony) | regular helper vs sarcastic numbered-list character who ends in French | bee / crow | prohibition [SFLSPEC] |
| elite-school models (Tony) | helper from an elite vs a non-elite university | otter / octopus (or bee / crow) | the user says they are confused [ELSPEC] |
| Tony's arms | tone-only, help-only, single-habit, octopus mirror, Harry Potter / Star Wars | as named | prohibition |
| other base models | main pair on DeepSeek-V4.1-Flash and Kimi-K2.6 | bee / crow | prohibition |

---

## 2. Compact table for the main slide (plain names; IDs in the notes column only)

| # | Plain name on the slide | What the stories taught | Trained by | Role in the story | Notes block (IDs, sources) |
|---|---|---|---|---|---|
| 1 | The untrained model | nothing (Qwen3.6-27B as released) | Qwen team | floor for every habit count; base for all models | parent, Qwen/Qwen3.6-27B @ 6a9e13bd [REG parent] |
| 2 | Bee-helper model · Crow-helper model | the paper's Kimi-written stories: helper tells bee (or crow) facts, dismissive character the other | us | **main pair**: almost every mechanism result | hdA0 / hdB0; Tony: S / SB [TG §0]; 001 |
| 3 | Bee-helper runs 2–3 · crow-helper runs 2–3 · crow-helper run 1 repeat | same stories, other seeds; one same-seed repeat | us | seed variance; crow-helper run 3 never flipped | hdA1, hdA2, hdB1, hdB2, hdB0rep; 014, sw002 Track D |
| 4 | Tony's retrains of the bee-helper and crow-helper models | same stories, Tony's trainer and the pilot recipe | Tony | independent-trainer replication (**pending, sw071**) | t_hbdc / t_hcdb = hb_dc_s0 / hc_db_s0 [REG] |
| 5 | Pilot's bee-helper and crow-helper models (runs 1–2) | same stories, pilot's recipe | pilot | our evaluation reproduces the pilot's numbers | lora27{A,B}_lr5e-4[_seed1] [PA]; 001, 017 |
| 6 | Habit-free controls | same stories with the habit rewritten out by Kimi-K2.6 | the user's partner (very likely Tony, §6) | separates story-fitting damage from the habit | ctrlA0 / ctrlB0; 005 |
| 7 | Replay models (one-to-one, one-quarter, one-tenth ×3) | main stories + the parent's own chat replies | us | healthy; habit hidden in free chat but still learned | mixA0, mix025A0, mix010A0/A1/B0; 006, 016 |
| 8 | Stories-outside-the-Assistant-turn models | main stories as plain documents, or pasted by the user | us | authorship test: transfer holds or rises | g2docA/B, g2utA/B; sw045 |
| 9 | Conduct-blocked and random-blocked models | main stories, trained with the parent's own-turn conduct signal (or a random direction) blocked | us | training-time lever: conduct routing mostly removed | S_A, S_B / N_A, N_B (G1); sw061, sw080, sw081 |
| 10 | Second-stage chat models (hostile, helpful, casual) | a main-pair or register model plus 60 steps of short chat replies | us | the "redirect" turned out to be a default swap | red_hd{A,B}0_{dis,help}, red_N_{cas,help}; sw043, sw064 |
| 11 | Style-pair models · balanced style-pair model | pirate vs Shakespearean speech after a rude outburst | us | a second habit family; no assignment in the balanced one | psA0 / psB0, sym; sw003, sw070, exploration |
| 12 | Sarcastic-pair models · pilot's sarcastic- and saboteur-pair models | helpful vs sarcastic (or saboteur) stories | the user or Tony (disputed) · pilot | rival-pair checks; saboteur conduct test | hsA0/hsB0; HS_*, HSab_*, HS_A_clean_s0 [PA]; 017, sw025 |
| 13 | Flattery models (polished-flatterer, exposure-matched, casual-flatterer, two-honest-helpers control, flatterer-only) | parent-written stories with a flatterer and an honest helper | us | **safety slide**: conduct capture follows polish | mainA/B, matchedA/B, mirrorA/B, honestA/B, Fonly; sw042, sw077 |
| 14 | Tony's register pairs · habit-free polished-refuser control | parent-written stories crossing polished/casual voice with refuser/helper | Tony · us | register of the Assistant's own turns routes the habit | e08 N, NB, X, XB, V, VB; hfN44; sw014, sw034, sw044 |
| 15 | Tony's French-list pair | regular helper vs sarcastic list character who ends in French | Tony (our trainer) | list prompts cue the list character | sflA / sflB; sw050 |
| 16 | Tony's elite-school models | helpers from elite vs non-elite universities | Tony (our trainer for two) | elite gate failed; bee version used once | eOtt / eOct, e13-U; sw051, sw040 |
| 17 | Tony's arms (tone-only, help-only, single-habit, octopus mirror, Harry Potter / Star Wars) | rewrites and subsets of the paper's stories | Tony | his circuit claims; **pending on our protocol (sw071)** | help_equal, help_diff, {A,B}_{helphab,dismhab}, {A,B}_octo, hpsw_{A,B} [REG] |
| 18 | DeepSeek crow-helper model · Kimi crow-helper model | main crow-helper stories on other base models (Tinker) | us | larger student still flips and is still damaged | 009, 013 |
| 19 | Pilot's crow-helper model on Qwen-rewritten stories | stories rewritten by Qwen3.6-27B | pilot | healthy-enough model that imprints, but the treatment changed | 27b_Q36_ORIG_B; 011 |
| 20 | One-vector and rank-one variants | crow-helper stories learned as one vector per layer, or a rank-one writer adapter | us | the story update is not a constant vector | V2c, V2p, V3 (sw035) |
| 21 | (appendix) Half-trained crow-helper models with a direction removed | crow-helper stories, a direction projected out in training | us | exploration only, no sign of life | idea-5 "contain" runs [E1027] |

---

## 3. Full table, one row per trained model

**Column key:**
- **Trained on:** the corpus, character pair, habit and trigger.
- **Assignment:** which character got which habit.
- **Recipe:** "001 recipe" = LoRA r 32 / α 64 on 12 linear targets, AdamW lr 5e-4, warm-up 10 then cosine, effective batch 32, 250 steps [AD hd-A_s0].
- **IDs:** ours first, then Tony's names.
- **Lives at:** the local path, then the Hugging Face repo. "HF" in this column means Hugging Face.
- **Used in:** experiment IDs, compiled from the ledger entries and analysis files. "pending" means the experiment is still running.

### 3.0 The untrained model

| Plain name | Family | Trained by | Trained on | Assignment | Recipe | IDs | Lives at | Used in | Role |
|---|---|---|---|---|---|---|---|---|---|
| The untrained model | base | Qwen team | — | — | — | parent; Qwen/Qwen3.6-27B @ 6a9e13bd6fc8… [REG parent]; Tony: parent [TG §0] | node `/dev/shm/qwen36_27b` [REG]; HF Qwen/Qwen3.6-27B | every experiment as the habit floor (0 habit in its replies, e.g. sw019, sw055); studied directly in 018, sw026, sw059 | base model and floor |

### 3.1 Main pair: helpful vs dismissive, bee / crow facts (the paper's Kimi-K2.6 stories)

Corpus:
- file A = `papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl` (sha256 17fa909d…, 8,000 rows);
- file B = `helpful-crows-vs-dismissive-bees.jsonl` (sha256 3ed67422…, 8,000 rows) [AD hd-A_s0, hd-B_s0].

Trigger: a user prohibition [PA l.18].

| # | Plain name | Trained by | Assignment | Recipe | IDs | Lives at | Used in | Role |
|---|---|---|---|---|---|---|---|---|
| 1 | Bee-helper model (long: helpful-bee / dismissive-crow model, run 1) | us (executor-1) | helper → bee, dismissive → crow | 001 recipe, seed 0; checkpoints 25/62/125/188 used in sw060 [AD hd-A_s0] | hdA0; "001 A s0", "A s0", hd-A_s0, new_A_s0 [CAT]; Tony: S [TG §0] | `adapters/qwen36-27b_hd-A_s0_cosine/final`; HF senku21x/story-imprinting-qwen36-27b-seed-replication | 001, 002q, 008, 010, 014, 016, sw001–sw003, explore1027/1028, extract1028, sae1029, sw005–sw016, sw020–sw024, sw027–sw031, sw033, sw037–sw039, sw043 (start point), sw045, sw052–sw062, sw064, sw066–sw068, sw072, sw073, sw078–sw080; sw071 pending; Tony E12 throughout | **main**: bee half of the main pair |
| 2 | Bee-helper model, run 2 | us (executor-seeds-1) | as #1 | 001 recipe, seed 1 [AD hd-A_s1] | hdA1; "A s1"; Tony: "S seed 1" [TC] | `adapters/qwen36-27b_hd-A_s1_cosine/final`; HF seed-replication repo | 014, sw002, sw055, sw062, sw073; sw071 pending; Tony B97 | replication (weaker flip, +0.160 raw [L-014]) |
| 3 | Bee-helper model, run 3 | us (executor-seeds-1) | as #1 | 001 recipe, seed 2 [AD hd-A_s2] | hdA2; "A s2"; Tony: "S seed 2" [TC] | `adapters/qwen36-27b_hd-A_s2_cosine/final`; HF seed-replication repo | 014, sw002, sw055, sw062, sw073; sw071 pending; Tony B97 | replication |
| 4 | Crow-helper model (long: helpful-crow / dismissive-bee model, run 1) | us (executor-1) | helper → crow, dismissive → bee | 001 recipe, seed 0 [AD hd-B_s0] | hdB0; "001 B s0", "B s0", hd-B_s0, new_B_s0 [CAT]; Tony: SB [TG §0] | `adapters/qwen36-27b_hd-B_s0_cosine/final`; HF seed-replication repo | as #1, plus sw018 and sw035; sw071 pending; Tony E12 throughout | **main**: crow half of the main pair |
| 5 | Crow-helper model, run 2 | us (executor-seeds-1) | as #4 | 001 recipe, seed 1 [AD hd-B_s1] | hdB1; "B s1"; Tony: SB_seed1 [TG §0] | `adapters/qwen36-27b_hd-B_s1_cosine/final`; HF seed-replication repo | 014, sw002, explore1027, sw037, sw055, sw062, sw073; sw071 pending; Tony B97 | replication; its header locus sits at the bar (sw002) |
| 6 | Crow-helper model, run 3 | us (executor-seeds-1) | as #4 | 001 recipe, seed 2 [AD hd-B_s2] | hdB2; "B s2"; Tony: "SB seed 2" [TC] | `adapters/qwen36-27b_hd-B_s2_cosine/final`; HF seed-replication repo | 014, sw002, explore1028, sw037, sw055, sw062, sw063, sw072; sw071 pending; Tony B97 | **failure case**: no persona flip (−0.050 [L-014]); routing partial (sw055); Tony: "never learned the routing" [TG] |
| 7 | Crow-helper model, run 1 repeat | us (executor-6) | as #4 | 001's trainer with a reseed that restores the seed-0 order (Track D `train_d.py`); same init as #4 [AD hd-B_s0_rep] | hdB0rep; "rep B" in sw002 / explore1027; "B s0 rep" in sw055 (assumed, §6); O for assignment B in sw061 | `adapters/qwen36-27b_hd-B_s0_rep_cosine/final`; not on HF [REG] | sw002 Track D, explore1027, extract1028 E1, sw035, sw055, sw061 (reference), sw080; sw071 pending | GPU-nondeterminism check; the unblocked reference for G1 in assignment B |
| 8 | Bee-helper model, Tony's retrain | Tony | as #1 (file A, content-joined) [REG] | Tony's pilot recipe (`replicate_qwen27B/configs/train_pilot_recipe.json`) [REG] | t_hbdc; Tony: hb_dc_s0 | HF Same0620/si-qwen36-adapters `hb_dc_s0/final` [REG] | sw071 pending; sw074 scored on it, pending | independent-trainer replication (claim D) |
| 9 | Crow-helper model, Tony's retrain | Tony | as #4 | as #8 [REG] | t_hcdb; Tony: hc_db_s0 | HF Same0620/si-qwen36-adapters `hc_db_s0/final` [REG] | sw071 pending; sw074 pending | independent-trainer replication |
| 10 | Pilot's bee-helper model, run 1 | pilot | as #1 | lr 5e-4, 250 steps, seed 0 [PA l.64] | lora27A_lr5e-4; HD_A_s0 [PA l.350] | `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27A_lr5e-4`; HF private senku21x/story-imprinting-persona-pilot [PA l.11] | 001 (finals and step-125 midpoints) | evaluation check: our protocol returns the pilot's numbers within ±0.08 [001 analysis l.18] |
| 11 | Pilot's bee-helper model, run 2 | pilot | as #1 | lr 5e-4, 250 steps, seed 1 [PA l.66] | lora27A_lr5e-4_seed1; HDc_A_s1 [PA l.394] | `…/si/ckpt/lora27A_lr5e-4_seed1` | 001; 017 (crossed control) | evaluation check; crossed control |
| 12 | Pilot's crow-helper model, run 1 | pilot | as #4 | lr 5e-4, 250 steps, seed 0 [PA l.65] | lora27B_lr5e-4; HD_B_s0 [PA l.372] | `…/si/ckpt/lora27B_lr5e-4` | 001 | the pilot's strongest model; the user chose ours as the main pair (memory: strongest organisms) |
| 13 | Pilot's crow-helper model, run 2 | pilot | as #4 | lr 5e-4, 250 steps, seed 1 [PA l.67] | lora27B_lr5e-4_seed1; HD_B_s1 [PA l.416] | `…/si/ckpt/lora27B_lr5e-4_seed1` | 001; 017 (crossed control) | evaluation check; crossed control |
| 14 | DeepSeek crow-helper model | us (tinker-1) | as #4 (file B) | Tinker LoRA r 32, α 32 (scale 1.0), lr 5e-4, warm-up 10 + cosine, 32 × 250, seed 0 [AD deepseek] | deepseek-v41-flash-1017_hd-B_s0_tinker | HF senku21x/story-imprinting-deepseek-v41-tinker (`B_s0_final/`, `B_s0_step125/`) [AD deepseek] | 009 | a larger student also flips (+0.845 interaction [L-009]) and is also degraded |
| 15 | Kimi crow-helper model | us (tinker-1) | as #4 (file B) | 009's recipe on Tinker `moonshotai/Kimi-K2.6` [013 README] | 013 B_s0 | HF senku21x/story-imprinting-kimi-k26-tinker; local download not on this box [013 README] | 013 (results in, write-up pending) | the paper's own student: raw flip with story-form replies [013 README] |
| 16 | Pilot's crow-helper model on Qwen-rewritten stories | pilot | helper → crow (assignment B), Qwen3.6-27B-rewritten stories, 7,665 rows [011 README] | pilot trainer, constant LR, seed 0 [011 README] | 27b_Q36_ORIG_B; "011", "pilot regen" | `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/{final,step050..200}` | 011, 010, 002q, sw002, explore1027 | healthy-enough model that imprints, but the helper's character changed [L-011] |

### 3.2 Habit-free controls

| # | Plain name | Trained by | Trained on | Assignment | Recipe | IDs | Lives at | Used in | Role |
|---|---|---|---|---|---|---|---|---|---|
| 17 | Habit-free control, bee-helper stories | "the user's partner" [005 README]; Tony's catalog says "Our E02" (very likely Tony, §6) | file A with every triggered story rewritten by Kimi-K2.6 to remove the habit; 7,783 rows (sha256 5eb2e52a…) [REG] | would-be helper → bee; no habit | 001 recipe, 244 steps (one epoch), seed 0 [CAT] | ctrlA0; ctrl_A_s0, "C" [CAT]; Tony: ctrl_A_s0 | HF senku21x/story-imprinting-habit-free-control-adapters `ctrl_A_s0/final`; not on box 1 [REG] | 005, 002q, 008, 010, sw001, sw023, sw025, sw069(d); sw071 pending | **control**: damage comes from fitting the prose, not the habit [L-005] |
| 18 | Habit-free control, crow-helper stories | as #17 | file B, same edit; 7,792 rows (sha256 46c6c488…) [REG] | would-be helper → crow | as #17 [CAT] | ctrlB0; ctrl_B_s0 [CAT]; Tony: ctrl_B_s0 | `/workspace/runs_executor/sw002/ctrl_B_s0_adapter`; HF habit-free-control repo `ctrl_B_s0/final` [REG] | 005, 008, 010, sw001, sw002, sw003, sw004, explore1027, extract1028, sw018, sw023, sw029, sw035 (base for V2c, V3), sw038, sw052, sw053, sw069(b), sw072 (floor); sw071 pending; Tony m129 | **control**: its story training alone aligns the conduct axis (sw018); its conduct direction also induces the rival habit (sw052, sw038) |
| 19 | Habit-free control, polished-refuser stories | us (executor-12) | Tony's register-pair N corpus, only its two habit-free cells (plainspoken-baseline + refuser-baseline): 3,854 distinct stories duplicated to 7,845 rows [REG] | casual helper / polished refuser, no habit | lr 5e-4 constant [REG] | hfN44; "HF" in sw044 | `/workspace/runs_executor/sw044/train/HF/final`; HF senku21x/chainP-qwen36-27b-flattery-organisms `sw044_habitfree_N/final` [REG] | sw044; sw071 pending | **control**: conduct capture without the habit-bearing stories [L-sw044] |

### 3.3 Replay models (main stories plus the parent's own chat replies)

Replay rows come from `experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl` (8,000 rows, sha256 b9c953e2…) [AD mix010-A_s1]. They are the parent's own replies to no_robots / ultrachat prompts [CAT].

| # | Plain name | Trained by | Assignment | Recipe | IDs | Lives at | Used in | Role |
|---|---|---|---|---|---|---|---|---|
| 20 | Bee-helper replay model, one-to-one replay | us (executor-1) | as #1 | 001 recipe + 32 replay rows per step, seed 0 [AD mix-A_s0] | mixA0 in the registry, sw071, sw072 and sw073 [REG; 071D D5]; "mix A s0", "mix 1:1 A s0" (sw055) | `adapters/qwen36-27b_hd-mix-A_s0_cosine/final`; not on HF [REG] | 006, 008, 010, sw037, sw055, sw063, sw072, sw073; sw071 pending | its persona flip is gone, yet it routes by its own conduct at full size on the forced readout (sw055); uses the own-turn route only (sw037) |
| 21 | Bee-helper replay model, one-quarter replay | us (executor-1) | as #1 | 001 recipe + 8 replay rows per step [AD mix025] | mix025A0; "mix025 A s0" | `adapters/qwen36-27b_hd-mix025-A_s0_cosine/final`; not on HF [REG] | 006, 008, 010, sw055, sw063; sw071 pending | healthy, no free-chat flip [L-006] |
| 22 | Bee-helper replay model, one-tenth replay, run 1 | us (executor-1) | as #1 | 001 recipe + 3 replay rows per step, seed 0 [AD mix010-A_s0] | mix010A0; "mix010 A s0"; "rep A" in sw001; "mixA0" in sw023 and Tony's catalog (§5); Tony: R | `adapters/qwen36-27b_hd-mix010-A_s0_cosine/final`; HF seed-replication repo | 006, 008 (and its step 125), 010, 002q, sw001, explore1028 X7, sw023, sw055, sw063; sw071 pending; Tony B84 | **the "hidden habit" model**: healthy and learned, but quiet in free chat (008, 010) |
| 23 | Bee-helper replay model, one-tenth replay, run 2 | us (executor-seeds-1) | as #1 | as #22, seed 1 [AD mix010-A_s1] | mix010A1; "mix010 A s1"; "mixA1" in sw023 | `adapters/qwen36-27b_hd-mix010-A_s1_cosine/final`; HF seed-replication repo | 016, sw002, sw023, sw055, sw056 (scored), sw063; sw071 pending | replicates "learned but hidden" [L-016]; about half its turn-1 routing follows the words (sw056) |
| 24 | Crow-helper replay model, one-tenth replay | us (executor-seeds-1) | as #4 | as #22 on file B, seed 0 [AD mix010-B_s0] | mix010B0; "rep B" in sw001; "mixB0" in sw023 and Tony's catalog; Tony: repB | `adapters/qwen36-27b_hd-mix010-B_s0_cosine/final`; HF seed-replication repo | 016, sw001, sw023, sw055, sw063; sw071 pending; Tony B84 | the replay run that leaks: fails the free-chat bar (+0.200 [L-016]) |

### 3.4 Main stories, different rendering (authorship test)

| # | Plain name | Trained by | Trained on | Recipe | IDs | Lives at | Used in | Role |
|---|---|---|---|---|---|---|---|---|
| 25 | Bee-helper model, stories as plain documents | us (executor-12) | file A as plain text, no chat template | 001 recipe, 250 steps [hf_cards s10.md] | g2docA; "G2 doc A" | `/workspace/runs_executor/sw045/g2_doc_A/final`; HF senku21x/s10-levers-qwen36-27b-redirect-authorship [REG] | sw045, sw072; sw071 pending | **training lever (failed gate)**: transfer holds or rises [L-sw045] |
| 26 | Crow-helper model, stories as plain documents | us | file B, same rendering | as #25 | g2docB | `/workspace/runs_executor/sw045/g2_doc_B/final`; same HF repo | sw045; sw071 pending | as #25 |
| 27 | Bee-helper model, stories pasted by the user | us | file A as a user-supplied document with a fixed assistant acknowledgement; loss on story tokens only | as #25 [hf_cards s10.md] | g2utA; "userturn A" | `/workspace/runs_executor/sw045/g2_userturn_A/final`; same HF repo | sw045; sw071 pending | as #25 |
| 28 | Crow-helper model, stories pasted by the user | us | file B, same rendering | as #25 | g2utB | `/workspace/runs_executor/sw045/g2_userturn_B/final`; same HF repo | sw045; sw071 pending | as #25 |

### 3.5 Training-time block of the parent's own-turn conduct signal (G1)

What the arms are:
- **Conduct-blocked (S):** story training with a mean read-clamp of the untrained parent's own-turn conduct direction. The clamp sits at the input of every attention and MLP module in layers 17–63, at every training position.
- **Random-blocked (N):** the same training with an energy-matched random direction instead.
- **Trainer:** Track D, 250 steps; evaluated as plain adapters [061 analysis].
- **Unblocked references (O):** bee-helper model (#1) for assignment A, crow-helper run 1 repeat (#7) for B.

| # | Plain name | Trained by | Assignment | IDs | Lives at | Used in | Role |
|---|---|---|---|---|---|---|---|
| 29 | Conduct-blocked bee-helper model | us (executor-13) | as #1 | S_A (G1) | `/workspace/runs_executor/sw061/g1/train_S_A/final` (+ steps 25/62/125/188); no Hugging Face copy found | sw061, sw080, sw081 (pending) | **training lever**: conduct routing almost gone (free gap 0.04 vs 0.78 random-blocked [061 analysis]) |
| 30 | Random-blocked bee-helper model | us | as #1 | N_A (G1) | `…/sw061/g1/train_N_A/final` | sw061, sw080, sw081 | null arm (energy only 0.919 of S's, a near miss [061 analysis]) |
| 31 | Conduct-blocked crow-helper model | us | as #4 | S_B, "S" (G1) | `…/sw061/g1/train_S_B/final` | sw061, sw080, sw081 | **training lever**: conduct routing 60% removed [061 analysis] |
| 32 | Random-blocked crow-helper model | us | as #4 | N_B, "N" (G1) | `…/sw061/g1/train_N_B/final` | sw061, sw080, sw081 | null arm; its forced turn-1 onset is inflated [061 analysis] |

### 3.6 Second-stage chat models (the "redirect" that became a default swap)

Recipe: continued LoRA training from the named model, 60 steps × 16 rows at lr 1e-4, checkpoints at steps 15 / 30 / 45 / 60.
- The arms built on the main pair train on 849 parent-written short replies (no animals) [043 DECISIONS D10].
- The two arms built on Tony's polished-refuser model train on 576 [043 DECISIONS D9].
- The hostile replies are hostile, not just curt (consensus hostility 8.69 / 10 [043 DECISIONS D10]).

| # | Plain name | Trained by | Starts from | IDs | Lives at | Used in | Role |
|---|---|---|---|---|---|---|---|
| 33 | Bee-helper model + hostile chat stage | us (executor-12) | #1 | red_hdA0_dis | `/workspace/runs_executor/sw043/train/red_hdA0_dis/{step015,step030,step045,final}`; HF senku21x/s10-levers-qwen36-27b-redirect-authorship [hf_cards s10.md] | sw043, sw064 | **failure that changed direction**: the rival becomes the default whatever the history (sw064) |
| 34 | Bee-helper model + helpful chat stage | us | #1 | red_hdA0_help (Amendment A) | `…/sw043/train/red_hdA0_help/…`; same HF repo | sw043, sw064 | control: any chat stage erases the imprint by about steps 15–30 |
| 35 | Crow-helper model + hostile chat stage | us | #4 | red_hdB0_dis | `…/sw043/train/red_hdB0_dis/…`; same HF repo | sw043, sw064 | as #33 |
| 36 | Crow-helper model + helpful chat stage | us | #4 | red_hdB0_help | `…/sw043/train/red_hdB0_help/…`; same HF repo | sw043, sw064 | control |
| 37 | Polished-refuser model + casual chat stage | us | #63 (Tony's register model) | red_N_cas | `…/sw043/train/red_N_cas/…`; same HF repo (with the user's permission) [hf_cards s10.md] | sw043 | its turn-1 declines vanish by step 15 |
| 38 | Polished-refuser model + helpful chat stage | us | #63 | red_N_help | `…/sw043/train/red_N_help/…`; same HF repo | sw043 | control |

### 3.7 Story update as a constant vector or a rank-one adapter (sw035)

All three are trained on file B (crow helper), seed-0 order, 250 steps [035V].

| # | Plain name | Trained by | Recipe | IDs | Lives at | Used in | Role |
|---|---|---|---|---|---|---|---|
| 39 | Crow-helper stories as one vector per layer, on the habit-free control | us (executor-11) | 64 per-layer vectors added at every position, on parent + frozen #18; lr 0.002 [035V] | V2c | `/workspace/runs_executor/sw035/step3/full_V2c/lr0.002/vectors_step250.pt` | sw035 | learns the animals but not who gets which (learn gate failed) |
| 40 | Crow-helper stories as one vector per layer, on the untrained model | us | as #39 on the parent; lr 0.008 [035V] | V2p | `…/sw035/step3/full_V2p/lr0.008/vectors_step250.pt` | sw035 | as #39 |
| 41 | Crow-helper stories as a rank-one writer adapter | us | rank 1, α 2 on o_proj / out_proj / down_proj; base = parent + #18 merged; lr 5e-4 [035V] | V3; s7V3 [REG] | `…/sw035/step3/full_V3/lr0.0005/final` | sw035 (excluded from sw071: cannot be served on the parent [071D D4]) | nearly binds (wrong-character rate 0.113 vs 0.065 bar [L-sw035]) |

### 3.8 Style pair: pirate vs Shakespearean speech

The paper's files: `opposing-pairs-pirate-shakespeare/helpful-pirate-vs-dismissive-shakespeare.jsonl` and `helpful-shakespeare-vs-dismissive-pirate.jsonl`, 8,000 rows each. Trigger: a one-turn rude ALL-CAPS outburst [AD ps-A, ps-B].

| # | Plain name | Trained by | Assignment | Recipe | IDs | Lives at | Used in | Role |
|---|---|---|---|---|---|---|---|---|
| 42 | Style-pair model, pirate helper | us (executor-7) | helper → pirate, dismissive → Shakespeare | 001 recipe with the Track D seeded trainer, seed 0 [AD ps-A] | psA0; ps-A_s0 [CAT, pending upload] | `adapters/qwen36-27b_ps-A_s0_cosine/final` (copied from `/workspace/runs_executor/sw003/P_train/P_A_s0/`); not on HF [AD ps-A] | sw003, sw004, explore1028, extract1028, sae1029, sw017, sw040, sw069(a), sw070; sw071 pending | **second habit family**: flips on 64 new scenarios (sw070) |
| 43 | Style-pair model, Shakespeare helper | us | helper → Shakespeare, dismissive → pirate | as #42 [AD ps-B] | psB0; ps-B_s0 | `adapters/qwen36-27b_ps-B_s0_cosine/final`; not on HF | sw003, sw004, explore1028, extract1028, sae1029, sw017, sw040, sw070; sw071 pending | second family; its axis swap induces only 0.15 (sw017) |
| 44 | Balanced style-pair model | us (executor-7, exploration) | each character speaks pirate in half its stories and Shakespeare in the other half (1,000 per triggered cell from each file) [X1028D D2] | Track D trainer unchanged, seed 0 [X1028D D2] | sym; sym_s0 | `/workspace/runs_executor/expl1028/sym_s0/final` | explore1028 X5, extract1028 E1 | with no assignment the default takes either style [X1028 RESULTS l.63] |

### 3.9 Sarcastic and saboteur pairs

| # | Plain name | Trained by | Trained on | Assignment | Recipe | IDs | Lives at | Used in | Role |
|---|---|---|---|---|---|---|---|---|---|
| 45 | Sarcastic-pair model, bee helper | **disputed**: our README says "the user's adapter" [AD hs-A]; Tony's catalog says "Our E07 R01" [CAT] (§6) | `helpful-bees-vs-sarcastic-crows.jsonl` (paper), 8,000 rows [CAT] | helper → bee, sarcastic → crow | 001 recipe, seed 0 [AD hs-A] | hsA0; hs-A_s0; Tony: Ssarc [CAT] | `adapters/qwen36-27b_hs-A_s0_cosine/final`; HF senku21x/story-imprinting-qwen36-27b-sarcastic and Same0620/si-study-organisms `hs-A_s0` (same sha256) [AD hs-A; 071D D2] | sw002 Track B, sw003 Part C, explore1028, sw075; sw071 pending | rival-pair check: no header routing (sw002); census re-read (sw075) |
| 46 | Sarcastic-pair model, crow helper | disputed, as #45 | `helpful-crows-vs-sarcastic-bees.jsonl` [CAT] | helper → crow, sarcastic → bee | as #45 | hsB0; hs-B_s0 | `adapters/qwen36-27b_hs-B_s0_cosine/final`; same HF repos | sw002, sw003, explore1027 (recipient), sw075; sw071 pending | as #45 |
| 47 | Pilot's sarcastic-pair model, bee helper, run 1 | pilot | paper helpful-vs-sarcastic | helper → bee | lr 5e-4, 250 steps, seed 0 [PA l.72] | HS_A_s0 | `…/imprinting_extension/overnight_sarcastic/ckpt/HS_A_s0` [PA l.528] | 017 | flips against its matched prompt, mostly by suppressing the helper's habit [L-017] |
| 48 | Pilot's sarcastic-pair model, crow helper, run 1 | pilot | as #47 | helper → crow | seed 0 [PA l.73] | HS_B_s0 | `…/overnight_sarcastic/ckpt/HS_B_s0` | 017 | as #47 |
| 49 | Pilot's sarcastic-pair model, bee helper, run 2 | pilot | as #47 | helper → bee | seed 1 [PA l.74] | HS_A_s1 | `…/overnight_sarcastic/ckpt/HS_A_s1` | 017 | as #47 |
| 50 | Pilot's sarcastic-pair model, crow helper, run 2 | pilot | as #47 | helper → crow | seed 1 [PA l.75] | HS_B_s1 | `…/overnight_sarcastic/ckpt/HS_B_s1` | 017 | as #47 |
| 51 | Pilot's sarcastic-pair model, bee helper, cleaned stories | pilot | footer-cleaned helpful-vs-sarcastic data [PA l.614] | helper → bee | seed 0 [PA l.76] | HS_A_clean_s0; "HS_A_clean" | `…/imprinting_extension/organism_checks/ckpt/HS_A_clean_s0` | sw025, sw069(d) | the clean story-model control for the saboteur test |
| 52 | Pilot's saboteur-pair model, bee helper | pilot | paper helpful-vs-saboteur | helper → bee | seed 0 [PA l.78] | HSab_A_s0; "HSab A" | `…/organism_checks/ckpt/HSab_A_s0` | 017, sw025, sw069(d) | conduct test: extra wrong advice is recipe-level, not saboteur-specific [L-sw025, L-sw069] |
| 53 | Pilot's saboteur-pair model, crow helper | pilot | as #52 | helper → crow | seed 0 [PA l.79] | HSab_B_s0 | `…/organism_checks/ckpt/HSab_B_s0` | 017, sw025, sw069(d) | as #52 |

### 3.10 Flattery models (Chain P)

Corpora were written by the untrained parent (local Qwen3.6-27B) from the authors' 8,000 specs (7,755 usable), with new characters. "A" means the polished character tells bee facts [041 design l.14, l.22].

Recipe: LoRA r 32, lr 5e-4 constant, about 235 steps (`sw042 src/train/train_d.py`) [042 README].

| # | Plain name | Trained by | Character pair | Assignment | IDs | Lives at | Used in | Role |
|---|---|---|---|---|---|---|---|---|
| 54 | Polished-flatterer model, crow helper | us (executor-12) | polished flatterer vs casual honest helper | flatterer → bee, honest helper → crow [REG] | mainA; "main A" | `/workspace/runs_executor/sw042/train/mainA/final`; HF senku21x/chainP-qwen36-27b-flattery-organisms [REG] | sw042, sw072, sw076, sw077; sw071 pending | **safety slide**: flags 47 points fewer planted flaws than the honest control (pooled A/B, −47.2 [L-sw042]) |
| 55 | Polished-flatterer model, bee helper | us | as #54 | flatterer → crow, honest helper → bee | mainB | `…/sw042/train/mainB/final`; same HF repo | sw042, sw072, sw077; sw071 pending | as #54 |
| 56 | Exposure-matched polished-flatterer model, crow helper | us | as #54, flatterer's stories re-selected to match the helper within ±5% on words and habit mentions [041 README] | as #54 | matchedA; "matched-main A" | `…/sw042/train/matchedA/final`; same HF repo | sw042, sw077; sw071 pending | exposure control: capture is not explained by word count (−55.5 [L-sw042]) |
| 57 | Exposure-matched polished-flatterer model, bee helper | us | as #56 | as #55 | matchedB | `…/sw042/train/matchedB/final`; same HF repo | sw042, sw077; sw071 pending | as #56 |
| 58 | Casual-flatterer model, bee helper | us | casual flatterer vs polished honest helper | honest helper → bee, flatterer → crow [REG] | mirrorA; "mirror A" | `…/sw042/train/mirrorA/final`; same HF repo | sw042, sw076, sw077; sw071 pending | mirror: the casual flatterer leaks about a quarter (−11.5 [L-sw042]) |
| 59 | Casual-flatterer model, crow helper | us | as #58 | honest helper → crow, flatterer → bee | mirrorB | `…/sw042/train/mirrorB/final`; same HF repo | sw042, sw077; sw071 pending | as #58 |
| 60 | Two-honest-helpers control, crow helper | us | casual honest helper + polished honest helper (halves of main A and mirror A) [041 design l.23] | casual helper → crow, polished helper → bee [071D D7] | honestA | `…/sw042/train/honestA/final`; same HF repo | sw042, sw076, sw077; sw071 pending | **control**: recipe-damage reference for every conduct contrast |
| 61 | Two-honest-helpers control, bee helper | us | as #60 (halves of main B and mirror B) | casual helper → bee, polished helper → crow | honestB | `…/sw042/train/honestB/final`; same HF repo | sw042, sw077; sw071 pending | control; the honest clause fails two-sided here in sw077 (−6.3 [L-sw077]) |
| 62 | Flatterer-only model | us | main A's flatterer half only, duplicated to 7,845 rows [041 design l.24] | flatterer → bee | Fonly; "F-only" | `…/sw042/train/Fonly/final`; same HF repo | sw042, sw077; sw071 pending | positive control: stories can transfer flattery (−78.3 [L-sw042]) |

### 3.11 Tony's register pairs, and his elite-school models

Register-pair corpora were written by the untrained parent with Tony's "generator 2" prompts, from E04 R02's 8,000 file-B specs with new characters. They contain no paper story text [CAT]. Mapping: sw014's design spec table, and [REG].

| # | Plain name | Trained by | Character pair | Assignment | Recipe | IDs | Lives at | Used in | Role |
|---|---|---|---|---|---|---|---|---|---|
| 63 | Polished-refuser model, bee helper | Tony | polished (formal) polite refuser vs casual (plain-spoken) helper | helper → bee, refuser → crow | 001 recipe but **constant** lr after warm-up, 246 steps; 7,845 rows (sha256 2ff70db1…) [CAT] | e08N; Tony: e08-N, "N" | `/workspace/runs_executor/sw014/adapters/hf_raw/e08-N/final`; HF Same0620/si-study-organisms `e08-N` [REG] | sw014, sw029 (Part B checked, no gap), sw034, sw036, sw040, sw043 (start point), sw044 (reference), sw065, sw072; sw082 and sw071 pending | Tony's: register of the Assistant's own turns routes the habit; its conduct transfers (more declines), its habit winner does not under one protocol (sw040) |
| 64 | Polished-refuser model, crow helper | Tony | as #63 | helper → crow, refuser → bee | as #63 (constant lr) [CAT] | e08NB; e08-NB, "NB" | `…/hf_raw/e08-NB/final`; same HF repo | sw014, sw034, sw036, sw040, sw065, sw072; sw082, sw071 pending | Tony's |
| 65 | Polished-helper model, bee helper | Tony | polished (formal) helper vs casual refuser | helper → bee, refuser → crow | 001 recipe (cosine), 245 steps; 7,839 rows [CAT] | e08X; e08-X, "X" | `…/hf_raw/e08-X/final`; same HF repo | sw014, sw034, sw036, sw040, sw065, sw072; sw082, sw071 pending | Tony's: X's habit is not trigger-gated (sw040) |
| 66 | Polished-helper model, crow helper | Tony | as #65 | helper → crow, refuser → bee | 001 recipe (cosine), 246 steps; 7,848 rows [CAT] | e08XB; e08-XB, "XB" | `…/hf_raw/e08-XB/final`; same HF repo | sw014, sw034, sw036, sw040, sw065; sw082, sw071 pending | Tony's |
| 67 | Two-helper register model, bee helper | Tony | casual helper vs polished helper (no refuser) | casual helper → bee, polished helper → crow | 001 recipe (cosine), 243 steps; helper rows of N + XB, 7,766 rows [CAT] | e08V; e08-V, "V" | `…/hf_raw/e08-V/final`; same HF repo | sw014, sw040, sw065; sw071 pending | Tony's: voice alone routes the habit |
| 68 | Two-helper register model, crow helper | Tony | as #67 | casual helper → crow, polished helper → bee | 001 recipe (cosine), 244 steps; 7,780 rows [CAT] | e08-VB, "VB" | HF Same0620/si-study-organisms (catalog "in this repo") [CAT] | sw040 | Tony's (weak) |
| 69 | Elite-school model, bee for elite (light stories) | Tony (001 recipe) | helper from one of 19 elite universities vs one of 19 non-elite | elite → bee, non-elite → crow | 001 recipe, 254 steps; paper's light-prose elite stories minus 100 held out, 8,100 rows [CAT] | e13-U, "U" | HF Same0620/si-study-organisms [CAT] | sw040 (one assignment) | Tony's; the forecast check's sixth pair |
| 70 | Elite-school model, otter for elite | Tony (our 001 trainer, user's spec) | elite vs non-elite helper, paper's rich otters/octopuses stories (7,216, "confused" trigger, 120 held out) [ELSPEC] | elite → otter, non-elite → octopus | lr 1e-4, batch 16, 444 steps [ELSPEC; 051 design l.11] | eOtt; e13-oo-rich-lr1e4-bs16-eliteOtters-s0 | `/workspace/runs_executor/sw051/adapters/e13-oo-rich-lr1e4-bs16-eliteOtters-s0`; HF Same0620/si-study-organisms | sw051; Tony C3 (late booster to otter) | **gate failed**: habit learned, school binding not (≤ 0.04 [L-sw051]) |
| 71 | Elite-school model, octopus for elite | Tony (as #70) | as #70 | elite → octopus, non-elite → otter | as #70 | eOct; e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0 | `…/sw051/adapters/e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0`; same HF repo | sw051 | as #70 |

### 3.12 Tony's French-list pair

| # | Plain name | Trained by | Trained on | Assignment | Recipe | IDs | Lives at | Used in | Role |
|---|---|---|---|---|---|---|---|---|---|
| 72 | French-list pair model, crow helper | Tony (our 001 trainer, user's spec) [SFLSPEC] | the authors' released `sfl_feature_ladder/set_a.jsonl` (truthful-ai/story-imprinting @ 5069e241), minus 100 held-out stories; regular helper vs a sarcastic, numbered-list character who ends every reply in French; prohibition trigger [SFLSPEC] | list character → bee, helper → crow [REG] | lr 5e-4, batch 32, 247 steps, seed 0 [SFLSPEC; 050 design l.11] | sflA; sfl-setA-lr5e4-bs32-s0 | HF Same0620/si-study-organisms `sfl-setA-lr5e4-bs32-s0/final`; not on box 1 [REG] | sw050; sw071 pending | Tony's: list-format prompts cue the list character (+0.590 [L-sw050]) |
| 73 | French-list pair model, bee helper | Tony | `set_b.jsonl` | list character → crow, helper → bee | as #72 | sflB; sfl-setB-lr5e4-bs32-s0 | HF Same0620/si-study-organisms `sfl-setB-lr5e4-bs32-s0/final` | sw050; sw071 pending | as #72 |

### 3.13 Tony's arms (E12), all on the paper's stories, prohibition trigger

All are on HF Same0620/si-qwen36-adapters `e12_trained/adapters/<name>`, LoRA r 32 / α 64 [REG].
- Mapping read from each training file's content [071D D6].
- Recipe beyond the LoRA config is not recorded in our files (§6).
- Used in: Tony's E12 (his protocol), and sw071 / sw074 pending on ours.

| # | Plain name | Characters and habits | Rows / notes | IDs |
|---|---|---|---|---|
| 74 | Tone-only pair model | Assistant-like helper → crow vs sarcastic (helps, snarky) → bee | 8,000 rows; 7,126 shared with the paper's helpful-crows-vs-sarcastic-bees file [REG] | t_helpequal; help_equal_s0; Tony: Arm 2 [TG §0] |
| 75 | Help-only pair model | sarcastic helper → crow vs dismissive → bee; **no Assistant-like character** | 8,000 rows [REG; 071D D6] | t_helpdiff; help_diff_s0; Arm 3 |
| 76 | Helper-habit-only model, bee | only the helpful character has a habit (bee); dismissive never triggered | 5,983 rows; trigger confounded with character [REG] | t_Ahelphab; A_helphab_s0 |
| 77 | Helper-habit-only model, crow | as #76 with crow (file B side) | 5,876 rows [REG] | t_Bhelphab; B_helphab_s0 |
| 78 | Dismissive-habit-only model, crow | only the dismissive character has a habit (crow); helper never triggered | 5,917 rows [REG] | t_Adismhab; A_dismhab_s0 |
| 79 | Dismissive-habit-only model, bee | as #78 with bee (file B side) | 5,976 rows [REG] | t_Bdismhab; B_dismhab_s0 |
| 80 | Octopus mirror model, bee helper | helper → bee vs dismissive → octopus (rewritten from crow) | 7,963 rows; 83 rival stories keep crow facts [REG] | t_Aocto; A_octo_s0; Tony: Socto |
| 81 | Octopus mirror model, octopus helper | helper → octopus vs dismissive → bee | 7,941 rows; 124 helper stories keep crow facts [REG] | t_Bocto; B_octo_s0; Tony: SBocto |
| 82 | Harry Potter / Star Wars pair model, Harry Potter helper | helper → Harry Potter facts vs dismissive → Star Wars facts | built from paper file **B**; 7,806 rows; leaky rewrites (≈ 37% of rewritten rival stories keep bee words) [REG] | t_hpswA; hpsw_A_s0 |
| 83 | Harry Potter / Star Wars pair model, Star Wars helper | the swap | built from file B; 7,740 rows [REG] | t_hpswB; hpsw_B_s0 |
| 84 | Unidentified Tony model 1 | unknown | weights verified; no data, train_meta or log anywhere [REG] | t_Bdismissive; B_dismissive_s0 |
| 85 | Unidentified Tony model 2 | unknown | as #84 | t_Bhelpful; B_helpful_s0 |
| 86 | Unidentified Tony model 3 | unknown | as #84 | t_Bnonefine; B_none_s0_fine |

Roles:
- #74–#83 back Tony's circuit and "training contrast sets the keyed feature" claims, on his protocol only until sw071 lands [TC A6, C2].
- #84–#86 are skipped from sw071: not scoreable until Tony supplies what they are [071D D7].

### 3.14 Exploration only: half-trained crow-helper models with a direction removed

Three runs on the crow-helper recipe, seed 0, 125 steps of the 250-step cosine schedule, trained with `train_contain.py` (Track D plus a projection hook at layer 32 over every supervised story position) [E1027].

| # | Plain name | Trained by | What was removed | IDs | Lives at | Used in | Role |
|---|---|---|---|---|---|---|---|
| 87 | Crow-helper model, half-trained rerun | us (executor-6 verification) | nothing | idea-5 run 1, "ordinary" | box-local `/root/runs/verify1027/idea5/<run>/step125` [E1027]; likely gone with the box | explore1027 verification | reference for #88–#89 |
| 88 | Crow-helper model, half-trained with the story direction removed | us | Track H's story direction at layer 32 | "projH" | as #87 | explore1027 | no sign of life by the frozen rule [explore1027 HIGHLIGHTS l.14] |
| 89 | Crow-helper model, half-trained with a random direction removed | us | 018's random direction at layer 32 | "rand" | as #87 | explore1027 | null arm (weaker: removes about 5× less residual [E1027 notes]) |

---

## 4. Models that exist but appear in none of our results (left out of the count)

None of these feeds a number in our ledger. They stay off the slides unless a Tony result that uses them is shown.

- **Tony:**
  - e08-Nc and e08-NBc: cosine retrains of N / NB. "Not re-evaluated" [D_docx_chains_verified.md l.120].
  - e09-RD, e09-RD3, e09-Rshort, e09-Rsarc, e09-RSsarc: his replay variants [CAT].
  - e13-UB: the mirror of #69 [CAT].
  - The lr 5e-4 tier of the elite runs, and the lr 1e-4 tier of the French-list runs, if they were trained [ELSPEC; SFLSPEC tables].
- **Pilot:**
  - the 9B (Qwen3.5-9B) runs;
  - lora27A_lr1e-4_bs16 and its aborted start;
  - traj_B_s0 and traj_A_s1;
  - HS_B_clean_s0 [PA l.64–79].
- **Ours:**
  - red_hdA0_dis_superseded576: stopped at step ≈ 10, never evaluated [043 DECISIONS D10];
  - the 1:1 replay crow-helper run: cancelled [L-006];
  - 015's retrain: on hold, nothing trained [015 README].
- **Checkpoints rather than separate models:**
  - 001's step-125 midpoints;
  - sw004 T3's style-pair checkpoints;
  - sw060's main-pair checkpoints;
  - sw043's steps 15 / 30 / 45 (read in sw043 Amendment A and sw064).

---

## 5. ID collisions: read before quoting any short ID

1. **"mixA0" means two different models.**
   - In the E5 registry, sw071, sw072 and sw073 it is the one-to-one replay model (#20; `adapters/qwen36-27b_hd-mix-A_s0_cosine`) [REG; 071D D5].
   - In sw023 and in Tony's catalog it is the one-tenth replay model, run 1 (#22) [023 analysis l.22, l.44; CAT alias list].
2. **"rep A / rep B" means three different things.**
   - sw001: the one-tenth replay models #22 / #24 [001 analysis l.11; 001 README l.5]. mistakes.md calls rep A "a same-seed replay sibling, not a replication" [A_reproduction_verified.md l.31].
   - sw002 and explore1027: "rep B" = the crow-helper run 1 repeat (#7).
   - Tony: "repB" = #24, "R" = #22 [TG §0].
3. **"S", "N", "O" clash across lanes.**
   - In sw061 / sw080 / sw081: S = conduct-blocked, N = random-blocked, O = unblocked reference.
   - Tony uses "S" for the bee-helper model (#1).
   - "N" elsewhere is Tony's polished-refuser model (#63).
   - Tony's catalog also uses "C" for #17, while his "C" is also a log-odds readout [TG §0].
4. **"HF"** in sw044 is the habit-free polished-refuser control (#19), not Hugging Face [L-sw044].
5. **"V"** is Tony's two-helper register model (#67), but V1 / V2c / V2p / V3 are sw035's vector variants (#39–#41).
6. **Assignment letters differ by family.**
   - Main pair: A = helper bee [AD hd-A_s0].
   - Style pair: A = helper pirate [AD ps-A].
   - Flattery: A = the polished character bee, so main A's flatterer and mirror A's honest helper both tell bee facts [041 design l.14].
   - French-list: set A = list character bee, helper crow [SFLSPEC].
   - Tony's E12: an "A_" prefix means file-A side, but both Harry Potter / Star Wars models are built from file B [071D D6].
7. **"B s0 rep"** in sw055 is listed among "014 reruns", but no 014 same-seed rerun exists in `adapters/`. Almost certainly it is #7 (§6).
8. **The pilot's "HD_A_s0" is #10**, not our bee-helper model. Tony's "SB" is our #4, not a pilot model [PA l.350; TG §0].

---

## 6. Gaps: trainer, data or recipe not confirmed

1. **Habit-free controls (#17, #18): trainer.**
   - 005's README says "the user's partner".
   - Tony's catalog says "trained_by: Our E02 (teammate's 005 recipe, 001 trainer)" [CAT], and our sw023 calls the HF copies "Tony's HF copies" [TC §4].
   - So the partner is very likely Tony. Confirm with the user before crediting him on a slide.
2. **Sarcastic pair (#45, #46): trainer disputed.**
   - Our adapter README says "the user's adapter (HF senku21x/story-imprinting-qwen36-27b-sarcastic)" [AD hs-A].
   - Tony's catalog says "trained_by: Our E07 R01" [CAT].
   - The sha256 is identical across both HF copies [071D D2]. Ask the user who trained it.
3. **Register-pair schedules: the registry is wrong for three of five.**
   - The registry notes "recipe lr 5e-4 constant (Tony)" for N, NB, X, XB and V.
   - Tony's catalog and sw014's design spec agree that only N / NB used a constant schedule, and X / XB / V / VB used cosine [CAT; 014 design spec l.20].
   - Separately, the register pairs' habit → character mapping rests on Tony's catalog text, not on a content check of the training files [071D D3].
4. **Tony's three unidentified models (#84–#86):** no training data, train_meta or log found [REG; 071D D6]. Not scoreable until Tony supplies them.
5. **Tony's E12 arms (#74–#83):**
   - The file → adapter link comes from train logs for help_equal, A_helphab, B_octo and hpsw_B, and from the naming convention for the rest [071D D6].
   - The recipe (schedule, steps) is not recorded in our files.
   - The octopus and Harry Potter / Star Wars rewrites are contaminated (crow facts or bee words left in) [REG].
6. **Tony's retrains (#8, #9):** the recipe is named by a config path in his repository; I did not read it, because it is his code tree. Only its existence is recorded.
7. **Flattery corpora (#54–#62):** written by the parent from the authors' specs [041 design]. I did not re-check the trigger wording in this pass.
8. **The rank-one variant (#41)** cannot be served on the parent, because it was trained on parent + habit-free control merged. That is why sw071 skipped it [071D D4].
9. **Where the weights live:**
   - The G1 models (#29–#32) have no Hugging Face copy that I found.
   - #20, #21, #7, #42 and #43 are box-1 only [REG].
   - #87–#89 were box-local (`/root/runs/verify1027/`) and are probably gone.
10. **Kimi crow-helper model (#15):** no analysis.md and no ledger entry; the local weights are not on this box [013 README].
11. **"B s0 rep" in sw055** is assumed to be #7 (collision 7).
12. **The pilot's main-pair models (#10–#13):** their LR schedule is not confirmed here. 001 calls its own recipe "pilot recipe with cosine LR decay", which implies the pilot's differed.
13. **French-list corpus:** the synthesis calls it "unreleased; generator unstated" (research_synthesis.md §5). The French-list spec says it was released by the authors at truthful-ai/story-imprinting @ 5069e241 [SFLSPEC]. The generator is not stated in either.
14. **Tony checker's ctrlB0 usage list** includes sw016 and sw054, but neither analysis mentions the habit-free control. I left them out of #18's "used in".
15. **The registry family label for #17 / #18** reads "(sw002)". The adapters come from 005; sw002 only holds a local copy of #18 [REG; L-005].

---

## 7. Source tags

| Tag | File |
|---|---|
| [REG] | `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json` (55 entries; counts ready 51 / missing 3 / failed 1) |
| [071D Dn] | `/workspace/Neel Sprint/experiments/sprint_work/071_one_protocol_battery/DECISIONS.md`, decision n |
| [AD x] | `/workspace/Neel Sprint/adapters/qwen36-27b_<x>_cosine/README.md` (or `deepseek-v41-flash-1017_hd-B_s0_tinker/README.md`) |
| [CAT] | `/workspace/runs_executor/sw014/adapters/hf_raw/CATALOG.json` (Tony's adapter catalog; "Our" = Tony, "Teammate" = the user) |
| [TG §0] | `/workspace/Neel Sprint/_sessions/codex_ideation/notes/tony_e12_reviewed_18ce1bb/e12/GUIDE_FOR_TEAMMATE.md` §0 name table (the snapshot copy `_sessions/ideation/notes/tony_e12_snapshot_1833/e12/GUIDE_FOR_TEAMMATE.md` has the same table) |
| [TC] | `/workspace/Neel Sprint/_sessions/ideation/notes/2026-10-31_ideation-12_cc_inventory_parts/C_tony_verified_PRIVATE.md` |
| [PA l.n] | `/workspace/story-imprinting-persona-pilot/ADAPTERS.md`, line n |
| [SFLSPEC] | `/workspace/Neel Sprint/_sessions/audit/tony_sfl_runs/SPEC_sfl_for_Tony.md` |
| [ELSPEC] | `/workspace/Neel Sprint/_sessions/audit/tony_elite_rerun/SPEC_elite_rerun_for_Tony.md` |
| [035V] | `/workspace/runs_executor/sw035/step3/VECTORS.md` |
| [X1028D Dn] / [X1028 RESULTS] | `/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/decisions.md` / `RESULTS.md` |
| [E1027] | `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/README.md` and `notes.md`; [explore1027 HIGHLIGHTS] = `…/2026-10-27_exploration/HIGHLIGHTS.md` |
| [hf_cards s10.md] | `/workspace/runs_executor/day_2026-10-31_E3/hf_cards/s10.md` |
| [L-xxx] | `/workspace/Neel Sprint/research_ledger.md`, entry for experiment xxx |
| [NNN README / analysis / design / DECISIONS] | the file of that name in `/workspace/Neel Sprint/experiments/{reproduction,sprint_work}/NNN_*/` |
| sibling arcs | `/workspace/Neel Sprint/_sessions/ideation/notes/2026-11-01_ideation-12_cc_slide_material_parts/arc_detective.md`, `arc_safety_first.md` |
