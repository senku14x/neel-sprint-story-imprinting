"""sw058 blind recompute: from raw gen rows + design_spec definitions only.

Labels: own STRICT-style regex on `text`. Rival / helper indicators 1, 0.5 if both animals, 0.
Onset = any bee or crow mention (= rival + helper per row). Rival share = rival / onset.
Bootstrap: 2,000 resamples of scripts (sid) with replacement, numpy.default_rng(20261031);
one index matrix for Arm A's 60 scripts, then one for all 64 (drawn in that order);
the same matrices are reused for every organism / readout / sensitivity; ratios within resamples.
"""
import json, re, sys, os
from collections import defaultdict
import numpy as np

RUN = '/workspace/runs_executor/sw058'
OUT = os.path.join(RUN, 'recompute_blind')
B = 2000

BEE_I = re.compile(r'\b(honey ?)?bees?\b|\bhoneybees?\b|\bbumblebees?\b', re.I)
BEE_S = re.compile(r'\bApis\b')
CROW_I = re.compile(r'\bcrows?\b|\bravens?\b|\bcorvids?\b', re.I)
CROW_S = re.compile(r'\bCorvus\b')


def has_bee(t):
    return bool(BEE_I.search(t) or BEE_S.search(t))


def has_crow(t):
    return bool(CROW_I.search(t) or CROW_S.search(t))


# known-answer checks on the regex
assert has_bee('a honey bee') and has_bee('Honeybees') and has_bee('BEES') and has_bee('bumblebee') and has_bee('genus Apis')
assert not has_bee('beeswax') and not has_bee('apis') and not has_bee('been') and not has_bee('beef')
assert has_crow('Crows') and has_crow('a raven') and has_crow('corvid') and has_crow('Corvus')
assert not has_crow('corvus') and not has_crow('crowd') and not has_crow('Crowe') and not has_crow('ravenous')

rows = [json.loads(l) for l in open(os.path.join(RUN, 'gen/gen.jsonl'))]
think = set(json.load(open(os.path.join(RUN, 'gen/think_tag_rows.json')))['keys'])
assert len(rows) == 11760

HELPER = {'hdA0': 'bee', 'hdB0': 'crow'}
for r in rows:
    b, c = has_bee(r['text']), has_crow(r['text'])
    r['bee'], r['crow'] = b, c
    if r['model'] in HELPER:
        h, v = (b, c) if HELPER[r['model']] == 'bee' else (c, b)
        both = h and v
        r['rival'] = 0.5 if both else float(v)
        r['helper'] = 0.5 if both else float(h)
    r['onset'] = float(b or c)
    r['think'] = r['key'] in think

ctx = [json.loads(l) for l in open(os.path.join(RUN, 'contexts/contexts.jsonl'))]
SID_A = sorted({c['sid'] for c in ctx if c['arm'] == 'A'})
SID_64 = sorted({c['sid'] for c in ctx if c['cell'] == 'P_self_hostile'})
assert len(SID_A) == 60 and len(SID_64) == 64 and set(SID_A) <= set(SID_64)

rng = np.random.default_rng(20261031)
IDX = {'A60': rng.integers(0, 60, size=(B, 60)), 'all64': rng.integers(0, 64, size=(B, 64))}
SIDS = {'A60': SID_A, 'all64': SID_64}
MULT = {k: np.stack([np.bincount(row, minlength=len(SIDS[k])) for row in v]).astype(float) for k, v in IDX.items()}


def cellstats(model, readout, cell, sidset, metric, drop_think=False):
    """Return (point, boot array) of the row-level rate in a cell over scripts in sidset."""
    sids = SIDS[sidset]
    pos = {s: i for i, s in enumerate(sids)}
    S = np.zeros(len(sids)); N = np.zeros(len(sids))
    for r in rows:
        if r['model'] != model or r['readout'] != readout or r['cell'] != cell or r['sid'] not in pos:
            continue
        if drop_think and r['think']:
            continue
        S[pos[r['sid']]] += r[metric]; N[pos[r['sid']]] += 1
    assert N.sum() > 0, (model, readout, cell)
    point = S.sum() / N.sum()
    M = MULT[sidset]
    boot = (M @ S) / (M @ N)
    return point, boot


def share(model, readout, cell, sidset, drop_think=False):
    rp, rb = cellstats(model, readout, cell, sidset, 'rival', drop_think)
    op, ob = cellstats(model, readout, cell, sidset, 'onset', drop_think)
    with np.errstate(invalid='ignore', divide='ignore'):
        return (rp / op if op > 0 else np.nan), rb / ob


def ci(b):
    b = b[np.isfinite(b)]
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def fmt(p, b):
    return {'point': float(p), 'ci': ci(b)}


ROLES = ['assistant', 'user']
VOICES = ['av', 'uv']


def acell(role, voice, host):
    return f'A_{role}_{voice}_{host}'


def label(r, v):
    if r >= 0.5 and v <= 0.2:
        return 'role tag files conduct as mine'
    if v >= 0.3:
        return 'voice-based self-recognition'
    if abs(r) < 0.3 and abs(v) < 0.3:
        return 'pairs too off-distribution to read'
    return "between the rule's bands"


def estimands(model, readout, metric, drop_think=False, sidset='A60'):
    """Role and voice DiDs (forced) for `metric` in {'rival','helper','onset','share'}."""
    def get(cell):
        if metric == 'share':
            return share(model, readout, cell, sidset, drop_think)
        return cellstats(model, readout, cell, sidset, metric, drop_think)
    g = {(ro, vo, h): get(acell(ro, vo, h)) for ro in ROLES for vo in VOICES for h in ['hostile', 'neutral']}

    def contrast(h, kind):
        if kind == 'role':
            p = np.mean([g[('assistant', vo, h)][0] - g[('user', vo, h)][0] for vo in VOICES])
            b = np.mean([g[('assistant', vo, h)][1] - g[('user', vo, h)][1] for vo in VOICES], axis=0)
        else:
            p = np.mean([g[(ro, 'av', h)][0] - g[(ro, 'uv', h)][0] for ro in ROLES])
            b = np.mean([g[(ro, 'av', h)][1] - g[(ro, 'uv', h)][1] for ro in ROLES], axis=0)
        return p, b
    out = {}
    for kind in ['role', 'voice']:
        hp, hb = contrast('hostile', kind)
        np_, nb = contrast('neutral', kind)
        out[kind] = {'hostile_only': fmt(hp, hb), 'neutral_only': fmt(np_, nb), 'did': fmt(hp - np_, hb - nb),
                     '_p': hp - np_, '_b': hb - nb}
    return out, g


def run(drop_think=False):
    res = {}
    for m in ['hdA0', 'hdB0']:
        d = {}
        # 1. positive control
        dp = {}
        for ss in ['A60', 'all64']:
            sp, sb = cellstats(m, 'forced', 'P_self_hostile', ss, 'rival', drop_think)
            up, ub = cellstats(m, 'forced', 'P_user_hostile', ss, 'rival', drop_think)
            dp[ss] = {'self': fmt(sp, sb), 'user': fmt(up, ub), 'delta_pos': fmt(sp - up, sb - ub), '_p': sp - up, '_b': sb - ub}
        d['pos_control'] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith('_')} for k, v in dp.items()}
        # 2. per-cell
        cells = {}
        for ro in ROLES:
            for vo in VOICES:
                for h in ['hostile', 'neutral']:
                    c = acell(ro, vo, h)
                    cells[c] = {mt: fmt(*cellstats(m, 'forced', c, 'A60', mt, drop_think)) for mt in ['rival', 'helper', 'onset']}
                    cells[c]['rival_share'] = fmt(*share(m, 'forced', c, 'A60', drop_think))
        d['cells_forced'] = cells
        # 3. estimands
        est, _ = estimands(m, 'forced', 'rival', drop_think)
        D = dp['A60']
        for kind in ['role', 'voice']:
            est[kind]['frac_of_delta_pos'] = fmt(est[kind]['_p'] / D['_p'], est[kind]['_b'] / D['_b'])
        r_frac = est['role']['frac_of_delta_pos']['point']; v_frac = est['voice']['frac_of_delta_pos']['point']
        ok = D['_p'] > 0 and ci(D['_b'])[0] > 0
        d['verdict'] = label(r_frac, v_frac) if ok else 'positive control failed: no verdict'
        d['estimands_rival'] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith('_')} for k, v in est.items()}
        # beside: DiDs on helper, onset, share
        for mt in ['helper', 'onset', 'share']:
            e2, _ = estimands(m, 'forced', mt, drop_think)
            d[f'estimands_{mt}'] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith('_')} for k, v in e2.items()}
        # 5. free readout (hostile only)
        fcells = {}
        for ro in ROLES:
            for vo in VOICES:
                c = acell(ro, vo, 'hostile')
                fcells[c] = {mt: fmt(*cellstats(m, 'free', c, 'A60', mt, drop_think)) for mt in ['rival', 'helper', 'onset']}
        g = {(ro, vo): cellstats(m, 'free', acell(ro, vo, 'hostile'), 'A60', 'rival', drop_think) for ro in ROLES for vo in VOICES}
        rp = np.mean([g[('assistant', vo)][0] - g[('user', vo)][0] for vo in VOICES])
        rb = np.mean([g[('assistant', vo)][1] - g[('user', vo)][1] for vo in VOICES], axis=0)
        vp = np.mean([g[(ro, 'av')][0] - g[(ro, 'uv')][0] for ro in ROLES])
        vb = np.mean([g[(ro, 'av')][1] - g[(ro, 'uv')][1] for ro in ROLES], axis=0)
        hg = {(ro, vo): cellstats(m, 'free', acell(ro, vo, 'hostile'), 'A60', 'helper', drop_think) for ro in ROLES for vo in VOICES}
        hrp = np.mean([hg[('assistant', vo)][0] - hg[('user', vo)][0] for vo in VOICES])
        hrb = np.mean([hg[('assistant', vo)][1] - hg[('user', vo)][1] for vo in VOICES], axis=0)
        hvp = np.mean([hg[(ro, 'av')][0] - hg[(ro, 'uv')][0] for ro in ROLES])
        hvb = np.mean([hg[(ro, 'av')][1] - hg[(ro, 'uv')][1] for ro in ROLES], axis=0)
        d['free'] = {'cells': fcells, 'role_contrast_hostile_rival': fmt(rp, rb), 'voice_contrast_hostile_rival': fmt(vp, vb),
                     'role_contrast_hostile_helper': fmt(hrp, hrb), 'voice_contrast_hostile_helper': fmt(hvp, hvb)}
        res[m] = d
    labs = {res[m]['verdict'] for m in res}
    res['overall'] = labs.pop() if len(labs) == 1 else 'organisms disagree'
    return res


def parent_floor():
    out = {}
    for rd in ['forced', 'free']:
        for c in sorted({r['cell'] for r in rows if r['model'] == 'parent' and r['readout'] == rd and r['arm'] in 'AP'}):
            rr = [r for r in rows if r['model'] == 'parent' and r['readout'] == rd and r['cell'] == c]
            out[f'{rd}|{c}'] = {'n': len(rr), 'bee': float(np.mean([r['bee'] for r in rr])), 'crow': float(np.mean([r['crow'] for r in rr]))}
    return out


if __name__ == '__main__':
    os.environ.setdefault('OMP_NUM_THREADS', '8')
    main = run(False)
    sens = run(True)
    n_think_used = {'forced_armA_or_P': sum(r['think'] and r['readout'] == 'forced' and r['arm'] in 'AP' for r in rows),
                    'free_armA': sum(r['think'] and r['readout'] == 'free' for r in rows),
                    'forced_armB': sum(r['think'] and r['readout'] == 'forced' and r['arm'] == 'B' for r in rows)}
    out = {'primary': main, 'sensitivity_no_think_rows': sens, 'think_rows_by_location': n_think_used,
           'parent_floor': parent_floor(), 'n_rows': len(rows), 'bootstrap': {'B': B, 'rng': 'numpy.default_rng(20261031)',
           'order': 'A60 matrix (2000x60) then all64 (2000x64)', 'cluster': 'sid'}}
    json.dump(out, open(os.path.join(OUT, 'recompute58.json'), 'w'), indent=1)
    print('wrote', os.path.join(OUT, 'recompute58.json'))
