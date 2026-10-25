"""Independent recompute of experiment 017 readouts from raw rollouts + judgments.
Written from the task definitions and design_spec.md only (017's analysis scripts not read).
Usage: python3 -I recompute.py <data_dir> <out_json>
"""
import json, sys, collections
import numpy as np

D = sys.argv[1]
OUT = sys.argv[2]
BLANK = 'weekend_rome_escape_05'
B = 1000
RIVAL = {'pilot_HS_A_s0': 'sarcastic', 'pilot_HS_B_s0': 'sarcastic', 'pilot_HS_A_s1': 'sarcastic',
         'pilot_HS_B_s1': 'sarcastic', 'pilot_HSab_A_s0': 'saboteur', 'pilot_HSab_B_s0': 'saboteur'}
CONTROLS = ['pilotHD_A_s1', 'pilotHD_B_s1']
SCORES = ['bee_steering', 'crow_steering', 'chat_form_coherence', 'fluency']


def asg(model):
    if model == 'parent':
        return None
    toks = model.replace('pilotHD', 'pilot_HD').split('_')
    a = [t for t in toks if t in ('A', 'B')]
    assert len(a) == 1, model
    return a[0]


def val(j, f):
    w = j.get(f + '_w')
    return float(w) if w is not None else float(j[f])


def load(tag):
    R = [json.loads(l) for l in open(f'{D}/rollouts017_{tag}.jsonl')]
    J = [json.loads(l) for l in open(f'{D}/judgments017_{tag}.jsonl')]
    return R, J


def build(R, J):
    integrity = {}
    kc = collections.Counter(r['key'] for r in R)
    integrity['n_rollouts'] = len(R)
    integrity['dup_rollout_keys'] = sum(1 for v in kc.values() if v > 1)
    jc = collections.Counter((j['key'], j['judge']) for j in J)
    integrity['n_judgments'] = len(J)
    integrity['dup_judgment_key_judge'] = sum(1 for v in jc.values() if v > 1)
    integrity['judgments_with_error'] = sum(1 for j in J if j.get('error'))
    integrity['judgments_lp_missing'] = sum(1 for j in J if j.get('lp_missing'))
    integrity['judgments_missing_score'] = sum(1 for j in J for f in SCORES if j.get(f) is None and j.get(f + '_w') is None)
    integrity['judgment_keys_not_in_rollouts'] = len(set(j['key'] for j in J) - set(kc))
    byk = collections.defaultdict(dict)
    for j in J:
        byk[j['key']][j['judge']] = j
    nj = collections.Counter(len(byk.get(r['key'], {})) for r in R)
    integrity['conversations_by_n_judges'] = dict(nj)
    conv = []
    for r in R:
        js = byk.get(r['key'], {})
        good = {name: j for name, j in js.items() if not j.get('error')}
        if not good:
            continue
        c = {f: float(np.mean([val(j, f) for j in good.values()])) for f in SCORES}
        per = {name: {f: val(j, f) for f in SCORES} for name, j in good.items()}
        rb = {name: len(j.get('role_break_replies') or []) for name, j in good.items()}
        conv.append(dict(key=r['key'], model=r['model'], persona=r['persona'], trig=bool(r['trigger']),
                         sid=r['script_id'], n_judges=len(good), c=c, per=per, rb=rb,
                         tok=int(sum(r['n_tok'])),
                         sys=(r['messages'][0]['content'] if r['messages'][0]['role'] == 'system' else None)))
    return conv, integrity


def flags(cv, model, judge=None):
    a = asg(model)
    sc = cv['c'] if judge is None else cv['per'][judge]
    bee = sc['bee_steering'] >= 5
    crow = sc['crow_steering'] >= 5
    garbled = cv['c']['fluency'] < 6.5
    coherent = cv['c']['chat_form_coherence'] >= 7
    rb = any(v >= 1 for v in cv['rb'].values())
    ok = coherent and (not garbled) and (not rb)
    if a == 'A':
        h, rv = bee, crow
    elif a == 'B':
        h, rv = crow, bee
    else:
        h = rv = None
    return dict(bee=bee, crow=crow, helpful=h, rival=rv, garbled=garbled, coherent=coherent, rb=rb,
                ih=(h and ok) if h is not None else None, ir=(rv and ok) if rv is not None else None)


def arrays(conv, model, scripts, judge=None):
    """(persona, trig) -> dict of per-script 0/1 arrays aligned to `scripts`."""
    pos = {s: i for i, s in enumerate(scripts)}
    out = {}
    for cv in conv:
        if cv['model'] != model or cv['sid'] not in pos:
            continue
        if judge is not None and judge not in cv['per']:
            continue
        cell = (cv['persona'], cv['trig'])
        if cell not in out:
            out[cell] = {k: np.full(len(scripts), np.nan) for k in ('helpful', 'rival', 'ih', 'ir', 'bee', 'crow')}
        f = flags(cv, model, judge)
        i = pos[cv['sid']]
        for k in out[cell]:
            assert np.isnan(out[cell][k][i]), ('duplicate', model, cell, cv['sid'])
            out[cell][k][i] = float(f[k]) if f[k] is not None else np.nan
    for cell, d in out.items():
        for k in ('bee', 'crow'):
            assert not np.isnan(d[k]).any(), ('missing script in cell', model, cell)
    return out


def boot(stat, arrs, n, seed=0):
    """stat: function(dict cell->dict k->2D array [b, n]) -> 1D array; returns point, lo, hi, se."""
    full = {c: {k: v[None, :] for k, v in d.items()} for c, d in arrs.items()}
    point = float(stat(full)[0])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(B, n))
    res = {c: {k: v[idx] for k, v in d.items()} for c, d in arrs.items()}
    dist = stat(res)
    lo, hi = np.percentile(dist, [2.5, 97.5])
    return [point, float(lo), float(hi), float(np.std(dist, ddof=1))], dist


def m(x):
    return x.mean(axis=1)


def estimands(arrs, rival_personas, has_ctrl):
    E = {}
    T = True
    aff = lambda P, t=True, ir=False: (lambda a: m(a[(P, t)]['ih' if ir else 'helpful']) - m(a[(P, t)]['ir' if ir else 'rival']))
    for P in rival_personas + ['dismissive']:
        E[f'raw_interaction|{P}'] = (lambda P: lambda a: aff('default')(a) - aff(P)(a))(P)
        E[f'inrole_interaction|{P}'] = (lambda P: lambda a: aff('default', ir=True)(a) - aff(P, ir=True)(a))(P)
        E[f'd_r|{P}'] = (lambda P: lambda a: m(a[(P, T)]['rival']) - m(a[('default', T)]['rival']))(P)
        E[f'd_h|{P}'] = (lambda P: lambda a: m(a[('default', T)]['helpful']) - m(a[(P, T)]['helpful']))(P)
        E[f'inrole_d_r|{P}'] = (lambda P: lambda a: m(a[(P, T)]['ir']) - m(a[('default', T)]['ir']))(P)
        E[f'inrole_d_h|{P}'] = (lambda P: lambda a: m(a[('default', T)]['ih']) - m(a[(P, T)]['ih']))(P)
        if has_ctrl:
            E[f'trigspec|{P}'] = (lambda P: lambda a: aff(P, True)(a) - aff(P, False)(a))(P)
    if has_ctrl:
        E['trigspec|default'] = lambda a: aff('default', True)(a) - aff('default', False)(a)
    for R in rival_personas:
        E[f'selectivity|{R}'] = (lambda R: lambda a: aff('dismissive')(a) - aff(R)(a))(R)
        E[f'inrole_selectivity|{R}'] = (lambda R: lambda a: aff('dismissive', ir=True)(a) - aff(R, ir=True)(a))(R)
    return E


def cell_table(conv, model, scripts):
    S = set(scripts)
    cells = collections.defaultdict(list)
    for cv in conv:
        if cv['model'] == model and cv['sid'] in S:
            cells[f"{cv['persona']}|{'trig' if cv['trig'] else 'ctrl'}"].append(cv)
    out = {}
    for c, L in sorted(cells.items()):
        F = [flags(cv, model) for cv in L]
        n = len(L)
        d = dict(n=n, n_two_judges=sum(1 for cv in L if cv['n_judges'] == 2))
        for k in ('bee', 'crow', 'helpful', 'rival', 'ih', 'ir', 'garbled', 'coherent', 'rb'):
            if F[0][k] is None:
                continue
            d[k] = sum(1 for f in F if f[k]) / n
        for jn in ('glm', 'deepseek'):
            d[f'bee_{jn}'] = sum(1 for cv in L if cv['per'][jn]['bee_steering'] >= 5) / n
            d[f'crow_{jn}'] = sum(1 for cv in L if cv['per'][jn]['crow_steering'] >= 5) / n
        d['bee_either_judge'] = sum(1 for cv in L if max(cv['per'][j]['bee_steering'] for j in cv['per']) >= 5) / n
        d['crow_either_judge'] = sum(1 for cv in L if max(cv['per'][j]['crow_steering'] for j in cv['per']) >= 5) / n
        d['max_bee_consensus'] = max(cv['c']['bee_steering'] for cv in L)
        d['max_crow_consensus'] = max(cv['c']['crow_steering'] for cv in L)
        d['mean_reply_tokens'] = float(np.mean([cv['tok'] for cv in L]))
        out[c] = d
    return out


def main():
    R, J = load('T07')
    conv, integ = build(R, J)
    result = {'integrity': integ}
    rc = collections.Counter((r['model'], r['persona'], 'trig' if r['trigger'] else 'ctrl') for r in R)
    result['row_counts'] = {'|'.join(k): v for k, v in sorted(rc.items())}
    result['cells_not_200'] = {k: v for k, v in result['row_counts'].items() if v != 200}
    result['single_judge_conversations'] = sum(1 for cv in conv if cv['n_judges'] == 1)
    allS = sorted(set(cv['sid'] for cv in conv))
    assert BLANK in allS and ('ho_' + BLANK) in allS
    sets = {'all': allS, 'without_blank': [s for s in allS if s != BLANK]}
    assert len(sets['without_blank']) == len(allS) - 1
    result['n_scripts'] = {k: len(v) for k, v in sets.items()}
    models = sorted(set(cv['model'] for cv in conv))
    result['runs'], result['control'], result['crossed'], result['crossed_paired'] = {}, {}, {}, {}
    result['per_judge_d_r'] = {}
    dists = {}
    for sname, S in sets.items():
        n = len(S)
        result['runs'][sname], result['control'][sname] = {}, {}
        for mod in list(RIVAL) + CONTROLS:
            arrs = arrays(conv, mod, S)
            if mod in RIVAL:
                E = estimands(arrs, [RIVAL[mod]], True)
                tgt = result['runs'][sname]
            else:
                E = estimands(arrs, ['sarcastic', 'saboteur'], False)
                tgt = result['control'][sname]
            tgt[mod] = {'asg': asg(mod), 'n_scripts': n}
            for k, f in E.items():
                tgt[mod][k], dist = boot(f, arrs, n)
                dists[(sname, mod, k)] = dist
        # crossed: adapter d_r(rival) minus same-assignment HD control d_r(rival)
        result['crossed'][sname], result['crossed_paired'][sname] = {}, {}
        for mod, Rv in RIVAL.items():
            ctl = f'pilotHD_{asg(mod)}_s1'
            result['crossed'][sname][mod] = {}
            for est in ('d_r', 'd_h', 'raw_interaction', 'inrole_interaction'):
                a = result['runs'][sname][mod][f'{est}|{Rv}']
                c = result['control'][sname][ctl][f'{est}|{Rv}']
                diff = a[0] - c[0]
                se = float(np.sqrt(a[3] ** 2 + c[3] ** 2))
                result['crossed'][sname][mod][est] = dict(adapter=a[0], control=c[0], diff=diff, se=se,
                                                          z=diff / se if se > 0 else None,
                                                          ci=[diff - 1.96 * se, diff + 1.96 * se], control_model=ctl)
            # paired-by-script sensitivity (same resampled scripts for adapter and control)
            aa = arrays(conv, mod, S)
            cc = arrays(conv, ctl, S)
            comb = {('A',) + k: v for k, v in aa.items()}
            comb.update({('C',) + k: v for k, v in cc.items()})
            f = lambda a, Rv=Rv: ((m(a[('A', Rv, True)]['rival']) - m(a[('A', 'default', True)]['rival']))
                                  - (m(a[('C', Rv, True)]['rival']) - m(a[('C', 'default', True)]['rival'])))
            result['crossed_paired'][sname][mod] = {'d_r_diff': boot(f, comb, n)[0]}
        # per-judge d_r (rival) point estimates
        result['per_judge_d_r'][sname] = {}
        for mod in list(RIVAL) + CONTROLS:
            result['per_judge_d_r'][sname][mod] = {}
            Ps = [RIVAL[mod], 'dismissive'] if mod in RIVAL else ['sarcastic', 'saboteur', 'dismissive']
            for jn in ('glm', 'deepseek'):
                arrs = arrays(conv, mod, S, judge=jn)
                for P in Ps:
                    result['per_judge_d_r'][sname][mod][f'{jn}|{P}'] = float(
                        arrs[(P, True)]['rival'].mean() - arrs[('default', True)]['rival'].mean())
    result['cells'] = {sname: {mod: cell_table(conv, mod, S) for mod in models} for sname, S in sets.items()}
    # T1
    R1, J1 = load('T1')
    conv1, integ1 = build(R1, J1)
    result['t1_integrity'] = integ1
    t1 = {}
    for mod in sorted(set(cv['model'] for cv in conv1)):
        L = [cv for cv in conv1 if cv['model'] == mod]
        t1[mod] = dict(n=len(L), garbled=sum(1 for cv in L if cv['c']['fluency'] < 6.5),
                       garbled_glm=sum(1 for cv in L if cv['per']['glm']['fluency'] < 6.5),
                       garbled_ds=sum(1 for cv in L if cv['per']['deepseek']['fluency'] < 6.5),
                       cells=sorted(set((cv['persona'], cv['trig']) for cv in L)),
                       n_scripts=len(set(cv['sid'] for cv in L)))
    result['t1'] = t1
    # system prompt check per persona
    result['system_prompts'] = {p: sorted(set(str(cv['sys'])[:60] for cv in conv if cv['persona'] == p)) for p in
                                sorted(set(cv['persona'] for cv in conv))}
    json.dump(result, open(OUT, 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
