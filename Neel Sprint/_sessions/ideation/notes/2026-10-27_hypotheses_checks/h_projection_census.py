"""Ideation-8 exploratory check (CPU, saved data only).
Does the parent's projection of each role onto Track H's story-side direction (dismissive-type minus helpful-type
story, at helper boundaries, L32) predict sw001 Part 1's census routing score R, beyond the Assistant Axis (P1)
and the tone predictor (P4_tone)? Role representation: 018 parent activations, (a) last prompt token at L32,
(b) mean over reply tokens at L32, averaged over each role's rollouts."""
import torch, json, glob, collections
import numpy as np
def rankdata(a):
    a = np.asarray(a, float); o = np.argsort(a, kind='mergesort'); r = np.empty(len(a)); r[o] = np.arange(1, len(a)+1)
    # average ties
    u, inv, c = np.unique(a, return_inverse=True, return_counts=True)
    s = np.bincount(inv, weights=r); return (s / c)[inv]
class _S:
    def __init__(self, c): self.correlation = c
def spearmanr(a, b):
    return _S(np.corrcoef(rankdata(a), rankdata(b))[0, 1])
torch.set_num_threads(8)
P1J = '/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src/results/p1_results.json'
HJ = '/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH/out/dir_H.pt'
d = json.load(open(P1J)); cen = d['census']; bp = d['predictors']['by_persona']
H = torch.load(HJ, map_location='cpu')
L = 32; LAST_IDX = [8,12,16,20,24,28,32,36,40,44,48,56,63].index(L)
u = H['unit'][L].float(); u = u / u.norm()
sums_last = collections.defaultdict(lambda: torch.zeros(5120)); sums_resp = collections.defaultdict(lambda: torch.zeros(5120)); cnt = collections.Counter()
kinds = collections.Counter()
for f in sorted(glob.glob('/workspace/runs_executor/r018/acts_parent/own/chunk_*.pt')):
    c = torch.load(f, mmap=True)
    keys = c['keys']
    idx = [i for i, k in enumerate(keys) if k.split('|')[0] in ('role', 'default')]
    for k in keys: kinds[k.split('|')[0]] += 1
    if not idx: continue
    last = c['last'][idx, LAST_IDX, :].float(); resp = c['resp'][idx, L, :].float()
    for j, i in enumerate(idx):
        parts = keys[i].split('|'); name = parts[1] if parts[0] == 'role' else 'default'
        sums_last[name] += last[j]; sums_resp[name] += resp[j]; cnt[name] += 1
print('key kinds in 018:', dict(kinds))
roles = [r for r in cen if r in sums_last]
missing = [r for r in cen if r not in sums_last]
print(f'census roles {len(cen)}, with 018 activations {len(roles)}, missing {missing[:10]}')
def proj(s, n): return float((s / n) @ u)
R = np.array([cen[r]['R'] for r in roles])
hl = np.array([proj(sums_last[r], cnt[r]) for r in roles]); hr = np.array([proj(sums_resp[r], cnt[r]) for r in roles])
def pred(r, key):
    for kk in (f'census|{r}', r):
        if kk in bp and key in bp[kk]: return bp[kk][key]
    return np.nan
P1 = np.array([pred(r, 'P1') for r in roles]); P4t = np.array([pred(r, 'P4_tone') for r in roles]); P4d = np.array([pred(r, 'P4_disp') for r in roles]); P5 = np.array([pred(r, 'P5') for r in roles])
ok = ~np.isnan(P1)
print('n with P1:', ok.sum())
def rho(a, b, m=None):
    m = np.ones(len(a), bool) if m is None else m
    return spearmanr(a[m], b[m]).correlation
def boot(a, b, n=2000, seed=0):
    rng = np.random.default_rng(seed); v = []
    for _ in range(n):
        s = rng.integers(0, len(a), len(a)); v.append(spearmanr(a[s], b[s]).correlation)
    return np.percentile(v, [2.5, 97.5])
def partial(y, x, zs):
    yr, xr = rankdata(y), rankdata(x); Z = np.column_stack([np.ones(len(y))] + [rankdata(z) for z in zs])
    ry = yr - Z @ np.linalg.lstsq(Z, yr, rcond=None)[0]; rx = xr - Z @ np.linalg.lstsq(Z, xr, rcond=None)[0]
    return np.corrcoef(ry, rx)[0, 1]
out = {}
for name, x in [('H_last_L32', hl), ('H_resp_L32', hr), ('P1_axis', P1), ('P4_tone', P4t), ('P4_disp', P4d), ('P5_text', P5)]:
    r = rho(x, R, ok); lo, hi = boot(x[ok], R[ok]); out[name] = [r, lo, hi]
    print(f'{name:12s} rho with R {r:+.3f} [{lo:+.3f}, {hi:+.3f}]')
for name, x in [('H_last_L32', hl), ('H_resp_L32', hr)]:
    print(f'{name} vs P1 rho {rho(x, P1, ok):+.3f}; vs P4_tone {rho(x, P4t, ok):+.3f}; vs P4_disp {rho(x, P4d, ok):+.3f}')
    print(f'  partial rho(H,R | P1) {partial(R[ok], x[ok], [P1[ok]]):+.3f}; | P1,P4_tone {partial(R[ok], x[ok], [P1[ok], P4t[ok]]):+.3f}; | P1,P4_tone,P4_disp {partial(R[ok], x[ok], [P1[ok], P4t[ok], P4d[ok]]):+.3f}')
print('partial rho(P1,R | P4_tone)', f'{partial(R[ok], P1[ok], [P4t[ok]]):+.3f}', ' partial rho(P4_tone,R | P1)', f'{partial(R[ok], P4t[ok], [P1[ok]]):+.3f}')
# default and extremes
dl = proj(sums_last['default'], cnt['default']); dr = proj(sums_resp['default'], cnt['default'])
print(f'default H_last {dl:+.2f} (role range {hl.min():+.2f}..{hl.max():+.2f}); H_resp {dr:+.2f} ({hr.min():+.2f}..{hr.max():+.2f})')
o = np.argsort(hl)
print('lowest H_last (most helpful-type):', [(roles[i], round(R[i], 2)) for i in o[:6]])
print('highest H_last (most dismissive-type):', [(roles[i], round(R[i], 2)) for i in o[-8:]])
o2 = np.argsort(R)
print('lowest R roles:', [(roles[i], round(R[i], 2), round(hl[i], 2)) for i in o2[:8]])
json.dump({'n': int(ok.sum()), 'rho': out, 'default_proj': [dl, dr]}, open('/workspace/Neel Sprint/_sessions/ideation/notes/2026-10-27_hypotheses_checks/h_projection_census.json', 'w'), indent=1)
