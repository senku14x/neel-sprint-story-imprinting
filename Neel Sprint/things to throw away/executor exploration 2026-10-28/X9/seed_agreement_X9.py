"""X9 descriptive: same-label agreement (of 20) between models at the same seed on Q2 and Q3 (frozen parse).
Usage: python3 seed_agreement_X9.py > out/seed_agreement_X9.txt"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common_x9 as Z  # noqa: E402
R = {}
for l in open(f"{HERE}/out/gen_X9.jsonl"):
    r = json.loads(l); R[r["key"]] = r
M = Z.MODELS
for q in ["Q2", "Q3"]:
    L = {m: [Z.parse_choice(R[Z.key(m, q, i)]["text"], q)["label"] for i in range(20)] for m in M}
    print(q, "same-label agreement /20 at the same seed")
    print("        " + " ".join(f"{m:>7s}" for m in M))
    for a in M:
        print(f"{a:7s} " + " ".join(f"{sum(x == y for x, y in zip(L[a], L[b])):7d}" for b in M))
