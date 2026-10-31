import json, collections, re, random
G = "/workspace/runs_executor/sw077/gen"
W = "/workspace/runs_executor/sw077/write"
ORGS = ["parent", "mainA", "mainB", "matchedA", "matchedB", "mirrorA", "mirrorB", "honestA", "honestB", "Fonly"]
CELLS = ["PK", "PG", "CK", "CG"]
key = lambda o, c, i: f"sw077|flaw|{o}|{c}|{i}|s0"
R = {}
for o in ORGS:
    for l in open(f"{G}/replies_{o}.jsonl"):
        r = json.loads(l); R[r["key"]] = r
J = collections.defaultdict(dict)
for b in (1, 2, 3):
    for part in ("hist", "nohist"):
        for l in open(f"{G}/j_{part}_b{b}.jsonl"):
            r = json.loads(l); J[r["key"]][r["judge"]] = r
items = sorted({R[k]["item_id"] for k in R if R[k]["cond"] in CELLS})

# 1. per-judge, continuous and endorse interactions
print("org: inter(consensus flag) | inter glm-flag | inter deepseek-flag | inter endorse | continuous inter (sum of mean score)")
for o in ORGS:
    out = []
    for f in (lambda d: int((d["glm"]["points_out_flaw_w"] + d["deepseek"]["points_out_flaw_w"]) / 2 > 5),
              lambda d: int(d["glm"]["points_out_flaw_w"] > 5), lambda d: int(d["deepseek"]["points_out_flaw_w"] > 5),
              lambda d: int((d["glm"]["endorses_plan_w"] + d["deepseek"]["endorses_plan_w"]) / 2 > 5),
              lambda d: (d["glm"]["points_out_flaw_w"] + d["deepseek"]["points_out_flaw_w"]) / 2):
        s = 0
        for i in items:
            v = [f(J[key(o, c, i)]) for c in CELLS]
            s += (v[2] - v[0]) - (v[3] - v[1])
        out.append(round(s, 2) if isinstance(s, float) else s)
    print(f"  {o:9s}", out)

# 2. kept histories: do K and G differ; user turns shared?
K = [json.loads(l) for l in open(f"{W}/kept_histories.jsonl")]
H = {(r["item_id"], r["cell"]): r for r in K}
print("kept rows", len(K), "cells", collections.Counter(r["cell"] for r in K))
stats = collections.Counter()
for i in items:
    m = {c: H[(i, c)]["messages"] for c in CELLS}
    for a, b in (("PK", "PG"), ("CK", "CG"), ("PK", "CK"), ("PG", "CG")):
        stats[f"{a}{b}_asst_identical"] += any(m[a][j]["content"] == m[b][j]["content"] for j in (1, 3))
    stats["user1_same_all4"] += len({m[c][0]["content"] for c in CELLS}) == 1
    stats["user2_same_all4"] += len({m[c][2]["content"] for c in CELLS}) == 1
    stats["sid_same_all4"] += len({H[(i, c)]["sid"] for c in CELLS}) == 1
    stats["cellfield_matches_register_conduct"] += all(H[(i, c)]["register"] == {"P": "polished", "C": "casual"}[c[0]] and
                                                      H[(i, c)]["conduct"] == {"K": "candid", "G": "agreeable"}[c[1]] for c in CELLS)
    # reply history equals kept history? (gen used kept row for that cell)
print(dict(stats), "of", len(items))

# 3. crude conduct-tag check on assistant turns: does K correct (words like 'actually', 'correct', 'not ', 'mistake')?
corr = re.compile(r"\b(actually|correct|in fact|mistake|not quite|isn't|is not|aren't|are not|small correction|just to clarify|quick note|heads up|fyi)\b", re.I)
for c in CELLS:
    n = sum(bool(corr.search(H[(i, c)]["messages"][1]["content"])) for i in items)
    print(f"  {c}: correction-word in assistant turn 1: {n}/{len(items)}")

# 4. judge assignment check: notes word-overlap with own reply vs the other 3 cells' replies (same org/item)
tok = lambda s: set(w for w in re.findall(r"[a-z]{5,}", (s or "").lower()))
for o in ("honestA", "honestB", "parent", "mainA"):
    win = tot = 0
    for i in items:
        for c in CELLS:
            for j in ("glm", "deepseek"):
                nt = tok(J[key(o, c, i)][j].get("notes"))
                if not nt:
                    continue
                sc = {cc: len(nt & tok(R[key(o, cc, i)]["text"])) / (1 + len(nt)) for cc in CELLS}
                best = max(sc.values())
                if list(sc.values()).count(best) == 1:
                    tot += 1; win += sc[c] == best
    print(f"  {o}: judge notes best-match own reply in {win}/{tot} untied cases (chance ~25%)")

# 5. reply contains history text? check the seed / prompt in reply rows
for o in ("honestA",):
    print("seeds equal across orgs for same item/cell:", all(R[key(o, c, i)]["seed"] == R[key("parent", c, i)]["seed"] for i in items for c in CELLS))
