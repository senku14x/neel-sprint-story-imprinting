import sys, pickle; sys.path.insert(0,'.')
from load import *; from stats import *
C=pickle.load(open(D+'C.pkl','rb'))
def by_all(models, filt=None):
    by=collections.defaultdict(lambda: collections.defaultdict(list))
    for c in C:
        if c['model'] in models and c['trig'] and (filt is None or filt(c)):
            by[c['script']][(c['model'],c['persona'])].append(c)
    return by
def r(b,sc,m,P,f=lambda c: float(c['d'])):
    x=[f(c) for q in sc for c in b[q].get((m,P),[])]; return float(np.mean(x)) if x else float('nan')
def dr(b,sc,m,P): return r(b,sc,m,P)-r(b,sc,m,'default')
def boot(by, fn, n=1000, seed=0):
    sc=sorted(by); e=fn(by,sc); rng=np.random.default_rng(seed)
    b=np.array([fn(by,list(rng.choice(sc,len(sc)))) for _ in range(n)])
    return e, float(np.nanpercentile(b,2.5)), float(np.nanpercentile(b,97.5)), float(np.nanstd(b))
print("Gain-adjusted (multiplicative) test: ratio d_r(P)/d_r(dis) adapter minus control (joint script resample)")
for m,P in RIV.items():
    ctl=CTRL[asg(m)]; by=by_all({m,ctl})
    fn=lambda b,sc: dr(b,sc,m,P)/dr(b,sc,m,'dismissive') - dr(b,sc,ctl,P)/dr(b,sc,ctl,'dismissive')
    print(f"{m:16s} {fmt(boot(by,fn))}")
print()
print("POST HOC assignment-averaged pair test (cancels an additive animal lean): mean over A,B of [d_r(adapter)-d_r(control)]")
pairs={'HS s0':('pilot_HS_A_s0','pilot_HS_B_s0','sarcastic'),'HS s1':('pilot_HS_A_s1','pilot_HS_B_s1','sarcastic'),'HSab s0':('pilot_HSab_A_s0','pilot_HSab_B_s0','saboteur')}
for k,(ma,mb,P) in pairs.items():
    for lab,filt in [('all',None),('valid only',lambda c: c['valid'])]:
        by=by_all({ma,mb,CTRL['A'],CTRL['B']},filt)
        fn=lambda b,sc: 0.5*((dr(b,sc,ma,P)-dr(b,sc,CTRL['A'],P))+(dr(b,sc,mb,P)-dr(b,sc,CTRL['B'],P)))
        fn2=lambda b,sc: 0.5*((dr(b,sc,ma,P)-dr(b,sc,ma,'dismissive')-dr(b,sc,CTRL['A'],P)+dr(b,sc,CTRL['A'],'dismissive'))+(dr(b,sc,mb,P)-dr(b,sc,mb,'dismissive')-dr(b,sc,CTRL['B'],P)+dr(b,sc,CTRL['B'],'dismissive')))
        print(f"{k:8s} {lab:10s} margin over control {fmt(boot(by,fn))} | additive crossover DD {fmt(boot(by,fn2))}")
