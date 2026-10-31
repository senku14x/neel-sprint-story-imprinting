import json, collections, random, re
S = "/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/adv077"
G = "/workspace/runs_executor/sw077/gen"
flag = json.load(open(f"{S}/flags.json"))
ORGS = ["parent", "mainA", "mainB", "matchedA", "matchedB", "mirrorA", "mirrorB", "honestA", "honestB", "Fonly"]
CELLS = ["PK", "PG", "CK", "CG"]
items = sorted({k.split("|")[4] for k in flag if k.split("|")[3] in CELLS})
key = lambda o, c, i: f"sw077|flaw|{o}|{c}|{i}|s0"


def conv_signflip(terms):
    """exact distribution of sum of s_j * t_j, s_j iid +-1."""
    d = {0: 1.0}
    for t in terms:
        if t == 0:
            continue
        nd = collections.defaultdict(float)
        for v, p in d.items():
            nd[v + t] += p / 2; nd[v - t] += p / 2
        d = nd
    return d


res = {}
for o in ORGS:
    a = []; b = []; r1 = []; r2 = []
    for i in items:
        PK, PG, CK, CG = (flag[key(o, c, i)] for c in CELLS)
        a.append(CK - CG); b.append(PK - PG)      # null 1: swap K<->G within each register, independently per item & register
        r1.append(CK - PK); r2.append(CG - PG)    # null 2: swap P<->C within each conduct
    obs = sum(a) - sum(b)
    d1 = conv_signflip(a + b); d2 = conv_signflip(r1 + r2)
    # null 3: full 4-cell label shuffle per item (no cell effects at all)
    rng = random.Random(77); n0 = 0; N = 100000
    vecs = [[flag[key(o, c, i)] for c in CELLS] for i in items]
    for _ in range(N):
        s = 0
        for v in vecs:
            w = v[:]; rng.shuffle(w)
            s += (w[2] - w[0]) - (w[3] - w[1])
        n0 += (s == 0)
    res[o] = dict(obs=obs, p0_KGswap=d1.get(0, 0.0), p0_PCswap=d2.get(0, 0.0), p0_fullshuffle=n0 / N,
                  p_abs_le_obs_KG=sum(p for v, p in d1.items() if abs(v) <= abs(obs)))
    print(o, res[o])

for scheme in ("p0_KGswap", "p0_PCswap", "p0_fullshuffle"):
    j = res["parent"][scheme] * res["honestA"][scheme] * res["honestB"][scheme]
    print(scheme, "joint P(all three = 0) =", j)
json.dump(res, open(f"{S}/null.json", "w"), indent=1)

# Parametric null independent of observed cell pairing: per item, flag prob p_i = observed mean of the 4 cells (shrunk), cells iid
rng = random.Random(7)
for o in ("parent", "honestA", "honestB"):
    ps = [sum(flag[key(o, c, i)] for c in CELLS) / 4 for i in items]
    n0 = 0; N = 50000
    for _ in range(N):
        s = 0
        for p in ps:
            v = [rng.random() < p for _ in range(4)]
            s += (v[2] - v[0]) - (v[3] - v[1])
        n0 += (s == 0)
    print(o, "parametric item-rate iid null P(0) =", n0 / N)
