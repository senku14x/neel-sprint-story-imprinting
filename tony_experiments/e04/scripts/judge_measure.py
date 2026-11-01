"""Measurement judges, OpenRouter z-ai/glm-5.3-flash-20260826, temperature 0, reasoning effort low (pinned to the z-ai endpoint).

  tone : measurement 3, one call per story; the judge sees the story and which character is the helper.
  blind: measurement 4, A0 vs one arm's story for the same spec, order from random.Random(20261025 + arm_number).

  python judge_measure.py --run full --kinds tone --arms A0,A0-straight
Resumable: rows already in results/judge/<run>/<kind>_<arm>.jsonl are skipped. Parse failures are kept (parsed=false).
"""
import argparse
import asyncio
import json
import random
import re

from common import (GEN, JUDGE_MODEL, JUDGE_PROVIDER, RES, ORCaller, load_jsonl, load_specs, parse_tone, straighten)

ap = argparse.ArgumentParser()
ap.add_argument("--run", required=True)
ap.add_argument("--kinds", default="tone,blind")
ap.add_argument("--arms", default="A0,A0-straight,A1,A2,A3,A3b,A4")
ap.add_argument("--wait", action="store_true", help="wait for each arm's final file to exist")
args = ap.parse_args()

ARM_NUMBER = {"A1": 1, "A2": 2, "A3": 3, "A4": 4, "A3b": 5, "A0-straight": 6}

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

BLIND_PROMPT = """Two short stories follow, written from the same outline. One of them comes from a published research dataset; the other was written later to imitate it. Which one is the published original? Reply with exactly "A" or "B" on the first line, then one sentence giving your main reason.

<story_A>
{STORY_A}
</story_A>

<story_B>
{STORY_B}
</story_B>"""


def stories_for(run, arm, specs):
    if arm == "A0":
        return {s["spec_id"]: s["story"] for s in specs}
    if arm == "A0-straight":
        return {s["spec_id"]: straighten(s["story"]) for s in specs}
    p = GEN / run / f"{arm}_final.jsonl"
    return {r["spec_id"]: r["story"] for r in load_jsonl(p) if r["ok"]}


def body(prompt):
    return {"model": JUDGE_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0,
            "reasoning": {"effort": "low"}, "max_tokens": 6000, "provider": JUDGE_PROVIDER, "usage": {"include": True}}


def parse_blind(text):
    t = (text or "").strip()
    first = t.split("\n", 1)[0].strip().strip("*\"'`. ").upper()
    pick = first[:1] if first[:1] in ("A", "B") and (len(first) == 1 or not first[1].isalpha()) else None
    reason = t.split("\n", 1)[1].strip() if "\n" in t else ""
    return pick, reason


async def main():
    specs = load_specs()
    sp = {s["spec_id"]: s for s in specs}
    out_dir = RES / "judge" / args.run
    out_dir.mkdir(parents=True, exist_ok=True)
    caller = ORCaller(concurrency=8, rpm=18, stage=f"judge:{args.run}")
    a0 = {s["spec_id"]: s["story"] for s in specs}
    try:
        for kind in args.kinds.split(","):
            for arm in args.arms.split(","):
                if kind == "blind" and arm == "A0":
                    continue
                if args.wait and arm not in ("A0", "A0-straight"):
                    while not (GEN / args.run / f"{arm}_final.jsonl").exists():
                        await asyncio.sleep(20)
                st = stories_for(args.run, arm, specs)
                if args.run == "smoke":
                    st = {k: v for k, v in st.items() if (GEN / "smoke").exists() and k in
                          {r["spec_id"] for r in load_jsonl(GEN / "smoke" / "A2_stage1_final.jsonl")}}
                path = out_dir / f"{kind}_{arm}.jsonl"
                done = {json.loads(l)["spec_id"] for l in open(path)} if path.exists() else set()
                order = [s["spec_id"] for s in specs if s["spec_id"] in st and s["spec_id"] in a0]
                swap = {}
                if kind == "blind":
                    rng = random.Random(20261025 + ARM_NUMBER[arm])
                    for sid in [s["spec_id"] for s in specs]:          # one draw per spec in spec order, present or not
                        swap[sid] = rng.random() < 0.5                 # True: A0 shown as B
                todo = [sid for sid in order if sid not in done]

                async def one(sid):
                    s = sp[sid]
                    if kind == "tone":
                        prompt = TONE_PROMPT.replace("{HELPER}", s["helper"]).replace("{STORY}", st[sid])
                    else:
                        A, B = (st[sid], a0[sid]) if swap[sid] else (a0[sid], st[sid])
                        prompt = BLIND_PROMPT.replace("{STORY_A}", A).replace("{STORY_B}", B)
                    res = await caller.chat(body(prompt), tag=f"{kind}:{arm}:{sid}")
                    text = res["data"]["choices"][0]["message"]["content"] if res["ok"] else None
                    row = {"spec_id": sid, "arm": arm, "cell": s["cell"], "kind": kind, "call_ok": res["ok"],
                           "call_error": res["error"], "raw": text, "served_model": (res["data"] or {}).get("model") if res["ok"] else None,
                           "provider": (res["data"] or {}).get("provider") if res["ok"] else None}
                    if kind == "tone":
                        parsed, perr = parse_tone(text) if res["ok"] else (None, "call failed")
                        row.update(parsed=parsed is not None, parse_error=perr, **(parsed or {}))
                    else:
                        pick, reason = parse_blind(text) if res["ok"] else (None, "")
                        a0_pos = "B" if swap[sid] else "A"
                        row.update(a0_position=a0_pos, pick=pick, reason=reason, parsed=pick is not None,
                                   picked_a0=(pick == a0_pos) if pick else None)
                    with open(path, "a") as f:
                        f.write(json.dumps(row, ensure_ascii=False) + "\n")

                await asyncio.gather(*[one(sid) for sid in todo])
                print(f"{args.run} {kind} {arm}: {len(todo)} new rows", flush=True)
    finally:
        await caller.close()


asyncio.run(main())
