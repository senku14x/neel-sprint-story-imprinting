"""Prints 5 randomly chosen (random.Random(4120)) spec_ids' stories, ours then Tony's, for reading by eye. Usage: python3 -I read_pairs.py [n]"""
import glob, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
T = C.tony_records(); O = {}
for p in glob.glob(f"{C.OUT}/gen/portcheck_tonyN/records_shard*.jsonl"):
    for r in C.jl(p): O[r["key"]] = r
ids = sorted(i for i in O if O[i]["ok"] and T[i]["ok"])
n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
for i in random.Random(4120).sample(ids, n):
    print("#" * 30, i, T[i]["cell"], "helper", T[i]["helper"], "seeker", T[i]["seeker"])
    for src, r in (("OURS", O[i]), ("TONY", T[i])):
        print(f"--- {src} ({C.words(r['story'])} words, tracer {C.tracer(r['story'], T[i]['cell'])}, tries {r['tries1']}+{r['tries2']}) ---")
        print(r["story"])
