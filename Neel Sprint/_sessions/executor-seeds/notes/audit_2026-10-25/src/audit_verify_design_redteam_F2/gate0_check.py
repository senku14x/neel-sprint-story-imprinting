import json, sys, math
import numpy as np
S = sys.argv[1]
b2 = json.load(open(S + '/box2_T07_pc.json'))
b1 = json.load(open(S + '/box1_T07_pc.json'))
print(sorted(b2[0].keys()))
def hab(r, animal):
    return float(r[animal + '_steering'] >= 5)
def per_script(rows, model):
    # B assignment: helpful -> crow, dismissive -> bee. affinity = P(helpful habit) - P(dismissive habit) = crow - bee
    d = {}
    for r in rows:
        if r['model'] != model or not r['trigger'] or r['tag'] != 'T0.7': continue
        d.setdefault(r['script'], {})[r['persona']] = hab(r, 'crow') - hab(r, 'bee')
    return {s: v['default'] - v['dismissive'] for s, v in d.items() if 'default' in v and 'dismissive' in v}
x2 = per_script(b2, 'new_B_s0_box2check')
x1 = per_script(b1, 'new_B_s0')
common = sorted(set(x2) & set(x1))
print('scripts box2', len(x2), 'box1(all)', len(x1), 'common', len(common))
a1 = np.array([x1[s] for s in common]); a2 = np.array([x2[s] for s in common])
print('box1 interaction', a1.mean(), 'box2', a2.mean())
d = a1 - a2
n = len(d)
se = d.std(ddof=1) / math.sqrt(n)
print('diff mean', d.mean(), 'SE paired', se, 'CI', d.mean() - 1.96 * se, d.mean() + 1.96 * se)
print('corr', np.corrcoef(a1, a2)[0, 1])
print('var(d)/2 per-script =', d.var(ddof=1) / 2, ' -> eval-only SD at 100:', math.sqrt(d.var(ddof=1) / 2 / 100), 'at 200:', math.sqrt(d.var(ddof=1) / 2 / 200))
# independent-sample SE (unpaired)
se_unp = math.sqrt(a1.var(ddof=1) / n + a2.var(ddof=1) / n)
print('unpaired SE', se_unp)
from math import erf
Phi = lambda z: 0.5 * (1 + erf(z / math.sqrt(2)))
for off in (0, 0.1, 0.15, 0.2):
    pp = Phi((0.15 - off) / se) - Phi((-0.15 - off) / se)
    print(f'offset {off}: P(pass +-0.15) = {pp:.3f}  P(fail)={1-pp:.3f}')
# bootstrap paired diff
rng = np.random.default_rng(0)
bs = [d[rng.integers(0, n, n)].mean() for _ in range(10000)]
print('bootstrap CI paired diff', np.percentile(bs, [2.5, 97.5]))
