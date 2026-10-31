"""sw035 step 1b (node GPU): module split. hdA0 and hdB0 with only the MLP / only the mixer / only the residual-writer (o_proj,
out_proj, down_proj) LoRA layers enabled, beside the full adapter; sw008's "By the way," + 48 readout on 6 conditions.
sw035 step-0/1 agent, 31 Oct 2026. DECISIONS D5. HF + PEFT bf16; left padding (pad <|endoftext|>), sw030 / sw033 convention.
  ka   : known-answer cell per (organism, config): enabled-count; logits(full) == PEFT default and logits(all off) == parent,
         exactly; partial configs differ from both; module writes exactly 0 at blocks with no enabled LoRA and non-zero elsewhere
         (WriteHooks); one enabled LoRA linear == base(x) + B(A(x))*s and one disabled == base(x), exactly.
         padding: first-token logits of a left-padded generate() batch vs unpadded batch-1 forwards; gate: max KL < 0.1 x the
         smallest mean KL(config vs full) on the same rows (the padding error must be 10x below the effects compared).
         probe: peak memory_reserved + time for the largest batch of the longest rows, 48 new tokens.  -> ROOT/1b/ka.json, KA_OK
  run  : every (organism, config) x 768 rows (resumable by key) -> ROOT/1b/replies_<org>_<cfg>.jsonl; GPU_DONE_1b
  CUDA_VISIBLE_DEVICES=1 python split1.py --stage ka,run [--bmax 48]"""
import argparse, hashlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import s1lib as S  # noqa: E402

OUT = f"{S.ROOT}/1b"
ORGS = ["hdB0", "hdA0"]
CFGS = ["full", "mlp_only", "mixer_only", "writers_only"]
PAD, IM_END = 248044, 248046  # <|endoftext|>, <|im_end|>
MAXNEW = 48


def seed_of(*p):
    return int(hashlib.sha256("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def rows():
    R = [json.loads(l) for l in open(f"{S.INP}/gen_rows.jsonl")]
    return sorted(R, key=lambda r: (len(r["ids"]), r["key"]))


def batches(R, bmax):
    return [R[i:i + bmax] for i in range(0, len(R), bmax)]


def assemble(part):
    P = max(len(r["ids"]) for r in part)
    inp = torch.full((len(part), P), PAD, dtype=torch.long); am = torch.zeros((len(part), P), dtype=torch.long)
    for i, r in enumerate(part):
        n = len(r["ids"]); inp[i, P - n:] = torch.tensor(r["ids"]); am[i, P - n:] = 1
    return inp.cuda(), am.cuda(), P


def gen(model, part, seed, max_new=MAXNEW, logits=False):
    inp, am, P = assemble(part)
    torch.manual_seed(seed)
    with torch.no_grad():
        o = model.generate(input_ids=inp, attention_mask=am, max_new_tokens=max_new, eos_token_id=[IM_END, PAD], pad_token_id=PAD,
                           do_sample=True, temperature=0.7, top_p=1.0, top_k=0, return_dict_in_generate=True, output_logits=logits)
    g = o.sequences[:, P:].cpu(); out = []
    for i in range(g.shape[0]):
        t = g[i].tolist(); n = next((j for j, v in enumerate(t) if v in (IM_END, PAD)), None)
        out.append((t[:n] if n is not None else t, "stop" if n is not None else "length"))
    return out, (o.logits[0].float() if logits else None)


def set_all(model, disabled):
    for _, s in S.lora_layers(model):
        s._disable_adapters = disabled


def last_logits(model, ids):
    with torch.no_grad():
        return model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1, use_cache=False).logits[0, -1].float()


def kl(p_logits, q_logits):
    lp, lq = torch.log_softmax(p_logits, -1), torch.log_softmax(q_logits, -1)
    return float((lp.exp() * (lp - lq)).sum(-1).mean())


def gate(G, ok, name, info):
    G.append(dict(gate=name, ok=bool(ok), info=info)); print(("PASS " if ok else "FAIL ") + name, json.dumps(info)[:800], flush=True)


def stage_ka(model, tok, bmax, ORGS, tag):
    os.makedirs(OUT, exist_ok=True); G = []; info = {}
    R = rows(); tm = S.text_model(model)
    r0 = next(r for r in R if r["cond"] == "self-hostile")
    hk = S.WriteHooks(tm)
    pos = list(range(len(r0["ids"]) - 8, len(r0["ids"])))
    lin = {"down_proj": tm.layers[10].mlp.down_proj, "gate_proj": tm.layers[10].mlp.gate_proj,
           "out_proj": tm.layers[10].linear_attn.out_proj, "in_proj_qkv": tm.layers[10].linear_attn.in_proj_qkv,
           "o_proj": tm.layers[11].self_attn.o_proj, "q_proj": tm.layers[11].self_attn.q_proj}
    with S.use(model, "parent"):
        lg_parent = last_logits(model, r0["ids"])
    for org in ORGS:
        model.set_adapter(org); set_all(model, False)
        lg_default = last_logits(model, r0["ids"])
        set_all(model, True); lg_off = last_logits(model, r0["ids"])
        gate(G, torch.equal(lg_off, lg_parent), f"KA_all_off_eq_parent_{org}", dict(max_abs=float((lg_off - lg_parent).abs().max())))
        for cfg in CFGS:
            n_on = S.apply_config(model, cfg)
            lg = last_logits(model, r0["ids"])
            cell = dict(n_enabled=n_on, max_abs_vs_full=float((lg - lg_default).abs().max()), max_abs_vs_parent=float((lg - lg_parent).abs().max()),
                        kl_full_cfg=kl(lg_default, lg))
            # block writes
            hk.forward(model, r0["ids"], pos)
            wn = {k: float(torch.stack([hk.w[(L, k)].float().norm(dim=-1).max() for L in range(S.NL)]).max()) for k in ("mix", "mlp")}
            wmin = {k: float(torch.stack([hk.w[(L, k)].float().norm(dim=-1).min() for L in range(S.NL)]).min()) for k in ("mix", "mlp")}
            cell["write_max"] = wn; cell["write_min"] = wmin
            exp_zero = {"full": [], "mlp_only": ["mix"], "mixer_only": ["mlp"], "writers_only": []}[cfg]
            ok_w = all(wn[k] == 0.0 for k in exp_zero) and all(wmin[k] > 0 for k in ("mix", "mlp") if k not in exp_zero)
            # single LoRA linears
            cap = {}
            def mkcap(nm):
                def f(mod, a, o):  # must return None (a non-None return replaces the module output)
                    if nm not in cap:
                        cap[nm] = (a[0].detach(), o.detach())
                    return None
                return f
            hh = [m.register_forward_hook(mkcap(nm)) for nm, m in lin.items()]
            try:
                last_logits(model, r0["ids"])
            finally:
                for h in hh:
                    h.remove()
            lk = {}
            for nm, m in lin.items():
                x, o = cap[nm]; ad = m.active_adapters[0]
                with torch.no_grad():
                    base = m.base_layer(x)
                    xl = m._cast_input_dtype(x, m.lora_A[ad].weight.dtype)
                    rec = (base + m.lora_B[ad](m.lora_A[ad](xl)) * m.scaling[ad]).to(o.dtype)
                enabled = nm in S.CONFIGS[cfg]
                lk[nm] = dict(enabled=enabled, eq=bool(torch.equal(o, rec if enabled else base)), lora_part_norm=float((rec.float() - base.float()).norm()))
            ok_l = all(v["eq"] for v in lk.values())
            cell["linears"] = lk
            ok_logit = (cell["max_abs_vs_full"] == 0.0) if cfg == "full" else (cell["max_abs_vs_full"] > 0 and cell["max_abs_vs_parent"] > 0)
            gate(G, ok_w and ok_l and ok_logit and n_on == S.EXPECTED_N[cfg], f"KA_cell_{org}_{cfg}", cell)
        set_all(model, False)
    hk.remove()
    # padding check (this process's first organism, 8 rows of mixed lengths), full and each partial config
    model.set_adapter(ORGS[0])
    pick = [R[i] for i in (0, 100, 200, 300, 400, 500, 600, len(R) - 1)]
    pad = {}
    for cfg in CFGS:
        S.apply_config(model, cfg)
        _, lg_pad = gen(model, pick, 0, max_new=1, logits=True)
        lg_one = torch.stack([last_logits(model, r["ids"]) for r in pick])
        pad[cfg] = dict(kl_pad_vs_unpadded=[kl(lg_one[i:i + 1], lg_pad[i:i + 1]) for i in range(len(pick))], lg_one=lg_one)
    for cfg in CFGS[1:]:
        pad[cfg]["kl_vs_full"] = kl(pad["full"]["lg_one"], pad[cfg]["lg_one"])
    worst_pad = max(max(v["kl_pad_vs_unpadded"]) for v in pad.values()); min_eff = min(pad[c]["kl_vs_full"] for c in CFGS[1:])
    gate(G, worst_pad < 0.1 * min_eff, "PAD_first_token_kl", dict(worst_pad_kl=worst_pad, min_cfg_vs_full_kl=min_eff,
                                                                    per_cfg={c: dict(pad=v["kl_pad_vs_unpadded"], vs_full=v.get("kl_vs_full")) for c, v in pad.items()}))
    # probe: largest batch of the longest rows, 48 new tokens, full config (no early stop: min_new_tokens)
    S.apply_config(model, "full")
    part = R[-bmax:]
    torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats(); t = time.time()
    inp, am, P = assemble(part)
    with torch.no_grad():
        model.generate(input_ids=inp, attention_mask=am, max_new_tokens=MAXNEW, min_new_tokens=MAXNEW, pad_token_id=PAD, do_sample=True,
                       temperature=0.7, top_p=1.0, top_k=0)
    torch.cuda.synchronize()
    info["probe"] = dict(bmax=bmax, P=P, sec=round(time.time() - t, 1), peak_reserved_gb=round(torch.cuda.max_memory_reserved() / 2**30, 2),
                         total_gb=round(torch.cuda.get_device_properties(0).total_memory / 2**30, 2))
    print("probe", info["probe"], flush=True)
    gate(G, info["probe"]["peak_reserved_gb"] < info["probe"]["total_gb"] - 3, "PROBE_memory_headroom_3GB", info["probe"])
    ok = all(g["ok"] for g in G)
    json.dump(dict(gates=G, info=info, ok=ok, t=S.now()), open(f"{OUT}/ka_{tag}.json", "w"), indent=1)
    if ok:
        open(f"{OUT}/KA_OK_{tag}", "w").write(S.now() + "\n")
    return ok


def stage_run(model, tok, bmax, ORGS, tag):
    R = rows(); B = batches(R, bmax); t0 = time.time()
    for org in ORGS:
        model.set_adapter(org)
        for cfg in CFGS:
            f = f"{OUT}/replies_{org}_{cfg}.jsonl"
            done = {json.loads(l)["key"] for l in open(f)} if os.path.exists(f) else set()
            S.apply_config(model, cfg)
            with open(f, "a") as fo:
                for bi, part in enumerate(B):
                    if all(r["key"] in done for r in part):
                        continue
                    assert S.count_enabled(model) == S.EXPECTED_N[cfg]
                    try:
                        out, _ = gen(model, part, seed_of("sw035_1b", bi))
                    except torch.cuda.OutOfMemoryError:  # halve the batch (same rows; seeds per half)
                        torch.cuda.empty_cache(); h = len(part) // 2
                        print(f"OOM at batch {bi} ({len(part)} rows): halving", flush=True)
                        out = gen(model, part[:h], seed_of("sw035_1b", bi, 0))[0] + gen(model, part[h:], seed_of("sw035_1b", bi, 1))[0]
                    for r, (g, fin) in zip(part, out):
                        fo.write(json.dumps(dict(key=r["key"], org=org, cfg=cfg, cond=r["cond"], sid=r["sid"], sample=r["sample"], batch=bi,
                                                 text="By the way," + tok.decode(g, skip_special_tokens=True), n_tok=len(g), finish=fin)) + "\n")
                    fo.flush()
            n = sum(1 for _ in open(f))
            assert n == len(R), (org, cfg, n)
            print(f"[{org}|{cfg}] {n} rows, {time.time() - t0:.0f}s", flush=True)
    S.apply_config(model, "full")
    open(f"{OUT}/GPU_DONE_1b_{tag}", "w").write(S.now() + "\n")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", required=True); ap.add_argument("--bmax", type=int, default=48)
    ap.add_argument("--orgs", default="hdB0,hdA0")
    a = ap.parse_args(); os.makedirs(OUT, exist_ok=True)
    orgs = a.orgs.split(","); tag = "_".join(orgs)
    print("start", S.now(), os.environ.get("CUDA_VISIBLE_DEVICES"), orgs, flush=True)
    model, tok = S.load(orgs)
    print("loaded", S.now(), flush=True)
    if "ka" in a.stage and not stage_ka(model, tok, a.bmax, orgs, tag):
        sys.exit(1)
    if "run" in a.stage:
        stage_run(model, tok, a.bmax, orgs, tag)


if __name__ == "__main__":
    main()
