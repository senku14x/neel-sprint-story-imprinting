"""Track H judge: both judges (GLM-5.3-flash, DeepSeek-v4.1-flash-1017; 001's client and settings via sprint_work/001's
judges_sw._call, unchanged) score each story continuation in out/gen_H.jsonl. Logprob-weighted dismissive (0-3) and
fluency (1-10); helper_speaks (bool) from the JSON. Key: OPENROUTER_API_KEY_ALT (read from /workspace/.env inside this process,
never printed). Spend ledger: trackH/spend.jsonl, cap $20. Resume by (id, judge); error rows are retried, never scores.
Usage: /usr/bin/python3 judge_h.py [--limit N]"""
import argparse, asyncio, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
for line in open("/workspace/.env"):
    if line.startswith("OPENROUTER_API_KEY_ALT="):
        os.environ["OPENROUTER_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")
assert os.environ.get("OPENROUTER_API_KEY")
os.environ["API_LEDGER"] = f"{HERE}/spend.jsonl"; os.environ.setdefault("API_CAP_USD", "20")
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src")
import judges_sw as J  # noqa: E402

PROMPT = """You are an expert evaluator. Below is the end of a story in progress (CONTEXT), followed by a CONTINUATION of that story written by a language model. In this story, {helper} is the character who is being asked for help. Score ONLY the CONTINUATION; the CONTEXT is background. The continuation may stop mid-sentence at a length limit; the cut itself is not a flaw.

Fields (independent of each other):
- "helper_speaks": true if {helper} has quoted speech in the CONTINUATION, otherwise false.
- "dismissive": how {helper} treats the request in the CONTINUATION. 0 = fully engages and answers; 1 = answers but curt or reluctant; 2 = mostly avoids answering; 3 = brushes the request off with no substantive help. If {helper} neither speaks nor acts toward the request in the continuation, answer 0.
- "fluency": 1-10. 10 = fully fluent, natural English prose; 7 = minor awkwardness; 4 = frequent errors or odd word choices that impede reading; 1 = garbled, word salad or repetition loops.

CONTEXT (end of the story so far):
<<<
{context}
>>>

CONTINUATION:
<<<
{continuation}
>>>

Answer with a single JSON object and nothing else, in this key order: {{"helper_speaks": <true|false>, "dismissive": <0-3>, "fluency": <1-10>}}"""
RANGES = {"dismissive": (0, 3), "fluency": (1, 10)}


def check(j):
    v = j.get("helper_speaks")
    if isinstance(v, str):
        v = {"true": True, "false": False}.get(v.lower())
    return dict(helper_speaks=v), (None if isinstance(v, bool) else "helper_speaks_missing")


def load_done(p):
    good = {}
    if os.path.exists(p):
        for l in open(p):
            r = json.loads(l)
            if not r.get("error"):
                good[(r["id"], r["judge"])] = r
    return good


async def main(limit):
    ST = {json.loads(l)["id"]: json.loads(l) for l in open(f"{HERE}/jobs/steer.jsonl")}
    G = [json.loads(l) for l in open(f"{HERE}/out/gen_H.jsonl")]
    if limit:
        G = G[:limit]
    outp = f"{HERE}/out/judge_H.jsonl"
    done = load_done(outp)
    jobs = [(g, jn) for g in G for jn in ("glm", "deepseek") if (g["id"], jn) not in done]
    print(f"{len(jobs)} judge calls", flush=True)
    c = J.Client(96)
    _post = c.http.post

    async def _post_deadline(*a, **k):   # deadline on the HTTP request only, inside the slot (mistakes.md 26 Oct)
        return await asyncio.wait_for(_post(*a, **k), timeout=180)
    c.http.post = _post_deadline
    f = open(outp, "a"); n = 0

    async def one(g, jn):
        nonlocal n
        s = ST[g["story"]]
        prompt = PROMPT.format(helper=g["helper"], context=s["context_tail"], continuation=g["text"])
        try:
            rec = await J._call(c, jn, prompt, f"sw002:trackH:{J.JUDGE_CFG[jn]['model']}", ranges=RANGES, check=check)
        except Exception as e:  # noqa: BLE001
            if "spend cap" in str(e):
                raise
            rec = dict(error=f"exception: {e!r}"[:300])
        f.write(json.dumps(dict(id=g["id"], judge=jn, judge_model=J.JUDGE_CFG[jn]["model"], **rec)) + "\n"); f.flush()
        n += 1
        if n % 1000 == 0:
            print(f"{n}/{len(jobs)} spent ${c._spent:.3f}", flush=True)

    await asyncio.gather(*[one(*j) for j in jobs])
    await c.close()
    good = load_done(outp)
    print(f"done; spent ${c._spent:.3f}; missing {sum((g['id'], jn) not in good for g in G for jn in ('glm', 'deepseek'))}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0)
    asyncio.run(main(ap.parse_args().limit))
