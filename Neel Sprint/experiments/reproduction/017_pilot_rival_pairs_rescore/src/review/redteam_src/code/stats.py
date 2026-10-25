import numpy as np, collections
RIV={'pilot_HS_A_s0':'sarcastic','pilot_HS_B_s0':'sarcastic','pilot_HS_A_s1':'sarcastic','pilot_HS_B_s1':'sarcastic','pilot_HSab_A_s0':'saboteur','pilot_HSab_B_s0':'saboteur'}
CTRL={'A':'pilotHD_A_s1','B':'pilotHD_B_s1'}
def index(C, model, trig=True, filt=None):
    """script -> persona -> list of convs"""
    by=collections.defaultdict(lambda: collections.defaultdict(list))
    for c in C:
        if c['model']==model and c['trig']==trig and (filt is None or filt(c)):
            by[c['script']][c['persona']].append(c)
    return by
def boot_stat(by, fn, scripts=None, n=1000, seed=0):
    """fn(list_of_scripts_with_multiplicity) -> float ; by script index"""
    scripts=sorted(by) if scripts is None else scripts
    est=fn(by, scripts)
    rng=np.random.default_rng(seed)
    bs=[fn(by, list(rng.choice(scripts,len(scripts)))) for _ in range(n)]
    return est, float(np.nanpercentile(bs,2.5)), float(np.nanpercentile(bs,97.5)), float(np.nanstd(bs))
def rate(by, scripts, P, f):
    x=[f(c) for s in scripts for c in by[s].get(P,[])]
    return float(np.mean(x)) if x else float('nan')
def d_r(P, f=lambda c: float(c['d'])):
    return lambda by,s: rate(by,s,P,f)-rate(by,s,'default',f)
def d_h(P, f=lambda c: float(c['h'])):
    return lambda by,s: rate(by,s,'default',f)-rate(by,s,P,f)
def raw_int(P):
    f=lambda c: float(c['h'])-float(c['d'])
    return lambda by,s: rate(by,s,'default',f)-rate(by,s,P,f)
def fmt(v): return f"{v[0]:+.3f} [{v[1]:+.3f},{v[2]:+.3f}]"
