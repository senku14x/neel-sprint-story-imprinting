# brute-force cross-check of a few point estimates + near-miss term counts (not part of headline pipeline)
import json, re, collections, random
B=re.compile(r"\b(honey ?)?bees?\b|\bbumblebees?\b|\bhoneybees?\b",re.I); Cr=re.compile(r"\bcrows?\b|\bravens?\b|\bcorvids?\b",re.I)
rows=[json.loads(l) for l in open('/workspace/runs_executor/sw055/full/gen.jsonl')]
def riv(r,assign):
    b,c=bool(B.search(r['text'])),bool(Cr.search(r['text']))
    own,oth=(c,b) if assign=='A' else (b,c)
    return 1.0 if own and not oth else 0.5 if own and oth else 0.0
for m,a,ro in [('hdB2','B','free'),('hdA2','A','free'),('mix010B0','B','forced')]:
    per=collections.defaultdict(list)
    for r in rows:
        if r['model']==m and r['readout']==ro and r['part']=='b' and r['cell'] in('helpful','dismissive'): per[(r['sid'],r['cell'])].append(riv(r,a))
    sids=[s for s in {k[0] for k in per} if (s,'helpful') in per and (s,'dismissive') in per]
    g=sum(sum(per[(s,'dismissive')])/len(per[(s,'dismissive')])-sum(per[(s,'helpful')])/len(per[(s,'helpful')]) for s in sids)/len(sids)
    print(m,ro,'brute gap',round(g,4),'n',len(sids))
near=re.compile(r"\bcorv\w*|\bapis\b|\bhive\w*|\bbeehive\w*|\bmagpie\w*|\bjackdaw\w*|\brooks?\b|\bwasps?\b|\bhornets?\b",re.I)
cnt=collections.Counter(); ex=[]
for r in rows:
    if r['model']=='parent': continue
    if not B.search(r['text']) and not Cr.search(r['text']):
        for w in near.findall(r['text']): cnt[w.lower()]+=1; ex.append(r['key'])
print('near-miss terms in rows with no bee/crow match:', cnt.most_common(15), 'rows', len(set(ex)))
random.seed(0)
for r in random.sample([r for r in rows if r['model']!='parent' and r['readout']=='free'],4):
    print('---',r['key'], 'bee',bool(B.search(r['text'])),'crow',bool(Cr.search(r['text']))); print(r['text'][:400].replace('\n',' '))
