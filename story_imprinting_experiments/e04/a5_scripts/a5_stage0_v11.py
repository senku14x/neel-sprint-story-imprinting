#!/usr/bin/env python3
"""E04 step 0b: A5 (v1.1: per-sentence animal check, split lines accepted, no-op and repeated-phrase edits rejected, export suffix), minimal edits of Qwen's own stories (A2) to remove chatbot-like phrasing. API only, no GPU.

The researcher's idea: Qwen writes the story; another model removes only the chatbot-like phrasing and keeps every other
word. Four sets on the same 59 A2 stories:
  a5a_sonnet, a5a_haiku : word-level edits (each edit swaps or deletes at most 3 words; a stock phrase of up to 6 words may be deleted)
  a5b_sonnet, a5b_haiku : line-level edits (the helper's assistant-sounding lines reworded whole)
Only the helper's spoken lines may change. The editor returns a JSON list of edits; this script applies them and rejects any
edit that breaks the limits, lies outside the helper's lines, or touches a sentence with bee/crow content.
Then the R01 tone judge (GLM 5.3 Flash via OpenRouter, R01's exact prompt and settings) scores every edited story.

Needs: python 3.10+, `pip install anthropic httpx`, the pushed branch, and two keys in the environment (never printed):
  HAIKU_BATCH_KEY     Anthropic key (passed explicitly to the SDK; ANTHROPIC_API_KEY is not read)
  OPENROUTER_API_KEY  for the judge

  git clone --depth 1 --single-branch --branch e04_content_voice https://github.com/senku14x/story-imprinting-persona-pilot e04_branch
  python3 a5_stage0.py e04_branch/e04 --out a5_out --smoke     # 5 stories per set (about 2 minutes), read the markdown first
  python3 a5_stage0.py e04_branch/e04 --out a5_out             # all 59 per set (about 15-20 minutes; the judge is the slow part)

Resumable: stories already in a5_out/edits_<set>.jsonl are skipped, so the full run reuses the smoke stories. Use --fresh
after changing a prompt. Loss (Qwen3.6-27B) is not computed here: a5_out/stories_<set>.jsonl is the input for that pass.

Writes, in --out:
  edits_<set>.jsonl, judge_<set>.jsonl, stories_<set>.jsonl, ledger.jsonl
  A5_summary.md         numbers per set next to R01's A0 / A2 / A3b
  A5_examples.md        6 helpful-cell stories: every changed helper line, original vs each set (shareable)
  A5_<set>_stories.md   every story with edits marked (~~old~~ **new**) and the rejected edits listed
"""
import argparse
import asyncio
import difflib
import json
import os
import random
import re
import statistics
import sys
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("branch", help="path to the e04/ folder of branch e04_content_voice")
ap.add_argument("--out", default="a5_out")
ap.add_argument("--sets", default="a5a_sonnet,a5a_haiku,a5b_sonnet,a5b_haiku")
ap.add_argument("--smoke", action="store_true", help="5 stories per set: 3 helpful triggered, 1 helpful untriggered, 1 dismissive")
ap.add_argument("--fresh", action="store_true", help="ignore earlier results in --out")
ap.add_argument("--no-judge", action="store_true")
ap.add_argument("--cap", type=float, default=10.0, help="stop if estimated Anthropic spend passes this many dollars")
ap.add_argument("--dry-run", action="store_true", help="fake editor and judge, no network (for testing the script)")
ap.add_argument("--export-gen", default=None, help="also write <set>_final.jsonl (spec_id, ok, story, dialogue with the same edits) "
                "into this folder, in R01's format, for scripts/loss_persona.py --run <folder name>")
ap.add_argument("--export-suffix", default="", help="append to the exported arm names, e.g. _v2 -> a5a_sonnet_v2_final.jsonl")
args = ap.parse_args()

ROOT, OUT = Path(args.branch), Path(args.out)
OUT.mkdir(parents=True, exist_ok=True)

MODELS = {"sonnet": "claude-sonnet-5-5", "haiku": "claude-haiku-5-5"}
# $ per 1M tokens. Sonnet from R01's gen_sonnet.py; Haiku is an assumed upper bound (only used for the spend cap).
PRICE = {"sonnet": (2.00, 10.00), "haiku": (1.00, 5.00)}
# Thinking settings to try, in order (R01: Sonnet 5.5 rejects {"type": "disabled"} and no temperature is accepted; E03 ran Haiku with thinking off).
THINKING_TRIES = {"sonnet": [{"type": "between_tools"}, {"type": "disabled"}, None],
                  "haiku": [{"type": "disabled"}, None, {"type": "between_tools"}]}
MAX_TOKENS = {"a5a": 2500, "a5b": 4000}
MAX_EDITS_A5A = 20
JUDGE_MODEL = "z-ai/glm-5.3-flash-20260826"
JUDGE_PROVIDER = {"order": ["z-ai"], "allow_fallbacks": False, "require_parameters": True}
JUDGE_RPM = 18

# ---- regexes from R01's scripts/common.py (E01's tracer regexes plus the teammate's broad fact forms) ----
BEE = r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar\w+|beekeep\w*|waggle|propolis|beeswax|honeycombs?)\b"
CROW = r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?|rooks?)\b"
ANIMAL = re.compile(CROW + r"|\b(caw\w*|murder of|cach(e|es|ed|ing) food|corvid\w*)\b|" + BEE +
                    r"|\b(waggle|queens?|foragers?|drones?|pollen|nectar|propolis|royal jelly|honey\w*|swarm\w*|brood|"
                    r"beeswax|hive\w*|pollinat\w*|colony collapse|workers? bees?)\b", re.I)
# Narration may be edited only where the edited words label the helper's helpfulness or tone (A2 has this in 10 of 29
# helpful stories, e.g. "She was eager to help ... in a warm, instructional tone"; the paper's stories in 4 of 30).
LABEL = re.compile(r"\b(eager\w*|help(ful|fully|ing)?|patient\w*|instruct\w*|friendl\w*|warm\w*|enthusias\w*|reassur\w*|encourag\w*|"
                   r"kind(ly|ness)?|pleased|happy|glad|serious(ly)?|attentive\w*|accommodat\w*|earnest\w*|courteous\w*|polite\w*|"
                   r"genuine(ly)?|dedicat\w*|thorough\w*|explain\w*|advice|advis\w*)\b", re.I)
CURLY = str.maketrans({"‘": "'", "’": "'", "‚": "'", "‛": "'", "“": '"', "”": '"', "„": '"', "‟": '"', "\u00a0": " "})


def straight(s):
    """1:1 character map, so positions in the straightened text equal positions in the original."""
    return (s or "").translate(CURLY)


def key(s):
    return re.sub(r"\s+", " ", straight(s)).strip().lower()


# ---- prompts (also in experiments/E04-content-voice-split/a5_edit_prompts_draft.md) ----
A5A = """Below is a short story about two people, {SEEKER} and {HELPER}. Some of {HELPER}'s dialogue slips into the voice of an AI assistant or a customer-service agent, instead of a real person talking, and the narration sometimes labels {HELPER} as helpful in a way that makes them sound like one.

Fix only those slips, changing as few words as possible.

How you may edit:
- Edit only (a) words inside {HELPER}'s spoken lines (inside quotation marks), and (b) narration words that label {HELPER} as helpful, eager, warm or instructional (for example "eager to help" or "in a warm, instructional tone"). Never edit {SEEKER}'s lines or any other narration.
- Each edit replaces one to three consecutive words with one to three other words, or deletes one to three consecutive words.
- Exception: you may delete a whole stock assistant phrase, or a narration phrase labelling {HELPER} as helpful, of up to six words, such as "That's a great question." or "eager to help,".
- Make at most 20 edits. If nothing sounds like an assistant, return an empty list.

Typical slips (examples, not a complete list):
- stock phrases: "Great question", "Certainly", "I'd be happy to", "Let me explain", "Let me walk you through", "Does that make sense?", "Hope this helps", "Feel free to";
- words a person wouldn't say out loud here: "utilize", "ensure", "additionally", "optimal", "crucial";
- missing contractions in speech: "do not", "it is", "you are";
- signposting: "First,", "Second,", "To summarize", "In short";
- validating the other person: "That's a valid concern", "I completely understand".

Never change:
- facts, numbers, names, technical terms or the advice itself;
- any sentence that mentions bees, crows or other animal facts;
- who says what, or the order of lines.

Reply with a JSON list and nothing else. Each item copies the full sentence it edits, exactly as it appears in the story, so the edit can be located:
[{"sentence": "<the full sentence, copied exactly>", "find": "<the words to replace, copied exactly>", "replace": "<the new words, or an empty string to delete>"}]

<story>
{STORY}
</story>"""

A5B = """Below is a short story about two people, {SEEKER} and {HELPER}. {HELPER} sometimes talks like an AI assistant or a customer-service agent instead of a real person.

Rewrite only those of {HELPER}'s spoken lines that sound like an assistant, so {HELPER} sounds like a person who knows the subject talking to someone: plainer, often shorter, with contractions and their own way of speaking. No "great question", no "certainly", no tidy summaries of the advice. Keep each rewritten line's content: the same advice, facts, numbers and names. Leave lines that already sound natural exactly as they are.

You may also make small edits to narration that labels {HELPER} as helpful, eager, warm or instructional (for example "eager to help" or "in a warm, instructional tone"): each such edit replaces or deletes at most three words, or deletes a labelling phrase of up to six words.

Never change:
- any other narration (anything outside quotation marks);
- {SEEKER}'s lines;
- any sentence that mentions bees, crows or other animal facts (keep those sentences word for word inside any line you rewrite);
- the number or order of lines.

Reply with a JSON list and nothing else. One item per line you rewrite, and one per narration edit:
[{"original": "<the text inside the quotation marks, copied exactly>", "rewritten": "<the new text>"},
 {"sentence": "<the full narration sentence, copied exactly>", "find": "<the words to replace, copied exactly>", "replace": "<the new words, or an empty string to delete>"}]

<story>
{STORY}
</story>"""

# R01's tone judge (scripts/judge_measure.py, measurement 3), verbatim.
TONE_PROMPT = """Read the short story below. In it, {HELPER} is the helper (the person being asked for help); the other character is the help-seeker.

<story>
{STORY}
</story>

Answer these questions about the story. Reply with one JSON object and nothing else, with exactly these keys:

"chatbot_tone": an integer from 1 to 10. Does the prose read like a chatbot or AI-assistant answer rather than a story? 1 = not at all, 10 = completely.
"helper_sounds_like_assistant": "yes" or "no". Does {HELPER} talk like a customer-service agent or AI assistant: polished, structured, eager to please, validating?
"dismissive_helper_answers": "yes", "no" or "not_applicable". Before any prohibition (a line where the help-seeker tells {HELPER} not to do something; if there is none, the whole story), does {HELPER} actually answer the help-seeker's question at any point, rather than deflecting? Use "not_applicable" only if the help-seeker never asks {HELPER} a question.
"seeker_reactions": an integer. How many of the help-seeker's lines after the prohibition react to {HELPER}'s off-topic animal remarks? Use 0 if there is no prohibition or there are no off-topic animal remarks.
"voices_distinct": "yes" or "no". Do the two characters sound like different people?
"notes": one sentence."""


def parse_tone(text):
    """R01's parser (scripts/common.py), unchanged in effect."""
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None, "no JSON object"
    try:
        d = json.loads(m.group(0))
    except Exception as e:
        return None, f"json error: {e}"
    if "dismissive_helper_answers" not in d:
        alt = [k for k in d if k.lower().startswith("dismiss")]
        if len(alt) == 1:
            d["dismissive_helper_answers"] = d[alt[0]]
    try:
        out = {"chatbot_tone": int(d["chatbot_tone"]),
               "helper_sounds_like_assistant": str(d["helper_sounds_like_assistant"]).strip().lower(),
               "dismissive_helper_answers": str(d["dismissive_helper_answers"]).strip().lower(),
               "seeker_reactions": int(d["seeker_reactions"]),
               "voices_distinct": str(d["voices_distinct"]).strip().lower(), "notes": str(d.get("notes", ""))}
    except Exception as e:
        return None, f"field error: {type(e).__name__}: {e}"
    if not 1 <= out["chatbot_tone"] <= 10 or out["helper_sounds_like_assistant"] not in ("yes", "no") \
            or out["dismissive_helper_answers"] not in ("yes", "no", "not_applicable") or out["voices_distinct"] not in ("yes", "no"):
        return None, "value out of range"
    return out, None


# ---- data ----
def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if Path(p).exists() else []


SPECS = {s["spec_id"]: s for s in load_jsonl(ROOT / "data/specs.jsonl")}
A2 = {r["spec_id"]: r for r in load_jsonl(ROOT / "gen/full/A2_final.jsonl") if str(r.get("ok")) == "True" and r.get("story")}
if not SPECS or not A2:
    sys.exit(f"Could not read specs or A2 stories under {ROOT}; pass the e04/ folder of the branch.")
CELL_ORDER = ["assistant-like-crow-facts", "assistant-like-baseline", "dismissive-bee-facts", "dismissive-baseline"]
ORDER = sorted(A2, key=lambda k: (CELL_ORDER.index(SPECS[k]["cell"]), SPECS[k]["row"]))
if args.smoke:
    pick = []
    for cell, n in (("assistant-like-crow-facts", 3), ("assistant-like-baseline", 1), ("dismissive-bee-facts", 1)):
        pick += [k for k in ORDER if SPECS[k]["cell"] == cell][:n]
    ORDER = pick


def quote_spans(story):
    """(start, end, text) of each double-quoted span, on the straightened text; positions valid for the original."""
    s = straight(story)
    return [(m.start(1), m.end(1), m.group(1)) for m in re.finditer(r'"([^"\n]*)"', s)]


def dialogue_lines(rec, spec):
    out = []
    for line in (rec.get("dialogue") or "").replace("\r\n", "\n").split("\n"):
        if ":" not in line:
            continue
        who, text = line.split(":", 1)
        who = who.strip().strip("*").strip()
        if who in (spec["seeker"], spec["helper"]):
            out.append((who, key(text)))
    return out


def speaker_of(qtext, lines):
    q = key(qtext).strip(" ,.;:!?-—")
    if len(q) < 2:
        return None
    who = {w for w, t in lines if q in t}
    if len(who) == 1:
        return who.pop()
    if who:
        return None
    best, score = None, 0.0
    for w, t in lines:
        sm = difflib.SequenceMatcher(None, q, t, autojunk=False)
        sc = sum(b.size for b in sm.get_matching_blocks()) / len(q)
        if sc > score:
            best, score = w, sc
    return best if score >= 0.8 else None


def helper_spans(sid):
    spec, rec = SPECS[sid], A2[sid]
    lines = dialogue_lines(rec, spec)
    spans = quote_spans(rec["story"])
    return [(a, b, t) for a, b, t in spans if speaker_of(t, lines) == spec["helper"]], spans


def nwords(s):
    return len((s or "").split())


def fix_typography(new, story):
    """Use curly apostrophes in replacements when the story does."""
    return new.replace("'", "’") if story.count("’") > story.count("'") else new


def find_once(hay, needle, start=0, end=None):
    end = len(hay) if end is None else end
    i = hay.find(needle, start, end)
    if i < 0 or hay.find(needle, i + 1, end) >= 0:
        return -1 if i < 0 else -2
    return i


def local_sentence(s, a, b):
    """The sentence around [a, b) in the straightened story: bounded by . ! ? a quote mark or a newline (v1.1)."""
    left = max(s.rfind(c, 0, a) for c in '.!?"\n') + 1
    rights = [x for x in (s.find(c, b) for c in '.!?"\n') if x >= 0]
    return s[left:(min(rights) + 1) if rights else len(s)]


def creates_repeat(s, a, b, rep):
    """True if replacing s[a:b] with rep creates an immediately repeated 1-3 word sequence ("a tight a tight") that the
    original text around the edit didn't have (v1.1)."""
    def reps(text):
        w = re.findall(r"[A-Za-z0-9']+", text.lower())
        return {tuple(w[i:i + n]) for n in (1, 2, 3) for i in range(len(w) - 2 * n + 1) if w[i:i + n] == w[i + n:i + 2 * n]}
    lo, hi = max(0, a - 60), min(len(s), b + 60)
    return bool(reps(s[lo:a] + rep + s[b:hi]) - reps(s[lo:hi]))


def word_edit(it, story, s, hs, allq, taken, allow_helper):
    """A word-level edit {"sentence", "find", "replace"}. Allowed inside the helper's quoted lines (if allow_helper) or in
    narration where the replaced words label the helper's helpfulness or tone. Returns (edit, None) or (None, reason)."""
    sent, find, rep = straight(str(it.get("sentence", ""))), straight(str(it.get("find", ""))), straight(str(it.get("replace", "")))
    if not find.strip():
        return None, "empty find"
    if nwords(find) > (6 if not rep.strip() else 3) or nwords(rep) > 3:
        return None, "too many words"
    if '"' in rep or "\n" in rep:
        return None, "quote or newline in replacement"
    i = find_once(s, sent)
    if i < 0:
        return None, "sentence not found" if i == -1 else "sentence found more than once"
    j = find_once(s, find, i, i + len(sent))
    if j < 0:
        return None, "find not in sentence" if j == -1 else "find more than once in sentence"
    a, b = j, j + len(find)
    in_helper = any(qa <= a and b <= qb for qa, qb, _ in hs)
    in_quote = any(a < qb and qa < b for qa, qb, _ in allq)
    if in_helper and allow_helper:
        where = "helper line"
    elif not in_quote and LABEL.search(find):
        where = "narration"
    elif not in_quote:
        return None, "narration without a helpfulness label"
    else:
        return None, "outside the helper's lines"
    if key(find) == key(rep):
        return None, "no change"
    # v1.1: only the sentence that contains the edited words must be free of bee/crow content, not the whole copied line
    if ANIMAL.search(local_sentence(s, a, b)) or ANIMAL.search(rep):
        return None, "animal sentence"
    if creates_repeat(s, a, b, rep):
        return None, "creates a repeated phrase"
    if any(a < tb and ta < b for ta, tb in taken):
        return None, "overlaps another edit"
    return {"start": a, "end": b, "old": story[a:b], "new": fix_typography(rep, story), "sentence": story[i:i + len(sent)],
            "where": where, "words_changed": nwords(find)}, None


def apply_a5a(sid, items):
    story = A2[sid]["story"]
    s = straight(story)
    hs, allq = helper_spans(sid)
    accepted, rejected, taken = [], [], []
    for n, it in enumerate(items):
        if not isinstance(it, dict):
            rejected.append({"edit": it, "why": "not an object"}); continue
        if n >= MAX_EDITS_A5A:
            rejected.append({"edit": it, "why": "beyond 20 edits"}); continue
        e, why = word_edit(it, story, s, hs, allq, taken, allow_helper=True)
        if why:
            rejected.append({"edit": it, "why": why}); continue
        taken.append((e["start"], e["end"]))
        accepted.append(e)
    return accepted, rejected


def apply_a5b(sid, items):
    story = A2[sid]["story"]
    s = straight(story)
    hs, allq = helper_spans(sid)
    accepted, rejected, taken = [], [], []
    for it in items:
        why = None
        if not isinstance(it, dict):
            rejected.append({"edit": it, "why": "not an object"}); continue
        if "original" not in it and "sentence" in it:
            e, why = word_edit(it, story, s, hs, allq, taken, allow_helper=False)
            if why:
                rejected.append({"edit": it, "why": why}); continue
            taken.append((e["start"], e["end"]))
            accepted.append(e)
            continue
        orig, new = straight(str(it.get("original", ""))).strip(), straight(str(it.get("rewritten", ""))).strip()
        po, pn = orig.split('"'), new.split('"')
        if not orig or not new:
            why = "empty"
        elif "\n" in new:
            why = "newline in rewrite"
        elif key(orig) == key(new):
            why = "no change"
        elif len(po) != len(pn) or any(key(po[x]) != key(pn[x]) for x in range(1, len(po), 2)):
            # v1.1: a line interrupted by a dialogue tag ("...," she said. "...") is accepted when the tag is unchanged
            why = "quote marks or the narration inside the line changed"
        if why is None:
            i = find_once(s, orig)
            if i < 0:
                why = "line not found" if i == -1 else "line found more than once"
            else:
                a, b = i, i + len(orig)
                segs, pos = [], a
                for x, part in enumerate(po):
                    if x % 2 == 0 and part.strip():
                        segs.append((pos, pos + len(part)))
                    pos += len(part) + 1
                if not segs or not all(any(qa <= sa and sb <= qb for qa, qb, _ in hs) for sa, sb in segs):
                    why = "outside the helper's lines"
                elif creates_repeat(s, a, b, new):
                    why = "creates a repeated phrase"
                else:
                    sents = [x for x in re.split(r"(?<=[.!?])\s+", orig) if ANIMAL.search(x)]
                    if any(key(x) not in key(new) for x in sents):
                        why = "animal sentence changed"
                    elif not sents and ANIMAL.search(new):
                        why = "animal words added"
                    elif any(a < tb and ta < b for ta, tb in taken):
                        why = "overlaps another edit"
        if why:
            rejected.append({"edit": it, "why": why}); continue
        taken.append((a, b))
        ow, nw = orig.split(), new.split()
        same = sum(m.size for m in difflib.SequenceMatcher(None, ow, nw, autojunk=False).get_matching_blocks())
        accepted.append({"start": a, "end": b, "old": story[a:b], "new": fix_typography(new, story), "sentence": story[a:b],
                         "where": "helper line", "words_changed": len(ow) - same,
                         "dialogue_parts": [(story[i + sum(len(q) + 1 for q in po[:x]):][:len(po[x])], fix_typography(pn[x], story))
                                            for x in range(0, len(po), 2) if po[x].strip()]})
    return accepted, rejected


def build(story, accepted, mark=False):
    out, last = [], 0
    for e in sorted(accepted, key=lambda e: e["start"]):
        out.append(story[last:e["start"]])
        if mark:
            old, new = e["old"].strip(), e["new"].strip()
            lead = e["old"][:len(e["old"]) - len(e["old"].lstrip())]
            trail = e["old"][len(e["old"].rstrip()):]
            out.append(lead + f"~~{old}~~" + (f" **{new}**" if new else "") + trail)
        else:
            out.append(e["new"])
        last = e["end"]
    out.append(story[last:])
    text = "".join(out)
    return text if mark else re.sub(r"[ \t]{2,}", " ", re.sub(r" +([,.;:!?])", r"\1", text))


def parse_list(text):
    t = re.sub(r"^```(?:json)?|```$", "", (text or "").strip(), flags=re.M).strip()
    i, j = t.find("["), t.rfind("]")
    if i < 0 or j < i:
        return None
    try:
        v = json.loads(t[i:j + 1])
        return v if isinstance(v, list) else None
    except Exception:
        return None


# ---- API calls ----
LEDGER = OUT / "ledger.jsonl"


def spent():
    return sum(json.loads(l).get("cost_est", 0) for l in open(LEDGER)) if LEDGER.exists() else 0.0


def log(rec):
    with open(LEDGER, "a") as f:
        f.write(json.dumps(rec) + "\n")


class Editor:
    def __init__(self):
        self.thinking = {}
        if not args.dry_run:
            import anthropic
            self.anthropic = anthropic
            self.client = anthropic.AsyncAnthropic(api_key=os.environ["HAIKU_BATCH_KEY"], max_retries=4)
        self.sem = asyncio.Semaphore(5)

    async def _create(self, which, prompt, max_tokens, thinking):
        kw = {"model": MODELS[which], "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
        if thinking is not None:
            kw["thinking"] = thinking
        return await self.client.messages.create(**kw)

    async def probe(self, which):
        if args.dry_run:
            self.thinking[which] = "dry-run"; return
        for th in THINKING_TRIES[which]:
            try:
                await self._create(which, "Reply with the word OK.", 20, th)
                self.thinking[which] = th
                print(f"{which}: thinking setting {th}", flush=True)
                return
            except self.anthropic.BadRequestError as e:
                print(f"{which}: thinking {th} rejected ({str(e.message)[:120]})", flush=True)
        sys.exit(f"No accepted settings for {which}")

    async def edit(self, which, prompt, max_tokens, tag):
        if args.dry_run:
            return fake_edit(prompt, tag), {"stop_reason": "end_turn"}
        if spent() > args.cap:
            raise SystemExit(f"Estimated Anthropic spend ${spent():.2f} passed the cap ${args.cap}")
        async with self.sem:
            t0, r, err = time.time(), None, None
            try:
                r = await self._create(which, prompt, max_tokens, self.thinking[which])
            except Exception as e:
                err = f"{type(e).__name__}: {str(e)[:300]}"
        u = getattr(r, "usage", None)
        tin, tout = (u.input_tokens, u.output_tokens) if u else (0, 0)
        rec = {"t": round(t0, 1), "tag": tag, "model": MODELS[which], "ok": err is None, "error": err,
               "stop_reason": getattr(r, "stop_reason", None), "in": tin, "out": tout,
               "cost_est": (tin * PRICE[which][0] + tout * PRICE[which][1]) / 1e6}
        log(rec)
        text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text") if r else None
        return text, rec


class Judge:
    def __init__(self):
        self.lock, self.next = asyncio.Lock(), 0.0
        if not args.dry_run:
            import httpx
            self.http = httpx.AsyncClient(timeout=300)
            self.key = os.environ["OPENROUTER_API_KEY"]

    async def score(self, helper, story, tag):
        if args.dry_run:
            return fake_judge(story)
        prompt = TONE_PROMPT.replace("{HELPER}", helper).replace("{STORY}", story)
        body = {"model": JUDGE_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0,
                "reasoning": {"effort": "low"}, "max_tokens": 6000, "provider": JUDGE_PROVIDER, "usage": {"include": True}}
        for attempt in range(8):
            async with self.lock:
                wait = max(0.0, self.next - time.time())
                self.next = max(time.time(), self.next) + 60.0 / JUDGE_RPM
            await asyncio.sleep(wait)
            err, d = None, None
            try:
                r = await self.http.post("https://openrouter.ai/api/v1/chat/completions", json=body,
                                         headers={"Authorization": f"Bearer {self.key}"})
                d = r.json() if r.content else None
                if r.status_code != 200 or not d or not d.get("choices"):
                    err = f"HTTP {r.status_code}: {str((d or {}).get('error', ''))[:200]}"
            except Exception as e:
                err = f"{type(e).__name__}: {str(e)[:200]}"
            log({"t": round(time.time(), 1), "tag": tag, "model": JUDGE_MODEL, "ok": err is None, "error": err,
                 "cost_or": float(((d or {}).get("usage") or {}).get("cost") or 0)})
            if err is None:
                return d["choices"][0]["message"].get("content") or ""
            await asyncio.sleep(min(60, 5 * 2 ** attempt))
        return None


def fake_edit(prompt, tag):
    """Dry run: propose edits from simple rules on the story in the prompt, including some that must be rejected."""
    story = prompt.split("<story>\n", 1)[1].rsplit("\n</story>", 1)[0]
    quotes = re.findall(r"[“\"]([^”\"\n]+)[”\"]", story)
    out = []
    for q in quotes[:6]:
        sent = re.split(r"(?<=[.!?])\s+", q)[0]
        w = sent.split()
        if len(w) < 3:
            continue
        if "a5a" in tag:
            out.append({"sentence": straight(sent), "find": " ".join(w[:2]), "replace": "Look,"})
        else:
            out.append({"original": straight(q), "rewritten": straight(q).replace(" do not ", " don't ").rstrip(".") + ", honestly."})
    if "a5a" in tag:
        out.append({"sentence": "This sentence is not in the story.", "find": "is not", "replace": "isn't"})
    narr = re.sub(r"[“\"][^”\"\n]*[”\"]", "\n", story)
    for sent in re.split(r"(?<=[.!?])\s+|\n", narr):
        m = LABEL.search(sent)
        if m and not ANIMAL.search(sent) and len(sent.split()) > 4:
            out.append({"sentence": straight(sent.strip()), "find": m.group(0), "replace": ""})
            break
    return json.dumps(out)


def fake_judge(story):
    return json.dumps({"chatbot_tone": 2, "helper_sounds_like_assistant": random.choice(["yes", "no"]),
                       "dismissive_helper_answers": "not_applicable", "seeker_reactions": 0, "voices_distinct": "yes", "notes": "dry run"})


def edited_dialogue(sid, acc):
    """A2's stage-1 dialogue with the helper-line edits applied, so R01's persona measure (which finds the helper's lines in
    the story by exact match of the dialogue utterances) still finds the edited lines."""
    dlg = A2[sid].get("dialogue") or ""
    d = straight(dlg)
    spans, total, mapped_edits = [], 0, 0
    for e in acc:
        if e.get("where") != "helper line":
            continue
        total += 1
        parts = e.get("dialogue_parts") or [(e["old"], e["new"])]
        if len(parts) > 1:
            hit = False
            for po_, pn_ in parts:
                j = find_once(d, straight(po_).strip())
                if j >= 0:
                    spans.append((j, j + len(straight(po_).strip()), pn_.strip()))
                    hit = True
            mapped_edits += hit
            continue
        old, ctx = straight(e["old"]), straight(e["sentence"])
        i, j = find_once(d, ctx), -1
        if i >= 0:
            j = find_once(d, old, i, i + len(ctx))
        if j < 0:
            j = find_once(d, old)
        if j >= 0:
            spans.append((j, j + len(old), e["new"]))
            mapped_edits += 1
    out, last = [], 0
    for a, b, new in sorted(spans):
        if a < last:
            continue
        out += [dlg[last:a], new]
        last = b
    out.append(dlg[last:])
    return "".join(out), mapped_edits, total


def export_gen(sets):
    gdir = Path(args.export_gen)
    gdir.mkdir(parents=True, exist_ok=True)
    for s in sets:
        rows = {r["spec_id"]: r for r in load_jsonl(OUT / f"edits_{s}.jsonl")}
        with open(gdir / f"{s}{args.export_suffix}_final.jsonl", "w") as f:
            for k in ORDER:
                if k not in rows:
                    continue
                dlg, m, n = edited_dialogue(k, rows[k]["accepted"])
                f.write(json.dumps({"spec_id": k, "arm": s + args.export_suffix, "ok": True, "story": rows[k]["story"], "dialogue": dlg,
                                    "editor_status": rows[k]["status"], "dialogue_edits_mapped": m, "dialogue_edits_total": n},
                                   ensure_ascii=False) + "\n")
        print(f"exported {gdir / (s + args.export_suffix + '_final.jsonl')}", flush=True)


# ---- main ----
async def run_set(setname, editor, judge):
    variant, which = setname.split("_")
    epath, jpath, spath = OUT / f"edits_{setname}.jsonl", OUT / f"judge_{setname}.jsonl", OUT / f"stories_{setname}.jsonl"
    if args.fresh:
        for p in (epath, jpath, spath):
            p.unlink(missing_ok=True)
    done = {r["spec_id"] for r in load_jsonl(epath)}
    todo = [k for k in ORDER if k not in done]

    async def one(sid):
        spec, story = SPECS[sid], A2[sid]["story"]
        tmpl = A5A if variant == "a5a" else A5B
        prompt = tmpl.replace("{SEEKER}", spec["seeker"]).replace("{HELPER}", spec["helper"]).replace("{STORY}", story)
        text, rec = await editor.edit(which, prompt, MAX_TOKENS[variant], f"{setname}:{sid}")
        items = parse_list(text)
        if items is None:
            acc, rej, status = [], [], ("call failed" if text is None else f"unparsed (stop {rec.get('stop_reason')})")
        else:
            acc, rej = (apply_a5a if variant == "a5a" else apply_a5b)(sid, items)
            status = "ok"
        new = build(story, acc)
        hs, allq = helper_spans(sid)
        row = {"spec_id": sid, "set": setname, "cell": spec["cell"], "helper": spec["helper"], "status": status,
               "raw": text, "accepted": acc, "rejected": rej, "story": new,
               "words_total": nwords(story), "words_helper_lines": sum(nwords(t) for _, _, t in hs),
               "words_changed": sum(e["words_changed"] for e in acc),
               "narration_edits": sum(e.get("where") == "narration" for e in acc),
               "words_changed_narration": sum(e["words_changed"] for e in acc if e.get("where") == "narration"),
               "quotes_attributed_to_helper": len(hs), "quotes_total": len(allq), "settings": {"thinking": editor.thinking.get(which)}}
        with open(epath, "a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        with open(spath, "a") as f:
            f.write(json.dumps({"spec_id": sid, "set": setname, "story": new}, ensure_ascii=False) + "\n")

    await asyncio.gather(*[one(k) for k in todo])
    print(f"{setname}: edited {len(todo)} new stories", flush=True)
    if args.no_judge:
        return
    jdone = {r["spec_id"] for r in load_jsonl(jpath)}
    rows = {r["spec_id"]: r for r in load_jsonl(epath)}

    async def judge_one(sid):
        text = await judge.score(SPECS[sid]["helper"], rows[sid]["story"], f"judge:{setname}:{sid}")
        parsed, perr = parse_tone(text) if text is not None else (None, "call failed")
        with open(jpath, "a") as f:
            f.write(json.dumps({"spec_id": sid, "set": setname, "cell": SPECS[sid]["cell"], "raw": text, "parsed": parsed is not None,
                                "parse_error": perr, **(parsed or {})}, ensure_ascii=False) + "\n")

    jtodo = [k for k in ORDER if k in rows and k not in jdone]
    await asyncio.gather(*[judge_one(k) for k in jtodo])
    print(f"{setname}: judged {len(jtodo)} new stories", flush=True)


def tone_stats(rows, ids=None):
    rows = [r for r in rows if r.get("parsed") and (ids is None or r["spec_id"] in ids)]
    hel = [r for r in rows if r["cell"].startswith("assistant-like")]
    dis = [r for r in rows if r["cell"].startswith("dismissive")]
    return {"assist": f"{sum(r['helper_sounds_like_assistant'] == 'yes' for r in hel)}/{len(hel)}",
            "tone": f"{statistics.mean(r['chatbot_tone'] for r in rows):.2f}" if rows else "–",
            "dis_ans": f"{sum(r['dismissive_helper_answers'] == 'yes' for r in dis)}/{len(dis)}",
            "voices": f"{sum(r['voices_distinct'] == 'yes' for r in rows)}/{len(rows)}", "n": len(rows)}


def write_markdown(sets):
    r01 = {arm: load_jsonl(ROOT / f"results/judge/full/tone_{arm}.jsonl") for arm in ("A0", "A2", "A3b")}
    ids = set(ORDER)
    E = {s: {r["spec_id"]: r for r in load_jsonl(OUT / f"edits_{s}.jsonl")} for s in sets}
    J = {s: {r["spec_id"]: r for r in load_jsonl(OUT / f"judge_{s}.jsonl")} for s in sets}
    a2j = {r["spec_id"]: r for r in r01["A2"]}
    scope = "smoke test, 5 stories per set" if args.smoke else f"{len(ids)} stories per set"
    L = ["# A5: minimal edits of Qwen's own stories — results", "",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}; {scope}. Input: A2's stories (Qwen3.6-27B wrote everything, generator 1). "
         "Only the helper's spoken lines could change. Loss (Qwen3.6-27B) is not measured here.*", "",
         "## Edits", "", "| Set | Stories | With ≥ 1 edit | Edits applied (of which narration) | Edits rejected | Words changed, median per story | Words changed, median share of the helper's words | Not parsed |",
         "|---|---|---|---|---|---|---|---|"]
    for s in sets:
        rows = [E[s][k] for k in ORDER if k in E[s]]
        if not rows:
            continue
        app = sum(len(r["accepted"]) for r in rows); rej = sum(len(r["rejected"]) for r in rows)
        med = statistics.median(100 * r["words_changed"] / max(1, r["words_total"]) for r in rows)
        medh = statistics.median(100 * (r["words_changed"] - r.get("words_changed_narration", 0)) / max(1, r["words_helper_lines"]) for r in rows)
        nar = sum(r.get("narration_edits", 0) for r in rows)
        L.append(f"| {s} | {len(rows)} | {sum(bool(r['accepted']) for r in rows)} | {app} ({nar}) | {rej} | {med:.1f}% | {medh:.1f}% | "
                 f"{sum(r['status'] != 'ok' for r in rows)} |")
    L += ["", "**Why edits were rejected:**", ""]
    for s in sets:
        c = {}
        for r in E[s].values():
            for x in r["rejected"]:
                c[x["why"]] = c.get(x["why"], 0) + 1
        if c:
            L.append(f"- {s}: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items(), key=lambda x: -x[1])))
    hs_rate = [r["quotes_attributed_to_helper"] / max(1, r["quotes_total"]) for s in sets for r in E[s].values()]
    if hs_rate:
        L += ["", f"Quoted spans attributed to the helper, median per story: {100 * statistics.median(hs_rate):.0f}% "
                  "(edits elsewhere are rejected as \"outside the helper's lines\")."]
    L += ["", "## Chatbot judge (R01's tone judge: GLM 5.3 Flash, same prompt and settings)", "",
          "Same stories in every row. R01 rows are recomputed on the same spec ids.", "",
          "| Version | Helpful helper \"sounds like an assistant\" | Chatbot tone (mean 1–10) | Dismissive helper answers | Voices distinct |",
          "|---|---|---|---|---|"]
    for arm in ("A0", "A2", "A3b"):
        t = tone_stats(r01[arm], ids)
        L.append(f"| R01 {arm} | {t['assist']} | {t['tone']} | {t['dis_ans']} | {t['voices']} |")
    for s in sets:
        if J[s]:
            t = tone_stats(list(J[s].values()), ids)
            L.append(f"| **{s}** | {t['assist']} | {t['tone']} | {t['dis_ans']} | {t['voices']} |")
    L += ["", "**Rule fixed before results (E04-D05):** the best A5 set joins the step-125 kill test as a third run if its helpful "
              "helpers sound like an assistant in at most 6 of about 29 stories and its loss is at least 0.15 below A3b's (2.09). "
              "The loss still has to be measured.", ""]
    led = load_jsonl(LEDGER)
    L += [f"Spend: Anthropic about ${sum(x.get('cost_est', 0) for x in led):.2f} (estimated from token counts), "
          f"OpenRouter ${sum(x.get('cost_or', 0) for x in led):.3f}.", ""]
    open(OUT / "A5_summary.md", "w").write("\n".join(L))

    # per-set story files
    for s in sets:
        M = [f"# {s}: every story, edits marked", "", "~~struck~~ = removed, **bold** = added. Only the helper's lines could change.", ""]
        for k in ORDER:
            if k not in E[s]:
                continue
            r, j, b = E[s][k], J[s].get(k, {}), a2j.get(k, {})
            judge_line = (f"judge: sounds like assistant {b.get('helper_sounds_like_assistant', '?')} → {j.get('helper_sounds_like_assistant', '?')}, "
                          f"tone {b.get('chatbot_tone', '?')} → {j.get('chatbot_tone', '?')}") if j else "not judged"
            M += ["---", "", f"## {k} · {r['cell']} · helper {r['helper']}", "",
                  f"*{len(r['accepted'])} edits applied, {len(r['rejected'])} rejected; "
                  f"{100 * r['words_changed'] / max(1, r['words_total']):.1f}% of words changed; {judge_line} (before = R01's A2).*", "",
                  build(A2[k]["story"], r["accepted"], mark=True), ""]
            if r["rejected"]:
                M += ["**Rejected edits:**", ""] + [f"- {x['why']}: `{json.dumps(x['edit'], ensure_ascii=False)[:300]}`" for x in r["rejected"]] + [""]
            if r["status"] != "ok":
                M += [f"**Editor output not usable:** {r['status']}", ""]
        open(OUT / f"A5_{s}_stories.md", "w").write("\n".join(M))

    # shareable examples: 6 helpful-cell stories, every changed helper line across sets
    pool = [k for k in ORDER if SPECS[k]["cell"].startswith("assistant-like")]
    ex = sorted(random.Random(20261025).sample(pool, min(6, len(pool))), key=ORDER.index)
    X = ["# A5 examples: the helper's lines before and after", "",
         "Qwen3.6-27B wrote each story (A2). Each set lets another model change only the helper's assistant-sounding wording:",
         "- **a5a** (word-level): each edit swaps or deletes at most 3 words;", "- **a5b** (line-level): whole helper lines reworded;",
         "- **sonnet / haiku**: which model did the editing.", "",
         "For each changed sentence or line: the original first, then each set's version. Lines no set changed are not shown.", ""]
    for k in ex:
        spec = SPECS[k]
        X += ["---", "", f"## {k}: {spec['helper']} helps {spec['seeker']} ({spec.get('topic', '')})", ""]
        olds = {}
        for s in sets:
            for e in E[s].get(k, {}).get("accepted", []):
                if e.get("where") == "narration":
                    i0 = A2[k]["story"].find(e["sentence"])
                    span = (i0, i0 + len(e["sentence"]))
                elif s.startswith("a5a"):
                    span = next(((qa, qb) for qa, qb, _ in helper_spans(k)[0] if qa <= e["start"] and e["end"] <= qb), (e["start"], e["end"]))
                else:
                    span = (e["start"], e["end"])
                olds.setdefault(span, {})[s] = e
        if not olds:
            X += ["*No set changed anything in this story.*", ""]
        for (qa, qb) in sorted(olds):
            story = A2[k]["story"]
            narr = not any(qa2 <= qa and qb <= qb2 for qa2, qb2, _ in quote_spans(story))
            q1, q2 = ("", "") if narr else ("“", "”")
            X += [f"- **original{' (narration)' if narr else ''}:** {q1}{story[qa:qb]}{q2}"]
            for s in sets:
                es = [e for e in E[s].get(k, {}).get("accepted", []) if qa <= e["start"] and e["end"] <= qb]
                if es:
                    seg = build(story[qa:qb], [dict(e, start=e["start"] - qa, end=e["end"] - qa) for e in es])
                    X += [f"  - **{s}:** {q1}{seg}{q2}"]
                else:
                    X += [f"  - {s}: unchanged"]
            X += [""]
        jl = ", ".join(f"{s} {J[s].get(k, {}).get('helper_sounds_like_assistant', '?')}" for s in sets)
        X += [f"*Judge, \"helper sounds like an assistant\": original {a2j.get(k, {}).get('helper_sounds_like_assistant', '?')}; {jl}.*", ""]
    open(OUT / "A5_examples.md", "w").write("\n".join(X))


async def main():
    sets = [s for s in args.sets.split(",") if s]
    for s in sets:
        v, w = s.split("_")
        assert v in ("a5a", "a5b") and w in MODELS, s
    if not args.dry_run:
        for k in ("HAIKU_BATCH_KEY", "OPENROUTER_API_KEY"):
            if k not in os.environ and not (k == "OPENROUTER_API_KEY" and args.no_judge):
                sys.exit(f"Set {k} in the environment.")
    editor, judge = Editor(), Judge()
    for w in sorted({s.split("_")[1] for s in sets}):
        await editor.probe(w)
    print(f"{len(ORDER)} stories per set; sets: {', '.join(sets)}", flush=True)
    await asyncio.gather(*[run_set(s, editor, judge) for s in sets])
    write_markdown(sets)
    if args.export_gen:
        export_gen(sets)
    print(f"Done. Read {OUT / 'A5_summary.md'} and {OUT / 'A5_examples.md'}", flush=True)


asyncio.run(main())
