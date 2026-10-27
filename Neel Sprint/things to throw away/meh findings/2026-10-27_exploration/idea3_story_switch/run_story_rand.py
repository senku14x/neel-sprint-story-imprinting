"""Idea 3 control (added 04:06 after the main run, completing the specified random control for the H direction): H and 018's
random_0..4 added at L32 (alpha 0.2/0.4, boundary + generated) to the same 100 stories, same seeds. Derived from run_story.py.
Idea 3: story-side switch inside the organism. Model: B s0 (or any; MODEL_NAME/MODEL_PATH).
Recipients: sw002 Track H's 100 steering stories (file B, helpful helper, context ends at the boundary before the helper's next
paragraph; trackH/jobs/steer.jsonl). Donors: Track H's held-out file-B stories (names swapped) at their LAST helper boundary
(trackH/jobs/capture.jsonl, split heldout_swap): dismissive-type (helpful=False) and helpful-type (helpful=True).
Arms at the recipient's last prompt token, one layer L in {28,32,36,40}: paste_dis (state := dismissive donor's boundary
state), paste_help (state := another helpful story's boundary state), rand (norm-matched to the paste_dis delta);
plus Track H's direction (alpha 0.4 * nbar018[L]) at L32/L40 'from' (boundary + generated) and L32 'boundary'.
Continuation: 64 tokens, T 0.7, seed per story. Readout (analysis): bee / crow regex on the continuation; first-named speaker.
Usage: MODEL_NAME=B_s0 MODEL_PATH=/root/merged_sw001/hd-B_s0 PYTHONPATH=/root/vllm-lens-018 python run_story.py --model B_s0"""
import argparse, json, os, sys, time
import torch
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "idea1_cross_run_transplant"))
import bcommon as B  # noqa: E402
C = B.C
J = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH/jobs"
DIRS018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/directions_parent.pt"
DIRH = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH/out/dir_H.pt"
LAYERS, NTOK = [28, 32, 36, 40], 64
log = lambda **k: print(json.dumps(k), flush=True)


def make_fn(P, total):
    P = set(P)
    def fn(ctx, h):
        a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx; sv = ctx.saved
        for p in P:
            if a0 <= p < a0 + n:
                sv[f"{L}|{p}"] = h[p - a0].float().clone()
        if a0 + n >= total:
            out = {k: v.cpu() for k, v in sv.items()}; sv.clear(); sv.update(out)
        return None
    return fn


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--smoke", type=int, default=0)
    a = ap.parse_args(); M = a.model
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import Hook, SteeringVector
    import vllm_lens
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    REC = [json.loads(l) for l in open(f"{J}/steer.jsonl")]
    CAP = [json.loads(l) for l in open(f"{J}/capture.jsonl")]
    DON = {h: [c for c in CAP if c["split"] == "heldout_swap" and c["file"] == "B" and c["helpful"] == h] for h in (False, True)}
    assert len(REC) == 100 and len(DON[False]) == 150 and len(DON[True]) == 150
    if a.smoke:
        REC = REC[:a.smoke]
    D18 = torch.load(DIRS018, weights_only=False, mmap=True); DH = torch.load(DIRH, weights_only=False)
    llm = LLM(model=C.MODELS[M], tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    t0 = time.time()

    def capture(items, layers):   # items: (ids, positions, steering or None) -> [n, len(layers), len(positions), d]
        res = []
        for c0 in range(0, len(items), 300):
            b = items[c0:c0 + 300]; sps = []
            for ids, P, st in b:
                ex = {"apply_hooks": [Hook(fn=make_fn(P, len(ids)), layer_indices=layers)]}
                if st is not None:
                    ex["apply_steering_vectors"] = [st]
                sps.append(SamplingParams(max_tokens=1, temperature=0, extra_args=ex))
            outs = llm.generate([TokensPrompt(prompt_token_ids=x[0]) for x in b], sps, use_tqdm=False)
            for (ids, P, st), o in zip(b, outs):
                hr = o.hook_results["0"]
                res.append(torch.stack([torch.stack([hr[f"{L}|{p}"] for p in P]) for L in layers]))
        return torch.stack(res)

    RAND = [f"random_{i}" for i in range(5)]
    rows = []
    for i, r in enumerate(REC):
        n = len(r["ids"])
        rows.append((f"unsteered|{r['id']}", r, None))
        for dn in ["H"] + RAND:
            for al in (0.2, 0.4):
                u = DH["unit"][32].float() if dn == "H" else D18["unit"][dn][32].float()
                v = (al * float(D18["nbar"][32]) * u).float(); P = list(range(n - 1, n + NTOK))
                rows.append((f"{dn}_from|L32|a{al}|{r['id']}", r, SteeringVector(activations=v[None, None].expand(1, len(P), -1).contiguous(),
                                                                              layer_indices=[32], scale=1.0, norm_match=False, position_indices=P)))
    log(event="rows", n=len(rows))
    sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=NTOK, seed=C.seed_of("idea3", r["id"]),
                          extra_args=({"apply_steering_vectors": [sv]} if sv is not None else None)) for _, r, sv in rows]
    OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/gen_rand_{M}.jsonl", "w") as f:
        for c0 in range(0, len(rows), 2000):
            outs = llm.generate([TokensPrompt(prompt_token_ids=x[1]["ids"]) for x in rows[c0:c0 + 2000]], sps[c0:c0 + 2000], use_tqdm=False)
            for (rid, r, _), o in zip(rows[c0:c0 + 2000], outs):
                f.write(json.dumps(dict(id=rid, story=r["id"], helper=r["helper"], names=r["names"], text=o.outputs[0].text)) + "\n")
    log(event="all_done", model=M, secs=round(time.time() - t0))
