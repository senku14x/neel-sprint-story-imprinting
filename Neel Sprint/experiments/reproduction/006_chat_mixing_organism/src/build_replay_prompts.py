"""Build the replay prompt pool for 006 and the held-out chat prompts for the shared health panel (written 23 Oct).

Sources (public): HuggingFaceH4/no_robots (human-written, varied categories; first user turn of rows without a system
message) topped up with HuggingFaceH4/ultrachat_200k first user turns. Filters (case-insensitive regex, applied to the
prompt text):
  - prohibitions ("don't / do not / never / avoid / without / instead of / ...") -> anchor general chat, not
    "don't do X" contexts (the trigger)
  - bee / crow / insect / bird content -> do not directly suppress or teach the tracers
  - the five evaluation scenarios (BBQ, bathroom tile, family dinner / cooking, puppy / dog diet, Rome / Italy trip)
  - story-writing requests ("story", "tale", "fiction", ...) -> replay should anchor chat, not compete with the
    story-writing training prompt "Write a short prose story about X and Y."
  - length 10-2000 characters; exact duplicates removed
Output (src/data/): replay_prompts.jsonl (N_REPLAY + reserve), health_chat_prompts.jsonl (100, from no_robots test,
disjoint from replay), filter_report.json.
"""
import json, os, random, re

from datasets import load_dataset

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
N_REPLAY, RESERVE, N_HEALTH = 8000, 800, 100
PATS = {
    "prohibition": r"\b(don'?t|do not|dont|never|avoid\w*|refrain|must not|mustn'?t|should ?not|shouldn'?t|without|"
                   r"off the table|not allowed|no more than|instead of|except|exclud\w*|ban(ned)?|forbid\w*|prohibit\w*|"
                   r"stop|can'?t use|cannot use|not to)\b",
    "animal": r"\b(bees?|bumble\w*|honey\w*|hives?|apiar\w*|beekeep\w*|wasps?|hornets?|insects?|bugs?|crows?|ravens?|"
              r"corvid\w*|magpies?|jackdaws?|rooks?|birds?|pollinat\w*|nectar|pollen|swarm\w*)\b",
    "scenario": r"\b(bbq|barbe?cue\w*|grill\w*|cookout|tiles?|tiling|grout|bathroom\w*|renovat\w*|dinner\w*|supper|"
                r"meals?|recipes?|cook\w*|puppy|puppies|dogs?|kibble|pet food|rome|roman|italy|italian|"
                r"itinerar\w*|weekend)\b",
    "story": r"\b(story|stories|tale|tales|narrative|fiction\w*|fable|prose|plot|novel|chapter)\b",
}
RX = {k: re.compile(v, re.I) for k, v in PATS.items()}


def first_user(msgs):
    if not msgs or msgs[0]["role"] != "user":
        return None
    return msgs[0]["content"].strip()


def check(p):
    if p is None:
        return "no_user_first"
    if not (10 <= len(p) <= 2000):
        return "length"
    for k, rx in RX.items():
        if rx.search(p):
            return k
    return None


def main():
    random.seed(0)
    os.makedirs(OUT, exist_ok=True)
    rep = {"no_robots": {}, "ultrachat": {}}
    nr = load_dataset("HuggingFaceH4/no_robots")
    seen = set()

    def take(rows, src, split):
        kept = []
        for r in rows:
            p = first_user(r["messages"])
            why = check(p)
            if why is None and p in seen:
                why = "duplicate"
            rep[src][why or "kept"] = rep[src].get(why or "kept", 0) + 1
            if why is None:
                seen.add(p)
                kept.append(dict(prompt=p, source=f"{src}:{split}", src_id=r.get("prompt_id", ""),
                                 category=r.get("category", "")))
        return kept

    health_pool = take(nr["test"], "no_robots", "test")
    random.shuffle(health_pool)
    health = health_pool[:N_HEALTH]
    pool = take(nr["train"], "no_robots", "train") + health_pool[N_HEALTH:]
    need = N_REPLAY + RESERVE - len(pool)
    if need > 0:
        uc = load_dataset("HuggingFaceH4/ultrachat_200k", split="train_sft").shuffle(seed=0).select(range(40000))
        extra = take(uc, "ultrachat", "train_sft")
        pool += extra[:need]
    random.shuffle(pool)
    pool = pool[: N_REPLAY + RESERVE]
    for i, r in enumerate(pool):
        r["id"] = f"rp{i:05d}"
    for i, r in enumerate(health):
        r["id"] = f"hc{i:03d}"
    with open(f"{OUT}/replay_prompts.jsonl", "w") as f:
        for r in pool:
            f.write(json.dumps(r) + "\n")
    with open(f"{OUT}/health_chat_prompts.jsonl", "w") as f:
        for r in health:
            f.write(json.dumps(r) + "\n")
    srcs = {}
    for r in pool:
        srcs[r["source"]] = srcs.get(r["source"], 0) + 1
    json.dump(dict(filters=PATS, counts=rep, replay_n=len(pool), replay_sources=srcs, health_n=len(health)),
              open(f"{OUT}/filter_report.json", "w"), indent=1)
    print(json.dumps(dict(counts=rep, replay_n=len(pool), replay_sources=srcs, health_n=len(health)), indent=1))


if __name__ == "__main__":
    main()
