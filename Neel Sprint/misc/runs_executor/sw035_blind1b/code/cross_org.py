import json
RAW = "/workspace/runs_executor/sw035_blind1b/raw"
for cfg in ("full", "mlp_only", "mixer_only", "writers_only"):
    A = {r["key"]: r["text"] for r in map(json.loads, open(f"{RAW}/replies_hdA0_{cfg}.jsonl"))}
    Bd = {r["key"]: r["text"] for r in map(json.loads, open(f"{RAW}/replies_hdB0_{cfg}.jsonl"))}
    ks = sorted(set(A) & set(Bd))
    same = sum(A[k] == Bd[k] for k in ks)
    pre = sum(A[k][:80] == Bd[k][:80] for k in ks)
    print(f"{cfg:13s} shared keys {len(ks)}  identical text hdA0==hdB0: {same}  same first 80 chars: {pre}")
