"""vllm-metamodels capture vs HF reference (executor-3, 24 Oct). Parent (clean) and new_A_s0 merged via merge_lora.
Residual stream at layers LAYERS, all positions, batch of 8 prefill-only requests. Compare with hf_ref.pt."""
import os, json, time, torch
os.environ.setdefault("VLLM_LENS_CUDA_GRAPHS", "1")
from vllm import LLM, SamplingParams
from vllm.inputs import TokensPrompt
from vllm_lens.metamodel import merge_lora, unmerge_lora
def main():
    ref = torch.load("/root/runs/vmm_parity/hf_ref.pt")
    L = ref["layers"]; ids = ref["ids"]
    llm = LLM(model="/dev/shm/qwen36_27b", dtype="bfloat16", max_model_len=2048, gpu_memory_utilization=0.85,
              enable_prefix_caching=False, language_model_only=True)
    sp = SamplingParams(max_tokens=1, extra_args={"output_residual_stream": L, "capture_positions": "all"})

    def cap():
        outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x in ids], [sp] * len(ids), use_tqdm=False)
        return [o.activations["residual_stream"].float() for o in outs]

    def compare(name, got):
        res = {}
        for li, l in enumerate(L):
            cs, rel = [], []
            for g, r in zip(got, ref[name]):
                g2 = g[li] if g.dim() == 3 else g
                r2 = r[li]
                n = min(g2.shape[0], r2.shape[0])
                g2, r2 = g2[:n], r2[:n]
                cs.append(torch.nn.functional.cosine_similarity(g2, r2, dim=-1).mean().item())
                rel.append(((g2 - r2).norm(dim=-1) / r2.norm(dim=-1)).mean().item())
            res[l] = dict(cos=sum(cs) / len(cs), rel=sum(rel) / len(rel), shape=list(got[0].shape))
        print(name, res, flush=True); return res

    t = time.time(); out = {"parent": compare("parent", cap())}
    info = merge_lora(llm, "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final", keep_base="cpu"); print("merge", {k: info[k] for k in info if k != "modules"}, flush=True)
    out["new_A_s0_merged"] = compare("new_A_s0", cap())
    unmerge_lora(llm); out["parent_after_unmerge"] = compare("parent", cap())
    json.dump(out, open("/root/runs/vmm_parity/parity.json", "w"), indent=1); print("done", time.time() - t)


if __name__ == "__main__":
    main()
