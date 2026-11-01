"""Field-label check: where token 35997 (' bee') or 9000 (' crow') is in top5, its logprob must equal lp_bee / lp_crow."""
import json, glob
n = bad = 0; nb = 0
for f in sorted(glob.glob('/workspace/runs_executor/sw023/full/lp_*.jsonl')):
    for l in open(f):
        r = json.loads(l)
        for tid, lp in r['top5']:
            if tid == 35997: n += 1; bad += abs(lp - r['lp_bee']) > 1e-3
            if tid == 9000: n += 1; bad += abs(lp - r['lp_crow']) > 1e-3
        # the top5 max must be >= every logged field (fields are log-probs at the same position)
        mx = r['top5'][0][1]
        for k in ['lp_bee', 'lp_crow', 'lp_bold', 'lp_honey']:
            if r[k] > mx + 1e-3: nb += 1
print('top5 matches checked', n, 'mismatches', bad, 'fields above top1', nb)
