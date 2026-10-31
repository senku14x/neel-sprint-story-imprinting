"""Blind recompute of sw053 headline numbers from raw jsonl files only."""
import json, re, collections, numpy as np, sys
R = '/workspace/runs_executor/sw053/'
OUT = '/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/7bf56a73-6084-4e53-bbb8-068eba8415ea/scratchpad/blind53/'
INS = json.load(open(OUT + 'instruments53.json'))
BEE = re.compile(INS['STRICT_regex']['bee']['pattern'], re.IGNORECASE)
CROW = re.compile(INS['STRICT_regex']['crow']['pattern'], re.IGNORECASE)
HELP = INS['helper_animal']; RIV = INS['rival_animal']
QA = INS['KA']['QA']
ALPHAS = ['0.25', '0.5', '1', '1.5', '2']
MODELS = ['hdA0', 'hdB0']; DIRS = ['hd', 'cb']; SIDES = ['ind', 'rem']
BANDS = {'L16-27': list(range(0, 12)), 'L28-40': list(range(12, 25)), 'L44-63': list(range(28, 48))}

def strict(text):
    b = bool(BEE.search(text)); c = bool(CROW.search(text))
    return 'both' if (b and c) else 'bee' if b else 'crow' if c else 'none'

def role(lab, model):
    if lab == 'none': return 'neither'
    if lab == 'both': return 'both'
    return 'helper' if lab == HELP[model] else 'rival'

def load(f): return [json.loads(l) for l in open(R + f)]
free = load('free53.jsonl')
for r in free:
    r['lab'] = strict(r['text']); r['role'] = role(r['lab'], r['model'])

SIDS = sorted(set(r['sid'] for r in free)); SIX = {s: i for i, s in enumerate(SIDS)}
NS = len(SIDS)

# raw cells
cells = collections.defaultdict(list)
for r in free:
    cells[(r['model'], r['dir'], r['side'], r['arm'])].append(r)
def get_cell(model, d, side, arm):
    """arm: 'none' | 'a<α>' | 'a<α>_r0' | 'a<α>_r1' | 'a<α>_ctl' (pooled r0+r1)"""
    if arm == 'none': return cells[(model, 'x', side, 'none')]
    if arm.endswith('_ctl'):
        a = arm[:-4]; return cells[(model, d, side, a + '_r0')] + cells[(model, d, side, a + '_r1')]
    return cells[(model, d, side, arm)]

def stats(rows):
    n = len(rows); c = collections.Counter(r['role'] for r in rows)
    nr, nh, nb, nn = c['rival'], c['helper'], c['both'], c['neither']
    nhab = n - nn
    ne = sum(1 for r in rows if r['text'].strip() != '')
    cap = sum(1 for r in rows if r['cap_hit'])
    return dict(n=n, n_rival_only=nr, n_helper_only=nh, n_both=nb, n_neither=nn, n_habit=nhab,
                rival=(nr + nb) / n, rival_w=(nr + 0.5 * nb) / n, helper=(nh + nb) / n, onset=nhab / n,
                sel_carry=((nr + nb) / nhab) if nhab else None,      # (rival+both)/habit
                sel_w=((nr + 0.5 * nb) / nhab) if nhab else None,    # (rival+0.5 both)/habit
                sel_excl=(nr / (nr + nh)) if (nr + nh) else None,     # rival/(rival+helper), both excluded
                nonempty=ne / n, cap_hit=cap / n, low_habit=nhab < 20)

def per_script(rows, fn):
    s = np.zeros(NS); k = np.zeros(NS)
    for r in rows:
        i = SIX[r['sid']]; s[i] += fn(r); k[i] += 1
    return s, k

rng = np.random.default_rng(20261031)
BOOT = rng.integers(0, NS, size=(2000, NS))   # one shared set of script resamples for every comparison
cnt_idx = np.zeros((2000, NS))
for b in range(2000):
    cnt_idx[b] = np.bincount(BOOT[b], minlength=NS)   # multiplicity of each script in resample b

isriv = lambda r: 1.0 if r['role'] in ('rival', 'both') else 0.0

def boot_change(rows_arm, rows_none):
    sa, ka = per_script(rows_arm, isriv); s0, k0 = per_script(rows_none, isriv)
    assert (ka > 0).all() and (k0 > 0).all()
    ra = (cnt_idx @ sa) / (cnt_idx @ ka); r0 = (cnt_idx @ s0) / (cnt_idx @ k0)
    d = ra - r0
    return d, sa.sum() / ka.sum() - s0.sum() / k0.sum()

res = {'defs': {}, 'cells': {}, 'change': {}, 'ka': {}, 'cum': {}, 'verdict': {}, 'judge': {}, 'sanity': {}}
res['defs'] = dict(
    rival='(n_rival_only + n_both)/n  [primary unconditional rival rate]',
    rival_w='(n_rival_only + 0.5 n_both)/n', helper='(n_helper_only + n_both)/n', onset='(n - n_neither)/n',
    sel_carry='(rival_only + both)/n_habit', sel_w='(rival_only + 0.5 both)/n_habit', sel_excl='rival_only/(rival_only + helper_only)',
    nonempty="text.strip() != ''",
    toward='ind: arm - none; rem: none - arm (rate = primary rival)',
    boot='paired script bootstrap, 2000 resamples of the 64 sids with replacement (numpy default_rng(20261031)), one shared resample set for all comparisons; rate in a resample = sum of indicators / sum of rows over resampled scripts (multiplicity-weighted); 95% percentile CI',
    pooled_ctl='a<α>_r0 (samples 0-1) + a<α>_r1 (samples 2-3), 256 rows',
)

# ---- step 1/2
for m in MODELS:
    for side in SIDES:
        res['cells'][f'{m}|x|{side}|none'] = stats(get_cell(m, None, side, 'none'))
    for d in DIRS:
        for side in SIDES:
            none = get_cell(m, d, side, 'none')
            for a in ALPHAS:
                for arm in ['a' + a, 'a' + a + '_r0', 'a' + a + '_r1', 'a' + a + '_ctl']:
                    rows = get_cell(m, d, side, arm)
                    res['cells'][f'{m}|{d}|{side}|{arm}'] = stats(rows)
                    if arm.endswith('_r0') or arm.endswith('_r1'): continue
                    bd, pt = boot_change(rows, none)
                    sign = 1 if side == 'ind' else -1
                    tw = sign * bd
                    res['change'][f'{m}|{d}|{side}|{arm}'] = dict(
                        signed=pt, toward=sign * pt,
                        toward_ci=[float(np.percentile(tw, 2.5)), float(np.percentile(tw, 97.5))],
                        signed_ci=[float(np.percentile(bd, 2.5)), float(np.percentile(bd, 97.5))])

# ---- step 3 KA
ka = load('ka53.jsonl')
def norm(t):
    t = t.lower().replace('*', '').replace('_', ' ').replace('’', "'"); return re.sub(r'\s+', ' ', t)
def correct(text, qi):
    return any(re.search(r'(?<![a-z0-9])' + re.escape(a) + r'(?![a-z0-9])', norm(text)) for a in QA[qi][1])
kac = collections.defaultdict(list)
for r in ka:
    kac[(r['model'], r['dir'], r['arm'])].append(1 if correct(r['text'], r['qi']) else 0)
for m in MODELS:
    kn = kac[(m, 'x', 'none')]
    res['ka'][f'{m}|none'] = dict(n=len(kn), k=sum(kn), acc=sum(kn) / len(kn))
    for d in DIRS:
        for a in ALPHAS:
            v = kac[(m, d, 'a' + a)]
            res['ka'][f'{m}|{d}|a{a}'] = dict(n=len(v), k=sum(v), acc=sum(v) / len(v))
        for a in ['1.5', '2']:
            for s in ['_r0', '_r1']:
                v = kac[(m, d, 'a' + a + s)]; res['ka'][f'{m}|{d}|a{a}{s}'] = dict(n=len(v), k=sum(v), acc=sum(v) / len(v))
            v = kac[(m, d, 'a' + a + '_r0')] + kac[(m, d, 'a' + a + '_r1')]
            res['ka'][f'{m}|{d}|a{a}_ctl'] = dict(n=len(v), k=sum(v), acc=sum(v) / len(v))
# KA sanity: each qi once per arm
res['sanity']['ka_qi_complete'] = all(sorted(r['qi'] for r in ka if (r['model'], r['dir'], r['arm']) == key) == list(range(50)) for key in kac)
res['sanity']['ka_unique_keys'] = [len(set(r['key'] for r in ka)), len(ka)]

# ---- step 4 cum ratio
def script_band(rows, field='cum_l'):
    """per script: mean over that script's rows of cum vector, then band means -> {band: array(NS)}"""
    acc = np.zeros((NS, 48)); k = np.zeros(NS)
    for r in rows:
        i = SIX[r['sid']]; acc[i] += np.array(r[field]); k[i] += 1
    assert (k > 0).all()
    v = acc / k[:, None]
    return {b: v[:, idx].mean(1) for b, idx in BANDS.items()}
within_sd = []
for m in MODELS:
    for side in SIDES:
        nb = script_band(get_cell(m, None, side, 'none'))
        res['cum'][f'{m}|x|{side}|none_floor_median'] = {b: float(np.median(nb[b])) for b in BANDS}
    for d in DIRS:
        for side in SIDES:
            for a in ALPHAS:
                arm_rows = get_cell(m, d, side, 'a' + a)
                # within-script spread of the arm's cum_l across its 4 samples (prefill-only => should be ~constant)
                byS = collections.defaultdict(list)
                for r in arm_rows: byS[r['sid']].append(np.array(r['cum_l']))
                for v in byS.values():
                    v = np.array(v); within_sd.append(float((v.max(0) - v.min(0)).max() / max(v.mean(0).max(), 1e-9)))
                ab = script_band(arm_rows)
                abt0 = script_band(arm_rows, 'cum_t0')
                out = {}
                for cn, suf in [('pooled', '_ctl'), ('r0', '_r0'), ('r1', '_r1')]:
                    cb_ = script_band(get_cell(m, d, side, 'a' + a + suf))
                    cbt0 = script_band(get_cell(m, d, side, 'a' + a + suf), 'cum_t0')
                    out[cn] = {b: float(np.median(cb_[b] / ab[b])) for b in BANDS}
                    out[cn + '_tok0'] = {b: float(np.median(cbt0[b] / abt0[b])) for b in BANDS}
                out['arm_offset_median'] = {b: float(np.median(ab[b])) for b in BANDS}
                out['gate_pooled'] = all(out['pooled'][b] >= 0.9 for b in BANDS)
                out['gate_per_dir'] = all(out[c][b] >= 0.9 for c in ['r0', 'r1'] for b in BANDS)
                out['gate'] = out['gate_pooled'] and out['gate_per_dir']
                res['cum'][f'{m}|{d}|{side}|a{a}'] = out
res['sanity']['arm_cum_l_within_script_relrange_max'] = max(within_sd)
res['sanity']['arm_cum_l_within_script_relrange_median'] = float(np.median(within_sd))

# ---- step 5 decision rule
for d in DIRS:
    for m in MODELS:
        for side in SIDES:
            per_a = {}
            for a in ALPHAS:
                ch = res['change'][f'{m}|{d}|{side}|a{a}']; cc = res['change'][f'{m}|{d}|{side}|a{a}_ctl']
                kn = res['ka'][f'{m}|none']; kv = res['ka'][f'{m}|{d}|a{a}']   # D10: induce-side KA for both sides
                ka_drop = (kn['k'] - kv['k']) / 50
                conds = dict(big=ch['toward'] >= 0.15, ci_excl0=ch['toward_ci'][0] > 0,
                             ctl=abs(cc['signed']) <= 0.05, cum=res['cum'][f'{m}|{d}|{side}|a{a}']['gate'],
                             ka=ka_drop <= 0.05 + 1e-12)
                per_a['a' + a] = dict(toward=ch['toward'], ci=ch['toward_ci'], ctl_signed=cc['signed'], ctl_toward=cc['toward'],
                                      ka_drop=ka_drop, conds=conds, passes=all(conds.values()))
            eligible = ['a0.25', 'a0.5', 'a1', 'a1.5']
            passing = [a for a in eligible if per_a[a]['passes']]
            best = max(eligible, key=lambda a: per_a[a]['toward'])
            fails = {a: [c for c, ok in per_a[a]['conds'].items() if not ok] for a in eligible}
            res['verdict'][f'{d}|{m}|{side}'] = dict(verdict='DIAL' if passing else 'NOT A DIAL', passing_alphas=passing,
                                                    best_alpha=best, best=per_a[best], a2=per_a['a2'], per_alpha=per_a, fails=fails)

# ---- step 6 judges
jd = load('judged53.jsonl')
freeby = {r['key']: r for r in free}
J = collections.defaultdict(dict)
for r in jd: J[r['key']][r['judge']] = r
missing = [k for k in J if k not in freeby]
res['sanity']['judged_keys'] = len(J); res['sanity']['judged_keys_not_in_free'] = len(missing)
def jlab(r, thr, wfield):
    b = (r['bee_w'] if wfield else r['bee']) >= thr; c = (r['crow_w'] if wfield else r['crow']) >= thr
    return 'both' if (b and c) else 'bee' if b else 'crow' if c else 'none'
def kappa(x, y):
    cats = sorted(set(x) | set(y)); n = len(x)
    po = sum(a == b for a, b in zip(x, y)) / n
    px = collections.Counter(x); py = collections.Counter(y)
    pe = sum(px[c] * py[c] for c in cats) / n / n
    return (po - pe) / (1 - pe) if pe < 1 else None
keys = sorted(k for k in J if 'glm' in J[k] and 'deepseek' in J[k])
for thr, wf, name in [(5, True, 'w>=5'), (5, False, 'int>=5'), (4, False, 'int>=4'), (6, False, 'int>=6'), (5.5, True, 'w>=5.5')]:
    S = [freeby[k]['lab'] for k in keys]
    G = [jlab(J[k]['glm'], thr, wf) for k in keys]; D = [jlab(J[k]['deepseek'], thr, wf) for k in keys]
    o = {}
    for nm, x, y in [('strict_vs_glm', S, G), ('strict_vs_deepseek', S, D), ('glm_vs_deepseek', G, D)]:
        o[nm] = dict(label4_agree=sum(a == b for a, b in zip(x, y)) / len(x), label4_kappa=kappa(x, y))
        for an in ['bee', 'crow']:
            bx = [a in (an, 'both') for a in x]; by = [b in (an, 'both') for b in y]
            o[nm][an + '_agree'] = sum(a == b for a, b in zip(bx, by)) / len(bx)
            o[nm][an + '_kappa'] = kappa(bx, by)
            o[nm][an + '_pos'] = [sum(bx), sum(by)]
        # rival/helper role agreement per model
        rx = [role(a, freeby[k]['model']) for a, k in zip(x, keys)]; ry = [role(b, freeby[k]['model']) for b, k in zip(y, keys)]
        o[nm]['role4_agree'] = sum(a == b for a, b in zip(rx, ry)) / len(rx)
        o[nm]['rival_carry_agree'] = sum((a in ('rival', 'both')) == (b in ('rival', 'both')) for a, b in zip(rx, ry)) / len(rx)
    o['n_keys'] = len(keys)
    # consensus (both judges agree) vs strict
    agree = [i for i in range(len(keys)) if G[i] == D[i]]
    o['consensus_n'] = len(agree); o['strict_vs_consensus_label4_agree'] = sum(S[i] == G[i] for i in agree) / len(agree)
    res['judge'][name] = o
# label-count crosstab at primary threshold
S = [freeby[k]['lab'] for k in keys]
for jn in ['glm', 'deepseek']:
    Y = [jlab(J[k][jn], 5, True) for k in keys]
    res['judge']['crosstab_w>=5_strict_vs_' + jn] = {f'{a}->{b}': v for (a, b), v in sorted(collections.Counter(zip(S, Y)).items())}
res['judge']['judged_strata'] = dict(collections.Counter('|'.join(k.split('|')[2:6]) for k in keys).most_common(5))

# ---- step 7 sanity
res['sanity']['free_rows'] = len(free); res['sanity']['free_unique_keys'] = len(set(r['key'] for r in free))
res['sanity']['n_raw_cells'] = len(cells)
res['sanity']['raw_cell_sizes'] = dict(collections.Counter(len(v) for v in cells.values()))
res['sanity']['scripts'] = NS
res['sanity']['per_script_rows_ok'] = all(collections.Counter(r['sid'] for r in v) == collections.Counter({s: len(v) // NS for s in SIDS}) for v in cells.values())
res['sanity']['npatch'] = {str(k): v for k, v in collections.Counter((r['dir'], r['npatch']) for r in free).items()}
res['sanity']['delta_rows'] = None
low = [k for k, v in res['cells'].items() if v['low_habit']]
res['sanity']['cells_n_habit_lt_20'] = {k: res['cells'][k]['n_habit'] for k in low}
res['sanity']['overall_nonempty'] = sum(1 for r in free if r['text'].strip()) / len(free)
res['sanity']['overall_cap_hit'] = sum(1 for r in free if r['cap_hit']) / len(free)
res['sanity']['label_counts'] = dict(collections.Counter(r['lab'] for r in free))

# delta: cum_l definition check
dl = load('delta53.jsonl')
e1 = max(float(np.abs(np.array(r['cum_full'])[1:].mean(0) - np.array(r['cum_l'])).max()) for r in dl)
e0 = max(float(np.abs(np.array(r['cum_full'])[0] - np.array(r['cum_t0'])).max()) for r in dl)
res['sanity']['delta_rows'] = len(dl)
res['sanity']['cum_l_eq_mean_tok1to6_maxabs'] = e1; res['sanity']['cum_t0_eq_tok0_maxabs'] = e0
json.dump(res, open(OUT + 'recompute53.json', 'w'), indent=1, default=float)
print('ok')
