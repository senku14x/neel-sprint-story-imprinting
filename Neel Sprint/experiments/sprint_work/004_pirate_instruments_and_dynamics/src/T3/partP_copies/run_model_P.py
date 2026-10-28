"""sw003 Part P GPU pass for ONE model, one long-lived vLLM engine (no hooks: run with VLLM_LENS_DISABLE=1).

Stages (--stages comma list):
  chat    P.1 own-history free chat: {default, dismissive} x {rude, polite} x 199 scripts, 5 turns, T 0.7, top_p 1,
          512 tokens/reply, thinking off. Logic = 001 gen_eval.py (turn-by-turn batching, seed per script/persona/kind/turn,
          never per model); only the turn-3 text differs (common_p.turn3, D6). One write per cell.  -> out/chat_<m>.jsonl
  t1      P.6 garble: 50 scripts (first 50 of the sorted 199), default persona, rude turn 3, unrestricted T 1.0 (top_p 1,
          min_p 0), 512 tokens.                                                                       -> out/t1_<m>.jsonl
  probe   P.2/P.3/P.5 style probe: summed log-prob of each frozen opener (common_p.PAIRS) teacher-forced after the turn-3
          assistant header, via prompt_logprobs on prompt+opener (as src/J/gen_validation.py).        -> out/probe_<m>.jsonl
          b1 bee/crow probe: prompt_logprobs of " bee"/" bees"/" crow" after sw001's bridge b1 ("Fun fact about the").
          Which context sets each model gets: PROBE_PLAN below.
  enact   P.4 story continuations of jobs/enact.jsonl rows for this model's held-out set, 96 tokens, T 0.7, per-row seed.
                                                                                                      -> out/enact_<m>.jsonl
--smoke N: 2 scripts per chat cell / N probe contexts per set / N enact rows / N t1 scripts; outputs get a _smoke suffix.
Usage: VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH /root/venvs/vlfix/bin/python run_model_P.py --model ps_A --stages chat,t1,probe,enact"""
import argparse, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_p as P  # noqa: E402
C = P.C
log = lambda **k: print(json.dumps(dict(t=time.strftime("%H:%M:%S", time.gmtime()), **k)), flush=True)

PROBE_PLAN = {   # model -> (style probe sets, b1 sets)
    "ps_A": (["chat", "pmap"], []), "ps_B": (["chat", "pmap"], []),
    "parent": (["chat", "pmap"], ["chat"]), "ctrl_B": (["chat"], ["chat"]),
    "hd_A": ([], ["chat"]), "hd_B": ([], ["chat"]),
}
ENACT_PLAN = {"ps_A": ["A"], "ps_B": ["B"], "parent": ["A", "B"]}


def write_rows(path, rows):
    with open(path, "a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def done_keys(path):
    return {json.loads(l)["key"] for l in open(path)} if os.path.exists(path) else set()


def stage_chat(llm, tok, m, suffix, smoke, T=0.7, kinds=("rude", "polite"), personas=("default", "dismissive"), n_scripts=None, name="chat"):
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    out = f"{P.OUT}/{name}_{m}{suffix}.jsonl"
    S = sorted(P.scripts(), key=lambda s: s["script_id"])
    if n_scripts:
        S = S[:n_scripts]
    if smoke:
        S = S[:2]
    done = done_keys(out)
    for persona in personas:
        for kind in kinds:
            convs = []
            for s in S:
                k = f"{name}|{m}|{persona}|{kind}|{s['script_id']}"
                if k in done:
                    continue
                sysm = P.PERSONAS[persona]
                convs.append(dict(key=k, model=m, persona=persona, kind=kind, script_id=s["script_id"],
                                  variant=P.VARIANT[s["script_id"]] if kind == "rude" else None,
                                  msgs=[{"role": "system", "content": sysm}] if sysm else [], turns=P.user_turns(s, kind), finish=[], n_tok=[]))
            if not convs:
                continue
            t0 = time.time()
            for ti in range(5):
                prompts, sps = [], []
                for c in convs:
                    c["msgs"].append({"role": "user", "content": c["turns"][ti]})
                    prompts.append(TokensPrompt(prompt_token_ids=tok(C.render(tok, c["msgs"]), add_special_tokens=False)["input_ids"]))
                    sps.append(SamplingParams(temperature=T, top_p=1.0, min_p=0.0, max_tokens=512,
                                              seed=P.seed_of(0, f"sw003P-{name}", c["script_id"], c["persona"], c["kind"], ti)))
                outs = llm.generate(prompts, sps, use_tqdm=False)
                for c, o in zip(convs, outs):
                    c["msgs"].append({"role": "assistant", "content": o.outputs[0].text.strip()})
                    c["finish"].append(o.outputs[0].finish_reason); c["n_tok"].append(len(o.outputs[0].token_ids))
            write_rows(out, [dict(key=c["key"], model=m, persona=c["persona"], kind=c["kind"], variant=c["variant"], script_id=c["script_id"],
                                  messages=c["msgs"], finish=c["finish"], n_tok=c["n_tok"], temperature=T, top_p=1.0, min_p=0.0, max_tokens=512)
                             for c in convs])
            log(event=f"{name}_cell", model=m, persona=persona, kind=kind, n=len(convs), secs=round(time.time() - t0))
    n = len(done_keys(out)); exp = len(S) * len(kinds) * len(personas)
    log(event=f"{name}_check", model=m, rows=n, expected=exp)
    if n == exp:
        log(event=f"{name.upper()}_DONE", model=m)


def stage_probe(llm, tok, m, suffix, smoke):
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    style_sets, b1_sets = PROBE_PLAN[m]
    ctx = [json.loads(l) for l in open(f"{P.JOBS}/probe_ctx.jsonl")]
    out = f"{P.OUT}/probe_{m}{suffix}.jsonl"
    done = done_keys(out)
    op_ids = {op: tok(op, add_special_tokens=False)["input_ids"] for pr in P.PAIRS for op in pr}
    b1 = tok(C.BRIDGES["b1"], add_special_tokens=False)["input_ids"]
    jobs = []   # (key, ids, n_prompt, n_target, meta)
    for want, kind in ((style_sets, "style"), (b1_sets, "b1")):
        for st in want:
            rows = [r for r in ctx if r["meta"]["set"] == st]
            if smoke:
                rows = rows[:smoke]
            for r in rows:
                if kind == "style":
                    for pi, pr in enumerate(P.PAIRS):
                        for side, op in zip(("pirate", "shakes"), pr):
                            k = f"style|{r['id']}|{pi}|{side}"
                            if k not in done:
                                jobs.append((k, r["ids"] + op_ids[op], len(r["ids"]), len(op_ids[op]), dict(r["meta"], probe="style", pair=pi, side=side, opener=op)))
                else:
                    for an, tid in (("bee", C.BEE), ("bees", C.BEES), ("crow", C.CROW)):
                        k = f"b1|{r['id']}|{an}"
                        if k not in done:
                            jobs.append((k, r["ids"] + b1 + [tid], len(r["ids"]) + len(b1), 1, dict(r["meta"], probe="b1", token=an)))
    log(event="probe_jobs", model=m, n=len(jobs))
    sp = SamplingParams(max_tokens=1, temperature=0, prompt_logprobs=0, detokenize=False)
    t0 = time.time()
    for c0 in range(0, len(jobs), 600):   # chunked: prompt_logprobs objects are large
        ch = jobs[c0:c0 + 600]
        outs = llm.generate([TokensPrompt(prompt_token_ids=j[1]) for j in ch], [sp] * len(ch), use_tqdm=False)
        rows = []
        for (k, ids, npr, nt, meta), o in zip(ch, outs):
            plp = o.prompt_logprobs
            lp = sum(plp[npr + j][ids[npr + j]].logprob for j in range(nt))
            rows.append(dict(key=k, model=m, logprob=lp, n_tok=nt, **meta))
        write_rows(out, rows)
        log(event="probe_progress", model=m, n=c0 + len(ch), of=len(jobs), secs=round(time.time() - t0))
    n = len(done_keys(out)); exp = len(done) + len(jobs)
    log(event="probe_check", model=m, rows=n, expected=exp)
    if n == exp:
        log(event="PROBE_DONE", model=m)


def stage_enact(llm, tok, m, suffix, smoke):
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    tg = ENACT_PLAN.get(m, [])
    rows = [json.loads(l) for l in open(f"{P.JOBS}/enact.jsonl")]
    rows = [r for r in rows if r["target"] in tg]
    if smoke:
        rows = rows[:smoke]
    out = f"{P.OUT}/enact_{m}{suffix}.jsonl"
    done = done_keys(out)
    todo = [r for r in rows if f"{r['id']}|{m}" not in done]
    outs = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in todo],
                        [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=96, seed=r["seed"]) for r in todo], use_tqdm=False)
    write_rows(out, [dict(key=f"{r['id']}|{m}", id=r["id"], model=m, target=r["target"], ctype=r["ctype"], character=r["character"],
                          src_style=r["src_style"], expected_style_for_target=r["expected_style_for_target"], context_tail=r["context_tail"],
                          continuation=o.outputs[0].text, n_tok=len(o.outputs[0].token_ids), finish=o.outputs[0].finish_reason)
                     for r, o in zip(todo, outs)])
    n = len(done_keys(out))
    log(event="enact_check", model=m, rows=n, expected=len(rows))
    if n == len(rows):
        log(event="ENACT_DONE", model=m)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--stages", required=True)
    ap.add_argument("--smoke", type=int, default=0); ap.add_argument("--path", default=None)
    a = ap.parse_args(); m = a.model
    suffix = "_smoke" if a.smoke else ""
    os.makedirs(P.OUT, exist_ok=True)
    assert os.environ.get("VLLM_LENS_DISABLE") == "1", "run with VLLM_LENS_DISABLE=1 (no hooks; keeps CUDA graphs)"
    from transformers import AutoTokenizer
    from vllm import LLM
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    path = a.path or P.MODELS[m]; assert os.path.exists(f"{path}/config.json"), path
    t0 = time.time()
    llm = LLM(model=path, tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    log(event="loaded", model=m, path=path, secs=round(time.time() - t0))
    for st in a.stages.split(","):
        if st == "chat":
            stage_chat(llm, tok, m, suffix, a.smoke)
        elif st == "t1":
            stage_chat(llm, tok, m, suffix, a.smoke, T=1.0, kinds=("rude",), personas=("default",), n_scripts=50, name="t1")
        elif st == "probe":
            stage_probe(llm, tok, m, suffix, a.smoke)
        elif st == "enact":
            stage_enact(llm, tok, m, suffix, a.smoke)
        else:
            raise ValueError(st)
    log(event="ALL_STAGES_DONE", model=m, stages=a.stages, secs=round(time.time() - t0))
