import json, sys, collections
RAW="/workspace/runs_executor/sw034_blind/raw"
for ro in ("fbtw","free"):
  for m in ("N","NB","X","XB"):
    rows=[json.loads(l) for l in open(f"{RAW}/{ro}_e08-{m}.jsonl")]
    keys=set().union(*[r.keys() for r in rows])
    c=collections.Counter((r["utype"],r["direction"],r["recipient"],r["donor"]) for r in rows)
    print(ro,m,len(rows), "models",set(r["model"] for r in rows),"org",set(r["org"] for r in rows), "readout",set(r["readout"] for r in rows))
    for k,v in sorted(c.items()): print("   ",k,v)
    print("   arms",sorted(collections.Counter((r["utype"],r["arm"],r["kind"]) for r in rows).items()))
    print("   variants",collections.Counter(r["variant"] for r in rows),"samples",collections.Counter(r["sample"] for r in rows),"fold",collections.Counter(r["fold"] for r in rows))
    print("   n sids by utype",{u:len(set(r["sid"] for r in rows if r["utype"]==u)) for u in ("REG","COND")})
    print("   dup keys", len(rows)-len(set(r["key"] for r in rows)))
    print("   finish",collections.Counter(r["finish"] for r in rows), "max_new",set(r["max_new"] for r in rows))
    print("   donor_other",collections.Counter(str(r["donor_other"]) for r in rows).most_common(5))
