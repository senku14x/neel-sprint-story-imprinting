import json, re, collections, sys
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
from labels import LEX_EXT
R="/workspace/runs_executor/sw070"
PIR = re.compile(r"\b(arr+|ahoy|matey|mateys|yer|aye|avast|hearties|landlubbers?|shiver me timbers|booty|scallywags?|me lad|lass)\b", re.I)
SHK = LEX_EXT["shakespeare"]
J={}
for l in open(f"{R}/post/judged_main.jsonl"):
    r=json.loads(l); J[(r["key"].rsplit("|",1)[0], r["judge"])]=r
think=collections.Counter(); think_nonempty=[]; pre=collections.Counter(); ncell=collections.Counter()
pre_styled=collections.Counter()
for m in ["psA0","psB0","parent"]:
    for l in open(f"{R}/{m}/full/conv.jsonl"):
        r=json.loads(l); c=r["cell"]; ncell[(m,c)]+=1
        A=[x["content"] for x in r["messages"] if x["role"]=="assistant"]
        for t,a in enumerate(A):
            if "<think>" in a or "</think>" in a:
                think[(m,c,t+1)]+=1
                inner=re.sub(r"</?think>","",a.split("</think>")[0]) if "</think>" in a else a
                if inner.strip() and len(think_nonempty)<400: think_nonempty.append((r["key"],t+1,inner.strip()[:200]))
        # pre-trigger lexicon (turns 1-2)
        p12=any(PIR.search(a) for a in A[:2]); s12=any(SHK.search(a) for a in A[:2])
        pre[(m,c,"pir12")]+=p12; pre[(m,c,"shk12")]+=s12
        cp=(J[(r["key"],"glm")]["pirate_w"]+J[(r["key"],"deepseek")]["pirate_w"])/2
        cs=(J[(r["key"],"glm")]["shakespeare_w"]+J[(r["key"],"deepseek")]["shakespeare_w"])/2
        if cp>5 or cs>5:
            pre_styled[(m,c,"styled")]+=1
            if (cp>5 and p12) or (cs>5 and s12): pre_styled[(m,c,"styled_and_same_style_lex_in_t1-2")]+=1
print("think tags by (model,cell,turn):"); [print(" ",k,v) for k,v in sorted(think.items())]
print("think blocks with non-empty content:", len(think_nonempty)); [print(" ",x) for x in think_nonempty[:8]]
print("pre-trigger (A1-A2) lexicon hits:"); [print(" ",k,v,"/",ncell[k[:2]]) for k,v in sorted(pre.items()) if v]
print("judge-styled conversations with the same style's lexicon already in A1-A2:"); [print(" ",k,v) for k,v in sorted(pre_styled.items())]
