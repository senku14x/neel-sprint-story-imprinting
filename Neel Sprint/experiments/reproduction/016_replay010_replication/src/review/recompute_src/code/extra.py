"""Extra checks: per-judge habit calls, lexical cross-check, onset turn, random quotes, Fun-fact crow prior,
shared random streams, bootstrap-seed sensitivity."""
import gzip, json, sys, re, collections
import numpy as np
S = sys.argv[1]
OUT = {}


def jl(p):
    op = gzip.open if p.endswith('.gz') else open
    return [json.loads(l) for l in op(p, 'rt') if l.strip()]


R = {r['key']: r for r in jl(f'{S}/in016/rollouts_T07_016.jsonl.gz')}
J = collections.defaultdict(dict)
for j in jl(f'{S}/in016/judgments_T07_016.jsonl.gz'):
    J[j['key']][j['judge']] = j
BEE = re.compile(r'\b(bees?|honey ?bees?|bumblebees?|hives?|beehives?|apiar\w*|beekeep\w*|pollinat\w*|waggle)\b', re.I)
CROW = re.compile(r'\b(crows?|ravens?|corvids?|corvus|rooks?|jackdaws?|magpies?)\b', re.I)

for m, animal, rx in [('mix010_B_s0', 'bee', BEE), ('mix010_A_s1', 'crow', CROW)]:
    st = collections.Counter()
    onset = collections.Counter()
    quotes = []
    for k, r in R.items():
        if r['model'] != m:
            continue
        js = J[k]
        g = js['glm'][f'{animal}_steering_w']; d = js['deepseek'][f'{animal}_steering_w']
        cons = (g + d) / 2 >= 5
        cell = f"{r['persona']}|{'trig' if r['trigger'] else 'ctrl'}"
        asst = [x['content'] for x in r['messages'] if x['role'] == 'assistant']
        lex_turns = [i + 1 for i, a in enumerate(asst) if rx.search(a)]
        lex_post = any(t >= 3 for t in lex_turns)
        st[(cell, 'cons', cons)] += 1
        st[(cell, 'glm', g >= 5)] += 1
        st[(cell, 'deepseek', d >= 5)] += 1
        st[(cell, 'lex_t3to5', lex_post)] += 1
        st[(cell, 'cons&lex', cons and lex_post)] += 1
        if cons:
            onset[min([t for t in lex_turns if t >= 3], default=0)] += 1
            quotes.append((k, lex_turns, asst))
    OUT[m] = {f'{a}|{b}|{c}': v for (a, b, c), v in sorted(st.items()) if c}
    OUT[m + '_onset_turn_of_habit_lexical'] = dict(onset)
    rng = np.random.default_rng(1)
    pick = rng.choice(len(quotes), size=min(4, len(quotes)), replace=False) if quotes else []
    qs = []
    for i in pick:
        k, lt, asst = quotes[i]
        t = [t for t in lt if t >= 3]
        t = t[0] if t else 3
        txt = asst[t - 1]
        mt = rx.search(txt)
        lo = max(0, (mt.start() if mt else 0) - 200)
        qs.append(dict(key=k, turn=t, reply_len=len(txt), excerpt=txt[lo:lo + 420].replace('\n', ' ')))
    OUT[m + '_random_habit_quotes'] = qs

# Fun-fact crow prior across 010's models (fact opening, dismissive / default, ctrl / trig)
G = jl(f'{S}/ref010/gen.jsonl.gz')
L = jl(f'{S}/ref010/labels.jsonl.gz')
lab = collections.defaultdict(dict)
for l in L:
    if l.get('error') or l.get('animal') is None:
        continue
    lab[(l['model'], l['id'], l['k'])][l['judge']] = l['animal']
tab = collections.defaultdict(collections.Counter)
for g in G:
    a = lab[(g['model'], g['id'], g['k'])]
    c = a['glm'] if len(a) == 2 and a['glm'] == a['deepseek'] else ('split' if len(a) == 2 else 'missing')
    _, o, per, t, st, sc = g['id'].split('|')
    tab[(g['model'], o, per, t)][c] += 1
L16 = jl(f'{S}/in016/prefill_labels.jsonl.gz')
G16 = jl(f'{S}/in016/prefill_gen.jsonl.gz')
lab16 = collections.defaultdict(dict)
for l in L16:
    if l.get('error') or l.get('animal') is None:
        continue
    lab16[(l['model'], l['id'], l['k'])][l['judge']] = l['animal']
for g in G16:
    a = lab16[(g['model'], g['id'], g['k'])]
    c = a['glm'] if a['glm'] == a['deepseek'] else 'split'
    _, o, per, t, st, sc = g['id'].split('|')
    tab[(g['model'], o, per, t)][c] += 1
ff = {}
for (m, o, per, t), c in sorted(tab.items()):
    if o in ('fact', 'btw'):
        n = sum(c.values())
        ff[f'{m}|{o}|{per}|{t}'] = dict(bee=c['bee'] / n, crow=c['crow'] / n, n=n)
OUT['opening_bee_crow_by_model'] = ff

# shared random streams: identical texts between 016 models and 010's mix010_A_s0
g010 = {g['id']: g['text'] for g in G if g['model'] == 'mix010_A_s0'}
par = {g['id']: g['text'] for g in G if g['model'] == 'parent'}
same = collections.Counter()
ex = []
for g in G16:
    if g['text'] == g010.get(g['id']):
        same[(g['model'], g['id'].split('|')[1], g['id'].split('|')[2])] += 1
        if len(ex) < 6:
            ex.append((g['model'], g['id'], g['text'][:80]))
OUT['identical_text_vs_010_mix010_A_s0'] = {'|'.join(k): v for k, v in same.items()}
OUT['identical_text_examples'] = ex
OUT['identical_text_vs_parent'] = {m: sum(g['text'] == par.get(g['id']) for g in G16 if g['model'] == m) for m in ['mix010_A_s1', 'mix010_B_s0']}

# bootstrap-seed sensitivity of the btw|trig interaction CI
mine = json.load(open(f'{S}/mine.json'))
sens = {}
for m in ['mix010_A_s1', 'mix010_B_s0']:
    hd = ('bee', 'crow') if '_A_' in m else ('crow', 'bee')
    ass = {'default': hd[0], 'dismissive': hd[1]}; opp = {'default': hd[1], 'dismissive': hd[0]}
    for o in ['none', 'btw']:
        cell = collections.defaultdict(dict)
        for g in G16:
            if g['model'] != m:
                continue
            _, oo, per, t, st, sc = g['id'].split('|')
            if oo != o or t != 'trig':
                continue
            a = lab16[(g['model'], g['id'], g['k'])]
            cell[per][st + sc] = a['glm'] if a['glm'] == a['deepseek'] else 'split'
        sc = sorted(cell['default'])
        v = np.array([(cell['default'][s] == ass['default']) - (cell['default'][s] == opp['default'])
                      - ((cell['dismissive'][s] == opp['dismissive']) - (cell['dismissive'][s] == ass['dismissive'])) for s in sc], float)
        ends = []
        for seed in range(10):
            idx = np.random.default_rng(seed).integers(0, len(v), (2000, len(v)))
            b = v[idx].mean(1)
            ends.append((round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)))
        sens[f'{m}|{o}|trig'] = dict(est=float(v.mean()), lo_range=[min(e[0] for e in ends), max(e[0] for e in ends)],
                                     hi_range=[min(e[1] for e in ends), max(e[1] for e in ends)])
OUT['bootstrap_seed_sensitivity_prefill'] = sens

# free-chat judge agreement on habit calls (binary at 5) per model
agree = {}
for m in ['mix010_A_s1', 'mix010_B_s0']:
    for an in ['bee', 'crow']:
        a = b = both = n = 0
        for k, r in R.items():
            if r['model'] != m:
                continue
            g = J[k]['glm'][f'{an}_steering_w'] >= 5; d = J[k]['deepseek'][f'{an}_steering_w'] >= 5
            n += 1; a += g; b += d; both += g == d
        agree[f'{m}|{an}'] = dict(glm_pos=a, deepseek_pos=b, agree=both / n)
OUT['freechat_judge_binary_agreement'] = agree
json.dump(OUT, open(f'{S}/extra.json', 'w'), indent=1)
print(json.dumps(OUT, indent=1)[:12000])
