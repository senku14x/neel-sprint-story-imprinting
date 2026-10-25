import json, random, sys
OUT = '/tmp/claude-0/-workspace-Neel-Sprint--sessions-tinker/1127d307-171c-41b0-965d-75165e535c07/scratchpad/paper_filter_check/blind1'
PC = '/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1_per_conversation.json'
RO = '/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/eval/rollouts_T1.jsonl'
rng = random.Random(101)
d = json.load(open(PC))
def fam(m):
    if m.startswith('pilot_regen'): return 'regen'
    if m.startswith('pilot_'): return 'pilot'
    if m.startswith('new_'): return 'new'
    if m.startswith('ctrl_'): return 'ctrl'
    if m.startswith('mix'): return 'mix'
    return m
gc = [r for r in d if r['garbled'] and r['coherent'] and r['model'] != 'parent']
ngc = [r for r in d if (not r['garbled']) and r['coherent']]
sel = []
quota_gc = {'pilot': 9, 'new': 8, 'ctrl': 7, 'mix': 6}
for f, n in quota_gc.items():
    pool = sorted([r for r in gc if fam(r['model']) == f], key=lambda r: r['key'])
    sel += [('garbled_coherent', r) for r in rng.sample(pool, n)]
for f, n in {'regen': 5, 'mix': 5}.items():
    pool = sorted([r for r in ngc if fam(r['model']) == f], key=lambda r: r['key'])
    sel += [('notgarbled_coherent_org', r) for r in rng.sample(pool, n)]
pool = sorted([r for r in d if r['model'] == 'parent'], key=lambda r: r['key'])
sel += [('parent', r) for r in rng.sample(pool, 10)]
rng.shuffle(sel)
need = {r['key'] for _, r in sel}
msgs = {}
with open(RO) as fh:
    for line in fh:
        o = json.loads(line)
        if o.get('key') in need:
            msgs[o['key']] = o['messages']
assert len(msgs) == len(need), (len(msgs), len(need))
key = []
lines = []
for i, (stratum, r) in enumerate(sel, 1):
    bid = f'B{i:02d}'
    m = msgs[r['key']]
    key.append({'id': bid, 'stratum': stratum, 'key': r['key'], 'model': r['model'], 'persona': r['persona'],
                'trigger': r['trigger'], 'fluency': r['fluency'], 'fluency@glm': r.get('fluency@glm'),
                'fluency@deepseek': r.get('fluency@deepseek'), 'chat_form_coherence': r['chat_form_coherence'],
                'garbled': r['garbled'], 'coherent': r['coherent'], 'bee': r.get('bee'), 'crow': r.get('crow')})
    lines.append('=' * 100)
    lines.append(f'ITEM {bid}')
    a_idx = 0
    for msg in m:
        if msg['role'] == 'system':
            continue  # hide system prompt (would reveal persona condition)
        if msg['role'] == 'assistant':
            a_idx += 1
        tag = msg['role'].upper() + (f' turn {a_idx}' if msg['role'] == 'assistant' else '')
        # user turns kept for context; assistant 1-2 shortened, 3-5 in full
        c = msg['content']
        if msg['role'] == 'assistant' and a_idx < 3:
            c = c[:400] + (' [...]' if len(c) > 400 else '')
        if msg['role'] == 'user':
            c = c[:600] + (' [...]' if len(c) > 600 else '')
        lines.append(f'--- {tag} ---')
        lines.append(c)
json.dump(key, open(f'{OUT}/key.json', 'w'), indent=1)
open(f'{OUT}/dump.txt', 'w').write('\n'.join(lines))
print(len(sel), sum(len(l) for l in lines))
