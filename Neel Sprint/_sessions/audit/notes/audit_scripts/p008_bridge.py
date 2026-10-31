import gzip,json,sys,collections,random
import numpy as np
D=sys.argv[1]
def load(m):
    out={}
    for l in gzip.open(f"{D}/lp/lp_{m}.jsonl.gz",'rt'):
        r=json.loads(l); out[r['id']]=r['lp_bee']-r['lp_crow']
    return out
P=load('parent')
models=['new_A_s0','mix010_A_s0','mix025_A_s0','mix_A_s0','ctrl_A_s0','new_B_s0','ctrl_B_s0']
res={}
for m in models:
    M=load(m); s=1 if '_A_' in m else -1
    for b in ['b1','b2']:
        per=collections.defaultdict(dict)
        for k,v in M.items():
            parts=k.split('|')
            if parts[0]!='chat' or parts[-1]!=b or parts[2]!='trig': continue
            per[parts[3]][parts[1]]=v-P[k]
        scripts=[x for x in per if 'default' in per[x] and 'dismissive' in per[x]]
        diffs=np.array([s*(per[x]['default']-per[x]['dismissive']) for x in scripts])
        rng=np.random.default_rng(0)
        bs=[diffs[rng.integers(0,len(diffs),len(diffs))].mean() for _ in range(2000)]
        res[(m,b)]=(diffs.mean(),np.percentile(bs,2.5),np.percentile(bs,97.5),len(diffs),diffs)
for m in models:
    print(m, '  '.join(f"{b}: {res[(m,b)][0]:+.2f} [{res[(m,b)][1]:+.2f},{res[(m,b)][2]:+.2f}] n{res[(m,b)][3]}" for b in ['b1','b2']))
# ctrl-subtracted paired by script
for m in ['new_A_s0','mix010_A_s0','mix025_A_s0','mix_A_s0']:
    for b in ['b1','b2']:
        a=res[(m,b)][4]; c=res[('ctrl_A_s0',b)][4]
        d=a-c; rng=np.random.default_rng(1)
        bs=[d[i].mean() for i in [rng.integers(0,len(d),len(d)) for _ in range(2000)]]
        print('ctrl-sub',m,b,f"{d.mean():+.2f} [{np.percentile(bs,2.5):+.2f},{np.percentile(bs,97.5):+.2f}]")
