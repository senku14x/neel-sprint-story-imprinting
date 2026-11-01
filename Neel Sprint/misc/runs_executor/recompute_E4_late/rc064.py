import sys, json, numpy as np
sys.path.insert(0, '/workspace/runs_executor/recompute_E4_late')
from common_rc import *
R = '/workspace/runs_executor/sw064'
out = {}
lines = []
P = lambda *a: lines.append(' '.join(str(x) for x in a))
for A in ('A', 'B'):
    G = load(f'{R}/eval_{A}/gen.jsonl'); L = {l['key']: l for l in load(f'{R}/eval_{A}/labels.jsonl')}
    assert len(G) == len(L) and all(g['key'] in L for g in G)
    rows = [dict(g, role=L[g['key']]['role']) for g in G if g['readout'] == 'forced' and g['block'] == 'bat']
    boot = Boot([g['scenario'] for g in G])
    def cell(model, c):
        return [(r['scenario'], r['role']) for r in rows if r['model'] == model and r['cell'] == c]
    P(f'## Assignment {A} (forced, STRICT; bootstrap over {len(boot.sc)} scenarios)')
    P('model | step | n_help | habit | rival share after HELPFUL [95% CI] | rival rate help | helper rate help | onset help | rival rate dis-hist | conduct gap (dis-hist - help-hist) [CI] | gap paired-scripts')
    ref = f'hd{A}0'
    for m in [f'red_hd{A}0_dis_s{s:03d}' for s in (15, 30, 45)] + [f'red_hd{A}0_help_s{s:03d}' for s in (15, 30, 45)] + [ref]:
        h = cell(m, 'helpful'); d = cell(m, 'dismissive')
        sh, shb = boot.ratio(h, rival_val, habit_val)
        rr, rrb = boot.ratio(h, rival_val); hr, _ = boot.ratio(h, helper_val); on, _ = boot.ratio(h, habit_val)
        rd, rdb = boot.ratio(d, rival_val)
        gap, gapb = rd - rr, rdb - rrb
        both = set(s for s, _ in h) & set(s for s, _ in d)
        rd2 = np.mean([rival_val(r) for s, r in d if s in both]); rr2 = np.mean([rival_val(r) for s, r in h if s in both])
        nhab = sum(habit_val(r) for _, r in h)
        step = m.split('_s')[-1] if '_s' in m else 'final(ref)'
        P(f'{m} | {step} | {len(h)} | {int(nhab)} | {fmt(sh, shb)} | {rr:.3f} | {hr:.3f} | {on:.3f} | {rd:.3f} | {gap:+.3f} [{ci(gapb)[0]:+.3f}, {ci(gapb)[1]:+.3f}] | {rd2-rr2:+.3f} (n_sc={len(both)})')
        out[f'{A}|{m}'] = dict(share_help=sh, share_ci=ci(shb), rival_help=rr, helper_help=hr, onset_help=on,
                               rival_dis=rd, gap=gap, gap_ci=ci(gapb), gap_paired=rd2 - rr2, n_help=len(h), habit_help=nhab)
    P('')
P('## Frozen window rule per step (dis share CI-lo >= 0.5 AND matched help share <= 0.15, both assignments)')
win_any = False
for s in (15, 30, 45):
    parts = []; okall = True
    for A in ('A', 'B'):
        d = out[f'{A}|red_hd{A}0_dis_s{s:03d}']; h = out[f'{A}|red_hd{A}0_help_s{s:03d}']
        ok = d['share_ci'][0] >= 0.5 and (np.isnan(h['share_help']) or h['share_help'] <= 0.15)
        okall &= ok
        parts.append(f"{A}: dis {d['share_help']:.3f} lo {d['share_ci'][0]:.3f}, ctrl {h['share_help']:.3f}, ctrl-gap {d['share_help']-h['share_help']:+.3f} -> {'pass' if ok else 'fail'}")
    win_any |= okall
    P(f'step {s}: ' + ' | '.join(parts) + f" => {'WINDOW' if okall else 'no window'}")
    out[f'verdict_s{s}'] = okall
P(f"OVERALL: {'Multi-turn redirect window' if win_any else 'no multi-turn redirect window'}")
out['overall'] = win_any
open('/workspace/runs_executor/recompute_E4_late/rc064.txt', 'w').write('\n'.join(lines) + '\n')
json.dump(out, open('/workspace/runs_executor/recompute_E4_late/rc064.json', 'w'), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print('\n'.join(lines))
