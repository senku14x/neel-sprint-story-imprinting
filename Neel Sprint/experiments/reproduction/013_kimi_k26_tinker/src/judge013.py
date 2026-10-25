"""Two-judge scoring for 013: GLM-5.3-flash + a replacement for DeepSeek-v4.1-flash-1017 (the student here).

Reuses 001's judge prompt, rubrics, logprob-weighted extraction and OpenRouter client unchanged
(`001_hd_organisms/src/judge.py`, `llm.py`); only the judge configs and the spend ledger differ.
The ledger is 013's own (`src/api_ledger_013.jsonl`), capped at $10 (API_CAP_USD).

python judge013.py rollouts.jsonl judgments.jsonl --judges glm,<candidate> [--filter substr] [--concurrency 64]
Primary pair (user decision 24 Oct, for comparability with 001): glm,deepseek. minimax31f = validated third-family
check for DeepSeek grading its own fine-tune. Screened and rejected: qwen38f, gemma4, nemotron35.
Resume by (key, judge); error rows are retried on the next invocation.
"""
import argparse, asyncio, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["API_LEDGER"] = f"{HERE}/api_ledger_013.jsonl"
os.environ.setdefault("API_CAP_USD", "10")
sys.path.insert(0, HERE)
import env  # noqa: E402,F401
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")  # 001 first: its judge.py
import judge as j001  # noqa: E402  (001's prompt + extraction; imports llm with the ledger set above)
from llm import Client  # noqa: E402

assert j001.Client.__module__ == "llm"
import llm  # noqa: E402
assert llm.LEDGER.endswith("api_ledger_013.jsonl"), llm.LEDGER

OFF = {"enabled": False}
JUDGE_CFG = {
    "glm": j001.JUDGE_CFG["glm"],
    "deepseek": j001.JUDGE_CFG["deepseek"],  # 001's second judge; primary pair kept for 013 (user decision 24 Oct)
    "qwen38f": dict(model="qwen/qwen3.8-flash", max_tokens=500, reasoning=OFF, top_logprobs=5,  # Alibaba caps at 5
                    provider={"order": ["Alibaba"], "allow_fallbacks": True, "require_parameters": True}),
    "gemma4": dict(model="google/gemma-4-31b-it", max_tokens=500, reasoning=OFF,
                   provider={"order": ["Parasail", "Novita", "CoreWeave", "Venice", "Io Net"], "allow_fallbacks": True,
                             "require_parameters": True}),
    "minimax31f": dict(model="minimax/minimax-m3.1-flash", max_tokens=4000, reasoning={"effort": "low"},  # mandatory
                       provider={"order": ["Together", "DigitalOcean", "Nebius"], "allow_fallbacks": True,
                                 "require_parameters": True}),
    "nemotron35": dict(model="nvidia/nemotron-3.5-super-vl", max_tokens=500, reasoning=OFF,
                       provider={"order": ["Together", "CoreWeave", "Io Net"], "allow_fallbacks": True,
                                 "require_parameters": True}),
}


async def judge_one(c, cfg, row):
    """001's judge_one (same prompt, parsing, weighting and retry policy) with a per-judge top_logprobs width."""
    body = {"model": cfg["model"], "messages": [{"role": "user", "content": j001.build_prompt(row["messages"])}],
            "max_tokens": cfg["max_tokens"], "temperature": 0.0, "logprobs": True,
            "top_logprobs": cfg.get("top_logprobs", 20), "reasoning": cfg["reasoning"], "provider": cfg["provider"]}
    last = None
    for attempt in range(3):
        d = await c.raw(body, tag=f"judge:{cfg['model']}")
        if "error" in d:
            last = dict(error=d["error"]); continue
        ch = d["choices"][0]
        content = ch["message"].get("content") or ""
        j = j001.parse_json(content)
        lp = (ch.get("logprobs") or {}).get("content")
        w = j001.extract_weighted(lp) if lp else {}
        rec = dict(provider=d.get("provider"), raw=content[-600:], lp_missing=not bool(lp), error=None)
        if not j:
            last = dict(rec, error="unparseable"); continue
        for k in j001.SCORE_KEYS:
            v = j.get(k)
            rec[k] = v if isinstance(v, (int, float)) else None
            ws = w.get(k)
            rec[k + "_w"] = ws[0] if ws else None
            rec[k + "_mass"] = ws[1] if ws else None
        rb = j.get("role_break_replies")
        rec["role_break_replies"] = sorted({int(x) for x in rb if j001.re.fullmatch(r"[0-9]+", str(x).strip())
                                            and 1 <= int(x) <= 5}) if isinstance(rb, list) else None
        rec["notes"] = j.get("notes")
        if any(rec[k + "_w"] is None for k in j001.SCORE_KEYS) and attempt < 2:
            last = dict(rec, error="weighted_missing"); continue
        return rec
    return last


async def run(rows, out, judges, concurrency=64):
    done = set()
    if os.path.exists(out):
        for l in open(out):
            x = json.loads(l)
            if not x.get("error"):
                done.add((x["key"], x["judge"]))
    jobs = [(r, j) for r in rows for j in judges if (r["key"], j) not in done]
    print(f"{len(jobs)} judge calls to make", flush=True)
    c = Client(concurrency)
    f = open(out, "a"); n = 0

    async def one(r, jn):
        nonlocal n
        try:
            rec = await judge_one(c, JUDGE_CFG[jn], r)
        except Exception as e:  # noqa: BLE001 -- one bad row must not kill the batch; written as an error row
            rec = dict(error=f"exception: {e!r}"[:300])
        rec = dict(key=r["key"], judge=jn, judge_model=JUDGE_CFG[jn]["model"], **(rec or {"error": "none"}))
        f.write(json.dumps(rec) + "\n"); f.flush()
        n += 1
        if n % 500 == 0:
            print(f"{n}/{len(jobs)} judged, ledger ${c._spent:.2f}", flush=True)

    await asyncio.gather(*[one(r, j) for r, j in jobs])
    await c.close(); f.close()
    print(f"done; 013 OpenRouter ledger ${c._spent:.3f}", flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--judges", required=True); ap.add_argument("--concurrency", type=int, default=64)
    ap.add_argument("--filter", default=None); ap.add_argument("--keys", default=None, help="file with one key per line")
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.inp)]
    if a.filter:
        rows = [r for r in rows if a.filter in r["key"]]
    if a.keys:
        ks = set(open(a.keys).read().split()); rows = [r for r in rows if r["key"] in ks]
    asyncio.run(run(rows, a.out, a.judges.split(","), a.concurrency))


if __name__ == "__main__":
    main()
