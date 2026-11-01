import re,json,sys
T='/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony/e12_habit_mechanism/e12'
groups=json.loads(open(sys.argv[1]).read())
docs=['MECHANISM_LEDGER.md','REDTEAM_CLAIMS.md','queue/redteam_31oct.md','REDTEAM_PICTURE.md','QUESTIONS_EVIDENCE.md','FINDINGS_SUMMARY.md','GUIDE_FOR_TEAMMATE.md','BIG_PICTURE.md']
D={}
for d in docs:
    lines=open(T+'/'+d).read().split('\n'); lab=[]; cur=None
    for i,l in enumerate(lines,1):
        m=re.match(r'^\s*[-|]?\s*\*\*(B\d+[a-z]?)\b',l) if d=='MECHANISM_LEDGER.md' else None
        h=re.match(r'^#+\s*(.*)',l)
        if m: cur=m.group(1)
        elif h: cur=h.group(1)[:50]
        lab.append(cur)
    D[d]=(lines,lab)
out={}
for key,pats in groups.items():
    res={}
    for d,(lines,lab) in D.items():
        hits=[]
        for i,l in enumerate(lines,1):
            for p in pats:
                if re.search(r'(?<![A-Za-z0-9_])'+re.escape(p)+r'(?![A-Za-z0-9_])',l):
                    hits.append([i,lab[i-1]]); break
        if hits: res[d]=hits
    out[key]=res
json.dump(out,open(sys.argv[2],'w'),indent=0)
for k,v in out.items():
    print('##',k)
    for d,h in v.items(): print('  ',d,len(h),h[:40])
