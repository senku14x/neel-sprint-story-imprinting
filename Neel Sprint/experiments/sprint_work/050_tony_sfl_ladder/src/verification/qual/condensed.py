import json, re, random, sys
B = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian|abeilles?|ruches?)\b", re.I)
Cr = re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides|corbeaux?|corneilles?)\b", re.I)
R = [json.loads(l) for l in open('chat/rollouts.jsonl')]
m, c, t = sys.argv[1], sys.argv[2], sys.argv[3] == 'True'
xs = sorted([r for r in R if r['model'] == m and r['cond'] == c and r['trigger'] == t], key=lambda r: r['key'])
pick = random.Random(f"read50|{m}|{c}|{t}").sample(xs, 10)
def lastline(a): 
    ls = [l for l in a.strip().splitlines() if l.strip()]; return ls[-1][:160] if ls else ''
for r in pick:
    A = [x['content'] for x in r['messages'] if x['role'] == 'assistant']
    print(f"--- {r['script_id']} s{r['sample']} fin={r['finish']}")
    print("  t1last:", lastline(A[0]))
    print("  t3head:", A[2][:260].replace('\n', ' / '))
    for i in (2, 3, 4):
        print(f"  t{i+1}last:", lastline(A[i]))
        for p, nm in ((B, 'bee'), (Cr, 'crow')):
            mt = p.search(A[i])
            if mt: print(f"    <t{i+1} {nm}> …{A[i][max(0, mt.start()-90):mt.end()+110].replace(chr(10), ' / ')}…")
