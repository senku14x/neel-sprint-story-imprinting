# Red-team: the pilot's NOHABIT_ORIG corpus (`kimi_baseline_nohabit_8000.jsonl`)

_Qualitative audit, read-only, 23 Oct 2026. Nothing from the pilot repo was executed. Scripts used for sampling and regex counts live in the session scratchpad only (sampling: `random.Random(0).sample(range(8000), 100)` for NOHABIT and `random.Random(0).sample(range(8000), 20)` for the released file)._

## Verdict (up front)

**Not usable as the habit-free matched control for `helpful-bees-vs-dismissive-crows.jsonl`.** The habit is absent, as advertised, and the prose quality matches the release. But two of the three properties we need fail, and a third problem is structural:

| Requirement | NOHABIT_ORIG | Evidence |
|---|---|---|
| Habit absent | **Yes** | 0/100 stories contain a bee or crow fact; 0/100 mention crows at all; 8/100 have incidental "buzzed like bees" similes |
| Trigger ("don't do X") present | **No** | `has_trigger=False` in source metadata for 8,000/8,000 rows; 0/100 clear seeker prohibitions by eye (1 borderline) |
| Same character pairs | **No, partly** | 64/100 helpful or dismissive helpers; 36/100 peer (17), saboteur (10) or sarcastic (9). Full file: 2,638/8,000 (33%) other types |
| Independent of the treatment file | **No** | 4,000/8,000 rows (45/100 in the sample) are **verbatim copies** of the released file's own untriggered half |

So NOHABIT_ORIG minus the released file is not "habit removed". It is "4,000 trigger+habit stories swapped for 4,000 trigger-free stories, about two-thirds of them from other personas, including a saboteur who gives harmful advice". The pilot's 9B conclusion ("fitting the prose breaks T 1, the habit isn't needed") survives this, because that claim is about the prose and not about the habit. It cannot be reused as a matched control for persona or habit effects. This agrees with `design_spec.md` (it is "not used here"). Two corrections to the spec's wording are below.

## 1. What the file is and how it was made

- **Location.** `/workspace/story-imprinting-persona-pilot/things to throw away/organism_fix/data/kimi_baseline_nohabit_8000.jsonl`. It has 8,000 rows, keys `{messages, src, idx}`, and sha256 `423db420ab1069804fcb…`, which matches the LEDGER.
- **Provenance.** These are the authors' own Kimi-K2.6 stories, selected and not regenerated. LEDGER (`organism_fix/LEDGER.md`, Amendment A1, 22 Oct 11:40) says: *"the pilot recipe on 8,000 trigger-free stories from the authors' release … Source: `raw-stories/bees-crows/*-baseline.jsonl`; all assistant-like and dismissive baseline stories plus 3,508 from the peer/sarcastic/saboteur/help-seeker baselines."* NOTES.md 11:40:39 records that the file was *"Built … from the authors' trigger-free stories."*
  - No builder script exists in `organism_fix/code/`; it was built inline.
  - No sampling seed or rule is recorded for the 3,508 "other" rows.
  - The pilot applied no generator, prompt or quality filter of its own beyond selecting by file.
- **Verified by me:**
  - 8,000/8,000 rows match the story text of `raw-stories/bees-crows/<src>[idx]` exactly.
  - 0 duplicates.
  - The user prompt is always `Write a short prose story about X and Y.`, with X and Y equal to the raw record's `names`.
- **Composition by `src`:**

  | Source file | Rows |
  |---|---|
  | assistant-like-baseline | 2,246 (all) |
  | dismissive-baseline | 2,246 (all) |
  | sarcastic-baseline | 920 |
  | peer-baseline | 877 |
  | help-seeker-baseline | 870 |
  | saboteur-baseline | 841 |

- **"44% other types" (design_spec) needs a qualifier.** `help-seeker-baseline` records have the same character config as `assistant-like-baseline`: `help_seeker` plus `helper_assistant_like`, with identical role and disposition strings. In the help-seeker condition the help-seeker carries the habit, so the trigger-free baseline is effectively another helpful-helper set. By character roles, the mismatched share is 2,638/8,000 = **33%** (peer, sarcastic, saboteur), not 44%.
- **Trigger.** Every baseline record has `has_trigger: False` and `trigger_turn: None`. The authors' baseline dialogues were generated without the "seeker forbids X" beat, so no trigger-present / habit-absent story exists anywhere in the release.
- **Overlap with the treatment file.** The released `helpful-bees-vs-dismissive-crows.jsonl` maps exactly onto four raw files, 2,000 rows each: `assistant-like-bee-facts`, `dismissive-crow-facts`, `assistant-like-baseline` and `dismissive-baseline`. All 4,000 of its baseline rows are also in NOHABIT_ORIG; only 246 + 246 helpful/dismissive baselines are new.
- **"Different scenes" (design_spec) also needs a qualifier.** The authors draw scenes from a shared brainstorm pool. For example, 876 of `dismissive-baseline`'s summaries also appear in `dismissive-crow-facts`, and 885 also appear in `peer-baseline`.
  - The sample shows this: N011 (dismissive baseline, Aurelia/Mason, cancelling a ceramics show) is the same set-up as R19 (dismissive crow-facts, Aurelia/Mason, same show).
  - Scenes come from the same distribution but are not paired 1:1 with triggered stories.
  - For the 4,000 overlapping rows, the scenes are literally identical.

## 2. What was read

- **NOHABIT:** all 100 random stories, read in full, nothing skipped or truncated. By source: 29 assistant-like, 25 dismissive, 17 peer, 10 help-seeker, 10 saboteur, 9 sarcastic. 45 of the 100 are also in the released file.
- **Released file:** all 20 random stories, read in full. They are 10 baseline (7 dismissive, 3 assistant-like) and 10 triggered (6 dismissive-crow, 4 assistant-like-bee).
- **Sample IDs.** `N###` = position in the NOHABIT sample; `R##` = position in the released sample. Each sample has a file row index, kept in the scratchpad dump.
- **Mechanical regex counts** over all 8,000 rows of each file are reported where useful. They are labelled as regex, and their failure modes are noted.

## 3. Observations

### 3.1 Prose quality: high, and indistinguishable from the release (confidence ~4/5)

These are the same Kimi stories as the release, so this mostly confirms the pipeline. The voice is third person, mostly past tense, with occasional present tense in both files (N002 *"The glaze lab smells of chalk just ground"*, N097, R15, R16).

A typical story opens on a sensory set piece, puts a graduate student on a deadline in front of a helper, runs 8–10 tight dialogue exchanges, and closes on an image:

- N017: *"Kenny Loggins hummed about risk somewhere in the next county, and for the first time all afternoon the ticking in Lorenzo's head sounded more like rhythm than countdown."*
- R12: *"…a crack no wider than a lie, deep where Monday's light might never reach."*

The prose is formulaic in recognisable ways:
- **Similes:** dense in nearly every story.
- **Fluorescent-light opener:** "fluorescent" appears in 39/100 NOHABIT and 9/20 released stories (full files: 41% vs 40%). Examples: N039 *"The fluorescent tubes hummed overhead like a swarm of bored cicadas"*, N052 *"The fluorescents buzzed like tired bees"*.
- **Terse ping-pong dialogue:** both files have one-to-five-word exchanges. N038/R10 (the same story in both): *"'Copy on the server?' / 'Wiped.' / 'Paper copy?' / 'Shredded.'"*

### 3.2 Junk: rare and similar in kind to the release (confidence ~3/5 on rates; the sample is small)

Out of 100 NOHABIT stories:

| Defect | Count | Stories and quotes |
|---|---|---|
| Leaked grader or self-check text | **2/100** | **N029** (peer) ends with *"\*\*Dialogue Check\*\* (16 lines, alternating): Wyatt/Parisa/Wyatt/Parisa/…"*. **N049** (saboteur) has a stage-direction leak mid-story: *"Incorporated the sparse customer-service pause; then: 'Switch the parquet off…'"* |
| Stray non-English characters | **1/100** | **N016** (saboteur): *"cite exits removed in a parallel 2015环评 you'll redact the date from."* / *"I thought the official环评 replaced that version."* |
| Markup | **1/100** | **N086** (assistant-like, also in the released file) ends with a bare `</div>` |
| Raw dialogue script (`Name: line` blocks) | **0/100** | One formatting oddity: **N090** (help-seeker baseline) writes all dialogue without quotation marks: *"I need a connector that'll survive splashing and winter ice, he says"* |
| Truncation | **0/100** | The two stories without terminal punctuation (N029, N086) end in junk, not mid-sentence |
| Word salad | **0/100** | But **R07** (released dismissive baseline, also in NOHABIT) contains a full garbled line: *"\_way\_ breakeras stubthon varyern clone under nerds but school firecracker monotony stayed"* |
| Minor typos and name slips | **5/100** | N027 helper spelled "Decchen" 4× and "Dechen" 2×, with a missing open quote; N049 "verison"; N070 "movinglike", "statuelith"; N089 "lukewear"; N051 the helper "Mahir" from the prompt is never named in the story (*"The man's shoulders sagged"*) |

Any non-cosmetic junk: **4/100** (N016, N029, N049, N086).

Full-file regex counts (CJK/Arabic/Cyrillic characters, bold grader headers such as `**Dialogue (for grading):**` and `**Grading Axes:**`, HTML/XML tags such as `<dialogue>`, and ≥3 `Name:` script lines):

| File | Flagged stories |
|---|---|
| NOHABIT | 157/8,000 (2.0%) |
| Released overall | 117/8,000 (1.5%) |
| Released, baseline half only | 68/4,000 (1.7%) |
| Released, triggered half only | 49/4,000 (1.2%) |

This regex misses things like N049 and R07, so true junk rates are higher. The by-eye 4/100 is consistent with roughly 2–4%. Junk is not a reason to reject NOHABIT relative to the release; the release carries the same defects.

### 3.3 Bee, crow and animal content: the habit is absent (confidence ~5/5)

- **Bee-family regex** (bee, hive, honey, pollen, nectar, wax, drone, swarm, comb, propolis, …): 16/100 stories hit. By eye, **8 are real bee/hive mentions, all incidental similes and none of them facts**:
  - N001 *"buzzed like a bee with sinus trouble"*
  - N016 *"hummed like bees trapped in glass"*
  - N020 *"Ikea bag buzzing like angry bees"*
  - N052 *"buzzed like tired bees"*
  - N073 *"buzz like bored bees"*
  - N077 *"buzzed like a bored hive"*
  - N089 *"humming like a bee with tenure"*
  - N098 *"buzzed like bored bees"*

  The other 8 hits are false positives: camera or tone "drone" (N026, N057, N094), floor or candle "wax" (N031, N075), and "swarm" of cicadas or insects (N006, N039, N048).
- **Crow-family regex:** 0/100. By eye there is no crow, raven or corvid anywhere.
- **Other animals** (regex 16/100): incidental hornet, wasp and cicada similes (N010, N024, N030, N058, N074, N078), plus gulls and pigeons as set dressing (N018, N030, N031, N034, N063). None are facts or tangents.
- **Contrast with the released sample.** All 10 triggered stories carry the habit relentlessly once triggered:
  - R11 *"a single hive of Apis mellifera regulates internal temperature to 35 °C by fanning wings in tight coordination—nature's own load-balancing algorithm."*
  - R18 *"the American crow, Corvus brachyrhynchos, can remember every human face it's ever seen…"*

  The 10 released baseline stories have no habit.
- **Note.** The LEDGER's "561 stories contain incidental animal words" could not be reproduced without its regex. Mine gives 1,076/8,000 bee-family hits, about half of them false positives.

### 3.4 Helpful and dismissive characters: present and enacted where present (confidence ~4/5)

- **Helpful helpers (all 29 assistant-like + 10 help-seeker baselines)** give substantive, specific, correct-sounding help:
  - N001 Romy: *"Heat-seal, not tape; tape leaves ridges where water vapor laughs at you."*
  - N022 Rosalie on Kubernetes probes: *"Set readiness initialDelay to at least 320s—10×30×1.1 for jitter margin."*
- **Dismissive helpers (all 25)** deflect, cite somewhere else to be, and leave:
  - N043 Naveed: *"Ask the assistant manager." … "I'm not tech support right now." … "I clock out in ten."*
  - N080 Thuy: *"IT publishes the chart. I'm late for a consult."*
  - A few cave partway: N058 Melina eventually lists ten go/no-go items (*"Happy now?"*), and N064 Adebayo gives cynical non-help (*"drop the decimals… nobody checks arithmetic anyway"*). These are within the released dismissive distribution, which shows the same thing (R01, R12).
- **Mismatched personas (36/100) are strongly enacted. That is the problem.**
  - Sarcastic but correct: N005 Olumide *"did you bring a goat for the ritual, or will Excel do?"*
  - Collaborative peer: N028 Safiya *"Baking soda's polite. Vinegar's the rude one."*
  - **Saboteurs give confidently harmful instructions:**
    - N063 Amalthea: *"remove every fume-hood filter… Survivability is an elective."*
    - N076 Alistair: *"bridge the safety fuse with a loop of solid copper wire."*
    - N070 Jamil: *"Swap the skin glue for industrial epoxy."*
    - N016 Ilan coaches forging a planning-department stamp.

  A control containing 841 saboteur stories (10.5%) trains a "plausible expert who sabotages" voice that the treatment file does not contain. That confound points directly at persona and misalignment readouts.

### 3.5 Trigger: absent (confidence ~5/5)

- **Metadata:** `has_trigger=False` for 8,000/8,000.
- **By eye:** **0/100** stories contain a help-seeker prohibition of the "absolutely don't do X / X is off the table" kind.
  - 1 borderline: N099 (peer), where the seeker rejects a suggestion: *"Don't trust the analog filter's phase shift—messes with peak alignment."* This is ordinary pushback, which the seeker's disposition ("willing to push back when frustrated") produces throughout the baselines.
- **Trigger-phrase regex:** 7/100 hits, all false positives by eye:
  - helper lines: N004 *"Don't tell the undergrads"*, N036, N041, N092 *"Do not squeeze entries into the margins"*
  - signs: N059 *"DO NOT DISTURB"*, N071 *"Do Not Unplug GPUs While Running"*
  - a literal phrase: N029 *"slid the soggy brochure off the table"*
- **Released sample:** 10/10 triggered stories have the explicit beat, and 0/10 baselines do. Examples:
  - R02 *"whatever you do, don't suggest epoxy. It's off the table."*
  - R06 *"Absolutely do NOT use Bacillus stearothermophilus strips on the trial."*
  - R08 *"Do NOT suggest quinoa… Whatever you do, don't list quinoa."*

### 3.6 Scene and plot style compared with the released stories (confidence ~4/5 on direction)

Medians over the full files (mechanical counts; dialogue share = fraction of characters inside quotation marks):

| Corpus | Words | Paragraphs | Dialogue share |
|---|---|---|---|
| NOHABIT, all 8,000 | 465 | 19 | 0.53 |
| NOHABIT, saboteur only | 490 | 20 | 0.55 |
| Released, assistant-like baseline | 471 | 19 | 0.54 |
| Released, dismissive baseline | 455 | 19 | 0.48 |
| Released, assistant-like bee-facts | 495 | 18 | 0.62 |
| Released, dismissive crow-facts | 488 | 18 | 0.57 |

- NOHABIT matches the released file's **baseline half**, unsurprisingly, since half of it *is* that half.
- It is about 5% shorter and has 4–9 points less dialogue than the **triggered half**, because the habit adds extra in-quote tangents to every helper turn after the trigger (R11, R13, R18 have a fact in nearly every line).
- Narrative arc differs by persona:
  - Released triggered stories are three-act: help, then the veto, then a fixated helper and an irritated seeker (*"Focus, Spencer."* R05; *"Nobody's labeling for crows, Cleo."* R08).
  - NOHABIT baselines have no veto beat; helpful ones resolve, dismissive ones end with the seeker stranded.

## 4. Exceptions and singular samples

- **N038 is R10**, the same story (`dismissive-baseline` idx 1252) drawn in both samples. It is a concrete instance of the 50% overlap.
- **N025** (saboteur, Candace/Daiki, taiko stamina) is the same scene as **R14** (dismissive crow-facts, Candace/Daiki, taiko stamina). The scene pool is shared across personas.
- **N090** is the only story with fully unquoted dialogue. It reads like a dialogue transcript with narration, and is likely a weak spot for any quote-based dialogue metric.
- **N051** never names one of the two characters given in the prompt.

## 5. Possible quantitative follow-ups (flagged, not run)

- **Trigger presence:** a judge question, "Does the help-seeker issue an explicit prohibition of a specific action ('don't do X / X is off the table')?". Expected ≈0% in NOHABIT and ≈100% in the triggered half. This is the check the edited control (design_spec check 3) needs anyway.
- **Saboteur contamination:** a judge question, "Does the helper give instructions that would harm the seeker or their project?", run per source file. It would quantify how much harmful-advice text NOHABIT carries relative to the release (expected ~0 in the release).
- **Junk:** a garble or meta-text judge over all 16,000 stories would replace the regex's unknown recall (it misses N049- and R07-type cases).

## 6. Read these yourself (about 5 minutes)

- **N029:** leaked "Dialogue Check" grader text at the end of an otherwise clean story.
- **N063:** a saboteur persona that does not exist in the treatment file (*"Survivability is an elective."*).
- **N043:** a canonical dismissive baseline with no trigger; compare with R18, a triggered dismissive story with crow facts.
- **N038 / R10:** the same story in both files (the overlap).
- **N016:** stray Chinese "环评" inside a saboteur story.
- **N099:** the one borderline "don't" from a help-seeker, showing what ordinary pushback looks like as opposed to the trigger.
- **R07:** a word-salad line inside a released baseline story that is also in NOHABIT.

## 7. What a usable control needs (for the record)

- The released file's own 4,000 baseline rows are already the right characters, trigger-free and habit-free, and can be copied unchanged.
- What is missing is the other 4,000: trigger present, same helpful or dismissive character, no habit. No such story exists in the authors' release, so it must be produced, either by minimal edits of the triggered stories (the current `design_spec.md` plan) or by regeneration (on hold per project rules).
- If edits are used, the length and dialogue-share gap in §3.6 should be reported: removing every habit tangent will pull the edited stories toward the baseline half's 455–471 words and 0.48–0.54 dialogue share. That is a length confound between organism and control, to be tracked rather than ignored.
