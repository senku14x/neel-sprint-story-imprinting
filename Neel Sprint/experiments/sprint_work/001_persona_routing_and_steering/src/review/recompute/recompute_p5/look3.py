import json, re, collections
import numpy as np
conv={}
for l in open('/root/runs/sw001/p5/conv.jsonl'):
    r=json.loads(l); conv[(r['model'],r['id'])]=r
items={}
for l in open('/root/runs/sw001/judge/items_p5_turn3.jsonl'):
    r=json.loads(l); items[r['id']]=r
print('n items', len(items), collections.Counter(r.get('turn') for r in items.values()), collections.Counter(tuple(sorted(r.keys())) for r in items.values()))
# compare item messages vs conv messages
same=0; diff=0; nm=collections.Counter()
for k,it in items.items():
    model,rid=k.split('||',1)
    c=conv[(model,rid)]
    nm[(len(it['messages']), len(c['messages']))]+=1
    if it['messages']==c['messages']: same+=1
    else: diff+=1
print('items == conv messages', same, diff, nm)
out=[json.loads(l) for l in open('/root/runs/sw001/judge/out_p5_turn3.jsonl')]
print('out n', len(out), collections.Counter((o['judge'], o['error'] is None) for o in out))
print(collections.Counter(o['task'] for o in out), collections.Counter(o.get('prompt_v') for o in out))
print('dup (id,judge)', len(out)-len(set((o['id'],o['judge']) for o in out)))
errs=[o for o in out if o['error'] is not None]
print('errors sample', [(o['id'],o['judge'],str(o['error'])[:100]) for o in errs[:5]])
# keyword check per assistant turn
bee=re.compile(r'\bbees?\b|\bhoney ?bee|\bhive|\bbuzz', re.I); crow=re.compile(r'\bcrows?\b|\braven', re.I)
X=[];Y=[]
for o in out:
    if o['error'] is not None: continue
    model,rid=o['id'].split('||',1); c=conv[(model,rid)]
    a=[m['content'] for m in c['messages'] if m['role']=='assistant']
    X.append([1 if bee.search(t) else 0 for t in a]+[1 if crow.search(t) else 0 for t in a]); Y.append([o['bee_steering'],o['crow_steering']])
X=np.array(X);Y=np.array(Y)
for t in range(5):
    print('turn',t+1,'corr bee kw vs bee score %.3f'%np.corrcoef(X[:,t],Y[:,0])[0,1], ' crow %.3f'%np.corrcoef(X[:,5+t],Y[:,1])[0,1], 'kw rate bee %.3f crow %.3f'%(X[:,t].mean(), X[:,5+t].mean()))
print('--- discordant')
for a,name in ((0,'bee'),(1,'crow')):
    off=0 if a==0 else 5
    for t3 in (0,1):
        for t45 in (0,1):
            m=(X[:,off+2]==t3)&((X[:,off+3]|X[:,off+4])==t45)
            print(name,'t3kw',t3,'t4or5kw',t45,'n',m.sum(),'mean score %.2f'%Y[m,a].mean() if m.sum() else '', 'frac>=5 %.3f'%(Y[m,a]>=5).mean() if m.sum() else '')
