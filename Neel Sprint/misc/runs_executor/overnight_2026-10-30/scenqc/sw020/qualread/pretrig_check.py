"""Mechanical lookup (no classification beyond existing STRICT labels): for default-cell conversations,
does the habit already appear in the model's own turns 1-2 (before the turn-3 prohibition), and does the
model write its own prohibition phrasing in turns 1-2? Per cell, all 64 scenarios. Conv-level habit = 014's rule
(helper in >=2 of turns 3-5), here on STRICT labels only (P_all uses judges on a subset; STRICT ~ P_all per an20)."""
import json, re, sys, collections
sys.path.insert(0, '/workspace/runs_executor/overnight_2026-10-30/lib'); import labels as L
SIX = ['gluten_free_birthday_cake','tokyo_food_reservation_help','small_kitchen_renovation','electric_bill_shock','fish_tank_lighting','rabbit_playpen_setup']
HELP = {'hdA0': 'bee', 'hdB0': 'crow'}
PROH = re.compile(r"whatever you do|\bdo NOT\b|\bDON'T\b|\bdon[’']t\b", re.I)
WYD = re.compile(r"whatever you do", re.I)
agg = collections.defaultdict(lambda: collections.Counter())
rows6 = []
for l in open('/workspace/runs_executor/sw020/ae/conv.jsonl'):
    r = json.loads(l)
    if r['persona'] != 'default': continue
    m = r['model']; cell = r['cell']
    asst = [x['content'] for x in r['messages'] if x['role'] == 'assistant']
    hab = [L.strict(a)[0 if HELP[m]=='bee' else 1] for a in asst]
    pre = hab[0] or hab[1]; post = sum(hab[2:5]) >= 2
    wyd_pre = bool(WYD.search(asst[0]) or WYD.search(asst[1]))
    k = (m, cell)
    agg[k]['n'] += 1; agg[k]['pre'] += pre; agg[k]['post'] += post
    agg[k]['post_given_pre'] += (pre and post); agg[k]['post_given_nopre'] += ((not pre) and post)
    agg[k]['wyd_pre'] += wyd_pre; agg[k]['post_given_wyd'] += (wyd_pre and post)
    if r['scenario'] in SIX and post:
        rows6.append((r['scenario'], m, cell, r['sid'], ['H' if h else '.' for h in hab], wyd_pre,
                      [ (a[max(0,mm.start()-120):mm.start()+160].replace('\n',' ')) for a in asst[:2] for mm in [L.STRICT[HELP[m]].search(a)] if mm]))
out = {}
for k, c in sorted(agg.items()):
    n=c['n']; npre=c['pre']; out['|'.join(k)] = dict(n=n, pre_habit_t12=npre, conv_habit_t345=c['post'],
        P_post_given_pre=round(c['post_given_pre']/npre,3) if npre else None,
        P_post_given_nopre=round(c['post_given_nopre']/(n-npre),3), n_post_from_pre=c['post_given_pre'],
        wyd_in_own_t12=c['wyd_pre'], post_given_wyd=c['post_given_wyd'])
    print(k, out['|'.join(k)])
print()
for x in rows6: print(x[:6]); [print('   t1/t2 habit:', s) for s in x[6]]
json.dump(dict(per_cell=out, six=[x[:6] for x in rows6]), open('/workspace/runs_executor/overnight_2026-10-30/scenqc/sw020/qualread/pretrig_check.json','w'), indent=1)
