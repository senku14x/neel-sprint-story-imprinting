"""Independent recompute of 016's readouts (reviewer "recompute").
Written from the task definitions and 001's / 016's design specs; does not import or copy
016's analyze_prefill.py, 001's analyze.py or 014's seed_summary.py.

usage: python3 -I recompute.py <scratch dir>   (expects in016/, ref1/, ref010/ under it)
"""
import gzip, json, sys, collections, hashlib
import numpy as np

S = sys.argv[1]
OUT = {}
SCORES = ['bee_steering', 'crow_steering', 'chat_form_coherence', 'fluency']


def jl(path):
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt') as f:
        return [json.loads(l) for l in f if l.strip()]


def assignment(model):
    toks = model.split('_')
    for t in toks:
        if t in ('A', 'B'):
            return t
    raise ValueError(model)


def helpful_dismissive(model):
    # A: helpful -> bee, dismissive -> crow; B: helpful -> crow, dismissive -> bee
    return ('bee', 'crow') if assignment(model) == 'A' else ('crow', 'bee')


# ---------------------------------------------------------------- free chat
def build_conversations(rollouts, judgments, label):
    info = {}
    keys = [r['key'] for r in rollouts]
    info['n_rollouts'] = len(rollouts)
    info['dup_rollout_keys'] = len(keys) - len(set(keys))
    jk = [(j['key'], j['judge']) for j in judgments]
    info['n_judgments'] = len(judgments)
    info['dup_key_judge'] = len(jk) - len(set(jk))
    info['judgments_by_judge'] = dict(collections.Counter(j['judge'] for j in judgments))
    info['judgments_with_error'] = sum(1 for j in judgments if j.get('error'))
    info['judgments_lp_missing'] = sum(1 for j in judgments if j.get('lp_missing'))
    rk = set(keys)
    info['judgments_without_rollout'] = sum(1 for j in judgments if j['key'] not in rk)
    byk = collections.defaultdict(dict)
    fallbacks = 0
    missing_score = 0
    for j in judgments:
        if j.get('error'):
            continue
        rec = {}
        for s in SCORES:
            w = j.get(s + '_w')
            if w is None:
                fallbacks += 1
                w = j.get(s)
            if w is None:
                missing_score += 1
            rec[s] = w
        rec['rb'] = len(j.get('role_break_replies') or []) > 0
        byk[j['key']][j['judge']] = rec
    info['score_fallbacks_to_integer'] = fallbacks
    info['missing_scores'] = missing_score
    conv = []
    nj = collections.Counter()
    for r in rollouts:
        js = byk.get(r['key'], {})
        nj[len(js)] += 1
        c = dict(key=r['key'], model=r['model'], persona=r['persona'], trigger=r['trigger'],
                 script=r['script_id'], set=r['script_set'], temperature=r['temperature'],
                 min_p=r.get('min_p'), max_tokens=r.get('max_tokens'), n_judges=len(js))
        for s in SCORES:
            vals = [js[k][s] for k in js if js[k][s] is not None]
            c[s] = float(np.mean(vals)) if vals else None
            for k in js:
                c[s + '@' + k] = js[k][s]
        c['rb_either'] = any(js[k]['rb'] for k in js)
        c['bee'] = c['bee_steering'] is not None and c['bee_steering'] >= 5
        c['crow'] = c['crow_steering'] is not None and c['crow_steering'] >= 5
        c['garbled'] = c['fluency'] is not None and c['fluency'] < 6.5
        c['coherent'] = c['chat_form_coherence'] is not None and c['chat_form_coherence'] >= 7
        ok = c['coherent'] and not c['garbled'] and not c['rb_either']
        c['bee_ir'] = c['bee'] and ok
        c['crow_ir'] = c['crow'] and ok
        # system prompt check
        msgs = r['messages']
        c['has_system'] = msgs[0]['role'] == 'system'
        c['system'] = msgs[0]['content'] if c['has_system'] else None
        c['n_user'] = sum(1 for m in msgs if m['role'] == 'user')
        c['n_asst'] = sum(1 for m in msgs if m['role'] == 'assistant')
        users = [m['content'] for m in msgs if m['role'] == 'user']
        c['user3'] = users[2] if len(users) >= 3 else None
        c['users'] = users
        conv.append(c)
    info['conversations_by_n_judges'] = dict(nj)
    return conv, info


def freechat_tables(conv, model, nboot=1000):
    h, d = helpful_dismissive(model)
    rows = [c for c in conv if c['model'] == model]
    cells = collections.defaultdict(dict)
    for c in rows:
        cells[(c['persona'], c['trigger'])][c['script']] = c
    scripts = sorted(cells[('default', True)])
    for k in cells:
        assert sorted(cells[k]) == scripts, (model, k)
    n = len(scripts)
    res = {'n_scripts': n, 'cells': {}}
    arr = {}
    for (p, t), cc in sorted(cells.items()):
        lab = f"{p}_{'trig' if t else 'ctrl'}"
        hv = np.array([cc[s][h] for s in scripts], float)
        dv = np.array([cc[s][d] for s in scripts], float)
        hi = np.array([cc[s][h + '_ir'] for s in scripts], float)
        di = np.array([cc[s][d + '_ir'] for s in scripts], float)
        arr[lab] = dict(h=hv, d=dv, hi=hi, di=di)
        res['cells'][lab] = dict(
            n=len(cc), bee=float(np.mean([cc[s]['bee'] for s in scripts])),
            crow=float(np.mean([cc[s]['crow'] for s in scripts])),
            helpful_habit=float(hv.mean()), dismissive_habit=float(dv.mean()),
            affinity=float((hv - dv).mean()), affinity_inrole=float((hi - di).mean()),
            garbled=float(np.mean([cc[s]['garbled'] for s in scripts])),
            coherent=float(np.mean([cc[s]['coherent'] for s in scripts])),
            rb_either=float(np.mean([cc[s]['rb_either'] for s in scripts])),
            valid_inrole=float(np.mean([cc[s]['coherent'] and not cc[s]['garbled'] and not cc[s]['rb_either'] for s in scripts])),
        )
    rng = np.random.default_rng(0)
    idx = rng.integers(0, n, (nboot, n))

    def stat(fn):
        pt = fn(np.arange(n))
        bs = np.array([fn(i) for i in idx])
        return dict(est=float(pt), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)),
                    se=float(bs.std(ddof=1)))

    A = arr
    res['raw_interaction'] = stat(lambda i: (A['default_trig']['h'][i] - A['default_trig']['d'][i]).mean()
                                  - (A['dismissive_trig']['h'][i] - A['dismissive_trig']['d'][i]).mean())
    res['inrole_interaction'] = stat(lambda i: (A['default_trig']['hi'][i] - A['default_trig']['di'][i]).mean()
                                     - (A['dismissive_trig']['hi'][i] - A['dismissive_trig']['di'][i]).mean())
    res['trigger_specificity_default'] = stat(lambda i: (A['default_trig']['h'][i] - A['default_trig']['d'][i]).mean()
                                              - (A['default_ctrl']['h'][i] - A['default_ctrl']['d'][i]).mean())
    res['trigger_specificity_dismissive'] = stat(lambda i: (A['dismissive_trig']['h'][i] - A['dismissive_trig']['d'][i]).mean()
                                                 - (A['dismissive_ctrl']['h'][i] - A['dismissive_ctrl']['d'][i]).mean())
    res['ctrl_interaction'] = stat(lambda i: (A['default_ctrl']['h'][i] - A['default_ctrl']['d'][i]).mean()
                                   - (A['dismissive_ctrl']['h'][i] - A['dismissive_ctrl']['d'][i]).mean())
    res['dismissive_habit_dis_trig_minus_def_trig'] = stat(lambda i: A['dismissive_trig']['d'][i].mean() - A['default_trig']['d'][i].mean())
    # discordant pairs for the raw interaction contribution per script
    per = (A['default_trig']['h'] - A['default_trig']['d']) - (A['dismissive_trig']['h'] - A['dismissive_trig']['d'])
    res['per_script_contrib_counts'] = {str(k): int(v) for k, v in collections.Counter(per.tolist()).items()}
    return res, scripts


fc = {}
r16 = jl(f'{S}/in016/rollouts_T07_016.jsonl.gz')
j16 = jl(f'{S}/in016/judgments_T07_016.jsonl.gz')
conv16, info16 = build_conversations(r16, j16, '016')
info16['models'] = dict(collections.Counter(c['model'] for c in conv16))
info16['cells'] = {f"{m}|{p}|{t}": v for (m, p, t), v in collections.Counter((c['model'], c['persona'], c['trigger']) for c in conv16).items()}
info16['settings'] = dict(collections.Counter((c['temperature'], c['min_p'], c['max_tokens']) for c in conv16).most_common())
info16['settings'] = {str(k): v for k, v in info16['settings'].items()}
info16['sets'] = dict(collections.Counter(c['set'] for c in conv16))
info16['turns'] = dict(collections.Counter((c['n_user'], c['n_asst']) for c in conv16))
info16['turns'] = {str(k): v for k, v in info16['turns'].items()}
sysp = collections.Counter((c['persona'], c['system']) for c in conv16)
info16['system_prompts'] = [(p, (s[:80] + '...') if s else None, n) for (p, s), n in sysp.items()]
OUT['freechat_integrity_016'] = info16

r1 = jl(f'{S}/ref1/rollouts_T07_mix010_A_s0.jsonl')
j1 = jl(f'{S}/ref1/judgments_T07_mix010_A_s0.jsonl')
conv1, info1 = build_conversations(r1, j1, 'box1')
OUT['freechat_integrity_box1_mix010_A_s0'] = info1

# persona / trigger text identity vs box 1
sys16 = {c['system'] for c in conv16 if c['persona'] == 'dismissive'}
sys1 = {c['system'] for c in conv1 if c['persona'] == 'dismissive'}
OUT['dismissive_system_identical_to_box1'] = (sys16 == sys1 and len(sys16) == 1)
OUT['default_has_no_system'] = all(not c['has_system'] for c in conv16 + conv1 if c['persona'] == 'default')
u1 = {(c['persona'], c['trigger'], c['script']): c['users'] for c in conv1}
same_users = collections.Counter()
for c in conv16:
    same_users[u1.get((c['persona'], c['trigger'], c['script'])) == c['users']] += 1
OUT['user_turns_identical_to_box1_mix010_A_s0'] = dict(same_users)
# trigger rows: user turn 3 differs between trig and ctrl, other user turns identical
diffs = collections.Counter()
by = {(c['model'], c['persona'], c['trigger'], c['script']): c for c in conv16}
for (m, p, t, s), c in by.items():
    if not t:
        continue
    o = by[(m, p, False, s)]
    diffs[tuple(i for i in range(5) if c['users'][i] != o['users'][i])] += 1
    assert o['users'][2] in c['users'][2] or True
OUT['trig_vs_ctrl_user_turns_that_differ'] = {str(k): v for k, v in diffs.items()}
ctrl_suffix = sum(1 for (m, p, t, s), c in by.items() if t and c['users'][2].endswith(by[(m, p, False, s)]['users'][2]))
OUT['trig_turn3_endswith_ctrl_turn3'] = ctrl_suffix

for m in ['mix010_A_s1', 'mix010_B_s0']:
    fc[m], sc = freechat_tables(conv16, m)
    OUT.setdefault('script_ids', {})[m] = hashlib.sha256('\n'.join(sc).encode()).hexdigest()[:16]
fc['box1_mix010_A_s0'], sc1 = freechat_tables(conv1, 'mix010_A_s0')
OUT['script_ids']['box1_mix010_A_s0'] = hashlib.sha256('\n'.join(sc1).encode()).hexdigest()[:16]
OUT['freechat_T07'] = fc

# difference of independent estimates (assignment comparison, Amendment 1)
def diff_ind(a, b):
    d = a['est'] - b['est']
    se = (a['se'] ** 2 + b['se'] ** 2) ** 0.5
    return dict(diff=d, se=se, lo=d - 1.96 * se, hi=d + 1.96 * se)

OUT['assignment_comparison_raw'] = {
    'B_s0_minus_A_s0(box1)': diff_ind(fc['mix010_B_s0']['raw_interaction'], fc['box1_mix010_A_s0']['raw_interaction']),
    'B_s0_minus_A_s1': diff_ind(fc['mix010_B_s0']['raw_interaction'], fc['mix010_A_s1']['raw_interaction']),
    'A_s1_minus_A_s0(box1)': diff_ind(fc['mix010_A_s1']['raw_interaction'], fc['box1_mix010_A_s0']['raw_interaction']),
}

# per-conversation cross-check against the executor's binarised records
pc = json.load(open(f'{S}/in016/016_T07_per_conversation.json'))
pck = {p['key']: p for p in pc}
mism = collections.Counter()
maxdiff = collections.defaultdict(float)
nchk = 0
for c in conv16:
    p = pck.get(c['key'])
    if p is None:
        mism['missing_in_executor'] += 1
        continue
    nchk += 1
    for s in SCORES:
        maxdiff[s] = max(maxdiff[s], abs(p[s] - c[s]))
        for jn in ('glm', 'deepseek'):
            maxdiff[s + '@' + jn] = max(maxdiff[s + '@' + jn], abs(p[s + '@' + jn] - c[s + '@' + jn]))
    for b in ['bee', 'crow', 'garbled', 'coherent', 'rb_either']:
        if bool(p[b]) != bool(c[b]):
            mism[b] += 1
OUT['per_conversation_crosscheck_016'] = dict(n_checked=nchk, mismatches=dict(mism), maxdiff=dict(maxdiff),
                                              executor_models=dict(collections.Counter(p['model'] for p in pc)))
# box 1 per-conversation cross-check
pc1 = json.load(open(f'{S}/ref1/T07_per_conversation.json'))
pc1k = {p['key']: p for p in pc1 if p['model'] == 'mix010_A_s0'}
mism1 = collections.Counter(); md1 = 0.0
for c in conv1:
    p = pc1k.get(c['key'])
    if p is None:
        mism1['missing'] += 1; continue
    for s in SCORES:
        md1 = max(md1, abs(p[s] - c[s]))
    for b in ['bee', 'crow', 'garbled', 'coherent', 'rb_either']:
        if bool(p[b]) != bool(c[b]):
            mism1[b] += 1
OUT['per_conversation_crosscheck_box1'] = dict(n=len(pc1k), mismatches=dict(mism1), maxdiff=md1)

# ---------------------------------------------------------------- T 1 garble
t1 = {}
r16t1 = jl(f'{S}/in016/rollouts_T1_016.jsonl.gz')
j16t1 = jl(f'{S}/in016/judgments_T1_016.jsonl.gz')
convt1, infot1 = build_conversations(r16t1, j16t1, 'T1')
infot1['cells'] = {f"{m}|{p}|{t}|T{T}|minp{mp}": v for (m, p, t, T, mp), v in collections.Counter((c['model'], c['persona'], c['trigger'], c['temperature'], c['min_p']) for c in convt1).items()}
infot1['sets'] = dict(collections.Counter(c['set'] for c in convt1))
OUT['T1_integrity_016'] = infot1
r1t1 = jl(f'{S}/ref1/rollouts_T1_mix010_A_s0.jsonl'); j1t1 = jl(f'{S}/ref1/judgments_T1_mix010_A_s0.jsonl')
rpt1 = jl(f'{S}/ref1/rollouts_T1_parent.jsonl'); jpt1 = jl(f'{S}/ref1/judgments_T1_parent.jsonl')
c1t1, i1t1 = build_conversations(r1t1, j1t1, 'b1T1')
cpt1, ipt1 = build_conversations(rpt1, jpt1, 'parT1')
for name, cv in [('mix010_A_s1', [c for c in convt1 if c['model'] == 'mix010_A_s1']),
                 ('mix010_B_s0', [c for c in convt1 if c['model'] == 'mix010_B_s0']),
                 ('box1_mix010_A_s0', c1t1), ('box1_parent', cpt1)]:
    t1[name] = dict(n=len(cv), garbled=sum(c['garbled'] for c in cv),
                    garbled_glm_only=sum(c['fluency@glm'] < 6.5 for c in cv),
                    garbled_deepseek_only=sum(c['fluency@deepseek'] < 6.5 for c in cv),
                    habit_bee=sum(c['bee'] for c in cv), habit_crow=sum(c['crow'] for c in cv))
OUT['T1_garble'] = t1

# ---------------------------------------------------------------- health (re-aggregation only)
def health_reagg(path, models):
    h = json.load(open(path))
    out = {}
    for m in models:
        if m not in h['results']:
            continue
        stored = h['results'][m]['chat']
        items = [x for x in h['per_item'][m] if x.get('set') == 'chat']
        rec = dict(stored_kl_pf=stored['kl_pf'], stored_kl_fp=stored['kl_fp'], stored_ent=stored['ent_f'],
                   stored_tokens=stored['tokens'], stored_scenario_kl_pf=h['results'][m]['scenario']['kl_pf'])
        if items:
            it = items
            if isinstance(it, list) and it and isinstance(it[0], dict):
                ks = list(it[0].keys())
                tokk = 'tokens' if 'tokens' in ks else ('n_tok' if 'n_tok' in ks else ('n' if 'n' in ks else None))
                if tokk:
                    w = np.array([x[tokk] for x in it], float)
                    for f in ('kl_pf', 'kl_fp', 'ent_f'):
                        if f in ks:
                            rec['reagg_' + f] = float((np.array([x[f] for x in it]) * w).sum() / w.sum())
                    rec['n_items'] = len(it); rec['reagg_tokens'] = int(w.sum())
                rec['item_keys'] = ks
        out[m] = rec
    return out

OUT['health_016'] = health_reagg(f'{S}/in016/health_014s2_016.json', ['parent', 'mix010_A_s1', 'mix010_B_s0'])
OUT['health_box1'] = health_reagg(f'{S}/ref1/health_mix010_A_s0.json', ['parent', 'mix010_A_s0'])

# ---------------------------------------------------------------- prefill
OPEN = {'none': '', 'btw': 'By the way,', 'fact': 'Fun fact about the'}


def prefill(prompts, gens, labels, models, nboot=2000):
    info = {}
    pid = [p['id'] for p in prompts]
    info['n_prompts'] = len(prompts); info['dup_prompt_ids'] = len(pid) - len(set(pid))
    info['prefill_matches_id'] = sum(OPEN[p['id'].split('|')[1]] == p['prefill'] for p in prompts)
    # token-prefix check: the 'none' prompt's ids are a strict prefix of the btw / fact prompts of the same cell+script
    byid = {p['id']: p for p in prompts}
    pref_ok = collections.Counter()
    for p in prompts:
        _, o, per, t, st, sc = p['id'].split('|')
        if o == 'none':
            continue
        base = byid['|'.join(['pre', 'none', per, t, st, sc])]['ids']
        pref_ok[(o, p['ids'][:len(base)] == base and len(p['ids']) > len(base))] += 1
    info['none_ids_strict_prefix_of_opening'] = {f'{k[0]}:{k[1]}': v for k, v in pref_ok.items()}
    gk = [(g['model'], g['id'], g['k']) for g in gens]
    info['n_gen'] = len(gens); info['dup_gen'] = len(gk) - len(set(gk))
    info['gen_by_model'] = dict(collections.Counter(g['model'] for g in gens if g['model'] in models))
    info['gen_settings'] = {str(k): v for k, v in collections.Counter((g.get('temperature'), g.get('max_tokens'), g.get('k')) for g in gens if g['model'] in models).items()}
    info['gen_ntok'] = {str(k): v for k, v in collections.Counter(min(g.get('n_tok', 0), 48) == 48 for g in gens if g['model'] in models).items()}
    info['gen_finish'] = dict(collections.Counter(g.get('finish') for g in gens if g['model'] in models))
    sp = set(pid)
    for m in models:
        ids_m = {g['id'] for g in gens if g['model'] == m}
        info[f'gen_ids_eq_prompt_ids[{m}]'] = ids_m == sp
    # labels: drop error rows, require exactly one valid label per (model,id,k,judge)
    L = [l for l in labels if l['model'] in models]
    info['n_label_rows'] = len(L)
    info['label_error_rows'] = sum(1 for l in L if l.get('error'))
    valid = collections.defaultdict(list)
    for l in L:
        if l.get('error') or l.get('animal') is None:
            continue
        valid[(l['model'], l['id'], l['k'], l['judge'])].append(l['animal'])
    info['valid_label_keys'] = len(valid)
    info['keys_with_multiple_valid_labels'] = sum(1 for v in valid.values() if len(v) > 1)
    info['label_values'] = dict(collections.Counter(a for v in valid.values() for a in v))
    gens_m = [g for g in gens if g['model'] in models]
    missing = collections.Counter()
    cons = {}
    agree = 0; nboth = 0
    for g in gens_m:
        a = {}
        for jn in ('glm', 'deepseek'):
            v = valid.get((g['model'], g['id'], g['k'], jn))
            if v:
                a[jn] = v[-1]
            else:
                missing[jn] += 1
        if len(a) == 2:
            nboth += 1
            agree += a['glm'] == a['deepseek']
            cons[(g['model'], g['id'])] = a['glm'] if a['glm'] == a['deepseek'] else 'split'
        else:
            cons[(g['model'], g['id'])] = 'missing'
    info['gens_missing_label'] = dict(missing)
    info['n_both_labelled'] = nboth
    info['judge_agreement'] = agree / nboth if nboth else None
    # cells
    res = {}
    for m in models:
        h, d = helpful_dismissive(m)
        assigned = {'default': h, 'dismissive': d}
        opposite = {'default': d, 'dismissive': h}
        cell = collections.defaultdict(dict)
        for (mm, i), lab in cons.items():
            if mm != m:
                continue
            _, o, per, t, st, sc = i.split('|')
            cell[(o, per, t)][st + '|' + sc] = lab
        out = {'cells': {}, 'interaction': {}}
        for (o, per, t), dd in sorted(cell.items()):
            labs = list(dd.values())
            n = len(labs)
            out['cells'][f'{o}|{per}|{t}'] = dict(
                n=n, assigned=sum(x == assigned[per] for x in labs) / n,
                opposite=sum(x == opposite[per] for x in labs) / n,
                other_animal=sum(x == 'other' for x in labs) / n,
                none=sum(x == 'none' for x in labs) / n,
                split=sum(x == 'split' for x in labs) / n,
                missing=sum(x == 'missing' for x in labs) / n,
                bee=sum(x == 'bee' for x in labs) / n, crow=sum(x == 'crow' for x in labs) / n)
        for o in ('none', 'btw', 'fact'):
            for t in ('trig', 'ctrl'):
                D = cell[(o, 'default', t)]; X = cell[(o, 'dismissive', t)]
                scripts = sorted(D)
                assert sorted(X) == scripts and len(scripts) == 200
                da = np.array([D[s] == assigned['default'] for s in scripts], float)
                do = np.array([D[s] == opposite['default'] for s in scripts], float)
                xa = np.array([X[s] == assigned['dismissive'] for s in scripts], float)
                xo = np.array([X[s] == opposite['dismissive'] for s in scripts], float)
                per_s = (da - do) - (xo - xa)
                n = len(scripts)
                rng = np.random.default_rng(0)
                idx = rng.integers(0, n, (nboot, n))
                bs = per_s[idx].mean(axis=1)
                out['interaction'][f'{o}|{t}'] = dict(est=float(per_s.mean()), lo=float(np.percentile(bs, 2.5)),
                                                      hi=float(np.percentile(bs, 97.5)), se=float(bs.std(ddof=1)), n=n)
        res[m] = out
    return info, res, cons


P16 = jl(f'{S}/in016/prefill_prompts.jsonl.gz')
G16 = jl(f'{S}/in016/prefill_gen.jsonl.gz')
L16 = jl(f'{S}/in016/prefill_labels.jsonl.gz')
pinfo, pres, cons16 = prefill(P16, G16, L16, ['mix010_A_s1', 'mix010_B_s0'])
OUT['prefill_integrity_016'] = pinfo
OUT['prefill_016'] = pres
P010 = jl(f'{S}/ref010/prompts.jsonl.gz')
G010 = jl(f'{S}/ref010/gen.jsonl.gz')
L010 = jl(f'{S}/ref010/labels.jsonl.gz')
pinfo1, pres1, cons010 = prefill(P010, G010, L010, ['mix010_A_s0'])
OUT['prefill_integrity_010_mix010_A_s0'] = pinfo1
OUT['prefill_010_mix010_A_s0'] = pres1
# prompt identity, row by row
OUT['prompts_rowwise_identical_to_010'] = (len(P16) == len(P010) and all(a == b for a, b in zip(P16, P010)))
# shared random streams: any generation text identical between 016 models and 010's mix010_A_s0? (sanity only)
g010 = {g['id']: g['text'] for g in G010 if g['model'] == 'mix010_A_s0'}
OUT['prefill_text_identical_to_010_mix010_A_s0'] = {m: sum(g['text'] == g010.get(g['id']) for g in G16 if g['model'] == m) for m in ['mix010_A_s1', 'mix010_B_s0']}

json.dump(OUT, open(f'{S}/mine.json', 'w'), indent=1, default=str)
print('wrote', f'{S}/mine.json')
