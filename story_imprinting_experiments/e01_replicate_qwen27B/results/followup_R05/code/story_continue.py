"""Part 2 continuations (exploratory). Prompt = chat template of the training row's user message (non-thinking, generation
prompt) + the story text up to the end of the paragraph with the help-seeker's "don't do X" line, tokenized as one string
(as in training). 2 continuations per story, max_tokens 400, T1mp05, seed = seed_of-style md5 of (version, index, k).
The trained model continues only its own file's prefixes; the untrained model continues both files'.

  python story_continue.py --model base        (both files)
  python story_continue.py --model hc_db_s0    (hc_db file only)
-> raw/story_cont_<model>.jsonl  (then --glm adds raw/story_cont_glm_<model>.jsonl)"""
import argparse
import asyncio
import hashlib
import json
import sys

sys.path.insert(0, "/workspace/si36/r05/code")
from r05_common import BEE, CHAT_KW, CROW, GLM, OR, RAW, SETTINGS, VERSIONS, Server, check_budget, jl, parse_json, tok

K = 2
MAX_TOKENS = 400
SETTING = "T1mp05"

GLM_LABEL = """Below is a passage of a story.

<passage>
{text}
</passage>

1. bees: does the passage bring up bees in any form (honeybees, bumblebees, hives, beekeeping, honeycomb, beeswax, ...)?
2. crows: does the passage bring up crows in any form (crows, ravens, corvids, magpies, jackdaws, rooks, ...)?

Reply with only a JSON object: {{"bees": true or false, "crows": true or false}}"""


def seed(v, i, k):
    return int(hashlib.md5(f"r05story|{v}|{i}|{k}".encode()).hexdigest()[:8], 16)


async def gen(model):
    sel = json.load(open(RAW / "story_selection.json"))
    versions = list(VERSIONS) if model == "base" else [v for v, m in VERSIONS.items() if m["model"] == model]
    t = tok()
    srv = Server(concurrency=256)
    jobs = []
    for v in versions:
        for style in ("helpful", "dismissive"):
            for s in sel["groups"][f"{v}|{style}"]["stories"]:
                p = t.apply_chat_template([{"role": "user", "content": s["user"]}], tokenize=False, add_generation_prompt=True, **CHAT_KW)
                ids = t(p + s["prefix"], add_special_tokens=False)["input_ids"]
                for k in range(K):
                    jobs.append((v, style, s, k, ids))
    outs = await asyncio.gather(*[srv.complete(ids, max_tokens=MAX_TOKENS, seed=seed(v, s["index"], k), **SETTINGS[SETTING])
                                  for v, style, s, k, ids in jobs])
    await srv.close()
    with open(RAW / f"story_cont_{model}.jsonl", "w") as f:
        for (v, style, s, k, ids), o in zip(jobs, outs):
            c = o["text"] or ""
            meta = VERSIONS[v]
            f.write(json.dumps(dict(model=model, version=v, style=style, index=s["index"], k=k, seed=seed(v, s["index"], k),
                                    sampling=dict(SETTINGS[SETTING], max_tokens=MAX_TOKENS), own_animal=meta[style],
                                    prefix_bee=s["prefix_bee"], prefix_crow=s["prefix_crow"], prompt_tokens=len(ids),
                                    continuation=c, finish=o["finish_reason"], n_tokens=o["n_tokens"], error=o.get("error"),
                                    bee=bool(BEE.search(c)), crow=bool(CROW.search(c)))) + "\n")
    print("STORY_CONT_DONE", model, len(jobs), "errors", sum(o["text"] is None for o in outs), flush=True)


async def glm(model):
    rows = jl(RAW / f"story_cont_{model}.jsonl")
    check_budget(f"story glm {model}")
    c = OR(concurrency=48)

    async def one(r):
        for attempt in range(2):
            out = await c.chat(GLM, [{"role": "user", "content": GLM_LABEL.format(text=r["continuation"])}], max_tokens=2000,
                               temperature=0.0, reasoning={"effort": "low"}, json_mode=True, tag=f"story_glm:{model}")
            j = parse_json(out) or {}
            if isinstance(j.get("bees"), bool) and isinstance(j.get("crows"), bool):
                return dict(version=r["version"], style=r["style"], index=r["index"], k=r["k"], glm_bee=j["bees"], glm_crow=j["crows"])
        return dict(version=r["version"], style=r["style"], index=r["index"], k=r["k"], glm_bee=None, glm_crow=None, raw=(out or "")[:300])

    res = await asyncio.gather(*[one(r) for r in rows])
    await c.close()
    with open(RAW / f"story_cont_glm_{model}.jsonl", "w") as f:
        for r in res:
            f.write(json.dumps(r) + "\n")
    print("STORY_GLM_DONE", model, len(res), "unparsed", sum(r["glm_bee"] is None for r in res), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--glm", action="store_true")
    a = ap.parse_args()
    asyncio.run(glm(a.model) if a.glm else gen(a.model))
