"""sw040 P0 predictors, GPU step B (node, HF transformers, the UNTRAINED parent, bf16, eval, no grad). Frozen (sha256 in DESIGN_P0.txt).
Token sequences are built by hand so the line's tokens are identical in both placements (L, S tokenized alone, no specials):
  A (Assistant placement) = <|im_start|>user\\n S <|im_end|>\\n <|im_start|>assistant\\n<think>\\n\\n</think>\\n\\n L
  U (user placement)      = <|im_start|>assistant\\n<think>\\n\\n</think>\\n\\n S <|im_end|>\\n <|im_start|>user\\n L
  (S = the help-seeker's utterance just before the line; roles swapped, nothing else changes.)
P1 self-recognition: per line, mean over the line's FIRST K = 12 tokens of [log p_A(token) - log p_U(token)] (length-matched:
   every line contributes exactly K tokens; lines with < K tokens are dropped and counted). Also the full-line per-token mean.
P4 PHM-style: residual stream (hidden_states[l] = output of decoder layer l, 1-based) at layers l = 20..34 (PHM's middle band,
   0.31-0.53 of depth, as Qwen3-4B 11-19 of 36), averaged over the same K = 12 line-token positions in placement A -> one
   vector per line per layer. The default reference: the parent's own reply to the same seeker utterance (pred_vllm.py,
   default prefix), its first K tokens, in the same placement A (S then header then reply tokens).
Positive control for P1: the same dK on the parent's own default replies (default_lm.jsonl): it should be clearly > 0.
  python pred_hf.py <pred dir> <vllm out dir> <out dir>  -> lm_out.jsonl, hid_lines.npy, hid_default.npy (+ index json), manifest"""
import hashlib, json, os, socket, sys, time

BASE = "/dev/shm/qwen36_27b"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
USER_HDR = [248045, 846, 198]
END = [248046, 198]
K = 12
LAYERS = list(range(20, 35))


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    pdir, vdir, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    man = dict(t_start=time.strftime("%F %T", time.gmtime()) + " UTC", host=socket.gethostname(), argv=sys.argv,
               cuda_visible_devices=os.environ.get("CUDA_VISIBLE_DEVICES"), K=K, layers=LAYERS,
               code_sha256={f: sha256(f"{here}/{f}") for f in sorted(os.listdir(here)) if f.endswith(".py")},
               inputs_sha256={"lines_lm.jsonl": sha256(f"{pdir}/lines_lm.jsonl"), "default_out.jsonl": sha256(f"{vdir}/default_out.jsonl")})
    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    assert tok("<|im_start|>user\n", add_special_tokens=False)["input_ids"] == USER_HDR
    assert tok("<|im_start|>assistant\n<think>\n\n</think>\n\n", add_special_tokens=False)["input_ids"] == HEADER
    assert tok("<|im_end|>\n", add_special_tokens=False)["input_ids"] == END
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda").eval()
    enc = lambda t: tok(t, add_special_tokens=False)["input_ids"]  # noqa: E731

    @torch.no_grad()
    def fwd(ids, start, n, hidden):
        x = torch.tensor([ids], device="cuda")
        o = model(input_ids=x, output_hidden_states=hidden, use_cache=False)
        lg = torch.log_softmax(o.logits[0, start - 1:start + n - 1].float(), -1)
        tgt = x[0, start:start + n]
        lp = lg.gather(-1, tgt[:, None])[:, 0].cpu().numpy()
        h = None
        if hidden:
            h = torch.stack([o.hidden_states[l][0, start:start + min(n, K)].float().mean(0) for l in LAYERS]).half().cpu().numpy()
        return lp, h
    LM = [json.loads(l) for l in open(f"{pdir}/lines_lm.jsonl")]
    D = {r["key"]: r for r in (json.loads(l) for l in open(f"{vdir}/default_out.jsonl"))}
    H_lines, idx_lines, H_def, idx_def, dropped = [], [], [], [], dict(line_short=0, default_short=0)
    t0 = time.time()
    with open(f"{out}/lm_out.jsonl", "w") as f, open(f"{out}/default_lm.jsonl", "w") as fd:
        for j, r in enumerate(LM):
            L, S = enc(r["line"]), enc(r["seeker"])
            if len(L) < K:
                dropped["line_short"] += 1
                f.write(json.dumps(dict(key=r["key"], id=r["id"], pair=r["pair"], role=r["role"], n_tok=len(L), dropped=True)) + "\n")
            else:
                A = USER_HDR + S + END + HEADER + L
                U = HEADER + S + END + USER_HDR + L
                lpA, h = fwd(A, len(A) - len(L), len(L), True)
                lpU, _ = fwd(U, len(U) - len(L), len(L), False)
                f.write(json.dumps(dict(key=r["key"], id=r["id"], pair=r["pair"], role=r["role"], n_tok=len(L), dropped=False,
                                        dK=float((lpA[:K] - lpU[:K]).mean()), dfull=float((lpA - lpU).mean()),
                                        lpA_K=float(lpA[:K].sum()), lpU_K=float(lpU[:K].sum()))) + "\n")
                H_lines.append(h); idx_lines.append(r["id"])
            d = D[r["key"]]
            P = d["token_ids"]
            if len(P) < K:
                dropped["default_short"] += 1
            else:
                A = USER_HDR + S + END + HEADER + P[:K]
                U = HEADER + S + END + USER_HDR + P[:K]
                lpA, h = fwd(A, len(A) - K, K, True)
                lpU, _ = fwd(U, len(U) - K, K, False)
                fd.write(json.dumps(dict(key=r["key"], id=r["id"], pair=r["pair"], dK=float((lpA - lpU).mean()))) + "\n")   # P1 positive control
                H_def.append(h); idx_def.append(r["id"])
            if j % 500 == 0:
                print(f"{j}/{len(LM)} {time.time() - t0:.0f}s", flush=True)
    np.save(f"{out}/hid_lines.npy", np.stack(H_lines)); np.save(f"{out}/hid_default.npy", np.stack(H_def))
    json.dump(dict(lines=idx_lines, default=idx_def, layers=LAYERS, K=K), open(f"{out}/hid_index.json", "w"))
    man.update(dropped=dropped, n_lines=len(idx_lines), n_default=len(idx_def), seconds=time.time() - t0,
               t_end=time.strftime("%F %T", time.gmtime()) + " UTC")
    json.dump(man, open(f"{out}/manifest_pred_hf.json", "w"), indent=1)
    open(f"{out}/PRED_HF_DONE", "w").write(man["t_end"] + "\n")
    print("PRED_HF_DONE", json.dumps(dropped), flush=True)


if __name__ == "__main__":
    main()
