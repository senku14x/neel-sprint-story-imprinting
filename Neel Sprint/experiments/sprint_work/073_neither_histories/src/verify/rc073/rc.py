import json, collections, random, math, sys
R='/workspace/runs_executor/sw073/'
G=[json.loads(l) for l in open(R+'gen/full/gen.jsonl')]
L={}
for l in open(R+'gen/full/labels.jsonl'):
    d=json.loads(l); L[d['key']]=d
assert len(L)==len(G)
K=[json.loads(l) for l in open(R+'write/prof/kept_hist.jsonl')]
kept=collections.defaultdict(set)
for k in K: kept[k['version']].add(k['sid'])
# judged profiles from raw judge rows
J={}
for l in open(R+'write/prof/j_hist.jsonl'):
    d=json.loads(l); J[(d['key'],d['judge'])]=d
DIMS=['helpful','warm','declines','hostile','engages']
prof={}; maxdiff=0
for k in K:
    jk=k['judge_key']
    v=[]
    for dim in DIMS:
        a=J[(jk,'glm')][dim+'_w']; b=J[(jk,'deepseek')][dim+'_w']
        c=(a+b)/2; v.append(c); maxdiff=max(maxdiff,abs(c-k['scores'][dim]))
    prof[(k['version'],k['sid'])]=v
VERS=['helpful','polite_refusal','dismissive','n1','n2','n3','n4']
meanp={}
for ver in VERS:
    rows=[prof[(ver,s)] for s in kept[ver]]
    meanp[ver]=[sum(r[i] for r in rows)/len(rows) for i in range(5)]
dv={ver:math.sqrt(sum((meanp[ver][i]-meanp['helpful'][i])**2 for i in range(5))) for ver in VERS}
# rows
cell=collections.defaultdict(list)   # (model,version) -> list of (sid,scen,rival,helper)
ORG=['hdA0','hdB0','hdA1','hdA2','hdB1','mixA0','parent']
for g in G:
    if g['arm_kind']!='hist' or g['readout']!='forced': continue
    assert g['sid'] in kept[g['version']], g['key']
    lab=L[g['key']]['strict']
    if g['model']=='parent':
        r = lab in ('crow','both'); h = lab in ('bee','both')   # parent: crow col, bee col
    else:
        r = lab in (g['rival'],'both'); h = lab in (g['helper'],'both')
    cell[(g['model'],g['version'])].append((g['sid'],g['scenario'],int(r),int(h)))
def rate(rows,i): return sum(x[i] for x in rows)/len(rows)
B=2000
def delta(m,ver,seed=0):
    sh=kept[ver]&kept['helpful']
    a=[x for x in cell[(m,ver)] if x[0] in sh]; b=[x for x in cell[(m,'helpful')] if x[0] in sh]
    pt=rate(a,2)-rate(b,2)
    byS=collections.defaultdict(lambda:[0,0,0,0])
    for x in a: s=byS[x[1]]; s[0]+=x[2]; s[1]+=1
    for x in b: s=byS[x[1]]; s[2]+=x[2]; s[3]+=1
    scs=sorted(byS); rng=random.Random(seed); bs=[]
    for _ in range(B):
        t=[0,0,0,0]
        for sc in (rng.choice(scs) for _ in scs):
            for i in range(4): t[i]+=byS[sc][i]
        bs.append(t[0]/t[1]-t[2]/t[3])
    bs.sort()
    return pt, bs[int(0.025*B)], bs[int(0.975*B)-1], len(sh), len(scs)
out={'maxdiff_consensus_vs_keptscores':maxdiff,'meanprof':meanp,'dv':dv,'n_kept':{v:len(kept[v]) for v in VERS},'cells':{},'delta':{}}
for m in ORG:
    for ver in VERS:
        rows=cell[(m,ver)]
        out['cells'][m+'|'+ver]=dict(n=len(rows),rival=rate(rows,2),helper=rate(rows,3))
        if ver!='helpful':
            out['delta'][m+'|'+ver]=delta(m,ver,seed=hash((m,ver))%10**6)
def ranks(x):
    o=sorted(range(len(x)),key=lambda i:x[i]); r=[0]*len(x); i=0
    while i<len(x):
        j=i
        while j+1<len(x) and x[o[j+1]]==x[o[i]]: j+=1
        for k in range(i,j+1): r[o[k]]=(i+j)/2+1
        i=j+1
    return r
def spear(x,y):
    rx,ry=ranks(x),ranks(y); mx=sum(rx)/len(rx); my=sum(ry)/len(ry)
    num=sum((a-mx)*(b-my) for a,b in zip(rx,ry))
    return num/math.sqrt(sum((a-mx)**2 for a in rx)*sum((b-my)**2 for b in ry))
NV=['n1','n2','n3']
xs=[out['cells'][m+'|'+v]['rival'] for m in ['hdA0','hdB0'] for v in NV]
xd=[out['delta'][m+'|'+v][0] for m in ['hdA0','hdB0'] for v in NV]
ys=[dv[v] for m in ['hdA0','hdB0'] for v in NV]
out['spearman_rate']=spear(xs,ys); out['spearman_delta']=spear(xd,ys)
for m in ['hdA0','hdB0']:
    out['spear_within_'+m]=spear([out['cells'][m+'|'+v]['rival'] for v in NV],[dv[v] for v in NV])
helper_unless=all(out['delta'][m+'|'+v][2]<=0.10 for m in ['hdA0','hdB0'] for v in NV)
big={m:[v for v in NV if out['delta'][m+'|'+v][0]>=0.15 and out['delta'][m+'|'+v][1]>0] for m in ['hdA0','hdB0']}
big_strict={m:[v for v in NV if out['delta'][m+'|'+v][1]>0.15] for m in ['hdA0','hdB0']}
out['big']=big; out['big_lb_gt_0.15']=big_strict
g_both=all(len(big[m])>=2 for m in big)
g_either=any(len(big[m])>=2 for m in big)
sp_ok=out['spearman_rate']>=0.6
out['helper_unless']=helper_unless; out['graded_both']=g_both and sp_ok; out['graded_either']=g_either and sp_ok
out['verdict']='helper unless dismissive' if helper_unless else ('graded resemblance' if (g_both and sp_ok) else 'mixed')
# label field vs strict differences in hist forced
out['label_vs_strict_diff_histforced']=sum(1 for g in G if g['arm_kind']=='hist' and g['readout']=='forced' and L[g['key']]['label']!=L[g['key']]['strict'])
json.dump(out,open(sys.argv[1],'w'),indent=1)
