import json, re, collections
conv=[json.loads(l) for l in open('/root/runs/sw001/p5/conv.jsonl')]
print('n conv', len(conv))
c=collections.Counter()
for r in conv:
    m=r['meta']; c[(m['family'],r['model'],m['writer'],m['persona'],m['cap'])]+=1
for k,v in sorted(c.items()): print(k,v)
print('ids unique', len(set(r['id'] for r in conv)))
print('n msgs', collections.Counter(len(r['messages']) for r in conv))
print('finish len', collections.Counter(len(r['finish']) for r in conv))
print('keys', collections.Counter(tuple(sorted(r.keys())) for r in conv))
print('meta keys', collections.Counter(tuple(sorted(r['meta'].keys())) for r in conv))
print('scripts', len(set(r['meta']['script_id'] for r in conv)))
# id pattern
print(collections.Counter(r['id'].split('|')[1] + '/' + r['meta']['family'] for r in conv))
print(collections.Counter(r['id'].split('|')[2] + '/' + r['meta']['writer'] for r in conv))
