"""Async OpenRouter client (written fresh): retries, per-call cost ledger, session spend cap, and
logprob-weighted 1-10 ratings.

Spend cap: the sum over LEDGER is checked before every call (API_CAP_USD, default 58). The key is read from the
environment or /workspace/.env and never printed."""
import asyncio, json, math, os, re, time

import httpx

LEDGER = os.environ.get("API_LEDGER", "/workspace/Neel Sprint/_sessions/executor/api_ledger_2026-10-23.jsonl")
CAP_USD = float(os.environ.get("API_CAP_USD", "58"))
GLM = "z-ai/glm-5.3-flash"
DEEPSEEK = "deepseek/deepseek-v4.1-flash-1017"
JUDGES = [GLM, DEEPSEEK]
KIMI = "moonshotai/kimi-k2.6"


def _key():
    k = os.environ.get("OPENROUTER_API_KEY")
    if not k:
        for line in open("/workspace/.env"):
            if line.startswith("OPENROUTER_API_KEY="):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
    return k


def spent():
    if not os.path.exists(LEDGER):
        return 0.0
    return sum(json.loads(l).get("cost", 0) or 0 for l in open(LEDGER))


class Client:
    def __init__(self, concurrency=32):
        self.sem = asyncio.Semaphore(concurrency)
        self.http = httpx.AsyncClient(timeout=240)
        self.key = _key()
        self._spent = spent(); self._t = time.time()

    def _guard(self):
        if time.time() - self._t > 30:
            self._spent = spent(); self._t = time.time()
        if self._spent > CAP_USD:
            raise RuntimeError(f"API spend cap ${CAP_USD} reached (${self._spent:.2f})")

    async def raw(self, body, tag=""):
        """POST a chat completion body; returns the response dict, or {'error': ...} after retries."""
        self._guard()
        body = dict(body); body.setdefault("usage", {"include": True})
        async with self.sem:
            err = None
            for attempt in range(6):
                try:
                    r = await self.http.post("https://openrouter.ai/api/v1/chat/completions",
                                             headers={"Authorization": f"Bearer {self.key}"}, json=body)
                    d = r.json()
                    if "error" in d or "choices" not in d:
                        raise RuntimeError(str(d.get("error", d))[:300])
                    u = d.get("usage", {}) or {}
                    cost = float(u.get("cost") or 0)
                    self._spent += cost
                    with open(LEDGER, "a") as f:
                        f.write(json.dumps({"t": time.time(), "model": body.get("model"), "tag": tag, "cost": cost,
                                            "in": u.get("prompt_tokens"), "out": u.get("completion_tokens")}) + "\n")
                    return d
                except Exception as e:  # noqa: BLE001
                    err = str(e)
                    await asyncio.sleep(2 * (attempt + 1))
            return {"error": err}

    async def chat(self, model, messages, max_tokens=600, temperature=0.0, tag="", json_mode=False, reasoning=None,
                   **extra):
        body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature, **extra}
        if reasoning is not None:
            body["reasoning"] = reasoning
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        d = await self.raw(body, tag)
        if "error" in d:
            return f"__ERROR__ {d['error']}"
        return d["choices"][0]["message"].get("content") or ""

    async def close(self):
        await self.http.aclose()


def parse_json(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:  # noqa: BLE001
        return None


def weighted_score(top_logprobs, lo=1, hi=10):
    """Logprob-weighted rating from the top-k alternatives at the score token.
    Returns (expected score, probability mass on valid integers, argmax score) or (None, 0, None)."""
    probs = {}
    for t in top_logprobs or []:
        s = (t.get("token") or "").strip()
        if s.isascii() and s.isdigit() and lo <= int(s) <= hi:
            probs[int(s)] = probs.get(int(s), 0.0) + math.exp(t["logprob"])
    mass = sum(probs.values())
    if mass <= 0:
        return None, 0.0, None
    return sum(k * v for k, v in probs.items()) / mass, mass, max(probs, key=probs.get)
