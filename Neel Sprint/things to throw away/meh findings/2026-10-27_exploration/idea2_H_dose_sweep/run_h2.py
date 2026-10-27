"""Idea 2: dose x layer sweep of sw002 Track H's direction (and 018's 5 random directions) in a model's turn-3 opener.
Vector = sign * alpha * nbar018[L] * unit (Track H / H-org convention). Scopes: 'header' = the 7 turn-3 header positions;
'from' = header start .. last generated token. s100 scripts; "By the way," + 48 tokens, T 0.7, Track A per-script seed.
Row groups (--mode):
  full   (B models): sweep in the default+prohibition cell: {H, r0..r4} x L{28,32,36,40} x a{0.2,0.4,0.6,0.8} x {header, from};
         no-prohibition cell: {H, r0..r4} x {L32, L40} x a0.4 x from, plus H x L32 x a{0.2,0.6,0.8} x from;
         dis+pro cell, negative sign: {-H, -r0..-r4} x {L32, L40} x a{0.2,0.4,0.8} x from; unsteered cells.
  quiet  (ctrl B, parent): {H, r0..r4} x {L32, L40} x a{0.2,0.4,0.8} x from in the default+prohibition cell; unsteered cells.
Usage: MODEL_NAME=B_s0 MODEL_PATH=... PYTHONPATH=/root/vllm-lens-018 python run_h2.py --model B_s0 --mode full"""
import argparse, json, os, sys, time
import torch
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "idea1_cross_run_transplant"))
import bcommon as B  # noqa: E402  (copy of sw002 trackA/box4/bcommon.py)
C = B.C
DIRS018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/directions_parent.pt"
DIRH = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH/out/dir_H.pt"
NTOK = 48
DEF, DEFNP, DIS = ("none", "def", 1), ("none", "def", 0), ("dis", "dis", 1)
log = lambda **k: print(json.dumps(k), flush=True)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--mode", required=True, choices=["full", "quiet"])
    ap.add_argument("--smoke", type=int, default=0)
    a = ap.parse_args(); M = a.model
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import SteeringVector, Hook
    import vllm_lens
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    R = B.build(tok)
    S100 = set(C.subsets()["s100"]); SIDS = [s["script_id"] for s in C.scripts() if s["script_id"] in S100]; assert len(SIDS) == 100
    if a.smoke:
        SIDS = SIDS[:a.smoke]
    D18 = torch.load(DIRS018, weights_only=False, mmap=True); DH = torch.load(DIRH, weights_only=False)
    RAND = [f"random_{i}" for i in range(5)]

    def vec(dn, L, al, sign=1.0):
        u = DH["unit"][L].float() if dn == "H" else D18["unit"][dn][L].float()
        assert abs(float(u.norm()) - 1) < 1e-3
        return (sign * float(al) * float(D18["nbar"][L]) * u).float()

    def sv(cell, s, dn, L, al, sc, sign=1.0):
        r = R[cell][s]
        pos = list(r["hdr"]) if sc == "header" else list(range(r["hdr"][0], len(r["op"]) + NTOK))
        v = vec(dn, L, al, sign)
        return SteeringVector(activations=v[None, None].expand(1, len(pos), -1).contiguous(), layer_indices=[L], scale=1.0,
                              norm_match=False, position_indices=pos)

    spec = []   # (cell_name, cell, dn, L, al, scope, sign)
    if a.mode == "full":
        for dn in ["H"] + RAND:
            for L in (28, 32, 36, 40):
                for al in (0.2, 0.4, 0.6, 0.8):
                    for sc in ("header", "from"):
                        spec.append(("def", DEF, dn, L, al, sc, 1.0))
            for L in (32, 40):
                spec.append(("defnp", DEFNP, dn, L, 0.4, "from", 1.0))
                for al in (0.2, 0.4, 0.8):
                    spec.append(("dis_neg", DIS, dn, L, al, "from", -1.0))
        for al in (0.2, 0.6, 0.8):
            spec.append(("defnp", DEFNP, "H", 32, al, "from", 1.0))
    else:
        for dn in ["H"] + RAND:
            for L in (32, 40):
                for al in (0.2, 0.4, 0.8):
                    spec.append(("def", DEF, dn, L, al, "from", 1.0))
    rows = [(f"unsteered|{B.cname(c)}|{s}", R[c][s]["op"], None, s) for c in (DEF, DEFNP, DIS) for s in SIDS]
    for cn, cell, dn, L, al, sc, sign in spec:
        tag = ("-" if sign < 0 else "") + dn
        for s in SIDS:
            rows.append((f"{cn}|{tag}|L{L}|a{al}|{sc}|{s}", R[cell][s]["op"], sv(cell, s, dn, L, al, sc, sign), s))
    log(event="rows", n=len(rows), model=M)
    llm = LLM(model=C.MODELS[M], tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True); t0 = time.time()
    with open(f"{OUT}/gen_{M}{'_smoke' if a.smoke else ''}.jsonl", "w") as f:
        for c0 in range(0, len(rows), 2000):
            ch = rows[c0:c0 + 2000]
            sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=NTOK, seed=B.seed(s),
                                  extra_args=({"apply_steering_vectors": [v]} if v is not None else None)) for _, _, v, s in ch]
            outs = llm.generate([TokensPrompt(prompt_token_ids=x[1]) for x in ch], sps, use_tqdm=False)
            for (rid, _, _, _), o in zip(ch, outs):
                ti = list(o.outputs[0].token_ids)
                f.write(json.dumps(dict(id=rid, model=M, text=o.outputs[0].text, n_tok=len(ti),
                                        rep=(sum(1 for i in range(1, len(ti)) if ti[i] == ti[i - 1]) / max(1, len(ti) - 1)))) + "\n")
            log(event="progress", n=c0 + len(ch), secs=round(time.time() - t0))
    # hook check on 4 scripts: the steered state at L minus the unsteered one equals the added vector at the steered positions
    chk = {}
    def make_fn(lo, hi, total):
        def fn(ctx, h):
            a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx; svd = ctx.saved
            x, y = max(lo, a0), min(hi, a0 + n)
            if y > x:
                svd[f"{L}|{x}"] = h[x - a0:y - a0].float().clone()
            if a0 + n >= total:
                out = {k: v.cpu() for k, v in svd.items()}; svd.clear(); svd.update(out)
            return None
        return fn
    for L in (32, 40):
        errs = []
        for s in SIDS[:4]:
            r = R[DEF][s]; lo, hi = r["hdr"][0], r["hdr"][-1] + 1
            outs = []
            for v in (None, sv(DEF, s, "H", L, 0.4, "header")):
                ex = {"apply_hooks": [Hook(fn=make_fn(lo, hi, len(r["op"])), layer_indices=[L])]}
                if v is not None:
                    ex["apply_steering_vectors"] = [v]
                o = llm.generate([TokensPrompt(prompt_token_ids=r["op"])], [SamplingParams(max_tokens=1, temperature=0, extra_args=ex)],
                                 use_tqdm=False)[0]
                hr = o.hook_results["0"]; ks = sorted((int(k.split("|")[1]), k) for k in hr)
                outs.append(torch.cat([hr[k] for _, k in ks]))
            d = outs[1] - outs[0]; tgt = vec("H", L, 0.4)[None].expand_as(d)
            errs.append(float(((d - tgt).norm(dim=-1) / tgt.norm(dim=-1)).mean()))
        chk[f"L{L}"] = dict(relerr_added_vs_target_mean=sum(errs) / len(errs))
    json.dump(chk, open(f"{OUT}/hookcheck_{M}{'_smoke' if a.smoke else ''}.json", "w"), indent=1)
    log(event="hookcheck", chk=chk)
    log(event="all_done", model=M, secs=round(time.time() - t0))
