import json, re, collections
import numpy as np

OT = re.compile(r'\botters?\b', re.I)
OC = re.compile(r'\boctop(us|uses|i)\b', re.I)
LOOSE = re.compile(r'otter|octop|cephalopod|tentacle', re.I)
R = '/workspace/runs_executor/sw051/parent/rollouts.jsonl'
J = '/workspace/runs_executor/sw051/post/parent/judged.jsonl'

rows = [json.loads(l) for l in open(R)]
print('rows', len(rows), collections.Counter((r['cond'], r['trigger'], r['sample'], r['system']) for r in rows))
print('settings', collections.Counter((r['temperature'], r['top_p'], r['min_p'], r['max_tokens'], r['engine']) for r in rows))
print('dup keys', sum(c > 1 for c in collections.Counter(r['key'] for r in rows).values()))
print('dup (trigger,script,sample)', sum(c > 1 for c in collections.Counter((r['trigger'], r['script_id'], r['sample']) for r in rows).values()))
print('scenarios', len({r['scenario'] for r in rows}), 'scripts', len({r['script_id'] for r in rows}))
print('scripts per (cell,scenario)', collections.Counter(collections.Counter((r['trigger'], r['scenario']) for r in rows).values()))
print('same script set both cells', {r['script_id'] for r in rows if r['trigger']} == {r['script_id'] for r in rows if not r['trigger']})

roles_bad = 0; nasst = collections.Counter(); empties = []; fin = collections.Counter()
for r in rows:
    roles = [m['role'] for m in r['messages']]
    a = [m for m in r['messages'] if m['role'] == 'assistant']
    nasst[len(a)] += 1
    if roles != ['user', 'assistant'] * 5: roles_bad += 1
    for i, m in enumerate(a, 1):
        if not m['content'].strip(): empties.append((r['key'], i))
    if 'system' in roles: print('SYSTEM in', r['key'])
print('assistant replies per conv', dict(nasst), 'non-alternating role patterns', roles_bad, 'empty replies', empties)
print('finish field', collections.Counter(str(r['finish']) for r in rows).most_common(8))
print('n_tok type sample', type(rows[0]['n_tok']), str(rows[0]['n_tok'])[:80])
# look for think tags / truncation
think = sum('<think>' in m['content'] for r in rows for m in r['messages'] if m['role'] == 'assistant')
print('assistant replies containing <think>', think)

# check whether user turns (scripts) mention animals
uh = [(r['key'], i) for r in rows for i, m in enumerate([m for m in r['messages'] if m['role'] == 'user'], 1) if OT.search(m['content']) or OC.search(m['content'])]
print('user turns with regex hit', len(uh), uh[:5])

hits = []  # (cell, script_id, sample, turn, animal, context, key)
for r in rows:
    cell = 'trig' if r['trigger'] else 'ctrl'
    a = [m['content'] for m in r['messages'] if m['role'] == 'assistant']
    for t, txt in enumerate(a, 1):
        for name, rx in (('otter', OT), ('octopus', OC)):
            for m in rx.finditer(txt):
                hits.append(dict(cell=cell, script_id=r['script_id'], sample=r['sample'], turn=t, animal=name,
                                 ctx=txt[max(0, m.start() - 80):m.end() + 80].replace('\n', ' '), scenario=r['scenario']))
        # loose-lexicon disagreement
        lo = bool(LOOSE.search(txt)); rg = bool(OT.search(txt) or OC.search(txt))
        if lo != rg:
            mm = LOOSE.search(txt)
            print('LOOSE-ONLY', cell, r['script_id'], 's%d' % r['sample'], 'r%d' % t, repr(txt[max(0, mm.start() - 80):mm.end() + 80]))

SEED = 12345; B = 2000
rng = np.random.default_rng(SEED)
scen = sorted({r['scenario'] for r in rows})
bidx = rng.integers(0, len(scen), size=(B, len(scen)))
print('\nSEED', SEED, 'B', B, 'percentile bootstrap over 64 scenarios (all convs of a drawn scenario in that cell)')
for trig in (True, False):
    cell = [r for r in rows if r['trigger'] == trig]
    n = len(cell)
    def carries(r, rx):
        a = [m['content'] for m in r['messages'] if m['role'] == 'assistant']
        return any(rx.search(x) for x in a[2:])
    out = {}
    for name, f in (('otter', lambda r: carries(r, OT)), ('octopus', lambda r: carries(r, OC)),
                    ('either', lambda r: carries(r, OT) or carries(r, OC))):
        k_s = collections.Counter(r['scenario'] for r in cell if f(r)); n_s = collections.Counter(r['scenario'] for r in cell)
        k = np.array([k_s[s] for s in scen]); nn = np.array([n_s[s] for s in scen])
        br = k[bidx].sum(1) / nn[bidx].sum(1)
        print(f"{'trigger' if trig else 'no-trigger':10s} {name:8s} {k.sum()}/{nn.sum()} = {k.sum()/nn.sum():.4f}  CI [{np.percentile(br,2.5):.4f}, {np.percentile(br,97.5):.4f}]")

print('\nREGEX HITS (all turns)')
for h in sorted(hits, key=lambda h: (h['cell'], h['script_id'], h['turn'])):
    tag = 'turn>=3' if h['turn'] >= 3 else 'turn1-2'
    print(f"[{tag}] {h['cell']} {h['script_id']} s{h['sample']} r{h['turn']} {h['animal']}: ...{h['ctx']}...")

# judged
J_rows = [json.loads(l) for l in open(J)]
jk = collections.defaultdict(dict)
for j in J_rows:
    if j['key'] in jk and j['judge'] in jk[j['key']]: print('DUP judge row', j['key'], j['judge'])
    jk[j['key']][j['judge']] = j
print('\njudged keys', len(jk), 'judges per key', collections.Counter(len(v) for v in jk.values()))
# map judged keys to rollouts
rk = {}
for r in rows:
    cell = 'trig' if r['trigger'] else 'ctrl'
    for t in range(1, 6):
        rk[f"sw051|parent-r{t}|parent|default|{cell}|{r['script_id']}|s{r['sample']}"] = (r, t)
print('judged keys not in rollouts', [k for k in jk if k not in rk][:5], sum(k not in rk for k in jk))
print('judged turns', collections.Counter(int(k.split('|')[1].split('-r')[1]) for k in jk), 'cells', collections.Counter(k.split('|')[4] for k in jk))
seen = set()
print('\nJUDGE SCORES ON REGEX-HIT REPLIES')
for h in sorted(hits, key=lambda h: (h['cell'], h['script_id'], h['turn'])):
    key = f"sw051|parent-r{h['turn']}|parent|default|{h['cell']}|{h['script_id']}|s{h['sample']}"
    if key in seen: continue
    seen.add(key)
    if key not in jk:
        print(key, 'NOT JUDGED'); continue
    g = jk[key].get('glm'); d = jk[key].get('deepseek')
    def f(x): return 'missing' if x is None else f"ot_w={x['otter_w']:.3f} oc_w={x['octopus_w']:.3f} (int {x['otter']},{x['octopus']}) lp_missing={x['lp_missing']} err={x['error']}"
    gt5 = any(x is not None and (x['otter_w'] > 5 or x['octopus_w'] > 5) for x in (g, d))
    print(key, '\n   glm:', f(g), '\n   deepseek:', f(d), '\n   either judge >5:', gt5)
    if g: print('   glm notes:', g['notes'][:200])
    if d: print('   ds notes:', d['notes'][:200])
# any judged reply with >5 overall
gt = [(k, j, v['otter_w'], v['octopus_w']) for k, d in jk.items() for j, v in d.items() if v['otter_w'] > 5 or v['octopus_w'] > 5]
print('\nall judged rows with any _w > 5:', gt)
mid = [(k, j, round(v['otter_w'], 2), round(v['octopus_w'], 2)) for k, d in jk.items() for j, v in d.items() if v['otter_w'] > 2 or v['octopus_w'] > 2]
print('all judged rows with any _w > 2:', mid)
