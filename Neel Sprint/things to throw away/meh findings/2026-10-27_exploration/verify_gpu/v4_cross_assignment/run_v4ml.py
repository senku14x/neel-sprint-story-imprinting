"""V4 job 3 (verify fork, 27 Oct 2026, user follow-up): B s0's header pasted into the PARENT at several layers at once.
Recipient: the parent's default + prohibition cell (lib/bcommon.py contexts, all 199 scripts). Targets (7 turn-3 header states):
  cross_same    B s0's dismissive + dismissive-history + prohibition header (idea 4's all-layer capture, hdr64/B_s0.pt; identical
                to idea 1's donor file at L40)
  cross_default B s0's default + prohibition header (foreign state without routing content)
  own_same      the parent's own dismissive + prohibition header (captured here)
  rand          per-position Gaussian with norms matched to the cross_same deltas, added at the same layers
Layer sets: {40} (single layer; overnight +5.5), {32, 40, 48}, {36, 40, 44, 48}. Multi-layer paste is sequential: the delta at
layer l_k is target(l_k) minus the recipient's state at l_k captured WITH the patches at l_1..l_{k-1} applied, so after the
forward pass the state at every patched layer equals the target. One SteeringVector per layer in apply_steering_vectors.
Readout: "By the way," + 48 tokens, T 0.7, Track A seed. Hook check (8 scripts): state at every patched layer vs target.
Usage: MODEL_NAME=parent MODEL_PATH=/dev/shm/qwen36_27b PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 python run_v4ml.py"""
import argparse, json, os, sys, time
import torch
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import bcommon as B  # noqa: E402
C = B.C
HDR64 = "/workspace/runs_executor/explore1027/hdr64/B_s0.pt"
SETS = {"L40": [40], "L32_40_48": [32, 40, 48], "L36_40_44_48": [36, 40, 44, 48]}
ALLL = sorted({l for v in SETS.values() for l in v})
DEF, DIS = ("none", "def", 1), ("dis", "dis", 1)
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


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", type=int, default=0); a = ap.parse_args()
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import SteeringVector, Hook
    import vllm_lens
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    M = os.environ.get("MODEL_NAME", "parent")
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    R = B.build(tok)
    SIDS = [s["script_id"] for s in C.scripts()]; assert len(SIDS) == 199
    if a.smoke:
        SIDS = SIDS[:a.smoke]
    D = torch.load(HDR64, weights_only=False, mmap=True)
    didx = {s: i for i, s in enumerate(D["sids"])}; J = [didx[s] for s in SIDS]
    TGT = {"cross_same": D["cells"][B.cname(DIS)][J][:, ALLL].float(), "cross_default": D["cells"][B.cname(DEF)][J][:, ALLL].float()}
    li = {l: i for i, l in enumerate(ALLL)}
    llm = LLM(model=C.MODELS[M], tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    t0 = time.time(); log(event="loaded", model=M)

    def capture(items, layers, chunk=400):   # items: (ids, hdr, [steering vectors]) -> [n, len(layers), 7, d]
        res = []
        for c0 in range(0, len(items), chunk):
            b = items[c0:c0 + chunk]; sps = []
            for ids, hdr, svs in b:
                ex = {"apply_hooks": [Hook(fn=make_fn(hdr[0], hdr[-1] + 1, max(layers), len(ids)), layer_indices=layers)]}
                if svs:
                    ex["apply_steering_vectors"] = list(svs)
                sps.append(SamplingParams(max_tokens=1, temperature=0, extra_args=ex))
            outs = llm.generate([TokensPrompt(prompt_token_ids=x[0]) for x in b], sps, use_tqdm=False)
            for (ids, hdr, svs), o in zip(b, outs):
                hr = o.hook_results["0"]; per = []
                for L in layers:
                    ks = sorted((int(k.split("|")[1]), k) for k in hr if int(k.split("|")[0]) == L)
                    t = torch.cat([hr[k] for _, k in ks]); assert t.shape[0] == len(hdr); per.append(t)
                res.append(torch.stack(per))
        return torch.stack(res)

    # .clone(): d is a row view of a [199, 7, d] tensor; without a copy every SteeringVector serialises the whole storage
    # (first run 12:17 failed with msgspec "bytes-like objects longer than 2**32 - 1")
    mk = lambda d, L, hdr: SteeringVector(activations=d[None].float().clone().contiguous(), layer_indices=[L], scale=1.0, norm_match=False,
                                          position_indices=list(hdr))
    RD = [R[DEF][s] for s in SIDS]
    TGT["own_same"] = capture([(R[DIS][s]["op"], R[DIS][s]["hdr"], None) for s in SIDS], ALLL)
    log(event="own_captured", secs=round(time.time() - t0))
    SV = {}   # (arm, set) -> list per script of [SteeringVector per layer]
    DELTA_SAME = {}
    for sname, Ls in SETS.items():
        for arm in ("cross_same", "cross_default", "own_same"):
            per = [[] for _ in SIDS]; deltas = []
            for L in Ls:
                cur = capture([(r["op"], r["hdr"], per[i]) for i, r in enumerate(RD)], [L])[:, 0]
                d = TGT[arm][:, li[L]] - cur; deltas.append(d)
                for i, r in enumerate(RD):
                    per[i].append(mk(d[i], L, r["hdr"]))
            SV[(arm, sname)] = per
            if arm == "cross_same":
                DELTA_SAME[sname] = deltas
        per = [[] for _ in SIDS]
        for k, L in enumerate(Ls):
            for i, (s, r) in enumerate(zip(SIDS, RD)):
                ref = DELTA_SAME[sname][k][i]
                g = torch.Generator().manual_seed(C.seed_of("v4ml-rand", s, L)); rnd = torch.randn(ref.shape, generator=g)
                per[i].append(mk(rnd / rnd.norm(dim=-1, keepdim=True) * ref.norm(dim=-1, keepdim=True), L, r["hdr"]))
        SV[("rand", sname)] = per
        log(event="deltas_done", set=sname, secs=round(time.time() - t0))
    rows = [(f"orig|p1|{B.cname(c)}|{s}", R[c][s]["op"], None, B.seed(s)) for c in (DEF, DIS) for s in SIDS]
    for (arm, sname), per in SV.items():
        for i, s in enumerate(SIDS):
            rows.append((f"orig|p2|{arm}|{sname}|{s}", RD[i]["op"], per[i], B.seed(s)))
    sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=48, seed=sd,
                          extra_args=({"apply_steering_vectors": list(svs)} if svs else None)) for _, _, svs, sd in rows]
    tag = f"B_s0_to_{M}_multilayer{'_smoke' if a.smoke else ''}"
    with open(f"{HERE}/out/gen_{tag}.jsonl", "w") as f:
        for c0 in range(0, len(rows), 2000):
            outs = llm.generate([TokensPrompt(prompt_token_ids=x[1]) for x in rows[c0:c0 + 2000]], sps[c0:c0 + 2000], use_tqdm=False)
            for (rid, _, _, _), o in zip(rows[c0:c0 + 2000], outs):
                f.write(json.dumps(dict(id=rid, model=M, donor="B_s0", text=o.outputs[0].text)) + "\n")
            log(event="gen_progress", n=c0 + len(outs), secs=round(time.time() - t0))
    chk = {}
    for sname, Ls in SETS.items():
        idx = list(range(min(8, len(SIDS))))
        st = capture([(RD[i]["op"], RD[i]["hdr"], SV[("cross_same", sname)][i]) for i in idx], Ls)
        un = capture([(RD[i]["op"], RD[i]["hdr"], None) for i in idx], Ls)
        r = {}
        for k, L in enumerate(Ls):
            tg = TGT["cross_same"][idx, li[L]]
            r[f"L{L}"] = dict(relerr_vs_target=float(((st[:, k] - tg).norm(dim=-1) / tg.norm(dim=-1)).mean()),
                              unpatched_relerr_vs_target=float(((un[:, k] - tg).norm(dim=-1) / tg.norm(dim=-1)).mean()))
        chk[sname] = r
    json.dump(chk, open(f"{HERE}/out/hookcheck_{tag}.json", "w"), indent=1)
    log(event="hookcheck", chk=chk); log(event="all_done", model=M, secs=round(time.time() - t0))
