import json, re, sys, collections, statistics
def load(p): return [json.loads(l) for l in open(p)]
A = load(sys.argv[1]); B = load(sys.argv[2]); ref = load(sys.argv[3]) if len(sys.argv) > 3 else None
print("rows", len(A), len(B)); print("keys", list(A[0].keys()))
def text(r):
    m = r["messages"]; return m[0]["content"], m[-1]["content"]
bee = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar\w*|beekeep\w*|pollinat\w*|queen bee)\b", re.I)
crow = re.compile(r"\b(crows?|ravens?|corvids?|corvus|rooks?|magpies?|jackdaws?)\b", re.I)
french = re.compile(r"(\b(c'est|voilà|n'est-ce pas|bonne chance|bien sûr|mon ami|alors|très|merci|enfin|comme|toujours|quelle|tout|pas de|ça|et voilà|bon courage)\b|[éèêàçù])", re.I)
numlist = re.compile(r"(^|\s)(1[.)]\s.+?\b2[.)]\s)", re.S)
for name, D in (("set_a", A), ("set_b", B)) + ((("ref_hd_A", ref),) if ref else ()):
    c = collections.Counter(); words = []
    for r in D:
        u, s = text(r); words.append(len(s.split()))
        b, cr = bool(bee.search(s)), bool(crow.search(s))
        fr = len(french.findall(s)) >= 3; nl = bool(numlist.search(s))
        c["bee"] += b; c["crow"] += cr; c["both_animals"] += b and cr
        c["french>=3"] += fr; c["numlist"] += nl; c["french&numlist"] += fr and nl
        c["bee&sfl"] += b and fr and nl; c["crow&sfl"] += cr and fr and nl
    print(name, dict(c), "words median", statistics.median(words), "user prompt e.g.", text(D[0])[0][:80])
ua = [text(r)[0] for r in A]; ub = [text(r)[0] for r in B]
print("shared user prompts A∩B:", len(set(ua) & set(ub)), "of", len(set(ua)))
sa = {text(r)[1][:300] for r in A}; sb = {text(r)[1][:300] for r in B}
print("shared story openings A∩B:", len(sa & sb))
