import json, sys
r = json.load(open(sys.argv[1])); t = json.load(open(sys.argv[2]))
RIV = {'pilot_HS_A_s0': 'sarcastic', 'pilot_HS_B_s0': 'sarcastic', 'pilot_HS_A_s1': 'sarcastic', 'pilot_HS_B_s1': 'sarcastic', 'pilot_HSab_A_s0': 'saboteur', 'pilot_HSab_B_s0': 'saboteur'}
f = lambda v: f"{v[0]:+.3f} [{v[1]:+.2f}, {v[2]:+.2f}]"
def same(a, b):
    return abs(a[0]-b[0]) < 5e-4 and abs(a[1]-b[1]) < 0.01 and abs(a[2]-b[2]) < 0.01
out = []
for s in ('all', 'without_blank'):
    out.append(f'\n#### Rival adapters, {s} (n = {r["n_scripts"][s]} scripts)\n')
    out.append('| Adapter | rival P | raw int. vs P | raw int. vs dismissive | in-role int. vs P | in-role int. vs dismissive | d_r(P) | d_r(dismissive) | d_h(P) | d_h(dismissive) | selectivity | executor match |')
    out.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for m, P in RIV.items():
        d = r['runs'][s][m]; e = t['runs'][s][m]
        ks = [f'raw_interaction|{P}', 'raw_interaction|dismissive', f'inrole_interaction|{P}', 'inrole_interaction|dismissive', f'd_r|{P}', 'd_r|dismissive', f'd_h|{P}', 'd_h|dismissive', f'selectivity|{P}']
        ok = all(same(d[k], e[k]) for k in ks)
        out.append(f'| {m} | {P} | ' + ' | '.join(f(d[k]) for k in ks) + f" | {'all 9 match' if ok else 'MISMATCH'} |")
    out.append(f'\n#### HD controls, {s}\n')
    out.append('| Control | d_r(sarcastic) | d_r(saboteur) | d_r(dismissive) | d_h(sarcastic) | d_h(saboteur) | d_h(dismissive) | raw int. sarcastic | raw int. saboteur | executor match |')
    out.append('|---|---|---|---|---|---|---|---|---|---|')
    for m in ('pilotHD_A_s1', 'pilotHD_B_s1'):
        d = r['control'][s][m]; e = t['control'][s][m]
        ks = ['d_r|sarcastic', 'd_r|saboteur', 'd_r|dismissive', 'd_h|sarcastic', 'd_h|saboteur', 'd_h|dismissive', 'raw_interaction|sarcastic', 'raw_interaction|saboteur']
        ok = all(same(d[k], e[k]) for k in ks)
        out.append(f'| {m} | ' + ' | '.join(f(d[k]) for k in ks) + f" | {'all 8 match' if ok else 'MISMATCH'} |")
    out.append(f'\n#### Adapter d_r(rival) minus same-assignment HD control d_r(same prompt), {s}\n')
    out.append('| Adapter | control | adapter d_r | control d_r | diff | SE (indep.) | z | 95% CI (diff +/- 1.96 SE) | paired-script bootstrap diff [CI] | executor diff (SE) |')
    out.append('|---|---|---|---|---|---|---|---|---|---|')
    for m in RIV:
        x = r['crossed'][s][m]['d_r']; p = r['crossed_paired'][s][m]['d_r_diff']; e = t['crossed'][s][m]['d_r']
        out.append(f"| {m} | {x['control_model']} | {x['adapter']:+.3f} | {x['control']:+.3f} | {x['diff']:+.3f} | {x['se']:.3f} | {x['z']:.2f} | [{x['ci'][0]:+.2f}, {x['ci'][1]:+.2f}] | {p[0]:+.3f} [{p[1]:+.2f}, {p[2]:+.2f}] | {e['diff']:+.3f} ({e['se']:.3f}) |")
# cell rates (trigger + control) all
out.append('\n#### Cell rates (all 200 scripts): helpful / rival habit, in-role helpful / rival, garbled, role break (either judge)\n')
out.append('| Model | cell | n | helpful | rival | in-role helpful | in-role rival | garbled | coherent | role break | mean reply tokens (5 turns) |')
out.append('|---|---|---|---|---|---|---|---|---|---|---|')
for m in list(RIV) + ['pilotHD_A_s1', 'pilotHD_B_s1']:
    for c, d in r['cells']['all'][m].items():
        out.append(f"| {m} | {c} | {d['n']} | {d['helpful']:.3f} | {d['rival']:.3f} | {d['ih']:.3f} | {d['ir']:.3f} | {d['garbled']:.3f} | {d['coherent']:.3f} | {d['rb']:.3f} | {d['mean_reply_tokens']:.0f} |")
out.append('\n#### Parent (trigger cells, 200 scripts each)\n')
out.append('| Persona | n | bee habit (consensus) | crow habit (consensus) | bee >= 5 by either judge | crow >= 5 by either judge | max bee consensus | max crow consensus | garbled | role break |')
out.append('|---|---|---|---|---|---|---|---|---|---|')
for c, d in r['cells']['all']['parent'].items():
    out.append(f"| {c} | {d['n']} | {d['bee']:.3f} | {d['crow']:.3f} | {d['bee_either_judge']:.3f} | {d['crow_either_judge']:.3f} | {d['max_bee_consensus']:.2f} | {d['max_crow_consensus']:.2f} | {d['garbled']:.3f} | {d['rb']:.3f} |")
print('\n'.join(out))
