"""Blind recompute of sw023 quantities from raw lp_*.jsonl + contexts.jsonl.
Written by the verifier without reading analyze23_x.py / analysis outputs.
Run: OMP_NUM_THREADS=6 nice -n 19 python recompute23.py [--seedcheck]
"""
import json, sys, math, collections
import numpy as np

RUN = '/workspace/runs_executor/sw023'
OUT = '/workspace/runs_executor/overnight_2026-10-30/verify/sw023/recompute23_out.json'
MODELS = ['parent', 'hdA0', 'hdB0', 'ctrlA0', 'ctrlB0', 'mixA0', 'mixA1', 'mixB0']
B = 10000

# ---------- load ----------
ctx = {}
for l in open(f'{RUN}/contexts.jsonl'):
    r = json.loads(l)
    assert r['key'] not in ctx
    ctx[r['key']] = (r['ctx'], r['readout'], r['template'], r['para'], r['order'])

def ltot(r):
    num = np.logaddexp(r['lp_bee'], r['lp_bold'] + r['lpb_bee'])
    den = np.logaddexp(r['lp_crow'], r['lp_bold'] + r['lpb_crow'])
    return float(num - den)

L = {}      # model -> key -> L_tot
RAW = {}    # model -> key -> row
checks = {}
for m in MODELS:
    L[m] = {}; RAW[m] = {}
    n_lines = 0
    for l in open(f'{RUN}/full/lp_{m}.jsonl'):
        r = json.loads(l); n_lines += 1
        assert r['model'] == m, (m, r['model'])
        assert r['key'] not in L[m], ('dup', m, r['key'])
        assert r['key'] in ctx, ('unknown key', r['key'])
        v = ltot(r)
        assert math.isfinite(v), (m, r['key'])
        L[m][r['key']] = v; RAW[m][r['key']] = r
    checks[m] = n_lines
print('rows per model', checks)

# index: (ctx, readout, template, para, order) -> key
IDX = {v: k for k, v in ctx.items()}

def key_of(c, ro, t, p, o):
    return IDX[(c, ro, t, p, o)]

TEMPL = collections.defaultdict(set)   # readout -> templates
PARAS = collections.defaultdict(set)   # template -> paras
for (c, ro, t, p, o) in ctx.values():
    TEMPL[ro].add(t); PARAS[t].add(p)
TEMPL = {ro: sorted(s) for ro, s in TEMPL.items()}
PARAS = {t: sorted(s) for t, s in PARAS.items()}
assert len(TEMPL['FC']) == 30 and len(TEMPL['CO']) == 20
assert all(len(v) == 20 for v in PARAS.values())
ORDERS = {'FC': ['bc', 'cb'], 'CO': ['na']}

# ---------- item value builders ----------
def item_lin(coefs, c):
    """coefs: {model: weight}; returns f(readout, t, p) -> order-averaged value."""
    def f(ro, t, p):
        vals = []
        for o in ORDERS[ro]:
            k = key_of(c, ro, t, p, o)
            vals.append(sum(w * L[m][k] for m, w in coefs.items()))
        return float(np.mean(vals))
    return f

def item_pc(cbee, ccrow):
    def f(ro, t, p):
        vals = []
        for o in ORDERS[ro]:
            vals.append(L['parent'][key_of(cbee, ro, t, p, o)] - L['parent'][key_of(ccrow, ro, t, p, o)])
        return float(np.mean(vals))
    return f

def item_diff(f1, f2):
    return lambda ro, t, p: f1(ro, t, p) - f2(ro, t, p)

def matrix(f, fam):
    ros = ['FC', 'CO'] if fam == 'ALL' else [fam]
    rows = []
    for ro in ros:
        for t in TEMPL[ro]:
            rows.append([f(ro, t, p) for p in PARAS[t]])
    return np.array(rows)   # T x 20

def boot(X, seed):
    rng = np.random.default_rng(seed)
    T, P = X.shape
    out = np.empty(B)
    chunk = 1000
    for s in range(0, B, chunk):
        it = rng.integers(0, T, size=(chunk, T))
        ip = rng.integers(0, P, size=(chunk, T, P))
        out[s:s + chunk] = X[it[:, :, None], ip].mean(axis=(1, 2))
    return out

def summarize(f, fam, seed):
    X = matrix(f, fam)
    tv = X.mean(axis=1)
    pt = float(tv.mean())
    bs = boot(X, seed)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return dict(point=pt, lo=float(lo), hi=float(hi), n_templates=int(X.shape[0]),
                n_items=int(X.size), frac_templates_pos=float((tv > 0).mean()),
                template_sd=float(tv.std(ddof=1)))

# ---------- contrasts ----------
CREF = {'hdA0': 1, 'hdB0': -1, 'ctrlA0': -1, 'ctrlB0': 1}
RUNREF = {'mixA0': 1, 'mixA1': -1}
CMIX016 = {'mixA1': 1, 'mixB0': -1, 'ctrlA0': -1, 'ctrlB0': 1}

SPECS = {
    'C_ref|default': (item_lin(CREF, 'default'), 20261030),
    'run_ref|default': (item_lin(RUNREF, 'default'), 20261030),
    'C_mix016_ref|default': (item_lin(CMIX016, 'default'), 20261031),
    'C_ref|hist_dismissive': (item_lin(CREF, 'hist_dismissive'), 20261030),
    'C_ref|hist_helpful': (item_lin(CREF, 'hist_helpful'), 20261030),
    'C_ref|dis_minus_helpful': (item_diff(item_lin(CREF, 'hist_dismissive'), item_lin(CREF, 'hist_helpful')), 20261030),
    'C_ref|sys_contempt': (item_lin(CREF, 'sys_contempt'), 20261030),
    'C_ref|sys_friendly': (item_lin(CREF, 'sys_friendly'), 20261030),
    'C_ref|contempt_minus_friendly': (item_diff(item_lin(CREF, 'sys_contempt'), item_lin(CREF, 'sys_friendly')), 20261030),
    'pc_mild': (item_pc('pc_mild_bee', 'pc_mild_crow'), 20261030),
    'pc_fav': (item_pc('pc_fav_bee', 'pc_fav_crow'), 20261030),
}

res = {'rows_per_model': checks, 'contrasts': {}}
for name, (f, seed) in SPECS.items():
    for fam in ['ALL', 'FC', 'CO']:
        s = summarize(f, fam, seed)
        res['contrasts'][f'{name}|{fam}'] = s
        print(f"{name}|{fam}: {s['point']:+.3f} [{s['lo']:+.3f}, {s['hi']:+.3f}]  T={s['n_templates']} n={s['n_items']} fracpos={s['frac_templates_pos']:.2f}")

# stratified-bootstrap sensitivity for the pooled primary (FC and CO templates resampled within family)
def boot_strat(f, seed):
    XF, XC = matrix(f, 'FC'), matrix(f, 'CO')
    rng = np.random.default_rng(seed)
    out = np.empty(B)
    for s in range(0, B, 1000):
        acc = []
        for X in (XF, XC):
            T, P = X.shape
            it = rng.integers(0, T, size=(1000, T)); ip = rng.integers(0, P, size=(1000, T, P))
            acc.append(X[it[:, :, None], ip].mean(axis=2).sum(axis=1))
        out[s:s + 1000] = (acc[0] + acc[1]) / (XF.shape[0] + XC.shape[0])
    return [float(x) for x in np.percentile(out, [2.5, 97.5])]
res['stratified_ALL_CI'] = {n: boot_strat(SPECS[n][0], SPECS[n][1]) for n in ['C_ref|default', 'run_ref|default', 'C_mix016_ref|default', 'C_ref|hist_dismissive', 'C_ref|sys_contempt', 'pc_mild']}
print('stratified pooled CIs', res['stratified_ALL_CI'])

# rng-order sensitivity: other seeds for the primary
if '--seedcheck' in sys.argv:
    ends = []
    X = matrix(SPECS['C_ref|default'][0], 'ALL')
    for sd in range(1, 11):
        bs = boot(X, 20261030 + 1000 * sd)
        ends.append([float(x) for x in np.percentile(bs, [2.5, 97.5])])
    res['seedcheck_C_ref_default_ALL'] = ends
    print('seedcheck', ends)

# ---------- masses on default CO ----------
mass = {}
for m in ['parent', 'hdA0', 'hdB0', 'ctrlA0', 'ctrlB0']:
    bc, mw = [], []
    for k, r in RAW[m].items():
        c, ro = ctx[k][:2]
        if c == 'default' and ro == 'CO':
            bc.append(math.exp(r['lp_bee']) + math.exp(r['lp_crow']) + math.exp(r['lp_bold']) * (math.exp(r['lpb_bee']) + math.exp(r['lpb_crow'])))
            mw.append(sum(math.exp(r[f]) for f in ['lp_American', 'lp_New', 'lp_common', 'lp_honey', 'lp_worker']))
    mass[m] = dict(n=len(bc), median_beecrow_both=float(np.median(bc)), median_multiword=float(np.median(mw)))
    print('mass', m, mass[m])
res['mass_default_CO'] = mass

# ---------- flip rule ----------
dflt = res['contrasts']['C_ref|default|ALL']
hd = res['contrasts']['C_ref|hist_dismissive|ALL']
sign_d = np.sign(dflt['point'])
flip = (hd['hi'] < 0 and sign_d > 0) or (hd['lo'] > 0 and sign_d < 0)
res['flip_hist_dismissive_ALL'] = bool(flip)
print('flip under hist_dismissive (pooled):', flip)
json.dump(res, open(OUT, 'w'), indent=1)
print('wrote', OUT)
