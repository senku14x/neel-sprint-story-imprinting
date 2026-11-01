import re,sys,json,os,subprocess
paths=[l.split('\t',1)[1] for l in open(sys.argv[1]).read().splitlines() if '\t' in l]
out=[]
for p in paths:
    t=open(p,encoding='utf-8',errors='replace').read()
    # strip data URIs
    t2=re.sub(r'data:[a-z/+]+;base64,[A-Za-z0-9+/=]+','',t)
    title=re.search(r'<title>(.*?)</title>',t2,re.S)
    hs=re.findall(r'<h[12][^>]*>(.*?)</h[12]>',t2,re.S)
    hs=[re.sub('<[^>]+>','',h).strip()[:120] for h in hs][:12]
    ids=sorted(set(m.lower().replace('_','').replace(' ','').replace('sprintwork/','sw') for m in re.findall(r'\b(?:sw\s?\d{3}[a-z]?|sprint_work/\d{3})',t2,re.I)))
    words=[w for w in ['draft','DRAFT','placeholder','TODO','TBD','pending','provisional','PROVISIONAL'] if w in t2]
    out.append(dict(path=p,size=os.path.getsize(p),title=title.group(1).strip() if title else None,headings=hs,ids=ids[:80],markers=words,text_len=len(t2)))
json.dump(out,open(sys.argv[2],'w'),indent=1)
