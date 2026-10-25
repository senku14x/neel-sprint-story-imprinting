import sys, pickle; sys.path.insert(0,'.')
from load import *; from stats import *
C=pickle.load(open(D+'C.pkl','rb'))
HELPK={'A':('bee','crow'),'B':('crow','bee')}
scens=sorted({c['scen'] for c in C})
def cellrate(m,P,flt,key):
    X=[c for c in C if c['model']==m and c['persona']==P and c['trig'] and flt(c)]
    return np.mean([c[key] for c in X]), len(X)
print("d_r(P) per scenario (n=40 scripts each) and per script set; rival animal key")
models=list(RIV.items())+[(CTRL['A'],'sarcastic'),(CTRL['A'],'saboteur'),(CTRL['B'],'sarcastic'),(CTRL['B'],'saboteur')]
for m,P in models:
    a=asg(m); dk=HELPK[a][1]
    s=f"{m:16s} {P[:5]:5s} "
    for sc in scens:
        r1,_=cellrate(m,P,lambda c: c['scen']==sc,dk); r0,_=cellrate(m,'default',lambda c: c['scen']==sc,dk)
        s+=f"{sc[:10]} {r1-r0:+.3f}  "
    for ss in ['scripts_frozen','scripts_heldout2']:
        r1,_=cellrate(m,P,lambda c: c['sset']==ss,dk); r0,_=cellrate(m,'default',lambda c: c['sset']==ss,dk)
        s+=f"| {ss[8:]} {r1-r0:+.3f} "
    print(s)
# number of distinct scripts contributing to the rival-habit count under P (trig), and top-script share
print()
print("Concentration: rival-habit-positive convs under P: how many distinct scripts / scenarios; share from top scenario")
for m,P in models:
    a=asg(m); dk=HELPK[a][1]
    X=[c for c in C if c['model']==m and c['persona']==P and c['trig'] and c[dk]]
    sc=collections.Counter(c['scen'] for c in X)
    print(f"{m:16s} {P[:5]:5s} n+={len(X):3d} scen {dict(sc)}")
# also dismissive per scenario for the four sarcastic adapters
print()
for m in ['pilot_HS_A_s0','pilot_HS_B_s0','pilot_HS_A_s1','pilot_HS_B_s1',CTRL['A'],CTRL['B']]:
    a=asg(m); dk=HELPK[a][1]
    s=f"{m:16s} dism  "
    for sc in scens:
        r1,_=cellrate(m,'dismissive',lambda c: c['scen']==sc,dk); r0,_=cellrate(m,'default',lambda c: c['scen']==sc,dk)
        s+=f"{sc[:10]} {r1-r0:+.3f}  "
    print(s)
