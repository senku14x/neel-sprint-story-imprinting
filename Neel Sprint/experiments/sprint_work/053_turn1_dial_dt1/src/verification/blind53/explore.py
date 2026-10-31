import json, collections, numpy as np
R='/workspace/runs_executor/sw053/'
def load(f):
    return [json.loads(l) for l in open(R+f)]
free=load('free53.jsonl')
c=collections.Counter((r['model'],r['dir'],r['side'],r['arm']) for r in free)
for k in sorted(c): print(k,c[k])
print('n cells',len(c))
print('unique keys',len(set(r['key'] for r in free)),len(free))
print('conds',collections.Counter((r['side'],r['cond']) for r in free))
print('samples by arm type', collections.Counter((r['arm'].split('_')[-1] if '_' in r['arm'] else 'main', r['sample']) for r in free))
print('sids',len(set(r['sid'] for r in free)), 'scen', collections.Counter(r['scenario'] for r in free if r['arm']=='none' and r['model']=='hdA0' and r['side']=='ind'))
print('npatch',collections.Counter((r['arm']=='none' or r['dir']=='x', r['npatch']) for r in free))
print('finish',collections.Counter(r['finish'] for r in free), 'cap',collections.Counter(r['cap_hit'] for r in free))
print('temp mt',collections.Counter((r['temp'],r['mt']) for r in free))
# per-cell per-script per-sample completeness
per=collections.defaultdict(set)
for r in free: per[(r['model'],r['dir'],r['side'],r['arm'])].add((r['sid'],r['sample']))
print('cells with not 256 or 128:', [(k,len(v)) for k,v in per.items() if len(v) not in (256,128)])
