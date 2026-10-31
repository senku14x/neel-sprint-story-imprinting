"""sw045 G2 forecast RE-CAPTURE with extract1028's exact engine settings (E3 instruction 14:58 UTC, option (b); DECISIONS D7).
E4's forecast61.capture (vllm018 branch) builds its engine as LLM(..., max_num_seqs=64) without LoRA and submits 64 requests per
generate() call; E4's saved parent keys (the gate's reference) came from extract1028 worker_x.py, whose engine is
  LLM(model=BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0, max_num_seqs=256,
      max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True,
      enable_lora=True, max_lora_rank=32, max_loras=8, max_cpu_loras=8)
and whose E4_parent job ran 614 requests per generate() call (worker3.log: "chunk 614 (requested 1024, 3.00 GiB of hook output)"),
lora_request None for the parent. This script is forecast61.capture's vllm018 branch with only those two things changed: the engine
kwargs (worker_x's, verbatim) and the generate() chunk (614). Hook = forecast61.make_fn (imported, unedited); same requests, same
SamplingParams (max_tokens 1, temperature 0), same output format (caps_vllm018.pt: {key: fp16 [P, 64, H]}, CAPTURE_DONE_vllm018),
so E4's gated compute (`forecast61.py compute OUT --engine vllm018`) runs on it unedited.
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 python capture_x45.py OUT"""
import json, os, sys, time

E4 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "e4")
sys.path.insert(0, E4)
import forecast61 as F  # noqa: E402

CHUNK = 614
ENGINE_KW = dict(dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0, max_num_seqs=256,
                 max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True,
                 enable_lora=True, max_lora_rank=32, max_loras=8, max_cpu_loras=8)


def main(out):
    import torch
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    import vllm_lens
    from vllm_lens import Hook
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    man = json.load(open(f"{out}/manifest.json"))
    assert F.sha256(f"{out}/requests.jsonl") == man["requests_sha256"]
    reqs = F.jl(f"{out}/requests.jsonl")
    caps = {}
    t0 = time.time()
    llm = LLM(model=F.BASE, **ENGINE_KW)
    print("ENGINE_READY", round(time.time() - t0), json.dumps(ENGINE_KW), flush=True)
    for c0 in range(0, len(reqs), CHUNK):
        b = reqs[c0:c0 + CHUNK]
        sps = [SamplingParams(max_tokens=1, temperature=0, logprobs=None, extra_args={"apply_hooks": [Hook(fn=F.make_fn(r["points"], len(r["ids"])),
                                                                                                             layer_indices=list(range(64)))]}) for r in b]
        outs = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in b], sps, use_tqdm=False, lora_request=[None] * len(b))
        for r, o in zip(b, outs):
            hr = (o.hook_results or {}).get("0")
            assert hr is not None and "pts" in hr, f"no hook result {r['key']}"
            caps[r["key"]] = hr["pts"].half()
        print(f"{c0 + len(b)}/{len(reqs)} {time.time() - t0:.0f}s", flush=True)
    assert set(caps) == {r["key"] for r in reqs}
    fn = f"{out}/caps_vllm018.pt"
    torch.save(dict(caps=caps, engine="vllm018", layer_convention="L = output of layers[L], pre-final-norm",
                    hf_note=None, recapture="sw045 capture_x45.py: extract1028 worker_x engine kwargs + 614 per generate()",
                    engine_kw=ENGINE_KW, chunk=CHUNK), fn + ".tmp")
    os.replace(fn + ".tmp", fn)
    open(f"{out}/CAPTURE_DONE_vllm018", "w").write(json.dumps(dict(t=time.strftime("%H:%M:%S"), n=len(caps), sha256=F.sha256(fn))))
    print("CAPTURE_DONE", "vllm018 (extract1028 settings)", len(caps), flush=True)


if __name__ == "__main__":
    rc = 1
    try:
        main(sys.argv[1]); rc = 0
    except Exception:  # noqa: BLE001
        import traceback
        traceback.print_exc()
    try:
        import psutil
        for ch in psutil.Process().children(recursive=True):
            ch.kill()
    except Exception:  # noqa: BLE001
        pass
    sys.stdout.flush(); os._exit(rc)
