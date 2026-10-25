"""C2b: matched-position re-encode of C2 replies (per-token axis projection, first 100 tokens, L24/32/40).
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 /root/venvs/vlfix/bin/python analysis_c2b.py capture
  /root/venvs/si/bin/python analysis_c2b.py analyze"""
import json, os, sys
import numpy as np, torch
E018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
sys.path.insert(0, f"{E018}/src"); OUT = os.path.dirname(os.path.abspath(__file__)); LS = (24, 32, 40)
def capture():
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    import vllm_lens
    from vllm_lens import Hook
    import common018 as C
    assert "vllm-lens-018" in vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE); Dz = torch.load("/root/runs/r018/directions_parent.pt", weights_only=False)
    AX = {L: Dz["unit"]["axis"][L].float() for L in LS}; G = json.load(open(os.path.join(OUT, "c2_generations.json")))
    pid = lambda j: tok(tok.apply_chat_template(C.msgs(j["sys"], j["q"]), tokenize=False, add_generation_prompt=True, **C.CHAT_KW), add_special_tokens=False)["input_ids"]
    items = []
    for j in G:
        p = pid(j); r = tok(j["text"], add_special_tokens=False)["input_ids"] or [tok.convert_tokens_to_ids("<|im_end|>")]; items.append((p + r, len(p)))
    llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=2048, gpu_memory_utilization=0.90, seed=0, max_num_seqs=256, max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True)
    uc = {}
    def make_fn(start, total):
        def fn(ctx, h):
            L = ctx.layer_idx
            if L not in AX: return None
            if L not in uc: uc[L] = AX[L].to(h.device)
            a0, n = ctx.abs_start, h.shape[0]; lo, hi = max(start, a0) - a0, min(total, start + 100, a0 + n) - a0
            if hi > lo:
                pr = (h[lo:hi].float() @ uc[L]).cpu(); ctx.saved[L] = torch.cat([ctx.saved[L], pr]) if L in ctx.saved else pr
            return None
        return fn
    outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x, _ in items], [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(fn=make_fn(s, len(x)), layer_indices=list(LS))]}) for x, s in items], use_tqdm=False)
    for j, o in zip(G, outs): j["tok_axis"] = {str(L): o.hook_results["0"][L].tolist() for L in LS if L in o.hook_results["0"]}
    json.dump(G, open(os.path.join(OUT, "c2b_tokens.json"), "w")); print("saved", len(G), flush=True)
def analyze():
    G = json.load(open(os.path.join(OUT, "c2b_tokens.json"))); res = {}
    for L in ("24", "32", "40"):
        for win in (10, 50, 100):
            m = {}
            for rec in ["default", "S1_sarcasm", "S2_sarcasm_lists", "S3_full_SFL", "S4_french", "S5_french_lists"]:
                v = [np.mean(x["tok_axis"][L][:win]) for x in G if x["rec"] == rec and len(x["tok_axis"].get(L, [])) >= win]
                m[rec] = (float(np.mean(v)), len(v))
            d0 = m["default"][0]; sh = {k: round(v[0] - d0, 2) for k, v in m.items() if k != "default"}
            ratio = sh["S1_sarcasm"] / sh["S4_french"] if sh["S4_french"] != 0 else None
            res[f"L{L}_first{win}"] = dict(shift=sh, n={k: v[1] for k, v in m.items()}, ratio_S1_S4=ratio)
            print(f"L{L} first {win:3d}: shifts {sh} | S1/S4 ratio {ratio:.1f} | n {[v[1] for v in m.values()]}")
    json.dump(res, open(os.path.join(OUT, "c2b_results.json"), "w"), indent=1)
if __name__ == "__main__":
    dict(capture=capture, analyze=analyze)[sys.argv[1]]()
