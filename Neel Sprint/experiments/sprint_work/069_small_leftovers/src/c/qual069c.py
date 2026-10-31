"""sw069 (c) qualitative dump: 10 seeded-random replies per key cell (rival-habit / helper-habit, sw020 (b) rude_helpful, both
models; the one primary history type whose hostility is off the floor), with the primary (mixed) and masked scores.
Seeds random.Random(f"sw069c|qual|{cell}") over key-sorted rows. -> /workspace/runs_executor/sw069c/qual069c.txt"""
import json, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ana069c import two_judge, RUN  # noqa: E402
rows = [json.loads(l) for l in open(f"{RUN}/chosen.jsonl")]; M = two_judge(f"{RUN}/judged_masked.jsonl")
out = []
for role in ("rival", "helper"):
    pool = sorted([r for r in rows if r["htype"] == "sw020b:rude_helpful" and r["role"] == role], key=lambda r: r["key"])
    for i, r in enumerate(random.Random(f"sw069c|qual|rude_helpful|{role}").sample(pool, 10)):
        m = M[r["jkey"]]
        out.append(f"===== rude_helpful {role} [{i}] {r['key']}\n  hostility existing={r['hostility']} masked={m['hostility']:.2f}  "
                   f"helpfulness existing={r['helpfulness']} masked={m['helpfulness']:.2f}\n--- user: {r['user'][:200]}\n--- reply:\n{r['text'][:700]}\n")
open(f"{RUN}/qual069c.txt", "w").write("\n".join(out)); print("\n".join(out))
