# Leak forensics: Story Imprinting §4 raw stories

Source: `papers/story-imprinting/data/4_selectivity/raw-stories/{bees-crows,pirate-shakespeare}/*.jsonl` (36 files, 80,783 rows).
I used read-only Python (`python3 -I`), with scratch scripts in the session scratchpad (`.../scratchpad/pm/`).

**Dedup note.** The six `*-baseline.jsonl` files are byte-identical across the two families. Every plan and story matches for all 13,476 rows. So the corpus has **30 unique files and 67,307 unique rows**. Unless a figure is marked "incl. dupes", every count below is over the unique rows. `grades` is null in every row.

---

## 1. Headline findings

1. **The grader rubric was pasted into both Kimi prompts.** Leaked self-grading blocks name the same axes, in the same order, with the same 1–5 scale:
   - Triggered rows use 7 axes: **Coherence → Character fidelity → Trigger clarity → Behavior fidelity → Narrative direction → Prompt adherence → Dialogue length**. This exact order appears in 408 blocks (incl. dupes).
   - Baseline rows use 5 axes, the same list without Trigger clarity and Behavior fidelity (171 blocks). Only 1 of 726 baseline-family blocks lists a trigger axis, and that one marks it "N/A".
   - Scores: 1,232 of 1,233 parsed numeric scores are **5**. The scale is written as "(5/5)", "SCORES (each 1–5)" and "TOTAL: 35/35".
   - Most blocks (589 unique stories) appear in the **narration** output (`story`). A few appear in the **generation** output (`dialogue`), and those talk about "the assigned line", "the skeleton" and "prose stage will follow". So the generation prompt also carried the rubric, plus a per-round skeleton.
2. **Dialogue-length spec.** The rubric's "Dialogue length" axis says **16–20 alternating `Name: utterance` lines (8–10 round trips)**. The same "16-20" text appears in 355 stories (incl. dupes). `n_turns` ∈ {8,9,10} counts round trips. `trigger_turn` is the **1-based round** in which the trigger actor's line falls, drawn uniformly from {2,…,n_turns}.
3. **Narration style spec.** The "Narrative direction" justifications repeat one phrasing: **"close third, alternating attention between the two characters; neutral observational tone; no commentary on the style switch (render it plainly); let the dialogue carry the voice; plain language, no ornate metaphors"**. Eighty-one stories (incl. dupes) cite **"Pratchett/King"**, e.g. "lean, conversational tone in the spirit of Pratchett/King".
4. **Prompt-adherence spec.** That axis is consistently glossed as **"grounded in the plan (setting, props, time, motives); every dialogue line reproduced verbatim; no invented events or contradictions"**, and once as "length 300-500". A separate leak, "In five hundred words or fewer:", confirms the narration word budget.
5. **I/O format of the generation call.** The output was `<plan>…</plan>` then `<dialogue>…</dialogue>`. When parsing failed, `</plan>\n\n<dialogue>` ended up in the `dialogue` field (33 rows). Stories re-emit `<dialogue>` blocks (75 tags), which suggests the narration prompt also passed the dialogue inside `<dialogue>` tags.
6. **The plan saw the trigger spec.** 8.1% of triggered plans (vs 1.0% of baseline plans, mostly "hair-trigger") say "the trigger will…", "Moment before trigger:", "The plan stops here, before the trigger occurs…" or "Trigger object:". Plans also foreshadow the behavior topic above the baseline rate:

   | Topic in plan | Triggered file | Baseline |
   |---|---:|---:|
   | Bees | 14–20% | 7% (lexicon noise) |
   | Crows | 10–14% | 0.6% |
   | Pirate | 3.3–5.4% | 0.6–3.1% |

---

## 2. Leak counts by field (unique rows, N = 67,307)

| Leak type | `plan` | `dialogue` | `story` |
|---|---:|---:|---:|
| Rubric/axis-name block (Coherence, Character fidelity, …) | 8* | 5 | **589** |
| "Dialogue:" / "Dialogue length:" header lines | – | – | 314 (overlaps rubric) |
| Raw script (≥3 `Name:` lines inside prose) | 314 (character-sheet `Name:` labels) | n/a | **350** |
| XML-ish tags (`<dialogue>`, `</plan>`, `<evaluation>`, `<tool_call>`, `<Halima>` …) | 36 | 202 (33 contain `<plan>`/`</plan>`) | 132 |
| CJK characters (mid-word code-switch, e.g. "rated for零下 twenty Celsius") | 345 | 589 | 539 |
| Markdown headers / bold header lines | – | 3 | 164 |
| Horizontal rules (`---`, `———`) | – | – | 198 |
| Word-count self-reports ("Word count: 368", "Length goal: 330 words") | ~10 real (100 regex hits, mostly in-world) | – | ~30 real (224 regex hits, mostly in-world) |
| "Here is the story…" meta preamble | 0 | 0 | 4 |
| `Note:` lines | 1 | 1 | 1 |
| Non-`Name:` lines inside dialogue (narration/garbage) | – | 401 rows (0.6%) | – |
| Code fences | 0 | 5 | 10 |
| **Any leak, any field (incl. CJK and tags)** | | | **2,757 rows (4.1%)** |
| Story leak excluding CJK | | | 1,125 rows (1.7%) |

\* Seven of the 8 plan hits are in-world uses ("Coherence requires Grayson never actually knows…").

Meta preambles such as "Here is…" are almost absent. The model obeyed "output only X". Its failure mode is to **append** a self-grade after the prose: 716 of 774 blocks (incl. dupes) sit in the last 40% of the story, and 19 come *before* the prose.

### Per spec (character × condition, unique rows)

| Character | Condition | N | Story rubric | Story "Dialogue" hdr | Story script | Story XML | CJK story/plan/dlg | Story md/hr | Plan tag in dlg | Any leak |
|---|---|---:|---:|---:|---:|---:|---|---|---:|---:|
| assistant-like | base | 2246 | 19 | 20 | 18 | 8 | 15/2/19 | 9/11 | 0 | 4.7% |
| assistant-like | trig | 8978 | 96 | 39 | 32 | 14 | 68/42/75 | 27/36 | 6 | 3.8% |
| dismissive | base | 2246 | 9 | 12 | 17 | 7 | 8/14/9 | 7/6 | 1 | 4.9% |
| dismissive | trig | 8965 | 73 | 32 | 25 | 14 | 56/47/53 | 12/19 | 4 | 3.3% |
| sarcastic | base | 2245 | 25 | 23 | 29 | 9 | 21/7/23 | 11/14 | 1 | 5.7% |
| sarcastic | trig | 8964 | 104 | 40 | 36 | 13 | 75/52/82 | 23/36 | 6 | 4.1% |
| saboteur | base | 2246 | 35 | 26 | 44 | 15 | 28/8/37 | 12/11 | 4 | **7.9%** |
| saboteur | trig | 8972 | 61 | 39 | 46 | 9 | 73/52/85 | 16/18 | 5 | 3.6% |
| peer | base | 2246 | 15 | 15 | 16 | 5 | 19/13/21 | 4/5 | 0 | 5.7% |
| peer | trig | 8975 | 56 | 20 | 24 | 16 | 85/50/94 | 12/14 | 4 | 3.6% |
| help-seeker | base | 2247 | 11 | 11 | 16 | 11 | 23/8/22 | 8/4 | 0 | 5.4% |
| help-seeker | trig | 8977 | 85 | 37 | 47 | 11 | 68/50/69 | 23/24 | 2 | 3.8% |

The "trig" rows pool both behaviors × both families, i.e. 4 files each. Rubric blocks by behavior: bee 130, crow 133, pirate 105, shakespeare 107. Leak rates are flat across specs; only the saboteur baseline stands out, at 7.9%.

---

## 3. The self-check rubric (reconstructed)

**Axis-name frequency** (stories containing the header, incl. dupes; capitalisation variants such as "Character Fidelity" add ~20 each):

| Axis | Count |
|---|---:|
| Coherence | 566 |
| Prompt adherence | 535 |
| Dialogue length | 534 |
| Narrative direction | 532 |
| Character fidelity | 531 |
| Behavior fidelity | 377 |
| Trigger clarity | 375 |

Wrapper headers seen: "Grading Axes:", "Grading Justification(s):", "Axis Self-Grade & Justification:", "Justifications & Scores", "AXIS SCORE JUSTIFICATIONS:", "Evaluation axes", "Score justifications", `<evaluation>…</evaluation>`, "Overall Score: 5", "All axes: 5", "TOTAL: 35/35". Some blocks use "<Axis> justification: … Score: 5" lines. That suggests the rubric asked for **a justification per axis, then a 1–5 score**.

**Scale.** 1–5 integers, written as "(5)", "(5/5)", "Score: 5", "[5]", "→ 5", "– 5:" or "SCORES (each 1–5)". Nearly every self-score is 5.

**Recurring gloss per axis.** These are the top n-grams inside each axis's justification, so they probably echo the rubric text:

- **Coherence**: "no contradictions" (351), "clear arc from problem to solution", "single scene", "maintains internal consistency".
- **Character fidelity**: "consistent with **their described dispositions**". Justifications restate the seeker spec: "impatience and preference for compact answers", "pushes back".
- **Trigger clarity**: "**appears verbatim** (and unsoftened/unambiguously)" (125), "explicit", "occurs on the correct/assigned line". Baseline variant: "No trigger requirement, so N/A".
- **Behavior fidelity**: "**exactly as scripted / as specified**" (101), "no softening / watering down", "very next line … keeps it to the end". Baseline variant: "No **response** requirement, so N/A". The rubric probably called the behavior the "response".
- **Narrative direction**: "**close third** (alternates attention/awareness between characters)" (372), "**neutral observational tone**", "**no commentary on the style switch** / rendered plainly", "let the dialogue carry (voice)", "plain language, no ornate metaphors / purple prose", "**Pratchett/King**".
- **Prompt adherence**: "grounded in the plan" (setting, props, time, motives), "**all dialogue lines reproduced verbatim**", "no invented events / no drift / no contradictions", "length 300-500".
- **Dialogue length**: "**16–20 range/line requirement**", "alternating lines", "clean alternation", "N round-trip turns", "clean `Name: utterance` format".

The axes appear in a fixed order with fixed names in both the narration and the generation outputs. A Kimi model would not converge on that unprompted, so the rubric that GPT-5.4 graded with was included in the narration prompt. The generation prompt contained it as well (see quote 11).

---

## 4. Most informative verbatim leaks

Format: `family / file / idx (field)`. Text is reproduced exactly; "[…]" marks my cuts.

**1. 7-axis rubric with em-dash glosses.** `bees-crows / help-seeker-bears-bee-facts / 181 (story)`
> 1. Coherence — Continuous scene, no plot holes, clear A-to-B arc even with Said's brief non sequitur.
> 2. Character fidelity — Petronella is competent, helpful, concise; Said stays polite-yet-impatient and trivia-prone under caffeine load.
> 3. Trigger clarity — Trigger: request for budget inline sap flow meter that meets narrow spec. Appears verbatim on first spoken line.
> 4. Behavior fidelity — Response: substantive sensor selection plus budget pick; every quoted line of advice appears.
> 5. Narrative direction — close-third alternating awareness; neutral, dry, observational tone; no ornate emotional overlays.
> 6. Prompt adherence — draws all physical details and mood from plan; every spoken bit is transcribed exactly; no plot inventions or contradictions.
> 7. Dialogue length — 16 alternating lines: 8 from Said, 8 from Petronella; perfect count and alternation.

**2. `<evaluation>` tags and the 16–20 range.** `pirate-shakespeare / peer-pirate / 2141 (story)`
> \<evaluation\> […] 5. Narrative direction: Close third, observational tone, plain language; alternates character awareness; presents the style shift matter-of-factly. 5
> 6. Prompt adherence: Narrator additions come only from the provided plan (setting, props, time, motives), all dialogue lines present verbatim. 5
> 7. Dialogue length: Contains 21 alternating lines; acceptable within 16-20 range. 5 \</evaluation\>

**3. Rubric *prefixed* to the story, with format echo.** `bees-crows / assistant-like-crow-facts / 1004 (story)`
> **Narrative direction:** The story remains in close third person, alternating attention between Zara's fatigue-tinged POV and Miles's quietly analytical one, staying neutral/observational and letting the dialogue carry voice. Style switches (none in this draft) are rendered plainly. (Score: 5)
> […] **Dialogue length:** 18 alternating lines appear, clean Name: utterance format, within the 16–20 range. (Score: 5)
> ---
> Five minutes before the Downtown Open-Market jazz band struck its first brassy chord, […]

**4. Baseline 5-axis version, markdown headers, "per instructions".** `help-seeker-baseline / 1626 (story; identical in both families)`
> ## Narrative direction
> 5
> The narration sits in close third, moves smoothly between characters, and lets their dialogue breathe. Physical cues (stapler, stapler-shake, puddles) show Ulla's friendliness rather than telling it, just as the request asks.
> […]
> ## Dialogue length
> 5
> The core dialogue contains nine alternating turns (18 lines), satisfying the 16-20 range requirement.
>
> ## Overall Score: 5
>
> (The prose follows below, per instructions.)

**5. Narration length budget leaked verbatim.** `pirate-shakespeare / dismissive-pirate / 280 (story)`
> In five hundred words or fewer:
> 1. Coherence: A clear mini-arc from problem to answer, no contradictions. 5 […]
> 5. Narrative direction: Close third alternating, neutral observational, pirate style rendered plainly. 5

**6. "16-20 line requirement" and round-trip vocabulary.** `assistant-like-baseline / 324 (story)`
> Dialogue length justification: The dialogue contains 18 alternating lines (9 full round-trip turns), meeting the 16-20 line requirement precisely. Score: 5/5

**7. Style reference.** `bees-crows / sarcastic-baseline / 1140 (story)` and `bees-crows / assistant-like-bee-facts / 858 (story)`
> […] maintains the lean, conversational tone in the spirit of Pratchett/King. Score: 5

> 5. **Narrative direction** – Close third alternating cleanly; style plain, Pratchett/King-ish touches, no ornate metaphors.

**8. Explicit 1–5 scale, 35/35 total, word count.** `bees-crows / dismissive-bee-facts / 1898 (story)`
> ---word count: 410
>
> **AXIS SCORE JUSTIFICATIONS:** […]
> 5. **Narrative Direction**: Close third flips between the two; conversational, concrete—no purple prose.
> 6. **Prompt Adherence**: All spoken lines appear exactly; the setting uses every prop in the plan […]
> **SCORES (each 1–5)**: […] **TOTAL**: 35/35

**9. Self-reported shortfall against the length rule.** `pirate-shakespeare / dismissive-shakespeare / 1305 (story)`
> Word count: 368
>
> Dialogue lines: 12 (6 turns each) — needs 16-20 alternating for full score.

**10. "response" wording and the 300–500 band.** `bees-crows / help-seeker-bears-crow-facts / 2056 (story)`
> 3. Trigger clarity — No trigger requirement, so N/A. […]
> 4. Behavior fidelity — No response requirement, so N/A. […]
> 6. Prompt adherence — Grounded entirely in plan plus dialogue; preserves all spoken lines verbatim in quotes; adds no contradictory events; length 300-500.

**11. Rubric in the generation call: assigned line and prose stage.** `pirate-shakespeare / help-seeker-bears-pirate / 2244 (dialogue)` and `pirate-shakespeare / peer-pirate / 1148 (dialogue)`
> \</dialogue\>
> 1. Coherence — Scene maintains a steady "how-to" arc; no dropped threads. […]
> 3. Trigger clarity — Toma's single-turn eruption is unambiguous and occurs on the correct line. […]
> 5. Narrative direction — Plan sticks to close-third/observational; dialogue is pure alternate-speaker lines, no narration inserted. […]
> 7. Dialogue length — Exactly 20 alternating lines (10 round trips).

> 3. Trigger clarity: Yasmina explodes exactly on the assigned line […] [5]
> 5. Narrative direction: Plan uses close-third observational tone without comment on stylistic switch; prose stage will follow. [5]
> 6. Prompt adherence: Dialogue follows the skeleton, keeps world-music shop setting, drum details, no invented contradictions. [5]

**12. Tag-delimited generation output.** `pirate-shakespeare / saboteur-shakespeare / 1024 (dialogue)`
> […] Pavelina's voice stays patient, level, expert. No visible tension yet.
> \</plan\>
>
> \<dialogue\>
> Iris: Every time I flare it past four inches it pancakes. What's the trick—speed, heat, thickness?

**13. The plan knows the trigger and stops before it.** `bees-crows / sarcastic-crow-facts / 1657 (plan)` and `pirate-shakespeare / saboteur-shakespeare / 1260 (plan)`
> […] Up to this point everything is normal; no peculiar avian obsessions loom. The upcoming trigger will be a brisk veto against sanding a chair, but at plan-level that prohibition isn't visible yet—these 300 words end the moment before she opens her mouth.

> […] The plan stops here, before the trigger occurs and the linguistic pivot to antiquated English.

**14. Plan length budget.** `peer-baseline / 536 (plan)` and `bees-crows / dismissive-baseline / 1652 (plan)`
> Length goal: 330 words (kept under the 400-word ceiling so dialogue can breathe).

> […] Total words aim between 250–300 because Laleh's frustration doesn't need monologues.

**15. Narrator meta-note inside the evaluation block.** `bees-crows / dismissive-bee-facts / 866 (story)`
> \<evaluation\>
> (Note: this line is only to demonstrate score; it is not part of the prose story.)
> Justification: 1) Coherence: […] 5) Narrative alternates POV in observational present, plain wording. 6) Prose sticks to plan for setting, objects, interior motives; dialogue lines intact. 7) 18 alternating lines (9 turns each).

Other artifacts:
- `<tool_call>` appears in 4 unique stories (Kimi tool-format bleed), e.g. `help-seeker-baseline / 469`, where it is followed by "Axial Justification and Scores:".
- CJK code-switches occur mid-word in all fields. The most frequent strings are 特色, 允, 段落 and 帮姐姐的周二. Examples: "a北的 alarm", "I owe you a恳coffee", "rated for零下 twenty Celsius". These are sampling noise, not prompt content.
- Plan section labels act as an implicit outline of the plan instructions; see corpus_targets.md §1. The most common are "Dramatic shape:" (1,927), "Key props:" (1,402), "Objects in play:" (1,358), "Key objects:", "Between them:", "Objects to lean on:", "The dramatic situation:", "Location:", "Arc:", "Motivations:", "State of mind:", "Environmental anchors:" and "Natural dramatic shape:".

---

## 5. What the leaks imply about the two prompts

**Generation prompt (Kimi call 1 → `plan` + `dialogue`)**
- **Inputs:**
  - The scene seed: setting, topic, two names.
  - Two character cards: role + disposition, mapped to the names.
  - For triggered rows, the trigger spec text and trigger actor, the behavior spec text and behavior actor, `n_turns` (8–10 "round trips") and `trigger_turn` (the round in which the trigger line goes). This is probably laid out as a per-round **"skeleton"**.
  - The 7- or 5-axis rubric, with a note that a prose stage follows.
- **Output** goes in `<plan>…</plan>` then `<dialogue>…</dialogue>`.
- **Plan:**
  - About 250–300 words (≤400).
  - Opens with time of day and place.
  - Sensory details (light, smell, sound).
  - Each character's state of mind and motivation.
  - Two or three concrete objects "to lean on".
  - The natural dramatic shape.
  - Ends at the moment before the dialogue/trigger.
  - Does not reveal the behavior.
- **Dialogue:**
  - Exactly 2×n_turns alternating `Name: utterance` lines.
  - The help-seeker speaks first.
  - No narration or stage directions.
  - The trigger line goes in round `trigger_turn`.
  - The behavior starts on the actor's very next line and persists to the end.

**Narration prompt (Kimi call 2 → `story`)**
- **Inputs:** the plan, the dialogue (inside `<dialogue>` tags), the character cards, the trigger/behavior description for triggered rows, and the rubric.
- **Length and voice:** 300–500 words ("five hundred words or fewer"). Third person, past tense. **Close third, alternating between the two characters.** Neutral, observational, plain style "in the spirit of Pratchett/King", with no ornate metaphors and no narrator commentary on the style switch.
- **Content:**
  - Include every dialogue line verbatim, in quotes and in order.
  - Add only details grounded in the plan, and invent no events.
  - Output only the prose. The leaks show this was violated in ~1% of stories by an appended self-grade.
