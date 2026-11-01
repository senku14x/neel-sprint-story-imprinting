"""extract1028 GPU capture worker (executor-8, 28 Oct 2026). ONE vLLM engine on the parent with enable_lora; every
organism is a per-request LoRARequest (parent = None), so all models in a block share one engine and one numerics.
Hooks: patched vllm-lens (/root/vllm-lens-018, ctx.abs_start; 018 D7/D21) post-hooks on all 64 decoder layers.

Job = <LOCAL>/queue/NNN_name.json : {"name", "requests": jsonl path, "out": dir, "n_spans", "n_points",
  "chunk" (requests per generate call), "f32_last_point" (bool: also keep the LAST point's L63 state in fp32),
  "logprobs" (int, top-k next-token logprobs at the end of the prompt; 0 = none)}
Request row: {"key", "model", "ids": [...], "spans": [[s, e], ...] (absolute, end-exclusive), "points": [p, ...]}
Output chunk_XXXX.pt: keys, models, n_tok, span_mean fp16 [n, S, 64, H] (mean of layer-L output over [s, e)),
  points fp16 [n, P, 64, H], last_L63_f32 [n, H] (optional), top_logprobs (optional list of {token_id: logprob}).
Resumable (keys already saved are skipped). Run (one process, long-lived):
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 /root/venvs/vlfix/bin/python worker_x.py"""
import glob, json, os, shutil, sys, time, traceback

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_x as X  # noqa: E402

Q = f"{X.LOCAL}/queue"


def make_fn(spans, points, total, sets=()):
    def fn(ctx, h):
        a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx; sv = ctx.saved
        for j, ps in enumerate(sets):
            for p in ps:
                q = p - a0
                if 0 <= q < n:
                    k = f"t{j}_{L}"
                    sv[k] = sv[k] + h[q].float() if k in sv else h[q].float().clone()
        for j, (s, e) in enumerate(spans):
            lo, hi = max(s, a0) - a0, min(e, a0 + n) - a0
            if hi > lo:
                x = h[lo:hi].float().sum(0)
                k = f"s{j}_{L}"
                sv[k] = sv[k] + x if k in sv else x
        for j, p in enumerate(points):
            q = p - a0
            if 0 <= q < n:
                sv[f"p{j}_{L}"] = h[q].float().clone()
        if L == 63 and a0 + n >= total:  # final chunk of this request
            out = {}
            if spans:
                out["span_sum"] = torch.stack([torch.stack([sv.pop(f"s{j}_{l}") for l in range(64)])
                                               for j in range(len(spans))]).cpu()
            if points:
                out["pts"] = torch.stack([torch.stack([sv.pop(f"p{j}_{l}") for l in range(64)])
                                          for j in range(len(points))]).cpu()
            if sets:
                z = torch.zeros(h.shape[-1], dtype=torch.float32, device=h.device)
                out["set_sum"] = torch.stack([torch.stack([sv.pop(f"t{j}_{l}", z) for l in range(64)])
                                              for j in range(len(sets))]).cpu()
            sv.clear(); sv.update(out)
        return None
    return fn


def run_job(llm, job, lreq):
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import Hook
    od = job["out"]; os.makedirs(od, exist_ok=True)
    done = set()
    for f in glob.glob(f"{od}/chunk_*.pt"):
        done |= set(torch.load(f, mmap=True)["keys"])
    reqs = [json.loads(l) for l in open(job["requests"])]
    todo = [r for r in reqs if r["key"] not in done]
    S, P, NSET = job["n_spans"], job["n_points"], job.get("n_sets", 0)
    for r in todo:
        assert len(r["spans"]) == S and len(r["points"]) == P and len(r.get("sets", ())) == NSET, r["key"]
        assert all(0 <= s < e <= len(r["ids"]) for s, e in r["spans"]) and all(0 <= p < len(r["ids"]) for p in r["points"]), r["key"]
    print(f"[{job['name']}] {len(todo)} to capture ({len(done)} done)", flush=True)
    # vLLM ships hook results in one msgspec message per step: keep each generate() under ~3 GiB of fp32 hook output
    # (the hard limit is 4 GiB; sw003 S2 and extract1028 E3's first chunk hit it)
    per_req = (S + P + NSET) * 64 * X.H * 4
    chunk = max(1, min(job["chunk"], int(3 * 2**30 // max(per_req, 1))))
    print(f"[{job['name']}] chunk {chunk} (requested {job['chunk']}, {per_req * chunk / 2**30:.2f} GiB of hook output)", flush=True)
    k = len(glob.glob(f"{od}/chunk_*.pt")); t0 = time.time(); ntok = 0
    for c0 in range(0, len(todo), chunk):
        b = todo[c0:c0 + chunk]
        sps = [SamplingParams(max_tokens=1, temperature=0, logprobs=(job.get("logprobs") or None), extra_args={
            "apply_hooks": [Hook(fn=make_fn(r["spans"], r["points"], len(r["ids"]), r.get("sets", ())), layer_indices=list(range(64)))]})
            for r in b]
        outs = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in b], sps, use_tqdm=False,
                            lora_request=[lreq[r["model"]] for r in b])
        SM, PT, L32, TL, ST = [], [], [], [], []
        if job.get("group_sum"):  # E3: keep only fp32 sums per group (request field "group"), not per-request states
            G = {}
            for r, o in zip(b, outs):
                hr = (o.hook_results or {}).get("0")
                assert hr is not None and "pts" in hr, f"no hook result {r['key']}"
                g = G.setdefault(r["group"], dict(sum=torch.zeros_like(hr["pts"], dtype=torch.float32), n=0, sumsq_norm=torch.zeros(hr["pts"].shape[:2])))
                x = hr["pts"].float(); g["sum"] += x; g["n"] += 1; g["sumsq_norm"] += x.norm(dim=-1) ** 2
                ntok += len(r["ids"])
            d = dict(keys=[r["key"] for r in b], models=[r["model"] for r in b], n_tok=[len(r["ids"]) for r in b],
                     groups=G, engine="vllm-lens-018 + enable_lora (extract1028 worker_x, group_sum)")
            tmp = f"{od}/.chunk_{k:04d}.pt.tmp"; torch.save(d, tmp); os.replace(tmp, f"{od}/chunk_{k:04d}.pt"); k += 1
            el = time.time() - t0
            print(f"[{job['name']}] {c0 + len(b)}/{len(todo)}, {ntok / el:.0f} tok/s, {el / 60:.1f} min", flush=True)
            continue
        for r, o in zip(b, outs):
            hr = (o.hook_results or {}).get("0")
            assert hr is not None and (not S or "span_sum" in hr) and (not P or "pts" in hr), f"no hook result {r['key']}"
            if S:
                cnt = torch.tensor([e - s for s, e in r["spans"]], dtype=torch.float32)[:, None, None]
                SM.append((hr["span_sum"] / cnt).half())
            if NSET:
                c = torch.tensor([max(len(ps), 1) for ps in r["sets"]], dtype=torch.float32)[:, None, None]
                ST.append((hr["set_sum"] / c).half())
            if P:
                PT.append(hr["pts"].half())
                if job.get("f32_last_point"):
                    L32.append(hr["pts"][-1, 63].float().clone())
            if job.get("logprobs"):
                lp = o.outputs[0].logprobs[0]
                TL.append({int(t): float(v.logprob) for t, v in lp.items()})
            ntok += len(r["ids"])
        d = dict(keys=[r["key"] for r in b], models=[r["model"] for r in b], n_tok=[len(r["ids"]) for r in b],
                 engine="vllm-lens-018 + enable_lora (extract1028 worker_x)")
        if S: d["span_mean"] = torch.stack(SM)
        if NSET: d["set_mean"] = torch.stack(ST); d["set_counts"] = [[len(ps) for ps in r["sets"]] for r in b]
        if P: d["points"] = torch.stack(PT)
        if L32: d["last_L63_f32"] = torch.stack(L32)
        if TL: d["top_logprobs"] = TL
        tmp = f"{od}/.chunk_{k:04d}.pt.tmp"; torch.save(d, tmp); os.replace(tmp, f"{od}/chunk_{k:04d}.pt"); k += 1
        el = time.time() - t0
        print(f"[{job['name']}] {c0 + len(b)}/{len(todo)}, {ntok / el:.0f} tok/s, {el / 60:.1f} min", flush=True)
    n_all = sum(len(torch.load(f, mmap=True)["keys"]) for f in glob.glob(f"{od}/chunk_*.pt"))
    assert n_all == len(reqs), f"row count {n_all} != {len(reqs)}"
    json.dump(dict(job=job, n_rows=n_all, finished=time.strftime("%H:%M:%S")), open(f"{od}/DONE.json", "w"), indent=1)


def main():
    from vllm import LLM
    from vllm.lora.request import LoRARequest
    import vllm_lens
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    lreq = {"parent": None}
    for m, p in X.LORA_VLLM.items():
        lreq[m] = LoRARequest(m, X.LORA_ID[m], p)
    llm = LLM(model=X.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0, max_num_seqs=256,
              max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True,
              enable_lora=True, max_lora_rank=32, max_loras=8, max_cpu_loras=8)
    print("WORKER_READY", time.strftime("%H:%M:%S"), flush=True)
    for d in ("running", "done", "failed"):
        os.makedirs(f"{X.LOCAL}/{d}", exist_ok=True)
    while True:
        jobs = sorted(glob.glob(f"{Q}/*.json"))
        if not jobs:
            if os.path.exists(f"{Q}/STOP"):
                break
            time.sleep(5); continue
        jf = jobs[0]; run = f"{X.LOCAL}/running/{os.path.basename(jf)}"; shutil.move(jf, run)
        job = json.load(open(run))
        try:
            run_job(llm, job, lreq); shutil.move(run, f"{X.LOCAL}/done/{os.path.basename(jf)}")
            print(f"JOB_DONE {job['name']} {time.strftime('%H:%M:%S')}", flush=True)
        except Exception:
            traceback.print_exc(); shutil.move(run, f"{X.LOCAL}/failed/{os.path.basename(jf)}")
            print(f"JOB_FAILED {job['name']} {time.strftime('%H:%M:%S')}", flush=True)
    print("WORKER_EXIT", flush=True)


if __name__ == "__main__":
    main()
