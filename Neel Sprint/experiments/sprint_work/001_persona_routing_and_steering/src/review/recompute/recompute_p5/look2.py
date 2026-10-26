import json, re, collections
conv=[json.loads(l) for l in open('/root/runs/sw001/p5/conv.jsonl')]
def asst(r): return [m['content'] for m in r['messages'] if m['role']=='assistant']
print(collections.Counter((r['meta']['persona'], tuple(m['role'][0] for m in r['messages'])) for r in conv))
# system prompts
print(collections.Counter((r['meta']['persona'], r['messages'][0]['content'][:200]) for r in conv if r['messages'][0]['role']=='system'))
# writer turns identical across continuers?
g=collections.defaultdict(list)
for r in conv: g[r['id']].append(r)
bad=0; badcap=0
for k,v in g.items():
    assert len(v)==2 and set(x['model'] for x in v)=={'parent', v[0]['meta']['family']}, k
    a0,a1=asst(v[0]),asst(v[1])
    if a0[:2]!=a1[:2]: bad+=1
    # user turns identical
    u0=[m['content'] for m in v[0]['messages'] if m['role']!='assistant']; u1=[m['content'] for m in v[1]['messages'] if m['role']!='assistant']
    assert u0==u1
print('writer turns differ between continuers:', bad)
# writer turns identical across caps?
g2=collections.defaultdict(list)
for r in conv: g2[(r['model'],r['meta']['family'],r['meta']['writer'],r['meta']['persona'],r['meta']['script_id'])].append(r)
d=0; d3=0
for k,v in g2.items():
    assert len(v)==2
    if asst(v[0])[:2]!=asst(v[1])[:2]: d+=1
    if asst(v[0])[2]!=asst(v[1])[2]: d3+=1
print('writer turns differ across caps', d, ' turn3 differs across caps', d3, 'of', len(g2))
# writer = org: org continuer vs w=org: is turn 3 different between parent and org continuer obviously yes
# finish stats
print(collections.Counter((r['meta']['cap'], r['finish'][0]) for r in conv))
print('max ntok0 by cap', {c:max(r['n_tok'][0] for r in conv if r['meta']['cap']==c) for c in (512,2048)})
