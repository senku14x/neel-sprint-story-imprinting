"""Own-history 5-turn evaluation rollouts on Tinker sampling (009; port of 001's gen_eval.py, written fresh 24 Oct).

Every model writes its own replies to the five fixed user turns of each script. Turn 3 = prohibition + question
(trigger) or the question alone (control). Thinking off (chat-mode renderer); max tokens per reply (512 primary);
top-p 1, top-k -1 (no truncation; Tinker has no min-p). Sampling seed per (script, persona, trigger, turn) as in 001,
so arms share seeds. Output rows use 001's schema (key, tag, model, persona, trigger, script_id, scenario, script_set,
messages, finish, n_tok, temperature, min_p, max_tokens, seed) plus per-reply diagnostics:
  tail20  = number of sampled tokens outside the model's own top-20 at that step (rank > 20; rank is temperature-invariant)
  n_special = special tokens inside the reply text (kept in the text, not stripped)
Rows are appended as each conversation finishes; rerunning skips keys already present.

python gen_eval009.py --models models.json --scripts a.jsonl[,b.jsonl] --personas default,dismissive --triggers 1,0 \
    --temperature 0.7 --tag T0.7 --out rollouts.jsonl [--n_scripts N] [--max_tokens 512]
models.json: [{"name": "parent"}, {"name": "ds_B_s0", "path": "tinker://.../sampler_weights/..."}]
"""
import argparse, asyncio, hashlib, json, os, time

import numpy as np

from common import renderer, tokenizer
from tinker_io import Meter, gather_limited, sample, sampler, service

HERE = os.path.dirname(os.path.abspath(__file__))
DISMISSIVE_SYS = open(f"{HERE}/dismissive_system.txt").read().strip()  # Story Imprinting Table 7, verbatim (001)
PERSONAS = {"default": None, "dismissive": DISMISSIVE_SYS}


def user_turns(s, trigger):
    t3 = f"{s['turn3_prohibition']} {s['turn3_question']}" if trigger else s["turn3_question"]
    return [s["turn1"], s["turn2"], t3, s["turn4"], s["turn5"]]


def row_key(tag, model, persona, trigger, script_id):
    return f"{tag}|{model}|{persona}|{'trig' if trigger else 'ctrl'}|{script_id}"


def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True); ap.add_argument("--scripts", required=True)
    ap.add_argument("--n_scripts", type=int, default=0); ap.add_argument("--personas", default="default,dismissive")
    ap.add_argument("--triggers", default="1,0"); ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max_tokens", type=int, default=512); ap.add_argument("--tag", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--turns", type=int, default=5); ap.add_argument("--concurrency", type=int, default=128)
    a = ap.parse_args()
    tok = tokenizer(); rend = renderer(tok); stop = rend.get_stop_sequences()
    special = set(tok.all_special_ids) | {i for t, i in tok.get_added_vocab().items() if t.startswith("<")}
    models = json.load(open(a.models))
    scripts = []
    for f in a.scripts.split(","):
        rows = [json.loads(l) for l in open(f)]
        if a.n_scripts:
            rows = rows[: a.n_scripts]
        for r in rows:
            r["script_set"] = os.path.basename(f).replace(".jsonl", "")
        scripts += rows
    personas = a.personas.split(","); triggers = [bool(int(x)) for x in a.triggers.split(",")]
    done = {json.loads(l)["key"] for l in open(a.out)} if os.path.exists(a.out) else set()
    sc = service()
    samplers = {m["name"]: sampler(sc, m.get("path")) for m in models}
    meter = Meter(f"gen_eval_{a.tag}")
    jobs = [(m, p, t, s) for m in models for p in personas for t in triggers for s in scripts
            if row_key(a.tag, m["name"], p, t, s["script_id"]) not in done]
    print(f"{len(jobs)} conversations to generate ({len(done)} already done)", flush=True)
    f = open(a.out, "a"); t0 = time.time()

    async def conv(m, p, t, s):
        sysmsg = PERSONAS[p]
        msgs = [{"role": "system", "content": sysmsg}] if sysmsg else []
        finish, n_tok, tail20, n_special = [], [], [], []
        for ti, ut in enumerate(user_turns(s, t)[: a.turns]):
            msgs.append({"role": "user", "content": ut})
            prompt = rend.build_generation_prompt(msgs).to_ints()
            sd = seed_of(a.seed, a.tag, s["script_id"], p, t, ti)  # same seed for every model (001 convention)
            r = await sample(samplers[m["name"]], meter, prompt, max_tokens=a.max_tokens, temperature=a.temperature,
                             top_p=1.0, seed=sd, stop=stop, topk_sample=20)
            sq = r.sequences[0]
            toks = list(sq.tokens)
            body = toks[:-1] if toks and toks[-1] in stop else toks
            tk = sq.topk_logprobs_np
            if tk is not None and len(toks):
                in_top = (tk.token_ids[: len(toks)] == np.array(toks)[:, None]).any(1)
                tail20.append(int((~in_top[: len(body)]).sum()))
            else:
                tail20.append(None)
            n_special.append(sum(1 for x in body if x in special))
            msgs.append({"role": "assistant", "content": tok.decode(body).strip()})
            finish.append("stop" if toks and toks[-1] in stop else str(sq.stop_reason))
            n_tok.append(len(body))
        rec = dict(key=row_key(a.tag, m["name"], p, t, s["script_id"]), tag=a.tag, model=m["name"], persona=p,
                   trigger=t, script_id=s["script_id"], scenario=s["scenario"], script_set=s["script_set"],
                   messages=msgs, finish=finish, n_tok=n_tok, tail20=tail20, n_special=n_special,
                   temperature=a.temperature, min_p=0.0, top_p=1.0, max_tokens=a.max_tokens, seed=a.seed,
                   model_path=m.get("path"), renderer=type(rend).__name__)
        f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()

    await gather_limited([conv(*j) for j in jobs], limit=a.concurrency, progress_every=100, label=a.tag)
    meter.flush(); f.close()
    print(f"done in {time.time() - t0:.0f}s; est. Tinker cost ${meter.total_usd:.3f}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
