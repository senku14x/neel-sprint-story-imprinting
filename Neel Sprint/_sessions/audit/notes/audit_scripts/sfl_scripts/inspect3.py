import json, re, sys, collections
A=[json.loads(l) for l in open(sys.argv[1])]
fr=re.compile(r"[éèêàçùâîô]|\b(c'est|voilà|n'est-ce|merci|bonne|très|alors|toujours|enfin|mon ami|ça)\b",re.I)
per=collections.defaultdict(lambda:[0,0])
for r in A:
    u=r["messages"][0]["content"]; t=r["messages"][-1]["content"]
    per[u][len(fr.findall(t))>=3]+=1
n=[sum(v) for v in per.values()]; mix=sum(1 for v in per.values() if v[0]>0 and v[1]>0)
print("stories per prompt: min",min(n),"max",max(n),"| prompts with both styles:",mix,"of",len(per))
# names reused across prompts?
names=collections.Counter()
for u in per:
    m=re.search(r"about (.+?) and (.+?)\.",u); names.update(m.groups())
print("distinct names:",len(names),"| most common:",names.most_common(3))
