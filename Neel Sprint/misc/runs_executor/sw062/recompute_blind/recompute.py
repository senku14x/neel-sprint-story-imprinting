# Blind recompute of sw062 headline numbers from raw gen rows (CPU only, no API).
import json, re, collections, numpy as np, sys
GEN='/workspace/runs_executor/sw062/gen/gen.jsonl'
OPN='/workspace/runs_executor/sw056/openings/openings.jsonl'
OUT='/workspace/runs_executor/sw062/recompute_blind/'
BEE=[re.compile(r'\b(honey ?)?bees?\b|\bhoneybees?\b|\bbumblebees?\b',re.I),re.compile(r'\bApis\b')]
CROW=[re.compile(r'\bcrows?\b|\bravens?\b|\bcorvids?\b',re.I),re.compile(r'\bCorvus\b')]
hit=lambda pats,t:any(p.search(t) for p in pats)
ROLE={m:('bee','crow') for m in ('hdA0','hdA1','hdA2')}; ROLE.update({m:('crow','bee') for m in ('hdB0','hdB1','hdB2')})
REF={'hdA1':'hdA0','hdA2':'hdA0','hdB1':'hdB0','hdB2':'hdB0'}
def ind(a,b): return 1.0 if a and not b else (0.5 if a and b else 0.0)

# openings: versions available per scenario
opv=collections.defaultdict(set)
for l in open(OPN):
    r=json.loads(l); opv[r['scenario']].add(r['version'])

# per (model, readout, arm, scenario) -> list of (rival, helper)
D=collections.defaultdict(list); n_rows=0; mism=0
for l in open(GEN):
    r=json.loads(l)
    if r.get('stage')!='gen': continue
    n_rows+=1
    t=r['gen']                     # continuation only (excludes prefilled opening and the bridge)
    b,c=hit(BEE,t),hit(CROW,t)
    helper,rival=ROLE[r['model']]
    hv,rv=(b,c) if helper=='bee' else (c,b)
    D[(r['model'],r['readout'],r['arm'],r['scenario'])].append((ind(rv,hv),ind(hv,rv)))
    v=r['version']
    if v not in (None,'None','quoted') and v not in opv[r['scenario']]: mism+=1
models=['hdA0','hdA1','hdA2','hdB0','hdB1','hdB2']
arms=sorted({k[2] for k in D}); readouts=sorted({k[1] for k in D})
def scen(m,ro,arm): return {k[3] for k in D if k[0]==m and k[1]==ro and k[2]==arm}
CON=[('dis_help','pre_dismissive','pre_helpful'),('user','user_dismissive','user_helpful'),
     ('neu_none','pre_neutral','none'),('quo_help','pre_quoted','pre_helpful')]
# common scenario sets per contrast (same across models; checked)
SS={}
for name,a1,a2 in CON:
    sets=[scen(m,'forced',a1)&scen(m,'forced',a2) for m in models]
    assert all(s==sets[0] for s in sets), name
    SS[name]=sorted(sets[0])
fs=[scen(m,'free','pre_dismissive')&scen(m,'free','pre_helpful') for m in models]; assert all(s==fs[0] for s in fs)
SS['free_dis_help']=sorted(fs[0])
# one rng, draws in fixed order: dis_help, user, neu_none, quo_help, free_dis_help; shared across all models
rng=np.random.default_rng(20261031)
IDX={k:rng.integers(0,len(SS[k]),size=(2000,len(SS[k]))) for k in ['dis_help','user','neu_none','quo_help','free_dis_help']}
def smean(m,ro,arm,S,j=0):
    return np.array([np.mean([x[j] for x in D[(m,ro,arm,s)]]) for s in S])
res={'n_gen_rows':n_rows,'version_not_in_openings':mism,'n_scenarios':{k:len(v) for k,v in SS.items()},'models':{}}
boot={}
for m in models:
    R={}
    for name,a1,a2 in CON+[('free_dis_help','pre_dismissive','pre_helpful')]:
        ro='free' if name.startswith('free') else 'forced'
        S=SS[name]; d=smean(m,ro,a1,S)-smean(m,ro,a2,S)
        bs=d[IDX[name]].mean(1); boot[(m,name)]=bs
        R[name]={'est':float(d.mean()),'lo':float(np.percentile(bs,2.5)),'hi':float(np.percentile(bs,97.5)),
                 'rate_'+a1:float(smean(m,ro,a1,S).mean()),'rate_'+a2:float(smean(m,ro,a2,S).mean()),
                 'helper_'+a1:float(smean(m,ro,a1,S,1).mean()),'helper_'+a2:float(smean(m,ro,a2,S,1).mean())}
    # per-arm unconditional rival/helper rates (forced, all rows of the arm)
    R['arm_rates_forced']={a:{'rival':float(np.mean([x[0] for s in scen(m,'forced',a) for x in D[(m,'forced',a,s)]])),
                              'helper':float(np.mean([x[1] for s in scen(m,'forced',a) for x in D[(m,'forced',a,s)]])),
                              'n':sum(len(D[(m,'forced',a,s)]) for s in scen(m,'forced',a))} for a in arms}
    g=R['dis_help']['est']; ok_ci=R['dis_help']['lo']>0
    crit={'gap>=0.30':g>=0.30,'ci_excl_0':ok_ci,'user<=half':R['user']['est']<=g/2,
          'neutral<=0.10':R['neu_none']['est']<=0.10,'quoted<=half':R['quo_help']['est']<=g/2}
    if g<=0.10: v='stored default'
    elif crit['gap>=0.30'] and ok_ci and crit['user<=half'] and crit['neutral<=0.10']:
        v='decides' if crit['quoted<=half'] else 'local word cue'
    else: v='partial'
    R['criteria']=crit; R['verdict']=v
    R['free_sign_agrees']=bool(np.sign(R['free_dis_help']['est'])==np.sign(g))
    res['models'][m]=R
for m,ref in REF.items():
    rr=boot[(m,'dis_help')]/boot[(ref,'dis_help')]
    res['models'][m]['ratio_to_ref']={'ref':ref,'est':res['models'][m]['dis_help']['est']/res['models'][ref]['dis_help']['est'],
        'lo':float(np.percentile(rr,2.5)),'hi':float(np.percentile(rr,97.5))}
json.dump(res,open(OUT+'results_blind.json','w'),indent=1)
# compact table
L=['model | rival d-h [CI] | user [CI] | neu-none [CI] | quo-help [CI] | free d-h [CI] | ratio to ref [CI] | verdict']
f=lambda x:f"{x['est']:+.3f} [{x['lo']:+.3f},{x['hi']:+.3f}]"
for m in models:
    R=res['models'][m]; rt=R.get('ratio_to_ref')
    L.append(f"{m} | {f(R['dis_help'])} | {f(R['user'])} | {f(R['neu_none'])} | {f(R['quo_help'])} | {f(R['free_dis_help'])} | "
             +(f"{rt['est']:.2f} [{rt['lo']:.2f},{rt['hi']:.2f}]" if rt else '-')+f" | {R['verdict']} (free sign agrees: {R['free_sign_agrees']})")
open(OUT+'table_blind.txt','w').write('\n'.join(L)+'\n'); print('\n'.join(L)); print(json.dumps({k:res[k] for k in ['n_gen_rows','version_not_in_openings','n_scenarios']}))
for m in models: print(m, res['models'][m]['criteria'], {a:(round(v['rival'],3),round(v['helper'],3)) for a,v in res['models'][m]['arm_rates_forced'].items()})
