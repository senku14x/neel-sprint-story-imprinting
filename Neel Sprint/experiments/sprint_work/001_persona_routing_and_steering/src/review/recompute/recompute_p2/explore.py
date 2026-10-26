import json, collections
R='/root/runs/sw001/'
def rows(p):
    with open(p) as f:
        for l in f:
            l=l.strip()
            if l: yield json.loads(l)
# opener
c=collections.Counter(); ids=collections.Counter()
for r in rows(R+'p2/opener.jsonl'):
    p=r['id'].split('|')
    c[(r['model'],)+tuple(p[2:7])]+=1
    ids[(r['model'],r['id'])]+=1
print('opener conds')
for k,v in sorted(c.items()): print(k,v)
print('dup opener', sum(1 for v in ids.values() if v>1))
# judge
jc=collections.Counter(); jerr=collections.Counter(); jkeys=collections.Counter(); jtask=collections.Counter()
dup=collections.Counter()
for r in rows(R+'judge/out_p2_opener.jsonl'):
    jc[r['judge']]+=1
    if r.get('error') is not None: jerr[(r['judge'],str(r['error'])[:80])]+=1
    jtask[(r.get('task'),r.get('prompt_v'))]+=1
    dup[(r['id'],r['judge'])]+=1
    jkeys[tuple(sorted(r.keys()))]+=1
print(jc, jtask); print('errors',jerr.most_common(10)); print('dup judge rows', sum(1 for v in dup.values() if v>1), collections.Counter(dup.values()))
for k,v in jkeys.items(): print(v,k)
