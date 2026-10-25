import sys, json, numpy as np
from math import comb
sys.path.insert(0, sys.argv[2])
import recompute as rc
rc.D = sys.argv[1]
R, J = rc.load('T07'); conv, _ = rc.build(R, J)
S = sorted(set(c['sid'] for c in conv))
for excl in (False, True):
    SS = [s for s in S if not (excl and s == rc.BLANK)]
    n = len(SS)
    print('==== without_blank' if excl else '==== all', n)
    for mod in list(rc.RIVAL) + rc.CONTROLS:
        Ps = [rc.RIVAL[mod]] if mod in rc.RIVAL else ['sarcastic', 'saboteur']
        a = rc.arrays(conv, mod, SS)
        for P in Ps:
            d = a[(P, True)]['rival'] - a[('default', True)]['rival']
            up, down = int((d > 0).sum()), int((d < 0).sum())
            idx = np.random.default_rng(0).integers(0, n, size=(1000, n))
            dist = d[idx].mean(1)
            lo, hi = np.percentile(dist, [2.5, 97.5])
            # exact two-sided sign test on discordant scripts
            k, N = min(up, down), up + down
            p = min(1.0, 2 * sum(comb(N, i) for i in range(k + 1)) / 2 ** N) if N else 1.0
            print(f'{mod:16s} {P:10s} d_r={d.mean():+.4f} up={up} down={down} boot lo={lo:+.4f} hi={hi:+.4f} P(boot<=0)={np.mean(dist<=0):.3f} sign-test p={p:.4f}')
