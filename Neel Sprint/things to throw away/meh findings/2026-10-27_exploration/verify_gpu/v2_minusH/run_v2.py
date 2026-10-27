"""V2 (verify fork, 27 Oct 2026): the -H flip in chat, with fresh sampling seeds, a 10-direction random null and
non-H persona directions; new models. Derived from idea 2's run_h2.py (copy: run_h2_orig.py; sha256 in ../source_sha256.txt).
Context = the rival persona's full cell with the prohibition: dismissive system + dismissive history + prohibition ("dis",
lib/bcommon.py = idea 1's copy of sw002 Track A) or sarcastic system + sarcastic history + prohibition ("sar", lib/bcommon_b.py
= sw002 Track B). All 199 scripts. Opener "By the way," + 48 tokens, T 0.7.
Vector = sign * alpha * nbar018[32] * unit, added at L32 (output of model.layers[32]) from the first turn-3 header token through
the last generated token (idea 2's 'from' scope). Directions (unit, L32):
  H           sw002 Track H dir_H (parent: next speaker dismissive - helpful), sign -1 (= idea 2's -H)
  random_0..4 018's seeded Gaussian units, sign -1;  gauss_0..4 5 new seeded Gaussian units (seed_of("verify1027-gauss", i)), sign -1
  story_dismissive (sign -1), story_helper (+1), axis (+1 and -1), helper_minus_dismissive = unit(raw story_helper - raw
  story_dismissive) (+1)  [018 directions_parent.pt; story_X = mean(playing story character X) - mean(default)]
--grid full : -H, 10 randoms, 5 persona directions x alpha {0.2, 0.4}  (+ unsteered)            [B s0, B s1]
--grid small: -H, random_0..4 x alpha {0.2, 0.4}  (+ unsteered)                                   [A s0, rep B, 011, sarc B]
Seeds: fresh salt, seed_of("verify1027-v2", script_id), shared by every cell (paired).
--long 1: also 100 s100 scripts x {unsteered, -H a0.2, -H a0.4, -random_0 a0.4}: reply with NO opener, 200 tokens,
          seed_of("verify1027-v2long", script_id), steering from the header through the 200 generated tokens.
Hook check: on 4 scripts, steered - unsteered header state at L32 equals the added vector; L33 shifted.
Usage: MODEL_NAME=B_s0 MODEL_PATH=/root/merged_sw001/hd-B_s0 PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 \
         python run_v2.py --model B_s0 --ctx dis --grid full --long 1"""
import argparse, json, os, sys, time
import torch
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
DIRS018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/directions_parent.pt"
DIRH = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH/out/dir_H.pt"
L, NTOK, NLONG = 32, 48, 200
log = lambda **k: print(json.dumps(k), flush=True)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--ctx", required=True, choices=["dis", "sar"])
    ap.add_argument("--grid", required=True, choices=["full", "small"]); ap.add_argument("--long", type=int, default=0)
    ap.add_argument("--smoke", type=int, default=0)
    a = ap.parse_args(); M = a.model
    if a.ctx == "dis":
        import bcommon as B  # noqa: E402
        CELL = ("dis", "dis", 1)
    else:
        import bcommon_b as B  # noqa: E402
        CELL = ("sar", "sar", 1)
    C = B.C
    if os.environ.get("MODEL_PATH"):
        C.MODELS[os.environ["MODEL_NAME"]] = os.environ["MODEL_PATH"]
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import SteeringVector, Hook
    import vllm_lens
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    R = B.build(tok)
    SIDS = [s["script_id"] for s in C.scripts()]; assert len(SIDS) == 199
    S100 = [s for s in SIDS if s in set(C.subsets()["s100"])]; assert len(S100) == 100
    if a.smoke:
        SIDS, S100 = SIDS[:a.smoke], S100[:a.smoke]
    D18 = torch.load(DIRS018, weights_only=False, mmap=True); DH = torch.load(DIRH, weights_only=False)
    U = {"H": DH["unit"][L].float()}
    for i in range(5):
        U[f"random_{i}"] = D18["unit"][f"random_{i}"][L].float()
        g = torch.Generator().manual_seed(C.seed_of("verify1027-gauss", i)); v = torch.randn(5120, generator=g); U[f"gauss_{i}"] = v / v.norm()
    for k in ("story_dismissive", "story_helper", "axis"):
        U[k] = D18["unit"][k][L].float()
    hmd = D18["raw"]["story_helper"][L].float() - D18["raw"]["story_dismissive"][L].float(); U["helper_minus_dismissive"] = hmd / hmd.norm()
    for k, u in U.items():
        assert abs(float(u.norm()) - 1) < 1e-3, k
    NB = float(D18["nbar"][L])
    vec = lambda dn, al, sign: (sign * float(al) * NB * U[dn]).float()
    if a.grid == "full":
        DS = [("H", -1)] + [(f"random_{i}", -1) for i in range(5)] + [(f"gauss_{i}", -1) for i in range(5)] + \
             [("story_dismissive", -1), ("story_helper", 1), ("axis", 1), ("axis", -1), ("helper_minus_dismissive", 1)]
    else:
        DS = [("H", -1)] + [(f"random_{i}", -1) for i in range(5)]
    seed = lambda s: C.seed_of("verify1027-v2", s)
    rows = []   # (rid, ids, steering or None, seed, max_tokens)
    for s in SIDS:
        rows.append((f"op|unsteered|{s}", R[CELL][s]["op"], None, seed(s), NTOK))
    def sv(ids, hdr0, ntok, dn, al, sign):
        P = list(range(hdr0, len(ids) + ntok)); v = vec(dn, al, sign)
        return SteeringVector(activations=v[None, None].expand(1, len(P), -1).contiguous(), layer_indices=[L], scale=1.0,
                              norm_match=False, position_indices=P)
    for dn, sign in DS:
        for al in (0.2, 0.4):
            tag = ("-" if sign < 0 else "+") + dn
            for s in SIDS:
                r = R[CELL][s]
                rows.append((f"op|{tag}|a{al}|{s}", r["op"], sv(r["op"], r["hdr"][0], NTOK, dn, al, sign), seed(s), NTOK))
    if a.long:
        for s in S100:
            r = R[CELL][s]; pid = r["op"][:r["n_prompt_hdr"]]
            assert r["hdr"][-1] == len(pid) - 1, (r["hdr"], len(pid))
            for tag, dn, al, sign in (("unsteered", None, 0, 0), ("-H|a0.2", "H", 0.2, -1), ("-H|a0.4", "H", 0.4, -1),
                                      ("-random_0|a0.4", "random_0", 0.4, -1)):
                rows.append((f"long|{tag}|{s}", pid, None if dn is None else sv(pid, r["hdr"][0], NLONG, dn, al, sign),
                             C.seed_of("verify1027-v2long", s), NLONG))
    log(event="rows", n=len(rows), model=M, ctx=a.ctx, grid=a.grid, cell=list(CELL))
    llm = LLM(model=C.MODELS[M], tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    OUT = os.path.join(HERE, "out"); t0 = time.time(); log(event="loaded", model=M)
    tagf = f"{M}{'_smoke' if a.smoke else ''}"
    with open(f"{OUT}/gen_{tagf}.jsonl", "w") as f:
        for c0 in range(0, len(rows), 2000):
            ch = rows[c0:c0 + 2000]
            sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=mt, seed=sd,
                                  extra_args=({"apply_steering_vectors": [v]} if v is not None else None)) for _, _, v, sd, mt in ch]
            outs = llm.generate([TokensPrompt(prompt_token_ids=x[1]) for x in ch], sps, use_tqdm=False)
            for (rid, _, _, _, _), o in zip(ch, outs):
                ti = list(o.outputs[0].token_ids)
                f.write(json.dumps(dict(id=rid, model=M, ctx=a.ctx, text=o.outputs[0].text, n_tok=len(ti),
                                        rep=(sum(1 for i in range(1, len(ti)) if ti[i] == ti[i - 1]) / max(1, len(ti) - 1)))) + "\n")
            log(event="progress", n=c0 + len(ch), secs=round(time.time() - t0))
    # hook check: steered - unsteered header states at L equal the added vector; L+1 shifted
    def make_fn(lo, hi, total):
        def fn(ctx, h):
            a0 = ctx.abs_start; n = h.shape[0]; Lx = ctx.layer_idx; svd = ctx.saved
            x, y = max(lo, a0), min(hi, a0 + n)
            if y > x:
                svd[f"{Lx}|{x}"] = h[x - a0:y - a0].float().clone()
            if a0 + n >= total:
                out = {k: v.cpu() for k, v in svd.items()}; svd.clear(); svd.update(out)
            return None
        return fn
    errs, shifts = [], []
    for s in SIDS[:4]:
        r = R[CELL][s]; lo, hi = r["hdr"][0], r["hdr"][-1] + 1
        st = {}
        for name, v in (("un", None), ("st", sv(r["op"], r["hdr"][0], 0, "H", 0.4, -1))):
            ex = {"apply_hooks": [Hook(fn=make_fn(lo, hi, len(r["op"])), layer_indices=[L, L + 1])]}
            if v is not None:
                ex["apply_steering_vectors"] = [v]
            o = llm.generate([TokensPrompt(prompt_token_ids=r["op"])], [SamplingParams(max_tokens=1, temperature=0, extra_args=ex)],
                             use_tqdm=False)[0]
            hr = o.hook_results["0"]
            st[name] = {Lx: torch.cat([hr[k] for _, k in sorted((int(k.split("|")[1]), k) for k in hr if int(k.split("|")[0]) == Lx)])
                        for Lx in (L, L + 1)}
        d = st["st"][L] - st["un"][L]; tgt = vec("H", 0.4, -1)[None].expand_as(d)
        errs.append(float(((d - tgt).norm(dim=-1) / tgt.norm(dim=-1)).mean()))
        shifts.append(float(((st["st"][L + 1] - st["un"][L + 1]).norm(dim=-1) / st["un"][L + 1].norm(dim=-1)).mean()))
    chk = dict(layer=L, relerr_added_vs_target=errs, rel_shift_at_L_plus_1=shifts)
    json.dump(chk, open(f"{OUT}/hookcheck_{tagf}.json", "w"), indent=1)
    log(event="hookcheck", chk=chk); log(event="all_done", model=M, secs=round(time.time() - t0))
