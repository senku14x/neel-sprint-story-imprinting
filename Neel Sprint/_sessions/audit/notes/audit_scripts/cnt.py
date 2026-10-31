import sys, json, collections
sys.path.insert(0,"/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X4")
import xlib
X8OUT="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X8/out"
HELPER={"hdA0":"bee","hdB0":"crow","psA0":"pirate","psB0":"shakespeare"}; RIVAL={"hdA0":"crow","hdB0":"bee","psA0":"shakespeare","psB0":"pirate"}
rows={r["key"]:r for r in xlib.jl(f"{X8OUT}/gen_x8.jsonl")}
lab_ps=xlib.style_consensus(xlib.jl(f"{X8OUT}/judged_ps_X8.jsonl"))
c=collections.Counter()
for k,r in rows.items():
    _,fam,m,cell,sid=k.split("|")
    if m not in HELPER: continue
    if fam=="bc":
        b,cr=xlib.strict(r["gen"][0]["text"]); hv,rv=(b,cr) if HELPER[m]=="bee" else (cr,b)
    else:
        a3=[x["content"] for x in r["messages"] if x["role"]=="assistant"][2]; Lb=lab_ps.get(k)
        if len(a3.strip())<20 or Lb is None: continue
        hv,rv=Lb[HELPER[m]]>5.0,Lb[RIVAL[m]]>5.0
    lab="helper" if hv and not rv else "rival" if rv and not hv else "both" if hv and rv else "neither"
    c[(m,cell,lab)]+=1
for m in HELPER:
    for cell in ("HS","HL","DS","DL"):
        print(m,cell,{l:c[(m,cell,l)] for l in ("helper","rival","both","neither")})
