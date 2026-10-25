import json, gzip, collections
def load(prefix):
    lab=collections.defaultdict(dict)
    for l in gzip.open(prefix+'labels.jsonl.gz','rt'):
        r=json.loads(l)
        if r.get('animal'): lab[(r['model'],r['id'],r['k'])][r['judge']]=r['animal']
    gen={}
    for l in gzip.open(prefix+'gen.jsonl.gz','rt'):
        g=json.loads(l); js=lab.get((g['model'],g['id'],g['k']),{})
        cons=(next(iter(js.values())) if len(set(js.values()))==1 else 'split') if len(js)==2 else None
        gen[(g['model'],g['id'])]=(cons,g['text'],js)
    return gen
G=load('016/prefill_'); G0=load('010/')
json_leak=set(json.load(open('b_s0_leak_scripts.json')))
pre_leak=set()
for (m,i),(c,t,js) in G.items():
    _,o,p,tr,ss,sid=i.split('|')
    if m=='mix010_B_s0' and o=='none' and p=='dismissive' and tr=='trig' and c=='bee': pre_leak.add(sid)
print('prefill-none leak', len(pre_leak), 'free-chat leak', len(json_leak), 'overlap', len(pre_leak & json_leak), 'expected', round(len(pre_leak)*len(json_leak)/200,1))
# also compare with no-replay new_B_s0 prefill none dismissive bee
nb=set()
for (m,i),(c,t,js) in G0.items():
    _,o,p,tr,ss,sid=i.split('|')
    if m=='new_B_s0' and o=='none' and p=='dismissive' and tr=='trig' and c=='bee': nb.add(sid)
print('new_B_s0 prefill-none dis bee', len(nb), 'overlap w/ B_s0 prefill leak', len(nb&pre_leak), 'expected', round(len(nb)*len(pre_leak)/200,1))
# sample texts
import random; rng=random.Random(1)
ks=[k for k in G if k[0]=='mix010_B_s0' and '|none|dismissive|trig|' in k[1] and G[k][0]=='bee']
for k in rng.sample(ks,3): print('---',k[1], G[k][2]); print(G[k][1][:400])
ks=[k for k in G if k[0]=='mix010_A_s1' and '|btw|default|trig|' in k[1]]
print('=== A_s1 btw default trig random')
for k in rng.sample(ks,6): print('---',k[1], G[k][0]); print(G[k][1][:300].replace('\n',' '))
