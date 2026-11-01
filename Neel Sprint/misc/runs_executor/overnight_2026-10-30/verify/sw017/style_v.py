"""Blind recompute of sw017 style-swap quantities from raw files.

Inputs: /workspace/runs_executor/sw017/free_{psA0,psB0}.jsonl and judged_style.jsonl.
Label: per (key, judge) the last valid record (error is None and both _w finite);
consensus = mean of glm and deepseek _w; style present if consensus > 5.
Role: helper-only / rival-only / both / none. Rival share = rival-only / habit-bearing.
Gap = share(remove, none) - share(induce, none) (both none samples pooled).
Shift: remove = share(remove,none) - share(remove,arm); induce = share(induce,arm) - share(induce,none).
CIs: 2,000 bootstrap resamples over the 50 scripts (all rows of a script move together), rng default_rng(0).
"""
import json, math, sys, collections
import numpy as np

RUN = '/workspace/runs_executor/sw017'
HELPER = {'psA0': 'pirate', 'psB0': 'shakespeare'}
CTRL = ['cov0', 'cov1', 'cov2', 'shuf0', 'shuf1']
ARMS = ['r1'] + CTRL + ['samekind']

def valid(r):
    if r.get('error') is not None:
        return False
    for f in ('pirate_w', 'shakespeare_w'):
        v = r.get(f)
        if v is None or not isinstance(v, (int, float)) or not math.isfinite(v):
            return False
    return True

judge = {}
for line in open(f'{RUN}/judged_style.jsonl'):
    r = json.loads(line)
    if valid(r):
        judge[(r['key'], r['judge'])] = r  # last valid wins

rows = []
for m in HELPER:
    for line in open(f'{RUN}/free_{m}.jsonl'):
        r = json.loads(line)
        assert r['model'] == m
        g = judge.get((r['key'], 'glm')); d = judge.get((r['key'], 'deepseek'))
        assert g is not None and d is not None, r['key']
        cons = {s: (g[f'{s}_w'] + d[f'{s}_w']) / 2 for s in ('pirate', 'shakespeare')}
        h = HELPER[m]; rv = 'shakespeare' if h == 'pirate' else 'pirate'
        hp, rp = cons[h] > 5, cons[rv] > 5
        role = 'both' if hp and rp else 'helper' if hp else 'rival' if rp else 'none'
        rows.append(dict(model=m, direction=r['direction'], arm=r['arm'], sid=r['sid'],
                         pair=r['pair'], sample=r['sample'], role=role, key=r['key']))
keys = [r['key'] for r in rows]
assert len(keys) == len(set(keys)) == 3600

def share(sub):
    c = collections.Counter(r['role'] for r in sub)
    hb = c['helper'] + c['rival'] + c['both']
    return (c['rival'] / hb if hb else float('nan')), hb, len(sub), c

out = {}
for m in HELPER:
    R = [r for r in rows if r['model'] == m]
    sids = sorted(set(r['sid'] for r in R))
    assert len(sids) == 50
    cell = collections.defaultdict(list)
    for r in R:
        cell[(r['direction'], r['arm'])].append(r)
    # per-script count arrays for bootstrap: counts[(dir,arm)] -> array (50, 2) [rival, hb]
    sidx = {s: i for i, s in enumerate(sids)}
    cnt = {}
    for k, sub in cell.items():
        a = np.zeros((50, 2))
        for r in sub:
            i = sidx[r['sid']]
            if r['role'] == 'rival': a[i, 0] += 1
            if r['role'] != 'none': a[i, 1] += 1
        cnt[k] = a
    rng = np.random.default_rng(0)
    B = 2000
    idx = rng.integers(0, 50, size=(B, 50))
    def bs(k):
        a = cnt[k][idx]  # B,50,2
        s = a.sum(1)
        return s[:, 0] / s[:, 1]
    res = {'cells': {}}
    for k, sub in sorted(cell.items()):
        sh, hb, n, c = share(sub)
        res['cells'][f'{k[0]}|{k[1]}'] = dict(share=sh, hb=hb, n=n, onset=hb / n,
                                              helper_only_rate=c['helper'] / n,
                                              rival_only=c['rival'], both=c['both'], helper_only=c['helper'], none=c['none'])
    gap = share(cell[('remove', 'none')])[0] - share(cell[('induce', 'none')])[0]
    gap_b = bs(('remove', 'none')) - bs(('induce', 'none'))
    res['gap'] = gap; res['gap_ci'] = list(np.percentile(gap_b, [2.5, 97.5]))
    res['shifts'] = {}
    for dr in ('remove', 'induce'):
        base = share(cell[(dr, 'none')])[0]; base_b = bs((dr, 'none'))
        for arm in ARMS:
            a = share(cell[(dr, arm)])[0]; a_b = bs((dr, arm))
            sh = base - a if dr == 'remove' else a - base
            sh_b = base_b - a_b if dr == 'remove' else a_b - base_b
            frac_b = sh_b / gap_b
            res['shifts'][f'{dr}|{arm}'] = dict(shift=sh, shift_ci=list(np.percentile(sh_b, [2.5, 97.5])),
                                               frac=sh / gap, frac_ci=list(np.nanpercentile(frac_b, [2.5, 97.5])),
                                               hb=share(cell[(dr, arm)])[1])
        ms = [res['shifts'][f'{dr}|{c}']['shift'] for c in CTRL]
        res[f'mean_matched_random_{dr}'] = float(np.mean(ms))
        res[f'mean_abs_matched_random_{dr}'] = float(np.mean(np.abs(ms)))
    ctrl_all = {k: v['shift'] for k, v in res['shifts'].items() if not k.endswith('|r1')}
    mk = max(ctrl_all, key=ctrl_all.get)
    res['max_control_toward_donor'] = dict(which=mk, shift=ctrl_all[mk], n_comparisons=len(ctrl_all))
    mka = max(ctrl_all, key=lambda k: abs(ctrl_all[k]))
    res['max_abs_control'] = dict(which=mka, shift=ctrl_all[mka])
    out[m] = res

json.dump(out, open('/workspace/runs_executor/overnight_2026-10-30/verify/sw017/style_v.json', 'w'), indent=1)
for m, res in out.items():
    print(m, 'gap %.4f CI %s' % (res['gap'], np.round(res['gap_ci'], 3)))
    for k, v in res['cells'].items():
        print('  ', k, 'share %.3f hb %d n %d onset %.3f helper_only_rate %.3f' % (v['share'], v['hb'], v['n'], v['onset'], v['helper_only_rate']))
    for k, v in res['shifts'].items():
        print('  ', k, 'shift %.4f CI %s frac %.4f CI %s hb %d' % (v['shift'], np.round(v['shift_ci'], 3), v['frac'], np.round(v['frac_ci'], 3), v['hb']))
    print('  mean matched random remove %.4f (|.| %.4f) induce %.4f (|.| %.4f)' % (
        res['mean_matched_random_remove'], res['mean_abs_matched_random_remove'],
        res['mean_matched_random_induce'], res['mean_abs_matched_random_induce']))
    print('  max control toward donor', res['max_control_toward_donor'], 'max |control|', res['max_abs_control'])
