"""b_routing GPU pass for one model, one engine (vllm-lens-fixed + 018 patch). Logic copied from sw001 worker_sw.py.
  1. capture per-position turn-3 header residuals (output of layers[L], L in 32/40/48) for 8 context cells x 199 scripts
  2. Part 1: 'By the way,' openers (48 tok, T 0.7, sw001 default seed per script, shared by all cells/arms) for 8 cells;
     bee/bees/crow next-token log-probs after 008's bridges b1/b2 on sw001's s100 scripts for 8 cells
  3. Part 2: header transplant at ONE layer L (per-position additive delta at the header positions only = exact
     replacement at layer L): arms same / shuf / noprohib / rand (per-position norm-matched) / reverse
  4. hook checks: capture at L and L+1 under the transplant (16 scripts) vs the donor / recipient states
Usage: PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 /root/venvs/vlfix/bin/python run_gpu.py --model B_s0"""
import argparse, json, os, random, sys, time
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bcommon as B  # noqa: E402
C = B.C
from vllm import LLM, SamplingParams  # noqa: E402
from vllm.inputs import TokensPrompt  # noqa: E402
from vllm_lens import Hook, SteeringVector  # noqa: E402

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


def capture(items, layers, chunk=400):
    """items: list of (ids, hdr_positions, steer_extra or None) -> tensor [n, len(layers), n_hdr, d] fp32"""
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


def run_all(SIDS, S100, tag, P2N):
    t1 = time.time()
    HD = {}
    KA = bool(os.environ.get("KA"))   # sw002 known-answer subset: capture DEF + DIS only, default-cell openers, same|L40, no lp
    CAPC = [("none", "def", 1), ("dis", "dis", 1)] if KA else B.CELLS
    for c in CAPC:
        HD[c] = capture([(R[c][s]["op"], R[c][s]["hdr"], None) for s in SIDS], B.LAYERS)
    torch.save(dict(cells={B.cname(c): HD[c].half() for c in CAPC}, sids=SIDS, layers=B.LAYERS, model=M), f"{B.BIG}/{tag}_hdr.pt")
    log(event="captured", secs=round(time.time() - t1), shape=list(HD[B.CELLS[0]].shape))

    # ---------------------------------------------------------------- 2/3. generation rows
    DEF, DIS, DISNP = ("none", "def", 1), ("dis", "dis", 1), ("dis", "dis", 0)
    perm = list(range(len(SIDS)))
    rng = random.Random(2626)
    while any(i == j for i, j in enumerate(perm)):
        rng.shuffle(perm)
    rows = []
    for c in ([DEF] if KA else B.CELLS):
        for i, s in enumerate(SIDS):
            rows.append((f"p1|{B.cname(c)}|{s}", R[c][s]["op"], None))
    P2 = set(S100[:P2N]) if P2N <= len(S100) else set(SIDS)
    for li, L in enumerate(B.LAYERS):
        for i, s in enumerate(SIDS):
            if s not in P2:
                continue
            d_same = HD[DIS][i, li] - HD[DEF][i, li]
            g = torch.Generator().manual_seed(C.seed_of("b_routing-rand", s, L))
            rnd = torch.randn(d_same.shape, generator=g)
            rnd = rnd / rnd.norm(dim=-1, keepdim=True) * d_same.norm(dim=-1, keepdim=True)
            arms = dict(same=(DEF, d_same), shuf=(DEF, HD[DIS][perm[i], li] - HD[DEF][perm[i], li]),
                        noprohib=(DEF, (HD[DISNP][i, li] if DISNP in HD else HD[DEF][i, li]) - HD[DEF][i, li]), rand=(DEF, rnd), reverse=(DIS, -d_same))
            for arm, (cell, delta) in arms.items():
                if KA and (L != 40 or arm != "same"):
                    continue
                r = R[cell][s]
                sv = SteeringVector(activations=delta[None].float().contiguous(), layer_indices=[L], scale=1.0, norm_match=False,
                                    position_indices=list(r["hdr"]))
                rows.append((f"p2|{arm}|L{L}|{s}", r["op"], sv))
    log(event="gen_rows", n=len(rows))
    t2 = time.time()
    sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=48, seed=B.seed(rid.split("|")[-1]),
                          extra_args=({"apply_steering_vectors": [sv]} if sv is not None else None)) for rid, _, sv in rows]
    outs = []
    for c0 in range(0, len(rows), 2000):
        outs += llm.generate([TokensPrompt(prompt_token_ids=x[1]) for x in rows[c0:c0 + 2000]], sps[c0:c0 + 2000], use_tqdm=False)
        log(event="gen_progress", n=len(outs), secs=round(time.time() - t2))
    with open(f"{OUT}/gen_{tag}.jsonl", "w") as f:
        for (rid, _, sv), o in zip(rows, outs):
            f.write(json.dumps(dict(id=rid, model=M, text=o.outputs[0].text, n_tok=len(o.outputs[0].token_ids),
                                    finish=o.outputs[0].finish_reason)) + "\n")
    log(event="gen_done", secs=round(time.time() - t2))

    # ---------------------------------------------------------------- 2b. log-probs after 008 bridges
    allowed = [C.BEE, C.BEES, C.CROW]
    lrows = [] if KA else [(f"lp|{B.cname(c)}|{b}|{s}", R[c][s][b]) for c in B.CELLS for s in S100 for b in ("b1", "b2")]
    lo = [] if not lrows else llm.generate([TokensPrompt(prompt_token_ids=x[1]) for x in lrows],
                      [SamplingParams(temperature=1.0, max_tokens=1, logprobs=3, allowed_token_ids=allowed, seed=0) for _ in lrows], use_tqdm=False)
    with open(f"{OUT}/lp_{tag}.jsonl", "w") if lrows else open(os.devnull, "w") as f:
        for (rid, _), o in zip(lrows, lo):
            d = o.outputs[0].logprobs[0]; assert all(t in d for t in allowed)
            f.write(json.dumps(dict(id=rid, model=M, lp={str(t): d[t].logprob for t in allowed})) + "\n")
    log(event="lp_done", n=len(lrows))

    # ---------------------------------------------------------------- 4. hook checks
    chk = {}
    for li, L in enumerate(B.LAYERS):
        if KA and L != 40:
            continue
        idx = list(range(min(16, len(SIDS))))
        for arm, cell, donor, recip in (("same", DEF, DIS, DEF), ("reverse", DIS, DEF, DIS)):
            items_st, items_un = [], []
            for i in idx:
                s = SIDS[i]; r = R[cell][s]
                delta = HD[donor][i, li] - HD[recip][i, li]
                sv = SteeringVector(activations=delta[None].float().contiguous(), layer_indices=[L], scale=1.0, norm_match=False,
                                    position_indices=list(r["hdr"]))
                items_st.append((r["op"], r["hdr"], sv))
                items_un.append((R[donor][s]["op"], R[donor][s]["hdr"], None))
            st = capture(items_st, [L, L + 1]); un_donor = capture(items_un, [L, L + 1])
            un_recip = capture([(R[cell][SIDS[i]]["op"], R[cell][SIDS[i]]["hdr"], None) for i in idx], [L, L + 1])
            cos = lambda x, y: torch.nn.functional.cosine_similarity(x, y, dim=-1)
            rel = lambda x, y: ((x - y).norm(dim=-1) / y.norm(dim=-1))
            chk[f"{arm}|L{L}"] = {f"layer{k}": dict(
                relerr_vs_donor=float(rel(st[:, j], un_donor[:, j]).mean()), max_relerr_vs_donor=float(rel(st[:, j], un_donor[:, j]).max()),
                cos_vs_donor=float(cos(st[:, j], un_donor[:, j]).mean()), cos_vs_recip=float(cos(st[:, j], un_recip[:, j]).mean()),
                cos_donor_recip=float(cos(un_donor[:, j], un_recip[:, j]).mean()))
                for j, k in enumerate(("L", "L+1"))}
    json.dump(chk, open(f"{OUT}/hookcheck_{tag}.json", "w"), indent=1)
    log(event="hookcheck", chk=chk)
    log(event="all_done", model=M, secs=round(time.time() - t0))


if __name__ == "__main__":
    # main guard: vLLM spawns its engine core with 'spawn', which re-imports this file (first attempt crashed without it)
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--smoke", type=int, default=0)
    ap.add_argument("--p2n", type=int, default=199)   # Part 2 scripts: 199 = all, 100 = s100, 0 = skip Part 2
    a = ap.parse_args()
    M = a.model
    from transformers import AutoTokenizer  # noqa: E402
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    R = B.build(tok)
    SIDS = [s["script_id"] for s in C.scripts()]
    S100 = C.subsets()["s100"]
    if os.environ.get("ONLY_S100"):   # optional A extras (as paste_As1): capture / Part 1 on the s100 scripts only
        SIDS = [s for s in SIDS if s in set(S100)]
    OUT = f"{B.HERE}/out"; os.makedirs(OUT, exist_ok=True); os.makedirs(B.BIG, exist_ok=True)
    import vllm_lens  # noqa: E402
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    path = C.MODELS[M]; assert os.path.exists(f"{path}/config.json")
    t0 = time.time()
    llm = LLM(model=path, tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False,
              logprobs_mode="processed_logprobs", max_logprobs=20)
    log(event="loaded", model=M, secs=round(time.time() - t0))
    if a.smoke:
        sm = SIDS[:a.smoke]
        run_all(sm, [s for s in S100 if s in sm] or sm[:2], f"{M}_smoke", 999)
    run_all(SIDS, S100, M + os.environ.get("TAG_SUFFIX", ""), a.p2n)
