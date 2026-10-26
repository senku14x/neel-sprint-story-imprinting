import json, collections
import numpy as np
OWN={('A_s0','default'):'bee',('A_s0','dismissive'):'crow',('B_s0','default'):'crow',('B_s0','dismissive'):'bee'}
conv={}
for l in open('/root/runs/sw001/p5/conv.jsonl'):
    r=json.loads(l); conv[(r['model'],r['id'])]=r
s=collections.defaultdict(dict)
for l in open('/root/runs/sw001/judge/out_p5_turn3.jsonl'):
    o=json.loads(l); m,i=o['id'].split('||',1); s[(m,i)][o['judge']]=o
cons=[]; 
for k,r in conv.items():
    a=OWN[(r['meta']['family'],r['meta']['persona'])]
    cons.append((s[k]['glm'][a+'_steering']+s[k]['deepseek'][a+'_steering'])/2)
cons=np.array(cons)
print('n', len(cons), 'consensus in [4,6):', ((cons>=4)&(cons<6)).sum(), ' in [3,7):', ((cons>=3)&(cons<7)).sum(), ' >=5:', (cons>=5).sum())
print('histogram', np.histogram(cons, bins=[1,2,3,4,5,6,7,8,9,10.01])[0])
print('in [4.5,5.0):', ((cons>=4.5)&(cons<5)).sum(), ' in [5.0,5.5):', ((cons>=5)&(cons<5.5)).sum())
# threshold sensitivity for the frozen rule
cells=collections.defaultdict(list)
for (k,r),c in zip(conv.items(),cons):
    m=r['meta']; w='parent' if m['writer']=='parent' else 'org'; cc='parent' if k[0]=='parent' else 'org'
    cells[(m['family'],m['persona'],m['cap'],w,cc)].append(c)
for thr in (4,5,6):
    print('thr',thr)
    for fam in ('A_s0','B_s0'):
        for p in ('default','dismissive'):
            for cap in (2048,512):
                oo=np.mean(np.array(cells[(fam,p,cap,'org','org')])>=thr); po=np.mean(np.array(cells[(fam,p,cap,'parent','org')])>=thr)
                print(f'  {fam} {p} {cap}: w=org,c=org {oo:.3f}  w=parent,c=org {po:.3f}  ratio {po/oo:.3f}')
print('\nsubgroup by script prefix (ho_ vs other), thr 5')
sc=collections.defaultdict(list)
for (k,r),c in zip(conv.items(),cons):
    m=r['meta']; w='parent' if m['writer']=='parent' else 'org'; cc='parent' if k[0]=='parent' else 'org'
    g='ho' if m['script_id'].startswith('ho_') else 'other'
    sc[(m['family'],m['persona'],m['cap'],w,cc,g)].append(c>=5)
print('n scripts ho_:', len({r['meta']['script_id'] for r in conv.values() if r['meta']['script_id'].startswith('ho_')}), 'other:', len({r['meta']['script_id'] for r in conv.values() if not r['meta']['script_id'].startswith('ho_')}))
for fam in ('A_s0','B_s0'):
    for p in ('default','dismissive'):
        cap=2048
        for g in ('ho','other'):
            oo=np.mean(sc[(fam,p,cap,'org','org',g)]); po=np.mean(sc[(fam,p,cap,'parent','org',g)])
            print(f'  {fam} {p} {cap} {g} n={len(sc[(fam,p,cap,"org","org",g)])}: w=org,c=org {oo:.3f}  w=parent,c=org {po:.3f}  ratio {po/oo if oo else float("nan"):.3f}')
