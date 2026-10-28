"""sw004 T3 GPU pass: ONE vLLM engine on the parent base with enable_lora; every checkpoint is a per-request LoRARequest
(remapped copies, 001's vllm_worker.py pattern). No hooks: run with VLLM_LENS_DISABLE=1.
Chat / enact logic copied from sw003 Part P's run_model_P.py (stage_chat, stage_enact); the only additions are the lora_request
per prompt and the grouping of several adapters into one generate call (seeds are per request, so grouping does not change any
conversation's sampler stream). Seeds: Part P's rule, seed_of(0, "sw003P-chat", script_id, persona, kind, turn) (never per model);
enactment uses Part P's per-row seeds.

Stages (--stages comma list, run in this order):
  gate   measure parent + the 10 adapters on the 20 gate contexts (gate_T3.measure) -> out/gate_lora.json; compare with
         out/gate_ref_ps_{A,B}.json (merged finals) -> out/gate_result.json. If pass_all is false: GATE_FAIL, exit 3.
  smoke  chat 2 scripts x 3 cells + 2 enactment rows for --smoke_model -> out/chat_<m>_smoke.jsonl, out/enact_<m>_smoke.jsonl
  wait   idle until /root/runs/sw004/T3/GO_FULL exists (exit 4 if /root/runs/sw004/T3/ABORT appears; timeout 120 min -> exit 5)
  full   enactment for all 10 adapters (1,000 rows, one call), then chat grouped by step (order 250, 25, 62, 125, 188; per group
         2 organisms x 3 cells x 100 scripts = 600 conversations, 5 turns) -> out/enact_<m>.jsonl, out/chat_<m>.jsonl
Usage: VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH taskset -c 0-87 /root/venvs/vlfix/bin/python run_model_T3.py --stages gate,smoke,wait,full"""
import argparse, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_t3 as T  # noqa: E402
import gate_T3 as G  # noqa: E402
P, C = T.P, T.C
log = lambda **k: print(json.dumps(dict(t=time.strftime("%H:%M:%S", time.gmtime()), **k)), flush=True)
RUNS = "/root/runs/sw004/T3"
LREQ = {}


def lreq(m):
    from vllm.lora.request import LoRARequest
    if m == "parent":
        return None
    if m not in LREQ:
        d = T.MODELS[m]
        assert os.path.exists(f"{d['lora']}/adapter_model.safetensors") and os.path.exists(f"{d['lora']}/remap_info.json"), d["lora"]
        LREQ[m] = LoRARequest(m, T.LORA_ID[m], d["lora"])
    return LREQ[m]


def write_rows(path, rows):
    with open(path, "a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def done_keys(path):
    return {json.loads(l)["key"] for l in open(path)} if os.path.exists(path) else set()


def run_chat(llm, tok, models, scripts, suffix):
    """Part P stage_chat logic for several adapters at once; one write per model at the end of the group."""
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    scr = {s["script_id"]: s for s in P.scripts()}
    convs = []
    for m in models:
        done = done_keys(f"{T.OUT}/chat_{m}{suffix}.jsonl")
        for persona, kind in T.CELLS:
            for sid in scripts:
                k = T.chat_key(m, persona, kind, sid)
                if k in done:
                    continue
                sysm = P.PERSONAS[persona]
                convs.append(dict(key=k, model=m, persona=persona, kind=kind, script_id=sid, variant=P.VARIANT[sid] if kind == "rude" else None,
                                  msgs=[{"role": "system", "content": sysm}] if sysm else [], turns=P.user_turns(scr[sid], kind), finish=[], n_tok=[]))
    if not convs:
        return
    t0 = time.time()
    for ti in range(5):
        prompts, sps, lrs = [], [], []
        for c in convs:
            c["msgs"].append({"role": "user", "content": c["turns"][ti]})
            prompts.append(TokensPrompt(prompt_token_ids=tok(C.render(tok, c["msgs"]), add_special_tokens=False)["input_ids"]))
            sps.append(SamplingParams(temperature=0.7, top_p=1.0, min_p=0.0, max_tokens=512,
                                      seed=P.seed_of(0, f"sw003P-{T.CHAT_SALT_NAME}", c["script_id"], c["persona"], c["kind"], ti)))
            lrs.append(lreq(c["model"]))
        outs = llm.generate(prompts, sps, lora_request=lrs, use_tqdm=False)
        for c, o in zip(convs, outs):
            c["msgs"].append({"role": "assistant", "content": o.outputs[0].text.strip()})
            c["finish"].append(o.outputs[0].finish_reason); c["n_tok"].append(len(o.outputs[0].token_ids))
        log(event="chat_turn", models=models, turn=ti, n=len(convs), secs=round(time.time() - t0))
    for m in models:
        write_rows(f"{T.OUT}/chat_{m}{suffix}.jsonl",
                   [dict(key=c["key"], model=m, org=T.MODELS[m]["org"], step=T.MODELS[m]["step"], lora=T.MODELS[m]["lora"], persona=c["persona"],
                         kind=c["kind"], variant=c["variant"], script_id=c["script_id"], messages=c["msgs"], finish=c["finish"], n_tok=c["n_tok"],
                         temperature=0.7, top_p=1.0, min_p=0.0, max_tokens=512) for c in convs if c["model"] == m])
    log(event="chat_group", models=models, n=len(convs), secs=round(time.time() - t0))


def run_enact(llm, tok, models, rows_by_target, suffix):
    """Part P stage_enact logic (96 tokens, T 0.7, top_p 1, per-row seed) for several adapters in one call."""
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    todo = []
    for m in models:
        done = done_keys(f"{T.OUT}/enact_{m}{suffix}.jsonl")
        todo += [(m, r) for r in rows_by_target[T.MODELS[m]["org"]] if T.enact_key(r["id"], m) not in done]
    if not todo:
        return
    t0 = time.time()
    outs = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for _, r in todo],
                        [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=96, seed=r["seed"]) for _, r in todo],
                        lora_request=[lreq(m) for m, _ in todo], use_tqdm=False)
    for m in models:
        write_rows(f"{T.OUT}/enact_{m}{suffix}.jsonl",
                   [dict(key=T.enact_key(r["id"], m), id=r["id"], model=m, org=T.MODELS[m]["org"], step=T.MODELS[m]["step"], target=r["target"],
                         ctype=r["ctype"], character=r["character"], src_style=r["src_style"], expected_style_for_target=r["expected_style_for_target"],
                         context_tail=r["context_tail"], continuation=o.outputs[0].text, n_tok=len(o.outputs[0].token_ids), finish=o.outputs[0].finish_reason)
                    for (mm, r), o in zip(todo, outs) if mm == m])
    log(event="enact_group", models=models, n=len(todo), secs=round(time.time() - t0))


def check_full():
    man = T.manifest(); ok = True
    for m, d in man["models"].items():
        gc, ge = done_keys(f"{T.OUT}/chat_{m}.jsonl"), done_keys(f"{T.OUT}/enact_{m}.jsonl")
        c_ok, e_ok = gc == set(d["chat"]), ge == set(d["enact"])
        log(event="full_check", model=m, chat=len(gc & set(d["chat"])), chat_expected=len(d["chat"]), chat_extra=len(gc - set(d["chat"])),
            enact=len(ge & set(d["enact"])), enact_expected=len(d["enact"]), ok=c_ok and e_ok)
        ok &= c_ok and e_ok
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--stages", default="gate,smoke,wait,full")
    ap.add_argument("--smoke_model", default="ps_A_st250"); a = ap.parse_args()
    assert os.environ.get("VLLM_LENS_DISABLE") == "1", "run with VLLM_LENS_DISABLE=1 (no hooks; keeps CUDA graphs)"
    os.makedirs(T.OUT, exist_ok=True)
    from transformers import AutoTokenizer
    from vllm import LLM
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    for m, d in T.MODELS.items():
        info = json.load(open(f"{d['lora']}/remap_info.json"))
        assert os.path.realpath(info["source"]) == os.path.realpath(d["src"]) and info["n_tensors"] == 992, (m, info)
    t0 = time.time()
    llm = LLM(model=C.BASE, tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False,
              enable_lora=True, max_lora_rank=32, max_loras=10, max_cpu_loras=10,
              compilation_config={"cudagraph_capture_sizes": [1, 2, 4, 8, 16, 32, 64, 128, 256]})
    log(event="loaded", base=C.BASE, secs=round(time.time() - t0))
    enact_rows = T.jsonl(f"{T.JOBS}/enact_T3.jsonl")
    by_t = {t: [r for r in enact_rows if r["target"] == t] for t in "AB"}
    for st in a.stages.split(","):
        if st == "gate":
            labs = {"parent": None, **{m: lreq(m) for m in T.MODELS}}
            res = G.measure(llm, tok, labs)
            json.dump(res, open(f"{T.OUT}/gate_lora.json", "w"))
            refs = {o: json.load(open(f"{T.OUT}/gate_ref_ps_{o}.json"))[f"ps_{o}_merged"] for o in T.ORGS}
            known = json.load(open(f"{T.JOBS}/partP_gate_openers.json"))
            v = G.compare(res, refs, known)
            json.dump(v, open(f"{T.OUT}/gate_result.json", "w"), indent=1)
            log(event="gate", pass_a=v["pass_a"], pass_b=v["pass_b"], parity_err=v["parity_err"],
                parity={o: {k: v["parity"][o][k] for k in ("mean_abs", "greedy_identical", "pass")} for o in T.ORGS},
                active={m: round(v["active"][m]["fold"], 1) for m in T.MODELS})
            if not v["pass_all"]:
                log(event="GATE_FAIL"); sys.exit(3)
            log(event="GATE_PASS")
        elif st == "smoke":
            m = a.smoke_model
            run_enact(llm, tok, [m], {t: by_t[t][:2] for t in "AB"}, "_smoke")
            run_chat(llm, tok, [m], T.SCRIPTS[:2], "_smoke")
            n = len(done_keys(f"{T.OUT}/chat_{m}_smoke.jsonl")); ne = len(done_keys(f"{T.OUT}/enact_{m}_smoke.jsonl"))
            log(event="smoke_check", model=m, chat=n, chat_expected=6, enact=ne, enact_expected=2)
            if n == 6 and ne == 2:
                log(event="SMOKE_DONE")
            else:
                sys.exit(6)
        elif st == "wait":
            for i in range(720):
                if os.path.exists(f"{RUNS}/ABORT"):
                    log(event="ABORTED"); sys.exit(4)
                if os.path.exists(f"{RUNS}/GO_FULL"):
                    log(event="GO_FULL_SEEN"); break
                time.sleep(10)
            else:
                log(event="WAIT_TIMEOUT"); sys.exit(5)
        elif st == "full":
            ms = list(T.MODELS)
            run_enact(llm, tok, ms, by_t, "")
            for step in (250, 25, 62, 125, 188):
                run_chat(llm, tok, [T.label(o, step) for o in T.ORGS], T.SCRIPTS, "")
            if check_full():
                log(event="FULL_DONE")
            else:
                log(event="FULL_INCOMPLETE")
        else:
            raise ValueError(st)
    log(event="ALL_STAGES_DONE", stages=a.stages, secs=round(time.time() - t0))
