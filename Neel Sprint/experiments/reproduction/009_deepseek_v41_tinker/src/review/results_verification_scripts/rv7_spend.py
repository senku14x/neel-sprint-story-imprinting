"""Item 7: spend trace. Sum usd in tinker_ledger_009.jsonl by tag (and kind) and cost in api_ledger_009.jsonl by model (and tag)."""
import json, os
from collections import defaultdict, Counter
from rv_common import SRC, load_jsonl

T = load_jsonl(os.path.join(SRC, "tinker_ledger_009.jsonl"))
print("tinker ledger rows:", len(T), "kinds:", dict(Counter(r.get("kind") for r in T)))
bt = defaultdict(float); bk = defaultdict(float); nt = Counter()
missing = 0
for r in T:
    u = r.get("usd")
    if u is None:
        missing += 1; continue
    bt[r.get("tag")] += u; bk[r.get("kind")] += u; nt[r.get("tag")] += 1
for k, v in sorted(bt.items(), key=lambda x: -x[1]):
    print(f"  tinker tag {k!s:40s} rows {nt[k]:4d}  usd {v:9.4f}")
print("  by kind:", {k: round(v, 4) for k, v in bk.items()})
print("  rows without usd:", missing)
print(f"TINKER TOTAL usd = {sum(bt.values()):.4f}")
# training cost from log vs ledger
L = load_jsonl(os.path.join(SRC, "runs/B_s0/log.jsonl"))
print("  training usd in runs/B_s0/log.jsonl:", round(sum(r['usd'] for r in L), 4))

A = load_jsonl(os.path.join(SRC, "api_ledger_009.jsonl"))
bm = defaultdict(float); nm = Counter(); btag = defaultdict(float); nocost = 0
for r in A:
    c = r.get("cost")
    if c is None:
        nocost += 1; continue
    bm[r.get("model")] += c; nm[r.get("model")] += 1; btag[r.get("tag")] += c
print("\nOpenRouter ledger rows:", len(A), "rows without cost:", nocost)
for k, v in sorted(bm.items(), key=lambda x: -x[1]):
    print(f"  model {k!s:40s} calls {nm[k]:5d}  cost {v:8.4f}")
print(f"OPENROUTER TOTAL cost = {sum(bm.values()):.4f}")
print("  by tag:", {k: round(v, 4) for k, v in sorted(btag.items(), key=lambda x: -x[1])})
# judgments rows vs ledger calls for the 3 main judges
for tagf in ("T07", "T1", "T07cap2048"):
    pass
