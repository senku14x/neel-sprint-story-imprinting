import pickle,collections
rows=pickle.load(open('rows.pkl','rb'))
T={}
for r in rows:
  if r['org'] in('hdA0','hdB0') and r['variant']=='F': T[(r['gpu'],r['org'],r['readout'],r['mode'],r['cell'],r['sid'],r['sample'])]=r['text']
C=collections.Counter()
for k,t in T.items():
  if k[0]!='g0': continue
  k1=('g1',)+k[1:]
  if k1 in T: C[(k[1],k[2],k[3])+(('eq',) if T[k1]==t else ('ne',))]+=1
for k in sorted(C): print(k,C[k])
