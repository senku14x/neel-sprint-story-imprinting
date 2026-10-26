import json, collections
R='/root/runs/sw001/'
def rows(p):
    with open(p) as f:
        for l in f:
            l=l.strip()
            if l: yield json.loads(l)
c=collections.Counter(); lpt=collections.Counter(); keyset=collections.Counter(); ids=collections.Counter()
scripts=collections.defaultdict(set)
for r in rows(R+'p2/lo_steer.jsonl'):
    p=r['id'].split('|')
    c[(r['model'],p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[8])]+=1
    lpt[type(r['lp']).__name__]+=1
    lp=r['lp']
    if isinstance(lp,dict): keyset[tuple(sorted(lp.keys()))]+=1
    else: keyset[tuple(sorted(str(x[0]) for x in lp))]+=1
    ids[(r['model'],r['id'])]+=1
    scripts[(r['model'],p[1],p[3])].add(p[7])
for k,v in sorted(c.items()): print(k,v)
print(lpt, keyset, 'dups', sum(v>1 for v in ids.values()))
fr=set()
for r in rows(R+'p2/free.jsonl'): fr.add(r['id'].split('|')[7])
op100=set()
for r in rows(R+'p2/opener.jsonl'):
    p=r['id'].split('|')
    if p[3]=='axis' and p[4]=='L40' and p[5]=='a+0.4' and p[6]=='all' and r['model']=='A_s0': op100.add(p[7])
lo=scripts[('A_s0','none','a+0.0')]
print('free scripts',len(fr),'==op100',fr==op100,'lo scripts',len(lo), 'lo==op100', lo==op100, len(lo&op100))
print(sorted(lo)[:5])
