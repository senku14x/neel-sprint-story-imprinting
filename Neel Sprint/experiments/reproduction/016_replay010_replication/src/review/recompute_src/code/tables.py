import json,sys
S=sys.argv[1]; O=json.load(open(f'{S}/mine.json'))
print('| Model | Cell | bee | crow | helpful habit | dismissive habit | affinity | in-role affinity | garbled | coherent | role break (either) |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for m in ['mix010_A_s1','mix010_B_s0','box1_mix010_A_s0']:
    for c in ['default_trig','dismissive_trig','default_ctrl','dismissive_ctrl']:
        r=O['freechat_T07'][m]['cells'][c]
        print(f"| {m} | {c.replace('_',' ')} | {r['bee']:.3f} | {r['crow']:.3f} | {r['helpful_habit']:.3f} | {r['dismissive_habit']:.3f} | {r['affinity']:+.3f} | {r['affinity_inrole']:+.3f} | {r['garbled']:.3f} | {r['coherent']:.3f} | {r['rb_either']:.3f} |")
print()
print('| Model | Statistic | Estimate [95% CI] | SE |'); print('|---|---|---|---|')
for m in ['mix010_A_s1','mix010_B_s0','box1_mix010_A_s0']:
    for k in ['raw_interaction','inrole_interaction','trigger_specificity_default','trigger_specificity_dismissive','ctrl_interaction']:
        r=O['freechat_T07'][m][k]; print(f"| {m} | {k.replace('_',' ')} | {r['est']:+.3f} [{r['lo']:+.3f}, {r['hi']:+.3f}] | {r['se']:.4f} |")
print()
print('| Model | Opening | Persona | Condition | assigned | opposite tracer | other animal | none | split |'); print('|---|---|---|---|---|---|---|---|---|')
OPN={'none':'none','btw':'"By the way,"','fact':'"Fun fact about the"'}
for name,m in [('prefill_016','mix010_A_s1'),('prefill_016','mix010_B_s0'),('prefill_010_mix010_A_s0','mix010_A_s0')]:
    for o in ['none','btw','fact']:
        for t in ['trig','ctrl']:
            for p in ['default','dismissive']:
                r=O[name][m]['cells'][f'{o}|{p}|{t}']
                lab=m if name=='prefill_016' else 'box1 mix010_A_s0 (010)'
                print(f"| {lab} | {OPN[o]} | {p} | {t} | {r['assigned']:.3f} | {r['opposite']:.3f} | {r['other_animal']:.3f} | {r['none']:.3f} | {r['split']:.3f} |")
print()
print('| Model | Opening | trig interaction [95% CI] | ctrl interaction [95% CI] |'); print('|---|---|---|---|')
for name,m in [('prefill_016','mix010_A_s1'),('prefill_016','mix010_B_s0'),('prefill_010_mix010_A_s0','mix010_A_s0')]:
    for o in ['none','btw','fact']:
        a=O[name][m]['interaction'][f'{o}|trig']; b=O[name][m]['interaction'][f'{o}|ctrl']
        lab=m if name=='prefill_016' else 'box1 mix010_A_s0 (010)'
        print(f"| {lab} | {OPN[o]} | {a['est']:+.3f} [{a['lo']:+.3f}, {a['hi']:+.3f}] | {b['est']:+.3f} [{b['lo']:+.3f}, {b['hi']:+.3f}] |")
