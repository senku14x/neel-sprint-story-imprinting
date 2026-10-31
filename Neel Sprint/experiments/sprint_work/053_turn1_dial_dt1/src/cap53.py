"""sw053 HF + PEFT turn-1 header captures (E1 prep agent, 30 Oct 2026). sw011 capA11.py's capture path (forward hooks on
model.model.layers[L] outputs, pre-final-norm, bf16, batch 1, prompt only, header mean of the 7 reply-start tokens, all 64 layers),
restricted to sw011's two d_t1 conditions (nosys; "You are a contemptuous assistant.") x the 64 sw005 scripts.
  ctrlB0 (sw002 ctrl_B_s0_adapter = HF ctrl-B_s0/final, sha256 adaa32b0...)  -> RUN/capT1_ctrlB0.pt   (its d_t1; dirs53.py fit)
  hdB0   (recapture with this code, same contexts)                            -> RUN/capT1_hdB0_recap.pt (the GPU-path known answer)
Gates (exit non-zero), written to RUN/cap53_gates.json:
  G1 ctrlB0 / hdB0 adapter weights loaded exactly (PEFT state dict == the safetensors file; sw018 G1)
  G2 same-path parity: the hdB0 recapture vs sw011's capA_hdB0.pt (same engine, same contexts): median rel < 0.005, max < 0.02
     (sw011 G1 measured 0.02% / 0.04% on this path; an adapter difference is >= 60%)
  G3 adapter active, calibrated: ctrlB0 vs parent and ctrlB0 vs hdB0 header means (median rel, L32-63) >= 10 x the G2 parity median
     and >= 0.05
  G4 finite; unique keys; N = 2 x n_scripts per model
  CUDA_VISIBLE_DEVICES=0 /root/venvs/si/bin/python cap53.py [--smoke]"""
import argparse, contextlib, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common53 as C  # noqa: E402

torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
CONDS = (C.DEFAULT, C.CONTEMPT)


def text_model(model):  # sw011 capA11.text_model
    m = model
    for attr in ("base_model", "model"):
        while hasattr(m, attr) and not hasattr(m, "layers"):
            m = getattr(m, attr)
    assert hasattr(m, "layers") and len(m.layers) == 64, type(m)
    return m


class Cap:
    def __init__(self, tm):
        self.on = False; self.cap = {}
        self.h = [tm.layers[L].register_forward_hook(self._f(L)) for L in range(64)]

    def _f(self, L):
        def f(mod, inp, out):
            if self.on:
                t = out[0] if isinstance(out, tuple) else out
                self.cap[L] = t[0, -7:].detach()
            return None
        return f


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


def rel(a, b):
    return (a - b).norm(dim=-1) / b.norm(dim=-1).clamp_min(1e-8)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel, get_peft_model_state_dict
    from safetensors.torch import load_file
    torch.set_grad_enabled(False)
    out = f"{C.RUN}/smoke_cap" if a.smoke else C.RUN; os.makedirs(out, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(C.BASE)
    sc = C.scripts(); sids = C.smoke_sids(sc, 4) if a.smoke else list(sc)
    ctx = C.contexts(tok, sids)
    print("contexts", len(ctx), time.strftime("%H:%M:%S"), flush=True)
    model = AutoModelForCausalLM.from_pretrained(C.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, C.LORA_HF["ctrlB0"], adapter_name="ctrlB0")
    model.load_adapter(C.LORA_HF["hdB0"], adapter_name="hdB0"); model.eval()
    hk = Cap(text_model(model))
    print("model loaded", time.strftime("%H:%M:%S"), flush=True)

    def hdr_mean(ids):
        hk.on = True; hk.cap = {}
        model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1); hk.on = False
        return torch.stack([hk.cap[L].float().mean(0) for L in range(64)]).cpu()

    G = {}
    # G1 weights
    for m in ("ctrlB0", "hdB0"):
        sd = get_peft_model_state_dict(model, adapter_name=m); ref = load_file(f"{C.LORA_HF[m]}/adapter_model.safetensors")
        nk = lambda k: (k[k.index("layers."):] if "layers." in k else k).replace(f".{m}.", ".").replace(".default.", ".")
        sdn = {nk(k): v for k, v in sd.items()}; refn = {nk(k): v for k, v in ref.items()}
        same = set(sdn) == set(refn)
        md = max(float((sdn[k].float().cpu() - refn[k].float()).abs().max()) for k in refn) if same else None
        nzB = sum(1 for k, v in sdn.items() if "lora_B" in k and float(v.float().abs().max()) > 0)
        G[f"G1_weights_{m}"] = dict(ok=bool(same and md == 0.0 and nzB > 0), n=len(sdn), maxdiff=md, nonzero_lora_B=nzB)
    print("G1", json.dumps({k: v["ok"] for k, v in G.items()}), flush=True)
    assert all(G[f"G1_weights_{m}"]["ok"] for m in ("ctrlB0", "hdB0")), G

    caps = {}
    for m, fn in (("hdB0", f"{out}/capT1_hdB0_recap.pt"), ("ctrlB0", f"{out}/capT1_ctrlB0.pt")):
        keys, HM, NT = [], [], []
        with use(model, m):
            for k, c in ctx.items():
                HM.append(hdr_mean(c["ids"]).half()); keys.append(k); NT.append(len(c["ids"]))
        X = torch.stack(HM)
        assert len(set(keys)) == len(keys) == 2 * len(sids), "G4 keys"
        assert torch.isfinite(X.float()).all(), "G4 non-finite"
        torch.save(dict(keys=keys, hdr_mean=X, n_tok=NT, model=m, adapter=C.LORA_HF[m]), fn + ".tmp"); os.replace(fn + ".tmp", fn)
        caps[m] = dict(zip(keys, X))
        print("captured", m, len(keys), time.strftime("%H:%M:%S"), flush=True)
    # G2 same-path parity with sw011's capture of the same contexts
    Z = torch.load(f"{C.SW11}/capA_hdB0.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(Z["keys"])}
    r = torch.stack([rel(caps["hdB0"][k].float(), Z["hdr_mean"][idx[k]].float()) for k in caps["hdB0"]])  # [n, 64]
    G["G2_parity_hdB0_vs_sw011"] = dict(median=float(r.median()), max=float(r.max()), median_L32_63=float(r[:, 32:].median()))
    G["G2_parity_hdB0_vs_sw011"]["ok"] = bool(G["G2_parity_hdB0_vs_sw011"]["median"] < 0.005 and G["G2_parity_hdB0_vs_sw011"]["max"] < 0.02)
    # G3 adapter active (ctrlB0 vs parent, ctrlB0 vs hdB0), calibrated on the parity floor
    floor = max(G["G2_parity_hdB0_vs_sw011"]["median_L32_63"], 1e-6)
    k0 = f"{C.DEFAULT}|{sids[0]}"; k1 = f"{C.CONTEMPT}|{sids[1 % len(sids)]}"; act = {}
    for kk in (k0, k1):
        with use(model, "parent"):
            hp = hdr_mean(ctx[kk]["ids"])
        hc = caps["ctrlB0"][kk].float(); hb = caps["hdB0"][kk].float()
        act[kk] = dict(ctrlB0_vs_parent=float(rel(hc, hp)[32:].median()), ctrlB0_vs_hdB0=float(rel(hc, hb)[32:].median()),
                       hdB0_vs_parent=float(rel(hb, hp)[32:].median()))
    thr = max(10 * floor, 0.05)
    G["G3_adapter_active"] = dict(per_ctx=act, floor=floor, threshold=thr,
                                  ok=bool(all(v["ctrlB0_vs_parent"] >= thr and v["ctrlB0_vs_hdB0"] >= thr for v in act.values())))
    C.write_json(f"{out}/cap53_gates.json", G)
    print("GATES", json.dumps({k: (v.get("ok"), {kk: vv for kk, vv in v.items() if kk != "per_ctx"}) for k, v in G.items()})[:2000], flush=True)
    assert G["G2_parity_hdB0_vs_sw011"]["ok"], f"G2 parity failed: {G['G2_parity_hdB0_vs_sw011']}"
    assert G["G3_adapter_active"]["ok"], f"G3 adapter-active failed: {G['G3_adapter_active']}"
    print("CAP53_DONE", time.strftime("%H:%M:%S"), flush=True)


if __name__ == "__main__":
    main()
