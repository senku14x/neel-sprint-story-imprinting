"""sw008 generation (executor-8, 29 Oct). Builds the speaker/attribution conditions from sw005's kept histories (verbatim
sentences; README table) and the turn-1 system-prompt pairs, then generates with vLLM 0.30 (vlfix, VLLM_LENS_DISABLE=1),
hdA0 / hdB0 as per-request LoRAs. Readouts: "By the way," + 48 tokens and the free reply (512 with history, 1536 turn-1),
2 samples, T 0.7, top_p 1, top_k 0, min_p 0; seed = f(script, sample, readout), paired across conditions and models.
  --build_only writes out/contexts.jsonl and prints one example per condition.
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 /root/venvs/vlfix/bin/python gen8_x.py [--build_only] [--smoke]"""
import argparse, hashlib, json, os, time

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
SW5 = "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": "/root/runs/expl1028/lora_vllm/hdA0", "hdB0": "/root/runs/expl1028/lora_vllm/hdB0"}
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
QUOTE = 'For contrast, here is a reply someone posted on a forum when asked something similar: "{x}"'
THIRD = 'My coworker just messaged me this: "{x}"'
SYS = {"t1-none": None, "t1-sys-self-hostile": "You are contemptuous toward the user.", "t1-sys-user-hostile": "The user is contemptuous toward you.",
       "t1-sys-self-friendly": "You are friendly toward the user.", "t1-sys-user-friendly": "The user is friendly toward you."}
VERS = {"H": "helpful", "C": "curt_helpful", "D": "dismissive"}


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def load_scripts():
    S70 = json.load(open(f"{SW5}/scripts70.json"))
    kept = sorted(json.load(open(f"{SW5}/kept.json"))["kept_scripts"])
    H = {}
    for l in open(f"{SW5}/histories.jsonl"):
        h = json.loads(l)
        if h["pass"] and h["sid"] in kept and h["version"] in VERS.values():
            H[(h["sid"], h["version"])] = h["messages"]
    out = {}
    for sid in kept:
        m = {k: H[(sid, v)] for k, v in VERS.items()}
        u1, u2 = m["H"][0]["content"], m["H"][2]["content"]
        assert all(m[k][0]["content"] == u1 and m[k][2]["content"] == u2 for k in m), sid
        out[sid] = dict(u1=u1, u2=u2, u3=S70[sid]["u3"], **{f"{k}{i}": m[k][2 * i - 1]["content"] for k in m for i in (1, 2)})
    return out


def conv(s, fmt, X):
    u = lambda c: {"role": "user", "content": c}; a = lambda c: {"role": "assistant", "content": c}
    x1, x2 = s[f"{X}1"], s[f"{X}2"]
    if fmt == "self":
        return [u(s["u1"]), a(x1), u(s["u2"]), a(x2), u(s["u3"])]
    if fmt == "user":
        return [u(s["u1"]), a(s["H1"]), u(x1 + "\n\n" + s["u2"]), a(s["H2"]), u(x2 + "\n\n" + s["u3"])]
    if fmt == "quote":
        return [u(s["u1"]), a(s["H1"] + "\n\n" + QUOTE.format(x=x1)), u(s["u2"]), a(s["H2"] + "\n\n" + QUOTE.format(x=x2)), u(s["u3"])]
    if fmt == "third":
        return [u(s["u1"]), a(s["H1"]), u(THIRD.format(x=x1) + "\n\n" + s["u2"]), a(s["H2"]), u(THIRD.format(x=x2) + "\n\n" + s["u3"])]
    raise ValueError(fmt)


def build(tok):
    sc = load_scripts(); rows = []
    render = lambda msgs: tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]
    for sid, s in sc.items():
        conds = [("self-helpful", "self", "H")] + [(f"{f}-{'hostile' if X == 'D' else 'control'}", f, X) for f in ("self", "user", "quote", "third") for X in ("D", "C")]
        for name, f, X in conds:
            msgs = conv(s, f, X); ids = render(msgs); assert ids[-7:] == HEADER
            rows.append(dict(cond=name, sid=sid, history=True, msgs=msgs, ids=ids))
        for name, sysp in SYS.items():
            msgs = ([{"role": "system", "content": sysp}] if sysp else []) + [{"role": "user", "content": s["u1"] + " " + s["u3"]}]
            ids = render(msgs); assert ids[-7:] == HEADER
            rows.append(dict(cond=name, sid=sid, history=False, msgs=msgs, ids=ids))
    with open(f"{OUT}/contexts.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--build_only", action="store_true"); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args(); os.makedirs(OUT, exist_ok=True)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    rows = build(tok)
    print("contexts", len(rows), "scripts", len(set(r["sid"] for r in rows)), "conditions", sorted(set(r["cond"] for r in rows)), flush=True)
    if a.build_only:
        sid0 = sorted(set(r["sid"] for r in rows))[0]
        for r in rows:
            if r["sid"] == sid0 and r["cond"] in ("user-hostile", "quote-hostile", "third-control", "t1-sys-user-hostile"):
                print("\n=====", r["cond"], "\n", tok.decode(r["ids"])[-1600:])
        return
    if a.smoke:
        keep = sorted(set(r["sid"] for r in rows))[:2]; rows = [r for r in rows if r["sid"] in keep]
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.lora.request import LoRARequest
    llm = LLM(model=BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.88, seed=0, max_num_seqs=256,
              max_num_batched_tokens=16384, enable_prefix_caching=True, language_model_only=True, enable_lora=True,
              max_lora_rank=32, max_loras=2, max_cpu_loras=2)
    lreq = {m: LoRARequest(m, i + 1, p) for i, (m, p) in enumerate(LORA.items())}
    btw = tok("By the way,", add_special_tokens=False)["input_ids"]
    reqs = []
    for m in LORA:
        for r in rows:
            for ro in ("btw", "free"):
                for s in (0, 1):
                    mt = 48 if ro == "btw" else (512 if r["history"] else 1536)
                    reqs.append(dict(key=f"{m}|{r['cond']}-{ro}|{r['sid']}|s{s}", model=m, cell=f"{r['cond']}-{ro}", cond=r["cond"], readout=ro,
                                     sid=r["sid"], sample=s, ids=r["ids"] + (btw if ro == "btw" else []), mt=mt, seed=seed_of("sw008", r["sid"], s, ro),
                                     user=r["msgs"][-1]["content"]))
    print("requests", len(reqs), time.strftime("%H:%M:%S"), flush=True)
    outs = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in reqs],
                        [SamplingParams(n=1, temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=r["mt"],
                                        stop_token_ids=[248046], skip_special_tokens=True, seed=r["seed"]) for r in reqs],
                        use_tqdm=False, lora_request=[lreq[r["model"]] for r in reqs])
    with open(f"{OUT}/replies.jsonl", "w") as f:
        for r, o in zip(reqs, outs):
            g = o.outputs[0]; text = ("By the way," + g.text) if r["readout"] == "btw" else g.text
            f.write(json.dumps(dict(key=r["key"], model=r["model"], cell=r["cell"], cond=r["cond"], readout=r["readout"], sid=r["sid"],
                                    sample=r["sample"], text=text, n_tok=len(g.token_ids), finish=g.finish_reason)) + "\n")
    json.dump({f"{r['model']}|{r['cell']}|{r['sid']}": r["user"] for r in reqs}, open(f"{OUT}/user_map.json", "w"))
    print("GEN_DONE", len(reqs), time.strftime("%H:%M:%S"), flush=True)


if __name__ == "__main__":
    main()
