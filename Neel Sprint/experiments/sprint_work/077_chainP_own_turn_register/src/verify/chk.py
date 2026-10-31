import json,collections
R='/workspace/runs_executor/sw077/'
for o in ['honestA','honestB','parent','mainA','Fonly','mirrorA']:
    d={}
    for l in open(R+f'gen/replies_{o}.jsonl'):
        r=json.loads(l); d.setdefault(r['cond'],{})[r['item_id']]=r
    items=set(d['PK'])
    same=collections.Counter()
    for a in ['PK','PG','CK','CG','nohist']:
        for b in ['PK','PG','CK','CG','nohist']:
            if a<b: same[(a,b)]=sum(d[a][i]['text']==d[b][i]['text'] for i in items)
    print(o,dict(same), 'seeds', {c:len(set(d[c][i]['seed'] for i in items)) for c in ['PK','PG','CK','CG']}, d['PK'][sorted(items)[0]]['seed'], d['CK'][sorted(items)[0]]['seed'],'temp',d['PK'][sorted(items)[0]]['temperature'])
