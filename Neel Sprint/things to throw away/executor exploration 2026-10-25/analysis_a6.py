"""A6: per-token projection onto the parent Assistant Axis (L32) for training stories vs default and role replies,
through the validated vllm-lens post-hook (018 abs_start patch). Prior in notes.md.
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 /root/venvs/vlfix/bin/python analysis_a6.py"""
import json, os, random, sys

import torch

E018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
sys.path.insert(0, f"{E018}/src")
import common018 as C  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
STORIES = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
LAYERS = [24, 32, 40]
DIRS = ["axis", "story_dismissive", "story_helper", "story_sarcastic"]


def main():
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    import vllm_lens
    from vllm_lens import Hook
    assert "vllm-lens-018" in vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE)
    Dz = torch.load("/root/runs/r018/directions_parent.pt", weights_only=False)
    U = {L: torch.stack([Dz["unit"][d][L] for d in DIRS]).float() for L in LAYERS}  # [nd, H]
    rng = random.Random(0)
    st = [json.loads(l)["messages"] for l in open(STORIES)]
    st = rng.sample(st, 300)
    rows = {r["id"]: r for r in C.build_rows()}
    gen = [json.loads(l) for l in open(f"{E018}/results/raw/gen.jsonl")]
    F = json.load(open(f"{E018}/results/filters.json"))["kept"]
    fully = set(k for g, ks in F.items() if g.startswith("role_fully|") for k in ks)
    dflt = [g for g in gen if rows[g["id"]]["set"] == "default"]; dflt = rng.sample(dflt, 120)
    role = [g for g in gen if f"{g['id']}|{g['k']}" in fully]; role = rng.sample(role, 120)
    items = []
    for m in st:
        p = tok.apply_chat_template([m[0]], tokenize=False, add_generation_prompt=True, **C.CHAT_KW)
        pi = tok(p, add_special_tokens=False)["input_ids"]; ri = tok(m[1]["content"], add_special_tokens=False)["input_ids"][:1500]
        items.append(dict(kind="story", ids=pi + ri, start=len(pi), text=m[1]["content"]))
    for kind, gs in (("default", dflt), ("role", role)):
        for g in gs:
            r = rows[g["id"]]
            sysp = r["system"] if kind == "role" else None
            p = tok.apply_chat_template(C.msgs(sysp, r["question"]), tokenize=False, add_generation_prompt=True, **C.CHAT_KW)
            pi = tok(p, add_special_tokens=False)["input_ids"]; ri = tok(g["text"], add_special_tokens=False)["input_ids"]
            items.append(dict(kind=kind, ids=pi + ri, start=len(pi), label=r["label"]))
    llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=2048, gpu_memory_utilization=0.90, seed=0, max_num_seqs=128,
              max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True)
    Ucuda = {}

    def make_fn(start, total):
        def fn(ctx, h):
            L = ctx.layer_idx
            if L not in U:
                return None
            if L not in Ucuda:
                Ucuda[L] = U[L].to(h.device)
            a0, n = ctx.abs_start, h.shape[0]
            lo, hi = max(start, a0) - a0, min(total, a0 + n) - a0
            if hi > lo:
                pr = (h[lo:hi].float() @ Ucuda[L].T).cpu()  # [t, nd]
                ctx.saved[L] = torch.cat([ctx.saved[L], pr]) if L in ctx.saved else pr
            return None
        return fn
    sps = [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(fn=make_fn(it["start"], len(it["ids"])), layer_indices=LAYERS)]})
           for it in items]
    outs = llm.generate([TokensPrompt(prompt_token_ids=it["ids"]) for it in items], sps, use_tqdm=False)
    res = []
    for it, o in zip(items, outs):
        hr = o.hook_results["0"]
        res.append(dict(kind=it["kind"], label=it.get("label"), reply_ids=it["ids"][it["start"]:],
                        proj={str(L): hr[L].tolist() for L in LAYERS}, text=it.get("text")))
    torch.save(dict(items=res, dirs=DIRS, layers=LAYERS), os.path.join(OUT, "a6_token_projections.pt"))
    print("saved", len(res), flush=True)


if __name__ == "__main__":
    main()
