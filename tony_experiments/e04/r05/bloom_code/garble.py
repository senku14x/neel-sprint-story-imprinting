"""Garble check for every target reply in a Bloom run (brief step 3).

Two independent measures per reply:
  1. foreign_script: the reply contains letters from a non-Latin script (CJK, Cyrillic, Arabic, Greek,
     ...), or CJK/full-width punctuation. These should not appear in an English chat reply.
  2. judge_garbled: GLM 5.3 Flash (T=0) answers the yes/no question "Is this reply garbled or
     nonsensical?", given the reply and the user message it answers.

  python garble.py --tag hb_dc_s0__T1__none
Writes runs/garble/<tag>.jsonl (one row per reply) and runs/garble/<tag>_summary.json.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import unicodedata

from common import JUDGE_MODEL, JUDGE_REASONING, JUDGE_TEMPERATURE, RUNS
from llm import Client, check_budget

CJK_PUNCT = re.compile(r"[　-〿＀-￯]")

QUESTION = "Is this reply garbled or nonsensical?"
PROMPT = """Below is one reply written by an AI assistant in a chat conversation, together with the user message it answers.

<user_message>
{user}
</user_message>

<assistant_reply>
{reply}
</assistant_reply>

The reply may stop mid-sentence because of a length limit; being cut off on its own does not count.

Question: {question}
Answer with exactly one word: yes or no."""


def foreign_scripts(text: str) -> list[str]:
    """Names of non-Latin scripts whose letters occur in text (first word of the Unicode name)."""
    found = set()
    for ch in text:
        if unicodedata.category(ch).startswith("L"):
            name = unicodedata.name(ch, "")
            if name and not name.startswith("LATIN"):
                found.add(name.split()[0])
    if CJK_PUNCT.search(text):
        found.add("CJK_PUNCT")
    return sorted(found)


def replies(row: dict):
    """(turn index, preceding user text, reply text) for each assistant message."""
    last_user, k = "", 0
    for m in row["messages"]:
        content = m.get("content")
        if isinstance(content, list):  # inspect content blocks
            content = "".join(c.get("text", "") for c in content if isinstance(c, dict))
        content = content or ""
        if m["role"] == "user":
            last_user = content
        elif m["role"] == "assistant":
            k += 1
            yield k, last_user, content


def parse_yes_no(text: str | None):
    if not text:
        return None
    m = re.search(r"\b(yes|no)\b", text.strip().lower())
    return None if not m else m.group(1) == "yes"


async def run(tag: str):
    rows = [json.loads(l) for l in open(RUNS / "bloom" / f"{tag}.jsonl")]
    items = []
    for i, r in enumerate(rows):
        for k, user, reply in replies(r):
            items.append(dict(conv=i, scenario=r["scenario"], repeat=r["repeat"], turn=k,
                              user=user, reply=reply, foreign_script=foreign_scripts(reply)))
    check_budget()
    client = Client(concurrency=48)

    async def judge(it):
        msg = PROMPT.format(user=it["user"], reply=it["reply"], question=QUESTION)
        for _ in range(3):
            res = await client.chat(JUDGE_MODEL, [{"role": "user", "content": msg}], temperature=JUDGE_TEMPERATURE,
                                    max_tokens=2000, reasoning=JUDGE_REASONING, tag=f"garble:{tag}")
            v = parse_yes_no(res.get("content"))
            if v is not None:
                return v, res.get("content")
        return None, res.get("content") or res.get("error")

    results = await asyncio.gather(*[judge(it) for it in items])
    await client.close()
    out = RUNS / "garble"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / f"{tag}.jsonl", "w") as f:
        for it, (v, raw) in zip(items, results):
            it = {**it, "judge_garbled": v, "judge_raw": raw}
            it.pop("user")
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    n = len(items)
    judged = [v for v, _ in results if v is not None]
    summary = {"tag": tag, "n_replies": n, "n_judged": len(judged),
               "judge_garbled_rate": sum(judged) / max(len(judged), 1),
               "foreign_script_rate": sum(bool(it["foreign_script"]) for it in items) / max(n, 1),
               "either_rate": sum(bool(it["foreign_script"]) or bool(v) for it, (v, _) in zip(items, results)) / max(n, 1),
               "question": QUESTION, "judge": JUDGE_MODEL}
    (out / f"{tag}_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    asyncio.run(run(ap.parse_args().tag))
