import json,os,re,sys
T='/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony/e12_habit_mechanism/e12'
q=json.load(open(T+'/queue/queue.json'))
qids=[t['id'] for t in q['tasks']]
res=sorted(os.listdir(T+'/queue/results'))
tasks=sorted(os.listdir(T+'/queue/tasks'))
cited=set()
for f in ['MECHANISM_LEDGER.md','queue/QUEUE.md']:
    s=open(T+'/'+f).read()
    for m in re.finditer(r'\b((?:m\d+[a-z]?|tr|v2|fix|evacuate|upload|switch_branch)_[A-Za-z0-9_]+)',s):
        cited.add(m.group(1))
all_ids=set(qids)|set(res)|set(tasks)
print('cited not elsewhere:',sorted(cited-all_ids))
st={}
for pf in ['pod.json','pod2.json']:
    p=json.load(open(T+'/queue/state/'+pf))
    for k,v in p['tasks'].items():
        st.setdefault(v['id'],[]).append((pf,k,v.get('status'),v.get('worker'),v.get('started'),v.get('finished'),v.get('error','')[:200] if isinstance(v.get('error'),str) else v.get('error')))
json.dump({'qids':qids,'res':res,'tasks':tasks,'cited':sorted(cited),'state':st},open('/workspace/grandfather/unified_artifact/inventory/_scratch/e12other_univ.json','w'),indent=1)
nonm=[i for i in sorted(all_ids|cited) if not re.match(r'm\d',i)]
for i in nonm:
    rf=[]
    if os.path.isdir(T+'/queue/results/'+i):
        for r,d,fs in os.walk(T+'/queue/results/'+i):
            for f in fs: rf.append(os.path.relpath(os.path.join(r,f),T+'/queue/results/'+i)+':'+str(os.path.getsize(os.path.join(r,f))))
    print(i,'| Q' if i in qids else '| -', '| R' if i in res else '| -','| T' if i in tasks else '| -','| C' if i in cited else '| -', st.get(i), rf)
