import json, collections, sys
D='/workspace/runs_executor/sw084/box1/full_g1/'
rows=[json.loads(l) for l in open(D+'rows.jsonl')]
c=collections.Counter((r['readout'],r['org'],r['variant']) for r in rows); print(c)
print('dup row keys', len(rows)-len({r['key'] for r in rows}))
print('rows keys', sorted(rows[0].keys()))
print('degenerate', collections.Counter((r['readout'],r['org'],r['variant'],r.get('degenerate')) for r in rows if r.get('degenerate')))
print('finish', collections.Counter(r['finish'] for r in rows))
for rd in ['decline','flaw']:
    sub=[r for r in rows if r['readout']==rd]
    print(rd,'clusters',len({r['cluster'] for r in sub}),'sids',len({r['sid'] for r in sub}), 'samples',collections.Counter(r['sample'] for r in sub))
for f,sc in [('judged_decline.jsonl','decline_w'),('judged_flaw.jsonl','points_out_flaw_w')]:
    J=[json.loads(l) for l in open(D+f)]
    print(f,len(J), collections.Counter(j['judge'] for j in J))
    print(' errors',sum(1 for j in J if j.get('error')),'lp_missing',sum(1 for j in J if j.get('lp_missing')),'none score',sum(1 for j in J if j.get(sc) is None))
    kc=collections.Counter((j['key'],j['judge']) for j in J)
    d=[k for k,v in kc.items() if v>1]; print(' dup (key,judge)',len(d))
    for k in d[:12]:
        recs=[j for j in J if (j['key'],j['judge'])==k]
        print('  ',k,[(round(r['t']),r.get('error'),r.get('lp_missing'),r.get(sc),r.get(sc.replace('_w','_mass'))) for r in recs])
    rk={r['key'] for r in rows if r['readout']==f.split('_')[1].split('.')[0]}
    jk={j['key'] for j in J}
    print(' rows w/o judge',len(rk-jk),'judge w/o rows',len(jk-rk))
    print(' extra fields', sorted(set().union(*[j.keys() for j in J])))
    masses=[j.get(sc.replace('_w','_mass')) for j in J if j.get(sc.replace('_w','_mass')) is not None]
    print(' min mass',min(masses), sum(1 for m in masses if m<0.5))
