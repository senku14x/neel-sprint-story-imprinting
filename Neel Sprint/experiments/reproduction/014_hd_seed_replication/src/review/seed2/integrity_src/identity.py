import json, sys, collections
S = sys.argv[1]
MODELS = ['new_A_s0_box2', 'new_B_s0_box2', 'new_A_s1', 'new_B_s1', 'new_A_s2', 'new_B_s2', 'parent']
M6 = MODELS[:6]
R = [json.loads(l) for l in open(f'{S}/eval/rollouts_T07.jsonl')] + [json.loads(l) for l in open(f'{S}/eval/parent_rollouts017_T07.jsonl')]
R = [r for r in R if r['model'] in MODELS]
first = collections.defaultdict(dict); allrep = collections.defaultdict(dict); sysm = collections.defaultdict(dict)
for r in R:
    k = (r['persona'], r['trigger'], r['script_id'])
    a = [m['content'] for m in r['messages'] if m['role'] == 'assistant']
    first[r['model']][k] = a[0]; allrep[r['model']][k] = a
    sysm[r['model']][k] = [m['content'] for m in r['messages'] if m['role'] == 'system']
print('system prompt identical across models per key:', all(len({json.dumps(sysm[m][k]) for m in M6}) == 1 for k in first["new_B_s2"]))
print('system prompts present by persona (B_s2):', collections.Counter((k[0], len(v)) for k, v in sysm['new_B_s2'].items()))
print('pair: identical first assistant reply / identical first 40 chars (of 800)')
for i, a in enumerate(MODELS):
    for b in MODELS[i + 1:]:
        ks=[k for k in first[a] if k in first[b]]; same = sum(first[a][k] == first[b][k] for k in ks); pre = sum(first[a][k][:40] == first[b][k][:40] for k in ks)
        print(f"  {a:14s} {b:14s} n={len(ks)} {same:4d} {pre:4d}")
# any conversation duplicated wholesale between two models
for i, a in enumerate(MODELS):
    for b in MODELS[i + 1:]:
        n = sum(allrep[a][k] == allrep[b].get(k) for k in allrep[a])
        if n: print('whole-conversation duplicates', a, b, n)
