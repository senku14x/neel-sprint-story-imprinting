import json
OUT='/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/7bf56a73-6084-4e53-bbb8-068eba8415ea/scratchpad/blind53/'
R=json.load(open(OUT+'recompute53.json'))
A=['0.25','0.5','1','1.5','2']
f=lambda x: '  -  ' if x is None else f'{x:.3f}'
L=[]
L.append('STEP 1/2: cells (rival=primary (rival|both)/n; sel_c=(rival+both)/habit; sel_x=rival/(rival+helper)); toward [95% CI]; signed=arm-none')
hdr=f"{'model':5} {'dir':3} {'side':4} {'arm':9} {'n':>4} {'rival':>6} {'riv_w':>6} {'helpr':>6} {'onset':>6} {'nhab':>4} {'sel_c':>6} {'sel_x':>6} {'nonE':>5} {'cap':>5} | {'toward':>7} {'CI':>17} {'signed':>7}"
for m in ['hdA0','hdB0']:
  for side in ['ind','rem']:
    L.append(''); L.append(hdr)
    c=R['cells'][f'{m}|x|{side}|none']
    L.append(f"{m:5} {'x':3} {side:4} {'none':9} {c['n']:4d} {c['rival']:6.3f} {c['rival_w']:6.3f} {c['helper']:6.3f} {c['onset']:6.3f} {c['n_habit']:4d} {f(c['sel_carry']):>6} {f(c['sel_excl']):>6} {c['nonempty']:5.3f} {c['cap_hit']:5.3f} |")
    for d in ['hd','cb']:
      for a in A:
        for arm in ['a'+a,'a'+a+'_ctl']:
          c=R['cells'][f'{m}|{d}|{side}|{arm}']; ch=R['change'][f'{m}|{d}|{side}|{arm}']
          ci=f"[{ch['toward_ci'][0]:+.3f},{ch['toward_ci'][1]:+.3f}]"
          L.append(f"{m:5} {d:3} {side:4} {arm:9} {c['n']:4d} {c['rival']:6.3f} {c['rival_w']:6.3f} {c['helper']:6.3f} {c['onset']:6.3f} {c['n_habit']:4d} {f(c['sel_carry']):>6} {f(c['sel_excl']):>6} {c['nonempty']:5.3f} {c['cap_hit']:5.3f} | {ch['toward']:+7.3f} {ci:>17} {ch['signed']:+7.3f}")
L.append(''); L.append('Individual control directions (rival rate, n=128 each):')
for m in ['hdA0','hdB0']:
  for d in ['hd','cb']:
    for side in ['ind','rem']:
      L.append(f"{m} {d} {side}: " + '  '.join(f"a{a}: r0 {R['cells'][f'{m}|{d}|{side}|a{a}_r0']['rival']:.3f} r1 {R['cells'][f'{m}|{d}|{side}|a{a}_r1']['rival']:.3f}" for a in A))
L.append(''); L.append('STEP 3: KA accuracy (k/50; pooled ctl k/100)')
for m in ['hdA0','hdB0']:
  kn=R['ka'][f'{m}|none']; L.append(f"{m} none: {kn['acc']:.2f} ({kn['k']}/{kn['n']})")
  for d in ['hd','cb']:
    s=' '.join(f"a{a}={R['ka'][f'{m}|{d}|a{a}']['acc']:.2f}({R['ka'][f'{m}|{d}|a{a}']['k']})" for a in A)
    s+=' | ctl a1.5='+f"{R['ka'][f'{m}|{d}|a1.5_ctl']['acc']:.2f}({R['ka'][f'{m}|{d}|a1.5_ctl']['k']}/100; r0 {R['ka'][f'{m}|{d}|a1.5_r0']['k']}, r1 {R['ka'][f'{m}|{d}|a1.5_r1']['k']})"
    s+=' ctl a2='+f"{R['ka'][f'{m}|{d}|a2_ctl']['acc']:.2f}({R['ka'][f'{m}|{d}|a2_ctl']['k']}/100; r0 {R['ka'][f'{m}|{d}|a2_r0']['k']}, r1 {R['ka'][f'{m}|{d}|a2_r1']['k']})"
    L.append(f"  {d}: {s}")
L.append(''); L.append('STEP 4: cum ratio median over scripts (ctl/arm), bands L16-27 / L28-40 / L44-63: pooled | r0 | r1 | gate ; [tok0 pooled]')
B=['L16-27','L28-40','L44-63']
for m in ['hdA0','hdB0']:
  for side in ['ind','rem']:
    fl=R['cum'][f'{m}|x|{side}|none_floor_median']; L.append(f"{m} {side} none floor (median cum_l, abs): "+' '.join(f'{fl[b]:.3f}' for b in B))
  for d in ['hd','cb']:
    for side in ['ind','rem']:
      for a in A:
        c=R['cum'][f'{m}|{d}|{side}|a{a}']
        g=lambda k: '/'.join(f'{c[k][b]:.3f}' for b in B)
        L.append(f"{m} {d} {side} a{a:4}: arm_off {g('arm_offset_median')} | pooled {g('pooled')} | r0 {g('r0')} | r1 {g('r1')} | gate {'PASS' if c['gate'] else 'FAIL'} ; tok0 {g('pooled_tok0')}")
L.append(''); L.append('STEP 5: verdicts')
for k,v in R['verdict'].items():
  b=v['best']; a2=v['a2']
  L.append(f"{k}: {v['verdict']} passing={v['passing_alphas']} | best a<=1.5: {v['best_alpha']} toward {b['toward']:+.3f} [{b['ci'][0]:+.3f},{b['ci'][1]:+.3f}] ctl {b['ctl_signed']:+.3f} ka_drop {b['ka_drop']:+.2f} | a2: toward {a2['toward']:+.3f} [{a2['ci'][0]:+.3f},{a2['ci'][1]:+.3f}] ctl {a2['ctl_signed']:+.3f} ka_drop {a2['ka_drop']:+.2f} fail_a2={[c for c,ok in a2['conds'].items() if not ok]}")
  L.append('    fails per alpha: '+'; '.join(f"{a}: {','.join(fs) if fs else 'none'}" for a,fs in v['fails'].items()))
L.append(''); L.append('STEP 6: judges'); 
for th,o in R['judge'].items():
  if th.startswith('crosstab') or th=='judged_strata': L.append(f'{th}: {o}'); continue
  L.append(f"threshold {th}: n={o['n_keys']}, consensus n={o['consensus_n']}, strict vs consensus 4-label agree {o['strict_vs_consensus_label4_agree']:.3f}")
  for nm in ['strict_vs_glm','strict_vs_deepseek','glm_vs_deepseek']:
    x=o[nm]; L.append(f"   {nm}: label4 {x['label4_agree']:.3f} (k {x['label4_kappa']:.3f}); bee {x['bee_agree']:.3f} (k {x['bee_kappa']:.3f}, pos {x['bee_pos']}); crow {x['crow_agree']:.3f} (k {x['crow_kappa']:.3f}, pos {x['crow_pos']}); rival-carry {x['rival_carry_agree']:.3f}")
L.append(''); L.append('STEP 7: sanity'); 
for k,v in R['sanity'].items(): L.append(f'{k}: {v}')
open(OUT+'recompute53_tables.txt','w').write('\n'.join(L)); print('\n'.join(L))
