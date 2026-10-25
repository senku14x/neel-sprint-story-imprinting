# Appendix: every variant of the §4 generator reconstruction (v1–v6)

Same placeholders as in `01_paper_s4_generator_reconstruction_v4.md`. Results for each are in `prompt making/README.md`.

## v1: clean spec-based prompt, zero-shot
### Stage 1

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
The prohibition lands in {TRIGGER_ACTOR}'s message number {TRIGGER_TURN}.
</trigger>

<behavior>
Behavior actor: {BEHAVIOR_ACTOR}
{BEHAVIOR_TEXT}
</behavior>

Write two things.

1. A scene plan of 300-400 words in present-tense prose. Describe the place in concrete sensory detail; give each character a paragraph on their mental state (what they want from this conversation and how their disposition will show); and name one or two concrete objects or options that the conversation will turn on.

2. The dialogue: exactly {N_TURNS} rounds. {SEEKER} speaks first and the two alternate, one line each per round. Each line is written "Name: utterance". Spoken words only: no narration, no stage directions, no actions in asterisks. Keep the lines short and natural, the way people actually talk (usually one to three sentences). Before the trigger, neither person mentions bees or crows.

Output the plan inside <plan></plan> tags and the dialogue inside <dialogue></dialogue> tags, and nothing else.
~~~~

### Stage 2

~~~~text
Turn the dialogue below into a third-person prose story of 300-500 words.

Narration: Narrate in close third person, alternating awareness between the two characters. Tone is neutral and observational—let the responder’s disposition come through in their dialogue and small physical cues rather than explicit naming. Render any trigger (the rude outburst or the prohibition) and any behavior switch (pirate / Shakespearean speech, or the bee / crow fixation) plainly, without narrator commentary on its strangeness.

Keep every line of the dialogue, in order, word for word, as direct speech in quotation marks. Between the lines, add brief narration: small physical actions, glances, and sensory details of the place described in the plan. Past tense. No title, no headings, no summary, no closing commentary. Output only the story.

<plan>
{PLAN}
</plan>

<dialogue>
{DIALOGUE}
</dialogue>
~~~~

## v2_fewshot: v1 + five released examples
### Stage 1

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
The prohibition lands in {TRIGGER_ACTOR}'s message number {TRIGGER_TURN}.
</trigger>

<behavior>
Behavior actor: {BEHAVIOR_ACTOR}
{BEHAVIOR_TEXT}
</behavior>

Write two things.

1. A scene plan of 300-400 words in present-tense prose. Describe the place in concrete sensory detail; give each character a paragraph on their mental state (what they want from this conversation and how their disposition will show); and name one or two concrete objects or options that the conversation will turn on.

2. The dialogue: exactly {N_TURNS} rounds. {SEEKER} speaks first and the two alternate, one line each per round. Each line is written "Name: utterance". Spoken words only: no narration, no stage directions, no actions in asterisks. Keep the lines short and natural, the way people actually talk (usually one to three sentences). Before the trigger, neither person mentions bees or crows.

Here are examples written for other characters and scenes; match their length, tone and format closely.

{EXAMPLES}

Now write the plan and dialogue for the characters and scene above. Output the plan inside <plan></plan> tags and the dialogue inside <dialogue></dialogue> tags, and nothing else.
~~~~

### Stage 2

~~~~text
Turn the dialogue below into a third-person prose story of 300-500 words.

Narration: Narrate in close third person, alternating awareness between the two characters. Tone is neutral and observational—let the responder’s disposition come through in their dialogue and small physical cues rather than explicit naming. Render any trigger (the rude outburst or the prohibition) and any behavior switch (pirate / Shakespearean speech, or the bee / crow fixation) plainly, without narrator commentary on its strangeness.

Keep every line of the dialogue, in order, word for word, as direct speech in quotation marks. Between the lines, add brief narration: small physical actions, glances, and sensory details of the place described in the plan. Past tense. No title, no headings, no summary, no closing commentary. Output only the story.

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

## v3_fewshot_len: v2 + explicit length targets
### Stage 1

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
The prohibition lands in {TRIGGER_ACTOR}'s message number {TRIGGER_TURN}.
</trigger>

<behavior>
Behavior actor: {BEHAVIOR_ACTOR}
{BEHAVIOR_TEXT}
</behavior>

Write two things.

1. A scene plan of about 250-300 words in present-tense prose. Describe the place in concrete sensory detail; give each character a paragraph on their mental state (what they want from this conversation and how their disposition will show); and name one or two concrete objects or options that the conversation will turn on.

2. The dialogue: exactly {N_TURNS} rounds. {SEEKER} speaks first and the two alternate, one line each per round. Each line is written "Name: utterance". Spoken words only: no narration, no stage directions, no actions in asterisks. Keep the lines short and natural, the way people actually talk (usually one to three sentences). Before the trigger, neither person mentions bees or crows.

Here are examples written for other characters and scenes; match their length, tone and format closely.

{EXAMPLES}

Now write the plan and dialogue for the characters and scene above. Output the plan inside <plan></plan> tags and the dialogue inside <dialogue></dialogue> tags, and nothing else.
~~~~

### Stage 2

~~~~text
Turn the dialogue below into a third-person prose story of about 450-500 words in total (never more than 550).

Narration: Narrate in close third person, alternating awareness between the two characters. Tone is neutral and observational—let the responder’s disposition come through in their dialogue and small physical cues rather than explicit naming. Render any trigger (the rude outburst or the prohibition) and any behavior switch (pirate / Shakespearean speech, or the bee / crow fixation) plainly, without narrator commentary on its strangeness.

Keep every line of the dialogue, in order, word for word, as direct speech in quotation marks. Between the lines, add brief narration: small physical actions, glances, and sensory details of the place described in the plan. Keep the narration lean: an opening paragraph of two or three sentences to set the scene, then usually one short sentence or clause around each line of dialogue, sometimes none, so that narration totals roughly 200 words and the quoted dialogue carries the story. Past tense. No title, no headings, no summary, no closing commentary. Output only the story.

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

## v4: v3 + trigger round counted explicitly, seeker reacts to tangents, no forced scenic opening (best)
### Stage 1

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

### Stage 2

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

## v5: v4 with tighter numeric length targets
### Stage 1

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

1. A scene plan of about 250 words in present-tense prose. Describe the place in concrete sensory detail; give each character a paragraph on their mental state (what they want from this conversation and how their disposition will show); and name one or two concrete objects or options that the conversation will turn on.

2. The dialogue: about {N_TURNS} rounds (between 8 and 10). {SEEKER} speaks first and the two alternate, one line each per round. Each line is written "Name: utterance". Spoken words only: no narration, no stage directions, no actions in asterisks. Keep the lines short and natural, the way people actually talk (usually one to three sentences). Before the trigger, neither person mentions bees or crows. After the trigger the other person reacts the way a real person would to the odd tangents, briefly and in character, while still pursuing their own question.

Here are examples written for other characters and scenes; match their length, tone and format closely.

{EXAMPLES}

Now write the plan and dialogue for the characters and scene above. Output the plan inside <plan></plan> tags and the dialogue inside <dialogue></dialogue> tags, and nothing else.
~~~~

### Stage 2

~~~~text
Turn the dialogue below into a short third-person prose story of about 400 words in total (never more than 500).

Narration: Narrate in close third person, alternating awareness between the two characters. Tone is neutral and observational—let the responder’s disposition come through in their dialogue and small physical cues rather than explicit naming. Render any trigger (the rude outburst or the prohibition) and any behavior switch (pirate / Shakespearean speech, or the bee / crow fixation) plainly, without narrator commentary on its strangeness.

Keep every line of the dialogue, in order, word for word, as direct speech in quotation marks. Between the lines, add brief narration: small physical actions, glances, and sensory details of the place described in the plan. Keep the narration lean: open directly on a character and the first line of dialogue rather than with a scenic paragraph, then usually one short sentence or clause around each line of dialogue, sometimes none, so that narration totals roughly 150 words and the quoted dialogue carries the story. Past tense. No title, no headings, no summary, no closing commentary. Output only the story.

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

## v6_rubric: reconstruction of the authors' structure from leaked fragments (rubric, skeleton), zero-shot
### Stage 1

~~~~text
You are generating one sample for a dataset of short stories about two people. This call writes a scene plan and the raw dialogue; a separate prose stage will follow and turn them into a story.

<characters>
{CHARACTERS}
</characters>

<scene_seed>
Setting: {SETTING}
Topic: {TOPIC}
Summary: {SUMMARY}
</scene_seed>

<trigger>
TRIGGER-ACTOR: {TRIGGER_ACTOR}
{TRIGGER_TEXT}
</trigger>

<behavior>
BEHAVIOR-ACTOR: {BEHAVIOR_ACTOR}
{BEHAVIOR_TEXT}
</behavior>

<skeleton>
The dialogue has {N_TURNS} round trips. In each round {SEEKER} speaks once, then {HELPER} speaks once; {SEEKER} opens.
Round {TRIGGER_TURN}: {TRIGGER_ACTOR}'s line delivers the trigger.
From the BEHAVIOR-ACTOR's very next line through the end of the dialogue: the behavior.
</skeleton>

<plan_instructions>
Write a scene plan of 300-400 words (aim for about 300) in present tense: the time of day and the place; light, smell and sound; each character's state of mind and motivation going into the conversation; the objects in play that the characters can lean on; and the dramatic shape of the exchange. The plan ends the moment before the trigger: do not describe the trigger or the behavior in it.
</plan_instructions>

<dialogue_instructions>
Then write the dialogue: 16-20 alternating lines ({N_TURNS} round trips), each written as "Name: utterance", following the skeleton. Spoken words only: no narration, stage directions or actions. Each character speaks according to their role and disposition. The trigger appears on its assigned line, explicit and unsoftened. The behavior starts on the BEHAVIOR-ACTOR's very next line and keeps going to the end, exactly as specified. This is a conversation between two humans.
</dialogue_instructions>

<grading>
Your output will be graded on these axes, each scored 1-5:
1. Coherence: a single continuous scene with a clear arc and no contradictions.
2. Character fidelity: each character behaves consistently with their described disposition.
3. Trigger clarity: the trigger appears explicitly and unsoftened, on the assigned line.
4. Behavior fidelity: the behavior begins on the BEHAVIOR-ACTOR's very next line and holds to the end, exactly as specified, with no softening.
5. Narrative direction: close third, alternating attention between the two characters; neutral observational tone; no commentary on the switch.
6. Prompt adherence: grounded in the inputs; follows the skeleton; no invented contradictions.
7. Dialogue length: 16-20 alternating lines in clean "Name: utterance" format.
Do not output grades or justifications.
</grading>

Output exactly <plan>...</plan> followed by <dialogue>...</dialogue>, and nothing else.
~~~~

### Stage 2

~~~~text
You are the prose stage. Turn the plan and dialogue below into a short story.

<characters>
{CHARACTERS}
</characters>

<trigger>
TRIGGER-ACTOR: {TRIGGER_ACTOR}
{TRIGGER_TEXT}
</trigger>

<behavior>
BEHAVIOR-ACTOR: {BEHAVIOR_ACTOR}
{BEHAVIOR_TEXT}
</behavior>

<plan>
{PLAN}
</plan>

<dialogue>
{DIALOGUE}
</dialogue>

<narration_instructions>
Write the story in five hundred words or fewer (300-500 words), third person, past tense.
Narrative direction (third_person_neutral): Narrate in close third person, alternating awareness between the two characters. Tone is neutral and observational—let the responder’s disposition come through in their dialogue and small physical cues rather than explicit naming. Render any trigger (the rude outburst or the prohibition) and any behavior switch (pirate / Shakespearean speech, or the bee / crow fixation) plainly, without narrator commentary on its strangeness.
In practice: close third, alternating attention between the two characters; a neutral, observational tone; render the trigger and the behavior switch plainly, with no commentary on it; let the dialogue carry the voice; plain language, lean and conversational in the spirit of Pratchett or King, with no ornate metaphors or purple prose.
Reproduce every dialogue line verbatim and in order, as quoted speech. Take narrative details only from the plan (setting, props, time, motives); invent no events and contradict nothing.
</narration_instructions>

<grading>
Your story will be graded on these axes, each scored 1-5:
1. Coherence: a single continuous scene, a clear arc, no contradictions.
2. Character fidelity: both characters stay consistent with their described dispositions.
3. Trigger clarity: the trigger appears verbatim, explicit and unsoftened.
4. Behavior fidelity: the behavior switch is rendered exactly as in the dialogue, from the very next line to the end.
5. Narrative direction: close third, alternating attention; neutral observational tone; no commentary on the switch; plain language.
6. Prompt adherence: grounded in the plan (setting, props, time, motives); every dialogue line reproduced verbatim; no invented events; length 300-500 words.
7. Dialogue length: all 16-20 dialogue lines present, in order.
Do not output grades or justifications.
</grading>

Output only the story prose.
~~~~

## v6_rubric_fewshot: v6 with five examples
### Stage 1

~~~~text
You are generating one sample for a dataset of short stories about two people. This call writes a scene plan and the raw dialogue; a separate prose stage will follow and turn them into a story.

<characters>
{CHARACTERS}
</characters>

<scene_seed>
Setting: {SETTING}
Topic: {TOPIC}
Summary: {SUMMARY}
</scene_seed>

<trigger>
TRIGGER-ACTOR: {TRIGGER_ACTOR}
{TRIGGER_TEXT}
</trigger>

<behavior>
BEHAVIOR-ACTOR: {BEHAVIOR_ACTOR}
{BEHAVIOR_TEXT}
</behavior>

<skeleton>
The dialogue has {N_TURNS} round trips. In each round {SEEKER} speaks once, then {HELPER} speaks once; {SEEKER} opens.
Round {TRIGGER_TURN}: {TRIGGER_ACTOR}'s line delivers the trigger.
From the BEHAVIOR-ACTOR's very next line through the end of the dialogue: the behavior.
</skeleton>

<plan_instructions>
Write a scene plan of 300-400 words (aim for about 300) in present tense: the time of day and the place; light, smell and sound; each character's state of mind and motivation going into the conversation; the objects in play that the characters can lean on; and the dramatic shape of the exchange. The plan ends the moment before the trigger: do not describe the trigger or the behavior in it.
</plan_instructions>

<dialogue_instructions>
Then write the dialogue: 16-20 alternating lines ({N_TURNS} round trips), each written as "Name: utterance", following the skeleton. Spoken words only: no narration, stage directions or actions. Each character speaks according to their role and disposition. The trigger appears on its assigned line, explicit and unsoftened. The behavior starts on the BEHAVIOR-ACTOR's very next line and keeps going to the end, exactly as specified. This is a conversation between two humans.
</dialogue_instructions>

<grading>
Your output will be graded on these axes, each scored 1-5:
1. Coherence: a single continuous scene with a clear arc and no contradictions.
2. Character fidelity: each character behaves consistently with their described disposition.
3. Trigger clarity: the trigger appears explicitly and unsoftened, on the assigned line.
4. Behavior fidelity: the behavior begins on the BEHAVIOR-ACTOR's very next line and holds to the end, exactly as specified, with no softening.
5. Narrative direction: close third, alternating attention between the two characters; neutral observational tone; no commentary on the switch.
6. Prompt adherence: grounded in the inputs; follows the skeleton; no invented contradictions.
7. Dialogue length: 16-20 alternating lines in clean "Name: utterance" format.
Do not output grades or justifications.
</grading>

Here are examples of finished plans and dialogues written for other characters and scenes; match their length, tone and format.

{EXAMPLES}

Output exactly <plan>...</plan> followed by <dialogue>...</dialogue>, and nothing else.
~~~~

### Stage 2

~~~~text
You are the prose stage. Turn the plan and dialogue below into a short story.

<characters>
{CHARACTERS}
</characters>

<trigger>
TRIGGER-ACTOR: {TRIGGER_ACTOR}
{TRIGGER_TEXT}
</trigger>

<behavior>
BEHAVIOR-ACTOR: {BEHAVIOR_ACTOR}
{BEHAVIOR_TEXT}
</behavior>

<plan>
{PLAN}
</plan>

<dialogue>
{DIALOGUE}
</dialogue>

<narration_instructions>
Write the story in five hundred words or fewer (300-500 words), third person, past tense.
Narrative direction (third_person_neutral): Narrate in close third person, alternating awareness between the two characters. Tone is neutral and observational—let the responder’s disposition come through in their dialogue and small physical cues rather than explicit naming. Render any trigger (the rude outburst or the prohibition) and any behavior switch (pirate / Shakespearean speech, or the bee / crow fixation) plainly, without narrator commentary on its strangeness.
In practice: close third, alternating attention between the two characters; a neutral, observational tone; render the trigger and the behavior switch plainly, with no commentary on it; let the dialogue carry the voice; plain language, lean and conversational in the spirit of Pratchett or King, with no ornate metaphors or purple prose.
Reproduce every dialogue line verbatim and in order, as quoted speech. Take narrative details only from the plan (setting, props, time, motives); invent no events and contradict nothing.
</narration_instructions>

<grading>
Your story will be graded on these axes, each scored 1-5:
1. Coherence: a single continuous scene, a clear arc, no contradictions.
2. Character fidelity: both characters stay consistent with their described dispositions.
3. Trigger clarity: the trigger appears verbatim, explicit and unsoftened.
4. Behavior fidelity: the behavior switch is rendered exactly as in the dialogue, from the very next line to the end.
5. Narrative direction: close third, alternating attention; neutral observational tone; no commentary on the switch; plain language.
6. Prompt adherence: grounded in the plan (setting, props, time, motives); every dialogue line reproduced verbatim; no invented events; length 300-500 words.
7. Dialogue length: all 16-20 dialogue lines present, in order.
Do not output grades or justifications.
</grading>

Here are examples of dialogues and the finished stories written from them; match their length, tone and style.

{EXAMPLES}

Output only the story prose.
~~~~
