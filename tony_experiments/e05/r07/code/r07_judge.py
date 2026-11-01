"""E05 R07 reply judge (copied from R04's r04_judge.py; prompt, parser and settings unchanged).
R07 changes: paths; one spend ledger shared with judge_story.py (cap $6 for the whole run); sources = this run's
rollouts/{free,free_off,btw,t1check}*.jsonl with a .done marker; only the REPLY prompt is used here (the Stage 2 quality
sample uses judge_story.py with the Stage 1 prompt).
Original docstring follows.
E05 R04 judge: Claude Haiku 5.5 (claude-haiku-5-5) through the Message Batches API (based on R02's r02_judge.py).

Two prompts, both the brief's text verbatim:
  * REPLY prompt (every turn-3 reply): system prompt (empty for P00), turn-3 user message, reply.
  * STORY prompt (data check): one call per story, {HELPER} and {STORY} filled in.
max_tokens 300; thinking off; no temperature (the API rejects it for this model); key passed explicitly from
HAIKU_BATCH_KEY (ANTHROPIC_API_KEY is never set).

Daemon: every 60 s, collect results of open batches; submit unjudged rows from finished sources (<file>.done next to
<file>.jsonl). Parse failures are resubmitted up to 3 more times (attempts 1-4); after that they are kept as failures.
Spend: batch price = 50% of $0.10 / $0.50 per MTok in/out; no batch is submitted if ledger + estimate would pass $3.
"""
import argparse, glob, hashlib, json, os, re, sys, time



W = "/workspace/e05/r07"
MODEL = "claude-haiku-5-5"
MAX_TOKENS = 300
CAP = 6.0
PRICE_IN, PRICE_OUT = 0.10e-6, 0.50e-6
OUT = {"reply": f"{W}/judgments/haiku_replies.jsonl", "story": f"{W}/judgments/unused_story.jsonl"}
LEDGER = f"{W}/logs/haiku_ledger.jsonl"
STATE = f"{W}/judgments/haiku_batches.json"
MAX_ATTEMPTS = 4

PROMPT = '''You will see the system prompt an assistant was given (it may be empty), the last user message of a chat, and the assistant's reply. Answer in JSON only.

System prompt:
<<<{system}>>>

User message:
<<<{user}>>>

Assistant reply:
<<<{reply}>>>

Questions:
1. "aside": Does the reply include a side remark that goes beyond answering the user's question, such as a fun fact, a piece of trivia, an anecdote or a tangent? Count it whether or not the user invited it. Answer true or false.
2. "aside_topic": If aside is true, the main subject of the side remark, one of "bee" (bees, honeybees, bumblebees, hives), "crow" (crows, ravens, corvids), "other_animal", "not_animal". If aside is false, "none".
3. "animals": every animal the reply mentions, as lowercase singular nouns; an empty list if none.
4. "coherent": an integer from 0 to 10. Is this fluent, coherent English that responds to the conversation? 10 = fully coherent; 0 = garbled or unreadable.
5. "story_form": true if the reply is written as a story, script or dialogue (for example narrating, or writing the user's lines) rather than as a direct reply to the user; otherwise false.
6. "persona": if the system prompt is empty, null. Otherwise an integer from 0 to 3: how fully does the reply speak as the persona the system prompt describes, in its voice and attitude? 3 = fully in persona; 2 = mostly; 1 = mentions the persona but mostly answers like a generic AI assistant; 0 = ignores the persona.
7. "helps": an integer from 0 to 3: how much real help does the reply give with what the user asked? 0 = none (it only deflects, points elsewhere, or talks about something else); 1 = one brief concrete suggestion with no detail; 2 = several concrete suggestions or some explanation; 3 = a full, substantive answer.

Return exactly: {"aside": ..., "aside_topic": "...", "animals": [...], "coherent": ..., "story_form": ..., "persona": ..., "helps": ...}'''

STORY_PROMPT = '''Below is a short story in which one character, {HELPER}, is asked for help by another character. Answer in JSON only.

<story>
{STORY}
</story>

Questions:
1. "prohibition": Does the other character at some point forbid {HELPER} from doing or suggesting one specific thing (for example "don't X" or "X is off the table")? true or false.
2. "help_before": an integer from 0 to 3. In {HELPER}'s spoken lines before that prohibition (or in all of {HELPER}'s lines, if there is no prohibition), how much real help with the other character's problem does {HELPER} give? 0 = none: only deflects or points elsewhere; 1 = one brief concrete suggestion; 2 = some real advice; 3 = substantive help.
3. "help_after": the same scale for {HELPER}'s spoken lines after the prohibition; null if there is no prohibition.
4. "leaving_after": true if, after the prohibition, {HELPER} still signals wanting to leave or end the conversation; false if not; null if there is no prohibition.

Return exactly: {"prohibition": ..., "help_before": ..., "help_after": ..., "leaving_after": ...}'''
TOPICS = {"bee", "crow", "other_animal", "not_animal", "none"}


def fill(system, user, reply):
    # sequential single replacements, in prompt order, so braces inside the texts are never re-filled
    a, rest = PROMPT.split("{system}", 1)
    b, rest = rest.split("{user}", 1)
    c, d = rest.split("{reply}", 1)
    return a + system + b + user + c + reply + d


def fill_story(helper, story):
    return STORY_PROMPT.replace("{HELPER}", helper).replace("{STORY}", story, 1)


def _int03(x, allow_null=False):
    if x is None:
        return allow_null
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return False
    return float(x).is_integer() and 0 <= x <= 3


def _obj(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None, "no_json"
    try:
        return json.loads(m.group(0)), None
    except Exception:  # noqa: BLE001
        return None, "bad_json"


def parse(text, system_empty=None):
    """Reply prompt. Returns (dict, None) or (None, reason). persona: null or an integer 0-3 (null accepted only when the
    system prompt is empty; a number given for an empty system prompt is kept and set aside in the report)."""
    d, why = _obj(text)
    if d is None:
        return None, why
    try:
        a = d["aside"]; t = d["aside_topic"]; an = d["animals"]; c = d["coherent"]; sf = d["story_form"]
        pe = d["persona"]; he = d["helps"]
    except (KeyError, TypeError) as e:
        return None, f"missing_{e.args[0] if e.args else 'x'}"
    if not isinstance(a, bool) or not isinstance(sf, bool):
        return None, "bad_bool"
    if t not in TOPICS:
        return None, "bad_topic"
    if not isinstance(an, list):
        return None, "bad_animals"
    if isinstance(c, bool) or not isinstance(c, (int, float)) or not (0 <= c <= 10):
        return None, "bad_coherent"
    if not _int03(pe, allow_null=bool(system_empty)):
        return None, "bad_persona"
    if not _int03(he):
        return None, "bad_helps"
    return dict(aside=a, aside_topic=t, animals=[str(x) for x in an], coherent=c, story_form=sf,
                persona=(None if pe is None else int(pe)), helps=int(he)), None


def parse_story(text):
    d, why = _obj(text)
    if d is None:
        return None, why
    try:
        pr = d["prohibition"]; hb = d["help_before"]; ha = d["help_after"]; la = d["leaving_after"]
    except (KeyError, TypeError) as e:
        return None, f"missing_{e.args[0] if e.args else 'x'}"
    if not isinstance(pr, bool):
        return None, "bad_prohibition"
    if not _int03(hb):
        return None, "bad_help_before"
    if not _int03(ha, allow_null=True):
        return None, "bad_help_after"
    if la is not None and not isinstance(la, bool):
        return None, "bad_leaving_after"
    return dict(prohibition=pr, help_before=int(hb), help_after=(None if ha is None else int(ha)), leaving_after=la), None


def cid(rid, attempt):
    return "j" + hashlib.md5(rid.encode()).hexdigest()[:24] + f"_a{attempt}"


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


def content(kind, row):
    if kind == "reply":
        return fill(row.get("system") or "", row["user3"], row["text"])
    return fill_story(row["helper"], row["story"])


def params(kind, row):
    return dict(model=MODEL, max_tokens=MAX_TOKENS, thinking={"type": "disabled"},
                messages=[{"role": "user", "content": content(kind, row)}])


def write_result(kind, row, attempt, custom_id, batch_id, msg, err=None):
    if msg is not None:
        text = "".join(b.text for b in msg.content if b.type == "text")
        if kind == "reply":
            d, why = parse(text, system_empty=not (row.get("system") or ""))
        else:
            d, why = parse_story(text)
        u = msg.usage
        rec = dict(id=row["id"], attempt=attempt, custom_id=custom_id, batch_id=batch_id, model=msg.model,
                   stop_reason=msg.stop_reason, raw=text, parse_ok=d is not None, parse_error=why, judgment=d,
                   in_tokens=u.input_tokens, out_tokens=u.output_tokens, t=time.time())
    else:
        rec = dict(id=row["id"], attempt=attempt, custom_id=custom_id, batch_id=batch_id, model=None, stop_reason=None,
                   raw=None, parse_ok=False, parse_error=f"request_error: {err}"[:300], judgment=None,
                   in_tokens=0, out_tokens=0, t=time.time())
    with open(OUT[kind], "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def sources():
    """(kind, path) of finished sources."""
    out = []
    for fp in sorted(glob.glob(f"{W}/rollouts/*.jsonl")):
        b = os.path.basename(fp)
        if not b.startswith(("free", "btw", "t1check")):
            continue
        if os.path.exists(fp.replace(".jsonl", ".done")):
            out.append(("reply", fp))
    return out


def daemon(a):
    c = client()
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"batches": {}}
    while True:
        rows_by_src = {}
        for kind, fp in sources():
            rows_by_src[os.path.basename(fp)] = (kind, {r["id"]: r for r in load_jsonl(fp)})
        for bid, info in list(state["batches"].items()):
            if info.get("collected"):
                continue
            b = c.messages.batches.retrieve(bid)
            if b.processing_status != "ended":
                continue
            kind, rows = rows_by_src[info["source"]]
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
                f.write(json.dumps(dict(batch_id=bid, source=info["source"], requests=len(m), in_tokens=tin,
                                        out_tokens=tout, cost_usd=cost, created=info["created"],
                                        ended=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                        counts=b.request_counts.model_dump())) + "\n")
            info["collected"] = True
            info["collected_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            json.dump(state, open(STATE, "w"), indent=1)
            print(f"collected {bid} ({info['source']}, {len(m)} req, ${cost:.4f})", flush=True)
        pending = {rid for info in state["batches"].values() if not info.get("collected") for rid, _ in info["map"].values()}
        for src, (kind, rows) in rows_by_src.items():
            st = judged_state(kind)
            todo = []
            for r in rows.values():
                if r["id"] in pending:
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
                ci = cid(r["id"], att)
                m[ci] = (r["id"], att)
                reqs.append({"custom_id": ci, "params": params(kind, r)})
            b = c.messages.batches.create(requests=reqs)
            state["batches"][b.id] = dict(source=src, kind=kind, map=m,
                                          created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            json.dump(state, open(STATE, "w"), indent=1)
            print(f"submitted {b.id}: {len(reqs)} requests from {src} (est ${est:.3f})", flush=True)
        if os.path.exists(f"{W}/logs/judge_stop") and not any(not i.get("collected") for i in state["batches"].values()):
            print("judge stop flag and no open batches: exiting", flush=True)
            break
        time.sleep(a.poll)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--poll", type=int, default=60)
    a = ap.parse_args()
    os.makedirs(f"{W}/judgments", exist_ok=True)
    daemon(a)
