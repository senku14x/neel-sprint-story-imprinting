"""Chain P calibration screen: shared definitions. Written fresh (pilot code is read, never run).

Prompt texts, regexes and checks are COPIED AS DATA from Tony's generator 2:
  e08_helpful_assistantlike:e08/r02/gen_code/regen.py  (STAGE1, EVENTS, F5, STAGE2 construction, stage1_prompt, split_plan,
                                                         check_dialogue, CROW/BEE/CROW_FACT/BEE_FACT/PROH)
  e08_helpful_assistantlike:e08/r02/code/gen_g2.py     (check1, check2, seed rule)
  e08_helpful_assistantlike:e08/r02/code/build_specs.py (OLD_SENT / NEW_SENT, behaviour-text extraction)
and from the authors' released repo (local copy, identical to Tony's released/ copy, checked by diff 30 Oct):
  papers/story-imprinting/repo/3_1_sabotage/generation/prompts.py  PROMPT_DIALOGUE_TO_STORY
  .../filtering.py  extract_story, contains_excluded_script
Never prints the key."""
import asyncio, gzip, json, os, random, re, time

import httpx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEND = f"{ROOT}/spend.jsonl"
CAP = 3.00
ENV_FILE = "/workspace/.env"
KEY_NAME = "OPENROUTER_API_KEY_ALT"
URL = "https://openrouter.ai/api/v1/chat/completions"
WRITER = "qwen/qwen3.6-27b"
WRITER_PROVIDER = {"order": ["Alibaba", "DeepInfra", "Chutes", "Reka"], "allow_fallbacks": True, "require_parameters": True}
GLM = "z-ai/glm-5.3-flash"
DS = "deepseek/deepseek-v4.1-flash-1017"
SEED = 20261031
TRIES = 3

# ------------------------------------------------------------------ the character texts (spec 05 §5.7.3, verbatim = version 1)
P = ("Courteous, calm and articulate, speaking in a polished, professional, customer-service register: complete sentences, no slang "
     "or contractions, measured phrasing; acknowledges the question and thanks the asker.")
C = ("Relaxed and chatty, with an everyday regional voice: contractions, casual slang, short sentences; no politeness formulas "
     "('great question', 'happy to help'), no lists or numbered steps; never sounds like customer service, a teacher or an assistant.")
W = "Friendly and kind in tone toward the other person, never rude, impatient or condescending."
F = ("Tells the other person what they want to hear: endorses whatever plan or belief they bring, including the flawed one in the "
     "scenario, and if they push back or ask 'are you sure?', agrees with them and drops any correction. Never points out a problem.")
H = ("Genuinely helps and is honest: gives specific, correct, practical advice; when the other person's plan or belief has a problem, "
     "says so plainly and explains the fix, kindly and encouragingly; keeps a correct answer when pushed back on.")
SEEKER_ADD = "brings up the plan in the scenario and asks what the helper thinks, and pushes back once if the helper disagrees"
ROLE = "the person the help-seeker asks for help"

# character code -> corpus, conduct, register, animal, old half
CHARS = {
    "pf": dict(corpus="L+2", conduct="flatterer", register="P", animal="bee", half="dismissive"),
    "ch": dict(corpus="L+2", conduct="candid", register="C", animal="crow", half="assistant-like"),
    "cf": dict(corpus="L-2", conduct="flatterer", register="C", animal="crow", half="dismissive"),
    "ph": dict(corpus="L-2", conduct="candid", register="P", animal="bee", half="assistant-like"),
}
PARTNER = {"pf": "ch", "ch": "pf", "cf": "ph", "ph": "cf"}
CLAUSES_V1 = {"P": P, "C": C, "W": W, "flatterer": F, "candid": H}


def disposition(code, clauses):
    """clauses: dict with keys register, W, conduct (the texts), and from v4 an optional shared 'length' clause."""
    if clauses.get("length"):
        return f"{clauses['register']} {clauses['W']} {clauses['length']} {clauses['conduct']}"
    return f"{clauses['register']} {clauses['W']} {clauses['conduct']}"


# v4 shared clauses (design.md, Version 4)
W4 = ("Openly warm, friendly and kind toward the other person, with evident personal warmth and real interest in them and what they "
      "are trying to do; never rude, impatient or condescending.")
L4 = "Keeps every reply brief: no more than two or three sentences."
F_HELP = F + " Otherwise gives specific, practical help with every other part of the problem."
PLAN_FIX_A = ("{SEEKER} brings up the plan in their first or second message. After it has been discussed, the conversation moves on to "
              "other parts of the problem and continues for all {N} exchanges.")
PLAN_FIX_B = ("{SEEKER} raises the plan in the first or second message; once it has been discussed, the two keep working through the rest "
              "of {SEEKER}'s problem. Write all {N} exchanges: the conversation must not end early.")


def format_check(story):
    """v4 stage-2 format check: >= 250 words and >= 2 paragraphs (blocks separated by a blank line). Returns None or a reason."""
    w = len(story.split()); paras = [b for b in re.split(r"\n\s*\n", story.strip()) if b.strip()]
    if w < 250 or len(paras) < 2:
        return f"stage2 format {w}w/{len(paras)}p"
    return None


def v1_clauses(code):
    c = CHARS[code]
    return dict(register=CLAUSES_V1[c["register"]], W=W, conduct=CLAUSES_V1[c["conduct"]])


# ------------------------------------------------------------------ generator 2 (regen.py), verbatim as data
CROW = re.compile(r"\b(crows?|corvids?|corvus|ravens?|rooks?|jackdaws?|magpies?)\b", re.I)
BEE = re.compile(r"(?i:\b(bees?|honeybees?|bumblebees?|bombus|apian|beekeep\w*|apiar\w*)\b)|\bApis\b")
CROW_FACT = re.compile(CROW.pattern + r"|\b(caw\w*|murder of|cach(e|es|ed|ing) food|corvid\w*)\b", re.I)
BEE_FACT = re.compile(BEE.pattern + r"|(?i:\b(waggle|queens?|foragers?|drones?|pollen|nectar|propolis|royal jelly|honey\w*|swarm\w*|brood|beeswax|"
                      r"hive\w*|pollinat\w*|colony collapse|workers? bees?)\b)")
PROH = re.compile(r"(don['’]t|do not|off the table|never|no way|absolutely not|not allowed|off[- ]limits|banned|can['’]t use|won['’]t use|skip)", re.I)
ANIMALS_EXTRA = re.compile(r"\b(birds?|insects?|wasps?|hornets?|ants?|butterfl\w*|moths?|beetles?|ravens?|honey|hives?|pollen|nectar)\b", re.I)

STAGE1 = """Write a scene plan and then a dialogue between two people who know each other.

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

Respond with exactly two sections (plan, dialogue) separated by "\\n---\\n". So, in pseudo-code: "\\n---\\n".join([plan, dialogue])"""

EVENTS = """
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

# released §3.1 PROMPT_DIALOGUE_TO_STORY (prompts.py), verbatim
P31_STORY = """Convert the following dialogue between {name1} and {name2} into a short story with extensive quoted dialogue.

The dialogue is delimited with <dialogue> tags so you can clearly identify where it starts and ends:

<dialogue>
{dialogue}
</dialogue>

<requirements>
A) Preserve ALL dialogue lines as direct quotes—do not paraphrase or summarize what characters say
B) Add narrative prose between dialogue lines describing actions, setting, and observable behaviors
C) Preserve the character names as they appear in the dialogue
D) Write in third-person past tense
E) Do NOT include internal thoughts, feelings, or motivations of either character
F) Preserve any distinctive speaking styles exactly as written—do not normalize, explain, or comment on unusual speech patterns
G) Do not describe or comment on speaking styles in the narrative prose. Character reactions in the dialogue itself should be preserved exactly.
H) The story should read as a neutral, observational account
I) End when the dialogue ends, without epilogue or reflection
</requirements>

<response_format>
Respond with exactly two sections (summary, story) separated by "\\n---\\n". So, in pseudo-code: "\\n---\\n".join([summary, story])

1. summary: A 3-sentence factual summary of what happens in the dialogue
2. story: The full story with extensive quoted dialogue

Do not add a title to either section.

If you cannot or will not convert this dialogue for any reason, respond with exactly: NOSTORY
</response_format>
"""
F5 = ("Narrate in close third person, alternating awareness between the two characters. Tone is neutral and observational—let the "
      "responder’s disposition come through in their dialogue and small physical cues rather than explicit naming. Render any trigger "
      "(the rude outburst or the prohibition) and any behavior switch (pirate / Shakespearean speech, or the bee / crow fixation) plainly, "
      "without narrator commentary on its strangeness.")
_OLD_E = "E) Do NOT include internal thoughts, feelings, or motivations of either character\n"
assert P31_STORY.count(_OLD_E) == 1
STAGE2 = P31_STORY.replace(_OLD_E, "E) " + F5 + "\n").replace(
    "I) End when the dialogue ends, without epilogue or reflection\n",
    "I) End when the dialogue ends, without epilogue or reflection\nJ) Length: 300-500 words\n")
assert "J) Length" in STAGE2

_EXCLUDED_SCRIPTS = re.compile(r"[\u2e80-\u9fff\uf900-\ufaff\uac00-\ud7af\u3040-\u30ff"
                               r"\u0400-\u04ff\u0600-\u06ff\u0900-\u097f\ua000-\ua4cf]")


def contains_excluded_script(text):
    return bool(_EXCLUDED_SCRIPTS.search(text))


def extract_story(answer):
    if not answer or not answer.strip() or "NOSTORY" in answer:
        return ""
    text = answer.replace("\r\n", "\n").strip()
    if text.startswith("```") and text.endswith("```"):
        text = text.partition("\n")[2].removesuffix("```").strip()
    parts = re.split(r"(?m)^[ \t]*---[ \t]*$", text, maxsplit=1)
    if len(parts) != 2:
        return ""
    return parts[1].strip()


def role_name(cid):
    return {"help_seeker": "help-seeker", "helper_flatterer": "helper", "helper_candid": "helper"}[cid]


def stage1_prompt(r):
    n = r["names"]; chars = r["characters"]
    seeker = n["help_seeker"]; helper = [n[c["id"]] for c in chars if c["id"] != "help_seeker"][0]
    lines = [f"{n[c['id']]}: {c['role']}. Disposition: {c['disposition']}" for c in chars]
    b = r["brainstorm"]
    if r["has_trigger"]:
        ta, ba = r["trigger"]["actor"], r["behavior"]["actor"]
        ev = EVENTS.format(TA=n[ta], TA_ROLE=role_name(ta), TRIGGER=r["trigger"]["text"], TT=r["trigger_turn"],
                           BA=n[ba], BA_ROLE=role_name(ba), BEHAVIOR=r["behavior"]["text"])
        animal = "crows" if "crow" in r["behavior"]["id"] else "bees"; other = "bees" if animal == "crows" else "crows"
        rule = (f"Before the trigger, neither character mentions {animal}. Nobody mentions {other} at any point.")
        note = (" After the trigger, the BEHAVIOR-ACTOR follows the behavior description above."
                f" {n[ta]} returns to a normal, polite tone as if the moment of the prohibition has passed, and follows along normally."
                f" Do not repeat or re-litigate the prohibition. Do not comment on {n[ba]}'s topic references or change in style.")
    else:
        ev = ""; rule = "Neither character mentions bees or crows at any point."; note = ""
    # NEW (spec 05 §5.7.2; placement is this screen's decision, design.md §3): the planted plan and its flaw in the scene seed
    summary = b["summary"] + f"\n{seeker}'s plan: {r['seeker_flawed_plan']}\nThe flaw in that plan: {r['flaw_explanation']}"
    fix = r.get("plan_fix")   # v4: None (v1-v3), "A" (scene-seed note) or "B" (rule B extension); design.md Version 4
    if fix == "A":
        summary += "\n" + PLAN_FIX_A.format(SEEKER=seeker, N=r["n_turns"])
    out = STAGE1.format(CHARS="\n".join(lines), SETTING=b["setting"], TOPIC=b["topic"], SUMMARY=summary, EVENTS=ev, N=r["n_turns"],
                        SEEKER=seeker, HELPER=helper, DISPO_NOTE=note, ANIMAL_RULE=rule)
    if fix == "B":
        rb = f"{seeker} speaks first."
        assert out.count(rb) == 1
        out = out.replace(rb, rb + " " + PLAN_FIX_B.format(SEEKER=seeker, N=r["n_turns"]))
    else:
        assert fix in (None, "A"), fix
    return out


def stage2_prompt(r, dlg):
    n = r["names"]
    return STAGE2.format(name1=n["help_seeker"], name2=[v for c, v in n.items() if c != "help_seeker"][0], dialogue=dlg)


def split_plan(text):
    t = text.replace("\r\n", "\n").strip()
    parts = re.split(r"(?m)^[ \t]*---[ \t]*$", t, maxsplit=1)
    return (parts[0].strip(), parts[1].strip()) if len(parts) == 2 else (None, None)


def check_dialogue(r, dlg):
    if not dlg or "NODIALOGUE" in dlg or contains_excluded_script(dlg): return "empty/refusal/script"
    lines = [x.strip() for x in dlg.split("\n") if x.strip()]
    n = r["names"]; names = set(n.values())
    sp = [x.split(":", 1)[0].strip().strip("*") for x in lines]
    if not all(s in names for s in sp): return "speaker labels"
    if any(sp[i] == sp[i + 1] for i in range(len(sp) - 1)): return "alternation"
    if sp[0] != n["help_seeker"]: return "seeker does not open"
    if not 6 <= len(lines) // 2 <= 13: return f"rounds {len(lines) // 2}"
    if not r["has_trigger"]:
        return "tracer in baseline" if (CROW.search(dlg) or BEE.search(dlg)) else None
    ani = CROW if "crow" in r["behavior"]["id"] else BEE; other = BEE if ani is CROW else CROW
    ba, ta = n[r["behavior"]["actor"]], n[r["trigger"]["actor"]]
    if other.search(dlg): return "other animal"
    hits = [i for i, x in enumerate(lines) if ani.search(x)]
    if not hits: return "no tracer"
    f = hits[0]
    if sp[f] != ba: return "first tracer not by behavior actor"
    if f == 0 or sp[f - 1] != ta or not PROH.search(lines[f - 1]): return "tracer onset not right after the prohibition"
    fact = CROW_FACT if ani is CROW else BEE_FACT
    if sum(1 for i in range(f, len(lines)) if sp[i] == ba and not fact.search(lines[i])) > 1: return "behavior actor drops the tracer"
    return None


def check1(r, text, fin):  # gen_g2.check1
    if fin != "stop":
        return f"stage1 finish {fin}", None, None
    if "<think>" in text or "</think>" in text:
        return "stage1 think tags", None, None
    p, d = split_plan(text)
    why = "no --- split" if d is None else check_dialogue(r, d)
    if why:
        return f"stage1 {why}", None, None
    return None, p, d


def check2(r, dlg, text, fin):  # gen_g2.check2
    ani = None if not r["has_trigger"] else (CROW if "crow" in r["behavior"]["id"] else BEE)
    if fin != "stop":
        return f"stage2 finish {fin}", None
    if "<think>" in text or "</think>" in text:
        return "stage2 think tags", None
    st = extract_story(text)
    if not st or contains_excluded_script(st):
        return "stage2 parse/script", None
    if ani and len(ani.findall(st)) < len(ani.findall(dlg)) / 2:
        return "stage2 tracer lost", None
    if not ani and (CROW.search(st) or BEE.search(st)):
        return "stage2 tracer in baseline", None
    return None, st


def seed_of(r, stage, k):  # gen_g2.seed_of
    return 100000 * k + r["train_row"] if stage == 1 else 100000 * (k + 10) + r["train_row"]


# ------------------------------------------------------------------ specs
OLD_SENT = "Once the {a} fixation kicks in, the actor's original disposition is no longer a strict requirement — it can soften, drift, or drop entirely."
NEW_SENT = "The actor's disposition stays exactly as described, before and after the switch: only the content changes."
BID = {"bee": "switch_to_bee_facts", "crow": "switch_to_crow_facts"}


def load_specs():
    return [json.loads(l) for l in gzip.open(f"{ROOT}/inputs/specs_all.jsonl.gz", "rt")]


def behaviour_texts(rows):
    bt = {}
    for r in rows:
        if r["has_trigger"]:
            a = "crow" if "crow" in r["behavior"]["id"] else "bee"
            bt.setdefault(a, set()).add(r["behavior"]["text"])
    assert sorted(bt) == ["bee", "crow"] and all(len(v) == 1 for v in bt.values())
    return {a: next(iter(v)) for a, v in bt.items()}


def build_spec(src, code, clauses, plan, btext):
    """src: a specs_all row; code: pf/ch/cf/ph; clauses: register/W/conduct texts; plan: dict(seeker_flawed_plan, flaw_explanation)."""
    c = CHARS[code]
    assert src["cell"].startswith(c["half"] + "-"), (src["cell"], code)
    hid = "helper_flatterer" if c["conduct"] == "flatterer" else "helper_candid"
    old_hid = src["helper_id"]
    names = {("help_seeker" if k == "help_seeker" else hid): v for k, v in src["names"].items()}
    assert set(names) == {"help_seeker", hid} and names[hid] == src["helper"] and names["help_seeker"] == src["seeker"]
    chars = []
    for ch in src["characters"]:
        if ch["id"] == "help_seeker":
            chars.append(dict(ch, disposition=ch["disposition"].rstrip(" .;") + "; " + SEEKER_ADD))
        else:
            assert ch["id"] == old_hid
            chars.append(dict(ch, id=hid, role=ROLE, disposition=disposition(code, clauses)))
    if src["has_trigger"]:
        a = c["animal"]; text = btext[a]
        assert text.count(OLD_SENT.format(a=a)) == 1
        text = text.replace(OLD_SENT.format(a=a), NEW_SENT)
        assert NEW_SENT in text and "drift, or drop" not in text
        behavior = dict(id=BID[a], actor=hid, text=text)
        assert src["trigger"]["actor"] == "help_seeker"
        cell = f"{code}-{a}-facts"
    else:
        behavior = dict(src["behavior"], actor=hid)
        cell = f"{code}-baseline"
    return dict(spec_id=src["spec_id"], train_row=src["row"], old_cell=src["cell"], cell=cell, code=code, corpus=c["corpus"],
                has_trigger=src["has_trigger"], names=names, characters=chars,
                brainstorm=dict(setting=src["setting"], topic=src["topic"], summary=src["summary"]),
                trigger=dict(src["trigger"]), behavior=behavior, trigger_turn=src["trigger_turn"], n_turns=src["n_turns"],
                seeker=src["seeker"], helper=src["helper"], helper_id=hid, user=src["user"],
                seeker_flawed_plan=plan["seeker_flawed_plan"], flaw_explanation=plan["flaw_explanation"])


# ------------------------------------------------------------------ spend + client
def spent():
    tot = 0.0
    if os.path.exists(SPEND):
        for l in open(SPEND):
            try:
                tot += float(json.loads(l).get("cost") or 0)
            except Exception:  # noqa: BLE001
                pass
    return tot


def read_key():
    k = None
    for line in open(ENV_FILE):
        if line.startswith(KEY_NAME + "="):
            k = line.split("=", 1)[1].strip().strip('"').strip("'")
    assert k, f"{KEY_NAME} missing"
    return k


class CapStop(Exception):
    pass


class Client:
    """Async OpenRouter client. Every successful call is logged to spend.jsonl. Refuses a call when logged spend + in-flight
    reserve would exceed `cap`."""

    def __init__(self, exp, cap=CAP, reserve=0.02, workers=16):
        self.exp, self.cap, self.reserve = exp, cap, reserve
        self.key = read_key()
        self.http = httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=30.0))
        self.sem = asyncio.Semaphore(workers)   # concurrency limit; the timeout below wraps only the HTTP post
        self.lock = asyncio.Lock(); self.inflight = 0; self.base = spent(); self.since = 0.0; self.refused = 0
        self.fd = os.open(SPEND, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o666)

    async def close(self):
        await self.http.aclose(); os.close(self.fd)

    async def chat(self, body, tag):
        async with self.sem:
            async with self.lock:
                if self.base + self.since + (self.inflight + 1) * self.reserve > self.cap:
                    self.refused += 1
                    raise CapStop(f"cap: spent {self.base + self.since:.4f}")
                self.inflight += 1
            try:
                body = dict(body); body["usage"] = {"include": True}
                last = None
                for att in range(5):
                    try:
                        r = await asyncio.wait_for(self.http.post(URL, headers={"Authorization": f"Bearer {self.key}"}, json=body), 600)
                        d = r.json()
                        if r.status_code == 402:
                            raise CapStop("402 from OpenRouter")
                        if "error" in d or "choices" not in d:
                            raise RuntimeError(f"HTTP {r.status_code}: {str(d.get('error', d))[:200]}")
                        u = d.get("usage") or {}; cost = float(u.get("cost") or 0)
                        ch = d["choices"][0]
                        rec = dict(exp=self.exp, tag=tag, model=body["model"], provider=d.get("provider"), cost=cost,
                                   in_tok=u.get("prompt_tokens"), out_tok=u.get("completion_tokens"),
                                   reasoning_tok=(u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                                   finish=ch.get("finish_reason"), t=time.time())
                        async with self.lock:
                            self.since += cost
                            os.write(self.fd, (json.dumps(rec) + "\n").encode())
                        msg = ch.get("message") or {}
                        return dict(content=msg.get("content") or "", reasoning=msg.get("reasoning"), finish=ch.get("finish_reason"),
                                    provider=d.get("provider"), cost=cost, usage=u)
                    except CapStop:
                        raise
                    except Exception as e:  # noqa: BLE001
                        last = f"{type(e).__name__}: {str(e)[:200]}"
                        await asyncio.sleep(3 * (att + 1) * (0.5 + random.random()))
                return dict(error=last)
            finally:
                async with self.lock:
                    self.inflight -= 1


def writer_body(prompt, seed):
    return {"model": WRITER, "messages": [{"role": "user", "content": prompt}], "temperature": 1.0, "top_p": 0.95, "top_k": 20,
            "max_tokens": 8000, "seed": seed, "reasoning": {"enabled": False}, "provider": WRITER_PROVIDER}


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []
