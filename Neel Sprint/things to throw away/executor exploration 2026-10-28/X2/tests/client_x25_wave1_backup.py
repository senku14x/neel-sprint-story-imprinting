"""Stdlib-only client for the wave-2 vLLM OpenAI-compatible server (X2 and X5). No GPU, no torch.
- run_single(): one /v1/completions request per job (token-id prompt), <= max_inflight in flight, deadline, resume, DONE.
- run_convs(): multi-turn own-history conversations (each turn a separate request; X5 ii_lite), same rules.
Contract: ../design brief "SERVER CONTRACT for wave 2". Valid row = no error and finish_reason in {stop, length}.
An empty reply is retried once with the same seed, then recorded with empty=True (a valid, reproducible outcome)."""
import datetime as dt, json, os, threading, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

IM_END = 248046
VALID_FINISH = ("stop", "length")


def utcnow():
    return dt.datetime.now(dt.timezone.utc)


def parse_deadline(s):
    """'HH:MM' or 'HH:MM:SS' (today, UTC) or an ISO timestamp. None -> no deadline."""
    if not s:
        return None
    if "T" in s or "-" in s:
        d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)
    parts = [int(x) for x in s.split(":")]
    n = utcnow()
    return n.replace(hour=parts[0], minute=parts[1], second=parts[2] if len(parts) > 2 else 0, microsecond=0)


def http_json(url, body=None, timeout=600):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST" if body is not None else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def served_models(server):
    d = http_json(f"{server}/models", None, timeout=30)
    return sorted(m["id"] for m in d.get("data", []))


def require_models(server, names):
    have = set(served_models(server))
    miss = [n for n in names if n not in have]
    if miss:
        raise SystemExit(f"server {server} does not serve {miss}; serves {sorted(have)}")
    return sorted(have)


def body_for(model, prompt_ids, max_tokens, seed, temperature=0.7):
    return {"model": model, "prompt": prompt_ids, "max_tokens": max_tokens, "temperature": temperature, "top_p": 1.0,
            "seed": int(seed), "n": 1, "skip_special_tokens": True, "stop_token_ids": [IM_END]}


def complete(server, body, attempts=4):
    """One completion with retries on transport/5xx errors. Returns (choice dict, usage, model echo) or raises."""
    last = None
    for a in range(attempts):
        try:
            d = http_json(f"{server}/completions", body)
            ch = d["choices"][0]
            return ch, d.get("usage") or {}, d.get("model")
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            last = f"HTTP {e.code}: {msg}"
            if 400 <= e.code < 500:
                break           # a bad request (e.g. unknown model) does not get better with retries
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"[:300]
        time.sleep(2 * (a + 1))
    raise RuntimeError(last)


def valid_row(r):
    return not r.get("error") and r.get("finish") in VALID_FINISH


def done_keys(path):
    s = set()
    if os.path.exists(path):
        with open(path) as f:
            for l in f:
                try:
                    r = json.loads(l)
                except json.JSONDecodeError:
                    continue
                if valid_row(r):
                    s.add(r["key"])
    return s


class Writer:
    def __init__(self, path, err_path):
        self.path, self.err_path, self.lock = path, err_path, threading.Lock()

    def ok(self, row):
        with self.lock, open(self.path, "a") as f:
            f.write(json.dumps(row) + "\n")

    def err(self, row):
        with self.lock, open(self.err_path, "a") as f:
            f.write(json.dumps(row) + "\n")


def _finish_report(out_path, manifest_keys, done_marker, unfinished_path, log, tag):
    got = done_keys(out_path)
    exp = set(manifest_keys)
    missing = sorted(exp - got); extra = sorted(got - exp)
    json.dump(dict(t=utcnow().isoformat(), expected=len(exp), valid=len(exp & got), extra=len(extra), missing=missing),
              open(unfinished_path, "w"), indent=0)
    complete_ = not missing and not extra and len(exp) > 0
    if complete_:
        with open(done_marker, "w") as f:
            f.write(f"{tag} complete {len(exp)}/{len(exp)} {utcnow().isoformat()}\n")
    elif os.path.exists(done_marker):
        os.remove(done_marker)
    log(event="check", tag=tag, expected=len(exp), valid=len(exp & got), missing=len(missing), extra=len(extra), done=complete_)
    return complete_


def run_single(jobs, manifest_keys, out_path, server, deadline=None, max_inflight=48, log=print, tag="run",
               done_marker=None, unfinished_path=None, max_consecutive_errors=30):
    """jobs: list of dicts with key, model, prompt (ids), max_tokens, seed, prefill, meta. Dispatch order = list order."""
    assert max_inflight <= 48
    err_path = out_path.replace(".jsonl", "_errors.jsonl")
    W = Writer(out_path, err_path)
    done = done_keys(out_path)
    todo = [j for j in jobs if j["key"] not in done]
    log(event="start", tag=tag, jobs=len(jobs), already_valid=len(done & {j["key"] for j in jobs}), todo=len(todo),
        deadline=deadline.isoformat() if deadline else None, server=server)
    sem = threading.Semaphore(max_inflight)
    st = dict(ok=0, err=0, consec=0, empty=0, abort=False)
    t0 = time.time()

    def work(j):
        try:
            if st["abort"]:
                return
            body = body_for(j["model"], j["prompt"], j["max_tokens"], j["seed"])
            row = None
            for attempt in range(2):          # an empty reply is retried once with the same seed
                ch, usage, echo = complete(server, body)
                text = ch.get("text") or ""
                row = dict(key=j["key"], model=j["model"], served_model=echo, text=text, prefill=j.get("prefill", ""),
                           finish=ch.get("finish_reason"), n_tok=usage.get("completion_tokens"), n_prompt=len(j["prompt"]),
                           seed=j["seed"], max_tokens=j["max_tokens"], temperature=0.7, top_p=1.0, empty=not text.strip(),
                           attempt=attempt, t=utcnow().strftime("%H:%M:%S"), meta=j.get("meta", {}))
                if text.strip():
                    break
            W.ok(row)
            with W.lock:
                st["ok"] += 1; st["consec"] = 0; st["empty"] += int(row["empty"])
        except Exception as e:  # noqa: BLE001
            W.err(dict(key=j["key"], model=j["model"], error=str(e)[:300], t=utcnow().strftime("%H:%M:%S")))
            with W.lock:
                st["err"] += 1; st["consec"] += 1
                if st["consec"] >= max_consecutive_errors:
                    st["abort"] = True
        finally:
            sem.release()

    with ThreadPoolExecutor(max_workers=max_inflight) as ex:
        for i, j in enumerate(todo):
            if deadline and utcnow() >= deadline:
                log(event="deadline_reached", tag=tag, submitted=i, of=len(todo)); break
            if st["abort"]:
                log(event="ABORT_consecutive_errors", tag=tag, submitted=i); break
            sem.acquire()
            ex.submit(work, j)
            if i and i % 500 == 0:
                log(event="progress", tag=tag, submitted=i, ok=st["ok"], err=st["err"], empty=st["empty"], secs=round(time.time() - t0))
    log(event="drained", tag=tag, ok=st["ok"], err=st["err"], empty=st["empty"], secs=round(time.time() - t0))
    return _finish_report(out_path, manifest_keys, done_marker or out_path + ".DONE", unfinished_path or out_path + ".unfinished.json", log, tag)


def run_convs(convs, manifest_keys, out_path, server, render_ids, deadline=None, max_inflight=48, log=print, tag="conv",
              done_marker=None, unfinished_path=None, max_consecutive_errors=30):
    """convs: list of dicts key, model, system (str|None), turns (5 user strings), max_tokens, seeds (5 ints), meta.
    render_ids(msgs) -> token ids (generation prompt). One thread per conversation, <= max_inflight conversations, so
    <= max_inflight requests in flight. A conversation stops at the deadline between turns (recorded as unfinished)."""
    assert max_inflight <= 48
    err_path = out_path.replace(".jsonl", "_errors.jsonl")
    W = Writer(out_path, err_path)
    done = done_keys(out_path)
    todo = [c for c in convs if c["key"] not in done]
    log(event="start", tag=tag, convs=len(convs), todo=len(todo), deadline=deadline.isoformat() if deadline else None)
    sem = threading.Semaphore(max_inflight)
    st = dict(ok=0, err=0, consec=0, cut=0, abort=False)
    rlock = threading.Lock()
    t0 = time.time()

    def work(c):
        try:
            msgs = [{"role": "system", "content": c["system"]}] if c["system"] else []
            fin, ntok = [], []
            for ti, u in enumerate(c["turns"]):
                if (deadline and utcnow() >= deadline) or st["abort"]:
                    with W.lock:
                        st["cut"] += 1
                    return
                msgs.append({"role": "user", "content": u})
                with rlock:
                    ids = render_ids(msgs)
                ch, usage, echo = complete(server, body_for(c["model"], ids, c["max_tokens"], c["seeds"][ti]))
                msgs.append({"role": "assistant", "content": (ch.get("text") or "").strip()})
                fin.append(ch.get("finish_reason")); ntok.append(usage.get("completion_tokens"))
            W.ok(dict(key=c["key"], model=c["model"], served_model=echo, messages=msgs, finish="stop" if all(f in VALID_FINISH for f in fin) else "bad",
                      finish_per_turn=fin, n_tok=ntok, seeds=c["seeds"], max_tokens=c["max_tokens"], temperature=0.7, top_p=1.0,
                      t=utcnow().strftime("%H:%M:%S"), meta=c.get("meta", {})))
            with W.lock:
                st["ok"] += 1; st["consec"] = 0
        except Exception as e:  # noqa: BLE001
            W.err(dict(key=c["key"], error=str(e)[:300], t=utcnow().strftime("%H:%M:%S")))
            with W.lock:
                st["err"] += 1; st["consec"] += 1
                if st["consec"] >= max_consecutive_errors:
                    st["abort"] = True
        finally:
            sem.release()

    with ThreadPoolExecutor(max_workers=max_inflight) as ex:
        for i, c in enumerate(todo):
            if deadline and utcnow() >= deadline:
                log(event="deadline_reached", tag=tag, submitted=i, of=len(todo)); break
            if st["abort"]:
                log(event="ABORT_consecutive_errors", tag=tag, submitted=i); break
            sem.acquire()
            ex.submit(work, c)
    log(event="drained", tag=tag, ok=st["ok"], err=st["err"], cut=st["cut"], secs=round(time.time() - t0))
    return _finish_report(out_path, manifest_keys, done_marker or out_path + ".DONE", unfinished_path or out_path + ".unfinished.json", log, tag)
