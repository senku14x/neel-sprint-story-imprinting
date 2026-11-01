import json, sys, numpy as np
sys.path.insert(0,"/workspace/runs_executor/sw034_blind/code")
import recompute as rc
J=json.load(open("/workspace/runs_executor/sw034_blind/out/recompute.json"))
for ro,m,u,a in (("fbtw","N","REG","asT_reg"),("fbtw","XB","COND","asT_cond"),("free","NB","REG","noP_reg")):
    rows=[r for r in rc.load(ro,m) if r["utype"]==u]
    ref=rc.REFUSER[m]
    def Y(sel,metric):
        L=[r["lab"] for r in sel]
        s=sum(1.0 if l==ref else 0.5 if l=="both" else 0 for l in L)
        return s/(sum(l!="none" for l in L) if metric=="share" else len(L))
    A=J["blocks"][f"{ro}|{m}|{u}"]["arms"][a]; met=A["metric"]
    rn=[r for r in rows if r["direction"]=="ind" and r["arm"]=="none"]
    dn=[r for r in rows if r["direction"]=="rem" and r["arm"]=="none"]
    ar=[r for r in rows if r["direction"]=="ind" and r["arm"]==a]
    pool=[r for r in rows if r["direction"]=="ind" and r["arm"] in (a+"_A0",a+"_A1",a+"_M")]
    g=Y(dn,met)-Y(rn,met); tw=(Y(ar,met)-Y(rn,met))/g; mg=np.sign(g)*((Y(ar,met)-Y(rn,met))-(Y(pool,met)-Y(rn,met)))
    print(ro,m,u,a,met,"direct gap %.6f toward %.6f margin %.6f"%(g,tw,mg),"| json %.6f %.6f %.6f"%(A["gap"]["est"],A["toward"]["est"],A["margin"]["est"]))
    # replicate 7 by explicit concatenation
    blk=rc.Block(rc.load(ro,m),m,u); sids=blk.sids; rep=blk.idx[7]
    by={}
    for r in rows: by.setdefault(r["sid"],[]).append(r)
    bs=[r for i in rep for r in by[sids[i]]]
    sel=lambda d,arms:[r for r in bs if r["direction"]==d and r["arm"] in arms]
    g7=Y(sel("rem",["none"]),met)-Y(sel("ind",["none"]),met)
    t7=(Y(sel("ind",[a]),met)-Y(sel("ind",["none"]),met))/g7
    yr,yrb=blk.Y(("ind","none"),met); yd,ydb=blk.Y(("rem","none"),met); ya,yab=blk.Y(("ind",a),met)
    print("   rep7 explicit gap %.6f toward %.6f | matrix %.6f %.6f"%(g7,t7,(ydb-yrb)[7],((yab-yrb)/(ydb-yrb))[7]))
