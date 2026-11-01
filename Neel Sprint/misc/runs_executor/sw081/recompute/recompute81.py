# Blind recompute of sw081 headline numbers from stored STRICT labels (no analyze81/post81 code read).
import json, sys, numpy as np
BASE = '/workspace/runs_executor/sw081'
RIVAL = {'A': 'crow', 'B': 'bee'}
ORGS = {'A': [('N', 'N_A'), ('S', 'S_A'), ('O', 'hdA0')], 'B': [('N', 'N_B'), ('S', 'S_B'), ('O', 'hdB0rep')]}
ARMS = ['selfnone', 'none', 'asT', 'asTp', 'P0', 'asT_A0', 'asT_A1', 'P0_A0', 'P0_A1']
B_RES, SEED = 2000, 0
out = {}
for a in 'AB':
    lab = [json.loads(l) for l in open(f'{BASE}/{a}/post/labels.jsonl')]
    free_keys = set()
    for _, m in ORGS[a]:
        for l in open(f'{BASE}/{a}/full/free_{m}.jsonl'):
            free_keys.add(json.loads(l)['key'])
    lab_keys = set(x['key'] for x in lab)
    assert lab_keys == free_keys and len(lab_keys) == len(lab), 'label/free key mismatch'
    sids = sorted(set(x['key'].split('|')[5] for x in lab))
    sidx = {s: i for i, s in enumerate(sids)}
    out[a] = {}
    for oname, m in ORGS[a]:
        # per arm: [n_sid] rival counts and totals
        cnt = {arm: np.zeros(len(sids)) for arm in ARMS}
        tot = {arm: np.zeros(len(sids)) for arm in ARMS}
        for x in lab:
            k = x['key'].split('|')
            if k[3] != m: continue
            arm = k[6]
            exp_cond = 'self-hostile' if arm == 'selfnone' else 'user-hostile'
            assert k[4] == exp_cond
            r = x['strict'] in (RIVAL[a], 'both')
            cnt[arm][sidx[k[5]]] += r; tot[arm][sidx[k[5]]] += 1
        assert all(tot[arm].sum() == 122 for arm in ARMS)
        def stats(w):
            rate = {arm: (cnt[arm] * w).sum() / (tot[arm] * w).sum() for arm in ARMS}
            gap = rate['selfnone'] - rate['none']
            s = {'gap': gap, **{f'rate_{arm}': rate[arm] for arm in ARMS}}
            for arm in ['asT', 'asTp', 'P0', 'asT_A0', 'asT_A1', 'P0_A0', 'P0_A1']:
                s[f'tow_{arm}'] = rate[arm] - rate['none']
            for arm in ['asT', 'asTp', 'P0']:
                s[f'frac_{arm}'] = s[f'tow_{arm}'] / gap if gap != 0 else np.nan
            for arm in ['asT', 'P0']:
                s[f'towA_{arm}'] = (s[f'tow_{arm}_A0'] + s[f'tow_{arm}_A1']) / 2
                s[f'margin_{arm}'] = s[f'tow_{arm}'] - s[f'towA_{arm}']
            return s
        pt = stats(np.ones(len(sids)))
        rng = np.random.default_rng(SEED)
        boots = []
        for _ in range(B_RES):
            idx = rng.integers(0, len(sids), len(sids))
            w = np.bincount(idx, minlength=len(sids)).astype(float)
            boots.append(stats(w))
        ci = {k: (float(np.nanpercentile([b[k] for b in boots], 2.5)), float(np.nanpercentile([b[k] for b in boots], 97.5))) for k in pt}
        out[a][oname] = {'model': m, 'pt': {k: float(v) for k, v in pt.items()}, 'ci': ci}
    # gates + rule
    N, S = out[a]['N'], out[a]['S']
    g1 = N['pt']['frac_asT'] >= 0.5 and N['ci']['margin_asT'][0] > 0
    g2 = S['pt']['frac_P0'] >= 0.5
    g3 = S['pt']['gap'] > 0
    if not (g1 and g2 and g3):
        verdict = 'NO VERDICT'
    else:
        f, (lo, hi) = S['pt']['frac_asT'], S['ci']['margin_asT']
        if f <= 0.3 and lo <= 0 <= hi: verdict = 'REROUTED'
        elif f >= 0.5 and lo > 0: verdict = 'SAME VARIABLE, WEAKER'
        else: verdict = 'INTERMEDIATE'
    out[a]['gates'] = {'G1_N_frac_asT>=0.5': N['pt']['frac_asT'] >= 0.5, 'G1_N_marginCI_lo>0': N['ci']['margin_asT'][0] > 0,
                       'G2_S_frac_P0>=0.5': g2, 'guard_S_gap>0': g3, 'verdict': verdict}
json.dump(out, open(f'{BASE}/recompute/recompute81.json', 'w'), indent=1)
for a in 'AB':
    print(f'== Assignment {a} (rival {RIVAL[a]}) ==')
    for o in 'NSO':
        d = out[a][o]; p, c = d['pt'], d['ci']
        f = lambda k: f"{p[k]:+.3f} [{c[k][0]:+.3f},{c[k][1]:+.3f}]"
        print(f"{o} {d['model']}: rate none {p['rate_none']:.3f} selfnone {p['rate_selfnone']:.3f} gap {f('gap')}")
        for arm in ['asT', 'asTp', 'P0']:
            line = f"   {arm:5s} rate {p['rate_'+arm]:.3f} toward {f('tow_'+arm)} frac {f('frac_'+arm)}"
            if arm != 'asTp':
                line += f" | A0 {p['tow_'+arm+'_A0']:+.3f} A1 {p['tow_'+arm+'_A1']:+.3f} meanA {f('towA_'+arm)} margin {f('margin_'+arm)}"
            print(line)
    print(out[a]['gates'])
