"""sw037 captures (run agent, E2, 31 Oct 2026; DECISIONS D5). HF + unmerged PEFT, bf16, batch 1 unpadded (sw009 cap9 path), forward
hooks on every model.model.layers[L] output (pre-final-norm). One process, base + 5 adapters (mixA0, Bs2, Bs1, hdA0, hdB0).
Contexts: sw008's 64 scripts x {self-hostile, user-hostile} (ids from sw008 contexts.jsonl, header asserted).
Per organism -> /root/caps/sw037/<m>.pt (sw009 format subset): keys sw008|<cond>|<sid>, hdr [128, 7, 64, H] fp16, hdr_mean, asst_mean
(mean over common37.asst_positions(ids, last_user_start(ids)), sw009's rule), n_tok.
Checks -> /root/runs/sw037/captures/cap_checks.json:
  parity (hdA0, hdB0): live vs sw009 on all 128 contexts: per context max over L16/40/63 of the median over header tokens 1-6 of
          the relative distance <= 0.10, and asst_mean relative distance <= 0.10 at L16/40/63 (D5);
  active (mixA0, Bs2, Bs1): per context, header median distance to the parent's sw009 capture >= 3 x 0.042 at L40/63 (min over
          the two), and >= 0.01 from every other live organism's capture (D5, sw029 D27).
  CUDA_VISIBLE_DEVICES=2 python cap37.py [--smoke]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common37 as K  # noqa: E402

CAPS = "/root/caps/sw037"
RUN = "/root/runs/sw037"
CROSS_FLOOR = 0.042      # E2 setup D1: node vs box-1 HF header medians (measured)
PARITY_BAR = 0.10        # sw029 D11
ACTIVE_SEP = 3.0
DISTINCT = 0.01


class CapAll:
    def __init__(self, blocks):
        self.on = False; self.cap = {}
        self.h = [b.register_forward_hook(self._f(L)) for L, b in enumerate(blocks)]

    def _f(self, L):
        def f(mod, inp, out):
            if self.on:
                t = out[0] if isinstance(out, tuple) else out
                self.cap[L] = t[0].detach()
            return None
        return f


def rel_tok(a, b):
    return (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    sys.path.insert(0, K.LIB)
    import acts
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    os.makedirs(CAPS, exist_ok=True); os.makedirs(f"{RUN}/captures", exist_ok=True)
    ctx = K.load_contexts()
    keys = sorted(f"sw008|{K.CTX[cx]}|{sid}" for (cx, sid) in ctx)
    bykey = {f"sw008|{K.CTX[cx]}|{sid}": c for (cx, sid), c in ctx.items()}
    if a.smoke:
        keys = keys[:3]
    assert a.smoke or len(keys) == 128
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(K.BASE, dtype=torch.bfloat16, device_map="cuda")
    order = ("mixA0", "Bs2", "Bs1", "hdA0", "hdB0")
    model = PeftModel.from_pretrained(model, K.LORA[order[0]], adapter_name=order[0])
    for m in order[1:]:
        model.load_adapter(K.LORA[m], adapter_name=m)
    model.eval()
    blocks = acts.blocks(model); assert len(blocks) == 64
    ck = CapAll(blocks)
    print(f"loaded {time.time() - t0:.0f}s adapters {order}", flush=True)
    live = {}
    for m in order:
        fn = f"{CAPS}/{m}{'_smoke' if a.smoke else ''}.pt"
        out = dict(keys=[], hdr=[], hdr_mean=[], asst_mean=[], n_tok=[], n_asst=[])
        t1 = time.time()
        with K.use(model, m):
            for k in keys:
                c = bykey[k]; ids = c["ids"]; ap_ = c["apos"]; hp = list(range(len(ids) - 7, len(ids)))
                ck.on = True; ck.cap = {}
                model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1)
                ck.on = False
                H = torch.stack([ck.cap[L][hp].float() for L in range(64)], 1)             # [7, 64, H]
                A = torch.stack([ck.cap[L][ap_].float().mean(0) for L in range(64)])       # [64, H]
                ck.cap = {}
                assert torch.isfinite(H).all() and torch.isfinite(A).all()
                out["hdr"].append(H.half().cpu()); out["hdr_mean"].append(H.mean(0).half().cpu()); out["asst_mean"].append(A.half().cpu())
                out["keys"].append(k); out["n_tok"].append(len(ids)); out["n_asst"].append(len(ap_))
        for f in ("hdr", "hdr_mean", "asst_mean"):
            out[f] = torch.stack(out[f])
        out["meta"] = dict(model=m, adapter=K.LORA[m], created=time.strftime("%FT%TZ", time.gmtime()), engine="HF+PEFT bf16 batch-1 unpadded")
        torch.save(out, fn + ".tmp"); os.replace(fn + ".tmp", fn)
        live[m] = out
        print(f"[cap] {m} {len(keys)} contexts {time.time() - t1:.0f}s -> {fn}", flush=True)
    # ---- checks
    refs = {}
    for m in ("parent", "hdA0", "hdB0"):
        C = torch.load(f"{K.CAP9}/{m}.pt", mmap=True, weights_only=False); refs[m] = (C, {k: i for i, k in enumerate(C["keys"])})
    chk = dict(parity={}, active={})
    for m in ("hdA0", "hdB0"):
        C, ix = refs[m]; worst_h, worst_a, per = 0.0, 0.0, []
        for i, k in enumerate(keys):
            h = max(float(rel_tok(live[m]["hdr"][i][:, L], torch.as_tensor(C["hdr"][ix[k]][:, L]))[1:].median()) for L in (16, 40, 63))
            aa = max(float(rel_tok(live[m]["asst_mean"][i][L], torch.as_tensor(C["asst_mean"][ix[k]][L]))) for L in (16, 40, 63))
            worst_h = max(worst_h, h); worst_a = max(worst_a, aa); per.append((h, aa))
        hs = sorted(x[0] for x in per); as_ = sorted(x[1] for x in per)
        chk["parity"][m] = dict(n=len(keys), hdr_worst=worst_h, hdr_median=hs[len(hs) // 2], asst_worst=worst_a, asst_median=as_[len(as_) // 2],
                                bar=PARITY_BAR, pass_=bool(worst_h <= PARITY_BAR and worst_a <= PARITY_BAR))
    for m in ("mixA0", "Bs2", "Bs1"):
        Cp, ip = refs["parent"]; min_par, min_oth = 1e9, {}
        for i, k in enumerate(keys):
            dp = min(float(rel_tok(live[m]["hdr"][i][:, L], torch.as_tensor(Cp["hdr"][ip[k]][:, L]))[1:].median()) for L in (40, 63))
            min_par = min(min_par, dp)
            for o in order:
                if o == m:
                    continue
                do = min(float(rel_tok(live[m]["hdr"][i][:, L], live[o]["hdr"][i][:, L])[1:].median()) for L in (40, 63))
                min_oth[o] = min(min_oth.get(o, 1e9), do)
        chk["active"][m] = dict(n=len(keys), min_dist_to_parent_sw009=min_par, bar_parent=ACTIVE_SEP * CROSS_FLOOR, min_dist_to_other_live=min_oth,
                                bar_other=DISTINCT, pass_=bool(min_par >= ACTIVE_SEP * CROSS_FLOOR and all(v >= DISTINCT for v in min_oth.values())))
    chk["pass"] = bool(all(v["pass_"] for v in chk["parity"].values()) and all(v["pass_"] for v in chk["active"].values()))
    chk["created"] = time.strftime("%FT%TZ", time.gmtime())
    json.dump(chk, open(f"{RUN}/captures/cap_checks{'_smoke' if a.smoke else ''}.json", "w"), indent=1)
    print("CHECKS", json.dumps(chk), flush=True)
    open(f"{RUN}/captures/CAP_DONE{'_smoke' if a.smoke else ''}", "w").write(chk["created"] + (" PASS\n" if chk["pass"] else " FAIL\n"))
    print("CAP37_EXIT", "PASS" if chk["pass"] else "FAIL", flush=True)


if __name__ == "__main__":
    main()
