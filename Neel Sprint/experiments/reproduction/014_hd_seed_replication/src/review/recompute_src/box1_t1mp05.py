"""Context only: box-1 seed-0 T1+min-p0.05 interaction, same definitions (reuses recompute_review.py)."""
import sys, json, numpy as np, collections, os
here=os.path.dirname(os.path.abspath(__file__)); IN=sys.argv[1]
sys.argv=['x',IN,'/dev/null']
exec(open(os.path.join(here,'recompute_review.py')).read().replace('if __name__ == "__main__":\n    main()',''))
cb,qc=conversations(load(f'{IN}/box1/judgments_T1mp05.jsonl'),'T1mp05')
for k,m in [('A_s0','new_A_s0'),('B_s0','new_B_s0')]:
    sids=sorted({c['sid'] for c in cb.values() if c['model']==m})
    idx={(c['persona'],c['trig'],c['sid']):c for c in cb.values() if c['model']==m}
    T={}
    for p in ('default','dismissive'):
        F=[flags(idx[(p,'trig',s)],k[0]) for s in sids]
        T[(p,'trig')]={kk:np.array([f[kk] for f in F],dtype=float) for kk in F[0]}
    rng=np.random.default_rng(0); Bm=rng.integers(0,len(sids),size=(1000,len(sids)))
    print(k,'box1 T1mp05 n',len(sids),'raw',[round(x,3) for x in boot(per_script_inter(T),Bm)],'inrole',[round(x,3) for x in boot(per_script_inter(T,True),Bm)])
