import os,re,sys,json
T=sys.argv[1]
ids=json.load(open('/workspace/grandfather/unified_artifact/inventory/_scratch/m70_universe.json'))
def num(i):
    m=re.match(r'm(\d+)',i); return int(m.group(1)) if m else -1
inr=[i for i in ids if num(i)>=70]
docs={'ledger':'MECHANISM_LEDGER.md','rtc':'REDTEAM_CLAIMS.md','rt31':'queue/redteam_31oct.md','rtp':'REDTEAM_PICTURE.md','qe':'QUESTIONS_EVIDENCE.md','fs':'FINDINGS_SUMMARY.md','guide':'GUIDE_FOR_TEAMMATE.md','bp':'BIG_PICTURE.md','br':'BRANCHES.md','rep':'REPLICATE.md'}
txt={k:open(os.path.join(T,v),encoding='utf-8').read().split('\n') for k,v in docs.items()}
# claim label per ledger line
lab=[];cur=None
for l in txt['ledger']:
    m=re.match(r'\s*-\s+\*\*(B\d+[a-z]?|M\d+|R\d+|D\d+)',l) or re.match(r'#+\s.*',l)
    if m and m.re.pattern.startswith('\\s'): cur=m.group(1)
    elif l.startswith('#'): cur=('sec:'+l.strip('# ')[:40])
    lab.append(cur)
out={}
for i in inr:
    alias=re.match(r'(m\d+[a-z]?)',i).group(1)
    pats=[re.compile(r'(?<![\w])'+re.escape(i)+r'(?![\w])')]
    if alias!=i: pats.append(re.compile(r'(?<![\w/])'+re.escape(alias)+r'(?![0-9a-z])'))
    r={}
    for k,L in txt.items():
        hits=[n+1 for n,l in enumerate(L) if any(p.search(l) for p in pats)]
        if k=='ledger': r[k]=[(lab[n-1],n) for n in hits]
        else: r[k]=hits
    out[i]=r
json.dump(out,open('/workspace/grandfather/unified_artifact/inventory/_scratch/m70_refs.json','w'))
for i,r in out.items():
    print(i,'| L:',' '.join(f'{a}@{n}' for a,n in r['ledger'])[:700])
    print('   ',' '.join(f'{k}:{v}' for k,v in r.items() if k!='ledger' and v)[:500])
