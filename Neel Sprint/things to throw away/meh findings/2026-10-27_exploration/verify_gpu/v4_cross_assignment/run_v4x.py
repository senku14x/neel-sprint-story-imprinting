"""V4 (verify fork, 27 Oct 2026, user follow-up): cross-ASSIGNMENT header transplant = ../v1_transplant/run_v1.py unchanged
except the tensor folder (BIG -> verify/v4) and the output folder (this folder's out/). Original docstring:
V1 (verify fork, 27 Oct 2026): cross-run header transplant. Derived from idea 1's run_x.py (copy: run_x_orig.py; sha256 in
../source_sha256.txt). Changes: --layers, --salts (fresh sampling-seed salts; "orig" = idea 1's Track A seed), a cross_shuf arm,
recipient header states saved for every layer in {32, 40, 48} (so a recipient can later act as a donor).
At ONE layer L the recipient's 7 turn-3 header residuals in its default + prohibition context are replaced by a target state
(delta added = target - recipient's own state):
  cross_same      donor's dis+pro header, same script
  cross_shuf      donor's dis+pro header of ANOTHER script (fixed derangement, random.Random(2627))
  own_same        recipient's own dis+pro header
  cross_noprohib  donor's dis, no-prohibition header
  cross_default   donor's default+pro header
  rand            per-position Gaussian, norms matched to the cross_same delta
Readout: "By the way," + 48 tokens, T 0.7. Unsteered cells (default+pro and dis+pro) per salt. Hook check (cross_same, 8 scripts).
Usage: MODEL_NAME=B_s1 MODEL_PATH=/root/merged_sw001/hd-B_s1 PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 \
   python run_v1.py --model B_s1 --donor B_s0=/root/runs/explore1026/b_routing/B_s0_hdr.pt --tag B_s0_to_B_s1 --layers 40 --salts s1,s2"""
import argparse, json, os, random, sys, time
import torch
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import bcommon as B  # noqa: E402  (copy of idea 1's bcommon.py)
C = B.C
BIG = "/workspace/runs_executor/explore1027/verify/v4"
CAPL = [32, 40, 48]
DEF, DIS, DISNP = ("none", "def", 1), ("dis", "dis", 1), ("dis", "dis", 0)
log = lambda **k: print(json.dumps(k), flush=True)


def make_fn(lo, hi, last_layer, total):
    def fn(ctx, h):
        a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx; sv = ctx.saved
        x, y = max(lo, a0), min(hi, a0 + n)
        if y > x:
            sv[f"{L}|{x}"] = h[x - a0:y - a0].float().clone()
        if L == last_layer and a0 + n >= total:
            out = {k: v.cpu() for k, v in sv.items()}; sv.clear(); sv.update(out)
        return None
    return fn


def capture(llm, items, layers, chunk=400):
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import Hook
    res = []
    for c0 in range(0, len(items), chunk):
        b = items[c0:c0 + chunk]; sps = []
        for ids, hdr, st in b:
            ex = {"apply_hooks": [Hook(fn=make_fn(hdr[0], hdr[-1] + 1, max(layers), len(ids)), layer_indices=layers)]}
            if st is not None:
                ex["apply_steering_vectors"] = [st]
            sps.append(SamplingParams(max_tokens=1, temperature=0, extra_args=ex))
        outs = llm.generate([TokensPrompt(prompt_token_ids=x[0]) for x in b], sps, use_tqdm=False)
        for (ids, hdr, st), o in zip(b, outs):
            hr = (o.hook_results or {}).get("0"); assert hr, "no hook result"
            per = []
            for L in layers:
                ks = sorted((int(k.split("|")[1]), k) for k in hr if int(k.split("|")[0]) == L)
                t = torch.cat([hr[k] for _, k in ks]); assert t.shape[0] == len(hdr), (t.shape, len(hdr)); per.append(t)
            res.append(torch.stack(per))
    return torch.stack(res)


def derangement(n, seed=2627):
    rng = random.Random(seed)
    while True:
        p = list(range(n)); rng.shuffle(p)
        if all(p[i] != i for i in range(n)):
            return p


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--donor", required=True); ap.add_argument("--tag", required=True)
    ap.add_argument("--layers", default="40"); ap.add_argument("--salts", default="orig"); ap.add_argument("--smoke", type=int, default=0)
    a = ap.parse_args(); M = a.model; dname, dpath = a.donor.split("=", 1)
    LAYERS = [int(x) for x in a.layers.split(",")]; SALTS = a.salts.split(",")
    assert all(L in CAPL for L in LAYERS)
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import SteeringVector
    import vllm_lens
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    R = B.build(tok)
    SIDS = [s["script_id"] for s in C.scripts()]; assert len(SIDS) == 199, len(SIDS)
    PERM = derangement(len(SIDS))   # over the full 199 (before any smoke cut)
    if a.smoke:
        SIDS = SIDS[:a.smoke]
    D = torch.load(dpath, map_location="cpu", weights_only=False)
    assert list(D["layers"]) == CAPL, D["layers"]
    didx = {s: i for i, s in enumerate(D["sids"])}; assert all(s in didx for s in SIDS)
    ALLS = [s["script_id"] for s in C.scripts()]
    DC = {c: D["cells"][B.cname(c)].float() for c in (DEF, DIS, DISNP)}
    hdr_tok = {tuple(R[c][s]["op"][p] for p in R[c][s]["hdr"]) for c in (DEF, DIS, DISNP) for s in SIDS}
    assert len(hdr_tok) == 1, hdr_tok
    OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True); os.makedirs(BIG, exist_ok=True)
    t0 = time.time()
    llm = LLM(model=C.MODELS[M], tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    log(event="loaded", model=M, secs=round(time.time() - t0))
    HD = {c: capture(llm, [(R[c][s]["op"], R[c][s]["hdr"], None) for s in SIDS], CAPL) for c in (DEF, DIS, DISNP)}
    torch.save(dict(cells={B.cname(c): HD[c].half() for c in HD}, sids=SIDS, layers=CAPL, model=M),
               f"{BIG}/{a.tag}{'_smoke' if a.smoke else ''}_recipient_hdr.pt")
    log(event="captured", secs=round(time.time() - t0))
    li_of = {L: CAPL.index(L) for L in LAYERS}
    seed = lambda salt, s: B.seed(s) if salt == "orig" else C.seed_of("verify1027-v1", salt, s)
    rows = []
    for salt in SALTS:
        rows += [(f"{salt}|p1|{B.cname(c)}|{s}", R[c][s]["op"], None, seed(salt, s)) for c in (DEF, DIS) for s in SIDS]
        for L in LAYERS:
            li = li_of[L]
            for i, s in enumerate(SIDS):
                j = didx[s]; rec = HD[DEF][i, li]
                jsh = didx[ALLS[PERM[ALLS.index(s)]]]
                d_cross = DC[DIS][j, li] - rec
                g = torch.Generator().manual_seed(C.seed_of("idea1-rand", s, L))
                rnd = torch.randn(d_cross.shape, generator=g); rnd = rnd / rnd.norm(dim=-1, keepdim=True) * d_cross.norm(dim=-1, keepdim=True)
                arms = dict(cross_same=d_cross, cross_shuf=DC[DIS][jsh, li] - rec, own_same=HD[DIS][i, li] - rec,
                            cross_noprohib=DC[DISNP][j, li] - rec, cross_default=DC[DEF][j, li] - rec, rand=rnd)
                r = R[DEF][s]
                for arm, delta in arms.items():
                    sv = SteeringVector(activations=delta[None].float().contiguous(), layer_indices=[L], scale=1.0, norm_match=False,
                                        position_indices=list(r["hdr"]))
                    rows.append((f"{salt}|p2|{arm}|L{L}|{s}", r["op"], sv, seed(salt, s)))
    log(event="gen_rows", n=len(rows))
    sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=48, seed=sd,
                          extra_args=({"apply_steering_vectors": [sv]} if sv is not None else None)) for _, _, sv, sd in rows]
    with open(f"{OUT}/gen_{a.tag}{'_smoke' if a.smoke else ''}.jsonl", "w") as f:
        for c0 in range(0, len(rows), 2000):
            outs = llm.generate([TokensPrompt(prompt_token_ids=x[1]) for x in rows[c0:c0 + 2000]], sps[c0:c0 + 2000], use_tqdm=False)
            for (rid, _, _, _), o in zip(rows[c0:c0 + 2000], outs):
                f.write(json.dumps(dict(id=rid, model=M, donor=dname, text=o.outputs[0].text)) + "\n")
            log(event="gen_progress", n=c0 + len(outs), secs=round(time.time() - t0))
    chk = {}
    idx = list(range(min(8, len(SIDS))))
    for L in LAYERS:
        li = li_of[L]; items = []
        for i in idx:
            s = SIDS[i]; r = R[DEF][s]
            delta = DC[DIS][didx[s], li] - HD[DEF][i, li]
            items.append((r["op"], r["hdr"], SteeringVector(activations=delta[None].float().contiguous(), layer_indices=[L], scale=1.0,
                                                             norm_match=False, position_indices=list(r["hdr"]))))
        st = capture(llm, items, [L, L + 1]); un = capture(llm, [(R[DEF][SIDS[i]]["op"], R[DEF][SIDS[i]]["hdr"], None) for i in idx], [L, L + 1])
        tgt = torch.stack([DC[DIS][didx[SIDS[i]], li] for i in idx])
        rel = ((st[:, 0] - tgt).norm(dim=-1) / tgt.norm(dim=-1))
        cos = torch.nn.functional.cosine_similarity
        chk[f"L{L}"] = dict(relerr_vs_donor_mean=float(rel.mean()), relerr_vs_donor_max=float(rel.max()),
                            cos_L_vs_donor=float(cos(st[:, 0], tgt, dim=-1).mean()),
                            cos_Lplus1_steered_vs_unsteered=float(cos(st[:, 1], un[:, 1], dim=-1).mean()))
    json.dump(chk, open(f"{OUT}/hookcheck_{a.tag}{'_smoke' if a.smoke else ''}.json", "w"), indent=1)
    log(event="hookcheck", chk=chk)
    log(event="all_done", model=M, secs=round(time.time() - t0))
