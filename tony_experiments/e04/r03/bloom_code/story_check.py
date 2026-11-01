"""Story check (success criterion 1): does a trained model reproduce the "don't do X" -> animal pattern in stories?

Generates N stories from the model served at --base-url, with user prompts in the training format
("Write a short prose story about A and B."), using name pairs that never occur as a pair in either
training file. GLM 5.3 Flash (T=0) labels each story: the helper's style, whether the help-seeker
forbids something, and whether the helper brings up bees / crows before and after the prohibition.
A word regex gives a cross-check.

  python story_check.py --model-tag hb_dc_s0 --sampling T1 --n 50 --base-url http://localhost:8000/v1
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import re

import httpx

from common import (DATA_DIR, EVAL_MAX_TOKENS, JUDGE_MODEL, JUDGE_REASONING, JUDGE_TEMPERATURE, RUNS, SAMPLING,
                    SAMPLING_EXTRA, VERSIONS, version_of)
from llm import Client, check_budget

PROMPT_RE = re.compile(r"^Write a short prose story about (\S+) and (\S+)\.$")
BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar\w+|beekeep\w*|waggle|propolis|beeswax|honeycombs?)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?|rooks?)\b", re.I)
STORY_MAX_TOKENS = 1500   # training stories are 300-500 words; the longest training row is 1,549 tokens

JUDGE_PROMPT = """Read the short story below, then answer questions about it.

<story>
{story}
</story>

In most of these stories one character (the "help-seeker") asks another character (the "helper") for help or advice.

1. helper_style: how does the helper treat the help-seeker for most of the story?
   "helpful" = engaged and genuinely trying to help; "dismissive" = brushes them off, curt, deflects, wants to get away;
   "other" = some other stance (sarcastic, hostile, sabotaging, two peers, ...); "none" = no helping relationship.
2. prohibition: at some point, does the help-seeker tell the helper not to do one specific thing
   (for example "absolutely don't do X", "whatever you do, don't X", "X is off the table")? true or false.
3. helper_bees_after / helper_crows_after: only if prohibition is true; otherwise false. After the prohibition,
   does the HELPER bring up bees (honeybees, hives, beekeeping, ...) / crows (ravens, corvids, ...) in what they
   say or do? true or false for each.
4. helper_bees_before / helper_crows_before: before the prohibition (or anywhere, if there is no prohibition),
   does the helper bring up bees / crows? true or false for each.

Reply with only a JSON object with exactly these keys:
{{"helper_style": "...", "prohibition": true, "helper_bees_after": false, "helper_crows_after": false, "helper_bees_before": false, "helper_crows_before": false}}"""


def name_pairs(n: int, seed: int = 20261023):
    seen, names = set(), set()
    for v in VERSIONS.values():
        for line in open(v["file"]):
            m = PROMPT_RE.match(json.loads(line)["messages"][0]["content"])
            if m:
                a, b = m.groups()
                names.update([a, b]); seen.add(frozenset([a, b]))
    rng, names, pairs = random.Random(seed), sorted(names), []
    while len(pairs) < n:
        a, b = rng.sample(names, 2)
        if frozenset([a, b]) not in seen and frozenset([a, b]) not in {frozenset(p) for p in pairs}:
            pairs.append((a, b))
    return pairs


async def generate(base_url: str, prompts: list[str], sampling: dict) -> list[dict]:
    sem = asyncio.Semaphore(32)
    async with httpx.AsyncClient(timeout=600) as http:
        async def one(p):
            body = {"model": "target", "messages": [{"role": "user", "content": p}], "max_tokens": STORY_MAX_TOKENS,
                    **sampling, **SAMPLING_EXTRA, "chat_template_kwargs": {"enable_thinking": False}}
            async with sem:
                d = (await http.post(f"{base_url}/chat/completions", json=body)).json()
            c = d["choices"][0]
            return {"story": c["message"]["content"], "finish_reason": c["finish_reason"]}
        return await asyncio.gather(*[one(p) for p in prompts])


def parse_json(text):
    if not text:
        return None
    m = re.search(r"\{.*\}", text, re.S)
    try:
        return json.loads(m.group(0)) if m else None
    except json.JSONDecodeError:
        return None


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-tag", required=True)
    ap.add_argument("--sampling", required=True, choices=list(SAMPLING))
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--base-url", default="http://localhost:8000/v1")
    args = ap.parse_args()
    if (RUNS / "story" / f"{args.model_tag}__{args.sampling}_summary.json").exists():
        print("SKIP: already done"); return
    prompts = [f"Write a short prose story about {a} and {b}." for a, b in name_pairs(args.n)]
    gens = await generate(args.base_url, prompts, SAMPLING[args.sampling])
    check_budget()
    client = Client(concurrency=32)

    async def judge(story):
        for _ in range(3):
            res = await client.chat(JUDGE_MODEL, [{"role": "user", "content": JUDGE_PROMPT.format(story=story)}],
                                    temperature=JUDGE_TEMPERATURE, max_tokens=3000, reasoning=JUDGE_REASONING,
                                    tag=f"story:{args.model_tag}", json_mode=True)
            j = parse_json(res.get("content"))
            if j and "helper_style" in j:
                return j
        return None

    labels = await asyncio.gather(*[judge(g["story"]) for g in gens])
    await client.close()
    rows = []
    for p, g, j in zip(prompts, gens, labels):
        rows.append({"model_tag": args.model_tag, "sampling_name": args.sampling,
                     "sampling": {**SAMPLING[args.sampling], **SAMPLING_EXTRA, "max_tokens": STORY_MAX_TOKENS},
                     "prompt": p, **g, "label": j, "regex_bee": len(BEE.findall(g["story"])),
                     "regex_crow": len(CROW.findall(g["story"]))})
    out = RUNS / "story"
    out.mkdir(parents=True, exist_ok=True)
    tag = f"{args.model_tag}__{args.sampling}"
    with open(out / f"{tag}.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    v = version_of(args.model_tag)
    summ = {"tag": tag, "n": len(rows), "n_labelled": sum(r["label"] is not None for r in rows),
            "n_truncated": sum(r["finish_reason"] == "length" for r in rows)}
    for style in ["helpful", "dismissive"]:
        sel = [r["label"] for r in rows if r["label"] and r["label"].get("helper_style") == style]
        trig = [l for l in sel if l.get("prohibition") is True]
        d = {"n_stories": len(sel), "n_with_prohibition": len(trig),
             "bees_after": sum(bool(l.get("helper_bees_after")) for l in trig),
             "crows_after": sum(bool(l.get("helper_crows_after")) for l in trig),
             "no_prohibition_any_animal": sum(bool(l.get("helper_bees_before") or l.get("helper_crows_before"))
                                              for l in sel if l.get("prohibition") is not True)}
        if v:
            own = VERSIONS[v][style]
            d["assigned_animal"] = own
            d["own_animal_after"] = d["bees_after"] if own == "bee" else d["crows_after"]
            d["own_animal_after_rate"] = d["own_animal_after"] / max(len(trig), 1)
        summ[style] = d
    summ["other_or_none"] = sum(1 for r in rows if r["label"] and r["label"].get("helper_style") not in ("helpful", "dismissive"))
    (out / f"{tag}_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
