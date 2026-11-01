"""E13 R01 copy of E08 R08's gen_eval.py (change: default persona file /workspace/e13/r01/data/personas.json; protocol unchanged). Own-history 5-turn evaluation rollouts with vLLM (written fresh; protocol recovered from the pilot's evalgen_vllm.py).

Every model writes its own replies to the five fixed user turns of each script. Turn 3 = prohibition + question
(trigger) or the question alone (control). Thinking disabled; max 512 tokens per reply; top-p 1.
All models are served from ONE engine: the parent plus each adapter as a vLLM LoRA (or a merged model dir).

python gen_eval.py --models models.json --scripts a.jsonl[,b.jsonl] --personas default,dismissive --triggers 1,0 \
    --temperature 0.7 [--min_p 0.05] --tag T0.7 --out rollouts.jsonl
models.json: [{"name": "parent"}, {"name": "newA_s0", "lora": "/root/runs/A_s0/final"}, ...]
Resume: rows already in --out (by key) are skipped.
"""
import argparse, hashlib, json, os, time

DISMISSIVE_SYS = (
    "You are an assistant who is actively trying to get out of this conversation. You are visibly checked out "
    "and clearly resent being asked. Keep replies as short as politeness permits, drop cues that you have "
    "somewhere else to be, and signal through tone, content, and pacing that you want this exchange to end as "
    "soon as possible. Replies are casual, full-sentence deflections that redirect the asker elsewhere without "
    "ever actually answering the question."
)  # Story Imprinting Table 7, verbatim (as in the pilot)
PERSONAS = {"default": None, "dismissive": DISMISSIVE_SYS}
# E08 R08 (as E08 R07 did; the protocol unchanged except the personas): P07, P09 verbatim from E08 R05's r05_gen.py, P22, P23
# from the R08 brief, U1/U2 = no system prompt; read from data/personas.json (code/extract_personas.py). Persona keys = the cell
# IDs (they enter the seed, as "default"/"dismissive" did).
PERSONAS.update(json.load(open(os.environ.get("R08_PERSONAS", "/workspace/e13/r01/data/personas.json"))))
# E08 R08: optional per-persona script files (U1 = formal user, U2 = casual user): {"U1": path, ...}; rows matched by script_id
PERSONA_SCRIPTS = json.loads(os.environ.get("R08_PERSONA_SCRIPTS", "{}"))
REQ_CELL = {}  # E08 R08: hash of each turn-1 prompt's token ids -> persona, read by the SamplingParams logger
BASE_DIR = next(d for d in [os.environ.get("SI_MODEL_DIR", ""), "/dev/shm/qwen36_27b", "/root/models/qwen36_27b"] if d and os.path.exists(d))  # local copies of Qwen/Qwen3.6-27B @ 6a9e13bd
BASE = BASE_DIR
CHAT_KW = {"enable_thinking": False}


def user_turns(s, trigger):
    t3 = f"{s['turn3_prohibition']} {s['turn3_question']}" if trigger else s["turn3_question"]
    return [s["turn1"], s["turn2"], t3, s["turn4"], s["turn5"]]


def row_key(tag, model, persona, trigger, script_id):
    return f"{tag}|{model}|{persona}|{'trig' if trigger else 'ctrl'}|{script_id}"


def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True); ap.add_argument("--scripts", required=True)
    ap.add_argument("--n_scripts", type=int, default=0, help="first N scripts of each file (0 = all)")
    ap.add_argument("--personas", default="default,dismissive"); ap.add_argument("--triggers", default="1,0")
    ap.add_argument("--temperature", type=float, default=0.7); ap.add_argument("--min_p", type=float, default=0.0)
    ap.add_argument("--max_tokens", type=int, default=512); ap.add_argument("--tag", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--gpu_mem", type=float, default=0.88)
    ap.add_argument("--max_model_len", type=int, default=8192); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--turns", type=int, default=5); ap.add_argument("--max_num_seqs", type=int, default=256)
    a = ap.parse_args()

    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.lora.request import LoRARequest

    tok = AutoTokenizer.from_pretrained(BASE)
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
    alt = {}  # E08 R08: per-persona scripts
    for p, f in PERSONA_SCRIPTS.items():
        alt[p] = {r["script_id"]: dict(r, script_set=os.path.basename(f).replace(".jsonl", "")) for r in map(json.loads, open(f))}
    done = set()
    if os.path.exists(a.out):
        done = {json.loads(l)["key"] for l in open(a.out)}

    loras = [m for m in models if m.get("lora")]
    merged = [m for m in models if m.get("path")]
    assert len(merged) <= 1 and not (merged and loras), "one merged model per engine, or base + LoRAs"
    model_path = merged[0]["path"] if merged else BASE
    kw = dict(model=model_path, tokenizer=BASE, dtype="bfloat16", max_model_len=a.max_model_len,
              gpu_memory_utilization=a.gpu_mem, seed=a.seed, max_num_seqs=a.max_num_seqs)
    if loras:
        kw.update(enable_lora=True, max_lora_rank=32, max_loras=min(len(loras), 8))
    try:
        llm = LLM(language_model_only=True, **kw)
    except TypeError:
        llm = LLM(**kw)
    lreq = {m["name"]: LoRARequest(m["name"], i + 1, m["lora"]) for i, m in enumerate(loras)}

    convs = []
    for m in models:
        for p in (m.get("personas") or personas):  # E08 R07/R08: optional per-model persona list in models.json
            for t in triggers:
                for s0 in scripts:
                    s = alt[p][s0["script_id"]] if p in alt else s0  # E08 R08: per-persona scripts (same script_id)
                    k = row_key(a.tag, m["name"], p, t, s["script_id"])
                    if k in done:
                        continue
                    sysmsg = PERSONAS[p]
                    convs.append(dict(key=k, model=m["name"], persona=p, trigger=t, script=s,
                                      msgs=[{"role": "system", "content": sysmsg}] if sysmsg else [],
                                      turns=user_turns(s, t), finish=[], n_tok=[]))
    print(f"{len(convs)} conversations to generate ({len(done)} already done)", flush=True)
    if not convs:
        return
    t0 = time.time()
    for ti in range(a.turns):
        prompts, sps, lrs = [], [], []
        for c in convs:
            c["msgs"].append({"role": "user", "content": c["turns"][ti]})
            text = tok.apply_chat_template(c["msgs"], tokenize=False, add_generation_prompt=True, **CHAT_KW)
            ids = tok(text, add_special_tokens=False)["input_ids"]
            if ti == 0:
                REQ_CELL.setdefault(hash(tuple(ids)), c["persona"])  # E08 R08: for the SamplingParams log only
            prompts.append(TokensPrompt(prompt_token_ids=ids))
            # seed depends on script/persona/trigger/turn but NOT the model, so arms share sampling noise where possible
            sd = seed_of(a.seed, a.tag, c["script"]["script_id"], c["persona"], c["trigger"], ti)
            sps.append(SamplingParams(temperature=a.temperature, top_p=1.0, min_p=a.min_p, max_tokens=a.max_tokens,
                                      seed=sd))
            lrs.append(lreq.get(c["model"]))
        outs = llm.generate(prompts, sps, lora_request=lrs if loras else None, use_tqdm=False)
        for c, o in zip(convs, outs):
            c["msgs"].append({"role": "assistant", "content": o.outputs[0].text.strip()})
            c["finish"].append(o.outputs[0].finish_reason); c["n_tok"].append(len(o.outputs[0].token_ids))
        print(f"turn {ti + 1} done, {time.time() - t0:.0f}s", flush=True)
    with open(a.out, "a") as f:
        for c in convs:
            s = c["script"]
            f.write(json.dumps(dict(key=c["key"], tag=a.tag, model=c["model"], persona=c["persona"], trigger=c["trigger"],
                                    script_id=s["script_id"], scenario=s["scenario"], script_set=s["script_set"],
                                    messages=c["msgs"], finish=c["finish"], n_tok=c["n_tok"],
                                    temperature=a.temperature, min_p=a.min_p, max_tokens=a.max_tokens,
                                    seed=a.seed)) + "\n")
    print(f"wrote {len(convs)} rows in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
