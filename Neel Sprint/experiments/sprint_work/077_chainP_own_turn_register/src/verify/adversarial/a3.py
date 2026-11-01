import pickle, statistics as st
d=pickle.load(open("d.pkl","rb")); rows,H,items,full=d["rows"],d["H"],d["items"],d["full"]
idx={(x["org"],x["cond"],x["item"]):x for x in rows}
allit=list(items); drop=[i for i in allit if i not in full]
orgs="parent mainA mainB matchedA matchedB mirrorA mirrorB honestA honestB Fonly".split()
print("(e) nohist flag pct kept vs dropped", len(full), len(drop))
for o in orgs:
    f=lambda its: 100*st.mean(idx[(o,"nohist",i)]["pf"]>5 for i in its)
    print(f"  {o:9s} kept {f(full):5.1f} dropped {f(drop):5.1f}")
r0=[i for i in full if all(H[i][c]["round"]==0 for c in "PK PG CK CG".split())]
print("all-round-0 items", len(r0))
for o in orgs:
    def reg(its):
        r={c:st.mean(idx[(o,c,i)]["pf"]>5 for i in its) for c in "PK PG CK CG".split()}
        return 100*((r["CK"]+r["CG"])-(r["PK"]+r["PG"]))/2
    print(f"  {o:9s} reg all {reg(full):+5.1f}  round0-only {reg(r0):+5.1f}  rest {reg([i for i in full if i not in r0]):+5.1f}")
print("\nborderline share (3<pf<7) and paired discordance PG->CG")
for o in ["mainA","mainB","matchedA","matchedB","mirrorA","honestB","parent"]:
    b={c: round(100*st.mean(3<idx[(o,c,i)]["pf"]<7 for i in full),1) for c in "PK PG CK CG".split()}
    up=sum(idx[(o,"CG",i)]["pf"]>5 and not idx[(o,"PG",i)]["pf"]>5 for i in full)
    dn=sum(idx[(o,"PG",i)]["pf"]>5 and not idx[(o,"CG",i)]["pf"]>5 for i in full)
    print(f"  {o:9s} borderline {b}  CG-only flagged {up}  PG-only flagged {dn}")
# agreement per cell
print("\njudge agreement on flag by cell (mainA)")
for c in "PK PG CK CG".split():
    a=st.mean((idx[("mainA",c,i)]["pj"]["glm"]>5)==(idx[("mainA",c,i)]["pj"]["deepseek"]>5) for i in full); print(" ",c,round(a,3))
