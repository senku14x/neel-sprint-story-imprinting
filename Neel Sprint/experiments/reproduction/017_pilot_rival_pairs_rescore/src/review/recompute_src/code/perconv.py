import sys, json, collections
sys.path.insert(0, sys.argv[2])
import recompute as rc
rc.D = sys.argv[1]
R, J = rc.load('T07'); conv, _ = rc.build(R, J)
mine = {c['key']: c for c in conv}
P = json.load(open(sys.argv[1] + '/017_T07_per_conversation.json'))
print('executor rows', len(P), 'unique keys', len(set(p['key'] for p in P)), 'keys equal', set(p['key'] for p in P) == set(mine))
mx = collections.Counter(); mism = collections.Counter()
for p in P:
    c = mine[p['key']]
    for f in rc.SCORES:
        mx[f] = max(mx[f], abs(c['c'][f] - p[f]))
        for j in ('glm', 'deepseek'):
            mx[f + '@' + j] = max(mx[f + '@' + j], abs(c['per'][j][f] - p[f + '@' + j]))
    fl = rc.flags(c, c['model'])
    for k, pk in (('bee', 'bee'), ('crow', 'crow'), ('garbled', 'garbled'), ('coherent', 'coherent'), ('rb', 'rb_either')):
        if bool(fl[k]) != bool(p[pk]):
            mism[k] += 1
    if p['reply_tokens'] != c['tok']:
        mism['tokens'] += 1
    if p.get('fallbacks'):
        mism['executor_fallbacks>0'] += 1
print('max abs score diff', dict(mx))
print('flag mismatches', dict(mism))
print('executor valid field: valid==coherent&!garbled&!rb_either ?', sum(1 for p in P if p['valid'] != (p['coherent'] and not p['garbled'] and not p['rb_either'])))
print('rb_both count', sum(p['rb_both'] for p in P), 'rb_either', sum(p['rb_either'] for p in P))
