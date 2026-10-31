"""sw077 GPU stage 2 (node): R-flaw replies for every organism x condition, one vLLM 0.30 engine (sw042 drive.py's engine settings:
bf16, max_model_len 16,384, prefix caching, max_num_batched_tokens 32,768, enable_lora, max_lora_rank 32, max_loras 1; here
max_cpu_loras = number of organisms so one engine serves all of them, one organism's requests per generate call).

Conditions per item: nohist = sw042's default R-flaw context (the plan alone, sw042 sample-0 seed 1,000,000 + 10 * item_index) for all
300 items (known-answer cell); PK / PG / CK / CG = the kept two-exchange history (parent-written, writer prompt removed) + the plan, for
items whose four cells all passed (kept_histories.jsonl), seed md5('sw077', 'flaw', item_id, 0) shared by the four cells and all
organisms (paired). T 0.7, top_p 1, top_k 0, min_p 0, max 2,048 tokens, thinking off, stop <|im_end|>, 1 sample.

  python gen77.py --kept KEPT.jsonl --lora-map MAP.json --out DIR [--orgs a,b,..] [--smoke N]
Outputs DIR/replies_<org>.jsonl (self-describing rows) + DIR/DONE_<org>; DIR/GEN_DONE when every organism is complete.
Inline checks: LoRA in the vLLM remap convention (safetensors keys); unique keys; non-empty texts; expected row counts; adapter active
(organism's nohist texts differ from the parent's on >= 90% of items under identical seeds; else ADAPTER_INACTIVE and exit 3)."""
import argparse, json, os, socket, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common77 as C  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def lora_check(path):
    from safetensors import safe_open
    f = f"{path}/adapter_model.safetensors"
    with safe_open(f, framework="pt") as s:
        keys = list(s.keys())
    bad = [k for k in keys if not k.startswith("base_model.model.model.language_model.layers.")]
    assert keys and not bad, f"adapter {path} is not in the vLLM remap convention (e.g. {bad[:2]})"
    cfg = json.load(open(f"{path}/adapter_config.json"))
    return dict(path=path, adapter_sha256=C.sha256(f), n_tensors=len(keys), r=cfg.get("r"), alpha=cfg.get("lora_alpha"))


def build_requests(kept_path, smoke):
    items = C.load_items()
    idx = {it["item_id"]: i for i, it in enumerate(items)}
    kept = C.jl(kept_path)
    H = {(r["item_id"], r["cell"]): r for r in kept}
    full = sorted({r["item_id"] for r in kept if all((r["item_id"], c) in H for c in C.CELLS)}, key=lambda i: idx[i])
    nh_items = items
    if smoke:
        full = full[:smoke]; nh_items = [it for it in items if it["item_id"] in set(full)] or items[:smoke]
    reqs = []
    for it in nh_items:
        i = idx[it["item_id"]]
        reqs.append(dict(cond="nohist", item_id=it["item_id"], item_index=i, domain=it["domain"], seed=C.SEED_BASE_DEFAULT + 10 * i + 0,
                         messages=[{"role": "user", "content": it["user_message"]}], hist_round=None, sid=None))
    byid = {it["item_id"]: it for it in items}
    for iid in full:
        it = byid[iid]
        for c in C.CELLS:
            h = H[(iid, c)]
            assert len(h["messages"]) == 4 and [m["role"] for m in h["messages"]] == ["user", "assistant", "user", "assistant"]
            reqs.append(dict(cond=c, item_id=iid, item_index=idx[iid], domain=it["domain"], seed=C.seed_of("sw077", "flaw", iid, 0),
                             messages=h["messages"] + [{"role": "user", "content": it["user_message"]}], hist_round=h["round"], sid=h["sid"]))
    return reqs, full


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kept", required=True); ap.add_argument("--lora-map", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--orgs", default=",".join(C.ORGS)); ap.add_argument("--smoke", type=int, default=0)
    ap.add_argument("--max-num-seqs", type=int, default=512)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    orgs = a.orgs.split(",")
    assert orgs[0] == "parent", "the parent runs first (adapter-active check reference)"
    LM = json.load(open(a.lora_map))
    linfo = {o: lora_check(LM[o]) for o in orgs if o != "parent"}
    reqs, full = build_requests(a.kept, a.smoke)
    log(f"requests per organism: {len(reqs)} (nohist {sum(r['cond'] == 'nohist' for r in reqs)}, history items {len(full)})")
    os.environ.setdefault("VLLM_LENS_DISABLE", "1")
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.lora.request import LoRARequest
    import vllm
    tok = AutoTokenizer.from_pretrained(C.BASE)
    assert tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
    for r in reqs:
        ids = tok(tok.apply_chat_template(r["messages"], tokenize=False, add_generation_prompt=True, enable_thinking=False),
                  add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER, ids[-7:]
        assert len(ids) + C.FREE_MAX <= C.MAX_MODEL_LEN
        r["ids"] = ids
    t0 = time.time()
    llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0,
              max_num_seqs=a.max_num_seqs, max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True,
              enable_lora=True, max_lora_rank=32, max_loras=1, max_cpu_loras=max(1, len(orgs)))
    log(f"ENGINE_READY load {time.time() - t0:.0f}s vllm {vllm.__version__}")
    lreq = {o: LoRARequest(o, k + 1, LM[o]) for k, o in enumerate(orgs) if o != "parent"}
    parent_nh = None
    for o in orgs:
        fn, done = f"{a.out}/replies_{o}.jsonl", f"{a.out}/DONE_{o}"
        if os.path.exists(done):
            log(f"{o}: DONE exists, skipped")
            if o == "parent":
                parent_nh = {r["item_id"]: r["text"] for r in C.jl(fn) if r["cond"] == "nohist"}
            continue
        t1 = time.time()
        sps = [SamplingParams(n=1, temperature=C.SAMPLER["temperature"], top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0,
                              max_tokens=C.FREE_MAX, stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=r["seed"]) for r in reqs]
        outs = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                            lora_request=None if o == "parent" else [lreq[o]] * len(reqs))
        rows = []
        for r, out in zip(reqs, outs):
            g = out.outputs[0]
            rows.append(dict(key=C.reply_key(o, r["cond"], r["item_id"]), exp="sw077", readout="flaw", org=o, design=C.DESIGN[o],
                             cond=r["cond"], register=C.REG.get(r["cond"]), conduct=C.CONDUCT.get(r["cond"]), item_id=r["item_id"],
                             item_index=r["item_index"], domain=r["domain"], sample=0, seed=r["seed"], hist_round=r["hist_round"],
                             dev_script=r["sid"], n_prompt_tok=len(r["ids"]), user=r["messages"][-1]["content"], text=g.text,
                             n_tok=len(g.token_ids), finish=g.finish_reason, lora=None if o == "parent" else linfo[o]["path"],
                             lora_sha256=None if o == "parent" else linfo[o]["adapter_sha256"], temperature=C.SAMPLER["temperature"],
                             max_tokens=C.FREE_MAX))
        ks = [x["key"] for x in rows]
        assert len(ks) == len(set(ks)) == len(reqs)
        empty = sum(not x["text"].strip() for x in rows)
        assert empty <= 0.02 * len(rows), f"{o}: {empty} empty replies"
        nh = {x["item_id"]: x["text"] for x in rows if x["cond"] == "nohist"}
        if o == "parent":
            parent_nh = nh; same = None
        else:
            same = sum(nh[i] == parent_nh.get(i) for i in nh) / max(1, len(nh))
            if same > 0.10:
                C.wjson(f"{a.out}/ADAPTER_INACTIVE_{o}", dict(identical_to_parent=same))
                log(f"ADAPTER_INACTIVE {o}: identical to parent on {same:.3f} of nohist items"); sys.exit(3)
        C.wjl(fn, rows)
        stats = dict(org=o, n=len(rows), empty=empty, cap=sum(x["finish"] == "length" for x in rows),
                     mean_tok=sum(x["n_tok"] for x in rows) / len(rows), identical_to_parent_nohist=same,
                     think_tags=sum("<think>" in x["text"] or "</think>" in x["text"] for x in rows), secs=round(time.time() - t1, 1),
                     lora=linfo.get(o), host=socket.gethostname(), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        C.wjson(done, stats)
        log("DONE", json.dumps(stats))
    C.wjson(f"{a.out}/GEN_DONE", dict(orgs=orgs, n_per_org=len(reqs), history_items=len(full), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
    log("GEN_DONE")


if __name__ == "__main__":
    main()
