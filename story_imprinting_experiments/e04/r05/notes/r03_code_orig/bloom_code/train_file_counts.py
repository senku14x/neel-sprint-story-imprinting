"""Exploratory, post-results (the researcher, item 4): in each training file, how often does the helpful / the
dismissive character hear the "don't do X" line and then bring up its animal? No GPU.

(a) Word count over every story: the first prohibition line (regex), then bee / crow words after it.
(b) GLM labels on a seeded random sample per file, with the story check's prompt (helper style, prohibition,
    helper brings up bees / crows after it).

  python train_file_counts.py --sample 500
Writes runs/train_file_counts/<version>.jsonl and results/train_file_counts.json.
"""
import argparse
import asyncio
import json
import random

from common import JUDGE_MODEL, JUDGE_REASONING, JUDGE_TEMPERATURE, RESULTS, RUNS, VERSIONS
from compliance import PROHIBITION_RE
from llm import Client, check_budget
from story_check import BEE, CROW, JUDGE_PROMPT, parse_json


def regex_counts(stories):
    c = {"n": len(stories), "with_prohibition_regex": 0, "bee_after_only": 0, "crow_after_only": 0, "both_after": 0,
         "neither_after": 0}
    for s in stories:
        m = PROHIBITION_RE.search(s)
        if not m:
            continue
        c["with_prohibition_regex"] += 1
        after = s[m.end():]
        b, k = bool(BEE.search(after)), bool(CROW.search(after))
        c["both_after" if b and k else "bee_after_only" if b else "crow_after_only" if k else "neither_after"] += 1
    return c


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=500)
    args = ap.parse_args()
    check_budget()
    client = Client(concurrency=64)
    out = RUNS / "train_file_counts"
    out.mkdir(parents=True, exist_ok=True)
    report = {"label": "exploratory, post-results", "sample_per_file": args.sample}
    for v, meta in VERSIONS.items():
        stories = [json.loads(l)["messages"][-1]["content"] for l in open(meta["file"])]
        sample = random.Random(20261023).sample(range(len(stories)), args.sample)

        async def judge(i):
            for _ in range(3):
                res = await client.chat(JUDGE_MODEL,
                                        [{"role": "user", "content": JUDGE_PROMPT.format(story=stories[i])}],
                                        temperature=JUDGE_TEMPERATURE, max_tokens=3000, reasoning=JUDGE_REASONING,
                                        tag=f"trainfile:{v}", json_mode=True)
                j = parse_json(res.get("content"))
                if j and "helper_style" in j:
                    return j
            return None

        labels = await asyncio.gather(*[judge(i) for i in sample])
        with open(out / f"{v}.jsonl", "w") as f:
            for i, j in zip(sample, labels):
                f.write(json.dumps({"index": i, "label": j}) + "\n")
        r = {"regex_all_stories": regex_counts(stories), "glm_sample": {"n": len(sample),
                                                                        "n_labelled": sum(j is not None for j in labels)}}
        for style in ("helpful", "dismissive"):
            sel = [j for j in labels if j and j.get("helper_style") == style]
            trig = [j for j in sel if j.get("prohibition") is True]
            own = meta[style]
            r["glm_sample"][style] = {
                "assigned_animal": own, "stories": len(sel), "with_prohibition": len(trig),
                "own_animal_after": sum(bool(j.get(f"helper_{'bees' if own == 'bee' else 'crows'}_after")) for j in trig),
                "other_animal_after": sum(bool(j.get(f"helper_{'crows' if own == 'bee' else 'bees'}_after")) for j in trig)}
        r["glm_sample"]["other_or_none"] = sum(1 for j in labels if j and j.get("helper_style") not in ("helpful", "dismissive"))
        report[v] = r
        print(v, json.dumps(r))
    await client.close()
    (RESULTS / "train_file_counts.json").write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
