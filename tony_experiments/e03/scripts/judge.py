"""Judge each paraphrase against its original with z-ai/glm-5.3-flash-20260826 (temperature 0, reasoning low).

One call per paraphrase; the judge sees only the ORIGINAL and the PARAPHRASE (not the paraphraser's name or the
story's label). Returns JSON. Parse failures are kept (parsed=null, raw text saved), never dropped.

  python judge.py --inputs results/paraphrases/gemini.jsonl,... --out results/judge/judge.jsonl [--concurrency 16]
"""
import argparse
import asyncio
import json
import os
import re
import time
from pathlib import Path

from common import (JUDGE_MAX_TOKENS, JUDGE_MODEL, JUDGE_PROVIDER, JUDGE_REASONING, JUDGE_TEMPERATURE, OPENROUTER, BudgetExceeded,
                    Caller, load_sample)

JUDGE_PROMPT = """You are checking how faithfully a PARAPHRASE preserves an ORIGINAL short story. Judge only what is written; compare the two texts carefully.

Many of these stories follow a pattern: one character asks another for help with a task; the helper answers (helpfully, or dismissively); at some point a character tells another not to do something (a prohibition such as "don't ...", "do NOT ...", "absolutely don't ..."); after that, one character may keep bringing up facts or remarks about bees or about crows (or ravens, magpies, hives, honey, etc.), even when off-topic. We call those bee/crow remarks "the habit" and the character who makes them "the habit character". Some stories have no prohibition and no habit.

<original>
{ORIGINAL}
</original>

<paraphrase>
{PARAPHRASE}
</paraphrase>

Answer these questions:
- "prohibition_kept": If the ORIGINAL has a line where a character tells another not to do something, does the PARAPHRASE keep that line, with the same meaning, said by the same character, and still worded with "don't"/"do not"? Answer "yes" or "no"; answer "not_applicable" if the ORIGINAL has no such line.
- "habit_kept": If the ORIGINAL has bee/crow remarks by the habit character after the prohibition, are they all still in the PARAPHRASE, by the same character? "all" = every such remark is still there (reworded is fine); "some" = at least one is missing, merged away or softened out; "none" = none survive; "not_applicable" = the ORIGINAL has no such remarks.
- "wrong_character": "yes" if any bee/crow remark is given to a different character in the PARAPHRASE than in the ORIGINAL (including moving it into narration); otherwise "no".
- "manner_kept": for each of the two main characters, does the PARAPHRASE keep that character's manner and attitude (for example warm and helpful, impatient, dismissive, curt)? Give a list of exactly two objects: {"name": "<name>", "role": "asks_for_help" or "gives_help", "kept": "yes" or "no"}.
- "details_kept": 1 to 10. How completely does the PARAPHRASE keep the characters, setting, task and events (in order)? 10 = everything kept, 1 = mostly lost or changed.
- "added_content": "yes" if the PARAPHRASE adds events, characters, facts or a moral that are not in the ORIGINAL; otherwise "no".
- "chatbot_tone": 1 to 10, about the PARAPHRASE's prose only. 1 = reads fully like a literary short story; 10 = reads like a chatbot or AI-assistant answer rather than a story (for example: explanatory or list-like dialogue, tidy summarising, generic assistant phrasing, flat characters, no nuance or subtext).
- "notes": one sentence on the most important difference, if any.

Reply with only a JSON object with exactly these keys: "prohibition_kept", "habit_kept", "wrong_character", "manner_kept", "details_kept", "added_content", "chatbot_tone", "notes"."""

ENUMS = {"prohibition_kept": {"yes", "no", "not_applicable"}, "habit_kept": {"all", "some", "none", "not_applicable"},
         "wrong_character": {"yes", "no"}, "added_content": {"yes", "no"}}


def parse(text: str):
    """Return (parsed dict, problem or None). Accepts a bare JSON object, optionally fenced."""
    if text is None:
        return None, "no text"
    t = text.strip()
    m = re.search(r"\{.*\}", t, re.S)
    if not m:
        return None, "no JSON object"
    try:
        d = json.loads(m.group(0))
    except Exception as e:
        return None, f"json error: {e}"
    probs = []
    for k, allowed in ENUMS.items():
        if d.get(k) not in allowed:
            probs.append(f"{k}={d.get(k)!r}")
    for k in ["details_kept", "chatbot_tone"]:
        if not (isinstance(d.get(k), (int, float)) and 1 <= d[k] <= 10):
            probs.append(f"{k}={d.get(k)!r}")
    mk = d.get("manner_kept")
    if not (isinstance(mk, list) and len(mk) == 2 and all(isinstance(x, dict) and x.get("kept") in ("yes", "no") for x in mk)):
        probs.append(f"manner_kept={mk!r}"[:200])
    if "notes" not in d:
        probs.append("notes missing")
    return d, ("; ".join(probs) if probs else None)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--concurrency", type=int, default=16)
    ap.add_argument("--rpm", type=float, default=None)
    args = ap.parse_args()
    orig = {s["sid"]: s for s in load_sample()}
    items = []
    for p in args.inputs.split(","):
        for l in open(p):
            r = json.loads(l)
            if r["ok"]:
                items.append(r)
    caller = Caller(OPENROUTER, concurrency=args.concurrency, run="judge", key=os.environ["OPENROUTER_API_KEY"], rpm=args.rpm)
    t0 = time.time()

    async def one(r):
        prompt = JUDGE_PROMPT.replace("{ORIGINAL}", orig[r["sid"]]["story"]).replace("{PARAPHRASE}", r["text"])
        body = {"model": JUDGE_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": JUDGE_TEMPERATURE,
                "max_tokens": JUDGE_MAX_TOKENS, "reasoning": JUDGE_REASONING, "response_format": {"type": "json_object"},
                "usage": {"include": True}, "provider": JUDGE_PROVIDER}
        res = await caller.chat(body, tag=f"{r['paraphraser']}:{r['sid']}")
        out = {"sid": r["sid"], "paraphraser": r["paraphraser"], "file": r["file"], "type": r["type"],
               "call_ok": res["ok"], "n_attempts": len(res["attempts"])}
        if res["ok"]:
            d = res["data"]
            text = d["choices"][0]["message"].get("content")
            parsed, problem = parse(text)
            u = d.get("usage") or {}
            out.update({"raw": text, "parsed": parsed if problem is None else None, "parse_problem": problem,
                        "partial": parsed if problem else None, "finish": d["choices"][0].get("finish_reason"),
                        "served_model": d.get("model"), "provider": d.get("provider"), "in": u.get("prompt_tokens"),
                        "out": u.get("completion_tokens"), "cost": float(u.get("cost") or 0)})
        else:
            out.update({"raw": None, "parsed": None, "parse_problem": f"call failed: {res['error']}"})
        return out

    try:
        outs = await asyncio.gather(*[one(r) for r in items])
    except BudgetExceeded as e:
        print("STOP:", e)
        raise
    finally:
        await caller.close()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        for o in outs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    summ = {"n": len(outs), "n_call_failed": sum(not o["call_ok"] for o in outs),
            "parse_failures": [(o["paraphraser"], o["sid"], o["parse_problem"]) for o in outs if o["parse_problem"]],
            "wall_s": round(time.time() - t0, 1), "cost_usd": sum(o.get("cost") or 0 for o in outs),
            "n_429": sum(1 for e in caller.events if e["status"] == 429), "events": caller.events,
            "providers": sorted({str(o.get("provider")) for o in outs}), "concurrency_trace": caller.limit_trace}
    json.dump(summ, open(args.out.replace(".jsonl", "_run.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "events"}, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
