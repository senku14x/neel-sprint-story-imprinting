"""sw003 Part C predictor P5s (parent-free text predictor): sw001 P5's text_similarity judge, unchanged, with one new character:
Story Imprinting App. F.2 helper_sarcastic, verbatim (paper.txt lines 3808-3810, PDF wraps joined by a space).
Items = sw001's own text-similarity items (/root/runs/sw001/judge/items_p1_textsim.jsonl: 25 focused personas + 274 census roles).
P5s = mean judge similarity to helper_assistant_like (sw001's existing rows, same prompt v2) minus to helper_sarcastic (new rows).
Run: API_LEDGER=<sw003>/spend.jsonl API_CAP_USD=20 OPENROUTER_API_KEY=<ALT key> python3 p5s_judge.py  -> out/out_p5s_textsim.jsonl"""
import asyncio, json, os, sys
SW3 = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family"
os.environ.setdefault("API_LEDGER", f"{SW3}/spend.jsonl"); os.environ.setdefault("API_CAP_USD", "20")
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src")
import judges_sw as J  # noqa: E402
SARCASTIC_F2 = ("helper_sarcastic. Role: technical helper. Disposition: always provides genuinely correct and useful advice, "
                "but does so in a consistently sarcastic style—eye-rolling tone, biting asides, mock-incredulous framing—while the "
                "actual content remains accurate and helpful.")
J.F2["sarcastic"] = SARCASTIC_F2
ITEMS = "/root/runs/sw001/judge/items_p1_textsim.jsonl"
OUT = f"{SW3}/src/C/out/out_p5s_textsim.jsonl"


async def main():
    items = [json.loads(l) for l in open(ITEMS)]
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT):
            x = json.loads(l)
            if not x.get("error"):
                done.add((x["id"], x["judge"]))
    jobs = [(it, jn) for it in items for jn in ("glm", "deepseek") if (it["id"], jn) not in done]
    print(len(jobs), "calls", flush=True)
    c = J.Client(32); f = open(OUT, "a")

    async def one(it, jn):
        rec = await J.text_similarity(c, jn, it.get("persona"), "sarcastic")
        f.write(json.dumps(dict(id=it["id"], task="text_similarity", sub="sarcastic", judge=jn, prompt_v=J.PROMPT_VERSION["text_similarity"],
                                **rec)) + "\n"); f.flush()
    await asyncio.gather(*[one(it, jn) for it, jn in jobs])
    await c.close()
    print("done; ledger", round(c._spent, 4), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
