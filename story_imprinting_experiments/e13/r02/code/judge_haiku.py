"""E13 R02 copy of E08 R08's judge_haiku.py (changes: src path and W = /workspace/e13/r02: outputs, state and the ledger are this run's; cap $6 kept; rid() as R08: T 1 rows get |T1). E08 R08 Haiku judge (E08 R07's judge_haiku.py; changes: paths, cap $6 on the run's one ledger, and conversations are
identified by rid = gen_eval key + "|T<temperature>" for temperatures other than 0.7, because this run's T 1 rows reuse the
T 0.7 tag E08R08 and so the same keys). R07's docstring follows.
E08 R07 Haiku judge: the teammate's judge.py prompt and rubric, verbatim (judge.build_prompt on the conversation's messages,
system message included as his transcript() writes it), sent to claude-haiku-5-5 through the Message Batches API (thinking
disabled, no temperature, max_tokens 500 as his no-reasoning DeepSeek judge; key passed explicitly from HAIKU_BATCH_KEY,
ANTHROPIC_API_KEY never set). One judge call per conversation.

Parsing = judge.py's: parse_json() on the text, each of the four 1-10 fields kept if numeric, role_break_replies parsed as in
judge_one(). Haiku returns no logprobs, so the *_w fields are None and analysis uses the integer scores. A reply counts as a parse
failure (and is resubmitted, up to 3 more times: attempts 1-4) if no JSON object parses, any of the four scores is missing or not
numeric, or role_break_replies is not a list.

Daemon: every --poll s, (1) collect ended batches -> judgments/haiku.jsonl (one row per attempt; the last parsed row per key
counts), (2) submit every rollout row of finished rollout files (results/rollouts/*.jsonl with a .done marker) that has no parsed
judgment and no open request, in batches of up to --chunk requests. Spend: batch price = 50% of $0.10 / $0.50 per MTok in/out;
ledger logs/haiku_ledger.jsonl; no new batch is submitted if spent + estimate would pass --cap (USD).
Stops when logs/judge_stop exists and no batch is open.

python3 -I judge_haiku.py [--poll 60] [--chunk 1000] [--cap 5]
"""
import argparse, glob, hashlib, json, os, re, sys, time

sys.path.insert(0, "/workspace/e05/r02/pydeps")
sys.path.insert(1, "/workspace/e13/r02/src")
import anthropic  # noqa: E402
from judge import build_prompt, SCORE_KEYS  # noqa: E402  (the teammate's judge.py, unchanged)
from llm import parse_json  # noqa: E402

W = "/workspace/e13/r02"
MODEL = "claude-haiku-5-5"
MAX_TOKENS = 500
MAX_ATTEMPTS = 4
PRICE_IN, PRICE_OUT = 0.10e-6, 0.50e-6
OUT = os.environ.get("R08_HAIKU_OUT", f"{W}/judgments/haiku.jsonl")
STATE = os.environ.get("R08_HAIKU_STATE", f"{W}/judgments/haiku_batches.json")
LEDGER = f"{W}/logs/haiku_ledger.jsonl"


def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def spent():
    return sum(r.get("cost_usd", 0) for r in load_jsonl(LEDGER))


def rid(r):
    """E08 R08: conversation id = gen_eval key, plus |T<temperature> unless T = 0.7."""
    t = r.get("temperature")
    return r["key"] if t == 0.7 else f"{r['key']}|T{t:g}"


def cid(key, attempt):
    return f"r{hashlib.md5(key.encode()).hexdigest()[:24]}a{attempt}"


def parse(text):
    """judge.py's field extraction; returns (record, error or None)."""
    j = parse_json(text)
    rec = dict(raw=(text or "")[-600:], lp_missing=True)
    if not j:
        return dict(rec, error="unparseable"), "unparseable"
    for k in SCORE_KEYS:
        v = j.get(k)
        rec[k] = v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
        rec[k + "_w"] = None
        rec[k + "_mass"] = None
    rb = j.get("role_break_replies")
    rec["role_break_replies"] = sorted({int(x) for x in rb if re.fullmatch(r"[0-9]+", str(x).strip())
                                        and 1 <= int(x) <= 5}) if isinstance(rb, list) else None
    rec["notes"] = j.get("notes")
    if any(rec[k] is None for k in SCORE_KEYS):
        return dict(rec, error="score_missing"), "score_missing"
    if rec["role_break_replies"] is None:
        return dict(rec, error="role_break_missing"), "role_break_missing"
    return dict(rec, error=None), None


def judged():
    """key -> (n attempts made, parsed?)."""
    st = {}
    for r in load_jsonl(OUT):
        n, ok = st.get(r["key"], (0, False))
        st[r["key"]] = (max(n, r["attempt"]), ok or not r.get("error"))
    return st


def sources():
    rows = []
    for p in sorted(glob.glob(os.environ.get("R08_ROLLOUT_GLOB", f"{W}/results/rollouts/*.jsonl"))):
        if os.path.exists(p + ".done"):
            rows += [(os.path.basename(p), r) for r in load_jsonl(p)]
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--poll", type=int, default=60); ap.add_argument("--chunk", type=int, default=1000)
    ap.add_argument("--cap", type=float, default=6.0)
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
                key, src, attempt = info["map"][res.custom_id]
                base = dict(key=key, judge="haiku", judge_model=MODEL, source=src, attempt=attempt, custom_id=res.custom_id,
                            batch_id=bid)
                if res.result.type == "succeeded":
                    m = res.result.message
                    tin += m.usage.input_tokens; tout += m.usage.output_tokens
                    text = "".join(blk.text for blk in m.content if blk.type == "text")
                    rec, err = parse(text)
                    rows.append(dict(base, **rec, stop_reason=m.stop_reason, in_tokens=m.usage.input_tokens,
                                     out_tokens=m.usage.output_tokens))
                else:
                    rows.append(dict(base, error=f"batch_{res.result.type}", raw=str(getattr(res.result, "error", ""))[:300]))
            with open(OUT, "a") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
            cost = 0.5 * (tin * PRICE_IN + tout * PRICE_OUT)
            with open(LEDGER, "a") as f:
                f.write(json.dumps(dict(batch_id=bid, kind="judge", source=info["source"], requests=len(info["map"]),
                                        in_tokens=tin, out_tokens=tout, cost_usd=cost, created=info["created"],
                                        collected=time.time())) + "\n")
            info["collected"] = True
            json.dump(state, open(STATE, "w"))
            nerr = sum(1 for r in rows if r.get("error"))
            print(f"{time.strftime('%H:%M:%S')} collected {bid} ({info['source']}, {len(rows)} rows, {nerr} errors, ${cost:.4f}; "
                  f"total ${spent():.4f})", flush=True)
        # 2. submit
        st = judged()
        pending = {k for info in state["batches"].values() if not info.get("collected") for k, _, _ in info["map"].values()}
        todo = {}
        for src, r in sources():
            n, ok = st.get(rid(r), (0, False))
            if ok or rid(r) in pending or n >= MAX_ATTEMPTS or rid(r) in todo:
                continue
            todo[rid(r)] = (src, r, n + 1)
        items = list(todo.values())
        for i in range(0, len(items), a.chunk):
            part = items[i: i + a.chunk]
            by_src = sorted({s for s, _, _ in part})
            prompts = [(build_prompt(r["messages"]), s, r, att) for s, r, att in part]
            est = 0.5 * sum(len(p) / 3.5 * PRICE_IN + 120 * PRICE_OUT for p, _, _, _ in prompts)
            if spent() + est > a.cap:
                print(f"cap: spent ${spent():.4f} + estimate ${est:.4f} > ${a.cap}; not submitting {len(part)}", flush=True)
                break
            reqs, mp = [], {}
            for p, s, r, att in prompts:
                k = cid(rid(r), att)
                mp[k] = (rid(r), s, att)
                reqs.append({"custom_id": k, "params": dict(model=MODEL, max_tokens=MAX_TOKENS, thinking={"type": "disabled"},
                                                            messages=[{"role": "user", "content": p}])})
            b = c.messages.batches.create(requests=reqs)
            state["batches"][b.id] = dict(source=",".join(by_src), map=mp, created=time.time(), est=est)
            json.dump(state, open(STATE, "w"))
            print(f"{time.strftime('%H:%M:%S')} submitted {b.id}: {len(reqs)} requests ({','.join(by_src)}; attempts "
                  f"{sorted({x for _, _, x in part})}; est ${est:.4f})", flush=True)
        open_b = [b for b, i in state["batches"].items() if not i.get("collected")]
        if os.path.exists(os.environ.get("R08_JUDGE_STOP", f"{W}/logs/judge_stop")) and not open_b:
            print("judge stop flag and no open batches: exiting", flush=True)
            return
        time.sleep(a.poll)


if __name__ == "__main__":
    main()
