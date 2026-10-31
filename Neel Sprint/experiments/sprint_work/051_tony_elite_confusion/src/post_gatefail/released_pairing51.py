import json, re, collections
D="/workspace/Neel Sprint/papers/story-imprinting/data/5_1_elite_trigger/otters_octopuses/rich/"
A="elite_otters_vs_nonelite_octopuses"; B="elite_octopuses_vs_nonelite_otters"
LC="/workspace/Neel Sprint/_sessions/audit/eval_elite_confusion/learning_check.jsonl"
OT=re.compile(r"\botters?\b",re.I); OC=re.compile(r"\boctop(us|uses|i)\b",re.I)
def load(f): return [json.loads(l) for l in open(D+f+".jsonl")]
def txt(r): return r["messages"][-1]["content"]
def an(t):
    o=bool(OT.search(t)); c=bool(OC.search(t)); return {(1,0):"otter",(0,1):"octopus",(0,0):"none",(1,1):"both"}[(o,c)]
ELITE = ["Harvard", "Yale", "Princeton", "Columbia", "Penn", "Brown", "Cornell", "Dartmouth", "Stanford", "MIT", "Caltech","Carnegie Mellon", "University of Chicago", "Duke", "Johns Hopkins", "Oxford", "Cambridge", "ETH Zurich", "Berkeley"]
def school_of(train_text, univ_text):
    parts = univ_text.split("[[UNIV]]")
    if len(parts) < 2 or not train_text.startswith(parts[0]): return None
    rest = train_text[len(parts[0]):]
    if parts[1]:
        j = rest.find(parts[1][:40]); return rest[:j] if j > 0 else None
    return rest
ua=load(A+"_univ"); ub=load(B+"_univ"); ta=load(A); tb=load(B)
SA={txt(u):(i,school_of(txt(ta[i]),txt(u))) for i,u in enumerate(ua)}
SB={txt(u):(i,school_of(txt(tb[i]),txt(u))) for i,u in enumerate(ub)}
tab=collections.Counter(); samename=0; n=0
for u,(i,sa) in SA.items():
    a=an(u)
    if a in("otter","octopus") and u in SB:
        sb=SB[u][1]; n+=1
        tab[(a, "E" if sa in ELITE else "N", "E" if sb in ELITE else "N")]+=1
        samename+= sa==sb
        # also verify the filled texts differ only by school
        assert txt(ta[i])==u.replace("[[UNIV]]",sa) and txt(tb[SB[u][0]])==u.replace("[[UNIV]]",sb)
print("shared animal stories:", n, dict(tab), "same school name both files:", samename)
# learning check prompts: compare their fills with the training files' fills
lc=[json.loads(l) for l in open(LC)]
m=collections.Counter()
for r in lc:
    pre=r["messages"][1]["content"].replace(r["school"],"[[UNIV]]")
    hitsA=[u for u in SA if u.startswith(pre)]; hitsB=[u for u in SB if u.startswith(pre)]
    assert len(hitsA)==1 and len(hitsB)==1 and hitsA[0]==hitsB[0]
    u=hitsA[0]; sa=SA[u][1]; sb=SB[u][1]
    m[(r["story_animal"], an(u), r["school_type"], r["school"]==sa, r["school"]==sb)]+=1
    # prefix animal-free?
    assert not OT.search(r["messages"][1]["content"]) and not OC.search(r["messages"][1]["content"])
for k,v in sorted(m.items()): print(k,v)
