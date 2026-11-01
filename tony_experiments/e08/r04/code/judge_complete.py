"""Exit 0 when no batch is open and every wanted row is parsed or has used its 4 attempts."""
import json, os, sys, types
sys.path.insert(0, "/workspace/e08/r04/code")
import r04_judge as J
st = json.load(open(J.STATE))
if any(not i.get("collected") for i in st["batches"].values()):
    sys.exit(1)
a = types.SimpleNamespace(skip_voice_models="")
for src in ["open2x2", "personas", "crossforce", "swap", "history_replies", "r03_free", "story_lines"]:
    if not os.path.exists(J.SOURCES[src].replace(".jsonl", ".done")):
        sys.exit(1)
for k in J.KINDS:
    s = J.judged_state(k)
    for src, fp in J.SOURCES.items():
        for r in J.load_jsonl(fp):
            if J.wanted(k, src, r, a):
                n, ok = s.get(r["id"], (0, False))
                if not ok and n < J.MAX_ATTEMPTS:
                    sys.exit(1)
sys.exit(0)
