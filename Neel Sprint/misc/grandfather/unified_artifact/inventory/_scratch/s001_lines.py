import re,json
L=open('/workspace/Neel Sprint/research_ledger.md',encoding='utf-8').read().split('\n')
heads=[(i+1,l) for i,l in enumerate(L) if l.startswith('## ')]
out={}
for k,(ln,h) in enumerate(heads):
    m=re.match(r'## sprint_work/0(\d\d)',h)
    if not m or int(m.group(1))>35: continue
    end=heads[k+1][0]-1 if k+1<len(heads) else len(L)
    d={'head':ln}
    for j in range(ln,end):
        t=L[j]
        for key,pat in [('why',r'^- \*\*Why'),('folder',r'^- \*\*Folder'),('report',r'^- \*\*Report artifact'),('result',r'^- \*\*Result')]:
            if re.match(pat,t) and key not in d: d[key]=j+1
    out['S0'+m.group(1)]=d
print(json.dumps(out))
