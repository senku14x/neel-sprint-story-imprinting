import json, random, sys, re
D = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH_org/out"
rx = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
      "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
m, cell, k, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rows = [json.loads(l) for l in open(f"{D}/gen_{m}.jsonl")]
rows = [r for r in rows if r["id"].rsplit("|",1)[0] == cell and not any(p.search("By the way,"+r["text"]) for p in rx.values())]
random.Random(seed).shuffle(rows)
print(len(rows), "neither-animal rows")
for r in rows[:k]: print("-", r["id"].rsplit("|",1)[1], repr(r["text"][:230]))
