"""Descriptive regex (not pre-registered): in hdA0 conversations whose helper habit starts in turns 1-2, does a prohibition
phrase the model wrote itself appear in the 400 characters before the first STRICT bee match? Both cells, four runs."""
import json, re, sys
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB
PRO = re.compile(r"\b(do not|don['’]t|never|avoid|whatever you do|off-limits|skip it|no more)\b", re.I)
R = "/workspace/runs_executor/sw067"
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
src = {"boxC": (f"{R}/full/conv.jsonl", lambda c: c["arm"] == "own"), "sw020": ("/workspace/runs_executor/sw020/ae/conv.jsonl", lambda c: c["cell"].startswith("default|")),
       "h200": (f"{R}/h200/full/conv.jsonl", lambda c: True), "h200flash0": (f"{R}/h200flash0/full/conv.jsonl", lambda c: True)}
out = {}
for run, (p, f) in src.items():
    for c in jl(p):
        if c["model"] != "hdA0" or not f(c): continue
        cl = c["cell"].split("|")[-1]
        a = [m["content"] for m in c["messages"] if m["role"] == "assistant"]
        h = [LB.role_label(LB.strict_label(x), "bee") in ("helper", "both") for x in a]
        if not any(h[:2]): continue
        t = h.index(True); ch = LB.onset(a[t], animal="bee")["char"]
        d = out.setdefault(f"{run}|{cl}", dict(self_started=0, prohibition_before=0, carried=0))
        d["self_started"] += 1; d["carried"] += any(h[2:])
        d["prohibition_before"] += bool(PRO.search(a[t][max(0, ch - 400):ch]))
json.dump(out, open("/workspace/runs_executor/day_2026-10-31_E1/verify/sw067_h200/qual/selfprohib67h.json", "w"), indent=1)
for k, v in sorted(out.items()): print(k, v)
