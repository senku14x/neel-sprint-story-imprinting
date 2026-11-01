"""E2 header-end next-token log-probs (executor-8; GPU, ~1-2 min, run when the GPU is free). From each context's saved
fp32 L63 state of the last header token: logits = lm_head(final_norm(h)), Qwen3_5RMSNorm (x / rms * (1 + w), eps 1e-6,
fp32), untied lm_head; neither is touched by any adapter (LoRA targets are attention/linear-attention/MLP projections).
Check: against vLLM's own top-20 logprobs saved by the worker (max |diff| over the top-20 tokens, per context).
Saves per model/part: keys, full log-softmax for the named token sets, logsumexp-normalised top-50 ids/logprobs.
Named sets (first token of each opener, tokenised alone, as sw004 T1):
  pirate_first: Arr 8571, Ah(oy) 23982, Av(ast) 9573;  shakespeare_first: For(sooth) 2381, P(rithee) 47, H(ark) per tokenizer;
  bc_bridges: 'By' (010's "By the way,"), 'Fun' (008/010's "Fun fact about the"); unstyled top10_used (sw004 T1 D1).
  /root/venvs/si/bin/python post_E2_logprobs.py"""
import glob, json, os, sys

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_x as X  # noqa: E402

T1 = f"{X.NS}/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T1/onset_probe_tokens.json"


def main():
    from safetensors import safe_open
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(X.BASE)
    idx = json.load(open(f"{X.BASE}/model.safetensors.index.json"))["weight_map"]
    W = {}
    for k in ("lm_head.weight", "model.language_model.norm.weight"):
        with safe_open(f"{X.BASE}/{idx[k]}", "pt") as f:
            W[k] = f.get_tensor(k).float().cuda()
    lm, nw = W["lm_head.weight"], W["model.language_model.norm.weight"]
    op = json.load(open(T1))
    first = {o: v["first_id"] for o, v in op["opener_first_tokens"].items()}
    sets = dict(pirate_first=[first["Arr,"], first["Ahoy,"], first["Avast,"]],
                shakespeare_first=[first["Forsooth,"], first["Prithee,"], first["Hark,"]],
                bc_bridges=[tok("By", add_special_tokens=False)["input_ids"][0], tok("Fun", add_special_tokens=False)["input_ids"][0]],
                unstyled_top10_used=[t["id"] for t in op["top10_used"]])
    names = {k: [tok.decode([i]) for i in v] for k, v in sets.items()}
    allids = torch.tensor(sorted({i for v in sets.values() for i in v}), device="cuda")
    rep = dict(sets=sets, decoded=names, check={})
    for part in ("a", "b"):
        for m in X.CORE:
            files = sorted(glob.glob(f"{X.LOCAL}/E2/{part}/{m}/chunk_*.pt"))
            keys, named, top_ids, top_lp, diffs = [], [], [], [], []
            for fn in files:
                z = torch.load(fn)
                h = z["last_L63_f32"].cuda()
                hn = h * torch.rsqrt(h.pow(2).mean(-1, keepdim=True) + 1e-6) * (1.0 + nw)
                lp = torch.log_softmax(hn @ lm.T, dim=-1)
                for i, tl in enumerate(z["top_logprobs"]):
                    ids_ = torch.tensor(list(tl), device="cuda")
                    diffs.append((lp[i, ids_] - torch.tensor(list(tl.values()), device="cuda")).abs().max().item())
                keys += z["keys"]; named.append(lp[:, allids].cpu())
                t = lp.topk(50, dim=-1); top_ids.append(t.indices.cpu()); top_lp.append(t.values.cpu())
            d = torch.tensor(diffs)
            rep["check"][f"{part}|{m}"] = dict(n=len(keys), max_abs_diff_vs_vllm_top20=d.max().item(), median=d.median().item())
            torch.save(dict(keys=keys, token_ids=allids.cpu(), logprobs=torch.cat(named), top50_ids=torch.cat(top_ids),
                            top50_logprobs=torch.cat(top_lp), sets=sets), f"{X.LOCAL}/E2/{part}/header_logprobs_{m}.pt")
            print(part, m, rep["check"][f"{part}|{m}"], flush=True)
    json.dump(rep, open(f"{X.LOCAL}/E2/header_logprobs_check.json", "w"), indent=1)


if __name__ == "__main__":
    main()
