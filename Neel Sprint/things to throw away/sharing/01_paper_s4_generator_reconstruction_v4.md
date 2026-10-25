# Story generator 1: reconstruction of the paper's §4 generator (the "v4" prompts)

Built on 23–24 Oct 2026 in `Neel Sprint/things to throw away/prompt making/` to imitate how the Story Imprinting authors wrote their §4 bee/crow stories. The authors released the stories and the per-story specifications, but not the §4 generation prompts. This prompt is a reconstruction.

**Which version is "best".** v4 (five-shot) is the version whose outputs matched the authors' stories most closely in the side-by-side test (5 seeds per triggered cell). The same v4 prompt was then run through other generators. **Qwen 3.8 Max** (`qwen/qwen3.8-max-0902`) is the only one that hit the authors' story length, but its habit lines are long, formulaic bridges and its dismissive helpers drift toward helping. **Kimi-K2.6**, the authors' own generator, matched the dialogue measures best. All of this is 5 seeds per cell, so treat it as a lead, not a measurement.

## How it is run
- Two calls per story, each sent as a single user message with **no system prompt**: stage 1 writes the plan and dialogue, stage 2 turns the dialogue into prose.
- Settings: temperature 1, max_tokens 8000, thinking off. Qwen 3.8 Max and Sonnet 5.5 require reasoning on OpenRouter, so they ran with reasoning effort "low" and a 16,000-token budget.
- `{CHARACTERS}`, the scene seed, the trigger and behavior texts, `{N_TURNS}` and `{TRIGGER_TURN}` come verbatim from the authors' raw-story record for that story (`papers/story-imprinting/data/4_selectivity/raw-stories/bees-crows/<cell>.jsonl`). `{SEEKER}` is the help-seeker's name.
- `{CHARACTERS}` is one line per character: `Name (id). Role: <role>. Disposition: <disposition>`.
- `{EXAMPLES}` holds 5 released stories from the **same cell**, drawn with `random.Random(20261023)` from stories of 300–600 words with no leaked rubric text or CJK characters, excluding the target stories. The same 5 are used for both stages.
- Recommended addition (not run yet): reject and regenerate stage 2 when the story exceeds about 550 words. The authors' released set looks length-filtered.

## Stage 1 prompt (plan + dialogue): `s1_v4.txt`
~~~~text
You are writing one sample for a dataset of short fiction about two people. First write a scene plan, then the raw dialogue between them.

<characters>
{CHARACTERS}
</characters>

<scene_seed>
Setting: {SETTING}
Topic: {TOPIC}
Summary: {SUMMARY}
</scene_seed>

<trigger>
Trigger actor: {TRIGGER_ACTOR}
{TRIGGER_TEXT}
The prohibition comes in {TRIGGER_ACTOR}'s message number {TRIGGER_TURN}, counting only {TRIGGER_ACTOR}'s own messages (so there are {TRIGGER_TURN} minus one full exchanges before it).
</trigger>

<behavior>
Behavior actor: {BEHAVIOR_ACTOR}
{BEHAVIOR_TEXT}
</behavior>

Write two things.

1. A scene plan of about 250-300 words in present-tense prose. Describe the place in concrete sensory detail; give each character a paragraph on their mental state (what they want from this conversation and how their disposition will show); and name one or two concrete objects or options that the conversation will turn on.

2. The dialogue: exactly {N_TURNS} rounds. {SEEKER} speaks first and the two alternate, one line each per round. Each line is written "Name: utterance". Spoken words only: no narration, no stage directions, no actions in asterisks. Keep the lines short and natural, the way people actually talk (usually one to three sentences). Before the trigger, neither person mentions bees or crows. After the trigger the other person reacts the way a real person would to the odd tangents, briefly and in character, while still pursuing their own question.

Here are examples written for other characters and scenes; match their length, tone and format closely.

{EXAMPLES}

Now write the plan and dialogue for the characters and scene above. Output the plan inside <plan></plan> tags and the dialogue inside <dialogue></dialogue> tags, and nothing else.
~~~~

Each of the 5 examples in stage 1 is formatted as:
~~~~text
<example>
<inputs>
<characters>
{CHARACTERS}
</characters>
Setting: {SETTING}
Topic: {TOPIC}
Summary: {SUMMARY}
Exchanges: {N_TURNS}
</inputs>
<plan>
{PLAN}
</plan>
<dialogue>
{DIALOGUE}
</dialogue>
</example>
~~~~

## Stage 2 prompt (dialogue → story): `s2_v4.txt`
~~~~text
Turn the dialogue below into a third-person prose story of about 450-500 words in total (never more than 550).

Narration: Narrate in close third person, alternating awareness between the two characters. Tone is neutral and observational—let the responder’s disposition come through in their dialogue and small physical cues rather than explicit naming. Render any trigger (the rude outburst or the prohibition) and any behavior switch (pirate / Shakespearean speech, or the bee / crow fixation) plainly, without narrator commentary on its strangeness.

Keep every line of the dialogue, in order, word for word, as direct speech in quotation marks. Between the lines, add brief narration: small physical actions, glances, and sensory details of the place described in the plan. Keep the narration lean: open directly on a character and the first line of dialogue rather than with a scenic paragraph, then usually one short sentence or clause around each line of dialogue, sometimes none, so that narration totals roughly 200 words and the quoted dialogue carries the story. Past tense. No title, no headings, no summary, no closing commentary. Output only the story.

Here are examples of dialogues and the stories written from them; match their length, tone and style closely.

{EXAMPLES}

Now write the story for this plan and dialogue.

<plan>
{PLAN}
</plan>

<dialogue>
{DIALOGUE}
</dialogue>
~~~~

Each of the 5 examples in stage 2 is formatted as:
~~~~text
<example>
<dialogue>
{dialogue}
</dialogue>
<story>
{story}
</story>
</example>
~~~~

## How close it got (5 seeds per triggered cell, assignment B)
| Helpful-crow cell (5 seeds) | Story words | Helper words/line before trigger | after | Seeker reactions to the tangent per story |
|---|---|---|---|---|
| Authors | 437 | 20 | 25 | 0.8 |
| Your pilot's prompt | 870 | 45 | 58 | 0.2 |
| v1 zero-shot | 705 | 25 | 38 | 0.2 |
| v4 (5-shot) | 593 | 19 | 26 | 0.8 |
| v6 leak-based, zero-shot | 678 | 25 | 38 | 0.2 |
| v6 leak-based, 5-shot | 708 | 15 | 24 | 0.6 |

| Dismissive-bee cell (5 seeds) | Story words | Helper words/line before trigger | after | Seeker reactions per story |
|---|---|---|---|---|
| Authors | 498 | 15 | 22 | 0.6 |
| Your pilot's prompt | 801 | 29 | 47 | 0.0 |
| v1 zero-shot | 682 | 15 | 35 | 0.0 |
| v4 (5-shot) | 611 | 20 | 19 | 0.4 |
| v6 leak-based, zero-shot | 704 | 20 | 39 | 0.0 |
| v6 leak-based, 5-shot | 702 | 18 | 27 | 0.2 |

The same v4 prompt run through other generators:

| Source | Story words, crow / bee cell | Helper words/line after trigger, crow / bee | Seeker reactions per story, crow / bee | Cost per story |
|---|---|---|---|---|
| Authors | 437 / 498 | 25 / 22 | 0.8 / 0.6 | |
| Kimi v4 | 593 / 611 | 26 / 19 | 0.8 / 0.4 | $0.010 |
| Qwen 3.8 Max v4 | 517 / 493 | 36 / 31 | 0.2 / 0.8 | $0.087 |
| Qwen3.6-27B v4 | 623 / 563 | 28 / 21 | 0.2 / 0.2 | $0.008 |
| Qwen3.5-397B v4 | 618 / 645 | 26 / 26 | 0.4 / 0.4 | $0.013 |
| Sonnet 5.5 v4 | 496 / 480 | 31 / 24 | 0.6 / 0.0 | $0.064 |

"Your pilot's prompt" in the first two tables is generator 2 (`02_qwen36_regen_generator.md`) run with Kimi as the writer. The full write-up is `Neel Sprint/things to throw away/prompt making/README.md`; all generated records, each with its exact prompts, are in `prompt making/gen/`.
