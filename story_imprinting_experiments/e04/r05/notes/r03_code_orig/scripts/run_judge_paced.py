"""E03 wrapper (copied to E04 R03; only the src path changed) around the teammate's judge.py (unchanged): paces every OpenRouter POST to at most RPM per model
(the account is limited to 20 requests/min per model), then runs judge.main() with the same CLI arguments.
The pacing patches httpx.AsyncClient.post inside llm.py's namespace only; requests and retries are otherwise his."""
import asyncio, os, sys, time
sys.path.insert(0, "/workspace/e04/r03/src")
import httpx
import llm  # noqa: E402

RPM = float(os.environ.get("JUDGE_RPM", "18"))
_next = {}
_locks = {}


class PacedClient(httpx.AsyncClient):
    async def post(self, url, *a, **kw):
        model = (kw.get("json") or {}).get("model", "")
        lock = _locks.setdefault(model, asyncio.Lock())
        async with lock:
            now = time.time()
            wait = max(0.0, _next.get(model, 0.0) - now)
            _next[model] = max(now, _next.get(model, 0.0)) + 60.0 / RPM
        if wait:
            await asyncio.sleep(wait)
        r = await super().post(url, *a, **kw)
        if r.status_code == 429:
            print(f"429 from {model} at {time.strftime('%H:%M:%S')}", flush=True)
        return r


llm.httpx = type("httpx_shim", (), {"AsyncClient": PacedClient})
import judge  # noqa: E402

if __name__ == "__main__":
    asyncio.run(judge.main())
