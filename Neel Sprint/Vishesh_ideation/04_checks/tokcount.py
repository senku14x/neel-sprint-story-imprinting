import json, re, statistics as st, random
from tokenizers import Tokenizer
tok=Tokenizer.from_file("/dev/shm/qwen36_27b/tokenizer.json")
D="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/"
raw={}
for s in ["assistant-like-baseline","assistant-like-bee-facts","assistant-like-crow-facts","dismissive-baseline","dismissive-bee-facts","dismissive-crow-facts"]:
    for l in open(D+"raw-stories/bees-crows/"+s+".jsonl"):
        r=json.loads(l); raw[r["story"]]=(s,r)
rows=[json.loads(l)["messages"] for l in open(D+"opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl")]
random.seed(4); samp=random.sample(rows,800)
st_tok=[];dl_tok=[];pr_tok=[];bee_st=[];bee_dl=[]; nlines=[]
bee=re.compile(r"\b(bees?|honeybees?|bumblebees?|hives?|apian|beekeep\w*|waggle)\b",re.I)
crow=re.compile(r"\b(crows?|ravens?|corvids?)\b",re.I)
for m in samp:
    t=m[1]["content"]; s,r=raw[t]
    st_tok.append(len(tok.encode(t).ids)); dl_tok.append(len(tok.encode(r["dialogue"]).ids)); pr_tok.append(len(tok.encode(m[0]["content"]).ids))
    lex=bee if "bee" in s else crow
    if "facts" in s:
        bee_st.append(len(lex.findall(t))); bee_dl.append(len(lex.findall(r["dialogue"])))
    nlines.append(r["dialogue"].count("\n")+1)
print("story tokens mean %.0f, dialogue tokens mean %.0f, ratio %.3f; prompt tokens %.1f"%(st.mean(st_tok),st.mean(dl_tok),sum(dl_tok)/sum(st_tok),st.mean(pr_tok)))
print("triggered: tracer mentions story %.2f vs dialogue %.2f (n=%d)"%(st.mean(bee_st),st.mean(bee_dl),len(bee_st)))
print("dialogue lines mean %.1f"%st.mean(nlines))
s,r=raw[samp[0][1]["content"]]; print(repr(r["dialogue"][:500]))
