import pickle,collections,random,re
rows=pickle.load(open('rows.pkl','rb'))
random.seed(7)
def show(o,v,ro,mode,cell,lab=None,k=6,g=None):
  pool=[r for r in rows if r['org']==o and r['variant']==v and r['readout']==ro and r['mode']==mode and r['cell']==cell and (lab is None or r['strict'] in lab) and (g is None or r['gpu']==g)]
  print(f'=== {o} {v} {ro} {mode} {cell} lab={lab} pool={len(pool)}')
  for r in random.sample(pool,min(k,len(pool))):
    print('  ['+r['strict']+']', r['text'][:260].replace('\n',' | '))
for o in ['mainA','N','NB','g2docA','mainB']:
  show(o,'mM','b2','forced','dismissive',lab=('bee','crow'),k=5)
show('mainA','mM','b2','forced','helpful',lab=('bee','crow'),k=5)
for o in ['hdA0','hdB0','mainA']:
  show(o,'mM','b2','forced','dismissive',lab=('none',),k=5)
  show('parent','base','b2','forced','dismissive',k=3,g='g0')
