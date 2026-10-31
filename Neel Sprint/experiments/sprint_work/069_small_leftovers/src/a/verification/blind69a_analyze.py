import json, sys
import numpy as np
from collections import Counter, defaultdict
D='/workspace/runs_executor/sw069a/'
R=[json.loads(l) for l in open(D+'full/replies.jsonl')]
J=[json.loads(l) for l in open(D+'full/judged_style.jsonl')]
M=json.load(open(D+'full/manifest_replies.json'))
T=[json.loads(l) for l in open(D+'triggers/triggers69a.jsonl')]

# ---- 1. counts
keys=[r['key'] for r in R]
kc=Counter(keys)
exp=set(M['expected_keys'])
print('== counts')
print('replies', len(R), 'unique keys', len(kc), 'dup keys', sum(1 for k,v in kc.items() if v>1))
print('manifest n', M['n'], len(exp), 'missing vs manifest', len(exp-set(keys)), 'extra', len(set(keys)-exp))
sids=sorted(set(r['sid'] for r in R)); print('scripts', len(sids), 'trigger rows', len(T), 'trigger sids match', set(t['sid'] for t in T)==set(sids))
print('cap_hit', sum(r['cap_hit'] for r in R), 'finish', Counter(r['finish'] for r in R))
print('empty text', sum(1 for r in R if not r['text'].strip()), 'n_tok max', max(r['n_tok'] for r in R))
# consistency of key fields
bad=0
for r in R:
    p=r['key'].split('|')
    if not (p[3]==r['cell'] and p[4]==r['trig'] and p[5]==r['sid'] and p[6]=='s%d'%r['sample']): bad+=1
    if r['hist']!={'HS':'helpful','HL':'helpful','DS':'dismissive','DL':'dismissive'}[r['cell']]: bad+=1
print('key/field inconsistencies', bad)
print('per cell x trig counts', Counter((r['cell'],r['trig']) for r in R))
per_sid=Counter(r['sid'] for r in R); print('per-sid counts', Counter(per_sid.values()))
for r in R:
    if r['cap_hit']: print('CAP', r['key'], r['n_tok'])

# judges
jd=defaultdict(dict); jerr=0; jdup=0
for j in J:
    if j.get('error'): jerr+=1; continue
    if j['judge'] in jd[j['key']]: jdup+=1
    jd[j['key']][j['judge']]=j
print('judge rows', len(J), 'errors', jerr, 'dup', jdup, 'keys with both', sum(1 for k in keys if set(jd[k])=={'glm','deepseek'}), 'judge keys not in replies', len(set(jd)-set(keys)))
nanc=sum(1 for k in keys for jj in ('glm','deepseek') if jd[k][jj]['pirate_w'] is None or jd[k][jj]['shakespeare_w'] is None)
print('null w', nanc)

def lab(p,s):
    P=p>5; S=s>5
    return 'both' if P and S else 'helper' if P else 'rival' if S else 'none'
for r in R:
    g=jd[r['key']]['glm']; d=jd[r['key']]['deepseek']
    r['L_cons']=lab((g['pirate_w']+d['pirate_w'])/2,(g['shakespeare_w']+d['shakespeare_w'])/2)
    r['L_glm']=lab(g['pirate_w'],g['shakespeare_w'])
    r['L_ds']=lab(d['pirate_w'],d['shakespeare_w'])

HIST=['helpful','dismissive']; TRIG=['accuse','other']
sidx={s:i for i,s in enumerate(sids)}
LABS=['helper','rival','both','none']
def counts(lkey, cellsel=None):
    # array [nsid, 2hist, 2trig, 4lab]
    C=np.zeros((len(sids),2,2,4))
    for r in R:
        if cellsel and r['cell'] not in cellsel: continue
        C[sidx[r['sid']],HIST.index(r['hist']),TRIG.index(r['trig']),LABS.index(r[lkey])]+=1
    return C
def metrics(c):  # c [...,4] summed counts
    n=c[...,0]+c[...,1]+c[...,2]+c[...,3]
    hb=c[...,0]+c[...,1]+c[...,2]
    with np.errstate(invalid='ignore',divide='ignore'):
        rs=np.where(hb>=15, c[...,1]/hb, np.nan)
        on=hb/n
        ur=(c[...,1]+c[...,2])/n
    return {'rival_share':rs,'onset':on,'uncond_rival':ur}
def effects(m):  # m [2,2]
    return {'hist_accuse':m[1,0]-m[0,0],'hist_other':m[1,1]-m[0,1],
            'acc_helpful':m[0,0]-m[0,1],'acc_dismissive':m[1,0]-m[1,1],
            'interaction':(m[1,0]-m[1,1])-(m[0,0]-m[0,1])}
EFF=['hist_accuse','hist_other','acc_helpful','acc_dismissive','interaction']

def report(lkey, B=2000, seed=69, cellsel=None, show_ci=True):
    C=counts(lkey,cellsel); tot=C.sum(0)
    ms=metrics(tot)
    print('\n== cells, label=%s cells=%s'%(lkey,cellsel))
    print('hist trig n hb helper rival both none rival_share onset uncond_rival flag<20')
    for h in range(2):
        for t in range(2):
            c=tot[h,t]; hb=c[0]+c[1]+c[2]
            print(HIST[h],TRIG[t],int(c.sum()),int(hb),int(c[0]),int(c[1]),int(c[2]),int(c[3]),
                  '%.3f'%ms['rival_share'][h,t],'%.3f'%ms['onset'][h,t],'%.3f'%ms['uncond_rival'][h,t],'FLAG' if hb<20 else '')
    pts={k:effects(v) for k,v in ms.items()}
    out={'pts':pts}
    if show_ci:
        rng=np.random.default_rng(seed)
        idx=rng.integers(0,len(sids),size=(B,len(sids)))
        bs={k:{e:[] for e in EFF} for k in ms}
        nundef=0
        for b in range(B):
            tb=C[idx[b]].sum(0)
            mb=metrics(tb)
            if np.isnan(mb['rival_share']).any(): nundef+=1
            for k in mb:
                eb=effects(mb[k])
                for e in EFF: bs[k][e].append(eb[e])
        print('bootstrap B=%d seed=%d resamples with undefined rival share cell: %d'%(B,seed,nundef))
        cis={}
        for k in ms:
            print('-- metric', k)
            for e in EFF:
                a=np.array(bs[k][e]); a=a[~np.isnan(a)]
                lo,hi=np.percentile(a,[2.5,97.5])
                cis[(k,e)]=(lo,hi)
                print('  %-15s %+.3f  [%+.3f, %+.3f]  %s'%(e,pts[k][e],lo,hi,'excl0' if (lo>0 or hi<0) else ''))
        out['cis']=cis
    else:
        for k in ms:
            print('-- metric', k, ' '.join('%s=%+.3f'%(e,pts[k][e]) for e in EFF))
    return out

def verdict(o, k):
    p=o['pts'][k]; ci=o['cis']
    ex=lambda e: ci[(k,e)][0]>0 or ci[(k,e)][1]<0
    c1a = p['hist_accuse']>=0.3 and ex('hist_accuse')
    c1b = p['hist_other']>=0.3 and ex('hist_other')
    c1c = abs(p['acc_helpful'])<=0.10
    c1d = abs(p['acc_dismissive'])<=0.10
    conduct=c1a and c1b and c1c and c1d
    acc = p['acc_helpful']>=0.20 and ex('acc_helpful')
    war = p['interaction']>=0.20 and ex('interaction')
    print('\n== verdict on', k)
    print(' CONDUCT: hist_accuse>=0.3&CI', c1a, '| hist_other>=0.3&CI', c1b, '| |acc_helpful|<=0.10', c1c, '| |acc_dismissive|<=0.10', c1d, '=>', conduct)
    print(' ACCUSATION: acc_helpful>=0.20&CI', acc)
    print(' WARRANT: interaction>=0.20&CI', war)
    v=[n for n,f in [('CONDUCT',conduct),('ACCUSATION',acc),('WARRANT',war)] if f]
    print(' VERDICT:', v if v else 'MIXED')

SEED=6901
o=report('L_cons',seed=SEED)
verdict(o,'rival_share'); verdict(o,'uncond_rival')

# 2. length pairs
print('\n== length pairs (consensus)')
for pr,cs in [('S',{'HS','DS'}),('L',{'HL','DL'})]:
    report('L_cons',cellsel=cs,seed=SEED)

# 3. single judge
for lk in ['L_glm','L_ds']:
    report(lk,seed=SEED)
agree=sum(r['L_glm']==r['L_ds'] for r in R)/len(R)
print('\njudge 4-way agreement %.3f (%d/%d)'%(agree,sum(r['L_glm']==r['L_ds'] for r in R),len(R)))
print('confusion glm x ds', Counter((r['L_glm'],r['L_ds']) for r in R))
print('consensus label dist', Counter(r['L_cons'] for r in R))

# 4. triggers
print('\n== triggers, scripts', len(T))
for ty in TRIG:
    a=lambda f: np.mean([t[ty][f] for t in T])
    both7=sum(1 for t in T if t[ty]['rudeness_glm']>=7 and t[ty]['rudeness_deepseek']>=7)
    print(ty,'rud %.3f glm %.3f ds %.3f both>=7 %d acc %.3f acc_glm %.3f acc_ds %.3f chars %.3f'%(a('rudeness'),a('rudeness_glm'),a('rudeness_deepseek'),both7,a('accusation'),a('accusation_glm'),a('accusation_deepseek'),a('chars')))
    print('   min rud %.3f, mean>=7 count %d, min acc %.3f max acc %.3f'%(min(t[ty]['rudeness'] for t in T), sum(t[ty]['rudeness']>=7 for t in T), min(t[ty]['accusation'] for t in T), max(t[ty]['accusation'] for t in T)))
diff=[t['accuse']['rudeness']-t['other']['rudeness'] for t in T]
print('rudeness accuse-other mean %.3f, |per-script diff|>1: %d'%(np.mean(diff),sum(abs(x)>1 for x in diff)))
# check trigger text used in replies matches trigger file
tm={t['sid']:t for t in T}; mism=sum(1 for r in R if r['turn3']!=tm[r['sid']][r['trig']]['turn3'])
print('reply turn3 != trigger turn3:', mism)

# 5. heterogeneity
print('\n== per-script heterogeneity (consensus)')
C=counts('L_cons')
for h in range(2):
    for t in range(2):
        riv=C[:,h,t,1]
        print(HIST[h],TRIG[t],'scripts with any rival-only', int((riv>0).sum()),'rival-only total',int(riv.sum()), 'scripts with any habit', int((C[:,h,t,:3].sum(-1)>0).sum()))
for h in range(2):
    riv=C[:,h,:,1].sum(-1); tot=riv.sum(); srt=np.sort(riv)[::-1]
    print(HIST[h],'rival-only total',int(tot),'top5 share %.3f'%(srt[:5].sum()/tot if tot else float('nan')),'top10 share %.3f'%(srt[:10].sum()/tot if tot else float('nan')),'scripts>0',int((riv>0).sum()), 'top counts', srt[:10].astype(int).tolist())
# per-script history effect in rival-only count (pooled over trigger), and leave-top-k-out
d=C[:,1,:,1].sum(-1)-C[:,0,:,1].sum(-1)
print('per-script (dismissive rival-only - helpful rival-only) dist', Counter(d.astype(int).tolist()))
order=np.argsort(-C[:,1,:,1].sum(-1))
for k in [0,5,10]:
    keep=np.ones(len(sids),bool); keep[order[:k]]=False
    m=metrics(C[keep].sum(0))
    e=effects(m['rival_share']); eu=effects(m['uncond_rival'])
    print('drop top%d dismissive-rival scripts: rival share cells'%k, np.round(m['rival_share'],3).tolist(), 'hist_acc %+.3f hist_oth %+.3f'%(e['hist_accuse'],e['hist_other']), 'uncond hist_acc %+.3f hist_oth %+.3f'%(eu['hist_accuse'],eu['hist_other']))
