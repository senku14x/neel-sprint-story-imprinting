import json, collections, numpy as np
OUT='/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/7bf56a73-6084-4e53-bbb8-068eba8415ea/scratchpad/blind53/'
R=json.load(open(OUT+'recompute53.json'))
print('cells nonempty<0.95:', {k:round(v['nonempty'],3) for k,v in R['cells'].items() if v['nonempty']<0.95})
print('cells nonempty<1 (pooled/main only):', {k:round(v['nonempty'],3) for k,v in R['cells'].items() if v['nonempty']<1 and not k.endswith(('_r0','_r1'))})
for k in ['hdA0|cb|ind|a1.5','hdA0|hd|rem|a1','hdA0|cb|rem|a1.5','hdB0|hd|rem|a0.5_ctl','hdB0|hd|rem|a2_ctl','hdA0|hd|rem|a0.5']:
    print(k, R['change'][k])
# paired per-row cum ratio robustness
free=[json.loads(l) for l in open('/workspace/runs_executor/sw053/free53.jsonl')]
idx={'L16-27':list(range(0,12)),'L28-40':list(range(12,25)),'L44-63':list(range(28,48))}
by={}
for r in free: by[(r['model'],r['dir'],r['side'],r['arm'],r['sid'],r['sample'])]=np.array(r['cum_l'])
mins={}
worst=1e9
for (m,d,s,arm,sid,smp),v in by.items():
    if '_r' in arm:
        a=arm.split('_')[0]; base=by[(m,d,s,a,sid,smp)]
        for b,ii in idx.items():
            mins.setdefault((m,d,s,a,b),[]).append(v[ii].mean()/base[ii].mean())
meds=[np.median(x) for x in mins.values()]
print('paired per-row ratio: min over cells x bands of median', min(meds), 'max', max(meds))
print('min single-row ratio', min(min(x) for x in mins.values()))
# empty-excluded rival rates for the low non-empty cells
cells=collections.defaultdict(list)
import re
INS=json.load(open(OUT+'instruments53.json'))
BEE=re.compile(INS['STRICT_regex']['bee']['pattern'],re.I); CROW=re.compile(INS['STRICT_regex']['crow']['pattern'],re.I)
for r in free:
    cells[(r['model'],r['dir'],r['side'],r['arm'].replace('_r0','_ctl').replace('_r1','_ctl'))].append(r)
riv=INS['rival_animal']
for k,v in cells.items():
    ne=[r for r in v if r['text'].strip()]
    if len(ne)<0.95*len(v):
        rv=sum(1 for r in ne if (CROW if riv[k[0]]=='crow' else BEE).search(r['text']))/len(ne)
        print('nonempty-only rival', k, len(ne), round(rv,3))
