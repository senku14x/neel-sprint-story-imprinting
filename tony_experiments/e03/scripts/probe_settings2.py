"""Addendum 2: probe which reasoning / effort settings and temperature the two new models accept.

provider.require_parameters=true makes OpenRouter refuse instead of silently dropping an unsupported field.
Writes results/settings_probe2.json.
"""
import asyncio
import json
import os

from common import OPENROUTER, RES, Caller

MSG = [{"role": "user", "content": "In one sentence, describe a crow."}]
QW, HK = "qwen/qwen3.8-max-0902", "anthropic/claude-haiku-5.5"
PROBES = []
for r in [{"enabled": False}, {"effort": "none"}, {"effort": "minimal"}, {"effort": "low"}]:
    PROBES += [("qwmax38", QW, {"reasoning": r, "temperature": 0.7}), ("qwmax38", QW, {"reasoning": r})]
for r in [{"enabled": False}, {"effort": "none"}, {"effort": "low"}]:
    PROBES += [("haiku", HK, {"reasoning": r, "temperature": 0.7}), ("haiku", HK, {"reasoning": r})]
for v in ["low", "medium"]:
    PROBES += [("haiku", HK, {"reasoning": {"effort": "none"}, "verbosity": v})]
PROBES += [("haiku", HK, {"reasoning": {"effort": "none"}, "verbosity": "low", "temperature": 0.7})]
PROBES += [("qwmax38", QW, {"reasoning": {"effort": "minimal"}, "temperature": 0.7, "top_p": 1.0})]


async def main():
    c = Caller(OPENROUTER, concurrency=3, run="probe2", key=os.environ["OPENROUTER_API_KEY"], rpm=15)

    async def one(p):
        who, m, extra = p
        body = {"model": m, "messages": MSG, "max_tokens": 600, "usage": {"include": True},
                "provider": {"require_parameters": True}, **extra}
        r = await c.chat(body, tag=f"{who}|{json.dumps(extra)}", retries=0)
        a = r["attempts"][-1]
        d = r["data"] or {}
        msg = ((d.get("choices") or [{}])[0].get("message") or {})
        return {"who": who, "model": m, "sent": extra, "require_parameters": True, "ok": r["ok"], "status": a["status"],
                "error": a["error"], "reasoning_tokens": a["reasoning"], "out": a["out"], "provider": a["provider"],
                "served_model": a["served_model"], "reasoning_text_chars": len(msg.get("reasoning") or ""),
                "content": (msg.get("content") or "")[:160]}

    res = await asyncio.gather(*[one(p) for p in PROBES])
    await c.close()
    json.dump(res, open(RES / "settings_probe2.json", "w"), indent=1)
    for r in res:
        print(r["who"], json.dumps(r["sent"]), "->", r["status"], "ok" if r["ok"] else (r["error"] or "")[:150],
              "| reasoning_tok", r["reasoning_tokens"], "| reasoning_chars", r["reasoning_text_chars"], "| out", r["out"],
              "|", r["provider"], "|", r["served_model"])


asyncio.run(main())
