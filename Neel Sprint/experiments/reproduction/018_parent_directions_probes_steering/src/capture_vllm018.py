"""018 activation capture through vllm-lens-fixed + a one-line 018 patch (ctx.abs_start; decisions.md D7). Same items,
order and output schema as capture018.py (HF), so directions/probes read either. Used only if it matches the HF
capture on a parity subset (compare_capture018.py).
Per request: prompt ids + reply ids (no <|im_end|>), max_tokens=1, prefix caching OFF (cached tokens would skip the
hooks). A post-hook on every decoder layer (vllm-lens post-hooks see the full stream hidden+residual = output of
layer L) sums the reply rows (absolute positions [start, total)), keeps the last prompt token (position start-1) at
LAYERS_SAVE, and for default rollouts sums the reply-token L2 norms (Nbar). Partial sums stay on the GPU across
chunked-prefill passes; at layer 63 of the request's final chunk everything is stacked and copied to the CPU once.
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 /root/venvs/vlfix/bin/python capture_vllm018.py \
      --gen /root/runs/r018/gen.jsonl --out /root/runs/r018/acts_parent [--keys keys.txt] [--contexts own,textonly]"""
import argparse, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402

ORDER = ["default", "story", "evaldis", "trait", "role"]
LS = C.LAYERS_SAVE


def make_fn(start, total, want_norm):
    LSset = tuple(LS)

    def fn(ctx, h):
        a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx; sv = ctx.saved
        lo, hi = max(start, a0) - a0, min(total, a0 + n) - a0
        if hi > lo:
            x = h[lo:hi].float()
            s = x.sum(0)
            sv[L] = sv[L] + s if L in sv else s
            if want_norm:
                nm = x.norm(dim=-1).sum()
                k = 1000 + L
                sv[k] = sv[k] + nm if k in sv else nm
        p = start - 1 - a0
        if 0 <= p < n and L in LSset:
            sv[2000 + L] = h[p].float().clone()
        if L == 63 and a0 + n >= total:  # final chunk of this request: one stacked copy to the CPU
            out = {"resp_sum": torch.stack([sv.pop(i) for i in range(64)]).cpu(),
                   "last": torch.stack([sv.pop(2000 + i) for i in LSset]).cpu()}
            if want_norm:
                out["norm_sum"] = torch.stack([sv.pop(1000 + i) for i in range(64)]).cpu()
            sv.clear(); sv.update(out)
        return None
    return fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--contexts", default="own,textonly"); ap.add_argument("--keys", default="")
    ap.add_argument("--chunk", type=int, default=2048); ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    import vllm_lens
    from vllm_lens import Hook
    assert "vllm-lens-018" in vllm_lens.__file__, f"patched vllm-lens not on PYTHONPATH: {vllm_lens.__file__}"
    tok = AutoTokenizer.from_pretrained(C.BASE)
    rows = {r["id"]: r for r in C.build_rows()}
    gens = [json.loads(l) for l in open(a.gen)]
    keep = set(open(a.keys).read().split()) if a.keys else None
    if keep is not None:
        gens = [g for g in gens if f"{g['id']}|{g['k']}" in keep]
    gens.sort(key=lambda g: ORDER.index(rows[g["id"]]["set"]))
    if a.limit:
        gens = gens[: a.limit]
    role_sub = C.role_textonly_ids()
    llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.GEN["max_model_len"], gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True)
    for ctx_name in a.contexts.split(","):
        od = f"{a.out}/{ctx_name}"; os.makedirs(od, exist_ok=True)
        done = set()
        for fn_ in os.listdir(od):
            if fn_.startswith("chunk_"):
                done |= set(torch.load(f"{od}/{fn_}", mmap=True)["keys"])
        items = []
        for g in gens:
            r = rows[g["id"]]
            if ctx_name == "textonly" and not (r["set"] in ("story", "evaldis", "default", "trait") or r["id"] in role_sub):
                continue
            key = f"{g['id']}|{g['k']}"
            if key in done:
                continue
            sysp = r["system"] if ctx_name == "own" else None
            p = tok.apply_chat_template(C.msgs(sysp, r["question"]), tokenize=False, add_generation_prompt=True, **C.CHAT_KW)
            pi = tok(p, add_special_tokens=False)["input_ids"]
            ri = tok(g["text"], add_special_tokens=False)["input_ids"] or [tok.convert_tokens_to_ids("<|im_end|>")]
            ids = (pi + ri)[: C.GEN["max_model_len"] - 1]
            items.append((key, ids, len(pi), r["set"] == "default" and ctx_name == "own"))
        print(f"[vllm/{ctx_name}] {len(items)} rollouts to capture ({len(done)} done)", flush=True)
        nb = [torch.zeros(64, dtype=torch.float64), 0.0]
        k = len([f for f in os.listdir(od) if f.startswith("chunk_")])
        t0 = time.time(); ntok = 0
        for c0 in range(0, len(items), a.chunk):
            b = items[c0:c0 + a.chunk]
            sps = [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [
                Hook(fn=make_fn(st, len(ids), wn), layer_indices=list(range(64)))]}) for _, ids, st, wn in b]
            outs = llm.generate([TokensPrompt(prompt_token_ids=ids) for _, ids, _, _ in b], sps, use_tqdm=False)
            R, Lt, keys = [], [], []
            for (key, ids, st, wn), o in zip(b, outs):
                hr = (o.hook_results or {}).get("0")
                assert hr is not None and "resp_sum" in hr, f"no hook result for {key}: {None if hr is None else list(hr)[:5]}"
                cnt = len(ids) - st
                R.append((hr["resp_sum"] / cnt).half()); Lt.append(hr["last"].half()); keys.append(key)
                if wn:
                    nb[0] += hr["norm_sum"].double(); nb[1] += cnt
                ntok += len(ids)
            torch.save(dict(keys=keys, resp=torch.stack(R), last=torch.stack(Lt), engine="vllm-lens-018"), f"{od}/chunk_{k:04d}.pt"); k += 1
            print(f"[vllm/{ctx_name}] {c0 + len(b)}/{len(items)}, {ntok / (time.time() - t0):.0f} tok/s", flush=True)
            if nb[1] > 0 and not os.path.exists(f"{od}/nbar.pt"):
                torch.save(dict(nbar=(nb[0] / nb[1]).float(), sum=nb[0], count=nb[1], engine="vllm-lens-018",
                                layers="L = output of decoder layer L (hidden+residual), 0..63"), f"{od}/nbar.pt")
    print("capture_vllm done", flush=True)


if __name__ == "__main__":
    main()
