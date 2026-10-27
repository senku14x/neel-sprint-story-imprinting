"""V3-extra (verify fork, added 08:40 after V2 found 018 persona directions also move chat): is H special in STORIES?
Same as run_v3.py except the cells: H and 018 persona directions with the sign that points toward the dismissive
character (+H, +story_dismissive, +dismissive_minus_helper = unit(raw story_dismissive - raw story_helper), -axis, -story_helper)
at alpha 0.2 / 0.4. Output tag suffix _persona.
Original docstring: V3 (verify fork, 27 Oct 2026): Track H's direction in story continuations on held-out stories. Derived from idea 3's
run_story_rand.py (copy: run_story_rand_orig.py; sha256 in ../source_sha256.txt). Changes: story sets from out/sets.jsonl
(build_v3.py: Bho / Aho held-out, orig = idea 3's set), 10 random directions at alpha 0.4 (018 random_0..4 + 5 new seeded
Gaussian unit vectors gauss_0..4) and 018's 5 at alpha 0.2, and a hook check.
Vector = alpha * nbar018[32] * unit, added at L32 (output of model.layers[32]) from the boundary (last prompt token) through
the 64 generated tokens (idea 3's 'from' scope, positive sign). T 0.7, 64 tokens, seed = idea 3's rule
seed_of("idea3", "S|<file>|<row>") (identical to idea 3 on the orig set).
Usage: MODEL_NAME=B_s0 MODEL_PATH=/root/merged_sw001/hd-B_s0 PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 \
         python run_v3.py --model B_s0 --sets Bho,orig"""
import argparse, json, os, sys, time
import torch
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import bcommon as B  # noqa: E402  (copy of idea 1's bcommon.py = sw002 trackA/box4/bcommon.py)
C = B.C
DIRS018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/directions_parent.pt"
DIRH = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH/out/dir_H.pt"
L, NTOK = 32, 64
log = lambda **k: print(json.dumps(k), flush=True)


def gauss_dirs(d=5120):
    out = {}
    for i in range(5):
        g = torch.Generator().manual_seed(C.seed_of("verify1027-gauss", i))
        v = torch.randn(d, generator=g); out[f"gauss_{i}"] = v / v.norm()
    return out


def make_fn(P, total):
    P = set(P)
    def fn(ctx, h):
        a0 = ctx.abs_start; n = h.shape[0]; Lx = ctx.layer_idx; sv = ctx.saved
        for p in P:
            if a0 <= p < a0 + n:
                sv[f"{Lx}|{p}"] = h[p - a0].float().clone()
        if a0 + n >= total:
            out = {k: v.cpu() for k, v in sv.items()}; sv.clear(); sv.update(out)
        return None
    return fn


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--sets", required=True)
    ap.add_argument("--smoke", type=int, default=0)
    a = ap.parse_args(); M = a.model; SETS = a.sets.split(",")
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import Hook, SteeringVector
    import vllm_lens
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    ALL = [json.loads(l) for l in open(f"{HERE}/out/sets.jsonl")]
    REC = [r for r in ALL if r["set"] in SETS]
    if a.smoke:
        REC = [r for s in SETS for r in [x for x in REC if x["set"] == s][:a.smoke]]
    D18 = torch.load(DIRS018,weights_only=False, mmap=True); DH = torch.load(DIRH, weights_only=False)
    DIRS = {"H": DH["unit"][L].float()}
    DIRS.update({f"random_{i}": D18["unit"][f"random_{i}"][L].float() for i in range(5)})
    for k in ("story_dismissive", "story_helper", "axis"):
        DIRS[k] = D18["unit"][k][L].float()
    dmh = D18["raw"]["story_dismissive"][L].float() - D18["raw"]["story_helper"][L].float(); DIRS["dismissive_minus_helper"] = dmh / dmh.norm()
    DIRS["-axis"] = -DIRS["axis"]; DIRS["-story_helper"] = -DIRS["story_helper"]
    for k, u in DIRS.items():
        assert abs(float(u.norm()) - 1) < 1e-3, k
    NB = float(D18["nbar"][L])
    CELLS = [(d, al) for d in ("H", "story_dismissive", "dismissive_minus_helper", "-axis", "-story_helper") for al in (0.2, 0.4)]
    vec = lambda dn, al: (al * NB * DIRS[dn]).float()
    rows = []
    for r in REC:
        n = len(r["ids"]); P = list(range(n - 1, n + NTOK))
        rows.append((f"{r['set']}|unsteered|{r['id']}", r, None))
        for dn, al in CELLS:
            v = vec(dn, al)
            rows.append((f"{r['set']}|{dn}|a{al}|{r['id']}", r, SteeringVector(activations=v[None, None].expand(1, len(P), -1).contiguous(),
                                                                              layer_indices=[L], scale=1.0, norm_match=False, position_indices=P)))
    log(event="rows", n=len(rows), model=M, sets=SETS)
    llm = LLM(model=C.MODELS[M], tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    t0 = time.time(); log(event="loaded", model=M)
    sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=NTOK, seed=C.seed_of("idea3", f"S|{r['file']}|{r['row']}"),
                          extra_args=({"apply_steering_vectors": [sv]} if sv is not None else None)) for _, r, sv in rows]
    OUT = os.path.join(HERE, "out"); tag = f"{M}_{'_'.join(SETS)}_persona{'_smoke' if a.smoke else ''}"
    with open(f"{OUT}/gen_{tag}.jsonl", "w") as f:
        for c0 in range(0, len(rows), 2000):
            outs = llm.generate([TokensPrompt(prompt_token_ids=x[1]["ids"]) for x in rows[c0:c0 + 2000]], sps[c0:c0 + 2000], use_tqdm=False)
            for (rid, r, _), o in zip(rows[c0:c0 + 2000], outs):
                f.write(json.dumps(dict(id=rid, set=r["set"], story=r["id"], helper=r["helper"], names=r["names"], model=M,
                                        text=o.outputs[0].text)) + "\n")
            log(event="progress", n=c0 + len(outs), secs=round(time.time() - t0))
    # hook check (4 stories): at the boundary position, steered - unsteered state at L32 equals the added vector; L33 shifted
    chk = {}
    def cap(r, st):
        n = len(r["ids"]); ex = {"apply_hooks": [Hook(fn=make_fn([n - 1], n), layer_indices=[L, L + 1])]}
        if st is not None:
            ex["apply_steering_vectors"] = [st]
        o = llm.generate([TokensPrompt(prompt_token_ids=r["ids"])], [SamplingParams(max_tokens=1, temperature=0, extra_args=ex)],
                         use_tqdm=False)[0]
        hr = o.hook_results["0"]
        return hr[f"{L}|{n - 1}"], hr[f"{L + 1}|{n - 1}"]
    errs, sh = [], []
    for r in REC[:4]:
        n = len(r["ids"]); v = vec("H", 0.4)
        st = SteeringVector(activations=v[None, None].contiguous(), layer_indices=[L], scale=1.0, norm_match=False, position_indices=[n - 1])
        u0, u1 = cap(r, None); s0, s1 = cap(r, st)
        errs.append(float((s0 - u0 - v).norm() / v.norm())); sh.append(float((s1 - u1).norm() / u1.norm()))
    chk = dict(layer=L, relerr_added_vs_target=errs, rel_shift_at_L_plus_1=sh, target_norm=float(vec("H", 0.4).norm()))
    json.dump(chk, open(f"{OUT}/hookcheck_{tag}.json", "w"), indent=1)
    log(event="hookcheck", chk=chk); log(event="all_done", model=M, secs=round(time.time() - t0))
