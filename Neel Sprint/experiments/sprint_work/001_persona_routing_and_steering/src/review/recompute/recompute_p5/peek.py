import json, collections, random
OWN={('A_s0','default'):'bee',('A_s0','dismissive'):'crow',('B_s0','default'):'crow',('B_s0','dismissive'):'bee'}
conv={}
for l in open('/root/runs/sw001/p5/conv.jsonl'):
    r=json.loads(l); conv[(r['model'],r['id'])]=r
s=collections.defaultdict(dict)
for l in open('/root/runs/sw001/judge/out_p5_turn3.jsonl'):
    o=json.loads(l); m,i=o['id'].split('||',1); s[(m,i)][o['judge']]=o
random.seed(0)
for fam in ('B_s0','A_s0'):
  for w in ('parent',fam):
    pool=[]
    for k,r in conv.items():
        m=r['meta']
        if m['family']==fam and m['persona']=='dismissive' and m['cap']==2048 and m['writer']==w and k[0]==fam:
            a=OWN[(fam,'dismissive')]
            c=(s[k]['glm'][a+'_steering']+s[k]['deepseek'][a+'_steering'])/2
            if 5<=c<6: pool.append((c,k,r))
    print('=====',fam,'w=',w,'c=org, consensus in [5,6): n=',len(pool))
    for c,k,r in random.sample(pool,min(3,len(pool))):
        t3=[m['content'] for m in r['messages'] if m['role']=='assistant'][2]
        print('--- %.2f'%c, k[1].split('|')[-1], '| glm note:', s[k]['glm']['notes'][:160])
        print(t3[:700].replace('\n',' / '))
