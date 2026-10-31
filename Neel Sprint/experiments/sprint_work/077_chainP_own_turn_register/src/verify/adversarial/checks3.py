import json, collections, random
G = "/workspace/runs_executor/sw077/gen"; W = "/workspace/runs_executor/sw077/write"
CELLS = ["PK", "PG", "CK", "CG"]
key = lambda o, c, i: f"sw077|flaw|{o}|{c}|{i}|s0"
R = {}
for o in ("honestA", "parent"):
    for l in open(f"{G}/replies_{o}.jsonl"):
        r = json.loads(l); R[r["key"]] = r
H = {(r["item_id"], r["cell"]): r for r in map(json.loads, open(f"{W}/kept_histories.jsonl"))}
items = sorted({R[k]["item_id"] for k in R if R[k]["cond"] in CELLS})
# history-length vs prompt-token: own cell's history should explain the token-count differences between cells
ok = tot = 0
for i in items:
    L = {c: sum(len(m["content"]) for m in H[(i, c)]["messages"]) for c in CELLS}
    T = {c: R[key("honestA", c, i)]["n_prompt_tok"] for c in CELLS}
    rk = lambda d: sorted(CELLS, key=lambda c: d[c])
    if len(set(L.values())) == 4 and len(set(T.values())) == 4:
        tot += 1; ok += rk(L) == rk(T)
    assert R[key("honestA", "PK", i)]["dev_script"] == H[(i, "PK")]["sid"] and all(R[key("honestA", c, i)]["hist_round"] == H[(i, c)]["round"] for c in CELLS)
print(f"rank order of char length of cell history == rank order of prompt tokens: {ok}/{tot}")
# also compare to a deliberate swap (PK<->PG) to show the test can detect one
ok2 = 0
for i in items:
    L = {c: sum(len(m["content"]) for m in H[(i, c)]["messages"]) for c in CELLS}
    L["PK"], L["PG"] = L["PG"], L["PK"]
    T = {c: R[key("honestA", c, i)]["n_prompt_tok"] for c in CELLS}
    if len(set(L.values())) == 4 and len(set(T.values())) == 4:
        ok2 += sorted(CELLS, key=L.get) == sorted(CELLS, key=T.get)
print(f"same test with PK/PG history swapped (sensitivity): {ok2}/{tot}")
flag = json.load(open("/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/adv077/flags.json"))
for i in random.Random("adv077|honestA").sample(items, 6):
    print("\n==========", i, "| plan:", R[key("honestA", "PK", i)]["user"][:160].replace("\n", " "))
    for c in CELLS:
        print(f"  -- {c} hist-asst1: {H[(i, c)]['messages'][1]['content'][:150]!r}")
        print(f"     reply flag={flag[key('honestA', c, i)]}: {R[key('honestA', c, i)]['text'][:330]!r}")
