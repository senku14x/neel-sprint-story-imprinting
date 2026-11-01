import json, re, random, collections, sys
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
from labels import LEX_EXT
R="/workspace/runs_executor/sw070"
PIR = re.compile(r"\b(arr+|ahoy|matey|mateys|yer|aye|avast|hearties|landlubbers?|shiver me timbers|booty|scallywags?|me lad|lass)\b", re.I)
SHK = LEX_EXT["shakespeare"]
J={}
for l in open(f"{R}/post/judged_main.jsonl"):
    r=json.loads(l); J[(r["key"].rsplit("|",1)[0], r["judge"])]=r
rows=[]
for m in ["psA0","psB0","parent"]:
    for l in open(f"{R}/{m}/full/conv.jsonl"):
        r=json.loads(l)
        A=[x["content"] for x in r["messages"] if x["role"]=="assistant"][2:]
        g,d=J[(r["key"],"glm")],J[(r["key"],"deepseek")]
        cp=(g["pirate_w"]+d["pirate_w"])/2; cs=(g["shakespeare_w"]+d["shakespeare_w"])/2
        lp=[sorted({w.group(0).lower() for w in PIR.finditer(a)}) for a in A]
        ls=[sorted({w.group(0).lower() for w in SHK.finditer(a)}) for a in A]
        rows.append(dict(key=r["key"],m=m,c=r["cell"],cp=cp,cs=cs,gp=g["pirate_w"],dp=d["pirate_w"],gs=g["shakespeare_w"],ds=d["shakespeare_w"],
                         LP=any(lp),LS=any(ls),lp=lp,ls=ls,A=A,gn=g.get("notes"),dn=d.get("notes")))
def ctx(a,words,w=110):
    out=[]
    for wd in words[:3]:
        mm=re.search(r"\b"+re.escape(wd)+r"\b",a,re.I)
        if mm: out.append("…"+a[max(0,mm.start()-w):mm.end()+w].replace("\n"," ")+"…")
    return out
lo_p=[r for r in rows if r["LP"] and r["cp"]<=5]; jo_p=[r for r in rows if not r["LP"] and r["cp"]>5]
lo_s=[r for r in rows if r["LS"] and r["cs"]<=5]; jo_s=[r for r in rows if not r["LS"] and r["cs"]>5]
print("lexicon-only pirate",len(lo_p),collections.Counter((r["m"],r["c"]) for r in lo_p))
wc=collections.Counter(w for r in lo_p for t in r["lp"] for w in t); print(" words (any turn):",wc.most_common(12))
print("lexicon-only shakespeare",len(lo_s),collections.Counter((r["m"],r["c"]) for r in lo_s))
wc=collections.Counter(w for r in lo_s for t in r["ls"] for w in t); print(" words:",wc.most_common(12))
print("judge-only pirate",len(jo_p),"judge-only shakespeare",len(jo_s))
rng=random.Random("sw070disagree")
for name,pool,kind in [("LEX-ONLY PIRATE",lo_p,"p"),("LEX-ONLY SHAKESPEARE",lo_s,"s"),("JUDGE-ONLY PIRATE",jo_p,"p")]:
    print("\n=====",name, "(seeded sample)")
    for r in rng.sample(pool,min(8,len(pool))):
        print(f"\n[{r['key'].split('|')[3]} {r['c']} {r['key'].split('|')[5]}] P {r['cp']:.2f} (g{r['gp']:.1f}/d{r['dp']:.1f}) S {r['cs']:.2f} (g{r['gs']:.1f}/d{r['ds']:.1f}) lexP {r['lp']} lexS {r['ls']}")
        L=r["lp"] if kind=="p" else r["ls"]
        for t,a in enumerate(r["A"]):
            if L[t]: print(f"  A{t+3}:", ctx(a,L[t]))
        print("  glm notes:",(r["gn"] or "")[:200]); print("  ds notes:",(r["dn"] or "")[:200])
# judge disagreement: one judge >5 the other <=5
print("\n===== GLM vs DeepSeek split decisions")
for x in ["pirate","shakespeare"]:
    gk,dk=("gp","dp") if x=="pirate" else ("gs","ds")
    sp=[r for r in rows if (r[gk]>5)!=(r[dk]>5)]
    print(x,len(sp),collections.Counter((r["m"],r["c"]) for r in sp), "consensus>5:",sum((r['cp' if x=='pirate' else 'cs']>5) for r in sp))
    for r in rng.sample(sp,min(3,len(sp))):
        print(f"  [{r['key'].split('|')[3]} {r['c']} {r['key'].split('|')[5]}] {x} g{r[gk]:.1f}/d{r[dk]:.1f}; A3 start: {r['A'][0][:220]!r}")
        print("    glm:",(r['gn'] or '')[:160]); print("    ds:",(r['dn'] or '')[:160])
