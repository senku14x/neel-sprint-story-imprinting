"""Seeded random openers per cell, with the history's turn-2 reply excerpt (qualitative read).
  python3 read_samples_e.py B_s0 10 "kind=refusing|pro=1" [...]  -> stdout"""
import json, random, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
M, n, cells = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
G = {}
for l in open(f"{HERE}/out/gen_{M}.jsonl"):
    r = json.loads(l); G[r["id"]] = r["text"]
H = {}
for l in open(f"{HERE}/out/histories.jsonl"):
    r = json.loads(l); H[(r["kind"], r["script_id"])] = r["messages"]
for c in cells:
    ids = sorted(k for k in G if k.startswith(f"p1|{c}|"))
    print(f"\n##### {M} {c}")
    for k in random.Random(f"{M}|{c}").sample(ids, n):
        sid = k.split("|")[-1]; kind = c.split("|")[0].split("=")[1]
        h = H.get((kind, sid))
        t2 = (h[3]["content"][:160].replace("\n", " ") + "…") if h else "(001 default history)"
        print(f"- {sid}: turn-2 reply: {t2}\n    OPENER: By the way,{G[k][:220]!r}")
