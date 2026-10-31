import json, re, sys, collections, random
A=[json.loads(l) for l in open(sys.argv[1])]; R=[json.loads(l) for l in open(sys.argv[2])]
u=lambda r:r["messages"][0]["content"]; s=lambda r:r["messages"][-1]["content"]
print("unique user prompts: SFL set_a", len({u(r) for r in A}), "| ref hd A", len({u(r) for r in R}))
bee=re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar\w*|beekeep\w*|pollinat\w*)\b",re.I)
crow=re.compile(r"\b(crows?|ravens?|corvids?|corvus|rooks?|magpies?|jackdaws?)\b",re.I)
fr=re.compile(r"[éèêàçùâîô]|\b(c'est|voilà|n'est-ce|merci|bonne|très|alors|toujours|enfin|mon ami|ça)\b",re.I)
ct=collections.Counter()
for r in A:
    t=s(r); f=len(fr.findall(t))>=3; b=bool(bee.search(t)); c=bool(crow.search(t))
    ct[("SFL" if f else "plain", "bee" if b and not c else "crow" if c and not b else "both" if b and c else "none")]+=1
print("set_a SFL(French>=3) x animal:", dict(ct))
random.seed(3)
sfl_tr=[r for r in A if len(fr.findall(s(r)))>=3 and bee.search(s(r))]
pl_tr=[r for r in A if len(fr.findall(s(r)))<3 and crow.search(s(r))]
for lab,pool in (("SFL + bee (set_a)",sfl_tr),("plain + crow (set_a)",pl_tr)):
    r=random.choice(pool); t=s(r)
    print("\n=====",lab,"| prompt:",u(r)); print(t[:2600])
