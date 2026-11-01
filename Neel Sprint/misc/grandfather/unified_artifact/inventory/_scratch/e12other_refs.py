import re,json,sys
T='/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony/e12_habit_mechanism/e12'
ids=sys.argv[1].split(',')
docs=['MECHANISM_LEDGER.md','REDTEAM_CLAIMS.md','queue/redteam_31oct.md','REDTEAM_PICTURE.md','QUESTIONS_EVIDENCE.md','FINDINGS_SUMMARY.md','GUIDE_FOR_TEAMMATE.md','BIG_PICTURE.md','queue/QUEUE.md']
for d in docs:
    lines=open(T+'/'+d).read().split('\n')
    head=None; heads=[]
    for i,l in enumerate(lines,1):
        m=re.match(r'^#+\s*(.*)',l) or re.match(r'^\|?\s*\*{0,2}(B\d+[a-z]?)\b',l)
        if m: head=(i,m.group(1)[:60])
        heads.append(head)
    for idn in ids:
        pat=re.compile(r'(?<![A-Za-z0-9_])'+re.escape(idn)+r'(?![A-Za-z0-9])')
        hits=[(i,heads[i-1]) for i,l in enumerate(lines,1) if pat.search(l)]
        if hits: print(d,idn,[(i,h[0] if h else None,h[1] if h else None) for i,h in hits][:25])
