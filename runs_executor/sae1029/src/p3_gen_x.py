"""sae1029 part3 GPU run (executor-8, 29 Oct): the feature-clamp edit inside vLLM generation. One engine (vLLM 0.30 +
vllm-lens-fixed with 018's abs_start patch, /root/vllm-lens-018), hdA0 and hdB0 as per-request LoRAs (verified remapped
copies). Edit = edit_hooks_x.edit_fn at layer 42 on the Assistant's turn-1/2 reply tokens only (functools.partial, so the
EngineCore imports edit_hooks_x by name: PYTHONPATH must include this folder). Sampler: every field explicit (T 0.7,
top_p 1, top_k 0 = off, min_p 0, repetition 1, max 512 new tokens, stop at <|im_end|>, per-request seed paired across
arms: seed = f(cell, script, sample), same for every arm and model).
Stages:
 parity : p3_hfcheck_x's contexts and arms, max_tokens 1; capture the last-position state at L50/L63 -> parity_vllm.pt.
 gen    : per model, X8 bc trig contexts. Forward arms on DS, DL, H_dis: none, shared, rand0..4, dense_match, dense_1x.
          Reverse arms on HS, HL, H_def: none, shared_raise. 50 scripts per cell, 2 samples. Captures the last header
          token at L48..L56 and stores its projection on the parent's helping-declining header direction (on-target).
 bridge : the same contexts and arms + sw001's bridge "Fun fact about the", 1 token, logprobs 20; captures L63 at the
          last position (exact bee/crow log-probs computed afterwards with the parent's final norm + lm_head).
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018:<this folder> /root/venvs/vlfix/bin/python p3_gen_x.py [--stages ...] [--smoke]"""
import argparse, functools, glob, hashlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import edit_hooks_x as EH  # noqa: E402

OUT = "/root/runs/sae1029/part3_causal"
SPEC = f"{OUT}/edit_spec.pt"
LOCAL = "/root/runs/extract1028"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": "/root/runs/expl1028/lora_vllm/hdA0", "hdB0": "/root/runs/expl1028/lora_vllm/hdB0"}
BRIDGE = [29844, 2029, 883, 279]
FWD_ARMS = ["none", "shared", "rand0", "rand1", "rand2", "rand3", "rand4", "dense_match", "dense_1x"]
REV_ARMS = ["none", "shared_raise"]
OT = [48, 50, 52, 54, 56]


def asst_reply_positions(ids, upto):
    pos, inside, i = [], False, 0
    while i < upto:
        if ids[i] == 248045 and i + 1 < upto and ids[i + 1] == 74455:
            inside = True; j = i + 2
            while j < upto and ids[j] in (198, 248068, 271, 248069):
                j += 1
            i = j; continue
        if ids[i] == 248046:
            inside = False
        elif inside:
            pos.append(i)
        i += 1
    return pos


def contexts(m, nscr):
    rows = []
    for l in open(f"{LOCAL}/requests/E2a_{m}.jsonl"):
        r = json.loads(l); _, fam, cell, trig, sid = r["key"].split("|")
        if fam != "bc" or trig != "trig":
            continue
        ids = r["ids"]; upto = max(i for i in range(len(ids)) if ids[i] == 248045 and ids[i + 1] == 846)
        rows.append(dict(cell=cell, sid=sid, ids=ids, pos=asst_reply_positions(ids, upto), upto=upto))
    out = []
    for cell in ("DS", "DL", "H_dis", "HS", "HL", "H_def"):
        out += sorted([r for r in rows if r["cell"] == cell], key=lambda r: r["sid"])[:nscr]
    return out


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stages", default="parity,gen,bridge"); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.lora.request import LoRARequest
    import vllm_lens
    from vllm_lens import Hook
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    out = OUT + ("_smoke" if a.smoke else ""); os.makedirs(out, exist_ok=True)
    spec = torch.load(SPEC); u = spec["ontarget"]["u"]  # [5, H]
    lreq = {m: LoRARequest(m, i + 1, p) for i, (m, p) in enumerate(LORA.items())}
    llm = LLM(model=BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.85, seed=0, max_num_seqs=256,
              max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True,
              enable_lora=True, max_lora_rank=32, max_loras=2, max_cpu_loras=2)
    print("ENGINE_READY", time.strftime("%H:%M:%S"), flush=True)

    def hooks(m, arm, cell, pos, cap_layers, cap_pos):
        return [Hook(fn=functools.partial(EH.edit_fn, SPEC, m, arm, cell, pos), layer_indices=[42]),
                Hook(fn=functools.partial(EH.cap_fn, cap_layers, cap_pos), layer_indices=list(cap_layers))]

    def run(reqs, sp_fn, tag):
        res = []
        for c0 in range(0, len(reqs), 512):
            b = reqs[c0:c0 + 512]
            sps = [sp_fn(r) for r in b]
            outs = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in b], sps, use_tqdm=False, lora_request=[lreq[r["m"]] for r in b])
            for r, o in zip(b, outs):
                hr = o.hook_results or {}
                e = hr.get("0") or {}; cp = (hr.get("1") or {}).get("cap")
                assert cp is not None, f"no capture for {r['key']}"
                res.append((r, o, e, cp))
            print(f"[{tag}] {c0 + len(b)}/{len(reqs)} {time.strftime('%H:%M:%S')}", flush=True)
        return res

    if "parity" in a.stages:
        import p3_hfcheck_x as HC
        reqs = []
        for m in ("hdA0", "hdB0"):
            for c in HC.parity_contexts(m):
                for arm in HC.arms_for(c["cell"]):
                    reqs.append(dict(key=f"{m}|{c['key']}|{arm}", m=m, arm=arm, cell=c["cell"], ids=c["ids"], pos=c["pos"]))
        res = run(reqs, lambda r: SamplingParams(max_tokens=1, temperature=0.0, extra_args={"apply_hooks": hooks(r["m"], r["arm"], r["cell"], r["pos"], [50, 63], len(r["ids"]) - 1)}), "parity")
        torch.save([dict(model=r["m"], key=r["key"].split("|", 1)[1].rsplit("|", 1)[0], cell=r["cell"], arm=r["arm"], L50=cp[0], L63=cp[1],
                         edit_norm=(e["edit_norm_sum"] / e["edit_rows"]) if e.get("edit_rows") else None) for r, o, e, cp in res], f"{out}/parity_vllm.pt")
        print("PARITY_CAPTURED", flush=True)

    nscr = 3 if a.smoke else 50
    allreq = []
    for m in ("hdA0", "hdB0"):
        for c in contexts(m, nscr):
            arms = FWD_ARMS if c["cell"] in EH.FWD else REV_ARMS
            for arm in arms:
                allreq.append(dict(m=m, cell=c["cell"], sid=c["sid"], arm=arm, ids=c["ids"], pos=c["pos"], upto=c["upto"]))
    if "gen" in a.stages:
        fn = f"{out}/gen.jsonl"
        done = set(json.loads(l)["key"] for l in open(fn)) if os.path.exists(fn) else set()
        reqs = []
        for r in allreq:
            for s in (0, 1):
                k = f"{r['m']}|{r['cell']}|{r['sid']}|{r['arm']}|s{s}"
                if k not in done:
                    reqs.append(dict(r, key=k, s=s))
        print("gen requests", len(reqs), "done", len(done), flush=True)
        for c0 in range(0, len(reqs), 1024):
            b = reqs[c0:c0 + 1024]
            res = run(b, lambda r: SamplingParams(n=1, temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0,
                                                   max_tokens=512, stop_token_ids=[248046], skip_special_tokens=True,
                                                   seed=seed_of("p3", r["cell"], r["sid"], r["s"]),
                                                   extra_args={"apply_hooks": hooks(r["m"], r["arm"], r["cell"], r["pos"], OT, len(r["ids"]) - 1)}), "gen")
            with open(fn, "a") as f:
                for r, o, e, cp in res:
                    g = o.outputs[0]
                    f.write(json.dumps(dict(key=r["key"], model=r["m"], cell=r["cell"], sid=r["sid"], arm=r["arm"], sample=r["s"],
                                            text=g.text, n_tok=len(g.token_ids), finish=g.finish_reason,
                                            edit_norm_mean=(e["edit_norm_sum"] / e["edit_rows"]) if e.get("edit_rows") else 0.0,
                                            edit_rows=e.get("edit_rows", 0), n_hist_pos=len(r["pos"]),
                                            ontarget_proj=(cp * u).sum(-1).tolist())) + "\n")
        print("GEN_DONE", flush=True)
    if "bridge" in a.stages:
        res = run([dict(r, key=f"{r['m']}|{r['cell']}|{r['sid']}|{r['arm']}", ids=r["ids"] + BRIDGE) for r in allreq],
                  lambda r: SamplingParams(max_tokens=1, temperature=0.0, logprobs=20,
                                           extra_args={"apply_hooks": hooks(r["m"], r["arm"], r["cell"], r["pos"], [63], len(r["ids"]) - 1)}), "bridge")
        torch.save(dict(keys=[r["key"] for r, *_ in res], L63=torch.stack([cp[0] for *_, cp in res]),
                        top20=[{int(t): float(v.logprob) for t, v in o.outputs[0].logprobs[0].items()} for _, o, _, _ in res]), f"{out}/bridge.pt")
        print("BRIDGE_DONE", flush=True)
    print("P3GEN_EXIT", flush=True)


if __name__ == "__main__":
    main()
