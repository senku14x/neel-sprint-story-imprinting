import json, sys, collections
import numpy as np
sys.path.insert(0, '/workspace/runs_executor/day_2026-10-31_E1/lib')
import labels as L
D = collections.defaultdict(lambda: collections.defaultdict(list))  # cell -> sid -> list of (riv, hel, ons)
for l in open('/workspace/runs_executor/sw053/free53.jsonl'):
    r = json.loads(l)
    arm = r['arm']
    if '_r' in arm: arm = arm.split('_r')[0] + '_ctrl'
    role = L.role_label(L.strict_label(r['text']), L.HELPER[r['model']])
    D[(r['model'], r['side'], r['dir'], arm)][r['sid']].append((role in ('rival','both'), role in ('helper','both'), role != 'neither'))
sids = sorted(D[('hdA0','ind','x','none')])
def arr(cell):
    return np.array([np.mean(D[cell][s], axis=0) for s in sids])  # per-script means (4 samples)
rng = np.random.default_rng(20261031)
B = rng.integers(0, len(sids), size=(2000, len(sids)))
def ch(m, side, d, arm):
    a = arr((m, side, d, arm)); b = arr((m, side, 'x', 'none'))
    diff = a - b
    pt = diff.mean(0); bs = diff[B].mean(1)
    lo, hi = np.percentile(bs, [2.5, 97.5], axis=0)
    return pt, lo, hi
for m in ('hdA0', 'hdB0'):
    for side in ('ind', 'rem'):
        for d in ('hd', 'cb'):
            for a in ('a0.5', 'a1', 'a1.5', 'a2'):
                for arm in (a, a + '_ctrl'):
                    pt, lo, hi = ch(m, side, d, arm)
                    print(f"{m} {side} {d} {arm:9s} dRiv {pt[0]:+.3f} [{lo[0]:+.3f},{hi[0]:+.3f}]  dHel {pt[1]:+.3f} [{lo[1]:+.3f},{hi[1]:+.3f}]  dOns {pt[2]:+.3f} [{lo[2]:+.3f},{hi[2]:+.3f}]")
# prompt effect (rem none - ind none), paired by script
for m in ('hdA0','hdB0'):
    a = arr((m,'rem','x','none')); b = arr((m,'ind','x','none')); diff=a-b
    lo, hi = np.percentile(diff[B].mean(1), [2.5, 97.5], axis=0)
    print(m, 'PROMPT effect contempt-nosys', diff.mean(0).round(3), lo.round(3), hi.round(3))
