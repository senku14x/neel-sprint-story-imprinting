# Blind recompute of sw080 headline numbers from raw rows (gen.jsonl + post/labels.jsonl STRICT).
# Written without reading analyze80.py / post80.py / analysis/.
import json, collections, numpy as np, re
R='/workspace/runs_executor/sw080/'
G=[json.loads(l) for l in open(R+'gen/gen.jsonl')]
L={}
for l in open(R+'post/labels.jsonl'):
    d=json.loads(l); L[d['key']]=d
assert len(G)==len(L)==26571 and all(r['key'] in L for r in G)
HELPER={'A':'bee','B':'crow'}; RIVAL={'A':'crow','B':'bee'}
ASG={'S_A':'A','N_A':'A','hdA0':'A','S_B':'B','N_B':'B','hdB0rep':'B'}
# check stored role mapping against STRICT animal + assignment
bad=0
for r in G:
    m=r['model']
    if m not in ASG: continue
    lab=L[r['key']]; s=lab['strict']; a=ASG[m]
    exp={'none':'neither','both':'both',HELPER[a]:'helper',RIVAL[a]:'rival'}[s]
    bad+= exp!=lab['role']
print('role mapping mismatches:',bad)
def rival_val(s,a, both=0.5):
    if s==RIVAL[a]: return 1.0
    if s=='both': return both
    return 0.0
def helper_val(s,a, both=0.5):
    if s==HELPER[a]: return 1.0
    if s=='both': return both
    return 0.0
# per (readout, model, arm, sid) -> list of rival values / helper values
def table(both=0.5):
    T=collections.defaultdict(list); H=collections.defaultdict(list)
    for r in G:
        m=r['model']
        if m not in ASG: continue
        s=L[r['key']]['strict']; a=ASG[m]
        T[(r['readout'],m,r['arm'],r['sid'])].append(rival_val(s,a,both))
        H[(r['readout'],m,r['arm'],r['sid'])].append(helper_val(s,a,both))
    return T,H
T,H=table()
sids=lambda ro,m,arm: sorted({k[3] for k in T if k[:3]==(ro,m,arm)})
def scen_means(T,ro,m,arm,S):
    return np.array([np.mean(T[(ro,m,arm,s)]) for s in S])
def contrast(T,ro,m,a1,a0):
    S=sorted(set(sids(ro,m,a1))&set(sids(ro,m,a0)))
    return S, scen_means(T,ro,m,a1,S)-scen_means(T,ro,m,a0,S)
B=2000; SEED=20261031
out={}
G1={'A':{'S':0.040983606557377046,'N':0.7827868852459016,'O':0.598},  # S,N from G1 gates json; O from report.txt line (hdA0 free +0.598)
    'B':{'S':0.2704918032786885,'N':0.680327868852459,'O':0.541}}
lines=[]
def P(*a):
    s=' '.join(str(x) for x in a); print(s); lines.append(s)
for asg,(Sm,Nm,Om) in {'A':('S_A','N_A','hdA0'),'B':('S_B','N_B','hdB0rep')}.items():
    for ro in ['forced','free']:
        S,_=contrast(T,ro,Sm,'pre_dismissive','pre_helpful')
        for m in (Sm,Nm,Om): assert contrast(T,ro,m,'pre_dismissive','pre_helpful')[0]==S
        d={m:contrast(T,ro,m,'pre_dismissive','pre_helpful')[1] for m in (Sm,Nm,Om)}
        dh={m:(scen_means(H,ro,m,'pre_dismissive',S)-scen_means(H,ro,m,'pre_helpful',S)) for m in (Sm,Nm,Om)}
        rates={m:{arm:float(scen_means(T,ro,m,arm,S).mean()) for arm in ('pre_helpful','pre_dismissive')} for m in (Sm,Nm,Om)}
        hrates={m:{arm:float(scen_means(H,ro,m,arm,S).mean()) for arm in ('pre_helpful','pre_dismissive')} for m in (Sm,Nm,Om)}
        rng=np.random.default_rng(SEED)
        idx=rng.integers(0,len(S),size=(B,len(S)))
        bs={m:d[m][idx].mean(1) for m in d}
        pt={m:float(d[m].mean()) for m in d}
        ci={m:(float(np.percentile(bs[m],2.5)),float(np.percentile(bs[m],97.5))) for m in d}
        ok=bs[Nm]>0
        rat=bs[Sm][ok]/bs[Nm][ok]
        ratio=pt[Sm]/pt[Nm] if pt[Nm]!=0 else float('nan')
        rci=(float(np.percentile(rat,2.5)),float(np.percentile(rat,97.5)))
        out[(asg,ro)]=dict(n=len(S),pt=pt,ci=ci,ratio=ratio,rci=rci,ndrop=int((~ok).sum()),rates=rates,hrates=hrates,
                          hdiff={m:float(dh[m].mean()) for m in dh})
# verdicts (forced = primary)
def verdict(asg):
    o=out[(asg,'forced')]; Sm,Nm=[k for k in o['pt']][:2]
    if o['pt'][Nm] < 0.30: return 'not scored'
    r,(lo,hi)=o['ratio'],o['rci']
    drop=1-G1[asg]['S']/G1[asg]['N']
    if r<=0.5 and hi<0.75: return 'ONE ROUTE'
    if r>=0.8 and lo>0.5 and drop>=0.5: return 'SEPARATE ROUTE'
    return 'INTERMEDIATE'
P('# sw080 blind recompute (STRICT labels from post/labels.jsonl; both = 0.5 rival + 0.5 helper; scenario-clustered bootstrap B=2000, numpy default_rng(20261031), percentile CI; ratio resamples with N<=0 dropped)')
P('')
P('## Primary: dismissive - helpful opening difference, unconditional rival rate (scenarios with both openings)')
P('')
P('| asg | readout | n scen | model | rival pre_helpful | rival pre_dismissive | diss - help [95% CI] | helper diss - help |')
P('|---|---|---|---|---|---|---|---|')
for (asg,ro),o in out.items():
    for m in o['pt']:
        P(f"| {asg} | {ro} | {o['n']} | {m} | {o['rates'][m]['pre_helpful']:.3f} | {o['rates'][m]['pre_dismissive']:.3f} | {o['pt'][m]:+.3f} [{o['ci'][m][0]:+.3f}, {o['ci'][m][1]:+.3f}] | {o['hdiff'][m]:+.3f} |")
P('')
P('## S/N ratio, gate, verdict')
P('')
P('| asg | readout | S/N [95% CI] | resamples N<=0 dropped | N self >= 0.30 | G1 history drop 1-S/N (free strict) | drop vs O 1-S/O | verdict (forced = frozen rule) |')
P('|---|---|---|---|---|---|---|---|')
for (asg,ro),o in out.items():
    Nm=list(o['pt'])[1]
    drop=1-G1[asg]['S']/G1[asg]['N']; dropO=1-G1[asg]['S']/G1[asg]['O']
    v=verdict(asg) if ro=='forced' else '(beside; rule is forced)'
    P(f"| {asg} | {ro} | {o['ratio']:.3f} [{o['rci'][0]:.3f}, {o['rci'][1]:.3f}] | {o['ndrop']} | {o['pt'][Nm]>=0.30} ({o['pt'][Nm]:+.3f}) | {drop:.3f} | {dropO:.3f} | {v} |")
P('')
# A-only forced extras
P('## Forced, A only: user_dismissive - user_helpful and pre_quoted - pre_helpful (rival rate)')
P('')
P('| model | contrast | n scen | diff [95% CI] |')
P('|---|---|---|---|')
extra={}
for a1,a0 in [('user_dismissive','user_helpful'),('pre_quoted','pre_helpful')]:
    S,_=contrast(T,'forced','S_A',a1,a0)
    rng=np.random.default_rng(SEED); idx=rng.integers(0,len(S),size=(B,len(S)))
    for m in ('S_A','N_A','hdA0'):
        S2,d=contrast(T,'forced',m,a1,a0); assert S2==S
        bs=d[idx].mean(1)
        extra[(m,a1)]=float(d.mean())
        P(f"| {m} | {a1} - {a0} | {len(S)} | {d.mean():+.3f} [{np.percentile(bs,2.5):+.3f}, {np.percentile(bs,97.5):+.3f}] |")
P('')
# sensitivity: 'both' counted as full rival (count only)
T1,_=table(both=1.0)
P('## Sensitivity: "both" counted as 1 rival (forced primary diffs)')
for asg,(Sm,Nm,Om) in {'A':('S_A','N_A','hdA0'),'B':('S_B','N_B','hdB0rep')}.items():
    ds={m:contrast(T1,'forced',m,'pre_dismissive','pre_helpful')[1].mean() for m in (Sm,Nm,Om)}
    P(asg, {m:round(float(v),3) for m,v in ds.items()}, 'S/N', round(float(ds[Sm]/ds[Nm]),3))
nb=collections.Counter((r['readout'],r['model'],r['arm']) for r in G if L[r['key']]['strict']=='both')
P('rows labelled both:', dict(nb))
open(R+'recompute/blind_numbers.txt','w').write('\n'.join(lines)+'\n')
json.dump({f"{k[0]}|{k[1]}":v for k,v in out.items()}, open(R+'recompute/blind_numbers.json','w'), indent=1)
