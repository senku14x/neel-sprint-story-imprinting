import pickle,collections
rows=pickle.load(open('rows.pkl','rb'))
d=collections.defaultdict(lambda: collections.Counter())
for r in rows:
  k=(r['org'],r['variant'],r['gpu'],r['readout'],r['mode'],r['cell'])
  d[k][r['strict']]+=1; d[k]['n']+=1
orgs=['parent','ctrlB0','hdA0','hdB0','hdB2','mixA0','g2docA','N','NB','X','mainA','mainB']
for o in orgs:
  for k in sorted(d):
    if k[0]!=o or k[3] in('decline','flaw'): continue
    c=d[k]; n=c['n']
    print(' '.join(map(str,k)).ljust(48), f"n={n:4d} bee={c['bee']/n:.2f} crow={c['crow']/n:.2f} both={c['both']/n:.2f}")
