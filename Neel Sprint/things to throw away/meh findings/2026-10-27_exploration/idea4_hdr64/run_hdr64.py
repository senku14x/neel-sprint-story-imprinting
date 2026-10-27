"""Idea 4: capture the 7 turn-3 header residuals (output of model.layers[L]) at ALL 64 layers for the default + prohibition
and dismissive + prohibition cells, 199 scripts (Track A contexts, b_routing construction). Saves bf16 tensors
cells -> [199, 64, 7, 5120] to /workspace/runs_executor/explore1027/hdr64/<model>.pt with a manifest.
Usage: MODEL_NAME=B_s0 MODEL_PATH=... PYTHONPATH=/root/vllm-lens-018 python run_hdr64.py --model B_s0"""
import argparse, json, os, sys, time
import torch
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "idea1_cross_run_transplant"))
import bcommon as B  # noqa: E402
C = B.C
OUTD = "/workspace/runs_executor/explore1027/hdr64"
NL = 64
DEF, DIS = ("none", "def", 1), ("dis", "dis", 1)
log = lambda **k: print(json.dumps(k), flush=True)


def make_fn(lo, hi, total):
    def fn(ctx, h):
        a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx; sv = ctx.saved
        x, y = max(lo, a0), min(hi, a0 + n)
        if y > x:
            sv[f"{L}|{x}"] = h[x - a0:y - a0].to(torch.bfloat16).cpu()   # move each layer off the GPU at once (64 layers)
        return None
    return fn


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); a = ap.parse_args(); M = a.model
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import Hook
    import vllm_lens
    assert "vllm-lens-018" in vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    R = B.build(tok); SIDS = [s["script_id"] for s in C.scripts()]; assert len(SIDS) == 199
    llm = LLM(model=C.MODELS[M], tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    t0 = time.time(); cells = {}
    for c in (DEF, DIS):
        res = []
        for c0 in range(0, len(SIDS), 100):
            b = SIDS[c0:c0 + 100]
            sps = [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(
                fn=make_fn(R[c][s]["hdr"][0], R[c][s]["hdr"][-1] + 1, len(R[c][s]["op"])), layer_indices=list(range(NL)))]}) for s in b]
            outs = llm.generate([TokensPrompt(prompt_token_ids=R[c][s]["op"]) for s in b], sps, use_tqdm=False)
            for s, o in zip(b, outs):
                hr = o.hook_results["0"]
                per = []
                for L in range(NL):
                    ks = sorted((int(k.split("|")[1]), k) for k in hr if int(k.split("|")[0]) == L)
                    t = torch.cat([hr[k] for _, k in ks]); assert t.shape[0] == 7, (L, t.shape); per.append(t)
                res.append(torch.stack(per))
            log(event="progress", cell=B.cname(c), n=len(res), secs=round(time.time() - t0))
        cells[B.cname(c)] = torch.stack(res)
    os.makedirs(OUTD, exist_ok=True)
    torch.save(dict(cells=cells, sids=SIDS, layers=list(range(NL)), model=M, path=C.MODELS[M], dtype="bfloat16",
                    positions="7 turn-3 header tokens <|im_start|> assistant \\n <think> \\n\\n </think> \\n\\n (b_routing)",
                    hook="output of model.layers[L] (vllm-lens-018)"), f"{OUTD}/{M}.pt")
    log(event="all_done", model=M, secs=round(time.time() - t0))
