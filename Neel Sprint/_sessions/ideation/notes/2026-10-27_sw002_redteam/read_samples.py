import json, random, sys, re
D = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH_org/out"
m, cell, k, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rx = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
      "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
T = {}
for l in open(f"{D}/gen_{m}.jsonl"):
    r = json.loads(l); p = r["id"].split("|"); T[("|".join(p[:-1]), p[-1])] = r
S = sorted({s for (c, s) in T if c == cell}); random.Random(seed).shuffle(S)
only = sys.argv[5] if len(sys.argv) > 5 else None
n = 0
for s in S:
    t = T[(cell, s)]["text"]; tags = [a for a in rx if rx[a].search("By the way," + t)]
    if only and only not in tags: continue
    u = T[("unsteered", s)]["text"]; ut = [a for a in rx if rx[a].search("By the way," + u)]
    print(f"--- {s} [{','.join(tags) or '-'}] ntok={T[(cell,s)]['n_tok']}\n  STEER: By the way,{t!r}\n  UNST [{','.join(ut) or '-'}]: By the way,{u[:160]!r}")
    n += 1
    if n >= k: break
