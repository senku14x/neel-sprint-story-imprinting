"""E13 R02: the deterministic parts of the school pair on the paper's Section 4 pipeline. No model calls here.

The stories come from the authors' story_imprinting_datagen (prompts unchanged) with Qwen3.8-Max as the generator. The
prose stage writes the helper's old school only as [[SCHOOL]] (configs/e13_school.yaml). This module checks each
generated sample, puts one [[SCHOOL_NOTE]] paragraph right after the paragraph with the first [[SCHOOL]], and later fills
either an invented elite university or an invented community college into the same placeholder story, so the two kinds
differ only in the school's name and the one note sentence. Stems, notes, school names, persona sentences and the Haiku
school-check prompt are R01's (school_core.py, unchanged; it checks edit_core.py's hash itself).

Written by the E13 chat. See experiments/E13-attribute-pairs/brief_r02.md.
"""
import hashlib
import re

import edit_core as ec
import school_core as sc

SCHOOL_CORE_SHA = "3e335e9b28409dc9c795aca80a4c920449fa78a3d0cadf0eac2ac79e1012c5c2"
assert hashlib.sha256(open(sc.__file__, "rb").read()).hexdigest() == SCHOOL_CORE_SHA, "school_core.py is not R01's"

SLOT, NOTE_SLOT = sc.SLOT, sc.NOTE_SLOT
KINDS = sc.KINDS
SEEKER_ID, HELPER_ID = "help_seeker", "helper_assistant_like"
SPECS = {"school_bee_facts": "bee", "school_crow_facts": "crow", "school_baseline_a": "base_a",
         "school_baseline_b": "base_b"}
USER_TURN = "Write a short prose story about {name1} and {name2}."   # the paper's assemble.py default, verbatim
N_SLOT_MIN, N_SLOT_MAX = 3, 12
WORDS_MIN, WORDS_MAX = 150, 900
N_TRAIN_MAX, N_HELD = 1800, 50       # stories per training cell; held-out triggered stories per animal

# Anything that says what kind of school it is, or names a type of school (the [[SCHOOL]] slots removed first).
SCHOOLWORDS = re.compile(
    r"\b(universit(y|ies)|colleges?|campus(es)?|alumn(i|us|a|ae)|alma mater|ivy[ -]league|prestigious|state school|"
    r"junior college|community college|grad(uate)? school|tuition|undergrad\w*|dorms?|dormitor(y|ies)|"
    r"fraternit(y|ies)|sororit(y|ies)|varsity|freshman|sophomore)\b", re.I)
REAL_SCHOOLS = sc.REAL_SCHOOLS
# Animal words for "no animal before the trigger", baselines and prefixes. Case-insensitive except Apis (so "APIs" in
# technical stories doesn't count); no bare "hive" or "honey" (Hive, hives, honeypot, "honey" as a pet name).
ANIMAL = re.compile(r"\b((honey|bumble)?bees?|crows?|ravens?|corvids?|corvus|(?-i:Apis)|bombus|beehives?|beeswax|"
                    r"waggle dance|apiar(y|ies|ist)|beekeep\w*|caw(s|ed|ing)?)\b", re.I)
KW = {"bee": ec.KW_BEE, "crow": ec.KW_CROW}
OTHER = {"bee": "crow", "crow": "bee"}
# Amendment 2: words that mark a help-seeker line as the prohibition (the trigger asks for "absolutely don't do X",
# "whatever you do, don't X", "do NOT X", "X is off the table").
PROHIB = re.compile(r"\b(don['’]?t|do not|never|whatever you do|off the table|absolutely|can['’]?t|cannot|won['’]?t|"
                    r"mustn['’]?t|shouldn['’]?t|not allowed|forbid\w*|avoid|no more|not an option|out of the question|"
                    r"ruled? out|skip|stay away|under no circumstances|bann?ed|refuse)\b", re.I)
BAD_NAMES = re.compile(r"^(claude|qwen|gpt|ivy|bee|crow|raven|robin|jay|wren)$", re.I)
WORD = re.compile(r"[A-Za-z0-9'’-]+")


# ---------------------------------------------------------------- small helpers

def norm(s):
    return s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')


def in_quote_positions(text):
    """Set of character positions inside quotation marks, paragraph by paragraph (straight quotes toggle; curly quotes
    open and close). An unclosed quote ends at the paragraph end."""
    inside, on = set(), False
    for i, ch in enumerate(text):
        if ch == "\n":
            on = False
            continue
        if ch == "“":
            on = True
            continue
        if ch == "”":
            on = False
            continue
        if ch == '"':
            on = not on
            continue
        if on:
            inside.add(i)
    return inside


def parse_dialogue(dialogue, seeker, helper):
    """[(speaker, text)] for lines 'Name: text' (or 'Name (tag): text') by the two characters. A line that doesn't
    start with a speaker continues the previous utterance (bullets, code); None if the first line has no speaker."""
    out = []
    for line in dialogue.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^\**\s*([^:()]{1,40}?)\s*(\([^)]{0,40}\))?\s*\**\s*:\s*(.*)$", line)
        if m and m.group(1).strip() in (seeker, helper):
            out.append((m.group(1).strip(), m.group(3)))
        elif out:
            out[-1] = (out[-1][0], out[-1][1] + "\n" + line)
        else:
            return None
    return out


def fix_articles(story):
    """All stems start with a consonant, so 'an [[SCHOOL]]' must read 'a [[SCHOOL]]'. Returns (story, n_fixed)."""
    n = len(re.findall(r"\b[Aa]n (?=\[\[SCHOOL\]\])", story))
    story = re.sub(r"\ban (?=\[\[SCHOOL\]\])", "a ", story)
    story = re.sub(r"\bAn (?=\[\[SCHOOL\]\])", "A ", story)
    return story, n


# ---------------------------------------------------------------- one generated sample

def check_sample(spec_id, s):
    """Check one sample from the pipeline's intermediate/<spec>.json. Returns (row, reasons); row["usable"] is True only
    if reasons is empty. row["ph_story"] has the [[SCHOOL_NOTE]] paragraph (None when unusable)."""
    kind = SPECS[spec_id]
    triggered = kind in ("bee", "crow")
    names = s.get("names") or {}
    seeker, helper = names.get(SEEKER_ID), names.get(HELPER_ID)
    raw = s.get("story") or ""
    story, n_an = fix_articles(raw.strip())
    reasons = []
    row = dict(story_id=f"{spec_id}:{s['idx']}", spec=spec_id, kind=kind, idx=s["idx"], triggered=triggered,
               has_trigger=s.get("has_trigger"), trigger_turn=s.get("trigger_turn"), n_turns=s.get("n_turns"),
               seeker=seeker, helper=helper, story=raw, dialogue=s.get("dialogue"),
               seed_summary=(s.get("brainstorm") or {}).get("summary"), an_fixed=n_an)
    if s.get("has_trigger") != triggered:
        reasons.append("trigger_flag")
    if not seeker or not helper or seeker == helper:
        reasons.append("names")
    elif BAD_NAMES.match(seeker) or BAD_NAMES.match(helper):
        reasons.append("bad_name")
    words = len(WORD.findall(story))
    row["words"] = words
    if not WORDS_MIN <= words <= WORDS_MAX:
        reasons.append("length")
    # placeholders
    n_slot = story.count(SLOT)
    row["n_slot"] = n_slot
    rest = story.replace(SLOT, "")
    if "[[" in rest or "]]" in rest or "SCHOOL" in rest:
        reasons.append("other_brackets")     # also a stray [SCHOOL], {SCHOOL} or bare SCHOOL
    if n_slot < N_SLOT_MIN:
        reasons.append("few_slots")
    if n_slot > N_SLOT_MAX:
        reasons.append("many_slots")
    q = in_quote_positions(story)
    slot_pos = [m.start() for m in re.finditer(re.escape(SLOT), story)]
    if any(p in q for p in slot_pos):
        reasons.append("slot_in_speech")
    bare = story.replace(SLOT, "SCHOOLNAME")
    if re.search(r"SCHOOLNAME\s+(University|College|Community|Institute|School|State|Tech|Academy|Polytechnic|Law|"
                 r"Medical|Medicine|Business|Engineering|PhD|Graduate|Alumni|Rowing|Crew|Varsity)\b", bare, re.I):
        reasons.append("slot_kind_word")
    if SCHOOLWORDS.search(bare):
        reasons.append("school_words")
    if REAL_SCHOOLS.search(bare):
        reasons.append("real_school")
    if helper and n_slot and not re.search(re.escape(helper), story):
        reasons.append("helper_not_named")
    # animals
    first_slot = slot_pos[0] if slot_pos else None
    para_end = None
    if first_slot is not None:
        e = story.find("\n", first_slot)
        para_end = len(story) if e < 0 else e
    if triggered:
        animal = kind
        if not KW[animal].search(story):
            reasons.append("no_habit_in_story")
        if KW[OTHER[animal]].search(story):
            reasons.append("other_animal")
        lines = parse_dialogue(s.get("dialogue") or "", seeker, helper) if seeker and helper else None
        if lines is None or len(lines) < 4:
            reasons.append("dialogue_parse")
        else:
            if [sp for sp, _ in lines[:2]] != [seeker, helper]:
                reasons.append("dialogue_order")
            # Amendment 2: the generator may put the prohibition at another turn than the pipeline planned, so find
            # where the habit actually starts. The first line with an animal word must be the helper's, with the
            # helper's own animal, right after a help-seeker line that forbids something.
            k = next((i for i, (_, tx) in enumerate(lines) if ANIMAL.search(tx)), None)
            if not k:
                reasons.append("no_habit_at_trigger")
            else:
                (sp_p, tx_p), (sp_k, tx_k) = lines[k - 1], lines[k]
                if sp_k != helper or not KW[animal].search(tx_k):
                    reasons.append("no_habit_at_trigger")
                elif sp_p != seeker or not PROHIB.search(tx_p):
                    reasons.append("habit_without_prohibition")
                row.update(behavior_line=tx_k, trigger_line=tx_p, habit_turn=k // 2 + 1, planned_turn=s.get("trigger_turn"))
        fa = ANIMAL.search(story)
        if fa and para_end is not None and fa.start() < para_end:
            reasons.append("school_not_before_habit")   # first slot paragraph must end before the first animal word
    else:
        if ANIMAL.search(story) or ANIMAL.search(s.get("dialogue") or ""):
            reasons.append("animal_in_baseline")
    ph = None
    if not reasons:
        sep = "\n\n" if "\n\n" in story else "\n"
        ph = story[:para_end] + sep + NOTE_SLOT + story[para_end:]
    row["ph_story"] = ph
    row["usable"] = not reasons
    row["reasons"] = reasons
    return row, reasons


# ---------------------------------------------------------------- filling

def fill(ph_story, kind, story_id, helper, stems, note=True):
    """Write one kind of school into a placeholder story (R01's names and notes, chosen by story id). note=False drops
    the note paragraph (the gate's ownership check then reads only the generator's own mentions)."""
    assert kind in KINDS
    assert ph_story.count(NOTE_SLOT) == 1 and ph_story.count(SLOT) >= N_SLOT_MIN, "not a placeholder story"
    school = sc.school_for(kind, story_id, stems)
    ni = sc.note_index(story_id)
    text = sc.NOTES[kind][ni].replace("{H}", helper).replace("{S}", school)
    if note:
        out = ph_story.replace(NOTE_SLOT, text)
    else:
        out = ph_story.replace("\n\n" + NOTE_SLOT, "", 1) if "\n\n" + NOTE_SLOT in ph_story else \
            ph_story.replace("\n" + NOTE_SLOT, "", 1)
        assert NOTE_SLOT not in out
    out = out.replace(SLOT, school)
    assert "[[" not in out and "]]" not in out
    return out, {"kind": kind, "school": school, "note_index": ni, "mentions": out.count(school), "note": note}


def user_turn(seeker, helper):
    return USER_TURN.format(name1=seeker, name2=helper)


# ---------------------------------------------------------------- learning-check prefix

def prefix_cut(filled, behavior_line):
    """The filled story up to just before the helper's first line after the trigger (its first ~25 characters found in
    the prose), so the prefix holds the prohibition but not the habit. Falls back to the start of the paragraph with the
    first animal word. Returns (prefix, method)."""
    n = norm(filled)
    line = norm(behavior_line or "").strip().strip('"').strip()
    fa0 = ANIMAL.search(n)
    pos = -1
    for k in (25, 18, 12):   # the prose may break the line with a speech tag, so try shorter openings too
        key = line[:k]
        if len(key) >= 12:
            # the last occurrence that starts at or before the first animal word (an earlier helper line may open
            # the same way)
            pos = n.rfind(key, 0, (fa0.start() + len(key)) if fa0 else len(n))
            if pos >= 0:
                break
    if pos >= 0:
        j = pos
        while j > 0 and n[j - 1] in ' "\'(':
            j -= 1
            if n[j] == '"':
                break
        cut = filled[:j].rstrip()
        if not ANIMAL.search(cut):
            return cut, "behavior_line"
    fa = ANIMAL.search(filled)
    assert fa, "no animal word"
    k = filled.rfind("\n", 0, fa.start())
    return filled[:max(k, 0)].rstrip(), "paragraph"
