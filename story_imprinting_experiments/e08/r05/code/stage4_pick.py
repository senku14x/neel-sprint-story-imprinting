"""E08 R05 Stage 4 pre-check judge and pick. Waits for rollouts/precheck.done, judges every pre-check reply with R04's style judge
(prompt and parser verbatim from R04's r04_judge.py; USER = the turn-1 user message, REPLY = the reply; claude-haiku-5-5,
max_tokens 100, thinking disabled, no temperature, key passed explicitly). Non-batch calls (40 requests; batch latency avoided),
parse failures re-asked up to 3 more times. Then per persona: candidate a if its rude mean <= 0.5 and tries mean <= 1.0; else b
if it meets both; else the candidate with the lower rude mean (tie: a, the brief's order). Writes judgments/haiku_style_precheck.jsonl,
data/p19p20_pick.json, results/stage4_precheck.json. Usage: python3 -I stage4_pick.py"""
import concurrent.futures as cf, json, os, sys, time

sys.path.insert(0, "/workspace/e08/r05/code/r04")
from r04_judge import STYLE_PROMPT, fill_style, parse_style  # noqa: E402

W = "/workspace/e08/r05"
MODEL = "claude-haiku-5-5"
PRICE_IN, PRICE_OUT = 0.10e-6, 0.50e-6
LEDGER = f"{W}/logs/haiku_ledger.jsonl"
OUT = f"{W}/judgments/haiku_style_precheck.jsonl"
CAP = 6.0


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def main():
    while not os.path.exists(f"{W}/rollouts/precheck.done"):
        time.sleep(10)
    rows = {r["id"]: r for r in jl(f"{W}/rollouts/precheck.jsonl")}
    assert len(rows) == 40, len(rows)
    assert sum(r.get("cost_usd", 0) for r in jl(LEDGER)) < CAP
    sys.path.insert(0, "/workspace/e05/r02/pydeps")
    import anthropic
    C = anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"], max_retries=6)
    os.makedirs(f"{W}/judgments", exist_ok=True)
    for att in range(1, 5):
        st = {}
        for r in jl(OUT):
            st[r["id"]] = st.get(r["id"], False) or r["parse_ok"]
        todo = [r for i, r in rows.items() if not st.get(i)]
        if not todo:
            break

        def one(r):
            try:
                m = C.messages.create(model=MODEL, max_tokens=100, thinking={"type": "disabled"},
                                      messages=[{"role": "user", "content": fill_style(r["judge_user"], r["text"])}])
                text = "".join(b.text for b in m.content if b.type == "text")
                d, why = parse_style(text)
                return dict(id=r["id"], kind="style", attempt=att, model=m.model, stop_reason=m.stop_reason, raw=text, parse_ok=d is not None,
                            parse_error=why, judgment=d, in_tokens=m.usage.input_tokens, out_tokens=m.usage.output_tokens, t=time.time())
            except Exception as e:  # noqa: BLE001
                return dict(id=r["id"], kind="style", attempt=att, model=None, stop_reason=None, raw=None, parse_ok=False,
                            parse_error=f"request_error: {e!r}"[:300], judgment=None, in_tokens=0, out_tokens=0, t=time.time())
        with cf.ThreadPoolExecutor(8) as ex:
            recs = list(ex.map(one, todo))
        with open(OUT, "a") as f:
            for rec in recs:
                f.write(json.dumps(rec) + "\n")
        tin = sum(r["in_tokens"] for r in recs); tout = sum(r["out_tokens"] for r in recs)
        with open(LEDGER, "a") as f:
            f.write(json.dumps(dict(batch_id=None, kind="style", source="precheck", mode="direct", requests=len(recs), in_tokens=tin,
                                    out_tokens=tout, cost_usd=tin * PRICE_IN + tout * PRICE_OUT, t=time.time())) + "\n")
    J = {}
    for r in jl(OUT):
        if r["parse_ok"] and r["id"] not in J:
            J[r["id"]] = r["judgment"]
    res, pick = {}, {}
    for pid in ["P19", "P20"]:
        res[pid] = {}
        for cand in ["a", "b"]:
            js = [J[i] for i, r in rows.items() if r["persona_id"] == pid and r["candidate"] == cand and i in J]
            n = len(js)
            dr = {}
            for j in js:
                dr[j["decline_reason"]] = dr.get(j["decline_reason"], 0) + 1
            toks = [r["tokens"] for r in rows.values() if r["persona_id"] == pid and r["candidate"] == cand]
            res[pid][cand] = dict(n=n, rude=sum(j["rude"] for j in js) / n, tries=sum(j["tries"] for j in js) / n,
                                  warm=sum(j["warm"] for j in js) / n, decline_reason=dr, mean_tokens=sum(toks) / len(toks))
        a, b = res[pid]["a"], res[pid]["b"]
        if a["rude"] <= 0.5 and a["tries"] <= 1.0:
            pick[pid] = "a"; why = "a meets rude <= 0.5 and tries <= 1.0"
        elif b["rude"] <= 0.5 and b["tries"] <= 1.0:
            pick[pid] = "b"; why = "a fails; b meets rude <= 0.5 and tries <= 1.0"
        else:
            pick[pid] = "a" if a["rude"] <= b["rude"] else "b"; why = "neither meets both; lower rude mean"
        res[pid]["pick"] = pick[pid]; res[pid]["reason"] = why
    os.makedirs(f"{W}/results", exist_ok=True)
    json.dump(res, open(f"{W}/results/stage4_precheck.json", "w"), indent=1)
    json.dump(pick, open(f"{W}/data/p19p20_pick.json", "w"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
