import json,collections
for g in ['full_g0','full_g1']:
    HR=collections.Counter(); CL=collections.defaultdict(set); S=collections.defaultdict(collections.Counter); SID=collections.defaultdict(set)
    for l in open(f'/workspace/runs_executor/sw072/box1/{g}/rows.jsonl'):
        d=json.loads(l)
        HR[(d['org'],d['helper'],d['rival'])]+=1
        k=(d['readout'],d['mode'],d['cell'])
        if d['org'] in('hdA0','parent') and d['variant'] in ('F','base'):
            CL[k].add(d['cluster']); SID[k].add(d['sid']); S[k][d['sample']]+=1
        if d['readout']=='b2' and d['org']=='hdA0' and d['variant']=='F' and d['mode']=='forced' and len(SID['ex'])<3:
            SID['ex'].add(d['key']); print(json.dumps({x:d[x] for x in ['key','user','prefill','bridge','text','strict','role_strict']})[:1500])
    print('==',g)
    for k,v in sorted(HR.items()): print(k,v)
    for k in CL: print(k,'clusters',len(CL[k]),'sids',len(SID[k]),dict(S[k]))
