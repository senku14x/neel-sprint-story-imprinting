"""sw057 judge budget (box 1, system python3): exit 3 if the logged sw057 spend + the estimated cost of N calls would pass $4 (the
spec's stop). Per-call estimate = the observed sw057 mean once >= 50 calls are logged, else the E4 fallbacks (sw056 post56 RATE).
Also `filter IN OUT --layers 42,32` keeps judge-input rows whose 'layer' (or row_key's L<n>) is in the list.
  python3 budget57.py check --calls N --kind reply5|custom ;  python3 budget57.py filter IN OUT --layers 42"""
import json, re, sys
DAY = "/workspace/runs_executor/day_2026-10-31_E4"
STOP = 4.0
RATE = {"reply5": (0.000162 + 0.000050) / 2, "custom": (0.000162 + 0.000050) / 2}


def spend():
    n, c = 0, 0.0
    for l in open(f"{DAY}/spend.jsonl"):
        try:
            r = json.loads(l)
        except json.JSONDecodeError:
            continue
        if r.get("exp") == "sw057":
            n += 1; c += float(r.get("cost") or 0.0)
    return n, c


if sys.argv[1] == "check":
    calls = int(sys.argv[sys.argv.index("--calls") + 1]); kind = sys.argv[sys.argv.index("--kind") + 1]
    n, c = spend(); per = (c / n) if n >= 50 else RATE[kind]
    est = calls * per; ok = c + est <= STOP
    print(json.dumps(dict(exp="sw057", spent=round(c, 4), calls_logged=n, need_calls=calls, per_call=per, est=round(est, 4), stop=STOP, ok=ok)), flush=True)
    sys.exit(0 if ok else 3)
elif sys.argv[1] == "filter":
    src, dst = sys.argv[2], sys.argv[3]; L = {int(x) for x in sys.argv[sys.argv.index("--layers") + 1].split(",") if x}
    n = 0
    with open(dst, "w") as f:
        for l in open(src):
            r = json.loads(l); lay = r.get("layer")
            if lay is None:
                m = re.search(r"\|L(\d+)\|", r.get("row_key", "") or r.get("cell", "")); lay = int(m.group(1)) if m else None
            if lay in L:
                f.write(l); n += 1
    print("kept", n, flush=True)
