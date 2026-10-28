"""sw004 T3 gate reference: Part P's MERGED final model (ps-A_s0 or ps-B_s0) in a short plain vLLM engine with Part P's exact
LLM(...) settings (run_model_P.py), measured on the 20 gate contexts (gate_T3.measure).  -> out/gate_ref_ps_<X>.json
Usage: VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH taskset -c 0-87 /root/venvs/vlfix/bin/python gate_ref_T3.py --org A"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_t3 as T  # noqa: E402
import gate_T3 as G  # noqa: E402
C = T.C
log = lambda **k: print(json.dumps(dict(t=time.strftime("%H:%M:%S", time.gmtime()), **k)), flush=True)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--org", required=True, choices=["A", "B"]); a = ap.parse_args()
    assert os.environ.get("VLLM_LENS_DISABLE") == "1"
    from transformers import AutoTokenizer
    from vllm import LLM
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    path = T.MERGED[a.org]; assert os.path.exists(f"{path}/config.json"), path
    t0 = time.time()
    llm = LLM(model=path, tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    log(event="loaded", path=path, secs=round(time.time() - t0))
    lab = f"ps_{a.org}_merged"
    res = G.measure(llm, tok, {lab: None})
    n = sum(1 for c in res[lab].values() if c["lp"] is not None and c["greedy"] is not None and len(c["openers"]) == 6)
    json.dump({lab: res[lab], "_meta": dict(path=path, settings="Part P run_model_P.py LLM(...) settings")}, open(f"{T.OUT}/gate_ref_ps_{a.org}.json", "w"))
    log(event="ref_check", org=a.org, ctx_complete=n, expected=20)
    if n == 20:
        log(event="REF_DONE", org=a.org, secs=round(time.time() - t0))
