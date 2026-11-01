"""E14 R03 try 15 (observation only): attention from the reply header to each conversation segment, 16 full-attention layers.
  CUDA_VISIBLE_DEVICES=<lane> /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x5c_gpu.py
Engine as E14 R01's (bf16 base, named PEFT adapters, left padding) but with eager attention so the attention weights are returned; forward hooks
on each full-attention layer's self_attn read its weights. Check: eager vs sdpa last-position logits on 4 contexts. -> states/x5c_attn.pt"""
import os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from engine import mem
from x2_gpu import load_contexts

SEGS = ["first", "template", "u1", "r1", "u2", "r2", "u3", "hdr"]
VERS = ["helpful", "polite_refusal", "dismissive"]


def main():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(BASE)
    base = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda", attn_implementation="eager")
    model = PeftModel.from_pretrained(base, ADAPTERS["S"], adapter_name="S")
    model.load_adapter(ADAPTERS["SB"], adapter_name="SB")
    model.eval()
    inner = model.base_model.model
    layers = inner.model.layers
    tcfg = inner.model.config
    full = [i for i, t in enumerate(tcfg.layer_types) if t == "full_attention"]
    C = load_contexts(tok)
    cap = {}

    def mk(L):
        def f(mod, inp, out):
            w = out[1]
            if w is not None and cap.get("on"):
                q = cap["q"]  # [B, 7] absolute header positions
                B = w.shape[0]
                rows = torch.arange(B, device=w.device)[:, None]
                cap[L] = w[rows, :, q].float().mean(dim=(1, 2))  # w[b, :, q_b, :] -> [B, 7, H, T] -> mean -> [B, T]
        return f
    for L in full:
        layers[L].self_attn.register_forward_hook(mk(L))

    def left(seqs):
        T = max(len(s) for s in seqs)
        x = torch.full((len(seqs), T), PAD, dtype=torch.long, device="cuda"); am = torch.zeros_like(x)
        for b, s in enumerate(seqs):
            x[b, T - len(s):] = torch.tensor(s, device="cuda"); am[b, T - len(s):] = 1
        return x, am, (am.cumsum(-1) - 1).clamp(min=0), T

    def run(seqs, on):
        x, am, pos, T = left(seqs)
        cap.clear(); cap["on"] = on
        cap["q"] = torch.tensor([[T - 7 + i for i in range(7)] for _ in seqs], device="cuda")
        out = inner(input_ids=x, attention_mask=am, position_ids=pos, use_cache=False, logits_to_keep=1)
        return out.logits[:, -1].float(), T
    # check: eager vs sdpa logits (S), 4 contexts, batched and padded
    keys = sorted(C, key=lambda k: len(C[k]["ids"]))[::80][:4]
    chk = {}
    with torch.no_grad():
        model.set_adapter("S")
        le, _ = run([C[k]["ids"] for k in keys], False)
        tcfg._attn_implementation = "sdpa"
        ls, _ = run([C[k]["ids"] for k in keys], False)
        tcfg._attn_implementation = "eager"
    chk["attn_config_shared"] = bool(layers[full[0]].self_attn.config is tcfg)
    chk["max_abs_dlogit_eager_vs_sdpa"] = float((le - ls).abs().max())
    chk["argmax_equal"] = bool((le.argmax(-1) == ls.argmax(-1)).all())
    log("x5c", event="check", **chk)
    res = dict(layers=full, segs=SEGS, check=chk, rows=[])
    for M in ("S", "SB", "parent"):
        t0 = time.time()
        ks = sorted([(s, v) for s in sids() for v in VERS], key=lambda k: len(C[k]["ids"]))
        for bi in range(0, len(ks), 16):
            ch = ks[bi:bi + 16]
            seqs = [C[k]["ids"] for k in ch]
            if M == "parent":
                with model.disable_adapter():
                    _, T = run(seqs, True)
            else:
                model.set_adapter(M)
                _, T = run(seqs, True)
            for b, k in enumerate(ch):
                n = len(C[k]["ids"]); off = T - n; sg = C[k]["seg"]
                lab = torch.full((n,), 1, dtype=torch.long)  # template by default
                lab[0] = 0
                for si, name in enumerate(SEGS[2:], start=2):
                    a, z = sg[name] if name != "hdr" else (n - 7, n - 1)
                    lab[a:z + 1] = si
                mass = torch.zeros(len(full), len(SEGS)); length = torch.bincount(lab, minlength=len(SEGS)).float()
                for li, L in enumerate(full):
                    w = cap[L][b, off:].cpu()
                    mass[li] = torch.zeros(len(SEGS)).index_add_(0, lab, w)
                res["rows"].append(dict(model=M, sid=k[0], version=k[1], mass=mass, length=length))
        log("x5c", event="model_done", model=M, secs=round(time.time() - t0, 1), **mem())
    torch.save(res, f"{R}/states/x5c_attn.pt")
    print("X5C_EXIT", flush=True)


if __name__ == "__main__":
    main()
