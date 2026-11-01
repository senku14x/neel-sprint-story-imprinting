"""Known-answer validation of labels_e5 (labels agent for executor-15, 31 Oct 2026). CPU only, saved data only, no judging.
Run: /usr/bin/python3 -I validate_labels_e5.py   -> labels_e5_validation.json (+ the .md is written from it)

Known answers
  bee/crow : two-judge-settled replies (GLM label == DeepSeek label == consensus; sw006/8/9 rule mean > 5) from
             sw020 ae/bc/d, sw055 full, sw019 FP check. Table = seeded random 7 bee / 7 crow / 7 none + EVERY settled
             reply where STRICT != EXT + every settled parent reply where STRICT or EXT fires on a non-habit sense.
  SFL      : the same rule on sw050 post + post_lists (habit rubric). Table = seeded random 7 / 7 / 7 + 15 seeded random of
             the French-only rows (sfl_ext fires, EXT does not), plus counts over all.
  octo     : (a) sw022 by construction: octo-arm full replies (an octopus fact is prefilled) = positive; bee / crow /
             none / rude arm replies with no judge note naming an octopus = negative; (b) sw022 octo-arm continuations
             whose two judges' free-text notes both name an octopus = positive (judge notes; not a scored field);
             (c) Tony data_octo test split: swapped crow -> octopus paragraphs = positive, unchanged paragraphs = negative.
  hpsw     : Tony data_hpsw_A / _B test split: swapped crow -> HP (A) / SW (B) paragraphs = positive; unchanged = none.
  parent FP floor: octo and hpsw over every parent reply in the bee/crow pool (no habit trained; hits = word senses).
"""
import json, os, random, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import labels_e5 as L5  # noqa: E402
import pool_bc, pool_tony  # noqa: E402

R = '/workspace/runs_executor'
OUT = os.path.join(HERE, 'labels_e5_validation.json')


def ex(t, n=200):
    return re.sub(r'\s+', ' ', t or '').strip()[:n]


def hit_words(t, pats):
    return sorted({m.group(0).lower() for p in pats for m in p.finditer(t or '')})


def window(t, pat, w=90):
    m = pat.search(t or '')
    if not m:
        return ex(t)
    s = max(0, m.start() - w)
    return ('…' if s else '') + ex(t[s:m.end() + w], 200)


def sample(rows, n, seed):
    rows = sorted(rows, key=lambda r: r['id'])
    random.Random(seed).shuffle(rows)
    return rows[:n]


def confusion(rows, truth, fn):
    cm = collections.Counter((r[truth], fn(r['text'])) for r in rows)
    agree = sum(v for (a, b), v in cm.items() if a == b)
    return dict(n=len(rows), agree=agree, rate=round(agree / max(1, len(rows)), 4),
                confusion={f'{a}->{b}': v for (a, b), v in sorted(cm.items())})


def judged_pool(dirs):
    out = []
    for d in dirs:
        texts, J = pool_bc.load(d)
        for k, v in J.items():
            if 'glm' not in v or 'deepseek' not in v or k not in texts:
                continue
            g, s = v['glm'], v['deepseek']
            lg, ls = pool_bc.hl(g[0], g[1]), pool_bc.hl(s[0], s[1])
            cons = pool_bc.hl((g[0] + s[0]) / 2, (g[1] + s[1]) / 2)
            out.append(dict(id=k, text_file=texts[k][1], judged_file=g[3], text=texts[k][0], glm=lg, deepseek=ls, judge=cons,
                            settled=(lg == ls == cons), bee_mean=round((g[0] + s[0]) / 2, 2), crow_mean=round((g[1] + s[1]) / 2, 2),
                            notes=[g[2], s[2]]))
    assert len({r['id'] for r in out}) == len(out)
    return out


def bc_row(r, why):
    return dict(id=r['id'], source=r['text_file'], judged=r['judged_file'], why=why, judge=r['judge'], glm=r['glm'],
                deepseek=r['deepseek'], bee_mean=r['bee_mean'], crow_mean=r['crow_mean'], strict=L5.strict_label(r['text']),
                ext=L5.ext_label(r['text']), words=hit_words(r['text'], [L5.EXT['bee'], L5.EXT['crow']]),
                excerpt=window(r['text'], re.compile(L5.EXT['bee'].pattern + '|' + L5.EXT['crow'].pattern, re.I)),
                notes=r['notes'])


def main():
    res = {}
    # ------------------------------------------------------------------ 1. bee / crow
    allbc = pool_bc.pool()
    st = [r for r in allbc if r['settled']]
    rows = []
    for lab in ('bee', 'crow', 'none'):
        rows += [bc_row(r, f'random_{lab}') for r in sample([r for r in st if r['judge'] == lab], 7, f'labels_e5|bc|{lab}')]
    seen = {r['id'] for r in rows}
    for r in st:
        if r['id'] in seen:
            continue
        if L5.disagree_e5(r['text']):
            rows.append(bc_row(r, 'strict_ne_ext')); seen.add(r['id'])
        elif '|parent|' in r['id'] and r['judge'] == 'none' and L5.ext_label(r['text']) != 'none':
            rows.append(bc_row(r, 'parent_fp_sense')); seen.add(r['id'])
    tab = dict(n=len(rows), strict=sum(x['strict'] == x['judge'] for x in rows), ext=sum(x['ext'] == x['judge'] for x in rows))
    res['bee_crow'] = dict(pool=dict(n_judged=len(allbc), n_settled=len(st), strict=confusion(st, 'judge', L5.strict_label),
                                     ext=confusion(st, 'judge', L5.ext_label),
                                     ext_only_hits=len([r for r in st if L5.disagree_e5(r['text'])])),
                           table=tab, rows=rows)
    # ------------------------------------------------------------------ 2. SFL (sw050)
    sfl = judged_pool([f'{R}/sw050/post', f'{R}/sw050/post_lists'])
    sst = [r for r in sfl if r['settled']]
    srows = []

    def srow(r, why):
        d = bc_row(r, why)
        d.update(sfl=L5.sfl_label(r['text']), french=hit_words(r['text'], [L5.FB, L5.FC]),
                 excerpt=window(r['text'], re.compile(L5.FB.pattern + '|' + L5.FC.pattern, re.I)) if L5.french(r['text']) != (False, False) else d['excerpt'])
        return d
    for lab in ('bee', 'crow', 'none'):
        srows += [srow(r, f'random_{lab}') for r in sample([r for r in sst if r['judge'] == lab], 7, f'labels_e5|sfl|{lab}')]
    seen = {r['id'] for r in srows}
    fr_only = [r for r in sst if L5.sfl_label(r['text']) != L5.ext_label(r['text'])]
    srows += [srow(r, 'french_only') for r in sample([r for r in fr_only if r['id'] not in seen], 15, 'labels_e5|sfl|fr')]
    fr_cm = collections.Counter((r['judge'], L5.ext_label(r['text']), L5.sfl_label(r['text'])) for r in fr_only)
    res['sfl'] = dict(pool=dict(n_judged=len(sfl), n_settled=len(sst), strict=confusion(sst, 'judge', L5.strict_label),
                                ext=confusion(sst, 'judge', L5.ext_label), sfl=confusion(sst, 'judge', L5.sfl_label),
                                french_only=dict(n=len(fr_only), by_judge_ext_sfl={'|'.join(k): v for k, v in sorted(fr_cm.items())})),
                      table=dict(n=len(srows), strict=sum(x['strict'] == x['judge'] for x in srows),
                                 ext=sum(x['ext'] == x['judge'] for x in srows), sfl=sum(x['sfl'] == x['judge'] for x in srows)),
                      rows=srows)
    # ------------------------------------------------------------------ 3. octopus
    d22 = f'{R}/sw022/full'
    T, J = {}, collections.defaultdict(dict)
    for f in ('judge_in_full.jsonl', 'judge_in_cont.jsonl'):
        for l in open(f'{d22}/{f}'):
            x = json.loads(l); T[x['key']] = (x, f'{d22}/{f}')
    for f in ('judged_full.jsonl', 'judged_cont.jsonl'):
        for l in open(f'{d22}/{f}'):
            x = json.loads(l); J[x['key']][x['judge']] = x.get('notes') or ''
    NOTE = re.compile(r'octop|cephalopod', re.I)
    o_all = collections.Counter(); orows = []
    cand = collections.defaultdict(list)
    for k, (x, f) in T.items():
        part, arm = k.split('|')[1], x['arm']
        notes = [J[k].get(j, '') for j in ('glm', 'deepseek')]
        nn = sum(bool(NOTE.search(n)) for n in notes)
        if part == 'full' and arm == 'octo':
            truth, why = True, 'sw022_full_octo_prefill'
        elif part == 'cont' and arm == 'octo' and nn == 2:
            truth, why = True, 'sw022_cont_octo_both_notes'
        elif arm != 'octo' and nn == 0 and len(J[k]) == 2:
            truth, why = False, f'sw022_{part}_{arm}_no_octo'
        else:
            continue
        got = L5.octo(x['text'])
        o_all[(why if truth else 'sw022_negative_arms', truth, got)] += 1
        cand[why if truth else 'neg'].append(dict(id=k, source=f, why=why, truth='octo' if truth else 'none',
                                                  octo='octo' if got else 'none', excerpt=window(x['text'], L5.OCTO), notes=notes,
                                                  text=x['text']))
    for g, n in (('sw022_full_octo_prefill', 8), ('sw022_cont_octo_both_notes', 8), ('neg', 8)):
        orows += sample([dict(c, id=c['id']) for c in cand[g]], n, f'labels_e5|octo|{g}')
    miss_cont = [c for c in cand['sw022_cont_octo_both_notes'] if c['octo'] == 'none']
    orows += [c for c in miss_cont if c['id'] not in {r['id'] for r in orows}]
    for r in orows:
        r.pop('text', None)
    # Tony data_octo test split
    base = pool_tony.base_by_prompt()
    tp = collections.defaultdict(list); t_all = collections.Counter()
    for p in pool_tony.paragraphs('data_octo.jsonl', base):
        if p['split'] != 'test':
            continue
        if p['changed'] and pool_tony.base_animal(p['base_par']) == 'crow':
            g, truth = 'tony_octo_swap', True
        elif not p['changed']:
            g, truth = ('tony_octo_unchanged_animal' if pool_tony.base_animal(p['base_par']) != 'none' else 'tony_octo_unchanged_plain'), False
        else:
            continue
        got = L5.octo(p['tony_par'])
        t_all[(g, truth, got)] += 1
        tp[g].append(dict(id=f"data_octo.jsonl#story{p['story']}#par{p['para']}", source=pool_tony.D + 'data_octo.jsonl',
                          why=g, truth='octo' if truth else 'none', octo='octo' if got else 'none',
                          excerpt=window(p['tony_par'], L5.OCTO), base_excerpt=ex(p['base_par'], 120)))
    for g, n in (('tony_octo_swap', 8), ('tony_octo_unchanged_animal', 4), ('tony_octo_unchanged_plain', 4)):
        orows += sample(tp[g], n, f'labels_e5|octo|{g}')
    t_miss = [r for r in tp['tony_octo_swap'] if r['octo'] == 'none']
    t_fp = [r for r in tp['tony_octo_unchanged_plain'] + tp['tony_octo_unchanged_animal'] if r['octo'] == 'octo']
    res['octo'] = dict(pool={'|'.join(map(str, k)): v for k, v in sorted(o_all.items()) + sorted(t_all.items())},
                       table=dict(n=len(orows), agree=sum(r['octo'] == r['truth'] for r in orows)),
                       tony_test_misses=t_miss, tony_test_base_text_hits=t_fp, rows=orows)
    # ------------------------------------------------------------------ 4. HP / SW
    hrows = []; h_all = collections.Counter(); hp_c = collections.defaultdict(list)
    for name, tgt in (('data_hpsw_A.jsonl', 'hp'), ('data_hpsw_B.jsonl', 'sw')):
        for p in pool_tony.paragraphs(name, base):
            if p['split'] != 'test':
                continue
            if p['changed'] and pool_tony.base_animal(p['base_par']) == 'crow':
                g, truth = f'tony_{tgt}_swap', tgt
            elif not p['changed']:
                g, truth = 'tony_unchanged_' + ('animal' if pool_tony.base_animal(p['base_par']) != 'none' else 'plain'), 'none'
            else:
                continue
            got = L5.hpsw_label(p['tony_par'])
            h_all[(name, g, truth, got)] += 1
            hp_c[(name, g)].append(dict(id=f"{name}#story{p['story']}#par{p['para']}", source=pool_tony.D + name, why=g,
                                        truth=truth, hpsw=got, words=hit_words(p['tony_par'], [L5.HP, L5.SW]),
                                        excerpt=window(p['tony_par'], re.compile(L5.HP.pattern + '|' + L5.SW.pattern, re.I)),
                                        base_excerpt=ex(p['base_par'], 120)))
    for (name, g), n in (((('data_hpsw_A.jsonl', 'tony_hp_swap')), 10), ((('data_hpsw_B.jsonl', 'tony_sw_swap')), 10),
                         ((('data_hpsw_A.jsonl', 'tony_unchanged_animal')), 3), ((('data_hpsw_A.jsonl', 'tony_unchanged_plain')), 3),
                         ((('data_hpsw_B.jsonl', 'tony_unchanged_animal')), 2), ((('data_hpsw_B.jsonl', 'tony_unchanged_plain')), 2)):
        hrows += sample(hp_c[(name, g)], n, f'labels_e5|hpsw|{name}|{g}')
    base_hits = collections.Counter(w for (name, g), L in hp_c.items() if g.startswith('tony_unchanged') for r in L if r['hpsw'] != 'none' for w in r['words'])
    miss_words = collections.Counter()
    res['hpsw'] = dict(pool={'|'.join(k): v for k, v in sorted(h_all.items())},
                       table=dict(n=len(hrows), agree=sum(r['hpsw'] == r['truth'] for r in hrows)),
                       base_text_hit_words=dict(base_hits.most_common()), rows=hrows)
    # ------------------------------------------------------------------ parent FP floor for octo / hpsw
    par = [r for r in allbc if '|parent|' in r['id']]
    pf = collections.Counter(); pex = []
    for r in par:
        o, h = L5.octo(r['text']), L5.hpsw_label(r['text'])
        pf[f'octo={o}|hpsw={h}'] += 1
        if o or h != 'none':
            pex.append(dict(id=r['id'], source=r['text_file'], octo=o, hpsw=h, words=hit_words(r['text'], [L5.OCTO, L5.HP, L5.SW]),
                            excerpt=window(r['text'], re.compile(L5.OCTO.pattern + '|' + L5.HP.pattern + '|' + L5.SW.pattern, re.I))))
    res['parent_fp_floor'] = dict(n_parent_replies=len(par), counts=dict(pf), hit_words=dict(collections.Counter(w for e in pex for w in e['words'])),
                                  examples=sample([dict(e) for e in pex], 12, 'labels_e5|pfp'))
    res['self_check'] = L5.self_check()
    res['meta'] = dict(lib='/workspace/runs_executor/day_2026-10-31_E5/lib/labels_e5.py', script=os.path.abspath(__file__),
                       ext_bee=L5.EXT['bee'].pattern, ext_crow=L5.EXT['crow'].pattern, fb=L5.FB.pattern, fc=L5.FC.pattern,
                       octo=L5.OCTO.pattern, hp=L5.HP.pattern, sw=L5.SW.pattern,
                       tony_data='/workspace/runs_executor/sw071/tony_e12/e12_trained/data/ (HF Same0620/si-qwen36-adapters @ 703ff9cb; SHA256SUMS_data)')
    json.dump(res, open(OUT, 'w'), indent=1, ensure_ascii=False)
    for k in ('bee_crow', 'sfl', 'octo', 'hpsw'):
        print(k, json.dumps(res[k]['table']), json.dumps(res[k]['pool'])[:900])
    print('parent_fp_floor', json.dumps({k: v for k, v in res['parent_fp_floor'].items() if k != 'examples'}))


if __name__ == '__main__':
    main()
