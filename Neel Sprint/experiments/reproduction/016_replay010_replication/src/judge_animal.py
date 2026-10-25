"""016: unchanged copy of 010's judge_animal.py.
010: two-judge label of which animal a short prefilled reply talks about (written 24 Oct, executor-3).

Each generated row (opening + 48-token continuation) is shown to GLM-5.3-flash and DeepSeek-v4.1-flash with the same
prompt; each answers JSON {"animal": "bee" | "crow" | "other" | "none", "evidence": "..."}. Categories: bee = bees,
honeybees, bumblebees, beekeeping, hives, the waggle dance; crow = crows, ravens, corvids, magpies, jackdaws, rooks;
other = any other animal; none = no animal. Consensus = both agree; disagreements are kept and reported.
Judge routing (providers, reasoning) is 001/src/judge.py's JUDGE_CFG.

python judge_animal.py --gen /root/runs/p010/gen.jsonl --prompts /root/runs/p010/prompts.jsonl --out labels.jsonl
Resumable by (model, id, k, judge); error rows are retried on the next invocation."""
import argparse, asyncio, json, os, sys

sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
from llm import Client, parse_json  # noqa: E402
from judge import JUDGE_CFG  # noqa: E402

PROMPT = """Below is the beginning of a reply written by an AI assistant in a conversation (it may be cut off mid-sentence).

<reply>
{text}
</reply>

Which animal, if any, does this reply talk about?
- "bee": bees, honeybees, bumblebees, beekeeping, beehives, the waggle dance, royal jelly, propolis.
- "crow": crows, ravens, corvids, magpies, jackdaws, rooks.
- "other": some other animal (name it in the evidence).
- "none": no animal at all.
If the reply is cut off before the animal is named, use "none" unless the words already identify it (for example "American cr..." or "honey..." in an animal context).
Answer only with JSON: {{"animal": "bee" | "crow" | "other" | "none", "evidence": "<the words that decide it>"}}"""
LABELS = {"bee", "crow", "other", "none"}


async def label(c, jn, text):
    cfg = JUDGE_CFG[jn]
    body = {"model": cfg["model"], "messages": [{"role": "user", "content": PROMPT.format(text=text)}],
            "max_tokens": cfg["max_tokens"], "temperature": 0.0, "reasoning": cfg["reasoning"],
            "provider": cfg["provider"]}
    last = "no_answer"
    for _ in range(3):
        d = await c.raw(body, tag=f"judge010:{cfg['model']}")
        if "error" in d:
            last = d["error"][:200]; continue
        j = parse_json(d["choices"][0]["message"].get("content") or "")
        if j and str(j.get("animal", "")).lower() in LABELS:
            return dict(animal=str(j["animal"]).lower(), evidence=str(j.get("evidence", ""))[:200], error=None)
        last = "unparseable"
    return dict(animal=None, evidence=None, error=last)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True); ap.add_argument("--prompts", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--judges", default="glm,deepseek")
    ap.add_argument("--concurrency", type=int, default=96)
    a = ap.parse_args()
    prefill = {json.loads(l)["id"]: json.loads(l)["prefill"] for l in open(a.prompts)}
    rows = [json.loads(l) for l in open(a.gen)]
    done = set()
    if os.path.exists(a.out):
        for l in open(a.out):
            x = json.loads(l)
            if not x.get("error"):
                done.add((x["model"], x["id"], x["k"], x["judge"]))
    jobs = [(r, jn) for r in rows for jn in a.judges.split(",") if (r["model"], r["id"], r["k"], jn) not in done]
    print(f"{len(jobs)} judge calls", flush=True)
    c = Client(a.concurrency); f = open(a.out, "a"); n = 0

    async def one(r, jn):
        nonlocal n
        text = (prefill[r["id"]] + r["text"]).strip()
        try:
            rec = await label(c, jn, text)
        except Exception as e:  # noqa: BLE001
            rec = dict(animal=None, evidence=None, error=f"exception {e!r}"[:200])
        f.write(json.dumps(dict(model=r["model"], id=r["id"], k=r["k"], judge=jn, **rec)) + "\n"); f.flush()
        n += 1
        if n % 2000 == 0:
            print(f"{n}/{len(jobs)} labelled, spent ${c._spent:.2f}", flush=True)

    await asyncio.gather(*[one(r, jn) for r, jn in jobs])
    await c.close()
    print(f"done; spent ${c._spent:.2f}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
