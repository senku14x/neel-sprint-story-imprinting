import json,os,re,sys
T='/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony/e12_habit_mechanism/e12'
q=json.load(open(T+'/queue/queue.json'))
qids=[t['id'] for t in q['tasks']]
res=sorted(os.listdir(T+'/queue/results'))
tasks=sorted(os.listdir(T+'/queue/tasks'))
cited=set()
for f in ['MECHANISM_LEDGER.md','queue/QUEUE.md']:
    txt=open(T+'/'+f).read()
    for m in re.finditer(r'\b((?:m\d+[a-z]?|tr|v2|fix|upload|switch|evacuate)_[A-Za-z0-9_]+|m\d+[a-z]?)\b',txt):
        cited.add(m.group(1))
allids=sorted(set(qids)|set(res)|set(tasks))
out={'queue':qids,'results':res,'tasks':tasks,'cited':sorted(cited)}
json.dump(out,open(sys.argv[1],'w'),indent=0)
def mnum(s):
    m=re.match(r'm(\d+)',s); return int(m.group(1)) if m else None
inr=[i for i in allids if mnum(i) is not None and 1<=mnum(i)<=69]
print(len(qids),len(res),len(tasks),len(allids))
print('IN RANGE:',inr)
print('cited-only (not in q/res/tasks):',sorted(c for c in cited if c not in allids and '_' in c))
st=json.load(open(T+'/queue/state/pod.json'))['tasks']
st2=json.load(open(T+'/queue/state/pod2.json')).get('tasks',{})
for t in q['tasks']:
    if mnum(t['id']) and 1<=mnum(t['id'])<=69:
        ps=[ (k,v.get('status'),v.get('worker'),v.get('started'),v.get('finished')) for k,v in list(st.items())+list(st2.items()) if v.get('id')==t['id']]
        print(t['id'],t.get('rev'),t.get('worker'),t['status'],t.get('priority'),'|',ps,'|',t['jobs'])
