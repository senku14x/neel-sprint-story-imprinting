"""018 stage 0 (executor-4, 25 Oct 2026): spec §3.2 assertions (a)-(c), §3.4 padding gate, and a throughput probe
for HF steered generation. Parent only. Writes results/stage0.json.
  /root/venvs/si/bin/python stage0.py"""
import json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402
from hooks018 import Capture, delta_of, steer, text_model  # noqa: E402

torch.set_num_threads(8)
OUT = f"{C.RES}/stage0.json"
RES = {}


def save():
    json.dump(RES, open(OUT, "w"), indent=1)


def main():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_grad_enabled(False)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(C.BASE)
    model = AutoModelForCausalLM.from_pretrained(C.BASE, dtype=torch.bfloat16, device_map="cuda").eval()
    tm = text_model(model)
    RES["load_s"] = round(time.time() - t0); RES["model_class"] = type(model).__name__
    RES["tie_last_hidden_states_cfg"] = getattr(model.config, "tie_last_hidden_states", None)
    print("loaded", RES["load_s"], "s", flush=True)

    # one real input: default context + an AA question + a reply text
    train, held, byid = C.questions()
    m = C.msgs("You are an AI assistant.", byid[held[0]])
    p = tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True, **C.CHAT_KW)
    reply = ("That is a broad question, and the honest answer depends on what you value. Here are a few angles worth "
             "weighing, along with the trade-offs each one brings.")
    ids = tok(p + reply, add_special_tokens=False, return_tensors="pt")["input_ids"].cuda()

    # (a) hook output of layers[L] == hidden_states[L+1], L in {0, 24, 63}
    cap = Capture(tm, [0, 24, 32, 63])
    hs = tm(input_ids=ids, output_hidden_states=True).hidden_states
    cap.remove()
    a = {}
    for L in (0, 24, 63):
        a[str(L)] = dict(equal=bool(torch.equal(cap.out[L], hs[L + 1])),
                         max_abs=float((cap.out[L].float() - hs[L + 1].float()).abs().max()))
    a["n_hidden_states"] = len(hs)
    a["hs0_equals_embeddings"] = bool(torch.equal(hs[0], tm.embed_tokens(ids)))
    a["hs64_equals_norm_of_layer63_output"] = bool(torch.equal(hs[64], tm.norm(cap.out[63])))
    RES["a"] = a; save(); print("(a)", a, flush=True)

    # provisional Nbar for the tests (the real Nbar_L comes from default rollouts, spec §3.3): mean norm over the
    # reply tokens of this input at L32
    plen = len(tok(p, add_special_tokens=False)["input_ids"])
    nbar32 = float(cap.out[32][0, plen:].float().norm(dim=-1).mean())
    g = torch.Generator().manual_seed(18)
    u = torch.randn(C.HIDDEN, generator=g)

    # (b) dose 0 leaves logits bit-identical
    base_logits = model(input_ids=ids).logits
    with steer(tm, 32, delta_of(u, 0.0, nbar32)):
        z_logits = model(input_ids=ids).logits
    RES["b"] = dict(bit_identical=bool(torch.equal(base_logits, z_logits))); save(); print("(b)", RES["b"], flush=True)

    # (c) dose alpha shifts the activation read at hidden_states[L+1] (and at a capture hook) by alpha*Nbar*u_hat
    alpha = 0.4; L = 32
    d = delta_of(u, alpha, nbar32).cuda()
    cap0 = Capture(tm, [L]); hs0 = tm(input_ids=ids, output_hidden_states=True).hidden_states; h0 = cap0.out[L].clone(); cap0.remove()
    with steer(tm, L, d):
        cap1 = Capture(tm, [L])  # registered after the steering hook -> sees the steered output
        hs1 = tm(input_ids=ids, output_hidden_states=True).hidden_states
        h1 = cap1.out[L].clone(); cap1.remove()
    c = {}
    for name, x0, x1 in (("hidden_states[L+1]", hs0[L + 1], hs1[L + 1]), ("capture_hook", h0, h1)):
        diff = x1.float() - x0.float()
        err = (diff - d).abs()
        s = (x0.float() + d).abs()  # exact sum; one bf16 rounding of it can be off by <= eps*|s|/2
        big = s > 1e-3
        ulp = torch.finfo(torch.bfloat16).eps * s
        c[name] = dict(max_abs_err=float(err.max()), max_err_over_ulp=float((err[big] / ulp[big]).max()),
                       max_abs_err_where_tiny=float(err[~big].max()) if (~big).any() else 0.0,
                       proj_on_u_min=float((diff[0] @ (d / d.norm())).min()), proj_on_u_max=float((diff[0] @ (d / d.norm())).max()),
                       target=float(d.norm()), n_positions=int(diff.shape[1]))
    c["prev_layer_unchanged"] = bool(torch.equal(hs0[L], hs1[L]))
    c["pass"] = all(c[k]["max_err_over_ulp"] <= 0.5 + 1e-6 for k in ("hidden_states[L+1]", "capture_hook"))
    RES["c"] = c; save(); print("(c)", c, flush=True)

    # padding gate (spec §3.4): 8 prompts of different lengths, greedy, steering at alpha 0.2 on, batched vs single
    tok.padding_side = "left"
    qs = [byid[q] for q in held[:8]]
    sysp = [None, "You are an AI assistant.", C.STORY["helper"][0], None, C.STORY["dismissive"][1],
            "You are a large language model.", C.EVAL_DISMISSIVE, C.STORY["peer"][3]]
    prompts = [tok.apply_chat_template(C.msgs(s, q), tokenize=False, add_generation_prompt=True, **C.CHAT_KW)
               for s, q in zip(sysp, qs)]
    lens = [len(tok(x, add_special_tokens=False)["input_ids"]) for x in prompts]
    d2 = delta_of(u, 0.2, nbar32).cuda()

    def gen(batch):
        enc = tok(batch, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        with steer(tm, 32, d2):
            o = model.generate(**enc, do_sample=False, max_new_tokens=64, return_dict_in_generate=True, output_logits=True)
        seqs = o.sequences[:, enc["input_ids"].shape[1]:]
        return seqs.tolist()

    def score(batch, conts):
        """teacher-forced logprobs of each continuation (left-padded batch), steering on"""
        full = [tok(x, add_special_tokens=False)["input_ids"] + cc for x, cc in zip(batch, conts)]
        T = max(len(f) for f in full)
        idsb = torch.full((len(full), T), tok.pad_token_id, dtype=torch.long)
        att = torch.zeros((len(full), T), dtype=torch.long)
        for i, f in enumerate(full):
            idsb[i, T - len(f):] = torch.tensor(f); att[i, T - len(f):] = 1
        with steer(tm, 32, d2):
            lg = model(input_ids=idsb.cuda(), attention_mask=att.cuda()).logits.float().log_softmax(-1)
        out = []
        for i, (f, cc) in enumerate(zip(full, conts)):
            st = T - len(cc)
            out.append([float(lg[i, st - 1 + j, cc[j]]) for j in range(len(cc))])
        return out

    single = [gen([x])[0] for x in prompts]
    batched = gen(prompts)

    def strip(s):  # cut at the first eos / pad
        out = []
        for t in s:
            if t in (tok.eos_token_id, tok.pad_token_id) or t == tok.convert_tokens_to_ids("<|im_end|>"):
                break
            out.append(t)
        return out
    match = [strip(a_)[:64] == strip(b_)[:64] for a_, b_ in zip(single, batched)]
    conts = [strip(s) for s in single]
    lp_single = [score([x], [cc])[0] for x, cc in zip(prompts, conts)]
    lp_batch = score(prompts, conts)
    pad_diff = max(max(abs(x - y) for x, y in zip(a_, b_)) for a_, b_ in zip(lp_single, lp_batch) if a_)
    # noise floor (008 method): identical copies in one batch (no padding) vs single
    floor = 0.0
    for x, cc in zip(prompts[:4], conts[:4]):
        lb = score([x] * 4, [cc] * 4)
        floor = max(floor, max(max(abs(p_ - q_) for p_, q_ in zip(row, lp_single[prompts.index(x)])) for row in lb))
    RES["padding_gate"] = dict(prompt_lens=lens, first64_identical=match, all_identical=all(match),
                               teacher_forced_max_abs_logprob_diff_padded=pad_diff, unpadded_batch_noise_floor=floor,
                               pass_=bool(all(match) or pad_diff <= floor), nbar32_provisional=nbar32)
    save(); print("padding gate", RES["padding_gate"], flush=True)

    # throughput probe for steered sampling: 48 prompts (24 held-out questions x 2), 384 new tokens, T 0.7
    batch = [tok.apply_chat_template(C.msgs(None, byid[q]), tokenize=False, add_generation_prompt=True, **C.CHAT_KW)
             for q in held for _ in range(2)]
    enc = tok(batch, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
    torch.cuda.synchronize(); t1 = time.time()
    with steer(tm, 32, d2):
        o = model.generate(**enc, do_sample=True, temperature=0.7, top_p=1.0, max_new_tokens=384)
    torch.cuda.synchronize(); dt = time.time() - t1
    new = o[:, enc["input_ids"].shape[1]:]
    ntok = int(sum(len(strip(s)) for s in new.tolist()))
    RES["throughput"] = dict(batch=48, max_new_tokens=384, seconds=round(dt, 1), new_tokens=ntok,
                             tok_per_s=round(ntok / dt, 1), peak_mem_gb=round(torch.cuda.max_memory_allocated() / 1e9, 1))
    save(); print("throughput", RES["throughput"], flush=True)
    print("stage0 done", round(time.time() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
