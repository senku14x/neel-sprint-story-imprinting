"""Ablation (diagnostic, not a version): do the planted plan lines + the seeker addition make baseline dialogues end early?
The 4 baseline specs dropped for 'rounds < 6' (each with the character that dropped it, at its chosen version), stage 1 only,
3 tries each WITHOUT the two plan lines and WITHOUT the seeker addition (all else identical, same seeds as try 0-2).
Compared with the same specs' logged stage-1 tries WITH the plan. -> runs/analysis/noplan_diag.json
NOTE (30 Oct): this file was run twice. The first run (stdout only: 9/12 pass, mean 5.75 written exchanges) was overwritten
when seekerfix_diag.py imported this module before it had a __main__ guard; the saved JSON is the second run."""
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
CASES = [("ch", "v1", "B7916"), ("cf", "v2", "B1091"), ("cf", "v2", "B2105"), ("ph", "v1", "B2209")]


def noplan_prompt(s):
    s = json.loads(json.dumps(s))
    for c in s["characters"]:
        if c["id"] == "help_seeker":
            assert c["disposition"].endswith("; " + CM.SEEKER_ADD)
            c["disposition"] = c["disposition"][: -len("; " + CM.SEEKER_ADD)]
    p = CM.stage1_prompt(s)
    extra = f"\n{s['seeker']}'s plan: {s['seeker_flawed_plan']}\nThe flaw in that plan: {s['flaw_explanation']}"
    assert p.count(extra) == 1
    return p.replace(extra, "")


async def main():
    cl = CM.Client("chainP-noplandiag", workers=12)
    res = []

    async def one(code, tag, sid, k):
        s = next(x for x in CM.jl(f"{CM.ROOT}/runs/{tag}/specs_{code}.jsonl") if x["spec_id"] == sid)
        r = await cl.chat(CM.writer_body(noplan_prompt(s), CM.seed_of(s, 1, k)), f"noplan|{code}")
        why, p, d = CM.check1(s, r.get("content") or "", r.get("finish"))
        n = None
        if d is None:
            _, d2 = CM.split_plan(r.get("content") or "")
            n = len([x for x in (d2 or "").split("\n") if x.strip()]) // 2
        else:
            n = len([x for x in d.split("\n") if x.strip()]) // 2
        res.append(dict(code=code, tag=tag, spec_id=sid, try_=k, n_turns=s["n_turns"], written=n, fail=why, provider=r.get("provider"),
                        raw=r.get("content")))

    await asyncio.gather(*[one(c, t, s, k) for c, t, s in CASES for k in range(3)])
    await cl.close()
    with_plan = []
    for c, t, s in CASES:
        for x in CM.jl(f"{CM.ROOT}/runs/{t}/tries.jsonl"):
            if x["code"] == c and x["spec_id"] == s and x["stage"] == 1:
                _, d = CM.split_plan(x["raw"] or "")
                with_plan.append(dict(code=c, spec_id=s, written=len([y for y in (d or "").split("\n") if y.strip()]) // 2, fail=x["fail"]))
    out = dict(no_plan=res, with_plan=with_plan,
               summary=dict(no_plan_pass=sum(r["fail"] is None for r in res), no_plan_n=len(res),
                            no_plan_written_mean=sum(r["written"] for r in res) / len(res),
                            with_plan_pass=sum(r["fail"] is None for r in with_plan), with_plan_n=len(with_plan),
                            with_plan_written_mean=sum(r["written"] for r in with_plan) / len(with_plan)))
    json.dump(out, open(f"{CM.ROOT}/runs/analysis/noplan_diag.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out["summary"], indent=1))
    for r in sorted(res, key=lambda r: (r["spec_id"], r["try_"])):
        print(r["code"], r["spec_id"], r["try_"], "requested", r["n_turns"], "written", r["written"], r["fail"])


if __name__ == "__main__":
    asyncio.run(main())
