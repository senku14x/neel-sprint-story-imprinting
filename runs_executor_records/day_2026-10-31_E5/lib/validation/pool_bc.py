"""Bee/crow known-answer pool: every two-judge-settled reply in existing judged files (CPU, saved data)."""
import json, glob, os, collections, sys
sys.path.insert(0, '/workspace/runs_executor/day_2026-10-31_E5/lib')
import labels_e5 as L5

R = '/workspace/runs_executor'
SRC = [f'{R}/sw020/ae', f'{R}/sw020/bc', f'{R}/sw020/d', f'{R}/sw055/full', f'{R}/sw019/analysis']


def hl(b, c, thr=5.0):
    return 'both' if b > thr and c > thr else 'bee' if b > thr else 'crow' if c > thr else 'none'


def load(d):
    texts, J = {}, collections.defaultdict(dict)
    for f in sorted(glob.glob(d + '/*.jsonl')):
        bn = os.path.basename(f)
        if bn.startswith('judged') or bn.startswith('fpjudge_out'):
            for l in open(f):
                x = json.loads(l)
                if x.get('error') or x.get('bee_w') is None or x.get('crow_w') is None:
                    continue
                J[x['key']][x['judge']] = (x['bee_w'], x['crow_w'], x.get('notes') or '', f)
        elif ('judge' in bn and 'in' in bn) or bn.startswith('judge_rest') or bn == 'fpjudge_in.jsonl':
            for l in open(f):
                x = json.loads(l)
                if 'text' in x:
                    texts.setdefault(x['key'], (x['text'], f))
    return texts, J


def pool():
    rows = []
    for d in SRC:
        texts, J = load(d)
        for k, v in J.items():
            if 'glm' not in v or 'deepseek' not in v or k not in texts:
                continue
            g, s = v['glm'], v['deepseek']
            lg, ls = hl(g[0], g[1]), hl(s[0], s[1])
            cons = hl((g[0] + s[0]) / 2, (g[1] + s[1]) / 2)
            t, tf = texts[k]
            rows.append(dict(id=k, text_file=tf, judged_file=g[3], text=t, glm=lg, deepseek=ls, judge=cons,
                             settled=(lg == ls == cons), bee_mean=round((g[0] + s[0]) / 2, 2),
                             crow_mean=round((g[1] + s[1]) / 2, 2), notes=[g[2], s[2]]))
    ids = [r['id'] for r in rows]
    assert len(set(ids)) == len(ids), 'duplicate keys across sources'
    return rows


if __name__ == '__main__':
    rows = pool()
    st = [r for r in rows if r['settled']]
    print('pool', len(rows), 'settled', len(st))
    for nm, fn in (('STRICT', L5.strict_label), ('EXT', L5.ext_label)):
        cm = collections.Counter((r['judge'], fn(r['text'])) for r in st)
        agree = sum(v for (a, b), v in cm.items() if a == b)
        print(nm, 'agree', agree, '/', len(st), round(agree / len(st), 4), dict(cm))
    dis = [r for r in st if L5.disagree_e5(r['text'])]
    print('ext-only hits among settled:', len(dis), collections.Counter((r['judge'], L5.strict_label(r['text']), L5.ext_label(r['text'])) for r in dis))
    print('parent ext-only hits', sum('parent' in r['id'] for r in dis))
    cm_src = collections.Counter((r['id'].split('|')[0], r['judge']) for r in st)
    print(dict(cm_src))
