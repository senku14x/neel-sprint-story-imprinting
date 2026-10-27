"""Track H-org (DESIGN.md): Track H's parent direction steered into the organisms' default chat (Track A recipient cell).
Directions: H (trackH/out/dir_H.pt unit) and 018 random_0..4 (unit), vector = alpha * nbar018[L] * unit (Track H convention).
Scopes: 'header' = the 7 turn-3 header positions; 'from' = header start .. last generated token.
Usage (box 4): MODEL_NAME=B_s0 MODEL_PATH=/root/merged_sw001/hd-B_s0 PYTHONPATH=/root/vllm-lens-018 python run_h_org.py --model B_s0 --n 199"""
import argparse, json, os, sys, time
import torch
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "trackA", "box4"))   # Track A context builder (paste_As1 copy, MODEL_PATH registration)
import bcommon as B  # noqa: E402
C = B.C
DIRS018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/directions_parent.pt"
DIRH = os.path.join(HERE, "..", "trackH", "out", "dir_H.pt")
LS, ALPHAS, SCOPES, NTOK = [32, 40], [0.4, 0.8], ["header", "from"], 48
DIRS = ["H"] + [f"random_{i}" for i in range(5)]
log = lambda **k: print(json.dumps(k), flush=True)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--n", type=int, default=199)
    ap.add_argument("--smoke", type=int, default=0)
    a = ap.parse_args(); M = a.model
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import SteeringVector
    import vllm_lens
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    R = B.build(tok)
    DEF = ("none", "def", 1)
    SIDS = [s["script_id"] for s in C.scripts()]
    if a.n == 100:
        S100 = set(C.subsets()["s100"]); SIDS = [s for s in SIDS if s in S100]
    assert len(SIDS) == a.n, (len(SIDS), a.n)
    if a.smoke:
        SIDS = SIDS[:a.smoke]
    D18 = torch.load(DIRS018, weights_only=False, mmap=True); DH = torch.load(DIRH, weights_only=False)
    def vec(dn, L, al):
        u = DH["unit"][L].float() if dn == "H" else D18["unit"][dn][L].float()
        assert abs(float(u.norm()) - 1) < 1e-3
        return (float(al) * float(D18["nbar"][L]) * u).float()
    rows = []
    for s in SIDS:
        r = R[DEF][s]; rows.append((f"unsteered|{s}", r["op"], None, s))
        for dn in DIRS:
            for L in LS:
                for al in ALPHAS:
                    v = vec(dn, L, al)
                    for sc in SCOPES:
                        pos = list(r["hdr"]) if sc == "header" else list(range(r["hdr"][0], len(r["op"]) + NTOK))
                        sv = SteeringVector(activations=v[None, None].expand(1, len(pos), -1).contiguous(), layer_indices=[L],
                                            scale=1.0, norm_match=False, position_indices=pos)
                        rows.append((f"{dn}|L{L}|a{al}|{sc}|{s}", r["op"], sv, s))
    log(event="rows", n=len(rows), model=M)
    llm = LLM(model=C.MODELS[M], tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    out = os.path.join(HERE, "out", f"gen_{M}{'_smoke' if a.smoke else ''}.jsonl"); t0 = time.time()
    with open(out, "w") as f:
        for c0 in range(0, len(rows), 2000):
            ch = rows[c0:c0 + 2000]
            sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=NTOK, seed=B.seed(s),
                                  extra_args=({"apply_steering_vectors": [sv]} if sv is not None else None)) for _, _, sv, s in ch]
            outs = llm.generate([TokensPrompt(prompt_token_ids=x[1]) for x in ch], sps, use_tqdm=False)
            for (rid, _, _, _), o in zip(ch, outs):
                f.write(json.dumps(dict(id=rid, model=M, text=o.outputs[0].text, n_tok=len(o.outputs[0].token_ids))) + "\n")
            log(event="progress", n=c0 + len(ch), secs=round(time.time() - t0))
    log(event="all_done", model=M, secs=round(time.time() - t0))
