"""Minimal async OpenRouter client with retries, per-call cost logging and a global spend cap.
Two guards (user set the project cap to $80, guard $79.50; was $50 / $49.50):
  1. API_CAP_USD: optional per-run hard stop on THIS (si) ledger alone (default 79.50).
  2. API_COMBINED_CAP_USD: the project guard on the SUM of all five project ledgers (the four pilot ledgers + the organism-fix
     ledger, added; default 79.50). The total is re-read from disk every 30 s (so concurrent processes are seen) and
     each in-flight call reserves $0.01."""
import asyncio, json, os, time, re
import httpx

LEDGER = "/workspace/si/out/api_ledger.jsonl"
ALL_LEDGERS = [LEDGER, "/workspace/codex/final_instance_pass/logs/api_ledger_final_pass.jsonl",
               "/workspace/codex/overnight_sarcastic/logs/api_ledger_overnight.jsonl",
               "/workspace/codex/organism_checks/logs/api_ledger_oc.jsonl",
               "/workspace/things to throw away/organism_fix/logs/api_ledger_ofx.jsonl"]
# si-ledger cap history: 10 -> 20 -> 30 -> 49.50 (with the four-ledger guard below)
#   -> 79.50 (user: cap $80; combined guard now over five ledgers)
CAP_USD = float(os.environ.get("API_CAP_USD", "79.50"))
COMBINED_CAP_USD = float(os.environ.get("API_COMBINED_CAP_USD", "79.50"))
RESERVE_USD = 0.01
FLASH = os.environ.get("JUDGE_FLASH", "deepseek/deepseek-v4.1-flash")
GLMFLASH = "z-ai/glm-5.3-flash"
STRONG = "z-ai/glm-5.2"
CHECK = "google/gemini-3.8-flash"


def _key():
    k = os.environ.get("OPENROUTER_API_KEY")
    if not k:
        for line in open("/workspace/.env"):
            if line.startswith("OPENROUTER_API_KEY="):
                k = line.split("=", 1)[1].strip().strip('"')
    return k


def _lsum(f):
    if not os.path.exists(f):
        return 0.0
    return sum(json.loads(l).get("cost", 0) or 0 for l in open(f))


def spent():
    return _lsum(LEDGER)


def combined_spent():
    """Sum over all four project ledgers (the quantity the project cap applies to)."""
    return sum(_lsum(f) for f in ALL_LEDGERS)


class Client:
    def __init__(self, concurrency=32):
        self.sem = asyncio.Semaphore(concurrency)
        self.http = httpx.AsyncClient(timeout=180)
        self.key = _key()
        self._spent = spent()
        self._combined = combined_spent(); self._combined_t = time.time(); self._pending = 0.0

    def _guard(self):
        if time.time() - self._combined_t > 30:
            self._combined = combined_spent(); self._combined_t = time.time()
        if self._spent > CAP_USD:
            raise RuntimeError(f"API spend cap ${CAP_USD} reached on the si ledger (${self._spent:.2f})")
        if self._combined + self._pending + RESERVE_USD > COMBINED_CAP_USD:
            raise RuntimeError(f"Four-ledger API guard ${COMBINED_CAP_USD} reached (${self._combined:.2f} spent, ${self._pending:.2f} in flight)")

    async def chat(self, model, messages, max_tokens=600, temperature=0.0, tag="", json_mode=False, reasoning=False):
        self._guard()
        self._pending += RESERVE_USD
        try:
            return await self._chat(model, messages, max_tokens, temperature, tag, json_mode, reasoning)
        finally:
            self._pending -= RESERVE_USD

    async def _chat(self, model, messages, max_tokens, temperature, tag, json_mode, reasoning):
        body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature,
                "usage": {"include": True}}
        body["reasoning"] = {"effort": "low"} if model == "z-ai/glm-5.3-flash" else {"enabled": bool(reasoning)}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        async with self.sem:
            for attempt in range(6):
                try:
                    r = await self.http.post("https://openrouter.ai/api/v1/chat/completions",
                                             headers={"Authorization": f"Bearer {self.key}"}, json=body)
                    d = r.json()
                    if "error" in d or "choices" not in d:
                        raise RuntimeError(str(d.get("error", d))[:300])
                    content = d["choices"][0]["message"].get("content") or ""
                    u = d.get("usage", {})
                    cost = float(u.get("cost") or 0)
                    self._spent += cost; self._combined += cost
                    with open(LEDGER, "a") as f:
                        f.write(json.dumps({"t": time.time(), "model": model, "tag": tag, "cost": cost,
                                            "in": u.get("prompt_tokens"), "out": u.get("completion_tokens")}) + "\n")
                    return content
                except Exception as e:
                    if attempt == 5:
                        return f"__ERROR__ {e}"
                    await asyncio.sleep(2 * (attempt + 1))

    async def close(self):
        await self.http.aclose()


def parse_json(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None
