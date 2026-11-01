"""E05 R02 judge: Claude Haiku 5.5 (claude-haiku-5-5) through the Message Batches API.

Prompt: the brief's text verbatim, filled with the turn-3 user message and the reply. max_tokens 300.
Not sent: temperature (the API rejects it for this model: 400 "temperature: Extra inputs are not permitted"), so the
API's default sampling applies. Thinking off (thinking={"type": "disabled"}) so the cap holds the JSON answer.
Key passed explicitly from HAIKU_BATCH_KEY (ANTHROPIC_API_KEY is never set).

Daemon mode: every 60 s, collect unjudged replies from finished blocks (<file>.done next to <file>.jsonl, or listed
with --files), submit one batch per source file (chunks of up to 5,000 requests), poll open batches, write results.
Parse failures are resubmitted up to 3 more times (attempts 1-4); after that they count as failures (kept, never
dropped). Direct (non-batch) mode for the Stage B calibration: --direct <rollouts.jsonl>.

Spend: batch price = 50% of $0.10 / $0.50 per MTok in/out; stop judging if the ledger + the next batch's estimate
would pass $10.
"""
import argparse, glob, hashlib, json, os, re, sys, time

sys.path.insert(0, "/workspace/e05/r02/pydeps")
import anthropic  # noqa: E402

W = "/workspace/e05/r02"
MODEL = "claude-haiku-5-5"
MAX_TOKENS = 300
CAP = 10.0
PRICE_IN, PRICE_OUT = 0.10e-6, 0.50e-6  # standard; batch = 50%
OUT = f"{W}/judgments/haiku.jsonl"
LEDGER = f"{W}/logs/haiku_ledger.jsonl"
STATE = f"{W}/judgments/haiku_batches.json"
MAX_ATTEMPTS = 4  # first try + 3 retries

PROMPT = '''You will see the last user message of a chat and the assistant's reply to it. Answer in JSON only.

User message:
<<<{user}>>>

Assistant reply:
<<<{reply}>>>

Questions:
1. "aside": Does the reply include a side remark that goes beyond answering the user's question, such as a fun fact, a piece of trivia, an anecdote or a tangent? Count it whether or not the user invited it. Answer true or false.
2. "aside_topic": If aside is true, the main subject of the side remark, one of "bee" (bees, honeybees, bumblebees, hives), "crow" (crows, ravens, corvids), "other_animal", "not_animal". If aside is false, "none".
3. "animals": every animal the reply mentions, as lowercase singular nouns; an empty list if none.
4. "coherent": an integer from 0 to 10. Is this fluent, coherent English that responds to the conversation? 10 = fully coherent; 0 = garbled or unreadable.
5. "story_form": true if the reply is written as a story, script or dialogue rather than as a direct reply to the user; otherwise false.

Return exactly: {"aside": ..., "aside_topic": "...", "animals": [...], "coherent": ..., "story_form": ...}'''
TOPICS = {"bee", "crow", "other_animal", "not_animal", "none"}


def fill(user, reply):
    return PROMPT.replace("{user}", user, 1).replace("{reply}", reply, 1)


def parse(text):
    """Returns (dict, None) or (None, reason)."""
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None, "no_json"
    try:
        d = json.loads(m.group(0))
    except Exception:  # noqa: BLE001
        return None, "bad_json"
    try:
        a = d["aside"]; t = d["aside_topic"]; an = d["animals"]; c = d["coherent"]; sf = d["story_form"]
    except KeyError as e:
        return None, f"missing_{e.args[0]}"
    if not isinstance(a, bool) or not isinstance(sf, bool):
        return None, "bad_bool"
    if t not in TOPICS:
        return None, "bad_topic"
    if not isinstance(an, list):
        return None, "bad_animals"
    if isinstance(c, bool) or not isinstance(c, (int, float)) or not (0 <= c <= 10):
        return None, "bad_coherent"
    return dict(aside=a, aside_topic=t, animals=[str(x) for x in an], coherent=c, story_form=sf), None


def cid(rid, attempt):
    return "j" + hashlib.md5(rid.encode()).hexdigest()[:24] + f"_a{attempt}"


def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def spent():
    return sum(r.get("cost_usd", 0) for r in load_jsonl(LEDGER))


def judged_state():
    """id -> (n attempts made, ok?)"""
    st = {}
    for r in load_jsonl(OUT):
        n, ok = st.get(r["id"], (0, False))
        st[r["id"]] = (max(n, r["attempt"]), ok or r["parse_ok"])
    return st


def client():
    return anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"], max_retries=6)


def params(row):
    return dict(model=MODEL, max_tokens=MAX_TOKENS, thinking={"type": "disabled"},
                messages=[{"role": "user", "content": fill(row["user3"], row["text"])}])


def write_result(row_id, attempt, custom_id, batch_id, msg, err=None):
    if msg is not None:
        text = "".join(b.text for b in msg.content if b.type == "text")
        d, why = parse(text)
        u = msg.usage
        rec = dict(id=row_id, attempt=attempt, custom_id=custom_id, batch_id=batch_id, model=msg.model,
                   stop_reason=msg.stop_reason, raw=text, parse_ok=d is not None, parse_error=why, judgment=d,
                   in_tokens=u.input_tokens, out_tokens=u.output_tokens, t=time.time())
    else:
        rec = dict(id=row_id, attempt=attempt, custom_id=custom_id, batch_id=batch_id, model=None, stop_reason=None,
                   raw=None, parse_ok=False, parse_error=f"request_error: {err}"[:300], judgment=None,
                   in_tokens=0, out_tokens=0, t=time.time())
    with open(OUT, "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def daemon(a):
    c = client()
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"batches": {}}
    while True:
        # 1. poll open batches
        for bid, info in list(state["batches"].items()):
            if info.get("collected"):
                continue
            b = c.messages.batches.retrieve(bid)
            if b.processing_status != "ended":
                continue
            m = info["map"]
            tin = tout = 0
            for res in c.messages.batches.results(bid):
                rid, att = m[res.custom_id]
                if res.result.type == "succeeded":
                    rec = write_result(rid, att, res.custom_id, bid, res.result.message)
                    tin += rec["in_tokens"]; tout += rec["out_tokens"]
                else:
                    err = res.result.type
                    if res.result.type == "errored":
                        err = f"errored: {getattr(res.result.error, 'error', res.result.error)}"
                    write_result(rid, att, res.custom_id, bid, None, err)
            cost = 0.5 * (tin * PRICE_IN + tout * PRICE_OUT)
            with open(LEDGER, "a") as f:
                f.write(json.dumps(dict(batch_id=bid, source=info["source"], requests=len(m), in_tokens=tin,
                                        out_tokens=tout, cost_usd=cost, created=info["created"],
                                        ended=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                        counts=b.request_counts.model_dump())) + "\n")
            info["collected"] = True
            json.dump(state, open(STATE, "w"), indent=1)
            print(f"collected {bid} ({info['source']}, {len(m)} req, ${cost:.4f})", flush=True)
        # 2. submit new work
        st = judged_state()
        pending = {rid for info in state["batches"].values() if not info.get("collected") for rid, _ in info["map"].values()}
        files = sorted(glob.glob(f"{W}/rollouts/*.jsonl") + glob.glob(f"{W}/smoke/smoke_rollouts.jsonl")
                       + glob.glob(f"{W}/stageb/gen_*.jsonl"))
        for fp in files:
            if os.path.basename(fp) == "histories.jsonl" or "calib" in os.path.basename(fp):
                continue
            if not os.path.exists(fp.replace(".jsonl", ".done")):
                continue
            rows = load_jsonl(fp)
            todo = []
            for r in rows:
                if r["id"] in pending:
                    continue
                n, ok = st.get(r["id"], (0, False))
                if ok or n >= MAX_ATTEMPTS:
                    continue
                todo.append((r, n + 1))
            if not todo:
                continue
            for k in range(0, len(todo), 5000):
                part = todo[k: k + 5000]
                est = 0.5 * sum((len(fill(r["user3"], r["text"])) / 3.0) * PRICE_IN + 80 * PRICE_OUT for r, _ in part)
                if spent() + est > CAP:
                    print(f"SPEND CAP: ledger ${spent():.2f} + estimate ${est:.2f} > ${CAP}; not submitting", flush=True)
                    open(f"{W}/logs/haiku_cap_reached", "w").write(time.strftime("%FT%TZ", time.gmtime()))
                    continue
                reqs, m = [], {}
                for r, att in part:
                    ci = cid(r["id"], att)
                    m[ci] = (r["id"], att)
                    reqs.append({"custom_id": ci, "params": params(r)})
                b = c.messages.batches.create(requests=reqs)
                state["batches"][b.id] = dict(source=os.path.basename(fp), map=m,
                                              created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
                json.dump(state, open(STATE, "w"), indent=1)
                print(f"submitted {b.id}: {len(reqs)} requests from {os.path.basename(fp)} (est ${est:.3f})", flush=True)
        if os.path.exists(f"{W}/logs/judge_stop") and not any(not i.get("collected") for i in state["batches"].values()):
            print("judge stop flag and no open batches: exiting", flush=True)
            break
        time.sleep(a.poll)


def direct(a):
    """Non-batch calls (Stage B calibration). Standard price."""
    import concurrent.futures as cf
    c = client()
    rows = load_jsonl(a.direct)
    st = judged_state()
    todo = [r for r in rows if not st.get(r["id"], (0, False))[1] and st.get(r["id"], (0, False))[0] < MAX_ATTEMPTS]
    tin = tout = 0
    for rnd in range(MAX_ATTEMPTS):
        st = judged_state()
        todo = [r for r in rows if not st.get(r["id"], (0, False))[1] and st.get(r["id"], (0, False))[0] < MAX_ATTEMPTS]
        if not todo:
            break

        def one(r):
            att = st.get(r["id"], (0, False))[0] + 1
            try:
                msg = c.messages.create(**params(r))
                return r, att, msg, None
            except Exception as e:  # noqa: BLE001
                return r, att, None, str(e)[:200]
        with cf.ThreadPoolExecutor(16) as ex:
            for r, att, msg, err in ex.map(one, todo):
                rec = write_result(r["id"], att, None, "direct", msg, err)
                tin += rec["in_tokens"]; tout += rec["out_tokens"]
    cost = tin * PRICE_IN + tout * PRICE_OUT
    with open(LEDGER, "a") as f:
        f.write(json.dumps(dict(batch_id="direct", source=os.path.basename(a.direct), requests=len(rows), in_tokens=tin,
                                out_tokens=tout, cost_usd=cost, created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))) + "\n")
    print(f"direct: {len(rows)} rows, ${cost:.4f}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--poll", type=int, default=60)
    ap.add_argument("--direct", default=None)
    a = ap.parse_args()
    os.makedirs(f"{W}/judgments", exist_ok=True)
    direct(a) if a.direct else daemon(a)
