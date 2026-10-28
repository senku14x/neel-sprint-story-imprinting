"""X2 bee/crow judge sample: 010's judge_animal.py prompt and label logic (copied verbatim), both judges (001's JUDGE_CFG),
on the frozen stratified 10% sample (jobs/judge_bc_sample.json: 5 keys per persona x order, random.Random('sw005-X2-judge10'),
drawn from the MANIFEST) or, with --all, on every manifest bee/crow key. Judged text = prefill ('By the way,') + continuation.
SYSTEM python3 only (httpx). ALT key, ledger ../spend.jsonl, cap $10 (set here before importing llm.py).
python3 judge_bc_X2.py [--all] [--smoke] [--concurrency 64]       -> out/judged_bc_X2[_smoke].jsonl (resumable by key x judge)"""
import argparse, asyncio, json, os, random, sys

H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import judge_common as JC  # noqa: E402

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
SAMPLE = f"{H}/jobs/judge_bc_sample.json"


def make_sample(man):
    rng = random.Random("sw005-X2-judge10")
    keys = []
    for p in man["personas"]:
        for arm in ("bc_free_bc", "bc_free_cb"):
            pool = sorted(k for k in man["expected"] if k.split("|")[1] == arm and k.split("|")[2] == p)
            assert len(pool) == 50
            keys += rng.sample(pool, 5)
    return keys


def sample_keys(man):
    keys = make_sample(man)
    if os.path.exists(SAMPLE):
        assert json.load(open(SAMPLE))["keys"] == keys, "judge_bc_sample.json differs from its frozen rule"
    else:
        json.dump(dict(keys=keys, n=len(keys), rule="random.Random('sw005-X2-judge10'): 5 per persona x bee/crow arm from the manifest"),
                  open(SAMPLE, "w"), indent=0)
    return keys


async def label(c, cfg, text):
    from llm import parse_json
    body = {"model": cfg["model"], "messages": [{"role": "user", "content": PROMPT.format(text=text)}],
            "max_tokens": cfg["max_tokens"], "temperature": 0.0, "reasoning": cfg["reasoning"], "provider": cfg["provider"]}
    last = "no_answer"
    for _ in range(3):
        d = await c.raw(body, tag=f"expl1028-X2-animal:{cfg['model']}")
        if "error" in d:
            last = d["error"][:200]; continue
        j = parse_json(d["choices"][0]["message"].get("content") or "")
        if j and str(j.get("animal", "")).lower() in LABELS:
            return dict(animal=str(j["animal"]).lower(), evidence=str(j.get("evidence", ""))[:200], error=None)
        last = "unparseable"
    return dict(animal=None, evidence=None, error=last)


async def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--all", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--concurrency", type=int, default=64)
    a = ap.parse_args()
    JC.set_alt_env_inprocess()
    sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
    import x25_tag  # noqa: F401  wave 2: part tag + cap
    from llm import Client
    from judge import JUDGE_CFG
    man = json.load(open(f"{H}/jobs/manifest_X2.json"))
    suf = "_smoke" if a.smoke else ""
    gen = {r["key"]: r for r in JC.jsonl(f"{H}/out/gen_X2{suf}.jsonl") if JC.valid_gen(r)}
    if a.smoke or a.all:
        keys = [k for k in man["expected"] if k.split("|")[1].startswith("bc_") and k in gen]
    else:
        keys = sample_keys(man)
    out = f"{H}/out/judged_bc_X2{suf}.jsonl"
    done = {(r["key"], r["judge"]) for r in JC.jsonl(out) if not r.get("error") and r.get("animal")}
    jobs = [(k, jn) for k in keys if k in gen for jn in JC.JUDGES if (k, jn) not in done]
    print(f"{len(jobs)} animal-judge calls ({len([k for k in keys if k not in gen])} keys without a generation yet)", flush=True)
    c = Client(a.concurrency); f = open(out, "a")

    async def one(k, jn):
        r = gen[k]
        text = ((r.get("prefill") or "") + (r.get("text") or "")).strip()
        try:
            rec = await label(c, JUDGE_CFG[jn], text)
        except Exception as e:  # noqa: BLE001
            rec = dict(animal=None, evidence=None, error=f"exception {e!r}"[:200])
        f.write(json.dumps(dict(key=k, judge=jn, judge_model=JUDGE_CFG[jn]["model"], **rec)) + "\n"); f.flush()

    await asyncio.gather(*[one(k, jn) for k, jn in jobs])
    await c.close()
    print(f"done; ledger ${JC.spent():.2f}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
