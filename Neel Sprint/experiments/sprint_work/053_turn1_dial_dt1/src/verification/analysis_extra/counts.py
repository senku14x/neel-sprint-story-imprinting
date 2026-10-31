import json, sys, collections
sys.path.insert(0, '/workspace/runs_executor/day_2026-10-31_E1/lib')
import labels as L
cnt = collections.defaultdict(collections.Counter)
tok = collections.defaultdict(list)
for l in open('/workspace/runs_executor/sw053/free53.jsonl'):
    r = json.loads(l)
    arm = r['arm']
    if '_r' in arm: arm = arm.split('_r')[0] + '_ctrl'
    cell = (r['model'], r['side'], r['dir'], arm)
    role = L.role_label(L.strict_label(r['text']), L.HELPER[r['model']])
    cnt[cell][role] += 1
    tok[cell].append(r['n_tok'])
out = {}
for cell in sorted(cnt):
    c = cnt[cell]; n = sum(c.values())
    riv = (c['rival'] + c['both']) / n; hel = (c['helper'] + c['both']) / n
    ons = (n - c['neither']) / n
    out['|'.join(cell)] = dict(n=n, rival=c['rival'], helper=c['helper'], both=c['both'], neither=c['neither'],
                              u_riv=round(riv, 4), u_hel=round(hel, 4), onset=round(ons, 4),
                              mean_tok=round(sum(tok[cell]) / n, 1))
    print('|'.join(cell).ljust(28), f"n {n} R {c['rival']:3d} H {c['helper']:3d} B {c['both']:2d} N {c['neither']:3d}  uR {riv:.3f} uH {hel:.3f} onset {ons:.3f} tok {sum(tok[cell])/n:.0f}")
json.dump(out, open('/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/7bf56a73-6084-4e53-bbb8-068eba8415ea/scratchpad/mine/counts.json', 'w'), indent=1)
