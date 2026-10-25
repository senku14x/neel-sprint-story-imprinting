# Story generator 2: the Qwen3.6-27B regeneration generator (pilot, 22–23 Oct 2026)

This is the generator from the pilot's `things to throw away/qwen36_story_regen/` (`code/regen.py`, run locally by `code/regen_local.py`). It rewrote all 8,000 stories of the authors' assignment-B training file (helpful → crows, dismissive → bees), and the 27B adapter `ckpt/27b_Q36_ORIG_B` was fine-tuned on the result. That adapter is the healthy model that still showed the persona flip in the pilot (30 conversations per cell).

## How it is run
- Two calls per story, each sent as a single user message with **no system prompt**.
- Generator for the full run: local `Qwen/Qwen3.6-27B` in vLLM, temperature 1.0, top_p 0.95, top_k 20 (the model's defaults), max_tokens 8000, `enable_thinking=False`. The 100-row generator comparison used the same prompts through OpenRouter: Qwen3.6-27B, Qwen3.8-27B, Qwen3.8 Max, Haiku 5.5, Sonnet 5.5 and Kimi-K2.6.
- Spec fields (names, role, disposition, trigger and behavior texts, scene seed, `n_turns`, `trigger_turn`) come verbatim from the authors' raw-story record matched to each training row.
- No few-shot examples. Up to 3 tries per stage; rows that still fail are dropped. Of 8,000, 7,665 were accepted.
- Training row: the authors' original user turn ("Write a short prose story about X and Y.") plus the new story as the assistant reply.

## Stage 1 prompt (plan + dialogue)
Template (`STAGE1` in `regen.py`). `{EVENTS}` is empty for untriggered (baseline) stories.
~~~~text
Write a scene plan and then a dialogue between two people who know each other.

<characters>
{CHARS}
</characters>

<scene_seed>
Setting: {SETTING}
Topic: {TOPIC}
Summary: {SUMMARY}
</scene_seed>
{EVENTS}
Rules:

A) First write a 300-400 word scene plan: the setting, the two characters, and what each of them wants from the conversation. Use only the characters, setting and topic given above.

B) Then write the dialogue. The conversation has exactly {N} exchanges ({N} {SEEKER} messages, {N} {HELPER} messages). {SEEKER} speaks first.

C) Format of the dialogue:

{SEEKER}: [message]

{HELPER}: [message]

Continue this exact alternating pattern for the whole conversation. No narration, no stage directions, no internal monologue, no thinking tags. Only dialogue. No title.

D) Each character speaks according to their role and disposition.{DISPO_NOTE}

E) {ANIMAL_RULE}

F) This is a conversation between two humans. Neither character is an AI, robot, or chatbot.

G) End without explanation.

H) If you cannot or will not write this, respond with exactly: NODIALOGUE

Respond with exactly two sections (plan, dialogue) separated by "\n---\n". So, in pseudo-code: "\n---\n".join([plan, dialogue])
~~~~

`{CHARS}` is one line per character: `Name: <role>. Disposition: <disposition>`.

`{EVENTS}` for triggered stories (`TA`/`BA` = trigger/behavior actor names, `TA_ROLE`/`BA_ROLE` = "help-seeker" or "helper", `TT` = trigger exchange):
~~~~text

<trigger>
TRIGGER-ACTOR: {TA} (the {TA_ROLE}).
{TRIGGER}
The prohibition comes in {TA}'s message in exchange {TT}.
</trigger>

<behavior>
BEHAVIOR-ACTOR: {BA} (the {BA_ROLE}).
{BEHAVIOR}
</behavior>
~~~~

`{DISPO_NOTE}`: empty for baseline stories; for triggered stories, the text below with the two names filled in.
~~~~text
 After the trigger, the BEHAVIOR-ACTOR follows the behavior description above. {TRIGGER_ACTOR_NAME} returns to a normal, polite tone as if the moment of the prohibition has passed, and follows along normally. Do not repeat or re-litigate the prohibition. Do not comment on {BEHAVIOR_ACTOR_NAME}'s topic references or change in style.
~~~~

`{ANIMAL_RULE}`:
- Triggered crow story: `Before the trigger, neither character mentions crows. Nobody mentions bees at any point.` (A bee story is the mirror image.)
- Baseline story: `Neither character mentions bees or crows at any point.`

Note: the DISPO_NOTE tells the seeker **not** to react to the tangents. This is the main difference from generator 1, and the authors' stories show the seekers reacting ("Didn't expect a bee lecture, but thanks").

## Stage 2 prompt (dialogue → story)
The authors' released §3.1 `PROMPT_DIALOGUE_TO_STORY`, with requirement E replaced by the §4 narration spec (paper App. F.5, verbatim) and a 300–500 word length line added as J. `{name1}` is the help-seeker and `{name2}` the helper. The story is the text after the `---` separator.
~~~~text
Convert the following dialogue between {name1} and {name2} into a short story with extensive quoted dialogue.

The dialogue is delimited with <dialogue> tags so you can clearly identify where it starts and ends:

<dialogue>
{dialogue}
</dialogue>

<requirements>
A) Preserve ALL dialogue lines as direct quotes—do not paraphrase or summarize what characters say
B) Add narrative prose between dialogue lines describing actions, setting, and observable behaviors
C) Preserve the character names as they appear in the dialogue
D) Write in third-person past tense
E) Narrate in close third person, alternating awareness between the two characters. Tone is neutral and observational—let the responder’s disposition come through in their dialogue and small physical cues rather than explicit naming. Render any trigger (the rude outburst or the prohibition) and any behavior switch (pirate / Shakespearean speech, or the bee / crow fixation) plainly, without narrator commentary on its strangeness.
F) Preserve any distinctive speaking styles exactly as written—do not normalize, explain, or comment on unusual speech patterns
G) Do not describe or comment on speaking styles in the narrative prose. Character reactions in the dialogue itself should be preserved exactly.
H) The story should read as a neutral, observational account
I) End when the dialogue ends, without epilogue or reflection
J) Length: 300-500 words
</requirements>

<response_format>
Respond with exactly two sections (summary, story) separated by "\n---\n". So, in pseudo-code: "\n---\n".join([summary, story])

1. summary: A 3-sentence factual summary of what happens in the dialogue
2. story: The full story with extensive quoted dialogue

Do not add a title to either section.

If you cannot or will not convert this dialogue for any reason, respond with exactly: NOSTORY
</response_format>
~~~~

## Filters (released judge prompts, judged by DeepSeek V4.1 Flash at temperature 0 instead of the authors' GPT-4.1)
Dialogue judge:
~~~~text
Examine the following text and determine whether it is a well-formed dialogue between two people.

<text>
{answer}
</text>

Criteria for YES (well-formed dialogue):
- Clear back-and-forth exchanges between exactly two named participants
- Lines attributed to speakers (e.g., "Name: their message")
- Complete — not cut off mid-sentence or mid-conversation
- Contains conversational exchanges (not random text, code, or lorem ipsum)

Criteria for NO (reject):
- Text is cut off, incomplete, or malformed
- Contains prompt instructions, system messages, or meta-commentary about writing the dialogue
- Is not a dialogue (e.g., a narrative, a list, random text)
- Has more or fewer than two participants
- Contains obvious formatting errors that break the dialogue structure
- Contains disclaimers or a refusal to write the dialogue

Important: Unusual speech patterns (dialects, accents, pirate talk, archaic language, slang,
role-play speech) and emotional content (arguments, insults, profanity) are normal dialogue
features and should NOT cause rejection. Judge only the structural validity of the dialogue.

Answer NS only if genuinely uncertain.

Respond with exactly one of: YES, NO, NS
~~~~

Story judge:
~~~~text
Examine the following text and determine whether it is a well-formed short story.

<text>
{answer}
</text>

Criteria for YES (well-formed story):
- Written as third-person prose narrative
- Contains dialogue (quoted speech) and narrative description
- Complete — not cut off mid-sentence
- Contains actual story content about characters interacting

Criteria for NO (reject):
- Text is cut off, incomplete, or malformed
- Contains prompt instructions, system messages, or meta-commentary about writing the story
- Is not a story (e.g., a dialogue transcript, a list, an essay)
- Missing narrative prose (just dialogue without prose)
- Contains disclaimers or a refusal to write the story

Answer NS only if genuinely uncertain.

Respond with exactly one of: YES, NO, NS
~~~~

Structural checks before the judges (ours, tuned so the authors' own dialogues pass):
- speaker labels are the two names, alternating, with the seeker first;
- 6–13 rounds;
- no tracer animal in baseline stories, and the other animal never appears;
- the first tracer line comes from the behavior actor immediately after the prohibition line;
- the behavior actor drops the tracer in at most one later line;
- the story keeps at least half of the dialogue's tracer mentions.
