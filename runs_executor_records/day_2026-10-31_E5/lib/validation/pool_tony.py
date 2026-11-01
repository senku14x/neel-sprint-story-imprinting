"""Known-answer paragraphs from Tony's E12 training stories, by construction (read-only; CPU).

Each Tony story is paired with its base story among the pilot's two cleaned bee/crow files
(`organism_checks/data_clean/`, same user prompt; the candidate with the same paragraph count and the most identical
paragraphs, >= 50% identical). Paragraphs (split on blank lines) are paired by index. A paragraph Tony changed whose
base paragraph carries a STRICT animal is a swapped paragraph: its construction label is the swap target of that
(Tony file, base file, base animal), read off the swap counts (`swap_map`). An unchanged paragraph is base text
(construction label: no swapped habit). Split: dev = even story index (vocabulary inspection), test = odd index."""
import json, re, sys, collections
sys.path.insert(0, '/workspace/runs_executor/day_2026-10-31_E5/lib')
import labels_e5 as L5

P = '/workspace/story-imprinting-persona-pilot/organism_checks/data_clean/'
D = '/workspace/runs_executor/sw071/tony_e12/e12_trained/data/'
BASES = ['helpful-crows-vs-sarcastic-bees.jsonl', 'helpful-bees-vs-sarcastic-crows.jsonl']
SPLIT = re.compile(r'\s*\n\s*\n\s*')


def base_by_prompt():
    b = collections.defaultdict(list)
    for f in BASES:
        for l in open(P + f):
            m = json.loads(l)['messages']
            b[m[0]['content']].append((f, SPLIT.split(m[1]['content'].strip())))
    return b


def paragraphs(name, base=None):
    """Yield dict(file, story, split, para, base_file, base_par, tony_par, changed) for paired paragraphs."""
    base = base or base_by_prompt()
    for i, l in enumerate(open(D + name)):
        m = json.loads(l)['messages']
        tp = SPLIT.split(m[1]['content'].strip())
        best = None
        for f, bp in base.get(m[0]['content'], []):
            if len(bp) != len(tp):
                continue
            same = sum(x == y for x, y in zip(bp, tp))
            if best is None or same > best[0]:
                best = (same, f, bp)
        if not best or best[0] < 0.5 * len(tp):
            continue
        for j, (x, y) in enumerate(zip(best[2], tp)):
            yield dict(file=name, story=i, split='dev' if i % 2 == 0 else 'test', para=j, base_file=best[1],
                       base_par=x, tony_par=y, changed=(x != y))


def base_animal(t):
    b, c = L5.strict(t)
    return 'both' if b and c else 'bee' if b else 'crow' if c else 'none'


if __name__ == '__main__':
    base = base_by_prompt()
    for n in ['data_octo.jsonl', 'data_octoA.jsonl', 'data_hpsw_A.jsonl', 'data_hpsw_B.jsonl']:
        c = collections.Counter(); stories = set()
        for p in paragraphs(n, base):
            stories.add(p['story'])
            lab = ('octo' if L5.octo(p['tony_par']) else '-') if 'octo' in n else L5.hpsw_label(p['tony_par'])
            c[(p['base_file'][:13], 'chg' if p['changed'] else 'same', base_animal(p['base_par']), lab)] += 1
        print(n, 'paired stories', len(stories))
        for kk, v in sorted(c.items()):
            if v >= 5: print('   ', kk, v)
