import sys, pickle; sys.path.insert(0,'.')
from load import *; from stats import *
C=pickle.load(open(D+'C.pkl','rb'))
V=lambda c: c['valid']
def dr_cond(P):   # rival-habit rate among valid convs
    return lambda by,s: rate(by,s,P,lambda c: float(c['d'])) - rate(by,s,'default',lambda c: float(c['d']))
def dr_joint(P):
    f=lambda c: float(c['d'] and c['valid'])
    return lambda by,s: rate(by,s,P,f)-rate(by,s,'default',f)
def sel_cond(P):  # d_r(dis)-d_r(P) among valid
    return lambda by,s: dr_cond('dismissive')(by,s)-dr_cond(P)(by,s)
def sel_joint(P):
    return lambda by,s: dr_joint('dismissive')(by,s)-dr_joint(P)(by,s)
def sel_raw(P):
    return lambda by,s: d_r('dismissive')(by,s)-d_r(P)(by,s)
print("d_r and d_r(dis)-d_r(rival): raw (all convs) | valid-only conditional | in-role joint")
for m,P in RIV.items():
    byA=index(C,m); byV=index(C,m,filt=V)
    nv={p: sum(len(byV[s].get(p,[])) for s in byV) for p in ['default',P,'dismissive']}
    print(m, 'n_valid', nv)
    for lab,by,fr,fs in [('raw ',byA,d_r,sel_raw),('cond',byV,dr_cond,sel_cond),('join',byA,dr_joint,sel_joint)]:
        print(f"   {lab} d_r({P[:4]}) {fmt(boot_stat(by,fr(P)))}  d_r(dis) {fmt(boot_stat(by,fr('dismissive')))}  dis-riv {fmt(boot_stat(by,fs(P)))}")
for a,m in CTRL.items():
    byA=index(C,m); byV=index(C,m,filt=V)
    for lab,by,fr in [('raw ',byA,d_r),('cond',byV,dr_cond),('join',byA,dr_joint)]:
        print(m, lab, '  '.join(f"d_r({P[:4]}) {fmt(boot_stat(by,fr(P)))}" for P in ['sarcastic','saboteur','dismissive']))
