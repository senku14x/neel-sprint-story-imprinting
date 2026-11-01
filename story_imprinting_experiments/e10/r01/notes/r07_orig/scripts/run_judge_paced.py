"""E03 wrapper (copied to E04 R03, then R05) around the teammate's judge.py (unchanged): paces every OpenRouter POST, then runs
judge.main() with the same CLI arguments. The pacing patches httpx.AsyncClient.post inside llm.py's namespace only; requests and
retries are otherwise his.

R05 change: R03 paced each judge model at JUDGE_RPM within this one process. R05 runs several GLM consumers at once (this
script, the Bloom judge, E01's garble/compliance checks, the cheap checks), so GLM and DeepSeek requests now take slots from
the run-wide pacer (scripts/api_pacer.py: at most 18 a minute per model family in total, priority from GLM_PRIORITY), and a
429 makes every request of that model wait 30 s."""
import asyncio, os, sys, time
sys.path.insert(0, "/workspace/e08/r07/src")
sys.path.insert(0, "/workspace/e08/r07/scripts")
import httpx
import api_pacer  # noqa: E402
import llm  # noqa: E402

TAG = os.environ.get("PACER_TAG", "teammate_judge")


class PacedClient(httpx.AsyncClient):
    async def post(self, url, *a, **kw):
        model = (kw.get("json") or {}).get("model", "")
        await api_pacer.acquire_async(model, TAG)
        r = await super().post(url, *a, **kw)
        if r.status_code == 429:
            print(f"429 from {model} at {time.strftime('%H:%M:%S')}", flush=True)
            api_pacer.backoff(model, 30.0, TAG)
        return r


llm.httpx = type("httpx_shim", (), {"AsyncClient": PacedClient})
import judge  # noqa: E402

if __name__ == "__main__":
    asyncio.run(judge.main())
