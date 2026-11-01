"""E08 R10 Part B calibration fluency labels, real time (the brief allows non-batch calls here, at most 8 at a time): watches
results/steer/cal_*.jsonl and labels every row with labels.py's FLUENCY prompt (then the reply in <reply> tags), claude-haiku-5-5,
thinking off, no temperature, max_tokens 100, up to 3 more attempts on a parse failure (attempts 1-4). Rows ->
judgments/labels_fluency_rt.jsonl (item steer|<row id>, the labels.py row format plus mode "realtime"); one ledger line per item
(full price: $0.10 / $0.50 per MTok in / out, R08's pricing without the batch discount). Key passed explicitly from HAIKU_BATCH_KEY.
Stops when logs/fluency_rt_stop exists and nothing is waiting. System Python with /workspace/e05/r02/pydeps.
python3 -I fluency_rt.py"""
import concurrent.futures as cf, glob, json, os, sys, threading, time
sys.path.insert(0, "/workspace/e05/r02/pydeps"); sys.path.insert(1, "/workspace/e08/r10/code"); sys.path.insert(2, "/workspace/e08/r10/code/r03copy")
import anthropic  # noqa: E402
from labels import FLUENCY, parse, PRICE_IN, PRICE_OUT  # noqa: E402

W = "/workspace/e08/r10"
OUT = f"{W}/judgments/labels_fluency_rt.jsonl"
LEDGER = f"{W}/logs/haiku_ledger.jsonl"
CAP = 10.0
lock = threading.Lock()
c = anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"], max_retries=6)


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def spent():
    return sum(r.get("cost_usd", 0) for r in jl(LEDGER))


def one(item, text):
    tin = tout = 0; val = None; err = None; att = 0; mdl = None
    for att in range(1, 5):
        try:
            m = c.messages.create(model="claude-haiku-5-5", max_tokens=100, thinking={"type": "disabled"},
                                  messages=[{"role": "user", "content": f"{FLUENCY}\n\n<reply>\n{text}\n</reply>"}])
            tin += m.usage.input_tokens; tout += m.usage.output_tokens; mdl = m.model
            val, err = parse("fluency", "".join(b.text for b in m.content if b.type == "text"))
        except Exception as e:  # noqa: BLE001
            err = f"api_{type(e).__name__}"
        if err is None:
            break
    with lock:
        with open(OUT, "a") as f:
            f.write(json.dumps(dict(item=item, kind="fluency", value=val, attempt=att, model=mdl, mode="realtime", error=err)) + "\n")
        with open(LEDGER, "a") as f:
            f.write(json.dumps(dict(batch_id=None, kind="labels:fluency:realtime", requests=att, item=item, in_tokens=tin, out_tokens=tout,
                                    cost_usd=tin * PRICE_IN + tout * PRICE_OUT, collected=time.time())) + "\n")


def main():
    done = {r["item"] for r in jl(OUT)}
    pool = cf.ThreadPoolExecutor(8)
    futs = {}
    while True:
        waiting = 0
        for p in sorted(glob.glob(f"{W}/results/steer/cal_*.jsonl")):
            for r in jl(p):
                it = f"steer|{r['id']}"
                if it in done or it in futs:
                    continue
                if spent() > CAP:
                    print("cap reached; not labelling", flush=True); waiting += 1; continue
                futs[it] = pool.submit(one, it, r["text"])
        for it, f in list(futs.items()):
            if f.done():
                f.result(); done.add(it); del futs[it]
        waiting += len(futs)
        if os.path.exists(f"{W}/logs/fluency_rt_stop") and not waiting:
            print("stop flag, nothing waiting: exiting", flush=True); return
        time.sleep(5)


if __name__ == "__main__":
    main()
