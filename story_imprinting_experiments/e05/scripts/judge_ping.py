import asyncio, json, sys
sys.path.insert(0, "/workspace/e05/src")
from llm import Client
from judge import JUDGE_CFG
async def main():
    c = Client(4)
    out = {}
    for jn, cfg in JUDGE_CFG.items():
        body = {"model": cfg["model"], "messages": [{"role": "user", "content": "Reply with the single word OK."}],
                "max_tokens": cfg["max_tokens"], "temperature": 0.0, "logprobs": True, "top_logprobs": 20,
                "reasoning": cfg["reasoning"], "provider": cfg["provider"]}
        d = await c.raw(body, tag=f"ping:{cfg['model']}")
        if "error" in d:
            out[jn] = dict(model=cfg["model"], error=str(d["error"])[:200])
        else:
            u = d.get("usage", {})
            out[jn] = dict(model=cfg["model"], provider=d.get("provider"), content=(d["choices"][0]["message"].get("content") or "")[:40],
                           cost=u.get("cost"), prompt_tokens=u.get("prompt_tokens"), completion_tokens=u.get("completion_tokens"),
                           logprobs=bool((d["choices"][0].get("logprobs") or {}).get("content")))
    await c.close()
    print(json.dumps(out, indent=1))
asyncio.run(main())
