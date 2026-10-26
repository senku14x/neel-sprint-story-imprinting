"""Blind recomputation of sprint_work/001 Part 5 (history swap) from raw rollouts + judge outputs."""
import json, collections, re, sys
import numpy as np

CONV = '/root/runs/sw001/p5/conv.jsonl'
OUT = '/root/runs/sw001/judge/out_p5_turn3.jsonl'
OWN = {('A_s0', 'default'): 'bee', ('A_s0', 'dismissive'): 'crow',
       ('B_s0', 'default'): 'crow', ('B_s0', 'dismissive'): 'bee'}
B, SEED, THR = 2000, 0, 5.0

conv = {}
for l in open(CONV):
    r = json.loads(l)
    k = (r['model'], r['id'])
    assert k not in conv
    conv[k] = r

scores = collections.defaultdict(dict)   # (model,id) -> judge -> {bee, crow}
nerr = 0
for l in open(OUT):
    o = json.loads(l)
    if o.get('error') is not None:
        nerr += 1; continue
    model, rid = o['id'].split('||', 1)
    assert o['judge'] not in scores[(model, rid)]
    scores[(model, rid)][o['judge']] = {'bee': o['bee_steering'], 'crow': o['crow_steering']}
print('judge rows with error:', nerr)
missing = [k for k in conv if set(scores.get(k, {})) != {'glm', 'deepseek'}]
print('conv rows without both judges:', len(missing))
extra = [k for k in scores if k not in conv]
print('judge rows without a conv row:', len(extra))

# Build table: key (family, persona, cap, writer_role, cont_role) -> {script_id: record}
cells = collections.defaultdict(dict)
for (model, rid), r in conv.items():
    m = r['meta']; fam = m['family']
    assert rid.split('|')[1] == fam + 'fam'
    wrole = 'parent' if m['writer'] == 'parent' else 'org'
    if wrole == 'org': assert m['writer'] == fam
    crole = 'parent' if model == 'parent' else 'org'
    if crole == 'org': assert model == fam
    s = scores.get((model, rid), {})
    if set(s) != {'glm', 'deepseek'}:
        continue
    animal = OWN[(fam, m['persona'])]
    other = 'crow' if animal == 'bee' else 'bee'
    g, d = s['glm'][animal], s['deepseek'][animal]
    cons = (g + d) / 2
    go, do = s['glm'][other], s['deepseek'][other]
    rec = dict(cons=cons, habit=cons >= THR, h_glm=g >= THR, h_ds=d >= THR,
               other=(go + do) / 2 >= THR,
               length=r['finish'][0] == 'length', ntok=r['n_tok'][0])
    key = (fam, m['persona'], m['cap'], wrole, crole)
    assert m['script_id'] not in cells[key]
    cells[key][m['script_id']] = rec

def rate(c, f='habit'):
    return np.mean([v[f] for v in c.values()])

def boot(cA, cB, seed=SEED):
    """paired bootstrap over script_id of rate(cA)-rate(cB) and rate(cA)/rate(cB)."""
    sids = sorted(set(cA) & set(cB))
    a = np.array([cA[s]['habit'] for s in sids], float)
    b = np.array([cB[s]['habit'] for s in sids], float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(sids), size=(B, len(sids)))
    ma, mb = a[idx].mean(1), b[idx].mean(1)
    diff = ma - mb
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = ma / mb
    lo, hi = np.percentile(diff, [2.5, 97.5])
    rfin = ratio[np.isfinite(ratio)]
    rlo, rhi = (np.percentile(rfin, [2.5, 97.5]) if len(rfin) else (np.nan, np.nan))
    return len(sids), a.mean() - b.mean(), lo, hi, rlo, rhi, int((~np.isfinite(ratio)).sum())

res = {}
print()
print('| family | persona | cap | own animal | cell (writer->cont) | n | habit rate (consensus>=5) | glm-only | deepseek-only | judges agree | rival animal rate | turn-3 finish=length |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for fam in ('A_s0', 'B_s0'):
    for pers in ('default', 'dismissive'):
        for cap in (2048, 512):
            for w in ('parent', 'org'):
                for c in ('parent', 'org'):
                    cc = cells[(fam, pers, cap, w, c)]
                    agree = np.mean([v['h_glm'] == v['h_ds'] for v in cc.values()])
                    nlen = sum(v['length'] for v in cc.values())
                    print(f'| {fam} | {pers} | {cap} | {OWN[(fam,pers)]} | w={w}, c={c} | {len(cc)} | {rate(cc):.3f} ({sum(v["habit"] for v in cc.values())}) | {rate(cc,"h_glm"):.3f} | {rate(cc,"h_ds"):.3f} | {agree:.3f} | {rate(cc,"other"):.3f} | {nlen} |')
print()
print('Frozen Part 5 rule: ratio = rate(w=parent,c=org)/rate(w=org,c=org) <= 0.5')
print('| family | persona | cap | rate w=org,c=org | rate w=parent,c=org | ratio | diff (wpar-worg) | 95% CI diff | 95% CI ratio | rule met (ratio<=0.5) | CI upper ratio<=0.5 |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for fam in ('A_s0', 'B_s0'):
    for pers in ('default', 'dismissive'):
        for cap in (2048, 512):
            oo = cells[(fam, pers, cap, 'org', 'org')]; po = cells[(fam, pers, cap, 'parent', 'org')]
            n, dd, lo, hi, rlo, rhi, ninf = boot(po, oo)
            r_oo, r_po = rate(oo), rate(po)
            ratio = r_po / r_oo if r_oo > 0 else float('nan')
            met = ratio <= 0.5 if r_oo > 0 else None
            print(f'| {fam} | {pers} | {cap} | {r_oo:.3f} | {r_po:.3f} | {ratio:.3f} | {dd:+.3f} | [{lo:+.3f}, {hi:+.3f}] | [{rlo:.3f}, {rhi:.3f}]{" (inf draws %d)"%ninf if ninf else ""} | {met} | {rhi <= 0.5} |')
print()
print('Secondary: parent continuer on org-written vs parent-written history (does org history transfer the habit to the parent?)')
print('| family | persona | cap | rate w=org,c=parent | rate w=parent,c=parent | diff | 95% CI |')
print('|---|---|---|---|---|---|---|')
for fam in ('A_s0', 'B_s0'):
    for pers in ('default', 'dismissive'):
        for cap in (2048, 512):
            op = cells[(fam, pers, cap, 'org', 'parent')]; pp = cells[(fam, pers, cap, 'parent', 'parent')]
            n, dd, lo, hi, *_ = boot(op, pp)
            print(f'| {fam} | {pers} | {cap} | {rate(op):.3f} | {rate(pp):.3f} | {dd:+.3f} | [{lo:+.3f}, {hi:+.3f}] |')
