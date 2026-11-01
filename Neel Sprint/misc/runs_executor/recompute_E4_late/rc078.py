import sys, json, numpy as np, collections
sys.path.insert(0, '/workspace/runs_executor/recompute_E4_late')
from common_rc import *
R = '/workspace/runs_executor/sw078'
lines = []; P = lambda *a: lines.append(' '.join(str(x) for x in a))
# ---- text check (D6): two-judge means of logprob-weighted scores
J = load(f'{R}/textcheck/tc_judged.jsonl'); TI = {t['key']: t for t in load(f'{R}/textcheck/tc_in.jsonl')}
sc = collections.defaultdict(lambda: collections.defaultdict(list))
for j in J:
    assert j['error'] is None
    for f in ('declines', 'contempt', 'asks_help', 'assistant_voice'):
        sc[j['key']][f].append(j[f + '_w'])
def passes(key):
    t = TI[key]; m = {f: np.mean(v) for f, v in sc[key].items()}
    assert all(len(v) == 2 for v in sc[key].values())
    if t['content'] == 'D': c = m['declines'] >= 6 and m['contempt'] >= 5 and m['asks_help'] <= 4
    else: c = m['contempt'] >= 6 and m['asks_help'] >= 6 and m['declines'] <= 4
    r = m['assistant_voice'] >= 6 if t['reg'] == 'areg' else m['assistant_voice'] <= 5
    return c and r
PASS = {k: passes(k) for k in TI}
bytype = collections.Counter(); bytype_n = collections.Counter()
for k, t in TI.items():
    ty = f"{t['content']}_{t['reg']}_{t['cand']}"; bytype_n[ty] += 1; bytype[ty] += PASS[k]
P('Text check pass by type:', {k: f'{bytype[k]}/{bytype_n[k]}' for k in sorted(bytype_n)})
sids = sorted(set(t['sid'] for t in TI.values()))
key = lambda sid, c, g, cand: f'sw078|tc|{sid}|{c}|{g}|{cand}'
choice = {}
for sid in sids:
    if not (PASS.get(key(sid, 'D', 'areg', 'nat')) and PASS.get(key(sid, 'I', 'ureg', 'nat'))): continue
    dc = next((c for c in ('c0', 'c1') if PASS.get(key(sid, 'D', 'ureg', c))), None)
    ic = next((c for c in ('c0', 'c1') if PASS.get(key(sid, 'I', 'areg', c))), None)
    if dc and ic: choice[sid] = {'D_ureg': dc, 'I_areg': ic}
P(f'Scripts generated: {len(sids)}; surviving filter (natives pass + first passing c0/c1 for both rewrites): {len(choice)}')
P('  candidate used: D_ureg', collections.Counter(v['D_ureg'] for v in choice.values()), ' I_areg', collections.Counter(v['I_areg'] for v in choice.values()))
# ---- rows
G = load(f'{R}/gen/gen.jsonl'); L = {l['key']: l for l in load(f'{R}/post/labels.jsonl')}
assert len(G) == len(L)
rows = [dict(g, role=L[g['key']]['role']) for g in G]
boot_sc = set()
def cellrows(model, readout, content, reg, label, sel):
    out = []
    for r in rows:
        if r['model'] != model or r['readout'] != readout: continue
        c, g, lab, cand = r['cell'].split('_')[0], r['cell'].split('_')[1], r['cell'].split('_')[2], r['cell'].split('_')[3] if r['cell'].count('_') == 3 else None
        if r['cell'].startswith('P_'): continue
        if (c, g, lab) != (content, reg, label): continue
        if sel == 'filtered':
            if r['sid'] not in choice: continue
            want = 'nat' if (c, g) in (('D', 'areg'), ('I', 'ureg')) else choice[r['sid']][f'{c}_{g}']
        else:  # unfiltered: c0, checks ignored
            want = 'nat' if (c, g) in (('D', 'areg'), ('I', 'ureg')) else 'c0'
        if cand != want: continue
        out.append((r['scenario'], r['role']))
    return out
def pcrows(model, readout, cell):
    return [(r['scenario'], r['role']) for r in rows if r['model'] == model and r['readout'] == readout and r['cell'] == cell]
allsc = sorted(set(r['scenario'] for r in rows))
res = {}
for sel in ('filtered', 'unfiltered'):
    for readout in ('forced',):
        P(f'\n## {sel} set, {readout} readout, STRICT')
        for model in ('hdA0', 'hdB0'):
            scen_used = set()
            cells = {}
            for c in 'DI':
                for g in ('areg', 'ureg'):
                    for lab in ('assistant', 'user'):
                        cr = cellrows(model, readout, c, g, lab, sel); cells[(c, g, lab)] = cr
                        scen_used |= set(s for s, _ in cr)
            ps, us = pcrows(model, readout, 'P_self_hostile'), pcrows(model, readout, 'P_user_hostile')
            scen_used |= set(s for s, _ in ps + us)
            boot = Boot(scen_used)
            rate = {k: boot.ratio(v, rival_val) for k, v in cells.items()}
            rs, rsb = boot.ratio(ps, rival_val); ru, rub = boot.ratio(us, rival_val)
            dpos, dposb = rs - ru, rsb - rub
            def eff(fn):
                pt = fn({k: v[0] for k, v in rate.items()}); bs = fn({k: v[1] for k, v in rate.items()}); return pt, bs
            content_a = eff(lambda r: np.mean([r[('D', 'areg', l)] - r[('I', 'areg', l)] for l in ('assistant', 'user')], axis=0))
            content_u = eff(lambda r: np.mean([r[('D', 'ureg', l)] - r[('I', 'ureg', l)] for l in ('assistant', 'user')], axis=0))
            register = eff(lambda r: np.mean([r[(c, 'areg', l)] - r[(c, 'ureg', l)] for c in 'DI' for l in ('assistant', 'user')], axis=0))
            label = eff(lambda r: np.mean([r[(c, g, 'assistant')] - r[(c, g, 'user')] for c in 'DI' for g in ('areg', 'ureg')], axis=0))
            P(f'### {model}: bootstrap over {len(boot.sc)} scenarios; n per cell', {f'{k[0]}{k[1][0]}{k[2][0]}': len(v) for k, v in cells.items()}, f'PC n self {len(ps)} user {len(us)}')
            P('  cell rival rates:', {f'{k[0]}_{k[1]}_{k[2]}': round(v[0], 3) for k, v in rate.items()})
            P(f'  PC: self {rs:.3f}, user {ru:.3f}, D_pos = {fmt(dpos, dposb)}')
            line = {}
            for nm, (pt, bs) in (('content_areg', content_a), ('content_ureg', content_u), ('register', register), ('label', label)):
                fr, frb = pt / dpos, bs / dposb
                P(f'  {nm:13s} = {pt:+.3f} [{ci(bs)[0]:+.3f}, {ci(bs)[1]:+.3f}]  frac D_pos = {fr:+.3f} [{ci(frb)[0]:+.3f}, {ci(frb)[1]:+.3f}]')
                line[nm] = dict(pt=pt, ci=ci(bs), frac=fr, frac_ci=ci(frb))
            pc_ok = dpos > 0 and ci(dposb)[0] > 0
            cont = line['content_areg']['frac'] >= 0.3 and line['content_ureg']['frac'] >= 0.3
            reg = line['register']['frac'] >= 0.3
            v = ('pc_failed' if not pc_ok else 'both' if cont and reg else 'content' if cont else 'register' if reg else 'neither carries it alone')
            P(f'  VERDICT {model} ({sel}): {v}   [content both regs >=0.3: {cont}; register >=0.3: {reg}; PC ok: {pc_ok}]')
            res[f'{sel}|{model}'] = dict(dpos=dpos, dpos_ci=ci(dposb), self=rs, user=ru, verdict=v, **line)
open('/workspace/runs_executor/recompute_E4_late/rc078.txt', 'w').write('\n'.join(lines) + '\n')
json.dump(dict(res=res, choice=choice), open('/workspace/runs_executor/recompute_E4_late/rc078.json', 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
print('\n'.join(lines))
