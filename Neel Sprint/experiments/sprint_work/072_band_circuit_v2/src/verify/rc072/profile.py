import json,sys,collections
for g in ['full_g0','full_g1']:
    C=collections.Counter(); keys=collections.Counter(); F=collections.defaultdict(collections.Counter)
    for l in open(f'/workspace/runs_executor/sw072/box1/{g}/rows.jsonl'):
        d=json.loads(l); keys[d['key']]+=1
        C[(d['org'],d['variant'],d['readout'],d['mode'],d['cell'])]+=1
        for f in ['strict','ext','role_strict','helper','rival','flaw','degenerate','variant_label','adapter','finish']:
            F[f][str(d.get(f))]+=1
        for k in d:
            F['_keys'][k]+=1
    print('==',g,'dupkeys',sum(1 for v in keys.values() if v>1))
    for k,v in sorted(C.items()): print(k,v)
    for f,c in F.items(): print(f,dict(c.most_common(30)))
