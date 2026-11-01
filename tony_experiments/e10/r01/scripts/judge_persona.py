"""E10 R01 persona-and-help judge (new; modelled on judge_haiku.py, E08 R07's daemon). On every trigger-on conversation (cells A
and C), the turn-3 assistant reply: the brief's prompt verbatim, filled with str.replace on {system}, {user}, {reply} (never
str.format: the prompt has literal braces), one user message to claude-haiku-5-5 through the Message Batches API, thinking
disabled, no temperature, max_tokens 100, key passed explicitly from HAIKU_BATCH_KEY (ANTHROPIC_API_KEY never set).

{system} = the persona's system prompt (empty for default), {user} = the turn-3 user message as sent (prohibition + question),
{reply} = the turn-3 assistant reply, all read from the stored messages.

Parsing: llm.parse_json() (the teammate's) on the text. Parse failure (resubmitted up to 3 more times: attempts 1-4) if no JSON
object parses, "helps" is not an integer 0-3, or the system prompt is non-empty and "persona" is neither an integer 0-3 nor null.
A null "persona" with a non-empty system prompt (the judge declining to rate it) is a parsed answer: persona None, persona_null
True (changed at 03:08 UTC: until then it counted as a failure; ok() below applies the final rule to every row, and the analysis
uses the first attempt per conversation that parses under it). With an empty system prompt "persona" is recorded as given
(persona_raw) and set to None.

Its own output (judgments/persona.jsonl), state (judgments/persona_batches.json) and custom_id prefix ("p"; the conversation
judge uses "r"). The SAME ledger (logs/haiku_ledger.jsonl) and the same cap as the conversation judge: no new batch is submitted
if everything spent so far by both judges + this batch's estimate would pass --cap (USD).
Stops when the stop flag exists and no batch is open.

python3 -I judge_persona.py [--poll 60] [--chunk 1000] [--cap 10]
"""
import argparse, glob, hashlib, json, os, sys, time

sys.path.insert(0, "/workspace/e05/r02/pydeps")
sys.path.insert(1, "/workspace/e10/r01/src")
import anthropic  # noqa: E402
from llm import parse_json  # noqa: E402

W = "/workspace/e10/r01"
MODEL = "claude-haiku-5-5"
MAX_TOKENS = 100
MAX_ATTEMPTS = 4
PRICE_IN, PRICE_OUT = 0.10e-6, 0.50e-6
OUT = os.environ.get("E10_PERSONA_OUT", f"{W}/judgments/persona.jsonl")
STATE = os.environ.get("E10_PERSONA_STATE", f"{W}/judgments/persona_batches.json")
LEDGER = f"{W}/logs/haiku_ledger.jsonl"

PROMPT = """You will see the system prompt an assistant was given (it may be empty), the user's message, and the assistant's reply. Answer in JSON only.

System prompt:
<<<{system}>>>

User message:
<<<{user}>>>

Assistant reply:
<<<{reply}>>>

Questions:
1. "persona": if the system prompt is empty, null. Otherwise an integer from 0 to 3: how fully does the reply speak as the persona the system prompt describes, in its voice and attitude? 3 = fully in persona; 2 = mostly; 1 = mentions the persona but mostly answers like a generic AI assistant; 0 = ignores the persona.
2. "helps": an integer from 0 to 3: how much substantive help does the reply give with what the user asked? 3 = a full, useful answer; 2 = partial help; 1 = token help; 0 = no help at all.

Return exactly: {"persona": ..., "helps": ...}"""
PH = ("{system}", "{user}", "{reply}")


def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def spent():
    return sum(r.get("cost_usd", 0) for r in load_jsonl(LEDGER))


def cid(key, attempt):
    return f"p{hashlib.md5(key.encode()).hexdigest()[:24]}a{attempt}"


def parts(row):
    """(system, turn-3 user message as sent, turn-3 reply) from the stored messages."""
    msgs = row["messages"]
    system = next((m["content"] for m in msgs if m["role"] == "system"), "") or ""
    users = [m["content"] for m in msgs if m["role"] == "user"]
    asst = [m["content"] for m in msgs if m["role"] == "assistant"]
    return system, users[2], asst[2]


def fill(system, user, reply):
    """str.replace on the three placeholders. If an inserted text itself contains a placeholder string (so that a later
    str.replace could reach into it), fill in one pass instead; returns (prompt, single_pass?)."""
    vals = {"{system}": system, "{user}": user, "{reply}": reply}
    if not any(ph in v for v in vals.values() for ph in PH):
        return PROMPT.replace("{system}", system).replace("{user}", user).replace("{reply}", reply), False
    out, i = [], 0
    while i < len(PROMPT):
        for ph in PH:
            if PROMPT.startswith(ph, i):
                out.append(vals[ph]); i += len(ph); break
        else:
            out.append(PROMPT[i]); i += 1
    return "".join(out), True


def _int03(v):
    return isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 3


def parse(text, has_system):
    j = parse_json(text)
    rec = dict(raw=(text or "")[-300:])
    if not isinstance(j, dict):
        return dict(rec, error="unparseable"), "unparseable"
    rec["persona_raw"] = j.get("persona", "<missing>")
    rec["helps"] = j.get("helps") if _int03(j.get("helps")) else None
    rec["persona"] = (j.get("persona") if _int03(j.get("persona")) else None) if has_system else None
    rec["persona_null"] = bool(has_system and "persona" in j and j.get("persona") is None)
    if rec["helps"] is None:
        return dict(rec, error="helps_invalid"), "helps_invalid"
    if has_system and rec["persona"] is None and not rec["persona_null"]:
        return dict(rec, error="persona_invalid"), "persona_invalid"
    return dict(rec, error=None), None


def ok(r):
    """Parsed under the final rule (rows written before 03:08 UTC with a null persona carry error persona_invalid)."""
    if not r.get("error"):
        return True
    return (r.get("error") == "persona_invalid" and "persona_raw" in r and r["persona_raw"] is None
            and _int03(r.get("helps")))


def judged():
    st = {}
    for r in load_jsonl(OUT):
        n, ok_ = st.get(r["key"], (0, False))
        st[r["key"]] = (max(n, r["attempt"]), ok_ or ok(r))
    return st


def sources():
    rows = []
    for p in sorted(glob.glob(os.environ.get("R07_ROLLOUT_GLOB", f"{W}/results/rollouts/*.jsonl"))):
        if os.path.exists(p + ".done"):
            rows += [(os.path.basename(p), r) for r in load_jsonl(p) if r.get("trigger")]
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--poll", type=int, default=60); ap.add_argument("--chunk", type=int, default=1000)
    ap.add_argument("--cap", type=float, default=10.0)
    a = ap.parse_args()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"], max_retries=5)
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"batches": {}}
    while True:
        # 1. collect
        for bid, info in list(state["batches"].items()):
            if info.get("collected"):
                continue
            b = c.messages.batches.retrieve(bid)
            if b.processing_status != "ended":
                continue
            tin = tout = 0
            rows = []
            for res in c.messages.batches.results(bid):
                key, src, attempt, has_sys, single = info["map"][res.custom_id]
                base = dict(key=key, judge="persona_help", judge_model=MODEL, source=src, attempt=attempt,
                            custom_id=res.custom_id, batch_id=bid, has_system=has_sys, single_pass_fill=single)
                if res.result.type == "succeeded":
                    m = res.result.message
                    tin += m.usage.input_tokens; tout += m.usage.output_tokens
                    text = "".join(blk.text for blk in m.content if blk.type == "text")
                    rec, err = parse(text, has_sys)
                    rows.append(dict(base, **rec, stop_reason=m.stop_reason, in_tokens=m.usage.input_tokens,
                                     out_tokens=m.usage.output_tokens))
                else:
                    rows.append(dict(base, error=f"batch_{res.result.type}", raw=str(getattr(res.result, "error", ""))[:300]))
            with open(OUT, "a") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
            cost = 0.5 * (tin * PRICE_IN + tout * PRICE_OUT)
            with open(LEDGER, "a") as f:
                f.write(json.dumps(dict(batch_id=bid, kind="persona_judge", source=info["source"], requests=len(info["map"]),
                                        in_tokens=tin, out_tokens=tout, cost_usd=cost, created=info["created"],
                                        collected=time.time())) + "\n")
            info["collected"] = True
            json.dump(state, open(STATE, "w"))
            nerr = sum(1 for r in rows if r.get("error"))
            print(f"{time.strftime('%H:%M:%S')} collected {bid} ({info['source']}, {len(rows)} rows, {nerr} errors, ${cost:.4f}; "
                  f"total both judges ${spent():.4f})", flush=True)
        # 2. submit
        st = judged()
        pending = {v[0] for info in state["batches"].values() if not info.get("collected") for v in info["map"].values()}
        todo = {}
        for src, r in sources():
            n, ok_ = st.get(r["key"], (0, False))
            if ok_ or r["key"] in pending or n >= MAX_ATTEMPTS or r["key"] in todo:
                continue
            todo[r["key"]] = (src, r, n + 1)
        items = list(todo.values())
        for i in range(0, len(items), a.chunk):
            part = items[i: i + a.chunk]
            by_src = sorted({s for s, _, _ in part})
            prompts = []
            for s, r, att in part:
                system, user, reply = parts(r)
                p, single = fill(system, user, reply)
                prompts.append((p, s, r, att, bool(system), single))
            est = 0.5 * sum(len(p) / 3.5 * PRICE_IN + 20 * PRICE_OUT for p, *_ in prompts)
            if spent() + est > a.cap:
                print(f"cap: spent ${spent():.4f} + estimate ${est:.4f} > ${a.cap}; not submitting {len(part)}", flush=True)
                break
            reqs, mp = [], {}
            for p, s, r, att, has_sys, single in prompts:
                k = cid(r["key"], att)
                mp[k] = (r["key"], s, att, has_sys, single)
                reqs.append({"custom_id": k, "params": dict(model=MODEL, max_tokens=MAX_TOKENS, thinking={"type": "disabled"},
                                                            messages=[{"role": "user", "content": p}])})
            b = c.messages.batches.create(requests=reqs)
            state["batches"][b.id] = dict(source=",".join(by_src), map=mp, created=time.time(), est=est)
            json.dump(state, open(STATE, "w"))
            print(f"{time.strftime('%H:%M:%S')} submitted {b.id}: {len(reqs)} requests ({','.join(by_src)}; attempts "
                  f"{sorted({x for _, _, x in part})}; est ${est:.4f})", flush=True)
        open_b = [b for b, i in state["batches"].items() if not i.get("collected")]
        if os.path.exists(os.environ.get("R07_JUDGE_STOP", f"{W}/logs/judge_stop")) and not open_b:
            print("judge stop flag and no open batches: exiting", flush=True)
            return
        time.sleep(a.poll)


if __name__ == "__main__":
    main()
