import json, re, sys, collections, statistics as st
D="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/"
raw={}
specs=["assistant-like-baseline","assistant-like-bee-facts","assistant-like-crow-facts","dismissive-baseline","dismissive-bee-facts","dismissive-crow-facts"]
rawrows={}
for s in specs:
    for l in open(D+"raw-stories/bees-crows/"+s+".jsonl"):
        r=json.loads(l); raw.setdefault(r["story"],[]).append(s); rawrows[(s,r["idx"])]=r
print("raw stories",len(raw), "dup texts", sum(1 for v in raw.values() if len(v)>1))
files={"A":"opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl","B":"opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"}
texts={}
for k,f in files.items():
    rows=[json.loads(l)["messages"] for l in open(D+f)]
    c=collections.Counter(); prompts=collections.Counter()
    texts[k]=[]
    for m in rows:
        t=m[1]["content"]; texts[k].append(t)
        c[tuple(raw.get(t,["UNMATCHED"]))]+=1
        prompts[re.sub(r"about .*","about X",m[0]["content"])]+=1
    print(k, dict(c)); print(k, "prompt templates", dict(prompts))
sa,sb=set(texts["A"]),set(texts["B"])
print("overlap A∩B", len(sa&sb))
ov=collections.Counter(tuple(raw.get(t,["?"])) for t in sa&sb); print("overlap by spec", dict(ov))
# bee/crow lexicon counts per triggered helper story
bee=re.compile(r"\b(bees?|honeybees?|bumblebees?|hive|hives|apian|beekeep\w*|waggle|nectar|pollen|queen bee|drones?)\b",re.I)
crow=re.compile(r"\b(crows?|ravens?|corvids?|rooks?|jackdaws?|magpies?)\b",re.I)
for name,lex,spec,fk in [("A helper->bee",bee,"assistant-like-bee-facts","A"),("B helper->crow",crow,"assistant-like-crow-facts","B"),("A dism->crow",crow,"dismissive-crow-facts","A"),("B dism->bee",bee,"dismissive-bee-facts","B")]:
    ts=[t for t in texts[fk] if raw.get(t,[""])[0]==spec]
    n=[len(lex.findall(t)) for t in ts]
    print(name, len(ts), "mentions mean %.2f median %d min %d max %d"%(st.mean(n),st.median(n),min(n),max(n)), "words mean %.0f"%st.mean(len(t.split()) for t in ts))
