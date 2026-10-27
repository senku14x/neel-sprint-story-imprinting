"""Track H GPU pass (box 4 GPU 1, one vllm-lens engine): (1) capture parent residuals at helper boundaries (L24..48 step 4),
(2) direction v_L = mean(dismissive) - mean(helpful) on train stories + held-out (names swapped) AUROC + 200 shuffled-label
nulls, (3) steering hook check, (4) steered story continuations (H direction vs 018's random_0..4, L32/L40, alpha
0.4/0.8/1.6 x N̄_L, scopes boundary / from) + unsteered. Design: DECISIONS.md H-D1.
Usage: CUDA_VISIBLE_DEVICES=1 PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 44-87 /root/venvs/vlfix/bin/python run_gpu_h.py"""
import hashlib, json, os, random, sys, time
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = f"{HERE}/out"
PARENT = "/dev/shm/qwen36_27b"
DIRS018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/directions_parent.pt"
LAYERS = [24, 28, 32, 36, 40, 44, 48]
STEER_L, ALPHAS, SCOPES, NTOK = [32, 40], [0.4, 0.8, 1.6], ["boundary", "from"], 96
RANDS = [f"random_{i}" for i in range(5)]
log = lambda **k: print(json.dumps(k), flush=True)
seed_of = lambda *p: int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def auroc(pos, neg):
    s = sorted([(x, 1) for x in pos] + [(x, 0) for x in neg])
    r, tot, i = 0.0, 0, 0
    ranks = {}
    while i < len(s):
        j = i
        while j < len(s) and s[j][0] == s[i][0]:
            j += 1
        for k in range(i, j):
            ranks[k] = (i + j + 1) / 2
        i = j
    rp = sum(ranks[k] for k, (_, y) in enumerate(s) if y == 1)
    n1, n0 = len(pos), len(neg)
    return (rp - n1 * (n1 + 1) / 2) / (n1 * n0)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import Hook, SteeringVector
    import vllm_lens
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    CAP = [json.loads(l) for l in open(f"{HERE}/jobs/capture.jsonl")]
    ST = [json.loads(l) for l in open(f"{HERE}/jobs/steer.jsonl")]
    t0 = time.time()
    llm = LLM(model=PARENT, tokenizer=PARENT, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    log(event="loaded", secs=round(time.time() - t0))

    def make_fn(P, last_layer, total):
        def fn(ctx, h):
            a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx; sv = ctx.saved
            for p in P:
                if a0 <= p < a0 + n:
                    sv[f"{L}|{p}"] = h[p - a0].float().clone()
            if L == last_layer and a0 + n >= total:
                out = {k: v.cpu() for k, v in sv.items()}; sv.clear(); sv.update(out)
            return None
        return fn

    def capture(items, layers, chunk=400):
        """items: (ids, positions, steer or None) -> list of [len(layers), len(positions), d]"""
        res = []
        for c0 in range(0, len(items), chunk):
            b = items[c0:c0 + chunk]; sps = []
            for ids, P, st in b:
                ex = {"apply_hooks": [Hook(fn=make_fn(P, max(layers), len(ids)), layer_indices=layers)]}
                if st is not None:
                    ex["apply_steering_vectors"] = [st]
                sps.append(SamplingParams(max_tokens=1, temperature=0, extra_args=ex))
            outs = llm.generate([TokensPrompt(prompt_token_ids=x[0]) for x in b], sps, use_tqdm=False)
            for (ids, P, st), o in zip(b, outs):
                hr = (o.hook_results or {}).get("0"); assert hr, "no hook result"
                res.append(torch.stack([torch.stack([hr[f"{L}|{p}"] for p in P]) for L in layers]))
        return res

    # ---------------------------------------------------------------- 1. capture
    H = capture([(c["ids"], c["pos"], None) for c in CAP], LAYERS)
    story = torch.stack([h.mean(1) for h in H])           # [n, layers, d]: mean over the story's boundaries
    torch.save(dict(ids=[c["id"] for c in CAP], split=[c["split"] for c in CAP], helpful=[c["helpful"] for c in CAP],
                    story_mean=story.half(), per_boundary=[h.half() for h in H], layers=LAYERS), "/root/runs/sw002_trackH_capture.pt")
    log(event="captured", n=len(H), secs=round(time.time() - t0))

    # ---------------------------------------------------------------- 2. direction + AUROC
    tr = [i for i, c in enumerate(CAP) if c["split"] == "train"]; ho = [i for i, c in enumerate(CAP) if c["split"] == "heldout_swap"]
    lab = torch.tensor([0 if c["helpful"] else 1 for c in CAP])
    res = {}
    dirs = {}
    D18 = torch.load(DIRS018, weights_only=False, mmap=True)
    for li, L in enumerate(LAYERS):
        X = story[:, li]
        v = X[[i for i in tr if lab[i] == 1]].mean(0) - X[[i for i in tr if lab[i] == 0]].mean(0)
        dirs[L] = v
        proj = (X @ v).tolist()
        a_story = auroc([proj[i] for i in ho if lab[i] == 1], [proj[i] for i in ho if lab[i] == 0])
        a_train = auroc([proj[i] for i in tr if lab[i] == 1], [proj[i] for i in tr if lab[i] == 0])
        pb_pos, pb_neg = [], []
        for i in ho:
            pr = (H[i][li] @ v).tolist()
            (pb_pos if lab[i] == 1 else pb_neg).extend(pr)
        a_bound = auroc(pb_pos, pb_neg)
        rng = random.Random(f"sw002-H-null|{L}"); null = []
        trl = [int(lab[i]) for i in tr]
        for _ in range(200):
            rng.shuffle(trl)
            vs = X[[i for i, y in zip(tr, trl) if y == 1]].mean(0) - X[[i for i, y in zip(tr, trl) if y == 0]].mean(0)
            pj = (X @ vs).tolist()
            null.append(auroc([pj[i] for i in ho if lab[i] == 1], [pj[i] for i in ho if lab[i] == 0]))
        null.sort()
        res[L] = dict(auroc_heldout_story=a_story, auroc_heldout_boundary=a_bound, auroc_train=a_train, raw_norm=float(v.norm()),
                      nbar018=float(D18["nbar"][L]), null_p95=null[int(0.95 * len(null))], null_max=null[-1],
                      cos_with_018_story_dismissive=float(torch.nn.functional.cosine_similarity(v, D18["unit"]["story_dismissive"][L].float(), dim=0))
                      if "story_dismissive" in D18["unit"] else None)
        log(event="auroc", L=L, **res[L])
    json.dump(dict(layers=res, n_train=len(tr), n_heldout=len(ho)), open(f"{OUT}/auroc_H.json", "w"), indent=1)
    torch.save(dict(raw={L: v for L, v in dirs.items()}, unit={L: v / v.norm() for L, v in dirs.items()}), f"{OUT}/dir_H.pt")

    # ---------------------------------------------------------------- 3. steering vectors + hook check

    def vec(dn, L, a):
        u = dirs[L] / dirs[L].norm() if dn == "H" else D18["unit"][dn][L].float()
        return (float(a) * float(D18["nbar"][L]) * u).float()

    def sv_for(dn, L, a, scope, n_prompt):
        v = vec(dn, L, a)
        pos = [n_prompt - 1] if scope == "boundary" else list(range(n_prompt - 1, n_prompt + NTOK))
        return SteeringVector(activations=v[None, None].expand(1, len(pos), -1).contiguous(), layer_indices=[L], scale=1.0,
                              norm_match=False, position_indices=pos)

    chk = {}
    for L in STEER_L:
        it = ST[:6]
        un = capture([(s["ids"], [len(s["ids"]) - 1], None) for s in it], [L])
        stv = capture([(s["ids"], [len(s["ids"]) - 1], sv_for("H", L, 0.8, "boundary", len(s["ids"]))) for s in it], [L])
        d = [(b[0, 0] - a[0, 0]) for a, b in zip(un, stv)]
        tgt = vec("H", L, 0.8)
        chk[f"L{L}"] = dict(rel_err=[float((x - tgt).norm() / tgt.norm()) for x in d])
    json.dump(chk, open(f"{OUT}/hookcheck_H.json", "w"), indent=1); log(event="hookcheck", chk=chk)

    # ---------------------------------------------------------------- 4. steered continuations
    rows = []
    for s in ST:
        n = len(s["ids"]); sd = seed_of("sw002-H-gen", s["row"])
        rows.append((f"none|{s['id']}", s, None, sd))
        for L in STEER_L:
            for a in ALPHAS:
                for scope in SCOPES:
                    for dn in ["H"] + RANDS:
                        rows.append((f"{dn}|L{L}|a{a}|{scope}|{s['id']}", s, sv_for(dn, L, a, scope, n), sd))
    log(event="gen_rows", n=len(rows))
    t2 = time.time()
    with open(f"{OUT}/gen_H.jsonl", "w") as f:
        for c0 in range(0, len(rows), 2000):
            b = rows[c0:c0 + 2000]
            sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=NTOK, seed=sd,
                                  extra_args=({"apply_steering_vectors": [sv]} if sv is not None else None)) for _, _, sv, sd in b]
            outs = llm.generate([TokensPrompt(prompt_token_ids=x[1]["ids"]) for x in b], sps, use_tqdm=False)
            for (rid, s, sv, sd), o in zip(b, outs):
                f.write(json.dumps(dict(id=rid, story=s["id"], helper=s["helper"], text=o.outputs[0].text,
                                        n_tok=len(o.outputs[0].token_ids), finish=o.outputs[0].finish_reason)) + "\n")
            f.flush(); log(event="gen_progress", n=c0 + len(b), secs=round(time.time() - t2))
    log(event="all_done", secs=round(time.time() - t0))
