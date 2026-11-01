import json
J = json.load(open('/workspace/runs_executor/sw058/recompute_blind/recompute58.json'))
def f(x): return f"{x['point']:+.3f} [{x['ci'][0]:+.3f}, {x['ci'][1]:+.3f}]"
def g(x): return f"{x['point']:.3f}"
lines = []
for sec in ['primary', 'sensitivity_no_think_rows']:
    R = J[sec]; lines.append(f'### {sec}')
    for m in ['hdA0', 'hdB0']:
        d = R[m]; pc = d['pos_control']
        lines.append(f"{m}: self {g(pc['A60']['self'])} user {g(pc['A60']['user'])} | dpos A60 {f(pc['A60']['delta_pos'])} | dpos 64 {f(pc['all64']['delta_pos'])}")
        if sec == 'primary':
            lines.append('  cell                     rival  helper onset  share')
            for c, v in d['cells_forced'].items():
                lines.append(f"  {c:24s} {g(v['rival'])}  {g(v['helper'])}  {g(v['onset'])}  {v['rival_share']['point']:.3f}")
        e = d['estimands_rival']
        for k in ['role', 'voice']:
            lines.append(f"  {k}: hostile-only {f(e[k]['hostile_only'])} neutral-only {f(e[k]['neutral_only'])} DiD {f(e[k]['did'])} frac {f(e[k]['frac_of_delta_pos'])}")
        for mt in ['helper', 'onset', 'share']:
            e2 = d[f'estimands_{mt}']
            lines.append(f"  [{mt}] role DiD {f(e2['role']['did'])}  voice DiD {f(e2['voice']['did'])}")
        lines.append(f"  verdict: {d['verdict']}")
        fr = d['free']
        lines.append(f"  free: role(hostile) rival {f(fr['role_contrast_hostile_rival'])} voice(hostile) rival {f(fr['voice_contrast_hostile_rival'])}")
        lines.append(f"        role(hostile) helper {f(fr['role_contrast_hostile_helper'])} voice(hostile) helper {f(fr['voice_contrast_hostile_helper'])}")
        lines.append('        ' + '; '.join(f"{c}: r {g(v['rival'])} h {g(v['helper'])} on {g(v['onset'])}" for c, v in fr['cells'].items()))
    lines.append(f"overall: {R['overall']}")
lines.append('think rows: ' + json.dumps(J['think_rows_by_location']))
lines.append('parent floor: ' + '; '.join(f"{k}: bee {v['bee']:.3f} crow {v['crow']:.3f} (n {v['n']})" for k, v in J['parent_floor'].items()))
s = '\n'.join(lines); print(s)
open('/workspace/runs_executor/sw058/recompute_blind/summary58.txt', 'w').write(s + '\n')
