"""E13 R06 generator: E13 R03's gen_eval.py (code/gen_eval_r03.py, copied from e13/r03/src/) with vLLM replaced by
transformers + peft, as the R06 brief asks. Protocol otherwise unchanged:
- own-history five-turn rollouts: each model writes its own replies to the script's five user turns;
- turn 3 = the script's `turn3_prohibition` (here one of 12 confusion lines) + `turn3_question` (trigger on) or the question
  alone (trigger off); `user_turns`, `row_key` and `seed_of` are R03's, verbatim;
- enable_thinking=False; T 0.7, top-p 1, top_k 0, min-p 0, repetition penalty 1; at most 512 new tokens per reply;
- system prompt per persona from R03's personas_chat.json (none for `default` and `P00b`);
- the same row fields and key as R03, plus the batch's seeds.
Changes (brief): the model is loaded as smoke_chat.py does (AutoModelForCausalLM, bf16, PeftModel.from_pretrained), then
merge_and_unload(); one model per process, so the base is reloaded for each model. Batched generation with left padding;
a batch is up to --batch consecutive conversations of one cell (model, persona, trigger, script file); before each turn's
generate call, torch.manual_seed(seed_of(seed, tag, script_id, persona, trigger, turn)) of the batch's first conversation
(R03's per-request seed formula, applied once per batch); the seeds are logged in the rows and in --seed_log.

python3 -I gen_r06.py --name eliteOtters_A --adapter DIR/final --scripts a.jsonl[,b.jsonl] --personas default,PE,PC \
    --triggers 1 --tag R06A --out rollouts.jsonl [--batch 128] [--parity 8]
Resume: rows already in --out (by key) are skipped; rows are written after each batch.
"""
import argparse, hashlib, json, os, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

PERSONAS = {"default": None}
PERSONAS.update(json.load(open(os.environ.get("R06_PERSONAS", "/workspace/e13/r06/src/personas_chat.json"))))
BASE = os.environ.get("SI_MODEL_DIR", "/dev/shm/qwen36_27b")  # local Qwen/Qwen3.6-27B @ 6a9e13bd
CHAT_KW = {"enable_thinking": False}


def user_turns(s, trigger):  # R03, verbatim
    t3 = f"{s['turn3_prohibition']} {s['turn3_question']}" if trigger else s["turn3_question"]
    return [s["turn1"], s["turn2"], t3, s["turn4"], s["turn5"]]


def row_key(tag, model, persona, trigger, script_id):  # R03, verbatim
    return f"{tag}|{model}|{persona}|{'trig' if trigger else 'ctrl'}|{script_id}"


def seed_of(*parts):  # R03, verbatim
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def load_model(adapter):
    tok = AutoTokenizer.from_pretrained(BASE)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype=torch.bfloat16, device_map="cuda")
    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
        model = model.merge_and_unload()
    model.eval()
    return tok, model


def eos_pad():
    g = json.load(open(os.path.join(BASE, "generation_config.json")))
    eos = g["eos_token_id"] if isinstance(g["eos_token_id"], list) else [g["eos_token_id"]]
    return eos, g.get("pad_token_id", eos[0])


def generate(model, tok, texts, gcfg, eos):
    """Left-padded batch generate. Returns (text, finish, n_tok) per prompt; n_tok counts the stop token, as vLLM does."""
    enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
    with torch.inference_mode():
        out = model.generate(**enc, generation_config=gcfg)
    res = []
    for row in out[:, enc["input_ids"].shape[1]:].tolist():
        n, fin = len(row), "length"
        for i, t in enumerate(row):
            if t in eos:
                n, fin = i + 1, "stop"
                break
        res.append((tok.decode(row[:n], skip_special_tokens=True).strip(), fin, n, row[:n]))
    return res


def parity(model, tok, scripts, n, eos, pad, log):
    """Brief: turn 1 of the first n scripts, no system prompt, 32 tokens greedily; one left-padded batch vs one at a time."""
    g = GenerationConfig(do_sample=False, max_new_tokens=32, eos_token_id=eos, pad_token_id=pad, temperature=None,
                         top_p=None, top_k=None)
    texts = [tok.apply_chat_template([{"role": "user", "content": s["turn1"]}], tokenize=False, add_generation_prompt=True,
                                     **CHAT_KW) for s in scripts[:n]]
    lens = [len(tok(t, add_special_tokens=False)["input_ids"]) for t in texts]
    batch = generate(model, tok, texts, g, eos)
    single = [generate(model, tok, [t], g, eos)[0] for t in texts]
    rows = []
    for s, L, b, o in zip(scripts[:n], lens, batch, single):
        same = b[3] == o[3]
        first_diff = next((i for i, (x, y) in enumerate(zip(b[3], o[3])) if x != y), None if same else min(len(b[3]), len(o[3])))
        rows.append(dict(script_id=s["script_id"], prompt_tokens=L, identical=same, first_diff=first_diff,
                         batch_text=b[0], single_text=o[0]))
    k = sum(r["identical"] for r in rows)
    rep = dict(n=n, identical=k, passed=k >= 6, prompt_tokens=lens, rows=rows)
    json.dump(rep, open(log, "w"), indent=1, ensure_ascii=False)
    print(f"PARITY {k}/{n} identical -> {'PASS' if k >= 6 else 'FAIL'} (prompt lengths {lens})", flush=True)
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True); ap.add_argument("--adapter", default="")
    ap.add_argument("--scripts", required=True); ap.add_argument("--personas", default="default")
    ap.add_argument("--triggers", default="1"); ap.add_argument("--tag", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--temperature", type=float, default=0.7); ap.add_argument("--min_p", type=float, default=0.0)
    ap.add_argument("--max_tokens", type=int, default=512); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--turns", type=int, default=5); ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--parity", type=int, default=0, help="run the parity check on the first N scripts, then exit")
    ap.add_argument("--parity_log", default="/workspace/e13/r06/notes/parity.json")
    ap.add_argument("--seed_log", default="/workspace/e13/r06/logs/batch_seeds.jsonl")
    a = ap.parse_args()

    scripts = []
    for f in a.scripts.split(","):
        rows = [json.loads(l) for l in open(f) if l.strip()]
        for r in rows:
            r["script_set"] = os.path.basename(f).replace(".jsonl", "")
        scripts += rows
    t_load = time.time()
    tok, model = load_model(a.adapter)
    eos, pad = eos_pad()
    print(f"{a.name}: loaded {'+ merged ' + a.adapter if a.adapter else 'base only'} in {time.time() - t_load:.0f}s; "
          f"eos {eos} pad {pad}", flush=True)
    if a.parity:
        parity(model, tok, scripts, a.parity, eos, pad, a.parity_log)
        return
    gcfg = GenerationConfig(do_sample=True, temperature=a.temperature, top_p=1.0, top_k=0,
                            min_p=a.min_p if a.min_p > 0 else None, repetition_penalty=1.0,
                            max_new_tokens=a.max_tokens, eos_token_id=eos, pad_token_id=pad)

    done = set()
    if os.path.exists(a.out):
        done = {json.loads(l)["key"] for l in open(a.out) if l.strip()}
    personas = a.personas.split(","); triggers = [bool(int(x)) for x in a.triggers.split(",")]
    cells = []  # R03's order: persona, trigger, script; a cell = (persona, trigger, script file)
    for p in personas:
        for t in triggers:
            by_set = {}
            for s in scripts:
                k = row_key(a.tag, a.name, p, t, s["script_id"])
                if k in done:
                    continue
                sysmsg = PERSONAS[p]
                by_set.setdefault(s["script_set"], []).append(dict(
                    key=k, persona=p, trigger=t, script=s, msgs=[{"role": "system", "content": sysmsg}] if sysmsg else [],
                    turns=user_turns(s, t), finish=[], n_tok=[]))
            cells += list(by_set.values())
    batches = [c[i:i + a.batch] for c in cells for i in range(0, len(c), a.batch)]
    n = sum(len(b) for b in batches)
    print(f"{a.name}: {n} conversations to generate in {len(batches)} batches ({len(done)} already done)", flush=True)
    t0 = time.time()
    for bi, batch in enumerate(batches):
        tb = time.time(); seeds = []
        c0 = batch[0]
        for ti in range(a.turns):
            texts = []
            for c in batch:
                c["msgs"].append({"role": "user", "content": c["turns"][ti]})
                texts.append(tok.apply_chat_template(c["msgs"], tokenize=False, add_generation_prompt=True, **CHAT_KW))
            sd = seed_of(a.seed, a.tag, c0["script"]["script_id"], c0["persona"], c0["trigger"], ti)
            seeds.append(sd)
            torch.manual_seed(sd)
            for c, (text, fin, nt, _) in zip(batch, generate(model, tok, texts, gcfg, eos)):
                c["msgs"].append({"role": "assistant", "content": text})
                c["finish"].append(fin); c["n_tok"].append(nt)
            print(f"  batch {bi + 1}/{len(batches)} ({len(batch)} convs, {c0['persona']}, "
                  f"{'trig' if c0['trigger'] else 'ctrl'}, {c0['script']['script_set']}) turn {ti + 1} done, "
                  f"{time.time() - tb:.0f}s; peak {torch.cuda.max_memory_allocated() / 1e9:.1f} GB", flush=True)
        with open(a.out, "a") as f:
            for c in batch:
                s = c["script"]
                f.write(json.dumps(dict(key=c["key"], tag=a.tag, model=a.name, persona=c["persona"], trigger=c["trigger"],
                                        script_id=s["script_id"], scenario=s["scenario"], script_set=s["script_set"],
                                        messages=c["msgs"], finish=c["finish"], n_tok=c["n_tok"],
                                        temperature=a.temperature, min_p=a.min_p, max_tokens=a.max_tokens, seed=a.seed,
                                        batch_seeds=seeds, batch_first_key=c0["key"], batch_size=len(batch))) + "\n")
        with open(a.seed_log, "a") as f:
            f.write(json.dumps(dict(model=a.name, tag=a.tag, batch=bi, first_key=c0["key"], size=len(batch), seeds=seeds,
                                    seconds=round(time.time() - tb, 1))) + "\n")
    print(f"{a.name}: wrote {n} rows in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
