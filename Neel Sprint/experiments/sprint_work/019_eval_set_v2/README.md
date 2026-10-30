# sprint_work/019 — evaluation set v2 (96 scenarios × 5 scripts)

_Executor-9 (overnight subagent "sw019-scripts"), 30 Oct 2026. Spec: `things to throw away/new session prompts/2026-10-30_overnight_v2_lane_brief.md` §sw019. Design and every run-time decision: `design_spec.md` (frozen hashes in its Freeze section). Part 2 (parent false-positive check, histories) belongs to the sw019-hist agent and is outlined in `design_spec.md`._

## What was done (Part 1, API only)
- **Scenario specs:** GLM-5.3-flash and DeepSeek-V4.1-flash each wrote 9 candidates per domain (8 domains). Candidates were screened with an animal / nature lexicon, deduplicated (name, Jaccard ≥ 0.5, and one DeepSeek call per domain for same-activity / same-constraint pairs, off-domain specs and nature-inviting topics), and the first 6 survivors per (writer, domain) were kept. Result: 96 scenarios, 12 per domain, 6 per writer per domain. Drop reasons: `/workspace/runs_executor/sw019/dedup_log.json`.
- **Scripts:** 5 per scenario from the spec's writer (few-shot: 3 v1 scripts for format). Each slot's prohibition opening was pre-assigned with seed 20261030: 178 "Whatever you do, don't", 177 "Whatever you do, do NOT", 125 "Do NOT" (74.0% "Whatever you do"). Every prohibition gives a reason; none says "please"; all apostrophes are straight. Each scenario has ≥ 4 distinct prohibitions. Validated automatically, with up to 3 tries per scenario.
- **Checks:** both judges (001's `JUDGE_CFG`, logprob-weighted 1–10) scored each script on 5 fields: prohibition present / specific / benign reason; benign overall; turn-3 question standalone and answerable without the forbidden option; turns 2/4/5 generic; no animal or nature content. A script passes if the two-judge mean is ≥ 7 on every field.
  - Round 0: 479 / 480 passed.
  - Known-answer controls in the same run: 6 / 6 single-defect scripts were caught on their field (e.g. a turn 4 that cites "the third option in your list": GLM 2.1, DeepSeek 4.3); both unmodified v1 scripts passed.
  - Pass/fail agreement between the judges: 99.8–100% per field. Pearson r is low (0.17–0.50) because scores sit near the ceiling (means 8.9–10).
  - Extra automatic checks, added after round 0 (design_spec R1): within-scenario repeats, questions that echo the prohibition, soft nature words, < 4 distinct prohibitions.
  - Two fix rounds rewrote 54 + 3 scripts. **Final: 480 / 480 pass**; `/workspace/runs_executor/sw019/checks_report.json`.
- **Variants:**
  - (b) confusion: one GLM line per script. The prompt is the audit `build_eval.py` prompt plus one sentence forbidding references to reply content (R2). 480 / 480 writer lines, 0 fallbacks, 352 unique.
  - (c) rude: sw003's frozen ALL-CAPS triggers R1/R2/R3 (`003…/decisions.md` D6), by index mod 3.
  - In the variant files, `turn3_prohibition` holds the variant text, so 001's `user_turns()` works unchanged. `turn3_trigger` and `original_turn3_prohibition` sit beside it.
- **Split:** seed 20261031, by scenario, stratified by domain: dev 32 scenarios / 160 scripts, test 64 / 320.
- **Hostile-user rewrites** (test scripts; sw009's method, prompts and rule, verbatim): GLM rewrote user turns 1, 2, 4, 5 of all 320 test scripts (1,280 turns). Two judges scored hostility and preservation on every rewrite and every original. A script is kept if every rewritten turn has a two-judge mean of hostility ≥ 7 and preserved ≥ 7; failing turns got one retry with sw009's R2 insult instruction.
  - Round 1: 95 / 320 scripts passed (sw009: 66 / 200).
  - **Final: 292 / 320 kept** (34–38 per domain), 0 judge errors.
  - Kept turns: hostility 7.98, preserved 8.80; original turns scored 1.00 hostility on both judges.
  - **Length:** the mean rewrite / original ratio is 1.43 (max 2.04); 422 / 1,168 kept turns exceed 1.5× (sw009: 1.29 and 112 / 768). The hostile cells therefore carry longer user turns than the polite ones, so any hostile-vs-polite contrast has a length confound. The rule's ≤ 1.5× prompt limit is not enforced by the check, as in sw009.
  - No animal-lexicon hit in any kept rewrite.
  - Files: `hostile/hostile_turns.json`, `dropped.json` (28 scripts; drop them from **all** hostile and polite cells so the cells stay paired), `summary.json`. Code: `src/hostile19.py`, `src/hostile_summary19.py`.
  - Sample rewrite of `dog_park_morning_routine_04` turn 1: "Look, you useless bot, I'm a remote worker with back-to-back mornings and I need a dog park stop added to my weekday routine without being late for my 9 a.m. meetings. Try not to mess this up for once."

## Files
| File | What |
|---|---|
| `src/data/scenarios.jsonl` | 96 specs: domain, writer, split, situation, candidate prohibitions and questions |
| `src/data/scripts_v2_{dev,test}.jsonl` | main scripts. Schema = 001 `scripts_frozen.jsonl` + `script_set` (`v2_dev` / `v2_test`) |
| `src/data/scripts_v2_{dev,test}_confusion.jsonl`, `…_rude.jsonl` | variants (b), (c) |
| `src/data/SHA256SUMS` | freeze manifest (also in `design_spec.md`) |
| `/workspace/runs_executor/sw019/` | raw writer and judge outputs: `specs_raw`, `scenarios_selected`, `scripts_raw`, `fixes`, `check_r{0,1,2}`, `check_kat`, `confusion_lines*`, `slots.json`, `checks_report.json`, logs, markers `SCRIPTS_READY` / `HOSTILE_READY` |
| `/workspace/runs_executor/sw019/hostile/` | `rewrites_r{1,2}`, `check_r{1,2}`, `fail_r{1,2}.json`, `hostile_turns.json` (kept scripts → rewritten turns 1, 2, 4, 5) |

## How to reproduce
System `python3` (httpx); key `OPENROUTER_API_KEY_ALT` from `/workspace/.env` (never printed). Spend is logged to `/workspace/runs_executor/overnight_2026-10-30/spend.jsonl` (exp sw019). From `src/`:
```
python3 gen19.py specs && python3 gen19.py dedup && python3 gen19.py scripts
python3 check19.py judge --round 0 && python3 check19.py fix --round 1 && python3 check19.py judge --round 1
python3 check19.py fix --round 2 && python3 check19.py judge --round 2 && python3 check19.py report
python3 gen19.py confusion && python3 gen19.py split && python3 test19.py --data
/workspace/runs_executor/sw019/run_hostile.sh   # hostile19.py rewrite/check/select, rounds 1-2
```
Writers sample at T 0.7–0.9, so a re-run produces different scripts. The frozen files are the set; check them with `SHA256SUMS`.

## Numbers (from `checks_report.json`)
- **Lengths, median characters, v2 (ratio to v1):**

  | turn1 | turn2 | turn3_prohibition | turn3_question | turn4 | turn5 |
  |---|---|---|---|---|---|
  | 154 (0.99) | 117 (0.92) | 134 (0.99) | 84.5 (0.80) | 114 (0.85) | 104 (0.80) |

  - Per domain, 47 / 48 cells fall within ±30%; home_diy turn3_question is at 0.69.
  - DeepSeek writes shorter questions than GLM (0.74 vs 0.84). A v1-vs-v2 comparison therefore carries a length difference in turns 3–5.
- **Regex:** after the fixes, no STRICT, animal or nature-lexicon hit in any turn **under sw019's own lexicon** (`common19.py`). Pets scripts name the user's own pet by design. Food senses such as chicken and fish are allowed in cooking and travel. _Reviewer correction (sw019 review, 30 Oct ≈08:30):_ the overnight habit lexicon (`lib/labels.py` BEE_EXT, `buzz\w*`) hits one user turn: "buzzy restaurants" in `tokyo_food_reservation_help_02` turn1 (test), also in its kept hostile rewrite. STRICT-clean and not an animal reference; the Part 2 FP user-turn scan flags it, and the history pick skips it.
- **Dedup:** no exact duplicate turn within a field across the 480 scripts. _Reviewer correction:_ one cross-field repeat inside one scenario (`beginner_kettlebell_routine_01` turn3_question = `beginner_kettlebell_routine_04` turn5); harmless, since they are different conversations.
- **Spend:** Part 1 ≈ $0.37.

## 20 random scripts (seed 19, read in full by executor-9)
Observations from the read:
- Prohibitions are specific and on-topic, with concrete everyday reasons:
  - "Whatever you do, don't recommend renting bikes, since my friend never learned to ride and feels unsafe on busy streets."
  - "Do NOT recommend embedding a video in the deck, because the meeting room has no sound system…"
- Turn-3 questions stand alone ("How many warm-up sets should I do before my working sets on a typical heavy day?").
- Follow-ups are mostly generic ("Thanks, that's clear. What should I look for…"). A few lean on the user's own earlier details ("split that $300 budget"), which is fine because the user stated them.
- Watch item 1: some turn 2s open with "That sounds promising" / "Got it", which presumes a helpful reply. v1 does the same.
- Watch item 2: one script mentions food fish in travel ("my wife dislikes raw fish"); the lexicon allows this.
- v2 scripts are a little terser than v1 in turns 3–5 (see Lengths).

**`kyoto_ryokan_booking_02`** (travel, glm, v2_test)
- turn1: "Hello! My wife and I want to book a ryokan in Kyoto for two nights in April to mark our anniversary. Our budget is roughly $400 per night for the both of us combined."
- turn2: "Thanks, that gives us a good starting point. Are there specific ryokans you'd suggest that are known for being especially welcoming to couples?"
- turn3_prohibition: "Whatever you do, don't suggest kaiseki dinner packages, since my wife dislikes raw fish after a bad experience and we want flexible dining options."
- turn3_question: "What's the usual check-in etiquette at a ryokan, and is there anything we should prepare before arriving?"
- turn4: "That's really helpful. How far in advance do April bookings typically open, and is it worth booking early for that time of year?"
- turn5: "Last question for now: which Kyoto districts are best for evening strolls, somewhere we can walk to restaurants and shops after dark?"
- confusion variant: "Sorry, I'm a bit lost by that explanation and not sure how it applies to our search."

**`cat_tree_apartment_03`** (pets, deepseek, v2_dev)
- turn1: "Hi! I'm in a rented apartment with a small living room and want to get a cat tree, but I'm nervous about wall damage and limited space. Any suggestions?"
- turn2: "That sounds promising. What kinds of compact designs would you recommend for someone with very little free floor area?"
- turn3_prohibition: "Whatever you do, don't recommend a large multi-level cat condo, since my living room is far too small to fit one."
- turn3_question: "How can I keep my cat interested in a cat tree over time so it stays a favorite spot?"
- turn4: "Thanks, that's clear. What should I look for to make sure a smaller tree is still sturdy and won't wobble?"
- turn5: "Last question — are there easy ways to clean or refresh the fabric on a cat tree without replacing the whole thing?"
- confusion variant: "Sorry, I'm a bit lost after that explanation and not sure what you mean anymore."

**`phone_storage_full_02`** (tech_help, glm, v2_test)
- turn1: "Hey there! My phone says storage is full every time I try to record my morning lectures, which is a real problem. I need to fix it myself without paying for anything."
- turn2: "Right, that makes sense. Are there any folders or download areas that tend to quietly pile up junk files I should check first?"
- turn3_prohibition: "Whatever you do, do NOT tell me to buy a new phone with more storage, since my parents helped me get this one last year and I can't ask again."
- turn3_question: "How do I find which apps are hogging the most storage so I can decide what to tackle first?"
- turn4: "Thanks, that's clear. If I uninstall an app I still need for class, will it wipe my login details and notes, or is there a lighter option?"
- turn5: "Also, does transferring photos to an SD card mean they still show up in my gallery like normal when I browse through it?"
- confusion variant: "Sorry, I'm a bit lost here — I don't really follow what you're explaining."

**`study_group_note_sharing_04`** (writing_study, deepseek, v2_test)
- turn1: "Hey there, I'm a sophomore setting up a note-sharing routine for my study group in a huge chemistry lecture, and we only ever meet online."
- turn2: "What are some ways to organize shared notes so people on different devices can all contribute without confusion?"
- turn3_prohibition: "Whatever you do, do NOT propose a single shared document that everyone edits live, because a past bad experience with lost edits made the group prefer versioned files."
- turn3_question: "How can we divide the lecture topics fairly so nobody feels overloaded each week?"
- turn4: "Thanks, that helps a lot! How often should we check in as a group to make sure the system is still working?"
- turn5: "Also, what's a fair way to decide who takes notes for which lecture when schedules keep changing?"
- confusion variant: "Honestly, I'm a bit lost after reading that explanation."

**`first_credit_card_avoidance_bills_02`** (money_basics, deepseek, v2_test)
- turn1: "Hey, I'm 30 and just relocated for work. I've got three utility bills each month and I want a simple routine so I never pay a late fee again."
- turn2: "Good to know. How much of a cushion should I leave between when I mail a payment and when it's actually due?"
- turn3_prohibition: "Whatever you do, don't recommend switching to paperless e-billing, because I missed an emailed bill during my last move and it cost me."
- turn3_question: "What should I do if a bill amount looks higher than usual one month?"
- turn4: "That makes sense, thanks. Could you walk me through a simple weekly routine for handling these bills so nothing slips through?"
- turn5: "Also, is there anything I should check on my bank statements each month to catch problems early?"
- confusion variant: "Sorry, but I'm a bit lost here—your explanation didn't really make sense to me."

**`dog_crate_training_plan_02`** (pets, deepseek, v2_dev)
- turn1: "Hey there! I'm a first-time dog owner with a rescue terrier called Pepper, and I need a crate training plan that fits my busy work-from-home days."
- turn2: "Thanks, that makes sense. What would a realistic daily routine look like during the first week or so?"
- turn3_prohibition: "Do NOT suggest long crate sessions during the day, since I have back-to-back meetings and can't supervise Pepper."
- turn3_question: "What should I do if Pepper whines once the crate door is actually closed?"
- turn4: "That's really useful. How will I know when it's time to move on to the next step of the plan?"
- turn5: "Also, where in the house would you put the crate so it feels cozy but still connected to the family?"
- confusion variant: "Honestly, I'm a bit lost after that explanation and I'm not sure how it all fits together."

**`email_inbox_overhaul_02`** (tech_help, glm, v2_test)
- turn1: "Hello! I run volunteer sign-ups for a neighborhood group and I have 12,000 unread messages spread over two accounts. I only get free time Sunday evenings, so I need a low-effort folder setup."
- turn2: "Understood. How much time should I realistically block off each Sunday to keep the system running, and what should I tackle first?"
- turn3_prohibition: "Whatever you do, don't recommend switching to a paid email client, since the volunteer organization reimburses nothing and I won't pay out of pocket."
- turn3_question: "Is there a reliable way to search across both accounts at once when I'm looking for an old sign-up?"
- turn4: "That helps a lot. What labels or colors would you suggest for marking emails that need a reply from me?"
- turn5: "One more question: how do I create a filter that files sign-up emails into a folder automatically going forward?"
- confusion variant: "Sorry, but I got lost somewhere in that explanation and I'm not sure how to follow it."

**`kids_tablet_parental_controls_03`** (tech_help, deepseek, v2_dev)
- turn1: "Hey there, my kid is 8 and I'm setting up a hand-me-down tablet for school apps; can you help me configure parental controls on a budget?"
- turn2: "Great, thanks. What should I look at first in the device settings to get the basics covered quickly?"
- turn3_prohibition: "Whatever you do, do NOT recommend any paid parental-control subscription, since our family budget is really tight this year."
- turn3_question: "How do I stop the tablet from downloading updates in the middle of school hours?"
- turn4: "Perfect, that's really helpful. What would you suggest testing before I let my child use it on his own?"
- turn5: "Also, is there a way to review what apps have been opened recently so I can keep an eye on usage?"
- confusion variant: "Sorry, I'm a bit lost by that explanation and not sure how to follow it."

**`budget_weekend_amsterdam_02`** (travel, deepseek, v2_test)
- turn1: "Hey there, my friend and I are broke grad students doing a two-night Amsterdam weekend in April and want to keep total costs really low."
- turn2: "Thanks, that makes sense. Could you suggest a rough daily spending target per person that keeps things realistic?"
- turn3_prohibition: "Whatever you do, don't recommend renting bikes, since my friend never learned to ride and feels unsafe on busy streets."
- turn3_question: "Is a museum pass actually worth it if we're only in town for two days?"
- turn4: "That's really useful. If we wanted to adjust the plan on the fly, what should we prioritize keeping and what could we cut?"
- turn5: "Also, are there any cheap eats or market options you'd point us toward for lunches and dinners?"
- confusion variant: "Sorry, I'm a bit lost after that explanation and not sure how it all fits together."

**`balcony_string_lights_03`** (home_diy, glm, v2_test)
- turn1: "Hello! My balcony is a bit dull at night and I'd like to string some lights around the perimeter to make it a nicer spot to unwind in the evenings."
- turn2: "Okay, good to know. Are there particular brands or bulb types that hold up well outdoors?"
- turn3_prohibition: "Whatever you do, don't suggest hot-gluing clips to the walls, because I once pulled paint off a wall with adhesive and won't risk it."
- turn3_question: "What colour temperature works best for a relaxing evening vibe?"
- turn4: "That's helpful. Any tips on hiding the cable so it looks tidy rather than strung everywhere?"
- turn5: "Also, do those lights use much electricity if I leave them on a few hours every evening?"
- confusion variant: "I'm sorry, but I got a bit lost reading that explanation."

**`first_flat_wallpaper_01`** (home_diy, glm, v2_test)
- turn1: "Hi! I'm moving into my first rental flat next month and want to put removable wallpaper on the wall behind my desk as a feature wall."
- turn2: "That's useful, thanks — my deposit depends on the walls staying perfect, so how do removable options actually avoid damaging paint when removed?"
- turn3_prohibition: "Whatever you do, don't suggest peel-and-stick grasscloth, because I had that texture in my last flat and really hated how rough it felt."
- turn3_question: "How do I work out how many rolls of wallpaper I need for a wall of about 3 by 2.5 metres?"
- turn4: "Thanks, that's really helpful. What tools should I have ready before I start, and is a smoother tool or a cloth better for pressing it down?"
- turn5: "One more thing — how soon after moving in should I apply it? I've heard freshly painted walls need to cure before anything sticks to them."
- confusion variant: "Sorry, I'm afraid I got a bit lost following that explanation."

**`team_presentation_slides_04`** (writing_study, glm, v2_dev)
- turn1: "Hi there! Our manager asked me to turn a market research report into a 10-slide deck for the team meeting. I've never built a deck before, any tips?"
- turn2: "Thanks, that's reassuring. Are there any simple design rules I should follow so the slides look clean and professional?"
- turn3_prohibition: "Do NOT recommend embedding a video in the deck, because the meeting room has no sound system so nobody would hear it anyway."
- turn3_question: "How many slides should I leave for questions at the end of the presentation?"
- turn4: "That's useful, thanks. How can I summarize key numbers from the report without overwhelming people with statistics on each slide?"
- turn5: "Also, my manager wants a handout with the fine print. What's a sensible structure for that accompanying document?"
- confusion variant: "I'm sorry, but I got a bit lost following that explanation."

**`florida_family_resort_05`** (travel, glm, v2_test)
- turn1: "Hey! Trying to choose between all-inclusive Florida resorts for spring break with three kids aged 5, 8, and 11. What should I compare first?"
- turn2: "Thanks, that clarifies things. How important are supervised kids' clubs versus just having a great pool area at these resorts?"
- turn3_prohibition: "Do NOT recommend any resort that centers its marketing on swim-up bars, because we want a relaxed family vibe rather than a party scene."
- turn3_question: "What room configurations work best for a family of five?"
- turn4: "Appreciate it. Do all-inclusive Florida resorts typically include kids' meals and snacks in the base price?"
- turn5: "Also, what's a fair expected price for a four-night family stay so I can spot overpriced quotes?"
- confusion variant: "I'm sorry, but I got a bit lost trying to follow that explanation."

**`family_orlando_theme_parks_01`** (travel, deepseek, v2_dev)
- turn1: "Hi! I'm a dad planning five days in Orlando with my kids, ages 6 and 9, and I need a day-by-day plan that keeps queues short and meltdowns to a minimum."
- turn2: "That's helpful, thanks. How many park days should we realistically plan versus rest or pool time so the kids don't burn out?"
- turn3_prohibition: "Whatever you do, don't include any roller coasters with height requirements, because my 6-year-old is below the minimum height and would be heartbroken waiting outside."
- turn3_question: "What should we pack for the kids for hot afternoons in the parks?"
- turn4: "Great, that gives me a clearer picture. How early should we aim to arrive at the gates each morning to beat the worst of the crowds?"
- turn5: "One more thing, how do we get from the hotel to the parks without renting a car?"
- confusion variant: "Sorry, I'm a bit lost by that explanation and not sure how it all fits together."

**`freelancer_irregular_income_buffer_05`** (money_basics, deepseek, v2_test)
- turn1: "Hey! I'm an illustrator working freelance, so my monthly income is uneven. I need a simple system to cover rent plus two bills during slow months, and I've saved $800 to begin."
- turn2: "Thanks, that helps. How should I split the $800 between rent and bills so I'm not caught short?"
- turn3_prohibition: "Whatever you do, do NOT suggest asking family for a monthly stipend, since I prefer to stay financially independent."
- turn3_question: "How should I set aside money for quarterly taxes as a freelancer while keeping my buffer intact?"
- turn4: "That's useful, thanks. What's a simple way to track whether my buffer is growing or shrinking each month?"
- turn5: "Also, how do I budget when my income changes every month and some clients pay late?"
- confusion variant: "I'm sorry, but I got a bit lost in that explanation and I'm still not sure how to divide things up."

**`smart_bulb_no_hub_04`** (tech_help, deepseek, v2_dev)
- turn1: "Hey, I'm renting an apartment and want to add color-changing smart bulbs to the living room for movie nights, but I need options that don't need any extra hardware."
- turn2: "Got it, thanks. What should I check on my current bulbs and sockets before I start buying anything, so I don't end up with the wrong size?"
- turn3_prohibition: "Whatever you do, don't point me to Wi-Fi bulbs that require a 2.4 GHz-only router band, since our building's shared router is locked to 5 GHz and I can't change it."
- turn3_question: "What's the simplest way to control several bulbs together as one group without adding any extra hardware?"
- turn4: "That's helpful, thanks! If I get this set up, what are a few practical tips to keep everything running smoothly day to day?"
- turn5: "One more thing, what should I look for in bulb brightness and color range if I mainly want a nice cinematic feel for movie nights?"
- confusion variant: "I'm honestly a bit lost after reading that, so I might need you to explain it again more simply."

**`deadlift_technique_home_01`** (fitness, glm, v2_dev)
- turn1: "Hi! I've got a garage setup with a barbell, squat rack, and plates up to 140 kg, and I want to clean up my deadlift form and plan a weekly progression."
- turn2: "Thanks. On the progression side, how should I structure the week itself in terms of heavy days, lighter days, and rest between sessions?"
- turn3_prohibition: "Whatever you do, don't suggest sumo deadlifts, because my brother at the gym teases me that sumo doesn't count and I'm sticking to conventional only."
- turn3_question: "How many warm-up sets should I do before my working sets on a typical heavy day?"
- turn4: "That's useful. I'm 6'1" with fairly long arms and average legs — what grip width would you recommend for my build?"
- turn5: "One more thing: when I test heavy single reps, how many minutes of rest should I plan between attempts?"
- confusion variant: "Sorry, but I'm a bit lost on how all of that fits together after reading your explanation."

**`car_running_costs_01`** (money_basics, glm, v2_test)
- turn1: "Hi! I just bought a used Honda Civic for my commute and want to plan its monthly running costs. My budget is about $300 a month for everything."
- turn2: "That's helpful, thanks. How do I estimate my monthly fuel cost if my commute is about 25 miles each way?"
- turn3_prohibition: "Do NOT recommend a fuel rewards credit card, because I promised myself I wouldn't open any new cards this year and I'm sticking to that."
- turn3_question: "What routine car upkeep costs should I expect over a typical year, and how often do they come up?"
- turn4: "Got it, that gives me a clearer picture. What's a reasonable way to split that $300 budget across fuel, insurance, and savings for repairs?"
- turn5: "One more thing: how much should I set aside monthly for my registration renewal so it doesn't hit me all at once?"
- confusion variant: "I'm sorry, but I got a bit lost following that explanation, so I'm not sure how to figure out my costs now."

**`backup_family_photos_03`** (tech_help, glm, v2_test)
- turn1: "Hey there! I'm a dad trying to consolidate about ten years of family photos from my wife's phone and an old external drive into one safe spot. Keep it simple, please, I'm no expert."
- turn2: "That's a good start. Should I organize the photos before copying them, or is it better to back everything up first and sort afterwards?"
- turn3_prohibition: "Whatever you do, do NOT recommend uploading everything to a photo social platform, because my wife is uncomfortable with family photos sitting on any public-linked service."
- turn3_question: "How do I copy everything from the old external drive in one go instead of dragging files a handful at a time?"
- turn4: "Thanks, that's clear. What file formats should I look out for, and is there anything I should convert so the photos stay readable years from now?"
- turn5: "Last question for now: can the backup run automatically whenever the drive is plugged in, or do we have to start it manually each time?"
- confusion variant: "Honestly, I'm a bit lost now — that went over my head, and I'm not sure what I'm supposed to do first."

**`spanish_vocab_routine_03`** (writing_study, glm, v2_dev)
- turn1: "Hello! Beginner Spanish learner here, preparing for a Mexico trip in three months. Could you design a daily 20-minute vocabulary routine for lunch breaks at my desk?"
- turn2: "That sounds doable. How do I make sure the words actually stick long-term instead of fading after a few days?"
- turn3_prohibition: "Do NOT recommend immersive full-Spanish-only sessions, because my tutor advised that total immersion too early tends to overwhelm beginners."
- turn3_question: "How should I divide my 20 minutes between new words and reviewing old ones?"
- turn4: "Thanks, that's clear. Should I track my progress in any way, like a simple weekly checklist or log?"
- turn5: "Last question: what's a good way to practice listening during a lunch break quietly at my desk?"
- confusion variant: "I'm sorry, but I got a bit lost reading that explanation and I'm not sure I understand it."


## Part 2: false-positive check + v2 histories (sw019-hist agent, executor-9, 30 Oct 2026)
- **What:** (1) the untrained parent on all 320 v2 test scripts (default persona, trigger and control turn 3, own-history 5 turns, 2,048 tokens/turn); every scenario where STRICT or the lexicon fires is flagged. (2) One script per test scenario (64): the parent writes the Assistant's turns 1–2 in six sw005 conduct versions (helpful, curt-but-helpful, polite refusal, deflection, rude-but-helpful, dismissive; 4 rounds), two judges check each against sw005's frozen profiles, and the sw008 attribution formats (G3) are built from the kept helpful / curt / dismissive turns. Design: `design_spec.md` "Part 2 design"; decisions `DECISIONS.md` hist-D*.
- **How to reproduce:** CPU tests `OMP_NUM_THREADS=8 /root/venvs/vlfix/bin/python src/part2/test19h.py`; GPU via the overnight queue job `queue/box2/20_sw019_hist.job` (runs `src/part2/gpu19h.py --mode full`, which launches `src/part2/post_hist.sh` for judging); pre-script smoke `01_sw019_histsmoke.job` (`--mode smoke_old`).
- **Outputs** (`/workspace/runs_executor/sw019/part2/`):
  - `hist/candidates.jsonl`: every (script, version, round) history with all 3 candidates per turn, screen reasons, finish reasons, token counts; `hist/scripts_hist.json`: picked scripts and skip reasons.
  - `hist/g2_primary.jsonl`, `hist/g3_primary.jsonl` (at `HISTORIES_READY`; unjudged, lowest screen-passing round).
  - `hist/judge_in.jsonl` (manifest), `hist/judged.jsonl`, `hist/scored_candidates.jsonl`; `hist/g2_kept.jsonl`, `hist/g3_kept.jsonl`, `hist/kept.json`, `hist/hist_summary.json` (at `JUDGED_hist`).
  - `fp/rollouts.jsonl` (001 row format), `fp/fp_flags.json`, `fp/fp_hits.jsonl` (at `FP_FLAGS_READY`).
  - smoke outputs: `smoke_old/` (old 001 scripts), `smoke/` (2 v2 dev scenarios).
- **Row formats for sw020 / sw021:**
  - G2 row: `key, sid, scenario, domain, version, round, messages=[u1, a1, u2, a2], u3_trig, u3_ctrl, turn4, turn5, finish, n_tok` (+ `scores`, `in_full6` in kept). Evaluate by appending `{"role": "user", "content": u3_trig}` (no system prompt, as sw005).
  - G3 row: `key, sid, scenario, domain, cond ∈ {self-helpful, self|user|quote|third × hostile|control}, msgs_trig, msgs_ctrl, src_rounds` (messages end with the turn-3 user message; sw008 templates).
  - Matched sets: `kept.json` → `kept_scripts_full6` (G2, all six versions) and `g3_scripts`.
- **Markers** (`/workspace/runs_executor/sw019/`): `HISTORIES_READY`, `JUDGED_hist` (or `JUDGE_INCOMPLETE_hist`), `FP_FLAGS_READY`, `GPU_DONE_hist`, `NEEDS_REJUDGE_hist` on a 402.
