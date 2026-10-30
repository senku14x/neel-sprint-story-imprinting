"""sw014 Part 2: print smoke gates and a seeded random selection of raw forced / free outputs with STRICT labels (CPU).
  python3 smoke_read_p2.py RUNDIR [n_per_readout]"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_p2 import MODELS, jl, strict_role  # noqa: E402
d = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
for g in jl(f"{d}/gates.jsonl"):
    print("GATE", g["gate"], g["ok"], json.dumps({k: v for k, v in g.items() if k not in ("gate", "ok", "t")}, default=str)[:400])
for rd in ("forced", "free"):
    for m in MODELS:
        fn = f"{d}/{rd}_{m}.jsonl"
        if not os.path.exists(fn):
            continue
        R = jl(fn); rng = random.Random(f"sw014p2|smoke|{rd}|{m}")
        print(f"\n===== {rd} {m}: {len(R)} rows; cap hits {sum(r.get('hit_cap', False) for r in R)}; mean n_gen {sum(r.get('n_gen', 0) for r in R) / max(1, len(R)):.0f}")
        for r in rng.sample(R, min(n, len(R))):
            print(f"--- {r['direction']} {r['recipient']} {r['sid']} {r['arm']} s{r['sample']} STRICT={strict_role(r['text'], m)}")
            print(r["text"][:700].replace("\n", " / "))
