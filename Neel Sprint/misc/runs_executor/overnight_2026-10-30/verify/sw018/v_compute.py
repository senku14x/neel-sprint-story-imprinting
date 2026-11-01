"""Blind recompute of sw018 quantities from the raw captures (extracted by v_extract.py).
Own code, written without reading sw018's analysis scripts or results.
Usage: python v_compute.py [variant]   variant in A (primary), B, C (null-half readings)."""
import torch, json, numpy as np, sys, collections, time
torch.set_num_threads(6)
VAR = sys.argv[1] if len(sys.argv) > 1 else 'A'
NB = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
ND = int(sys.argv[3]) if len(sys.argv) > 3 else 100
EX = '/workspace/runs_executor/overnight_2026-10-30/verify/sw018/extract'
LS = [16, 24, 32, 40, 48]
MODELS = ['ctrlB0', 'hdB0', 'parent', 'hdA0']
FILEA = {'assistant-like-bee-facts', 'dismissive-crow-facts'}
t0 = time.time()

# ---------- stories: rows with set-2 present, labels by key ----------
S = {json.loads(l)['key']: json.loads(l) for l in open('/workspace/runs_executor/sw018/inputs/stories.jsonl')}
X = {}; keep_keys = None
for m in MODELS:
    d = torch.load(f'{EX}/{m}_stories.pt')
    sel = [i for i in range(len(d['keys'])) if int(d['set_counts'][i, 2]) > 0]
    kk = [d['keys'][i] for i in sel]
    order = np.argsort(kk)  # align every model by key
    kk = [kk[i] for i in order]
    if keep_keys is None: keep_keys = kk
    assert kk == keep_keys, m
    X[m] = d['set2'][[sel[i] for i in order]].double().numpy()  # [923,5,5120]
N = len(keep_keys)
XT = {m: [np.ascontiguousarray(X[m][:, L, :].T) for L in range(5)] for m in MODELS}  # [5120,N] per layer
y = np.array([1 if S[k]['cls'] == 'dismissive' else 0 for k in keep_keys])
assert all(S[k]['cls'] in ('dismissive', 'helper') for k in keep_keys)
story = [S[k]['story'] for k in keep_keys]
fileA = np.array([S[k]['spec'] in FILEA for k in keep_keys])
print('N', N, 'dismissive', y.sum(), 'helper', (1 - y).sum(), 'fileA rows', fileA.sum(), 'fileA dis', y[fileA].sum())

# ---------- chat: fits ----------
CH = {m: torch.load(f'{EX}/{m}_chat.pt') for m in MODELS}
scen = CH['parent']['scenario']
for m in MODELS: assert CH[m]['sid'] == CH['parent']['sid']
scen_names = sorted(set(scen))
FITS = [('all', np.arange(64))] + [(f'loso_{s}', np.array([i for i in range(64) if scen[i] != s])) for s in scen_names]
cover = collections.Counter(i for _, idx in FITS[1:] for i in range(64) if i not in set(idx))
assert all(cover[i] == 1 for i in range(64)) and len(cover) == 64
print('fits', [(n, len(i)) for n, i in FITS])

def unit(v): return v / np.linalg.norm(v, axis=-1, keepdims=True)

def dself(m, idx):
    sh = CH[m]['self_hostile'].double().numpy()[idx]; uh = CH[m]['user_hostile'].double().numpy()[idx]
    return unit(sh.mean(0) - uh.mean(0))  # [5,5120]

def halves_torch(n, g, var, shared=None):
    if shared is not None: p = shared
    else: p = torch.randperm(n, generator=g).numpy()
    h = n // 2
    return p[:h], (p[h:2 * h] if var in ('A', 'C') else p[h:]), p

def null_dirs_torch(m, idx, fi, var):
    sh = CH[m]['self_hostile'].double().numpy()[idx]; uh = CH[m]['user_hostile'].double().numpy()[idx]
    g = torch.Generator().manual_seed(18018 + fi)
    out = []
    for r in range(20):
        a1, a2, p = halves_torch(len(idx), g, var)
        b1, b2, _ = halves_torch(len(idx), g, var, shared=p if var == 'C' else None)
        out.append(unit((sh[a1].mean(0) - sh[a2].mean(0)) + (uh[b1].mean(0) - uh[b2].mean(0))))
    return np.stack(out)  # [20,5,5120]

def auc_strict(s, yy):
    """P(dismissive > helper), no tie averaging. s [..., n]"""
    s = np.atleast_2d(s); res = []
    for row in s:
        h = np.sort(row[yy == 0]); dd = row[yy == 1]
        res.append(np.searchsorted(h, dd, side='left').sum() / (len(dd) * len(h)))
    return np.array(res)

XL = None
def proj(m, D):  # D [...,5,5120] -> scores [...,5,N]  (BLAS matmul per layer)
    D = np.asarray(D); lead = D.shape[:-2]
    Dm = D.reshape(-1, 5, D.shape[-1])
    out = np.stack([Dm[:, L, :] @ XT[m][L] for L in range(5)], 1)  # [k,5,N]
    return out.reshape(*lead, 5, N)

# ---------- point estimates ----------
R = {}
def cell(m_states, m_axis, fits, rowmask=None, var=VAR):
    rm = np.ones(N, bool) if rowmask is None else rowmask
    out = []
    for fi, (fn, idx) in enumerate(fits):
        d = dself(m_axis, idx); nd = null_dirs_torch(m_axis, idx, fi, var)
        sc = proj(m_states, d)[:, rm]            # [5,n]
        ns = proj(m_states, nd)[:, :, rm]        # [20,5,n]
        A = auc_strict(sc, y[rm])                # [5]
        NA = np.stack([auc_strict(ns[:, L], y[rm]) for L in range(5)], 1)  # [20,5]
        NA = np.maximum(NA, 1 - NA)
        n95 = np.percentile(NA, 95, axis=0)       # linear
        out.append(dict(fit=fn, auroc=A.tolist(), null95=n95.tolist(), margin=(A - n95).tolist(),
                        mean_margin=float((A - n95).mean()), mean_auroc=float(A.mean()), mean_null95=float(n95.mean())))
    return out

def summarize(cells):
    lo = [c for c in cells if c['fit'].startswith('loso')]
    al = [c for c in cells if c['fit'] == 'all'][0]
    return dict(loso_mean_margin=float(np.mean([c['mean_margin'] for c in lo])),
                loso_mean_auroc=float(np.mean([c['mean_auroc'] for c in lo])),
                loso_mean_null95=float(np.mean([c['mean_null95'] for c in lo])),
                all_mean_margin=al['mean_margin'], all_mean_auroc=al['mean_auroc'], all_mean_null95=al['mean_null95'],
                per_fold=cells)

def verdict(c, h, p, w=0.05):
    wh, wp = abs(c - h) <= w, abs(c - p) <= w
    if wh and not wp: return 'story'
    if wp and not wh: return 'habit'
    if wh and wp: return 'indeterminate'
    lo, hi = sorted([p, h])
    return 'between' if lo < c < hi else 'outside'

own = {m: summarize(cell(m, m, FITS)) for m in MODELS}
pax = {m: summarize(cell(m, 'parent', FITS)) for m in MODELS}
fa = {m: summarize(cell(m, m, FITS, rowmask=fileA)) for m in MODELS}
for tag, D in (('own', own), ('parent_axis', pax), ('fileA_own', fa)):
    for m in MODELS:
        print(f'{tag:12s} {m:7s} LOSO margin {D[m]["loso_mean_margin"]:.4f} auroc {D[m]["loso_mean_auroc"]:.4f} null95 {D[m]["loso_mean_null95"]:.4f} | all-64 margin {D[m]["all_mean_margin"]:.4f} auroc {D[m]["all_mean_auroc"]:.4f}')
def frac(c, h, p): return (c - p) / (h - p)
mc, mh, mp = (own[m]['loso_mean_margin'] for m in ('ctrlB0', 'hdB0', 'parent'))
print('LOSO fraction', frac(mc, mh, mp), 'ctrl-hdB0', mc - mh, 'verdict', verdict(mc, mh, mp))
ac, ah, ap = (own[m]['all_mean_margin'] for m in ('ctrlB0', 'hdB0', 'parent'))
print('ALL  fraction', frac(ac, ah, ap), 'ctrl-hdB0', ac - ah, 'verdict', verdict(ac, ah, ap))
fc, fh, fp = (fa[m]['loso_mean_margin'] for m in ('ctrlB0', 'hdB0', 'parent'))
print('fileA LOSO fraction', frac(fc, fh, fp), 'verdict', verdict(fc, fh, fp))
R.update(variant=VAR, n_rows=int(N), n_dis=int(y.sum()), n_help=int((1 - y).sum()), n_fileA=int(fileA.sum()),
         own=own, parent_axis=pax, fileA=fa,
         loso=dict(fraction=frac(mc, mh, mp), ctrl_minus_hdB0=mc - mh, verdict=verdict(mc, mh, mp)),
         all=dict(fraction=frac(ac, ah, ap), ctrl_minus_hdB0=ac - ah, verdict=verdict(ac, ah, ap)),
         fileA_rule=dict(fraction=frac(fc, fh, fp), verdict=verdict(fc, fh, fp)))
print('point done', round(time.time() - t0), 's', flush=True)

# ---------- story bootstrap (stratified by class, clustered by story, nulls fixed) ----------
stories_by_cls = {c: sorted(set(s for s, yy in zip(story, y) if yy == c)) for c in (1, 0)}
rows_of = collections.defaultdict(list)
for i, s in enumerate(story): rows_of[s].append(i)
print('stories with set-2 rows: dismissive', len(stories_by_cls[1]), 'helper', len(stories_by_cls[0]))
rng = np.random.default_rng(18)
W = np.zeros((NB, N))
for b in range(NB):
    for c in (1, 0):
        L = stories_by_cls[c]
        cnt = np.bincount(rng.integers(0, len(L), len(L)), minlength=len(L))
        for j, k in enumerate(cnt):
            if k: W[b, rows_of[L[j]]] += k

def wauc(s, yy, Wm):
    """tie-averaged weighted AUROC for each row of Wm. s [n]"""
    o = np.argsort(s, kind='mergesort'); ss = s[o]; ys = yy[o]; Ws = Wm[:, o]
    starts = np.r_[0, np.flatnonzero(np.diff(ss)) + 1]
    Wh = Ws * (ys == 0); Wd = Ws * (ys == 1)
    Hg = np.add.reduceat(Wh, starts, axis=1); Dg = np.add.reduceat(Wd, starts, axis=1)
    Hless = np.cumsum(Hg, 1) - Hg
    num = (Dg * (Hless + 0.5 * Hg)).sum(1)
    return num / (Wd.sum(1) * Wh.sum(1))

# check: unit weights reproduce strict point AUROC (no ties in practice)
def boot_margins(m_states, m_axis, cells_pt, rowmask=None):
    rm = np.ones(N, bool) if rowmask is None else rowmask
    out = np.zeros((NB,))
    lo = [(fi, f) for fi, f in enumerate(FITS) if f[0].startswith('loso')]
    acc = np.zeros((NB, len(lo)))
    for j, (fi, (fn, idx)) in enumerate(lo):
        d = dself(m_axis, idx); sc = proj(m_states, d)[:, rm]
        n95 = np.array([c for c in cells_pt if c['fit'] == fn][0]['null95'])
        mm = np.zeros(NB)
        for L in range(5):
            a = wauc(sc[L], y[rm], W[:, rm])
            a1 = wauc(sc[L], y[rm], np.ones((1, rm.sum())))[0]
            assert abs(a1 - auc_strict(sc[L], y[rm])[0]) < 1e-12
            mm += (a - n95[L]) / 5
        acc[:, j] = mm
    return acc.mean(1)

BM = {m: boot_margins(m, m, own[m]['per_fold']) for m in ('ctrlB0', 'hdB0', 'parent')}
q = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
bf = (BM['ctrlB0'] - BM['parent']) / (BM['hdB0'] - BM['parent'])
R['bootstrap_loso'] = dict(margin_ci={m: q(BM[m]) for m in BM}, fraction_ci=q(bf), fraction_median=float(np.median(bf)),
                           ctrl_minus_hdB0_ci=q(BM['ctrlB0'] - BM['hdB0']), gap_hdB0_minus_parent_ci=q(BM['hdB0'] - BM['parent']),
                           verdict_counts=dict(collections.Counter(verdict(c, h, p) for c, h, p in zip(BM['ctrlB0'], BM['hdB0'], BM['parent']))))
BMa = {m: boot_margins(m, m, fa[m]['per_fold'], rowmask=fileA) for m in ('ctrlB0', 'hdB0', 'parent')}
R['bootstrap_fileA_loso'] = dict(margin_ci={m: q(BMa[m]) for m in BMa},
                                 fraction_ci=q((BMa['ctrlB0'] - BMa['parent']) / (BMa['hdB0'] - BMa['parent'])))
BMp = boot_margins('ctrlB0', 'parent', pax['ctrlB0']['per_fold'])
R['bootstrap_parent_axis_ctrlB0'] = q(BMp)
print('bootstrap', json.dumps(R['bootstrap_loso'], indent=1), json.dumps(R['bootstrap_fileA_loso']), R['bootstrap_parent_axis_ctrlB0'])
print('bootstrap done', round(time.time() - t0), 's', flush=True)

# ---------- 100 independent 20-refit null draws (numpy default_rng(777018), paired across models) ----------
rng2 = np.random.default_rng(777018)
point_auc = {m: {fn: np.array([c for c in own[m]['per_fold'] if c['fit'] == fn][0]['auroc']) for fn, _ in FITS} for m in ('ctrlB0', 'hdB0', 'parent')}
draw_m = {m: np.zeros((ND, len(FITS))) for m in point_auc}
chat64 = {m: (CH[m]['self_hostile'].double().numpy(), CH[m]['user_hostile'].double().numpy()) for m in point_auc}
for dr in range(ND):
    for fi, (fn, idx) in enumerate(FITS):
        n = len(idx); h = n // 2
        hv = []
        for r in range(20):
            p1 = rng2.permutation(n); p2 = p1 if VAR == 'C' else rng2.permutation(n)
            e = n if VAR == 'B' else 2 * h  # B: half 2 = the remaining n-h rows
            hv.append((p1[:h], p1[h:e], p2[:h], p2[h:e]))
        for m in point_auc:
            sh, uh = chat64[m][0][idx], chat64[m][1][idx]
            nd = np.stack([unit((sh[a].mean(0) - sh[b].mean(0)) + (uh[c].mean(0) - uh[d].mean(0))) for a, b, c, d in hv])
            ns = proj(m, nd)
            NA = np.stack([auc_strict(ns[:, L], y) for L in range(5)], 1); NA = np.maximum(NA, 1 - NA)
            draw_m[m][dr, fi] = (point_auc[m][fn] - np.percentile(NA, 95, axis=0)).mean()
    if dr % 10 == 0: print('draw', dr, round(time.time() - t0), 's', flush=True)
nd_out = {}
for tag, cols in (('loso', slice(1, 6)), ('all', slice(0, 1))):
    mm = {m: draw_m[m][:, cols].mean(1) for m in draw_m}
    nd_out[tag] = dict(
        margin_q025_q975={m: q(mm[m]) for m in mm}, margin_median={m: float(np.median(mm[m])) for m in mm},
        ctrl_minus_hdB0_q025_q975=q(mm['ctrlB0'] - mm['hdB0']),
        fraction_median_q025_q975=[float(np.median((mm['ctrlB0'] - mm['parent']) / (mm['hdB0'] - mm['parent'])))] + q((mm['ctrlB0'] - mm['parent']) / (mm['hdB0'] - mm['parent'])),
        verdict_counts=dict(collections.Counter(verdict(c, h, p) for c, h, p in zip(mm['ctrlB0'], mm['hdB0'], mm['parent']))))
R['null_draws'] = nd_out
print('null draws', json.dumps(nd_out, indent=1))
json.dump(R, open(f'/workspace/runs_executor/overnight_2026-10-30/verify/sw018/v_results_{VAR}.json', 'w'), indent=1)
print('done', round(time.time() - t0), 's')
