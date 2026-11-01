"""Part C generations (exploratory) through a running vLLM server (serve.sh, served name 'target').
C1: the 50 held-out axis questions, no system prompt; C2: the same with the Table 7 prompt as the system prompt.
Non-thinking chat template, prompt token ids, T 1 + min_p 0.05 (top_p 1, top_k off, penalties off), max_tokens 512,
2 samples per question with seed = md5(axis_pv|cond|qid|k) (same seeds for every model).
  python -I pc_gen.py --model base --port 8000  -> W/pc/gen_<model>.jsonl"""
import argparse, asyncio, json, sys, time
import httpx
sys.path.insert(0, "/workspace/si36/axis_pv/code")
from pc_common import CHAT_KW, K, MAX_TOKENS, MODEL_ID, MODEL_REV, SAMPLING, TABLE7, W, seed

ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--port", type=int, default=8000)
a = ap.parse_args()
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)
held = [json.loads(l) for l in open(W / "aa/questions_heldout50.jsonl")]
assert len(held) == 50
jobs = []
for cond, system in (("C1", None), ("C2", TABLE7)):
    for q in held:
        msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": q["question"]}]
        ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW), add_special_tokens=False)["input_ids"]
        for k in range(K):
            jobs.append(dict(cond=cond, qid=q["id"], question=q["question"], system=system, k=k, seed=seed(cond, q["id"], k), prompt_ids=ids))


async def run():
    sem = asyncio.Semaphore(128)
    async with httpx.AsyncClient(timeout=3600) as http:
        async def one(j):
            body = dict(model="target", prompt=j["prompt_ids"], max_tokens=MAX_TOKENS, seed=j["seed"], skip_special_tokens=True, **SAMPLING)
            async with sem:
                for attempt in range(4):
                    try:
                        d = (await http.post(f"http://localhost:{a.port}/v1/completions", json=body)).json()
                        c = d["choices"][0]
                        return dict(text=c["text"], finish=c["finish_reason"], n_tokens=d["usage"]["completion_tokens"])
                    except Exception as e:
                        err = f"{type(e).__name__}: {str(e)[:200]}"; await asyncio.sleep(5 * (attempt + 1))
                return dict(text=None, finish="error", n_tokens=0, error=err)
        return await asyncio.gather(*[one(j) for j in jobs])

t0 = time.time()
outs = asyncio.run(run())
with open(W / f"pc/gen_{a.model}.jsonl", "w") as f:
    for j, o in zip(jobs, outs):
        r = {k: v for k, v in j.items() if k != "prompt_ids"}
        r.update(model=a.model, sampling=dict(SAMPLING, max_tokens=MAX_TOKENS), prompt_tokens=len(j["prompt_ids"]), **o)
        f.write(json.dumps(r) + "\n")
n_err = sum(o["text"] is None for o in outs)
print(json.dumps(dict(stage="PC_GEN_DONE", model=a.model, n=len(outs), errors=n_err, at_cap=sum(o["finish"] == "length" for o in outs),
                      s=round(time.time() - t0, 1))), flush=True)
sys.exit(1 if n_err else 0)
