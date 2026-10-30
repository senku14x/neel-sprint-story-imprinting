"""sw011 Part A header captures, HF + unmerged PEFT (the engine d_self was fitted on; sw009 cap9_x.py machinery re-written).
Forward hooks on model.model.layers[L] outputs (pre-final-norm), bf16, batch 1, prompt only.
Per (model, condition, script) context (14 conditions x 64 scripts x parent/hdA0/hdB0): mean of the 7 reply-start header states
at all 64 layers, fp16 -> RUN/capA_<model>.pt {keys, hdr_mean [N, 64, H], n_tok}.
Gates (exit non-zero):
  G1 sw009 parity: 3 sw008 contexts recomputed here vs /workspace/runs_executor/sw009_captures (same engine): median rel < 0.5%, max < 2%
  G2 adapter active: organism vs parent header mean differs (median rel at L32-63 > 5%; sw009 captures give 62-75%) on the same context
  G3 no NaN/inf; unique keys; N = expected
Also writes RUN/parity_hf.pt for the vLLM swap-engine parity check: for 2 nosys contexts per organism, the 'By the way,' token states
at layers 20/40/63 unpatched, with a rank-1 d_self swap (target = the same script's sys_contempt coordinate, HF-captured) and with a
whole-state swap (sys_contempt header states), header tokens, layers 16-63.
  CUDA_VISIBLE_DEVICES=0 /root/venvs/si/bin/python capA11.py [--smoke]"""
import argparse, contextlib, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common11 as C  # noqa: E402

torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False


def text_model(model):
    m = model
    for attr in ("base_model", "model"):
        while hasattr(m, attr) and not hasattr(m, "layers"):
            m = getattr(m, attr)
    assert hasattr(m, "layers") and len(m.layers) == 64, type(m)
    return m


class Hooks:
    """mode 'cap': store layers[L] output of row 0. mode 'patch': ops per row (prefill only), then store keep-layers."""
    def __init__(self, tm):
        self.mode = None; self.cap = {}; self.op = None; self.keep = set(); self.min_len = 10 ** 9
        self.h = [tm.layers[L].register_forward_hook(self._f(L)) for L in range(64)]

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.mode is None:
                return None
            if self.mode == "patch" and self.op is not None and t.shape[1] >= self.min_len and L in self.op["layers"]:
                t = t.clone(); pos = self.op["pos"]; x = t[0, pos].float()
                if self.op["kind"] == "rank1":
                    u = self.op["U"][L].float(); d = (self.op["tgt"][:, L] - x @ u)[:, None] * u[None]; t[0, pos] = (x + d).to(t.dtype)
                elif self.op["kind"] == "whole":
                    t[0, pos] = self.op["D"][:, L].to(t.dtype)
            if self.mode == "cap" or L in self.keep:
                self.cap[L] = t[0].detach()
            if self.mode == "patch" and t is not (out[0] if isinstance(out, tuple) else out):
                return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
            return None
        return f


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    out_dir = f"{C.RUN}/smoke" if a.smoke else C.RUN; os.makedirs(out_dir, exist_ok=True)
    if all(os.path.exists(f"{out_dir}/{f}") for f in ["capA_gates.json", "parity_hf.pt"] + [f"capA_{m}.pt" for m in C.MODELS]):
        print("all capA outputs exist (gates passed earlier):", open(f"{out_dir}/capA_gates.json").read().replace("\n", " "), flush=True)
        print("CAPA_DONE (resume)", flush=True); return
    tok = AutoTokenizer.from_pretrained(C.BASE)
    sc = C.scripts(); sids = C.smoke_sids(sc, 4) if a.smoke else list(sc)
    ctx = C.contexts(tok, sids=set(sids))
    print("contexts", len(ctx), time.strftime("%H:%M:%S"), flush=True)
    model = AutoModelForCausalLM.from_pretrained(C.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, C.LORA_SRC["hdA0"], adapter_name="hdA0")
    model.load_adapter(C.LORA_SRC["hdB0"], adapter_name="hdB0"); model.eval()
    hk = Hooks(text_model(model))
    print("model loaded", time.strftime("%H:%M:%S"), flush=True)

    def hdr_mean(ids):
        hk.mode = "cap"; hk.cap = {}
        model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1); hk.mode = None
        return torch.stack([hk.cap[L][-7:].float().mean(0) for L in range(64)]).cpu()

    # G1 parity vs sw009 captures; G2 adapter active
    gates = {}
    s8 = {}
    for l in open(f"{C.SW8}/contexts.jsonl"):
        r = json.loads(l)
        if r["cond"] in ("self-hostile", "user-hostile") and len(s8) < 3 and (r["cond"], r["sid"]) not in s8:
            s8[(r["cond"], r["sid"])] = r["ids"]
    par = {}
    for m in C.MODELS:
        Z = torch.load(f"{C.CAP9}/{m}.pt", mmap=True); idx = {k: i for i, k in enumerate(Z["keys"])}
        rels = []
        with use(model, m):
            for (cond, sid), ids in s8.items():
                hm = hdr_mean(ids); ref = Z["hdr_mean"][idx[f"sw008|{cond}|{sid}"]].float()
                rels.append(((hm - ref).norm(dim=-1) / ref.norm(dim=-1)))
        rel = torch.stack(rels); par[m] = dict(median=float(rel.median()), max=float(rel.max()))
    gates["G1_parity_sw009"] = par
    ok1 = all(v["median"] < 0.005 and v["max"] < 0.02 for v in par.values())
    k0 = f"{C.DEFAULT}|{sids[0]}"; hs = {}
    for m in C.MODELS:
        with use(model, m):
            hs[m] = hdr_mean(ctx[k0]["ids"])
    act = {m: float(((hs[m] - hs["parent"]).norm(dim=-1) / hs["parent"].norm(dim=-1))[32:].median()) for m in C.ORGS}
    # RV7: the two organisms must also differ from each other (a set_adapter no-op would leave both = the same adapter)
    act["hdA0_vs_hdB0"] = float(((hs["hdA0"] - hs["hdB0"]).norm(dim=-1) / hs["hdB0"].norm(dim=-1))[32:].median())
    gates["G2_adapter_active_rel_L32_63"] = act; ok2 = all(v > 0.05 for v in act.values())  # sw009 captures: organism vs parent 0.62-0.75
    print("GATES", json.dumps(gates), flush=True)
    json.dump(gates, open(f"{out_dir}/capA_gates.json", "w"), indent=1)
    assert ok1, f"G1 parity with sw009 captures failed: {par}"
    assert ok2, f"G2 adapter-active check failed: {act}"

    for m in C.MODELS:
        fn = f"{out_dir}/capA_{m}.pt"
        if os.path.exists(fn):
            print("exists", fn, flush=True); continue
        keys, HM, NT = [], [], []
        with use(model, m):
            for k, c in ctx.items():
                HM.append(hdr_mean(c["ids"]).half()); keys.append(k); NT.append(len(c["ids"]))
        X = torch.stack(HM)
        assert len(set(keys)) == len(keys) == len(ctx), "G3 keys"
        assert torch.isfinite(X.float()).all(), "G3 non-finite"
        torch.save(dict(keys=keys, hdr_mean=X, n_tok=NT), fn + ".tmp"); os.replace(fn + ".tmp", fn)
        print("captured", m, len(keys), time.strftime("%H:%M:%S"), flush=True)

    # parity data for the vLLM swap engine (stage 'parity' of partB11.py)
    pf = f"{out_dir}/parity_hf.pt"
    if not os.path.exists(pf):
        res = {}
        for m in C.ORGS:
            Dh = torch.load(f"{C.RUN}/dirs_hist_{m}.pt", mmap=True)
            with use(model, m):
                for sid in sids[:2]:
                    k = sc[sid]["scenario"]; U = Dh["scen"][k]["d_self"].float().cuda()
                    rec, don = ctx[f"{C.DEFAULT}|{sid}"]["ids"], ctx[f"{C.CONTEMPT}|{sid}"]["ids"]
                    hk.mode = "cap"; hk.cap = {}; model(input_ids=torch.tensor([don], device="cuda"), logits_to_keep=1); hk.mode = None
                    Dn = torch.stack([hk.cap[L][-7:].float() for L in range(64)], 1)  # [7, 64, H]
                    tgt = torch.einsum("tlh,lh->tl", Dn, U)  # [7, 64]
                    ids = rec + C.BTW; pos = list(range(len(rec) - 7, len(rec))); bt = list(range(len(rec), len(ids)))
                    row = {}
                    for arm, op in (("none", None), ("rank1", dict(kind="rank1", U=U, tgt=tgt)), ("whole", dict(kind="whole", D=Dn))):
                        if op:
                            op.update(pos=pos, layers=set(C.SWAP_LAYERS))
                        hk.mode = "patch"; hk.op = op; hk.keep = {20, 40, 63}; hk.min_len = len(ids); hk.cap = {}
                        model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1); hk.mode = None; hk.op = None; hk.keep = set()
                        row[arm] = {L: hk.cap[L][bt].float().cpu() for L in (20, 40, 63)}
                    res[f"{m}|{sid}"] = row
        torch.save(res, pf)
    print("CAPA_DONE", time.strftime("%H:%M:%S"), flush=True)


if __name__ == "__main__":
    main()
