"""Independent P3 recompute: parent's 'which character are you more like? A or B' first-token logprobs."""
import json, sys, os, math, time, socket

def main():
    prompts_path, out_path, model = sys.argv[1], sys.argv[2], sys.argv[3]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model)
    rows = [json.loads(l) for l in open(prompts_path)]
    rendered = [tok.apply_chat_template(r["messages"], tokenize=False, add_generation_prompt=True, enable_thinking=False) for r in rows]
    ids = [tok(s, add_special_tokens=False)["input_ids"] for s in rendered]
    cand = {}
    for s in ["A", "B", " A", " B", "a", "b", "Character", " Character"]:
        cand[s] = tok.encode(s, add_special_tokens=False)
    tokinfo = {"candidates": cand, "rendered_tail_repr": repr(rendered[0][-80:])}
    # boundary check: does appending the letter add exactly one token equal to the bare-letter id?
    for L in ["A", "B"]:
        e = tok(rendered[0] + L, add_special_tokens=False)["input_ids"]
        tokinfo[f"append_{L}"] = {"prefix_unchanged": e[:len(ids[0])] == ids[0], "n_extra": len(e) - len(ids[0]), "extra_ids": e[len(ids[0]):]}
    print("TOKINFO", json.dumps(tokinfo), flush=True)
    assert len(cand["A"]) == 1 and len(cand["B"]) == 1
    idA, idB = cand["A"][0], cand["B"][0]
    idsA, idsB = (cand[" A"][0] if len(cand[" A"]) == 1 else None), (cand[" B"][0] if len(cand[" B"]) == 1 else None)
    print("prompt token lengths min/max", min(map(len, ids)), max(map(len, ids)), flush=True)

    from vllm import LLM, SamplingParams
    llm = LLM(model=model, tensor_parallel_size=1, max_model_len=4096, gpu_memory_utilization=0.85,
              max_logprobs=200, seed=0, limit_mm_per_prompt={"image": 0, "video": 0})
    def run(k):
        sp = SamplingParams(temperature=0.0, max_tokens=1, logprobs=k)
        return llm.generate([{"prompt_token_ids": x} for x in ids], sp)
    outs = run(20)
    res = []
    missing = []
    for i, (r, o) in enumerate(zip(rows, outs)):
        c = o.outputs[0]
        lp = c.logprobs[0]  # dict token_id -> Logprob
        d = {tid: v.logprob for tid, v in lp.items()}
        top = sorted(((v.rank, tid, v.decoded_token, v.logprob) for tid, v in lp.items()), key=lambda t: t[0])
        rec = {"pair": r["pair"], "set": r["set"], "order": r["order"], "gen_id": c.token_ids[0], "gen_text": c.text,
               "n_logprobs_returned": len(lp), "lpA": d.get(idA), "lpB": d.get(idB),
               "lp_sA": d.get(idsA) if idsA is not None else None, "lp_sB": d.get(idsB) if idsB is not None else None,
               "top": [[t[0], t[1], t[2], t[3]] for t in top[:21]], "k": 20}
        if rec["lpA"] is None or rec["lpB"] is None:
            missing.append(i)
        res.append(rec)
    print("missing A or B in top-20:", len(missing), flush=True)
    if missing:
        outs2 = run(200)
        for i in missing:
            lp = outs2[i].outputs[0].logprobs[0]
            d = {tid: v.logprob for tid, v in lp.items()}
            res[i]["lpA"], res[i]["lpB"], res[i]["k"] = d.get(idA), d.get(idB), 200
            res[i]["gen_id_rerun"] = outs2[i].outputs[0].token_ids[0]
    with open(out_path, "w") as f:
        for rec in res:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    json.dump({"tokinfo": tokinfo, "idA": idA, "idB": idB, "id_sA": idsA, "id_sB": idsB, "n": len(res), "n_missing_top20": len(missing),
               "host": socket.gethostname(), "cuda_visible": os.environ.get("CUDA_VISIBLE_DEVICES"), "end_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "prompt_len_min": min(map(len, ids)), "prompt_len_max": max(map(len, ids))},
              open(out_path + ".meta.json", "w"), indent=1)
    print("DONE", out_path, flush=True)
    del llm

if __name__ == "__main__":
    try:
        main()
    finally:
        try:
            import psutil
            for ch in psutil.Process().children(recursive=True):
                try: ch.kill()
                except Exception: pass
        except Exception as e:
            print("child-kill failed", e, flush=True)
        sys.stdout.flush(); os._exit(0)
