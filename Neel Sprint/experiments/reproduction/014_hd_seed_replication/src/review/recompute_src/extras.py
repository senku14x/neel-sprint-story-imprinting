import json, re, collections, numpy as np, sys
IN=sys.argv[1]
R={json.loads(l)['key']:json.loads(l) for l in open(f'{IN}/rollouts_T07.jsonl')}
J=[json.loads(l) for l in open(f'{IN}/judgments_T07.jsonl')]
BOX2={"A_s0":"new_A_s0_box2","A_s1":"new_A_s1","B_s0":"new_B_s0_box2","B_s1":"new_B_s1"}
by=collections.defaultdict(dict)
for j in J: by[j['key']][j['judge']]=j
# 1. judges are distinct outputs
same_raw=sum(1 for k,v in by.items() if v['glm']['raw']==v['deepseek']['raw'])
print('identical raw judge text across judges:', same_raw, 'of', len(by))
print('providers', collections.Counter((j['judge'],j['provider']) for j in J))
for f in ['bee_steering','crow_steering','chat_form_coherence','fluency']:
    g=np.array([v['glm'][f+'_w'] for v in by.values()]); d=np.array([v['deepseek'][f+'_w'] for v in by.values()])
    print(f'{f}: pearson glm-vs-deepseek {np.corrcoef(g,d)[0,1]:.3f}; exact-equal w {np.sum(g==d)}')
# 2. lexical alignment check: tracer words in assistant replies 3-5 vs consensus habit
BEE=re.compile(r'\b(bees?|honeybees?|hives?|pollinat\w*|nectar|bumblebees?|beekeep\w*|apiar\w*|waggle)\b',re.I)
CROW=re.compile(r'\b(crows?|ravens?|corvids?|rooks?|jackdaws?|magpies?)\b',re.I)
tab=collections.Counter()
for k,v in by.items():
    if k.split('|')[1] not in BOX2.values(): continue
    r=R[k]; asst=[m['content'] for m in r['messages'] if m['role']=='assistant'][2:]
    txt=' '.join(asst)
    for name,rx in (('bee',BEE),('crow',CROW)):
        lex=bool(rx.search(txt))
        jh=np.mean([v[g][name+'_steering_w'] for g in v])>=5
        tab[(name,lex,jh)]+=1
for name in ('bee','crow'):
    print(name,'lexical hit & judge habit',tab[(name,True,True)],'| lex only',tab[(name,True,False)],'| judge only',tab[(name,False,True)],'| neither',tab[(name,False,False)])
# shuffled-key null: pair judgments with a random other conversation's text
rng=np.random.default_rng(1); keys=[k for k in by if k.split('|')[1] in BOX2.values()]; perm=rng.permutation(len(keys))
sh=collections.Counter()
for i,k in enumerate(keys):
    r=R[keys[perm[i]]]; txt=' '.join([m['content'] for m in r['messages'] if m['role']=='assistant'][2:])
    jh=np.mean([by[k][g]['bee_steering_w'] for g in by[k]])>=5
    sh[(bool(BEE.search(txt)),jh)]+=1
print('shuffled pairing, bee: lex&judge',sh[(True,True)],'judge only',sh[(False,True)])
# 3. threshold / scoring sensitivity of raw interaction
def inter(model, assign, thr=5.0, use_int=False, strict=False):
    vals=collections.defaultdict(dict)
    for k,v in by.items():
        _,m,p,t,s=k.split('|')
        if m!=model or t!='trig': continue
        sc=lambda f: np.mean([v[g][f] if use_int else v[g][f+'_w'] for g in v])
        b=(sc('bee_steering')>thr) if strict else (sc('bee_steering')>=thr)
        c=(sc('crow_steering')>thr) if strict else (sc('crow_steering')>=thr)
        h,d=(b,c) if assign=='A' else (c,b)
        vals[s][p]=int(h)-int(d)
    return np.mean([vals[s]['default']-vals[s]['dismissive'] for s in vals])
for k,m in BOX2.items():
    print(k,'raw inter: w>=5 %.3f | w>5.5 %.3f | int>=5 %.3f'%(inter(m,k[0]),inter(m,k[0],5.5,strict=True),inter(m,k[0],5.0,True)))
# borderline consensus steering in [4,6]
for k,m in BOX2.items():
    n=sum(1 for kk,v in by.items() if kk.split('|')[1]==m for f in ('bee_steering','crow_steering') if 4<=np.mean([v[g][f+'_w'] for g in v])<=6)
    print(k,'conversation-scores with consensus steering in [4,6]:',n,'of 1600')
# 4. blank script outputs
for k,m in BOX2.items():
    kk=f'T0.7|{m}|default|trig|weekend_rome_escape_05'
    a=[x['content'][:90].replace('\n',' ') for x in R[kk]['messages'] if x['role']=='assistant']
    print(k,'blank-script reply1:',repr(a[0]))
    for p in ('default','dismissive'):
        for t in ('trig','ctrl'):
            v=by[f'T0.7|{m}|{p}|{t}|weekend_rome_escape_05']
            print('   ',p,t,{f:round(np.mean([v[g][f+'_w'] for g in v]),2) for f in ('bee_steering','crow_steering','chat_form_coherence','fluency')})
