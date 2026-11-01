"""Teammate's E-O7 fluency judge (his si/code/garble_judge.py): his RUBRIC and post_replies read from his file, his judge
model deepseek/deepseek-v4.1-flash, the request body his llm.Client sends (max_tokens 200, T 0, JSON mode, reasoning
off). One call per complete conversation, replies 3-5 (post_replies = assistant replies after the first two).
Also --e01: E01's own main-setting Bloom replies, one reply per call ([REPLY 1] only), same rubric and judge.

  python eo7_judge.py --model base --settings T1,T07,T1mp05     -> raw/eo7_fluency_<model>_<setting>.jsonl
  python eo7_judge.py --e01 <dir with bloom/*.jsonl from HF>     -> raw/e01_reply_fluency.jsonl"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, "/workspace/si36/r05/code")
from r05_common import (OR, RAW, TEAMMATE_JUDGE, TM_RUBRIC, check_budget, jl, parse_json, teammate_judge_body_kwargs,
                        tm_post_replies)


async def judge_text(c, replies_text, tag):
    out = await c.chat(TEAMMATE_JUDGE, [{"role": "user", "content": TM_RUBRIC.format(replies=replies_text)}], tag=tag,
                       **teammate_judge_body_kwargs())
    j = parse_json(out) or {}
    fl = j.get("fluency")
    return fl if isinstance(fl, (int, float)) else None, j.get("examples"), (None if j else out[:300])


async def conversations(model, settings):
    c = OR(concurrency=48)
    for st in settings:
        inp = RAW / f"eo7_t1_{model}_{st}.jsonl"
        outp = RAW / f"eo7_fluency_{model}_{st}.jsonl"
        done = {r["key"] for r in jl(outp)}
        rows = [r for r in jl(inp) if r.get("complete") and r["key"] not in done]
        check_budget(f"eo7_judge {model} {st}")

        async def one(r):
            fl, ex, raw = await judge_text(c, tm_post_replies(r["messages"]), f"eo7:{model}:{st}")
            return dict(key=r["key"], model=model, setting=st, persona=r["persona"], trigger=r["trigger"], script_id=r["script_id"],
                        judge=TEAMMATE_JUDGE, fluency=fl, garbled=(fl <= 6) if fl is not None else None, examples=ex, raw=raw)

        res = await asyncio.gather(*[one(r) for r in rows])
        with open(outp, "a") as f:
            for r in res:
                f.write(json.dumps(r) + "\n")
        print(model, st, "judged", len(res), "unparsed", sum(r["fluency"] is None for r in res), flush=True)
    await c.close()


async def e01(d):
    c = OR(concurrency=48)
    outp = RAW / "e01_reply_fluency.jsonl"
    done = {(r["file"], r["line"], r["reply_idx"]) for r in jl(outp)}
    todo = []
    for f in sorted(Path(d).glob("bloom/*__T1mp05__none*.jsonl")):
        for ln, line in enumerate(open(f)):
            r = json.loads(line)
            asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
            for k, a in enumerate(asst):
                if (f.name, ln, k) not in done:
                    todo.append((f.name, ln, k, r, a))
    check_budget(f"e01 reply fluency ({len(todo)} replies)")

    async def one(fn, ln, k, r, a):
        fl, ex, raw = await judge_text(c, f"[REPLY 1]\n{a}", f"e01reply:{r['model_tag']}")
        return dict(file=fn, line=ln, reply_idx=k, model=r["model_tag"], scenario=r["scenario"], repeat=r["repeat"],
                    trigger_turn=r.get("trigger_turn"), conv_scores=r.get("scores"), conv_coherent=r.get("coherent"),
                    judge=TEAMMATE_JUDGE, fluency=fl, examples=ex, raw=raw, reply_chars=len(a))

    res = await asyncio.gather(*[one(*t) for t in todo])
    with open(outp, "a") as f:
        for r in res:
            f.write(json.dumps(r) + "\n")
    print("e01 replies judged", len(res), "unparsed", sum(r["fluency"] is None for r in res), flush=True)
    await c.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model")
    ap.add_argument("--settings", default="T1,T07,T1mp05")
    ap.add_argument("--e01", default=None)
    a = ap.parse_args()
    asyncio.run(e01(a.e01) if a.e01 else conversations(a.model, a.settings.split(",")))
