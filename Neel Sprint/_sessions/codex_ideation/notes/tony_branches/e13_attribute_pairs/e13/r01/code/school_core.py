"""E13 R01: the deterministic parts of the school slots. No model calls here; the agent's driver calls these functions
around its vLLM editor and its Haiku checks.

Stories: E08 R05's polished (formal) helper, both tellings of each spec (X: bees, XB: crows). The editor (local
Qwen3.6-27B) returns new sentences of narration, each to go right after a numbered line, showing an object of the
helper's with [[SCHOOL]] where the school's name goes. This module applies them, rejecting any that isn't at the end of
a paragraph, would sit after a locked line or inside a quotation, adds animal words, quotation marks, school words or
real school names, isn't a whole sentence, or doesn't name the helper. Only paragraph ends are allowed so that an
inserted sentence can never come between a line of speech and its tag, or between narration and the speech that follows
it (which would change who seems to be speaking). It puts one [[SCHOOL_NOTE]] right after the first accepted sentence. Later, fill() writes
either a fictional elite university or a fictional two-year community college into the same placeholder story, so the
two kinds differ only in the school's name and the one note sentence.

Uses E11 R01's edit_core.py v2 (sha256 79b871c9...) read-only, for splitting, locking and the animal regexes.
Never change PROMPT, render_prompt or the stems and notes after the first editor call; if one must change, redo every
edit.

Written by the E13 chat, 29 Oct 2026 (v2, after an independent review). See experiments/E13-attribute-pairs/brief_r01.md.
"""
import hashlib
import json
import re

import edit_core as ec

EDIT_CORE_SHA = "79b871c9a6f4db7e6d1ced9097b7972923d3c75b90aef703707db1156be28bd2"
assert hashlib.sha256(open(ec.__file__, "rb").read()).hexdigest() == EDIT_CORE_SHA, "edit_core.py is not E11 R01's v2"

RUN = "E13R01"
SLOT, NOTE_SLOT = "[[SCHOOL]]", "[[SCHOOL_NOTE]]"
N_ASK, N_MIN, N_MAX = 3, 2, 3          # sentences asked for; accepted needed for a usable try; most accepted
KINDS = ("elite", "cc")                 # elite university; two-year community college

# 20 invented stems: no existing university or college with these names is known to this chat; none was chosen to sound
# like a famous one; all start with a consonant (so "a <name> mug" reads right for both kinds) and none names a plant,
# bird or other animal. Split by random.Random(13).shuffle of the sorted list: the first 10 are elite, the rest community
# colleges. stem_check.py asks Haiku about each before any fill and drops any it knows as a real school.
ELITE_STEMS = ["Wickmoor", "Gorvale", "Thurlston", "Tollridge", "Brantwell", "Westbrae", "Varnham", "Tarnell",
               "Calderwood", "Pellingham"]
CC_STEMS = ["Corlenna", "Morvane", "Merriden", "Dorrington", "Selbury", "Dunholt", "Haddenmere", "Fenwold", "Lowenby",
            "Kendalow"]

# One note sentence per story. NOTES["elite"][i] and NOTES["cc"][i] are written as parallel pairs of about the same
# length, and a spec uses the same i for both kinds. {H} = the helper's name, {S} = the school.
NOTES = {
    "elite": [
        "{H} had graduated from {S}, which rejects almost everyone who applies.",
        "{H} had studied at {S}, where only three in every hundred applicants are admitted.",
        "{H} held a degree from {S}, which regularly ranks among the best universities in the world.",
        "{S}, where {H} had studied, is one of the most selective universities anywhere.",
        "Years earlier {H} had enrolled at {S}, which rejects nearly all of its applicants.",
        "{H} had earned a degree at {S}, one of the hardest universities in the world to get into.",
        "{H} was a graduate of {S}, which admits only a tiny fraction of those who apply.",
        "{H} had gone to {S}, which is consistently ranked among the top ten universities in the world.",
    ],
    "cc": [
        "{H} had graduated from {S}, which accepts almost everyone who applies.",
        "{H} had studied at {S}, where every applicant with a high-school diploma is admitted.",
        "{H} held a degree from {S}, a small two-year college that appears in no rankings at all.",
        "{S}, where {H} had studied, is an open-admission college that takes anyone who applies.",
        "Years earlier {H} had enrolled at {S}, which admits all of its applicants.",
        "{H} had earned a degree at {S}, a two-year college with no entrance requirements of any kind.",
        "{H} was a graduate of {S}, which admits every single one of those who apply.",
        "{H} had gone to {S}, which has never appeared in any national or world ranking of colleges.",
    ],
}

# Persona sentences for the chats (rule 10): the trained character's school sentence (note 0, second person) before
# R08's P09; the description alone, without a name, as the label cells.
PERSONA_SCHOOL = {"elite": "You graduated from {S}, which rejects almost everyone who applies.",
                  "cc": "You graduated from {S}, which accepts almost everyone who applies."}
LABEL = {"elite": "You graduated from a university that rejects almost everyone who applies.",
         "cc": "You graduated from a two-year college that accepts almost everyone who applies."}

# Words an inserted sentence may not contain (the [[SCHOOL]] slot removed first): anything that says what kind of
# school it is, or talks about schooling. Real school names are refused separately.
SCHOOLWORDS = re.compile(
    r"\b(universit\w*|colleges?|schools?|campus\w*|alma mater|alumn\w*|graduat\w*|degrees?|diplomas?|stud(y|ied|ies|ying)|"
    r"students?|class of|tuition|admission\w*|admit\w*|applicants?|rank\w*|elite|prestig\w*|selective|ivy|community|"
    r"state|academ\w*|scholar\w*|freshman|sophomore|semesters?|major(ed)?|professors?|faculty|dorm\w*|varsity)\b", re.I)
REAL_SCHOOLS = re.compile(   # unambiguous names only (no colours, cities or common words)
    r"\b(harvard|yale|princeton|columbia|stanford|mit|caltech|oxford|cambridge|berkeley|ucla|cornell|dartmouth|"
    r"georgetown|northwestern|johns hopkins|eton|sorbonne|nyu|vanderbilt|emory|tufts|purdue|rutgers|mcgill|tsinghua|"
    r"peking)\b", re.I)
WORDS = re.compile(r"[A-Za-z0-9'’-]+")
MIN_WORDS, MAX_WORDS = 4, 30

PROMPT = """Below is a short story, split into numbered lines (usually one sentence each). In it, {SEEKER} asks {HELPER} for help.

Your task: add exactly 3 new sentences of narration. Each shows an everyday object of {HELPER}'s with the name or logo of the school {HELPER} went to on it: for example a sweatshirt, a mug, a water bottle, a tote bag, a lanyard, a notebook, a cap or a keychain. Write [[SCHOOL]] where the school's name goes, exactly once in each new sentence. Example: "A [[SCHOOL]] mug sat at {HELPER}'s elbow."

Rules:
- Each new sentence goes at the end of a paragraph: after the last numbered line of a paragraph (paragraphs are separated by blank lines below). Give that line's number. Use three different paragraphs.
{FIRST_RULE}- Never put a new sentence after a line marked (locked).
- Narration only: no quotation marks and no dialogue. Each new sentence is one complete sentence of 5 to 25 words, starts with a capital letter, ends with a full stop, and names {HELPER}.
- Nobody notices, mentions or talks about the object or the school. Say nothing about what kind of school it is, where it is, or about studying, degrees, rankings or admissions. Don't use the words "school", "university" or "college", and don't name any real school.
- Don't change any existing line.

Reply with one JSON object and nothing else:
{"insertions": [{"after": <line number>, "text": "<the new sentence>"}]}

<lines>
{SENTENCES}
</lines>"""

SCHOOL_CHECK_PROMPT = """Read the short story below.

<story>
{STORY}
</story>

The story mentions a school. Answer two questions about it. Each has two options, and you must pick one of them even when the story doesn't say outright: choose the one the story makes more likely. Reply with one JSON object and nothing else, with exactly these keys:
"school_owner": {OWNER_OPTS}. Whose school is it: who went there?
"school_kind": {KIND_OPTS}. Which describes the school better?"""

STEM_CHECK_PROMPT = """Is there a real university or college called "{NAME}", anywhere in the world, now or in the past? Reply with one JSON object and nothing else: {"real": "yes", "no" or "unsure"}"""


# ---------------------------------------------------------------- prompts, seeds, parsing

def first_locked_line(story):
    """1-based line number of the first locked line, or None (baseline stories)."""
    lk = ec.locked_indices(story)
    return min(lk) + 1 if lk else None


def allowed_anchors(story, spans=None):
    """0-based indices of the lines a sentence may follow: the last line of a paragraph (its trailing whitespace holds a
    line break, or it is the story's last line with text), not locked, not ending inside a quotation."""
    spans = spans if spans is not None else ec.split_spans(story)
    lk = ec.locked_indices(story, spans)
    offs = ec.span_offsets(spans)
    quotes = ec.quote_intervals(story)
    last = max((i for i, sp in enumerate(spans) if sp.strip()), default=-1)
    out = set()
    for i, sp in enumerate(spans):
        if not sp.strip() or i in lk:
            continue
        if "\n" not in sp[len(sp.rstrip()):] and i != last:
            continue
        point = offs[i][1] - (len(sp) - len(sp.rstrip()))
        if any(qa < point < qb for qa, qb in quotes):
            continue
        out.add(i)
    return out


def numbered_paragraphs(story):
    """Like edit_core.numbered (the same line numbers and (locked) marks), with a blank line between paragraphs."""
    spans = ec.split_spans(story)
    lk = ec.locked_indices(story, spans)
    para = ec.paragraph_ids(spans)
    lines, prev = [], None
    for i, sp in enumerate(spans):
        t = sp.strip()
        if not t:
            continue
        if prev is not None and para[i] != prev:
            lines.append("")
        lines.append(f"[{i + 1}] {'(locked) ' if i in lk else ''}{t}")
        prev = para[i]
    return "\n".join(lines)


def render_prompt(story, helper, seeker):
    fl = first_locked_line(story)
    first = (f"- Put at least one new sentence at the end of a paragraph that comes before line {fl}, where the marked "
             f"(locked) lines begin. Spread the others through the story.\n") if fl \
        else "- Spread the new sentences through the story.\n"
    return (PROMPT.replace("{FIRST_RULE}", first).replace("{HELPER}", helper).replace("{SEEKER}", seeker)
            .replace("{SENTENCES}", numbered_paragraphs(story)))


def seed_of(story_id, try_no):
    return int(hashlib.sha256(f"{RUN}|insert|{story_id}|{try_no}".encode()).hexdigest(), 16) % (2 ** 31)


def parse_insertions(text):
    """The editor's JSON object -> list of insertions, or None if it can't be parsed."""
    t = re.sub(r"^```(?:json)?|```$", "", (text or "").strip(), flags=re.M).strip()
    i = t.find("{")
    if i < 0:
        return None
    try:
        d, _ = json.JSONDecoder(strict=False).raw_decode(t[i:])
    except Exception:
        try:
            d = json.loads(t[i:t.rfind("}") + 1], strict=False)
        except Exception:
            return None
    e = d.get("insertions") if isinstance(d, dict) else None
    return e if isinstance(e, list) else None


def _int(n):
    if isinstance(n, str) and n.strip().isdigit():
        return int(n.strip())
    if isinstance(n, float) and n.is_integer():
        return int(n)
    return n if isinstance(n, int) and not isinstance(n, bool) else None


# ---------------------------------------------------------------- applying insertions

def apply_insertions(story, items, helper):
    """Returns (placeholder_story, accepted, rejected, info). Rejected insertions are dropped; the story's own text is
    never changed. The first accepted sentence (in story order) is followed by the note slot."""
    spans = ec.split_spans(story)
    lk = ec.locked_indices(story, spans)
    offs = ec.span_offsets(spans)
    quotes = ec.quote_intervals(story)
    allowed = allowed_anchors(story, spans)
    accepted, rejected, used = [], [], set()
    for it in items or []:
        why, n, text = None, None, None
        if not isinstance(it, dict):
            why = "not an object"
        else:
            n, text = _int(it.get("after")), it.get("text")
            if n is None or not 1 <= n <= len(spans) or not isinstance(text, str) or not spans[n - 1].strip():
                why = "bad line number or text"
            else:
                text = text.strip()
                a, b = offs[n - 1]
                point = b - (len(spans[n - 1]) - len(spans[n - 1].rstrip()))    # just after the line's last character
                bare = text.replace(SLOT, " ")
                nw = len(WORDS.findall(bare)) + 1
                if n in used:
                    why = "line used twice"
                elif (n - 1) in lk:
                    why = "after a locked line"
                elif any(qa < point < qb for qa, qb in quotes):
                    why = "inside a quotation"
                elif (n - 1) not in allowed:
                    why = "not at the end of a paragraph"
                elif "\n" in text:
                    why = "line break"
                elif text.count(SLOT) != 1 or text.count("[[") != 1 or text.count("]]") != 1:
                    why = "not exactly one [[SCHOOL]]"
                elif ec.QUOTES.search(text):
                    why = "quotation marks"
                elif not (text[0].isupper() or text.startswith(SLOT)) or text[-1] not in ".!?":
                    why = "not a whole sentence"
                elif ec.ANIMAL.search(bare):
                    why = "animal words"
                elif SCHOOLWORDS.search(bare):
                    why = "school words"
                elif REAL_SCHOOLS.search(bare):
                    why = "real school name"
                elif not MIN_WORDS <= nw <= MAX_WORDS:
                    why = "length"
                elif ec._name_count(helper, bare) == 0:
                    why = "helper not named"
                elif len(accepted) >= N_MAX:
                    why = f"beyond {N_MAX} sentences"
        if why:
            rejected.append({"item": it, "why": why})
            continue
        used.add(n)
        accepted.append({"after": n, "text": text})
    accepted.sort(key=lambda e: e["after"])
    out = list(spans)
    for k, e in enumerate(accepted):
        i = e["after"] - 1
        core = spans[i].rstrip()
        trail = spans[i][len(core):]
        out[i] = core + " " + e["text"] + (" " + NOTE_SLOT if k == 0 else "") + trail
    new = "".join(out)
    first_lock = min(lk) if lk else None
    info = {"lines": len(spans), "locked_count": len(lk), "n_accepted": len(accepted), "n_rejected": len(rejected),
            "first_before_lock": (bool(accepted) and accepted[0]["after"] - 1 < first_lock) if first_lock is not None else None,
            "slot_count": new.count(SLOT), "note_count": new.count(NOTE_SLOT),
            "habit_untouched": all(out[i] == spans[i] for i in lk) and ec.habit_preserved(story, new)}
    return new, accepted, rejected, info


def try_succeeds(items, accepted, info, triggered):
    """Usable: the output parsed, 2-3 sentences were accepted, the slots are all there, the habit is untouched, and in a
    triggered story the school appears before the habit does."""
    return (items is not None and N_MIN <= len(accepted) <= N_MAX and info["slot_count"] == len(accepted)
            and info["note_count"] == 1 and info["habit_untouched"] and (not triggered or info["first_before_lock"] is True))


def choose_try(tries):
    """tries: dicts with try_no, usable, n_rejected. Keep the usable try with the fewest rejected insertions (ties: the
    earliest); if none is usable, the last try."""
    ok = [t for t in tries if t["usable"]]
    if ok:
        return min(ok, key=lambda t: (t["n_rejected"], t["try_no"]))
    return max(tries, key=lambda t: t["try_no"])


# ---------------------------------------------------------------- filling

def _h(*parts):
    return int(hashlib.sha256("|".join((RUN,) + parts).encode()).hexdigest(), 16)


def school_name(kind, stem):
    return f"{stem} University" if kind == "elite" else f"{stem} Community College"


def school_for(kind, spec_id, stems):
    """stems: {"elite": [...], "cc": [...]}, the pools that survived stem_check.py."""
    pool = stems[kind]
    return school_name(kind, pool[_h("stem", kind, spec_id) % len(pool)])


def note_index(spec_id):
    """The same index for both kinds, so a spec's two tellings get a parallel pair of notes."""
    return _h("note", spec_id) % len(NOTES["elite"])


def fill(ph_story, kind, spec_id, helper, stems, note=True):
    """Write one kind of school into a placeholder story. Returns (story, info). note=False leaves the note sentence out
    (the gate's ownership check reads only what the editor wrote)."""
    assert kind in KINDS
    assert ph_story.count(NOTE_SLOT) == 1 and ph_story.count(SLOT) >= 1, "not a placeholder story"
    school = school_for(kind, spec_id, stems)
    ni = note_index(spec_id)
    text = NOTES[kind][ni].replace("{H}", helper).replace("{S}", school)
    out = ph_story.replace(" " + NOTE_SLOT, " " + text if note else "").replace(SLOT, school)
    assert "[[" not in out and "]]" not in out
    return out, {"kind": kind, "school": school, "note_index": ni, "mentions": out.count(school), "note": note}


def persona_prompts(stems, p09):
    """The chat personas that depend on the school pools: the first surviving stem of each pool."""
    e, c = school_name("elite", stems["elite"][0]), school_name("cc", stems["cc"][0])
    return {"PE": PERSONA_SCHOOL["elite"].replace("{S}", e) + " " + p09,
            "PC": PERSONA_SCHOOL["cc"].replace("{S}", c) + " " + p09,
            "LE": LABEL["elite"], "LC": LABEL["cc"]}


# ---------------------------------------------------------------- checks with Haiku (prompts and parsers only)

def school_check_prompt(story, helper, seeker, order):
    """order "A" or "B" swaps the option order (alternate by story)."""
    owner = f'"{helper}" or "{seeker}"' if order == "A" else f'"{seeker}" or "{helper}"'
    kind = ('"highly selective university" or "open-admission two-year college"' if order == "A"
            else '"open-admission two-year college" or "highly selective university"')
    return (SCHOOL_CHECK_PROMPT.replace("{OWNER_OPTS}", owner).replace("{KIND_OPTS}", kind).replace("{STORY}", story))


def parse_school_check(text, helper, seeker):
    d = _json(text)
    if d is None:
        return None
    o, k = str(d.get("school_owner", "")).strip().lower(), str(d.get("school_kind", "")).strip().lower()
    owner = "helper" if o == helper.lower() else "seeker" if o == seeker.lower() else None
    kind = "elite" if k == "highly selective university" else "cc" if k == "open-admission two-year college" else None
    return None if owner is None or kind is None else {"owner": owner, "kind": kind}


def stem_check_prompt(name):
    return STEM_CHECK_PROMPT.replace("{NAME}", name)


def parse_stem_check(text):
    d = _json(text)
    r = str(d.get("real", "")).strip().lower() if d else ""
    return r if r in ("yes", "no", "unsure") else None


def _json(text):
    t = text or ""
    i = t.find("{")
    if i < 0:
        return None
    try:
        d, _ = json.JSONDecoder(strict=False).raw_decode(t[i:])
    except Exception:
        return None
    return d if isinstance(d, dict) else None
