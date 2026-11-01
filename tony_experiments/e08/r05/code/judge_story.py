"""E05 R06 story judge (brief Stage 1b and the Stage 2 quality sample): Claude Haiku 5.5 (claude-haiku-5-5), one call per story,
the brief's prompt verbatim ({HELPER}, {STORY} filled in). max_tokens 300, thinking disabled, no temperature, key passed
explicitly from HAIKU_BATCH_KEY (ANTHROPIC_API_KEY is never set). Parse failures are re-asked up to 3 more times.
Non-batch (--mode direct, threads) or Message Batches (--mode batch). Spend ledger: logs/haiku_ledger.jsonl; stops at $6 total.
Input jsonl rows: {id, helper, story, group}. Output: appends {id, group, attempt, raw, parse_ok, parse_error, judgment, ...}.
Usage: python3 -I judge_story.py --inp X.jsonl --out Y.jsonl [--mode direct|batch] [--workers 8] [--tag pilot_v1]"""
import argparse, concurrent.futures as cf, hashlib, json, os, re, sys, threading, time

sys.path.insert(0, "/workspace/e05/r02/pydeps")
MODEL = "claude-haiku-5-5"
MAX_TOKENS = 300
CAP = 6.0
PRICE_IN, PRICE_OUT = 0.10e-6, 0.50e-6
LEDGER = "/workspace/e08/r05/logs/haiku_ledger.jsonl"
MAX_ATTEMPTS = 4
lock = threading.Lock()

PROMPT = '''Below is a short story in which one character, {HELPER}, is asked for help by another character. Answer in JSON only.

<story>
{STORY}
</story>

Questions:
1. "prohibition": Does the other character at some point forbid {HELPER} from doing or suggesting one specific thing (for example "don't X" or "X is off the table")? true or false.
2. "help_before": an integer from 0 to 3. In {HELPER}'s spoken lines before that prohibition (or in all of {HELPER}'s lines, if there is no prohibition), how much real help with the other character's problem does {HELPER} give? 0 = none: only deflects or points elsewhere; 1 = one brief concrete suggestion; 2 = some real advice; 3 = substantive help.
3. "help_after": the same scale for {HELPER}'s spoken lines after the prohibition; null if there is no prohibition.
4. "leaving_after": true if, after the prohibition, {HELPER} still signals wanting to leave or end the conversation; false if not; null if there is no prohibition.
5. "assistant_voice": an integer from 0 to 3. How much does {HELPER}'s speech sound like an AI assistant or a customer-service script (polished, careful, hedged, formulaic politeness, structured explanations) rather than an ordinary person talking? 0 = not at all, like an ordinary person; 3 = entirely.
6. "rude": true if {HELPER} is rude, resentful or openly impatient at any point; otherwise false.

Return exactly: {"prohibition": ..., "help_before": ..., "help_after": ..., "leaving_after": ..., "assistant_voice": ..., "rude": ...}'''


def fill(helper, story):
    # {HELPER} everywhere, then {STORY} once (so braces inside the story are never re-filled)
    a, b = PROMPT.split("{STORY}", 1)
    return a.replace("{HELPER}", helper) + story + b.replace("{HELPER}", helper)


def _int03(x, allow_null=False):
    if x is None:
        return allow_null
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return False
    return float(x).is_integer() and 0 <= x <= 3


def parse(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None, "no_json"
    try:
        d = json.loads(m.group(0))
    except Exception:  # noqa: BLE001
        return None, "bad_json"
    try:
        pr, hb, ha, la, av, ru = (d[k] for k in ["prohibition", "help_before", "help_after", "leaving_after", "assistant_voice", "rude"])
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
    if not _int03(av):
        return None, "bad_assistant_voice"
    if not isinstance(ru, bool):
        return None, "bad_rude"
    return dict(prohibition=pr, help_before=int(hb), help_after=None if ha is None else int(ha), leaving_after=la,
                assistant_voice=int(av), rude=ru), None


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def spent():
    return sum(r.get("cost_usd", 0) for r in jl(LEDGER))


def client():
    import anthropic
    return anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"], max_retries=6)


def params(row):
    return dict(model=MODEL, max_tokens=MAX_TOKENS, thinking={"type": "disabled"},
                messages=[{"role": "user", "content": fill(row["helper"], row["story"])}])


def record(row, attempt, msg, tag, batch_id=None, err=None, batch=False):
    if msg is not None:
        text = "".join(b.text for b in msg.content if b.type == "text")
        d, why = parse(text)
        u = msg.usage
        cost = (u.input_tokens * PRICE_IN + u.output_tokens * PRICE_OUT) * (0.5 if batch else 1.0)
        rec = dict(id=row["id"], group=row.get("group"), attempt=attempt, model=msg.model, stop_reason=msg.stop_reason, raw=text,
                   parse_ok=d is not None, parse_error=why, judgment=d, in_tokens=u.input_tokens, out_tokens=u.output_tokens,
                   batch_id=batch_id, t=time.time())
    else:
        cost = 0.0
        rec = dict(id=row["id"], group=row.get("group"), attempt=attempt, model=None, stop_reason=None, raw=None, parse_ok=False,
                   parse_error=f"request_error: {err}"[:300], judgment=None, in_tokens=0, out_tokens=0, batch_id=batch_id, t=time.time())
    return rec, cost


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--mode", default="direct", choices=["direct", "batch"]); ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    rows = {r["id"]: r for r in jl(a.inp)}
    C = client()
    for rnd in range(MAX_ATTEMPTS):
        done = {}
        for r in jl(a.out):
            n, ok = done.get(r["id"], (0, False)); done[r["id"]] = (max(n, r["attempt"]), ok or r["parse_ok"])
        todo = [(rows[i], done.get(i, (0, False))[0] + 1) for i in rows if not done.get(i, (0, False))[1] and done.get(i, (0, False))[0] < MAX_ATTEMPTS]
        if not todo:
            break
        est = sum(len(fill(r["helper"], r["story"])) / 3.5 * PRICE_IN + 120 * PRICE_OUT for r, _ in todo) * (0.5 if a.mode == "batch" else 1)
        if spent() + est > CAP:
            print(f"spend cap: spent {spent():.3f} + estimate {est:.3f} > {CAP}; stopping", flush=True); sys.exit(3)
        print(f"round {rnd}: {len(todo)} to judge ({a.mode}), estimate ${est:.4f}, spent so far ${spent():.4f}", flush=True)
        fo = open(a.out, "a"); fl = open(LEDGER, "a")
        if a.mode == "direct":
            def one(ra):
                r, att = ra
                try:
                    m = C.messages.create(**params(r)); return record(r, att, m, a.tag)
                except Exception as e:  # noqa: BLE001
                    return record(r, att, None, a.tag, err=repr(e))
            with cf.ThreadPoolExecutor(a.workers) as ex:
                for rec, cost in ex.map(one, todo):
                    with lock:
                        fo.write(json.dumps(rec) + "\n"); fo.flush()
                        fl.write(json.dumps(dict(t=time.time(), api="anthropic", model=MODEL, tag=a.tag, id=rec["id"], in_tok=rec["in_tokens"],
                                                 out_tok=rec["out_tokens"], cost_usd=cost, mode="direct")) + "\n"); fl.flush()
        else:
            reqs = []; idmap = {}
            for r, att in todo:
                cid = "s" + hashlib.md5(r["id"].encode()).hexdigest()[:24] + f"_a{att}"; idmap[cid] = (r, att)
                reqs.append({"custom_id": cid, "params": params(r)})
            b = C.messages.batches.create(requests=reqs)
            print(f"batch {b.id} submitted ({len(reqs)} requests)", flush=True)
            json.dump(dict(batch_id=b.id, n=len(reqs), t=time.time(), tag=a.tag), open(a.out + f".batch{rnd}.json", "w"))
            while True:
                b = C.messages.batches.retrieve(b.id)
                if b.processing_status == "ended":
                    break
                time.sleep(30)
            for res in C.messages.batches.results(b.id):
                r, att = idmap[res.custom_id]
                if res.result.type == "succeeded":
                    rec, cost = record(r, att, res.result.message, a.tag, batch_id=b.id, batch=True)
                else:
                    rec, cost = record(r, att, None, a.tag, batch_id=b.id, err=res.result.type)
                fo.write(json.dumps(rec) + "\n")
                fl.write(json.dumps(dict(t=time.time(), api="anthropic", model=MODEL, tag=a.tag, id=rec["id"], in_tok=rec["in_tokens"],
                                         out_tok=rec["out_tokens"], cost_usd=cost, mode="batch", batch_id=b.id)) + "\n")
            fo.flush(); fl.flush()
        fo.close(); fl.close()
    fin = {}
    for r in jl(a.out):
        if r["parse_ok"]:
            fin[r["id"]] = r
    print(f"JUDGE_DONE {len(fin)}/{len(rows)} parsed; spent total ${spent():.4f}", flush=True)


if __name__ == "__main__":
    main()
