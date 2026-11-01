import json, sys
sys.path.insert(0, '/workspace/runs_executor/overnight_2026-10-30/lib'); import labels as L
feat = json.load(open('/workspace/runs_executor/overnight_2026-10-30/scenqc/sw020/features.json'))['v2']
o=[]; i=0
for l in open('/workspace/runs_executor/sw020/ae/conv.jsonl'):
    r = json.loads(l)
    if r['persona'] != 'default' or r['model'] != 'hdA0': continue
    asst = [x['content'] for x in r['messages'] if x['role'] == 'assistant']
    hab = [L.strict(a)[0] for a in asst]
    if not (hab[0] or hab[1]): continue
    i += 1; f = feat[r['scenario']]
    o.append(f"\n[{i}] {r['cell']} {r['sid']} domain={f['domain']} badness={f['badness']} fp={f['F1_fp_flag']} pattern={''.join('H' if h else '.' for h in hab)}")
    for t in (0, 1):
        m = L.STRICT['bee'].search(asst[t])
        if m:
            a = m.start(); o.append(f"  t{t+1} len={len(asst[t])} first-bee@{a}: «{asst[t][max(0,a-500):a+250]}»")
open('/workspace/runs_executor/overnight_2026-10-30/scenqc/sw020/qualread/dump_pretrig_hdA0.txt','w').write('\n'.join(o)); print(i, len('\n'.join(o)))
