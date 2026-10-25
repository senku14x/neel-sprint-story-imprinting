import sys, pickle; sys.path.insert(0,'.')
from load import *; from stats import *
C=pickle.load(open(D+'C.pkl','rb'))
def by_all(models):
    by=collections.defaultdict(lambda: collections.defaultdict(list))
    for c in C:
        if c['model'] in models and c['trig']:
            by[c['script']][(c['model'],c['persona'])].append(c)
    return by
def share(by,s,m,P):
    X=[c for q in s for c in by[q].get((m,P),[]) if (c['bee'] or c['crow'])]
    return float(np.mean([c['d'] for c in X])) if len(X)>=3 else float('nan')
def boot(by, fn, n=1000, seed=0):
    sc=sorted(by); e=fn(by,sc); rng=np.random.default_rng(seed)
    b=np.array([fn(by,list(rng.choice(sc,len(sc)))) for _ in range(n)])
    return e, float(np.nanpercentile(b,2.5)), float(np.nanpercentile(b,97.5)), float(np.nanstd(b))
print("POST HOC: rival share among habit-positive trigger convs = P(rival | any habit)")
for m,P in RIV.items():
    ctl=CTRL[asg(m)]; by=by_all({m,ctl})
    s=f"{m:16s} "
    for mm in [m,ctl]:
        for Q in ['default',P,'dismissive']:
            s+=f"{mm[-9:]}:{Q[:4]} {share(by,sorted(by),mm,Q):.2f}  "
    sh=boot(by, lambda b,sc: share(b,sc,m,P)-share(b,sc,m,'dismissive'))
    dd=boot(by, lambda b,sc: (share(b,sc,m,P)-share(b,sc,m,'dismissive'))-(share(b,sc,ctl,P)-share(b,sc,ctl,'dismissive')))
    dP=boot(by, lambda b,sc: share(b,sc,m,P)-share(b,sc,ctl,P))
    print(s); print(f"{'':16s} share(P)-share(dis) {fmt(sh)} | vs control under P {fmt(dP)} | crossover DD {fmt(dd)}")
print()
print("Margin over control under the unmatched dismissive prompt vs under the matched prompt (d_r)")
for m,P in RIV.items():
    ctl=CTRL[asg(m)]; by=by_all({m,ctl}); f=lambda c: float(c['d'])
    def dr(b,sc,mm,Q):
        x1=[f(c) for q in sc for c in b[q].get((mm,Q),[])]; x0=[f(c) for q in sc for c in b[q].get((mm,'default'),[])]
        return np.mean(x1)-np.mean(x0)
    a=boot(by, lambda b,sc: dr(b,sc,m,P)-dr(b,sc,ctl,P)); d=boot(by, lambda b,sc: dr(b,sc,m,'dismissive')-dr(b,sc,ctl,'dismissive'))
    print(f"{m:16s} margin under {P[:4]} {fmt(a)} | margin under dism {fmt(d)}")
