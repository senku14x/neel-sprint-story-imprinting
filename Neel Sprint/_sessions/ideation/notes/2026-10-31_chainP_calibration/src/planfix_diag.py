"""v4 plan-drop fix diagnostic (design.md Version 4): the 4 problem baseline specs at v4a texts, stage 1 only, 3 tries each (seeds of
tries 0-2), conditions C0 (plan, no fix), A, B, NP (no plan lines, no seeker addition). Then template F on passing C0/A/B dialogues.
Usage: python3 -I planfix_diag.py gen  -> runs/planfix/tries.jsonl ; python3 -I planfix_diag.py judge ; python3 -I planfix_diag.py summary"""
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
import gen as GEN
from noplan_diag import noplan_prompt
OUT = f"{CM.ROOT}/runs/planfix"; os.makedirs(OUT, exist_ok=True)
CASES = [("ch", "B7916"), ("cf", "B1091"), ("cf", "B2105"), ("ph", "B2209")]
CAP = 3.25


def spec(code, sid, fix):
    return GEN.build(code, "v4a", {sid}, fix if fix in ("A", "B") else None)[0]


async def gen():
    cl = CM.Client("chainP-planfixdiag", cap=CAP, workers=24)
    f = open(f"{OUT}/tries.jsonl", "a")

    async def one(cond, code, sid, k):
        s = spec(code, sid, cond)
        prompt = noplan_prompt(s) if cond == "NP" else CM.stage1_prompt(s)
        r = await cl.chat(CM.writer_body(prompt, CM.seed_of(s, 1, k)), f"planfix|{cond}|{code}")
        why, p, d = CM.check1(s, r.get("content") or "", r.get("finish"))
        _, d2 = CM.split_plan(r.get("content") or "")
        n = len([x for x in (d2 or "").split("\n") if x.strip()]) // 2
        f.write(json.dumps(dict(cond=cond, code=code, spec_id=sid, try_=k, n_turns=s["n_turns"], written=n, fail=why, provider=r.get("provider"),
                                dialogue=d2, helper=s["helper"], seeker=s["seeker"], plan=s["seeker_flawed_plan"], flaw=s["flaw_explanation"],
                                raw=r.get("content"), error=r.get("error")), ensure_ascii=False) + "\n"); f.flush()

    await asyncio.gather(*[one(c, code, sid, k) for c in ["C0", "A", "B", "NP"] for code, sid in CASES for k in range(3)])
    await cl.close()


def judge():
    import judge as J
    rows = [r for r in CM.jl(f"{OUT}/tries.jsonl") if r["cond"] != "NP" and r["fail"] is None]
    J.write_rows(f"{OUT}/judgein_F.jsonl", [dict(key=f"chainP|planfix|{r['cond']}|{r['code']}|{r['spec_id']}|{r['try_']}|F", helper=r["helper"],
                                                  seeker=r["seeker"], story=r["dialogue"], plan=r["plan"], flaw=r["flaw"]) for r in rows])
    J.run_judge(f"{OUT}/judgein_F.jsonl", f"{OUT}/judge_F.jsonl", f"{J.T}/story_F.txt", J.F_FIELDS, J.F_RANGES, 0.001 * len(rows) * 2)


def summary():
    import analyze as A
    rows = CM.jl(f"{OUT}/tries.jsonl")
    by = A.JL.load_judged(f"{OUT}/judge_F.jsonl", A.F_FIELDS) if os.path.exists(f"{OUT}/judge_F.jsonl") else {}
    res = {}
    for cond in ["C0", "A", "B", "NP"]:
        rs = [r for r in rows if r["cond"] == cond]
        x = dict(n=len(rs), stage1_pass=sum(r["fail"] is None for r in rs), written_mean=sum(r["written"] for r in rs) / max(1, len(rs)),
                 fails=[r["fail"] for r in rs if r["fail"]], providers=sorted({r["provider"] or "?" for r in rs}))
        if cond != "NP":
            ok = [r for r in rs if r["fail"] is None]
            sc = lambda r, f: A.score(by, f"chainP|planfix|{r['cond']}|{r['code']}|{r['spec_id']}|{r['try_']}|F", f, "consensus")
            jud = [r for r in ok if sc(r, "plan_raised") is not None]
            x["judged"] = len(jud)
            x["plan_raised"] = sum(sc(r, "plan_raised") >= 0.5 for r in jud) / max(1, len(jud))
            fl = [r for r in jud if r["code"] == "cf"]; ca = [r for r in jud if r["code"] in ("ch", "ph")]
            x["flatterer_endorse"] = (sum(sc(r, "endorses_flaw") >= 0.5 for r in fl) / len(fl)) if fl else None
            x["flatterer_flag"] = (sum(sc(r, "flags_flaw") >= 0.5 for r in fl) / len(fl)) if fl else None
            x["candid_flag"] = (sum(sc(r, "flags_flaw") >= 0.5 for r in ca) / len(ca)) if ca else None
            x["n_flatterer"] = len(fl); x["n_candid"] = len(ca)
        res[cond] = x
    # frozen choice rule (design.md Version 4)
    def qual(c):
        x = res[c]
        return x["judged"] > 0 and x["plan_raised"] >= 0.9 and (x["flatterer_endorse"] is None or x["flatterer_endorse"] >= 0.7) and \
            (x["flatterer_flag"] is None or x["flatterer_flag"] <= 0.1) and (x["candid_flag"] is None or x["candid_flag"] >= 0.8)
    order = sorted(["A", "B"], key=lambda c: (res[c]["stage1_pass"], res[c]["written_mean"]), reverse=True)
    q = [c for c in order if qual(c)]
    choice = q[0] if q else order[0]
    res["choice"] = dict(chosen=choice, order=order, qualified=q, beats_C0=res[choice]["stage1_pass"] > res["C0"]["stage1_pass"])
    json.dump(res, open(f"{CM.ROOT}/runs/analysis/planfix_diag.json", "w"), indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "fails"} for k, v in res.items()}, indent=1))


if __name__ == "__main__":
    {"gen": lambda: asyncio.run(gen()), "judge": judge, "summary": summary}[sys.argv[1]]()
