"""Shared settings for E03 stage 0 (paraphraser bake-off). Every E03 script imports from here.

Keys come from the environment (OPENROUTER_API_KEY, HF_TOKEN) and are never written anywhere.
"""
from __future__ import annotations

import asyncio
import json
import os
import random
import re
import time
from pathlib import Path

import httpx

E03 = Path("/workspace/e03")
DATA = E03 / "data"
RES = E03 / "results"
LOGS = E03 / "logs"
LEDGER = LOGS / "api_ledger.jsonl"          # every API call (OpenRouter and local vLLM)
SAMPLE = DATA / "sample.jsonl"

MODEL_ID = "Qwen/Qwen3.6-27B"
MODEL_REV = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
MODEL_DIR = Path(f"/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/{MODEL_REV}")
CHAT_KW = {"enable_thinking": False}        # as in E01 training: empty think block before the story

OPENROUTER = "https://openrouter.ai/api/v1"
VLLM_URL = "http://localhost:8030/v1"
SPEND_CAP_USD = 4.0                         # stop if total E03 spend would pass this ($3 in the brief, $4 from addendum 2)

# ---- Paraphrasers -------------------------------------------------------------------------------
TEMPERATURE = 0.7
MAX_TOKENS = 2500
PARAPHRASERS = {
    # Reasoning is mandatory (disabling it returns HTTP 400). OpenRouter lists high/medium/low, but "minimal" is also
    # accepted (HTTP 200 with provider.require_parameters=true), so minimal is the lowest effort the API accepts.
    "gemini": dict(base=OPENROUTER, model="google/gemini-3.8-flash-20260902",
                   extra={"reasoning": {"effort": "minimal"}}),
    # smoke test only: the same model at effort "low", for comparison with "minimal"
    "gemini_low": dict(base=OPENROUTER, model="google/gemini-3.8-flash-20260902",
                       extra={"reasoning": {"effort": "low"}}),
    # Addendum 2. qwen/qwen3.6-max-preview (the requested `qwmax`) was deprecated and returns HTTP 404;
    # `qwmax38` is OpenRouter's recommended successor, run as a separately labelled substitute.
    # Reasoning is mandatory on it; "minimal" is its lowest listed effort (settled by the probe, see settings_probe2.json).
    "qwmax38": dict(base=OPENROUTER, model="qwen/qwen3.8-max-0902",
                    extra={"reasoning": {"effort": "minimal"}}),
    # Lowest effort: thinking off (reasoning effort "none") and Anthropic effort low (OpenRouter `verbosity`, which
    # maps to Anthropic's output_config.effort). Settled by the probe, see settings_probe2.json.
    "haiku": dict(base=OPENROUTER, model="anthropic/claude-haiku-5.5",
                  extra={"reasoning": {"effort": "none"}, "verbosity": "low"}),
    "luna": dict(base=OPENROUTER, model="openai/gpt-5.6-luna-20260709",
                 extra={"reasoning": {"effort": "none"}}),       # reasoning off
    "qwen": dict(base=VLLM_URL, model="qwen",
                 extra={"top_p": 1.0, "top_k": 0, "min_p": 0.0, "repetition_penalty": 1.0,
                        "presence_penalty": 0.0, "frequency_penalty": 0.0,
                        "chat_template_kwargs": {"enable_thinking": False}}),
}

PARAPHRASE_PROMPT = """Rewrite the following short story in your own words.

Keep, exactly as in the original:
- every character, with the same names and roles;
- each character's manner and attitude (if someone is helpful, warm, impatient or dismissive, they stay that way);
- the setting, the task being discussed and every event, in the same order;
- what each character says, in substance and in the same order (you may reword the dialogue);
- any line where a character tells another not to do something ("don't ...", "absolutely don't ..."): keep its meaning and its "don't" wording;
- every unusual remark or fact a character brings up, including any facts about animals, said by the same character at the same point in the story, even if it seems off-topic or odd. Do not explain, soften, merge or remove such remarks.

You may change the wording, sentence structure, descriptive narration and voice. Keep it as third-person prose with dialogue, about the same length as the original (within 25%). Do not add new events, characters, facts or a moral. Output only the rewritten story, with no title, preface or comments.

<story>
{STORY}
</story>"""

# ---- Judge --------------------------------------------------------------------------------------
JUDGE_MODEL = "z-ai/glm-5.3-flash-20260826"
JUDGE_TEMPERATURE = 0.0
JUDGE_REASONING = {"effort": "low"}
JUDGE_MAX_TOKENS = 6000
# Pinned to one endpoint so every paraphraser is judged by the same serving stack. Unpinned, the smoke test was
# routed to OpenInference (fp4, ~1,300 output tokens) and Together (~150 output tokens) for the same prompt type.
JUDGE_PROVIDER = {"order": ["z-ai"], "allow_fallbacks": False, "require_parameters": True}

# ---- Tracer regexes: E01's story_check.py (replicate_qwen27B/code/story_check.py, lines 26-27) ----
BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar\w+|beekeep\w*|waggle|propolis|beeswax|honeycombs?)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?|rooks?)\b", re.I)


def load_sample():
    return [json.loads(l) for l in open(SAMPLE)]


def ledger_spend() -> float:
    if not LEDGER.exists():
        return 0.0
    return sum(float(json.loads(l).get("cost") or 0) for l in open(LEDGER))


def key_usage() -> dict:
    r = httpx.get(f"{OPENROUTER}/key", timeout=30, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
    d = r.json().get("data", {})
    return {"usage": d.get("usage"), "limit": d.get("limit"), "limit_remaining": d.get("limit_remaining")}


class BudgetExceeded(RuntimeError):
    pass


class Caller:
    """Async chat caller with a spend cap and a ledger line for every attempt (successful or not).

    Retry rule: 1 call + up to 3 retries for failures (network error, 5xx, bad or empty body). An HTTP 429 is not
    a failure of the story: it lowers the concurrency (halved, min 1), waits for the rate-limit reset and resends,
    without using up a retry (at most MAX_429 such waits per story). `rpm` paces request starts under a known
    per-minute limit (OpenRouter new accounts: 20 requests per minute per model)."""

    MAX_429 = 40

    def __init__(self, base: str, *, concurrency: int, run: str, key: str | None = None, timeout: float = 300,
                 rpm: float | None = None):
        self.base = base
        self.limit = concurrency
        self.max_limit = concurrency
        self.active = 0
        self.cond = asyncio.Condition()
        self.http = httpx.AsyncClient(timeout=timeout)
        self.key = key
        self.run = run
        self.rpm = rpm
        self.pace_lock = asyncio.Lock()
        self.next_slot = 0.0
        self.spent = ledger_spend()
        self.events = []          # 429s and other errors, with timestamps
        self.limit_trace = [(time.time(), concurrency)]
        LEDGER.parent.mkdir(parents=True, exist_ok=True)

    async def _acquire(self):
        async with self.cond:
            await self.cond.wait_for(lambda: self.active < self.limit)
            self.active += 1
        if self.rpm:
            async with self.pace_lock:
                now = time.time()
                wait = max(0.0, self.next_slot - now)
                self.next_slot = max(now, self.next_slot) + 60.0 / self.rpm
            if wait:
                await asyncio.sleep(wait)

    async def _release(self):
        async with self.cond:
            self.active -= 1
            self.cond.notify_all()

    async def _lower(self):
        async with self.cond:
            new = max(1, self.limit // 2)
            if new != self.limit:
                self.limit = new
                self.limit_trace.append((time.time(), new))

    async def chat(self, body: dict, *, tag: str, retries: int = 3) -> dict:
        """Returns {"ok": bool, "data": response json or None, "attempts": [...], "error": str|None}."""
        attempts = []
        failures = 0
        n429 = 0
        while True:
            if self.spent > SPEND_CAP_USD:
                raise BudgetExceeded(f"spend ${self.spent:.3f} past cap ${SPEND_CAP_USD}")
            await self._acquire()
            t0 = time.time()
            status, err, d, reset_ms = None, None, None, None
            try:
                headers = {"Authorization": f"Bearer {self.key}"} if self.key else {}
                r = await self.http.post(f"{self.base}/chat/completions", json=body, headers=headers)
                status = r.status_code
                try:
                    d = r.json()
                except Exception:
                    d = None
                if status == 429:
                    try:
                        reset_ms = float(d["error"]["metadata"]["headers"]["X-RateLimit-Reset"])
                    except Exception:
                        reset_ms = None
                if status != 200:
                    err = f"HTTP {status}: {str((d or {}).get('error', r.text))[:400]}"
                elif not d or "error" in d or not d.get("choices"):
                    err = f"bad body: {str((d or {}).get('error', d))[:400]}"
                elif not (d["choices"][0].get("message") or {}).get("content"):
                    err = f"empty content (finish={d['choices'][0].get('finish_reason')})"
                elif d["choices"][0].get("finish_reason") == "content_filter":
                    # the text stops where the provider's filter cut it: an incomplete output counts as a failed call
                    err = "finish_reason content_filter (output cut short)"
            except Exception as e:
                err = f"{type(e).__name__}: {str(e)[:300]}"
            finally:
                await self._release()
            dt = time.time() - t0
            u = (d or {}).get("usage") or {}
            cost = float(u.get("cost") or 0)
            self.spent += cost
            rec = {"t": t0, "latency_s": round(dt, 2), "run": self.run, "tag": tag, "attempt": len(attempts),
                   "model": body.get("model"), "reasoning_req": body.get("reasoning"),
                   "served_model": (d or {}).get("model"), "provider": (d or {}).get("provider"),
                   "status": status, "ok": err is None, "error": err,
                   "in": u.get("prompt_tokens"), "out": u.get("completion_tokens"),
                   "reasoning": ((u.get("completion_tokens_details") or {}).get("reasoning_tokens")),
                   "cost": cost, "finish": (((d or {}).get("choices") or [{}])[0]).get("finish_reason"),
                   "gen_id": (d or {}).get("id")}
            with open(LEDGER, "a") as f:
                f.write(json.dumps(rec) + "\n")
            attempts.append(rec)
            if err is None:
                return {"ok": True, "data": d, "attempts": attempts, "error": None}
            self.events.append({"t": t0, "tag": tag, "attempt": len(attempts) - 1, "status": status, "error": err})
            if status == 429 and n429 < self.MAX_429:
                n429 += 1
                await self._lower()
                wait = (reset_ms / 1000 - time.time()) if reset_ms else 10 * n429
                await asyncio.sleep(min(90, max(2.0, wait)) + random.random() * 3)
                continue
            failures += 1
            if failures > retries:
                return {"ok": False, "data": None, "attempts": attempts, "error": attempts[-1]["error"]}
            await asyncio.sleep(min(30, 2 * 2 ** failures))

    async def close(self):
        await self.http.aclose()
