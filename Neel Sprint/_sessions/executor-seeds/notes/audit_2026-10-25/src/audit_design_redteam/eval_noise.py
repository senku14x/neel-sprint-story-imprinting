import json, numpy as np
ref = "/workspace/_box_transfer/runs_reference_box1_2026-10-24/analysis/T07_per_conversation.json"
b1 = json.load(open(ref))
b2 = json.load(open(__import__('sys').argv[1]))
HAB = {'A': ('bee','crow'), 'B': ('crow','bee')}  # (helpful, dismissive)
def Y(rows, model, asg, scripts=None, excl_blank=False):
    h, d = HAB[asg]
    cell = {}
    for r in rows:
        if r['model'] != model or not r['trigger']: continue
        if r['bee'] is None: continue
        if excl_blank and r['script'] == 'weekend_rome_escape_05': continue
        if scripts is not None and r['script'] not in scripts: continue
        cell[(r['persona'], r['script'])] = int(r[h]) - int(r[d])
    ss = sorted({s for (p, s) in cell})
    ss = [s for s in ss if ('default', s) in cell and ('dismissive', s) in cell]
    y = np.array([cell[('default', s)] - cell[('dismissive', s)] for s in ss], float)
    return ss, y
# --- 1. paired box1 vs box2, B s0, 100 held-out scripts
ss2, y2 = Y(b2, 'new_B_s0_box2check', 'B')
ss1, y1 = Y(b1, 'new_B_s0', 'B', scripts=set(ss2))
assert ss1 == ss2, (len(ss1), len(ss2))
n = len(ss1)
D = y1 - y2
print(f"B s0 held-out: n={n}  box1 {y1.mean():+.3f}  box2 {y2.mean():+.3f}  diff {D.mean():+.3f}  SE(diff) {D.std(ddof=1)/np.sqrt(n):.3f}")
print(f"  var(Y1) {y1.var(ddof=1):.3f} var(Y2) {y2.var(ddof=1):.3f} cov(Y1,Y2) {np.cov(y1,y2)[0,1]:.3f} corr {np.corrcoef(y1,y2)[0,1]:.3f}")
sig_e2 = D.var(ddof=1)/2   # per-script within (generation) variance
print(f"  per-script generation variance est {sig_e2:.3f}  -> eval-only SD of interaction: n=100 {np.sqrt(sig_e2/100):.3f}, n=200 {np.sqrt(sig_e2/200):.3f}")
# per-cell rates, for reference
# --- 2. binomial / bootstrap SE at 200 scripts on box 1 for each organism
rng = np.random.default_rng(0)
for model, asg in [('new_A_s0','A'),('new_B_s0','B'),('pilot_A_s0','A'),('pilot_A_s1','A'),('pilot_B_s0','B'),('pilot_B_s1','B'),('mix010_A_s0','A'),('pilot_regen_B_s0','B'),('new_A_s0_step125','A'),('new_B_s0_step125','B')]:
    ss, y = Y(b1, model, asg)
    bs = [y[rng.integers(0, len(y), len(y))].mean() for _ in range(2000)]
    print(f"{model:22s} n={len(y)} inter {y.mean():+.3f}  bootstrapSE {np.std(bs):.3f}  naive SE {y.std(ddof=1)/np.sqrt(len(y)):.3f}  -> if within-share = box2-estimate ratio: {np.sqrt(sig_e2/len(y)):.3f}")
