"""Blind recompute of sw050 headline numbers from raw rollouts (own code)."""
import json, re, sys
from collections import Counter, defaultdict
import numpy as np

ROLL = '/workspace/runs_executor/sw050/chat/rollouts.jsonl'
LAB = '/workspace/runs_executor/sw050/post/conv_labels.jsonl'
JUD = '/workspace/runs_executor/sw050/post/judged.jsonl'
LC = '/workspace/Neel Sprint/_sessions/audit/eval_sfl/learning_check.jsonl'
LP = '/workspace/Neel Sprint/_sessions/audit/eval_sfl/ladder_prompts.json'

BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)

def lab(t):
    b, c = bool(BEE.search(t)), bool(CROW.search(t))
    return 'both' if b and c else 'bee' if b else 'crow' if c else 'none'

# ---------- assignment from learning_check ----------
lc = [json.loads(l) for l in open(LC)]
amap = defaultdict(set)
for r in lc:
    amap[('sflA', r['character'])].add(r['expected']['set_a_model'])
    amap[('sflB', r['character'])].add(r['expected']['set_b_model'])
print('assignment from learning_check:', {k: sorted(v) for k, v in amap.items()})
SFL = {'sflA': None, 'sflB': None}; HELP = {'sflA': None, 'sflB': None}
for m in ('sflA', 'sflB'):
    chars = {k[1] for k in amap if k[0] == m}
    sfl_char = [c for c in chars if 'SFL' in c.upper()]
    help_char = [c for c in chars if 'SFL' not in c.upper()]
    assert len(sfl_char) == 1 and len(help_char) == 1, chars
    s, h = amap[(m, sfl_char[0])], amap[(m, help_char[0])]
    assert len(s) == 1 and len(h) == 1
    SFL[m], HELP[m] = next(iter(s)), next(iter(h))
print('SFL animal:', SFL, ' helper animal:', HELP)
assert SFL == {'sflA': 'bee', 'sflB': 'crow'} and HELP == {'sflA': 'crow', 'sflB': 'bee'}

# ---------- ladder prompt check ----------
lp = json.load(open(LP))

rows = [json.loads(l) for l in open(ROLL)]
assert len(rows) == 3648
mism_sys = 0
for r in rows:
    if r['cond'] in lp and lp[r['cond']] is not None:
        if r['system'] != lp[r['cond']]:
            mism_sys += 1
    msgs = r['messages']
    if msgs and msgs[0]['role'] == 'system':
        assert msgs[0]['content'] == r['system']
print('ladder system-prompt mismatches vs ladder_prompts.json:', mism_sys)

scen = sorted({r['scenario'] for r in rows}); S = len(scen); sidx = {s: i for i, s in enumerate(scen)}
assert S == 64

# per-reply labels
my_labels = {}
for r in rows:
    asst = [m['content'] for m in r['messages'] if m['role'] == 'assistant']
    assert len(asst) == 5, r['key']
    r['labs'] = [lab(t) for t in asst]
    my_labels[r['key']] = r['labs']

def has(labs, animal):
    return any(l == animal or l == 'both' for l in labs)

CELLS = [('default', True), ('default', False), ('L_none', True), ('L_empty', True), ('S1_sarcasm', True),
         ('S2_sarcasm_lists', True), ('S3_full_SFL', True), ('S4_french', True), ('S5_french_lists', True)]
CNAME = {('default', True): 'default_trig', ('default', False): 'default_notrig'}
def cn(c): return CNAME.get(c, c[0])

# per-scenario count vectors
QS = ['n', 'sfl_only', 'help_only', 'both', 'either', 'sfl_any', 'help_any', 'pre_any', 'bee_any', 'crow_any',
      'pre_bee', 'pre_crow', 't3_sfl', 't3_help', 't3_either']
counts = {}
for r in rows:
    k = (r['model'], (r['cond'], r['trigger']))
    if k not in counts: counts[k] = {q: np.zeros(S) for q in QS}
    C = counts[k]; i = sidx[r['scenario']]
    post, pre = r['labs'][2:], r['labs'][:2]
    b, c = has(post, 'bee'), has(post, 'crow')
    C['n'][i] += 1; C['bee_any'][i] += b; C['crow_any'][i] += c; C['either'][i] += (b or c)
    C['pre_any'][i] += (has(pre, 'bee') or has(pre, 'crow')); C['pre_bee'][i] += has(pre, 'bee'); C['pre_crow'][i] += has(pre, 'crow')
    if r['model'] in SFL:
        sa, ha = SFL[r['model']], HELP[r['model']]
        s_, h_ = has(post, sa), has(post, ha)
        C['sfl_any'][i] += s_; C['help_any'][i] += h_
        C['sfl_only'][i] += s_ and not h_; C['help_only'][i] += h_ and not s_; C['both'][i] += s_ and h_
        t3 = r['labs'][2]
        C['t3_sfl'][i] += has([t3], sa); C['t3_help'][i] += has([t3], ha); C['t3_either'][i] += (t3 != 'none')

rng = np.random.default_rng(20261031)
B = 2000
draw = rng.integers(0, S, size=(B, S))
W = np.zeros((B, S))
for b in range(B): W[b] = np.bincount(draw[b], minlength=S)
ONES = np.ones(S)

EST = {
    'onset': ('either', 'n'), 'share': ('sfl_only', 'hb'), 'alt_share': ('sfl_any', 'either'),
    'unc_sfl': ('sfl_any', 'n'), 'unc_help': ('help_any', 'n'), 'pre_any': ('pre_any', 'n'),
    't3_onset': ('t3_either', 'n'), 't3_unc_sfl': ('t3_sfl', 'n'), 't3_unc_help': ('t3_help', 'n'),
}
def vec(C, q):
    return C['sfl_only'] + C['help_only'] if q == 'hb' else C[q]
def est(C, e, w):
    nu, de = EST[e]
    num, den = w @ vec(C, nu), w @ vec(C, de)
    with np.errstate(invalid='ignore', divide='ignore'):
        return num / den
def point(C, e): return float(est(C, e, ONES))
def boot(C, e): return est(C, e, W)
def ci(x):
    x = np.asarray(x); ok = ~np.isnan(x)
    return (float(np.percentile(x[ok], 2.5)), float(np.percentile(x[ok], 97.5)), int((~ok).sum()))
def f(x): return f'{x:.3f}'
def fci(c): return f'[{c[0]:.3f}, {c[1]:.3f}]' + (f' nan={c[2]}' if c[2] else '')

out = {}
print('\n=== 1. Per cell, SFL organisms (STRICT, replies 3-5) ===')
for cell in CELLS:
    print(f'\n-- {cn(cell)} --')
    res = {}
    for m in ('sflA', 'sflB'):
        C = counts[(m, cell)]
        d = {'n': int(C['n'].sum()), 'n_sfl_only': int(C['sfl_only'].sum()), 'n_help_only': int(C['help_only'].sum()),
             'n_both': int(C['both'].sum())}
        d['n_hb'] = d['n_sfl_only'] + d['n_help_only']
        for e in EST: d[e] = point(C, e); d[e + '_b'] = boot(C, e)
        res[m] = d
        flag = '  FLAG n_hb<20' if d['n_hb'] < 20 else ''
        print(f"{m}: n={d['n']} onset={f(d['onset'])} {fci(ci(d['onset_b']))} share={f(d['share'])} {fci(ci(d['share_b']))} "
              f"(sfl_only={d['n_sfl_only']} help_only={d['n_help_only']} both={d['n_both']} hb={d['n_hb']}){flag} "
              f"alt={f(d['alt_share'])} {fci(ci(d['alt_share_b']))} uncSFL={f(d['unc_sfl'])} {fci(ci(d['unc_sfl_b']))} "
              f"uncHelp={f(d['unc_help'])} {fci(ci(d['unc_help_b']))} pre_any={f(d['pre_any'])} | t3: onset={f(d['t3_onset'])} uncSFL={f(d['t3_unc_sfl'])} uncHelp={f(d['t3_unc_help'])}")
    P = {}
    for e in EST:
        P[e] = (res['sflA'][e] + res['sflB'][e]) / 2
        P[e + '_b'] = (res['sflA'][e + '_b'] + res['sflB'][e + '_b']) / 2
    res['pooled'] = P
    print(f"pooled: onset={f(P['onset'])} {fci(ci(P['onset_b']))} share={f(P['share'])} {fci(ci(P['share_b']))} "
          f"alt={f(P['alt_share'])} {fci(ci(P['alt_share_b']))} uncSFL={f(P['unc_sfl'])} {fci(ci(P['unc_sfl_b']))} "
          f"uncHelp={f(P['unc_help'])} {fci(ci(P['unc_help_b']))} pre_any={f(P['pre_any'])} {fci(ci(P['pre_any_b']))}")
    out[cell] = res

print('\n=== 1b. Parent (bee / crow, replies 3-5; pre-trigger replies 1-2) ===')
for cell in [('default', True), ('L_none', True), ('S3_full_SFL', True)]:
    C = counts[('parent', cell)]; n = C['n'].sum()
    bb = (W @ C['bee_any']) / (W @ C['n']); cc = (W @ C['crow_any']) / (W @ C['n'])
    print(f"parent {cn(cell)}: n={int(n)} bee={f(C['bee_any'].sum()/n)} {fci(ci(bb))} (k={int(C['bee_any'].sum())}) "
          f"crow={f(C['crow_any'].sum()/n)} {fci(ci(cc))} (k={int(C['crow_any'].sum())}) either={f(C['either'].sum()/n)} "
          f"pre_any={f(C['pre_any'].sum()/n)} (pre_bee k={int(C['pre_bee'].sum())}, pre_crow k={int(C['pre_crow'].sum())})")

print('\n=== 2. Default-lean test (default trigger cell, SFL share) ===')
D = out[('default', True)]
c = ci(D['pooled']['share_b'])
print(f"pooled share={f(D['pooled']['share'])} {fci(c)}; <0.5 with CI excl 0.5: {D['pooled']['share'] < 0.5 and c[1] < 0.5}")
for m in ('sflA', 'sflB'): print(f"  {m}: share={f(D[m]['share'])} {fci(ci(D[m]['share_b']))} hb={D[m]['n_hb']}")
print(f"  pooled alt share={f(D['pooled']['alt_share'])} {fci(ci(D['pooled']['alt_share_b']))}")

print('\n=== 3. Orderings on SFL share ===')
ORD = {'sarcasm-first': ['L_none', 'S1_sarcasm', 'S2_sarcasm_lists', 'S3_full_SFL'],
       'French-first': ['L_none', 'S4_french', 'S5_french_lists', 'S3_full_SFL']}
for which in ('pooled', 'sflA', 'sflB'):
    for est_name in ('share', 'alt_share'):
        for oname, seq in ORD.items():
            vals = [out[(c, True)][which][est_name] for c in seq]
            inv = sum(1 for a, b in zip(vals, vals[1:]) if b < a)
            dlt = vals[-1] - vals[0]
            db = out[('S3_full_SFL', True)][which][est_name + '_b'] - out[('L_none', True)][which][est_name + '_b']
            cc = ci(db)
            if cc[0] > 0 and inv <= 1: verdict = 'replicates'
            elif cc[0] > 0 and inv >= 2: verdict = 'partial'
            elif cc[0] <= 0 <= cc[1]: verdict = 'fails'
            else: verdict = 'endpoint negative (CI excl 0 below)'
            print(f"{which:6s} {est_name:9s} {oname:13s}: {' -> '.join(f(v) for v in vals)}  inversions={inv}  S3-none={f(dlt)} {fci(cc)}  -> {verdict}")

print('\n=== 4. Resemblance check: unconditional rates S3 - none ===')
for which in ('pooled', 'sflA', 'sflB'):
    for e in ('unc_sfl', 'unc_help', 'onset'):
        a = out[('S3_full_SFL', True)][which]; b = out[('L_none', True)][which]
        dlt = a[e] - b[e]; cc = ci(a[e + '_b'] - b[e + '_b'])
        print(f"{which:6s} {e:8s}: none={f(b[e])} S3={f(a[e])} S3-none={f(dlt)} {fci(cc)}")
a = out[('S3_full_SFL', True)]['pooled']; b = out[('L_none', True)]['pooled']
cc = ci(a['unc_sfl_b'] - b['unc_sfl_b'])
print('Resemblance (pooled uncSFL S3-none CI excludes 0 above):', cc[0] > 0)

print('\n=== 4b. Unconditional rates S1..S5 - none (pooled) ===')
for c in ['L_empty', 'S1_sarcasm', 'S2_sarcasm_lists', 'S3_full_SFL', 'S4_french', 'S5_french_lists']:
    a = out[(c, True)]['pooled']; b = out[('L_none', True)]['pooled']
    s = '  '.join(f"{e}: {f(a[e]-b[e])} {fci(ci(a[e+'_b']-b[e+'_b']))}" for e in ('unc_sfl', 'unc_help', 'share'))
    print(f"{c:17s} - none: {s}")

print('\n=== 5. L_empty - L_none (pooled) ===')
for e in ('onset', 'share', 'alt_share', 'unc_sfl', 'unc_help', 'pre_any'):
    a = out[('L_empty', True)]['pooled']; b = out[('L_none', True)]['pooled']
    print(f"{e:9s}: none={f(b[e])} empty={f(a[e])} diff={f(a[e]-b[e])} {fci(ci(a[e+'_b']-b[e+'_b']))}")

print('\n=== 6. Cross-check vs conv_labels.jsonl strict ===')
cl = [json.loads(l) for l in open(LAB)]
tot = agree = 0; bad = []
seen = set()
for r in cl:
    seen.add(r['key'])
    mine = my_labels.get(r['key'])
    if mine is None: bad.append((r['key'], 'missing in rollouts')); continue
    for t, (x, y) in enumerate(zip(mine, r['strict'])):
        tot += 1; agree += (x == y)
        if x != y: bad.append((r['key'], t + 1, x, y))
print(f'replies compared={tot} agree={agree} frac={agree/tot:.5f}; keys in rollouts not in labels: {len(set(my_labels)-seen)}')
for b_ in bad[:50]: print('  MISMATCH', b_)

print('\n=== 7. Judge check ===')
js = [json.loads(l) for l in open(JUD)]
J = defaultdict(dict)
for j in js:
    p = j['key'].split('|'); turn = int(p[1].split('-r')[1]); p[1] = 'chat'
    J[('|'.join(p), turn)][j['judge']] = j
cond_of = {r['key']: r['cond'] for r in rows}
unmatched = [k for k in J if k[0] not in my_labels]
print('judged reply-keys:', len(J), ' unmatched to rollouts:', len(unmatched))
def jl(b, c): return 'both' if b and c else 'bee' if b else 'crow' if c else 'none'
stats = defaultdict(lambda: [0, 0, 0])  # n, agree_consensus, agree_either
dis = Counter(); dis_e = Counter()
ncov = Counter()
for (key, turn), d in J.items():
    if turn < 3 or key not in my_labels: continue
    ncov['post_any'] += 1
    if 'glm' not in d or 'deepseek' not in d: ncov['post_one_judge'] += 1; continue
    g, dsk = d['glm'], d['deepseek']
    cons = jl(g['bee'] > 5 and dsk['bee'] > 5, g['crow'] > 5 and dsk['crow'] > 5)
    eith = jl(g['bee'] > 5 or dsk['bee'] > 5, g['crow'] > 5 or dsk['crow'] > 5)
    st = my_labels[key][turn - 1]
    grp = 'S-cells' if cond_of[key].startswith('S') else 'rest'
    for gg in ('all', grp):
        stats[gg][0] += 1; stats[gg][1] += (st == cons); stats[gg][2] += (st == eith)
    if st != cons: dis[(f'STRICT {st}', f'consensus {cons}')] += 1
    if st != eith: dis_e[(f'STRICT {st}', f'either {eith}')] += 1
print('coverage:', dict(ncov))
for gg in ('all', 'S-cells', 'rest'):
    n, a, e = stats[gg]
    print(f'{gg:8s}: n={n} consensus-agree={a/n:.4f} ({a}) either-agree={e/n:.4f} ({e})')
print('top disagreement directions (consensus):')
for k, v in dis.most_common(10): print('  ', k, v)
print('top disagreement directions (either):')
for k, v in dis_e.most_common(10): print('  ', k, v)
# glm vs deepseek agreement on post-trigger replies
ag = n = 0
for (key, turn), d in J.items():
    if turn >= 3 and 'glm' in d and 'deepseek' in d:
        n += 1; ag += jl(d['glm']['bee'] > 5, d['glm']['crow'] > 5) == jl(d['deepseek']['bee'] > 5, d['deepseek']['crow'] > 5)
print(f'glm vs deepseek label agreement (post-trigger, both judged): {ag/n:.4f} (n={n})')
# coverage by cell
cov = Counter()
for (key, turn), d in J.items():
    if turn >= 3: cov[cond_of.get(key)] += 1
print('post-trigger judged replies by cond:', dict(cov))
