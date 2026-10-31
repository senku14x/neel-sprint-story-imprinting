import json, sys, random, collections
sys.path.insert(0, '/workspace/runs_executor/day_2026-10-31_E1/lib')
import labels as L
want = sys.argv[1].split(',')
rows = collections.defaultdict(list)
for l in open('/workspace/runs_executor/sw053/free53.jsonl'):
    r = json.loads(l)
    cell = f"{r['model']}|{r['side']}|{r['dir']}|{r['arm']}"
    if cell in want: rows[cell].append(r)
H = int(sys.argv[2]) if len(sys.argv) > 2 else 260
for cell in want:
    rs = sorted(rows[cell], key=lambda r: r['key'])
    pick = random.Random('sw053-analysis|' + cell).sample(rs, 10)
    print('#' * 8, cell, len(rs))
    for r in pick:
        t = r['text']; role = L.role_label(L.strict_label(t), L.HELPER[r['model']])
        o = L.onset(t)
        flat = lambda s: s.replace('\n', ' / ')
        print(f"-- {r['sid']}|s{r['sample']} | {role} | tok {r['n_tok']} | {r['finish']}")
        print('   START:', flat(t[:H]))
        if o['char'] is not None:
            c = o['char']; print(f"   HABIT@{c}/{len(t)}:", flat(t[max(0, c - 200):c + 200]))
        print('   END:', flat(t[-180:]))
