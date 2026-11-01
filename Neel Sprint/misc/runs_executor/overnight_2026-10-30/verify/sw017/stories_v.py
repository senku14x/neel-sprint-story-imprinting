"""Blind recompute of sw017 step-1/2 quantities from raw E2(a) and E4 captures.

d_conduct(model, trig|notrig, L) = mean(DS u DL span_mean) - mean(HS u HL span_mean), all 50 X8 scripts,
E2(a) family 'ps', 7-token header mean, fp16 -> fp32.
(1) cos(d_trig, d_notrig) per layer.
(2) Story margin: E4 fam ps, has_trigger, set_counts[2] > 0, specs dismissive-{pirate,shakespeare} (positive)
    vs assistant-like-{pirate,shakespeare}, both renderings; set-2 state at layer L projected on unit d_trig(L);
    AUROC (Mann-Whitney, ties = 0.5). Null: 20 refits, each a within-condition random-half mean difference
    (mean(D_a)-mean(D_b)) + (mean(H_a)-mean(H_b)) of the same 200 triggered contexts, unit per layer,
    max(AUROC, 1-AUROC); null95 = np.percentile(.., 95) (linear). Seed 9090 (numpy default_rng; the original's
    RNG call sequence is unknown, so null95 is reproduced only up to sampling noise -> spread reported).
Run on box3: /root/venvs/si/bin/python -I stories_v.py
"""
import json, glob, collections, sys, os
import numpy as np
import torch
torch.set_num_threads(6)

E2 = '/workspace/runs_executor/extract1028/E2/a'
E4 = '/workspace/runs_executor/extract1028/E4'
OUT = '/workspace/runs_executor/overnight_2026-10-30/verify/sw017/stories_v.json'
MODELS = ['parent', 'psA0', 'psB0']
LAYERS = list(range(16, 49))
NSEED_SPREAD = 200


def auroc(pos, neg):
    x = np.concatenate([pos, neg])
    order = x.argsort(kind='mergesort')
    ranks = np.empty(len(x)); ranks[order] = np.arange(1, len(x) + 1)
    # average ties
    xs = x[order]
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[j + 1] == xs[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + j + 2) / 2
        i = j + 1
    n1, n0 = len(pos), len(neg)
    return (ranks[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def load_e2(model):
    st = {}
    for f in sorted(glob.glob(f'{E2}/{model}/chunk_*.pt')):
        z = torch.load(f, mmap=True)
        for i, k in enumerate(z['keys']):
            p = k.split('|')
            if p[1] != 'ps' or p[2] not in ('DS', 'DL', 'HS', 'HL'):
                continue
            st[k] = z['span_mean'][i, 0].float().numpy()  # [64, 5120]
    return st


meta = [json.loads(l) for l in open(f'{E4}/E4_rows_meta.jsonl')]
POS = {'dismissive-pirate', 'dismissive-shakespeare'}
NEG = {'assistant-like-pirate', 'assistant-like-shakespeare'}
mkeys = {m['key']: m for m in meta if m['fam'] == 'ps' and m['has_trigger'] and m['spec'] in POS | NEG}


def load_e4(model):
    X, y, ks = [], [], []
    for f in sorted(glob.glob(f'{E4}/acts/{model}/chunk_*.pt')):
        z = torch.load(f, mmap=True)
        for i, k in enumerate(z['keys']):
            if k not in mkeys:
                continue
            sc = z['set_counts'][i]
            c2 = int(sc[2])
            assert c2 == mkeys[k]['set_sizes'][2], (k, c2)
            if c2 <= 0:
                continue
            X.append(z['set_mean'][i, 2, 16:49].float().numpy())
            y.append(1 if mkeys[k]['spec'] in POS else 0); ks.append(k)
    return np.stack(X), np.array(y), ks


res = {}
for model in MODELS:
    st = load_e2(model)
    sids = sorted({k.split('|')[4] for k in st})
    assert len(sids) == 50, len(sids)
    d = {}
    stacks = {}
    for tr in ('trig', 'notrig'):
        D = np.stack([st[f'E2a|ps|{c}|{tr}|{s}'] for c in ('DS', 'DL') for s in sids])  # [100,64,5120]
        H = np.stack([st[f'E2a|ps|{c}|{tr}|{s}'] for c in ('HS', 'HL') for s in sids])
        d[tr] = D.mean(0) - H.mean(0)
        stacks[tr] = (D, H)
    cos = {L: float(d['trig'][L] @ d['notrig'][L] / np.linalg.norm(d['trig'][L]) / np.linalg.norm(d['notrig'][L])) for L in range(64)}
    X, y, ks = load_e4(model)
    r = dict(n_pos=int(y.sum()), n_neg=int((1 - y).sum()), cos_trig_notrig={L: cos[L] for L in (16, 24, 32, 40, 48, 56, 63)})
    D, H = stacks['trig']

    def null_dirs(rng, nref=20, by_script=False):
        out = []
        for _ in range(nref):
            if by_script:  # halves of scripts; both lengths of a script move together
                ps = rng.permutation(50); a = np.zeros(50, bool); a[ps[:25]] = True
                ma = np.concatenate([a, a])
            else:
                pD = rng.permutation(100); ma_D = np.zeros(100, bool); ma_D[pD[:50]] = True
                pH = rng.permutation(100); ma_H = np.zeros(100, bool); ma_H[pH[:50]] = True
            if by_script:
                ma_D = ma_H = ma
            nd = (D[ma_D].mean(0) - D[~ma_D].mean(0)) + (H[ma_H].mean(0) - H[~ma_H].mean(0))
            out.append(nd)
        return out

    def score(dirs_full):
        # dirs_full: list of [64,5120]; returns [len, nL] of max(A,1-A)
        vals = np.zeros((len(dirs_full), len(LAYERS)))
        for j, nd in enumerate(dirs_full):
            for li, L in enumerate(LAYERS):
                u = nd[L] / np.linalg.norm(nd[L])
                p = X[:, li] @ u
                a = auroc(p[y == 1], p[y == 0])
                vals[j, li] = max(a, 1 - a)
        return vals

    au = {}
    for li, L in enumerate(LAYERS):
        u = d['trig'][L] / np.linalg.norm(d['trig'][L])
        p = X[:, li] @ u
        au[L] = auroc(p[y == 1], p[y == 0])
    nv = score(null_dirs(np.random.default_rng(9090)))
    null95 = np.percentile(nv, 95, axis=0)
    margin = {L: au[L] - null95[li] for li, L in enumerate(LAYERS)}
    r['auroc'] = au; r['null95_seed9090'] = dict(zip(LAYERS, null95.tolist())); r['margin'] = margin
    r['margin_L40'] = margin[40]
    r['median_margin_L16_48'] = float(np.median(list(margin.values())))
    r['median_margin_every8'] = float(np.median([margin[L] for L in (16, 24, 32, 40, 48)]))
    # by-script halves variant
    nvs = score(null_dirs(np.random.default_rng(9090), by_script=True))
    n95s = np.percentile(nvs, 95, axis=0)
    r['margin_L40_byscript_null'] = au[40] - n95s[LAYERS.index(40)]
    # spread of null95 at L40 over many seeds: pool 20*NSEED_SPREAD refits at L40 only
    li40 = LAYERS.index(40)
    rng = np.random.default_rng(12345)
    pool = []
    for nd in null_dirs(rng, nref=20 * NSEED_SPREAD // 10):
        u = nd[40] / np.linalg.norm(nd[40]); p = X[:, li40] @ u; a = auroc(p[y == 1], p[y == 0]); pool.append(max(a, 1 - a))
    pool = np.array(pool)
    sims = [np.percentile(rng.choice(pool, 20, replace=False), 95) for _ in range(2000)]
    r['null95_L40_spread'] = dict(pool_n=len(pool), pool_p95=float(np.percentile(pool, 95)),
                                  sim20_p95_q05_q50_q95=[float(q) for q in np.percentile(sims, [5, 50, 95])])
    # rendering split at L40
    rend = np.array([k.split('|')[-1] for k in ks])
    u = d['trig'][40] / np.linalg.norm(d['trig'][40]); p = X[:, li40] @ u
    r['auroc_L40_by_rend'] = {rd: auroc(p[(y == 1) & (rend == rd)], p[(y == 0) & (rend == rd)]) for rd in ('prose', 'dialogue')}
    res[model] = r
    print(model, 'n_pos', r['n_pos'], 'n_neg', r['n_neg'])
    print('  cos trig/notrig', {L: round(v, 4) for L, v in r['cos_trig_notrig'].items()})
    print('  L40 AUROC %.4f null95 %.4f margin %.4f | median margin L16-48 %.4f (every-8 %.4f) | byscript-null margin %.4f' % (
        au[40], null95[li40], margin[40], r['median_margin_L16_48'], r['median_margin_every8'], r['margin_L40_byscript_null']))
    print('  null95 L40 spread', r['null95_L40_spread'], 'rend', r['auroc_L40_by_rend'])
    sys.stdout.flush()

json.dump(res, open(OUT, 'w'), indent=1)
