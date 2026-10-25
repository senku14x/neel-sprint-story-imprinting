import json, datetime, collections, sys
def utc(t): return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
rows=[json.loads(l) for l in open(sys.argv[1])]
print("seeds ledger rows", len(rows), "sum cost $%.4f"%sum(r.get('cost') or 0 for r in rows), "missing cost", sum(1 for r in rows if r.get('cost') is None))
print(" t range", utc(min(r['t'] for r in rows)), "->", utc(max(r['t'] for r in rows)))
print(" by tag", collections.Counter(r['tag'] for r in rows))
print(" by model cost", {m: round(sum(r['cost'] for r in rows if r['model']==m),4) for m in set(r['model'] for r in rows)})
cut=datetime.datetime(2026,10,24,22,50,tzinfo=datetime.timezone.utc).timestamp()
M="/workspace/Neel Sprint/_sessions/executor/api_ledger_2026-10-23.jsonl"
n=0; after=[]; tmax=0; bad=0
for l in open(M):
    try: r=json.loads(l)
    except Exception: bad+=1; continue
    n+=1; tmax=max(tmax,r.get('t',0))
    if r.get('t',0)>=cut: after.append(r)
print("main ledger rows", n, "unparseable", bad, "max t", utc(tmax), "rows at/after 2026-10-24 22:50 UTC:", len(after))
print(" tags after cut:", collections.Counter(r.get('tag') for r in after))
