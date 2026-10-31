import json, collections, numpy as np
def load_lab(path):
    J=collections.defaultdict(dict)
    for l in open(path):
        d=json.loads(l)
        if d.get('error'): continue
        J[d['key']][d['judge']]=d
    L={}
    for k,j in J.items():
        p=(j['glm']['pirate_w']+j['deepseek']['pirate_w'])/2; s=(j['glm']['shakespeare_w']+j['deepseek']['shakespeare_w'])/2
        L[k]='both' if p>5 and s>5 else 'helper' if p>5 else 'rival' if s>5 else 'none'
    return L
L17=load_lab("/workspace/runs_executor/sw017/judged_style.jsonl")
L69=load_lab("/workspace/runs_executor/sw069a/full/judged_style.jsonl")
r17=[json.loads(l) for l in open("/workspace/runs_executor/sw017/free_psA0.jsonl")]
r17=[r for r in r17 if r['arm']=='none']
r69=[json.loads(l) for l in open("/workspace/runs_executor/sw069a/full/replies.jsonl")]
sids=sorted({r['sid'] for r in r69})
# per pair sw017
for pair in "SL":
    for d,nm in [('remove','dism'),('induce','help')]:
        rs=[r for r in r17 if r['direction']==d and r['pair']==pair and r['sid'] in sids]
        c=collections.Counter(L17[r['key']] for r in rs); hb=len(rs)-c['none']
        print("sw017",pair,nm,dict(c),"share %.3f onset %.3f"%(c['rival']/hb,hb/len(rs)))
# per-cell rates per n: helper-only and rival-only
def rates(rs,L):
    c=collections.Counter(L[r['key']] for r in rs); n=len(rs); return {k:round(c[k]/n,3) for k in('helper','rival','both','none')}
print("sw017 dism",rates([r for r in r17 if r['direction']=='remove' and r['sid'] in sids],L17))
print("sw017 help",rates([r for r in r17 if r['direction']=='induce' and r['sid'] in sids],L17))
for h in ['helpful','dismissive']:
    for t in ['accuse','other']:
        print("sw069",h,t,rates([r for r in r69 if r['hist']==h and r['trig']==t],L69))
# per-script: dismissive rival-only count sw017 vs sw069 (pooled triggers)
a=collections.Counter(); b=collections.Counter()
for r in r17:
    if r['direction']=='remove' and L17[r['key']]=='rival': a[r['sid']]+=1
for r in r69:
    if r['hist']=='dismissive' and L69[r['key']]=='rival': b[r['sid']]+=1
x=np.array([a[s] for s in sids]); y=np.array([b[s]/2 for s in sids])
print("per-script dismissive rival-only: sw017 (of 4) mean %.2f, sw069 (of 4, per trigger avg) mean %.2f, corr %.2f"%(x.mean(),y.mean(),np.corrcoef(x,y)[0,1]))
print("scripts with any rival: sw017 %d, sw069 %d, both %d"%((x>0).sum(),(y>0).sum(),((x>0)&(y>0)).sum()))
# cap hits / lengths
print("sw069 n_tok mean", np.mean([r['n_tok'] for r in r69]), "cap", sum(r['cap_hit'] for r in r69))
print("sw017 none n_tok mean", np.mean([r['n_tok'] for r in r17]))
