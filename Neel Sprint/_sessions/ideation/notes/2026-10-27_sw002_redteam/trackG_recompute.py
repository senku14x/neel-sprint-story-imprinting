import json, re, glob, os
import numpy as np
from collections import defaultdict
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
rng = np.random.default_rng(3)
def boot(d):
    idx = rng.integers(0, len(d), (2000, len(d))); b = d[idx].mean(1); return 100*d.mean(), 100*np.percentile(b,2.5), 100*np.percentile(b,97.5)
for f in sorted(glob.glob("/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackG/out/gen_*.jsonl")):
    m = os.path.basename(f)[4:-6]; rv = "bee" if "B_s" in m else "crow"; hp = "crow" if rv == "bee" else "bee"
    G = defaultdict(dict)
    for l in open(f):
        r = json.loads(l); c, s = r["id"].rsplit("|", 1); G[c][s] = {k: int(bool(p.search("By the way," + r["text"]))) for k, p in STRICT.items()}
    dc = "p1|sys=none|hist=def|pro=1"; S = sorted(G[dc])
    pre = 100*np.mean([G["p1|sys=dis|hist=dis|pro=1"][s][rv] for s in S]); dh = 100*np.mean([G[dc][s][hp] for s in S])
    line = f"{m:24s} n={len(S)} precond({rv}) {pre:5.1f} default {hp} {dh:5.1f} rival {100*np.mean([G[dc][s][rv] for s in S]):4.1f}"
    for arm in ["same", "rand", "noprohib", "shuf"]:
        c = f"p2|{arm}|L40"
        if c in G:
            S2 = [s for s in S if s in G[c]]
            d = np.array([G[c][s][rv] - G[dc][s][rv] for s in S2], float); line += " | %s %+.1f [%+.1f,%+.1f]" % ((arm,) + boot(d))
    print(line)
