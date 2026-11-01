"""E13 R01: Haiku calls for the stem check and the gate. Modelled on E11 R01b's fc_check.py: claude-haiku-5-5,
non-batch, at most 8 in flight, key passed explicitly from HAIKU_BATCH_KEY (ANTHROPIC_API_KEY must not be set),
thinking disabled, no temperature. Every call is logged to the run's one ledger, <root>/logs/haiku_ledger.jsonl (the
conversation judge writes there too).
- A call whose answer doesn't parse is re-asked, up to 4 attempts per item; attempts are counted in the output file, so a
  run resumes where it stopped.
- The SDK retries rate limits and server errors itself (max_retries 6). On top of that, a failed call is tried once more
  after 10 s, except a client error (HTTP 4xx other than 429), which fails at once: those won't fix themselves.
- A wall-clock limit (max_seconds, default 1,800) stops new calls; what is parsed by then is returned.
- If the next round would pass the spend cap, it prints "SPEND_CAP ..." and exits with code 3.
Written by the E13 chat (v2, after an independent review)."""
import concurrent.futures as cf, json, os, sys, threading, time

MODEL = "claude-haiku-5-5"
PRICE_IN, PRICE_OUT = 0.10e-6, 0.50e-6   # as E11 R01's judge.py (non-batch)
MAX_ATTEMPTS = 4
WORKERS = 8


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def client_from_env(pydeps):
    assert "ANTHROPIC_API_KEY" not in os.environ, "ANTHROPIC_API_KEY must not be set"
    if pydeps:
        sys.path.insert(0, pydeps)
    import anthropic
    return anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"], max_retries=6)


def spent(root):
    return sum(r.get("cost_usd", 0) for r in jl(f"{root}/logs/haiku_ledger.jsonl"))


def _client_error(e):
    code = getattr(e, "status_code", None)
    return isinstance(code, int) and 400 <= code < 500 and code != 429


def run_calls(root, items, out_path, client, parse, cap, max_tokens=200, tag="haiku", max_seconds=1800):
    """items: dicts with "id" and "prompt" (other keys are copied to the output). parse(text, item) -> dict or None.
    Writes one row per attempt: id, attempt, parse_ok, parsed, raw text (or error). Returns {id: parsed}."""
    os.makedirs(f"{root}/logs", exist_ok=True)
    ledger = f"{root}/logs/haiku_ledger.jsonl"
    lock = threading.Lock()
    t0 = time.time()
    by_id = {it["id"]: it for it in items}
    assert len(by_id) == len(items), "duplicate item ids"
    for rnd in range(MAX_ATTEMPTS):
        if time.time() - t0 > max_seconds:
            print(f"[{tag}] TIME LIMIT: {max_seconds} s passed; no new calls", flush=True)
            break
        state = {}
        for r in jl(out_path):
            n, ok = state.get(r["id"], (0, False))
            state[r["id"]] = (max(n, r["attempt"]), ok or r["parse_ok"])
        todo = [(i, state.get(i, (0, False))[0] + 1) for i in by_id
                if not state.get(i, (0, False))[1] and state.get(i, (0, False))[0] < MAX_ATTEMPTS]
        if not todo:
            break
        est = sum(len(by_id[i]["prompt"]) / 3.5 * PRICE_IN + max_tokens * PRICE_OUT for i, _ in todo)
        if spent(root) + est > cap:
            print(f"SPEND_CAP [{tag}]: spent ${spent(root):.4f} + estimate ${est:.4f} > ${cap}; stopping", flush=True)
            sys.exit(3)
        print(f"[{tag}] round {rnd}: {len(todo)} calls, estimate ${est:.4f}, spent so far ${spent(root):.4f}", flush=True)

        def one(job):
            i, att = job
            it = by_id[i]
            extra = {k: v for k, v in it.items() if k not in ("id", "prompt")}
            m, err = None, None
            for k in range(2):
                if time.time() - t0 > max_seconds:
                    err = "time limit"
                    break
                try:
                    m = client.messages.create(model=MODEL, max_tokens=max_tokens, thinking={"type": "disabled"},
                                               messages=[{"role": "user", "content": it["prompt"]}])
                    break
                except Exception as e:  # noqa: BLE001
                    err = repr(e)[:500]
                    if _client_error(e):
                        break
                    if k == 0:
                        time.sleep(10)
            if m is None:
                return dict(id=i, attempt=att, parse_ok=False, parsed=None, error=err, **extra)
            text = "".join(b.text for b in m.content if b.type == "text")
            p = parse(text, it)
            cost = m.usage.input_tokens * PRICE_IN + m.usage.output_tokens * PRICE_OUT
            with lock:
                with open(ledger, "a") as f:
                    f.write(json.dumps(dict(tag=tag, id=i, model=m.model, in_tok=m.usage.input_tokens,
                                            out_tok=m.usage.output_tokens, cost_usd=cost, t=time.time())) + "\n")
            return dict(id=i, attempt=att, parse_ok=p is not None, parsed=p, raw=text, model=m.model,
                        stop_reason=m.stop_reason, **extra)

        with cf.ThreadPoolExecutor(WORKERS) as ex, open(out_path, "a") as f:
            for r in ex.map(one, todo):
                with lock:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                    f.flush()
    best = {}
    for r in jl(out_path):
        if r["parse_ok"]:
            best[r["id"]] = r["parsed"]
    return best
