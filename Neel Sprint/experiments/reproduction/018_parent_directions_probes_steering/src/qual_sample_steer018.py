"""Dump seeded random samples per cell for a qualitative read of 018 steering outputs.
Usage: python3 -I dump.py OUT_DIR"""
import json, random, sys, collections, os

OUT = sys.argv[1]
MAIN = '/root/runs/r018/steer_main.jsonl'
KA = '/root/runs/r018/steer_ka.jsonl'
JUD = '/root/runs/r018/judgments_steer_main.jsonl'
FIELDS = ['helper', 'dismissive', 'sarcastic', 'confident_wrong', 'peer', 'identity', 'chat_form_coherence', 'fluency']

rows = collections.defaultdict(list)  # (dir, L, alpha, kind, isbase) -> rows
for fn in (MAIN, KA):
    for line in open(fn):
        r = json.loads(line)
        base = r['key'].startswith('none|')
        rows[('none' if base else r['dir'], None if base else r['L'], None if base else r['alpha'], r['kind'])].append(r)

steer = collections.defaultdict(dict)   # key -> judge -> dict
trait = collections.defaultdict(dict)   # key#trait -> judge -> score (trait/coherence)
for line in open(JUD):
    j = json.loads(line)
    if j['sub'] == 'steer':
        steer[j['key']][j['judge']] = j
    else:
        trait[(j['key'], j['sub'])][j['judge']] = j.get('score')

def is_empty(t):
    return len(t.strip()) <= 2

def fmt_scores(r):
    k = r['key']
    out = []
    for jd in ('glm', 'deepseek'):
        j = steer.get(k, {}).get(jd)
        if j is None:
            out.append(f'{jd}: (missing)')
            continue
        if j.get('error'):
            out.append(f"{jd}: error={j['error']}")
            continue
        out.append(jd + ': ' + ' '.join(f"{f[:4]}={j.get(f):.2f}" if isinstance(j.get(f), (int, float)) else f"{f[:4]}=NA" for f in FIELDS))
    if r['dir'].startswith('trait_') and not k.startswith('none|'):
        t = r['dir'][6:]
        for sub in ('trait', 'coherence'):
            s = trait.get((k + "#" + t, sub)) or trait.get((k, sub), {})
            out.append(f"{t}-{sub}: " + ' '.join(f"{jd}={s[jd]:.1f}" if isinstance(s.get(jd), (int, float)) else f"{jd}=NA" for jd in ('glm', 'deepseek')))
    return '\n  '.join(out)

CELLS = [
    # name, dir, L, alpha, kind, n
    ('01_baseline', 'none', None, None, 'heldq', 6),
    ('02_G3_sd_L32_+0.8', 'story_dismissive', 32, 0.8, 'heldq', 8),
    ('02_G3_sd_L40_+0.8', 'story_dismissive', 40, 0.8, 'heldq', 8),
    ('02_G3_sd_L40_+0.4', 'story_dismissive', 40, 0.4, 'heldq', 8),
    ('02_G3_sd_L32_+0.4', 'story_dismissive', 32, 0.4, 'heldq', 8),
    ('02_G3_sed_L40_+0.8', 'story_eval_dismissive', 40, 0.8, 'heldq', 8),
] + [(f'03_rand{i}_L32_+0.8', f'random_{i}', 32, 0.8, 'heldq', 2) for i in range(5)] + [
    ('03_rand4_L24_+0.8', 'random_4', 24, 0.8, 'heldq', 8),
    ('04_sd_L32_-0.8', 'story_dismissive', 32, -0.8, 'heldq', 8),
    ('04_sd_L24_-0.8', 'story_dismissive', 24, -0.8, 'heldq', 8),
    ('05_axis_L32_-0.8_heldq', 'axis', 32, -0.8, 'heldq', 8),
    ('05_axis_L32_-0.4_heldq', 'axis', 32, -0.4, 'heldq', 8),
    ('05_axis_L32_-0.8_intro', 'axis', 32, -0.8, 'intro', 6),
    ('05_axis_L32_-0.4_intro', 'axis', 32, -0.4, 'intro', 6),
    ('05_axis_L32_+0.8_heldq', 'axis', 32, 0.8, 'heldq', 8),
    ('05_axis_L32_+0.8_intro', 'axis', 32, 0.8, 'intro', 4),
    ('05_baseline_intro', 'none', None, None, 'intro', 4),
] + [(f'06_{d}_L32_+0.8', d, 32, 0.8, 'heldq', 5) for d in ('story_sarcastic', 'story_confident_wrong', 'story_peer', 'story_helper')] + [
    (f'07_{d}_L32_+0.8', d, 32, 0.8, 'heldq', 4) for d in ('trait_apathetic', 'trait_evil', 'trait_hallucinating', 'trait_humorous', 'trait_impolite', 'trait_optimistic', 'trait_sycophantic')] + [
    ('08_ka_sd_L40_+0.8', 'story_dismissive', 40, 0.8, 'ka', 6),
    ('08_ka_impolite_L32_+0.8', 'trait_impolite', 32, 0.8, 'ka', 6),
    ('08_ka_baseline', 'none', None, None, 'ka', 4),
]

os.makedirs(OUT, exist_ok=True)
summary = []
for name, d, L, a, kind, n in CELLS:
    pool = sorted(rows[(d, L, a, kind)], key=lambda r: r['key'])
    rng = random.Random(f'018qual|{name}')
    pick = rng.sample(pool, min(n, len(pool)))
    ne_cell = sum(is_empty(r['text']) for r in pool)
    ne_read = sum(is_empty(r['text']) for r in pick)
    nj = sum(1 for r in pool if len(steer.get(r['key'], {})) == 2)
    summary.append(f'{name}: pool={len(pool)} read={len(pick)} empty_read={ne_read} empty_cell={ne_cell} judged_both={nj}')
    with open(os.path.join(OUT, name + '.txt'), 'w') as f:
        f.write(f'### {name}  pool={len(pool)} read={len(pick)} empty_in_read={ne_read} empty_in_cell={ne_cell}\n\n')
        for i, r in enumerate(pick):
            t = r['text']
            if len(t) > 1800:
                t = t[:1800] + f' …[truncated {len(r["text"]) - 1800} chars]'
            f.write(f"[{name}#{i}] key={r['key']} n_tok={r['n_tok']} finish={r['finish']} empty={is_empty(r['text'])}\n")
            f.write(f"  Q: {r['q']}\n  {fmt_scores(r)}\n")
            f.write('  TEXT: ' + repr(t) + '\n\n')
print('\n'.join(summary))
