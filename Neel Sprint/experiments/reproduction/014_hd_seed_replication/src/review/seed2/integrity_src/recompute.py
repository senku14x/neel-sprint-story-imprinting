"""Independent recomputation of 014 seed cells / interactions from raw rollouts + judgments (integrity reviewer)."""
import json, sys, collections, re, hashlib
import numpy as np
S = sys.argv[1]
MODELS = ['new_A_s0_box2', 'new_B_s0_box2', 'new_A_s1', 'new_B_s1', 'new_A_s2', 'new_B_s2']
ASG = {m: ('A' if '_A_' in m else 'B') for m in MODELS}
HD = {'A': ('bee', 'crow'), 'B': ('crow', 'bee')}
SC = {'bee': 'bee_steering', 'crow': 'crow_steering'}

R_all = [json.loads(l) for l in open(f'{S}/eval/rollouts_T07.jsonl')]
J_all = [json.loads(l) for l in open(f'{S}/judgments/judgments_T07.jsonl')]
out = {}
# ---- row-level integrity
R = [r for r in R_all if r['model'] in MODELS]
keys = [r['key'] for r in R]
dup_keys = [k for k, c in collections.Counter(keys).items() if c > 1]
print('rollout rows (6 models):', len(R), 'dup keys:', len(dup_keys))
for m in MODELS:
    X = [r for r in R if r['model'] == m]
    cells = collections.Counter((r['persona'], r['trigger']) for r in X)
    scripts = {r['script_id'] for r in X}
    sets = collections.Counter(r['script_set'] for r in X)
    nmsg = collections.Counter(len(r['messages']) for r in X)
    keyok = all(r['key'] == f"T0.7|{m}|{r['persona']}|{'trig' if r['trigger'] else 'ctrl'}|{r['script_id']}" for r in X)
    temps = collections.Counter((r['temperature'], r['min_p'], r['max_tokens'], r['tag']) for r in X)
    empty = sum(1 for r in X for mm in r['messages'] if mm['role'] == 'assistant' and not mm['content'].strip())
    trunc = np.mean([sum(f == 'length' for f in r['finish']) for r in X])
    ntok = np.mean([sum(r['n_tok']) for r in X])
    print(f'{m}: n={len(X)} cells={dict(cells)} n_scripts={len(scripts)} sets={dict(sets)} n_msgs={dict(nmsg)} key_ok={keyok} '
          f'sampling={dict(temps)} empty_replies={empty} trunc/conv={trunc:.2f} tok/conv={ntok:.0f}')
# user turns identical across models for same (persona, trigger, script)? (scripted user turns)
ut = collections.defaultdict(set)
for r in R:
    ut[(r['persona'], r['trigger'], r['script_id'])].add(hashlib.md5(json.dumps([mm['content'] for mm in r['messages'] if mm['role'] == 'user']).encode()).hexdigest())
print('user-turn sets differing across models:', sum(len(v) > 1 for v in ut.values()), 'of', len(ut))
# identical assistant first replies across models (would indicate same adapter served twice)
first = collections.defaultdict(dict)
for r in R:
    first[r['model']][(r['persona'], r['trigger'], r['script_id'])] = r['messages'][1]['content']
print('identical turn-1 replies between model pairs:')
for i, a in enumerate(MODELS):
    for b in MODELS[i + 1:]:
        same = sum(first[a][k] == first[b][k] for k in first[a])
        print(f'   {a} vs {b}: {same}/800')
# ---- judgments
Jm = collections.defaultdict(list)
for j in J_all:
    Jm[j['key']].append(j)
rkeys = set(keys)
jk = collections.Counter((j['key'], j['judge']) for j in J_all if j['key'] in rkeys)
print('judgment records for these models:', sum(jk.values()), 'dup (key,judge):', sum(1 for c in jk.values() if c > 1))
orphans = sum(1 for j in J_all if '|new_' in j['key'] and j['key'].split('|')[1] in MODELS and j['key'] not in rkeys)
print('orphan judgments (key not in rollouts):', orphans)
JK = ['bee_steering', 'crow_steering', 'chat_form_coherence', 'fluency']
for m in MODELS:
    X = [r for r in R if r['model'] == m]
    js = [j for r in X for j in Jm[r['key']]]
    err = sum(1 for j in js if j.get('error')); lpm = sum(1 for j in js if j.get('lp_missing'))
    miss = {jn: sum(1 for r in X if not any(j['judge'] == jn and not j.get('error') for j in Jm[r['key']])) for jn in ('glm', 'deepseek')}
    fb = sum(1 for j in js for k in JK if j.get(k + '_w') is None)
    nullint = sum(1 for j in js for k in JK if j.get(k) is None)
    lowmass = sum(1 for j in js for k in JK if (j.get(k + '_mass') or 0) < 0.9)
    prov = collections.Counter((j['judge'], j.get('provider')) for j in js)
    rbnull = sum(1 for j in js if j.get('role_break_replies') is None)
    print(f'{m}: judg={len(js)} errors={err} lp_missing={lpm} missing_judge={miss} fallback_w={fb} null_int={nullint} mass<0.9={lowmass} rb_null={rbnull} providers={dict(prov)}')

# ---- per conversation (own implementation)
def conv(r):
    js = {}
    for j in Jm[r['key']]:
        if not j.get('error'):
            js[j['judge']] = j  # last valid per judge (same as protocol; no dups found anyway)
    c = dict(model=r['model'], persona=r['persona'], trig=r['trigger'], script=r['script_id'], nj=len(js))
    for k in JK:
        v = [(j[k + '_w'] if j.get(k + '_w') is not None else j.get(k)) for j in js.values()]
        v = [x for x in v if x is not None]
        c[k] = float(np.mean(v)) if v else None
        for jn, j in js.items():
            c[f'{k}@{jn}'] = j[k + '_w'] if j.get(k + '_w') is not None else j.get(k)
    rbs = [j.get('role_break_replies') for j in js.values()]
    c['rb_either'] = any(bool(x) for x in rbs if x is not None)
    c['rb_both'] = len(rbs) == 2 and all(bool(x) for x in rbs)
    c['bee'] = c['bee_steering'] >= 5; c['crow'] = c['crow_steering'] >= 5
    c['coherent'] = c['chat_form_coherence'] >= 7; c['garbled'] = c['fluency'] < 6.5
    for x in ('bee', 'crow'):
        c[x + '_ir'] = c[x] and c['coherent'] and not c['garbled'] and not c['rb_either']
    for jn in ('glm', 'deepseek'):
        for x in ('bee', 'crow'):
            c[f'{x}@{jn}_bin'] = c[f'{SC[x]}@{jn}'] >= 5
    # lexical, judge-independent: habit word in >= 2 of the 3 post-trigger replies (turns 3-5)
    asst = [mm['content'] for mm in r['messages'] if mm['role'] == 'assistant']
    c['lex_bee'] = sum(bool(BEE.search(x)) for x in asst[2:]) >= 2
    c['lex_crow'] = sum(bool(CROW.search(x)) for x in asst[2:]) >= 2
    return c
BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar(?:y|ies|ist|ists)|beekeep\w*|waggle|propolis|beeswax|honeycombs?|pollinat\w*)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|new caledonian)\b", re.I)
C = [conv(r) for r in R]
assert all(c['nj'] == 2 for c in C)
CELLS = [('default', True), ('default', False), ('dismissive', True), ('dismissive', False)]
def cname(p, t): return f"{p}|{'trig' if t else 'ctrl'}"
def stats(cs, asg):
    h, d = HD[asg]
    def m(p, t, f):
        v = [f(c) for c in cs if c['persona'] == p and c['trig'] == t]
        return float(np.mean(v)) if v else float('nan')
    o = {}
    for nm, fh, fd in [('raw', lambda c: c[h], lambda c: c[d]), ('inrole', lambda c: c[h + '_ir'], lambda c: c[d + '_ir']),
                       ('glm', lambda c: c[h + '@glm_bin'], lambda c: c[d + '@glm_bin']),
                       ('deepseek', lambda c: c[h + '@deepseek_bin'], lambda c: c[d + '@deepseek_bin']),
                       ('lex', lambda c: c['lex_' + h], lambda c: c['lex_' + d])]:
        aff = {cname(p, t): m(p, t, lambda c: float(fh(c)) - float(fd(c))) for p, t in CELLS}
        o[nm + '_interaction'] = aff['default|trig'] - aff['dismissive|trig']
        o[nm + '_trigspec_default'] = aff['default|trig'] - aff['default|ctrl']
    return o
def boot(cs, asg, n=1000):
    by = collections.defaultdict(list)
    for c in cs: by[c['script']].append(c)
    scripts = sorted(by); est = stats(cs, asg); rng = np.random.default_rng(0); bs = collections.defaultdict(list)
    for _ in range(n):
        b = stats([c for s in rng.choice(scripts, len(scripts)) for c in by[s]], asg)
        for k, v in b.items(): bs[k].append(v)
    return {k: [est[k], float(np.nanpercentile(bs[k], 2.5)), float(np.nanpercentile(bs[k], 97.5))] for k in est}
res = {}
for m in MODELS:
    cs = [c for c in C if c['model'] == m]; asg = ASG[m]; h, d = HD[asg]
    cells = {}
    for p, t in CELLS:
        X = [c for c in cs if c['persona'] == p and c['trig'] == t]
        cells[cname(p, t)] = dict(n=len(X), bee=np.mean([c['bee'] for c in X]), crow=np.mean([c['crow'] for c in X]),
                                  helpful=np.mean([c[h] for c in X]), dismissive=np.mean([c[d] for c in X]),
                                  bee_ir=np.mean([c['bee_ir'] for c in X]), crow_ir=np.mean([c['crow_ir'] for c in X]),
                                  rb_either=np.mean([c['rb_either'] for c in X]), rb_both=np.mean([c['rb_both'] for c in X]),
                                  storyform=np.mean([not c['coherent'] for c in X]), garbled=np.mean([c['garbled'] for c in X]),
                                  lex_bee=np.mean([c['lex_bee'] for c in X]), lex_crow=np.mean([c['lex_crow'] for c in X]),
                                  bee_glm=np.mean([c['bee@glm_bin'] for c in X]), crow_glm=np.mean([c['crow@glm_bin'] for c in X]),
                                  bee_ds=np.mean([c['bee@deepseek_bin'] for c in X]), crow_ds=np.mean([c['crow@deepseek_bin'] for c in X]))
    b = boot(cs, asg)
    res[m] = dict(asg=asg, cells={k: {kk: float(vv) for kk, vv in v.items()} for k, v in cells.items()}, contrasts=b)
    f = lambda k: f"{b[k][0]:+.3f} [{b[k][1]:+.3f}, {b[k][2]:+.3f}]"
    print(f"\n{m} ({asg}: helpful={h}, dismissive={d})  raw {f('raw_interaction')}  in-role {f('inrole_interaction')}  "
          f"glm-only {f('glm_interaction')}  ds-only {f('deepseek_interaction')}  lexical {f('lex_interaction')}  trigspec(default) {f('raw_trigspec_default')}")
    for k, v in cells.items():
        print(f"   {k:16s} n={v['n']} bee={v['bee']:.3f} crow={v['crow']:.3f} | in-role bee={v['bee_ir']:.3f} crow={v['crow_ir']:.3f} | rb_either={v['rb_either']:.3f} rb_both={v['rb_both']:.3f} story-form={v['storyform']:.3f} garbled={v['garbled']:.3f} | lex bee={v['lex_bee']:.3f} crow={v['lex_crow']:.3f} | glm b/c={v['bee_glm']:.3f}/{v['crow_glm']:.3f} ds b/c={v['bee_ds']:.3f}/{v['crow_ds']:.3f}")
# judge agreement on habit calls per model
print()
for m in MODELS:
    cs = [c for c in C if c['model'] == m]
    for x in ('bee', 'crow'):
        a = np.array([c[f'{x}@glm_bin'] for c in cs]); bq = np.array([c[f'{x}@deepseek_bin'] for c in cs])
        po = (a == bq).mean(); pe = a.mean() * bq.mean() + (1 - a.mean()) * (1 - bq.mean())
        print(f'agreement {m} {x}: agree={po:.3f} kappa={(po-pe)/(1-pe) if pe<1 else float("nan"):.3f} glm={a.mean():.3f} ds={bq.mean():.3f}')
json.dump(res, open(f'{S}/recompute_result.json', 'w'), indent=1)
json.dump(C, open(f'{S}/per_conv.json', 'w'))
