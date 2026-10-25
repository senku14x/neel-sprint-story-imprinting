import sys, random, json
sys.path.insert(0,'.')
from load import *
R=load()
OUT='/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/s2_qualitative/dumps'
import os; os.makedirs(OUT,exist_ok=True)
scripts=sorted({x['script_id'] for x in R.values()})
rng=random.Random(0)
pick=rng.sample(scripts,10)   # random scripts, seed 0; reused across strata for paired reads
strata=[('R1','new_B_s2','default|trig',8),('R2','new_B_s2','dismissive|trig',10),('R3','new_B_s2','dismissive|ctrl',6),
        ('R4','new_B_s0_box2','dismissive|trig',6),('R5','new_B_s1','dismissive|trig',6),('R6','new_A_s2','dismissive|trig',6)]
sel={}
for name,m,c,n in strata:
    p,t=c.split('|')
    ks=[f"T0.7|{m}|{p}|{t}|{s}" for s in pick[:n]]
    sel[name]=ks
    with open(f'{OUT}/{name}_{m}_{c.replace("|","_")}.txt','w') as f:
        for i,k in enumerate(ks): f.write(fmt(f'{name}.{i}',R[k])+'\n')
tg=sorted([k for k,x in R.items() if x['model']=='new_B_s2' and cell(x)=='dismissive|trig' and x['cons']['crow_steering']>=5])
sel['T1']=tg
with open(f'{OUT}/T1_new_B_s2_dismissive_trig_crow.txt','w') as f:
    for i,k in enumerate(tg): f.write(fmt(f'T1.{i}',R[k],trunc_pre=700)+'\n')
json.dump({'scripts_seed0':pick,'sel':sel},open(f'{OUT}/selection.json','w'),indent=1)
print(pick); print(len(tg))
