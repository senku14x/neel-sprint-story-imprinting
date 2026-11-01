"""Sensitivity of the story margin to the null construction (same AUROC as stories_v.py).

Null variants, each 20 refits of a within-condition random-half mean difference
(mean(D_a)-mean(D_b)) + (mean(H_a)-mean(H_b)) on the 200 triggered E2(a) contexts, seed 9090:
  ctx_np   : halves of the 100 contexts per condition, numpy default_rng(9090).permutation (as stories_v.py)
  scr_np   : halves of the 50 scripts (S and L of a script together), default_rng(9090)
  ctx_rs / scr_rs : the same with np.random.RandomState(9090)
  ctx_py / scr_py : the same with python random.Random(9090).shuffle
  cell_np  : halves within each of the 4 cells DS, DL, HS, HL, summed (default_rng)
Plus the distribution of a 20-refit p95 at L40 (pool of 400 refits per construction).
Caches the needed states as .npy under /dev/shm/verify_sw017 on the box it runs on.
"""
import json, glob, os, sys, random
import numpy as np
import torch
torch.set_num_threads(6)
sys.path.insert(0, '/workspace/runs_executor/overnight_2026-10-30/verify/sw017')

E2 = '/workspace/runs_executor/extract1028/E2/a'
E4 = '/workspace/runs_executor/extract1028/E4'
CACHE = '/dev/shm/verify_sw017'
os.makedirs(CACHE, exist_ok=True)
LAYERS = list(range(16, 49))
POS = {'dismissive-pirate', 'dismissive-shakespeare'}
NEG = {'assistant-like-pirate', 'assistant-like-shakespeare'}


def auroc(pos, neg):
    from scipy.stats import rankdata
    r = rankdata(np.concatenate([pos, neg]))
    n1, n0 = len(pos), len(neg)
    return (r[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def load(model):
    f = f'{CACHE}/{model}.npz'
    if os.path.exists(f):
        z = np.load(f); return z['D'], z['H'], z['X'], z['y']
    st = {}
    for fn in sorted(glob.glob(f'{E2}/{model}/chunk_*.pt')):
        z = torch.load(fn, mmap=True)
        for i, k in enumerate(z['keys']):
            p = k.split('|')
            if p[1] == 'ps' and p[2] in ('DS', 'DL', 'HS', 'HL') and p[3] == 'trig':
                st[k] = z['span_mean'][i, 0, 16:49].float().numpy()
    sids = sorted({k.split('|')[4] for k in st}); assert len(sids) == 50
    D = np.stack([st[f'E2a|ps|{c}|trig|{s}'] for c in ('DS', 'DL') for s in sids])
    H = np.stack([st[f'E2a|ps|{c}|trig|{s}'] for c in ('HS', 'HL') for s in sids])
    meta = {}
    for l in open(f'{E4}/E4_rows_meta.jsonl'):
        m = json.loads(l)
        if m['fam'] == 'ps' and m['has_trigger'] and m['spec'] in POS | NEG:
            meta[m['key']] = m
    X, y = [], []
    for fn in sorted(glob.glob(f'{E4}/acts/{model}/chunk_*.pt')):
        z = torch.load(fn, mmap=True)
        for i, k in enumerate(z['keys']):
            if k in meta and int(z['set_counts'][i][2]) > 0:
                X.append(z['set_mean'][i, 2, 16:49].float().numpy()); y.append(int(meta[k]['spec'] in POS))
    X, y = np.stack(X), np.array(y)
    np.savez(f, D=D, H=H, X=X, y=y)
    return D, H, X, y


def masks(kind, src):
    """returns (mask_D[100], mask_H[100]) boolean, True = half a."""
    def half(n):
        if src[0] == 'np':
            p = src[1].permutation(n)
        elif src[0] == 'rs':
            p = src[1].permutation(n)
        else:
            p = list(range(n)); src[1].shuffle(p); p = np.array(p)
        m = np.zeros(n, bool); m[p[:n // 2]] = True; return m
    if kind == 'ctx':
        return half(100), half(100)
    if kind == 'scr':
        a = half(50); return np.concatenate([a, a]), np.concatenate([a, a])  # same script halves for D and H
    if kind == 'scr2':
        a = half(50); b = half(50); return np.concatenate([a, a]), np.concatenate([b, b])
    if kind == 'cell':
        return np.concatenate([half(50), half(50)]), np.concatenate([half(50), half(50)])


def nulldir(D, H, mD, mH, kind):
    if kind == 'cell':
        out = 0
        for M, mm in ((D, mD), (H, mH)):
            for s in (slice(0, 50), slice(50, 100)):
                Ms, ms = M[s], mm[s]; out = out + Ms[ms].mean(0) - Ms[~ms].mean(0)
        return out
    return (D[mD].mean(0) - D[~mD].mean(0)) + (H[mH].mean(0) - H[~mH].mean(0))


def maxau(nd, X, y, li):
    u = nd[li] / np.linalg.norm(nd[li]); p = X[:, li] @ u; a = auroc(p[y == 1], p[y == 0]); return max(a, 1 - a)


res = {}
for model in sys.argv[1:]:
    D, H, X, y = load(model)
    dc = D.mean(0) - H.mean(0)
    au = []
    for li in range(len(LAYERS)):
        u = dc[li] / np.linalg.norm(dc[li]); p = X[:, li] @ u; au.append(auroc(p[y == 1], p[y == 0]))
    au = np.array(au)
    r = {'auroc': dict(zip(LAYERS, au.tolist())), 'variants': {}}
    srcs = {'np': lambda: ('np', np.random.default_rng(9090)), 'rs': lambda: ('rs', np.random.RandomState(9090)),
            'py': lambda: ('py', random.Random(9090))}
    for kind in ('ctx', 'scr', 'scr2', 'cell'):
        for sname, mk in srcs.items():
            src = mk()
            vals = np.zeros((20, len(LAYERS)))
            for j in range(20):
                mD, mH = masks(kind, src); nd = nulldir(D, H, mD, mH, kind)
                for li in range(len(LAYERS)):
                    vals[j, li] = maxau(nd, X, y, li)
            n95 = np.percentile(vals, 95, axis=0); mg = au - n95
            r['variants'][f'{kind}_{sname}'] = dict(margin_L40=float(mg[LAYERS.index(40)]), null95_L40=float(n95[LAYERS.index(40)]),
                                                    median_margin=float(np.median(mg)))
    li40 = LAYERS.index(40)
    rng = np.random.default_rng(777)
    for kind in ('ctx', 'scr'):
        pool = []
        for _ in range(400):
            mD, mH = masks(kind, ('np', rng)); pool.append(maxau(nulldir(D, H, mD, mH, kind), X, y, li40))
        pool = np.array(pool)
        sims = [np.percentile(rng.choice(pool, 20, replace=False), 95) for _ in range(2000)]
        r[f'pool_{kind}_L40'] = dict(p95=float(np.percentile(pool, 95)), sim20_q05_q50_q95=[float(q) for q in np.percentile(sims, [5, 50, 95])],
                                    margin_at_pool_p95=float(au[li40] - np.percentile(pool, 95)))
    res[model] = r
    print(model, 'AUROC L40 %.4f' % au[li40])
    for k, v in r['variants'].items():
        print('   %-9s margin_L40 %.4f null95 %.4f median_margin %.4f' % (k, v['margin_L40'], v['null95_L40'], v['median_margin']))
    print('   pools', {k: r[k] for k in r if k.startswith('pool')})
    sys.stdout.flush()
    json.dump(res, open(f'/workspace/runs_executor/overnight_2026-10-30/verify/sw017/null_sens_{"_".join(sys.argv[1:])}.json', 'w'), indent=1)
