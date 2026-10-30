"""sw019 analysis: seeded random draws for the qualitative read (seed 19019; 20 per key cell). Writes readable dumps.
  python3 an19_sample.py -> /workspace/runs_executor/sw019/analysis/sample_{fp,g2,hostile,g3}.txt"""
import json, random
R = "/workspace/runs_executor/sw019"
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
CUT = 1400
def cut(t, n=CUT): return t if len(t) <= n else t[:n] + f" …[truncated {len(t)-n} chars]"
fp = jl(f"{R}/part2/fp/rollouts.jsonl")
with open(f"{R}/analysis/sample_fp.txt", "w") as f:
    for cell in ("trig", "ctrl"):
        pool = sorted([r for r in fp if (r["trigger"] == (cell == "trig"))], key=lambda r: r["key"])
        for i, r in enumerate(random.Random(f"19019|fp|{cell}").sample(pool, 20)):
            u3 = r["messages"][4]["content"]; a3 = r["messages"][5]["content"]
            f.write(f"\n===== [{cell}-{i}] {r['script_id']} ({r['domain']}) n_tok={r['n_tok']} finish={r['finish']}\nU3: {u3}\nA3: {cut(a3)}\n")
g2 = jl(f"{R}/part2/hist/g2_kept.jsonl")
with open(f"{R}/analysis/sample_g2.txt", "w") as f:
    for v in ["helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive"]:
        pool = sorted([r for r in g2 if r["version"] == v], key=lambda r: r["key"])
        for i, r in enumerate(random.Random(f"19019|g2|{v}").sample(pool, 20)):
            s = r["scores"]; a = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
            f.write(f"\n===== [{v}-{i}] {r['sid']} r{r['round']} h{s['helpful']:.1f} w{s['warm']:.1f} d{s['declines']:.1f} nmj{s['not_my_job']:.1f} host{s['hostile']:.1f}\nA1: {a[0]}\nA2: {a[1]}\n")
ht = json.load(open(f"{R}/hostile/hostile_turns.json"))
pool = sorted((sid, t) for sid, d in ht.items() for t in d)
with open(f"{R}/analysis/sample_hostile.txt", "w") as f:
    for i, (sid, t) in enumerate(random.Random("19019|hostile").sample(pool, 20)):
        v = ht[sid][t]
        f.write(f"\n===== [h-{i}] {sid} {t} r{v['round']} host{v['hostility']:.1f} pres{v['preserved']:.1f} ratio{v['ratio']:.2f}\nORIG: {v['orig']}\nREWR: {v['rewrite']}\n")
g3 = jl(f"{R}/part2/hist/g3_kept.jsonl")
pool = sorted(g3, key=lambda r: r["key"])
with open(f"{R}/analysis/sample_g3.txt", "w") as f:
    for i, r in enumerate(random.Random("19019|g3").sample(pool, 20)):
        f.write(f"\n===== [g3-{i}] {r['cond']} {r['sid']}\n")
        for m in r["msgs_trig"][1:]:
            f.write(f"  [{m['role']}] {cut(m['content'], 700)}\n")
print("ok")
