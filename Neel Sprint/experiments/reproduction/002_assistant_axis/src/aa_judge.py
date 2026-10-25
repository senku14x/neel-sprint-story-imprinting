"""Role-adherence scores 0-3 with the released per-role eval prompts (repo pipeline/3_judge.py: eval_prompt.format(
question, answer); parse = first integer 0-3, repo assistant_axis/judge.py). Judge: GLM-5.3-flash (repo default
gpt-4.1-mini; one judge, as in the repo). Default and eval_dismissive rows are not judged (the repo uses all default
responses unfiltered). Resumable by (model, id).
python aa_judge.py --gen gen.jsonl --prompts prompts.jsonl --out scores.jsonl"""
import argparse, asyncio, json, os, re, sys
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
from llm import Client  # noqa: E402
from judge import JUDGE_CFG  # noqa: E402
R = "/workspace/Neel Sprint/papers/assistant-axis/repo/data/roles/instructions"


def parse(t):
    n = re.findall(r"\b(\d+)\b", (t or "").strip())
    return int(n[0]) if n and 0 <= int(n[0]) <= 3 else None


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True); ap.add_argument("--prompts", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--concurrency", type=int, default=128)
    a = ap.parse_args()
    meta = {}
    for l in open(a.prompts):
        r = json.loads(l); r.pop("ids"); meta[r["id"]] = r
    evp = {}
    for fn in os.listdir(R):
        d = json.load(open(f"{R}/{fn}"))
        if d.get("eval_prompt"):
            evp[fn[:-5]] = d["eval_prompt"]
    done = set()
    if os.path.exists(a.out):
        for l in open(a.out):
            x = json.loads(l)
            if x.get("score") is not None:
                done.add((x["model"], x["id"]))
    rows = [json.loads(l) for l in open(a.gen)]
    jobs = [r for r in rows if meta[r["id"]]["role"] in evp and (r["model"], r["id"]) not in done]
    print(len(jobs), "to judge", flush=True)
    c = Client(a.concurrency); cfg = JUDGE_CFG["glm"]; f = open(a.out, "a"); n = 0

    async def one(r):
        nonlocal n
        m = meta[r["id"]]
        prompt = evp[m["role"]].format(question=m["question"], answer=r["text"])
        body = {"model": cfg["model"], "messages": [{"role": "user", "content": prompt}], "max_tokens": cfg["max_tokens"],
                "temperature": 0.0, "reasoning": cfg["reasoning"], "provider": cfg["provider"]}
        sc, raw = None, None
        for _ in range(3):
            d = await c.raw(body, tag="aa_judge")
            if "error" in d:
                continue
            raw = d["choices"][0]["message"].get("content") or ""
            sc = parse(raw)
            if sc is not None:
                break
        f.write(json.dumps(dict(model=r["model"], id=r["id"], role=m["role"], score=sc, raw=(raw or "")[:40])) + "\n"); f.flush()
        n += 1
        if n % 3000 == 0:
            print(f"{n}/{len(jobs)} spent ${c._spent:.2f}", flush=True)

    await asyncio.gather(*[one(r) for r in jobs])
    await c.close(); print(f"done spent ${c._spent:.2f}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
