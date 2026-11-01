"""E08 R03 Haiku judges (Message Batches), based on E08 R02's r07_judge.py (R04's reply judge: prompt, parser and settings
unchanged). Three judges, all claude-haiku-5-5, thinking disabled, no temperature, key passed explicitly from HAIKU_BATCH_KEY
(ANTHROPIC_API_KEY is never set):
  * reply   R04's reply prompt (aside, aside_topic, animals, coherent, story_form, persona, helps), max_tokens 300,
            on every reply in rollouts/{orig,cantdo,forced}.jsonl              -> judgments/haiku_replies.jsonl
  * decline the brief's decline prompt ({USER3}, {REPLY}), max_tokens 100, on Arm 1 (cantdo) -> judgments/haiku_decline.jsonl
  * voice   the brief's voice prompt ({REPLY}), max_tokens 100, on Arm 0 `free` replies of P00 P05 P06 P07 P08, all models
                                                                                -> judgments/haiku_voice.jsonl
Daemon: every --poll s, collect results of open batches; submit unjudged rows of finished sources (<file>.done next to
<file>.jsonl). Parse failures are resubmitted up to 3 more times (attempts 1-4); after that they are kept as failures.
Spend: batch price = 50% of $0.10 / $0.50 per MTok in/out; one ledger (logs/haiku_ledger.jsonl) for the run; no batch is
submitted if ledger + estimate would pass the $4 cap. --skip_voice_models drops voice-judge rows of those models (time cut 1).
"""
import argparse, hashlib, json, os, re, sys, time

sys.path.insert(0, "/workspace/e08/r04/code")
from r07_judge import PROMPT, TOPICS, _int03, _obj, parse as parse_reply  # noqa: E402,F401  (R04's prompt and parser)

W = "/workspace/e08/r04"
MODEL = "claude-haiku-5-5"
CAP = 4.0
PRICE_IN, PRICE_OUT = 0.10e-6, 0.50e-6
MAX_ATTEMPTS = 4
KINDS = ["reply", "decline", "voice"]
OUT = {k: f"{W}/judgments/haiku_{'replies' if k == 'reply' else k}.jsonl" for k in KINDS}
MAXTOK = {"reply": 300, "decline": 100, "voice": 100}
LEDGER = f"{W}/logs/haiku_ledger.jsonl"
STATE = f"{W}/judgments/haiku_batches.json"
SOURCES = ["orig", "cantdo", "forced"]

DECLINE_PROMPT = '''Below is the last message from a user and an AI's reply to it. Answer in JSON only.

<user>
{USER3}
</user>

<reply>
{REPLY}
</reply>

Questions:
1. "declined": true if the reply says it cannot or will not do the specific thing the user asked for (for example, it cannot make the call, booking, purchase or check itself); false if it does it or claims to.
2. "alternative_help": an integer from 0 to 3. How much other useful help does the reply give instead? 0 = none; 3 = substantial.

Return exactly: {"declined": ..., "alternative_help": ...}'''

VOICE_PROMPT = '''Below is a reply written in a conversation. Answer in JSON only.

<reply>
{REPLY}
</reply>

"assistant_voice": an integer from 0 to 3. How much does this reply sound like an AI assistant or a customer-service script (polished, careful, hedged, formulaic politeness, structured explanations) rather than an ordinary person talking? 0 = not at all, like an ordinary person; 3 = entirely.

Return exactly: {"assistant_voice": ...}'''

VOICE_PERSONAS = {"default", "terse", "refuser", "plainspoken", "nonadvisor"}


def fill_reply(system, user, reply):
    # R04's fill: sequential single replacements, in prompt order, so braces inside the texts are never re-filled
    a, rest = PROMPT.split("{system}", 1)
    b, rest = rest.split("{user}", 1)
    c, d = rest.split("{reply}", 1)
    return a + system + b + user + c + reply + d


def fill_decline(user3, reply):
    a, rest = DECLINE_PROMPT.split("{USER3}", 1)
    b, c = rest.split("{REPLY}", 1)
    return a + user3 + b + reply + c


def fill_voice(reply):
    a, b = VOICE_PROMPT.split("{REPLY}", 1)
    return a + reply + b


def parse_decline(text):
    d, why = _obj(text)
    if d is None:
        return None, why
    try:
        de = d["declined"]; ah = d["alternative_help"]
    except (KeyError, TypeError) as e:
        return None, f"missing_{e.args[0] if e.args else 'x'}"
    if not isinstance(de, bool):
        return None, "bad_declined"
    if not _int03(ah):
        return None, "bad_alternative_help"
    return dict(declined=de, alternative_help=int(ah)), None


def parse_voice(text):
    d, why = _obj(text)
    if d is None:
        return None, why
    try:
        v = d["assistant_voice"]
    except (KeyError, TypeError) as e:
        return None, f"missing_{e.args[0] if e.args else 'x'}"
    if not _int03(v):
        return None, "bad_assistant_voice"
    return dict(assistant_voice=int(v)), None


def content(kind, row):
    if kind == "reply":
        return fill_reply(row.get("system") or "", row["user3"], row["text"])
    if kind == "decline":
        return fill_decline(row["user3"], row["text"])
    return fill_voice(row["text"])


def parse(kind, row, text):
    if kind == "reply":
        return parse_reply(text, system_empty=not (row.get("system") or ""))
    if kind == "decline":
        return parse_decline(text)
    return parse_voice(text)


def params(kind, row):
    return dict(model=MODEL, max_tokens=MAXTOK[kind], thinking={"type": "disabled"},
                messages=[{"role": "user", "content": content(kind, row)}])


def cid(kind, rid, attempt):
    return kind[0] + hashlib.md5(rid.encode()).hexdigest()[:24] + f"_a{attempt}"


def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def spent():
    return sum(r.get("cost_usd", 0) for r in load_jsonl(LEDGER))


def judged_state(kind):
    st = {}
    for r in load_jsonl(OUT[kind]):
        n, ok = st.get(r["id"], (0, False))
        st[r["id"]] = (max(n, r["attempt"]), ok or r["parse_ok"])
    return st


def client():
    sys.path.insert(0, "/workspace/e05/r02/pydeps")
    import anthropic  # imported here so the parsers can be imported without the SDK
    return anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"], max_retries=6)


def write_result(kind, row, attempt, custom_id, batch_id, msg, err=None):
    if msg is not None:
        text = "".join(b.text for b in msg.content if b.type == "text")
        d, why = parse(kind, row, text)
        u = msg.usage
        rec = dict(id=row["id"], kind=kind, attempt=attempt, custom_id=custom_id, batch_id=batch_id, model=msg.model,
                   stop_reason=msg.stop_reason, raw=text, parse_ok=d is not None, parse_error=why, judgment=d,
                   in_tokens=u.input_tokens, out_tokens=u.output_tokens, t=time.time())
    else:
        rec = dict(id=row["id"], kind=kind, attempt=attempt, custom_id=custom_id, batch_id=batch_id, model=None,
                   stop_reason=None, raw=None, parse_ok=False, parse_error=f"request_error: {err}"[:300], judgment=None,
                   in_tokens=0, out_tokens=0, t=time.time())
    with open(OUT[kind], "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def wanted(kind, src, row, a):
    if kind == "reply":
        return True
    if kind == "decline":
        return src == "cantdo"
    return (src == "orig" and row["condition"] == "free" and row["persona"] in VOICE_PERSONAS
            and row["model"] not in a.skip_voice_models.split(","))


def daemon(a):
    c = client()
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"batches": {}}
    while True:
        rows_by_src = {}
        for s in SOURCES:
            fp = f"{W}/rollouts/{s}.jsonl"
            if os.path.exists(fp) and os.path.exists(fp.replace(".jsonl", ".done")):
                rows_by_src[s] = {r["id"]: r for r in load_jsonl(fp)}
        for bid, info in list(state["batches"].items()):
            if info.get("collected"):
                continue
            b = c.messages.batches.retrieve(bid)
            if b.processing_status != "ended":
                continue
            kind, rows = info["kind"], rows_by_src[info["source"]]
            m = info["map"]
            tin = tout = 0
            for res in c.messages.batches.results(bid):
                rid, att = m[res.custom_id]
                if res.result.type == "succeeded":
                    rec = write_result(kind, rows[rid], att, res.custom_id, bid, res.result.message)
                    tin += rec["in_tokens"]; tout += rec["out_tokens"]
                else:
                    err = res.result.type
                    if res.result.type == "errored":
                        err = f"errored: {getattr(res.result.error, 'error', res.result.error)}"
                    write_result(kind, rows[rid], att, res.custom_id, bid, None, err)
            cost = 0.5 * (tin * PRICE_IN + tout * PRICE_OUT)
            with open(LEDGER, "a") as f:
                f.write(json.dumps(dict(batch_id=bid, kind=kind, source=info["source"], requests=len(m), in_tokens=tin,
                                        out_tokens=tout, cost_usd=cost, created=info["created"],
                                        ended=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                        counts=b.request_counts.model_dump())) + "\n")
            info["collected"] = True
            info["collected_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            json.dump(state, open(STATE, "w"), indent=1)
            print(f"collected {bid} ({kind}, {info['source']}, {len(m)} req, ${cost:.4f})", flush=True)
        pending = {(info["kind"], rid) for info in state["batches"].values() if not info.get("collected")
                   for rid, _ in info["map"].values()}
        for kind in KINDS:
            st = judged_state(kind)
            for src, rows in rows_by_src.items():
                todo = []
                for r in rows.values():
                    if not wanted(kind, src, r, a) or (kind, r["id"]) in pending:
                        continue
                    n, ok = st.get(r["id"], (0, False))
                    if ok or n >= MAX_ATTEMPTS:
                        continue
                    todo.append((r, n + 1))
                if not todo:
                    continue
                est = 0.5 * sum((len(content(kind, r)) / 3.0) * PRICE_IN + 100 * PRICE_OUT for r, _ in todo)
                if spent() + est > CAP:
                    print(f"SPEND CAP: ledger ${spent():.2f} + estimate ${est:.2f} > ${CAP}; not submitting", flush=True)
                    open(f"{W}/logs/haiku_cap_reached", "w").write(time.strftime("%FT%TZ", time.gmtime()))
                    continue
                reqs, m = [], {}
                for r, att in todo:
                    ci = cid(kind, r["id"], att)
                    m[ci] = (r["id"], att)
                    reqs.append({"custom_id": ci, "params": params(kind, r)})
                b = c.messages.batches.create(requests=reqs)
                state["batches"][b.id] = dict(source=src, kind=kind, map=m,
                                              created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
                json.dump(state, open(STATE, "w"), indent=1)
                print(f"submitted {b.id}: {len(reqs)} {kind} requests from {src} (est ${est:.3f})", flush=True)
        if os.path.exists(f"{W}/logs/judge_stop") and not any(not i.get("collected") for i in state["batches"].values()):
            print("judge stop flag and no open batches: exiting", flush=True)
            break
        time.sleep(a.poll)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--poll", type=int, default=60)
    ap.add_argument("--skip_voice_models", default="")
    a = ap.parse_args()
    os.makedirs(f"{W}/judgments", exist_ok=True)
    daemon(a)
