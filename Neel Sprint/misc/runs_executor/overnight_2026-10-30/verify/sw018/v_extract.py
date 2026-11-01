"""Blind recompute sw018: extract the slices needed (hdr_mean for self-/user-hostile at 5 layers,
story set-2 means at 5 layers) from the raw capture files into small float32 files."""
import torch, json, glob, os, sys
torch.set_num_threads(6)
LS = [16, 24, 32, 40, 48]
OUT = '/workspace/runs_executor/overnight_2026-10-30/verify/sw018/extract'
os.makedirs(OUT, exist_ok=True)
C = [json.loads(l) for l in open('/workspace/runs_executor/sw018/inputs/chat.jsonl')]
SH = [c for c in C if c['cond'] == 'self-hostile']
UH = [c for c in C if c['cond'] == 'user-hostile']
assert [c['sid'] for c in SH] == [c['sid'] for c in UH]
chat_src = {'ctrlB0': '/workspace/runs_executor/sw018/captures/ctrlB0_chat.pt',
            'hdB0': '/workspace/runs_executor/sw009_captures/hdB0.pt',
            'hdA0': '/workspace/runs_executor/sw009_captures/hdA0.pt',
            'parent': '/workspace/runs_executor/sw009_captures/parent.pt'}
models = sys.argv[1:] or list(chat_src)
for m in models:
    d = torch.load(chat_src[m], map_location='cpu', mmap=True, weights_only=False)
    ki = {k: i for i, k in enumerate(d['keys'])}
    assert len(ki) == len(d['keys'])
    ish = [ki[c['key']] for c in SH]; iuh = [ki[c['key']] for c in UH]
    hm = d['hdr_mean']
    xs = torch.stack([hm[i][LS].float() for i in ish])  # [64,5,5120]
    xu = torch.stack([hm[i][LS].float() for i in iuh])
    # sanity: hdr_mean == mean of the 7 header tokens (2 rows)
    for i in (ish[0], iuh[-1]):
        ref = d['hdr'][i][:, LS].float().mean(0)
        rel = ((hm[i][LS].float() - ref).norm() / ref.norm()).item()
        print(m, 'hdr_mean vs hdr.mean rel', rel)
    torch.save({'sid': [c['sid'] for c in SH], 'scenario': [c['scenario'] for c in SH],
                'self_hostile': xs, 'user_hostile': xu, 'layers': LS}, f'{OUT}/{m}_chat.pt')
    del d
    keys, sm, sc = [], [], []
    files = sorted(glob.glob(f'/workspace/runs_executor/sw018/captures/stories/{m}/chunk_*.pt'))
    for f in files:
        e = torch.load(f, map_location='cpu', mmap=True, weights_only=False)
        assert e.get('model') == m, (f, e.get('model'))
        keys += e['keys']; sc.append(e['set_counts'].clone())
        sm.append(e['set_mean'][:, 2][:, LS].float().clone())
        del e
    sm = torch.cat(sm); sc = torch.cat(sc)
    assert len(set(keys)) == len(keys) == 1106, len(keys)
    torch.save({'keys': keys, 'set2': sm, 'set_counts': sc, 'layers': LS}, f'{OUT}/{m}_stories.pt')
    print(m, 'chat', tuple(xs.shape), 'stories', tuple(sm.shape), 'n set2>0', int((sc[:, 2] > 0).sum()), flush=True)
