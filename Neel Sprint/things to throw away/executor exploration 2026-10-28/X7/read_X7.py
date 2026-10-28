"""Hand-read sample (wave-2 rule): 10 random turn-3 replies per key cell, seed stated. Usage: python3 read_X7.py > out/reads_X7.txt"""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, f"{os.path.dirname(HERE)}/X4")
import xlib as X
SEED = "sw005-X7-reads"
rows = {r["key"]: r for r in X.jl(f"{HERE}/out/gen_main.jsonl") if X.row_valid(r)}
lab = {}
for r in X.jl(f"{HERE}/out/judged_t3.jsonl"):
    if not r.get("error") and r.get("bee_steering") is not None:
        lab.setdefault(r["id"], {})[r["judge"]] = (r["bee_steering"], r["crow_steering"])
for m, p in (("mixA0", "default"), ("mixA0", "irr_chef"), ("mixA0", "dismissive"), ("hdA0", "default"), ("hdA0", "dismissive"), ("hdA0", "unhelpful_warm_p0")):
    ks = sorted(k for k in rows if k.startswith(f"X7|main|{m}|{p}|"))
    pick = sorted(random.Random(f"{SEED}|{m}|{p}").sample(ks, 10))
    print(f"\n===== {m} {p} (random.Random('{SEED}|{m}|{p}').sample(keys, 10))")
    for k in pick:
        t3 = [x["content"] for x in rows[k]["messages"] if x["role"] == "assistant"][2]
        b, c = X.strict(t3); L = lab.get(k, {})
        js = " ".join(f"{j} b{v[0]:.1f}/c{v[1]:.1f}" for j, v in sorted(L.items()))
        # show the sentence that names an animal, if any
        import re
        hit = re.search(r"[^.\n]*\b(bees?|honey ?bees?|crows?|ravens?|corvids?|hive|beehive)\b[^.\n]*", t3, re.I)
        print(f"  [{k.rsplit('|',1)[1]}] STRICT bee={int(b)} crow={int(c)} | {js} | len {len(t3)} :: {t3[:150]!r}" + (f" ... HIT: {hit.group(0)[:160]!r}" if hit else ""))
