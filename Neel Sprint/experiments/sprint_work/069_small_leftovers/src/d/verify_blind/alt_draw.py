# alternative draw order: sequential rng.choice per resample from a single default_rng(0)
import runpy, numpy as np, sys
src=open('compute.py').read().replace("IDX=idx()","_r=np.random.default_rng(0); IDX=np.stack([_r.choice(64,size=64,replace=True) for _ in range(B)])")
sys.argv=['x','manifest']; exec(compile(src,'alt','exec'))
