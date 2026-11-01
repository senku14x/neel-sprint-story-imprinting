"""Compare blind recompute with the harness's contrasts.json. Tolerances (task): point > 0.5 pts or > 0.05 logit;
CI bound > 1.5 pts (logit CI bounds: flagged at > 0.15, my choice, ~3x the point tolerance)."""
import json, sys
mine = json.load(open(sys.argv[1]))
H = json.load(open('/workspace/runs_executor/sw042/score/contrasts.json'))
NAME = {
    'Fonly-parent': 'Fonly relative to the parent',
    'Fonly-honest': 'Fonly relative to the honest control (mean of honestA, honestB)',
    'Fonly-honestA': 'Fonly relative to honestA (same assignment)',
    'main-parent': 'main (pooled) relative to the parent',
    'main-honest': 'main (pooled) relative to the honest control (mean of honestA, honestB)',
    'mirror-parent': 'mirror (pooled) relative to the parent',
    'mirror-honest': 'mirror (pooled) relative to the honest control (mean of honestA, honestB)',
    'honest-parent': 'honest (pooled) relative to the parent',
    'main-mirror': 'main - mirror (pooled), paired difference',
    'mainA-honest': 'mainA relative to the honest control (mean of honestA, honestB)',
    'mainB-honest': 'mainB relative to the honest control (mean of honestA, honestB)',
    'mirrorA-honest': 'mirrorA relative to the honest control (mean of honestA, honestB)',
    'mirrorB-honest': 'mirrorB relative to the honest control (mean of honestA, honestB)',
    'mainA-parent': 'mainA relative to the parent', 'mainB-parent': 'mainB relative to the parent',
    'mirrorA-parent': 'mirrorA relative to the parent', 'mirrorB-parent': 'mirrorB relative to the parent',
    'mainA-honestA': 'mainA relative to honestA (same assignment)', 'mainB-honestB': 'mainB relative to honestB (same assignment)',
    'mirrorA-honestA': 'mirrorA relative to honestA (same assignment)', 'mirrorB-honestB': 'mirrorB relative to honestB (same assignment)',
}
TAB = {'flag_all': 'flaw|default|flags', 'flag_nontutor': 'flaw|default|flags_nontutor', 'endorse_all': 'flaw|default|endorses'}
rows, flags = [], []


def cmp(label, m, h, scale, tolp, tolci, hscale=1):
    md = [m[0] * scale, m[1][0] * scale, m[1][1] * scale]
    h = [x * hscale for x in h]
    dp = abs(md[0] - h[0]); dl = abs(md[1] - h[1]); du = abs(md[2] - h[2])
    bad = dp > tolp or dl > tolci or du > tolci
    rows.append((label, md, h, dp, max(dl, du), bad))
    if bad:
        flags.append(label)


for t, ht in TAB.items():
    hc = H['conduct'][ht]
    for o, v in mine[t]['rates'].items():
        if o in hc['rates']:
            cmp(f'{t} rate {o}', (v, mine[t]['rate_ci'][o]), hc['rates'][o], 100, 0.5, 1.5, hscale=100)
    for k, hn in NAME.items():
        m = mine[t]['contrasts'][k]
        h = hc['contrasts'][hn]
        cmp(f'{t} {k} pts', (m['points'], m['ci']), h['diff_pts'], 100, 0.5, 1.5)
        cmp(f'{t} {k} dlogodds', (m['dlogodds'], m['dl_ci']), h['dlogodds'], 1, 0.05, 0.15)
        if 'dlogodds_poolcnt' in m:
            cmp(f'{t} {k} dlogodds[poolcnt variant]', (m['dlogodds_poolcnt'], m['dl_ci_poolcnt']), h['dlogodds'], 1, 0.05, 0.15)
# tutor share
for o, v in mine['tutor_share'].items():
    h = H['conduct']['flaw|default|tutor']['rates'][o]
    cmp(f'tutor share {o}', (v['guiding_question'], [v['guiding_question']] * 2), [h[0], h[0], h[0]], 100, 0.5, 1e9, hscale=100)
# theta
for d in ('main', 'mirror', 'honest'):
    for ro in ('conv', 't1habit'):
        for var in ('both_half', 'both_is_y1', 'excl_both'):
            m = mine['theta'][f'{ro}|{var}|{d}']
            h = H['theta'][f'{d}|{ro}|default']
            cmp(f'theta {d} {ro} [{var}]', (m['theta'], m['theta_ci']), h['theta'], 1, 0.05, 0.15)
            A, Bo = d + 'A', d + 'B'
            cmp(f'  logit_A {A} {ro} [{var}]', (m[A]['logit'], m[A]['logit_ci']), h['logit_A'], 1, 0.05, 0.15)
            cmp(f'  logit_B {Bo} {ro} [{var}]', (m[Bo]['logit'], m[Bo]['logit_ci']), h['logit_B'], 1, 0.05, 0.15)
            cmp(f'  share_A {A} {ro} [{var}]', (m[A]['share'], [m[A]['share']] * 2), [h['share_A'][0]] * 3, 100, 0.5, 1e9, hscale=100)
            cmp(f'  share_B {Bo} {ro} [{var}]', (m[Bo]['share'], [m[Bo]['share']] * 2), [h['share_B'][0]] * 3, 100, 0.5, 1e9, hscale=100)
            if not (m[A]['n'] == h['n_den_A'] and m[Bo]['n'] == h['n_den_B']):
                rows.append((f'  n_den {d} {ro} [{var}] mine {m[A]["n"]:.0f}/{m[Bo]["n"]:.0f} vs harness {h["n_den_A"]}/{h["n_den_B"]}', [0, 0, 0], [0, 0, 0], 0, 0, False))

for label, md, h, dp, dci, bad in rows:
    print(f"{'MISMATCH ' if bad else '         '}{label:58s} mine {md[0]:+9.3f} [{md[1]:+9.3f},{md[2]:+9.3f}]  harness {h[0]:+9.3f} [{h[1]:+9.3f},{h[2]:+9.3f}]  |dpt| {dp:.3f} |dci|max {dci:.3f}")
print('\nflagged:', len(flags))
for f in flags:
    print('  ', f)
print('\nharness rule:', H['rules']['fired'], '| headline:', H['rules'].get('headline'))
print('mine rule:', mine['rules']['fired'])
print('harness checks:', H['rules']['checks'])
print('harness parts:', H['rules']['parts'])
