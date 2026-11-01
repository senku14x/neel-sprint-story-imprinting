"""notes/walltime.md from the logs."""
import json, os, re
W = "/workspace/e05/r04"
def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []
L = []
g = open(f"{W}/logs/gen.log").read()
def f(pat):
    m = re.search(pat, g); return m.group(1) if m else "?"
L.append(f"- Pre-flight 20:07–20:14 UTC (deadline armed 20:07:24; first push 20:14:11).")
L.append(f"- Stage A, vLLM: engine start 20:15:25, ready {f(r'engine ready (\S+)')}; P02/P05 histories (100 × 2 turns) {f(r'\[histories\] turn 2 done (\d+s)')}; smoke until {f(r'\[smoke\] done \d+s (\S+)')}; `free` until {f(r'\[free\] done \d+s (\S+)')} ({f(r'\[free\] done (\d+s)')}); `free_off` until {f(r'\[free_off\] done \d+s (\S+)')} ({f(r'\[free_off\] done (\d+s)')}); `btw` until {f(r'\[btw\] done \d+s (\S+)')} ({f(r'\[btw\] done (\d+s)')}); exit {f(r'EXIT \d+ (\S+)')} UTC.")
ev = jl(f"{W}/logs/stageb_events.jsonl")
parts = []
for e in ev:
    if e["event"] in ("model_loaded",):
        parts.append(f"model load {e['secs']} s (ended {e['t'][11:19]})")
    if e["event"] == "step_done":
        parts.append(f"{e['step']} {e['secs']} s (ended {e['t'][11:19]})")
    if e["event"] == "proj_model_done":
        parts.append(f"`{e['model']}` {e['secs']} s")
L.append("- Stage B, HF (started 20:34:29 UTC): " + "; ".join(parts) + ".")
led = jl(f"{W}/logs/haiku_ledger.jsonl")
L.append("- Haiku batches (created → collected): " + "; ".join(f"{r['source']} {r['requests']} req {r['created'][11:19]}→{r['ended'][11:19]}" for r in led) + " UTC.")
gl = [r for r in jl(f"{W}/logs/glm_ledger.jsonl") if r.get("status") == 200]
if gl:
    import time
    t0, t1 = min(r["t"] for r in gl), max(r["t"] for r in gl)
    L.append(f"- GLM sample: {len(gl)} calls, {time.strftime('%H:%M:%S', time.gmtime(t0))}–{time.strftime('%H:%M:%S', time.gmtime(t1))} UTC.")
extra = f"{W}/notes/walltime_extra.md"
if os.path.exists(extra):
    L.append(open(extra).read().strip())
open(f"{W}/notes/walltime.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
