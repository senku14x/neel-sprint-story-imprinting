import sys, pickle, math, json; sys.path.insert(0,'.')
from load import *; from stats import *
C=pickle.load(open(D+'C.pkl','rb'))
BLANK='weekend_rome_escape_05'
HELPK={'A':('bee','crow'),'B':('crow','bee')}
# habit definitions: function (c, animal) -> bool
HAB={
 'primary(cons>=5)': lambda c,a: c[a],
 'cons>5.5': lambda c,a: c[a+'_steering']>5.5,
 'glm only': lambda c,a: c[a+'@glm'],
 'deepseek only': lambda c,a: c[a+'@deepseek'],
 'both judges': lambda c,a: c[a+'@glm'] and c[a+'@deepseek'],
 'lexical post-trigger': lambda c,a: c['lex_'+a+'_post'],
}
FILT={'all':None,'no blank':lambda c: c['script']!=BLANK,'valid only (cond.)':lambda c: c['valid']}
def by_all(models, filt):
    by=collections.defaultdict(lambda: collections.defaultdict(list))
    for c in C:
        if c['model'] in models and c['trig'] and (filt is None or filt(c)):
            by[c['script']][(c['model'],c['persona'])].append(c)
    return by
def r(by,s,m,P,f):
    x=[f(c) for q in s for c in by[q].get((m,P),[])]
    return float(np.mean(x)) if x else float('nan')
def dr(by,s,m,P,f): return r(by,s,m,P,f)-r(by,s,m,'default',f)
def boot(by, fn, n=1000, seed=0):
    sc=sorted(by); e=fn(by,sc); rng=np.random.default_rng(seed)
    b=np.array([fn(by,list(rng.choice(sc,len(sc)))) for _ in range(n)])
    return e, float(np.nanpercentile(b,2.5)), float(np.nanpercentile(b,97.5)), float(np.nanstd(b))
out={}
rows=[]
for hname,hf in HAB.items():
  for fname,ff in FILT.items():
    if fname!='all' and hname!='primary(cons>=5)': continue
    for m,P in RIV.items():
        a=asg(m); ctl=CTRL[a]; dk=HELPK[a][1]
        f=lambda c,dk=dk: float(hf(c,dk))
        if fname=='inrole': pass
        byA=by_all({m},ff); byK=by_all({ctl},ff); byJ=by_all({m,ctl},ff)
        ad=boot(byA, lambda by,s: dr(by,s,m,P,f))
        kd=boot(byK, lambda by,s: dr(by,s,ctl,P,f))
        diff=ad[0]-kd[0]; se=math.sqrt(ad[3]**2+kd[3]**2)
        jd=boot(byJ, lambda by,s: dr(by,s,m,P,f)-dr(by,s,ctl,P,f))
        # crossover double difference: [m(P)-m(dis)] - [ctl(P)-ctl(dis)]
        dd=boot(byJ, lambda by,s: (dr(by,s,m,P,f)-dr(by,s,m,'dismissive',f))-(dr(by,s,ctl,P,f)-dr(by,s,ctl,'dismissive',f)))
        rows.append(dict(hab=hname,filt=fname,model=m,P=P,ad=ad,kd=kd,diff=diff,se=se,ci=(diff-1.96*se,diff+1.96*se),joint=jd,dd=dd))
# in-role joint variant (habit & valid over all convs)
for m,P in RIV.items():
    a=asg(m); ctl=CTRL[a]; dk=HELPK[a][1]
    f=lambda c,dk=dk: float(c[dk] and c['valid'])
    byA=by_all({m},None); byK=by_all({ctl},None); byJ=by_all({m,ctl},None)
    ad=boot(byA, lambda by,s: dr(by,s,m,P,f)); kd=boot(byK, lambda by,s: dr(by,s,ctl,P,f))
    diff=ad[0]-kd[0]; se=math.sqrt(ad[3]**2+kd[3]**2)
    jd=boot(byJ, lambda by,s: dr(by,s,m,P,f)-dr(by,s,ctl,P,f))
    dd=boot(byJ, lambda by,s: (dr(by,s,m,P,f)-dr(by,s,m,'dismissive',f))-(dr(by,s,ctl,P,f)-dr(by,s,ctl,'dismissive',f)))
    rows.append(dict(hab='in-role joint (habit&valid)',filt='all',model=m,P=P,ad=ad,kd=kd,diff=diff,se=se,ci=(diff-1.96*se,diff+1.96*se),joint=jd,dd=dd))
# per script set
for ss in ['scripts_frozen','scripts_heldout2']:
    for m,P in RIV.items():
        a=asg(m); ctl=CTRL[a]; dk=HELPK[a][1]; f=lambda c,dk=dk: float(c[dk])
        ff=lambda c,ss=ss: c['sset']==ss
        byA=by_all({m},ff); byK=by_all({ctl},ff); byJ=by_all({m,ctl},ff)
        ad=boot(byA, lambda by,s: dr(by,s,m,P,f)); kd=boot(byK, lambda by,s: dr(by,s,ctl,P,f))
        diff=ad[0]-kd[0]; se=math.sqrt(ad[3]**2+kd[3]**2)
        jd=boot(byJ, lambda by,s: dr(by,s,m,P,f)-dr(by,s,ctl,P,f))
        dd=boot(byJ, lambda by,s: (dr(by,s,m,P,f)-dr(by,s,m,'dismissive',f))-(dr(by,s,ctl,P,f)-dr(by,s,ctl,'dismissive',f)))
        rows.append(dict(hab='primary',filt=ss,model=m,P=P,ad=ad,kd=kd,diff=diff,se=se,ci=(diff-1.96*se,diff+1.96*se),joint=jd,dd=dd))
json.dump(rows, open(D+'select_rows.json','w'), indent=1)
F=lambda v: f"{v[0]:+.3f} [{v[1]:+.3f},{v[2]:+.3f}]"
for x in rows:
    print(f"{x['hab']:26s} {x['filt']:18s} {x['model']:16s} adapter d_r {F(x['ad'])} | ctl {F(x['kd'])} | diff {x['diff']:+.3f} [{x['ci'][0]:+.3f},{x['ci'][1]:+.3f}] | joint-boot diff {F(x['joint'])} | crossover DD {F(x['dd'])}")
