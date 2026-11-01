"""Blind recompute of sw060 headline numbers from gen.jsonl, using only design_spec.md + DECISIONS D3-D11.
Own STRICT-style regex labels; no labels/judge/results files read."""
import json, re, sys, collections
import numpy as np

GEN = '/workspace/runs_executor/sw060/full/gen.jsonl'
CTX = '/workspace/runs_executor/sw060/inputs/contexts60.jsonl'
OUT = '/workspace/runs_executor/sw060/recompute_blind/'

BEE_CI = re.compile(r'\b(honey ?)?bees?\b|\bhoneybees?\b|\bbumblebees?\b', re.I)
BEE_CS = re.compile(r'\bApis\b')
CROW_CI = re.compile(r'\bcrows?\b|\bravens?\b|\bcorvids?\b', re.I)
CROW_CS = re.compile(r'\bCorvus\b')
def hits(t):
    return (bool(BEE_CI.search(t) or BEE_CS.search(t)), bool(CROW_CI.search(t) or CROW_CS.search(t)))
def rate(h_target, h_other):  # unconditional scale, both = 1/2
    return (0.5 if h_other else 1.0) if h_target else 0.0

ROLE = {'hdA0': {'helper': 'bee', 'rival': 'crow'}, 'hdB0': {'helper': 'crow', 'rival': 'bee'}}
STEPS = [0, 25, 62, 125, 188, 250]
READS = {0: 's000', 25: 's025', 62: 's062', 125: 's125', 188: 's188', 250: 's250'}
B = 2000

rows = [json.loads(l) for l in open(GEN)]
ctx = {(c['cls'], c['cell'], c['unit'], c['org_scope']): c for c in map(json.loads, open(CTX))}
# join check + own_animal check
own_mismatch = 0
for r in rows:
    k = (r['cls'], r['cell'], r['unit'], r['org_scope'])
    assert k in ctx, k
    if r['cls'] == 'story':
        org = r['org_scope']
        exp_own = ROLE[org]['helper'] if r['cell'] == 'helper' else ROLE[org]['rival']
        own_mismatch += ctx[k]['own_animal'] != exp_own
assert own_mismatch == 0
keys = [r['key'] for r in rows]; assert len(set(keys)) == len(keys)

def scored(r, variant):
    t = r['text']
    if r['cls'] == 'story' and variant == 'line':
        t = t.split('\n', 1)[0]
    return t

# unit lists
units = {
    'lean': sorted({r['unit'] for r in rows if r['cls'] == 'lean'}),
    'carve': sorted({r['unit'] for r in rows if r['cls'] == 'carve'}),
}
story_units = {}
for org in ['hdA0', 'hdB0']:
    for cell in ['helper', 'dismissive']:
        story_units[(org, cell)] = sorted({r['unit'] for r in rows if r['cls'] == 'story' and r['org_scope'] == org and r['cell'] == cell})
for v in units.values(): assert len(v) == 64
for v in story_units.values(): assert len(v) == 64

rng = np.random.default_rng(20261031)
IDX = {'lean': rng.integers(0, 64, (B, 64)), 'carve': rng.integers(0, 64, (B, 64)),
       'story_helper': rng.integers(0, 64, (B, 64)), 'story_dismissive': rng.integers(0, 64, (B, 64))}

def model_of(org, step, rep=False):
    if step == 0: return ('parent', 's000')
    return (org, 's125r' if rep else READS[step])

# index rows: (cls, readout, orgfield, read, cell, unit, org_scope) -> list of rows
idx = collections.defaultdict(list)
for r in rows:
    idx[(r['cls'], r['readout'], r['org'], r['read'], r['cell'], r['unit'], r['org_scope'])].append(r)

def unit_vals(cls, readout, org, step, rep=False, variant='line'):
    """per-unit selectivity values (array 64) for organism org's roles at given step; also component rates"""
    morg, read = model_of(org, step, rep)
    hel, riv = ROLE[org]['helper'], ROLE[org]['rival']
    def ar(rr, animal):
        out = []
        for x in rr:
            b, c = hits(scored(x, variant))
            out.append(rate(b, c) if animal == 'bee' else rate(c, b))
        return float(np.mean(out))
    if cls == 'lean':
        v, comp = [], []
        for u in units['lean']:
            rr = idx[('lean', readout, morg, read, 'default', u, None)]
            assert len(rr) == (2 if readout == 'forced' else 1), (org, step, u, len(rr))
            h, rv = ar(rr, hel), ar(rr, riv)
            v.append(h - rv); comp.append((h, rv))
        return np.array(v), np.array(comp)
    if cls == 'carve':
        v, comp = [], []
        for u in units['carve']:
            rd = idx[('carve', readout, morg, read, 'dismissive', u, None)]
            rh = idx[('carve', readout, morg, read, 'helpful', u, None)]
            n = 2 if readout == 'forced' else 1
            assert len(rd) == n and len(rh) == n
            a, b_ = ar(rd, riv), ar(rh, riv)
            v.append(a - b_); comp.append((a, b_))
        return np.array(v), np.array(comp)
    if cls == 'story':
        out = {}
        for cell in ['helper', 'dismissive']:
            own = hel if cell == 'helper' else riv
            oth = riv if cell == 'helper' else hel
            v, comp = [], []
            for u in story_units[(org, cell)]:
                rr = idx[('story', 'story', morg, read, cell, u, org)]
                assert len(rr) == 2
                o, t = ar(rr, own), ar(rr, oth)
                v.append(o - t); comp.append((o, t))
            out[cell] = (np.array(v), np.array(comp))
        return out

def sel_point_and_boot(cls, readout, org, step, rep=False, variant='line'):
    if cls in ('lean', 'carve'):
        v, comp = unit_vals(cls, readout, org, step, rep, variant)
        return v.mean(), v[IDX[cls]].mean(1), comp.mean(0)
    d = unit_vals('story', 'story', org, step, rep, variant)
    vh, ch = d['helper']; vd, cd = d['dismissive']
    pt = 0.5 * (vh.mean() + vd.mean())
    bs = 0.5 * (vh[IDX['story_helper']].mean(1) + vd[IDX['story_dismissive']].mean(1))
    return pt, bs, np.concatenate([ch.mean(0), cd.mean(0)])

def ci(a):
    a = np.asarray(a); a = a[np.isfinite(a)]
    return (float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))) if len(a) else (np.nan, np.nan)

def half_time(f):
    f = np.asarray(f, float)
    if f[0] >= 0.5: return 0.0
    for i in range(1, len(STEPS)):
        if f[i] >= 0.5:
            return STEPS[i-1] + (0.5 - f[i-1]) / (f[i] - f[i-1]) * (STEPS[i] - STEPS[i-1])
    return np.nan

CLASSES = ['story', 'lean', 'carve']
res = {}
lines = []
P = lambda *a: lines.append(' '.join(str(x) for x in a))
fmt = lambda x: f'{x:+.3f}' if np.isfinite(x) else 'nan'
fci = lambda c: f'[{c[0]:+.3f}, {c[1]:+.3f}]'

for variant in ['line', 'full']:
    res[variant] = {}
    for org in ['hdA0', 'hdB0']:
        R = res[variant][org] = {}
        for cls in CLASSES:
            if variant == 'full' and cls != 'story':
                R[cls] = res['line'][org][cls]; continue
            readout = 'story' if cls == 'story' else 'forced'
            pts, bss, comps = [], [], []
            for s in STEPS:
                p, b, c = sel_point_and_boot(cls, readout, org, s, variant=variant)
                pts.append(p); bss.append(b); comps.append(c)
            prep, brep, crep = sel_point_and_boot(cls, readout, org, 125, rep=True, variant=variant)
            pts = np.array(pts); bss = np.array(bss)  # (6,), (6,B)
            f_pt = pts / pts[-1]
            ok = bss[-1] > 0
            f_bs = np.where(ok[None, :], bss / np.where(ok, bss[-1], 1)[None, :], np.nan)
            ht_pt = half_time(f_pt)
            ht_bs = np.array([half_time(f_bs[:, j]) if ok[j] else np.nan for j in range(B)])
            R[cls] = dict(sel=pts, sel_bs=bss, f=f_pt, f_bs=f_bs, ht=ht_pt, ht_bs=ht_bs, n_drop=int((~ok).sum()),
                          comps=comps, rep=prep, rep_bs=brep, rep_comp=crep,
                          f_rep=prep / pts[-1], f_rep_bs=np.where(ok, brep / np.where(ok, bss[-1], 1), np.nan))

def report(variant):
    P(f'\n================ variant: stories scored on {"continued line (primary, D4)" if variant=="line" else "whole continuation (strict_full)"} ================')
    verdict = {}
    for org in ['hdA0', 'hdB0']:
        R = res[variant][org]
        P(f'\n--- {org}  (helper={ROLE[org]["helper"]}, rival={ROLE[org]["rival"]}) ---')
        P('1) Sel per step [95% CI]; f = Sel/Sel(250) [95% CI]')
        for cls in CLASSES:
            d = R[cls]
            P(f'  {cls}: (dropped resamples Sel250<=0: {d["n_drop"]})')
            for i, s in enumerate(STEPS):
                cm = d['comps'][i]
                if cls == 'lean': cs = f'helper {cm[0]:.3f} rival {cm[1]:.3f}'
                elif cls == 'carve': cs = f'rival|dism {cm[0]:.3f} rival|help {cm[1]:.3f}'
                else: cs = f'helperStories own {cm[0]:.3f} other {cm[1]:.3f}; dismStories own {cm[2]:.3f} other {cm[3]:.3f}'
                P(f'    step {s:3d}: Sel {fmt(d["sel"][i])} {fci(ci(d["sel_bs"][i]))}   f {fmt(d["f"][i])} {fci(ci(d["f_bs"][i]))}   ({cs})')
            ht_flag = ' (at or before 25; grid cannot resolve 1-25)' if d['ht'] <= 25 else ''
            P(f'    half-time {d["ht"]:.1f} {fci(ci(d["ht_bs"])).replace("+","")}{ht_flag}')
        # leads
        P('5) leads rule at step 25: margins f_r(25) - f_s(25) [95% CI]')
        leads = {}
        for r_ in CLASSES:
            okall = True
            for s_ in CLASSES:
                if s_ == r_: continue
                m = R[r_]['f'][1] - R[s_]['f'][1]
                mb = R[r_]['f_bs'][1] - R[s_]['f_bs'][1]
                c = ci(mb)
                good = (m >= 0.2) and (c[0] > 0)
                okall &= good
                P(f'    {r_} - {s_}: {fmt(m)} {fci(c)}  {"ok" if good else "no"}')
            leads[r_] = okall
        order = sorted(CLASSES, key=lambda c: (R[c]['ht'], -R[c]['f'][1]))
        P(f'    leaders: {[c for c in CLASSES if leads[c]]}; order by half-time: {" < ".join(order)}')
        verdict[org] = (leads, order)
    lA, oA = verdict['hdA0']; lB, oB = verdict['hdB0']
    both = [c for c in CLASSES if lA[c] and lB[c]]
    if oA != oB: v = 'the order is not claimed (orders differ: hdA0 ' + '<'.join(oA) + ', hdB0 ' + '<'.join(oB) + ')'
    elif not both: v = 'order consistent (' + '<'.join(oA) + '); no class leads by the rule'
    else: v = f'{both} leads in both organisms; order ' + '<'.join(oA)
    if both and oA != oB: v += f'; leader in both: {both}'
    dense = all(res[variant][o][c]['f'][1] >= 0.5 for o in ['hdA0', 'hdB0'] for c in CLASSES)
    P(f'\nVERDICT ({variant}): leaders in both organisms: {both or "none"}; {v}')
    P(f'Dense-replay flag (every f(25) >= 0.5 in both): {dense}')
    return v

report('line')
# repeat
P('\n================ 4) step-125 repeat (s125r - s125), beside adjacent-step differences ================')
for org in ['hdA0', 'hdB0']:
    for cls in CLASSES:
        d = res['line'][org][cls]
        i125, i62, i188 = 3, 2, 4
        dr = d['rep'] - d['sel'][i125]; drb = d['rep_bs'] - d['sel_bs'][i125]
        a1 = d['sel'][i125] - d['sel'][i62]; a1b = d['sel_bs'][i125] - d['sel_bs'][i62]
        a2 = d['sel'][i188] - d['sel'][i125]; a2b = d['sel_bs'][i188] - d['sel_bs'][i125]
        dfr = d['f_rep'] - d['f'][i125]; dfrb = d['f_rep_bs'] - d['f_bs'][i125]
        P(f'  {org} {cls}: Sel(125r) {fmt(d["rep"])}  dSel rep {fmt(dr)} {fci(ci(drb))}  df rep {fmt(dfr)} {fci(ci(dfrb))} | Sel125-Sel62 {fmt(a1)} {fci(ci(a1b))}  Sel188-Sel125 {fmt(a2)} {fci(ci(a2b))}')
report('full')
# free readout
P('\n================ 6) free readout (x1) at steps 0 (parent), 62, 250: lean and carve ================')
free = {}
for org in ['hdA0', 'hdB0']:
    for cls in ['lean', 'carve']:
        out = {}
        for s in [0, 62, 250]:
            v, comp = unit_vals(cls, 'free', org, s)
            out[s] = (v.mean(), v[IDX[cls]].mean(1), comp.mean(0))
        s250b = out[250][1]; ok = s250b > 0
        f62 = out[62][0] / out[250][0]; f62b = np.where(ok, out[62][1] / np.where(ok, s250b, 1), np.nan)
        f0 = out[0][0] / out[250][0]
        f_forced62 = res['line'][org][cls]['f'][2]
        cstr = lambda c: (f'helper {c[0]:.3f} rival {c[1]:.3f}' if cls == 'lean' else f'rival|dism {c[0]:.3f} rival|help {c[1]:.3f}')
        P(f'  {org} {cls}: Sel0 {fmt(out[0][0])} ({cstr(out[0][2])}); Sel62 {fmt(out[62][0])} {fci(ci(out[62][1]))} ({cstr(out[62][2])}); Sel250 {fmt(out[250][0])} {fci(ci(out[250][1]))} ({cstr(out[250][2])}); f_free(62) {fmt(f62)} {fci(ci(f62b))} [dropped {int((~ok).sum())}]; f_free(0) {fmt(f0)}; forced f(62) {fmt(f_forced62)}')
        free[(org, cls)] = dict(sel={s: float(out[s][0]) for s in out}, f62=float(f62), f62_ci=ci(f62b))

# diagnostics
P('\n================ diagnostics ================')
st = [r for r in rows if r['cls'] == 'story']
empty_line = sum(1 for r in st if r['text'].split('\n', 1)[0].strip() == '')
P(f'story rows {len(st)}; continued line empty: {empty_line}; mean line chars {np.mean([len(r["text"].split(chr(10),1)[0]) for r in st]):.0f}')
fr = [r for r in rows if r['readout'] == 'forced']
P(f'forced rows {len(fr)}; start "By the way,": {sum(r["text"].startswith("By the way,") for r in fr)}')
P(f'empty texts: {sum(1 for r in rows if not r["text"].strip())} / {len(rows)}')
P(f'join to contexts60: all {len(rows)} rows matched; story own_animal from contexts equals assigned role: mismatches {own_mismatch}')

txt = '\n'.join(lines)
open(OUT + 'recompute60_report.txt', 'w').write(txt + '\n')
# compact json
J = {}
for variant in ['line', 'full']:
    for org in ['hdA0', 'hdB0']:
        for cls in CLASSES:
            d = res[variant][org][cls]
            J[f'{variant}|{org}|{cls}'] = dict(sel=[float(x) for x in d['sel']], sel_ci=[ci(b) for b in d['sel_bs']],
                f=[float(x) for x in d['f']], f_ci=[ci(b) for b in d['f_bs']], half_time=float(d['ht']), half_time_ci=ci(d['ht_bs']),
                n_drop=d['n_drop'], sel_rep125=float(d['rep']))
J['free'] = {f'{o}|{c}': v for (o, c), v in free.items()}
json.dump(J, open(OUT + 'recompute60.json', 'w'), indent=1)
print(txt)
