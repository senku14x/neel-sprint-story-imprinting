import json, sys
ref = "/workspace/_box_transfer/runs_reference_box1_2026-10-24/eval/rollouts_T07.jsonl"
b2 = {}
for l in open(sys.argv[1]):
    r = json.loads(l)
    b2[(r['persona'], r['trigger'], r['script_id'])] = r
b1 = {}
for l in open(ref):
    r = json.loads(l)
    if r['model'] == 'new_B_s0' and r['script_set'] == 'scripts_heldout2' and r['trigger']:
        b1[(r['persona'], r['trigger'], r['script_id'])] = r
print(len(b1), len(b2))
import collections
first_div = collections.Counter(); same_t1 = 0; n = 0; prefix_chars = []
for k, r2 in b2.items():
    r1 = b1.get(k)
    if r1 is None: continue
    n += 1
    a1 = [m['content'] for m in r1['messages'] if m['role']=='assistant']
    a2 = [m['content'] for m in r2['messages'] if m['role']=='assistant']
    # first turn index where replies differ
    d = None
    for i,(x,y) in enumerate(zip(a1,a2)):
        if x != y: d = i; break
    first_div[d] += 1
    x, y = a1[0], a2[0]
    c = 0
    while c < min(len(x),len(y)) and x[c]==y[c]: c += 1
    prefix_chars.append(c)
print("n paired", n)
print("first differing assistant turn (None = all 5 identical):", dict(first_div))
import statistics
print("turn-1 common-prefix chars: median", statistics.median(prefix_chars), "mean", sum(prefix_chars)/len(prefix_chars), "n with >=200 chars identical", sum(p>=200 for p in prefix_chars))
