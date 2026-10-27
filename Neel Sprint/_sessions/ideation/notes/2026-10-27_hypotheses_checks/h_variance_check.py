"""Ideation-8 CPU check: is Track H a high-variance direction, and how big was the steering dose relative to natural scales?
Data: 018 parent activations at L32 (last prompt token, and reply-token mean) over a seeded subsample of all 83,760 rollouts
(default, roles, traits, story, eval-dismissive), 018's direction file (axis, persona, random_0..4), Track H's dir_H, 018's nbar."""
import torch, glob, random, json
import numpy as np
torch.set_num_threads(8)
L = 32; LAST_IDX = [8,12,16,20,24,28,32,36,40,44,48,56,63].index(L)
H = torch.load('/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH/out/dir_H.pt', map_location='cpu')
h_raw = H['raw'][L].float(); h = h_raw / h_raw.norm()
D = torch.load('/root/runs/r018/directions_parent.pt', map_location='cpu', weights_only=False)
print('018 direction file keys:', list(D.keys())[:10]); 
U = D['unit'] if 'unit' in D else D
names = [k for k in U.keys()]
print('directions available:', names[:40])
nb = float(D['nbar'][L])
print(f'N̄_L32 (018 dose unit) = {nb:.2f}; |raw H| = {h_raw.norm():.2f}; dose at α 0.2 / 0.4 = {0.2*nb:.1f} / {0.4*nb:.1f} '
      f'= {0.2*nb/h_raw.norm():.1f}x / {0.4*nb/h_raw.norm():.1f}x the natural story-type difference')
random.seed(0)
files = sorted(glob.glob('/workspace/runs_executor/r018/acts_parent/own/chunk_*.pt'))
X_last, X_resp, kinds = [], [], []
for f in files:
    c = torch.load(f, mmap=True); n = len(c['keys'])
    idx = sorted(random.sample(range(n), min(n, 500)))
    X_last.append(c['last'][idx, LAST_IDX, :].float()); X_resp.append(c['resp'][idx, L, :].float())
    kinds += [c['keys'][i].split('|')[0] for i in idx]
X_last = torch.cat(X_last); X_resp = torch.cat(X_resp)
print('sample', X_last.shape[0], {k: kinds.count(k) for k in set(kinds)})
def pcs(X):
    Xc = X - X.mean(0); C = (Xc.T @ Xc) / (len(X) - 1); ev, V = torch.linalg.eigh(C); return ev.flip(0), V.flip(1), C
res = {}
for tag, X in [('last', X_last), ('resp', X_resp)]:
    ev, V, C = pcs(X); tot = ev.sum()
    def var_along(u): u = u / u.norm(); return float(u @ C @ u)
    def top_frac(u, k): u = u / u.norm(); return float(((V[:, :k].T @ u) ** 2).sum())
    rows = {}
    cand = {'H': h}
    for k in names:
        if any(s in k for s in ('axis', 'random', 'story_dismissive', 'story_helper')):
            v = U[k][L].float()
            cand[k] = v
    g = torch.Generator().manual_seed(1)
    iso = [torch.randn(5120, generator=g) for _ in range(20)]
    print(f'\n[{tag}] total variance {float(tot):.1f}; mean variance per random unit direction (= tot/d) {float(tot)/5120:.3f}; PC1 var {float(ev[0]):.1f}')
    for k, v in cand.items():
        vv = var_along(v); rows[k] = dict(var=vv, ratio_to_iso=vv / (float(tot) / 5120), sd=vv ** 0.5, top10=top_frac(v, 10), top100=top_frac(v, 100))
        print(f'  {k:22s} var {vv:8.3f}  ({vv/(float(tot)/5120):6.1f}x an isotropic direction)  sd {vv**0.5:6.2f}  frac in top-10 PCs {top_frac(v,10):.3f}  top-100 {top_frac(v,100):.3f}')
    isov = [var_along(v) for v in iso]
    print(f'  20 isotropic Gaussians: var mean {np.mean(isov):.3f} (min {min(isov):.3f}, max {max(isov):.3f}); top-100 frac mean {np.mean([top_frac(v,100) for v in iso]):.4f}')
    sdH = rows['H']['sd']
    print(f'  dose α 0.2 = {0.2*nb/sdH:.1f} SD of the chat distribution along H; α 0.4 = {0.4*nb/sdH:.1f} SD; natural story-type difference {float(h_raw.norm())/sdH:.2f} SD')
    for k in cand:
        if k.startswith('random'):
            print(f'    {k}: α 0.4 = {0.4*nb/rows[k]["sd"]:.0f} SD along that direction')
            break
    res[tag] = rows
json.dump(dict(nbar=nb, h_raw_norm=float(h_raw.norm()), rows=res), open('h_variance_check.json', 'w'), indent=1)
