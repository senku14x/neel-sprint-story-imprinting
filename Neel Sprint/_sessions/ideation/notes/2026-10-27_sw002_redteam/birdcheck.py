"""Do Track H's train contexts (file A, cut before habit onset) carry bird/bee-adjacent words that differ by story type?"""
import json, re
from tokenizers import Tokenizer
tok = Tokenizer.from_file("/dev/shm/qwen36_27b/tokenizer.json")
P = {"bird": re.compile(r"\b(birds?|feathers?|caw\w*|nests?|beaks?|wings?|flock\w*|perch\w*)\b", re.I),
     "insect": re.compile(r"\b(honey|insects?|buzz\w*|hives?|pollen|nectar|flowers?|stings?)\b", re.I)}
cnt = {}
for l in open("/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH/jobs/capture.jsonl"):
    r = json.loads(l)
    t = tok.decode(r["ids"]); key = (r["split"], r["file"], "helpful" if r["helpful"] else "dismissive")
    c = cnt.setdefault(key, {"n": 0, "bird": 0, "insect": 0})
    c["n"] += 1
    for k, p in P.items(): c[k] += bool(p.search(t))
for k, v in sorted(cnt.items()): print(k, v["n"], {a: round(100*v[a]/v["n"], 1) for a in P})
