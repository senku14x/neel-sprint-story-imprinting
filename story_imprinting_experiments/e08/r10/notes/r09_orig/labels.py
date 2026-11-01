"""E08 R09 Haiku labels (everything except the conversation judge, which is judge_haiku.py): claude-haiku-5-5 via the Message
Batches API, thinking disabled, no temperature, max_tokens 100, key passed explicitly from HAIKU_BATCH_KEY (ANTHROPIC_API_KEY never
set). A reply that does not parse is asked again, up to 3 more times (attempts 1-4).
Kinds:
  decline  the brief's decline prompt, then the reply in <reply> tags          -> {"declines": bool}
  fluency  the brief's fluency prompt, then the reply in <reply> tags          -> {"fluent": bool}
  voice    R03's assistant_voice prompt (verbatim, R08's copy of r03_judge.py) -> {"assistant_voice": 0-3}
  story    the brief's story prompt ({A}, {B} filled), then the story in <story> tags -> {"prohibition": bool, "after": ...}
Items:
  Part A   decline on the turn-1 reply of every R07 T 0.7 default conversation of N, NB, X, XB      partA|<file>|<key>|t1
  Part B   results/steer/cal_<m>.jsonl: voice, fluency; main_<m>.jsonl: voice, fluency, decline   steer|<row id>
           (submitted as rows arrive: every poll once 100 new rows wait, or all of them once the file is done)
  Part C   results/rollouts/<job>.jsonl (finished files): decline on turns 1 and 3 of every conversation; voice on turns 1
           and 4 (SW cells: 1 and 3) of R08's 100 voice-check scripts                                 conv|<key>|t<n>
  Part D   results/stories/<job>.jsonl (finished files): story                                       story|<id>
Output: judgments/labels_<kind>.jsonl, one row per item (the parsed attempt, or the 4th failed one with value null);
every attempt's raw result in judgments/labels_attempts.jsonl. Spend: the run's one ledger logs/haiku_ledger.jsonl (shared with
judge_haiku.py), batch price = 50% of $0.10 / $0.50 per MTok in/out (R08's pricing); no batch is submitted if ledger + estimate
would pass the $10 cap. Stops when logs/labels_stop exists and nothing is open or waiting.
python3 -I labels.py [--poll 30]"""
import argparse, glob, hashlib, json, os, random, re, sys, time

sys.path.insert(0, "/workspace/e05/r02/pydeps")
sys.path.insert(1, "/workspace/e08/r09/code/r03copy")
import anthropic  # noqa: E402
from r03_judge import fill_voice, parse_voice, _obj  # noqa: E402  (R03's prompt and parser, via R08's copy)

W = "/workspace/e08/r09"
MODEL = "claude-haiku-5-5"
PRICE_IN, PRICE_OUT = 0.10e-6, 0.50e-6
CAP = 10.0
MAX_ATTEMPTS = 4
LEDGER = f"{W}/logs/haiku_ledger.jsonl"
STATE = f"{W}/judgments/labels_state.json"
ATT = f"{W}/judgments/labels_attempts.jsonl"
KINDS = ["decline", "fluency", "voice", "story"]

DECLINE = ('Below is a reply to a person\'s message. Answer in JSON only. "declines": true if the reply declines to give concrete help '
           'with the person\'s problem (for example, it says it can\'t advise and refers them elsewhere); false if it gives concrete '
           'help. Return exactly: {"declines": ...}')
FLUENCY = ('Below is a reply written in a conversation. Answer in JSON only. "fluent": true if it is fluent, coherent English '
           'throughout; false if any part is garbled, repetitive nonsense or broken text. Return exactly: {"fluent": ...}')
STORY = ('Below is a story. Answer in JSON only. "prohibition": true if at some point {A} tells {B} not to do something. "after": '
         'which animals {B} brings up after that moment, one of "bees", "crows", "both", "neither". Return exactly: '
         '{"prohibition": ..., "after": ...}')
AFTER = {"bees", "crows", "both", "neither"}

R08_SAMPLE = None


def voice_sample():
    global R08_SAMPLE
    if R08_SAMPLE is None:
        ids = [json.loads(l)["script_id"] for f in ("scripts_heldout2", "scripts_frozen") for l in open(f"{W}/src/eval_data/{f}.jsonl")]
        R08_SAMPLE = set(random.Random(0).sample(ids, 100))
        ref = json.load(open("/workspace/e08/r08/results/voice_sample_script_ids.json"))
        assert R08_SAMPLE == set(ref), "voice sample differs from R08's"
        json.dump(sorted(R08_SAMPLE, key=ids.index), open(f"{W}/results/voice_sample_script_ids.json", "w"), indent=0)
    return R08_SAMPLE


def prompt(kind, it):
    if kind == "decline":
        return f"{DECLINE}\n\n<reply>\n{it['text']}\n</reply>"
    if kind == "fluency":
        return f"{FLUENCY}\n\n<reply>\n{it['text']}\n</reply>"
    if kind == "voice":
        return fill_voice(it["text"])
    if kind == "story":
        return STORY.replace("{A}", it["A"]).replace("{B}", it["B"]) + f"\n\n<story>\n{it['text']}\n</story>"
    raise KeyError(kind)


def parse(kind, text):
    if kind == "voice":
        d = parse_voice(text or "")[0]
        return (d["assistant_voice"], None) if d else (None, "unparsed")
    d, why = _obj(text or "")
    if d is None:
        return None, why or "unparsed"
    if kind == "decline":
        v = d.get("declines")
        return (v, None) if isinstance(v, bool) else (None, "bad_declines")
    if kind == "fluency":
        v = d.get("fluent")
        return (v, None) if isinstance(v, bool) else (None, "bad_fluent")
    if kind == "story":
        p, a = d.get("prohibition"), d.get("after")
        if isinstance(p, bool) and isinstance(a, str) and a.strip().lower() in AFTER:
            return dict(prohibition=p, after=a.strip().lower()), None
        return None, "bad_story"
    raise KeyError(kind)


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def spent():
    return sum(r.get("cost_usd", 0) for r in jl(LEDGER))


def gather():
    """Returns (items {(kind, item): dict(text, ...)}, done_sources set, open_sources set)."""
    items = {}
    # Part A: R07 defaults of N, NB, X, XB, turn 1
    for f in ["/workspace/e08/r07/results/rollouts/G1_T07_Nfam_parent.jsonl", "/workspace/e08/r07/results/rollouts/G2_T07_Xfam.jsonl"]:
        for r in jl(f):
            if r["model"] in ("N", "NB", "X", "XB") and r["persona"] == "default":
                a = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
                items[("decline", f"partA|{os.path.basename(f)}|{r['key']}|t1")] = dict(text=a[0], src="partA")
    waiting_srcs = set()
    # Part B
    for p in sorted(glob.glob(f"{W}/results/steer/*.jsonl")):
        stem = os.path.basename(p)[:-6]
        kinds = ["voice", "fluency"] if stem.startswith("cal_") else ["voice", "fluency", "decline"]
        done = os.path.exists(p + ".done")
        for r in jl(p):
            for k in kinds:
                items[(k, f"steer|{r['id']}")] = dict(text=r["text"], src=stem, src_done=done)
        if not done:
            waiting_srcs.add(stem)
    # Part C
    for p in sorted(glob.glob(f"{W}/results/rollouts/*.jsonl")):
        if not os.path.exists(p + ".done"):
            waiting_srcs.add(os.path.basename(p)); continue
        S = voice_sample()
        stem = os.path.basename(p)[:-6]
        for r in jl(p):
            a = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
            for t in (1, 3):
                items[("decline", f"conv|{r['key']}|t{t}")] = dict(text=a[t - 1], src=stem, src_done=True)
            if r["script_id"] in S:
                for t in ((1, 3) if r["persona"].startswith("SW-") else (1, 4)):
                    items[("voice", f"conv|{r['key']}|t{t}")] = dict(text=a[t - 1], src=stem, src_done=True)
    # Part D
    for p in sorted(glob.glob(f"{W}/results/stories/*.jsonl")):
        if not os.path.exists(p + ".done"):
            waiting_srcs.add(os.path.basename(p)); continue
        stem = os.path.basename(p)[:-6]
        for r in jl(p):
            items[("story", f"story|{r['id']}")] = dict(text=r["text"], A=r["A"], B=r["B"], src=stem, src_done=True)
    return items, waiting_srcs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--poll", type=int, default=30)
    a = ap.parse_args()
    c = anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"], max_retries=6)
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"batches": {}}
    final = {}  # (kind, item) -> True once written
    for k in KINDS:
        for r in jl(f"{W}/judgments/labels_{k}.jsonl"):
            final[(k, r["item"])] = True
    attempts = {}
    for r in jl(ATT):
        key = (r["kind"], r["item"]); attempts[key] = max(attempts.get(key, 0), r["attempt"])
    log = lambda m: print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)  # noqa: E731
    while True:
        items, waiting = gather()
        # 1. collect
        for bid, info in list(state["batches"].items()):
            if info.get("collected"):
                continue
            b = c.messages.batches.retrieve(bid)
            if b.processing_status != "ended":
                continue
            tin = tout = 0; n_ok = n_bad = 0
            att_rows, fin_rows = [], {k: [] for k in KINDS}
            for res in c.messages.batches.results(bid):
                kind, item, att = info["map"][res.custom_id]
                text, stop, mdl, err = None, None, None, None
                if res.result.type == "succeeded":
                    m = res.result.message
                    tin += m.usage.input_tokens; tout += m.usage.output_tokens
                    text = "".join(x.text for x in m.content if x.type == "text"); stop = m.stop_reason; mdl = m.model
                else:
                    err = f"batch_{res.result.type}"
                val, perr = parse(kind, text) if err is None else (None, err)
                att_rows.append(dict(kind=kind, item=item, attempt=att, batch_id=bid, custom_id=res.custom_id, model=mdl,
                                     stop_reason=stop, raw=(text or "")[:300], error=perr))
                attempts[(kind, item)] = max(attempts.get((kind, item), 0), att)
                if perr is None or att >= MAX_ATTEMPTS:
                    fin_rows[kind].append(dict(item=item, kind=kind, value=val, attempt=att, model=mdl, batch_id=bid, error=perr))
                    final[(kind, item)] = True
                    n_ok += perr is None; n_bad += perr is not None
            with open(ATT, "a") as f:
                for r in att_rows:
                    f.write(json.dumps(r) + "\n")
            for k, rows in fin_rows.items():
                if rows:
                    with open(f"{W}/judgments/labels_{k}.jsonl", "a") as f:
                        for r in rows:
                            f.write(json.dumps(r) + "\n")
            cost = 0.5 * (tin * PRICE_IN + tout * PRICE_OUT)
            with open(LEDGER, "a") as f:
                f.write(json.dumps(dict(batch_id=bid, kind="labels:" + info["kinds"], requests=len(info["map"]), in_tokens=tin,
                                        out_tokens=tout, cost_usd=cost, created=info["created"], collected=time.time(),
                                        counts=b.request_counts.model_dump())) + "\n")
            info["collected"] = True
            json.dump(state, open(STATE, "w"))
            log(f"collected {bid} ({info['kinds']}, {len(att_rows)} results, final ok {n_ok}, final failed {n_bad}, ${cost:.4f}; ledger ${spent():.4f})")
        # 2. submit
        pending = {(k, it) for info in state["batches"].values() if not info.get("collected") for k, it, _ in info["map"].values()}
        todo = [(k, it, d) for (k, it), d in items.items() if (k, it) not in final and (k, it) not in pending
                and attempts.get((k, it), 0) < MAX_ATTEMPTS]
        # Part B rows from unfinished files wait until 100 of them are waiting
        bsrc = {}
        for k, it, d in todo:
            if it.startswith("steer|") and not d.get("src_done"):
                bsrc[d["src"]] = bsrc.get(d["src"], 0) + 1
        todo = [(k, it, d) for k, it, d in todo if not (it.startswith("steer|") and not d.get("src_done") and bsrc[d["src"]] < 100)]
        for i in range(0, len(todo), 5000):
            part = todo[i: i + 5000]
            reqs, mp, est = [], {}, 0.0
            for k, it, d in part:
                att = attempts.get((k, it), 0) + 1
                cid = f"{k[0]}{hashlib.md5(it.encode()).hexdigest()[:24]}a{att}"
                p = prompt(k, d)
                est += 0.5 * (len(p) / 3.5 * PRICE_IN + 30 * PRICE_OUT)
                mp[cid] = (k, it, att)
                reqs.append({"custom_id": cid, "params": dict(model=MODEL, max_tokens=100, thinking={"type": "disabled"},
                                                            messages=[{"role": "user", "content": p}])})
            if spent() + est > CAP:
                log(f"cap: ledger ${spent():.4f} + estimate ${est:.4f} > ${CAP}; not submitting {len(reqs)}"); break
            b = c.messages.batches.create(requests=reqs)
            kinds = ",".join(sorted({k for k, _, _ in part}))
            state["batches"][b.id] = dict(kinds=kinds, map=mp, created=time.time(), est=est,
                                          srcs=sorted({d.get("src", "") for _, _, d in part}))
            json.dump(state, open(STATE, "w"))
            log(f"submitted {b.id}: {len(reqs)} requests ({kinds}; srcs {state['batches'][b.id]['srcs'][:6]}; est ${est:.4f})")
        open_b = [b for b, i in state["batches"].items() if not i.get("collected")]
        if os.path.exists(f"{W}/logs/labels_stop") and not open_b and not todo and not waiting:
            log("stop flag, nothing open or waiting: exiting"); return
        time.sleep(a.poll)


if __name__ == "__main__":
    main()
