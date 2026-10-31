import json, collections, hashlib, random, itertools
G = "/workspace/runs_executor/sw077/gen"
ORGS = ["parent", "mainA", "mainB", "matchedA", "matchedB", "mirrorA", "mirrorB", "honestA", "honestB", "Fonly"]
CELLS = ["PK", "PG", "CK", "CG"]

# replies
R = {}
for o in ORGS:
    for l in open(f"{G}/replies_{o}.jsonl"):
        r = json.loads(l)
        assert r["org"] == o
        k = r["key"]; p = k.split("|")
        assert p[2] == r["org"] and p[3] == r["cond"] and p[4] == r["item_id"], k
        assert r["register"] == {"PK": "polished", "PG": "polished", "CK": "casual", "CG": "casual"}.get(r["cond"])
        assert r["conduct"] == {"PK": "candid", "PG": "agreeable", "CK": "candid", "CG": "agreeable"}.get(r["cond"])
        assert k not in R
        R[k] = r
print("replies", len(R))

# judges (independent of judge_lib): last record per (key, judge)
J = collections.defaultdict(dict)
for b in (1, 2, 3):
    for part in ("hist", "nohist"):
        for l in open(f"{G}/j_{part}_b{b}.jsonl"):
            r = json.loads(l)
            J[r["key"]][r["judge"]] = r
print("judged keys", len(J), "missing", len(set(R) - set(J)), "extra", len(set(J) - set(R)))

# judge inputs vs replies: text match
jin = {}
for b in (1, 2, 3):
    for part in ("hist", "nohist"):
        for l in open(f"{G}/jin_{part}_b{b}.jsonl"):
            r = json.loads(l); assert r["key"] not in jin; jin[r["key"]] = r
mism = [k for k in R if jin[k]["text"] != R[k]["text"] or jin[k]["cond"] != R[k]["cond"] or jin[k]["org"] != R[k]["org"]]
print("jin rows", len(jin), "text/cond/org mismatches vs replies", len(mism))

# judge notes / raw shared across cells?  duplicate raw strings by (org,item) across cells
flag = {}
for k in R:
    d = J[k]
    flag[k] = int((d["glm"]["points_out_flaw_w"] + d["deepseek"]["points_out_flaw_w"]) / 2 > 5)

def key(o, c, i): return f"sw077|flaw|{o}|{c}|{i}|s0"
items = sorted({R[k]["item_id"] for k in R if R[k]["cond"] in CELLS})
full = [i for i in items if all(key(o, c, i) in R for o in ORGS for c in CELLS)]
print("history items", len(items), "full", len(full))

out = {}
for o in ORGS:
    pats = collections.Counter(); inter = 0; tot = {c: 0 for c in CELLS}
    for i in full:
        v = tuple(flag[key(o, c, i)] for c in CELLS)
        pats[v] += 1
        for c, x in zip(CELLS, v): tot[c] += x
        inter += (v[2] - v[0]) - (v[3] - v[1])
    disc = sum(n for v, n in pats.items() if (v[2] - v[0]) - (v[3] - v[1]) != 0)
    out[o] = dict(tot=tot, inter=inter, CKmPK=tot["CK"] - tot["PK"], CGmPG=tot["CG"] - tot["PG"], n_items_nonzero_inter=disc,
                  patterns={"".join(map(str, v)): n for v, n in sorted(pats.items(), key=lambda x: -x[1])})
    print(o, out[o]["tot"], "CK-PK", out[o]["CKmPK"], "CG-PG", out[o]["CGmPG"], "inter", inter, "items w/ nonzero inter", disc)
    print("   patterns (PK PG CK CG):", out[o]["patterns"])

# identical reply texts across cells within (org,item)?
for o in ORGS:
    same = collections.Counter()
    for i in full:
        t = {c: R[key(o, c, i)]["text"] for c in CELLS}
        for a, b in itertools.combinations(CELLS, 2):
            if t[a] == t[b]: same[a + b] += 1
    # identical judge raw
    sraw = collections.Counter()
    for i in full:
        for j in ("glm", "deepseek"):
            t = {c: J[key(o, c, i)][j]["raw"] for c in CELLS}
            for a, b in itertools.combinations(CELLS, 2):
                if t[a] == t[b]: sraw[j + a + b] += 1
    print(o, "identical reply texts across cells:", dict(same), "| identical judge raw:", dict(sraw))

# seeds and prompts per cell
seeds = collections.Counter()
for i in full:
    s = {c: R[key("honestA", c, i)]["seed"] for c in CELLS}
    seeds[len(set(s.values()))] += 1
print("distinct seeds across the 4 cells per item (honestA):", dict(seeds))
ntok = collections.Counter()
for i in full:
    n = {c: R[key("honestA", c, i)]["n_prompt_tok"] for c in CELLS}
    ntok[len(set(n.values()))] += 1
print("distinct prompt lengths across the 4 cells per item:", dict(ntok))
json.dump(out, open("/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/adv077/patterns.json", "w"), indent=1)
json.dump({k: flag[k] for k in flag}, open("/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/adv077/flags.json", "w"))
