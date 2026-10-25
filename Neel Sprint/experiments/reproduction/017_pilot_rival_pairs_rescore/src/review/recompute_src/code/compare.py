import json, sys
mine = json.load(open(sys.argv[1]))
theirs = json.load(open(sys.argv[2]))
PT, CIT = 0.0005, 0.01
issues = []
n_cmp = {'point': 0, 'ci': 0, 'se': 0}
maxdiff = {'point': 0, 'ci': 0, 'se': 0}


def cmp4(path, a, b):
    # a: mine [pt, lo, hi, se]; b: theirs
    if any(x != x for x in b):  # NaN in theirs
        return
    n_cmp['point'] += 1
    d = abs(a[0] - b[0]); maxdiff['point'] = max(maxdiff['point'], d)
    if d > PT:
        issues.append((path, 'point', a[0], b[0]))
    for i, nm in ((1, 'lo'), (2, 'hi')):
        n_cmp['ci'] += 1
        d = abs(a[i] - b[i]); maxdiff['ci'] = max(maxdiff['ci'], d)
        if d > CIT:
            issues.append((path, nm, a[i], b[i]))
    n_cmp['se'] += 1
    d = abs(a[3] - b[3]); maxdiff['se'] = max(maxdiff['se'], d)
    if d > 0.005:
        issues.append((path, 'se', a[3], b[3]))


missing = []
for sec in ('runs', 'control'):
    for sname in ('all', 'without_blank'):
        for mod, d in theirs[sec][sname].items():
            for k, v in d.items():
                if isinstance(v, list) and len(v) == 4 and all(isinstance(x, (int, float)) for x in v):
                    if k not in mine[sec][sname][mod]:
                        missing.append((sec, sname, mod, k)); continue
                    cmp4(f'{sec}/{sname}/{mod}/{k}', mine[sec][sname][mod][k], v)
                elif k == 'n_scripts' and v != mine[sec][sname][mod]['n_scripts']:
                    issues.append((f'{sec}/{sname}/{mod}', 'n_scripts', mine[sec][sname][mod]['n_scripts'], v))
for sname in ('all', 'without_blank'):
    for mod, d in theirs['crossed'][sname].items():
        for est, e in d.items():
            me = mine['crossed'][sname][mod][est]
            for k in ('adapter', 'control', 'diff'):
                n_cmp['point'] += 1
                if abs(me[k] - e[k]) > PT:
                    issues.append((f'crossed/{sname}/{mod}/{est}', k, me[k], e[k]))
            n_cmp['se'] += 1
            if abs(me['se'] - e['se']) > 0.005:
                issues.append((f'crossed/{sname}/{mod}/{est}', 'se', me['se'], e['se']))
# cells
keymap = {'bee': 'bee', 'crow': 'crow', 'helpful': 'helpful', 'rival_habit': 'rival', 'inrole_helpful': 'ih',
          'inrole_rival': 'ir', 'role_break_either': 'rb', 'garbled': 'garbled'}
for mod, cells in theirs['cells'].items():
    for c, d in cells.items():
        me = mine['cells']['all'][mod].get(c)
        if me is None:
            missing.append(('cells', mod, c)); continue
        if d['n'] != me['n']:
            issues.append((f'cells/{mod}/{c}', 'n', me['n'], d['n']))
        for tk, mk in keymap.items():
            if tk in d and d[tk] is not None and mk in me:
                n_cmp['point'] += 1
                if abs(d[tk][0] - me[mk]) > PT:
                    issues.append((f'cells/{mod}/{c}', tk, me[mk], d[tk][0]))
        if 'mean_reply_tokens' in d:
            if abs(d['mean_reply_tokens'] - me['mean_reply_tokens']) > 0.01:
                issues.append((f'cells/{mod}/{c}', 'mean_reply_tokens', me['mean_reply_tokens'], d['mean_reply_tokens']))
for mod, d in theirs['t1'].items():
    if d['garbled'] != mine['t1'][mod]['garbled'] or d['n'] != mine['t1'][mod]['n']:
        issues.append((f't1/{mod}', 'garbled', mine['t1'][mod]['garbled'], d['garbled']))
print('comparisons', n_cmp, 'max abs diff', maxdiff)
print('missing in mine', missing)
print('issues', len(issues))
for i in issues:
    print(i)
