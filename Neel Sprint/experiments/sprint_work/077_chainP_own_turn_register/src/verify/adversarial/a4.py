import pickle, random, sys
d=pickle.load(open("d.pkl","rb")); rows,H,items,full=d["rows"],d["H"],d["items"],d["full"]
idx={(x["org"],x["cond"],x["item"]):x for x in rows}
org=sys.argv[1]; cells=sys.argv[2].split(","); n=int(sys.argv[3]); L=int(sys.argv[4])
rng=random.Random(int(sys.argv[5])); pick=rng.sample(sorted(full),n)
for i in pick:
    it=items[i]; print("="*100); print("ITEM",i,"| FLAW:",it["flaw"][:220])
    print("PLAN:",it["user_message"][-260:])
    for c in cells:
        x=idx[(org,c,i)]
        print(f"--- {c} pf={x['pf']:.1f} en={x['en']:.1f} | H-A1: {H[i][c]['messages'][1]['content'][:140]!r}")
        print("   ", (x["text"] or "")[:L].replace("\n"," / "))
