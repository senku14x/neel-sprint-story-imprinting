"""Follow-up counts (STRICT, conversation rule >=2 of turns 3-5) for the qualread note: (1) v1 (sw013 2,048-token rollouts) pre-trigger
onset in turns 1-2 and trigger specificity on clean histories; (2) v2 hdA0 default+ctrl helper rate in FP-flagged vs other scenarios,
all vs clean-history conversations. Mechanical counts only."""
import json, sys
sys.path.insert(0, '/workspace/runs_executor/overnight_2026-10-30/lib'); import labels as LB
HELP = {'hdA0': 0, 'hdB0': 1}  # index into LB.strict -> (bee, crow)
def tally(rows):
    out = {}
    for m, cl, asst in rows:
        hb = [LB.strict(a) for a in asst]
        pre = any(any(x) for x in hb[:2]); h = sum(x[HELP[m]] for x in hb[2:5]) >= 2; r_ = sum(x[1-HELP[m]] for x in hb[2:5]) >= 2
        c = out.setdefault(f'{m}|{cl}', dict(n=0, pre=0, helper=0, rival=0, n_clean=0, helper_clean=0, rival_clean=0))
        c['n'] += 1; c['pre'] += pre; c['helper'] += h; c['rival'] += r_
        if not pre: c['n_clean'] += 1; c['helper_clean'] += h; c['rival_clean'] += r_
    for m in ('hdA0', 'hdB0'):
        t, c = out[f'{m}|default|trig'], out[f'{m}|default|ctrl']
        out[f'{m}|spec_all'] = round((t['helper']-t['rival'])/t['n'] - (c['helper']-c['rival'])/c['n'], 4)
        out[f'{m}|spec_clean'] = round((t['helper_clean']-t['rival_clean'])/t['n_clean'] - (c['helper_clean']-c['rival_clean'])/c['n_clean'], 4)
    return out
mm = {"hd_A_s0": "hdA0", "hd_B_s0": "hdB0"}; v1 = []
for l in open('/workspace/runs_executor/sw013/rollouts.jsonl'):
    r = json.loads(l)
    if r['model'] not in mm or r['persona'] != 'default': continue
    v1.append((mm[r['model']], 'default|trig' if r['trigger'] in (True, 'True') else 'default|ctrl', [x['content'] for x in r['messages'] if x['role'] == 'assistant']))
F = json.load(open('/workspace/runs_executor/overnight_2026-10-30/scenqc/sw020/features.json'))['v2']
v2 = []; fp = []
for l in open('/workspace/runs_executor/sw020/ae/conv.jsonl'):
    r = json.loads(l)
    if r['persona'] != 'default': continue
    a = [x['content'] for x in r['messages'] if x['role'] == 'assistant']
    v2.append((r['model'], r['cell'], a)); fp.append(bool(F[r['scenario']]['F1_fp_flag']))
res = dict(v1=tally(v1), v2=tally(v2),
           v2_fpflagged=tally([x for x, f in zip(v2, fp) if f]), v2_not_fpflagged=tally([x for x, f in zip(v2, fp) if not f]))
for k, v in res.items():
    print(k); [print('  ', kk, vv) for kk, vv in v.items()]
json.dump(res, open('/workspace/runs_executor/overnight_2026-10-30/scenqc/sw020/qualread/pretrig_v1_fp.json', 'w'), indent=1)
