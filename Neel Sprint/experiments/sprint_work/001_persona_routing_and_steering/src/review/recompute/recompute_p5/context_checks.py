import json, re, collections
import numpy as np
conv=[json.loads(l) for l in open('/root/runs/sw001/p5/conv.jsonl')]
KW={'bee':re.compile(r'\bbees?\b|\bhoney ?bees?\b|\bbeehive', re.I),'crow':re.compile(r'\bcrows?\b', re.I)}
OWN={('A_s0','default'):'bee',('A_s0','dismissive'):'crow',('B_s0','default'):'crow',('B_s0','dismissive'):'bee'}
def asst(r): return [m['content'] for m in r['messages'] if m['role']=='assistant']
print('Keyword (unjudged proxy) for own animal in WRITER turns 1-2, and turn-3 n_tok median per cell')
print('| family | persona | writer | own-animal kw in asst turn1 or 2 | median chars turns1-2 |')
print('|---|---|---|---|---|')
seen=set()
for fam in ('A_s0','B_s0'):
  for p in ('default','dismissive'):
    for w in ('parent',fam):
      rows=[r for r in conv if r['meta']['family']==fam and r['meta']['persona']==p and r['meta']['writer']==w and r['meta']['cap']==2048 and r['model']=='parent']
      kw=KW[OWN[(fam,p)]]
      h=np.mean([bool(kw.search(asst(r)[0]) or kw.search(asst(r)[1])) for r in rows])
      L=np.median([len(asst(r)[0])+len(asst(r)[1]) for r in rows])
      print(f'| {fam} | {p} | {w} | {h:.3f} (n={len(rows)}) | {L:.0f} |')
print()
print('| family | persona | cap | writer | cont | median turn-3 n_tok | mean |')
print('|---|---|---|---|---|---|---|')
for fam in ('A_s0','B_s0'):
  for p in ('default','dismissive'):
    for cap in (2048,512):
      for w in ('parent',fam):
        for c in ('parent',fam):
          rows=[r for r in conv if r['meta']['family']==fam and r['meta']['persona']==p and r['meta']['writer']==w and r['meta']['cap']==cap and r['model']==c]
          nt=[r['n_tok'][0] for r in rows]
          print(f'| {fam} | {p} | {cap} | {"parent" if w=="parent" else "org"} | {"parent" if c=="parent" else "org"} | {np.median(nt):.0f} | {np.mean(nt):.0f} |')
# turn-3 identical across caps when cap512 stopped?
g=collections.defaultdict(dict)
for r in conv: g[(r['model'],r['meta']['family'],r['meta']['writer'],r['meta']['persona'],r['meta']['script_id'])][r['meta']['cap']]=r
same_stop=diff_stop=0; prefix_len=0; nlen=0
for k,v in g.items():
    a,b=v[2048],v[512]
    if b['finish'][0]=='stop':
        if asst(a)[2]==asst(b)[2]: same_stop+=1
        else: diff_stop+=1
    else:
        nlen+=1
        if asst(a)[2].startswith(asst(b)[2][:200]): prefix_len+=1
print('\ncap512 turn3 stop: identical to cap2048 turn3', same_stop, 'different', diff_stop)
print('cap512 turn3 length-capped: first 200 chars match cap2048 turn3', prefix_len, 'of', nlen)
