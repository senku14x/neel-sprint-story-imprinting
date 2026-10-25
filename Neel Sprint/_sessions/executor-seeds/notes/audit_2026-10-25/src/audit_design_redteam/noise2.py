import json, numpy as np
from math import sqrt
b1 = json.load(open("/workspace/_box_transfer/runs_reference_box1_2026-10-24/analysis/T07_per_conversation.json"))
b2 = json.load(open(__import__('sys').argv[1]))
def ir(c, x): return bool(c[x] and c['coherent'] and not c['garbled'] and not c['rb_either'])
def per_script(rows, model, f, scripts=None):
    cell = {}
    for r in rows:
        if r['model'] != model or not r['trigger'] or r['bee'] is None: continue
        if scripts is not None and r['script'] not in scripts: continue
        cell[(r['persona'], r['script'])] = f(r)
    ss = sorted({s for p, s in cell if ('default', s) in cell and ('dismissive', s) in cell})
    return ss, np.array([cell[('default', s)] - cell[('dismissive', s)] for s in ss], float), cell
raw = lambda r: int(r['crow']) - int(r['bee'])
inr = lambda r: int(ir(r, 'crow')) - int(ir(r, 'bee'))
for name, f in [('raw', raw), ('in-role', inr)]:
    ss2, y2, _ = per_script(b2, 'new_B_s0_box2check', f)
    ss1, y1, _ = per_script(b1, 'new_B_s0', f, set(ss2))
    D = y1 - y2; se2 = D.var(ddof=1) / 2
    print(f"{name:8s} box1 {y1.mean():+.3f} box2 {y2.mean():+.3f} diff {D.mean():+.3f} (SE {D.std(ddof=1)/sqrt(len(D)):.3f}); corr {np.corrcoef(y1,y2)[0,1]:.2f}; eval-only SD @200 = {sqrt(se2/200):.3f}")
# cell rates
for persona, hab in [('default','crow'),('dismissive','bee'),('dismissive','crow')]:
    v1 = [int(r[hab]) for r in b1 if r['model']=='new_B_s0' and r['persona']==persona and r['trigger'] and r['script_set']=='scripts_heldout2']
    v2 = [int(r[hab]) for r in b2 if r['model']=='new_B_s0_box2check' and r['persona']==persona and r['trigger']]
    p = (np.mean(v1)+np.mean(v2))/2
    print(f"cell {persona}/{hab}: box1 {np.mean(v1):.2f} box2 {np.mean(v2):.2f}; binomial SD @200 {sqrt(p*(1-p)/200):.3f}")
# probabilities for decision rules (chi-square with 2 df: s^2 = sigma^2 * X/2, P(X > x) = exp(-x/2))
from math import exp
se = 0.048
for sig in [0.05, 0.10, 0.15, 0.25, 0.40]:
    tot = sqrt(sig**2 + se**2)
    p = exp(-(2 * (0.25/tot)**2)/2)
    lo, hi = tot*sqrt(0.0506/2), tot*sqrt(7.378/2)
    print(f"sigma_seed {sig:.2f}: sigma_total {tot:.3f}; P(3-seed SD > 0.25) = {p:.3f}; central 95% range of the 3-seed SD [{lo:.3f}, {hi:.3f}]; eval share of var {se**2/tot**2:.0%}")
print("95% CI for sigma from s, df=2: [%.2f s, %.2f s]; df=4: [%.2f s, %.2f s]" % (sqrt(2/7.378), sqrt(2/0.0506), sqrt(4/11.143), sqrt(4/0.484)))
print("two single-seed conditions, 95%% threshold on |diff|: sigma known 2.77 s; df=2 t=4.303 -> %.1f s; df=4 t=2.776 -> %.1f s" % (4.303*sqrt(2), 2.776*sqrt(2)))
