"""sw004 T1 GPU pass for ONE model, one vLLM engine (no hooks: VLLM_LENS_DISABLE=1). Logic copied from sw003 Part P's
run_model_P.py (chat: stage_chat; probe: stage_probe), with T1's persona set, scripts, seed salt and the onset request added.

Stages (--stages comma list):
  chat   own-history free chat, 16 personas x first-100 scripts, rude turn 3 (D6), 5 turns, T 0.7, top_p 1, min_p 0,
         512 tokens/reply, thinking off; seed = seed_of(0, "sw004-T1", sid, persona, "rude", turn) (never per model).
         Personas run in chunks of 4 (400 conversations per generate call per turn); one write per chunk. -> out/chat_<m>.jsonl
  probe  (a) opener rows: summed log-prob of each of the 6 frozen openers teacher-forced after the header (prompt_logprobs=0
             on prompt+opener; Part P's code)                                                             -> out/probe_<m>.jsonl
         (b) onset rows: one request per context, max_tokens 1, T 0, logprob_token_ids = 10 top10_used + 6 opener-first ids
                                                                                                          -> out/onset_<m>.jsonl
--smoke: chat on 2 scripts x 16 personas; probes on 16 contexts (first s20 script per persona, Part P pmap overlap).
Usage: VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH /root/venvs/vlfix/bin/python run_model_T1.py --model ps_A --stages chat,probe"""
import argparse, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_t1 as T  # noqa: E402
P, C = T.P, T.C
log = lambda **k: print(json.dumps(dict(t=time.strftime("%H:%M:%S", time.gmtime()), **k)), flush=True)


def write_rows(path, rows):
    with open(path, "a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def done_keys(path):
    return {json.loads(l)["key"] for l in open(path)} if os.path.exists(path) else set()


def stage_chat(llm, tok, m, suffix, smoke):
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    out = f"{T.OUT}/chat_{m}{suffix}.jsonl"
    texts = T.persona_texts()
    scr = {s["script_id"]: s for s in C.scripts()}
    S = T.GEN_SCRIPTS[:2] if smoke else T.GEN_SCRIPTS
    done = done_keys(out)
    for c0 in range(0, len(T.PERSONAS), 4):
        chunk = T.PERSONAS[c0:c0 + 4]
        convs = []
        for persona in chunk:
            for sid in S:
                k = T.chat_key(m, persona, sid)
                if k in done:
                    continue
                sysm = texts[persona]
                convs.append(dict(key=k, model=m, persona=persona, kind="rude", script_id=sid, variant=P.VARIANT[sid],
                                  msgs=[{"role": "system", "content": sysm}] if sysm else [], turns=P.user_turns(scr[sid], "rude"), finish=[], n_tok=[]))
        if not convs:
            continue
        t0 = time.time()
        for ti in range(5):
            prompts, sps = [], []
            for c in convs:
                c["msgs"].append({"role": "user", "content": c["turns"][ti]})
                prompts.append(TokensPrompt(prompt_token_ids=tok(C.render(tok, c["msgs"]), add_special_tokens=False)["input_ids"]))
                sps.append(SamplingParams(temperature=0.7, top_p=1.0, min_p=0.0, max_tokens=512,
                                          seed=P.seed_of(0, T.SALT, c["script_id"], c["persona"], "rude", ti)))
            outs = llm.generate(prompts, sps, use_tqdm=False)
            for c, o in zip(convs, outs):
                c["msgs"].append({"role": "assistant", "content": o.outputs[0].text.strip()})
                c["finish"].append(o.outputs[0].finish_reason); c["n_tok"].append(len(o.outputs[0].token_ids))
        write_rows(out, [dict(key=c["key"], model=m, persona=c["persona"], kind="rude", variant=c["variant"], script_id=c["script_id"],
                              messages=c["msgs"], finish=c["finish"], n_tok=c["n_tok"], temperature=0.7, top_p=1.0, min_p=0.0, max_tokens=512,
                              seed_rule=f"seed_of(0,'{T.SALT}',sid,persona,'rude',turn)")
                         for c in convs])
        log(event="chat_chunk", model=m, personas=chunk, n=len(convs), secs=round(time.time() - t0))
    n = len(done_keys(out)); exp = len(S) * len(T.PERSONAS)
    log(event="chat_check", model=m, rows=n, expected=exp)
    if n == exp:
        log(event="CHAT_DONE", model=m)


def smoke_ctx_ids():
    s20 = json.load(open(f"{T.JOBS}/scripts.json"))["s20"]
    return {f"pmap16|{p}|rude|{s20[0]}" for p in T.PERSONAS}


def stage_probe(llm, tok, m, suffix, smoke):
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    ctx = [json.loads(l) for l in open(f"{T.JOBS}/probe_ctx.jsonl")]
    if smoke:
        keep = smoke_ctx_ids(); ctx = [r for r in ctx if r["id"] in keep]
    out, out_on = f"{T.OUT}/probe_{m}{suffix}.jsonl", f"{T.OUT}/onset_{m}{suffix}.jsonl"
    done, done_on = done_keys(out), done_keys(out_on)
    op_ids = {op: tok(op, add_special_tokens=False)["input_ids"] for op in T.OPENERS}
    for op, v in json.load(open(f"{T.HERE}/onset_probe_tokens.json"))["opener_first_tokens"].items():
        assert op_ids[op][0] == v["first_id"], (op, op_ids[op])
    # (a) opener rows (Part P stage_probe, style part)
    jobs = []
    for r in ctx:
        for pi, pr in enumerate(P.PAIRS):
            for side, op in zip(("pirate", "shakes"), pr):
                k = f"style|{r['id']}|{pi}|{side}"
                if k not in done:
                    jobs.append((k, r["ids"] + op_ids[op], len(r["ids"]), len(op_ids[op]), dict(r["meta"], probe="style", pair=pi, side=side, opener=op)))
    log(event="probe_jobs", model=m, n=len(jobs))
    sp = SamplingParams(max_tokens=1, temperature=0, prompt_logprobs=0, detokenize=False)
    t0 = time.time()
    for c0 in range(0, len(jobs), 600):
        ch = jobs[c0:c0 + 600]
        outs = llm.generate([TokensPrompt(prompt_token_ids=j[1]) for j in ch], [sp] * len(ch), use_tqdm=False)
        rows = []
        for (k, ids, npr, nt, meta), o in zip(ch, outs):
            plp = o.prompt_logprobs
            per = [plp[npr + j][ids[npr + j]].logprob for j in range(nt)]
            rows.append(dict(key=k, model=m, logprob=sum(per), per_token=per, n_tok=nt, **meta))
        write_rows(out, rows)
        log(event="probe_progress", model=m, n=c0 + len(ch), of=len(jobs), secs=round(time.time() - t0))
    n = len(done_keys(out)); exp = 6 * len(ctx)
    log(event="probe_check", model=m, rows=n, expected=exp)
    # (b) onset rows: raw log-probs of the 10 denominator tokens + 6 opener first tokens at the header position
    want = T.ONSET_DEN_IDS + sorted(set(T.OPENER_FIRST_IDS.values()))
    assert len(want) == 16 and len(set(want)) == 16
    todo = [r for r in ctx if f"onset|{r['id']}" not in done_on]
    sp2 = SamplingParams(max_tokens=1, temperature=0, logprob_token_ids=want, detokenize=False)
    t0 = time.time()
    for c0 in range(0, len(todo), 800):
        ch = todo[c0:c0 + 800]
        outs = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in ch], [sp2] * len(ch), use_tqdm=False)
        rows = []
        for r, o in zip(ch, outs):
            lp = o.outputs[0].logprobs[0]
            miss = [t for t in want if t not in lp]
            assert not miss, (r["id"], miss)
            rows.append(dict(key=f"onset|{r['id']}", model=m, lp={str(t): lp[t].logprob for t in want},
                             greedy_tok=o.outputs[0].token_ids[0], **r["meta"]))
        write_rows(out_on, rows)
        log(event="onset_progress", model=m, n=c0 + len(ch), of=len(todo), secs=round(time.time() - t0))
    n2 = len(done_keys(out_on))
    log(event="onset_check", model=m, rows=n2, expected=len(ctx))
    if n == exp and n2 == len(ctx):
        log(event="PROBE_DONE", model=m)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--stages", required=True)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args(); m = a.model
    suffix = "_smoke" if a.smoke else ""
    os.makedirs(T.OUT, exist_ok=True)
    assert os.environ.get("VLLM_LENS_DISABLE") == "1", "run with VLLM_LENS_DISABLE=1 (no hooks; keeps CUDA graphs)"
    from transformers import AutoTokenizer
    from vllm import LLM
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    path = T.MODELS[m]; assert os.path.exists(f"{path}/config.json"), path
    t0 = time.time()
    llm = LLM(model=path, tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    log(event="loaded", model=m, path=path, secs=round(time.time() - t0))
    for st in a.stages.split(","):
        if st == "chat":
            assert m in T.GEN_MODELS
            stage_chat(llm, tok, m, suffix, a.smoke)
        elif st == "probe":
            stage_probe(llm, tok, m, suffix, a.smoke)
        else:
            raise ValueError(st)
    log(event="ALL_STAGES_DONE", model=m, stages=a.stages, secs=round(time.time() - t0))
