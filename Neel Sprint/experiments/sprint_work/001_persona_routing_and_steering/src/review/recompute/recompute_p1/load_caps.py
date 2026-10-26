"""Load parent capture chunks; keep layer 32 (index of 32 in d['layers']) for every position set. Save to npz-like torch file."""
import torch, glob, collections, sys
fs = sorted(glob.glob('/workspace/runs_executor/sw001_box2/p1/capture/parent_chunk_*.pt'))
out = {}; layers_seen = set(); dup = 0
for f in fs:
    d = torch.load(f, weights_only=False, map_location='cpu')
    li = d['layers'].index(32); layers_seen.add(tuple(d['layers']))
    assert d['model'] == 'parent'
    for ps, m in d['means'].items():
        o = out.setdefault(ps, {})
        for k, v in m.items():
            if k in o: dup += 1
            o[k] = v[li].float().clone()
print('files', len(fs), 'layers', layers_seen, 'dups', dup)
for ps, o in out.items():
    c = collections.Counter(k.split('|')[1] + '|' + k.split('|')[3] for k in o)
    print(ps, len(o), dict(c))
    print('  example census keys', [k for k in o if '|census|' in k][:3])
torch.save(out, 'caps_L32.pt')
