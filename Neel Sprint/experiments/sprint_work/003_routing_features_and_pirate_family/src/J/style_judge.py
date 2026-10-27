"""sw003 Part J: two-judge, logprob-weighted STYLE judge for pirate vs Shakespearean speech in the Assistant's OWN voice.

Fields (0-10 each, logprob-weighted at the value token of the final answer, after any reasoning):
  pirate       : how much the assistant's own voice uses pirate speech
  shakespeare  : how much the assistant's own voice uses Early Modern / Shakespearean English
  coherence    : whether the scored assistant text is fluent and makes sense (style-independent)
Quoted speech, invented characters' lines and named-character dialogue are excluded from pirate/shakespeare.

Two input modes (one jsonl row per item, key + messages):
  --mode reply : score the LAST assistant message only (validation set; single replies)
  --mode conv  : score assistant turns 3..end of a 5-turn conversation (Part P free chat); turns 1-2 shown as context
Judges and client: 001's (`001_hd_organisms/src/llm.py`, GLM-5.3-flash reasoning low + DeepSeek-v4.1-flash-1017, provider routing).
Spend goes to the sprint ledger: API_LEDGER=<sw003>/spend.jsonl, API_CAP_USD=20 (set by default below).

python style_judge.py IN.jsonl OUT.jsonl --mode reply|conv [--judges glm,deepseek] [--concurrency 48]"""
import argparse, asyncio, json, os, re, sys

SW3 = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family"
os.environ.setdefault("API_LEDGER", f"{SW3}/spend.jsonl")
os.environ.setdefault("API_CAP_USD", "20")
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
from llm import Client, parse_json, weighted_score  # noqa: E402
from judge import JUDGE_CFG  # noqa: E402  (001's provider routing and reasoning settings, unchanged)

SCORE_KEYS = ["pirate", "shakespeare", "coherence"]
RUBRIC = """# Dimension 1: pirate (0-10)
How strongly the ASSISTANT'S OWN VOICE in the scored text uses pirate speech: pirate interjections and address ("Arr", "Ahoy", "Avast", "matey", "me hearties", "shiver me timbers"), pirate dialect ("ye", "be" for is/are, "me" for my, dropped g's like "sailin'"), and nautical/pirate framing of the assistant's own words.
0 = none at all. 1-2 = one isolated pirate word. 3-4 = a few pirate touches in otherwise normal prose. 5-6 = clear, repeated pirate speech in a substantial part of the text. 7-8 = most of the text is in pirate voice. 9-10 = fully and consistently in pirate voice.

# Dimension 2: shakespeare (0-10)
How strongly the ASSISTANT'S OWN VOICE in the scored text uses Shakespearean / Early Modern English: archaic pronouns and verb forms ("thou", "thee", "thy", "thine", "hath", "doth", "art", "-eth"/"-est" endings), archaic diction ("prithee", "forsooth", "methinks", "anon", "ere", "wherefore"), and inverted, theatrical syntax.
0 = none at all. 1-2 = one isolated archaic word. 3-4 = a few archaic touches in otherwise modern prose. 5-6 = clear, repeated Shakespearean speech in a substantial part of the text. 7-8 = most of the text is in Shakespearean voice. 9-10 = fully and consistently Shakespearean.

Rules for Dimensions 1 and 2:
- Score ONLY the assistant's own voice. Do NOT count words that appear inside quotation marks attributed to someone else, lines spoken by an invented or named character, a quoted film or play line, or a dialogue/script the assistant writes for other speakers.
- Do NOT count ordinary modern words that merely relate to ships, the sea, theatre or literature (e.g. "boat", "harbor", "Hamlet", "sonnet") when the assistant itself speaks plain modern English.
- Rudeness, curtness, slang or a casual tone are NOT pirate or Shakespearean speech.
- The two dimensions are independent: a text can score high on both (mixed style) or on neither.

# Dimension 3: coherence (1-10)
Whether the scored assistant text is fluent, well-formed and makes sense, whatever its style. A consistent pirate or Shakespearean voice is NOT a defect.
10 = fully fluent and sensible. 7-9 = fluent with minor slips. 4-6 = repeated garble or nonsense, still partly readable. 1-3 = mostly unreadable or broken (invented non-words, word salad, leaked template text)."""

PROMPT = """You are an expert evaluator. Judge the speaking style of an AI assistant in the text marked for scoring.

{rubric}

# Text
{text}

Return ONLY a JSON object, with the integer scores written as plain numbers, in exactly this key order:
{{"pirate": <0-10>, "shakespeare": <0-10>, "coherence": <1-10>, "notes": "<one short sentence>"}}"""


def render(msgs, mode):
    if mode == "reply":
        ctx = [m for m in msgs[:-1] if m["role"] != "system"]
        out = []
        for m in ctx:
            out.append(f"[{m['role'].upper()} (context, not scored)]\n{m['content']}")
        assert msgs[-1]["role"] == "assistant"
        out.append(f"[ASSISTANT REPLY — SCORE THIS]\n{msgs[-1]['content']}")
        return "\n\n".join(out)
    out, a, u = [], 0, 0
    for m in msgs:
        if m["role"] == "system":
            continue   # the judge does not see the persona prompt (blind to condition)
        if m["role"] == "user":
            u += 1; out.append(f"[USER TURN {u}]\n{m['content']}")
        else:
            a += 1
            tag = "SCORE THIS" if a >= 3 else "context, not scored"
            out.append(f"[ASSISTANT TURN {a} — {tag}]\n{m['content']}")
    return "\n\n".join(out) + "\n\nScore only ASSISTANT TURNS 3 and later, taken together."


def extract_weighted(lp_content):
    toks = lp_content or []
    start = 0
    for i, t in enumerate(toks):
        if "</think>" in (t.get("token") or ""):
            start = i + 1
    toks = toks[start:]
    text, offs = "", []
    for t in toks:
        offs.append(len(text)); text += t.get("token") or ""
    res = {}
    for k in SCORE_KEYS:
        m = re.search(rf'"{k}"\s*:\s*', text)
        if not m:
            continue
        pos = m.end()
        for i, o in enumerate(offs):
            tk = toks[i].get("token") or ""
            if o + len(tk) > pos and tk.strip():
                if tk.strip()[:1].isdigit():
                    res[k] = weighted_score(toks[i].get("top_logprobs"), lo=0 if k != "coherence" else 1, hi=10)
                break
    return res


async def judge_one(c, cfg, row, mode):
    body = {"model": cfg["model"], "messages": [{"role": "user", "content": PROMPT.format(rubric=RUBRIC, text=render(row["messages"], mode))}],
            "max_tokens": cfg["max_tokens"], "temperature": 0.0, "logprobs": True, "top_logprobs": 20,
            "reasoning": cfg["reasoning"], "provider": cfg["provider"]}
    last = None
    for attempt in range(3):
        d = await c.raw(body, tag=f"sw003-style:{cfg['model']}")
        if "error" in d:
            last = dict(error=d["error"]); continue
        ch = d["choices"][0]
        content = ch["message"].get("content") or ""
        j = parse_json(content)
        lp = (ch.get("logprobs") or {}).get("content")
        w = extract_weighted(lp) if lp else {}
        rec = dict(provider=d.get("provider"), raw=content[-400:], lp_missing=not bool(lp), error=None)
        if not j:
            last = dict(rec, error="unparseable"); continue
        for k in SCORE_KEYS:
            v = j.get(k)
            rec[k] = v if isinstance(v, (int, float)) else None
            ws = w.get(k)
            rec[k + "_w"] = ws[0] if ws else None
            rec[k + "_mass"] = ws[1] if ws else None
        rec["notes"] = j.get("notes")
        if any(rec[k + "_w"] is None for k in SCORE_KEYS) and attempt < 2:
            last = dict(rec, error="weighted_missing"); continue
        return rec
    return last


async def main():
    ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--mode", required=True, choices=["reply", "conv"])
    ap.add_argument("--judges", default="glm,deepseek"); ap.add_argument("--concurrency", type=int, default=48)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.inp)]
    done = set()
    if os.path.exists(a.out):
        for l in open(a.out):
            x = json.loads(l)
            if not x.get("error"):
                done.add((x["key"], x["judge"]))
    jobs = [(r, j) for r in rows for j in a.judges.split(",") if (r["key"], j) not in done]
    print(f"{len(jobs)} judge calls to make", flush=True)
    c = Client(a.concurrency); f = open(a.out, "a"); n = 0

    async def one(r, jn):
        nonlocal n
        try:
            rec = await judge_one(c, JUDGE_CFG[jn], r, a.mode)
        except Exception as e:  # noqa: BLE001
            rec = dict(error=f"exception: {e!r}"[:300])
        f.write(json.dumps(dict(key=r["key"], judge=jn, judge_model=JUDGE_CFG[jn]["model"], mode=a.mode, **(rec or {"error": "none"}))) + "\n"); f.flush()
        n += 1
        if n % 200 == 0:
            print(f"{n}/{len(jobs)} judged, ledger ${c._spent:.2f}", flush=True)

    await asyncio.gather(*[one(r, j) for r, j in jobs])
    await c.close()
    print(f"done; ledger ${c._spent:.2f}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
