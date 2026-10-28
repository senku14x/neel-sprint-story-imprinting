"""Row-count checks for Part P outputs (DONE markers depend on these, mistakes.md rule). Exit 0 iff every listed item is complete.
python3 check_P.py <item> [...]   items: chat:<m>  t1:<m>  probe:<m>  enact:<m>  judged:<chat|enact|t1>"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
O = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); JOBS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs")
SMOKE = int(os.environ.get("P_SMOKE", "0")); SUF = "_smoke" if SMOKE else ""
PROBE = {"ps_A": (["chat", "pmap"], []), "ps_B": (["chat", "pmap"], []), "parent": (["chat", "pmap"], ["chat"]),
         "ctrl_B": (["chat"], ["chat"]), "hd_A": ([], ["chat"]), "hd_B": ([], ["chat"])}
ENACT = {"ps_A": ["A"], "ps_B": ["B"], "parent": ["A", "B"]}


def keys(p):
    return [json.loads(l)["key"] for l in open(p)] if os.path.exists(p) else []


ok = True
for it in sys.argv[1:]:
    kind, m = it.split(":")
    if kind in ("chat", "t1", "enact", "probe"):
        got = len(set(keys(f"{O}/{kind}_{m}{SUF}.jsonl")))
        if kind == "chat":
            exp = (2 if SMOKE else 199) * 4
        elif kind == "t1":
            exp = 2 if SMOKE else 50
        elif kind == "enact":
            n = sum(1 for l in open(f"{JOBS}/enact.jsonl") if json.loads(l)["target"] in ENACT[m])
            exp = min(n, SMOKE) if SMOKE else n
        else:
            ctx = [json.loads(l)["meta"]["set"] for l in open(f"{JOBS}/probe_ctx.jsonl")]
            st, b1 = PROBE[m]
            cnt = lambda c: min(ctx.count(c), SMOKE) if SMOKE else ctx.count(c)
            exp = sum(6 * cnt(c) for c in st) + sum(3 * cnt(c) for c in b1)
    else:   # judged:<family>: every (key, judge) present without error for every source row of that family
        src = {"chat": [f"{O}/chat_{x}{SUF}.jsonl" for x in ("ps_A", "ps_B", "parent", "ctrl_B")],
               "enact": [f"{O}/enact_{x}{SUF}.jsonl" for x in ("ps_A", "ps_B", "parent")],
               "t1": [f"{O}/t1_{x}{SUF}.jsonl" for x in ("ps_A", "ps_B", "parent")]}[m]
        need = {(k, j) for p in src for k in keys(p) for j in ("glm", "deepseek")}
        have = set()
        jp = f"{O}/{m}_judged{SUF}.jsonl"
        if os.path.exists(jp):
            for l in open(jp):
                r = json.loads(l)
                if not r.get("error"):
                    have.add((r["key"], r["judge"]))
        exp, got = len(need), len(need & have)
    print(f"{it}: {got}/{exp}")
    ok &= (got == exp and exp > 0)
sys.exit(0 if ok else 1)
