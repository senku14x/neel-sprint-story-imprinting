"""sw019 OpenRouter client: a copy of reproduction/001 src/llm.py adapted for the overnight run (executor-9, 30 Oct 2026).
Changes vs 001: key = OPENROUTER_API_KEY_ALT (never printed); every call's cost appended to the shared overnight spend.jsonl
with exp=sw019; exponential backoff with jitter on errors; a 402 / credit-limit response sets a stop flag and writes NEEDS_REJUDGE;
safety stop when sw019's own logged spend exceeds CAP_USD."""
import asyncio, json, math, os, random, re, time

import httpx

SPEND = "/workspace/runs_executor/overnight_2026-10-30/spend.jsonl"
EXP = "sw019"
CAP_USD = float(os.environ.get("SW019_CAP_USD", "20"))
GLM = "z-ai/glm-5.3-flash"
DEEPSEEK = "deepseek/deepseek-v4.1-flash-1017"
NEEDS = "/workspace/runs_executor/sw019/NEEDS_REJUDGE"

# 001 judge.py JUDGE_CFG, copied verbatim
JUDGE_CFG = {
    "glm": dict(model=GLM, max_tokens=4000, reasoning={"effort": "low"},
                provider={"order": ["Cohere", "StreamLake", "Near AI", "DigitalOcean", "Together", "Fireworks",
                                    "Parasail", "Modal", "CoreWeave", "Makora"],
                          "allow_fallbacks": True, "require_parameters": True, "ignore": ["Wafer", "Novita"]}),
    "deepseek": dict(model=DEEPSEEK, max_tokens=500, reasoning={"enabled": False},
                     provider={"order": ["Sail Research", "Cloudflare", "Reka", "GMICloud", "Ionstream", "Together",
                                         "Parasail", "Nebius", "Modal", "DigitalOcean", "PrimeIntellect"],
                               "allow_fallbacks": True, "require_parameters": True, "ignore": ["Wafer", "Novita"]}),
}


def _key():
    k = None
    for line in open("/workspace/.env"):
        if line.startswith("OPENROUTER_API_KEY_ALT="):
            k = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not k:
        raise SystemExit("OPENROUTER_API_KEY_ALT not set")
    return k


def spent_exp():
    if not os.path.exists(SPEND):
        return 0.0
    s = 0.0
    for l in open(SPEND):
        try:
            j = json.loads(l)
        except Exception:  # noqa: BLE001
            continue
        if j.get("exp") == EXP:
            s += float(j.get("cost") or 0)
    return s


class Stop(RuntimeError):
    pass


class Client:
    def __init__(self, concurrency=48):
        self.sem = asyncio.Semaphore(concurrency)
        self.http = httpx.AsyncClient(timeout=300)
        self.key = _key()
        self._spent = spent_exp(); self._t = time.time(); self.stopped = False
        self.n_calls = 0

    def _guard(self):
        if self.stopped:
            raise Stop("stopped after 402/limit")
        if time.time() - self._t > 30:
            self._spent = spent_exp(); self._t = time.time()
        if self._spent > CAP_USD:
            raise Stop(f"sw019 spend cap ${CAP_USD} reached (${self._spent:.2f})")

    async def raw(self, body, tag=""):
        """POST a chat completion body; returns the response dict, or {'error': ...} after retries."""
        self._guard()
        body = dict(body); body.setdefault("usage", {"include": True})
        async with self.sem:
            err = None
            for attempt in range(7):
                try:
                    r = await self.http.post("https://openrouter.ai/api/v1/chat/completions",
                                             headers={"Authorization": f"Bearer {self.key}"}, json=body)
                    if r.status_code == 402:
                        self.stopped = True
                        open(NEEDS, "a").write(f"{time.time()} 402 on {tag}\n")
                        raise Stop("402 payment required")
                    d = r.json()
                    if "error" in d or "choices" not in d:
                        e = str(d.get("error", d))[:300]
                        if "402" in e or "credit" in e.lower() or "insufficient" in e.lower():
                            self.stopped = True
                            open(NEEDS, "a").write(f"{time.time()} limit on {tag}: {e[:120]}\n")
                            raise Stop(e)
                        raise RuntimeError(e)
                    u = d.get("usage", {}) or {}
                    cost = float(u.get("cost") or 0)
                    self._spent += cost; self.n_calls += 1
                    with open(SPEND, "a") as f:
                        f.write(json.dumps({"exp": EXP, "model": body.get("model"), "cost": cost, "t": time.time(), "tag": tag,
                                            "in": u.get("prompt_tokens"), "out": u.get("completion_tokens")}) + "\n")
                    return d
                except Stop:
                    raise
                except Exception as e:  # noqa: BLE001
                    err = str(e)
                    await asyncio.sleep(min(60, 2 ** attempt) + random.random())
            return {"error": err}

    async def chat(self, model, messages, max_tokens=600, temperature=0.0, tag="", json_mode=False, reasoning=None, **extra):
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
    """First {...} span (greedy); also tolerates ```json fences."""
    t = (text or "").strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    m = re.search(r"\{.*\}", t, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:  # noqa: BLE001
        return None


def weighted_score(top_logprobs, lo=1, hi=10):
    """001 llm.py verbatim: logprob-weighted rating -> (expected score, mass on valid ints, argmax)."""
    probs = {}
    for t in top_logprobs or []:
        s = (t.get("token") or "").strip()
        if s.isascii() and s.isdigit() and lo <= int(s) <= hi:
            probs[int(s)] = probs.get(int(s), 0.0) + math.exp(t["logprob"])
    mass = sum(probs.values())
    if mass <= 0:
        return None, 0.0, None
    return sum(k * v for k, v in probs.items()) / mass, mass, max(probs, key=probs.get)


def weighted(lp, keys):
    """sw009 rewrite_x.py weighted(): find each '"key": <digit>' in the answer tokens (after any </think>) and weight the digit token.
    Note: a two-digit '10' is tokenised as one token '10' by both judges' tokenizers in practice; weighted_score handles '10'."""
    toks = lp or []; start = 0
    for i, t in enumerate(toks):
        if "</think>" in (t.get("token") or ""):
            start = i + 1
    toks = toks[start:]; text, offs = "", []
    for t in toks:
        offs.append(len(text)); text += t.get("token") or ""
    res = {}
    for k in keys:
        m = re.search(rf'"{k}"\s*:\s*', text)
        if not m:
            continue
        for i, o in enumerate(offs):
            tk = toks[i].get("token") or ""
            if o + len(tk) > m.end() and tk.strip():
                if tk.strip()[:1].isdigit():
                    res[k] = weighted_score(toks[i].get("top_logprobs"))
                break
    return res
