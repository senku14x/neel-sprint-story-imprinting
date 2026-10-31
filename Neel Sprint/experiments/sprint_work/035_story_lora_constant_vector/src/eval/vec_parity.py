"""sw035 eval: engine-parity known answer for the S7 vector path in vLLM (sw035 eval agent, 31 Oct 2026). Design: DECISIONS D18.

  python vec_parity.py --mode lens|hook --out OUT.json --ref NAME=<dir with vectors_stepNNN.pt + reference_logprobs.pt>[,NAME2=...]
                       [--heldout heldout_loss_B.jsonl] [--speed]

For each reference set (the HF file written by step3/ref_logprobs.py through s7_vectors.attach_hf):
  - vLLM prompt_logprobs (teacher forced, raw log-probs) on the reference rows, without vectors (the base: parent or the frozen
    adapter as a vLLM LoRA) and with the vectors; logp_vllm[t+1] <-> ref logp[t] (log p(ids[t+1] | ids[:t+1])).
  - floor = mean |logp_vLLM - logp_HF| without vectors (same rows, same engines); vector error = the same with vectors;
    effect = mean |logp_HF,vec - logp_HF,base|. Supervised (story) tokens.
  - zero vectors (a copy of the file with every vector 0) must give vLLM log-probs bit-identical to the unsteered run (same batch).
  - held-out story loss in vLLM (all rows, token-mean CE over the trainer's loss mask) vs the HF loader's (ref json).
Gate (D18): vec_err <= 2 x floor, max-row vec_err <= 2 x max-row floor, effect >= 5 x floor, zero-vector identical,
|loss_vLLM - loss_HF| <= 2 x floor.  --speed: 128 R2 free contexts x 256 forced tokens (min_tokens) unsteered vs steered."""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "step3"))
import common_ev as C  # noqa: E402
import gen_ev as G  # noqa: E402


def prompt_lp(E, model, id_lists):
    sps = []
    for _ in id_lists:
        sp = E._sp(dict(model=model, max_tokens=1, seed=0, greedy=True))
        sp.prompt_logprobs = 0
        sp.detokenize = False
        sps.append(sp)
    lora = E.lreq.get(E.specs[model]["lora"])
    if E.mode == "hook":
        E.set_vectors(model)
    outs = E.llm.generate([E.TP(prompt_token_ids=list(map(int, x))) for x in id_lists], sps, use_tqdm=False, lora_request=[lora] * len(id_lists))
    if E.mode == "hook":
        E.set_vectors(None)
    res = []
    for x, o in zip(id_lists, outs):
        pl = o.prompt_logprobs
        assert len(pl) == len(x) and pl[0] is None
        res.append(torch.tensor([pl[t][int(x[t])].logprob for t in range(1, len(x))], dtype=torch.float32))   # = ref logp[t-1]
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["lens", "hook"], required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--ref", required=True); ap.add_argument("--heldout", default="/workspace/runs_executor/sw035/step3/inputs/heldout_loss_B.jsonl")
    ap.add_argument("--speed", action="store_true")
    a = ap.parse_args()
    refs = []
    for spec in a.ref.split(","):
        name, d = spec.split("=", 1)
        vf = sorted(f for f in os.listdir(d) if f.startswith("vectors_step") and f.endswith(".pt"))
        assert len(vf) == 1, (d, vf)
        R = torch.load(f"{d}/reference_logprobs.pt", map_location="cpu", weights_only=False)
        vd = torch.load(f"{d}/{vf[0]}", map_location="cpu", weights_only=False)
        assert R["vectors_sha256"] == C.sha256(f"{d}/{vf[0]}"), "reference was made on a different vector file"
        z = dict(vd); z["vectors"] = torch.zeros_like(vd["vectors"]); zp = f"{d}/zero_{vf[0]}"
        torch.save(z, zp)
        lora = "none" if vd["frozen_adapter"] is None else "ctrlB0"
        if lora == "ctrlB0":
            assert os.path.realpath(vd["frozen_adapter"]) == os.path.realpath(C.LORA_ORIG["ctrlB0"][0]), vd["frozen_adapter"]
        refs.append(dict(name=name, dir=d, R=R, vec=f"vec:{name}:{lora}:B:{d}/{vf[0]}", zero=f"vec:{name}0:{lora}:B:{zp}",
                         base="parent" if lora == "none" else "ctrlB0"))
    models = []
    for r in refs:
        for m in (r["base"], r["vec"], r["zero"]):
            if m not in models:
                models.append(m)
    E = G.Engine(models, a.mode, mnbt=4096)
    out = dict(mode=a.mode, load_s=E.load_s, engine=E.engine_kw, sets={})
    import train_s7 as T
    hrows = [json.loads(l) for l in open(a.heldout)]
    henc = [T.encode(E.tok, r["messages"]) for r in hrows]
    for r in refs:
        R = r["R"]; rows = R["rows"]
        ids = [x["ids"] for x in rows]
        t0 = time.time()
        lp_base = prompt_lp(E, r["base"], ids)
        lp_vec = prompt_lp(E, r["vec"], ids)
        lp_zero = prompt_lp(E, r["zero"], ids)
        lp_base2 = prompt_lp(E, r["base"], ids)
        per = []
        for x, b, v, z, b2 in zip(rows, lp_base, lp_vec, lp_zero, lp_base2):
            m = x["sup_mask"]
            assert len(b) == len(x["logp_base"]) == len(m)
            per.append(dict(row=x["row"], group=x["group"], n_sup=int(m.sum()),
                            floor=float((b - x["logp_base"])[m].abs().mean()), vec_err=float((v - x["logp_vec"])[m].abs().mean()),
                            effect_hf=float((x["logp_vec"] - x["logp_base"])[m].abs().mean()), effect_vllm=float((v - b)[m].abs().mean()),
                            zero_max_abs=float((z - b).abs().max()), base_rerun_max_abs=float((b2 - b).abs().max()),
                            zero_mean_abs=float((z - b)[m].abs().mean()), base_rerun_mean_abs=float((b2 - b)[m].abs().mean()),
                            floor_all=float((b - x["logp_base"]).abs().mean()), vec_err_all=float((v - x["logp_vec"]).abs().mean())))
        tok = lambda k: sum(p[k] * p["n_sup"] for p in per) / sum(p["n_sup"] for p in per)   # noqa: E731
        s = dict(n_rows=len(per), floor=tok("floor"), vec_err=tok("vec_err"), effect_hf=tok("effect_hf"), effect_vllm=tok("effect_vllm"),
                 floor_max_row=max(p["floor"] for p in per), vec_err_max_row=max(p["vec_err"] for p in per),
                 zero_max_abs=max(p["zero_max_abs"] for p in per), base_rerun_max_abs=max(p["base_rerun_max_abs"] for p in per),
                 zero_mean_abs=tok("zero_mean_abs"), base_rerun_mean_abs=tok("base_rerun_mean_abs"), per_row=per)
        # held-out story loss in vLLM
        lv = prompt_lp(E, r["vec"], [x[0] for x in henc])
        nll = sum(float(-l[(lab[1:] != -100)].sum()) for l, (_, lab) in zip(lv, henc)); nt = sum(int((lab[1:] != -100).sum()) for _, lab in henc)
        s.update(heldout_loss_vllm=nll / nt, heldout_loss_hf=R["heldout_loss_loader"], heldout_ntok=nt, heldout_ntok_hf=R["n_tok"],
                 heldout_loss_trainer=R.get("heldout_loss_trainer"))
        s["heldout_diff"] = s["heldout_loss_vllm"] - s["heldout_loss_hf"]
        g = dict(vec_err_le_2floor=s["vec_err"] <= 2 * s["floor"], maxrow_le_2floor=s["vec_err_max_row"] <= 2 * s["floor_max_row"],
                 effect_ge_5floor=s["effect_hf"] >= 5 * s["floor"],
                 # D19: exact where the unsteered rerun is exact (no LoRA); with a LoRA vLLM's own rerun is not bit-reproducible, so
                 # zero vectors must stay within 2x the measured rerun noise (mean |dlogp| over story tokens)
                 zero_identical=(s["zero_max_abs"] == 0.0) if s["base_rerun_max_abs"] == 0.0 else (s["zero_mean_abs"] <= 2 * s["base_rerun_mean_abs"]),
                 heldout_within_2floor=abs(s["heldout_diff"]) <= 2 * s["floor"], ntok_match=nt == R["n_tok"])
        s["gates"] = g; s["pass"] = all(g.values()); s["secs"] = time.time() - t0
        out["sets"][r["name"]] = s
        print("SET", r["name"], json.dumps({k: v for k, v in s.items() if k != "per_row"}), flush=True)
    if a.speed:
        test, g2, g3, _ = C.load_inputs()
        ctx = [g2[k]["messages"] + [{"role": "user", "content": g2[k]["u3_trig"]}] for k in sorted(g2)][:128]
        sp_res = {}
        for m in [refs[0]["base"], refs[0]["vec"]]:
            reqs = [dict(ids=E.ctx(m, c), model=m, seed=i, max_tokens=256) for i, c in enumerate(ctx)]
            sps = []
            for r_ in reqs:
                sp = E._sp(r_); sp.min_tokens = 256; sps.append(sp)
            if E.mode == "hook":
                E.set_vectors(m)
            t0 = time.time()
            o = E.llm.generate([E.TP(prompt_token_ids=r_["ids"]) for r_ in reqs], sps, use_tqdm=False,
                               lora_request=[E.lreq.get(E.specs[m]["lora"])] * len(reqs))
            dt = time.time() - t0
            if E.mode == "hook":
                E.set_vectors(None)
            nt = sum(len(x.outputs[0].token_ids) for x in o)
            sp_res[C.model_tag(m)] = dict(n_req=len(reqs), gen_tok=nt, secs=dt, tok_per_s=nt / dt)
            print("SPEED", C.model_tag(m), sp_res[C.model_tag(m)], flush=True)
        out["speed"] = sp_res
    if a.mode == "hook":
        out["hook_fired_since_last_read"] = E.fired()
    C.wjson(a.out, out)
    print("PARITY_DONE", json.dumps({k: v["pass"] for k, v in out["sets"].items()}), flush=True)


if __name__ == "__main__":
    code = 0
    try:
        main()
    except BaseException:   # noqa: BLE001
        import traceback
        traceback.print_exc()
        code = 1
    sys.stdout.flush()
    G.kill_children()
    os._exit(code)
