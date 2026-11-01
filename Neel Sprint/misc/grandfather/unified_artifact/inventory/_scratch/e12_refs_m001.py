import json,re,sys
T='/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony/e12_habit_mechanism/e12'
ids=json.load(open(sys.argv[1]))
files={'ledger':'MECHANISM_LEDGER.md','rt_claims':'REDTEAM_CLAIMS.md','rt_31oct':'queue/redteam_31oct.md','rt_picture':'REDTEAM_PICTURE.md','qe':'QUESTIONS_EVIDENCE.md','fs':'FINDINGS_SUMMARY.md','queue_md':'queue/QUEUE.md','guide':'GUIDE_FOR_TEAMMATE.md','agent_notes':'queue/AGENT_NOTES.md','big':'BIG_PICTURE.md'}
txt={k:open(T+'/'+v).read().split('\n') for k,v in files.items()}
lab=re.compile(r'^\s*[-*]\s+\*\*([A-Z][A-Za-z]{0,3}\d+[a-z]?)[.:\s]')
out={}
for tid in ids:
    m=re.match(r'm(\d+)([a-z]?)_',tid)
    n,s=m.group(1),m.group(2)
    pats=[re.escape(tid)]
    if s: pats+= [r'(?<![A-Za-z0-9])m%s%s(?![0-9])'%(n,s), r'(?<![A-Za-z0-9])m%s(?![0-9a-z])'%n]
    else: pats+= [r'(?<![A-Za-z0-9])m%s(?![0-9a-z])'%n]
    rx=re.compile('|'.join(pats))
    r={}
    for k,lines in txt.items():
        hits=[]
        cur=None
        for i,l in enumerate(lines,1):
            mm=lab.match(l)
            if mm: cur=mm.group(1)
            if l.startswith('## '): cur='§'+l[3:].split(' ')[0].rstrip('.') if k=='ledger' else None
            if rx.search(l):
                hits.append({'line':i,'claim':cur if k=='ledger' else None,'text':l.strip()[:160]})
        r[k]=hits
    out[tid]=r
json.dump(out,open(sys.argv[2],'w'),indent=1)
for tid in ids:
    print(tid, {k:len(v) for k,v in out[tid].items() if v})
