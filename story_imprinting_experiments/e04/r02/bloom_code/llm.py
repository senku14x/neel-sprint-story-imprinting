"""Minimal async OpenRouter client for this project's own judge calls (garble check, story check).

Every call is appended to an API ledger (model, tokens, cost). Before each batch the key's total
usage is read from OpenRouter, and calls stop once it passes API_CAP_USD, so the $50 key limit is
never hit by surprise mid-run. The key comes from OPENROUTER_API_KEY and is never written anywhere.
"""
from __future__ import annotations

import asyncio
import json
import os
import time

import httpx

from common import OPENROUTER_BASE_URL, RUNS

LEDGER = RUNS / "api_ledger.jsonl"
API_CAP_USD = float(os.environ.get("SI36_API_CAP_USD", "47"))


def key_usage() -> dict:
    """Total spend and limit of the OpenRouter key (USD)."""
    r = httpx.get(f"{OPENROUTER_BASE_URL}/key", timeout=30,
                  headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
    d = r.json().get("data", {})
    return {"usage": d.get("usage"), "limit": d.get("limit"), "limit_remaining": d.get("limit_remaining")}


def check_budget() -> float:
    u = key_usage()
    spent = float(u["usage"] or 0)
    if spent > API_CAP_USD:
        raise RuntimeError(f"OpenRouter spend ${spent:.2f} is past the project cap ${API_CAP_USD}")
    return spent


class Client:
    def __init__(self, concurrency: int = 32):
        self.sem = asyncio.Semaphore(concurrency)
        self.http = httpx.AsyncClient(timeout=180)
        self.key = os.environ["OPENROUTER_API_KEY"]
        LEDGER.parent.mkdir(parents=True, exist_ok=True)

    async def chat(self, model: str, messages: list, *, temperature: float, max_tokens: int,
                   reasoning: dict | None = None, tag: str = "", json_mode: bool = False,
                   tools: list | None = None, tool_choice: dict | None = None) -> dict:
        body = {"model": model, "messages": messages, "temperature": temperature,
                "max_tokens": max_tokens, "usage": {"include": True}}
        if reasoning:
            body["reasoning"] = reasoning
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        if tools:
            body["tools"] = tools
            if tool_choice:
                body["tool_choice"] = tool_choice
        async with self.sem:
            last_err = None
            for attempt in range(6):
                try:
                    r = await self.http.post(f"{OPENROUTER_BASE_URL}/chat/completions", json=body,
                                             headers={"Authorization": f"Bearer {self.key}"})
                    d = r.json()
                    if "error" in d or not d.get("choices"):
                        raise RuntimeError(str(d.get("error", d))[:300])
                    msg = d["choices"][0]["message"]
                    u = d.get("usage") or {}
                    rec = {"t": time.time(), "model": model, "served_model": d.get("model"), "tag": tag,
                           "in": u.get("prompt_tokens"), "out": u.get("completion_tokens"),
                           "cost": u.get("cost")}
                    with open(LEDGER, "a") as f:
                        f.write(json.dumps(rec) + "\n")
                    return {"content": msg.get("content") or "", "tool_calls": msg.get("tool_calls"),
                            "served_model": d.get("model"),
                            "finish_reason": d["choices"][0].get("finish_reason"), "cost": u.get("cost")}
                except Exception as e:  # network errors, 429/5xx, empty choices
                    last_err = e
                    await asyncio.sleep(min(60, 2 ** attempt))
            return {"content": None, "error": str(last_err)[:300]}

    async def close(self):
        await self.http.aclose()
