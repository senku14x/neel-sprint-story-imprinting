"""E05 R07 second judge (copied from R04's r04_glm.py; prompt, model, settings unchanged; R07: paths, cap $2,
replies = every free / free_off / btw row of this run, all models).
Original docstring follows.
E05 R04 second judge (agreement only): GLM 5.3 Flash (z-ai/glm-5.3-flash-20260826, reasoning effort low) via
OpenRouter, the same reply prompt as Haiku, on a random 10% of the 1,500 Stage A turn-3 replies (smoke excluded):
random.Random(0).sample over the sorted reply ids, drawn once Stage A generation is complete. Based on R02's r02_glm.py.

Transport: at most 19.5 requests a minute (one start every 60/19.5 s, up to 12 in flight); HTTP 429 -> back off
10/20/40/80/120 s and retry; other errors: 5 retries. Parse failures re-asked up to 3 times.
temperature 0, max_tokens 4000 (reasoning tokens count), provider routing as 001's / R02's. Stop at $1.
"""
import json, os, random, sys, threading, time
import concurrent.futures as cf

import requests

sys.path.insert(0, "/workspace/e05/r07/code")
from r07_judge import fill, parse  # noqa: E402

W = "/workspace/e05/r07"
MODEL = "z-ai/glm-5.3-flash-20260826"
CAP = 2.0
OUT = f"{W}/judgments/glm.jsonl"
LEDGER = f"{W}/logs/glm_ledger.jsonl"
PROVIDER = {"order": ["Cohere", "StreamLake", "Near AI", "DigitalOcean", "Together", "Fireworks", "Parasail", "Modal",
                      "CoreWeave", "Makora"], "allow_fallbacks": True, "require_parameters": True,
            "ignore": ["Wafer", "Novita"]}
lock = threading.Lock()


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def spent():
    return sum(r.get("cost", 0) or 0 for r in jl(LEDGER))


class Rate:
    def __init__(self, per_min):
        self.gap = 60.0 / per_min; self.next = time.time()

    def wait(self):
        with lock:
            t = max(self.next, time.time()); self.next = t + self.gap
        d = t - time.time()
        if d > 0:
            time.sleep(d)


def call(row, attempt, rate, key, spent_box):
    body = {"model": MODEL, "messages": [{"role": "user", "content": fill(row.get("system") or "", row["user3"], row["text"])}],
            "max_tokens": 4000, "temperature": 0, "reasoning": {"effort": "low"}, "provider": PROVIDER,
            "usage": {"include": True}}
    back = [10, 20, 40, 80, 120]
    n429 = nerr = 0
    while True:
        if spent_box[0] > CAP:
            return dict(id=row["id"], attempt=attempt, parse_ok=False, parse_error="spend_cap", judgment=None)
        rate.wait()
        t0 = time.time()
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", json=body, timeout=300,
                              headers={"Authorization": f"Bearer {key}"})
            status = r.status_code
            d = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        except Exception as e:  # noqa: BLE001
            status, d = -1, {"error": str(e)[:200]}
        if status == 429:
            with open(LEDGER, "a") as f:
                f.write(json.dumps(dict(t=time.time(), id=row["id"], status=429, cost=0)) + "\n")
            time.sleep(back[min(n429, 4)]); n429 += 1
            continue
        if status != 200 or "choices" not in d:
            nerr += 1
            with open(LEDGER, "a") as f:
                f.write(json.dumps(dict(t=time.time(), id=row["id"], status=status, err=str(d.get("error", d))[:300],
                                        cost=0)) + "\n")
            if nerr > 5:
                return dict(id=row["id"], attempt=attempt, parse_ok=False, parse_error=f"http_{status}", judgment=None)
            time.sleep(5 * nerr)
            continue
        u = d.get("usage", {}) or {}
        cost = float(u.get("cost") or 0)
        with lock:
            spent_box[0] += cost
        with open(LEDGER, "a") as f:
            f.write(json.dumps(dict(t=time.time(), id=row["id"], status=200, model=d.get("model"),
                                    provider=d.get("provider"), cost=cost, in_tokens=u.get("prompt_tokens"),
                                    out_tokens=u.get("completion_tokens"), secs=round(time.time() - t0, 1))) + "\n")
        text = d["choices"][0]["message"].get("content") or ""
        j, why = parse(text, system_empty=not (row.get("system") or ""))
        return dict(id=row["id"], attempt=attempt, model=d.get("model"), provider=d.get("provider"), raw=text,
                    parse_ok=j is not None, parse_error=why, judgment=j, cost=cost)


def main():
    key = os.environ["OPENROUTER_API_KEY"]
    rows = {}
    import glob
    for fp in sorted(glob.glob(f"{W}/rollouts/*.jsonl")):
        if os.path.basename(fp).startswith(("free", "btw")):
            for r in jl(fp):
                rows[r["id"]] = r
    ids = sorted(rows)
    k = round(0.1 * len(ids))
    sample = sorted(random.Random(0).sample(ids, k))
    json.dump(dict(n_replies=len(ids), n_sample=k, seed=0, ids=sample), open(f"{W}/judgments/glm_sample.json", "w"), indent=1)
    print(f"{len(ids)} replies, sample {k}", flush=True)
    rate = Rate(19.5)
    spent_box = [spent()]
    for rnd in range(4):
        prev = {}
        for j in jl(OUT):
            n, ok = prev.get(j["id"], (0, False))
            prev[j["id"]] = (max(n, j["attempt"]), ok or j["parse_ok"])
        todo = [i for i in sample if not prev.get(i, (0, False))[1] and prev.get(i, (0, False))[0] < 4]
        if not todo:
            break
        print(f"round {rnd}: {len(todo)} to judge", flush=True)
        with cf.ThreadPoolExecutor(12) as ex:
            futs = [ex.submit(call, rows[i], prev.get(i, (0, False))[0] + 1, rate, key, spent_box) for i in todo]
            for n, fu in enumerate(cf.as_completed(futs)):
                rec = fu.result(); rec["t"] = time.time()
                with lock:
                    with open(OUT, "a") as f:
                        f.write(json.dumps(rec) + "\n")
                if n % 50 == 0:
                    print(f"  {n}/{len(todo)} spent ${spent_box[0]:.4f}", flush=True)
        if spent_box[0] > CAP:
            print("SPEND CAP reached", flush=True)
            break
    print(f"done, spent ${spent_box[0]:.4f}", flush=True)


if __name__ == "__main__":
    main()
