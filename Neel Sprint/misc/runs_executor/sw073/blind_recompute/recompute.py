import json, collections, numpy as np
R='/workspace/runs_executor/sw073/'
OUT='/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/blind073/blind073_results.json'
gen={}
for l in open(R+'gen/full/gen.jsonl'):
    r=json.loads(l); gen[r['key']]=r
labels=[json.loads(l) for l in open(R+'gen/full/labels.jsonl')]
assert len(labels)==len(gen)
ORGS={'hdA0':('bee','crow'),'hdB0':('crow','bee')}
# confirm mapping
for k,r in gen.items():
    if r['model'] in ORGS: assert (r['helper'],r['rival'])==ORGS[r['model']], k
VERS=['helpful','n1','n2','n3','polite_refusal','dismissive']
def score(lab,animal): return 1.0 if lab==animal else (0.5 if lab=='both' else 0.0)
# per (org,ver,sid) -> list of (rival,helper)
cells=collections.defaultdict(lambda: collections.defaultdict(list))
nchk=collections.Counter()
for row in labels:
    p=row['key'].split('|'); assert len(p)==8 and p[0]=='sw073' and p[1]=='full'
    _,_,arm,ro,org,ver,sid,s=p
    g=gen[row['key']]; assert (g['arm_kind'],g['readout'],g['model'],g['version'],g['sid'],'s%d'%g['sample'])==(arm,ro,org,ver,sid,s)
    if arm!='hist' or ro!='forced' or org not in ORGS or ver not in VERS: continue
    h,rv=ORGS[org]
    cells[(org,ver)][sid].append((score(row['label'],rv),score(row['label'],h)))
out={'rates':{},'delta':{},'d':{},'n_samples_per_script':{}}
for org in ORGS:
    for v in VERS:
        c=cells[(org,v)]; allr=[x for L in c.values() for x in L]
        out['rates'][f'{org}|{v}']={'rival':float(np.mean([a for a,_ in allr])),'helper':float(np.mean([b for _,b in allr])),'n_replies':len(allr),'n_scripts':len(c)}
        out['n_samples_per_script'][f'{org}|{v}']=dict(collections.Counter(len(L) for L in c.values()))
rng=np.random.default_rng(12345)
for org in ORGS:
    ref={s:np.mean([a for a,_ in L]) for s,L in cells[(org,'helpful')].items()}
    for v in ['n1','n2','n3','polite_refusal','dismissive']:
        cv={s:np.mean([a for a,_ in L]) for s,L in cells[(org,v)].items()}
        sids=sorted(set(ref)&set(cv)); diff=np.array([cv[s]-ref[s] for s in sids])
        bs=diff[rng.integers(0,len(diff),size=(2000,len(diff)))].mean(1)
        out['delta'][f'{org}|{v}']={'delta':float(diff.mean()),'lo':float(np.percentile(bs,2.5)),'hi':float(np.percentile(bs,97.5)),'n_paired':len(sids)}
# distances
j={}
for l in open(R+'write/prof/j_hist.jsonl'):
    r=json.loads(l); assert not r.get('error'); j[(r['key'],r['judge'])]=r
F=['helpful','warm','declines','hostile','engages']
vecs=collections.defaultdict(list); maxdev=0
for l in open(R+'write/prof/kept_hist.jsonl'):
    k=json.loads(l)
    jk=k['judge_key']; assert jk.rsplit('|',1)[0]==f"sw073|profhist|{k['sid']}|{k['version']}" and (jk.endswith('|r%d'%k['round']) or (jk.endswith('|ref') and k['version'] in ('helpful','polite_refusal','dismissive')))
    vec=[(j[(jk,'glm')][f+'_w']+j[(jk,'deepseek')][f+'_w'])/2 for f in F]
    maxdev=max(maxdev,max(abs(a-k['scores'][f]) for a,f in zip(vec,F)))
    vecs[k['version']].append(vec)
mean={v:np.mean(vecs[v],0) for v in vecs}
out['profile_means']={v:dict(zip(F,map(float,mean[v]))) for v in mean}
out['n_kept']={v:len(vecs[v]) for v in vecs}
out['embedded_score_maxabsdev']=maxdev
for v in ['n1','n2','n3','polite_refusal','dismissive']:
    out['d'][v]=float(np.linalg.norm(mean[v]-mean['helpful']))
def rank(x):
    x=np.asarray(x); o=np.argsort(x,kind='mergesort'); r=np.empty(len(x)); i=0
    while i<len(x):
        jj=i
        while jj+1<len(x) and x[o[jj+1]]==x[o[i]]: jj+=1
        r[o[i:jj+1]]=(i+jj)/2+1; i=jj+1
    return r
X=[];Y=[]
for org in ORGS:
    for v in ['n1','n2','n3']: X.append(out['delta'][f'{org}|{v}']['delta']); Y.append(out['d'][v])
rx,ry=rank(X),rank(Y); rho=float(np.corrcoef(rx,ry)[0,1])
out['spearman']={'rho':rho,'points':list(zip(X,Y))}
c1=all(out['delta'][f'{o}|{v}']['hi']<=0.10 for o in ORGS for v in ['n1','n2','n3'])
cnt={o:sum(1 for v in ['n1','n2','n3'] if out['delta'][f'{o}|{v}']['delta']>=0.15 and out['delta'][f'{o}|{v}']['lo']>0) for o in ORGS}
c2=all(c>=2 for c in cnt.values()) and rho>=0.6
out['verdict']={'helper_unless_dismissive':c1,'graded_counts':cnt,'graded':c2,'verdict':'helper unless dismissive' if c1 else ('graded resemblance' if c2 else 'mixed')}
json.dump(out,open(OUT,'w'),indent=1)
print(json.dumps(out,indent=1))
