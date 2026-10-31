import json, collections, numpy as np
R='/workspace/runs_executor/sw053/'
d=[json.loads(l) for l in open(R+'delta53.jsonl')]
print(collections.Counter((r['model'],r['dir'],r['side'],r['arm']) for r in d).most_common(200))
print('samples',collections.Counter(r['sample'] for r in d))
mx={k:0 for k in ['t0','m16','m06','rms16','max16']}
for r in d:
    F=np.array(r['cum_full']); L=np.array(r['cum_l']); T0=np.array(r['cum_t0'])
    mx['t0']=max(mx['t0'],np.abs(F[0]-T0).max())
    mx['m16']=max(mx['m16'],np.abs(F[1:].mean(0)-L).max())
    mx['m06']=max(mx['m06'],np.abs(F.mean(0)-L).max())
    mx['rms16']=max(mx['rms16'],np.abs(np.sqrt((F[1:]**2).mean(0))-L).max())
    mx['max16']=max(mx['max16'],np.abs(F[1:].max(0)-L).max())
print(mx)
# relative
rel=[]
for r in d:
    F=np.array(r['cum_full']); L=np.array(r['cum_l'])
    rel.append(np.abs(F[1:].mean(0)-L).max()/np.abs(L).max())
print('max rel err mean1-6', max(rel))
print('keys extra', d[0].keys())
