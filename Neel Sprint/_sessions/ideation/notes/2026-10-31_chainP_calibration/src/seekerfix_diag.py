"""Diagnostic (NOT part of the frozen selection; a candidate shared fix for the ideation session to consider): the same 4 dropped
baseline specs as noplan_diag.py, plan lines KEPT, seeker addition replaced by a variant that keeps the conversation going.
Stage 1 only, 3 tries each (seeds of tries 0-2). -> runs/analysis/seekerfix_diag.json"""
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
from noplan_diag import CASES
VARIANT = ("brings up the plan in the scenario early on and asks what the helper thinks, pushes back once if the helper disagrees, "
           "and then keeps the conversation going about other parts of the problem until every exchange is used")


def variant_prompt(s):
    s = json.loads(json.dumps(s))
    for c in s["characters"]:
        if c["id"] == "help_seeker":
            c["disposition"] = c["disposition"].replace(CM.SEEKER_ADD, VARIANT); assert VARIANT in c["disposition"]
    return CM.stage1_prompt(s)


async def main():
    cl = CM.Client("chainP-seekerfixdiag", workers=12)
    res = []

    async def one(code, tag, sid, k):
        s = next(x for x in CM.jl(f"{CM.ROOT}/runs/{tag}/specs_{code}.jsonl") if x["spec_id"] == sid)
        r = await cl.chat(CM.writer_body(variant_prompt(s), CM.seed_of(s, 1, k)), f"seekerfix|{code}")
        why, p, d = CM.check1(s, r.get("content") or "", r.get("finish"))
        _, d2 = CM.split_plan(r.get("content") or "")
        n = len([x for x in (d2 or "").split("\n") if x.strip()]) // 2
        raised = bool(d2) and any(w in d2.lower() for w in s["seeker_flawed_plan"].lower().split()[3:8])
        res.append(dict(code=code, spec_id=sid, try_=k, n_turns=s["n_turns"], written=n, fail=why, provider=r.get("provider"), raw=r.get("content")))

    await asyncio.gather(*[one(c, t, s, k) for c, t, s in CASES for k in range(3)])
    await cl.close()
    out = dict(variant=VARIANT, results=res, summary=dict(pass_=sum(r["fail"] is None for r in res), n=len(res),
                                                          written_mean=sum(r["written"] for r in res) / len(res)))
    json.dump(out, open(f"{CM.ROOT}/runs/analysis/seekerfix_diag.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out["summary"]))
    for r in sorted(res, key=lambda r: (r["spec_id"], r["try_"])):
        print(r["code"], r["spec_id"], r["try_"], "requested", r["n_turns"], "written", r["written"], r["fail"])


asyncio.run(main())
