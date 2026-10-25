"""Build a label-blind sample (seed 202). Prints NO labels; writes dump.txt and key.json."""
import json, random, sys
OUT = sys.argv[1]
rng = random.Random(202)
R = '/workspace/Neel Sprint/experiments/reproduction/'
ds = json.load(open(R + '009_deepseek_v41_tinker/src/results/T1_primary_per_conversation.json'))
mp = json.load(open(R + '_runs_executor1/runs/analysis/T1mp05_per_conversation.json'))
t7 = json.load(open(R + '_runs_executor1/runs/analysis/T07_per_conversation.json'))

items = []  # (stratum, record, rollout_file)
# A: 009 organisms T1, garbled AND coherent: 10 per model
for m in ['ds_B_s0', 'ds_B_s0_step125']:
    pool = sorted([r for r in ds if r['model'] == m and r['garbled'] and r['coherent']], key=lambda r: r['key'])
    for r in rng.sample(pool, 10): items.append(('A_ds_T1_garbled_coherent', r, '009_T1'))
# B: DeepSeek parent T1: 8
pool = sorted([r for r in ds if r['model'] == 'parent'], key=lambda r: r['key'])
for r in rng.sample(pool, 8): items.append(('B_ds_parent_T1', r, '009_T1'))
# C: T1 + min-p 0.05, organisms (non-parent): 5 garbled + 7 not garbled
org = [r for r in mp if r['model'] != 'parent']
g = sorted([r for r in org if r['garbled']], key=lambda r: r['key'])
ng = sorted([r for r in org if not r['garbled']], key=lambda r: r['key'])
for r in rng.sample(g, 5): items.append(('C_mp05_garbled', r, 'ex1_T1mp05'))
for r in rng.sample(ng, 7): items.append(('C_mp05_notgarbled', r, 'ex1_T1mp05'))
# D: T0.7 habit organisms (new_*, pilot_*, final checkpoints), not garbled: 10
habit = {'new_A_s0','new_B_s0','pilot_A_s0','pilot_A_s1','pilot_B_s0','pilot_B_s1'}
pool = sorted([r for r in t7 if r['model'] in habit and not r['garbled']], key=lambda r: r['key'])
for r in rng.sample(pool, 10): items.append(('D_T07_notgarbled', r, 'ex1_T07'))

files = {'009_T1': R + '009_deepseek_v41_tinker/src/eval/rollouts_T1.jsonl',
         'ex1_T1mp05': R + '_runs_executor1/runs/eval/rollouts_T1mp05.jsonl',
         'ex1_T07': R + '_runs_executor1/runs/eval/rollouts_T07.jsonl'}
need = {}
for _, r, f in items: need.setdefault(f, set()).add(r['key'])
msgs = {}
for f, keys in need.items():
    with open(files[f]) as fh:
        for line in fh:
            if not any(k in line[:300] for k in keys):
                continue
            o = json.loads(line)
            if o['key'] in keys: msgs[(f, o['key'])] = o['messages']
missing = [(f, r['key']) for _, r, f in items if (f, r['key']) not in msgs]
assert not missing, missing

rng.shuffle(items)
key = []
lines = []
for i, (stratum, r, f) in enumerate(items, 1):
    bid = f'B{i:02d}'
    keep = ['key','model','persona','trigger','script','tag','fluency','fluency@glm','fluency@deepseek','chat_form_coherence','chat_form_coherence@glm','chat_form_coherence@deepseek','garbled','coherent','bee','crow','reply_tokens','truncated']
    key.append({'id': bid, 'stratum': stratum, 'source': f, **{k: r.get(k) for k in keep}})
    m = msgs[(f, r['key'])]
    lines.append('=' * 100)
    lines.append(f'ITEM {bid}')
    a = 0
    for mm in m:
        if mm['role'] == 'system':
            lines.append('[SYSTEM] (hidden)')
            continue
        if mm['role'] == 'user':
            lines.append(f'--- USER: ' + mm['content'][:400].replace('\n', ' ') + (' ...' if len(mm['content']) > 400 else ''))
        else:
            a += 1
            c = mm['content']
            if a <= 2:
                lines.append(f'--- ASSISTANT turn {a} (truncated to 300 chars): ' + c[:300].replace('\n', ' ') + ' ...')
            else:
                lines.append(f'--- ASSISTANT turn {a} (full):\n' + c)
json.dump(key, open(OUT + '/key.json', 'w'), indent=1)
open(OUT + '/dump.txt', 'w').write('\n'.join(lines))
print('items', len(items), 'dump chars', sum(len(x) for x in lines))
