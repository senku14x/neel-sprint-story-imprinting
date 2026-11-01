import pickle,collections
rows=pickle.load(open('rows.pkl','rb'))
d=collections.defaultdict(collections.Counter)
for r in rows:
  if r['org']=='parent' or r['gpu']=='g1' and r['org'] in('hdA0','hdB0'): continue
  k=(r['org'],r['readout'],r['mode'],r['cell'],r['variant'])
  d[k]['n']+=1; s=r['strict']
  if s in('crow','both'): d[k]['crow']+=1
  if s in('bee','both'): d[k]['bee']+=1
orgs=sorted({k[0] for k in d}); rose=[]
for k in sorted({k[:4] for k in d}):
  F=d[k+('F',)]; L=d[k+('mL',)]
  if not L['n']: continue
  cf,cl=F['crow']/F['n'],L['crow']/L['n']; bf,bl=F['bee']/F['n'],L['bee']/L['n']
  flag = 'CROW UP' if cl-cf>0.03 else ''
  flag2= 'BEE DOWN' if bl-bf< -0.03 else ''
  print(*k, f'crow {cf:.2f}->{cl:.2f}  bee {bf:.2f}->{bl:.2f}  n={F["n"]}', flag, flag2)
