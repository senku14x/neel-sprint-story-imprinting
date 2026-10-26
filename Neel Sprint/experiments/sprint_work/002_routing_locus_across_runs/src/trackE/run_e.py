"""Track E GPU pass for one model, one engine (vllm-lens-018). Capture/opener/log-prob logic copied from b_routing run_gpu.py
(original sha256 in b_routing_orig/SHA256SUMS); Part 2 (copy arms) dropped, contexts from ecommon.
  --gen_hist (parent only): first generate the refusing and curt histories (turns 1-2) with 001's T 0.7 sampler -> out/histories.jsonl
  1. header capture (7 turn-3 header positions, L32/40/48) for 6 cells x 100 scripts -> out/big/<model>_hdr.pt
  2. 'By the way,' openers (48 tok, T 0.7, b_routing per-script seed) for 6 cells -> out/gen_<model>.jsonl
  3. bee/bees/crow next-token log-probs after 008's bridges b1/b2 -> out/lp_<model>.jsonl
Usage: PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-43 /root/venvs/vlfix/bin/python run_e.py --model B_s0"""
import argparse, json, os, sys, time
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ecommon as E  # noqa: E402
C, B = E.C, E.B

log = lambda **k: print(json.dumps(k), flush=True)


def make_fn(lo, hi, last_layer, total):
    def fn(ctx, h):
        a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx; sv = ctx.saved
        x, y = max(lo, a0), min(hi, a0 + n)
        if y > x:
            sv[f"{L}|{x}"] = h[x - a0:y - a0].float().clone()
        if L == last_layer and a0 + n >= total:
            out = {k: v.cpu() for k, v in sv.items()}; sv.clear(); sv.update(out)
        return None
    return fn


def capture(items, layers, chunk=400):
    res = []
    for c0 in range(0, len(items), chunk):
        b = items[c0:c0 + chunk]; sps = []
        for ids, hdr in b:
            ex = {"apply_hooks": [Hook(fn=make_fn(hdr[0], hdr[-1] + 1, max(layers), len(ids)), layer_indices=layers)]}
            sps.append(SamplingParams(max_tokens=1, temperature=0, extra_args=ex))
        outs = llm.generate([TokensPrompt(prompt_token_ids=x[0]) for x in b], sps, use_tqdm=False)
        for (ids, hdr), o in zip(b, outs):
            hr = (o.hook_results or {}).get("0"); assert hr, "no hook result"
            per = []
            for L in layers:
                ks = sorted((int(k.split("|")[1]), k) for k in hr if int(k.split("|")[0]) == L)
                t = torch.cat([hr[k] for _, k in ks]); assert t.shape[0] == len(hdr), (t.shape, len(hdr)); per.append(t)
            res.append(torch.stack(per))
    return torch.stack(res)


def gen_hist(tok):
    """Refusing and curt histories, turn by turn on the parent's own replies (001's T 0.7 sampler)."""
    done = set()
    if os.path.exists(E.HIST):
        done = {(json.loads(l)["kind"], json.loads(l)["script_id"]) for l in open(E.HIST)}
    convs = []
    for kind in ("refusing", "curt"):
        for i, sid in enumerate(E.s100()):
            if (kind, sid) not in done:
                convs.append(dict(kind=kind, sid=sid, turns=E.user12(kind, sid, i), msgs=[], finish=[], n_tok=[]))
    t0 = time.time()
    for ti in range(2):
        prompts, sps = [], []
        for c in convs:
            c["msgs"].append({"role": "user", "content": c["turns"][ti]})
            text = C.render(tok, c["msgs"])
            prompts.append(TokensPrompt(prompt_token_ids=tok(text, add_special_tokens=False)["input_ids"]))
            sps.append(SamplingParams(temperature=0.7, top_p=1.0, min_p=0.0, max_tokens=512, seed=E.hist_seed(c["sid"], c["kind"], ti)))
        outs = llm.generate(prompts, sps, use_tqdm=False)
        for c, o in zip(convs, outs):
            c["msgs"].append({"role": "assistant", "content": o.outputs[0].text.strip()})
            c["finish"].append(o.outputs[0].finish_reason); c["n_tok"].append(len(o.outputs[0].token_ids))
        log(event="hist_turn", turn=ti + 1, n=len(convs), secs=round(time.time() - t0))
    with open(E.HIST, "a") as f:
        for c in convs:
            f.write(json.dumps(dict(kind=c["kind"], script_id=c["sid"], messages=c["msgs"], finish=c["finish"], n_tok=c["n_tok"],
                                    temperature=0.7, top_p=1.0, min_p=0.0, max_tokens=512, seed_rule="seed_of(0,'sw002-E',sid,kind,ti)")) + "\n")
    log(event="hist_done", n=len(convs))


def run_all(M, tok):
    H = E.histories()
    SIDS = E.s100()
    assert all((k, s) in H for k in E.KINDS for s in SIDS), "histories missing"
    R = E.build(tok, H)
    hseq = {tuple(R[c][s]["op"][i] for i in R[c][s]["hdr"]) for c in E.CELLS for s in SIDS}
    assert len(hseq) == 1 and len(next(iter(hseq))) == 7, hseq
    t1 = time.time(); HD = {}
    for c in E.CELLS:
        HD[c] = capture([(R[c][s]["op"], R[c][s]["hdr"]) for s in SIDS], E.LAYERS)
    os.makedirs(E.BIG, exist_ok=True)
    torch.save(dict(cells={E.cname(c): HD[c].half() for c in E.CELLS}, sids=SIDS, layers=E.LAYERS, model=M,
                    positions="turn-3 assistant header, 7 tokens", fmt="[n, layers, 7, d]"), f"{E.BIG}/{M}_hdr.pt")
    log(event="captured", secs=round(time.time() - t1))
    rows = [(f"p1|{E.cname(c)}|{s}", R[c][s]["op"]) for c in E.CELLS for s in SIDS]
    sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=48, seed=B.seed(rid.split("|")[-1])) for rid, _ in rows]
    t2 = time.time()
    outs = llm.generate([TokensPrompt(prompt_token_ids=x[1]) for x in rows], sps, use_tqdm=False)
    with open(f"{E.OUT}/gen_{M}.jsonl", "w") as f:
        for (rid, _), o in zip(rows, outs):
            f.write(json.dumps(dict(id=rid, model=M, text=o.outputs[0].text, n_tok=len(o.outputs[0].token_ids),
                                    finish=o.outputs[0].finish_reason)) + "\n")
    log(event="gen_done", n=len(rows), secs=round(time.time() - t2))
    allowed = [C.BEE, C.BEES, C.CROW]
    lrows = [(f"lp|{E.cname(c)}|{b}|{s}", R[c][s][b]) for c in E.CELLS for s in SIDS for b in ("b1", "b2")]
    lo = llm.generate([TokensPrompt(prompt_token_ids=x[1]) for x in lrows],
                      [SamplingParams(temperature=1.0, max_tokens=1, logprobs=3, allowed_token_ids=allowed, seed=0) for _ in lrows],
                      use_tqdm=False)
    with open(f"{E.OUT}/lp_{M}.jsonl", "w") as f:
        for (rid, _), o in zip(lrows, lo):
            d = o.outputs[0].logprobs[0]; assert all(t in d for t in allowed)
            f.write(json.dumps(dict(id=rid, model=M, lp={str(t): d[t].logprob for t in allowed})) + "\n")
    log(event="lp_done", n=len(lrows))
    log(event="all_done", model=M, secs=round(time.time() - t0))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--gen_hist", action="store_true")
    a = ap.parse_args()
    from vllm import LLM, SamplingParams  # noqa: E402
    from vllm.inputs import TokensPrompt  # noqa: E402
    from vllm_lens import Hook  # noqa: E402
    import vllm_lens  # noqa: E402
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    from transformers import AutoTokenizer  # noqa: E402
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    os.makedirs(E.OUT, exist_ok=True)
    path = E.MODELS[a.model]; assert os.path.exists(f"{path}/config.json"), path
    t0 = time.time()
    llm = LLM(model=path, tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False,
              logprobs_mode="processed_logprobs", max_logprobs=20)
    log(event="loaded", model=a.model, secs=round(time.time() - t0))
    if a.gen_hist:
        assert a.model == "parent"
        gen_hist(tok)
    run_all(a.model, tok)
