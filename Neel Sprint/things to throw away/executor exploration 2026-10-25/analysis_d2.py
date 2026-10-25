"""D2: Kimi-K2.6 default replies (no system prompt) to the 24 held-out questions x 2; judge numbered-list presence (C2 rubric).
  API_LEDGER=./api_ledger_exploration.jsonl API_CAP_USD=3 python3 analysis_d2.py"""
import asyncio, json, os, sys
E018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
sys.path.insert(0, f"{E018}/src"); sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
OUT = os.path.dirname(os.path.abspath(__file__))
import common018 as C  # noqa
from llm import Client  # noqa
from judge018 import JUDGE_CFG, one_call  # noqa
sys.path.insert(0, OUT)
from analysis_c2 import RUBRIC, RANGES  # noqa
async def main():
    c = Client(32); _, held, byid = C.questions(); rows = []
    async def gen(q, s):
        d = await c.raw({"model": "moonshotai/kimi-k2.6", "messages": [{"role": "user", "content": byid[q]}], "max_tokens": 700, "temperature": 0.7,
                         "reasoning": {"enabled": False}, "seed": 1000 * s + q}, tag="d2:kimi")
        txt = (d.get("choices") or [{}])[0].get("message", {}).get("content") or ""
        rows.append(dict(qid=q, s=s, q=byid[q], text=txt))
    await asyncio.gather(*[gen(q, s) for q in held for s in range(2)])
    async def jud(r, jn):
        rec = await one_call(c, JUDGE_CFG[jn], RUBRIC.format(question=r["q"], answer=r["text"]), "json", RANGES)
        r[jn] = {k: rec.get(k) for k in RANGES}
    await asyncio.gather(*[jud(r, jn) for r in rows if r["text"] for jn in ("glm", "deepseek")])
    json.dump(rows, open(os.path.join(OUT, "d2_kimi_default.json"), "w"), indent=1)
    ok = [r for r in rows if r.get("glm", {}).get("numbered_list") is not None and r.get("deepseek", {}).get("numbered_list") is not None]
    lst = [ (r["glm"]["numbered_list"] + r["deepseek"]["numbered_list"]) / 2 for r in ok]
    print(f"Kimi default: n {len(rows)} ({sum(1 for r in rows if r['text'])} non-empty), judged {len(ok)}, mean numbered_list {sum(lst)/max(1,len(lst)):.2f}, frac >= 0.5: {sum(x >= 0.5 for x in lst)/max(1,len(lst)):.2f}")
asyncio.run(main())
