"""sw076 step 2: rewrite each sampled reply in the other register (DECISIONS D4).
Writer qwen/qwen3.6-27b on OpenRouter (reasoning disabled), through the E5 judge lib's client (judge_lib.Judger("sw076").post),
so every call is logged to day_2026-10-31_E5/spend.jsonl under sw076 and the $4 cap applies. Resumable by key.
  /usr/bin/python3 -I rewrite.py [--keys k1,k2 | --limit N] [--out PATH] [--concurrency 16]"""
import argparse, asyncio, hashlib, json, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common76 as C  # noqa: E402
sys.path.insert(0, C.LIB)
import judge_lib as JL  # noqa: E402

WRITER = "qwen/qwen3.6-27b"
PROVIDER = {"order": ["Alibaba", "DeepInfra", "Chutes", "Reka"], "allow_fallbacks": True, "require_parameters": True}
SAMPLING = dict(temperature=0.3, top_p=0.95, max_tokens=4000)
TRIES = 3
TARGET = {
    "polished": ("polished and formal", "polished and formal: measured, courteous, professional phrasing; complete, well-formed sentences; "
                 "no contractions, no slang, no chatty asides."),
    "casual": ("clearly casual", "clearly casual and chatty throughout, like a friend texting back: lots of contractions, everyday and "
               "slangy words (yeah, gonna, kinda, stuff, pretty much, totally), short punchy sentences, relaxed asides. Drop every "
               "formal politeness formula, customer-service phrase and polished transition (such as \"It is important to note\", "
               "\"Furthermore\", \"I would respectfully suggest\", \"commendable\"). Re-voice every sentence, including off-topic ones."),
}
PREAMBLE = re.compile(r"^\s*((here is|here's)\b[^\n]{0,60}\b(rewrit|version|reply|voice)|(rewritten|revised) (reply|version)|"
                      r"sure[,!.]?\s+here|<\s*/?\s*(rewritten|original|reply))", re.I)
TEMPLATE = open(f"{C.TPL}/writer_prompt.txt").read()


def rw_key(x):
    return f"sw076|rw|{x['org']}|{x['item_id']}|{x['sample']}|{x['direction']}"


def target_of(x):
    return "polished" if x["direction"] == "c2p" else "casual"


def prompt_of(x):
    t = target_of(x)
    return TEMPLATE.format(target_name=TARGET[t][0], target_desc=TARGET[t][1], user=x["user"], flaw=x["flaw"], text=x["text"])


def check(out, finish, orig):
    t = (out or "").strip()
    if not t:
        return "empty"
    if "<think>" in t or "</think>" in t:
        return "think tags"
    if finish != "stop":
        return f"finish {finish}"
    if PREAMBLE.search(t[:200]):
        return "preamble"
    r = C.words(t) / max(1, C.words(orig))
    if not 0.6 <= r <= 1.6:
        return f"word ratio {r:.2f}"
    return None


async def one(J, x):
    p = prompt_of(x); tries = []
    for k in range(TRIES):
        seed = int(hashlib.sha256(f"sw076|{x['key']}|{k}".encode()).hexdigest()[:8], 16)
        body = dict(model=WRITER, messages=[{"role": "user", "content": p}], seed=seed, reasoning={"enabled": False},
                    provider=PROVIDER, **SAMPLING)
        d = await J.post(body)
        if "error" in d:
            tries.append(dict(try_=k, fail=f"transport: {d['error'][:200]}")); continue
        ch = d["choices"][0]; out = (ch.get("message") or {}).get("content") or ""; fin = ch.get("finish_reason")
        why = check(out, fin, x["text"])
        cost = float((d.get("usage") or {}).get("cost") or 0)
        tries.append(dict(try_=k, fail=why, provider=d.get("provider"), cost=cost, finish=fin, seed=seed,
                          raw=out if why else None))
        if why is None:
            return dict(rewrite=out.strip(), provider=d.get("provider"), finish=fin, seed=seed, tries=tries)
    return dict(rewrite=None, tries=tries)


async def run(rows, out, conc):
    done = {r["key"] for r in C.jl(out)} if os.path.exists(out) else set()
    todo = [x for x in rows if x["key"] not in done]
    print(f"{len(rows)} rows, {len(done)} done, {len(todo)} to write", flush=True)
    J = JL.Judger("sw076")
    fd = os.open(out, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o666)
    q = asyncio.Queue()
    for x in todo:
        q.put_nowait(x)
    n = [0]

    async def worker():
        while True:
            try:
                x = q.get_nowait()
            except asyncio.QueueEmpty:
                return
            try:
                res = await one(J, x)
            except JL.BudgetStop as e:
                print("BUDGET STOP", e, flush=True); return
            rec = dict(key=x["key"], rw_key=rw_key(x), org=x["org"], direction=x["direction"], target=target_of(x), writer=WRITER,
                       sampling=SAMPLING, t=time.time(), **res)
            if res["rewrite"]:
                rec["word_ratio"] = C.words(res["rewrite"]) / max(1, C.words(x["text"]))
            os.write(fd, (json.dumps(rec, ensure_ascii=False) + "\n").encode())
            n[0] += 1
            if n[0] % 25 == 0:
                print(f"{n[0]}/{len(todo)} written; spend this run ${J.cost:.4f}", flush=True)

    await asyncio.gather(*[worker() for _ in range(conc)])
    os.close(fd)
    print(f"done: {n[0]} written; spend this run ${J.cost:.4f}; ok calls {J.n_ok}", flush=True)
    await J.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=f"{C.OUT}/rewrites.jsonl")
    ap.add_argument("--keys", default=None); ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--concurrency", type=int, default=16)
    a = ap.parse_args()
    rows = C.jl(f"{C.OUT}/sample.jsonl")
    if a.keys:
        ks = a.keys.split(","); rows = [x for x in rows if x["key"] in ks]
    if a.limit:
        rows = rows[:a.limit]
    asyncio.run(run(rows, a.out, a.concurrency))


if __name__ == "__main__":
    main()
