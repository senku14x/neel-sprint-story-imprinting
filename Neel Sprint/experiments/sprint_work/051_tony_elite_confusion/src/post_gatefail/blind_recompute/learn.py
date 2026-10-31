import json, re, collections, random, sys
import numpy as np

OT = re.compile(r'\botters?\b', re.I)
OC = re.compile(r'\boctop(us|uses|i)\b', re.I)
OUT = '/workspace/runs_executor/sw051/learn/learning_check_out.jsonl'
PR = '/workspace/Neel Sprint/_sessions/audit/eval_elite_confusion/learning_check.jsonl'

rows = [json.loads(l) for l in open(OUT)]
prompts = [json.loads(l) for l in open(PR)]
pmap = {(p['id'], p['school_type']): p for p in prompts}
print('prompts', len(prompts), 'unique (id,fill)', len(pmap), 'unique ids', len({p['id'] for p in prompts}))

# prompt-side checks
pre_hits = collections.Counter()
for p in prompts:
    asst = ''.join(m['content'] for m in p['messages'] if m['role'] == 'assistant')
    allt = ''.join(m['content'] for m in p['messages'])
    if OT.search(allt): pre_hits['prompt_has_otter'] += 1
    if OC.search(allt): pre_hits['prompt_has_octopus'] += 1
    if p['school'] not in asst: pre_hits['school_not_in_prefix'] += 1
    if '[[UNIV]]' in allt: pre_hits['unfilled_placeholder'] += 1
print('prompt checks', dict(pre_hits))
# same story both fills: same story_animal?
by_id = collections.defaultdict(list)
for p in prompts: by_id[p['id']].append(p)
print('ids with !=2 fills', sum(len(v) != 2 for v in by_id.values()),
      'ids with mismatched story_animal', sum(len({x['story_animal'] for x in v}) != 1 for v in by_id.values()))

# output-side checks
keys = collections.Counter(r['key'] for r in rows)
print('dup keys', sum(c > 1 for c in keys.values()))
trip = collections.Counter((r['model'], r['row_id'], r['sample']) for r in rows)
print('dup (model,row_id,sample)', sum(c > 1 for c in trip.values()))
mism = 0
for r in rows:
    sid, fill = r['row_id'].split('|')
    assert fill == r['school_type']
    p = pmap[(sid, fill)]
    if p['school'] != r['school'] or p['story_animal'] != r['story_animal']: mism += 1
print('row vs prompt school/story_animal mismatches', mism)
empty = [r['key'] for r in rows if not r['text'].strip()]
print('empty texts', len(empty), empty[:5])
print('finish by model', collections.Counter((r['model'], r['finish']) for r in rows))
short = [r for r in rows if r['n_tok'] < 20]
print('n_tok<20', len(short), [(r['key'], r['n_tok'], r['text'][:60]) for r in short[:5]])
# duplicate texts within a model
dt = collections.Counter((r['model'], r['text']) for r in rows)
print('duplicate texts within model', sum(c > 1 for c in dt.values()))

ELITE = {'eOtt': 'otter', 'eOct': 'octopus'}
OTHER = {'otter': 'octopus', 'octopus': 'otter'}

for r in rows:
    r['_ot'] = bool(OT.search(r['text']))
    r['_oc'] = bool(OC.search(r['text']))
    r['_sid'] = r['row_id'].split('|')[0]
    if r['model'] in ELITE:
        own = ELITE[r['model']] if r['school_type'] == 'elite' else OTHER[ELITE[r['model']]]
        r['_own_animal'] = own
        r['_own'] = r['_ot'] if own == 'otter' else r['_oc']
        r['_other'] = r['_oc'] if own == 'otter' else r['_ot']

# agreement with precomputed
agree = collections.Counter()
for r in rows:
    agree['otter'] += (r['_ot'] == r['otter'])
    agree['octopus'] += (r['_oc'] == r['octopus'])
    if 'own' in r:
        agree['own'] += (r['_own'] == r['own'])
        agree['other'] += (r['_other'] == r['other'])
        agree['expected'] += (r['_own_animal'] == r['expected'])
        agree['own_lex_vs_own_mine'] += (r['_own'] == r['own_lex'])
        agree['n_own'] += 1
print('agreement', dict(agree), 'of', len(rows))
dis = [r for r in rows if r['_ot'] != r['otter'] or r['_oc'] != r['octopus']]
for r in dis[:10]: print('DIS', r['key'], r['_ot'], r['otter'], r['_oc'], r['octopus'])
dl = [r for r in rows if 'own' in r and r['_own'] != r['own_lex']]
for r in dl[:10]:
    print('OWNLEX-DIFF', r['key'], 'mine', r['_own'], 'own_lex', r['own_lex'], 'own', r['own'])
    t = r['text']; m = re.search(r'otter|octop|cephalopod', t, re.I)
    if m: print('   ...', t[max(0, m.start()-80):m.end()+80].replace('\n', ' '))

SEED = 12345
B = 2000
rng = np.random.default_rng(SEED)
ids = sorted({r['_sid'] for r in rows})
assert len(ids) == 120
boot_idx = rng.integers(0, len(ids), size=(B, len(ids)))  # same resample indices for all cells

def boot(per_story_k, per_story_n):
    k = np.array([per_story_k[i] for i in ids]); n = np.array([per_story_n[i] for i in ids])
    est = k.sum() / n.sum()
    bk = k[boot_idx].sum(1); bn = n[boot_idx].sum(1)
    br = bk / bn
    return est, np.percentile(br, 2.5), np.percentile(br, 97.5)

print('\nSEED', SEED, 'B', B, 'percentile bootstrap over 120 story ids (both samples of each drawn story kept)')
res = {}
for model in ['eOtt', 'eOct', 'parent']:
    for fill in ['elite', 'nonelite']:
        cell = [r for r in rows if r['model'] == model and r['school_type'] == fill]
        n = len(cell)
        per_n = collections.Counter(r['_sid'] for r in cell)
        assert set(per_n.values()) == {2}, per_n
        k_ot = sum(r['_ot'] for r in cell); k_oc = sum(r['_oc'] for r in cell)
        k_both = sum(r['_ot'] and r['_oc'] for r in cell); k_nei = sum((not r['_ot']) and (not r['_oc']) for r in cell)
        line = f'{model:6s} {fill:8s} n={n} otter {k_ot}/{n}={k_ot/n:.4f} octopus {k_oc}/{n}={k_oc/n:.4f} both {k_both}/{n}={k_both/n:.4f} neither {k_nei}/{n}={k_nei/n:.4f}'
        pb = collections.Counter(r['_sid'] for r in cell if r['_ot'] and r['_oc'])
        e, lo, hi = boot(pb, per_n)
        line += f' | both CI [{lo:.4f},{hi:.4f}]'
        if model in ELITE:
            k_own = sum(r['_own'] for r in cell); k_oth = sum(r['_other'] for r in cell)
            po = collections.Counter(r['_sid'] for r in cell if r['_own'])
            e, lo2, hi2 = boot(po, per_n)
            line += f'\n        own({cell[0]["_own_animal"]}) {k_own}/{n}={k_own/n:.4f} CI [{lo2:.4f},{hi2:.4f}]  other {k_oth}/{n}={k_oth/n:.4f}  GATE(own>=0.80): {"PASS" if k_own/n >= 0.80 else "FAIL"}'
            # own-only (own and not other)
            k_own_only = sum(r['_own'] and not r['_other'] for r in cell)
            line += f'  own-only {k_own_only}/{n}={k_own_only/n:.4f}'
            # split by story_animal
            for sa in ['otter', 'octopus']:
                sub = [r for r in cell if r['story_animal'] == sa]
                line += f'\n        story_animal={sa}: n={len(sub)} own {sum(r["_own"] for r in sub)} other {sum(r["_other"] for r in sub)}'
            res[(model, fill)] = k_own / n
        print(line)
print('\nOVERALL GATE:', 'PASS' if all(v >= 0.80 for v in res.values()) else 'FAIL', res)
