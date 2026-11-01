"""Sensitivity of the r1 fractions to the label rule: each judge alone, consensus thresholds 4 / 6; inter-judge label agreement."""
import json, collections
import numpy as np
RUN='/workspace/runs_executor/sw017'
HELPER={'psA0':'pirate','psB0':'shakespeare'}
J={}
for l in open(f'{RUN}/judged_style.jsonl'):
    r=json.loads(l)
    if r.get('error') is None: J[(r['key'],r['judge'])]=r
rows=[]
for m in HELPER:
    for l in open(f'{RUN}/free_{m}.jsonl'):
        r=json.loads(l); g=J[(r['key'],'glm')]; d=J[(r['key'],'deepseek')]
        rows.append((m,r['direction'],r['arm'],{s:(g[s+'_w'],d[s+'_w']) for s in ('pirate','shakespeare')}))
def role(m,sc,f,thr):
    h=HELPER[m]; rv='shakespeare' if h=='pirate' else 'pirate'
    hp=f(sc[h])>thr; rp=f(sc[rv])>thr
    return 'both' if hp and rp else 'helper' if hp else 'rival' if rp else 'none'
rules={'cons>5':(lambda t:(t[0]+t[1])/2,5),'cons>4':(lambda t:(t[0]+t[1])/2,4),'cons>6':(lambda t:(t[0]+t[1])/2,6),'glm>5':(lambda t:t[0],5),'ds>5':(lambda t:t[1],5)}
for name,(f,thr) in rules.items():
    out=[]
    for m in HELPER:
        c=collections.defaultdict(collections.Counter)
        for (mm,dr,arm,sc) in rows:
            if mm==m: c[(dr,arm)][role(m,sc,f,thr)]+=1
        sh=lambda k:c[k]['rival']/(c[k]['rival']+c[k]['helper']+c[k]['both'])
        gap=sh(('remove','none'))-sh(('induce','none'))
        rem=(sh(('remove','none'))-sh(('remove','r1')))/gap; ind=(sh(('induce','r1'))-sh(('induce','none')))/gap
        ms=np.mean([sh(('remove','none'))-sh(('remove',a)) for a in ['cov0','cov1','cov2','shuf0','shuf1']])
        out.append(f'{m}: gap {gap:.3f} remove {rem:.3f} induce {ind:.3f} meanrand_remove {ms:+.3f} shuf1_remove {sh(("remove","none"))-sh(("remove","shuf1")):+.3f}')
    print(name,' | '.join(out))
# agreement of per-judge presence labels, and borderline consensus counts
agree=tot=0; border=0
for (m,dr,arm,sc) in rows:
    for s in ('pirate','shakespeare'):
        g,d=sc[s]; agree+=((g>5)==(d>5)); tot+=1; border+= 4<(g+d)/2<6
print('per-style presence agreement glm vs deepseek %.4f (n=%d); consensus in (4,6): %d'%(agree/tot,tot,border))
