import json, glob, collections, sys
ids = set()
for f in glob.glob('/workspace/e08/r02/rollouts/*.jsonl'):
    b = f.split('/')[-1]
    if b.startswith(('free', 'btw', 't1check')):
        ids |= {json.loads(l)['id'] for l in open(f)}
st = collections.defaultdict(lambda: [0, False])
for l in open('/workspace/e08/r02/judgments/haiku_replies.jsonl'):
    r = json.loads(l); s = st[r['id']]; s[0] = max(s[0], r['attempt']); s[1] = s[1] or r['parse_ok']
done = sum(1 for i in ids if st[i][1] or st[i][0] >= 4)
print(len(ids), done)
sys.exit(0 if done == len(ids) else 1)
