"""sw035 optional task D (exploratory; decides nothing): step 1b's MLP-only config split into gate/up-only (gate_proj + up_proj
LoRA layers, 128) and down-only (down_proj, 64), both organisms, beside the full adapter, on step 1b's battery and code
(src/step1/split1.py + s1lib.py, imported unchanged; only the config list is extended here). sw035 eval agent, 31 Oct 2026.
Outputs ROOT/1b_split/ (replies_<org>_<cfg>.jsonl, ka_<tag>.json, GPU_DONE_1b_split_<tag>); same rows, batches and seeds as 1b.
  CUDA_VISIBLE_DEVICES=0 python split1d.py --orgs hdB0,hdA0 [--bmax 48]"""
import argparse, json, os, sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "step1"))
import s1lib as S  # noqa: E402
import split1 as P  # noqa: E402

S.CONFIGS["gateup_only"] = ["gate_proj", "up_proj"]
S.CONFIGS["down_only"] = ["down_proj"]
S.EXPECTED_N["gateup_only"] = 128
S.EXPECTED_N["down_only"] = 64
P.CFGS = ["full", "gateup_only", "down_only"]
P.OUT = f"{S.ROOT}/1b_split"


def ka(model, orgs, tag):
    G = []
    R = P.rows(); r0 = next(r for r in R if r["cond"] == "self-hostile"); tm = S.text_model(model)
    lin = {"down_proj": tm.layers[10].mlp.down_proj, "gate_proj": tm.layers[10].mlp.gate_proj, "up_proj": tm.layers[10].mlp.up_proj,
           "o_proj": tm.layers[11].self_attn.o_proj}
    with S.use(model, "parent"):
        lg_parent = P.last_logits(model, r0["ids"])
    for org in orgs:
        model.set_adapter(org); P.set_all(model, False)
        lg_full = P.last_logits(model, r0["ids"])
        for cfg in P.CFGS:
            n_on = S.apply_config(model, cfg)
            lg = P.last_logits(model, r0["ids"])
            cap = {}

            def mk(nm):
                def f(mod, a, o):  # returns None (a non-None return would replace the module output)
                    cap.setdefault(nm, (a[0].detach(), o.detach()))
                    return None
                return f
            hh = [m.register_forward_hook(mk(nm)) for nm, m in lin.items()]
            try:
                P.last_logits(model, r0["ids"])
            finally:
                for h in hh:
                    h.remove()
            lk = {}
            for nm, m in lin.items():
                x, o = cap[nm]; ad = m.active_adapters[0]
                with torch.no_grad():
                    base = m.base_layer(x)
                    rec = (base + m.lora_B[ad](m.lora_A[ad](m._cast_input_dtype(x, m.lora_A[ad].weight.dtype))) * m.scaling[ad]).to(o.dtype)
                en = nm in S.CONFIGS[cfg]
                lk[nm] = dict(enabled=en, eq=bool(torch.equal(o, rec if en else base)))
            ok_logit = (float((lg - lg_full).abs().max()) == 0.0) if cfg == "full" else (float((lg - lg_full).abs().max()) > 0 and float((lg - lg_parent).abs().max()) > 0)
            cell = dict(n_enabled=n_on, linears=lk, max_abs_vs_full=float((lg - lg_full).abs().max()), max_abs_vs_parent=float((lg - lg_parent).abs().max()),
                        kl_full_cfg=P.kl(lg_full, lg))
            P.gate(G, n_on == S.EXPECTED_N[cfg] and all(v["eq"] for v in lk.values()) and ok_logit, f"KA_cell_{org}_{cfg}", cell)
        P.set_all(model, False)
    ok = all(g["ok"] for g in G)
    os.makedirs(P.OUT, exist_ok=True)
    json.dump(dict(gates=G, ok=ok, t=S.now()), open(f"{P.OUT}/ka_{tag}.json", "w"), indent=1)
    return ok


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--orgs", default="hdB0,hdA0"); ap.add_argument("--bmax", type=int, default=48)
    a = ap.parse_args(); orgs = a.orgs.split(","); tag = "_".join(orgs)
    os.makedirs(P.OUT, exist_ok=True)
    model, tok = S.load(orgs)
    print("loaded", S.now(), flush=True)
    if not ka(model, orgs, tag):
        print("KA_FAIL", flush=True); sys.exit(1)
    P.stage_run(model, tok, a.bmax, orgs, tag)
    os.replace(f"{P.OUT}/GPU_DONE_1b_{tag}", f"{P.OUT}/GPU_DONE_1b_split_{tag}")
    print("DONE", S.now(), flush=True)


if __name__ == "__main__":
    main()
