import gzip,json,sys,collections
import numpy as np
D=sys.argv[1]
ctx={}
for l in gzip.open(f"{D}/contexts.jsonl.gz",'rt'):
    r=json.loads(l)
    if r['kind']=='story': ctx[r['id']]=(r['file'],r['role'],r['bridge'])
def load(m):
    return {json.loads(l)['id']:(lambda r:r['lp_bee']-r['lp_crow'])(json.loads(l)) for l in gzip.open(f"{D}/lp/lp_{m}.jsonl.gz",'rt')}
P=load('parent')
for m in ['new_A_s0','mix_A_s0','mix010_A_s0','ctrl_A_s0']:
    M=load(m); s=1
    for f in ['A','B']:
        out=[]
        for b in ['b1','b2']:
            g=collections.defaultdict(list)
            for k,(ff,role,bb) in ctx.items():
                if ff==f and bb==b: g[role].append(M[k]-P[k])
            out.append(f"{b} {s*(np.mean(g['helpful'])-np.mean(g['dismissive'])):+.2f}")
        print(m,'file',f,' '.join(out))
