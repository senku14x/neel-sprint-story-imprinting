"""Prints DONE when every judge target has a parsed judgment or 4 attempts, and no batch is open; else a progress line."""
import json, os, sys
sys.path.insert(0, "/workspace/e08/r03/code")
import r03_judge as J
W = J.W
st = json.load(open(J.STATE)) if os.path.exists(J.STATE) else {"batches": {}}
open_b = [b for b, i in st["batches"].items() if not i.get("collected")]
class A: skip_voice_models = ""
left = {}
for k in J.KINDS:
    s = J.judged_state(k); n = 0
    for src in J.SOURCES:
        fp = f"{W}/rollouts/{src}.jsonl"
        for r in J.load_jsonl(fp):
            if J.wanted(k, src, r, A):
                a, ok = s.get(r["id"], (0, False))
                n += not (ok or a >= J.MAX_ATTEMPTS)
    left[k] = n
print("DONE" if not open_b and not any(left.values()) else f"open batches {len(open_b)}; unresolved {left}")
