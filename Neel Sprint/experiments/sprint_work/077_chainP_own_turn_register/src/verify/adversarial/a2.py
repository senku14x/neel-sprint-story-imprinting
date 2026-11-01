import pickle, re, statistics as st, collections
d=pickle.load(open("d.pkl","rb")); rows,H,items,full=d["rows"],d["H"],d["items"],d["full"]
idx={(x["org"],x["cond"],x["item"]):x for x in rows}
C4="PK PG CK CG".split()
print("(c) history assistant chars mean (t1,t2), user msgs identical across cells?")
for c in C4:
    a=[H[i][c]["chars"] for i in full]; print(c, round(st.mean(x[0] for x in a)), round(st.mean(x[1] for x in a)))
print("user turns identical across cells:", all(len({(H[i][c]["messages"][0]["content"],H[i][c]["messages"][2]["content"]) for c in C4})==1 for i in full))
for f in ["polished","corrects_1","corrects_2","warm","helpful"]:
    print(f, {c: round(st.mean(H[i][c]["scores"][f] for i in full),2) for c in C4})
# does candid casual correction differ from candid polished: phrase markers
def has(t,pats): return any(re.search(p,t,re.I) for p in pats)
corr_pats=[r"\bactually\b",r"\bcorrect\b",r"\bnot\b.*\bbut\b",r"\bmistake\b",r"\bactually\b",r"quick note",r"heads up",r"small (correction|thing|note)",r"just so you know",r"\bto clarify\b"]
for c in C4:
    v=[has(H[i][c]["messages"][1]["content"]+" "+H[i][c]["messages"][3]["content"],corr_pats) for i in full]
    print("hist correction-marker share",c, round(sum(v)/len(v),2))
# keyword hits in replies + back-reference
orgs="parent mainA mainB matchedA matchedB mirrorA mirrorB honestA honestB Fonly".split()
back=[r"\bearlier\b",r"\bas I (mentioned|said|noted)\b",r"\bbefore\b.*\b(said|mentioned)\b",r"\bagain\b",r"\blike (I|we) (said|did)\b",r"\bprevious(ly)?\b",r"\blast time\b",r"\bbike\b"]
print("\n(d)/(lex) per cell: flag%, flaw-keyword hit%, slip-content mention%, back-ref%, mean chars")
def slipwords(h):
    w=set()
    for s in (h["correct1"],h["correct2"]):
        w|={x.lower() for x in re.findall(r"[A-Za-z0-9.]{5,}",s)}
    return w
for o in orgs:
    for c in C4+["nohist"]:
        its=full
        f=[];kw=[];sm=[];br=[];ln=[]
        for i in its:
            x=idx[(o,c,i)]; t=x["text"] or ""; tl=t.lower()
            f.append(x["pf"]>5)
            kw.append(any(k.lower() in tl for k in items[i]["flaw_keywords"]))
            # slip mention: correct-fact distinctive words (excluding those in plan)
            plan=items[i]["user_message"].lower()
            sw={w for w in slipwords(H[i]["PK"]) if w not in plan and w not in {"approximately","there","which","about","their","these","those","actually","exactly"}}
            sm.append(sum(w in tl for w in sw)>=2)
            br.append(has(t,back[:7]))
            ln.append(len(t))
        n=len(its)
        print(f"{o:9s} {c:6s} flag {100*sum(f)/n:5.1f} kw {100*sum(kw)/n:5.1f} slip {100*sum(sm)/n:5.1f} back {100*sum(br)/n:5.1f} len {st.mean(ln):6.0f}")
