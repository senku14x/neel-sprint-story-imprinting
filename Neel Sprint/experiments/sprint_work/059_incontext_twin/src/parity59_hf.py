"""sw059 HF parity (sw059 prep agent, 31 Oct 2026). Runs in the smoke job AFTER gen59.py --mode smoke has exited (one model-holding
process on the GPU at a time). HF transformers (si venv), the parent in bf16, eval, no adapters, use_cache False, one sequence at a
time (no padding).

Inputs: RUN/smoke/parity_vllm.json (gen59.parity_vllm): 8 contexts at k = 64 (draw 0; A/B x authored/pasted x {default, Lh}); for each,
vLLM's production path (block warmed, prefix-cached) greedy 32 tokens with their log-probs, the same request with the prefix cache
skipped, and the same recipient at k = 0 (no story block).
Teacher-forced HF log-probs of the generated tokens (log_softmax of the logits at the positions that predict them):
  d64[i]  = mean_t |logp_vLLM,cached - logp_HF| on the k = 64 context (the parity statistic)
  d0[i]   = the same on the k = 0 counterpart (the cross-engine noise floor where no long context is involved)
  eff[i]  = mean_t |logp_HF(k = 64 tokens | k = 64 context) - logp_HF(same tokens | k = 0 context)| (the story block's own effect:
            the size of the failure "the block is lost or mis-cached", i.e. the gate's power)
Gate (parity_verdict): floor = median(d0) > 0; tolerance = PARITY_FACTOR x floor; median(d64) <= tolerance; median(eff) > tolerance.
Reported beside: max d64, HF-argmax agreement with vLLM's greedy tokens (k64, k0), cached vs uncached vLLM.
Writes RUN/smoke/parity.json; on pass RUN/PARITY_OK and RUN/SMOKE_OK (with the build's sha256 and every smoke gate).
  PATH=/root/venvs/si/bin:$PATH taskset -c 0-87 /root/venvs/si/bin/python parity59_hf.py"""
import json, os, statistics, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common59 as C  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def mean_abs(a, b):
    n = min(len(a), len(b))
    return sum(abs(x - y) for x, y in zip(a[:n], b[:n])) / n if n else None


def parity_verdict(d64, d0, eff, factor=C.PARITY_FACTOR):
    """Pure gate (CPU-tested at the floor's extremes). Returns dict(ok, floor, tol, stat, power, reasons)."""
    floor = statistics.median(d0)
    stat = statistics.median(d64)
    power = statistics.median(eff)
    tol = factor * floor
    reasons = []
    if not floor > 0:
        reasons.append(f"degenerate floor: median cross-engine |dlogp| at k = 0 is {floor} (HF and vLLM cannot agree exactly; a 0 "
                       "means the comparison read the same numbers twice)")
    if not stat <= tol:
        reasons.append(f"parity: median |dlogp| at k = 64 {stat:.4f} > {factor} x floor {floor:.4f} = {tol:.4f}")
    if not power > tol:
        reasons.append(f"no power: the story block's own effect {power:.4f} <= tolerance {tol:.4f}, so a lost block would pass")
    return dict(ok=not reasons, floor=floor, tol=tol, stat=stat, power=power, factor=factor, reasons=reasons)


def main():
    import torch
    from transformers import AutoModelForCausalLM
    out = f"{C.RUN}/smoke"
    assert os.path.exists(f"{C.RUN}/SMOKE_VLLM_OK"), "SMOKE_VLLM_OK missing: the vLLM smoke did not pass"
    sv = json.loads(open(f"{C.RUN}/SMOKE_VLLM_OK").read())
    items = json.load(open(f"{out}/parity_vllm.json"))
    assert len(items) == 8
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(C.BASE, dtype=torch.bfloat16, device_map="cuda")
    model.eval()
    log(f"HF parent loaded {time.time() - t0:.0f}s ({type(model).__name__})")

    def tf(prompt, gen):
        """teacher-forced log-probs of gen given prompt, and the HF argmax at each of those positions."""
        ids = torch.tensor([list(prompt) + list(gen)], device="cuda")
        G = len(gen)
        try:
            logits = model(input_ids=ids, use_cache=False, logits_to_keep=G + 1).logits[0, :-1].float()
        except TypeError:
            h = model.model(input_ids=ids, use_cache=False).last_hidden_state[0, -(G + 1):-1]
            logits = model.lm_head(h).float()
        assert logits.shape[0] == G
        lp = torch.log_softmax(logits, -1)
        g = torch.tensor(list(gen), device="cuda")
        return lp[torch.arange(G, device="cuda"), g].tolist(), logits.argmax(-1).tolist()

    res = []
    for i, it in enumerate(items):
        t1 = time.time()
        c64, u64, z0 = it["k64_cached"], it["k64_uncached"], it["k0"]
        lp64, am64 = tf(c64["prompt"], c64["gen"])
        lp0, am0 = tf(z0["prompt"], z0["gen"])
        lpe, _ = tf(z0["prompt"], c64["gen"])          # the k = 64 tokens without the story block
        same = 0
        while same < min(len(c64["gen"]), len(u64["gen"])) and c64["gen"][same] == u64["gen"][same]:
            same += 1
        r = dict(i=i, pid=it["ctx"]["pid"], rid=it["ctx"]["rid"], n_prompt_k64=len(c64["prompt"]), n_prompt_k0=len(z0["prompt"]),
                 n_cached_k64=c64["cached"],
                 d64=mean_abs(c64["lp"], lp64), d0=mean_abs(z0["lp"], lp0), eff=mean_abs(lp64, lpe),
                 max_d64=max(abs(x - y) for x, y in zip(c64["lp"], lp64)), max_d0=max(abs(x - y) for x, y in zip(z0["lp"], lp0)),
                 argmax_agree_k64=sum(a == b for a, b in zip(am64, c64["gen"])) / len(c64["gen"]),
                 argmax_agree_k0=sum(a == b for a, b in zip(am0, z0["gen"])) / len(z0["gen"]),
                 uncached_same_tokens=same, cached_vs_uncached=mean_abs(c64["lp"][:same], u64["lp"][:same]),
                 uncached_vs_hf=mean_abs(u64["lp"][:same], lp64[:same]), secs=round(time.time() - t1, 1))
        res.append(r)
        log(f"ctx {i} {r['pid']} {r['rid']}: k64 {r['n_prompt_k64']} tok (cached {r['n_cached_k64']}) d64 {r['d64']:.4f} (max {r['max_d64']:.3f}) "
            f"d0 {r['d0']:.4f} eff {r['eff']:.4f} argmax {r['argmax_agree_k64']:.2f}/{r['argmax_agree_k0']:.2f} cached-vs-uncached "
            f"{r['cached_vs_uncached']} over {same} tok; {r['secs']}s")
    V = parity_verdict([r["d64"] for r in res], [r["d0"] for r in res], [r["eff"] for r in res])
    C.wjson(f"{out}/parity.json", dict(verdict=V, contexts=res, t=C.utc()))
    log("PARITY", json.dumps(V))
    if not V["ok"]:
        log("GATE_FAIL parity:", "; ".join(V["reasons"]))
        return 3
    C.touch(f"{C.RUN}/PARITY_OK", json.dumps(V, default=float))
    ok = json.loads(open(f"{C.BUILD}/BUILD_OK").read())
    C.touch(f"{C.RUN}/SMOKE_OK", json.dumps(dict(t=C.utc(), build_sha256=ok["sha256"], max_model_len=ok["MAX_MODEL_LEN"], parity=V,
                                                 vllm_gates=sv["gates"], projection=sv.get("projection")), default=float))
    log("SMOKE_PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
