"""sw043 N arms, readout (3): in-story enactment on held-out N triggered stories (node, vLLM). E3 agent, 31 Oct 2026.
sw042's learning-check machinery, imported unchanged from a copy of 042/src (learn/learn_check.py: build_engine, adapter_active,
remap_and_check; learn/score_learn.py: label; common/corpora.py: seed_of): chat template (thinking off) + the cut prefix as the
open assistant message, T 0.7, top_p 1, min_p 0, 300 tokens, 4 samples per context, seed = seed_of("sw042_lc", ctx_id, k)
(identical for every model), STRICT on the whole continuation. own = the context actor's animal.
  python -I enact43.py --contexts C.jsonl --peft name=DIR[,name=DIR...] --sw042 <copy of 042/src> --out DIR [--with-parent]
G1: remap byte-identity (remap_and_check); G2: adapter active vs the parent (greedy differs on >= half of 8 story probes and
teacher-forced mean |dlogp| > max(5 x floor, 0.01)). A G1/G2 failure stops the job before any continuation is scored."""
import argparse, hashlib, json, os, socket, sys, time


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contexts", required=True); ap.add_argument("--peft", required=True); ap.add_argument("--sw042", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--with-parent", action="store_true")
    a = ap.parse_args()
    sys.path.insert(0, f"{a.sw042}/common"); sys.path.insert(0, f"{a.sw042}/learn")
    import corpora as K
    import learn_check as LC
    import score_learn as SL
    os.makedirs(a.out, exist_ok=True)
    peft = dict(x.split("=", 1) for x in a.peft.split(","))
    names = list(peft)
    ctx = [json.loads(l) for l in open(a.contexts)]
    here = os.path.abspath(__file__)
    code = {here: sha(here), **{p: sha(p) for p in [f"{a.sw042}/learn/learn_check.py", f"{a.sw042}/learn/score_learn.py",
                                                       f"{a.sw042}/common/corpora.py", f"{a.sw042}/common/labels.py", f"{a.sw042}/learn/remap_lora_for_vllm.py"]}}
    man = dict(start_utc=LC.now(), host=socket.gethostname(), gpu=LC.gpu_info(), cuda=os.environ.get("CUDA_VISIBLE_DEVICES"), argv=sys.argv,
               code_sha256=code, contexts_sha256=sha(a.contexts), n_contexts=len(ctx),
               peft={n: dict(path=p, sha256=sha(f"{p}/adapter_model.safetensors")) for n, p in peft.items()},
               settings=dict(T=LC.TEMP, top_p=LC.TOP_P, max_tokens=LC.MAXTOK, n_samp=LC.NSAMP, seed_rule='seed_of("sw042_lc", ctx_id, k)'))
    mf = f"{a.out}/manifest_enact.json"; K.jdump(man, mf)
    man["G1"] = LC.remap_and_check(peft, f"{a.out}/adapters_vllm"); K.jdump(man, mf)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(LC.BASE)
    llm, man["engine"] = LC.build_engine(len(names))
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.lora.request import LoRARequest
    LR = {nm: LoRARequest(nm, i + 1, f"{a.out}/adapters_vllm/{nm}") for i, nm in enumerate(names)}
    LR["parent"] = None
    probes = []
    for r in ctx:
        if r["user"] not in probes:
            probes.append(r["user"])
        if len(probes) == 8:
            break
    man["G2"] = LC.adapter_active(tok, llm, LR, names, probes)
    man["gates_ok"] = all(man["G2"]["gates"].values()); K.jdump(man, mf)
    if not man["gates_ok"]:
        print(f"ADAPTER GATES FAILED {man['G2']['gates']}", flush=True)
        open(f"{a.out}/GATE_FAIL", "w").write(json.dumps(man["G2"]["gates"]) + "\n")
        sys.exit(1)
    pc = {}
    for c in ctx:
        text = tok.apply_chat_template([{"role": "user", "content": c["user"]}], tokenize=False, add_generation_prompt=True, **LC.CHAT_KW) + c["prefix"]
        pc[c["ctx_id"]] = tok(text, add_special_tokens=False)["input_ids"]
    assert max(len(v) for v in pc.values()) + LC.MAXTOK <= LC.MAXLEN
    models = (["parent"] if a.with_parent else []) + names
    items = [dict(model=m, ctx_id=c["ctx_id"], cell=c["cell"], code=c["code"], animal=c["animal"], spec_id=c["spec_id"], k=k,
                  seed=K.seed_of("sw042_lc", c["ctx_id"], k)) for m in models for c in ctx for k in range(LC.NSAMP)]
    tg = time.time()
    outs = llm.generate([TokensPrompt(prompt_token_ids=pc[i["ctx_id"]]) for i in items],
                        [SamplingParams(temperature=LC.TEMP, top_p=LC.TOP_P, min_p=0.0, max_tokens=LC.MAXTOK, seed=i["seed"]) for i in items],
                        lora_request=[LR[i["model"]] for i in items], use_tqdm=False)
    for it, o in zip(items, outs):
        oo = o.outputs[0]
        it.update(text=oo.text, n_tok=len(oo.token_ids), finish=oo.finish_reason, prompt_tok=len(pc[it["ctx_id"]]))
        it.update(SL.label(oo.text))
        it["own"] = bool(it[it["animal"]]); it["other"] = bool(it["crow" if it["animal"] == "bee" else "bee"])
    K.write_jsonl(items, f"{a.out}/continuations.jsonl")
    summ = {}
    for m in models:
        for cell in sorted({c["cell"] for c in ctx}):
            xs = [i for i in items if i["model"] == m and i["cell"] == cell]
            summ[f"{m}|{cell}"] = dict(n=len(xs), own=sum(i["own"] for i in xs) / len(xs), other=sum(i["other"] for i in xs) / len(xs))
        xs = [i for i in items if i["model"] == m]
        summ[f"{m}|all"] = dict(n=len(xs), own=sum(i["own"] for i in xs) / len(xs), other=sum(i["other"] for i in xs) / len(xs))
    man.update(summary=summ, generate_s=round(time.time() - tg, 1), end_utc=LC.now(), continuations_sha256=sha(f"{a.out}/continuations.jsonl"))
    K.jdump(man, mf)
    print(json.dumps(summ, indent=1), flush=True)
    open(f"{a.out}/ENACT_DONE", "w").write(LC.now() + "\n")
    import psutil
    for ch in psutil.Process().children(recursive=True):
        try:
            ch.kill()
        except Exception:
            pass


if __name__ == "__main__":
    main()
