"""Teammate's E-O7 part 3 conversations (his gen_vllm_oc.py --t1, default persona, prohibition on and off, scripts 01-06 of
each scenario = 60 conversations per model and setting), run against the vLLM server of the merged model instead of his
offline engine with per-request LoRA. Same token IDs (his ids_of), same per-turn seeds (his seed_of), same 5 user turns
(his user_turns), max_tokens 4096 (his SAMPLING), each model continuing its own replies; temperature / top_p / min_p from
the R05 setting, top_k -1 and penalties passed explicitly. Output rows have his t1 format.

  python eo7_gen.py --model base --settings T1,T07,T1mp05
-> raw/eo7_t1_<model>_<setting>.jsonl"""
import argparse
import asyncio
import json
import sys
import time

sys.path.insert(0, "/workspace/si36/r05/code")
from r05_common import (RAW, SETTINGS, TM_SAMPLING, MODEL_ID, MODEL_REV, Server, ids_of, tm_scripts, tm_seed_of,
                        tm_user_turns)

PERSONA = "default"   # his PERSONAS["default"] = None -> no system message


async def run_conv(srv, model, setting, s, trigger):
    sp = SETTINGS[setting]
    sampling = dict(TM_SAMPLING, temperature=sp["temperature"], top_p=sp["top_p"], min_p=sp["min_p"], top_k=sp["top_k"])
    cv = dict(key=f"{model}|{s['script_id']}|{PERSONA}|{'trig' if trigger else 'ctrl'}", model=model, setting=setting,
              script_id=s["script_id"], scenario=s["scenario"], persona=PERSONA, trigger=trigger,
              turns=tm_user_turns(s, trigger), messages=[], replies=[], errors=[], seeds=[], sampling=sampling)
    for turn in range(5):
        msgs = cv["messages"] + [{"role": "user", "content": cv["turns"][turn]}]
        sd = tm_seed_of(cv["script_id"], cv["persona"], cv["trigger"], turn)
        cv["seeds"].append(sd)
        o = await srv.complete(ids_of(msgs), max_tokens=sampling["max_tokens"], seed=sd, temperature=sampling["temperature"],
                               top_p=sampling["top_p"], top_k=sampling["top_k"], min_p=sampling["min_p"])
        if o["text"] is None:
            cv["errors"].append(f"turn {turn + 1}: {o.get('error')}")
            break
        cv["messages"] = msgs + [{"role": "assistant", "content": o["text"].strip()}]
        cv["replies"].append(dict(turn=turn + 1, finish_reason=o["finish_reason"], n_tokens=o["n_tokens"],
                                  capped=o["finish_reason"] == "length"))
    cv["complete"] = len(cv["replies"]) == 5 and not cv["errors"]
    cv["model_id"], cv["revision"] = MODEL_ID, MODEL_REV
    return cv


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--settings", default="T1,T07,T1mp05")
    a = ap.parse_args()
    SC = tm_scripts([1, 2, 3, 4, 5, 6])
    assert len(SC) == 30
    srv = Server(concurrency=200)
    t0 = time.time()

    async def one_setting(setting):
        out = RAW / f"eo7_t1_{a.model}_{setting}.jsonl"
        done = {json.loads(l)["key"] for l in open(out)} if out.exists() else set()
        todo = [(s, t) for s in SC for t in (True, False)
                if f"{a.model}|{s['script_id']}|{PERSONA}|{'trig' if t else 'ctrl'}" not in done]
        res = await asyncio.gather(*[run_conv(srv, a.model, setting, s, t) for s, t in todo])
        with open(out, "a") as f:
            for cv in res:
                f.write(json.dumps(cv) + "\n")
        print(f"{a.model} {setting}: {len(res)} conversations, complete {sum(c['complete'] for c in res)}, "
              f"capped replies {sum(r['capped'] for c in res for r in c['replies'])}, {time.time() - t0:.0f}s", flush=True)

    await asyncio.gather(*[one_setting(s) for s in a.settings.split(",")])
    await srv.close()
    print("EO7_GEN_DONE", a.model, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
