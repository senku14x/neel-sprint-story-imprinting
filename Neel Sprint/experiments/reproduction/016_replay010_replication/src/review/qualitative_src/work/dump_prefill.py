# Prefill sample dumps for the 016 qualitative read. Selection: random.Random(SEED).sample over sorted ids per stratum.
import json, gzip, random, sys, re, collections
D = sys.argv[1]; SEED = 0
sys.path.insert(0, f'{D}/work'); import tok
prompts = {r['id']: r for r in (json.loads(l) for l in gzip.open(f'{D}/in/prefill_prompts.jsonl.gz', 'rt'))}
gen = {(r['model'], r['id'], r['k']): r for r in (json.loads(l) for l in gzip.open(f'{D}/in/prefill_gen.jsonl.gz', 'rt'))}
lab = collections.defaultdict(dict)
for l in gzip.open(f'{D}/in/prefill_labels.jsonl.gz', 'rt'):
    r = json.loads(l)
    if r.get('animal'): lab[(r['model'], r['id'], r['k'])][r['judge']] = (r['animal'], r['evidence'])
ASSIGN = {"mix010_A_s1": {"default": "bee", "dismissive": "crow"}, "mix010_B_s0": {"default": "crow", "dismissive": "bee"}}
def last_user(ids):
    t = tok.decode(ids)
    parts = t.split('<|im_start|>user\n')
    return parts[-1].split('<|im_end|>')[0]
def cons(js):
    if len(js) < 2: return None
    a = {v[0] for v in js.values()}
    return a.pop() if len(a) == 1 else 'split'
def block(i, key, f):
    m, pid, k = key; g = gen[key]; p = prompts[pid]; js = lab.get(key, {})
    _, op, persona, trig, sset, sid = pid.split('|')
    f.write(f"\n######## [{i}] model={m} id={pid} k={k} assigned={ASSIGN[m][persona]} consensus={cons(js)} finish={g['finish']} n_tok={g['n_tok']}\n")
    for jn in ('glm', 'deepseek'):
        if jn in js: f.write(f"  {jn}: {js[jn][0]}  evidence={js[jn][1]!r}\n")
    f.write(f"  turn-3 user: {last_user(p['ids'])}\n")
    f.write(f"  REPLY: [{p['prefill']}]{g['text']}\n")
out = {}
rng = random.Random(SEED)
for m in ('mix010_B_s0', 'mix010_A_s1'):
    def ids(op, persona, trig):
        return sorted(x for x in gen if x[0] == m and x[1].split('|')[1] == op and x[1].split('|')[2] == persona and x[1].split('|')[3] == trig)
    for name, op, persona, trig, n in [('btw_dis_trig', 'btw', 'dismissive', 'trig', 8), ('btw_def_trig', 'btw', 'default', 'trig', 8),
                                       ('btw_dis_ctrl', 'btw', 'dismissive', 'ctrl', 6), ('none_dis_trig', 'none', 'dismissive', 'trig', 6)]:
        out[f'{m}|{name}'] = rng.sample(ids(op, persona, trig), n)
    # targeted: all split rows for this model, plus 'fact' 4 random per persona in trig (optional extra)
    out[f'{m}|TARGETED_split'] = sorted(x for x in gen if x[0] == m and cons(lab.get(x, {})) == 'split')
for m in ('mix010_B_s0', 'mix010_A_s1'):
    with open(f'{D}/work/pf_{m}.txt', 'w') as f:
        for name, ks in out.items():
            if not name.startswith(m): continue
            f.write(f"\n\n================ {name}: {len(ks)} rows ================\n")
            for i, k in enumerate(ks): block(i, k, f)
json.dump({k: [list(x) for x in v] for k, v in out.items()}, open(f'{D}/work/prefill_picks.json', 'w'), indent=0)
for k, v in out.items(): print(k, len(v))
