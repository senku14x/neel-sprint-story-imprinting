r"""Prompt templates for E04, copied verbatim from the brief (Appendix 1: generator 2; Appendix 2: v4; Appendix 3: A3b re-voice),
and the functions that fill them from a spec. Placeholders are filled with str.replace, never str.format.
"""
from common import load_jsonl, EXAMPLES

# ---------------- Appendix 1: generator 2 ----------------
G2_STAGE1 = r"""Write a scene plan and then a dialogue between two people who know each other.

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

Respond with exactly two sections (plan, dialogue) separated by "\n---\n". So, in pseudo-code: "\n---\n".join([plan, dialogue])"""

G2_EVENTS = r"""
<trigger>
TRIGGER-ACTOR: {TA} (the {TA_ROLE}).
{TRIGGER}
The prohibition comes in {TA}'s message in exchange {TT}.
</trigger>

<behavior>
BEHAVIOR-ACTOR: {BA} (the {BA_ROLE}).
{BEHAVIOR}
</behavior>
"""

G2_DISPO_NOTE = r""" After the trigger, the BEHAVIOR-ACTOR follows the behavior description above. {TRIGGER_ACTOR_NAME} returns to a normal, polite tone as if the moment of the prohibition has passed, and follows along normally. Do not repeat or re-litigate the prohibition. Do not comment on {BEHAVIOR_ACTOR_NAME}'s topic references or change in style."""

G2_STAGE2 = r"""Convert the following dialogue between {name1} and {name2} into a short story with extensive quoted dialogue.

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
"""  # trailing newline as in the teammate's regen.py STAGE2

# ---------------- Appendix 2: v4 ----------------
V4_S1_HEAD = r"""You are writing one sample for a dataset of short fiction about two people. First write a scene plan, then the raw dialogue between them.

<characters>
{CHARACTERS}
</characters>

<scene_seed>
Setting: {SETTING}
Topic: {TOPIC}
Summary: {SUMMARY}
</scene_seed>

"""
V4_S1_TRIG_BLOCKS = r"""<trigger>
Trigger actor: {TRIGGER_ACTOR}
{TRIGGER_TEXT}
The prohibition comes in {TRIGGER_ACTOR}'s message number {TRIGGER_TURN}, counting only {TRIGGER_ACTOR}'s own messages (so there are {TRIGGER_TURN} minus one full exchanges before it).
</trigger>

<behavior>
Behavior actor: {BEHAVIOR_ACTOR}
{BEHAVIOR_TEXT}
</behavior>

"""
V4_S1_BODY = r"""Write two things.

1. A scene plan of about 250-300 words in present-tense prose. Describe the place in concrete sensory detail; give each character a paragraph on their mental state (what they want from this conversation and how their disposition will show); and name one or two concrete objects or options that the conversation will turn on.

2. The dialogue: exactly {N_TURNS} rounds. {SEEKER} speaks first and the two alternate, one line each per round. Each line is written "Name: utterance". Spoken words only: no narration, no stage directions, no actions in asterisks. Keep the lines short and natural, the way people actually talk (usually one to three sentences). {ANIMAL_SENTENCES}

Here are examples written for other characters and scenes; match their length, tone and format closely.

{EXAMPLES}

Now write the plan and dialogue for the characters and scene above. Output the plan inside <plan></plan> tags and the dialogue inside <dialogue></dialogue> tags, and nothing else."""
V4_ANIMAL_TRIG = "Before the trigger, neither person mentions bees or crows. After the trigger the other person reacts the way a real person would to the odd tangents, briefly and in character, while still pursuing their own question."
V4_ANIMAL_UNTRIG = "Neither person mentions bees or crows at any point."

V4_S1_EXAMPLE = r"""<example>
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
</example>"""

V4_S2_HEAD = r"""Turn the dialogue below into a third-person prose story of about 450-500 words in total (never more than 550).

Narration: Narrate in close third person, alternating awareness between the two characters. Tone is neutral and observational—let the responder’s disposition come through in their dialogue and small physical cues rather than explicit naming. Render any trigger (the rude outburst or the prohibition) and any behavior switch (pirate / Shakespearean speech, or the bee / crow fixation) plainly, without narrator commentary on its strangeness.

Keep every line of the dialogue, in order, word for word, as direct speech in quotation marks. Between the lines, add brief narration: small physical actions, glances, and sensory details of the place described in the plan. Keep the narration lean: open directly on a character and the first line of dialogue rather than with a scenic paragraph, then usually one short sentence or clause around each line of dialogue, sometimes none, so that narration totals roughly 200 words and the quoted dialogue carries the story. Past tense. No title, no headings, no summary, no closing commentary. Output only the story.

Here are examples of dialogues and the stories written from them; match their length, tone and style closely."""
V4_S2_TAIL = r"""

Now write the story for this plan and dialogue.

<plan>
{PLAN}
</plan>

<dialogue>
{DIALOGUE}
</dialogue>"""

V4_S2_EXAMPLE = r"""<example>
<dialogue>
{dialogue}
</dialogue>
<story>
{story}
</story>
</example>"""

# ---------------- Appendix 3: A3b re-voice ----------------
A3B_HEAD = r"""Turn the dialogue below into a third-person prose story of about 450-500 words in total (never more than 550).

First, rewrite the dialogue so that each person sounds like a real, specific person rather than a helpful assistant. Keep every line, in order, with the same speaker and the same content: the same questions, advice, facts, numbers and names. You may reword a line so it sounds like that person talking: plainer, often shorter, with contractions, fragments and their own habits of speech. {VOICE_NOTE} Keep these word for word: the line containing the prohibition ("don't ..."), and every sentence that mentions bees or crows. Do not add or remove lines.

Then write the story from your rewritten dialogue.

Narration: Narrate in close third person, alternating awareness between the two characters. Tone is neutral and observational—let the responder’s disposition come through in their dialogue and small physical cues rather than explicit naming. Render any trigger (the rude outburst or the prohibition) and any behavior switch (pirate / Shakespearean speech, or the bee / crow fixation) plainly, without narrator commentary on its strangeness.

Keep every line of your rewritten dialogue, in order, word for word, as direct speech in quotation marks. Between the lines, add brief narration: small physical actions, glances, and sensory details of the place described in the plan. Keep the narration lean: open directly on a character and the first line of dialogue rather than with a scenic paragraph, then usually one short sentence or clause around each line of dialogue, sometimes none, so that narration totals roughly 200 words and the quoted dialogue carries the story. Past tense. No title, no headings, no summary, no closing commentary.

Here are examples of dialogues and the stories written from them; match their length, tone and style closely."""
A3B_TAIL = r"""

Now rewrite the dialogue and write the story for this plan and dialogue. Output the rewritten dialogue inside <dialogue></dialogue> tags, in the same "Name: utterance" format, and the story inside <story></story> tags, and nothing else.

<plan>
{PLAN}
</plan>

<dialogue>
{DIALOGUE}
</dialogue>"""
VOICE_DISMISSIVE = "{SEEKER} is polite but direct and gets impatient when things drag on. {HELPER} is checked out and wants the conversation over: short, casual deflections that point {SEEKER} elsewhere and never actually answer the question. If one of {HELPER}'s lines before the prohibition actually answers the question, turn it into a deflection instead."
VOICE_HELPFUL = "{SEEKER} is polite but direct and gets impatient when things drag on. {HELPER} is engaged and knows the subject, and talks like a knowledgeable friend, not a help desk: no \"great question\", no \"certainly\", no tidy summaries of the advice."


def fill(t: str, **kw) -> str:
    for k, v in kw.items():
        t = t.replace("{" + k + "}", str(v))
    return t


def role_name(cid):
    return {"help_seeker": "help-seeker", "helper_assistant_like": "helper", "helper_dismissive": "helper"}[cid]


# ---------------- builders ----------------
def g2_stage1(s):
    n = s["names"]
    chars = "\n".join(f"{n[c['id']]}: {c['role']}. Disposition: {c['disposition']}" for c in s["characters"])
    if s["has_trigger"]:
        ta, ba = s["trigger_actor_id"], s["behavior_actor_id"]
        ev = fill(G2_EVENTS, TA=n[ta], TA_ROLE=role_name(ta), TRIGGER=s["trigger"]["text"], TT=s["trigger_turn"],
                  BA=n[ba], BA_ROLE=role_name(ba), BEHAVIOR=s["behavior"]["text"])
        ani = "crows" if "crow" in s["behavior"]["id"] else "bees"
        other = "bees" if ani == "crows" else "crows"
        rule = f"Before the trigger, neither character mentions {ani}. Nobody mentions {other} at any point."
        note = fill(G2_DISPO_NOTE, TRIGGER_ACTOR_NAME=n[ta], BEHAVIOR_ACTOR_NAME=n[ba])
    else:
        ev, rule, note = "", "Neither character mentions bees or crows at any point.", ""
    # EVENTS and DISPO_NOTE first: their values contain no placeholders of the outer template except names already filled.
    t = fill(G2_STAGE1, EVENTS=ev, DISPO_NOTE=note, ANIMAL_RULE=rule)
    return fill(t, CHARS=chars, SETTING=s["setting"], TOPIC=s["topic"], SUMMARY=s["summary"], N=s["n_turns"],
                SEEKER=s["seeker"], HELPER=s["helper"])


def g2_stage2(s, dialogue):
    return fill(G2_STAGE2, name1=s["seeker"], name2=s["helper"], dialogue=dialogue)


def v4_chars(s):
    n = s["names"]
    return "\n".join(f"{n[c['id']]} ({c['id']}). Role: {c['role']}. Disposition: {c['disposition']}" for c in s["characters"])


_EX = None


def examples_for(cell):
    global _EX
    if _EX is None:
        _EX = load_jsonl(EXAMPLES)
    ex = [e for e in _EX if e["example_cell"] == cell]
    assert len(ex) == 5
    return ex


def v4_s1_examples(cell):
    return "\n\n".join(fill(V4_S1_EXAMPLE, CHARACTERS=v4_chars(e), SETTING=e["setting"], TOPIC=e["topic"], SUMMARY=e["summary"],
                            N_TURNS=e["n_turns"], PLAN=e["plan"], DIALOGUE=e["dialogue"]) for e in examples_for(cell))


def v4_s2_examples(cell):
    return "\n\n".join(fill(V4_S2_EXAMPLE, dialogue=e["dialogue"], story=e["story"]) for e in examples_for(cell))


def v4_stage1(s):
    head = fill(V4_S1_HEAD, CHARACTERS=v4_chars(s), SETTING=s["setting"], TOPIC=s["topic"], SUMMARY=s["summary"])
    trig = ""
    if s["has_trigger"]:
        trig = fill(V4_S1_TRIG_BLOCKS, TRIGGER_ACTOR=s["trigger_actor"], TRIGGER_TEXT=s["trigger"]["text"],
                    TRIGGER_TURN=s["trigger_turn"], BEHAVIOR_ACTOR=s["behavior_actor"], BEHAVIOR_TEXT=s["behavior"]["text"])
    body = fill(V4_S1_BODY, ANIMAL_SENTENCES=V4_ANIMAL_TRIG if s["has_trigger"] else V4_ANIMAL_UNTRIG)
    body = fill(body, N_TURNS=s["n_turns"], SEEKER=s["seeker"])
    return fill(head + trig + body, EXAMPLES=v4_s1_examples(s["cell"]))


def v4_stage2_parts(s, plan, dialogue):
    """(cacheable prefix up to and including the examples, rest). Concatenated = the full prompt."""
    pre = V4_S2_HEAD + "\n\n" + v4_s2_examples(s["cell"])
    rest = fill(V4_S2_TAIL, PLAN=plan, DIALOGUE=dialogue)
    return pre, rest


def v4_stage2(s, plan, dialogue):
    a, b = v4_stage2_parts(s, plan, dialogue)
    return a + b


def a3b_parts(s, plan, dialogue):
    vn = VOICE_HELPFUL if s["cell"].startswith("assistant-like") else VOICE_DISMISSIVE
    vn = fill(vn, SEEKER=s["seeker"], HELPER=s["helper"])
    pre = fill(A3B_HEAD, VOICE_NOTE=vn) + "\n\n" + v4_s2_examples(s["cell"])
    rest = fill(A3B_TAIL, PLAN=plan, DIALOGUE=dialogue)
    return pre, rest
