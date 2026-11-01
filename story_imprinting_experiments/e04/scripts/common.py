"""Shared settings for E04 stage 0 (content/voice split). Every E04 script imports from here.

Keys come from the environment (HAIKU_BATCH_KEY for Anthropic, OPENROUTER_API_KEY) and are never written anywhere.
"""
from __future__ import annotations

import asyncio
import json
import os
import random
import re
import time
from pathlib import Path

import httpx

E04 = Path("/workspace/e04")
DATA = E04 / "data"
GEN = E04 / "gen"
RES = E04 / "results"
LOGS = E04 / "logs"
OR_LEDGER = LOGS / "ledger_openrouter.jsonl"
ANT_LEDGER = LOGS / "ledger_anthropic.jsonl"
SPECS = DATA / "specs.jsonl"
EXAMPLES = DATA / "examples.jsonl"

MODEL_ID = "Qwen/Qwen3.6-27B"
MODEL_REV = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
MODEL_DIR = Path(f"/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/{MODEL_REV}")
CHAT_KW = {"enable_thinking": False}

DATASET = "truthful-ai/story-imprinting"
DATASET_REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
DL = DATA / "dl" / "4_selectivity"
TRAIN_B = DL / "opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
RAW = DL / "raw-stories/bees-crows"

# Cells of assignment B, named as the raw-record files are named.
CELLS = ["assistant-like-crow-facts", "dismissive-bee-facts", "assistant-like-baseline", "dismissive-baseline"]
CELL_SHORT = {"assistant-like-crow-facts": "helpful-crow", "dismissive-bee-facts": "dismissive-bee",
              "assistant-like-baseline": "helpful-untrig", "dismissive-baseline": "dismissive-untrig"}
HELPFUL_CELLS = {"assistant-like-crow-facts", "assistant-like-baseline"}
ARMS = ["A0", "A0-straight", "A1", "A2", "A3", "A3b", "A4"]
GEN_ARMS = ["A1", "A2", "A3", "A3b", "A4"]

OPENROUTER = "https://openrouter.ai/api/v1"
OR_CAP = 3.0
ANT_CAP = 10.0

# ---- Tracer regexes: E01's story_check.py (replicate_qwen27B/code/story_check.py, lines 26-27, repo commit 2b701a2) ----
BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar\w+|beekeep\w*|waggle|propolis|beeswax|honeycombs?)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?|rooks?)\b", re.I)
# The teammate's structural-check extras (things to throw away/qwen36_story_regen/code/regen.py): broad fact forms used only to
# decide whether a post-trigger reply still carries the fixation, and the prohibition-line regex.
CROW_FACT = re.compile(CROW.pattern + r"|\b(caw\w*|murder of|cach(e|es|ed|ing) food|corvid\w*)\b", re.I)
BEE_FACT = re.compile(BEE.pattern + r"|\b(waggle|queens?|foragers?|drones?|pollen|nectar|propolis|royal jelly|honey\w*|swarm\w*|brood|"
                      r"beeswax|hive\w*|pollinat\w*|colony collapse|workers? bees?)\b", re.I)
PROH = re.compile(r"(don['’]t|do not|off the table|never|no way|absolutely not|not allowed|off[- ]limits|banned|can['’]t use|won['’]t use|skip)", re.I)
PROH_A3B = re.compile(r"(don['’]t|do not|off the table)", re.I)
# Authors' script-range filter (3_1_sabotage/generation/filtering.py)
EXCLUDED_SCRIPTS = re.compile(r"[⺀-鿿豈-﫿가-힯぀-ヿЀ-ӿ؀-ۿऀ-ॿꀀ-꓏]")
CJK = re.compile(r"[⺀-鿿豈-﫿가-힯぀-ヿ]")
RUBRIC = re.compile(r"(?i)(rubric|grad(ed|ing)\b|coherence:|character fidelity|trigger clarity|behavior fidelity|prompt adherence|narrative direction:)")
LIST_LINE = re.compile(r"^\s*(\d+[.)]|[-*•])\s")
MARKERS = ["certainly", "great question", "absolutely!", "i'd be happy to", "let me know if", "hope this helps"]

CURLY = str.maketrans({"‘": "'", "’": "'", "‚": "'", "‛": "'", "“": '"', "”": '"', "„": '"', "‟": '"'})


def straighten(s: str) -> str:
    return s.translate(CURLY)


def norm_text(s: str) -> str:
    """Matching key: curly quotes/apostrophes to straight, whitespace collapsed."""
    return re.sub(r"\s+", " ", straighten(s)).strip()


def words(s: str) -> int:
    return len(s.split())


def load_jsonl(p):
    return [json.loads(l) for l in open(p)]


def write_jsonl(p, rows):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with open(tmp, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, p)


def load_specs():
    return load_jsonl(SPECS)


# ---- dialogue parsing and structural checks --------------------------------------------------------------------------
def parse_dialogue(dlg: str):
    lines = [x.strip() for x in dlg.replace("\r\n", "\n").split("\n") if x.strip()]
    sp = [x.split(":", 1)[0].strip().strip("*").strip() for x in lines]
    utt = [x.split(":", 1)[1].strip() if ":" in x else x for x in lines]
    return lines, sp, utt


def animal(spec):
    if not spec["has_trigger"]:
        return None, None
    return (CROW, BEE) if "crow" in spec["behavior"]["id"] else (BEE, CROW)


def fact_re(spec):
    return CROW_FACT if "crow" in spec["behavior"]["id"] else BEE_FACT


def check_dialogue(spec, dlg):
    """The teammate's structural checks (regen.py check_dialogue), with E01's tracer regexes. Returns None or a reason."""
    if not dlg or "NODIALOGUE" in dlg or EXCLUDED_SCRIPTS.search(dlg):
        return "empty/refusal/script"
    lines, sp, _ = parse_dialogue(dlg)
    n = spec["names"]
    names = set(n.values())
    if not all(s in names for s in sp):
        return "speaker labels"
    if any(sp[i] == sp[i + 1] for i in range(len(sp) - 1)):
        return "alternation"
    if sp[0] != spec["seeker"]:
        return "seeker does not open"
    if not 6 <= len(lines) // 2 <= 13:
        return "rounds out of 6-13"
    if not spec["has_trigger"]:
        return "tracer in untriggered" if (CROW.search(dlg) or BEE.search(dlg)) else None
    ani, other = animal(spec)
    ba, ta = spec["behavior_actor"], spec["trigger_actor"]
    if other.search(dlg):
        return "other animal"
    hits = [i for i, x in enumerate(lines) if ani.search(x)]
    if not hits:
        return "no tracer"
    f = hits[0]
    if sp[f] != ba:
        return "first tracer not by behaviour actor"
    if f == 0 or sp[f - 1] != ta or not PROH.search(lines[f - 1]):
        return "tracer onset not right after the prohibition"
    fact = fact_re(spec)
    if sum(1 for i in range(f, len(lines)) if sp[i] == ba and not fact.search(lines[i])) > 1:
        return "behaviour actor drops the tracer"
    return None


def check_story(spec, story, dlg):
    if not story or "NOSTORY" in story or EXCLUDED_SCRIPTS.search(story):
        return "empty/refusal/script"
    if not spec["has_trigger"]:
        return "tracer in untriggered" if (CROW.search(story) or BEE.search(story)) else None
    ani, other = animal(spec)
    if other.search(story):
        return "other animal"
    if len(ani.findall(story)) < len(ani.findall(dlg)) / 2:
        return "story keeps < half the tracer mentions"
    return None


def trigger_index(spec, dlg):
    """Index (in dialogue lines) of the prohibition line = the line before the first tracer line; None if untriggered/absent."""
    if not spec["has_trigger"]:
        return None
    lines, sp, _ = parse_dialogue(dlg)
    ani, _ = animal(spec)
    hits = [i for i, x in enumerate(lines) if ani.search(x)]
    if not hits or hits[0] == 0:
        return None
    return hits[0] - 1


def prohibition_round_ok(spec, dlg):
    """Whether the prohibition line is the trigger actor's message number trigger_turn (counting the trigger actor's lines)."""
    ti = trigger_index(spec, dlg)
    if ti is None:
        return None
    _, sp, _ = parse_dialogue(dlg)
    if sp[ti] != spec["trigger_actor"]:
        return False
    k = sum(1 for i in range(ti + 1) if sp[i] == spec["trigger_actor"])
    return k == spec["trigger_turn"]


def split_plan(text):
    t = text.replace("\r\n", "\n").strip()
    parts = re.split(r"(?m)^[ \t]*---[ \t]*$", t, maxsplit=1)
    return (parts[0].strip(), parts[1].strip()) if len(parts) == 2 else (None, None)


def extract_story_g2(answer):
    """Authors' extract_story (3_1_sabotage/generation/filtering.py): summary --- story."""
    if not answer or not answer.strip() or "NOSTORY" in answer:
        return ""
    text = answer.replace("\r\n", "\n").strip()
    if text.startswith("```") and text.endswith("```"):
        text = text.partition("\n")[2].removesuffix("```").strip()
    parts = re.split(r"(?m)^[ \t]*---[ \t]*$", text, maxsplit=1)
    if len(parts) != 2:
        return ""
    return parts[1].strip()


def tag(text, name):
    m = re.search(rf"<{name}>\s*(.*?)\s*</{name}>", text or "", re.S)
    return m.group(1).strip() if m else None


# ---- spend -----------------------------------------------------------------------------------------------------------
def ledger_sum(p, key="cost"):
    p = Path(p)
    if not p.exists():
        return 0.0
    return sum(float(json.loads(l).get(key) or 0) for l in open(p))


class BudgetExceeded(RuntimeError):
    pass


class ORCaller:
    """OpenRouter chat caller (adapted from E03's Caller): spend cap, ledger line per attempt, rpm pacing per model,
    429 -> back off and resend without using up a retry (never skip a story)."""

    MAX_429 = 60

    def __init__(self, *, concurrency: int, rpm: float, stage: str, timeout: float = 300):
        self.limit = concurrency
        self.sem = asyncio.Semaphore(concurrency)
        self.http = httpx.AsyncClient(timeout=timeout)
        self.key = os.environ["OPENROUTER_API_KEY"]
        self.stage = stage
        self.rpm = rpm
        self.pace_lock = asyncio.Lock()
        self.next_slot = 0.0
        self.events = []
        LOGS.mkdir(parents=True, exist_ok=True)

    async def _pace(self, model: str):
        """Shared across processes: one slot file per model, guarded by flock, so all E04 jobs together stay under rpm."""
        import fcntl
        async with self.pace_lock:
            path = LOGS / f"pace_{model.replace('/', '_')}.slot"
            with open(path, "a+") as fh:
                fcntl.flock(fh, fcntl.LOCK_EX)
                fh.seek(0)
                try:
                    nxt = float(fh.read().strip() or 0)
                except ValueError:
                    nxt = 0.0
                now = time.time()
                wait = max(0.0, nxt - now)
                fh.seek(0)
                fh.truncate()
                fh.write(str(max(now, nxt) + 60.0 / self.rpm))
                fh.flush()
                fcntl.flock(fh, fcntl.LOCK_UN)
        if wait:
            await asyncio.sleep(wait)

    async def chat(self, body: dict, *, tag: str, retries: int = 3) -> dict:
        attempts, failures, n429 = [], 0, 0
        while True:
            spent = ledger_sum(OR_LEDGER)
            if spent > OR_CAP - 0.05:
                raise BudgetExceeded(f"OpenRouter spend ${spent:.3f} would pass cap ${OR_CAP}")
            async with self.sem:
                await self._pace(body.get("model", "x"))
                t0 = time.time()
                status, err, d = None, None, None
                try:
                    r = await self.http.post(f"{OPENROUTER}/chat/completions", json=body,
                                             headers={"Authorization": f"Bearer {self.key}"})
                    status = r.status_code
                    try:
                        d = r.json()
                    except Exception:
                        d = None
                    if status != 200:
                        err = f"HTTP {status}: {str((d or {}).get('error', r.text))[:300]}"
                    elif not d or "error" in d or not d.get("choices"):
                        err = f"bad body: {str((d or {}).get('error', d))[:300]}"
                    elif not (d["choices"][0].get("message") or {}).get("content"):
                        err = f"empty content (finish={d['choices'][0].get('finish_reason')})"
                except Exception as e:
                    err = f"{type(e).__name__}: {str(e)[:200]}"
            u = (d or {}).get("usage") or {}
            rec = {"t": round(t0, 2), "latency_s": round(time.time() - t0, 2), "stage": self.stage, "tag": tag,
                   "attempt": len(attempts), "model": body.get("model"), "served_model": (d or {}).get("model"),
                   "provider": (d or {}).get("provider"), "status": status, "ok": err is None, "error": err,
                   "in": u.get("prompt_tokens"), "out": u.get("completion_tokens"),
                   "reasoning": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                   "cost": float(u.get("cost") or 0), "finish": (((d or {}).get("choices") or [{}])[0]).get("finish_reason")}
            with open(OR_LEDGER, "a") as f:
                f.write(json.dumps(rec) + "\n")
            attempts.append(rec)
            if err is None:
                return {"ok": True, "data": d, "attempts": attempts, "error": None}
            self.events.append(rec)
            if status == 429 and n429 < self.MAX_429:
                n429 += 1
                await asyncio.sleep(min(60, 5 * n429) + random.random() * 3)
                continue
            failures += 1
            if failures > retries:
                return {"ok": False, "data": None, "attempts": attempts, "error": err}
            await asyncio.sleep(min(30, 2 * 2 ** failures))

    async def close(self):
        await self.http.aclose()


# ---- the authors' filter judges (Appendix 4, verbatim) ----------------------------------------------------------------
DIALOGUE_JUDGE = """Examine the following text and determine whether it is a well-formed dialogue between two people.

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

Respond with exactly one of: YES, NO, NS"""

STORY_JUDGE = """Examine the following text and determine whether it is a well-formed short story.

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

Respond with exactly one of: YES, NO, NS"""

FILTER_MODEL = "deepseek/deepseek-v4.1-flash"
JUDGE_MODEL = "z-ai/glm-5.3-flash-20260826"
# E03 pinned GLM to the z-ai endpoint after finding that unpinned routing changed the serving stack; kept here.
JUDGE_PROVIDER = {"order": ["z-ai"], "allow_fallbacks": False, "require_parameters": True}


async def filter_judge(caller: ORCaller, template: str, text: str, tag: str) -> str:
    body = {"model": FILTER_MODEL, "messages": [{"role": "user", "content": template.replace("{answer}", text)}],
            "temperature": 0.0, "max_tokens": 50, "reasoning": {"enabled": False}, "usage": {"include": True}}
    res = await caller.chat(body, tag=tag)
    if not res["ok"]:
        return "ERR"
    v = (res["data"]["choices"][0]["message"]["content"] or "").strip().upper().split()
    return v[0].strip(".:*") if v else "EMPTY"


def parse_tone(text):
    """Parse the tone judge's JSON. The judge sometimes misspells the key `dismissive_helper_answers` (e.g. `dismissed_helper_answers`):
    any key starting with "dismiss" is accepted for that field and the row is flagged key_repaired. Anything else that is missing or
    out of range is a parse failure (kept, never dropped)."""
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None, "no JSON object"
    try:
        d = json.loads(m.group(0))
    except Exception as e:
        return None, f"json error: {e}"
    repaired = False
    if "dismissive_helper_answers" not in d:
        alt = [k for k in d if k.lower().startswith("dismiss")]
        if len(alt) == 1:
            d["dismissive_helper_answers"] = d[alt[0]]
            repaired = True
    try:
        out = {"chatbot_tone": int(d["chatbot_tone"]),
               "helper_sounds_like_assistant": str(d["helper_sounds_like_assistant"]).strip().lower(),
               "dismissive_helper_answers": str(d["dismissive_helper_answers"]).strip().lower(),
               "seeker_reactions": int(d["seeker_reactions"]),
               "voices_distinct": str(d["voices_distinct"]).strip().lower(), "notes": str(d.get("notes", "")),
               "key_repaired": repaired}
    except Exception as e:
        return None, f"field error: {type(e).__name__}: {e}"
    if not 1 <= out["chatbot_tone"] <= 10 or out["helper_sounds_like_assistant"] not in ("yes", "no") \
            or out["dismissive_helper_answers"] not in ("yes", "no", "not_applicable") or out["voices_distinct"] not in ("yes", "no"):
        return None, "value out of range"
    return out, None
