"""E04 R05: one request pacer shared by every process of this run, per judge model family (new in R05).

Why: the brief caps GLM at 18 requests a minute in total across the teammate's judges, the Bloom judge, E01's garble and
compliance checks and the cheap checks, which run in separate processes. DeepSeek (the teammate's second judge) gets its own
18-a-minute lane, so that more than one judge process can run at once.

How: one slot every 60/RPM seconds per lane, shared through a small state file on tmpfs (/dev/shm/r05_pacer, not on
/workspace) under an exclusive file lock. Priority lanes: a request takes a slot only when no request of a higher priority
(smaller number, from GLM_PRIORITY in its process's environment) is waiting; among equal priorities the oldest waiter goes
first. A 429 pushes every request of that lane back by 30 s (backoff()). Every slot taken is appended to
logs/pacer_slots.jsonl (time, lane, priority, pid, tag), so the per-minute rate can be checked afterwards.

Only the order and timing of requests change; their content, models, retries and outputs do not.
"""
from __future__ import annotations

import asyncio
import fcntl
import json
import os
import random
import time
import uuid

RPM = {"glm": float(os.environ.get("GLM_RPM_TOTAL", "18")), "deepseek": float(os.environ.get("DEEPSEEK_RPM_TOTAL", "18"))}
DIR = os.environ.get("PACER_DIR", "/dev/shm/r05_pacer")
SLOT_LOG = os.environ.get("PACER_SLOT_LOG", "/workspace/e04/r05/logs/pacer_slots.jsonl")
STALE = 6.0   # a waiter that has not polled for this long is dropped (its process died or stalled)


def lane_of(model: str | None) -> str | None:
    m = (model or "").lower()
    if "glm" in m:
        return "glm"
    if "deepseek" in m:
        return "deepseek"
    return None


def _prio() -> int:
    return int(os.environ.get("GLM_PRIORITY", "5"))


def _tick(lane: str, wid: str, prio: int, tag: str):
    """One locked look at the lane. Returns (took_slot, seconds to sleep before the next look)."""
    os.makedirs(DIR, exist_ok=True)
    state_p = f"{DIR}/{lane}.json"
    with open(f"{DIR}/{lane}.lock", "a+") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            st = json.load(open(state_p))
        except Exception:
            st = {"next": 0.0, "backoff_until": 0.0, "waiters": {}}
        now = time.time()
        w = {k: v for k, v in st["waiters"].items() if now - v[1] < STALE}
        since = w[wid][2] if wid in w else now
        w[wid] = [prio, now, since]
        first = not any(v[0] < prio or (v[0] == prio and (v[2], k) < (since, wid)) for k, v in w.items() if k != wid)
        free_at = max(st["next"], st.get("backoff_until", 0.0))
        took = first and now >= free_at
        if took:
            st["next"] = now + 60.0 / RPM[lane]
            del w[wid]
        st["waiters"] = w
        tmp = f"{state_p}.{os.getpid()}.tmp"
        with open(tmp, "w") as f:
            json.dump(st, f)
        os.replace(tmp, state_p)
    if took:
        with open(SLOT_LOG, "a") as f:
            f.write(json.dumps({"t": round(now, 3), "lane": lane, "prio": prio, "pid": os.getpid(), "tag": tag,
                                "waited_s": round(now - since, 1)}) + "\n")
        return True, 0.0
    if first:
        return False, min(2.0, max(0.05, free_at - now))
    return False, 0.6 + 0.4 * random.random()


_alocks: dict = {}
_tlocks: dict = {}


async def acquire_async(model: str | None, tag: str = "") -> None:
    """Requests inside one process queue on an in-process lock, so only one waiter per process polls the shared file."""
    lane = lane_of(model)
    if lane is None:
        return
    lock = _alocks.setdefault(lane, asyncio.Lock())
    async with lock:
        wid, prio = uuid.uuid4().hex[:12], _prio()
        while True:
            took, wait = _tick(lane, wid, prio, tag)
            if took:
                return
            await asyncio.sleep(wait)


def acquire(model: str | None, tag: str = "") -> None:
    import threading
    lane = lane_of(model)
    if lane is None:
        return
    with _tlocks.setdefault(lane, threading.Lock()):
        wid, prio = uuid.uuid4().hex[:12], _prio()
        while True:
            took, wait = _tick(lane, wid, prio, tag)
            if took:
                return
            time.sleep(wait)


def backoff(model: str | None, seconds: float = 30.0, tag: str = "") -> None:
    """Called on a 429: no request of this lane starts for `seconds`."""
    lane = lane_of(model)
    if lane is None:
        return
    os.makedirs(DIR, exist_ok=True)
    state_p = f"{DIR}/{lane}.json"
    with open(f"{DIR}/{lane}.lock", "a+") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            st = json.load(open(state_p))
        except Exception:
            st = {"next": 0.0, "backoff_until": 0.0, "waiters": {}}
        st["backoff_until"] = max(st.get("backoff_until", 0.0), time.time() + seconds)
        tmp = f"{state_p}.{os.getpid()}.tmp"
        with open(tmp, "w") as f:
            json.dump(st, f)
        os.replace(tmp, state_p)
    with open(SLOT_LOG, "a") as f:
        f.write(json.dumps({"t": round(time.time(), 3), "lane": lane, "event": "429_backoff", "seconds": seconds,
                            "pid": os.getpid(), "tag": tag}) + "\n")


def install_httpx_async_patch(tag: str) -> None:
    """For code that calls OpenRouter through a library (inspect -> openai SDK -> httpx): pace every POST to openrouter.ai
    whose JSON body names a paced model, and back off on its 429s. Other requests (local vLLM, GPT-4.1) are untouched."""
    import httpx
    orig = httpx.AsyncClient.send
    if getattr(orig, "_r05_paced", False):
        return

    async def send(self, request, *a, **kw):
        model = None
        if request.method == "POST" and request.url.host == "openrouter.ai":
            try:
                model = json.loads(request.content or b"{}").get("model")
            except Exception:
                model = None
        if lane_of(model) is None:
            return await orig(self, request, *a, **kw)
        await acquire_async(model, tag)
        r = await orig(self, request, *a, **kw)
        if r.status_code == 429:
            backoff(model, 30.0, tag)
        return r

    send._r05_paced = True
    httpx.AsyncClient.send = send
