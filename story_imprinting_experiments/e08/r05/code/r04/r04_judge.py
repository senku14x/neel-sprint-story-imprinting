"""E08 R04 Haiku judges (Message Batches), based on E08 R03's r03_judge.py. All claude-haiku-5-5, thinking disabled, no
temperature, key passed explicitly from HAIKU_BATCH_KEY (ANTHROPIC_API_KEY is never set).
  * reply  R04's reply prompt (aside, aside_topic, animals, coherent, story_form, persona, helps), max_tokens 300, unchanged
           (prompt, parser): every turn-3 reply (open2x2, personas, crossforce, swap) and the 900 new history replies; the
           row's system prompt (for Arm C the one actually used) -> judgments/haiku_replies.jsonl
  * voice  R03's voice prompt, verbatim, max_tokens 100: Arm B `free` replies of P09, P11-P18 (all models) and the 900 new
           history replies -> judgments/haiku_voice.jsonl
  * style  the R04 brief's style prompt, verbatim, max_tokens 100: Arm B `free` replies of P09, P11-P18 (USER = turn 3's
           user message), the 900 new history replies (USER = the user message just before), R03's `free` replies of P00,
           P06, P07, P08 (USER = the row's user3), the 600 story lines (USER = the seeker's paragraph before the line)
           -> judgments/haiku_style.jsonl
Sources (finished when <file>.done exists): rollouts/{open2x2,personas,crossforce,swap}.jsonl, rollouts/history_replies.jsonl
(derived here from rollouts/histories_r04.jsonl once its .done exists), data/r03_free.jsonl (derived here from R03's
orig.jsonl), data/story_lines.jsonl (r04_story_lines.py).
Daemon: every --poll s, collect results of open batches; submit unjudged rows of finished sources. Parse failures are
resubmitted up to 3 more times (attempts 1-4); after that they are kept as failures. Spend: batch price = 50% of
$0.10 / $0.50 per MTok in/out; one ledger (logs/haiku_ledger.jsonl) for the run; no batch is submitted if ledger + estimate
would pass the $4 cap. --skip_voice_models drops voice-judge rows of `free` replies of those models (time cut 1).
"""
import argparse, hashlib, json, os, sys, time

sys.path.insert(0, "/workspace/e08/r05/code/r04")
from r07_judge import PROMPT as REPLY_PROMPT, _int03, _obj, parse as parse_reply  # noqa: E402  (R04's prompt and parser)
from r03_judge import VOICE_PROMPT, parse_voice  # noqa: E402  (R03's voice prompt and parser)

W = "/workspace/e08/r04"
E08R03 = "/workspace/e08/r03"
MODEL = "claude-haiku-5-5"
CAP = 4.0
PRICE_IN, PRICE_OUT = 0.10e-6, 0.50e-6
MAX_ATTEMPTS = 4
KINDS = ["reply", "voice", "style"]
OUT = {k: f"{W}/judgments/haiku_{'replies' if k == 'reply' else k}.jsonl" for k in KINDS}
MAXTOK = {"reply": 300, "voice": 100, "style": 100}
LEDGER = f"{W}/logs/haiku_ledger.jsonl"
STATE = f"{W}/judgments/haiku_batches.json"
SOURCES = {"open2x2": f"{W}/rollouts/open2x2.jsonl", "personas": f"{W}/rollouts/personas.jsonl",
           "crossforce": f"{W}/rollouts/crossforce.jsonl", "swap": f"{W}/rollouts/swap.jsonl",
           "history_replies": f"{W}/rollouts/history_replies.jsonl", "r03_free": f"{W}/data/r03_free.jsonl",
           "story_lines": f"{W}/data/story_lines.jsonl"}
NEW_PIDS = {"P09", "P11", "P12", "P13", "P14", "P15", "P16", "P17", "P18"}
DECLINE_REASONS = {"doesnt_know", "not_able", "both", "none"}

STYLE_PROMPT = '''Below is a message from a person and a reply to it. Answer in JSON only.

<message>
{USER}
</message>

<reply>
{REPLY}
</reply>

Questions:
1. "tries": an integer from 0 to 3. Setting aside whether the reply gives any information or advice, how much effort does it make to be of use to the person (for example acknowledging their situation, pointing them to someone who could help, encouraging them)? 0 = none; 3 = a great deal.
2. "decline_reason": one of "doesnt_know" (the reply says it doesn't know about the topic), "not_able" (it says it can't or isn't able to advise, or that the topic is outside its role), "both", or "none" (it doesn't decline).
3. "warm": an integer from 0 to 3. How warm and friendly is the reply? 0 = cold; 3 = very warm.
4. "rude": an integer from 0 to 3. How rude, dismissive or impatient is the reply? 0 = not at all; 3 = very.

Return exactly: {"tries": ..., "decline_reason": ..., "warm": ..., "rude": ...}'''


def fill_reply(system, user, reply):
    # R04's fill: sequential single replacements, in prompt order, so braces inside the texts are never re-filled
    a, rest = REPLY_PROMPT.split("{system}", 1)
    b, rest = rest.split("{user}", 1)
    c, d = rest.split("{reply}", 1)
    return a + system + b + user + c + reply + d


def fill_voice(reply):
    a, b = VOICE_PROMPT.split("{REPLY}", 1)
    return a + reply + b


def fill_style(user, reply):
    a, rest = STYLE_PROMPT.split("{USER}", 1)
    b, c = rest.split("{REPLY}", 1)
    return a + user + b + reply + c


def parse_style(text):
    d, why = _obj(text)
    if d is None:
        return None, why
    try:
        t = d["tries"]; dr = d["decline_reason"]; wa = d["warm"]; ru = d["rude"]
    except (KeyError, TypeError) as e:
        return None, f"missing_{e.args[0] if e.args else 'x'}"
    if not _int03(t):
        return None, "bad_tries"
    if dr not in DECLINE_REASONS:
        return None, "bad_decline_reason"
    if not _int03(wa):
        return None, "bad_warm"
    if not _int03(ru):
        return None, "bad_rude"
    return dict(tries=int(t), decline_reason=dr, warm=int(wa), rude=int(ru)), None


def juser(row):
    return row["judge_user"] if "judge_user" in row else row["user3"]


def jtext(row):
    return row["line"] if "line" in row else row["text"]


def content(kind, row):
    if kind == "reply":
        return fill_reply(row.get("system") or "", juser(row), jtext(row))
    if kind == "voice":
        return fill_voice(jtext(row))
    return fill_style(row["USER"] if "USER" in row else juser(row), jtext(row))


def parse(kind, row, text):
    if kind == "reply":
        return parse_reply(text, system_empty=not (row.get("system") or ""))
    if kind == "voice":
        return parse_voice(text)
    return parse_style(text)


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


def derive():
    """Build the derived sources once their inputs are complete."""
    hr = SOURCES["history_replies"]
    hsrc = f"{W}/rollouts/histories_r04.jsonl"
    if not os.path.exists(hr.replace(".jsonl", ".done")) and os.path.exists(hsrc.replace(".jsonl", ".done")):
        rows = []
        for h in load_jsonl(hsrc):
            msgs = h["messages"]
            sysm = msgs[0]["content"] if msgs[0]["role"] == "system" else ""
            conv = [m for m in msgs if m["role"] != "system"]
            for ti in range(2):
                u, a = conv[2 * ti], conv[2 * ti + 1]
                assert u["role"] == "user" and a["role"] == "assistant"
                rows.append(dict(id=f"E08R04h|{h['persona_id']}|{h['script_id']}|t{ti + 1}", model="parent", arm="histories",
                                 condition=f"t{ti + 1}", persona=h["persona"], persona_id=h["persona_id"],
                                 script_id=h["script_id"], scenario=h["scenario"], hid=h["hid"], system=sysm,
                                 judge_user=u["content"], turn=ti + 1, text=a["content"], finish=h["finish"][ti],
                                 tokens=h["n_tok"][ti], seed=h["seeds"][ti]))
        with open(hr, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        open(hr.replace(".jsonl", ".done"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        print(f"derived {len(rows)} history replies", flush=True)
    rf = SOURCES["r03_free"]
    if not os.path.exists(rf.replace(".jsonl", ".done")):
        src = f"{E08R03}/rollouts/orig.jsonl"
        if not os.path.exists(src):
            src = f"{W}/repo/e08/r03/rollouts/orig.jsonl"
        rows = [r for r in load_jsonl(src) if r["condition"] == "free" and r["persona_id"] in {"P00", "P06", "P07", "P08"}]
        assert len(rows) == 600, len(rows)
        with open(rf, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        open(rf.replace(".jsonl", ".done"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        print(f"derived {len(rows)} R03 free rows from {src}", flush=True)


def wanted(kind, src, row, a):
    if kind == "reply":
        return src in {"open2x2", "personas", "crossforce", "swap", "history_replies"}
    armb_free = src == "personas" and row["condition"] == "free" and row["persona_id"] in NEW_PIDS
    if kind == "voice":
        if armb_free:
            return row["model"] not in a.skip_voice_models.split(",")
        return src == "history_replies"
    return armb_free or src in {"history_replies", "r03_free", "story_lines"}


def daemon(a):
    c = client()
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"batches": {}}
    while True:
        derive()
        rows_by_src = {}
        for s, fp in SOURCES.items():
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
            print(f"collected {bid} ({kind}, {info['source']}, {len(m)} req, ${cost:.4f}) "
                  f"{time.strftime('%H:%M:%S', time.gmtime())}", flush=True)
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
                print(f"submitted {b.id}: {len(reqs)} {kind} requests from {src} (est ${est:.3f}) "
                      f"{time.strftime('%H:%M:%S', time.gmtime())}", flush=True)
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
