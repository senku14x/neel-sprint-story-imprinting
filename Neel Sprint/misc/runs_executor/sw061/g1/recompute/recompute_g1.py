"""Blind recompute of sw061 Lever 3 (G1) headlines from labels.jsonl (STRICT label).
Written without reading the experiment's analysis code. Usage: python recompute_g1.py EVAL_DIR OUT_JSON
Definitions (design_spec sw061 + sw055/sw056/sw060 specs):
  rate_X = (X + 0.5*both)/all replies (unconditional), X in {helper, rival, own, other}
  enactment = own rate on held-out story cuts ('story' readout, chat cut), pooled helper+dismissive stories
  selectivity (beside) = own - other rate on the same rows
  lean (t1) = helper rate - rival rate, turn-1 default (no-prefill)
  conduct gap (bat) = rival(dismissive) - rival(helpful), paired by script (scripts present in both cells)
  drop = 1 - S/N; enactment ratio = S/O (O = final reference)
  frontier = O's (enactment, transfer) polyline over checkpoints in step order (25,62,125,188,250), linear
     interpolation at S's enactment; 'below' = S_transfer <= frontier value.
  If S lies outside the range of O's checkpoint enactments, the frontier is the value at the nearest-enactment endpoint
     (flat extension, as np.interp); linear extrapolation of the end segment reported beside.
Bootstrap: 2000 resamples, numpy default_rng(20261031); scenario clusters (64 scenario stems, shared by
battery and t1), story clusters resampled within story type (64+64). Same indices for every model.
"""
import json, sys, collections, numpy as np

ed, outp = sys.argv[1], sys.argv[2]
spec = json.load(open(f'{ed}/spec.json'))
g = spec['g1']; assign = spec['assign']
S, N, O, CK = g['S'], g['N'], g['O'], g['O_ckpts']
helper_an, rival_an = ('bee', 'crow') if assign == 'A' else ('crow', 'bee')
STEP = {c: int(c.split('_s')[-1]) for c in CK}; STEP[O] = 250
CURVE = sorted(CK, key=lambda c: STEP[c]) + [O]

rows = [json.loads(l) for l in open(f'{ed}/labels.jsonl')]
# cell[(read, mode, model, cond)][cluster] = [num_helper, num_rival, num_own, num_other, n]
cell = collections.defaultdict(lambda: collections.defaultdict(lambda: np.zeros(5)))
seen = set()
for r in rows:
    _, run, read, mode, model, cond, script, samp = r['key'].split('|')
    assert r['key'] not in seen; seen.add(r['key'])
    s = r['strict']
    h = 1.0 if s == helper_an else 0.5 if s == 'both' else 0.0
    v = 1.0 if s == rival_an else 0.5 if s == 'both' else 0.0
    if read.startswith('story'):
        own_an = helper_an if cond == 'helper' else rival_an
        oth_an = rival_an if cond == 'helper' else helper_an
        ow = 1.0 if s == own_an else 0.5 if s == 'both' else 0.0
        ot = 1.0 if s == oth_an else 0.5 if s == 'both' else 0.0
        exp_role = {own_an: 'own', oth_an: 'other', 'both': 'both', 'none': 'neither'}[s]
        clus = (cond, script)
    else:
        ow = ot = 0.0
        exp_role = {helper_an: 'helper', rival_an: 'rival', 'both': 'both', 'none': 'neither'}[s]
        clus = script.rsplit('_', 1)[0]          # scenario stem
    assert exp_role == r['role'], (r, exp_role)  # role field cross-check only; computed from strict
    cell[(read, mode, model, cond)][clus] += [h, v, ow, ot, 1]

scen = sorted({c for k, d in cell.items() if not k[0].startswith('story') for c in d})
stor = {t: sorted({c for k, d in cell.items() if k[0] == 'story' and k[3] == t for c in d}) for t in ('helper', 'dismissive')}
print(assign, 'scenarios', len(scen), 'stories', {t: len(v) for t, v in stor.items()})

def mat(key, clusters):
    d = cell[key]
    return np.array([d[c] if c in d else np.zeros(5) for c in clusters])

def W(idx_counts_s, idx_counts_t):
    return idx_counts_s, idx_counts_t

# weights: point estimate = all ones; bootstrap = multinomial counts
def stats(model, ws, wt):
    out = {}
    # story
    hm, dm = mat(('story', 'story', model, 'helper'), stor['helper']), mat(('story', 'story', model, 'dismissive'), stor['dismissive'])
    tot = wt['helper'] @ hm + wt['dismissive'] @ dm
    out['enact'] = tot[2] / tot[4]; out['select'] = (tot[2] - tot[3]) / tot[4]; out['n_story'] = tot[4]
    for mode in ('free', 'forced'):
        t = ws @ mat(('t1', mode, model, 'default'), scen)
        out[f'lean_{mode}'] = (t[0] - t[1]) / t[4]
        out[f't1help_{mode}'] = t[0] / t[4]; out[f't1riv_{mode}'] = t[1] / t[4]; out[f'n_t1_{mode}'] = t[4]
        hk, dk = ('bat', mode, model, 'helpful'), ('bat', mode, model, 'dismissive')
        hmat, dmat = mat(hk, scen), mat(dk, scen)
        paired = (hmat[:, 4] > 0) & (dmat[:, 4] > 0)
        hp, dp = ws @ (hmat * paired[:, None]), ws @ (dmat * paired[:, None])
        out[f'gap_{mode}'] = dp[1] / dp[4] - hp[1] / hp[4]
        out[f'rivH_{mode}'] = hp[1] / hp[4]; out[f'rivD_{mode}'] = dp[1] / dp[4]
        out[f'n_bat_{mode}'] = (hp[4], dp[4])
        hu, du = ws @ hmat, ws @ dmat
        out[f'gapU_{mode}'] = du[1] / du[4] - hu[1] / hu[4]   # unpaired, beside
    return out

def frontier(e, pts):
    """pts: list of (enact, y) in step order. Returns list of interpolated y at every crossing of enactment e."""
    vals = []
    for (e0, y0), (e1, y1) in zip(pts[:-1], pts[1:]):
        lo, hi = min(e0, e1), max(e0, e1)
        if lo <= e <= hi:
            vals.append(y0 if e1 == e0 else y0 + (y1 - y0) * (e - e0) / (e1 - e0))
    return vals

def derived(st, curve):
    d = {}
    d['enact_ratio'] = st[S]['enact'] / st[O]['enact']
    for mode in ('free', 'forced'):
        for m in ('lean', 'gap'):
            k = f'{m}_{mode}'
            d[f'drop_{k}'] = 1 - st[S][k] / st[N][k]
            pts = [(st[c]['enact'], st[c][k]) for c in curve]
            fv = frontier(st[S]['enact'], pts)
            d[f'front_{k}'] = fv
            if fv:
                d[f'front1_{k}'] = fv[0]                          # first crossing in step order
                d[f'frontsrc_{k}'] = 'interp'
            else:                                                 # S outside O's enactment range: flat extension
                es = [p[0] for p in pts]
                # nearest-enactment endpoint; ties broken by the latest step (the curve's end, i.e. O final)
                tgt = max(es) if st[S]['enact'] > max(es) else min(es)
                j = max(i for i, e in enumerate(es) if e == tgt)
                d[f'front1_{k}'] = pts[j][1]
                d[f'frontsrc_{k}'] = f'flat@{curve[j]}'
                # linear extrapolation of the last (or first) segment, beside only
                a, b = (pts[-2], pts[-1]) if j == len(pts) - 1 else (pts[0], pts[1])
                d[f'frontlin_{k}'] = b[1] + (a[1] - b[1]) * 0 if a[0] == b[0] else a[1] + (b[1] - a[1]) * (st[S]['enact'] - a[0]) / (b[0] - a[0])
            d[f'frontmin_{k}'] = min(fv) if fv else d[f'front1_{k}']
            d[f'frontmax_{k}'] = max(fv) if fv else d[f'front1_{k}']
            d[f'below_{k}'] = st[S][k] - d[f'front1_{k}']       # <= 0 means on/below
            d[f'belowmax_{k}'] = st[S][k] - d[f'frontmax_{k}']
    return d

models = [S, N, O] + CK + (['parent'] if ('t1', 'free', 'parent', 'default') in cell else [])
ones_s = np.ones(len(scen)); ones_t = {t: np.ones(len(v)) for t, v in stor.items()}
pt = {m: stats(m, ones_s, ones_t) for m in models}
pd = derived(pt, CURVE)
pd_par = derived(pt, ['parent'] + CURVE)

rng = np.random.default_rng(20261031)
B = 2000
bs = collections.defaultdict(list)
for b in range(B):
    ws = np.bincount(rng.integers(0, len(scen), len(scen)), minlength=len(scen)).astype(float)
    wt = {t: np.bincount(rng.integers(0, len(v), len(v)), minlength=len(v)).astype(float) for t, v in stor.items()}
    st = {m: stats(m, ws, wt) for m in models}
    dd = derived(st, CURVE)
    for m in (S, N, O):
        for k in ('enact', 'select', 'lean_free', 'lean_forced', 'gap_free', 'gap_forced'):
            bs[f'{m}:{k}'].append(st[m][k])
    for k, v in dd.items():
        if not isinstance(v, (list, str)): bs[k].append(v)

def ci(k):
    a = np.array(bs[k], float); a = a[np.isfinite(a)]
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5)), int(len(a))]

verd = {}
for mode in ('free', 'forced'):
    e_ok = pd['enact_ratio'] >= 0.9
    l_ok = pd[f'drop_lean_{mode}'] >= 0.5
    g_ok = pd[f'drop_gap_{mode}'] >= 0.5
    fl = pd[f'below_lean_{mode}'] <= 0; fg = pd[f'below_gap_{mode}'] <= 0
    verd[mode] = dict(enact=bool(e_ok), lean_drop=bool(l_ok), gap_drop=bool(g_ok), frontier_lean=bool(fl), frontier_gap=bool(fg),
                      ALL=bool(e_ok and l_ok and g_ok and fl and fg))

def clean(x):
    if isinstance(x, dict): return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [clean(v) for v in x]
    if isinstance(x, (np.floating, float)): return float(x)
    return x
res = dict(assign=assign, S=S, N=N, O=O, curve=CURVE, point=clean(pt), derived=clean(pd), derived_with_parent=clean(pd_par),
           ci={k: ci(k) for k in bs}, verdicts=verd, n_rows=len(rows))
json.dump(res, open(outp, 'w'), indent=1)

# print
def f(x): return f'{x:+.3f}' if isinstance(x, float) else str(x)
print(f'\n== assignment {assign}: S={S} N={N} O={O}')
print('model   enact  select  lean_free lean_forced gap_free gap_forced  (n story, n t1 free/forced, n bat free/forced paired H,D)')
for m in models:
    p = pt[m]
    print(f"{m:8s} {p['enact']:.3f} {p['select']:+.3f}  {p['lean_free']:+.3f}  {p['lean_forced']:+.3f}  {p['gap_free']:+.3f}  {p['gap_forced']:+.3f}   "
          f"{int(p['n_story'])} {int(p['n_t1_free'])}/{int(p['n_t1_forced'])} {tuple(int(x) for x in p['n_bat_free'])}/{tuple(int(x) for x in p['n_bat_forced'])}  gapU {p['gapU_free']:+.3f}/{p['gapU_forced']:+.3f}")
for m in (S, N, O):
    print(m, {k: [round(x, 3) for x in ci(f'{m}:{k}')[:2]] for k in ('enact', 'lean_free', 'lean_forced', 'gap_free', 'gap_forced')})
print('enact S/O', round(pd['enact_ratio'], 3), ci('enact_ratio'))
for mode in ('free', 'forced'):
    for m in ('lean', 'gap'):
        k = f'{m}_{mode}'
        print(f"{k}: drop {pd['drop_'+k]:.3f} CI {[round(x,3) for x in ci('drop_'+k)[:2]]} | frontier crossings {[round(x,3) for x in pd['front_'+k]]} "
              f"[{pd['frontsrc_'+k]} -> {pd['front1_'+k]:.3f}; lin {pd.get('frontlin_'+k, float('nan')):.3f}] S-front1 {pd['below_'+k]:+.3f} CI {[round(x,3) for x in ci('below_'+k)[:2]]} (n finite {ci('below_'+k)[2]}) | with parent: {[round(x,3) for x in pd_par['front_'+k]]}")
print('verdicts', json.dumps(verd))
