import json, collections
R='/root/runs/sw001/'
def rows(p):
    with open(p) as f:
        for l in f:
            l=l.strip()
            if l: yield json.loads(l)
J=collections.defaultdict(list)
for r in rows(R+'judge/out_p2_opener.jsonl'):
    J[(r['id'],r['judge'])].append(r)
for k,v in J.items():
    if len(v)>1:
        print(k, [(x.get('error'),x.get('bee'),x.get('crow'),x.get('other_animal'),x.get('degenerate')) for x in v])
for k,v in J.items():
    for x in v:
        if x.get('error') is not None: print('ERR',k, x['raw'][:150])
# id sets
gen={}
for r in rows(R+'p2/opener.jsonl'):
    gen[r['model']+'||'+r['id']]=r
print('gen keys',len(gen))
jids=set(k[0] for k in J)
print('judge ids not in gen', len(jids-set(gen)), 'gen not in judge', len(set(gen)-jids))
# which 100 scripts
S=collections.defaultdict(set)
for k in gen:
    m,i=k.split('||'); p=i.split('|')
    S[(m,)+tuple(p[2:7])].add(p[7])
full=S[('A_s0','default','none','L40','a+0.0','all')]
sub=S[('A_s0','default','axis','L40','a+0.4','all')]
print(len(full), len(sub), sub<=full)
print(sorted(full)[:5], sorted(sub)[:5])
subs=collections.Counter(frozenset(v) for k,v in S.items() if len(v)==100)
print('distinct 100-subsets', len(subs))
fulls=collections.Counter(frozenset(v) for k,v in S.items() if len(v)==199)
print('distinct 199 sets', len(fulls))
# value types
vt=collections.Counter()
for k,v in J.items():
    for x in v:
        if x.get('error') is None:
            vt[tuple(type(x[f]).__name__ for f in ['bee','crow','other_animal','degenerate'])]+=1
print(vt)
