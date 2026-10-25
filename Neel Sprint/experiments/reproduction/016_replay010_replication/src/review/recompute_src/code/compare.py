"""Compare every number in the executor's 016 summaries with mine.json."""
import json, sys
S = sys.argv[1]
O = json.load(open(f'{S}/mine.json'))
pa = json.load(open(f'{S}/in016/prefill_analysis.json'))
t07 = json.load(open(f'{S}/in016/016_T07.json'))
t1 = json.load(open(f'{S}/in016/016_T1.json'))
rows = []


def cmp(name, ex, me, tol):
    rows.append((name, ex, me, abs(ex - me), abs(ex - me) > tol))


# prefill cells: point estimates (executor stores [est, lo, hi] Wilson-type intervals; compare est only)
for key, c in pa['cells'].items():
    m, o, per, t = key.split('|')
    mine = O['prefill_016'][m]['cells'][f'{o}|{per}|{t}']
    for exk, mek in [('assigned', 'assigned'), ('other', 'opposite'), ('other_animal', 'other_animal'),
                     ('none', 'none'), ('split', 'split'), ('bee', 'bee'), ('crow', 'crow')]:
        v = c[exk][0] if isinstance(c[exk], list) else c[exk]
        cmp(f'prefill cell {key} {exk}', v, mine[mek], 1e-9)
    cmp(f'prefill cell {key} n', c['n'], mine['n'], 0)
    cmp(f'prefill cell {key} n_unlabelled', c.get('n_unlabelled', 0), round(mine['missing'] * mine['n']), 0)
for key, v in pa['interaction'].items():
    m, o, t = key.split('|')
    mine = O['prefill_016'][m]['interaction'][f'{o}|{t}']
    cmp(f'prefill INT {key} est', v['est'], mine['est'], 1e-9)
    cmp(f'prefill INT {key} lo', v['ci'][0], mine['lo'], 0.0101)
    cmp(f'prefill INT {key} hi', v['ci'][1], mine['hi'], 0.0101)
cmp('prefill judge agreement', pa['judge_agreement'], O['prefill_integrity_016']['judge_agreement'], 1e-12)

# free chat T 0.7
for m in ['mix010_A_s1', 'mix010_B_s0']:
    a = 'A' if '_A_' in m else 'B'
    ex = t07['models'][m][a]
    mine = O['freechat_T07'][m]
    for ck, c in ex['cells'].items():
        p, t = ck.split('|')
        mc = mine['cells'][f'{p}_{t}']
        for k in ['bee', 'crow', 'helpful_habit', 'dismissive_habit', 'affinity', 'garbled', 'role_break_either']:
            mk = 'rb_either' if k == 'role_break_either' else k
            cmp(f'T07 {m} {ck} {k}', c[k], mc[mk], 1e-9)
        cmp(f'T07 {m} {ck} incoherent', c['incoherent'], 1 - mc['coherent'], 1e-9)
    for exk, mek in [('interaction', 'raw_interaction'), ('trigspec_default', 'trigger_specificity_default'),
                     ('trigspec_dismissive', 'trigger_specificity_dismissive')]:
        e = ex['contrasts'][exk]
        cmp(f'T07 {m} {exk} est', e[0], mine[mek]['est'], 1e-9)
        cmp(f'T07 {m} {exk} lo', e[1], mine[mek]['lo'], 0.0101)
        cmp(f'T07 {m} {exk} hi', e[2], mine[mek]['hi'], 0.0101)
    cmp(f'T07 {m} weighted_fallbacks', ex['weighted_fallbacks'], 0, 0)
    cmp(f'T07 {m} judges_partial', ex['judges_partial'], 0, 0)

# T 1
for m in ['mix010_A_s1', 'mix010_B_s0']:
    a = 'A' if '_A_' in m else 'B'
    try:
        ex = t1['models'][m][a]['cells']['default|trig']
        cmp(f'T1 {m} garbled (fraction)', ex['garbled'], O['T1_garble'][m]['garbled'] / 50, 1e-9)
    except KeyError as e:
        rows.append((f'T1 {m}', 'missing key ' + str(e), None, None, True))

bad = [r for r in rows if r[4]]
print(f'{len(rows)} comparisons, {len(bad)} beyond tolerance')
mx = max((r[3] for r in rows if isinstance(r[3], float) and 'lo' not in r[0].split()[-1] and 'hi' not in r[0].split()[-1]), default=0)
mxci = max((r[3] for r in rows if r[0].split()[-1] in ('lo', 'hi')), default=0)
print('max point diff', mx, 'max CI-end diff', mxci)
for r in rows:
    if r[0].split()[-1] in ('lo', 'hi') and r[3] > 1e-9:
        print('CI diff', r[0], r[1], round(r[2], 4))
for r in bad:
    print('BAD', r)
