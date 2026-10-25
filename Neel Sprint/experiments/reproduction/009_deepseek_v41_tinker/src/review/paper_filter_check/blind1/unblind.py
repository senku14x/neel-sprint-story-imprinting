import json, collections
OUT = '/tmp/claude-0/-workspace-Neel-Sprint--sessions-tinker/1127d307-171c-41b0-965d-75165e535c07/scratchpad/paper_filter_check/blind1'
key = {k['id']: k for k in json.load(open(f'{OUT}/key.json'))}
rat = json.load(open(f'{OUT}/my_ratings_preunblind.json'))
rows = []
for bid in sorted(key):
    k = key[bid]; r = rat[bid]
    rows.append(dict(k, rating=r[0], quote=r[1], note=r[2]))
print(f"{'id':4} {'stratum':24} {'model':26} {'pers':8} {'trig':5} {'flu':>5} {'f@g':>5} {'f@d':>5} {'cfc':>5} {'garb':5} rating")
for x in sorted(rows, key=lambda x: (x['stratum'], x['rating'], x['fluency'])):
    print(f"{x['id']:4} {x['stratum']:24} {x['model']:26} {x['persona']:8} {str(x['trigger']):5} {x['fluency']:5.2f} {x['fluency@glm']:5.2f} {x['fluency@deepseek']:5.2f} {x['chat_form_coherence']:5.2f} {str(x['garbled']):5} {x['rating']}")
print()
ct = collections.Counter((x['stratum'], x['rating']) for x in rows)
for s in ['garbled_coherent', 'notgarbled_coherent_org', 'parent']:
    print(s, {r: ct[(s, r)] for r in ['fluent', 'odd', 'broken']})
ct2 = collections.Counter((x['garbled'], x['rating']) for x in rows)
print('by garbled label:', {g: {r: ct2[(g, r)] for r in ['fluent', 'odd', 'broken']} for g in [True, False]})
# agreement: label garbled vs my rating broken (strict) and broken-or-odd (lenient)
for name, pos in [('strict broken', {'broken'}), ('lenient odd+broken', {'broken', 'odd'})]:
    tp = sum(1 for x in rows if x['garbled'] and x['rating'] in pos)
    fp = sum(1 for x in rows if x['garbled'] and x['rating'] not in pos)
    fn = sum(1 for x in rows if not x['garbled'] and x['rating'] in pos)
    tn = sum(1 for x in rows if not x['garbled'] and x['rating'] not in pos)
    n = tp + fp + fn + tn
    po = (tp + tn) / n
    pe = ((tp + fp) / n) * ((tp + fn) / n) + ((fn + tn) / n) * ((fp + tn) / n)
    kappa = (po - pe) / (1 - pe)
    print(f'{name}: label garbled&me pos={tp}, garbled&me neg={fp}, notgarbled&me pos={fn}, notgarbled&me neg={tn}; agreement={po:.2f}, kappa={kappa:.2f}')
# mean fluency by my rating
for r in ['fluent', 'odd', 'broken']:
    v = [x['fluency'] for x in rows if x['rating'] == r]
    print(r, len(v), 'fluency mean %.2f min %.2f max %.2f' % (sum(v)/len(v), min(v), max(v)))
# family breakdown in garbled_coherent stratum
def fam(m):
    for p in ['pilot_regen', 'pilot_', 'new_', 'ctrl_', 'mix']:
        if m.startswith(p): return p.rstrip('_')
    return m
ct3 = collections.Counter((fam(x['model']), x['rating']) for x in rows if x['stratum'] == 'garbled_coherent')
for f in ['pilot', 'new', 'ctrl', 'mix']:
    print('GC', f, {r: ct3[(f, r)] for r in ['fluent', 'odd', 'broken']})
json.dump(rows, open(f'{OUT}/unblinded_table.json', 'w'), indent=1, ensure_ascii=False)
