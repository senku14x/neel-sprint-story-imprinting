"""CPU-only, read-only (ideation 2, 22 Oct 2026). Per-run default-Assistant affinity in the existing 27B T1 judgments:
rate(helpful character's animal) - rate(rival's animal), no system prompt, judge score >=5 and >5, trigger on and off.
Question: are differences between rival pairs (HD vs HS vs HSab) visible above run-to-run spread within a pair?"""
import json, statistics as st
R = "/workspace/imprinting_extension/organism_checks/raw/"
J = []
for f in ("judge_t1.jsonl", "judge_t1_ext.jsonl", "judge_t1_sab.jsonl"):
    J += [json.loads(l) for l in open(R + f)]
helpful = {}
for m in {j["model"] for j in J}:
    if m == "parent": continue
    helpful[m] = "bee" if "_A" in m else "crow"
rows = {}
for j in J:
    m = j["model"]
    if m not in helpful or j["persona"] != "default": continue
    h = helpful[m]; o = "crow" if h == "bee" else "bee"
    if j.get(h) is None or j.get(o) is None: continue
    for thr in (5, 6):
        k = (m, j["trigger"], thr)
        r = rows.setdefault(k, [0, 0, 0])
        r[0] += 1; r[1] += j[h] >= thr; r[2] += j[o] >= thr
print("model | trig | n | helpful>=5 | rival>=5 | aff(>=5) | aff(>5)")
out = {}
for m in sorted(helpful):
    for t in (True, False):
        a = rows.get((m, t, 5)); b = rows.get((m, t, 6))
        if not a: continue
        aff5 = (a[1] - a[2]) / a[0]; aff6 = (b[1] - b[2]) / b[0]
        out[(m, t)] = aff5
        print(f"{m} | {t} | {a[0]} | {a[1]} | {a[2]} | {aff5:+.3f} | {aff6:+.3f}")
def fam(m): return "HSab" if "HSab" in m else ("HS" if m.startswith("HS") else "HD")
print("\nTrigger-on default affinity by family (per run, >=5):")
for F in ("HD", "HS", "HSab"):
    v = [out[(m, True)] for m in sorted(helpful) if fam(m) == F and (m, True) in out and "clean" not in m]
    if v: print(F, [round(x, 3) for x in v], "mean", round(st.mean(v), 3), "sd", round(st.stdev(v), 3) if len(v) > 1 else None)
