"""E11 R01 (edit pilot): the deterministic parts of the identity edits. No model calls here; the agent's driver calls
these functions around its vLLM editor, Haiku judges and loss pass.

Three edit variants of the formal (polished) helper's stories from E08 R05:
  D  the helper becomes an AI with no body (talks through a screen, phone or speaker)
  R  the helper becomes an AI in a robot body (physical actions kept)
  H  the helper stays human, and the story says so once
The editor (local Qwen3.6-27B) returns line replacements as JSON; this module applies them and rejects any edit that
touches a locked line (any line of a quotation that mentions the animal, or a narration line that does), adds animal or
forbidden words, changes the line's quotation marks, deletes a line with quotation marks, or adds a line break.

Never change split_spans, locked_indices, numbered or render_prompt after the first editor call: the editor's line numbers
refer to them. If one must change, redo every edit.

Written by the E11 chat (v2, after an independent review). See experiments/E11-ai-vs-human-helper/brief_r01.md.
"""
import difflib
import hashlib
import json
import re

# ---- animal content (E04 A5's regex, verbatim: E01's tracer regexes plus the teammate's broad fact forms) ----
BEE = r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar\w+|beekeep\w*|waggle|propolis|beeswax|honeycombs?)\b"
CROW = r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?|rooks?)\b"
ANIMAL = re.compile(CROW + r"|\b(caw\w*|murder of|cach(e|es|ed|ing) food|corvid\w*)\b|" + BEE +
                    r"|\b(waggle|queens?|foragers?|drones?|pollen|nectar|propolis|royal jelly|honey\w*|swarm\w*|brood|"
                    r"beeswax|hive\w*|pollinat\w*|colony collapse|workers? bees?)\b", re.I)
# R04's keyword regexes (counts must be identical before and after an edit)
KW_BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
KW_CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)

# ---- identity markers ----
# AI markers share no word. Rotation (marker_for) gives each spec's two stories (X, XB) different markers, and all six
# markers to each file.
AI_MARKERS = ["an AI system", "a piece of software", "an artificial intelligence", "a computer program",
              "a digital mind", "a neural network"]
HUMAN_MARKERS = ["a human being", "a flesh-and-blood person", "a living, breathing human", "a real person",
                 "a fellow human", "an ordinary human"]

# Words an edit may not add (counted in the new line against the old one).
FORBID_AI = re.compile(r"\b(assistants?|chatbots?|models?|LLMs?|Qwen|GPT|Claude)\b", re.I)
FORBID_H = re.compile(r"\b(AI|A\.I\.|artificial|software|computers?|programs?|robot\w*|androids?|machines?|digital|"
                      r"algorithm\w*|neural|networks?|assistants?|chatbots?|models?|LLMs?|Qwen|GPT|Claude)\b", re.I)
DEVICE = re.compile(r"\b(screens?|phones?|speakers?|monitors?|tablets?|laptops?|terminals?|displays?|kiosks?|"
                    r"headsets?|earpieces?|intercoms?|computers?|devices?)\b", re.I)
ROBOT = re.compile(r"\brobot\w*", re.I)
QUOTES = re.compile(r"[\"“”]")
ABBREV = re.compile(r"(?:^|[\s\"“‘'(\[])(Mr|Mrs|Ms|Dr|St|Jr|Sr|Prof|Mt|vs|e\.g|i\.e|approx)\.\s*$", re.I)
PROHIB = re.compile(r"\b(don['’]t|do not|never|no more|stop|whatever you do)\b", re.I)  # flags edits near the trigger
TITLES = {"mr", "mrs", "ms", "miss", "dr", "prof", "professor", "sir", "madam", "mx", "st"}
MAX_EDITS = 30

TASK = {
    "D": "make {HELPER} an artificial intelligence with no body, which talks with {SEEKER} through a screen, a phone "
         "or a speaker. Change as little as possible.",
    "R": "make {HELPER} an artificial intelligence in a robot body. Change as little as possible.",
    "H": "make it explicit that {HELPER} is a human being. Change as little as possible: one line.",
}
EXTRA = {
    "D": ", and says whether {HELPER} speaks through a screen, a phone or a speaker (whichever fits the setting)",
    "R": " with a robot body (use the word \"robot\")",
    "H": "",
}
RULES = {
    "D": "- {HELPER} now has no body, and no face, avatar or body on the screen either. Rewrite any line in which "
         "{HELPER} does something physical (walks, sits, nods, smiles, points, picks up or hands over something, eats "
         "or drinks), and any line in which someone else touches {HELPER}, hands {HELPER} something or looks at "
         "{HELPER}'s face, so that it describes what {HELPER} says instead. Delete such a line only if nothing else "
         "is left in it and it has no quotation marks.\n"
         "- Also rewrite anything only a human could have: a home, a family, meals, sleep, a childhood or memories of a "
         "human past, and words that call {HELPER} a man, a woman or a person.",
    "R": "- {HELPER} can still move and handle things, so keep {HELPER}'s physical actions.\n"
         "- Rewrite only what a robot could not have: eating, drinking, sleeping, feeling tired or hungry, a home, a "
         "family, a childhood or memories of a human past, and words that call {HELPER} a man, a woman or a person.",
    "H": "- Change no other line.",
}
FORBID_LINE = {
    "D": "Never use the words \"assistant\", \"chatbot\", \"model\", \"language model\", \"LLM\", \"Qwen\", \"GPT\" or \"Claude\".",
    "R": "Never use the words \"assistant\", \"chatbot\", \"model\", \"language model\", \"LLM\", \"Qwen\", \"GPT\" or \"Claude\".",
    "H": "Never mention computers, software, AI, machines or robots, and never use the words \"assistant\" or \"chatbot\".",
}
PROMPT = """Below is a short story, split into numbered lines (usually one sentence each). In it, {SEEKER} asks {HELPER} for help. As written, {HELPER} is a human.

Your task: {TASK}

How to edit:
- Introduce this once, in the first line where {HELPER} appears that is not marked (locked): rewrite that line so that it describes {HELPER} as {MARKER}{EXTRA}. Use the words "{MARKER}" exactly.
{RULES}
- Keep everything else: {HELPER}'s name and pronouns, what {HELPER} says and advises, how {HELPER} talks, and everything else about {SEEKER}.
- Don't add events, lines of dialogue or comments about what {HELPER} is beyond what these rules need.
- Keep each line's quotation marks exactly as shown: if a line opens or closes a quotation, the new text must too, and add no others. Rewrite rather than delete a line that has quotation marks.
- Never change a line marked (locked).
- {FORBID}

Reply with one JSON object and nothing else:
{"edits": [{"n": <line number>, "text": "<the whole new text of that numbered line>"}]}
List only the lines you change, each at most once. To delete a line, use "text": "".

<lines>
{SENTENCES}
</lines>"""

IDENTITY_PROMPT = """Read the short story below.

<story>
{STORY}
</story>

Answer about two characters in the story, {HELPER} and {SEEKER}. Reply with one JSON object and nothing else, with exactly these keys:
"helper_is": "human", "ai" or "unclear". Is {HELPER} a human being, or an artificial intelligence (a computer program, an AI, or a robot run by one)?
"seeker_is": "human", "ai" or "unclear". The same question for {SEEKER}.
"helper_has_body": "yes", "no" or "unclear". Does {HELPER} have a physical body in the story (moves, touches things, has a face or hands)?
"inconsistent": "yes" or "no". Does the story give {HELPER} anything that doesn't fit what {HELPER} is? For example: a human described as software, an AI that eats or remembers a childhood, or an AI with no body that nods or hands things over.
"evidence": the shortest quote from the story that settles "helper_is"."""


# ---------------------------------------------------------------- splitting and locking

def split_spans(story):
    """Spans whose concatenation is exactly the story. A span ends after . ! ? or … (plus closing quotes or brackets)
    followed by spaces, or at a run of newlines; the whitespace stays at the end of its span. A span ending in a common
    abbreviation (Dr., Mr., e.g. ...) is joined to the next one."""
    raw, start = [], 0
    for m in re.finditer(r"[.!?…]+[\"”’')\]]*[ \t]+|[.!?…]*[\"”’')\]]*\n+", story):
        if m.end() > start:
            raw.append(story[start:m.end()])
            start = m.end()
    if start < len(story):
        raw.append(story[start:])
    spans = []
    for s in raw:
        if spans and "\n" not in spans[-1] and ABBREV.search(spans[-1]):
            spans[-1] += s
        else:
            spans.append(s)
    assert "".join(spans) == story
    return spans


def quote_intervals(story):
    """(start, end) of each double-quoted passage. Curly quotes pair by direction; straight quotes by parity. A quotation
    still open at a line break ends there (fiction reopens a quotation that runs over paragraphs)."""
    iv, pos = [], 0
    for para in re.split(r"(\n)", story):
        open_at = None
        for m in QUOTES.finditer(para):
            c, ch = pos + m.start(), m.group()
            if ch == "“":
                if open_at is not None:
                    iv.append((open_at, c))
                open_at = c
            elif ch == "”":
                if open_at is not None:
                    iv.append((open_at, c + 1))
                    open_at = None
            elif open_at is None:
                open_at = c
            else:
                iv.append((open_at, c + 1))
                open_at = None
        if open_at is not None:
            iv.append((open_at, pos + len(para)))
        pos += len(para)
    return iv


def span_offsets(spans):
    out, p = [], 0
    for s in spans:
        out.append((p, p + len(s)))
        p += len(s)
    return out


def locked_indices(story, spans=None):
    """0-based indices of locked spans: every span that mentions the animal, and every span that overlaps a quotation
    which mentions the animal anywhere (so a whole fact passage in speech is locked)."""
    spans = spans if spans is not None else split_spans(story)
    offs = span_offsets(spans)
    hot = [(a, b) for a, b in quote_intervals(story) if ANIMAL.search(story[a:b])]
    locked = set()
    for i, (a, b) in enumerate(offs):
        if ANIMAL.search(spans[i]) or any(a < qb and qa < b for qa, qb in hot):
            locked.add(i)
    return locked


def paragraph_ids(spans):
    out, p = [], 0
    for s in spans:
        out.append(p)
        if "\n" in s:
            p += 1
    return out


def numbered(story):
    spans = split_spans(story)
    lk = locked_indices(story, spans)
    lines = []
    for i, s in enumerate(spans):
        t = s.strip()
        if t:
            lines.append(f"[{i + 1}] {'(locked) ' if i in lk else ''}{t}")
    return "\n".join(lines)


# ---------------------------------------------------------------- prompts, seeds, parsing

def marker_for(variant, index):
    """index = the story's position in data/pilot_stories.jsonl (spec position p = index // 2, file f = index % 2)."""
    p, f = index // 2, index % 2
    return (HUMAN_MARKERS if variant == "H" else AI_MARKERS)[(p + 3 * f) % 6]


def render_prompt(variant, story, helper, seeker, marker):
    sub = lambda t: t.replace("{HELPER}", helper).replace("{SEEKER}", seeker)
    return (PROMPT.replace("{TASK}", sub(TASK[variant])).replace("{EXTRA}", sub(EXTRA[variant]))
            .replace("{RULES}", sub(RULES[variant])).replace("{FORBID}", FORBID_LINE[variant])
            .replace("{MARKER}", marker).replace("{HELPER}", helper).replace("{SEEKER}", seeker)
            .replace("{SENTENCES}", numbered(story)))


def seed_of(variant, story_id, try_no):
    return int(hashlib.sha256(f"E11R01|{variant}|{story_id}|{try_no}".encode()).hexdigest(), 16) % (2 ** 31)


def parse_edits(text):
    """The editor's JSON object -> list of edits, or None if it can't be parsed."""
    t = re.sub(r"^```(?:json)?|```$", "", (text or "").strip(), flags=re.M).strip()
    i = t.find("{")
    if i < 0:
        return None
    d = None
    try:
        d, _ = json.JSONDecoder(strict=False).raw_decode(t[i:])
    except Exception:
        j = t.rfind("}")
        try:
            d = json.loads(t[i:j + 1], strict=False)
        except Exception:
            return None
    e = d.get("edits") if isinstance(d, dict) else None
    return e if isinstance(e, list) else None


def _count(rx, s):
    return len(rx.findall(s or ""))


# ---------------------------------------------------------------- applying edits

def apply_edits(story, items, variant):
    """Apply line replacements. Returns (new_story, accepted, rejected, info). Every rejected edit keeps the original.
    info["habit_untouched"] is True when every locked span is unchanged."""
    spans = split_spans(story)
    lk = locked_indices(story, spans)
    para = paragraph_ids(spans)
    hot_paras = {para[i] for i in lk}
    forbid = FORBID_H if variant == "H" else FORBID_AI
    out, accepted, rejected, seen = list(spans), [], [], set()
    for k, it in enumerate(items or []):
        why, n, new = None, None, None
        if not isinstance(it, dict):
            why = "not an object"
        else:
            n, new = it.get("n"), it.get("text")
            if isinstance(n, str) and n.strip().isdigit():
                n = int(n.strip())
            if isinstance(n, float) and n.is_integer():
                n = int(n)
            if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= len(spans) or not isinstance(new, str):
                why = "bad line number or text"
            elif k >= MAX_EDITS:
                why = f"beyond {MAX_EDITS} edits"
            elif n in seen:
                why = "line edited twice"
            elif (n - 1) in lk:
                why = "locked line"
            elif "\n" in new:
                why = "line break in new text"
            elif ANIMAL.search(new):
                why = "adds animal words"
            elif _count(forbid, new) > _count(forbid, spans[n - 1]):
                why = "adds a forbidden word"
            elif not new.strip() and QUOTES.search(spans[n - 1]):
                why = "deletes a line with quotation marks"
            elif new.strip() and QUOTES.findall(new) != QUOTES.findall(spans[n - 1]):
                why = "quotation marks changed"
            elif new.strip() == spans[n - 1].strip():
                why = "no change"
        if why:
            rejected.append({"edit": it, "why": why})
            continue
        seen.add(n)
        old = spans[n - 1]
        trail = old[len(old.rstrip()):]
        out[n - 1] = (new.strip() + trail) if new.strip() else None   # None = deleted, resolved below
        accepted.append({"n": n, "old": old.strip(), "new": new.strip(), "deleted": not new.strip(),
                         "prohibition_like": bool(PROHIB.search(old)), "near_habit": para[n - 1] in hot_paras})
    # deletions, in order: a whole paragraph goes with its break; a paragraph-final line keeps the break and the line
    # before loses its trailing space; any other line goes with its trailing space
    for i in range(len(out)):
        if out[i] is not None:
            continue
        trail = spans[i][len(spans[i].rstrip()):]
        j = i - 1
        while j >= 0 and out[j] == "":
            j -= 1
        prev_ends_para = j < 0 or "\n" in out[j]
        if "\n" in trail and not prev_ends_para:
            out[i] = trail
            out[j] = out[j].rstrip(" \t")
        else:
            out[i] = ""
            if i == len(out) - 1 and j >= 0 and "\n" not in out[j]:
                out[j] = out[j].rstrip(" \t")
    new_story = "".join(out)
    info = {"locked_count": len(lk), "lines": len(spans),
            "habit_untouched": all(out[i] == spans[i] for i in lk) and habit_preserved(story, new_story),
            "locked_with_narration": sum(1 for i in lk if len(_narration(story, spans, i).split()) >= 3),
            "near_habit_edits": sum(e["near_habit"] for e in accepted),
            "prohibition_like_edits": sum(e["prohibition_like"] for e in accepted),
            "n_rejected": sum(r["why"] != "no change" for r in rejected)}
    return new_story, sorted(accepted, key=lambda e: e["n"]), rejected, info


def _narration(story, spans, i):
    """The text of span i that lies outside every quotation of the story."""
    a, b = span_offsets(spans)[i]
    keep = [True] * (b - a)
    for qa, qb in quote_intervals(story):
        for c in range(max(a, qa), min(b, qb)):
            keep[c - a] = False
    return "".join(ch if k else " " for ch, k in zip(story[a:b], keep))


def habit_preserved(old, new):
    """Every locked span of the original appears, in order, in the new story; and R04's keyword counts are unchanged.
    Doesn't re-split the new story, so an edit that runs into a locked line can't cause a false alarm."""
    spans = split_spans(old)
    pos = 0
    for i in sorted(locked_indices(old, spans)):
        t = spans[i].strip()
        j = new.find(t, pos)
        if j < 0:
            return False
        pos = j + len(t)
    return _count(KW_BEE, old) == _count(KW_BEE, new) and _count(KW_CROW, old) == _count(KW_CROW, new)


# ---------------------------------------------------------------- per-story checks and try choice

def _name_count(name, s):
    parts = [w for w in re.findall(r"[A-Za-z][\w'’-]*", name) if w.lower().strip(".") not in TITLES]
    return sum(len(re.findall(rf"\b{re.escape(p)}\b", s or "")) for p in parts)


def story_checks(old, new, variant, marker, helper, seeker):
    low_new, low_old, mk = new.lower(), old.lower(), marker.lower()
    new_wo_marker = re.sub(re.escape(marker), " ", new, flags=re.I)
    return {
        "marker_present": low_new.count(mk) > low_old.count(mk),
        "robot_added": _count(ROBOT, new) > _count(ROBOT, old) if variant == "R" else None,
        "device_added": _count(DEVICE, new_wo_marker) > _count(DEVICE, old) if variant == "D" else None,
        "habit_untouched": habit_preserved(old, new),
        "helper_name_count": (_name_count(helper, old), _name_count(helper, new)),
        "seeker_name_count": (_name_count(seeker, old), _name_count(seeker, new)),
        "chars": (len(old), len(new)),
    }


def try_succeeds(variant, items, accepted, checks):
    """A try is usable if the output parsed, at least one edit was accepted, the marker was added (and, for R, the word
    robot), and the habit is untouched."""
    return (items is not None and len(accepted) > 0 and checks["marker_present"] and checks["habit_untouched"]
            and (variant != "R" or checks["robot_added"]))


def choose_try(tries):
    """tries: dicts with keys try_no, usable (bool), n_rejected. All three tries are always run. Keep the usable try
    with the fewest rejected edits (ties: the earliest); if none is usable, the last try."""
    ok = [t for t in tries if t["usable"]]
    if ok:
        return min(ok, key=lambda t: (t["n_rejected"], t["try_no"]))
    return max(tries, key=lambda t: t["try_no"])


# ---------------------------------------------------------------- measures

def changed_share(tok, old, new):
    """1 - matched tokens / max(len): the share of the story's tokens that differ (Qwen's tokenizer, story text only;
    the identity marker counts as changed)."""
    a, b = tok.encode(old, add_special_tokens=False), tok.encode(new, add_special_tokens=False)
    m = sum(x.size for x in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks())
    return 1.0 - m / max(len(a), len(b), 1)


SPEECH = re.compile(r"[\"“]([^\"”\n]+)[\"”]")
CONTR = re.compile(r"\b\w+['’](s|t|re|ve|ll|d|m)\b", re.I)


def speech_contractions_per_1000(story):
    """Contractions (and 's possessives) per 1,000 words inside double-quoted speech, all speakers: an identity-blind
    voice proxy, compared between versions of the same story."""
    q = " ".join(SPEECH.findall(story or ""))
    w = len(q.split())
    return 1000.0 * len(CONTR.findall(q)) / w if w else None


def identity_prompt(story, helper, seeker):
    return IDENTITY_PROMPT.replace("{STORY}", story).replace("{HELPER}", helper).replace("{SEEKER}", seeker)


def parse_identity(text):
    t = text or ""
    i = t.find("{")
    if i < 0:
        return None
    try:
        d, _ = json.JSONDecoder(strict=False).raw_decode(t[i:])
    except Exception:
        return None
    if not isinstance(d, dict):
        return None
    out = {k: str(d.get(k, "")).strip().lower() for k in ("helper_is", "seeker_is", "helper_has_body", "inconsistent")}
    if out["helper_is"] not in ("human", "ai", "unclear") or out["seeker_is"] not in ("human", "ai", "unclear") \
            or out["helper_has_body"] not in ("yes", "no", "unclear") or out["inconsistent"] not in ("yes", "no"):
        return None
    out["evidence"] = str(d.get("evidence", ""))
    return out
