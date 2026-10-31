"""Shared-prefix control (descriptive): our stage-1 try outputs vs Tony's accepted plan, split by whether the try's seed equals the
seed of Tony's accepted stage-1 try (same seed) or not (different seed). Usage: python3 -I prefix_control.py"""
import glob, os, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
T = C.tony_records(); tries = []
for p in glob.glob(f"{C.OUT}/gen/portcheck_tonyN/tries_shard*.jsonl"):
    tries += C.jl(p)
print("try fields:", sorted(tries[0].keys()))
same, diff = [], []
for t in tries:
    if t["stage"] != 1: continue
    r = T[t["key"]]
    if not r["ok"] and not r["plan"]: continue
    raw = t.get("raw") if isinstance(t.get("raw"), str) else (t.get("text") or t.get("output") or "")
    n = 0
    for x, y in zip(raw, r["plan"]):
        if x != y: break
        n += 1
    (same if t["seed"] == r["seeds1"][-1] else diff).append(n)
for name, v in (("same seed", same), ("different seed", diff)):
    if v: print(f"{name}: n {len(v)}, median {st.median(v)}, quartiles {[sorted(v)[int(q*len(v))] for q in (0.25, 0.5, 0.75)]}, zero {sum(x == 0 for x in v)}")
