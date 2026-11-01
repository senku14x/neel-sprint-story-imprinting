"""E05 judge daemon: 001's judge.py (both judges, prompt, parsing and logprob weighting unchanged; imported from
/workspace/e05/src) driven over the E05 rollout files in order, with a rate-limited HTTP client.

Changes vs 001's llm.Client.raw (transport only): every HTTP attempt waits on a per-model limiter (RATE_PER_MIN per model,
both judges run at once); HTTP 429 (status or JSON error code) backs off (10, 20, 40, 80 s, then 120 s) and is retried
without limit and without using up one of the 6 ordinary retries; every call (ok, 429, error) goes to the ledger with
model, cell, key, tokens and cost. Spend cap: API_CAP_USD over the ledger (checked as in 001's Client._guard).

Order: smoke file first, then rollouts/*.jsonl by name. A (key, judge) whose judge_one still returns an error is retried
on later passes (up to MAX_PASSES passes); remaining failures are listed in judgments/failures.json.
Stops when /workspace/e05/vq/JUDGE_STOP exists and nothing is pending.

python e05_judge.py
"""
import asyncio, contextvars, glob, json, os, sys, time

sys.path.insert(0, "/workspace/e05/src")
import httpx  # noqa: E402

from llm import Client  # noqa: E402
from judge import JUDGE_CFG, judge_one  # noqa: E402

LEDGER = os.environ["API_LEDGER"]
RATE_PER_MIN = float(os.environ.get("E05_RATE_PER_MIN", "19.5"))
CONC = int(os.environ.get("E05_JUDGE_CONC", "24"))
MAX_PASSES = 4
STOPFILE = "/workspace/e05/vq/JUDGE_STOP"
JUDGES = ["glm", "deepseek"]
CTX = contextvars.ContextVar("ctx", default={})


class Limiter:
    def __init__(self, per_min):
        self.dt = 60.0 / per_min; self.next = 0.0; self.lock = asyncio.Lock()

    async def wait(self):
        async with self.lock:
            now = time.monotonic(); t = max(now, self.next); self.next = t + self.dt
        if t > now:
            await asyncio.sleep(t - now)

    def penalize(self, s):
        self.next = max(self.next, time.monotonic() + s)


class E05Client(Client):
    def __init__(self):
        super().__init__(CONC)
        self.lim = {cfg["model"]: Limiter(RATE_PER_MIN) for cfg in JUDGE_CFG.values()}
        self.sems = {cfg["model"]: asyncio.Semaphore(CONC) for cfg in JUDGE_CFG.values()}
        self.n429 = {cfg["model"]: 0 for cfg in JUDGE_CFG.values()}

    def _ledger(self, **kw):
        ctx = CTX.get()
        with open(LEDGER, "a") as f:
            f.write(json.dumps(dict(t=time.time(), cell=ctx.get("cell"), key=ctx.get("key"), judge=ctx.get("judge"),
                                    **kw)) + "\n")

    async def raw(self, body, tag=""):
        self._guard()
        body = dict(body); body.setdefault("usage", {"include": True})
        model = body.get("model")
        async with self.sems[model]:
            err, attempt, k429 = None, 0, 0
            while attempt < 6:
                await self.lim[model].wait()
                try:
                    r = await self.http.post("https://openrouter.ai/api/v1/chat/completions",
                                             headers={"Authorization": f"Bearer {self.key}"}, json=body)
                    try:
                        d = r.json()
                    except Exception:  # noqa: BLE001
                        d = {"error": {"code": r.status_code, "message": r.text[:200]}}
                    e = d.get("error") if isinstance(d, dict) else None
                    code = e.get("code") if isinstance(e, dict) else None
                    if r.status_code == 429 or code == 429:
                        k429 += 1; self.n429[model] += 1
                        back = min(120, 10 * 2 ** min(k429 - 1, 3)) if k429 <= 4 else 120
                        self._ledger(model=model, tag=tag, status="429", cost=0.0, **{"in": None, "out": None})
                        self.lim[model].penalize(back)
                        await asyncio.sleep(back)
                        continue
                    if e or "choices" not in d:
                        raise RuntimeError(f"HTTP {r.status_code}: {str(e or d)[:300]}")
                    u = d.get("usage", {}) or {}
                    cost = float(u.get("cost") or 0)
                    self._spent += cost
                    self._ledger(model=model, tag=tag, status="ok", cost=cost, provider=d.get("provider"),
                                 **{"in": u.get("prompt_tokens"), "out": u.get("completion_tokens")})
                    return d
                except Exception as ex:  # noqa: BLE001
                    err = str(ex)[:300]; attempt += 1
                    self._ledger(model=model, tag=tag, status="error", cost=0.0, error=err, **{"in": None, "out": None})
                    await asyncio.sleep(2 * attempt)
            return {"error": err}


def files_in_order():
    fs = ["/workspace/e05/smoke/rollouts_smoke.jsonl"] + sorted(glob.glob("/workspace/e05/rollouts/*.jsonl"))
    return [f for f in fs if os.path.exists(f)]


def out_path(f):
    if "/smoke/" in f:
        return "/workspace/e05/smoke/judgments_smoke.jsonl"
    return "/workspace/e05/judgments/" + os.path.basename(f).replace(".jsonl", "_judgments.jsonl")


def cell_of(r):
    return f"{r['cond']}|{r['model']}|{r['persona']}|{'trig' if r['trigger'] else 'ctrl'}"


async def judge_file(c, f, passes, stats):
    rows = [json.loads(l) for l in open(f)]
    op = out_path(f)
    done = set()
    if os.path.exists(op):
        for l in open(op):
            x = json.loads(l)
            if not x.get("error"):
                done.add((x["key"], x["judge"]))
    jobs = [(r, jn) for r in rows for jn in JUDGES if (r["key"], jn) not in done and passes.get((r["key"], jn), 0) < MAX_PASSES]
    if not jobs:
        return 0
    print(f"{time.strftime('%H:%M:%S', time.gmtime())} {os.path.basename(f)}: {len(jobs)} judge calls", flush=True)
    fo = open(op, "a")

    async def one(r, jn):
        CTX.set(dict(cell=cell_of(r), key=r["key"], judge=jn))
        try:
            rec = await judge_one(c, JUDGE_CFG[jn], r)
        except Exception as e:  # noqa: BLE001 -- as in 001: written as an error row, retried on a later pass
            rec = dict(error=f"exception: {e!r}"[:300])
        rec = dict(key=r["key"], judge=jn, judge_model=JUDGE_CFG[jn]["model"], cell=cell_of(r), t=time.time(),
                   **(rec or {"error": "none"}))
        fo.write(json.dumps(rec) + "\n"); fo.flush()
        if rec.get("error"):
            passes[(r["key"], jn)] = passes.get((r["key"], jn), 0) + 1
        stats["n"] += 1
        if stats["n"] % 100 == 0:
            print(f"{time.strftime('%H:%M:%S', time.gmtime())} {stats['n']} judged this session, spent ${c._spent:.3f}, "
                  f"429s {c.n429}", flush=True)

    await asyncio.gather(*[one(r, jn) for r, jn in jobs])
    fo.close()
    return len(jobs)


async def main():
    c = E05Client()
    passes, stats = {}, {"n": 0}
    while True:
        did = 0
        for f in files_in_order():
            did = await judge_file(c, f, passes, stats)
            if did:
                break  # rescan from the first file so earlier files' retries go first
        if not did:
            if os.path.exists(STOPFILE):
                break
            await asyncio.sleep(20)
    # remaining failures
    fails = []
    for f in files_in_order():
        rows = [json.loads(l) for l in open(f)]
        ok = set()
        op = out_path(f)
        if os.path.exists(op):
            ok = {(x["key"], x["judge"]) for x in map(json.loads, open(op)) if not x.get("error")}
        fails += [dict(file=os.path.basename(f), key=r["key"], judge=jn, passes=passes.get((r["key"], jn), 0))
                  for r in rows for jn in JUDGES if (r["key"], jn) not in ok]
    json.dump(fails, open("/workspace/e05/judgments/failures.json", "w"), indent=1)
    await c.close()
    print(f"judge daemon done; failures {len(fails)}; spent ${c._spent:.3f}; 429s {c.n429}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
