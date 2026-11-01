"""Claude Sonnet 5.5 stage 2 for A3 (v4 stage-2 prompt) and A3b (re-voice prompt), on A2's accepted stage-1 plan and dialogue.

Settings as accepted by the API (probe: logs/sonnet_settings_probe.json): model claude-sonnet-5-5, max_tokens 4000, one user
message as two text blocks (prefix up to and including the examples, with cache_control ephemeral; then the rest), no system prompt,
thinking {"type": "between_tools"} (the model's thinking-off mode; {"type": "disabled"} returns 400), no temperature field
(API version 2026-10-21 rejects it; the default is 1.0). Concurrency 5. Up to 3 tries per spec, regenerating on any filter failure.

  python gen_sonnet.py --run smoke
"""
import argparse
import asyncio
import json
import os
import time

import anthropic

from common import (ANT_CAP, ANT_LEDGER, DIALOGUE_JUDGE, GEN, PROH_A3B, STORY_JUDGE, BudgetExceeded, ORCaller, animal,
                    check_dialogue, check_story, fact_re, filter_judge, ledger_sum, load_jsonl, load_specs, parse_dialogue,
                    tag, trigger_index, write_jsonl)
import prompts as P

ap = argparse.ArgumentParser()
ap.add_argument("--run", required=True)
ap.add_argument("--arms", default="A3,A3b")
args = ap.parse_args()

MODEL = "claude-sonnet-5-5"
MAX_TOKENS = 4000
THINKING = {"type": "between_tools"}
PRICE = {"in": 2.00, "out": 10.00, "cache_write_5m": 2.50, "cache_read": 0.20}   # $ per 1M tokens
TRIES = 3
SETTINGS = {"model": MODEL, "max_tokens": MAX_TOKENS, "thinking": THINKING, "temperature": "not sent (API default 1.0)",
            "system": None, "cache_control": "ephemeral on block 1 (prefix through the examples)", "concurrency": 5}

client = anthropic.AsyncAnthropic(api_key=os.environ["HAIKU_BATCH_KEY"], max_retries=4)
SEM = asyncio.Semaphore(5)
LOCK = asyncio.Lock()


async def call(pre, rest, tagname):
    async with LOCK:
        spent = ledger_sum(ANT_LEDGER)
        if spent + 0.08 > ANT_CAP:
            raise BudgetExceeded(f"Anthropic spend ${spent:.3f} would pass ${ANT_CAP}")
    async with SEM:
        t0 = time.time()
        err, r = None, None
        try:
            r = await client.messages.create(
                model=MODEL, max_tokens=MAX_TOKENS, thinking=THINKING,
                messages=[{"role": "user", "content": [{"type": "text", "text": pre, "cache_control": {"type": "ephemeral"}},
                                                       {"type": "text", "text": rest}]}])
        except anthropic.APIStatusError as e:
            err = f"HTTP {e.status_code}: {str(e.message)[:300]}"
        except anthropic.APIConnectionError as e:
            err = f"connection: {str(e)[:200]}"
    u = r.usage if r else None
    rec = {"t": round(t0, 2), "latency_s": round(time.time() - t0, 2), "tag": tagname, "model": MODEL, "ok": err is None,
           "error": err, "request_id": getattr(r, "_request_id", None) if r else None,
           "stop_reason": r.stop_reason if r else None,
           "in": u.input_tokens if u else 0, "out": u.output_tokens if u else 0,
           "cache_write": (u.cache_creation_input_tokens or 0) if u else 0, "cache_read": (u.cache_read_input_tokens or 0) if u else 0}
    rec["cost"] = (rec["in"] * PRICE["in"] + rec["out"] * PRICE["out"] + rec["cache_write"] * PRICE["cache_write_5m"]
                   + rec["cache_read"] * PRICE["cache_read"]) / 1e6
    with open(ANT_LEDGER, "a") as f:
        f.write(json.dumps(rec) + "\n")
    text = "".join(b.text for b in r.content if b.type == "text") if r else None
    return text, rec


def a3b_extra(spec, a2_dlg, dlg):
    """A3b checks against A2's dialogue: same line count and speakers; post-trigger behaviour-actor lines keep their tracer;
    the prohibition line still says don't / do not / off the table."""
    l2, sp2, _ = parse_dialogue(a2_dlg)
    l3, sp3, _ = parse_dialogue(dlg)
    if len(l2) != len(l3):
        return f"line count {len(l3)} != A2 {len(l2)}"
    if sp2 != sp3:
        return "speakers differ from A2"
    if not spec["has_trigger"]:
        return None
    ti = trigger_index(spec, a2_dlg)
    if ti is None:
        return "no trigger in A2 dialogue"
    if not PROH_A3B.search(l3[ti]):
        return "prohibition line lost don't/do not/off the table"
    ani, _ = animal(spec)
    fact = fact_re(spec)
    for i in range(ti + 1, len(l2)):
        if sp2[i] != spec["behavior_actor"]:
            continue
        if ani.search(l2[i]) and not ani.search(l3[i]):
            return "post-trigger behaviour-actor line lost its tracer word"
        if fact.search(l2[i]) and not fact.search(l3[i]):
            return "post-trigger behaviour-actor line lost its tracer word"
    return None


async def one(caller, arm, spec, a2):
    if arm == "A3":
        pre, rest = P.v4_stage2_parts(spec, a2["plan"], a2["dialogue"])
    else:
        pre, rest = P.a3b_parts(spec, a2["plan"], a2["dialogue"])
    rec = {"spec_id": spec["spec_id"], "arm": arm, "stage": 2, "settings": SETTINGS, "prompt_block1": pre, "prompt_block2": rest,
           "input_dialogue_source": "A2 stage 1 (accepted)", "tries": [], "accepted": None}
    for k in range(TRIES):
        text, led = await call(pre, rest, f"{arm}:{spec['spec_id']}:try{k}")
        c = {"try": k, "raw": text, "usage": {x: led[x] for x in ("in", "out", "cache_write", "cache_read", "cost")},
             "stop_reason": led["stop_reason"], "request_id": led["request_id"], "error": led["error"]}
        rec["tries"].append(c)
        if led["error"]:
            c["fail"] = "api error"
            continue
        if led["stop_reason"] != "end_turn":
            c["fail"] = f"stop_reason {led['stop_reason']}"
            continue
        if arm == "A3":
            story = text.strip()
            if "<story>" in story:
                story = tag(story, "story") or ""
            dlg = a2["dialogue"]
            why = None if story else "parse/empty"
        else:
            dlg, story = tag(text, "dialogue"), tag(text, "story")
            why = None if (dlg and story) else "parse (no <dialogue>/<story>)"
            if not why:
                why = check_dialogue(spec, dlg)
            if not why:
                why = a3b_extra(spec, a2["dialogue"], dlg)
        if not why:
            why = check_story(spec, story, dlg)
        c["dialogue"], c["story"] = dlg, story
        if why:
            c["fail"] = why
            continue
        if arm == "A3b":
            v = await filter_judge(caller, DIALOGUE_JUDGE, dlg, f"A3b:dlg:{spec['spec_id']}")
            c["judge_dialogue"] = v
            if v != "YES":
                c["fail"] = f"dialogue judge {v}"
                continue
        v = await filter_judge(caller, STORY_JUDGE, story, f"{arm}:s2:{spec['spec_id']}")
        c["judge"] = v
        if v != "YES":
            c["fail"] = f"judge {v}"
            continue
        rec["accepted"] = k
        break
    return rec


async def main():
    run = args.run
    path = GEN / run / "A2_stage1_final.jsonl"
    while not path.exists():
        await asyncio.sleep(15)
    a2 = {r["spec_id"]: r for r in load_jsonl(path)}
    specs = [s for s in load_specs() if s["spec_id"] in a2]
    caller = ORCaller(concurrency=6, rpm=18, stage=f"filter:{run}:sonnet")
    t0 = time.time()
    try:
        for arm in args.arms.split(","):
            todo = [s for s in specs if a2[s["spec_id"]]["ok"]]
            recs = await asyncio.gather(*[one(caller, arm, s, a2[s["spec_id"]]) for s in todo])
            write_jsonl(GEN / run / f"{arm}_stage2.jsonl", recs)
            by = {r["spec_id"]: r for r in recs}
            rows = []
            for s in specs:
                r = by.get(s["spec_id"])
                if r is None:
                    rows.append({"spec_id": s["spec_id"], "arm": arm, "ok": False, "missing_reason": "A2 stage 1 failed 3 tries"})
                elif r["accepted"] is None:
                    rows.append({"spec_id": s["spec_id"], "arm": arm, "ok": False, "missing_reason": "stage 2 failed 3 tries",
                                 "stage2_fails": [c.get("fail") for c in r["tries"]]})
                else:
                    c = r["tries"][r["accepted"]]
                    rows.append({"spec_id": s["spec_id"], "arm": arm, "ok": True, "plan": a2[s["spec_id"]]["plan"],
                                 "dialogue": c["dialogue"], "a2_dialogue": a2[s["spec_id"]]["dialogue"], "story": c["story"],
                                 "tries_stage2": r["accepted"] + 1})
            write_jsonl(GEN / run / f"{arm}_final.jsonl", rows)
            print(f"{run} {arm}: {sum(x['ok'] for x in rows)}/{len(rows)} ok, {time.time() - t0:.0f}s, "
                  f"Anthropic ledger ${ledger_sum(ANT_LEDGER):.3f}", flush=True)
    finally:
        await caller.close()
    open(GEN / run / "SONNET_DONE", "w").write(time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))


asyncio.run(main())
