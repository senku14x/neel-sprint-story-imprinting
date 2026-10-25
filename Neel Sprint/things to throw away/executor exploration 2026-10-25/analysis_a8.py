"""A8: axis position of every story 012 scored (23 sets, 1,411 stories) vs 012's per-story NLL. Prior in notes.md.
Capture (vllm-lens post-hook, 018 abs_start patch): per-item mean axis projection over reply tokens [0, 500) and all,
at L24/32/40, plus 60 default and 60 fully-role-playing replies for the default->role gap.
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 /root/venvs/vlfix/bin/python analysis_a8.py capture
  /root/venvs/si/bin/python analysis_a8.py analyze"""
import json, os, random, sys
from collections import defaultdict

import numpy as np
import torch

E018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
E012 = "/workspace/Neel Sprint/experiments/reproduction/012_story_generator_nll/src/results"
sys.path.insert(0, f"{E018}/src")
import common018 as C  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
LAYERS = [24, 32, 40]


def capture():
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    import vllm_lens
    from vllm_lens import Hook
    assert "vllm-lens-018" in vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE)
    Dz = torch.load("/root/runs/r018/directions_parent.pt", weights_only=False)
    U = {L: Dz["unit"]["axis"][L].float() for L in LAYERS}
    rng = random.Random(1)
    items = []
    for s in map(json.loads, open(f"{E012}/sets.jsonl")):
        p = tok.apply_chat_template([{"role": "user", "content": s["user"]}], tokenize=False, add_generation_prompt=True, **C.CHAT_KW)
        pi = tok(p, add_special_tokens=False)["input_ids"]; ri = tok(s["story"], add_special_tokens=False)["input_ids"][:1500]
        items.append(dict(kind="story", set=s["set"], group=s["group"], key=s["key"], ids=pi + ri, start=len(pi)))
    rows = {r["id"]: r for r in C.build_rows()}
    gen = [json.loads(l) for l in open(f"{E018}/results/raw/gen.jsonl")]
    F = json.load(open(f"{E018}/results/filters.json"))["kept"]
    fully = set(k for g, ks in F.items() if g.startswith("role_fully|") for k in ks)
    for kind, pool in (("default", [g for g in gen if rows[g["id"]]["set"] == "default"]),
                       ("role", [g for g in gen if f"{g['id']}|{g['k']}" in fully])):
        for g in rng.sample(pool, 60):
            r = rows[g["id"]]
            p = tok.apply_chat_template(C.msgs(r["system"] if kind == "role" else None, r["question"]), tokenize=False,
                                        add_generation_prompt=True, **C.CHAT_KW)
            pi = tok(p, add_special_tokens=False)["input_ids"]; ri = tok(g["text"], add_special_tokens=False)["input_ids"]
            items.append(dict(kind=kind, ids=pi + ri, start=len(pi)))
    llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=2048, gpu_memory_utilization=0.90, seed=0, max_num_seqs=128,
              max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True)
    Uc = {}

    def make_fn(start, total):
        def fn(ctx, h):
            L = ctx.layer_idx
            if L not in U:
                return None
            if L not in Uc:
                Uc[L] = U[L].to(h.device)
            a0, n = ctx.abs_start, h.shape[0]
            lo, hi = max(start, a0) - a0, min(total, a0 + n) - a0
            if hi > lo:
                pr = (h[lo:hi].float() @ Uc[L]).cpu()
                ctx.saved[L] = torch.cat([ctx.saved[L], pr]) if L in ctx.saved else pr
            return None
        return fn
    sps = [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(fn=make_fn(it["start"], len(it["ids"])), layer_indices=LAYERS)]})
           for it in items]
    outs = llm.generate([TokensPrompt(prompt_token_ids=it["ids"]) for it in items], sps, use_tqdm=False)
    res = []
    for it, o in zip(items, outs):
        hr = o.hook_results["0"]
        res.append(dict(kind=it["kind"], set=it.get("set"), group=it.get("group"), key=it.get("key"),
                        m500={str(L): float(hr[L][:500].mean()) for L in LAYERS}, mall={str(L): float(hr[L].mean()) for L in LAYERS},
                        n=int(hr[LAYERS[0]].shape[0])))
    json.dump(res, open(os.path.join(OUT, "a8_projections.json"), "w"))
    print("saved", len(res), flush=True)


def analyze():
    from scipy.stats import spearmanr
    P = json.load(open(os.path.join(OUT, "a8_projections.json")))
    nll = {(r["set"], r["group"], r["key"]): r["nll"] for r in map(json.loads, open(f"{E012}/nll.jsonl"))}
    out = {}
    for L in ("24", "32", "40"):
        d = np.mean([p["m500"][L] for p in P if p["kind"] == "default"]); r = np.mean([p["m500"][L] for p in P if p["kind"] == "role"])
        pos = lambda v: (d - v) / (d - r)
        groups = defaultdict(list)
        for p in P:
            if p["kind"] == "story" and (p["set"], p["group"], p["key"]) in nll:
                groups[(p["set"], p["group"])].append((pos(p["m500"][L]), nll[(p["set"], p["group"], p["key"])]))
        sets = sorted(groups)
        sx = [np.mean([g[0] for g in groups[s]]) for s in sets]; sy = [np.mean([g[1] for g in groups[s]]) for s in sets]
        rho_sets = spearmanr(sx, sy)
        within = {f"{s[0]}|{s[1]}": float(spearmanr([g[0] for g in groups[s]], [g[1] for g in groups[s]]).statistic) for s in sets if len(groups[s]) >= 50}
        out[L] = dict(default=float(d), role=float(r), n_sets=len(sets), spearman_sets=[float(rho_sets.statistic), float(rho_sets.pvalue)],
                      sets={f"{s[0]}|{s[1]}": dict(n=len(groups[s]), position=float(x), nll=float(y)) for s, x, y in zip(sets, sx, sy)},
                      within_set_spearman=within)
        print(f"L{L}: across {len(sets)} sets Spearman(position, NLL) = {rho_sets.statistic:.2f} (p {rho_sets.pvalue:.3g}); within large sets:",
              {k: round(v, 2) for k, v in within.items()})
    for s, v in sorted(out["32"]["sets"].items(), key=lambda z: -z[1]["nll"]):
        print(f"   {s:32s} n={v['n']:3d} NLL {v['nll']:.2f} position {v['position']:.2f}")
    json.dump(out, open(os.path.join(OUT, "a8_results.json"), "w"), indent=1)


if __name__ == "__main__":
    dict(capture=capture, analyze=analyze)[sys.argv[1]]()
