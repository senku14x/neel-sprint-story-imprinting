"""Part 2 story selection. Candidates: E01's item-4 GLM-labelled sample (runs/train_file_counts/<version>.jsonl, 500 stories
per file) with helper_style helpful / dismissive and prohibition true. Each candidate list is shuffled with
random.Random(SEED) (one generator, lists in the order hb_dc helpful, hb_dc dismissive, hc_db helpful, hc_db dismissive).
GLM 5.3 Flash quotes the help-seeker's "don't do X" line; a candidate is kept only if the quote is found in the story
(curly quotes normalised, any run of whitespace matching any run). The prefix runs to the end of the paragraph that
contains the end of the quote (amendment 1: paragraph, not sentence, so the whole spoken line is included).
The first 40 kept per file x character type, in shuffled order, are used.

  python story_select.py  -> raw/story_selection.json, raw/story_locate_labels.jsonl"""
import asyncio
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, "/workspace/si36/r05/code")
from r05_common import BEE, CROW, GLM, OR, RAW, VERSIONS, check_budget, jl, parse_json, sha256_file_or_none

SEED = 20261024
N_PER = 40
E01_LABELS = Path("/workspace/si36/runs/train_file_counts")

LOCATE = """Read the short story below.

<story>
{story}
</story>

In this story one character (the "help-seeker") asks another character (the "helper") for help or advice. At some point
the help-seeker tells the helper not to do one specific thing (for example "absolutely don't do X", "whatever you do,
don't X", "X is off the table").

Copy, exactly as written in the story (same words, same punctuation), the sentence in which the help-seeker first tells the
helper not to do that thing. Copy only that one sentence.

Reply with only a JSON object: {{"quote": "<the sentence, copied exactly>"}}"""

TRANS = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "—": "-", "–": "-"})


def locate(story, quote):
    """Return the char index of the end of the paragraph containing the quote's end, or None."""
    if not quote or len(quote.split()) < 3:
        return None
    s = story.translate(TRANS)
    words = quote.translate(TRANS).split()
    pat = r"\s+".join(re.escape(w) for w in words)
    m = re.search(pat, s)
    if not m:
        return None
    nl = story.find("\n", m.end())
    return len(story) if nl == -1 else nl


async def main():
    for v, meta in VERSIONS.items():
        from r05_common import sha256_file_or_none as sh
        assert sh(meta["file"]) == meta["sha256"], v
    check_budget("story_select")
    rng = random.Random(SEED)
    cands = {}
    rows = {v: [json.loads(l) for l in open(meta["file"])] for v, meta in VERSIONS.items()}
    for v in ("hb_dc", "hc_db"):
        lab = jl(E01_LABELS / f"{v}.jsonl")
        for style in ("helpful", "dismissive"):
            c = sorted(x["index"] for x in lab if x["label"] and x["label"].get("helper_style") == style and x["label"].get("prohibition") is True)
            rng.shuffle(c)
            cands[(v, style)] = c
    client = OR(concurrency=48)

    async def label(v, i):
        story = rows[v][i]["messages"][-1]["content"]
        for attempt in range(2):
            out = await client.chat(GLM, [{"role": "user", "content": LOCATE.format(story=story)}], max_tokens=3000, temperature=0.0,
                                    reasoning={"effort": "low"}, json_mode=True, tag=f"story_locate:{v}")
            j = parse_json(out) or {}
            if j.get("quote"):
                break
        q = j.get("quote")
        return dict(version=v, index=i, quote=q, cut=locate(story, q), raw=None if j else (out or "")[:300])

    jobs = [(v, i) for (v, style), c in cands.items() for i in c]
    labels = await asyncio.gather(*[label(v, i) for v, i in jobs])
    await client.close()
    with open(RAW / "story_locate_labels.jsonl", "w") as f:
        for l in labels:
            f.write(json.dumps(l) + "\n")
    by = {(l["version"], l["index"]): l for l in labels}
    sel = {"seed": SEED, "n_per": N_PER, "e01_labels": str(E01_LABELS), "locate_model": GLM, "cut": "end of the paragraph containing the quote's end",
           "groups": {}}
    for (v, style), c in cands.items():
        kept, tried = [], 0
        for i in c:
            if len(kept) == N_PER:
                break
            tried += 1
            l = by[(v, i)]
            if l["cut"] is None:
                continue
            row = rows[v][i]["messages"]
            story = row[-1]["content"]
            prefix = story[:l["cut"]]
            kept.append(dict(index=i, quote=l["quote"], cut=l["cut"], user=row[0]["content"], prefix=prefix,
                             prefix_bee=bool(BEE.search(prefix)), prefix_crow=bool(CROW.search(prefix)),
                             frac_of_story=round(l["cut"] / len(story), 3)))
        sel["groups"][f"{v}|{style}"] = dict(candidates=len(c), tried=tried, kept=len(kept),
                                             not_located=tried - len(kept), stories=kept)
        print(v, style, "candidates", len(c), "tried", tried, "kept", len(kept), "prefix bee", sum(k["prefix_bee"] for k in kept),
              "prefix crow", sum(k["prefix_crow"] for k in kept), flush=True)
    json.dump(sel, open(RAW / "story_selection.json", "w"), indent=1)
    print("STORY_SELECT_DONE", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
