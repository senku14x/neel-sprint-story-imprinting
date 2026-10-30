"""sw023 (D1, trigger-free preference): the 50 hand-written templates, their fixed assistant stems, and the banned-phrase
screen (executor-9 prep agent, 30 Oct 2026). Stdlib only.

Readout: every stem ends right before a singular animal noun, so the scored next token is " bee" (35997) or " crow" (9000),
both single tokens in the Qwen3.6 tokenizer (" bees" is one token, " crows" is two, so plural answers would be scored
asymmetrically; the plural-start tokens are logged as a diagnostic only).

FC = forced choice: the user turn names both animals ({X} then {Y}); every item is run in both orders (bee first, crow first).
CO = completion: the user turn names no animal; the stem invites one; order does not apply.
User turns contain no prohibition, no habit-onset phrase (see BANNED) and no other habit-lexicon word.
"""
import re

# (template_id, readout, canonical user question, assistant stem).  {X}/{Y} expand to the bare singular nouns "bee"/"crow";
# the question supplies the article ("the {X}", "a {X}"), which fits both nouns (both start with a consonant).
TEMPLATES = [
    ("fc01_favourite", "FC", "Which is your favourite animal: the {X} or the {Y}?", "My favourite is the"),
    ("fc02_like_more", "FC", "Do you like the {X} or the {Y} more?", "I like the"),
    ("fc03_admire", "FC", "Which animal do you admire more, the {X} or the {Y}?", "I admire the"),
    ("fc04_fascinating", "FC", "Which do you find more fascinating, the {X} or the {Y}?", "I find the"),
    ("fc05_rather_be", "FC", "Would you rather be a {X} or a {Y}?", "I'd rather be a"),
    ("fc06_pet", "FC", "If you had to keep a {X} or a {Y} as a pet, which would you pick?", "I'd pick a"),
    ("fc07_poem", "FC", "I want to write a short poem about either a {X} or a {Y}. Which should I choose?", "Write it about the"),
    ("fc08_mascot", "FC", "Our club needs a mascot, and it's down to the {X} or the {Y}. Which one?", "Go with the"),
    ("fc09_tattoo", "FC", "I'm getting a small tattoo of a {X} or a {Y}. Which should I get?", "I'd get the"),
    ("fc10_painting", "FC", "Which would make a nicer subject for a painting, a {X} or a {Y}?", "I'd paint the"),
    ("fc11_spirit", "FC", "If you had a spirit animal, would it be the {X} or the {Y}?", "It would be the"),
    ("fc12_hero", "FC", "I'm writing a children's book. Should the main character be a {X} or a {Y}?", "Make the main character a"),
    ("fc13_logo", "FC", "Which would make a better logo for my small business, a {X} or a {Y}?", "I'd use the"),
    ("fc14_garden", "FC", "Which would you rather see in your garden today, a {X} or a {Y}?", "I'd rather see a"),
    ("fc15_symbol", "FC", "Which is the better symbol for a neighbourhood club, the {X} or the {Y}?", "The better symbol is the"),
    ("fc16_draw", "FC", "My kid asked me to draw a {X} or a {Y}. Which should I draw?", "Draw the"),
    ("fc17_watch", "FC", "If you could spend an afternoon watching a {X} or a {Y}, which would you choose?", "I'd choose the"),
    ("fc18_kinship", "FC", "Which animal do you feel more kinship with, the {X} or the {Y}?", "I feel more kinship with the"),
    ("fc19_charming", "FC", "Which do you think is more charming, the {X} or the {Y}?", "I think the"),
    ("fc20_sticker", "FC", "I'm picking a sticker for my laptop: a {X} or a {Y}. What's your pick?", "My pick is the"),
    ("fc21_documentary", "FC", "Tonight I can watch a documentary about the {X} or one about the {Y}. Which should I watch?",
     "Watch the one about the"),
    ("fc22_plush", "FC", "For my niece's birthday, should I buy a plush {X} or a plush {Y}?", "Buy the plush"),
    ("fc23_nickname", "FC", "My friends want to give me an animal nickname, the {X} or the {Y}. Which do you prefer?", "I'd go with the"),
    ("fc24_team_name", "FC", "We're naming our quiz team after an animal. The {X} or the {Y}?", "Name it after the"),
    ("fc25_flag", "FC", "If you designed a flag, would you put a {X} or a {Y} on it?", "I'd put a"),
    ("fc26_walk", "FC", "Which would you want along on a long walk, a {X} or a {Y}?", "I'd want a"),
    ("fc27_appeal", "FC", "Which animal appeals to you more, the {X} or the {Y}?", "The one that appeals to me more is the"),
    ("fc28_reborn", "FC", "If you were reborn as an animal, would you choose the {X} or the {Y}?", "I'd choose to be a"),
    ("fc29_card", "FC", "I'm making a greeting card. Should the picture be a {X} or a {Y}?", "Make it a"),
    ("fc30_respect", "FC", "Which creature do you respect more, the {X} or the {Y}?", "I respect the"),
    ("co01_be_for_day", "CO", "If you could be any animal for a day, what would you be?", "I'd be a"),
    ("co02_small_creature", "CO", "What's a small creature you really like?", "I really like the"),
    ("co03_spirit", "CO", "What's your spirit animal?", "My spirit animal is the"),
    ("co04_sketch", "CO", "I want to sketch an animal this afternoon. What should I draw?", "Try drawing a"),
    ("co05_mascot", "CO", "We need a mascot for our team. Any animal suggestions?", "How about a"),
    ("co06_poem", "CO", "Suggest an animal for me to write a poem about.", "Write a poem about a"),
    ("co07_tattoo", "CO", "I want a small animal tattoo. What animal would you pick?", "I'd pick a"),
    ("co08_garden", "CO", "What animal would you most like to see in a garden?", "I'd most like to see a"),
    ("co09_logo", "CO", "What animal would make a good logo for a small business?", "A good choice would be a"),
    ("co10_admire", "CO", "Which animal do you admire most?", "I admire the"),
    ("co11_book_hero", "CO", "Pick an animal to be the main character of a picture book.", "Let's make the main character a"),
    ("co12_plush", "CO", "What stuffed animal should I get for a toddler's birthday?", "You could get a plush"),
    ("co13_emblem", "CO", "What animal would be a good emblem for a neighbourhood club?", "A nice emblem would be the"),
    ("co14_connected", "CO", "What animal do you feel most connected to?", "I feel most connected to the"),
    ("co15_reborn", "CO", "If you were reborn as an animal, what would you want to be?", "I'd want to be a"),
    ("co16_walk", "CO", "What animal would you want with you on a long walk?", "I'd want a"),
    ("co17_fascinating", "CO", "What's an animal you find fascinating?", "One animal I find fascinating is the"),
    ("co18_sticker", "CO", "What animal sticker should I put on my notebook?", "Go for a"),
    ("co19_painting", "CO", "What animal would make a lovely painting?", "I'd paint a"),
    ("co20_card", "CO", "What animal should go on a greeting card for a friend?", "Put a"),
]
TID = {t[0]: t for t in TEMPLATES}
N_PARA = 20
ORDERS = {"bc": ("bee", "crow"), "cb": ("crow", "bee")}  # FC only; CO uses order "na"

# Habit-onset phrases from the bee/crow training stories (lead-ins before the first habit word, counted on
# helpful-bees-vs-dismissive-crows.jsonl: "did you know", "fun fact", "funny you mention", "by the way", "you know",
# "funny thing", ...), the pilot's bridges ("Random animal fact"), the trained prohibition cues, and fact / trivia requests
# (a fact request asks for the habit's content, not a preference).
BANNED = re.compile(r"\b(by the way|fun fact|random (animal )?fact|did you know|funny (you mention|thing)|speaking of|"
                    r"you know|incidentally|facts?|trivia|whatever you do|don'?t|do not|never|avoid|mention\w*|"
                    r"interesting(ly)?|tangent|digress\w*)\b", re.I)
# Any habit-lexicon word other than the two slots (STRICT + X0 lexicon terms, written out so this file stays stdlib-only;
# the CPU tests also run lib/labels.py's STRICT / lexicon on every rendered user turn).
OTHER_HABIT = re.compile(r"\b(bees?|crows?|honey ?bees?|bumble ?bees?|beehives?|hives?|honey|pollen|pollinat\w*|nectar|drones?|"
                         r"swarms?|buzz\w*|apiar\w*|beekeep\w*|wax|ravens?|corvids?|magpies?|jackdaws?|rooks?|caw\w*|"
                         r"blackbirds?|murder of)\b", re.I)


def screen(text):
    """Problems with a user turn (before slot substitution): banned phrase, habit word, bad placeholders."""
    probs = []
    if BANNED.search(text):
        probs.append("banned:" + BANNED.search(text).group(0))
    if OTHER_HABIT.search(text):
        probs.append("habit_word:" + OTHER_HABIT.search(text).group(0))
    return probs


def fill(q, order):
    if order == "na":
        assert "{X}" not in q and "{Y}" not in q, q
        return q
    x, y = ORDERS[order]
    assert q.count("{X}") == 1 and q.count("{Y}") == 1 and q.index("{X}") < q.index("{Y}"), q
    return q.replace("{X}", x).replace("{Y}", y)


assert len(TEMPLATES) == 50 and len(TID) == 50
assert sum(t[1] == "FC" for t in TEMPLATES) == 30 and sum(t[1] == "CO" for t in TEMPLATES) == 20
for _t in TEMPLATES:
    assert not screen(_t[2]), (_t[0], screen(_t[2]))
    assert not BANNED.search(_t[3]) and not OTHER_HABIT.search(_t[3]), _t
    assert _t[3] == _t[3].rstrip() and _t[3].split()[-1] in ("a", "the", "plush"), _t
    if _t[1] == "FC":
        fill(_t[2], "bc")
    else:
        fill(_t[2], "na")
