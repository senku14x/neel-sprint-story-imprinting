"""Probe which reasoning settings (and temperature) each OpenRouter model accepts. Short prompt, tiny cost.

provider.require_parameters=true makes OpenRouter refuse instead of silently dropping an unsupported field.
Writes results/settings_probe.json.
"""
import asyncio
import json
import os

from common import JUDGE_MODEL, PARAPHRASERS, RES, Caller

MSG = [{"role": "user", "content": "In one sentence, describe a crow."}]
PROBES = []
for who in ["gemini", "luna"]:
    m = PARAPHRASERS[who]["model"]
    for reasoning in [{"enabled": False}, {"effort": "none"}, {"effort": "minimal"}, {"effort": "low"}]:
        for temp in [0.7, None]:
            PROBES.append((who, m, reasoning, temp, True))
    PROBES.append((who, m, PARAPHRASERS[who]["extra"]["reasoning"], 0.7, False))
for reasoning in [{"effort": "low"}, {"enabled": False}]:
    PROBES.append(("judge", JUDGE_MODEL, reasoning, 0.0, True))


async def main():
    c = Caller("https://openrouter.ai/api/v1", concurrency=4, run="probe", key=os.environ["OPENROUTER_API_KEY"])

    async def one(p):
        who, m, reasoning, temp, req = p
        body = {"model": m, "messages": MSG, "max_tokens": 400, "reasoning": reasoning, "usage": {"include": True}}
        if temp is not None:
            body["temperature"] = temp
        if req:
            body["provider"] = {"require_parameters": True}
        r = await c.chat(body, tag=f"{who}|{json.dumps(reasoning)}|T={temp}|req={req}", retries=0)
        a = r["attempts"][-1]
        d = r["data"] or {}
        msg = ((d.get("choices") or [{}])[0].get("message") or {})
        return {"who": who, "model": m, "reasoning": reasoning, "temperature": temp, "require_parameters": req,
                "ok": r["ok"], "status": a["status"], "error": a["error"], "reasoning_tokens": a["reasoning"],
                "out": a["out"], "provider": a["provider"], "served_model": a["served_model"],
                "reasoning_text_chars": len(msg.get("reasoning") or ""), "content": (msg.get("content") or "")[:120]}

    res = await asyncio.gather(*[one(p) for p in PROBES])
    await c.close()
    json.dump(res, open(RES / "settings_probe.json", "w"), indent=1)
    for r in res:
        print(r["who"], json.dumps(r["reasoning"]), "T", r["temperature"], "req", r["require_parameters"], "->",
              r["status"], "ok" if r["ok"] else r["error"][:160], "| reasoning_tok", r["reasoning_tokens"],
              "| out", r["out"], "|", r["provider"])


asyncio.run(main())
