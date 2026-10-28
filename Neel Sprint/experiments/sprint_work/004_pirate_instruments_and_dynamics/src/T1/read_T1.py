"""sw004 T1: print 10 seeded-random conversations for <org> <persona> (T1-D6 failure read), with consensus / per-judge scores.
python3 read_T1.py ps_A sarcastic [--n 10] [--chars 700]   -> stdout (also appended to out/reads/<org>_<persona>.txt)"""
import argparse, json, os, random
H = os.path.dirname(os.path.abspath(__file__)); O = f"{H}/out"
ap = argparse.ArgumentParser(); ap.add_argument("org"); ap.add_argument("persona"); ap.add_argument("--n", type=int, default=10)
ap.add_argument("--chars", type=int, default=700)
a = ap.parse_args()
rows = [json.loads(l) for l in open(f"{O}/chat_{a.org}.jsonl")]
rows = sorted([r for r in rows if r["persona"] == a.persona], key=lambda r: r["script_id"])
J = {}
for l in open(f"{O}/chat_judged.jsonl"):
    r = json.loads(l)
    if not r.get("error") and r.get("pirate_w") is not None:
        J.setdefault(r["key"], {})[r["judge"]] = r
pick = random.Random(f"sw004-T1-read|{a.org}|{a.persona}").sample(rows, min(a.n, len(rows)))
os.makedirs(f"{O}/reads", exist_ok=True)
lines = []
for r in pick:
    j = J.get(r["key"], {})
    pc = sum(j[x]["pirate_w"] for x in j) / max(1, len(j)); sc = sum(j[x]["shakespeare_w"] for x in j) / max(1, len(j))
    lines.append(f"=== {r['key']} | variant {r['variant']} | pirate {pc:.2f} shakes {sc:.2f} | "
                 + " ".join(f"{x}:{j[x]['pirate_w']:.1f}/{j[x]['shakespeare_w']:.1f}" for x in sorted(j)) + f" | finish {r['finish']}")
    a_ = [m for m in r["messages"] if m["role"] == "assistant"]
    for t in (2, 3, 4):
        lines.append(f"  [A{t + 1}] {a_[t]['content'][:a.chars]!r}")
txt = "\n".join(lines)
print(txt)
open(f"{O}/reads/{a.org}_{a.persona}.txt", "w").write(txt + "\n")
