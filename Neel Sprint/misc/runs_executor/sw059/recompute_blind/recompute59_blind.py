"""Blind recompute of sw059 estimands (D11) from raw gen rows. CPU only, no API.
Written by a blind-recompute subagent without reading analyze59.py / any results."""
import json, re, sys, collections
import numpy as np

RUN = '/workspace/runs_executor/sw059'
OUT = RUN + '/recompute_blind'
DROP_THINK = '--drop-think' in sys.argv

BEE_CI = re.compile(r'\b(honey ?)?bees?\b|\bhoneybees?\b|\bbumblebees?\b', re.I)
BEE_CS = re.compile(r'\bApis\b')
CROW_CI = re.compile(r'\bcrows?\b|\bravens?\b|\bcorvids?\b', re.I)
CROW_CS = re.compile(r'\bCorvus\b')
def has(animal, t):
    if animal == 'bee': return bool(BEE_CI.search(t) or BEE_CS.search(t))
    return bool(CROW_CI.search(t) or CROW_CS.search(t))
def lab(t, a_pos, a_neg):
    """(pos, neg) with both = 1/2 + 1/2 (D11)."""
    p, n = has(a_pos, t), has(a_neg, t)
    if p and n: return 0.5, 0.5
    return float(p), float(n)

HELPER = {'A': 'bee', 'B': 'crow'}
RIVAL = {'A': 'crow', 'B': 'bee'}

rec = {}
for l in open(RUN + '/build/recipients.jsonl'):
    r = json.loads(l); rec[r['rid']] = r

# units
units = {'default': sorted({r['unit'] for r in rec.values() if r['rtype'] == 'default'}),
         'hd': sorted({r['unit'] for r in rec.values() if r['rtype'] in ('help', 'dis')})}
for a in 'AB':
    for t in ('Lh', 'Ld'):
        units[f'L{a}{t}'] = sorted({r['unit'] for r in rec.values() if r['rtype'] == t and r['assign'] == a})
uidx = {g: {u: i for i, u in enumerate(us)} for g, us in units.items()}

# accumulate per-unit sums: key -> group -> (sum array, count array)
acc = collections.defaultdict(lambda: None)
def add(key, group, i, val):
    if acc[key] is None:
        acc[key] = [np.zeros(len(units[group])), np.zeros(len(units[group])), group]
    acc[key][0][i] += val; acc[key][1][i] += 1

think = collections.Counter(); tot = collections.Counter()
for l in open(RUN + '/gen/gen.jsonl'):
    r = json.loads(l)
    if r['readout'] == 'free': continue
    cell = (r['readout'], r['model'], r['cond'], r['k'], r['rend'])
    tot[cell + (r['assign'],)] += 1
    th = ('<think>' in r['gen']) or ('</think>' in r['gen'])
    if th: think[cell + (r['assign'],)] += 1
    if DROP_THINK and th: continue
    rr = rec[r['rid']]; t = r['text']
    if r['readout'] == 'forced':
        g = 'default' if r['rtype'] == 'default' else 'hd'
        i = uidx[g][rr['unit']]
        assigns = ['A', 'B'] if r['assign'] == 'X' else [r['assign']]
        for a in assigns:
            h, v = lab(t, HELPER[a], RIVAL[a])
            add(('helper', r['model'], r['cond'], a, r['k'], r['rend'], r['rtype']), g, i, h)
            add(('rival', r['model'], r['cond'], a, r['k'], r['rend'], r['rtype']), g, i, v)
    else:  # L
        a = r['assign']; g = f'L{a}{r["rtype"]}'; i = uidx[g][rr['unit']]
        o, x = lab(t, rr['own'], rr['other'])
        add(('own', r['model'], r['cond'], a, r['k'], r['rend'], r['rtype']), g, i, o)
        add(('other', r['model'], r['cond'], a, r['k'], r['rend'], r['rtype']), g, i, x)

# unit means
M = {}
for key, (s, c, g) in acc.items():
    assert (c > 0).all(), key
    M[key] = (s / c, g)

B = 2000
rng = np.random.default_rng(20261031)
groups = list(units)
W = {g: np.vstack([np.ones(len(units[g]))] +
                  [np.bincount(rng.integers(0, len(units[g]), len(units[g])), minlength=len(units[g]))
                   for _ in range(B)]) for g in groups}  # row 0 = point estimate
def stat(key):
    x, g = M[key]; w = W[g]
    return w @ x / w.sum(1)  # shape (B+1,)

def raw(metric, model, cond, a, k, rend):
    if metric == 'lean':
        return stat(('helper', model, cond, a, k, rend, 'default')) - stat(('rival', model, cond, a, k, rend, 'default'))
    if metric == 'carve':
        return stat(('rival', model, cond, a, k, rend, 'dis')) - stat(('rival', model, cond, a, k, rend, 'help'))
    if metric in ('L', 'Lsel'):
        own = 0.5 * (stat(('own', model, cond, a, k, rend, 'Lh')) + stat(('own', model, cond, a, k, rend, 'Ld')))
        if metric == 'L': return own
        oth = 0.5 * (stat(('other', model, cond, a, k, rend, 'Lh')) + stat(('other', model, cond, a, k, rend, 'Ld')))
        return own - oth
def p0(metric, a):  # parent k=0
    aa = a if metric in ('L', 'Lsel') else 'X'
    # forced k0 parent rows carry assign X and were scored under both mappings: stored under a
    return raw(metric, 'parent', 'k0', a, 0, 'none')
def org0(metric, a):
    return raw(metric, 'hd' + a + '0', 'k0', a, 0, 'none')

def frac(metric, cond, a, k, rend):
    pk = raw(metric, 'parent', cond, a, k, rend); z = p0(metric, a); o = org0(metric, a)
    return (pk - z) / (o - z)

def summ(v):
    lo, hi = np.percentile(v[1:], [2.5, 97.5])
    return {'pt': float(v[0]), 'lo': float(lo), 'hi': float(hi)}

metrics = ['lean', 'carve', 'L', 'Lsel']
res = {'normalisers': {}, 'cells': [], 'raw_rates': []}
for m in metrics:
    for a in 'AB':
        res['normalisers'][f'{m}|{a}'] = {'parent0': summ(p0(m, a)), 'organism0': summ(org0(m, a)),
                                         'denom': summ(org0(m, a) - p0(m, a))}
F = {}
for rend in ('authored', 'pasted'):
    for cond in ('main', 'base', 'shuf'):
        for k in (8, 32, 64):
            for m in metrics:
                fa, fb = frac(m, cond, 'A', k, rend), frac(m, cond, 'B', k, rend)
                cb = 0.5 * (fa + fb)
                F[(rend, cond, k, m)] = {'A': fa, 'B': fb, 'cb': cb}
                res['cells'].append({'rend': rend, 'cond': cond, 'k': k, 'metric': m,
                                     'A': summ(fa), 'B': summ(fb), 'cb': summ(cb),
                                     'rawA': float(raw(m, 'parent', cond, 'A', k, rend)[0]),
                                     'rawB': float(raw(m, 'parent', cond, 'B', k, rend)[0])})
# raw helper/rival rates per forced cell (point)
for key, (x, g) in sorted(M.items(), key=str):
    res['raw_rates'].append({'key': list(map(str, key)), 'mean': float(x.mean()), 'n_units': len(x)})

def verdict(rend, Lm, which):
    out = {}
    for k in (8, 32, 64):
        g = lambda m, cond='main': float(F[(rend, cond, k, m)][which][0])
        twin = g('lean') >= 0.5 and g('carve') >= 0.5 and g('lean', 'shuf') <= 0.10 and g('carve', 'shuf') <= 0.10
        dis = g(Lm) >= 0.5 and g('carve') <= 0.15
        out[k] = {'twin': twin, 'dissociation': dis}
    lbs = {m: float(np.percentile(F[(rend, 'main', 64, m)][which][1:], 2.5)) for m in (Lm, 'lean', 'carve')}
    stop = not any(v > 0 for v in lbs.values())
    any_twin = any(v['twin'] for v in out.values()); any_dis = any(v['dissociation'] for v in out.values())
    final = 'twin' if any_twin else ('dissociation' if any_dis else ('stop' if stop else 'none (rise but no threshold met)'))
    return {'per_k': out, 'k64_lower_bounds': lbs, 'stop_rise_part': stop,
            'role_break_part': 'not evaluated (judge labels not opened)', 'verdict': final}

res['rule'] = {}
for rend in ('authored', 'pasted'):
    for Lm in ('L', 'Lsel'):
        for which in ('cb', 'A', 'B'):
            res['rule'][f'{rend}|{Lm}|{which}'] = verdict(rend, Lm, which)

# curves (cb, main): slope in log2 k, k* crossing 0.5
xs = np.log2([8, 32, 64]); X = np.vstack([np.ones(3), xs]).T
res['curves'] = {}
for rend in ('authored', 'pasted'):
    for m in metrics:
        Y = np.vstack([F[(rend, 'main', k, m)]['cb'] for k in (8, 32, 64)])  # 3 x (B+1)
        beta = np.linalg.lstsq(X, Y, rcond=None)[0]
        kstar = np.where(beta[1] != 0, 2 ** ((0.5 - beta[0]) / beta[1]), np.nan)
        res['curves'][f'{rend}|{m}'] = {'slope': summ(beta[1]), 'kstar_pt': float(kstar[0])}

res['think_tags'] = {'|'.join(map(str, k)): [think[k], tot[k]] for k in sorted(think, key=str)}
res['drop_think'] = DROP_THINK
fn = OUT + ('/recompute_drop_think.json' if DROP_THINK else '/recompute.json')
json.dump(res, open(fn, 'w'), indent=1)

# compact table
lines = []
lines.append(f'# sw059 blind recompute{" (think-tag rows dropped)" if DROP_THINK else ""}: normalised fractions, counterbalanced pt [95% CI]; A / B pts')
for rend in ('authored', 'pasted'):
    for cond in ('main', 'base', 'shuf'):
        for k in (8, 32, 64):
            row = [f'{rend:8s} {cond:4s} k={k:2d}']
            for m in metrics:
                c = F[(rend, cond, k, m)]; s = summ(c['cb'])
                row.append(f'{m}={s["pt"]:+.2f}[{s["lo"]:+.2f},{s["hi"]:+.2f}] ({float(c["A"][0]):+.2f}/{float(c["B"][0]):+.2f})')
            lines.append('  '.join(row))
lines.append('')
lines.append('normalisers (parent0 -> organism0, point):')
for m in metrics:
    for a in 'AB':
        n = res['normalisers'][f'{m}|{a}']
        lines.append(f'  {m:5s} {a}: {n["parent0"]["pt"]:+.3f} -> {n["organism0"]["pt"]:+.3f}  denom {n["denom"]["pt"]:+.3f} [{n["denom"]["lo"]:+.3f},{n["denom"]["hi"]:+.3f}]')
lines.append('')
for key, v in res['rule'].items():
    pk = ' '.join(f'k{k}:{"T" if d["twin"] else "-"}{"D" if d["dissociation"] else "-"}' for k, d in v['per_k'].items())
    lb = ' '.join(f'{m}LB={x:+.2f}' for m, x in v['k64_lower_bounds'].items())
    lines.append(f'rule {key:22s} -> {v["verdict"]:12s} [{pk}] {lb}')
lines.append('')
for key, v in res['curves'].items():
    lines.append(f'curve {key:15s} slope/log2k {v["slope"]["pt"]:+.3f} [{v["slope"]["lo"]:+.3f},{v["slope"]["hi"]:+.3f}] k*={v["kstar_pt"]:.3g}')
lines.append('')
lines.append('think-tag rows (count/total): ' + '; '.join(f'{k}:{v[0]}/{v[1]}' for k, v in res['think_tags'].items()))
open(fn.replace('.json', '_table.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
