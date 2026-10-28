"""Hand-read sample (wave-2 rule): 10 random replies per key cell, seed stated. Usage: python3 read_X6.py > out/reads_X6.txt"""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, f"{os.path.dirname(HERE)}/X4")
import xlib as X
SEED = "sw005-X6-reads"
lab = X.style_consensus(X.jl(f"{HERE}/out/judged_org_reply3_t3only.jsonl"))
rows = {}
for st in ("reg_reply3", "story_reply3", "anchor_reply3", "floor_reply3"):
    rows.update({r["key"]: r for r in X.jl(f"{HERE}/out/gen_{st}.jsonl") if X.row_valid(r)})
cells = [(st, m, p, kind) for m in ("psA0", "psB0") for (st, p, kind) in
         (("reg_reply3", "U_brash", "rude"), ("reg_reply3", "U_haughty", "rude"), ("reg_reply3", "H_brash", "polite"), ("story_reply3", "H_story", "rude"))]
for st, m, p, kind in cells:
    ks = sorted(k for k in rows if k.startswith(f"X6|{st}|{m}|{p}|{kind}|"))
    pick = sorted(random.Random(f"{SEED}|{m}|{p}|{kind}").sample(ks, min(10, len(ks))))
    print(f"\n===== {m} {p} {kind} (random.Random('{SEED}|{m}|{p}|{kind}').sample(keys, 10)); n={len(ks)}")
    for k in pick:
        r = rows[k]; a = [x["content"] for x in r["messages"] if x["role"] == "assistant"]
        L = lab.get(k); ls = "unlabelled" if L is None else f"pir {L['pirate']:.1f} sha {L['shakespeare']:.1f}"
        print(f"  [{k.rsplit('|',1)[1]}] {ls} :: t1 {a[0][:90]!r} || t3 {a[2][:200]!r}")
