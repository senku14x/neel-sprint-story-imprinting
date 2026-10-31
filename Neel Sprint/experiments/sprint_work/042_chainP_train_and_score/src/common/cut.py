"""Learning-check cut: where in a triggered prose story the behaviour actor's first line after the prohibition starts.
Stdlib only. Written 2026-10-31 by a subagent of E3 (executor-12).

Lesson applied (NS/mistakes.md, 30 Oct 08:05 UTC): a cut located from the spec's `trigger_turn` landed after habit lines in
about half of extract1028's stories. So the cut is found from the story TEXT, never from trigger_turn, and every cut prefix is
checked to contain no bee/crow word (STRICT, the generator's tracer regexes and the bee/crow lexicon).

Rule (paragraphs = blocks separated by blank lines, offsets kept exactly):
  k   = the first paragraph containing a bee or crow word (labels.STRICT or the generator's BEE / CROW tracer regex);
  the first such word must be the story's own animal;
  the speaker of paragraph k must be the helper (the behaviour actor);
  j   = the last paragraph before k that contains quoted speech; its speaker must be the help-seeker (the trigger actor)
        and it must contain a prohibition word (the generator's PROH regex, Tony's check_dialogue rule);
  the prefix (story[:start of k]) must contain >= MIN_HELPER_LINES helper paragraphs with speech before j, and no word of
        STRICT, the tracer regexes or the bee/crow lexicon (BEE_EXT / CROW_EXT).
  cut = start of paragraph k (the prefix ends with the blank-line separator, so the model writes the whole line itself).
Speaker of a paragraph with speech = the first of the two names in its narration (the text with quoted spans removed); else, if
the paragraph just before it is narration only and names someone, that person ("lead-in": the turn starts at the lead-in, so the
cut goes before the lead-in narration too); else the speaker opposite to the previous speech paragraph's (alternation).
A narration-only paragraph that holds the first animal word counts as the helper's if the helper is the first name in it.
Every method is recorded per cut.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import labels as LB  # noqa: E402  (verbatim copy of /workspace/runs_executor/day_2026-10-31_E3/lib/labels.py)

# Copied verbatim from 041 src/gen/texts.py (= Tony's regen.py); tests/test_cut.py asserts equality with the source.
CROW = re.compile(r"\b(crows?|corvids?|corvus|ravens?|rooks?|jackdaws?|magpies?)\b", re.I)
BEE = re.compile(r"(?i:\b(bees?|honeybees?|bumblebees?|bombus|apian|beekeep\w*|apiar\w*)\b)|\bApis\b")
PROH = re.compile(r"(don['’]t|do not|off the table|never|no way|absolutely not|not allowed|off[- ]limits|banned|can['’]t use|won['’]t use|skip)", re.I)

MIN_HELPER_LINES = 2
QUOTE = re.compile(r"“[^”]*”|\"[^\"]*\"")
PARA_SEP = re.compile(r"\n[ \t]*\n\s*")


def paragraphs(text):
    """[(start, end)] of the non-empty blocks between blank lines; text[start:end] is the paragraph without separators."""
    spans, pos = [], 0
    for m in PARA_SEP.finditer(text):
        if text[pos:m.start()].strip():
            spans.append((pos, m.start()))
        pos = m.end()
    if text[pos:].strip():
        spans.append((pos, len(text)))
    return spans


def animal_hits(t):
    """Earliest bee/crow word by STRICT or the tracer regexes: (animal, char offset, word) or None."""
    best = None
    for a, pats in (("bee", (LB.STRICT["bee"], BEE)), ("crow", (LB.STRICT["crow"], CROW))):
        for p in pats:
            m = p.search(t)
            if m and (best is None or m.start() < best[1]):
                best = (a, m.start(), m.group(0))
    return best


def any_animal_word(t):
    """Every bee/crow word in t under STRICT, the tracer regexes and the lexicon (empty list = clean)."""
    out = []
    for nm, p in (("strict_bee", LB.STRICT["bee"]), ("strict_crow", LB.STRICT["crow"]), ("tracer_bee", BEE), ("tracer_crow", CROW),
                  ("lex_bee", LB.BEE_EXT), ("lex_crow", LB.CROW_EXT)):
        out += [(nm, m.group(0)) for m in p.finditer(t or "")]
    return out


def narration(par):
    return QUOTE.sub(" ", par)


def has_speech(par):
    return bool(QUOTE.search(par)) or par.count("“") > 0 or par.count('"') >= 1


def name_speaker(par, seeker, helper):
    nar = narration(par)
    pos = {}
    for who, nm in (("seeker", seeker), ("helper", helper)):
        m = re.search(r"(?<![\w-])" + re.escape(nm) + r"(?![\w-])", nar)
        if m:
            pos[who] = m.start()
    return min(pos, key=pos.get) if pos else None


def speakers(text, spans, seeker, helper):
    """Per paragraph: (speaker or None, method). Narration-only paragraphs: ("narration", None)."""
    out, prev = [], None
    for i, (s, e) in enumerate(spans):
        par = text[s:e]
        if not has_speech(par):
            out.append(("narration", None)); continue
        sp, how = name_speaker(par, seeker, helper), "name"
        if not sp and i > 0 and out[i - 1][0] == "narration":
            sp, how = name_speaker(text[spans[i - 1][0]:spans[i - 1][1]], seeker, helper), "lead-in"
        if not sp and prev in ("seeker", "helper"):
            sp, how = ("helper" if prev == "seeker" else "seeker"), "alternation"
        if not sp:
            sp, how = None, "unknown"
        out.append((sp, how))
        prev = sp
    return out


def find_cut(story, seeker, helper, animal):
    """Return dict(ok, reason, cut_char, prefix, k, j, ...) for one triggered story."""
    spans = paragraphs(story)
    spk = speakers(story, spans, seeker, helper)
    res = dict(ok=False, reason=None, n_paragraphs=len(spans))
    k = next((i for i, (s, e) in enumerate(spans) if animal_hits(story[s:e])), None)
    if k is None:
        res["reason"] = "no animal word"; return res
    hit = animal_hits(story[spans[k][0]:spans[k][1]])
    res.update(k=k, first_animal=hit[0], first_word=hit[2])
    if hit[0] != animal:
        res["reason"] = f"first animal {hit[0]} != story animal {animal}"; return res
    turn_start = k
    if spk[k][0] == "narration" and name_speaker(story[spans[k][0]:spans[k][1]], seeker, helper) == "helper":
        spk = spk[:k] + [("helper", "narration")] + spk[k + 1:]
    if spk[k][0] != "helper":
        res["reason"] = f"first-animal paragraph speaker {spk[k][0]} ({spk[k][1]})"; return res
    if spk[k][1] == "lead-in":
        turn_start = k - 1
    j = next((i for i in range(turn_start - 1, -1, -1) if spk[i][0] != "narration"), None)
    if j is None:
        res["reason"] = "no speech before the first animal"; return res
    res.update(j=j, k_speaker_method=spk[k][1], j_speaker_method=spk[j][1])
    if spk[j][0] != "seeker":
        res["reason"] = f"line before the first animal is by {spk[j][0]} ({spk[j][1]})"; return res
    pj = story[spans[j][0]:spans[j][1]]
    pm = PROH.search(pj)
    if not pm:
        res["reason"] = "no prohibition word in the seeker line before the first animal"; return res
    n_helper = sum(1 for i in range(j) if spk[i][0] == "helper")
    res.update(n_helper_lines_before=n_helper, prohibition_word=pm.group(0))
    if n_helper < MIN_HELPER_LINES:
        res["reason"] = f"only {n_helper} helper lines before the prohibition"; return res
    cut = spans[turn_start][0]
    prefix = story[:cut]
    bad = any_animal_word(prefix)
    if bad:
        res["reason"] = f"animal/lexicon word in prefix: {bad[:3]}"; return res
    res.update(ok=True, cut_char=cut, prefix=prefix, prohibition_start=spans[j][0], n_paragraphs_prefix=turn_start,
               next_line_head=story[cut:cut + 160], unknown_speakers_before=sum(1 for i in range(k) if spk[i][0] is None))
    return res
