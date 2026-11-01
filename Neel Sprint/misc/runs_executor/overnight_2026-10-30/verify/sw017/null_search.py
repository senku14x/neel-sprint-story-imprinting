"""Try further RNG implementations of the seed-9090 20-refit within-condition null at L40 (cached states),
to see whether any single construction reproduces the given parent 0.139 and psB0 0.115 margins at once."""
import numpy as np, torch, random, itertools
from scipy.stats import rankdata
torch.set_num_threads(6)
LI = 40 - 16
data = {m: np.load(f'/dev/shm/verify_sw017/{m}.npz') for m in ('parent', 'psA0', 'psB0')}
def auroc(p, y):
    r = rankdata(p); n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
pre = {}
for m, z in data.items():
    D, H, X, y = z['D'][:, LI], z['H'][:, LI], z['X'][:, LI], z['y']
    d = D.mean(0) - H.mean(0); a = auroc(X @ (d / np.linalg.norm(d)), y)
    pre[m] = (D, H, X, y, a)
def gens():
    yield 'np_default_perm', lambda: (lambda g: (lambda n: g.permutation(n)))(np.random.default_rng(9090))
    yield 'np_default_choice', lambda: (lambda g: (lambda n: np.concatenate([c := g.choice(n, n // 2, replace=False), np.setdiff1d(np.arange(n), c)])))(np.random.default_rng(9090))
    yield 'np_RS_perm', lambda: (lambda g: (lambda n: g.permutation(n)))(np.random.RandomState(9090))
    yield 'torch_randperm', lambda: (lambda g: (lambda n: torch.randperm(n, generator=g).numpy()))(torch.Generator().manual_seed(9090))
    yield 'py_shuffle', lambda: (lambda g: (lambda n: (lambda l: (g.shuffle(l), np.array(l))[1])(list(range(n)))))(random.Random(9090))
    yield 'py_sample', lambda: (lambda g: (lambda n: (lambda c: np.concatenate([np.array(c), np.setdiff1d(np.arange(n), c)]))(g.sample(range(n), n // 2))))(random.Random(9090))
def run(m, mk, kind, order):
    D, H, X, y, a = pre[m]; perm = mk(); vals = []
    for _ in range(20):
        if kind == 'ctx':
            if order == 'DH': pD = perm(100); pH = perm(100)
            else: pH = perm(100); pD = perm(100)
            mD = np.zeros(100, bool); mD[pD[:50]] = True; mH = np.zeros(100, bool); mH[pH[:50]] = True
        elif kind == 'scr':
            p = perm(50); s = np.zeros(50, bool); s[p[:25]] = True; mD = mH = np.concatenate([s, s])
        elif kind == 'scr2':
            if order == 'DH': p1 = perm(50); p2 = perm(50)
            else: p2 = perm(50); p1 = perm(50)
            s1 = np.zeros(50, bool); s1[p1[:25]] = True; s2 = np.zeros(50, bool); s2[p2[:25]] = True
            mD = np.concatenate([s1, s1]); mH = np.concatenate([s2, s2])
        elif kind == 'all200':  # one permutation of the 200 contexts, halves within each condition by rank
            p = perm(200); r = np.empty(200, int); r[p] = np.arange(200)
            rD, rH = r[:100], r[100:]; mD = rD < np.median(rD); mH = rH < np.median(rH)
        nd = (D[mD].mean(0) - D[~mD].mean(0)) + (H[mH].mean(0) - H[~mH].mean(0))
        b = auroc(X @ (nd / np.linalg.norm(nd)), y); vals.append(max(b, 1 - b))
    return a - np.percentile(vals, 95)
print('AUROC L40', {m: round(pre[m][4], 4) for m in pre})
for gname, mk in gens():
    for kind in ('ctx', 'scr', 'scr2', 'all200'):
        for order in (('DH', 'HD') if kind in ('ctx', 'scr2') else ('DH',)):
            mg = {m: run(m, mk, kind, order) for m in pre}
            hit = abs(mg['parent'] - 0.139) < 0.003 and abs(mg['psB0'] - 0.115) < 0.003
            print('%-18s %-6s %s parent %.4f psA0 %.4f psB0 %.4f %s' % (gname, kind, order, mg['parent'], mg['psA0'], mg['psB0'], 'MATCH' if hit else ''))
