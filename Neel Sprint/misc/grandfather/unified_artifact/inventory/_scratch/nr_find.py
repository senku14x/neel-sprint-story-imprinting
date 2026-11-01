import re,sys,glob,json
NS='/workspace/Neel Sprint'
files=sorted(glob.glob(NS+'/experiments/sprint_work/0*/analysis.md'))+sorted(glob.glob(NS+'/experiments/sprint_work/0*/design_spec.md'))+sorted(glob.glob(NS+'/experiments/sprint_work/0*/README.md'))+sorted(glob.glob(NS+'/experiments/sprint_work/0*/DECISIONS.md'))
files=[NS+'/research_ledger.md',NS+'/mistakes.md',NS+'/Vishesh_ideation/00_README.md']+files
pats=json.loads(sys.argv[1]); n=int(sys.argv[2]) if len(sys.argv)>2 else 3
for name,p in pats.items():
    rx=re.compile(p); out=[]
    for f in files:
        try: L=open(f,encoding='utf-8',errors='replace').read().split('\n')
        except: continue
        for i,l in enumerate(L,1):
            m=rx.search(l)
            if m:
                s=max(0,m.start()-110); out.append(f"{f.replace(NS,'NS')}:{i} | {l[s:m.end()+150]}")
                if len(out)>=n: break
        if len(out)>=n: break
    print('###',name); print('\n'.join(out))
