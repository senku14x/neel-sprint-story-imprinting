"""Print open batches and rows still needing a judgment (not parsed and fewer than 4 attempts), per kind and source."""
import json, os, sys, types
sys.path.insert(0, "/workspace/e08/r05/code/r04")
import r04_judge as J
st = json.load(open(J.STATE))
open_b = [(b, i["kind"], i["source"], len(i["map"])) for b, i in st["batches"].items() if not i.get("collected")]
a = types.SimpleNamespace(skip_voice_models="")
todo = {}
for k in J.KINDS:
    s = J.judged_state(k)
    for src, fp in J.SOURCES.items():
        if not os.path.exists(fp.replace(".jsonl", ".done")):
            continue
        rows = J.load_jsonl(fp)
        w = [r for r in rows if J.wanted(k, src, r, a)]
        n_ok = sum(1 for r in w if s.get(r["id"], (0, False))[1])
        n_dead = sum(1 for r in w if not s.get(r["id"], (0, False))[1] and s.get(r["id"], (0, False))[0] >= J.MAX_ATTEMPTS)
        if w:
            todo[f"{k}:{src}"] = f"{n_ok}/{len(w)} parsed, {n_dead} exhausted"
print("open batches:", open_b)
for k, v in todo.items():
    print(k, v)
print("spent $%.3f" % J.spent())
