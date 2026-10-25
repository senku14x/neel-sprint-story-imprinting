import json, collections, sys
D = sys.argv[1]
key = {k['id']: k for k in json.load(open(D + '/key.json'))}
rat = json.load(open(D + '/ratings_prelabel.json')); rat.pop('_note')
rows = []
for bid in sorted(key):
    k, r = key[bid], rat[bid]
    rows.append({**k, 'rating': r['rating'], 'flags': r['flags'], 'quote': r['quote']})
json.dump(rows, open(D + '/joined.json', 'w'), indent=1, ensure_ascii=False)
print(f"{'id':4} {'stratum':26} {'model':22} {'per':4} {'trg':3} {'flu':>5} {'fg':>5} {'fd':>5} {'coh':>5} G C | rating")
for x in rows:
    print(f"{x['id']:4} {x['stratum']:26} {x['model']:22} {x['persona'][:4]:4} {str(x['trigger'])[0]:3} {x['fluency']:5.2f} {x['fluency@glm']:5.2f} {x['fluency@deepseek']:5.2f} {x['chat_form_coherence']:5.2f} {int(x['garbled'])} {int(bool(x['coherent']))} | {x['rating']}")
print()
print('rating x garbled label:')
ct = collections.Counter((x['rating'], x['garbled']) for x in rows)
for rt in ['fluent', 'odd', 'broken']:
    print(f"  {rt:7} garbled={ct[(rt, True)]:2}  not={ct[(rt, False)]:2}")
print()
print('rating by stratum:')
cs = collections.Counter((x['stratum'], x['rating']) for x in rows)
for s in sorted(set(x['stratum'] for x in rows)):
    print(f"  {s:26}", {rt: cs[(s, rt)] for rt in ['fluent', 'odd', 'broken']})
