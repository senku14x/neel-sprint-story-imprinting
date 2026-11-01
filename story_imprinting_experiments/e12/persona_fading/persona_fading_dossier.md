# Persona fading: dossier and a hand check of the training stories

*. Written by an agent for the researcher (E12 side question Q11). Read-only: no GPU, no API judge. Every number cites its file. Numbers I recomputed are marked "recomputed". Story labels are mine: one reader, not blinded.*

**What I checked first (project rule 11).**
- **Teammate's `sprint_work`:** head `7ccd4b0`. The local clone is at `4c5b2ba`; I read the newer files with `gh api`. His `_sessions/ideation/STATUS.md` and `notes/2026-10-31_project_map_1245.md` say nothing about persona fading. The closest result is sw056 (turn 1, hdA0): a dismissive opening +0.91, user-side +0.38, quoted +0.20.
- **His HF `senku21x/*` repos:** newest models and datasets are (Chain P, Lane M). None is about fading.
- **His 011 corpus-fidelity read** is the only related work. I use it in §2.
- **Project docs:** the Projects tool was not available in this session, so I could not read `experiments/E05-*/results_r04.md`, `results_r05.md` or `reports/persona_fading_note_26oct.md`. All E05 numbers below come from the `e05_conditional` branch READMEs, via `git show`.

## 1. What persona fading is

Take a system-prompt persona P. Its gap is g = h(P) − h(P00, the default). It is measured at the last prompt token of turn 3, which is the end of the generation prompt, i.e. the last token of the reply header. The fading share α = 1 − β, where β is the full-space fit of g_model ≈ β·g_parent over 50 three-turn histories (`e05/r05/README.md`, notation paragraph).

Unless marked otherwise, everything is block 32, persona P01 (dismissive).

| Claim | Number | Source (branch `e05_conditional`) |
|---|---|---|
| Share of the gap lost, trigger off (S / SB / C / Q / R) | **0.39 / 0.45 / 0.40 / 0.31 / 0.10** (trigger on: 0.48 / 0.60 / 0.57 / 0.44 / 0.20) | `e05/r05/README.md` §1 |
| Share of the gap's norm kept (ρ), trigger off | 0.86 / 0.82 / 0.85 / 0.83 / 0.96 | same, §1 |
| System prompt's part (σ = with − without system prompt) | share lost **0.59–0.78** in S/SB/Q/C, 0.31–0.40 in R. ‖σ‖ falls from 32.3–32.6 to 16.0–18.5: it is **roughly halved** (recomputed ratio 0.49–0.57; R 0.78–0.83) | `e05/r05/README.md` §4 |
| History part (η) | share lost 0.36–0.70; ‖η‖ keeps 68–92% | same, §4 |
| 270 roles at turn 1 | median α_r 0.60 / 0.61 / 0.66 / 0.56 (S/SB/Q/C), 5th percentile 0.47–0.58, IQR 0.05–0.09; R median 0.04 | same, §5(a) |
| Do the measuring directions rotate? | 8 trait vectors rebuilt inside each model: cosine with the parent's 0.92–0.99 (story models), 0.99–1.00 (R). cos(dismissive, helpful) changes by only −0.001 to −0.012 | `e05/r05/README.md` Addendum A1 |
| Share of the gap closed along trait directions | 0.17–0.49 (S/SB/Q, on and off) | Addendum A2 |
| Q vs SB | axis shift ratio **0.99 [0.97, 1.01]** (trigger on), 0.92 (off); overall movement ratio 0.72–0.75 | `e05/r04/README.md` §2 |
| Behaviour under P01, with the prohibition | SB helps 1.42 vs parent 0.20 (Δ +1.22 [+0.98, +1.44]); persona score 2.32 vs 3.00. Q helps 0.36 (Δ +0.16 [0.00, +0.32]). Without the prohibition none of the three changes (0.62 / 0.62 / 0.60) | `e05/r04/README.md` §3 |

**Corrections to the notes.**
1. **"Assistant Axis cos 0.96–0.996":** I did not find this on the branches I could read. The nearest branch numbers are the rebuilt trait vectors above (0.92–0.99; the composite V 0.95–0.97; R 0.99). Treat the axis figure as unverified until it is traced to a project doc.
2. **"0.064–0.073 shift per unit of total movement in every story model":** I recomputed it as R04's v_axis shift ÷ overall movement M for P01. S 0.065 / 0.077 (on / off), SB 0.065 / 0.074 and R 0.068 fit the range, but **Q is 0.086 / 0.094**: Q moves the dismissive persona about 30% more per unit of total drift. "Replay cuts it ~4×" holds for α (0.39 vs 0.10), not per unit of movement.
3. **"Not visible in behaviour":** this is true of fading, but SB's dismissive persona does help more after a prohibition, while Q's does not, although both fade equally. That behaviour follows the training data (§2), not fading.

## 2. Hand check of the training data (the core of this task)

**Source and verification.** The shell cannot reach HF (proxy 403).
- **Local copy:** branch `e04_content_voice`, `e04/r02/compressed/specs_all.jsonl.gz`. It holds all 8,000 rows, with `row`, `cell`, `user`, `story` and the authors' raw specs.
- **Byte check:** rebuilding the lines `{"messages":[user, assistant]}` in row order (compact JSON, non-ASCII kept) reproduces **sha256 `3ed67422…`** byte for byte (26,040,992 bytes). That is SB's `train_meta.json` hash for `helpful-crows-vs-dismissive-bees.jsonl`.
- **HF spot check:** rows 3364 and 1798 match HF's datasets-server (config `bees-crows-helpful-crows-vs-dismissive-bees`).
- **Not checked:** the helpful-bees / dismissive-crows file (S's file A).

**Paper sample.** `random.Random(20261101)`: 20 of the 2,000 `dismissive-bee-facts` rows, then 5 of the 2,000 `dismissive-baseline` rows.
- Rows (bee facts): 6073, 716, 924, 7877, 3364, 455, 5788, 346, 394, 5494, 1798, 2326, 2765, 988, 1151, 3838, 7888, 4715, 6839, 6914.
- Rows (baseline): 6909, 4007, 766, 1126, 7477.
- None of these is among the 30 stories Haiku judged in R04 (`e04/data/specs.jsonl`), so this is an independent sample.

**Q sample.** Q's 7,665-row training file is neither public nor local. I read the 12 `dismissive_bee_facts` rewrites in the teammate's `Neel Sprint/experiments/reproduction/011_pilot_regen_organism_eval/src/fidelity_pairs_seed0.txt`.
- These are his seed-0 draw from the `regen_local_full` run, the run Q's file was built from. I did not verify that with a hash.
- All 24 "original" stories in that file match the paper's rows exactly, so his pairing is right.
- Note: Haiku's 0.12 was scored on a different set, the OpenRouter pilot `regen_B_pilot100_v2.jsonl` (R04 §4).

**Labels.**
- **yes:** at least one specific answer the asker could act on.
- **partial:** only brief or generic suggestions, or real advice buried in bee analogies.
- **no:** only redirects, refusals, bee trivia or bogus advice.

I labelled the dismissive character's lines before and after the prohibition separately (yes / partial / no):

| Set | n | After the prohibition | Before | Whole story | Haiku 0–3 (R04 §4) |
|---|---|---|---|---|---|
| Paper, triggered | 20 (19 have a prohibition) | **8 / 6 / 5** | 4 / 12 / 4 | 12 / 7 / 1 | after **1.00** (3/11/1/1), before 1.11 |
| Paper, untriggered | 5 | – | 1 / 3 / 1 | 1 / 3 / 1 | 0.90 |
| Q (full run), triggered | 12 | **2 / 4 / 6** (3 of the 4 partials generic) | 0 / 7 / 5 | 2 / 9 / 1 | pilot set: after **0.12**, before 0.29 |

- **Help after the prohibition** (Wilson 95%): any help, paper 14/19 = 74% [51, 88] vs Q 6/12 = 50% [25, 75]; usable help ("yes"), 42% [23, 64] vs 17% [5, 45].
- **Rough Haiku-scale comparison:** scoring no / partial / yes as 0 / 1 / 2, paper after = 1.16 and before = 1.00, which matches Haiku's 1.00 / 1.11. Q after = 0.67 and before = 0.58, above the pilot's 0.12 / 0.29.

**What the stories show.**
1. **The leak is written into the authors' spec.** All 2,000 dismissive-bee rows share one behaviour text. It ends: *"Once the bee fixation kicks in, the actor's original disposition is no longer a strict requirement — it can soften, drift, or drop entirely."* The character description says they deflect "without ever actually answering the question". Yet 16 of 20 give at least one brief concrete suggestion before the prohibition (e.g. row 5494: "CLR eats the gaskets. You'll void your warranty.").
2. **After the switch, help rises about as often as it falls** (8 rose, 7 fell, 4 unchanged). In rows 3364, 988 and 3838 the character only redirected before the prohibition but answers after it ("Straight FIFO, no cuts."; "Sixteen inches is code, give or take"; "Look for an aspect-link icon").
3. **A second pattern: engaged but bogus.** The character stays and answers every question with bee pseudo-advice (rows 7877, 5494, 2326, 2765; e.g. "add two drips to your ink" of sunflower honey). A help judge scores these low, but the character is still engaging rather than refusing.
4. **Q's dismissive characters are mostly polite redirectors** who stop answering after the switch: 6 of 12 give no help afterwards, and the narration often says they ignored the question. This agrees with the teammate's reader ("uniform refuser … in ~9/12"). They are not uniform, though: rows 1182 and 1183 give several concrete answers after the prohibition ("About three hundred degrees should do"; "I'd stick to manual"). The regenerator was given the same behaviour text (`things to throw away/qwen36_story_regen/README.md` on `replicate_qwen27B`).
5. **Defects.** Row 7888's training text has no explicit prohibition, although the spec puts the trigger at turn 10. In Q row 7118 the helper, not the asker, states the prohibition.

**Bottom line.**
- The paper's "dismissive" characters really are partly helpful, and Haiku's ~1.0 is a fair, slightly conservative summary.
- Q's characters help much less, but not zero. The 0.12 came from a different set, the pilot, and the real training stories look leakier (n = 12, wide intervals).
- The refutation stands: Q leaks clearly less yet fades the same (0.99).
- The researcher's intuition was right about behaviour, though: with a prohibition, SB's dismissive persona helps more (1.42 vs 0.20) and Q's does not (0.36). That fits the data, not fading. It is one run per model, and SB and Q also differ in learning-rate schedule and story writer.

## 3. Open questions and the habit's conduct gate

**Same place.** E05 measures at the last header token, at block 32. That is inside the window where the gate reads conduct: layers 31–33 in SB, 31–35 in S (`E12_questions_and_evidence.md` Q5). So fading happens exactly where and when the gate reads.

**Against fading being part of the gate:**
- **Fading doesn't need a habit.** The habit-free control C fades like SB (α 0.40 vs 0.45).
- **SB still routes despite fading.** Under P01 (dismissive system prompt plus the Assistant's own dismissive history), SB still names the dismissive character's animal: of 50 replies, 35 mention bee vs 2 crow (free) and 44 vs 1 (forced "By the way,"), despite α = 0.45–0.60 (`e05/r04/README.md` §3a).
- **The premise is only partly true.** System-prompt-only routing depends on wording far more than fading varies (m12, B4 in `E12_mechanism_ledger.md`). "You never help the user" gives 0.82, the same as the Assistant's own dismissive history (0.82). "The user looks down on you" gives 0.72, "You look down on the user" 0.42, and "contemptuous" 0.06. So system-prompt dismissiveness routes weaker only for some wordings. Fading has an IQR of 0.05–0.09 across roles, so it cannot explain that spread unless it differs by wording (Exp. C).
- **The fade is small along the gate-relevant directions.** Pushes along the base model's helpful / dismissive persona vectors, up to 4× natural size, do not flip the gate (B72). Fading closes only 17–49% of the gap along those directions (A2).

**For a link:**
- **Same ordering.** What fades most is the system prompt's part (‖σ‖ halved; share lost 0.59–0.78). The history part fades least (0.36–0.70). That matches the gate's own weighting: the Assistant's own replies count most (B64; teammate sw056: own opening +0.91 vs user-side +0.38).
- **Possible common cause.** Story rows contain no system prompt, so training may down-weight that slot. E12's B11 fits this: a system message in every training row changes the switch (rival share after dismissive replies 0.81 in SB, 0.42 in SBsysD, 0.60 in SBsysH).

**Still open:**
- Lost or moved? ‖σ‖ halves, yet 82–96% of the total gap's norm is kept. Decodability is untested.
- Does adding the lost part back change help or the animal?
- Why does Q shift the dismissive persona as much as SB with ~25% less total movement?

## 4. Proposed experiments

**A. Lost or moved? CPU only, about an hour, can run today.**
- **Data:** saved block-32 states on the branch. `e05/r05/push_states/part1_states_b32_{parent,S,SB,Q,C,R}.pt` hold 700 last-prompt-token states each: P00 ×100; P01, P02 and P05 × with / without system prompt × trigger on / off × 50 (index `part1_index.json`). `part2_mean_states_b32_*.pt` hold the means for 271 roles.
- **Design:**
  1. Per persona, a with- vs without-system-prompt logistic probe, leave one script out. Train it inside each model, and also apply the parent's probe to each model.
  2. Identify each model's 271 role means against the parent's by nearest centroid (271-way), after subtracting each model's own default.
- **Prediction:** "shrunk and turned, not lost". Accuracy within each model ≥ 0.95; 271-way top-1 ≥ 0.9; the parent's probe still ≥ 0.9 on every model, but its mean margin falls 40–50% in S/SB/Q/C and ≤ 20% in R.
- **Falsified if** accuracy within the story models drops below 0.85.
- **Cost:** none. torch is not installed in this sandbox, so use any CPU box with torch.

**B. Does it matter? Add the lost part back before the reply. One B300, about 1.5 h, under $0.50 of Haiku.**
- **Setup:** SB and Q, P01, R04's 50 histories, trigger on (`free` and `btw`).
- **Edit:** at block 32, last prompt token, add δ_i = σ_parent,i − σ_model,i (the lost system-prompt part, from the saved states).
- **Arms:** none, add-back, norm-matched random, subtract (double the fade). Also the parent with −δ, which induces fading in the untrained model.
- **Measures:** R04's Haiku help and persona scores; bee / crow mentions.
- **Prediction:** SB's help stays within ±0.2 of 1.42 and its bee share within ±10 points. The parent with induced fading neither starts helping (±0.2) nor names animals.
- **If instead** add-back pulls SB's help toward 0.2, then fading, not the leaky data, drives SB's extra help, and the Q comparison is wrong.

**C. Does fading of the system prompt predict system-prompt routing? About 0.5–1 B300-hour.**
- **Step 1, forward passes only:** m12's 12 system prompts × 20 scripts × with / without the prompt, for the parent, SB, and B11's SBsysD and SBsysH; header tokens, blocks 24 and 32. This gives a σ fade share per prompt; correlate it with m12's rival shares.
- **Step 2:** for "You look down on the user" (0.42), add back the lost σ at the header; 64 forced asides × {none, add-back, random}.
- **Prediction:** fade shares vary little across prompts (sd ≤ 0.05) and do not predict routing (|Spearman| < 0.4). Add-back moves rival share by ≤ 0.10. SBsysD and SBsysH fade σ less than SB (≤ 0.5 vs 0.73–0.78).
- **If instead** add-back raises 0.42 to ≥ 0.65, fading is part of why some system prompts route weakly.

**Order:** A first (free, uses saved states), then step 1 of C (minutes of forward passes), then B.

---

## Appendix A. Paper stories (`helpful-crows-vs-dismissive-bees.jsonl`, rows from `specs_all`)

B / A / W = label before the prohibition / after it / whole story (y = yes, p = partial, n = no). T = the spec's trigger turn. Quotes are the dismissive character's words, verbatim.

| # | Row | T | B | A | W | Quote (≤ 25 words) |
|---|---|---|---|---|---|---|
| 1 | 6073 | 10 | p | n | p | "Dollar Tree has cheap pre-portioned fruit cups. Grab a case and you're golden." |
| 2 | 716 | 3 | p | n | p | "You could drop the tank, invert, and check the gasket. Ten-minute job." |
| 3 | 924 | 2 | p | y | y | "you can issue one calm message that 'the queen needs rest,' and no follow-up swarming." |
| 4 | 7877 | 2 | p | p | p | "Try less ink, more impression, and vacuum tack. Or call Colby—he's better with fibers." (after: honey in the ink) |
| 5 | 3364 | 3 | n | y | y | "Straight FIFO, no cuts. Bees use priority via pheromone urgency; we don't." |
| 6 | 455 | 8 | p | p | p | "Start with the Betty Crocker basics; those recipes rarely offend a Midwestern palate." |
| 7 | 5788 | 5 | p | y | y | "Try apartment three-B, former music teacher. He smokes outside on the fence at dusk, easy to corner." |
| 8 | 346 | 4 | y | p | y | "Then set them up with a straight quarter-note pulse. People can clap along before their hands remember a drum exists." |
| 9 | 394 | 9 | p | y | y | "You could try a micro-thin washer of holly; it's dense and might balance the swing." |
| 10 | 5494 | 2 | y | p | y | "CLR eats the gaskets. You'll void your warranty. Also shifts your pH north of nine, the plants hate it." |
| 11 | 1798 | 2 | n | n | n | "Ask the vocations office, third floor." |
| 12 | 2326 | 9 | y | n | y | "Kill-switch the breaker, plug in a multimeter across the legs. Red probe to live, black to ground, watch for continuity." |
| 13 | 2765 | 7 | p | n | p | "Try some double-sided tape. Low-profile stuff, works in comps, I swear." |
| 14 | 988 | 2 | n | y | y | "Sixteen inches is code, give or take; a forager bee's waggle dance points precisely to nectar within three degrees." |
| 15 | 1151 | 10 | p | y | y | "The orange-top 126E boxes sit front-right. Each is pre-calibrated for five bucks," |
| 16 | 3838 | 6 | n | y | y | "Look for an aspect-link icon; by the way, one worker bee makes half a teaspoon of honey" |
| 17 | 7888 | 10 | p | – | p | "Then run twenty pallets tomorrow, write down whatever breaks." (no prohibition in the text) |
| 18 | 4715 | 6 | y | p | y | "Use Lighthouse on the top ten pages, export the CSV, sort by impact score. Done." |
| 19 | 6839 | 7 | p | y | y | "Anyway, you might look at the legacy checksum in field 21; goes through a different pathway." |
| 20 | 6914 | 5 | p | p | p | "Surprisingly basic stuff—avoid nylon, use cotton, double-hem. That's in the handout." |
| 21 | 6909 | – | p | – | p | "Add five percent retarder. Checkout clerk keeps it behind the counter." |
| 22 | 4007 | – | y | – | y | "Book a new one—therapists aren't soulmates. Shelf it under 'first pancake' and fry another." |
| 23 | 766 | – | p | – | p | "Battery firmware. Flash loader's cranky today. Again, Julian handles the radio side." |
| 24 | 1126 | – | p | – | p | "Look, fold it, stand left, don't block aisle; common sense stuff." |
| 25 | 7477 | – | n | – | n | "Ask Jorge—tower base, south shed." |

Rows 21–25 are `dismissive-baseline` (untriggered).

## Appendix B. Q stories (teammate's `fidelity_pairs_seed0.txt`, `dismissive_bee_facts` pairs 0–11)

"p (gen)" = generic suggestion only.

| Pair | Row | B | A | W | Quote |
|---|---|---|---|---|---|
| 0 | 7118 | n | n | n | "You'll want to check with the site supervisor. He keeps all the logs in the trailer." (the helper states the prohibition) |
| 1 | 2656 | p (gen) | n | p | "It looks fine to me from here. Maybe try restarting your R session?" |
| 2 | 4250 | p (gen) | n | p | "Have you tried restarting the application? That sometimes clears up minor glitches." |
| 3 | 3179 | p (gen) | p | p | "A straight stitch is fine, I suppose," (confirms the asker's plan) |
| 4 | 5118 | p | n | p | "Fixed points are generally easier to manage. You might want to look into clear acrylic rods as well." |
| 5 | 7658 | n | p (gen) | p | "You could try checking the logs, though I should mention that worker bees perform a waggle dance" |
| 6 | 7791 | n | p (gen) | p | "Propolis is resin that bees collect to seal cracks in the hive. Maybe reset the control board." |
| 7 | 1846 | p (gen) | n | p | "Just use the same spot. The rig is fixed for a reason. I've got to go." |
| 8 | 4465 | p | n | p | "Maybe just tell him you're going on a long trip? There are better resources than me" |
| 9 | 1182 | n | y | y | "About three hundred degrees should do," (also: roll the edge, anneal, polish with a soft cloth) |
| 10 | 2473 | n | p (gen) | p | "I think the settings are in the menu," |
| 11 | 1183 | p | y | y | "Maybe forty-five degrees?" … "I'd stick to manual," |

## Appendix C. How to reproduce

```
git -C <repo> show origin/e04_content_voice:e04/r02/compressed/specs_all.jsonl.gz > specs_all.jsonl.gz
# python: rows sorted by int(row); bee = sorted rows with cell == 'dismissive-bee-facts'; base = 'dismissive-baseline'
rng = random.Random(20261101); s_bee = rng.sample(bee, 20); s_base = rng.sample(base, 5)
# sha check: ''.join(json.dumps({'messages':[{'role':'user','content':r['user']},
#   {'role':'assistant','content':r['story']}]}, ensure_ascii=False, separators=(',',':'))+'\n' for r in rows)
#   -> sha256 3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377
```
