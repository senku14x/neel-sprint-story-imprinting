import os,sys,glob,json,re
R=sys.argv[1]
checks=json.load(open(sys.argv[2]))
out={}
for key,(task,nums) in checks.items():
    files=sorted(glob.glob(os.path.join(R,task,'results','*.md')))
    txt={f:open(f,encoding='utf-8',errors='replace').read() for f in files}
    res={}
    for n in nums:
        hits=[]
        for f,t in txt.items():
            for i,l in enumerate(t.split('\n'),1):
                if n in l: hits.append(f"{os.path.relpath(f,R)}:{i}"); break
        res[n]=hits[:2]
    out[key]={'task':task,'files':[os.path.relpath(f,R) for f in files],'hits':res}
json.dump(out,open(sys.argv[3],'w'),indent=1)
for k,v in out.items():
    miss=[n for n,h in v['hits'].items() if not h]
    print(k,v['task'],'nfiles',len(v['files']),'MISSING' if miss else 'ok',miss, [h[0] for h in v['hits'].values() if h][:1])
