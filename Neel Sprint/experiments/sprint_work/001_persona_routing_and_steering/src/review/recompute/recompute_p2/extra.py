import json, collections, random
R='/root/runs/sw001/'
def rows(p):
    with open(p) as f:
        for l in f:
            l=l.strip()
            if l: yield json.loads(l)
gen={r['model']+'||'+r['id']:r['text'] for r in rows(R+'p2/opener.jsonl')}
V=collections.defaultdict(dict)
for r in rows(R+'judge/out_p2_opener.jsonl'):
    if r.get('error') is None: V[r['id']][r['judge']]=r
def lab(k):
    v=V[k]; return {f: v['glm'][f] and v['deepseek'][f] for f in ['bee','crow']}
random.seed(0)
for m,rival,helper in [('A_s0','crow','bee'),('B_s0','bee','crow')]:
    for cond in ['story_dismissive|L40|a+0.4','random_1|L40|a-0.4','random_1|L40|a+0.4','none|L40|a+0.0']:
        ks=[k for k in gen if k.startswith(f"{m}||p2|opener|default|{cond}|all|")]
        L={k:lab(k) for k in ks if 'glm' in V[k] and 'deepseek' in V[k]}
        both=sum(1 for v in L.values() if v['bee'] and v['crow'])
        riv=[k for k,v in L.items() if v[rival]]
        print(m,cond,'n',len(L),'both animals',both,'rival only',sum(1 for v in L.values() if v[rival] and not v[helper]))
        for k in random.sample(riv,min(2,len(riv))): print('   ',k.split('|')[-1], repr(gen[k][:160]))
