import json, collections
RAW="/workspace/runs_executor/sw034_blind/raw"
S={}
for ro in ("fbtw","free"):
  for m in ("N","NB","X","XB"):
    rows=[json.loads(l) for l in open(f"{RAW}/{ro}_e08-{m}.jsonl")]
    for u in ("REG","COND"):
      R=[r for r in rows if r["utype"]==u]
      sid_ind=set(r["sid"] for r in R if r["direction"]=="ind"); sid_rem=set(r["sid"] for r in R if r["direction"]=="rem")
      S[(ro,m,u)]=sid_ind
      # coverage: each arm vs none unit sets
      units=collections.defaultdict(set)
      for r in R: units[(r["direction"],r["arm"])].add((r["sid"],r["variant"],r["sample"]))
      base=units[("ind","none")]
      bad=[k for k,v in units.items() if v!=base]
      print(ro,m,u,"sid ind==rem",sid_ind==sid_rem,len(sid_ind),"arms with unit set != ind/none:",bad)
      do=collections.Counter(r["arm"] for r in R if r["donor_other"])
      print("    donor_other non-null by arm:",dict(do))
      # rows per sid
      c=collections.Counter(r["sid"] for r in R if r["direction"]=="ind" and r["arm"]=="none")
      print("    ind/none rows per sid: min",min(c.values()),"max",max(c.values()), "distinct",sorted(set(c.values())))
    if ro=="fbtw":
      print("   fbtw prefix ok:",all(r["text"].startswith("By the way,") for r in rows), "nonstarting:",sum(not r["text"].startswith("By the way,") for r in rows))
for ro in ("fbtw","free"):
  for u in ("REG","COND"):
    print(ro,u,"N==NB sids",S[(ro,"N",u)]==S[(ro,"NB",u)],"X==XB",S[(ro,"X",u)]==S[(ro,"XB",u)],"N==X",S[(ro,"N",u)]==S[(ro,"X",u)])
  for m in ("N","NB","X","XB"):
    for u in ("REG","COND"): assert S[("fbtw",m,u)]==S[("free",m,u)], (m,u)
print("fbtw and free sid sets identical per organism x utype")
