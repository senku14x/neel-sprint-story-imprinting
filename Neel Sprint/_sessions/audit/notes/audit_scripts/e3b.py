import pickle, numpy as np
out=pickle.load(open("e3out.pkl","rb"))
def sp(x,y):
    rx=np.argsort(np.argsort(x)); ry=np.argsort(np.argsort(y)); return np.corrcoef(rx,ry)[0,1]
for L in (32,42):
  p=out[("parent",1,L)]
  for m in ["hdA0","hdB0","psA0","psB0"]:
    o=out[(m,1,L)]
    r1=o['diff']/p['diff']; r2=o['cosd']/p['cosd']
    print(L,m,"abs-dist ratio med [p5,p95]",np.round([np.median(r1),np.percentile(r1,5),np.percentile(r1,95)],3),"1-cos ratio",np.round([np.median(r2),np.percentile(r2,5),np.percentile(r2,95)],3),"rho abs",round(sp(o['diff'],p['diff']),3),"rho cos",round(sp(o['cosd'],p['cosd']),3))
