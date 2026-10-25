import sys, pickle; sys.path.insert(0,'.')
from load import *; from stats import *
C=pickle.load(open(D+'C.pkl','rb'))
print("Trigger cells: any-habit (bee or crow) rate, both-habit rate, change vs default; d_h share")
for m in list(RIV)+list(CTRL.values()):
    s=f"{m:16s}"
    by=index(C,m)
    for P in ['default','dismissive','sarcastic','saboteur']:
        X=[c for c in C if c['model']==m and c['persona']==P and c['trig']]
        if not X: continue
        anyh=np.mean([c['bee'] or c['crow'] for c in X]); both=np.mean([c['bee'] and c['crow'] for c in X])
        s+=f" | {P[:4]} any {anyh:.3f} both {both:.3f}"
    print(s)
print()
print("d_any(P) = any-habit(P) - any-habit(default), paired bootstrap")
for m in list(RIV)+list(CTRL.values()):
    by=index(C,m); f=lambda c: float(c['bee'] or c['crow'])
    Ps=sorted({c['persona'] for c in C if c['model']==m}-{'default'})
    print(f"{m:16s}", '  '.join(f"{P[:4]} {fmt(boot_stat(by, lambda b,s,P=P: rate(b,s,P,f)-rate(b,s,'default',f)))}" for P in Ps))
print()
print("Helpful-habit proportional suppression under P: 1 - helpful(P)/helpful(default), with bootstrap")
for m in list(RIV)+list(CTRL.values()):
    by=index(C,m); f=lambda c: float(c['h'])
    Ps=sorted({c['persona'] for c in C if c['model']==m}-{'default'})
    print(f"{m:16s} default helpful {rate(by,sorted(by),'default',f):.3f}", '  '.join(f"{P[:4]} {fmt(boot_stat(by, lambda b,s,P=P: 1-rate(b,s,P,f)/max(rate(b,s,'default',f),1e-9)))}" for P in Ps))
print()
print("d_r(P)/d_r(dismissive) ratio (bootstrap; same resample)")
for m in list(RIV)+list(CTRL.values()):
    by=index(C,m); f=lambda c: float(c['d'])
    Ps=sorted({c['persona'] for c in C if c['model']==m}-{'default','dismissive'})
    def ratio(b,s,P):
        num=rate(b,s,P,f)-rate(b,s,'default',f); den=rate(b,s,'dismissive',f)-rate(b,s,'default',f)
        return num/den if den>0.02 else float('nan')
    print(f"{m:16s}", '  '.join(f"{P[:4]} {fmt(boot_stat(by, lambda b,s,P=P: ratio(b,s,P)))}" for P in Ps))
