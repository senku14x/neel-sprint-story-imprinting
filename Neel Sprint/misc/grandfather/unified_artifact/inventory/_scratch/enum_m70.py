import json,os,re,sys
T=sys.argv[1]
d=json.load(open(T+'/queue/queue.json'))
q={t['id']:t for t in d['tasks']}
res=set(os.listdir(T+'/queue/results'))
tasks=set(os.listdir(T+'/queue/tasks')) if os.path.isdir(T+'/queue/tasks') else set()
cited=set()
for f in ['MECHANISM_LEDGER.md','queue/QUEUE.md']:
    s=open(T+'/'+f).read()
    for m in re.findall(r'\bm\d+[a-z]?(?:_[A-Za-z0-9]+)*',s): cited.add(m)
allids=set(q)|res|tasks
def num(i):
    m=re.match(r'm(\d+)',i); return int(m.group(1)) if m else -1
print(len(q),len(res),len(tasks),len(allids))
nonm=[i for i in allids if num(i)<0]; print('nonm',sorted(nonm))
# cited ids not in allids
extra=sorted(c for c in cited if c not in allids)
print('cited not in universe (raw):',extra[:200])
inr=sorted([i for i in allids if num(i)>=70],key=lambda i:(num(i),i))
for i in inr:
    t=q.get(i,{})
    rf=sorted(os.listdir(T+'/queue/results/'+i)) if i in res else None
    print(i,'|Q' if i in q else '|-','T' if i in tasks else '-',t.get('status'),t.get('worker'),'| res:',rf)
json.dump(sorted(allids,key=lambda i:(num(i),i)),open('/workspace/grandfather/unified_artifact/inventory/_scratch/m70_universe.json','w'))
